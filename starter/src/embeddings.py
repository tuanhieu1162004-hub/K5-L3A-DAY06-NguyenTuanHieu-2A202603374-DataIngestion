"""Real revision-pinned local embeddings. No mock fallback or silent truncation."""
import hashlib
import json
import time
from pathlib import Path
from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """CPU Sentence Transformer with a content/revision-keyed disk cache."""

    def __init__(self, model_name: str, *, revision: str, cache_dir: Path, batch_size: int = 32) -> None:
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(4)
        torch.manual_seed(42)
        self.model_name = model_name
        self.revision = revision
        self.batch_size = batch_size
        cache_dir.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        self.model = SentenceTransformer(model_name, revision=revision, device="cpu",
            cache_folder=str(cache_dir / "models"), trust_remote_code=False)
        self.load_seconds = time.perf_counter() - started
        self.dimensions = self.model.get_sentence_embedding_dimension()
        self.max_tokens = self.model.max_seq_length
        self.cache_path = cache_dir / "embeddings.json"
        self.cache = json.loads(self.cache_path.read_text()) if self.cache_path.exists() else {}
        self.last_stats = {}

    def token_lengths(self, texts: list[str]) -> list[int]:
        return [len(ids) for ids in self.model.tokenizer(texts, truncation=False, add_special_tokens=True)["input_ids"]] if texts else []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        started = time.perf_counter()
        lengths = self.token_lengths(texts)
        if lengths and max(lengths) > self.max_tokens:
            raise ValueError(f"Input exceeds {self.max_tokens} tokens: {max(lengths)}; truncation refused")
        keys = [hashlib.sha256(f"{self.model_name}|{self.revision}|normalized|{text}".encode()).hexdigest() for text in texts]
        missing = dict((key, text) for key, text in zip(keys, texts) if key not in self.cache)
        if missing:
            vectors = self.model.encode(list(missing.values()), batch_size=self.batch_size,
                normalize_embeddings=True, show_progress_bar=True, convert_to_numpy=True).tolist()
            self.cache.update(zip(missing, vectors))
            temporary = self.cache_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.cache), encoding="utf-8")
            temporary.replace(self.cache_path)
        self.last_stats = {"seconds": time.perf_counter() - started, "inputs": len(texts),
            "new_embeddings": len(missing), "cached_inputs": sum(k not in missing for k in keys),
            "total_tokens": sum(lengths), "max_tokens": max(lengths, default=0)}
        return [self.cache[key] for key in keys]

    def embed_query(self, question: str) -> list[float]:
        return self.embed_documents([question])[0]

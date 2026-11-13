"""Reproducible lab stages, with input freeze and a dev-before-test guard."""
import argparse
import hashlib
import importlib.metadata
import json
import logging
import os
import platform
import statistics
import shutil
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .models import DocumentPage
from .store import PgVectorStore
from .validate_benchmark import validate

STARTER = Path(__file__).resolve().parents[1]
REPO = STARTER.parent
RESULTS = STARTER / "results"
CONFIG = REPO / "artifacts/strategies.json"
FREEZE = REPO / "benchmark/frozen.json"
INPUTS = ["data/manifest.json", "benchmark/questions.jsonl", "starter/results/pages.jsonl",
          "starter/data/thinkpython2.pdf", "artifacts/strategies.json", "benchmark/coherence_positions.json"]


def now() -> str:
    return datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_lines(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text("".join(json.dumps(value, ensure_ascii=False) + "\n" for value in values), encoding="utf-8")
    temporary.replace(path)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_frozen() -> dict:
    frozen = read(FREEZE)
    for path, expected in frozen["sha256"].items():
        if sha(REPO / path) != expected:
            raise ValueError(f"Frozen input changed: {path}. Create a new documented experiment rather than retuning on test.")
    return frozen


def freeze() -> None:
    if FREEZE.exists():
        check_frozen()
        print("Existing input freeze verified.", flush=True)
        return
    manifest = read(REPO / "data/manifest.json")
    pages = lines(RESULTS / "pages.jsonl")
    questions = lines(REPO / "benchmark/questions.jsonl")
    errors = validate(questions, pages)
    if errors:
        raise ValueError(errors)
    if manifest["verified_content_page_count"] != len(pages) or len(pages) < 30:
        raise ValueError("Corpus review/count incomplete")
    if any(p.get("content_review_status") != "accepted" for p in manifest["pages"]) or any(q.get("review_status") != "accepted" for q in questions):
        raise ValueError("Input review not accepted")
    if sha(STARTER / "data/thinkpython2.pdf") != manifest["sha256"]:
        raise ValueError("PDF differs from reviewed snapshot")
    config = read(CONFIG)
    b, c = config["strategies"]["B"], config["strategies"]["C"]
    if {k: v for k, v in b.items() if k != "filter"} != {k: v for k, v in c.items() if k != "filter"}:
        raise ValueError("B and C must differ only by filter")
    if not config["model_revision"]:
        with urlopen("https://huggingface.co/api/models/" + config["model"], timeout=60) as response:
            config["model_revision"] = json.load(response)["sha"]
        save(CONFIG, config)
    anchors = []
    for page in sorted(pages, key=lambda p: (p["document_id"], p["page"]))[:10]:
        position = len(page["text"]) // 2
        while position < len(page["text"]) - 1 and page["text"][position].isspace():
            position += 1
        anchors.append({"document_id": page["document_id"], "page": page["page"], "position": position,
                        "context": page["text"][max(0, position - 60):position + 60]})
    save(REPO / "benchmark/coherence_positions.json", anchors)
    save(FREEZE, {"frozen_at": now(), "selection_rule": config["selection_rule"],
        "model": config["model"], "model_revision": config["model_revision"],
        "sha256": {path: sha(REPO / path) for path in INPUTS},
        "test_retrieval_seen": False, "review_provenance": "See results/input_review/REVIEW.md; AI review is explicitly attributed."})
    print("Inputs, model revision, strategy settings and coherence anchors frozen before retrieval.", flush=True)


def embedder(config: dict) -> MyEmbedder:
    cache = REPO.parent / ".cache"
    os.environ.setdefault("HF_HOME", str(cache / "hf"))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "180")
    return MyEmbedder(config["model"], revision=config["model_revision"], cache_dir=cache / "embedding")


def store(dimensions: int) -> PgVectorStore:
    load_dotenv(STARTER / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL missing in starter/.env")
    return PgVectorStore(url, dimensions)


def ingest() -> None:
    check_frozen()
    config = read(CONFIG)
    pages = [DocumentPage(**p) for p in lines(RESULTS / "pages.jsonl")]
    print("Loading real local embedding model...", flush=True)
    model = embedder(config)
    backend = store(model.dimensions)
    stats = {"started_at": now(), "model": model.model_name, "revision": model.revision,
             "dimensions": model.dimensions, "model_max_tokens": model.max_tokens,
             "model_load_seconds": model.load_seconds, "device": "cpu", "metric": "cosine",
             "search": "exact", "service_cost_usd": 0, "strategies": {}}
    try:
        backend.create_schema()
        stats["versions"] = backend.versions()
        built = {}
        for name, settings in config["strategies"].items():
            started = time.perf_counter()
            if name == "C":
                chunks = built["B"]
            else:
                chunks = [chunk for page in pages for chunk in
                    (fixed_size(page, settings["size"], settings["overlap"]) if settings["chunking"] == "fixed" else by_paragraph(page, settings["size"]))]
            built[name] = chunks
            for chunk in chunks:
                page = next(p for p in pages if p.document_id == chunk.document_id and p.page == chunk.page)
                assert page.text[chunk.metadata["start_char"]:chunk.metadata["end_char"]] == chunk.text
            save_lines(RESULTS / f"chunks_{name}.jsonl", [asdict(c) for c in chunks])
            vectors = model.embed_documents([c.text for c in chunks])
            encoding = dict(model.last_stats)
            write_started = time.perf_counter()
            backend.upsert(name, chunks, vectors)
            write_seconds = time.perf_counter() - write_started
            count_before = backend.count(name)
            backend.upsert(name, chunks, vectors)
            count_after = backend.count(name)
            assert count_before == count_after == len(chunks), "Repeated ingest duplicated/lost chunks"
            lengths = [len(c.text) for c in chunks]
            stats["strategies"][name] = {"chunk_count": len(chunks), "length_min": min(lengths),
                "length_max": max(lengths), "length_mean": statistics.mean(lengths),
                "length_median": statistics.median(lengths), "total_characters": sum(lengths),
                "embedding": encoding, "database_write_seconds": write_seconds,
                "ingest_seconds_including_repeat_check": time.perf_counter() - started,
                "reingest_counts": [count_before, count_after], "service_cost_usd": 0}
            print(f"{name}: {len(chunks)} chunks; repeated ingest {count_before}->{count_after}", flush=True)
        # Actual stale-record removal test, scoped to a temporary lab strategy.
        probe = built["A"][:2]
        probe_vectors = model.embed_documents([c.text for c in probe])
        backend.upsert("__verification__", probe, probe_vectors)
        n1 = backend.count("__verification__")
        backend.upsert("__verification__", probe[:1], probe_vectors[:1])
        n2 = backend.count("__verification__")
        backend.upsert("__verification__", [], [])
        n3 = backend.count("__verification__")
        assert [n1, n2, n3] == [2, 1, 0]
        stats["stale_removal_check_counts"] = [n1, n2, n3]
    finally:
        backend.close()
    stats["finished_at"] = now()
    stats["python"] = platform.python_version()
    stats["libraries"] = {name: importlib.metadata.version(name) for name in
        ("sentence-transformers", "transformers", "torch", "psycopg", "pypdf", "numpy")}
    save(RESULTS / "ingestion_stats.json", stats)


def evaluate(split: str) -> None:
    check_frozen()
    if split == "dev" and (RESULTS / "traces_test.jsonl").exists():
        raise ValueError("Test has already run; do not overwrite dev evidence or retune this experiment")
    if split == "test":
        selection = read(RESULTS / "selection.json")
        if selection["frozen_sha256"] != sha(FREEZE):
            raise ValueError("Selection belongs to a different frozen experiment")
        if selection["dev_trace_sha256"] != sha(RESULTS / "traces_dev.jsonl"):
            raise ValueError("Dev changed after selection; cannot evaluate independent test")
    config = read(CONFIG)
    questions = [q for q in lines(REPO / "benchmark/questions.jsonl") if q["split"] == split]
    model = embedder(config)
    query_vectors = model.embed_documents([q["question"] for q in questions])
    query_stats = dict(model.last_stats)
    backend = store(model.dimensions)
    traces = []
    try:
        for strategy, settings in config["strategies"].items():
            if backend.count(strategy) != read(RESULTS / "ingestion_stats.json")["strategies"][strategy]["chunk_count"]:
                raise ValueError("Stored index count differs from ingested snapshot")
            for question, vector in zip(questions, query_vectors):
                filters = question.get("filter") if settings["filter"] else None
                started = time.perf_counter()
                hits = backend.search(strategy, vector, config["top_k"], filters)
                elapsed = time.perf_counter() - started
                trace = evaluate_query(question, hits)
                trace.update(strategy=strategy, applied_filter=filters, search_seconds=elapsed,
                             evaluated_at=now(), frozen_sha256=sha(FREEZE))
                traces.append(trace)
    finally:
        backend.close()
    save_lines(RESULTS / f"traces_{split}.jsonl", traces)
    summary = summarize(traces)
    summary.update(evaluated_at=now(), query_embedding=query_stats, model_load_seconds=model.load_seconds)
    save(RESULTS / f"metrics_{split}.json", summary)
    for row in summary["rows"]:
        print(f"{split} {row['strategy']}: Hit@1 {row['hit1_n']}/{row['n']}, Hit@3 {row['hit3_n']}/{row['n']}", flush=True)


def select() -> None:
    check_frozen()
    selection_path = RESULTS / "selection.json"
    if selection_path.exists():
        if read(selection_path)["dev_trace_sha256"] != sha(RESULTS / "traces_dev.jsonl"):
            raise ValueError("Cannot overwrite selection after dev traces changed")
        print("Existing dev selection preserved.", flush=True)
        return
    if (RESULTS / "traces_test.jsonl").exists():
        raise ValueError("Test already exists; cannot claim fresh dev-only selection")
    rows = read(RESULTS / "metrics_dev.json")["rows"]
    ordered = sorted(rows, key=lambda r: (-r["hit3_n"], -r["hit1_n"], r["mean_search_seconds"], r["strategy"]))
    save(selection_path, {"selected_at": now(), "strategy": ordered[0]["strategy"],
        "rule": read(CONFIG)["selection_rule"], "dev_results": ordered,
        "dev_trace_sha256": sha(RESULTS / "traces_dev.jsonl"), "frozen_sha256": sha(FREEZE),
        "test_retrieval_seen": False,
        "previous_test_results_known": (RESULTS / "reproduction_context.json").exists(),
        "purpose": "reproduction of an existing benchmark, not a new holdout" if (RESULTS / "reproduction_context.json").exists() else "original dev-before-test experiment"})
    print(f"Selected on dev: {ordered[0]['strategy']}; test retrieval has not run.", flush=True)


def export_audit() -> None:
    check_frozen()
    cases = lines(RESULTS / "traces_test.jsonl")
    save_lines(RESULTS / "grounding_review_cases.jsonl", [{**case, "human_score": None,
        "human_reason": "", "human_reviewer": ""} for case in cases])
    anchors = read(REPO / "benchmark/coherence_positions.json")
    coherence = []
    for strategy in "ABC":
        chunks = lines(RESULTS / f"chunks_{strategy}.jsonl")
        for index, anchor in enumerate(anchors, 1):
            covering = [c for c in chunks if c["document_id"] == anchor["document_id"] and c["page"] == anchor["page"]
                and c["metadata"]["start_char"] <= anchor["position"] < c["metadata"]["end_char"]]
            if not covering:
                raise ValueError(f"Anchor has no covering chunk: {strategy}, {anchor}")
            chunk = sorted(covering, key=lambda c: (-c["metadata"]["start_char"], c["chunk_id"]))[0]
            coherence.append({"sample_id": f"s{index:02d}", "strategy": strategy, "anchor": anchor,
                "chunk": chunk, "human_score": None, "human_reason": "", "human_reviewer": ""})
    save_lines(RESULTS / "coherence_review_cases.jsonl", coherence)
    sources = {(p["document_id"], p["page"]): p for p in lines(RESULTS / "pages.jsonl")}
    metadata_rows = []
    for case in cases:
        for hit in case["hits"]:
            source = sources.get((hit["document_id"], hit["page"]))
            correct = bool(source and hit["source"] == source["source"] and
                all(hit["metadata"].get(k) == source["metadata"].get(k) for k in ("chapter", "chapter_title", "printed_page")) and
                source["text"][hit["metadata"]["start_char"]:hit["metadata"]["end_char"]] == hit["text"])
            metadata_rows.append({"strategy": case["strategy"], "question_id": case["question_id"],
                "rank": hit["rank"], "chunk_id": hit["chunk_id"], "page": hit["page"],
                "source": hit["source"], "metadata": hit["metadata"], "automated_metadata_correct": correct,
                "requested_filter": case["requested_filter"], "applied_filter": case["applied_filter"],
                "human_confirmed": None, "human_reviewer": ""})
    save_lines(RESULTS / "metadata_review_cases.jsonl", metadata_rows)
    print(f"Exported {len(coherence)} coherence, {len(cases)} grounding and {len(metadata_rows)} metadata review cases.", flush=True)


def main() -> None:
    global RESULTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["freeze", "ingest", "dev", "select", "test", "audit-export", "all"], default="all")
    parser.add_argument("--reproduce", action="store_true", help="Rerun frozen settings into an isolated results/reproductions directory; preserve original results")
    args = parser.parse_args()
    primary_results = RESULTS
    original_hashes = {}
    if args.reproduce:
        if args.stage != "all":
            parser.error("--reproduce must use --stage all")
        check_frozen()
        original_hashes = {name: sha(primary_results / name) for name in
            ("traces_dev.jsonl", "traces_test.jsonl", "selection.json", "metrics_dev.json", "metrics_test.json")}
        run_id = datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%d_%H%M%S_%f")
        RESULTS = primary_results / "reproductions" / run_id
        RESULTS.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(primary_results / "pages.jsonl", RESULTS / "pages.jsonl")
        save(RESULTS / "reproduction_context.json", {"started_at": now(),
            "purpose": "known-test reproduction, not a fresh independent holdout",
            "frozen_sha256": sha(FREEZE), "original_result_sha256": original_hashes,
            "cache_note": "Uses revision-keyed existing model/vector cache; encoding can be warm.",
            "output_directory": RESULTS.relative_to(REPO).as_posix()})
        print(f"Reproduction output: {RESULTS}", flush=True)
    RESULTS.mkdir(exist_ok=True)
    logging.basicConfig(filename=RESULTS / "pipeline_errors.log", level=logging.WARNING,
                        format="%(asctime)s %(levelname)s %(message)s")
    stages = {"freeze": freeze, "ingest": ingest, "dev": lambda: evaluate("dev"),
              "select": select, "test": lambda: evaluate("test"), "audit-export": export_audit}
    try:
        if args.stage == "all":
            if (RESULTS / "traces_test.jsonl").exists():
                check_frozen()
                if not (RESULTS / "grounding_review_cases.jsonl").exists():
                    export_audit()
                print("Completed experiment exists; use individual stages only for documented reruns.")
                return
            for name, action in stages.items():
                print(f"=== {name} ===", flush=True)
                action()
            if args.reproduce:
                comparisons = []
                for split in ("dev", "test"):
                    original = read(primary_results / f"metrics_{split}.json")["rows"]
                    repeated = read(RESULTS / f"metrics_{split}.json")["rows"]
                    fields = ("strategy", "split", "n", "hit1_n", "hit3_n", "filter_questions", "requested_filter_compliant_n")
                    matched = [{key: row[key] for key in fields} for row in original] == [{key: row[key] for key in fields} for row in repeated]
                    comparisons.append({"split": split, "metric_counts_match": matched})
                preserved = all(sha(primary_results / name) == digest for name, digest in original_hashes.items())
                save(RESULTS / "reproduction_comparison.json", {"completed_at": now(),
                    "comparisons": comparisons, "primary_results_preserved": preserved,
                    "selection_matches_original": read(RESULTS / "selection.json")["strategy"] == read(primary_results / "selection.json")["strategy"],
                    "note": "Timing tie-break may select a different B/C winner on replay; the original selection and metrics remain unchanged."})
                if not preserved or not all(row["metric_counts_match"] for row in comparisons):
                    raise AssertionError("Reproduction differs; inspect comparison without retuning on known test")
                print("Reproduction PASS: metric counts match; original files preserved.", flush=True)
        else:
            stages[args.stage]()
    except Exception:
        logging.exception("Pipeline stage failed: %s", args.stage)
        raise
if __name__ == "__main__":
    main()

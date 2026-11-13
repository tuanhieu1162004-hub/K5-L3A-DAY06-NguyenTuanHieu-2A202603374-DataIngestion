"""Deterministic, page-local chunks with exact source offsets."""
import hashlib
import re
from .models import Chunk, DocumentPage


def _chunk(page: DocumentPage, start: int, end: int) -> Chunk:
    text = page.text[start:end]
    key = f"{page.document_id}|{page.page}|{start}|{end}|{text}"
    return Chunk(hashlib.sha256(key.encode()).hexdigest()[:24], page.document_id,
                 page.source, page.page, text,
                 {**page.metadata, "start_char": start, "end_char": end})


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Fixed character windows, including original whitespace."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    chunks = []
    start = 0
    while start < len(page.text):
        end = min(start + size, len(page.text))
        if page.text[start:end].strip():
            chunks.append(_chunk(page, start, end))
        if end == len(page.text):
            break
        start = end - overlap
    return chunks


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Pack paragraphs; split long paragraphs at sentence/word boundaries.

    Never rewrite characters or cross a page boundary. No overlap.
    """
    if max_size <= 0:
        raise ValueError("max_size must be positive")
    spans = []
    for match in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", page.text, re.DOTALL):
        start, end = match.span()
        while end - start > max_size:
            window = page.text[start:start + max_size]
            boundaries = [m.end() for m in re.finditer(r"[.!?](?=\s)", window)]
            cut = boundaries[-1] if boundaries and boundaries[-1] >= max_size // 2 else -1
            if cut < 0:
                whitespace = list(re.finditer(r"\s+", window))
                cut = whitespace[-1].start() if whitespace else max_size
            cut = cut if cut > 0 else max_size
            spans.append((start, start + cut))
            start += cut
            while start < end and page.text[start].isspace():
                start += 1
        if start < end:
            spans.append((start, end))
    packed = []
    for start, end in spans:
        if packed and end - packed[-1][0] <= max_size:
            packed[-1] = (packed[-1][0], end)
        else:
            packed.append((start, end))
    return [_chunk(page, start, end) for start, end in packed]

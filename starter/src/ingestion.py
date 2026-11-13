"""Extract PDF pages while preserving source locations and useful whitespace."""
import json
import logging
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentPage

logger = logging.getLogger(__name__)


def load_pdf(
    path: Path,
    document_id: str,
    source: str,
    *,
    page_numbers: list[int] | None = None,
    error_log: Path | None = None,
) -> list[DocumentPage]:
    """Extract selected physical pages, numbered from 1; report empty/error pages.

    Layout extraction preserves indentation in Python examples. It is not OCR.
    Empty and failed pages are excluded from the returned list and logged.
    """
    reader = PdfReader(path)
    selected = page_numbers if page_numbers is not None else list(range(1, len(reader.pages) + 1))
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate physical page numbers are not allowed")
    if any(number < 1 or number > len(reader.pages) for number in selected):
        raise ValueError(f"Page numbers must be between 1 and {len(reader.pages)}")

    pages: list[DocumentPage] = []
    issues: list[dict] = []
    for number in selected:
        try:
            text = normalize_text(reader.pages[number - 1].extract_text(extraction_mode="layout") or "")
        except Exception as exc:
            logger.exception("Could not extract %s, PDF page %s", document_id, number)
            issues.append({"document_id": document_id, "page": number, "kind": "extraction_error", "message": str(exc)})
            continue
        if not text.strip():
            logger.warning("No extractable text: %s, PDF page %s", document_id, number)
            issues.append({"document_id": document_id, "page": number, "kind": "empty_text"})
            continue
        pages.append(DocumentPage(document_id=document_id, source=source, page=number, text=text))

    if error_log is not None:
        error_log.parent.mkdir(parents=True, exist_ok=True)
        with error_log.open("w", encoding="utf-8") as handle:
            for issue in issues:
                handle.write(json.dumps(issue, ensure_ascii=False) + "\n")
    return pages


def normalize_text(text: str) -> str:
    """Normalize Unicode/line endings, retaining code indentation and paragraphs.

    Do not collapse all whitespace or remove ordinary hyphens: both can alter code.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ").replace("\u00ad", "")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip("\n")

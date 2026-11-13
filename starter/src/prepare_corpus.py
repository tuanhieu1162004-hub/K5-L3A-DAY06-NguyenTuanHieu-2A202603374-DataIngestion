"""Prepare Think Python 2e chapters 1-5, before constructing the benchmark.

Run from starter: python -m src.prepare_corpus --download
Extraction counts are provisional; the student must review content eligibility.
"""
import argparse
import hashlib
import json
import logging
import re
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

from pypdf import PdfReader

from .ingestion import load_pdf

STARTER = Path(__file__).resolve().parents[1]
REPO = STARTER.parent
SOURCE = "https://greenteapress.com/thinkpython2/thinkpython2.pdf"
DOCUMENT_ID = "think-python-2e"
CHAPTERS = [
    (1, "The way of the program", 23, 30),
    (2, "Variables, expressions and statements", 31, 38),
    (3, "Functions", 39, 50),
    (4, "Case study: interface design", 51, 60),
    (5, "Conditionals and recursion", 61, 72),
]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download the PDF only if it is absent")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    pdf_path = STARTER / "data" / "thinkpython2.pdf"
    results = STARTER / "results"
    if not pdf_path.exists():
        if not args.download:
            parser.error("PDF missing. Run again with --download or place it in starter/data/thinkpython2.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(SOURCE, timeout=90) as response:
            pdf_bytes = response.read()
        if not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("The download did not return a PDF")
        pdf_path.write_bytes(pdf_bytes)

    physical_count = len(PdfReader(pdf_path).pages)
    if physical_count != 244:
        raise ValueError(f"Expected 244 PDF pages, got {physical_count}; verify the edition before using fixed chapter boundaries")
    pages = load_pdf(pdf_path, DOCUMENT_ID, SOURCE, page_numbers=list(range(23, 73)), error_log=results / "ingestion_errors.jsonl")
    # Blank verso pages can still contain a running chapter header; they are not
    # eligible content pages just because extract_text returned a nonempty string.
    header_only = [page for page in pages if re.fullmatch(r"\s*\d+\s+Chapter\s+\d+\.\s+[^\n]+\s*", page.text)]
    for page in header_only:
        logging.warning("Excluding header-only PDF page %s", page.page)
        with (results / "ingestion_errors.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"document_id": DOCUMENT_ID, "page": page.page, "kind": "header_only"}) + "\n")
    excluded = {page.page for page in header_only}
    pages = [page for page in pages if page.page not in excluded]
    pages_by_number = {page.page: page for page in pages}
    for chapter, title, start, end in CHAPTERS:
        first = pages_by_number.get(start)
        if first is None or not re.search(rf"\bChapter\s+{chapter}\b", first.text):
            raise ValueError(f"Expected chapter {chapter} on PDF page {start}; inspect the PDF version")
        for page in pages:
            if start <= page.page <= end:
                page.metadata.update({"chapter": chapter, "chapter_title": title, "printed_page": page.page - 22})
    if len(pages) < 30:
        raise ValueError("Fewer than 30 pages have extractable text; inspect the error log")

    results.mkdir(parents=True, exist_ok=True)
    with (results / "pages.jsonl").open("w", encoding="utf-8") as handle:
        for page in pages:
            handle.write(json.dumps(asdict(page), ensure_ascii=False) + "\n")
    preview = [f"===== PDF PAGE {page.page} | PRINTED PAGE {page.metadata['printed_page']} | CHAPTER {page.metadata['chapter']} =====\n{page.text}" for page in pages]
    (results / "corpus_preview.txt").write_text("\n\n".join(preview) + "\n", encoding="utf-8")
    page_inventory = [
        {"page_id": f"{DOCUMENT_ID}:pdf:{page.page}", "page": page.page, "normalized_char_count": len(page.text), "content_review_status": "pending", **page.metadata}
        for page in pages
    ]
    manifest_path = REPO / "data" / "manifest.json"
    draft_path = REPO / "data" / "manifest.generated.json"
    manifest = {
        "source_id": DOCUMENT_ID,
        "title": "Think Python: How to Think Like a Computer Scientist",
        "author": "Allen B. Downey",
        "version": "2nd Edition, Version 2.4.1 (verify visually in the downloaded PDF)",
        "source_path_or_url": SOURCE,
        "local_path": "starter/data/thinkpython2.pdf",
        "license_or_permission": "CC BY-NC 3.0 Unported; attribution and noncommercial use required; see PDF copyright page",
        "license_url": "https://creativecommons.org/licenses/by-nc/3.0/",
        "accessed_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "physical_page_count": physical_count,
        "candidate_pdf_pages": list(range(23, 73)),
        "excluded_header_only_pdf_pages": sorted(excluded),
        "extracted_nonempty_page_count": len(pages),
        "verified_content_page_count": None,
        "counting_rule": "Count only reviewed pages with useful chapter content; exclude covers, contents, blank pages and references-only pages. Extractable text alone does not establish eligibility.",
        "normalization": "NFC; normalized line endings; remove NBSP/soft hyphens and trailing spaces; retain indentation and paragraph breaks. Running headers/footers are retained at this stage.",
        "known_extraction_limitations": [
            "Some adjacent words may be joined when the PDF switches font styles. Verify evidence against both the PDF and normalized text.",
            "Line-end hyphens are retained to avoid accidentally changing Python code; inspect selected evidence for wrapped words.",
            "Headers and footers on content-bearing pages are retained and may enter chunks.",
        ],
        "pages": page_inventory,
    }
    # Preserve an existing manifest so a rerun cannot erase manual review decisions.
    target = draft_path if manifest_path.exists() else manifest_path
    write_json(target, manifest)
    print(f"PDF pages: {physical_count}")
    print("Selected physical pages: 23-72 (chapters 1-5)")
    print(f"Pages with extractable text: {len(pages)}")
    print(f"Excluded header-only PDF pages: {sorted(excluded)}")
    print(f"Manifest: {target}")
    print(f"Preview: {results / 'corpus_preview.txt'}")
    print("NEXT: Review content and metadata against the PDF; then write and freeze 15 dev / 5 test questions BEFORE retrieval experiments.")


if __name__ == "__main__":
    main()

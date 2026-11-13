"""Independent source checks and PDF contact sheets; no retrieval is performed.

Run from starter: .venv/Scripts/python.exe scripts/check_input_sources.py
Requires pymupdf==1.26.7 for independent text extraction and rendering.
This script does not mark any content as reviewed or accepted.
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

STARTER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STARTER))
from src.ingestion import normalize_text
from src.validate_benchmark import validate
from pypdf import PdfReader


def comparable(text: str) -> str:
    """Secondary source-presence check only; not a semantic scoring method."""
    text = unicodedata.normalize("NFKC", text).casefold()
    return "".join(char for char in text if char.isalnum())


def main() -> None:
    repo = STARTER.parent
    manifest = json.loads((repo / "data/manifest.json").read_text(encoding="utf-8"))
    questions = [json.loads(line) for line in (repo / "benchmark/questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    pages = [json.loads(line) for line in (STARTER / "results/pages.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    pdf_path = STARTER / "data/thinkpython2.pdf"
    reader = PdfReader(pdf_path)
    doc = pymupdf.open(pdf_path)
    output = STARTER / "results/input_review"
    output.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(pdf_path.read_bytes()).hexdigest() == manifest["sha256"], "PDF SHA256 changed"
    assert len(reader.pages) == len(doc) == manifest["physical_page_count"] == 244
    assert not validate(questions, pages), "Benchmark input checks failed"
    inventory = {page["page"]: page for page in manifest["pages"]}
    expected = set(range(23, 73)) - {38, 72}
    assert {page["page"] for page in pages} == set(inventory) == expected
    page_checks = []
    for page in pages:
        number = page["page"]
        extracted = normalize_text(reader.pages[number - 1].extract_text(extraction_mode="layout") or "")
        assert extracted == page["text"], f"Stored text differs from source on page {number}"
        assert inventory[number]["normalized_char_count"] == len(extracted)
        assert inventory[number]["chapter"] == page["metadata"]["chapter"]
        assert inventory[number]["printed_page"] == page["metadata"]["printed_page"] == number - 22
        assert page["source"] == manifest["source_path_or_url"] and page["document_id"] == manifest["source_id"]
        chapter = 1 if number <= 30 else 2 if number <= 38 else 3 if number <= 50 else 4 if number <= 60 else 5
        assert page["metadata"]["chapter"] == chapter
        page_checks.append({"page": number, "chapter": chapter, "printed_page": number - 22, "characters": len(extracted), "stored_text_matches_pdf": True, "metadata_checks_passed": True})

    evidence_checks = []
    for question in questions:
        golds = [{"source_id": question["gold_source_id"], "page": question["gold_page"], "evidence_quote": question["evidence_quote"]}, *question.get("gold_alternatives", [])]
        for gold in golds:
            match = comparable(gold["evidence_quote"]) in comparable(doc[gold["page"] - 1].get_text("text"))
            evidence_checks.append({"id": question["id"], "page": gold["page"], "independent_pdf_text_match": match})

    # Render the pages needing review, plus the edition/copyright and exclusions.
    numbers = [3, 4, 38, 72, *range(49, 72)]
    for start in range(0, len(numbers), 4):
        sheet_doc = pymupdf.open()
        sheet = sheet_doc.new_page(width=1240, height=1640)
        for index, number in enumerate(numbers[start:start + 4]):
            x = (index % 2) * 620
            y = (index // 2) * 820
            sheet.insert_text((x + 12, y + 18), f"PDF page {number}", fontsize=12)
            sheet.show_pdf_page(pymupdf.Rect(x + 10, y + 26, x + 610, y + 810), doc, number - 1)
        sheet.get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(output / f"sheet_{start // 4 + 1:02d}.png")
        sheet_doc.close()
    report = {"pdf_sha256": manifest["sha256"], "pymupdf_version": pymupdf.VersionBind, "page_checks": page_checks, "evidence_checks": evidence_checks, "limitations": "Mechanical source checks and contact sheets support review; this script does not judge semantic support or assign human labels."}
    (output / "source_checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = [check for check in evidence_checks if not check["independent_pdf_text_match"]]
    print(f"Source identity, stored text and metadata: PASS ({len(page_checks)} pages)")
    print(f"Independent evidence matches: {len(evidence_checks) - len(failures)}/{len(evidence_checks)}")
    for failure in failures:
        print(f"REVIEW: {failure}")
    print(f"PDF contact sheets and checks: {output}")


if __name__ == "__main__":
    main()

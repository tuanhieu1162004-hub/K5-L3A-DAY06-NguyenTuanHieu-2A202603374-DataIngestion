"""Validate benchmark inputs without embedding or retrieval experiments."""
import json
import hashlib
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STARTER = Path(__file__).resolve().parents[1]
REPO = STARTER.parent
REQUIRED = {"id", "split", "question", "expected_answer", "gold_source_id", "gold_page", "evidence_quote"}


def canonical(text: str) -> str:
    """Ignore layout whitespace only, not punctuation, words or letter case."""
    return re.sub(r"\s+", " ", text).strip()


def validate(questions: list[dict[str, Any]], pages: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    page_lookup = {(p["document_id"], p["page"]): p for p in pages}
    if len(page_lookup) != len(pages):
        errors.append("Corpus contains duplicate document/page IDs")
    ids = [q.get("id") for q in questions]
    if len(ids) != len(set(ids)):
        errors.append("Question IDs must be unique")
    counts = Counter(q.get("split") for q in questions)
    if len(questions) < 20 or counts["dev"] < 15 or counts["test"] < 5:
        errors.append("Need >=20 questions, >=15 dev and >=5 test")
    filter_count = 0
    test_filter_count = 0
    for q in questions:
        label = q.get("id", "<missing id>")
        missing = REQUIRED - q.keys()
        if missing:
            errors.append(f"{label}: missing {sorted(missing)}")
            continue
        if q["split"] not in ("dev", "test"):
            errors.append(f"{label}: invalid split")
        for key in ("id", "question", "expected_answer", "gold_source_id", "evidence_quote"):
            if not isinstance(q[key], str) or not q[key].strip():
                errors.append(f"{label}: {key} must be a nonempty string")
        filters = q.get("filter")
        if filters is not None:
            filter_count += 1
            test_filter_count += q["split"] == "test"
            if not isinstance(filters, dict) or set(filters) != {"chapter"} or type(filters.get("chapter")) is not int:
                errors.append(f"{label}: filter must contain only an integer chapter")
            elif not re.search(rf"\bchapter\s+{filters['chapter']}\b", q["question"], re.IGNORECASE):
                errors.append(f"{label}: chapter filter must be supplied in the question")
        golds = [{"source_id": q["gold_source_id"], "page": q["gold_page"], "evidence_quote": q["evidence_quote"]}, *q.get("gold_alternatives", [])]
        for gold in golds:
            if not isinstance(gold, dict) or not {"source_id", "page", "evidence_quote"} <= gold.keys():
                errors.append(f"{label}: invalid alternative gold")
                continue
            if type(gold["page"]) is not int or not isinstance(gold["source_id"], str):
                errors.append(f"{label}: invalid gold page/source type")
                continue
            source_page = page_lookup.get((gold["source_id"], gold["page"]))
            if source_page is None:
                errors.append(f"{label}: gold page {gold['page']} is absent from corpus")
                continue
            quote = gold["evidence_quote"]
            if not isinstance(quote, str) or not canonical(quote) or canonical(quote) not in canonical(source_page["text"]):
                errors.append(f"{label}: evidence not found on PDF page {gold['page']}")
            if isinstance(filters, dict) and any(source_page["metadata"].get(key) != value for key, value in filters.items()):
                errors.append(f"{label}: gold metadata does not satisfy supplied filter")
    if filter_count < 3 or test_filter_count < 1:
        errors.append("Need >=3 filtered questions, including >=1 test question")
    return errors


def main() -> None:
    questions = [json.loads(line) for line in (REPO / "benchmark" / "questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    pages = [json.loads(line) for line in (STARTER / "results" / "pages.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = json.loads((REPO / "data" / "manifest.json").read_text(encoding="utf-8"))
    errors = validate(questions, pages)
    reviewed = sum(q.get("review_status") == "accepted" for q in questions)
    corpus_reviewed = sum(p.get("content_review_status") == "accepted" for p in manifest["pages"])
    verified_count = manifest.get("verified_content_page_count")
    corpus_ready = (
        type(verified_count) is int and verified_count >= 30
        and verified_count == corpus_reviewed == len(pages) == len(manifest["pages"])
        and {(manifest["source_id"], p["page"]) for p in manifest["pages"]} == {(p["document_id"], p["page"]) for p in pages}
    )
    frozen_path = REPO / "benchmark/frozen.json"
    frozen_valid = False
    if frozen_path.exists():
        frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
        frozen_valid = all((REPO / name).exists() and hashlib.sha256((REPO / name).read_bytes()).hexdigest() == expected
                           for name, expected in frozen["sha256"].items())
        if not frozen_valid:
            errors.append("Frozen input checksum mismatch")
    report = {
        "checked_at": datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds"),
        "question_count": len(questions),
        "split_counts": dict(Counter(q.get("split") for q in questions)),
        "filtered_question_count": sum(q.get("filter") is not None for q in questions),
        "test_filtered_question_count": sum(q.get("filter") is not None and q.get("split") == "test" for q in questions),
        "question_reviews_accepted": reviewed,
        "corpus_reviews_accepted": corpus_reviewed,
        "corpus_ai_reviews_accepted": sum(p.get("content_review_status") == "accepted" and p.get("reviewed_by") == "Codex (AI)" for p in manifest["pages"]),
        "structure_and_evidence_checks_passed": not errors,
        "ready_for_manual_freeze": not errors and reviewed == len(questions) and corpus_ready,
        "benchmark_frozen": frozen_valid,
        "errors": errors,
        "limitation": "Whitespace matching verifies quote presence only. Accepted input reviews may include explicitly attributed AI review; these are not human coherence or grounding labels. See results/input_review for review provenance.",
    }
    target = STARTER / "results" / "benchmark_validation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Questions: {len(questions)} | dev: {report['split_counts'].get('dev', 0)} | test: {report['split_counts'].get('test', 0)}")
    print(f"Filtered questions: {report['filtered_question_count']} (test: {report['test_filtered_question_count']})")
    print(f"Structure and evidence checks: {'PASS' if not errors else 'FAIL'}")
    print(f"Reviews accepted: questions {reviewed}/{len(questions)}, corpus {corpus_reviewed}/{len(pages)}")
    print(f"Corpus pages reviewed by AI: {report['corpus_ai_reviews_accepted']} (see input_review provenance)")
    print(f"Ready for manual freeze: {report['ready_for_manual_freeze']}")
    print(f"Benchmark frozen and checksums valid: {frozen_valid}")
    print(f"Report: {target}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

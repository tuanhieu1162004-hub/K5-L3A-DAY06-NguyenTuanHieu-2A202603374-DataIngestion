"""Strict single-chunk evidence metrics, including documented alternative golds."""
from collections import defaultdict
from typing import Any
from .validate_benchmark import canonical


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """TODO: check source/page and enough gold evidence; keep hit@1 and hit@3 trace.

    Accept any documented alternative gold evidence. Do not infer human grounding
    or chunk coherence labels from exact string match.
    """
    golds = [{"source_id": question["gold_source_id"], "page": question["gold_page"],
              "evidence_quote": question["evidence_quote"]}, *question.get("gold_alternatives", [])]
    checked = []
    for rank, hit in enumerate(hits[:3], 1):
        matching = [i for i, gold in enumerate(golds)
            if hit["document_id"] == gold["source_id"] and hit["page"] == gold["page"]
            and canonical(gold["evidence_quote"]) in canonical(hit["text"])]
        checked.append({**hit, "rank": rank, "evidence_hit": bool(matching), "matching_gold_indices": matching})
    filters = question.get("filter")
    return {"question_id": question["id"], "split": question["split"], "question": question["question"],
        "expected_answer": question["expected_answer"], "gold_evidence": golds,
        "requested_filter": filters, "hits": checked,
        "hit_at_1": bool(checked and checked[0]["evidence_hit"]),
        "hit_at_3": any(hit["evidence_hit"] for hit in checked),
        "requested_filter_compliant": bool(checked) and all(all(h["metadata"].get(k) == v for k, v in filters.items()) for h in checked) if filters else None,
        "metric_method": "Same source/page and full evidence in one chunk after whitespace folding; equivalent evidence needs separate attributed review."}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """TODO: aggregate Hit@1 and Evidence Hit@3 by strategy and dev/test split."""
    groups = defaultdict(list)
    for trace in traces:
        groups[(trace["strategy"], trace["split"])].append(trace)
    rows = []
    for (strategy, split), items in sorted(groups.items()):
        n = len(items)
        h1 = sum(t["hit_at_1"] for t in items)
        h3 = sum(t["hit_at_3"] for t in items)
        filtered = [t for t in items if t["requested_filter"]]
        rows.append({"strategy": strategy, "split": split, "n": n,
            "hit1_n": h1, "hit3_n": h3, "hit1": h1 / n, "hit3": h3 / n,
            "filter_questions": len(filtered), "requested_filter_compliant_n": sum(t["requested_filter_compliant"] for t in filtered),
            "mean_search_seconds": sum(t["search_seconds"] for t in items) / n})
    return {"rows": rows}

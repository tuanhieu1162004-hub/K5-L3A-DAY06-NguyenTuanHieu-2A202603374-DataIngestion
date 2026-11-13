"""Package the reviewable lab, excluding environments, model cache and secrets."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STARTER))
from src.run import REPO, RESULTS, now, read, save


def main() -> None:
    verification = read(RESULTS / "verification.json")
    assert verification["passed"]
    grading = read(RESULTS / "audit_summary.json")
    graded = grading["graded_records"]
    receipt_path = REPO / "artifacts/publish_receipt.json"
    published = receipt_path.exists() and read(receipt_path).get("remote_head_verified", False)
    ignored = {".venv", ".cache", ".model_cache", "__pycache__", ".git", ".pytest_cache", ".aws", ".codex", ".agents"}
    snapshot = REPO / "artifacts/submission_manifest.json"
    paths = []
    for path in REPO.rglob("*"):
        relative = path.relative_to(REPO)
        if not path.is_file() or set(relative.parts) & ignored or path == snapshot:
            continue
        if path.name.startswith(".env") and path.name != ".env.example":
            continue
        if path.name == "manifest.generated.json" or path.suffix in (".pyc", ".tmp", ".zip"):
            continue
        paths.append(path)
    files = [{"path": p.relative_to(REPO).as_posix(), "bytes": p.stat().st_size,
              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
    save(snapshot, {"packaged_at": now(), "technical_verification_passed": True,
        "graded_records": graded, "grading_complete": grading["grading_complete"],
        "author_independent_manual_review_confirmed": grading["author_independent_manual_review_confirmed"],
        "repository_push_verified": published, "final_submission_confirmed": False,
        "files": files, "note": "Inventory excludes this manifest itself. AI labels are explicitly attributed; author confirmation and actual submission are separate."})
    target = REPO.parent / "K5-L3A-DAY06-NguyenTuanHieu-2A202603374-DataIngestion.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in [*paths, snapshot]:
            archive.write(path, path.relative_to(REPO).as_posix())
    with zipfile.ZipFile(target) as archive:
        names = archive.namelist()
        assert archive.testzip() is None
        assert all(not (set(Path(name).parts) & ignored) for name in names)
        assert all(not Path(name).name.startswith(".env") or Path(name).name == ".env.example" for name in names)
    print(f"ZIP verified: {len(names)} files, {target.stat().st_size} bytes.")
    print(f"Archive: {target}")
    print(f"Graded records: {graded}/90; reviewer/method recorded; repository push verified: {published}.")


if __name__ == "__main__":
    main()

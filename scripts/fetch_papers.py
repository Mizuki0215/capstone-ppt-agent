#!/usr/bin/env python3
"""Reproduce the paper corpus from research/papers_index.csv.

The 40 PDFs under research/pdfs/ are third-party papers (~400 MB). They are
deliberately **not** committed: they are not our work, they bloat git history,
and every one of them can be fetched again from the arXiv id recorded in the
index. This script is what makes the corpus reproducible from a clean clone.

    python3 scripts/fetch_papers.py            # fetch whatever is missing
    python3 scripts/fetch_papers.py --check    # report only, download nothing
    python3 scripts/fetch_papers.py --all      # re-fetch even if present

Naming: <label>_<arxiv-id>.pdf, matching the existing files. A paper counts as
present if any file in research/pdfs/ contains its arXiv id, so files that were
renamed by hand are not downloaded twice.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "research" / "papers_index.csv"
OUTDIR = ROOT / "research" / "pdfs"
UA = "capstone-ppt-agent/0.1 (paper corpus fetch; contact: author)"
DELAY_S = 1.5


def ids_on_disk() -> set[str]:
    if not OUTDIR.is_dir():
        return set()
    return {p.name for p in OUTDIR.iterdir() if p.is_file()}


def download(arxiv_id: str, dest: Path) -> tuple[bool, str]:
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as exc:  # network, 404, rate limit
        return False, f"{type(exc).__name__}: {exc}"
    if not data.startswith(b"%PDF"):
        return False, "not a PDF (arXiv may be rate limiting)"
    dest.write_bytes(data)
    return True, f"{len(data) / 1e6:.1f} MB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only")
    ap.add_argument("--all", action="store_true", help="re-fetch existing files")
    args = ap.parse_args()

    if not INDEX.is_file():
        print(f"missing index: {INDEX}", file=sys.stderr)
        return 2
    OUTDIR.mkdir(parents=True, exist_ok=True)

    with INDEX.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    on_disk = ids_on_disk()
    have = todo = 0
    failures: list[tuple[str, str]] = []

    for row in rows:
        arxiv_id = (row.get("arxiv") or "").strip()
        label = (row.get("label") or "paper").strip().replace(" ", "-")
        if not arxiv_id:
            continue
        present = any(arxiv_id in name for name in on_disk)
        if present and not args.all:
            have += 1
            continue
        todo += 1
        if args.check:
            print(f"  missing  {label:28} {arxiv_id}")
            continue
        dest = OUTDIR / f"{label}_{arxiv_id}.pdf"
        ok, note = download(arxiv_id, dest)
        print(f"  {'ok      ' if ok else 'FAILED  '} {label:28} {arxiv_id}  {note}")
        if ok:
            on_disk.add(dest.name)
        else:
            failures.append((label, note))
        time.sleep(DELAY_S)

    print(f"\n{len(rows)} indexed · {have} already present · {todo} to fetch")
    if failures:
        print(f"{len(failures)} failed:")
        for label, note in failures:
            print(f"  - {label}: {note}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

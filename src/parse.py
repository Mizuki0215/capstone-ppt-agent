#!/usr/bin/env python3
"""Stage 1 - parse a paper PDF into sections and figures.

Runs on a Python that has PyMuPDF (fitz). Writes a JSON contract consumed by
compose.py. Target: single-column English research papers.
"""
import argparse
import json
import os
import re
import statistics
import sys
from pathlib import Path

import fitz

import figures

HEADING_PAT = re.compile(
    r"^(abstract|introduction|related work|background|method|methods|approach|"
    r"experiments?|evaluation|results?|analysis|discussion|limitations?|"
    r"conclusion|conclusions|references)\b",
    re.I,
)
NUMBERED = re.compile(r"^\d+(\.\d+)*\s+[A-Z]")
NUMBERING = re.compile(r"^\d{1,2}(?:\.\d+)*\.?\s+")
CAPTION = re.compile(r"^(figure|fig\.?|table)\s*\d+", re.I)


def clean_heading(title):
    r"""Drop a leading section number: "1. Introduction" -> "Introduction".

    The separator must be whitespace, so "5G Networks" and "2023 Results" keep
    their leading number. An earlier version stripped only `\d+`, which turned
    "1. Introduction" into ". Introduction" on any paper that numbers sections
    with a dot (AISSA in our corpus).
    """
    out = NUMBERING.sub("", title.strip()).strip()
    return out or title.strip()


def lines(doc):
    """Yield (page, text, size, bold) for every text line."""
    for pno, page in enumerate(doc, start=1):
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                if not text:
                    continue
                size = max(s["size"] for s in spans)
                bold = any("Bold" in s.get("font", "") or "Semibold" in s.get("font", "")
                           for s in spans)
                yield pno, text, size, bold


def find_title(doc):
    if doc.metadata and doc.metadata.get("title"):
        t = doc.metadata["title"].strip()
        if 8 < len(t) < 200:
            return t
    first = doc[0].get_text().strip().split("\n")
    for line in first[:6]:
        line = line.strip()
        if 8 < len(line) < 160 and not line.lower().startswith("arxiv"):
            return line
    return "Untitled paper"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    all_lines = list(lines(doc))
    if not all_lines:
        sys.exit("no extractable text - is this a scanned PDF?")

    sizes = [s for _, t, s, _ in all_lines if len(t) > 25]
    med = statistics.median(sizes) if sizes else 10.0

    freq = {}
    for pno, text, size, bold in all_lines:
        key = text.strip().lower()
        if 3 < len(key) < 120:
            freq[key] = freq.get(key, 0) + 1
    running = {k for k, v in freq.items() if v >= 3}

    sections = []
    current = None
    started = False
    for pno, text, size, bold in all_lines:
        words = text.split()
        caps_ratio = (sum(1 for w in words if w[:1].isupper()) / len(words)) if words else 0
        is_std = bool(NUMBERED.match(text)) or (bool(HEADING_PAT.match(text)) and len(words) <= 3)
        looks_heading = (
            len(text) <= 60
            and text.strip().lower() not in running
            and sum(c.isalpha() for c in text) >= 3
            and not re.search(r",\s+[a-z]", text)
            and not re.search(r"\b(January|February|March|April|May|June|July|August|"
                              r"September|October|November|December)\b", text)
            and not text.endswith(".")
            and not text.endswith("-")
            and not re.search(r"\((?:19|20)\d{2}\)", text)
            and not CAPTION.match(text)
            and (is_std or (size >= med + 2.2 and bold and caps_ratio >= 0.5))
        )
        if looks_heading:
            name = text.strip()
            if re.match(r"^references\b", name, re.I):
                break
            # skip the paper title itself (first heading, no body yet)
            if not started and len(sections) == 0 and current is None:
                current = {"title": name, "page": pno, "lines": []}
                started = True
                continue
            if current and current["lines"]:
                sections.append(current)
            current = {"title": name, "page": pno, "lines": []}
            started = True
        elif current is not None:
            current["lines"].append(text)
    if current and current["lines"]:
        sections.append(current)

    out_sections = []
    for s in sections:
        body = " ".join(s["lines"])
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < 80:
            continue
        out_sections.append({
            "title": clean_heading(s["title"]),
            "page": s["page"],
            "text": body,
        })

    # figures / tables: clip the region above each caption (see figures.py).
    # Captions alone would put "Figure 3: ..." on a slide with nothing above it.
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.splitext(os.path.basename(args.pdf))[0])
    figs = figures.extract(args.pdf, Path("build/figures") / stem, stem)
    captions_seen = sum(len(figures.find_captions(p)) for p in doc)
    if not figs:   # scanned PDF, or no caption had ink above it
        for pno, text, size, bold in all_lines:
            if CAPTION.match(text) and 10 < len(text) < 300:
                figs.append({"caption": re.sub(r"\s+", " ", text).strip(), "page": str(pno),
                             "image": None})

    payload = {
        "source": args.pdf,
        "title": find_title(doc),
        "pages": doc.page_count,
        "median_font": round(med, 1),
        "sections": out_sections,
        "captions": captions_seen,
        "figures": figs[:40],
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1)
    with_image = sum(1 for f in figs if f.get("image"))
    print(f"sections={len(out_sections)} captions={captions_seen} "
          f"figures={len(figs)} (clipped={with_image}) -> {args.out}")
    for s in out_sections[:12]:
        print(f"  p{s['page']:<3} {s['title'][:60]:60s} {len(s['text']):>5} chars")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage 1 - parse a paper PDF into sections and figures.

Runs on a Python that has PyMuPDF. Writes a JSON contract consumed by
compose.py. Target: single-column English research papers.

Four things the parser has to get right, in the order they go wrong:

  1. ligatures. PyMuPDF returns U+FB01 for "fi", so 148 occurrences in one paper
     reached the slide as "signicant". They are normalised here, before any
     sentence is cut, because the evidence matching downstream compares strings.
  2. headings. A heading is not marked in a PDF; it is the line that is larger
     and bolder than the body. The word list below catches the headings whose
     type is not distinctive, which is how "Dataset" used to end up inside
     "Approach".
  3. text inside figures. Diagrams carry their own labels ("Text Encoder",
     "Image Encoder"). Those labels sit inside the band figures.py already
     computes, so the band is used to drop them from the body text.
  4. stopping. Everything after "References" or "Appendix" is not talk material.
"""
import argparse
import json
import os
import re
import statistics
import sys
from pathlib import Path

import pymupdf                # `import fitz` is deprecated in 2.0; this works on 1.24+

import figures

HEADING_PAT = re.compile(
    r"^(abstract|introduction|related work|background|method|methods|approach|"
    r"experiments?|evaluation|results?|analysis|discussion|limitations?|"
    r"dataset|data|implementation|training|inference|notation|"
    r"conclusion|conclusions|references)\b",
    re.I,
)
# anything from here on is apparatus, not argument
STOP_PAT = re.compile(r"^(references|appendix|appendices|supplementary|acknowledg)", re.I)
NUMBERED = re.compile(r"^\d+(\.\d+)*\s+[A-Z]")
NUMBERING = re.compile(r"^\d{1,2}(?:\.\d+)*\.?\s+")
CAPTION = re.compile(r"^(figure|fig\.?|table)\s*\d+", re.I)
# front matter and footnotes that are never talk material
ARTIFACT = re.compile(r"^(project webpage|arxiv|copyright\s*©|https?://|all rights reserved)", re.I)

# Captions are stored separately in figures[]; letting them into the body means
# a 200-character caption can be chosen as a bullet.
DROP_CAPTION_LINES = True


def clean_heading(title):
    r"""Drop a leading section number: "1. Introduction" -> "Introduction".

    The separator must be whitespace, so "5G Networks" and "2023 Results" keep
    their leading number. An earlier version stripped only `\d+`, which turned
    "1. Introduction" into ". Introduction" on any paper that numbers sections
    with a dot (AISSA in our corpus).
    """
    out = NUMBERING.sub("", title.strip()).strip()
    return out or title.strip()


def lines(doc, bands=None):
    """Yield (page, text, size, bold, bbox) for every text line outside figures.

    `bands` is {page: [Rect]} from figures.figure_bands(); a block whose box
    falls inside one is a label drawn as part of a figure, not prose.
    """
    bands = bands or {}
    skipping_caption = False
    for pno, page in enumerate(doc, start=1):
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            if block.get("type") != 0:
                continue
            box = pymupdf.Rect(block["bbox"])
            if any(box.intersects(b) for b in bands.get(pno, [])):
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = figures.deligature(figures.join_spans(spans))
                if not text:
                    continue
                if DROP_CAPTION_LINES and CAPTION.match(text):
                    # a caption often wraps: drop its continuation lines too
                    skipping_caption = not text.rstrip().endswith(".")
                    continue
                if skipping_caption:
                    skipping_caption = not text.rstrip().endswith(".")
                    continue
                if ARTIFACT.match(text):
                    continue
                size = max(s["size"] for s in spans)
                bold = any("Bold" in s.get("font", "") or "Semibold" in s.get("font", "")
                           for s in spans)
                yield pno, text, size, bold, tuple(box)


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

    doc = pymupdf.open(args.pdf)
    bands = figures.figure_bands(doc)
    all_lines = list(lines(doc, bands))
    if not all_lines:
        sys.exit("no extractable text - is this a scanned PDF?")

    sizes = [s for _, t, s, _, _ in all_lines if len(t) > 25]
    med = statistics.median(sizes) if sizes else 10.0

    freq = {}
    for pno, text, size, bold, box in all_lines:
        key = text.strip().lower()
        if 3 < len(key) < 120:
            freq[key] = freq.get(key, 0) + 1
    running = {k for k, v in freq.items() if v >= 3}

    sections = []
    current = None
    started = False
    last_page = None
    for idx, (pno, text, size, bold, box) in enumerate(all_lines):
        page_opens = pno != last_page
        last_page = pno
        nxt = all_lines[idx + 1][1] if idx + 1 < len(all_lines) else ""
        prose_follows = len(nxt.split()) >= 6 and bool(re.search(r"\b[a-z]{4,}\b", nxt))
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
        # a supplement often opens a page with an unnumbered, unelevated title
        # ("Details of the Data Processing Steps"); sizes alone miss it
        opens_a_page = (
            page_opens
            and 3 <= len(words) <= 9
            and text[:1].isupper()
            and caps_ratio >= 0.6
            and not text.endswith((".", ",", ";", ":"))
            and not CAPTION.match(text)
            and prose_follows
        )
        looks_heading = looks_heading or opens_a_page
        if looks_heading:
            name = text.strip()
            if STOP_PAT.match(name):
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
        body = figures.deligature(" ".join(s["lines"]))
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < 80:
            continue
        out_sections.append({
            "title": clean_heading(s["title"]),
            "page": s["page"],
            "text": body,
        })

    # A talk ends at the conclusion. Anything after it - supplementary details,
    # technical appendices - is apparatus, and a 12 minute talk never reaches it.
    for i, sec in enumerate(out_sections):
        if re.match(r"^conclusions?\b", sec["title"], re.I):
            out_sections = out_sections[: i + 1]
            break

    # figures / tables: clip the region above each caption (see figures.py).
    # Captions alone would put "Figure 3: ..." on a slide with nothing above it.
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.splitext(os.path.basename(args.pdf))[0])
    figs = figures.extract(args.pdf, Path("build/figures") / stem, stem)
    captions_seen = sum(len(figures.find_captions(p)) for p in doc)
    if not figs:   # scanned PDF, or no caption had ink above it
        for pno, page in enumerate(doc, start=1):
            for _rect, text in figures.find_captions(page):
                figs.append({"caption": text, "page": str(pno), "image": None})

    payload = {
        "source": args.pdf,
        "pymupdf": pymupdf.__version__,
        "title": find_title(doc),
        "pages": doc.page_count,
        "median_font": round(med, 1),
        "sections": out_sections,
        "captions": captions_seen,
        "figures": figs[:40],
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    with_image = sum(1 for f in figs if f.get("image"))
    print(f"pymupdf={pymupdf.__version__} sections={len(out_sections)} "
          f"captions={captions_seen} figures={len(figs)} (clipped={with_image}) -> {args.out}")
    for s in out_sections[:12]:
        print(f"  p{s['page']:<3} {s['title'][:60]:60s} {len(s['text']):>5} chars")


if __name__ == "__main__":
    main()

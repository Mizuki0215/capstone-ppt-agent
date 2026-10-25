#!/usr/bin/env python3
"""Extract figures from a paper PDF by clipping the region above each caption.

Why not pull embedded images: in the corpus the real figures are vector
drawings. On PPTAgent p2 there are 39 embedded images (icons, 32x32) and 160
drawing paths; the actual Figure 2 is a set of paths. Extracting "the images"
therefore yields icons, or nothing. So each figure is *clipped and rendered*.

The rule: a block's extent is where ink stops being white.
  1. find the caption block ("Figure 3: ..." / "Table 2: ...")
  2. take the vertical band above it, bounded by the nearest body-text paragraph
     in the same column, so a paragraph above the caption is never swallowed
  3. rasterise that band and keep the bounding box of non-white pixels
  4. clip-render at FIGURE_DPI and save

The same bands are handed to parse.py, which uses them to drop text drawn
inside a figure ("Text Encoder", "Image Encoder") from the body text.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pymupdf

CAPTION = re.compile(r"^(figure|fig\.?|table)\s*\d+", re.I)
FIGURE_DPI = 200
MIN_W, MIN_H = 150.0, 100.0      # pt; below this it is a rule, a logo or a letter
MIN_BAND_H = 40.0
WHITE_CUTOFF = 250               # a channel below this counts as ink
GAP_RATIO = 0.12                 # of the font size; below this, spans are one word

LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
             "\ufb03": "ffi", "\ufb04": "ffl"}


def deligature(text: str) -> str:
    """PDFs encode "fi" as U+FB01. Left alone, "significant" reaches a slide as
    "signicant" and every evidence comparison downstream fails."""
    for bad, good in LIGATURES.items():
        if bad in text:
            text = text.replace(bad, good)
    return text


def _block_text(block) -> str:
    lines = [join_spans(line.get("spans", [])) for line in block.get("lines", [])]
    return re.sub(r"\s+", " ", " ".join(l for l in lines if l)).strip()


def join_spans(spans, gap_ratio: float = GAP_RATIO) -> str:
    """Join a line's spans, inserting a space only where the PDF left a gap.

    Neither extreme works: joining with "" turns "PPTA|GENT" (a word split by
    kerning) into "PPTAGENT" but also "Stage|I:" into "StageI"; joining with " "
    does the opposite. The horizontal gap between span boxes distinguishes them.
    """
    out: list[str] = []
    prev_x1 = None
    prev_size = 10.0
    for sp in spans:
        text = sp.get("text", "")
        size = sp.get("size") or prev_size
        if prev_x1 is not None and text and not text.startswith(" "):
            if sp["bbox"][0] - prev_x1 > gap_ratio * size:
                out.append(" ")
        out.append(text)
        prev_x1 = sp["bbox"][2]
        prev_size = size
    return deligature(re.sub(r"\s+", " ", "".join(out)).strip())


def text_blocks(page) -> list[tuple[pymupdf.Rect, str]]:
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        text = _block_text(block)
        if text:
            out.append((pymupdf.Rect(block["bbox"]), text))
    return out


def find_captions(page) -> list[tuple[pymupdf.Rect, str]]:
    caps = []
    for rect, text in text_blocks(page):
        if CAPTION.match(text) and 10 < len(text) < 400:
            caps.append((rect, re.sub(r"\s+", " ", text)))
    return caps


def same_column(a: pymupdf.Rect, b: pymupdf.Rect) -> bool:
    """True when two rectangles share most of their horizontal extent."""
    overlap = min(a.x1, b.x1) - max(a.x0, b.x0)
    if overlap <= 0:
        return False
    return overlap >= 0.5 * min(a.width, b.width)


def is_paragraph(rect, text) -> bool:
    """Body text, not a label inside a figure.

    This is the correction that matters: figures carry their own text ("Stage I:
    Presentation Analysis"), and stopping at *any* text block cut the band off
    inside the figure, so most captions produced no image. A paragraph has
    several words and real height; a label does not.
    """
    return len(text.split()) >= 8 and rect.height >= 18


def figure_band(page_rect, cap_rect, blocks, margin=36.0):
    """Band above the caption, stopping at the nearest *paragraph*, not label."""
    top = page_rect.y0 + margin
    for rect, text in blocks:
        if rect.y1 <= cap_rect.y0 + 1 and same_column(rect, cap_rect) and is_paragraph(rect, text):
            top = max(top, rect.y1)
    return pymupdf.Rect(cap_rect.x0, top, cap_rect.x1, cap_rect.y0 - 2)


def page_bands(page) -> list[tuple[pymupdf.Rect, pymupdf.Rect]]:
    """[(caption_rect, band)] for one page."""
    blocks = text_blocks(page)
    return [(rect, figure_band(page.rect, rect, blocks)) for rect, _ in find_captions(page)]


def figure_bands(doc) -> dict[int, list[pymupdf.Rect]]:
    """{page_number: [band]} - used by parse.py to drop text drawn inside figures."""
    out: dict[int, list[pymupdf.Rect]] = {}
    for pno, page in enumerate(doc, start=1):
        out[pno] = [band for _cap, band in page_bands(page)]
    return out


def ink_bbox(page, band: pymupdf.Rect):
    """Bounding box of non-white pixels inside the band, in PDF points."""
    if band.height < MIN_BAND_H or band.width < 10:
        return None
    pix = page.get_pixmap(clip=band, dpi=FIGURE_DPI, colorspace=pymupdf.csRGB)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    ink = (arr < WHITE_CUTOFF).any(axis=2)
    if not ink.any():
        return None
    ys, xs = np.where(ink)
    sx, sy = band.width / pix.width, band.height / pix.height
    return pymupdf.Rect(band.x0 + xs.min() * sx, band.y0 + ys.min() * sy,
                        band.x0 + (xs.max() + 1) * sx, band.y0 + (ys.max() + 1) * sy)


def extract(pdf_path: str, out_dir: Path, stem: str) -> list[dict]:
    """Clip every caption's figure and save it as PNG."""
    doc = pymupdf.open(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for pno, page in enumerate(doc, start=1):
        bands = page_bands(page)
        captions = [c for c, _ in find_captions(page)]
        for i, ((cap_rect, caption), (_c2, band)) in enumerate(zip(find_captions(page), bands), start=1):
            box = ink_bbox(page, band)
            if box is None:
                continue
            pad = 4.0
            clip = pymupdf.Rect(box.x0 - pad, box.y0 - pad, box.x1 + pad, box.y1 + pad) & page.rect
            if clip.width < MIN_W or clip.height < MIN_H:
                continue
            kind = "table" if caption.lower().startswith("table") else "figure"
            name = f"p{pno:02d}_{i:02d}_{kind}.png"
            dest = out_dir / name
            page.get_pixmap(clip=clip, dpi=FIGURE_DPI).save(dest)
            records.append({
                "caption": caption,
                "page": str(pno),
                "image": str(dest.relative_to(Path.cwd())) if dest.is_relative_to(Path.cwd()) else str(dest),
                "bbox": [round(v, 1) for v in (clip.x0, clip.y0, clip.x1, clip.y1)],
                "area": round(clip.width * clip.height),
            })
    return records

"""Real font metrics for the text-fit gate (G5) and the contrast gate (G4).

Text height is computed with Arial's real advance widths at 8x device scale,
not with a per-character average. That is the difference between "the box
looks big enough" and "this string needs 5.4 in in a 5.0 in box".
"""
from __future__ import annotations

import re
from functools import lru_cache

from PIL import ImageFont

from . import spec

SCALE = 8  # px per pt
_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# CJK / full-width punctuation breaks anywhere; latin words break on spaces.
_TOKEN = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]"
                    r"|[^\s\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]+\s*")


@lru_cache(maxsize=512)
def _font(size_pt: float, bold: bool) -> ImageFont.FreeTypeFont:
    px = max(6, int(round(size_pt * SCALE)))
    return ImageFont.truetype(_BOLD if bold else _REG, px)


def wrap(text: str, size_pt: float, bold: bool, width_in: float) -> list[str]:
    if not text.strip():
        return [""]
    f = _font(size_pt, bold)
    limit = width_in * 72 * SCALE
    lines: list[str] = []
    cur = ""
    for tok in _TOKEN.findall(text):
        cand = cur + tok
        if not cur or f.getlength(cand.rstrip()) <= limit:
            cur = cand
        else:
            lines.append(cur.rstrip())
            cur = tok.lstrip()
    lines.append(cur.rstrip())
    return lines


def paragraph_height(text: str, size_pt: float, bold: bool, width_in: float) -> float:
    n = len(wrap(text, size_pt, bold, width_in))
    return n * size_pt * spec.LINE_HEIGHT / 72.0


def required_height(paras: list[tuple[str, float, bool]], width_in: float,
                    indent_in: float = 0.0, gap_pt: float = spec.PARA_GAP_PT) -> float:
    """Height in inches needed to lay `paras` out inside a box of `width_in`."""
    avail = max(0.2, width_in - 2 * spec.BOX_MX - indent_in)
    h = sum(paragraph_height(t, s, b, avail) for t, s, b in paras)
    h += max(0, len(paras) - 1) * gap_pt / 72.0
    return h


def usable_height(box_h: float) -> float:
    return max(0.05, box_h - 2 * spec.BOX_MY)


# --- WCAG 2.2 relative luminance / contrast ratio ---------------------------

def _lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = (_lin(float(v)) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def is_large(size_pt: float, bold: bool) -> bool:
    return size_pt >= 24 or (bold and size_pt >= 18.66)


def threshold_for(size_pt: float, bold: bool) -> float:
    return spec.CONTRAST_AA_LARGE if is_large(size_pt, bold) else spec.CONTRAST_AA

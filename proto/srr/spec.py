"""Deck specification: the intermediate representation the loop edits.

Everything the repair operators touch lives here, so a repair is a pure
mutation of this IR; the .pptx is always a projection of it.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Optional

RGB = tuple[int, int, int]

INK: RGB = (26, 26, 26)
NAVY: RGB = (31, 58, 95)
MUTED: RGB = (95, 107, 122)
ACCENT: RGB = (200, 83, 61)
PAPER: RGB = (255, 255, 255)
PANEL: RGB = (242, 244, 247)
WHITE: RGB = (255, 255, 255)

# geometry (inches)
SLIDE_W = 13.333
SLIDE_H = 7.5
MARGIN = 0.6
SAFE_L, SAFE_T = 0.25, 0.25
SAFE_R, SAFE_B = SLIDE_W - 0.25, 6.95
BODY_TOP = 1.55
BODY_BOTTOM = 6.85
TEXT_W = SLIDE_W - 2 * MARGIN

# text metrics assumptions (documented in the report)
BOX_MX = 0.1          # default text-frame left/right inset, inches
BOX_MY = 0.05         # default text-frame top/bottom inset, inches
BULLET_INDENT = 0.28  # hanging indent, inches
PARA_GAP_PT = 9
LINE_HEIGHT = 1.2     # single spacing as a multiple of point size

# gate thresholds (see docs/evidence_plan.md §2)
FIT_RATIO = 0.95
MIN_BODY_PT = 18
MIN_TITLE_PT = 28
MAX_BULLETS = 6
MAX_CHARS = 140
OVERLAP_FRAC = 0.05
CONTRAST_AA = 4.5
CONTRAST_AA_LARGE = 3.0


@dataclass
class Block:
    """One text frame on a slide."""

    items: list[str]
    kind: str = "bullets"          # bullets | plain | kpi
    x: float = MARGIN
    y: float = BODY_TOP
    w: float = TEXT_W
    h: float = 4.6
    size: int = 22
    bold: bool = False
    color: RGB = INK
    fill: Optional[RGB] = None
    align: str = "left"

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def clone(self) -> "Block":
        return copy.deepcopy(self)


@dataclass
class Slide:
    title: str
    blocks: list[Block] = field(default_factory=list)
    layout: str = "content"        # content | cover
    notes: list[str] = field(default_factory=list)

    def body_text(self) -> str:
        return " ".join(" ".join(b.items) for b in self.blocks)


@dataclass
class Deck:
    title: str
    slides: list[Slide] = field(default_factory=list)

    def clone(self) -> "Deck":
        return copy.deepcopy(self)


def para_specs(block: Block) -> list[tuple[str, float, bool, RGB]]:
    """(text, size_pt, bold, colour) per paragraph — single source of truth
    shared by the renderer and the text-fit gate."""
    if block.kind == "kpi":
        if not block.items:
            return []
        out = [(block.items[0], 44.0, True, block.color)]
        if len(block.items) > 1:
            out.append((block.items[1], 15.0, False, block.color))
        return out
    return [(t, float(block.size), block.bold, block.color) for t in block.items]


def bullet_indent(block: Block) -> float:
    return BULLET_INDENT if block.kind == "bullets" else 0.0

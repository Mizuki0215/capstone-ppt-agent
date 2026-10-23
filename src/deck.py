#!/usr/bin/env python3
"""The deck contract: what a generated deck *is*, before anything is drawn.

Three artefacts, three jobs — the split follows ReDeck's state tuple
`st = (dt, rt, Ct)`, where dt is the editable deck, rt the measured geometry and
Ct the diagnostics:

    deck.json    dt   what to say: claims, headlines, bullets, notes  (text layer)
    layout.json  rt   where it went: resolved boxes after render      (layout layer)
    metrics.json Ct   what is wrong with it: gate violations, SRR     (measurement)

The point of the split is enforcement, not tidiness. The repair loop may edit
layout.json and may never edit deck.json. If it could edit both, "the loop
improved the deck" would no longer separate layout repair from rewriting, and
the whole ablation (A2 - A1) would be uninterpretable.

Text integrity is checked here as invariants:
  - every bullet names the claim it came from
  - no slide cites a claim that was not selected
  - no figure reference resolves to nothing
  - the time budget adds up to the talk length
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from schema import Claim, Decision, Requirement, SectionType

SCHEMA_VERSION = "1.0"
ROLES = ("title", "agenda", "problem", "method", "result", "figure", "conclusion")
ORIGINS = ("llm", "human", "heuristic")
SIDES = ("deck", "layout")


class DeckError(ValueError):
    """A deck that would produce a slide with no defensible provenance."""


@dataclass
class Bullet:
    text: str
    claim_id: str
    importance: int = 3

    def to_dict(self) -> dict:
        return {"text": self.text, "claim_id": self.claim_id, "importance": self.importance}

    @classmethod
    def from_dict(cls, d: dict) -> "Bullet":
        return cls(text=str(d["text"]), claim_id=str(d["claim_id"]),
                   importance=int(d.get("importance", 3)))


@dataclass
class Notes:
    """Speaker notes, with the two things that make them notes and not bullets."""

    text: str
    target_sec: int = 90
    transition: str = ""       # the sentence that hands over to the next slide

    def to_dict(self) -> dict:
        return {"text": self.text, "target_sec": self.target_sec,
                "transition": self.transition}

    @classmethod
    def from_dict(cls, d: dict) -> "Notes":
        return cls(text=str(d.get("text", "")), target_sec=int(d.get("target_sec", 90)),
                   transition=str(d.get("transition", "")))


@dataclass
class Figure:
    figure_id: str
    page: int
    caption: str
    image: str | None = None
    bbox: list[float] = field(default_factory=list)
    area: int = 0
    kind: str = "figure"

    def to_dict(self) -> dict:
        return {"figure_id": self.figure_id, "page": self.page, "caption": self.caption,
                "image": self.image, "bbox": self.bbox, "area": self.area, "kind": self.kind}

    @classmethod
    def from_dict(cls, d: dict) -> "Figure":
        cap = str(d.get("caption", ""))
        return cls(figure_id=str(d["figure_id"]), page=int(d.get("page", 0)), caption=cap,
                   image=d.get("image"), bbox=list(d.get("bbox", [])),
                   area=int(d.get("area", 0)),
                   kind="table" if cap.lower().startswith("table") else "figure")


@dataclass
class Slide:
    index: int
    role: str
    section_type: SectionType
    headline: str
    claim_ids: list[str] = field(default_factory=list)
    bullets: list[Bullet] = field(default_factory=list)
    notes: Notes | None = None
    figure_id: str | None = None
    budget_sec: int = 90
    origin: str = "llm"

    def to_dict(self) -> dict:
        return {"index": self.index, "role": self.role,
                "section_type": self.section_type.value, "headline": self.headline,
                "claim_ids": self.claim_ids,
                "bullets": [b.to_dict() for b in self.bullets],
                "notes": self.notes.to_dict() if self.notes else None,
                "figure_id": self.figure_id, "budget_sec": self.budget_sec,
                "origin": self.origin}


@dataclass
class Deck:
    title: str
    requirement: Requirement
    claims: list[tuple[Claim, Decision]] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    slides: list[Slide] = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    human_edits: list[dict] = field(default_factory=list)

    # ---- serialisation ---------------------------------------------------- #
    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "title": self.title,
            "requirement": {
                "duration_min": self.requirement.duration_min,
                "audience": self.requirement.audience,
                "focus": list(self.requirement.focus),
                "must_include": [s.value for s in self.requirement.must_include],
                "must_exclude": [s.value for s in self.requirement.must_exclude],
            },
            "claims": [{
                "claim_id": c.claim_id, "section_type": c.section_type.value,
                "importance": c.importance, "text": c.text, "evidence": c.evidence,
                "selected": d.selected, "rule": d.rule, "why": d.why,
            } for c, d in self.claims],
            "figures": [f.to_dict() for f in self.figures],
            "slides": [s.to_dict() for s in self.slides],
            "meta": self.meta,
            "metrics": self.metrics,
            "human_edits": self.human_edits,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=1, ensure_ascii=False))

    def selected_claim_ids(self) -> set[str]:
        return {c.claim_id for c, d in self.claims if d.selected}

    # ---- invariants -------------------------------------------------------- #
    def validate(self) -> list[str]:
        """Return every broken invariant, not just the first one."""
        errs: list[str] = []
        ids = [c.claim_id for c, _ in self.claims]
        if len(ids) != len(set(ids)):
            errs.append("duplicate claim_id")
        fig_ids = [f.figure_id for f in self.figures]
        if len(fig_ids) != len(set(fig_ids)):
            errs.append("duplicate figure_id")
        selected = self.selected_claim_ids()

        for c, d in self.claims:
            if d.claim_id != c.claim_id:
                errs.append(f"claim {c.claim_id}: decision belongs to {d.claim_id}")
            if not c.evidence:
                errs.append(f"claim {c.claim_id}: no evidence handle")

        if len(self.slides) < 3:
            errs.append("fewer than three slides")
        for i, s in enumerate(self.slides):
            if s.role not in ROLES:
                errs.append(f"slide {i}: unknown role {s.role!r}")
            if s.origin not in ORIGINS:
                errs.append(f"slide {i}: unknown origin {s.origin!r}")
            for cid in s.claim_ids:
                if cid not in selected:
                    errs.append(f"slide {i}: cites unselected claim {cid}")
            for b in s.bullets:
                if b.claim_id not in selected:
                    errs.append(f"slide {i}: bullet cites unselected claim {b.claim_id}")
                if b.claim_id not in s.claim_ids:
                    errs.append(f"slide {i}: bullet cites {b.claim_id} not listed on the slide")
                if not b.text.strip():
                    errs.append(f"slide {i}: empty bullet")
            if s.figure_id and s.figure_id not in fig_ids:
                errs.append(f"slide {i}: figure {s.figure_id} does not exist")
            if s.notes and s.notes.target_sec <= 0:
                errs.append(f"slide {i}: notes target_sec must be positive")

        declared = self.requirement.duration_min * 60
        total = sum(s.budget_sec for s in self.slides)
        if self.slides and abs(total - declared) > 30:
            errs.append(f"budget {total}s does not match the {declared}s talk")
        return errs

    def check(self) -> None:
        errs = self.validate()
        if errs:
            raise DeckError("; ".join(errs))


# --------------------------------------------------------------------------- #
# prompt interface: one builder, so eight section types cannot drift apart
# --------------------------------------------------------------------------- #

PROMPT = {
    SectionType.MOTIVATION: {
        "goal": "why the audience should care, in one breath",
        "bullets": "2-3",
        "shape": "a problem the audience recognises, then the gap",
        "forbid": "no method detail, no numbers unless quoted from the evidence",
    },
    SectionType.PROBLEM: {
        "goal": "state precisely what is being solved",
        "bullets": "2-3",
        "shape": "input, desired output, why the obvious approach is not enough",
        "forbid": "no results, no evaluation claims",
    },
    SectionType.BACKGROUND: {
        "goal": "only the terms the rest of the talk depends on",
        "bullets": "2-3",
        "shape": "definition, then why it matters here",
        "forbid": "no history, no literature survey",
    },
    SectionType.METHOD: {
        "goal": "how it works, well enough to be trusted",
        "bullets": "3-4",
        "shape": "the pipeline in order; name the one idea that is new",
        "forbid": "no ablations, no numbers that are not in the evidence",
    },
    SectionType.SETUP: {
        "goal": "what was compared against what",
        "bullets": "1-3",
        "shape": "datasets, baselines, metric",
        "forbid": "no results",
    },
    SectionType.RESULTS: {
        "goal": "the headline number and what it means",
        "bullets": "2-4",
        "shape": "each bullet carries a number that appears in the evidence",
        "forbid": "no new numbers, no rounding up, no interpretation beyond the data",
    },
    SectionType.ANALYSIS: {
        "goal": "which part of the method is doing the work",
        "bullets": "2-3",
        "shape": "one contrast per bullet: with / without, more / less",
        "forbid": "no new experiments",
    },
    SectionType.LIMITATIONS: {
        "goal": "one honest boundary",
        "bullets": "1-2",
        "shape": "what does not hold, and under what conditions",
        "forbid": "no defensive framing, no promises about future work",
    },
    SectionType.CONCLUSION: {
        "goal": "what to remember, and what is next",
        "bullets": "2-3",
        "shape": "takeaway, then one forward-looking sentence",
        "forbid": "no new claims, no claims already dropped from the talk",
    },
    SectionType.RELATED: {
        "goal": "usually dropped for a short talk",
        "bullets": "0-2",
        "shape": "only if the talk depends on the comparison",
        "forbid": "no list of citations",
    },
}


def build_prompt(slide: Slide, requirement: Requirement, evidence: list[tuple[str, str]],
                 figure_caption: str | None = None) -> str:
    """The one place a generation prompt is assembled.

    `evidence` is [(claim_id, text)] drawn from the slide's own claims only. That
    allow-list is the strongest on-topic control we have: the model cannot drift
    into material it was never shown, and the V1 numeric check can verify every
    number against the text that was actually in front of it.
    """
    spec = PROMPT[slide.section_type]
    lines = [
        f"ROLE: {slide.section_type.value} slide — {spec['goal']}",
        f"REQUIREMENT: {requirement.duration_min} minutes, audience: {requirement.audience}"
        + (f", focus: {', '.join(requirement.focus)}" if requirement.focus else ""),
        f"HEADLINE: {slide.headline}",
        f"BULLETS: {spec['bullets']}, each at most 14 words",
        f"SHAPE: {spec['shape']}",
        f"FORBIDDEN: {spec['forbid']}",
        "EVIDENCE (this is all you may use; do not add facts):",
    ]
    for cid, text in evidence:
        lines.append(f"  [{cid}] {text}")
    if figure_caption:
        lines.append(f"FIGURE ON THIS SLIDE: {figure_caption}")
    lines += [
        "RULES:",
        "  - every bullet must map to one of the claim ids above",
        "  - every number must appear verbatim in the evidence above",
        "  - notes: 120-200 words, open without repeating a bullet, end with a transition",
        'Return JSON only: {"bullets":[{"text":str,"claim_id":str}],'
        ' "notes":{"text":str,"transition":str},"est_sec":int}',
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# editing: who may change what
# --------------------------------------------------------------------------- #

def record_edit(deck: Deck, side: str, slide_index: int, field_name: str,
                before: str, after: str, kind: str) -> dict:
    """Log a human change. `side` is which layer it touches.

    A text edit forks the text layer: the slide's origin becomes "human", and any
    claim the deck makes about this slide being generated and verified no longer
    applies to it. That is why the ablation only ever runs on decks whose edits
    are all layout edits.
    """
    if side not in SIDES:
        raise DeckError(f"side must be one of {SIDES}")
    if kind not in ("instruction", "direct"):
        raise DeckError("kind must be 'instruction' or 'direct'")
    if side == "layout" and field_name in ("headline", "bullet", "notes"):
        raise DeckError("text belongs to the deck layer; this is a layout edit")
    if side == "deck":
        slide = deck.slides[slide_index]
        slide.origin = "human"
    entry = {"side": side, "slide": slide_index, "field": field_name,
             "kind": kind, "before": before, "after": after}
    deck.human_edits.append(entry)
    return entry

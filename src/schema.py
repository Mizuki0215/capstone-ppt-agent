#!/usr/bin/env python3
"""Fixed vocabulary and the selection rule table for a slide plan.

The model appears at exactly two boundaries, and nowhere else:

  1. free-text request  -> Requirement   (`Requirement.from_dict`: enums only, fails closed)
  2. paper section text -> Claim         (`Claim.from_dict`: evidence id required, fails closed)

Everything between them is a rule table a second person can audit row by row:
why this claim survived, which rule kept it, and what a different requirement
would have done instead. A selection we cannot explain cannot go into a paper
about explainable measurement.

Two layers, deliberately separated (see docs/plan_selection.md):

  extraction   per section, sees only that section, produces Claim objects
  composition  one outline step sees every kept claim and re-orders them into
               motivation -> problem -> insight -> evidence -> conclusion

Only extraction may claim to be locally grounded. A results slide has to know
what the problem was, so grounding is a property of the evidence id, not of the
window the text came from.

Two accounting numbers, never mixed:

  retention = claims kept / claims annotated on the paper
  coverage  = claims surviving into the deck / claims kept
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

# --------------------------------------------------------------------------- #
# fixed vocabulary
# --------------------------------------------------------------------------- #


class SectionType(str, Enum):
    MOTIVATION = "motivation"
    PROBLEM = "problem"
    BACKGROUND = "background"
    RELATED = "related_work"
    METHOD = "method"
    SETUP = "setup"
    RESULTS = "results"
    ANALYSIS = "analysis"
    LIMITATIONS = "limitations"
    CONCLUSION = "conclusion"


DURATIONS = (5, 10, 12, 15, 20)          # minutes; anything else is rejected
AUDIENCES = ("expert", "general")

EVIDENCE = re.compile(r"^sec\d+:s\d+$")   # sec3:s12 — the handle validation uses


# Paper headings are not standardised, so they are mapped onto the fixed set
# above. Order matters: the first pattern that matches wins, so the more
# specific headings must come first.
SECTION_PATTERNS: tuple[tuple[SectionType, str], ...] = (
    (SectionType.PROBLEM, r"^(abstract|summary)\b"),
    (SectionType.CONCLUSION, r"^(conclusions?|future work|take ?aways?)\b"),
    (SectionType.LIMITATIONS, r"^(limitations?|threats? to validity)\b"),
    (SectionType.ANALYSIS, r"^(analysis|ablation|discussion|case stud)"),
    (SectionType.RELATED, r"^(related works?|prior work|literature review|related)\b"),
    (SectionType.BACKGROUND, r"^background\b"),
    (SectionType.METHOD, r"^(problem formulation|methods?|approach|proposed|our approach|formulation|architecture|design)\b"),
    (SectionType.SETUP, r"^(experimental setup|setup|implementation|datasets?|data collection|evaluation setup)\b"),
    (SectionType.RESULTS, r"^(experiments?|results?|evaluations?|findings)\b"),
    (SectionType.MOTIVATION, r"^(introduction|motivation)\b"),
)


def section_type(title: str) -> SectionType | None:
    """Map a paper heading onto the fixed set, or None if it does not map.

    None is not a fallback: a section that does not map cannot carry claims,
    because we have no rule for how long it should get.
    """
    t = re.sub(r"^\d{1,2}(?:\.\d+)*\.?\s+", "", (title or "").strip()).lower()
    for st, pat in SECTION_PATTERNS:
        if re.match(pat, t):
            return st
    return None


# --------------------------------------------------------------------------- #
# the two validated boundaries
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Requirement:
    """A talk request, after the model has converted free text into this table.

    Frozen and fully validated on construction: a request the rules cannot
    interpret is an error, not a guess.
    """

    duration_min: int
    audience: str = "expert"
    focus: tuple[str, ...] = ()
    must_include: tuple[SectionType, ...] = ()
    must_exclude: tuple[SectionType, ...] = ()
    requested_min: tuple[int, ...] = ()   # part types the LLM wanted, if any

    def __post_init__(self) -> None:
        if self.duration_min not in DURATIONS:
            raise ValueError(f"duration_min={self.duration_min!r} not in {DURATIONS}")
        if self.audience not in AUDIENCES:
            raise ValueError(f"audience={self.audience!r} not in {AUDIENCES}")
        for name, values in (("must_include", self.must_include),
                             ("must_exclude", self.must_exclude)):
            for v in values:
                if not isinstance(v, SectionType):
                    raise ValueError(f"{name} contains {v!r}, expected a SectionType")
        both = set(self.must_include) & set(self.must_exclude)
        if both:
            names = ", ".join(sorted(s.value for s in both))
            raise ValueError(f"contradictory request: {names} both included and excluded")
        for st in self.must_exclude:
            if st in HARD_ON:
                raise ValueError(f"cannot exclude {st.value}: a deck always keeps it")

    @classmethod
    def from_dict(cls, d: dict) -> "Requirement":
        """Parse the model's table. Unknown keys or values are rejected."""
        allowed = {"duration_min", "audience", "focus", "must_include", "must_exclude"}
        unknown = set(d) - allowed
        if unknown:
            raise ValueError(f"unknown requirement keys: {sorted(unknown)}")
        try:
            dur = int(d["duration_min"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("duration_min is required and must be an integer") from exc
        return cls(
            duration_min=dur,
            audience=str(d.get("audience", "expert")).lower(),
            focus=tuple(d.get("focus", ())),
            must_include=tuple(_as_type(x) for x in d.get("must_include", ())),
            must_exclude=tuple(_as_type(x) for x in d.get("must_exclude", ())),
        )


def _as_type(value) -> SectionType:
    try:
        return SectionType(str(value).lower())
    except ValueError as exc:
        allowed = ", ".join(s.value for s in SectionType)
        raise ValueError(f"unknown section type {value!r}; allowed: {allowed}") from exc


# --- selection tables ------------------------------------------------------ #
# Only two profiles. People do not plan a talk differently for 10 versus 12
# minutes, and a third column would imply a precision the evidence does not
# support. Every cell is auditable, and a different table is a different
# experiment (report both, as with the gate sweeps).
TABLE: dict[int, dict[SectionType, bool]] = {
    12: {
        SectionType.MOTIVATION: True,
        SectionType.PROBLEM: True,
        SectionType.BACKGROUND: True,
        SectionType.RELATED: False,
        SectionType.METHOD: True,
        SectionType.SETUP: False,
        SectionType.RESULTS: True,
        SectionType.ANALYSIS: True,
        SectionType.LIMITATIONS: True,
        SectionType.CONCLUSION: True,
    },
    5: {
        SectionType.MOTIVATION: True,
        SectionType.PROBLEM: True,
        SectionType.BACKGROUND: False,
        SectionType.RELATED: False,
        SectionType.METHOD: True,
        SectionType.SETUP: False,
        SectionType.RESULTS: True,
        SectionType.ANALYSIS: False,
        SectionType.LIMITATIONS: False,
        SectionType.CONCLUSION: True,
    },
}

# A deck that drops its results or its conclusion is not a shorter talk, it is
# a broken one. These can be forced on by a request but never off.
HARD_ON = {SectionType.RESULTS, SectionType.CONCLUSION}

# Importance is 1 (detail) .. 3 (must land). A short talk keeps only 3s.
CUTOFF: dict[int, int] = {5: 3, 12: 2}


def profile_for(duration_min: int) -> dict[SectionType, bool]:
    return TABLE[5] if duration_min <= 5 else TABLE[12]


def cutoff_for(duration_min: int) -> int:
    return CUTOFF[5] if duration_min <= 5 else CUTOFF[12]


@dataclass(frozen=True)
class Claim:
    """One assertion extracted from exactly one section, with an evidence handle."""

    claim_id: str
    section_type: SectionType
    importance: int
    text: str
    evidence: str

    def __post_init__(self) -> None:
        if not self.claim_id:
            raise ValueError("claim_id is required")
        if not isinstance(self.section_type, SectionType):
            raise ValueError(f"claim {self.claim_id}: section_type must be a SectionType")
        if self.importance not in (1, 2, 3):
            raise ValueError(f"claim {self.claim_id}: importance={self.importance!r} not in (1,2,3)")
        if not self.text.strip():
            raise ValueError(f"claim {self.claim_id}: text is empty")
        if not EVIDENCE.match(self.evidence or ""):
            raise ValueError(
                f"claim {self.claim_id}: evidence={self.evidence!r} must look like sec3:s12"
            )

    @classmethod
    def from_dict(cls, d: dict) -> "Claim":
        return cls(
            claim_id=str(d["claim_id"]),
            section_type=_as_type(d["section_type"]),
            importance=int(d["importance"]),
            text=str(d["text"]),
            evidence=str(d["evidence"]),
        )


# --------------------------------------------------------------------------- #
# the decision, with its provenance
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Decision:
    claim_id: str
    section_type: SectionType
    importance: int
    selected: bool
    rule: str          # which rule decided: hard:results, table:12:setup, ...
    why: str


def decide(claims: list[Claim], req: Requirement) -> list[Decision]:
    """Apply the rule table. Pure, total, and deterministic.

    Precedence, highest first — the order is part of the design, not an
    implementation detail:
      1. hard rules      results and conclusion are always kept
      2. must_exclude    an explicit request to drop a part type
      3. must_include    an explicit request to keep a part type (bypasses the cutoff)
      4. profile table   section type x talk length
      5. importance      within a kept part, drop claims below the cutoff
    """
    seen = set()
    for c in claims:
        if c.claim_id in seen:
            raise ValueError(f"duplicate claim_id {c.claim_id}")
        seen.add(c.claim_id)

    table = profile_for(req.duration_min)
    cutoff = cutoff_for(req.duration_min)
    include, exclude = set(req.must_include), set(req.must_exclude)
    out: list[Decision] = []

    for c in claims:
        st = c.section_type
        if st in HARD_ON:
            out.append(Decision(c.claim_id, st, c.importance, True, f"hard:{st.value}",
                                "results and conclusions are never dropped"))
        elif st in exclude:
            out.append(Decision(c.claim_id, st, c.importance, False, "req:exclude",
                                "the request excludes this part type"))
        elif st in include:
            out.append(Decision(c.claim_id, st, c.importance, True, "req:include",
                                "the request asks for this part type"))
        elif not table.get(st, False):
            out.append(Decision(c.claim_id, st, c.importance, False,
                                f"table:{req.duration_min}:{st.value}",
                                f"not kept in a {req.duration_min} min talk"))
        elif c.importance < cutoff:
            out.append(Decision(c.claim_id, st, c.importance, False,
                                f"importance:cut{cutoff}",
                                f"importance {c.importance} < cutoff {cutoff}"))
        else:
            out.append(Decision(c.claim_id, st, c.importance, True,
                                f"table:{req.duration_min}:{st.value}",
                                f"kept in a {req.duration_min} min talk"))
    return out


def accounting(annotated: list[str], kept: list[str], in_deck: list[str]) -> dict:
    """The two numbers, kept apart.

    `annotated` are the claims a human marked as the paper's key claims;
    `kept` are those the rule table selected; `in_deck` are those whose text
    actually reached a slide. Reporting retention and coverage as one number is
    how a short talk gets a flattering score for having dropped half the paper.
    """
    a, k, d = set(annotated), set(kept), set(in_deck)
    if not k <= a:
        raise ValueError(f"kept claims not in the annotated set: {sorted(k - a)}")
    if not d <= k:
        raise ValueError(f"claims in deck were never kept: {sorted(d - k)}")
    return {
        "annotated": len(a),
        "kept": len(k),
        "in_deck": len(d),
        "retention": round(len(k) / len(a), 3) if a else 0.0,
        "coverage": round(len(d) / len(k), 3) if k else 0.0,
    }


# The requirement every experimental arm uses. Changing it would change what
# every system is asked to do, so it is frozen here and pre-registered: the
# adaptive request feature is a demo, never a variable in the comparison.
DEFAULT_REQ = Requirement(duration_min=12, audience="expert")

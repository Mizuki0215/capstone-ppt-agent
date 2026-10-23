"""Tests for the requirement vocabulary and the selection rule table.

These are the parts that must not need a model to check: if a rule cannot be
tested here, it cannot be defended in the report either.
"""
import pytest

from schema import (
    DEFAULT_REQ,
    HARD_ON,
    Claim,
    Requirement,
    SectionType as S,
    accounting,
    decide,
    section_type,
)


def claim(cid, st, imp=3, text="x", ev="sec1:s1"):
    return Claim(claim_id=cid, section_type=st, importance=imp, text=text, evidence=ev)


# --------------------------------------------------------------------------- #
# heading -> fixed section type
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("heading,expected", [
    ("Abstract", S.PROBLEM),
    ("1 Introduction", S.MOTIVATION),
    ("2. Background", S.BACKGROUND),
    ("3 Related Work", S.RELATED),
    ("4 Method", S.METHOD),
    ("4.2 Experimental Setup", S.SETUP),
    ("5 Experiments", S.RESULTS),
    ("6 Results", S.RESULTS),
    ("7 Ablation Study", S.ANALYSIS),
    ("8 Limitations", S.LIMITATIONS),
    ("9 Conclusion", S.CONCLUSION),
    ("Acknowledgements", None),
    ("Appendix A", None),
])
def test_section_type_mapping(heading, expected):
    assert section_type(heading) is expected


def test_section_type_ignores_numbering_prefix():
    assert section_type("3.2.1 Problem Formulation") is S.METHOD
    assert section_type("  5 Results  ") is S.RESULTS


# --------------------------------------------------------------------------- #
# the requirement boundary fails closed
# --------------------------------------------------------------------------- #

def test_duration_must_be_from_the_enum():
    with pytest.raises(ValueError, match="duration_min"):
        Requirement(duration_min=7)


def test_audience_must_be_from_the_enum():
    with pytest.raises(ValueError, match="audience"):
        Requirement(duration_min=12, audience="kids")


def test_unknown_requirement_key_is_rejected():
    with pytest.raises(ValueError, match="unknown requirement keys"):
        Requirement.from_dict({"duration_min": 12, "tone": "funny"})


def test_from_dict_accepts_the_documented_shape():
    req = Requirement.from_dict({
        "duration_min": 5, "audience": "general",
        "must_include": ["analysis"], "must_exclude": ["setup"],
    })
    assert req.duration_min == 5 and req.audience == "general"
    assert req.must_include == (S.ANALYSIS,)
    assert req.must_exclude == (S.SETUP,)


def test_contradictory_request_is_an_error():
    with pytest.raises(ValueError, match="contradictory"):
        Requirement(duration_min=12, must_include=(S.SETUP,), must_exclude=(S.SETUP,))


def test_results_cannot_be_excluded():
    with pytest.raises(ValueError, match="cannot exclude results"):
        Requirement(duration_min=12, must_exclude=(S.RESULTS,))


def test_conclusion_cannot_be_excluded():
    with pytest.raises(ValueError, match="cannot exclude conclusion"):
        Requirement(duration_min=5, must_exclude=(S.CONCLUSION,))


# --------------------------------------------------------------------------- #
# claims fail closed
# --------------------------------------------------------------------------- #

def test_evidence_handle_is_required():
    with pytest.raises(ValueError, match="evidence"):
        claim("c1", S.RESULTS, ev="paragraph 3")


def test_importance_is_bounded():
    with pytest.raises(ValueError, match="importance"):
        claim("c1", S.RESULTS, imp=4)


def test_duplicate_claim_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate claim_id"):
        decide([claim("c1", S.RESULTS), claim("c1", S.METHOD)], DEFAULT_REQ)


# --------------------------------------------------------------------------- #
# the rule table
# --------------------------------------------------------------------------- #

def test_twelve_minute_talk_keeps_the_full_argument():
    d = decide([claim(f"c{i}", st) for i, st in enumerate(S)], DEFAULT_REQ)
    kept = {x.section_type for x in d if x.selected}
    assert kept == {S.MOTIVATION, S.PROBLEM, S.BACKGROUND, S.METHOD,
                    S.RESULTS, S.ANALYSIS, S.LIMITATIONS, S.CONCLUSION}
    dropped = {x.section_type for x in d if not x.selected}
    assert dropped == {S.RELATED, S.SETUP}


def test_five_minute_talk_drops_analysis_and_limitations():
    d = decide([claim(f"c{i}", st) for i, st in enumerate(S)],
               Requirement(duration_min=5, audience="general"))
    dropped = {x.section_type for x in d if not x.selected}
    assert dropped == {S.RELATED, S.SETUP, S.BACKGROUND, S.ANALYSIS, S.LIMITATIONS}
    assert S.RESULTS not in dropped and S.CONCLUSION not in dropped


def test_hard_rules_beat_the_table():
    # a 5-minute talk would drop ANALYSIS, but results are never dropped
    d = decide([claim("c1", S.RESULTS, imp=1)], Requirement(duration_min=5))
    assert d[0].selected and d[0].rule == "hard:results"


def test_must_include_beats_the_table_and_the_cutoff():
    req = Requirement(duration_min=5, must_include=(S.ANALYSIS,))
    d = decide([claim("c1", S.ANALYSIS, imp=1)], req)
    assert d[0].selected and d[0].rule == "req:include"


def test_must_exclude_is_recorded_with_its_own_rule():
    req = Requirement(duration_min=12, must_exclude=(S.SETUP,))
    d = decide([claim("c1", S.SETUP)], req)
    assert not d[0].selected and d[0].rule == "req:exclude"


def test_importance_cutoff_drops_detail_in_a_short_talk():
    short = decide([claim("low", S.METHOD, imp=2), claim("high", S.METHOD, imp=3)],
                   Requirement(duration_min=5))
    assert {x.claim_id: x.selected for x in short} == {"low": False, "high": True}
    assert short[0].rule == "importance:cut3"


def test_same_claim_survives_at_twelve_minutes():
    d = decide([claim("low", S.METHOD, imp=2)], DEFAULT_REQ)
    assert d[0].selected


def test_decisions_are_deterministic_and_order_preserving():
    claims = [claim("b", S.RESULTS), claim("a", S.METHOD), claim("c", S.RELATED)]
    first = decide(claims, DEFAULT_REQ)
    second = decide(claims, DEFAULT_REQ)
    assert first == second
    assert [x.claim_id for x in first] == ["b", "a", "c"]


def test_every_decision_carries_a_traceable_rule():
    d = decide([claim(f"c{i}", st, imp=1) for i, st in enumerate(S)], DEFAULT_REQ)
    for x in d:
        assert x.rule.split(":")[0] in {"hard", "req", "table", "importance"}
        assert x.why


# --------------------------------------------------------------------------- #
# accounting: retention and coverage are different questions
# --------------------------------------------------------------------------- #

def test_short_talk_has_low_retention_but_full_coverage():
    # 8 claims annotated, a 5-minute talk keeps 3, all 3 reach the deck
    annotated = [f"c{i}" for i in range(8)]
    kept = annotated[:3]
    got = accounting(annotated, kept, kept)
    assert got["retention"] == pytest.approx(0.375)
    assert got["coverage"] == pytest.approx(1.0)


def test_coverage_cannot_exceed_what_was_kept():
    with pytest.raises(ValueError, match="never kept"):
        accounting(["a", "b"], ["a"], ["b"])


def test_kept_claims_must_come_from_the_annotated_set():
    with pytest.raises(ValueError, match="annotated set"):
        accounting(["a"], ["b"], ["b"])


# --------------------------------------------------------------------------- #
# the frozen experimental requirement
# --------------------------------------------------------------------------- #

def test_default_requirement_is_the_frozen_twelve_minute_expert_talk():
    assert DEFAULT_REQ.duration_min == 12
    assert DEFAULT_REQ.audience == "expert"
    assert DEFAULT_REQ.must_include == () and DEFAULT_REQ.must_exclude == ()


def test_hard_on_is_exactly_results_and_conclusion():
    assert HARD_ON == {S.RESULTS, S.CONCLUSION}

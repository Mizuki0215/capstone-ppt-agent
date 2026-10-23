"""Tests for the deck contract and the prompt interface."""
import pytest

from deck import (Bullet, Claim, Decision, Deck, DeckError, Figure, Notes, PROMPT,
                  Requirement, SectionType, Slide, build_prompt, record_edit)


def req(minutes=12):
    return Requirement(duration_min=minutes, audience="expert")


def claim(cid, st=SectionType.RESULTS, imp=3, ev="sec1:s1"):
    return Claim(claim_id=cid, section_type=st, importance=imp, text=f"text of {cid}",
                 evidence=ev)


def deck(**kw):
    c = claim("c1")
    base = dict(
        title="T",
        requirement=req(),
        claims=[(c, Decision("c1", SectionType.RESULTS, 3, True, "hard:results", "kept"))],
        figures=[Figure("f1", 2, "Figure 1: the pipeline", "build/f.png", [0, 0, 10, 10], 100)],
        slides=[
            Slide(1, "result", SectionType.RESULTS, "Headline",
                  ["c1"], [Bullet("one", "c1")], Notes("n", 240, "next"), "f1", 240),
            Slide(2, "result", SectionType.RESULTS, "Headline 2",
                  ["c1"], [Bullet("two", "c1")], Notes("n", 240), None, 240),
            Slide(3, "conclusion", SectionType.CONCLUSION, "Takeaway",
                  ["c1"], [Bullet("three", "c1")], Notes("n", 240), None, 240),
        ],
    )
    base.update(kw)
    return Deck(**base)


# --------------------------------------------------------------------------- #
# invariants
# --------------------------------------------------------------------------- #

def test_a_well_formed_deck_passes():
    assert deck().validate() == []


def test_bullets_must_name_a_selected_claim():
    d = deck()
    d.slides[0].bullets = [Bullet("x", "c9")]
    assert any("unselected claim c9" in e for e in d.validate())


def test_bullet_claim_must_be_listed_on_its_slide():
    d = deck()
    d.slides[0].claim_ids = []
    assert any("not listed on the slide" in e for e in d.validate())


def test_figure_reference_must_resolve():
    d = deck()
    d.slides[0].figure_id = "f9"
    assert any("f9 does not exist" in e for e in d.validate())


def test_budget_must_match_the_talk_length():
    d = deck()
    d.slides[0].budget_sec = 60
    assert any("does not match" in e for e in d.validate())


def test_unknown_role_and_origin_are_rejected():
    d = deck()
    d.slides[0].role = "appendix"
    d.slides[1].origin = "magic"
    errs = d.validate()
    assert any("unknown role" in e for e in errs)
    assert any("unknown origin" in e for e in errs)


def test_check_raises_with_every_error_together():
    d = deck()
    d.slides[0].figure_id = "f9"
    d.slides[1].role = "nope"
    with pytest.raises(DeckError) as exc:
        d.check()
    assert "f9" in str(exc.value) and "nope" in str(exc.value)


def test_round_trip_through_json(tmp_path):
    d = deck()
    d.check()
    p = tmp_path / "deck.json"
    d.save(p)
    import json
    raw = json.loads(p.read_text())
    assert raw["schema_version"] == "1.0"
    assert raw["slides"][0]["bullets"][0]["claim_id"] == "c1"
    assert raw["requirement"]["duration_min"] == 12
    assert raw["claims"][0]["rule"] == "hard:results"


# --------------------------------------------------------------------------- #
# prompt interface
# --------------------------------------------------------------------------- #

def test_every_section_type_has_a_prompt():
    assert set(PROMPT) == set(SectionType)


def test_prompt_contains_the_requirement_and_only_the_given_evidence():
    s = deck().slides[0]
    p = build_prompt(s, req(5), [("c1", "the claim text")], "Figure 1: the pipeline")
    assert "5 minutes" in p and "results slide" in p
    assert "[c1] the claim text" in p
    assert "every number must appear verbatim" in p
    assert "Figure 1: the pipeline" in p


def test_results_prompt_forbids_new_numbers():
    s = deck().slides[0]
    p = build_prompt(s, req(), [("c1", "x")])
    assert "no new numbers" in p.lower()


# --------------------------------------------------------------------------- #
# editing model
# --------------------------------------------------------------------------- #

def test_layout_edit_does_not_touch_the_text_layer():
    d = deck()
    record_edit(d, "layout", 0, "box", "0,0", "1,1", "direct")
    assert d.slides[0].origin == "llm"
    assert d.human_edits[-1]["side"] == "layout"


def test_text_edit_forks_the_slide_to_human():
    d = deck()
    record_edit(d, "deck", 0, "bullet", "old", "new", "instruction")
    assert d.slides[0].origin == "human"


def test_layout_layer_cannot_carry_text():
    with pytest.raises(DeckError, match="layout edit"):
        record_edit(deck(), "layout", 0, "headline", "a", "b", "direct")


def test_unknown_layer_and_kind_are_rejected():
    with pytest.raises(DeckError, match="side"):
        record_edit(deck(), "pixels", 0, "x", "a", "b", "direct")
    with pytest.raises(DeckError, match="kind"):
        record_edit(deck(), "deck", 0, "bullet", "a", "b", "telepathy")

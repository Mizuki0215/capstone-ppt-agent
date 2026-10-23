"""Tests for figure extraction.

The geometry helpers are pure, so they are tested directly. The end-to-end clip
is tested against a real paper when the corpus is present (the PDFs are
gitignored, so the test skips on a clean clone).
"""
from pathlib import Path

import pymupdf
import pytest

import figures

PDF = Path("research/pdfs/PPTAgent_2501.03936.pdf")


def rect(x0, y0, x1, y1):
    return pymupdf.Rect(x0, y0, x1, y1)


def test_same_column_requires_half_overlap():
    caption = rect(300, 500, 560, 600)
    assert figures.same_column(caption, rect(300, 100, 560, 300))
    assert not figures.same_column(caption, rect(40, 100, 290, 300))


def test_a_paragraph_is_not_a_label():
    assert figures.is_paragraph(rect(0, 0, 400, 40),
                                "We evaluate on three benchmarks and report the mean score")
    assert not figures.is_paragraph(rect(0, 0, 200, 14), "Stage I: Presentation Analysis")
    assert not figures.is_paragraph(rect(0, 0, 400, 40), "Table 1")


def test_band_stops_at_the_paragraph_not_at_a_label_inside_the_figure():
    # body text, then a figure whose own labels sit between it and the caption
    blocks = [
        (rect(300, 90, 560, 300), "We compare against two baselines on three datasets and report scores"),
        (rect(300, 380, 470, 396), "Stage I: Presentation Analysis"),
        (rect(300, 400, 560, 412), "1. Slide Clustering"),
    ]
    cap = rect(300, 500, 560, 600)
    band = figures.figure_band(rect(0, 0, 612, 792), cap, blocks)
    assert band.y0 == pytest.approx(300)
    assert band.y1 < cap.y0


def test_band_ignores_a_paragraph_in_the_other_column():
    blocks = [(rect(40, 90, 290, 300),
               "This paragraph lives in the left column and must not bound a right-column figure")]
    cap = rect(300, 500, 560, 600)
    band = figures.figure_band(rect(0, 0, 612, 792), cap, blocks)
    assert band.y0 == pytest.approx(36)      # page margin, not the other column


def test_ink_bbox_ignores_an_empty_band():
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "some ink")
    assert figures.ink_bbox(page, rect(72, 300, 300, 360)) is None   # nothing there


def test_ink_bbox_finds_the_ink():
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((100, 200), "TARGET", fontsize=20)
    box = figures.ink_bbox(page, rect(72, 150, 400, 260))
    assert box is not None
    # the glyph starts a little right of the insertion point (side bearing),
    # so the assertion is a tolerance, not an equality
    assert 95 <= box.x0 <= 110 and 95 <= box.x1 <= 195
    assert 175 <= box.y0 <= 200 and 200 <= box.y1 <= 215


@pytest.mark.skipif(not PDF.exists(), reason="corpus PDF not downloaded")
def test_end_to_end_on_a_real_paper(tmp_path):
    recs = figures.extract(str(PDF), tmp_path, "probe")
    assert len(recs) >= 8, f"only {len(recs)} figures clipped"
    for r in recs:
        p = Path(r["image"].replace(str(tmp_path), str(tmp_path)))
        assert p.exists() and p.stat().st_size > 5000
        assert r["caption"].lower().startswith(("figure", "table"))
        assert r["area"] > figures.MIN_W * figures.MIN_H
    # the workflow figure on page 2 is wide and short, and must not be a logo
    wide = [r for r in recs if r["page"] == "2"]
    assert wide and wide[0]["area"] > 50000

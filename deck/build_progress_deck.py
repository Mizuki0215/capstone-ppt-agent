#!/usr/bin/env python3
"""Build the English progress deck for the supervisor meeting.

    <python with python-pptx> deck/build_progress_deck.py

Content is the project as it stands on 2026-10-24: the literature argument, the
parts of the system, and the measured results. Every number on the result slides
comes from build/detect_v1.json and a fresh detector run, not from memory.
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deck" / "progress_deck.pptx"
IMG = ROOT / "deck" / "progress_img"

INK = RGBColor(0x10, 0x23, 0x3A)
INK2 = RGBColor(0x1E, 0x36, 0x52)
GREY = RGBColor(0x5A, 0x6B, 0x7C)
LGREY = RGBColor(0x8A, 0x99, 0xA8)
GOLD = RGBColor(0xC0, 0x8A, 0x2E)
PANEL = RGBColor(0xF4, 0xF6, 0xF8)
PANEL2 = RGBColor(0xEC, 0xF1, 0xF5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2F, 0x7D, 0x5D)
AMBER = RGBColor(0xB0, 0x7A, 0x1E)
RED = RGBColor(0xA8, 0x35, 0x42)
TEAL = RGBColor(0x2E, 0x6F, 0x95)

FONT = "Helvetica Neue"
W, H = 13.333, 7.5


# --------------------------------------------------------------------------- #
def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def tb(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    return tf


def write(tf, text, size, colour=INK, bold=False, first=False, space=0, line=1.15,
          align=PP_ALIGN.LEFT, italic=False, font=FONT):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space)
    p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = colour
    return p


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.9, shape=MSO_SHAPE.RECTANGLE,
         radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    s.shadow.inherit = False
    style = s._element.find(qn("p:style"))   # theme effects put a shadow back
    if style is not None:
        s._element.remove(style)
    s.text_frame.word_wrap = True
    return s


def page(prs, kicker, title, number=None):
    s = blank(prs)
    rect(s, 0, 0, 0.26, H, fill=INK)
    rect(s, 0.26, 0, 0.05, H, fill=GOLD)
    tf = tb(s, 0.95, 0.42, 11.6, 0.30)
    write(tf, kicker.upper(), 9.5, GOLD, True, first=True)
    tf = tb(s, 0.95, 0.70, 11.9, 0.75)
    write(tf, title, 25, INK, True, first=True, line=1.05)
    rect(s, 0.95, 1.52, 11.9, 0.014, fill=RGBColor(0xDD, 0xE2, 0xE8))
    if number:
        tf = tb(s, 12.2, 6.95, 0.7, 0.3)
        write(tf, f"{number:02d}", 9, LGREY, first=True, align=PP_ALIGN.RIGHT)
    return s


def bullets(slide, x, y, w, items, size=15, gap=8, colour=INK, bullet_col=GOLD):
    tf = tb(slide, x, y, w, 4.2)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else gap)
        p.line_spacing = 1.22
        r = p.add_run()
        r.text = "-  "
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = bullet_col
        if isinstance(item, tuple):
            head, rest = item
            r = p.add_run(); r.text = head
            r.font.name = FONT; r.font.size = Pt(size); r.font.bold = True
            r.font.color.rgb = colour
            r = p.add_run(); r.text = rest
            r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = colour
        else:
            r = p.add_run(); r.text = item
            r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = colour
    return tf


def table(slide, headers, rows, x, y, w, widths, size=10, head=10, row_h=0.32,
          head_h=0.34):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(x), Inches(y),
                                   Inches(w), Inches(row_h * (len(rows) + 1)))
    t = shape.table
    for i, cw in enumerate(widths):
        t.columns[i].width = Inches(cw)
    t.rows[0].height = Inches(head_h)
    for r in range(1, len(rows) + 1):
        t.rows[r].height = Inches(row_h)
    for i, h in enumerate(headers):
        cell = t.cell(0, i)
        cell.fill.solid(); cell.fill.fore_color.rgb = PANEL2
        cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        tf = cell.text_frame; tf.word_wrap = True
        write(tf, h, head, INK, True, first=True)
    for r, row in enumerate(rows, start=1):
        for i, val in enumerate(row):
            cell = t.cell(r, i)
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
            cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            tf = cell.text_frame; tf.word_wrap = True
            colour = INK if i == 0 else INK2
            write(tf, str(val), size, colour, i == 0, first=True, line=1.1)
    return t


def pill(slide, x, y, w, text, colour, size=9):
    s = rect(slide, x, y, w, 0.30, fill=WHITE, line=colour, lw=1.2,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = s.text_frame
    tf.margin_top = 0; tf.margin_bottom = 0
    write(tf, text, size, colour, True, first=True, align=PP_ALIGN.CENTER)
    return s


# --------------------------------------------------------------------------- #
def slide_title(prs):
    s = blank(prs)
    rect(s, 0, 0, 0.34, H, fill=INK)
    rect(s, 0.34, 0, 0.07, H, fill=GOLD)
    tf = tb(s, 1.1, 1.35, 10.8, 0.4)
    write(tf, "DSAI4901  ·  CAPSTONE PROGRESS BRIEFING", 11, GOLD, True, first=True)
    tf = tb(s, 1.1, 1.95, 10.9, 2.4)
    write(tf, "From generating\nto verifying", 46, INK, True, first=True, line=1.02)
    tf = tb(s, 1.1, 4.15, 10.4, 1.0)
    write(tf, "A reference-free measure of deck usability, used as a control signal "
              "in paper-to-slide generation", 14.5, GREY, first=True, line=1.3)
    rect(s, 1.1, 5.35, 3.4, 0.02, fill=GOLD)
    tf = tb(s, 1.1, 5.55, 10.4, 1.0)
    write(tf, "CHAN Yee Tung", 12.5, INK, True, first=True)
    write(tf, "Supervisor: Dr. Jibin Wu   ·   29 October 2026", 11, GREY, space=4)
    return s


def slide_lit(prs):
    s = page(prs, "where the field stands", "Two families, one missing instrument", 2)
    rows = [
        ["PPTAgent, SlideGen,\nSlideLab, ArcDeck", "Strong generators;\nnarrative planning",
         "Whether any given deck is usable;\nlocal, mechanical failures"],
        ["ReDeck, PPTPilot,\nSLIDEFORGE", "Repair loops that read\nrendered feedback",
         "Which class of defect responded\nto repair, and by how much"],
        ["SlideAudit, DECKBench,\nPresentBench", "Flaw taxonomy; deck-level\nscoring against a reference",
         "Arrives after generation; needs a\ntarget deck or labels"],
    ]
    table(s, ["Work", "What it provides", "What it leaves open"], rows, 0.95, 1.82,
          11.9, [3.5, 3.6, 4.8], size=10.5, head=10.5, row_h=0.58, head_h=0.36)
    tf = tb(s, 0.95, 4.30, 11.6, 1.9)
    write(tf, "Read together, the field is good at producing decks and good at scoring them "
              "afterwards, but it has not closed the loop in between.", 15, INK, first=True,
          line=1.35)
    write(tf, "The instrument arrives too late to steer generation, and it is not "
              "decomposable when it does arrive.", 12.5, GREY, space=8, line=1.3)
    rect(s, 0.95, 5.55, 11.9, 1.05, fill=PANEL2)
    rect(s, 0.95, 5.55, 0.07, 1.05, fill=GOLD)
    tf = tb(s, 1.28, 5.72, 11.3, 0.8)
    write(tf, "The gap: no instrument runs inside the loop, and none of them decomposes the "
              "score. A deck-level number cannot tell you which defect to fix.", 12.5, INK,
          first=True, line=1.3)
    return s


def slide_why(prs):
    s = page(prs, "why this direction", "Three things the literature does not do", 3)
    cols = [
        ("Attribution is missing", "ReDeck and PPTPilot both repair, but a deck-level gain "
                                   "of ten points does not say which defect class responded.",
         AMBER),
        ("Measurement is post-hoc", "SlideAudit and DECKBench score finished decks. A score "
                                    "that arrives after generation cannot steer it.", TEAL),
        ("Instruments need references", "A target deck, or human labels on images. Neither can "
                                        "run on an arbitrary .pptx at generation time.", RED),
    ]
    x = 0.95
    for title, body, colour in cols:
        rect(s, x, 1.88, 3.72, 2.15, fill=PANEL)
        rect(s, x, 1.90, 3.72, 0.06, fill=colour)
        tf = tb(s, x + 0.28, 2.08, 3.2, 0.6)
        write(tf, title, 13.5, INK, True, first=True, line=1.15)
        tf = tb(s, x + 0.28, 2.68, 3.2, 1.3)
        write(tf, body, 10.5, INK2, first=True, line=1.3)
        x += 3.96
    tf = tb(s, 0.95, 4.45, 11.6, 0.5)
    write(tf, "So the contribution is not another generator, and not a new taxonomy.", 15, INK,
          True, first=True)
    bullets(s, 0.95, 5.10, 11.6, [
        ("It is a measurement layer ", "that is reference-free, computed on the object model, "
                                       "and cheap enough to run inside the loop."),
        ("And a study of what that measurement is worth", " - per violation class, against cost."),
    ], size=12.5, gap=6)
    return s


def slide_gap(prs):
    s = page(prs, "the question", "One gap, two research questions", 4)
    rect(s, 0.95, 1.85, 11.9, 1.55, fill=PANEL2)
    rect(s, 0.95, 1.85, 0.07, 1.55, fill=GOLD)
    tf = tb(s, 1.28, 2.02, 11.3, 1.3)
    write(tf, "\u201cSlide quality can now be measured after the fact. What these instruments "
              "cannot answer is whether measurement can drive generation.\u201d",
          13.5, INK, first=True, line=1.35, italic=True)
    qs = [("RQ1", "Can a small set of mechanical gates replace a reference deck or human "
                  "labels, and still rank decks in the order a person would?"),
          ("RQ2", "What does using that signal inside the loop actually add - per violation "
                  "class, and at what cost?")]
    y = 3.72
    for tag, q in qs:
        pill(s, 0.95, y + 0.04, 0.85, tag, GOLD, size=10)
        tf = tb(s, 1.98, y, 10.8, 0.9)
        write(tf, q, 13, INK2, first=True, line=1.35)
        y += 1.05
    tf = tb(s, 0.95, 5.95, 11.6, 0.9)
    write(tf, "Both are answered by the same artefact: a deck, a score, and a repair log.",
          11.5, GREY, first=True, italic=True)
    return s


def slide_workflow(prs):
    s = page(prs, "the system", "Seven parts, four of which call a model", 5)
    parts = [
        ("parse", "PDF -> sections,\nfigures, captions", "det"),
        ("claims", "assertions with\nan evidence id", "AI"),
        ("requirement", "talk length and\naudience -> table", "AI"),
        ("select", "keep or drop,\nper claim", "rule"),
        ("outline", "re-order into\nan argument", "AI"),
        ("bullets+notes", "compress, then\nwrite the talk", "AI"),
        ("render", "native, editable\n.pptx", "det"),
    ]
    x, y, w, h, gap = 0.95, 1.92, 1.43, 1.12, 0.155
    for i, (name, sub, tag) in enumerate(parts):
        fill = PANEL if tag == "AI" else PANEL2
        rect(s, x, y, w, h, fill=fill, line=RGBColor(0xD3, 0xDB, 0xE3))
        tf = tb(s, x + 0.08, y + 0.12, w - 0.16, 0.3)
        write(tf, name, 10.5, INK, True, first=True, align=PP_ALIGN.CENTER)
        tf = tb(s, x + 0.08, y + 0.44, w - 0.16, 0.55)
        write(tf, sub, 7.8, INK2, first=True, align=PP_ALIGN.CENTER, line=1.15)
        if tag == "AI":
            tf = tb(s, x + w - 0.40, y + 0.10, 0.32, 0.2)
            write(tf, "AI", 6.5, TEAL, True, first=True, align=PP_ALIGN.RIGHT)
        if i < len(parts) - 1:
            arrow = rect(s, x + w + 0.025, y + h / 2 - 0.075, gap - 0.05, 0.15,
                         fill=LGREY, shape=MSO_SHAPE.RIGHT_ARROW)
        x += w + gap

    # measurement row
    gates = ["G1 containment", "G2 overlap", "G3 font size", "G4 contrast",
             "G5 text fit", "G6 density"]
    gx, gy, gw, gh, gg = 0.95, 3.92, 1.40, 0.70, 0.12
    for i, g in enumerate(gates):
        rect(s, gx, gy, gw, gh, fill=WHITE, line=RGBColor(0xC3, 0xCE, 0xD8))
        tf = tb(s, gx + 0.05, gy + 0.24, gw - 0.1, 0.3)
        write(tf, g, 9, INK, True, first=True, align=PP_ALIGN.CENTER)
        gx += gw + gg
    rect(s, 10.12, gy, 1.00, gh, fill=PANEL2, line=GOLD)
    tf = tb(s, 10.17, gy + 0.23, 0.90, 0.3)
    write(tf, "SRR", 11, INK, True, first=True, align=PP_ALIGN.CENTER)
    rect(s, 11.28, gy, 1.05, gh, fill=PANEL2, line=GOLD)
    tf = tb(s, 11.33, gy + 0.23, 0.95, 0.3)
    write(tf, "ready?", 9.5, INK, True, first=True, align=PP_ALIGN.CENTER)

    tf = tb(s, 0.95, 1.62, 11.6, 0.3)
    write(tf, "A  generation - text layer, frozen once written", 9.5, GREY, True, first=True)
    tf = tb(s, 0.95, 3.52, 11.6, 0.3)
    write(tf, "B  measurement - six gates on the .pptx object model, no rendering", 9.5, GREY,
          True, first=True)
    # the contribution, drawn as the third band
    cx, cy, cw, ch = 0.95, 4.95, 3.55, 0.78
    for label, sub, colour in [("1  measure", "worst violation first", GREY),
                               ("2  repair", "cheapest reversible action", GREY),
                               ("3  re-measure", "gain per second and per dollar", GREY)]:
        rect(s, cx, cy, cw, ch, fill=WHITE, line=colour, lw=1.0)
        tf = tb(s, cx + 0.15, cy + 0.14, cw - 0.3, 0.55)
        write(tf, label, 10.5, INK, True, first=True)
        write(tf, sub, 8, INK2, space=2)
        cx += cw + 0.35
    tf = tb(s, 0.95, 5.88, 11.9, 0.95)
    write(tf, "Only the text layer is allowed to change the words. Repair may move, resize "
              "or recolour; it may never add content or change a number. That is what keeps "
              "\u201cthe loop improved the deck\u201d from being confounded with \u201cthe loop "
              "rewrote the deck\u201d.", 11, INK2, first=True, line=1.35)
    return s


def slide_parse(prs):
    s = page(prs, "part 1  ·  reading the paper", "Captions are re-rendered, not extracted", 6)
    bullets(s, 0.95, 1.85, 6.3, [
        ("Headings ", "are found by font size and weight, not by a fixed list."),
        ("Figures ", "are vector art in this literature: pulling embedded images returns "
                     "32x32 icons. So each caption's region is clipped and rasterised at 200 dpi."),
        ("The band stops at the nearest paragraph", ", not at any text block - a figure "
                                                       "carries its own labels, and stopping at those cut the figure in half."),
    ], size=12, gap=10)
    img = IMG.parent / "figures" / "PPTAgent_2501.03936" / "p02_01_figure.png"
    if not img.exists():
        img = ROOT / "build" / "figures" / "PPTAgent_2501.03936" / "p02_01_figure.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(7.55), Inches(1.95), width=Inches(4.85))
        tf = tb(s, 7.55, 4.35, 4.85, 0.5)
        write(tf, "Figure 2 of PPTAgent, clipped from the PDF", 8.5, GREY, first=True,
              italic=True)
    tf = tb(s, 0.95, 5.62, 11.9, 1.1)
    write(tf, "12 of 32 captions in this paper produced a usable crop. The failures are "
              "tables whose caption sits above the table, and figures that span both columns. "
              "Both are fixable; the rule that produced the 12 is already the one the "
              "evaluation will use.", 10.5, GREY, first=True, line=1.35)
    return s


def slide_select(prs):
    s = page(prs, "part 2  ·  deciding what to say", "Selection is a table, not a judgement", 7)
    rows = [
        ["5 min, general", "results, conclusion", "method (core only)", "analysis, limitations"],
        ["12 min, expert", "results, conclusion, method,\nmotivation, background, analysis",
         "related work, setup", "-"],
    ]
    table(s, ["request", "always kept", "kept if room", "dropped"], rows, 0.95, 1.85,
          11.9, [2.4, 4.3, 2.9, 2.3], size=10, head=10, row_h=0.55)
    tf = tb(s, 0.95, 3.55, 11.9, 0.4)
    write(tf, "Every kept or dropped claim carries the id of the rule that decided it:", 11.5,
          INK, True, first=True)
    rows2 = [
        ["c3", "results", "3", "kept", "hard:results", "results are never dropped"],
        ["c7", "setup", "2", "dropped", "table:12:setup", "not kept in a 12-minute talk"],
        ["c9", "analysis", "1", "dropped", "importance:cut2", "importance 1 < cutoff 2"],
    ]
    table(s, ["claim", "section", "imp.", "decision", "rule id", "why"], rows2, 0.95, 4.05,
          11.9, [1.0, 1.5, 0.8, 1.3, 2.5, 4.8], size=9.5, head=9.5, row_h=0.32)
    tf = tb(s, 0.95, 5.95, 11.9, 0.9)
    write(tf, "The model appears at two boundaries only: it converts a free-text request into "
              "that table, and it extracts claims. The keep/drop decision in between is a "
              "lookup, so a second person can re-run it.", 10.5, GREY, first=True, line=1.35)
    return s


def slide_measure(prs):
    s = page(prs, "part 3  ·  measuring", "Four of six gates exist; two are next", 8)
    rows = [
        ["G1 containment", "every shape inside the slide", "0 pt", "built"],
        ["G2 overlap", "text intersection over the smaller box", "> 5 %", "built"],
        ["G3 font size", "body and title, by slide role", "role min", "built (global)"],
        ["G6 density", "characters and bullets, by role", "role max", "built (global)"],
        ["G4 contrast", "WCAG 2.2 AA, fill against background", "4.5 : 1", "next"],
        ["G5 text fit", "rendered height over box height", "<= 0.95", "next"],
    ]
    t = table(s, ["gate", "rule", "threshold", "state"], rows, 0.95, 1.85, 7.6,
              [1.9, 3.3, 1.2, 1.2], size=10, head=10, row_h=0.42)
    for r in range(1, len(rows) + 1):
        cell = t.cell(r, 3)
        state = rows[r - 1][3]
        write(cell.text_frame, state, 10, GREEN if state == "built" else
              (AMBER if "global" in state else RED), True, first=True)

    rect(s, 8.85, 1.85, 3.95, 1.55, fill=PANEL)
    tf = tb(s, 9.1, 2.02, 3.5, 1.2)
    write(tf, "SRR", 16, INK, True, first=True)
    write(tf, "Equal-weight pass rate over decidable checks. No gate weight is fitted; "
              "unknown checks leave the average but block deck-ready.", 10, INK2, space=6,
          line=1.3)
    rect(s, 8.85, 3.60, 3.95, 1.55, fill=PANEL)
    tf = tb(s, 9.1, 3.77, 3.5, 1.2)
    write(tf, "Why no weights", 13, INK, True, first=True)
    write(tf, "A weight would be a number with no evidence behind it - the same objection "
              "the report makes to the 24-point rule.", 10, INK2, space=6, line=1.3)
    tf = tb(s, 0.95, 5.35, 11.9, 1.2)
    write(tf, "G4 and G5 are the two that need real resolution: colour has to be resolved "
              "through the theme and z-order, and text height has to be estimated from font "
              "metrics. Both are scheduled before the loop is built, because a metric that "
              "cannot be trusted cannot be the signal.", 10.5, GREY, first=True, line=1.35)
    return s


def slide_results(prs):
    s = page(prs, "results so far", "Every generated slide fails at least one gate", 9)
    img = IMG / "slide02.png"
    if img.exists():
        s.shapes.add_picture(str(img), Inches(0.95), Inches(1.80), width=Inches(6.85))
        tf = tb(s, 0.95, 5.75, 6.85, 0.5)
        write(tf, "Slide 2 of the generated deck: figure placed, caption under it", 8.5, GREY,
              first=True, italic=True)
    rows = [
        ["slides", "9", "9"],
        ["clean slides", "0", "0"],
        ["SRR (slide-level)", "0.00", "0.00"],
        ["violations", "33", "32"],
        ["slides failing G3", "9 / 9", "9 / 9"],
        ["slides failing G6", "8 / 9", "8 / 9"],
    ]
    table(s, ["", "PPTAgent", "DOC2PPT"], rows, 8.15, 1.82, 4.55,
          [2.05, 1.25, 1.25], size=10, head=9.5, row_h=0.33)
    tf = tb(s, 8.15, 4.62, 4.6, 1.6)
    write(tf, "This is the expected result, not a defect: the baseline generator ignores "
              "every gate. What matters is that the number is reproducible and the "
              "violations are named.", 10, INK2, first=True, line=1.35)
    return s


def slide_status(prs):
    s = page(prs, "status", "What is built, what is next", 10)
    groups = [
        ("Built and tested", GREEN, ["parse: sections, figures, captions",
                                     "figure clipping, 12/32 on the sample",
                                     "render: native .pptx with speaker notes",
                                     "G1, G2, G3, G6 + SRR",
                                     "selection rule table, 55 test functions"]),
        ("Partially built", AMBER, ["G3 / G6 still use one global threshold",
                                    "figure captions need a word-boundary trim",
                                    "claims are still extracted by heuristic"]),
        ("Not started", GREY, ["G4 contrast, G5 text fit",
                               "repair actions and the loop",
                               "110-slide test set and its labels",
                               "human decks, baselines, the 2x2 experiment"]),
    ]
    x = 0.95
    for title, colour, items in groups:
        rect(s, x, 1.85, 3.85, 4.05, fill=PANEL)
        rect(s, x, 1.85, 3.85, 0.055, fill=colour)
        tf = tb(s, x + 0.25, 2.05, 3.4, 0.35)
        write(tf, title, 12.5, INK, True, first=True)
        tf = tb(s, x + 0.25, 2.55, 3.45, 3.1)
        for i, item in enumerate(items):
            write(tf, "-  " + item, 9.5, INK2, first=(i == 0), space=0 if i == 0 else 7,
                  line=1.25)
        x += 4.03
    tf = tb(s, 0.95, 6.15, 11.9, 0.6)
    write(tf, "76 test cases pass. The deck above was produced by this pipeline end to end.",
          10.5, GREY, first=True, italic=True)
    return s


def slide_plan(prs):
    s = page(prs, "plan", "The experiment, and the calendar", 11)
    # 2x2
    tf = tb(s, 0.95, 1.80, 5.6, 0.35)
    write(tf, "The design: a 2 x 2 factor", 12.5, INK, True, first=True)
    headers = ["", "no inspection", "inspection on"]
    rows = [["base model", "A1", "A2"], ["fine-tuned", "A1'", "A2'"]]
    table(s, headers, rows, 0.95, 2.20, 5.4, [1.9, 1.75, 1.75], size=11, head=9.5, row_h=0.45)
    tf = tb(s, 0.95, 3.45, 5.5, 1.6)
    write(tf, "A2 - A1 isolates what inspection adds. The fine-tuned row tests whether that "
              "gain survives a better generator.", 10.5, INK2, first=True, line=1.35)
    write(tf, "The fine-tuned arm is conditional: it runs only if the main result is in and "
              "four weeks of buffer remain.", 10, GREY, space=6, line=1.3, italic=True)

    rows2 = [
        ["W1-2", "scope and literature", "proposal, 5 Nov"],
        ["W3-7", "rulebook, six gates, calibration", "validity check"],
        ["W8-11", "repair actions, 110-slide test set", "interim report, 7 Jan"],
        ["W12-18", "loop, ablation, 20-person study", "preference correlation"],
        ["W19-23", "report, demo, presentation", "final, 8 Apr"],
    ]
    table(s, ["weeks", "work", "milestone"], rows2, 6.85, 2.20, 6.0,
          [1.15, 3.0, 1.85], size=9.5, head=9.5, row_h=0.40)
    tf = tb(s, 6.85, 5.05, 6.0, 1.3)
    write(tf, "Two validity checks run before the study: decks must rank human > PPTAgent > "
              "naive, and SRR must track preference. The correlation is pre-registered and "
              "reported whatever it shows.", 10, GREY, first=True, line=1.35)
    return s


def slide_asks(prs):
    s = page(prs, "what I need from you", "Three decisions and one question", 12)
    items = [
        ("1", "Human decks", "Where can I get decks an author actually presented? "
                             "They are the upper bound in the validity check, and I have none."),
        ("2", "Scope", "Single-column English papers, 10-12 slides, 8 held-out papers - "
                       "is that narrow enough to finish, or too narrow to generalise?"),
        ("3", "Gate set", "Six mechanical gates, with density and font size swept rather "
                          "than fitted. Is that defensible, or should one be dropped?"),
    ]
    y = 1.85
    for num, head, body in items:
        pill(s, 0.95, y + 0.05, 0.55, num, GOLD, size=12)
        tf = tb(s, 1.75, y, 10.9, 0.95)
        write(tf, head, 12.5, INK, True, first=True)
        write(tf, body, 10.5, INK2, space=3, line=1.3)
        y += 1.35
    rect(s, 0.95, 5.95, 11.9, 0.85, fill=PANEL2)
    tf = tb(s, 1.2, 6.08, 11.3, 0.6)
    write(tf, "And one question I would like your view on: is a deterministic detector seen as "
              "a strength here, or as a gap in the AI content of the project?",
          11, INK, first=True, line=1.3)
    return s


# --------------------------------------------------------------------------- #
def main():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    slide_title(prs)
    slide_lit(prs)
    slide_why(prs)
    slide_gap(prs)
    slide_workflow(prs)
    slide_parse(prs)
    slide_select(prs)
    slide_measure(prs)
    slide_results(prs)
    slide_status(prs)
    slide_plan(prs)
    slide_asks(prs)
    prs.save(OUT)
    print(f"wrote {OUT}  slides={len(prs.slides.__iter__.__self__._sldIdLst)}")


if __name__ == "__main__":
    main()

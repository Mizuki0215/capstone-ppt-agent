from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

INK     = RGBColor(0x10, 0x23, 0x3A)
INK2    = RGBColor(0x1E, 0x36, 0x52)
GOLD    = RGBColor(0xC0, 0x8A, 0x2E)
TEAL    = RGBColor(0x2E, 0x6F, 0x95)
RED     = RGBColor(0xA8, 0x35, 0x42)
GREY    = RGBColor(0x5A, 0x6B, 0x7C)
LGREY   = RGBColor(0x8A, 0x99, 0xA8)
PANEL   = RGBColor(0xF4, 0xF6, 0xF8)
PANEL2  = RGBColor(0xEC, 0xF1, 0xF5)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
REDBG   = RGBColor(0xFA, 0xEE, 0xEF)
GOLDBG  = RGBColor(0xF9, 0xF3, 0xE4)

FONT = "Helvetica Neue"
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def new_slide():
    return prs.slides.add_slide(BLANK)


def nostyle(sh):
    el = sh._element
    st = el.find(qn('p:style'))
    if st is not None:
        el.remove(st)
    return sh


def rrect(s, x, y, w, h, fill=None, line=None, lw=1.0, radius=0.035, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    sh.text_frame.word_wrap = True
    nostyle(sh)
    return sh


def tbox(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = 0; tf.margin_bottom = 0
    return tf


def add(tf, text, size=13, bold=False, color=INK, align=PP_ALIGN.LEFT,
        space_before=0, space_after=0, line=1.18, italic=False, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line
    r = p.add_run(); r.text = text
    f = r.font
    f.name = FONT; f.size = Pt(size); f.bold = bold; f.italic = italic; f.color.rgb = color
    return p


def header(s, kicker, title, sub=None):
    tf = tbox(s, 0.85, 0.42, 11.6, 0.3)
    add(tf, kicker.upper(), size=9.5, bold=True, color=GOLD, first=True)
    tf = tbox(s, 0.85, 0.72, 11.6, 0.62)
    add(tf, title, size=27, bold=True, color=INK, first=True)
    if sub:
        tf = tbox(s, 0.85, 1.42, 11.6, 0.35)
        add(tf, sub, size=12, color=GREY, first=True)
    yl = 1.32 if not sub else 1.86
    ln = s.shapes.add_connector(1, Inches(0.85), Inches(yl), Inches(12.48), Inches(yl))
    ln.line.color.rgb = RGBColor(0xDD, 0xE2, 0xE8); ln.line.width = Pt(0.9)


def footer(s, page):
    tf = tbox(s, 0.85, 7.02, 8.0, 0.25)
    add(tf, "DSAI4901  ·  Capstone Project Proposal  ·  CHAN Yee Tung", size=8, color=LGREY, first=True)
    tf = tbox(s, 12.0, 7.02, 0.5, 0.25)
    add(tf, f"{page:02d}", size=8.5, bold=True, color=LGREY, align=PP_ALIGN.RIGHT, first=True)


def bullets(tf, items, size=11, color=INK2, gap=4, line=1.2, mark="•", mark_color=GOLD):
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else gap)
        p.line_spacing = line
        r1 = p.add_run(); r1.text = mark + "  "
        r1.font.name = FONT; r1.font.size = Pt(size); r1.font.bold = True; r1.font.color.rgb = mark_color
        r2 = p.add_run(); r2.text = it
        r2.font.name = FONT; r2.font.size = Pt(size); r2.font.color.rgb = color


# ============================ 01 TITLE ============================
s = new_slide()
rrect(s, 0, 0, 0.28, H, fill=INK, shape=MSO_SHAPE.RECTANGLE)
rrect(s, 0.28, 0, 0.06, H, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)

tf = tbox(s, 1.0, 1.30, 8.0, 0.3)
add(tf, "DSAI4901  ·  CAPSTONE PROJECT PROPOSAL", size=10, bold=True, color=GOLD, first=True)

tf = tbox(s, 1.0, 1.80, 8.3, 1.6)
add(tf, "Paper-Distillation PPT Agent", size=39, bold=True, color=INK, line=1.05, first=True)
add(tf, "From generating to verifying", size=25, color=TEAL, space_before=12, line=1.1)

rrect(s, 1.0, 4.05, 1.5, 0.045, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)

tf = tbox(s, 1.0, 4.30, 7.6, 0.8)
add(tf, "A slide generation system built around content traceability\nand deck-readiness",
    size=13.5, color=GREY, line=1.45, first=True)

tf = tbox(s, 1.0, 5.55, 5.5, 1.2)
add(tf, "CHAN Yee Tung", size=13, bold=True, color=INK, first=True)
add(tf, "Supervisor: Mr. Chen Xianwei", size=10.5, color=GREY, space_before=3)
add(tf, "October 2026", size=10.5, color=GREY, space_before=1)

stats = [("35", "papers reviewed"), ("8", "functional gaps"), ("1", "research direction")]
for i, (num, lab) in enumerate(stats):
    y = 1.95 + i * 1.62
    tf = tbox(s, 9.75, y, 2.6, 0.8)
    add(tf, num, size=46, bold=True, color=GOLD, line=0.95, first=True)
    tf = tbox(s, 9.75, y + 0.72, 2.6, 0.3)
    add(tf, lab, size=10.5, color=GREY, first=True)
    if i < 2:
        ln = s.shapes.add_connector(1, Inches(9.75), Inches(y + 1.42), Inches(12.3), Inches(y + 1.42))
        ln.line.color.rgb = RGBColor(0xE4, 0xE8, 0xEC); ln.line.width = Pt(0.75)

footer(s, 1)

# ============================ 02 LITERATURE ============================
s = new_slide()
header(s, "01 · FOUNDATION", "Literature review: from 367 papers to 35")

rows = [("367", "arXiv candidates", 8.6, INK),
        ("69",  "after relevance screening", 5.6, INK2),
        ("35",  "read in depth (30 agents + 5 education)", 4.2, TEAL),
        ("18",  "with author-released code", 3.6, GOLD)]
y0 = 2.10
for i, (num, lab, wbar, col) in enumerate(rows):
    y = y0 + i * 0.98
    rrect(s, 0.85, y, wbar, 0.74, fill=col if i == 3 else PANEL, line=None)
    tf = tbox(s, 0.85 + 0.22, y + 0.13, 0.95, 0.5)
    add(tf, num, size=21, bold=True, color=WHITE if i == 3 else INK, first=True)
    tf = tbox(s, 0.85 + 1.25, y + 0.20, wbar - 1.3, 0.36)
    add(tf, lab, size=10.5, color=WHITE if i == 3 else GREY, first=True)

rrect(s, 9.35, 2.10, 3.1, 3.35, fill=PANEL2)
tf = tbox(s, 9.60, 2.26, 2.62, 0.3)
add(tf, "WHAT I ACTUALLY DID", size=9, bold=True, color=GOLD, first=True)
tf = tbox(s, 9.60, 2.58, 2.62, 2.75)
bullets(tf, ["12 arXiv queries across slide, PPT, poster and deck",
             "Relevance screening to remove unrelated work",
             "Full-text keyword scan of all 35 papers",
             "GitHub links extracted from each PDF, then verified by HTTP"],
        size=8.8, gap=7, line=1.25)

tf = tbox(s, 0.85, 6.25, 8.2, 0.4)
add(tf, "18/35 release author code (each link verified by HTTP); the rest are paper-only or anonymous submissions",
    size=9, color=LGREY, first=True)
footer(s, 2)

# ============================ 03 WHAT THEY DO WELL ============================
s = new_slide()
header(s, "01 · FOUNDATION", "Four things they already do well",
       "First establish what is solved — this decides what I should not rebuild")

cards = [
    ("01", "Generation & layout", "Decks already look convincing: stable layout, consistent styling, competitive in blind tests.",
     "Zheng et al. (2025); Vats et al. (2026)"),
    ("02", "Native editable output", "Work has moved into the .pptx object layer, preserving styling and editability.",
     "Jung et al. (2025); Zheng et al. (2026b)"),
    ("03", "Evaluation methods", "From holistic scores to task-based tests: answering questions on a deck, gating readiness.",
     "Pang et al. (2025); Hu et al. (2026)"),
    ("04", "Multimodal & narrative", "Figures, tables and equations enter the layout; story structure is now modelled explicitly.",
     "Liang et al. (2025); Ozden et al. (2026a)"),
]
cw, gap = 2.86, 0.22
for i, (num, title, body, cite) in enumerate(cards):
    x = 0.85 + i * (cw + gap)
    rrect(s, x, 2.15, cw, 3.02, fill=PANEL)
    rrect(s, x, 2.15, cw, 0.05, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
    tf = tbox(s, x + 0.24, 2.38, cw - 0.4, 0.35)
    add(tf, num, size=11, bold=True, color=GOLD, first=True)
    tf = tbox(s, x + 0.24, 2.70, cw - 0.42, 0.7)
    add(tf, title, size=13.5, bold=True, color=INK, line=1.15, first=True)
    tf = tbox(s, x + 0.24, 3.42, cw - 0.42, 1.05)
    add(tf, body, size=9.8, color=INK2, line=1.32, first=True)
    tf = tbox(s, x + 0.24, 4.20, cw - 0.42, 0.5)
    add(tf, cite, size=7.6, color=TEAL, line=1.2, first=True)

tf = tbox(s, 0.85, 5.62, 11.6, 0.5)
add(tf, "Conclusion: generation is commoditised. Building one more generator is not a contribution.",
    size=12, bold=True, color=RED, first=True)
footer(s, 3)

# ============================ 04 FUNCTION MAP ============================
s = new_slide()
header(s, "01 · FOUNDATION", "Decomposing a PPT agent into 8 functions",
       "A precise gap needs a function map — the next four slides walk through it")

funcs = [("①", "Parsing"), ("②", "Content"), ("③", "Narrative"),
         ("④", "Layout"), ("⑤", "Output"), ("⑥", "Inspection")]
bw, bh, bgap = 1.62, 1.30, 0.30
x0 = 0.85
for i, (num, name) in enumerate(funcs):
    x = x0 + i * (bw + bgap)
    rrect(s, x, 2.30, bw, bh, fill=PANEL2, line=RGBColor(0xD8, 0xE0, 0xE8))
    tf = tbox(s, x, 2.46, bw, 0.32)
    add(tf, num, size=13, bold=True, color=GOLD, align=PP_ALIGN.CENTER, first=True)
    tf = tbox(s, x, 2.86, bw, 0.4)
    add(tf, name, size=13, bold=True, color=INK, align=PP_ALIGN.CENTER, first=True)
    if i < 5:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw + 0.05), Inches(2.83),
                                Inches(0.20), Inches(0.24))
        ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
        ar.line.fill.background(); ar.shadow.inherit = False; nostyle(ar)

for i, (num, name, desc) in enumerate([
        ("⑦", "Speaker notes", "Cross-stage: turn content into speakable pacing"),
        ("⑧", "Provenance", "Cross-stage: every sentence needs a source")]):
    y = 4.15 + i * 1.05
    rrect(s, 0.85, y, 11.6, 0.86, fill=GOLDBG, line=None)
    tf = tbox(s, 1.10, y + 0.10, 0.5, 0.6)
    add(tf, num, size=15, bold=True, color=GOLD, first=True)
    tf = tbox(s, 1.62, y + 0.11, 2.6, 0.6)
    add(tf, name, size=13, bold=True, color=INK, first=True)
    tf = tbox(s, 4.35, y + 0.20, 7.8, 0.5)
    add(tf, desc, size=10.5, color=GREY, first=True)

tf = tbox(s, 0.85, 6.55, 11.6, 0.35)
add(tf, "Next four slides: two gaps per slide — symptom · evidence · consequence",
    size=10.5, color=LGREY, first=True)
footer(s, 4)


def weakness_slide(page, kicker, title, left, right):
    s = new_slide()
    header(s, kicker, title)
    for idx, d in enumerate([left, right]):
        x = 0.85 + idx * 6.02
        wcol = 5.72
        rrect(s, x, 1.72, wcol, 4.95, fill=WHITE, line=RGBColor(0xDF, 0xE5, 0xEB), lw=0.9)
        rrect(s, x, 1.72, wcol, 0.055, fill=RED, shape=MSO_SHAPE.RECTANGLE)

        tf = tbox(s, x + 0.28, 1.92, wcol - 0.5, 0.36)
        add(tf, d["label"], size=9.5, bold=True, color=RED, first=True)
        tf = tbox(s, x + 0.28, 2.20, wcol - 0.5, 0.45)
        add(tf, d["name"], size=15.5, bold=True, color=INK, first=True)

        tf = tbox(s, x + 0.28, 2.76, wcol - 0.5, 0.22)
        add(tf, "SYMPTOMS", size=8.5, bold=True, color=LGREY, first=True)
        tf = tbox(s, x + 0.28, 2.97, wcol - 0.5, 1.20)
        bullets(tf, d["symptoms"], size=9.2, gap=2.5, line=1.18, mark="▪", mark_color=RED)

        tf = tbox(s, x + 0.28, 4.18, wcol - 0.5, 0.22)
        add(tf, "EVIDENCE · APA", size=8.5, bold=True, color=LGREY, first=True)
        tf = tbox(s, x + 0.28, 4.39, wcol - 0.5, 0.70)
        add(tf, d["evidence"], size=8.8, color=TEAL, line=1.25, first=True)

        rrect(s, x + 0.20, 5.18, wcol - 0.40, 1.12, fill=REDBG, line=None)
        tf = tbox(s, x + 0.36, 5.27, wcol - 0.70, 0.2)
        add(tf, "CONSEQUENCE", size=8.5, bold=True, color=RED, first=True)
        tf = tbox(s, x + 0.36, 5.47, wcol - 0.70, 0.76)
        add(tf, d["consequence"], size=9.2, color=INK, line=1.22, first=True)
    footer(s, page)
    return s


# ============================ 05 GAP 1–2 ============================
weakness_slide(5, "02 · FUNCTIONAL GAPS", "Gap 1  |  Parsing and content selection",
    {"label": "① PARSING", "name": "Figures and captions split apart",
     "symptoms": ["figure and caption are detached, so image and text no longer correspond",
                  "two-column papers are read in the wrong order; paragraphs get spliced",
                  "tables are flattened into a wall of text, losing row and column structure"],
     "evidence": "Parsing is treated as preprocessing and figure–text alignment is not enforced (Pang et al., 2025; Fu et al., 2021).",
     "consequence": "A corrupted input is inherited by every later step, and the error is invisible in the final deck."},
    {"label": "② CONTENT SELECTION", "name": "Even allocation, no emphasis",
     "symptoms": ["one slide per section, regardless of how much it matters",
                  "the key experimental result is dropped while background survives",
                  "method details are pushed into the introduction slide"],
     "evidence": "Most methods concentrate on text selection and ignore the link between space and importance (Liang et al., 2025; Chen et al., 2026).",
     "consequence": "The deck is complete but has no emphasis; the audience keeps only the title and the speaker cannot name the key claim."})

# ============================ 06 GAP 3–4 ============================
weakness_slide(6, "02 · FUNCTIONAL GAPS", "Gap 2  |  Narrative and layout",
    {"label": "③ NARRATIVE", "name": "A table of contents, not a talk",
     "symptoms": ["section-by-section summarising reproduces the paper's order",
                  "ten slides of background, two of results — emphasis inverted",
                  "no motivation → problem → insight → evidence arc"],
     "evidence": "Source text is summarised straight into slides (Ozden et al., 2026a); explicit narrative planning remains rare (Vats et al., 2026).",
     "consequence": "The speaker reads a table of contents aloud and the audience cannot build causal understanding."},
    {"label": "④ LAYOUT", "name": "Overflow, overlap, clipping",
     "symptoms": ["text runs past the slide edge; elements overlap each other",
                  "fonts too small and contrast too low to read once projected",
                  "figures cropped, whitespace unbalanced, every slide a wall of bullets"],
     "evidence": "Local failures include overflow, overlap, clipping and off-canvas placement (Tian et al., 2026); models understand content yet fail at layout (Huang et al., 2025).",
     "consequence": "This is the most visible failure: text clipped and figures covered during the talk, so the audience loses trust immediately."})

# ============================ 07 GAP 5–6 ============================
weakness_slide(7, "02 · FUNCTIONAL GAPS", "Gap 3  |  Output and inspection",
    {"label": "⑤ OUTPUT", "name": "Looks usable, cannot be edited",
     "symptoms": ["output is an image or HTML, not editable inside PowerPoint",
                  "even .pptx output is all text boxes — editing one word breaks the layout",
                  "charts are rasterised, so the underlying data is gone"],
     "evidence": "Agents frequently rasterise editable content or break the layout (Zheng et al., 2026b); only an object-model route preserves styling (Jung et al., 2025).",
     "consequence": "Users get an artefact they cannot modify, so it is unusable and the tool is abandoned."},
    {"label": "⑥ INSPECTION", "name": "One-shot feedback, no attribution",
     "symptoms": ["the whole deck is rewritten and then reviewed once",
                  "errors cannot be localised to an element — which shape overflows?",
                  "repair can make things worse, with no convergence guarantee"],
     "evidence": "A monolithic one-version-one-feedback loop makes local errors hard to attribute (Tian et al., 2026); reflection must be grounded in rendered state (Zheng et al., 2026a).",
     "consequence": "Iteration becomes a gamble: each pass may degrade the deck and nobody can say why."})

# ============================ 08 GAP 7–8 ============================
weakness_slide(8, "02 · FUNCTIONAL GAPS", "Gap 4  |  Speaker notes and provenance",
    {"label": "⑦ SPEAKER NOTES", "name": "Notes are the bullets again",
     "symptoms": ["speaker notes duplicate the text already on the slide",
                  "no time budget — no idea how many slides fit three minutes",
                  "no transitions, so slides do not connect to each other"],
     "evidence": "Delivery is under-optimised in current systems (Yang et al., 2026); only 5 of 35 papers mention speaker notes, none as a research focus.",
     "consequence": "The speaker reads the slide while the audience reads and listens at once, splitting attention."},
    {"label": "⑧ PROVENANCE", "name": "Writes the words, cannot cite them",
     "symptoms": ["bullets carry no source, so there is no path back to a passage",
                  "related work is presented as 'we propose'",
                  "figures and tables misnumbered; numbers attached to the wrong claim"],
     "evidence": "Retrieval improves reliability but per-sentence provenance is not exposed (Xie et al., 2025); global intent is kept while sentence-level anchors are missing (Ozden et al., 2026a).",
     "consequence": "A wrong number goes unnoticed; in academic settings one misattributed claim destroys the credibility of the talk."})

# ============================ 09 CONSEQUENCE CHAIN ============================
s = new_slide()
header(s, "02 · FUNCTIONAL GAPS", "A single failure is amplified downstream")

chain = ["Bad input", "Bad content", "Weak story", "Broken layout", "No repair", "No verification"]
cw2, ch2, gap2 = 1.72, 0.72, 0.26
x0 = 0.85
for i, t in enumerate(chain):
    x = x0 + i * (cw2 + gap2)
    rrect(s, x, 1.85, cw2, ch2, fill=INK if i < 5 else RED, line=None)
    tf = tbox(s, x, 2.05, cw2, 0.4)
    add(tf, t, size=10.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER, first=True)
    if i < 5:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + cw2 + 0.04), Inches(2.12),
                                Inches(0.18), Inches(0.18))
        ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
        ar.line.fill.background(); ar.shadow.inherit = False; nostyle(ar)

tf = tbox(s, 0.85, 2.72, 11.6, 0.3)
add(tf, "Every upstream error is amplified downstream — and cannot be traced back",
    size=10, color=LGREY, first=True)

impacts = [("Audience", "Cannot follow or remember; sees clipped text live", "Attention lost"),
           ("Speaker", "Will not trust it; must rebuild; cannot answer 'where does this number come from?'", "Trust collapses"),
           ("Field", "Cannot compare systems, because there is no shared measure of trustworthiness", "Progress stalls")]
for i, (who, what, tag) in enumerate(impacts):
    x = 0.85 + i * 3.92
    rrect(s, x, 3.30, 3.66, 1.62, fill=PANEL)
    tf = tbox(s, x + 0.26, 3.45, 3.15, 0.3)
    add(tf, who, size=11.5, bold=True, color=GOLD, first=True)
    tf = tbox(s, x + 0.26, 3.76, 3.15, 0.85)
    add(tf, what, size=9.6, color=INK2, line=1.3, first=True)
    tf = tbox(s, x + 0.26, 4.56, 3.15, 0.3)
    add(tf, "→ " + tag, size=9.2, bold=True, color=RED, first=True)

rrect(s, 0.85, 5.45, 11.6, 0.95, fill=GOLDBG, line=None)
tf = tbox(s, 1.15, 5.62, 11.0, 0.65)
add(tf, "The shared problem across all 35 papers: everyone optimises generation; no one measures trust.",
    size=14, bold=True, color=INK, first=True)
footer(s, 9)

# ============================ 10 DIRECTION ============================
s = new_slide()
header(s, "03 · POSITIONING", "My direction: a paper-distillation PPT agent",
       "Explicitly not lecture notes — the two tasks have different success criteria")

rows = [("Input", "A single paper (PDF)", "Course material or lecture content"),
        ("Goal", "Compress the research into a defensible argument chain", "Break knowledge into learning units"),
        ("Success", "Traceable content and a complete argument", "Learner comprehension and exercises"),
        ("Hard part", "Factual correctness", "Instructional design")]
tx, ty = 0.85, 2.05
colw = [1.15, 2.70, 2.35]
rrect(s, tx, ty, sum(colw), 0.44, fill=INK, shape=MSO_SHAPE.RECTANGLE)
heads = ["", "Paper distillation (this project)", "Lecture notes (not doing)"]
cx = tx
for i, hd in enumerate(heads):
    tf = tbox(s, cx + 0.16, ty + 0.11, colw[i] - 0.2, 0.3)
    add(tf, hd, size=9.2, bold=True, color=WHITE, first=True)
    cx += colw[i]
for r, row in enumerate(rows):
    y = ty + 0.44 + r * 0.86
    bg = PANEL if r % 2 == 0 else WHITE
    rrect(s, tx, y, sum(colw), 0.86, fill=bg, line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
    cx = tx
    for i, cell in enumerate(row):
        tf = tbox(s, cx + 0.16, y + 0.10, colw[i] - 0.26, 0.68)
        if i == 0:
            add(tf, cell, size=9.2, bold=True, color=GREY, first=True)
        elif i == 1:
            add(tf, cell, size=9.0, color=INK, line=1.22, first=True)
        else:
            add(tf, cell, size=9.0, color=LGREY, line=1.22, first=True)
        cx += colw[i]

rrect(s, 7.32, 2.05, 5.16, 3.90, fill=PANEL2)
tf = tbox(s, 7.58, 2.22, 4.6, 0.3)
add(tf, "RESEARCH QUESTIONS", size=9, bold=True, color=GOLD, first=True)
rqs = [("RQ1", "How can every bullet be anchored to a verifiable source?"),
       ("RQ2", "How can deck usability be turned into a computable metric?"),
       ("RQ3", "Can an inspect–repair loop improve both at an acceptable cost?")]
for i, (k, q) in enumerate(rqs):
    y = 2.60 + i * 1.02
    tf = tbox(s, 7.58, y, 0.6, 0.3)
    add(tf, k, size=10.5, bold=True, color=RED, first=True)
    tf = tbox(s, 8.14, y - 0.02, 4.05, 0.9)
    add(tf, q, size=10, color=INK2, line=1.32, first=True)

footer(s, 10)

# ============================ 11 CONTRIBUTIONS ============================
s = new_slide()
header(s, "03 · POSITIONING", "Three contributions")

contribs = [
    ("01", "A computable notion of trustworthiness",
     "Content trust and deck usability each become an automatically measurable ratio:\ntraceable-bullet ratio and deck-ready rate.",
     "Deliverable:\nmetric definitions + open-source toolkit"),
    ("02", "A step-wise inspect–repair loop",
     "Change one element at a time, render and verify immediately, so errors are attributable;\nreport convergence rather than only a final score.",
     "Deliverable:\nagent implementation + convergence curves"),
    ("03", "A public dataset and evaluation protocol",
     "150 human-annotated reference slides, a 30-participant pairwise study,\nand rerunnable evaluation scripts.",
     "Deliverable:\ndataset + benchmark script"),
]
for i, (num, title, body, deliver) in enumerate(contribs):
    y = 1.85 + i * 1.62
    rrect(s, 0.85, y, 11.6, 1.42, fill=PANEL if i % 2 == 0 else WHITE,
          line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.7)
    tf = tbox(s, 1.10, y + 0.20, 0.9, 0.6)
    add(tf, num, size=22, bold=True, color=GOLD, first=True)
    tf = tbox(s, 2.00, y + 0.18, 4.6, 0.4)
    add(tf, title, size=13, bold=True, color=INK, first=True)
    tf = tbox(s, 2.00, y + 0.60, 6.5, 0.75)
    add(tf, body, size=9.4, color=INK2, line=1.32, first=True)
    tf = tbox(s, 8.95, y + 0.48, 3.3, 0.7)
    add(tf, deliver, size=8.5, bold=True, color=TEAL, line=1.25, first=True)

footer(s, 11)

# ============================ 12 ARCHITECTURE ============================
s = new_slide()
header(s, "04 · METHOD", "System architecture", "Gold = new contributions; the rest reuses validated practice")

stages = [("PDF", "input", False), ("Parse", "section / figure / table", False),
          ("Evidence graph", "claim–evidence", True), ("Narrative plan", "space allocation", True),
          ("Layout solver", "capacity-aware", True), ("Render", "python-pptx", False),
          ("Inspect", "violation detection", True), ("Repair", "local rewrite", True)]
bw2, gap3 = 1.36, 0.15
x0 = 0.85
for i, (name, desc, new) in enumerate(stages):
    x = x0 + i * (bw2 + gap3)
    fill = GOLDBG if new else PANEL2
    line = GOLD if new else RGBColor(0xD8, 0xE0, 0xE8)
    rrect(s, x, 2.05, bw2, 1.32, fill=fill, line=line, lw=1.2 if new else 0.8)
    tf = tbox(s, x + 0.06, 2.20, bw2 - 0.12, 0.5)
    add(tf, name, size=10.5, bold=True, color=INK, align=PP_ALIGN.CENTER, line=1.1, first=True)
    tf = tbox(s, x + 0.06, 2.76, bw2 - 0.12, 0.5)
    add(tf, desc, size=7.2, color=GREY, align=PP_ALIGN.CENTER, line=1.15, first=True)
    if i < len(stages) - 1:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw2 + 0.015), Inches(2.60),
                                Inches(0.12), Inches(0.20))
        ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
        ar.line.fill.background(); ar.shadow.inherit = False; nostyle(ar)

principles = [("Restrict the output space", "The model writes structured content only; geometry and styling belong to templates"),
              ("One element at a time", "Local rewrites with immediate verification make errors attributable"),
              ("Every judgement has a number", "No 'looks fine' — only measured violations and ratios")]
for i, (t, d) in enumerate(principles):
    x = 0.85 + i * 3.92
    rrect(s, x, 3.95, 3.66, 1.12, fill=WHITE, line=RGBColor(0xDF, 0xE5, 0xEB), lw=0.8)
    tf = tbox(s, x + 0.26, 4.10, 3.1, 0.34)
    add(tf, t, size=11, bold=True, color=INK, first=True)
    tf = tbox(s, x + 0.26, 4.44, 3.1, 0.55)
    add(tf, d, size=9.2, color=GREY, line=1.28, first=True)

tf = tbox(s, 0.85, 5.45, 11.6, 0.7)
add(tf, "The output is not an image but an editable .pptx: layout comes from constraint solving, content from the evidence graph.",
    size=11, color=INK2, first=True)
footer(s, 12)

# ============================ 13 EVALUATION ============================
s = new_slide()
header(s, "04 · METHOD", "How I will show it works", "Three tracks in parallel, avoiding the circularity of an LLM judging an LLM")

tracks = [("Automatic (geometry)", "Violation count, deck-ready rate", "8 held-out papers, 150 annotated slides", "Deterministic and rerunnable"),
          ("Task-based (QA)", "Answer accuracy from the deck", "10 questions × 8 papers", "Tests whether a reader can extract correct facts"),
          ("Human", "Pairwise preference, speakability", "30 participants", "Design has no ground truth, so only relative comparison is valid")]
hdrs = ["Track", "Metric", "Sample", "Why it is needed"]
colx = [0.85, 3.55, 6.75, 9.55]
colw3 = [2.60, 3.10, 2.70, 2.90]
rrect(s, 0.85, 2.05, 11.6, 0.42, fill=INK, shape=MSO_SHAPE.RECTANGLE)
for i, h in enumerate(hdrs):
    tf = tbox(s, colx[i] + 0.12, 2.13, colw3[i] - 0.2, 0.3)
    add(tf, h, size=9, bold=True, color=WHITE, first=True)
for r, row in enumerate(tracks):
    y = 2.47 + r * 0.72
    rrect(s, 0.85, y, 11.6, 0.72, fill=PANEL if r % 2 == 0 else WHITE,
          line=RGBColor(0xE4, 0xEA, 0xF0), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
    for i, cell in enumerate(row):
        tf = tbox(s, colx[i] + 0.12, y + 0.10, colw3[i] - 0.22, 0.55)
        add(tf, cell, size=8.6 if i == 3 else 9.2,
            bold=(i == 0), color=INK if i < 3 else GREY, line=1.22, first=True)

rrect(s, 0.85, 4.95, 5.7, 1.12, fill=PANEL2)
tf = tbox(s, 1.08, 5.09, 5.2, 0.25)
add(tf, "BASELINES", size=8.5, bold=True, color=GOLD, first=True)
tf = tbox(s, 1.08, 5.35, 5.2, 0.7)
add(tf, "① Naive single-pass (one generation, no inspection)\n② PPTAgent (strongest reproducible system)", size=9.2, color=INK2, line=1.35, first=True)

rrect(s, 6.78, 4.95, 5.67, 1.12, fill=PANEL2)
tf = tbox(s, 7.01, 5.09, 5.2, 0.25)
add(tf, "ABLATION", size=8.5, bold=True, color=GOLD, first=True)
tf = tbox(s, 7.01, 5.35, 5.2, 0.7)
add(tf, "Remove provenance anchors / remove inspection / remove repair\n→ attribute each module's contribution", size=9.2, color=INK2, line=1.35, first=True)
footer(s, 13)

# ============================ 14 TIMELINE ============================
s = new_slide()
header(s, "05 · PLAN", "20-week timeline")

phases = [("Literature & scope", 0, 2, "W1–2"),
          ("Setup & spikes", 2, 2, "W3–4"),
          ("Parsing & evidence", 4, 3, "W5–7"),
          ("Layout & rendering", 7, 4, "W8–11"),
          ("Inspection & repair", 11, 3, "W12–14"),
          ("Experiments & study", 14, 4, "W15–18"),
          ("Report & talk", 18, 2, "W19–20")]
gx, gw = 2.75, 9.4
for wk in range(0, 21, 5):
    x = gx + gw * wk / 20
    ln = s.shapes.add_connector(1, Inches(x), Inches(1.85), Inches(x), Inches(5.95))
    ln.line.color.rgb = RGBColor(0xEC, 0xF0, 0xF4); ln.line.width = Pt(0.75)
    tf = tbox(s, x - 0.35, 1.60, 0.7, 0.22)
    add(tf, f"W{wk}" if wk else "", size=7.5, color=LGREY, align=PP_ALIGN.CENTER, first=True)

for i, (name, start, dur, lab) in enumerate(phases):
    y = 2.00 + i * 0.56
    x = gx + gw * start / 20
    w = max(gw * dur / 20, 0.9)
    col = GOLD if i in (2, 4) else TEAL
    rrect(s, x, y, w, 0.36, fill=col, line=None, radius=0.25)
    tf = tbox(s, x + 0.12, y + 0.075, w - 0.15, 0.25)
    add(tf, lab, size=7.5, bold=True, color=WHITE, first=True)
    tf = tbox(s, 0.85, y + 0.05, 1.90, 0.3)
    add(tf, name, size=9.2, bold=True, color=INK, first=True)

mss = [("2026-11-05", "Proposal submission"), ("2027-01-07", "Interim Report"),
       ("2027-04-08", "Final Report + Turnitin + AI Report")]
for i, (dt, nm) in enumerate(mss):
    x = 0.85 + i * 3.92
    rrect(s, x, 6.00, 3.66, 0.76, fill=PANEL)
    rrect(s, x, 6.00, 0.05, 0.76, fill=RED, shape=MSO_SHAPE.RECTANGLE)
    tf = tbox(s, x + 0.22, 6.08, 1.6, 0.3)
    add(tf, dt, size=9.5, bold=True, color=RED, first=True)
    tf = tbox(s, x + 0.22, 6.40, 3.3, 0.3)
    add(tf, nm, size=8.5, color=GREY, first=True)
footer(s, 14)

# ============================ 15 REFERENCES ============================
s = new_slide()
header(s, "APPENDIX · APA 7TH", "References")

refs = [
 "Chen, H., Zhou, X., Zhou, W., Shao, X., Zhu, Y., Wang, B., Hong, J., Jia, A., & Wu, F. (2026). X+Slides: Benchmarking audience-conditioned slide generation (arXiv:2606.19256). arXiv. https://doi.org/10.48550/arXiv.2606.19256",
 "Fu, T.-J., Wang, W. Y., McDuff, D., & Song, Y. (2021). DOC2PPT: Automatic presentation slides generation from scientific documents (arXiv:2101.11796). arXiv. https://doi.org/10.48550/arXiv.2101.11796",
 "Ge, J., Wang, Z. Z., Zhou, X., Peng, Y.-H., Subramanian, S., Tan, Q., Sap, M., Suhr, A., Fried, D., Neubig, G., & Darrell, T. (2025). AutoPresent: Designing structured visuals from scratch (arXiv:2501.00912). arXiv. https://doi.org/10.48550/arXiv.2501.00912",
 "Hu, H., Dang, C., Liu, Y., Kang, H., He, C., & Li, W. (2026). PosterMELD: Multi-agent paper-to-poster generation for controllable design diversity with editable print-ready outputs (arXiv:2608.02218). arXiv. https://doi.org/10.48550/arXiv.2608.02218",
 "Huang, Z., Liu, X., Hu, T., Zhang, K., & Liu, Y. (2025). PPTBench: Towards holistic evaluation of large language models for PowerPoint layout and design understanding (arXiv:2512.02624). arXiv. https://doi.org/10.48550/arXiv.2512.02624",
 "Jung, K., Cho, H., Yun, J., Yang, S., Jang, J., & Choo, J. (2025). Talk to your slides: High-efficiency slide editing via language-driven structured data manipulation (arXiv:2505.11604). arXiv. https://doi.org/10.48550/arXiv.2505.11604",
 "Liang, X., Zhang, Z., Zhang, X., Su, H., Xu, Y., Sun, S., & You, C. (2025). SlideGen: Collaborative multimodal agents for scientific slide generation (arXiv:2512.04529). arXiv. https://doi.org/10.48550/arXiv.2512.04529",
 "Ozden, T. C., VS, S., Horoz, F., Kara, O., Kim, J., & Rehg, J. M. (2026a). Narrative-driven paper-to-slide generation via ArcDeck (arXiv:2604.11969). arXiv. https://doi.org/10.48550/arXiv.2604.11969",
 "Ozden, T. C., VS, S., Horoz, F., Kara, O., Hakkani-Tür, D., Kim, J., & Rehg, J. M. (2026b). ConvDeck: Conversational paper-to-slide generation via stage-specific user feedback (arXiv:2609.00226). arXiv. https://doi.org/10.48550/arXiv.2609.00226",
 "Pang, W., Lin, K. Q., Jian, X., He, X., & Torr, P. (2025). Paper2Poster: Towards multimodal poster automation from scientific papers (arXiv:2505.21497). arXiv. https://doi.org/10.48550/arXiv.2505.21497",
 "Sun, E., Hou, Y., Wang, D., Zhang, Y., & Wang, N. X. R. (2021). D2S: Document-to-slide generation via query-based text summarization (arXiv:2105.03664). arXiv. https://doi.org/10.48550/arXiv.2105.03664",
 "Tian, M., Zeng, Z., Yang, Y., Gao, X., Li, Y., Huang, Z., Wang, X., Lv, C., Cheng, M., Liu, B., Qiu, K., Dai, Q., Chen, D., Dong, Y., Zheng, X., Li, J., & Luo, C. (2026). ReDeck: Step-level render-grounded refinement for document-to-slide generation (arXiv:2609.00194). arXiv. https://doi.org/10.48550/arXiv.2609.00194",
 "Vats, V., Sharma, K., & Wang, Y. (2026). SlideLab: Audience-centered scientific slide generation and evaluation (arXiv:2609.30294). arXiv. https://doi.org/10.48550/arXiv.2609.30294",
 "Xie, E., Waterfield, D., Kennedy, M., & Zhang, A. (2025). SlideBot: A multi-agent framework for generating informative, reliable, multi-modal presentations (arXiv:2511.09804). arXiv. https://doi.org/10.48550/arXiv.2511.09804",
 "Yang, M., Zhang, Z., Li, J., Liu, H., Cai, Y., & Zheng, W. (2026). DeepSlide: From artifacts to presentation delivery (arXiv:2605.15202). arXiv. https://doi.org/10.48550/arXiv.2605.15202",
 "Zheng, H., Guan, X., Kong, H., Zheng, J., Zhou, W., Lin, H., Lu, Y., He, B., Han, X., & Sun, L. (2025). PPTAgent: Generating and evaluating presentations beyond text-to-slides (arXiv:2501.03936). arXiv. https://doi.org/10.48550/arXiv.2501.03936",
 "Zheng, H., Mo, G., Yan, X., Yuan, Q., Zhang, W., Chen, X., Lu, Y., Lin, H., Han, X., & Sun, L. (2026a). DeepPresenter: Environment-grounded reflection for agentic presentation generation (arXiv:2602.22839). arXiv. https://doi.org/10.48550/arXiv.2602.22839",
 "Zheng, H., Wang, F., Xiong, T., Yu, Y., Qian, S., Yu, H., Schwing, A., Nahrstedt, K., & Wu, M. (2026b). SLIDEFORGE: An LLM agent for controllable editing of slides as structured artifacts (arXiv:2609.03109). arXiv. https://doi.org/10.48550/arXiv.2609.03109",
]
half = 9
for c, group in enumerate([refs[:half], refs[half:]]):
    x = 0.85 + c * 5.95
    tf = tbox(s, x, 1.72, 5.55, 5.1)
    for i, r in enumerate(group):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else 4)
        p.line_spacing = 1.06
        run = p.add_run(); run.text = r
        run.font.name = FONT; run.font.size = Pt(7.6); run.font.color.rgb = INK2
footer(s, 15)

out = "/Users/yeetungchan/Documents/deepseek-harness/default-workspace/capstone-ppt-agent/deck/proposal_deck_en.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides._sldIdLst))

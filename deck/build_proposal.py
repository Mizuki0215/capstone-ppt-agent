# -*- coding: utf-8 -*-
"""Builds the capstone proposal deck in English and Chinese from one content model."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

INK = RGBColor(0x10, 0x23, 0x3A); INK2 = RGBColor(0x1E, 0x36, 0x52)
GOLD = RGBColor(0xC0, 0x8A, 0x2E); TEAL = RGBColor(0x2E, 0x6F, 0x95)
RED = RGBColor(0xA8, 0x35, 0x42); GREY = RGBColor(0x5A, 0x6B, 0x7C)
LGREY = RGBColor(0x8A, 0x99, 0xA8); PANEL = RGBColor(0xF4, 0xF6, 0xF8)
PANEL2 = RGBColor(0xEC, 0xF1, 0xF5); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
REDBG = RGBColor(0xFA, 0xEE, 0xEF); GOLDBG = RGBColor(0xF9, 0xF3, 0xE4)
W, H = 13.333, 7.5


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
    st = sh._element.find(qn('p:style'))
    if st is not None:
        sh._element.remove(st)
    return sh


def tbox(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    return tf


def add(tf, text, size=13, bold=False, color=INK, align=PP_ALIGN.LEFT,
        space_before=0, line=1.18, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.line_spacing = line
    r = p.add_run(); r.text = text
    f = r.font
    f.name = FONT; f.size = Pt(size); f.bold = bold; f.color.rgb = color
    return p


def bullets(tf, items, size=10, color=INK2, gap=4, line=1.2, mark="•", mark_color=GOLD):
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(0 if i == 0 else gap)
        p.line_spacing = line
        r1 = p.add_run(); r1.text = mark + "  "
        r1.font.name = FONT; r1.font.size = Pt(size); r1.font.bold = True; r1.font.color.rgb = mark_color
        r2 = p.add_run(); r2.text = it
        r2.font.name = FONT; r2.font.size = Pt(size); r2.font.color.rgb = color


def header(s, kicker, title, sub=None):
    tf = tbox(s, 0.85, 0.42, 11.6, 0.3)
    add(tf, kicker, size=9.5, bold=True, color=GOLD, first=True)
    tf = tbox(s, 0.85, 0.72, 11.6, 0.62)
    add(tf, title, size=26, bold=True, color=INK, first=True)
    if sub:
        tf = tbox(s, 0.85, 1.42, 11.6, 0.35)
        add(tf, sub, size=11.5, color=GREY, first=True)
    yl = 1.32 if not sub else 1.86
    ln = s.shapes.add_connector(1, Inches(0.85), Inches(yl), Inches(12.48), Inches(yl))
    ln.line.color.rgb = RGBColor(0xDD, 0xE2, 0xE8); ln.line.width = Pt(0.9)


def footer(s, page, L):
    foot = L["meta"]["foot"] if "meta" in L else L["foot"]
    tf = tbox(s, 0.85, 7.02, 8.0, 0.25)
    add(tf, foot, size=8, color=LGREY, first=True)
    tf = tbox(s, 12.0, 7.02, 0.5, 0.25)
    add(tf, f"{page:02d}", size=8.5, bold=True, color=LGREY, align=PP_ALIGN.RIGHT, first=True)


def table(s, x, y, cols, rows, rowh=0.62, headh=0.42, fs=8.6, hfs=8.6, bold_col0=True, zebra=True):
    rrect(s, x, y, sum(cols), headh, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = x
    for i, h in zip(range(len(cols)), rows[0][1] if False else []):
        pass
    return


# ============================ CONTENT ============================
C = {
"en": {
 "meta": {"font": "Helvetica Neue", "foot": "DSAI4901  ·  Capstone Project Proposal  ·  CHAN Yee Tung"},
 "s01": {"kicker": "DSAI4901  ·  CAPSTONE PROJECT PROPOSAL",
         "t1": "Paper-Distillation PPT Agent", "t2": "From generating to verifying",
         "desc": "A slide generation system built around a measurable definition\nof deck usability",
         "who": "CHAN Yee Tung", "sup": "Supervisor: Dr. Jibin Wu", "date": "October 2026",
         "stats": [("38", "papers reviewed"), ("8", "functional gaps"), ("1", "research direction")]},
 "s02": {"kicker": "01 · FOUNDATION", "title": "Literature review: from 367 papers to 38",
         "bars": [("367", "arXiv candidates", 8.6, "ink"),
                  ("69", "after relevance screening", 5.6, "ink2"),
                  ("38", "read in depth (33 agents + 5 education)", 4.4, "teal"),
                  ("18", "with author-released code", 3.6, "gold")],
         "box": "WHAT I ACTUALLY DID",
         "bullets": ["12 arXiv queries across slide, PPT, poster and deck",
                     "Relevance screening to remove unrelated work",
                     "Full-text keyword scan of all 38 papers",
                     "GitHub links extracted from each PDF, then verified by HTTP"],
         "note": "18/38 release author code (each link verified by HTTP); the rest are paper-only or anonymous submissions"},
 "s03": {"kicker": "01 · FOUNDATION", "title": "Four things they already do well",
         "sub": "First establish what is solved — this decides what not to rebuild",
         "cards": [("01", "Generation & layout", "Decks already look convincing: stable layout, consistent styling.", "Zheng et al. (2025); Vats et al. (2026)"),
                   ("02", "Native editable output", "Work has moved into the .pptx object layer, preserving editability.", "Jung et al. (2025); Zheng et al. (2026b)"),
                   ("03", "Evaluation methods", "From holistic scores to task-based tests and rubric gates.", "Zhang et al. (2025); Jang et al. (2026)"),
                   ("04", "Multimodal & narrative", "Figures and tables enter the layout; story structure is modelled.", "Liang et al. (2025); Ozden et al. (2026a)")],
         "concl": "Conclusion: generation is commoditised. One more generator is not a contribution."},
 "s04": {"kicker": "01 · FOUNDATION", "title": "Decomposing a PPT agent into 8 functions",
         "sub": "A precise gap needs a function map — the next four slides walk through it",
         "funcs": [("①", "Parsing"), ("②", "Content"), ("③", "Narrative"), ("④", "Layout"), ("⑤", "Output"), ("⑥", "Inspection")],
         "cross": [("⑦", "Speaker notes", "Cross-stage: turn content into speakable pacing"),
                   ("⑧", "Provenance", "Cross-stage: every sentence needs a source")],
         "note": "Next four slides: two gaps per slide — symptom · evidence · consequence"},
 "s05": {"kicker": "02 · FUNCTIONAL GAPS", "title": "Gap 1  |  Parsing and content selection",
         "left": {"label": "① PARSING", "name": "Figures and captions split apart",
                  "symptoms": ["figure and caption are detached, so image and text no longer correspond",
                               "two-column papers are read in the wrong order",
                               "tables are flattened into a wall of text"],
                  "evidence": "Parsing is treated as preprocessing and figure–text alignment is not enforced (Pang et al., 2025; Fu et al., 2021).",
                  "consequence": "A corrupted input is inherited by every later step, and the error is invisible in the final deck."},
         "right": {"label": "② CONTENT SELECTION", "name": "Even allocation, no emphasis",
                   "symptoms": ["one slide per section, regardless of how much it matters",
                                "the key result is dropped while background survives",
                                "method details are pushed into the introduction slide"],
                   "evidence": "Most methods concentrate on text selection and ignore the link between space and importance (Liang et al., 2025; Chen et al., 2026).",
                   "consequence": "The deck is complete but has no emphasis; the audience keeps only the title."}},
 "s06": {"kicker": "02 · FUNCTIONAL GAPS", "title": "Gap 2  |  Narrative and layout",
         "left": {"label": "③ NARRATIVE", "name": "A table of contents, not a talk",
                  "symptoms": ["section-by-section summarising reproduces the paper's order",
                               "ten slides of background, two of results",
                               "no motivation → problem → insight → evidence arc"],
                  "evidence": "Source text is summarised straight into slides (Ozden et al., 2026a); explicit narrative planning remains rare (Vats et al., 2026).",
                  "consequence": "The speaker reads a table of contents aloud and the audience cannot build causal understanding."},
         "right": {"label": "④ LAYOUT", "name": "Overflow, overlap, clipping",
                   "symptoms": ["text runs past the slide edge; elements overlap",
                                "fonts too small and contrast too low once projected",
                                "figures cropped, every slide a wall of bullets"],
                   "evidence": "Local failures include overflow, overlap, clipping and off-canvas placement (Tian et al., 2026); models understand content yet fail at layout (Huang et al., 2025).",
                   "consequence": "The most visible failure: text clipped and figures covered during the talk, so the audience loses trust."}},
 "s07": {"kicker": "02 · FUNCTIONAL GAPS", "title": "Gap 3  |  Output and inspection",
         "left": {"label": "⑤ OUTPUT", "name": "Looks usable, cannot be edited",
                  "symptoms": ["output is an image or HTML, not editable in PowerPoint",
                               "even .pptx output is all text boxes — one edit breaks the layout",
                               "charts are rasterised and the data is gone"],
                  "evidence": "Agents frequently rasterise editable content or break the layout (Zheng et al., 2026b); only an object-model route preserves styling (Jung et al., 2025).",
                  "consequence": "Users get an artefact they cannot modify, so it is unusable and the tool is abandoned."},
         "right": {"label": "⑥ INSPECTION", "name": "One-shot feedback, no attribution",
                   "symptoms": ["the whole deck is rewritten and reviewed once",
                                "errors cannot be localised to an element",
                                "repair can make things worse, with no convergence guarantee"],
                   "evidence": "A monolithic one-version-one-feedback loop makes local errors hard to attribute (Tian et al., 2026); reflection must be grounded in rendered state (Zheng et al., 2026a).",
                   "consequence": "Iteration becomes a gamble: each pass may degrade the deck and nobody can say why."}},
 "s08": {"kicker": "02 · FUNCTIONAL GAPS", "title": "Gap 4  |  Speaker notes and provenance",
         "left": {"label": "⑦ SPEAKER NOTES", "name": "Notes are the bullets again",
                  "symptoms": ["speaker notes duplicate the text on the slide",
                               "no time budget — no idea how many slides fit three minutes",
                               "no transitions, so slides do not connect"],
                  "evidence": "Delivery is under-optimised (Yang et al., 2026); only 5 of 38 papers mention speaker notes, none as a research focus.",
                  "consequence": "The speaker reads the slide while the audience reads and listens at once."},
         "right": {"label": "⑧ PROVENANCE", "name": "Writes the words, cannot cite them",
                   "symptoms": ["bullets carry no source, so there is no path back to a passage",
                                "related work is presented as 'we propose'",
                                "figures and tables misnumbered; numbers attached to the wrong claim"],
                   "evidence": "Retrieval improves reliability but per-sentence provenance is not exposed (Xie et al., 2025); global intent is kept while sentence-level anchors are missing (Ozden et al., 2026a).",
                   "consequence": "A wrong number goes unnoticed; in academic settings one misattributed claim destroys credibility."}},
 "s09": {"kicker": "02 · FUNCTIONAL GAPS", "title": "A single failure is amplified downstream",
         "chain": ["Bad input", "Bad content", "Weak story", "Broken layout", "No repair", "No verification"],
         "cap": "Every upstream error is amplified downstream — and cannot be traced back",
         "impacts": [("Audience", "Cannot follow or remember; sees clipped text live", "Attention lost"),
                     ("Speaker", "Will not trust it; cannot answer 'where does this number come from?'", "Trust collapses"),
                     ("Field", "Cannot compare systems, because there is no shared measure", "Progress stalls")],
         "gold": "Measurement now exists (SlideAudit, DECKBench). What is missing is using it as a control signal — and measuring what it buys."},
 "s10": {"kicker": "03 · WHY THIS DIRECTION", "title": "Why this direction and not the others",
         "sub": "Four alternatives were considered seriously; each fails on a specific constraint",
         "cols": ["Direction considered", "Why it is attractive", "Why we are not doing it"],
         "rows": [["Reducing hallucination",
                   "Compelling story; high novelty",
                   "Hallucination is a property of the base model. A student can only wrap RAG around it, which fixes fabrication but not over-claiming or misattribution. Ground truth needs sentence-level human checking: 300 bullets × 2 min."],
                  ["A finer taxonomy",
                   "Clear definition; easy to write",
                   "SlideAudit already published 27 categories over 2,400 slides, built with design experts and trained annotators. A solo project cannot match that."],
                  ["A multi-agent architecture",
                   "Sounds advanced",
                   "Per-module ablation becomes near-impossible, and the first defence question is which agent actually contributes."],
                  ["Cost optimisation",
                   "Easy to quantify",
                   "Cost is the denominator, not the goal. Pure engineering tuning is not a research contribution."]],
         "bottom": "The intersection we chose: mechanically decidable  ×  per-class attributable  ×  feasible for one person."},
 "s11": {"kicker": "03 · WHY THIS DIRECTION", "title": "The eight works this direction builds on",
         "sub": "Each one plays a specific role — none is simply 'related work'",
         "items": [("SlideAudit", "Label space", "six overlapping categories, re-used verbatim"),
                   ("DECKBench", "Contrast", "reference-aware scoring; needs a target deck"),
                   ("PPTArena / PPTPilot", "Baseline ③", "the loop we run as a controlled ablation"),
                   ("ReDeck", "Loop design", "one edit, one observation"),
                   ("PPTAgent", "Baseline ②", "strongest reproducible generator"),
                   ("Paper2Poster", "Evaluation idea", "answer questions using only the artefact"),
                   ("PosterMELD", "Concept source", "print-ready rate → slide-ready rate"),
                   ("SLIDEFORGE", "Representation", "pptx object layer instead of pixels")]},
 "s12": {"kicker": "04 · DIRECTION", "title": "My direction: paper distillation, not lecture notes",
         "sub": "Turn computable layout violations into an in-loop control signal, and measure what it buys",
         "inlabel": "IN SCOPE", "outlabel": "OUT OF SCOPE",
         "in": ["single-column English papers, 8–10 in total",
                "10–12 slides per deck, editable .pptx output",
                "six violation classes, per-class reporting",
                "speaker notes: 2–3 lines per slide plus a time budget",
                "20-participant pairwise human study"],
         "out": ["lecture notes and teaching material",
                 "multi-column or scanned papers",
                 "Chinese / bilingual output",
                 "hallucination measurement",
                 "multi-agent architecture as a selling point"],
         "rq": [("RQ1", "Can layout usability be measured without a reference deck?"),
                ("RQ2", "Does a rule-based verifier beat a VLM judge in the same loop?"),
                ("RQ3", "Which violation classes improve, and which stay flat?"),
                ("RQ4", "What does each improvement cost?"),
                ("RQ5", "Can every bullet carry a resolvable source anchor?")],
         "pm": "After the main line — provenance module (C5): per-bullet source anchor, 100 bullets, about four hours of annotation."},
 "s13": {"kicker": "04 · DIRECTION", "title": "Five contributions, in order of weight",
         "rows": [("C1", "A reference-free, object-level measure of usability", "SRR, deck-ready and per-gate pass rates, computed on the native .pptx — no ground-truth deck required."),
                  ("C2", "Measurement turned into a control signal", "detect → edit → re-render → re-measure; the verifier is isolated as the only variable."),
                  ("C3", "Per-class attribution", "which classes repair well, which do not, and why. This is the paper."),
                  ("C4", "A rerunnable research artefact", "150 annotated slides (40 calibration + 110 test), rulebook, detectors, scripts."),
                  ("C5", "Provenance anchors (secondary)", "every bullet resolves to a passage; reported as coverage and accuracy.")],
         "note": "C1 is the ruler, C2 is the hand, C3 is the finding. C4 makes it reproducible; C5 is cut first if time runs out."},
 "s14": {"kicker": "05 · METHOD", "title": "Operational definition: slide-ready rate",
         "sub": "SRR = slides passing every gate / slides; deck-ready is a separate binary. Both are always reported.",
         "cols": ["Gate", "Rule", "Threshold", "Anchor", "Swept over"],
         "rows": [["G1 Containment", "Every shape box inside the slide; no image cropped", "0 pt", "binary rule", "—"],
                  ["G2 Overlap", "Text–text intersection ÷ area of smaller box", "> 5%", "empirical", "2 / 5 / 10%"],
                  ["G3 Font size", "Body and titles, read from run properties", "18 / 28 pt", "design guidance", "16 / 18 / 20"],
                  ["G4 Contrast", "WCAG 2.2 AA ratio, fill vs background", "4.5:1 (3:1 large)", "published standard", "—"],
                  ["G5 Text fit", "Rendered text height ÷ box height", "≤ 0.95", "renderer tolerance", "0.90 / 1.00"],
                  ["G6 Density", "Characters per slide; bullets per block", "≤ 140; ≤ 6", "empirical", "120 / 160"]],
         "notes": [("Calibration: sweep each threshold, keep the value that maximises agreement with human labels.", GREY),
                   ("Aggregation: SRR is slide-level and continuous; deck-ready = every slide passes (9 of 10 is NOT deck-ready).", RED),
                   ("Positioning: SlideAudit supplies the label space; DECKBench scores against references; SRR is reference-free — a control signal, not a score.", TEAL)]},
 "s15": {"kicker": "05 · METHOD", "title": "Evidence plan: agreement, power, fallbacks",
         "sub": "The grade depends on whether a sceptic can rerun these three numbers",
         "left_t": "DETECTOR VALIDATION",
         "left": ["150 slides = 40 calibration + 110 held-out, stratified across all three systems",
                  "2 independent annotators; rulebook training plus 10 calibration slides",
                  "Cohen's kappa >= 0.70 per class, adjudicated by a third pass",
                  "precision / recall / F1 per class, never an aggregate only",
                  "if per-class F1 < 0.70 on calibration, revise the rule and re-freeze"],
         "right_t": "HUMAN STUDY",
         "right": ["within-subject: 20 raters x 4 papers, all three systems on the same paper",
                   "one primary contrast pre-registered: ours vs the VLM-judge loop",
                   "Holm–Bonferroni across the remaining two comparisons",
                   "n = 20 detects d about 0.65–0.70 at 80% power",
                   "raters blind to condition order; papers rotated"],
         "fb_t": "IF RECRUITMENT FALLS SHORT OF 20",
         "fb": "3 expert raters with ICC(2,k)  ·  expand automated QA from 10 to 25 items  ·  report posterior probability of superiority  ·  label the result exploratory"},
 "s16": {"kicker": "05 · METHOD", "title": "System architecture",
         "sub": "Gold = new contributions; the rest reuses validated practice",
         "stages": [("PDF", "input", 0), ("Parse", "section / figure", 0), ("Evidence graph", "claim–evidence", 1),
                    ("Narrative plan", "space allocation", 1), ("Layout solver", "capacity-aware", 1), ("Render", "python-pptx", 0),
                    ("Inspect", "violation detection", 1), ("Repair", "local rewrite", 1)],
         "principles": [("Restrict the output space", "the model writes structured content only; geometry belongs to the solver"),
                        ("One element at a time", "local rewrites with immediate verification make errors attributable"),
                        ("Every judgement has a number", "no 'looks fine' — only measured violations and ratios")],
         "notesline": "⑨ Speaker notes — 2–3 lines per slide plus a time budget, written into .pptx notes; generated once, outside the control loop.",
         "note": "The output is not an image but an editable .pptx: layout comes from constraint solving, content from the evidence graph."},
"s17r": {"kicker": "05 · METHOD", "title": "What the repair actually does",
         "sub": "One decision procedure per violation class: cheapest action first, with a guardrail that forbids adding content",
         "cols": ["Violation", "What we do, in order", "Guardrail"],
         "rows": [["Text out of bounds / clipped", "shrink font one step → reduce box margin → move the box inward → split the slide", "never below 14 pt"],
                  ["Overlapping text", "move the lower-priority element → resize the box → reflow into two columns", "keep image z-order"],
                  ["Text over a busy background", "add a scrim behind the text → move the text → change the text colour", "contrast must reach 4.5:1"],
                  ["Text too long", "delete words (never add) → split across two slides", "no new claims, no number changes"],
                  ["Too dense", "split one slide into two", "preserve claim order"]],
         "note": "Order matters: the cheapest reversible action is tried first, so the cost of a repair is predictable."},
 "s17": {"kicker": "05 · METHOD", "title": "Three ways to build the loop — and the order we take",
         "sub": "All three are feasible; they differ in cost, risk and how early they produce a number",
         "cols": ["Route", "What it does", "Cost / risk", "When"],
         "rows": [["A  Deterministic repair", "shrink font → move → resize → split slide, no LLM call", "cheapest, fully reproducible; limited reach", "W5–7"],
                  ["B  Detector-conditioned rewrite", "violations become constraints; the LLM rewrites one slide's structured content", "1 call per slide per pass; content drift", "W8–11"],
                  ["C  Hybrid two-loop", "inner loop A + a VLM pass every third iteration", "highest complexity; hardest to debug", "W12–14"]],
         "bottom": "A alone already yields a reportable result. B is added only if A converges; C exists only as the comparison arm."},
 "s18": {"kicker": "05 · METHOD", "title": "How the claims are tested",
         "sub": "Three tracks in parallel, avoiding the circularity of an LLM judging an LLM",
         "cols": ["Track", "Metric", "Sample", "Why it is needed"],
         "rows": [["Automatic (geometry)", "Violation count, SRR, deck-ready", "150 slides (40 + 110)", "deterministic and rerunnable"],
                  ["Task-based (QA)", "answer accuracy from the deck", "10 questions x 8 papers", "can a reader extract correct facts?"],
                  ["Coverage", "key claims that survive into the deck", "5-8 claims per paper", "required by the brief"],
                  ["Human", "pairwise preference, speakability", "20 participants", "design has no ground truth"]],
         "bl_t": "BASELINES — EACH ANSWERS A DIFFERENT QUESTION",
         "bl": [("1", "Naive single-pass", "does inspection add anything at all?"),
                ("2", "PPTAgent", "versus the strongest reproducible generator"),
                ("3", "VLM-judge repair loop", "computable rules versus subjective judgement")],
         "blnote": "3 is the primary claim: same loop, same budget, only the verifier changes.",
         "ab_t": "ABLATION", "ab": "Remove anchors\nRemove inspection\nRemove repair\n→ per-module attribution",
         "abnote": "Report per class,\nincluding where repair fails.",
         "stage_note": "Inspection starts in W5, ahead of the brief's stage 5 - the metric must be validated before the loop that depends on it."},
 "s19": {"kicker": "06 · PLAN", "title": "20-week timeline",
         "sub": "Four parallel workstreams; if recruitment is short, fall back to expert rating plus expanded QA",
         "phases": [("Literature & scope", 0, 2, "W1–2"), ("Setup & spikes", 2, 2, "W3–4"),
                    ("Rulebook & parsing", 4, 3, "W5–7"), ("Layout & rendering", 7, 4, "W8–11"),
                    ("Calibrate & repair", 11, 3, "W12–14"), ("Experiments & study", 14, 4, "W15–18"),
                    ("Report & talk", 18, 2, "W19–20")],
         "ms": [("2026-11-05", "Proposal submission"), ("2027-01-07", "Interim Report"),
                ("2027-04-08", "Final Report + Turnitin + AI Report")]},
 "s20": {"kicker": "APPENDIX · APA 7TH", "title": "References", "refs": None},
},
"zh": {
 "meta": {"font": "PingFang HK", "foot": "DSAI4901  ·  Capstone Project Proposal  ·  CHAN Yee Tung"},
 "s01": {"kicker": "DSAI4901  ·  CAPSTONE PROJECT PROPOSAL",
         "t1": "論文整理型 PPT Agent", "t2": "從生成，到可驗證",
         "desc": "以「可量度的版面可用性」為核心的\n簡報生成系統",
         "who": "CHAN Yee Tung", "sup": "指導老師：Dr. Jibin Wu", "date": "2026 年 10 月",
         "stats": [("38", "篇核心文獻"), ("8", "個功能缺口"), ("1", "條研究路線")]},
 "s02": {"kicker": "01 · 研究基礎", "title": "文獻研究：由 367 篇收窄到 38 篇",
         "bars": [("367", "arXiv 候選", 8.6, "ink"), ("69", "相關度篩選後", 5.6, "ink2"),
                  ("38", "精讀（33 Agent + 5 教育）", 4.4, "teal"), ("18", "作者公開原始碼", 3.6, "gold")],
         "box": "我實際做了什麼",
         "bullets": ["12 組 arXiv 查詢（slide / PPT / poster / deck）",
                     "以功能相關度篩選，排除無關領域",
                     "38 篇全文關鍵詞掃描",
                     "逐篇由 PDF 抽取 GitHub 連結並 HTTP 驗證"],
         "note": "18/38 有作者公開原始碼（已逐一 HTTP 驗證）；其餘為論文描述或匿名投稿"},
 "s03": {"kicker": "01 · 研究基礎", "title": "佢哋做得好嘅四件事",
         "sub": "先確認已解決了什麼——這決定我不應該重做什麼",
         "cards": [("01", "生成品質與版面", "已做到「看起來像真」：版面穩定、風格一致。", "Zheng et al. (2025); Vats et al. (2026)"),
                   ("02", "原生可編輯輸出", "開始在 .pptx 物件層操作，保留可編輯性。", "Jung et al. (2025); Zheng et al. (2026b)"),
                   ("03", "評測方法", "從主觀打分走向任務化測試與 rubric gate。", "Zhang et al. (2025); Jang et al. (2026)"),
                   ("04", "多模態與敘事", "圖表進入版面；開始顯式建模故事線。", "Liang et al. (2025); Ozden et al. (2026a)")],
         "concl": "結論：生成能力已商品化，再做一個生成器不是貢獻。"},
 "s04": {"kicker": "01 · 研究基礎", "title": "把 PPT Agent 拆成 8 個功能",
         "sub": "缺口要講得具體，先要有一張功能地圖——之後四頁逐個對照",
         "funcs": [("①", "解析"), ("②", "內容選取"), ("③", "敘事"), ("④", "版面"), ("⑤", "輸出"), ("⑥", "檢查")],
         "cross": [("⑦", "講稿", "跨階段：把內容轉成可講的節奏"),
                   ("⑧", "引用與可追溯", "跨階段：每一句都要有出處")],
         "note": "接下來四頁：每頁兩個缺口——症狀 · 證據 · 後果"},
 "s05": {"kicker": "02 · 功能缺口", "title": "缺口 1 ｜ 解析與內容選取",
         "left": {"label": "① 解析", "name": "圖文分離，輸入即失真",
                  "symptoms": ["figure 與 caption 被拆散，圖文對不上", "雙欄論文閱讀順序錯亂", "表格被壓成文字牆"],
                  "evidence": "解析被當作前處理，未處理圖文對齊（Pang et al., 2025; Fu et al., 2021）。",
                  "consequence": "錯的輸入被下游全部繼承，而且錯誤在成品上不可見。"},
         "right": {"label": "② 內容選取", "name": "平均分配，沒有輕重",
                   "symptoms": ["每節平均一頁，與重要性無關", "最關鍵結果被省略", "method 細節塞進 introduction"],
                   "evidence": "多數方法集中文字選取，忽略篇幅與重要性的對應（Liang et al., 2025; Chen et al., 2026）。",
                   "consequence": "deck 完整但沒有重點，觀眾只記得標題。"}},
 "s06": {"kicker": "02 · 功能缺口", "title": "缺口 2 ｜ 敘事與版面",
         "left": {"label": "③ 敘事", "name": "目錄式摘要，不是演講",
                  "symptoms": ["逐段摘要＝論文目錄", "十頁 background、兩頁 result", "沒有動機→問題→洞見→證據的弧線"],
                  "evidence": "原文直接摘要成 slide（Ozden et al., 2026a）；顯式敘事規劃仍屬少數（Vats et al., 2026）。",
                  "consequence": "講者朗讀目錄，聽眾建立不到因果理解。"},
         "right": {"label": "④ 版面", "name": "出界、重疊、被裁切",
                   "symptoms": ["文字出界、元素重疊", "字級過小、對比不足", "圖被裁切，每頁都是 bullet 牆"],
                   "evidence": "局部錯誤包括 overflow、overlap、clipping、off-canvas（Tian et al., 2026）；模型讀得懂卻排不好（Huang et al., 2025）。",
                   "consequence": "投影時文字被切、圖被遮，觀眾即時失去信任。"}},
 "s07": {"kicker": "02 · 功能缺口", "title": "缺口 3 ｜ 輸出與檢查",
         "left": {"label": "⑤ 輸出", "name": "看似可用，其實不能改",
                  "symptoms": ["輸出圖片或 HTML，不能在 PowerPoint 內編輯", "全 textbox，改一個字就爆版", "圖表被點陣化，資料消失"],
                  "evidence": "常把可編輯內容點陣化或破壞版面（Zheng et al., 2026b）；物件模型路線才保留樣式（Jung et al., 2025）。",
                  "consequence": "用戶拿到成品但不能改，等於不能用。"},
         "right": {"label": "⑥ 檢查", "name": "一次性回饋，無法歸因",
                   "symptoms": ["整份重寫一次，只看一次回饋", "錯誤無法定位到具體元素", "修完可能更差，無收斂保證"],
                   "evidence": "單體式 one-version-one-feedback 令局部錯誤難以歸因（Tian et al., 2026）；反思須以渲染狀態為依據（Zheng et al., 2026a）。",
                   "consequence": "迭代變成賭博：越修越差，而且無法解釋。"}},
 "s08": {"kicker": "02 · 功能缺口", "title": "缺口 4 ｜ 講稿與引用",
         "left": {"label": "⑦ 講稿", "name": "notes 只是 bullet 的複述",
                  "symptoms": ["notes 與頁面文字高度重複", "沒有時間預算", "沒有轉場句"],
                  "evidence": "現有系統低估交付過程（Yang et al., 2026）；38 篇中僅 5 篇提及 speaker notes，且非研究重點。",
                  "consequence": "講者照讀 slide，觀眾同時讀字與聽字。"},
         "right": {"label": "⑧ 引用與可追溯", "name": "寫得出字，說不出出處",
                   "symptoms": ["bullet 沒有出處", "related work 寫成「本文提出」", "圖表編號錯配、數字張冠李戴"],
                   "evidence": "檢索提升可靠性但未提供逐句出處（Xie et al., 2025）；全局意圖保留，句子級錨點仍缺（Ozden et al., 2026a）。",
                   "consequence": "講錯數據無人察覺；一次錯誤引用足以摧毀可信度。"}},
 "s09": {"kicker": "02 · 功能缺口", "title": "單點失效，會被下游放大",
         "chain": ["輸入錯", "內容錯", "敘事散", "版面爆", "修不好", "無從查證"],
         "cap": "每一個上游錯誤都會在下游被放大，而且無法回溯",
         "impacts": [("觀眾", "看不懂、記不住，當場看到字被切", "注意力流失"),
                     ("講者", "不敢用，答不出「這數字哪來的」", "信任崩塌"),
                     ("研究者", "無法比較系統好壞，因為沒有共同的度量", "領域停滯")],
         "gold": "量度已經存在（SlideAudit、DECKBench）；缺的是把它當作控制訊號，並量度它換來幾多。"},
 "s10": {"kicker": "03 · 為何是這個方向", "title": "為何揀這個方向，唔做其他",
         "sub": "四個替代方向都認真考慮過，各自卡在一個具體限制",
         "cols": ["考慮過的方向", "為何吸引", "為何唔做"],
         "rows": [["減少幻覺", "故事易講、novelty 高",
                   "幻覺係大模型本身的屬性。學生只能在外面加 RAG，而 RAG 對「編造」有效，對「過度概括／張冠李戴」無效。真值要逐句人手核對：300 條 × 2 分鐘。"],
                  ["更細的分類", "定義清楚、容易寫",
                   "SlideAudit 已用設計專家 + 受訓標註做了 27 類、2,400 張。單人不可能比它更細更好。"],
                  ["多智能體架構", "聽起來先進",
                   "逐模組消融幾乎做唔到；評審第一句必問「邊個 agent 真正有用」。"],
                  ["成本優化", "容易量化",
                   "成本係分母，唔係目標。純工程調優唔算研究貢獻。"]],
         "bottom": "我們揀的交集：可機械判定  ×  可逐類歸因  ×  單人做得完。"},
 "s11": {"kicker": "03 · 為何是這個方向", "title": "這個方向建立在這八篇之上",
         "sub": "每一篇都有明確角色，唔係「相關工作」四個字帶過",
         "items": [("SlideAudit", "標籤空間", "借用六個重疊類別，逐字沿用"),
                   ("DECKBench", "對照", "需要參考 deck 的評分；證明我們不同"),
                   ("PPTArena / PPTPilot", "Baseline ③", "同一迴圈的對照臂"),
                   ("ReDeck", "迴圈設計", "一次改一個元素、改完即驗"),
                   ("PPTAgent", "Baseline ②", "最強可複現生成系統"),
                   ("Paper2Poster", "評測靈感", "只用成品答問題"),
                   ("PosterMELD", "概念來源", "PRR → SRR"),
                   ("SLIDEFORGE", "表徵方式", "用 pptx 物件層而非像素")]},
 "s12": {"kicker": "04 · 研究方向", "title": "我的方向：論文整理，不做 lecture notes",
         "sub": "把可計算的版面違規變成迴圈中的控制訊號，並量度它換來幾多",
         "inlabel": "範圍之內", "outlabel": "明確不做",
         "in": ["單欄英文論文，共 8–10 篇", "每份 10–12 版，輸出可編輯 .pptx", "六類違規，逐類報告", "講稿：每頁 2–3 句 + 時間預算", "20 人 pairwise 人評"],
         "out": ["lecture notes／教材", "雙欄或掃描論文", "中文／雙語輸出", "幻覺量度", "以多智能體作賣點"],
         "rq": [("RQ1", "唔需要參考 deck，可以量度版面可用性嗎？"),
                ("RQ2", "同一個迴圈裡，規則驗證器會否勝過 VLM judge？"),
                ("RQ3", "邊類違規改得好，邊類改完都無效？"),
                ("RQ4", "每一點改善要幾多成本？"),
                ("RQ5", "每條 bullet 能否帶可解析的出處？")],
         "pm": "主線之後——provenance 模組（C5）：逐條 bullet 標出處，100 條，約四小時標註。"},
 "s13": {"kicker": "04 · 研究方向", "title": "五個貢獻，按份量排序",
         "rows": [("C1", "一個 reference-free 的物件層可用性量度", "SRR、deck-ready、逐 gate 通過率，全部在原生 .pptx 上計算，不需標準答案。"),
                  ("C2", "把量度變成控制訊號", "detect → edit → re-render → re-measure；只把「驗證器」當變量隔離。"),
                  ("C3", "逐類歸因", "哪類修得好、哪類修唔好、為什麼。這才是論文。"),
                  ("C4", "可重跑的研究資源", "150 版標註（40 校準 + 110 測試）、rulebook、detector、腳本。"),
                  ("C5", "出處錨點（次要）", "每條 bullet 可解析到原文段落；報 coverage 與 accuracy。")],
         "note": "C1 是尺，C2 是手，C3 是結論。C4 令它可被重跑；C5 時間不足時最先砍。"},
 "s14": {"kicker": "05 · 方法", "title": "操作型定義：slide-ready rate",
         "sub": "SRR ＝ 過關 slide 數 ÷ slide 總數；deck-ready 是另一個 binary。兩者永遠一齊報。",
         "cols": ["Gate", "規則", "閾值", "依據", "掃描範圍"],
         "rows": [["G1 出界", "所有 shape 在版面內；圖片不被裁切", "0 pt", "二元規則", "—"],
                  ["G2 重疊", "文字交集 ÷ 較小框面積", "> 5%", "經驗值", "2 / 5 / 10%"],
                  ["G3 字級", "由 run properties 讀取", "18 / 28 pt", "設計慣例", "16 / 18 / 20"],
                  ["G4 對比", "WCAG 2.2 AA，填充對背景", "4.5:1（大字 3:1）", "公開標準", "—"],
                  ["G5 文字溢出", "渲染文字高度 ÷ 框高", "≤ 0.95", "渲染容差", "0.90 / 1.00"],
                  ["G6 密度", "每版字數；每段 bullet 數", "≤ 140；≤ 6", "經驗值", "120 / 160"]],
         "notes": [("校準：逐個閾值掃描，取與人評一致度最高的值，並報整條曲線。", GREY),
                   ("聚合：SRR 是 slide 級連續值；deck-ready 要求全部過關（9/10 唔算 ready）。", RED),
                   ("定位：SlideAudit 提供標籤空間；DECKBench 對參考 deck 評分；SRR 無需參考，係控制訊號而非分數。", TEAL)]},
 "s15": {"kicker": "05 · 方法", "title": "證據計劃：一致性、檢定力、後備方案",
         "sub": "分數取決於懷疑論者能唔能重跑這三個數字",
         "left_t": "DETECTOR 驗證",
         "left": ["150 版 ＝ 40 校準 + 110 測試，跨三個系統分層抽樣",
                  "2 位獨立標註者；規則訓練 + 10 版校準",
                  "每類 Cohen's kappa ≥ 0.70，分歧由第三方裁定",
                  "逐類報 precision / recall / F1，不報總分",
                  "校準 F1 < 0.70 就改規則並重新凍結"],
         "right_t": "人評",
         "right": ["受試者內設計：20 人 × 4 篇，同一篇見三個系統",
                   "預先註冊單一主要對比：我們 vs VLM-judge 迴圈",
                   "其餘兩個對比用 Holm–Bonferroni 校正",
                   "n = 20 可偵測 d ≈ 0.65–0.70（80% 檢定力）",
                   "受試者不知條件次序；論文輪換"],
         "fb_t": "若招募不足 20 人",
         "fb": "3 位專家評分（ICC）  ·  QA 題目由 10 增至 25  ·  報貝氏優越機率  ·  標記為 exploratory"},
 "s16": {"kicker": "05 · 方法", "title": "系統架構",
         "sub": "金色 = 本項目的新貢獻；其餘沿用已被驗證的成熟做法",
         "stages": [("PDF", "輸入", 0), ("解析", "section / figure", 0), ("證據圖", "claim–evidence", 1),
                    ("敘事規劃", "篇幅分配", 1), ("版面求解", "容量感知", 1), ("渲染", "python-pptx", 0),
                    ("檢查", "違規偵測", 1), ("修復", "局部重寫", 1)],
         "principles": [("限制輸出空間", "模型只寫結構化內容，幾何交給求解器"),
                        ("一次只改一個元素", "局部重寫 + 即時驗證，錯誤才可歸因"),
                        ("所有判斷都要有數字", "不用「看起來不錯」，只用可量度的違規與比率")],
         "notesline": "⑨ 講稿 — 每頁 2–3 句 + 時間預算，寫入 .pptx notes；一次生成，不在控制迴圈內。",
         "note": "輸出不是圖片，而是可編輯的 .pptx：版面由約束求解決定，內容由證據圖決定。"},
"s17r": {"kicker": "05 · 方法", "title": "修復到底做啲咩",
         "sub": "每類違規一個決策程序：由最便宜開始，並有護欄禁止新增內容",
         "cols": ["違規類別", "按次序做啲咩", "護欄"],
         "rows": [["文字出界／被切", "縮一級字 → 減內邊距 → 移入框內 → 拆頁", "唔低於 14 pt"],
                  ["文字重疊", "移走優先級低嘅元素 → 改框大小 → 改成兩欄", "保持圖片 z-order"],
                  ["文字壓住背景", "文字後加半透明底 → 移文字 → 改字色", "對比要達 4.5:1"],
                  ["字太長", "刪字（只刪不加）→ 拆去下一頁", "唔准加新內容、唔准改數字"],
                  ["太密", "一版拆兩版", "保持論點次序"]],
         "note": "次序有意義：先做最便宜且可逆的動作，修復成本才可預測。"},
 "s17": {"kicker": "05 · 方法", "title": "三條實作路線，同我哋行嘅次序",
         "sub": "三條都可行；差別在成本、風險，同幾時有第一個數字",
         "cols": ["路線", "做啲咩", "成本／風險", "時間"],
         "rows": [["A 確定性修復", "縮字 → 移位 → 改框 → 拆頁，零 LLM 呼叫", "最便宜、完全可複現；表達力有限", "W5–7"],
                  ["B 違規條件化重寫", "違規轉成約束，LLM 只重寫該版結構化內容", "每版每次 1 次呼叫；內容漂移", "W8–11"],
                  ["C 雙迴圈", "內圈 A，每三次迭代加一次 VLM 檢查", "複雜度最高，最難 debug", "W12–14"]],
         "bottom": "A 單獨已經有可報告結果。B 只在 A 收斂後加入；C 只作為對照臂存在。"},
 "s18": {"kicker": "05 · 方法", "title": "如何證明",
         "sub": "三軌並行，避免「用 LLM 評 LLM」的循環論證",
         "cols": ["軌道", "指標", "樣本", "為何需要"],
         "rows": [["自動（幾何）", "違規數、SRR、deck-ready", "150 版（40 + 110）", "確定性、可重跑"],
                  ["任務式（問答）", "由成品作答的正確率", "10 題 × 8 篇", "讀者能否取得正確資訊"],
                  ["覆蓋率", "論文重點有多少留在 deck 裡", "每篇 5–8 個 claim", "brief 明確要求"],
                  ["人評", "pairwise 偏好、可講性", "20 人", "設計沒有標準答案"]],
         "bl_t": "BASELINES —— 各自回答不同問題",
         "bl": [("1", "Naive single-pass", "檢查到底有冇用？"),
                ("2", "PPTAgent", "對比最強可複現生成器"),
                ("3", "VLM-judge 修復迴圈", "可計算規則 vs 主觀判斷")],
         "blnote": "3 是主要主張：同一個迴圈、同一個預算，只換驗證器。",
         "ab_t": "消融", "ab": "去錨點\n去檢查\n去修復\n→ 逐模組歸因",
         "abnote": "逐類報告，\n包括修復無效的類別。",
         "stage_note": "檢查提前到 W5（brief 的第 5 階段）——指標要先驗證，迴圈才建得穩。"},
 "s19": {"kicker": "06 · 計劃", "title": "20 週時間表",
         "sub": "四條並行工作流；若招募不足，改用專家評分 + 擴大 QA",
         "phases": [("文獻與範圍", 0, 2, "W1–2"), ("環境與 spike", 2, 2, "W3–4"),
                    ("Rulebook 與解析", 4, 3, "W5–7"), ("版面與渲染", 7, 4, "W8–11"),
                    ("校準與修復", 11, 3, "W12–14"), ("實驗與人評", 14, 4, "W15–18"),
                    ("報告與簡報", 18, 2, "W19–20")],
         "ms": [("2026-11-05", "Proposal 提交"), ("2027-01-07", "Interim Report"),
                ("2027-04-08", "Final + Turnitin + AI Report")]},
 "s20": {"kicker": "附錄 · APA 7TH", "title": "引用文獻", "refs": None},
},
}

REFS = [
 "Chen, H., Zhou, X., Zhou, W., Shao, X., Zhu, Y., Wang, B., Hong, J., Jia, A., & Wu, F. (2026). X+Slides: Benchmarking audience-conditioned slide generation (arXiv:2606.19256). arXiv. https://doi.org/10.48550/arXiv.2606.19256",
 "Fu, T.-J., Wang, W. Y., McDuff, D., & Song, Y. (2021). DOC2PPT: Automatic presentation slides generation from scientific documents (arXiv:2101.11796). arXiv. https://doi.org/10.48550/arXiv.2101.11796",
 "Ge, J., Wang, Z. Z., Zhou, X., Peng, Y.-H., Subramanian, S., Tan, Q., Sap, M., Suhr, A., Fried, D., Neubig, G., & Darrell, T. (2025). AutoPresent: Designing structured visuals from scratch (arXiv:2501.00912). arXiv. https://doi.org/10.48550/arXiv.2501.00912",
 "Hu, H., Dang, C., Liu, Y., Kang, H., He, C., & Li, W. (2026). PosterMELD: Multi-agent paper-to-poster generation for controllable design diversity with editable print-ready outputs (arXiv:2608.02218). arXiv. https://doi.org/10.48550/arXiv.2608.02218",
 "Huang, Z., Liu, X., Hu, T., Zhang, K., & Liu, Y. (2025). PPTBench: Towards holistic evaluation of large language models for PowerPoint layout and design understanding (arXiv:2512.02624). arXiv. https://doi.org/10.48550/arXiv.2512.02624",
 "Jang, D., Heisler, M. L., Xing, L., Li, Y., Wang, E., Xiong, Y., Zhang, Y., & Fan, Z. (2026). DECKBench: Benchmarking multi-agent frameworks for academic slide generation and editing (arXiv:2602.13318). arXiv. https://doi.org/10.48550/arXiv.2602.13318",
 "Jung, K., Cho, H., Yun, J., Yang, S., Jang, J., & Choo, J. (2025). Talk to your slides: High-efficiency slide editing via language-driven structured data manipulation (arXiv:2505.11604). arXiv. https://doi.org/10.48550/arXiv.2505.11604",
 "Liang, X., Zhang, Z., Zhang, X., Su, H., Xu, Y., Sun, S., & You, C. (2025). SlideGen: Collaborative multimodal agents for scientific slide generation (arXiv:2512.04529). arXiv. https://doi.org/10.48550/arXiv.2512.04529",
 "Ofengenden, M., Man, Y., Pang, Z., Gui, L.-Y., & Wang, Y.-X. (2025). PPTArena: A benchmark for PowerPoint editing (arXiv:2512.03042). arXiv. https://doi.org/10.48550/arXiv.2512.03042",
 "Ozden, T. C., VS, S., Horoz, F., Kara, O., Kim, J., & Rehg, J. M. (2026a). Narrative-driven paper-to-slide generation via ArcDeck (arXiv:2604.11969). arXiv. https://doi.org/10.48550/arXiv.2604.11969",
 "Ozden, T. C., VS, S., Horoz, F., Kara, O., Hakkani-Tür, D., Kim, J., & Rehg, J. M. (2026b). ConvDeck: Conversational paper-to-slide generation via stage-specific user feedback (arXiv:2609.00226). arXiv. https://doi.org/10.48550/arXiv.2609.00226",
 "Pang, W., Lin, K. Q., Jian, X., He, X., & Torr, P. (2025). Paper2Poster: Towards multimodal poster automation from scientific papers (arXiv:2505.21497). arXiv. https://doi.org/10.48550/arXiv.2505.21497",
 "Sun, E., Hou, Y., Wang, D., Zhang, Y., & Wang, N. X. R. (2021). D2S: Document-to-slide generation via query-based text summarization (arXiv:2105.03664). arXiv. https://doi.org/10.48550/arXiv.2105.03664",
 "Tian, M., Zeng, Z., Yang, Y., Gao, X., Li, Y., Huang, Z., Wang, X., Lv, C., Cheng, M., Liu, B., Qiu, K., Dai, Q., Chen, D., Dong, Y., Zheng, X., Li, J., & Luo, C. (2026). ReDeck: Step-level render-grounded refinement for document-to-slide generation (arXiv:2609.00194). arXiv. https://doi.org/10.48550/arXiv.2609.00194",
 "Vats, V., Sharma, K., & Wang, Y. (2026). SlideLab: Audience-centered scientific slide generation and evaluation (arXiv:2609.30294). arXiv. https://doi.org/10.48550/arXiv.2609.30294",
 "Xie, E., Waterfield, D., Kennedy, M., & Zhang, A. (2025). SlideBot: A multi-agent framework for generating informative, reliable, multi-modal presentations (arXiv:2511.09804). arXiv. https://doi.org/10.48550/arXiv.2511.09804",
 "Yang, M., Zhang, Z., Li, J., Liu, H., Cai, Y., & Zheng, W. (2026). DeepSlide: From artifacts to presentation delivery (arXiv:2605.15202). arXiv. https://doi.org/10.48550/arXiv.2605.15202",
 "Zhang, Z. J., Chen, R., Zhong, M., & Wobbrock, J. O. (2025). SlideAudit: A dataset and taxonomy for automated evaluation of presentation slides (arXiv:2508.03630). arXiv. https://doi.org/10.48550/arXiv.2508.03630",
 "Zheng, H., Guan, X., Kong, H., Zheng, J., Zhou, W., Lin, H., Lu, Y., He, B., Han, X., & Sun, L. (2025). PPTAgent: Generating and evaluating presentations beyond text-to-slides (arXiv:2501.03936). arXiv. https://doi.org/10.48550/arXiv.2501.03936",
 "Zheng, H., Mo, G., Yan, X., Yuan, Q., Zhang, W., Chen, X., Lu, Y., Lin, H., Han, X., & Sun, L. (2026a). DeepPresenter: Environment-grounded reflection for agentic presentation generation (arXiv:2602.22839). arXiv. https://doi.org/10.48550/arXiv.2602.22839",
 "Zheng, H., Wang, F., Xiong, T., Yu, Y., Qian, S., Yu, H., Schwing, A., Nahrstedt, K., & Wu, M. (2026b). SLIDEFORGE: An LLM agent for controllable editing of slides as structured artifacts (arXiv:2609.03109). arXiv. https://doi.org/10.48550/arXiv.2609.03109",
]

# ============================ SLIDE BUILDERS ============================
def build(lang):
    global FONT
    L = C[lang]
    FONT = L["meta"]["font"]
    prs = Presentation()
    prs.slide_width = Inches(W); prs.slide_height = Inches(H)
    BLANK = prs.slide_layouts[6]
    ns = lambda: prs.slides.add_slide(BLANK)

    # ---- 01 title
    s = ns(); m = L["s01"]
    rrect(s, 0, 0, 0.28, H, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    rrect(s, 0.28, 0, 0.06, H, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
    tf = tbox(s, 1.0, 1.30, 8.0, 0.3); add(tf, m["kicker"], size=9.5, bold=True, color=GOLD, first=True)
    tf = tbox(s, 1.0, 1.78, 8.4, 1.7)
    add(tf, m["t1"], size=37, bold=True, color=INK, line=1.05, first=True)
    add(tf, m["t2"], size=23, color=TEAL, space_before=12)
    rrect(s, 1.0, 4.02, 1.5, 0.045, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
    tf = tbox(s, 1.0, 4.26, 7.7, 0.8); add(tf, m["desc"], size=12.5, color=GREY, line=1.4, first=True)
    tf = tbox(s, 1.0, 5.55, 5.5, 1.2)
    add(tf, m["who"], size=13, bold=True, color=INK, first=True)
    add(tf, m["sup"], size=10.5, color=GREY, space_before=3)
    add(tf, m["date"], size=10.5, color=GREY, space_before=1)
    for i, (num, lab) in enumerate(m["stats"]):
        y = 1.95 + i * 1.62
        tf = tbox(s, 9.75, y, 2.6, 0.8); add(tf, num, size=44, bold=True, color=GOLD, line=0.95, first=True)
        tf = tbox(s, 9.75, y + 0.70, 2.6, 0.3); add(tf, lab, size=10, color=GREY, first=True)
        if i < 2:
            ln = s.shapes.add_connector(1, Inches(9.75), Inches(y + 1.40), Inches(12.3), Inches(y + 1.40))
            ln.line.color.rgb = RGBColor(0xE4, 0xE8, 0xEC); ln.line.width = Pt(0.75)
    footer(s, 1, L)

    # ---- 02 literature
    s = ns(); m = L["s02"]
    header(s, m["kicker"], m["title"])
    colmap = {"ink": INK, "ink2": INK2, "teal": TEAL, "gold": GOLD}
    for i, (num, lab, wbar, col) in enumerate(m["bars"]):
        y = 2.10 + i * 0.98
        rrect(s, 0.85, y, wbar, 0.74, fill=colmap[col] if col == "gold" else PANEL)
        tf = tbox(s, 1.07, y + 0.13, 1.0, 0.5)
        add(tf, num, size=21, bold=True, color=WHITE if col == "gold" else INK, first=True)
        tf = tbox(s, 2.10, y + 0.20, wbar - 1.35, 0.36)
        add(tf, lab, size=10.2, color=WHITE if col == "gold" else GREY, first=True)
    rrect(s, 9.35, 2.10, 3.1, 3.35, fill=PANEL2)
    tf = tbox(s, 9.60, 2.26, 2.62, 0.3); add(tf, m["box"], size=9, bold=True, color=GOLD, first=True)
    tf = tbox(s, 9.60, 2.58, 2.62, 2.75); bullets(tf, m["bullets"], size=8.8, gap=7, line=1.25)
    tf = tbox(s, 0.85, 6.25, 8.3, 0.4); add(tf, m["note"], size=8.8, color=LGREY, first=True)
    footer(s, 2, L)

    # ---- 03 strengths
    s = ns(); m = L["s03"]
    header(s, m["kicker"], m["title"], m["sub"])
    cw, gap = 2.86, 0.22
    for i, (num, t, body, cite) in enumerate(m["cards"]):
        x = 0.85 + i * (cw + gap)
        rrect(s, x, 2.15, cw, 3.02, fill=PANEL)
        rrect(s, x, 2.15, cw, 0.05, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
        tf = tbox(s, x + 0.24, 2.36, cw - 0.4, 0.35); add(tf, num, size=10.5, bold=True, color=GOLD, first=True)
        tf = tbox(s, x + 0.24, 2.68, cw - 0.42, 0.72); add(tf, t, size=13, bold=True, color=INK, line=1.15, first=True)
        tf = tbox(s, x + 0.24, 3.44, cw - 0.42, 2.3); add(tf, body, size=9.6, color=INK2, line=1.32, first=True)
        tf = tbox(s, x + 0.24, 4.20, cw - 0.42, 0.8); add(tf, cite, size=7.5, color=TEAL, line=1.2, first=True)
    tf = tbox(s, 0.85, 5.62, 11.6, 0.5); add(tf, m["concl"], size=12, bold=True, color=RED, first=True)
    footer(s, 3, L)

    # ---- 04 function map
    s = ns(); m = L["s04"]
    header(s, m["kicker"], m["title"], m["sub"])
    bw, bh, bgap = 1.62, 1.30, 0.30
    for i, (num, name) in enumerate(m["funcs"]):
        x = 0.85 + i * (bw + bgap)
        rrect(s, x, 2.30, bw, bh, fill=PANEL2, line=RGBColor(0xD8, 0xE0, 0xE8))
        tf = tbox(s, x, 2.46, bw, 0.32); add(tf, num, size=12.5, bold=True, color=GOLD, align=PP_ALIGN.CENTER, first=True)
        tf = tbox(s, x, 2.86, bw, 0.40); add(tf, name, size=12, bold=True, color=INK, align=PP_ALIGN.CENTER, first=True)
        if i < 5:
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw + 0.05), Inches(2.83), Inches(0.20), Inches(0.24))
            ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
            ar.line.fill.background(); ar.shadow.inherit = False
            st = ar._element.find(qn('p:style'))
            if st is not None:
                ar._element.remove(st)
    for i, (num, name, desc) in enumerate(m["cross"]):
        y = 4.15 + i * 1.05
        rrect(s, 0.85, y, 11.6, 0.86, fill=GOLDBG)
        tf = tbox(s, 1.10, y + 0.10, 0.5, 0.6); add(tf, num, size=14, bold=True, color=GOLD, first=True)
        tf = tbox(s, 1.62, y + 0.11, 2.6, 0.6); add(tf, name, size=12, bold=True, color=INK, first=True)
        tf = tbox(s, 4.35, y + 0.20, 7.8, 0.5); add(tf, desc, size=10, color=GREY, first=True)
    tf = tbox(s, 0.85, 6.55, 11.6, 0.35); add(tf, m["note"], size=10, color=LGREY, first=True)
    footer(s, 4, L)

    # ---- 05..08 gaps
    def gap_slide(page, m):
        s = ns()
        header(s, m["kicker"], m["title"])
        for idx, d in enumerate([m["left"], m["right"]]):
            x = 0.85 + idx * 6.02; wc = 5.72
            rrect(s, x, 1.72, wc, 4.95, fill=WHITE, line=RGBColor(0xDF, 0xE5, 0xEB), lw=0.9)
            rrect(s, x, 1.72, wc, 0.055, fill=RED, shape=MSO_SHAPE.RECTANGLE)
            tf = tbox(s, x + 0.28, 1.92, wc - 0.5, 0.36); add(tf, d["label"], size=9, bold=True, color=RED, first=True)
            tf = tbox(s, x + 0.28, 2.20, wc - 0.5, 0.45); add(tf, d["name"], size=15, bold=True, color=INK, first=True)
            tf = tbox(s, x + 0.28, 2.76, wc - 0.5, 0.22)
            add(tf, m["sym"], size=8, bold=True, color=LGREY, first=True)
            tf = tbox(s, x + 0.28, 2.97, wc - 0.5, 1.22)
            bullets(tf, d["symptoms"], size=8.8, gap=2.5, line=1.16, mark="▪", mark_color=RED)
            tf = tbox(s, x + 0.28, 4.20, wc - 0.5, 0.22)
            add(tf, m["evi"], size=8, bold=True, color=LGREY, first=True)
            tf = tbox(s, x + 0.28, 4.41, wc - 0.5, 0.70); add(tf, d["evidence"], size=8.5, color=TEAL, line=1.22, first=True)
            rrect(s, x + 0.20, 5.18, wc - 0.40, 1.12, fill=REDBG)
            tf = tbox(s, x + 0.36, 5.27, wc - 0.70, 0.2)
            add(tf, m["con"], size=8, bold=True, color=RED, first=True)
            tf = tbox(s, x + 0.36, 5.47, wc - 0.70, 0.76); add(tf, d["consequence"], size=9, color=INK, line=1.2, first=True)
        footer(s, page, L)

    GAPHEADS = {
        "en": {"sym": "SYMPTOMS", "evi": "EVIDENCE · APA", "con": "CONSEQUENCE"},
        "zh": {"sym": "症狀", "evi": "文獻證據 · APA", "con": "後果"},
    }[lang]
    for page, key in [(5, "s05"), (6, "s06"), (7, "s07"), (8, "s08")]:
        m = dict(L[key]); m.update(GAPHEADS)
        gap_slide(page, m)

    # ---- 09 consequence chain
    s = ns(); m = L["s09"]
    header(s, m["kicker"], m["title"])
    cw2, ch2, gp = 1.72, 0.72, 0.26
    for i, t in enumerate(m["chain"]):
        x = 0.85 + i * (cw2 + gp)
        rrect(s, x, 1.85, cw2, ch2, fill=INK if i < 5 else RED)
        tf = tbox(s, x, 2.05, cw2, 0.4); add(tf, t, size=9.8, bold=True, color=WHITE, align=PP_ALIGN.CENTER, first=True)
        if i < 5:
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + cw2 + 0.04), Inches(2.12), Inches(0.18), Inches(0.18))
            ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
            ar.line.fill.background(); ar.shadow.inherit = False
            st = ar._element.find(qn('p:style'))
            if st is not None:
                ar._element.remove(st)
    tf = tbox(s, 0.85, 2.72, 11.6, 0.3); add(tf, m["cap"], size=9.8, color=LGREY, first=True)
    for i, (who, what, tag) in enumerate(m["impacts"]):
        x = 0.85 + i * 3.92
        rrect(s, x, 3.30, 3.66, 1.62, fill=PANEL)
        tf = tbox(s, x + 0.26, 3.45, 3.15, 0.3); add(tf, who, size=11, bold=True, color=GOLD, first=True)
        tf = tbox(s, x + 0.26, 3.76, 3.15, 0.85); add(tf, what, size=9.2, color=INK2, line=1.3, first=True)
        tf = tbox(s, x + 0.26, 4.56, 3.15, 0.3); add(tf, "→ " + tag, size=9, bold=True, color=RED, first=True)
    rrect(s, 0.85, 5.38, 11.6, 1.04, fill=GOLDBG)
    tf = tbox(s, 1.15, 5.50, 11.0, 0.85); add(tf, m["gold"], size=12.5, bold=True, color=INK, line=1.25, first=True)
    footer(s, 9, L)

    # ---- 10 why this direction
    s = ns(); m = L["s10"]
    header(s, m["kicker"], m["title"], m["sub"])
    cols = [2.55, 3.05, 5.95]; rh = 0.92
    rrect(s, 0.85, 2.02, sum(cols), 0.40, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = 0.85
    for i, h in enumerate(m["cols"]):
        tf = tbox(s, cx + 0.14, 2.10, cols[i] - 0.22, 0.3); add(tf, h, size=8.6, bold=True, color=WHITE, first=True)
        cx += cols[i]
    for r, row in enumerate(m["rows"]):
        y = 2.42 + r * rh
        rrect(s, 0.85, y, sum(cols), rh, fill=PANEL if r % 2 == 0 else WHITE,
              line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
        cx = 0.85
        for i, cell in enumerate(row):
            tf = tbox(s, cx + 0.14, y + 0.06, cols[i] - 0.24, rh - 0.12, anchor=MSO_ANCHOR.MIDDLE)
            add(tf, cell, size=8.2 if i == 2 else 8.8, bold=(i == 0),
                color=INK if i == 0 else (GREY if i == 1 else INK2), line=1.22, first=True)
            cx += cols[i]
    tf = tbox(s, 0.85, 6.22, 11.6, 0.4); add(tf, m["bottom"], size=11, bold=True, color=RED, first=True)
    footer(s, 10, L)

    # ---- 11 works we build on
    s = ns(); m = L["s11"]
    header(s, m["kicker"], m["title"], m["sub"])
    for i, (name, role, take) in enumerate(m["items"]):
        col = i % 2; row = i // 2
        x = 0.85 + col * 5.95
        y = 2.02 + row * 1.05
        rrect(s, x, y, 5.55, 0.88, fill=PANEL if row % 2 == 0 else PANEL2)
        rrect(s, x, y, 0.05, 0.88, fill=GOLD, shape=MSO_SHAPE.RECTANGLE)
        tf = tbox(s, x + 0.22, y + 0.10, 2.5, 0.3); add(tf, name, size=10.5, bold=True, color=INK, first=True)
        tf = tbox(s, x + 0.22, y + 0.40, 2.5, 0.3); add(tf, role, size=8, bold=True, color=TEAL, first=True)
        tf = tbox(s, x + 2.85, y + 0.24, 2.55, 0.7); add(tf, take, size=8.2, color=GREY, line=1.2, first=True)
    footer(s, 11, L)

    # ---- 12 direction
    s = ns(); m = L["s12"]
    header(s, m["kicker"], m["title"], m["sub"])
    rrect(s, 0.85, 2.02, 5.55, 1.70, fill=PANEL2)
    tf = tbox(s, 1.08, 2.14, 5.1, 0.26); add(tf, m["inlabel"], size=8.4, bold=True, color=TEAL, first=True)
    tf = tbox(s, 1.08, 2.42, 5.1, 1.55); bullets(tf, m["in"], size=8.8, gap=4, line=1.2, mark_color=TEAL)
    rrect(s, 0.85, 3.84, 5.55, 2.14, fill=PANEL)
    tf = tbox(s, 1.08, 3.96, 5.1, 0.26); add(tf, m["outlabel"], size=8.4, bold=True, color=RED, first=True)
    tf = tbox(s, 1.08, 4.24, 5.1, 1.62); bullets(tf, m["out"], size=8.8, gap=4, line=1.2, mark_color=RED)
    rrect(s, 6.72, 2.02, 5.76, 3.06, fill=WHITE, line=RGBColor(0xDF, 0xE5, 0xEB), lw=0.8)
    for i, (k, q) in enumerate(m["rq"]):
        y = 2.18 + i * 0.54
        tf = tbox(s, 6.92, y, 0.55, 0.3); add(tf, k, size=9, bold=True, color=RED, first=True)
        tf = tbox(s, 7.42, y - 0.02, 4.9, 0.5); add(tf, q, size=8.6, color=INK2, line=1.18, first=True)
    rrect(s, 6.72, 5.22, 5.76, 0.86, fill=GOLDBG)
    tf = tbox(s, 6.92, 5.32, 5.4, 0.70); add(tf, m["pm"], size=8.4, color=INK, line=1.2, first=True)
    footer(s, 12, L)

    # ---- 13 contributions
    s = ns(); m = L["s13"]
    header(s, m["kicker"], m["title"])
    for i, (num, t, body) in enumerate(m["rows"]):
        y = 1.78 + i * 0.90
        rrect(s, 0.85, y, 11.6, 0.80, fill=PANEL if i % 2 == 0 else WHITE,
              line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.6)
        tf = tbox(s, 1.08, y + 0.20, 0.7, 0.4); add(tf, num, size=13, bold=True, color=GOLD, first=True)
        tf = tbox(s, 1.75, y + 0.10, 3.9, 0.6); add(tf, t, size=10, bold=True, color=INK, line=1.15, first=True)
        tf = tbox(s, 5.75, y + 0.12, 6.4, 0.58); add(tf, body, size=8.4, color=INK2, line=1.2, first=True)
    tf = tbox(s, 0.85, 6.42, 11.6, 0.35); add(tf, m["note"], size=9, color=GREY, first=True)
    footer(s, 13, L)

    # ---- 14 SRR
    s = ns(); m = L["s14"]
    header(s, m["kicker"], m["title"], m["sub"])
    cols = [1.58, 4.55, 1.72, 2.12, 1.58]
    rrect(s, 0.85, 2.02, sum(cols), 0.40, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = 0.85
    for i, h in enumerate(m["cols"]):
        tf = tbox(s, cx + 0.12, 2.10, cols[i] - 0.2, 0.3); add(tf, h, size=8.4, bold=True, color=WHITE, first=True)
        cx += cols[i]
    for r, row in enumerate(m["rows"]):
        y = 2.44 + r * 0.60
        rrect(s, 0.85, y, sum(cols), 0.60, fill=PANEL if r % 2 == 0 else WHITE,
              line=RGBColor(0xE4, 0xEA, 0xF0), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
        cx = 0.85
        for i, cell in enumerate(row):
            tf = tbox(s, cx + 0.12, y + 0.09, cols[i] - 0.22, 0.44)
            add(tf, cell, size=8.2, bold=(i == 0), color=INK if i < 3 else GREY, line=1.15, first=True)
            cx += cols[i]
    tf = tbox(s, 0.85, 6.14, 11.6, 0.66)
    for i, (txt, col) in enumerate(m["notes"]):
        add(tf, txt, size=7.8, color=col, first=(i == 0), space_before=0 if i == 0 else 2)
    footer(s, 14, L)

    # ---- 15 evidence plan
    s = ns(); m = L["s15"]
    header(s, m["kicker"], m["title"], m["sub"])
    rrect(s, 0.85, 1.98, 5.55, 2.95, fill=PANEL)
    tf = tbox(s, 1.08, 2.12, 5.1, 0.28); add(tf, m["left_t"], size=8.4, bold=True, color=GOLD, first=True)
    tf = tbox(s, 1.08, 2.42, 5.1, 2.35); bullets(tf, m["left"], size=8.6, gap=6, line=1.22)
    rrect(s, 6.78, 1.98, 5.70, 2.95, fill=PANEL)
    tf = tbox(s, 7.01, 2.12, 5.2, 0.28); add(tf, m["right_t"], size=8.4, bold=True, color=GOLD, first=True)
    tf = tbox(s, 7.01, 2.42, 5.2, 2.35); bullets(tf, m["right"], size=8.6, gap=6, line=1.22)
    rrect(s, 0.85, 5.12, 11.63, 1.02, fill=REDBG)
    tf = tbox(s, 1.08, 5.22, 11.1, 0.24); add(tf, m["fb_t"], size=8.4, bold=True, color=RED, first=True)
    tf = tbox(s, 1.08, 5.48, 11.1, 0.55); add(tf, m["fb"], size=8.4, color=INK2, line=1.3, first=True)
    footer(s, 15, L)

    # ---- 16 architecture
    s = ns(); m = L["s16"]
    header(s, m["kicker"], m["title"], m["sub"])
    bw2, gp2 = 1.36, 0.15
    for i, (name, desc, new) in enumerate(m["stages"]):
        x = 0.85 + i * (bw2 + gp2)
        rrect(s, x, 2.02, bw2, 1.30, fill=GOLDBG if new else PANEL2,
              line=GOLD if new else RGBColor(0xD8, 0xE0, 0xE8), lw=1.2 if new else 0.8)
        tf = tbox(s, x + 0.06, 2.16, bw2 - 0.12, 0.5)
        add(tf, name, size=10, bold=True, color=INK, align=PP_ALIGN.CENTER, line=1.1, first=True)
        tf = tbox(s, x + 0.06, 2.72, bw2 - 0.12, 0.5)
        add(tf, desc, size=7, color=GREY, align=PP_ALIGN.CENTER, line=1.15, first=True)
        if i < len(m["stages"]) - 1:
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw2 + 0.015), Inches(2.57), Inches(0.12), Inches(0.20))
            ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0xC5, 0xCF, 0xD9)
            ar.line.fill.background(); ar.shadow.inherit = False
            st = ar._element.find(qn('p:style'))
            if st is not None:
                ar._element.remove(st)
    rrect(s, 0.85, 3.44, 11.6, 0.34, fill=GOLDBG, line=GOLD, lw=0.8)
    tf = tbox(s, 1.02, 3.50, 11.2, 0.24)
    add(tf, m["notesline"], size=8.2, color=INK, first=True)

    for i, (t, d) in enumerate(m["principles"]):
        x = 0.85 + i * 3.92
        rrect(s, x, 3.88, 3.66, 1.10, fill=WHITE, line=RGBColor(0xDF, 0xE5, 0xEB), lw=0.8)
        tf = tbox(s, x + 0.26, 4.02, 3.1, 0.34); add(tf, t, size=10.5, bold=True, color=INK, first=True)
        tf = tbox(s, x + 0.26, 4.36, 3.1, 0.55); add(tf, d, size=8.8, color=GREY, line=1.25, first=True)
    tf = tbox(s, 0.85, 5.35, 11.6, 0.7); add(tf, m["note"], size=10.5, color=INK2, first=True)
    footer(s, 16, L)

    # ---- 17 repair playbook
    s = ns(); m = L["s17r"]
    header(s, m["kicker"], m["title"], m["sub"])
    cols = [2.55, 6.35, 2.70]
    rrect(s, 0.85, 2.02, sum(cols), 0.40, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = 0.85
    for i, h in enumerate(m["cols"]):
        tf = tbox(s, cx + 0.14, 2.10, cols[i] - 0.2, 0.3)
        add(tf, h, size=8.6, bold=True, color=WHITE, first=True)
        cx += cols[i]
    for r, row in enumerate(m["rows"]):
        y = 2.42 + r * 0.82
        rrect(s, 0.85, y, sum(cols), 0.78, fill=PANEL if r % 2 == 0 else WHITE,
              line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
        cx = 0.85
        for i, cell in enumerate(row):
            tf = tbox(s, cx + 0.14, y + 0.08, cols[i] - 0.24, 0.62, anchor=MSO_ANCHOR.MIDDLE)
            add(tf, cell, size=8.8 if i == 0 else 8.5, bold=(i == 0),
                color=INK if i == 0 else (INK2 if i == 1 else RED), line=1.22, first=True)
            cx += cols[i]
    tf = tbox(s, 0.85, 6.62, 11.6, 0.35)
    add(tf, m["note"], size=9, color=GREY, first=True)
    footer(s, 17, L)

    # ---- 17 three routes
    s = ns(); m = L["s17"]
    header(s, m["kicker"], m["title"], m["sub"])
    cols = [2.55, 4.55, 3.10, 1.20]
    rrect(s, 0.85, 2.02, sum(cols), 0.40, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = 0.85
    for i, h in enumerate(m["cols"]):
        tf = tbox(s, cx + 0.14, 2.10, cols[i] - 0.2, 0.3); add(tf, h, size=8.4, bold=True, color=WHITE, first=True)
        cx += cols[i]
    for r, row in enumerate(m["rows"]):
        y = 2.42 + r * 0.98
        rrect(s, 0.85, y, sum(cols), 0.86, fill=PANEL if r % 2 == 0 else WHITE,
              line=RGBColor(0xE2, 0xE8, 0xEE), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
        cx = 0.85
        for i, cell in enumerate(row):
            tf = tbox(s, cx + 0.14, y + 0.10, cols[i] - 0.24, 0.66, anchor=MSO_ANCHOR.MIDDLE)
            add(tf, cell, size=9.4 if i == 0 else 8.6, bold=(i == 0),
                color=INK if i == 0 else (INK2 if i == 1 else GREY), line=1.25, first=True)
            cx += cols[i]
    tf = tbox(s, 0.85, 5.62, 11.6, 0.4); add(tf, m["bottom"], size=9.6, bold=True, color=RED, first=True)
    footer(s, 18, L)

    # ---- 18 evaluation
    s = ns(); m = L["s18"]
    header(s, m["kicker"], m["title"], m["sub"])
    cols = [2.55, 3.15, 2.75, 3.10]
    rrect(s, 0.85, 2.02, sum(cols), 0.40, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    cx = 0.85
    for i, h in enumerate(m["cols"]):
        tf = tbox(s, cx + 0.12, 2.10, cols[i] - 0.2, 0.3); add(tf, h, size=8.4, bold=True, color=WHITE, first=True)
        cx += cols[i]
    for r, row in enumerate(m["rows"]):
        y = 2.44 + r * 0.54
        rrect(s, 0.85, y, sum(cols), 0.54, fill=PANEL if r % 2 == 0 else WHITE,
              line=RGBColor(0xE4, 0xEA, 0xF0), lw=0.6, shape=MSO_SHAPE.RECTANGLE)
        cx = 0.85
        for i, cell in enumerate(row):
            tf = tbox(s, cx + 0.12, y + 0.06, cols[i] - 0.22, 0.42)
            add(tf, cell, size=8.2, bold=(i == 0), color=INK if i < 3 else GREY, line=1.15, first=True)
            cx += cols[i]
    rrect(s, 0.85, 4.72, 8.30, 1.62, fill=PANEL2)
    tf = tbox(s, 1.08, 4.82, 7.8, 0.24); add(tf, m["bl_t"], size=8.2, bold=True, color=GOLD, first=True)
    for i, (n, nm, q) in enumerate(m["bl"]):
        yy = 5.08 + i * 0.34
        tf = tbox(s, 1.08, yy, 0.3, 0.3); add(tf, n, size=8.6, bold=True, color=RED, first=True)
        tf = tbox(s, 1.38, yy, 2.25, 0.3); add(tf, nm, size=8.4, bold=True, color=INK, first=True)
        tf = tbox(s, 3.62, yy, 5.3, 0.3); add(tf, q, size=8.2, color=GREY, first=True)
    tf = tbox(s, 1.08, 6.10, 7.9, 0.24); add(tf, m["blnote"], size=8, bold=True, color=RED, first=True)
    rrect(s, 9.35, 4.72, 3.13, 1.62, fill=PANEL2)
    tf = tbox(s, 9.56, 4.82, 2.8, 0.24); add(tf, m["ab_t"], size=8.2, bold=True, color=GOLD, first=True)
    tf = tbox(s, 9.56, 5.08, 2.75, 1.0); add(tf, m["ab"], size=8.2, color=INK2, line=1.3, first=True)
    tf = tbox(s, 9.56, 6.06, 2.8, 0.3); add(tf, m["abnote"], size=7.4, color=RED, line=1.15, first=True)
    tf = tbox(s, 0.85, 6.52, 11.6, 0.3)
    add(tf, m["stage_note"], size=8, color=GREY, first=True)
    footer(s, 19, L)

    # ---- 19 timeline
    s = ns(); m = L["s19"]
    header(s, m["kicker"], m["title"], m["sub"])
    gx, gw = 2.75, 9.4
    for wk in range(0, 21, 5):
        x = gx + gw * wk / 20
        ln = s.shapes.add_connector(1, Inches(x), Inches(1.95), Inches(x), Inches(5.75))
        ln.line.color.rgb = RGBColor(0xEC, 0xF0, 0xF4); ln.line.width = Pt(0.75)
        tf = tbox(s, x - 0.35, 1.72, 0.7, 0.22); add(tf, f"W{wk}" if wk else "", size=7.2, color=LGREY, align=PP_ALIGN.CENTER, first=True)
    for i, (name, start, dur, lab) in enumerate(m["phases"]):
        y = 2.10 + i * 0.52
        x = gx + gw * start / 20
        w = max(gw * dur / 20, 0.9)
        rrect(s, x, y, w, 0.34, fill=GOLD if i in (2, 4) else TEAL, radius=0.25)
        tf = tbox(s, x + 0.12, y + 0.06, w - 0.15, 0.25); add(tf, lab, size=7.2, bold=True, color=WHITE, first=True)
        tf = tbox(s, 0.85, y + 0.04, 1.90, 0.3); add(tf, name, size=8.8, bold=True, color=INK, first=True)
    for i, (dt, nm) in enumerate(m["ms"]):
        x = 0.85 + i * 3.92
        rrect(s, x, 6.00, 3.66, 0.76, fill=PANEL)
        rrect(s, x, 6.00, 0.05, 0.76, fill=RED, shape=MSO_SHAPE.RECTANGLE)
        tf = tbox(s, x + 0.22, 6.08, 1.6, 0.3); add(tf, dt, size=9, bold=True, color=RED, first=True)
        tf = tbox(s, x + 0.22, 6.40, 3.3, 0.3); add(tf, nm, size=8.2, color=GREY, first=True)
    footer(s, 20, L)

    # ---- 20 references
    s = ns(); m = L["s20"]
    header(s, m["kicker"], m["title"])
    for c, group in enumerate([REFS[:11], REFS[11:]]):
        tf = tbox(s, 0.85 + c * 5.95, 1.72, 5.55, 5.1)
        for i, r in enumerate(group):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_before = Pt(0 if i == 0 else 4); p.line_spacing = 1.06
            run = p.add_run(); run.text = r
            run.font.name = FONT; run.font.size = Pt(7.4); run.font.color.rgb = INK2
    footer(s, 21, L)

    return prs


for lang, out in [("en", "proposal_en.pptx"), ("zh", "proposal_zh.pptx")]:
    p = build(lang)
    p.save(out)
    print("saved", out, len(p.slides._sldIdLst))

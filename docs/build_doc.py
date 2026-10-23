from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

INK = RGBColor(0x10, 0x23, 0x3A)
GREY = RGBColor(0x5A, 0x6B, 0x7C)

doc = Document()

# ---- page + base styles ----
for sec in doc.sections:
    sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.4)
    sec.left_margin = Cm(2.6); sec.right_margin = Cm(2.6)

normal = doc.styles["Normal"]
normal.font.name = "Helvetica Neue"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(7)
normal.paragraph_format.line_spacing = 1.22
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "PingFang HK")

def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = "Helvetica Neue"
        r.font.color.rgb = INK
        r.font.size = Pt(14 if level == 1 else 11.5)
    h.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    h.paragraph_format.space_after = Pt(5)
    return h

def para(text, italic=False, size=10.5, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic
    r.font.size = Pt(size)
    if color is not None:
        r.font.color.rgb = color
    return p

def bullet(text):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10.5)
    return p

def caption(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True; r.font.size = Pt(8.5); r.font.color.rgb = GREY
    p.paragraph_format.space_before = Pt(2)
    return p

def table(headers, rows, widths, cap=None):
    if cap:
        cp = caption(cap)
        cp.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h); r.bold = True; r.font.size = Pt(8.8)
    for row in rows:
        cells = t.add_row().cells
        for i, c in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(c); r.font.size = Pt(8.6)
            p.paragraph_format.space_after = Pt(1)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True
    for cell in t.rows[-1].cells:
        for p in cell.paragraphs:
            p.paragraph_format.keep_with_next = False
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


# ============================ TITLE ============================
t = doc.add_paragraph()
r = t.add_run("From Generating to Verifying")
r.bold = True; r.font.size = Pt(22); r.font.color.rgb = INK
t.paragraph_format.space_after = Pt(2)

st = doc.add_paragraph()
r = st.add_run("A reference-free measure of deck usability, used as a control signal in paper-to-slide generation")
r.font.size = Pt(11.5); r.font.color.rgb = GREY; r.italic = True
st.paragraph_format.space_after = Pt(10)

meta = doc.add_paragraph()
r = meta.add_run("CHAN Yee Tung  ·  DSAI4901 Capstone  ·  Supervisor: Dr. Jibin Wu  ·  October 2026")
r.font.size = Pt(9); r.font.color.rgb = GREY
meta.paragraph_format.space_after = Pt(4)

hr = doc.add_paragraph()
hr.paragraph_format.space_after = Pt(6)
pPr = hr._p.get_or_add_pPr()
from docx.oxml import OxmlElement
pBdr = OxmlElement("w:pBdr")
bottom = OxmlElement("w:bottom")
bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
bottom.set(qn("w:space"), "1"); bottom.set(qn("w:color"), "C08A2E")
pBdr.append(bottom); pPr.append(pBdr)

# ============================ 1 BACKGROUND ============================
heading("1. Background")
para("A conference talk gives an author ten to fifteen minutes to communicate work that occupies eight pages of a paper. "
     "The deck is therefore not a summary of the paper; it is a compression of it into an argument that an audience can follow in real time. "
     "Producing that compression is slow: the author must decide what to keep, find the figure that carries each claim, and fit both into a page "
     "that remains legible from the back of a room.")
para("Language models can now produce a plausible deck from a paper in under a minute. The question this project starts from is not whether they can, "
     "but whether the result is usable — and whether the system itself can tell.")
para("That second question matters because the failures are not subtle. A text box that runs past the slide edge, two elements that overlap, "
     "a caption that sits on a dark background, a page carrying two hundred and fifty words: these are mechanical failures, visible the moment the "
     "deck is projected. They are also the failures that a language model cannot see, because it never renders what it has written.")

# ============================ 2 CURRENT PRACTICE ============================
heading("2. How this is done today")
para("Work in this area has settled into two families, with an evaluation literature growing alongside them.")
para("Generation. PPTAgent treats deck creation as editing rather than authoring: it analyses reference presentations, extracts slide-level schemas, "
     "and emits edit actions. SlideGen, SlideLab and ArcDeck add narrative planning and multimodal grounding. These systems produce convincing decks, "
     "and on blind preference tests they are competitive with commercial tools. X+Slides makes the audience an explicit "
     "conditioning input rather than a constant (Chen et al., 2026).")
para("Repair. ReDeck decomposes revision into atomic edit actions and returns a renderer-derived observation after each one. PPTPilot, introduced with "
     "PPTArena, runs a plan-edit-check loop in which a vision-language model judges the result. SLIDEFORGE keeps slides as structured artefacts so that "
     "edits preserve native editability. DeepPresenter extends the loop with environment-grounded reflection "
     "(Zheng et al., 2026a).")
para("Evaluation. SlideAudit (UIST '25) provides an expert taxonomy of 27 slide design flaws over 2,400 annotated slides. DECKBench (KDD '26) scores "
     "decks against reference decks with similarity metrics and an LLM judge. PresentBench scores generation with fine-grained rubrics. "
     "PPTBench asks a different question - whether a model understands layout and design at all (Huang et al., 2025).")
table(
    ["Work", "Provides", "Leaves open"],
    [["PPTAgent, SlideGen, SlideLab", "Strong generators; narrative planning", "Whether the output is usable; local failures"],
     ["ReDeck, PPTPilot, SLIDEFORGE", "Repair loops with rendered feedback", "Which repairs helped, and by how much"],
     ["SlideAudit", "Flaw taxonomy; 2,400 annotated slides", "No loop; image-based; no per-class repair analysis"],
     ["DECKBench", "Deck-level scoring against a reference", "Needs a target deck; ranks systems, does not drive one"]],
    [3.7, 5.2, 6.3], cap="Table 1. What each body of work provides, and what it leaves open.")

# ============================ 3 GOOD / BAD ============================
heading("3. What is good, and what is not")
para("Three things are genuinely solved. Decks look convincing: layout is stable and styling consistent. Output is increasingly editable, because work has "
     "moved into the .pptx object layer; PosterMELD shows the same shift for posters, emitting print-ready, editable artefacts "
     "(Hu et al., 2026). And evaluation has matured from holistic scores to task-based measures — answering questions using only the "
     "artefact, or gating readiness on explicit criteria.")
para("Four things are not.")
bullet("Attribution is missing. ReDeck and PPTPilot both run repair loops, but neither reports which class of defect responded to repair and which did not. "
       "A deck-level gain of ten points tells us the loop helped; it does not tell us where.")
bullet("Measurement is post-hoc. SlideAudit and DECKBench score finished decks. A score that arrives after generation cannot steer generation.")
bullet("The instruments need references or labels. DECKBench requires a target deck; SlideAudit requires human annotation of images. Neither can be computed "
       "on an arbitrary .pptx at run time.")
bullet("Thresholds are conventions. The numbers used to decide whether a page is too dense — six bullets, thirty words, 24-point type — are widely repeated "
       "and rarely evidenced, as Section 6 sets out.")

# ============================ 4 CONCLUSION ============================
heading("4. Our reading of the evidence")
para("Put together, the literature describes a field that is good at producing decks and good at scoring them afterwards, but that has not closed the loop "
     "between the two. The instrument arrives too late to be used, and it is not decomposable when it does arrive.")
para("That is the gap this project addresses. It is narrow on purpose: not another generator, not a new taxonomy, but a measurement layer that can be computed "
     "during generation and a study of what that measurement is worth.")

# ============================ 5 WHY ============================
heading("5. Why this is worth doing")
para("First, the failures are mechanical, so they can be decided deterministically. Whether a shape lies outside the slide, whether two text boxes intersect, "
     "whether a colour pair reaches a contrast ratio: these are arithmetic, not judgements. A rule can be audited; a model's opinion cannot.")
para("Second, usability is a precondition. A deck that cannot be read fails regardless of how well its content was selected. Improving content on an unreadable "
     "page does not produce a better talk.")
para("Third, the result transfers. If the measurement is reference-free and computed on the object model, it can be applied to any deck produced by any system — "
     "including the baselines this project compares against. That is what makes the comparison fair, and what makes the artefact reusable.")

# ============================ 6 CONVENTION VS EVIDENCE ============================
heading("6. Convention, not evidence")
para("Practitioners are not short of rules. The IEEE NMDC author guidelines, for example, state that authors should \"not use font sizes smaller than 24 point\" "
     "and that a text-only page should carry \"no more than 30 words and no more than 6 lines\". The advice is clear, widely followed, and entirely without "
     "cited evidence. No study is referenced; other conferences give different numbers.")
para("The rules also disagree with each other. The six-by-six rule allows six words on each of six lines — thirty-six words in total — while the guideline above "
     "caps the same page at thirty. Both are stated with confidence; neither cites a study, and the practitioner literature has begun to argue that the six-by-six "
     "rule should be retired. When two widely used conventions differ by twenty per cent and neither can point to evidence, what is being transmitted is habit, "
     "not knowledge.")
para("It is worth separating three kinds of anchor, because they carry different weight and the design must treat them differently.")
table(["Anchor", "Example", "Where it comes from", "Can it support a measurement?"],
      [["Formal standard", "WCAG 2.2 AA contrast, 4.5:1", "Perceptual research, normatively fixed", "Yes — testable against users"],
       ["Practitioner convention", "24 pt; 30 words; 6 lines", "Repeated across guides, no citation chain", "No — a default, not a finding"],
       ["Empirical value", "Overlap greater than 5%", "Fitted to a particular corpus", "Only with sufficient data"]],
      [3.3, 4.4, 5.0, 3.6], cap="Table 2. Three kinds of anchor. Only the first is evidence in the ordinary sense; the third is evidence only if the sample supports it.")
para("Conventions persist for reasons unrelated to validity. They are cheap to state, easy to check, and plausible on their face. Nobody is held accountable "
     "when one is wrong, because the cost of a wrong threshold is invisible: a page that is slightly too dense still presents, and the audience simply reads less. "
     "A guideline can survive for decades on plausibility alone.")
para("What would it take to validate one? Vary the value, hold content and audience constant, and measure comprehension or preference — a design with severe "
     "confounds, since content quality dominates any effect of density. That study does not exist for slides, and it is not the contribution of this project. "
     "The honest position is therefore not that the conventions are wrong, but that they cannot bear the weight of a measurement instrument.")
para("The consequence is methodological. There is no validated value to fit, and forty calibration slides cannot support six fitted thresholds — roughly six "
     "slides per gate — so a value chosen that way would be an artefact of the sample. The design separates the gates by provenance instead:")
table(
    ["Gate", "Rule", "Threshold", "Provenance"],
    [["G1 Containment", "Every shape box inside the slide", "0 pt", "Binary rule — no free parameter"],
     ["G4 Contrast", "WCAG 2.2 AA ratio, fill against background", "4.5:1 (3:1 large)", "Published standard"],
     ["G3 Font size", "Body and title size, by slide role", "role-specific", "Convention; swept, not fitted"],
     ["G6 Density", "Characters and bullets, by slide role", "role-specific", "Convention; swept, not fitted"],
     ["G2 Overlap", "Text intersection over smaller box", "> 5%", "Empirical; swept"],
     ["G5 Text fit", "Rendered text height over box height", "≤ 0.95", "Renderer tolerance; swept"]],
    [3.0, 6.4, 2.6, 5.2], cap="Table 3. Gate provenance. Two gates are fixed by rule or published standard; the remaining four are swept, and none is fitted.")

para("Swept, not fitted, means the value is reported across a range and a conclusion is only accepted if it survives the whole range. The two standard-anchored "
     "gates have no free parameter at all. Because this project generates the decks, the role of each slide — title, agenda, content, figure, conclusion — is "
     "known from the outline, so density and type limits can differ by role without a classifier. That removes the objection that a title slide and a methods "
     "slide cannot share one density limit: they no longer do.")

# ============================ 7 PLAN ============================
heading("7. Plan and schedule")
para("The work is organised into four streams. Each produces something reportable on its own, so that a slip in one does not leave the project without a result.")
bullet("W1 — Metric. Six gates implemented on the .pptx object model; SRR and deck-ready computed for every deck.")
bullet("W2 — Repair. A decision procedure per violation class, cheapest reversible action first, with a guardrail that forbids adding content or changing numbers.")
bullet("W3 — Control. The loop that applies W2 under W1's signal: greedy, iterative, then budget-aware.")
bullet("W4 — Evidence. Detector validation against human labels; discriminative validity across systems; a controlled ablation of the verifier; a human study.")
para("Two checks run before the main study, because a failure in either invalidates the rest. Discriminative validity asks whether SRR orders systems as it "
     "should — human-made decks above PPTAgent above a naive pipeline. If human decks do not score highest, the gates are mis-specified and must be revised "
     "before any loop is run. Convergent validity asks whether SRR tracks human preference; that correlation is pre-registered, and it will be reported whether "
     "or not it holds.")
para("The stack follows the brief: PyMuPDF for parsing and figure extraction, python-pptx for native, editable output, a Streamlit front end for the demonstration, and CodeBuddy as the agent harness during development.")
para("Two departures from the brief's suggested schedule are deliberate. The brief places inspection in stage 5, weeks 12 to 14; this project begins it in week 5, "
     "because the metric has to be validated before the loop that depends on it is built. Second, the brief's stage 6 comparison names accuracy, coverage, "
     "readability, design, latency and cost. Coverage — whether the paper's key claims survive into the deck — is measured explicitly, with five to eight claims "
     "annotated per paper, so that all six dimensions are reported.")
table(
    ["Weeks", "Stream", "Deliverable", "Milestone"],
    [["W1–2  26 Oct – 8 Nov", "Scope and literature", "38 papers reviewed; gap fixed", "Proposal due 5 Nov 2026"],
     ["W3–4  9 – 22 Nov", "Environment and spikes", "Parse and render working", "Workshop 1, TBC (≈9 Nov)"],
     ["W5–7  23 Nov – 13 Dec", "Rulebook and detectors", "Six gates; 40-slide calibration", "Discriminative validity check"],
     ["W8–11  14 Dec – 17 Jan", "Layout and repair", "Repair actions; 110-slide test set", "Interim report, 7 Jan 2027"],
     ["W12–14  18 Jan – 7 Feb", "Calibration and loop", "Sweeps frozen; loop converged", "First SRR comparison"],
     ["W15–18  8 Feb – 7 Mar", "Experiments and study", "Ablation; 20-participant study", "Preference correlation"],
     ["W19–21  8 – 28 Mar", "Report and demonstration", "Report, demo, slide draft", "Supervisor review"],
     ["W22–23  29 Mar – 8 Apr", "Finalisation", "Final report, demo, slides", "Final, 8 Apr 2027; presentations 9–21 Apr"]],
    [3.5, 3.7, 5.2, 4.0],
    cap="Table 4. Schedule against the University timeline. Weeks are counted from 26 Oct 2026; the run to the final "
        "submission is 23 weeks, not the 20 in the brief's suggested plan.")

# ============================ 8 DISCLOSURE ============================
heading("8. Disclosure")
para("Generative AI tools were used for drafting and for code generation. All design decisions, the metric definitions, the evaluation protocol, the annotation "
     "and the analysis are the author's. The tools used and the extent of their use are recorded in a log, submitted with the report in line with the University's "
     "student guide on the use of GenAI. This document also forms the basis of the separate AI report submitted with the "
     "final report.")

# ============================ REFERENCES ============================
heading("References")
refs = [
 "Chen, H., Zhou, X., Zhou, W., et al. (2026). X+Slides: Benchmarking audience-conditioned slide generation. arXiv:2606.19256.",
 "Chen, X.-S., Zhu, J., Li, P.-L., Wang, H., & Guo, M.-H. (2026). PresentBench: A fine-grained rubric-based benchmark for slide generation. arXiv:2603.07244.",
 "Hu, H., Dang, C., Liu, Y., et al. (2026). PosterMELD: Multi-agent paper-to-poster generation with editable print-ready outputs. arXiv:2608.02218.",
 "Huang, Z., Liu, X., Hu, T., Zhang, K., & Liu, Y. (2025). PPTBench: Holistic evaluation of LLMs for PowerPoint layout and design understanding. arXiv:2512.02624.",
 "IEEE Nanotechnology Materials and Devices Conference. (2021). Presentation preparation guidelines and requirements. https://ieeenmdc.org/past-conferences/nmdc-2021/call-for-papers/presentation-preparation-guidelines-and-requirements/",
 "Liang, X., Zhang, Z., Zhang, X., Su, H., Xu, Y., Sun, S., & You, C. (2025). SlideGen: Collaborative multimodal agents for scientific slide generation. arXiv:2512.04529.",
 "Jang, D., Heisler, M. L., Xing, L., et al. (2026). DECKBench: Benchmarking multi-agent frameworks for academic slide generation and editing. arXiv:2602.13318.",
 "Ofengenden, M., Man, Y., Pang, Z., Gui, L.-Y., & Wang, Y.-X. (2025). PPTArena: A benchmark for PowerPoint editing. arXiv:2512.03042.",
 "Ozden, T. C., VS, S., Horoz, F., et al. (2026). Narrative-driven paper-to-slide generation via ArcDeck. arXiv:2604.11969.",
 "Pang, W., Lin, K. Q., Jian, X., He, X., & Torr, P. (2025). Paper2Poster: Towards multimodal poster automation from scientific papers. arXiv:2505.21497.",
 "Tian, M., Zeng, Z., Yang, Y., et al. (2026). ReDeck: Step-level render-grounded refinement for document-to-slide generation. arXiv:2609.00194.",
 "Vats, V., Sharma, K., & Wang, Y. (2026). SlideLab: Audience-centered scientific slide generation and evaluation. arXiv:2609.30294.",
 "Zhang, Z. J., Chen, R., Zhong, M., & Wobbrock, J. O. (2025). SlideAudit: A dataset and taxonomy for automated evaluation of presentation slides. arXiv:2508.03630.",
 "Zheng, H., Guan, X., Kong, H., et al. (2025). PPTAgent: Generating and evaluating presentations beyond text-to-slides. arXiv:2501.03936.",
 "Zheng, H., Mo, G., Yan, X., et al. (2026a). DeepPresenter: Environment-grounded reflection for agentic presentation generation. arXiv:2602.22839.",
 "Zheng, H., Wang, F., Xiong, T., et al. (2026b). SLIDEFORGE: An LLM agent for controllable editing of slides as structured artifacts. arXiv:2609.03109.",
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.first_line_indent = Cm(-0.6)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(ref); r.font.size = Pt(8.4); r.font.color.rgb = INK

out = str(Path(__file__).resolve().parent / "Proposal_Background_and_Plan.docx")
doc.save(out)
print("saved", out)

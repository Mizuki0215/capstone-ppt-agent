# Capstone — From Generating to Verifying

An AI agent that turns a research paper into a presentation deck **and can tell
whether the result is usable**. DSAI4901 capstone, CHAN Yee Tung, supervisor
Dr. Jibin Wu.

> The deck is not a summary of the paper; it is a compression of it into an
> argument an audience can follow in real time. A language model can produce one
> in a minute — but it never renders what it has written, so it cannot see that a
> text box runs past the slide edge.

The contribution is not another generator. It is a **reference-free usability
measure computed on the `.pptx` object model**, used as an in-loop control
signal, plus a study of what that measurement is worth.

---

## Status

| | |
|---|---|
| Pipeline (parse → compose → render) | working; 2 papers rendered end-to-end |
| Generation layer | heuristic only; LLM stages designed in `docs/llm_plan.md`, not yet built |
| Selection | `src/schema.py` — requirement + rule table + claim-level 1/0, 38 tests green |
| Detector | **4 of 6 gates** — G1 containment, G2 overlap, G3 font size, G6 density |
| Gates still missing | **G4 contrast** (WCAG 2.2 AA), **G5 text fit** (rendered height) |
| First measurement | `build/detect_v1.json` — DOC2PPT, 9 slides, 0 clean, SRR 0.0 |
| Repair / control loop | not started |
| Test set, labels, baselines, human study | not started |
| Proposal | EN + ZH, DOCX + PDF, 6 pp |

Plan: **[WBS.md](WBS.md)** (98 jobs, 216 h) · generation layer: **[docs/llm_plan.md](docs/llm_plan.md)**

## Layout

```
src/
  parse.py      paper PDF → sections, figures, captions   (PyMuPDF)
  compose.py    outline + bullets + speaker notes         (stdlib; --llm optional)
  render.py     plan → editable .pptx with notes          (python-pptx)
  detect.py     gate checks straight off the object model (v1: G1 G2 G3 G6)
  schema.py     requirement / section type / claim, and the selection rule table
build/          intermediate JSON (deck.json, plan.json, detect_v1.json)
out/            rendered decks
docs/           proposal EN/ZH (.docx/.pdf) + the scripts that build them
research/       literature: 35 indexed papers, notes; PDFs are not committed
deck/           proposal deck builder and its outputs
rulebook.md     the violation rulebook — every gate as a decision procedure
scripts/        fetch_papers.py — rebuild the paper corpus from arXiv ids
docs/diagrams/  three views of the same system, generated from content.py
WBS.md          work breakdown, 98 jobs, 22-week calendar
docs/llm_plan.md   how outline → bullets → speaker notes are generated
```

## Running the pipeline

`parse` needs PyMuPDF; `render` needs python-pptx. They may live in different
interpreters, which is why `run.sh` takes both paths.

```bash
./run.sh research/pdfs/PPTAgent_2501.03936.pdf          # → out/PPTAgent_2501.03936.pptx
./run.sh path/to/paper.pdf --llm                        # let a model rewrite bullets/notes

python3 src/detect.py out/PPTAgent_2501.03936.pptx --json build/detect_v2.json
python3 -m pytest                                                # 38 tests
```

Current scope is deliberately narrow: **single-column English papers**, 10–12
slides, 16:9.

## The six gates

| Gate | Rule | Threshold | Provenance |
|---|---|---|---|
| G1 Containment | every shape box inside the slide | 0 pt | binary rule, no free parameter |
| G2 Overlap | text intersection over smaller box | > 5 % | empirical; swept |
| G3 Font size | body and title, by slide role | role-specific | convention; swept, not fitted |
| G4 Contrast | WCAG 2.2 AA, fill against background | 4.5:1 (3:1 large) | published standard |
| G5 Text fit | rendered text height over box height | ≤ 0.95 | renderer tolerance; swept |
| G6 Density | characters and bullets, by slide role | role-specific | convention; swept, not fitted |

*Swept, not fitted*: the value is reported across a range, and a conclusion is
only accepted if it survives the whole range. Forty calibration slides cannot
support six fitted thresholds, so none is fitted. See §6 of the proposal.

## Paper corpus

`research/pdfs/` holds 40 third-party PDFs (~400 MB). They are **not committed**
— they are not our work, and every one is reproducible from the arXiv id in
`research/papers_index.csv`:

```bash
python3 scripts/fetch_papers.py           # fetch what is missing
python3 scripts/fetch_papers.py --check   # report only
```

## Documents

```bash
python3 docs/build_doc.py        # → docs/Proposal_Background_and_Plan.docx
python3 docs/build_doc_zh.py     # → docs/Proposal_Background_and_Plan_ZH.docx
```

PDFs are exported from the DOCX with LibreOffice.

## Disclosure

Generative AI tools were used for drafting and for code generation. All design
decisions, metric definitions, the evaluation protocol, the annotation and the
analysis are the author's. Tools and extent of use are recorded in a log
submitted with the report, per the University's student guide on GenAI use.

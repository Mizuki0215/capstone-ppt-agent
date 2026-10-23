# Evidence plan — response to review feedback

Status: proposal-stage decisions locked. This document fixes the four open points before the interim report.

---

## 0. Correction first

The earlier claim "no one measures trust, 0 of 35 papers" was **wrong**. It was an artefact of my own selection: the relevance scoring favoured generation/agent papers and filtered out evaluation work.

What actually exists:

| Work | What it does | What it does not do |
|---|---|---|
| **SlideAudit** (Zhang et al., 2025) | Expert taxonomy of slide design flaws; 2,400 annotated slides via trained Prolific annotators; benchmarks LLMs on flaw identification | Measures; does not repair. No closed loop, no causal claim |
| **DECKBench** (Jang et al., 2026) | Benchmark for academic slide generation **and editing**; slide- and deck-level fidelity, coherence, layout quality, multi-turn instruction following | Evaluates outputs of fixed systems; does not isolate the contribution of inspection |
| **PPTArena / PPTPilot** (Ofengenden et al., 2025) | 1,300 human-curated edits; VLM judges; PPTPilot runs a plan–edit–**check** loop | Check is VLM-judged, not deterministic; no per-class attribution |
| **ReDeck** (Tian et al., 2026) | Step-level render-grounded refinement; one edit, one observation | Repairs well; does not quantify what inspection buys |
| **This project** | Deterministic, per-class violation signal used **inside** the loop | — |

So the corrected claim is not "nobody measures". It is: **measurement exists as a post-hoc score; nobody uses it as a control signal, and nobody has isolated its causal contribution.**

---

## 1. The fork: Option A, locked

**Do not build a finer slide taxonomy.** SlideAudit already published an expert taxonomy with 2,400 annotations produced through paid, trained annotation. A solo student competing on taxonomy breadth loses on both quality and credibility, and a reviewer will name the overlap immediately.

**Locked direction: violation detection embedded in the repair loop, with quantified marginal gain.**

The unit of contribution is the *controller*, not the *label space*. Reuse SlideAudit's categories where they overlap (overlap, crowding, legibility) and add only the mechanical ones a design taxonomy does not cover (containment, rendered fit).

Why this survives review:
- SlideAudit/DECKBench are *evaluators*: they rank outputs. They cannot answer "how much of this deck's quality came from inspection?"
- That question needs a system with the controller switched on and off — i.e. an experiment, not a benchmark.
- The answer is a number a sceptic can rerun: ΔSRR per inspection dollar.

### Paste-ready gap statement

> Slide quality can now be measured after the fact: SlideAudit provides an expert taxonomy with 2,400 annotated slides, and DECKBench scores deck-level fidelity and layout quality. What these instruments cannot answer is whether measurement can *drive* generation. Existing agents either repair without measuring (ReDeck) or verify with a VLM judge that is itself a black box (PPTPilot), so in neither case is the contribution of inspection separable from the contribution of the generator. This project treats computable violations as an in-loop control signal and reports, per violation class, what inspection and repair add to deck quality and at what cost.

---

## 1b. Differentiation vs SlideAudit and DECKBench

Verified against both full texts (SlideAudit is UIST '25; DECKBench is KDD '26), not abstracts.

**Relation to SlideAudit: re-operationalisation — not a subclass, not a competing taxonomy.**

| | SlideAudit | This project |
|---|---|---|
| Label space | 27 categories across 5 dimensions (19 used in their evaluation) | **Adopts the six overlapping categories verbatim** |
| Input | Rendered slide image | **Native .pptx object model** — exact pt sizes, bounding boxes, z-order, fill colours |
| Task | Name the flaws; propose a text fix plan; humans rate the plan | **Detect → edit → re-render → re-measure** |
| Outcome | Agreement with human labels; plan quality | Change in the artifact, and what it cost |
| Scope | General design critique | **Deliberately narrowed** to mechanistically decidable flaws |

Overlapping categories adopted as the label space: `Content Overflow/Cut-off`, `Text Overlap`, `Occluded Content`, `Low contrast text`, `Illegible Typeface`, `Cluttered Layout`.
Out of scope by design (requires semantic judgement, not mechanism): spelling, distracting header, narrative ordering.

**Relation to DECKBench: a different object of measurement.**

| | DECKBench | SRR |
|---|---|---|
| Reference | Requires a ground-truth deck (similarity, DTW, transition similarity) | **Reference-free** |
| Granularity | Deck-level suite + LLM judge for coherence | Per-slide predicate, then aggregated |
| Use | Rank finished systems | **Optimise during generation** |
| Determinism | Similarity metrics + LLM judge | Fully deterministic, rerunnable bit-for-bit |

**One-sentence version, for the proposal:**

> SlideAudit supplies the vocabulary — 27 categories produced by image-based critique — and DECKBench scores completed decks against a reference; neither yields a reference-free, object-level predicate that can be optimised during generation. This project re-operationalises six of SlideAudit's categories as computable predicates over the native .pptx object model and uses them as an in-loop control signal rather than a post-hoc score.

**Head-to-head experiment this unlocks** (cheap, and it is the core of the thesis):

1. Run SlideAudit's full-taxonomy prompt condition (GPT-4o) on our slides, restricted to the six overlapping classes.
2. Compare its per-class F1 with our deterministic detectors on the same slides and the same labels.
3. Pre-registered reading of the result:
   - rules win on mechanical classes (overflow, containment, font size) → supports "computable beats subjective" where it matters;
   - LLM wins on holistic classes (clutter) → **defines the boundary of the approach**, reported as a finding, not a failure.

Either outcome is a defensible contribution; a null on one class is information, not noise.

## 2. Slide-ready rate (SRR) and deck-ready — operational definition

Two related but different quantities. Reporting only one invites the obvious challenge: *nine of ten slides passed — is the deck ready?*

```
SRR(deck)  = |{slides passing every gate}| / |{slides}|     # continuous, slide-level
deck-ready = (SRR == 1.0)                                   # binary, all-or-nothing
```

| Quantity | Level | Range | Used for |
|---|---|---|---|
| **SRR** | slide | 0–1 | the control signal; what the repair loop optimises |
| **Deck-ready** | deck | {0,1} | whether the artefact is usable without manual fixes |

Rules of reporting:

1. Always report SRR, deck-ready **and per-gate pass rates** — an aggregate hides one gate failing on every slide.
2. Never report deck-ready alone: it maps a near-miss (9/10) and a disaster (2/10) onto the same zero.
3. Never call SRR a "deck-ready rate". The previous draft did exactly that; the two are not interchangeable.

| Gate | Rule (mechanical) | Threshold | Anchor | Swept over |
|---|---|---|---|---|
| G1 Containment | every shape bbox ⊆ slide area; images not cropped | 0 pt | binary — no threshold to justify | — |
| G2 Overlap | text–text intersection ÷ area of smaller box | > 5 % | empirical | 2 / 5 / 10 % |
| G3 Font size | body, title, read from run properties | 18 / 28 pt | design guidance | 16 / 18 / 20 |
| G4 Contrast | WCAG 2.2 AA ratio from fill vs background | 4.5:1 (3:1 large) | published standard | — |
| G5 Text fit | rendered text height ÷ box height, real font metrics | ≤ 0.95 | renderer tolerance | 0.90 / 1.00 |
| G6 Density | characters per slide; bullets per block | ≤ 140; ≤ 6 | empirical | 120 / 160 |

**Provenance is stated per gate on purpose.** Two thresholds are external standards (WCAG, common minimum font guidance) and need no defence; the binary rule has no free parameter; the remaining three are explicitly *empirical*, and that is the honest answer to "where did the threshold come from".

**Sensitivity procedure (this is the answer to the reviewer's question):**
1. Sweep each empirical threshold over the values listed.
2. Compute SRR at each setting across the 150-slide set.
3. Compute Spearman ρ between SRR and the mean human quality rating of the same slides.
4. Report the full curve, not only the chosen point; pick the setting that maximises ρ, and report how flat the optimum is.
5. Re-run the main comparison at the worst plausible setting (best and worst end of the sweep) as a robustness check.

---

## 3. Detector validation protocol

| Item | Decision |
|---|---|
| Split | **40 calibration + 110 held-out test** (150 annotated in total). Calibration sets thresholds and revises rules; the test set is opened once |
| Disjointness | Calibration slides, test slides and human-study stimuli are **three disjoint sets**. No slide a human rates is ever used for threshold tuning |
| Sample | Stratified across **all three systems** (naive, PPTAgent, ours) — never validate only on our own output |
| Sampling frame | 8 held-out papers × 3 systems = 24 decks; ~6 slides per deck, drawn to include at least two figure-heavy slides |
| Annotators | 2, independent; rulebook session + 10 calibration slides before starting |
| Agreement | Cohen's κ per class, target ≥ 0.70; if below, revise the rulebook and re-annotate 20 % **before** proceeding |
| Adjudication | disagreements resolved by a third pass; the adjudicated label is the reference |
| Reporting | precision / recall / F1 **per class**, plus confusion matrix; never an aggregate only |
| Re-freeze rule | If any class has F1 < 0.70 on the calibration set: revise the operational definition (relax or tighten the rule), re-annotate 20 % of calibration, re-freeze. At most **two** revision rounds, logged with dates and reasons |
| Final freeze | All detectors frozen before the held-out test set is opened and before the human study begins |

---

## 4. Human study

| Item | Decision |
|---|---|
| Design | within-subject; each rater sees all three systems on the same paper |
| Sample | 30 raters × 4 papers = 120 paired comparisons per contrast; papers rotated across raters |
| Primary contrast | **ours vs the VLM-judge repair loop**, pre-registered, α = .05 two-sided |
| Secondary | ours vs naive, naive vs PPTAgent — Holm–Bonferroni, α = .05/3 ≈ .017 |
| Test | Wilcoxon signed-rank, paired; report median difference, bootstrap 95 % CI, effect size r = \|Z\|/√N |
| Reliability | ICC(2,k) across raters, reported alongside |
| Stimulus set | drawn only from held-out test decks; raters never see calibration slides |
| Blinding | conditions anonymised and order counterbalanced |

**Power.** n = 30 pairs gives ≈ 80 % power for d ≈ 0.55 at α = .05; under the Holm-adjusted α = .017 the detectable effect rises to d ≈ 0.60. Written into the proposal as a limitation: the design is powered for **medium** effects, so a null on a small effect is reported as inconclusive, not as evidence of no difference.

**Fallbacks if recruitment falls short of 30** (declared in advance, in this order):
1. Three expert raters on a 5-point rubric → ICC(2,k) as secondary evidence.
2. Expand automated QA from 10 to 25 items per deck — cheap, and increases the precision of the automated track.
3. Report the Bayesian posterior probability of superiority instead of a p-value.
4. Label the human result **exploratory**, not confirmatory, and say so in the abstract.

---

## 5. Baselines — each answers a different question

These are **not three equivalent competitors**. They are three separate claims, and conflating them is the fastest way to lose the argument.

| # | Baseline | The question it answers | Role |
|---|---|---|---|
| ① | Naive single-pass — one generation, no inspection | Does inspection add anything at all? | **Necessity check.** If we cannot beat this, nothing else matters |
| ② | PPTAgent (Zheng et al., 2025) | Are we competitive with the strongest reproducible generator? | **Calibration against the field**, not the thesis |
| ③ | VLM-judge repair loop (PPTPilot/ReDeck-style) | Same loop, same budget — is computable verification better than a VLM judge? | **The methodological claim, run as a controlled ablation** |

③ is a **controlled ablation, not a competitor system**: identical loop, identical generator, identical retry cap and token budget; **only the verifier differs** (deterministic predicates vs VLM critique). Any difference in outcome is therefore attributable to the verifier, which is the only claim the thesis needs.

Only ③ isolates the variable the thesis is actually about: *the verification mechanism*, holding the loop fixed. ① and ② hold the *system* variable instead. Write them that way in the report, and order the results section accordingly — ③ first, not last.

Ablation: remove anchors / remove inspection / remove repair → per-module attribution.

---

## 6. Timeline: critical path and cut order

```
annotation (40 cal) ──► calibrate ──► FREEZE ──► repair ──► experiment ──► human study ──► writing
      ▲                    ▲                        │                          │
      │              re-freeze allowed              │                          │
  20/wk from W5      (max 2 rounds)                └── test set opened once ───┘
                                                   (no tuning after this line)
```

| Checkpoint | Week | Rule |
|---|---|---|
| **Rulebook frozen** | **W4** | Each violation written as a decision procedure (what counts, what is excluded, edge cases) **before any detector code exists** |
| Calibration set complete | W7 | 40 slides annotated, κ reported |
| First freeze | W8 | Detectors locked; repair loop built against them |
| Re-freeze window | W13 | Up to 2 revision rounds, logged; no changes after |
| Test set opened | W14 | 110 slides annotated; **no detector changes after this point** |
| Human study | W15–18 | Detectors and system frozen |

Single point of failure is **annotation**. Mitigation: use SlideAudit's published categories as pre-labels for the overlapping gates, so annotators confirm rather than label from scratch.

Cut order if behind (decided now, not in March):

| Priority | If behind | Cost |
|---|---|---|
| 1st cut | papers 8 → 6 | loses generality, keeps validity |
| 2nd cut | drop naive from the human study (keep it automated) | weakens the "loop adds anything" claim only |
| 3rd cut | annotation 150 → 100 slides | keeps per-class κ, widens CIs |
| **never cut** | κ, ablation, cost/latency, one human study | these are the grade |

Feature freeze: end of W15. Anything not finished is reported as future work.

---

## 7. Where each piece goes in the proposal

| Section | Uses |
|---|---|
| Problem statement | §1 corrected gap paragraph |
| Related work | §0 comparison table — lead with SlideAudit and DECKBench, not with a strawman |
| Methodology | §2 gate table, §3 validation protocol |
| Evaluation | §4 design + power, §5 baselines |
| Risk / feasibility | §4 fallbacks, §6 cut order |

---

## 8. What this changes in the deck

- Slide 9 claim corrected (was factually wrong).
- Two slides added: slide-ready rate definition, evidence plan.
- Baselines 2 → 3; the VLM-judge loop is now the primary contrast.
- References 18 → 21 (SlideAudit, DECKBench, PPTArena).
- Paper count 35 → 38 (33 agents + 5 education).


---

## 9. Negative results we commit to reporting

An A-grade report is defined by what it says when the answer is unflattering. These are pre-registered, so they cannot be quietly dropped in March.

| If we find | We report it as |
|---|---|
| SRR rises but human preference is flat or falls | **The control-signal claim fails.** Report as a dissociation: the metric moved, perceived quality did not. This is the single most threatening outcome and it is pre-registered here precisely so it cannot be buried |
| A detector class has F1 < 0.70 after two revision rounds | That class is not mechanically decidable; we report the class as out of scope and say why |
| The VLM-judge loop matches ours on overlap but loses on overflow | Verification mechanism matters per class, not globally — a sharper finding than "ours wins" |
| Ablation shows repair contributes more than detection | The loop's value is in editing, not measurement — contradicts the framing, and we say so |
| Cost per deck exceeds the human baseline | The approach is not deployable at this scale; report the break-even point |

The last two are the ones that would hurt. Writing the commitment down now is what makes the positive results credible.

---

## 10. Risk register tied to the grade

| Risk | Trigger | Pre-committed response | Grade impact if unmanaged |
|---|---|---|---|
| Detector F1 too low | calibration F1 < 0.70 | re-operationalise, re-freeze, at most 2 rounds | B+ — SRR becomes uninterpretable |
| Annotation κ < 0.70 | calibration κ | revise rulebook, re-annotate 20 %, third adjudicator | B+ — ground truth not trustworthy |
| Human recruitment < 30 | end W14 | expert rating + expanded QA + exploratory label | B+ — evidence downgraded |
| Novelty questioned | reviewer cannot see SRR vs SlideAudit | §1b statement, stated in the first two minutes | B+ — reads as unread literature |
| Behind schedule | end W14 | cut order in §6 | B — incomplete evidence chain |

Floor is B; none of these risks can push below it. Every one of them pushes *within* the B range, which is why they are worth managing rather than fearing.

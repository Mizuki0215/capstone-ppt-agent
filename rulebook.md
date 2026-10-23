# Violation rulebook — v0 (draft)

Purpose: turn each gate into a decision procedure that a second person can apply
without asking the author. Every rule must state **what counts**, **what does not
count**, and **why**. If a rule cannot be applied to a specific slide without a
judgement call, the rule is not finished.

Scope: single-column English papers; decks produced by this pipeline; `.pptx`
object model (not rendered images).

Status legend: `[ ]` open · `[x]` decided · `[?]` needs a decision before coding

---

## G1 Containment — does anything sit outside the slide?

**Rule.** A slide violates G1 if any shape's bounding box, after rotation, is not
fully inside the slide rectangle (0, 0, W, H). Tolerance 0 pt.

- [ ] Does a shape that is deliberately full-bleed (its box extends past the edge
      but the visible content does not) count? *Proposed: yes, it violates, because
      the object model is what a user edits.*
- [ ] Are off-slide shapes that are hidden behind others counted separately or once?
- [?] Group shapes: test the group box, or the union of its children?
- [ ] Zero-size placeholder shapes left by python-pptx: exclude by area < 1 pt².

**Why 0 pt.** Containment is binary; there is no defensible tolerance. Anything
else becomes an arbitrary threshold.

---

## G2 Overlap — do two text elements collide?

**Rule.** Violation if the intersection area of two text-bearing shapes exceeds
5 % of the **smaller** shape's area.

- [ ] Background or decorative shapes vs text: count only when both carry text?
      *Proposed: yes — text-on-text only.*
- [?] Text inside a shape that intentionally sits on a coloured panel: the panel
      is not text, so it is excluded by the rule above. Confirm.
- [ ] Two text boxes in the same group and deliberately stacked (e.g. title +
      subtitle): still an overlap? *Proposed: yes, if the intersection > 5 %.*
- [ ] Rotated shapes: use the axis-aligned bounding box, or the rotated polygon?
- [ ] Overlap of a text box with an image is **not** G2. It belongs to G6
      (text over a busy background) or to a separate class. Decide.

**Threshold.** 5 % is empirical. Sweep 2 / 5 / 10 % and report.

---

## G3 Font size — is the type too small?

**Rule.** Body text ≥ 18 pt; titles ≥ 28 pt. Read from run properties, not from
rendered height.

- [ ] Slide role: title slide, section divider, content, figure, conclusion.
      Which minimum applies to each?
- [?] Does a table's cell text count as body text?
- [ ] Text inside a chart or a group: recurse into it or ignore?
- [ ] `autofit` set to shrink: read the authored size, or the effective size?

**Why 18 / 28.** Convention (see doc §6). Not evidence. Sweep 16 / 18 / 20.

---

## G4 Contrast — can the text be read against what is behind it?

**Rule.** WCAG 2.2 AA: contrast ratio ≥ 4.5:1 for body, ≥ 3:1 for large text
(≥ 18 pt bold or ≥ 24 pt). Computed from the run colour and the effective
background.

- [?] Effective background: solid fill of the shape behind, or the slide
      background, or the nearest opaque shape in z-order?
- [ ] Gradient or image backgrounds: what is the reference colour?
- [ ] Text with no explicit colour (inherits from theme): resolve via the theme,
      or skip?
- [ ] Links and accent colours: same threshold?

**Why 4.5:1.** Published standard, not a fitted value.

---

## G5 Text fit — does the text overflow its box?

**Rule.** Estimate the rendered text height using real font metrics; violation if
height > 0.95 × box height.

- [ ] Font substitution: the deck's font may be missing on the reviewer's machine.
      Which metrics do we use — declared or fallback?
- [ ] Line breaking: greedy wrap is not what PowerPoint does. How large is the
      error, and do we accept it?
- [?] CJK text: width per glyph differs; the estimator must branch on script.
- [ ] `autofit` shapes: if PowerPoint would shrink the text automatically, is that
      a violation? *Proposed: no — but record it as a warning.*

**Threshold.** 0.95 is a renderer tolerance, not a claim about legibility.

---

## G6 Density — is the slide doing too much?

**Rule.** Per slide, by role: characters ≤ 140 and bullets ≤ 6 for content
slides; different limits for title and conclusion slides. (To be fixed.)

- [?] Characters: count spaces? Count bullet markers? Count the title?
- [ ] CJK: one character carries several English words' worth of meaning. Separate
      limit, or convert to a rough word-equivalent?
- [ ] Is a slide with one long sentence worse than six short bullets?
- [ ] Tables: count cell text toward the slide total?

**Threshold.** Convention, and a weak one. Sweep 120 / 140 / 160.

---

## Cross-cutting decisions

- [ ] Units: every number above is in **pt at the deck's own scale**. Confirm the
      deck is 16:9 and 13.333 × 7.5 in for all papers.
- [ ] Order of application: G1 → G5 → G2 → G4 → G3 → G6. Repairs change later
      results; the order must be fixed before any experiment.
- [ ] Counting: a slide may violate several gates; report per gate, and report
      `deck-ready` as "no gate violated on any slide".
- [ ] Annotation: two annotators, independent, per class; adjudicate disagreements.

## What is deliberately out of scope

Spelling, narrative order, claim correctness, aesthetics. These need semantic
judgement and are not mechanically decidable. They are covered by the human
study, not by the gates.

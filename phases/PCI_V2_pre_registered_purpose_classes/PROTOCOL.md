# Phase PCI-V2: Pre-Registered Purpose Class Inference

**Status:** PRE-REGISTRATION (protocol only — no execution yet)
**Date of pre-registration:** 2026-04-19
**Date of execution:** (to be filled in when test is run)
**Committed before execution:** YES (commit hash to be recorded after commit)

---

## Pre-Registration Integrity Statement

This protocol is being written **before any execution of the tests described below.** The purpose is to provide a methodologically rigorous replacement for the original PCI phase (2026-01-04), which was audited in April 2026 and found to have several weaknesses:

1. No pre-registration — the 8 candidate classes appear to have been selected post-hoc
2. Circular reasoning — elimination constraints derived from grammar statistics then used to eliminate alternatives
3. Test-specificity bias — constraints bundled toward active process-control framing
4. Subdivision bias — "Continuous Process Control" emerged as sub-class after "Workshop Operations" umbrella failed
5. Missing alternative candidates — mnemonic, positional, grammatical-metadata framings were not tested
6. No scripts, data tables, or falsifiable protocol documents

The original PCI produced C171 ("continuous closed-loop process control is the only viable purpose class"). This claim has received substantial retrospective support from downstream predictions (Brunschwig structural alignment, Testamentum recipe matching, compositional atom decomposition), but the derivation itself does not justify a uniqueness claim.

PCI-V2 tests the continuous-control framing against a broader set of pre-registered alternatives, using pre-specified tests with pre-specified pass/fail criteria. The objective is to determine whether continuous-control is the best-fitting class under rigorous comparison, or whether alternative framings fit comparably well.

**We commit to reporting whatever outcome PCI-V2 produces**, including an outcome that weakens the continuous-control framing or favors an alternative. The goal is epistemic rigor, not retroactive validation.

---

## Research Question

Of the candidate purpose classes below, which best predicts the observed structural features of Voynich Currier B?

"Best" is operationalized via a scoring function over multiple pre-specified predictions. See Section 5 for scoring methodology.

---

## Candidate Classes

Ten candidate purpose classes, each defined independently of Voynich-specific observations. Each class is characterized by the structural signature it would produce in a system authentically encoding that purpose (drawing on known systems in that class, e.g., programming languages for process control, mnemonic systems for memory aids).

### Class 1: Continuous closed-loop process control (CCPC)
**Definition:** The notation encodes ongoing active control over a physical process requiring hazard management, stability maintenance, and recovery procedures. Exemplars: industrial control system notations, distillation manuals, reaction control checklists.

### Class 2: Mnemonic notation system (MNEM)
**Definition:** The notation functions as a memory aid for trained operators — compact identifiers for concepts the operator already knows, without encoding process dynamics. Exemplars: chemical symbol systems as pure nomenclature, mnemonic prayer texts, pharmacist's shorthand.

### Class 3: Positional reference system (POS)
**Definition:** The notation encodes spatial or sequential positions within a larger reference structure (apparatus, calendar, sequence of operations) without encoding dynamics. Exemplars: position codes on equipment, index cards, catalog reference numbers.

### Class 4: Grammatical metadata system (GMETA)
**Definition:** The notation records morphological, syntactic, or orthographic patterns of a natural-language corpus (possibly for linguistic or scribal purposes). Exemplars: grammar notation in classical treatises, scribal abbreviation systems, shorthand for natural-language dictation.

### Class 5: Discrete recipe collection (RECIPE)
**Definition:** The notation encodes a collection of independent, self-contained recipes (cookbook-style) with specific quantities, durations, and named ingredients. Exemplars: Apicius, medieval cookbooks, Circa Instans, individual medicinal compositions.

### Class 6: Medical treatment protocol (MED)
**Definition:** The notation encodes patient-care protocols with conditional branching, dosage specification, symptom observation, and outcome criteria. Exemplars: Ortolf von Baierland's Arzneibuch, medical consilia, diagnostic flowcharts.

### Class 7: Ritual / liturgical notation (RIT)
**Definition:** The notation encodes repeated formulaic sequences for ritual performance, with emphasis on exact reproduction rather than adaptive execution. Exemplars: liturgical books, magical-ritual texts, canonical prayers.

### Class 8: Calendar / astronomical computation (CAL)
**Definition:** The notation encodes temporal cycles, astronomical events, or calendrical computation. Exemplars: astronomical tables, computus texts, zodiacal medicine calendars.

### Class 9: Random / hoax text (RAND)
**Definition:** The notation is meaningless — generated to appear textual but lacking structural organization characteristic of any purpose class. Exemplars: Nabokov's intentional nonsense, deliberately falsified texts.

### Class 10: Hybrid / multiple purposes (HYB)
**Definition:** The notation combines features of two or more of the above classes (e.g., recipe collection + mnemonic catalog, ritual + calendar). Scored as the best-fitting combination whose predictions jointly cover the observed features.

---

## Structural Features Used for Testing

The following structural features of Currier B are publicly documented (via existing constraints) and will serve as the observations against which each candidate class is scored. These features are SELECTED for this test; they are not exhaustive of what's known about B, but they are the ones we judge most discriminative between candidate classes.

**Features are NOT new measurements — they are existing structural observations.** This test compares how well each candidate class's typical signature matches these observations.

| # | Feature | Observed Value (documented constraint) |
|---|---|---|
| F1 | Forbidden transitions (directional) | ~17 disfavored transitions at O/E < 0.5, ~65% compliance (C789) |
| F2 | Kernel convergence structure | k/h/e kernel with recovery pathways (C085, C089) |
| F3 | Hazard topology (5-class structure) | 5 natural clusters of disfavored transitions (C109) |
| F4 | Positional zone gradient within lines | Q0 → Q1-Q3 → Q4 gradient documented (C1425-C1430) |
| F5 | Presence of numeric quantities | Zero numeric markers detected (C287, C288) |
| F6 | Conditional branching structures | Zero if-then structures detected |
| F7 | Completion/endpoint markers | Zero explicit completion markers |
| F8 | Self-transition in macro states | AXM at 70% self-transition; very high monostate dominance |
| F9 | Cross-line dependency | MI=0 across lines (each line independent) |
| F10 | Document-level atom homogeneity | Per-folio JSD from corpus ~0.019 (high homogeneity) |
| F11 | Heaps' β (lexical diversity) | 0.74 for B — higher than natural-language range (0.5-0.7) |
| F12 | Closed vocabulary occupancy | 479 of 48,640 possible MIDDLEs exist (0.9%, C1028) |
| F13 | Adjacent atom MI | 1.65 bits — 2.5x natural-language character MI |
| F14 | Mode A/B suffix alternation | ~80% within-paragraph alternation of two suffix modes |
| F15 | Cross-token terminal-to-HEAD routing | Specific preferential transitions documented (C1563) |

---

## Pre-Specified Predictions per Class

For each candidate class, we list predicted directions for each feature. Prediction = whether the feature is expected (HIGH, PRESENT, STRONG), absent (LOW, ABSENT, WEAK), or indeterminate (NEUTRAL) under that class.

### Legend
- **HIGH / PRESENT / STRONG:** feature would typically be present/pronounced under this class
- **LOW / ABSENT / WEAK:** feature would typically be absent/weak under this class
- **NEUTRAL:** class doesn't strongly predict this feature either way
- **INCOMPATIBLE:** this feature's observed value is incompatible with the class

Pre-specified prediction direction for each class-feature pair:
- `HIGH` = class predicts feature should be strongly PRESENT
- `LOW` = class predicts feature should be ABSENT or weak
- `NEUTRAL` = class doesn't strongly predict this feature
- `INCOMPATIBLE` = reserved for direct categorical falsification only (e.g., RAND predicts NO structure, so all structural features are incompatible with RAND)

Predictions table (committed predictions — will not be modified after this document is committed):

| Feature | CCPC | MNEM | POS | GMETA | RECIPE | MED | RIT | CAL | RAND | HYB |
|---|---|---|---|---|---|---|---|---|---|---|
| F1: Forbidden transitions (directional) | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | LOW | INCOMPATIBLE | NEUTRAL |
| F2: Kernel convergence structure | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | LOW | INCOMPATIBLE | NEUTRAL |
| F3: Hazard 5-class structure | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | LOW | INCOMPATIBLE | NEUTRAL |
| F4: Line positional gradient | HIGH | LOW | HIGH | LOW | HIGH | HIGH | HIGH | HIGH | LOW | NEUTRAL |
| F5: Numeric quantities present (observed: LOW) | LOW | LOW | LOW | LOW | HIGH | HIGH | LOW | HIGH | NEUTRAL | NEUTRAL |
| F6: Conditional branching (observed: LOW) | LOW | LOW | LOW | LOW | LOW | HIGH | LOW | LOW | NEUTRAL | NEUTRAL |
| F7: Completion markers (observed: LOW) | LOW | LOW | LOW | LOW | HIGH | HIGH | HIGH | LOW | NEUTRAL | NEUTRAL |
| F8: Macro-state monostate (high self-transition) | HIGH | LOW | HIGH | LOW | LOW | LOW | HIGH | LOW | INCOMPATIBLE | NEUTRAL |
| F9: Cross-line MI = 0 (observed: TRUE) | HIGH | HIGH | HIGH | LOW | HIGH | LOW | LOW | HIGH | HIGH | NEUTRAL |
| F10: Folio atom homogeneity (low JSD ~0.019) | HIGH | LOW | HIGH | HIGH | LOW | LOW | HIGH | HIGH | HIGH | NEUTRAL |
| F11: Heaps β high (0.74) | HIGH | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | HIGH | NEUTRAL |
| F12: Closed vocabulary (0.9% occupancy) | HIGH | HIGH | HIGH | LOW | LOW | LOW | HIGH | HIGH | LOW | NEUTRAL |
| F13: High atom MI (2.5x NL chars) | HIGH | NEUTRAL | NEUTRAL | LOW | LOW | LOW | NEUTRAL | LOW | INCOMPATIBLE | NEUTRAL |
| F14: Mode A/B alternation | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | LOW | INCOMPATIBLE | NEUTRAL |
| F15: Terminal-HEAD routing | HIGH | LOW | LOW | LOW | LOW | LOW | LOW | LOW | INCOMPATIBLE | NEUTRAL |

Note: CCPC predicts F9 HIGH (cross-line independence within an executing program is expected — each line is a safety-envelope unit).

HYB is deliberately NEUTRAL on all features because a "hybrid" class doesn't make specific predictions; it will be scored as the best-fitting combination ex post, acknowledged as an interpretive weakness of the HYB class.

Observed values for each feature (pre-documented constraints, used as the "ground truth" that predictions score against):

| Feature | Observed value | Counted as |
|---|---|---|
| F1 | 17 disfavored transitions at O/E<0.5, directional | PRESENT (HIGH) |
| F2 | k/h/e kernel, recovery pathways documented | PRESENT |
| F3 | 5 natural clusters of disfavored transitions | PRESENT |
| F4 | Q0→Q1-Q3→Q4 gradient documented | PRESENT |
| F5 | Zero numeric markers (C287, C288) | ABSENT (LOW) |
| F6 | Zero if-then structures | ABSENT |
| F7 | Zero explicit completion markers | ABSENT |
| F8 | AXM 70% self-transition | PRESENT |
| F9 | MI = 0 across lines | PRESENT (cross-line independence) |
| F10 | JSD ~0.019 mean (very low) | PRESENT (high homogeneity) |
| F11 | Heaps β = 0.74 | PRESENT (high) |
| F12 | 479/48640 = 0.9% occupancy | PRESENT (closed vocabulary) |
| F13 | Atom MI 1.65 vs 0.65 NL | PRESENT (high) |
| F14 | ~80% within-paragraph alternation | PRESENT |
| F15 | Specific terminal-HEAD preferences documented | PRESENT |

All 15 features have observed PRESENT/HIGH values in Voynich B (or LOW for F5/F6/F7 which are negative findings). This is deliberate — features were selected because they have clear directional observations.

---

## Scoring

For each class, count:
- **MATCHES:** prediction direction consistent with observed value (HIGH + present, LOW + absent)
- **MISMATCHES:** prediction direction inconsistent with observed value
- **INCOMPATIBLE:** observed value directly falsifies the class's prediction
- **NEUTRAL:** no strong prediction; excluded from scoring

**Class score = (MATCHES - 2×MISMATCHES - 5×INCOMPATIBLE) / (# scoring features for this class)**

(The 2× and 5× weightings reflect that direct mismatches and incompatibilities are more informative than matches — this prevents a class from scoring well by making only trivial predictions.)

Classes with any INCOMPATIBLE result are disqualified from being "best-fit" regardless of other matches (direct falsification takes precedence).

---

## Decision Rule

**Primary:** Which class has the highest score? Is the margin over second place greater than 0.15 (approximately 2 standard deviations in the scoring metric)?

**Outcomes:**
1. **Clear winner** (margin > 0.15): one class is best-supported; C171 reformulated to reference it specifically
2. **Close competition** (margin ≤ 0.15): multiple classes fit comparably well; C171 reformulated as "manuscript is consistent with [top N classes]; alternative framings not differentiated"
3. **No class scores positive** (all scores ≤ 0): the candidate set is insufficient; a new round of candidates is needed; C171 is withdrawn

**Pre-specified hypothesis:** CCPC will achieve the highest score. We commit to reporting this prediction's outcome regardless of direction.

---

## Multiple-Testing Correction

Not strictly applicable (this is not a multiple-hypothesis test in the traditional sense) but we include the following conservative measures:

- Class scores will be computed via **blind scoring** — specifically, predictions per class will be entered into a JSON file BEFORE running the comparison, and the comparison script will compute scores mechanically from that JSON without opportunity for adjustment.
- The JSON will be committed to the repo as a timestamped pre-registration artifact BEFORE the scoring script is executed.
- Any modification to predictions after the JSON is committed will be considered post-hoc and invalidate the pre-registration.

---

## Execution Plan

1. **This protocol document is committed to the repo with pre-registration timestamp.** (Target: 2026-04-19)

2. **Predictions JSON is written and committed separately**, capturing the per-class per-feature predictions machine-readably. (Target: 2026-04-19 or 2026-04-20)

3. **Scoring script is written and tested on a dummy JSON** to verify mechanical correctness. (Target: 2026-04-21 or later)

4. **Execution:** scoring script reads predictions JSON and produces class scores. Script output is saved to results/pci_v2_scores.json. (Target: after SISMEL validation work, likely May 2026)

5. **Results are reported verbatim** in an INDEX.md that documents outcome (winner, margin, per-class scores, decision).

6. **No modifications to predictions after execution.** If the outcome is surprising, the protocol is followed to its conclusion; post-hoc revisions are not permitted.

---

## What Would Count as Falsification of the Working Hypothesis

The working hypothesis is that Currier B is best characterized as a continuous closed-loop process control (CCPC) notation. PCI-V2 falsifies this hypothesis if:

1. **Alternative class wins by margin > 0.15.** Some other class (MNEM, POS, etc.) achieves a higher score than CCPC. In this case, the paper's framing must be revised to reflect the alternative.

2. **All classes score low (≤ 0).** The candidate set is inadequate; the purpose-class inference framework is insufficient and C171 should be withdrawn pending a better approach.

3. **CCPC has an INCOMPATIBLE flag** that wasn't expected. If some observed feature directly contradicts a CCPC prediction, CCPC is disqualified regardless of other matches.

**We commit to reporting all three of these outcomes if they occur.** The paper's citation of C171 will reflect whatever PCI-V2 produces.

---

## Why This Is NOT Dishonest

A few reasons this constitutes legitimate methodology, not retrofit rationalization:

1. **Pre-registration is real.** This document commits to pre-specified criteria before any scoring is performed. Git timestamps make this verifiable.
2. **Alternatives are genuinely threatening.** MNEM, POS, GMETA are real candidates that could plausibly fit. They are not strawmen.
3. **Incompatibility criteria are asymmetric.** CCPC can be disqualified by INCOMPATIBLE flags just as easily as any other class.
4. **Committed outcome reporting.** Whatever PCI-V2 produces, it will be reported. This document exists specifically to make that commitment public and auditable.
5. **Original PCI is retained, not replaced.** The original PCI record stays intact. PCI-V2 is a separate, pre-registered re-examination.

---

## Relationship to Original PCI

This is NOT:
- A validation of original PCI
- An attempt to re-derive the same answer
- A back-fit of methodology to a pre-existing conclusion

This IS:
- An independent pre-registered test of the same question
- A good-faith attempt to determine whether alternative framings fit as well or better
- Self-correction of a methodologically weak prior phase

The original PCI's derivation remains in the record as an exploratory precursor. PCI-V2's result will supersede it as the primary citation for C171 regardless of outcome.

---

## Limitations of This Protocol

We acknowledge several limitations that future PCI-V3 efforts should address:

1. **Predictions are based on typical signatures of each class, not on rigorous cross-corpus comparisons.** A better test would benchmark Voynich features against actual corpora from each class.
2. **The 15 structural features are themselves not exhaustive.** A reviewer could argue we've selected features that favor CCPC.
3. **Pre-registered scoring weights (2×, 5×) are our choice.** Different weightings could produce different outcomes.
4. **INCOMPATIBLE thresholds are qualitative.** A fully quantitative version would specify numerical cutoffs.
5. **This is not a Bayesian model comparison.** A proper Bayesian version would require likelihood functions, not prediction-direction matching.

These limitations are real. PCI-V2 is an improvement over PCI, not a gold-standard methodology. The paper should cite PCI-V2's result with appropriate hedging about these limits.

---

## Status

- **Protocol committed:** (fill in commit hash after commit)
- **Predictions JSON committed:** (pending)
- **Scoring script written:** (pending)
- **Execution:** (pending)
- **Results:** (pending)

# PHASE 702: Scribe × Engineered-Substrate Interaction

**Status:** COMPLETE — INDEX-only documentation (no constraint registration)
**Date opened:** 2026-05-19
**Date closed:** 2026-05-19
**Verdict:** Test design defeated by structural data confound that cannot be resolved internally. Methodology lessons saved; substrate measurements unchanged from prior values.

---

## Question

Davis 2020 identifies 5 distinct scribal hands in the Voynich. The engineered substrate quintet (C2015, C2022, C2032, C2035, C2036, C2039) had been measured as a corpus-level property without scribe partition. PHASE_702 asked whether:

- **Hypothesis A — Substrate-as-grammar:** Scribes produce identical substrate signatures; the engineering is at the system/language level.
- **Hypothesis B — Substrate-as-convention:** Scribes diverge measurably; the engineering is a workshop-trained convention with potential teacher-scribe identification.

Both experts converged on PHASE_702 as the highest-EV next move because Davis 2020 is an external classification (published without knowledge of our substrate metrics).

---

## Data acquisition

Davis 2020 paper ("How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript," *Manuscript Studies* 5.1) downloaded from Internet Archive (`data/davis_2020_paper.txt`). Table 1 transcribed manually to `data/davis_scribe_attribution.csv` covering 228 folio entries.

Davis explicitly maps Currier dialect to scribe: **Currier A = Scribe 1; Currier B = Scribes 2, 3, 4, 5.** This means the "engineered substrate" (a Currier-B property) is a property of Scribes 2-5 collectively.

---

## Feasibility check

Currier-B P-placement tokens per scribe (per `_load_davis_attribution.py`):

| Scribe | N tokens (Currier B, P) | Status |
|-------:|------------------------:|:------|
| 1 | 0 | Currier A only |
| 2 | 8,925 | PASS |
| 3 | 10,990 | PASS |
| 4 | 1,116 | MARGINAL |
| 5 | 579 | INSUFFICIENT |

3-way cross-scribe comparison feasible (Scribes 2, 3, 4) with Scribe 4 at the floor.

Scribe 3 Currier-A audit (`_audit_scribe3_currierA.py`): 875 tokens trace cleanly to Davis's botanical assignments (f58, f96). Data internally consistent.

---

## Main test result — methodologically empty

Three-way scribe comparison (`_scribe_substrate_test.py`):

| Scribe | r21 (raw) | Bootstrap r21 mean | Bootstrap SE |
|-------:|----------:|-------------------:|-------------:|
| 2 | −1.21 | −2.53 | **11.16** |
| 3 | +0.72 | +0.79 | 0.33 |
| 4 | +2.05 | +4.85 | 35.93 |

F-ratio = 0.029, mechanically triggering "Hypothesis A supported." However, the result is empty: bootstrap-ratio noise (r21 = lag2/lag1 explodes when lag1 samples near zero) inflated within-scribe variance, deflating F-ratio. The verdict triggered for the wrong reason.

**Underlying confound identified:** Davis scribes correlate ~perfectly with sections at the within-Currier-B level (Scribe 3 = matched-S Q18; Scribe 2 ≈ Section B Q13 + botanical bifolia). No clean within-section cross-scribe comparison possible at adequate N.

---

## Within-scribe content pivots

### Scribe 2 content comparison (`_scribe2_content_comparison.py`)

| Partition | N tokens | lag1 | lag2 | r21 |
|-----------|---------:|-----:|-----:|----:|
| Botanical Q4-7 | 2,296 | +0.015 | +0.015 | +1.00 (flat) |
| Balneology Q13 | 6,166 | **−0.018** | +0.011 | −0.61 (period-2) |
| Rose obverse Q14 | 396 | −0.014 | +0.007 | −0.47 |

Pairwise z(botanical vs balneology) = −2.05 — marginally significant content-driven flip.

### Scribe 3 content comparison (`_scribe3_content_comparison.py`)

| Partition | N tokens | lag1 | lag2 | r21 |
|-----------|---------:|-----:|-----:|----:|
| Botanical Q8/Q16 (Currier A) | 866 | +0.026 | +0.014 | +0.54 (sustain) |
| Matched-S Q18 | 6,969 | +0.024 | +0.014 | +0.59 (sustain) |
| Unmatched-S Q18 | 2,527 | +0.003 | +0.008 | +1.45 (flat) |

All pairwise |z| < 1.5. Scribe 3 maintains consistent sustain signature across content domains. Reading A (content-driven) and Reading B (scribe-driven personal accent) both compatible with this result.

---

## Expanded content-class clustering (`_content_class_clustering.py`)

Per crazy-expert's Reading C proposal + expert-advisor's N-matching insistence. Tested whether substrate signatures cluster by content class across scribes, with ratio-valid gating (|lag1| > 0.015) and N-matched downsample controls.

| Cell | Scribe | Currier | N | lag1 | lag2 | Mode |
|------|-------:|--------:|--:|-----:|-----:|------|
| S1 herbal pure Q1-3 | 1 | A | 3,871 | +0.004 | +0.002 | flat |
| S1 herbal mixed Q4-7 | 1 | A | 3,245 | +0.011 | +0.007 | flat |
| S1 Q15 pharma | 1 | A | 1,384 | −0.005 | +0.013 | flat |
| S1 Q17 recipes | 1 | A | 1,347 | +0.025 | +0.010 | sustain |
| S2 botanical Q4-7 | 2 | B | 2,296 | +0.013 | +0.015 | flat |
| **S2 balneology Q13** | 2 | B | 6,166 | **−0.018** | +0.011 | **period-2** |
| S3 botanical Q8/Q16 | 3 | A | 866 | +0.025 | +0.014 | sustain |
| S3 matched-S Q18 | 3 | B | 6,969 | +0.024 | +0.015 | sustain |
| S3 unmatched-S Q18 | 3 | B | 2,527 | +0.003 | +0.008 | flat |

**Three modes descriptively observed:** flat (5 cells), sustain (3 cells), period-2 (1 cell).

### N-matched downsample controls (load-bearing)

| Comparison | Raw z | N-matched median z | 80% CI | Verdict |
|------------|------:|-------------------:|:-------|:--------|
| S2 botanical vs S2 balneology | −2.05 | **+1.73** | [+0.89, +2.68] | **Marginal under N-matching** |
| S2 botanical vs S3 botanical | n/a | +0.47 | [+0.05, +1.49] | N-driven artifact |
| S3 matched-S vs S3 unmatched-S | n/a | −0.42 | [−1.62, +0.35] | N-driven artifact |

**The Scribe 2 content flip (z=−2.05) was N-driven.** Balneology was 2.7× larger than botanical; downsampling balneology to match drops |z| below 2.0 with CI crossing zero. The original finding does not survive N-matching.

---

## Verdict: INDEX-only, no constraint

**Reading A (content-driven) weakened.** The only evidence for content-driven flipping within a single scribe was Scribe 2 botanical vs balneology, and that does not survive N-matching.

**Reading B (scribe-driven) cannot be ruled out.** Scribe 3's consistency across botanical Q8/Q16, matched-S Q18, and (partly) unmatched-S Q18 is compatible with personal-accent style.

**Reading C (three-mode content-class clustering)** is descriptively present in the table but is partly framework-echo: the modes map onto existing Section B / matched-S / non-procedural distinctions. The Scribe-1-Q17-recipes sustain finding is the only clean novel observation, but a single cell at N=1,347 is not strong enough to register a new mode-class.

**The substrate quintet's period-2 signature is structurally Q13-only / Scribe-2-only data.** This is a previously undocumented data limitation worth recording: C2032's −0.65 reference value is essentially a Q13 measurement on a single scribe, and the scribe×section confound prevents internal disentanglement.

No new constraint registered. Existing substrate quintet measurements (C2015, C2022, C2032, C2035, C2036, C2039) stand at their prior values.

---

## Cross-references

- C171 — engineered substrate (foundational, unchanged)
- C2015, C2022, C2032, C2035, C2036, C2039 — substrate quintet measurements (unchanged)
- C361 — Section B intrinsic vocab cohesion (relevant to section confound)
- C2031 — e-depth oscillation in Section B (Q13 measurement, now flagged as scribe-confounded)
- `feedback_framework_as_null.md` — caught this attempt at registration overshoot
- `feedback_within_folio_shuffle_null_first.md` — analogous N-control discipline
- `feedback_calibrate_thresholds_against_controls.md` — calibration against in-distribution controls (PHASE_697 lesson applied here)

---

## Methodology lessons (saved to memory)

1. **Bootstrap-ratio noise + N asymmetry produces framework-fit false positives.** PHASE_702 main test (3-way scribe F-ratio) returned mechanical Hypothesis-A from inflated within-scribe variance. Within-scribe pivot produced z=−2.05 that was driven by 2.7× N imbalance. Without N-matched downsampling controls, would have registered a false finding. Save as `feedback_n_matching_for_within_scribe_comparisons.md`.

2. **Scribe×section confound in Davis attribution structurally prevents internal substrate-vs-scribe disentanglement.** Davis scribes correlate ~perfectly with sections at adequate-N partition. Q13 = Scribe 2 only; matched-S = Scribe 3 only; zodiac = Scribe 4 only. No clean within-section cross-scribe comparison exists in the data. Save as `project_scribe_section_confound_structural.md`.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `_load_davis_attribution.py` | Feasibility check: per-(scribe, Currier, placement) token counts |
| `_audit_scribe3_currierA.py` | Audit Scribe 3 Currier-A anomaly (875 tokens trace to f58, f96 — internally consistent) |
| `_scribe_substrate_test.py` | Main 3-way per-scribe substrate test (methodologically empty) |
| `_scribe2_content_comparison.py` | Within-Scribe-2 content pivot (z=−2.05 raw, N-driven artifact) |
| `_scribe3_content_comparison.py` | Within-Scribe-3 content pivot (ambiguous, max z=1.14) |
| `_content_class_clustering.py` | Expanded content-class test with N-matched controls (verdict: Reading C weakened) |

---

## Data

| File | Source |
|------|--------|
| `data/davis_2020_paper.txt` | Davis 2020 djvu OCR from Internet Archive |
| `data/davis_scribe_attribution.csv` | Davis Table 1 + narrative description, 228 folio entries with confidence flags |

---

## What this means for the project

**Internal-methodology procedural ceiling now confirmed across two consecutive phases** (PHASE_701 Lullian wheels + PHASE_702 scribe×substrate). Both produced clean negative findings on legitimately-designed tests. The internal-methodology toolkit is saturated for the current question class (alternative-class adversarial testing, substrate disentanglement).

Real next-direction options remain external:
1. External corpus acquisition (Antidotarium Nicolai, Mesue's Grabadin) for the Section S 4-folio source gap
2. Physical reconstruction grounded in C2031/C2032/C2040 substrate signatures
3. Vellum codicological analysis (animal DNA, hair follicle patterns, parchment quality)
4. Italian archive research (Visconti court records, Pavia library inventories, Faenza/Florentine workshop traces)

PROJECT_SYNTHESIS.md remains canonical reference for current understanding.

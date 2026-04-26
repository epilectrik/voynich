# Phase 651: HT-Density Validation

**Status:** COMPLETE
**Date:** 2026-04-26
**Constraint registered:** C1966 (Tier 2)

---

## Question

The HT (Human Track) layer has had three competing readings across project history:

1. **Fluency practice** (early Tier 4): HT consolidates uncommon character combinations for handwriting practice.
2. **Attention scaffolding** (early Tier 4): HT keeps the operator-scribe alert during long passive-monitoring procedures (the "watch the bath for 8 hours" use case).
3. **Compound specification** (current C935 revised, Tier 2): HT carries condensed compound specs that mirror local control grammar content.

C935 anchored reading #3 at the corpus-wide level: HT contains operational content redundant with body simple MIDDLEs (71.6% hit rate vs 59.2% random). Phase 651 tests whether reading #3 also holds at **per-folio resolution** — does HT density quantitatively track compound-specification load? — and whether the competing readings (#1, #2) show any independent signal.

---

## Method

### HT operationalization

Per HTSC C740: HT = UN by definition. UN = tokens whose MIDDLE is not in the simple/core MIDDLE inventory. Operationally: any Currier B token whose MIDDLE is classified compound by `MiddleAnalyzer.is_compound()`.

### Predictors tested

| Predictor | Reading tested |
|---|---|
| Distinct compound MIDDLE count per folio | Specification (#3) — folios with more diverse compounds need more HT |
| Total tokens per folio | Condensation pressure — short folios compress; long ones don't |
| sh-rate (passive observation marker) per folio | Attention scaffolding (#2) — passive watching → more HT |
| qo-rate (active fire marker) per folio | Inverse attention — active fire → less HT |

Spearman correlations + 2000-permutation p-values, n=82 folios.

### Within-section robustness

Computed pairwise correlations within Section B (Bath, n=20), Section H (Herbal, n=32), Section S (Stars/Recipes, n=23) to control for section confound.

---

## Results

### Pairwise correlations across all 82 folios

| Predictor | Spearman ρ | p (two-sided) | Verdict |
|---|---|---|---|
| **distinct compound MIDDLEs** | **+0.602** | **<0.0001** | Specification: strongly confirmed |
| total tokens | +0.260 | 0.021 | Mild positive (opposite of condensation hypothesis) |
| sh_rate | -0.195 | 0.075 | Marginal, opposite of attention prediction |
| qo_rate | +0.048 | 0.65 | Null |

### Within-section robustness

| Section | n | HT vs distinct compound MIDDLEs |
|---|---|:---:|
| B (Bath) | 20 | **+0.764** |
| H (Herbal) | 32 | **+0.507** |
| S (Stars/Recipes) | 23 | **+0.686** |

Every section shows a strong positive correlation. The signal is structural, not section-driven.

Section H and S also show inverse correlation with total tokens (rho = −0.34, −0.40) — secondary condensation effect on those sections specifically. Section B is too long-form for condensation pressure to manifest.

---

## Findings

### Finding 1: HT density quantitatively tracks compound-specification load (C1966)

The +0.602 cross-folio correlation with p<0.0001 promotes C935 from "HT carries compound specification (corpus-wide)" to "HT density quantitatively tracks per-folio compound specification needs." The relationship is robust across all three major sections at rho 0.51–0.76.

Mechanistically: HT compound MIDDLEs are by definition not in the simple core. A folio with many *distinct* compound MIDDLEs has many different compound specs to encode. The strong positive correlation says HT density tracks compound *diversity*, not just total instance count. That's a real informational claim — high-HT folios deploy many different specs, not just repeated instances of the same spec.

### Finding 2: Attention-maintenance hypothesis rejected at corpus scale

The early Tier 4 attention-scaffolding reading predicted HT density should correlate positively with passive-monitoring intensity (sh-rate). The data shows the OPPOSITE: rho = −0.195 (p = 0.075). Folios with more passive monitoring have *less* HT, not more.

The hypothesis was given a fair test (the prediction was specific and falsifiable). It failed. Removing it from the live interpretation set.

Note: the broader "scribe-attention infrastructure" speculation discussed in INTERPRETATION_SUMMARY.md (which is distributed across HT, line-as-safety-packet, transition markers, etc.) is not refuted by this — only the specific reading "HT density tracks passive-monitoring duration" is. The attention function may still be served by HT *as a side effect* of compound specification (writing complex compounds keeps the hand busy), but that's not the primary function.

### Finding 3: Secondary condensation effect in Section H and S

Within Section H (Herbal) and Section S (Stars/Recipes), HT density inversely correlates with folio token count (rho = −0.335, −0.398 respectively). Short folios compress more into HT compounds; long ones spell things out in body. This effect is absent in Section B (long-form bath operations don't show condensation pressure).

This is a sub-finding worth documenting in C1966 evidence but not a separate constraint.

---

## What's NOT registered

- **Fluency-practice reading (#1)** is not separately tested. The strong specification result suggests HT's primary function is operational; fluency practice could be a side effect but not primary. The reading is left in the SPECULATIVE record without active support or refutation.

- **Section-S enrichment** (HT mean rate 31.6% vs B at 21.2%) is documented but doesn't get its own constraint. It's a downstream consequence of Section S having more compound diversity per folio (recipes section packs many different compound specs into condensed format).

---

## Pending future work

- **Partial correlation with multiple predictors simultaneously** would tighten the specification-vs-condensation independence. Not registered as immediate work — the within-section breakdown already provides the main robustness check.

- **Cross-scribe HT analysis.** Lisa Fagin Davis identified ≥5 scribal hands. Does HT density vary by scribe, and if so does it co-vary with compound specification load or independently? Could distinguish operator-specific style from procedural specification needs.

- **Out-of-sample compound-MIDDLE inventory check.** MiddleAnalyzer's "compound" classification depends on the core-inventory cutoff. Robustness of C1966 to the cutoff threshold should be checked.

---

## Files

- `scripts/`
  - `s1_ht_density_v1.py` — initial test (3 predictors, crude metrics; preserved for transparency)
  - `s2_ht_density_v2.py` — refined test with proper compound MIDDLE counting (the locked-in result)
- `results/`
  - `ht_density_test.json`
  - `ht_density_v2.json`

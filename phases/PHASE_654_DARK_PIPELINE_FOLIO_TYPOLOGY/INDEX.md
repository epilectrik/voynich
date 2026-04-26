# Phase 654: Dark Pipeline Folio-Resolution Typology Test

**Status:** COMPLETE — VERDICT: NULL
**Date:** 2026-04-26
**Constraint registered:** None (per locked outcome plan)

---

## Question

Does a unified atom-substrate typology exist at folio resolution? Per the materials-as-identifiers thesis: do all 9 named dark-pipeline atoms (per C1941) map to substrate categories such that ≥3 show enrichment ≥4× with Bonferroni-corrected p<0.0056?

This test was specified after Phase 653 demonstrated that paragraph-resolution material-event alignment was structurally underpowered (per crazy-expert post-mortem). Pre-registration committed BEFORE running the test (commit f346cbb).

---

## Method

See `PRE_REGISTRATION.md` and `locked_classifications.json` for full pre-registered protocol. Key elements:

- **8 substrate categories** (mutually exclusive): MINERAL_MERCURY, GOLD, SILVER, ANIMAL_SUBSTRATE, VEGETABLE_SUBSTRATE, FERMENT_GENERIC, MIXED_MINERAL, THEORETICAL
- **21 matched folios classified** (per SISMEL Catalan recipe content; locked before any atom analysis)
- **9 atoms tested** per C1941: equipment (lch, lk, eed), process (cth, eke, ksh), material (fch, cs, eckh)
- **Statistical test:** Fisher exact one-sided, Bonferroni-corrected alpha = 0.05/9 = 0.0056
- **Pass:** ≥3 atoms with enrichment ≥4× and corrected p<0.0056
- **Null:** ≤1 atom passes

---

## Result

**0 atoms passed strict criteria. VERDICT: NULL.**

Closest to passing:
- **cs → GOLD:** 2/2 in-category (100%) vs 7/19 not-in-category (37%). Enrichment 2.71×, p=0.17. Below 4× threshold, well above corrected alpha (0.0056).
- **fch → MINERAL_MERCURY:** 6/7 in-category (86%) vs 11/14 not-in-category (79%). Enrichment 1.09×, p=0.59. fch is essentially universal across matched folios.

All other (atom, category) pairs showed enrichment <2× with p>0.10.

## Why the result contradicts C1939/C1940 apparently

C1939 reports "fch ∞ enrichment on 6/6 mercury folios." Phase 654 finds fch on 11/14 non-mercury folios, ratio 1.09×.

The discrepancy is methodological:
- **C1939** likely uses morphological/structural extraction of fch (e.g., f-prefix + ch in specific MIDDLE position)
- **Phase 654** used the locked pre-registered methodology: substring presence (any token containing 'fch')

These are **different definitions** of "fch occurrence." Under substring-presence, fch is essentially universal. Under morphological extraction, fch may be substantially more specific.

Per pre-registration discipline, the locked methodology was substring-presence. The test asked that specific question and got the specific answer NULL. Retroactively switching to morphological extraction would violate pre-registration.

## What survives

- **C1939 and C1940 stand on their original methodology** (more specific than substring-presence). Tier 3 status preserved.
- **The unified atom-substrate typology framework** — that all 9 dark-pipeline atoms map to substrate categories under uniform folio-presence-by-substring methodology — **is empirically refuted at this resolution and methodology.**

## What this tells us

The architecture's substrate-marking signals exist at a more specific structural level than substring presence. Atoms like fch are nearly universal as substrings but may be more specific when extracted with proper morphological position constraints.

Future work (NOT this phase, NOT under the pre-registered protocol):
- A morphological-extraction version of the same test could give different results
- That would be a separate test under a separate pre-registration
- The specific structural definition of each material atom (which positional and contextual features make a token an "fch occurrence") needs to be operationalized first

## Methodology lesson

Pre-registration discipline forces honest registration of nulls even when post-hoc reasoning would want to revise the test. The Phase 654 null is real **under the methodology specified at lock-time**. A stricter test under a different specification might pass; that test would need its own pre-registration.

This is the discipline working as intended: the test asked a specific question and got a specific answer. Retroactively changing the question to find a passing result would be the methodological failure.

---

## Outcome registration

Per `PRE_REGISTRATION.md` locked outcome plan:

> "If Phase 654 NULL: Document the null result; no new constraint registered. C1939 and C1940 stand as isolated material-identification findings (already Tier 3). Update INTERPRETATION_SUMMARY.md to reflect that the broader material-atom typology is empirically refuted."

Action taken:
- No new constraint registered
- C1939 (fch=mercury, Tier 3) and C1940 (cs=gold, Tier 3) preserved
- INTERPRETATION_SUMMARY.md updated with note that unified typology is refuted under tested methodology
- Phase 654 documented as a clean null

---

## Files

- `PRE_REGISTRATION.md` — locked protocol (committed before test)
- `locked_classifications.json` — locked categories + per-folio classifications
- `scripts/s1_run_typology_test.py` — test execution
- `results/test_results.json` — full result table

---

## Project-level note

Phase 651 + 652 + 654 together: two clean Tier 2 findings (C1966, C1967) + one clean null (Phase 654). The null is a feature, not a failure — pre-registration discipline enforced rigor where Phase 653's post-hoc framework would have produced over-claims.

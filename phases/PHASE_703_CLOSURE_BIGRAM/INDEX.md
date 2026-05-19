# PHASE 703: Closure Protocol Bigram Grammar Test

**Status:** COMPLETE
**Date opened:** 2026-05-19
**Date closed:** 2026-05-19
**Result:** Tier 3 registration as C2041 — `ar → al` directional asymmetry (47%, FDR p=0.005). Forbidden-bigram test inconclusive (data sparseness).
**Posture:** Refines C2030 (Voynich-wide late-term within-line adjacency clustering at +0.036) by testing whether the clustering has internal bigram grammar — directional asymmetries and/or forbidden LATE-LATE pairs.

---

## Result summary

**Test 1 (directional asymmetry) — PASS (1 of 6 testable pairs):**

| Pair | A→B | B→A | Asymmetry | p_raw | p_BH |
|------|----:|----:|----------:|------:|-----:|
| **ar/al** | **39** | **14** | **+0.47** | 0.0008 | **0.005** ✓ |
| ar/ol | 27 | 17 | +0.23 | 0.17 | 0.49 |
| al/ol | 16 | 10 | +0.23 | 0.33 | 0.49 |
| ol/or | 16 | 10 | +0.23 | 0.33 | 0.49 |
| ar/or | 19 | 21 | −0.05 | 0.87 | 1.00 |
| al/or | 10 | 11 | −0.05 | 1.00 | 1.00 |

**Test 2 (forbidden bigrams) — INCONCLUSIVE:**
Zero bigrams met the pre-registered N-floor (null-expected ≥ 5). 320 LATE-LATE bigrams across 144 possible (12×12) types → mean expected per type ≈ 2, below threshold. Test could not run at locked criteria — this is data sparseness, not negative result.

**Verdict:** Tier 3 per pre-registered combined criteria. Single constraint registered as C2041.

---

## Near-miss findings (not registered)

Three additional pairs show consistent +0.23 asymmetry toward `ol` as later position:
- ar → ol (27 vs 17)
- al → ol (16 vs 10)
- or → ol (16 vs 10)

None survive FDR at current N. If LATE-LATE bigram counts increase (e.g., extended corpus), these are pre-registered next-to-test candidates.

---

## Question

C2030 established that LATE-class MIDDLE families (ar/ary/aly/al and related short closure markers) chain adjacently within-line at +0.036 excess. The clustering is real and survives within-line shuffle null. C2030's registration explicitly says: *"Predicts (NOT tested): closure protocols may have internal bigram grammar (e.g., directional `or → al` vs `al → or` asymmetries, forbidden LATE-LATE pairs parallel to C109's class-level forbidden transitions)."*

This phase tests both predictions.

If confirmed:
- Closure is multi-token protocol, not single-token termination
- Refines C2030 with internal sub-grammar
- Parallel to C109 (class-level forbidden transitions) at MIDDLE-class level
- Aligns with C886 MIDDLE asymmetry prediction (constraint symmetric, execution directional)

---

## LATE inventory (LOCKED)

Closure/output-terminal MIDDLEs from C539 + C562:

```
ar, ary, aly, al, dar, dal, dary, daly, or, ory, oly, ol
```

12 MIDDLE strings. Identified via `morph.extract()` MIDDLE field equal to one of these.

---

## Test design (LOCKED)

### Pre-registered decision rules

**Test 1: Directional asymmetry**

For each ordered pair (A, B) with A ≠ B in the LATE inventory, observe count(A→B) and count(B→A) across all within-line adjacent LATE-LATE pairs in Currier B P-placement.

Null model: under within-line shuffle, P(observed(A→B) | total=count(A→B)+count(B→A)) = Binomial(total, 0.5).

Significance: two-sided binomial test on (A→B) vs (B→A) imbalance. FDR correction (Benjamini-Hochberg) across all pairs with total ≥ 5.

**Decision rule: REGISTERABLE if at least 1 pair has FDR-corrected p < 0.05 AND |obs(A→B) − obs(B→A)| / total ≥ 0.30** (effect size floor: at least 30% asymmetric)

**Test 2: Forbidden bigrams**

For each ordered LATE-LATE pair (A, B), compute expected count under within-line shuffle null (200 permutations). A bigram is "forbidden" if:
- Observed count = 0
- Expected count (null mean) ≥ 5
- Empirical null p (frequency of null shuffles producing observed=0) < 0.005

**Decision rule: REGISTERABLE if at least 1 bigram meets all three forbidden criteria.**

### Combined registration

- **Tier 2** if BOTH Test 1 and Test 2 produce at least one passing result
- **Tier 3** if exactly ONE of Test 1, Test 2 produces a passing result (with directional asymmetry > forbidden bigrams in interpretive weight, per C886 prediction)
- **No constraint** if neither test produces a passing result

---

## Controls

1. **Within-line shuffle null:** preserve line membership and token count per line; shuffle token order within each line. 200 permutations. (Per C2030 methodology.)

2. **Effect-size floor (Test 1):** the asymmetry must be at least 30% to count, even if statistically significant. This prevents large-N pairs from passing on tiny biases.

3. **N floor for inclusion in FDR:** only test pairs where count(A→B) + count(B→A) ≥ 5.

4. **N floor for forbidden:** expected count ≥ 5 means we have enough data to detect that observed=0 is meaningful.

---

## Registration-trap audit (pre-test)

- **External grounding:** No external corpus is being constructed here; we're refining an existing within-Voynich measurement (C2030). No alternative-class construction risk.
- **Framework-fit:** Closure protocols + LATE-class are existing operational vocabulary. The bigram grammar prediction is *not* in existing vocabulary — it's a new sub-structural claim. NOT framework-echo by construction.
- **N-asymmetry risk:** Bigram counts will vary across pairs; FDR + N floor + effect-size floor address this.
- **Pre-registration locked:** decision rules above were written BEFORE looking at any bigram frequencies.

---

## Scripts to write

| Script | Purpose | Status |
|--------|---------|--------|
| `_closure_bigram_test.py` | Main: extract LATE-LATE bigrams, compute asymmetry + forbidden tests, report results with FDR | Pending |

---

## Cross-references

- **C2030** — Voynich-wide late-term within-line adjacency clustering (+0.036); the measurement this refines
- **C539** — LATE prefix morphological class (positional substrate)
- **C562** — FLOW role structure (function-strength ordering)
- **C886** — MIDDLE asymmetry (constraint symmetric, execution directional) — predicts asymmetry should be measurable
- **C109/C997** — Class-level forbidden transitions (parallel at coarser scope)
- `feedback_within_folio_shuffle_null_first.md` — methodology lineage
- `feedback_framework_as_null.md` — applied to pre-registration design
- `feedback_n_matching_for_within_scribe_comparisons.md` — N-floor discipline

---

## Expected effort

Per memory entry: ~2 hours bounded. Likely 30-60 min actual.

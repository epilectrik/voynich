# PHASE 705: C2041 Terminal-Atom Generalization Test

**Status:** COMPLETE — INDEX-only documentation (no new constraint)
**Date:** 2026-05-19
**Verdict:** Pre-registered Test A passed letter-of-law but expert consultation concluded the aggregate result is mostly inherited C2041 signal, not independent generalization. C2041 sharpened with refinement footnote; no C2042 registered.

---

## Question

Does C2041's `ar → al` directional asymmetry generalize to a broader r-terminal → l-terminal class-level grammar pattern across the full LATE MIDDLE inventory?

LATE inventory partition (locked pre-test):
- r-class: ar, dar, or (ends in -r)
- l-class: al, dal, ol (ends in -l)
- y-class: ary, aly, dary, daly, ory, oly (ends in -y)

---

## Pre-registered design

**Test A:** aggregate r-class → l-class vs l-class → r-class bigrams. Binomial p with FDR correction at < 0.05; aggregate asymmetry effect floor 0.20; N floor 30.

**Test B:** y-class positional preference (r/y and l/y asymmetries with same thresholds).

**Test C:** per-pair direction consistency (≥6 of 9 cross-class pairs same direction).

Pre-registered combined criteria: Tier 2 if A+C both pass; Tier 3 if exactly one; no new constraint if neither.

---

## Results

### Test A — aggregate (PASSED letter-of-law)

| | Count |
|---|---:|
| r-class → l-class | 94 |
| l-class → r-class | 51 |
| Aggregate asymmetry | +0.297 |
| N | 145 |
| p_raw | 0.0004 |
| **p_BH** | **0.0018** |

Decisive significance and effect size above floor.

### Test C — per-pair direction (FAILED 6/9 strict, 5/9 observable)

| r-class | l-class | r→l | l→r | total | asym | direction |
|--------|--------|----:|----:|------:|-----:|-----------|
| ar | al | 39 | 14 | 53 | +0.47 | **r→l** ✓ (C2041) |
| ar | dal | 1 | 0 | 1 | — | r→l (N=1 negligible) |
| ar | ol | 27 | 17 | 44 | +0.23 | **r→l** ✓ |
| dar | al | 0 | 0 | 0 | — | empty |
| dar | dal | 0 | 0 | 0 | — | empty |
| dar | ol | 0 | 0 | 0 | — | empty |
| or | al | 11 | 10 | 21 | +0.05 | r→l (near-symmetric) |
| or | dal | 0 | 0 | 0 | — | empty |
| or | ol | 16 | 10 | 26 | +0.23 | **r→l** ✓ |

5/9 pairs go r→l, 0/9 go l→r, 4 empty (all involve dar/dal — rare in adjacency).

### Test B — y-class (INVALID at morphology level)

Y-class produced 0 observed bigrams with r-class or l-class at N=320. Follow-up position check revealed **only 1 y-class MIDDLE token exists in the entire Currier B P-placement corpus** (ary, N=1). This is a morphology-extraction artifact: tokens with -y terminals (e.g., "ary", "oly") are parsed as MIDDLE=ar/ol + SUFFIX=y, not as MIDDLE=ary/oly. The "y-class" defined by full MIDDLE string match doesn't exist in the parsed token stream. Test B is invalid by morphological definition; the C2030 LATE-class enumeration (ar/ary/aly/al) at MIDDLE level reduces to {ar, al, or, ol, dar, dal} when extracted via Morphology.extract.

---

## Expert consultation outcome

Both experts consulted; sharp methodological split. **Crazy-expert's argument prevailed** for not registering C2042:

1. **Aggregate inherits C2041 signal.** Two of 5 contributing pairs (ar→al, al→ar) are literally C2041's data. Removing ar→al from the aggregate yields r→l=55, l→r=37, asymmetry +0.196 with binomial p ≈ 0.06 — not significant. The "generalization" is largely C2041 re-measured.

2. **or→al near-symmetry (+0.05, N=21) is the load-bearing diagnostic.** If the pattern were truly "r-class → l-class as grammar," all four r×l combinations should show asymmetry. They don't:
   - ar→al = +0.47 ✓
   - ar→ol = +0.23 ✓
   - or→ol = +0.23 ✓
   - **or→al = +0.05** ✗ (near-symmetric, doesn't participate)
   
   The pattern is ar-lexeme-specific (ar prefers preceding al and ol) + a separate "ol-as-late-destination" effect (ol preceded by r-class).

3. **y-class non-participation** is a morphology artifact, not a discovery. Confirmed by `_y_class_position_check.py`.

Expert-advisor took the more cautious-register stance (Tier 3, separate C2042, honor letter of pre-registration). Crazy-expert's substantive critique of overlapping evidence + or→al diagnostic carried the methodological argument.

---

## What gets registered: nothing new; sharpened C2041

C2041's description gets a footnote/extension noting:
- ar → ol (+0.23, N=44) and or → ol (+0.23, N=26) extend the pattern beyond the original ar/al pair
- or → al at +0.05 (N=21) is near-symmetric, indicating the asymmetry is ar-lexeme-specific + ol-as-late-destination, not a class-level r→l grammar
- Aggregate r-class → l-class = 94 vs 51 (asym +0.297, p_BH=0.0018, N=145) but ~37% of signal comes from C2041's ar→al pair alone
- y-class enumeration in C2030 (ary, aly, etc.) doesn't exist at MIDDLE-extraction level; closure-grammar claims about -y terminals need suffix-level (not MIDDLE-level) measurement

This refines C2041 from "LATE-class directional grammar" to "ar-lexeme-specific closure preference + ol-as-late-destination tendency."

---

## Methodology lesson

When testing whether a registered specific finding (C2041 ar→al pair) generalizes to a class-level pattern, **the aggregate test must demonstrate independence from the original signal**. If excluding the original pair doesn't preserve significance, the "generalization" is consistency-checking, not new evidence. Save as `feedback_aggregate_minus_original_independence_test.md`.

---

## Cross-references

- C2041 — the original pair-level asymmetry; gets sharpened
- C2030 — LATE-class within-line clustering (parent measurement)
- C539 — LATE prefix class line-final concentration (positional substrate; relevant to y-class issue)
- C886 — MIDDLE asymmetry prediction
- `feedback_framework_as_null.md` — applied via crazy-expert's overlap argument
- `feedback_n_matching_for_within_scribe_comparisons.md` — sister discipline (control overlapping/imbalanced evidence)

---

## Scripts

| File | Purpose |
|------|---------|
| `scripts/_terminal_atom_test.py` | Main test (Test A/B/C) |
| `scripts/_y_class_position_check.py` | Follow-up verification — y-class is morphology artifact |
| `results/terminal_atom_test.json` | Full main-test output |
| `results/y_class_position_check.json` | Y-class position verification |

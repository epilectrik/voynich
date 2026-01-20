# Phase: A_INTERNAL_STRATIFICATION

**Date:** 2026-01-20
**Status:** COMPLETE
**Outcome:** C498 added (Tier 2)

---

## Purpose

Investigate whether A-exclusive MIDDLEs (those appearing in Currier A but never in Currier B) have distinct structural roles within Currier A itself.

---

## Key Finding

**Currier A has two vocabulary tracks:**

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating** | 268 (43.4%) | Standard prefixes/suffixes, broad folio spread (7.96) | Flow through A→AZC→B |
| **Registry-internal** | 349 (56.6%) | ct-prefix 5.1×, suffix-less 3×, folio-localized (1.34) | Stay in A registry |

---

## Evidence

### Morphological Signature (A-exclusive vs A/B-shared)

| Metric | A-exclusive | A/B-shared | Significance |
|--------|-------------|------------|--------------|
| ct-prefix | 5.1× enriched | baseline | Significant |
| Suffix-less | 3× enriched | baseline | Significant |
| Folio spread | 1.34 folios | 7.96 folios | Significant (KS=0.480) |
| AZC presence | 8.9% | 57.5% | Significant |

### Corrected Test Results (after data bug fix)

| Test | Finding | Significant? |
|------|---------|--------------|
| Position (opener) | 18.8% vs 17.1% | NO |
| Entry composition | 25.5% MIXED (matches random) | NO |
| Folio spread | 1.34 vs 7.96 folios | **YES** |
| Morphology (PREFIX) | ct- 5.1× enriched | **YES** |
| Morphology (SUFFIX) | suffix-less 3× enriched | **YES** |
| AZC presence | 8.9% vs 57.5% | **YES** |

### Falsified Hypotheses

1. **Entry-type marker hypothesis: FALSIFIED**
   - Initial findings (98.8% opener rate, 0% mixing) were artifacts of a data bug
   - Bug: Script grouped by (word, folio) instead of (folio, line_number)
   - Corrected data: Opener rate 18.8% vs 17.1% (not significant), 25.5% MIXED entries (matches random)
   - A-exclusive tokens do NOT mark entry boundaries

2. **AZC-terminal bifurcation hypothesis: FALSIFIED**
   - 31 A-exclusive MIDDLEs appear in AZC but never reach B
   - Verification checks:
     - C304 overlap: FAIL (only 77.6% in AZC-unique)
     - C300 NA consistent: FAIL (1 token classified B by transcriber F)
     - Placement legality: PASS (2.35× peripheral enrichment, but 75% in legality zones)
     - Transcriber robustness: PASS (68.1% confirmed)
   - **Conclusion:** The 8.9% residue is interface noise from systems sharing the same alphabet, not a distinct stratum

---

## Interpretation

Registry-internal MIDDLEs encode **within-category fine distinctions** that matter for A-registry organization but don't propagate because they are **below the granularity threshold for execution**.

The morphological signature explains the mechanism:
- **ct-prefix** (C492): Only legal in P-zone AZC (0% in C/S-zones) → morphologically incompatible with most AZC positions
- **Suffix-less**: No downstream execution routing required → these MIDDLEs terminate in A
- **Folio-localized**: Hyper-specialized discriminators for local registry organization

---

## Constraint Added

### C498 - Registry-Internal Vocabulary Track
**Tier:** 2 | **Scope:** A

A-exclusive MIDDLEs (56.6%, 349 types) form a morphologically distinct registry-internal vocabulary track that does not propagate through the A→AZC→B pipeline. They encode within-category fine distinctions for A-registry navigation that don't propagate to B execution.

---

## Data Bug Documentation

**Critical bug discovered and fixed during phase:**

The original `prepare_middle_classes.py` script used raw line splitting with wrong column indices:
- `parts[1]` was assumed to be folio but was actually `complex_word`
- This caused grouping by (word, folio) instead of (folio, line_number)
- Result: 7,048 artificial single-token "entries" instead of 1,571 real lines

**Fix:** Changed to `csv.DictReader` to read columns by name instead of index.

All findings after the fix are based on correct data.

---

## Files Modified

| File | Change |
|------|--------|
| `context/CLAIMS/currier_a.md` | Added C498 |
| `context/CLAIMS/INDEX.md` | Added C498 entry |
| `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` | Added two_track_structure to middle section |
| `context/MODEL_CONTEXT.md` | Added Section VII subsection |
| `context/SYSTEM/CHANGELOG.md` | Phase entry |

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C293 (MIDDLE primary discriminator) | Refined: Both tracks discriminate; scope differs |
| C475 (95.7% incompatibility) | Explained: Cross-track incompatibility is part of the 95.7% |
| C476 (hub rationing) | Instantiated: Registry-internal track IS hub-rationing in action |
| C383 (global type system) | Consistent: Same morphology, different usage pattern |
| C492 (ct phase-exclusive) | Connected: ct-prefix enrichment explains AZC incompatibility |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `prepare_middle_classes.py` | Extract A-exclusive vs A/B-shared MIDDLEs (FIXED) |
| `run_all_tests.py` | Run 8 stratification tests |
| `analyze_azc_terminal.py` | Analyze 31 AZC-terminal MIDDLEs |
| `verify_azc_terminal.py` | Run 4 verification checks |
| `verify_h_filtering.py` | Discovered data bug |
| `debug_data_loading.py` | Diagnosed column index mismatch |

---

## Data Outputs

| File | Contents |
|------|----------|
| `results/middle_classes.json` | MIDDLE classification data |
| `results/stratification_tests.json` | Test results |
| `results/azc_terminal_analysis.json` | AZC-terminal analysis |
| `results/azc_terminal_verification.json` | Verification check results |

# MIDDLE_COVERAGE_ANALYSIS Phase

**Date:** 2026-02-04
**Status:** COMPLETE
**Verdict:** PRODUCTIVE - Major coverage improvement

---

## Summary

Systematic analysis of MIDDLE coverage in Currier B, discovering the **Vowel Primitive Suffix Saturation** pattern that explains 38% of previously unmapped tokens.

---

## Key Findings

### 1. Vowel Primitive Suffix Saturation (C906, F-BRU-014)

**Discovery:** Vowel MIDDLEs (a, e, o) exhibit suffix saturation - when combined with END-class atoms (y, dy, l, r, in, iin), the resulting compound MIDDLE suppresses additional suffixation.

**Evidence:**
| MIDDLE | Takes Additional Suffix |
|--------|------------------------|
| `e` (base) | 98.3% |
| `edy` (compound) | 0.4% |
| `o` (base) | 78.5% |
| `ol` (compound) | 3.3% |

**Impact:** Operational coverage improved from 19.1% to 57.3% (+38.2%).

### 2. Coverage Model

Final Currier B coverage: **73.1%**

| Category | Tokens | Coverage |
|----------|--------|----------|
| PREP tier | 331 | 1.4% |
| CORE tier (k, t, e) | 3,500 | 15.2% |
| EXT tier (ke, kch) | 569 | 2.5% |
| e-absorbed | 4,585 | 19.9% |
| o-absorbed | 1,195 | 5.2% |
| a-absorbed | 2,612 | 11.3% |
| Vowel cores (a, o) | 439 | 1.9% |
| **Operational subtotal** | **13,231** | **57.3%** |
| Primary infrastructure | 2,738 | 11.9% |
| Secondary infrastructure (-hy) | 910 | 3.9% |
| **Total explained** | **16,877** | **73.1%** |

### 3. -hy Secondary Infrastructure (C907)

**Discovery:** Tokens with -hy suffix (chckhy, shckhy, etc.) form formulaic constructions with consonant cluster MIDDLEs.

**Tested Hypothesis:** -hy tokens are "procedural connectors" marking boundaries.

**Result:** FALSIFIED - No enrichment for boundary crossing (0.99x baseline).

**Status:** Morphologically characterized, functionally unknown.

### 4. k-Variant Analysis

**Discovery:** ck, eck, ek MIDDLEs are NOT absorption patterns like vowel cores. They're specialized constructions with specific suffixes (-hy, -y) and prefixes (ch-, sh-).

---

## Constraints Added

| Constraint | Tier | Status |
|------------|------|--------|
| C906 - Vowel Primitive Suffix Saturation | 2 | CLOSED |
| C907 - -hy Consonant Cluster Infrastructure | 4 | OPEN |

## Fits Added

| Fit | Tier | Result |
|-----|------|--------|
| F-BRU-014 - Vowel Primitive Suffix Saturation | F2 | CONFIRMED |

---

## Methodology

1. Computed suffix attachment rates for base vs compound MIDDLEs
2. Identified vowel primitives (a, e, o) as the cores showing absorption
3. Validated with PREFIX distribution comparison
4. Tested -hy tokens as potential procedural connectors (falsified)
5. Analyzed k-variants (distinct from absorption pattern)

---

## Scripts

| Script | Purpose |
|--------|---------|
| `compound_middle_decomposition.py` | e-family absorption analysis |
| `core_suffix_comparison.py` | Cross-MIDDLE suffix rate comparison |
| `ol_or_absorption_test.py` | o-family absorption analysis |
| `final_coverage_update.py` | Final coverage calculation |
| `k_variant_analysis.py` | k-variant (ck, eck, ek) analysis |
| `hy_suffix_analysis.py` | -hy suffix pattern analysis |
| `hy_connector_test.py` | Procedural connector hypothesis test |
| `unmapped_inventory.py` | Token coverage inventory |
| `unknown_middle_analysis.py` | l, r, d, iin analysis |

---

## Related Documentation

- `context/CLAIMS/C906_vowel_primitive_suffix_saturation.md`
- `context/CLAIMS/C907_hy_consonant_cluster_infrastructure.md`
- `context/MODEL_FITS/fits_brunschwig.md` (F-BRU-014)

---

## Next Steps

Remaining unknown tokens (26.9%):
1. Suffix-as-MIDDLE (dy, y) - ~4.5%
2. Prefix-as-MIDDLE (ch, sh) - ~2.0%
3. k-variants (ek, ckh, etc.) - ~2.0%
4. Misc compounds - ~18%

Potential investigations:
- Why do dy, y appear as standalone MIDDLEs?
- What do prefix-only tokens (ch, sh) encode?
- Is there a fourth tier of "notation markers"?

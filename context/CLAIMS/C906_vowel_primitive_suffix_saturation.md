# C906: Vowel Primitive Suffix Saturation

**Tier:** 2 | **Scope:** GLOBAL | **Status:** CLOSED

---

## Statement

Vowel primitives (a, e, o) exhibit **suffix saturation**: when combined with END-class atoms (y, dy, l, r, in, iin, am), the resulting compound MIDDLE is morphologically "closed" and suppresses additional suffixation. Tokens with compound MIDDLEs (e.g., `edy`, `ol`, `aiin`) are notational variants of base vowel + suffix, not distinct operations.

---

## Evidence

### Suffix Attachment Rates

| MIDDLE | Takes Additional Suffix | Sample Size |
|--------|------------------------|-------------|
| `e` | 98.3% | 845 |
| `edy` | 0.4% | 1,763 |
| `ey` | 0.7% | 769 |
| `eey` | 0.0% | 615 |
| `o` | 78.5% | 376 |
| `ol` | 3.3% | 759 |
| `or` | 2.8% | 436 |
| `a` | ~98% | 63 |
| `al` | 7.1% | 520 |
| `ar` | 5.5% | 670 |
| `ain` | 0.5% | 419 |
| `aiin` | 0.5% | 831 |

### Interpretation

The pattern `okeedy` (PREFIX=ok, MIDDLE=e, SUFFIX=edy) and `okedy` (PREFIX=ok, MIDDLE=edy, SUFFIX=none) encode the **same operation**. The suffix has been "absorbed" into the MIDDLE string as a writing convention.

### Coverage Impact

- Before absorption model: 19.1% operational coverage
- After absorption model: 57.3% operational coverage
- Tokens explained: ~8,800 previously "unmapped" tokens

---

## Absorbed Forms by Vowel Core

### e-family
- Core: `e` (845 tokens)
- Absorbed: `edy` (1,763), `ey` (769), `eey` (615), `ed` (377), `eo` (340), `eol` (281), `ee` (146), `eeo` (130)
- Total e-family: 5,266 tokens (22.8% of B)

### o-family
- Core: `o` (376 tokens)
- Absorbed: `ol` (759), `or` (436)
- Total o-family: 1,571 tokens (6.8% of B)

### a-family
- Core: `a` (63 tokens)
- Absorbed: `al` (520), `ar` (670), `ain` (419), `aiin` (831), `am` (172)
- Total a-family: 2,675 tokens (11.6% of B)

---

## Relationship to Existing Constraints

- **Extends C267** (Tokens are COMPOSITIONAL): Reveals sub-MIDDLE compositional layer
- **Extends C510-C513** (Sub-Component Grammar): The absorbed suffixes are exactly the END-class atoms from C512.a
- **Consistent with C540** (Kernel Primitives Are Bound Morphemes): Vowel cores behave similarly - they almost always bind with something
- **Consistent with C383** (Global Morphological Type System): Same atom functions identically whether written as suffix or MIDDLE-terminal

---

## Provenance

- **Phase:** MIDDLE_COVERAGE_ANALYSIS (2026-02-04)
- **Method:** Comparative suffix attachment rates across MIDDLEs
- **Key Observation:** Compound MIDDLEs show 95%+ "no additional suffix" rate, confirming absorption

---

## Related Constraints

- C267 (Compositional Morphology)
- C510-C513 (Sub-Component Grammar)
- C540 (Kernel Primitives Are Bound Morphemes)
- C376 (Suffix Kernel Dichotomy)

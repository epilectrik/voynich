# C570: AX PREFIX Derivability

**Tier:** 2 (Structural Inference)
**Phase:** AX_FUNCTIONAL_ANATOMY
**Scope:** Currier B grammar / morphology-role correspondence
**Status:** VALIDATED (re-verified 2026-01-26 with 19 AX classes)

## Claim

AX class membership is 87.1% predictable from PREFIX alone. PREFIX functions as a role selector: the same MIDDLE becomes AX or operational depending on which PREFIX it carries.

## Evidence

### Binary Classification (AX vs non-AX)
- Accuracy: 87.1%
- Precision: 0.823
- Recall: 0.941
- F1: 0.878

### PREFIX Categories
- 22 AX-exclusive prefixes: ct, dch, do, fch, ka, kch, ke, ko, lch, lk, lsh, or, pch, po, rch, sa, so, ta, tch, te, to, yk
- 3 non-AX-exclusive prefixes: al, ar, qo
- 7 ambiguous prefixes: NONE, ch, da, ok, ol, ot, sh

### Main Violations
- AX_INIT tokens (classes 4, 5, 6) use ch/sh prefixes with articulators (ychedy, dshey, lcheey)
- These are predicted as EN by prefix-only classifier but are AX due to articulator presence
- FQ tokens with ok/ot prefixes (classes 13, 14: okaiin, okeey, otaiin) predicted as AX — Class 14's 707 tokens are the primary source of false positives

### PREFIX Differentiation of Shared MIDDLEs
- 41 MIDDLEs shared between AX and operational roles
- 24/41 (58.5%) fully PREFIX-differentiated (zero prefix overlap)
- 8/41 more ARTICULATOR-differentiated
- Total 32/41 (78%) differentiated by morphological form

## Interpretation

PREFIX is the primary role selector in Currier B. The MIDDLE carries the material identity from the A->AZC->B pipeline; the PREFIX determines whether that material is deployed as an operation (ch/sh/qo = EN) or as scaffolding (ok/ot = AX_MED, bare = AX_FINAL, articulated ch/sh = AX_INIT).

The 12.9% of tokens that violate prefix-based prediction are concentrated in AX_INIT (articulated variants of operational prefixes) and FQ (ok/ot-prefixed frequent operators, especially Class 14 with 707 tokens). This suggests a secondary role for articulators in AX_INIT assignment.

## Dependencies

- C567: AX-operational MIDDLE sharing
- C564: AX morphological-positional correspondence
- C235: 8 prefix markers (mutual exclusion)

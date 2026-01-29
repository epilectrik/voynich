# C726: Role-Position Accessibility Interaction

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** A-B

## Finding

The aggregate within-line accessibility arch (C722) decomposes into **role-specific trajectories** that are NOT unanimous in direction:

| Role | SETUP | WORK | CLOSE | Gradient (CLOSE-SETUP) |
|------|-------|------|-------|------------------------|
| CC | 0.423 | 0.486 | 0.499 | +0.076 |
| EN | 0.396 | 0.379 | 0.366 | -0.030 |
| FL | 0.192 | 0.223 | 0.191 | -0.001 |
| FQ | 0.587 | 0.550 | 0.545 | -0.042 |
| AX | 0.216 | 0.227 | 0.253 | +0.037 |
| UN | 0.131 | 0.113 | 0.110 | -0.021 |

**CC and AX increase** accessibility from SETUP to CLOSE; **EN, FQ, and UN decrease**. Each pattern is explained by morphological composition shifts at different line positions:

- CC increases because daiin (1.8% accessible) dominates initial positions (C590) while ol (98.2%) is medial/final.
- AX increases because AX_INIT tokens carry articulators (C564: 17.5%, B-enriched) while AX_FINAL is prefix-light (60.9%, more accessible).
- EN decreases because late-line EN uses more specialized B-enriched suffix combinations.
- FQ decreases because Class 23 (boundary specialist, C597, 29.8% final rate) has morphologically minimal B-specific tokens.

## Implication

The "SETUP is less accessible" generalization (C722) holds at the aggregate level but is not a universal per-role truth. Different roles use line positions differently in their accessibility profiles. The non-unanimity is structurally explained by the morphological composition of each role at each position, not by any cross-system signaling.

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (T5)
- Extends: C722 (within-line arch), C556 (positional role grammar)
- Explained by: C590 (CC positional dichotomy), C564 (AX morphological profiles), C597 (FQ Class 23)

# C723: Role Accessibility Hierarchy

**Status:** VALIDATED | **Tier:** 2 | **Phase:** B_LEGALITY_GRADIENT | **Scope:** A-B

## Finding

Classified B token roles show a stable accessibility ordering under A-folio filtering (KW H=50.9, p=2.4e-10):

| Role | Mean Accessibility | N Types | Character |
|------|-------------------|---------|-----------|
| FQ (Frequent) | 0.582 | 33 | Most shared |
| EN (Energy) | 0.382 | 173 | Operational core |
| AX (Auxiliary) | 0.321 | 232 | Structural scaffold |
| CC (Core Control) | 0.261 | 11 | Control triggers |
| FL (Flow) | 0.085 | 19 | B-autonomous termination |
| UN (Unclassified) | 0.098 | 4421 | Overwhelmingly B-exclusive |

FL's extremely low accessibility (8.5%) confirms that B's flow control and termination vocabulary is autonomously determined. FL manages hazard transitions (C586: 4.5x hazard initiation bias) — this function cannot depend on external authorization. CC's low accessibility is driven by daiin (1.8%) pulling down the average while ol (98.2%) is near-universal.

## Implication

The role hierarchy reveals a functional stratification: shared operational vocabulary (FQ, EN) forms the A-accessible core, while grammatical infrastructure (FL, CC, UN) is B-internal. A's authorization reaches B's "what" (operational content) but not B's "how" (grammar and flow control).

## Key Numbers

| Metric | Value |
|--------|-------|
| FQ mean accessibility | 0.582 |
| EN mean accessibility | 0.382 |
| AX mean accessibility | 0.321 |
| CC mean accessibility | 0.261 |
| FL mean accessibility | 0.085 |
| UN mean accessibility | 0.098 |
| KW H (classified roles) | 50.9 (p=2.4e-10) |
| Zero-access rate: FL | 26.3% (5/19) |
| Zero-access rate: UN | 37.8% (1671/4421) |

## Provenance

- Script: `phases/B_LEGALITY_GRADIENT/scripts/legality_gradient.py` (T2)
- Extends: C556 (positional role grammar), C562 (FL final-biased), C575 (EN 100% PP)
- Strengthens: C586 (FL hazard-source), C557 (daiin B-autonomous deployment)

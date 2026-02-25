# C1281: TRANSITION Anti-Escape is PREFIX-Independent

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

TRANSITION's anti-escape correlation (rho=-0.582, p<0.001) does NOT collapse when controlling for ch/sh PREFIX composition (partial rho=-0.586, p<0.001). TRANSITION suppresses escape through a mechanism independent of PREFIX routing. TRANSITION ch/sh rate (25.7%) is indistinguishable from baseline (25.1%). TRANSITION hazard MIDDLE rate is moderate (24.2%) — not hazard-mediated either.

## Architecture

- **Asymmetric escape architecture.** C1277 shows escape is enabled via PREFIX routing (THERMAL→qo). C1281 shows escape is suppressed via a PREFIX-independent, category-intrinsic mechanism. The two directions use fundamentally different mechanisms.
- **Not hazard-mediated.** TRANSITION's hazard MIDDLE rate (24.2%) is unremarkable — FLOW (66.1%) and CONTAINMENT (61.4%) are the hazard categories (C1280). TRANSITION doesn't suppress escape by creating dangerous transitions.
- **TRANSITION ch/sh rate is baseline.** 25.7% vs 25.1%. TRANSITION MIDDLEs don't preferentially enter any PREFIX lane. Their anti-escape effect is something the MIDDLE itself carries, not how it gets prefixed.
- **Open mechanism.** What TRANSITION does to suppress escape remains unknown. It's real (rho=-0.586 after control), strong, and operates at the MIDDLE level independent of PREFIX routing or hazard topology.

## Key Findings

| Metric | Value |
|--------|-------|
| TRANSITION-escape rho | -0.582 |
| Partial (controlling ch/sh) | -0.586 (p<0.001) |
| Mediation collapsed | No |
| TRANSITION ch/sh rate | 25.7% |
| Baseline ch/sh rate | 25.1% |
| TRANSITION hazard MIDDLE rate | 24.2% |

## Provenance

- Complements C1277 (THERMAL escape PREFIX-mediated) -- asymmetric architecture
- Extends C1274 (TRANSITION rho=-0.598) with mediation analysis
- Tests C601 (EN_CHSH hazard sub-group) -- TRANSITION is NOT ch/sh-lane enriched

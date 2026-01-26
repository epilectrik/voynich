# SUB_ROLE_INTERACTION Phase

**Date:** 2026-01-26
**Goal:** Map how the internal sub-groups of each role interact across role boundaries, connecting C550 (role-level transitions) to the anatomy phases (EN, FQ, FL, AX, CC sub-groups).
**Status:** COMPLETE

## Key Findings

### Cross-Boundary Structure is Strong (C598)

8/10 cross-role pairs show significant sub-group routing (raw p<0.05), 5/10 survive Bonferroni correction. Sub-group structure is visible across role boundaries.

### FQ Connector Routes Exclusively to CHSH (C598)

The strongest cross-boundary signal: FQ_CONN (Class 9) feeds EN_CHSH at 1.41x but avoids EN_QO at 0.16x. This avoidance holds across all 4 REGIMEs (0.00-0.31x). The or/aiin bigram (C561) connects almost exclusively to ch/sh-prefixed ENERGY tokens, not qo-prefixed ones.

### CC Sub-Groups Are Differentiated Triggers (C600)

CC sub-group follower independence: chi2=129.2, p=9.6e-21.

| CC Sub-Group | EN_QO | EN_CHSH | Pattern |
|-------------|-------|---------|---------|
| CC_DAIIN (daiin) | 0.18x | 1.60x | Triggers CHSH |
| CC_OL (ol) | 0.18x | 1.74x | Triggers CHSH |
| CC_OL_D (ol-derived) | 1.39x | 0.77x | Triggers QO |

daiin and ol both strongly avoid QO and trigger CHSH. CC_OL_D (Class 17, C560) is the only CC class that preferentially routes to QO — consistent with its distinct morphological origin (ol-derived compounds).

### AX Scaffolding Routes Differently by Sub-Position (C599)

AX routing independence: chi2=48.3, p=3.9e-4.

| AX Sub-Group | EN_QO | EN_CHSH | FQ_CONN | Key Pattern |
|-------------|-------|---------|---------|-------------|
| AX_INIT | 0.96x | 1.05x | 1.23x | Neutral, slight FQ_CONN preference |
| AX_MED | 1.10x | 0.96x | 0.81x | Slight QO preference, avoids CONN |
| AX_FINAL | 0.59x | 1.09x | 1.31x | Avoids QO, feeds FQ_CONN |

AX_FINAL avoids EN_QO (0.59x) and preferentially feeds FQ_CONN (1.31x). AX is not a neutral frame — sub-position predicts what operational sub-group follows.

### Hazards Concentrate in 3 Sub-Groups (C601)

All 19 hazard events come from exactly 3 source sub-groups:
- FL_HAZ: 9 events (47%) — all from hazard FL classes
- EN_CHSH: 5 events (26%) — all from ch/sh-prefixed ENERGY
- FQ_CONN: 5 events (26%) — all from Class 9 (connector)

Target distribution: EN_CHSH absorbs 58% (11/19) of hazard targets. QO is never a hazard source or target. Safe sub-groups (FL_SAFE, FQ_PAIR, FQ_CLOSER) never participate.

### REGIME Conditioning is Selective (C602)

Homogeneity tests across REGIMEs:

| Pair | chi2 | p | Verdict |
|------|------|---|---------|
| EN->FQ | 50.7 | 9.2e-6 | REGIME-DEPENDENT |
| FQ->EN | 31.4 | 7.8e-3 | REGIME-DEPENDENT |
| AX->EN | 30.0 | 1.2e-2 | REGIME-DEPENDENT |
| CC->EN | 26.5 | 3.3e-2 | REGIME-DEPENDENT |
| AX->FQ | 16.7 | 8.6e-1 | REGIME-INDEPENDENT |

4/5 focus pairs are REGIME-dependent. AX->FQ routing is the exception — it's REGIME-independent (the INIT->CONN preference holds regardless of thermal/flow context).

### Context Classifier

Sub-group prediction from context: 30.8% accuracy (vs 24.7% majority baseline, +6.1pp). Role-level: 48.1% (vs 44.9%, +3.1pp). Sub-group adds 2.9pp over role-level prediction — modest but measurable cross-boundary context signal at the sub-group level.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| sub_role_transitions.py | Cross-boundary sub-group matrices, enrichment, chi2 | sub_role_transitions.json |
| sub_role_conditioning.py | REGIME/position/trigger conditioning, AX flow, hazards | sub_role_conditioning.json |

## New Constraints

| # | Name | Key Finding |
|---|------|-------------|
| C598 | Cross-Boundary Sub-Group Structure | 8/10 significant; FQ_CONN->EN_CHSH 1.41x, FQ_CONN->EN_QO 0.16x |
| C599 | AX Scaffolding Routing | chi2=48.3 p=3.9e-4; AX_FINAL avoids QO (0.59x), feeds FQ_CONN (1.31x) |
| C600 | CC Trigger Sub-Group Selectivity | chi2=129.2 p=9.6e-21; daiin/ol trigger CHSH, ol-derived triggers QO |
| C601 | Hazard Sub-Group Concentration | 100% from FL_HAZ/EN_CHSH/FQ_CONN; QO never participates; EN_CHSH absorbs 58% |
| C602 | REGIME-Conditioned Sub-Role Grammar | 4/5 pairs REGIME-dependent; AX->FQ REGIME-independent |

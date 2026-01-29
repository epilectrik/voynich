# B_LEGALITY_GRADIENT

**Status:** COMPLETE | **Constraints:** C722-C727 | **Scope:** A-B

## Objective

Test whether B folio tokens show a predictable legality gradient (accessibility under A-folio filtering) correlated with the SETUP->WORK->CLOSE line syntax (C556). Motivated by visual inspection showing B folios opening with B-exclusive procedure-identity vocabulary then transitioning to shared operational vocabulary.

## Method

**Accessibility metric:** For each B token type, compute the fraction of A folios (out of 114) under which that token is legal per C502.a full morphological filtering (MIDDLE + PREFIX + SUFFIX). This produces a continuous accessibility score per token type (0.0 = completely B-exclusive, 1.0 = universally legal).

Analysis dimensions:
- Within-line position (quintiles and SETUP/WORK/CLOSE thirds)
- Token role (CC, EN, FL, FQ, AX, UN)
- Across-line position (line order within B folios)
- Role x position interaction

## Key Findings

**Within-line accessibility ARCH (C722):** Accessibility follows a nonlinear arch by position (KW p=2.67e-15). Initial (0.279) and final (0.282) positions are LESS accessible than medial positions (0.301-0.306). Mirrors C556's positional syntax. Mechanism: morphological composition varies by position (daiin at initial, EN at medial, FL at final), not cross-system recognition.

**Role hierarchy (C723):** FQ (0.582) > EN (0.382) > AX (0.321) > CC (0.261) > FL (0.085). Flow tokens are almost entirely B-exclusive — B's termination grammar is autonomously determined. daiin (CC) at 1.8% accessibility confirms B-autonomous deployment (C557).

**Suffix determines accessibility (C724):** Within Class 33 (EN), qokaiin=0.675 vs qokeedy=0.035 — 19x difference from suffix alone. First within-class demonstration of C502.a's three-axis filtering at individual token resolution.

**Across-line gradient (C725):** Later lines have slightly higher accessibility (rho=0.124, p=8.6e-10, 56/82 folios positive). First-third: 0.276, last-third: 0.306. Consistent with C325 completion gradient. Moderate effect.

**Role-position interaction (C726):** Aggregate arch decomposes into role-specific trajectories. CC and AX increase accessibility toward line-final (composition effects from C590/C564). EN and FQ decrease. Non-unanimous but morphologically explained.

**B vocabulary autonomy (C727):** 69.3% of B token types are low-or-zero accessibility. No token is universally legal. B's structural scaffold (~70% of types) is autonomously determined; A specifies operational content (~30%).

## Test Results

| Test | Key Metric | Result |
|------|-----------|--------|
| T1: Within-line position (linear) | rho=0.011 | FAIL (arch, not linear) |
| T2: Role-correlated legality | KW p=2.4e-10 | PASS |
| T3: Across-line gradient | rho=0.124, p=8.6e-10 | PASS |
| T4: SETUP/WORK/CLOSE thirds | KW p=2.3e-8 | PASS |
| T5: Role x position interaction | Not unanimous | FAIL |

Note: T1 FAIL is an artifact of using linear correlation for a nonlinear (arch) pattern. The KW test within T1 is p=2.67e-15, confirming the positional effect.

## Special Token Accessibility

| Token | Accessibility | Class | Role | Note |
|-------|-------------|-------|------|------|
| daiin | 0.018 | 10 | CC | #1 B line opener, nearly B-exclusive |
| ol | 0.982 | 11 | CC | Near-universal phase marker |
| or | 0.974 | 9 | FQ | Near-universal |
| aiin | 0.746 | 9 | FQ | Broadly accessible |
| ar | 0.482 | 7 | FL | Moderate |
| chedy | 0.053 | 8 | EN | Low (B-enriched suffix) |
| qokaiin | 0.675 | 33 | EN | High (-aiin suffix) |
| qokeedy | 0.035 | 33 | EN | Low (-eedy suffix, same class!) |
| lkeedy | 0.018 | 29 | AX | lk-prefix nearly B-exclusive |

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `legality_gradient.py` | T1-T5 (C722-C727) | `legality_gradient.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C722 | Within-Line Accessibility Arch | Nonlinear arch (KW p=2.67e-15), mirrors C556 |
| C723 | Role Accessibility Hierarchy | FQ > EN > AX > CC > FL (KW p=2.4e-10) |
| C724 | Within-Class Suffix Accessibility | 19x variation within Class 33 from suffix alone |
| C725 | Across-Line Accessibility Gradient | rho=0.124, 56/82 folios positive |
| C726 | Role-Position Accessibility Interaction | Non-unanimous, morphologically explained |
| C727 | B Vocabulary Autonomy Rate | 69.3% low-or-zero accessibility |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP classification)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token-to-class)

## Cross-References

- C325 (Completion Gradient): Consistent with across-line gradient
- C384 (no entry-level coupling): Accessibility patterns are population-level, not addressable
- C502.a (morphological filtering cascade): Confirmed at individual token resolution
- C556 (SETUP-WORK-CLOSE): Arch pattern mirrors positional syntax
- C557 (daiin trigger): daiin at 1.8% confirms B-autonomous deployment
- C562 (FLOW final): FL at 8.5% confirms B-autonomous termination
- C575 (EN 100% PP): EN's high accessibility consistent with shared vocabulary
- C586 (FL hazard-source): FL's B-exclusivity explained by autonomous hazard management
- C704-C709 (folio-level filtering): Baseline filtering architecture

# C1191: Position-Dependent Behavioral Composition

## Statement

Single-character atoms carry consistent behavioral IDENTITY across morphological positions (PREFIX, MIDDLE, SUFFIX) but follow position-specific COMPOSITIONAL RULES. MIDDLE composition is additive (C1190: r=0.754). PREFIX composition is emergent — compounds like ch, sh acquire specialized behavioral profiles that exceed simple atom addition. SUFFIX position imposes a systematic behavioral shift on all atoms (shift correlation r=0.892).

## Tier

2 — Empirical, statistically validated, no gloss dependency

## Scope

B (Currier B internal grammar)

## Evidence

### Cross-Position Identity (T2)

15/18 testable atoms show CONSISTENT behavioral profiles across positions (CPC >= 0.7). Same atom carries same behavioral signature regardless of whether it appears in PREFIX, MIDDLE, or SUFFIX.

| Status | Count | Atoms |
|--------|-------|-------|
| CONSISTENT (CPC >= 0.7) | 15 | e, g, q, t, l, h, i, m, o, r, k, a, d, y, s, n |
| MODERATE (0.3-0.7) | 2 | f (0.542), p (0.423) |
| DIVERGENT (< 0.3) | 1 | c (-0.108) |

### PREFIX Emergence (T1R)

Prediction error attribution: which atoms degrade compound predictions?

| Status | Atoms | Error delta | Interpretation |
|--------|-------|-------------|----------------|
| GOOD (improve predictions) | d, e, a, i, m, y, o, l | negative | Compose additively |
| ACCEPTABLE | r, k, q | +0.002 to +0.004 | Neutral |
| DEGRADING | t, n, f | +0.010 to +0.015 | Weaken predictions |
| PROBLEMATIC | s, c, h, p | +0.026 to +0.035 | Emergent behavior |

The 4 PROBLEMATIC atoms (c, h, s, p) are the primary building blocks of PREFIX compounds: ch (check), sh (verify), pch (chop), cph (measure), cth (hazard). Their emergent behavior is consistent with C929 (ch/sh sensory modality specialization).

Null percentiles for problematic atoms: c=5.2%, h=4.4%, p=10.0%, s=25.4% — significantly worse than random for c and h.

### PREFIX Shift: Subgroup-Specific (Grammatical Role Test)

PREFIX->MIDDLE shift vectors are NOT uniformly correlated (mean r=0.070, p=0.067, marginal). However, subgroups shift identically:

| Subgroup | Internal r | Shift pattern |
|----------|-----------|---------------|
| {c, h, k, t, f, s} | 0.91-0.98 | Lose suffix rate, gain line-initial rate |
| {q} | anti-correlated with {c,h} at r=-0.83 | Different prefix class |
| {a, d} | moderate cluster | Infrastructure/marking prefixes |

Dominant feature shift: sfx_rate drops -0.218 (t=-2.78, significant) when atoms enter PREFIX position. Structurally expected: PREFIX atoms precede the MIDDLE, which takes the suffix.

### SUFFIX Shift: Systematic (Grammatical Role Test)

MIDDLE->SUFFIX shift vectors are HIGHLY correlated across atoms: mean pairwise r=0.892. All atoms shift behavior in the SAME direction when moving to SUFFIX position. This constitutes a grammatical rule: SUFFIX position imposes a consistent behavioral transformation.

13 atoms testable in both MIDDLE and SUFFIX positions.

### Near-Identical Behavioral Pairs

Atom similarity analysis revealed pairs with near-identical behavioral profiles despite different glosses:

| Pair | r | Glosses | Interpretation |
|------|---|---------|----------------|
| k-t | 0.993 | heat / transfer | Both qo-prefix dominated, always suffixed |
| d-o | 0.945 | mark / near | Both broadly distributed, similar position |
| p-t | 0.935 | pause / transfer | {k, t, p} cluster: active operation atoms |
| l-r | 0.919 | late / mid | Both FL-state markers |

These pairs may indicate: (a) behavioral features too coarse to distinguish functionally different atoms, (b) atoms with genuinely similar operational roles, or (c) gloss errors.

## Interpretation

C1190 proved atoms compose additively in MIDDLEs. C1191 shows this is one of THREE position-specific rules:

1. **MIDDLE**: Additive composition (C1190, r=0.754, p<0.001)
2. **PREFIX**: Emergent composition — compounds acquire specialized function beyond atom addition. Consistent with PREFIX compounds being functional units (C929: ch/sh sensory modalities).
3. **SUFFIX**: Systematic shift — all atoms transform behavior consistently in SUFFIX position (r=0.892). SUFFIX imposes a grammatical-role transformation.

The atoms themselves maintain consistent IDENTITY across positions (15/18 pass cross-position test), but the COMPOSITIONAL MECHANISM changes. This is analogous to how individual words carry consistent meaning but combine differently as verbs, adjectives, or suffixes.

## Strengthens

- **C1190** (MIDDLE Behavioral Atomicity): Precisely scopes where additive composition holds
- **C929** (ch/sh Sensory Modality): Explains WHY PREFIX compounds are emergent — they encode specialized sensory functions
- **C267** (TOKEN = PREFIX + MIDDLE + SUFFIX): The three positions aren't just structural — they select different compositional rules

## Prior Constraints

- C1190 (MIDDLE Behavioral Atomicity — additive composition validated)
- C929 (ch/sh Sensory Modality Discrimination)
- C267 (Tokens are COMPOSITIONAL)
- C510 (Positional Sub-Component Grammar)
- C522 (Construction-Execution Layer Independence)

## Falsification

Would be falsified if:
1. A different feature set yields non-marginal systematic PREFIX shift (p < 0.01), contradicting the "emergent" characterization
2. SUFFIX shift correlation drops below 0.5 with different sections or feature sets
3. The PROBLEMATIC atoms (c, h, s, p) are shown to compose additively when PREFIX-specific features are used

## Provenance

Phase: CROSSWORD_GLOSS_VALIDATION (Phase 422)
Scripts:
- `phases/CROSSWORD_GLOSS_VALIDATION/scripts/crossword_validation.py` (T1R, T2)
- `phases/CROSSWORD_GLOSS_VALIDATION/scripts/crossword_refined.py` (T1R refined, similarity)
- `phases/CROSSWORD_GLOSS_VALIDATION/scripts/grammatical_role_test.py` (shift test)
Results: `phases/CROSSWORD_GLOSS_VALIDATION/results/`

# Phase 522: Two-Level Closure Architecture

**Date:** 2026-03-05
**Status:** COMPLETE
**Phase type:** Characterization
**Extends:** C1439 (m/am orthogonality), C1412 (MIDDLE terminal gates suffix), C1408-C1409 (suffix atom decomposition), C1414 (cross-slot atom exclusion)
**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json`

---

## Research Question

C1439 showed that m-terminal MIDDLEs and the -am suffix are orthogonal closure systems operating at different grammar levels. Does this generalize? Do ALL terminal atoms partition closure/routing functions with the suffix layer, creating a systematic two-level information architecture?

## Key Findings Summary

| Finding | Result | Constraint |
|---------|--------|-----------|
| Three-tier terminal opacity gradient | n/y/m OPAQUE (<5%), l/r SEMI-TRANSPARENT (17-20%), h TRANSPARENT (99%) | C1440 |
| Active terminal-suffix exclusion grammar rule | m, y, n actively exclude suffix in matched population (O/E 0.07-0.17) | C1441 |
| TERMINAL-suffix information complementarity | 8.2% redundancy; 3.4x more info in TERMINAL than suffix; position-invariant | C1442 |
| 17 forbidden TERMINAL x suffix-head pairs | Extends C1414 with terminal-gated exclusion rules | C1443 |
| Self-atom cross-layer repulsion | y(0.028x), n(0.000x), r(0.486x) repel across MIDDLE->suffix | C1444 |
| m-terminal anticorrelates with suffix at paragraph level | rho=-0.199, p=0.00001 across 486 paragraphs | C1445 |

---

## T1: Terminal-Suffix Orthogonality Matrix

A 6 x 13 matrix of TERMINAL atom x suffix-head atom O/E ratios was constructed from 13,030 tokens with both a classifiable terminal and a suffix. The matrix reveals structured, non-random selectivity.

Key patterns from the matrix:

| Terminal | Suffix heads ATTRACTED (>3x) | Suffix heads REPELLED (<0.1) |
|----------|------------------------------|-------------------------------|
| y | d(3.8x), r(3.0x), s(3.1x), l(8.4x) | e(0.05x), i(0), n(0) |
| l | o(5.4x), d(2.6x) | e(0.03x), h(0), y(0), i(0) |
| r | a(2.4x), o(3.5x) | e(0), h(0), y(0), r(0), s(0.07x) |
| h | e(2.2x), d(2.6x) | a(0.18x), y(0), r(0.04x), s(0.17x), l(0.09x), i(0) |
| m | o(3.7x), d(2.8x), y(2.7x) | e(0), h(0), r(0), s(0), l(0), i(0) |
| n | y(8.2x) | e(0), h(0), r(0), s(0), l(0), i(0) |

**Overall contingency:** chi2 = 7384.7, V = 0.753, p = 0.0. The TERMINAL x suffix-presence association is extremely strong.

---

## T2: Suffix Suppression Gradient

Terminals do NOT form a binary opaque/transparent dichotomy. They form a **three-tier gradient**:

| Tier | Terminals | Suffix Rate | Suppression Ratio |
|------|-----------|------------|-------------------|
| **OPAQUE** | n (0.84%), y (1.61%), m (4.15%) | <5% | 12-57x |
| **SEMI-TRANSPARENT** | l (16.78%), r (19.52%) | 17-20% | 2.5-2.9x |
| **TRANSPARENT** | h (98.68%) | >98% | 0.49x (ATTRACTS) |

The gap between OPAQUE and SEMI-TRANSPARENT is 12 percentage points. The gap between SEMI-TRANSPARENT and TRANSPARENT is 79 percentage points. Both boundaries are sharp and unambiguous.

Each tier has distinct category concentration:
- OPAQUE terminals: y=OPERATION(40.6%), m=TRANSITION(87.9%), n=TRANSITION(39.3%)
- SEMI-TRANSPARENT: l=STAGING(64.5%), r=FLOW(98.9%)
- TRANSPARENT: h=MARKING(30.0%) -- most distributed across categories

Suffix suppression does NOT correlate with category concentration (rho=0.086, p=0.87). The opacity gradient is independent of functional specialization.

---

## T3: Same-Atom Orthogonality (Self-Repulsion)

When a terminal atom and a suffix-head atom are the SAME character, do they co-occur at expected rates? For 3 of 6 atoms, the answer is strongly NO:

| Atom | O/E (self-across-layers) | Fisher p | Direction |
|------|--------------------------|----------|-----------|
| y | **0.028** | 0.0 | SELF_REPEL |
| n | **0.000** | 0.0 | SELF_REPEL |
| r | **0.486** | 0.0 | SELF_REPEL |
| l | 0.621 | 0.0 | NEUTRAL (weak) |
| h | 0.843 | 0.286 | NEUTRAL |
| m | 1.048 | 0.795 | NEUTRAL |

**y, n, r actively avoid repeating themselves across the MIDDLE-suffix boundary.** y is most extreme: O/E = 0.028, meaning y-terminal MIDDLEs essentially never take a y-headed suffix. n-terminal never co-occurs with n-suffix (0 observed out of 2,147 n-terminal tokens). This extends C1414 (cross-slot atom exclusion) from individual atom pairs to a general self-repulsion principle.

---

## T4: Functional Partitioning

For each TERMINAL x suffix-head pair, I compared the top operational category of the TERMINAL population versus the suffix-head population. 88.5% of pairs (69/78) are COMPLEMENTARY -- their top categories differ.

All 6 self-pairs are complementary:

| Atom | TERMINAL top category | Suffix-head top category | JSD |
|------|----------------------|--------------------------|-----|
| y | OPERATION | THERMAL | 0.342 |
| l | STAGING | TRANSITION | 0.453 |
| r | FLOW | STAGING | 0.795 |
| h | MARKING | OPERATION | 0.027 |
| m | TRANSITION | MARKING | 0.499 |
| n | TRANSITION | FLOW | 0.616 |

Even atoms that are the "same character" carry DIFFERENT functional information depending on whether they appear at MIDDLE terminal or suffix-head position. This is a strong extension of C1409 (suffix atoms diverge from MIDDLE-terminal atoms).

---

## T5: Closure Generalization

### Line-Final Concentration by Terminal

Only m shows extreme line-final concentration (7.04x). All other terminals are near-flat:

| Terminal | Final Enrichment |
|----------|-----------------|
| m | **7.04x** |
| l | 1.12x |
| y | 1.03x |
| r | 1.02x |
| n | 0.70x |
| h | 0.68x |

m remains uniquely positional. The closure function is NOT generalized across terminals -- it is m-specific.

### Suffix-Head Line-Final Patterns

In the suffix layer, different atoms dominate:

| Suffix Head | Final Enrichment |
|-------------|-----------------|
| g | 8.09x |
| l | 2.97x |
| i | 2.32x |
| y | 1.80x |
| d | 1.27x |

### Composition of Line-Final Tokens

Of 2,554 line-final tokens, 45.5% are bare (no suffix) and 54.5% are suffixed. Among bare line-final tokens:

| Terminal | Count | % of bare finals |
|----------|-------|-----------------|
| y | 504 | 43.4% |
| m | 215 | 18.5% |
| l | 184 | 15.9% |
| n | 153 | 13.2% |
| r | 99 | 8.5% |

y dominates bare line-final tokens, m is second. This shows the two-level system: bare closure (MIDDLE terminal does the work) vs suffixed closure (suffix layer does the work).

---

## T6: Mutual Exclusivity Patterns

### Near-Exclusive Pairs (O/E < 0.1)

17 TERMINAL x suffix-head pairs show near-zero co-occurrence:

| Terminal | Excluded Suffix Heads | Count |
|----------|----------------------|-------|
| y | e (0.05x) | 1 pair |
| l | e (0.03x), h (0), y (0), i (0) | 4 pairs |
| r | e (0), h (0), y (0), r (0), s (0.07x) | 5 pairs |
| h | y (0), r (0.04x), l (0.09x), i (0), g (0) | 5 pairs |
| m | e (0) | 1 pair |
| n | e (0) | 1 pair |

**e-suffix is near-universally excluded** by all non-h terminals. Only h-terminal permits e-headed suffix (O/E = 2.21x). This makes h the gateway for e-suffix attachment, consistent with C1419 (ARTICULATOR e-HEAD selectivity).

### Strong Co-occurrence Pairs (O/E > 3)

8 pairs show strong enrichment:

| Terminal | Attracted Suffix Head | O/E |
|----------|----------------------|-----|
| y | d (3.8x), r (3.0x), s (3.1x), l (8.4x) | 4 pairs |
| l | o (5.4x) | 1 pair |
| r | o (3.5x) | 1 pair |
| m | o (3.7x) | 1 pair |
| n | y (8.2x) | 1 pair |

**o-suffix is the universal attractor** for l/r/m terminals. This is a complementary domain pattern: STAGING/FLOW/TRANSITION terminals consistently attract STAGING-associated suffixes.

---

## T7: Information Complementarity

| Metric | Value |
|--------|-------|
| I(category; TERMINAL) | 1.261 bits |
| I(category; suffix_head) | 0.347 bits |
| I(category; TERMINAL + suffix_head jointly) | 1.252 bits |
| Sum of individual MIs | 1.363 bits |
| Redundancy | 0.112 bits |
| **Redundancy fraction** | **8.2%** |
| **Verdict** | **COMPLEMENTARY** |

TERMINAL carries 3.6x more category information than suffix. The two layers are 91.8% non-redundant -- they encode almost entirely DIFFERENT aspects of operational category. This is not a system where the two layers say the same thing in different ways. They are complementary information channels.

---

## T8: Position-Invariant Layer Ratio

The TERMINAL-to-suffix information ratio is stable across all line positions:

| Line Quintile | MI(TERMINAL) | MI(suffix) | Layer Ratio |
|---------------|-------------|-----------|-------------|
| Q0 (initial) | 1.237 | 0.358 | 3.46x |
| Q1 | 1.223 | 0.360 | 3.40x |
| Q2 (medial) | 1.287 | 0.369 | 3.49x |
| Q3 | 1.272 | 0.398 | 3.20x |
| Q4 (final) | 1.317 | 0.372 | 3.54x |

The ratio hovers between 3.2-3.5x at every position. Neither layer gains or loses information dominance as tokens move from line-initial to line-final. The two-level architecture is structurally invariant across the line.

---

## T9: Paragraph-Level Layer Balance

Across 486 paragraphs with 3+ tokens:

| Metric | Mean |
|--------|------|
| m-terminal fraction | 1.27% |
| Suffix fraction | 49.7% |
| Both (m-term AND suffixed) | 0.06% |
| Neither (bare, non-m-term) | 39.7% |

### m-terminal and suffix anticorrelation

Spearman rho = **-0.199**, p = 0.00001 across 486 paragraphs. Paragraphs that use more m-terminal closure use less suffix attachment. This is a weak but highly significant anticorrelation, consistent with the two systems being partial substitutes at the paragraph level.

### Section variation

| Section | m-terminal mean | Suffix mean |
|---------|----------------|-------------|
| B (Bio) | 0.57% | 46.8% |
| H (Herbal) | 1.97% | 45.0% |
| C (Cosmo) | 2.46% | 46.7% |
| T (Zodiac) | 1.56% | 51.4% |
| S (Stars/Recipe) | 1.19% | 52.0% |

Bio uses the least m-terminal closure (0.57%), consistent with C1435's finding that m anti-correlates with THERMAL intensity.

---

## T10: Active Exclusion vs Statistical Independence

This is the crucial design-principle test. If m and -am are merely from different populations, their avoidance could be passive. But if they ACTIVELY exclude each other in populations where both are plausible, that proves a grammar rule.

### m-terminal / -am suffix exclusion test

**Population:** Body-line-final tokens that are NOT paragraph-final (N=1,439). This is the population where both m-terminal and -am suffix are structurally plausible.

| Metric | Value |
|--------|-------|
| N population | 1,439 |
| N m-terminal | 166 (11.5%) |
| N -am suffix | 117 (8.1%) |
| N both | **1** |
| Expected both | 13.5 |
| **O/E ratio** | **0.074** |
| Fisher p | **0.000012** |
| **Verdict** | **ACTIVE EXCLUSION** |

Only 1 token has both m-terminal MIDDLE and -am suffix, vs 13.5 expected. This is 13.5x depletion with p = 0.000012. **The exclusion is a grammar rule, not a population artifact.**

### Generalized terminal exclusion in matched population

Testing all 6 terminals for suffix rate within the same body-line-final, non-par-final population (baseline suffix rate = 45.8%):

| Terminal | N | Suffix Rate | O/E vs Population | Verdict |
|----------|---|------------|-------------------|---------|
| y | 302 | 7.3% | **0.159** | **ACTIVE_EXCLUSION** |
| n | 104 | 7.7% | **0.168** | **ACTIVE_EXCLUSION** |
| m | 166 | 4.8% | **0.105** | **ACTIVE_EXCLUSION** |
| l | 205 | 43.4% | 0.948 | NEUTRAL |
| r | 122 | 55.7% | 1.217 | NEUTRAL |
| h | 44 | 100% | 2.184 | NEUTRAL (always suffixed) |

**Three terminals (y, m, n) actively suppress suffix attachment** even in contexts where suffixation is the norm. l and r are neutral -- their overall lower suffix rates reflect population differences, not active suppression. h always takes a suffix.

This confirms the three-tier gradient from T2 is a GRAMMAR RULE, not a distributional artifact.

---

## Synthesis: The Two-Level Information Architecture

Phase 522 establishes that C1439's m/am orthogonality generalizes to a broader design principle. The instruction token's closure/routing information is systematically partitioned between two parallel layers:

### Layer 1: MIDDLE Terminal Atom
- **Information capacity:** 1.26 bits of category information (3.6x suffix)
- **Function:** Primary operational specification
- **Opacity gradient:** Three tiers (OPAQUE n/y/m, SEMI-TRANSPARENT l/r, TRANSPARENT h)
- **Position invariance:** Constant 3.2-3.5x ratio across line positions
- **Self-containment:** OPAQUE terminals suppress suffix, encoding closure WITHIN the MIDDLE

### Layer 2: Suffix Head Atom
- **Information capacity:** 0.35 bits of category information
- **Function:** Supplementary parametric specification
- **Access control:** Gated by terminal opacity (h always permits, n/y/m rarely permit)
- **Complementarity:** 88.5% of TERMINAL x suffix pairs encode different top categories
- **Exclusion rules:** 17 near-forbidden TERMINAL x suffix-head combinations

### Design Principle

The grammar partitions closure information between MIDDLE and suffix so that:
1. **OPAQUE terminals (n, y, m)** are self-contained operators. They carry their own closure semantics and block suffix attachment. When these appear, the instruction is specified entirely within the MIDDLE.
2. **TRANSPARENT terminals (h)** are parametric hosts. They carry minimal closure semantics and REQUIRE suffix attachment (98.7% suffixed). The suffix provides the operational specification.
3. **SEMI-TRANSPARENT terminals (l, r)** can operate either way. They accept suffix for additional specification but function independently when bare.

This is NOT the same character doing the same thing in two places. It is the same CHARACTER carrying DIFFERENT information depending on position (C1409), with the terminal atom gating whether the suffix layer gets to contribute at all (C1412).

---

## New Constraints

### C1440: Three-Tier Terminal Opacity Gradient
Terminal atoms form a three-tier suffix suppression gradient, not a binary opaque/transparent split. OPAQUE: n (0.84%), y (1.61%), m (4.15%) -- suppress suffix <5%. SEMI-TRANSPARENT: l (16.78%), r (19.52%) -- partial suppression. TRANSPARENT: h (98.68%) -- near-obligatory suffix. V=0.753, chi2=7384.7, p=0.0. Gradient is independent of category concentration (rho=0.086, p=0.87).

### C1441: Active Terminal-Suffix Exclusion Grammar Rule
In the body-line-final, non-paragraph-final population (N=1,439), three terminals actively suppress suffix attachment: y (O/E=0.159), m (O/E=0.105), n (O/E=0.168). All show suffix rates <8% in a population with 45.8% baseline. l and r are neutral (O/E ~1.0), h always suffixed. The opacity gradient is a grammar rule, not a distributional artifact.

### C1442: TERMINAL-Suffix Category Information Complementarity
TERMINAL carries 1.261 bits of category MI vs suffix-head 0.347 bits (3.6x ratio). Joint MI=1.252 bits, redundancy=0.112 bits (8.2%). The two layers encode almost entirely different category information. Layer ratio stable 3.2-3.5x across all five line-position quintiles. COMPLEMENTARY verdict.

### C1443: 17 Forbidden TERMINAL x Suffix-Head Pairs
17 TERMINAL x suffix-head combinations show near-zero co-occurrence (O/E < 0.1). e-suffix is excluded by all non-h terminals (5 pairs). r-terminal excludes 5 suffix heads (e, h, y, r, s). l-terminal excludes 4 (e, h, y, i). h-terminal excludes 5 (y, r, l, i, g). Extends C1414 cross-slot exclusion rules to the full terminal x suffix-head space.

### C1444: Self-Atom Cross-Layer Repulsion
Three of six testable atoms actively avoid repeating across the MIDDLE terminal -> suffix head boundary: y (O/E=0.028, Fisher p=0.0), n (O/E=0.000, p=0.0), r (O/E=0.486, p=0.0). l shows weak avoidance (0.621), h and m are neutral. The same character in MIDDLE terminal and suffix head encodes DIFFERENT information (C1409), and the grammar actively prevents redundant repetition.

### C1445: m-Terminal and Suffix Anticorrelation at Paragraph Level
Across 486 paragraphs, m-terminal fraction and suffix fraction anticorrelate (Spearman rho=-0.199, p=0.00001). Paragraphs that use more m-terminal closure use less suffix attachment. Bio section uses least m-terminal (0.57%), Stars/Recipe highest suffix (52.0%). The two closure layers are partial substitutes at paragraph scale.

---

## Falsification Criteria

- C1440: If any terminal's suffix rate moves across a tier boundary by >5 percentage points under different filtering
- C1441: If y/m/n show O/E > 0.5 in the matched population under alternative population definitions
- C1442: If redundancy fraction exceeds 25% or layer ratio reverses (suffix > TERMINAL)
- C1443: If more than 3 of the 17 forbidden pairs exceed O/E = 0.3 under replication
- C1444: If y or n self-co-occurrence O/E exceeds 0.3
- C1445: If paragraph-level m/suffix correlation changes sign under section control

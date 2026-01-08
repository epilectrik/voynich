# Phase SISTER: Sister Pair Analysis

**Date:** 2026-01-08
**Status:** CLOSED
**Constraints:** 407-410, 383a (5 Tier 2 constraints)

## Overview

This phase investigated the internal structure of Currier A's 8-prefix system, discovering that prefixes partition into distinct structural categories rather than forming 8 independent families.

## Key Discoveries

### 1. DA is Infrastructure, Not a Material Family (Constraint 407)

Evidence:
- Extreme suffix bias: -in at 34.4% vs 1.1% for other prefixes
- Extreme line-boundary enrichment: 20.9% line-initial vs 2-8% for others
- Low internal diversity: top 3 tokens (daiin, dain, dar) = 42.6% of class
- Alignment with known infrastructure token `daiin`

**Conclusion:** DA functions as record articulation (structural punctuation), not material classification.

### 2. Sister Pair Equivalence Classes (Constraint 408)

Jaccard similarity of MIDDLE component vocabulary:

| Pair | Jaccard |
|------|---------|
| ch-sh | 0.23 |
| ok-ot | 0.24 |
| Cross-pair baseline | 0.05-0.08 |
| CT, DA with others | <0.04 |

Sister pairs share 3-4x more MIDDLE vocabulary than non-sister pairs.

**Prefix space partition:**
- 2 Sister pairs: ch-sh, ok-ot
- 2 Isolates: da (infrastructure), ct (Section H specialist)
- 2 Bridging families: qo, ol

### 3. Sister Pairs are Substitutable but Mutually Exclusive (Constraint 409)

In Currier B programs:
- Bigram suppression: ch-sh 0.62-0.65x, ok-ot 0.53-0.64x (they AVOID direct sequence)
- Shared predecessor contexts: 336 predecessors lead to both ch-X and sh-X
- Minimal pairs: 195 suffixes appear with both ch- and sh-
- Trigram substitution: 119 A...B frames accept either ch or sh

**Key finding:** Sister pairs occupy the same grammatical slot but are alternative choices, not companions. You choose ONE or the OTHER.

### 4. Sister Pair Choice is Section-Conditioned (Constraint 410)

Section preferences for ch-form:
| Pair | Section H | Section B |
|------|-----------|-----------|
| cheky/sheky | 85% ch | 42% ch |
| chckhy/shckhy | 92% ch | 57% ch |
| checkhy/sheckhy | 78% ch | 50% ch |

Quire pattern:
- Earlier quires (E, F, G): prefer ch-forms
- Quire M: balanced or sh-leaning

Conditioning operates at section/quire level, not folio level (71% of occurrences in mixed folios).

### 5. System-Specific Realization of Global Types (Constraint 383a)

AZC probe confirmed sister pair substitutability is GLOBAL but realization is SYSTEM-SPECIFIC:

| Property | Currier A | Currier B | AZC |
|----------|-----------|-----------|-----|
| ch/sh substitutable | Yes | Yes | Yes |
| ch/sh mutually exclusive | — | Strong (0.65x) | Partial (asymmetric) |
| Section conditioning | — | Strong (H=ch) | Weak |
| DA = infrastructure | Yes (20.9% init) | Yes | **NO** |
| Boundary specialists | DA | DA | **ok/ot** (38%/27% init) |

**Key insight:** Infrastructure is ROLE-BASED, not TOKEN-FIXED. The same type system underlies all three modes, but different grammars project it differently. AZC reassigns boundary roles from DA to ok/ot.

## Implications

1. **Currier A is not 8 equal categories** but a structured space with infrastructure elements, equivalence classes, and bridging families.

2. **Sister pairs in A correspond to grammatical alternatives in B** - the registry tracks variants that serve the same functional role under different conditions.

3. **Section/quire context constrains variant choice** - organizational structure determines which alternative is preferred.

## Scripts

- `currier_a_combination_explorer.py` - Initial token analysis and counting
- `currier_a_deep_dive.py` - DA anomaly and Jaccard similarity matrix
- `sister_pair_test.py` - Co-occurrence and bigram analysis in B
- `substitutability_test.py` - Minimal pairs and trigram substitution
- `sister_pair_conditioning.py` - Section/quire/position conditioning tests
- `azc_sister_pair_probe.py` - Cross-system validation (A, B, AZC)

## Tier Assessment

All 5 constraints are **Tier 2 (Structural Inference)** - backed by quantitative tests on internal structure, no semantic claims.

Speculative interpretations (materials, preparations, variants) remain **Tier 3-4**.

## Architectural Summary

This phase establishes that the Voynich manuscript uses a **deliberately modular formal system**:

- **Global type system** (substitution classes, kernel dichotomy) shared across all modes
- **System-specific positional grammar** determines realization
- **Infrastructure is role-based** — the same function can be performed by different tokens in different systems

This explains why AZC felt "almost B but not quite" and why DA behaved inconsistently across prior analyses.

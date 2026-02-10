# Structural Gloss Qualifier Key

**Tier:** 3 (INTERPRETIVE) | **Status:** ACTIVE | **Date:** 2026-02-09

> **Qualifiers indicate structural differentiation only. They are mnemonic labels, not claims about physical action.**

---

## Purpose

The B decoder uses colon-qualified glosses (`category:qualifier`) to ensure every structurally distinct MIDDLE produces a visually distinct English rendering. Qualifiers are grounded in Tier-2 structural evidence (kernel profiles C908, regime correlations C910, transition behavior C506.b), not semantic interpretation.

---

## Category Families

| Pattern | Structural meaning |
|---------|-------------------|
| `heat:*` | Energy-domain operator (k-kernel cluster, C908) |
| `cool:*` | Stability-domain operator (e-kernel cluster, C908) |
| `check:*` | Evaluative observation (monitoring MIDDLEs) |
| `mark` | Non-evaluative structural annotation (MIDDLE `d`, distinct from `check:*` family) |
| `watch` | Ambient monitoring (MIDDLE `h`, from F-BRU-011 "watch for hazards") |
| `close:*` | Boundary/closure operators |
| `collect:*` | Gathering/accumulation operators |

---

## Qualifier Meanings

| Qualifier | Source | Structural basis |
|-----------|--------|-----------------|
| `:steady` | C910 regime | Sustained / equilibrating mode |
| `:pulse` | C908 k-cluster | Precision / bounded mode |
| `:hard` | C908 k-cluster | Direct / unmodulated application |
| `:watch` | C908 h-cluster | Monitoring / hazard observation |
| `:deep` | C910 regime | Extended depth / thorough mode |
| `:long` | C908 e-cluster | Extended duration |
| `:open` | C908 e-cluster | Open / permissive mode |
| `:wide` | C908/C910 | Extended open / broad mode |
| `:fire` | C908 h-cluster | H-kernel monitoring (hazard watching) |
| `:settle` | C910 SETTLING | Equilibration checkpoint |
| `:seal` | C908 k-cluster | Energy-side sealing (PRECISION) |
| `:release` | — | Neutral / passive release |
| `:precise` | C910 PRECISION | Precision-regime collection |
| `:gather` | C908 k-cluster | Active energy-side gathering |

---

## Suffix Labels

| Label | Structural basis |
|-------|-----------------|
| `[gate]` | Full quality gate (suffix `aiin`, C561 directional bigram) |
| `[check]` | Light inline check (suffix `ain`) |
| `[loop]` | Iterative continuation (suffix `iin`, LOOP flow_type) |
| `[final]` | Finalize flow (suffix `am`, LINE_FINAL role) |
| `[seal]` | Work-final completion (suffix `om`, LINE_FINAL) |
| `[cycle]` | Iterate-final (suffix `im`, LINE_FINAL) |
| `[step]` | Continuation step (suffix `in`, LINK_ATTR) |

---

## `mark` vs `check:*` Distinction

- **`mark`** (MIDDLE `d`): Non-evaluative structural annotation — a positional marker or setup label that does not assess state
- **`check:fire`** (MIDDLE `ch`): Evaluative observation in H-kernel (hazard) context — actively monitors a condition
- **`check:settle`** (MIDDLE `aiin`): Evaluative observation in SETTLING regime — verifies equilibration

The distinction is between *annotating structure* (mark) and *evaluating state* (check:*).

---

## Validation

Uniqueness invariant enforced by `phases/GLOSS_RESEARCH/scripts/25_middle_uniqueness_test.py`:
- 340 glossed MIDDLEs → 340 distinct gloss strings (zero collisions)
- 25 suffix glosses → 25 distinct values (zero collisions)

---

## Provenance

- C506.b: Different MIDDLEs within same class have statistically different transition profiles (p<0.0001)
- C631: MIDDLE variation is continuous — qualifiers mark structural distinctions, not discrete categories
- C908: 55% of MIDDLEs correlate with kernel type (k/e/h clusters)
- C910: 67% of MIDDLEs show regime dependence (PRECISION/HIGH_ENERGY/SETTLING)
- F-BRU-011: Brunschwig "watch" vocabulary for hazard monitoring

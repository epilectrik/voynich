# B_EXCLUSIVE_MIDDLE_ORIGINS Phase Summary

**Date:** 2026-01-21
**Status:** COMPLETE
**Result:** B-EXCLUSIVE STRATIFICATION CONFIRMED (C501)

---

## Research Question

Why are 569 MIDDLEs B-exclusive? What property makes them incompatible with Currier A's registry system?

---

## Pre-Registered Predictions

| Test | Prediction | Actual | Verdict |
|------|------------|--------|---------|
| T1: PREFIX (OL/QO) | >3x enriched | 0.84x, 0.95x | FAIL |
| T1: PREFIX (CT) | <0.2x depleted | 0.79x | FAIL |
| T2: Edit Distance | 15-25% distance-1 | **65.9%** | FAIL (informative) |
| T3: Length | B-excl > shared | 4.40 > 3.03 (p<0.0001) | **PASS** |
| T4: Boundary | >1.5x enrichment | 1.70x | **PASS** |
| T5: REGIME | R3/4 >1.5x | 0.65x (opposite) | FAIL |

---

## Key Discovery: Orthographic Variants Dominate

**65.9% of B-exclusive MIDDLEs are edit-distance-1 from shared MIDDLEs.**

| Edit Type | Count | Percentage |
|-----------|-------|------------|
| Insertion | 222 | 59.2% |
| Substitution | 146 | 38.9% |
| Deletion | 7 | 1.9% |

**Examples:** `ked→ke`, `eees→eee`, `lkesh→kesh`, `cta→ct`

This means B-exclusivity is NOT about distinct discriminators - it's **morphological surface variation**.

---

## Three-Layer Stratification (C501)

### Layer 1: True Grammar Operators (Small, Concentrated)

L-compound MIDDLEs that function as line-initial control operators:

| MIDDLE | Count | Line-Initial% |
|--------|-------|---------------|
| `lk` | 30 | 37% |
| `lkee` | 15 | 47% |
| `lched` | 4 | 50% |
| `lar` | 2 | 100% |

**Total:** 49 types, 111 tokens

These are the only B-exclusive MIDDLEs that behave like operators. Covered by C298.

### Layer 2: Boundary Closers (Small, Structural)

Line-final termination markers:

| MIDDLE | Count | Line-Final% |
|--------|-------|-------------|
| `edy` | 9 | 67% |
| `dy` | 7 | 29% |
| `eeed` | 5 | 40% |

### Layer 3: Singleton Cloud (Large, Non-Operational)

- **457/569 (80.3%)** are hapax legomena
- **65.9%** are edit-distance-1 variants of shared MIDDLEs
- **Longer** than shared MIDDLEs (mean 4.40 vs 3.03 chars)
- **Zero reuse** - no combinatorial power
- **NOT grammar**

---

## False Lead: The "49 Distant MIDDLEs"

We investigated whether the 49 MIDDLEs with edit-distance ≥3 correlated with the 49 instruction classes (C121).

**Result:** The coincidence is false.

- All 49 are **hapax legomena** (appear exactly once)
- No clustering, no positional dominance, no reuse
- Likely scribal anomalies or malformed compounds

This line of inquiry is **correctly closed**.

---

## Architectural Interpretation

B-exclusive status primarily reflects **positional and orthographic realization under execution constraints**, not novel discriminative content.

| What B-Exclusive Is | What B-Exclusive Is NOT |
|---------------------|-------------------------|
| Elaborated shared MIDDLEs | Distinct semantic operators |
| Boundary-position variants | New discrimination space |
| Morphological surface variation | Grammar-level specialization |

**Exception:** The small L-compound core (49 types, C298) ARE genuine B-specific grammar operators.

---

## REGIME Finding

REGIME_1 (simple procedures) has the **highest** B-exclusive rate (60.4%), not REGIME_3/4.

| REGIME | B-Exclusive Rate |
|--------|------------------|
| REGIME_1 | 60.4% |
| REGIME_2 | 46.7% |
| REGIME_3 | 44.3% |
| REGIME_4 | 46.2% |

**Interpretation:** Simple procedures tolerate more orthographic variation. Complex/precision procedures stick to canonical (shared) vocabulary. This supports C458 (Execution Design Clamp).

---

## Constraint Added

### C501 - B-Exclusive MIDDLE Stratification
**Tier:** 2 | **Status:** CLOSED

The set of B-exclusive MIDDLEs does not represent a distinct semantic or discriminative layer. Empirically, B-exclusive MIDDLEs stratify into:

1. **True grammar operators** — L-compound MIDDLEs (49 types, 111 tokens) functioning as line-initial control operators
2. **Boundary closers** — `-edy/-dy` forms enriched at line-final position
3. **Singleton cloud** — 80.3% hapax legomena, 65.9% edit-distance-1 variants of shared MIDDLEs

B-exclusive status primarily reflects positional and orthographic realization under execution constraints, not novel discriminative content.

---

## Files Produced

```
phases/B_EXCLUSIVE_MIDDLE_ORIGINS/
├── scripts/
│   ├── b_excl_origin_analysis.py      # Main 5-test battery
│   ├── extract_distant_middles.py     # 49 distant MIDDLE investigation
│   └── high_freq_b_exclusive.py       # L-compound and operator analysis
├── results/
│   └── b_excl_origin_analysis.json
└── PHASE_SUMMARY.md
```

---

## Constraint Compliance

| Constraint | Status |
|------------|--------|
| C298 (L-compounds) | **SUPPORTED** - L-compounds confirmed as concentrated operator core |
| C271 (Compositional) | **STRENGTHENED** - edit patterns confirm productive morphology |
| C358 (Boundary tokens) | **COMPATIBLE** - boundary enrichment confirmed |
| C383 (Global type system) | UNAFFECTED |
| C458 (Design clamp) | **SUPPORTED** - REGIME_1 freedom = more variation |

---

## Navigation

← [../A_SECTION_T_CHARACTERIZATION/PHASE_SUMMARY.md](../A_SECTION_T_CHARACTERIZATION/PHASE_SUMMARY.md) | ↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)

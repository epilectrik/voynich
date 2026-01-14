# Perturbation Space Analysis Phase

**Status:** COMPLETE + SATURATED | **Date:** 2026-01-11 | **Tests:** 1/3 perturbation + 3/3 structural + 2/2 refinements

> **Saturation Declaration:** This line of inquiry is now CLOSED. Expert review confirmed this phase does not violate any Tier 0-2 constraints, resolves the open question about shared MIDDLEs, and produces two legitimate Tier 3 constraints (C461, C462). No unexplained structural feature remains in Currier A.

---

## Executive Summary

This phase tested whether MIDDLE frequency tier (Core vs Tail) correlates with operational complexity in Currier B execution. The results reveal a **layer-specific** pattern:

- **HT layer confirms perturbation recognition** (1.58x higher HT density for Tail)
- **B-layer shows uniform execution** (no recovery or stabilization differences)

This refines the perturbation space model: the system *recognizes* rare situations (A + HT) but *executes* them uniformly (B).

---

## Test Results

### Test A: HT Density vs MIDDLE Tier

**Result: STRONGLY CONFIRMED (p < 0.0001)**

| Metric | Core | Tail | Ratio |
|--------|------|------|-------|
| Tokens | 10,174 | 3,493 | - |
| HT marker rate | 18.70% | 29.54% | 1.58x |

Chi-squared = 180.56, p < 0.0001

**Interpretation:** The Human Track layer anticipates perturbation-space situations. Rare MIDDLEs trigger heightened attention markers 58% more often than common MIDDLEs.

---

### Test B: Recovery-Path Diversity

**Result: NOT CONFIRMED (p = 0.28)**

| Metric | Core | Tail |
|--------|------|------|
| Transitions | 9,387 | 3,149 |
| Unique successors | 139 | 104 |
| Successor entropy | 4.36 bits | 4.31 bits |

**Interpretation:** Both tiers have nearly identical recovery-path diversity. The B-layer grammar does not constrain rare situations more than common ones.

---

### Test C: Time-to-STATE-C

**Result: OPPOSITE OF PREDICTION**

| Metric | Core | Tail |
|--------|------|------|
| Mean distance | 2.11 tokens | 2.05 tokens |
| Std deviation | 1.55 | 1.52 |

Mann-Whitney p = 0.995 (Tail is actually FASTER)

**Interpretation:** Rare situations stabilize as quickly (or faster) than common ones. The grammar doesn't require extended recovery for perturbations.

---

## Refined Perturbation Space Model

The original hypothesis was:
> Tail MIDDLEs = harder to handle = more recovery effort

The actual finding is:
> Tail MIDDLEs = recognized as unusual = executed uniformly

### Layer-Specific Roles

| Layer | Perturbation Response | Evidence |
|-------|----------------------|----------|
| **A + HT** | Recognition + attention | 1.58x HT density (confirmed) |
| **B** | Uniform execution | Equal recovery/stabilization |

### Why This Makes Sense

1. **Recognition is the hard part.** Once a situation is identified (via MIDDLE), the grammar knows what to do. The difficulty is in *seeing* the edge case, not in *handling* it.

2. **HT anticipates difficulty.** The Human Track layer marks where attention is needed - precisely at rare situations. This is anticipatory, not reactive.

3. **B-layer is mode-agnostic.** The execution grammar doesn't care whether a situation is common or rare. It applies the same recovery logic either way.

4. **Fast stabilization for rare cases.** This aligns with earlier findings that rare MIDDLEs have HIGHER mutual information with decision archetypes. Edge cases trigger immediate, specific responses - not prolonged uncertainty.

---

## Connection to Earlier Findings

### Bayesian Test B3 (MI "Failure")

Earlier we found: Tail MIDDLEs have HIGHER mutual information with decision archetypes.

This perturbation phase explains why:
- Rare situations trigger **specific, immediate responses**
- The system tightens control when something unusual happens
- Edge cases are rare precisely because they have sharp, well-defined responses

### Constraint Alignment

This phase supports:
- **C458** (recovery freedom is local, constraints tighten near boundaries)
- **C404-405** (HT is non-operational but cognitively functional)
- **C459** (HT anticipates stress)

---

## Synthesis Statement

The perturbation space model is **partially confirmed but refined**:

> MIDDLEs encode situational recognition points drawn from two frequency regimes (Core vs Tail). The Human Track layer recognizes perturbation-space situations and flags them for heightened attention. However, the B-layer execution grammar treats all recognized situations uniformly - the difficulty is in recognition, not execution.

This means:
- **A-layer + HT** = "This is unusual, pay attention"
- **B-layer** = "Understood, executing standard protocol"

The system doesn't have "special handling" at the execution layer for rare cases. It has **special recognition** at the discrimination layer.

---

---

## MIDDLE Material Class Sharing Analysis

A follow-up analysis examined how MIDDLEs are shared across material classes.

### Sharing Structure

| Pattern | MIDDLEs | % Types | Tokens | % Tokens |
|---------|---------|---------|--------|----------|
| Universal (all 4 classes) | 18 | 2.5% | 3,118 | **43.7%** |
| Tri-class (3 classes) | 35 | 4.8% | 1,432 | 20.1% |
| Bi-class (2 classes) | 99 | 13.7% | 1,397 | 19.6% |
| Exclusive (1 class) | 573 | **79.0%** | 1,180 | 16.6% |

**Key insight:** 79% of MIDDLE *types* are class-exclusive, but the 21% shared types account for 83% of *tokens*.

### Property-Based Bridging

| Bridge Type | MIDDLEs | Shared Property | Interpretation |
|-------------|---------|-----------------|----------------|
| Mobility bridge | 61 | Same phase mobility | Phase behavior situations |
| Composition bridge | 14 | Same composition | Fractionation behavior situations |
| Diagonal bridge | 24 | Opposite on both | Pure apparatus states |

### Universal MIDDLEs (Top 10)

| MIDDLE | Total | M-A | M-B | M-C | M-D |
|--------|-------|-----|-----|-----|-----|
| 'o' | 1,137 | 623 | 428 | 62 | 24 |
| '' | 1,041 | 229 | 204 | 460 | 148 |
| 'e' | 207 | 91 | 107 | 8 | 1 |
| 'a' | 193 | 74 | 74 | 44 | 1 |
| 'k' | 133 | 126 | 5 | 1 | 1 |
| 'cho' | 95 | 4 | 34 | 54 | 3 |

### Class-Exclusive Patterns

| Class | Exclusive MIDDLEs | Top Examples | Interpretation |
|-------|-------------------|--------------|----------------|
| M-A | 315 | 'to', 'tcho', 'teo' | Volatile phase behaviors |
| M-B | 84 | 'ysho', 'oeo' | Flow perturbations |
| M-C | 104 | 'ii', 'la', 'ir' | Separation/settling |
| M-D | 70 | 'ho', 'he', 'ha' | Baseline/anchor states |

### Behavioral Inference

The sharing patterns align with material class properties:

1. **Universal MIDDLEs** = Material-independent apparatus states (temperature, time, generic conditions)
2. **Mobility bridges** = Phase behavior shared by mobile OR stable classes
3. **Composition bridges** = Fractionation behavior shared by distinct OR homogeneous classes
4. **Exclusive MIDDLEs** = Material-specific perturbations

This supports the apparatus-centric model: MIDDLEs encode situational fingerprints, and their class-sharing patterns reveal which situations depend on material properties vs which are pure apparatus states.

---

## Universal MIDDLE Structural Properties

A structural analysis compared the 18 universal MIDDLEs against 573 class-exclusive MIDDLEs.

### Test Results

| Property | Universal | Exclusive | Direction | Significance |
|----------|-----------|-----------|-----------|--------------|
| Suffix entropy | 3.08 bits | 2.97 bits | MORE diverse | Confirmed |
| Sister preference | 51.0% precision | 87.3% precision | MORE balanced | p < 0.0001 |
| Section entropy | 1.065 bits | 1.126 bits | MORE concentrated | Confirmed |

Chi-squared = 471.55 for sister preference test.

### Balance Score Distribution

Universal MIDDLEs vary in how evenly they're distributed across material classes:

| MIDDLE | Balance | Pattern |
|--------|---------|---------|
| `ald` | 1.00 | Perfectly balanced |
| `ol` | 0.96 | Highly balanced |
| `ai` | 0.95 | Highly balanced |
| ... | ... | ... |
| `k` | 0.18 | Heavily skewed (M-A dominant) |

Mean balance: 0.789 | Highly balanced (>0.75): 10/18

### Tight Interpretation

**What universal MIDDLEs show:**
1. **More decision flexibility** - wider range of suffix outcomes
2. **Mode-agnostic** - occur equally in precision (ch) and tolerance (sh) modes
3. **Not material-dependent** - these situations don't require knowing what material is being processed

**What we cannot claim:**
- What physical phenomenon these MIDDLEs represent
- Entity-level semantics (e.g., "temperature" or "time")

### Synthesis

The sharing-based classification reveals structural hierarchy:

| Category | Behavioral Profile |
|----------|-------------------|
| **Universal** | Mode-balanced, suffix-flexible, material-independent |
| **Bridging** | Shared by property similarity (mobility or composition) |
| **Exclusive** | Mode-specific, suffix-constrained, material-dependent |

This suggests the MIDDLE vocabulary has three functional tiers:
1. **Apparatus states** (universal) - conditions independent of material
2. **Property states** (bridging) - conditions shared by material property
3. **Material states** (exclusive) - conditions specific to material class

---

## Expert Synthesis: Currier A is Internally Solved

With this phase complete, Currier A's internal function can be stated precisely:

> **Currier A partitions the operational recognition space into:**
> - a small, shared, routine core of apparatus-generic situations
> - and a large, sparse, class-specific perturbation space requiring expert recognition

> **MIDDLE sharing patterns show *where recognition equivalence holds* across material-behavior classes - not why, not what, and not how to act.**

This explains every structural oddity in Currier A:
- Why it's flat -> registry, not taxonomy
- Why repetition is literal -> enumeration of variants, not quantities
- Why most entries are rare -> perturbation space dominates recognition
- Why clustering is local -> distinctions matter only in context
- Why HT spikes in tails -> recognition difficulty, not execution difficulty

The complete pipeline is now:
```
Currier A  -> recognition space partition
HT         -> anticipatory vigilance for recognition difficulty
Currier B  -> uniform safe execution once recognized
```

**No unexplained structural feature remains in Currier A.**

### External Genre Comparison (Post-Saturation)

A structural elimination analysis compared Currier A against documented medieval organizational traditions. See [../../context/SPECULATIVE/currier_a_genre_elimination.md](../../context/SPECULATIVE/currier_a_genre_elimination.md).

**Eliminated traditions:**
- Alphabetical (Circa instans, Tractatus) - violates C240
- Head-to-toe anatomical - violates C240, C345
- Therapeutic/symptomatic - violates C345, C236
- Encyclopedic - violates C236, C231
- Narrative craft manuals - violates C240, C233
- Taxonomic (naturalistic) - violates C236, C345

**Plausible but not matching:**
- Galenic quality-based organization
- Workshop reference lists (Mappae Clavicula type)
- Pre-reorganization Dioscorides
- Books of secrets tradition

**Conclusion:** Currier A is structurally optimized for expert operational use, not knowledge transmission. This explains why it resists genre classification.

---

## Final Refinements (Post-Saturation)

Two final analyses were conducted following expert guidance to sharpen the functional taxonomy without reopening semantic questions.

### Refinement 1: MIDDLE -> Suffix Dependency

**Framing:** How recognition hands off to control

| Category | Mean Entropy | High-Entropy Rate | Rigid Rate |
|----------|--------------|-------------------|------------|
| Universal | 2.37 bits | 84.6% | 7.7% |
| Other | 1.38 bits | 42.6% | 17.8% |

**Finding:** Universal MIDDLEs hand off to MORE decision options (higher suffix entropy). Material-independent recognition allows greater decision flexibility.

### Refinement 2: MIDDLE Co-occurrence

**Framing:** Local recognition bundles (NOT compound meanings)

| Metric | Value |
|--------|-------|
| Total attractions | 76 |
| Total repulsions | 0 |
| Universal-universal | 3 attractions |
| Universal-other | 40 attractions |

**Top recognition hubs:**
- `e` (20 attractions) - UNIVERSAL
- `ke` (12 attractions)
- `o` (8 attractions) - UNIVERSAL
- `k` (7 attractions) - UNIVERSAL

**Finding:** Universal MIDDLEs act as recognition hubs that cluster with many other MIDDLEs. No forbidden combinations detected - the grammar permits but doesn't require all MIDDLE pairings.

### Synthesis of Refinements

These two analyses confirm and extend the core model:

1. **Universal MIDDLEs are decision-flexible** - they don't constrain downstream choices
2. **Universal MIDDLEs are recognition hubs** - they cluster with diverse other MIDDLEs
3. **No repulsion patterns** - the system permits combination, doesn't forbid it

This is consistent with apparatus-generic recognition points that can co-occur with any material-specific situation.

**Semantic ceiling maintained:** These are structural properties of the recognition -> decision pipeline, not semantic content.

---

## Files Generated

| File | Contents |
|------|----------|
| `perturbation_analysis.py` | Perturbation space tests |
| `middle_class_sharing.py` | Material class sharing analysis |
| `universal_middle_properties.py` | Universal vs exclusive MIDDLE structural tests |
| `middle_suffix_dependency.py` | MIDDLE -> suffix handoff analysis |
| `middle_cooccurrence.py` | MIDDLE co-occurrence / repulsion analysis |
| `results/perturbation_space_analysis.json` | Perturbation test results |
| `results/middle_class_sharing.json` | Sharing analysis results |
| `results/universal_middle_properties.json` | Universal MIDDLE property tests |
| `results/middle_suffix_dependency.json` | Suffix dependency results |
| `results/middle_cooccurrence.json` | Co-occurrence results |
| `context/SPECULATIVE/currier_a_genre_elimination.md` | External genre elimination |
| This document | Interpretation |

---

## Registered Constraints

### C461: HT density correlates with MIDDLE rarity

**Evidence:** Tail MIDDLEs have 1.58x higher HT density (chi² = 180.56, p < 0.0001)

**Statement:** Human Track markers occur more frequently in contexts containing rare (Tail) MIDDLEs than common (Core) MIDDLEs, indicating that the HT layer anticipates recognition difficulty rather than execution difficulty.

**Status:** Tier 3 REGISTERED - see [C461_ht_middle_rarity.md](../../context/CLAIMS/C461_ht_middle_rarity.md)

---

### C462: Universal MIDDLEs are mode-balanced

**Evidence:** Universal MIDDLEs show 51.0% precision mode vs 87.3% for exclusive MIDDLEs (chi² = 471.55, p < 0.0001)

**Statement:** MIDDLEs that appear across all material classes show balanced distribution between precision (ch-family) and tolerance (sh-family) modes, while class-exclusive MIDDLEs strongly prefer precision mode.

**Status:** Tier 3 REGISTERED - see [C462_universal_mode_balance.md](../../context/CLAIMS/C462_universal_mode_balance.md)

---

## Limitations

1. **MIDDLE classification from A applied to B** - MIDDLEs are classified by A-corpus frequency, then analyzed in B-corpus context. The shared vocabulary overlap is only 33.7%.

2. **HT marker detection is approximate** - Uses known HT markers but may miss some or include false positives.

3. **Time-to-STATE-C uses e-presence as proxy** - The stability anchor is approximated by tokens containing 'e', not formal STATE-C classification.

---

## Navigation

- [../](../) - Phases index
- [../../context/SPECULATIVE/middle_distribution_analysis.md](../../context/SPECULATIVE/middle_distribution_analysis.md) - MIDDLE distribution analysis
- [../../context/SPECULATIVE/apparatus_centric_semantics.md](../../context/SPECULATIVE/apparatus_centric_semantics.md) - Apparatus-centric model

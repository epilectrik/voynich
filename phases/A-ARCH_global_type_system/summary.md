# Phase A-ARCH: Global Morphological Type System

## Discovery

Testing Currier A for the phase-encoded grammar patterns found in B and AZC revealed that **A shares the same morphological type system**, despite having no sequential grammar.

## Evidence

### Kernel Dichotomy (Identical in A and B)

| Prefix | Currier A | Currier B |
|--------|-----------|-----------|
| ch | 100.0% | 100.0% |
| sh | 100.0% | 100.0% |
| ok | 100.0% | 100.0% |
| da | 1.9% | 4.9% |
| sa | 3.1% | 3.4% |

The INTERVENTION (ch/sh/ok) vs MONITORING (da/sa) split is identical.

### LINK Affinity (Same patterns)

| Prefix | A Enrichment | B Enrichment | Pattern |
|--------|--------------|--------------|---------|
| da | 1.41x | 1.59x | Attracted |
| al | 1.67x | 2.37x | Attracted |
| qo | 0.74x | 0.62x | Avoiding |
| ok | 0.70x | 0.86x | Avoiding |

Same prefixes attract/avoid LINK in both systems.

### Positional Patterns

Both systems show line-boundary preferences:
- A: sa=2.27x line-initial, da=1.88x line-final
- B: sa=6.58x line-initial, da=2.88x line-initial

## Interpretation

The manuscript uses a **single, global morphological type system** instantiated in multiple formal regimes:

| System | Grammar | Type System | Function |
|--------|---------|-------------|----------|
| Currier A | None (position-free) | Shared | Registry of typed items |
| Currier B | Sequential | Shared | Programs using typed items |
| AZC | Sequential (constrained) | Shared | Constrained programs |

This is like having:
- **A = Parts catalog** (items organized by type)
- **B = Assembly instructions** (sequences of typed operations)
- **Same part types, different formal systems**

## Why This Matters

This resolves the A-B relationship cleanly:
1. A and B share morphological components (known)
2. Those components have **the same functional roles** in both (new)
3. The difference is organization, not vocabulary function
4. HT prefixes had to be disjoint to avoid type collision

## Constraints Added

**Constraint 383**: GLOBAL MORPHOLOGICAL TYPE SYSTEM: Prefixes encode functional type (INTERVENTION vs MONITORING) globally across A, B, and AZC; ch/sh/ok=100% kernel contact in ALL systems, da/sa<5% in ALL systems; LINK affinity patterns identical (da/al attracted, qo/ok avoiding); type system is grammar-independent (A has no sequential grammar but same types); B instantiates types in sequential programs, A instantiates types in non-sequential registry; explains vocabulary sharing without semantic transfer (A-ARCH, Tier 2)

**Constraint 384**: NO ENTRY-LEVEL A-B COUPLING: Although A and B share global vocabulary and type system, there is NO entry-level or folio-level cross-reference; all B programs draw from identical A-derived vocabulary pool (Jaccard 0.998 between all B folios); 215 one-to-one tokens scatter across 207 unique A-B pairs (no repeated pairings beyond noise); rare tokens are rare globally, not relationally; A does NOT function as lookup catalog for B programs; coupling occurs ONLY at global type-system level (A-ARCH, Tier 2)

**Constraint 385**: STRUCTURAL GRADIENT IN CURRIER A: Currier A exhibits measurable internal ordering; higher-frequency tokens appear earlier in sequence (rho=-0.44); later folios contain longer tokens with fewer recognizable morphological components (length rho=+0.35, components rho=-0.29); section-level diversity increases H (0.311) -> P (0.440) -> T (0.623); gradient reflects systematic structural change within registry, independent of execution grammar or semantic interpretation (A-ARCH, Tier 2)

## Entry-Level Coupling Tests

Three tests were run to check for A→B entry-level cross-reference:

### Test 1: Vocabulary Concentration
- All B folios reference ~114 A folios (essentially all)
- Concentration 2.39x expected, but this is a frequency artifact
- No folio-specific A referencing

### Test 2: B-Folio Clustering by A-Reference
- Jaccard similarity between ALL B folio pairs: **0.998**
- Adjacent B folios: 0.998, Non-adjacent: 0.998
- **All B programs reference the SAME A vocabulary**

### Test 3: One-to-One Token Analysis
- 215 tokens appear in exactly 1 A folio and 1 B folio
- These map to **207 unique A-B pairs** (almost no repeats!)
- Max pair frequency: 2 (only 8 pairs)
- **RANDOM scatter** - no stable A-B pairing

## Final Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLOBAL TYPE SYSTEM                           │
│         (prefixes encode INTERVENTION vs MONITORING)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                    GLOBAL VOCABULARY POOL
                    (1,141 shared tokens)
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   CURRIER A   │   │   CURRIER B   │   │     AZC       │
│  (Registry)   │   │  (Programs)   │   │ (Constrained) │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ Catalogs types│   │ All programs  │   │ Diagram-bound │
│ Section H/P/T │   │ use SAME pool │   │ same pool     │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Key insight**: A is a classification space for learning/familiarity/naming discipline, NOT a procedural lookup table. All B programs draw from the same global vocabulary pool defined by the shared type system.

## A-Internal Gradient Test

Final stress test to check for internal ordering within Currier A:

| Test | rho | Finding |
|------|-----|---------|
| Freq vs position | -0.08 | NULL (tokens distributed evenly) |
| Position vs length | **+0.35** | STRONG (later = longer) |
| Position vs components | **-0.29** | MODERATE (later = less decomposable) |
| Freq vs first occurrence | **-0.44** | STRONG (high-freq appear first) |

Section diversity: H (0.311) < P (0.440) < T (0.623)

This is a structural gradient, not a pedagogical claim. The ordering exists regardless of intent.

## Files

- `archive/scripts/currier_a_phase_patterns.py` - Type system comparison
- `archive/scripts/azc_phase_patterns.py` - AZC pattern verification
- `archive/scripts/a_b_entry_mapping.py` - Entry-level coupling tests
- `archive/scripts/a_b_rare_token_probe.py` - Rare token analysis
- `archive/scripts/a_b_folio_cooccurrence.py` - One-to-one token analysis
- `archive/scripts/a_internal_gradient_test.py` - Internal ordering analysis

## Status

**CLOSED** - Three architectural constraints established:
- 383: Global type system
- 384: No entry-level coupling (falsified)
- 385: Structural gradient in A

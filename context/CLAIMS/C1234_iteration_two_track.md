# C1234 - Iteration Two-Track System

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

Iteration atoms form a two-track system: iin at line-initial (29.6%, infrastructure prefixes da/sa/ta/ka) for cycle setup, aiin at penultimate (14.1%, 1.35x enriched, scaffold/energy prefixes ok/ot/lk) for bounded loop control. ii = formal bounded cycling (92.6% n-accompanied, default form per C1204), i = open cycling (52.9% n-accompanied). ii is enriched at line-initial (1.46x) and depleted at line-final (0.62x).

## Evidence

### Iteration atom profiles

| Atom | Count | Mean position | Key positional signal |
|------|-------|---------------|----------------------|
| aiin | 834 | 0.526 | Penultimate enrichment 1.35x, line-final depleted 0.59x |
| iin | 560 | 0.393 | Line-initial rate 29.6% |

### Extension form distribution

| Form | Count | % of tokens | n-accompanied |
|------|-------|-------------|---------------|
| ii (formal bounded) | 2328 | 10.9% | 92.6% |
| i (open cycling) | 1828 | 8.6% | 52.9% |

The inverted gradient (ii more common than i) confirms C1204.

### Positional enrichment for ii

| Position | Enrichment |
|----------|------------|
| Line-initial | 1.46x |
| Line-final | 0.62x (depleted) |

### Prefix pairing

| Track | Prefixes | Context |
|-------|----------|---------|
| iin (line-initial) | da, sa, ta, ka | Infrastructure prefixes — cycle setup |
| aiin (penultimate) | ok, ot, lk, ol | Scaffold/energy prefixes — bounded loop control |

## Interpretation

The iteration system has two distinct tracks that serve different roles within the line. iin at line-initial sets up the cycling context (infrastructure), while aiin near line-end provides bounded loop control (scaffold/energy). The two forms are positionally complementary, not interchangeable.

## Related constraints

- C1195: i = cycle/iterate (LOCKED)
- C1204: i-extension inverted gradient
- C1205: i orthogonal to k/e

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/iteration_atom_analysis.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/extension_analysis.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/iteration_atom_analysis.json`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/extension_analysis.json`

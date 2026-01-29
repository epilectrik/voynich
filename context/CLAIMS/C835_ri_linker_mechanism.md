# C835: RI Linker Mechanism

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

4 RI tokens create 12 directed links connecting 12 folios through a FINAL->INITIAL bridging mechanism. Links flow predominantly forward (66.7%) with mean distance +6.6 folios.

## Evidence

From t18_ri_link_network.py:

**The 4 Linkers:**

| Token | FINAL (source) in | INITIAL (target) in | Links |
|-------|-------------------|---------------------|-------|
| cthody | f21r, f53v, f54r, f87r, f89v1 | f93v | 5 |
| ctho | f27r, f30v, f42r, f93r | f32r | 4 |
| ctheody | f53v, f87r | f87r | 2 |
| qokoiiin | f89v1 | f37v | 1 |

**Network Properties:**

```
Total directed links: 12
Unique folio pairs: 12
Folios in network: 12

Direction distribution:
  Forward (to later folio): 8 (66.7%)
  Backward (to earlier folio): 3 (25.0%)
  Same folio (self-loop): 1 (8.3%)

Distance statistics:
  Mean: +6.6 folios
  Range: -61 to +72
```

**Hub Structure:**

- f93v: 5 incoming links (major collector)
- f32r: 4 incoming links
- f53v, f87r, f89v1: 2 outgoing each

## Topology: Convergent (Many-to-One)

Critical structural property: each linker appears as INITIAL in exactly ONE folio but as FINAL in MULTIPLE folios.

| Linker | FINAL in | INITIAL in | Ratio |
|--------|----------|------------|-------|
| cthody | 5 folios | 1 folio | 5:1 |
| ctho | 4 folios | 1 folio | 4:1 |
| ctheody | 2 folios | 1 folio | 2:1 |
| qokoiiin | 1 folio | 1 folio | 1:1 |

This is **convergence** (many sources → one destination), NOT distribution (one source → many destinations).

## Interpretation (Tier 3 - Two Alternatives)

The convergent topology supports two mutually exclusive interpretations that cannot be distinguished from structure alone:

### Interpretation A: AND (Constraint Aggregation)

```
f21r ──┐
f53v ──┼──→ f93v requires ALL FIVE conditions satisfied
f54r ──┤
f87r ──┤
f89v1 ─┘
```

- Collector record specifies compound constraints
- All prerequisite records must be completed
- Physical analog: compound product requiring 5 ingredients

### Interpretation B: OR (Candidate Alternatives)

```
f21r ──┐
f53v ──┼──→ f93v accepts ANY of these as valid input
f54r ──┤
f87r ──┤
f89v1 ─┘
```

- Collector record accepts alternative sources
- Any one prerequisite is sufficient
- Physical analog: 5 equivalent suppliers for same ingredient

### Why Both Are Plausible

| Evidence | Supports AND | Supports OR |
|----------|--------------|-------------|
| Hub structure | Aggregation point | Central routing |
| Forward bias | Prerequisite chain | Process progression |
| Sparse linking | Rare compounds | Rare equivalences |
| 95% singletons | Most are unique | Few have alternatives |

**The ambiguity may be deliberate** - a compact encoding where context determines whether AND or OR applies. This would be efficient for practitioners but opaque to outsiders.

## Structural Properties (Tier 2)

Regardless of interpretation, these are confirmed:

1. **Convergent topology** - Many-to-one, not one-to-many
2. **Hub structure** - f93v (5 inputs), f32r (4 inputs)
3. **Forward bias** - 66.7% of links go to later folios
4. **Sparse connectivity** - Only 0.6% of RI serve as linkers
5. **Self-reference** - f87r has a self-loop (ctheody)

## Provenance

- t18_ri_link_network.json: total_links=12, forward_links=8, mean_distance=+6.6
- Related: C831 (three-tier structure), C836 (ct-prefix signature)

## Status

CONFIRMED - Link network is structurally verified with reproducible topology.

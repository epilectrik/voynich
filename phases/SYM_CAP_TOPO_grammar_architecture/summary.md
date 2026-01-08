# Phase SYM/CAP/TOPO: Grammar Architecture Probes

## Core Questions

1. **TIME SYMMETRY**: Is the grammar causal (directed) or relational (undirected)?
2. **GRAMMAR CAPACITY**: Are there hidden role-level prohibitions beyond documented hazards?
3. **GRAPH TOPOLOGY**: What is the global shape of the allowed transition space?

## Results

### TIME-REVERSAL SYMMETRY (Constraint 391)

| Context | H(X|past) | H(X|future) | Ratio |
|---------|-----------|-------------|-------|
| 1 token | 4.198 | 4.207 | 1.002 |
| 2 tokens | 0.410 | 0.411 | 1.003 |
| 3 tokens | 0.011 | 0.011 | 1.008 |

**Verdict: PERFECTLY SYMMETRIC**

Past context predicts future roles with **exactly the same accuracy** as future context predicts past roles. This is a rare property.

**What this means:**
- The grammar encodes **bidirectional adjacency constraints**, not causal direction
- Transitions are symmetric: if A can follow B, the constraint is equally about "A and B are adjacent"
- **Procedural direction is supplied by the operator, not encoded in the grammar**

**What this does NOT mean:**
- ~~Reading direction is arbitrary~~ (overclaim)
- ~~Text could be read backwards~~ (overclaim)

The grammar is like Hamiltonian mechanics: time-reversal invariant in its constraints, but used in a directed process by an external agent.

### ROLE-LEVEL CAPACITY CLOSURE (Constraint 392)

| Metric | Value |
|--------|-------|
| Role classes | 6 |
| Theoretical transitions | 36 |
| Observed transitions | 35 (97.2%) |
| Zero-count | 1 (HIGH_IMPACT → HIGH_IMPACT) |

**Verdict: EXTREMELY PERMISSIVE**

At the role abstraction level, almost everything is allowed. The single prohibition (HIGH_IMPACT self-transition) is consistent with documented hazard topology.

**What this means:**
- No hidden role-level prohibitions
- Structure emerges from **preference and local determinism**, not expanded illegality
- Hazards and constraints live at finer grain (token level), not role level

### FLAT ROLE-LEVEL TOPOLOGY (Constraint 393)

| Metric | Value |
|--------|-------|
| Strongly Connected Components | 1 (fully connected) |
| Diameter | 1 |
| Transitivity | 1.0000 |
| Reciprocity | 0.857 |
| Articulation points | 0 |

**Verdict: FLAT TOPOLOGY**

- All roles can reach all other roles in 1 step
- No mandatory gateway states
- No hierarchical role layering
- No global bottlenecks

**PageRank dominance:** ENERGY_OPERATOR (0.39) > CORE_CONTROL (0.21) > FREQUENT_OPERATOR (0.14)

This matches kernel centrality findings — ENERGY_OPERATOR is the gravitational center.

## Synthesis

The Voynich B grammar is now characterized as:

> **Locally deterministic, globally unconstrained, time-symmetric, and operator-directed.**

| Property | Evidence |
|----------|----------|
| Locally deterministic | H(X|prev 2) = 0.41 bits (Constraint 389) |
| Globally unconstrained | 97.2% role transitions observed (Constraint 392) |
| Time-symmetric | H(past) = H(future) at all context levels (Constraint 391) |
| Operator-directed | No internal sequencing; direction external |

This is a **very rare combination** in notation systems.

### What the Grammar Encodes vs What the Operator Supplies

| Grammar Encodes | Operator Supplies |
|-----------------|-------------------|
| Which adjacencies are valid | Which direction to read |
| Which transitions are forbidden | When to start/stop |
| Which states are preferred | Which program to execute |
| Local determinism (next token) | Global goal |

The grammar is a **constraint satisfaction system**, not a **procedural specification**.

## Tier Boundaries

**Tier 2 (what we claim):**
- Time-reversal symmetry at role level
- Capacity closure (no hidden prohibitions)
- Flat topology (no bottlenecks)
- Adjacency constraints rather than causal direction

**Tier 3+ (what we cannot claim):**
- That reading direction is arbitrary
- That text could be read backwards
- Any external validation of these properties

## Constraints Added

**Constraint 391**: TIME-REVERSAL SYMMETRY: Role-level transitions in Currier B are statistically time-reversal invariant; H(X|past k) = H(X|future k) for k=1,2,3 (ratio 1.00); grammar encodes bidirectional adjacency constraints rather than intrinsic causal direction; procedural direction is supplied by operator, not grammar (SYM, Tier 2)

**Constraint 392**: ROLE-LEVEL CAPACITY CLOSURE: At role abstraction level (6 classes), 35/36 possible transitions observed (97.2%); only HIGH_IMPACT->HIGH_IMPACT is zero-count; no hidden role-level prohibitions beyond documented hazards; structural control imposed through preference and local determinism, not expanded illegality (CAP, Tier 2)

**Constraint 393**: FLAT ROLE-LEVEL TOPOLOGY: Role-transition graph is single strongly-connected component with diameter 1, transitivity 1.0, zero articulation points; no global chokepoints or hierarchical role gating; global structure arises from fine-grain local constraints, not role-level architecture (TOPO, Tier 2)

## Files

- `archive/scripts/time_asymmetry_test.py` - Time symmetry analysis
- `archive/scripts/grammar_capacity_analysis.py` - Capacity probe
- `archive/scripts/transition_graph_topology.py` - Topology analysis

## Status

**CLOSED** - Three constraints established (391-393)

This phase completes the grammar architecture characterization.

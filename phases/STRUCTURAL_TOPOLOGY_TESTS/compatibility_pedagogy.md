# Test 5: Compatibility-Driven Pedagogy

**Question:** Is A-registry ordering governed by incompatibility space topology, not just human memory?

**Verdict:** TOPOLOGY_CONSTRAINED - Ordering serves graph navigation, not just memory

---

## Background

### Expert Hypothesis

> "Some discriminators *must* be introduced early because they serve as **bridges** between otherwise incompatible regimes."

### Combining Multiple Constraints

| Constraint | Finding |
|------------|---------|
| C475 | 95.7% MIDDLE pairs are incompatible |
| C476 | 22.3% hub savings vs greedy strategy |
| C478 | Novelty front-loading (21.2% Phase 1) |
| C487 | Memory optimization z=-97 vs random |

**Test Question:** Is the ordering topology-constrained (graph navigation) or just memory-optimized?

---

## Findings

### 1. The Incompatibility Lattice

**From middle_incompatibility.json:**

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| Legal pairs | 30,394 (4.3%) |
| **Illegal pairs** | **673,342 (95.7%)** |
| Connected components | 30 |
| Largest component | 1,141 MIDDLEs (96%) |
| Isolated MIDDLEs | 20 |

**Interpretation:** The discrimination space is a **sparse lattice** where 95.7% of MIDDLE pairs cannot co-occur. Navigation through this space requires careful path selection.

### 2. Hub MIDDLEs as Bridges

**21 Hub MIDDLEs Identified:**

```
'a', 'o', 'e', 'ee', 'eo', 'd', 'y', 'r', 'l', 's', 'i',
'ch', 'ai', 'al', 'eeo', 'eod', 'ed', 't', 'ot', 'op'
```

**Characteristics of Hub MIDDLEs (from C462):**

| Property | Hub MIDDLEs | Exclusive MIDDLEs |
|----------|-------------|-------------------|
| Types | 18 | 573 |
| Token coverage | 44% | 17% |
| Mode balance | 51% | 87% |
| Function | Universal connectors | Specialized discriminators |

**Interpretation:** Hub MIDDLEs have **exceptionally high compatibility** - they can co-occur with many other MIDDLEs. They serve as **bridges** across the sparse incompatibility lattice.

### 3. Evidence for Topology-Constrained Ordering

#### A. Hub Rationing (C476)

| Ordering | Coverage | Hub Usage |
|----------|----------|-----------|
| Real A | 100% | 31.6% |
| Greedy | 100% | 53.9% |
| **Hub Savings** | - | **22.3pp** |

**Interpretation:** The A-registry achieves full coverage while using **22.3 percentage points fewer hubs** than a greedy strategy. This is not random - it's strategic hub rationing that:
1. Reserves hubs for bridging roles
2. Forces navigation through non-hub discriminators
3. Ensures broader coverage of the discrimination space

#### B. Novelty Front-Loading (C478)

| Phase | Novelty Rate | Interpretation |
|-------|--------------|----------------|
| Phase 1 | **21.2%** | Introduce vocabulary early |
| Phase 2 | 9.4% | Reinforcement trough |
| Phase 3 | 11.3% | Ramp up again |

**Interpretation:** Novelty is front-loaded to ensure **bridges are introduced before they're needed**. You cannot navigate to an incompatible region without first having the bridge MIDDLE available.

#### C. PREFIX Cycling (C478)

- 7 prefixes cycle throughout the manuscript
- 164 regime changes documented
- Multi-axis traversal pattern

**Interpretation:** PREFIX cycling forces navigation across different regions of the discrimination space. This requires bridges to be introduced BEFORE the cycling begins.

### 4. The Topology-Pedagogy Connection

**Why graph topology constrains pedagogy:**

1. **Navigation requires bridges:** With 95.7% pairs incompatible, you cannot move freely between discriminators. Hub MIDDLEs enable transitions.

2. **Early bridge introduction is mandatory:** If bridges are introduced late, entire regions of the discrimination space are inaccessible during early learning.

3. **Hub rationing preserves discrimination:** Using too many hubs (like greedy strategy) means less exploration of specialized discriminators. Strategic rationing forces broader coverage.

4. **PREFIX cycling requires cross-domain navigation:** Cycling through 7 prefix domains requires bridges that span PREFIX families.

### 5. Reframing C487: Topology-Constrained Memory Optimization

Original framing (C487):
> A-registry ordering achieves z=-97 vs random for memory retention.

**New framing:**
> A-registry ordering achieves z=-97 WHILE ALSO serving graph navigation constraints. The ordering is **Pareto-optimal** across multiple objectives.

| Objective | How Achieved |
|-----------|--------------|
| Memory retention | z=-97 (vs random) |
| Graph navigation | Front-loaded bridges, hub rationing |
| Coverage completion | 100% with strategic pacing |
| Discrimination variety | PREFIX cycling, hub rationing |

---

## Structural Model: Pedagogy as Graph Navigation

```
INCOMPATIBILITY LATTICE
(95.7% pairs forbidden)
          │
          ▼
┌─────────────────────────────────────┐
│         HUB MIDDLEs (21)            │
│    (Bridges between regions)        │
│  a, o, e, ee, eo, d, y, r, l, s... │
└─────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  PEDAGOGICAL ORDERING CONSTRAINTS   │
│  • Introduce bridges EARLY          │
│  • Ration hubs (22.3% savings)      │
│  • Cycle through PREFIX domains     │
│  • Maintain memory activation       │
└─────────────────────────────────────┘
          │
          ▼
   A-REGISTRY: z=-97 memory optimization
   WHILE navigating topology constraints
```

---

## Conclusion

**Test 5 Verdict: TOPOLOGY_CONSTRAINED**

A-registry ordering is governed by incompatibility topology, not just memory optimization:

1. **95.7% MIDDLE incompatibility** creates a sparse navigation problem
2. **21 hub MIDDLEs** serve as bridges across incompatible regions
3. **Front-loaded novelty (21.2%)** ensures bridges are available early
4. **Hub rationing (22.3% savings)** forces broader discrimination coverage
5. **PREFIX cycling** requires cross-domain navigation via bridges

**Tier 3 Hypothesis:**
> A-registry ordering implements **topology-constrained pedagogy** - the ordering must satisfy graph navigation requirements (bridge availability, cross-domain traversal) while also optimizing memory retention. This explains why ordering is z=-97 but not perfectly optimal: it's Pareto-optimal across multiple structural objectives.

---

## Connection to Medieval Ars Memoria

**Historical Parallel:**

Medieval memory arts (Carruthers) used:
- **Divisio** - cutting into retrievable units
- **Compositio** - building from blocks
- **Progressive illumination** - step-by-step learning

**Voynich Implementation:**
- **Incompatibility lattice** - determines valid units
- **Hub MIDDLEs** - universal building blocks
- **Front-loaded bridges** - enables progressive navigation

The ars memoria techniques operate ON TOP OF the topological constraints. Memory optimization is possible ONLY within the constraints imposed by the incompatibility lattice.

---

## Data Sources

- `results/middle_incompatibility.json` - Incompatibility graph
- `results/coverage_optimality.json` - Hub rationing analysis
- `results/temporal_coverage_trajectories.json` - Novelty front-loading
- `results/memory_optimality.json` - Memory optimization (z=-97)
- `context/CLAIMS/currier_a.md` - C475, C476, C478

## Related Constraints

- C475: MIDDLE Incompatibility (95.7%)
- C476: Coverage Optimality (22.3% hub savings)
- C478: Temporal Scheduling (front-loaded novelty)
- C487: Memory Optimization (z=-97)
- C462: Universal MIDDLE Mode Balance

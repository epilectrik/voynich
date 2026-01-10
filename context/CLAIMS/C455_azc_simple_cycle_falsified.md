# C455: AZC Simple Cycle Topology FALSIFIED

**Tier:** 1 (falsified) | **Status:** CLOSED | **Scope:** AZC

---

## Statement

The hypothesis that **Zodiac AZC represents a simple circulatory cycle** (single ring topology mapping to apparatus stages) is **FALSIFIED**.

Zodiac AZC shows:
- Multiple independent cycles (cycle_rank = 5, not 1)
- Non-uniform degree distribution (CV = 0.817, not 0)
- Interleaved R-S transitions (not pure radial progression)

**This closes the door on:**
- "AZC Zodiac = literal apparatus stage diagram"
- Single-loop circulatory mapping
- Direct apparatus-to-placement correspondence

---

## Evidence

### Test Design (TEST 8 - Internal Topology)

Built directed graph from AZC placement transitions within Zodiac folios.

**Metrics computed:**
- Cycle rank (number of independent cycles)
- Degree coefficient of variation (uniformity)
- Transition patterns (R-series progression)

### Zodiac Results

| Metric | Observed | Pure Cycle (ideal) | Tree (control) |
|--------|----------|-------------------|----------------|
| Cycle rank | 5 | 1 | 0 |
| Degree CV | 0.817 | 0 (uniform) | ~0.5 |
| R-series forward | 0 | n/a | n/a |

### Critical Finding: Interleaved Pattern

Top Zodiac transitions:
```
R1 -> S1: 11
S1 -> R2: 10
R2 -> S2: 11
S2 -> R3: 10
```

This is **NOT** R1->R2->R3->R1 (simple radial cycle).
This is R1->S1->R2->S2->R3 (interleaved spiral).

---

## What This Constraint Claims

- Zodiac AZC is NOT a simple ring/cycle topology
- Multiple cycles exist (cycle_rank > 1)
- Connectivity is non-uniform (high degree variance)
- The "literal apparatus diagram" interpretation is falsified

---

## What This Constraint Does NOT Claim

- AZC has no structure (it does - see C456)
- AZC is random (it shows consistent interleaved pattern)
- Circulatory thinking is irrelevant (weaker version survives)

---

## Architectural Implication

This falsification **redirects** interpretation:

| Interpretation | Status |
|----------------|--------|
| AZC = apparatus stage map | FALSIFIED |
| AZC = single circulatory loop | FALSIFIED |
| AZC = cognitive orientation scaffold | SUPPORTED (see C456) |

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C454** | C455 is independent: internal topology test, not B-coupling test |
| **C456** | C455 is refined by: interleaved spiral is the actual structure |
| **C306-C315** | C455 constrains: AZC structure is more complex than expected |

---

## Phase Documentation

Research conducted: 2026-01-10 (AZC internal topology analysis)

Scripts:
- `phases/exploration/azc_topology_test.py` - Topology analysis

Results:
- `results/azc_topology_analysis.json`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

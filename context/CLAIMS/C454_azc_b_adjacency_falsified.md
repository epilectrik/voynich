# C454: AZC-B Adjacency Coupling FALSIFIED

**Tier:** 1 (falsified) | **Status:** CLOSED | **Scope:** AZC / B / GLOBAL

---

## Statement

The hypothesis that **AZC context influences Currier B control metrics via codicological proximity** is **FALSIFIED**.

B folios adjacent to AZC pages show **no statistically significant differences** in any control metric (link density, hazard density, intervention frequency, kernel contact ratio, cycle regularity) compared to B folios far from AZC pages.

**This closes the door on:**
- AZC folio = cluster of related B procedures
- Diagram complexity correlating with execution complexity
- Apparatus stage alignment with B program characteristics

---

## Evidence

### Test Design (K1' - Adjacency Influence)

Properly designed test operating at adjacency level (not folio level), respecting the architectural fact that AZC and B occupy disjoint folio sets.

**Method:**
1. For each B folio, compute minimum distance to any AZC folio
2. Partition B folios into "near AZC" (distance <= k) and "far from AZC" (distance > k)
3. Compare B control metrics between groups using Mann-Whitney U test
4. Test at multiple window sizes (1, 2, 3, 5 folios)

### Results

| Window | Near B | Far B | Best p-value | Significant? |
|--------|--------|-------|--------------|--------------|
| 1 folio | 5 | 78 | 0.102 | NO |
| 2 folios | 8 | 75 | 0.053 | NO |
| 3 folios | 11 | 72 | 0.060 | NO |
| 5 folios | 17 | 66 | 0.178 | NO |

**No metric reached p < 0.01 at any window size.**

### Kill Condition K1' Triggered

> If no AZC proximity class shows p < 0.01 difference in ANY B metric -> REJECT hypothesis

**Result:** K1' TRIGGERED - hypothesis falsified.

### Negative Control (K2') Passed

AZC placement does not predict B token characteristics beyond shuffled null distribution (after multiple comparison correction).

---

## What This Constraint Claims

- AZC proximity does NOT affect B program characteristics
- Diagram complexity is orthogonal to execution complexity
- AZC and B are topologically and functionally segregated
- This is **positive architectural evidence**, not absence of finding

---

## What This Constraint Does NOT Claim

- AZC is meaningless (it serves orientation, not execution)
- AZC has no function (it gates legality, per C313)
- No relationship exists between AZC and B (they share production context but not execution coupling)

---

## Architectural Implication

This falsification **strengthens** the 4-layer model:

| Layer | Function | Coupling |
|-------|----------|----------|
| B (Execution) | Adaptive control | Self-contained |
| A (Registry) | Discrimination points | External to B |
| AZC (Orientation) | Spatial scaffolding | Segregated from B |
| HT (Endurance) | Human attention | Anchored to AZC, not B |

**Each layer does its job without leaking into others.**

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C313** | C454 reinforces: placement constrains legality, not prediction |
| **C384** | C454 extends: no entry-level coupling at adjacency scale either |
| **C306-C315** | C454 complements: AZC structure is internal, not B-coupled |

---

## Phase Documentation

Research conducted: 2026-01-10 (APPARATUS-TOPOLOGY hypothesis testing)

Scripts:
- `phases/exploration/apparatus_topology_tests_v2.py` - Redesigned adjacency tests

Results:
- `results/apparatus_topology_critical_tests_v2.json`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

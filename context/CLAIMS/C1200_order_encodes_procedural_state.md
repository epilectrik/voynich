# C1200: Order Encodes Procedural State

**Tier:** 2
**Scope:** B
**Phase:** ATOM_EXTENSIBILITY (Phase 425)
**Depends on:** C1198 (distributional equivalence of reordered MIDDLEs)

## Constraint

While reordered MIDDLEs (ke vs ek) are distributionally equivalent (C1198), atom ordering within MIDDLEs encodes **procedural state carry-over** detectable through sequential transition analysis.

### Evidence 1: Terminal-to-Initial Bias (T6a)

| Previous ends with | Next starts with e | Next starts with k |
|--------------------|-------------------|-------------------|
| k (hot state) | **70.6%** | 29.4% |
| e (cool state) | 58.2% | **41.8%** |

Carryover signal: +0.123 in both directions (symmetric). Permutation test p<0.001.

After a hot-terminal step, the system preferentially begins with cooling. After a cool-terminal step, it preferentially begins with heating.

### Evidence 2: ke vs ek Preceding Context (T6b)

| Target | Predecessors ending in k | Predecessors ending in e |
|--------|-------------------------|-------------------------|
| EK (cool-first) | **18.9%** | 5.3% |
| KE (heat-first) | 11.9% | **21.2%** |

The system selects EK after hot steps and KE after cool steps.

### Evidence 3: Asymmetric Alternation (T6c)

| After | Switch preference | Stay preference | Alternation ratio |
|-------|------------------|----------------|-------------------|
| K-DOM | 30.7% -> E-DOM | 15.8% -> K-DOM | **1.94x** (prefers switching) |
| E-DOM | 18.1% -> K-DOM | 30.4% -> E-DOM | **0.60x** (prefers staying) |

Heating alternates to cooling (1.94x), but cooling persists (0.60x). Consistent with a fixed heat source where heating is the active/marked operation and cooling is the default/passive state.

### Evidence 4: Line Boundary Reset (T6d)

| Scope | Carryover signal |
|-------|-----------------|
| Within-line | +0.247 (strong) |
| Across-line | +0.021 (near zero) |

Carryover is 12x stronger within lines. State resets at line boundaries. Lines are independent procedural units.

## Relationship to C1198

C1198 and C1200 are complementary, not contradictory:
- **C1198**: ke and ek occupy the same grammatical slots (section, position, prefix/suffix context)
- **C1200**: ke and ek carry different procedural implications detectable through sequential context

The grammar treats them equivalently. The procedural sequence does not.

## Falsification

Would be falsified if the carryover signal disappears under a more controlled analysis (e.g., controlling for MIDDLE frequency, section, or line position), revealing it as a confound rather than genuine state tracking.

## Provenance

- `phases/ATOM_EXTENSIBILITY/scripts/order_carryover_test.py` (T6a-T6d)
- `phases/ATOM_EXTENSIBILITY/results/order_carryover_results.json`

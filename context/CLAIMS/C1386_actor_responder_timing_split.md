# C1386: ACTOR/RESPONDER Terminal-Atom Timing Split

**Tier:** 2
**Scope:** B
**Phase:** L_ATOM_SEMANTIC_DEEP_DIVE (Phase 496)
**Date:** 2026-03-03
**Depends on:** C1209 (positional grammar), C1208 (carryover classification), C976 (macro-automaton)

## Statement

Terminal atoms partition into three timing classes based on their position relative to macro-state transitions within lines. For each token, the fraction of occurrences that follow a macro-state change (i.e., the preceding token has a different macro-state) reveals a clean three-way split:

| Class | Atoms | Post-change rate | Behavior |
|-------|-------|-----------------|----------|
| **ACTOR** | e(18.4%), h(29.1%), k(31.8%), t(30.4%) | 18-32% | Precede state changes (cause/initiate transitions) |
| **NEUTRAL** | d(38.3%), i(48.7%), o(42.4%), y(43.9%) | 38-49% | No timing preference |
| **RESPONDER** | l(68.9%), m(78.2%), n(63.6%), r(72.6%) | 64-78% | Follow state changes (respond to/assess transitions) |

The gap between ACTOR and RESPONDER ranges is 31.8 percentage points (k=31.8% to n=63.6%), with NEUTRAL atoms filling the middle. This classification is:
- **Orthogonal to C1208** (carryover): l is NEUTRAL carryover but RESPONDER timing; k is POSITIVE carryover but ACTOR timing
- **Orthogonal to C1209** (within-MIDDLE position): TERMINAL slot atoms appear in all three timing classes
- **Consistent with C1200** (order encodes procedural state): the timing split reveals what "procedural state" means at the macro-automaton level

ACTORS correspond to the kernel operators (k, h, e) plus transfer (t) — atoms that drive state transitions. RESPONDERS correspond to state-reading (l, r), final/closure (m), and steady-state (n) atoms — atoms that assess or consolidate after transitions.

## Evidence

### E1: Post-state-change rates (P-L15 Test 3)

For each token at position i>0 in a line, computed whether the preceding token (position i-1) had a different macro-state (C976). Then aggregated by the current token's terminal atom.

| Atom | Post-change | After-same | Total | Post-change % |
|------|-----------|------------|-------|---------------|
| e | 18.4% | 81.6% | — | ACTOR |
| h | 29.1% | 70.9% | — | ACTOR |
| t | 30.4% | 69.6% | — | ACTOR |
| k | 31.8% | 68.2% | — | ACTOR |
| d | 38.3% | 61.7% | — | NEUTRAL |
| o | 42.4% | 57.6% | — | NEUTRAL |
| y | 43.9% | 56.1% | — | NEUTRAL |
| i | 48.7% | 51.3% | — | NEUTRAL |
| n | 63.6% | 36.4% | — | RESPONDER |
| l | 68.9% | 31.1% | — | RESPONDER |
| r | 72.6% | 27.4% | — | RESPONDER |
| m | 78.2% | 21.8% | — | RESPONDER |

Baseline across all atoms: 47.2%.

### E2: Interpretation consistency

| Class | Atoms | Gloss pattern | Operational role |
|-------|-------|--------------|-----------------|
| ACTOR | e(cool), k(heat), h(watch), t(transfer) | Active operations | Drive transitions |
| NEUTRAL | d(mark), o(work), y(end), i(iterate) | Mixed/generic | No timing bias |
| RESPONDER | l(state), m(final), n(halt), r(input) | Assessment/closure | Follow transitions |

The ACTOR class contains exactly the kernel operators (C521: k, h, e) plus t (transfer). The RESPONDER class contains atoms associated with observation, conclusion, or continuation.

## Relationship to Existing Constraints

- **C1200** (Tier 2): Order encodes procedural state. C1386 specifies what procedural state means at macro-automaton granularity: ACTORS initiate state changes, RESPONDERS follow them.
- **C1208** (Tier 2): Carryover classification (POSITIVE/NEGATIVE/NEUTRAL). Orthogonal: k is POSITIVE carryover + ACTOR, l is NEUTRAL carryover + RESPONDER, e is NEGATIVE carryover + ACTOR.
- **C1209** (Tier 2): Positional grammar (INITIAL/TERMINAL/FREE). Orthogonal: TERMINAL-slot atoms appear in all three timing classes (m=RESPONDER, h=ACTOR, y=NEUTRAL).
- **C976** (Tier 2): 6-state macro-automaton. C1386 uses C976 states to define the transition signal.
- **C1383** (Tier 2): n-terminal boundary avoidance. Consistent: n is a RESPONDER (63.6% post-change) that responds to transitions but avoids being AT boundaries.

## Falsification

Would be falsified if:
1. The three-way partition were shown to be an artifact of MIDDLE frequency or length (high-frequency MIDDLEs might inherently appear more after transitions due to base rates)
2. Within-section analysis showed the partition inverts or disappears in specific sections
3. A shuffle test randomizing macro-state labels reproduced the split magnitude

## Provenance

- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_l15_state_condition_marker.py` — Test 3 produces the timing data
- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/results/l_atom_prediction_results.json` — P-L15 structured results

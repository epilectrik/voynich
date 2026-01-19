# Constraint Flow Visualizer

A control-system visualizer demonstrating the A->AZC->B pipeline.

## What This Is

This app shows **option space contraction** - how the reachable grammar shrinks
under AZC legality fields without the grammar itself changing.

**This is NOT:**
- A decoder or translator
- A filter or recommender
- A similarity matcher

**This IS:**
- A reachable-state explorer for a grammar under environmental constraints
- A control-system visualizer showing shrinking option space

## Core Conceptual Model

> Currier A specifies constraint bundles (what must not be confused).
> AZC projects those bundles into position-indexed legality fields (when things are allowed).
> Currier B executes blind grammar within the shrinking reachable space.
>
> No semantics. No branching. No lookup.

## Pipeline

```
Currier A entry
   | (morphology decomposition)
   v
Constraint bundle (PREFIX set, MIDDLE set)
   | (C441-C444, C468-C472)
   v
AZC legality projection (zone-indexed)
   | (reachability suppression)
   v
Zone-dependent reachable grammar
   |
   v
Reachable Currier B folios
```

## Key Design Principles

1. **Baseline vs Conditioned**: Always show the full 49-class grammar alongside
   the conditioned (pruned) view. Grammar never changes - only what is reachable.

2. **Zone-Indexed Reachability**: AZC is not just "what's allowed" but WHEN it
   is allowed. Reachability is computed per-zone (C, P, R1, R2, R3, S).

3. **Binary Classification First**: Folios are REACHABLE, CONDITIONAL, or
   UNREACHABLE before any percentage scores.

4. **Field-Like Visualization**: AZC should feel like a legality field with
   fading/disappearance, not a checklist with toggles.

## Language Discipline

**Allowed:** "reachable under", "legality field", "unavailable", "option space
contracts", "grammar remains unchanged"

**Forbidden:** "selects", "activates", "triggers", "matches", "corresponds to",
"predicts", "recommends"

AZC never selects. Currier A never calls. Currier B never decides.

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Epistemic Note

The atomic vs decomposable hazard class distinction used in this app is a
**mechanism-level explanation** valid for this corpus. It is NOT an architectural
invariant - different instantiations of the same control architecture could
realize hazards differently. The structural contracts (CASC, AZC-ACT, AZC-B-ACT,
BCSC) remain unchanged.

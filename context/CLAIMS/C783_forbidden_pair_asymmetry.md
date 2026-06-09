# C783: Forbidden Pair Asymmetry

**Tier:** 2 (Validated)

> **DEMOTED 2->3 (SELF_CITATION_HEAD_TO_HEAD P4a, 2026-06-08) -- REGISTRY COMPRESSION.**
> The class-level projection of the 17 forbidden transitions shows NO suppression: among the 9
> adequately-powered class pairs (within-line shuffle exp >= 5), the forbidden direction occurs
> at aggregate O/E = 1.13 (strict word-adjacency; chain-adjacency 1.05), reciprocal 1.03, and
> one "forbidden" pair (23->9) is ~2x ENRICHED (28 obs vs 11.8 exp). The 8 remaining pairs are
> zero-vs-zero phantom sparsity (C1118/C2023 pattern). "All 17 class pairs are directional" was
> a lossy class-level compression of TOKEN-level facts. **The directional prohibition is real
> ONE LAYER DOWN (C957):** 9 forward token bigrams at 0 observed vs ~37.5 joint expectation
> (P ~ 5e-17) while every reverse flows at-or-above expectation. This also resolves C789's
> puzzling "65% compliance": there was never a class-level prohibition to comply with.
> Audits: `phases/SELF_CITATION_HEAD_TO_HEAD/scripts/p0_preflight_audits.py`,
> `p0b_strict_adjacency_verification.py`.
**Phase:** CONTROL_TOPOLOGY_ANALYSIS
**Scope:** B-GRAMMAR

---

## Constraint

All 17 forbidden class pairs are asymmetric (directional). No symmetric forbidden pairs exist. Hazard is a directed graph, not an undirected constraint.

---

## Quantitative

| Pattern | Count | Pairs |
|---------|-------|-------|
| CC->FQ | 8 | (12,23), (12,9), (17,23), (17,9), (10,23), (10,9), (11,23), (11,9) |
| CC->CC | 4 | (10,12), (10,17), (11,12), (11,17) |
| EN->CC | 4 | (32,12), (32,17), (31,12), (31,17) |
| FQ->FQ | 1 | (23,9) |

- Symmetric pairs: 0
- Asymmetric pairs: 17

---

## Interpretation

Hazard flows in one direction. If A->B is forbidden, B->A is permitted. This creates:
- Clear "upstream" hazard sources (CC Group A: 10, 11)
- Clear "downstream" hazard targets (CC Group B: 12, 17; FQ: 9, 23)
- Directional control flow, not mutual exclusion

---

## Dependencies

- C467 (forbidden pair definitions)
- C782 (CC kernel paradox)

---

## Provenance

```
phases/CONTROL_TOPOLOGY_ANALYSIS/scripts/t2_forbidden_pair_pattern.py
phases/CONTROL_TOPOLOGY_ANALYSIS/results/t2_forbidden_pair_pattern.json
```

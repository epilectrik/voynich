# PHASE_776 — Does B's class-transition structure (C2061/C2067) go beyond its word-boundary rules?

**Status: COMPLETE.**
- **Lock:** `phase776-lock` (42dfe66), pre-registration v3.1.
- **Run:** one pass on B (1,000 EF-K2 permutations, about 1 minute at Idle priority). verify_lock ran first.
- **Raw results committed before this write-up** (9181055).
- **Results check by the lean-expert:** calls correct; three wording fixes applied.
- **Registered:** **C2094** (Tier 2, measurement). **C2061 and C2067 annotated:** their "sequence beyond boundary rules"
  reading moves to Tier 3 under the pre-registered λ2 rule; their measurements against the character 5-gram stand.

## Question
The procedural ("program") reading of B needs sequence. Its last measured leg was the class-transition eigenstructure
(C2061/C2067: λ2 and λ3 of the 49-class transition operator above a character 5-gram null). Is that structure anything
more than B's word-boundary rules (glyph junction coupling C1212/C1563, and the routing of the next token by the
previous token's last two glyph units, C2082) plus folio × line-type composition?

## Result on Currier B (P-text, 21,610 tokens; null EF-K2, 1,000 permutations)
| Statistic | Observed | EF-K2 null (sd) | D | p | Call |
|---|---|---|---|---|---|
| **Class-pair MI (primary)** | 0.2321 bits | 0.2281 (0.0026) | +0.0040 | 0.062 | **ROUTING-REDUCIBLE** |
| λ2 (C2061's statistic) | 0.2057 | 0.2032 (0.0039) | +0.0025 | 0.27 | λ2 rule: **not shown** beyond boundary rules |
| λ3 (C2067's) | 0.1344 | 0.1273 | +0.0071 | 0.17 | covered by the same annotation |

- **The bound.** B's residual class-pair dependence beyond the boundary rules is at most about 0.009 bits (D + 2 sd).
  The weakest of the 35 class or token chains fitted to B's adjacent pairs gave +0.016 (the strongest +0.031, all at
  p ≤ 0.003); the edge-only chains gave −0.003 to +0.004. B sits at the upper edge of the edge-only range, below every
  fitted chain.
- **What carries the dependence.** Under plain EF (own edges fixed, routing not), the same MI is +0.019 above null
  (p 0.001). Fixing the two-unit ending routing brings it to +0.004. B's class dependence beyond its own edges is the
  ending routing.
- **The eigenvalue.** On this population, EF-K2 reproduces 97% of λ2's excess over the within-line shuffle floor
  (obs 0.2057, null 0.2032, floor 0.1225; C2061 reported 0.206 and 0.118 on its own population). Plain EF already
  reproduces about 86% (null 0.1937): most of λ2 is carried by composition and edges, and routing adds the rest. The
  residual +0.0025 is not significant, at a test power of about 0.68 against B-fitted class chains.
- **Residuals (descriptive, uncorrected, not read).** The 50-state MI with UN as its own state is at p 0.013 with the
  raw-adjacent 49-class MI at null (p 0.16): the signature of the audit's UN-placement plant (an edge chain in which
  unmapped tokens tend to follow unmapped tokens), not of class order. EFL-K2 MI p 0.041 and EFL λ2 p 0.006 are two of
  about ten descriptives, uncorrected; EFL λ2 also lights up from routing alone and mislabelled an edge chain in the
  audit. The shape readout is locked off under ROUTING-REDUCIBLE.

## Reading
- **B's class-level sequence is its spelling rules.** Which class follows which is explained by how words join at
  their boundaries (the junction coupling and the two-unit ending routing) together with each page's composition. There
  is no measurable class-to-class dependence left, at the strength any class chain fitted to B would show.
- **The eigenstructure of C2061/C2067 is real but is not sequence beyond boundary rules.** It survived the character
  5-gram because a 5-gram does not reproduce junction routing and composition together; the exact null that fixes them
  does.
- **For the procedural reading:** its last measured leg, class-level transition structure, is not shown. Together with
  C2091 (no recurring 5-token phrase) and C2093 (rank-level neighbour dependence at null within ending contexts), the
  three ways of looking for sequence in B all come back to the boundary rules.
- **Not tested here:** narrow token-level effects (C549, C2056), which an aggregate 49 × 49 MI barely moves; longer
  boundary keys (three glyph units; first unit plus last two), which the audit's plants put at D +0.006 to +0.010, above
  B's +0.004; any within-line residual beyond two-unit routing (a candidate for its own pre-registration).
- It is not evidence of meaninglessness.

## Design history (controls only)
1. **v1** (λ2 under the plain EF null): certification failed. One edge-only chain in ten read as SURVIVES, because EF
   fixes each slot's own edges but not C2082's routing of the next class by the preceding ending.
2. **v2**: the routing-preserving null EF-K2 (cells also keyed by the preceding token's last two glyph units, which is
   invariant under EF) and the class-pair MI as primary (λ2 under EF-K2 had power about 0.5 at α 0.005). Fresh-seed
   certification passed: 10 of 10 edge-only chains ROUTING-REDUCIBLE, 10 of 10 class chains BEYOND ROUTING (z 9–12).
3. **Lean-expert lock audit** (`scripts/audit/`, `results/audit/`): LOCKABLE WITH EDITS. Its plants showed that a
   line-level class latent with no transitions also reads BEYOND ROUTING (so a positive would have been "dependence,
   carrier unresolved"), that longer boundary keys give D between NEG and τ, and that bridging carries UN placement
   into the 49-class MI. It replaced the shape readout with EFL-K2 MI and separated the λ2 rule for C2061/C2067.
4. **Confirmation pass** (wording): v3.1, locked.

## Scripts
| Script | Role |
|---|---|
| `eig776.py` | the statistic, the nulls (EF, EF-K2, EFL, EFL-K2), the edge-only generator |
| `prelock_calib776.py`, `prelock_thresholds776.py`, `prelock_cert776.py` | calibration, thresholds, certification (v1 and v2) |
| `run776.py` | the locked run |
| `audit/audit776.py`, `audit/audit776_linehomog.py` | the lock audit's control-only plants |

## Deviations
None from the locked v3.1 procedure. The design history (v1 → v2 → v3 → v3.1) is recorded in the pre-registration.

# PHASE_776 — Does Currier B's class-transition structure (C2061/C2067) go beyond its word-boundary rules? (pre-registration)

**Status: v3.1, for lock** (the confirmation pass returned LOCKABLE WITH EDITS; its six wording edits are applied; no
call, threshold or sample changed). The lean-expert lock audit of v2 returned LOCKABLE WITH EDITS (audit scripts and plants
committed at a1fe415, `scripts/audit/`, `results/audit/`). Edits 1–6 are applied below. The v2 certification PASSED.
- **v1** (λ2 under the plain edge-frame null EF) **failed certification C1:** one edge-only chain in 10 read as
  SURVIVES (D +0.027, p 0.003). The cause is C2082: the previous ending routes the next token's class, and EF fixes
  each slot's own edges but not that routing, so an edge chain that draws from B's continuations carries class
  information EF cannot reproduce.
- **v2 is the redesign** the v1 rule requires, with no re-tuning: a stricter null that also fixes each slot's
  preceding ending (**EF-K2**), and a primary statistic with enough power under it (the class-pair mutual information;
  λ2 stays as the C2061-specific descriptive). New thresholds come from a fresh design set (seeds 8700+); certification
  uses fresh seeds (8600+); v1's certification is kept as `results/prelock_cert776_v1.json`.

After the lock nothing below may change without a new phase number.

## Origin
- **Where things stand.** The procedural ("program") reading of B needs sequence: what comes next depending on what
  came before. PHASE_774 (C2091) found no recurring 5-token phrase. PHASE_775 (C2093, descriptive) found that once each
  position's glyph edges and page are fixed, neighbour dependence among frequent tokens is small, and within ending
  contexts at null. The one registered leg of sequence structure still standing is the class-transition
  eigenstructure: λ2 and λ3 of the 49-class transition operator exceed a character 5-gram model (C2061, C2067; C2065).
  The research agenda (Tier B #4) asks for a re-run under a null that preserves composition, zones and boundary
  coupling.
- **The question.** Is B's class-to-class dependence anything more than its word-boundary rules, plus folio
  composition? **"Boundary rules" here means exactly:** the glyph junction coupling (C1212/C1563) and the routing of the
  next token by the previous token's last two glyph units (C2082). Longer boundary keys (three units; first unit plus
  last two) are not fixed by the null and, in the audit's plants, give small excesses between NEG and τ (edit 3).

## Statistics
Every token is mapped to its class (CLASS_COSURVIVAL_TEST map: 480 types, 49 classes, about 69.5% of tokens); within
each line unmapped tokens are dropped and their neighbours joined (the BRIDGE convention of PHASE_733); adjacent class
pairs are counted into a 49 × 49 matrix.

- **Primary: MI = I(class_i; class_{i+1})**, the plug-in mutual information (bits) of the pair counts (the C2023
  scalar). **D = MI(B) − mean MI(null); p = (1 + #{null ≥ observed}) / (1 + R).**
- **Descriptive:** λ2 and λ3 of the row-normalised matrix (the C2061/C2067 statistics), the lag-2 MI and λ2, the
  within-line class shuffle floor (C2061's floor), and (edit 5) two un-bridged variants of the MI: the raw-adjacent
  49-class MI (both neighbours classified) and the 50-state MI with UN as its own state. Bridging carries the placement
  of unmapped tokens into the 49-class MI: in the audit, an edge chain in which unmapped tokens tend to follow unmapped
  tokens gave a bridged D of +0.0035 (just under NEG) while its raw-adjacent MI was at null.

**Population note.** PHASE_733 used all non-label placements (2,420 lines); this phase uses the P-text skeleton of
PHASE_756/774/775 (2,299 lines, 21,610 certain tokens, 22 blockers). λ2 is measured afresh on it.

## Nulls
- **EF-K2 (primary).** The header-aware exact edge-frame permutation (PHASE_774/775) with every cell also keyed by the
  slot's preceding-token ending: tokens are permuted within folio × line type among positions that share zone, first
  glyph unit, last two glyph units, **and the last two glyph units of the preceding token** ('^' at a line start or
  after a blocker). Each slot's own last-two signature is fixed under EF, so every slot's preceding ending is invariant
  and the refined cells are consistent under permutation.
  - **Preserved exactly:** every boundary junction; every position's edges; the routing of each slot's token by the
    preceding ending (P(token | own edges, preceding ending, zone, folio × line type)); line lengths; folio
    composition by line type.
  - **Destroyed:** dependence of a token, and so its class, on the preceding token beyond that token's ending.
  - Movable mass on B: 32.5% of positions (structural exposure; edge chains 27%, class chains 19%).
- **EF (descriptive; the v1 null):** the same without the preceding-ending key. It shows how much routing carries.
- **EFL-K2 (descriptive; the shape readout, edit 2):** EF-K2 within the **line**: cells keyed by zone, first glyph
  unit, last two glyph units and the preceding ending, within one line. Exact for any line-level latent. Movable mass
  is small (controls 1–5%; B 3.8%, a declared structural exposure: adjacent edge-pair information). In the
  audit it separated class chains (5 of 5 at p ≤ 0.03) from line-latent, positional, folio, longer-key and UN plants
  (0 of 14).
- **EFL (descriptive, λ2 only):** EF within the line with first and last glyph as the edge signature (about 20%
  movable). The audit found it weak and it no longer enters the wording rule.
- The B run uses 1,000 permutations, seed 77600.

## Reference families (v2 design calibration; `results/prelock_calib776_design2.json`, R = 300)
| Family | What it has | MI excess D under EF-K2 (12 runs each) | p |
|---|---|---|---|
| **EDGE** (edge-only chains fitted to B: the next token drawn by the previous ending, k = 1 or 2 glyph units, and zone) | boundary rules only, routing included | −0.003 to +0.004 (z −1.5 to +1.8) | 0.04–0.95; none ≤ 0.005 |
| **CLASS** (class-chain generators fitted to B: habit, M1) | class structure beyond routing by construction | +0.021 to +0.031 (z 9–13) | 0.003 in 12 of 12 |
| MIXED (habit2, habit3, habit3b, section-fitted; 20 runs) | partial | +0.016 to +0.026 | 0.003 in all |

**Why MI and not λ2 under EF-K2.** λ2 separated the same families poorly under the routing-preserving null: 5 of 12
CLASS runs at p ≤ 0.005, 0 of 12 EDGE. The scalar MI has an order of magnitude more power here. λ2 is kept as the
C2061-specific descriptive.

**Why EF-K2 and not EF.** Under plain EF, EDGE chains show an MI excess at p ≤ 0.01 in 4 of 12 design runs and at
p ≤ 0.05 in 8 of 12 (routing); under EF-K2 none reaches p ≤ 0.04.

## Thresholds (`prelock_thresholds776.py` → `results/thresholds776.json`)
- **NEG** = max D over the EDGE family = **+0.0038**.
- **POS** = min D over the CLASS family = **+0.0206**.
- **τ** = (NEG + POS) / 2 = **0.0122**.

| Call | Condition |
|---|---|
| **BEYOND ROUTING** | p ≤ 0.005 and D ≥ τ |
| **ROUTING-REDUCIBLE** | p > 0.05, or D ≤ NEG |
| **INDETERMINATE** | otherwise |

In the design, 12 of 12 CLASS runs are BEYOND ROUTING and 12 of 12 EDGE runs are ROUTING-REDUCIBLE.

## Certification (`prelock_cert776.py`; fresh seeds 8600+; criteria fixed before running)
- **Set:** EDGE ×10 (edge1 ×5, edge2 ×5), CLASS ×10 (habit ×5, M1 ×5), MIXED ×15 (reported only).
- **C1:** no EDGE run is BEYOND ROUTING, and at most 2 are INDETERMINATE.
- **C2:** at least 9 of 10 CLASS runs are BEYOND ROUTING, and none is ROUTING-REDUCIBLE.
- PASS = C1 and C2. A FAIL means redesign, with no re-tuning on these seeds.

**Result** (`results/prelock_cert776.json`, run after the v2 draft was written): **PASS.**

| Criterion | Result |
|---|---|
| C1 (EDGE ×10: none BEYOND ROUTING, ≤ 2 INDETERMINATE) | pass: 10 of 10 ROUTING-REDUCIBLE; max D +0.0024; 0 INDETERMINATE |
| C2 (CLASS ×10: ≥ 9 BEYOND ROUTING, none ROUTING-REDUCIBLE) | pass: 10 of 10 BEYOND ROUTING; min D +0.0214 (z 9.2–12.3) |

MIXED (reported): all 15 BEYOND ROUTING. λ2 under EF-K2 on the same runs: 1 of 10 CLASS runs at p ≤ 0.005 and 0 of
10 EDGE (the low-power descriptive); at α 0.05, λ2 reached 15 of 22 CLASS runs and 0 of 22 EDGE runs across design and
certification.

**What the certification licenses (audit).**
- A BEYOND ROUTING call excludes a process whose tokens depend only on the previous two-unit ending, zone and folio ×
  line-type composition. It does **not** exclude longer boundary keys, line-level class clustering, or the placement of
  unmapped tokens. The audit's line-latent plant (a per-line class mode with no transitions) read BEYOND ROUTING
  (D +0.016, z 7.3).
- A ROUTING-REDUCIBLE call means B's pooled class-pair dependence beyond routing is weaker than in every class or
  token chain fitted to B's adjacent pairs: all 35 such runs, including the MIXED family and the audit's
  folio-emission chains.

**Dry run (v3 code):**
- the edge-only decoy is ROUTING-REDUCIBLE (MI D +0.0023, p 0.14; under plain EF its MI is significant, p 0.007, which
  is the routing EF-K2 removes; raw-adjacent 49-class D +0.0011; EFL-K2 p 0.27; shape "unresolved"; λ2 rule →
  annotate);
- the class-chain decoy is BEYOND ROUTING (D +0.0237, z 10.2; raw-adjacent D +0.0394; EFL-K2 p 0.036; shape
  "order-like"; λ2 p 0.006 → no demotion).

## Pre-declared descriptives (no verdict)
- MI under plain EF (routing not fixed).
- λ2 under EF-K2 and under EF, and the shuffle floor; λ3 under EF-K2.
- Lag-2 MI and λ2 under EF-K2.
- EFL-K2 MI; EFL λ2; raw-adjacent 49-class MI and 50-state MI under EF-K2.
- **Shape wording rule** (edit 2; restricts wording only; uncertified): if the MI excess D > 0, "order-like" when the
  lag-2 excess is less than half the lag-1 excess and EFL-K2 MI p ≤ 0.05; "clustering-like" when EFL-K2 MI p > 0.05 and
  the lag-2 excess is at least 0.75 × the lag-1 excess; otherwise "unresolved".
- **The C2061/C2067 rule** (edit 1; pre-registered; applied whatever the MI call): on λ2 under EF-K2 at α 0.05.
  - If p > 0.05: C2061/C2067 are annotated "**not shown** to be sequence beyond boundary rules" and that reading moves
    to Tier 3, while the measurement against the 5-gram stands. The annotation carries its power: at α 0.05 the λ2
    test reached 15 of 22 class chains (about 0.68), so when MI is BEYOND ROUTING a λ2 miss happens about 30% of the
    time; "not shown", not "absent".
  - If p ≤ 0.05: no demotion. **λ2 significance under EF-K2 is not evidence of order:** the audit's line-latent plants
    reached p 0.003 with a λ2 excess three to four times a class chain's. C2061's "sequence" reading stays unresolved
    unless the shape reading is order-like. (λ2 and MI come apart: PHASE_733 showed it, and the audit's line plants did
    too.)
- **Shape-rule scope** (edit 4): the shape reading is reported only under BEYOND ROUTING or INDETERMINATE; under
  ROUTING-REDUCIBLE the excess is noise and no shape is read.
- **Power of the shape readout on B** (confirmation pass): B's EFL-K2 movable mass (3.8%) exceeds the controls' (1–3%),
  where EFL-K2 MI reached p ≤ 0.036 in 6 of 6 class chains and the "order-like" arm was reached by no non-order plant
  (0 of 14); the "clustering-like" arm labelled all 3 line-latent plants correctly. Power holds at class-chain strength
  (D about 0.02–0.03); below τ, or with order and clustering mixed, "unresolved" is the likely wording.

## Declared prior knowledge and exposure
- **B's facts relied on:** C2061/C2067 (λ2 0.206, λ3 0.134 on the PHASE_733 population; shuffle floor 0.118; 5-gram
  0.119); C2023 (class MI 0.264 against a within-line shuffle 0.215, and 5-gram-reproducible); C2065; C1212/C1563/C2082;
  C2091; C2093.
- **B supplied before the lock:** its skeleton; paragraph-first-line flags; adjacent-pair transitions (for the
  generators: token, class and edge chains, line-initial distribution, line-quintile unigrams, within-section pairs);
  and, for the movable-mass checks (EF, EF-K2, EFL, EFL-K2), its per-slot cell memberships. The EF-K2 and EFL-K2 cells
  use each slot's own edges plus the preceding token's ending, which is adjacent edge-pair information (edit 6), not
  composition only; no order statistic beyond adjacent pairs was computed.
- **Not computed on B before the lock:** MI, λ2 or λ3 on this population, any EF, EF-K2 or EFL sample, or any order
  statistic beyond adjacent pairs.

## What each outcome means
**ROUTING-REDUCIBLE.** B's pooled class-pair dependence (C2023's statistic) on the P-text reduces to its boundary
rules (junction coupling and two-unit ending routing) plus folio × line-type composition: it is weaker than in every
class or token chain fitted to B's adjacent pairs (35 runs).
- Registry: a new Tier-2 row stating that. **C2061/C2067 are not demoted by this call** (edit 1): they differ in
  statistic (λ2), population and null. They are handled by the pre-registered λ2 rule above.
- It does not say the text is meaningless. (C2056 and C549 stand: a narrow effect such as qok → ok barely moves an
  aggregate 49 × 49 MI.)

**BEYOND ROUTING.** B has neighbouring-class dependence beyond two-unit ending routing and folio × line-type
composition, with D ≥ τ, midway between the edge chains and the B-fitted class chains. No edge-only chain reads this
way (C1); the audit's line-latent plant, with no transitions at all, reached D 0.016.
- **The carrier is unresolved by the call:** order (a transition structure) or sub-folio clustering (a line-level
  latent) both produce it. The wording rule on EFL-K2 and lag-2 restricts the wording only.
- It ties to C2023's statistic, not to C2061's; it does not by itself say the eigenstructure survives.
- Any mechanism reading is echo-class.

**INDETERMINATE.** Phase record; the λ2 rule for C2061/C2067 applies as above; the shape reading is reported.

## Registry consequences
| Outcome | Consequence |
|---|---|
| ROUTING-REDUCIBLE | A Tier-2 measurement row (class-pair MI reduces to boundary rules plus composition) |
| BEYOND ROUTING | A Tier-2 measurement row (neighbouring-class dependence beyond routing; carrier unresolved) |
| INDETERMINATE | Phase record (a D between NEG and τ has explanations with no class structure: longer boundary keys, UN placement) |
| Always | The λ2 rule for C2061/C2067 (annotation or no change), applied whatever the MI call |

## Procedure
1. Commit this draft, the scripts and the v2 design results.
2. Run the v2 certification; write its result here.
3. Lean-expert lock audit and confirmation pass.
4. `run776.py --checksums`, commit, tag `phase776-lock`.
5. `run776.py` (verify_lock first; 1,000 permutations; raw result committed before the write-up).
6. The dry run (`run776.py --dry`: an edge-only chain and a class chain) runs before the lock.

## Caveats
- **Population differs from C2061's** (P-text skeleton, blockers), so λ2 values are not directly comparable to 0.206.
- **The reference families are first-order generators fitted to B's adjacent pairs.** A no-message process with
  higher-order or line-level class structure that is not routing-mediated would be called BEYOND ROUTING; the
  descriptives are meant to show its shape, not to exclude it.
- **The primary statistic is a scalar.** A BEYOND ROUTING result says dependence exists; it does not by itself say
  the eigenstructure survives (λ2 under EF-K2 is reported for that, at low power).
- **λ3 and EFL are underpowered** at this size.
- **The MI plug-in is biased upward** at finite samples. The number of bridged pairs varies by 0–3 across null
  samples (bridging depends on where unmapped tokens land), a negligible difference; the permutation test is exact
  either way.
- **INDEX.md** is updated with each version.

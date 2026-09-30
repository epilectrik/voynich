# PHASE_776 — Does Currier B's class-transition structure (C2061/C2067) go beyond its word-boundary rules? (pre-registration)

**Status: DRAFT v2 for the lean-expert lock audit (not locked); v2 certification PASSED (below).**
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
- **The question.** Is B's class-to-class transition structure anything more than its word-boundary rules: the glyph
  junction coupling (C1212/C1563) and the routing of the next class by the previous ending (C2082)? If a null that
  preserves both, plus folio composition, reproduces the class dependence, the eigenstructure reduces to boundary rules
  and the procedural reading loses its last measured leg. If B's dependence stays above it, there is class-level
  structure beyond spelling and routing.

## Statistics
Every token is mapped to its class (CLASS_COSURVIVAL_TEST map: 480 types, 49 classes, about 69.5% of tokens); within
each line unmapped tokens are dropped and their neighbours joined (the BRIDGE convention of PHASE_733); adjacent class
pairs are counted into a 49 × 49 matrix.

- **Primary: MI = I(class_i; class_{i+1})**, the plug-in mutual information (bits) of the pair counts (the C2023
  scalar). **D = MI(B) − mean MI(null); p = (1 + #{null ≥ observed}) / (1 + R).**
- **Descriptive:** λ2 and λ3 of the row-normalised matrix (the C2061/C2067 statistics), the lag-2 MI and λ2, and the
  within-line class shuffle floor (C2061's floor).

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
- **EFL (descriptive):** EF within the line, first and last glyph as the edge signature (edges and line composition
  both fixed; about 20% movable).
- The B run uses 1,000 permutations, seed 77600.

## Reference families (v2 design calibration; `results/prelock_calib776_design2.json`, R = 300)
| Family | What it has | MI excess D under EF-K2 (12 runs each) | p |
|---|---|---|---|
| **EDGE** (edge-only chains fitted to B: the next token drawn by the previous ending, k = 1 or 2 glyph units, and zone) | boundary rules only, routing included | −0.003 to +0.004 (z −1.5 to +1.8) | 0.04–0.95; none ≤ 0.005 |
| **CLASS** (class-chain generators fitted to B: habit, M1) | class structure beyond routing by construction | +0.021 to +0.031 (z 9–13) | 0.003 in 12 of 12 |
| MIXED (habit2, habit3, habit3b, section-fitted; 20 runs) | partial | −0.0005 to +0.019 (λ2 basis; MI reported) | mixed |

**Why MI and not λ2 under EF-K2.** λ2 separated the same families poorly under the routing-preserving null: 5 of 12
CLASS runs at p ≤ 0.005, 0 of 12 EDGE. The scalar MI has an order of magnitude more power here. λ2 is kept as the
C2061-specific descriptive.

**Why EF-K2 and not EF.** Under plain EF, EDGE chains show a significant MI excess in 4 of 12 design runs (routing);
under EF-K2 none does.

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

MIXED (reported): habit2 3/3 and habit3 2/3 BEYOND ROUTING; the others between the families. λ2 under EF-K2 on the same
runs: 1 of 10 CLASS runs at p ≤ 0.005 (the low-power descriptive, as expected), 0 of 10 EDGE.

**Dry run (v2 code):** the edge-only decoy is ROUTING-REDUCIBLE (MI D +0.0023, p 0.14; under plain EF its MI is
significant, p 0.007, which is the routing EF-K2 removes); the class-chain decoy is BEYOND ROUTING (D +0.0237,
z 10.2), shape "order-like".

## Pre-declared descriptives (no verdict)
- MI under plain EF (routing not fixed).
- λ2 under EF-K2 and under EF, and the shuffle floor; λ3 under EF-K2.
- Lag-2 MI and λ2 under EF-K2.
- EFL λ2.
- **Shape wording rule** (restricts wording only; uncertified): if the MI excess D > 0, "order-like" when the lag-2
  excess is less than half the lag-1 excess and EFL p ≤ 0.05; "clustering-like" when the lag-2 excess is at least the
  lag-1 excess; otherwise "unresolved".

## Declared prior knowledge and exposure
- **B's facts relied on:** C2061/C2067 (λ2 0.206, λ3 0.134 on the PHASE_733 population; shuffle floor 0.118; 5-gram
  0.119); C2023 (class MI 0.264 against a within-line shuffle 0.215, and 5-gram-reproducible); C2065; C1212/C1563/C2082;
  C2091; C2093.
- **B supplied before the lock:** its skeleton; paragraph-first-line flags; adjacent-pair transitions (for the
  generators: token, class and edge chains, line-initial distribution, line-quintile unigrams, within-section pairs);
  and, for the movable-mass checks, its per-slot cell memberships (composition only).
- **Not computed on B before the lock:** MI, λ2 or λ3 on this population, any EF, EF-K2 or EFL sample, or any order
  statistic beyond adjacent pairs.

## What each outcome means
**ROUTING-REDUCIBLE.** B's class-to-class dependence is what its boundary rules (junction coupling and ending
routing) and folio composition produce. No class-chain generator fitted to B ever reads this way (certification C2),
so the outcome excludes class-level sequence structure at the strength of a class Markov chain fitted to B.
- Registry: C2061 and C2067 get a scope note and drop to Tier 3 as "sequence beyond boundary rules" claims (same
  claim, stricter null; a null-driven demotion, self-clearing). C2023's Tier-2 measurement is unaffected. The working
  interpretation's last measured "program-like" leg is gone.
- It does not say the text is meaningless.

**BEYOND ROUTING.** B has class-level transition structure beyond its boundary rules and folio composition, at the
level of a class Markov chain fitted to B. No edge-only chain reads this way (C1). The shape (order versus line
clustering) is read from the descriptives under the wording rule only. Any mechanism reading is echo-class.

**INDETERMINATE.** Phase record; C2061/C2067 stay as they are with a note.

## Registry consequences
| Outcome | Consequence |
|---|---|
| ROUTING-REDUCIBLE | A Tier-2 row; C2061/C2067 annotated and demoted to Tier 3 as sequence claims |
| BEYOND ROUTING | A Tier-2 measurement row extending C2061 to the routing-preserving null |
| INDETERMINATE | Phase record and a note on C2061 |

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
- **The MI plug-in is biased upward** at finite samples; the bias is the same for B and its null samples (same
  counts), so D and p are unaffected.

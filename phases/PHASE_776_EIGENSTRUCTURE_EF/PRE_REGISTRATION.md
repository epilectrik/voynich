# PHASE_776 — Does Currier B's class-transition eigenstructure (C2061/C2067) survive the edge-fixing null? (pre-registration)

**Status: DRAFT v1 for the lean-expert lock audit (not locked).** The certification criteria were fixed (in
`prelock_cert776.py` and here) before the certification ran. After the lock nothing below may change without a new
phase number.

## Origin
- **Where things stand.** The procedural ("program") reading of B needs sequence: what comes next depending on what came
  before. PHASE_774 (C2091) found no recurring 5-token phrase; PHASE_775 (C2093, descriptive) found that once each
  position's glyph edges and page are fixed, neighbour dependence among the frequent tokens is small, and within ending
  contexts at null. The one registered leg of sequence structure still standing is the class-transition eigenstructure:
  λ2 and λ3 of the 49-class transition operator exceed a character 5-gram model (C2061, C2067; also C2065). The
  research agenda (Tier B #4) asks for a re-run under a null that preserves composition, zones and boundary coupling.
- **The question.** Is B's slow class-transition structure anything more than the word-boundary spelling rule
  (C1212/C1563, C2082)? If the edge-fixing null reproduces λ2, the eigenstructure reduces to edges and folio
  composition, and the procedural reading loses its last measured leg. If B's λ2 stays above it, there is class-level
  structure beyond spelling.

## Statistic (the C2061 pipeline)
- Map every certain token to its class (CLASS_COSURVIVAL_TEST map: 480 types, 49 classes, about 69.5% of tokens).
- Within each line, drop unmapped tokens and join their neighbours (the BRIDGE convention of PHASE_733).
- Count adjacent class pairs into a 49 × 49 matrix; row-normalise; **λ2** and λ3 are the second and third largest
  eigenvalue magnitudes.
- **D = λ2(B) − mean λ2(null samples); p = (1 + #{null ≥ observed}) / (1 + R).**

**Population note.** PHASE_733 used all non-label placements (2,420 lines); this phase uses the P-text skeleton of
PHASE_756/774/775 (2,299 lines, 21,610 certain tokens, 22 blockers). B's λ2 is measured afresh on it.

## Null: header-aware EF (PHASE_774/775)
- Tokens are permuted within folio × line type (paragraph-first line or body line) among positions sharing zone, first
  glyph unit and last two glyph units. Blockers stay fixed. Sampling is exact.
- **Preserved:** every boundary junction; every position's edges; line lengths; folio composition by line type.
- **Destroyed:** which token, and therefore which class, fills a slot among same-edge tokens, across the lines of a
  folio.
- **B run:** 1,000 permutations, seed 77600.

## Reference families (design calibration; `results/prelock_calib776_design.json`, R = 300)
| Family | What it has | λ2 excess D (12 runs each) | p |
|---|---|---|---|
| **EDGE** (edge-only chains fitted to B: next token drawn by the previous ending, k = 1 or 2 glyph units, and zone) | class structure only as far as edges carry it | −0.016 to +0.0145 | 0.08–0.95 (none ≤ 0.05) |
| **CLASS** (class-chain generators fitted to B: habit, M1) | class structure beyond edges by construction | +0.013 to +0.048 | ≤ 0.003 in 11 of 12; 0.027 in one |
| MIXED (habit2, habit3, habit3b, section-fitted; 20 runs) | partial | −0.009 to +0.028 | mixed |

**What the null absorbs.** Under EF the CLASS generators' null λ2 is 0.12–0.18, far above the within-line shuffle
floor (0.07–0.09): most of a fitted class chain's λ2 is carried by edges. What is left, +0.013 to +0.048, is the
class-beyond-edges signal the test is calibrated to see.

## Thresholds (`prelock_thresholds776.py` → `results/thresholds776.json`)
- **NEG** = max D over the EDGE family = **+0.0145** (a non-significant run; p 0.37).
- **POS** = min D over the CLASS family = **+0.0134**.
- **τ** = (NEG + POS) / 2 = **0.0139**.

| Call | Condition |
|---|---|
| **SURVIVES EDGES** | p ≤ 0.005 and D ≥ τ |
| **EDGE-REDUCIBLE** | p > 0.05 |
| **INDETERMINATE** | otherwise |

The p-value is the exact test of edge-exchangeability (the EDGE family's p-values are uniform-like); τ guards against a
tiny but significant excess. In the design, 11 of 12 CLASS runs are SURVIVES and 12 of 12 EDGE runs are
EDGE-REDUCIBLE.

## Certification (`prelock_cert776.py`; fresh seeds; criteria fixed before running)
- **Set:** EDGE ×10 (edge1 ×5, edge2 ×5), CLASS ×10 (habit ×5, M1 ×5), MIXED ×15 (reported only).
- **C1:** no EDGE run is SURVIVES EDGES, and at most 2 are INDETERMINATE.
- **C2:** at least 8 of 10 CLASS runs are SURVIVES EDGES, and none is EDGE-REDUCIBLE.
- PASS = C1 and C2. A FAIL means redesign, with no re-tuning on these seeds.

**Result:** *(filled in after the run)*

## Pre-declared descriptives (no verdict)
- **λ3** under EF (C2067's second dimension). In the design, λ3 separated the families poorly (EDGE z −2.9 to +2.8),
  so it is descriptive.
- **Lag-2 λ2** under the same EF samples (classes two apart in the bridged sequence).
- **EFL:** the same permutation within the **line** (edges and line composition both fixed; first and last glyph as
  the edge signature; about 20% of positions movable). Exact but low-powered: in the design, CLASS runs gave EFL p
  from 0.01 to 0.68.
- **The within-line class shuffle floor** (C2061's floor), for continuity.
- **Shape wording rule** (restricts wording only; uncertified): if D > 0, "order-like" when the lag-2 excess is less
  than half the lag-1 excess and EFL p ≤ 0.05; "clustering-like" when the lag-2 excess is at least the lag-1 excess;
  otherwise "unresolved".

## Declared prior knowledge and exposure
- **B's facts relied on:** C2061/C2067 (λ2 0.206, λ3 0.134 on the PHASE_733 population; shuffle floor 0.118; 5-gram
  0.119); C2065 (distributed modes); C1212/C1563/C2082 (edges); C2091, C2093.
- **B supplied before the lock:** its skeleton; paragraph-first-line flags; adjacent-pair transitions (for the
  generators: token, class and edge chains, line-initial distribution, line-quintile unigrams, within-section pairs);
  and, for the EFL movable-mass check, its per-line edge-cell memberships (composition only).
- **Not computed on B before the lock:** λ2 or λ3 on this population, any EF or EFL sample, or any order statistic
  beyond adjacent pairs.

## What each outcome means
**EDGE-REDUCIBLE.** B's class-transition λ2 is what its word-boundary spelling rule and folio composition produce. The
C2061/C2067 eigenstructure then reduces to boundary coupling: it does not stand as evidence of sequence structure beyond
spelling. (It stays a valid measurement against its own nulls; this is a same-claim re-test at a stricter null.)
- Registry: C2061 and C2067 get a scope note and drop to Tier 3 as "sequence" claims; the working interpretation's
  last measured "program-like" leg is gone.
- It does not say the text is meaningless.

**SURVIVES EDGES.** B has class-level transition structure beyond what edges and folio composition carry, at the level
of a class Markov chain fitted to B (the CLASS family). Its shape (order versus line clustering) is read from the
descriptives under the wording rule only. Any mechanism reading is echo-class.

**INDETERMINATE.** Phase record; C2061/C2067 stay as they are with a note.

## Registry consequences
| Outcome | Consequence |
|---|---|
| EDGE-REDUCIBLE | A Tier-2 row; C2061/C2067 annotated and demoted to Tier 3 as sequence claims (same claim, stricter null; a null-driven demotion, self-clearing) |
| SURVIVES EDGES | A Tier-2 measurement row extending C2061 to the edge-fixing null |
| INDETERMINATE | Phase record and a note on C2061 |

## Procedure
1. Commit this draft, the scripts and the design results.
2. Run the certification; write its result here.
3. Lean-expert lock audit and confirmation pass.
4. `run776.py --checksums`, commit, tag `phase776-lock`.
5. `run776.py` (verify_lock first; 1,000 permutations; raw result committed before the write-up).
6. The dry run (`run776.py --dry`: an edge-only chain and a class chain) runs before the lock.

## Caveats
- **Population differs from C2061's** (P-text skeleton, blockers), so λ2 values are not directly comparable to 0.206.
- **The reference families are first-order generators fitted to B's adjacent pairs.** A no-message process with
  higher-order or line-level class structure that is not edge-mediated would be called SURVIVES; the descriptives are
  meant to show its shape, not to exclude it.
- **The EDGE family's D spread (sd about 0.008)** is realization noise of the generators; on B there is one realization,
  and the exact p carries the significance.
- **λ3 and EFL are underpowered** at this size.

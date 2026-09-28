# PHASE_763 — Glyph-level re-test of "kernel-centric" (pre-registration)

**Status:** LOCKED v3 (2026-09-28), before any analysis code for this phase was written or run.
- **First lean-expert audit (of v1):** LOCK WITH CHANGES, ten changes, all incorporated.
- **Second lean-expert audit (of v2):** LOCK WITH CHANGES, six edits and four clarifications, all incorporated.
- **Remaining deviations:** listed at the end.
**Origin:** Tier-0 restatement 2026-09-28 (v7.24). The only documented evidence for C089 ("core within core: k, h, e")
was X_adversarial_audit Attack 1, and it was found uninformative:
- its pass criterion did not depend on the data (the real corpus fails it; k ranks 7th);
- its first-order Markov null reproduces the bigram counts the centrality is computed from;
- it ranks EVA letters, and EVA "h" is half of the bench glyph (PHASE_754, C1440).

C089, C085 and C103–C105 moved to Tier 3 as "support withdrawn, not falsified". This phase runs the fair glyph-level
test in two arms that measure different constructs:
- **Arm W — within-token centrality.** A property of the word list.
- **Arm S — cross-token routing beyond the prefix channel.** A property of the sequence.

**Stated prior (expert-advisor):** probably fails. C2065's slow modes are distributed, C2067's carrier attribution was
refuted, and k ranked 7th in the old test.

**Known effects each arm must get past (lean-expert audit):**
- **Arm W:** medial vs edge position (C1209, C1210) and within-token bench→e order (C521). These are handled by the
  edge-anchored null and by matching controls on position.
- **Arm S:** prefix routing and the qo vs ch/sh alternation (C509.b, C549, C2056, C1012, C1023). These are handled by
  conditioning on the first glyph unit of t.

**Change control:** after lock nothing below may change without a new phase number. Implementation errors found after
lock are fixed and reported as deviations, with both results shown if a fix changes a verdict-bearing number.

## Units (locked)
Glyph tokenizer (PHASE_754): `c[tkpf]h|[cs]h|i+[nrlm]|.`.

- **S1 (primary):**
  - bench `B` = {ch, sh} merged;
  - the benched gallows {ckh, cth, cph, cfh} are separate units, counted as neither k nor bench;
  - `k` is the plain gallows k only;
  - e-runs are kept as repeated e units;
  - minim groups follow the PHASE_754 frame;
  - q and o are separate units.
- **S2 (sensitivity):** {ch, sh, ckh, cth, cph, cfh} → `B`, i.e. every glyph that contains EVA "h".
  - Decomposing a benched gallows into bench + gallows would force an arbitrary within-glyph order, so S2 merges it
    instead.
  - The sign of each arm's effect under S2 must agree with S1 for a PASS.
- **Kernel set:** {k, e, B}.
- No other kernel mapping may be adopted after unblinding.
- **Graph nodes (Arm W):** the most frequent units that together cover ≥ 99% of unit instances. The rest merge into one
  node `X`, which is never ranked. Two further nodes, `START` and `END`, delimit tokens.
- **Control pool:**
  - Arm W: non-kernel units with ≥ 200 instances.
  - Arm S: non-kernel units with ≥ 200 left tokens t (in the Arm-S pair set) that contain the unit non-initially
    (X_g(t) = 1 and F(t) ≠ g). A kernel unit below 200 is flagged.
  - Eligibility excludes units whose conditional statistic is near-degenerate. q is the example: it is almost always
    token-initial.
  - On H, the kernel counts are k 5,215, e 8,848 and B 2,947.

## Data
- **Voynich H (primary):** Currier B, H track, `P` placement, labels excluded.
  - Arm W: readable tokens only (no `*`): 21,610 tokens, 116,196 within-token bigrams including the START and END
    edges.
  - Arm S: the PHASE_756 `load_primary()` corpus (uncertain tokens are blockers).
- **Voynich ZL (transcription robustness):**
  - Source: ZL 3b IVTFF, language B, `P` placement, parsed with the PHASE_761 loader.
  - Both `.` and `,` count as spaces.
  - A segment split by `<->` counts as its own line.
  - Tokens containing `?` or `*` are unreadable: dropped in Arm W, blockers in Arm S.
  - Sections come from the H folio → section map; unmapped folios are dropped (count reported).
  - ZL is a robustness check on the same manuscript, not an independent replication.
- **Class map:** `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`.
  - `token_to_class`: 49 classes; unmapped tokens go to a UN bucket, giving 50 categories.
  - `class_to_role`: 5 roles; with UN, 6 categories.

## Frequency- and position-matched controls
- **Rule:** each kernel unit's controls are the 5 non-kernel pool units nearest to it in three standardised features:
  - frequency: log instance count (Arm W), or the non-initial containment rate among Arm-S left tokens (Arm S);
  - mean relative position within the token (i / (L−1); 0.5 for L = 1);
  - interior share (the fraction of the unit's instances that are neither first nor last).
- Features are z-scored across the pool plus the kernel units; distance is Euclidean.
- **Extrapolation flag:** raised when a kernel unit's frequency feature exceeds all 5 of its controls by more than 2×.
- The rule is re-applied unchanged to ZL, Currier A, each floor corpus and each generator member.

Controls on H, computed before lock (no kernel unit is flagged):

| Kernel | Arm W (S1) | Arm S (S1) | Arm W (S2) | Arm S (S2) |
|---|---|---|---|---|
| k | t, a, d, o, p | a, d, o, t, ckh | t, a, d, o, l | a, d, o, t, l |
| e | a, d, t, o, l | a, d, o, t, l | a, d, t, o, l | a, d, o, t, l |
| B | o, q, t, l, p | p, t, o, s, cth | o, t, l, a, d | p, t, o, s, l |

## Decision statistic (both arms)
- **Per-unit score:** z_g = (observed − null mean) / null SD of the arm's per-unit statistic.
- **Kernel score:** K = mean z over {k, e, B}.
- **Control triads:** every triad of distinct units (c_k, c_e, c_B), with each unit taken from the matching kernel
  unit's control set (at most 125 triads). Each triad is scored as the mean z of its three units.
- **Arm p-value:** p = (1 + #{triad score ≥ K}) / (1 + #triads).
- **Effect:** E = K − median triad score. E is in z units.
- If any kernel unit is flagged, PASS also requires the same test on the unflagged kernel units at p ≤ 0.05.
- **Per-arm outcome:**
  - **PASS:** p ≤ 0.05 and every robustness sign agrees (listed per arm).
  - **FAIL:** p ≥ 0.5.
  - **INCONCLUSIVE:** anything in between.
- **Across arms:** Holm correction over the two arm p-values applies to the overall PASS. Per-unit tests are
  descriptive only.
- **Ranks:** reported descriptively and never used as a criterion. Under the alternative, z grows with frequency and
  role share.

## Arm W — within-token centrality
- **Chain:** the renewal chain over the graph nodes.
  - Transitions: START → first unit, then unit → unit within the token, then last unit → END, then END → START with
    probability 1.
  - Probabilities come from token-weighted instance counts.
  - Self-transitions (for example e → e) are **kept**; see deviation D1.
  - **Pair set V′:** the glyph-unit nodes other than X, START and END.
- **Random-walk betweenness:** RWB(g) = Σ over ordered pairs s ≠ t in V′, with s and t ≠ g, of N_t[s, g], where
  N_t = (I − Q_t)⁻¹ and t is made absorbing.
  - By the Aldous & Fill identity (no reversibility needed), RWB(g)/π_g = H_tot − h_g, where
    h_g = Σ over u ∈ V′, u ≠ g, of (E_u T_g + E_g T_u). Hitting times come from the fundamental matrix.
- **Primary statistic — centred random-walk closeness:** Y_g = mean over u ∈ G of h_u − h_g.
  - G is the ranked set: the Arm-W pool plus the kernel.
  - Centring removes every term shared by all units (H_tot and the common part of h_g), so K minus the triads cannot
    be driven by differences in null SD acting on a shared shift.
  - Y does not depend on π, so the folio bootstraps are unaffected by sampling noise in π.
  - The z of RWB is reported descriptively.
- **Null (edge-anchored run-block permutation):**
  - Each token is parsed into maximal runs of identical units, e.g. an e-run is one block.
  - The first and last runs stay in place; the interior runs are permuted as blocks, keeping their lengths.
  - A permutation that would make two identical runs adjacent is rejected and redrawn, up to 100 tries; after that the
    token keeps its order.
  - Every self-transition count is therefore preserved, so both π and each unit's self-transition probability match
    between the real text and the null.
  - Tokens with fewer than 2 interior runs stay intact.
  - R = 1,000 permutations, seed 763.
  - START/END transitions are identical in the real text and the null.
  - The same null is used for the plant bases and for the A, Latin and generator floors.
- **Robustness (the sign of E must agree for a PASS):**
  - S2;
  - ZL (also p ≤ 0.10).
- **Type-weighted graph:** reported. If E changes sign, the result is labelled "frequent-token-driven".
- **Secondary (reported, not verdict-bearing):** weighted shortest-path betweenness with d = −log P(j|i). Its observed
  value is bagged over 200 token bootstraps; its z uses the same null.
- **Interpretation limit:** Arm W is a property of the word list. Any generator that emits B's vocabulary reproduces it.

## Arm S — cross-token routing beyond the prefix channel
- **Pairs:** within-line adjacent certain tokens (the PHASE_756 `valid_edge` set) in lines with ≥ 5 certain tokens.
- **Primary statistic:** CMI_g = I(X_g(t); C(t+1) | F(t)), Miller–Madow corrected.
  - X_g(t) = 1 if token t contains unit g;
  - C = 50 categories (49 classes + UN);
  - F(t) = the first glyph unit of t.
- **Robustness (the sign of E must agree for a PASS):**
  - R1: target F(t+1) instead of C(t+1);
  - R2: condition on (F(t), glyph-length bin of t ∈ {≤2, 3, 4, 5, ≥6}), with the target collapsed to 5 roles + UN;
  - R3: ZL (also p ≤ 0.10);
  - S2.
- **Descriptive:** the unconditional MI I(X_g(t); C(t+1)), which was the expert-advisor's original statistic. It is
  shown with his original criterion (kernel = top 3 by z). It re-measures prefix routing and cannot be a verdict.
- **Null: PHASE_756 N5** (`c957_joint_null_n5.py`, imported unchanged).
  - Moves: within-line medial swaps.
  - Constraint: a soft penalty on the per-section counts of glyph-unit edges (`Data(..., 'GLYPH')`), with **β = 2**.
  - Why this configuration: in PHASE_756, β = 4 and β = 8 did not mix (fraction-changed ESS ≈ 5, R-hat > 2), while
    glyph-unit β = 2 mixed (R-hat ≈ 1.00, TV within tolerance). Its only miss was the ESS of the fraction-changed
    diagnostic (940 vs 1,000), which is not a statistic here.
  - Glyph-unit edges are kept, not EVA edges, because the statistic conditions on the first glyph unit of t. The null
    should therefore preserve boundary coupling in the same units.
- **N5 sampling procedure:**
  1. **Pilot:** one chain (seed 76390) from the real text, 2,000 burn-in sweeps, then 500 samples at thin 5. Estimate
     the integrated autocorrelation time τ (in sweeps) of the primary CMI statistic for every kernel and control unit.
  2. **Main run:** 4 chains. Seeds 76300–76303 on H; 76310–76313 on ZL, which gets its own pilot with seed 76391.
     Chains 1–2 start from the real text; chains 3–4 start from an N1 shuffle with 1,000 annealing sweeps. Burn-in is
     2,000 sweeps, followed by 300 samples per chain at thin T = max(10, ⌈max τ⌉), giving 1,200 draws.
- **Gates** (PHASE_756's own values), checked before any observed statistic is computed:
  - rank-normalised split R-hat < 1.05 and bulk ESS ≥ 1,000, for the primary statistic of every kernel and control
    unit;
  - mean edge TV ≤ tol_g for every section group (N5's own tolerance: min(0.02, 0.10 K_g));
  - fraction changed ≥ 0.50.
  - If ESS is short, the chains are extended once to 600 samples each. If any gate still fails, Arm S is INCONCLUSIVE
    for that corpus.

## Power certification (an uncertified arm cannot return FAIL)
- **MDE80 per unit:** 2.485 null SDs, i.e. z = 2.485.
- **Certification target:** at least 80% detection (arm p ≤ 0.05) across 100 plants at the plant strength π*.
  - π* is the smallest π on the grid {0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0} at which the mean E over 20 plants
    is ≥ 2.485.
  - E is used rather than the kernel's mean z because plants can shift the controls as well. This also puts
    certification on the same scale as the KILLED margin.
  - If no π on the grid reaches it, the arm is uncertified.
- **Arm W plant:**
  - Base: a fresh edge-anchored permutation of the H tokens, which is itself a null text; 100 bases.
  - Plant, per token and with probability π: take the kernel units in a seeded random order. For each kernel unit g
    that has an interior run, move its first interior run (the whole run block) to the first interior position,
    immediately after the first run.
  - A move is skipped if it would make two identical runs adjacent.
  - Composition and self-transition counts are preserved, so the H null applies unchanged.
- **Arm S plant:**
  - Base: 100 draws from the main H N5 chains (every 12th draw).
  - Target sets: each kernel unit g gets a fixed target set T_g of 5 classes, drawn at seed 763 from the 20 classes
    with ≥ 1% of Arm-S left tokens.
  - Plant: take each pair (t, t+1) in order along the line, where t+1 is medial, X_g(t) = 1, F(t) ≠ g and
    C(t+1) ∉ T_g. With probability π, token t+1 is swapped with a randomly chosen medial token of the same line
    (neither t nor t+1) whose class is in T_g, if one exists.
  - Composition, line lengths and the initial and final tokens are preserved. Planted texts are scored against the
    main H N5 null.
- **Equivalence bound:** a 95% upper bound on E, from a folio bootstrap for both arms (vocabulary and coupling cluster
  by folio: C531, C681). 200 resamples; null mean and SD held fixed.

## Floors
- **(a) Currier A (Arm W):**
  - Corpus: Currier A, H, `P` placement, readable tokens. Kernel as above; controls re-selected on A.
  - B is downsampled to A's within-token bigram count by random folio subsets, 100 times, each with a
    200-permutation null.
  - If E_A falls inside B's 2.5–97.5% range, the Arm W result is re-scoped to "script/lexicon property", not a Currier B
    property.
- **(b) Latin (Arm W):** Mesue Grabadin Latin (`mesue_grabadin_latin_full.txt`), Rupescissa 1561
  (`rupescissa_latin_1561.txt`, first 200 lines skipped) and the SISMEL Testamentum Latin pages.
  - The SISMEL pages are the L spreads headed "TESTAMENTUM" (254 spreads), taking text above the apparatus separator,
    with line-end hyphenation joined.
  - Preparation: lower-cased; words = `[a-z]+`; units = letters.
  - N-matching: each corpus contributes one contiguous span, from a seeded random start, whose within-token bigram
    count matches B's 116,196. A corpus that is too short is used whole (reported).
    - The span is split into 83 contiguous blocks, the analogue of folios, for the block bootstrap.
    - Each span gets its own null, R = 1,000.
  - Floor statistic: the corpus's best triad, i.e. the maximum E over all triads of distinct pool letters, each triad
    scored with its own matched controls under the same rule. This is deliberately conservative, since B's kernel was
    itself chosen from B data.
  - **Distinctive** only if the lower 2.5% bound of B's kernel E exceeds the upper 97.5% bound of every floor's
    best-triad E. B uses a folio bootstrap and the floors a block bootstrap, 200 resamples each.
  - Otherwise a PASS is re-scoped to "not distinguishable from the best-case letter triad of an alphabetic script".
- **(c) Generators (both arms):**
  - Naibbe GV1 / P-REC / STREAM / SR0 / V0 (the declared canonical variant) and the fitted Timm–Schinner generator
    (C2077), both through the PHASE_757 harness; 20 members each.
  - Arm W: 200 permutations per member.
  - Arm S: N5 (glyph edges, β = 2) with 2 chains × 300 draws at H's thin T. Gates are reported, not enforced.
  - Controls are re-selected per member.
  - If B's E lies inside a generator's 2.5–97.5% ensemble range, that arm cannot support the Tier-3 reading.

## Verdict and registry consequences
**In every outcome**, C089 (EVA letters) is superseded by a new glyph-level row stating the result.

| Outcome | Condition | Registry action |
|---|---|---|
| **PASS** | Both arms PASS under Holm; every robustness sign agrees; no floor reproduces the effect | New Tier-2 measurement. The Tier-0 wording is not restored and the control-program reading is not promoted; that is echo-class and needs an external test or human sign-off. |
| **PASS, FLOOR-SCOPED** | As PASS, but a floor reproduces the effect | Tier-2 measurement scoped to the floor's level: script/lexicon (A); "not distinguishable from the best-case letter triad of an alphabetic script" (Latin); or generator-reproducible (Naibbe/Timm). |
| **MIXED** | Exactly one arm PASS | The passing arm is registered as a Tier-2 measurement; C089 is not restored. |
| **KILLED** | Both arms FAIL, both certified, and each arm's 95% upper bound on E < 2.485 | Tier 1, scoped to "glyph-level centrality (RWB) and routing beyond the prefix channel (conditional forward information) of {k, e, bench}". This is not a blanket kernel Tier 1. |
| **NOT ESTABLISHED** | Anything else, including a single-arm FAIL, FAIL without the equivalence bound, or an uncertified or gate-failed arm | C089 superseded; no Tier 1. |

A single-arm FAIL cannot kill the other construct. Arm S measures routing, and a true hub can carry little routing
information.

## Not in scope
The C2067 λ3 class-level follow-up, and any test of "closed-loop" (its C171 legs are withdrawn).

## Deviations from the audit
- **D1:** self-transitions are kept, not dropped. RWB(g) = π_g × (hitting-time sum), so dropping self-loops collapses
  e-runs in the real text but not in the null, which breaks them apart. π_e would then be lower in the real text than in
  the null by construction, biasing e's z downwards.
  - The second audit showed that keeping self-loops alone only moves the bias, into how often the walk enters e.
  - It is removed by the run-block null, which preserves every self-transition count.
- **D2:** Theophilus is excluded from the Latin floors. The Hendrie 1847 text interleaves English (the same reason
  Codicillus is excluded under C2054). Three Latin floors remain.
- **D3:** the plant designs and the equivalence-bound resampling units are this document's choices; the audit specified
  only the requirements.
- **D4:** S2 merges benched gallows into B instead of decomposing them; see Units.
- **D5:** the Arm S null uses glyph-unit edges at β = 2 with PHASE_756's gate values. This replaces v1's β = 4 and
  stricter gates, which PHASE_756 showed do not mix.

## Outputs
`results/kernel_retest.json` (all statistics, controls, gates, certification, floors and verdicts),
`results/run_log.txt` and interim JSON. Script: `scripts/kernel_retest.py`.

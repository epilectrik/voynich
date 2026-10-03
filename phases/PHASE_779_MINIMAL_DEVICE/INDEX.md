# PHASE_779 — The minimal device: which of B's registered regularities is a sampler of the measured rules not outside?

**Status: COMPLETE. Locked verdict (tag `phase779-lock`, c336b1d; pre-registration v4 after a lean-expert design
audit and confirmation pass): the primary sampler is INCOMPLETE on D5; the layer map on eight registered
regularities is five NOT REPRODUCED, three NO EXCESS DETECTED OVER THE WITHIN-CELL SHUFFLE, none REPRODUCED.
Registered as C2097 (Tier 2, measurement).**

- **Question.** Take the simplest sampler of B's three measured rules: page × line-type word stocks (the cells of
  C2093–C2095), line-position vocabulary (zone tables with back-off), and two-unit junction routing (C2082, with
  the first-unit marginal divided out). On eight registered regularities the sampler is not given, is B inside or
  outside its ensemble, and with what power? A layer map of the registry, not a production method (C2052; the
  sampler's tables are fitted to B).
- **Device.** `scripts/mind779.py`; run script `scripts/run779.py`; pre-registration `PRE_REGISTRATION.md` (v4).
  Within-cell Metropolis sampler (swap proposals, composition exact, 10 sweeps; the sequential sampler failed the
  fidelity gate through depletion). Ladder R0L (within-cell shuffle) → R1L (+ zones) → R2aL (+ one-unit routing) →
  **R2L (primary)** → R3L; variants R2P (page-only stocks), R2Lmemo (per-word zone tables for every word), R2Lw
  (sequential, with replacement), R2L+H (header extension). N = 1,000 per variant, plus a second seed block for R2L
  and R0L (pooled 2,000 for the discrete statistic). κ = 0.5 selected on D2 alone (fidelity gate: D2 0.2275 ±
  0.0050 against B's 0.2282, z +0.13; mixing checked at 20 sweeps).
- **Power.** Each counted prediction has a plant on R2L with a grid; MDE80 = the weakest plant strength that puts
  ≥ 80% of plant members outside the primary ensemble (locked rule: it and every stronger point). Pre-lock grids
  (recovered from the stage log after the stage hung, baseline regenerated and checked; 18 added points) were
  recomputed after the lock against the locked ensemble (`run779.py plantcheck`: 24 reruns, every mean reproduced).

## Result on Currier B

### Step 1 — the panel (D3, D4, D5 tested; D2 and D6 fidelity / descriptive)

| Variant | D2 (fidelity) | D3 | D4 | D5 | D6 | Panel |
|---|---|---|---|---|---|---|
| B | 0.2282 | 0.0148 | 2.357 | 0.0378 | 0.1717 | |
| R0L (shuffle) | 0.000 (z +187*) | −0.001 ± 0.074 (z +0.2) | −0.11 ± 0.50 (z +4.9*) | 0.000 ± 0.004 (z +9.0*) | 0.000 (z +88*) | fails |
| R1L (+ zones) | 0.000 (z +186*) | 0.088 (z −1.1) | 0.01 ± 0.59 (z +4.0*) | 0.008 ± 0.004 (z +7.3*) | 0.187 ± 0.005 (z −2.8) | fails |
| R2aL (+ 1-unit routing) | 0.233 ± 0.005 (z −0.9) | 0.035 (z −0.3) | 0.55 ± 0.74 (z +2.4, rank 999) | 0.0095 ± 0.0044 (z +6.4*) | 0.185 (z −2.5) | fails on D5 |
| **R2L (primary)** | 0.2273 ± 0.0050 (z +0.2) | 0.031 ± 0.071 (z −0.2) | 0.71 ± 0.74 (z +2.2, rank 997) | 0.0145 ± 0.0046 (z +5.1, rank 1000*) | 0.185 ± 0.005 (z −2.6) | **INCOMPLETE on D5** |
| R3L (+ 2-to-2 routing) | 0.226 (z +0.5) | 0.034 (z −0.3) | 0.88 ± 0.72 (z +2.1) | 0.022 ± 0.005 (z +3.3*, rank 1000) | 0.182 (z −1.9) | fails on D5 |
| R2P (page stocks) | 0.228 (z +0.1) | 0.038 (z −0.3) | 0.74 (z +2.2) | 0.014 (z +5.5*) | 0.185 (z −2.4) | fails on D5 |
| R2Lmemo | 0.229 (z −0.1) | 0.036 (z −0.3) | 0.67 (z +2.3) | 0.015 (z +5.3*) | 0.186 (z −2.7; not marginal) | fails on D5 |
| R2Lw (sequential, with replacement) | 0.234 ± 0.006 (z −1.0) | 0.040 (z −0.5) | 0.94 ± 0.68 (z +2.1) | 0.033 ± 0.007 (z +0.7, rank 790) | 0.196 (z −3.5*) | passes (not a rung) |
| R2L+H (header extension) | 0.227 (z +0.2) | 0.034 (z −0.3) | 0.70 (z +2.2) | 0.015 (z +5.4*) | 0.184 (z −2.2) | fails on D5 |

\* outside (beyond [min, max] and |z| > 3.09). **MIN-D: none** (no ladder rung passes the panel).

- **Not outside, by rung.** D2 (an input on the routing rungs) and D6 (the zone input from R1L) are fidelity, not
  reproduction: the primary's D2 is on B (z +0.2, rank 602) and its D6 is over-produced (z −2.6, B below 993 of
  1,000; outside at κ_z × 0.5, z −4.0). D3 is inside at every rung (z −0.2 on the primary); D4 is inside from R2aL
  (primary z +2.2, B above 997 of 1,000). B's D4 reference is a seeded shuffle (2.357 here, 2.414 in PHASE_757/778;
  the verdict is the same either way, z +2.3).
- **INCOMPLETE relative to the PHASE_779 sampler: B is outside on D5.** D5 is the held-out gain of a token-bigram
  model over a last-glyph-unit edge model (PHASE_757). Every Metropolis variant under-produces it (0.0145–0.022
  against B's 0.038, B above all 1,000 members in each, from z +3.3 on R3L to +9.0 on R0L). Whether the D5
  shortfall belongs to the rules or to this sampler is not resolved: R3L narrows it, and R2Lw, which differs in
  two ways (sequential, with replacement) and is outside on D6 (z −3.5) without keeping cell composition, is not
  outside on D5 (0.033, z +0.7). The sampler generates the edge sequence from first-order routing, whereas the exact
  nulls of C2093–C2094 fix B's edge sequence; this does not contradict C2093/C2094. Per the locked rule, every
  scope note below carries "the sampler is itself outside B on D5".
- **Sensitivity (descriptive):** the primary at κ × 0.5, κ × 2, κ_z × 0.5 and κ_z × 2 (200 members each) gives the
  same outside pattern on every panel statistic and every prediction.

### Step 2 — the layer map on the primary (outside = beyond [min, max] and |z| > 3.23; P6z pooled N 2,000)

| Prediction (registered relative) | B | Primary R2L | z, rank | R0L shuffle | MDE80 (locked) | Verdict |
|---|---|---|---|---|---|---|
| P1u glyph-unit line homogeneity, pct (C1214, related) | 0.962 | 0.199 ± 0.061 [0.03, 0.41] | +12.6, 1000/1000 | 0.364 ± 0.065 (z +9.3, outside) | λ 1: 0.335 [0.260, 0.335] | **NOT REPRODUCED** |
| P2 within-folio paragraph PREFIX JSD (C1811/C1812, related) | 0.2282 | 0.2023 ± 0.0037 [0.188, 0.212] | +6.9, 1000/1000 | 0.2027 ± 0.0038 (z +6.7, outside) | κ_p 100: 0.0199 [0.0105, 0.0199] | **NOT REPRODUCED** |
| P7 adjacent e-run class agreement (PHASE_757 descriptive; partly unblinded) | 0.4555 | 0.4328 ± 0.0030 [0.423, 0.444] | +7.5, 1000/1000 | 0.4421 ± 0.0030 (z +4.4, outside) | λ 0.1: 0.0169 [0.0126, 0.0169] | **NOT REPRODUCED** |
| P8 qo / ch-sh alternation, adjacent pairs (C549, C2056, related; partly unblinded) | 0.5846 | 0.5150 ± 0.0076 [0.486, 0.542] | +9.2, 1000/1000 | 0.4748 ± 0.0085 (z +13.0, outside) | λ 0.2: 0.0374 [0.0297, 0.0374] | **NOT REPRODUCED** |
| P10 within-folio hapax dispersion | 0.969 | 0.893 ± 0.029 [0.81, 0.99] | +2.6, 996/1000 | 0.889 ± 0.029 (z +2.8, rank 995, inside) | λ 0.5: 0.155 [0.079, 0.155] | NO EXCESS DETECTED (sampler-sensitive: R2P) |
| P11 e-run medial quintile JSD, ×10⁻⁴ (C1671, C1566, related) | 30 | 2.3 ± 1.6 [0, 10] | +16.5, 1000/1000 | 2.3 ± 1.6 (z +16.1, outside) | λ 0.15: 15 [not rerun; pre-lock λ 0.1: 0.20 outside, effect 7.7] | **NOT REPRODUCED** |
| P12 ok- after qok- share (C2056 lane, related) | 0.380 | 0.342 ± 0.021 [0.28, 0.40] | +1.8, 973/1000 | 0.345 ± 0.023 (z +1.5, rank 944, inside) | λ 0.75: 0.110 [0.080, 0.110] | NO EXCESS DETECTED |
| P6z pair zeros, C2081's form (196 cells) | 10 | 2.88 ± 1.66 [0, 10] (pooled 2,000) | +4.3, 1999/2000 (tie at the maximum: inside) | 15.4 ± 3.4 (z −1.6, rank 70, inside) | m 10: 9.6 [8.0, 9.6] | NO EXCESS DETECTED |

- **Five NOT REPRODUCED.** Line-level glyph-unit homogeneity, within-folio paragraph PREFIX composition, adjacent
  e-run persistence, qo / ch-sh alternation (R0L 0.475 → primary 0.515 → B 0.585), and the e-run medial position
  gradient lie outside the primary ensemble and outside the shuffle, with the same status on every variant and all
  four κ / κ_z settings (descriptive). They are not shown to follow from these rules as sampled; the missing
  structure is not identified. The five are not shown to be independent of one another or of the D5 shortfall
  (P7 and P8 are adjacent-token statistics). The MDE80 ratios (0.34–1.27) are reported but do not enter a NOT
  REPRODUCED verdict.
- **Three NO EXCESS DETECTED OVER THE WITHIN-CELL SHUFFLE.** The label means only that B is not outside the R0L
  ensemble under the locked rule (beyond its range and |z| > 3.23; for P6z, strictly beyond every member). It does
  not mean that B has no excess, that the sampler reproduces the statistic, or that a related row is weakened. P10
  hapax dispersion: B 0.969, shuffle z +2.79 (above 995 of 1,000), primary z +2.58 (above 996); outside on page-only
  stocks (R2P, z +3.7), so sampler-sensitive; B's excess over the shuffle (+0.080) is below MDE80 on the primary
  (0.155), which measures power on the primary only. P12 the share of ok- among ok/ot/ol successors of qok-initial
  words: 0.380, shuffle z +1.53 (above 944), primary z +1.82 (above 973); B's excess (+0.034) is about a third of
  MDE80 (0.110); this is not C2056's enrichment test and C2056 is not re-tested. P6z zeros on 196 fixed common-pair
  cells: B 10; primary 2.88 ± 1.66, B ties the pooled maximum and is inside only by the locked tie rule (z +4.3,
  not used); shuffle 15.4 ± 3.4 (z −1.59, rank 70 of 2,000), but the cells were chosen as common under the primary,
  so the shuffle is not a neutral reference here; no bearing on C2081, whose null fixes B's edge sequence exactly.
- **Nothing is REPRODUCED.** No registered row is shown to follow from composition, zones and routing as sampled;
  C1811/C1812 get the related NOT REPRODUCED note, not a re-check flag.
- **Partly unblinded.** P7 is identical to PHASE_757's `erun_class_same_lag1` (B 0.455 known) and P8 is a related
  statistic of C549 (56.3% known on a different population); both verdicts were foreseeable from the pre-lock
  primary means and are labelled so. The blind counted set is P1u, P2, P6z, P10, P11, P12.

### Descriptives on the primary (not counted)
Token-level line homogeneity (P1t) B 0.576 against 0.026 ± 0.065 (z +8.4); P3 (last-unit m at line ends,
paragraph-first minus body) B +0.022 against 0.005 ± 0.011 (z +1.6; consistent with the disclosed B ≈ +0.02);
gallows-initial first words, paragraph-first minus other (P4) B 0.787 against 0.485 ± 0.018 (z +16.6; composition
is an input on R2L, line-initial placement is not); p/f/cph/cfh share contrast (P5) exact by construction; the nine
C957 bigrams B 0 against 18.7 ± 4.3 (selected on the outcome; not read); max qok-initial tokens in a 10-token
window B 8 against 6.97 ± 0.60 and max identical run 4 against 3.12 ± 0.42 (not an anchor re-pricing: the anchor
is a joint conjunction, C1889, PHASE_741); class-pair MI (C2094's statistic) B 0.232 against 0.1705 ± 0.0043
(z +14.3; measured under a sampler that generates edges, not under C2094's exact null: no bearing on C2094);
repeated 5-windows 0 and 0; duplicate lines 0 against 0.01.

## Provenance and harness notes
- Pre-lock: the sequential sampler failed the fidelity gate (depletion; `results/fidelity779_sequential_v1.json`)
  and the declared Metropolis fallback passed (`results/fidelity779.json`). The plants stage hung at its 37th point
  (pool workers replaced, tasks lost) having written nothing; `scripts/plants_recover779.py` rebuilt
  `results/plants779.json` from the log (baseline regenerated from the stage seed, all eight means reproduced) and
  `scripts/plants_extend779.py` added 18 grid points on generated members only. The Metropolis P11 tilt was clamped
  at zero before its grid ran. All recorded in `PRE_REGISTRATION.md`.
- Locked chain: `run` (11,000 members, 21,451 s; incremental partial writes with seeded resumption, not needed),
  `sens`, `plantcheck` (15,498 s), `verdict`. Raw arrays `results/raw779_run.npz` local (gitignored); JSON and
  logs committed.
- Lean-expert: design audit (38 edits), confirmation pass (18 edits + 2), presence check (LOCKABLE), results check
  (10 corrections to the draft reading, applied; B's P2 0.22817 against D2 0.22824 verified as distinct values by an
  independent recomputation; P11's MDE80 fell from λ 0.2 to 0.15 because the locked ensemble's maximum lay below
  the 200-member baseline's, within the locked walk).

## Registry
- **C2097** (Tier 2, measurement): see `context/CLAIMS/INDEX.md`. Scope notes on C1214, C1811, C1812, C549, C2056,
  C1671, C1566 (related-statistic NOT REPRODUCED template with the D5 suffix). No notes for P7 (no row), P6z, P10,
  P12 (NO EXCESS). No tier changes; no Tier-0 change.
- **Scope statement.** Composition is an input; nothing here bears on vocabulary, folio-unique words (C531), Zipf or
  hapax share, or on how page stocks arose. MIN-D is a sampler of measured rules, not a production method, and does
  not bear on C2077/C2096. Not being outside the sampler is not evidence of generation. No reading.

## Files
`PRE_REGISTRATION.md` (v4, locked) · `scripts/mind779.py`, `scripts/run779.py`, `scripts/plants_recover779.py`,
`scripts/plants_extend779.py` · `results/fidelity779.json`, `results/plants779.json`, `results/pair_cells779.json`,
`results/input_checksums.json`, `results/b_values779.json`, `results/pair_zeros779.json`, `results/sens779.json`,
`results/plantcheck779.json`, `results/verdict779.json`, logs `results/*_log779.txt`.

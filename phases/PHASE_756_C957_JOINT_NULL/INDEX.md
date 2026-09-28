# PHASE_756 — C957 joint null (N5) and cross-track check

**Status:** COMPLETE. Locked verdict **REDUCES** → C957 superseded by **C2081** (Tier 2 reduction row); the 28
forbidden-transition scope notes, `CORE/frozen_conclusion.md`, CLAUDE_INDEX, MODEL_CONTEXT, the crazy-expert stance and
the BCSC contract updated. D1 dropped from the rival panel (PHASE_757).
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit 766b1cd; lean-expert audit applied).
**Script:** `scripts/c957_joint_null_n5.py` (numba MCMC; 5 h 12 min total, single-threaded, mostly under CPU contention
with PHASE_757). **Results:** `results/c957_joint_null_n5.json`, `results/run_log.txt`.

## Question
Rejecting a zone-preserving null and an edge-glyph null *separately* (PHASE_753) is expected even with no residual. Does
an excess of zero cells among common Currier B token bigrams survive a null that preserves line composition, zones and
boundary glyph coupling *jointly*?

## Null N5 and diagnostics
MCMC over within-line permutations of movable MEDIAL tokens; target ∝ exp(−β · L1) with L1 the per-section distance
between the edge-count matrices (last unit → first unit) of the state and the real text. Pilot (β grid 0.5–8): β = 2, 4,
8 admissible for EVA edges; only β = 2 for glyph-unit edges.
| Unit | Attempts | Outcome |
|---|---|---|
| EVA | β 8 (×1, ×2), β 4 (×1, ×2): chains did not mix (ESS for Z 7–34, R-hat for fraction changed 1.7–2.3) | β = 2, doubled: **all diagnostics passed** — R-hat ≈ 1.00, ESS(Z) 6,570, ESS(fraction changed) 1,115, 83% of movable positions changed, max section edge TV 0.007 |
| GLYPH | β = 2 (×1, ×2) | **not achieved**: ESS for fraction changed 940 < 1,000 (R-hat 1.003, ESS(Z) 6,903) — narrowly failed; did not enter the verdict |
At β = 8 the chain stays on exact-preservation states (L1 ≈ 0) but moves too slowly; at β = 2 the edge matrices are
preserved within TV ≤ 0.007 (tolerance 0.018–0.02).

## Results (EVA edges, β = 2)
| Data | Statistic | Candidates | Real zeros | Null mean ± sd | p |
|---|---|---|---|---|---|
| Primary (P text, blockers) | **cleaned, E ≥ 3 (primary)** | 247 | **2** | 1.98 ± 1.39 | **0.60** |
| | raw, E ≥ 3 | 250 | 5 | 2.02 ± 1.41 | 0.054 |
| | cleaned, E ≥ 5 | 93 | 0 | 0.05 ± 0.23 | 1.0 |
| C957-identical data (all placements; reported) | cleaned, E ≥ 3 | 269 | 3 | 2.25 ± 1.49 | 0.39 |
| | raw, E ≥ 3 | 273 | 7 | 2.30 ± 1.51 | 0.009 |
L1 extrapolation changes nothing (slope ≈ 0 at β = 2); leave-one-cell-out: p 0.86 (cleaned, removing chey→chedy).
**Track-fragile cells** (zero in H, attested in F or C): aiin→aiin (F: 2), shedy→daiin (F: 1), qokeedy→ol (F: 1); on the
C957 data also shedy→lchedy (F: 1). None is attested in C (Currier); none appears as a concatenated single token.
Frozen lines carry 0.15% of the candidates' expected counts.

## Verdict (locked rules): REDUCES
p_EVA (cleaned) = 0.60 ≥ 0.10 with the glyph-unit null not achieved → REDUCES. The common-token zero-cell excess is
explained by line composition, positional zones (C956) and boundary glyph coupling (C1212/C1563); the reduction did not
need glyph-unit edges.

## Reading
- There is no token-level "prohibition" layer left in Currier B beyond known positional and boundary effects. With the
  class-level hazard topology already demoted (C783, C2060, C2063), the "forbidden transition / hazard" storyline has no
  surviving support.
- The small residual that the raw statistic shows is transcription-dependent: every extra zero is a pair that the First
  Study Group transcription reads as present. Whether H or F is right for those five occurrences is an image question.
- Methodological: exact edge preservation (β ≥ 4) freezes the chain; a soft constraint at β = 2 kept edge distributions
  within 0.7% TV while mixing well. Future joint nulls on this corpus should start there.

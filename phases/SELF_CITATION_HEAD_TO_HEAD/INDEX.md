# SELF_CITATION_HEAD_TO_HEAD

**Status:** COMPLETE (2026-06-08) | **Verdict:** RIVAL EXCLUDED (pre-registered kill conditions) | **Registered:** C2077 (Tier 2)

## Question

Can Timm & Schinner's self-citation / copy-modify generation model — the mainstream academic
non-semantic account of the Voynich, never previously tested head-to-head — account for Currier B's
structure? It attacks the DESIGNED/FUNCTIONAL half of the frozen Tier-0 conclusion (both sides agree
the text is non-semantic).

## Design

`PRE_REGISTRATION.md` — locked 2026-06-08 BEFORE generator construction, via three-expert
consultation (advisor / lean adjudication / crazy steelman), with kill conditions, fit/eval split
(P1), single-fit rule (P2), ensemble criterion (P3), pre-flight audits (P4), controls (P6), and a
pre-committed Tier-0-rewrite branch had the rival passed.

## Pipeline

| Script | Purpose | Result |
|---|---|---|
| `scripts/p0_preflight_audits.py` | P4a C783 denominator audit; P4b C458 frequency-matched CV | K1 class-level DEAD (forbidden O/E≈1.13 — misspecified, registry compression); K5 DEAD (freq shadow, corrected gap 0.089) |
| `scripts/p0b_strict_adjacency_verification.py` | strict-adjacency verification, class + token levels | class level confirmed at-null; TOKEN level confirmed: 9 forward bigrams 0 obs vs ~37.5 exp, reverses at-null → K1′ re-staked |
| `scripts/p1_generator_fit.py` + `p1b_refine.py` | 8-param uniform-glyph-kernel copy-modify generator, fitted on locked surface set (~500 evals, Yule–Simon long-range mode required) | best loss 2.62; **residual misfit structural: types 1.8×, Zipf flat — B's novelty is morphology-channeled** |
| `scripts/p2_battery.py` | 200-corpus ensemble vs B; M2 Markov + scramble controls (N=60) | **generator FAILS K2 (−0.108 vs B −0.019) and K4 (lag1 0.20 vs B 0.035; M2 matches B exactly) decisively; K1′ via expressibility+census** |

## Verdict (per locked map, §7/§12)

Generator fails ≥2 of 3 live kills → **self-citation excluded as a complete account of Currier B**
(C2077). Side findings: C783 demoted 2→3 (class-level projection shows no suppression; the real
prohibition layer is token-level, C957 — directionality verified, reverses at-null); C458 demoted
2→3 (clamp/free CV asymmetry is a frequency shadow). K4 sign-prediction was mis-calibrated against
this operationalization (C2032's −0.66 is a different instrument) — the ensemble criterion carried
the kill; recorded per registration-calibration discipline.

## Results files

`results/p0_preflight_audits.json`, `results/p0b_strict_adjacency.json`,
`results/p1_generator_fit.json`, `results/p2_battery.json`

# Phase 685: Section S Token-Level Thermal Coupling

**Status:** COMPLETE — 1 constraint registered (Tier 2)
**Started:** 2026-05-04
**Goal:** Test whether Currier B Section S folios exhibit token-level e-depth autocorrelation absent from Section B.

## Background

Scatter-shot exploration (round 2) ran 10 distributional probes. The strongest signal: token-level lag-1 autocorrelation of e-depth (the count of 'e' atoms in token MIDDLE — interpreted per C1455 as balneum mariae thermal signature) is dramatically section-dependent. Section S folios cluster e-depth values token-to-token; Section B folios do not.

Per crazy-expert framing: "B encodes thermal state at REGIME/PREFIX level (set once, executed). S encodes it at token level (tracked continuously)." Different control granularity, not different thermal involvement.

## Tests

### Killer test: within-paragraph, cross-token, marginal-preserving

**Pre-registered controls (locked before running):**
- C1: Within-paragraph pairs only (skip cross-paragraph pairs — controls C1308 within-paragraph coherence)
- C2: Cross-token-type only (skip pairs where token[t] == token[t+1] — controls C1789 repetition)
- C3: Marginal-preserving null (shuffle e-depths within folio preserving count of each e-depth value — controls C1106 marginal-shape inflation)

**Pre-registered criteria:**
| | Test | Threshold |
|--|------|-----------|
| P1 | S vs B mean z permutation (10000 perms) | p<0.01 |
| P2 | S mean z (after all controls) | ≥ +1.5 |
| P3 | Top-5 folios from exploration survive | ≥3/5 with z>2 |
| P4 | S frac z>2 AND B frac z>2 | S≥30%, B==0 |
| P5 | Within REGIME_1 (C1404 control), S vs B p | p<0.05 |
| P6 | Mode-B-residualized (C1260 control), S vs B p | p<0.05 |

**Results: 6/6 PASS.**

| Test | Result | Verdict |
|------|--------|---------|
| P1 | p=0.0001 | PASS |
| P2 | S mean z=+1.513 | PASS |
| P3 | 5/5 top folios survive (f112v=+4.98, f108r=+3.91, f111r=+4.05, f55v=+3.34, f95r2=+2.76) | PASS |
| P4 | S=39.1% (9/23), B=0/19 | PASS |
| P5 | Within REGIME_1: S(n=10) mean=+2.31, B(n=19) mean=-0.35, diff=+2.66, p<0.0001 | PASS (effect WIDENS within-REGIME) |
| P6 | After Mode-B-residualization: S vs B diff=+1.81, p<0.0001 | PASS |

### Section/REGIME breakdown

| sec | REGIME | n | mean_z | sig (z>2) |
|-----|--------|---|--------|-----------|
| B | REGIME_1 | 19 | -0.35 | 0/19 |
| S | REGIME_1 | 10 | +2.31 | 5/10 |
| S | REGIME_3 | 12 | +0.86 | 4/12 |
| S | REGIME_4 | 1 | +1.38 | 0/1 |
| H | REGIME_1 | 2 | -0.17 | 0/2 |
| H | REGIME_2 | 13 | +0.72 | 2/13 |
| H | REGIME_3 | 5 | +0.99 | 0/5 |
| H | REGIME_4 | 12 | +0.86 | 3/12 |
| C | REGIME_2-3 | 4 | +1.10 | 1/4 |

### Top folios (by killer-test z)

| folio | sec | regime | mode_B% | lag1 | z | n_pairs |
|-------|-----|--------|---------|------|---|---------|
| f112v | S | REGIME_1 | 17% | +0.240 | +4.98 | 401 |
| f108r | S | REGIME_1 | 12% | +0.181 | +3.91 | 468 |
| f55v | H | REGIME_2 | 67% | +0.305 | +3.34 | 101 |
| f111r | S | REGIME_1 | 6% | +0.162 | +4.05 | 601 |
| f107r | S | REGIME_1 | 22% | +0.113 | +2.78 | 470 |
| f95r2 | H | REGIME_4 | 36% | +0.278 | +2.76 | 76 |
| f112r | S | REGIME_1 | 30% | +0.113 | +2.21 | 381 |
| f86v5 | C | REGIME_3 | 59% | +0.103 | +2.13 | 369 |
| f66v | H | REGIME_4 | 33% | +0.193 | +2.08 | 113 |
| f113v | S | REGIME_3 | 7% | +0.095 | +2.08 | 460 |

### Bottom (most anti-correlated)

f80r at z=-2.77 is the only significant anti-correlation in the corpus (Section B). Recipes that *alternate* e-depth token-to-token rather than coupling.

## Verdict

**Tier 2 structural fact registered as C1994.** Effect survives:
- Vocabulary-repetition control (C1789)
- Within-paragraph stratification (C1308)
- Marginal-preserving null (C1106)
- REGIME stratification (C1404) — effect WIDENS within REGIME_1
- Mode-B-line-fraction residualization (C1260)

**Tier 3 substantive interpretation (C1995):** S and B implement different thermal-control architectures. B uses categorical thermal commitments (REGIME/PREFIX selects state, executed across paragraph). S uses continuous thermal tracking (state propagates token-to-token within paragraph).

## Constraints Registered

### C1994 (Tier 2): Section S token-level e-depth autocorrelation

Currier B Section S folios (n=23, Pharmaceutical/Stars f103-f116) exhibit lag-1 autocorrelation of e-depth on within-paragraph cross-token-type adjacent pairs at mean z=+1.51 vs marginal-preserving null. Section B folios (n=19, alchemical recipes f75-f86) show mean z=-0.36 with 0/19 folios at z>2. S vs B permutation p=0.0001 (10000 perms, n_perm=500 per folio for null). Effect WIDENS when restricted to REGIME_1 (S_R1 mean=+2.31, B_R1 mean=-0.35, diff=+2.66, p<0.0001 — not REGIME-mediated). Survives Mode-B-line-fraction residualization (residualized S vs B diff=+1.81, p<0.0001 — not Mode-B-mediated). Five top folios from exploration (f112v=+4.98, f108r=+3.91, f111r=+4.05, f55v=+3.34, f95r2=+2.76) survive killer-test controls. Pure structural fact about token-token e-depth coupling distribution; interpretation registered separately as C1995.

**Tier:** 2 (Currier B section-comparison structural fact, all confounds controlled)

### C1995 (Tier 3): Different thermal-control architectures S vs B

Section S and Section B exhibit different thermal-control granularities consistent with C1994's structural finding. Section B encodes thermal state categorically (REGIME/PREFIX selects a thermal commitment that is executed across an entire paragraph; token-level e-depth values are independent given the commitment). Section S encodes thermal state continuously (e-depth values propagate token-to-token within a paragraph; sustained-state behavior at the token level). Direct corollary: matched alchemical recipes (Pseudo-Lull Testamentum) in Section B operate as discrete-batch thermal programs; Section S pharmaceutical-style recipes operate as closed-loop continuous-state thermal programs. Generalizes C1206 paragraph kernel gradient (smooth e-depth across paragraph) from paragraph-scale to token-scale, but only in Section S. Connects to C1260 thermal state propagation (Mode B mechanic) and C1768-C1771 Stars monitoring axis as operational philosophy. Not falsification of C1404 (REGIME-determined PREFIX programs) — the architectures are orthogonal: REGIME selects PREFIX program, granularity selects how thermal state evolves within that program.

**Tier:** 3 (Currier B, observation; substantive interpretation derived from C1994 structural fact)

## Scripts

- `s1_exploration.py` — round-2 scatter probes (10 ideas from crazy-expert), found e-depth tempo as #3 lead
- `s2_killer_test.py` — pre-registered killer test with 3 controls + REGIME stratification + Mode B mediation

## Relationship to Existing Constraints

- **C1206** (paragraph kernel gradient — smooth e-depth across folio quintiles): C1994 extends from paragraph-scale to token-scale, but section-specific
- **C1404** (section determines PREFIX programs): C1994 within-REGIME confirms section is the load-bearing variable, not REGIME
- **C1260** (Mode B thermal state tracking): C1994 survives Mode-B-line-fraction residualization — token-level coupling is *not* a Mode B sub-effect
- **C1455** (balneum mariae thermal signature): grounds the e-depth interpretation as a thermal control parameter
- **C1768-C1771** (Stars monitoring axis as operational philosophy): C1995 substantively integrates with this thread
- **C1733** (two-strategy safety): consistent — B uses categorical commitments, S uses continuous tracking
- **C1789** (local repetition): C1994 controls for this directly (cross-token-type-only filter)
- **C1308** (within-paragraph category coherence): C1994 controls for this (within-paragraph stratification)
- **C1106** (e-depth marginal): C1994 controls for this (marginal-preserving null)

## Limits

- 23 S folios + 19 B folios = sample is finite. Effect is robust within current sample but generalization to full alchemical-corpus families would require external-source recipe collections.
- Tier 3 interpretation (C1995) is logically grounded but not directly tested. Promotion to Tier 2 would require showing predictive value of the granularity-distinction (e.g., predicting recipe-source structure from S/B classification beyond what C1404 already explains).
- f80r as outlier (z=-2.77) is a Section B folio with anti-correlated e-depth — interesting subcase, not characterized.

## Methodological Note

Pre-registration discipline held throughout: killer test was specified BEFORE the second-round controls were run, with explicit pass/fail thresholds. All 6 criteria specified in advance were met.

The session demonstrated **why expert consultation works**:
- Crazy-expert proposed the e-depth tempo probe (idea #3 in their brainstorm)
- Crazy-expert flagged the three load-bearing confounds (vocabulary repetition, marginal shape, paragraph coherence) before the killer test was written
- Expert-advisor flagged the two further confounds (REGIME, Mode B) for full Tier 2
- All five confounds controlled simultaneously; effect survives

The user's "follow the evidence where it leads" instruction produced a clean register on the third try (Phase 684 f66r → Phase 685 S thermal coupling). Both phases used scatter-shot exploration → killer test pattern.

# Phase 676: Cross-Cipher Token Consistency Test

**Status:** COMPLETE
**Started:** 2026-05-03
**Goal:** Test the foundational assumption that Voynich tokens carry cipher-invariant operational meaning, not substance-coupled meaning. Required by C171, C1394, C1976 but never directly tested against the SISMEL Testamentum's multi-cipher source structure.

## Setup

The Pseudo-Lull Testamentum source uses different cipher systems in different parts:
- Part II: A–H cipher, B = mercury
- Part III: B–G cipher, B = simple water (different substance!)
- Tavola 2: mirror-script (separate mechanism)
- Practica de Furnis: own conventions

Our 11 matched folios split:
- **Part II:** f76r, f84r (n=2)
- **Part III:** f75r, f79r, f82r, f76v, f81v, f112v, f103r, f116r, f112r (n=9)

The matching catalog (Phase 668, C1971) implicitly assumes Voynich tokens carry **cipher-invariant operational meaning** — `qo` means "thermal injection" regardless of whether the encoded source-passage describes mercury (Part II) or water (Part III) processing. Never directly tested.

## Pre-Registration

**Hypothesis:** Frequent Voynich tokens have statistically equivalent operational profiles on Part-II-matched folios and on REGIME/Section-matched Part-III-matched folios.

**Trap (per expert-advisor):** f76r/f84r are both REGIME_1/Section B. A naive Part-II vs Part-III comparison confounds cipher with REGIME. **Required control:** stratify Part-III into Section-B subset (REGIME-matched: f75r, f79r, f82r, f76v, f81v) and compare specifically against that subset, with REGIME-mismatched Section-S subset (f112v, f103r, f116r, f112r) as section-confound check.

**Test:** For each token X with n≥5 in BOTH Part II pool AND Part III B-section pool, compute per-token operational profile (mean line position, mean e-depth, terminal/head atom rates). Aggregate mean distance.

**Falsification:** Between-part mean distance > within-Part III random-split null at p < 0.05 → tokens have substance-coupled meaning → matching catalog needs Part-II/Part-III stratification.

## Results

**30 common tokens** (n ≥ 5 in both Part II pool and Part III B-section pool).

| Comparison | Mean distance | Notes |
|------------|--------------|-------|
| Part II vs Part III B-section (REGIME-matched) | **0.086** | actual |
| Within-Part III B-section random splits | 0.139 | null |
| Part II vs Part III S-section (REGIME-mismatched) | 0.124 | section-confound check |

**p(actual ≥ random within-Part III) = 0.93** — actual is SMALLER than random null.

Per-token results:
- Position differences mostly 0.01–0.20
- Mean e-depth diff = 0.000 across all 30 tokens (per-word e-depth is structurally invariant; this dimension doesn't add variance)
- Most tokens with very low between-part distance: chedy (0.010), qokeey (0.001), qokaiin (0.010), saiin (0.011), otedy (0.001)

The Part II vs Part III S-section distance (0.124) is slightly higher than the Part II vs Part III B-section distance (0.086), consistent with REGIME being a real but secondary factor — confirming that the section-matched comparison was the right control.

## Verdict

**Tier 3 observation: consistent with cipher-invariance under section/REGIME-matched comparison.**

Tokens look operationally equivalent across Part-II-matched and Part-III-matched folios at the section-matched comparison level. The cipher-invariance hypothesis is not falsified; it survives a controlled test for the first time.

**Why Tier 3 not Tier 2** (per expert review):

1. **n=2 Part-II folios is sample-thin.** Cannot distinguish "cipher-invariant" from "f76r/f84r happen to share REGIME/section character with the Part-III B pool" at scale.
2. **Mean e-depth diff = 0.000 is partly trivial.** Per-token e-depth is structurally invariant (the same word form has the same e-depth always). The position-only variance (0.086) is the load-bearing measurement.
3. **Crazy-expert flagged scope-restriction:** the test validates a TOKEN-LEVEL property within section-matched strata, not "all cipher systems" universally.

## Constraint Update

### C1987 (Tier 3, observation): Cross-cipher token operational profiles equivalent under section-matched comparison

For 30 frequent Voynich tokens (n≥5) appearing in both Phase-668-validated Part-II-matched folios (f76r, f84r) and Part-III B-section-matched folios (f75r, f79r, f82r, f76v, f81v), per-token operational profiles (mean position, e-depth, terminal/head rates) are statistically equivalent. Mean profile distance Part II vs Part III B-section = 0.086, smaller than within-Part III random-split null (0.139) — actual is closer than random (p ≈ 0.93 one-sided for between > within). REGIME-mismatched control (Part II vs Part III S-section) = 0.124, slightly higher, consistent with REGIME as secondary factor.

Result is consistent with the implicit foundation of the matching catalog (C1971): Voynich tokens carry operational meaning that is invariant to source-cipher context. NOT falsified for the first time on a controlled test.

**Scope limit:** n=2 Part-II folios; cannot generalize to "all cipher systems." Mean e-depth diff = 0.000 is partly structurally trivial. Per-token position variance is the load-bearing measurement.

**Tier:** 3 (Currier B, foundation-consistent observation under section-matched comparison)

## Methodological Notes

- Pre-registered comparison structure with REGIME control included
- Direction predicted (cipher-invariant → equivalent profiles) and confirmed
- Result is structurally informative: actual distance SMALLER than random null, not just "no significant difference"
- Sample-thin Part II side prevents Tier 2 promotion despite clean directional result
- Both experts converged on Tier 3 with scope-limit framing

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_cipher_consistency_test.py | Token operational profile comparison + within-Part III null + REGIME-mismatched control | ~10s |

## Relationship to Existing Constraints

- **C171** (atom semantics stable across prefix channels): C1987 extends to "stable across cipher contexts" at the section-matched comparison level.
- **C1394** (HEAD+MOD*+TERM atom model): consistent — atom roles encode operations independent of substance.
- **C1976** (polyalphabetic cipher REJECTED, atoms stable): C1987 strengthens this with cross-cipher-source verification under control.
- **C1971** (Phase 668 cold read coherence): foundation assumption now has direct evidence rather than inference.
- **C1808** (section significantly affects 13/14 PREFIX fractions): the REGIME-matched comparison was specifically designed to control for this confound.

## Suggested Follow-Up

- **More Part-II matches:** if additional Voynich folios get matched to Part II chapters in future phases, increase n_Part-II folios to enable Tier 2 promotion.
- **Cross-corpus replication:** test the same invariance against Brunschwig-matched folios if any are validated in future phases.

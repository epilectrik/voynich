# Phase 683b Pre-Registration: Balneum Signature Retest

**Locked: 2026-05-04, before any retest data inspection.**

## Context

C1970 (Phase 664) claimed CONFIRMED-tier matched folios have elevated ke/ek RATIO (mean=9.74) vs supported (5.03) and corpus (4.68), d=+1.04, p=0.0023. **PERMANENTLY RETRACTED v6.37 per Phase 667** — ratio metric was artifactual (unstable when denominator small). Corrected metric ke/(ke+ek) PROPORTION gave d=+0.256, p=0.24 — directionally consistent but underpowered.

New visual evidence: rosettes_annotated.json describes CENTER as "6 alembic/retort vessels in shared heating medium - balneum mariae - strikingly similar to Brunschwig's woodcuts." This iconographic identification motivates retesting the underlying claim with corrected methodology.

Both experts agree:
- Retraction is metric-specific, not claim-permanent
- Pattern fits C1966/C1967 (signal preserved at lower magnitude after correction)
- Retest with proper pre-registration is methodologically clean

## Hypothesis

**H1:** CONFIRMED-tier matched folios + supported-tier matched folios (combined: 11 folios with 8 coherent + 3 partial) have elevated indirect/dampened-thermal signature vs corpus baseline.

**Underlying claim:** Matched recipes (which describe gentle-heat / balneum operations explicitly) have a quantifiable text signature distinguishing them from corpus average.

**Tier ceiling:** Tier 3 maximum (correspondence claim, not direct validation of "CENTER=balneum"). Iconographic claim stays Tier 4 regardless of outcome.

## Operational Definitions

**Sample:**
- Matched folios (n=11): f75r, f76r, f76v, f79r, f81v, f82r, f84r, f103r, f112r, f112v, f116r
- Corpus baseline: all body B paragraphs from non-matched folios

**Primary metric:** ke/(ke+ek) proportion per paragraph
- Token-level: count k+e bigrams (ke pattern) and e+k bigrams (ek pattern) within each token's MIDDLE atoms
- Paragraph-level: sum ke counts and ek counts, compute proportion = ke / (ke + ek)
- Sample unit: paragraph (not folio), to maximize n

**Secondary metrics** (Bonferroni alpha=0.0167):
- M2: e_depth>=2 token fraction per paragraph (per C1225 e-depth = thermal dampening)
- M3: kernel-e fraction (e count / total kernel atoms k+h+e)

## Pre-Registered Tests

### PRIMARY (T1)

**Statistic:** Mann-Whitney U comparing matched-folio paragraph distribution to corpus-baseline paragraph distribution on ke/(ke+ek) proportion. One-tailed (matched > corpus, directional from C1970 history).

**Pass criterion:**
- Cohen's d >= 0.35
- p < 0.05 (one-tailed)
- LOO safeguard: drop each matched folio, recompute; minimum d >= 0.20

### SECONDARY (T2, T3)

Run only if T1 passes (per stopping rule).

**T2:** e_depth>=2 token fraction. Same Mann-Whitney design. Pass: d>=0.35, p<0.0167 (Bonferroni).

**T3:** kernel-e fraction. Same. Pass: d>=0.35, p<0.0167.

### NEGATIVE CONTROL

**N1:** Permutation null — shuffle folio labels (matched/non-matched) 10000x, recompute Mann-Whitney d. Required: actual d in <5% of permutations.

**N2:** Phase 642 cluster folios as positive control comparator. If cluster folios (which are non-matched but herbal-section-rich) show d closer to matched than to corpus, the signal is section-driven, not match-driven.

## Stopping Rules

- **If T1 p > 0.10:** Do NOT run T2/T3. Workshop interpretation stays Tier 4. Document as "underlying claim not statistically supported with corrected methodology."
- **If T1 p < 0.05 but d < 0.35:** Underpowered evidence. Document as suggestive but not registerable.
- **If T1 d >= 0.35 AND p < 0.05:** Run T2/T3 with Bonferroni. Register new constraint citing C1970 retraction history.
- **If LOO minimum d < 0.20:** Single-folio dependency; do not register.

## Decision Tree

| Outcome | Verdict | Action |
|---------|---------|--------|
| T1 d>=0.35, p<0.05, LOO holds, T2+T3 also pass | Strong signal: register Tier 3 (analog of C1972 e-depth tracking) | Register C198X with corrected methodology lineage to C1970 |
| T1 d>=0.35, p<0.05, LOO holds, T2/T3 mixed | Primary signal only: Tier 3 narrow | Register narrow scope |
| T1 marginal (0.10>p>0.05 or d<0.35) | Underpowered: no registration | Document as bound on claim |
| T1 null (p>0.10) | Underlying claim NOT supported | Workshop interpretation Tier 4 ceiling final |

## What Will NOT Happen

- No post-hoc adjustment of metrics if T1 fails
- No "let me try a different metric" salvage if T1 fails
- No registration based on direction alone without effect size + p
- No tier promotion above Tier 3 from this test
- No claim that this validates "CENTER = balneum apparatus" specifically — that stays Tier 4 iconographic

## Crazy-Expert Bet (For Calibration)

> "d=+0.30 to +0.40, p=0.04-0.12, marginally significant or borderline. Most likely outcome: directionally consistent, power-limited."

If outcome matches this bet (marginal), document as borderline and don't register. Use as calibration check.

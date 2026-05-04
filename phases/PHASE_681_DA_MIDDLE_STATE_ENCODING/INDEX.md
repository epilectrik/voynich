# Phase 681: da-MIDDLE State Encoding Test on f84r

**Status:** COMPLETE — pre-registered test rejected
**Started:** 2026-05-04
**Goal:** Test the hypothesis that da-prefix MIDDLE composition encodes material state (refinement of C897 FL TERMINAL state markers extended to da-prefix MIDDLE).

## Pre-Registered Test (locked in PRE_REGISTRATION.md)

PRIMARY (ARI clustering): cluster f84r dar tokens' MIDDLE atom-sets via Jaccard distance, k=4. Compute ARI between cluster assignments and paragraph-quartile bins. Pass: ARI > 0.30, p < 0.01.

SECONDARY (Mantel correlation): pairwise paragraph-distance vs MIDDLE-Jaccard-distance. Pass: rho > 0.30, p < 0.01.

## Result: Test Inapplicable for dar Specifically

**Critical structural finding embedded in failure:** All 13 dar tokens in f84r atomize identically — `dar` = prefix `da` + single SOLE atom `r`. **No MIDDLE composition variability exists within the dar token form.**

The hypothesis "MIDDLE composition encodes state" is structurally inapplicable to dar — the token has no compositional MIDDLE to vary.

Expanding to all da-prefix tokens (n=25 in f84r) gives 8 with non-empty MIDDLE atoms (the daiin/dain/dair forms). On this expanded set:
- ARI: -0.089 (p=0.82) — opposite direction, totally null
- Mantel: 0.000 (p=1.00) — perfectly null

## Verdict

Per pre-registration decision tree: **STATE-ENCODING REJECTED for f84r dar; identification-vocabulary explanation per C1135 prevails.**

The substantive nuance: short da-prefix tokens (dar, dal, dam) lack compositional MIDDLE; longer da-prefix forms found on rosette paths (darchdy, daldal, daraldy) have compositional MIDDLEs but matched-recipe folios use predominantly the short forms. The state-encoding question for compositional da-prefix forms remains untested at current sample sizes.

## Tier Assessment

NOT registered as Tier 1 falsification because the test was structurally inapplicable for dar specifically (no MIDDLE to vary). Documented as a methodological lesson: state-encoding hypotheses must specify the granularity of compositional variation; dar has no MIDDLE composition.

## Methodological Note

Pre-registration discipline worked: hypothesis was specifically defined, test was clean, structural inapplicability was discovered through the data not retrofit afterward. The "all 13 dar atomize identically" finding emerged from the test execution, refining our understanding of dar's place in the morphology.

## Scripts

- `s1_test_state_encoding.py` — pre-registered ARI clustering + Mantel test

## Relationship to Existing Constraints

- **C897** (FL TERMINAL MIDDLEs as state markers): Hypothesis was extension to da-prefix; not supported for dar specifically
- **C1925** (dar = material introduction, 5 distribution patterns): Refined understanding — dar's invariant morphology is consistent with "simple material marker" not "stateful material descriptor"
- **C1135-C1142** (dark pipeline = identification vocabulary): Identification-vocabulary explanation prevails
- **C1394** (HEAD+MOD*+TERM atom model): No conflict; refines understanding of dar's atomization

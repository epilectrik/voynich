# Phase 689: qotar Morphological Clustering Mechanism

**Status:** COMPLETE — 1 constraint registered (C2002, Tier 2 NULL); three pre-registered mechanisms FALSIFIED
**Started:** 2026-05-07
**Completed:** 2026-05-07
**Goal:** Identify what specifically drives qotar's morphological clustering. Phase 688 established that qotar's high MI (Phase 687 z=+3.95, rank 1/72) collapses at cross-tier (z=−0.20) — qotar's apparent context propagation is morphological co-occurrence, not operational embedding. This phase asks: WHAT KIND of morphological co-occurrence?

## Result summary

**All three pre-registered mechanisms FALSIFIED.** qotar's morphological clustering is NOT same-stem density (1.7% vs predicted >30%), NOT folio concentration (Gini 0.684 vs predicted >0.70), and NOT S/C section concentration (χ²=5.39, p=0.25; S/C ratio 1.15 vs predicted >1.5).

| Test | Predicted | Observed | Verdict |
|------|-----------|----------|---------|
| T1 same-stem density | > 30% | **1.7%** (2/121) | **FAIL** |
| T2 folio Gini | > 0.70 | **0.684** | **FAIL** |
| T3 S/C section concentration | χ² p<0.01 AND ratio>1.5 | p=0.25, ratio=1.15 | **FAIL** |
| T4 qokedy comparison (compound) | qokedy lower on all three metrics | mixed (PARTIAL) | PARTIAL |

**Surprising counter-finding:** qokedy (operational embedder per C2001) has **9.2× higher** same-stem density (15.7%) than qotar (alleged morphological clusterer at 1.7%). This contradicts what Phase 688's framing would have predicted.

**Phase 688's "morphological clustering" interpretation of qotar/chol is empirically refuted at same-stem density level.** The cross-tier z=−0.20 measurement stands; the mechanism explanation needs amending.

## Methodological lesson

Phase 688 inferred mechanism ("morphological clustering") from a measurement (cross-tier MI z collapse). Phase 689 demonstrates this inference was over-stepping — cross-tier collapse measures *whether* MI propagates, not *why* it doesn't. Saved as feedback memory: `feedback_measurement_vs_mechanism.md`.

## Background

Phase 687 found qotar as the #1 context propagator among 72 eligible Currier B tokens (z=+3.95, n_triplets=61). Phase 688 cross-tier decomposition revealed this MI is driven entirely by qo-family co-occurrence: when (prev, next) pairs are restricted to non-qo prefixes, qotar's MI z drops to −0.20.

Three candidate mechanisms for qotar's morphological clustering (mutually compatible — could combine):

**M1: Same-stem run (Section S signature per C1995).** qotar appears in dense runs of morphological near-relatives (qotar→qoteedy→qotedy→qotar). The Section S finding from Phase 685 documented this as an S-specific operational compactness pattern.

**M2: Folio concentration.** qotar is concentrated in specific folios where local vocabulary repeats. Folio-specific clustering rather than corpus-wide pattern.

**M3: Section concentration.** qotar appears predominantly in Section S (where C1995 documents same-stem runs as a structural property), not Section B (which exhibits operational alternation per C1995).

These predict observable patterns in qotar's empirical distribution.

## Definitions (locked)

For the empirical analysis:

**qotar instance:** any occurrence of the exact token "qotar" in Currier B H-track filtered corpus (no labels, no asterisks).

**Same-stem neighbor:** a token T is same-stem with qotar if Levenshtein distance(T, qotar) ≤ 1 OR T shares qotar's MIDDLE atom sequence after qo-prefix.

**Adjacent token:** the token immediately before (prev) or after (next) qotar within the same paragraph.

**qokedy comparison set:** identical analysis applied to qokedy as the "operational embedder" reference (Phase 688 cross-tier z=+2.49).

## Locked methodology

| ID | Spec |
|----|------|
| M1 | Currier B tokens, H-track only, no labels, no asterisks |
| M2 | qotar and qokedy instances enumerated by folio + line + paragraph |
| M3 | Same-stem definition: Levenshtein ≤ 1 OR same MIDDLE atoms after qo-prefix |
| M4 | Adjacent tokens: prev (t−1) and next (t+1), excluding paragraph-boundary cases |
| M5 | Section labels from Transcript metadata (H/B/S/C/P/T/Z/A) |
| M6 | Folio concentration measured by Gini coefficient on per-folio counts |
| M7 | Section concentration measured by χ² test of qotar count vs token-count proportion per section |

## Pre-registered tests

### T1 (Same-stem density) — qotar's adjacent tokens are dominated by same-stem neighbors

**Hypothesis:** Of qotar's adjacent (prev, next) tokens, > 30% are same-stem neighbors (Levenshtein ≤ 1 OR same MIDDLE).

**Reference baseline:** Typical Currier B tokens have ~5–10% same-stem neighbors at adjacent positions (estimate from Phase 685 Section B baseline of ~2% same-stem pair fraction).

**Pass:** Same-stem fraction > 30%.
**Fail:** Same-stem fraction ≤ 30% — clustering not driven by morphological repetition.

### T2 (Folio concentration) — qotar concentrates in few folios

**Hypothesis:** Gini coefficient of qotar instances across folios > 0.7 (high concentration).

**Reference baseline:** A randomly distributed token would have Gini ≈ 0.4–0.5 reflecting underlying token-count Gini.

**Pass:** Gini > 0.7. qotar is concentrated.
**Fail:** Gini ≤ 0.7. qotar is broadly distributed.

### T3 (Section concentration) — qotar appears predominantly in S/C sections (where same-stem density is documented per C1995)

**Hypothesis:** χ² test of qotar count by section, expected proportions = section token-count proportions. p < 0.01 with observed concentration in {S, C} > expected.

**Pass:** χ² p < 0.01 AND S+C observed/expected ratio > 1.5. qotar is section-clustered toward S/C.
**Fail:** Either χ² p ≥ 0.01 OR S+C ratio ≤ 1.5. qotar is not section-clustered as predicted.

### T4 (Comparison with qokedy) — qokedy shows different mechanism profile

**Hypothesis (compound):** qokedy has lower same-stem fraction than qotar AND lower Gini than qotar AND no S+C concentration. This would distinguish operational embedders from morphological clusterers as different mechanisms.

**Pass:** All three predictions hold simultaneously.
**Partial:** One or two predictions hold.
**Fail:** None of the predicted differences appear.

## Anti-HARK commitments

- All thresholds locked: T1 30%, T2 Gini 0.7, T3 p<0.01 + ratio 1.5.
- Same-stem definition fixed: Levenshtein ≤ 1 OR same MIDDLE atoms.
- Section grouping locked: {S, C} as expected concentration target (per C1995 Section S compactness; C as visual-diagram-text section that may share format).
- qokedy comparison set fixed (no other tokens substituted post-hoc).
- T4 compound hypothesis: ALL three predictions required for "PASS"; partial registration as such.

## Constraint registration plan

**C2002:** qotar morphological clustering mechanism (PASS/FAIL of T1+T2+T3 combined verdict).
- If all three pass: Tier 2 — qotar clusters via dense same-stem runs in S/C section concentration
- If 2 of 3 pass: Tier 2 — qotar clusters via [partial mechanism], dominant driver identified
- If 0–1 of 3 pass: Tier 2 — qotar morphological clustering is real (Phase 688) but does not match S-section-compactness mechanism

**C2003 (conditional on T4):** qokedy vs qotar mechanism contrast.
- Registers if T4 PASS (operational embedder vs morphological clusterer dichotomy supported across all three metrics)
- Tier 2 if registered

If T1–T3 all FAIL, C2002 still registers as a NULL result documenting that the proposed mechanisms do not explain qotar's clustering.

## Computational plan

Single script s1_qotar_mechanism.py:
1. Load Currier B tokens with folio/line/paragraph/section metadata
2. Find all qotar and qokedy instances
3. For each instance, identify adjacent tokens (prev, next)
4. Compute same-stem fraction for both tokens
5. Compute Gini coefficient of folio counts for both
6. Compute section distribution for both, χ² vs token-count proportions
7. Adjudicate T1, T2, T3, T4

Expected runtime: < 1 minute (small set of qotar instances).

## Relationship to existing constraints

- **C1300** — qo as 100% k-HEAD thermal channel (qotar has t-HEAD, not k-HEAD; different operational role)
- **C1394** — atom model: qotar = qo + t(HEAD, transfer) + a(MOD, yield) + r(TERM, respond)
- **C1995** — Section S operational compactness via dense same-stem runs; this phase tests whether qotar specifically exhibits this pattern
- **C1404** — section structural differentiation; predicts S/C distinct from B
- **C1808** — section qo-rate baselines (S~0.15, B~0.20)
- **C1999** — section-level z_μ ordering (S/C/B most order-constrained); consistent with same-stem clustering hypothesis for S
- **C2001** — qokedy operational embedding (Phase 688 confirmation)
- **Phase 688 auxiliary observation** — qotar morphological clustering is the finding this phase mechanistically dissects

## What this phase can and cannot establish

**Can establish:**
- Whether qotar's clustering is dominated by same-stem runs, folio concentration, section concentration, or some combination
- Whether qotar's mechanism profile differs from qokedy's (operational vs morphological)
- Whether the operational/morphological distinction tracks the S-section-compactness pattern from C1995

**Cannot establish:**
- Why qotar specifically (vs other qo-tokens) shows this pattern
- Whether qotar's clustering reflects production-side scribal habit or content-side recipe convention
- Whether the mechanism generalizes to other morphological clusterers (chol from Phase 688)

## Detailed results

### qotar empirical profile (n=61 instances, 121 adjacent positions)

| Metric | Value |
|--------|-------|
| Folios touched | 35/82 |
| Folio Gini | 0.684 |
| Top folios | f86v6 (5), f114r (4), f106v (3), f113v (3), f114v (3), f43r (2), f75r (2), f79r (2) |
| Section distribution | S=29 (47.5%), B=14 (23%), H=8 (13%), C=8 (13%), T=2 (3%) |
| Section χ² (vs corpus proportions) | 5.39, df=4, p=0.25 |
| S+C observed/expected ratio | 1.15 |
| Same-stem fraction | 1.7% (2/121) |
| Top adjacent tokens | otal (5×), shedy (4×), okar (3×), ain (3×), qotchdy (3×), okedy (2×), chdy (2×), otedy (2×), chedy (2×), opchedy (2×) |

### qokedy comparison (n=271 instances, 541 adjacent positions)

| Metric | Value |
|--------|-------|
| Folios touched | 61/82 |
| Folio Gini | 0.620 |
| Top folios | f77v (16), f108r (16), f78r (15), f75r (14), f78v (13), f83r (13), f84r (12), f84v (12) |
| Section distribution | B=164 (60.5%), S=61 (22.5%), H=40 (14.8%), T=4 (1.5%), C=2 (0.7%) |
| Section χ² | 135.36, p<0.0001 (highly section-skewed toward B, away from S) |
| S+C observed/expected ratio | 0.44 (under-represented in S/C) |
| Same-stem fraction | **15.7%** (85/541) — 9.2× higher than qotar |
| Top adjacent tokens | shedy (30×), qokedy (28× — self-iteration!), chedy (25×), qokeedy (23×), otedy (14×), qokeey (11×), okedy (10×), dal (10×), qokey (7×), dy (6×) |

### Why qokedy has higher same-stem density than qotar

Inspecting qokedy's top adjacents: qokedy itself appears 28× as adjacent to qokedy. This is the f75r ×4 self-iteration pattern (per C1965 cardinality anchor). qokedy → qokedy → qokedy runs are documented operational signature. qokedy ALSO has many adjacent qokeedy (23×), qokeey (11×) — morphological near-relatives.

So qokedy combines:
- Operational embedding (cross-tier z=+2.49 in Phase 688) — distinct context
- Self-iteration (28× qokedy-adjacent-qokedy) — counting cycles
- Morphological near-relatives in vicinity (qokeedy, qokeey)

qotar combines:
- High overall MI (z=+3.95) — measurement
- Cross-tier collapse (z=−0.20) — measurement
- Mostly o-prefix family neighbors (otal, okar, okedy, otedy) but NOT same-stem
- No self-iteration
- No same-stem density

These are structurally different operational profiles, not on the same dichotomy axis.

## Constraint Registered

### C2002 (Tier 2 NULL, Scope: B): qotar cross-tier MI collapse mechanism — three candidate mechanisms FALSIFIED

Pre-registered Phase 689 hypotheses for qotar's "morphological clustering" (Phase 688 cross-tier z=−0.20): **all FALSIFIED**.

- T1 (same-stem density): observed 1.7% (2/121 adjacent positions) vs predicted >30%. FAIL.
- T2 (folio concentration): observed Gini 0.684 vs predicted >0.70. FAIL.
- T3 (S/C section concentration): observed χ²=5.39, p=0.25, S+C ratio=1.15 vs predicted p<0.01 AND ratio>1.5. FAIL.

**Surprising counter-finding (T4 partial):** qokedy (operational embedder per C2001) has 15.7% same-stem density vs qotar's 1.7% — 9.2× higher. The operational embedder has *more* morphological clustering than the alleged morphological clusterer. Phase 688's framing of qotar/chol as "morphological clusterers" is empirically refuted at the same-stem-density level.

**The Phase 688 cross-tier z=−0.20 measurement is preserved**; what is refuted is the inferred mechanism. qotar's MI is NOT explained by same-stem density, folio concentration, or S/C section concentration. The actual mechanism remains under-determined.

**Likely explanation (NOT registered, observation only):** With qotar's small sample (n=61), the high overall MI is plausibly driven by a small number of specific recurrent (prev, next) joint pairs in qo-cluster + boundary tiers, not by diffuse family co-occurrence. qotar's neighbors are dominated by o-prefix-family tokens (otal, okar, okedy, otedy, opchedy) — family-level pooling at the o-prefix base, not at qo-stem level. This is consistent with qotar functioning as a junction/marker token (t-HEAD = transfer, r-TERM = respond per C1394 atom decomposition) rather than an iterative operational primitive like qokedy (k-HEAD = heat, thermal cycle).

These three modes (operational embedder, family-pooled, junction/marker) are a candidate for follow-up phase but NOT registered here — would require pre-registration.

**Tier:** 2 (Currier B structural fact, falsification of three pre-registered mechanisms)

**Scope:** B

**Connections:**
- C1995 (Section S operational compactness via dense same-stem runs) — predicted same-stem density mechanism for qotar; falsified for qotar specifically
- C1404 (section structural differentiation) — predicted S/C concentration; falsified for qotar
- C1962 (o-prefix runtime channel taxonomy), C1963 (qo→ok 72.9%) — qotar's o-prefix family neighbors consistent with qo↔ok junction role
- C1394 (HEAD+MOD*+TERM atom model) — qotar's t-HEAD/r-TERM atom profile suggests junction function
- C1971 (matched recipes catalog), C1965, C1988 — qokedy operational embedding context
- **C2001 (Phase 688 qokedy operational embedding)** — narrative needs amending: qotar/chol "morphological clustering" framing was over-interpretation; preserved measurement is cross-tier z=−0.20, mechanism remains under-determined
- C2000 (Phase 687 daiin state-flush rejection) — also a directional negative; pattern of failed mechanism inferences from MI measurements
- Methodological lesson: `feedback_measurement_vs_mechanism.md` — cross-tier MI z is a measurement, not a mechanism

## Scripts

- `s1_qotar_mechanism.py` — same-stem density, Gini, χ² section concentration; compares qotar vs qokedy

## What this phase establishes

1. **Three candidate mechanisms FALSIFIED.** Same-stem density, folio concentration, S/C section concentration — none explain qotar's MI inflation.
2. **qokedy has 9.2× higher same-stem density than qotar.** Operational embedder has more morphological clustering than the alleged clusterer — opposite of Phase 688's framing.
3. **qotar's neighbors are dominated by o-prefix family but not same-stem.** Family-level pooling at the o-prefix base is a candidate mechanism not yet tested.
4. **Phase 688's "morphological clustering" interpretation is empirically refuted at same-stem level.** Cross-tier z=−0.20 measurement stands; mechanism inference was over-stepping.
5. **Methodological lesson:** cross-tier MI z is a measurement, not a mechanism. Saved as feedback memory.

## What this phase does not establish

- *What* mechanism drives qotar's high overall MI (the 0.30→1.7%, 0.70→0.684, 1.5→1.15 pattern says "not these three"; doesn't say what is)
- Whether the o-prefix family pooling hypothesis (auxiliary) holds
- Whether chol (Phase 688's other "morphological clusterer") follows the same pattern as qotar
- Whether chcthy (Phase 688's other strong cross-tier signal at +3.78) is operational or marker

## Candidates for follow-up phases (NOT in this phase)

Per crazy-expert speculation, candidates that would build on Phase 689's null:
1. Run Phase 689's tests on chol (test family-pooling hypothesis at o-prefix base)
2. Compute o-prefix family concentration for qotar's neighbors (test the "family pool not same-stem" mechanism)
3. Test recipe-positional concentration for qotar (paragraph-slot specificity → junction marker hypothesis)
4. Run chcthy through Phase 689 tests
5. Bias-correct Phase 688 cross-tier MI for self-iterating tokens (qokedy's true context-coupling is underestimated when qokedy→qokedy self-iteration is filtered out)

None of these is committed — listed as candidates only.

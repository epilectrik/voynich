# Phase 687: Daiin State-Flush Hypothesis

**Status:** COMPLETE — 1 constraint registered (C2000); state-flush hypothesis REJECTED
**Started:** 2026-05-06
**Completed:** 2026-05-06
**Goal:** Test crazy-expert's reframe of daiin/dar/saiin as state-flush / context-reset operators rather than formulaic glue. The hypothesis: tokens preceding daiin should give little information about tokens following daiin (low context propagation = state-flush behavior).

## Result summary

**State-flush hypothesis REJECTED.** Pre-registered T1 failed: daiin's z_T = +0.76 (67th percentile of 72 eligible tokens), above the population median of −0.11. T2 passed (z < +1.0, no significant context propagation), but the *unusually low MI* prediction was wrong. daiin is moderate-context-propagation, not state-flush.

| Test | Verdict | Detail |
|------|---------|--------|
| T1 | **FAIL** | daiin z=+0.76 (67th %ile), median = −0.11. daiin ABOVE median, not below. |
| T2 | PASS | daiin z < +1.0; MI not significantly above shuffle null |
| T3 | **PARTIAL** | dar +0.91 (above median), saiin −0.41 (below median). No class pattern. |
| T4 | PASS | qokedy z=+2.51, shedy z=+2.07 — methodology can detect MI when present |

Per pre-reg: C2001 conditional on T3 clean PASS/FAIL; T3 PARTIAL → C2001 NOT registered.

## Background

Phase 686 C1998 found INFRA token H_succ EXCEEDS RI in Currier B (predicted direction REVERSED). daiin (n=314, H_succ=7.30 bits, ~150 distinct effective successors), dar (n=188, H=6.80), saiin (n=99, H=6.07) all show near-uniform successor distributions — anomalous for "infrastructure glue" tokens.

Crazy-expert reframe (registered as Tier 4 speculation, not adopted into constraint system): daiin functions as a **state-flush / context-reset operator**. After daiin, the next token is selected fresh, with the prior token carrying little information about what comes next. If true, this would reframe C557 (daiin line-initial trigger), C800 (HT escape driver), C843 (paragraph prefix markers), and the broader RI/PP/INFRA classification.

The cleanest single test: **mutual information** between predecessor and successor of daiin. If state-flush, MI(prev; next | T=daiin) ≈ 0. If context propagates, MI > 0 significantly.

## Definitions (locked)

For each token T appearing in middle position of a triplet (prev, T, next):
- Let pairs(T) = {(prev_i, next_i)} for all instances of T with both predecessor and successor in corpus
- I_actual(T) = empirical mutual information of (prev, next) given T as middle
- Null distribution: shuffle prev independently of next within T (preserves marginal P(prev|T) and P(next|T) but breaks any joint structure)
- z_T = (I_actual − mean(I_null)) / std(I_null)

Low z_T = MI not above shuffle = state-flush behavior (predecessor doesn't predict successor).
High z_T = MI well above shuffle = context propagation through T.

## Locked methodology

| ID | Spec |
|----|------|
| M1 | Currier B tokens only, H-track, no labels, no asterisks |
| M2 | Token T eligible if it has ≥50 (prev, T, next) triplets in the corpus |
| M3 | MI computed via plug-in estimator: I = Σ p(x,y) log₂(p(x,y) / (p(x)p(y))) |
| M4 | Null = 200 shuffles where prev is independently permuted within T |
| M5 | RNG seed = 42 (with token-specific salting per_token = 42 + hash(token) % 1000000) |
| M6 | All tokens with n_triplets≥50 ranked by z_T (ascending = most state-flush-like) |
| M7 | Median z_T computed over the eligible token set as reference |

## Pre-registered tests

### T1 (Primary, daiin) — daiin's z_T below population median

**Hypothesis:** daiin's z_T < median(z_T) across all eligible tokens.

**Rationale:** State-flush behavior should place daiin in the lower half of MI propagation magnitude.

**Pass:** daiin's z_T strictly less than the median z_T.
**Fail:** daiin's z_T at or above median (state-flush rejected for daiin).

### T2 (Strict, daiin) — daiin's z_T below significance threshold

**Hypothesis:** daiin's z_T < +1.0 (i.e., MI through daiin is not significantly above shuffle null).

**Rationale:** A genuine state-flush should not show statistically distinguishable context propagation. z_T < 1.0 corresponds to roughly p > 0.16 one-sided.

**Pass:** daiin z_T < 1.0.
**Fail:** daiin z_T ≥ 1.0 (some context propagation detected even if below median).

### T3 (Class generalization) — dar and saiin both below median

**Hypothesis:** dar (n=188) and saiin (n=99) both have z_T < median.

**Rationale:** If state-flush is a class property of these high-frequency function tokens, the pattern should generalize.

**Pass:** Both dar z_T < median AND saiin z_T < median.
**Partial pass:** Only one of dar/saiin below median — register as daiin-specific phenomenon.
**Fail:** Both at or above median — state-flush is daiin-specific, not class.

### T4 (Discrimination check) — content tokens demonstrate detectable context propagation

**Hypothesis:** At least one of {chedy, qokedy, qokeedy, qokeey, shedy} (high-frequency content/recipe tokens) has z_T > 2 (above shuffle null).

**Rationale:** If MI computation cannot detect context propagation in ANY token, the methodology is underpowered and T1-T3 results are uninterpretable. T4 is a sanity check that we CAN detect MI when present.

**Pass:** At least one content reference token has z_T > 2.
**Fail:** No content reference token shows context propagation — methodology is underpowered.

## Anti-HARK commitments

- Test order fixed: T1, T2, T3, T4 evaluated independently.
- Eligibility threshold (n_triplets ≥ 50) locked before computing.
- Significance thresholds locked (z_T < 1.0 for T2; z_T > 2 for T4).
- Class generalization set fixed: {dar, saiin}. Cannot expand the set after seeing results.
- Content reference set fixed: {chedy, qokedy, qokeedy, qokeey, shedy}. Cannot substitute after seeing results.
- If T4 fails, T1-T3 results are reported but constraint registration is suspended pending methodology revision.

## Constraint registration plan

Outcomes register at most 2 constraints (not 4 — this is a single-axis test):

**C2000:** Mutual information through daiin in Currier B
- Tier 2 (structural fact)
- Outcome: PASS / FAIL of T1 + T2 combined verdict

**C2001:** Class-level state-flush among high-frequency function tokens (conditional on T3)
- Registered only if T3 produces clean PASS or clean FAIL
- Tier 2 (structural fact about class generalization)
- If T3 partial-pass, C2001 not registered — results reported as exploratory

If T4 fails (methodology underpowered), nothing registers. Phase status would be "methodology limit reached, no findings."

## Computational plan

Single script s1_mi_per_token.py:
1. Load Currier B tokens (H-track, no labels, no asterisks)
2. Build triplet index: for each middle token T, list of (prev, next) pairs
3. Filter to T with n_triplets ≥ 50
4. For each eligible T:
   - Compute I_actual
   - Generate 200 shuffles, compute I_null distribution
   - Compute z_T
5. Rank tokens by z_T
6. Adjudicate T1-T4
7. Output: per-token MI/z, ranked list, top-10 lowest, top-10 highest, verdicts

Expected runtime: ≤10 minutes (MI computation is cheap; ~500 tokens × 200 shuffles × small triplet sets).

## Relationship to existing constraints

- **C557** (daiin line-initial ENERGY trigger) — current interpretation: daiin signals a state. Test could complement: daiin both signals AND flushes context.
- **C800** (Body HT escape driver) — daiin appears at escape boundaries. Consistent with state-flush interpretation.
- **C843** (paragraph prefix markers) — daiin at paragraph starts. State-flush would explain "fresh frame" at paragraph boundaries.
- **C1979** (da-prefix terminal-atom positional gradient) — daiin at mean position 0.413. State-flush at line/paragraph boundaries would predict early-line concentration.
- **C998** (RI/PP/INFRA classification) — if state-flush confirmed, INFRA is misnamed; these aren't infrastructure but state operators.
- **C1998** (Phase 686 directional negative) — directly motivates this phase.

## What this phase can and cannot establish

**Can establish:**
- Whether MI(prev; next | daiin) is above shuffle null (context-propagation magnitude)
- Whether daiin's MI is unusual relative to other tokens of similar frequency
- Whether dar and saiin share the same property

**Cannot establish:**
- Why daiin behaves this way (mechanism interpretation)
- Whether daiin's behavior matches "state-flush" semantically — the term is interpretive
- Whether the finding generalizes to all DA-family tokens (only daiin/dar/saiin tested)

The phase is a measurement; "state-flush" is the hypothesis the measurement tests, not a finding the measurement establishes.

## Detailed results

### Target tokens

| Token | n_triplets | distinct_prev | distinct_next | MI_actual | MI_null | z | rank | %ile |
|-------|------------|---------------|---------------|-----------|---------|---|------|------|
| daiin | 314 | 232 | 203 | 6.585 | 6.581 | **+0.76** | 49/72 | 67 |
| dar | 188 | 139 | 135 | 6.185 | 6.179 | +0.91 | 53/72 | 72 |
| saiin | 99 | 82 | 76 | 5.684 | 5.688 | −0.41 | 21/72 | 28 |

Population: 72 tokens with n_triplets ≥ 50 in Currier B. Median z = −0.11. Range: [−1.31, +3.95].

### Most state-flush-like (lowest z, bottom 10)

| Token | z | n |
|-------|---|---|
| qokal | −1.31 | 167 |
| shey | −1.24 | 204 |
| al | −0.95 | 186 |
| ar | −0.94 | 248 |
| qoky | −0.92 | 111 |
| okaiin | −0.84 | 168 |
| otar | −0.79 | 114 |
| okar | −0.75 | 103 |
| okeey | −0.69 | 122 |
| okal | −0.69 | 95 |

### Most context-propagating (highest z, top 10)

| Token | z | n |
|-------|---|---|
| qotar | **+3.95** | 61 |
| chol | +3.17 | 99 |
| chcthy | +2.77 | 56 |
| qokedy | +2.51 | 271 |
| okedy | +2.39 | 114 |
| dy | +2.33 | 109 |
| qokar | +2.29 | 137 |
| s | +2.24 | 53 |
| shedy | +2.07 | 416 |
| okain | +1.97 | 135 |

### Content reference tokens (T4 sanity check)

| Token | z |
|-------|---|
| chedy | +0.71 |
| qokedy | **+2.51** [*] |
| qokeedy | +1.10 |
| qokeey | +0.52 |
| shedy | **+2.07** [*] |

T4 PASS: methodology detects context propagation in qokedy and shedy.

## Auxiliary observations (NOT registered as constraints — observation only)

The strongest finding from the broader ranking, not pre-registered:

**qokedy ranks 4th among 72 eligible tokens for context propagation** (z=+2.51). The famous f75r ×4 balneum mariae signature is *operationally embedded* — what comes before predicts what comes after. This is consistent with our existing reading (C1300, C1394, the qokedy counting shorthand from the f75r↔Ch.19 match) but not a pre-registered prediction.

**The state-flush vs context-propagation axis tracks token complexity, not function class:**
- Long compound operational tokens (qotar, chol, chcthy, qokedy, qokar) are top context-propagators
- Short suffix-like or bare-stem tokens (qokal, shey, al, ar, qoky) are most state-flush-like
- Function-class tokens (daiin, dar, saiin) are not coherent on this axis

These observations are noted in the phase narrative but not registered as constraints — the phase pre-registered specific predictions about daiin/dar/saiin, not about token-complexity correlates of MI. Registering these as findings would be HARK.

## Constraint Registered

### C2000 (Tier 2, Scope: B): daiin state-flush hypothesis REJECTED

Pre-registered Phase 687 hypothesis (Tier 4 reframe from Phase 686 crazy-expert speculation): daiin functions as state-flush / context-reset operator; predicts MI(prev; next | T=daiin) below population median (T1) AND below significance threshold z<+1.0 (T2).

**Result:** T1 FAILS (daiin z=+0.76 at 67th percentile, ABOVE median = −0.11). T2 PASSES (daiin z < +1.0 — MI not significantly above shuffle null). T3 PARTIAL (dar z=+0.91 above median, saiin z=−0.41 below median; no class-level pattern). T4 PASSES (qokedy z=+2.51, shedy z=+2.07 confirm methodology can detect context propagation).

**Falsification verdict:** State-flush hypothesis REJECTED for daiin. daiin is moderate-context-propagation, not unusually low MI. The high marginal H_succ documented in C1998 (7.30 bits) reflects daiin's diverse predecessor and successor pool but does NOT mean context fails to propagate through it. Equivalently: context doesn't pass through in a structured way (T2 pass — z<1.0) but it doesn't get specifically flushed either (T1 fail — daiin above median).

Both the original "infrastructure glue" framing (C998-class taxonomy) AND the proposed "state-flush operator" reframe (Phase 686 Tier 4 speculation) fail to predict daiin's transition behavior at MI resolution. daiin is a high-throughput junction with diverse contexts that don't strongly relate to each other through it.

T3 PARTIAL means class-level state-flush hypothesis NOT registered (per Phase 687 pre-reg "if T3 partial-pass, C2001 not registered — results reported as exploratory"). dar, saiin individual results documented in narrative but not constrained.

**Tier:** 2 (Currier B structural fact, falsification of pre-registered hypothesis)

**Scope:** B

**Connections:**
- C557 (daiin line-initial ENERGY trigger) — unaffected; daiin still triggers operationally, just doesn't flush context at MI resolution
- C998 (RI/PP/INFRA classification) — INFRA classification stands at structural level despite naming being partially misleading (C1998 + C2000)
- C800 (HT escape driver), C843 (paragraph prefix markers) — unaffected; daiin's role at boundaries is positional, not context-disrupting
- C1979 (da-prefix terminal-atom positional gradient) — unaffected
- C1998 (Phase 686 directional negative on RI vs INFRA H_succ) — directly motivates this phase
- Phase 687 closes the speculative reframe documented in Phase 686 INDEX.md (crazy-expert section)

**Methodological discipline preserved:** Pre-registered prediction failed in registered direction; result registered as falsification per project standard. No revision to "low z but not unusually low" or any softer form. Auxiliary findings (qokedy as top-MI token, complexity correlates) noted as observations only, not registered.

## Scripts

- `s1_mi_per_token.py` — MI(prev; next | T) per token, 200 shuffle null per token, ranking + adjudication

## What this phase establishes

1. **The state-flush reframe of daiin is wrong.** Specific testable prediction failed in registered direction.
2. **Both "infrastructure glue" and "state-flush operator" framings of daiin/dar/saiin are inadequate.** Their MI behavior is not coherent as a class.
3. **Methodology can detect context propagation when present** (qokedy, shedy at z>+2). Negative results on daiin are signal-detection, not methodology limit.
4. **Token complexity tracks MI propagation more cleanly than function class.** Long compounds propagate; short stems don't. This is observation, not constraint.

## What this phase does not establish

- *Why* daiin has high marginal H_succ — measurement, not mechanism
- Whether daiin has any other distinguishing structural property at finer resolution
- Whether the qokedy / qotar / chol context-propagation pattern means anything beyond morphological complexity
- What replaces "infrastructure" as the right name for daiin's class — both candidates failed

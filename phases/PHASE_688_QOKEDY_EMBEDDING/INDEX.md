# Phase 688: qokedy Context Propagation Decomposition

**Status:** COMPLETE — 1 constraint registered (C2001); operational embedding CONFIRMED. **See Phase 689 (C2002):** the "morphological clusterer" framing of qotar/chol in this phase's auxiliary T4 narrative was empirically refuted at same-stem density level. Cross-tier z=−0.20 measurement stands; the mechanism inference was over-stepping.
**Started:** 2026-05-07
**Completed:** 2026-05-07
**Goal:** Test whether qokedy's high MI propagation (Phase 687, z=+2.51, 4th-highest of 72 eligible tokens) reflects **operational embedding** (qokedy is structurally embedded in recipe sequences with predictive prev→next pairs) versus **morphological clustering** (MI is dominated by adjacent qo-prefix tokens like qokeedy/qokeey appearing near qokedy).

## Result summary

**T1 PASS — qokedy operational embedding CONFIRMED.** Cross-tier z=+2.49 (n=140), HIGHER than cluster tier z=+1.34 (n=19, insufficient) or boundary z=+1.26 (n=112). When (prev, next) pairs are restricted to those where neither is qo-prefix, qokedy's context propagation is actually strongest. Morphological clustering hypothesis fails — qokedy's MI is not driven by qo-family co-occurrence around it.

| Tier | n | MI bits | null | z | adjudicate |
|------|---|---------|------|---|------------|
| qo-cluster | 19 | 2.411 | 2.281 | +1.34 | INSUFFICIENT (n<30) |
| boundary | 112 | 4.674 | 4.641 | +1.26 | sufficient |
| cross | 140 | 5.292 | 5.249 | **+2.49** | **sufficient — T1 PASS** |

**Major auxiliary finding (T4 comparison, observation only):** Top context-propagators from Phase 687 split cleanly into operational embedders vs morphological clusterers when cross-tier decomposition is applied.

## Background

Phase 687 auxiliary observation (not registered, observation-only): qokedy ranks 4th-highest of 72 eligible tokens for context propagation (z=+2.51, n_triplets=271). Top-10 context-propagators were dominantly qo-prefix or operationally compound tokens: qotar (+3.95), chol (+3.17), chcthy (+2.77), qokedy (+2.51), okedy (+2.39), dy (+2.33), qokar (+2.29), s (+2.24), shedy (+2.07), okain (+1.97).

Two competing hypotheses for qokedy's high MI:

**Hypothesis 1 (operational embedding):** qokedy is embedded in recipe sequences. The token preceding qokedy carries information about what follows because of recipe-internal structure (preparation step → thermal cycle → next operation). MI persists across cross-PREFIX pairs (prev and next from operationally distinct token classes).

**Hypothesis 2 (morphological clustering):** qokedy's high MI reflects qo-prefix family clustering (qokeedy → qokedy → qokeey patterns; same-stem runs documented in C1995 / Phase 685 for Section S). If true, restricting to pairs where neither prev nor next is qo-prefix should collapse the MI to shuffle null.

These are mechanistically distinct and the existing data can decisively choose between them via tier decomposition (mirrors Phase 685's three-tier methodology for C1995).

## Definitions (locked)

For each (prev, qokedy, next) triplet in the H-track Currier B corpus:

**Tier classification by (prev, next) pair:**
- **Tier QO-cluster:** prev has qo-prefix AND next has qo-prefix
- **Tier boundary:** exactly one of {prev, next} has qo-prefix
- **Tier cross:** neither prev nor next has qo-prefix (operationally distinct from qokedy's qo-channel)

**qo-prefix definition:** token starts with literal "qo" character sequence (covers qokedy, qokeedy, qokeey, qokar, qotar, qoteedy, etc.). This is the empirical definition matching our morphology library.

**Per-tier MI:**
- Restrict triplets to those whose (prev, next) pair satisfies the tier definition
- Compute MI(prev; next) on the restricted set
- Generate 200 shuffles where prev is shuffled within the restricted set
- z_tier = (MI_actual − mean(MI_null)) / std(MI_null)

## Locked methodology

| ID | Spec |
|----|------|
| M1 | Currier B tokens only, H-track, no labels, no asterisks |
| M2 | Triplets: (prev, qokedy, next) where qokedy is at position t, prev at t−1, next at t+1, all in same Currier B span |
| M3 | qo-prefix membership: token starts with literal "qo" |
| M4 | MI = plug-in estimator −Σ p(x,y) log₂(p(x,y) / (p(x)p(y))) |
| M5 | Per-tier null: 200 shuffles of prev within the tier-restricted set |
| M6 | RNG seed = 42, with token+tier salting |
| M7 | Minimum tier sample for statistical inference: n_tier ≥ 30 (smaller samples noted but not adjudicated) |
| M8 | Top-10 context-propagators from Phase 687 included as comparison set |

## Pre-registered tests

### T1 (Primary, operational embedding) — qokedy cross-tier MI persists

**Hypothesis:** qokedy's MI z when restricted to cross-tier pairs (neither prev nor next is qo-prefix) is > +1.0.

**Pass:** z_cross > +1.0. Operational embedding hypothesis SUPPORTED — qokedy's MI persists across operationally distinct token classes; recipe-structural prediction.

**Fail:** z_cross ≤ +1.0. Morphological clustering hypothesis SUPPORTED — qokedy's MI is primarily qo-cluster co-occurrence; collapses when cross-tier restriction applied.

**Constraint registered:** C2001 (PASS or FAIL outcome, registered regardless).

### T2 (Diagnostic) — morphological clustering present but not exclusive

**Hypothesis:** qokedy's qo-cluster tier z > qokedy's cross tier z by ≥ 1.0 standard units.

**Rationale:** If morphological clustering exists (which we expect given C1995 / Phase 685 same-stem run findings), qo-cluster z should exceed cross z. This is a diagnostic check, not load-bearing for T1.

**Pass:** qo-cluster z − cross z > 1.0. Both mechanisms present.

**Fail:** Difference ≤ 1.0. Either morphological clustering absent or both tiers similarly low.

**No constraint registered for T2** — diagnostic only.

### T3 (Sample-size sanity) — minimum sample requirement

If any tier has n_tier < 30, the corresponding z is reported but not adjudicated. T1 verdict requires cross-tier n ≥ 30. If cross-tier sample is too small, T1 returns INSUFFICIENT_DATA and no constraint registers.

### T4 (Comparison) — context for qokedy's behavior

For each of the other top-9 context-propagators from Phase 687 (qotar, chol, chcthy, okedy, dy, qokar, s, shedy, okain), compute their cross-tier z (restricting to pairs where neither prev nor next has the same prefix as the token under analysis).

**Reported descriptively, not registered.** This contextualizes whether qokedy is unusual or representative.

## Anti-HARK commitments

- Tier definitions locked: qo-prefix = literal "qo" start. Cannot redefine after seeing data.
- Threshold locked: T1 passes if z_cross > +1.0. Cannot soften to "z > 0" or "z > 0.5" if T1 fails.
- T2 is diagnostic only; T2 results cannot drive T1 reinterpretation.
- T4 comparison set fixed: top-9 from Phase 687 ranking. Cannot substitute or expand.
- Sample-size threshold locked: n_tier ≥ 30 required for adjudication.

## Constraint registration plan

**C2001:** qokedy operational embedding test (T1 outcome)
- Tier 2 if PASS — structural fact: qokedy's MI persists across cross-PREFIX pairs
- Tier 2 if FAIL — falsification: qokedy's MI is dominated by morphological clustering
- Tier "INSUFFICIENT" if cross-tier sample < 30 — phase status: methodology limit reached
- Either positive outcome registers; only insufficient sample suspends registration

T2 (diagnostic) and T4 (comparison) findings reported in phase narrative, not registered as constraints.

## Computational plan

Single script s1_tier_decomposition.py:
1. Load Currier B tokens (H-track, no labels, no asterisks)
2. Find all (prev, qokedy, next) triplets
3. Classify each triplet by tier (qo-cluster / boundary / cross)
4. Per tier with n ≥ 30:
   - Compute MI_actual
   - Compute null distribution over 200 shuffles
   - Compute z
5. T4: repeat per-token tier decomposition for top-9 from Phase 687 (defining same-prefix membership per target token)
6. Adjudicate T1, report T2-T4

Expected runtime: < 5 minutes (single token's triplets, three tiers, 200 shuffles each; T4 expands to ~10 tokens).

## Relationship to existing constraints

- **C1300** (qo as 100% k-HEAD thermal channel) — qokedy is qo+k+e+e+d+y, full thermal-channel specification
- **C1394** (HEAD+MOD*+TERM atom model) — qokedy's atoms: k-HEAD heat + e-MOD cool + e-MOD cool + d-MOD do/mark + y-TERM end
- **C1995** (S=operational compactness, B=operational alternation; three-tier decomposition) — methodology import; same statistical framework
- **C1965, C1988** (matched recipe cardinality anchors) — qokedy ×4 on f75r is a documented operational embedding
- **C1971** (matched recipes catalog) — f75r↔Pseudo-Lull III.19 is the canonical qokedy embedding case
- **C2000** (Phase 687) — daiin's failure to show operational embedding at MI level; this phase tests whether qokedy succeeds where daiin failed
- **PT-013** (qokedy = "maintain fire level" operational specification) — qokedy's known operational role

## What this phase can and cannot establish

**Can establish:**
- Whether qokedy's MI propagation persists across operationally distinct token contexts
- Whether morphological clustering and operational embedding coexist or one dominates
- Whether qokedy is anomalous among top context-propagators or representative

**Cannot establish:**
- Specific recipe-structural mechanism (would require source-corpus alignment)
- Whether the operational embedding (if confirmed) reflects production-side structure or reading-side enumeration
- Whether the result generalizes to other qo-prefix operational tokens beyond qokedy

## Detailed results

### Phase 687 top-9 context propagators — cross-tier decomposition (T4 comparison)

Each token's "cross tier" is defined relative to its own first-2-char prefix.

| Token | Phase 687 overall z | Cross-tier n | Cross-tier z | Verdict |
|-------|--------------------:|-------------:|-------------:|---------|
| **chcthy** | +2.77 | 45 | **+3.78** | Strongest operational embedding |
| **qokedy** | +2.51 | 140 | **+2.49** | Strong operational embedding (this phase's primary) |
| okain | +1.97 | 117 | +2.26 | Strong operational embedding |
| s | +2.24 | 46 | +2.24 | Strong operational embedding |
| dy | +2.33 | 102 | +1.78 | Moderate embedding |
| qokar | +2.29 | 103 | +1.73 | Moderate embedding |
| shedy | +2.07 | 366 | +1.69 | Moderate embedding |
| okedy | +2.39 | 85 | +1.29 | Moderate embedding |
| **qotar** | **+3.95** | 48 | **−0.20** | **Morphological clustering** |
| **chol** | +3.17 | 68 | **−0.23** | **Morphological clustering** |

**The biggest surprise:** qotar (Phase 687's #1 context propagator at z=+3.95) and chol (#2 at z=+3.17) are **primarily morphological clustering**. Their cross-tier MI collapses to zero or below. Their high overall MI is driven by qo+qo or ch+ch co-occurrence around them, not by structural embedding.

By contrast, **chcthy** (only Phase 687 #3 at z=+2.77) is the *strongest* operational embedder at z=+3.78 cross-tier. The Phase 687 ranking does NOT predict operational embedding strength — only this decomposition does.

### State-flush tokens (diagnostic) — cross-tier z

Bottom-of-Phase-687 tokens remain state-flush at cross-tier (predecessor doesn't predict successor through them, even when restricted):

| Token | Cross-tier n | Cross-tier z |
|-------|-------------:|-------------:|
| qokal | 120 | −1.01 |
| shey | 184 | −1.22 |
| al | 178 | −0.95 |
| ar | 222 | −1.37 |
| qoky | 81 | −0.65 |

State-flush behavior is robust to tier decomposition.

## Constraint Registered

### C2001 (Tier 2, Scope: B): qokedy operational embedding CONFIRMED via cross-PREFIX MI persistence

Pre-registered Phase 688 hypothesis: qokedy's MI z, when restricted to (prev, next) pairs where neither has qo-prefix, > +1.0 (operational embedding); otherwise z would collapse (morphological clustering hypothesis).

**Result:** T1 PASSES at z_cross = +2.49 (n=140 cross-tier triplets). Cross-tier z is HIGHER than qo-cluster tier (z=+1.34, n=19 insufficient) and boundary tier (z=+1.26, n=112). qokedy's context propagation persists — and is actually strongest — when prev and next are operationally distinct from qokedy's qo-channel.

**Operational embedding interpretation:** qokedy is structurally embedded in recipe sequences. The token preceding qokedy carries information about what follows, not via qo-family co-occurrence (which would collapse at cross-tier) but via genuine sequential structure. Consistent with C1300 (qo as 100% k-HEAD thermal channel), C1394 (HEAD+MOD*+TERM atom model), C1965/C1988 (matched recipe cardinality anchors), PT-013 (qokedy = "maintain fire level" operational specification), and the f75r ×4 qokedy run as documented operational embedding.

**T2 (diagnostic):** INSUFFICIENT — qo-cluster tier has only n=19 triplets (<30 threshold). Point-estimate direction is opposite to morphological-dominance hypothesis (cluster z=+1.34 < cross z=+2.49). Even with more cluster sample, T2's "z_cluster − z_cross > +1.0" prediction would be expected to fail.

**T4 (auxiliary, NOT registered):** Top-9 Phase-687 context propagators decompose into distinct mechanism categories at cross-tier:
- Strong operational embedders: chcthy (+3.78), qokedy (+2.49), okain (+2.26), s (+2.24)
- Moderate: dy, qokar, shedy, okedy (z 1.3-1.8)
- Morphological clusterers (collapse cross-tier): qotar (−0.20), chol (−0.23)

**Critical insight:** Phase 687's overall z-ranking does NOT predict operational embedding strength. qotar (rank 1 at +3.95) is morphological clustering; chcthy (rank 3 at +2.77) is strongest operational embedder. Only the cross-tier decomposition distinguishes the mechanisms.

This decomposition is registered as observation in narrative but NOT as a constraint — it was not pre-registered and registering would be HARK. Future phases could pre-register and test the operational-embedder vs morphological-clusterer dichotomy explicitly.

**Tier:** 2 (Currier B structural fact)

**Scope:** B

**Connections:**
- C1300 (qo as 100% k-HEAD thermal channel) — qokedy is full thermal-channel operational specification; embedding result confirms it functions as a structured operation
- C1394 (HEAD+MOD*+TERM atom model) — qokedy = qo+k(HEAD,heat) + e(MOD,cool) + e(MOD,cool) + d(MOD,mark) + y(TERM,end)
- C1965 / C1988 (matched recipe cardinality anchors) — operational embedding measured here matches the cardinality-encoding observations on f75r and f103r
- C1971 (matched recipes catalog) — f75r↔Pseudo-Lull III.19 is the canonical qokedy embedding case
- C1995 (S=operational compactness, B=operational alternation) — methodology import; same three-tier decomposition pattern
- C1998, C2000 (Phase 686/687 daiin findings) — daiin failed cross-tier embedding test (z=+0.76 overall, T2 just barely passes); qokedy succeeds (z=+2.49 cross-tier). Establishes cross-tier MI z as a discriminator between operationally embedded and non-embedded tokens
- PT-013 (qokedy = "maintain fire level") — qokedy's known operational role validated structurally

## Methodological notes

- T1 result is robust: n=140 cross-tier sample is well above the n=30 sufficiency threshold; z=+2.49 is well above +1.0 threshold; effect direction matches operational embedding hypothesis.
- T2 INSUFFICIENT but informative: cluster tier n=19 means we cannot adjudicate, but point estimates strongly suggest morphological clustering is NOT dominant for qokedy. This is reported but not registered.
- T4 reveals heterogeneity that was invisible at the Phase 687 ranking level. The operational-vs-morphological mechanism split is a candidate for follow-up phase. NOT registered here.
- Pre-reg discipline preserved: only T1 outcome registers (C2001 PASS). T2/T4 are diagnostic/auxiliary per pre-reg.

## Scripts

- `s1_tier_decomposition.py` — three-tier decomposition for qokedy + comparison tokens

## What this phase establishes

1. **qokedy is operationally embedded.** Cross-tier z=+2.49 confirms predecessor predicts successor through qokedy beyond what qo-family co-occurrence explains.
2. **Phase 687 ranking does NOT equal operational embedding strength.** qotar (rank 1) and chol (rank 2) are morphological clusterers; chcthy (rank 3) and qokedy (rank 4) are operational embedders.
3. **Cross-tier MI decomposition discriminates two distinct mechanisms.** Same statistical methodology as Phase 685 (C1995); now extended to MI propagation.
4. **State-flush behavior is robust to tier decomposition.** qokal, shey, al, ar all remain negative cross-tier — they don't propagate context regardless of slicing.

## What this phase does not establish

- *Why* qokedy is operationally embedded — measurement, not mechanism
- Whether the operational embedding reflects recipe-internal sequence (production) or reader's enumeration order (consumption)
- Whether other qo-prefix operational tokens (qokeedy, qokeey) share qokedy's embedding profile
- Whether qotar and chol's morphological clustering is *production-side* (scribe writing similar tokens together) or *content-side* (recipe with repeated qo-prefix instructions)

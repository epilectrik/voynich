# Phase 559: Compositional Supervisory State Induction

**Date:** 2026-03-08
**Folio:** f43v
**Phase verdict:** FAIL

---

## 1. Objective

Test whether compositional pairwise features (PREFIX x HEAD, TERM x SUFFIX_HEAD,
HEAD x TERM frame hazard, HEAD x MOD, zone context, cross-token routing, and
meta-features) can induce supervisory states on a single folio (f43v) that are
more structured than baselines and null models. This is the corrected successor
to Phase 558 (SINGLE_FOLIO_EXECUTION_COHERENCE), which failed due to hand-authored
evidence vectors.

## 2. Method

### Evidence Construction

Seven weighted channels derive evidence from corpus-wide enrichment ratios:

| Channel | Weight | Key | Source |
|---------|--------|-----|--------|
| w1_prefix_head | 0.3 | pairwise key | B-corpus enrichment |
| w2_term_suffix | 0.15 | pairwise key | B-corpus enrichment |
| w3_frame_hazard | 0.25 | pairwise key | B-corpus enrichment |
| w4_head_mod | 0.1 | pairwise key | B-corpus enrichment |
| w5_zone | 0.1 | pairwise key | B-corpus enrichment |
| w6_routing | 0.05 | pairwise key | B-corpus enrichment |
| w7_meta | 0.05 | pairwise key | B-corpus enrichment |

For each channel, the corpus-wide count of tokens matching each pairwise key
is computed. Per-category enrichment ratios (vs corpus baseline) are converted
to log2 evidence, mapped from 8 operational categories to 6 supervisory states,
and softmax-normalized.

### State Ontology

| State | Category sources |
|-------|-----------------|
| TWORK | THERMAL |
| TRANS | FLOW |
| CLOSE | CONTAINMENT |
| SPEC | STAGING |
| TWORK | OPERATION |
| TRANS | TRANSITION |
| CHK | MARKING |
| OBS | MONITORING |

### Partitions Tested

- **Partition A:** 6-state hypothesis (SPEC, TWORK, OBS, CHK, TRANS, CLOSE)
- **Partition B:** 4-state coarse (SPECIFY, OPERATE, TRANSITION, CLOSURE)
- **Partition C:** Unsupervised k-means on one-hot feature matrix with PCA

### Baselines

- **HEAD-only:** State assignment using only the HEAD atom channel
- **Zone-only:** State assignment using only the line-zone channel

### Null Models (5 types x 50 seeds each)

| Null type | Description |
|-----------|-------------|
| token_shuffle | Shuffle tokens within each line |
| line_shuffle | Shuffle lines within each paragraph |
| cross_paragraph | Shuffle lines across all paragraphs |
| random_token | Replace each token with random B-corpus token |
| head_matched | Replace each token with HEAD-matched random token |

## 3. Results

### 3.1 State Profile (6-state)

| State | Fraction |
|-------|----------|
| SPEC | 0.255 |
| TWORK | 0.327 |
| OBS | 0.111 |
| CHK | 0.039 |
| TRANS | 0.170 |
| CLOSE | 0.098 |

**Entropy:** 2.3284 bits
**Zone alignment:** 0.4379

### 3.2 Baseline Comparison

| Model | Entropy |
|-------|---------|
| Full 7-channel | 2.3284 |
| HEAD-only | 1.4898 |
| Zone-only | 1.4512 |

**Gain vs HEAD-only:** -56.3%
**Gain vs Zone-only:** -60.4%

The full model produces **higher** entropy than both baselines,
indicating that the additional channels disperse rather than
concentrate state assignments. HEAD atom alone is more informative.

### 3.3 Null Model Comparisons

| Null type | Real-Null JSD | Null-Null JSD | p-value |
|-----------|--------------|--------------|---------|
| token_shuffle | 0.000053 | 0.000081 | 0.3927 |
| line_shuffle | 0.000000 | 0.000000 | 1.0000 |
| cross_paragraph | 0.000000 | 0.000000 | 1.0000 |
| random_token | 0.019040 | 0.011290 | 0.1290 |
| head_matched | 0.010102 | 0.007289 | 0.2359 |

**Interpretation:** The real folio's state profile is indistinguishable
from all five null types. Token shuffle and structural shuffles produce
JSD values near zero, meaning the state assignments are entirely
token-local with no sequential or positional structure contributing.

### 3.4 Head-Matched Separation

- Effect size: 0.506 (threshold: 1.5)
- Real vs head-matched JSD: 0.010102

The full model barely distinguishes real f43v from HEAD-matched
random tokens. The compositional features beyond HEAD add negligible
discriminative power.

### 3.5 Paragraph Differentiation

Significant metrics (p<0.05): 0/5

| Metric | p-value |
|--------|---------|
| state_distribution_jsd | 1.0000 |
| transition_matrix_distance | 1.0000 |
| zone_conditioned_jsd | 1.0000 |
| closure_incidence | 1.0000 |
| state_entropy | 1.0000 |

All paragraph differentiation p-values are 1.0, indicating the
3 paragraphs of f43v are categorically undifferentiated under the
induced states.

### 3.6 Partition Comparison

- 6-state mean separation JSD: 0.005839
- Unsupervised silhouette: 0.2053 (null mean: 0.2125)
- Unsupervised beats 6-state: False
- 4-state entropy: 1.7388
- 6-state entropy: 2.3284

The unsupervised partition does NOT beat the 6-state partition (FC6
not triggered), but this is cold comfort since neither partition
demonstrates meaningful structure.

### 3.7 Failure Conditions

| Condition | Triggered | Detail |
|-----------|-----------|--------|
| FC1 | no | NaN/inf in >1% tokens |
| FC2 | no | No state > 20% |
| FC3 | no | head_matched JSD < 0.01 |
| FC4 | YES | Full entropy >= HEAD-only entropy |
| FC5 | no | All paragraphs > 60% same state |
| FC6 | no | Unsupervised > 6-state |

**FC4 triggered:** Full model entropy (2.328) exceeds HEAD-only (1.490).
The compositional evidence accumulation adds noise, not signal.

## 4. Stage 1 Criteria Summary

| Criterion | Result | Detail |
|-----------|--------|--------|
| S1: State Profile Distinctiveness | FAIL | threshold: perm p < 0.01 for >= 2 of 5 null types |
| S2: Line-Zone Alignment | FAIL | threshold: alignment > 0.35 AND > null_mean + 2*sigma |
| S3: Paragraph Differentiation | FAIL | threshold: >= 2 of 5 metrics significant at p<0.05 |
| S4: Compositional Gain | FAIL | threshold: full model entropy lower than BOTH baselines by >10% |
| S5: Head-Matched Separation | FAIL | threshold: effect size > 1.5 |
| S6: Partition Comparison | diagnostic | 6-state mean sep JSD = 0.005839 |

**Stage 1 verdict:** FAIL (failure conditions: FC4)

## 5. Stage 2: Plant Coupling

**Status:** STAGE_1_FAILED

Stage 1 failure blocks Stage 2. No plant coupling was performed.

## 6. Phase Verdict: FAIL

## 7. Interpretation

### Why the compositional approach failed

The core problem is that the 7-channel evidence accumulation produces a
MORE uncertain (higher entropy) state assignment than using HEAD atom alone.
This is the opposite of what would occur if the additional channels carried
complementary information.

**Diagnosis:** The 8-to-6 category mapping with softmax normalization
spreads probability mass across states. When multiple channels contribute
different evidence, they average out rather than reinforcing each other.
HEAD atom alone is a strong enough signal (C1475: HEAD atoms define
categorically distinct operational domains, V=0.511) that diluting it with
weaker signals degrades the assignment.

### What the baselines tell us

HEAD-only entropy (1.490) is 36% lower than the full model (2.328).
Zone-only entropy (1.451) is similar to HEAD-only. Both baselines produce
sharper, more concentrated state assignments than the 7-channel model.
This means the simplest possible atom-level feature already carries most
of the category information, consistent with C1475 (HEAD is the primary
domain selector).

### What the null models tell us

Token shuffle JSD near zero means that reordering tokens within lines
does not change the state profile. This confirms that the induced states
are entirely determined by token identity, not by position or sequence.
This is expected given C1003 (pairwise compositionality) and C1429
(cross-line category independence) -- there should be no sequential
structure to detect.

### Structural implications

This result is consistent with the existing constraint system:

- C1003: No three-way morphological synergy. Pairwise channels should
  suffice, but weighted averaging of many pairwise signals can degrade.
- C1475: HEAD atom is the PRIMARY domain selector. Adding secondary
  signals dilutes rather than sharpens the assignment.
- C1431-C1433: PREFIX explains 94.4% of theoretical AXM max variance.
  The compositional details beyond PREFIX+HEAD are near-deterministic,
  leaving little room for a supervisory layer to add.
- C1429: Cross-line category independence. Lines are i.i.d. samples
  from folio profile, so line-level state induction cannot find
  sequential structure that does not exist.

### What would need to change

A supervisory state model would need to either:
1. Operate at FOLIO level (comparing folios, not tokens within a folio)
2. Use a non-weighted-average combination rule (e.g., max, argmax)
3. Accept that HEAD alone is sufficient and build on it directly
4. Find a different decomposition that does not dilute HEAD's signal

## 8. Non-Circularity Audit

| Component | Voynich Input | Verdict |
|-----------|---------------|---------|
| Evidence tables | Corpus-wide enrichment ratios | INDIRECT (no f43v-specific tuning) |
| Channel weights | Proportional to measured MI | INDIRECT |
| 6-state ontology | Model hypothesis | TESTED against alternatives |
| Token decomposition | BFolioDecoder on f43v | DIRECT (unavoidable) |
| Null baselines | Random permutation/sampling | NONE |
| Thresholds | Pre-registered in plan | NONE |

No circularity detected. The failure is genuine.

## 9. Relationship to Phase 558

Phase 558 failed due to hand-authored evidence vectors that were
insufficiently grounded. Phase 559 corrected this by deriving all
evidence from corpus-wide enrichment ratios. Despite this improvement,
the fundamental problem remains: the token-level compositional features
do not produce supervisory states more informative than the HEAD atom
alone. Phase 558's failure was methodological; Phase 559's failure is
substantive -- the signal is not there at this level of analysis.

---

**Constraint implications:** No new constraints proposed. The negative
result is consistent with existing Tier 2 constraints (C1003, C1475,
C1429, C1431-C1433). The result strengthens the interpretation that
HEAD atom is the primary (and near-sufficient) domain selector, and
that within-folio token-level state induction cannot improve upon it.

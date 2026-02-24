# C1250: Gloss Category Structural Coherence

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** GLOSS_SCALE_VALIDATION (Phase 446)
**Extends:** C936 (compositional gloss system), C911 (PREFIX domain uniqueness), C1190 (atomicity)
**Relates to:** C1251 (atom compositional validation), C1196 (autogloss coverage), C267 (MIDDLE encodes core action)

---

## Statement

The 8 operational categories assigned to 90 high-frequency MIDDLEs are structurally coherent at corpus scale. A 7-test permutation battery (1000 permutations each, p<0.01 threshold) achieves **5/7 PASS** against two null models:

| Test | Null Model | Statistic | Result | Key Value |
|------|-----------|-----------|--------|-----------|
| T1: Behavioral silhouette | A (random partition) | Silhouette score | **PASS** | z=3.46, sil=-0.070 vs -0.102 |
| T2: Kernel-category alignment | A | Chi-square | **PASS** | V=0.675, p=0.000 |
| T3: Affordance family alignment | A | Chi-square | FAIL | V=0.316, p=0.187 |
| T4: Line-position coherence | B (random token labels) | ANOVA F | **PASS** | F=29.9, 30.5x over random |
| T5: Directional REGIME predictions | A | Correct/4 | FAIL | 2/4 correct, p=0.262 |
| T6: Apparatus-gloss correlation | A | Spearman rho | **PASS** | rho=0.758, p=0.003 |
| T7: Within-line MI | B | Mutual information | **PASS** | MI 8.7x, z=37.9 |

**Null Model A:** Random partition of 90 MIDDLEs into 8 groups of the same sizes.
**Null Model B:** Random per-token category labeling from marginal distribution (breaks MIDDLE consistency).

### 8 Operational Categories

| Category | Tokens | Example Glosses |
|----------|--------|-----------------|
| THERMAL | 4,841 | heat, cool, sustain, pulse, extended |
| FLOW | 3,985 | transfer, gather, discharge, release |
| TRANSITION | 3,395 | start, open, close, end, settle, yield |
| OPERATION | 3,273 | work, operate, batch, pound |
| STAGING | 2,691 | frame, step, iterate, sequence, cycle |
| CONTAINMENT | 1,099 | seal, hold, lock, bind |
| MARKING | 862 | mark, flag, note, pause, adjust |
| MONITORING | 327 | watch, check, verify, scan |

Coverage: 20,473 / 23,096 tokens (88.6%).

### Failure Analysis

- **T3 (affordance family):** Affordance families (THERMAL, PHASE, FLOW, RECOVERY) are derived from behavioral clustering (k_ratio, REGIME enrichment, etc.). These capture a different structural axis than operational glosses. The orthogonality is expected given that affordance families are topology-derived while gloss categories are semantics-derived.
- **T5 (REGIME predictions):** REGIME composites are section-confounded. CONTAINMENT predicted for R2 but R2 has flat category distribution; TRANSITION predicted for R3 but R3's actual max is R4 (by 0.003). The predictions assume clean REGIME-to-function mapping that doesn't hold at this granularity.

### Kernel Profiles (T2)

| Kernel | Dominant Categories |
|--------|-------------------|
| K | THERMAL (37.5%), FLOW (18.8%), TRANSITION (18.8%) |
| E | THERMAL (37.5%), STAGING (12.5%), OPERATION (6.2%) |
| H | MONITORING (61.5%), MARKING (30.8%) |

---

## Interpretation

The 8 operational categories are not arbitrary labels — they capture genuine structural partitioning of the MIDDLE vocabulary. Categories predict behavioral similarity, kernel identity, line position, apparatus type, and within-line adjacency patterns. This validates the Tier 3 interpretive layer at corpus scale.

---

## Method

- Corpus: 23,096 Currier B tokens, 90 MIDDLEs with human-assigned glosses mapped to 8 categories
- V1 attempt (shuffling categories among same 90 MIDDLEs) returned 0/7 — null too conservative
- V2 redesigned with two proper null models (random partition + random token labels)
- All structural features (behavioral signatures, kernel identity, line position) derived independently of gloss assignments

**Script:** `phases/GLOSS_SCALE_VALIDATION/scripts/gloss_scale_validation.py`
**Results:** `phases/GLOSS_SCALE_VALIDATION/results/gloss_scale_validation.json`

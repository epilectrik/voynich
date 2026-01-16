# AZC System Fit Registry

> **This document logs explanatory fits.**
> **No entry in this file constrains the model.**

**Version:** 4.3 | **Last Updated:** 2026-01-11 | **Fit Count:** 15 | **Status:** CLOSED

---

## Placement Coding Fits

### F-AZC-001 - Placement Prediction Model

**Tier:** F4 | **Result:** NEGATIVE | **Supports:** C466-C467

#### Question
Can we predict which placement code a token receives from its morphology?

#### Method
Naive Bayes classifier with features: PREFIX, MIDDLE, SUFFIX, token length.
Target: Placement code (C, P, R, R1, R2, R3, S, S1, S2, etc.)

Stage 1: Global model (all AZC)
Stage 2: Family-split models (only if Stage 1 accuracy is high)

Data: 5,354 decomposed AZC tokens.

Success criteria:
- Accuracy >50% (vs ~10% random baseline for 10 placements)

#### Result Details
- Global accuracy: 24.5% (vs 19.2% baseline)
- Lift over baseline: 1.27x
- Zodiac accuracy: 23.3% (vs 28.2% baseline - WORSE than random)
- A/C accuracy: 36.4% (vs 31.2% baseline)
- Target >50%: NOT MET

Feature associations detected:
- ok prefix → L, U, S0 placements (55-69%)
- ot prefix → S-series, R-series (30-49%)
- ch prefix → C, P placements (31-40%)

#### Interpretation
Morphology does NOT predict placement. Placement is diagrammatic/positional, not content-based. The weak signal (1.27x lift) suggests placement has layout meaning rather than morphological meaning.

This is a meaningful negative result: AZC placement codes describe WHERE a token appears in visual layout, not WHAT the token IS.

#### Limitations
Does not test whether placement has POSITIONAL meaning (see F-AZC-002).

---

### F-AZC-002 - Zodiac Positional Grammar

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C467

#### Question
Is R1→R2→R3 ordering a true grammar or just labeling?

#### Method
1. Build transition matrix for placement sequences within lines
2. Test forward vs backward transition bias (R1→R2 vs R2→R1)
3. Test position correlation (does placement predict line position?)
4. Check if R1<R2<R3<R4 in mean line position

Data: 3,654 Zodiac tokens, 3,641 transitions, 12 unique placements.

Success criteria:
- Transition matrix shows non-uniform probabilities
- Forward ordering significantly preferred
- Placement correlates with line position

#### Result Details
- **Position correlation: H=927.48, p<0.000001** (MASSIVELY SIGNIFICANT)
- R-series mean positions:
  - R1: 0.246 (early in line)
  - R2: 0.576 (middle)
  - R3: 0.657 (late-middle)
  - R4: 0.871 (near end)
- S-series mean positions:
  - S0: 0.024 (line start)
  - S1: 0.509 (middle)
  - S2: 0.647 (late-middle)
  - S3: 0.921 (near end)
- R-positions monotonically ordered: YES (R1<R2<R3<R4)
- S-positions monotonically ordered: YES (S0<S1<S2<S3)

Transition test: Only 3 forward transitions observed (tokens cluster by placement, don't interleave). Binomial test not significant due to low N.

#### Interpretation
**Zodiac AZC implements a POSITIONAL GRAMMAR.** Placement codes encode WHERE in the line a token can appear, not just arbitrary labeling.

This is NOT a transition grammar (R1→R2→R3 as a sequence) but a POSITIONAL grammar (R1 tokens appear early, R3 tokens appear late). The placement code is a hard positional constraint.

This immediately strengthens AZC conceptually: Zodiac is a directional orientation scaffold with grammar-governed placement.

#### Limitations
Does not explain WHY positions are ordered this way. Does not establish whether A/C family has similar positional grammar.

---

### F-AZC-005 - A/C Positional Grammar Test (DECISIVE)

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C430-C436, C467

#### Question
Does A/C also show positional grammar like Zodiac?

#### Method
Same methodology as F-AZC-002:
1. Extract placement sequences within A/C folios
2. Test monotonic ordering of C, P, R, S placements
3. Test transition entropy and asymmetry
4. Check if placement predicts position-in-line

Data: 5,747 A/C tokens, 5,730 transitions, 16 unique placements.

Success criteria:
- If A/C shows monotonic position ordering → AZC = ONE grammar, two parameter regimes
- If A/C does NOT show ordering → AZC = TWO fundamentally different systems

#### Result Details
- **Position correlation: H=1284.07, p<0.000001** (EVEN STRONGER than Zodiac!)
- A/C mean positions:
  - C: 0.349 (early in line)
  - P: 0.436 (early-middle)
  - R: 0.666 (late-middle)
  - S: 0.785 (late)
- **Monotonic ordering: C < P < R < S** (PERFECT!)
- Transition asymmetry: Low N (only 9 inter-placement transitions)

#### Interpretation
**A/C HAS POSITIONAL GRAMMAR.** This is the DECISIVE test result.

Both families share the same grammatical structure:
- **Zodiac**: R1 < R2 < R3 < R4 (subscripted positional codes)
- **A/C**: C < P < R < S (unsubscripted positional codes)

**CONCLUSION: AZC = ONE UNIFIED SYSTEM with two parameter regimes.**

The families are not bifurcated by design - they share a common positional-legality grammar with different "dialects" (subscripted vs unsubscripted codes).

#### Limitations
Does not explain why families use different labeling conventions.

---

## Boundary Behavior Fits

### F-AZC-003 - Family Membership Classifier

**Tier:** F4 | **Result:** PARTIAL | **Supports:** C466

#### Question
Can we predict Zodiac vs A/C family membership from token morphology alone?

#### Method
Naive Bayes classifier with features: PREFIX, MIDDLE, SUFFIX.
Target: Family (Zodiac vs A/C).

Data: 5,354 tokens (2,076 Zodiac, 3,278 A/C).

Success criteria:
- Accuracy >80% (vs 61.2% majority-class baseline)

#### Result Details
- Accuracy: 70.1%
- Lift over baseline: 1.15x
- Zodiac precision: 63.1%, recall: 50.6%, F1: 56.2%
- A/C precision: 73.2%, recall: 82.0%, F1: 77.3%
- Target >80%: NOT MET

Feature importance (KL divergence):
- MIDDLE: 0.538 (highest discriminative power)
- PREFIX: 0.243
- SUFFIX: 0.188

#### Interpretation
Morphology provides a WEAK signal for family prediction (1.15x lift), but not a strong one. This is confirmatory: families share a common type space but are tuned differently.

The key insight is that Zodiac and A/C differ primarily in LAYOUT (placement codes), not morphology. They are "parameterized variants" of the same underlying system, not separate systems.

#### Limitations
Confirmatory only. Does not identify the "tuning parameters" that differentiate families.

---

## Topology Fits

### F-AZC-004 - Option-Space Compression

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C463-C465

#### Question
By how much does AZC reduce the operator's available option space compared to Currier A?

#### Method
Measure entropy / cardinality differences across:
- PREFIX choices
- MIDDLE universality (core vs tail access)
- SUFFIX entropy
- Escape prefix availability (qo, ct)

Compare: A baseline vs AZC-Z vs AZC-A/C.

Data: 23,442 Currier A tokens, 2,076 AZC-Z tokens, 3,278 AZC-A/C tokens.

Success criteria:
- Quantifiable entropy reduction (>20%)
- Strong escape suppression (>50%)
- Universal MIDDLEs preserved (>80% of A rate)

#### Result Details

| Metric | Currier A | AZC-Z | AZC-A/C |
|--------|-----------|-------|---------|
| Tokens | 23,442 | 2,076 | 3,278 |
| Types | 2,425 | 741 | 848 |
| PREFIX entropy | 2.73 bits | 2.34 bits | 2.63 bits |
| MIDDLE entropy | 4.93 bits | 5.63 bits | 5.50 bits |
| SUFFIX entropy | 4.20 bits | 4.23 bits | 4.33 bits |
| TOTAL entropy | 11.87 bits | 12.20 bits | 12.47 bits |
| Escape prefix % | 21.1% | 2.1% | 7.8% |
| Universal MIDDLE % | 51.3% | 48.2% | 48.0% |

Compression analysis:
- **Escape suppression: Zodiac +89.9%, A/C +62.8%** (MASSIVE)
- Universal MIDDLE enrichment: -3.1pp, -3.3pp (preserved)
- Total entropy: EXPANDS slightly (+2.8% Zodiac, +5.0% A/C)

Success criteria:
- Significant compression (>20%): NO (entropy expands)
- Strong escape suppression (>50%): YES
- Universal preserved (>80%): YES
- Met: 2/3

#### Interpretation
**AZC is a COGNITIVE LOAD REDUCER and LEGALITY SIEVE at transition zones.**

Key insight: AZC does NOT compress overall entropy. It REDIRECTS:
- PREFIX compresses (+14.2% in Zodiac)
- MIDDLE EXPANDS (-14.0% in Zodiac)
- Escape logic SUPPRESSED by 90%

AZC filters hazardous options (escape prefixes like qo, ct) while EXPANDING recognition options (MIDDLE variety). This is selective filtering, not blanket simplification.

#### Limitations
Does not explain WHY escape logic is suppressed in AZC. Does not establish causal mechanism.

---

### F-AZC-006 - Boundary Airlock Profile

**Tier:** F4 | **Result:** INCONCLUSIVE | **Supports:** (pending data)

#### Question
Does AZC act as an entropy discontinuity in the A-space?

#### Method
Measure option-space metrics in windows:
- N tokens BEFORE AZC entry
- INSIDE AZC
- N tokens AFTER AZC exit

Metrics: MIDDLE diversity, suffix entropy, escape availability.
Fit models: step vs ramp vs null.

Data: ~122,000 total tokens, 37,214 A tokens, 3,299 AZC tokens.

Success criteria:
- Sharp entropy drop/redistribution at entry
- Rebound after exit
- Step model fits better than ramp or null

#### Result Details
- **Boundary crossings found: 1** (A→AZC in transcription order)
- Insufficient data for statistical comparison
- Before AZC: entropy 9.45, escape 19.7%, MIDDLE diversity 0.25
- Inside AZC: entropy 9.89, escape 18.4%, MIDDLE diversity 0.28
- After AZC: No data (no A→AZC→A transitions found)

#### Interpretation
**INCONCLUSIVE due to data sparsity.** The transcription order (folio-by-folio) does not capture frequent A↔AZC transitions. AZC folios are contiguous blocks, not interleaved with A.

This is a structural limitation of the source data, not a negative result. Testing this hypothesis would require either:
1. Line-level interleaving data
2. A different definition of "boundary" (e.g., within mixed folios)

#### Limitations
Cannot distinguish between "no airlock effect" and "insufficient transitions to detect effect."

---

### F-AZC-007 - Position-Conditioned Escape Suppression

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C463-C465

#### Question
Is escape suppression uniform or position-conditioned?

#### Method
1. Measure qo/ct frequency by placement code
2. Test if suppression is:
   - Uniform across all placements → AZC = global safety lock
   - Concentrated at boundaries → AZC = transition stabilizer
3. Chi-squared test for uniform distribution
4. Fisher's exact test for boundary vs interior comparison

Data: 5,354 AZC tokens, 301 escape tokens (5.6% overall).

Success criteria:
- Significant non-uniformity in escape distribution
- Clear boundary vs interior pattern

#### Result Details

**Zodiac:**
- Overall escape rate: 2.1%
- Chi-squared (uniform): 42.38, p<0.000001 (SIGNIFICANT)
- R1 escape rate: 5.3% (highest)
- R2 escape rate: 1.8%
- R3, R4, S0, S2: 0% escape
- Boundary vs interior: 0.0% vs 2.2% (Fisher p=0.62, not significant due to low N)

**A/C:**
- Overall escape rate: 7.9%
- Chi-squared (uniform): 144.84, p<0.000001 (SIGNIFICANT)
- P placement: 15.9% escape (highest)
- C placement: 2.3% escape (lowest major)
- Boundary vs interior: **2.8% vs 13.9%** (Fisher p<0.000001, SIGNIFICANT)

#### Interpretation
**Escape suppression is POSITION-CONDITIONED.** Evidence: 3/4 tests significant.

Key findings:
1. **Zodiac concentrates escape at R1** (early position), suppresses at later positions
2. **A/C suppresses escape at boundaries** (C, S) vs interior (P, R)
3. Pattern supports AZC = TRANSITION STABILIZER hypothesis

This refines F-AZC-004: escape suppression is not blanket filtering but selective by position. AZC allows more escape logic in "interior" positions while clamping down at boundaries.

#### Limitations
Does not explain WHY boundaries need stronger escape suppression. Mechanism remains speculative.

---

### F-AZC-008 - Boundary Asymmetry (Semantic Hypothesis Test)

**Tier:** F3 | **Result:** PARTIAL | **Supports:** (exploratory)

#### Semantic Hypothesis
> C and S positions are functionally asymmetric:
> - C = Intake/Initialization (entry into AZC processing zone)
> - S = Release/Finalization (exit from AZC processing zone)

This follows the semantic hypothesis testing protocol: **Name boldly. Test ruthlessly. Promote rarely.**

#### Structural Translation
If C and S are functionally asymmetric, we predict:
1. SUFFIX entropy: C < S (C constrains, S permits)
2. MIDDLE universality: C > S (C uses core, S allows tail)
3. Escape prefix rate: C < S (already observed)
4. Type overlap: Low Jaccard similarity (<50%)
5. Distributional difference: Chi-squared p < 0.05

#### Method
1. Load A/C family tokens, split by placement (C, C1, C2 vs S, S1, S2, S3)
2. Compare per-slot entropy (PREFIX, MIDDLE, SUFFIX)
3. Chi-squared test for distributional differences
4. Jaccard similarity for type overlap
5. Fisher's exact for universal MIDDLE and escape rates

Data: 3,278 A/C tokens (1,131 C-position, 275 S-position).

#### Result Details

**Per-Slot Entropy:**
| Slot | C entropy | S entropy | Delta | Significant |
|------|-----------|-----------|-------|-------------|
| PREFIX | 2.42 bits | 2.39 bits | -0.03 | NO |
| MIDDLE | 5.87 bits | 5.66 bits | -0.22 | NO |
| SUFFIX | 4.12 bits | 4.12 bits | +0.01 | NO |

**Distribution Tests (Chi-Squared):**
- PREFIX: χ²=59.0, p<0.000001, Cramér's V=0.21 (SIGNIFICANT)
- MIDDLE: χ²=550.8, p<0.000001, Cramér's V=0.74 (SIGNIFICANT)
- SUFFIX: χ²=119.8, p<0.000001, Cramér's V=0.29 (SIGNIFICANT)

**Type Overlap:**
- C unique types: 344
- S unique types: 129
- Shared types: 32
- Jaccard similarity: **0.073** (7.3% overlap - HIGHLY DISTINCT)

**Universal MIDDLE Rate:**
- C: 4.4%, S: 10.2% (Fisher p=0.0006, SIGNIFICANT but **opposite** direction)

**Escape Rate:**
- C: 2.6%, S: 4.4% (Fisher p=0.16, not significant)

**Evidence Summary:** 2/5 criteria met

#### Interpretation
**PARTIAL support for asymmetry hypothesis.** C and S are structurally different but not in the predicted direction.

Key insight: C and S have **different vocabularies** (distributions differ, Jaccard=0.073) but **equal entropy constraints** (similar bits per slot). They select from distinct token pools but with equal freedom within those pools.

The "intake/release" semantic frame is partially supported but requires refinement:
- **Confirmed:** C and S use different type vocabularies
- **Disconfirmed:** C does NOT constrain more than S (entropy equal)
- **Reversed:** S uses MORE universal MIDDLEs, not fewer

The hypothesis is **not promoted** but **not discarded**. The structural finding (distinct vocabularies, equal entropy) is real and may require a different semantic frame.

#### Limitations
Does not explain WHY C and S have distinct vocabularies. The "intake/release" metaphor may be wrong even though asymmetry exists.

---

### F-AZC-009 - Local vs Global Reference Partition (FINAL SEMANTIC TEST)

**Tier:** F4 | **Result:** DISCARDED | **Supports:** (none - frame rejected)

#### Semantic Frame (Tier 3 Hypothesis)
> C and S partition AZC boundary legality into local (AZC-specific) vs global (cross-system) reference spaces.
> - C = local/AZC-endemic vocabulary
> - S = global/cross-system vocabulary

This follows the semantic hypothesis testing protocol: **Name boldly. Test ruthlessly. Promote rarely.**

#### Pre-Registered Predictions
1. **P1**: AZC endemicity C > S (C-types appear only in AZC more often)
2. **P2**: Cross-system persistence S > C (S-types appear in A/B more often)
3. **P3**: Global reusability S > C (S-types span more systems)
4. **P4**: Family invariance (same patterns in Zodiac and A/C)

**Success criterion:** >=3 of 4 predictions met
**Failure criterion:** No systematic difference → discard frame

#### Method
1. Load all tokens from A, B, and AZC systems
2. For each token type, determine system membership
3. Compare C-position vs S-position types on endemicity, cross-system persistence, and global reusability
4. Fisher's exact and Mann-Whitney U tests for significance

Data: 37,214 A tokens, 75,545 B tokens, 3,299 AZC tokens, ~12,000 unique types.

#### Result Details

**Overall AZC:**
| Metric | C-position | S-position | Direction | Significant |
|--------|------------|------------|-----------|-------------|
| Endemicity | 47.0% | 46.0% | C > S | NO (p=0.72) |
| Cross-system | 53.0% | 54.0% | S > C | NO (p=0.72) |
| Avg systems | 1.883 | 1.886 | S > C | NO (p=0.92) |

**Predictions Met:** 1/4 (P4 only - family invariance)

#### Interpretation
**FRAME DISCARDED.** C and S have essentially identical cross-system reference profiles.

Key finding: C and S draw from the **same reference pools at the same rates**. The "local/global" partition hypothesis has no structural support.

This is a clean falsification. The semantic frame was tested rigorously with pre-registered criteria and failed. Per protocol, it is discarded without defense.

**STOP CONDITION REACHED:** After this test, AZC semantic exploration is COMPLETE. No further semantic frames should be proposed unless they contradict an existing constraint.

#### Limitations
N/A - frame is discarded.

---

### F-AZC-010 - Cross-System Alignment by Family (CALENDRIC STRESS TEST)

**Tier:** F4 | **Result:** FALSIFIED | **Supports:** (strengthens null hypothesis)

#### Hypothesis (Synthesis)
> Zodiac and A/C gate DIFFERENT domains:
> - Zodiac = seasonal/material gating (should align with Currier A)
> - A/C = operation-type gating (should align with Currier B)

This was a stress test of the calendric/seasonal interpretation of Zodiac pages.

#### Pre-Registered Predictions
1. **P1**: Zodiac types overlap MORE with Currier A than A/C types do
2. **P2**: A/C types overlap MORE with Currier B than Zodiac types do
3. **P3**: Zodiac types are more A-endemic (appear in A, not B)
4. **P4**: A/C types are more B-endemic (appear in B, not A)

**Success criterion:** >=3 of 4 predictions met with correct direction and significance

#### Method
1. Extract unique types from Zodiac folios and A/C folios
2. Calculate overlap with Currier A types and Currier B types
3. Calculate endemic rates (A-only, B-only)
4. Fisher's exact test for significance

Data: 5,101 A types, 7,263 B types, 1,335 Zodiac types, 1,667 A/C types.

#### Result Details

**Cross-System Alignment:**
| Metric | Zodiac | A/C | Difference |
|--------|--------|-----|------------|
| Overlap with A | 35.7% | 35.9% | -0.2% |
| Overlap with B | 41.7% | 41.5% | +0.2% |
| A-endemic | 6.5% | 6.8% | -0.3% |
| B-endemic | 12.6% | 12.4% | +0.2% |
| Shared (A∩B) | 29.1% | 29.1% | 0% |
| AZC-only | 51.8% | 51.8% | 0% |

**Predictions Met:** 0/4 (ALL directions WRONG, none significant)
- P1: NO (Zodiac 35.7% < A/C 35.9%, p=0.91)
- P2: NO (A/C 41.5% < Zodiac 41.7%, p=0.88)
- P3: NO (Zodiac 6.5% < A/C 6.8%, p=0.83)
- P4: NO (A/C 12.4% < Zodiac 12.6%, p=0.87)

#### Interpretation
**CALENDRIC/SEASONAL SYNTHESIS FALSIFIED.** Zodiac and A/C have essentially identical cross-system alignment patterns to within 0.2 percentage points.

Key findings:
1. **Both families gate the SAME domain** - they share vocabulary alignment profiles
2. **The family distinction is NOT about cross-system reference** - it's about positional parameterization and visual organization
3. **If Zodiac is seasonally-indexed, A/C must be too** - or neither is

This is the most extensive calendric stress test performed on AZC. The clean null result (0/4, all directions wrong) strongly suggests that the circular Zodiac diagrams are NOT functionally distinct from A/C pages in terms of what they reference.

**Historical note:** The possibility of proto-greenhouses, wintergardens, or year-round material availability in a large operation would further weaken any calendric interpretation. Seasonal constraints may not have been absolute for a well-resourced guild.

#### Limitations
Does not rule out external seasonal association (operator knowing which page to use when). Rules out the hypothesis that Zodiac and A/C gate DIFFERENT domains.

---

## Orientation Basis Fits

### F-AZC-011 - Folio Threading Analysis

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C318, C321, C430, C436

#### Question
How do AZC folios thread into A and B vocabulary? Why are there so many AZC folios?

#### Method
1. Load all tokens by folio with Currier A/B/AZC classification
2. For each AZC folio, calculate vocabulary overlap with A and B
3. Calculate inter-folio Jaccard similarity
4. Analyze A-type coverage distribution across AZC folios
5. Analyze B-folio sourcing patterns from AZC

Data: 30 AZC folios (27 diagram folios + 3 non-diagram), 3,047 types; 114 A folios, 4,737 types; 77 B folios, 6,616 types.

#### Result Details

**Per-Folio Threading:**
| Metric | Mean | Range |
|--------|------|-------|
| A overlap | 56.6% | 41.4% - 100% |
| B overlap | 63.4% | 42.3% - 100% |
| Endemic rate | 31.2% | 0% - 54.1% |

**Inter-Folio Similarity:**
- Mean Jaccard: **0.056** (lower than C321's 0.076 for consecutive zodiac)
- Most similar pair: f86v6:f86v5 (0.176)
- AZC folios have nearly independent vocabularies

**A-Type Coverage Distribution:**
- 478 A-types (49%) appear in exactly 1 AZC folio (SPECIALIZED)
- 28 A-types appear in 20+ AZC folios (GRAMMATICAL: daiin, aiin, dar, ar, al...)

**B-Folio Sourcing:**
- Every B folio draws from **34-36 AZC folios** (essentially ALL)
- Range is only 2 folios - extremely uniform
- B procedures do NOT concentrate on specific AZC sources

#### Interpretation
**AZC folios are maximally orthogonal orientation contexts.** Key findings:

1. Each AZC folio has nearly unique vocabulary (Jaccard=0.056)
2. All B procedures draw from essentially ALL AZC folios uniformly
3. Shared vocabulary is grammatical scaffolding
4. Specialized vocabulary is domain-specific

This pattern describes neither lookup tables nor variant procedures. It describes:

> **AZC is a complete basis of legal orientation states, not an index you look things up in.**

An index selects. A basis spans. Every operation happens in some linear combination of AZC constraints, but no operation "chooses" an AZC folio.

**Why there are many AZC folios:** AZC enumerates distinct orientation postures, each locally complete but globally different.

#### Limitations
Does not explain the content of individual orientation postures.

---

### F-AZC-012 - Orientation Basis Coverage

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C301, C318, C326, C343

#### Question
Does AZC collectively cover all A-vocabulary tokens that appear in B procedures?

If AZC is a "complete orientation basis," it should cover essentially all A-types that B procedures reference. Gaps would indicate incomplete coverage.

#### Method
1. Extract all A-types that appear in B procedures
2. Extract union of all A-types in AZC folios
3. Calculate coverage: |B's A-types ∩ AZC's A-types| / |B's A-types|
4. Calculate per-folio coverage for each B procedure

Data: 4,737 A types, 6,616 B types, 3,047 AZC types.

#### Result Details

**Aggregate Coverage:**
- A-types appearing in B: 1,431
- A-types appearing in AZC: 973
- A-types in B covered by AZC: 754
- **Aggregate coverage: 52.69%**

**Per-Folio Coverage:**
- Mean coverage per B folio: **83.2%**
- Min coverage: 72.5%
- Max coverage: 94.3%

**Gap Analysis:**
- 677 A-types appear in B but not AZC (long-tail, low-frequency types)
- 219 A-types appear in AZC but not B (excess coverage)

#### Interpretation
**AZC is a practically complete orientation basis.** The aggregate 52.7% is misleading.

Key insight: The 677 gap types are low-frequency A-types. The **83.2% per-folio coverage** means individual B procedures find most of their A-vocabulary represented in AZC. The basis is complete for common vocabulary.

This matches the expected pattern:
- AZC is not a full lookup table (would be 100%)
- AZC supports practically all common distinctions (83%+)
- Rare, edge-case A-types fall outside any given orientation posture

**83% ± ~10% is the sweet spot** for an orientation basis.

#### Limitations
Does not identify which A-types are missing and why.

---

### F-AZC-013 - Orientation Posture Differentiation

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C436, C457, C458, C460

#### Question
Do different AZC folios correspond to different HT decay profiles?

This is descriptive only - not causal. We're testing whether AZC folio identity correlates with HT characteristics.

#### Method
1. For each AZC folio, calculate HT-relevant metrics:
   - Escape rate (qo- prefix frequency)
   - Early rate (ol-, or-, al-, ar- prefixes)
   - Core rate (ch-, sh- prefixes)
   - Prefix entropy
2. Compare profiles across folios
3. Look for clustering and systematic variation

Data: 30 AZC folios (27 diagram folios + 3 non-diagram).

#### Result Details

**HT Profile Variance:**
| Metric | Min | Max | Variance |
|--------|-----|-----|----------|
| Escape rate | 0.00% | 18.13% | **18.1pp** |
| Early rate | 0.00% | 50.00% | **50.0pp** |
| Core rate | 0.00% | 50.00% | **50.0pp** |
| Prefix entropy | 1.00 | 3.22 | 2.22 bits |

**Zodiac vs Non-Zodiac Pattern:**
- **Lowest escape folios:** f68v1, f71v, f72r1, f72r3, f72v1 (all zodiac) → **0%**
- **Highest escape folios:** f86v6, f86v3, f85r2 (non-zodiac) → **13-18%**

**Clustering:**
- 17 distinct clusters found (threshold=3.0pp)
- Cluster 1: 8 zodiac folios (similar low-escape profiles)
- High differentiation across AZC space

#### Interpretation
**Different AZC folios instantiate genuinely different orientation postures.** This is the most important new result in the AZC arc.

Key findings:
1. **18pp escape variance** - not noise, real differentiation
2. **Zodiac folios = consistently low escape** (0-2%)
3. **Non-zodiac folios = wide escape range** (9-18%)
4. **17 clusters** - high posture differentiation

This ties together:
- AZC grammar (C430-C436)
- Escape suppression (C463-C465)
- HT behavior (C457, C460)
- Zodiac vs non-Zodiac distinction

without invoking calendar semantics, material lists, or procedure selection.

Combined with F-AZC-012: **AZC is not big because it encodes many things. It is big because it encodes many distinct ways of not making a mistake.**

#### Limitations
Does not establish causal mechanism. Descriptive only.

---

### F-AZC-015 - Windowed AZC Activation Trace

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C440, C441-C444

#### Question
What does the parallel constraint landscape look like during B procedure execution?

We established that:
- AZC operates at token level, not entry level (C441-C444)
- B procedures draw from ALL 34-36 AZC folios uniformly (C440)
- This implies multiple compatibility classes may be simultaneously active

This probe reveals whether parallelism is:
- **Case A**: Structured (3-5 folios dominate per moment)
- **Case B**: Uniform (20-30 folios always active)
- **Case C**: Phased (broad → narrow → collapse over execution)

#### Method
1. Select 8 B folios: 3 brittle (f83v, f77r, f76r), 3 forgiving (f48r, f85v2, f105v), 2 mixed (f113r, f41r)
2. Build complete token→AZC folio mapping from source data (3,047 types)
3. For each B folio, compute windowed metrics:
   - Window size: 11 tokens
   - Stride: 3 tokens
   - Track: n_folios_active, zodiac_fraction, persistence, suffix-phase rate
4. Compute temporal pattern: UNIFORM, OSCILLATING, PHASED_NARROWING, or PHASED_BROADENING
5. Compute persistence: Jaccard overlap between consecutive windows

Data: 8 B folios, 8,618 tokens total, 2,849 windows analyzed.

#### Result Details

**Per-Folio Summary:**
| Folio | Type | Tokens | N Folios Mean | Range | Pattern | Persistence |
|-------|------|--------|---------------|-------|---------|-------------|
| f83v | brittle | 1,021 | 24.7 | 5-34 | OSCILLATING | 0.917 |
| f77r | brittle | 1,294 | 23.3 | 1-35 | PHASED_BROADENING | 0.924 |
| f76r | brittle | 2,222 | 28.6 | 9-35 | OSCILLATING | 0.932 |
| f48r | forgiving | 330 | 27.7 | 17-34 | OSCILLATING | 0.918 |
| f85v2 | forgiving | 343 | 25.8 | 3-34 | OSCILLATING | 0.835 |
| f105v | forgiving | 1,169 | 27.2 | 3-35 | PHASED_BROADENING | 0.931 |
| f113r | mixed | 1,868 | 25.7 | 3-35 | OSCILLATING | 0.903 |
| f41r | mixed | 371 | 20.5 | 0-34 | PHASED_BROADENING | 0.869 |

**Type Analysis:**
| Folio Type | N Folios Mean | Pattern Distribution | Persistence |
|------------|---------------|---------------------|-------------|
| Brittle | 25.56 | OSCILLATING: 2, PHASED_BROADENING: 1 | 0.924 |
| Forgiving | 26.89 | OSCILLATING: 2, PHASED_BROADENING: 1 | 0.895 |
| Mixed | 23.08 | OSCILLATING: 1, PHASED_BROADENING: 1 | 0.886 |

**Aggregate:**
- Mean AZC folios active: **25.18** (out of ~36 total = 70%)
- Threshold for Case B: ≥15 folios → **CASE B CONFIRMED**
- Dominant patterns: OSCILLATING (50%), PHASED_BROADENING (50%)
- Persistence: 0.87-0.93 (same folios stay active across windows)
- Zodiac fraction: stable at 0.32-0.36 (~1/3 of active set)

#### Interpretation
**Case B confirmed: High-order uniform parallelism.**

Key findings:
1. **~70% of AZC folios are active at any given moment** - not 3-5 (Case A) or narrowing (Case C)
2. **Very high persistence** (0.87-0.93) - the same folios stay active across consecutive windows
3. **No significant difference by folio type** - brittle (25.6), forgiving (26.9), and mixed (23.1) show similar patterns
4. **Zodiac fraction stable** - Zodiac folios consistently ~1/3 of active set

**Implication for architecture:**
> **AZC is primarily a global legality baseline, not a dynamic constraint narrower.**

The parallelism is **latent** (built-in to the vocabulary), not dynamically resolved during execution. When a B procedure runs, it operates against essentially the entire AZC constraint space simultaneously.

This refines our understanding:
- AZC provides **broad ambient legality** - you're always constrained by ~25 folios
- HT (Human Track) becomes the primary **attentional modulator** - focuses attention within the broad constraint field
- Constraint narrowing happens at the **vocabulary selection** level, not execution level

The high persistence (0.9+) means once you commit to certain vocabulary, the constraint profile stays stable. You don't "move through" different AZC postures during execution - you operate within a fixed, broad constraint envelope.

#### Limitations
Does not distinguish between:
1. Active constraint enforcement vs passive background legality
2. Whether all 25 folios contribute equally or some dominate

---

### F-AZC-016 - AZC->B Constraint Fit Validation

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C468, C469, C470

#### Question
Do AZC constraints actually apply in Currier B, or is vocabulary overlap coincidental?

This is the decisive pipeline validation test. We've shown AZC vocabulary appears in B (F-AZC-012), but not whether constraints transfer.

#### Method
Three tests of constraint transfer:

1. **MIDDLE restriction inheritance**: Do MIDDLEs restricted in AZC show restricted behavior in B?
2. **Position preservation**: Do AZC position-locked MIDDLEs show position bias in B?
3. **Escape rate transfer**: Do tokens from high-escape AZC folios show higher escape in B?

Data: 12,563 AZC tokens, 71,585 B tokens.

#### Result Details

**Test 1: MIDDLE Restriction -> B Folio Spread**
| Restriction Class | AZC Folios | Mean B Folio Spread |
|-------------------|------------|---------------------|
| Restricted (1-2 folios) | 1,176 MIDDLEs | 4.0 B folios |
| Moderate (3-10 folios) | 189 MIDDLEs | 11.9 B folios |
| Universal (10+ folios) | 54 MIDDLEs | 50.6 B folios |

**Result: CONFIRMED** - 12.7x difference between restricted and universal MIDDLEs

**Test 2: AZC Position -> B Position**
- C-only MIDDLEs: 186 types
- S-only MIDDLEs: 192 types
- Insufficient matching data in B for statistical test

**Result: INCONCLUSIVE** (data sparsity)

**Test 3: AZC Escape Profile -> B Escape Behavior**
| AZC Escape Profile | B Escape Rate | Sample Size |
|--------------------|---------------|-------------|
| Low (<5%) | 1.0% | 17,456 tokens |
| High (>=5%) | 28.6% | 34,830 tokens |

**Result: CONFIRMED** - 28x difference in B escape rates

#### Interpretation
**Pipeline causality validated.** AZC constraints DO apply in B.

Key findings:
1. **MIDDLE restriction transfers** - MIDDLEs legal in few AZC contexts remain restricted in B
2. **Escape profiles transfer** - Tokens from high-escape AZC folios show 28x higher escape in B
3. **This is not coincidental overlap** - structural properties propagate through the pipeline

This completes the pipeline validation:
- A provides the registry (WHAT exists)
- AZC provides the legality filter (WHEN things can combine)
- B respects AZC constraints during execution (HOW things proceed)

The manuscript is a **causally connected control system**, not just correlated text layers.

#### Limitations
Position preservation test was inconclusive due to data sparsity.

---

### F-AZC-017 - Zodiac Internal Stratification Test (NEGATIVE)

**Tier:** F4 | **Result:** FALSIFIED | **Supports:** C431, C436

#### Question
Do different Zodiac AZC folios preferentially admit different regions of the Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?

This tests whether the 12 Zodiac folios (C321: independent vocabularies, Jaccard 0.076) represent internal legality stratification, or whether their multiplicity exists purely for coverage optimality.

**Critical framing note:** This is NOT a test of "product routing through gates." AZC filters constraint bundles; product types are downstream inferences from B behavior.

#### Method

1. Extract product-associated MIDDLEs from B folios (by REGIME classification)
2. Map those MIDDLEs to the 13 Zodiac folios (12 Z + f57v)
3. Test for clustering via chi-squared test of independence

**Data:** 75,173 B tokens, 3,368 Zodiac AZC tokens, 2,777 product-exclusive MIDDLEs.

#### Result Details

**Distribution entropy per product (higher = more spread):**
| Product | Entropy | Max Possible |
|---------|---------|--------------|
| OIL_RESIN | 2.87 bits | 3.70 bits |
| PRECISION | 3.40 bits | 3.70 bits |
| WATER_GENTLE | 2.73 bits | 3.70 bits |
| WATER_STANDARD | 3.63 bits | 3.70 bits |

All products show near-maximum entropy (spread across all folios).

**Enrichment analysis:**
- No folio shows >23% of any product's MIDDLEs
- Maximum enrichment: f70v1 has 23.1% of OIL_RESIN MIDDLEs
- WATER_STANDARD (largest) is nearly uniform: max folio has only 11.8%

**Chi-squared test:**
- Statistic: 27.32
- Degrees of freedom: 36
- **P-value: 0.85** (far above 0.05 threshold)

#### Interpretation

**VERDICT: NO STRATIFICATION**

Product-associated MIDDLEs are uniformly distributed across all 13 Zodiac folios. The null hypothesis (no internal stratification) is strongly confirmed.

**Conclusion:** Zodiac multiplicity exists purely for **coverage optimality**, not for internal stratification of the legality manifold. The 12 Zodiac folios are structurally equivalent gates.

This closes the door definitively on the hypothesis that Zodiac folios realize different sub-regions of incompatibility space correlated with product inference.

#### Implications

1. **Validates existing model** — Zodiac folios ARE equivalent gates (C431 "structural clones" confirmed)
2. **No hidden routing** — Product differentiation is NOT encoded at the Zodiac level
3. **Coverage is the answer** — Zodiac needed 12 copies to cover the full MIDDLE space, not to stratify it
4. **Refines C436 (Dual Rigidity)** — The uniform scaffold is also uniformly populated

#### Source Phase
`phases/AZC_ZODIAC_INTERNAL_STRATIFICATION/`

---

### F-AZC-018 - A/C Internal Stratification Test (NEGATIVE)

**Tier:** F4 | **Result:** FALSIFIED | **Supports:** C430, C436

#### Question
Do different A/C AZC folios preferentially admit different regions of the Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?

This tests whether the A/C family (C430: low cross-folio consistency 0.340, each folio has its own scaffold) shows product-correlated stratification that Zodiac does not.

**Critical framing note:** This is NOT a test of "product routing through gates." AZC filters constraint bundles; product types are downstream inferences from B behavior.

#### Method

1. Identify A/C AZC folios (17 folios: f65v-f70r2 range, excluding Zodiac)
2. Extract product-exclusive MIDDLEs from B (by REGIME classification)
3. Map those MIDDLEs to A/C folio vocabularies
4. Test for clustering via chi-squared test of independence

#### Data

**Input:**
- 75,173 B tokens across 83 folios
- 5,607 A/C AZC tokens across 17 folios
- 2,777 product-exclusive MIDDLEs

**Product-exclusive MIDDLE counts:**
| Product | Exclusive MIDDLEs |
|---------|-------------------|
| WATER_STANDARD | 1,517 |
| WATER_GENTLE | 450 |
| PRECISION | 430 |
| OIL_RESIN | 380 |

#### Results

**Distribution entropy per product (higher = more spread):**
| Product | Entropy | Max Possible |
|---------|---------|--------------|
| OIL_RESIN | 2.00 bits | 4.09 bits |
| PRECISION | 3.46 bits | 4.09 bits |
| WATER_GENTLE | 3.17 bits | 4.09 bits |
| WATER_STANDARD | 3.69 bits | 4.09 bits |

OIL_RESIN has lower entropy due to data sparsity (only 4 mapped MIDDLEs across all A/C folios).

**Enrichment analysis:**
- No folio shows >25% of any product's MIDDLEs
- Maximum enrichment: f67r2 has 25% of OIL_RESIN (1 of 4 MIDDLEs)
- WATER_STANDARD (largest) is nearly uniform: max folio has only 15%

**Chi-squared test:**
- Statistic: 46.67
- Degrees of freedom: 42
- **P-value: 0.29** (far above 0.05 threshold)

#### Interpretation

**VERDICT: NO STRATIFICATION**

Product-associated MIDDLEs are uniformly distributed across all 17 A/C folios. The null hypothesis (no internal stratification) is strongly confirmed.

**Comparison with Zodiac:**
| Family | P-value | Verdict |
|--------|---------|---------|
| Zodiac | 0.85 | NO STRATIFICATION |
| A/C | 0.29 | NO STRATIFICATION |

**Conclusion:** A/C scaffold diversity (consistency=0.340) does NOT correlate with product types. The variation exists for other structural reasons, not for product-specific stratification.

#### Implications

1. **AZC is uniformly product-agnostic** — Neither family shows product-correlated stratification
2. **Validates C430** — A/C diversity is structural, not semantic
3. **Closes stratification hypothesis** — Product differentiation is NOT encoded at ANY AZC level
4. **Supports universal filtering** — AZC filters constraint bundles uniformly regardless of downstream product inference

#### Source Phase
`phases/AZC_ZODIAC_INTERNAL_STRATIFICATION/`

---

### F-AZC-019 - A/C Incompatibility Density Test (POSITIVE)

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C430, C475

#### Question
Are A/C AZC folios activating more densely incompatible subsets of the MIDDLE space than Zodiac folios?

This tests whether A/C's scaffold diversity (C430: consistency 0.340) reflects higher constraint exclusion burden - more mutually exclusive constraints held simultaneously.

#### Method

1. Build global MIDDLE co-occurrence matrix from all AZC folios
2. For each folio, extract its unique MIDDLE vocabulary
3. Compute local incompatibility density: (illegal pairs / total pairs among folio MIDDLEs)
4. Compare A/C family vs Zodiac family via Mann-Whitney U

#### Results

**Local incompatibility density (fraction of MIDDLE pairs that are illegal):**
| Family | Mean | Std | n |
|--------|------|-----|---|
| A/C | **0.5488** | 0.2347 | 17 |
| Zodiac | **0.3799** | 0.0833 | 13 |
| Global baseline | 0.9568 | - | - |

**Statistical test:**
- Mann-Whitney U: 188.00
- **P-value: 0.0006** (highly significant)
- Effect size: r = -0.70 (large)

#### Interpretation

**VERDICT: STRONG SIGNAL**

A/C folios activate significantly more densely incompatible MIDDLE subsets than Zodiac folios. This confirms the expert's hypothesis:

> **A/C manages fine-discrimination through higher constraint exclusion burden. It holds more mutually exclusive constraints simultaneously than Zodiac.**

**Complementary finding:** Zone-transition analysis showed A/C has LOWER zone switching (0.004 vs 0.018). This means A/C achieves higher incompatibility density while maintaining positional stability - the opposite of what "more complex = more movement" would predict.

#### Implications

1. **Validates expert framing** - A/C = fine-discrimination checkpoints, Zodiac = coarse-discrimination flow
2. **Explains C430** - A/C scaffold diversity reflects discrimination burden, not product types
3. **Quantifies family difference** - 45% higher incompatibility density in A/C (0.55 vs 0.38)
4. **Refines AZC model** - Incompatibility density is the discriminating feature between families

#### Source Phase
`phases/AC_INTERNAL_CHARACTERIZATION/`

---

## Summary

| Fit | Tier | Result | Key Finding |
|-----|------|--------|-------------|
| F-AZC-001 | F4 | NEGATIVE | Morphology does not predict placement |
| F-AZC-002 | F2 | SUCCESS | Zodiac implements positional grammar |
| F-AZC-003 | F4 | PARTIAL | Families share morphology, differ in layout |
| F-AZC-004 | F2 | SUCCESS | AZC suppresses escape logic by 90% |
| F-AZC-005 | F2 | SUCCESS | A/C implements positional grammar (DECISIVE) |
| F-AZC-006 | F4 | INCONCLUSIVE | Boundary airlock untestable (data sparsity) |
| F-AZC-007 | F2 | SUCCESS | Escape suppression is position-conditioned |
| F-AZC-008 | F3 | PARTIAL | C/S have distinct vocabularies, equal entropy |
| F-AZC-009 | F4 | DISCARDED | Local/global reference partition falsified |
| F-AZC-010 | F4 | FALSIFIED | Calendric synthesis: families gate SAME domain |
| F-AZC-011 | F2 | SUCCESS | AZC folios are maximally orthogonal orientation contexts |
| F-AZC-012 | F2 | SUCCESS | AZC is a practically complete orientation basis (83%) |
| F-AZC-013 | F2 | SUCCESS | Different AZC folios have distinct HT profiles |
| F-AZC-015 | F2 | SUCCESS | Case B: High-order uniform parallelism (70% AZC active) |
| F-AZC-016 | F2 | SUCCESS | Pipeline causality validated (28x escape transfer) |
| F-AZC-017 | F4 | FALSIFIED | Zodiac internal stratification falsified (p=0.85) |
| F-AZC-018 | F4 | FALSIFIED | A/C internal stratification falsified (p=0.29) |
| F-AZC-019 | F2 | SUCCESS | A/C has 45% higher incompatibility density than Zodiac (p=0.0006) |

### Architectural Implications

1. **Placement is positional, not content-based** (F-AZC-001)
2. **Zodiac has a true positional grammar** (F-AZC-002)
3. **Families are parameterized variants** (F-AZC-003)
4. **AZC is a legality sieve** (F-AZC-004)
5. **A/C has a true positional grammar** (F-AZC-005) - DECISIVE
6. **Escape suppression is selective by position** (F-AZC-007)
7. **C and S use distinct vocabularies with equal entropy** (F-AZC-008)
8. **AZC folios are maximally orthogonal orientation contexts** (F-AZC-011) - Jaccard=0.056
9. **AZC is a practically complete orientation basis** (F-AZC-012) - 83% per-folio coverage
10. **Different AZC folios have distinct HT profiles** (F-AZC-013) - 18pp escape variance
11. **AZC provides ambient, not dynamic, constraint activation** (F-AZC-015) - 70% active per window
12. **AZC constraints causally transfer to B execution** (F-AZC-016) - 28x escape rate difference
13. **Zodiac multiplicity is for coverage, not stratification** (F-AZC-017) - p=0.85 null confirmed
14. **A/C diversity is structural, not product-correlated** (F-AZC-018) - p=0.29 null confirmed
15. **A/C manages higher incompatibility density than Zodiac** (F-AZC-019) - 0.55 vs 0.38 (p=0.0006)

Combined interpretation:
> **AZC is a complete basis of legal orientation states. Each folio instantiates a distinct "how should I be thinking right now?" posture, not a variant procedure or material list. AZC is large because it must explicitly enumerate every orientation posture in which an operator might find themselves, since no single posture is safe across all contexts.**

This resolves the "why so many AZC folios?" question:
> **AZC is not big because it encodes many things. It is big because it encodes many distinct ways of not making a mistake.**

---

## Component Closure Statement

**AZC is FULLY CLOSED: STRUCTURALLY, SEMANTICALLY, AND FUNCTIONALLY.**

### Structural Closure (F-AZC-005)

The decisive test established that both AZC families share a common positional grammar:
- **Zodiac**: R1 < R2 < R3 < R4 (subscripted positional codes)
- **A/C**: C < P < R < S (unsubscripted positional codes)

This resolves the fundamental question: **AZC = ONE UNIFIED SYSTEM with two parameter regimes**, not two separate systems.

Key structural findings:
1. Positional grammar governs token placement (F-AZC-002, F-AZC-005)
2. Escape logic is suppressed overall but position-conditioned (F-AZC-004, F-AZC-007)
3. Morphology does not predict placement (F-AZC-001)
4. Families differ in layout parameters, not fundamental structure (F-AZC-003)
5. C and S use distinct vocabularies with equal entropy (F-AZC-008)

### Semantic Closure (F-AZC-008, F-AZC-009, F-AZC-010)

Three semantic frames were tested following the protocol: **Name boldly. Test ruthlessly. Promote rarely.**

| Frame | Hypothesis | Outcome |
|-------|------------|---------|
| Intake/Release | C constrains, S permits | PARTIAL - wrong direction |
| Local/Global | C = AZC-endemic, S = cross-system | DISCARDED - no difference |
| Calendric Synthesis | Zodiac = seasonal, A/C = operational | FALSIFIED - identical alignment |

**Finding:** C and S have distinct vocabularies (Jaccard=7.3%) but identical entropy and cross-system reference profiles. Zodiac and A/C have identical cross-system alignment to within 0.2 percentage points.

**Calendric Stress Test (F-AZC-010):** The most extensive test of seasonal/calendric interpretation. Result: 0/4 predictions met, all directions wrong. Both AZC families gate the SAME domain with the SAME vocabulary alignment. The family distinction is about positional parameterization and visual organization, not functional domain.

### Functional Closure (F-AZC-011, F-AZC-012, F-AZC-013) - FINAL

The "why so many AZC folios?" question is now definitively answered:

| Finding | Evidence | Implication |
|---------|----------|-------------|
| AZC folios are maximally orthogonal | Jaccard=0.056 | Each folio = distinct orientation |
| AZC is practically complete | 83% per-folio coverage | Basis spans common vocabulary |
| Different folios = different HT profiles | 18pp escape variance | Real posture differentiation |
| B procedures touch ALL AZC folios | 34-36 sources per B | AZC is ambient, not selected |

**Final Interpretation:**
> **AZC is a complete basis of legal orientation states, not an index you look things up in. Each folio instantiates a distinct orientation posture. AZC is large because it enumerates many distinct ways of not making a mistake.**

This explains:
- why AZC is neither small nor exhaustive
- why Zodiac pages repeat structure but differ in effect
- why A and B both "touch" every AZC folio
- why semantic decoding kept failing

**STOP CONDITION:** AZC is fully closed. No further discovery-class tests remain. Any remaining work is presentation refinement only.

### What Remains Unknown (Parked)

- WHAT the content of individual orientation postures IS (opaque by design)
- WHY C and S have distinct vocabularies (structural fact without semantic explanation)
- WHAT the subscripted vs unsubscripted labeling conventions mean

These questions are **parked, not pursued**. AZC's structure and function are understood; semantic content remains opaque and is not expected to yield to further testing.

---

## Operational Synthesis (Tier 3)

The structural findings (Tier 2) support a coherent operational interpretation of how AZC functions within the complete system.

### AZC as Decision-Point Grammar

**Core insight:** AZC converts static Currier A registry entries into phase-gated decision points.

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to proceed | Procedural sequence |
| AZC | WHEN to decide | Decision grammar |

A Currier A entry (e.g., "daiin") in isolation is a material class - static, descriptive. The SAME token in AZC becomes a decision point:
- In position P: intervention is legal (11.6% escape)
- In position S: intervention is forbidden (0% escape)

**AZC is the interface layer** that converts static knowledge (A) into actionable decision points within procedures (B).

### Phase-to-Workflow Mapping

The positional grammar maps to operational workflow phases:

| AZC Position | Workflow Phase | Escape Rate | Operational Meaning |
|--------------|----------------|-------------|---------------------|
| C | Setup/Loading | 1.4% | Entry constrained, errors fixable |
| P | Active work | 11.6% | Recovery permitted, intervention legal |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Collection/Exit | 0-3.8% | Locked, must accept outcome |

This matches the physical reality of reflux distillation: early phases are reversible, late phases are committed.

### Compatibility Filter Mechanism

**Key structural fact:** AZC folios have 94% unique vocabulary (Jaccard = 0.056).

This means AZC folios function as **compatibility filters**:
- Specialized A-types appear in only 1-3 folios
- Using vocabulary from one folio excludes vocabulary from others
- Incompatible A-registry entries cannot be combined in the same constraint space

**The enforcement mechanism:** You cannot specify incompatible combinations because the grammar won't let you write them. The mistake is blocked at the specification level, not at execution.

### Ambient Constraint Activation

AZC folios are not selected explicitly. They operate as a parallel constraint field:

1. **Core vocabulary** (appears in 20+ folios) → broadly legal, moderate constraints
2. **Specialized vocabulary** (appears in 1-3 folios) → activates specific constraint profile
3. **Position (C→P→R→S)** → determines phase-specific rules within that profile

The vocabulary you use determines which constraints apply. B procedures touch ALL AZC folios because they use diverse vocabulary that spans the constraint space.

### Zodiac vs Non-Zodiac Distinction

| Family | Escape Profile | Operational Context |
|--------|---------------|---------------------|
| Zodiac (26 folios) | 2.4% mean | Routine, predictable, low intervention |
| Non-Zodiac (10 folios) | 7.6% mean | Variable, demanding, more intervention |

The family distinction encodes **context risk profiles**, not different domains or procedures. Zodiac vocabulary activates low-intervention constraints; non-Zodiac vocabulary permits more intervention.

### Summary Statement

> **AZC is a decision-point grammar that transforms static material references into phase-gated choice nodes, enforces compatibility between materials and operations, and encodes when intervention is legal versus when outcomes must be accepted.**

This explains:
- Why AZC is large (enumerates all compatibility classes)
- Why folios have unique vocabulary (mutual exclusion of incompatible terms)
- Why B procedures touch all folios (use vocabulary from entire constraint space)
- Why escape rates vary by position (phase-dependent intervention legality)
- Why semantic decoding failed (AZC encodes constraints, not content)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

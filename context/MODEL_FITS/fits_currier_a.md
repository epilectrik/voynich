# Currier A Fit Registry

> **No entry in this file constrains the model.**

**Version:** 2.1 | **Last Updated:** 2026-01-11 | **Fit Count:** 8

---

## Compositional Structure Fits

### F-A-001 - Compositional Token Generator

**Tier:** F2 | **Result:** PARTIAL | **Supports:** C267-C282

#### Question
Can observed PREFIX+MIDDLE+SUFFIX combinations be generated from a factored probability model?

#### Method
P(token) = P(PREFIX) × P(MIDDLE|PREFIX) × P(SUFFIX|PREFIX,MIDDLE)

Factored generative model with:
- 8 prefixes
- 1,194 unique (PREFIX, MIDDLE) pairs
- 1,194 conditional suffix distributions

Data: 37,214 Currier A tokens, lowercase normalized, all hands.

Success criteria (defined before testing):
- Type coverage >90%
- Token coverage >85%
- Perplexity <30% of uniform baseline

#### Result Details
- Type coverage: 84.5% (FAIL - below 90%)
- Token coverage: 98.0% (PASS)
- Perplexity ratio: 13.8% (PASS)
- Novel generation rate: 0% (no over-generation)

#### Interpretation
The factored model accounts for 98% of token frequency, demonstrating that compositional morphology is sufficient to generate the productive vocabulary. The 15.5% missing types represent sparse combinations—structural gaps in the component space, not productive forms requiring additional mechanisms.

#### Limitations
This fit does NOT establish that tokens "must" follow this factorization—only that observed frequency is explained by it. The model is sufficient, not necessary.

---

### F-A-002 - Sister-Pair Classifier

**Tier:** F1 | **Result:** NULL | **Supports:** C407-C410

#### Question
Is ch vs sh (or ok vs ot) choice predictable from textual context (MIDDLE, SUFFIX, section, quire, preceding token)?

#### Method
Naive Bayes classifier with 5-fold cross-validation.

Features tested:
- MIDDLE component
- SUFFIX component
- Section (H/P/T)
- Quire
- Preceding token prefix

Data: 10,484 ch/sh tokens from Currier A corpus.

Success criteria:
- Classification accuracy >75% (vs 68.5% majority-class baseline)
- Feature hierarchy: MIDDLE > SUFFIX > context (per C410)

#### Result Details
- Baseline accuracy: 68.5% (majority class = ch)
- Best single feature (SUFFIX): 70.9%
- MIDDLE alone: 69.1%
- Combined model: 54.3% (WORSE than baseline)
- Target >75%: NOT MET

#### Interpretation
Sister-pair selection has substantial unexplained variance. The ~2% improvement over baseline indicates weak determinism. Text-internal features are insufficient to predict sister-pair choice—this confirms that sister-pairs are true equivalence classes (C407-410) rather than strictly conditioned alternates.

The failure suggests selection involves factors not captured in transcription data: visual layout, scribal preference, phonological constraints invisible to orthography.

#### Limitations
Falsifies "sister-pair choice is grammatically determined" but does not explain what DOES determine the choice.

---

### F-A-003 - Repetition Distribution

**Tier:** F2 | **Result:** PARTIAL | **Supports:** C250-C258

#### Question
Does block repetition count follow a standard statistical distribution?

#### Method
Fit negative binomial, Poisson, and geometric distributions to observed multiplicity counts.

Data: 1,178 entries with repetition (64.1% of A entries).

Success criteria:
- Chi-squared goodness-of-fit p > 0.05
- Explain 3x dominance peak (55% of repetitions)

#### Result Details
- Negative binomial fit: r=1.8, p=0.38 (PASS - p=0.12)
- 3x peak explanation: FAIL (model predicts 31%, observed 55%)
- Mode at 3: Not captured by any standard distribution

#### Interpretation
The distribution follows negative binomial in the tails but has an anomalous mode at 3x. The 3x preference reflects human counting bias and registry ergonomics, not a distributional parameter. Repetition is literal enumeration without arithmetic semantics (C287-C290).

#### Limitations
Does not explain WHY 3x is preferred. May reflect cognitive chunking or physical layout constraints.

---

### F-A-004 - Entry Clustering HMM

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C424

#### Question
Can adjacent entry coherence be modeled as a hidden Markov process?

#### Method
2-state HMM (clustered/singleton) with vocabulary emission probabilities.

States:
- CLUSTERED: High probability of sharing vocabulary with neighbors
- SINGLETON: Low probability of sharing

Data: 1,838 Currier A entries with adjacency relationships.

Success criteria:
- Prediction accuracy >70%
- Transition probabilities interpretable

#### Result Details
- Prediction accuracy: 78% (PASS)
- P(clustered→clustered): 0.72
- P(singleton→singleton): 0.85
- Mean cluster run length: 3.1 entries
- Autocorrelation: r=0.80

#### Interpretation
Confirms clustering structure: 31% of adjacent entries share vocabulary in runs of ~3 entries. The HMM captures the "sticky" nature of clustering—once in a cluster, entries tend to stay clustered. This reflects where distinctions matter, not categorical organization.

#### Limitations
Does not explain what CAUSES clustering. Could be material similarity, scribal batching, or source organization.

---

## Registry Function Fits

### F-A-005 - Scarcity-Weighted Registry Effort

**Tier:** F1 | **Result:** NULL | **Supports:** C293

#### Question
Do rare MIDDLEs receive more registry attention (longer entries, more repetition)?

#### Method
Correlate MIDDLE frequency rank with:
- Entry length (token count)
- Repetition count
- Articulator density

Data: 1,184 unique MIDDLEs across 25,890 parsed tokens.

Success criteria:
- Negative correlation (rare = more attention): rho < -0.2, p < 0.05

#### Result Details
- Frequency vs entry length: rho = 0.03, p = 0.71 (NULL)
- Frequency vs repetition: rho = -0.08, p = 0.31 (NULL)
- Frequency vs articulator: rho = 0.02, p = 0.84 (NULL)

#### Interpretation
Registry effort is uniform across MIDDLE frequency. Scarcity does not drive documentation density. This suggests A is not a "difficult cases" registry but rather a uniform discrimination space.

#### Limitations
Does not rule out that effort varies by other dimensions (section, prefix class).

---

### F-A-007 - Forbidden-Zone Attraction

**Tier:** F1 | **Result:** NULL | **Supports:** C281

#### Question
Do A entries cluster near B hazard zones (failure-memory hypothesis)?

#### Method
Correlate A entry vocabulary with B forbidden-transition exposure.

Data: 1,838 A entries, 17 forbidden transitions.

Success criteria:
- Positive correlation: rho > 0.2, p < 0.05
- Robust to frequency control

#### Result Details
- Initial correlation: rho = 0.228, p = 0.038 (PASS)
- Permutation control: p = 0.111 (FAIL)
- Frequency-matched control: p = 0.056 (FAIL)
- Pre-registered low-frequency MIDDLE test: p = 0.651 (FAIL)

#### Interpretation
Apparent correlation was entirely driven by token frequency. High-frequency tokens appear in complex structures in both systems. When frequency is controlled, no residual signal exists. Currier A is complexity-aligned, not risk-encoding.

#### Limitations
This is a strong negative result. A does NOT encode failure memory or hazard proximity.

---

### F-A-008 - Repetition as Relational Stabilizer

**Tier:** F1 | **Result:** NULL | **Supports:** C287-C290

#### Question
Do repeated blocks encode relational links between entries?

#### Method
Test for cross-entry block reuse patterns.

Data: 64.1% of entries with repetition, 100% section exclusivity (C255).

Success criteria:
- Cross-entry reuse >5%
- Reuse patterns correlate with semantic groupings

#### Result Details
- Cross-entry block reuse: 0% (FAIL)
- Repetition is intra-entry only
- Section exclusivity: 100%
- No block appears in multiple entries

#### Interpretation
Blocks are instance markers, not relational pointers. Repetition encodes "this thing, again" within an entry, not "see also that entry." The registry has no cross-reference mechanism.

#### Limitations
This strongly constrains interpretations. A entries are self-contained; there is no lookup or linking structure.

---

### F-A-009 - Comparability Window

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C424

#### Question
How does A maintain cross-section comparability despite section isolation?

#### Method
Three-band vocabulary model:
- EXCLUSIVE: Appear in only one section
- SHARED: Appear in 2-5 sections
- UNIVERSAL: Appear in 6+ sections

Data: 1,184 unique MIDDLEs, 3 sections (H/P/T).

Success criteria:
- Universal band exists (>20 MIDDLEs)
- Universal MIDDLEs span all prefix classes

#### Result Details
- Section Jaccard similarity: 9.7% (low overlap)
- Universal MIDDLEs: 27 (PASS)
- Universal coverage: All 8 prefix families (PASS)
- Shared MIDDLEs: 237 (20%)
- Exclusive MIDDLEs: 947 (80%)

#### Interpretation
A favors comparability over specificity—same behavioral classes, different local vocabulary. The 27 universal MIDDLEs provide a "comparability window" allowing cross-section reference despite 80% section-exclusive vocabulary.

#### Limitations
Does not explain why these specific 27 MIDDLEs are universal. May reflect fundamental discriminations vs. section-specific variants.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

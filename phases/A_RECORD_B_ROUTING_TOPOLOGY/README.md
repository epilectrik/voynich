# A_RECORD_B_ROUTING_TOPOLOGY Phase

## Objective

Test whether the A->AZC->B pipeline creates genuine operational differentiation. Does the manuscript function as a conditional reference system where different A-records route to different B-program subsets?

## Key Findings

### 1. C502 Token-Filtering Model Validated

| Test | Result | Interpretation |
|------|--------|----------------|
| T7: Model reconciliation | **C502 VALIDATED** | Token filtering is correct model |
| T7: Aggregation direction | **+4.45x survival** | Line->Folio: 11.2% -> 50.0% |
| T1-T4: Routing topology | **Continuous** | No discrete categories (sil=0.124) |

### 2. RI Three-Tier Structure Discovered

| Tier | Rate | Function |
|------|------|----------|
| Singletons | 95.3% | Unique situation identifiers |
| Position-locked | ~4% | Repeat within fixed position class |
| **Linkers** | 0.6% | Bridge FINAL->INITIAL across folios |

### 3. RI Linker Network Discovered

**4 RI tokens create 12 directed links connecting 12 folios:**

```
                     cthody
    f21r, f53v, f54r, f87r, f89v1 -----> f93v (COLLECTOR: 5 inputs)

                      ctho
    f27r, f30v, f42r, f93r ------------> f32r (4 inputs)
```

- **66.7% forward flow** (earlier folio -> later folio)
- **75% ct-prefix** in linkers (cthody, ctho, ctheody)
- **f93v is major hub** receiving 5 inputs

---

## Critical Clarification: Two Competing Models

**MODEL 1 - C502 Token Filtering (CORRECT):**
- A-record PP MIDDLEs define what's ALLOWED in B
- More PP = MORE B tokens survive filtering
- Line: 11.2% survival, Paragraph: 31.8%, Folio: 50.0%
- Aggregation HELPS usability

**MODEL 2 - Subset Viability (WRONG QUESTION):**
- Tests if B-folio CONTAINS all A-unit PP MIDDLEs
- More PP = STRICTER requirements = fewer viable folios
- This is NOT how the system works

T1-T4 inadvertently tested the wrong model. T7 reconciles this.

---

## Detailed Results

### T7: Model Reconciliation (DECISIVE)

| Aggregation Level | Mean PP | C502 Survival | T6 Viability |
|-------------------|---------|---------------|--------------|
| Single Line | 5.8 | **11.2%** | 15.3 folios |
| Paragraph | 20.2 | **31.8%** | 1.6 folios |
| Full A-Folio | 38.9 | **50.0%** | 0.0 folios |

**C502 Model:** PP -> Survival rho = +0.734 to +0.862 (MORE PP = MORE survival)

### T8-T9: Repetition Analysis

| Finding | Value | Interpretation |
|---------|-------|----------------|
| PP repetition | 100% | Only PP repeats within paragraphs |
| RI repetition | 0% | RI never repeats (identity-like) |
| daiin dominance | 22% | Control loop trigger encodes cycle count? |
| Position bias | 0.675 | Repeats are late-biased |

### T10-T15: RI Structure Analysis

| Finding | Value | Interpretation |
|---------|-------|----------------|
| RI per paragraph | 2.5 mean | Consistent RI density |
| INITIAL/FINAL Jaccard | 0.010 | Different vocabularies |
| First-line concentration | 1.85x | RI clusters in paragraph header |
| Folio-level structure | 1.03x | No structure at folio level |

### T16: RI-FL Correlation Test

**No correlation** between RI position and FL state encoding:
- RI MIDDLEs have ZERO overlap with FL MIDDLEs
- INITIAL RI doesn't use more 'i' (early marker)
- FINAL RI doesn't use more 'y' (late marker)
- RI encodes something orthogonal to material state

### T17-T18: RI Linker Discovery

**Three-tier population:**
- Singletons: 674 (95.3%)
- Position-locked repeaters: 29 (~4%)
- Linkers: 4 (0.6%)

**Link network properties:**
- 12 directed links connecting 12 folios
- 66.7% forward flow (to later folios)
- Mean distance: +6.6 folios
- Hub structure: f93v (5 inputs), f32r (4 inputs)

**Linker morphology:**
- 75% ct-prefix (cthody, ctho, ctheody)
- All ct-linkers share 'ho/heo' MIDDLE
- ct-prefix may mark "linkable output" tokens

---

## Interpretation

### The Correct A->B Model

A-record PP MIDDLEs function as **vocabulary allowance lists**, not requirement lists:

1. **A record specifies allowed MIDDLEs** - any B token whose MIDDLE appears in A's PP set is LEGAL
2. **Aggregation expands allowances** - pooling A records (line -> paragraph -> folio) INCREASES legal vocabulary
3. **Usability improves with aggregation** - 11.2% -> 31.8% -> 50.0% token survival

### Paragraph as Operational Unit

The gallows-initial "paragraph" structure is validated as the operational record size:
- Paragraphs provide **2.8x better token survival** than single lines
- RI shows internal structure ONLY at paragraph level (1.85x first-line concentration)
- No internal structure visible at folio level (1.03x ratio)

### RI Functional Bifurcation

RI tokens serve distinct roles based on position:

```
PARAGRAPH STRUCTURE:
  INITIAL RI: "Input" markers (po-, do- prefixes)
  PP, PP, PP: Operational vocabulary (can repeat)
  FINAL RI:   "Output" markers (ch-, ct- prefixes)
```

The 4 linker tokens bridge records: a FINAL RI in one paragraph becomes an INITIAL RI in another, creating a **progressive dependency chain**.

### Network Interpretation (Tier 3)

**Convergent topology confirmed:** Each linker appears as INITIAL in exactly ONE folio but as FINAL in MULTIPLE folios. This is many-to-one, not one-to-many.

**Two alternative interpretations (cannot distinguish structurally):**

| Model | Meaning | Physical Analog |
|-------|---------|-----------------|
| **AND (aggregation)** | f93v requires ALL 5 conditions satisfied | Compound needing 5 ingredients |
| **OR (alternatives)** | f93v accepts ANY of the 5 as valid input | 5 equivalent suppliers |

Both fit the topology equally well. The ambiguity may be deliberate - a compact encoding where practitioners know which logic applies from context.

**Structural facts (Tier 2):**
- f93v receives 5 inputs (major hub)
- Forward bias (66.7%) - earlier folios feed later folios
- Sparse connectivity - most records are self-contained
- ct-prefix dominance (75%) - morphological marker for linkable outputs

---

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C824 | A-Record Filtering Mechanism | 81.3% filtering (confirms C502) |
| C825 | Continuous Not Discrete Routing | Silhouette=0.124, no discrete clusters |
| C826 | Token Filtering Model Validation | C502 CORRECT: more PP = more survival (+0.734 rho) |
| C827 | Paragraph Operational Unit | Gallows-initial paragraphs: 31.8% survival, 2.8x better than lines |
| C828 | PP Repetition Exclusivity | 100% PP, 0% RI within-line repeats (p=2.64e-07) |
| C829 | daiin Repetition Dominance | 22% of all repeats; CC trigger encodes cycle count? |
| C830 | Repetition Position Bias | Late-biased (0.675); FINAL 12x higher than INITIAL |
| C831 | RI Three-Tier Population Structure | Singletons 95.3%, position-locked ~4%, linkers 0.6% |
| C832 | Initial/Final RI Vocabulary Separation | Jaccard=0.010; only 4 words overlap |
| C833 | RI First-Line Concentration | 1.85x in paragraph first line; validates paragraph unit |
| C834 | Paragraph Granularity Validation | RI structure visible ONLY at paragraph level |
| C835 | RI Linker Mechanism | 4 tokens, 12 links, 12 folios; 66.7% forward flow |
| C836 | RI Linker ct-Prefix Signature | 75% ct-prefix; may mark linkable outputs |
| C837 | ct-ho Linker Morphological Signature | 75% ct + 75% h-MIDDLE = 12-15x enrichment |
| C838 | qo-Linker Exception | qokoiiin uses different mechanism (qo-koi) |
| C839 | RI Input-Output Morphological Asymmetry | 12+ INPUT markers vs 5 OUTPUT markers |

## Constraints Validated

| # | Status | Finding |
|---|--------|---------|
| C502 | CONFIRMED | Token filtering is correct A->B mechanism |
| C693 | CONFIRMED | Aggregation DOES help usability under C502 model |
| C738 | CONFIRMED | Union of A folios increases coverage |

---

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| t1_viability_profiles.py | Build survivor sets | 81.3% filtering |
| t2_profile_clustering.py | Cluster A-records | sil=0.124 (poor) |
| t3_pp_breadth_prediction.py | PP->viability correlation | rho=-0.439 (subset model) |
| t4_bestmatch_specificity.py | Routing lift | 82.9% >2x lift |
| t5_routing_synthesis.py | Combine findings | 2/4 hypotheses |
| t6_aggregation_levels.py | Test aggregation | Subset model paradox |
| t7_model_reconciliation.py | **DECISIVE** | C502 validated, +4.45x aggregation effect |
| t8_repetition_boundary.py | Test gallows reset | Gallows lines 1.58x lower repeat rate |
| t9_repeat_function.py | Analyze repeat tokens | 100% PP, daiin 22%, late-biased |
| t10_ri_per_paragraph.py | RI density | Mean 2.5 RI per paragraph |
| t11_ri_ht_comparison.py | RI vs HT structure | 3/5 similar, partial analogy |
| t12_ri_cooccurrence.py | RI sharing | 95.3% singletons, 4.7% shared |
| t13_ri_position.py | RI positional rules | Bimodal: INITIAL 25%, FINAL 31% |
| t14_ri_initial_vs_final.py | INITIAL vs FINAL | Jaccard=0.010, different vocabularies |
| t15_granularity_validation.py | Validate paragraph size | 1.85x first-line, 1.03x folio-level |
| t16_ri_fl_correlation.py | RI-FL relationship | No correlation, orthogonal systems |
| t17_ri_repeater_position.py | Repeater positions | 4 linkers found |
| t18_ri_link_network.py | **DISCOVERY** | 12 links, 66.7% forward, ct-prefix |
| t19_input_output_morphology.py | INPUT/OUTPUT markers | 12+ INPUT, 5 OUTPUT; -ry = OUTPUT |
| t20_linker_morphology.py | **ct-ho SIGNATURE** | Linkers are 75% ct + 75% h-MIDDLE |

---

## Dependencies

- C502 (~80% filtering)
- C689 (97.6% unique survivor sets)
- C734-C739 (A-B coverage architecture)
- C498 (RI definition)

## Data Sources

- `scripts/voynich.py` (Transcript, Morphology)
- `phases/A_RECORD_B_FILTERING/` (prior work)

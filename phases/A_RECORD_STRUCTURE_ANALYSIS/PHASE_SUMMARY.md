# Phase: A_RECORD_STRUCTURE_ANALYSIS

**Date:** 2026-01-20
**Status:** COMPLETE
**Scope:** Currier A records, RI/PP token structure

---

## Summary

This phase investigated the internal structure of Currier A records using the registry-internal (RI) vs pipeline-participating (PP) token distinction established in C498. We discovered **RI closure tokens** — the missing complementary half of A's structural punctuation, orthogonal to the already-known DA articulation (C422).

Key finding: RI tokens show line-final **positional preference** (29.5% vs 16.8% expected) with near-disjoint opener/closer vocabularies (Jaccard 0.072). However, this is **ergonomic bias**, not grammar — C234 (POSITION_FREE) remains intact. The 87% singleton rate among closers indicates they provide instance-specific discrimination, not just generic termination.

**Outcome:** Tier 3 characterization block (C498-CHAR-A-CLOSURE) added to C498.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total RI MIDDLEs | 349 (56.6% of A types) |
| RI token instances | 483 (5.3% of A tokens) |
| Lines with any RI | 26.1% |
| Mean RI per line | 0.31 |
| RI line-final bias | 29.5% (vs 16.8% expected) |
| Opener/closer Jaccard | 0.072 (near-disjoint) |

---

## Part 1: Positional Signal Investigation

### Priority 1: Line-Final Predecessors

**Question:** What precedes line-final RI tokens?

**Results:**
- 140 line-final RI tokens across 77 folios
- **95.7%** preceded by PP tokens (not RI)
- Predecessor PREFIX distribution matches general A distribution
- 58% of predecessors have EMPTY MIDDLE (prefix-only tokens)

**Interpretation:** Line-final RI follows normal PP content. The closer is a punctuation-like element, not a content modifier.

### Priority 2: First-Line Multi-RI Propagation

**Question:** Do first-line multi-RI entries set up vocabulary for later lines?

**Results:**
- 14 folios have multi-RI on first line
- **0% propagation rate** (no RI types from line 0 reappear later)
- Control rate: 1.77% (random PP types do propagate)

**Interpretation:** First-line RI doesn't function as "headers" that establish vocabulary. RI tokens are isolated to their lines.

### Priority 3: Opener vs Closer Vocabulary

**Question:** Are line-initial and line-final RI the same vocabulary?

**Results:**
- Line-initial RI types: 82 MIDDLEs (61 exclusive)
- Line-final RI types: 111 MIDDLEs (84 exclusive)
- Overlap: 13 MIDDLEs
- **Jaccard similarity: 0.072** (near-disjoint)

**Interpretation:** RI has positional sub-roles. Openers and closers are almost entirely different vocabularies.

### Priority 4: Pure-RI Lines

**Results:**
- 9 lines are 100% RI tokens
- All are 1-token or 3-token lines
- All use folio-unique MIDDLEs
- Example: f99v.0 = [otaramy, okoldody, darolaly] (3 RI tokens)

**Interpretation:** Pure-RI lines are rare single-token annotations or short special entries.

---

## Part 2: Non-Closer RI Investigation

The expert advisor clarified that the "positional grammar" interpretation only applies to line-final closers (84 MIDDLEs). The remaining 265 RI MIDDLEs required separate investigation.

### RI Positional Classification

| Category | MIDDLE Types | Token Instances |
|----------|--------------|-----------------|
| Opener RI (pos 0) | 90 | 91 |
| Closer RI (last pos) | 111 | 140 |
| Middle-position RI | 191 | 252 |
| **Non-closer RI** | **238** | **343** |
| Pure openers only | 69 | - |
| Pure middle only | 161 | - |

### Test A: MIDDLE Incompatibility Participation

**Question:** Do non-closer RI MIDDLEs participate in the 95.7% incompatibility rate?

**Results:**
- Non-closer RI in incompatibility graph: 30 MIDDLEs
- Closer RI in incompatibility graph: 18 MIDDLEs
- Both show low illegal pair counts (~0.1 mean)

**Note:** The incompatibility analysis was AZC-only. Most RI MIDDLEs never reach AZC, so they don't appear in the incompatibility graph.

### Test B: AZC Participation

**Question:** Do non-closer RI MIDDLEs appear in AZC positions?

**Results:**
- Non-closer RI in AZC: **18 MIDDLEs** (7.6% of non-closer RI)
- Closer RI in AZC: **13 MIDDLEs** (11.7% of closer RI)

**Non-closer RI MIDDLEs in AZC:**
```
chy, echo, echod, eeee, eeet, eeoa, eoda, eokeo, eto, eyd,
iid, lol, oka, oldo, ols, opcho, otee, oteo
```

**Placement distribution (non-closer):**
```
C: 8, Y: 5, R2: 5, R: 3, P: 3, R1: 3, R3: 2, O: 1, S: 1, S1: 1
```

**Interpretation:** Non-closer RI that reaches AZC uses diverse placement codes (C, Y, R-series). This suggests non-closer RI that participates in AZC may carry content (not just structural markers).

### Test C: Opener-Closer Pairing

**Question:** When a line has both opener and closer RI, are they correlated?

**Results:**
- Lines with both: **10** (0.6% of lines)
- Distinct opener-closer pairs: **10** (all unique)
- Same MIDDLE as both opener and closer: **0**

**Examples:**
```
f21r.4: [pchofychy] ... [tolchory]
f36v.10: [ykchotchy] ... [daiild]
f87r.2: [dcheeckhos] ... [cthodal]
```

**Interpretation:** No evidence of structured opener-closer pairing. When both occur, they are independent.

### Test D: Middle-Position Behavior

**Question:** Are middle-position RI tokens like DA articulation or content?

**Results:**
- Token instances: 252 (52% of all RI tokens)
- Distinct MIDDLEs: 191
- Top MIDDLE: `ho` (31 instances)
- PREFIX concentration: Top 3 = 62.3% (ct, ch, qo)
- Folio spread: 88 (widespread)

**Position within middle zone:**
```
inner: 125 (50%)
pos_1 (right after opener): 77 (31%)
pos_-2 (right before closer): 50 (20%)
```

**Interpretation:** Middle-position RI is dominated by `ho`-family MIDDLEs (ho, heo, hod, heod). These favor the ct/ch/qo PREFIX families. The 62.3% PREFIX concentration suggests a functional vocabulary, not random noise.

---

## Synthesis: RI Closure Characterization

### Key Finding: Two Distinct Structural Mechanisms

This phase discovered the **missing complementary half** of Currier A's structural punctuation:

| Layer | Mechanism | Scope | Constraint |
|-------|-----------|-------|------------|
| **Internal segmentation** | DA articulation | Within a record | C422 (existing) |
| **Record termination** | RI closure MIDDLEs | End of a record | NEW characterization |

These are **orthogonal mechanisms** operating at different structural levels:
- **DA** tells you how the bundle is structured internally (like a comma)
- **RI closers** tell you that the bundle is complete (like a period)

But RI closers are periods that often need to be **unique** — because what matters is not just that something ended, but that **it ended as *this* and not anything else**.

### Closer Frequency Analysis

| Metric | Value |
|--------|-------|
| Total closer tokens | 148 |
| Distinct closer MIDDLEs | 119 |
| Average uses per MIDDLE | 1.24 |
| **Singletons (used once)** | **104 (87.4%)** |

**Core reusable kernel** (15 MIDDLEs with -o/-od/-ol morphology):
- `ho` (10x), `hod` (4x), `hol` (3x), `mo` (3x), `oro` (3x), `tod` (3x)

**Singleton tail** (104 MIDDLEs): Instance-specific terminators providing record-level discrimination.

### Relationship to C234 (POSITION_FREE)

**This does NOT contradict C234.** The finding is **ergonomic bias**, not grammar:
- RI closers **prefer** line-final position
- But **can appear elsewhere**
- And **do not constrain what can follow** (nothing follows line-final)

C234 remains true: position does not determine legality, grammar, or prediction. Certain functional subclasses (DA articulators, RI closers) exhibit positional preferences for human interface stability without imposing positional constraints.

### Tier 3 Characterization (NOT Tier 2)

This is a **distributional regularity with explanatory coherence**, not a structural necessity. The Tier 2 test:

> *Would Currier A still satisfy all structural contracts if RI closers were less singleton-heavy or slightly less end-biased?*

**Answer: Yes.** Therefore this is Tier 3, not Tier 2.

### Characterization Block

> **C498-CHAR-A-CLOSURE (Tier 3):**
> A subset of registry-internal MIDDLEs functions as record-terminal closure discriminators. These tokens show strong line-final preference (29.5% vs 16.8% expected), a small reusable kernel (ho, hod, hol, mo, oro, tod), and a large singleton tail (87%) providing instance-specific separation. They serve as cognitive closure anchors rather than internal articulators and do not affect legality, grammar, or downstream propagation. Near-disjoint from opener vocabulary (Jaccard 0.072).

| Position | MIDDLEs | Character | Interpretation |
|----------|---------|-----------|----------------|
| Closer (line-final) | 119 | 15 core + 104 singletons | Record completion + instance discrimination |
| Opener (line-initial) | 90 | Widespread | Remains open |
| Middle | 191 | `ho`-family dominated | Remains open |

---

## Files Produced

```
phases/A_RECORD_STRUCTURE_ANALYSIS/
|-- scripts/
|   |-- ri_pp_structure_v2.py
|   |-- ri_signal_investigation.py
|   |-- ri_position_analysis.py
|   |-- analyze_multi_ri.py
|   |-- check_ri_adjacency.py
|   |-- noncloser_ri_investigation.py
|   |-- closer_frequency.py
|   |-- closer_folio_analysis.py
|-- results/
|   |-- ri_pp_structure_v2.json
|   |-- ri_signal_investigation.json
|   |-- noncloser_ri_investigation.json
|-- PHASE_SUMMARY.md
```

---

## Constraint Compliance

| Constraint | Status |
|------------|--------|
| C233 (LINE_ATOMIC) | COMPATIBLE - analysis respects line boundaries |
| C234 (POSITION_FREE) | COMPATIBLE - ergonomic bias, not grammar |
| C422 (DA Articulation) | COMPLEMENTARY - different structural level |
| C498 (RI Vocabulary Track) | CHARACTERIZED - Tier 3 closure block added |
| C475 (MIDDLE Incompatibility) | COMPATIBLE - RI participates where it reaches AZC |
| Semantic ceiling | SAFE - structural patterns only, no semantic claims |

---

## Part 3: DA Segmentation Through RI/PP Lens

Following the RI closure finding, we investigated whether DA articulation (C422) reveals additional RI/PP structure beyond what PREFIX alone explains.

### Pre-Check: PREFIX × RI/PP Association

**Question:** Does PREFIX already explain RI/PP distribution?

**Results:**
- Chi-square highly significant (p < 10⁻⁵⁰)
- Cramér's V = 0.183 (MODERATE association)
- Only 22.2% of RI tokens in RI-enriched prefixes
- 77.8% of RI tokens use balanced/PP-dominant prefixes

**Interpretation:** PREFIX partially predicts RI/PP at token level, but most RI tokens are not in RI-enriched prefixes. Proceed with segment analysis.

### Phase 1: Segment-Level RI/PP Composition

**Question:** Do DA-segmented blocks show RI/PP stratification?

**Results:**
- Lines with DA tokens: 740 (47% of A lines)
- Segments analyzed: 416 (with 2+ tokens)
- Cohen's d = 0.323 (weak, below 0.5 threshold)
- P-value = 0.123 (not significant)

**Distribution:**
- 87% of segments have <5% RI tokens (PP-dominated)
- 8% of segments have >20% RI tokens (bimodal tail)

**Finding:** Weak stratification effect. DA segments don't strongly stratify by RI/PP composition.

### Phase 2: Within-Segment RI Position

**Question:** Do RI tokens prefer specific positions within DA segments?

**Results:**

| Position | RI Rate | vs Overall (5.29%) |
|----------|---------|-------------------|
| OPENER | 5.36% | 1.01× (baseline) |
| INTERIOR | 4.55% | 0.86× (depleted) |
| CLOSER | 7.57% | **1.43×** (enriched) |

- Chi-square p < 0.0001 (significant)
- Opener vs Closer: p = 0.024 (significant)
- Boundary vs Interior odds ratio: 1.45×

**Comparison to Line-Level:**

| Scale | RI Closer Preference |
|-------|---------------------|
| Line-final (C498-CHAR-A-CLOSURE) | 1.76× |
| Segment-final (this analysis) | 1.43× |

**Finding:** RI closer preference operates hierarchically — stronger at line level (1.76×), weaker at segment level (1.43×). Consistent with nested closure structure.

### Phase 3: Segment-Type Clustering

**Question:** Are RI-RICH segments a distinct structural type?

**Profile Distribution:**

| Profile | Count | % | Definition |
|---------|-------|---|------------|
| PP_PURE | 1337 | 79.0% | No RI tokens |
| RI_MODERATE | 246 | 14.5% | 10-30% RI |
| RI_RICH | 104 | **6.1%** | >30% RI |

**Key Tests:**

| Test | Result | Interpretation |
|------|--------|----------------|
| Position × Profile | p=0.0495 | Position predicts RI profile |
| PREFIX × Profile | p=0.151 | PREFIX does NOT predict |
| Binomial test | 5.0× expected | RI-RICH not random |
| PREFIX coherence | p<0.0001 | RI-RICH more coherent |

**RI-RICH Segment Characteristics:**
- Short (mean 3.3 tokens)
- PREFIX-coherent (diversity 2.66 vs 3.44)
- Terminal-preferring (78.8% are "only" or "last" segments)
- 5× more common than binomial chance

**Critical Finding:** PREFIX does NOT predict segment RI profile (p=0.151), even though PREFIX does predict token-level RI/PP (V=0.183). This means RI concentration is a **segment-level positional phenomenon**, not a PREFIX vocabulary property.

### Synthesis: Hierarchical RI Closure

The investigation reveals **two orthogonal organizational axes** in Currier A:

1. **PREFIX families** — what domain/material-class is being discriminated
2. **RI closure bursts** — where fine-grained instance discrimination happens

RI-RICH segments are **closure units** — short, PREFIX-coherent, terminal-preferring — that can involve any PREFIX family. The registry "gets specific" at closure boundaries, marking variants that B programs never need to distinguish.

**Hierarchical Model:**

```
Line structure:
  [PP-heavy segment] DA [PP-heavy segment] DA [RI-RICH closure unit]
                                              └── Short, coherent,
                                                  instance-discriminating

Within segments:
  [opener] [interior...] [closer]
    5.4%      4.5%        7.6% RI
```

### Characterization Block

> **C498-CHAR-A-SEGMENT (Tier 3):**
> RI closer preference operates hierarchically: 1.76× at line-final, 1.43× at segment-final. RI-RICH segments (>30% RI, 6.1% of segments) are structurally distinct: short (mean 3.3 tokens), PREFIX-coherent (diversity 2.66 vs 3.44), and terminal-preferring (78.8% "only" or "last"). PREFIX does NOT predict segment RI profile (p=0.151), indicating RI concentration is a positional-closure phenomenon independent of PREFIX vocabulary.

---

## Updated Files Produced

```
phases/A_RECORD_STRUCTURE_ANALYSIS/
├── scripts/
│   ├── ri_pp_structure_v2.py
│   ├── ri_signal_investigation.py
│   ├── ri_position_analysis.py
│   ├── analyze_multi_ri.py
│   ├── check_ri_adjacency.py
│   ├── noncloser_ri_investigation.py
│   ├── closer_frequency.py
│   ├── closer_folio_analysis.py
│   ├── prefix_ri_pp_crosstab.py        # Pre-check
│   ├── da_segment_ri_pp_composition.py  # Phase 1
│   ├── da_segment_ri_position.py        # Phase 2
│   └── da_segment_clustering.py         # Phase 3
├── results/
│   ├── ri_pp_structure_v2.json
│   ├── ri_signal_investigation.json
│   ├── noncloser_ri_investigation.json
│   ├── prefix_ri_pp_crosstab.json
│   ├── da_segment_ri_pp_composition.json
│   ├── da_segment_ri_position.json
│   └── da_segment_clustering.json
└── PHASE_SUMMARY.md
```

---

---

## Part 4: PP Vocabulary Bifurcation (C498.a)

Following the RI closure characterizations (Parts 1-3), we investigated the internal structure of the "Pipeline-Participating" (PP) vocabulary track.

### Question

Do all 268 A∩B shared MIDDLEs actually participate in the A→AZC→B pipeline?

### Investigation Path

#### Step 1: PP MIDDLE Frequency Distribution

| Category | Count | % of PP | Token Coverage |
|----------|-------|---------|----------------|
| Singletons (freq=1) | 98 | 36.6% | 1.1% |
| Low (2-5) | 72 | 26.9% | 3.0% |
| Mid (6-50) | 68 | 25.4% | 16.6% |
| High (>50) | 30 | 11.2% | 79.3% |

**Finding:** Top 10 MIDDLEs cover 80.1% of PP usage. `_EMPTY_` alone = 58.5%.

#### Step 2: AZC Propagation Trace

Traced all 268 PP MIDDLEs through A → AZC → B:

| AZC Category | Count | % of PP | Mean B Folio Spread |
|--------------|-------|---------|---------------------|
| No AZC presence | **114** | **42.5%** | 4.0 folios |
| Restricted (1-2 AZC folios) | 92 | 34.3% | 6.8 folios |
| Moderate (3-10 AZC folios) | 45 | 16.8% | 20.1 folios |
| Universal (10+ AZC folios) | 17 | 6.3% | 48.7 folios |

**Critical Finding:** 114 PP MIDDLEs (42.5%) appear in A and B but NEVER in any AZC folio.

#### Step 3: Bypass MIDDLE Characteristics

The 114 "bypass" MIDDLEs show B-heavy frequency ratios:

| MIDDLE | A count | B count | Ratio |
|--------|---------|---------|-------|
| `eck` | 2 | 85 | 42× more in B |
| `ect` | 2 | 46 | 23× more in B |
| `keed` | 1 | 29 | 29× more in B |
| `pch` | 2 | 25 | 12× more in B |

**A vs B balance:**
- B-heavy (B > 2×A): 67 MIDDLEs (58.8%)
- A-heavy (A > 2×B): 12 MIDDLEs (10.5%)
- Balanced: 35 MIDDLEs (30.7%)

### Key Insight

The B-heavy ratios indicate these are NOT A vocabulary that "selects" B destinations. They are **B-native operational vocabulary** with incidental A presence. Causality runs B→A (shared operational domain), not A→B (pipeline transmission).

### Complete A MIDDLE Hierarchy

```
A MIDDLEs (617 total)
├── RI: Registry-Internal (349, 56.6%)
│     A-exclusive, instance discrimination, folio-localized
│
└── Shared with B (268, 43.4%)
    ├── AZC-Mediated (154, 25.0% of A vocabulary)
    │     A→AZC→B constraint propagation
    │     ├── Universal (17) - 10+ AZC folios
    │     ├── Moderate (45) - 3-10 AZC folios
    │     └── Restricted (92) - 1-2 AZC folios
    │
    └── B-Native Overlap (114, 18.5% of A vocabulary)
          Zero AZC presence, B-dominant frequency
          Execution-layer vocabulary with incidental A appearance
```

### Architectural Implications

1. **Pipeline scope narrower than assumed:** Only 154 (25% of A vocabulary) genuinely participate in A→AZC→B constraint propagation
2. **C468-C470 preserved but scoped:** Constraint inheritance applies only to AZC-Mediated subclass
3. **Reinforces C384:** No entry-level A-B coupling — B-Native Overlap demonstrates statistical, not referential, sharing

### Terminology Correction

The original "Pipeline-Participating" label is misleading:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

### External Expert Validation

The finding was reviewed by a domain expert:

> "This is a solid, architecture-strengthening refinement. It sharpens C498, clarifies pipeline scope, and removes an implicit overgeneralization — without reopening any closed tier."

**Verdict:** C498.a added as Tier 2 refinement (not independent constraint).

### Constraint Added

> **C498.a (Tier 2 Refinement):**
> The A∩B shared MIDDLE vocabulary comprises two structurally distinct subclasses: (i) AZC-mediated pipeline MIDDLEs (154), which propagate A-origin discrimination constraints through AZC into B; and (ii) B-native overlap MIDDLEs (114), which appear in both A and B but do not participate in AZC mediation and function as execution-layer vocabulary with incidental A presence. Constraint inheritance (C468-C470) applies only to the former subclass.

---

## Final Files Produced

```
phases/A_RECORD_STRUCTURE_ANALYSIS/
├── scripts/
│   ├── ri_pp_structure_v2.py
│   ├── ri_signal_investigation.py
│   ├── ri_position_analysis.py
│   ├── analyze_multi_ri.py
│   ├── check_ri_adjacency.py
│   ├── noncloser_ri_investigation.py
│   ├── closer_frequency.py
│   ├── closer_folio_analysis.py
│   ├── prefix_ri_pp_crosstab.py
│   ├── da_segment_ri_pp_composition.py
│   ├── da_segment_ri_position.py
│   ├── da_segment_clustering.py
│   ├── pp_middle_frequency.py          # Part 4
│   ├── pp_singleton_analysis.py        # Part 4
│   ├── pp_singleton_b_frequency.py     # Part 4
│   ├── pp_middle_propagation.py        # Part 4
│   └── pp_bypass_azc.py                # Part 4
├── results/
│   ├── ri_pp_structure_v2.json
│   ├── ri_signal_investigation.json
│   ├── noncloser_ri_investigation.json
│   ├── prefix_ri_pp_crosstab.json
│   ├── da_segment_ri_pp_composition.json
│   ├── da_segment_ri_position.json
│   ├── da_segment_clustering.json
│   └── pp_middle_propagation.json      # Part 4
└── PHASE_SUMMARY.md
```

---

## Phase Status: COMPLETE

All four parts of A_RECORD_STRUCTURE_ANALYSIS have been completed:

| Part | Topic | Outcome |
|------|-------|---------|
| 1 | RI Positional Signal | C498-CHAR-A-CLOSURE (Tier 3) |
| 2 | Non-Closer RI | Opener/middle characterization |
| 3 | DA Segmentation | C498-CHAR-A-SEGMENT (Tier 3) |
| 4 | PP Bifurcation | **C498.a (Tier 2 Refinement)** |

The phase discovered both a distributional regularity (RI closure behavior) and an architectural refinement (PP/BN bifurcation) that sharpens the pipeline model.

## Open Questions for Future Phases

1. **What are `ho`-family MIDDLEs in middle position?**
   - ho (31), heo (8), hod (5), heod (3) dominate middle-position RI
   - Are they articulation markers? Content qualifiers?

2. **Do the 18 AZC-participating non-closer RI have special semantics?**
   - They use C, Y, R-series placements
   - Might bridge A-internal and AZC roles

3. **What distinguishes the 104 RI-RICH segments?**
   - Are they a specific entry subtype?
   - Do they correlate with folio sections or manuscript regions?

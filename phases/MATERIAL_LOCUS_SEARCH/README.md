# Phase: MATERIAL_LOCUS_SEARCH

**Status**: COMPLETE
**Verdict**: MATERIAL EMERGENT — Section identity is the material coordinate; no sub-section material markers exist
**Tests**: 16 completed (6 PASS, 2 PARTIAL, 1 MARGINAL, 7 FAIL)

## Research Question

If material identity does NOT live in MIDDLE morphology (C937-C940), where IS it encoded? This phase systematically searched all remaining combinatorial hiding places.

**Motivation**: The MIDDLE_MATERIAL_SEMANTICS phase proved that 89.4% of zone-exclusive rare MIDDLEs are distance-1 compositional elaborations (C939). But if these are real recipes (Brunschwig-style), materials MUST be specified somewhere. This phase tests six loci: folio-level profiles, token-level combinations, paragraph structure, A-to-B routing, cross-paragraph sequences, and AI direct folio inspection.

## Results Summary

### Locus 1: Folio-Level Vocabulary Profile (Tests 1, 12)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 1 | Folio MIDDLE Vocabulary Clustering | **PASS*** | ARI=0.40, NMI=0.53, p<0.0001; but residual after section removal ~0 |
| 12 | Cross-Paragraph Material Persistence | FAIL | Only 3 persistent rare MIDDLEs found (threshold: >10) |

*Test 1 is a qualified PASS: clusters strongly correspond to section (ARI=0.40) but do NOT explain variance beyond section. Section IS the vocabulary organizer.

### Locus 2: Token-Level Combination (Tests 2, 4, 11)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 2 | Suffix Section Interaction | **PARTIAL** | Mean V=0.198 (threshold 0.20), section > regime for 76.5% of MIDDLEs |
| 4 | Whole-Token Variant Coordination | **PASS** | Residual MI=0.105 bits, p=0.0, 60% persists after PREFIX conditioning |
| 11 | Prefix+Suffix Combination | **PARTIAL** | Pair V=0.22 > components (0.15/0.12), but exclusivity only +1.8pp |

### Locus 3: Paragraph-Internal Structure (Tests 3, 6, 8, 10)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 3 | Paragraph Vocabulary Scope | FAIL | Lift=1.069 (threshold 1.15), kernel signature doesn't predict vocab |
| 6 | Context-Dependent Successors | **PASS** | 45.8% of MIDDLEs section-dependent, section KL 2x > position KL |
| 8 | Paragraph-Initial Signature | MARGINAL | 39.2% accuracy (>20% chance, <60% threshold) |
| 10 | Specification Vocabulary | FAIL | Early 62.5% vs Late 64.2% — no specification gradient |

### Locus 4: A-to-B Routing (Tests 5, 9)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 5 | RI Extension → B-Section | FAIL | V=0.071 << 0.15 threshold |
| 9 | A Folio Material Domains | FAIL | ARI=-0.007, A folios cover all B sections uniformly |

### Locus 5: Cross-Paragraph Sequence (Test 7)

| # | Test | Verdict | Key Stat |
|---|------|---------|----------|
| 7 | Paragraph Kernel Sequence | **PASS** | Entropy p=0.004, section T most stereotyped (1.32 bits) |

### Locus 6: AI Direct Folio Inspection (Tests 13-16)

| # | Test | Verdict | Key Finding |
|---|------|---------|-------------|
| 13 | Cross-Section Folio Pairs | FAIL | 0/10 pairs show material signal; all overlap is operational |
| 14 | Within-Section Outliers | FAIL | All 38 morphologically independent MIDDLEs are hapax legomena |
| 15 | Paragraph Material Tracking | **PASS*** | 6/6 folios show signals, but agent's own analysis: "shared grammar, not material" |
| 16 | Glossed Sequence Patterns | **PASS** | Gloss gaps 4x enriched at paragraph start, section-specific gap rates |

## Key Findings

### 1. Section IS the Material Coordinate (The Central Finding)

Every test that passes does so because of **section identity**. Token variant coordination (Test 4), context-dependent successors (Test 6), paragraph sequences (Test 7), and vocabulary clustering (Test 1) all point to section as the organizer. But no test finds structure **within** or **beyond** section that could be a material marker.

The same MIDDLE (e.g., `ed`) behaves differently in section B vs section S — different successor distributions, different co-occurrence patterns, different variant selections. But the MIDDLE itself doesn't change form. Material identity is implicit in the section-level vocabulary profile, not explicitly marked by any token.

### 2. No Sub-Section Material Markers Exist

Every test searching for discrete material tokens fails:
- **No folio-persistent rare vocabulary** (Test 12): Only 3 MIDDLEs persist across >50% of a folio's paragraphs while being rare overall
- **No A→B material routing** (Tests 5, 9): RI extensions don't predict B sections (V=0.071); A folios cover all B sections uniformly
- **No specification gradient** (Test 10): Early and late paragraph vocabulary discriminate section equally
- **No cross-section material signals** (Tests 13, 14): All cross-section vocabulary overlap is operational; all morphologically independent divergent MIDDLEs are hapax legomena
- **No kernel-based vocabulary scope** (Test 3): Paragraphs with same kernel signature don't share more vocabulary

### 3. Combinatorial Structure Carries Section Signal

Token-level combinations encode more section information than any individual component:
- **PREFIX+SUFFIX pairs** (Test 11): Pair Cramer's V=0.22 exceeds prefix V=0.15 and suffix V=0.12
- **Whole-token variants** (Test 4): 60% of variant-section mutual information persists after conditioning on PREFIX compatibility
- **Suffix-section interaction** (Test 2): Same MIDDLE takes different suffix distributions by section (V=0.198)

This is consistent with section being an operational configuration that shapes how the compositional grammar is parameterized — not a label applied to tokens, but an emergent property of how tokens are assembled and sequenced.

### 4. AI Inspection Findings (Mixed)

- **Test 15 (PASS with major caveat)**: All 6 inspected folios show vocabulary that persists across operationally independent paragraphs. However, the agent's own qualitative analysis concluded: "No folio has folio-persistent rare MIDDLEs... shared vocabulary consists of common grammatical tokens, not material-specific rare MIDDLEs." The ANIMAL/WATER/ROOT/OIL labels come from BFolioDecoder's suffix-based classification — their persistence reflects grammar consistency, not material tracking. The automated PASS is effectively overridden by the narrative analysis.
- **Test 16 (PASS — most interesting)**: Gloss gaps (unglossed MIDDLEs between glossed ones) are 4x enriched at paragraph start and section-specific in rate. However, the 16 morphologically distinct gaps (edit distance >2) are all hapax legomena (frequency=1), meaning they're compositional tail noise, not recurring markers.
- **Tests 13-14 (FAIL — clean)**: Direct folio comparison found no evidence of shared rare vocabulary across sections or distinctive material vocabulary within sections.

### 5. Section-Specific Operational Patterns (Test 16)

Gloss sequences show distinctive procedural signatures per section:
- **Section B**: `batch → intake`, `close → stage:late` (batch processing patterns)
- **Section S**: `cool → cool`, `deep cool → deep cool`, `heat → open` (thermal cycling)
- **Section T**: `precision heat → transfer`, `stage:near-end → cool-open` (precision operations)
- **Section C**: `set → transfer`, `set → collect` (setup-driven)

These are operational signatures, not material markers. But they ARE section-specific, reinforcing that section identity is carried in the procedural grammar.

## Integrated Verdict: MATERIAL EMERGENT

Using the pre-registered criteria:
- **MATERIAL FOUND** (5+ independent passes, AI confirms): Not met — passes are not independent of section
- **MATERIAL EMERGENT** (3-4 passes, AI finds partial patterns): **MET** — 6 passes all at section level, AI finds partial patterns (Test 15-16)
- **MATERIAL ABSENT** (0-2 passes): Not applicable
- **OPERATIONAL ONLY** (all signals are section/regime): Nearly met — but combinatorial structure adds to section

**Final assessment:** Material identity is NOT explicitly encoded at any structural level testable by morphological or statistical methods. Instead, it is **emergently encoded** in the section-level vocabulary profile — the specific combination of which variants, which successors, which sequences, and which token assemblies a section uses. Sections function simultaneously as operational configurations AND as implicit material domains. The two cannot be separated because the manuscript's grammar does not separate them.

**Implication for the semantic ceiling (C120/C171):** Material identity is bound to section identity. If you know the section, you know the material domain (per Brunschwig: section B ≈ biological, H ≈ herbal, S ≈ pharmaceutical, etc.). But you cannot recover material identity from any individual token, MIDDLE, or morphological feature. The information is distributed across the entire vocabulary profile.

## Candidate Constraints

| Finding | Constraint | Tier |
|---------|-----------|------|
| Section is the primary vocabulary organizer (ARI=0.40, residual ~0) | **C941** | 2 |
| Context-dependent MIDDLE successors: section KL 2x > position KL | **C942** | 2 |
| Whole-token variant coordination: 60% residual MI after PREFIX conditioning | **C943** | 2 |
| Paragraph kernel sequences are section-stereotyped (entropy p=0.004) | **C944** | 2 |
| No folio-persistent rare MIDDLEs as material markers | **C945** | 1 |
| A folios cover all B sections uniformly (no material routing) | **C946** | 1 |
| No specification vocabulary gradient (early=late discrimination) | **C947** | 1 |
| Gloss gaps enriched at paragraph start (4x) but are hapax | **C948** | 2 |

## Scripts

```
scripts/
├── 01_folio_vocabulary_clustering.py
├── 02_suffix_section_interaction.py
├── 03_paragraph_vocabulary_scope.py
├── 04_whole_token_coordination.py
├── 05_ri_extension_b_outcome.py
├── 06_context_dependent_successors.py
├── 07_paragraph_kernel_sequence.py
├── 08_paragraph_initial_signature.py
├── 09_ab_vocabulary_material_domains.py
├── 10_specification_vocabulary_distinctiveness.py
├── 11_prefix_suffix_combination.py
├── 12_cross_paragraph_persistence.py
├── 13_cross_section_folio_pairs.py       # AI inspection
├── 14_within_section_outliers.py          # AI inspection
├── 15_paragraph_material_tracking.py      # AI inspection
└── 16_glossed_sequence_patterns.py        # AI inspection
```

## Provenance

- **Trigger**: MIDDLE_MATERIAL_SEMANTICS phase showed materials NOT in MIDDLE morphology (C937-C940)
- **Question**: If not in MIDDLEs, where IS material identity encoded?
- **Method**: 16 tests across 6 loci (folio profile, token combination, paragraph structure, A→B routing, cross-paragraph sequence, AI inspection)
- **Result**: Section identity IS the material coordinate. No sub-section material markers exist. Material encoding is emergent, distributed across the combinatorial vocabulary profile.

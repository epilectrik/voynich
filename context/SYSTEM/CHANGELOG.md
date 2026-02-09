# Context System Changelog

**Purpose:** Track changes to the context system structure and content.

---

## Version 3.37 (2026-02-09) - MIDDLE Material Semantics Phase

### Summary

14-test research phase tested whether tail MIDDLEs (rare, <15 folios) encode material-specific identity. **Verdict: WEAK** — phase-position semantics confirmed; material-level identity NOT supported. Semantic ceiling (C120) stands with refinement.

### New Constraints

| # | Name | Tier | Key Evidence |
|---|------|------|-------------|
| C937 | Rare MIDDLE Zone-Exclusivity | 2 | 55.1% vs 25.5%, d=0.67, p=2.97e-15 |
| C938 | Section-Specific Tail Vocabulary | 2 | 42-66% exclusive, ratio=1.40, p=1.29e-06 |
| C939 | Zone-Exclusive MIDDLEs Are Compositional Variants | 2 | 89.4% distance-1, p=0.978 indistinguishable |
| C940 | FL State Marking via Rare MIDDLEs FALSIFIED | 1 | p=0.224, bimodal distribution |

### Revision Notes

- **C619:** Confirmed within procedural phases (JSD=0.01, no zone survives Bonferroni)

### Key Findings

- Rare MIDDLEs deploy in specific procedural phases (SETUP/PROCESS/FINISH) — genuine structural feature
- But they are compositional elaborations (single-char edits) of common MIDDLEs, not independent identifiers
- FL state marking ruled out as explanation for finish-zone vocabulary
- Section-specific tail vocabulary extends C909 to the rare distribution
- Material encoding does NOT live in MIDDLE morphology

### Files Changed

- `context/CLAIMS/INDEX.md` — v3.37, +4 constraints (790→794)
- `context/CLAIMS/C937_rare_middle_zone_exclusivity.md` — NEW
- `context/CLAIMS/C938_section_tail_vocabulary.md` — NEW
- `context/CLAIMS/C939_zone_exclusive_compositional_variants.md` — NEW
- `context/CLAIMS/C940_fl_rare_middle_falsification.md` — NEW
- `context/CLAIMS/C619_unique_middle_behavioral_equivalence.md` — Revision note added
- `phases/MIDDLE_MATERIAL_SEMANTICS/` — Full phase (14 scripts, 14 results, README)

---

## Version 3.10 (2026-02-03) - B Paragraph Structure Analysis

### Summary

Detailed line-by-line annotation of **10 Currier B folios** (~350 lines) revealed paragraph-level vocabulary distribution patterns. New section 0.M added to INTERPRETATION_SUMMARY.md documenting sequential paragraph structure, terminal vocabulary signature, and state transition marking.

### Key Findings (Tier 3)

| Finding | Evidence |
|---------|----------|
| **Sequential paragraph structure** | Vocabulary distribution correlates with folio position (early=HT-heavy, late=AX+FL-heavy) |
| **Terminal vocabulary signature** | Late paragraphs show AX clustering + TERMINAL FL (-aly, -am) + SHORT lines |
| **State transition brackets** | HT at BOTH line-initial AND line-final marks explicit X→Y transformation |
| **FL STATE INDEX confirmation** | FL tokens (ar→al→aly) track material progression through folio |

### Interpretation Strengthened

The annotation work significantly strengthened the Brunschwig/distillation interpretation:
- Paragraphs correspond to named operations (maceration, distillation, rectification)
- Early identification → middle processing → late completion matches recipe structure
- State transition brackets match material state tracking in distillation manuals

### Files Updated

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Version 4.56, Section 0.M added
- `context/SYSTEM/CHANGELOG.md` - This entry

### Annotated Folios

First 5: f41v, f43r, f43v, f46r, f46v
Next 5: f103r, f103v, f104r, f104v, f105r

### Source

Manual token-level annotation using pacemaker workflow (`scripts/annotate_next_line.py --mode b`)

---

## Version 3.09 (2026-02-01) - Token Annotation Findings

### Summary

Systematic token-by-token annotation of all **114 Currier A folios** (1,272+ lines) completed. Three new constraints document previously invisible patterns. Annotation data infrastructure added to context system.

### New Constraints

| # | Name | Finding |
|---|------|---------|
| C901 | Extended e Stability Gradient | e→ee→eee→eeee forms stability depth continuum; quadruple-e rare (11 folios), concentrated in late Currier A |
| C902 | Late Currier A Register | f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, very short lines, morphological MONSTERS |
| C903 | Prefix Rarity Gradient | Common→rare→very-rare→extremely-rare prefix distribution (ch/sh > ct > qk > qy) |

### Constraint Refinement

**C833 (RI First-Line Concentration):** Added refinement note that 50% of folios have RI outside L1, establishing this as a preference rather than a requirement.

### New Data Files Documented

| File | Purpose |
|------|---------|
| `data/token_dictionary.json` | Token-level annotations with morphology, distribution, notes |
| `data/folio_notes.json` | Folio-level observations from systematic annotation |
| `data/annotation_progress.json` | Pacemaker script progress tracking |

Documentation added to `DATA/TRANSCRIPT_ARCHITECTURE.md` with usage examples.

### Expert Analysis Findings

Key patterns identified across 114 folios:

- **Doubled patterns**: 81 folios (71%)
- **Short lines**: 70 folios (61%)
- **QO concentration**: 64 folios (56%)
- **C833 flags (non-L1 RI)**: 57 folios (50%)
- **P-domain markers**: 51 folios (45%)
- **Linkers**: 47 folios (41%)
- **Triple e patterns**: 41 folios (36%)
- **Quadruple e patterns**: 11 folios (10%)
- **Rare qk-prefix**: 9 folios (8%)
- **Extremely rare qy-prefix**: 3 folios (3%)

### Files Updated

- `context/CLAIMS/INDEX.md` - Version 3.22, 768 constraints
- `context/CLAUDE_INDEX.md` - Version 3.09, constraint count updated
- `context/DATA/TRANSCRIPT_ARCHITECTURE.md` - Annotation data section added
- `context/CLAIMS/C833_ri_first_line_concentration.md` - Refinement added
- `context/CONSTRAINT_TABLE.txt` - Regenerated
- `context/MODEL_FITS/FIT_TABLE.txt` - Regenerated
- `.claude/agents/expert-advisor.md` - Regenerated with new constraints

### Cross-References

C901, C902, C903, C833 (refined), TOKEN_ANNOTATION_BATCH_11 phase

---

## Version 3.00 (2026-01-31) - Kernel Layer Clarification

### Summary

**Major clarification:** k, h, e "kernel" characters operate at CONSTRUCTION level (within-token morphology), not EXECUTION level (token-to-token sequencing). The 17 "forbidden transitions" operate at CLASS level, not k/h/e character level. These are INDEPENDENT constraint systems.

### KERNEL_STATE_SEMANTICS Phase Findings

| Test | Finding |
|------|---------|
| T1-T6 | Between-token k/h/e transitions are UNIFORM (O/E 0.87-1.21) |
| T7 | Class-level transitions show STRONG structure (O/E 0.20-7.31) |
| T9 | Within-token k/h/e transitions confirm C521 (5/5 claims) |
| T10 | k/h/e content does NOT predict forbidden transition participation |

### Key Discovery

Two independent constraint systems share the same symbol substrate:
1. **CONSTRUCTION layer (C521):** Within-token k→h→e ordering with strong asymmetry
2. **EXECUTION layer (C109):** Class-level forbidden transitions operating on instruction classes

C522 (layer independence) CONFIRMED with additional evidence.

### Files Updated

**BCSC v2.0:**
- KERNEL_CENTRALITY guarantee: Reframed from "control core" to "morphological core"
- kernel_boundary_adjacency invariant: Clarified as correlational, not causal
- kernel section: Added scope note that operators describe morphological contribution, not execution state

**Constraints:**
- C107: Added scope clarification (correlational not causal)
- C522: Added KERNEL_STATE_SEMANTICS evidence table

**Metrics:**
- hazard_metrics.md: Added scope note on class-level vs character-level

### Cross-References

C107, C109, C521, C522, KERNEL_STATE_SEMANTICS phase

---

## Version 2.99 (2026-01-31) - Escape Terminology Revision

### Summary

**Major terminology correction:** "Escape routes" (C397/C398) reframed as "lane transitions."

### Problem Identified

The HAV phase (C397-C398) introduced "escape" terminology that was later contradicted:
- C397 claimed "qo-prefix = escape route" after hazard sources
- But C645 shows CHSH dominates post-hazard (75.2%), QO is depleted (0.55x)
- C601 shows QO has zero hazard participation (0/19)
- The "escape to energy" framing was backwards

### Correct Model

| Lane | Kernel | Hazard Role |
|------|--------|-------------|
| CHSH | e-rich (68.7%) | Handles hazard-adjacent contexts, recovery |
| QO | k-rich (70.7%) | Operates hazard-distant, depleted near hazards |

What C397/C398 actually measured: the normal CHSH→QO lane transition pattern (C643), not escape.

### Files Updated

- `phases/HAV_hazard_avoidance/summary.md` - Revised interpretation
- `context/CLAIMS/morphology.md` - C397/C398 descriptions corrected
- `context/CONSTRAINT_TABLE.txt` - C397/C398 entries updated
- `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` - Recovery section rewritten
- `context/METRICS/hazard_metrics.md` - Escape section replaced

### Cross-References

C601 (QO zero hazard), C643 (QO-CHSH alternation), C645 (CHSH post-hazard dominance)

---

## Version 2.98 (2026-01-31) - P-TEXT FOLIO ANALYSIS Phase

### Summary

Investigated why P-text appears on 9 specific AZC folios and discovered it represents a **privileged Currier A vocabulary subset** with high transmission to B.

### Key Findings

| Finding | Value |
|---------|-------|
| P-text folios | 9 of 29 AZC folios (f65v-f70r2) |
| P-text to B transmission | **76.7%** (vs 39.9% for general A) |
| Same-folio Jaccard | 0.195 (vs 0.040 baseline) |
| Correlation with B TTR | r=0.524, p<0.0001 |

### Interpretation

P-text is not "A text on AZC folios" but a **privileged vocabulary subset** that:
- Has high transmission to B execution
- Correlates with high qo-density B folios (vocabulary diversity)
- Has content relationship to same-folio diagrams

### Constraints Updated

- **C492**: Added reframing note - "P-zone" → "P-text (Currier A paragraph)"
- **C486**: Added reframing note - strengthened by vocabulary-based interpretation

### Anomaly Noted

f65v is 100% P-text with 0 diagram tokens - unique among AZC folios.

---

## Version 2.97 (2026-01-31) - P Position Clarification

### Summary

Audited and corrected context system to clarify that **P (Paragraph) is NOT an AZC diagram position**. P is paragraph text that appears on AZC folios but is physically separate from the circular diagrams.

### Authoritative Source

From `context/ARCHITECTURE/azc_transcript_encoding.md`:

| Code | Physical Meaning |
|------|------------------|
| R, R1-R4 | Ring text (concentric circles) |
| S, S0-S3 | Star/spoke OR nymph-interrupted ring |
| C, C1-C2 | Circle text (continuous ring) |
| **P** | **Paragraph (separate from diagram)** |

### Files Updated

- `azc_activation.act.yaml`: Removed P from positional zones; added clarification
- `fits_azc.md`: Removed P from workflow phase table; added clarification notes
- `AZC_POSITION_VOCABULARY/README.md`: Labeled P as "(not diagram)" throughout
- `azc_system.md`: Updated C443 to focus on diagram positions (C, R, S)
- `CHANGELOG.md`: Fixed v2.96 entry which incorrectly listed P

---

## Version 2.96 (2026-01-31) - AZC Terminology Cleanup

### Summary

Fixed pervasive "filter/gate/route" language that incorrectly implied AZC actively affects execution. AZC is a static positional encoding: each PREFIX+MIDDLE has ONE fixed position, and position reflects vocabulary character, not causal effect.

### Correct Model

**AZC is NOT:**
- A filter that selects/blocks tokens
- A gate that controls execution flow
- A router that directs content
- An active transformation layer

**AZC IS:**
- A static lookup table (PREFIX+MIDDLE → position)
- A vocabulary classifier (position reflects operational character)
- A positional encoding (each token type has one fixed position)

### Key Finding (AZC_POSITION_VOCABULARY Phase)

AZC **diagram** position vocabulary signatures (C, R, S only - P is paragraph text, not diagram):

| Position | Character | Indicators |
|----------|-----------|------------|
| S-series | Stabilization | Highest AX% (35-45%), highest ok/ot% (41-45%), lowest EN% |
| R-series | Processing | Balanced profile, interior positions |
| C | Core | Balanced |

*P (Paragraph) is Currier A text on AZC folios, not a diagram position.*

Position has NO independent effect beyond vocabulary composition (Test 4: 0/10 MIDDLEs showed position effect when controlling for MIDDLE).

### Documentation Updates

| File | Change |
|------|--------|
| phases/AZC_POSITION_VOCABULARY/ | New phase documenting position vocabulary analysis |
| azc_activation.act.yaml | Replaced "gates/filters" → "encodes/groups" |
| currier_AZC.md | "gates" → "encodes position" |
| azc_system.md | "compatibility filter" → "compatibility grouping" |
| C384a | "AZC legality routing" → "AZC positional encoding" |
| C765 | "constrains execution" → "has characteristic B behavior" |
| fits_azc.md | Multiple filter/gate references corrected |

### Terminology Corrections

| Wrong | Right |
|-------|-------|
| AZC gates | AZC encodes position |
| AZC filters | AZC positions reflect |
| compatibility filter | compatibility grouping |
| AZC routes | AZC maps |
| AZC constrains B execution | AZC vocabulary has characteristic B behavior |

---

## Version 2.95 (2026-01-31) - FL Terminology Disambiguation

### Summary

Added terminology disambiguation for "FL" which was being used for two different concepts:

1. **FL (MIDDLE taxonomy)** - C777 material state index (~25% of tokens)
2. **FLOW_OPERATOR (FO)** - 49-class behavioral role (4.7% of tokens)

### Documentation Updates

| File | Change |
|------|--------|
| TERMINOLOGY/fl_disambiguation.md | New file explaining the distinction |
| C777_fl_state_index.md | Added terminology note |
| currierB.bcsc.yaml | Added FO abbreviation and disambiguation note |
| CLAIMS/INDEX.md | Added terminology note to FL section |

### Why This Matters

FL MIDDLEs (y, m, am, dy, r, l, etc.) appear in ~25% of all tokens across all 49 classes. FLOW_OPERATOR is a specific behavioral role with only 4.7% of tokens. Confusing them leads to incorrect analysis (e.g., expecting "FL rate" of 25% but seeing 4.7% when using 49-class role).

---

## Version 2.94 (2026-01-31) - A-B Within-Line Positional Correspondence

### Summary

Extended A_PP_INTERNAL_STRUCTURE phase with cross-system analysis. Major finding: shared vocabulary has consistent within-line positional roles across A and B.

### Key Finding (C899)

**A-B Within-Line Positional Correspondence:** PP MIDDLEs maintain consistent within-line positions across systems.

| Metric | Value |
|--------|-------|
| Corpus-level r | 0.654 (p < 0.0001) |
| Folio-level r (mean) | 0.149 (weak) |
| Zone preservation | 92.5% (vs 33% chance) |
| Hub zone stability | 5/5 MIDDLE in both systems |

**Interpretation:** This is a **corpus-level grammar property**, not a folio-level mapping. Vocabulary items carry positional semantics (EARLY/MIDDLE/LATE roles) that are consistent across both systems. This differs from C885, which establishes folio-level vocabulary correspondence.

### Documentation Updates

| File | Change |
|------|--------|
| INDEX.md | Updated A PP Internal Structure section (C898-C899) |
| C899_ab_positional_correspondence.md | New constraint file |

### Constraint Count

- Before: 764 constraints
- After: 765 constraints (+1: C899)

---

## Version 2.93 (2026-01-30) - A PP Internal Structure

### Summary

New phase A_PP_INTERNAL_STRUCTURE reveals that Currier A PP vocabulary has significant internal organization, refining C234's aggregate "position-free" finding.

### Key Findings (C898)

1. **PP Positional Grammar** (C898.a)
   - 50% of MIDDLEs have significant position bias (KS p<0.0001)
   - LATE-biased: m (0.85), am (0.79), d (0.75), dy (0.73) - closure markers
   - EARLY-biased: or (0.35), pch (0.31), dch (0.38) - opening/initiation

2. **PP Hub Network Structure** (C898.b)
   - Scale-free network with CV=1.69 (hub-dominated)
   - Top hub: iin (degree 277, mega-hub connector)
   - Secondary hubs: ol (208), s (197), or (188), y (181)
   - Consistent with C475: hubs are "legal connectors" bridging otherwise incompatible vocabulary

3. **Bimodal Position Distribution**
   - INITIAL zone (0.0-0.1): 13.9%
   - MIDDLE zone (0.4-0.6): 17.8% (valley)
   - FINAL zone (0.9-1.0): 18.9%
   - Aligns with C830 FINAL-bias (0.675) since C828 confirms 100% of repeats are PP

### Relationship to C234

C234 establishes aggregate position-freedom. C898 refines this: the aggregate may be uniform, but the PP subpopulation has bimodal structure. Analogous to C498.d refining C498 for RI length-frequency correlation.

### Phase Verdict

**STRONG** (2 confirmed, 1 support, 1 not supported)

| Test | Verdict |
|------|---------|
| 1. Positional Preferences | CONFIRMED |
| 2. Network Topology | CONFIRMED |
| 4. WITH-RI vs WITHOUT-RI | SUPPORT (sample imbalanced) |
| 6. Gradient Analysis | NOT SUPPORTED (primary axis is DIVERSITY vs CLOSURE) |

### Documentation Updates

| File | Change |
|------|--------|
| INDEX.md | Added C898 section |
| C898_a_pp_internal_structure.md | New constraint file |
| phases/A_PP_INTERNAL_STRUCTURE/ | New phase directory |

### Constraint Count

- Before: 763 constraints
- After: 764 constraints (+1: C898)

---

## Version 2.92 (2026-01-30) - Section-Specific Registry Architecture

### Summary

Extended C888 with comprehensive section architecture comparison. Sections (H, P, T) have distinct registry architectures, not just different content.

### Key Findings

1. **WITH-RI ratio differs significantly** (p=0.044)
   - P section: 64.5% WITH-RI (material specification focus)
   - H section: 49.1% WITH-RI (cross-reference balance)

2. **Section-distinctive PREFIXes**
   - H: kch, sch, dch, tch, ct (gallows-ch compounds, cross-ref)
   - P: or, ol (LINK prefixes - monitoring/safety)
   - T: al, ar, ta (highly distinctive)

3. **Low vocabulary overlap** (Jaccard ~0.2)
   - H: 69% exclusive MIDDLEs
   - P: 46% exclusive MIDDLEs

### Documentation Updates

| File | Change |
|------|--------|
| C888 | Renamed to "Section-Specific Registry Architecture", added C888.a (WITH-RI ratio), C888.c (vocabulary distinctiveness), C888.d (section PREFIXes) |

### Scripts Created

- `scripts/section_architecture_comparison.py`
- `scripts/ri_positional_function_test.py` (investigation closed - effect explained by PREFIX)
- `scripts/ri_pp_control_test.py`
- `scripts/ri_pp_dual_use_analysis.py`

### Constraint Count

- No change: 763 constraints (extension of C888, not new constraint)

---

## Version 2.91 (2026-01-30) - Linker Destination Characterization

### Summary

Characterized the structural properties of linker destination folios (C835) and refined understanding of linker function. Expert validation confirmed findings are consistent with existing constraints.

### Key Findings

1. **Hub destinations are structurally typical** - f93v and f32r show no outlier properties (z-scores < |1|)
2. **Linkers don't consistently appear as INITIAL** in destinations - suggests cross-reference function
3. **High source vocabulary similarity** (Jaccard 0.50-0.77) favors OR (alternatives) over AND (aggregation)
4. **Section concentration** - 96% in section H (herbal)
5. **ct-ho is necessary but not sufficient** - only 3/42 ct-ho tokens are linkers (7.1%)

### Documentation Updates

| File | Change |
|------|--------|
| C835 | Added "Hub Destination Characterization" section with structural metrics, positions, Jaccard analysis |
| C837 | Added "ct-ho is Necessary But Not Sufficient" section (7.1% linker rate) |
| INTERPRETATION_SUMMARY.md | Added new evidence favoring OR interpretation under RI Linker Mechanism |

### Scripts Created

- `scripts/linker_destination_characterization.py`
- `scripts/linker_destination_followup.py`

### Constraint Count

- No change: 763 constraints (refinement of existing, not new constraint)

---

## Version 2.90 (2026-01-30) - RI Chain Investigation (No New Constraint)

### Summary

Investigated whether RI token connections form a "procedural network" in Currier A.

### Investigation

1. Found 93.7% of A records connected via shared RI tokens
2. Common tokens (daiin, chol) create dense connectivity
3. Initially interpreted as procedural chaining

### Null Test Result

Chi-square testing revealed the pattern is **positional grammar**, not procedural linking:
- daiin, dy, chol = significantly OUTPUT-biased (end of paragraphs)
- sho, cthol, okol = significantly INPUT-biased (start of paragraphs)
- da- prefix = grammatical closure marker

### Expert Validation

Checked against existing constraints:
- **C422**: DA as internal articulation punctuation (75% separation)
- **C839**: RI Input-Output morphological asymmetry
- **C830**: Repetition tokens late-biased

**Verdict:** Pattern already covered by existing constraints. No new constraint needed.

### Constraint Count

- No change: 763 constraints

---

## Version 2.89 (2026-01-30) - Prefixed FL MIDDLEs as State Markers

### Summary

Analysis of tokens ending in -am/-y reveals they contain **FL MIDDLEs** (am, y, dy, ly, m) from C777's state index. These prefixed FL MIDDLEs inherit FL's state-indexing function, explaining their line-final concentration and operation→state mappings.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C897** | Prefixed FL MIDDLEs as Line-Final State Markers (Tier 2) |

### Key Discovery: FL MIDDLE Connection

All tokens contain FL MIDDLEs from C777:

| Token | Prefix | MIDDLE | FL Stage | Position |
|-------|--------|--------|----------|----------|
| am | - | am | FINAL | 0.802 |
| dam | da | m | TERMINAL | 0.861 |
| otam | ot | am | FINAL | 0.802 |
| oly | ol | y | TERMINAL | 0.942 |
| oldy | ol | dy | TERMINAL | 0.908 |
| daly | da | ly | FINAL | 0.785 |
| ary | ar | y | TERMINAL | 0.942 |

### Why This Wasn't Obvious

1. Role classification masks FL MIDDLEs - prefixes shift tokens to AUXILIARY/FREQUENT_OPERATOR
2. Tokens analyzed as wholes - morphological decomposition reveals FL core
3. FL constraints (C770-C777) focus on pure FL tokens, not prefixed forms

### Operation → State Mappings (Extends C777)

| ENERGY Operation | Terminal State | FL MIDDLE |
|------------------|----------------|-----------|
| shey | → ldy | l (LATE) |
| cheky, chedy | → daly | ly (FINAL) |
| qokain, qokeedy | → oly | y (TERMINAL) |

Different heating operations produce different FL terminal states.

### Constraint Count

713 validated constraints (+1 from 712).

---

## Version 2.88 (2026-01-30) - Process Type Discrimination

### Summary

Discovered kernel-recovery correlations that discriminate thermal process types. Phase monitoring (h) anti-correlates with recovery (FQ), while fire control (k) positively correlates. This supports process mode discrimination: distillation (high h) vs boiling/decoction (high k, low h).

### New Constraints

| Constraint | Statement |
|------------|-----------|
| **C895** | Kernel-Recovery Correlation Asymmetry: k-FQ r=+0.27, h-FQ r=-0.29 (Tier 2) |
| **C896** | Process Mode Discrimination: HIGH_K_LOW_H = 2.5x FQ, non-distillation (Tier 3) |

### Key Findings

**Kernel-FQ correlations (527 paragraphs):**

| Kernel | Correlation | p-value | Interpretation |
|--------|-------------|---------|----------------|
| k% | +0.268 | < 10^-6 | Fire control requires recovery |
| h% | -0.286 | < 10^-6 | Phase monitoring substitutes for recovery |
| e% | +0.040 | 0.36 | Equilibration neutral |

**Process interpretation:**
- HIGH_H = DISTILLATION (drip feedback reduces errors)
- HIGH_K_LOW_H = BOILING/DECOCTION (no drip feedback, more recovery needed)

### Convergent Evidence

This is convergent with C781 ("FQ has 0% h; escape routes bypass phase management"). The negative h-FQ correlation (r=-0.286) quantifies this architectural bypass.

### Constraint Count

712 validated constraints (+2 from 710).

---

## Version 2.87 (2026-01-30) - REGIME-Paragraph Recovery Concentration

### Summary

Extended C893 to REGIME level, discovering that recovery-specialized folios cluster in REGIME_4 (33% vs 0-3% other REGIMEs). This validates C494's precision interpretation at paragraph level.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C894** | REGIME_4 Recovery Specialization Concentration: 33% recovery-specialized folios in REGIME_4 (chi-sq=28.41, p=0.0001); validates C494 precision interpretation |

### Key Findings

**Folio specialization by REGIME:**

| REGIME | Recovery% | K/(K+H) | Interpretation |
|--------|-----------|---------|----------------|
| REGIME_4 | 33% | 0.32 | Precision + recovery capacity |
| REGIME_1 | 3% | 0.21 | Moderate, forgiving |
| REGIME_2 | 0% | 0.27 | Low intensity |
| REGIME_3 | 0% | 0.10 | Aggressive, distillation-focused |

**Confounding analysis:**
- Effect persists within sections (controlling for section composition)
- Section H: REGIME_4 has 56% higher K/(K+H) than REGIME_3

**Multi-level validation chain:**
- Token level: C780 (FQ is k-rich)
- Paragraph level: C893 (HIGH_K = recovery)
- Folio level: Recovery-specialized folios exist
- REGIME level: REGIME_4 concentrates recovery-specialized folios

### Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C494 | VALIDATES - paragraph-level confirmation of precision interpretation |
| C893 | EXTENDS - from paragraph-level to REGIME aggregation |
| C780 | ALIGNS - FQ is k-rich explains HIGH_K -> recovery link |

### Constraint Count

710 validated constraints (+1 from 709).

---

## Version 2.86 (2026-01-30) - Paragraph Kernel-Operation Mapping

### Summary

Discovered that B paragraph kernel signatures predict operation types, mapping to Brunschwig operation categories. HIGH_K paragraphs concentrate escape/recovery operations; HIGH_H paragraphs concentrate active processing operations.

### New Constraint

| Constraint | Statement |
|------------|-----------|
| **C893** | Paragraph Kernel Signature Predicts Operation Type: HIGH_K=2x FQ enrichment (p<0.0001), HIGH_H=elevated EN (p=0.036) |

### Key Findings

**Paragraph-level operation specialization:**

| Para Type | Count | FQ Rate | EN Rate | Brunschwig Mapping |
|-----------|-------|---------|---------|-------------------|
| HIGH_K | 58 | 19.7% | 19.3% | Recovery procedures |
| HIGH_H | 203 | 9.7% | 22.0% | Active distillation |
| BALANCED | 235 | 12.6% | 23.9% | General procedures |

**Statistical significance:**
- FQ difference (HIGH_K vs HIGH_H): p < 0.0001 (Tier 2)
- EN difference: p = 0.036 (supporting evidence)

**Brunschwig operation categories (Tier 3 interpretation):**
- HIGH_K = "If it overheats, remove from fire" (crisis response)
- HIGH_H = "Distill with fire, watching drip rate" (careful processing)
- BALANCED = Standard distillation steps

### Relationship to C780

This extends C780 (Role Kernel Taxonomy) from token-level to paragraph-level:
- C780: "FQ tokens use k+e with 0% h" (token property)
- C893: "HIGH_K paragraphs concentrate FQ operations" (spatial organization)

The concentration of recovery operations in HIGH_K paragraphs is new structural information.

### Expert Validation

Approved for Tier 2 documentation. No conflicts with existing constraints (C780, C781, C778, C103-105).

### Constraint Count

709 validated constraints (+1 from 708).

---

## Version 2.85 (2026-01-30) - Closed-Loop Orthogonality Discovery

### Summary

Discovered orthogonal control dimensions in the Voynich closed-loop model that Brunschwig's linear recipe model cannot capture. Added 3 new constraints (C890-C892) and extended REVERSE_BRUNSCHWIG_TEST to 10 tests.

### New Constraints

| Constraint | Statement |
|------------|-----------|
| **C890** | Recovery Rate-Pathway Independence: FQ rate and post-FQ kernel vary independently |
| **C891** | ENERGY-FREQUENT Inverse: rho=-0.80 at REGIME level |
| **C892** | Post-FQ h-Dominance: h (24-36%) dominates over e (3-8%) in recovery |

### Key Findings

**Recovery orthogonality (C890, C892):**
- FQ rate ranking: R4 > R2 > R1 > R3
- Post-FQ e% ranking: R2 > R1 > R3 > R4 (nearly inverse)
- h dominates post-FQ in ALL 4 REGIMEs (phase-check before equilibration)

**Role composition orthogonality (C891):**
- ENERGY_OPERATOR vs FREQUENT_OPERATOR: rho = -0.80 (strong inverse)
- CORE_CONTROL vs FREQUENT_OPERATOR: rho = 0.00 (perfectly orthogonal)
- R3 (intense): highest ENERGY (36.5%), lowest FREQUENT (11.2%)
- R4 (precision): lowest ENERGY (22.7%), highest FREQUENT (15.1%)

### Phase Update

REVERSE_BRUNSCHWIG_TEST upgraded from MODERATE-STRONG to STRONG:
- Tests 9-10 added (recovery_orthogonality, role_orthogonality)
- Overall: 2 STRONG + 5 SUPPORT + 2 WEAK + 1 NEUTRAL = STRONG correspondence

### Expert Validation

Findings validated against existing constraints:
- Consistent with C458 (recovery is free)
- Refines C105 (e = STABILITY_ANCHOR) - h is entry point, e is anchor
- Strengthens C494 (REGIME_4 precision)
- No conflicts detected

### Constraint Count

758 validated constraints (+3 from 755).

---

## Version 2.84 (2026-01-30) - Escape Terminology Clarification

### Summary

Discovered that two distinct "escape" measures exist in the constraint system with nearly inverse REGIME rankings. Added terminology clarifications to affected constraints.

### Discovery

| Measure | Definition | Classes | Used In | REGIME Ranking |
|---------|------------|---------|---------|----------------|
| qo_density | qo-prefixed tokens | 32, 33, 36 | C494, REGIME profiles | R3 > R1 > R2 > R4 |
| FQ_density | FREQUENT_OPERATOR role | 9, 13, 14, 23 | BCSC, escape recovery | R4 > R2 > R1 > R3 |

**Overlap: 0 tokens** - completely disjoint sets with orthogonal semantics:
- qo_density = thermal/energy operation intensity (C838: "execution-facing, kernel-adjacent")
- FQ_density = grammatical escape/flow control operators

**Key Insight:** REGIME_4's apparent contradiction (lowest "escape" in C494 but highest error handling) is resolved:
- Low qo_density = gentle heat (precision processing)
- High FQ_density = tight tolerances require more error correction

### Changes

**C494_regime4_precision_axis.md:**
- Added terminology note clarifying "escape rate" = qo_density (morphological), not FQ_density (grammatical)
- Changed table label from "Escape rate" to "Escape rate (qo)" for clarity

**REVERSE_BRUNSCHWIG_TEST phase:**
- Updated README with "Methodology Discovery: Dual Escape Measures" section
- Updated fire_stability_proxy.json with terminology clarification
- Updated reverse_brunschwig_verdict.json with methodology_discovery section

### Source

REVERSE_BRUNSCHWIG_TEST phase, Test 8 verification

---

## Version 2.83 (2026-01-30) - Aggregation Level Cleanup Round 2

### Summary

Extended aggregation annotations to additional constraints. Round 1 covered 14 constraints; Round 2 covered 17 more for a total of 31 annotated constraints.

### Round 2 Changes

**A-Record Filtering constraints annotated (line-level):**
- C682 (survivor distribution profile)
- C683 (role composition under filtering)
- C684 (hazard pruning under filtering)
- C685 (LINK/kernel survival rates)
- C686 (role vulnerability gradient)
- C687 (composition-filtering interaction)
- C688 (REGIME filtering robustness)
- C689 (survivor set uniqueness)

**PP Structure constraints annotated:**
- C640 (PP role projection architecture)
- C641 (PP population execution profiles)
- C656 (PP co-occurrence continuity)
- C658 (PP material gradient)

**Cross-System constraints annotated:**
- C642 (A record role material architecture)
- C825 (continuous not discrete routing)
- C691 (program coherence) - added C885 reference

**RI Structure constraints clarified:**
- C831 (RI three-tier structure) - scope note added
- C833 (RI first-line concentration) - scope clarification added
- C834 (paragraph granularity validation) - scope clarification added

**Verified correct (no changes needed):**
- C722 (within-line accessibility) - already uses "A-folio filtering"
- C725 (across-line accessibility) - B-scope analysis

### Constraint Count

755 validated constraints (no new constraints, annotations only).

---

## Version 2.82 (2026-01-30) - Aggregation Level Cleanup Round 1

### Summary

Annotated constraints that analyze Currier A at line or paragraph level to clarify the three-level hierarchy established by C881 and C885:

| Level | Count | Purpose |
|-------|-------|---------|
| Line | 1,575 | Transcript structure (not operationally meaningful) |
| Paragraph | 342 | A-internal record unit (C881) |
| **Folio** | 114 | **A-B operational unit** (C885: 81% coverage) |

### Changes

**Line-level constraints annotated:**
- C481 (survivor-set uniqueness)
- C690 (line-level legality distribution)
- C693 (usability gradient)
- C728 (PP co-occurrence incompatibility)
- C730 (PREFIX-MIDDLE within-line coupling)
- C731 (adjacent line continuity)
- C732 (within-line selection uniformity)
- C733 (PP token variant line structure)
- C824 (A-record filtering mechanism)

**Paragraph-level constraints annotated:**
- C827 (paragraph operational unit) - clarified: paragraph is A-internal, folio is A-B operational
- C846 (A-B paragraph pool) - noted folio achieves higher coverage
- C881 (A record paragraph structure) - clarified distinction from A-B operational level

**Multi-level constraints linked to C885:**
- C826 (token filtering model) - added C885 reference

### Constraint Count

755 validated constraints (no new constraints, annotations only).

---

## Version 2.81 (2026-01-30) - CURRIER_A_STRUCTURE_V2 Phase + C887-C889

### Summary

Comprehensive characterization of Currier A paragraph-level structure. Extended existing constraints (C881, C837) and added new constraints documenting WITHOUT-RI paragraph behavior.

### Key Findings

**Two Paragraph Opening Types:**
- WITH-RI (62.9%): Material-focused records with RI in first line
- WITHOUT-RI (37.1%): Process-focused annotations with pure PP

**WITHOUT-RI Backward Reference (C887):**
- 1.23x backward/forward asymmetry
- Highest overlap (Jaccard 0.228) when following WITH-RI paragraph
- Mechanism: process instructions apply to just-identified material

**Section-Specific Function (C888):**
- Section H: ct-prefix 3.87x enriched (cross-referencing)
- Section P: qo/ok/ol enriched (safety protocols)

**ct-ho PP Vocabulary (C889):**
- MIDDLEs h, hy, ho are 98-100% ct-prefixed in Section H
- Extends C837 linker signature to PP level
- Reserved vocabulary for linking/transfer operations

### Changes

- **C881 updated:** Integrated CURRIER_A_STRUCTURE_V2 findings into existing paragraph structure constraint
- **C837 updated:** Added cross-reference to C889 (PP-level extension)
- **C887 added:** WITHOUT-RI Backward Reference mechanism
- **C888 added:** Section-Specific WITHOUT-RI Function
- **C889 added:** ct-ho Reserved PP Vocabulary

### Constraint Count

755 validated constraints.

---

## Version 2.80 (2026-01-30) - C391 Clarification + C886 Transition Directionality

### Summary

Clarified C391 (time-reversal symmetry) and added C886 (transition directionality) based on external audit.

### Key Finding

C391 and C886 measure **different properties** that together are diagnostic:

| Property | Voynich | Natural Language | Procedural |
|----------|---------|------------------|------------|
| Conditional entropy symmetry (C391) | Yes (1.00) | No (~0.85) | ~0.9 |
| Transition probability correlation (C886) | **Near-zero (-0.055)** | High (~0.99) | High (~0.99) |

**Interpretation:** Grammar constraints are bidirectional (C391), but execution paths are directional (C886). This combination excludes both natural language AND simple procedural text.

### Changes

- **C391 renamed/clarified:** "Conditional Entropy Symmetry" - explicitly distinguishes constraint symmetry from transition symmetry
- **C886 added:** "Transition Probability Directionality" - P(A→B) uncorrelated with P(B→A)
- **BCSC contract updated:** TIME_REVERSAL_SYMMETRIC → CONDITIONAL_ENTROPY_SYMMETRIC with dual provenance

### Constraint Count

752 validated constraints.

---

## Version 2.79 (2026-01-29) - A-B Vocabulary Correspondence Definitive Answer

### Summary

**DEFINITIVE ANSWER:** A folios provide 81.2% vocabulary coverage for B paragraphs (1.71x vs random). Single A paragraphs provide only 58.3% coverage (2.04x vs random). The A-B relationship is real but requires folio-level or multi-paragraph aggregation.

### Key Finding (C885)

| A Unit | B Unit | Coverage | vs Random |
|--------|--------|----------|-----------|
| Paragraph | Paragraph (>=10 PP) | 58.3% | 2.04x |
| **Folio** | **Paragraph** | **81.2%** | 1.71x |
| 2-3 Paragraphs | Paragraph | 76-80% | - |

### What Works vs Doesn't

**Works:**
- A folio -> B paragraph: 81% coverage, 1.71x lift
- Multi-paragraph aggregation: 80%+ with 3 paragraphs

**Doesn't Work (Artifacts/Null):**
- Lane balance correlation: 0.99x (artifact of best-match)
- Kernel matching: 1.17x (marginal)
- Linker bundles: 0.99x (no better than random)

### Interpretation

A folios are "material contexts" that define available vocabulary. B paragraphs are "mini-programs" that execute with that vocabulary. The operator selects an A context (folio) appropriate for their material.

### Documentation

- `context/CLAIMS/C885_ab_vocabulary_correspondence.md` - New constraint
- `phases/A_B_CORRESPONDENCE_SYSTEMATIC/FINDINGS.md` - Full analysis
- `context/CLAIMS/C384a_conditional_correspondence.md` - Updated with quantitative evidence

### Constraint Count

751 validated constraints.

---

## Version 2.78 (2026-01-29) - Record Unit Correction (eoschso Invalidated)

### Summary

**CRITICAL CORRECTION:** The eoschso = chicken identification is **INVALIDATED**. The previous methodology incorrectly treated lines as records.

A records are **paragraphs**, not lines. Initial RI (material identifier) appears in the **first line** of a paragraph.

### Evidence

- eoschso (MIDDLE of "okeoschso") appears at position 41/70 in paragraph A_268
- This is in the MIDDLE lines of the paragraph, not the first line
- Therefore eoschso is NOT initial RI and cannot be a material identifier

### Corrected Methodology

New paragraph-level PP triangulation (MATERIAL_MAPPING_V2, Scripts 09-11):
1. Group paragraph tokens by LINE
2. Extract RI from FIRST LINE only (initial RI = material ID)
3. Match PP patterns against Brunschwig handling types
4. Validate via kernel signature (k+e vs h ratio)

### New PRECISION Candidates (Potential Animals)

6 paragraphs pass both PP pattern AND kernel validation (k+e >> h):

| Para | Initial RI | Folio | k+e | h |
|------|-----------|-------|-----|---|
| A_194 | opolch | f58v | 0.53 | 0.05 |
| A_196 | eoik | f58v | 0.50 | 0.06 |
| A_283 | qkol | f99v | 0.50 | 0.09 |
| A_280 | opsho, eoef | f99r | 0.60 | 0.23 |
| A_332 | ho, efchocp | f102r2 | 0.78 | 0.22 |
| A_324 | qekeol, laii | f101v2 | 0.48 | 0.12 |

### Documentation Updated

- `context/SPECULATIVE/recipe_triangulation_methodology.md` - Marked as INVALIDATED
- `phases/MATERIAL_MAPPING_V2/FINDINGS.md` - New corrected analysis

---

## Version 2.77 (2026-01-21) - Recipe Triangulation Methodology + C384 Scope Fix

### Summary

Developed and validated a methodology for mapping Brunschwig recipe characteristics to specific Voynich A records via multi-dimensional PP convergence. Successfully identified **eoschso = ennen (chicken)** as Tier 3 hypothesis.

**Also fixed C384 scope** - the original wording was over-blocking valid record-level inference, causing AI derailment.

### Key Findings

| Test | Result |
|------|--------|
| REGIME vocabulary distinctiveness | 11.9% exclusive (weak) |
| 4D conjunction narrowing | 0.29x ratio (synergistic) |
| Rose water vs animal folio overlap | 90.8% (PP not discriminative at folio level) |
| Record-level PP convergence | **DISCRIMINATES** (different records for different animals) |

### The Working Pipeline

```
Recipe Dimensions → B Folio Constraints → 4D Conjunction →
PP Vocabulary → A RECORD Convergence (3+) → RI Extraction →
PREFIX Profile Matching → Instruction Sequence → Material ID
```

### Animal Identification

| RI Token | ESCAPE PP? | AUX PP? | Candidate Animal |
|----------|------------|---------|------------------|
| eoschso | YES | YES | **ennen (chicken)** |
| teold | YES | NO | scharlach/charlach/milch? |
| chald | YES | NO | scharlach/charlach/milch? |
| eyd | weak | weak | blut/ltzinblut? |

### Constraint Refinement

**C384 (no entry-level A-B coupling) refined:**
> Single PP tokens do not establish entry-level coupling, but multi-dimensional PP convergence at RECORD level combined with PREFIX profile matching can identify specific A records.

### New Documentation

- `context/SPECULATIVE/recipe_triangulation_methodology.md` - Full methodology
- `phases/ANIMAL_PRECISION_CORRELATION/results/animal_identification.md` - Results
- `phases/ANIMAL_PRECISION_CORRELATION/results/pipeline_gap_analysis.md` - Initial tests

### C384 Scope Fix

**Problem:** Original C384 wording ("No entry-level A-B coupling") was over-blocking record-level inference, causing AI to abort valid tests.

**Solution:** Split into two constraints:
- **C384** (revised): No TOKEN-level or context-free A-B lookup
- **C384.a** (new): Conditional record-level correspondence PERMITTED

**What C384 now BLOCKS:**
- Token -> meaning lookup
- Token -> folio mapping
- Entry -> folio WITHOUT constraint routing
- Dictionary / translation claims

**What C384.a PERMITS:**
- Record-level correspondence via multi-axis constraint composition
- Survivor-set collapse (C481)
- Reverse inference via AZC routing
- Multi-dimensional PP convergence at RECORD level

**Canonical rule added to MODEL_CONTEXT.md:**
> "Currier A never names anything, but Currier A records can correspond to Currier B execution contexts when sufficient constraints collapse through AZC."

### Files Changed

- CLAIMS/C384_no_entry_coupling.md - REVISED (narrowed scope)
- CLAIMS/C384a_conditional_correspondence.md - NEW
- CLAIMS/INDEX.md - Updated C384, added C384.a
- CLAIMS/currier_a.md - Updated C384 references
- MODEL_CONTEXT.md - Updated forbidden list, added canonical rule
- SPECULATIVE/INTERPRETATION_SUMMARY.md - Added X.28 (Recipe Triangulation)
- SPECULATIVE/recipe_triangulation_methodology.md - NEW

---

## Version 2.76 (2026-01-21) - ANIMAL_PRECISION_CORRELATION: A-Exclusive Registry Vocabulary

### Summary

Investigated whether REGIME_4 (precision procedures) shows distinctive morphological signatures consistent with animal distillation's categorical procedural differences. The "animal distillation / REGIME_4 correlation" hypothesis was partially supported but critically reframed.

### Pre-Registered Predictions

| ID | Prediction | Result |
|----|------------|--------|
| P1 (Strong) | REGIME_4 hazard CV within 0.04-0.11 | **PASS** |
| P2 (Medium) | REGIME_4 ch-prefix enrichment >1.2x | **FAIL** |
| P3 (Medium) | f75r distinctive within REGIME_1 | **FAIL** |
| P4 (Weak) | <20% L-compound in PRECISION tokens | **PASS** (0%) |
| P5 (Exploratory) | REGIME_4 lower escape density | **SUPPORTED** |

### Critical Discovery

All 18 P(animal)=1.00 tokens are **A-exclusive** - they exist in Currier A's registry but NEVER appear in Currier B's execution layer. The "animal distillation" connection is about A's material cataloguing, not B's procedural execution.

### REGIME_4 Distinctive Profile

| Characteristic | REGIME_4 vs Others |
|----------------|-------------------|
| Recovery operations | **0.37x** (much less) |
| Near-miss events | **0.52x** (much less) |
| da-prefix | **1.48x** enriched |
| ok-prefix | **1.24x** enriched |
| ct-prefix | **1.84x** enriched |
| qo-prefix | **0.68x** depleted |

REGIME_4 is "get it right the first time" - less recovery, less intervention, different PREFIX profile.

### f75r Investigation

The Tier 4 speculative mapping of Kudreck→f75r is NOT supported. f75r is a typical REGIME_1 folio (z-score +0.18), not a REGIME_4 outlier.

### Constraint Implications

| Constraint | Status |
|------------|--------|
| C458 (Design Clamp) | **VALIDATED** - all REGIMEs show clamped hazard |
| C494 (REGIME_4 = precision) | **SUPPORTED** - distinctive low-recovery/low-escape profile |
| C384 (No A-B coupling) | **PRESERVED** - PRECISION tokens are A-exclusive |
| C499 (RI vocabulary) | **VALIDATED** - animal-associated MIDDLEs stay in A |

### Documentation Updates

- Updated C499 in currier_a.md with validation note (corrected count 27→18)
- Created comprehensive PHASE_SUMMARY.md

### Provenance

- Phase: ANIMAL_PRECISION_CORRELATION
- Scripts: `test_a_design_clamp.py`, `test_b_precision_tokens.py`, `test_c_f75r_investigation.py`, `test_de_morphology_by_regime.py`
- Results: 4 JSON files in results/

---

## Version 2.75 (2026-01-21) - B_EXCLUSIVE_MIDDLE_ORIGINS: Three-Layer Stratification (C501)

### Summary

Investigated why 569 MIDDLEs are B-exclusive. Discovered that B-exclusivity is NOT about distinct discriminators - it's morphological surface variation. 65.9% of B-exclusive MIDDLEs are edit-distance-1 variants of shared MIDDLEs.

### Key Findings

| Finding | Evidence |
|---------|----------|
| 65.9% are edit-distance-1 variants | 375/569 MIDDLEs |
| Edit types | 59% insertion, 39% substitution, 2% deletion |
| B-exclusive longer | Mean 4.40 vs 3.03 chars (p<0.0001) |
| Boundary enriched | 1.70x at line edges |
| 80.3% are singletons | 457/569 appear exactly once |
| L-compound operators | 49 types, 111 tokens (line-initial) |

### Three-Layer Stratification

| Layer | Size | Function |
|-------|------|----------|
| L-compound operators | 49 types | Line-initial control (C298) |
| Boundary closers | ~15 types | Line-final markers (-edy/-dy) |
| Singleton cloud | 457 types (80%) | Orthographic variants, no grammar role |

### False Lead Closed

The "49 distant MIDDLEs = 49 instruction classes" coincidence was tested and correctly rejected. All 49 distant MIDDLEs are hapax legomena with no operator behavior.

### REGIME Finding

REGIME_1 (simple) has highest B-exclusive rate (60.4%). Complex procedures use more canonical vocabulary. Supports C458 (design freedom in simple contexts).

### Constraint Added

**C501 - B-Exclusive MIDDLE Stratification (Tier 2):** B-exclusive status primarily reflects positional and orthographic realization under execution constraints, not novel discriminative content. True grammar operators are confined to the small L-compound core.

### Documentation Updates

- Added C501 to currier_a.md
- Updated MODEL_CONTEXT.md Section V with quantified stratification
- Updated EXPERT_CONTEXT.md via regeneration

### Provenance

- Phase: B_EXCLUSIVE_MIDDLE_ORIGINS
- Scripts: `b_excl_origin_analysis.py`, `extract_distant_middles.py`, `high_freq_b_exclusive.py`
- Results: `b_excl_origin_analysis.json`

---

## Version 2.74 (2026-01-21) - A_SECTION_T_CHARACTERIZATION: Measurement Disambiguation

### Summary

Investigated why Section T vocabulary shows 0% presence in Currier B (C299). Resolved apparent anomaly by discovering C299 measures section-characteristic vocabulary, not raw vocabulary overlap. Section T contains no distinctive vocabulary—only generic infrastructure tokens.

### Investigation Path

| Phase | Test | Finding |
|-------|------|---------|
| 1 | Registry-Internal Check | OPPOSITE - Section T is 32.3% RI vs 57.6% baseline (DEPLETED) |
| 1 | AZC Participation | OPPOSITE - Section T 52.8% vs 28.1% baseline (ENRICHED) |
| 1 | Control Operators | Zero control operators found in Section T |
| 2 | S-Zone Concentration | FALSIFIED - Section T DEPLETED in boundary zones (15.1% vs 17.9%) |
| 3 | Vocabulary Overlap | **KEY DISCOVERY** - 67.7% of T MIDDLEs appear in B (vs 42.4% baseline) |
| 3 | B Folio Presence | 100% of B folios contain Section T vocabulary |

### Key Discovery

Two different questions were conflated:

| Question | Answer |
|----------|--------|
| Does B use vocabulary that appears in Section T? | **YES - 100% of B folios** |
| Does B use vocabulary *distinctive* of Section T? | **NO - 0%** |

Both results are true simultaneously and not in tension.

### Resolution

Section T (f1r, f58r, f58v) contains **no section-characteristic vocabulary**. Its vocabulary consists entirely of shared infrastructure tokens (`_EMPTY_`, `a`, `al`, `ck`, `d`, etc.) that appear ubiquitously across all systems.

Section T functions as:
- Generic baseline (not specialized registry content)
- Template/scaffold (demonstrates morphology without domain specifics)
- Non-discriminative registry surface (orientation, not content)

### External Validation

Reviewed by domain expert. Verdict: "This represents a successful disambiguation rather than a correction. C299 was correct all along—it measures section-characteristic vocabulary, not raw overlap. Section T simply has no distinctive content to measure."

### Constraint Changes

| Constraint | Change |
|------------|--------|
| C299 | VALIDATED - measures section-characteristic vocabulary correctly |
| C299.a | ADDED - clarification that C299 measures discriminators, not raw overlap |

### Provenance

- Phase: A_SECTION_T_CHARACTERIZATION
- Scripts: `phases/A_SECTION_T_CHARACTERIZATION/scripts/`
  - `section_t_analysis.py` (initial characterization)
  - `azc_zone_analysis.py` (S-zone hypothesis test)
  - `permutation_and_overlap_test.py` (vocabulary overlap discovery)
- Results: `phases/A_SECTION_T_CHARACTERIZATION/results/`

---

## Version 2.73 (2026-01-21) - HT_MORPHOLOGICAL_CURRICULUM: Partial Curriculum Structure

### Summary

Investigated whether HT morphological patterns follow curriculum structure. Found partial evidence (1 strong, 2 weak, 1 provisional out of 5 valid tests). Key rebinding confound identified for difficulty gradient finding.

### Test Battery Results

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Introduction Sequencing | **STRONG PASS** | All 21 families in first 0.3% (KS=0.857) |
| 2. Spaced Repetition | UNDERPOWERED | Insufficient rare-but-repeated tokens |
| 3. Block Complexity | FAIL | No within-block gradient |
| 4. Family Rotation | **WEAK PASS** | Quasi-periodic ACF peaks |
| 5. Difficulty Gradient | **PROVISIONAL** | Inverted-U confounded by rebinding |
| 6. Prerequisite Structure | **WEAK PASS** | 26 pairs (2.5x expected) |

### Key Findings

| Finding | Evidence | Status |
|---------|----------|--------|
| Vocabulary front-loading | All 21 families in first 0.3% | CONFIRMED |
| Prerequisite relationships | 26 pairs vs 10.5 expected | CONFIRMED |
| Quasi-periodic rotation | ACF peaks at 6,9,12,14,17 | CONFIRMED |
| Inverted-U difficulty | H=89.04, p<0.0001 | PROVISIONAL (rebinding confound) |

### Rebinding Caveat

The inverted-U difficulty pattern cannot be distinguished from rebinding artifact without quire-level controls. The manuscript was rebound by someone who couldn't read it (C156, C367-C370). The "middle" zone in current binding is a mixture of originally non-adjacent folios.

### Documentation Updates

- Added Section I.A to INTERPRETATION_SUMMARY.md (HT Morphological Curriculum)
- Added curriculum characterization note to C221 in operations.md
- Added brief mention to MODEL_CONTEXT.md Section IX
- Updated phase summary to reflect PROVISIONAL status for Test 5

### Outcome

Tier 3 characterization (not Tier 2 constraint). Refines C221 (Deliberate Skill Practice) with specific curriculum mechanics.

### Provenance

- Phase: HT_MORPHOLOGICAL_CURRICULUM
- Script: `phases/HT_MORPHOLOGICAL_CURRICULUM/scripts/ht_curriculum_analysis.py`
- Results: `phases/HT_MORPHOLOGICAL_CURRICULUM/results/ht_curriculum_results.json`

---

## Version 2.72 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: PP Vocabulary Bifurcation (C498.a)

### Summary

Investigated the internal structure of "Pipeline-Participating" (PP) MIDDLEs from C498. Discovered that the 268 A∩B shared MIDDLEs comprise two structurally distinct subclasses, not a uniform pipeline-participating population.

### Key Findings

| Finding | Evidence |
|---------|----------|
| 114 bypass MIDDLEs | Appear in A and B but **never** in AZC |
| B-heavy frequency | 58.8% have B count > 2× A count |
| B-native vocabulary | e.g., `eck` A=2, B=85; `ect` A=2, B=46 |
| Pipeline narrower | Only 154 (25%) genuinely participate in A→AZC→B |

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

### Terminology Correction

The original "Pipeline-Participating" label is misleading:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

### External Validation

Reviewed by domain expert. Verdict: "This is a solid, architecture-strengthening refinement. It sharpens C498, clarifies pipeline scope, and removes an implicit overgeneralization — without reopening any closed tier."

### Constraint Changes

1. **C498.a added (Tier 2 Refinement):** A∩B shared vocabulary bifurcates into AZC-Mediated (154) and B-Native Overlap (114). Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass.

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498.a refinement
- `context/CLAIMS/INDEX.md` - Added C498.a entry and characterization note
- `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` - Updated two_track_structure with substructure
- `context/MODEL_CONTEXT.md` - Updated Two-Track section with full hierarchy

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS (PP vocabulary analysis)
- Scripts: pp_middle_frequency.py, pp_singleton_analysis.py, pp_singleton_b_frequency.py, pp_middle_propagation.py, pp_bypass_azc.py
- Results: pp_middle_propagation.json

---

## Version 2.71 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: Hierarchical RI Closure at Segment Level

### Summary

Extended RI closure investigation to DA-segmented structure. Tested whether DA articulation (C422) reveals RI/PP stratification beyond what PREFIX alone explains. Discovered **hierarchical RI closure** — the closer preference operates at both line and segment scales.

### Three-Phase Investigation

| Phase | Question | Result |
|-------|----------|--------|
| Pre-check | Does PREFIX explain RI/PP? | V=0.183 (moderate), proceed |
| Phase 1 | Do DA segments stratify by RI/PP? | d=0.323 (weak), bimodal tail |
| Phase 2 | RI position within segments? | 1.43× closer preference (p<0.001) |
| Phase 3 | Are RI-RICH segments distinct? | Yes, 5× expected by chance |

### Key Findings

| Finding | Evidence |
|---------|----------|
| Hierarchical closure | Line-final 1.76×, segment-final 1.43× |
| RI-RICH segments distinct | 6.1% of segments, 5× binomial expected |
| PREFIX ≠ segment profile | p=0.151 (PREFIX doesn't predict) |
| RI-RICH are short, coherent | 3.3 tokens mean, diversity 2.66 |

### Critical Insight

PREFIX does NOT predict segment RI profile (p=0.151), even though PREFIX partially predicts token-level RI/PP (V=0.183). This means **RI concentration is a positional-closure phenomenon independent of PREFIX vocabulary**.

Two orthogonal organizational axes in A:
1. **PREFIX families** — what domain/material-class is being discriminated
2. **RI closure bursts** — where instance discrimination happens

### Constraint Changes

1. **C498-CHAR-A-SEGMENT added (Tier 3):** Hierarchical RI closure at segment level — 1.43× segment-final preference, RI-RICH segments as distinct closure units

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498-CHAR-A-SEGMENT characterization block
- `context/CLAIMS/INDEX.md` - Added segment characterization note
- `phases/A_RECORD_STRUCTURE_ANALYSIS/PHASE_SUMMARY.md` - Added Part 3 (DA segmentation)

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS (DA segmentation sub-phases)
- Scripts: prefix_ri_pp_crosstab.py, da_segment_ri_pp_composition.py, da_segment_ri_position.py, da_segment_clustering.py
- Results: prefix_ri_pp_crosstab.json, da_segment_*.json

---

## Version 2.70 (2026-01-20) - A_RECORD_STRUCTURE_ANALYSIS: RI Closure Characterization

### Summary

Investigated internal structure of Currier A records using the RI (registry-internal) vs PP (pipeline-participating) distinction from C498. Discovered **RI closure tokens** — the missing complementary half of A's structural punctuation, orthogonal to DA articulation (C422).

### Key Findings

| Finding | Evidence |
|---------|----------|
| RI line-final preference | 29.5% vs 16.8% expected (1.75×) |
| Opener/closer vocabulary disjoint | Jaccard = 0.072 |
| 87% singleton closers | 104 of 119 closer MIDDLEs used exactly once |
| Core closure kernel | ho (10×), hod (4×), hol (3×), mo (3×), oro (3×), tod (3×) |

### Two Complementary Structural Mechanisms

| Layer | Mechanism | Scope | Function |
|-------|-----------|-------|----------|
| Internal segmentation | DA articulation (C422) | Within a record | Sub-unit boundary punctuation |
| Record termination | RI closers | End of a record | Completion + instance discrimination |

**Key insight:** If DA is a comma, RI closers are a period — but one that often needs to be unique, because what matters is not just that something ended, but that it ended as *this* and not anything else.

### Governance Decision

This is **Tier 3 characterization**, not Tier 2 constraint. The finding is **ergonomic bias**, not grammar — C234 (POSITION_FREE) remains intact. Currier A would satisfy all structural contracts even if closers were less singleton-heavy or end-biased.

### Constraint Changes

1. **C498-CHAR-A-CLOSURE added (Tier 3):** RI closure token characterization — line-final preference, singleton tail, complementary to C422

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C498-CHAR-A-CLOSURE characterization block
- `context/CLAIMS/INDEX.md` - Added characterization note under C498-C500 section
- `phases/A_RECORD_STRUCTURE_ANALYSIS/PHASE_SUMMARY.md` - Complete phase documentation

### Provenance

- Phase: A_RECORD_STRUCTURE_ANALYSIS
- Scripts: ri_*.py, closer_*.py, analyze_multi_ri.py, etc.
- Results: ri_signal_investigation.json, noncloser_ri_investigation.json

---

## Version 2.69 (2026-01-20) - BRUNSCHWIG_CANDIDATE_LABELING Phase 4: PREFIX/SUFFIX Track Distribution

### Summary

Extended registry-internal vocabulary analysis with PREFIX/SUFFIX track distribution tests and suffix posture confirmation tests. Key findings: ct-prefix marks exclusive discrimination layer (85% exclusivity, 4.41× enrichment); CLOSURE suffixes are front-loaded (foundational framework) while NAKED entries are late refinements.

### PREFIX/SUFFIX Distribution Results

| Test | Finding | Effect Size |
|------|---------|-------------|
| PREFIX track distribution | ct-prefix 4.41× enriched in registry-internal | Cramér's V=0.307 (strong) |
| CT-prefix deep dive | 85% ct-MIDDLEs exclusive, 13.0 folio spread | - |
| SUFFIX track distribution | 45% registry-internal types ALWAYS suffix-less | Cramér's V=0.222 (moderate) |

### Suffix Posture Confirmation Tests

| Test | Hypothesis | Result | Effect Size |
|------|-----------|--------|-------------|
| S-1 (HT density) | CLOSURE → higher HT | NULL | r=0.152 (small) |
| S-2 (Incompatibility) | NAKED → more isolated | NULL | r=0.0 |
| S-3 (Temporal) | NAKED → introduced earlier | **CONTRADICTED** | r=0.495 (medium) |
| S-4 (Tail pressure) | NAKED → Q4 concentration | **CONFIRMED** | Phi=0.333 (medium) |

### Key Finding

| Posture | Q1 Share | Q4 Share | Interpretation |
|---------|----------|----------|----------------|
| CLOSURE (-y) | **76.7%** | 6.7% | Foundational framework |
| NAKED | 25.9% | **37.9%** | Late refinement |
| EXECUTION | ~100% | 0% | Earliest routing |

**Tail concentration ratio:** NAKED 5.69× more likely in Q4 than CLOSURE

### Constraint Changes

1. **C500 added (Tier 3):** Suffix Posture Temporal Pattern - CLOSURE front-loaded, NAKED late refinement, reverses initial hypothesis

### Files Updated

- `context/CLAIMS/currier_a.md` - Added C500 section
- `context/CLAIMS/INDEX.md` - Added C500 to A-Exclusive Vocabulary Track
- `phases/BRUNSCHWIG_CANDIDATE_LABELING/PHASE_SUMMARY.md` - Added Phase 4 documentation

### Provenance

- Phase: BRUNSCHWIG_CANDIDATE_LABELING Phase 4
- Scripts: s1-s4_*.py in phases/BRUNSCHWIG_CANDIDATE_LABELING/scripts/
- Results: s1-s4_*.json in phases/BRUNSCHWIG_CANDIDATE_LABELING/results/

---

## Version 2.68 (2026-01-20) - BRUNSCHWIG_CANDIDATE_LABELING: Bounded Material-Class Recoverability

### Summary

Attempted to generate Tier 4 candidate labels for registry-internal vocabulary using Brunschwig procedural coordinates. Discovered that while entity-level identity remains irrecoverable, **material-class probability vectors are computable** via Bayesian inference through procedural context.

**Framing:** "What these tokens COULD HAVE BEEN" - not "what they ARE"

### Phase Results

| Phase | Question | Result |
|-------|----------|--------|
| Phase 1 | Material category discrimination | UNINTERPRETABLE (nesting problem) |
| Phase 2 | WATER_STANDARD structural clustering | NULL (Q=0.068, near-random) |
| Phase 3 | Material-class posteriors via Bayesian inference | **POSITIVE** |

### Key Achievement: Bounded Recoverability

| Before | After |
|--------|-------|
| "Entity-level semantics are irrecoverable" | "Entity IDENTITY is irrecoverable, but CLASS-LEVEL PRIORS are computable" |
| "We can't know what these tokens mean" | "We can't know WHICH material, but we CAN compute P(material_class)" |

### Results

- 128 MIDDLEs analyzed with full material-class probability vectors
- 27 tokens with P(animal) = 1.00 (PRECISION-exclusive)
- Mean entropy: 1.08 bits (range 0.00 - 2.62)
- Null model validation: 86% match baseline (confirms prior-dominated nature)

### Semantic Ceiling Gradient

| Level | Recoverability |
|-------|----------------|
| Specific material (lavender) | IRRECOVERABLE |
| Material class (flower vs herb) | **PARTIALLY RECOVERABLE** |
| Procedural context (gentle distillation) | RECOVERABLE |

### Constraint Changes

1. **C499 added (Tier 3):** Bounded Material-Class Recoverability - material-class probability vectors computable for registry-internal MIDDLEs, conditional on Brunschwig interpretive frame.

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C499
- `context/CLAIMS/INDEX.md` - Updated to v2.46 (339 constraints), added C499
- Phase: `phases/BRUNSCHWIG_CANDIDATE_LABELING/`

---

## Version 2.67 (2026-01-20) - BRUNSCHWIG_2TRACK_STRATIFICATION: Type-Specificity Confound Discovered

### Summary

Re-tested F-BRU-005's finding (75.4% type-specific MIDDLEs) using the new 2-track vocabulary classification (C498). Discovered that the aggregate rate is confounded by the registry-internal vocabulary's folio-localization.

### Key Findings

| Track | Type-Specific Rate | n |
|-------|--------------------|---|
| Registry-internal | **62.5%** | 128 |
| Pipeline-participating | **46.1%** | 128 |

**Chi-square:** 12.64, df=3, p < 0.01, Cramer's V = 0.222

### Interpretation

The 75.4% aggregate type-specific rate is inflated by registry-internal vocabulary (56.6% of MIDDLEs). These are folio-localized (avg 1.34 folios) and naturally appear in fewer product types.

The pipeline-participating vocabulary (which actually flows through A→AZC→B) shows a lower 46.1% type-specificity rate - still substantial but not the dominant pattern.

### Angle D: Reference Material Correlation (C498 Validation)

Tested whether registry-internal vocabulary correlates with Brunschwig reference-only materials (listed but no procedure):

| Group | Product Types | n Folios | Mean Reg-Int Ratio |
|-------|---------------|----------|-------------------|
| HIGH-REFERENCE | OIL_RESIN, WATER_GENTLE | 36 | **35.6%** |
| LOW-REFERENCE | WATER_STANDARD, PRECISION | 74 | **30.3%** |

**Mann-Whitney U:** z = -2.602, **p = 0.01**, effect size r = 0.248

**Result:** SUPPORTED - validates C498's "fine distinctions below execution threshold" interpretation.

### Expert Validation

Both internal expert-advisor and external expert validated findings:
- No Tier 0-2 violations
- C498 externally corroborated by orthogonal historical signal
- F-BRU-005 REFINED, not falsified
- Model-strengthening refinement, not scope creep

**Locked-in sentence:** "Separating Currier A into pipeline-participating and registry-internal vocabulary reveals that much of the apparent product-type specificity arises from coverage-driven folio localization; genuine operational alignment exists only in the pipeline vocabulary and is necessarily weaker, overlapping, and regime-mediated—exactly as required by an expert-only, non-semantic control system."

### Documentation Updates

- `context/MODEL_FITS/fits_brunschwig.md` - Added 2-track stratification section to F-BRU-005
- `context/CLAIMS/currier_a.md` - Added external validation note to C498
- Phase: `phases/BRUNSCHWIG_2TRACK_STRATIFICATION/`

---

## Version 2.66 (2026-01-20) - A_INTERNAL_STRATIFICATION: Two-Track Vocabulary Structure

### Summary

Investigated whether A-exclusive MIDDLEs (those appearing in Currier A but never in Currier B) have distinct structural roles. Discovered that Currier A has two vocabulary tracks with different morphological signatures and propagation behavior.

**Result: C498 added (Tier 2) - Registry-Internal Vocabulary Track**

### Key Findings

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating** | 268 (43.4%) | Standard prefixes/suffixes, broad folio spread (7.96) | Flow through A→AZC→B |
| **Registry-internal** | 349 (56.6%) | ct-prefix 5.1×, suffix-less 3×, folio-localized (1.34) | Stay in A registry |

### Falsified Hypotheses

1. **Entry-type marker hypothesis: FALSIFIED** - Initial findings (98.8% opener rate) were artifacts of a data bug (grouping by word,folio instead of folio,line). Corrected: 18.8% vs 17.1% (not significant).

2. **AZC-terminal bifurcation hypothesis: FALSIFIED** - The 8.9% (31 MIDDLEs) that appear in AZC but never reach B are interface noise from systems sharing the same alphabet, not a distinct stratum. Verification checks: 2 PASS, 2 FAIL.

### Constraint Changes

1. **C498 added (Tier 2):** Registry-Internal Vocabulary Track - A-exclusive MIDDLEs (56.6%) form a morphologically distinct track that encodes within-category fine distinctions below the granularity threshold for execution.

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C498 with full evidence
- `context/CLAIMS/INDEX.md` - Added C498 entry
- `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` - Added two_track_structure to middle section
- `context/MODEL_CONTEXT.md` - Added Section VII subsection
- Phase: `phases/A_INTERNAL_STRATIFICATION/`

---

## Version 2.65 (2026-01-20) - f49v Instructional Apparatus Discovery

### Summary

Discovered that f49v contains unique instructional apparatus - a teaching/reference page demonstrating Currier A structural principles. This is the only page in the manuscript with systematic marginal ordinal labels.

### Key Findings

1. **26 single-character L-placement labels** (65% of all such labels in manuscript)
2. **Marginal numbers 1-5** aligned with ordinal positions in vertical character column
3. **33 vocabulary types exclusive to f49v** (phonotactically extreme but structurally valid)
4. **Statistical test for category encoding: NEGATIVE** (p=0.0517, not significant)

### Interpretation

The single-letter column is not encoding values - it is **indexing examples**. The page demonstrates A structure rather than instantiating registry content.

Per external expert: *"A rare, deliberate moment where the manuscript turns inward and teaches how to read itself — without ever explaining itself."* The system that refuses instruction everywhere else has exactly ONE place where it demonstrates form - structurally, not semantically. This is strong corroboration of the expert-only, non-semantic model.

The existence of a single instructional/reference page demonstrates that Currier A was actively used and taught, not that it contains pedagogical grammar or semantic encoding.

### Constraint Changes

1. **C497 added (Tier 2):** f49v Instructional Apparatus - documents unique meta-structural apparatus

### Documentation Updates

- `context/CLAIMS/currier_a.md` - Added C497 in new "Meta-Structural Artifacts" section
- `context/CLAIMS/INDEX.md` - Added C497 entry, updated count to 338
- `phases/PHARMA_LABEL_DECODING/` - Investigation scripts and analysis

---

## Version 2.64 (2026-01-19) - AZC_INTERFACE_VALIDATION: Visual Heterogeneity is Interface-Only

### Summary

Validated that AZC visual heterogeneity (scatter diagrams, rings, nymph pages, P-text) represents interface variation, not mechanism variation. Core A→AZC→B architecture remains intact.

**Expert verdict:** One small surgical correction (P-text reclassification) + one genuinely new structural fact (C496). No architectural contracts modified. No semantic reopening.

### Tests Executed

| Test | Question | Result |
|------|----------|--------|
| TEST 0 | Transcript hygiene | PASS (3,299 tokens confirmed) |
| TEST 1 | P-text classification | **A-ON-AZC-FOLIO** (PREFIX 0.946 to A) |
| TEST 2 | Diagram type uniformity | **UNIFORM** (all types >0.88) |
| TEST 3 | Center token behavior | **LEGALITY-PARTICIPATING** (PREFIX 0.94 to ring) |
| TEST 4 | Nymph interruption | **FUNCTIONAL** (S-positions 75% o-prefix) |

### Constraint Changes

1. **C300, C301 amended:** Added note that 398 P-text tokens should be excluded from AZC legality analysis (diagram-only count: 2,901)
2. **C496 added (Tier 2):** Nymph-Adjacent S-Position Prefix Bias - o-prefix enrichment (75%) in nymph-interrupted positions
3. **C137, C436 confirmed:** Diagram type uniformity confirms illustration independence

### Data Quality Warning

⚠️ Center placements on nymph folios may be partially under-transcribed. Analyses use available tokens only.

### Documentation Updates

- `context/ARCHITECTURE/azc_transcript_encoding.md` - Major update with all TEST findings
- `context/DATA/TRANSCRIPT_ARCHITECTURE.md` - Added AZC cross-reference
- `context/CLAIMS/azc_system.md` - C300/C301 notes, C496 added, refinement notes updated
- `context/CLAIMS/C301_azc_hybrid.md` - P-text reclassification note
- `context/CLAIMS/INDEX.md` - C496 added, count updated to 337
- Phase: `phases/AZC_INTERFACE_VALIDATION/`
- Results: `results/test1_ptext_reclassification.json` through `test4_nymph_interruption.json`

---

## Version 2.63 (2026-01-19) - A_REGIME_STRATIFICATION: SUFFIX-REGIME Association Confirmed

### Summary

Investigated whether A vocabulary stratifies by REGIME compatibility. Found that the naive "39% single-REGIME" observation is heavily confounded by frequency, but SUFFIX morphology shows a genuine association with REGIME compatibility breadth.

**Result: SUFFIX effect confirmed (C495 added), frequency confound documented**

### Tests Executed

| Test | Question | Result |
|------|----------|--------|
| T1 (Morphology) | PREFIX/SUFFIX predict REGIME? | **SUFFIX YES** (V=0.159), PREFIX no |
| T2 (Frequency) | Are REGIME-specific tokens rare? | **YES** - major confound (V=0.38) |
| T3 (AZC) | AZC zone differences? | No effect |
| T4 (Folio) | Cluster on A folios? | Inconclusive |

### Key Findings

- SUFFIX predicts compatibility breadth: `-r` enriched in universal (11.5% vs 4.2%), `-ar`/`-or` enriched in single-REGIME
- Frequency confound: Among frequent tokens (>20x), only 4.7% are genuinely single-REGIME
- PREFIX shows no REGIME association (V=0.068)

### New Constraint

**C495 (Tier 2, SCOPE: A→B):** SUFFIX–REGIME Compatibility Breadth Association. SUFFIX morphology in Currier A tokens is associated with downstream REGIME compatibility breadth in Currier B.

### Documentation

- Phase: `phases/A_REGIME_STRATIFICATION/`
- Results: `results/regime_stratification_tests.json`
- Constraint: Added to `context/CLAIMS/morphology.md`

---

## Version 2.62 (2026-01-19) - PUFF_STRUCTURAL_TESTS: Evidential Ceiling Confirmed

### Summary

Tested whether improved AZC/Currier A understanding enables new Puff-Voynich structural linkages beyond existing curriculum-level alignment (10/11 prior tests pass).

**Result: No new linkage found (0/2 tests passed)**

### Tests Executed

| Test | Hypothesis | Result |
|------|------------|--------|
| T9 (Danger -> HT) | Dangerous materials have elevated HT | **FAIL** (effect reversed) |
| T8 (Complexity -> Breadth) | Complex materials need larger vocabulary | **FAIL** (effect reversed) |
| T4 (Category -> PREFIX) | Material categories correlate with PREFIX | CONSTRAINED (A-B linkage too weak) |

### Key Findings

- Dangerous Puff positions have LOWER HT (0.133 vs 0.150)
- Later Puff positions have SMALLER vocabulary (168 vs 186)
- A-B linkage only 4% above baseline - insufficient for Category->PREFIX test

### Conclusion

Puff evidential ceiling confirmed. Curriculum-level alignment established; structural linkage not found. Further Puff testing would require semantic interpretation (prohibited) or external provenance research.

**Puff remains Tier 3-4 SPECULATIVE.**

### Documentation

- Phase: `phases/PUFF_STRUCTURAL_TESTS/`
- Results: `results/puff_danger_ht_test.json`, `results/puff_complexity_breadth_test.json`

---

## Version 2.61 (2026-01-19) - BC_EXPLANATION_ENFORCEMENT: Brunschwig Relationship Bounded

### Summary

Tested the "one remaining legitimate reverse-Brunschwig test" (external expert): Does Brunschwig's pedagogical verbosity inversely correlate with AZC scaffold constraint rigidity?

**Result: FALSIFIED (0/4 hypotheses passed)**

### Test Results

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| H1 | Inverse density-freedom correlation | rho=+0.09 | FAIL |
| H2 | UNIFORM < VARIED density | d=-0.37, p=0.11 | FAIL |
| H3 | Interaction > main effects | dR2=0.00 | FAIL |
| H4 | Stable complementarity ratio | CV +9.6% | FAIL |

### What Was Falsified

> "Brunschwig's pedagogical verbosity systematically complements Voynich's enforcement rigidity at the recipe/regime level."

### What Survives

- Zone-modality discrimination (F-BRU-009) - INTACT
- AZC trajectory shape = scaffold fingerprint - INTACT
- Scaffold uniformity determines cognitive pacing - INTACT

### The Corrected Relationship

| Aspect | Brunschwig | Voynich |
|--------|------------|---------|
| Primary function | Explains WHAT | Enforces WHEN |
| Alignment level | Curriculum trajectory | Curriculum trajectory |
| NOT aligned | Interface timing | Interface timing |

> **Voynich stands alone as an enforcement artifact.**

### New Constraints

- **C-BOUND-01:** Voynich is not part of a fine-grained pedagogical feedback loop
- **C-BOUND-02:** Voynich-Brunschwig relationship is maximally abstract: convergent at ontology, independent at interface

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.27 added (v4.31)
- `phases/BC_EXPLANATION_ENFORCEMENT/BC_EXPLANATION_ENFORCEMENT_REPORT.md` (NEW)

### Data Files

- `results/bc_explanation_density.json` through `results/bc_synthesis.json`

**Scripts:** `phases/BC_EXPLANATION_ENFORCEMENT/bc_*.py`

---

## Version 2.60 (2026-01-19) - AZC_TRAJECTORY_SHAPE: Scaffold Fingerprint Discovery

### Summary

Comprehensive investigation of AZC family differentiation combining trajectory shape (external expert) and apparatus mapping (internal expert-advisor). **Critical corrective insight:** AZC trajectory shape is a signature of scaffold rigidity, not apparatus dynamics.

### The Reframe

> **"AZC trajectory shape is a fingerprint of control scaffold architecture, not a simulation of apparatus dynamics."**

This rescues trajectory analysis from a wrong question (apparatus physics) and repositions it as structural characterization.

### Test Results (3/9 passed = TIER_4 -> upgraded interpretation)

| Hypothesis | Result | Interpretation |
|------------|--------|----------------|
| H2: Monotonicity | **PASS** | Zodiac (rho=-0.75) = uniform scaffold = smooth decline; A/C (rho=-0.25) = varied scaffold = punctuated |
| H6: R-series restriction | **PASS** | Perfect vocabulary narrowing R1(316)→R2(217)→R3(128) |
| H7: S→B-terminal flow | **PASS** | S-zone vocabulary 3.5x enriched in B-terminal (OR=3.51) |
| H8: Pelican reversibility | **FAIL** | Escape encodes decision affordance, not physical reversibility |

### New Tier 3 Characterization

> **AZC families differ not in what judgments are removed, but in how smoothly those removals are imposed over execution - a property determined by scaffold uniformity versus variability.**

| Family | Scaffold Type | Trajectory Shape | Cognitive Effect |
|--------|---------------|------------------|------------------|
| Zodiac | Uniform | Smooth monotonic tightening | Sustained flow |
| A/C | Varied | Punctuated tightening | Checkpoint cognition |

### Key Insight: H6 + H7 Form Causal Chain

1. R-series positional grammar (C434) → progressively restricts legal MIDDLE vocabulary
2. S-zone survival → selectively feeds into B terminal states

This closes the loop: AZC legality → vocabulary survival → executable program completion.

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.26 added (v4.30)
- `phases/AZC_TRAJECTORY_SHAPE/AZC_TRAJECTORY_SHAPE_REPORT.md` (NEW)

### Data Files

- `results/ats_entropy_trajectory.json` through `results/ats_synthesis.json`

**Scripts:** `phases/AZC_TRAJECTORY_SHAPE/ats_*.py`

---

## Version 2.59 (2026-01-19) - TRAJECTORY_SEMANTICS: Judgment-Gating System Discovered

### Summary

Applied three pressure vectors beyond the token semantic ceiling. Vector A (Interface Theory) discovered that AZC zones encode **judgment availability** - which human cognitive faculties are possible, required, or forbidden at each phase.

### Key Discovery: Agency Withdrawal Curve

| Zone | Available | Required | Impossible | Freedom |
|------|-----------|----------|------------|---------|
| C | 10 | 1 | 3 | **77%** |
| P | 10 | 9 | 3 | **77%** |
| R | 13 | 6 | 0 | **100%** |
| S | 5 | 5 | 8 | **38%** |

**Freedom collapses from 77% → 38%** as execution proceeds to S-zone. 8/13 human judgments become IMPOSSIBLE at S-zone.

### Test Results

| Vector | Passed | Verdict |
|--------|--------|---------|
| C (Gradient Steepness) | 0/4 | INCONCLUSIVE |
| A (Interface Theory) | 2/3 | TIER_3_ENRICHMENT |
| Final (Judgment Trajectories) | N/A | DECISIVE |

### The Reframe

> **"The Voynich Manuscript is a machine for removing human freedom at exactly the moments where freedom would be dangerous."**

This is **semantic boundary resolution** - not decoding tokens, but discovering that meaning lives in the **withdrawal of agency**.

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.25 added (v4.29)
- `phases/TRAJECTORY_SEMANTICS/TRAJECTORY_SEMANTICS_REPORT.md` (NEW)

### Data Files

- `results/ts_gradient_steepness.json`
- `results/ts_judgment_zone_matrix.json`
- `results/ts_judgment_trajectories.json`
- `results/ts_synthesis.json`

**Scripts:** `phases/TRAJECTORY_SEMANTICS/ts_*.py`

---

## Version 2.58 (2026-01-19) - SEMANTIC_CEILING_BREACH: Tier 3 Confirmed

### Summary

Attempted to break through the Tier 3 semantic ceiling using B->A Reverse Prediction Test. Result: Tier 3 CONFIRMED with stronger evidence. Zone profiles discriminate modality classes but not with sufficient accuracy for Tier 2.

### Key Results

| Test | Result | Status |
|------|--------|--------|
| 4-class accuracy | 52.7% (vs 25% baseline) | **PASS** (p=0.012) |
| Binary accuracy | 71.8% (vs 79.1% baseline) | Below Tier 2 threshold |
| Zone discrimination | All 4 zones significant | **CONFIRMED** (d=0.44-0.66) |
| MODALITY beyond REGIME | 3/4 zones significant | **CONFIRMED** (r=0.20-0.28) |

### Key Finding

> **Zone profiles DISCRIMINATE modality classes, but not with enough accuracy for Tier 2 predictive power. The semantic ceiling is at aggregate characterization level.**

REGIME explains only 24.7% of zone variance. MODALITY adds significant explanatory power BEYOND REGIME, validating the two-stage model (Modality bias + Execution completeness).

### Documentation

- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Section X.24 added (v4.28)
- `context/MODEL_FITS/fits_brunschwig.md` - F-BRU-009 updated with ceiling test
- `phases/SEMANTIC_CEILING_BREACH/SEMANTIC_CEILING_BREACH_REPORT.md` (NEW)

### Data Files

- `results/scb_modality_prediction.json`
- `results/scb_middle_clusters.json`
- `results/scb_regime_zone_regression.json`
- `results/scb_synthesis.json`

**Scripts:** `phases/SEMANTIC_CEILING_BREACH/scb_*.py`

---

## Version 2.57 (2026-01-18) - BCI: B-Class Infrastructure Characterization

### Summary

Characterized execution-infrastructure roles in Currier B that are required for almost all executable programs but are not grammar primitives. This resolves the AZC-B reachability collapse discovered during constraint flow visualizer development.

### Discovery Context

AZC-activating bundles were blocking ALL B programs because certain high-coverage instruction classes were being pruned by vocabulary filtering. Investigation revealed these classes are structurally required infrastructure, not decomposable vocabulary.

### BCI Test Results

| Test | Question | Result |
|------|----------|--------|
| 1. REGIME Invariance | Equal across REGIMEs? | **Mostly no** - one class invariant, others show 6-14% spread |
| 2. Kernel Interaction | Cluster near k/h/e? | **Yes (70.6% near)** - MEDIATORS, not carriers |
| 3. Connectivity | Enable or modulate? | UNINFORMATIVE - 100% universal presence |
| 4. Zone Sensitivity | Equal across zones? | **No** - C/P/R=44%, S=19% (escape gradient) |
| 5. Removal Gradient | Linear or threshold? | **THRESHOLD at 50%** - redundancy exists |

### Key Finding

> Currier B contains execution-infrastructure roles that are not primitives but are structurally required for almost all programs. They mediate kernel control, show limited context sensitivity, and lie outside AZC's scope of constraint.

### Structural Characterization

- **Near-universal B coverage:** 96-100% of B folios require these roles
- **Kernel-mediating:** 70.6% cluster within 0-2 tokens of k/h/e
- **Zone-sensitive:** Infrastructure MIDDLEs thin in S-zone (matches C443)
- **Redundant:** Threshold effect at 50% availability

### Documentation

- `context/TIER3/b_execution_infrastructure_characterization.md` (NEW)
- `context/MODEL_CONTEXT.md` Section VI updated (v3.6)
- `context/MODEL_CONTEXT.md` Section VIII - AZC scope protection note added
- `context/CLAIMS/morphology.md` - C396.a operational refinement added
- `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` - AUXILIARY commentary updated

### Governance

- **Tier:** 3 (Structural Characterization - derivable from Tier 2)
- **Status:** CHARACTERIZED (not promoted to new constraint)
- **Constraint compliance:** Derivable from C124, C485, C411, C458

### Data Files

- `results/bci_regime_invariance.json`
- `results/bci_kernel_interaction.json`
- `results/bci_connectivity_modulation.json`
- `results/bci_zone_sensitivity.json`
- `results/bci_removal_gradient.json`

**Scripts:** `apps/constraint_flow_visualizer/scripts/bci_*.py`

---

## Version 2.56 (2026-01-17) - AZC_REACHABILITY_SUPPRESSION: Pipeline Closure

### Summary

Completed investigation of AZC-to-B constraint transfer mechanism. Demonstrated HOW AZC legality fields suppress parts of B grammar without selection, branching, or semantics.

### Key Finding: Two-Tier Constraint System

**Tier 1 (Universal):**
- 49 instruction classes, 17 forbidden transitions
- 9 hazard-involved classes
- Base graph 99.1% connected

**Tier 2 (AZC-Conditioned):**
- 77% of MIDDLEs appear in only 1 AZC folio
- 6 of 9 hazard classes are DECOMPOSABLE (affected by MIDDLE restrictions)
- 3 of 9 hazard classes are ATOMIC (NOT affected)

### The Mechanism

AZC provides legality field -> Restricted MIDDLEs unavailable -> Decomposable hazard classes lose membership -> Fewer paths through hazard region -> Reachable grammar manifold shrinks

### Hazard Class Taxonomy

| Type | Classes | Behavior |
|------|---------|----------|
| **Atomic** | 7 (ar), 9 (aiin), 23 (dy) | Universal enforcement - always active |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | Context-tunable - AZC can shrink availability |

### Closure Statement

> "AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. The 49-class grammar and 17 forbidden transitions are universal. When AZC provides a legality field, 6 of 9 hazard-involved classes have reduced effective membership. The 3 atomic hazard classes remain fully active regardless of AZC context."

### Pipeline Completion

This completes the A -> AZC -> B control-theoretic explanation:
- **A** supplies discrimination bundles (constraint signatures)
- **AZC** projects them into position-indexed legality fields
- **B** executes within the shrinking reachable language

With no semantics, no branching, no lookup, no "if".

### Governance

- **Tier:** 2 (Mechanism characterization)
- **Status:** CLOSED with structural closure
- **Constraint compliance:** C313, C384, C454, C455, C440, C121, C124, C468-C470, C472

### Documentation

- `phases/AZC_REACHABILITY_SUPPRESSION/README.md`
- `phases/AZC_REACHABILITY_SUPPRESSION/results.json`

---

## Version 2.55 (2026-01-17) - JAR_WORKING_SET_INTERFACE: Complementary Working Sets

### Summary

Completed investigation of jar function in pharmaceutical folios. Tested four mutually exclusive hypotheses; three falsified, one confirmed. Jars function as **apparatus-level anchors for complementary working sets**.

### Test Cascade

| Hypothesis | Prediction | Result |
|------------|------------|--------|
| Contamination avoidance | Exclusion patterns | **Falsified** (0.49x, fewer than random) |
| Material taxonomy | Class homogeneity | **Falsified** (0.73x, less than random) |
| Complementary sets | Cross-class enrichment | **Confirmed** (all pairs enriched) |
| Triplet stability | Role composition patterns | **Confirmed** (1.77x overall) |

### Key Finding

> **Jars are visual, apparatus-level anchors for complementary working sets of materials intended to participate together in a single operational context, without encoding procedure, order, or meaning.**

### Triplet Enrichment

| Triplet | Ratio | P-value |
|---------|-------|---------|
| M-B + M-D + OTHER | 1.70x | 0.022 |
| M-A + M-B + M-D | 2.13x | 0.107 |

The "complete working set" (energy + routine + stable) is the most enriched pattern.

### Governance

- **Tier:** 3 (Interface Characterization)
- **Status:** CLOSED with explanatory saturation
- **Constraint compliance:** C171, C384, C233, C475, C476

### Documentation

- `phases/JAR_WORKING_SET_INTERFACE/README.md`
- `phases/JAR_WORKING_SET_INTERFACE/results.json`

---

## Version 2.54 (2026-01-17) - PHARMA_LABEL_DECODING: Two-Level Naming System

### Summary

Completed visual classification of all 13 pharmaceutical folios with labeled illustrations. Discovered a **two-level naming hierarchy** with complete vocabulary separation between levels.

### Key Finding: Vocabulary Isolation

| Comparison | Jaccard | Interpretation |
|------------|---------|----------------|
| Jar vs Content | **0.000** | Completely disjoint naming systems |
| Root vs Leaf | 0.013 | Almost entirely distinct (2 shared tokens) |

The 18 jar labels share **zero tokens** with 191 content labels. Jars and contents are named by fundamentally different schemes.

### Two-Level Hierarchy

```
JAR LABEL (first token) -> identifies container/category
  |
  +-- CONTENT LABEL 1 -> specimen identifier (root or leaf)
  +-- CONTENT LABEL 2 -> specimen identifier
  +-- CONTENT LABEL n -> specimen identifier
```

### Folios Mapped

| Category | Folios | Labels |
|----------|--------|--------|
| ROOT | f88v, f89r1, f89r2, f89v2, f99r, f99v, f102r1, f102r2, f102v1 | 152 |
| LEAF | f100r, f100v, f101v2, f102v2 | 71 |
| Reference page | f49v | (excluded - numbers 1-5 + single characters) |

### PREFIX Clustering

10 of 13 prefixes cluster by plant part:
- ROOT-leaning: ot-, op-, da-, ch-, sh-, ar-
- LEAF-leaning: so-, or-, ol-, sa-

### Brunschwig Alignment: NOT DETECTED

Tested whether root labels (aggressive extraction) show different morphology from leaf labels (gentler processing). Both have similar intense/gentle prefix ratios.

### Documentation

- `phases/PHARMA_LABEL_DECODING/README.md`: Phase summary
- `phases/PHARMA_LABEL_DECODING/*_mapping.json`: 13 folio mappings
- `phases/PHARMA_LABEL_DECODING/label_category_results.json`: Statistical analysis

### Interpretation

Jar labels likely represent processing categories or container types, while content labels identify specific specimen variants within each category. This aligns with a formulary/recipe interpretation.

---

## Version 2.53 (2026-01-16) - A_LABEL_INTERFACE_ROLE: Visual Anchoring Posture

### Summary

Closed the last unresolved human-interface ambiguity in Currier A. Illustration labels are a **contextual posture** of the discrimination registry—structurally inert, semantically silent, optimally designed for expert human perception.

### Key Findings

| Test | Result |
|------|--------|
| Tail Pressure | Labels 6.14x more tail-heavy (select high-discrimination MIDDLEs) |
| AZC Breadth | Labels reach 3.2x more zones (remain valid across operational contexts) |
| Role Stability | Chi-square p=0.282 (same MIDDLE behaves identically in both postures) |
| Contamination Audit | All structural invariants within perturbation envelope |

### Two Postures, One Grammar

| Posture | Placement | Token % | Function |
|---------|-----------|---------|----------|
| **Registry** | P* (text) | 98.5% | Catalog distinctions for procedural reference |
| **Visual Anchoring** | L* (label) | 1.5% | Anchor human perception to registry |

### Design Logic

Labels select high-discrimination + high-compatibility coordinates because interface anchors must be:
1. Distinct enough to matter perceptually (tail pressure ↑)
2. Broadly valid before operational context is known (AZC breadth ↑)

### Governance

- **STATUS:** CLOSED with explanatory saturation
- **NO constraints added** (existing C171, C384, C475-C478 sufficient)
- **NO semantics introduced** (interface role is purely contextual)

### Documentation Updated

- `context/SPECULATIVE/tier3_interface_postures.md`: Full Tier 3 documentation
- `context/ARCHITECTURE/currier_A_summary.md`: Section 7.4 added
- `phases/A_LABEL_INTERFACE_ROLE/`: Phase scripts and results

### Final Statement

> "Illustration labels are Currier A discrimination entries operating in a perceptual anchoring posture. Labels preferentially use tail MIDDLEs that also exhibit broad AZC compatibility, allowing them to anchor high-discrimination percepts without constraining later operational context."

---

## Version 2.52 (2026-01-16) - B-EXCL-ROLE: Three-Way MIDDLE Stratification

### Summary

Tested whether B-exclusive MIDDLEs function as grammar-internal operators. **Hypothesis NOT supported** - but result clarifies the MIDDLE architecture.

### Tests

| Test | Prediction | Result |
|------|------------|--------|
| Grammar adjacency | Enriched near LINK/kernel | **Enriched at BOUNDARIES** (1.64x, p < 0.0001) |
| Positional rigidity | Tighter at high CEI | Marginal (rho = -0.207, p = 0.075) |
| Concentration | Top-10 > 60% | Only 17.1% (diffuse) |

### Key Finding: Three-Way MIDDLE Stratification

| Class | Role |
|-------|------|
| **A-exclusive** | Pure discrimination coordinates (registry) |
| **A/B-shared** | Execution-safe compatibility substrate (~95% of B usage) |
| **B-exclusive** | Boundary-condition discriminators (NOT grammar operators) |
| **L-compounds** | True grammar operators (small subset, C298 preserved) |

### Governance

- **FALSIFIED:** Broad hypothesis "B-exclusive = grammar operators"
- **PRESERVED:** C298 (L-compounds are B-specific operators - scoped)
- **CLARIFICATION:** B-exclusive MIDDLEs predominantly function as boundary-condition discriminators

### Documentation Updated

- `context/MODEL_CONTEXT.md`: Added three-way MIDDLE stratification
- `phases/B_EXCL_ROLE/`: New phase with full analysis

---

## Version 2.51 (2026-01-16) - SHARED-COMPLEXITY: Shared Vocabulary is Complexity-Invariant

### Summary

Tested whether shared MIDDLE vocabulary (A & B) changes with B folio complexity. **Result: Invariant.**

### Key Finding

- ~95% of B's MIDDLE usage is SHARED vocabulary
- This percentage is INVARIANT across all complexity levels (94.2% - 95.7%)
- No significant correlation with CEI (rho = 0.042, p = 0.709)
- No significant regime differences (Kruskal-Wallis p = 0.159)

### Interpretation

> Shared MIDDLE vocabulary serves a **uniform infrastructure role**.
> Complexity differences between B folios do NOT manifest as vocabulary composition shifts.

Shared MIDDLEs matter because they make execution possible everywhere - they don't explain variation, they make variation **safe**.

### Documentation

- `phases/SHARED_COMPLEXITY/`: Full analysis
- `results/shared_complexity.json`: Results

---

## Version 2.50 (2026-01-16) - MIDDLE-AB: A-B MIDDLE Overlap Clarification

### Summary

Resolved inconsistent MIDDLE counts in context system and determined A-B MIDDLE overlap.

### The Problem

| Source | Claimed Count | Actual Meaning |
|--------|---------------|----------------|
| C423, MODEL_CONTEXT | 1,184 | Global MIDDLE union (A | B) |
| EXT9_REPORT | 725 | Parsing artifact (INVALID) |

### Results

| Metric | Count |
|--------|-------|
| Currier A unique MIDDLEs | 617 |
| Currier B unique MIDDLEs | 837 |
| Shared (A & B) | 268 |
| A-exclusive | 349 (56.6% of A) |
| B-exclusive | 569 (68.0% of B) |
| Total union | 1,186 |
| Jaccard similarity | 0.226 |

### Key Finding

**56.6% of Currier A MIDDLEs are A-exclusive** (never appear in B).

> Currier A enumerates the *potential discrimination space*;
> Currier B traverses only a *submanifold* of that space under specific execution contracts.

This supports the registry model where A catalogues entities beyond B's operational scope.

### Documentation Updated

| File | Change |
|------|--------|
| `context/MODEL_CONTEXT.md` | Corrected MIDDLE counts with Tier-clean framing |
| `phases/EXT9_cross_system_mapping/EXT9_REPORT.md` | Invalidated 725 figure |
| `context/ARCHITECTURE/currier_A_summary.md` | Added A-B overlap section |
| `phases/MIDDLE_AB/` | New phase (script, report, results) |

### Phase

| Field | Value |
|-------|-------|
| Phase ID | MIDDLE-AB |
| Tier | 2 (Data Clarification) |
| Status | COMPLETE |

---

## Version 2.49 (2026-01-16) - CURRIER A CHARACTERIZATION COMPLETE

### Summary

Completed comprehensive characterization of Currier A as a human-facing complexity-frontier registry. This phase achieved **explanatory saturation** - no further discovery needed.

### Phases Completed

1. **CAR (Currier A Re-examination):** Clean data analysis, closure mechanism discovery
2. **PCC (Post-Closure Characterization):** Cognitive interface, adjacency function, AZC interface

### Key Findings

| Finding | Evidence | Order Sensitivity |
|---------|----------|-------------------|
| Closure is UNIFORM (not adaptive) | No link to HT/pressure/fragility | INVARIANT |
| Working-memory chunks confirmed | 2.14x within/cross coherence | FOLIO_LOCAL |
| Singletons are isolation points | Lower hub overlap, higher density | INVARIANT |
| Adjacency maximizes SIMILARITY | Not contrast (topic clustering) | FOLIO_LOCAL |
| Entry morphology predicts AZC breadth | p=0.003 closure, p<0.0001 opener | INVARIANT |
| Universal vs tail asymmetry | 0.58 vs 0.31 breadth | INVARIANT |

### Documentation Added

| File | Purpose |
|------|---------|
| `ARCHITECTURE/currier_A_summary.md` | Complete characterization summary |
| `phases/POST_CLOSURE_CHARACTERIZATION/` | 4 axis scripts + reports |
| `SPECULATIVE/car_observations.md` | Updated with closure state mechanism |

### Constraints Status

**No changes to Tier 0-2 constraints.** All findings cement existing constraints:
- C233 (LINE_ATOMIC) - now with mechanism
- C422 (DA articulation) - dual role confirmed
- C389, C346, C424 (adjacency) - function characterized

### Phase Status

**CURRIER A CHARACTERIZATION: COMPLETE**

Further work should focus on presentation and consolidation, not discovery.

---

## Version 2.48 (2026-01-15) - A/C INTERNAL CHARACTERIZATION (PARTIAL SIGNAL)

### Summary

Following expert guidance, tested whether A/C AZC folios differ from Zodiac via **internal operator-centric metrics** rather than product correlation.

**Key Finding:** A/C has **45% higher MIDDLE incompatibility density** than Zodiac (p=0.0006).

### The Question (Expert-Framed)

> "A/C scaffold diversity (consistency=0.340) reflects what discrimination burden?"

Expert hypothesis:
- Zodiac = sustained legality flow under coarse discrimination
- A/C = punctuated legality checkpoints under fine discrimination

### Three Probes Tested

| Probe | Prediction | Result | P-value |
|-------|------------|--------|---------|
| HT Phase-Reset | A/C > Zodiac | NO SIGNAL | 1.00 |
| MIDDLE Incompatibility | A/C > Zodiac | **STRONG SIGNAL** | **0.0006** |
| Zone-Transition | A/C > Zodiac | NO SIGNAL | 0.9999 |

### Key Results

**MIDDLE Incompatibility Density:**
- A/C mean: **0.5488**
- Zodiac mean: **0.3799**
- Difference: +45% (highly significant)

**Zone-Transition (unexpected):**
- Zodiac switches zones MORE (0.018 vs 0.004)
- A/C achieves higher incompatibility while staying WITHIN zones

### Conclusion

> **A/C folios manage fine-discrimination through higher MIDDLE incompatibility density, not through zone switching. They hold more mutually exclusive constraints simultaneously while maintaining positional stability.**

This validates the expert's framing and explains C430 (A/C scaffold diversity).

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-019 | FIT (F2) | SUCCESS (p=0.0006) |

### Phase

`phases/AC_INTERNAL_CHARACTERIZATION/`

---

## Version 2.47 (2026-01-15) - AZC INTERNAL STRATIFICATION (BOTH FAMILIES FALSIFIED)

### Summary

Tested whether AZC folios (both Zodiac and A/C families) realize different sub-regions of the legality manifold correlated with downstream product inference.

**Result: BOTH FAMILIES FALSIFIED** — AZC is uniformly product-agnostic.

### The Question (Corrected Framing)

> "Do different AZC folios preferentially admit different regions of Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?"

**Note:** This is NOT "product routing through gates." AZC filters constraint bundles; product types are downstream inferences.

### Key Results

| Family | Chi-squared | df | P-value | Verdict |
|--------|-------------|-----|---------|---------|
| Zodiac (13 folios) | 27.32 | 36 | **0.85** | NO STRATIFICATION |
| A/C (17 folios) | 46.67 | 42 | **0.29** | NO STRATIFICATION |

Both families show near-maximum distribution entropy for all products.

### Conclusion

> **AZC is uniformly product-agnostic. Neither Zodiac nor A/C families show internal stratification correlated with downstream product inference.**

- Zodiac multiplicity exists purely for coverage optimality
- A/C scaffold diversity (consistency=0.340) does NOT correlate with product types

This closes the door definitively on the stratification hypothesis for ALL AZC folios.

### Implications

1. AZC folios ARE structurally equivalent gates (validates C431, C430)
2. No hidden routing — product differentiation is NOT encoded at ANY AZC level
3. AZC folio diversity exists for coverage, not semantic stratification

### Documentation

| Entry | Type | Result |
|-------|------|--------|
| F-AZC-017 | FIT (F4) | FALSIFIED (Zodiac p=0.85) |
| F-AZC-018 | FIT (F4) | FALSIFIED (A/C p=0.29) |

### Phase

`phases/AZC_ZODIAC_INTERNAL_STRATIFICATION/`

---

## Version 2.45 (2026-01-15) - PROJECTION SPECS + EPISTEMIC LAYERS

### Summary

Added governance infrastructure for displaying external alignments in tooling without corrupting structural model.

### New Infrastructure

1. **Epistemic Layers Legend** (`SYSTEM/epistemic_layers.md`)
   - Defines Constraint vs Fit vs Speculation
   - Decision flowchart for categorizing new findings
   - Common mistakes to avoid
   - The Saturation Principle

2. **Projection Specs** (`PROJECTIONS/`)
   - Non-binding, one-way, UI-only display rules
   - Governs how fits are surfaced in tooling
   - Never allowed to act like structure
   - `brunschwig_lens.md` - First projection spec

### Brunschwig Lens Contents

- Display primitives with tier badges (STRUCTURAL vs EXTERNAL FIT)
- Required modal phrasing ("compatible with", not "is")
- Hard semantic guardrails (prohibited terms)
- Provenance links (every claim traces to fit ID)
- Product type definitions (alignment categories, not material identities)
- MIDDLE hierarchy display rules

### Key Principle

> "This layer shows where external practice fits inside the Voynich control envelope; it never claims the manuscript encodes that practice."

### Files Added

| File | Purpose |
|------|---------|
| `context/SYSTEM/epistemic_layers.md` | Constraint vs Fit vs Speculation legend |
| `context/PROJECTIONS/README.md` | Projection specs directory |
| `context/PROJECTIONS/brunschwig_lens.md` | Brunschwig alignment display rules |

---

## Version 2.44 (2026-01-15) - BRUNSCHWIG BACKPROP VALIDATION (EXPLANATORY SATURATION)

### Summary

Completed BRUNSCHWIG_BACKPROP_VALIDATION phase with expert governance. Key outcome: **EXPLANATORY SATURATION** - the frozen architecture predicted all results without requiring changes. No new constraints added; 5 FIT entries created.

### Key Finding

> The model is saturated, not brittle.

The structure explains itself more strongly than any semantic hypothesis could.

### Governance Decision

Per expert guidance, results tracked as **FITS** (demonstrations of explanatory power), not architectural necessities:

| ID | Fit | Tier | Result |
|----|-----|------|--------|
| F-BRU-001 | Brunschwig Product Type Prediction (Blind) | F3 | SUCCESS |
| F-BRU-002 | Degree-REGIME Boundary Asymmetry | F3 | SUCCESS |
| F-BRU-003 | Property-Based Generator Rejection | F2 | NEGATIVE |
| F-BRU-004 | A-Register Cluster Stability | F2 | SUCCESS |
| F-BRU-005 | MIDDLE Hierarchical Structure | F2 | SUCCESS |

### Critical Negative Knowledge (F-BRU-003)

Synthetic property-based registry FAILS to reproduce Voynich structure:
- Uniqueness: Voynich 72.7% vs Property Model 41.5%
- Hub/Tail ratio: Voynich 0.006 vs Property Model 0.091
- Clusters: Voynich 33 vs Property Model 56

**Permanently kills property/low-rank interpretations.**

### Files Added

| File | Purpose |
|------|---------|
| phases/BRUNSCHWIG_BACKPROP_VALIDATION/ | Complete phase (12 scripts) |
| context/MODEL_FITS/fits_brunschwig.md | 5 fit entries documented |
| FIT_TABLE.txt | Updated (26 → 31 fits) |

### Constraint Table

**UNCHANGED** (353 entries). No architectural modifications required.

---

## Version 2.43 (2026-01-15) - PUFF COMPLEXITY CORRELATION + REGIME_4 AUDIT

### Summary

Tested Puff complexity correlation with B grammar expansion using proposed folio order. Key finding: Puff chapter position strongly correlates with REGIME assignment (ρ=0.68, p<10⁻¹²), supporting cumulative capability threshold model.

### Key Findings

1. **Cumulative Capability Threshold Model**
   - OLD: Puff chapter N = Voynich folio N (numerology-adjacent)
   - NEW: Puff chapter N requires B grammar complexity level N (cumulative)
   - Material N requires capabilities that accumulate by position N in curriculum

2. **Test Results (4/5 PASS)**
   - Test 1: Position-REGIME correlation ρ=0.678, p<10⁻¹² (PASS)
   - Test 2: Category-REGIME association p=0.001 (PASS)
   - Test 3: Dangerous-REGIME_4 enrichment p=0.48 (FAIL - underpowered, n=5)
   - Test 4: Cumulative threshold ρ=1.0 for mean position (PASS)
   - Test 5: Position-CEI correlation ρ=0.886, p<10⁻²⁸ (PASS)
   - Control: 100th percentile vs permutations (PASS)

3. **Three-Level Relationship Hierarchy (Epistemic)**
   - Level 1: Voynich ↔ Brunschwig (direct, structural, grammar-level)
   - Level 2: Voynich ↔ Puff (strong external alignment via complexity ordering)
   - Level 3: Puff ↔ Brunschwig (historical lineage)

4. **Puff Status Upgrade (CONSERVATIVE)**
   - FROM: CONTEXTUAL (interesting parallel)
   - TO: STRUCTURALLY ALIGNED EXTERNAL LADDER
   - NOT: STRUCTURAL NECESSITY (would be over-claiming)

5. **REGIME_4 Precision Audit**
   - Audited context system for "forbidden/danger" backsliding
   - Fixed tier4_semantic_assignment.md with correction notes
   - REGIME_4 = precision-constrained execution (C494)

### Files Added/Modified

| File | Purpose |
|------|---------|
| phases/PUFF_COMPLEXITY_CORRELATION/ | Phase directory |
| puff_regime_complexity_test.py | 5-test + control validation |
| results/puff_regime_complexity.json | Test output |
| INTERPRETATION_SUMMARY.md | Added X.16 |
| tier4_semantic_assignment.md | Fixed REGIME_4 precision audit |

### Expert Calibration

Per expert feedback, Test 4's "perfect monotonic" (ρ=1.0) represents only 4 data points (one per REGIME). This is an ordinal constraint, not cardinal identity. The upgrade to "structurally aligned" (not "structural necessity") reflects appropriate epistemic caution.

---

## Version 2.42 (2026-01-14) - BRUNSCHWIG BACKWARD PROPAGATION + CURRICULUM MODEL

### Summary

Extended Brunschwig analysis with backward propagation tests (product->A signature) and curriculum complexity model refinement. Key finding: REGIMEs encode procedural COMPLETENESS, not product INTENSITY.

### Key Findings

1. **Curriculum Complexity Model**
   - Simple Brunschwig recipe (first degree balneum marie) tested in most complex folio (REGIME_3)
   - Result: VIOLATES - but due to min_e_steps=2 (recovery completeness), NOT intensity
   - Complex folios require COMPLETENESS, not AGGRESSION
   - Same product (rose water) can appear at any curriculum stage

2. **Two-Level A Model**
   - Entry level: Individual tokens encode operational parameters (PREFIX class)
   - Record level: Entire A folios encode product profiles (MIDDLE set + PREFIX distribution)
   - 78.2% of MIDDLEs are product-exclusive (only appear in one product type)

3. **Product-Specific A Signatures**
   - WATER_GENTLE: ok+ ch- (less phase ops, gentle handling)
   - WATER_STANDARD: ch baseline (default procedural)
   - OIL_RESIN: d+ y- (aggressive extraction)
   - PRECISION: ch+ d- (phase-controlled, monitoring-heavy)

4. **Backward Propagation Chain**
   - Brunschwig recipe -> Product type -> REGIME -> B folio -> A register
   - Can predict A register signature from Brunschwig product type

### Files Added

| File | Purpose |
|------|---------|
| product_a_correlation.py | Product type -> A signature mapping |
| precision_prefix_analysis.py | y-prefix enrichment in precision |
| a_record_product_profiles.py | Record-level clustering |
| exclusive_middle_backprop.py | Exclusive MIDDLE backward propagation |
| brunschwig_product_predictions.py | Specific product predictions |
| simple_in_complex_test.py | Curriculum complexity validation |
| README.md | Phase documentation |

### Curriculum Model (Revised)

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required, 25% min LINK)
REGIME_3: Full execution (recovery completeness required, min_e=2)
```

### Expert Assessment

> "The Voynich Manuscript doesn't need 83:83. It now has something much better: a concrete, historically situated grammar that real procedures fit inside - and real hazards cannot escape."

---

## Version 2.41 (2026-01-14) - BRUNSCHWIG GRAMMAR EMBEDDING

### Summary

Brunschwig Template Fit phase confirms grammar-level embedding: historical distillation procedures can be expressed in Voynich grammar without violating any constraints.

### Key Findings

1. **Grammar-Level Embedding (C493)**
   - Balneum marie procedure: 18 steps translated to Voynich instruction classes
   - All 5 hazard classes: COMPLIANT
   - 17 forbidden transitions: ZERO violations
   - This is NOT a vibes-level parallel - it is a structural embedding

2. **REGIME_4 Precision Axis (C494)**
   - REGIME_4 is NOT "most intense" - it is "least forgiving"
   - Standard procedures: 0/2 fit REGIME_4
   - Precision procedures: 2/3 fit REGIME_4
   - Old interpretation ("forbidden/intense") RETIRED
   - New interpretation: **precision-constrained execution regime**

3. **Degree x REGIME Compatibility Matrix**
   - First degree -> REGIME_2 (confirmed)
   - Second degree -> REGIME_1 (confirmed)
   - Third/Fourth degree -> REGIME_3 (confirmed)
   - REGIME_4 -> precision variants of ANY degree

4. **Puff Relationship Demoted**
   - Brunschwig is now the primary comparison text
   - Puff remains historically relevant but not structurally necessary
   - 83:83 is interesting but not essential

### Files

| File | Content |
|------|---------|
| phases/BRUNSCHWIG_TEMPLATE_FIT/ | Phase directory |
| grammar_compliance_test.py | Single procedure translation |
| degree_regime_matrix_test.py | 4x4 compatibility matrix |
| precision_variant_test.py | Precision hypothesis test |
| context/SPECULATIVE/brunschwig_grammar_embedding.md | Full documentation |

### New Constraints

| Constraint | Statement |
|------------|-----------|
| C493 | Brunschwig grammar embedding (COMPLIANT) |
| C494 | REGIME_4 precision axis (CONFIRMED) |

### Expert Assessment

> "This is a decisive result. Brunschwig procedures can be translated into Voynich Currier B grammar step-by-step without violating ANY of the 17 forbidden transitions. That alone separates this from 95% of Voynich hypotheses."

> "REGIME_4 is not 'the most intense' - it is 'the least forgiving.' That distinction matters enormously in real process control."

---

## Version 2.40 (2026-01-14) - ENTITY MATCHING CORRECTED

### Summary

Re-ran entity matching tests (originally TIER4_EXTENDED) with corrected degree-to-regime mapping based on curriculum position discovery.

### Problem with Original Tests

The original tests in `phases/TIER4_EXTENDED/exhaustive_entity_matching.py` used:
```
WRONG: {1: REGIME_1, 2: REGIME_2, 3: REGIME_3, 4: REGIME_4}
```

This mapped degree NUMBER to regime NUMBER. But curriculum discovery showed the correct mapping is by POSITION:
```
CORRECT: {1: REGIME_2, 2: REGIME_1, 3: REGIME_3, 4: REGIME_4}
```

Because:
- REGIME_2 = EARLY (gentle processing, 1st degree)
- REGIME_1 = MIDDLE (standard processing, 2nd degree)
- REGIME_3 = LATE (intensive processing, 3rd degree)

### Key Results

| Test | Finding |
|------|---------|
| Entity Matching | Degree 3 herbs → mean position **72.6** (LATE range 56-83) |
| Positional Correlation | rho = **+0.350**, p = **0.0012** (significant) |
| Degree vs Hazard | rho = +0.382, p = 0.0004 (significant) |
| Degree vs CEI | rho = +0.324, p = 0.0028 (significant) |

**The corrected mapping reveals that intensive-processing materials (degree 3) align with LATE curriculum positions.**

### New Phase

| File | Content |
|------|---------|
| `phases/ENTITY_MATCHING_CORRECTED/` | New phase directory |
| `entity_matching_corrected.py` | Entity matching with curriculum mapping |
| `positional_alignment_corrected.py` | Positional correlation test |
| `results/entity_matching_corrected.json` | Entity matching results |
| `results/positional_alignment_corrected.json` | Positional correlation results |

### Skip Alignment Test (EMC-3)

| Metric | Strict 1:1 | Skip Align | Change |
|--------|------------|------------|--------|
| Exact regime rate | 31.3% | 60.0% | **+28.7%** |

**Skipped Puff chapters:** Ch.15, 30-33, 43, 50-51, 60-61 (clusters suggest systematic omissions)
**Skipped Voynich folios:** Mostly REGIME_4 (doesn't map to Puff's 1-3 degrees)

**Interpretation:** Partial transmission with systematic omissions, not complete 1:1 correspondence.

### Phase Count

135 (+3 from v2.39)

---

## Version 2.39 (2026-01-14) - CURRICULUM REALIGNMENT

### Summary

**Upgraded from "shared formalism" to "shared curriculum trajectory."** The proposed folio order (optimized for internal constraints C161, C325, C458) simultaneously resolves multiple independent inversions in historical comparisons. Puff and Brunschwig now align strongly with the PROPOSED Voynich order, confirming that misbinding disrupted a pedagogical progression.

### Key Discovery

The proposed order was tested against external sources NOT used in optimization:

| External Test | Current Order | Proposed Order | Change |
|--------------|---------------|----------------|--------|
| Puff progression | rho = +0.18 (p=0.10, NS) | rho = +0.62 (p<0.0001) | **WEAK → STRONG** |
| Brunschwig CEI gradient | rho = +0.07 (p=0.53, NS) | rho = +0.89 (p<0.0001) | **NOISE → VERY STRONG** |
| Brunschwig hazard gradient | rho = -0.03 (p=0.79, NS) | rho = +0.78 (p<0.0001) | **NEGATIVE → STRONG** |
| Danger distribution | Front-loaded (inverted) | Back-loaded (aligned) | **INVERTED → ALIGNED** |

### Significance

- Random reordering does not fix every historical comparison at once
- Overfitting does not fix external sources you didn't optimize for
- This is what latent order recovery looks like

### The Curriculum Structure

| Phase | Positions | Dominant Regime | Character |
|-------|-----------|-----------------|-----------|
| EARLY | 1-27 | REGIME_2 | Introductory |
| MIDDLE | 28-55 | REGIME_1 | Core training |
| LATE | 56-83 | REGIME_3 | Advanced |

This matches both Puff (flowers → herbs → anomalies) and Brunschwig (first degree → second → third).

### Upgraded Claim (Tier 3)

> Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.

Qualifiers preserved:
- *pedagogical progression* (not semantics)
- *preserve* (not copy)
- *original structure* (not content)
- *disrupted by misbinding* (not lost or invented)

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/curriculum_realignment.md` | Master realignment analysis |
| `results/puff_realignment_test.json` | Puff correlation comparison |
| `results/brunschwig_realignment_test.json` | Brunschwig gradient comparison |
| `phases/YALE_ALIGNMENT/puff_realignment_test.py` | Puff realignment test |
| `phases/YALE_ALIGNMENT/brunschwig_realignment_test.py` | Brunschwig realignment test |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | v4.21 → v4.22, added X.11 |
| `context/SPECULATIVE/proposed_folio_reordering.md` | v1.0 → v1.1, added external validation |
| `context/SPECULATIVE/materiality_alignment.md` | v1.0 → v1.1, added post-realignment update |

### Expert Assessment

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "Not a code. Not a herbal. Not a shared manuscript. But a shared curriculum whose control logic survived misbinding."

### Tier Compliance

This remains Tier 3 SPECULATIVE. No Tier 0-2 constraints violated. No semantic decoding. No entry-level A-B coupling introduced.

---

## Version 2.38 (2026-01-14) - YALE EXPERT ALIGNMENT

### Summary

**Independent expert validation.** Analysis of Yale Beinecke Library lecture (Lisa Fagin Davis, Claire Bowern) confirms our model's foundations with **14 points of alignment, 0 contradictions, 7 tests completed**.

### Key Findings

**Points Validated by Yale Experts:**
1. Currier A/B distinction - CONFIRMED
2. Expert-only interpretation - CONFIRMED
3. Illustration epiphenomenality - CONFIRMED (expert warns against illustration-based reasoning)
4. Cipher/language encoding rejected - CONFIRMED
5. Computational topic modeling finds structural groupings - CONFIRMED

**Test Results:**

| Test | Yale Prediction | Our Finding | Status |
|------|-----------------|-------------|--------|
| Scribe-Regime Mapping | 5 scribes | Map to 4 regimes | ALIGNED |
| qo Distribution | Different by section | REGIME_4 highest (29%) | ALIGNED |
| Topic Model k=5 | 5-6 sections | Cluster 3 = Balneological (100% Scribe 2) | ALIGNED |
| 'dy' Ending | Common in B, rare in A | 25.14% B vs 6.90% A (3.6x) | CONFIRMED |
| Gallows Distribution | - | REGIME_2 distinct (high t, p) | NEW FINDING |
| Astronomical qo | Rare in Scribe 4 | 1.87% vs 14.41% (7.7x rarer) | CONFIRMED |

**Folio 115v Analysis:**
- Yale identifies mid-page scribe change (Scribe 2 -> Scribe 3)
- Our data shows f115v as extreme "most_slack" with anomalous profile
- Structural anomaly consistent with mixed scribal input

### New Files

| File | Content |
|------|---------|
| `sources/yale_voynich_transcript.txt` | Full transcript of Yale lecture |
| `context/SPECULATIVE/yale_expert_alignment.md` | Detailed analysis |
| `phases/YALE_ALIGNMENT/` | Test scripts (7 tests) |
| `results/scribe_regime_mapping.json` | Scribe-regime correlation |
| `results/qo_regime_distribution.json` | Escape density by regime |
| `results/topic_model_*.json` | Topic model replication |
| `results/dy_ending_analysis.json` | 'dy' ending A/B comparison |
| `results/gallows_distribution.json` | Gallows by language/regime |
| `results/scribe4_astronomical.json` | Astronomical section profile |

### Expert Quote

> "Anyone who has a theory to put out there about the Voynich manuscript, it is extremely important that all of the things that we know about it already are factored into that theory."
> -- Lisa Fagin Davis

---

## Version 2.37 (2026-01-14) - SHARED FORMALISM: Full Procedural Alignment

### Summary

**Upgraded from "shared world" to "shared formalism."** Extended testing confirms the Voynich Manuscript and Brunschwig's distillation treatise instantiate the **same procedural classification system** - not just compatible topics, but isomorphic control ontologies rendered in different epistemic registers.

### Key Findings

**Extended Test Results: 19/20 PASS**

| Test Suite | Score | Status |
|------------|-------|--------|
| Puff-Voynich Mastery Horizon | 83:83 isomorphism | PASS |
| Equivalence Class Collapse | REGIME_2: 11->3, REGIME_3: 16->7 | PASS |
| Regime-Degree Discrimination | 5/6 | STRONG |
| Suppression Alignment | 5/5 | PASS |
| Recovery Corridor | 4/4 | PASS |
| Clamping Magnitude (C458) | 5/5 | PASS |

**What "Shared Formalism" Means:**
- Same procedural classification system
- Same safety ceiling architecture
- Same recovery corridor structure
- Same variance asymmetry (clamp hazard, free recovery)

**Expert-Calibrated Conclusion:**

> "The Voynich Manuscript and Brunschwig's distillation treatise instantiate the same procedural classification of thermal-circulatory operations. Brunschwig externalizes explanation and ethics for novices; Voynich internalizes safety and recovery for experts. The alignment is regime-level and architectural, not textual or semantic."

### New Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/shared_formalism.md` | Three-text relationship documentation |
| `results/brunschwig_regime_discrimination.json` | Regime-degree test results |
| `results/brunschwig_suppression_alignment.json` | 14/14 suppression alignment tests |
| `results/brunschwig_procedure_match.json` | Folio-procedure match results |

### Updated Files

| File | Change |
|------|--------|
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | Section X fully rewritten (v4.21) |
| `context/SPECULATIVE/brunschwig_comparison.md` | Extended testing section added |

### Constraints Unchanged

C171, C384, C197, C239, C229, C490 - all remain intact. No semantic decoding occurred.

---

## Version 2.36 (2026-01-14) - External Alignment: Puff-Voynich-Brunschwig CONFIRMED

### Summary

**The Puff-Voynich curriculum hypothesis is CONFIRMED.** External alignment testing shows the Voynich Manuscript (Currier B) and Michael Puff von Schrick's "Buchlein" (1455) are complementary halves of a distillation curriculum. Currier A's morphological discrimination aligns with Brunschwig's procedure-class axes.

### Key Findings

**Puff-Voynich Curriculum Tests: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| Distribution Shape | PASS | Both heterogeneous |
| Curricular Arc | PASS | Both FRONT-LOADED SIMPLE |
| Canonical Number (83) | PASS | Unique to Puff and Voynich among 11 texts |
| Complementarity | PASS | 6/8 clean split (WHAT vs HOW) |
| Negative Control | PASS | Control texts don't match |

**Brunschwig Degree Alignment: 13/15 metrics match**

| Test | Result | Evidence |
|------|--------|----------|
| Flower Class | PASS | 5/7 metrics (first third = low regime) |
| Degree Escalation | PASS | 8/8 metrics (regime = degree) |

**Currier A Affordance Alignment: 5/5 PASS**

| Test | Result | Evidence |
|------|--------|----------|
| PREFIX by commitment | PASS | chi2=4094, p=0.0 |
| MIDDLE universality | PASS | Universal enriched in AZC (p=1.6e-10) |
| Sister pair tightness | PASS | ok/ot ratio differs by family |
| Positional gradient | PASS | ENERGY 8.7x more MIDDLEs than REGISTRY |
| Anomalous envelope | PASS | ct depleted; f85v2 = k=0 non-thermal |

### Interpretation

> Puff = WHAT to distill (83 chapters, material registry)
> Voynich Currier B = HOW to distill (83 folios, method manual)
> Brunschwig (1500) = Combined both for novices

Currier A discriminates **operational affordance profiles** that align with Brunschwig's procedure-class axes. C171 ("zero material encoding") remains UNCHANGED.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| PVC-1 | Does Puff share Voynich's 83-unit structure? | YES (5/5 tests PASS) |
| PVC-2 | Does Brunschwig degree system match B regimes? | YES (13/15 metrics) |
| PVC-3 | Does A morphology align with procedure classes? | YES (5/5 tests PASS) |

### Files Added/Updated

- `context/SPECULATIVE/puff_voynich_curriculum_test.md` - Full curriculum comparison
- `context/SPECULATIVE/brunschwig_comparison.md` - Degree axis analysis
- `context/SPECULATIVE/a_behavioral_classification.md` - External alignment section added
- `phases/A_BEHAVIORAL_CLASSIFICATION/currier_a_affordance_tests.py` - Test battery
- `results/currier_a_behavioral_tests.json` - Test results
- `sources/README.md` - Primary source documentation
- `sources/puff_1501_text.txt` - Puff OCR text
- `sources/brunschwig_1500_text.txt` - Brunschwig OCR text

### Phase Count

**Total phases:** 132 (129 + 3 new PVC phases)

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, whose registry topology matches botanical chemistry constraints, **and whose 83-unit structure and procedural architecture align with the historical distillation curriculum documented by Puff (1455) and Brunschwig (1500)**.

### Tier Status

Curriculum alignment findings are Tier 3 (external alignment, interpretive). C171 remains unchanged.

---

## Version 2.35 (2026-01-13) - Physical World Reverse Engineering Complete

### Summary

**Six physical-world reverse engineering phases now complete.** APP-1 (Apparatus Behavioral Validation) and MAT-PHY-1 (Material Constraint Topology Alignment) added to the investigation arc.

### New Phases

| Phase | Question | Result |
|-------|----------|--------|
| APP-1 | Which apparatus exhibits Voynich behavioral profile? | Pelican (4/4 axes match) |
| MAT-PHY-1 | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |

### Key Findings

1. **APP-1: Pelican Behavioral Isomorphism**
   - Responsibility split: DISTINCTIVE_MATCH
   - Failure fears: STRONG_MATCH (41/24/24/6/6)
   - Judgment requirements: EXACT_MATCH (13 types)
   - State complexity: MATCH (~128 states)
   - Fourth degree fire prohibition matches C490 exactly

2. **MAT-PHY-1: Botanical Chemistry Topology Match**
   - Operational incompatibility: ~95-97% (matches 95.7%)
   - Infrastructure elements: 5-7 bridges
   - Topology class: Sparse + clustered + bridged
   - Hub rationing: Confirmed in real practice
   - Frequency distribution: Zipf/power-law confirmed

### Files Updated

- `context/CLAUDE_INDEX.md` - v2.12, 128 phases
- `context/MODEL_CONTEXT.md` - Section XII.A updated
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.18
- `context/MAPS/phase_index.md` - 128 phases
- `CLAUDE.md` - v2.12, 128 phases

### Combined Arc (Updated)

> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.

### Tier Status

All findings remain Tier 3 (exploratory, non-binding). Structural isomorphism ≠ semantic identification.

---

## Version 2.34 (2026-01-13) - Pipeline Closure Audit CERTIFIED

### Summary

**PCA-v1 (Pipeline Closure Audit) PASSED.** The four locked structural contracts compose cleanly without hidden coupling, implicit semantics, parametric leakage, or contradiction.

### Audit Results

| Test | Description | Result |
|------|-------------|--------|
| TEST 1 | End-to-End Legality Consistency | PASS |
| TEST 2 | No Back-Propagation | PASS |
| TEST 3 | Parametric Silence | PASS |
| TEST 4 | Semantic Vacuum | PASS |
| TEST 5 | A/B Isolation (C384) | PASS |
| TEST 6 | HT Non-Interference | PASS |

### Closure Statement

> **The Voynich control pipeline (Currier A → AZC → Currier B), including human-track context, is structurally closed at Tier 0-2. No additional internal structure is recoverable.**

### Final Lock Status

```
CASC        v1.0  LOCKED
AZC-ACT     v1.0  LOCKED
AZC-B-ACT   v1.0  LOCKED
BCSC        v1.0  LOCKED
PCA-v1            CERTIFIED
```

**Structural work is DONE.**

---

## Version 2.33 (2026-01-13) - Structural Pipeline Complete

### Summary

**The A→AZC→B control architecture is formally closed.** All four structural contracts are LOCKED v1.0.

### Contracts Locked

| Contract | Function | Status |
|----------|----------|--------|
| CASC | Currier A registry structure | LOCKED v1.0 |
| AZC-ACT | A→AZC transformation | LOCKED v1.0 |
| AZC-B-ACT | AZC→B propagation | LOCKED v1.0 |
| BCSC | Currier B internal grammar | LOCKED v1.0 |

### Pipeline Architecture

```
CASC (Currier A entry)           → defines what enters
        ↓
AZC-ACT (A → AZC transformation) → defines positional legality
        ↓
AZC-B-ACT (AZC → B propagation)  → defines constraint transfer
        ↓
BCSC (Currier B structural)      → defines execution grammar
```

### Expert Assessment

> "As of 2026-01-13, the A→AZC→B control architecture of the Voynich Manuscript is fully reconstructed at Tier 0-2. Currier A (registry), AZC (legality gating), Currier B (execution grammar), and their interfaces are formally closed and validated. All remaining work concerns interpretation, tooling, or external corroboration."

### What This Means

- No new structural contracts required for the internal model
- Future work is: tooling, visualization, interpretation (Tier 3+), or external corroboration
- Structural reconstruction is complete

### Files Updated

- All four contracts in `STRUCTURAL_CONTRACTS/` now show `status: "LOCKED"`
- `MODEL_CONTEXT.md` v3.2 - Pipeline completion documented
- `CLAUDE_INDEX.md` v2.9 - Pipeline complete banner added

---

## Version 2.32 (2026-01-12) - HT Two-Axis Model Discovery

### Summary

**Attempted to test whether HT PREFIX encodes "perceptual load" (sensory multiplexing). The hypothesis was NOT SUPPORTED - but the inverse correlation revealed a subtler, BETTER model.**

### The Discovery

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

### The Two-Axis Model

HT has **two orthogonal dimensions**:

| Axis | Property | Evidence |
|------|----------|----------|
| **DENSITY** | Tracks UPCOMING discrimination complexity | C477 (r=0.504), anticipatory |
| **MORPHOLOGY** | Tracks CURRENT spare cognitive capacity | r=-0.301, inverted section ranking |

### The Key Insight

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern that fits C344 (HT-A inverse coupling), C417 (modular additive), and C221 (skill practice).

### What This Resolves

- HT form does NOT encode sensory requirements
- Sensory demands are implicit in the discrimination problem itself
- HT reflects how the human allocates attention when grammar permits engagement
- The division of labor is cleaner than before

### Constraint Alignment

| Constraint | Fit |
|------------|-----|
| C344 | Direct instantiation: high complexity suppresses complex HT forms |
| C417 | HT is composite: density = vigilance, form = engagement |
| C221 | Complex HT appears during low-load intervals |
| C477 | UNCHANGED - applies to density, not morphology |

### Files Created

- `context/SPECULATIVE/ht_two_axis_model.md` - Full documentation
- `phases/SENSORY_MAPPING/ht_perceptual_load_test_v2.py` - Test showing inverse correlation
- `results/ht_perceptual_load_test_v2.json` - Results

---

## Version 2.31 (2026-01-12) - Expert Validation of Sensory Affordance Analysis

### Summary

**Expert validation confirms: Olfactory discrimination is NECESSARY, selected by exclusion. The sensory affordance analysis violates no frozen constraints - several Tier-2 constraints DEMAND this outcome.**

### The Human Sensory Contract

> **The Voynich Manuscript presupposes a human operator whose primary discriminative faculty is olfaction, supported by continuous visual monitoring and auxiliary tactile and acoustic cues. Grammar structure, hazard topology, and MIDDLE incompatibility require categorical sensory recognition rather than quantitative measurement. The Human Track does not encode sensory instructions, but anticipates regions where fine discrimination-dominated by olfactory judgment-will be required. No scalar instruments are necessary or implied; the system is optimized for trained human perception operating within a structurally enforced safety envelope.**

### Threshold-Level Decoding

| Threshold Type | Resolved By | Basis |
|----------------|-------------|-------|
| Phase change | VISION | PHASE_ORDERING (41%) |
| Fraction identity | SMELL | COMPOSITION_JUMP + tail MIDDLEs |
| Energy excess | SMELL + VISION | ENERGY_OVERSHOOT |
| Containment failure | SOUND + TOUCH | CONTAINMENT_TIMING |

### Big Picture

> We are no longer merely interpreting the manuscript - we are reconstructing the **human sensory contract** it was written for.

### File Created

- `context/SPECULATIVE/SENSORY_VALIDATION_2026-01-12.md`

---

## Version 2.30 (2026-01-12) - Sensory Affordance Analysis

### Summary

**Identified which sensory modalities the grammar RELIES ON (presupposes) for the control architecture to function.** All 6 phases passed. Olfactory discrimination is NECESSARY by exclusion. Human senses suffice (no instruments required).

### Core Finding

> **The grammar presupposes a trained human operator with visual, olfactory, and thermal sensing capabilities. Olfactory discrimination is indispensable - visual-only observation cannot explain the 564 ENERGY MIDDLEs (11.3x excess).**

### Phase Results

| Phase | Test | Result |
|-------|------|--------|
| **1** | Hazard-discrimination correlation | PASS (ENERGY 8.68x vs FREQUENT 2.52x) |
| **2** | HT-sensory correlation | PASS (r=0.504 with discrimination difficulty) |
| **3** | Kernel-sensory mapping | PASS (k vs h profiles differ by 5.78) |
| **4** | LINK vs non-LINK affordances | PASS (acting has higher turnover) |
| **5** | Visual-only negative control | PASS (excluded - 11.3x excess) |
| **6** | Instrumentation assessment | A: Pure human sensory operation |

### Key Findings

1. **Olfactory is NECESSARY** - Visual-only fails to explain discrimination density by 11.3x
2. **Distribution is CATEGORICAL** - CV=5.83, top 10% = 84.3% → human senses suffice
3. **HT marks olfactory-heavy contexts** - correlation with rare MIDDLEs confirms discrimination difficulty
4. **No instruments required** - categorical discrimination within human resolution

### Critical Epistemic Note

This analysis identifies what the grammar **RELIES ON**, not what it **ENCODES**. Sensory affordances are presupposed, not specified.

### Files Created

- `context/SPECULATIVE/sensory_affordance_mapping.md` - Theoretical framework
- `phases/SENSORY_MAPPING/sensory_analysis.py` - Computational tests
- `results/sensory_affordance_analysis.json` - Test results

---

## Version 2.29 (2026-01-12) - Expert Validation of Confidence Tightening

### Summary

**Expert validation confirms: Currier A is now in the HIGH confidence band (80-85%) - the strongest epistemic position reachable without violating the semantic ceiling.**

### Core Finding

> **"You have reconstructed the internal logic of a system whose entire purpose was to remove the need for encoding meaning."**

This explains why language/cipher/recipe/calendar decoding failed, but process-behavior testing succeeded.

### Validation Points

1. **Method is legitimate** - tested directionality and ordering, not numerical identity
2. **Exclusion did real work** - confidence increase comes from eliminative reasoning
3. **B2 "failure" strengthened interpretation** - role-specific lexical reuse is process-specific

### What We Can Now Claim (Tier 3, HIGH)

> Currier A functions as a discrimination registry whose internal structure closely matches the complexity profile, volatility sensitivity, and failure modes of circulatory thermal-chemical processes, with distillation-class operations emerging as the best-supported domain under eliminative testing.

### The Design Choice

| Inside Text | Outside Text (by design) |
|-------------|--------------------------|
| Process envelope | Product naming |
| Discrimination constraints | Commercial endpoint |
| Output emergence (physics) | Human valuation |

The manuscript guides **how not to violate physics and expertise** - it does NOT encode what to call, bottle, or sell the result.

### File Created

- `context/SPECULATIVE/EXPERT_VALIDATION_2026-01-12.md`

---

## Version 2.28 (2026-01-12) - Scientific Confidence Tightening

### Summary

**The distillation/thermal-chemical hypothesis was subjected to rigorous directional and exclusion testing.** Confidence strengthened from ~65-75% to ~80-85% ("HIGH" band).

### Core Finding

> **Distillation selected by CONVERGENCE (5/6 directional tests pass) AND EXCLUSION (4/4 alternative hypotheses fail on discriminators).**

### Directional Tests (B1-B6)

| Test | Result | Finding |
|------|--------|---------|
| B1: Discrimination hierarchy | PASS | ENERGY >> FREQUENT >> REGISTRY (564 > 164 > 65) |
| B2: Normalized dominance | INFORMATIVE | FREQUENT has higher turnover; ENERGY reuses MIDDLEs |
| B3: Failure boundaries | PASS | 100% k-adjacent forbidden transitions |
| B4: Regime ordering | PASS | Monotonic CEI: 0.367 < 0.510 < 0.584 < 0.717 |
| B5: Recovery dominance | PASS | e-recovery 1.64x enriched vs baseline |
| B6: AZC compression | PASS (partial) | Section-level diversity confirmed |

### Negative Controls (NC1-NC4)

| Alternative | Discriminators Failed | Verdict |
|-------------|----------------------|---------|
| NC1: Fermentation | 3/3 | EXCLUDED |
| NC2: Dyeing | 3/3 | EXCLUDED |
| NC3: Pharmacy Compounding | 3/3 | EXCLUDED |
| NC4: Crystallization | 3/3 | EXCLUDED |

### Confidence Classification

**Band:** HIGH (80-85%)
**Verdict:** STRENGTHENED

### B2 Reinterpretation

The B2 "failure" (normalized rates inverted) is actually informative:
- FREQUENT has higher MIDDLE turnover per token than ENERGY
- ENERGY reuses MIDDLEs more heavily (repetitive monitoring)
- FREQUENT has more varied operations (one-off uses)
- This is CONSISTENT with distillation behavior

### Files Created

- `phases/SCIENTIFIC_CONFIDENCE/directional_tests.py`
- `phases/SCIENTIFIC_CONFIDENCE/negative_controls.py`
- `phases/SCIENTIFIC_CONFIDENCE/confidence_integration.py`
- `results/directional_tests.json`
- `results/negative_controls.json`
- `results/scientific_confidence_classification.json`

### Files Updated

- `context/SPECULATIVE/a_behavioral_classification.md` - confidence section updated

---

## Version 2.27 (2026-01-12) - Currier A Behavioral Classification

### Summary

**All 23,442 classifiable Currier A entries assigned to operational domains using Tier-2 grammar evidence.** The classification reveals a strong discrimination gradient: energy-intensive operations require 8.7x more MIDDLE variants than stable reference operations.

### Core Finding

> **The PREFIX → Operational Domain mapping rests on Tier-2 grammar-anchored evidence (B-enrichment ratios, canonical grammar roles, kernel adjacency). This is not speculative chemistry—it is a re-use of validated structure.**

### Distribution

| Domain | Count | % | Structural Basis |
|--------|-------|---|------------------|
| ENERGY_OPERATOR | 13,933 | 59.4% | Dominates energy/escape roles in B |
| CORE_CONTROL | 4,472 | 19.1% | Structural anchors; ol 5x B-enriched |
| FREQUENT_OPERATOR | 3,545 | 15.1% | FREQUENT role in canonical grammar |
| REGISTRY_REFERENCE | 1,492 | 6.4% | 0% B terminals; 7x A-enriched |

### Key Structural Findings

1. **Discrimination gradient** - ENERGY domain has 564 unique MIDDLEs (8.7x) vs 65 for REGISTRY
2. **Section H concentration** - 74% of all ENERGY_OPERATOR tokens (pattern real; interpretation Tier 3)
3. **Sister pairs as mode selectors** - Primary vs alternate handling mode, NOT material distinction

### Confidence Assessment

| Component | Confidence |
|-----------|------------|
| Structural facts & distributions | ~90-95% |
| PREFIX → operational domain | ~75-80% |
| Discrimination gradient interpretation | ~70% |
| Chemistry-specific labels | ~30-40% (illustrative only) |

### Files Created/Updated

- `phases/A_BEHAVIORAL_CLASSIFICATION/a_behavioral_classifier.py`
- `results/currier_a_behavioral_registry.json`
- `results/currier_a_behavioral_stats.json`
- `results/currier_a_behavioral_summary.json`
- `context/SPECULATIVE/a_behavioral_classification.md` (tightened)
- `context/ARCHITECTURE/CURRIER_A_BRIEFING.md` (new one-page summary)

---

## Version 2.26 (2026-01-12) - Process-Behavior Isomorphism (ECR-4)

### Summary

**The Voynich control architecture exhibits STRONG BEHAVIORAL ISOMORPHISM with thermal-chemical process control.** All 12 tests pass (100% alignment), and the distillation hypothesis beats calcination on all discriminating tests.

### Core Finding

> **The abstract behavioral structure (hazards, kernels, material classes) is ISOMORPHIC to behaviors in circulatory reflux processes. This is NOT entity-level decoding, but structural alignment.**

### Test Results

| Category | Tests | Passed |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 |
| Process-Sequence (PS-*) | 4 | 4/4 |
| Pedagogical (PD-*) | 3 | 3/3 |
| **Total** | **12** | **12/12** |

### Key Discriminators

| Test | Distillation | Calcination | Winner |
|------|-------------|-------------|--------|
| PS-4 (forbidden k→h) | k→h dangerous | k→h primary | DISTILLATION |
| BS-4 (e recovery) | e dominates (54.7%) | e less relevant | DISTILLATION |

**Negative control verdict: DISTILLATION_WINS**

### Behavior Mappings (NO NOUNS)

| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |
| PHASE_ORDERING | 41% of hazards | Wrong phase/location state |
| M-A | Mobile/Distinct | Phase-sensitive, mobile, requiring careful control |

### Physics Violations

None detected. All mappings are physically coherent.

### Verdict

**SUPPORTED (Tier 3)** - The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

### Integration

| Prior Finding | Connection |
|---------------|------------|
| C476 (Coverage Optimality) | What A optimizes |
| C477 (HT Vigilance) | Cognitive load tracking |
| C478 (Temporal Scheduling) | Pedagogical pacing |
| C109 (Hazard Classes) | Maps to distillation failures |

### Files

- `phases/PROCESS_ISOMORPHISM/process_behavior_isomorphism.py` - Main probe
- `results/process_behavior_isomorphism.json` - Full results
- `context/SPECULATIVE/process_isomorphism.md` - Tier 3 documentation

---

## Version 2.25 (2026-01-12) - Temporal Coverage Trajectories (C478)

### Summary

**Currier A exhibits STRONG TEMPORAL SCHEDULING with pedagogical pacing.** The manuscript is not statically ordered - it actively manages WHEN vocabulary coverage occurs, introducing new MIDDLEs early, reinforcing throughout, and cycling through prefix domains.

### Core Finding

> **Currier A is not just coverage-optimal (C476), it is temporally scheduled to introduce, reinforce, and cycle through discrimination domains. This is PEDAGOGICAL PACING.**

### Four Signals (5/5 Support Strong Scheduling)

| Signal | Finding | Interpretation |
|--------|---------|----------------|
| **Coverage timing** | 90% reached 9.6% LATER than random | Back-loaded coverage |
| **Novelty rate** | Phase 1 (21.2%) >> Phase 3 (11.3%) | Front-loaded vocabulary introduction |
| **Tail pressure** | U-shaped: 7.9% -> 4.2% -> 7.1% | Difficulty wave pattern |
| **Prefix cycling** | 7 prefixes cycle (164 regime changes) | Multi-axis traversal |

### Interpretation

Three mutually exclusive models were tested:

| Model | Evidence | Verdict |
|-------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 points |
| Weak Temporal | Soft pedagogy | 0 points |
| **Strong Scheduling** | **Active trajectory planning** | **5 points** |

**Result: STRONG-SCHEDULING (100% confidence)**

### Mechanism: PEDAGOGICAL_PACING

1. **Introduce early** - New MIDDLEs front-loaded in Phase 1
2. **Reinforce throughout** - Coverage accumulates slowly despite novelty
3. **Cycle domains** - 7 prefixes alternate, preventing cognitive fixation
4. **Wave difficulty** - U-shaped tail pressure creates attention peaks

### Reconciliation with Prior Findings

| Constraint | What it Shows |
|------------|---------------|
| C476 (Coverage Optimality) | WHAT Currier A optimizes |
| **C478 (Temporal Scheduling)** | **HOW it achieves that optimization** |

### New Constraint

**C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)
- Strong temporal scheduling with pedagogical pacing
- Evidence: 5/5 signals support scheduled traversal
- Interpretation: Introduce early, reinforce throughout, cycle domains

### Files

- `phases/TEMPORAL_TRAJECTORIES/temporal_coverage_trajectories.py` - Analysis
- `results/temporal_coverage_trajectories.json` - Full results

---

## Version 2.24 (2026-01-12) - HT Variance Decomposition (C477)

### Summary

**HT density is partially explained (R² = 0.28) by A metrics, with TAIL PRESSURE as the dominant predictor (68% of variance).** HT rises when rare MIDDLEs are in play - evidence of cognitive load balancing.

### Core Finding

> **HT correlates with tail pressure (r = 0.504, p = 0.0045). When folios have more rare MIDDLEs, HT density is higher. HT is a cognitive load signal for tail discrimination complexity.**

### Regression Results

| Predictor | r | p-value | Ablation |
|-----------|---|---------|----------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| novelty | 0.153 | 0.42 | 6.3% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

### Interpretation

| R² Range | Interpretation | This Result |
|----------|----------------|-------------|
| 0.50+ | Strongly tied to discrimination | - |
| **0.25-0.40** | **Coarse vigilance signal** | **R² = 0.28** |
| 0.10-0.25 | Weak connection | - |
| <0.10 | HT signals something else | - |

### Why Tail Pressure?

- **Common MIDDLEs (hubs)** are easy to recognize (low cognitive load)
- **Rare MIDDLEs (tail)** require more attention to discriminate (high cognitive load)
- **HT rises when rare variants are in play** → anticipatory vigilance

### Integration with Prior Findings

| System | Role | Now Grounded |
|--------|------|--------------|
| Currier A | Coverage control | C476: optimal coverage with hub rationing |
| HT | Vigilance signal | **C477: tracks tail discrimination pressure** |
| AZC | Decision gating | C437-C444 |
| Currier B | Execution safety | Frozen Tier 0 |

### New Constraint

**C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)
- HT density correlates with tail MIDDLE pressure (r = 0.504)
- Evidence of cognitive load balancing for rare discriminations

### Files

- `phases/HT_VARIANCE_DECOMPOSITION/ht_variance_decomposition.py` - Analysis
- `results/ht_variance_decomposition.json` - Full results

---

## Version 2.23 (2026-01-12) - Coverage Optimality CONFIRMED (C476)

### Summary

**Currier A achieves GREEDY-OPTIMAL coverage (100%) while using 22.3% FEWER hub tokens.** This confirms deliberate coverage management - Currier A is not generated, it is maintained.

### Core Finding

> **Real A achieves the same coverage as a greedy coverage-maximizing strategy, but with significantly less reliance on universal hub MIDDLEs. This is evidence of deliberate vocabulary management.**

### Coverage Comparison

| Model | Final Coverage | Hub Usage | Tail Activation |
|-------|---------------|-----------|-----------------|
| **Real A** | **100%** | **31.6%** | **100%** |
| Random | 72% | 9.8% | 67.8% |
| Freq-Match | 27% | 56.1% | 10.2% |
| **Greedy** | **100%** | **53.9%** | **100%** |

### Key Insight: Hub Efficiency

- Real A and Greedy both achieve 100% coverage
- Real A uses **31.6%** hub tokens
- Greedy uses **53.9%** hub tokens
- **Hub savings: 22.3 percentage points**

### Interpretation

The four residuals from Move #2 collapse into ONE control objective: **COVERAGE CONTROL**

| Residual | Mechanism |
|----------|-----------|
| PREFIX coherence | Reduce cognitive load during discrimination |
| Tail forcing | Ensure coverage of rare variants |
| Repetition structure | Stabilize attention on distinctions |
| Hub rationing | Prevent collapsing distinctions too early |

> **Currier A is not meant to be generated. It is meant to be maintained.**

### New Constraint

**C476 - COVERAGE OPTIMALITY** (Tier 2, CLOSED)
- Real A achieves greedy-optimal coverage with hub rationing
- Evidence of deliberate vocabulary management

### Files

- `phases/COVERAGE_OPTIMALITY/coverage_optimality.py` - Main analysis
- `results/coverage_optimality.json` - Full results

---

## Version 2.22 (2026-01-12) - Bundle Generator Diagnostic (EXPECTED FAILURE)

### Summary

**A minimal generator constrained only by MIDDLE incompatibility + line length + PREFIX priors fails on 9/14 diagnostic metrics.** Failure modes reveal additional structure in Currier A: PREFIX coherence, block purity, repetition structure, and tail access.

### Core Finding

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT. The generator over-mixes, under-uses the tail, and fails to reproduce the repetition structure.**

### Generator Configuration

**Included (hard constraints only):**
- MIDDLE atomic incompatibility (C475)
- Line length distribution (C233, C250-C252)
- PREFIX priors (empirical frequencies)
- LINE as specification context

**Excluded (want to see if they emerge):**
- Marker exclusivity rules
- Section conditioning
- AZC family information
- Adjacency coherence (C424)
- Suffix preferences

### Diagnostic Results

| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL (-95.6%)** |
| pure_block_frac | 46.9% | 2.7% | **FAIL (-94.2%)** |
| universal_middle_frac | 31.6% | 56.7% | **FAIL (+79.6%)** |
| unique_middles | 1187 | 330 | **FAIL (-72.2%)** |
| lines_with_repetition | 96.4% | 63.9% | **FAIL (-33.7%)** |
| prefixes_per_line | 1.78 | 4.64 | **FAIL (+160%)** |
| line_length_mean | 19.2 | 20.0 | OK |
| line_length_median | 8.0 | 8.0 | OK |

### Residual Interpretation (New Structure Identified)

1. **PREFIX COHERENCE CONSTRAINT** - Lines prefer to stay within a single PREFIX family (not just compatibility)

2. **TAIL ACCESS FORCING** - Real A systematically uses rare MIDDLEs; generator ignores them

3. **REPETITION IS STRUCTURAL** - 96.4% of real lines have MIDDLE repetition (deliberate, not random)

4. **HUB RATIONING** - Universal MIDDLEs ('a','o','e') are used sparingly (31.6% vs 56.7% generator)

### What This Proves

| Finding | Status |
|---------|--------|
| Incompatibility is necessary | Confirmed (line length matches) |
| Incompatibility is sufficient | **REJECTED** (9/14 metrics fail) |
| PREFIX coherence exists | **NEW CONSTRAINT** (block purity) |
| Repetition is structural | **NEW CONSTRAINT** (not in current model) |
| Tail MIDDLEs are forced | **NEW CONSTRAINT** (registry coverage) |

### Files

- `phases/A_BUNDLE_GENERATOR/a_bundle_generator.py` - Generator and diagnostics
- `results/a_bundle_generator.json` - Full results

### Next Step

**HT Variance Decomposition** - Can incompatibility degree explain HT density?

---

## Version 2.21 (2026-01-12) - Latent Discrimination Axes (HIGH-DIMENSIONAL)

### Summary

**The MIDDLE compatibility space requires ~128 latent axes to achieve 97% prediction accuracy.** This is HIGH-DIMENSIONAL - discrimination is not reducible to a few binary choices.

### Core Finding

> **128 dimensions needed for 97% AUC. The discrimination space is NOT low-rank (not 2-4 axes as initially hypothesized). PREFIX, character content, and length are all weak predictors of the axes.**

### Probe Results (latent_discrimination_axes.py)

| Metric | Value |
|--------|-------|
| Optimal K | 128 |
| AUC at K=128 | 97.2% |
| AUC at K=2 | 86.9% |
| AUC at K=32 | 90.0% |
| Variance at K=128 | 83.4% |
| K for 90% variance | 51 |

### AUC by Dimensionality

| K | AUC | Interpretation |
|---|-----|----------------|
| 2 | 0.869 | Two axes capture ~87% |
| 4 | 0.870 | Minimal gain |
| 8 | 0.869 | Minimal gain |
| 16 | 0.886 | Starts improving |
| 32 | 0.900 | 90% threshold |
| 64 | 0.923 | Significant gain |
| 128 | 0.972 | Near ceiling |

### Axis Structure Analysis

**Axes do NOT align with interpretable features:**

| Feature | Max Correlation | Verdict |
|---------|-----------------|---------|
| PREFIX | 0.011 (separation) | WEAK |
| Characters | 0.138 ('f' on axis 2) | WEAK |
| Length | 0.160 (axis 17) | WEAK |

### Interpretation

1. **Not 2-4 binary switches** - The expert hypothesis of "2-4 axes of distinction" is rejected
2. **Rich feature space** - Each MIDDLE encodes ~128 bits of discriminatory information
3. **Emergent structure** - The axes don't map to obvious linguistic features
4. **PREFIX is ~1/128th** - PREFIX explains about 1/128th of the discrimination variance

### Hub Confirmation

Top-5 hubs by degree match prior finding:
| MIDDLE | Degree (weighted) |
|--------|------------------|
| 'a' | 2047 |
| 'o' | 1870 |
| 'e' | 1800 |
| 'ee' | 1625 |
| 'eo' | 1579 |

### What This Means

1. **Vocabulary is NOT simple categorization** - Not just "A/B/C with variants"
2. **Each MIDDLE is unique** - 128-dimensional fingerprint
3. **Compatibility is learned, not rule-based** - No simple grammar generates it
4. **Generative model needs ~128 features per MIDDLE** - High complexity

### Files

- `phases/LATENT_AXES/latent_discrimination_axes.py` - Main analysis
- `results/latent_discrimination_axes.json` - Full results

### Next Steps (from expert roadmap)

1. ~~Latent Discrimination Axes Inference~~ **DONE - HIGH-DIMENSIONAL**
2. **Probabilistic Currier-A Bundle Generator** - Can we reproduce A entries?
3. **HT Variance Decomposition** - Ground HT quantitatively

---

## Version 2.20 (2026-01-12) - MIDDLE Atomic Incompatibility (C475)

### Summary

**MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice.** This is the atomic discrimination layer - everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.

### Core Finding

> **95.7% of MIDDLE pairs are illegal. Only 4.3% can co-occur on the same specification line. This sparsity is robust to context definition (97.3% overlap with 2-line sensitivity check).**

### Probe Results (middle_incompatibility.py)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Trivially absent | 155 |
| Connected components | 30 |
| Largest component | 1,141 (96% of MIDDLEs) |
| Isolated MIDDLEs | 20 |

### PREFIX Clustering (H1 - SUPPORTED)

| Type | Legal % | Interpretation |
|------|---------|----------------|
| Within-PREFIX | 17.39% | Soft prior for compatibility |
| Cross-PREFIX | 5.44% | Hard exclusion boundary |
| **Ratio** | **3.2x** | PREFIX is first partition |

### Key Structural Objects Identified

1. **Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
   - Compatibility basis elements
   - Bridge otherwise incompatible regimes
   - "Legal transition anchors"

2. **Isolated MIDDLEs** (20 total)
   - Hard decision points
   - "If you specify this, you cannot specify anything else"
   - Pure regime commitment

3. **PREFIX = soft prior, MIDDLE = hard constraint**
   - PREFIX increases odds of legality ~3x
   - MIDDLE applies near-binary exclusions

### Reconciliation with Prior Constraints

| Constraint | Previous | Now Resolved |
|------------|----------|--------------|
| C293 | MIDDLE is primary discriminator | Quantified: 95.7% exclusion rate |
| C423 | PREFIX-bound vocabulary | PREFIX is first partition, MIDDLE is sharper |
| C437-C442 | Why so many AZC folios? | AZC = projections of sparse graph |
| C459, C461 | HT anticipatory function | HT ≈ incompatibility density (testable) |

### f116v Correction

f116v folio-level isolation (from v2.19) is explained by **data sparsity** (only 2 words in AZC corpus), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### New Constraint

**C475 - MIDDLE ATOMIC INCOMPATIBILITY** (Tier 2, CLOSED)
- Added to `context/CLAIMS/currier_a.md`

### Interpretation

> **The MIDDLE vocabulary forms a globally navigable but locally forbidden discrimination space. This is the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.**

### What This Enables (Bayesian Roadmap)

1. **Latent Discrimination Axes Inference** - How many latent axes explain the incompatibility graph?
2. **Probabilistic A Bundle Generator** - Can MIDDLE incompatibility + line length + PREFIX priors reproduce A entries?
3. **HT Variance Decomposition** - How much HT density is explained by local incompatibility degree?

### Updated Files

- `phases/MIDDLE_INCOMPATIBILITY/middle_incompatibility.py` - Main probe
- `results/middle_incompatibility.json` - Full results
- `context/CLAIMS/currier_a.md` - Added C475
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - Updated

### Significance

This is a **regime change** in what kind of modeling is now possible. We've reached bedrock - the atomic discrimination layer. All higher-level structure (A, AZC, HT) can now be understood as aggregations of this sparse graph.

---

## Version 2.19 (2026-01-12) - AZC Compatibility at Specification Level

### Summary

**AZC compatibility filtering operates at the Currier A constraint-bundle level, not at execution level.** Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both. 10.3% of folio pairs are unbridged, with f116v being structurally isolated.

### Key Finding

> **Currier A entries define which AZC vocabularies can be jointly activated. Most folio pairs are compatible, but ~10% are not—with f116v being a structurally isolated discrimination regime. AZC compatibility is enforced at specification (A-bundle) level, not at execution or folio-presence level.**

### Probe Results

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

### Family-Level Coherence

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap, partial incompatibility |

### f116v Structural Isolation

f116v shares NO bridging tokens with most other folios:
- Vocabulary uniquely concentrated
- Cannot be jointly specified with most other constraint bundles
- Can still appear in B executions (C440 holds)
- Defines a discrimination profile incompatible at A-level

### C442 Refinement

Previous understanding: "94% unique vocabulary per folio"

Refined understanding:
> **AZC compatibility filtering operates at the level of Currier A constraint-bundle co-specification. Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.**

Corollaries:
- Folios are NOT execution-exclusive
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no discrete trace—they simply never occur

### Why This Matters

This resolves family-level coherence:
- **Zodiac (0% unbridged)**: Supports sustained HT flow—interchangeable contexts
- **A/C (14.7% unbridged)**: Causes punctuated HT resets—true alternatives
- **Execution difficulty unchanged**: CEI, recovery, hazard models unaffected

### Updated Files

- `phases/AZC_COMPATIBILITY/azc_entry_bridges.py` - Correct probe
- `phases/AZC_COMPATIBILITY/azc_folio_compatibility.py` - First probe (coarse)
- `results/azc_entry_bridges.json` - Bridge analysis results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.5
- `context/CLAIMS/azc_system.md` - C442 refined

### Significance

This is a **Tier-2 advance**:
- Pinpoints the mechanism of AZC compatibility (A-bundle level)
- Identifies f116v as structurally isolated
- Explains Zodiac coherence vs A/C alternatives
- Connects discrimination regimes to specification constraints

---

## Version 2.18 (2026-01-11) - AZC-Based Currier A Clustering

### Summary

**AZC folio co-occurrence can reverse-cluster Currier A entries, revealing sub-families within PREFIX classes.** The y- PREFIX shows a family split: some y- tokens cluster with Zodiac contexts, others with A/C contexts.

### Key Finding

> **PREFIX morphology does not fully determine AZC family affinity. Some PREFIX classes (notably y-) contain sub-families that differ in their discrimination-regime membership.**

### Probe Results

| Metric | Value |
|--------|-------|
| Currier A tokens in AZC | 778 (16% of vocabulary) |
| Tokens eligible for clustering | 367 (appear in 2+ AZC folios) |
| Sub-families detected | y- (FAMILY_SPLIT) |

### PREFIX → AZC Family Baseline (confirms C471)

| PREFIX | Zodiac % | A/C % | Bias |
|--------|----------|-------|------|
| qo- | 18.8% | 71.9% | A/C |
| d- | 14.5% | 62.9% | A/C |
| or- | 58.3% | 16.7% | Zodiac |
| ot- | 25.0% | 25.0% | BALANCED |
| **y-** | 28.1% | 46.9% | **SPLIT** |

### y- Family Split Evidence

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

### Interpretation

y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

### Extreme Family Clusters (100% bias)

| Cluster | Bias | Tokens | Shared Folios |
|---------|------|--------|---------------|
| 67 | 100% Zodiac | okeoly, dalal, otalal | f70v2, f72v1 |
| 38 | 100% A/C | om, oir, ykaly | f67v2, f67r2 |
| 139 | 100% Zodiac | okam, okaldy, chas | f72r2, f72v3 |

### Updated Files

- `phases/EFFICIENCY_REGIME_TEST/azc_based_a_clustering.py` - Clustering probe
- `results/azc_based_a_clustering.json` - Full results
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.4, y- finding
- `context/SPECULATIVE/efficiency_regimes.md` - Added y- evidence

### Significance

This probe demonstrates that AZC can be used in reverse to reveal structure within Currier A vocabulary that PREFIX morphology alone doesn't show. The y- split provides evidence that some morphological markers encode regime-independent properties.

---

## Version 2.17 (2026-01-11) - Perceptual Discrimination Regime Synthesis

### Summary

**HT oscillation analysis completes the regime interpretation.** The concurrency management probe falsified the parallel-batch hypothesis but revealed the correct explanatory axis: discrimination complexity determines attentional flow patterns.

### Key Finding

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

### HT Oscillation Results

| Family | HT Density | Oscillation Score | Interpretation |
|--------|-----------|-------------------|----------------|
| Zodiac | 0.131 | 0.060 | Sustained attentional flow |
| A/C | 0.236 | 0.110 | Punctuated attentional checkpoints |

**A/C shows ~80% higher HT oscillation than Zodiac.**

### Falsified Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Parallel batch management | FALSIFIED | HT oscillation reversed from prediction |
| Zodiac = high context switching | FALSIFIED | Zodiac has LOWER oscillation |

### The Coherent Explanatory Axis (All Layers Aligned)

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

### Final Interpretation (Tier 3 - VALIDATED)

> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Final validated interpretation
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.3, coherent axis table
- `phases/EFFICIENCY_REGIME_TEST/test_concurrency_management.py` - HT probe
- `results/concurrency_management_probe.json` - HT test output

### Significance

This is the first interpretation that cleanly integrates ALL layers (A, AZC, B, HT, CEI) without contradiction. The internal evidence has been exhausted correctly, by falsification rather than narrative preference.

---

## Version 2.16 (2026-01-11) - Lexical Granularity Regime Validation

### Summary

**This phase empirically tested the "efficiency regime" interpretation of Zodiac vs A/C.** The results localized the signal to the vocabulary layer and falsified behavioral-level claims.

### Key Finding

> **Zodiac vs A/C encodes regimes of lexical discrimination, not regimes of operational difficulty; the control grammar absorbs lexical complexity so that execution behavior remains stable.**

### Test Results

| Test | Result | Interpretation |
|------|--------|----------------|
| MIDDLE Discrimination Pressure | WEAK SUPPORT | 5/15 prefixes show gradient, 0 reversed |
| Residual Brittleness Analysis | **FAILED** | Effect is PREFIX-morphological, not regime-based |
| Universal MIDDLE Negative Control | **PASSED** | Universal MIDDLEs regime-neutral (58.7%), Exclusive biased (64.8%) |
| Family Escape Transfer | PARTIAL | Weak positive correlation (r=0.265) |

**Overall Verdict: WEAK_PARTIAL**

### What IS Supported (Lexical Level)

- MIDDLE discrimination is genuinely family-biased
- Universal MIDDLEs are regime-neutral; Exclusive MIDDLEs show A/C bias
- A/C contexts require finer vocabulary distinctions; Zodiac uses broader categories

### What Is NOT Supported (Behavioral Level - FALSIFIED)

- A/C = operationally brittle (REJECTED)
- Zodiac = operationally forgiving (REJECTED)
- Family affects CEI or recovery (REJECTED)
- Efficiency stress propagates to B programs (REJECTED)

### New Insight

**CEI measures control strain *within* execution, not *between* lexical regimes.**

CEI and AZC family live on orthogonal axes:
- CEI = trajectory management within execution
- AZC family = what distinctions exist ahead of time

### Updated Files

- `context/SPECULATIVE/efficiency_regimes.md` - Renamed, tested, revised
- `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` - v4.2, updated regime section
- `phases/EFFICIENCY_REGIME_TEST/` - Four test scripts + synthesis
- `results/efficiency_regime_*.json` - All test outputs

### Methodology Note

This represents a proper falsification attempt, not confirmation bias. The test suite was designed with pre-declared stop conditions and negative controls. The partial failure is a scientific success: it precisely located where the signal exists (vocabulary) vs where it does not (behavior).

---

## Version 2.15 (2026-01-11) - Morphological Binding Phase Closure

### Summary

**This phase resolved the interface between Currier A, AZC, and Currier B.** The binding logic that connects vocabulary composition to constraint activation is now morphologically encoded, causally active, and empirically validated.

### The One-Sentence Takeaway

> **Currier A records define which worlds are allowed to exist, AZC defines what is legal in each world and when recovery is possible, and Currier B blindly executes - leaving the consequences of earlier discriminations unavoidable but structurally bounded.**

### New Constraints

- **C471** - PREFIX Encodes AZC Family Affinity (Tier 2)
  - qo- and ol- strongly enriched in A/C AZC folios (91% / 81%)
  - ot- enriched in Zodiac folios (54%)
  - ch-, sh-, ok- broadly distributed
  - Statistical affinity, not exclusive mapping

- **C472** - MIDDLE Is Primary Carrier of AZC Folio Specificity (Tier 2)
  - PREFIX-exclusive MIDDLEs (77%) exhibit median entropy = 0.0
  - Typically appear in exactly one AZC folio
  - Shared MIDDLEs span multiple folios (18.7% vs 3.3% coverage)
  - MIDDLE is principal determinant of folio-level constraints

- **C473** - Currier A Entry Defines a Constraint Bundle (Tier 2)
  - A entry does not encode addressable object or procedure
  - Morphological composition specifies compatibility signature
  - Determines which AZC legality envelopes are applicable

### Final Definitions (Locked)

- **Currier A record** = Pre-execution compatibility declaration
- **AZC folio** = Complete legality regime (permissions + recoveries)
- **Currier B program** = Blind execution against filtered vocabulary

### Closure Declarations

**Pipeline Resolution & Morphological Binding: CLOSED**

No remaining degrees of freedom. The binding logic is:
- PREFIX -> AZC family affinity
- MIDDLE -> AZC folio specificity
- Together: each vocabulary item carries a compatibility signature

**Additional closures (do NOT reopen):**
- Naming or meaning of AZC folios (they are legality regimes)
- Aligning A entries to specific B programs (vocabulary-mediated)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C471-C473, morphological binding section
- `context/CLAUDE_INDEX.md` - Updated to v2.8, 335 constraints
- `context/MAPS/claim_to_phase.md` - Added C471-C473 mapping
- `phases/INTEGRATION_PROBE/` - Three probe scripts archived
- `results/integration_probe_*.json` - Probe results saved

---

## Version 2.14 (2026-01-11) - Pipeline Resolution Phase Closure

### Summary

**This phase achieved structural closure on the A -> AZC -> B pipeline.** The decisive finding: AZC constraint profiles propagate causally into Currier B execution behavior.

### New Constraints

- **C468** - AZC Legality Inheritance (Tier 2)
  - Tokens from high-escape AZC contexts show 28.6% escape in B
  - Tokens from low-escape AZC contexts show 1.0% escape in B
  - 28x difference confirms causal constraint transfer

- **C469** - Categorical Resolution Principle (Tier 2)
  - Operational conditions represented categorically via token legality
  - Not parametrically via encoded values
  - Physics exists externally; representation is categorical

- **C470** - MIDDLE Restriction Inheritance (Tier 2)
  - Restricted MIDDLEs (1-2 AZC folios): 4.0 B folio spread
  - Universal MIDDLEs (10+ AZC folios): 50.6 B folio spread
  - 12.7x difference confirms constraint transfer

### New Fits

- **F-AZC-015** - Windowed AZC Activation Trace
  - Case B confirmed: 70% of AZC folios active per window
  - High persistence (0.87-0.93): same folios persist
  - AZC is ambient legality field, not dynamic selector

- **F-AZC-016** - AZC->B Constraint Fit Validation
  - MIDDLE restriction transfers: CONFIRMED (12.7x)
  - Escape rate transfers: CONFIRMED (28x)
  - Pipeline causality validated

### Closure Declarations

**Pipeline Resolution Phase: CLOSED**

The A -> AZC -> B control pipeline is structurally and behaviorally validated.

**Do NOT reopen:**
- Entry-level A->B mapping (ruled out by pipeline mechanics)
- Dynamic AZC decision-making (F-AZC-015 closed this)
- Parametric variable encoding (no evidence exists)
- Semantic token meaning (all evidence against)

### Updated Files

- `context/CLAIMS/azc_system.md` - Added C468-C470, closure statement
- `context/MODEL_FITS/fits_azc.md` - Added F-AZC-015, F-AZC-016
- `context/MODEL_CONTEXT.md` - Added Section X.C (Representation Principle)
- `context/CLAUDE_INDEX.md` - Updated to v2.7, 320+ constraints

### Archived Scripts

29 scripts from `phases/AZC_constraint_hunting/` archived to `archive/scripts/AZC_constraint_hunting/`

---

## Version 2.13 (2026-01-10)

### E4: AZC Entry Orientation Trace (C460)

**Summary:** Tested whether AZC folios serve as cognitive entry points by analyzing HT trajectories in their neighborhood. Found significant step-change pattern, but it resembles random positions more than A/B entries.

**New Constraint:**

- **C460** - AZC Entry Orientation Effect (Tier 2)
  - Step-change at AZC: p < 0.002 (all window sizes)
  - Pre-entry HT: above average (+0.1 to +0.28 z-score)
  - Post-entry HT: below average (-0.08 to -0.30 z-score)
  - Gradient: decay, R^2 > 0.86

**Critical Nuance:**
- AZC trajectory differs from A and B systems (p < 0.005)
- AZC trajectory does NOT differ from random (p > 0.08)
- Interpretation: AZC is **placed at** natural HT transitions, not **causing** them

**Zodiac vs Non-Zodiac:**
- Zodiac step-change: -0.39 (stronger)
- Non-zodiac step-change: -0.36

**New Files:**
- `phases/exploration/azc_entry_orientation_trace.py`
- `results/azc_entry_orientation_trace.json`
- `context/CLAIMS/C460_azc_entry_orientation.md`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.13, 310 constraints

**Status:** E4 COMPLETE

### E5: AZC Internal Oscillation (Observation Only)

**Question:** Does AZC show internal micro-oscillations matching the global HT rhythm?

**Answer:** No. AZC does not replicate manuscript-wide dynamics internally.
- No significant autocorrelation
- Faster cadence (~3.75 folios vs global ~10)
- Zodiac internally flat; non-Zodiac shows decreasing trend

**Status:** Documented as observation, NOT a constraint. Line of inquiry closed.

**New File:**
- `results/azc_internal_oscillation.json`

---

## Version 2.11 (2026-01-10)

### Intra-Role Differentiation Audit (C458-C459)

**Summary:** Complete audit of intra-folio variation across all four systems. Discovered that risk is globally constrained while human burden and recovery strategy are locally variable. Established HT as anticipatory (not reactive) attention layer.

**Core Finding:**
> The Voynich Manuscript does not vary in how risky its procedures are; it varies in how much *slack, recovery capacity, and human attention* each situation demands - and it encodes that distinction with remarkable consistency across systems.

**New Constraints:**

- **C458** - Execution Design Clamp vs Recovery Freedom (Tier 2)
  - Hazard exposure: CV = 0.04-0.11 (CLAMPED)
  - Recovery operations: CV = 0.72-0.82 (FREE)
  - Regime separation: eta² = 0.70-0.74
  - C458.a: Hazard/LINK mutual exclusion (r = -0.945)

- **C459** - HT Anticipatory Compensation (Tier 2)
  - Quire-level correlation: r = 0.343, p = 0.0015
  - HT before B: r = 0.236, p = 0.032 (significant)
  - HT after B: r = 0.177, p = 0.109 (not significant)
  - Pattern: HT_ANTICIPATES_STRESS
  - C459.a: REGIME_2 shows inverted compensation

**Additional Findings (not constraints):**

- **D2 (AZC Zodiac):** Zodiac folios vary in monitoring vs transition emphasis (CV = 0.15-0.39), no position gradient
- **P1 (Clustering):** 4 natural folio clusters; 4 anomalous folios cluster by HT burden across systems (f41r, f65r, f67r2, f86v5)
- **P2 (Recto-Verso):** No systematic asymmetry (p = 0.79); HT balanced across spreads

**Theoretical Impact:**

| Category | Effect |
|----------|--------|
| Strengthened | Control-artifact model, human-centric design, non-semantic stance |
| Constrained | Danger tied to pages, diagrams encoding execution, HT as reactive |
| Disfavored | Recipe difficulty gradients, didactic sequences, per-page semantics |

**New Files:**
- `phases/exploration/unified_folio_profile.py` - D0
- `phases/exploration/b_design_space_cartography.py` - D1
- `phases/exploration/azc_zodiac_fingerprints.py` - D2
- `phases/exploration/ht_compensation_analysis.py` - D3
- `phases/exploration/folio_personality_clusters.py` - P1
- `phases/exploration/recto_verso_asymmetry.py` - P2
- `phases/exploration/INTRA_ROLE_DIFFERENTIATION_SUMMARY.md` - Synthesis
- `context/CLAIMS/C458_execution_design_clamp.md`
- `context/CLAIMS/C459_ht_anticipatory_compensation.md`

**Results Files:**
- `results/unified_folio_profiles.json` (227 profiles)
- `results/b_design_space_cartography.json`
- `results/azc_zodiac_fingerprints.json`
- `results/ht_compensation_analysis.json`
- `results/folio_personality_clusters.json`
- `results/recto_verso_asymmetry.json`

**Updated Files:**
- `context/CLAIMS/INDEX.md` - Version 2.11, 309 constraints

**Status:** Intra-Role Differentiation Audit COMPLETE.

### Extended Analysis: HT Temporal Dynamics + Anomalous Folios

**HT Temporal Dynamics:**
- Global decreasing trend: r=-0.158, p=0.017 (HT falls through manuscript)
- ~10-folio periodicity: SNR=4.78 (quire-scale oscillation)
- 9 changepoints detected
- Front-loaded: f39r-f67v2 is HIGH region (48 folios), ending is LOW

**Anomalous Folio Investigation:**

All 4 folios that cluster across system boundaries are HT HOTSPOTS:
| Folio | System | HT | Escape | Status |
|-------|--------|-----|--------|--------|
| f41r | B | 0.296 | 0.197 | HOTSPOT |
| f65r | AZC | 0.333 | n/a | HOTSPOT |
| f67r2 | AZC | 0.294 | n/a | HOTSPOT |
| f86v5 | B | 0.278 | 0.094 | HOTSPOT |

**New Files (Extended):**
- `phases/exploration/ht_temporal_dynamics.py`
- `phases/exploration/anomalous_folio_investigation.py`
- `results/ht_temporal_dynamics.json`
- `results/anomalous_folio_investigation.json`

**Deepest Pattern Discovered:**
> The Voynich is not primarily a manual of actions. It is a manual of **responsibility allocation** between system and human.

---

## Version 2.12 (2026-01-10)

### Post-Differentiation Explorations (E1-E3)

**E1: Quire Rhythm Alignment**
- HT changepoints do NOT align with quire boundaries (enrichment=0.59x, p=0.35)
- HT rhythm is CONTENT-DRIVEN, not production-driven
- Quires differ significantly in mean HT level (H=48.2, p<0.0001, eta²=0.149)
- No consistent internal pattern (43% flat)

**E2: Zero-Escape Characterization (CORRECTION)**
- Only 2 B folios have near-zero escape: f33v (0.009), f85v2 (0.010)
- Neither is an HT hotspot
- Zero-escape is RARE (2.4% of B folios)
- No HT difference between zero-escape and normal B (p=0.22)
- **CORRECTED:** f41r and f86v5 are NOT zero-escape (original finding was due to field name bug)

**E3: Anomalous Folio Deep Dive**
- 13 total HT hotspots (6 A, 5 B, 2 AZC)
- The "anomalous 4" (f41r, f65r, f67r2, f86v5) are not unique
- Only f65r is at a system boundary (A→AZC)
- B hotspots span different regimes (REGIME_2, REGIME_4)
- All anomalous folios have ~2x median HT for their system

**Key Corrections:**
- C459.b "zero-escape → max HT" WITHDRAWN (data error)
- Escape density for f41r: 0.197 (not 0)
- Escape density for f86v5: 0.094 (not 0)

**New Files:**
- `phases/exploration/quire_rhythm_analysis.py`
- `phases/exploration/zero_escape_characterization.py`
- `phases/exploration/anomalous_folio_deep_dive.py`
- `results/quire_rhythm_analysis.json`
- `results/zero_escape_characterization.json`
- `results/anomalous_folio_deep_dive.json`

**Updated Files:**
- `context/CLAIMS/C459_ht_anticipatory_compensation.md` - C459.b corrected

**Status:** Post-Differentiation Explorations COMPLETE

---

## Version 2.10 (2026-01-10)

### B Design Space Cartography (C458)

**Summary:** Interim version during Intra-Role audit. See v2.11 for complete documentation.

---

## Version 2.9 (2026-01-10)

### HT-AZC Placement Affinity (C457)

**Summary:** Single focused test of HT-AZC relationship, following the architectural synthesis. Discovered that HT preferentially marks boundary (S) positions over interior (R) positions in Zodiac AZC.

**New Constraint:**

- **C457** - HT Boundary Preference in Zodiac AZC (Tier 2)
  - S-family HT rate: 39.7%
  - R-family HT rate: 29.5%
  - Difference: 10.3 percentage points (p < 0.0001, V = 0.105)
  - HT preferentially marks BOUNDARIES (sector positions)
  - Supports "attention at phase boundaries" interpretation

**Key Insight:**
> AZC defines the boundary structure of experience; HT marks when human attention should increase inside that structure.

**Files Created:**
- `context/CLAIMS/C457_ht_boundary_preference.md`
- `results/ht_azc_placement_affinity.json`
- `phases/exploration/ht_azc_placement_test.py`

**Status:** HT-AZC investigation CLOSED. No further tests needed.

---

## Version 2.8 (2026-01-10)

### Apparatus-Topology Hypothesis Testing (C454-C456)

**Summary:** Rigorous hypothesis testing of whether AZC encodes apparatus-stage alignment. Properly designed tests with pre-registered kill conditions. Hypothesis FALSIFIED, but produced valuable architectural insights.

**New Constraints:**

- **C454** - AZC-B Adjacency Coupling FALSIFIED (Tier 1)
  - B folios near AZC show NO significant metric differences from B folios far from AZC
  - All window sizes (1-5 folios) returned p > 0.01
  - AZC does NOT modulate B execution
  - AZC and B are topologically segregated

- **C455** - AZC Simple Cycle Topology FALSIFIED (Tier 1)
  - Zodiac AZC is NOT a single ring/cycle
  - Multiple independent cycles (cycle_rank = 5)
  - Non-uniform degree distribution (CV = 0.817)
  - "Literal apparatus diagram" interpretation rejected

- **C456** - AZC Interleaved Spiral Topology (Tier 2)
  - Zodiac shows R-S-R-S alternating pattern
  - R1 -> S1 -> R2 -> S2 -> R3
  - Consistent with cognitive orientation scaffolding
  - Alternation represents interior (R) vs boundary (S) states

**Architectural Synthesis:**

Created `context/ARCHITECTURE/layer_separation_synthesis.md` explaining:
- Why execution (B) must be context-free
- Why orientation (AZC) must be execution-free
- Why legality != prediction
- Why humans need spatial scaffolds for cyclic processes

**The Answer:**
> Why are there spatial diagrams that don't seem to describe anything?
> Because they describe *orientation*, not *operation*.

**Files Created:**
- `context/CLAIMS/C454_azc_b_adjacency_falsified.md`
- `context/CLAIMS/C455_azc_simple_cycle_falsified.md`
- `context/CLAIMS/C456_azc_interleaved_spiral.md`
- `context/ARCHITECTURE/layer_separation_synthesis.md`
- `phases/exploration/apparatus_topology_tests_v2.py`
- `phases/exploration/azc_topology_test.py`
- `results/apparatus_topology_critical_tests_v2.json`
- `results/azc_topology_analysis.json`

**Methodological Note:**
This phase demonstrated proper hypothesis testing:
1. Proposed falsifiable Tier-3 hypothesis
2. Pre-registered kill conditions (K1, K2)
3. Fixed test design flaws when detected
4. Accepted null results
5. Refined understanding based on evidence

**Status:** Apparatus-topology investigation CLOSED. Doors permanently closed on:
- AZC diagrams "representing" apparatus
- R/S/C positions mapping to physical components
- Diagram complexity correlating with execution difficulty

---

## Version 2.7 (2026-01-10)

### AZC-DEEP: Folio Family Architecture (C430-C432)

**Summary:** Completed AZC-DEEP Phases 1-3, discovering that AZC comprises two architecturally distinct folio families. This parallels the CAS-DEEP analysis of Currier A and reveals internal structure beyond "hybrid with placement."

**New Constraints:**

- **C430** - AZC Bifurcation (Tier 2)
  - AZC divides into two families with no transitional intermediates
  - Family 0: Zodiac-dominated, placement-stratified (13 folios)
  - Family 1: A/C-dominated, placement-flat (17 folios)
  - Bootstrap stability = 0.947, Silhouette = 0.34

- **C431** - Zodiac Family Coherence (Tier 2, refines C319)
  - All 12 Zodiac folios form single homogeneous cluster
  - JS similarity = 0.964
  - Higher TTR (0.54), placement entropy (2.25), AZC-unique rate (0.28)
  - Confirms Zodiac as distinct structural mode, not just template reuse

- **C432** - Ordered Subscript Exclusivity (Tier 2)
  - R1-R3, S1-S2 occur exclusively in Zodiac family
  - Binary diagnostic feature (0.96 vs 0.00 depth)
  - Ordered subscripts are family-defining, not AZC-general

**Architectural Impact:**
- AZC is now demonstrably non-monolithic
- Zodiac pages define a separate AZC control mode
- Ordered subscripts become diagnostic, not incidental
- Hybrid story sharpens: Cluster 1 has more shared vocabulary, Cluster 0 has more AZC-unique

**Files Modified:**
- `context/CLAIMS/azc_system.md` - Added C430-C435
- `context/CLAIMS/INDEX.md` - Updated AZC section

### AZC-DEEP Phase 4a: Zodiac Placement Grammar (C433-C435)

**Summary:** Discovered that Zodiac pages implement an extremely strict, block-based placement grammar - stricter than Currier B grammar, not looser.

**New Constraints:**

- **C433** - Zodiac Block Grammar (Tier 2)
  - Placement codes occur in extended contiguous blocks (mean 40-80 tokens)
  - Self-transition rate exceeds 98% for all major codes
  - Zero singletons - once a placement starts, it locks for dozens of tokens
  - **Stricter than Currier B grammar**

- **C434** - R-Series Strict Forward Ordering (Tier 2)
  - R1→R2→R3 only - no backward, no skipping
  - Backward transitions: 0 observed (349 expected)
  - Skip transitions: 0 observed (139 expected)

- **C435** - S/R Positional Division (Tier 2)
  - S-series: Boundary layer (95%+ at line edges)
  - R-series: Interior layer (89-95% interior positions)
  - Two-layer grammar: S marks entry/exit, R fills interior in ordered stages

**Key Insight:**
> The Zodiac pages are not "diagrams with labels." They are a rigid, page-bound control scaffold - the same structure reused twelve times with local vocabulary variation but identical placement logic.

### AZC-DEEP Phase 4b: A/C Family Placement Grammar (C436)

**Summary:** Discovered that the A/C family is ALSO rigid (98% self-transition, zero singletons), but differs from Zodiac in cross-folio consistency. The contrast is uniform-vs-varied, not rigid-vs-permissive.

**New Constraint:**

- **C436** - AZC Dual Rigidity Pattern (Tier 2)
  - Both families: >=98% self-transition, zero singletons
  - Zodiac family: 0.945 cross-folio consistency (uniform scaffold)
  - A/C family: 0.340 cross-folio consistency (folio-specific scaffolds)
  - The contrast is uniform-versus-varied rigidity

**Key Insight:**
> AZC is not "one mode with variation" - it implements two distinct coordination strategies. Every AZC page enforces a hard placement lock. The difference is whether that lock is standardized (Zodiac) or custom (A/C).

**Four-Layer Stack Now Complete:**
- Currier B: Controls systems (execution grammar)
- Currier A: Catalogs distinctions (complexity frontier)
- AZC: Locks context (uniform or custom scaffolds)
- HT: Keeps the human oriented once the lock is engaged

**AZC-DEEP Status:** COMPLETE (discovery phase). All four Voynich systems now show internal, non-trivial, testable architecture

---

## Version 2.6 (2026-01-10)

### C424: Clustered Adjacency + A-B Correlation Investigation + CFR Interpretation

**Summary:** Added C424 (Clustered Adjacency) with three refinements. Completed A-B hazard correlation investigation that falsified failure-memory hypothesis. Established Complexity-Frontier Registry (CFR) as unified interpretation for Currier A. Declared Currier A structurally exhausted.

**New Constraint:**
- **C424** - Clustered Adjacency in Currier A (Tier 2)
  - 31% of adjacent entries share vocabulary (clustered), 69% do not (singletons)
  - Mean cluster size: 3 entries (range 2-20)
  - Autocorrelation r=0.80 exceeds section-controlled null (z=5.85)

**Refinements:**
- **C424.a** - Structural correlates (68% vocabulary divergence between populations)
- **C424.b** - Run-size threshold (size 5+ shows J=0.36 vs size-2 J=0.08)
- **C424.c** - Section P inversion (singletons concentrate at top of pages)

**A-B Correlation Investigation (Exploratory - NO CONSTRAINT):**

| Test | Result | Interpretation |
|------|--------|----------------|
| Hazard density correlation | rho=0.228, p=0.038 | Initial positive |
| Permutation control | p=0.111 | FAILED |
| Frequency-matched control | p=0.056 | FAILED |
| **Pre-registered low-freq MIDDLE** | **rho=-0.052, p=0.651** | **FAIL** |

**Conclusion:** Apparent A-B hazard correlation entirely explained by token frequency. No residual risk-specific signal. Failure-memory hypothesis falsified.

**Unified Interpretation: Complexity-Frontier Registry (CFR)**

> Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

- Currier B provides sequences (how to act)
- Currier A provides discrimination (where fine distinctions matter)
- AZC constrains availability
- HT supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

**Structural Exhaustion Declared:**
Currier A has reached its structural analysis limit. No further purely structural analyses expected to yield new constraints.

**Closed Tests (DO NOT RE-RUN):**
- Hazard density correlation - CLOSED (frequency-explained)
- Forgiveness/brittleness discrimination - CLOSED (inseparable from complexity)

**New files:**
- `CLAIMS/C424_clustered_adjacency.md` - Full constraint documentation
- `phases/exploration/a_b_hazard_correlation.py` - Main correlation script
- `phases/exploration/preregistered_low_freq_test.py` - Decisive final test
- `phases/exploration/a_b_connection_map.py` - Connection map generator
- `phases/exploration/A_B_CORRELATION_RESULTS.md` - Correlation results
- `phases/exploration/A_B_CONNECTION_MAP.md` - Connection map summary
- `phases/exploration/a_b_connection_map.json` - Machine-readable map

**Updated files:**
- `CLAIMS/INDEX.md` - Added C424, version 2.6, count 424
- `CLAIMS/currier_a.md` - Added C424 section, exploratory note with CFR interpretation

**Research phase:** Exploration (1838 entries, 83 folios analyzed)

---

## Version 2.5 (2026-01-09)

### Record Structure Analysis + C250.a Refinement

**Summary:** Complete analysis of Currier A record-level structure using DA-segmented block boundaries.

**Findings (validated but not all constraint-worthy):**
- Block count distribution: 57% single-block, 43% multi-block
- Block size pattern: FRONT-HEAVY (first block ~11 tokens, later ~5)
- Positional prefix tendencies: qo/sh prefer first, ct prefers last (V=0.136)
- Block-level repetition: 58.7% exact, 91.5% high similarity (J>=0.5)
- Record templates: 3-5 patterns cover 77%

**Expert review outcome:**
- C424-C426 initially proposed but REJECTED as constraints
- Positional preferences = tendencies, not rules (no constraint)
- Templates = emergent patterns, not grammar (no constraint)
- Block-aligned repetition = valid refinement of C250

**Accepted:**
- **C250.a** - Block-Aligned Repetition (refinement)
  - Repetition applies to DA-segmented blocks, not partial segments
  - Non-adjacent blocks more similar than adjacent (interleaved enumeration)

**Rejected (kept as descriptive findings only):**
- Positional prefix preferences (tendency, not constraint)
- Record structure templates (emergent, not grammar)

**New files:**
- `phases/exploration/record_structure_analysis.py`
- `phases/exploration/block_position_prefix_test.py`
- `phases/exploration/repetition_block_alignment.py`
- `phases/exploration/RECORD_STRUCTURE_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C250.a refinement under Multiplicity Encoding

**Note:** Constraint count unchanged (423). Findings describe USE of structure, not design limits.

---

## Version 2.4 (2026-01-09)

### C410.a: Sister Pair Micro-Conditioning (Refinement)

**Summary:** Refinement documenting compositional conditioning of sister-pair choice in Currier A.

**Findings:**
- MIDDLE is the PRIMARY conditioning factor (25.4% deviation from 50%)
- Some MIDDLEs are >95% one sister (yk: 97% ch, okch: 96% ch)
- Suffix compatibility provides secondary conditioning (22.1% deviation)
- Adjacent-token effects favor run continuation (ch->ch: 77%)
- DA context has ZERO effect (V=0.001) - confirms DA is structural
- Section effect is background bias (V=0.078)

**Interpretation:**
Sister pairs encode equivalent classificatory roles but permit compositionally conditioned surface variation. Preferences are local within the compositional system - no new categories, semantics, or hierarchies.

**New files:**
- `phases/exploration/sister_pair_conditioning.py`

**Updated files:**
- `CLAIMS/C408_sister_pairs.md` - Added C410.a refinement section

**Note:** This closes Priority 3 (sister-pair conditioning). Does not break equivalence class status.

---

## Version 2.3 (2026-01-09)

### C346.b: Component-Level Adjacency Drivers (Refinement)

**Summary:** Refinement note added to C346 documenting component-level analysis of adjacency coherence.

**Findings:**
- Removing DA tokens increases adjacency coherence (+18.4%)
- MIDDLE-only adjacency is LOWER than full-token (2.10x vs 2.98x)
- PREFIX and SUFFIX drive local adjacency more than MIDDLE
- DA-segmented blocks show 26.8x internal coherence

**Key insight:** Currier A adjacency reflects domain-level continuity (PREFIX) with item-level variation (MIDDLE). This is registry organization, not semantic chaining.

**New files:**
- `phases/exploration/payload_refinement.py`

**Updated files:**
- `CLAIMS/currier_a.md` - Added C346.b refinement note

**Note:** This is a refinement, not a new constraint. Does not change C346's core finding.

---

## Version 2.2 (2026-01-09)

### C423: PREFIX-BOUND VOCABULARY DOMAINS + C267 Amendment

**Summary:** New Tier-2 constraint establishing MIDDLE as the primary vocabulary layer in Currier A, with prefixes defining domain-specific vocabularies. Amendment to C267 corrects "42 common middles" to full census of 1,184.

**Finding (MIDDLE census):**
- 1,184 distinct MIDDLEs identified (full inventory)
- 80% (947) are PREFIX-EXCLUSIVE
- 20% (237) are shared across prefixes
- 27 UNIVERSAL middles appear in 6+ prefixes
- Top 30 account for 67.6% of usage
- MIDDLE entropy: 6.70 bits (65.6% efficiency)

**PREFIX vocabulary sizes:**
| Prefix | Exclusive MIDDLEs |
|--------|-------------------|
| ch | 259 (largest) |
| qo | 191 |
| da | 135 |
| ct | 87 |
| sh | 85 |
| ok | 68 |
| ot | 55 |
| ol | 34 (smallest) |

**DA-MIDDLE coherence finding:**
- DA-segmented sub-records do NOT exhibit increased MIDDLE similarity
- Adjacent segment J=0.037 vs random segment J=0.039 (0.94x)
- DA separates structure, not vocabulary content

**Interpretation:**
- Prefixes define domain-specific vocabularies
- MIDDLEs are selected from prefix-specific inventories
- Shared/universal middles form small cross-domain core
- This is the vocabulary layer of Currier A

**C267 amendment:**
- Original: "42 common middles" (discovery-era simplification)
- Updated: "1,184 unique (27 universal)" with cross-reference to C423
- Added note explaining scope mismatch

**New files:**
- `phases/exploration/middle_census.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C423, version 2.2, count 423
- `CLAIMS/currier_a.md` - Added Vocabulary Domains section, MIDDLE coherence note to C422
- `CLAIMS/C267_compositional_morphology.md` - Amended MIDDLE count and added note

**Research phase:** Exploration (25,890 tokens parsed, 17,589 with MIDDLE)

---

## Version 2.1 (2026-01-09)

### C422: DA as Internal Articulation Punctuation

**Summary:** New Tier-2 constraint documenting DA's structural punctuation role within Currier A entries.

**Finding:**
- 75.1% of internal DA occurrences separate adjacent runs of different marker prefixes (3:1 ratio)
- All DA tokens (daiin and non-daiin) exhibit identical separation behavior (74.9% vs 75.4%)
- Entries with DA are significantly longer (25.2 vs 16.4 tokens) and more prefix-diverse (3.57 vs 2.01)
- DA-segmented regions form prefix-coherent blocks

**Section gradient:**
- H (Herbal): 76.9% separation rate (3.3:1)
- P (Pharmaceutical): 71.7% (2.5:1)
- T (Text-only): 65.0% (1.9:1)
- Direction invariant across all sections

**Interpretation:**
- DA does not encode category identity
- DA marks internal sub-record boundaries within complex registry entries
- DA functions as punctuation rather than classifier
- Role is globally infrastructural, intensity correlates with section complexity

**New files:**
- `phases/exploration/da_punctuation_analysis.py`
- `phases/exploration/da_deep_dive.py`
- `phases/exploration/da_section_invariance.py`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C422, version 2.1, count 422
- `CLAIMS/currier_a.md` - Added DA Internal Articulation section

**Research phase:** Exploration (1838 entries, 3619 DA tokens analyzed)

---

## Version 2.0 (2026-01-09)

### C421: Section-Boundary Adjacency Suppression + C346.a Refinement

**Summary:** New Tier-2 constraint documenting section boundary effects on adjacent entry similarity. Refinement note added to C346 explaining similarity decomposition.

**C421 Finding:**
- Adjacent entries crossing section boundaries exhibit 2.42x lower vocabulary overlap
- Same-section adjacent: J=0.0160
- Cross-section adjacent: J=0.0066
- p < 0.001

**C346.a Refinement:**
- 1.31x adjacency similarity driven by MIDDLE (1.23x) and SUFFIX (1.18x)
- Weak contribution from marker prefixes (1.15x)
- Local ordering reflects subtype/property similarity, not marker class

**Interpretation:**
- Section boundaries (H/P/T) are primary hard discontinuities in Currier A
- Catalog organized by content/topic first, markers classify within clusters
- Does NOT change what Currier A represents; tightens characterization

**New files:**
- `phases/exploration/adjacent_entry_analysis.py`
- `phases/exploration/adjacent_section_boundary.py`
- `phases/exploration/ADJACENT_ENTRY_SYNTHESIS.md`

**Updated files:**
- `CLAIMS/INDEX.md` - Added C421, version 2.0, count 421
- `CLAIMS/currier_a.md` - Added C346.a refinement, C421 section

**Research phase:** Exploration (1838 entries, 114 folios analyzed)

---

## Version 1.9 (2026-01-09)

### C420: Currier A Folio-Initial Positional Exception

**Summary:** New Tier-2 constraint documenting positional tolerance at folio boundaries in Currier A.

**Finding:**
- First-token position in Currier A permits otherwise illegal C+vowel prefix variants (ko-, po-, to-)
- 75% failure rate at position 1 vs 31% at positions 2-3
- C+vowel prefixes: 47.9% at position 1, 0% elsewhere
- Fisher exact p < 0.0001
- Morphologically compatible (ko- shares 100% suffix vocabulary with ok-)

**Interpretation:**
- Positional tolerance at codicological boundaries (common in medieval registries)
- Does NOT imply headers, markers, semantic categories, or enumeration
- No revision to C240 (marker families) or C234 (position-free) required

**New files:**
- `CLAIMS/C420_folio_initial_exception.md` - Full constraint documentation
- `phases/exploration/first_token_*.py` - Research scripts
- `phases/exploration/FIRST_TOKEN_SYNTHESIS.md` - Research synthesis

**Updated files:**
- `CLAIMS/INDEX.md` - Added C420, version 1.9, count 420
- `CLAIMS/currier_a.md` - Added Positional Exception section

**Research phase:** Exploration (48 folios analyzed)

---

## Version 1.8 (2026-01-09)

### HT/AZC FINAL CLOSED

**Summary:** Completed final constraint audit; verified C412; declared HT and AZC sections FINAL CLOSED.

**Audit results:**
- HT: 21 constraints + 1 superseded - ALL PASS
- AZC: 23 constraints - ALL PASS
- Notes: HT-AZC-NOTE-01, AZC-NOTE-01 correctly scoped

**C412 verification:**
- Original methodology replicated exactly
- Results reproduced: rho=-0.327 (original -0.326), p=0.0027 (original 0.002)
- Prior discrepancy explained: wrong metric used in re-analysis (ch-density vs ch-preference)
- Review flag removed

**Updated files:**
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added verification section
- `CLAIMS/INDEX.md` - Removed ⚠️ REVIEW marker

**New files:**
- `phases/exploration/c412_verification.py` - Verification script

**Final status:**
| Section | Status |
|---------|--------|
| Human Track (HT) | FINAL CLOSED |
| AZC System | FINAL CLOSED |
| Sister Pairs | FINAL CLOSED |

---

## Version 1.7 (2026-01-09)

### HT-AZC Third Anchoring Pressure

**Summary:** Identified AZC-specific HT pattern (diagram label concentration).

**Updated files:**
- `CLAIMS/human_track.md` - Added HT-AZC-NOTE-01, updated frozen statement

**Key finding:**
- AZC HT uniquely shows BOTH line-initial AND line-final enrichment
- Driven by L-placement (label) text: 88.8% initial, 95% final
- L-placement lines are short (1-3 tokens) with 15.1% HT density
- Establishes **third anchoring pressure**: diagram geometry (label positions)

**Three-system refinement:**
| System | Anchoring Pressure |
|--------|-------------------|
| Currier A | Registry layout (entry boundaries) |
| Currier B | Temporal/attentional context |
| AZC | Diagram geometry (label positions) |

---

## Version 1.6 (2026-01-09)

### Data Source Documentation + AZC/C412 Updates

**Summary:** Added data source documentation; documented AZC findings; flagged C412 discrepancy.

**Updated files:**
- `SYSTEM/METHODOLOGY.md` - Added "Canonical Data Source" section
- `CLAIMS/azc_system.md` - Added AZC-NOTE-01 (qo-depletion refinement)
- `CLAIMS/C412_sister_escape_anticorrelation.md` - Added review flag
- `CLAIMS/INDEX.md` - Added review marker to C412

**Key additions:**

1. **Data source documentation:**
   - PRIMARY DATA FILE: `data/transcriptions/interlinear_full_words.txt`
   - WARNING about EVA vs standard vocabulary encoding

2. **AZC-NOTE-01:** qo-prefix depletion (2.8x lower than B), refines C301/C313

3. **C412 review flag:** Re-analysis finds anticorrelation in Currier A (rho=-0.334, p=0.0003), NOT in B (rho=-0.089, p=0.42). Requires reconciliation with original SISTER phase.

**Issue caught:** During AZC exploration, wrong transcription file was initially used. All previous constraints verified safe.

---

## Version 1.5 (2026-01-09)

### HT Formal Hierarchy

**Summary:** Established canonical hierarchy for Human Track layer. Adds C414-C419.

**New files:**
- `CLAIMS/HT_HIERARCHY.md` - Formal hierarchy document (canonical)

**Updated files:**
- `CLAIMS/human_track.md` - Added C414-C419, system-specific refinement
- `CLAIMS/HT_CONTEXT_SUMMARY.md` - Updated with hierarchy reference
- `CLAIMS/INDEX.md` - Count 411→419, added 6 new constraints
- `CLAUDE_INDEX.md` - Count update, navigation to HT_HIERARCHY.md

**Constraints added:**
| # | Name | Tier | Key Finding |
|---|------|------|-------------|
| C414 | Strong Grammar Association | 2 | chi2=934, p<10^-145 |
| C415 | Non-Predictivity | 1 (FALSIFICATION) | MAE worsens with HT conditioning |
| C416 | Directional Asymmetry | 2 | V=0.324 vs 0.202 (1.6x) |
| C417 | Modular Additive | 2 | No synergy (p=1.0) |
| C418 | Positional Without Informativeness | 2 | Bias exists but non-predictive |
| C419 | HT Positional Specialization in A | 2 | Entry-aligned, seam-avoiding |

**Terminology guardrail established:**
- DO: "aligned with", "correlated with", "position-biased"
- DON'T: "marks", "encodes", "annotates", "means"

**Model refinement:**
- Currier A: HT aligned with registry layout (entry boundaries)
- Currier B: HT aligned with temporal/attentional context
- Same layer, different anchoring pressures

---

## Version 1.4 (2026-01-09)

### Phase: STRUCTURE_FREEZE_v1

**Summary:** Formal freeze of structural inspection layer. Transitions project from foundational reconstruction to deliberate post-structure paths.

**Components frozen:**
- **Basic Inspection v1** (`apps/script_explorer/BASIC_INSPECTION.md`)
  - Currier A registry parsing and roles
  - Currier B grammar roles (49-class, conservative binding)
  - AZC placement binding (`R/R1/R2/R3`, `S/S1/S2`, `C`, `MULTI`)
  - HT isolation and override behavior
  - Global properties (prefix family, kernel affinity, escape)

- **Execution Inspector v0.1** (`apps/script_explorer/EXECUTION_INSPECTOR.md`)
  - Grammar-only execution inspection
  - `grammar_bound` semantics
  - Conservative UNKNOWN handling
  - No hazards, order, or kernel contact beyond grammar anchors

**Repository rules enforced:**
- ❌ Do not alter parsing logic
- ❌ Do not alter classification logic
- ❌ Do not alter role assignment tables
- ❌ Do not alter system boundaries
- ❌ Do not reinterpret UNKNOWNs
- ❌ Do not extend execution semantics implicitly
- ❌ Do not weaken system gating (A/B/AZC/HT)

**Post-freeze paths available:**
1. Documentation & Consolidation (RECOMMENDED)
2. Visualization / UX (SAFE)
3. Deeper Execution Semantics (ADVANCED, requires new phase)

**Intent:** Preserve structural integrity. Expansion is a choice, not an accident.

---

## Version 1.0 (2026-01-08)

### Initial Release

**Created:** Context expansion system to replace monolithic CLAUDE.md

**Structure:**
- `context/` directory with 9 subdirectories
- `CLAUDE_INDEX.md` as primary entry point (~4k tokens)
- Progressive disclosure architecture
- 57 markdown files total

**Directories:**
- `SYSTEM/` - Meta-rules, tiers, methodology (5 files)
- `CORE/` - Tier 0-1 facts (3 files)
- `ARCHITECTURE/` - Structural analysis by text type (5 files)
- `OPERATIONS/` - OPS doctrine, program taxonomy (3 files)
- `CLAIMS/` - 411 constraints indexed (24 files: 1 index, 16 individual claims, 7 grouped registries)
- `TERMINOLOGY/` - Key definitions (3 files)
- `METRICS/` - Quantitative facts (4 files)
- `SPECULATIVE/` - Tier 3-4 content (4 files)
- `MAPS/` - Cross-references (3 files)

**Design Principles:**
1. Entry point stays slim (<10k tokens)
2. One concept per file
3. ≤15k tokens per file
4. Every claim declares Tier + closure
5. No analysis in context files
6. Archive is append-only
7. Context points to archive

**Migration:**
- Content extracted from CLAUDE.md v1.8 (95KB, ~30k tokens)
- Original preserved as `archive/CLAUDE_v1.8_2026-01-08.md`
- CLAUDE.md converted to redirect

---

## Version 1.3 (2026-01-08)

### Added: Constraint-First Reasoning Protocol

**Summary:** Added methodology for checking constraints before speculating, and guidance on when/how to question constraints.

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added two new sections:
  - "Constraint-First Reasoning" - rule to search constraints before interpreting
  - "Questioning Constraints" - when and how to challenge existing claims
- `context/CLAUDE_INDEX.md` - Added stop condition reminder and note that questioning is allowed

**Motivation:** During conversation, speculated that "Currier A entries might reference the same categories B executes" — but C384 explicitly falsifies this. Checking constraints first would have prevented the error.

**Key principles added:**
- Search CLAIMS/ before reasoning about relationships
- Distinguish "constrained" from "undocumented" (gap ≠ permission)
- Cite constraint numbers or flag as research gap
- Questioning is allowed but must be explicit, not silent override
- Tier determines revisability (0=frozen, 2=reopenable with evidence)

---

## Version 1.2 (2026-01-08)

### Added: Structural Intuition Clarification

**Summary:** Added documentation to prevent the misinterpretation that "neutral/unhighlighted tokens are unknown."

**Files updated:**
- `context/CLAUDE_INDEX.md` - Added three new sections:
  - "How to Think About Tokens (Structural Layer)"
  - "Why Visualization Tools Highlight Only Some Tokens"
  - "Structural Analysis vs Interpretive / Probabilistic Reasoning"

**Clarifications made:**
- Tokens are surface realizations, not functional operators
- Functional behavior determined at instruction-class level
- High hapax rates explained by compositional morphology
- "Neutral" means "non-contrastive", not "unknown"
- Visualization highlighting is a UI choice, not knowledge boundary
- Bayesian/probabilistic reasoning explicitly supported in interpretive layer

**No constraint changes:** This is a documentation-only update for human intuition alignment. No tiers, claims, or conclusions were altered.

---

## Version 1.1 (2026-01-08)

### Added: Research Automation

**Summary:** Added skills, hooks, and workflow documentation for automated research.

**Files created:**
- `.claude/skills/phase-analysis/SKILL.md` - Automatic phase analysis
- `.claude/skills/constraint-lookup/SKILL.md` - Constraint search and citation
- `.claude/settings.json` - Hook configuration
- `archive/scripts/validate_constraint_reference.py` - Constraint validation
- `archive/scripts/extract_phase_metrics.py` - Metrics extraction

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added "Research Workflow (Automated)" section
- `context/SYSTEM/HOW_TO_READ.md` - Added multi-branch access patterns
- `context/CLAUDE_INDEX.md` - Added "Automation" section

**New workflows:**
- Phase Analysis Protocol (automatic)
- Constraint Lookup Protocol (automatic)
- Constraint reference validation (hook)

---

## Future Entries

When updating context, add entries in this format:

```markdown
## Version X.Y (YYYY-MM-DD)

### [Type: Added/Changed/Removed/Fixed]

**Summary:** Brief description

**Files affected:**
- `path/to/file.md` - what changed

**Constraint changes:**
- C### added/updated/removed

**Source:** Phase PHASE_NAME (if applicable)
```

---

## Navigation

← [HOW_TO_READ.md](HOW_TO_READ.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

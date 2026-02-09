# Recipe Triangulation Methodology

**Tier**: 3 (Interpretive - requires Brunschwig alignment)
**Status**: INVALIDATED - Methodology was based on incorrect record unit
**Phase**: ANIMAL_PRECISION_CORRELATION, MATERIAL_MAPPING_V2

---

## CRITICAL INVALIDATION (2026-01-29)

**The entire methodology described below is INVALID because it treats lines as records.**

A records are **paragraphs**, not lines. Initial RI (material ID) appears in the **first line** of a paragraph, not as the first token of a "record" defined by line.

**Evidence:**
- eoschso (MIDDLE of "okeoschso") appears at position 41/70 in paragraph A_268
- This is in the MIDDLE of the paragraph, not the first line
- Therefore eoschso is NOT an initial RI (material identifier)

**The eoschso = chicken identification is INVALID.**

See `phases/MATERIAL_MAPPING_V2/FINDINGS.md` for corrected paragraph-level methodology.

---

---

## CRITICAL CORRECTIONS (2026-01-21) + Curation Complete (2026-01-22)

Manual curation of Brunschwig OCR text revealed major errors in automated extraction:

| Original Claim | Correction | Impact |
|----------------|------------|--------|
| beste = heo | **INVALID** - "beste" is an adjective ("das beste wasser"), not a material name | Remove from validated list |
| scharlach = animal (kermes insect) | **INVALID** - Text says "iſt ein krut wie ſalbet" (is an herb like sage) = CLARY SAGE | chald identification rejected |
| frog (frosch) = ofy | **INVALID** - OCR corrupted, no readable procedure | ofy identification unverified |
| thyme sequence [RECOVERY, LINK] | **CORRECTED** to [AUX, e_ESCAPE] | keolo identification needs reverification |
| chicken sequence [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE] | **CORRECTED** to [AUX, e_ESCAPE, FLOW, k_ENERGY] | eoschso still valid but different profile |

**Root cause**: Original data extracted via regex pattern `X wasser` which captured:
- Adjectives as materials (beste, gut, erst, ander)
- Procedure text from adjacent entries
- Wrong material classifications

**Data Curation Complete (2026-01-22):**
- 203 recipes re-scanned for instruction keywords
- 16 corrections applied via automated scanner + manual validation
- Spot-checked 4 random recipes (#89, #98, #119, #159) against OCR - all correct
- **Sequence diversity improved**: 5 unique → 12 unique instruction sequences
- **170 generic [AUX, e_ESCAPE]** + **33 specialized sequences**

**Data source**: Use `data/brunschwig_complete.json` (curated with all 203 recipes)

---

## Purpose

Map Brunschwig recipe characteristics to specific Voynich A records containing material-identifying RI tokens.

---

## Key Insight

**Single PP tokens don't discriminate.** Different recipes (even different fire degrees) share 90%+ of PP vocabulary at the folio level.

**Multi-dimensional PP convergence at RECORD level DOES discriminate** when combined with PREFIX profile matching against instruction patterns.

---

## The Pipeline

```
Brunschwig Recipe
       ↓
[1] Extract Recipe Dimensions
       ↓
[2] Map to B Folio Constraints
       ↓
[3] Multi-dimensional Conjunction → Candidate B Folios
       ↓
[4] Extract PP Vocabulary (discriminative only)
       ↓
[5] Find A RECORDS with Multiple PP Convergence
       ↓
[6] Extract RI Tokens from Converging Records
       ↓
[7] Match PREFIX Profiles to Instruction Patterns
       ↓
[8] Compare with Brunschwig Sequences → Material Identification
```

---

## Step-by-Step Process

### Step 1: Extract Recipe Dimensions

From Brunschwig entry, extract:

| Dimension | Source | Maps to |
|-----------|--------|---------|
| fire_degree | Recipe text | REGIME_N |
| instruction_sequence | Procedural steps | PREFIX profile |
| material_source | Entry classification | Material class prior |

**Example - Chicken (hennen)** (CORRECTED):
- fire_degree: 4 → REGIME_4
- instruction_sequence: [AUX, e_ESCAPE, FLOW, k_ENERGY] *(manual reading of OCR)*
- material_source: animal

**Note**: Original automated extraction claimed [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE]. Manual reading shows AUX (preparation) comes BEFORE e_ESCAPE (distillation), plus FLOW (collection) and k_ENERGY (balneum mariae redistillation).

### Step 2: Map to B Folio Constraints

| Recipe Dimension | B Constraint | Implementation |
|------------------|--------------|----------------|
| fire_degree = N | REGIME_N folios | `regime_folio_mapping.json` |
| e_ESCAPE in sequence | High qo ratio | `qo_ratio >= avg_qo` |
| AUX in sequence | High ok/ot ratio | `(ok+ot)/total >= avg_aux` |
| FLOW in sequence | High da ratio | `da_ratio >= avg_da` |
| No FLOW | Low da ratio | `da_ratio <= avg_da` |

**Instruction → PREFIX mapping**:
- e_ESCAPE → qo (escape/recovery)
- AUX → ok, ot (auxiliary)
- FLOW → da (direct action)
- LINK → monitoring operations

### Step 3: Multi-dimensional Conjunction

Apply ALL constraints simultaneously to narrow B folios.

```python
candidate_folios = (
    regime_folios &
    high_qo_folios &
    high_aux_folios &
    low_da_folios  # if no FLOW in sequence
)
```

**Critical**: Conjunction narrows synergistically (ratio < 1.0 vs independent expectation). Single dimensions give 30-55% of folios; 4D conjunction gave 1 folio for chicken.

### Step 4: Extract PP Vocabulary

From candidate B folios, get discriminative PP:

```python
candidate_middles = set()
for folio in candidate_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    candidate_middles.update(folio_tokens['middle'].dropna().unique())

# Filter to shared (PP) only, remove infrastructure
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
discriminative_pp = (candidate_middles & shared_middles) - infrastructure
```

### Step 5: Find A RECORDS with Multiple PP Convergence

**KEY STEP**: Work at RECORD level (folio:line), not folio level.

```python
a_records = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()

a_records['pp_overlap'] = a_records['middles'].apply(
    lambda x: len(x & discriminative_pp)
)

# Require multiple PP convergence (not just 1)
converging_records = a_records[a_records['pp_overlap'] >= 3]
```

**Why record level matters**: Folio-level gives 90%+ overlap between recipes. Record-level with 3+ PP convergence narrows to specific entries.

### Step 6: Extract RI from Converging Records

RI tokens (Registry-Internal) stay in A, never enter B. These encode material identity.

```python
for _, row in converging_records.iterrows():
    ri_tokens = row['middles'] - b_middles
    # These are material candidates
```

Cross-reference with known material class priors from `material_class_priors.json`.

### Step 7: Match PREFIX Profiles to Instruction Patterns

For each converging record's PP tokens, check their PREFIX distribution in B:

```python
def get_prefix_profile(middle):
    b_tokens = df_b[df_b['middle'] == middle]
    prefix_counts = b_tokens['prefix'].value_counts()
    total = len(b_tokens)
    return {
        'escape': prefix_counts.get('qo', 0) / total,
        'aux': (prefix_counts.get('ok', 0) + prefix_counts.get('ot', 0)) / total,
        'flow': prefix_counts.get('da', 0) / total
    }
```

**Chicken score** = escape + aux - flow (higher = more chicken-like)

### Step 8: Compare with Brunschwig Sequences

Match PREFIX profile to instruction sequence:

| Instruction Sequence | Expected Profile |
|---------------------|------------------|
| [e_ESCAPE, AUX, ...] | High escape, high aux |
| [e_ESCAPE, FLOW, ...] | High escape, high flow |
| [AUX, UNKNOWN] | High aux only |
| [UNKNOWN, LINK] | Link operations |

**Example result (INVALIDATED)**: ~~eoschso was the only animal RI token in a record with BOTH escape PP (ke, keo) AND aux PP (ch), matching chicken's unique [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE] pattern.~~ This finding is invalid because eoschso is not initial RI - it appears at position 41/70 in paragraph A_268, not in the first line.

---

## Worked Example: Chicken Identification

### Input (CORRECTED from manual OCR reading)
- Recipe: hennen (chicken)
- fire_degree: 4
- instruction_sequence: [AUX, e_ESCAPE, FLOW, k_ENERGY] *(was [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE])*
- material_source: animal

**Note**: The corrected sequence shows preparation (AUX) comes BEFORE distillation (e_ESCAPE), not after. This changes the expected PREFIX profile but eoschso identification remains valid due to unique AUX+ESCAPE combination among animals.

### Step 3 Result
4D conjunction (REGIME_4 + high qo + high aux + low da) → 1 folio: f95v1

Expanding to chicken-like folios (relaxed threshold): f40v, f41v, f85r1, f94v, f95v1

### Step 5 Result
110 A records converge to 3+ chicken folios at 2+ PP each

### Step 6 Result
4 records contain known animal RI tokens:
- f100r:3 → teold
- f89r2:1 → eyd
- f23r:4 → chald
- f90r1:6 → eoschso

### Step 7 Result
| RI Token | Unique PP | Escape? | Aux? |
|----------|-----------|---------|------|
| teold | t | 88% | 0% |
| chald | fch | 74% | 0% |
| eoschso | ch,l | 24% | 48% |
| eyd | d,ckh,eod | 14% | 9% |

### Step 8 Result
Only **eoschso** has BOTH escape AND aux PP, matching chicken's [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE].

**~~Conclusion: eoschso = ennen (chicken)~~**

**INVALIDATED (2026-01-29):** This conclusion is based on treating lines as records. eoschso appears at position 41/70 in paragraph A_268 - it is NOT initial RI.

---

## Validated Identifications (REVISED)

| Material | Brunschwig | Token | Location | CORRECTED Steps | Confidence |
|----------|------------|-------|----------|-----------------|------------|
| ~~Chicken~~ | ~~hennen~~ | ~~eoschso~~ | ~~f90r1:6~~ | ~~AUX, e_ESCAPE, FLOW, k_ENERGY~~ | **INVALIDATED** |
| Thyme | quendel | **keolo** | f99v:7 | AUX, e_ESCAPE | MEDIUM (needs reverification) |

### INVALIDATED Identifications

| Material | Token | Reason |
|----------|-------|--------|
| **Chicken** | **eoschso** | **METHODOLOGY ERROR** - eoschso is NOT initial RI; appears at position 41/70 in paragraph A_268 (middle lines, not first line) |
| ~~Frog~~ | ~~ofy~~ | OCR CORRUPTED - no readable procedure in source text |
| ~~Scharlach~~ | ~~chald~~ | MISCLASSIFIED - Scharlach is CLARY SAGE (herb), not kermes insect (animal) |
| ~~Beste~~ | ~~heo~~ | FALSE POSITIVE - "beste" is an adjective, not a material name |

### Discrimination Notes (Updated)

**Chicken identification is INVALID.** The methodology treated lines as records, but A records are paragraphs. eoschso appears in the middle of its paragraph, not as initial RI in the first line.

**Thyme identification needs reverification** - original claimed [RECOVERY, LINK] but actual text shows [AUX, e_ESCAPE]. Same pattern as many herbs. keolo may have been found via different mechanism than claimed.

---

## Critical Warnings

### UNKNOWN Steps in Brunschwig Sequences

**Problem**: ~40% of extracted Brunschwig steps are classified as UNKNOWN. These are primarily **usage/dosage instructions** (how to take the water), not production steps.

**Rule**: Only match on KNOWN instruction classes. UNKNOWN = "no information", not a signal.

| Material | CORRECTED Sequence | Notes |
|----------|-------------------|-------|
| Chicken (hennen) | AUX → e_ESCAPE → FLOW → k_ENERGY | Manual OCR reading |
| Thyme (quendel) | AUX → e_ESCAPE | Manual OCR reading |
| Frog (frosch) | [CORRUPTED] | OCR unreadable |

**Consequence**: Materials with few KNOWN steps (like frog) have weaker discrimination. Fall back to:
- REGIME + class priors
- Process of elimination ("not chicken, not thyme")

### DO NOT
- Use single PP tokens for discrimination (90%+ overlap)
- Work at folio level instead of record level
- Skip PREFIX profile matching (just PP convergence is insufficient)
- Assume REGIME alone discriminates (it provides weak selection)
- **Treat UNKNOWN as a positive signal** (it means "no information")
- **Match on instruction sequences with only UNKNOWN steps**

### DO
- Use multi-dimensional conjunction for B folio selection
- Require 3+ PP convergence at record level
- Match PREFIX profiles to instruction patterns
- Compare against Brunschwig sequences for final identification
- **Strip UNKNOWN from sequences before matching**
- **Flag identifications with few KNOWN steps as provisional**

---

## Materials Without Specific Procedures

**Finding**: Materials without specific Brunschwig procedures (like rose/flowers) cannot be triangulated using this method.

| Material Type | Has Procedure | Triangulation |
|---------------|---------------|---------------|
| Animals (chicken, frog) | Yes (fire=4) | Works |
| Precision herbs (thyme) | Yes (override) | Works |
| Generic herbs | Generic only | Class-level only |
| Flowers (rose) | No procedure | Fails - sparse records |

**Why flowers fail**: Rose water was so common Brunschwig didn't describe how to make it. Flower entries in Currier A have sparse morphological structure (avg 0.3 PP vs 5.3 PP for animals). No PP context = no convergence possible.

**Implication**: The Voynich registry only assigns specific tokens to materials requiring specific handling. Generic materials get class-level designation only.

---

## Constraints Referenced

- C384: No entry-level A-B coupling (via single tokens)
- C466-467: PREFIX control-flow semantics
- C495: REGIME compatibility
- C498: Two-track vocabulary (PP vs RI)

---

## Files

| Purpose | Location |
|---------|----------|
| Regime mapping | `results/regime_folio_mapping.json` |
| Material priors | `phases/BRUNSCHWIG_CANDIDATE_LABELING/results/material_class_priors.json` |
| **Brunschwig data (CURATED)** | `data/brunschwig_complete.json` |
| ~~Old data (ARCHIVED)~~ | ~~`archive/data/brunschwig_materials_master_ARCHIVED_*.json`~~ |
| Scripts | `phases/ANIMAL_PRECISION_CORRELATION/scripts/` |
| Results | `phases/ANIMAL_PRECISION_CORRELATION/results/` |
| **Progress tracking** | `phases/ANIMAL_PRECISION_CORRELATION/INSTRUCTION_EXTRACTION_PROGRESS.md` |

---

## Next Steps for Refinement

### Completed (Pre-Curation)
1. ~~Apply to plant materials (rose water, etc.) as control~~ - DONE: Fails as expected (no procedure)

### INVALIDATED by Manual Curation
2. ~~Test if scharlach/charlach/milch map to teold/chald~~ - **INVALID**: Scharlach is a herb, not an animal
3. ~~Identify which animals have LINK pattern (frosch?)~~ - **INVALID**: Frog OCR corrupted
4. ~~Test beste/besser/ish/kyrsen (precision herb with FLOW)~~ - **INVALID**: "beste" is an adjective
7. ~~Cross-validate: chald appears in chicken analysis but has scharlach-like da profile~~ - **INVALID**: Wrong material class

### Remaining Tasks
5. Build automated pipeline for any recipe - **Blocked until data quality resolved**
6. Find additional animal materials with valid procedures in OCR
8. **NEW**: Re-verify thyme (keolo) identification with corrected sequence [AUX, e_ESCAPE]
9. **NEW**: Attempt triangulation on curated blood waters (duck, goat, calf)

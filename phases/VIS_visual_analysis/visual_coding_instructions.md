# Visual Feature Coding Instructions for Voynich Manuscript Pilot Study

## Pre-Registration Statement

**This analysis is pre-registered. We commit to:**
- Testing exactly 30 Currier A herbal folios (listed below)
- Using only objectively defined visual features
- Reporting all results including negative findings
- Defining success/failure criteria in advance
- Not modifying hypotheses after seeing results

---

## 1. Folio Selection

### 1.1 Selection Criteria

| Criterion | Value |
|-----------|-------|
| Population | Currier A only |
| Section | Herbal (H) only |
| Total available | 95 herbal folios |
| Selected | 30 folios |
| Distribution | 10 short, 10 medium, 10 long |
| Prefix diversity | 24 unique opening prefixes |

### 1.2 Selected Folios

**SHORT ENTRIES (10 folios, 42-88 words)**

| Folio | Words | Opening Prefix | Opening Word |
|-------|-------|----------------|--------------|
| f38r | 42 | to | tolor |
| f25r | 48 | fc | fcholdy |
| f11r | 57 | ts | tshol |
| f11v | 57 | po | poldchody |
| f5v | 58 | ko | kocheor |
| f10v | 63 | pa | paiin |
| f38v | 65 | ok | okchop |
| f5r | 66 | ks | kshody |
| f36r | 70 | pc | pchafdan |
| f30v | 75 | ct | cthscthain |

**MEDIUM ENTRIES (10 folios, 89-105 words)**

| Folio | Words | Opening Prefix | Opening Word |
|-------|-------|----------------|--------------|
| f22v | 90 | py | pysaiinor |
| f9v | 94 | fo | fochor |
| f90v2 | 95 | cp | cphdaithy |
| f32v | 97 | kc | kcheodaiin |
| f17r | 99 | fs | fshody |
| f18r | 100 | pd | pdrairdy |
| f9r | 101 | ty | tydlo |
| f20v | 103 | fa | faiis |
| f2r | 103 | ky | kydainy |
| f47v | 104 | ps | psheot |

**LONG ENTRIES (10 folios, >105 words)**

| Folio | Words | Opening Prefix | Opening Word |
|-------|-------|----------------|--------------|
| f24v | 117 | tc | tchodar |
| f56r | 127 | ot | otchal |
| f42r | 174 | sh | sho |
| f49v | 189 | r* | r* |
| f51v | 108 | po | poshody |
| f45v | 109 | ko | korary |
| f3v | 110 | ko | koaiin |
| f29v | 112 | ko | kooiin |
| f4v | 112 | pc | pchooiin |
| f23v | 113 | po | podairol |

### 1.3 Selection Rationale

- **Word count diversity:** Tercile-based selection ensures coverage of short, medium, and long entries
- **Prefix diversity:** 24 different opening prefixes represented (maximizes heading word variation)
- **No cherry-picking:** Algorithmic selection, no prior plant identifications considered
- **Section purity:** Only herbal folios (section H), excludes pharmaceutical (P), text-only (T), zodiac, biological

---

## 2. Visual Feature Coding Protocol

### 2.1 General Principles

1. **Code ONLY what is visually observable** - NO interpretation or identification
2. **Use UNSURE only when genuinely ambiguous** - not for difficult decisions
3. **Code the PREDOMINANT pattern** when multiple exist
4. **Each folio coded independently** - do not compare between folios while coding
5. **Record coder ID and date** for reproducibility
6. **Complete all features for one folio before moving to next**

### 2.2 Materials Required

- High-resolution scans of the 30 pilot folios
- This coding sheet (printed or digital)
- Source: Yale Beinecke Library digital scans (preferred) or equivalent
- Minimum resolution: visible leaf margins, root textures, flower details

---

## 3. Feature Definitions and Decision Rules

### 3.1 ROOT FEATURES (4 features)

#### root_present
| Value | Definition |
|-------|------------|
| **YES** | Any root structure visible below the stem base or soil line |
| **NO** | No root structure visible; plant appears to end at ground level |

*Decision rule: If any part of the plant extends downward in a root-like manner (bulb, taproot, fibers), code YES.*

#### root_type
| Value | Definition |
|-------|------------|
| **NONE** | No root visible |
| **SINGLE_TAPROOT** | Single main root descending vertically, may have minor side roots |
| **BRANCHING** | Root divides into 2+ distinct thick branches |
| **BULBOUS** | Round swelling at root base (like onion, garlic) |
| **FIBROUS** | Many thin roots of similar size, no dominant central root |

*Decision rule: BRANCHING requires distinct thick branches (like tree roots). FIBROUS is many fine roots (like grass). If bulb-shaped regardless of other features, code BULBOUS.*

#### root_color_distinct
| Value | Definition |
|-------|------------|
| **YES** | Root is colored differently from stem (different ink color or shading) |
| **NO** | Root is same color/shading as stem |

#### root_prominence
| Value | Definition |
|-------|------------|
| **SMALL** | Root < 20% of total plant height |
| **MEDIUM** | Root 20-40% of total plant height |
| **LARGE** | Root > 40% of total plant height |
| **NA** | Root not present |

*Decision rule: Measure visually. Include bulb in root measurement if bulbous type.*

---

### 3.2 STEM FEATURES (4 features)

#### stem_count
| Value | Definition |
|-------|------------|
| **1** | Single main stem from root/base |
| **2** | Two main stems from root/base |
| **3+** | Three or more main stems from root/base |

*Decision rule: Count stems emerging from the base. Do not count branches higher up.*

#### stem_type
| Value | Definition |
|-------|------------|
| **STRAIGHT** | Stem grows in predominantly straight vertical line |
| **CURVED** | Stem has gradual curve or S-shape |
| **BRANCHING** | Main stem divides into multiple branches above the base |
| **TWINING** | Stem appears to wrap, climb, or spiral |

*Decision rule: Code predominant pattern. If stem branches above base, code BRANCHING.*

#### stem_thickness
| Value | Definition |
|-------|------------|
| **THIN** | Line-like, minimal visible width |
| **MEDIUM** | Visible width, neither line-like nor trunk-like |
| **THICK** | Substantial width, trunk-like appearance |

*Decision rule: Compare to typical herbal stem; thick = woody/tree-like.*

#### stem_color_distinct
| Value | Definition |
|-------|------------|
| **YES** | Stem colored differently from leaves |
| **NO** | Stem same color as leaves |

---

### 3.3 LEAF FEATURES (6 features)

#### leaf_present
| Value | Definition |
|-------|------------|
| **YES** | Any leaf structures visible on plant |
| **NO** | No recognizable leaf structures |

#### leaf_count_category
| Value | Definition |
|-------|------------|
| **NONE** | No leaves present |
| **FEW_1-5** | 1 to 5 distinct leaves |
| **MEDIUM_6-15** | 6 to 15 distinct leaves |
| **MANY_16+** | 16 or more distinct leaves |

*Decision rule: Count individual leaves, not leaflets of compound leaves.*

#### leaf_shape
| Value | Definition |
|-------|------------|
| **ROUND** | Circular or near-circular outline |
| **OVAL** | Elliptical outline, longer than wide |
| **LANCEOLATE** | Long and narrow, tapering at both ends (lance-shaped) |
| **LOBED** | Deep indentations extending >25% into leaf (like oak) |
| **COMPOUND** | Multiple distinct leaflets attached to single stem (like rose) |
| **SERRATED** | Toothed/jagged margin, teeth <25% into leaf |
| **NEEDLE** | Very thin, needle-like (like pine) |
| **MIXED** | Multiple distinct shapes present; no dominant type |

*Decision rules:*
- *LOBED vs SERRATED: Lobed indentations go >25% into leaf; serrated teeth are shallow (<25%)*
- *LOBED vs COMPOUND: Lobed is single leaf with indentations; compound has separate leaflets*
- *Code PREDOMINANT shape if >50% of leaves share it; otherwise MIXED*

#### leaf_arrangement
| Value | Definition |
|-------|------------|
| **ALTERNATE** | Single leaf at each node, alternating sides along stem |
| **OPPOSITE** | Two leaves at each node, facing each other |
| **BASAL** | Leaves emerge from base/ground level, not along stem |
| **WHORLED** | Three or more leaves at each node, radiating |
| **SCATTERED** | No clear pattern discernible |
| **NA** | Leaves not present |

#### leaf_size_relative
| Value | Definition |
|-------|------------|
| **SMALL** | Leaves are small relative to overall plant size (<20% plant height) |
| **MEDIUM** | Leaves are medium relative to plant (20-40% plant height) |
| **LARGE** | Leaves are large/dominant feature (>40% plant height) |
| **MIXED** | Significant variation in leaf sizes |

#### leaf_color_uniform
| Value | Definition |
|-------|------------|
| **YES** | All leaves same color/shading |
| **NO** | Leaves show multiple colors or shading variations |
| **NA** | Leaves not present |

---

### 3.4 FLOWER FEATURES (5 features)

#### flower_present
| Value | Definition |
|-------|------------|
| **YES** | Any flower, bud, or reproductive structure visible |
| **NO** | No recognizable flower structures |

#### flower_count
| Value | Definition |
|-------|------------|
| **NONE** | No flowers present |
| **1** | Single flower |
| **2-5** | 2 to 5 distinct flowers |
| **6+** | 6 or more flowers |

*Decision rule: Count distinct flower heads, not petals.*

#### flower_position
| Value | Definition |
|-------|------------|
| **NONE** | No flowers present |
| **TERMINAL** | Flower(s) at stem tip(s) only |
| **AXILLARY** | Flower(s) at leaf axils (where leaf meets stem) |
| **THROUGHOUT** | Flowers distributed along stem length |

#### flower_color_distinct
| Value | Definition |
|-------|------------|
| **YES** | Flower colored differently from leaves |
| **NO** | Flower same color as leaves |
| **NA** | No flowers present |

#### flower_shape
| Value | Definition |
|-------|------------|
| **NONE** | No flowers present |
| **SIMPLE** | Basic flower form, few petals, not compound |
| **COMPOUND** | Cluster of small flowers (like daisy center) |
| **RADIAL** | Star-shaped with distinct petals radiating |
| **IRREGULAR** | Asymmetric flower shape |

---

### 3.5 OVERALL FEATURES (6 features)

#### plant_count
| Value | Definition |
|-------|------------|
| **1** | Single plant depicted on folio |
| **2** | Two distinct plants on folio |
| **3+** | Three or more distinct plants |

*Decision rule: Count separate plants with own root systems, not branches of one plant.*

#### container_present
| Value | Definition |
|-------|------------|
| **YES** | Plant shown in pot, vase, or container |
| **NO** | Plant shown without container (in ground or floating) |

#### plant_symmetry
| Value | Definition |
|-------|------------|
| **SYMMETRIC** | Plant shows left-right mirror symmetry |
| **ASYMMETRIC** | Plant is not symmetric |

*Decision rule: Approximate symmetry counts. Minor deviations OK for SYMMETRIC.*

#### overall_complexity
| Value | Definition |
|-------|------------|
| **SIMPLE** | Fewer than 5 distinct visual elements |
| **MODERATE** | 5-15 distinct visual elements |
| **COMPLEX** | More than 15 distinct visual elements, intricate detail |

*Decision rule: Elements = leaves + flowers + branches + distinctive features.*

#### identifiable_impression
| Value | Definition |
|-------|------------|
| **YES** | Drawing gives impression of representing a real, identifiable plant |
| **NO** | Drawing appears fantastical, schematic, or unreal |
| **UNCERTAIN** | Cannot determine |

*Decision rule: Subjective but record initial impression. Do NOT try to identify.*

#### drawing_completeness
| Value | Definition |
|-------|------------|
| **COMPLETE** | Drawing appears finished, all parts visible |
| **PARTIAL** | Some parts appear unfinished or cut off by page edge |
| **FRAGMENTARY** | Significant damage, fading, or incompleteness |

---

## 4. Coding Sheet Template

### Folio: __________ Coder ID: __________ Date: __________

| Category | Feature | Value |
|----------|---------|-------|
| **ROOT** | root_present | YES / NO |
| | root_type | NONE / SINGLE_TAPROOT / BRANCHING / BULBOUS / FIBROUS |
| | root_color_distinct | YES / NO |
| | root_prominence | SMALL / MEDIUM / LARGE / NA |
| **STEM** | stem_count | 1 / 2 / 3+ |
| | stem_type | STRAIGHT / CURVED / BRANCHING / TWINING |
| | stem_thickness | THIN / MEDIUM / THICK |
| | stem_color_distinct | YES / NO |
| **LEAF** | leaf_present | YES / NO |
| | leaf_count_category | NONE / FEW_1-5 / MEDIUM_6-15 / MANY_16+ |
| | leaf_shape | ROUND / OVAL / LANCEOLATE / LOBED / COMPOUND / SERRATED / NEEDLE / MIXED |
| | leaf_arrangement | ALTERNATE / OPPOSITE / BASAL / WHORLED / SCATTERED / NA |
| | leaf_size_relative | SMALL / MEDIUM / LARGE / MIXED |
| | leaf_color_uniform | YES / NO / NA |
| **FLOWER** | flower_present | YES / NO |
| | flower_count | NONE / 1 / 2-5 / 6+ |
| | flower_position | NONE / TERMINAL / AXILLARY / THROUGHOUT |
| | flower_color_distinct | YES / NO / NA |
| | flower_shape | NONE / SIMPLE / COMPOUND / RADIAL / IRREGULAR |
| **OVERALL** | plant_count | 1 / 2 / 3+ |
| | container_present | YES / NO |
| | plant_symmetry | SYMMETRIC / ASYMMETRIC |
| | overall_complexity | SIMPLE / MODERATE / COMPLEX |
| | identifiable_impression | YES / NO / UNCERTAIN |
| | drawing_completeness | COMPLETE / PARTIAL / FRAGMENTARY |

**Notes:** _______________________________________________________________

---

## 5. Inter-Coder Reliability Protocol

### 5.1 If Two or More Coders Available

**Calibration Phase (5 folios):**
1. Both coders independently code: f38r, f9v, f56r, f3v, f42r
2. Compare coding; calculate agreement per feature
3. Discuss disagreements, clarify decision rules if needed
4. Target: >80% agreement on each feature

**Production Phase (25 remaining folios):**
1. Divide remaining 25 folios equally (or code overlapping subset)
2. Each coder completes their assigned folios
3. For any overlapping folios, resolve disagreements

### 5.2 Agreement Calculation

For each feature, calculate:
- **Percent agreement:** (agreements / total comparisons) × 100
- **Cohen's kappa:** Accounts for chance agreement

Target: Kappa > 0.6 for all features

### 5.3 Resolving Disagreements

1. Review the folio image together
2. Re-read the decision rule
3. If genuinely ambiguous, discuss and record consensus
4. Document any rule clarifications made

---

## 6. Data Entry Format

### 6.1 JSON Output Format

After coding, enter data in this format:

```json
{
  "folio_id": "f38r",
  "coder_id": "coder_1",
  "coding_date": "2025-12-30",
  "root": {
    "root_present": "YES",
    "root_type": "SINGLE_TAPROOT",
    "root_color_distinct": "NO",
    "root_prominence": "MEDIUM"
  },
  "stem": {
    "stem_count": "1",
    "stem_type": "STRAIGHT",
    "stem_thickness": "MEDIUM",
    "stem_color_distinct": "NO"
  },
  "leaf": {
    "leaf_present": "YES",
    "leaf_count_category": "MEDIUM_6-15",
    "leaf_shape": "OVAL",
    "leaf_arrangement": "ALTERNATE",
    "leaf_size_relative": "MEDIUM",
    "leaf_color_uniform": "YES"
  },
  "flower": {
    "flower_present": "NO",
    "flower_count": "NONE",
    "flower_position": "NONE",
    "flower_color_distinct": "NA",
    "flower_shape": "NONE"
  },
  "overall": {
    "plant_count": "1",
    "container_present": "NO",
    "plant_symmetry": "ASYMMETRIC",
    "overall_complexity": "MODERATE",
    "identifiable_impression": "YES",
    "drawing_completeness": "COMPLETE"
  },
  "notes": ""
}
```

### 6.2 File Naming

Save coded data as: `visual_coding_[coder_id]_[date].json`

---

## 7. Analysis Plan (Post-Coding)

Once visual coding is complete, the following analyses will be run:

### 7.1 Feature Distribution

- Frequency of each feature value across 30 folios
- Features with low variance may be excluded from correlation analysis

### 7.2 Text-Visual Correlation

- Chi-square tests for each visual feature × text feature pair
- Cramér's V for effect size
- Bonferroni correction for multiple comparisons

### 7.3 Cluster Analysis

- Cluster folios by visual features (k=3,4,5)
- Cluster folios by text features (k=3,4,5)
- Compare clusters using adjusted Rand index

### 7.4 Null Model Comparison

For each significant correlation:
- Shuffle visual assignments 1000 times
- Real correlation must exceed 99th percentile of null distribution

---

## 8. Pre-Registered Success/Failure Criteria

### SUCCESS Defined As:
- At least **3 visual features** correlate with text features at p < 0.01 (Bonferroni-corrected)
- At least **1 correlation** survives null model comparison (>99th percentile)
- Correlations are **interpretable** (not arbitrary)

### FAILURE Defined As:
- Fewer than 3 significant correlations after correction
- All correlations explained by null model
- No interpretable patterns

### Either Outcome Is Valuable:
- **Success** → Justifies heading-to-plant matching attempts
- **Failure** → Confirms semantic interpretation remains blocked; structural findings become endpoint

---

## 9. Contact and Submission

After completing coding:
1. Review all entries for consistency
2. Export to JSON format
3. Save with coder ID and date
4. Submit for correlation analysis

---

**Document Version:** 1.0
**Created:** 2025-12-30
**Purpose:** Enable rigorous, reproducible visual feature coding for Voynich Manuscript pilot study

# Phase ILL-TOP-1: Illustration-Registry Topology Correspondence

**Phase:** ILL-TOP-1 | **Status:** IN PROGRESS | **Tier:** 3

**Prerequisites:** MAT-PHY-1 (botanical topology match), PIAA (perfumery plant alignment)

---

## Purpose

Test whether the botanical illustrations' **grouping structure** corresponds to Currier A's **MIDDLE incompatibility structure** at the category level - without identifying specific plants.

---

## Core Principle (MANDATORY)

> **This phase compares organizational structures, not identities.**
> No illustration -> specific plant -> specific MIDDLE mapping is allowed.

We are NOT asking: "Which plant is MIDDLE 'a'?"
We ARE asking: "Do illustration groupings reflect the same constraint families as MIDDLE incompatibility clusters?"

---

## The Epistemological Shift

### What We Ruled Out (Tier 1)
- C137: Swap invariance p=1.0 - swapping illustrations doesn't affect grammar
- C138: Illustrations don't constrain execution
- C140: Illustrations are "epiphenomenal" to grammar
- C165: No program-morphology correlation

**Precise claim falsified:** "Text references or depends on illustrations."

### What Was NOT Tested
- Whether illustrations and text **independently index the same domain**
- Whether illustration families correspond to **MIDDLE families** at cluster level
- Whether both reflect the same underlying **material category organization**

### Why This Is Now Legitimate
MAT-PHY-1 showed:
- A's constraint topology matches botanical chemistry (5/5 tests)
- Hub structure matches universal solvent behavior
- Incompatibility density matches real material constraints

PIAA showed:
- 86.7% of illustrated plants are perfumery-aligned
- Illustrations are from the RIGHT DOMAIN

**The honest question is no longer IF they're related, but HOW.**

---

## Four Tests

### Test A: Visual Clustering <-> Incompatibility Clustering (PRIMARY)

**Question:** When illustrations look visually similar, is the constraint space around them similar?

**Pre-registered Clustering Method:**

| Level | Method | Rationale |
|-------|--------|-----------|
| **Primary** | PREFIX-conditioned incompatibility neighborhoods | PREFIX already partitions constraint space (3.2x clustering) |
| **Secondary** | Community detection (Louvain) on compatibility graph | Captures emergent families beyond PREFIX |
| **Tertiary** | Zone-survival profile similarity | Captures AZC filtering effects |

We test at the **PRIMARY level first**. If null, we do NOT mine lower levels.

**Success Criterion:** Significant positive correlation between visual similarity and MIDDLE neighborhood overlap.

---

### Test B: Section-PREFIX Alignment (Asymmetric)

**Question:** Are illustration section boundaries better predicted by PREFIX distributions than by chance, controlling for section size?

**Method:** Permutation test with 10,000 shuffles against null model.

**Success Criterion:** Observed alignment significantly exceeds null (p < 0.05).

---

### Test C: Schematic-Hub Correlation

**Question:** Do illustrations with low morphological specificity correlate with hub-MIDDLE usage?

**Definition of "Schematic" (Internal Visual Features Only):**

| Feature | Schematic | Specific |
|---------|-----------|----------|
| Morphological detail | LOW | HIGH |
| Plant symmetry | SYMMETRIC | ASYMMETRIC |
| `identifiable_impression` | NO | YES |

**Success Criterion:** Significant positive correlation between schematic score and hub density.

---

### Test D: Mismatch as Evidence (Pre-registered Falsification)

**Question:** If visually dissimilar plants map to similar constraint regimes, does this support regime-level interpretation over identity-level interpretation?

**Pre-registered Prediction:**

| Observation | Identity Model | Regime Model |
|-------------|----------------|--------------|
| Similar images -> similar constraints | SUPPORTS | SUPPORTS |
| Dissimilar images -> similar constraints (in hub zones) | FALSIFIES | SUPPORTS |
| Similar images -> dissimilar constraints | AMBIGUOUS | SUPPORTS |

**Success Criterion:** Dissimilar-but-compatible pairs exist AND concentrate in hub regions.

---

## Success Criteria

| Test | Question | Success Criterion | Failure Mode |
|------|----------|-------------------|--------------|
| A | Visual similarity <-> constraint space similarity | Mantel r > 0, p < 0.05 | No correlation |
| B | Section-PREFIX alignment vs null | Alignment > null (p < 0.05) | Alignment <= null |
| C | Schematic illustrations <-> hub density | Positive correlation | No correlation |
| D | Dissimilar-but-compatible -> hub regions | Concentration in hubs | Uniform distribution |

**Interpretation Matrix:**

| A | B | C | D | Verdict |
|---|---|---|---|---------|
| Y | Y | Y | Y | **STRONG MATCH** - Parallel indexing confirmed |
| Y | Y | Y | N | **PARTIAL** - Parallel indexing, but identity-level not ruled out |
| Y | Y | N | Y | **PARTIAL** - Structural parallel, hub interpretation unclear |
| Y | N | N | N | **WEAK** - Only primary test passes |
| N | * | * | * | **MISMATCH** - Primary test failed, parallel indexing falsified |

**Critical:** If Test A fails, the phase concludes with MISMATCH regardless of other tests.

---

## Data Sources

### Visual Analysis Data
- `phases/VIS_visual_analysis/visual_coding_complete.json` - Feature coding per folio
- `phases/ANN_annotation_analysis/h3_2_visual_neighborhoods.json` - 10 visual clusters, 29 folios

### MIDDLE Incompatibility Data
- `phases/SSD_PHY_1a/topology_fingerprint.md` - Full topology analysis
- Hub MIDDLEs: 'a', 'o', 'e', 'ee', 'eo'
- 95.7% incompatibility, 3.2x within-PREFIX clustering

---

## Why A Positive Result != Decoding

Even if all four tests pass with STRONG MATCH, this phase establishes:

| Established | NOT Established |
|-------------|-----------------|
| Illustrations and text index the same domain | Which plant is which token |
| Organizational structure is parallel | Any semantic content |
| Visual families reflect constraint families | Translation pathway |
| Hub regions show category-neutral behavior | Identity-level mapping |

---

## Phase Status

**ILL-TOP-1 is the FINAL INTERNAL EXPLORATORY PHASE.**

After this phase, internal investigation is COMPLETE.

---

> *This phase compares organizational structures, not identities. It tests whether illustration groupings correspond to MIDDLE incompatibility clusters at the category level - without identifying which plant corresponds to which token. No identity-level claims are made. All findings are Tier 3.*

---

*Phase specification: 2026-01-13*

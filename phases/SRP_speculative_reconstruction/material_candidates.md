# Material Candidates

> **PURPOSE**: Map abstract material classes to real medieval materials that could plausibly be processed by the locked grammar.

> **STATUS**: EXPLICITLY SPECULATIVE AND NON-BINDING

---

## Locked Material Class Definitions

From Lane 3 analysis:

| Class | Physical Traits | Grammar Status |
|-------|-----------------|----------------|
| CLASS_A | High porosity, slow diffusion, swelling | COMPATIBLE (0% failure) |
| CLASS_B | Low porosity, hydrophobic, minimal swelling | COMPATIBLE (0% failure) |
| CLASS_C | Phase-change prone, emulsion-forming | INCOMPATIBLE (19.8% failure) |
| CLASS_D | Non-swelling, rapid diffusion, stable | COMPATIBLE (0% failure) |
| CLASS_E | Homogeneous fluid, no solid interactions | COMPATIBLE (0% failure) |

---

## CLASS_A: Porous, Swelling Plant Matter

**Physical Profile**: High porosity, slow diffusion, swells when wetted

**STRUCTURAL SUPPORT**: Grammar tolerates these completely (0% failure). LINK operator allows time for slow diffusion.

### Candidate Materials (MEDIUM confidence)

| Material | Properties | Historical Use | Grammar Fit |
|----------|------------|----------------|-------------|
| **Dried leaves** | Highly porous, absorbs liquid, swells | Medicinal teas, infusions | STRONG |
| **Dried flowers** | Delicate, porous, expands in liquid | Aromatic waters, cosmetics | STRONG |
| **Crushed roots** | Fibrous, slow diffusion, swells | Medicinal extracts | STRONG |
| **Dried bark fragments** | Porous, slow release, gradual swelling | Tanning, dyeing, medicine | STRONG |
| **Sponge-like plant tissue** | Maximum porosity, slow equilibration | Various preparations | MODERATE |

### Why These Fit

- **LINK-heavy programs** make sense: Material needs time to swell, release components
- **Slow diffusion** means waiting is productive, not wasted
- **No phase instability**: Swelling is gradual, not catastrophic
- **Conservative programs** appropriate: Gentle handling prevents damage

### Medieval Context (HISTORICAL ALIGNMENT)

These materials were central to:
- **Apothecary practice**: Dried herbs, flowers, roots
- **Distillation manuals** (Brunschwig): Plant material preparation
- **Monastic medicine**: Herbal preparations

---

## CLASS_B: Dense, Hydrophobic Material

**Physical Profile**: Low porosity, resists wetting, minimal swelling

**STRUCTURAL SUPPORT**: Grammar tolerates completely (0% failure). AGGRESSIVE programs may be needed for resistant materials.

### Candidate Materials (MEDIUM confidence)

| Material | Properties | Historical Use | Grammar Fit |
|----------|------------|----------------|-------------|
| **Resinous plant parts** | Hydrophobic, slow release, dense | Incense, varnish, medicine | STRONG |
| **Seeds with oily coating** | Resistant to water, slow extraction | Oils, ointments | STRONG |
| **Waxy plant surfaces** | Hydrophobic, need aggressive treatment | Specialty extracts | MODERATE |
| **Dense woody material** | Low porosity, needs time | Structural extracts | MODERATE |
| **Dried citrus peel** | Oily, resistant, aromatic | Perfumery, medicine | STRONG |

### Why These Fit

- **AGGRESSIVE programs** make sense: Dense material needs pushing
- **Low LINK** in some programs: Material doesn't absorb—waiting less useful
- **High hazard density** tolerable: Material is stable under stress
- **Extended programs** needed: Extraction from dense material takes time

### Medieval Context (HISTORICAL ALIGNMENT)

These materials required specialized processing:
- **Resin collection**: Frankincense, myrrh, mastic
- **Seed pressing**: Almond, poppy, flax
- **Citrus processing**: Orange flower water (medieval perfumery)

---

## CLASS_C: Phase-Unstable Materials (INCOMPATIBLE)

**Physical Profile**: Phase-change prone, emulsion-forming

**STRUCTURAL SUPPORT**: Grammar FAILS on these (19.8% failure, 100% PHASE_COLLAPSE mode).

### What This EXCLUDES (MEDIUM-HIGH confidence)

| Material | Why Incompatible | Grammar Evidence |
|----------|------------------|------------------|
| **Fresh plant tissue** | High water content, can freeze/steam | PHASE_COLLAPSE |
| **Fats and oils near solidification** | Phase boundaries unstable | PHASE_COLLAPSE |
| **Emulsion-prone mixtures** | Two-phase instability | PHASE_COLLAPSE |
| **Materials near boiling** | Vapor/liquid transition | PHASE_COLLAPSE |
| **Mucilaginous substances** | Gel formation possible | PHASE_COLLAPSE |
| **Watery slurries** | Can separate or foam | PHASE_COLLAPSE |

### What This Means (HISTORICAL ALIGNMENT)

The grammar is NOT designed for:
- **Distillation to completion** (phase change required)
- **Butter/fat processing** (solidification risk)
- **Soap making** (emulsion formation)
- **Fresh herb processing** (water phase instability)

The system processes **already-dried or already-stable** materials.

---

## CLASS_D: Stable, Rapid-Diffusion Materials

**Physical Profile**: Non-swelling, rapid diffusion, stable phase

**STRUCTURAL SUPPORT**: Grammar works perfectly (0% failure). Best match for circulatory reflux apparatus (100% structural homology).

### Candidate Materials (HIGH confidence for class, MEDIUM for specific)

| Material | Properties | Historical Use | Grammar Fit |
|----------|------------|----------------|-------------|
| **Alcohol/water mixtures** | Stable, good diffusion, no phase issues | Distillation, extraction | STRONG |
| **Dilute aqueous extracts** | Homogeneous, no phase instability | Medicinal waters | STRONG |
| **Pre-infused liquids** | Already stable, rapid equilibration | Secondary processing | STRONG |
| **Light essential oils** | Stable liquid phase, miscible | Aromatic preparations | STRONG |
| **Clear filtrates** | Particulate-free, stable | Finished products | STRONG |

### Why These Fit

- **TEMPLATE_C programs** (equilibrium-seeking): Perfect for stable fluids
- **High LINK effectiveness** in closed loops: Circulation works optimally
- **100% convergence**: Stable materials reach stable endpoints
- **Any stability level** works: Material can handle aggressive programs

### Medieval Context (HISTORICAL ALIGNMENT)

CLASS_D materials match:
- **Aqua vitae** (distilled alcohol): Stable, well-diffusing
- **Simple waters** (hydrolats): After distillation, stable
- **Rectification** (re-distillation): Processing stable product

---

## CLASS_E: Pure Homogeneous Fluids

**Physical Profile**: No solid interactions, fully homogeneous

**STRUCTURAL SUPPORT**: Grammar works perfectly (0% failure).

### Candidate Materials (MEDIUM confidence)

| Material | Properties | Historical Use | Grammar Fit |
|----------|------------|----------------|-------------|
| **Distilled water** | Pure, no solids | Carrier, solvent | STRONG |
| **Pure alcohol** | Homogeneous, stable | Extraction solvent | STRONG |
| **Clarified wines** | Filtered, stable | Base for preparations | MODERATE |
| **Clear vinegars** | Acidic but stable | Extraction medium | MODERATE |
| **Rose water (finished)** | Pure aromatic water | Cosmetic, medicinal | STRONG |

### Why These Fit

- No particle-carrier interactions to manage
- Pure circulation with no clogging risk
- Grammar's LINK has nothing to wait for—but still works
- May represent **carrier fluids** rather than substrates

### Medieval Context (HISTORICAL ALIGNMENT)

Pure fluids were essential for:
- **Carrier media**: What the apparatus circulates
- **Extraction solvents**: Drawing out plant components
- **Finished products**: Ready for use or sale

---

## Material Selection Hypothesis

**PURE SPECULATION** (LOW confidence):

Based on grammar compatibility patterns, a workshop using this manual would likely process:

### Primary Substrates
1. **Dried plant material** (CLASS_A): Leaves, flowers, roots, bark
2. **Dense/resinous parts** (CLASS_B): Seeds, resins, citrus peel
3. **Pre-stabilized extracts** (CLASS_D): Previously processed material

### Processing Medium
4. **Alcohol-water mixtures** (CLASS_D/E): Stable carrier fluid
5. **Pure water** (CLASS_E): Alternative carrier

### Explicitly Avoided
6. **Fresh plant material** (CLASS_C): Too much water, phase unstable
7. **Fatty/waxy materials at transition** (CLASS_C): Phase boundary danger
8. **Emulsion-forming mixtures** (CLASS_C): Two-phase instability

---

## Historical Alignment Summary

| Material Type | Grammar Fit | Medieval Use | Confidence |
|---------------|-------------|--------------|------------|
| Dried herbs/flowers | COMPATIBLE | Apothecary staple | MEDIUM |
| Dried roots/bark | COMPATIBLE | Medicinal preparations | MEDIUM |
| Resins | COMPATIBLE | Incense, varnish, medicine | MEDIUM |
| Aromatic seeds | COMPATIBLE | Oils, perfumery | MEDIUM |
| Alcohol/water | COMPATIBLE | Extraction medium | HIGH |
| Fresh plant material | INCOMPATIBLE | Needs different apparatus | MEDIUM |
| Fats/oils | INCOMPATIBLE | Wrong process type | MEDIUM |
| Emulsions | INCOMPATIBLE | Grammar cannot stabilize | HIGH |

---

## What Phase Instability Means Practically

**STRUCTURAL SUPPORT** + **HISTORICAL ALIGNMENT**:

The exclusive failure mode of CLASS_C materials (PHASE_COLLAPSE) suggests the apparatus operates in a regime where:

1. **Temperature is controlled but not precisely** — Materials that could suddenly boil or freeze are dangerous
2. **Separation is not desired** — Emulsions that split defeat the purpose
3. **Dried materials preferred** — Fresh material has too much unstable water

**Workshop Interpretation** (PURE SPECULATION):

> *"Dry your material first. If it's still wet, or if it might foam or separate, don't put it in the apparatus. Use the right starting material."*

This matches **Brunschwig's advice** (1500): Prepare material properly before processing.

---

## What This Does NOT Claim

- ❌ Specific plants or species used
- ❌ Exact preparation methods
- ❌ Geographic origin of materials
- ❌ Commercial vs. personal use
- ❌ Token meanings

---

*Speculation complete. See `illustration_alignment.md` for visual memory aid hypotheses.*

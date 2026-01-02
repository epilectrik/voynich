# Product Convergence Ranking

> **PURPOSE**: Rank candidate products by structural convergence with locked grammar constraints.

> **METHOD**: Multi-axis scoring with fatal failure detection and residual tension analysis.

---

## Final Ranking

| Rank | Product Class | Score | Confidence | Status |
|------|---------------|-------|------------|--------|
| **1** | Aromatic Waters | **19/21** (90.5%) | HIGH | **PRIMARY CANDIDATE** |
| **2** | Medicinal Herb Infusions | **18/21** (85.7%) | MEDIUM-HIGH | Strong alternative |
| **3** | Resin Extracts | **16/21** (76.2%) | MEDIUM | Viable subset |
| 4 | Ritual Substances | 14/21 (66.7%) | LOW-MEDIUM | Possible specialty |
| 4 | Pharmaceutical Concentrates | 14/21 (66.7%) | LOW | Process tension |
| 6 | Food Flavoring | 13/21 (61.9%) | LOW | Weak justification |
| 7 | Cosmetics | 12/21 (57.1%) | VERY LOW | CLASS_C fatal |
| — | Industrial Solvents | 5/21 | ELIMINATED | No complexity justification |
| — | Fermented Products | — | ELIMINATED | Batch + phase change |
| — | Distilled Spirits | — | ELIMINATED | Phase change required |

---

## Hard Eliminations (Fatal Failures)

### 1. Distilled Spirits
**Failure**: Phase change fundamentally required
- Grammar: CLASS_C materials cause 100% PHASE_COLLAPSE
- Distillation requires vapor→liquid transition
- No amount of reinterpretation can resolve this

### 2. Fermented Products
**Failure**: Batch process with biological phase change
- Fermentation is inherently discrete-batch
- Grammar assumes continuous indefinite operation
- Microbial growth = phase-unstable system

### 3. Industrial Solvents
**Failure**: No justification for control complexity
- Solvents are forgiving materials
- 17 forbidden transitions make no sense
- 83 programs vastly exceed need

---

## Convergence Analysis: Top 3 Candidates

### Candidate #1: AROMATIC WATERS

**Overall Score**: 19/21 (90.5%)

**Strongest Alignments**:
| Axis | Score | Why Exceptionally Strong |
|------|-------|-------------------------|
| Process (A1) | 3 | Pelican alembic = designed for this; phase stability critical |
| Material (A3) | 3 | Dried flowers/petals = perfect CLASS_A match |
| Economic (A4) | 3 | Rose water = major luxury commodity 1400-1450 |
| Frequency (A5) | 3 | Seasonal production; substrate variety justifies 83 programs |
| Outcome (A6) | 3 | Pure olfactory/visual judgment; no objective endpoint |

**Residual Tensions**:
- A2 (Control) = 2: Failure is quality loss, not catastrophe
- A7 (Documentation) = 2: Some formulas were published (Brunschwig)

**Key Insight**: The 83-program question resolves naturally. Rose water made from:
- Spanish roses vs. Persian roses vs. Provençal roses
- Early bloom vs. late bloom
- Fresh-dried vs. aged-dried
- Intense extraction vs. delicate extraction

Each combination = different program. 83 is plausible, not excessive.

---

### Candidate #2: MEDICINAL HERB INFUSIONS

**Overall Score**: 18/21 (85.7%)

**Strongest Alignments**:
| Axis | Score | Why Strong |
|------|-------|-----------|
| Process (A1) | 3 | Circulation extracts compounds; phase stability preserves therapeutics |
| Control (A2) | 3 | Medical stakes justify complexity; degradation = harm |
| Material (A3) | 3 | Dried herbs = CLASS_A; many species, conditions |
| Economic (A4) | 3 | Medicine always high-value; guild protection |

**Residual Tensions**:
- A5 (Frequency) = 2: 83 programs seems high for herbal waters alone
- A6 (Outcome) = 2: Potency harder to assess than fragrance
- Missing dosage/ingredient information contradicts medicinal purpose

**Key Insight**: Strong alternative, but the "pure operational" verdict (0 identifier tokens) is in tension with medicinal use. Medicines typically require some product specification.

**Resolution Possibility**: The book handles *apparatus operation*, not *recipe selection*. Operator brings material knowledge externally.

---

### Candidate #3: RESIN EXTRACTS

**Overall Score**: 16/21 (76.2%)

**Strongest Alignments**:
| Axis | Score | Why Strong |
|------|-------|-----------|
| Process (A1) | 3 | Dense materials need extended circulation; solidification = failure |
| Material (A3) | 3 | Perfect CLASS_B match (hydrophobic, slow diffusion) |
| Outcome (A6) | 3 | Pure sensory judgment |

**Residual Tensions**:
- A5 (Frequency) = 1: **WEAK** — Far fewer resin types than 83 programs
- A4 (Economic) = 2: Specialty market, not mass commerce

**Key Insight**: Resin extraction is a plausible *subset* of the book's use, not its primary purpose. AGGRESSIVE programs match CLASS_B handling needs.

**Resolution Possibility**: The book covers multiple product classes, with resins using the AGGRESSIVE program subset while aromatics use CONSERVATIVE/MODERATE.

---

## Multi-Product Hypothesis

The data support a **multi-product workshop** interpretation:

| Product Type | Programs Used | Material Class | Program Style |
|--------------|---------------|----------------|---------------|
| Aromatic waters | CONSERVATIVE, MODERATE | CLASS_A | High LINK, gentle |
| Medicinal waters | MODERATE | CLASS_A | Balanced |
| Resin extracts | AGGRESSIVE | CLASS_B | Low LINK, pushing |
| Stabilization/finishing | ULTRA_CONSERVATIVE | CLASS_D | Pure equilibration |

This explains:
- Why 83 programs (product × substrate × intensity combinations)
- Why AGGRESSIVE programs exist (CLASS_B materials need them)
- Why ULTRA_CONSERVATIVE programs exist (finishing/stabilization)
- Why the book has no product identifiers (operator knows what they're making)

---

## Confidence Assessment

| Claim | Confidence | Basis |
|-------|------------|-------|
| Primary product = aromatic waters | **HIGH** | 90.5% multi-axis convergence |
| Secondary products include medicinal waters | **MEDIUM-HIGH** | 85.7% convergence; minor tensions |
| Resin extracts = specialty subset | **MEDIUM** | Explains AGGRESSIVE programs |
| Multi-product workshop interpretation | **MEDIUM-HIGH** | Best explains 83-program diversity |
| Distilled spirits RULED OUT | **HIGH** | Phase change fatal |
| Cosmetics RULED OUT | **MEDIUM-HIGH** | CLASS_C emulsion problem |

---

## What Would Change This Ranking

| If This Were True | Ranking Would Change To |
|-------------------|------------------------|
| Grammar tolerates phase changes | Distilled spirits re-enters (#1-2) |
| Fewer than 83 programs actually used | Resin extracts rises |
| Dosage tokens discovered | Medicinal waters rises to #1 |
| Emulsion compatibility found | Cosmetics re-enters |
| Illustrations encode specific plants | All rankings would need revision |

None of these conditions are supported by the locked model.

---

## Verdict

**Aromatic waters** is the product class with highest structural convergence to the Voynich control grammar.

The data support a **multi-product aromatic workshop** interpretation:
- Primary: Aromatic waters (rose, lavender, orange flower, etc.)
- Secondary: Medicinal herbal waters
- Specialty: Resin extracts (using AGGRESSIVE programs)
- Auxiliary: Stabilization/maturation (using ULTRA_CONSERVATIVE programs)

This interpretation explains:
- The 83-program library (substrate × intensity combinations)
- The absence of product identifiers (expert knows what they're making)
- The program style distribution (CONSERVATIVE dominance + AGGRESSIVE subset)
- The illustration abstraction (category markers, not species identification)
- The external endpoint judgment (operator assesses fragrance/quality)

---

*See `sensitivity_analysis.md` for robustness testing and `top_candidate_rationale.md` for "Why This Book?" analysis.*

# AX_FUNCTIONAL_ANATOMY Phase

## Purpose

Investigate what AUXILIARY (AX) tokens functionally ARE by tracing AX vocabulary through the A->AZC->B pipeline. Test whether AX is an independent functional component or an emergent morphological consequence of the pipeline.

## Status: CLOSED

Phase complete. 5 constraints documented (C567-C571). AX is not an independent functional component -- it is the PREFIX-determined default mode of the same vocabulary used by operational roles. PREFIX is the role selector; MIDDLE is the material carrier.

## Research Questions

| Question | Script | Status | Finding | Constraint |
|----------|--------|--------|---------|------------|
| Q1: AX MIDDLE inventory | ax_middle_inventory.py | **DOCUMENTED** | 57 MIDDLEs, 98.2% PP, 72% shared with operational | C567 |
| Q2: A-record coverage | ax_a_record_trace.py | **DOCUMENTED** | 97.2% of A records carry AX vocabulary | C568 |
| Q3: Vocabulary overlap | ax_vocabulary_overlap.py | **DOCUMENTED** | 72% shared with operational, PREFIX-differentiated | C567, C570 |
| Q4: Byproduct test | ax_byproduct_test.py | **DOCUMENTED** | R²=0.83, fraction matches but composition varies | C569 |
| Q5: Necessity test | ax_necessity_test.py | **DOCUMENTED** | Always present (0 zero-AX records), classes 21/22 universal | C568 |
| Q6: Prefix derivation | ax_prefix_derivation_test.py | **DOCUMENTED** | 89.6% accuracy, PREFIX is role selector | C570 |

## Key Finding: PREFIX as Role Selector

AX is NOT a separate vocabulary or independent function. AX tokens use the SAME MIDDLEs as operational roles (EN, CC, FL, FQ), differentiated by PREFIX:

| PREFIX | Role Assignment | Example (MIDDLE="edy") |
|--------|----------------|----------------------|
| ch, sh | ENERGY_OPERATOR | chedy, shedy |
| qo | ENERGY_OPERATOR | - |
| ok, ot | AUXILIARY (AX_MED) | okedy, otedy |
| Articulated (y, d, l, k, p, f, r, t) + ch/sh | AUXILIARY (AX_INIT) | ychedy, dchedy, lchedy |
| bare (no prefix) | AUXILIARY (AX_FINAL) | dy, d, s, y |
| da | FLOW/CC | daiin |

**Interpretation:** The MIDDLE is the material carrier (from the pipeline). The PREFIX decides how to deploy it:
- Operational prefixes (ch/sh/qo) = "process this material"
- Scaffold prefixes (ok/ot) = "stage this material"
- Bare form = "material is ready / frame closed"
- Articulated operational = "frame opened with this material"

## Documented Findings

### C567: AX-Operational MIDDLE Sharing (Tier 2)
- 57 unique AX MIDDLEs; 56 PP (98.2%), 1 RI, 0 B-exclusive
- 41/57 (71.9%) shared with operational roles
- Highest overlap: AX-EN Jaccard = 0.400 (36 shared MIDDLEs)
- 16 AX-exclusive MIDDLEs (28.1%), mostly: a, h, ai, aii, cho, cph, do, g, ho, hy, lo, op, opc, opch, yt, c
- 78% of shared MIDDLEs are differentiated by PREFIX + ARTICULATOR

### C568: AX Pipeline Ubiquity (Tier 2)
- 97.2% of A records carry at least 1 AX PP MIDDLE
- Mean 3.7 AX MIDDLEs per A record (median 4)
- Top AX MIDDLEs are universal single-character forms: o (60%), i (39%), e (34%), a (27%), y (24%)
- 44 records (2.8%) have zero AX MIDDLEs -- all have <=4 total MIDDLEs (tiny records)
- 0 B contexts have zero AX classes (classes 21, 22 always survive)
- AX_FINAL always present (100%), AX_INIT 95.9%, AX_MED 97.0%, all three 95.6%

### C569: AX Proportional Scaling (Tier 2)
- AX fraction per record = 0.4540, expected = 0.4545 (deviation = -0.0005)
- Linear model: AX = 0.4246 * total + 0.96, R² = 0.8299
- AX is NOT pure byproduct (R² < 0.9) but scales proportionally on average
- Subgroup asymmetry: AX_INIT over-represented (slope 0.130 vs expected 0.102), AX_FINAL under-represented (slope 0.093 vs expected 0.122)
- Interpretation: AX volume is proportional to pipeline throughput, but AX composition has independent structure

### C570: AX PREFIX Derivability (Tier 2)
- PREFIX alone predicts AX vs non-AX with 89.6% binary accuracy
- 22 AX-exclusive prefixes (ct, dch, do, fch, ka, kch, ke, ko, lch, lk, lsh, or, pch, po, rch, sa, so, ta, tch, te, to, yk)
- 3 non-AX-exclusive prefixes (al, ar, qo)
- 7 ambiguous prefixes (NONE, ch, da, ok, ol, ot, sh)
- Main violations: AX_INIT tokens with ch/sh prefixes (articulated variants)
- F1 score: 0.904 (precision 0.867, recall 0.944)

### C571: AX Functional Identity Resolution (Tier 2)
- AX is the PREFIX-determined default deployment mode of pipeline vocabulary
- Same MIDDLEs serve as scaffolding (AX) or operations (EN/CC/FL/FQ) depending on PREFIX
- PREFIX = role selector; MIDDLE = material carrier
- AX is not independent of the pipeline -- it IS the pipeline vocabulary in scaffold mode
- The 16 AX-exclusive MIDDLEs (28%) provide the only truly AX-specific vocabulary
- AX is structurally guaranteed: always at least 2 classes (21, 22) survive

## Scripts

| Script | Status | Output |
|--------|--------|--------|
| ax_middle_inventory.py | **C567** | ax_middle_inventory.json |
| ax_a_record_trace.py | **C568** | ax_a_record_trace.json |
| ax_vocabulary_overlap.py | **C567, C570** | ax_vocabulary_overlap.json |
| ax_byproduct_test.py | **C569** | ax_byproduct_test.json |
| ax_necessity_test.py | **C568** | ax_necessity_test.json |
| ax_prefix_derivation_test.py | **C570** | ax_prefix_derivation_test.json |

## Dependencies

- AUXILIARY_STRATIFICATION (C563-C566): positional sub-structure
- CLASS_COSURVIVAL_TEST: survivor sets and class token map
- A_INTERNAL_STRATIFICATION: RI/PP MIDDLE classification

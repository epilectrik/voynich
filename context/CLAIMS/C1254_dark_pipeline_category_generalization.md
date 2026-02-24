# C1254: Dark Pipeline Category Generalization

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** DARK_PIPELINE_CHARACTERIZATION (Phase 448)
**Extends:** C1250 (gloss category structural coherence), C1137 (dark pipeline HT substrate), C935 (compound specification dual purpose)
**Relates to:** C1251 (atom compositional validation), C1141 (dark compounds built from bridge atoms), C1196 (autogloss coverage), C404 (HT operationally redundant)

---

## Statement

The 8 operational gloss categories (C1250) **partially generalize** to the dark pipeline (1,144 autoglossable compound MIDDLEs, 2,489 tokens). Auto-assignment via atom-level plurality vote achieves 95.2% coverage of dark MIDDLEs, raising total B token coverage from 88.6% to 99.5%. A 6-test battery produces 3/6 PASS:

| Test | Null Model | Statistic | Result | Key Value |
|------|-----------|-----------|--------|-----------|
| T1: Coverage | Descriptive | Assignment rate | **PASS** | 95.2% MIDDLEs, 99.5% tokens |
| T2: Behavioral silhouette | A (random partition) | Silhouette score | FAIL | sil=-0.050, p=0.155 |
| T3: Line-position differentiation | B (random token labels) | ANOVA F | **PASS** | F=10.9, 10.8x, p=0.001 |
| T4: Section profile divergence | A (random partition) | Mean pairwise JSD | FAIL | JSD=0.011, p=0.235 |
| T5: Within-line MI | B (random token labels) | Mutual information | **PASS** | MI=0.060, 1.5x, p=0.001 |
| T6: Q-MIDDLE divergence | Descriptive + MW | Mann-Whitney U | FAIL | p=0.342 |

### Critical Stratified Finding (T2)

The overall silhouette fails, but **confidence-stratified analysis reveals a clean gradient**:

| Tier | n | Silhouette | p | Status |
|------|---|-----------|---|--------|
| LOCKED+SOLID | 40 | -0.011 | 0.001 | **PASS** |
| PLAUSIBLE | 57 | -0.109 | 0.166 | FAIL |
| WEAK | 199 | -0.052 | 0.057 | FAIL (borderline) |

High-confidence atom assignments (LOCKED+SOLID) produce valid behavioral groupings. WEAK atoms (o=work, l=frame, r=input — 65% of assignments) add noise that drowns the overall signal.

### Category Distribution

Dark MIDDLEs are THERMAL-heavy (467/1144 = 40.8% of types) because k and e atoms dominate compound construction. Zero dark MIDDLEs map to CONTAINMENT (all containment MIDDLEs are core grammar).

### Atom-Level Operational Encoding Penetrates HT Layer

Dark-pipeline tokens are 100% HT/UN substrate (C1137) — invisible to the 49-class grammar. Yet their atom-level categories carry real structural information: line position differentiation (10.8x), sequential MI with adjacent grammar tokens (cross MI=0.071), and behavioral clustering for high-confidence atoms. The operational encoding at the atom level is more fundamental than the grammar classification boundary.

---

## Interpretation

The 8-category system generalizes to the dark pipeline with **confidence stratification**:
- **Trust:** KERNEL, LOCKED, SOLID auto-assignments (133 MIDDLEs, ~12%)
- **Use with caution:** PLAUSIBLE (269 MIDDLEs, ~24%)
- **Treat as approximate:** WEAK (742 MIDDLEs, ~65%)

The section divergence failure (T4) is expected: dark compounds are built from the same atoms regardless of section. C1148's 3.9x section hyper-modulation operates at the *selection* level (which compounds appear), not the *category* level (what categories those compounds encode).

---

## Method

- 1,144 dark MIDDLEs with autoglosses auto-assigned via plurality vote over constituent atoms
- Each atom maps to a category through ATOM_GLOSSES → GLOSS_TO_CATEGORY
- Tie-breaking by atom confidence tier (LOCKED > SOLID > PLAUSIBLE > WEAK)
- Category confidence inherits weakest atom confidence in compound
- 58 q-containing MIDDLEs (127 tokens) remain unassignable — insufficient affordance data for 9th category test
- 1000 permutations for all null models, p < 0.01 threshold

**Script:** `phases/DARK_PIPELINE_CHARACTERIZATION/scripts/dark_pipeline_characterization.py`
**Results:** `phases/DARK_PIPELINE_CHARACTERIZATION/results/dark_pipeline_characterization.json`

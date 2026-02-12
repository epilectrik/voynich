# C974: Suffix-Role Binding Structural Not Random

**Tier:** 2 | **Scope:** B | **Phase:** FINGERPRINT_UNIQUENESS

## Statement

The strong association between suffix presence and role (chi2 = 3872.2) is destroyed by random class reassignment (null chi2 ~ 390, p = 0.000), confirming that suffix-role binding reflects genuine class-level structure, not frequency artifacts.

## Evidence

- Observed suffix-role profile:
  - CC: 100.0% suffix-less, 0 suffix types (735 tokens)
  - FQ: 93.4% suffix-less, 1 suffix type (2,890 tokens)
  - FL: 93.8% suffix-less, 2 suffix types (1,078 tokens)
  - AX: 69.3% suffix-less, 19 suffix types (4,140 tokens)
  - EN: 39.0% suffix-less, 17 suffix types (7,211 tokens)
- chi2 = 3872.2 (contingency test, suffix presence vs role)

| Ensemble | null chi2 mean | p(chi2 >= 3872) |
|----------|---------------|-----------------|
| NULL-G (token shuffle) | 3872.2 | 1.000 |
| NULL-H (class reassign) | 390.0 | 0.000 |
| NULL-I (latent, all d) | 3872.2 | 1.000 |

## Interpretation

Token shuffle preserves role assignments (and thus suffix-role binding) — hence p = 1.0. Class reassignment randomizes which tokens belong to which role — and chi2 drops 10x, from 3872 to 390. This proves the binding is a property of the class structure itself, not of individual token frequencies.

CC's 100% suffix-less status and EN's 17 suffix types with only 39% suffix-less are structural signatures of the role taxonomy.

## Provenance

- Confirms: C588 (suffix role selectivity, chi2 = 5063.2 at full scope)
- Method: `phases/FINGERPRINT_UNIQUENESS/scripts/t3_compositional_sparsity.py`
- Results: `phases/FINGERPRINT_UNIQUENESS/results/t3_composition.json`

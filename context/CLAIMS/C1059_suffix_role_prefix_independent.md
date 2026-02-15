# C1059: Suffix Carries Role Information Independent of PREFIX

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_DEEP_STRUCTURE (Phase 379)
**Extends:** C588 (role-suffix distributions), C556 (PREFIX determines role), C378 (PREFIX constrains suffix)
**Relates to:** C1058 (suffix sequential grammar genuine)

---

## Statement

Suffix carries **independent** role information beyond what PREFIX determines. Conditioning on PREFIX does not mediate the role-suffix association — it **strengthens** it:

| Measure | Value |
|---------|-------|
| V_raw (role × suffix) | 0.2869 |
| V_conditioned (weighted average within PREFIX) | **0.3750** |
| Mediation fraction | **-30.7%** (anti-mediation) |
| n classified tokens | 16,054 |

Per-PREFIX role-suffix V (n >= 30):

| PREFIX | V | n | Interpretation |
|--------|---|---|----------------|
| ol | 0.663 | 475 | Very strong within-PREFIX role-suffix signal |
| ok | 0.655 | 1185 | Very strong |
| da | 0.611 | 900 | Strong |
| ot | 0.532 | 1137 | Strong |
| _BARE_ | 0.436 | 2715 | Moderate |
| ch | 0.129 | 2510 | Weak but present |
| sh | 0.120 | 1595 | Weak but present |

Even within a single PREFIX (e.g., all ok-prefixed tokens), suffix still strongly predicts role (V=0.655). This means PREFIX and suffix **jointly but independently** encode role information.

---

## Interpretation

C556 established that PREFIX determines role, and C378 showed PREFIX constrains suffix (chi²=7053). The naive expectation was that suffix's role association (C588: chi²=5063) is merely a byproduct: PREFIX→role and PREFIX→suffix, so suffix correlates with role only through PREFIX.

This test falsifies that hypothesis decisively. The role-suffix V *increases* by 30.7% after PREFIX conditioning, meaning PREFIX acts as a **confounder that masks** the suffix-role signal rather than creating it. Within PREFIX groups, suffix-role association is actually stronger than the marginal.

The strongest within-PREFIX signals (ol, ok, da, ot) are all QO-family prefixes. These PREFIX groups contain multiple roles (EN, AX, FQ) distinguished almost entirely by suffix choice. The ch/sh prefixes show weaker but still nonzero within-PREFIX V (0.12-0.13), indicating even sister-pair prefixes use suffix to differentiate roles.

This establishes a three-layer role encoding: PREFIX (primary), suffix (independent secondary), and their joint combination.

---

## Method

- 16,054 classified Currier B tokens (49-class taxonomy with role assignment)
- V_raw: Cramér's V for full role × suffix contingency table
- V_conditioned: For each PREFIX with 2+ roles and 2+ suffixes present, compute within-PREFIX role × suffix V. Weighted average by PREFIX token count.
- Mediation fraction: (V_raw - V_conditioned) / V_raw
- PREFIX groups with only 1 role or 1 suffix (unable to compute V) are reported as skip=true

**Script:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py`
**Results:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t2_role_suffix_signatures.json`

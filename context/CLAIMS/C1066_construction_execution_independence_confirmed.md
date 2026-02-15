# C1066: Construction-Execution Independence Confirmed at Token Level

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE (Phase 380)
**Extends:** C522 (construction-execution independence, r=-0.21 NS at type-level)
**Relates to:** C1060 (atom position grammar), C1001 (PREFIX line-position R²=0.069), C873 (kernel positional ordering)

---

## Statement

Atom string position within compound MIDDLEs has **zero correlation** with token line position (rho=-0.004, p=0.65, n=11,525 observations). This holds within every PREFIX group tested (19 groups with n >= 50, all |rho| < 0.10, all NS).

| Measure | Value |
|---------|-------|
| Observations | 11,525 (token-level) |
| Raw Spearman rho | **-0.004** |
| Raw p | 0.647 |
| Partial rho (controlling PREFIX) | **0.007** |
| Partial p | 0.455 |
| Per-PREFIX max |rho| | 0.097 (all NS) |

This is a **stronger confirmation of C522** than the original type-level test: with 11,525 observations (vs C522's type-level sample), the power to detect even a weak effect (rho=0.04) is >99%. The null is clean.

---

## Interpretation

C522 established construction-execution layer independence at r=-0.21 (p=0.07, not significant) with a moderate sample. This constraint confirms the independence at full power: an atom's position within its compound MIDDLE string contains literally zero information about where that token will appear in a line.

This has a profound implication: the construction grammar (C1065: how atoms are ordered within compounds) and the execution grammar (how tokens are positioned in lines) are **completely separate systems**. A compound with atoms ordered op→al→ai (construction) can appear at any line position (execution). The construction layer builds the lexicon; the execution layer deploys it according to independent rules.

This also means C1060's gateway/terminal atoms (opch=INITIAL, ai=FINAL) describe positions within the compound string, not predictions about line behavior. Gateway atoms open compounds; terminal atoms close compounds. Neither predicts where the token goes in a line.

---

## Method

- 11,525 token-level observations: each token with a compound MIDDLE contributes one observation per atom
- String position: atom_index / (compound_length - 1) normalized to [0,1]
- Line position: token_index / (line_length - 1) normalized to [0,1]
- Raw: Spearman correlation on all observations
- Partial: residualize both positions on PREFIX group means, then Spearman
- Per-PREFIX: Spearman within each PREFIX group with >= 50 observations

**Script:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/scripts/morphological_joint_space.py`
**Results:** `phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t4_string_vs_line_position.json`

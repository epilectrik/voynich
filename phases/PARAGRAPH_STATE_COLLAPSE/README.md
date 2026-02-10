# PARAGRAPH_STATE_COLLAPSE Phase

**Status:** CLOSED
**Verdict:** NO COLLAPSE — Body homogeneity confirmed across all diversity dimensions
**Tests:** 8 (01-08) | **Constraints:** C963_EXTENDED, C965 (kernel shift)
**Scope:** Currier B (23,243 tokens, 2,420 lines, 83 folios)

## Governing Premise

External expert observed that late paragraphs look "quiet and rigid" — short lines, AX clustering, EN suppression, low HT. C963 proved role *fractions* are flat, and C932 proved vocabulary *rarity* decreases. But no formal test existed for whether the *effective instruction set* — the diversity of available operations — actually shrinks as paragraphs progress.

Central question:
> Does the number of distinct structural options measurably collapse toward paragraph ends, even when compositional proportions stay stable?

## Key Distinction from Prior Work

| Prior Constraint | What it measures | What this phase measures |
|-----------------|-----------------|------------------------|
| C963 | Role *fractions* (EN/FL/CC %) | Role/suffix/MIDDLE *entropy* and *distinct counts* |
| C932 | Vocabulary *rarity* (rare→universal) | Vocabulary *diversity* (how many options) |
| C677 | Line *shortening* | Whether diversity drops *beyond* what shortening explains |

These are orthogonal. Fractions can be stable while diversity decreases (same recipe, fewer ingredients per line).

## Results Summary

| Test | Topic | Verdict | Key Finding |
|------|-------|---------|-------------|
| T01 | Vocabulary Entropy | **FAIL** | Raw rho=-0.18 vanishes after length control (partial=-0.02, p=0.47) |
| T02 | Role Entropy | **FAIL** | Partial rho=+0.009 (p=0.75) — completely flat |
| T03 | Suffix Entropy | **FAIL** | Partial rho=-0.011 (p=0.69) — completely flat |
| T04 | Effective Instruction Set | **FAIL** | All 4 metrics (roles/classes/MIDDLEs/suffixes), raw+rate — nothing survives |
| T05 | AX Terminal Scaffold | **FAIL** | AX fraction, INIT/MEDIAL/FINAL subgroups — all flat |
| T06 | HT-AX Substitution | **FAIL** | Rates flat; cross-correlation rho=-0.10 (p=0.0004) is per-line trade-off |
| T07 | Kernel Diversity | **FAIL** | Diversity flat, BUT h-fraction rises/e-fraction drops (survives length control) |
| T08 | Integrated Verdict | **NO COLLAPSE** | Score 0.0/7.0 |

## The Line-Length Confound

The single most important finding: **line length correlates with MIDDLE entropy at rho=+0.75** (T01). Every raw diversity decline observed (T01-T04, T07) is a mechanical consequence of C677 (paragraphs get shorter toward the end). After controlling for line length via partial Spearman rho, ALL effects vanish.

This means the expert's observation of "quiet and rigid" late paragraphs is an optical illusion created by line shortening — fewer tokens per line means fewer distinct types per line, but the *rate* (types/token) is unchanged.

## Notable Findings

Despite 7/7 FAIL verdicts on the collapse hypothesis, two genuine signals emerged:

### 1. Kernel Composition Shift (T07)

h-kernel fraction increases through body lines (partial rho=+0.10, p=0.0004), while e-kernel fraction decreases (partial rho=-0.086, p=0.002). Both survive line-length control and Bonferroni correction.

This is NOT a diversity collapse — the number of distinct kernels stays flat (~2.6 per line). It's a composition shift: late body lines favor h-kernel (ch/sh prefix) tokens over e-kernel tokens. → Proposed as **C965**.

### 2. HT-AX Per-Line Trade-off (T06)

HT rate and AX rate show negative cross-correlation (rho=-0.10, p=0.0004) across body lines. This is not a positional trend (neither rate changes with position) but a per-line substitution pattern: lines with more HT tend to have less AX.

## Final Characterization

C963 body homogeneity is **comprehensively confirmed** across every diversity dimension tested:

1. **Entropy flat**: Shannon entropy of MIDDLE vocabulary, role distribution, suffix distribution, and kernel distribution — all flat after length control
2. **Distinct counts flat**: n_unique roles, classes, MIDDLEs, suffixes — all flat
3. **Rate-normalized flat**: types/token rates — all flat
4. **AX subgroups flat**: INIT/MEDIAL/FINAL AX fractions — no terminal scaffold
5. **HT rate flat**: confirms C842 within body
6. **Only genuine positional signal**: kernel composition shift (h rises, e drops)

The system writes structurally equivalent control blocks throughout the paragraph body. The only progression is: (a) lines get shorter (C677), (b) vocabulary gets more universal (C932), (c) h-kernel tokens gradually replace e-kernel tokens (C965). The effective instruction set does NOT shrink.

## Stop Conditions

- Phase verdict: NO_COLLAPSE (0.0/7.0)
- All pre-registered collapse hypotheses falsified
- Line-length confound explains all raw diversity declines
- No further diversity/entropy investigation warranted
- Kernel composition shift (C965) is the only novel finding — suitable for targeted follow-up if desired

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_vocabulary_entropy_collapse.py | T01 | 01_*.json |
| 02_role_entropy_collapse.py | T02 | 02_*.json |
| 03_suffix_entropy_collapse.py | T03 | 03_*.json |
| 04_effective_instruction_set.py | T04 | 04_*.json |
| 05_ax_terminal_scaffold.py | T05 | 05_*.json |
| 06_ht_ax_substitution.py | T06 | 06_*.json |
| 07_kernel_diversity_collapse.py | T07 | 07_*.json |
| 08_integrated_verdict.py | T08 | 08_*.json |

## Provenance

- Designed in response to external expert review of decoded f103v
- Pre-registered pass/fail criteria per test
- All length controls: partial Spearman rho via OLS residualization
- All shuffle controls: 1000 iterations, seed=42, within-paragraph line permutation
- Bonferroni correction within each script
- T01/T03: 174 paragraphs with 5+ lines, 1,324 body lines (matching C963 reference)
- T02/T04-T07: 187 paragraphs with 5+ lines, 1,261 body lines (par_final split variant)
- Both counts yield identical verdict pattern (all FAIL); difference is inconsequential

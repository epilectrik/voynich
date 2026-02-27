# C1340: Suffix Stability Across Modes

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_ASSIGNMENT (469)

## Constraint

When the same MIDDLE appears in Mode A and Mode B lines, its suffix distribution barely changes. Median cross-mode JSD is 0.020 and only 12.1% of dual-mode MIDDLEs show statistically significant suffix shift (p<0.01). A small but real contextual modulation exists (mean JSD 0.035 vs null 0.026, permutation p=0.003).

## Evidence

From suffix_mode_assignment.py test S3 (91 MIDDLEs with 5+ tokens in both modes):

**Cross-mode suffix JSD distribution:**

| Metric | Value |
|--------|-------|
| Mean JSD | 0.035 |
| Median JSD | 0.020 |
| Null mean JSD | 0.026 |
| Permutation p | 0.003 |
| Significant shift (p<0.01) | 11/91 (12.1%) |

**Perfectly stable MIDDLEs (JSD = 0.000):**
- eck (n_A=47, n_B=31): always terminal in both modes
- eey (n_A=171, n_B=387): always bare in both modes
- ect (n_A=32, n_B=11): always terminal in both modes

**Top shifters:**
- ka (JSD=0.318, n_A=11, n_B=9): shifts suffix between modes
- lsh (JSD=0.181, n_A=14, n_B=5): shifts suffix between modes

## Interpretation

The dominant pattern is suffix stability: the same MIDDLE carries the same suffix regardless of line mode. The 12.1% of MIDDLEs that do shift are real (perm p=0.003) but represent a minority contextual effect. This directly supports the identity model of suffix assignment (C1338): suffix is primarily a MIDDLE property, with modest contextual modulation.

The top shifters (ka, lsh, cph, lke) have small sample sizes in at least one mode, so the apparent shifts may partly reflect sampling noise. The high-frequency MIDDLEs (eck, eey, edy) are perfectly stable.

## Provenance

- suffix_mode_assignment.json: test S3
- Extends: C1338 (MIDDLE suffix selectivity — S3 confirms suffix stability is preserved across mode contexts)
- Relates to: C1229 (alternating suffix modes), C1258 (parallel mode tracks)

## Status

CONFIRMED — suffix assignment is stable across modes (median JSD 0.020), with 12.1% showing weak contextual shift.

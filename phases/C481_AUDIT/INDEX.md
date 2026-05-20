# C481_AUDIT — Survivor-Set Uniqueness retraction

**Status:** COMPLETE — audit narrative only
**Date:** 2026-05-19
**Verdict:** RETRACT (Tier 1) — triple-pattern failure + post-hoc reframe in FINDINGS.md

---

## Audit method

No re-run script needed. The project's own follow-up code (`phases/CLASS_COSURVIVAL_TEST/scripts/compute_survivor_sets.py`) had already explicitly verified C481 and recorded `c481_verified: False` in its JSON output. The audit consisted of:

1. Reading C481 constraint claim ("0 collisions in 1,575 lines")
2. Checking the verification JSON: `c481_verified: False`, 1579 records → 1203 unique sets = 376 collisions
3. Identifying the FINDINGS.md reframe ("C481 VALIDATED — 1,203 unique class patterns confirms discrimination")
4. Recognizing this as claim-substitution: original claim was about UNIQUENESS, reframe was about DISCRIMINATION

---

## Findings (see C481 entry + CHANGELOG v6.77 for full text)

**Triple-pattern failure** within the constraint itself:
1. **Value doesn't reproduce** — 376 collisions ≠ 0 (C131-shape)
2. **Direction wrong** — clustering observed (24% collision rate), uniqueness claimed (C476-shape)
3. **Denominator non-informative** — 2^49 possible subsets makes "0 collisions" expected even randomly (C475-shape)

**5th new failure pattern** in the writeup layer:
- **FINDINGS.md post-hoc claim-substitution**: original "0 collisions / DETERMINISTIC" silently reframed as "1,203 patterns = discrimination confirmed = VALIDATED"
- The script JSON says False; the markdown says VALIDATED. Same directory, contradictory verdicts.

---

## Action taken

- C481 retracted (Tier 1) with full audit narrative
- FINDINGS.md corrected to acknowledge `c481_verified: False` actual outcome
- Methodology memory `feedback_post_hoc_claim_substitution.md` saved (5th distinct failure pattern)

---

## 2026-01-12 batch status

After C481 retraction, the 2026-01-12 probe family stands at:
- **C475 DEMOTED** (sparsity denominator)
- **C476 RETRACTED** (broken baseline, wrong direction)
- **C481 RETRACTED** (triple-pattern failure + FINDINGS.md reframe)

**3/3 audit-driven action rate.** Both experts recommend switching to **batch-sweep mode** for the remaining 2026-01-12 cohort:
- C478 (already AUDIT_PENDING)
- C479 (Survivor-Set Dimensionality — same Phase SSD family)
- C480 (same family)
- C755, C756 (coverage-family successors)

Per crazy-expert: 30-40% retraction-rate prediction undershot. Real rate is 100% (3/3). Strong evidence of methodology cohort issue — likely shared registration discipline gap (no within-line shuffle null, sparsity-denominator unawareness, post-hoc reframe tolerance).

Recommendation: pre-register three diagnostic axes (value reproducibility / direction correctness / denominator informativeness) + check for FINDINGS.md reframe pattern, then batch-sweep all 5 remaining 2026-01-12 candidates in one commit.

---

## Files

| File | Purpose |
|------|---------|
| `../CLASS_COSURVIVAL_TEST/scripts/compute_survivor_sets.py` | Has `c481_verified` field; reports False |
| `../CLASS_COSURVIVAL_TEST/results/a_record_survivors.json` | Contains the False verification |
| `../CLASS_COSURVIVAL_TEST/results/FINDINGS.md` | Was incorrectly labeling C481 "VALIDATED"; now corrected |
| `../../context/CLAIMS/C481_survivor_set_uniqueness.md` | Retraction narrative |
| `~/.claude/projects/.../memory/feedback_post_hoc_claim_substitution.md` | NEW methodology memory (5th pattern) |

No new audit scripts — the audit was a read-and-cross-reference action using the project's own follow-up artifacts.

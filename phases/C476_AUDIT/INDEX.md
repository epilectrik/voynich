# C476_AUDIT — Coverage Optimality retraction

**Status:** COMPLETE — audit narrative only (no new script needed; audit done by reading existing methodology)
**Date:** 2026-05-19
**Verdict:** RETRACT (Tier 1) — broken-baseline pattern + directionally-opposite surviving measurement

---

## Audit method

C476 was flagged by audit-sweep triage as score=1 (targeted-list membership only; full text not in INDEX.md row so script couldn't analyze methodology). Manual audit consisted of reading the original methodology in `phases/COVERAGE_OPTIMALITY/coverage_optimality.py` and inspecting the existing results JSON.

No re-run script needed — the audit findings are about the methodology design (broken baseline), not about value reproducibility.

---

## Findings (see currier_a.md C476 entry + CHANGELOG v6.76 for full text)

Three methodological issues:

1. **"100% coverage" is tautological** (denominator = data)
2. **Greedy baseline uses alphabetical fallback** when gain=0 after coverage saturates → spams hubs ('a', 'o', 'e' etc.) as artifact, not as coverage strategy
3. **Frequency-matched baseline has sampling-with-replacement issues** on Zipfian distribution

The "22.3pp hub savings" headline was measuring `sort(alphabetically_early_strings)`, not `coverage_optimization_vs_rationing`.

**Surviving measurement: 3.2× hub enrichment vs uniform** (Real A 31.6% vs random uniform 9.8%) — but this is **directionally opposite** to "rationing" claim.

Retract (not demote) per `feedback_broken_baseline_audit.md`: when surviving measurement contradicts the claim's direction, retraction is cleaner than demotion.

---

## Downstream

- **C478** flagged AUDIT_PENDING (inherits coverage-control framing from C476)
- **C481, C755, C756** added to audit-sweep target list (2026-01-12 batch elevated prior)

---

## Files

| File | Purpose |
|------|---------|
| `../COVERAGE_OPTIMALITY/coverage_optimality.py` | Original methodology (lines 332-380 for greedy algorithm) |
| `../COVERAGE_OPTIMALITY/results/coverage_optimality.json` | Original results (numbers verified to reproduce) |
| `../../context/CLAIMS/currier_a.md` (C476 entry) | Retraction narrative |
| `~/.claude/projects/.../memory/feedback_broken_baseline_audit.md` | Methodology lesson |

No new scripts. Audit was a read-and-reason action on the existing methodology.

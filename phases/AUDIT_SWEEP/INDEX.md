# AUDIT_SWEEP — Mechanical Audit Triage Infrastructure

**Status:** ESTABLISHED — tool + baseline triage report
**Date opened:** 2026-05-19
**Created during:** session that produced C131 retraction + C475/C1068 demotions

---

## Purpose

After three audit-driven actions in one session established a **failure-mode taxonomy** (three distinct patterns), this directory provides infrastructure to apply those diagnostics mechanically across the full constraint corpus.

The script does NOT auto-audit. It **triages** — flagging candidates for manual review based on diagnostic regex patterns matched against constraint descriptions.

---

## The three diagnostic patterns

### 1. INVENTED-THRESHOLD (C131 pattern)
- Constraint cites a specific numerical threshold for falsification
- Threshold is not validated against external baselines
- Pre-v2.42 era (transcriber filter bug) → values may not reproduce
- **Memory:** `feedback_made_up_threshold_audit.md`

### 2. SPARSITY-DENOMINATOR (C475 pattern)
- Constraint cites "X% of [possible/total] pairs forbidden"
- On a sparse graph (vocabulary V > 100, attested pairs << V*(V-1)/2)
- Headline % uses N_possible denominator, not N_attested
- **Memory:** `feedback_denominator_choice_sparse_cooccurrence.md`

### 3. CHI²-VS-PERMNULL (C1068 pattern)
- Cross-layer/coupling claim with chi² statistic
- Permutation null is marginal (p > 0.05) or absent entirely
- Chi² against independence null is misleading when factors share frequency marginals
- **Memory:** `feedback_chi2_vs_permutation_null_mismatch.md`

---

## Usage

```bash
# Show all candidates with score ≥ 1
python scripts/audit_sweep.py --min-score 1

# Show only high-suspicion (multi-signal) candidates
python scripts/audit_sweep.py --min-score 2

# Filter to specific pattern
python scripts/audit_sweep.py --pattern sparsity
python scripts/audit_sweep.py --pattern chi2

# Crazy-expert's targeted list only
python scripts/audit_sweep.py --targeted-only

# Limit to top N
python scripts/audit_sweep.py --min-score 1 --top 30
```

Re-run after each audit action — the constraint table updates with retractions/demotions and already-acted constraints are auto-skipped.

---

## Baseline triage findings (2026-05-19)

Initial run produced:
- **2 candidates at score ≥ 2** (multi-pattern flag) — highest-priority audit
- **199 candidates at score ≥ 1** — broader audit pool
- Pattern breakdown:
  - Pattern 1 (invented-threshold) flagged: 31
  - Pattern 2 (sparsity-denominator) flagged: 9
  - Pattern 3 (chi²-vs-perm-null) flagged: 152
  - In targeted list: 9
  - Pre-v2.42 era (C# < 500): 9

### Top-2 multi-signal candidates

| Constraint | Score | Patterns | Notes |
|-----------|------:|----------|-------|
| **C1065** | 2 | sparsity + chi² | Atom Bigram Ordering Grammar; chi²=1898.8, p=1.8e-73, 659 pairs cited |
| **C1711** | 2 | sparsity + chi² | PP-manifold section-independent; chi² without perm-null companion |

### Crazy-expert's targeted list (all flagged via list membership)

C153, C268, C476, C481, C517, C518, C982, C983, C996 — from expert-consultation during C475 audit. These are pre-2026-02 / pre-PHASE_700 era constraints in the AZC-graph + cross-system-compatibility burst that are high-suspicion for sparsity-denominator pattern.

### The Pattern 3 problem (152 candidates)

The chi²-without-perm-companion signal fires on **152 constraints**. This doesn't mean all 152 are flawed — but it does mean the project has 152 chi²-based claims that never had permutation null companions. Crazy-expert estimated 8-20; the actual count is much higher.

**This is the methodological bulk of the audit-sweep work.** Many will survive review (chi² is appropriate when factors aren't frequency-correlated), but each is audit-eligible until checked.

---

## Recommended audit cadence

Per crazy-expert's cadence guidance:
- Continue one-at-a-time audits while finding new failure modes
- Move to batch-mode when audits start producing only repeats of the three known patterns
- The taxonomy is the high-EV product — each new pattern is a new diagnostic

**Suggested next audits (in priority order):**

1. **C1065** (score 2) — multi-signal, recent enough that audit infrastructure should be readily reusable
2. **C1711** (score 2) — second multi-signal
3. **C476** (Coverage Optimality) — targeted list, sister probe to C475 from same 2026-01-12 session, high a-priori suspicion
4. **C153, C268, C481, C517, C518, C982, C983, C996** — rest of targeted list
5. **Spot-check 5-10 of the 152 chi²-only constraints** to estimate hit rate; if >40% need demotion, do the full sweep; if <20%, opportunistic

---

## Files

| File | Purpose |
|------|---------|
| `../../scripts/audit_sweep.py` | The triage script |
| `triage_baseline_2026_05_19.txt` | First-run output with all 199 score≥1 candidates |
| This INDEX.md | Tool documentation |

---

## Limitations

- **Regex-based:** can produce false positives (signal fires without underlying problem) and false negatives (signal fails to fire when problem exists)
- **Does not re-run tests:** can't tell if a value reproduces on current data — that requires manual audit
- **Reads only constraint table + INDEX.md row text:** if substantive detail is in per-constraint .md files, the regex won't see it. Full audit needs the per-constraint file.
- **No phase-date filter:** pre-v2.42 era proxy is C-number < 500, which is approximate
- **Conservative scoring:** the +1 for being on the targeted list is the only way many short-text constraints get flagged

The script is **triage, not verdict**. Treat hits as "worth manual look," not "definitely needs action."

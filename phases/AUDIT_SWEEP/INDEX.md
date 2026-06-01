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
3. ~~**C476** (Coverage Optimality)~~ — RETRACTED (broken-baseline audit, separate)
4. ~~**C153, C268, C481, C517, C518, C982, C983, C996**~~ — **CLEARED / actioned (see Round 2 log, 2026-05-31).** Pattern-2 targeted list is exhausted of un-actioned Tier-2 targets. Do NOT re-flag.
5. **Spot-check 5-10 of the ~128 chi²-without-perm-companion (Pattern-3) constraints** to estimate hit rate; if >40% need demotion, do the full sweep; if <20%, opportunistic. **This is now the only open audit bulk.**

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

---

## Audit outcomes log (running list of triage hits → actual verdicts)

### Round 1 audits (2026-05-19)

| Constraint | Triage score | Manual audit verdict | Action |
|-----------|------:|----------------------|--------|
| C131 | n/a (selected from expert list) | Retract — invented threshold + non-reproducing value + null at observed (3-axis fail) | RETRACTED Tier 1 |
| C475 | n/a (selected from expert list) | Demote — sparsity-denominator, max expected=2.51 among "illegal" pairs | DEMOTED Tier 2→3 |
| C1068 | n/a (AUDIT_PENDING flag from C475 commit) | Demote — chi²-vs-perm-null mismatch (perm_p=0.13) | DEMOTED Tier 2→3 |
| **C1065** | **2 (multi-signal: pair-counts + chi²-huge)** | **SURVIVES — methodology sound: permutation null preserves composition, observed >> null, V=0.376 effect, N≥5 filter on per-pair analysis. Text honestly distinguishes main claim (grammar exists, STRONG) from secondary claim (C521 kernel propagation, PARTIAL).** | **NONE (false positive)** |

### Pattern hit-rate calibration (n=1)

First multi-signal triage hit (C1065) was a **false positive**. Sample size n=1 is too small to update priors, but suggests Pattern 3 (chi²-huge) is the least-specific signal — it fires on any chi² with high statistic regardless of whether permutation null companion exists.

**Refined expected hit-rate estimates (after C1065):**
- Pattern 3 (chi²-vs-perm-null) standalone: **<40% hit rate** (downward revision from crazy-expert's original 5-15% retraction / 15-25% demotion). The 152-candidate pool likely includes many like C1065 with proper perm-null companions that the regex doesn't see.
- Pattern 2 (sparsity-denominator): probably higher hit rate — C475 was a clean hit, the denominator-choice issue is structural
- Pattern 1 (invented-threshold): C131 was a clean hit, but the pattern requires reading source code for true verification; hit rate uncertain
- Multi-signal (score ≥ 2): n=1 false positive so far. Reserve judgment until more data.

### Pattern enhancement candidates — APPLIED 2026-05-19

**Refinement implemented:** Pattern 3 now classifies the chi² situation into four sub-states:
- `chi2_with_clean_perm_null` (perm p < 0.05 cited) — **NOT flagged** (C1065 case)
- `chi2_with_marginal_perm_null` (perm p ≥ 0.05 cited) — flagged (C1068 pattern, demotion candidate)
- `chi2_with_unclear_perm` (perm mentioned, no extractable p) — flagged for manual review
- `chi2_without_perm_companion` (no perm mention at all) — flagged AUDIT-PENDING

**Implementation:** `PERM_P_REGEX` extracts numeric p-values associated with permutation null mentions, then `classify_perm_null()` returns the four-way classification. Pattern 3 only fires when chi² is cited AND perm-null status is non-clean.

**Impact on triage pool (post-refinement, 2026-05-19):**

| Metric | Before refinement | After refinement | Delta |
|--------|------------------:|-----------------:|------:|
| Score ≥ 1 candidates | 199 | 181 | −18 |
| Pattern 3 flagged | 152 | 133 | −19 |
| Score ≥ 2 (multi-signal) | 2 | 1 | −1 (C1065 correctly removed) |

**Sub-breakdown of Pattern 3 hits (133 total):**

| Sub-category | Count | Action implication |
|--------------|------:|---------------------|
| `chi2_without_perm_companion` | 128 | AUDIT-PENDING; needs perm-null companion or downgrade |
| `chi2_with_marginal_perm_null` | 2 | Direct C1068 candidates; high-priority for demotion check |
| `chi2_with_unclear_perm` | 1 | Manual review of perm-null status needed |
| `nmi_cited` | 2 | Supplementary signal (cross-layer coupling) |

**Highest-priority targets identified by refined Pattern 3:**
- **C1226** "ke/ek Ratio Process-Context Conditioning" (chi²=77 with marginal perm)
- **C1295** "Paragraph Termination is Memoryless" (chi²=1 + perm p=0.822) — likely **false positive at semantic level**: this is a null-finding registration where the marginal perm-p is APPROPRIATE evidence FOR the null claim, not a positive overclaim. The regex cannot distinguish "perm p>0.05 supporting null claim" from "perm p>0.05 undermining positive claim."

Manual review remains essential. The refined tool reduces false-positive rate but cannot eliminate it without semantic understanding of each constraint's claim direction.

### Audit-outcome taxonomy (4 categories now)

After 4 audits, four distinct verdict shapes:

1. **RETRACT** (C131) — three-axis failure, nothing survives
2. **DEMOTE-with-survivor** (C475) — wrong framing, strong-form survives in adjacent constraint
3. **DEMOTE-with-narrative** (C1068) — methodology sound, but tier classification too generous for proper null
4. **NO ACTION (false positive)** (C1065) — triage signature fires but methodology is actually sound

Category 4 is informative for tool calibration even though no constraint changed.

### Round 2 audits (2026-05-31) — sparsity-denominator targeted-list clearance

Audited crazy-expert's remaining Pattern-2 targeted list against the **signature** ("constraint citing a percentage of possible/potential pairs/triples on sparse data"), verified from source (CONSTRAINT_TABLE + per-constraint `.md`). **None matches the signature** — the targeted list was a membership guess broader than the diagnostic.

| Constraint | Actual claim | Matches sparsity signature? | Verdict |
|-----------|--------------|:---:|--------|
| C982 | Discrimination-space dimensionality ~101 (median of 7 methods, 28–256 spread) | No — dimensionality estimate, no pair denominator | NO ACTION — sound; "~101" already hedged as STRUCTURED_HIGH_DIMENSIONAL |
| C983 | Compatibility transitivity: clustering 0.873 vs **Configuration Model** 0.253 (z=+136.9) | No — degree-preserving null; 3.5× effect | NO ACTION — robust (CM controls the hub/frequency confound by construction) |
| C996 | Forbidden topology: 13/17 forbidden transitions involve HUB (denominator = **17 attested**) | No — attested denominator, descriptive | NO ACTION — descriptive fact sound; chi² p-values (3928/596) frequency-confounded (cosmetic; claim doesn't rest on them) |
| C153 | Prefix/suffix axes partially independent (MI=0.075) | No — MI/independence claim | NO ACTION (wrong pattern; if anything a Pattern-3 candidate, separate) |
| C268 | 897 observed combinations | No — attested count, not a forbidden-% | NO ACTION (wrong pattern) |

C476 retracted (broken-baseline, separate); C481 audited (claim-substitution, separate); C517/C518 already Tier 3.

**Conclusion: the sparsity-denominator (Pattern 2) targeted list is EXHAUSTED of un-actioned Tier-2 targets.** No remaining flagged constraint makes a genuine "X% of possible pairs forbidden on N_possible" claim. Pattern-2 baseline-flagged count (9) = exactly this list; with it cleared, Pattern 2 has no open targeted candidates. The ~128 chi²-without-perm-companion (Pattern-3) pool is now the only open audit bulk.

**Tool/calibration lesson:** crazy-expert's `--targeted-only` list is *membership-based*, not signature-based — it flagged 5 constraints (C153/C268/C982/C983/C996) that don't match the Pattern-2 regex signature at all. Treat list membership as the *weakest* triage signal (it was added precisely because short-text constraints don't trip the regex); always confirm against the per-constraint source before auditing. (Consider dropping the 5 cleared constraints from the script's hardcoded `TARGETED` list so `--targeted-only` stops re-surfacing them — optional.)

### Audit-outcome category count (after Round 2)

Round 2 added 5 Category-4 (NO ACTION) outcomes, all "signature-does-not-match" rather than "methodology-sound-but-flagged" (C1065's flavor). Net audit tally: 1 retract (C131), 2 demote (C475, C1068), 6 no-action (C1065 + 5 Round-2). The taxonomy of *failure* patterns is unchanged; what Round 2 adds is a **no-action sub-reason**: *triage list-membership over-included constraints that never matched the signature.*

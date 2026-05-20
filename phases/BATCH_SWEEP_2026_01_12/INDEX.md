# BATCH_SWEEP_2026_01_12 — Cohort audit of Phase SSD + COVERAGE_OPTIMALITY successors

**Status:** COMPLETE
**Date:** 2026-05-19
**Mode:** Batch (5 constraints in one commit)
**Trigger:** 3/3 hit rate on prior 2026-01-12 audits (C475 demoted, C476 retracted, C481 retracted) — both experts recommended switching to batch-sweep

---

## Pre-registered diagnostic axes (locked before reading constraints)

For each candidate, score:

1. **Value reproducibility:** does the headline value reproduce on current data? (C131 pattern)
2. **Direction correctness:** does direction of surviving observation match registered claim? (C476 pattern)
3. **Denominator informativeness:** is the denominator informative (max-expected > 5 for "X%" claims)? (C475 pattern)
4. **JSON-vs-writeup mismatch:** does a follow-up FINDINGS.md contradict the script JSON verification field? (C481 pattern)

**Pre-registered decision rules (locked before reading):**
- 3+ axes fail → RETRACT
- 2 axes fail → DEMOTE
- 1 axis fails → REFRAME (in-place, no tier change)
- 0 axes fail → SURVIVES

Plus: **interpretive dependence on retracted/demoted constraints** counts as 1 axis (the interpretation is invalid even if measurements stand).

---

## Candidate verdicts

### C478 — Temporal Coverage Scheduling
**Verdict:** REFRAME (no tier change, update text)

Four sub-claims:
1. **Back-loaded coverage** — 90% coverage 9.6% later than random permutation. Descriptive measurement of A's MIDDLE ordering. ✅ Holds as descriptive fact.
2. **Front-loaded novelty** — 21.2%/9.4%/11.3% phase distribution. Descriptive. ✅ Holds.
3. **U-shaped tail pressure** — 7.9%/4.2%/7.1% by phase. Descriptive. ✅ Holds.
4. **PREFIX cycling** — 7 prefixes cycle, 164 regime changes. Descriptive. ✅ Holds.

**The descriptive measurements are real.** What dies is the **"pedagogical pacing" / "deliberate scheduling" interpretation** — it depended on C476's "coverage is a meaningful target" premise, which C476 retraction killed.

**Action:** clear AUDIT_PENDING flag, reframe C478 entry to register the descriptive measurements as Tier 2 facts about A's MIDDLE ordering, with the "scheduling" interpretation demoted to Tier 3 candidate.

**Axes failed:** ~1 (interpretive dependence only; raw measurements survive)

---

### C479 — Survivor-Set Discrimination Scaling
**Verdict:** SURVIVES (update cross-references)

Methodology: partial correlation between survivor-set size and HT morphological diversity, controlling for line length. Raw rho=0.185, partial rho=0.395, p=2.4e-30, n=774.

This is an independent measurement using standard partial correlation. **Doesn't depend on the retracted C481 framing** (C481 was about "0 collisions" uniqueness; C479 is about size correlation).

Cross-references to C475 (now demoted) and C481 (now retracted) need updating but the core measurement stands.

**Axes failed:** 0

**Action:** No tier change. Update cross-references to note C475 demotion + C481 retraction.

---

### C480 — Constrained Execution Variability
**Verdict:** SURVIVES (already properly hedged)

Already Tier 3 PROVISIONAL with rho=0.306, p=0.078 explicitly cited as marginal. The constraint text honestly says: "marginal", "PROVISIONAL", "do not promote without replication."

**Axes failed:** 0

**Action:** No change needed. Constraint registered with appropriate epistemic hedging.

---

### C755 — A Folio Coverage Homogeneity
**Verdict:** DEMOTE Tier 2 → Tier 3

Measurement: real A folios at 0th percentile vs synthetic for discrimination (mean discrimination 1.064 real vs 1.281 synthetic). The number is real but the **interpretation depends on retracted C476.**

The constraint text explicitly says: "This is not a failure — it is evidence of deliberate coverage optimization. This aligns with C476 (Coverage Optimality)."

With C476 retracted (broken baseline + tautological "100% coverage"), the "deliberate coverage optimization" interpretation loses its foundation. The descriptive measurement (real folios are more homogeneous than synthetic) survives but the **interpretation flip** ("worse-than-random = deliberate optimization") is unsupported.

Also: this is structurally similar to the C476 pattern — finding "real worse than baseline" and reframing as "deliberate." Once is suspicious; in a cohort with C476 already retracted for this pattern, it's a red flag.

**Axes failed:** 2 (interpretive dependence on retracted C476 + same "worse-than-random reframed as optimization" pattern that broke C476)

**Action:** Demote Tier 2 → Tier 3. Preserve measurement, note interpretive dependence on retracted C476.

---

### C756 — Coverage Optimization Confirmed
**Verdict:** DEMOTE Tier 2 → Tier 3

Two main claims:
- **11× higher pairwise Jaccard similarity** (real 0.246 vs random 0.022, z=1144)
- **First 10 folios cover 60% PP** + 25 hub MIDDLEs in >50% of folios, 100% PP

The 11× figure has the same baseline issue as C476: comparison to "random PP vocabulary" likely doesn't represent any meaningful alternative hypothesis. The z=1144 is extreme — characteristic of comparing actual frequency-weighted distributions to uniform-random samples.

The interpretation explicitly inherits from retracted C476: "This confirms C476 (Coverage Optimality) and explains C755 (A Folio Homogeneity). A folios are not designed to discriminate B programs — they are designed to maximize vocabulary availability."

The **hub-MIDDLE observation (25 MIDDLEs in >50% folios, 100% PP)** is likely a real structural fact that survives as descriptive observation. But the **11× similarity comparison** and the **"coverage optimization" interpretation** both inherit from C476's broken framework.

**Axes failed:** 2 (interpretive dependence on retracted C476 + likely-broken random-PP baseline for 11× comparison)

**Action:** Demote Tier 2 → Tier 3. Preserve the hub-MIDDLE structural observation, note interpretive dependence on retracted C476.

---

## Batch verdict summary

| Constraint | Verdict | Action | Axes failed |
|-----------|---------|--------|------------:|
| C478 | REFRAME | Clear AUDIT_PENDING, demote interpretation only | 1 |
| C479 | SURVIVES | Update cross-refs | 0 |
| C480 | SURVIVES | No change | 0 |
| C755 | DEMOTE | Tier 2 → Tier 3 | 2 |
| C756 | DEMOTE | Tier 2 → Tier 3 | 2 |

**Sweep outcome: 0 retractions, 2 demotions, 1 reframe, 2 survives.**

Crazy-expert's prediction of 4-5 of 5 hits was overshooting. Actual hit rate: 3/5 (60%) including reframe. The remaining 2/5 (C479, C480) survive because:
- C479: methodologically independent of the C475/C476/C481 framework
- C480: already properly hedged as PROVISIONAL Tier 3

---

## 2026-01-12 cohort final status

After this batch-sweep, the 2026-01-12 probe family stands at:
- **C475** DEMOTED (sparsity denominator)
- **C476** RETRACTED (broken baseline, wrong direction)
- **C478** REFRAMED (descriptive measurements stay, interpretation demoted)
- **C479** SURVIVES
- **C480** SURVIVES (Tier 3 PROVISIONAL, already hedged)
- **C481** RETRACTED (triple-pattern + reframe)
- **C755** DEMOTED (interpretive dependence on C476)
- **C756** DEMOTED (interpretive dependence on C476 + broken-baseline pattern)

**Cohort hit rate: 6/8 (75%) actions taken (2 retractions + 3 demotions + 1 reframe + 2 survives).** This is the methodology cohort issue that crazy-expert predicted — confirmed.

The 2026-01-12 batch had a systemic registration discipline gap:
- Sparsity-denominator unawareness (C475)
- Broken-baseline tolerance (C476, C755, C756)
- Wrong-direction interpretation flip ("worse than random = deliberate optimization": C476, C755)
- Post-hoc claim-substitution in writeups (C481)
- Interpretive dependence chains (C478 → C476, C755 → C476, C756 → C476)

The independent measurements that survive (C479, C480, C478 raw distributions) are sound; the **framework that wove them together into "coverage optimization" / "deliberate scheduling" interpretation** was the methodology problem.

---

## Files modified in this batch

| File | Change |
|------|--------|
| `context/CLAIMS/currier_a.md` | C478 cleared AUDIT_PENDING + reframed; C755 + C756 marked DEMOTED |
| `context/CLAIMS/C479_*.md` | Cross-refs updated to note C475 demotion + C481 retraction |
| `context/CLAIMS/C480_*.md` | No change (already properly hedged) |
| `CLAUDE.md` | Version bump, demoted count 3 → 5 |
| `context/CLAIMS/INDEX.md` | Version bump |
| `context/SYSTEM/CHANGELOG.md` | v6.78 entry |
| `.claude/agents/crazy-expert.md` | C478, C755, C756 rows updated |
| Sync files | Regenerated |

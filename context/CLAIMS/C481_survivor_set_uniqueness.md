# ~~C481: Survivor-Set Uniqueness~~ [RETRACTED 2026-05-19]

**Tier:** 1 (RETRACTED) | **Status:** FALSIFIED — value does not reproduce, direction inverted, denominator non-informative
**Scope:** A+AZC | **Source:** Phase SSD (2026-01-12); audit `phases/C481_AUDIT/` + `phases/CLASS_COSURVIVAL_TEST/` (2026-05-19)

---

## Original claim (RETRACTED)

> AZC survivor sets are essentially unique per Currier A line (0 collisions in 1,575 lines), functioning as high-dimensional constraint fingerprints rather than grouping labels or variant lists.

Original interpretation: "DETERMINISTIC" — each A line produces a distinct survivor set.

---

## Audit findings

**The project's own follow-up code reports `c481_verified: False`.** The `phases/CLASS_COSURVIVAL_TEST/scripts/compute_survivor_sets.py` script explicitly verifies C481 and reports failure in its output JSON:

```json
{
  "a_record_count": 1579,
  "unique_survivor_sets": 1203,
  "c481_verified": false
}
```

**1579 records produce 1203 unique survivor sets = 376 collisions = 24% collision rate.** Not 0 collisions in 1575 lines.

### Three independent failure axes

**1. Value does not reproduce.** Original "0 collisions" → current 376 collisions. The 1,575-line count is also off by 4 (current: 1,579 records). Likely pre-v2.42 transcriber filter effects on the original methodology.

**2. Direction is wrong.** The claim is "essentially UNIQUE" (uniqueness). The data shows 24% collision rate (CLUSTERING). These are opposite claims. Demoting under "essentially unique" framing would mislead future readers per C476 precedent.

**3. Denominator is non-informative.** Survivor sets are subsets of ~49 instruction classes. The possible-subset space is 2^49 ≈ 5.6 × 10^14. With 1579 records drawing randomly from 10^14 space, expected collisions ≈ 0 (birthday paradox: 1579² / 2·10^14 ≈ 10^-8 probability). So "0 collisions" wouldn't be informative even if it reproduced — random data gives the same result. The observed 376 collisions actually shows clustering BELOW random expectation — the constraint claimed near-100% uniqueness but reality is more clustered than chance.

### Triple-pattern combined failure

C481 combines three previously-identified failure patterns:
- **C131-shape** (value doesn't reproduce)
- **C476-shape** (direction wrong — clustering vs uniqueness)
- **C475-shape** (sparsity denominator — 2^49 makes "0 collisions" non-informative)

---

## Why retract, not demote

Per C476 precedent (`feedback_broken_baseline_audit.md`): when surviving observation runs OPPOSITE the registered direction, demotion under original framing misleads. The substantive observation (1,203 distinct survivor patterns, clustering below random) is informationally useful but in the wrong direction relative to "essentially unique."

If the clustering observation is to be preserved at all, it should be a FRESH constraint with correct directional framing — e.g., "A records cluster into ~1200 distinct class-survivor patterns from 1579 records (~24% collision rate, indicating clustering below random expectation in 2^49 space)."

---

## Additional methodological issue: FINDINGS.md reframe

A separate failure pattern is documented in `phases/CLASS_COSURVIVAL_TEST/results/FINDINGS.md` line 164:

> **C481 VALIDATED** — 1,203 unique class patterns confirms discrimination

This is **post-hoc claim-substitution under shared headline.** The original C481 claim was specifically "0 collisions / essentially unique / DETERMINISTIC." The FINDINGS.md silently reframes "1,203 patterns (24% collision rate) = 76% uniqueness" as "discrimination confirmed = C481 VALIDATED" — a different and weaker claim labeled with the original constraint number.

The smoking gun is in the same directory: the script writes `c481_verified: false` to the JSON while the human-written FINDINGS.md says "VALIDATED."

**New methodology lesson saved:** `feedback_post_hoc_claim_substitution.md` — 5th distinct failure pattern. Catches post-hoc rescue framings in writeup layers (vs constraint registrations themselves).

The FINDINGS.md text should also be updated to reflect the actual `c481_verified: False` outcome.

---

## Downstream impact

- **C729** ("0 violations across 19,576 ATTESTED pair occurrences") — INDEPENDENT, uses attested-denominator methodology, unaffected by C481 retraction
- **C475** — already demoted; C481's relation to C475 was "C475 explains C481's uniqueness." With C481 retracted, this cross-reference becomes invalid. C475's demotion narrative noted "C475's specific 95.7% framing is sparsity-driven" — consistent picture.
- **C476** — already retracted. Cross-reference also stale.
- **C479-C480** — same 2026-01-12 SSD probe family. **AUDIT-PRIORITY** per batch-sweep recommendation below.
- **`phases/CLASS_COSURVIVAL_TEST/results/FINDINGS.md`** — should be updated to reflect actual c481_verified: False outcome.

---

## 2026-01-12 cohort batch-sweep — 3/3 audit-hit rate

The 2026-01-12 probe family now has **3/3 audit-driven action rate**:
- C475 DEMOTED (sparsity denominator)
- C476 RETRACTED (broken baseline, wrong direction)
- C481 RETRACTED (this audit — value + direction + denominator)

Per both expert consultations: this is past the threshold for one-at-a-time audits. **Batch-sweep mode justified.** Remaining 2026-01-12 candidates:
- **C478** — already AUDIT_PENDING from C476 commit
- **C479** — Survivor-Set Dimensionality (same Phase SSD family)
- **C480** — same family
- **C755, C756** — coverage-family successors

Crazy-expert's 30-40% retraction-rate prediction undershot at 3/3 = 100%. Real rate looks like systematic methodology cohort issue, not noise.

---

## Provenance

- Original probe: Phase SSD (2026-01-12)
- Follow-up validation: `phases/CLASS_COSURVIVAL_TEST/` already reported `c481_verified: False` in its JSON output but was silently reframed in FINDINGS.md as "VALIDATED"
- Audit: `phases/C481_AUDIT/INDEX.md` (2026-05-19)
- Methodology memories: `feedback_made_up_threshold_audit.md` (axis 1), `feedback_broken_baseline_audit.md` (axis 2), `feedback_denominator_choice_sparse_cooccurrence.md` (axis 3), `feedback_post_hoc_claim_substitution.md` (NEW — FINDINGS.md reframe pattern)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

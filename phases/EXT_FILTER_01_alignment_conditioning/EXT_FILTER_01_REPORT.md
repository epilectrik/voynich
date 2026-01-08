# EXT-FILTER-01: External Alignment Conditioning

**Status:** COMPLETE
**Tier:** 3 (CONDITIONING ONLY)
**Date:** 2026-01-05

---

## Section 1 - Method

### What Was Filtered

Human-track tokens were identified using the grammar classification from SID-04/SID-05:

- **Grammar tokens:** Tokens with prefixes (qo, ch, sh, ok, da, ot, ct, kc, pc, fc) or suffixes (aiin, dy, ol, or, ar, ain, ey, edy, eey)
- **Human-track tokens:** All other tokens (non-grammar residue)

### Filtering Results

| Category | Count | Percentage |
|----------|-------|------------|
| Total tokens | 121,531 | 100% |
| Grammar tokens | 104,324 | 85.8% |
| Human-track tokens | 17,207 | 14.2% |

### Confirmation

- **No grammar changes occurred** — only token removal
- **No reclassification** — used SID-05 established criteria
- **No reordering** — folio/section structure preserved

---

## Section 2 - Before vs After Tables

### Process Rhythm Metrics

| Metric | Baseline | Filtered | Δ | % Change |
|--------|----------|----------|---|----------|
| Mean intervention rate | 0.8443 | 1.0000 | +0.1557 | +18.4% |
| Std intervention rate | 0.0692 | 0.0000 | -0.0692 | -100.0%* |
| Mean LINK run length | 1.83 | 2.02 | +0.18 | +10.0% |
| Max LINK run length | 35 | 37 | +2 | +5.7% |
| Median LINK run length | 1.0 | 1.0 | 0 | 0.0% |
| Mean hazard spacing | 6.76 | 6.26 | -0.50 | -7.4% |
| CV hazard spacing | 1.466 | 1.441 | -0.03 | -1.7% |

*Std deviation drops to 0 by definition when all tokens are grammar.

### Hazard Profile Shape

| Metric | Baseline | Filtered | Δ | % Change |
|--------|----------|----------|---|----------|
| Hazard token count | 17,984 | 16,669 | -1,315 | -7.3% |
| Hazard density | 0.1480 | 0.1598 | +0.0118 | **+8.0%** |
| Phase-ordering ratio | 35.5% | 38.3% | +2.8% | **+7.9%** |

### LINK Fraction vs Safety

| Metric | Baseline | Filtered | Δ | % Change |
|--------|----------|----------|---|----------|
| LINK token count | 51,439 | 49,055 | -2,384 | -4.6% |
| LINK density | 0.4233 | 0.4702 | +0.0470 | **+11.1%** |
| LINK-hazard proximity | 0.732 | 0.744 | +0.012 | +1.6% |
| Safety margin (25th pctl) | 2.0 | 2.0 | 0 | 0.0% |

### Closed-Loop / Batch Compatibility

| Metric | Baseline | Filtered | Δ | % Change |
|--------|----------|----------|---|----------|
| Unique tokens | 12,128 | 8,539 | -3,589 | -29.6% |
| Repeat ratio | 60.9% | 62.8% | +1.9% | +3.1% |
| Circularity | 0.0142 | 0.0196 | +0.0053 | +37.5%* |
| Ending concentration | 0.281 | 0.321 | +0.040 | +14.3% |

*Only metric exceeding 25% threshold; absolute values remain tiny (0.014 → 0.020).

---

## Section 3 - Outcome Classification

### Summary Statistics

| Criterion | Count |
|-----------|-------|
| Key metrics with >25% change | 1/6 |
| Metrics collapsed (>25% decrease) | 0 |
| Metrics sharpened (>25% increase) | 1 |

### Key Metrics Evaluated

1. **Mean intervention rate:** +18.4% (below threshold)
2. **LINK density:** +11.1% (below threshold)
3. **Hazard density:** +8.0% (below threshold)
4. **Phase-ordering ratio:** +7.9% (below threshold)
5. **LINK-hazard proximity:** +1.6% (below threshold)
6. **Circularity:** +37.5% (above threshold, but absolute change 0.005)

### Outcome

**ALIGNMENT_UNCHANGED**

### Justification (Metrics-Only)

- **5/6 key metrics changed less than 25%** after human-track removal
- The single metric exceeding threshold (circularity) has negligible absolute values (0.014 → 0.020)
- All substantive alignment signals remain statistically similar:
  - Hazard density: 14.8% → 16.0%
  - LINK density: 42.3% → 47.0%
  - Phase-ordering dominance: 35.5% → 38.3%
  - LINK-hazard proximity: 73.2% → 74.4%
- Safety margin unchanged (25th percentile gap = 2.0 tokens)
- Process rhythm structure unchanged (hazard CV 1.47 → 1.44)

### What This Establishes

Prior external alignment signals (process-class compatibility, hazard profile, LINK distribution) were **properties of the executable grammar**, not artifacts of human attentional behavior.

Removing 14.2% of tokens (the human-track layer) does not collapse or substantially alter any alignment signature.

---

## Section 4 - Interpretive Boundary

This result does not imply materials, substances, instructions, meanings, or historical identification.

EXT-FILTER-01 is a conditioning pass that removes a known confound (human attentional behavior documented in SID-05) and checks whether prior external alignments survive that removal. The outcome (ALIGNMENT_UNCHANGED) confirms that:

1. Grammar-based alignment signals are robust to human-track removal
2. Human-track layer was not inflating or distorting external compatibility measures
3. Prior external phase findings (EXT-1 through EXT-7) remain valid after conditioning

This is a hygiene pass, not an interpretive phase.

---

## Files

- `ext_filter_01.py` — Analysis implementation
- `EXT_FILTER_01_REPORT.md` — This report

---

*EXT-FILTER-01 COMPLETE. Alignment unchanged. Prior external matches were grammar-driven.*

# Phase OPS-1: Folio-Level Control Signature Extraction

**Status:** COMPLETE
**Date:** 2026-01-15
**Mode:** INTERNAL OPERATIONAL ANALYSIS (NO EXTERNAL DATA)

---

## Summary Statistics

### Corpus Overview

| Metric | Value |
|--------|-------|
| Total folios analyzed | 83 |
| Total instructions | 76156 |
| Mean instructions per folio | 917.5 |
| Min instructions | 174 |
| Max instructions | 2233 |

---

## Temporal & Waiting Metrics

| Statistic | LINK Density | Mean LINK Run |
|-----------|--------------|---------------|
| Mean | 0.3756 | 1.69 |
| Std Dev | 0.0673 | 0.24 |
| Min | 0.2016 | 1.22 |
| Max | 0.5572 | 2.75 |

### Waiting Profile Distribution

| Profile | Count | Percentage |
|---------|-------|------------|
| EXTREME | 4 | 4.8% |
| HIGH | 23 | 27.7% |
| MODERATE | 50 | 60.2% |
| LOW | 6 | 7.2% |

---

## Hazard Profile

| Statistic | Hazard Density |
|-----------|----------------|
| Mean | 0.5816 |
| Std Dev | 0.0667 |
| Min | 0.4060 |
| Max | 0.7710 |

### Risk Profile Distribution

| Profile | Count | Percentage |
|---------|-------|------------|
| TIGHT_MARGIN | 41 | 49.4% |
| BALANCED | 37 | 44.6% |
| LOW_MARGIN | 5 | 6.0% |

---

## Intervention Style Distribution

| Style | Count | Percentage |
|-------|-------|------------|
| CONSERVATIVE | 12 | 14.5% |
| BALANCED | 65 | 78.3% |
| AGGRESSIVE | 6 | 7.2% |

---

## Stability Role Distribution

| Role | Count | Percentage |
|------|-------|------------|
| MAINTENANCE_HEAVY | 28 | 33.7% |
| TRANSITION_HEAVY | 34 | 41.0% |
| MIXED | 21 | 25.3% |

---

## Convergence & Recovery

### Terminal State Distribution

| State | Count | Percentage |
|-------|-------|------------|
| STATE-C | 48 | 57.8% |
| other | 32 | 38.6% |

### Restart Capability

| Metric | Value |
|--------|-------|
| Restart-capable folios | 3 |
| Percentage | 3.6% |

---

## Quality Checks

| Check | Status |
|-------|--------|
| All 83 folios present | PASS |
| No material references | PASS |
| No collapsed folios | PASS |
| Illustration invariant | PASS |
| Reproducible from grammar | PASS |
| **Overall** | **ALL PASS** |

---

## Output Files

| File | Description |
|------|-------------|
| `ops1_folio_control_signatures.json` | Complete signature vectors (JSON) |
| `ops1_folio_signature_table.csv` | Tabular format for clustering |
| `ops1_summary_report.md` | This file |

---

**"OPS-1 is complete. All internally recoverable folio-level operational information has been extracted. No additional process information is derivable from the manuscript itself without external comparison."**

---

*Generated: 2026-01-15T23:42:48.616821*

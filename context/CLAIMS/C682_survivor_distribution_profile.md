# C682: Survivor Distribution Profile

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

Under full morphological filtering (C502.a), each A record admits a **mean of 11.08 / 49 B instruction classes** (22.6%). The distribution is right-skewed: median 10, std 5.79, range 0-38. Only 1.2% of records (18/1562) eliminate all B classes entirely.

## Key Numbers

| Metric | Value |
|--------|-------|
| Records analyzed | 1,562 |
| Mean classes surviving | 11.08 / 49 (22.6%) |
| Median | 10 |
| Std | 5.79 |
| Min / Max | 0 / 38 |
| Percentiles [5,25,50,75,95] | [3, 7, 10, 15, 21] |
| Zero-class records | 18 (1.2%) |
| Mean legal tokens | 38.5 / 4,889 types (0.8%) |
| Token percentiles [5,25,50,75,95] | [6, 17, 32, 51, 92] |

## Note on C503.a Discrepancy

C503.a reported mean 6.8 classes under full morphological filtering. This analysis finds 11.08. The discrepancy likely reflects differences in record extraction methodology (this analysis uses RecordAnalyzer from voynich.py with consistent H-track, label-excluded, uncertainty-excluded processing). The kernel access sanity check (C685: 97.4% vs C503.c: 97.6%) confirms data alignment, suggesting the class counting methodology differs rather than the underlying data.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/survivor_population_profile.py` (Test 1)
- Method: Full C502.a morphological filtering per A record via RecordAnalyzer
- Extends: C502.a (filtering algorithm), C503.a (population mean)

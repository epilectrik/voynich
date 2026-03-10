# REPORT 572: A2 Forgivingness Audit (T5)

**Generated:** 2026-03-10T21:20:05.244823+00:00
**Folios analyzed:** 76 / 76 eligible

## 1. Forgivingness Index (FI)

FI = mean null DYE (M4f) per profile. Higher FI means the null model
converts random disruption into Y-gain more easily, erasing grammar advantage.

| Profile | FI | n | min | max | std |
|---------|-----|---|-----|-----|-----|
| A1_BATH_REFLUX | 0.0131 | 21 | -0.0066 | 0.0368 | 0.0132 |
| A2_SEALED_RECIRCULATION | 0.1184 | 18 | -0.0429 | 0.2982 | 0.0910 |
| A3_DISTILL_COLLECT | 0.0806 | 37 | -0.0554 | 0.1833 | 0.0531 |

## 2. DVA-DYE Decomposition

| Profile | n | M1 dV/tok | M4f dV/tok | M1 DYE | M4f DYE | DYE adv | DVA M1 | DVA M4f | YGA |
|---------|---|-----------|------------|--------|---------|---------|--------|---------|-----|
| A1_BATH_REFLUX | 21 | 0.0688 | 0.0428 | 0.1288 | 0.0131 | 0.1156 | 0.5948 | 0.3778 | 0.3278 |
| A2_SEALED_RECIRCULATION | 18 | 0.0699 | 0.0363 | 0.1260 | 0.1184 | 0.0076 | 0.8989 | 0.4758 | 0.1688 |
| A3_DISTILL_COLLECT | 37 | 0.0708 | 0.0387 | 0.1900 | 0.0806 | 0.1094 | 0.7189 | 0.3844 | 0.3745 |

## 3. Section-Profile Interaction

| Section|Profile | n | DYE pass | DYE pass% | EPV pass | EPV pass% | mean DYE adv |
|--------|---|----------|-----------|----------|-----------|--------------|
| B|A1_BATH_REFLUX | 19 | 19 | 100% | 19 | 100% | 0.1155 |
| C|A2_SEALED_RECIRCULATION | 5 | 3 | 60% | 1 | 20% | -0.0230 |
| H|A1_BATH_REFLUX | 2 | 2 | 100% | 2 | 100% | 0.1172 |
| H|A2_SEALED_RECIRCULATION | 11 | 6 | 55% | 3 | 27% | 0.0061 |
| H|A3_DISTILL_COLLECT | 14 | 13 | 93% | 12 | 86% | 0.1275 |
| S|A3_DISTILL_COLLECT | 23 | 23 | 100% | 22 | 96% | 0.0983 |
| T|A2_SEALED_RECIRCULATION | 2 | 2 | 100% | 2 | 100% | 0.0925 |

## 4. Matched-Profile Audit

### By Event Count Bin

| Bin | A2 n | A2 FI | A2 DYE adv | A2 EPV | non-A2 n | non-A2 FI | non-A2 DYE adv | non-A2 EPV |
|-----|------|-------|------------|--------|----------|-----------|----------------|------------|
| 1-2 | 11 | 0.1322 | -0.0003 | 0.4624 | 23 | 0.0623 | 0.1202 | 0.9413 |
| 3-5 | 4 | 0.0707 | 0.0630 | 0.8000 | 20 | 0.0559 | 0.1117 | 0.9700 |
| 6-10 | 3 | 0.1314 | -0.0371 | 0.5500 | 14 | 0.0509 | 0.0964 | 0.9714 |
| 11+ | 0 | 0.0000 | 0.0000 | 0.0000 | 1 | -0.0048 | 0.1260 | 1.0000 |

### By Eligibility Class

| Class | A2 n | A2 FI | A2 DYE adv | non-A2 n | non-A2 FI | non-A2 DYE adv |
|-------|------|-------|------------|----------|-----------|----------------|
| demand_eligible | 1 | 0.0885 | 0.0741 | 7 | 0.0183 | 0.1248 |
| demand_strong | 1 | 0.1204 | 0.0003 | 16 | 0.0519 | 0.0957 |
| fallback_only | 6 | 0.0928 | 0.0234 | 21 | 0.0513 | 0.1113 |
| sparse_close | 10 | 0.1366 | -0.0077 | 14 | 0.0873 | 0.1238 |

## 5. Confound Tests

| Profile | n | mean n_events | F1 | F2 | F3 | F4 | F5 | DVA(M1) |
|---------|---|---------------|-----|-----|-----|-----|-----|---------|
| A1_BATH_REFLUX | 21 | 4.9 | 1.229 | 1.091 | 1.247 | 0.486 | 0.855 | 0.5948 |
| A2_SEALED_RECIRCULATION | 18 | 2.8 | 0.866 | 0.977 | 0.904 | 0.587 | 0.969 | 0.8989 |
| A3_DISTILL_COLLECT | 37 | 3.7 | 1.047 | 0.998 | 0.953 | 0.370 | 1.027 | 0.7189 |

## 6. Mechanistic Test (Entry Deviation)

Mean |state deviation| at CLOSE line entry. Smaller values mean the system
is closer to equilibrium (0.5) when disruption begins.

| Profile | mean entry dev | min | max | std | n |
|---------|----------------|-----|-----|-----|---|
| A1_BATH_REFLUX | 0.0728 | 0.0294 | 0.1025 | 0.0175 | 21 |
| A2_SEALED_RECIRCULATION | 0.0812 | 0.0241 | 0.1324 | 0.0326 | 18 |
| A3_DISTILL_COLLECT | 0.0833 | 0.0000 | 0.1315 | 0.0245 | 37 |

## 7. Interpretation

Highest FI (null forgivingness): A2_SEALED_RECIRCULATION at FI=0.1184. Lowest FI: A1_BATH_REFLUX at FI=0.0131. DYE advantages: A1=0.1156, A2=0.0076, A3=0.1094. Entry deviation: A1=0.0728, A2=0.0812, A3=0.0833. CONFIRMED: A2 has the highest null forgivingness — random disruption converts to Y most easily in A2 folios, washing out the grammar advantage.

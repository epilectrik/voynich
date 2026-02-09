# C908: MIDDLE-Kernel Correlation

**Tier:** 2 | **Scope:** B | **Status:** CLOSED

---

## Statement

MIDDLEs correlate significantly with paragraph-level kernel profiles. **55% of MIDDLEs** show statistically significant correlation with kernel composition (p < 0.01), establishing that MIDDLE selection encodes energy/stability requirements.

---

## Evidence

### K-Enriched MIDDLEs (Energy Operations)

| MIDDLE | K-ratio | p-value | Interpretation |
|--------|---------|---------|----------------|
| eck | 1.61x | <0.0001 | High energy |
| ck | 1.60x | <0.0001 | High energy |
| lk | 1.55x | <0.0001 | High energy |
| k | 1.53x | <0.0001 | Core energy operator |
| ek | 1.47x | <0.0001 | Extended energy |
| ke | 1.36x | <0.0001 | Sustained energy |

### K-Depleted MIDDLEs (Low-Energy Operations)

| MIDDLE | K-ratio | p-value | Interpretation |
|--------|---------|---------|----------------|
| eod | 0.53x | <0.0001 | Passive/settling |
| eeo | 0.55x | <0.0001 | Deep stability |
| eed | 0.57x | <0.0001 | Completion |
| eo | 0.66x | <0.0001 | Transition to stability |
| ed | 0.76x | <0.0001 | Light settling |

### H-Enriched MIDDLEs (Phase Monitoring)

| MIDDLE | H-ratio | p-value | Interpretation |
|--------|---------|---------|----------------|
| opch | 1.55x | <0.0001 | Monitoring |
| sh | 1.42x | <0.0001 | Phase check |
| ch | 1.41x | <0.0001 | Phase check |
| pch | 1.36x | 0.0015 | Monitoring |

### E-Enriched MIDDLEs (Stability Anchoring)

| MIDDLE | E-ratio | p-value | Interpretation |
|--------|---------|---------|----------------|
| eed | 1.62x | <0.0001 | Deep stability |
| eeo | 1.45x | <0.0001 | Extended stability |
| ed | 1.33x | <0.0001 | Light stability |
| eey | 1.26x | <0.0001 | Stable terminal |
| e | 1.22x | <0.0001 | Core stability |

---

## Functional Clusters

1. **k-cluster** (energy): k, ck, eck, ek, ke, lk, eek
2. **e-cluster** (stability): e, ed, eed, eo, eeo, eod, eey
3. **h-cluster** (monitoring): ch, sh, pch, opch, d

---

## Provenance

- **Phase:** MIDDLE_SEMANTIC_MAPPING (2026-02-04)
- **Method:** Paragraph-level kernel profile classification, chi-square enrichment testing
- **Sample:** 478 paragraphs, 53 MIDDLEs with n≥50

---

## Related Constraints

- C103-C105 (Kernel positional roles)
- C893 (Kernel signature predicts operation type)
- C777 (FL State Index)
- F-BRU-011 (Three-tier MIDDLE structure)

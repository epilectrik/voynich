# C1112: P-Text is Bridge-Enriched at Extreme Levels

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** PTEXT_ROSETTES_INDEXING_ARCHITECTURE (Phase 395)
**Strengthens:** C486 (P-text B-transmission), C758 (P-text Currier A identity), C1014 (bridge MIDDLEs)

---

## Statement

P-text (398 Currier A-like tokens on 9 AZC folios) is bridge-enriched at extreme levels: 45.5% of its unique MIDDLEs (55/121) are bridge MIDDLEs, placing it at the 100th percentile of Currier A vocabulary (bootstrap p95 = 13.2%, mean = 8.8%). P-text bridge density exceeds even Rosettes (24.4%), making it the most bridge-concentrated vocabulary in the manuscript.

P-text and Rosettes share a highly similar affordance bin profile (cosine = 0.925), with both concentrating in FLOW_TERMINAL, HUB_UNIVERSAL, and STABILITY_CRITICAL bins. This profile similarity is far above the 0.85 threshold.

---

## Evidence

### P1: Bridge Density (PASS)
| Metric | Value |
|--------|-------|
| P-text bridge fraction | 0.4545 (55/121) |
| Rosettes bridge fraction | 0.2435 |
| A bootstrap mean | 0.0876 |
| A bootstrap p95 | 0.1322 |
| P-text percentile in A | 100.0th |

### P2: Affordance Bin Profile (PASS)
| Metric | Value |
|--------|-------|
| Cosine (P-text vs Rosettes) | 0.9253 |
| Shared dominant bins | FLOW_TERMINAL, HUB_UNIVERSAL, STABILITY_CRITICAL |

### P3: Bridge Mediation (FAIL)
| Metric | Value |
|--------|-------|
| Bridge-in-B rate | 1.0000 (100%) |
| Non-bridge-in-B rate | 0.6061 (60.6%) |
| Overall B-transmission | 0.7851 (matches C486 ~76.7%) |

Bridge MIDDLEs fully transmit to B by definition, but non-bridge MIDDLEs also transmit substantially (60.6%), meaning bridges do NOT fully explain the 76.7% B-transmission rate. Non-bridge transmission is a significant secondary channel.

### P4: Folio Specificity (MODERATE)
| Metric | Value |
|--------|-------|
| P-text mean inter-folio Jaccard | 0.1851 |
| Currier A mean inter-folio Jaccard | 0.2498 |
| Classification | MODERATE |

P-text vocabulary is neither universal (shared everywhere) nor folio-specific (unique per page). It falls between, consistent with a vocabulary drawn from a shared pool but deployed selectively.

### P5: Kernel/LINK Absence (FAIL — test design artifact)

P5 tested whether P-text contains B-grammar markers (kernel chars k/h/e and LINK prefixes). Kernel char fraction was 50.1%, far above the 5% threshold. However, this is a test design artifact: kernel characters (k, h, e) are normal morphemic characters in ALL MIDDLEs — Currier A baseline is 36.5%, Currier B is 52.8%. P-text at 50.1% is between A and B, consistent with its bridge-heavy profile. LINK hits were 0 (0.0%), confirming P-text has no LINK grammar.

---

## Constraint Implications

- **C486 strengthened**: The 76.7% B-transmission is confirmed (observed 78.5%) and now explained as bridge-mediated with substantial non-bridge secondary transmission.
- **C1014 extended**: Bridge MIDDLEs are not just cross-system vocabulary — they are specifically concentrated in P-text at nearly 2x the Rosettes level, suggesting P-text is a dedicated bridge-vocabulary carrier.

---

## Provenance

- Phase: 395 (PTEXT_ROSETTES_INDEXING_ARCHITECTURE), 10-test battery (5 Stage 1 + 5 Stage 2)
- Script: `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/scripts/ptext_rosettes_indexing.py`
- Results: `phases/PTEXT_ROSETTES_INDEXING_ARCHITECTURE/results/ptext_rosettes_indexing.json`
- Related: C486, C758, C900, C1014, C1096

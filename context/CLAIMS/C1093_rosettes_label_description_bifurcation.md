# C1093: Rosettes Label-Description Bifurcation

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Extends:** C301 (AZC is HYBRID), C305 (AZC labeling signature)
**Relates to:** C233 (A lines are atomic), C525 (label morphological stratification)

---

## Statement

f85v2 contains both A-like single-token label regions (87 tokens across 8 regions: B1, B2, B3, M1, M2, U1, U2, W1) and B-like continuous-text description regions (8 regions: C2, D1, M3, N1, N2, U3, V1, V2). Label regions have 68-100% single-token lines and use ok/ot prefix dominance. Description regions have 23-37 tokens per line and use B-like sequential text with hub role distributions. This confirms AZC hybrid architecture (C301) at region level within a single folio page.

---

## Evidence

### Region Classification

| Region | Tokens | Lines | Single-tok% | Type |
|--------|--------|-------|-------------|------|
| B1 | 29 | 22 | 68% | LABEL |
| B2 | 7 | 7 | 100% | LABEL |
| B3 | 2 | 2 | 100% | LABEL |
| M1 | 8 | 7 | 86% | LABEL |
| M2 | 23 | 21 | 90% | LABEL |
| U1 | 8 | 8 | 100% | LABEL |
| U2 | 7 | 7 | 100% | LABEL |
| W1 | 3 | 3 | 100% | LABEL |
| C2 | 33 | 1 | 0% | DESCRIPTION |
| N1 | 23 | 1 | 0% | DESCRIPTION |
| N2 | 37 | 1 | 0% | DESCRIPTION |
| V1 | 30 | 1 | 0% | DESCRIPTION |
| V2 | 32 | 1 | 0% | DESCRIPTION |

### Label Properties (A-like)

- 87 total label tokens, 49 unique MIDDLEs
- 9 MIDDLEs NOT IN B body text (iino, lashal, lcpheek, opaiiino, opar, opashcfh, opdar, oped, opydsh)
- 29 labels (34%) exclusive to Rosettes (appear nowhere else in manuscript)
- Single-token-per-line structure matches C233 (A lines are atomic)

### Description Properties (B-like)

- Continuous text with hub role distributions
- NORTH (N1+N2): 71% hazard, K=18
- VERT (V1+V2): 73% hazard, K=23
- CENTER (C2): 62% hazard, TARGET-dominant

---

## Interpretation

f85v2 instantiates the AZC hybrid architecture at region scale: label regions function as an A-like vocabulary index (single entries naming operational elements), while description regions function as B-like procedural text (continuous sequences with hub role structure). The coexistence on a single page confirms that the A/B distinction is a functional mode, not a system boundary.

---

## Method

- Region classification by single-token-line rate (>50% = LABEL, else DESCRIPTION)
- Label morphological extraction via Morphology.extract()
- Description structural profiling via BFolioDecoder.analyze_token()
- Cross-reference against full A, B, AZC corpora

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_rosette_labels.py`

---

## Verdict

**LABEL_DESCRIPTION_BIFURCATION**: f85v2 contains both A-like labels (87 tokens, 8 regions) and B-like descriptions (8 regions) on the same page, confirming AZC hybrid architecture at region level.

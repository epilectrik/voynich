# C1129: P-Text/Rosettes Unified Indexing (Revalidated)

**Tier:** 2 | **Scope:** GLOBAL | **Status:** VALIDATED
**Phase:** 403 (PTEXT_ROSETTES_INTEGRATION_REVALIDATION)

## Statement

P-text and Rosettes participate in a unified vocabulary-mediated paragraph-level indexing system. Both vocabularies share significant MIDDLE overlap (Jaccard=0.137, 100th percentile of A bootstrap), co-target the same B paragraphs (Spearman rho=0.576, p<<0.001), and their union predicts B paragraph header affordance profiles (cosine=0.876).

## Evidence

### Synthesis: UNIFIED_CONFIRMED (4/4 PASS)

Formula: R1 + R3 + (I2_original | R4) + R5

| Test | Verdict | Key Metric |
|------|---------|-----------|
| R1 (Bridge density) | PASS | P-text 45.5%, Rosettes 21.5%, both >> A p95 12.4% |
| R3 (Vocabulary overlap) | PASS | Jaccard=0.137, 36 shared MIDDLEs, 100th pctl of A |
| R4 (Paragraph co-tracking) | PASS | Spearman rho=0.576, p<<0.001, 552 paragraphs |
| R5 (Union prediction) | PASS | Cosine=0.876 (unified > P-text 0.810, Rosettes 0.813 alone) |

### Diagnostic Findings

- **Grammar divergence (R2):** P-text is A-like (PREFIX cosine 0.964 to A) while Rosettes are AZC-like (cosine 0.908 to AZC). PREFIX cosine between P-text and Rosettes is only 0.493. Unified vocabulary but divergent grammar.
- **Section mediation (R6):** Shared vocabulary is section-general, not T-specific. 97.2% of 36 shared MIDDLEs appear in Section S, 94.4% in B and H, 75.0% in T.
- **Specificity (R7):** P-text is more specific in B folio targeting (intra-group top-5 overlap 0.253) than Rosettes (0.322). Cross-group overlap is low (0.101).

## Relationship to Phase 395

Phase 395 established C1113 (UNIFIED_INDEXING) using old EVA-based Rosettes data. Phase 403 revalidates with corrected ZL data. Key changes:
- Rosettes MIDDLEs: 308 (old) → 177 (corrected)
- Jaccard: 0.210 (old) → 0.137 (corrected) — lower but still far above chance
- Spearman rho: 0.642 (old) → 0.576 (corrected) — slightly lower, still strongly significant
- Cosine: 0.949 (old) → 0.876 (corrected) — lower but well above 0.70 threshold
- Verdict: UNIFIED_INDEXING (old) → UNIFIED_CONFIRMED (corrected) — replicates

## Key Constraints

- C1112: P-text bridge enrichment (45.5%, 100th percentile of A)
- C1124: Rosettes bridge enrichment (3.05x, 21.5%)
- C1125: Rosettes universal Section T correlation
- C758: P-text is linguistically A (PREFIX cosine 0.97)
- C1127: Rosettes AZC-like grammar
- C384: No token-level A-B lookup (indexing is statistical, not addressable)

## Provenance

- Supersedes: C1113 (Phase 395, deleted in v4.10.10)
- Data: data/rosettes_annotated.json (Rosettes), Transcript.azc() (P-text)
- Script: phases/ROSETTES_SYSTEM_REVALIDATION/scripts/ptext_rosettes_integration.py
- Results: phases/ROSETTES_SYSTEM_REVALIDATION/results/ptext_rosettes_integration.json

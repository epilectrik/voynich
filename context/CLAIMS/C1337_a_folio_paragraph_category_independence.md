# C1337: A Folio Paragraph Category Independence

**Tier:** 2
**Scope:** A (all sections)
**Phase:** A_PARAGRAPH_CATEGORY_ARCHITECTURE (468)

## Constraint

A paragraph category types are NOT organized within folios. Consecutive paragraphs within a folio are no more categorically similar than non-consecutive pairs (consecutive JSD 0.104 vs random JSD 0.096, permutation p=0.850). The first paragraph has no distinct category profile (first-rest JSD = 0.004, max enrichment ratio 1.25x). This contrasts sharply with B blocks, where adjacent blocks are categorically similar (C1326) and block 0 has MARKING enrichment (C1332).

## Evidence

From a_paragraph_category_architecture.py test A4 (36 folios with 3+ eligible paragraphs):

**Consecutive vs random-pair JSD:**

| Metric | Value |
|--------|-------|
| Consecutive mean JSD | 0.104 |
| Non-consecutive mean JSD | 0.096 |
| Gap | +0.008 (wrong direction) |
| MW z | 0.23, p = 0.761 |
| Permutation p | 0.850 |

**First-paragraph distinctness (cf. C1332):**

| Category | First-para | Rest | Ratio |
|----------|-----------|------|-------|
| FLOW | 19.8% | 15.9% | 1.25x |
| TRANSITION | 20.0% | 17.5% | 1.15x |
| MARKING | 7.0% | 6.2% | 1.14x |
| STAGING | 20.2% | 23.1% | 0.87x |
| THERMAL | 14.4% | 19.7% | 0.73x |

No category exceeds 1.5x enrichment. JSD between first and rest is 0.004 (negligible).

**Section breakdown:**

| Section | n folios | Consec JSD | Random JSD | Gap |
|---------|----------|-----------|------------|-----|
| H | 20 | 0.108 | 0.101 | +0.007 |
| P | 13 | 0.066 | 0.089 | -0.023 |
| T | 3 | 0.221 | 0.096 | +0.125 |

Section P shows consecutive < random but n=13 is too small to be conclusive.

## Interpretation

A paragraph types within a folio are categorically independent — their order carries no structural information. This confirms C240 (NON_SEQUENTIAL_CATEGORICAL_REGISTRY) extends to paragraph-level category organization, not just token/line level.

The contrast with B is striking: B blocks within a folio are categorically similar to neighbors (C1326, mean adjacent JSD 0.071) and block 0 is MARKING-enriched (C1332, 2.48x). A paragraph types are randomly ordered and paragraph 0 is unremarkable. This asymmetry is consistent with A being a registry (unordered catalog) while B is a program (sequenced execution).

## Provenance

- a_paragraph_category_architecture.json: test A4
- Confirms: C240 (NON_SEQUENTIAL — extends to paragraph category organization)
- Contrasts with: C1326 (B cross-block category continuity), C1332 (B block-0 marking enrichment)
- Relates to: C1040 (folio compatibility coherence — MIDDLE level, not category level)

## Status

CONFIRMED — A paragraph category types are folio-independent (no sequential organization, no first-paragraph distinctness).

# C1130: Ring Text Forbidden Compliance Without Transition Grammar

**Tier:** 2 | **Scope:** Rosettes | **Status:** VALIDATED
**Phase:** 402 (ROSETTES_SYSTEM_REVALIDATION), S5 test

## Statement

Ring text across all 9 rosettes obeys B's 17 forbidden MIDDLE pairs (C783): 0 violations in 277 MIDDLE bigrams. However, transition structure is effectively random: bigram entropy 7.92 bits (vs B corpus ~0.41 bits per C389), self-transition rate 2.89%, 252/277 bigrams unique. Ring text respects hard constraints (forbidden topology) but lacks soft constraints (positional/transition grammar).

## Evidence

| Metric | Ring Text | B Corpus | Interpretation |
|--------|-----------|----------|----------------|
| Forbidden violations | 0/277 | 0 (by definition) | Full compliance |
| Bigram entropy | 7.92 bits | ~0.41 bits (C389) | ~19x higher — effectively random |
| Self-transition rate | 2.89% | ~15% (structured) | No self-repetition preference |
| Unique bigrams | 252/277 (91%) | ~30% typical | Near-maximal diversity |

Data source: corrected ZL transcription (`data/rosettes_annotated.json`), all 9 rosettes' ring sub-regions.

## Interpretation

Ring text was composed within the MIDDLE compatibility space (it avoids the 17 forbidden pairs) but without B's execution-layer transition grammar. This is consistent with AZC-layer material (C1127) that draws from the same vocabulary substrate as B but operates outside the execution framework. The forbidden pairs are probably fundamental incompatibilities in the vocabulary itself (C475: 95.7% of MIDDLE pairs are incompatible), not learned transition rules that ring text deliberately follows.

## Relationship to Other Constraints

- **C1127** (AZC-like grammar profile): Complementary — C1127 captures static compositional profile (grammar coverage, kernel density, morphological cosine), C1130 captures sequential/transition structure
- **C783** (forbidden pair asymmetry): C1130 extends C783's scope to rosettes ring text
- **C757** (AZC zero kernel/LINK): Consistent — material outside execution layer has no reason for structured transitions
- **C1126** (metalayer confirmed): Consistent — a metalayer respects hard structural constraints without implementing execution grammar

## Provenance

- Phase 402, test S5 (Sequential Grammar)
- Supersedes: C1114 (ring text construction compliance, deleted v4.10.10)
- Supersedes: C1115 (ring text operational divergence, deleted v4.10.10)

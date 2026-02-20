# C1134: Section Specificity Is Frequency-Modulated

**Tier:** 2
**Status:** Active
**Scope:** B, A->B
**Phase:** 406 (CROSS_SYSTEM_VOCABULARY_FLOW)
**Resolves paradox:** C1049 (shared vocabulary section-universal) vs C909 (96% section-specific)

## Finding

Section-specificity in Currier B emerges primarily through **frequency modulation** of section-universal shared vocabulary, not through section-specific vocabulary additions.

Shared/PP MIDDLEs (94.1% of B tokens) appear in all sections (type-universal, Herfindahl 0.701 per C1049) but at section-specific token frequencies. This frequency modulation accounts for 74% of total between-section JS divergence.

B-exclusive MIDDLEs (5.8% of B tokens) are maximally section-specific (pairwise JS = 0.847, Jaccard distance 0.944) but their tiny token share means they contribute minimally to actual section discrimination.

| Vocabulary Partition | Token Share | Mean Pairwise JS | Contribution to Section Divergence |
|---------------------|-------------|------------------|------------------------------------|
| Shared/PP | 94.1% | 0.124 | 74% (JS_PP / JS_ALL = 0.124/0.167) |
| B-exclusive | 5.8% | 0.847 | Token-diluted despite extreme specificity |
| All | 100% | 0.167 | 100% (reference) |

Pairwise section detail (major B sections S, B, H, C):

| Pair | PP JS | B-excl JS | All JS | PP Token Share |
|------|-------|-----------|--------|----------------|
| S-B | 0.120 | 0.730 | 0.154 | 94.2% |
| S-H | 0.095 | 0.812 | 0.143 | 93.2% |
| S-C | 0.094 | 0.861 | 0.144 | 93.2% |
| B-H | 0.155 | 0.832 | 0.192 | 95.1% |
| B-C | 0.189 | 0.896 | 0.226 | 95.5% |
| H-C | 0.090 | 0.950 | 0.145 | 93.5% |

B-C pair shows greatest PP divergence (0.189); H-C pair shows greatest B-exclusive divergence (0.950).

## Mechanism

Sections use the same shared vocabulary but at different rates:
- **Frequency modulation** carries most discriminating signal (74% of total JS)
- **Presence/absence** carries less (PP Jaccard distance 0.547, but JS/Jaccard_dist ratio only 0.227)
- **B-exclusive vocabulary** is section-diagnostic per-type but token-negligible

This resolves the C1049/C909 paradox: vocabulary is type-universal but frequency-specific.

## Evidence

- 4 major B sections (S, B, H, C) with >= 1,000 tokens each
- JS divergence computed on MIDDLE frequency profiles per section
- Decomposition: PP-only vs B-exclusive-only vs all-vocabulary JS

## Provenance

- Source: Phase 406, Tests A1 + A2
- Resolves: C1049 (universal) + C909 (specific) apparent contradiction
- Related: C941 (section exhausts organizing dimension), C552 (section role profiles)

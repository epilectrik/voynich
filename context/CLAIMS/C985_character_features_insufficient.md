# C985: Character-Level Features Insufficient for Discrimination

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

Logistic regression on 245 character-level features (character presence, bigrams, positional features, length) achieves AUC = 0.71 for predicting MIDDLE compatibility, compared to AUC = 0.93 for spectral embedding of the compatibility graph. The 29% gap is structural: discrimination requires information that individual characters do not encode. PREFIX enrichment is 3.92× within-PREFIX vs cross-PREFIX, but PREFIX-spectral alignment is NONE (ARI = 0.006, NMI = 0.013).

## Evidence

### Character Feature Prediction (T4)

| Method | AUC | Features |
|--------|-----|----------|
| Character-level logistic regression | 0.71 | 245 (chars, bigrams, position, length) |
| Spectral embedding (K=256) | 0.93 | Graph structure |
| **Gap** | **0.22** | **Structural information** |

### PREFIX Block Structure (T3)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| PREFIX enrichment | 3.92× | Compatibility enriched within same PREFIX |
| PREFIX-spectral ARI | 0.006 | NO alignment between PREFIX groups and spectral communities |
| PREFIX-spectral NMI | 0.013 | Near zero mutual information |
| Spectral modularity (k=8) | Q = 0.037 | Very weak community structure |

### Information Content (T4)

| Metric | Value |
|--------|-------|
| Morphological PCA k_95 | 101 independent features |
| Mean row entropy | 0.133 bits |
| Mean row-pair MI | 0.011 bits |
| Description length per row | 97.2 bits |

### Interpretation

1. Characters partially predict compatibility (AUC 0.71 > random 0.50) — morphological similarity matters
2. But 29% of discriminability requires non-character information — compatibility is not reducible to string similarity
3. PREFIX creates soft compatibility blocks (3.92× enrichment) but these blocks DON'T align with the graph's spectral communities
4. Consistent with C120/C171 semantic ceiling: individual morphological features don't determine function

## Provenance

- T3 (structural decomposition), T4 (morphological derivation)
- Reinforces C120 (semantic ceiling) and C171 (morphology ≠ semantics)
- Consistent with C984 (independent features insufficient) — the features that DO determine compatibility are structured and correlated

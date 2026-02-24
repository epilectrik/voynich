# C1233 - Cross-Line Independence

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

Cross-line FL regression (40.7%), suffix mode alternation (45.7%), and prefix channel switching (41.7%) are statistically independent AND near-random. Mode transition entropy = 97.8% of maximum. Three-way chi-squared = 23.56 (df=17, independent). Cramer's V = 0.12. Mutual information < 1% across all pairwise combinations. Cross-line sequencing is unstructured; each line is an independently composed extraction pass.

## Evidence

### Three-way independence (3D contingency tensor: FL x MODE x CHANNEL)

| Test | chi2 | df | Result |
|------|------|----|--------|
| Three-way | 23.56 | 17 | Independent (p>0.05) |
| FL x MODE | 7.98 | — | Independent |
| FL x CHANNEL | 0.35 | — | Independent |
| MODE x CHANNEL | 8.55 | — | Barely dependent |

### Mode transition matrix

| From \ To | Mode A | Mode B |
|-----------|--------|--------|
| Mode A | 43.8% | 56.2% |
| Mode B | 39.8% | 60.2% |

Base rates: P(A)=43%, P(B)=57% — transition probabilities track base rates.

### Run length analysis

| Mode | Observed mean run | Expected (random) |
|------|-------------------|-------------------|
| A | 1.61 | 1.76 |
| B | 2.01 | 2.32 |

Run lengths match random expectations.

### Key observations

1. **1992 lines** from 591 paragraphs across 82 folios analyzed
2. **Mode transition entropy** = 97.8% of maximum — near-random sequencing
3. **Cramer's V** = 0.12 — negligible association
4. **Mutual information** < 1% across all pairwise combinations
5. **No stereotyped bigram sequences** — highest PMI bigram: or->aiin at count 42

## Interpretation

Lines within a paragraph are not sequentially programmed. Each line is an independently composed extraction pass that does not depend on its predecessor's mode, channel, or FL status. The paragraph is a parallel collection of independent operations, not a sequential pipeline.

## Related constraints

- C670: Adjacent-line vocabulary null
- C673: CC sequential independence
- C972: Cross-line independence stronger than random Markov
- C966: No cross-line memory

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/loop_deep_analysis.py` (Tests 4, 5)
- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/cycle_tensor_analysis.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/loop_deep_analysis.json`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/cycle_tensor_analysis.json`

# C619: Unique MIDDLE Behavioral Equivalence

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** UNIQUE_VOCABULARY_ROLE

## Statement

Tokens carrying unique MIDDLEs are behaviorally near-identical to tokens carrying shared MIDDLEs within the UN population. Transition divergence is statistically significant but functionally negligible (successor V=0.070, predecessor V=0.051). The only systematic difference: unique MIDDLE tokens are more likely to neighbor other UN tokens (54.6% vs 47.5%). Unique MIDDLEs are interchangeable with shared UN vocabulary — H1 (lexical tail) is confirmed over H2 (parametric specialization) and H3 (functional specialization).

## Evidence

### Successor Role Distribution (Within UN)

| Role | Unique MIDDLE | Shared MIDDLE | Delta |
|------|--------------|---------------|-------|
| EN | 25.8% | 30.6% | -4.8 pp |
| AX | 17.4% | 15.7% | +1.7 pp |
| FQ | 9.5% | 13.3% | -3.8 pp |
| FL | 4.0% | 4.6% | -0.6 pp |
| CC | 1.8% | 2.9% | -1.1 pp |
| UN | 41.5% | 32.9% | +8.6 pp |

Chi-squared: chi2=29.22, p=0.000021, dof=5, V=0.070

The only notable difference: unique MIDDLE UN tokens are followed by UN 41.5% of the time (vs 32.9%) — they cluster in UN-dense neighborhoods.

### Predecessor Role Distribution (Within UN)

Chi-squared: chi2=15.60, p=0.008080, dof=5, V=0.051. Same pattern: more UN predecessors (40.1% vs 33.5%).

### EN-Predicted UN Subset

Within the EN-predicted UN population, unique vs shared transition divergence remains weak: chi2=13.94, p=0.016, V=0.076.

### Context Signatures

| Metric | Unique MIDDLE UN | Shared MIDDLE UN |
|--------|-----------------|-----------------|
| Top bigram | UN->UN (18.9%) | UN->UN (12.7%) |
| UN-neighbor rate | 54.6% | 47.5% |

Unique MIDDLE tokens are embedded in UN-dominant contexts but the bigram distributions are qualitatively identical — same top-10 bigrams in the same order.

### Folio Complexity Coupling

| Metric | rho | p |
|--------|-----|---|
| Unique count vs token count | +0.730 | <0.001 *** |
| Unique count vs TTR | -0.280 | 0.011 * |
| Unique density vs TTR | +0.491 | <0.001 *** |
| Unique density vs UN proportion | +0.740 | <0.001 *** |
| Unique density vs LINK density | -0.358 | 0.001 *** |
| Unique density vs hazard density | -0.179 | 0.107 n.s. |

Unique density is essentially a proxy for UN proportion (rho=+0.740).

### Section and REGIME Concentration

Section predicts unique density (Kruskal-Wallis H=20.50, p=0.000134): section B lowest (2.14%), T highest (5.29%).

REGIME does NOT predict unique density (H=4.18, p=0.243).

## Hypothesis Verdict

| Hypothesis | Prediction | Observed | Verdict |
|------------|-----------|----------|---------|
| H1: Lexical tail | Unique = shared transitions within UN | V=0.070 (negligible) | SUPPORTED |
| H2: Parametric specialization | Unique = distinct transition targets | No distinct targets | REJECTED |
| H3: Functional specialization | Unique in different positions/contexts | Weak position shift only | REJECTED |

## Related

C506.b, C531, C535, C610, C612, C618

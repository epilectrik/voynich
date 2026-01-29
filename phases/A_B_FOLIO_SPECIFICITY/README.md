# A_B_FOLIO_SPECIFICITY

**Status:** COMPLETE | **Constraints:** C734-C739 | **Scope:** A<>B

## Objective

Determine whether A folios serve specific B folios (routing architecture) or all A folios contribute uniformly to B execution (flat relationship). For each of 114 A folios, compute its C502.a survivor set, then measure how well it covers each of 82 B folios' actual vocabulary.

## Method

One script performing 9 analyses on a 114x82 coverage matrix:

- T1: Coverage matrix statistics (means, ranges, extremes)
- T2: Variance decomposition (A effect vs B effect vs residual)
- T3: A-folio specificity ratio (per-A variance vs B-only baseline)
- T4: A-folio clustering (hierarchical, Ward's method, ANOVA)
- T5: Best-match specificity (per-B-folio best A folio lift)
- T6: Coverage gap analysis (ceiling - floor per B folio)
- T7: Union coverage (greedy A folio accumulation)
- T8: Pool size vs coverage correlation
- T9: Shared vs unique B vocabulary partition

C502.a filtering: for each A folio, extract PP pool (MIDDLEs, PREFIXes, SUFFIXes). A B token is legal if its MIDDLE is shared with the A pool, AND its PREFIX (if any) is shared, AND its SUFFIX (if any) is shared.

## Key Findings

**The A-B relationship is a routing architecture, not flat.** A folio identity explains 72% of coverage variance. Every B folio has a strongly preferred A folio (all 82 show lift > 1.5x). Coverage is low (mean 26.1%) and A-dominated.

**Pool size is the primary driver** (rho=0.85). Larger A PP pools produce proportionally more legal B tokens. The relationship is mostly quantitative (how many MIDDLEs) with a secondary qualitative component (which MIDDLEs).

**B vocabulary partitions into three accessibility tiers:** B-exclusive (34.4%, never legal under any A folio), narrow-access (33.9%, legal under 1-10 A folios), and broad-access (31.7%, legal under 11+ A folios). Zero tokens are universally legal.

**A folios cluster into ~6 groups** by coverage profile. One dominant standard cluster (62 folios, coverage ~23%) and 5 smaller specialized groups including a high-coverage cluster (17 folios, coverage ~39%).

**Union ceiling is ~85%.** Even combining all 114 A folios, B folio coverage does not reach 95%. The ~15-35% gap represents B's autonomous grammar.

## Test Results

| Test | Key Metric | Result |
|------|-----------|--------|
| T1: Coverage matrix | Mean 0.261, range 0.026-0.793 | LOW coverage |
| T2: Variance decomposition | A=72.0%, B=18.1%, residual=9.9% | A-DOMINATED |
| T3: Specificity ratio | 1.544x null | ROUTING |
| T4: Clustering | k=6, F=19.90, p<0.001, corr=0.648 | CLUSTERED |
| T5: Best-match lift | All 82 B folios > 1.5x, mean 2.43x | SPECIFIC |
| T6: Coverage gap | Mean gap 0.533 | LARGE |
| T7: Union coverage | Median 95% threshold unreachable | CEILING ~85% |
| T8: Pool size | rho=0.85, p=5e-33 | DOMINANT |
| T9: Accessibility | 0% universal, 34.4% never-legal | PARTITIONED |

## Data Summary

| Metric | Value |
|--------|-------|
| A folios | 114 |
| B folios | 82 |
| B token types with morphology | 4,889 |
| A PP pool size (median) | 34 |
| A legal set size (median) | 544 |
| B folio vocab size (median) | 168 |
| Coverage matrix entries | 9,348 |
| B tokens universally legal | 0 |
| B tokens never legal | 1,684 (34.4%) |
| B tokens with any access | 3,205 (65.6%) |
| Median B token accessibility | 3 A folios |

## Scenario Outcome

This phase was designed with two scenarios:
- **FLAT:** All A folios cover all B folios roughly equally
- **ROUTING:** A folios serve specific B folio subsets

**Result: ROUTING.** A folio identity dominates coverage variance (72%), every B folio has a strongly preferred A folio (lift > 1.5x), and A folios cluster into ~6 groups. The routing is primarily quantitative (pool size rho=0.85) with secondary qualitative structure.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `scripts/ab_specificity.py` | T1-T9 | `results/ab_specificity.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C734 | A-B Coverage Architecture | Mean 26.1%, A explains 72% variance, routing architecture |
| C735 | Pool Size Coverage Dominance | rho=0.85 pool size to coverage |
| C736 | B Vocabulary Accessibility Partition | 0% universal, 34.4% never-legal, tripartite |
| C737 | A-Folio Cluster Structure | 6 clusters, correlation 0.648, specificity 1.544x |
| C738 | Union Coverage Ceiling | ~85% max with all A folios, 95% unreachable |
| C739 | Best-Match Specificity | All B folios lift > 1.5x, mean 2.43x |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP classification)

## Cross-References

- C502.a (three-axis filtering): Applied per-A-folio to build coverage matrix
- C703 (PP folio homogeneity): A folio pools are the input to filtering
- C384 (B vocabulary sharing): Aggregate 99.8% sharing masks per-folio routing (C734)
- C475 (MIDDLE incompatibility): Constrains which MIDDLEs can co-occur within A folios, indirectly shaping pool composition
- C728-C733 (PP line-level structure): Within-folio selection is random beyond incompatibility; between-folio selection is structured (this phase)

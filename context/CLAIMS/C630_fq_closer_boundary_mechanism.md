# C630: FQ_CLOSER Boundary Mechanism

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** FQ_CLOSER_BOUNDARY_HAZARD

## Statement

The 3 FQ_CLOSER forbidden pairs from C627 have heterogeneous explanations: (1) **dy→aiin** is positionally segregated -- dy's 35.8% final bias prevents adjacency to c9 tokens entirely; (2) **dy→chey** is a likely token-specific prohibition -- dy reaches c31 class (via dy→shey) but never chey despite expected count 1.32; (3) **l→chol** is a frequency artifact -- expected count 0.16 makes zero observation unsurprising (P(0)=0.85). Only 1 of 3 pairs represents a genuine token-level prohibition. The s→aiin bigram is 20x over-represented (O/E=20.0), dominating the 23→9 restart loop. The "25% unexplained gap" from C627 is largely resolved: 1 positional, 1 frequency artifact, 1 likely genuine.

## Evidence

### Expected Pair Counts Under Independence

| Pair | f(src) | f(tgt) | Expected | Observed | P(0) | Verdict |
|------|--------|--------|----------|----------|------|---------|
| dy→aiin | 109 | 351 | 1.850 | 0 | 0.157 | LIKELY (but positional) |
| dy→chey | 109 | 250 | 1.318 | 0 | 0.268 | BORDERLINE |
| l→chol | 34 | 99 | 0.163 | 0 | 0.850 | ARTIFACT |

### Allowed Pair Over-Representation

| Pair | Expected | Observed | O/E Ratio |
|------|----------|----------|-----------|
| s→aiin | 0.900 | 18 | 20.0x |
| r→aiin | 0.662 | 7 | 10.6x |
| y→shor | 0.083 | 1 | 12.1x |

### Integrated Verdicts

| Pair | Positional | Expected | P(0) | Final Verdict |
|------|------------|----------|------|---------------|
| dy→aiin | SEPARATED (0 adj to c9) | 1.85 | 0.16 | POSITIONAL_PLUS_FREQUENCY |
| dy→chey | GENUINE (1 adj to c31) | 1.32 | 0.27 | LIKELY_PROHIBITION |
| l→chol | GENUINE (4 adj to c8) | 0.16 | 0.85 | FREQUENCY_ARTIFACT |

### Restart Loop Analysis

| Token | c9 Rate | EN_CHSH Rate | Role |
|-------|---------|-------------|------|
| s | 48.6% | 0.0% | Restart specialist |
| r | 25.9% | 3.7% | Restart specialist |
| dy | 0.0% | 3.9% | General distributor |
| l | 3.7% | 22.2% | EN_CHSH feeder |

Spearman(c9_rate, EN_CHSH_rate) = -0.295 (weak negative, not significant at n=7).

## Interpretation

Class 23's "boundary specialist" role (C597) is not a unified mechanism -- it contains functionally distinct sub-populations. The 25% gap from C627 decomposes into:

- **Positional artifact** (dy→aiin): dy's extreme final bias excludes it from reaching c9 entirely. This is a consequence of positional stratification, not hazard grammar.
- **Frequency artifact** (l→chol): chol is rare enough (99) relative to l (34) that zero co-occurrence is expected by chance.
- **Likely genuine prohibition** (dy→chey): dy CAN reach c31 (observed via shey) but specifically avoids chey. Expected count 1.32 with P(0)=0.27 is borderline but combined with the dy→shey observation, constitutes token-level selectivity.

The s→aiin pathway (O/E=20x) reveals that the 23→9 restart loop is not a class-level property but a token-specific routing channel dominated by a single bigram.

## Extends

- **C627**: Resolves the 25% unexplained gap (1 positional, 1 artifact, 1 likely genuine)
- **C595**: 23→9 enrichment (2.85x) is driven by s→aiin (20x) not by class-level uniformity

## Related

C595, C597, C601, C622, C625, C627, C628, C629

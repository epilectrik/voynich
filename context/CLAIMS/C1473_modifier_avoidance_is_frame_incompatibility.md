# C1473: Modifier Avoidance is Frame Incompatibility

**Tier:** 2
**Scope:** B, MIDDLE, atom, modifier, co-occurrence, avoidance, frame, HEAD, TERMINAL
**Phase:** MODIFIER_FUNCTIONAL_GROUPING (Phase 532)
**Depends on:** C1472 (modifier co-occurrence avoidance), C1393 (compound MIDDLE composition grammar), C1394 (instruction encoding architecture), C1448 (HEAD x TERM frame hazard map), C1450 (modifier quenching), C1389-C1392 (individual modifier profiles)

## Constraint

The 8 modifier pair avoidance patterns from C1472 are driven by **frame incompatibility** (HEAD x TERMINAL selectivity conflict), NOT by functional redundancy or discrete grouping. Evidence: 5/5 incompatibility indicators PASS, 0/5 redundancy indicators PASS. The proposed {p,f,i} vs {c,d} vs {s} grouping (Hypothesis A) is REJECTED (separation ratio 0.997 -- no between-group vs within-group behavioral difference). Instead, modifier avoidance is explained by HEAD selectivity narrowness: d (85.1% e-HEAD) and i (88.6% a-HEAD) each occupy narrow, non-overlapping HEAD domains. Modifiers with narrow HEAD selectivity avoid each other because combining them would require a HEAD compatible with BOTH -- and no HEAD satisfies both e-dominant and a-dominant demands simultaneously. Co-occurring pairs share compatible frame demands.

## Key Evidence

| Metric | Avoiding Pairs | Co-occurring Pairs | Ratio |
|--------|---------------|-------------------|-------|
| Mean behavioral JSD | 0.1821 | 0.1510 | 1.21x (avoid LESS similar) |
| HEAD JSD | 0.4091 | 0.2923 | 1.40x |
| TERMINAL JSD | 0.5903 | 0.5380 | 1.10x |
| Category JSD | 0.2380 | 0.1443 | 1.65x |
| Folio Jaccard | 0.9405 | 0.9634 | 0.98x (avoid in FEWER shared folios) |
| HEAD set Jaccard | 0.9000 | 0.9714 | 0.93x |

### HEAD Selectivity Profiles (headed MIDDLEs only)

| Modifier | Dominant HEAD | % | Second HEAD | % | HEAD entropy |
|----------|--------------|---|-------------|---|-------------|
| d | e | 85.1% | o | 9.1% | 1.460 |
| i | a | 88.6% | o | 6.8% | 1.386 |
| p | o | 78.7% | e | 18.3% | 1.462 |
| f | o | 61.2% | e | 31.9% | 1.696 |
| c | e | 33.4% | o | 31.3% | 2.076 |
| s | o | 33.7% | e | 29.3% | 1.909 |

### TERMINAL Selectivity Profiles

| Modifier | Dominant TERM | % | Second TERM | % |
|----------|--------------|---|-------------|---|
| d | y | 59.6% | bare | 38.9% |
| i | n | 73.8% | bare | 23.3% |
| c | h | 50.7% | bare | 48.6% |
| p | bare | 53.4% | h | 43.1% |
| f | bare | 60.0% | h | 35.8% |
| s | bare | 70.7% | h | 28.2% |

### Modifier x HEAD/TERM contingency

| Test | chi-squared | Cramer's V |
|------|------------|------------|
| Modifier x HEAD | 7,929.0 | 0.545 |
| Modifier x TERMINAL | 13,371.5 | 0.498 |

Both V > 0.40 confirms modifiers are STRONGLY structured by HEAD and TERMINAL selection.

### Hypothesis Testing

| Hypothesis | Verdict | Key Evidence |
|-----------|---------|-------------|
| A: {p,f,i} vs {c,d} vs {s} discrete groups | **REJECTED** | Separation ratio 0.997 (no between > within) |
| B: Avoidance = functional redundancy | **REJECTED** | 0/5 redundancy signals; avoid pairs LESS similar |
| C: Avoidance = frame incompatibility | **SUPPORTED** | 5/5 incompatibility signals; HEAD JSD 1.40x higher for avoid pairs |

### Frame Incompatibility Mechanism

The avoidance pattern resolves to HEAD domain conflict:
- d demands e-HEAD (85.1%) -- THERMAL frame
- i demands a-HEAD (88.6%) -- TRANSITION frame
- These two have nearly non-overlapping HEAD demands, so d+i compounds would need a HEAD that is simultaneously e-dominant AND a-dominant -- impossible
- p and f demand o-HEAD (78.7% and 61.2%) -- OPERATION frame -- also incompatible with both d's e-frame and i's a-frame
- c and s have BROAD HEAD distributions (entropy 2.076 and 1.909) and can flexibly accommodate any HEAD, enabling co-occurrence with both narrow modifiers

The 8 empty pairs decompose as:
- d avoids {p, f, i}: d's e-HEAD is incompatible with p/f's o-HEAD and i's a-HEAD
- i avoids {p, c, d}: i's a-HEAD is incompatible with p's o-HEAD, c's broad-but-e-weighted HEAD, and d's e-HEAD
- c avoids {p, f}: despite c's broad HEAD, c's h-TERMINAL (50.7%) conflicts with p/f's bare-TERMINAL preference in practice

The 7 co-occurring pairs all have compatible frame demands:
- c+d: c is broad enough to accept d's e-HEAD
- c+s: both are broad HEAD distributions
- f+i: f's o-HEAD and i's a-HEAD are different but CAN co-occur (compounds like aifh, 2 tokens)
- etc.

s co-occurs with ALL other modifiers because: (1) broadest HEAD distribution after c (entropy 1.909), (2) lowest mean behavioral distance to centroid (0.1176 vs next-lowest c at 0.1518), (3) operates primarily in FQ macro-state (C1391: 64.6%) rather than AXM, providing orthogonal execution context.

## Falsification

Would be falsified if: (1) new multi-modifier compounds showed d+i co-occurrence at significant rates, or (2) modifier avoidance patterns changed when controlling for HEAD selection (i.e., within e-HEAD compounds, p and d freely co-occur), or (3) modifier pairs with matched HEAD selectivity showed the same avoidance patterns.

## Provenance

- `phases/MODIFIER_FUNCTIONAL_GROUPING/scripts/modifier_functional_grouping.py` -- Phase 532 analysis script
- `phases/MODIFIER_FUNCTIONAL_GROUPING/results/modifier_functional_grouping.json` -- structured results

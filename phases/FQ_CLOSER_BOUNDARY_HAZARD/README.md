# FQ_CLOSER_BOUNDARY_HAZARD

**Phase status:** COMPLETE | **Constraints:** C628-C630 | **Date:** 2026-01-26

## Objective

Determine whether the 3 unexplained forbidden pairs from C627 (all originating from FQ_CLOSER Class 23) are explained by positional segregation, Class 23's boundary function, or independent token-level prohibitions.

## Key Findings

1. **dy→aiin is positionally segregated** (C628). dy's extreme final bias (35.8% line-final, mean position 0.738, Mann-Whitney p<0.000001) prevents it from appearing adjacent to ANY c9 token. Zero adjacency to target class, not just to aiin.

2. **l→chol is a frequency artifact** (C630). Expected count under independence is 0.163; P(0)=0.85. l IS adjacent to c8 class 4 times (l→chedy×2, l→shedy×2), but chol (99 occurrences) is too rare relative to l (34) for the specific bigram to be expected.

3. **dy→chey is a likely genuine token-specific prohibition** (C630). dy reaches c31 class (1 adjacency: dy→shey) but never chey despite expected count 1.32. P(0)=0.27 (borderline). Combined with dy→shey being observed, this indicates token-level selectivity within Class 31.

4. **Class 23 contains functional sub-populations** (C629). The class-level 23→9 restart enrichment (2.85x, C595) is carried by s (48.6% → c9) and r (25.9% → c9). dy contributes 0%. s→aiin alone is 20x over-represented (O/E=20.0). dy is a generalist distributor (22 successor classes, entropy 4.179), not a restart specialist.

## Verdict

The "25% unexplained gap" from C627 decomposes into: 1 positional artifact, 1 frequency artifact, 1 likely genuine prohibition. Class 23 is NOT a unified boundary mechanism -- it contains at least two functional sub-populations (restart specialists vs general distributors). Only dy→chey survives as a potential structural prohibition.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `fq_closer_positional_segregation.py` | Per-token positions, overlap test, Mann-Whitney, verdict | `results/fq_closer_positional_segregation.json` |
| `fq_closer_source_discrimination.py` | Successor/predecessor profiles, context, morphology | `results/fq_closer_source_discrimination.json` |
| `fq_closer_boundary_mechanism.py` | Boundary asymmetry, restart loop, expected counts, verdict | `results/fq_closer_boundary_mechanism.json` |

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/HAZARD_CIRCUIT_TOKEN_RESOLUTION/results/fq_closer_positional_segregation.json`
- `scripts/voynich.py`

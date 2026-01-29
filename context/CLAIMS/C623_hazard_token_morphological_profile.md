# C623: Hazard Token Morphological Profile

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** HAZARD_CLASS_VULNERABILITY

## Statement

The 18 tokens participating in forbidden transitions are universally **suffix-less** (0% suffix rate) and **articulator-less** (0% articulator rate), with only 33% carrying prefixes (the ch/sh-prefixed EN tokens). Despite these shared properties, no single morphological feature reliably separates forbidden tokens from safe tokens within the same hazard classes (best accuracy: 68.8% on n=32, baseline: 56.2%). Hazard participation is **lexically specific** -- the forbidden transitions target specific token identities, not morphological categories.

## Evidence

### Forbidden Token Profile (n=18)

| Feature | Forbidden | Non-forbidden (same classes) |
|---------|-----------|------------------------------|
| Mean length | 2.86 | 3.06 |
| Mean MIDDLE length | 2.00 | 1.44 |
| Suffix rate | 0.00 | 0.06 |
| Prefix rate | 0.43 | 0.78 |
| Articulator rate | 0.00 | 0.00 |

### Best Discriminant

| Metric | Value |
|--------|-------|
| Best rule | has_prefix == False |
| Accuracy | 68.8% |
| Baseline (majority) | 56.2% |
| Sample size | 32 hazard-class tokens |

At n=32, the 12.6 pp improvement over baseline is not statistically reliable.

### MIDDLE Analysis

Forbidden-exclusive MIDDLEs: {aiin, al, edy, ey, l}
Safe-exclusive MIDDLEs: {am, d, eo, i, in, m, s, y}
Shared MIDDLEs: {ar, dy, o, ol, or, r} -- 6 MIDDLEs appear in both forbidden and safe tokens

### Position Distribution

| Group | N | Mean position | Initial% | Final% |
|-------|---|---------------|----------|--------|
| Forbidden tokens | 2,836 | 0.522 | 2.2% | 7.5% |
| Hazard-class non-forbidden | 987 | 0.506 | 13.0% | -- |

Mann-Whitney (forbidden vs non-forbidden in hazard classes): p=0.19 (not significant). Forbidden tokens are under-represented at line-initial position (2.2% vs 13.0%).

Compared to safe tokens by role: forbidden tokens differ from safe FL (p<0.001) and safe FQ (p<0.001) but not from safe EN (not tested separately).

## Interpretation

Forbidden transitions are not predictable from morphology. The zero suffix/articulator rate reflects the fact that hazard-class tokens are inherently short and morphologically minimal (classes 7, 9, 23 are atomic single-character or two-character tokens). The forbidden pairs are specific token-token combinations, not pattern-based. This is consistent with the hazard system being a finite lookup table of disallowed transitions rather than a rule-based grammar.

## Extends

- **C109**: Characterizes the 17 forbidden transitions at the morphological level
- **C541**: The 6 hazard classes contain both forbidden and non-forbidden tokens; the boundary is lexical

## Related

C109, C541, C542, C601, C622

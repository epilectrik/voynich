# C1908: Zodiac Folio i/d MOD Atom Swap

**Tier:** 2
**Scope:** AZC, zodiac, MOD, atom, i, d, seasonal
**Phase:** AZC_ATOM_SEASONAL (exploratory)

## Claim

Zodiac folios show statistically significant differentiation in MOD atom distribution (chi2=39.3, p=0.0006, dof=15). The primary driver is an i/d swap: Summer/Winter folios are enriched in i-containing tokens (`aiin` family: a-HEAD, ii-MOD, n-TERM), while Spring/Autumn folios are enriched in d-containing tokens (`-ody` family: e/o-HEAD, od-MOD, y-TERM). These are two structurally distinct token populations that are nearly mutually exclusive (3-7% co-occurrence).

## Evidence

### Token-level rates by season
| Season | i-rate | d-rate | Dominant |
|--------|--------|--------|----------|
| Spring | 0.104 | 0.193 | d |
| Summer | 0.199 | 0.148 | i |
| Autumn | 0.123 | 0.213 | d |
| Winter | 0.140 | 0.196 | d (mixed) |

### HEAD+MOD compounds
The swap is concentrated in a-HEAD tokens:
- Summer: a+i=37, a+d=5 (7.4:1 ratio)
- Spring: a+i=11, a+d=6 (1.8:1 ratio)

e-HEAD tokens are consistently d-dominant across ALL seasons (e+d >> e+i).

### Token family structure
| Feature | i-family (`aiin`) | d-family (`-ody`) |
|---------|-------------------|-------------------|
| HEAD | a (into/yield) | e/o (cool/arrange) |
| MOD pattern | ii (double iterate) | od (arrange.mark) |
| TERM | n (bind, OPAQUE) | y (end, OPAQUE) |
| Mean length | ~5 atoms | ~4 atoms |
| i_depth | 2 (ii is standard) | 0 |

### Supporting statistics
- HEAD atoms also significant (chi2=32.7, p=0.005): Autumn elevated e-HEAD (43.5%)
- TERM atoms NOT significant (p=0.104)
- Terminal opacity NOT significant (p=0.591)
- e_depth gradient: Autumn 0.813, Summer 0.597, Spring 0.573, Winter 0.515

### Seasonal interpretation caveats
- Seasonal assignments use C1681/C1684 corrected map (7 confident + 5 uncertain folios)
- Full 12-folio seasonal map is not significant (C1685, p=0.112)
- Only 3 folios per season — small N per group
- The structural differentiation is robust; the seasonal CAUSE is Tier 4

## Source
`phases/AZC_ATOM_SEASONAL/scripts/s1_zodiac_atom_profiles.py`
`phases/AZC_ATOM_SEASONAL/scripts/s2_id_swap_analysis.py`
`phases/AZC_ATOM_SEASONAL/results/s1_zodiac_atom_profiles.json`
`phases/AZC_ATOM_SEASONAL/results/s2_id_swap_analysis.json`

## Related Constraints
| Constraint | Relationship |
|------------|-------------|
| C321 | Zodiac vocabulary isolated (Jaccard 0.076) — now shown to include MOD-level differentiation |
| C1519 | Zodiac HEAD uniformity — partially challenged by HEAD significance (p=0.005) |
| C1681 | Seasonal signal confirmed at category level — now extended to atom level |
| C1394 | HEAD+MOD+TERM atom model — applied to AZC for first time |

## Falsification Criteria
Disproven if:
1. The chi-squared result does not survive multiple-comparison correction across all atom types
2. Alternative seasonal assignments eliminate the i/d pattern
3. The pattern is an artifact of a few high-frequency tokens on specific folios

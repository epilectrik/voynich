# C1150: Dark-Dominant Folios Shift Kernel Profile Within Section

**Tier:** 2
**Status:** Active
**Scope:** B, kernel, section
**Phase:** 410 (FOLIO_BALANCE_CHARACTERIZATION)

## Finding

Dark-dominant folios have significantly different kernel profiles than bridge-dominant folios: less k-kernel (heat/energy) and more h-kernel (hazard/monitoring). This signal survives within-section control in RECIPE_B (p=0.002), confirming it is not a section artifact.

### Global kernel fractions by balance group

| Kernel | BRIDGE_DOM | BALANCED | DARK_DOM | KW H | p | eta² |
|--------|-----------|----------|----------|------|---|------|
| k | 0.314 | 0.309 | 0.226 | 12.57 | 0.002 | 0.144 |
| h | 0.100 | 0.113 | 0.135 | 7.59 | 0.023 | 0.088 |
| e | 0.586 | 0.579 | 0.639 | 4.74 | 0.093 | 0.064 |

### Within-section control (k_frac)

| Section | KW H | p |
|---------|------|---|
| HERBAL_B | 0.02 | 0.992 |
| BIO | 0.33 | 0.569 |
| RECIPE_B | 12.13 | 0.002 |

The k-kernel shift is concentrated in RECIPE_B, where the balance groups are well-populated (BD=2, BAL=21, DD=10). In HERBAL_B and BIO, the balance groups are more homogeneous in kernel profile.

## Evidence

- Phase 410, Test 4: k_frac Kruskal-Wallis H=12.57, p=0.002, eta²=0.144
- Phase 410, Test 4: h_frac Kruskal-Wallis H=7.59, p=0.023, eta²=0.088
- Phase 410, Test 4: e_frac Kruskal-Wallis H=4.74, p=0.093 (trend only)
- Within-section: RECIPE_B k_frac H=12.13, p=0.002 (survives section control)

## Implication

Within the recipe section, folios that invest more in identification vocabulary (dark-dominant) systematically use less k-kernel (energy/heat operations) and more h-kernel (hazard/monitoring operations). This is consistent with a structural trade-off: procedures handling more distinct materials require more monitoring and less brute heating. The effect is specific to recipes, where the balance groups span the full range; in BIO (uniformly bridge-dominant) and HERBAL_B (mixed but similar), there is insufficient balance variation to detect the shift.

## Provenance

- Source: Phase 410, Test 4
- Related: C1146 (bridge-dark anti-correlation), C1149 (balance-dynamics independence), C1148 (hyper-modulation)

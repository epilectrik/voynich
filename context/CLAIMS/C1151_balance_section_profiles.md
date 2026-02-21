# C1151: Balance Distribution Is Section-Structured

**Tier:** 2
**Status:** Active
**Scope:** B, section differentiation
**Phase:** 410 (FOLIO_BALANCE_CHARACTERIZATION)

## Finding

The bridge/dark balance classification is strongly associated with section membership (chi-square = 29.95, df = 6, p < 0.0001). Each section has a characteristic balance profile that reflects its operational emphasis.

### Balance distribution by section

| Section | BRIDGE_DOM | BALANCED | DARK_DOM | n | Dominant |
|---------|-----------|----------|----------|---|----------|
| BIO | 11 (55%) | 9 (45%) | 0 (0%) | 20 | BRIDGE_DOM |
| HERBAL_B | 8 (33%) | 9 (38%) | 7 (29%) | 24 | mixed |
| PHARMA | 0 (0%) | 0 (0%) | 3 (100%) | 3 | DARK_DOM |
| RECIPE_B | 2 (6%) | 23 (66%) | 10 (29%) | 35 | BALANCED |

BIO is uniformly bridge-dominant (no dark-dominant folios). PHARMA is exclusively dark-dominant. RECIPE_B is predominantly balanced with a dark-dominant tail. HERBAL_B spans all three categories.

## Evidence

- Phase 410, Test 1: Chi-square = 29.95, df = 6, p < 0.0001
- Balance thresholds: dark/bridge ratio < 0.063 = BRIDGE_DOM, > 0.110 = DARK_DOM (empirical quartiles P25/P75)
- Sharpens C1148: hyper-modulation (3.9x) manifests as section-specific balance profiles

## Implication

The balance profiles characterize sections operationally: BIO folios are instruction-dense (low identification vocabulary), PHARMA folios are identification-dense (high identification vocabulary), and RECIPE_B folios are mixed. This is consistent with C1148's finding that dark-pipeline MIDDLEs are the primary vehicle for section-level vocabulary modulation. Balance classification provides a coarser but interpretable summary of the same underlying modulation.

## Provenance

- Source: Phase 410, Test 1
- Related: C1148 (hyper-modulation), C1146 (bridge-dark anti-correlation), C1134 (PP frequency modulation)

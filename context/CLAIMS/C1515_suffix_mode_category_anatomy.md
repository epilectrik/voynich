# C1515: Suffix Mode A/B category anatomy with positional asymmetry

**Tier:** 2
**Scope:** B, suffix, mode, category, positional, THERMAL, FLOW, MONITORING, TRANSITION, anatomy
**Phase:** SUFFIX_ATOM_TAXONOMY (Phase 540)

## Claim

The two suffix modes (C1229, C1410) have sharply divergent category and positional profiles at atom-level resolution. Mode A (N=5,676) is enriched in THERMAL (1.20x), CONTAINMENT (2.93x), MONITORING (5.08x), OPERATION (2.95x) -- the specification/energy categories. Mode B (N=5,454) is enriched in FLOW (0.47x A/B), STAGING (0.46x A/B), TRANSITION (0.46x A/B) -- the continuation/state-change categories. Mode A tokens are more interior-positioned (mean 0.491 vs 0.514), less frequent at line boundaries (initial 8.9% vs 12.7%, final 8.5% vs 13.9%). Mode A multi-atom suffixes are longer (3-atom 35.9% vs 31.4%) while Mode B has more single-atom suffixes (17.2% vs 11.9%). This confirms C1410 with full 8-category resolution and adds the positional asymmetry finding: Mode A is the medial specification mode, Mode B is the boundary continuation mode.

## Evidence

- Mode A: 5,676 tokens; Mode B: 5,454 tokens (51.0% vs 49.0%)
- Category ratios (Mode A / Mode B):
  - MONITORING: 5.08x (A=5.8%, B=1.1%)
  - CONTAINMENT: 2.93x (A=5.5%, B=1.9%)
  - OPERATION: 2.95x (A=14.8%, B=5.0%)
  - THERMAL: 1.20x (A=42.9%, B=35.8%)
  - MARKING: 0.83x (A=10.9%, B=13.2%)
  - FLOW: 0.47x (A=10.7%, B=22.7%)
  - STAGING: 0.46x (A=5.3%, B=11.4%)
  - TRANSITION: 0.46x (A=4.0%, B=8.8%)
- Positional: Mode A mean pos 0.491 vs B 0.514
- Line-initial: A=8.9%, B=12.7% (1.43x B-enriched)
- Line-final: A=8.5%, B=13.9% (1.64x B-enriched)
- Atom-length: A has 35.9% 3-atom suffixes vs B 31.4%; B has 17.2% 1-atom vs A 11.9%

## Relationship to Prior Constraints

- **Extends C1410**: Confirmed Mode A = {d,e,ee,h,y} THERMAL/MONITORING and Mode B = {a,i,ii,l,m,n,o,r,s} STAGING/FLOW at full 8-category resolution with ratios
- **Extends C1279**: Mode A THERMAL-enriched and Mode B TRANSITION-enriched confirmed with all 8 categories
- **Connects C1258**: Parallel mode tracks -- Mode A (specification) is medial, Mode B (continuation) is boundary-biased
- **Connects C1426-C1427**: Line-initial specification and line-final transition align with Mode B being boundary-enriched
- **Connects C1309**: Mode category specialization confirmed at atom resolution

## Source

`phases/SUFFIX_ATOM_TAXONOMY/results/suffix_atom_taxonomy.json` (T8)

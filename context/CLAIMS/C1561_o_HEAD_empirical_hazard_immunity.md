# C1561: o-HEAD Empirical Hazard Immunity (0% Source AND 0% Target)

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, o-HEAD, hazard, immunity, source, target, double-protection, C1388, C1446, C1546, C1551, C1557, C1561
**Phase:** O_DOMAIN_DEEP_DIVE (Phase 548)
**Date:** 2026-03-06

## Claim

o-HEAD has 0% hazard source rate AND 0% hazard target rate across all 2,717 tokens. While C1546 established that ALL HEADs have 0% source rate, the target rate finding is new. Three forbidden pairs theoretically involve o-HEAD MIDDLEs as targets: [he->or], [shedy->o], and o-HEAD as source in [or->dal]. In practice, none fire: shedy is a phantom MIDDLE (C1552, 0 tokens), and he->or is vanishingly rare. This makes o-HEAD the safest HEAD domain: zero hazard involvement in any direction, reinforced by y-terminal avoidance (C1557, 0.007x) and executive modifier preference (C1558).

## Evidence

### Hazard rates by HEAD

| HEAD | Source Rate | Target Rate |
|---|---|---|
| a | 0.038% | 0.337% |
| e | 0.000% | 0.000% |
| **o** | **0.000%** | **0.000%** |
| k | 0.000% | 0.000% |
| t | 0.000% | 0.000% |
| HEADLESS | 0.189% | 0.019% |

### Theoretical forbidden pairs involving o-HEAD

| Forbidden Pair | Source Exists | Target Exists | Fires |
|---|---|---|---|
| he -> or | Yes (he: low freq) | Yes (or: 446 tokens) | No |
| shedy -> o | No (phantom, 0 tokens) | Yes (o: 388 tokens) | No |
| or -> dal | Yes (or: 446 tokens) | Yes (dal: present) | No |

### Three-layer protection

1. **HEAD immunity** (C1546): All headed tokens are immune from hazard sourcing
2. **y-terminal avoidance** (C1557): o-HEAD depletes y at 0.007x, avoiding PHASE_ORDERING vector
3. **Phantom source protection** (C1552): Key forbidden source (shedy) is a phantom with 0 tokens

## Interpretation

o-HEAD operates in a structurally protected safety zone. The arrangement domain does not generate or absorb hazard. This is functionally appropriate: arrangement/configuration tokens describe static states and relationships, not dynamic operations that could fail. The three-layer protection is likely a structural consequence of o-HEAD's functional role rather than an independently designed safety feature.

## Falsification Criteria

1. If any o-HEAD token is found as hazard source or target
2. If the theoretical forbidden pairs involving o-HEAD MIDDLEs begin firing with additional corpus data
3. If the 0% target rate is shown to be a sampling artifact

## Source

`phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json`

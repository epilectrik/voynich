# C1541: Suffix exclusion defines instruction-only atom tier

**Tier:** 2
**Scope:** GLOBAL, atom, suffix, exclusion, instruction, tier, C1509, C1511, C1540

## Claim

The 5 suffix-excluded atoms {k,t,p,f,c} (C1511) partition the 18-atom alphabet into OUTCOME-accessible atoms (13 atoms that appear in suffix) and INSTRUCTION-ONLY atoms (5 atoms that never appear in suffix). This partition exactly equals C1509's UNSTABLE set {p,f,c} plus ACTION HEAD set {k,t}. Suffix exclusion = instruction-only function = register sensitivity. The suffix-excluded atoms encode actions and parameters; the suffix-accessible atoms can additionally encode outcomes and conditions.

## Evidence

Suffix presence across all three systems (A, B, AZC):

| Atom | In suffix | Category | C1509 tier |
|------|-----------|----------|------------|
| k | 0 | ACTION HEAD | MODERATE |
| t | 0 | ACTION HEAD | MODERATE |
| p | 0 | EXECUTIVE MOD | UNSTABLE |
| f | 0 | EXECUTIVE MOD | UNSTABLE |
| c | 0 | EXECUTIVE MOD | UNSTABLE |
| i | 4,209 | STABLE MOD | STABLE |
| d | 3,806 | STABLE MOD | MODERATE |
| s | 986 | STABLE MOD | STABLE |

All 13 non-excluded atoms appear in suffix: highest y (8,713), lowest m (532). All 5 excluded atoms have exactly 0 suffix occurrences across all systems.

## Methodology

Phase 545 analysis. Atom presence counted character-by-character in suffix field across all 37,497 morphologically parsed tokens in A (11,174), B (23,096), and AZC (3,227).

## Constraints

- Connects C1511 (suffix atom exclusion) with C1509 (instability tiers)
- Extends C1510 (suffix parallel HEAD+TERM decomposition): explains WHY {k,t,p,f,c} are excluded
- Consistent with C1394 (instruction encoding): instruction atoms don't encode outcomes

## Phase

Phase 545: Executive Atom Instability

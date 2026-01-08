# Grammar Metrics

**Status:** FROZEN | **Tier:** 0-2

---

## Core Grammar Numbers

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Raw token types | 479 | 0 | - |
| Instruction classes | 49 | 0 | C121 |
| Compression ratio | 9.8x | 0 | C121 |
| Grammar coverage | 100% | 0 | C124 |
| Non-executable tokens | 0 | 0 | C115 |
| Translation-eligible zones | 0 | 0 | C119 |

---

## Kernel Structure

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Single-char primitives | 10 (s,e,t,d,l,o,h,c,k,r) | 2 | C085 |
| Core kernel operators | 3 (k, h, e) | 2 | C089 |
| 4-cycles | 500+ | 2 | C090 |
| 3-cycles | 56 | 2 | C090 |
| e-class dominance | 36% of tokens | 2 | C339 |
| e-state trigrams | 97.2% (e→e→e) | 2 | C333 |

---

## Local Determinism

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| H(X\|prev 2) | 0.41 bits | 2 | C389 |
| Reduction from unconditioned | 95.9% | 2 | C389 |
| Trigram hapax rate | 99.6% | 2 | C390 |
| 5-gram uniqueness | 100% | 2 | C390 |

---

## Role Distribution

| Role | % of B Tokens |
|------|---------------|
| ENERGY_OPERATOR | ~35% |
| CORE_CONTROL | ~20% |
| AUXILIARY | ~9% |
| HIGH_IMPACT | ~10% |
| FLOW_OPERATOR | ~15% |
| Other | ~11% |

---

## Morphological Composition

| Metric | Value | Constraint |
|--------|-------|------------|
| PREFIX × MIDDLE × SUFFIX combinations | 897 | C268 |
| Universal suffixes | 7 | C269 |
| Universal middles | 3 | C269 |
| PREFIX-exclusive middles | 28 | C276 |
| Instruction concentration (50%) | 28 combinations | C381 |
| Instruction concentration (80%) | 87 combinations | C381 |

---

## Navigation

← [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [hazard_metrics.md](hazard_metrics.md) →

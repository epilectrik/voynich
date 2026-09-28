# Grammar Metrics

**Status:** FROZEN | **Tier:** 0-2

> **Status note (v7.25):** tiers in this file are aligned with the generated `CONSTRAINT_TABLE.txt` as of 2026-09-28. The "Kernel Structure" section is withdrawn (see its banner). Current orientation: SYSTEM/STATUS_BRIEF.md.

---

## Core Grammar Numbers

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Raw token types | 479 (the corrected C124 row counts 480) | 0 | - |
| Instruction classes | 49 | 0 | C121 |
| Compression ratio | 9.8x | 0 | C121 |
| Grammar coverage | 100% of the grammar's own vocabulary = 69.5% of B tokens (HT/UN defined by exclusion, C566) | 0 | C124 (as corrected) |
| Non-executable tokens | 0 — coverage by construction; 30.5% of B tokens (HT/UN) lie outside the grammar | 3 (demoted from 0) | C115 |
| Translation-eligible zones | 0 | 2 (from 0; negative knowledge) | C119 |

---

## Kernel Structure

**[Withdrawn v7.24/7.25 — historical; see SYSTEM/STATUS_BRIEF.md §3]** C089 ("core kernel operators k, h, e") is superseded by C2082: at glyph level k shows no cross-token routing beyond its controls, and the e/bench signal is word-ending routing, not a kernel role. C085 is demoted to Tier 3 (an EVA letter inventory, not a primitive inventory). Rows below that remain Tier 2 (C090, C339, C333) are letter/class counts; the "kernel" label on them is historical.

| Metric | Value | Tier | Constraint |
|--------|-------|------|------------|
| Single-char primitives | 10 (s,e,t,d,l,o,h,c,k,r) | 3 (demoted: EVA letter inventory) | C085 |
| Core kernel operators | 3 (k, h, e) | superseded by C2082 (dead) | C089 |
| 4-cycles | 500+ | 2 | C090 [v7.26 status: C090 demoted to Tier 3 (4-cycles are a floor for a diameter-1 graph)] |
| 3-cycles | 56 | 2 | C090 [v7.26 status: C090 demoted to Tier 3 (4-cycles are a floor for a diameter-1 graph)] |
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

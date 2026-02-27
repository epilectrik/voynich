# C1353: Dark MIDDLEs Have Weak Positional Bias Before Bridge

**Tier:** 2
**Scope:** B
**Phase:** DARK_PIPELINE_STRUCTURE (472)

## Constraint

On lines containing both dark and bridge tokens (1,191 lines, 13,697 pairs), dark tokens precede bridge tokens 52.7% of the time — statistically significant (Z=3.0, perm p=0.004) but with trivial effect size (2.7% above the 50% null). The bias is section-uniform: all sections show 49-57% dark-before-bridge, with no section exceeding 57%. Dark tokens occupy no dedicated syntactic slot relative to grammar; they are approximately freely positioned within lines with only a slight leftward tendency.

## Evidence

From dark_pipeline_structure.py test T4 (1,191 mixed lines):

| Metric | Value |
|--------|-------|
| Mixed lines | 1,191 |
| Total dark-bridge pairs | 13,697 |
| Dark-before-bridge | 7,217 (52.7%) |
| Null mean | 50.0% |
| Z-score | 3.0 |
| Perm p | 0.004 |

**Per-section dark-before-bridge fraction:**

| Section | Fraction | Pairs |
|---------|----------|-------|
| B | 54.7% | 2,774 |
| C | 49.0% | 1,879 |
| H | 50.9% | 1,817 |
| S | 53.1% | 6,689 |
| T | 56.9% | 538 |

## Interpretation

Dark MIDDLEs do not have a syntactic slot. Material referents in a natural-language-like system would occupy a consistent grammatical position (e.g., object position after a verb). Instead, dark tokens are nearly symmetrically distributed around bridge tokens. The 2.7% leftward bias is real but too small to constitute a slot — it may reflect the slight interaction between dark tokens' interior enrichment (C1147) and bridge tokens' own positional preferences (C813 phase ordering), rather than a genuine ordering constraint.

Combined with the random adjacency finding (C1350: ratio=1.02), this confirms dark tokens are freely interleaved with grammar, not constrained to specific positions.

## Provenance

- dark_pipeline_structure.json: test T4
- Extends: C1147 (interior enrichment — the slight leftward bias may be a consequence of interior-vs-boundary positioning)
- Extends: C813 (canonical phase ordering — bridge tokens have their own positional preferences)
- Extends: C1350 (atomistic distribution — consistent with free placement)

## Status

CONFIRMED — dark MIDDLEs show weak positional bias (52.7% before bridge, Z=3.0) but no syntactic slot. Effect size is trivial (2.7%) and section-uniform.

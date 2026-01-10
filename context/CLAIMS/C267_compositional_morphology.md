# C267: Tokens are COMPOSITIONAL

**Tier:** 2 | **Status:** CLOSED | **Phase:** CAS-MORPH

---

## Claim

Marker tokens in Currier A are compositional, not atomic. They decompose into orthogonal components that combine predictably.

## Compositional Structure

```
marker_token = [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
```

| Component | Count | Role | Required? |
|-----------|-------|------|-----------|
| ARTICULATOR | ~9 forms | Optional refinement | No |
| PREFIX | 8 | Primary classifier family (domain selector) | Yes |
| MIDDLE | 1,184 unique (27 universal) | Vocabulary item within domain | No |
| SUFFIX | 7 universal | Terminal variant code | Yes |

**Note:** Early analysis identified "42 common middles" as a discovery-era simplification. Full census (C423) reveals 1,184 unique MIDDLEs with 80% PREFIX-EXCLUSIVE, confirming MIDDLE as the primary vocabulary layer.

## Evidence

- 897 observed PREFIX x MIDDLE x SUFFIX combinations (C268)
- 7 universal suffixes across 6+ prefixes (C269)
- 28 middles are PREFIX-EXCLUSIVE (C276)
- Components shared between A and B (C281)

## What This Explains

| Observation | Explanation |
|-------------|-------------|
| Low TTR (0.137) | Component reuse |
| High bigram reuse (70.7%) | Predictable combinations |
| Learnability | Small codebook, compositional rules |
| ~11,000 HT types | Combinatorial stringing |

## Component Hierarchy (EXT-8)

```
PREFIX (family) → MIDDLE (type-specific) → SUFFIX (universal form)
```

This is the signature of a MATERIAL CLASSIFICATION SYSTEM.

## Related Constraints

- C268-271 - Combination counts, universals, exclusives
- C276-278 - Middle/suffix roles
- C293 - Component essentiality hierarchy

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

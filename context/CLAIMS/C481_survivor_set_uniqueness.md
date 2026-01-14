# C481: Survivor-Set Uniqueness

**Tier:** 2 | **Status:** CLOSED | **Scope:** A+AZC | **Source:** Phase SSD (2026-01-12)

---

## Statement

AZC survivor sets are essentially unique per Currier A line (0 collisions in 1,575 lines), functioning as high-dimensional constraint fingerprints rather than grouping labels or variant lists.

---

## Structural Interpretation

Survivor sets are **constraint profiles**, not menus.

- Each A line defines a distinct discrimination context
- No two A lines produce identical survivor sets
- This is a direct consequence of massive MIDDLE incompatibility (C475: 95.7% illegal pairs)

---

## Evidence

```
Phase SSD Test 3 Results:
- Collision groups found: 0
- A lines analyzed: 1,575
- Each line produces distinct survivor set
- Result: DETERMINISTIC
```

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C475 | **Explains**: 95.7% MIDDLE incompatibility creates uniqueness |
| C240 | **Compatible**: A is registry, not lookup table |
| C476 | **Compatible**: Coverage optimality achieved through unique fingerprints |
| F-AZC-011 | **Extends**: AZC folios maximally orthogonal (Jaccard=0.056) |

---

## Eliminates Misinterpretations

This constraint rules out survivor sets being:

- Grouping labels (would require collisions)
- Sub-record selectors (would require shared structure)
- Execution alternatives (would require discrete options)
- Semantic variant lists (would require categorical boundaries)

Survivor sets are **continuous constraint regions** in a ~128-dimensional discrimination space, not discrete categories.

---

## Architectural Role

Completes the characterization of A→AZC filtering:

> **Each Currier A line induces a unique point (or region) in compatibility space.**

Combined with C479, this establishes:
- A line → unique survivor set → unique discrimination envelope → scaled HT response

The pipeline is now fully characterized from A input to HT output.

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

# Jar Label Analysis Results

**Date:** 2026-01-17
**Status:** COMPLETE

---

## Summary of Findings

### 1. Jar Labels Are Unique Container Identifiers

**Critical finding:** NO jar labels repeat across folios.

- 16 unique jar labels across 7 folios
- Each jar label appears in exactly ONE folio
- This rules out "jar = processing category" hypothesis

**Interpretation:** Jar labels are **unique identifiers for individual containers**, not names for processing methods.

---

### 2. Jar Prefix Patterns

Despite unique labels, jar prefixes show systematic patterns:

| Prefix | Count | Plant Part | Material Class |
|--------|-------|------------|----------------|
| ok-    | 5     | 4 root, 1 leaf | M-B (Routine) |
| da-    | 3     | 3 root, 0 leaf | M-D (Stable) |
| others | 8     | various | various |

**Key pattern:** Jar labels NEVER use M-A prefixes (ch-, sh-).
- M-A = "energy operations" (precision required)
- Jars favor M-B (routine) and M-D (stable)

---

### 3. Content Clustering by Jar Prefix

| Metric | Value |
|--------|-------|
| Within-group similarity | 0.112 |
| Between-group similarity | 0.089 |
| Ratio | **1.25x** |

**Result:** Jars with the same prefix contain 25% more similar contents than jars with different prefixes.

Weak but detectable clustering - jar prefix encodes something about expected contents.

---

### 4. ok- vs da- Jars: Content Differences

| Content Prefix | ok- Jars | da- Jars | Direction |
|---------------|----------|----------|-----------|
| sa- | 9.4% | 0.0% | -> ok |
| os- | 9.4% | 0.0% | -> ok |
| ch- | 0.0% | 9.1% | -> da |
| do- | 0.0% | 9.1% | -> da |

ok- jars contain more sa-/os- prefixed content; da- jars contain more ch-/do- content.

---

## Revised Model

### Two-Level Naming System

```
JAR = UNIQUE CONTAINER ID
    = PREFIX (category marker) + MIDDLE + SUFFIX (unique ID)

Example:
  okaradag = ok (routine category) + arada + g (unique suffix)
  darolaly = da (stable category) + rola + ly (unique suffix)
```

### What Jar Prefix Encodes

The jar PREFIX likely encodes a **processing category** while the full label is a unique container ID:

| Jar Prefix | Interpretation |
|------------|----------------|
| ok- | Containers for routine processing |
| da- | Containers for stable/structural materials |
| po- | Containers for leaf-based materials? |
| etc. | Other processing requirements |

---

## Comparison to External Systems

### Brunschwig (16 ≈ 15)
- 5 fire methods × 3 allowed degrees = 15 categories
- We have 16 jar labels
- **Match is suggestive but unprovable**

The key insight: While total COUNT is similar, the STRUCTURE differs:
- Brunschwig categories would repeat across folios
- Voynich jar labels do NOT repeat

This suggests Voynich jars are individual container IDs **within** processing categories, not the categories themselves.

### Puff Categories
- Puff has ~8-9 material categories
- Jar prefixes show ~10 distinct values
- **Weak structural match**

---

## Conclusions

1. **Jar labels = unique container identifiers** (not category names)
2. **Jar prefixes = category markers** (processing type?)
3. **Content labels = specimen identifiers** (what's in the container)
4. **Vocabulary separation is absolute** (Jaccard = 0.000)
5. **Weak content clustering by jar prefix** exists (1.25x effect)

The system appears to be:
- Categories encoded by PREFIX
- Unique container IDs encoded by full jar label
- Contents identified by separate vocabulary

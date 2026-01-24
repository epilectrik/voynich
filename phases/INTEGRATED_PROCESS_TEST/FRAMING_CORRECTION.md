# Framing Correction: Operational Profile Generality

**Date:** 2026-01-22
**Status:** RESOLVED
**Validated by:** Internal expert-advisor, external expert, primary analyst

---

## The Conflict

During testing of hypothesis H1 ("B encodes integrated process control"), a conflict emerged between test results and frozen constraints.

**Test claimed:** 48.8% of B instruction usage encodes "preparation" operations
**Constraints say:** C171 forbids batch processing; C120 confirms pure operational

This appeared to be a contradiction.

---

## Root Cause: Level Conflation

Two questions were being conflated:

| Question | Level | Answer |
|----------|-------|--------|
| "Does Currier B *handle* preparation?" | Compatibility (external) | Conditionally yes |
| "Does Currier B *encode* preparation steps?" | Grammar (internal) | **NO - FORBIDDEN** |

The slide from the first to the second caused the apparent conflict.

---

## Resolution

### The Validated Key Sentence

> **"Currier B never encodes preparation steps. It encodes control envelopes. Externally, we can observe that these envelopes are compatible with materials which, in practice, require preparation before entering the loop."**

### What C171 Actually Forbids

- Discrete steps
- Batch completion semantics
- Narrative ordering ("do X, then Y")
- State machines
- Decision trees

### What C171 Does NOT Forbid

- Different operational regimes
- Different control envelopes
- Different control requirements depending on what has entered the loop
- Compatibility observations made by external analysts

---

## Constraint Compliance

| Constraint | Requirement | Resolution Status |
|------------|-------------|-------------------|
| C171 | Closed-loop control only | COMPLIANT - "control envelopes" is continuous |
| C120 | Pure operational, no materials | COMPLIANT - compatibility is external observation |
| C175 | 3 process classes survive | COMPLIANT - no new classes introduced |
| C121 | 49 classes are abstract | COMPLIANT - envelopes are abstract |
| C384 | No entry-level A-B coupling | COMPLIANT - aggregate profiles, not token-level |
| C458 | Grammar clamps danger, frees recovery | COMPLIANT - envelope abstraction preserved |

---

## What Must Be Discarded

- **The 48.8%/51.2% "PREP/DISTILL split"** - Artifact of incorrect classification
- **PREP vs DISTILLATION as internal categories** - B has no such distinction
- **Any claim that B "encodes" collection, washing, soaking, etc.** - ILLEGAL
- **The original test name "Integrated Process Test"** - Misleading framing

---

## What Survives

- **Role-level correlations** (e.g., FLOW→da r=0.98) - Valid as abstract mappings
- **Earthworm triangulation** - Valid at Tier 4 as profile compatibility
- **The observation that B profiles vary** - This is structural fact
- **Compatibility matching methodology** - Valid when correctly framed

---

## Renamed Test

**Original:** Integrated Process Test
**Corrected:** Operational Profile Generality Test

The test validated that B's operational profiles exhibit generality beyond narrow distillation-only interpretations. It did NOT validate that B "encodes prep steps."

---

## Warning (Add Near C171)

> **DISALLOWED INTERPRETATIONS**
> Any interpretation that introduces discrete steps, batch semantics, or narrative sequence is invalid. "B handles X" must never slide into "B encodes X steps."

---

## Earthworm Triangulation Status

| Framing | Status |
|---------|--------|
| "B encodes collecting worms" | **ILLEGAL** - violates C120, C171 |
| "B operational profile is compatible with earthworm-like processing requirements" | **ALLOWED** - Tier 4, externally grounded |

The candidate "cthea" remains a valid Tier 4 discriminator for operational profile matching, not a semantic label for earthworm.

---

## Key Conceptual Distinction

```
INTERNAL (what B encodes):
  - Control envelopes
  - Operational regimes
  - Abstract instruction roles
  - Hazard topology
  - Recovery architecture

EXTERNAL (what analysts observe):
  - Compatibility with material classes
  - Profile matching to historical recipes
  - Aggregate statistical correlations
  - Tier 3-4 interpretations
```

B encodes the left column. The right column is our analysis of what the left column is compatible with.

---

## Lessons Learned

1. **Framing level matters** - "encodes X" ≠ "is compatible with X"
2. **Constraints are precise** - C171 forbids specific things, not everything
3. **Non-semantic means non-semantic** - BCSC role taxonomy is abstract
4. **External knowledge is external** - Compatibility is discovered, not encoded

---

## Sign-Off

This resolution:
- Requires NO changes to Tier 0-2 constraints
- Introduces NO new constraints
- Clarifies interpretive language only
- Is validated by all reviewing parties

The constraint system is internally consistent. The conflict was linguistic, not structural.

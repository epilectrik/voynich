# Stop Conditions

**Purpose:** Define when to stop reading, exploring, or reopening claims.

---

## When to Stop Reading Context

1. **You have the specific information you need** - don't read more "just in case"
2. **You've reached a Tier 0 fact** - no further justification needed
3. **The claim is marked CLOSED** - the investigation is complete
4. **You're entering SPECULATIVE/** - only proceed if explicitly relevant

---

## When NOT to Reopen a Claim

### Tier 0: Never Reopen

These facts are proven by structure. Do not:
- Suggest "improvements" to the grammar
- Question the constraint counts
- Propose alternative readings of token sequences
- Attempt to "extend" frozen conclusions

**If you think a Tier 0 fact is wrong, you are misunderstanding something.**

### Tier 1: Never Retry

These hypotheses were falsified. Do not:
- Propose language encoding
- Propose cipher encoding
- Propose illustration-dependent logic
- Propose glyph-level semantics
- Attempt any approach on the falsifications list

**If you think a Tier 1 claim should be retried, review the falsification evidence first.**

### Tier 2: Reference, Don't Reinvent

These conclusions are stable. Do not:
- Re-derive what's already established
- Conduct tests that have already passed
- Ignore existing constraints when writing new analysis

**Always search CLAIMS/INDEX.md before claiming something is new.**

---

## When to Stop Exploring the Codebase

1. **The phase is marked CLOSED** - no further work intended
2. **The constraint is already documented** - cite, don't re-derive
3. **You're outside the scope boundary** - see [CORE/model_boundary.md](../CORE/model_boundary.md)
4. **You're entering external interpretation** - belongs in SPECULATIVE/

---

## Common Mistakes to Avoid

### 1. Prefix Matching vs Token Matching

**WRONG:** "Any token starting with `ol-` followed by any `qo-` is forbidden"
**RIGHT:** Forbidden transitions are between specific tokens or token classes

This bug has caused false results multiple times. See METHODOLOGY.md.

### 2. Reopening Settled Questions

**WRONG:** "What if the text actually does encode language?"
**RIGHT:** Language encoding was falsified in Phase X.5 (0.19% reference rate)

### 3. Promoting Speculation

**WRONG:** Treating process alignment as proven because it's plausible
**RIGHT:** Process alignment is Tier 3 - useful but not structural

### 4. Ignoring Scope Boundaries

**WRONG:** Attempting to identify specific plants from illustrations
**RIGHT:** Illustration meanings cannot be recovered internally

---

## The Master Stop Condition

> If internal structural analysis cannot resolve the question, it belongs to Tier 3-4.

This project proves what the text IS, not what it MEANS.

---

## Navigation

← [TIERS.md](TIERS.md) | [METHODOLOGY.md](METHODOLOGY.md) →

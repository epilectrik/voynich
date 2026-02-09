# Component-to-Class Mapping: MIDDLE Analysis (CCM-4)

**Tier:** 3 | **Status:** COMPLETE | **Date:** 2026-01-10

> **Goal:** Classify the MIDDLE component based on prefix material class and understand its discriminative function.

---

## Data Sources

| Source | What It Provides |
|--------|------------------|
| C276 | 28 MIDDLEs are PREFIX-EXCLUSIVE |
| C293 | MIDDLE provides 402 unique distinctions (primary discriminator) |
| C423 | 1,184 distinct MIDDLEs, 80% prefix-exclusive, 20% shared |
| C410.a | MIDDLE drives sister-pair choice (25.4% deviation) |

---

## MIDDLE Census

From C423:

| Metric | Value |
|--------|-------|
| Total distinct MIDDLEs | 1,184 |
| Prefix-EXCLUSIVE | 947 (80%) |
| Shared across prefixes | 237 (20%) |
| UNIVERSAL (6+ prefixes) | 27 |

### Prefix-Exclusive Vocabulary Sizes

| Prefix | Exclusive MIDDLEs | Material Class |
|--------|-------------------|----------------|
| ch | 259 (largest) | M-A operations |
| qo | 191 | M-A operations |
| da | 135 | Cross-class anchor |
| ct | 87 | M-C/M-D registry |
| sh | 85 | M-A operations (variant) |
| ok | 68 | M-B operations |
| ot | 55 | M-B operations (variant) |
| ol | 34 (smallest) | Cross-class anchor |

---

## CCM-4 Synthesis: MIDDLE Function

### What MIDDLE Encodes

| Prefix Domain | MIDDLE Function | Example Interpretation |
|---------------|-----------------|----------------------|
| **ch-exclusive** | M-A sub-variants | Distinctions within mobile-distinct handling |
| **qo-exclusive** | Energy sub-types | Distinctions within energy control |
| **ct-exclusive** | Registry categories | Distinctions within stable-material classification |
| **ok-exclusive** | M-B sub-variants | Distinctions within mobile-homogeneous handling |
| **da-exclusive** | Structural markers | Distinctions within articulation patterns |

### MIDDLE as Within-Class Discriminator

Given:
- PREFIX = material-class operation
- MIDDLE = 80% prefix-exclusive
- MIDDLE is primary discriminator (402 distinctions vs 13 for suffix)

**Conclusion:** MIDDLE encodes **within-class variation**.

If ch- operates on M-A materials (mobile, distinct), then:
- ch-exclusive MIDDLEs discriminate among M-A variants
- Different ch-MIDDLEs = different M-A sub-types or states

This is analogous to:
- PREFIX = genus (what kind of thing)
- MIDDLE = species (which variant within that kind)
- SUFFIX = decision context (what decision type applies)

---

## MIDDLE and Sister-Pair Choice

From C410.a, MIDDLE drives sister preference (25.4% deviation).

| MIDDLE Type | Sister Preference | Interpretation |
|-------------|-------------------|----------------|
| High ch-preference MIDDLEs | Precision mode | These variants require tight handling |
| Balanced MIDDLEs | Either mode acceptable | These variants are tolerant |
| High sh-preference MIDDLEs | Recovery mode | These variants permit looser handling |

**Implication:** Some material variants within M-A class are inherently more precision-critical than others. The MIDDLE encodes this.

---

## Shared vs Exclusive MIDDLEs

### Shared MIDDLEs (20%)

The 237 shared MIDDLEs appear across multiple prefix families.

| Shared MIDDLE Type | Function |
|--------------------|----------|
| Universal (27) | Core discriminations that apply to all material classes |
| Semi-shared | Discriminations that cross 2-5 prefix families |

**Interpretation:** Some discriminations are class-independent:
- All materials have states that need the same kind of distinction
- Universal MIDDLEs encode these cross-class discriminations

### Exclusive MIDDLEs (80%)

The 947 exclusive MIDDLEs are locked to specific prefix families.

**Interpretation:** Most discriminations are class-specific:
- M-A materials have variants that M-B materials don't
- Registry items (ct-) have categories that operational prefixes don't
- This specialization is expected in a domain with multiple material types

---

## MIDDLE Entropy

From C423: MIDDLE entropy = 6.70 bits (65.6% of maximum)

This means:
- High diversity (many distinct MIDDLEs)
- Not maximally random (structured, learnable)
- Consistent with human-usable discrimination system

A practitioner would need to learn ~1,000+ variant codes, but they're organized by prefix family, making the system tractable.

---

## Complete Compositional Model

```
TOKEN = PREFIX (material-class operation)
      + SISTER-VARIANT (operational mode: precision vs tolerance)
      + MIDDLE (within-class variant specification)
      + SUFFIX (decision archetype marker)
```

### Example Interpretation

| Token | PREFIX | MIDDLE | SUFFIX | Meaning (class-level) |
|-------|--------|--------|--------|----------------------|
| chedy | ch | e | -dy | M-A energy op, variant-e, routine decision |
| sheor | sh | e | -or | M-A energy op (tolerant), variant-e, fraction decision |
| ctor | ct | [null] | -or | M-C/D registry ref, fraction decision |
| okaiin | ok | a | -aiin | M-B op, variant-a, phase/flow decision |

---

## Semantic Achievement

**We can now decompose any Currier A/B token into:**

1. **What class of material** it operates on (PREFIX → M-A/B/C/D)
2. **What operational mode** applies (sister variant → precision/tolerance)
3. **Which specific variant** within the class (MIDDLE → ~1000 options)
4. **What decision type** is involved (SUFFIX → D1-D12 archetypes)

This is **complete class-level decomposition**.

We cannot say:
- "chedy means distill lavender"

But we CAN say:
- "chedy encodes a routine-decision (D6) operation on a precision-required (ch-) variant (e-) of a mobile-distinct (M-A) material class"

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C276 | Prefix-exclusive MIDDLEs = class-specific variants |
| C293 | MIDDLE as primary discriminator = variant specification |
| C423 | 80/20 split = most variants class-specific, some universal |
| C410.a | MIDDLE-driven sister preference = variant-level mode selection |

---

## Remaining Uncertainty

| Question | Status |
|----------|--------|
| Exact variant-to-variant mappings | Beyond structural analysis |
| Whether MIDDLEs form natural clusters | Not tested |
| Relationship between MIDDLE and section | Partially explored |

---

## Navigation

← [ccm_sister_pairs.md](ccm_sister_pairs.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

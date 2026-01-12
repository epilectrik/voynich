# C462: Universal MIDDLEs are Mode-Balanced

**Tier:** 3 | **Scope:** A->B | **Status:** OPEN | **Phase:** Perturbation Space

---

## Statement

MIDDLEs that appear across all four material classes (M-A, M-B, M-C, M-D) show balanced distribution between precision mode (ch-family) and tolerance mode (sh-family), while class-exclusive MIDDLEs strongly prefer precision mode.

---

## Evidence

| Property | Universal (18 types) | Exclusive (573 types) |
|----------|---------------------|----------------------|
| Sister preference | 51.0% precision | 87.3% precision |
| Suffix entropy | 3.08 bits | 2.97 bits |

Chi-squared = 471.55, p < 0.0001

---

## Structural Profile

Universal MIDDLEs exhibit:
1. **Mode-agnostic**: Occur equally in precision and tolerance modes
2. **Decision-flexible**: Higher suffix entropy (more decision outcomes)
3. **Material-independent**: By definition, appear in all material classes

---

## What This Does NOT Claim

- What physical phenomenon universal MIDDLEs represent
- Entity-level semantics (e.g., "temperature", "time")
- Why these specific 18 MIDDLEs are universal

---

## Three-Tier MIDDLE Hierarchy

This constraint supports a functional hierarchy:

| Tier | MIDDLEs | Behavior |
|------|---------|----------|
| Universal | 18 types (44% tokens) | Mode-balanced, suffix-flexible, material-independent |
| Bridging | 134 types (40% tokens) | Shared by property similarity (mobility/composition) |
| Exclusive | 573 types (17% tokens) | Mode-specific, suffix-constrained, material-dependent |

---

## Constraints Supported

- Refines C408 (sister pair equivalence classes)
- Consistent with C423 (prefix-bound vocabulary domains)
- Consistent with C293 (MIDDLE is primary discriminator)

---

## Saturation Note

This constraint, together with C461, represents the **maximum achievable internal resolution** for MIDDLE identification. The shared MIDDLE question is CLOSED: MIDDLEs can be classified by behavioral independence but not by entity semantics.

---

## Source

- Script: `phases/perturbation_space/universal_middle_properties.py`
- Data: `results/universal_middle_properties.json`
- Doc: `phases/perturbation_space/PHASE_SUMMARY.md`

---

## Navigation

<- [C461_ht_middle_rarity.md](C461_ht_middle_rarity.md) | [INDEX.md](INDEX.md) ->

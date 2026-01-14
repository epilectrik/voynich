# MIDDLE Zone Survival Analysis

**Status:** COMPLETE
**Date:** 2026-01-13
**Tier:** 3 (Exploratory)

---

## Pre-Registered Question

> "Do MIDDLEs exhibit stable, non-random survival profiles across AZC legality zones (C/P/R/S), after controlling for frequency, section, and prefix?"

---

## Result: CONFIRMED

| Metric | Value |
|--------|-------|
| AZC tokens analyzed | 8,257 |
| Qualified MIDDLEs | 175 (≥5 occurrences) |
| Optimal clusters | 4 |
| Silhouette score | 0.51 |
| P-value (vs null) | < 0.000001 |
| Frequency-controlled | 0.51 ± 0.04 |

---

## Cluster Profiles

| Cluster | n | Dominant Zone | C | P | R | S | Interpretation |
|---------|---|---------------|---|---|---|---|----------------|
| 1 | 47 | S (59%) | 0.14 | 0.07 | 0.21 | 0.59 | Boundary-surviving |
| 2 | 29 | P (75%) | 0.06 | 0.75 | 0.12 | 0.07 | Intervention-requiring |
| 3 | 25 | C (66%) | 0.66 | 0.17 | 0.13 | 0.05 | Entry-preferring |
| 4 | 74 | R (51%) | 0.23 | 0.17 | 0.51 | 0.09 | Restriction-tolerant |

---

## What This Shows

MIDDLEs exhibit stable, non-random preferences for specific legality regimes:

- **P-cluster** (n=29): 75% permissive zone - discriminators that require high intervention affordance
- **S-cluster** (n=47): 59% boundary zone - discriminators that survive even when intervention is locked
- **C-cluster** (n=25): 66% entry zone - discriminators that need setup flexibility
- **R-cluster** (n=74): 51% restricting zone - discriminators that tolerate progressive commitment

The effect survives frequency control, ruling out hub/tail artifacts.

---

## What This Does NOT Show

- ❌ MIDDLEs do not *force* positions (C313 intact: position constrains legality, not content)
- ❌ No A→B entry-level coupling (C384 intact)
- ❌ No semantic encoding (discriminators have *roles*, not *meanings*)
- ❌ No routing rule (this is survival preference, not placement causation)

---

## Structural Interpretation

> Currier A's discriminators are not only incompatible with each other - they are tuned to different *degrees of intervention affordance*, which the AZC legality field later enforces.

This is a **characterization refinement**, not a mechanism discovery.

---

## Cross-References (Tier 2)

| Constraint | Relationship |
|------------|--------------|
| C293 | MIDDLE is primary discriminator |
| C441-C444 | AZC legality projection |
| C475 | MIDDLE atomic incompatibility |
| C313 | Position constrains legality, not content |
| C384 | No entry-level A-B coupling |

---

## Tier 3 Status

This finding is documented as **Tier 3 Exploratory**:

- Statistically strong (p < 10⁻⁶)
- Survives frequency control
- Aligned with apparatus-centric interpretation
- Does NOT justify Tier 2 promotion (no invariant/necessity claim)

---

## Future Promotion Criteria

Could be promoted to Tier 2 if:
- Same zone-preference clusters found in another manuscript
- Mathematical necessity linking discrimination → zone is established
- Invariant across all conceivable registry designs

---

## Semantic Ceiling

This reveals MIDDLE-level legality patterns. It does NOT:
- Decode material identities
- Establish A→B semantic transfer
- Imply zones encode meaning

The cluster labels ("intervention-requiring", "boundary-surviving") are interpretive glosses, not referential claims.

---

## Files

| File | Contents |
|------|----------|
| `middle_zone_survival.py` | Analysis script |
| `results/middle_zone_survival.json` | Full results |

---

*Phase completed 2026-01-13*

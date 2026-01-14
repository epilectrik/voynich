# Zone-Material Coherence Test

**Status:** COMPLETE
**Date:** 2026-01-13
**Tier:** 3 (Exploratory)

---

## Epistemic Safeguard

> **"This phase tests coherence between two independent Tier 3 abstractions. A positive result strengthens interpretive plausibility but does not imply semantic encoding, referential meaning, or Tier 2 structural necessity."**

---

## Pre-Registered Question

> "Do discriminators that require higher intervention affordance also tend to occur in grammar regions associated with greater phase sensitivity?"

---

## Result: ORTHOGONAL

| Metric | Value |
|--------|-------|
| Currier A pairs analyzed | 23,630 |
| Zone-assigned MIDDLEs | 154 |
| Hypothesis matches | 1/4 |
| P-value (vs permutation null) | 0.852 |

---

## Zone Material Profiles

| Zone | n | M-A | M-B | M-C | M-D | Dominant |
|------|---|-----|-----|-----|-----|----------|
| C | 706 | 72.2% | 13.6% | 0.0% | 14.2% | M-A |
| P | 3,253 | 66.4% | 0.8% | 26.3% | 6.5% | M-A |
| R | 5,204 | 57.1% | 24.3% | 7.2% | 11.4% | M-A |
| S | 500 | 59.8% | 31.4% | 0.2% | 8.6% | M-A |

M-A (phase-sensitive, mobile - ch/qo/sh prefixes) dominates ALL zones.

---

## Hypothesis Test

| Zone | Predicted Class | Actual Dominant | Match |
|------|-----------------|-----------------|-------|
| P (high intervention) | M-A | M-A | YES |
| S (boundary-surviving) | M-D | M-A | NO |
| R (restriction-tolerant) | M-B | M-A | NO |
| C (entry-preferring) | M-C | M-A | NO |

Only 1/4 predictions matched, not different from random (p=0.852).

---

## What This Shows

Material behavior class (inferred from prefix) and zone survival profile (inferred from MIDDLE discrimination) are **orthogonal axes**.

The system apparently tracks two independent dimensions:

| Dimension | Encoded By | What It Captures |
|-----------|------------|------------------|
| Material type | PREFIX | Category of material |
| Handling requirement | MIDDLE zone survival | Intervention latitude needed |

This is structurally sensible: an apparatus-centric system might need to know both *what something is* and *how carefully it must be handled* - and these need not be the same thing.

---

## What This Does NOT Show

- No semantic decoding
- No material identification
- No refutation of either abstraction (both remain valid Tier 3)

The negative result means the axes are **independent**, not that either is wrong.

---

## Structural Interpretation

> Zone survival profiles and material behavior classes capture different aspects of the discrimination system. Discriminators are tuned to intervention affordance (zone survival) independently of the material classes they operate on (prefix).

This is consistent with:
- A system that can apply the same processing logic to different material types
- Intervention affordance being about **process dynamics**, not material identity
- Material class being about **what**, intervention affordance about **how**

---

## Cross-References

| Finding | Phase | Relationship |
|---------|-------|--------------|
| MIDDLE zone survival | MIDDLE_ZONE_SURVIVAL | Source of zone clusters |
| Material behavior classes | PROCESS_ISOMORPHISM | Source of M-A...M-D |
| MIDDLE incompatibility | MIDDLE_INCOMPATIBILITY | Discrimination layer |

---

## Files

| File | Contents |
|------|----------|
| `zone_material_coherence.py` | Analysis script |
| `results/zone_material_coherence.json` | Full results |

---

*Phase completed 2026-01-13*

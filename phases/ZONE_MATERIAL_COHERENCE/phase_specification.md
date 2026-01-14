# ZONE-MATERIAL Coherence Test

**Status:** PRE-REGISTERED
**Date:** 2026-01-13
**Tier:** 3 (Exploratory)

---

## Epistemic Safeguard

> **"This phase tests coherence between two independent Tier 3 abstractions. A positive result strengthens interpretive plausibility but does not imply semantic encoding, referential meaning, or Tier 2 structural necessity."**

---

## Pre-Registered Question

> "Do discriminators that require higher intervention affordance also tend to occur in grammar regions associated with greater phase sensitivity?"

Concretely:

> "Do MIDDLEs that survive predominantly in P-zones tend to co-occur with prefixes associated with phase-sensitive behavior in Currier B?"

---

## Background

Two independent abstractions of "material behavior" exist:

| Axis | Source | What it captures |
|------|--------|------------------|
| Material behavior class (M-A...M-D) | PROCESS_ISOMORPHISM | How grammar behaves under hazards |
| Zone survival class (P/S/C/R) | MIDDLE_ZONE_SURVIVAL | What legality affordance discriminators require |

These were derived independently using different data and methods.

---

## Hypothesis (to test, not assume)

| Zone Cluster | Expected Material Class | Rationale |
|--------------|------------------------|-----------|
| P-cluster (high intervention) | M-A (phase-sensitive, mobile) | Volatile materials need constant attention |
| S-cluster (boundary-surviving) | M-D (control-stable) | Robust materials survive constraints |
| R-cluster (restriction-tolerant) | M-B (uniform mobile) | Standard processing, progressive commitment |
| C-cluster (entry-preferring) | M-C (phase-stable, exclusion-prone) | Setup flexibility for tricky materials |

---

## Method

1. **Input A:** MIDDLE sets for each zone-survival cluster (from MIDDLE_ZONE_SURVIVAL)
2. **Input B:** Observed prefix co-occurrence for those MIDDLEs in Currier A tokens
3. **Mapping:** Map prefixes → material behavior classes using PROCESS_ISOMORPHISM definitions
4. **Test:** Measure non-random enrichment using permutation/frequency-matched controls
5. **Output:** Effect size, p-value, alignment verdict

---

## Success Criteria

- Statistically significant alignment (p < 0.05)
- Effect survives frequency controls
- At least 2/4 cluster-class pairs show predicted alignment

---

## Failure Criteria

- No significant alignment
- Effect driven by frequency artifacts
- Random distribution across clusters

---

## Interpretation Rules

### If PASS:
> "Two independently derived abstractions of material behavior are statistically aligned."

This strengthens apparatus-centric interpretation. Does NOT name solvents.

### If FAIL:
> "Material behavior and discrimination affordance are orthogonal axes."

This implies the system distinguishes *what a thing is* from *how cautiously it must be handled*.

---

## Forbidden Outputs

- Specific substance identifications
- Claims like "this MIDDLE = ethanol"
- Tier 2 promotions without independent corroboration
- Semantic encoding claims

---

## Files

| File | Contents |
|------|----------|
| `zone_material_coherence.py` | Analysis script |
| `results/zone_material_coherence.json` | Full results |

---

*Phase pre-registered 2026-01-13*

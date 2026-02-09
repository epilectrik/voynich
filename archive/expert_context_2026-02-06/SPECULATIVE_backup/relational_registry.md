# Currier A as Relational Registry, Not Frontier Catalogue

**Tier:** 3 | **Status:** SYNTHESIS | **Date:** 2026-01-10 | **Updated:** 2026-01-10

> **WARNING: This document is Tier 3 speculative interpretation.**
> It synthesizes fit results (F1s and one F2). It makes no new structural claims.
> Treat as orientation, not fact.

---

## Summary

Four independent fits (F-A-005, F-A-007, F-A-008, F-A-009) converge on a consistent pattern:

1. **Vocabulary selection** favors cross-domain comparability (F-A-007)
2. **Effort/repetition** does not differentially reinforce relational entries (F-A-005, F-A-008)
3. **Physical layout** provides weak scaffolding for comparison (F-A-009 - **F2 SUCCESS**)

This suggests Currier A functions as a **relational registry** (enables comparison across contexts) with **layout-based scaffolding** rather than internal reinforcement mechanisms.

---

## Evidence (F1 Fits)

### F-A-005: Scarcity-Weighted Registry Effort

**Hypothesis:** When vocabulary is scarce (few legal MIDDLE options), the registry expends more effort (repetition, articulators).

**Result:** F1 (NULL - section-specific only)
- Effect exists in H section (r=0.22, p=0.03)
- No effect in P section (r=0.05, p=0.84)
- Fails section robustness criterion

**Implication:** Effort adaptation is not a universal registry property. The registry does not systematically compensate for vocabulary scarcity across all domains.

### F-A-007: Forbidden-Zone Attraction

**Hypothesis:** Currier A entries cluster near structural boundaries (prefix-exclusive vocabulary).

**Result:** F1 (NULL - opposite effect found)
- Observed entries: 0.591 mean boundary distance
- Random composites: 0.176 mean boundary distance
- Difference: +0.415 (opposite of attraction)
- 48% of observed tokens use universal MIDDLEs (vs 8% random)
- 8% use exclusive MIDDLEs (vs 53% random)
- Effect robust across H, P, T sections (all p < 0.0001)

**Implication:** The registry systematically **avoids** exclusive vocabulary and **prefers** cross-domain valid vocabulary. This is deliberate selection, not random sampling.

### F-A-008: Repetition as Relational Stabilizer

**Hypothesis:** Universal-reference entries receive more internal reinforcement (repetition).

**Result:** F1 (NULL - direction correct but not significant)
- Universal entries: 2.16 mean repetition
- Exclusive entries: 1.98 mean repetition
- Difference: +0.19 (correct direction but p = 0.198)
- Correlation (universality vs repetition): rho = -0.006, p = 0.82

**Implication:** Relationality is enforced through **selection only** (F-A-007), not through repetition reinforcement. The registry chooses universal vocabulary but does not additionally stabilize those entries.

### F-A-009: Comparability Window (F2 SUCCESS)

**Hypothesis:** Entries with similar universality band cluster in manuscript space.

**Result:** F2 (SUCCESS - all windows significant)
- +/-1 window: +4.31pp, p = 0.0001
- +/-2 window: +3.31pp, p < 0.0001
- +/-3 window: +3.05pp, p < 0.0001
- +/-5 window: +2.59pp, p < 0.0001
- SHARED entries are 34% closer to each other than expected

**Implication:** Relational comparison IS scaffolded - but by **physical layout**, not by repetition or vocabulary emphasis. Entries with similar universality band cluster together, creating weak topological affordances for human comparison.

---

## The Convergence

Four fits point to the same underlying pattern:

| Fit | Tier | What Tested | Result |
|-----|------|-------------|--------|
| F-A-005 | F1 | Scarcity → effort compensation | Section-specific only |
| F-A-007 | F1 | Boundary/frontier attraction | Opposite: interior preference |
| F-A-008 | F1 | Repetition → relational stabilization | Null: uniform repetition |
| F-A-009 | **F2** | Layout → comparability scaffolding | **SUCCESS: 34% clustering** |

Together:
> The registry is not optimized for recording distinctions that the grammar cannot track.
> It is optimized for recording **stable reference points that remain valid across multiple grammatical domains**.

---

## Two CFR Flavors (One Falsified)

This pattern resolves an ambiguity in the Control-Flow Reference (CFR) model:

### CFR-A: Frontier Recording (FALSIFIED)
> "Write down the edge-cases where grammar breaks, so humans know what to watch for."

This would predict:
- Preference for exclusive vocabulary (maximizes specificity)
- Boundary attraction (records what grammar cannot reach)
- Effort compensation under scarcity (harder cases need more work)

**F-A-007 falsifies this decisively.** The opposite pattern holds.

### CFR-B: Relational Differentiation (SUPPORTED)
> "Write down stable reference points that allow humans to compare cases that otherwise look the same."

This predicts:
- Preference for universal vocabulary (remains valid across contexts)
- Interior selection (stable under domain shifts)
- Section-specific effort (different domains have different needs)

**Both fits are consistent with CFR-B.**

---

## Why This Matters (Interpretation Only)

If CFR-B is correct, then Currier A serves a specific cognitive function:

> **Externalize distinctions that the executable grammar (B) intentionally collapses.**

Currier B clamps risk globally and allows variation locally. It deliberately refuses to track certain distinctions because they don't affect hazard.

Currier A records those same distinctions - but in vocabulary that remains **recognizable across prefix domains**, so an experienced operator can:
1. Look at a B program step
2. Recognize which A reference points apply
3. Determine if "this step" differs from "that step" in ways B ignores but humans must know

This is not translation. This is **relational lookup**.

---

## Alignment with Existing Constraints

This interpretation is consistent with (not derived from):

| Constraint | Relevance |
|------------|-----------|
| C232 | Section-conditioned but class-uniform (sections differ in content, not structure) |
| C238 | Global schema, local instantiation (one registry design, many applications) |
| C253 | All blocks unique (no reuse = each entry is a distinct reference point) |
| C281 | Components SHARED (universal vocabulary is available) |
| C293 | MIDDLE is discriminator (selection happens at MIDDLE level) |
| C385 | Structural gradient in A (not all entries are equal) |

---

## What This Does NOT Establish

This interpretation does NOT:
- Assign meaning to any token
- Identify what is being referenced
- Establish cross-system lookup (C384 still holds: no A↔B entry coupling)
- Create new constraints
- Override any Tier 0-2 claim

It provides orientation for understanding **what kind of artifact this is**, not what it says.

---

## The Emergent Coherence

Currier A and Currier B now form a recognizable design philosophy:

| System | What It Does | Vocabulary Strategy |
|--------|--------------|---------------------|
| **B** | Clamps risk, allows recovery | Domain-specific precision (49 classes) |
| **A** | Externalizes collapsed distinctions | Cross-domain validity (universal MIDDLEs) |

Together:
> **Fix what must not vary.**
> **Allow variation where recovery is possible.**
> **Externalize only what humans must compare across contexts.**

This is not an analogy. It is a convergent design visible only because multiple fits failed in consistent directions.

---

## Suggested Next Fits

If this synthesis is correct, these predictions should hold:

1. **Universal vocabulary in clusters:** Do clustered entries (C424) preferentially use universal MIDDLEs?
2. **HT correlation with universality:** Does Human Track annotation correlate with universal vocabulary?
3. **AZC placement bias:** Does AZC bridge text favor universal A-vocabulary?

These would be second-order fits testing the relational registry hypothesis.

---

## Governance

This document is:
- **Tier 3** (speculative synthesis)
- **Not a constraint** (does not restrict)
- **Discardable** (if contradicted by Tier 0-2 evidence)
- **Orientation only** (helps interpret, does not prove)

---

## Navigation

← [README.md](README.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

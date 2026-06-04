# PHASE 749 — Arrangement-Metalayer Architecture Map

**Status:** SCOPED (not yet run)
**Date:** 2026-06-03
**Type:** Forward structural characterization (death-zone-safe; measurement-level)
**Builds on:** C2071–C2073 (zodiac = kernel-free arrangement metalayer, Rosettes-family), C1126–C1128 (Rosettes metalayer), C1502/C1814 (o-HEAD arrangement), C757 (AZC zero-kernel)

---

## Question

The zodiac was just characterized as a **kernel-free arrangement/reference layer in the Rosettes/AZC family** (C2071–C2073, human-signed-off interpretation). That raised a question it didn't answer:

> **Is the manuscript's "index/arrangement" layer ONE unified structure, or SEVERAL differentiated layers?**

Concretely: do the **cosmological AZC folios (f67–f69)**, the **rosettes foldout**, the **zodiac**, and the **pharma section** all belong to one arrangement-metalayer family (same atom-profile, same B-hub targeting, kernel-free) — or do they differentiate into distinct sub-layers?

This characterizes the manuscript's **macro-architecture**: how many functional layers exist, and which folios are *index* vs *registry* vs *execution*.

---

## Pre-registered tests (measurement-level, death-zone-safe)

1. **Per-section atom-HEAD-profile.** Compute the 6-cat HEAD profile {a,e,o,k,t,headless} for each candidate section (zodiac, cosmological-AZC, rosettes-by-entity-type, pharma-labels, pharma-text). Place all in HEAD-profile space against the anchors (Rosettes, Currier-A, Currier-B). **Test:** do they all cluster in the kernel-free arrangement neighborhood, or split?

2. **Kernel-density per section.** Confirm/measure kernel-HEAD fraction per section. Arrangement metalayer ⇒ k≈0 (cf C757). Differentiation ⇒ some sections carry kernel.

3. **B-hub targeting per section.** Which B-folios does each section's vocabulary share with? **Unified index** ⇒ all converge on the same hub (the Rosettes/zodiac f40 hub). **Differentiated** ⇒ distinct targets. **CAVEAT (locked):** the f40-hub convergence carries the **C1133 vocab-size artifact** — use a **frequency-matched null** before claiming specific targeting (the lesson from C2073/C2074-dropped-leg).

4. **Unification criterion (pre-registered):** ONE unified index ⇔ (a) all sections within JSD < 0.05 of each other in HEAD-profile AND (b) all converge on the same B-hub above a frequency-matched null. Otherwise → differentiated layers (report the partition).

---

## Discipline guards

- **Measurement-only.** Atom-profile, kernel-density, hub-targeting are structural measurements (survive the operational-specificity death zone). The *referent* of any index (what it indexes) is walled (C171) — NOT in scope.
- **Frequency-matched null mandatory** for any hub-targeting claim (C1133; the random-null is wrong — see the C2074-dropped-leg and the just-closed compatibility family, which fell entirely to frequency-blind/wrong nulls).
- **No co-occurrence-graph spectral claims** without a clique-preserving bipartite null (the PHASE_748 lesson — the entire A-side compatibility family was a configuration-model-on-affiliation-network artifact).
- **Hold interpretation.** "One index / several layers" is a structural finding; any functional reading ("this layer indexes materials") needs the human (echo-class).

---

## Anchors / data

- Sections: zodiac (Z), cosmological AZC (f67–f69), rosettes (`data/rosettes_annotated.json`), pharma (f88–f102).
- Profile anchors: Rosettes (C1814), Currier-A, Currier-B.
- Scans available: `sources/voynich_scans/` (for codicological cross-check only; image channel is decoupled per C138/C1824 — not a grounding channel).

---

## Status: COMPLETE (2026-06-03)

**Result — the grand "unified index" framing deflated under the expert differential check; two narrowed measurements registered.**

- **Test 1 (kernel-HEAD, Wilson CIs):** index sections (AZC+Rosettes) kernel-depleted 0.010–0.043 < Currier-A 0.057 < pharma 0.087 < Currier-B 0.134 — a **GRADIENT, not a partition** (pharma intermediate). New: **pharma P-text is kernel-bearing, NOT an index layer → C2074**. Zodiac/Rosettes kernel-freeness = corroboration of C757/C1126/C1127 (not new).
- **Test 3 (composition-matched null + per-section z):** NO index section targets any B-folio above the null (z: ZODIAC −1.4, COSMO −0.2, ROS-RING +0.8 NS, ROS-LABEL −3.8 self-folio). Apparent f113r-hub = C1133 vocab-size artifact. **Extends C2073 to the whole index → C2075**.
- **HELD (→human):** "the index is ONE self-contained kernel-depleted lexically-isolated reference layer, internally heterogeneous (C430/C1519), not a B-routing table." Echo-class.

**Registered:** C2074 (pharma kernel-bearing, gradient), C2075 (full-index no-B-targeting). **Discipline win:** the mandatory composition-matched null caught the would-be "unified B-hub" as the C1133 artifact — the PHASE_748 lesson fed forward and prevented a repeat. Data gap: pharma jar-labels not located (L-placement empty on f88-102).

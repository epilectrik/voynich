# Pre-Registered Predictions: Layfield & Davis Paper 2 (LSA → Codicological Structure)

**Locked:** 2026-06-08, before publication.
**Target:** the forthcoming second Layfield & Davis paper, announced in DHQ 20.1 (000857):
*"in forthcoming work (currently under review), the authors will present more granular results
that consider how LSA can shed light on the original codicological structure of the manuscript."*
**Purpose:** blind external validation in BOTH directions. Their toolchain (LSA cosine similarity,
ZL transliteration, k=75 SVD) is fully independent of this project's (H-track EVA, morphology,
constraint system). If predictions made from our constraint base score well against their
independent results, that is external validation of our order/structure model; where they miss,
the misses localize genuine errors in our model. Predictions are scored CONFIRMED / PARTIAL /
REFUTED / NOT-ADDRESSED when the paper publishes. Confidences are honest forecasts, not hedges.

**Independence note:** nothing in this file uses non-public information about their paper beyond
the single sentence quoted above and their published Paper 1.

---

## Predictions

**P1 (90%) — The herbal unshuffling is the centerpiece.** The paper's principal reordering claim
concerns the herbal section: separating the currently-interleaved Currier-A (Scribe 1) and
Currier-B (Scribe 5) herbal folios into originally distinct gatherings, with LSA similarity
reuniting same-scribe folios across current binding positions.
*Grounding:* Davis's published codicological position; our C239 (A/B folio-disjoint, designed),
C346 (adjacent-A entries 1.31× vocabulary coherence), this season's Herbal-A adjacency structure
(corr −0.178 surviving the Currier split).

**P2 (75%) — Herbal-A yields local runs, not a confident global sequence.** Within Currier-A
herbal material, their LSA-supported ordering claims will be at the level of contiguous LOCAL
clusters/runs (2–7 folios) and bifolio adjacencies, with explicit hedging (or instability) about
any single full-sequence reconstruction.
*Grounding:* C424 (clustered contiguous runs, autocorr 0.80, working-memory-sized), C346 local
adjacency, our weak global gradient (−0.178 ≈ 3% of pair variance).

**P3 (80%) — Quire 13 (Biological/balneological) gets NO strong text-internal reordering.**
Despite Q13 being the most famous misbinding candidate, their LSA evidence for any *specific
internal* re-sequencing of f75–84 will be weak, ambiguous, or explicitly deferred to physical
(non-textual) evidence — because the section is textually homogeneous.
*Grounding:* our receptary results (Balneo folio-order flat: corr +0.03, p=0.62; C1834 paragraph
resets; C963 body homogeneity); their own Paper-1 finding of uniformly high Biological cohesion —
a reordering method needs gradients, and Bio has none.

**P4 (80%) — Same for Quire 20 / Stars:** no robust LSA-internal folio re-sequencing; any claim
there is at quire/bifolio-placement level, not folio-order level.
*Grounding:* Stars folio-order flat (corr +0.01, p=0.56); C1839 (local coherence WITHOUT global
ordering).

**P5 (70%) — Pharma is affiliated with Herbal-A.** The pharmaceutical section shows strong LSA
affinity to Currier-A herbal material (same vocabulary stratum), and the paper proposes or
supports an original association/adjacency of pharma gatherings with herbal-A material.
*Grounding:* shared Currier-A vocabulary stratum; C2074 (pharma at the A-side of the kernel
gradient); the jar↔plant iconographic literature.

**P6 (65%) — Reconstructed gatherings respect scribal-hand boundaries.** Their proposed original
structure essentially never mixes different-scribe folios within one reconstructed gathering
(beyond the explicit unshuffling of known-mixed quires). LSA is vocabulary-driven and vocabulary
tracks hand≈section.
*Grounding:* PHASE_702 hand≈section structural confound; C1029 section-conditioned composition.

**P7 (85%) — No narrative arc.** The paper makes no claim of a recovered *progressive reading
order* (development/argument across the manuscript), and if they test directional development it
comes back null. The recovered organization is topical/codicological grouping only.
*Grounding:* our reference-not-narrative result (forward-reuse z=+1.0 vs English control +12.2);
C1727 (ordering information is structural, not compositional); C1399/C1400.

**P8 (60%, risky) — At least one specific bifolio swap/inversion proposal inside an A-section
quire, supported primarily by LSA — and NO bifolio-level proposal inside a B-section quire that
rests primarily on LSA (B proposals, if any, lean on codicology).**
*Grounding:* signal exists in A (C346/C424), absent in B (receptary); their validation control
(Speculum chapters) behaves like A-material, not B-material.

**P9 (75%) — Cosmological/zodiac pages are treated as standalone topical units** (no text-based
within-cosmo reordering; foldout/quire placement discussed codicologically). Their Paper 1
already found below-average page-break similarity there (each page its own topic).
*Grounding:* their own Paper-1 result; our C2068/C2071-era zodiac characterization (per-diagram
self-containment).

**P10 (70%, risky) — The astronomical/cosmological + Rosettes material forms its own LSA block,
NOT strongly affiliated with either herbal-A or recipe-B vocabulary.** If they place it, they
place it as a distinct unit rather than merging it into either main stratum.
*Grounding:* C760/C321 (AZC lexical isolation), C2075 (index layer does not target B), C1125
(Rosettes section-T correlation is a vocabulary-size artifact).

---

## Meta-predictions about the method (scored only if the paper reports the relevant analysis)

**M1 (70%):** If they compare reordering performance across sections against their Speculum-style
control, the herbal performs comparably to the control while Biological/Stars perform markedly
worse (they may attribute this to "strong cohesion" rather than to order-freedom).
**M2 (60%):** Conjugate-leaf (same physical bifolium) text-similarity validates in A-material and
fails to validate in B-material.

---

## Scoring protocol (locked)

When the paper publishes: score each P/M as CONFIRMED / PARTIAL / REFUTED / NOT-ADDRESSED, by the
plain reading of their published claims (quote the relevant passage per item). Pre-committed
interpretations:

- **High score on P1/P2 + P3/P4 (the A-signal/B-null pattern):** external, toolchain-independent
  validation of the project's central order finding (Herbal-A = ordered reference; Currier B =
  receptary). Registrable as corroboration on existing constraints (C346/C424/C1839-family), not
  as new claims.
- **REFUTED P3 or P4 (robust text-internal reordering inside Bio or Stars):** genuine challenge
  to the receptary model — would require reconciling their gradient with our flat results
  (instrument difference? our power? their overfit?). Pre-commit: treat as a real anomaly, not
  noise; run their claimed ordering against our within-section permutation framework.
- **REFUTED P7 (they recover a progressive narrative order):** direct conflict with the
  reference-not-narrative result; same reconciliation obligation.
- **NOT-ADDRESSED items carry no weight either way.**

Honest exposure statement: P1/P9 lean substantially on Davis's already-public positions and their
own Paper 1 (lower information value if confirmed); P2, P3, P4, P8, M1, M2 are the genuinely
risky, model-derived predictions — they are where our constraint system sticks its neck out.

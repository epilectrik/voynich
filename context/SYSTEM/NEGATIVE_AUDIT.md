# Negative Audit (2026-06-05)

**Status:** OPEN (pass 1: C171 eliminations, death-by-stage, thermal-sim wall, + dark-pipeline material re-tests [2 confirmed walls])
**Purpose:** the project audits false POSITIVES ruthlessly (Verdict Gate, echo-class, expert
validation, promotion tiers, the PHASE_748 sweep) and false NEGATIVES not at all. So false
positives die under scrutiny; false negatives get CITED and persist as always-loaded walls
(falsifications.md "do not retry"; C171 "ONLY closed-loop control"; the "death zone";
framework-as-null; C2052-as-general-law). 5–15% of audited Tier-2 positives were flawed;
negatives have never been audited. This file is the negative-audit record and the standard.

**A negative reclassification REDUCES foreclosure. This audit registers no new negatives.**

---

## The standard (symmetric, + the one thing only negatives need)

The project controls α (false-positive rate) everywhere and **β (false-negative rate) nowhere.**
A null is uninterpretable without a power statement. A negative may **FORECLOSE** (be cited as
"do not retry / eliminated / death zone") only if it clears all four:

1. **Powered** — states the effect size it could have detected at stated power. An underpowered
   null is absence-of-evidence, not evidence-of-absence.
2. **Correct null** for the claim class (token-shuffle for adjacency not char-5-gram per C2066;
   within-folio for composition; section-perm for confound; N-match for imbalance).
3. **Reproducible** under the current pipeline (transcriber filter, denominators, `voynich.py`).
4. **Scope-locked** to exactly the hypothesis / layer / **direction** tested.

Fail (1) → SUSPECT. Fail (2)/(3) → SUSPECT + clean re-test. Fail only (4) → OVER-GENERALIZED
(restrict scope; core stays SOLID).

## Anti-circularity firewall

Same-model auditors carry the priors under audit. Flag on the test's **metadata only** —
threshold provenance (grep `# Adjusted`, hardcoded cutoffs), null type vs claim class, N/power,
reproducibility, **direction-tested vs direction-cited**, verification-field contradictions,
multiplicity — produced *before* reasoning about the conclusion. **Agreement is the contaminated
channel; it stays out of the flagging step.**

## The audit's OWN locked kill-conditions

- **SOLID is default; downgrade requires a NAMED mechanical defect + artifact**, never a vibe
  (symmetric with the anti-dismissal rule).
- **Control group:** cipher and constructed-language must stay SOLID. If the audit flips either,
  **the audit is broken** (each has ≥2 independent adversarial kills).
- **Base rate:** expect ~25–35% flagged. **>50% flip rate = the auditor is mis-calibrated**, not
  the corpus.
- **Downgrade ≠ re-open:** a wall comes down only when a properly-powered re-test *replaces* it.
  Removing a wall and putting nothing there is worse than a flawed wall.
- **Re-test survival:** ≥40% of re-tested SUSPECTs should *survive* — if re-tests confirm
  everything, they were designed to confirm.

---

## DISPOSITION 1 — C171 "12 eliminated → ONLY closed-loop control"

Mechanical criterion: does the elimination cite a *discriminating test* or assert an *absence*?

| Elimination | Reason as written | Class |
|---|---|---|
| Cipher/hoax | transforms DECREASE MI | **SOLID** (directional test; C2017/C2055 corroborate) |
| Glassmaking/metallurgy | wrong hazard topology | **SOLID** (the one real contrast test — calcination negative control PS-4/BS-4) |
| Fermentation | "no time-dependent markers" | **REAL but mis-cited** — re-cite from C1900 (fingerprint falsified); retire the absence wording |
| Encoded language | "Phase X.5: 0.19% reference rate" | **TAINTED** — X.5 is the C131-retracted phase (invented threshold + 3.2× transcriber inflation); conclusion survives on cipher/C2055; **strike the 0.19% statistic** |
| Recipe/pharmacology | "no batch boundaries" | **OVER-GENERALIZED** — only a *format* tested (FSS); contradicted by the live recipe-matching program |
| Discrete batch ops | "no end markers" | **OVER-GENERALIZED / contradicted** — C1237/C1295 find -am termination |
| Herbarium/taxonomy | "no identifier tokens" | **SUSPECT** — unstated threshold; partly propped by swap-invariance |
| Medical procedure | "no patient-response branching" | **PURE ABSENCE-ASSERTION** |
| Astronomical calc | "no computational primitives" | **PURE ABSENCE-ASSERTION** |
| Ritual/symbolic | "no conditional structure" | **PURE ABSENCE-ASSERTION** |
| Educational text | "no definitions or examples" | **PURE ABSENCE-ASSERTION** |
| Dyeing/mordanting | "wrong phase structure" | **PURE ABSENCE-ASSERTION** (no contrast test) |

**Tally:** 2 SOLID, 2 real-but-mis-cited, 3 over-generalized/suspect, **5 pure absence-assertions.**
Only **2 of 12** alternatives were eliminated by a discriminating test.

**Disposition:** downgrade **"ONLY closed-loop control survives"** → *"best-supported among tested
alternatives; only 2 of 12 alternatives eliminated by a discriminating contrast test, 5 by
untested absence-assertion."* **The frozen Tier-0 structural conclusion (it IS a closed-loop
control grammar) is UNTOUCHED** — only the exclusivity overlay weakens.
**Kill-condition check:** control group held (cipher SOLID); 5/12 pure flips = 42% (< 50%);
named defect per flip. ✓

---

## DISPOSITION 2 — the "death zone" (operational-specificity reliably dies)

Death-by-stage classification (where each documented death actually died):

**REAL (discriminating / external-disconfirmation) — keep:**
- C2027 (family-stratified discriminating control)
- Sustain-vs-phase-switch (alternation-slot follow-up)
- Trajectory-encoded (*survived all internal controls*, died at Codicillus external grounding)
- Mensural notation (external lag-ratio: +0.18 vs Voynich ±0.66)
- qotar morphological-clustering (Phase 689 same-stem-density direct prediction, 1.7% vs >30%)

**PROPOSAL / COMPOSITION-stage (killed before any external prediction) — self-fulfilling:**
- k-e-depth thermal regimes (within-folio shuffle)
- triple-i iteration encoding (within-folio shuffle)
- hh intense-monitoring (composition controls)
- cardinality-anchors-generalize (within-folio shuffle p=0.67)
- cold-read coherence, 2026-06-05 (floor — no external test ever built)

**Net: ~half real, ~half proposal-stage.** The canonical 2026-05-16 quartet is 4/4 REAL (two
survived every internal control and died only on external corpora) — so the death zone is **not a
fiction**. But ~half the broader record is composition-null kills that never reached a test.
Counter-evidence: fch/cs (mercury/gold) were demoted but **recovered signal on careful retest** —
deaths partly methodological.

**Disposition:** the death zone is **partly real and badly over-applied.** Keep it as evidence
that operational interpretations have a low survival rate *under discriminating/external tests*.
**RULE: a proposal-stage death (within-folio shuffle / composition / floor) may NOT be cited to
foreclose a new hypothesis that has an external test attached.** Only discriminating/external
deaths count as evidence the class is empirically hard. Keep the external-test bar (earned by the
quartet); drop the proposal-stage pre-kill (unearned).

---

## DISPOSITION 3 — the thermal-sim wall (C998 / C999, "designed not emergent")

C998/C999 tested **forward** (can analog physics / discretization *generate* the Voynich
topology? — no, median 3/10, null models equal). SOLID for that direction. But the conclusion
"designed, not emergent" + C998's "any physical interpretation must explain the discrete encoding
layer" is cited to foreclose the **inverse** direction — does the *fixed* topology map
isomorphically to a physical process state-machine? — **which was never tested.** A *designed
control instruction-set* is expected to be isomorphic to the process it controls; "designed not
emergent" is compatible with, not contradictory to, the inverse.

**Disposition:** C998/C999 are **SOLID for forward-generation** and **OVER-GENERALIZED if cited
against inverse structure-matching.** Scope-restrict to forward-generation. **This RE-OPENS the
architectural-isomorphism / physical-reconstruction direction** — scoped to *architectural/physical*
matching (text-statistical corpus matching stays exhausted at the Latin-subdomain level per C2052 /
`feedback_text_statistical_methods_generic_at_domain_level`).

---

## DISPOSITION 4 — semantic ceiling for material recovery via the dark pipeline: TESTED, WALL HELD

crazy's pre-registered bet (the dark pipeline carries a hidden material-reference layer; the
constraint's own "from internal analysis ALONE" caveat permits external grounding) was run on
**two independent externally-grounded instruments** over the 16/14 matched-recipe folios, and
**failed both:**

1. **Cross-folio Mantel** (dark-MIDDLE Jaccard distance vs material-class-match, 14 folios):
   r = **−0.086** (wrong sign, |r|<0.10); fails full label-perm null (p=0.24) AND within-section
   perm null (p=0.51). Dark-MIDDLE overlap tracks **section** (r=0.49, = C1148), not material. The
   built-in positive control (section) fires → the instrument detects signal; the material signal
   is simply absent.
2. **Folio-local count** (does the dark layer scale with recipe material diversity, controlling
   folio length): material→DARK = **−0.32** (n.s.; −0.51 controlling recipe length, marginal /
   not multiple-comparison-robust) — null-to-negative, wrong direction. Control (material→CORE ≈ 0)
   and discriminator (operation→DARK ≈ 0) both null. Dark count is **folio-length-driven**
   (+0.665), not recipe-content-driven.

**Verdict: WALL CONFIRMED.** The dark pipeline does not encode materials in any measurable form
(not as a shared lexicon, not as count-scaling). A material-naming layer invisible to *both*
sharing and count is, operationally, not a material-naming layer. The semantic ceiling for
material recovery via the dark pipeline is now **tested by two instruments, not asserted** — an
over-cited wall converted to a *tested* wall.

**Audit calibration check (re-test-survival, the load-bearing one):** the rule was that ≥40% of
re-tested SUSPECTs must SURVIVE, else the re-tests were designed to confirm. **2 of 2 dark-pipeline
re-tests held.** Combined with 2 downgraded walls (C171 "ONLY", thermal-sim direction), the audit
has both loosened and confirmed walls → **calibrated, not a reflexive purge.**

**Still OPEN (not closed by this):** the dark pipeline *is* an identification layer (C1135–C1141) —
it names something folio/section-local; just not the recipe's material inventory. A post-hoc
pattern (dark proliferates in single-substance *iterative* procedures — ferment multiplication,
mercury coagulation — and is depleted in multi-material recipes) is a candidate "**names
intermediate states/products, not input materials**" hypothesis → pre-registered separately in
`phases/DARK_INTERMEDIATE_STATES/PRE_REGISTRATION.md`. Operational-story-first caution applies; it
is a noticing, not a result.

## DISPOSITION 5 — "stateless per-line" cluster (C670/C673/C681/C1031) measured CROSS-VOICE pre-Mode-discovery

**Trigger:** noticed C1031 (FL cross-line null, 2026-02-14) **predates the Mode A/B discovery** (C1258, Phase 450, 2026-02-24) and was measured across both suffix-mode voices — the same C670 artifact C1258 later named ("C670's adjacent-line null measured across voices, not within them"). The experts reproduced the gap: when reasoning about line independence they cited C670/C1031 without surfacing the Mode A/B constraints, despite having them embedded. **The human caught it** (same-model review reproduces the registry's blind spots; cf. [[feedback_same_model_review_not_echo_defense]]).

**Retests:**
- (a) **C673 within-Mode-B** (crude y-terminal proxy): CC-trigger self-transition 0.711 vs within-folio-Mode-B shuffle 0.723, **z=−1.9, p=0.98 → INCONCLUSIVE** (crude-proxy null attenuates toward null; needs C1231 centroids). Does not extend C673.
- (b) **Nested-null ladder** on within-Mode-B thermal (e_depth) + loop continuity: survives folio-shadow null and length-residualization (z~4.3); then the **lag-1-vs-lag-2 within-paragraph discriminator is FLAT** (e_depth lag1 .356/lag2 .332/lag3 .362; lag1−lag2 +0.024, 95% CI [−.058,+.106]; loop flat too) → continuity is **paragraph-level (C1967), not line-to-line.** *(Method note: a within-paragraph SHUFFLE over-controls the negative — destroys short runs — so the lag-1-vs-lag-2 comparison, not a shuffle, is the load-bearing discriminator. lean caught a first-pass "dissolves" over-claim on the z=1.6 loop channel.)*

**Verdict:** re-derives **C681** (folio/paragraph-mediated, not line-to-line) + **C1834** (paragraph reset) + **C1967** (thermal-by-paragraph). **Registered NOTHING new.** Net durable output: (1) the methodology rule → [[feedback_cross_line_b_tests_within_voice_within_paragraph]]; (2) inline SCOPE tags added to the INDEX rows for C670/C673/C681/C1031/C1260 (so the experts' embedded table carries the Mode A/B caveat — the actual fix for the blind spot, since experts read INDEX rows not constraint files) + matching `## Scope note` blocks in those five files. **DO NOT RE-RUN.** A positive within-voice CC-coupling claim would require faithful C1231 mode assignment, not the y-terminal proxy.

## Files edited this pass

- `C171_closed_loop_only.md` — audit annotation; "ONLY" → scoped; X.5 statistic retired; eliminations tagged.
- `CORE/falsifications.md` — self-sealing clause softened; recipe/pharmacology + thermal-sim entries scope-restricted; pointer here.
- `C998_analog_physics_topology_divergence.md` — inverse-direction scope note.

## Pending (next passes)

- The always-loaded **death-zone qualifier** in `CLAUDE.md` + `SYSTEM/RIGOR_AND_FAILURE_TAXONOMY.md`
  (master/instruction files — apply Disposition 2's rule there; confirm with human first).
- **C2052** scope (one matcher, not all matching) — still to audit.
- **Semantic-ceiling-as-deployed:** the *material-via-dark-pipeline* sub-question is now CLOSED
  (Disposition 4, wall held, 2 instruments). The broader "is the ceiling over-cited beyond its
  'from internal analysis ALONE' scope" question remains open for *other* channels (e.g. RI
  instance-layer, externally-grounded recovery via a true Rosetta key — not internal analysis).
- Mechanical sweep of the specific-claim falsification table for the suspect signatures.

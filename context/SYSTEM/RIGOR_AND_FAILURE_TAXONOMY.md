# Rigor & Failure Taxonomy — How to Analyze an Undeciphered Corpus Without Fooling Yourself

**Version:** 1.0 | **Date:** 2026-06-04 | **Status:** Consolidation (the project's transferable epistemic asset)

This document consolidates the discipline the project developed across ~750 phases and ~2050 constraints. It is the most **transferable** thing the project produced — immune to every ceiling on the analysis itself (it is *method*, not *finding*). Complements `METHODOLOGY.md` (the operational codebase how-to: scripts, data loading); this doc is the **epistemic** layer: how findings are established, how they fail, and how the failures were caught.

> **The one-sentence summary:** *at maturity, the null is load-bearing and a clean fit to the existing framework is a prior toward NULL, not confirmation.* Everything below elaborates that.

---

## I. Core stance

1. **Tiers.** 0 = frozen structural fact; 1 = falsified (negative knowledge, preserved); 2 = validated measurement; 3 = conditional interpretation; 4 = exploratory. **Only 0–2 constrain the model.** Tier 0 rests on the B-side control-program grammar and has never moved.

2. **Measurement survives; mechanism/referent dies.** Structural *measurements* (distances, distributions, nulls) survive. *Operational interpretations* ("encodes X," "represents Y," "tracks Z") reliably die — this is the **operational-specificity death zone**, now a documented regularity (a four-cycle demotion quartet, 2026-05). The referent wall (**C171**) is permanent: token/atom referents are not recoverable from the text.

3. **Framework-as-null (the maturity prior).** With ~2050 constraints and a mature operational vocabulary, *the vocabulary IS the hypothesis*. A new finding that slots neatly into existing glosses/taxonomy **without introducing new mechanism** is framework-echo, not discovery — it gets MORE scrutiny, not less. A clean framework-fit is a prior **toward null**.

4. **The null is the claim's load-bearing control — and it must match the claim class** (§III). Most demotions in this project were not "the effect was small" but "the null was wrong."

---

## II. The failure taxonomy

Each pattern: what it is · diagnostic · precedent · remedy. These are the priors to apply when auditing or registering.

| # | Pattern | What it is / Diagnostic | Precedent | Remedy |
|---|---------|--------------------------|-----------|--------|
| 1 | **Invented-threshold** | A threshold set *post-hoc in source* to make a result pass (look for a literal `# adjusted threshold` line). Check the headline value reproduces. | **C131** (source literally set >80% DSL→0.5; 23.8%→12.2% on re-run) | Calibrate thresholds against *control distributions* before locking, never from theoretical priors. |
| 2 | **Sparsity-denominator** | "X% of *possible* pairs forbidden/incompatible" on a combinatorial denominator measures *sparsity*, not prohibition. **Diagnostic: max EXPECTED count among the forbidden subset — if <5, sparsity-dominated.** | **C475** (95.7%→max-exp<5; 0 robustly illegal), C642, C1118, C973 | Use the *attested* denominator (**C729**: 0 violations / 19,576 attested pairs). |
| 3 | **Wrong-null: chi² vs permutation** | When both factors correlate with frequency, chi² rejects independence trivially (p≈1e-290) while a marginal-preserving permutation gives the honest (often null) p. | **C1068** (chi² p=3.4e-292, perm_p=0.13) | Marginal-preserving permutation null, not chi². |
| 4 | **Wrong-null: affiliation-network** | Clustering/spectral metrics on a *co-occurrence* graph (a union of record-cliques) compared to a configuration model — which *destroys* the cliques — produce spurious huge z. | **C981/C983** (λ₁ 79, n_eig 13, clustering 0.89 ALL reproduced by the clique-preserving bipartite null; config-model gives 15/1.6/0.25) | Clique-preserving **bipartite** null (preserve record sizes + node degrees, reshuffle, reproject). |
| 5 | **Frequency-confound** | A frequency-driven property presented as structural/causal transfer. **Diagnostic: does it survive a partial correlation controlling for log-frequency?** | **C470** (restriction-inheritance: B-spread 0.996≡frequency; partial ρ 0.062), **C989** (37× over a sparsity baseline) | Frequency- / composition-matched null; partial correlation on log-frequency. |
| 6 | **Broken-baseline** | A baseline that doesn't instantiate the alternative hypothesis (greedy with alphabetical fallback; sampling-with-replacement; frequency-blind generative models). **Requires reading the baseline source — regex can't catch it.** | **C476** (greedy spams alphabetically-early hubs post-saturation), C973 (frequency-blind latent models, dense by construction) | A baseline that actually represents the alternative; read the algorithm. |
| 7 | **Post-hoc claim-substitution** | A follow-up writeup says "VALIDATED" while the script JSON says `verified:False`; a weaker claim swapped under the original number. **Read the JSON verification fields before the prose.** | **C481** (`c481_verified:False` in JSON; "VALIDATED" in FINDINGS.md) | The registered claim must match the actual test output. |
| 8 | **Floor-vs-discriminator** | A metric *any* structured-symbolic system passes (a floor) mistaken for a natural-language discriminator. **Run a non-NL structured benchmark (mensural notation); if it passes, it's a floor.** | **C2052** (8D matcher generic — Theophilus *metalwork* hit the distillation folios); burstiness/DFA-Hurst (mensural passes the NL threshold) | Gate on *discriminators*, not floors; require a non-NL negative control. |
| 9 | **Label-fit-to-signal** | A latent categorical assignment chosen to *maximize* the statistic, reported as pre-registered. **Tell: the row names two candidate values and reports the better one.** | **C1684** (chose goat=Aries because perm_p 0.033<0.220; honest full-enum = null 0.112) | Freedom-free external label definition; report the un-fitted full-enumeration estimate. |
| 10 | **Window-blindness (wrong instrument)** | A low-order char-Markov null is blind to a long source token's prefix at a boundary; "transition survival" is a source-ungeneratability artifact. | **C2066** (daiin/qo→CHSH; 28% long-token fidelity vs 99.6% short) | Within-line *token*-shuffle null for token-adjacency / prefix-routing claims. |
| 11 | **Bootstrap-ratio at noise floor** | A ratio metric (e.g. lag2/lag1) explodes when the denominator ≈ 0; fragile under N-imbalance. | within-Scribe autocorrelation (z −2.05 → median +1.73 under N-matching) | N-matched downsample (≥20 iters) before locking. |
| 12 | **Phantom-clustering (imposed taxonomy)** | A partition *imposed* by keyword-matching, not discovered; the validation silhouette is circular (features = the defining atoms). **Was k ever tested? Are the validation features the defining features?** | **C2060** (C109 5-class hazard taxonomy keyword-imposed), **C2069** (8-category dict hardcoded; real silhouette −0.070) | Data-driven k-sweep; validate on axes *independent* of the defining features. |
| 13 | **Transcription-serialization-artifact** | Order/transition/rigidity stats on transcriber-imposed row order measure the *serialization*, not the manuscript. **Tell: the convention flips between units (a grammar can't).** | **C434/C435/C436** (R-series "forward ordering" = depth-sorted blocks; edge-rate ≡ 1/locus-length) | Order-*independent* stats (set overlap); the artifact is upstream of the test. |
| 14 | **Stale-retraction-row** | A retraction in a prose note but *not struck* in the machine-readable row leaks into the generated table as live; prose and table silently disagree. | **C1959/C1960/C1970** (retracted in notice, stale-live in table) | Strike the number field (`~~N~~`) + a parseable STATUS token; **generate the table from source**, never hand-list retraction status. |
| 15 | **Asymmetric-update** | Removing artifact evidence treated as *supplying* inclusion evidence; snapping to a prior in one direction. | the "is AZC a calendar" overreach (removing the seasonal artifact ≠ evidence FOR a calendar) | Symmetric update: surviving a refutation moves UP, a failed framework-fit moves DOWN, neither snaps. |

---

## III. The null discipline — which null for which claim class

The single highest-leverage rule in the project. **The correct null is determined by the claim class, not by convenience.**

| Claim class | CORRECT null | WRONG null (and why) | Precedent |
|---|---|---|---|
| Token adjacency / prefix-routing | within-line **token-shuffle** | char-5-gram (window-blind to long sources) | C2066 |
| Composition / folio-aggregate | **within-folio shuffle** | permutation-anything (folio-composition shadow) | within_folio_null_first |
| Co-occurrence graph spectral/clustering | clique-preserving **bipartite** | configuration-model (destroys record-cliques) | C981/C983 |
| "% forbidden / incompatible" | **max-expected-among-forbidden ≥5** | N_possible combinatorial denominator (sparsity) | C475 |
| Enrichment / cross-system coupling | **frequency- / composition-matched** | random or sparsity baseline (frequency-confound) | C470/C989/C1133 |
| Cross-layer association | **marginal-preserving permutation** | chi² (rejects trivially under shared frequency) | C1068 |
| Subset comparison w/ N imbalance | **N-matched downsample** | raw comparison (imbalance drives it) | n_matching |
| NL-vs-non-NL discrimination | **non-NL structured benchmark gate** (mensural) | any NL-range threshold alone (it's a floor) | C2052 |
| Latent-label categorical | **un-fitted full enumeration** | the maximizing assignment (label-fit) | C1684 |

**The diagnostic question for any claim:** *what is the cheapest null that preserves everything except the thing I'm claiming?* If the observed effect doesn't beat THAT, it's the structure-you-didn't-control-for, not your claim.

---

## IV. The verdict gate (echo-class clearance)

Before any verdict on an EXISTING finding (promote / demote / "confirms" / "X means Y"):

1. **CITE** the governing constraint(s) + tier + exactly what you'd contradict/extend.
2. **SOURCE:** new evidence, or in-context reconstruction? A fresh computation does NOT supersede a documented finding unless it tests the *same claim, same layer, valid null*.
3. **LAYER + NULL:** name the layer (atom/PREFIX/MIDDLE/paragraph/folio) and the null, justified for the claim class (§III).

**Echo-class verdicts cannot be self-cleared.** Any structural-feature↔external-referent claim (regardless of verb — "encodes / tracks / consistent-with / signature-of" all count), a Tier-3→2 promotion, or a new-mechanism-token claim requires an **adversarial external test** (a corpus/null *outside* the prior, kill-condition pre-registered) **OR explicit human sign-off**. Null-driven demotions and retractions are **exempt** (self-correcting).

**Same-model review is NOT an echo defense.** Routing a clean-fit to `expert-advisor` or `crazy-expert` clears ONLY rigor / null / tier / bookkeeping — never clean-fit (both share the embedded-constraint prior + the framework-echo magnet). The real catches in this project came from **external corpora + the human**, never a second constraint-carrying agent.

**The differential check** (where interpretation is load-bearing): run the verdict past BOTH `expert-advisor` (full interpretive context) and `lean-expert` (constraints + statistics + discipline priors only, NO interpretive layer). **Where they diverge, interpretation — not the statistics — is carrying the verdict.** Agreement means it rests on the numbers. (This still doesn't *clear* clean-fit — both are same-model — but it localizes the risk to the human.) This worked predictively: in PHASE_749 the advisor *predicted* lean would flag a "partition vs gradient" tension, it did, and that confirmed the "unified index" framing was interpretation-carried.

**Anti-dismissal (symmetric).** Contradicting a Tier-2 claim *also* requires new evidence OR a named methodological flaw — bare disagreement is not a verdict.

---

## V. The ceilings (what the analysis cannot do, from inside the corpus)

- **Referent wall (C171):** token/atom referents are unrecoverable from the text. "What does it mean" has no internal answer.
- **Text-statistical exhaustion:** these methods discriminate Voynich-vs-Latin but NOT among Latin subdomains (PHASE_718/720). Cross-corpus matching is generic at the domain-within-Latin resolution.
- **Image decoupling:** illustrations are epiphenomenal — they don't predict the grammar (C138/C140/C1824); the one tested image attribute (clothed/naked) is decoupled from the text. The image is a *domain* channel (plants, apparatus are real referents) but not a text-decoding channel.
- **The mechanism-cycle procedural ceiling:** the surface→candidate→discriminating-test→sharpen cycle promotes *structural measurements* to Tier 2 but CANNOT promote *operational interpretations* to mechanism-tier facts from inside the procedure.
- **The ONLY documented path past Tier 3** is external grounding: physical reconstruction, external-corpus alignment with a *discriminating* signature, or a fundamentally different evidence class. All obvious such routes are currently foreclosed (image decoupled, corpus-matching generic, apparatus-grounding foreordained-or-echo).

**Implication:** at maturity, the highest-EV work is **integrity (audit) + integration (consolidation)**, not discovery. Manufacturing new constraints to feel productive is the trap; the next 20 "discoveries" are likelier echo than the next 20 audit retractions are wrong.

---

## VI. The audit method (finding & fixing inflated families)

The project's audit found that **constraints registered in batches share a batch null** — so a single pre-discipline null error inflates a whole *family* that looks like independent findings. PHASE_748 found one such family: 12 A-side compatibility/discrimination-space constraints, all the same co-occurrence-graph wrong-null, reducing to ~28 above-noise modes + C729.

**To audit:**
1. **Grep the signature, not a guessed candidate list.** (The memory's guessed sparsity list was largely wrong; the real hits came from grepping "% forbidden / incompatible," chi², "enrichment Nx," etc.)
2. **Match the failure pattern to the right diagnostic** (§II/§III): max-expected-among-forbidden, bipartite null, frequency-partial, read the baseline source, read the JSON before the prose.
3. **Use the constraint's OWN evidence table** — inflated constraints frequently self-document (C973's NULL-G p=0.093, C982's 9× estimate spread, C1118's "by construction" note were all on the face of the evidence).
4. **Cascade both ways.** Demoting a parent obligates checking its *dependents* (the C981 cascade initially stopped one ring short of the inheritance layer → C470).
5. **Verdicts are self-clearing** (null-driven demotions are exempt from the echo gate) — audit is the rare direction where the rigor bar is automatically met.

**Kill-condition (when to STOP auditing):** stop when two consecutive family sweeps return <~15% correction AND zero load-bearing (cited-downstream) constraints move. **Anti-dismissal caveat:** the "batch → shared-null" prior is inductive; if the *first* sweep of a new family returns low correction, the inflation was *localized* (not base-wide) → stop and consolidate. (This is exactly how PHASE_748 ended: the inheritance check returned one leaf, C470 — localized → audits done.)

---

## VII. Provenance

The patterns above were extracted from ~40 `feedback_*` methodology memories (`~/.claude/projects/C--git-voynich/memory/`) and the PHASE_731–748 audit changelog. The canonical short list lives in `CLAUDE.md` (the always-loaded negative-knowledge priors). This doc is the expanded reference; the memories are the primary record of each pattern's discovery.

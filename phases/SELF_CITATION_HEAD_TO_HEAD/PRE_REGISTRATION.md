# Self-Citation Head-to-Head (PRE-REGISTRATION)

**Status:** LOCKED 2026-06-08, before any generator code is written.
**Class:** adversarial EXTERNAL test — rival hypothesis from outside the prior, kill conditions
pre-registered. This is the verdict-gate-clearing class (same family as the Theophilus negative
control C2052 and the mensural test). Same-model review cannot clear what this test addresses.
**Expert record:** designed via three-way consultation (expert-advisor, crazy-expert steelman,
lean-expert adjudication). Divergences and their resolutions are recorded in §9 — they are part
of the lock.

---

## 1. The rival

**Timm & Schinner self-citation / copy-modify generation:** the scribe produces each new word by
copying a word already on the page (usually nearby — same line or line above) and modifying it
slightly (one-glyph change, prefix/suffix swap). Parameters (~5–10): copy-distance distribution,
mutation rate, line/paragraph reset behavior, seed vocabulary, (optionally) a per-system
copy-window length to represent the rival's own A-vs-B drift claim.

**What it attacks:** NOT the non-semantic conclusion (rival and project agree the text has no
referents). It attacks the **DESIGNED / FUNCTIONAL** half of the frozen Tier-0 conclusion: if a
fitted copy-modify process reproduces the structure we attribute to control engineering, that
structure is scribal-process residue, not design.

**Three-hypothesis space** (the test must keep all three live):
- **H-COPY:** pure copy-modify generation; all structure is process residue.
- **H-DESIGN:** designed control notation; copying played no structural role.
- **H-HYBRID:** designed content *executed* via copy-modify production (ledger-clerk model:
  legal token-slots filled by copying the row above and editing). The hybrid's signature is the
  project's own recurring two-layer pattern — structure at aggregate/class level, Markov at
  adjacent-token level (C2023, C2062, C2051). §5-K2 is the designated separator.

## 2. What the generator is EXPECTED to reproduce (implementation checks, not kills)

If the fitted generator fails these, the implementation is broken — fix it, don't celebrate:
C501 edit-distance-1 singleton cloud (80.3%); C346/C361/C424 vocabulary locality; C2055
char-5-gram saturation; rigid-morphology/loose-syntax two-axis determinism profile (~0.41
within-word vs ~0.05 token-level); C1834 paragraph reset; C963 body homogeneity; Zipf;
quasi-reduplication. **No surface statistic may be staked as a kill** (C2055 already proved the
surface is character-Markov; the generator owns the surface).

## 3. Fitting protocol (P1–P3, locked)

- **P1 — Fit/eval split.** FIT on: vocabulary growth curve, edit-distance-1 network density,
  repetition/quasi-reduplication rates, Zipf slope, token-length distribution. EVALUATE on the
  kill battery (§5) — none of which appears in the fit set.
  **Mutation kernel locked to UNIFORM-over-glyphs as primary.** An empirically-fitted
  glyph-confusion kernel bakes morphological structure into the null (leakage). An
  empirical-kernel run may be reported as a documented secondary, whose passes are interpreted
  as "morphological structure required" — i.e., evidence FOR designed structure, not against.
  Noted leakage caveat: §5-K2 and §5-K4 are partially downstream of fit quantities
  (edit-density, reduplication); they carry reduced — not zero — independent weight.
- **P2 — Single-fit rule (the spine).** ONE parameter set must address all evaluation statistics
  jointly. Per-statistic tuning = disqualified. **Concession clause:** if passing any kill
  requires injecting a directional / conditional / alternating production rule beyond the
  copy-mutate primitive set, the rival has conceded the designed-grammar point *by becoming it*.
- **P3 — Ensemble criterion.** N ≥ 200 runs per fitted parameter set (≥ 500 for ratio
  statistics). B counts as "reproduced" on a statistic iff it falls inside the ensemble's
  two-sided central 95% (2.5/97.5 percentiles) **on the pre-registered side for signed kills**.
  Report B's percentile rank in every case, not just in/out.

## 4. Pre-flight audits (P4 — run FIRST; results lock which kills are live)

- **P4a — C783 denominator audit.** For each of the 17 forbidden class transitions: max expected
  adjacent count (over both directions) under a frequency-preserving within-line class-shuffle
  null (NOT a char-5-gram — C2066). Pair is live iff max-exp ≥ 5 (the C475/C1118 robustness
  floor). **N_live ≤ 4 ⇒ K1 is DEAD as a standalone kill.** Lean's read of C2023 (16/17
  zero-observed in BOTH directions; the one attested pair `he→t` suppressed symmetrically)
  predicts it dies. Salvage form if any pairs are live: attested-subset aggregate O/E,
  forbidden-direction vs reciprocal-direction; stakeable only if the subset is non-trivial.
- **P4b — C458 frequency-matched CV audit.** Frequency-match the hazard-token and recovery-token
  sets (match on token-frequency distribution), recompute folio-level CVs.
  **Live iff |CV_haz − CV_rec| ≥ 0.40 after matching** (raw gap ≈ 0.71, C1747). Result in
  [0.25, 0.40) ⇒ INCONCLUSIVE (not live, not dead). < 0.25 ⇒ K5 dead (Zipf/frequency shadow);
  crazy-expert predicts this outcome at 60/40.

## 5. The staked kill battery (post-adjudication)

| # | Kill | Statistic & null | Status |
|---|------|------------------|--------|
| **K1** | C783 directional forbidden transitions | attested-subset aggregate O/E forbidden-vs-reciprocal; freq-preserving within-line class-shuffle | **GATED by P4a; provisionally DEAD pending audit** |
| **K2** | Production-process test (the H-HYBRID separator) | mean token-string Levenshtein, adjacent vs non-adjacent body lines within folio (cross-voice, primary); null = within-folio line-label shuffle. Copy-execution predicts adjacent ≪ non-adjacent; B per C670/C1429 predicts ≈ 0 | **TIER-A — cleanest pure-process discriminator** |
| **K3** | C2045/C2046 post-hazard single-step CHSH recovery | lag+1 CHSH rate after hazard tokens vs after frequency-matched non-hazard tokens; generator ensemble as null | **TIER-B, expected FLOOR** — generator-pass carries near-zero weight; generator-fail is informative |
| **K4** | C2032/C2031 period-2 e-depth | **signed lag1 AND signed lag2 separately** (bootstrap-ratio guard: never the bare ratio at lag1≈0); generator ensemble under the single fit. Copy-nearby generically produces lag1 > 0 (positive local autocorrelation) — the WRONG SIGN vs B's negative period-2. Flipping the sign requires an alternation rule → P2 concession clause | **TIER-A, conditional on P2 + lag-magnitude guard** |
| **K5** | C458 clamp/free CV asymmetry | folio-level CV of frequency-matched hazard vs recovery sets vs generator ensemble | **GATED by P4b** |
| (battery) | C2061 λ2 above-Markov eigenstructure; A-at-null (C2025) vs B-above-Markov contrast | fair head-to-head statistics, no pre-judged direction (the char-5-gram null does not transfer to a word-copy generator) | evaluated, subject to P6 floor-classification |

## 6. Controls and floor-classification (P6 — mandatory)

Run the full battery on: (a) true-random scramble, (b) an NL Latin sample, (c) the **M2 49-class
Markov baseline** (C1025). Any statistic that M2 also passes is a **FLOOR** and cannot be staked
as a kill — corroboration only. Pre-register the resulting floor/discriminator classification
table before scoring the generator. BH correction applies to this exploratory classification
scan; **no correction on the pre-registered staked kills** (pre-registration is the correction).

## 7. Verdict map (P7, locked)

Let **N_live** = kills surviving P4 gating + P6 floor-classification (lean's structural
estimate: N_live ≈ 2, namely K2 and K4).

- **Generator FAILS ≥ 2 live kills** (or ALL live kills if N_live ≤ 2): register Tier-2 negative
  knowledge — *"Self-citation/copy-modify generation (Timm–Schinner class) is EXCLUDED as a
  complete account of Currier B structure: a generator fitted to reproduce [the §2 set] fails
  [named kills]."* Exact wording requires human sign-off ("complete account" vs broader).
- **Generator PASSES all live kills under a single uniform-kernel fit:** **pre-committed
  consequence** — the teleological half of the frozen Tier-0 conclusion ("designed... control
  programs") must be rewritten to its structural skeleton (the grammar, the transitions, the
  kernel asymmetries survive as measurements; the "designed/control" attribution does not).
  This is an echo-class verdict of maximum magnitude: **mandatory human sign-off before any
  rewrite.** Pre-committing to this downside is what makes the test honest.
- **Mixed outcome:** INCONCLUSIVE, with the surviving/failed kills named individually. No spin:
  a partial pass is reported as the H-HYBRID-shaped outcome it is.

## 8. Evidence held OUTSIDE the staked battery

- **f75r ×4∧×9 external count anchor (C2034, joint p ≈ 0.011 — the JOINT conjunction, not
  ×4-alone):** an already-observed singular event cannot serve as a pre-registered kill
  (post-hoc staking is invalid by construction). CITED as a scope limitation of the generator
  class — the copy-mutate primitive has no mechanism for language-invariant external count
  correspondence — but carries **no verdict weight** in §7. A *blind prospective* count-match
  protocol (pre-register predicted repetition signatures for the strong-cardinality recipes
  before examining their folios; crazy-expert's G-WIN-1, concession bar ≥ 3 blind hits) is a
  separate future test.
- **C2076 prohibition-layer craft fingerprint:** Tier 3, coder-non-independent — NOT stakeable.
  Noted as the external-ontology argument; its blinded-coder promotion path (G-WIN-2) is a
  separate future test.
- **Pro-rival diagnostic (honesty clause):** **f57v** (exact 12-char period × 4 cycles, C921) is
  EQUIVOCAL — readable as a generation/substitution table. If the fitted generator's
  reverse-engineered seed/kernel structure *predicts* f57v's ring, that is positive evidence FOR
  the rival and will be reported as such. f49v is likewise not staked (a 1:1 label/example
  alternation is also readable as a seed table with worked examples).
- **Conceded to the rival up front:** the cross-system vocabulary-composition gradients
  (C2074, C1559) are drift-friendly; the A/B *vocabulary* axis is not contested. The contested
  axis is grammatical (sequential structure), evaluated in the battery.

## 9. Expert differential record (part of the lock)

- **C783 (K1):** advisor ranked it the strongest kill; crazy and lean ruled it likely dead at
  the layer the generator operates on (C2023: 16/17 zero-observed both directions — the
  C1118/C475 sparsity signature). **Resolution: lean's statistics-only adjudication wins; P4a
  gates it.** The divergence localized to constraint-tier reading vs operating-layer statistics.
- **C2045 (K3):** advisor weighted its null-rigor; crazy called it edit-adjacency-native; lean
  ruled real-in-B but **non-discriminating (floor trap)** — within-folio-shuffle rigor proves
  the effect exists, not that it separates B from a copy process. Tier-B.
- **C2032 (K4):** advisor called it cleanest; crazy called it wrong-target (tunable). **Both
  right at different scopes** — unstakeable as a free claim, stakeable under the single-fit
  rule, which is exactly what P2 exists for.
- **Convergent across all three:** K2/P5 as the cleanest pure-process discriminator; the
  single-fit rule as the spine; f75r held outside; the M2 floor-classification as mandatory;
  the all-pass outcome requiring human sign-off.

## 10. Honest prior

The generator will very likely reproduce the §2 set plus several Tier-B statistics — the
surface and the locality are its home field, and more than half the structural corpus is
Markov-class-reproducible (C2055, C1025). The test's real evidential content concentrates in
**K2 (production process) and K4 (period-2 sign)**. Modal outcome per lean: generator passes
floors, fails K2 and K4 → registrable Tier-2 exclusion of the rival as a complete account,
with the H-HYBRID question (designed content, copy-influenced production) explicitly left open
unless K2 separates it. The all-pass outcome is judged unlikely but is pre-committed above —
that pre-commitment is the point.

## 11. PHASE 0 RESULTS (2026-06-08) — pre-flight audits run; kills re-locked BEFORE generator construction

**P4b — K5 (C458 clamp/free CV): DEAD, frequency shadow.** Raw density-CV gap reproduces the
published value (0.720 ≈ C1747's 0.71). But each set sits AT its own frequency-matched null
(hazard 82nd pctile, recovery 36th — neither anomalous), and the frequency-corrected gap is
**0.089 — far below the 0.25 floor.** "Hazard clamped / recovery free" is "common words are
folio-uniform, rare words are folio-variable" — Zipf, not design. (Bonus symptom: C458's
clamped dimensions were densities while its free dimensions were raw counts — a
measurement-type confound stacked on the frequency confound.) **C458 flagged for audit
disposition** (frequency-confound class, C475 family; null-driven → self-clearing per gate,
human bookkeeping pending). Scripts: `scripts/p0_preflight_audits.py`.

**P4a — K1 (C783 class-level directionality): DEAD — but NOT by sparsity. MISSPECIFIED.**
N_live = 9/17 (gate not triggered), but the salvage statistic shows the class-level
prohibition **does not exist**: aggregate forbidden-direction O/E = **1.045** (chain) /
**1.126** (strict word-adjacency — verified, not a construction artifact), reciprocal ≈ 1.0.
One "forbidden" pair (23→9) is ~2× ENRICHED (28 obs vs 11.8 exp). The class-level rows of
C783/C109 are a **registry-compression artifact**: token-level facts projected onto class
pairs where no suppression exists. (This also explains C789's "65% compliance" — at class
level there was never a prohibition to comply with.) **C783/C109 class-level framing flagged
for audit disposition.** Scripts: `scripts/p0b_strict_adjacency_verification.py`.

**K1′ (REPLACEMENT, locked now, pre-generator) — token-level directional forbidden bigrams
(C957 layer).** Independently re-verified strict-adjacent: the 9 forbidden token bigrams
(chedy→aiin, shedy→aiin, qokeedy→ol, chedy→ar, ol→qokain, ol→qokedy, qokeedy→aiin,
chey→chedy, chey→shedy) are **0 observed / ~37.5 jointly expected** under within-line shuffle
(P(0|37.5) ≈ 5e-17), while **all reverse directions are at-or-above expectation** (31 obs vs
~35.5 exp; qokain→ol enriched 12 vs 7.4). This is real, directional, token-level prohibition
among the HIGHEST-frequency words in the corpus.
**Why K1′ is a stronger kill than K1 ever was:** chey→chedy is an edit-distance-1 pair —
writing a word then its 1-edit variant is the copy-modify mechanism's *signature move*. The
corpus abounds in adjacent similar words (quasi-reduplication — the generator's home turf),
yet these specific ordered pairs are at absolute zero in one direction only. A copy-modify
generator must reproduce **selective directional zeroes embedded in abundant adjacent-
similarity** — suppressing exactly its own most natural outputs, in one direction, for
specific high-frequency pairs. Kill condition: the fitted generator's ensemble must reproduce
joint forward obs ≤ 2 (vs its own expectation ≥ 20) on these 9 ordered pairs while reverse
directions remain at-null AND quasi-reduplication stays at B's rate. Legitimacy note: staking
a known B-side distributional statistic is valid (all battery statistics are known); the P8
bar excluded only the singular already-observed external EVENT (f75r).

**Re-locked battery after Phase 0:** Tier-A live kills = **K1′ (token-level directional
zeroes), K2 (production process), K4 (period-2 sign)**. K3 = Tier-B floor. K5 = dead.
Verdict map (§7) applies with N_live = 3: generator fails ≥ 2 ⇒ rival excluded as complete
account; generator passes all 3 under single uniform-kernel fit ⇒ Tier-0-rewrite branch
(human sign-off).

**Constraint-base side effects for disposition (human):** (1) C783/C109 class-level rows fail
their own audit — the surviving hazard-topology object is the token-bigram layer (C957's 9 +
C2023's per-pair facts); (2) C458 headline asymmetry is frequency-shadow; (3) C789's "65%
compliance" re-read as symptom of (1). Expert differential prediction record: lean predicted
K1 dead by sparsity (right verdict, wrong mechanism — it died by at-null, not sparsity);
crazy predicted K5 dead 60/40 (right) and that C783 had "the C1118 signature" (vindicated in
the stronger form); advisor ranked K1 strongest (wrong at the class layer, but the
directionality instinct survives at the token layer as K1′).

## 12. PHASE 1 RESULTS (2026-06-08) — generator built, fitted, scored. VERDICT PER LOCKED MAP: RIVAL EXCLUDED.

**Implementation:** 8-parameter uniform-glyph-kernel copy-modify generator (copy-distance
geometric q, line-above weight, exact-copy rate, sub/ins/del mix, second-edit rate, edge-
position bias [T&S prefix/suffix ops], long-range Yule–Simon copy mode p_far). Seeds = real
first lines; real line layout. Fitted on the locked §3 surface set: 420+ random-search draws +
targeted probes + coordinate hill-climb (loss 10.8 → 2.62; fitted p_far=0.7 — the Yule–Simon
mechanism was required to approach B's Zipf, as theory predicts). Scripts:
`scripts/p1_generator_fit.py`, `p1b_refine.py`, `p2_battery.py`; ensemble N=200; M2 49-class
Markov + within-folio scramble controls N=60 each.

**FIT-STAGE FINDING (pre-registered P1 prediction confirmed):** even at its optimum, the
uniform-kernel generator CANNOT fully reproduce B's surface — type inventory 8,777 vs B's
4,889 (1.8×) and Zipf −0.56 vs −1.05, stable across ~500 evaluations and two model
extensions, while ed1-density (15.99 vs 15.31), token length, adjacency rates, and early
vocabulary growth fit well. **B's novelty production is morphology-channeled** (new words land
in the existing lattice); uniform mutation is not. Per P1's locked interpretation, this is
evidence that morphological structure is required upstream of any kill.

**KILL RESULTS (B vs generator ensemble central 95%, P3):**

| stat | B | gen mean [2.5%, 97.5%] | M2 | scramble | verdict |
|---|---|---|---|---|---|
| K1′ fwd O/E | **0.000** | 0.51 [0.00, 2.40] | 0.46 | 0.96 | primary INEXPRESSIBLE (see below) |
| K1′ fwd E (expressibility) | 35.5 | **0.90** [0.34, 1.93] | 51.6 | 42.7 | generator fails ≥20 precondition |
| K1′ census (secondary) | 1 | **0.00** [0, 0] | 1.75 | 0.02 | **FAIL** (thin: B census=1) |
| K2 copy-explainability gap | **−0.019** | −0.108 [−0.115, −0.102] | −0.001 | −0.000 | **FAIL — decisive** |
| K4 e-depth lag1 | **+0.035** | 0.202 [0.117, 0.292] | 0.032 | 0.030 | **FAIL — decisive** |
| K4 e-depth lag2 | **+0.056** | 0.193 [0.104, 0.283] | 0.009 | 0.028 | **FAIL — decisive** |
| K3 post-trigger CHSH (floor) | **−0.200** | 0.001 [−0.080, 0.074] | −0.080 | 0.011 | FAIL (supportive; correlated w/ K1′) |

- **K1′:** the generator never expresses the statistic — its joint expectation on the 9 pairs is
  0.9 vs the required ≥20 (its lexicon drifts off B's high-frequency core; same root cause as the
  type over-generation). Identity-free census: the generator produces ZERO directional-zero pairs
  in 200/200 runs vs B's 1 — a fail, honestly flagged thin (census definition here: within-line
  analytic E ≥ 5, stricter than C957's corpus-wide E; B's 9 pairs mostly fall at E 2–5 under it).
- **K2 (cleanest):** the generator cannot avoid its production signature — its adjacent lines are
  5.6× more copy-explainable than B's (−0.108 vs −0.019), with zero overlap. B sits near the
  no-copy controls (M2/scramble ≈ 0.00). **Honest H-HYBRID note:** B's −0.019 is small but
  nonzero vs controls — a faint adjacent-line similarity trace, consistent with paragraph-level
  thermal homogeneity (C1967/C1834, established this season) rather than copy-execution; the
  pure-copy hypothesis is excluded, the faint trace is NOT evidence for it.
- **K4:** locked sign-prediction was mis-calibrated (B's lag1 on THIS operationalization is
  +0.035, not negative — C2032's −0.66 was a different instrument; registration-calibration
  noted per discipline). The discriminating logic held exactly as designed: copying forces
  strong positive local e-depth autocorrelation (0.12–0.29); B has almost none. M2 reproduces
  B's value almost exactly (0.032 vs 0.035) → K4 separates copy-process from B *and* from
  Markov: the failure is specific to the copy mechanism, not to "any generative model."
- **K3:** not a floor on this operationalization — B's post-trigger CHSH depression (−0.20) is
  partially a re-expression of the K1′ zeros (trigger set overlaps the forbidden-bigram
  sources); counted as supportive, NOT as an independent kill.

**VERDICT (locked map, §7, N_live=3):** generator fails K2 and K4 decisively, K1′ by
expressibility+census (thin). **≥2 live kills failed ⇒ "self-citation/copy-modify generation
(Timm–Schinner class) is EXCLUDED as a complete account of Currier B structure."** The
all-pass/Tier-0-rewrite branch is moot. Registrable Tier-2 negative knowledge; exact wording
requires human sign-off (§13). Draft wording:

> *Self-citation/copy-modify generation (uniform glyph kernel, 8 parameters incl. Yule–Simon
> long-range copying), fitted to Currier B's surface statistics (vocabulary growth,
> edit-distance-1 network, adjacency rates, Zipf, token length), is excluded as a complete
> account of Currier B: (i) at fit stage it over-generates the type inventory 1.8× with
> under-steep Zipf — B's novelty is morphology-channeled; (ii) its production signature
> (adjacent-line copy-explainability −0.108 [−0.115,−0.102]) is absent from B (−0.019 ≈
> no-copy controls); (iii) it forces local e-depth autocorrelation (lag1 0.12–0.29) that B
> lacks (+0.035) and that the M2 Markov baseline reproduces exactly — the failure is specific
> to the copying mechanism. The faint adjacent-line trace in B is attributable to
> paragraph-level state homogeneity (C1967/C1834), not copy-execution.*

**Not run (documented):** the empirical-kernel secondary (P1) — its passes would mean
"morphological structure required," already demonstrated at fit stage; NL Latin control
(would sharpen floor classification but no kill depended on it).

## 13. Human sign-off points

1. **This lock** (kill conditions, thresholds, verdict map) — sign-off = authorization to run
   Phase 0 (P4 pre-flight audits).
2. **The Tier-0-rewrite pre-commitment** (§7, all-pass branch) — must be explicitly
   acknowledged by the human before the generator is scored against the battery.
3. **Wording of any registered negative-knowledge constraint** (§7, fail branch).

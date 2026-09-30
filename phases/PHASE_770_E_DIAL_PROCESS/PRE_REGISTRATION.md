# PHASE_770 — What kind of process sets the e-dial? (pre-registration)

**Status: LOCKED** (git tag `phase770-lock`). Final after the lean-expert's lock audit (E1–E6 required, R1–R9 recommended; all applied).
- Merges the expert-advisor and lean-expert checks of v2 (2026-09-29) and the full calibration on controls.
- Nothing under this design has been computed on B. §2 lists what is known and what the design stage computed.

**History:**
- **v1** was reviewed by three experts.
- **v2** merged those reviews. Its checks found:
  - the class-label classifier's gate fails (v2 bank: `results/calib/bank/gate_H81_0.323_0.095_770_v2double.json`);
  - two conditioning variables leak outcomes;
  - k/t is not a clean lexical control.
- **v3** fixes all three (§4, §6, §7).

## 1. Origin and question
C2086 (PHASE_769): with the word frame and position fixed, the choice of one e versus 2+ carries a folio-level component
shared across different words (S3c +0.323, z 4.3, confirmed on ZL). Whether it drifts within the page is unresolved,
and its source is open.

PHASE_770 asks:
- **Arm 0:** is the component produced by neighbour context combined with folio vocabulary?
- **Arm A:** is it static on the page or position-dependent?
- **Arm B:** is it shared with other spelling choices?
- **Arm C:** is it continuous across page turns in writing order?

It can favour or disfavour classes of source; it identifies none. Every source reading is echo-class (§11).

## 2. What is already known about B (disclosure)
### Known from PHASE_769
- S3c +0.323, S3 +0.315 and S3far +0.095;
- S3P, and S3P-within p 0.58 (overlaps A3);
- per-stratum S3c;
- frame-controlled folio propensities, and their recto/verso leaf-pair correlation r 0.26 (27 pairs; C1977's frame-controlled value, and C2's leaf-pair cell).

### Prior evidence on the other dials (not frame-controlled)
**CS:**
- depends on section (C409, C410);
- sister choice is 32% folio- or paragraph-determined (C1182); C1180 is positional mediation;
- line-start clustering on a fixed frame (C1983); sh before ch in paragraphs (C1963);
- boundary coupling (C1186, C1212, C1563, C2082);
- independent of ok/ot (C1184);
- priors linking sh and e: C1203, C1967.

**KT:**
- k and t head different MIDDLEs (C1478, C1538);
- the k share is a REGIME-defining axis (C1715, C1871, C1920, C2070; ot: C1890);
- the plain k/t unit also carries the ok/ot sister-prefix choice (C408, C1184, C1539) and the paragraph-initial gallows, which has its own order grammar (C864, C1780, C1784). C865 is paragraph-gallows position.
- Hence KTH (§7).

**MIN:**
- only e and i extend (C1197);
- the ii/ee choice splits by HEAD atom (C1912);
- folio i-rate against e-rate r −0.41 (C1205);
- C1732 and C1740;
- graded by section and REGIME (C1204, C1730);
- within-line position: aiin before ain (C1244, C1909); C1234 is line position.

**Line and page position:**
- C1566, C1672, C1235 and C1460 describe composition, which the frame holds. No within-frame position effect is registered for E. C1855 tests h, not e.
- Lines shorten with paragraph order (C1782, C1783).
- The e-depth arc was a paragraph-1 artifact (C1986, Tier 1; C1287). This is relevant to A4.

**Pair structure of composition:** leaf pairs (C1978); bifolia (PHASE_759, unregistered); page adjacency (C361, C1839).

### Computed in the design stage (`scripts/design_checks770.py`, `results/design_checks.json`)
Transcription agreement, counts and codicology.

### Computed before lock on B's outcomes, pooled with folio fixed effects
These carry no folio, position or page-turn information:
- the within-folio additive effects of the preceding token's last two collapsed units and of the line-fullness tercile (the background effects in every plant; §4);
- the pooled cell rates (plant base logits, as in PHASE_769).

### Not computed on B
Any dial statistic by folio, page position, paragraph order or page turn, including S3c and S3far on the analysis set, and anything from the published e-dial folio propensities.

## 3. Design checks (done)
### 3.1 Transcription agreement
Measured on aligned tokens whose other glyphs match.
- H–F uses the interlinear line ids.
- H–ZL matches lines by content (ZL numbers its loci in one sequence per page; 421 equal ids name different lines).

| Dial | Marked value | κ H–F | κ H–ZL | Informative (analysis set) | Marked rate |
|---|---|---|---|---|---|
| E | 2+ e | 0.984 | 0.995 | 6,229 | 0.36 |
| CS | sh | 0.992 | 0.994 | 4,812 (3,086 with the two-unit context in the cell) | 0.35 |
| KTH | t as HEAD atom | 0.985 | 0.985 | 2,958 | 0.22 |
| OKOT | ot prefix | 0.986 | 0.988 | 2,039 | 0.49 |
| MIN | 2+ minims | **0.423** | **0.971** | 3,058 | 0.60 |
| BENCH | benched | 0.999 | 1.000 | 6,541 (958 with variation) | 0.08 |

- **F differs from H and ZL on minims.** Which reading matches the scans is unsettled; H and ZL are not independent, and κ is an upper bound. MIN is "the minim count as read by H and ZL".
- **Registration of MIN claims:** none without the scan check in §14.
- **Consistent-run subsets:**
  - read alike by H, F and ZL: E 4,996, CS 3,729 and KTH 2,313 informative (marked rates unchanged);
  - MIN read alike by H and ZL: 2,535 (rate unchanged, 0.60).
  - A filter by H–F agreement on MIN selects on the outcome (rate 0.84) and is never used.

### 3.2 Analysis set
- **Folios:** 81. f76r is included (H placement R, ZL paragraph text).
  - Its lines match ZL's in order.
  - The sentinels (C762) are coded as labels in H and excluded.
  - Its paragraphs and headers come from H's paragraph-initial markers (4 paragraphs).
  - Its stratum is B/2.
- **f115r:** hand 3 (blank $H in ZL; its quire is hand 3). Sensitivity: excluded.
- **No paragraph spans a tested page turn.**

### 3.3 Codicology (ZL $Q, $B, $F, $H)
- **55 usable reading-order transitions:** 34 leaf turns and 21 openings (f40v→f41r excluded).
  - Chains are led by Q13 (20 pages, 19 transitions) and Q20 (12 and 11 pages).
- **33 sheet faces with both pages in B:** 17 outer (B-v | A-r) and 16 inner (A-v | B-r). The reading-adjacent inner face f79v | f80r is an opening and is counted in C1 only.

### 3.4 Floor corpus
Aberdeen is infeasible, so the floor is deferred (§9).

## 4. Common machinery
- **Engine.** `scripts/ed770.py` and `scripts/cal770.py`. With PHASE_769's settings, `ed770.py` reproduces PHASE_769's arrays exactly.
- **Frame and cell.**
  - The dial frame is the token with the dial's units replaced by a class symbol (e-runs collapsed), plus the slot.
  - The cell is frame × slot × line zone × header line × paragraph-length tercile × section × hand.
- **Residuals.** Residual = y − cell mean. The null is permutation within cell across folios, unless stated.
- **Collapsed context variables** (lean-expert v2 check). Every dial class is collapsed before building them, so no dial outcome is visible in them: an e-run is one e, a minim group I+final, ch/sh X, any gallows G.
  - **Context:** the preceding token's last two collapsed units (C2082 places routing there), or START / GAP. The last unit alone is a sensitivity.
  - **Line fullness:** collapsed units in the line ÷ the page median, as a tercile.
- **Within-folio nuisance effects.** Additive effects with cell means and folio fixed effects (backfitting), so no folio component leaks into them.
  - Measured: context effects up to ±0.08 on the probability scale; fullness about 0.
  - Every plant carries both as background (logit SD 0.12).
- **Cross-frame split.** Every statistic compares keys from one random half with keys from the other (50 halvings, both assignments). The key is the dial frame, or for two dials the joint frame.
- **Folio covariates** (S3c): log lines, tokens per line, paragraphs, and legibility with every dial class collapsed. PHASE_769's legibility is a sensitivity.
- **ZL rule.** Stated per arm.

## 5. Arm 0 — Is C2086 produced by neighbour context?
- **0a (B).** S3c on y_adj = y − (the within-folio additive effect of the preceding token's last two collapsed units), with standard cells. The null is permutation within cell of y_adj.
  - Also reported: S3c_adj ÷ S3c on the same occurrences, and the one-unit sensitivity.
- **Rule (fixed now).** C2086 receives the scope note *"not separated from neighbour context × folio vocabulary"* if either holds:
  - S3c_adj < 0.16 (an absolute materiality line: about 40% of the folio variance at B's reliability);
  - S3c_adj has p > 0.01 while calibrated power is ≥ 0.9 in both H and ZL.

  If power is < 0.9 in either, that leg is UNRESOLVED.
- **Applied to H** (lean-expert lock audit E4).
  - If the unadjusted S3c is < 0.16, Arm 0 is UNRESOLVED: there is no component to explain. On a control text without a component, the dry run had issued the note.
  - If C2086 stands on H but ZL fails (S3c_adj < 0.16 or p > 0.01), the result is labelled ZL-dependent.
- **Calibration** (`results/calib/cal0.json`). M1 at B's strength (the pilot s*), plants with background:

| Set | Power at α 0.01 | Ratio S3c_adj / S3c (median) | False note from S3c_adj < 0.16 |
|---|---|---|---|
| H | 0.98 | 1.00 | 2% |
| ZL | 0.96 | 1.00 | 4% |

  - At 0.75× strength, power is 0.81 (H) and 0.71 (ZL).
  - A context-only plant, at 1× or 3× the within-folio context effect, gives S3c −0.01 to +0.004 before and after adjustment. The CONTEXT mechanism alone does not produce a folio component.

## 6. Arm A — Shape of the component over the page
### A1: quarter covariance matrix (descriptor; source of the features)
- **Estimator.** C_h(q, q') = Σ_f S^A_{f,q} S^B_{f,q'} / Σ_f n^A_{f,q} n^B_{f,q'}, over 50 halvings and both assignments, symmetrised. Residuals are centred within stratum × quarter. Every folio enters every element.
- **Features:**
  - raw (7): V1–V4 and the mean off-diagonal at quarter distances 1–3;
  - scale-free (6): V1–V3 and D1–D3, each ÷ mean(V1–V4).
- **Reported:** per stratum, the effective number of folios, and a leave-one-folio-out range.

### A2: classification (primary)
**Plant bank** (`scripts/bank770.py`, `results/calib/bank/bank_v3_*`):
- Every model is planted on the analysis set's cells, with background.
- Scale is log-uniform on [0.55 s*, 1.5 s*]. Replicates with S3c in [0.25, 0.40] are kept, 10,000 per model.

**Classes by the latent position contrast D14** = E(u₁ − u₄)² / E(u₁² + u₄²):
- u_q is the mean latent over a page's informative occurrences in quarter q;
- it is computed from 200 latent draws on the skeleton, with no outcomes.

| Class | Models (D14) |
|---|---|
| **STATIC** (D14 ≤ 0.15) | M1 constant (0.000); M2a paragraph edges unexpressed (0.064); M2b page edges unexpressed, 2 / 4 / 6 lines (0.083 / 0.023 / 0.047) |
| **INTERMEDIATE** (fit check and tables only) | M2c first and last paragraph unexpressed (0.186); M7 constant plus paragraph offsets (0.383); M4-0.97 and M4-0.99 (0.454 / 0.186); M6-0.97 and M6-0.99 (0.449 / 0.199); M8-40 (0.387) |
| **POSITION-DEPENDENT** (D14 ≥ 0.5) | M3 restart walk (0.728); M4-0.95 (0.595); M5 trend (0.717); M6-0.95 (0.591); M8-20 changepoints (0.602) |
| **Mixtures** (gate by own D14) | M1 + M3 at 25 / 50 / 75% (D14 0.143 / 0.315 / 0.509); M1 + M6-0.97 at 25 / 50 / 75% (0.108 / 0.217 / 0.338) |

- **Dropped after the pilot:** M8-10 and M9 (a paragraph-restarting walk) cannot reach S3c 0.25 at any scale tried.
- **Background effects, not classes:** CONTEXT and LAYOUT.

**Classifier** (`scripts/clf770.py`):
- A joint Gaussian of (S3c, S3far, features) per model, fitted to training replicates. The replicates are split 40% training, 40% reference, 20% evaluation.
- For B's (S3c, S3far, f):
  - known part = density of S3far given S3c;
  - new part = density of f given S3c and S3far.
- **Posterior** over STATIC and POSITION-DEPENDENT models: prior (½ per class, equal per base model, equal per variant) × known × new.
- **BF_new** is the new part's class Bayes factor, with within-class prior weights.
- **Fit check:** the conditional Mahalanobis distance of f to the best-fitting model among STATIC, POSITION-DEPENDENT and INTERMEDIATE must be at or below that model's 99th reference percentile.

**Verdict** (thresholds calibrated on controls before lock, `scripts/thr770.py`; v3's first values were 0.8 and 3):

| Verdict | Condition | Bound stated with it |
|---|---|---|
| **STATIC-DOMINANT** | P(STATIC) ≥ 0.9, BF_new ≥ 10, fit check passes | "position-dependent models with D14 ≥ 0.5 disfavoured" |
| **POSITION-DEPENDENT-DOMINANT** | P(STATIC) ≤ 0.1, BF_new ≤ 1/10, fit check passes | "static models with D14 ≤ 0.15 disfavoured" |
| **UNRESOLVED** | otherwise, including "model set inadequate" when the fit check fails | — |

- A verdict carried only by the known part, with BF_new between 1/10 and 10, is UNRESOLVED.
- Verdict probabilities for INTERMEDIATE truths and mixtures are published (§13).

**Gate map.**
- **Grid:** S3c {0.28, 0.30, 0.32, 0.34, 0.36} × S3far {0.03, 0.06, 0.09, 0.12, 0.15}. At each point, evaluation replicates within ±0.03 of both are used.
- **Pure models:** each STATIC or POSITION-DEPENDENT model with n ≥ 30 must reach its own class in ≥ 70% and the wrong class in ≤ 5%.
- **Mixtures:** a mixture is gated by its own D14 class, and must reach the other class in ≤ 15%. Mixtures with intermediate D14 are not gated, like intermediate models.
  - This replaces the lean-expert's literal rule, which gated the 25% and 75% mixtures on the minority class.
  - The literal rule fails at every threshold because the 75% mixture of M1 and M6-0.97 has D14 0.34, which is intermediate by the class definition itself. It is called STATIC 20–47% of the time, as an intermediate truth may be, with the bound stated.
  - Flagged for the lock audit.
- **Feature version: raw** (fixed at lock).
  - With thresholds 0.9 and 10, the raw gate passes at 22 of 25 grid points, including all nine at S3c 0.30–0.34 × S3far 0.06–0.12.
  - It fails at (0.28, 0.12), (0.28, 0.15) and (0.30, 0.15), where the 75% M1+M3 mixture (D14 0.51) is called STATIC 17–22% of the time.
  - The scale-free version fails at most points near B and is not used.
  - The version may not be switched at run time.
- **Run time:** A2 is verdict-bearing only if both hold; otherwise Arm A is UNRESOLVED.
  - B's S3c lies inside the bank window [0.25, 0.40]. Outside it, the Gaussian conditioning extrapolates: poured
    habit3b controls at S3c about 0.04 were labelled STATIC by the bare classifier.
  - The gate passes at B's own (S3c, S3far) on **fresh replicates**: a frozen seed tag, 100 replicates per gated model within ±0.03 of B's values, up to 60,000 draws.
    - This removes the in-sample optimism: the thresholds were selected on the bank's evaluation replicates.
    - Gated models: the frozen S and P classes, and mixtures whose D14 falls in a class.
    - Same criteria as the gate map, and at least one STATIC and one POSITION-DEPENDENT pure model must be evaluated (n ≥ 30).
    - The in-sample gate at B's point is reported too. The pre-lock gate map is published (`results/calib/bank/clf_v3_H81_770.json`).

**Run-time bank rule.**
- The bank is regenerated with the frozen code and seeds.
- If fewer than 200 replicates of a model fall within ±0.03 of B's values, the same generator is extended (frozen seeds) up to 150,000 draws.
- A model is never dropped: its acceptance rate is part of its likelihood.

**Exclusion list** (descriptive; `scripts/excl770.py`). For every model, p_m is the share of its reference replicates at least as far from its mean as B, on the 8-vector (S3far, raw features), among replicates within ±0.03 of B's S3c. Models with p_m ≤ 0.01 are listed as excluded.

### A3: paragraph order (veto only)
- **Units:** paragraph means over body lines only; the first and last 2 lines of each page excluded; residuals centred within stratum × position decile.
- **Statistic:** D (adjacent minus 2+ apart), with pair weights the smaller half-count.
- **Null:** paragraph order permuted within folio (2,000).
- **Calibration** (plants with background):
  - size at α 0.01: M1 0.010, M2a 0.010, M7 0.025, **M2b-4 0.085**;
  - power: M3 0.21, M5 0.05, M6-0.97 0.15.
- **Veto:** if A3 gives p ≤ 0.01 while A2 says STATIC-DOMINANT, Arm A is UNRESOLVED.
- A3 is anti-conservative under M2b-4 in the direction that makes STATIC verdicts harder, not easier. This is stated in the result.

### A4: edge checks (descriptive)
S3c and S3far, stratum × quarter centred:
- all lines;
- without header and paragraph-final lines;
- without the first and last 2 lines of each page;
- without the first and last 4 lines of each page.

### A5: residual variogram (descriptive)
- **Measure:** cross-frame covariance of line residual sums against absolute separation (1, 2, 3–4, 5–8, 9–16, 17–32 lines), within pages. Reported by page-length stratum (< 20 and ≥ 20 lines) and for same- versus different-paragraph pairs.
- **Continued** through page turns along reading-order chains.
- **Envelopes:** M1, M2b-4, M3, M6-0.97 and M8-20.

### Arm A verdict
- **Verdict-bearing:** A2 on the H analysis set, subject to A3's veto and the ZL rule.
  - ZL is classified on its own ZL bank. Its S3c must lie in [0.25, 0.40] and it must reach posterior ≥ 0.5 for the same class; otherwise UNRESOLVED.
  - Model classes and D14 are frozen from `bank_v3_H81_770.json` for every set.
- **No-flip checks:** the 80-folio set (f76r excluded; f115r uninformative), the fullness-tercile cell, and runs read alike by H, F and ZL, each on its own bank generated at run time with frozen code and seeds.
  - If any gives the opposite class at posterior ≥ 0.8, the arm is UNRESOLVED.
  - A set whose S3c lies outside [0.25, 0.40] is reported as not evaluable and does not veto.
- **Descriptive:** A1 per stratum, A4, A5, the exclusion list.

## 7. Arm B — Do other spelling choices share the component?
**Dials:**
- **CS** (sh vs ch): the cell includes the two-unit collapsed context. It is a plume that is also grammatical, and its own component is anticipated (C1182).
- **KTH** (t vs k as the HEAD atom, e.g. qok-/qot-, chk-/cht-): the lexical control. Paragraph-initial gallows units are excluded (included as a sensitivity).
- **MIN** (2+ minims): E's extension sibling, as read by H and ZL.
- **Descriptive:** OKOT (the ok/ot sister-prefix choice) and BENCH.

### B1: own component
S3c per dial, with the within-cell null.
- A dial has its own component at p ≤ 0.01 (H) with ZL the same sign at p ≤ 0.05.
- MIN is also run on F as a sensitivity.
- **Strength.** From the dial's calibration curve (mean and SD of S3c against folio logit SD, M1 plants on the dial's own cells), the strength estimate and its lower 80% bound are read at the observed S3c.
- **MDE80** at α 0.01 (logit SD; `results/calib/calB.json`):

| Dial | MDE80 |
|---|---|
| CS (two-unit context cell) | 0.46 |
| KTH | 0.48 |
| MIN | 0.43 |
| OKOT | 0.49 |

  For comparison, E's own component is about 0.42.
- None meets 0.25, so "no own component" never counts as NOT SHARED. B2 decides every dial.

### B2: shared folio component (primary; all three dials)
- **Statistic.** For each of 50 joint-frame halvings: E's covariate-residualised folio mean vector (its key half, one region) and Y's (the other key half, the other region). X is the mean correlation over halvings, key-half swaps and region swaps.
- **Region split: block**, fixed at lock by calibrated power under drift (`results/calib/calBj_*.json`).
  - *block:* alternating 3-line blocks with a buffer line, line index mod 8 in {0–2} against {4–6}.
  - *half* (top against bottom half) is not used. Under drift at a family-adjusted threshold of about 0.003, block had power 0.66–0.75 against half's 0.34–0.45, and block also held size slightly better.
- **Null: circular shifts within stratum.** Y's folio vector is shifted along manuscript order by a random non-zero offset in each section × hand stratum. One relabelling is applied to every halving, swap and dial (joint); 2,000 relabellings at run time.
- **The z-scale threshold replaces nominal p.** The 1,000-replicate certification showed the random within-stratum relabelling anti-conservative under independent drifting components:
  - per-dial size 0.026 at α 0.01 (half split);
  - X's spread across H0 replicates 16% wider than the null's, or 10% with shifts.

  No nominal threshold held size at the attainable permutation resolution. The critical value is therefore calibrated on the z scale, z = (X − null mean) / null SD. It is the 99th percentile of max |z| over the three dials under joint H0 plants, in which one e-dial draw is shared by all pairs and each Y dial carries an independent component (1,000 replicates with drifting components, 500 with folio-level ones):
  - 99th percentile 3.10 (drift) and 3.12 (folio);
  - **critical |z| = 3.2**, which gives P(any dial ≥ 3.2) of 0.007 (drift) and 0.006 (folio).
  - The Westfall–Young p is reported, descriptive only.

**Per-dial verdicts:**

| Verdict | Condition |
|---|---|
| **SHARED (+ or −)** | \|z\| ≥ 3.2 on H, with ZL the same sign at p ≤ 0.05 |
| **NOT SHARED (bounded)** | p > 0.05 on H **and** ZL, with power ≥ 0.8 (P(\|z\| ≥ 3.2)) to detect a shared component at ρ 0.7, at the lower 80% bound of Y's strength, under the drifting and the folio-level versions (the minimum of the two; computed by simulation at run time with frozen seeds) |
| **UNRESOLVED** | anything else |

- **Power at |z| ≥ 3.2** (block split, ρ 0.7, 200 replicates):

| Y dial | Folio-level, Y 0.35 | Folio-level, Y 0.5 | Drifting |
|---|---|---|---|
| CS | 0.16 | 0.29 | 0.45 |
| KTH | 0.18 | 0.31 | 0.47 |
| MIN | 0.21 | 0.33 | 0.49 |

- **NOT SHARED is unreachable at these strengths**, so Arm B returns SHARED or UNRESOLVED. A SHARED verdict requires strong sharing.
- **A dial without a SHARED verdict is reported as "not SHARED (UNRESOLVED; specificity untested)"**, never as NOT SHARED, "only" or "independent".
- **B1 strength estimates beyond the calibration grid** (0.7 logit) are flagged.

**Secondary (reported with p; no bounded negative):**
- **B3, co-drift within pages.** Folio-demeaned quarter profiles of E and Y from different key halves and different line blocks (buffer line between), after removing within-folio additive effects of line type (paragraph-final line, first body line, fullness tercile) and centring within stratum × quarter. Shift null.
  - Verdict: CO-DRIFT WITHIN PAGES at |z| ≥ the calibrated B3 critical value (the 99th percentile of max |z| over dials under independent drift, line-state and line-type plants), with ZL the same sign at p ≤ 0.05.
  - **Calibration** (`results/calib/calB3.json`, 400 replicates per H0):
    - 99th percentile of max |z| over dials: 3.19 (independent drift), 3.23 (line-state), 3.76 (line-type);
    - **critical |z| = 3.76**;
    - power at ρ 0.7 under shared drift: 0.06 (CS), 0.07 (KTH), 0.06 (MIN).
  - **B3 is descriptive** (lean-expert lock audit R7): z and p are reported, together with whether |z| ≥ 3.76. No label is issued.
- **Consistent-run sensitivity.** B1 and B2 on runs read alike by H, F and ZL (E, CS, KTH), and by H and ZL for MIN.
- **Descriptive:**
  - all pairs X(CS, KTH), X(CS, MIN), X(KTH, MIN), with a rank-1 (tetrad) check;
  - each dial's paragraph-level share;
  - OKOT and BENCH through B1 and B2.
- **Crowding probe** (descriptive). Within folio, each dial's residual against line fullness at a fixed within-line position (cell × position quintile), with the null permuted within cell × folio.
  - CS and MIN have registered within-frame line-position effects (C1983; C1244, C1909). The probe therefore measures fullness at fixed position, not position.

### Pattern (reported, not a single label)
The vector of per-dial verdicts, with signs, read through §10.
- **RUN-LENGTH-LINKED:** X(E, MIN) > 0 SHARED, with CS and KTH not SHARED (UNRESOLVED; specificity untested). E and MIN are both counts of a repeated stroke, so stroke habit, pen, leaf wear and the transcriber's stroke counting are all live readings.

## 8. Arm C — Page turns and writing order
### C1: directional continuity, present binding order
**Statistic.** K = Σ_t [b_t · top_{t+1} − top_t · b_{t+1}] over the 55 transitions:
- b and top are cross-frame bottom- and top-quarter residual means, centred within stratum;
- averaged over halvings and swaps.

**Null (b):** a sign flip per chain, exact under time-reversibility.
- Null (a) (per transition) failed calibration: size 0.030 under M4-0.97, 0.022 under M7 and 0.020 under parchment side at α 0.01. It is reported descriptively only.
- **Size of (b)** at α 0.01 (plants with background): M1 0.010; constant pages with neighbour correlation 0.3 / 0.6 / 0.9 at most 0.013; M2b ≤ 0.010; M3 0.018; M4-0.97 0.010; M7 0.015; mixtures ≤ 0.02; parchment side and quire trend ≤ 0.015.

**C1 is descriptive** (lean-expert lock audit E1).
- **Power.** Under null (b), the pre-specified criteria reach power of only:
  - 0.07 under M6-0.97 at B's strength;
  - 0.12 under M6-0.95 and M8-20;
  - 0.06 under M6-0.99.

  The 0.20 / 0.45 / 0.69 curve in the v3 draft had been computed under null (a).
- **Criteria**, reported as met or not met with no verdict label: K > 0, p(b) ≤ 0.01, ZL the same sign at p ≤ 0.05, and K of the same sign in Q13 and in Q20 separately.
- **Also reported:**
  - K, p(b), and p(a) (descriptive);
  - leaf turns and openings separately (openings depend on the binding);
  - K by quire half (Q13 and Q20);
  - the result on the 80-folio set (f76r excluded; f115r uninformative). If the H criteria differ between the two sets, it is labelled 80-folio-set-dependent.

### C2: which pages are alike? (descriptive)
Whole-page cross-frame similarity for same-quire pairs. Reading distance is counted on original page positions, so the missing leaves count.

**Comparisons:**
- sheet faces against same-quire pairs at exactly the same reading distance;
- the cross-face pairs of the same bifolium (e.g. f75r–f84r);
- a same-side indicator over all same-quire pairs (Gregory's rule).

**Face K.** Directional K along each sheet face (left page to right page; outer B-v→A-r, inner A-v→B-r; two-sided), beside leaf-turn K and opening K. Calibration:

| Plant | Face K > 0 | Leaf-turn K | Opening K | Q13/Q20 halves same sign |
|---|---|---|---|---|
| Flat-sheet writing (AR along face order) | 87% | +0.05 | −0.03 | 0.41–0.49 |
| Reading-order drift (M6) | 53% | +0.11 | +0.10 | 0.74–0.82 |
| Page-level models | 45–56% | about 0 | about 0 | about 0.5 |

**Covariates:**
- composition similarity (cosine of vocabularies of e-free tokens);
- legibility similarity;
- within a quire, e-propensity similarity against vocabulary similarity, with reading distance partialled out.

**Null:** Freedman–Lane permutation within quire.

## 9. Arm D — Floor (deferred) and an internal comparison
- **D0 (descriptive):** the e-dial S3c on Currier A.
- **Floor ("every hand drifts"):** its own phase, with feasibility fixed in advance: one hand, known page order, ≥ 60 pages, ≥ 3,000 informative within-frame choices.
- **Until then,** every POSITION-DEPENDENT or CONTINUITY result carries: *"consistent with ordinary scribal drift; floor untested"*.

## 10. What each source predicts
**Arm A** notation: S = static, P = position-dependent. P-restart restarts on each page; P-carry carries over.

| Source | Arm A | Arm B (sign) | C1 | C2 |
|---|---|---|---|---|
| Writer state, session | P, or S if one session per page | stroke dials (E+MIN+, E+CS+); KTH not | + only if the state carries over a turn | reading distance |
| Pen or ink cycle | P, steps at re-cuts | E+MIN+, E+CS+ (plume); attenuates on consistently read runs | + | reading distance |
| Every hand drifts (floor) | P | as writer state | + | reading distance |
| Unrecognised hand | S; P if the hand changes mid-page | general, including KTH and CS | 0; + if the change is mid-page | per bifolium: all four pages alike, face K ≈ 0 |
| Exemplar aligned with pages | S | general if the exemplars differ in several habits | 0 | exemplar blocks |
| Exemplar not aligned (M8) | P, steps | general if the exemplars differ in several habits | + | reading distance |
| Multi-step copying (Timm–Schinner) | P, local | any sign, lineage-dependent | + | reading distance |
| Space management or compression | S, edge, or P-restart | E+MIN+ only; CS and KTH 0; fullness probe + | 0 | layout |
| Neighbour context × vocabulary | S | own components, strongest in CS | 0 | composition |
| Content: page parameter or topic | S | E only, unless another dial tracks it (KTH via REGIME) | 0 | composition (C1978) |
| Content: running log | P (restarting per paragraph, M9, excluded by C2086's S3c) | E only | + | reading distance |
| Pictures | S or region | E only | 0 | picture |
| Parchment side | S | stroke dials (ink spread) | 0 | same side alike; leaf pairs unlike |
| Leaf wear or legibility | S or edge | E+MIN+, E+CS+ (as pen); absorbed by the legibility covariate; scan check | 0 | openings alike (rubbing); outer leaves of a quire |
| Composition or REGIME leakage | S | X(E, MIN) < 0 possible (C1205 r −0.41; C1732, C1740) | 0 | composition |
| Slow campaign trend | S within the page | depends | 0 | smooth decay with reading distance |
| Flat-sheet writing | depends | depends | leaf-turn and opening K of opposite sign in the two quire halves | face K > 0; faces more alike than cross-face pairs |
| Slow generator or cipher key | P or steps | depends | + | reading distance |

**Combinations (readings, not claims):**
- **P-DOMINANT + C1 criteria met (descriptive) + MIN or CS SHARED, with KTH not SHARED (UNRESOLVED; specificity untested):** leans towards the stroke / writer-state class over a running log or copying. Timm output produced this pattern in 0 of 50 members (requirement < 5%).
- **STATIC-DOMINANT + no dial SHARED:** consistent with, but does not show, e-specificity. Sharing at ρ ≤ 0.7 is not excluded (B2 power 0.16–0.49).
- **E+MIN+ SHARED with CS and KTH not SHARED (UNRESOLVED; specificity untested), plus a positive fullness probe:** leans towards space management. Without the probe it leans towards an extension carrier or a stroke-count source.
- **Do not discriminate on their own:** any single SHARED, P alone, the C1 statistics, any C2 pattern.

## 11. Guardrails (binding on the INDEX, registry and summaries)
| Outcome | Forbidden wording | Required wording |
|---|---|---|
| KTH shared | heat, fire, thermal, REGIME level, stage, encodes, tracks | "the folio components of the e-run and k/t-HEAD choices correlate within section and hand; k/t share is a REGIME-defining feature (C1715, C2070)" |
| MIN or CS shared, KTH not | pen, fatigue, scribal habit, meaningless | "shared with the minim (as read by H and ZL; scan check pending) [and plume] choice, not with k/t" |
| NOT SHARED (bounded) for a dial (unreachable at these strengths) | e-specific, content, parameter | "not shared with Y at latent ρ ≥ 0.7" |
| No dial SHARED (UNRESOLVED) | not shared, e-specific, independent of, content, parameter | "no shared component detected; B2 power at ρ 0.7 is 0.16–0.49, so sharing is not excluded" |
| A dial with no own component | shared, e-specific | "Y shows no folio component above its MDE80 (x logit)" |
| STATIC-DOMINANT | program, recipe, procedure, chosen setting, no drift, constant on the page | "page-level component; position-dependent models with D14 ≥ 0.5 disfavoured; slow drift (D14 ≈ 0.2) not distinguished" |
| POSITION-DEPENDENT-DOMINANT | the scribe drifted, one sitting, written in the present order, the binding is original | "varies within the page; static models with D14 ≤ 0.15 disfavoured; mechanism not distinguished", plus "consistent with ordinary scribal drift; floor untested" |
| C1 criteria met (descriptive) | continuity shown, the scribe drifted, written in the present order | "the pre-specified continuity criteria are met across the tested page turns (present binding order); descriptive, power about 0.1" |
| B3 (descriptive) | fatigue, pen, co-drift shown | "E and Y quarter profiles, line-type adjusted: z = …" |
| Arm 0 stands | context irrelevant | "C2086 stands against the preceding-glyph context model (additive, within folio)" |
| C2, face K | flat sheets, per bifolium, hair/flesh | "pair type X is more alike than distance-matched pairs (descriptive)" / "directional continuity along sheet faces (descriptive)" |

Also forbidden:
- "confirms C1977";
- any verdict on Davis's hands;
- asserting drift in C2086 unless Arm A reaches POSITION-DEPENDENT-DOMINANT. Naming it as unresolved stays allowed.

## 12. Error control
| Verdict | Error bound (calibrated on controls) |
|---|---|
| Arm 0 note, falsely issued | ≤ 0.04 at B's strength (H 0.02, ZL 0.04) |
| Arm A wrong class | ≤ 0.05 for pure models at B's point, the gate evaluated on fresh draws at run time |
| Arm A, gated mixtures | other class ≤ 0.15. The M1+M3 25% mixture sits at the limit in-sample: POSITION 0.148 (n 61) at (0.32, 0.09) and 0.150 (n 40) at (0.34, 0.09) |
| Arm A, intermediate truths | labelled STATIC up to 0.72 (M4-0.99) and POSITION up to 0.75 (M6-0.97) at (0.32, 0.09). A verdict carries its D14 bound |
| Arm A, in-sample note | the pre-lock gate map used the same replicates as the threshold selection; the run's gate uses fresh draws |
| Arm B SHARED, any dial | ≤ 0.007 (independent drift) and ≤ 0.006 (independent folio-level components); family-wise over the three dials at \|z\| ≥ 3.2 |
| Arm B NOT SHARED miss | ≤ 0.2 by rule (power ≥ 0.8); unreachable at these strengths |
| B3 (descriptive) | \|z\| ≥ 3.76: ≤ 0.01 family-wise (worst H0: line-type plant) |
| C1 criteria (descriptive) | ≤ 0.018 under the no-continuity plants; power 0.06–0.12 |
| Any positive verdict across arms | ≤ about 0.1 (sum of the above) |
| A combination reading | its weakest leg |

No claim requires more than one arm. The §10 combinations are readings, not claims.

## 13. Calibration results (controls only; `results/calib/`)
- **Pilot** (`pilot.json`):
  - s* per model;
  - pooled context and fullness effects;
  - CONTEXT gives S3c of about 0 at 1–3×;
  - M8-10 and M9 cannot reach S3c 0.25.
- **Arm 0** (`cal0.json`): §5.
- **Arm A** (`bank/bank_v3_H81_770.json`, `bank/clf_v3_H81_770.json`, `bank/thr_v3_H81_770.json`, `bank/clf_v3_ZL_770.json`).
  - **Bank:** 10,000 replicates per model with S3c in [0.25, 0.40], plants with background.
  - **v2's classifier failed its gate** (`bank/gate_H81_0.323_0.095_770_v2double.json`). The v3 classes are by D14.
  - **Thresholds** 0.9 and 10, calibrated with `thr770.py`. Raw features.
  - **Raw gate:** passes at 22 of 25 grid points, including all nine at S3c 0.30–0.34 × S3far 0.06–0.12. The ZL bank also passes at 22 of 25.
  - **Verdict probabilities at (0.32, 0.09)** (raw):
    - static models: STATIC 0.79–0.92, POSITION ≤ 0.02;
    - position-dependent models: POSITION 0.92–0.98, STATIC ≤ 0.01;
    - intermediate models: M2c 0.69 STATIC; M7 0.36 STATIC / 0.44 POSITION; M4-0.97 0.59 POSITION; M4-0.99 0.72 STATIC; M6-0.97 0.75 POSITION; M6-0.99 0.58 STATIC; M8-40 0.63 POSITION;
    - mixtures: M1+M3 25% 0.51 STATIC / 0.15 POSITION; 50% 0.25 / 0.32; 75% 0.07 / 0.73.
  - **Bank checksums** (`bank_checksums.txt`; the `.npz` files are gitignored and reproducible from the frozen seeds):
    - bank_v3_H81_770.npz sha256 66f53676…51cdd
    - bank_v3_ZL_770.npz 99006dda…b3742
- **Arm B:**
  - `calB.json`: B1 curves and MDE80s.
  - `calB_relabel_null.json`: the random-relabelling certification that failed.
  - `calBj_half.json`, `calBj_block.json`, `calBj_block_cert.json`, `calBj_block_power.json` and the `calBj_raw_*` / `calBj_power_z_*` arrays: the joint certification with the shift null; critical |z| 3.2; power table in §7.
  - `calB3.json`: B3.
- **Arm C** (`calC.json`): §8, plus A3's size and power.
- **Negative texts** (`results/calib/neg_v3.json`; Naibbe dropped):
  - **Timm–Schinner, 50 members.**
    - Informative e-runs: median 825, against B's 6,229, because its vocabulary is page-specific.
    - S3c fires (p ≤ 0.01) in 46% (median 0.37), as expected from copying.
    - Arm 0's note would fire in 10%.
    - A2, with the window and the gate as in the run: POSITION-DEPENDENT 2%, UNRESOLVED 98% (fit check fails in 96%).
    - A3 0%; C1 CONTINUITY 2%.
    - B1: Y dials too sparse, never fires. B2 SHARED 0% for every dial. B3 2% (CS).
    - Combination 1: 0%.
  - **habit3b, 3 members:** nothing fires. With the window and the gate, A2 is UNRESOLVED in all three. The bare classifier labelled them STATIC at S3c about 0.04, hence the window condition.
  - **Caveat (lean-expert lock audit R8):** the Timm Arm A check used B's H81 bank on Timm's own cell structure, a mismatched skeleton. This contributes to the 96% fit-check failures.
  - v2 panel: habit3b and Naibbe fired nothing at 0.01; Timm produced folio components in 2 of 3 members.
- **Dry run** (`scripts/run_b770.py --dry`; `results/dryrun/`):
  - the full pipeline on a habit3b control poured into every analysis set, with small banks.
  - **Final version** (after the lock audit), every path exercised:
    - one bank-extension round;
    - the consistent-run B2 (pseudo-random consistency masks, since the flags are meaningless on poured text);
    - D0 on a habit3b control poured into Currier A's skeleton;
    - the fresh-draw gate at a fixed point.
  - Results in `results/dryrun/run_log.txt`.

## 14. MIN scan check (required before any MIN claim is registered)
- **Sample:** 100 minim groups stratified by folio. 60 are drawn from the 879 groups H reads as one minim and F as 2+; 20 are agreed single and 20 agreed 2+.
- **Blind coding** by the human on the Beinecke scans (`sources/voynich_scans/images`):
  - each crop shows the word with its minim group marked;
  - no transcription is shown;
  - order is randomised.
- **Decision rule (fixed now):**
  - one minim read in ≥ 80% of the disputed groups: the H/ZL reading stands, and MIN claims can be registered;
  - ≤ 50%: F's reading stands, and MIN results are withdrawn;
  - otherwise unresolved: MIN results stay descriptive.
- The scan check does not block the run.

## 15. Run-time procedure (fixed at lock)
Idle priority; frozen code and seeds.

**Lock constants in `scripts/run_b770.py`:**
- `LOCK = 'phase770-lock'`: a git tag on the lock commit. At start the run script checks that the tag exists, that `git diff --quiet phase770-lock -- phases/PHASE_770_E_DIAL_PROCESS/scripts` holds, and that the banks match `results/calib/bank_checksums.txt`;
- `A2_VERSION = 'raw'`;
- `B2_SPLIT = 'block'`;
- `B2_ZCRIT = 3.2`;
- `B3_ZCRIT = 3.76`;
- `NPERM = 2000`.
1. Build the analysis sets (H, ZL, sensitivities).
2. Arm 0: S3c_adj (H and ZL).
3. Arm A:
   - compute S3c, S3far and features on H and ZL;
   - load the checksummed banks and extend them if needed (frozen seeds);
   - A2 with the fit check, the S3c window and the fresh-draw gate at B's point;
   - A3;
   - ZL classification (window) and the no-flip checks (window);
   - A1, A4 and A5 descriptives.
4. Arm B: B1, then B2 (joint shift null, \|z\| ≥ 3.2 with the ZL leg; Westfall–Young descriptive), then B3 (descriptive); the power simulation at the lower bound; the sensitivities and descriptives.
5. Arm C (descriptive): C1 (null (b)), the ZL check and quire signs, leaf and opening, quire halves, the 80-folio set; C2.
6. D0.
7. Verdicts by the rules above, and the report.

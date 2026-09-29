# PHASE_770 — What kind of process sets the e-dial? (pre-registration)

**Status: DRAFT v2.** This version merges the reviews of v1 by expert-advisor, lean-expert and crazy-expert
(2026-09-29). It goes to calibration on controls, then a final lean-expert check, then the lock. No statistic under
this design has been computed on B. §2 lists what is already known and what the design stage computed.

## 1. Origin and question
**C2086 (PHASE_769).** With the word frame and position fixed, the choice of one e versus 2+ carries a folio-level
component shared across different words: S3c +0.323, z 4.3, ZL p 0.0005.
- Whether it drifts within the page is unresolved (S3far/S3c 0.29, SE about 0.22).
- The source is open. The human asked for three tests, designed and checked by the experts before any run:
  - the shape of the component over the page (**Arm A**);
  - co-drift of other free spelling choices (**Arm B**);
  - continuity across page turns in writing order (**Arm C**).
- The reviews added **Arm 0**: a check that C2086 is not produced by neighbour context combined with folio
  vocabulary.

This phase can favour or disfavour classes of source. It cannot identify one: every source reading is echo-class
(§11).

## 2. What is already known about B (disclosure)
**Known from PHASE_769 (e-dial, 80 folios):**
- S3c +0.323, S3 +0.315 and S3far +0.095;
- S3P, and S3P-within (p 0.58, which overlaps A3);
- per-stratum S3c;
- frame-controlled folio propensities, and their recto/verso leaf-pair correlation (r 0.26, 27 pairs; this is C2's
  leaf-pair cell).

**Prior evidence on the other dials (not frame-controlled):**
- **CS (ch/sh):**
  - depends on section (C409, C410) and has a folio component (C1182, ICC 0.317; C639);
  - sister choice is about 32% folio-determined and mostly at paragraph level (C1180, C1182);
  - line-start clustering (C1983); sh before ch in paragraphs (C1963);
  - coupled to the word boundary (C1186, C1212, C1563, C2082);
  - independent of ok/ot (C1184).
- **KT:** k and t head different MIDDLEs (C1478, C1538). The k share is a REGIME-defining axis (C1715, C1871, C1920,
  C2070; C865, C1872, C1890).
- **MIN:**
  - only e and i extend (C1197);
  - the ii/ee choice splits by HEAD atom (C1912);
  - folio-level e/ii relations (C1732, C1740);
  - graded by section and REGIME (C1204, C1730, C1234).
- **Line and page position:**
  - e collapses in the last quarter of a line (C1566, C1672);
  - line-final e/k depletion (C1235); early-line e→y (C1460);
  - first-body and paragraph-final lines are distinctive (C1729, C1837, C1237);
  - lines shorten with paragraph order (C1782, C1783);
  - the e-fraction gradient is composition (C1206, C1855).
- **Pair structure of composition:** leaf pairs (C1978); bifolia (PHASE_759, Q13 p 0.013, Q20 p 0.017, unregistered);
  page adjacency (C361, C1839).

**Computed in the design stage** (`scripts/design_checks770.py`, `results/design_checks.json`; §3): transcription
agreement, counts and codicology.

**Pooled quantities, computed before lock only to parameterise plants** (not by folio, position or page turn):
- the pooled effect of the preceding glyph unit on each dial's outcome within its cell (CONTEXT plant);
- the pooled effect of line fullness (LAYOUT plant).

**Not computed on B:**
- any dial statistic by folio, page position, paragraph order or page turn;
- S3c and S3far on the new analysis set. A2 conditions on these at analysis time from a plant bank generated in advance
  (§6).

## 3. Design checks (done)
### 3.1 Transcription agreement
H–F uses the interlinear file, on the same line ids. H–ZL matches lines by content, because ZL numbers its loci per page
in one sequence: 421 equal line ids name different lines.

| Dial | Marked value | κ H–F | κ H–ZL | Occurrences | Informative | With variation | Marked rate |
|---|---|---|---|---|---|---|---|
| E | 2+ e | 0.984 | 0.995 | 9,927 | 5,851 | 4,382 | 0.37 |
| CS | sh | 0.992 | 0.994 | 8,440 | 4,425 | 3,535 | 0.35 |
| KT | t | 0.984 | 0.987 | 9,816 | 6,046 | 4,903 | 0.33 |
| MIN | 2+ minims | **0.423** | **0.971** | 4,258 | 2,921 | 2,507 | 0.61 |
| BENCH | benched | 0.999 | 1.000 | 11,885 | 6,215 | 918 | 0.08 |

(Counts are for the 80-folio H set.)

- **F differs from H and ZL on minims** (κ 0.42 against 0.97). Which reading matches the scans is unsettled: H and ZL are
  not independent readings, and κ is an upper bound.
  - The registry annotations C1204 and C1910, the STATUS_BRIEF line and the PHASE_769 INDEX were corrected in the design
    commit.
  - MIN is "the minim count as read by H and ZL". No MIN claim is registered without a blind scan check of about 100
    minim groups stratified by folio (§8).
- **BENCH** is descriptive only (918 occurrences with variation).

### 3.2 Analysis set
- **f76r is included.** H codes its 546 tokens (47 lines, 4 paragraphs) as placement R; ZL codes them as paragraph text.
  - Its text lines match ZL's in order.
  - The single-glyph "sentinels" (C762) are coded as labels in H and stay excluded.
  - Its stratum is B/2.
- **f115r's hand is set to 3.** Its $H in ZL is blank, which put it in a one-folio stratum where PHASE_769 got no
  informative runs; its quire Q20 is hand 3. A sensitivity excludes it.
- **Resulting set:** 81 folios. The e-dial has 10,184 occurrences, 6,229 informative.
- **Sensitivity:** every Arm A and Arm B verdict is recomputed on PHASE_769's 80-folio set (f76r out, f115r as before).
  If the two sets give different verdicts, the arm is UNRESOLVED.
- **Paragraphs:** no B page opens mid-paragraph, except f75r at the start of Q13. No paragraph spans a tested page turn.

### 3.3 Codicology (ZL page variables $Q, $B, $F, $H)
- **Usable reading-order transitions (no foldout panels): 55.**
  - 34 leaf turns and 21 openings.
  - f40v→f41r is excluded: it crosses a quire and changes hand.
- **Chains:** the transitions form chains led by Q13 f75r–f84v (20 pages), Q20 f103r–f108v (12) and f111r–f116r (11).
  - Q13 carries 19 of the 55 transitions.
  - f108v→f111r is a gap, because f109–f110 are missing.
- **Sheet faces:** 34 conjoint face pairs have both pages in B, and only f79v | f80r is reading-adjacent.
  - The inner face is A-v | B-r, the outer face A-r | B-v.

### 3.4 Floor corpus
The Aberdeen Bestiary has about 60 ti/ci and 24 y/i minority tokens, which is infeasible. The floor is deferred to its
own phase (§9).

## 4. Common machinery
**Basis:** PHASE_769's occurrence, cell and permutation engine, generalised (`scripts/ed770.py`; it reproduces PHASE_769's
arrays exactly).
- The dial frame is the token with every unit of the dial's class replaced by a class symbol (e-runs collapsed), plus
  the slot index.
- The cell is frame × slot × line zone × header line × paragraph-length tercile × section × hand.
- The CS cell also includes the preceding glyph unit (the last unit of the preceding token, or START / GAP).

**Residuals.**
- r = y − cell mean.
- In Arms A and C, residuals are also centred within stratum × page quarter (A1, C1) or stratum × position decile (A3).
  This removes position gradients that differ by stratum.

**Cross-frame split.** Every statistic compares keys from one random half with keys from the other (50 halvings, both
assignments). The key is the dial frame, or for a pair of dials the **joint frame**: both dials' units replaced by their
symbols.

**Folio covariates** (S3c):
- log lines, tokens per line and paragraphs;
- legibility **recomputed with every dial class collapsed**, so it cannot carry the MIN or E outcome. PHASE_769's
  version is kept as a sensitivity.

**ZL rule (every verdict):** H at the stated α, and ZL with the same sign at p ≤ 0.05.

## 5. Arm 0 — Is C2086 produced by neighbour context?
Neighbour coupling (C1212, C1563, C2082, C1994) combined with folio-specific vocabulary (C531) could produce a static
folio component shared across frames. PHASE_769's local-persistence control did not model this.

- **0a (B).** S3c with the preceding glyph unit added to the E cell, on the analysis set.
- **0b (plant).** The CONTEXT plant draws y from each occurrence's cell rate, shifted by the pooled preceding-glyph
  effect and centred within the cell. It uses B's actual neighbours, so any folio component it produces comes from folio
  composition alone.
- **Rule:**
  - If 0a gives p > 0.01 (H), or ZL fails, C2086 receives a scope note: *"not separated from neighbour context ×
    folio vocabulary"*.
  - If CONTEXT plants reach a mean S3c ≥ 0.16 (half of B's), the same note applies.
  - Otherwise C2086 stands against this rival.

## 6. Arm A — Shape of the component over the page
### A1: quarter covariance matrix (descriptor; source of A2's features)
- **Estimator.** For halving h and assignment, over folio sums S and counts n:

  C_h(q, q') = Σ_f S^A_{f,q} S^B_{f,q'} / Σ_f n^A_{f,q} n^B_{f,q'}

  - S^A_{f,q} is the sum of residuals of half-A keys in quarter q of folio f.
  - Averaged over halvings and assignments, then symmetrised.
- **Properties.** Every folio enters every element, so there is no per-element folio set. Sampling noise and effects
  specific to one word do not enter.
- **Features (7):** V1–V4 (the diagonal) and the mean off-diagonal at quarter distances 1, 2 and 3. Two versions:
  - raw;
  - scale-free (each divided by the mean of the seven).
- **Reported per stratum** (S/3, B/2, other) as a descriptor. The quarters of short herbal pages are about 2 lines, so
  the pooled result mainly describes Bio and Stars.

### A2: classification against a plant bank
Every model is planted as synthetic y on the analysis set's cells.

| Class | Models |
|---|---|
| **STATIC** | M1 constant setting per folio |
| | M2a paragraph-edge lines (header, paragraph-final) unexpressed |
| | M2b page-edge lines unexpressed, 2 / 4 / 6 lines at each end |
| | M2c first and last paragraph unexpressed |
| | M7 constant plus independent paragraph offsets (half the variance) |
| | CONTEXT (as 0b) |
| | LAYOUT: constant plus the pooled line-fullness effect |
| **POSITION-DEPENDENT** | M3 random walk over lines, restarting at 0 on each page |
| | M4 stationary AR(1) over lines restarting on each page, ρ 0.95 / 0.97 / 0.99 per line |
| | M5 page-specific linear trend from a common start |
| | M6 the M4 process continuing across pages along reading-order chains, stationary at each chain start |
| | M8 changepoints along writing order, level iid at each change, mean segment 10 / 20 / 40 lines, continuing across turns |
| | M9 walk restarting at each paragraph |
| **Mixtures** (not a class) | M1 plus M3 or M6, with 25 / 50 / 75% of the variance position-dependent |

**Strength.**
- Each model's scale is drawn from a wide prior. A replicate is accepted when its S3c and S3far fall within ±0.03 of
  B's values on the analysis set, computed at run time.
- The bank is generated before lock and large enough to leave ≥ 200 accepted replicates per model at B's
  PHASE_769 values (S3c 0.32, S3far 0.095). The same check is repeated at run time.

**Classifier.**
- A multivariate normal on the 7 features, fitted to each model's accepted replicates.
- Equal prior per class, split equally among the models within a class, and equally among each model's variants.

**Verdict rule.**
- **Fit check.** B's squared Mahalanobis distance to the best-fitting model must lie below that model's own 99th
  percentile; otherwise UNRESOLVED (model set inadequate).
- **Classes.** Class posterior ≥ 0.8 gives STATIC-DOMINANT or POSITION-DEPENDENT-DOMINANT; otherwise UNRESOLVED.
- **Two-part Bayes factor.**
  - Report the known part (S3far given S3c) and the new part (V1–V4 and off-diagonals, given S3c and S3far).
  - A verdict is confirmatory only if the new part favours the same class.
  - Otherwise the report reads "carried by the already-known S3far".
- **Within POSITION-DEPENDENT-DOMINANT:** restarting on each page (M3, M4, M5, M9) against carrying over (M6, M8),
  reported descriptively.

**Gate.** Evaluated on held-out accepted replicates, at the PHASE_769 values before lock and at B's values at run time.
- Each pure model reaches its own class at posterior ≥ 0.8 in ≥ 70% of replicates, and the wrong class in ≤ 5%.
- Each 50/50 mixture reaches either class in ≤ 25%.
- If the gate fails, A2 is descriptive and Arm A is UNRESOLVED.
- The gate is run on both feature versions. The version used for the verdict is fixed at lock from calibration: the one
  that passes, preferring raw.

### A3: paragraph order (veto only)
- **Units:** paragraph means over body lines only (header and paragraph-final lines excluded). The first and last 2
  lines of each page are excluded. Residuals are centred within stratum × position decile.
- **Statistic.** D is the mean cross-frame product of the paragraph means for adjacent paragraphs, minus that for
  paragraphs 2 or more apart.
  - Each pair is weighted by the smaller of its two half-counts.
  - Paragraph halves with fewer than 2 occurrences are dropped.
  - Folios with ≥ 3 usable paragraphs.
- **Null:** paragraph order permuted within each folio (2,000). Its size is checked under M1, M2a, M2b, M7 and LAYOUT.
- **Role:** veto only (power about 0.23 against M3 at B's strength). If A3 gives p ≤ 0.01 while A2 says STATIC-DOMINANT,
  Arm A is UNRESOLVED.

### A4: edge checks (descriptive)
S3c and S3far recomputed with stratum × quarter centring, in four versions:
- all lines;
- without header and paragraph-final lines;
- without the first and last 2 lines of each page;
- without the first and last 4 lines of each page.

### A5: residual variogram (descriptive)
- **Measure:** the cross-frame covariance of line residual sums against absolute separation in lines (1, 2, 3–4, 5–8,
  9–16, 17–32). Computed within pages, and separately for same-paragraph and different-paragraph pairs.
- **Reported:** by page-length stratum (< 20 and ≥ 20 lines), and continued through page turns along reading-order chains.
- **Envelopes:** M1, M2b-4, M3, M6 and M8 plants.

### Arm A verdict
- **Rule:** A2's verdict, subject to A3's veto and the ZL rule (A2 recomputed on ZL must reach the same class, or
  UNRESOLVED).
- **Sensitivities that must agree, otherwise UNRESOLVED:**
  - the 80-folio set;
  - the E cell with line-fullness tercile added;
  - runs read alike by H and F.
- **Reported, not verdict-bearing:** per-stratum A1, A4 and A5.

## 7. Arm B — Do other spelling choices share the component?
**Dials:**
- **CS** (sh vs ch; cell includes the preceding glyph unit): a plume stroke that is also grammatical. Its own component
  is anticipated (C1182).
- **KT** (t vs k): the lexical control dial, on the REGIME axis. Its own component is anticipated.
- **MIN** (2+ minims): E's extension sibling, "as read by H and ZL".
- **BENCH:** descriptive.

### B1: own component
S3c per dial. A dial has its own component at p ≤ 0.01 (H) under the ZL rule. MDE80 and the lower 80% bound of its
strength are reported. MIN is also run on F as a sensitivity.

### B2: shared folio component (primary; run for all three dials whatever B1 says)
- **Statistic.**
  - For each of 50 joint-frame halvings: E's covariate-residualised folio mean vector (its key half, top half of the
    page) and Y's (the other key half, bottom half).
  - X is the mean correlation over halvings, key-half swaps and page-half swaps.
  - Cross-half excludes adjacent-token coupling (C1212, C2082).
- **Null (pairing).** Y's folio labels are permuted within stratum (section × hand), with one relabelling applied to
  every halving and swap; 2,000 relabellings. The lean-expert's simulation gave size 0.007 at α 0.01, and power 0.82 at
  shared ρ 0.7.
- **Multiplicity:** Westfall–Young max-|z| over the three dials; two-sided.

**Per-dial verdicts:**

| Verdict | Condition |
|---|---|
| **SHARED (+ or −)** | adjusted p ≤ 0.01, under the ZL rule |
| **NOT SHARED (bounded)** | p > 0.05, with calibrated power ≥ 0.8 to detect a shared component at ρ 0.7, at the lower 80% bound of Y's own strength (B1) |
| **UNRESOLVED** | anything else |

- "No own component" counts as NOT SHARED only if B1's MDE80 is ≤ 0.25 logit.

**Secondary:**
- alternating 3-line blocks with one buffer line, for power under drift;
- all pairs X(CS, KT), X(CS, MIN) and X(KT, MIN), with a rank-1 (tetrad) check;
- each dial's paragraph-level share (S3P-within analogue).

### B3: co-drift within pages (secondary)
- **Statistic:** the covariance of folio-demeaned quarter profiles between E (key half A, odd lines) and Y (key half B,
  even lines). It is immune to folio-level REGIME, section and composition effects.
- **Null:** the same pairing null.
- **Verdict:** CO-DRIFT WITHIN PAGES at p ≤ 0.01 under the ZL rule. There is no bounded negative.

### Pattern (reported, not a single label)
The vector of per-dial verdicts, with signs, read through §10. X(E, MIN) > 0 alone is named RUN-LENGTH-LINKED: E and MIN
both count a repeated stroke, so stroke habit, pen and the transcriber's stroke counting are all live readings.

### Line crowding probe (descriptive, E and MIN)
- **Measure:** within folio, the dial residual against the line's collapsed glyph length and against tokens remaining to
  the line end.
- **Null:** permutation within cell × folio.
- **Prediction:** space management predicts effects for E and MIN only.

## 8. Arm C — Page turns and writing order
### C1: directional continuity (present binding order)
- **Statistic.** K = Σ_t [b_t · top_{t+1} − top_t · b_{t+1}] over the 55 transitions.
  - b and top are the cross-frame bottom- and top-quarter residual means: key half A on one page, half B on the other,
    averaged over halvings and swaps.
  - Each is centred within stratum.
- **Null (a):** a sign flip per transition, if its calibrated size is ≤ α under all of the following:
  - constant pages with neighbour correlation 0.3 / 0.6 / 0.9;
  - M2b; M3; M4; M7; mixtures;
  - a parchment-side plant (Gregory's rule, pages two apart anti-correlated);
  - a quire trend × stratum offset;
  - Timm–Schinner output.

  Otherwise **null (b):** a sign flip per chain.
- **Verdicts:**

| Verdict | Condition |
|---|---|
| **CONTINUITY ACROSS PAGE TURNS (present binding order)** | K p ≤ 0.01 under the ZL rule, with the same sign in Q13 and Q20 separately |
| **UNRESOLVED** | anything else |

  - NO CONTINUITY is unreachable (power about 0.22 under M6 at B's strength). MDE80 is reported, including under M6 +
    M2b.
- **Also reported:** leaf turns and openings separately (openings depend on the binding, leaf turns do not); and the
  result without f76r.

### C2: which pages are alike? (descriptive)
Whole-page cross-frame similarity for pairs of pages in the same quire.
- **Face vs matched pairs.** Sheet-face pairs against same-quire pairs at exactly the same reading distance.
- **Parchment side.** A same-side indicator (Gregory's rule) over all same-quire pairs.
- **Face K.** Directional K along each sheet face (inner A-v→B-r, outer B-v→A-r; two-sided), beside leaf-turn K and
  opening K:

| Source | Face K | Leaf-turn K | Opening K |
|---|---|---|---|
| Flat-sheet writing | > 0 | ≈ 0 | ≈ 0 |
| Writing in the present reading order | ≈ 0 | > 0 | > 0 |
| Written in reading order, later misbound | ≈ 0 | > 0 | ≈ 0 |
| Hand, exemplar, parchment | ≈ 0 | ≈ 0 | ≈ 0 |

- **Covariates:**
  - composition similarity (cosine of e-free token vocabularies);
  - legibility similarity;
  - within a quire, e-propensity similarity against vocabulary similarity with reading distance partialled out (content
    predicts a relation; a key or generator does not).
- **Null:** Freedman–Lane permutation within quire.

## 9. Arm D — Floor (deferred) and an internal comparison
- **D0 (descriptive):** the e-dial S3c on Currier A, a different hand and "language", with the same machinery.
- **Floor ("every hand drifts"):** its own phase, with feasibility fixed in advance:
  - one hand;
  - known page order;
  - ≥ 60 pages;
  - ≥ 3,000 informative within-frame choices.

  Candidates are a diplomatic corpus with abbreviation choices, or a dated single-hand notebook (spelling variants such
  as ye/the, &/and).
- **Until it runs,** every POSITION-DEPENDENT or CONTINUITY result carries: *"consistent with ordinary scribal drift;
  floor untested"*.

## 10. What each source predicts
**Arm A** notation: S = static, P = position-dependent. P-restart restarts on each page, P-carry carries over; "steps"
means changepoints.

| Source | Arm A | Arm B (sign) | C1 | C2 |
|---|---|---|---|---|
| Writer state, session | P (restart or carry) | stroke dials (E+MIN+, E+CS+); KT not | + | reading distance |
| Pen or ink cycle (wear, re-cut) | P, steps at re-cuts | E+MIN+, E+CS+ (plume); attenuates on consistently read runs | + | reading distance |
| "Every hand drifts" (floor) | P | as writer state | + | reading distance |
| Unrecognised hand | S; P if the hand changes mid-page | general, incl. KT and CS | 0; + if the change is mid-page | hand blocks (per bifolium: same as flat sheets) |
| Exemplar aligned with pages | S | general if the exemplars differ in several habits | 0 | exemplar blocks |
| Exemplar not aligned with pages (M8) | P, steps | general | + | reading distance |
| Multi-step copying (Timm–Schinner) | P, local | any sign, lineage-dependent | + | reading distance |
| Space management, compression down the page | S, edge, or P-restart (M5-like) | E+MIN+ only; CS, KT 0 | 0 | layout |
| Neighbour context × vocabulary (CONTEXT) | S | own components, strongest in CS; sharing via common context | 0 | composition |
| Content: page parameter or topic | S | E-only unless another dial tracks it (KT via REGIME) | 0 | composition (C1978) |
| Content: running log (whole text or per paragraph) | P (P-restart per paragraph for M9) | E-only | + (whole text) | reading distance |
| Pictures | S or region | E-only | 0 | picture |
| Parchment side | S | stroke dials (ink spread) | 0 | same side alike; leaf pairs unlike |
| Leaf wear or legibility | S or edge | fewer strokes: E−, MIN−; CS toward ch | 0 | leaf pairs alike |
| Slow trend over the writing campaign | S within page | depends | 0 | smooth decay with reading distance |
| Slow generator or cipher key | P or steps | depends | + | reading distance |

**Combinations that discriminate:**
- **P + C1 continuity + MIN or CS shared, KT not:** favours the stroke / writer-state class over a running log or
  copying.
- **S (bounded) + all B2 NOT SHARED:** disfavours writer state, copying and a hand that carries its own habits.
- **E+MIN+ only, plus a positive crowding probe:** favours space management. Without the probe it favours an extension
  carrier.

**Combinations that do not discriminate:**
- any single SHARED;
- P alone;
- C1 alone;
- any C2 pattern.

## 11. Guardrails (binding on the INDEX, registry and summaries)
| Outcome | Forbidden wording | Required wording |
|---|---|---|
| KT shared | heat, fire, thermal, REGIME level, stage, encodes, tracks | "the folio components of the e-run and k/t choices correlate within section and hand; k/t share is a REGIME-defining feature (C1715, C2070)" |
| MIN or CS shared, KT not | pen, fatigue, scribal habit, meaningless | "shared with the minim (and plume) choice, not with k/t" |
| Nothing shared | e-specific content, parameter | "not shared with MIN, CS or KT at latent ρ ≥ 0.7" |
| STATIC-DOMINANT | program, recipe, procedure, chosen setting | "page-level component; no detected dependence on line position (bounded against the position-dependent models)" |
| POSITION-DEPENDENT-DOMINANT, or CONTINUITY | the scribe drifted, one sitting, written in the present order, the binding is original | "changes with line position" / "continuity across the tested page turns, present binding order", plus "consistent with ordinary scribal drift; floor untested" |
| C2 | flat sheets, per bifolium, hair/flesh | "pair type X is more alike than distance-matched pairs (descriptive)" |

Also forbidden: "confirms C1977", and any verdict on Davis's hands. "Drift" stays out of C2086 unless Arm A reaches
POSITION-DEPENDENT-DOMINANT.

## 12. Error control
- **Primary verdicts:** Arm 0 (0a), Arm A (A2 with the A3 veto), Arm B (B2 per dial, Westfall–Young within the arm) and
  Arm C (C1).
- **Family-wise error:** each arm is tested at α 0.01. With four arms this is ≤ 0.04 (Bonferroni bound). No claim
  requires more than one arm.
- **Everything else is secondary or descriptive** and is labelled as such.

## 13. Calibration before lock (controls only; Idle priority)
**Plant bank (A2).** All models and mixtures in §6, with wide strength priors, generated until ≥ 200 replicates per
model are accepted at the PHASE_769 values.
- This gives the gate, the confusion matrix, and a mixture check.
- A3's size under M1, M2a, M2b, M7 and LAYOUT, and its power under M3, M5 and M6.

**Arm 0.** CONTEXT plants: mean S3c and its distribution.

**Arm B:**
- **Size:**
  - E and Y each carrying an independent component, including independent M6 walks;
  - word-level coupling (a word preferred per folio on both dials);
  - habit3b-style local-rule generators fitted to CS and KT.
- **Power:** a shared latent component at ρ 0.4 and 0.7, over a grid of Y strengths, with folio-level and drifting
  versions.
- **B1 MDE80** per dial.

**Arm C:**
- size of null (a) under the full list in §8;
- power (MDE80) under M6 and M6 + M2b.

**Negative texts, all arms:** Timm–Schinner, habit3b and Naibbe poured into B's skeleton.

**Verdict-probability tables** (the probability of each verdict under each plant) are published in the locked text.

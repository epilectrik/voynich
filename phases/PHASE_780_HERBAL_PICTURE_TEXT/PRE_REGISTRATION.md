# PHASE_780 — Does the herbal text co-vary with its drawings? A blind picture test within one hand, with an illustrated herbal as positive control (pre-registration)

**Status: DRAFT v2 after the lean-expert design audit (v1: LOCKABLE AFTER EDITS; all blocking items A1–A6, the adopted
non-blocking items and the drops in C are incorporated; changes are listed at the end). Nothing below has been computed
on the Voynich text–picture alignment. No image has been coded.**

**Origin.** STATUS_BRIEF and RESEARCH_AGENDA item 8 ("pictures and text, powered"): the earlier picture tests had
n ≈ 30 and little power (VIS, ILL-TOP-1); the first powered test found no signal for one narrow design (C2084, label
recurrence, 13 pairs). The agenda's next step is a blind picture-coding test within one section and hand that does not
assume a label is a word of the text and that tests writing-session drift and copying as rival sources. This phase is
that test for the herbal section. Content claims need an external channel (C171, Tier 3; C2052); the drawings are
external to the text.

**Question.** On the herbal pages written by one hand (Currier A, Davis hand 1), do pages whose plant drawings are
similar carry similar text, beyond page position, quire, bifolium, layout, spelling dials, drawing style and text
length? The same statistic is run on an illustrated herbal whose text refers to its pictures (Brunschwig, *Liber de
arte distillandi de simplicibus*, Strasbourg 1500, Part 2), matched to the Voynich data, to say whether this test
could see such a link at this size.

**What each outcome can show (asymmetric by design; declared now).** NOT DETECTED is predicted by every hypothesis in
which the text does not describe plant form: content-free text, a process notation, a herbal of names and uses. It
discriminates only against form-describing text. CO-VARIES is predicted by form-keyed text, or by a picture-keyed
writing habit that survives the covariates. A positive can move the reading of the manuscript strongly; a
genre-powered negative mainly removes form-describing text. How either maps onto the user's working odds is an
interpretive question routed to the expert-advisor at write-up, not decided here.

**Mechanism, not meaning (C2052).** A positive result says the text co-varies with what is drawn; it does not say what
any word means and does not recover a referent. No reading.

**Change control:** after the lock nothing below (populations, images, codebook, gate, text measures, covariates,
statistic, nulls, calibration, thresholds, controls, seeds, verdict rules) may change without a new phase number.

## Populations
- **Primary (V-A1):** herbal pages (section H) in Currier A by Davis hand 1, H track, P placement, labels excluded,
  uncertain tokens removed: **91 pages**, quires A–G (f1v–f56v as present) and O, Q (f87r, f87v, f93r, f93v, f96r,
  f96v). The four f90 foldout panels (f90r1–f90v2) are excluded before coding: the scan mapping has no panel-level
  image. Pages the locator flags as having no main plant are excluded before coding; the final list is
  `data/pages_v.json`. Davis hand assignments are contested; the population is fixed by list.
- **Descriptive arm (V-B2):** the 20 herbal pages in Currier B by Davis hand 2. S reported descriptively with its own
  nulls; no verdict. It lies inside the population of C137–C140 and is stated as unable to bear on them. (The v1 e-run
  sub-analysis is dropped: C2086 is a frame-controlled folio component and a per-page share at N = 20 cannot be read.)
- **Positive control (BR):** Brunschwig 1500 Part 2 entries whose heading ("Von … wasser.") is followed within five
  lines by the entry's woodcut (148 entries; `data/entries_br_all.json`). Entries under 41 words are excluded; reused
  woodcut blocks (duplicates by perceptual hash on the crops) keep one entry per block (seeded). The eligible list is
  `data/entries_br.json`.

## Images and locating (no coding)
- **V:** the full Beinecke scan, downscaled to 2,000 px on the long side. A locator agent outputs, per page, one polygon
  (≤ 16 vertices) around the main plant drawing, up to six rectangles over text lines that lie inside the polygon, a
  flag for "no main plant", and a count of comparable plants. Everything outside the polygon and inside the text
  rectangles is filled with mid-grey. Drawing height = the polygon's vertical extent / page height (computed, not coded).
- **BR:** the page image (pages per `data/entries_br_all.json`); a locator agent outputs one box per woodcut in reading
  order for each page with its expected woodcut count; the crop is the box. Woodcut height = box height / page height.
  Every crop is checked for printed text by both coder sets (`text_visible`); a crop flagged by either is re-cut and
  re-coded before the gate.
- Every image gets a fresh random code; no folio, page or plant name. V-A1 and V-B2 images are mixed in the V batches;
  BR images go to separate batches.

## Coding
- **Coder sets A and B**, each a group of agents (opus), each agent a batch of images (random subsets drawn
  independently for A and B; random order within batch). Set B receives a paraphrased codebook. Both are told: "code
  only what is visible in the drawing; ignore any writing or grey areas; do not use knowledge of what species it might
  be".
- **Context and blindness (declared).** The harness loads project context into subagents (CLAUDE.md, MEMORY.md, the
  git status, which names this phase). Coders may therefore know the project and the design. Coders are instructed to
  use only the Read tool on the listed images and the Write tool for one output file; every coder transcript is
  audited for other tool calls, and a batch with any other file access is discarded and re-coded by a fresh agent. With
  the text masked, coding error cannot depend on the text: it can only weaken the statistic.
- **Codebook (content), by organ.** Root: `root_form` (nominal: none_visible / single_taproot / few_branched (2–4 main
  roots) / many_branched_or_fibrous (5+) / swollen (bulb, tuber, thick rhizome)); `root_size` (ordinal: none / small
  (< 1/4 of plant height) / medium / large (> 1/2)). Stem: `stem_count` (ordinal: 1 / 2–3 / 4+). Leaf: `leaf_type`
  (nominal: simple_entire / simple_toothed_or_lobed / compound / grass_or_needle / none / mixed); `leaf_size` (ordinal:
  small / medium / large relative to the plant); `leaf_count` (ordinal: 0 / 1–5 / 6–15 / 16+). Flower: `flowers`
  (nominal: none / flowers / fruits_or_seed_heads / both); `flower_count` (ordinal: 0 / 1 / 2–5 / 6+); `flower_colour`
  (nominal, V only: none / blue / red_or_pink / yellow / white_or_unpainted / mixed). Habit: `habit` (nominal:
  upright_herb / sprawling_or_climbing / shrub_or_tree_like). Every feature allows `unclear`. (Dropped from v1:
  `root_present`, `symmetry`, `non_plant_element`.)
- **Codebook (style).** V: `fill` (ordinal: outline_only / partly_painted / fully_painted), `line_weight` (ordinal:
  thin / heavy). BR: `line_weight`, `shading` (nominal: none / hatching). Plus the computed drawing height. `pigments`
  (V) is coded and reported descriptively only (it overlaps `flower_colour`).
- **Also recorded:** `text_visible` (yes / no), `main_plant` (yes / no), `n_plants` (1 / 2+).

## Agreement gate (per corpus, before any text is consulted)
- Krippendorff's α between sets A and B per feature (nominal: 0/1 distance; ordinal: interval metric on ranks;
  `unclear` as missing).
- A feature enters if α ≥ 0.60 **and** ≥ 80% of the corpus's units are non-`unclear` in both sets.
- The corpus passes if the entered content features cover ≥ 3 of the 5 organs and number ≥ 4; otherwise CODING FAILED
  for that corpus.
- With same-model coder sets, α measures self-consistency, not validity; with the text masked the gate controls power,
  not false positives.

## Picture similarity
- Per coder set: for each organ, the mean over its entered features of the per-feature similarity (nominal: 1 if
  equal; ordinal: 1 − |Δrank| / (levels − 1)); the pair's content similarity is the mean over organs observed for both
  pages (nested features within an organ count once through the organ mean). A pair needs ≥ 3 organs observed for both
  pages, else it is excluded. C = the mean of the two sets' matrices. Style similarity Y likewise over entered style
  features plus 1 − |Δheight| for the computed drawing height.
- **Double-centring:** T, C and Y are double-centred (each page's mean similarity removed, over defined pairs) before
  the statistic; the raw version is reported descriptively.

## Text measures
- V: tokens per page as above; units = EVA glyph units (`c[tkpf]h|[cs]h|i+[nrlm]|.`). idf over V-A1 only (V-B2
  separately).
- BR: entry text after its heading line (`[WOODCUT …]` annotations, page markers and bracketed editorial notes removed),
  lower-cased, letters only, words of ≥ 2 letters; **primary: the first n words**, with n drawn from the V-A1 page-length
  distribution conditional on n ≤ the entry's length (seeded, per replicate); units = letters; idf recomputed on each
  sample.
- **T1 (word level):** cosine of tf–idf vectors over word types (tf = 1 + log count; idf = log(N / df)).
- **T2 (glyph-trigram level):** cosine of tf–idf vectors over within-word unit trigrams with word-boundary markers
  (C2092). A result outside on T2 only is reported as "glyph-trigram level" and never in word-level language.

## Covariates (pair level; they do not move with the pictures)
- **V-A1:** quire-pair fixed effects (9 quires, 45 categories); indicators for |Δpos| = 1, 2 and 3–4 and log(1 +
  |Δpos|), with pos = 2 × folio number + (0 recto, 1 verso), so physical gaps count (O and Q are ~30 folios after
  f56v); same leaf; same bifolium (conjugate leaves: in a quire beginning at folio a, leaf f pairs with 2a + 7 − f;
  quire O pairs f87–f90, quire Q f93–f96; f13 has no conjugate, f12 being lost); length (|Δ log n|, Σ log n);
  **layout** (|Δ| and Σ of tokens per line, line-edge share = (line starts + line ends + tokens next to a drawing break)
  / tokens, paragraph count; breaks counted on the ZL transliteration with PHASE_771's parser); **spelling dials** (|Δ|
  of the page shares of: e-runs of 2+ among tokens with an e-run; minim groups of 2+ among tokens with a minim group;
  k among k + t gallows; ch among ch + sh).
- **BR:** same letter chapter; the same |Δpos| terms on entry order; length.
- **Style:** Y (double-centred), entered as a covariate (it moves with the pictures).
- Computation: the fixed covariates are partialled out once (Frisch–Waugh); per permutation only C and Y are
  re-residualised.

## The statistic
For each measure m ∈ {T1, T2}: **S_m = the partial correlation (Pearson) of the double-centred text similarity and the
double-centred content similarity over the defined pairs, given the fixed covariates and Y.** Descriptive companions:
S without Y; S on raw (not double-centred) matrices; a Spearman (rank) partial S; S with T computed on line-interior
tokens only (line-initial, line-final and break-adjacent tokens removed); S without the pages flagged as having two
comparable plants.

## Nulls
- **N-local:** exact permutation of the picture records (content and style together) within fixed blocks of two
  consecutive leaves (up to 4 pages) aligned to quire boundaries (block = (quire, ⌊(leaf − first leaf of quire) / 2⌋);
  offset 0); BR: blocks of 4 consecutive entries within a letter chapter. 10,000 permutations; z_local and the exact
  p_local. It holds size for any confound at a scale of ≥ 4 pages (w0 = one leaf pair).
- **N-shift:** circular shift of the picture records along binding (V) or entry (BR) order, k = 3 … N − 3; z_shift.
  The rank among the shifts is descriptive only (≈ N − 5 strongly autocorrelated values).
- **N-sheet** (permutation within bifolium) is added to the decision only if the misbinding variant of K2 shows a
  false-positive rate > 0.01 under N-local; decided on controls before the lock.
- Per measure, Z_m = min(z_local, z_shift [, z_sheet]). **Outside on m** if Z_m > z* (calibrated below).

## Calibration (pre-lock; the Voynich alignment at k = 0 is never computed before the lock)
- **K1 — drift, a family of four generators** of synthetic picture records for the 91 V-A1 pages (organ-tuple states,
  so the joint structure within an organ is kept; set-B records perturbed from set-A records at the observed per-feature
  disagreement rates):
  (i) stationary Markov in binding order (stay with the observed lag-1 agreement, else draw from the global marginal);
  (ii) quire steps: quire-specific marginals (estimated leaving out the target page's leaf and its conjugate) with a
  within-quire Markov chain; (iii) a smooth trend (tuple log-weights following a smoothed random walk along the order);
  (iv) shared drift: tuple probabilities ∝ marginal × exp(γ · a_t · s̃_i), where s̃ is the first eigenvector of the
  double-centred T (a text-only page score; no alignment) smoothed along the order with a Gaussian of width w = 8, 16 or
  32 pages, a_t fixed random tuple loadings, and γ set by bisection so the generated lag-1 agreement matches the real
  one (picture-only).
  **Fidelity gate (picture-only):** for each entered content feature, the mean lag-1-to-10 agreement and the
  between-quire variance of the modal-value frequency; a generator passes if at most 2 of these checks fall outside the
  central 90% of its replicates. **Leak control:** no generator copies a real record to its own position (all are
  parametric; (ii) excludes the target's leaf and bifolium from its quire marginal).
- **K2 — writing sessions, anchored.** Anchors measured without any alignment: the text-only adjacency excess (mean
  double-centred T at |Δpos| ≤ 4 minus at |Δpos| > 20, after the length covariates) and the picture-only adjacency
  excess (the same on C). Generator: the real V-A1 tokens are redistributed across pages at random (page lengths kept;
  all page-level text structure destroyed); latent sessions are (contiguous) runs of 4–12 consecutive pages or
  (misbinding) random groups of bifolia; each session plants a session-specific set of mid-frequency V-A1 types into
  its pages at rate r, and draws its pages' picture records from a session-specific perturbation of the marginal with
  concentration κ; r and κ are set by bisection so the generated text and picture adjacency excesses equal the real
  anchors (attributing all observed adjacency to shared sessions: conservative). No content–text link except through
  sessions. Settings: anchored and 2 × anchored (the latter descriptive).
- **z\*:** per replicate, Z_rep = max over m of Z_m; z\* = the 99th percentile of Z_rep, maximised over the passing
  K1 generators (and widths) and the anchored K2 variants; ≥ 500 replicates per setting and ≥ 2,000 at the binding
  setting (or the upper 90% bound of the quantile if fewer). The same permutation counts as in the real run.
  **Fallback:** if no K1 generator passes its fidelity gate, the decision is p_local ≤ 0.005 on at least one measure
  (exact N-local), labelled so.
- **K3 — power (plants; outcomes of planted replicates only are stored; the unplanted S(k) is never printed).** The
  real V-A1 texts with the real picture records under a random shift k ∈ [10, N − 10]. For each entered content
  feature, each value gets two descriptor types (random mid-frequency V-A1 types, disjoint across values), inserted by
  replacing r random tokens per page on pages with that value; plants keyed on set A's codes with C computed from set
  B, and the reverse (MDE80 is the larger of the two). Variants: exact; spelled (a family of three spellings differing
  in one unit, chosen per insertion); single-organ (leaf descriptors only). Grid r = 0.5, 1, 2, 4 per feature; 200
  replicates per point; idf recomputed after planting. MDE80 = the smallest r at which ≥ 80% of replicates are
  outside.
- **K4 — genre control (Brunschwig).** BR's own z\*_BR from K1 (i)–(ii) run on BR (same fidelity gate). Features: those
  entered in both corpora; BR codes degraded per feature to V's α by random replacement from the feature's marginal
  until α_BR ≈ α_V (seeded). 200 replicates: a random 95 eligible entries, a fresh length draw. **Genre power** = the
  fraction of replicates outside at max(z\*, z\*_BR), with a Wilson 95% interval (optimistic: the replicates overlap).
  Ablation rows, each with its own genre power: (i) uses only (the text from the first virtue paragraph mark onward;
  names and description removed); (ii) n/2 words; (iii) the BR text rewritten as a word code in V-A1's forms (word
  types mapped by frequency rank onto V-A1 types, k = 1 and k = 4 interchangeable spellings, synthetic forms beyond
  V-A1's inventory spliced from V-A1 glyph units); (iv) a random window of n words instead of the first n; (v) the
  entry's own name stems masked.

## Verdicts (V-A1; applied in this order)
1. **CODING FAILED** — the V-A1 coding fails the gate. No test.
2. **CO-VARIES WITH CODED DRAWN CONTENT** — outside on T1 or T2. (Outside only without the style partial does not
   count: the verdict is then NOT DETECTED and "style-linked" appears in the text only.)
3. **NOT DETECTED (genre-powered)** — not outside, and the main genre power ≥ 0.85 (BR CODING not FAILED).
4. **NOT DETECTED (unpowered)** — otherwise. A label: genre power and MDE80 reported, no "no link" wording.
- Per-feature breakdowns are uncorrected and never registrable. V-B2 is descriptive.

## Registry (one Tier-2 row; templates)
- CO-VARIES: "Hand-1 herbal text co-varies with the coded content of its plant drawings beyond page position (w0 = one
  leaf pair), quire, bifolium, layout, spelling dials, drawing style and length ([T1 word | T2 glyph-trigram] level;
  S {s}, z_local {z1}, z_shift {z2}, z\* {z}); the test cannot distinguish reference from a writer's picture-keyed
  habits outside these covariates; no referent recovered (C171, Tier 3)." Human sign-off on the row wording is
  requested before registration (the first positive external-channel result). Scope notes on C137/C138/C140: "a
  different population (Currier A, hand 1) and layer (page vocabulary / glyph trigrams vs B grammar profiles); not the
  same claim; no tier change", and on C2058, C2084, C171.
- NOT DETECTED (genre-powered): "Hand-1 herbal text does not co-vary with the coded content of its plant drawings at
  the strength of a form-describing printed herbal (Brunschwig 1500), at V's N and page lengths, on the features
  entered in both corpora at V's coding reliability, at one Brunschwig word per V token (genre power {g}; ablation rows
  reaching 0.85: {list}). A herbal giving names and uses without describing form is not covered unless the uses-only
  row reaches 0.85." Scope notes on C2058 and C2084; on C140: "no extension of this row to Currier A text".
- NOT DETECTED (unpowered) and CODING FAILED: the row records the result, genre power and MDE80; no notes.
- No tier changes; no Tier-0 change.

## Declared prior knowledge and exposure
- C137 / C138 / C140 (Tier 1, scope B): swap invariance p = 1.0; "visual similarity does not predict constraint
  similarity at any level" (ILL); ILL-TOP-1 (8/8 failed); PPC (all p ≫ 0.05). Any later confirmatory test on Currier B
  must first read the ILL source to see whether its "constraint similarity" included vocabulary.
- VIS (30 herbal folios, human and Claude coding, not blind to text; no signal); its codes are not used.
- C2058 (o-HEAD rate vs plant complexity, N = 29, null); C2084 (13 pairs, null).
- Text-derived page features computed before the lock: page lengths (for the Brunschwig truncation draw and the
  covariates), layout and dial shares (covariates), the double-centred T's first eigenvector (K1 iv), and the text-only
  adjacency excess (K2 anchor). None involves the pictures.
- I (the orchestrator) have not computed any text–picture association on V and do not view the Voynich page images
  (the locator and coders do); I view Brunschwig crops to check them.

## Procedure
1. v2 → (this document) → build page and entry lists, locate (V polygons, BR boxes), mask and crop, anonymise; commit.
2. Coding by sets A and B; transcript audit; text-flag re-cuts; agreement gate per corpus; commit codes.
3. K1–K4; z\*, MDE80, genre power and ablation rows filled in here; lean-expert confirmation pass; checksums; tag
   `phase780-lock`.
4. Locked run on V-A1 (V-B2 descriptive); lean-expert results check; expert-advisor on the interpretive mapping;
   write-up; registry (with human sign-off if CO-VARIES); bookkeeping.

## Caveats
- Coders are the same model; α is self-consistency. A human check of 20–30 V pages is offered to the user (non-gating).
- Binding order is not writing order; N-local covers structure at ≥ 4 pages, K2's misbinding variant the non-contiguous
  sessions.
- V drawings are stylised and hand-coloured; BR woodcuts are naturalistic and uncoloured; the reliability degradation
  and shared-feature rule match them only on what is coded.
- Position-resolved features (text near roots vs flowers) are not tested.

## Amendments made before any coding (implementation; none uses a code or a text–picture value)
1. **Colour in both corpora.** The Brunschwig copy scanned is hand-coloured (seen on a locator check crop), so
   `flower_colour` and `fill` are coded and may enter in both corpora; `pigments` stays descriptive in both;
   `shading` stays Brunschwig-only.
2. **Undefined pairs.** A pair whose pages share fewer than 3 observed organs takes the neutral value 0 after
   double-centring (instead of being dropped), so the pair set is fixed under permutation.
3. **Line-interior sensitivity.** The H track carries no drawing-break markup; the variant removes line-initial and
   line-final tokens only (break counts for the layout covariate come from ZL).
4. **V-B2** uses V-A1's entered features (its own α at N = 20 is not interpretable).
5. **Fidelity allowance.** A K1 generator passes if the number of checks outside the central 90% is at most the 95th
   percentile of Binomial(n_checks, 0.10) (4 for 16–20 checks): v2's fixed "2" was set for fewer checks and would fail
   a correct generator about a third of the time.
6. **K2** recomputes the spelling-dial covariates on the redistributed text (layout covariates stay the real page
   values).
7. **K4 details.** z\*_BR is calibrated on random 95-entry subsets (K1 i–ii with letter chapters as quires); the
   uses-only text starts at the first "A" virtue mark (regex `(^|[\s.])A\s+[A-ZÄÖÜ]` on the raw entry), entries
   without one or under 41 words after it are not eligible for that row; name stems = the first five letters of the
   heading's words outside a stop list (von, wasser, krut, blumen, …).
8. The locators' free-text notes are kept in `data/geometry.json` and are not used.
9. **Non-plant woodcuts.** Brunschwig entries whose woodcut both coder sets mark `main_plant: no` (e.g. birds,
   beehives) are excluded before the gate; entries whose woodcut could not be located are excluded.
10. **Text flags on Brunschwig crops (after coding, before the gate).** Six crops were flagged `text_visible` by at
    least one set. Inspected by eye: four show faint mirror-image bleed-through from the other side of the leaf inside
    the woodcut frame, one a small cutter's mark carved in the block, one nothing legible. None shows the entry's own
    printed text or a name, and none can be re-cut without cutting the drawing. They are kept as coded (the v2 rule
    "re-cut and re-code" presumed removable printed text). On the Voynich side, coders report residual writing inside
    most masked outlines (166 of 182 codings), where text runs between stalks; it is unreadable to the coders and is
    declared, not removed.
11. **Code files** are copied into `data/codes/` (the loaders read them there) so the coded data are in the repository;
    the coder transcripts were audited: 16 of 16 batches used only Read on their own batch file, codebook and images
    and Write on their own output (`results/coder_audit780.json`).

## Changes from v1 (design audit)
N-block replaced by N-local (exact, 10,000 permutations) and AND with N-shift (A1a); K1 a family of four generators with
a picture-only fidelity gate and a fallback (A1b); parametric, leak-free generation (A1c); K2 anchored to measured
adjacency excesses and included in z\* (A1d); a single z\* from the max-over-measures, min-over-nulls statistic (A1e);
quire-pair fixed effects, distance indicators, bifolium and physical positions (A1f); layout and spelling-dial
covariates, line-interior sensitivity, double-centring (A2); drawing masks, harness disclosure and transcript audit,
coverage floor, organ-level similarity, Gower floor, style without pigments, mixed V batches (A3); Brunschwig matched
(reused blocks, shared features, α degradation, own size, first-n truncation, ablations) and the genre-power statement
(A4); T2-only wording, idf populations (A5); verdict renamed, style-only rule, per-feature rule, label wording, C137–C140
wording, the asymmetry statement (A6); non-blocking B1, B4–B12 adopted (B2 sparse statistic not adopted; B3 offered to
the user; genre threshold 0.85 per B9); drops per C.

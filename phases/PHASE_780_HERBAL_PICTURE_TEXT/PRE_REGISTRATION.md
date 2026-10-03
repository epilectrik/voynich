# PHASE_780 — Does the herbal text track its drawings? A blind picture test within one hand, with an illustrated herbal as positive control (pre-registration)

**Status: DRAFT v1, for the lean-expert design audit. Nothing below has been computed. No image has been coded. No
text-similarity statistic has been computed on any Voynich page pair.**

**Origin.** STATUS_BRIEF and RESEARCH_AGENDA item 8 ("pictures and text, powered"): the earlier picture tests had
n ≈ 30 and little power (VIS, ILL-TOP-1); the first powered test found no signal for one narrow design (C2084, label
recurrence, 13 pairs). The agenda's next step is a blind picture-coding test within one section and hand that does not
assume a label is a word of the text, and that tests writing-session drift and copying as rival sources. This phase
is that test for the herbal section. Content claims need an external channel (C171 referent ceiling; C2052 matcher
genericity); the drawings are external to the text.

**Question.** On the herbal pages written by one hand (Currier A, Davis hand 1), do pages whose plant drawings are
similar carry similar text, beyond what page position, quire, drawing style and text length predict? The same
statistic is run on an illustrated herbal whose text certainly refers to its pictures (Brunschwig, *Liber de arte
distillandi de simplicibus*, Strasbourg 1500, Part 2, one woodcut per plant entry), cut to the Voynich page lengths:
it says whether this test could see a real herbal's text–picture link at this size.

**Mechanism, not meaning (C2052).** A positive result says the text co-varies with what is drawn; it does not say
what any word means, and it does not recover a referent. A negative result says the text does not co-vary with the
drawings at the strength a real illustrated herbal shows; it does not say the text is meaningless (a recipe notation
need not describe the plant beside it). No reading.

**Change control:** after the lock nothing below (populations, codebook, agreement gate, text measures, statistic,
nulls, thresholds, controls, seeds, verdict rules) may change without a new phase number.

## Populations
- **Primary (V-A1):** herbal pages (section H) in Currier A by Davis hand 1: 95 pages, quires A–G (85 pages, f1v–f56v
  as present) and O, Q (f87r, f87v, the four panels f90r1–f90v2 of the f90 foldout, f93r, f93v, f96r, f96v); the list
  is fixed in `data/pages_v.json` before coding. H track, P placement, labels excluded, uncertain tokens removed;
  41–152 tokens per page (mean 83).
- **Descriptive arm (V-B2):** herbal pages in Currier B by Davis hand 2: 20 pages. No verdict; reported descriptively
  with its own nulls. The folio-level e-run setting of C2086 is a Currier B measurement; on this arm the per-page
  share of e-runs of 2+ among e-run tokens is reported against picture similarity, descriptively, with the caveat
  that N = 20 has little power.
- **Positive control (BR):** Brunschwig 1500 Part 2 entries headed "Von … wasser." with a woodcut on the same or the
  facing page (`sources/brunschwig_1500/brunschwig_1500_corrected.txt`, early modern German; page images
  `sources/brunschwig_1500/pages/`). Entries whose woodcut cannot be located are dropped before coding; the list is
  fixed in `data/entries_br.json`.

## Picture coding (blind)
- **Images.** V: the full page scan (Beinecke IIIF, `sources/voynich_scans/`), downscaled to 2,000 px on the long
  side. BR: the woodcut alone, cropped by a locator agent that outputs bounding boxes only (no coding), checked by me on
  a sample of 10 for absence of printed text; crops containing text are re-cut. Every image is renamed with a random
  code (no folio, page or plant name), and the order is randomised.
- **Coders.** Two independent coder sets, A and B; each set is a group of agents (opus) given the codebook below and
  a batch of images; batches are random subsets, drawn independently for A and B, with random order within batch.
  Coders are told only: "code the main plant drawing on each image with this codebook; ignore any writing". They are
  not told the source of the comparison, the hypothesis, that text will be compared, or which manuscript a batch
  comes from (V and BR images go to separate batches; the corpora are recognisable, which is accepted). Coders have no
  access to the transcript, the project context files or the other set's output.
- **Codebook (content: what plant is drawn).**
  - `root_present`: yes / no / unclear.
  - `root_form` (nominal): none_visible / single_taproot / few_branched (2–4 main roots) / many_branched_or_fibrous
    (5+) / swollen (bulb, tuber, thick rhizome) / unclear.
  - `root_size` (ordinal): small (< 1/4 of plant height) / medium / large (> 1/2) / unclear; `none` if no root.
  - `stem_count` (ordinal): 1 / 2–3 / 4+ / unclear (main stems from the base).
  - `leaf_type` (nominal): simple_entire / simple_toothed_or_lobed / compound (leaflets on a shared stalk) /
    grass_or_needle / none / mixed / unclear.
  - `leaf_size` (ordinal): small / medium / large relative to the plant / unclear.
  - `leaf_count` (ordinal): 0 / 1–5 / 6–15 / 16+ / unclear.
  - `flowers` (nominal): none / flowers / fruits_or_seed_heads / both / unclear.
  - `flower_count` (ordinal): 0 / 1 / 2–5 / 6+ / unclear.
  - `flower_colour` (nominal; V only, BR is uncoloured): none / blue / red_or_pink / yellow / white_or_unpainted /
    mixed / unclear.
  - `habit` (nominal): upright_herb / sprawling_or_climbing / shrub_or_tree_like / unclear.
  - `symmetry` (nominal): symmetric / asymmetric / unclear.
  - `non_plant_element` (nominal): none / animal_or_human / object / unclear.
- **Codebook (style: how it is drawn).**
  - `pigments` (set; V only): any of green, blue, red_brown, yellow, other; `unclear`.
  - `fill` (ordinal): outline_only / partly_painted / fully_painted / unclear (V only).
  - `drawing_height` (ordinal): < 1/3 / 1/3–2/3 / > 2/3 of the image height / unclear.
  - `line_weight` (ordinal): thin / heavy / unclear.
  - `shading` (nominal; BR only): none / hatching / unclear.
- **Agreement gate (per corpus, before any text is consulted).** For each feature, Krippendorff's α between coder
  sets A and B (nominal or ordinal as declared; `unclear` as missing; sets by Jaccard distance). A feature enters the
  corpus's similarity if α ≥ 0.60. The corpus coding passes if ≥ 5 content features enter; otherwise CODING FAILED for
  that corpus and no test is run on it.
- **Similarity.** For pages i, j and coder set c: Gower similarity over the entered content features observed for
  both pages (nominal: 1 if equal; ordinal: 1 − |a − b| / (levels − 1); sets: Jaccard), averaged over coder sets:
  C_ij. Style similarity Y_ij likewise over entered style features (Y_ij = 0 for all pairs if no style feature
  enters).

## Text measures (computed identically on V and BR)
- V: tokens per page as above; units = EVA glyph units (`c[tkpf]h|[cs]h|i+[nrlm]|.`, as in PHASE_778/779).
  BR: the entry text after its heading line, `[WOODCUT …]` annotations and page markers removed, lower-cased, letters
  only, single-letter paragraph marks removed; each entry truncated to a length drawn from the V-A1 page-length
  distribution (one draw per entry per replicate, seeded); units = letters.
- **T1 (word level):** cosine similarity of tf–idf vectors over word types (tf = 1 + log count; idf = log(N / df)
  over the corpus's N pages).
- **T2 (spelling-robust):** cosine similarity of tf–idf vectors over within-word unit trigrams with word-boundary
  markers (C2092: interchangeable spellings defeat word-level repeat statistics).

## The statistic
For every pair i < j, with covariates X_ij: Y_ij (style similarity); same quire (V) or same letter chapter (BR); same
leaf (recto and verso of one folio, V only); log(1 + |position_i − position_j|) in binding order (V) or entry order
(BR); |log n_i − log n_j|; log n_i + log n_j. Residualise T_ij and C_ij on X_ij by ordinary least squares; **S = the
Pearson correlation of the two residual vectors** (the partial correlation of text and content similarity given X),
computed separately for T1 and T2. One-sided: only positive S counts.

## Nulls
- **N-shift:** the picture records (content and style codes together) are shifted circularly along the order by k,
  k = 3 … N − 3; S recomputed with X recomputed (Y moves with the pictures). z_shift and the rank of S among the
  shifted values. Preserves each sequence's autocorrelation in order.
- **N-block:** the picture records are permuted among pages within quire (V) or letter chapter (BR), 2,000
  permutations; z_block and p.
- **Outside** for measure m: S_m beyond the calibrated critical value z*_m under both nulls (below). The critical
  values come from control K1 (drift) and K2 (session) so that the family-wise false-positive rate over T1 and T2
  is ≤ 0.01.

## Controls and calibration (pre-lock; no Voynich text–picture alignment is ever computed at k = 0 before the lock)
- **K1 — drift.** The real V-A1 texts paired with synthetic picture records: per feature a Markov chain in binding
  order fitted to the coded records (marginals and lag-1 agreement; joint structure kept by resampling whole records
  within a sliding window). 1,000 replicates. Sets z*_m so that the family-wise FP over T1, T2 is ≤ 0.01 under both
  nulls.
- **K2 — writing session.** Latent sessions (runs of 4–12 consecutive pages; and a misbinding variant with sessions
  spread over random bifolia) shift both the content and the style code distributions (records resampled within a
  session-specific subset of the coded records) and plant session words into the text (r = 1, 2, 4 tokens per page
  from a session-specific set of mid-frequency types). No content–text link except through sessions. 500 replicates
  per setting. Reported: the FP rate of the full procedure (with the style partial). If FP > 0.01 at a setting, the
  verdict text carries "a session confound of that strength is not excluded".
- **K3 — power (plants).** The real V-A1 texts with the real picture records under a random shift k ∈ [10, N − 10]
  (which removes any true link); descriptor words planted: for each entered content feature, each value gets two
  descriptor types (random mid-frequency types, disjoint across values), inserted by replacing r random tokens per
  page on pages with that value. Exact variant (the same types) and spelled variant (each descriptor a family of
  three spellings differing in one unit, chosen at random per insertion). Grid r = 0.25, 0.5, 1, 2, 4 per feature.
  200 replicates per point. MDE80 = the smallest r at which ≥ 80% of replicates are outside (both nulls, z*).
- **K4 — genre control (Brunschwig).** The BR statistic on 200 replicates (a random 95 of the eligible entries, a
  fresh length draw), with the BR nulls and the same z*. **Genre power** = the fraction of replicates outside on at
  least one measure. Also reported: the BR S per measure (mean, sd).
- **Exposure accepted:** K3 computes S on the real texts and real picture records at non-zero shifts, i.e. values of
  the N-shift null; S at k = 0 is never computed before the lock.

## Verdicts (V-A1; applied in this order)
1. **CODING FAILED** — the V-A1 coding fails the agreement gate. No test.
2. **TEXT TRACKS DRAWN CONTENT** — outside on T1 or T2 (both nulls, z*).
3. **NOT DETECTED (genre-powered)** — not outside, and genre power ≥ 0.80 (a real illustrated herbal's text–picture
   link of Brunschwig's strength would have been detected at this size).
4. **NOT DETECTED (unpowered)** — not outside, genre power < 0.80, or BR CODING FAILED.
- Descriptive: S without the style partial (if a link appears only without it: "style-linked"); per-feature
  breakdowns; V-B2; the MDE80 from K3; the K2 FP table.

## Registry (one Tier-2 row; templates)
- TRACKS: "[Hand-1 herbal text co-varies with the drawn plant's coded content beyond page position, quire, style and
  length (PHASE_780; S {s}, z_shift {z1}, z_block {z2}). Not a reading; no referent recovered. Session confound
  check: {K2}.]" Scope notes on C137/C140 (Tier 1, B grammar: "a different layer (A vocabulary); not a contradiction
  of this row's scope"), C2058, C2084, C171 (a text–picture covariation, not a referent).
- NOT DETECTED (genre-powered): "Hand-1 herbal text does not co-vary with the drawn plant's coded content at the
  strength the Brunschwig 1500 herbal shows (genre power {g}); a notation need not describe its pictures." Scope notes
  on C2058, C2084.
- NOT DETECTED (unpowered) and CODING FAILED: the row records the result and the power; no notes.
- No tier changes; no Tier-0 change.

## Declared prior knowledge and exposure
- C137 / C138 / C140 (Tier 1, scope B): swap invariance p = 1.0; "visual similarity does not predict constraint
  similarity at any level" (ILL); ILL-TOP-1 (8/8 failed); PPC (program vs plant morphology, all p ≫ 0.05). All on
  Currier B grammar profiles.
- VIS (n = 30 herbal folios, coded by a human and Claude together, not blind to text; prefix–feature Cramér's V; no
  signal). Some of those folios are in V-A1; their codes are not used.
- C2058 (A o-HEAD rate vs plant complexity, N = 29, null); C2084 (fragment labels vs herbal pages, 13 pairs, null).
- I (the orchestrator) have not computed any text similarity between herbal pages, have not viewed the herbal page
  images in this phase, and know published plant identifications only from general literature.

## Procedure
1. This draft → lean-expert design audit → edits.
2. Build the image sets and page/entry lists; BR woodcut location and crops; commit lists and scripts.
3. Coding by the two coder sets; agreement gate per corpus; commit codes.
4. Controls K1–K4; z*, MDE80, genre power filled in here; confirmation pass; checksums; tag `phase780-lock`.
5. Locked run on V-A1 (and V-B2, descriptive); results check; write-up; registry; bookkeeping.

## Caveats
- Coders are the same model; agreement between them is not independent of shared model biases. A human check of a
  sample of codes is offered to the user and does not gate the test.
- V coders see full pages (the drawing is interleaved with text); BR coders see woodcut crops. V drawings are stylised;
  BR woodcuts are naturalistic, so coding noise may differ between corpora (reported through α).
- Binding order is not writing order (the herbal quires were rebound); the N-shift null preserves binding-order
  autocorrelation only, and K2's misbinding variant is the check on non-contiguous sessions.
- Position-resolved features (text near roots vs near flowers) are not tested here.

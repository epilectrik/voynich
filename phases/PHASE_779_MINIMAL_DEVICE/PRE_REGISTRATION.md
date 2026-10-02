# PHASE_779 — The minimal device: a sampler of page × line-type composition, line-position vocabulary and two-unit junction routing; which of Currier B's other registered regularities is it not outside? (pre-registration)

**Status: DRAFT v2 after the lean-expert design audit (NOT LOCKABLE as v1; all 38 edits incorporated). Pending before
the lock: the fidelity gate and plant results below, and the confirmation pass.** No counted prediction statistic
has been computed on Currier B (see Exposure for the three disclosed exceptions). The device has one pre-lock
choice, the routing smoothing κ, made on D2 alone.

**Origin.** PHASE_774–778 reduced B's measurable sequence to its word-boundary rules and page × line-type
composition (C2091, C2093, C2094; the nulls of C2093–C2095 are keyed by folio × line type) and excluded the two
published content-free production methods (C2077; C2096 as described). What remains is a specification any method
must meet: a page × line-type word stock, line-position vocabulary (D6, C956), and junction routing (C2082,
C1212/C1563). This phase asks how much of what the registry records beyond those rules is reproduced by a sampler of
them, and how much is an extra layer. It can only reproduce statistics from B-fitted tables; it does not recover a
method. STATUS_BRIEF §4; RESEARCH_AGENDA Tier B.

**Question.** Take the simplest sampler of the three rules, MIN-D. On the registered regularities below, none of
which it is given, is B inside or outside its ensemble? The answer is a layer map, with each verdict powered by a
plant or marked unpowered.

**Mechanism, not meaning (C2052).** MIN-D is a sampler of measured rules, not a production method; nothing here
bears on C2077/C2096, on vocabulary or on how page stocks arose. Not being outside the sampler is not evidence that B
was produced this way. No reading.

**Change control:** after the lock nothing below (device, rungs, κ, statistics, criterion, N, seeds, plants) may
change without a new phase number. Redefinitions since v1 follow the design audit and its named flaws (selection on
the outcome, layer mismatch, sample-size form, built-in line type, double-counted marginal, position lookup for rare
words), not member values.

## The device (`scripts/mind779.py`)
- **Stock.** Tokens drawn without replacement from the page × line-type multiset (paragraph-first lines and body
  lines separately), so every generated cell has exactly B's composition for that cell: the cells of C2093–C2095.
  Lower rung R2P: page-only stocks. Sensitivity R2Lw: with replacement from the cell's frequencies (depletion only;
  composition statistics P2 and P10 and the descriptives are not read on it).
- **Zone.** Candidate weight × P_s(z | w), z ∈ {line-initial, medial, line-final}: per-word for words with n ≥ 5
  (`NMIN_ZONE`), otherwise P_s(z | first unit, last unit), otherwise P(z); every table smoothed toward P(z) with
  pseudo-count κ_z = 1. The variant R2Lmemo uses per-word tables for every word (a position lookup for rare words:
  about two thirds of B's types are hapaxes, and under additive smoothing a hapax seen line-initially would get a
  5.7× initial lift); it carries rare words' B positions and is read descriptively.
- **Routing.** Candidate weight × P_s(u(w) | e_prev) / P(u(w)): the within-line junction population only (D2's
  pairs); u = the next word's first glyph unit, e_prev = the previous word's last two units (R2), its last unit (R2a),
  or u = the first two units (R3); P_s smoothed toward P(u) with pseudo-count κ; divided by the first-unit marginal so
  that the stock count does not count the marginal twice. Line-initial slots receive zone weights only.
- Weight = n_rem(w) × zone × routing; if every weight is zero, the stock count alone. No paragraph state, no line
  memory, no interior rule, no repeat rule.
- **Ladder (page × line-type stocks, without replacement):** R0L (stock only: a within-cell shuffle) → R1L (+ zone)
  → R2aL (+ one-unit routing) → **R2L (+ two-unit routing; the primary)** → R3L (+ two-to-two routing). Fixed in
  advance: prediction verdicts are registered on R2L; MIN-D (the lowest rung passing the panel) is descriptive.
- **Header extension R2L+H** (descriptive; B-fitted line-type tables; exposure-carrying): in a line of type t a
  word's zone weight is multiplied by P_B(z | first unit, t) / P_B(z | first unit) × P_B(z | last unit, t) / P_B(z |
  last unit) and by the header propensity P_B(header | first unit) × P_B(header | last unit) / P_B(header) (clipped to
  1) for paragraph-first lines and its complement for body lines. Not a power control.
- Variants: R0L, R1L, R2aL, R2L, R3L, R2P, R2Lmemo, R2Lw, R2L+H; N = 1,000 members each (seed 779,000,000 +
  10,000·variant + member); a second seed block (779,500,000 + …) of 1,000 for R2L and R0L gives the pooled N = 2,000
  used for the discrete statistic. Skeleton: 2,299 lines, 21,610 certain tokens, 80 folios, 457 paragraph-first lines.

## Fidelity gate (pre-lock; generated members; B's D2 and D6 are the PHASE_778 certification values, already exposed)
- κ ∈ {0.5, 2, 8}, 200 members of R2L each; **κ is selected on D2 alone** (smallest |z_B| on D2). The primary rung
  must not be outside on D2 under the PHASE_757 rule; R2Lmemo must not be outside on D6. Reported descriptively:
  the generated raw MI(previous last two units; next first unit), and the raw edge MI on the first and second half of
  each page's lines (a depletion diagnostic); R2Lw, R2P alongside.
- If the primary fails on D2 after the κ grid, the declared fallback is a within-cell Metropolis sampler targeting
  the same weights with composition exact and mixing diagnostics; every sampler tried is listed. Nothing on D3–D5 or
  the predictions may inform these choices.
- **Result:** *to be inserted (`results/fidelity779.json`).*

## Step 1 — the panel (PHASE_757's D2–D6, unchanged; B's values recomputed in the run)
D2 is a fidelity statistic on every routing rung (an input marginal), D6 a fidelity statistic on R2Lmemo and a
descriptive on the back-off primary; **the panel tests are D3, D4 and D5.** Outside = beyond the ensemble [min, max]
and |z| > z\* = Φ⁻¹(1 − 0.005/5) = 3.09; B on the boundary is inside. A rung passes if B is outside on none of
D3–D5. If the primary does not pass: "INCOMPLETE relative to the PHASE_779 sampler: B is outside on {D}. The sampler
generates the edge sequence from first-order routing, whereas the exact nulls of C2093–C2094 fix B's edge sequence;
this does not contradict C2093/C2094." Predictions are read on the primary regardless.

## Step 2 — the predictions (fixed now)
Computed identically on B and on every member. Continuous statistics: B is outside a variant if beyond [min, max]
and |z| > z\* = Φ⁻¹(1 − 0.005/8) = 3.29; boundary counts as inside. Discrete statistic (P6z): the pooled N = 2,000
ensemble; outside = strictly beyond every member; ties inside; z reported, not used.

| | Counted statistic | Registered relatives | Encoded? |
|---|---|---|---|
| P1u | Line homogeneity at the glyph-unit level: mean within-line glyph-unit entropy, percent reduction against 20 within-page shuffles of the member | C1214 (an atom-level measurement; not the identical statistic); the C2095 F1/F2 descriptives | no (no line memory) |
| P2 | Paragraph PREFIX composition: mean within-folio between-paragraph PREFIX JSD, body lines only, paragraphs with ≥ 10 body tokens, pairs weighted equally within a folio and folios equally | C1811, C1812 (their "within 1.37× between" has an unequal-size form and is not an effect size here) | no (no paragraph state) |
| P6z | Pair zeros in C2081's form: among ordered pairs of common tokens (n ≥ 10) whose expected count under the primary ensemble is ≥ 3, the number of pairs B never writes, against the members' zero counts on the same cells | C2081 (live); not C957 (superseded; its nine bigrams are selected on the outcome and are a descriptive only) | no (routing is glyph-level) |
| P7 | e-run lag-1 agreement: share of within-line adjacent pairs whose e-run classes (longest e-run in glyph units: 0, 1, 2+) agree | PHASE_757's descriptive 0.455 if identical; C2077 K4, C1994 | no (interior) |
| P8 | qo / ch-sh alternation per C549: strictly adjacent within-line pairs where both words start with qo (first two EVA glyphs) or with the bench unit ch/sh (benched gallows excluded); the share that alternate | C549 (56.3% vs 50.6%), C2056 | partly, through routing |
| P10 | Hapax dispersion: body lines only, hapaxes defined on the skeleton; the within-folio dispersion index Σ_l (c_l − n_l p_f)² / (n_l p_f) over (lines − folios) | — | no |
| P11 | e-run medial position gradient: medial positions only (first and last token excluded), lines of ≥ 6 tokens, quintiles of relative medial position; JSD between the quintile distribution of tokens with an e-run of 2+ and that of all tokens | C1671, C1566 | no (the three zones are excluded) |
| P12 | The C2056 lane: among within-line pairs starting with a qok-initial token, the share whose next token is ok-initial rather than ot- or ol-initial | C2056 | no on R2 (routes the first unit only); an input on R3 |

**Consistency statistics and descriptives (not counted, no scope notes):** P1t (token-level line homogeneity, overlaps
D3); P3 (last-unit m at line ends, paragraph-first minus body lines; C1435 counts m-terminal MIDDLEs and C1439 says
those are orthogonal to the -am suffix: not the same statistic); line-type contrasts P4 (gallows-initial first words,
paragraph-first minus other lines; C864, C841) and P5 (p/f/cph/cfh share, paragraph-first minus body), which are about
zero on page-only stocks by construction and inputs on line-type stocks; the nine C957 bigrams' count ("B = 0 by
selection; not read"); P9 the corpus maximum of qok-initial tokens in a 10-token window and the maximum identical run
(corpus-level values only; "not an anchor re-pricing: the anchor is a joint conjunction (C1889, PHASE_741); any
re-pricing must use the joint and goes to the human"); the class-pair MI (C2094's statistic) on members; repeated
5-windows (C2091, B 0); duplicate lines (B 0).

## Power and the three-way rule (plants on the primary; generated members only; `results/plants779.json`)
Each counted prediction has a plant: a weight multiplier on R2L with a declared grid, 200 members per point.
**MDE80** = the smallest grid point at which ≥ 80% of plant members are outside the primary ensemble on that
statistic, expressed in the statistic's units as |plant mean − primary mean|.

| Prediction | Plant (× on the candidate weight) | Grid |
|---|---|---|
| P1u | line memory: × (1 + λ · share of the candidate's glyph units already written in the line) | λ 0.1, 0.25, 0.5, 1, 2 |
| P2 | paragraph palette: a per-paragraph PREFIX tilt ~ Dirichlet(κ_p · cell PREFIX distribution); stocks unchanged | κ_p 50, 20, 10, 5, 2 |
| P6z | pair prohibition: zero the weight of m random cells with primary expectation ≥ 3 | m 5, 10, 20 |
| P7 | e-run persistence: × (1 + λ) when the candidate's e-class equals the previous word's | λ grid |
| P8 | family alternation: × (1 + λ) when the qo vs ch/sh family switches from the previous word | λ grid |
| P10 | per-line hapax propensity: × g_l for hapax candidates, g_l ~ Gamma(1/λ², λ²) (mean 1) | λ grid |
| P11 | linear medial-quintile tilt for e-run 2+ candidates: × (1 + λ (q − 2)/2) | λ grid |
| P12 | × (1 + λ) for ok-initial candidates after a qok-initial word | λ grid |

Verdict per counted prediction on the primary:
- **NOT REPRODUCED:** B outside the primary ensemble.
- **NO EXCESS ON THIS SKELETON:** B not outside R0L (the within-cell shuffle). No note.
- **REPRODUCED (powered):** B outside R0L, not outside the primary, and MDE80 ≤ |B − mean(R0L)| (a residual as large
  as B's own excess over the shuffle would have been detected).
- **REPRODUCED (unpowered):** otherwise not outside. No note.
- **Sampler-sensitive:** a verdict that flips on R3L, R2Lw, R2Lmemo or R2P is labelled so and gets no scope note.
- The ladder spread (which rung carries the statistic) is reported descriptively. A high z\* makes "not outside"
  cheap; the MDE80 condition is what a powered REPRODUCED rests on.
- **Results:** *MDE80 per prediction to be inserted before the lock.*

## Decision rules (locked)
- Step 1: the primary's panel result (pass / INCOMPLETE with the outside statistics), the fidelity result, MIN-D
  descriptively.
- Step 2: the layer map on the primary, with every verdict's z, rank, MDE80 and sampler-sensitivity.
- **Registry:** one Tier-2 measurement row (inputs, sampler type and N, fidelity result, layer map, the scope
  statement below). Scope notes only on live Tier-2 measurement rows, with these templates:
  - same statistic, powered REPRODUCED: "[PHASE_779: not outside the PHASE_779 sampler of page × line-type
    composition, line-position vocabulary and two-unit junction routing (B {b}; sampler {m} ± {sd}; z {z}; MDE80 {d}).
    The sampler's inputs are fitted to B; not being outside it is not evidence that B was produced this way.]"
  - related statistic: "[PHASE_779: a related statistic ({definition}) is not outside the PHASE_779 sampler (z {z};
    MDE80 {d}); this row's measurement is not re-tested and stands.]"
  - NOT REPRODUCED: "[PHASE_779: {statistic} lies outside the PHASE_779 sampler (B {b}; sampler {m} ± {sd}; z {z}); it
    is not shown to follow from these rules as sampled. Sampler-sensitive: {yes/no}.]"
  - unpowered REPRODUCED and NO EXCESS: no note. If P2 is powered and REPRODUCED, C1811/C1812 get a re-check flag,
    not a re-scope. C1435 keeps its definition-check flag. No notes on Tier-3 rows, content rows (C1889, C1965,
    C1969, C2034) or superseded rows (C957). No tier changes. No Tier-0 change.
  - Row scope statement: "Composition is an input; nothing here bears on vocabulary, folio-unique words (C531), Zipf
    or hapax share, or on how page stocks arose. MIN-D is a sampler of measured rules, not a production method, and
    does not bear on C2077/C2096. Not being outside the sampler is not evidence of generation. No reading."
- Sensitivity (descriptive): the primary at κ × 0.5 and κ × 2 and at κ_z × 0.5 and × 2 (200 members each).
- **HARNESS-FAIL:** a code failure; no verdict.

## Declared prior knowledge and exposure
- **B supplied before the lock:** the skeleton with paragraph-first flags; the per-cell token multisets; the zone
  tables and routing tables above (composition and within-line adjacent-pair statistics); B's D2–D6 (PHASE_757/778);
  the header extension's line-type tables (P_B(header | unit), P_B(zone | unit, line type)); registered B values for
  the nine-bigram count (0), the maximum-window statistic (8), P7 (0.455 if the definition matches) and P8 (C549).
- **Not computed on B before the lock:** P1u, P2, P6z, P10, P11, P12 as defined here; the consistency descriptives
  as defined here.
- **Disclosed, unblinded:** (i) P3: while checking the v1 header plant, the plant's own line-type tables showed that
  last-unit-m tokens end paragraph-first lines about as often as body lines (91 of 457 against 327 of 1,842), so B's
  P3 ≈ +0.02; it is a consistency statistic. (ii) P4 and P5: the v1 header plant's dry-run members (gallows-initial
  excess +0.68 to +0.75; f/p excess +0.03 to +0.05) approximate B's values by construction, and the two are inputs on
  the line-type stocks; they are line-type contrasts, not counted. (iii) Dry-run member values were seen for every
  statistic on every variant (members only), including the nine-bigram count (15–36 on v1 members).
- The fidelity run computes D2, D6 and the diagnostics only; the plants compute prediction statistics on generated
  members only.

## Procedure
1. Fidelity gate; plants; this draft completed with their results; commit; lean-expert confirmation pass.
2. `run779.py --checksums`, commit, tag `phase779-lock`.
3. `run779.py run` (B's values; 9 × 1,000 members plus the second block for R2L and R0L; about 1.5 h at Idle
   priority); `run779.py verdict`; raw results committed before the write-up; lean-expert results check; write-up.

## Caveats
- **One sampler, one implementation of the rules.** The ladder, the 'w', 'memo' and page-only variants and the κ
  sensitivity bound the choices that matter most; a within-cell Metropolis sampler is the declared fallback.
- **The device is given B's cell compositions exactly** and therefore says nothing about how a cell's vocabulary
  arose, only about what follows once it exists.
- **Statistics with a registered relative that is not the identical statistic** (P1u ↔ C1214, P2 ↔ C1811) cannot
  retire the constraint; the related-statistic template applies.

# PHASE_781 — The head of the page: do the first lines of the herbal pages co-vary with their drawings? (go/no-go on Brunschwig first) (pre-registration)

**Status: v2 after the lean-expert design audit (v1: LOCKABLE AFTER EDITS; A1–A8 and B1–B7 incorporated, drops per C).
To be tagged `phase781-prelock` before Stage 1 runs (A8); final lock after Stage 2. After the pre-lock tag, changes
come only as numbered amendments justified on controls; no amendment may touch the gate, the 0.85 bar, the z\* rule or
the verdict rules.**

**Origin.** PHASE_780 (C2098, NOT DETECTED, unpowered) showed where a real herbal's text–picture link lives: in
Brunschwig 1500 the whole-entry link was detected in 61% of samples, with names masked 27%, uses only 14%, a random
window 1%: it runs through the plant's name at the head of each entry. This phase aims the same machinery at the head of
the page and runs the Brunschwig control first; the Voynich first lines are touched only if the control shows the test
can see a real herbal's head-of-entry link at the Voynich's size.

**Question.** On the 91 hand-1 herbal pages (Currier A), do pages whose drawings are similar carry similar first lines
(and first words), beyond position, quire, sheet, layout, spelling dials, the initial gallows, style and length?

**Family (declared now).** PHASE_780 and PHASE_781 are the planned family of text–picture tests on these 91 pages. This
is the second; the chance that at least one of the two returns a false positive is ≤ 0.02. PHASE_780's result is known
(whole page, T1 Z +0.73, T2 +0.11); its statistic included the first lines. Same pages, same blind picture codes, same
covariates: not independent evidence. Reusing the codes is fine (blind to text, gated on pictures only).

**Mechanism, not meaning (C2052).** A positive says first lines co-vary with what is drawn; it does not read any word.

## Data
- **V-A1:** PHASE_780's 91 pages, picture codes, gate, content similarity C and style similarity Y (no recoding).
- **First line:** the first line of the first paragraph (on all 91 pages it is also the first P line in reading order;
  checked on text only); mean 7.8 tokens (3–12). **First word:** its first token.
- **Initial gallows (A7, decided after the census below was seen):** the first word's initial gallows unit (p, k, t, f,
  cph, cfh, cth, ckh) is removed **in both H1 and H2**; "same initial gallows" (categories p, k, t, f, cph, cfh, cth,
  ckh, none) enters the covariates of both. Rationale from text-only facts: 87 of 91 first words open with a gallows
  unit taking four main values, so it behaves as a page-level category; C530 (Tier 2, A) records gallows folio
  specialisation, so it may act as a spelling dial. Versions with the gallows kept are descriptive only.
- **Census (seen before the design):** 86 distinct first words of 91; first units p 39, k 20, t 17, f 8, cth 3, o 3,
  sh 1; 482 first-line types, 397 hapaxes.
- **Brunschwig (BR):** PHASE_780's 121 eligible entries and codes, degraded to V's α as in PHASE_780. **Each replicate
  draws 91 entries (A1).** Head = the first n tokens of the entry text after its heading line (the rubric "Von …
  wasser" excluded: the conservative choice, matching PHASE_780; B1), n drawn per entry per replicate from the V-A1
  first-line lengths. First word taken literally (sometimes a modifier, e.g. "wyss" in "wyss gylgen"; 11 of 121
  entries open with a colour or kind adjective).
- **Brunschwig's decorated initial (text-only fact, found while testing the code).** Each entry opens with the plant
  name, whose first letter is a decorated initial; in about a sixth of the entries the transcription omits it
  ("Mpfferwasser", "Grimonien", "Albeyen"). Nothing is restored: where it is missing, Brunschwig's first word is the
  name without its initial, which resembles the Voynich first word without its gallows (A7). 98 of 121 first tokens carry the heading's name stem
  (matching the stem, or the stem without its first letter on the first token); the misses are spelling variants,
  modifiers and three entries whose text opens mid-sentence (22, 41, 42; PHASE_780's entry boundaries, unchanged).

## Measures
- **H1:** cosine of tf–idf vectors over within-word unit trigrams (word-boundary markers) of the first line.
- **H2:** the same over the first word only.
- idf over the corpus's own first lines / first words (BR: per sample).

## Statistic, covariates, nulls
- S_m (m ∈ {H1, H2}) = PHASE_780's partial correlation of double-centred text and content similarity, given the
  covariates and Y.
- **Covariates:** V: PHASE_780's V covariates plus first-line length (|Δ log| and Σ log) and same initial gallows. BR:
  same chapter, PHASE_780's distance terms, first-line length.
- **Nulls (identical for V and BR, A2):** N-local, N-shift, N-sheet. For BR, the 91-entry sample in entry order takes
  V-A1's page structure: entry k is assigned V-A1 page k's bifolium label (V's quire sizes and conjugate pattern,
  including V's incomplete bifolia: 21 groups of 4 pages, one of 3, two of 2) and V-A1 page k's two-leaf block label
  (17 blocks of 4, one of 3, ten of 2) for N-local. 10,000 permutations for N-local and N-sheet.
- **Decision statistic (B5):** Z_m = min(z_local, z_shift, z_sheet); Z_rep = max over (H1, H2) of Z_m; outside if
  Z_rep > z\*.

## Replicate and threshold rule (A3, fixed now)
Every calibration setting (Brunschwig and Voynich) is run to 2,000 replicates; z\* = the maximum over settings of the
point 99th percentile. No setting is extended or cut after any result. (The audit's first option; compute allows it:
about 6.5 s per replicate on six workers. The bootstrap upper 90% bound is reported beside each setting, descriptive
only.)

## Stage 1 — the go/no-go (Brunschwig only; no Voynich first-line statistic)
- z\*_BR,head: K1 (i) Markov and (ii) quire-step generators (PHASE_780's, letter chapters as quires) on 91-entry BR
  samples with the head text, 2,000 replicates each, under the three nulls.
- **Gate genre power** = the fraction of 200 BR replicates (91 entries, fresh length draw, degraded codes) with
  Z_rep > z\*_BR,head; point estimate, Wilson 95% interval reported. It is an upper bound on the final genre power
  (computed on the same 200 replicates at the final threshold, A1).
- Descriptive rows (none can reopen the gate), 200 replicates each with their own seeds:
  - names masked: tokens carrying a heading name stem removed before the head is drawn (the first token also matched
    without its first letter; PHASE_780's names-masked row matched full stems only, so it left 20 of these 98
    name-bearing first words in place);
  - body-window comparison: a window of the same length starting after the head (not a size control, B3);
  - rubric included: the heading's words other than "von" and "wasser" prefixed to the head (B1);
  - first non-modifier: H2 on the first head token not in the declared list of colour and kind adjectives;
  - the gate power at 2.957 (PHASE_780's z\*_V, a forecast, B2); the share of heads containing a name stem (B4); the
    number of entries whose first word is a modifier (11 of 121).
- **Gate:** if the gate genre power < 0.85, the phase STOPS.

## Stage 2 (only if the gate passes)
- **Voynich calibration:** K1 (all PHASE_780 settings, including the maximum-strength shared drift) and K2 (contiguous
  and misbinding sessions, anchored to the first-line adjacency excesses measured on the text alone and on the
  pictures alone), first-line measures, the A3 rule → z\*_V.
- **K3 power (A4):** (a) total-token plant: t ∈ {1, 2, 3} descriptor tokens per first line in total, each belonging to
  an entered feature chosen at random per page, keyed on set A's codes, tested with C from set B; (b) name plant (H2):
  the pictures clustered into k = 10 and k = 20 groups on set A's C; the first word (after its gallows) replaced by a
  stem keyed to the group, exact and spelled (variants differing in 1–2 units), tested with C from set B; 200
  replicates per point; planted outcomes only are stored; the unplanted shifted S is never printed.
- **Final genre power** = the same 200 gate replicates at max(z\*_V, z\*_BR,head). **If < 0.85, the phase STOPS** before
  the Voynich run.

## Stage 3 (only if Stage 2 passes): final lock and one run on V-A1
- **Verdicts:** CO-VARIES AT THE HEAD OF THE PAGE (outside on H1 or H2; then PHASE_780's interleaved-writing re-coding
  check decides robustness, unchanged) / NOT DETECTED (genre-powered).
- **Templates (A5):**
  - CO-VARIES: PHASE_780's template with head-of-page wording, plus "the second pre-registered test of text–picture
    co-variation on these 91 pages (after C2098); the chance that at least one of the two returns a false positive is
    ≤ 0.02"; one cross-reference note on C2098 in this case only: "whole-page statistic; co-variation at the head of
    the page is reported in C{n}". Human sign-off before registration.
  - NOT DETECTED (genre-powered): "… bears on head-of-page links at least as strong as Brunschwig's, which run through
    plant names that share stems across related plants; a naming system that does not share name parts across similar
    plants is not covered. Same pages as C2098; not independent evidence beyond this row." No notes on other rows.
- What each result can show (likelihood ratios as in PHASE_780) is filled in at the final lock from the Stage 1–2
  numbers.

## Exposure and binding stop (A6)
- Before the final lock, no statistic combines the real picture records (or C) at their own positions with any
  text-derived quantity: no covariate fits, no collinearity checks of "same initial gallows" against C, no previews.
  Diagnostics use synthetic, resampled or shifted (|k| ≥ 10) pictures only.
- **On a STOP, no Voynich first-line × picture statistic is computed, descriptive or exploratory, in this phase or
  later without a new phase with its own power gate.**

## Registry
- **STOP (at the gate or at Stage 2):** no constraint row (precedent PHASE_773); no note on C2098 or any row. The INDEX,
  STATUS_BRIEF and RESEARCH_AGENDA record: "PHASE_781 stopped at its pre-registered gate [its Stage 2 power re-check]:
  on the Brunschwig 1500 herbal, a head-of-page text–picture test at 91 entries and the Voynich first-line lengths
  detected the herbal's own link in at most {g}% of samples (Wilson {lo}–{hi}%; bar 85%). The Voynich first lines were
  not tested against the drawings and remain unexposed. This is a fact about the test's power, not about the Voynich."
- NOT DETECTED (genre-powered) and CO-VARIES: one Tier-2 row each, per the templates.

## Caveats
- The first line of a Currier A paragraph is a special line; the covariates include its length and initial gallows,
  not its full profile.
- Brunschwig's names repeat across related plants (rosen, gilgen, violen); a Voynich naming system need not share
  name parts across similar plants.
- Any further text–picture test on these 91 pages must be justified on controls and carry the family bound
  (RESEARCH_AGENDA, B7).

## Drops (audit C)
V-B2 (all arms); the gallows-kept measures as decision measures; per-feature K3 plants; CODING FAILED as a Stage 3
verdict.

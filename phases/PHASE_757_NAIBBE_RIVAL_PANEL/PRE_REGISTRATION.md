# PHASE_757 — Rival-generator panel I: the Naibbe cipher (pre-registration)

**Locked:** 2026-09-27, before any panel statistic was computed. Design audited by the lean-expert (verdict LOCK WITH
CHANGES; every requested change is incorporated below). Only the generator harness gates (G1, G2) may run before the
panel; they compute no discriminator.
**Origin:** STRATEGIC_REVIEW_2026-09-27 §3 #5. Gates #2–#4 have reported (PHASE_753 + PHASE_756, PHASE_754, PHASE_755).
**Question:** Can the Naibbe cipher as published — a verbose homophonic substitution cipher that encrypts Latin or
Italian as Voynich-like text and remains decipherable — generate Currier B? The Tier-0 "not a cipher" clause has
never faced a generator of *meaningful* Voynich-like text (only Timm & Schinner, C2077, non-semantic). This is the
first adversarial test of the encoding half of Tier 0 against a decodable cipher.
**Content vs encoding:** the result bears only on encoding. A Naibbe-style encryption of a distillation text would
still be a distillation text.
**Change control:** after lock nothing below (plaintexts, windows, variants, statistics, thresholds, N, seeds) may
change without a new phase number. Making this pre-registration public (external timestamp) and contacting the
cipher's author are decisions for the human collaborator; the lock is the local commit.

## Generator under test
Greshko, M. A. (2025), *Cryptologia*, DOI 10.1080/01611194.2025.2566408; code github.com/greshko/naibbe-cipher at
commit f2675ec (modified MIT; cited as required); supplementary materials Zenodo 17219445. Two published versions:
- **GV2:** `naibbe_v2.py` defaults — 78-card deck (the deck of the supplement's representative ciphertexts), RESPACING
  = 17, unambiguous bigrams with the full cross-bigram collision check.
- **GV1:** `naibbe.py` defaults — 52-card deck, RESPACING = 17, unigram-collision check (the version that produced
  the repository's committed reference ciphertexts).
Both use `references/naibbe_tables.csv` and `clean_line` (letters only; J→I, K→C, W→UU). Code is used unmodified
except for per-member seeding of Python's `random` and the layouts below. The tables were tuned on Currier B: this is
the strongest available form of the rival, not a strawman.

## Harness gates (must pass before any panel statistic)
- **G1 — decipherability.** For 5 members per plaintext and version (SR0, V0), the repository's `decrypt_naibbe.py`
  (BASIC, MARK_COMPOUND) recovers ≥ 99% of the plaintext letters in order.
- **G2 — reproduces the published generator.** (a) GV2 on P-NH at 21,610 tokens: the fraction of word types occurring
  once lies in [0.40, 0.60] (supplement S1.1: "about half of all Naibbe cipher word types in ciphertexts approaching
  the length of Voynich B appear only once"). (b) GV1 on P-NH versus the committed `encrypted/nathist_output_ciphertext.txt`
  truncated to the same token count: type/token ratio, single-occurrence type fraction and mean token length each
  within ±10% (relative).
Failure of either gate: fix the harness (never the generator logic). If it cannot pass without changing generator
logic: verdict HARNESS-FAIL.

## Plaintexts (declared)
| Id | Text | Genre | File |
|---|---|---|---|
| P-REC | Pseudo-Lull *Codicillus* (MS pv54euh, c. 1470; project transcription; `#` lines, `[?]`, `{red: …}` wrappers and page markers stripped, bracketed text kept) | Latin alchemical recipe | `sources/codicillus/codicillus_complete_latin.txt` |
| P-PHA | *Antidotarium Nicolai* (van den Berg 1917) | Latin pharmacy | `sources/antidotarium_nicolai/antidotarium_nicolai_latin_plain.txt` |
| P-ITA | Dante, *Inferno* | Italian (verse; no Italian prose on hand) | `sources/italian_german/dante_inferno.txt` |
| P-NH | Pliny, *Natural History* XVI (the cipher author's own plaintext) | Latin prose | repo `input/examples/nathist_book16.txt` |
Each member uses a contiguous window starting at a uniformly random plaintext line, wrapping to the start if needed.
As a descriptive ceiling (no verdict role), D5's statistic is also computed on each plaintext's respaced chunk
sequence (Naibbe tokens decipher to chunks, so I(T_n; T_n+1) ≈ I(C_n; C_n+1) at population level).

## Target skeleton, layouts, spacing, noise
**B reference:** Currier B, H track, `P` placement, labels excluded; uncertain tokens are blockers (no adjacency or
bigram across them), as in PHASE_756: 2,299 lines, 21,610 certain tokens, 22 blockers, folio / line / position
skeleton. **Every generated corpus carries blockers at B's blocker positions.**
- **L-STREAM:** the member's ciphertext stream (encrypted line by line from the plaintext's own lines, as the
  published code does) is poured, in order, into B's certain-token positions.
- **L-WRAP (best case for line effects):** each skeleton line is encrypted from whole plaintext words, filled to the
  word boundary nearest B's certain-token count for that line (over or under; at least one word), so every line starts
  at a plaintext word. Lines continue past B's last line only if needed to keep the total within ±1% of 21,610 tokens;
  the corpus is cut at the first line boundary inside that band.
- **Space removal:** SR0 (none) and SR3 (the published 3% random space removal, `respace_line`), applied to the
  ciphertext **before** pouring or wrapping.
- **Noise:** V0 (none) and V1: token corruption rate ρ = ½ × the H–F token disagreement rate over aligned tokens of
  Currier B `P` lines with equal token counts in both tracks. A corrupted token receives one glyph-unit edit; the edit
  type (substitution / insertion / deletion) and the glyph units involved are drawn from the empirical H–F
  edit-distance-1 glyph-unit pairs (substitutions from the H→F confusion pairs).
**Declared variants:** 2 versions × 4 plaintexts × 2 layouts × 2 spacing × 2 noise = **64 variants**; every one must
exclude for EXCLUDED.

## Positive controls (same skeleton and blockers; no added noise — they resample B's own tokens)
- **M1:** 50-state first-order Markov (the 49 instruction classes of `CLASS_COSURVIVAL_TEST/results/class_token_map.json`
  plus one bucket for all unclassified tokens), line-initial state distribution, class-conditional emission from B's
  own frequencies; no forbidden-transition suppression. Features it builds in: D5 (class transitions) and D6
  (line-initial state) — declared conservatively.
- **G-EDGE:** PHASE_753's N2 edge-glyph generator. Features it builds in: D2 and D6.
N = 1,000 each. Reference members (reported only; N = 50): the Timm & Schinner fitted generator
(SELF_CITATION_HEAD_TO_HEAD parameters) and B with V1 noise added.

## Discriminators (identical computation on B and every corpus)
Adjacency is within line and never crosses a blocker. "Common" = token frequency ≥ 10 in that corpus. "Shuffle" = a
full uniform permutation of each line's certain tokens (blockers stay).
- **D1 — zero-cell excess (conditional).** Included **only if PHASE_756's locked verdict is RESIDUAL**, otherwise dropped
  before any panel statistic is computed. If included: zeros among common pairs with N5 expectation ≥ 3 minus their
  N5-expected count, each corpus's own N5 at PHASE_756's β\* (2 + 2 chains, 500 samples each), 40 members per variant;
  the outside test for D1 is parametric only (z-leg; the [min, max] leg is not meaningful at N = 40). Positive control:
  M1 only. M1 is expected not to contain B on D1 (a pure class Markov model has no mechanism for an excess of zeros);
  if so, D1 is dropped as unusable, as pre-declared.
- **D2 — edge-glyph MI (declared expected failure).** Plug-in mutual information (bits) between the last glyph unit of
  token n and the first glyph unit of token n+1 (PHASE_754 tokenizer `c[tkpf]h|[cs]h|i+[nrlm]|.`) over adjacent
  pairs, minus its mean over 20 shuffles. The Naibbe paper's own comparison reports this as a failure; it counts, and
  the verdict is also reported with D2 removed (secondary, not verdict-bearing).
- **D3 — adjacent repetition.** log((O + 0.5) / (X + 0.5)), O = adjacent identical pairs, X = exact shuffle
  expectation Σ_lines Σ_w n_w(n_w − 1) / L_line (certain tokens per line; lines split at blockers are treated as
  separate segments).
- **D4 — cross-folio trigram recurrence (C1790).** log((O + 0.5) / (S + 0.5)), O = number of distinct within-line
  token trigrams occurring in ≥ 3 distinct folios of the skeleton, S = its mean over 20 shuffles.
- **D5 — order information beyond edge coupling.** Held-out log-gain in bits per token, 10-fold cross-validation by
  line (line index mod 10). Base model P0(w | g): interpolated absolute discounting (d = 0.75) on g = last glyph unit
  of the previous token (`<S>` at line start or after a blocker), backing off to a unigram with Good–Turing UNK mass
  n1/N (held-out tokens unseen in training map to UNK). Full model P1(w | v): interpolated absolute discounting on the
  previous token v, backing off to P0(w | g(v)); P1 = P0 when v is unseen. Gain = mean over held-out tokens of
  log2 P1 − log2 P0. **D5 = gain(corpus) − mean gain over 3 shuffles.** (Edge-conditional, so D2 and D5 are separate
  families.)
- **D6 — zone dependence.** Mutual information (bits) between common token type and zone (INITIAL / MEDIAL / FINAL)
  over lines with ≥ 3 certain tokens, minus its mean over 20 shuffles.
Descriptive only: type count, single-occurrence type fraction, Zipf slope, mean token length, duplicate lines,
identical-run length distribution, per-folio max qok-window density, e-depth lag-1 and PHASE_755's D.

## Outside criterion, certification, verdict inputs
- N = 1,000 members per Naibbe variant (seed = 757_000_000 + 10_000 · variant index + member), 1,000 per positive
  control, 50 per reference member.
- For discriminator j and ensemble X, B is **outside** X if B lies outside X's [min, max] AND |B − mean_X| / sd_X > z\*,
  z\* = Φ⁻¹(1 − 0.005/k). If sd_X = 0, the [min, max] leg alone decides. Ensemble skewness is reported.
- **Certification (before any Naibbe comparison is read):** discriminator j is usable if B is not outside at least one
  positive control (D1: M1 only). For each usable j, record which control(s) certified it and whether that control
  builds j in. k = number of usable discriminators, fixed at this step.
- For variant v, **n_out(v)** = number of usable discriminators on which B is outside the Naibbe ensemble. A variant
  **excludes** if n_out(v) ≥ 2 AND at least one of its outside discriminators was certified by a control that does not
  build it in.

## Decision rules (locked)
- **Rerun rule:** any variant that does not exclude is rerun once with a fresh seed block (seed offset + 5,000,000);
  it counts as non-excluding only if the rerun also fails to exclude.
- **EXCLUDED** — every one of the 64 variants excludes. Registry: Tier-2 **negative-knowledge** row "Naibbe v2/v1 as
  published (four plaintexts, two layouts, two spacing settings, noise-matched and noise-free) excluded as a generator
  of Currier B on {discriminators}". Scope notes on C119/C120/C171/C173 and in `CORE/frozen_conclusion.md`: "verbose
  homophonic substitution — Naibbe as published — tested and excluded". This is a tested-and-excluded rival, not
  evidence for C120 or for the control-program reading (framework-as-null). A modified Naibbe (for example with
  line-initial conventions) is a new test.
- **NOT EXCLUDED** — at least one variant fails to exclude after its rerun. Registry: Tier-2 row "Naibbe not
  distinguishable from Currier B on k − n_out of k usable discriminators under variant(s) …". Flag for human review:
  the Tier-0 sentence (its "not a cipher" scope), C119, C120, C173, and the engineered-substrate stack (C2015, C2022,
  C2032, C2055), whose "not natural language" readings become compatible with enciphered Latin or Italian.
- **PARTIAL** — reported alongside either verdict: outcomes per version, plaintext, layout, spacing and noise, and the
  verdict with D2 removed. Never changes the verdict.
- **HARNESS-FAIL** — G1 or G2 cannot pass without modifying generator logic; no verdict.

## What this phase does not do
It does not test verbose homophonic ciphers as a class, the Rugg grille (panel II), the content reading, or B versus
natural language (letter-unit baselines would be required for that).

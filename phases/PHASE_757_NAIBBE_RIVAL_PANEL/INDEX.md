# PHASE_757 — Rival-generator panel I: the Naibbe cipher

**Status:** RUNNING. **Pre-registration:** `PRE_REGISTRATION.md` (locked, commit a5506cb, audited by the lean-expert).
**Scripts:** `scripts/naibbe_harness.py` (generator, plaintexts, skeleton, layouts, noise, controls),
`scripts/panel_stats.py` (D2–D6, descriptives), `scripts/harness_gates.py` (G1, G2), `scripts/panel_run.py`
(stages `controls`, `naibbe`, `verdict`).
**Generator code:** github.com/greshko/naibbe-cipher at commit f2675ec, cloned to `external/naibbe-cipher/`
(git-ignored; 44 files whose names contain backslashes could not be checked out on Windows — all under
`figure_utils/gaskell_bowern_2022/data/cleaned/`, duplicates of the zip in the same folder; none is used).
Supplementary materials (Zenodo 17219445) in `external/naibbe-zenodo/`.

## Harness gates (run before any panel statistic) — PASSED
| Gate | Result |
|---|---|
| G1 decipherability (5 members × 4 plaintexts × 2 versions, 150 lines each) | GV2 min letter recovery 1.0000 on every plaintext; GV1 0.9916–0.9929 (threshold 0.99). |
| G2a GV2 on P-NH at 21,610 tokens: single-occurrence type fraction in [0.40, 0.60] | 0.485 (SR0), 0.541 (SR3) |
| G2b GV1 vs the committed `encrypted/nathist_output_ciphertext.txt` (34,741 tokens each) | TTR 0.1618 vs 0.1611; single-occurrence types 0.4099 vs 0.4091; mean length 5.247 vs 5.234 (all within 0.5%) |
Noise model (`results/noise_model.json`): H–F disagreement 13.59% of 34,000+ aligned certain tokens → ρ = 0.0679;
1,477 edit-distance-1 glyph-unit edits (substitution 1,261, deletion 173, insertion 43).

## Implementation details fixed before any panel statistic was read
- **Plaintext normalization:** the published `clean_line`, then removal of any character outside a–z (the
  Antidotarium contains the drachm sign ʒ, which `clean_line` keeps and the cipher cannot encode).
- **P-REC extraction** (the Codicillus file mixes the Latin transcription with English page descriptions): headings,
  rules, code fences, list items, lines opening with `(` (English translations), notes/provenance sections and lines
  with ≥ 2 English marker words are dropped; `[?]` removed, `{red: …}` unwrapped, bracketed expansions kept. The
  transcription is heavily uncertain (`[?]` after most words); the plaintext is Latin-like but garbled.
- **P-ITA:** the file holds the whole *Commedia*; the declared *Inferno* is taken from the Gutenberg START marker to
  the `PURGATORIO` heading.
- **Certification z\*:** certification needs z\* before k is known; it uses k0 = 5 candidate discriminators.
- **Descriptive e-run statistic:** the descriptive "e-depth lag-1" uses the longest e-run per token (classes 0/1/2+)
  rather than `Morphology.atomize` (too slow for 66,000 corpora). Descriptive only.
- **D5 ceiling:** computed for the first 20 members of every STREAM/SR0/V0 variant, on the respaced plaintext chunk
  sequence poured into B's skeleton.
- **D1:** conditional on PHASE_756 (running at the time of the controls stage).

# PHASE_757 — Rival-generator panel I: the Naibbe cipher

**Status:** COMPLETE. Locked verdict **EXCLUDED** (all 64 declared variants, first pass; no rerun needed).
Registered as **C2080** (Tier 2, negative knowledge); scope notes on C119, C120, C171, C173 and in
`CORE/frozen_conclusion.md`.
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit a5506cb, audited by the lean-expert).
**Scripts:** `scripts/naibbe_harness.py` (generator, plaintexts, skeleton, layouts, noise, controls),
`scripts/panel_stats.py` (D2–D6, descriptives), `scripts/harness_gates.py` (G1, G2), `scripts/panel_run.py`
(stages `controls`, `naibbe`, `verdict`). Runtime: controls 5 min; Naibbe ensembles 2 h 53 min (64,000 corpora,
11 workers at below-normal priority); verdict < 1 min.
**Results:** `results/harness_gates.json`, `results/noise_model.json`, `results/controls_certification.json`,
`results/controls_raw.npz`, `results/naibbe_raw_offset0.npz` (64 × 1,000 × 5 discriminators and descriptives),
`results/d5_chunk_ceiling_offset0.json`, `results/panel_verdict.json`, logs.
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
Noise model: H–F disagreement 13.59% of aligned certain tokens → ρ = 0.0679; 1,477 edit-distance-1 glyph-unit edits.

## Certification (controls only, before any Naibbe comparison)
| | B | M1 mean (z_B) | G-EDGE mean (z_B) | Certified by |
|---|---|---|---|---|
| D2 edge-glyph MI (bits) | 0.228 | 0.009 (+141) | 0.238 (−1.7) | G-EDGE (built in) |
| D3 adjacent repetition (log O/E) | 0.015 | 0.299 (−3.7) | 0.107 (−1.0) | G-EDGE (not built in) |
| D4 cross-folio trigram recurrence (log O/S) | 2.474 | 0.690 (+2.5) | 0.515 (+2.9) | M1, G-EDGE (not built in) |
| D5 order information beyond edge (bits/token) | 0.040 | 0.040 (+0.1) | 0.020 (+4.2) | M1 (built in) |
| D6 zone dependence (bits) | 0.172 | 0.048 (+36) | 0.186 (−2.4) | G-EDGE (built in) |
All five usable (k = 5, z\* = 3.09). A variant excludes only if ≥ 2 discriminators are outside and at least one of them is
D3 or D4. Reference members: B + noise stays near B on every measure; the Timm & Schinner generator is far from B on D2,
D5, D6 (as C2077 found by other means).

## Result
| Discriminator | B | Naibbe variant means (range over 64) | B outside the ensemble in |
|---|---|---|---|
| D2 edge-glyph coupling | 0.228 | 0.005 – 0.009 (z 83–173) | **64 / 64** |
| D3 adjacent repetition | +0.015 (chance) | −1.07 – −0.59 (repeats suppressed; z 3.6–5.3) | **64 / 64** |
| D6 line-zone dependence | 0.172 | 0.000 (stream) – 0.130 (word-wrapped) (z 5.5–96) | **64 / 64** |
| D5 order information beyond edge | 0.040 | 0.050 – 0.127 (z −1.9 – −11.7) | **51 / 64** (B lower than every variant mean) |
| D4 cross-folio trigram recurrence | 2.47 | 0.20 – 1.67 | 15 / 64 |
Discriminators outside per variant: 3 (6 variants), 4 (50), 5 (8). Same pattern in both code versions (GV1: D5 outside
26/32, D4 5/32; GV2: D5 25/32, D4 10/32). **Secondary (D2 removed): all 64 variants still exclude.**
D5 ceiling: the respaced plaintext chunk sequences themselves carry 0.19–0.27 bits/token; the cipher's homophony dilutes
this to 0.05–0.13; B shows 0.040.
Descriptive (example, GV2 / Codicillus / stream / 3% spacing / noise): types 5,666 vs B 4,640; single-occurrence types
58.5% vs 66.9%; Zipf slope −0.91 vs −1.05; max identical run 2 vs 4; max qok tokens in a 10-token window 6.0 vs 8.

## Verdict (locked rules): EXCLUDED
The Naibbe cipher as published cannot generate Currier B under any declared plaintext, layout, spacing or noise setting.
B has four properties Naibbe lacks: tokens linked across word boundaries (end glyph → start glyph), repetition at chance
rather than suppressed, vocabulary tied to line start/end, and less token-to-token order information than a decodable
encryption of real text carries.

## Reading and scope
- **What is excluded:** this generator as published (both code versions), on these plaintexts and layouts. A modified
  Naibbe with line-initial conventions and boundary rules would be a new test. Ciphers with coarser units (syllables,
  whole-word codebooks) are untested.
- **What it is not:** evidence for the control-program reading (C120) or for any content reading. Excluding one rival is
  negative knowledge (framework-as-null). Content and encoding are separate: a cipher of a distillation text would still
  be a distillation text.
- **The four properties are a specification** any future cipher proposal must meet.
- **The order-information result (D5) reaches beyond this generator,** but only as a lead: any letter-level decodable
  cipher must carry its plaintext's letter order into the token sequence, and B carries less order (beyond edge coupling)
  than every Naibbe variant. That argues against letter-level verbose ciphers generally, and it is also the signal a
  statistical decipherment would need. It does not cover syllable- or word-level codes.
- **Human decisions pending:** making the pre-registration public (external timestamp) and contacting the cipher's author.

## Implementation details fixed before any panel statistic was read
- **Plaintext normalization:** the published `clean_line`, then removal of any character outside a–z (the Antidotarium
  contains the drachm sign ʒ, which `clean_line` keeps and the cipher cannot encode).
- **P-REC extraction** (the Codicillus file mixes the Latin transcription with English page descriptions): headings,
  rules, code fences, list items, lines opening with `(` (English translations), notes/provenance sections and lines
  with ≥ 2 English marker words are dropped; `[?]` removed, `{red: …}` unwrapped, bracketed expansions kept. The
  transcription is heavily uncertain (`[?]` after most words); the plaintext is Latin-like but garbled.
- **P-ITA:** the file holds the whole *Commedia*; the declared *Inferno* is taken from the Gutenberg START marker to the
  `PURGATORIO` heading.
- **Certification z\*:** certification needs z\* before k is known; it used k0 = 5 candidate discriminators (k turned
  out to be 5).
- **Descriptive e-run statistic:** longest e-run per token (classes 0/1/2+), not `Morphology.atomize`. Descriptive only.
- **D1:** dropped. PHASE_756 had not returned a RESIDUAL verdict when the panel ran (its EVA run returned p = 0.60).

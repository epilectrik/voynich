# PHASE_777 — Is one glyph position per word a message channel, with the rest of the word rule-built filler?

**Status: DESIGN COMPLETE, v3 for lock (pre-registration `PRE_REGISTRATION.md`).**
- **Origin:** the human's idea (2026-09-30): "maybe one character in a token is important and the rest is generated
  from rules" — the Trithemius *Ave Maria* construction, one plaintext letter per word.
- **Why untested before:** every null of PHASE_774–776 fixes each word's first glyph and last two glyphs and scrambles
  only the interiors. A payload in the edge glyphs was preserved in every null sample.
- **Design history (controls only; B blind):** v1 (four arms F1/F2/L1/L2) failed its fresh-seed certification
  (INDETERMINATE count; L1 ↔ L2 leakage); v2 restricted the confirmatory arms to F1 and F2 with two-way calls and
  passed a fresh certification (0 of 48 no-payload arm calls PRESENT; 12 of 12 payloads PRESENT). No threshold
  changed between versions.
- **Lock audit (lean-expert, controls only; `scripts/audit/`, `results/audit/`):** LOCKABLE WITH EDITS. The audit
  found that no-payload *palette* plants (start symbols drawn from a per-paragraph or per-line-position palette at
  Dirichlet α 5) can read PRESENT under EF-F, and that two refined nulls (EFq: line-position quintile in the key;
  EFpar: paragraph × line-type groups) remove them while payload controls keep power. v3 adds those nulls as the
  interpretation gate for a PRESENT, the band-dependent exclusion scope with noise figures, and the wording edits.
  The confirmation pass (05ab031) found that line palettes pass both refined nulls and added the line-entropy
  condition to the gate.
- **Lock:** pending (`phase777-lock`).
- **Run:** pending.

## Question
Does the first or second glyph position of B's words carry a letter-by-letter payload of natural language, with the
rest of each word filler built by the boundary rules? Statistic: repeated 7-runs of the position's symbol sequence
within lines (RPT7, z7) under an exact null that scrambles that position among words with the same ending following
the same ending, within folio × line type (EF-F), so the junction coupling and the two-unit routing (C2082) are kept.

## Thresholds (design controls, R = 300; `results/thresholds777.json`)
| Arm | NEG (max no-payload z7) | POS (min payload z7) | τ | Call |
|---|---|---|---|---|
| F1 | 2.85 | 18.2 (Mesue) | 10.54 | PRESENT if p ≤ 0.005 and z7 ≥ τ; else NOT PRESENT (residual flag if z7 > NEG and p ≤ 0.05) |
| F2 | 3.13 | 17.8 (Mesue) | 10.46 | same |
| L1 / L2 / GAL | 3.95 / 3.94 / 2.63 | 6.1 / 5.1 / 2.3 | 5.05 / 4.53 / 2.46 | descriptive only |

**Interpretation gate (v3):** a PRESENT on F1/F2 is payload-level only if z7 ≥ τ/2 with p ≤ 0.005 under both EFq
and EFpar *and* the channel's line-entropy reduction (against within-folio shuffles) is below 8%. If the refined nulls
fail it names the palette they remove; if only the entropy condition fails it is "payload-level or line palette" (the
auditor's confirmation plants: α 7 line palettes pass both refined nulls at a 19% reduction). B's F1/F2 line-entropy
reduction and paragraph χ²/df are reported after the run as composition descriptives.

## Dry run (v3 code; `results/dryrun/`)
| Decoy | F1 | F2 | Gate | Composition F1 (entropy reduction; χ²/df) |
|---|---|---|---|---|
| F1 payload, Latin NT (third block) | PRESENT z7 89.6 | NONE −1.0 | payload-level (EFq 43.8, EFpar 35.8) | −2.9%; 0.84 |
| Edge-only chain (k = 2) | NONE 0.6 | NONE −0.5 | n/a (EFq 0.5, EFpar 0.7) | 0.0%; 0.99 |
| Paragraph-palette plant, α 5 (no payload) | PRESENT z7 17.0 | residual 10.1 | **fails**: EFq 11.8, EFpar 1.07 (p 0.16) → "consistent with a paragraph palette" | 19.4%; 7.10 |
| Line-palette plant, α 7 (no payload; the auditor's confirmation plant) | PRESENT z7 15.6 | residual 5.5 | passes EFq 9.5 and EFpar 7.3; entropy condition fails → "payload-level or line palette" | 19.3%; 2.12 |

## Result on Currier B
Pending the locked run (1,000 permutations per null, seed 77700).

## Files
- `PRE_REGISTRATION.md` (v3), `scripts/chan777.py` (channels, nulls EF-F/EF-L/EF-K2/EFq/EFpar, payload and palette
  constructions, composition figures), `scripts/prelock_proto777.py`, `scripts/prelock_calib777.py`,
  `scripts/prelock_thresholds777.py`, `scripts/prelock_cert777.py`, `scripts/run777.py`, `scripts/audit/`.
- Results: `results/prelock_proto777.json`, `results/prelock_calib777_design.json`, `results/thresholds777.json`,
  `results/prelock_cert777_v1.json` (failed v1), `results/prelock_cert777.json` (v2, PASSED), `results/audit/`,
  `results/dryrun/`.

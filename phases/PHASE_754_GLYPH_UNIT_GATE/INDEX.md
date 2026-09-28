# PHASE_754 — Glyph-unit orthography gate

**Status:** COMPLETE. Annotations applied to C1440, C1209, C1484, C1207, C521 (no new constraint).
**Pre-registration:** `PRE_REGISTRATION.md` (commit e9d7f1e, before code). **Script:** `scripts/glyph_unit_gate.py` (~45 s).
**Results:** `results/glyph_unit_gate.json`.

## Question
Are the flagged atom-level constraints restatements of how EVA spells single glyphs (benches ch/sh, benched gallows
cth/ckh/cph/cfh, minim groups in/iin/ir/…)? If so, what are the correct glyph-level statements?

## Part A — context determinism (share of a letter's occurrences inside a multi-letter glyph)
| Letter | Currier B | Currier A | Reading |
|---|---|---|---|
| h | 98.9% | 99.2% | second half of a bench / benched gallows |
| c | 99.3% | 98.7% | first half of a bench / benched gallows |
| n | 98.7% (i or a before it: 99.9%) | 95.1% | final stroke of a minim group |
| i | 97.7% | 97.4% | minim stroke |
| s | 68.5% | 57.4% | bench `sh`, but also standalone |
| r | 10.6% | 7.4% | mostly standalone (`ar`, `or`) |
| a, e, l, m | 0–6% | 0–7% | standalone glyphs |

## Locked classification
| Claim | B | A |
|---|---|---|
| C1440 (h transparent terminal) | PARTLY ORTHOGRAPHIC (98.9%) | IDENTITY (99.2%) |
| C1209 (n terminal) | PARTLY ORTHOGRAPHIC (98.7%) | PARTLY ORTHOGRAPHIC (95.1%) |
| C1484 (n←i only; h←c) | PARTLY ORTHOGRAPHIC | PARTLY ORTHOGRAPHIC |
| C1207 {c,h} cluster | PARTLY ORTHOGRAPHIC (98.9%) | PARTLY ORTHOGRAPHIC (98.7%) |
| C1207 {i,n} core | PARTLY ORTHOGRAPHIC (97.7%) | PARTLY ORTHOGRAPHIC (95.1%) |
| C1207 {a,i,n,r} cluster | NOT ORTHOGRAPHIC (a, r standalone) | NOT ORTHOGRAPHIC |
| C521 (e→h = 0) | PARTLY ORTHOGRAPHIC (98.9%) | IDENTITY (99.2%) |

"PARTLY ORTHOGRAPHIC" here means 97.7–98.9%: the claims are overwhelmingly spelling, with a residual of 1–2% rare
forms and readings.

## Part B — glyph-level restatements (the real facts behind the atom claims)
- **Bench non-finality (C1440):** bench and benched-gallows glyphs are token-final 0.16% of the time in B (0.6% in A),
  against 25.4% (29.7%) for all other glyphs. "h is a transparent terminal" means "the bench glyph is not a final form".
- **Minim-group finality (C1209):** in/iin/ir/… glyphs are token-final 97.1% (B) and 96.6% (A): final forms, like a
  final sigma. Bare `n` is rare (54 occurrences in B).
- **Bench/e ordering (C521):** within tokens, e→bench occurs 369 times against 1,713 under a within-token glyph shuffle
  (0.22×); bench→e 5,978 against 1,720 (3.5×). Currier A runs the same way (44 vs 518; 1,626 vs 513). EVA e→h itself
  is 4 (B) and 0 (A): the registered zero is spelling; the underlying glyph-order asymmetry is real.
- **Folio clusters (C1207):** EVA folio-proportion correlations reproduce the registered values (c–h 0.75, a–i 0.83,
  a–n 0.80, i–n 0.87). At glyph level c and h vanish into the bench; ch and sh proportions are anti-correlated across B
  folios (r = −0.24), and a with the in/iin family stays correlated (0.82): the aiin/ain family, not letter chemistry.
- **C1484:** n preceded by i 98.7%; h preceded by c/s/gallows 99.3%. Spelling rules.

## Reading
These constraints are not fake structure. They describe real glyph-position facts (non-final benches, final-form minim
groups, bench-before-e order) at the wrong unit. Interpretations built on the letter-level reading ("h-terminal
transparency", "n = opaque closure", "e→h one-way valve / stabilization is absorbing") rest on the transliteration,
not on the manuscript. Next steps: the same gate for the e-run family (C1225, C1967, C2031) and the remaining atom
constraints (C1394's slot model), and an image re-read of disputed minim and e counts.

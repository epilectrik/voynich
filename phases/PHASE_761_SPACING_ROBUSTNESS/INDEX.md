# PHASE_761 — Boundary glyph coupling vs word-spacing uncertainty

**Status:** COMPLETE. Locked verdict **ROBUST**.
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit cd7d887). **Script:** `scripts/spacing_check.py` (< 1 min).
**Results:** `results/spacing_check.json`, `results/run_log.txt`.
**Data:** ZL 3b IVTFF transliteration (Zandbergen–Landini, 2025-05-13), Currier B paragraph text, 2,478 lines —
an independent second transcription relative to the project's H track.

## Question
Boundary glyph coupling (last glyph unit of token n → first glyph unit of token n+1; C1212/C1563) is load-bearing: it is
the strongest discriminator that excluded the Naibbe cipher (C2080, D2). Rozanova & Temerev (2026) report that uncertain
spaces are mostly word-internal. Is the coupling carried by real word boundaries or by doubtful spaces?

## Results (shuffle-corrected MI, bits; 1,000 permutations; all p < 0.001)
| Boundary set | N | Coupling C | Share of C_all |
|---|---|---|---|
| All boundaries (definite + uncertain) | 20,331 | 0.256 | — |
| **Definite spaces only** | 18,711 | **0.215** | **0.84** |
| **Tokens merged across uncertain spaces** | 18,701 | **0.215** | **0.84** |
| Uncertain spaces only | 1,620 | **0.569** | — |
| Definite spaces, size-matched to the uncertain set (1,000 subsets) | 1,620 | median 0.208 [0.172, 0.246] | — |
Replication of PHASE_757's D2 (within-line pairs, full within-line shuffle baseline) on ZL: **0.243** vs **0.228** on the
H track.

## Verdict (locked rules): ROBUST
The coupling is carried by definite word boundaries: 84% of the pooled value survives both restricting to definite
spaces and merging tokens across uncertain spaces. C1212/C1563 and the D2 leg of C2080 stand (even the definite-space
value is about 25 times the Naibbe range of 0.005–0.009).

## Reading
- **Uncertain spaces behave like word-internal glyph transitions:** coupling across them (0.57 bits) is 2.7 times the
  definite-space value at the same N, and above all 1,000 size-matched definite subsets. This agrees with Rozanova &
  Temerev's finding that most uncertain spaces are not word boundaries.
- **Consequence for measurement:** counting uncertain spaces as boundaries inflates boundary-coupling estimates by about
  16% (0.256 vs 0.215 on ZL). Token-level statistics that treat every space as a word break carry a small within-word
  contamination; the effect is modest for coupling, but any statistic concentrated at doubtful spaces should be checked.
- **Second transcription:** the coupling reproduces on ZL at essentially the H-track magnitude (0.243 vs 0.228).

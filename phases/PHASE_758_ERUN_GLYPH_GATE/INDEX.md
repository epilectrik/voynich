# PHASE_758 — e-run family gate

**Status:** COMPLETE. **Pre-registration:** `PRE_REGISTRATION.md` (locked, commit 10134f7; first draft redesigned after
a lean-expert audit). **Script:** `scripts/erun_gate.py` (~3 min). **Results:** `results/erun_gate.json`, `results/run_log.txt`.
**Historical parser:** `scripts/voynich_pre_c1957.py` = `scripts/voynich.py` at f6015c8 (parent of a52ca08, before
C1957 blocked e-initial suffixes).

## Part A — cross-track consistency of e-run length: CONSISTENT, with a one-directional bias in track F
A0: the Currier (C) and First Study Group (F) transliterations write the e glyph as "C", one symbol per stroke, and
were converted into EVA reversibly (voynich.nu/transcr.html); e-run disagreements are reading differences.
Alignment: whole lines, token alignment by edit operations (equal blocks and equal-length replace blocks).

| | H–F | H–C |
|---|---|---|
| aligned certain token pairs | 19,603 | 8,363 |
| 1-vs-2+ (either track e-depth ≥ 1): n, raw agreement, κ, PABAK | 8,708; 0.982; **0.958**; 0.964 | 3,787; 0.979; **0.946**; 0.958 |
| H 2+ read as ≤ 1 / H ≤ 1 read as 2+ | 130 / 27 (**directional**) | 28 / 51 |
| run-length agreement, H runs of 1 / 2 / 3+ | 0.999 / 0.977 / 0.867 | 0.999 / 0.994 / 0.974 |
| equal-token-count rule: line retention; e-run density kept vs dropped | 70%; 0.478 vs 0.445 | 62%; 0.485 vs 0.442 |

Classification CONSISTENT (κ ≥ 0.80) with DIRECTIONAL BIAS for F (F reads 4.7% of H's 2+ runs as 1). Agreement between
non-independent transcriptions is an upper bound on reliability.

## Part B — C1225: SEGMENTATION ARTIFACT
- **B1:** under the pre-C1957 parser the published table reproduces exactly (single-e 590 tokens, -edy 368 = 64%, -y
  14%; multi-e 102, -y 37%, -s 13%, -edy 12%). Under the current parser it does not (single-e 607: -dy 52%, -y 31%;
  multi-e 839: -y 48%, -dy 46%).
- **B2 (migration crosstab, historical classes vs unsegmented e-run after k):** single-e: run 0 (e before k) 146, run 1
  44, run 2 367, run 3+ 33. **68% of "single-e" tokens have a run of 2+ after k** — the parser moved the second e into
  the suffix (qo·ke·edy). Named flaw SEGMENTATION ARTIFACT (threshold 25%).
- **B3/B4 (unsegmented, H):** 2,708 k + e-run occurrences. Next glyph after run 1: d 57%, o 17%, y 15%; after run 2+:
  d 45%, y 39%, o 11%. Miller–Madow MI = 0.061 bits; order-1 null (no memory of run length) mean 0.00001, q99 0.003;
  order-2 null (generic e-run transition pooled over heads) mean 0.083, q99 0.103; fraction reproduced by order 2 =
  1.35 [1.06, 1.67]. Verdict **GENERIC e-RUN TRANSITION**: run length matters, but after k no more than after e-runs
  generally (order 2 over-predicts).
- **B5:** next-glyph distributions differ by head (k, ch, sh, o, other; conditional MI permutation p = 0.001):
  **HEAD-SPECIFIC**. Common direction: after ch-e / sh-e the next glyph is mostly d (46–48%); after ch-ee / sh-ee mostly
  y (39–43%). The 1 → 2+ shift toward y is script-wide; its size differs by head.
- **B6 (track F):** same verdicts (GENERIC e-RUN TRANSITION; HEAD-SPECIFIC).

## Part C — cross-token e-depth claims on track F (N-matched): TRACK-ROBUST
- **C1 (C2031 D, Section B):** matched H D = +0.0277 [+0.0070, +0.0472] (81 paragraphs); F D = +0.0323 [+0.0114,
  +0.0529]. TRACK-ROBUST.
- **C2 (C1967 non-prefix gradient qo − sh):** matched H +0.157 (p = 0.0008; qo 116, ch 87, sh 34); F e-depth with H
  classes +0.131 (p = 0.004) TRACK-ROBUST; all-F +0.119 (p = 0.008) TRACK-ROBUST (its bootstrap CI includes 0).

## Registry actions applied (locked rules)
- **C1225:** rescoped. "Parametric axis" and "different instruction types" struck on the named flaw; the Tier-2 row now
  states the glyph-level table and its B4/B5 verdicts. Claim file banner added.
- **C1957:** note — the parser change stands as a segmentation choice; its gloss relied on C1225's struck reading.
- **Part A (DIRECTIONAL BIAS):** reliability note added to the 41 rows selected by the pre-registered grep (C901,
  C1199, C1204, C1225, C1245, C1410, C1735, C1736, C1897, C1899, C1908, C1912, C1914, C1918, C1923, C1941, C1943,
  C1945, C1952, C1953, C1957, C1967, C1968, C1972, C1977, C1985–C1987, C1994, C1995, C2021, C2028, C2031, C2032,
  C2039, C2043, C2044, C2047, C2067, C2072, C2077).
- **Part C:** no annotation needed (TRACK-ROBUST).

## Reading
The e-depth measurements that are cross-token or paragraph-level (C2031, C1967) survive a change of transcription,
and the e-run lengths they rest on are read consistently. The within-token claim C1225 was a parser artifact; the fact
underneath is a script-wide spelling regularity (…eey vs …edy), not a k-specific parameter.

# PHASE_759 — Aberdeen Bestiary negative control for the bifolium pipeline (PHASE_752 v2 step 1)

**Status:** COMPLETE. Locked verdict **SPECIFIC**.
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit 84d8339; lean-expert audit LOCK WITH CHANGES, applied).
**Script:** `scripts/aberdeen_control.py` (15 min). **Results:** `results/aberdeen_control.json`, `results/run_log.txt`.
**Data:** `sources/aberdeen_bestiary/` (199 text pages, 43,800 words; collation read from James's formula with the site's
quire and leaf marks; quire H undetermined and excluded; transcription text kept local — no licence stated).

## Question
Does the PHASE_752 pipeline (TF-IDF, SVD k = 75, cosine), with the re-pairing null and distance/length
residualization, report a same-sheet effect in a normal codex whose text runs continuously? And could it have seen an
effect as large as the Voynich ones?

## Aberdeen, primary stratum (regular quires E, F, G, I, K, M: 24 sheets, 658 cross-leaf page pairs, 94 sheet pairs)
| Statistic | Value | p (upper / lower) |
|---|---|---|
| T_sheet (mean residual of sheet pairs; model: log page distance + contiguity + log min/max words + quire FE) | +0.005 (0.04 residual SD) | 0.34 / 0.66 |
| T_strat (sheet vs non-sheet pairs at the same leaf distance 1, 3, 5; 18 cells) | +0.003 (0.03 SD) | 0.44 / 0.56 |
| T_face (facing minus other, raw) — sanity gate | +0.250 | 0.0001 |
| MDE80 (residual-SD units) | T_sheet 0.26, T_strat 0.48 | |
| Similarity slope on page distance | −0.013 per page | |
Per-quire exact p for T_sheet: E 0.24, F 0.95, G 0.53, I 0.34, K 0.09, M 0.52. Diagnostic v1-style linear model:
T_sheet p 0.16 / 0.84. Robustness: k = 50 (p_up 0.29 / 0.46), k = 100 (0.30 / 0.38), raw TF-IDF (0.60 / 0.63);
T_face p = 0.0001 in every setting. Secondary stratum (all 14 determined quires): T_sheet 0.38 / 0.62, T_strat 0.87 /
0.13. No lower-tail flag anywhere (no misspecification).
**Planted effect:** appending 10% of each page's length in tokens drawn from the conjugate leaf shifts T_sheet by 1.66
SD and T_strat by 2.07 SD (both p = 0.0005); the SVD step does not distort the shift (raw TF-IDF: 1.64 / 2.04).
**Length-matched runs** (Aberdeen pages cut to Voynich page lengths, 20 replicates each): pure-A lengths (median 80
words) median p_up 0.27 / 0.23, MDE80 0.25 / 0.41; Q13 lengths (327) 0.33 / 0.45, MDE80 0.26 / 0.48; Q20 lengths (449)
0.34 / 0.45, MDE80 0.26 / 0.49.

## Voynich comparison (H track; reported, not registered)
| Stratum | T_sheet (SD) | p_up | T_strat (SD) | p_up | T_face p |
|---|---|---|---|---|---|
| herbal pure-A Q1–Q3 (44 sheet pairs) | +0.58 | **0.0007** | +0.87 | **0.004** | 0.14 |
| Q13 (20) | +0.71 | 0.013 | +0.99 | 0.040 | 0.49 |
| Q20 (22) | +0.64 | 0.017 | +0.63 | 0.26 | 0.65 |
Every Voynich effect exceeds the Aberdeen MDE80 in the matching length regime, so the control is not underpowered.

## Verdict (locked rules): SPECIFIC
The pipeline does not manufacture a sheet effect in a continuous-text codex, sees that codex's page-to-page continuity
very strongly, and detects a planted sheet effect far smaller than the Voynich effects. T_sheet and T_strat may be used at
the Voynich registration gate.

## Reading
- The two manuscripts behave in opposite ways. Aberdeen: continuity between facing pages, no sheet effect. Voynich:
  sheet effect, no continuity between facing pages (T_face p 0.14–0.65). A normal codex written in gathering order
  looks like the first; the Voynich text does not.
- **For the PHASE_752 registration gate** (re-pairing p < 0.01 in ≥ 2 of 3 strata, both tracks, after residualization):
  with the residual model locked here, only herbal pure-A passes on the H track (T_sheet 0.0007, T_strat 0.004). Q13
  (0.013) and Q20 (0.017) miss 0.01; the unresidualized PHASE_752 audit values were 0.0095 and 0.0033. As things stand
  the gate is not met even before the second track (ZL3b), which is v2 step 2.
- Scope: the assumption that Aberdeen was copied in gathering order is standard codicology, not tested here.

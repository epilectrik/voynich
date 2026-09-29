# PHASE_769 — Is the e-run "dial" set per folio or per procedure?

**Status:** COMPLETE. Verdicts under the locked rules:
- **Folio arm:** FOLIO-LEVEL COMPONENT PRESENT.
- **Paragraph arm:** SETTING AT PARAGRAPH SCALE OR COARSER PRESENT. It is not paragraph-specific.
- **Picture gate:** PASSED.

Registered as C2086 (Tier 2, measurement).

**Pre-registration:** `PRE_REGISTRATION.md`, locked at b98c287 after a lean-expert audit (E1–E12) and a 200-replicate
calibration on controls only. B's run-length statistics by folio or paragraph were never computed before lock.

**Scripts:**
- `ed769.py`, `ed769b.py` (the engine);
- the calibration scripts: `prelock_controls769*.py`, `prelock769_worker.py`, `prelock769_summary.py`,
  `prelock769_zl_para.py`;
- `run_b769.py` (37 s at Idle priority).

**Post-lock script correction:** the i-run block was removed from `run_b769.py` to match the locked text, which says
i-runs are not analysed. The lock hash was filled in.

**Results:** `results/e_dial_B.json`, `results/run_log.txt`, `results/prelock_calibration_summary.json`,
`results/calib/`.

## Question
Hold the word frame fixed: the token with its e-runs collapsed, plus run index, line zone, header line,
paragraph-length class, section and scribal hand. Does the choice between one e and a run of 2+ still carry a component
shared across different words at the scale of a folio or a procedure (paragraph)? This is the precondition the two
lean-expert reviews set before any picture test of the human's heat-level reading.

## Result (H track; 5,851 informative e-runs in 80 folios)
| Statistic | Observed | Null mean (SD) | z | p |
|---|---|---|---|---|
| **S3c** (primary: top vs bottom half of a folio, different words, covariate-adjusted) | **+0.323** | −0.002 (0.076) | +4.28 | **0.0005** |
| S3 (unadjusted) | +0.315 | −0.002 (0.074) | +4.30 | 0.0005 |
| **ZL transcription check**, S3c | +0.306 | | | 0.0005 |
| S3-dis (pairs 3+ edits apart) | | | +7.10 | 0.0005 |
| S3-int (token-final runs excluded) | +0.318 | | | 0.0005 |
| S3-cons (runs H and F read alike) | +0.276 | | | 0.0005 |
| S3c-k (runs after k only; 1,858 runs) | +0.259 | | | 0.010 |
| S1 (any folio dependence) | | | +19.1 | 0.0005 |
| **S3far** (first vs last quarter) | +0.095 | −0.001 (0.079) | +1.21 | 0.119 |
| **S3P** (paragraph halves; across-folio null) | | | +5.75 | 0.0005; ZL 0.0005 |
| **S3P-within** (paragraph-specific; within-folio null) | −33.4 | +9.0 | | **0.575** |

- **By stratum:** recipes S/3, S3c +0.347 (p 0.002, 22 folios); biological B/2, +0.328 (p 0.008, 19 folios). The
  other folios reach +0.171 (p 0.17, only 551 runs).
- **Folio propensities** (mean residual, folios with ≥ 30 runs): SD 0.075 (7.5 percentage points), range −0.15 to
  +0.17.
- **Leaf correlation** under frame control: r = 0.26 over 27 recto/verso pairs. That is much weaker than C1977's
  uncontrolled r = 0.665.

## Reading
- **The dial is not just spelling.** Once the word, position, paragraph length, section and hand are held fixed, the
  choice between e and ee still varies in a way shared across different words, at the folio scale.
  - The effect holds on the second transcription.
  - It holds on the runs both transcribers read alike, so it is not legibility.
  - It holds for words that differ in three or more glyphs.
  - It holds after adjusting for folio shape.
  - It holds in the two largest strata independently.
- **Its size** corresponds to a folio-level logit SD of about 0.4 (calibration: σ 0.35 gives mean S3c 0.25, σ 0.5 gives
  0.38), or roughly ±6–7 points around the 20% base rate.
- **It behaves like drift, not a fixed setting.** [Rescoped 2026-09-29 after expert review: unresolved. The ratio
  has SE about 0.22; a uniform constant setting gives S3far this low about 4% of the time and drift 25%. A page
  setting that header or closing lines do not express is not yet excluded. See the variance profile and
  variogram in the next phase.]
  - The first and last quarters of a folio share much less than its two halves do: S3far/S3c = 0.29.
  - In calibration, a constant per-folio setting gave 0.70–0.72 and slow drift within the folio gave 0.33.
  - So the long-e propensity changes gradually down a page; it is not set once per page.
- **There is no procedure-level setting.**
  - Paragraphs of the same folio do not differ from one another beyond the folio's own level (S3P-within p 0.58).
  - "Each procedure has its own heat level" is not supported.
  - The positive S3P reflects the folio-level component.
- **Its source is not identified.** Candidates:
  - content that changes gradually along the page;
  - the writing session or a scribal habit drifting as the page is written (the drift pattern fits this naturally);
  - a pen;
  - an unrecognised hand;
  - copying.

  Legibility, folio shape and exact one-edit copying are controlled. Multi-step copying of the Timm–Schinner kind is
  not excluded: its point estimate was S3c +0.25, though with too few runs to reach significance.
- **The picture gate passed** (S3-dis, S3-int and S3-cons all p ≤ 0.05). A blind picture-coding test is warranted.
  Given the drift, it should code page regions or position-resolved features, not only whole folios.
- **Transcription finding: i-runs are not interpretable** (pre-lock). [Corrected 2026-09-29 by the PHASE_770
  design check: H and ZL agree on minim counts (kappa 0.971, 3,584 units); F is the outlier. Minim statistics are
  usable on H with a ZL check. The text below records what was known at lock.] H and F agree on minim counts with κ = 0.42: F
  reads 879 of H's 1,428 single-minim groups as 2+, and only 8 of 2,124 the other way. The ain/aiin (dain/daiin)
  distinction depends on the transcription. This may be a convention of the older F transcription, which only the scans
  can settle.

## Deviations
- Removing the i-run block from `run_b769.py` after lock brought the script into line with the locked text.
- The ten-highest and ten-lowest folio list was not produced as a separate item. All folio propensities are in the
  JSON; they are descriptive and are not used to select picture-test folios.

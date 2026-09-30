# PHASE_770 — What kind of process sets the e-dial?

**Status: LOCKED** (git tag `phase770-lock`); the run on B follows. The pre-registration is `PRE_REGISTRATION.md`.

**Question.** C2086 found that the e-run dial carries a folio-level component shared across words. PHASE_770 asks four
things:
- **Arm 0:** is the component produced by neighbour context combined with folio vocabulary?
- **Arm A:** is it static on the page or position-dependent?
- **Arm B:** is it shared with other spelling choices (ch/sh, k/t as HEAD, minim count)?
- **Arm C (descriptive):** is it continuous across page turns in the present binding order?

**Design history:**
- **Draft v1** was reviewed by expert-advisor, lean-expert and crazy-expert.
- **Draft v2** merged those reviews (design commit 4d5e204, v7.33). Its checks by lean-expert and expert-advisor found three problems:
  - the class-label classifier's gate fails;
  - two conditioning variables leak outcomes;
  - k/t is not a clean lexical control.
- **Draft v3** fixes them.
  - **Collapsed context and fullness,** with within-folio nuisance effects as plant background.
  - **D14 classes.**
  - **The KTH dial.**
  - **Arm 0** by additive within-folio adjustment.
- **Calibration on controls then changed four parts of the design, all before lock:**
  - **Arm A:** the verdict thresholds were raised to posterior 0.9 and Bayes factor 10; mixtures are gated by their own D14 class; raw features; an S3c applicability window.
  - **Arm B:** the random within-stratum pairing null was anti-conservative under drift (size 0.026 at α 0.01, 1,000 replicates). It was replaced by circular shifts within stratum and a z-scale critical value of 3.2, calibrated under joint H0 plants. The block split was chosen by power under drift.
  - **B3:** critical |z| 3.76, power about 0.06, so it is descriptive.
  - **Arm C:** the per-transition null failed size, so the per-chain null is used. Power under it is 0.06–0.12, so Arm C is descriptive.
- **The lean-expert's lock audit** (LOCK after E1–E6; R1–R9 recommended) was applied in full.
  - C1 and B3 are descriptive.
  - The guardrails now forbid a bounded "not shared".
  - Arm 0 is UNRESOLVED when there is no component.
  - The window is applied to ZL and to the no-flip checks.
  - Classes are frozen from the H81 bank.
  - The gate is evaluated on fresh draws and must evaluate both classes.
  - The lock is verified by tag and bank checksums.
  - A dry run exercised every code path.

**Design-stage checks** (`scripts/design_checks770.py`, `results/design_checks.json`).
- **Minim counts:** H and ZL agree (κ 0.971); F is the outlier (0.42). This corrects the PHASE_769 note (v7.33).
- **ZL line ids:** ZL numbers its loci in one sequence per page, so H–ZL comparisons match lines by content.

**Scripts:**
- **Engine:**
  - `ed770.py`: occurrences for any dial, reproducing PHASE_769 exactly;
  - `cal770.py`: analysis set, plants, statistics;
  - `desc770.py`: descriptives.
- **Arm A:** `bank770.py` (plant bank), `clf770.py` (classifier and gate map), `thr770.py` (threshold scan), `excl770.py` (exclusion list).
- **Arm B:** `calB770.py` (machinery and calibration), `calBj770.py` (joint certification), `calB3_770.py` (B3).
- **Arm 0:** `cal0_770.py`.
- **Arm C:** `calC770.py`.
- **Controls and pilot:** `neg770v3.py` (negative texts; `neg770.py` is the v2 panel), `pilot770.py`.
- **Run:** `run_b770.py`. `--dry` runs it on a poured control.
- `audit/`: the lean-expert's synthetic scripts from the v1 audit.

**Calibration** (`results/calib/`): JSON summaries for every step.
- The plant banks (`.npz`) are gitignored, reproducible from frozen seeds, and verified against `bank_checksums.txt`.
- Dry-run outputs are in `results/dryrun/`.

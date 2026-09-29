# PHASE_770 — What kind of process sets the e-dial?

**Status: DESIGN STAGE (draft v2; not locked).** No statistic under this design has been computed on B.

**Question.** C2086 found that the e-run dial carries a folio-level component shared across words. PHASE_770 asks four
things:
- **Arm 0:** is the component produced by neighbour context combined with folio vocabulary?
- **Arm A:** is it static on the page or position-dependent?
- **Arm B:** is it shared with other spelling choices (ch/sh, k/t, minim count)?
- **Arm C:** is it continuous across page turns in the present binding order?

**History:**
- **Draft v1** was reviewed by expert-advisor, lean-expert and crazy-expert on 2026-09-29.
- **Draft v2 merges the reviews.** Main changes:
  - a pairing null for Arm B (the within-cell null was anti-conservative in the lean-expert's simulation: size 0.073 at
    α 0.01);
  - a joint-frame split key;
  - an expanded plant bank with a fit check and a two-part Bayes factor for Arm A;
  - the paragraph-order test demoted to a veto;
  - Arm C limited to CONTINUITY or UNRESOLVED;
  - Arm 0 (the neighbour-context rival);
  - a guardrail block;
  - f76r included (its H lines carry placement R);
  - f115r assigned hand 3.

**Design-stage checks** (`scripts/design_checks770.py`, `results/design_checks.json`): transcription agreement per dial,
counts, codicology.
- **Minim counts:** H and ZL agree (κ 0.971); F is the outlier (κ 0.42 against H). This corrects the PHASE_769 note;
  the registry annotations were updated in v7.33.
- **ZL line ids:** ZL numbers its loci in one sequence per page, so 421 equal line ids name different lines. H–ZL
  comparisons match lines by content.

**Scripts:**
- `scripts/ed770.py`: the engine, which reproduces PHASE_769's arrays exactly.
- `scripts/design_checks770.py`
- `scripts/audit/`: the lean-expert's synthetic-only simulations for the v1 audit, `sim770.py` and `b2null.py`. They use
  no Voynich data.

**Next steps:**
1. Build the plant bank and calibrate on controls (Idle priority).
2. A lean-expert check of v2 and of the calibration.
3. Lock.
4. Run on B.

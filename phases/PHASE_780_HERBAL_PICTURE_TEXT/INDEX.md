# PHASE_780 — Does the herbal text co-vary with its drawings? (blind picture test, Brunschwig 1500 positive control)

**Status: DESIGN v2 (lean-expert design audit: LOCKABLE AFTER EDITS, all edits incorporated; pre-coding amendments
1–9); locating done; coding in progress; not yet calibrated or locked.**

- **Question.** On the 91 herbal pages written by Davis hand 1 (Currier A), do pages with similar plant drawings carry
  similar text, beyond page position, quire, bifolium, layout, spelling dials, drawing style and length? Positive
  control: the same statistic on the illustrated herbal of Brunschwig's *Liber de arte distillandi de simplicibus*
  (Strasbourg 1500), matched to the Voynich data (reliability, features, page lengths, reused blocks).
- **Pictures** are coded blind by two independent coder sets from masked drawings (`data/codebook_A.md`,
  `data/codebook_B.md`); a locator outlined each Voynich plant (polygons) and boxed each Brunschwig woodcut; reused
  woodcut blocks were confirmed by eye (`data/br_duplicates.json`).
- **Statistic.** Partial correlation of double-centred text similarity (T1 word tf-idf, T2 glyph-trigram tf-idf) and
  double-centred content similarity, given the covariates and drawing style; nulls N-local (exact, within leaf pairs)
  and N-shift; threshold z\* calibrated on four drift generators and anchored writing-session controls.
- **What the outcome can show** is asymmetric (declared): a positive is strong evidence the text is keyed to drawn
  plant form; a genre-powered negative mainly removes form-describing text.
- Pre-registration: `PRE_REGISTRATION.md`. Scripts: `scripts/core780.py` (engine), `scripts/calib780.py` (controls),
  `scripts/run780.py` (locked run), `scripts/build_sets780.py`, `scripts/features780.py`, `scripts/prepare_coding780.py`,
  `scripts/audit_coders780.py`.

## Result
Pending calibration, the confirmation pass, the lock and the run.

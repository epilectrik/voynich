# PHASE_774 — Merged spellings: word- and MIDDLE-level phrase repeats under an exact edge-frame null

**Status:** DESIGN. The draft pre-registration (`PRE_REGISTRATION.md`, v1) is under the lean-expert lock audit.
**No statistic has been computed on Currier B's token order.** B supplied its skeleton, its marginals (for controls
written in B's forms) and its adjacent-token transitions (for the no-message habit generators); see the
pre-registration's exposure section.

## Question (the human's idea)
Could interchangeable spellings hide a message, so that the same thing written twice looks different? If the spelling
variants can be merged, the message's repeated phrases should reappear.

## Done so far (controls only)
- **Stage 1: which merges recover hidden units** (`scripts/prelock_recovery.py`, `results/prelock_recovery*`).
  - A MIDDLE merge recovers a stem code, where spelling varies only in the affix frames.
  - Distributional (exchange) clustering recovers homophones only when every spelling is frequent.
  - Nothing recovers Naibbe-type letter ciphers.
- **An exact null (EF)** replaces PHASE_768's non-converging MCMC: within-folio permutation among positions with the
  same zone and first/last glyph (`scripts/ef774.py`).
- **Power prototypes** (`prelock_power*.py`):
  - Stem codes built on Currier A's forms are easy to see, but their ratios do not transfer to B.
  - Written in B's own forms, a stem code of recipe prose adds no more MIDDLE repeats than B's first-order habits
    already make.
- **Calibration and thresholds** (`prelock_calib*.py`, `prelock_thresholds.py`, `results/thresholds774.json`):
  - T arm (whole-word codes): TOK 5-window excess, τ_T 7.78.
  - M arm (stem codes of repetitive text): MID 5-window ratio, τ_M 7.60.
- **Certification on fresh seeds** (`prelock_cert.py`): PASS.
  - 12/12 held-out whole-word codes detected.
  - 6/6 NT stem codes detected.
  - 0 of 20 fresh no-message runs detected.
  - 0 of 4 twins detected.
- **Dry run of the locked script on decoys:** a whole-word code of Mesue is PRESENT on T; habit3 is NONE on both
  arms.

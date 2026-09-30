# PHASE_774 — Merged spellings: word- and MIDDLE-level phrase repeats under an exact edge-frame null

**Status: LOCKING.** The pre-registration (`PRE_REGISTRATION.md`) is at v3.1, after a lean-expert lock audit (v1 NOT
LOCKABLE), a re-certification on unscored segments (the M arm failed R2, so v3 redesigned it) and a confirmation pass
(LOCKABLE WITH EDITS, applied). **No statistic has been computed on Currier B's token order.**

## Question (the human's idea)
Could interchangeable spellings hide a message, so that the same thing written twice looks different? If the spelling
variants can be merged, the message's repeated phrases should reappear.

## Design history (controls only)
- **Stage 1: which merges recover hidden units** (`prelock_recovery.py`).
  - A MIDDLE merge recovers a stem code.
  - Distributional (exchange) clustering recovers homophones only when each spelling is frequent. It did not merge the
    two-spelling Latin code (k1 0.50).
  - Nothing recovers Naibbe-type letter ciphers.
- **An exact null (EF)** replaces PHASE_768's non-converging MCMC (`ef774.py`).
- **Power prototypes.** Calibration ratios transfer only when the controls are written in B's own marginals.
- **v1 design and certification** (`prelock_calib*.py`, `prelock_cert.py`): superseded, because every run reused one
  segment of each plaintext.
- **The lock audit found v1 NOT LOCKABLE** (`scripts/audit/`, `results/audit/`). Edits E1–E9 went into v2:
  - integer-aware T boundaries (NONE < 4.5, PRESENT ≥ 7.5);
  - per-arm calls;
  - honest scopes;
  - a re-certification on unscored segments, defined before it ran.
- **Re-certification** (`prelock_recert.py`):
  - T arm: every criterion passed (P5 ≥ 12 → PRESENT 31/31; P5 ≥ 8 → not NONE 32/32; no-message runs ≤ 2 windows).
  - M arm: failed R2. A stem code of Latin NT segment 7 came out NONE.
  - **v3 redesign, no re-tuning:** the T arm stays confirmatory, and the M arm becomes one-sided (PRESENT only).
- **Confirmation pass:** LOCKABLE WITH EDITS (E1–E5), applied as v3.1.

## Locked design (summary)
| Arm | Statistic | Calls |
|---|---|---|
| **T** (whole-word codes, confirmatory) | D5, the excess of repeated 5-token windows under EF | PRESENT at D5 ≥ 7.5 with p ≤ 0.01; NONE at D5 < 4.5 or p > 0.05 |
| **M** (stem codes, one-sided) | X5, the ratio of repeated 5-MIDDLE windows | PRESENT at X5 ≥ 7.60 with p ≤ 0.01; otherwise described, with no exclusion claim |

**False-PRESENT bound:** 0 of 102 no-message runs were PRESENT (about 2.9% per arm).

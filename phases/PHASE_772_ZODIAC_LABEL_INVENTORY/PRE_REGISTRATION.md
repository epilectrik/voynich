# PHASE_772 — Do the zodiac labels form a shared per-sign inventory (a numeral-type crib)?

**Status: LOCKED at the git tag `phase772-lock`.** This is v2, after the lean-expert lock audit ("lockable with edits")
and its confirmation pass (four further edits). All edits are applied. The blinding disclosure below is part of the
lock.

## Blinding disclosure (required by the audit)
**The smoke calibration was not blind.**
- The first smoke run (`results/cal772_v1_smoke_LEAK_DISCLOSED.json`, written 2026-09-30 08:57) built its palette model
  from each sign's real labels.
- Its printed palette medians of R are therefore close to a direct readout of the real cross-sign recurrence: N0
  0.066, N1 0.097, N2 0.138. Its inventory-model W at λ = 0 likewise reflects real within-sign duplicates.
- Claude saw these numbers before the rules were finalised.
- The v1 draft of this file (08:58) and of `run772.py` (08:58) were edited after that smoke file. The phase was
  untracked, so git cannot show that the rules predate it.

**The leak covers the W channel as well as R.** The leak file also holds W medians and W-test power for both models
built from real labels. So PALETTE and the W clause of NO INVENTORY are partly unblinded too.

**The R side is effectively unblinded.** The smoke N2 palette R (0.138) is below every final 1st-percentile threshold
(the lowest is 0.638, at λ = 8). A NO INVENTORY with λ* = 8 was therefore foreseeable before the run. The extended λ
grid (up to 8) came from the audit, not from Claude.

**What was done about it.**
- The full calibration now draws all base forms from Currier A paragraph words, not from the labels. Only the sign
  sizes come from the labels.
- Report NO INVENTORY and PALETTE as **partly unblinded** measurements, not as blind confirmations.

## Why
**The zodiac pages are the manuscript's most table-like section.**
- There are ten signs, identified by their pictures and by month names written in Roman script on the pages.
- Each sign has 29–30 labelled figures in two or three rings, with Aries and Taurus split over two pages.
- ZL gives each label's clock position.

**A shared inventory would be the classic entry point.** If the labels are degree or day numbers (1–30), or any small
shared vocabulary not repeated within a page, the same set of forms recurs in every sign. That would be a numeral-type
crib: known meanings at known places.

**Prior rows.** C319 (placement templates), C431, C759 and DATA/ZODIAC_ICONOGRAPHIC_MAP. No row tests recurrence of
label forms across signs as a per-sign set.

## Data
- **Source:** ZL 3b.
- **Pages and signs:**

  | Page(s) | Sign |
  |---|---|
  | f70v2 | Pisces |
  | f70v1 + f71r | Aries |
  | f71v + f72r1 | Taurus |
  | f72r2 | Gemini |
  | f72r3 | Cancer |
  | f72v3 | Leo |
  | f72v2 | Virgo |
  | f72v1 | Libra |
  | f73r | Scorpius |
  | f73v | Sagittarius |

- **Labels:** every Lz locus with a clock position. The Pisces central label, which has none, is excluded.
- **Form:** the label's words joined. Alternative readings `[a:b]` take the first reading (17 labels). Labels with
  unreadable glyphs are excluded from the statistics (8 labels).
- **Counts:** 290 labels: Pisces 28, Aries 30, Taurus 30, Gemini 29, Cancer 28, Leo 29, Virgo 30, Libra 27, Scorpius 30,
  Sagittarius 29.
- **Rings:** ring membership is the ring text that precedes the label. Ring 0 is the short top-row arcs on Gemini,
  Scorpius and Sagittarius (13 labels).

## Normalisations
- **N0:** raw. **Descriptive only.**
- **N1:** the free-variation layer collapsed: runs of e become one e, and runs of i become one i.
- **N2:** maximal collapse. N1 plus sh → ch, benched gallows → ckh, and t/p/f → k.

N2 is generous to an inventory, since it merges forms that may be distinct. The nulls use the same level.

## Statistics
- **R:** the share of labels whose normalised form occurs in at least one other sign.
- **D_w, D_a, W:** within- and across-sign pairs of labels sharing a form; W = D_w / (D_w + D_a).
  - Exchangeable E[W] = 0.097.
  - A per-sign inventory drives W toward 0; a sign-specific palette drives W toward 1.
- **Null for W:** labels permuted across signs with sign sizes fixed, 10,000 permutations.
  - D_w + D_a is invariant under relabelling, so this is an exact conditional test of D_w.
  - One-sided p is reported in both directions, with the smallest attainable p at each level. p = 1 if W is undefined.
- **R_words:** conservative word-level recurrence. A label recurs if any of its words (split at definite spaces)
  occurs among the words of another sign's labels. Joining multi-word labels can only push toward NO INVENTORY; this
  guards against that.

## Verdicts (pre-registered)
| Verdict | Rule |
|---|---|
| **INVENTORY** | W below the null (one-sided p < 0.01) at both N1 and N2, **and** R(N2) ≥ the inventory model's 5th percentile at λ = 3 |
| **NO INVENTORY (bounded)** | not INVENTORY, **and** W not significantly low at N1 **and** not at N2, **and** λ* ≥ 1 |
| **PALETTE** | W above the null (one-sided p < 0.01) at N1 **and W not low at N2**. Sign-level (Aries and Taurus span two pages each) |
| **UNRESOLVED** | none of the above. This includes W low at only one of N1 and N2, a possible shared subset |

- **λ\*** is the largest λ in {0, 0.5, 1, 2, 3, 5, 8} such that R(N2) and R_words(N2) are both below the inventory
  model's 1st percentile at that λ **and at every smaller λ**.
- λ = 0 is degenerate (its 1st percentile is 1.0), hence the requirement λ* ≥ 1.
- **Co-occurrence:** only NO INVENTORY + PALETTE can occur together.
- **Multiplicity:**
  - INVENTORY is an intersection-union test over N1 and N2.
  - PALETTE is a single test.
  - NO INVENTORY is a nested test inversion.
  - The combined false-call rate is at most about 0.03. N0 is descriptive.

## The simulation models (calibration)
- **Base pool:** 5,773 Currier A paragraph tokens (2,768 types) of 4–8 glyph units (ZL), not the labels.
- **Pure inventory:** one base form per position, shared by all signs. Each sign's label is a copy with Poisson(λ)
  attempted spelling-variant edits:
  - e-run ±1;
  - minim-run ±1;
  - ch ↔ sh;
  - a gallows among k, t, p, f;
  - the initial o/y/q;
  - the ending among -y/-dy/-ey and -l/-r/-m.
- **Attempted edits include no-ops.** The share of copies visibly changed at N2 is output per λ; only initial and ending
  edits survive N2. The bound is stated as "copies up to X% visibly changed at N2, plus any e-run, minim, ch/sh or
  gallows variation".
- **Mixtures:** an inventory share φ ∈ {0.25, 0.5, 0.75}. The remainder is either palette draws (8 sign-specific base
  forms, λ = 1) or random Currier A words (token-weighted, drawn with replacement; labelled "unique" in the code).
- **Also calibrated:** a pure palette model and pure random words.
- **Simulation counts:** 2,000 R-only simulations per λ for the thresholds (unrounded), 100 per λ for the W rule, 40 per
  mixture, and 200 / 100 for the pure palette and unique-form models.

## Interpretation (fixed now)
- **INVENTORY:** the labels behave like a repeated per-sign set, as numerals would, or any small shared vocabulary not
  repeated within a page.
  - The next step is a separate pre-registered positional test (do recurring forms sit at matching positions?), which
    could give a numeral crib.
- **NO INVENTORY (bounded):** scoped to **full** inventories and the modelled variant kinds. A full per-sign set whose
  copies are up to X% visibly changed at N2 is excluded. The test does **not** exclude:
  - partial inventories (the mixture rows say how partial);
  - affixed or sign-specific forms;
  - two-word numerals;
  - medially varied numerals;
  - transcription error.
- **PALETTE:** label forms are shared within a sign more than across signs. This is **consistent with** the page-level
  vocabulary of the running text (C531).
- **None of these reads meaning.**
- **Limits:**
  - one primary transcription (ZL; H is a descriptive replication);
  - the edit model is a guess;
  - every label in the inventory model is a copy.
- **Sign-specific affixes are out of reach.** R and W have no power against a numeral system with sign-specific
  affixes. The first-unit-stripped descriptive bears only on a sign-constant first unit.

## Descriptive (no verdict)
- W by page (12 pages).
- R and W without the 13 top-row labels.
- R and W on N2 forms with the first glyph unit stripped.
- H-track replication (H placement S labels).
- **Adjacency similarity (N1):**
  - within each ring or arc, labels are ordered by clock position linearly from the largest gap (no wrap);
  - adjacent readable pairs that do not straddle an unreadable label are compared with other within-ring pairs;
  - null: labels permuted within rings (2,000 permutations);
  - effect = observed minus null mean.
- The 12 most frequent forms at each normalisation, with the number of signs each occurs in.

## Calibration
**Final calibration, binding.** `scripts/cal772.py`, seed 7721, base pool 5,773 Currier A tokens (2,768 types) of 4–8 glyph units, real sign sizes, runtime 2,185 s. Output: `results/cal772.json`, with unrounded thresholds.

| λ (attempted edits) | Copies visibly changed at N2 | R(N2) 1st pct | R(N2) 5th pct | INVENTORY rule rate (pure inventory) |
|---|---|---|---|---|
| 0.0 | 0.000 | 1.0000 | 1.0000 | 1.00 |
| 0.5 | 0.125 | 0.8828 | 0.8931 | 1.00 |
| 1.0 | 0.229 | 0.8414 | 0.8586 | 1.00 |
| 2.0 | 0.390 | 0.7931 | 0.8103 | 1.00 |
| 3.0 | 0.508 | 0.7552 | 0.7724 | 0.95 |
| 5.0 | 0.657 | 0.6966 | 0.7172 | 0.37 |
| 8.0 | 0.769 | 0.6379 | 0.6619 | 0.10 |

| Mixture (λ = 1) | Verdict distribution |
|---|---|
| phi0.25_palette | NO INVENTORY (bounded, lam* = 8.0) + PALETTE 1.000 |
| phi0.25_unique | NO INVENTORY 0.775; UNRESOLVED 0.225 |
| phi0.5_palette | NO INVENTORY (bounded, lam* = 8.0) + PALETTE 0.975; NO INVENTORY 0.025 |
| phi0.5_unique | UNRESOLVED 0.975; NO INVENTORY 0.025 |
| phi0.75_palette | UNRESOLVED 0.975; NO INVENTORY 0.025 |
| phi0.75_unique | UNRESOLVED 0.975; INVENTORY 0.025 |
| pure palette | NO INVENTORY (bounded, lam* = 8.0) + PALETTE 1.000 |
| pure unique forms | NO INVENTORY 0.970; UNRESOLVED 0.020; NO INVENTORY (bounded, lam* = 8.0) + PALETTE 0.010 |

**Reading the mixture rows:**
- NO INVENTORY excludes **full** per-sign inventories up to λ* (the visibly-changed share at λ* is in the table).
- At λ = 1, three-quarter inventories give UNRESOLVED in 39 of 40 runs. φ = 0.75 is not calibrated at larger λ.
- It does **not** exclude a half inventory whose remainder is palette-like: φ = 0.5 + palette gives NO INVENTORY +
  PALETTE in 39 of 40 runs. Nor does it exclude a quarter inventory.

**Random words** (token-weighted Currier A) give NO INVENTORY in 98% of runs (97% alone).

**The PALETTE rule change** ("and W not low at N2", confirmation pass) needs no recalibration. No calibrated outcome
had PALETTE without NO INVENTORY, and NO INVENTORY already requires W not low at N2.

**Dry run** (`results/dryrun/`): decoy labels, i.e. random Currier A words at the real positions.
- NO INVENTORY (λ* = 8).
- W 0.093 at N1 against an exchangeable 0.097.
- No PALETTE; every code path ran in 83 s.

## Run procedure
1. `python scripts/run772.py --checksums`.
2. Commit the phase, including the audit scripts in `scripts/audit/`, and tag `phase772-lock`.
3. `python scripts/run772.py` at Idle priority. It verifies:
   - that every locked file is in the tag and unchanged;
   - that there are no untracked scripts;
   - the input checksums.
4. Commit the raw results before interpretation. `run772.py --dry` exercises every path on decoy labels.

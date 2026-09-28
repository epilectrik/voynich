# PHASE_764 — Does human-improvised gibberish reach Currier B's cross-word coupling? (pre-registration)

**Status:** LOCKED v2 (2026-09-28), before any statistic was computed on gibberish or meaningful text.
- The lean-expert design audit of v1 returned LOCK WITH CHANGES. Edits E1–E10 are incorporated; deviations are listed
  at the end.
- The B-only pre-lock checks (E2) were run on B data only: `scripts/prelock_b_checks.py` →
  `results/prelock_b_checks.json`.

**Origin:** RESEARCH_AGENDA Tier A #1, human-approved 2026-09-28.
- The algorithmic meaningless rival (Timm & Schinner self-citation) is excluded (C2077).
- Human-improvised gibberish has never been run against our measurements.
- Gaskell & Bowern 2022 (38 volunteers) report that gibberish matches Voynichese on repetition, placement bias,
  word-length autocorrelation and Zipf fit. They did not measure cross-word coupling (C1212/C1563).

**Question:** does human-improvised gibberish reach B's coupling between the last unit of a word and the first unit of
the next, at matched folio scale?

**Scope:** folio scale (about 200–400 within-line pairs), low-level structure only. The volunteers are modern and wrote
in Latin letters; improvising fluently in a practised script is untested. **Neither outcome changes the Tier-0
sentence.**

**Change control:** after lock nothing below may change without a new phase number.

## Data
- **B (primary): ZL 3b, Currier B, `P` placement.**
  - Word boundaries: definite spaces only. Tokens separated by an uncertain space are merged (PHASE_761).
  - Sensitivities: ZL with all spaces as boundaries, and the H track.
  - Units: PHASE_754 glyph units (`c[tkpf]h|[cs]h|i+[nrlm]|.`, raw).
  - V1 sensitivity: EVA characters.
- **Gibberish (G):** Gaskell & Bowern's 38 transcriptions (`external/gaskell-bowern`, modified MIT, git-ignored).
  - Lines as transcribed; lines with no letters dropped.
  - Words: whitespace tokens, NFD-normalised, lower-cased, alphabetic code points only.
  - Units: letters.
- **Meaningful (M):** Gaskell & Bowern's 71 meaningful texts, cleaned the same way. Every text has ≥ 542 pairs.
- **No bridging (all corpora):** a pair is formed only between two adjacent retained tokens. A token dropped for any
  reason (unreadable, letterless, empty after cleaning, a drawing interruption `<->`) splits its line. The split
  pieces are the "segments" within which pairs are formed and shuffles run.
- **Line-break provenance (E9):** the repository does not record whether each sample's line breaks were the writer's.
  S3 is therefore descriptive only, and is not computed for M.

## Matching
Every statistic is computed on each G sample at its own size, P_i within-segment pairs.
- **B reference:** 200 chunks of exactly P_i pairs each (seed 764).
  - A chunk starts at a random segment of a random B folio, chosen in proportion to its pairs.
  - It takes consecutive segments within the same section, crossing folios where needed, and truncates the last one.
  - The share of chunks that cross a folio is reported. A single-folio-only reference is run as a sensitivity.
- **M reference:** one chunk of P_i pairs from each of the 71 texts, starting at a seeded random segment.
  - Each chunk is re-wrapped to line lengths drawn from the paired G sample's line-length distribution (E8).

## Statistics
All statistics use plug-in MI in bits, minus the mean of 200 permutations of word order within each segment.

| Name | Definition | Role |
|---|---|---|
| **S1 boundary coupling** | I(L1(t); F1(t+1)): last unit of word t vs first unit of word t+1 | **primary (the only one)** |
| S2 ending routing | I(L2(t); F1(t+1) \| L1(t)), where L2 = the penultimate unit, or `#` for one-unit words | secondary (E3; power fails, below) |
| S3 positional zone | I(F1(t); zone), with zone ∈ {first, medial, last} in the segment | descriptive (E9) |
| S4 adjacent repetition | log((O+0.5)/(E+0.5)) for identical adjacent words | descriptive |

**Also reported per sample:**
- the near-repeat rate: the share of adjacent pairs at edit distance ≤ 1;
- the pair-weighted E[1/n]: the adjacency that the within-segment shuffle keeps;
- H(F1).

**S2 is new.** It is not C2082's verdict statistic: C2082 conditioned on t's first glyph and targeted t+1's class, and
placing the signal in the ending was a post-hoc decomposition.

## Pre-lock B-only results (E2, recorded before lock)
- **Full-B S1:**
  - ZL, merged spaces: 0.204 bits.
  - ZL, all spaces: 0.245 bits (PHASE_761: 0.243).
  - H: 0.228 bits (C1212: 0.228).
  - The pipeline reproduces the registered values. The merged-space figure is below PHASE_761's 0.215 because the null
    here is the within-segment shuffle.
- **Full-B S2 (ZL, merged spaces):** raw excess 0.0086 bits; top-4 binned 0.016.
- **Power** (share of B chunks beating their own shuffle null at p ≤ 0.05; ZL, merged spaces):

| P (pairs) | 100 | 150 | 224 | 300 | 400 |
|---|---|---|---|---|---|
| S1 raw | 0.435 | 0.635 | 0.895 | 0.995 | 0.995 |
| S1 top-6 | 0.70 | 0.885 | 0.965 | 0.99 | 1.0 |
| S2 raw | 0.025 | 0.0 | 0.01 | 0.005 | 0.0 |
| S2 top-4 | 0.095 | 0.11 | 0.24 | 0.32 | 0.42 |

- **Consequences:**
  - S1 is certified for power (i).
  - S1 power crosses 80% at about 197 pairs, so G samples with fewer than 197 pairs are excluded from S1: 23 of 38
    remain (≥ 20 required).
  - S2 fails the 80% requirement and is secondary (E3). It is reported as the pair-weighted mean of per-sample S2
    over the included G samples, placed in the distribution of that mean over 200 matched sets of B chunks.

## Certification of S1 (all four required before any G statistic on real word order is computed)
- **(i) Power:** met, from the pre-lock results.
- **(ii) Positive control:** 23 single-folio B pseudo-samples at the G sizes, each scored against reference chunks from
  other folios, must return REPRODUCED.
- **(iii) Negative control:** the G samples with their words shuffled within segments must return NOT REPRODUCED.
- **(iv) Resolution:** the positive-control bootstrap CI half-width must be ≤ 0.15; see deviation D1.

If any of (ii)–(iv) fails, S1 is uncertified and the verdict is UNINFORMATIVE AT THIS SIZE.

## Comparison and per-statistic rule (E6)
- **AUC_BG:** P(B chunk > G sample) at matched size. For each G sample, the fraction of its B chunks exceeding it
  (ties count ½); then the mean over G samples.
- **AUC_MG and AUC_BM:** the same comparison for the other two pairings.
- **95% CI:** 1,000 bootstrap resamples of the G samples, with B chunks resampled in folio blocks (by start folio).
- **Outcome:**
  - **NOT REPRODUCED:** the AUC_BG lower bound ≥ 0.80.
  - **REPRODUCED:** the CI lies within [0.30, 0.70].
  - **EXCEEDED:** the upper bound < 0.30, meaning gibberish is stronger than B.
  - **UNRESOLVED:** anything else.

## Robustness variants (E5)
The S1 label stands unless any variant returns the opposite definite label, in which case it becomes UNRESOLVED.

| Variant | Change |
|---|---|
| V1 | B in EVA characters |
| V2 | top-k binning: per chunk, the 5 commonest units plus OTHER (k = 6), for B, G and M alike |
| V3 | segment-matched null: B segments are cut into consecutive pieces with lengths drawn from the paired G sample's segment-length distribution; pairs across the cuts are dropped from both observed and null |
| V4 | edge-fixed shuffle: first and last word of each segment held in place |
| V5 | S1 divided by the chunk's plug-in H(F1) |

"Opposite" means NOT REPRODUCED against REPRODUCED or EXCEEDED.

## Overall verdict (E7) and registry consequences (E10)
| Verdict | Condition | Registry action |
|---|---|---|
| **B-DISTINCT** | S1 certified and NOT REPRODUCED | Tier-2 row: "At folio scale (≈200–400 within-line pairs), Currier B's boundary coupling exceeds improvised gibberish written by modern volunteers in Latin letters (Gaskell & Bowern 2022). Not evidence of meaning or of the control-program reading; improvisation in a practised script is untested." STATUS_BRIEF §4 lists human gibberish as excluded with this scope. |
| **GIBBERISH-COMPATIBLE** | S1 certified and REPRODUCED, or EXCEEDED with V2 and V5 agreeing | Tier-2 row: "Currier B's folio-scale boundary coupling lies within the range of modern improvised gibberish; this does not show B is meaningless." STATUS_BRIEF notes that boundary coupling is not diagnostic against improvisation at folio scale. |
| **MIXED / UNRESOLVED** | S1 certified, label UNRESOLVED | Phase record only; STATUS_BRIEF §4 reads "tested at folio scale, unresolved". |
| **UNINFORMATIVE AT THIS SIZE** | S1 not certified | Phase record only. |

**Floor rule (E8):**
- If S1 is NOT REPRODUCED and the lower bound of AUC_BM is also ≥ 0.80, the row states that B exceeds both human
  gibberish and human meaningful text on S1, so the contrast is not specific to meaninglessness.
- If AUC_BG and AUC_BM are both in the REPRODUCED band, the row states that human-written text in general reaches
  this level at this size.

**Descriptive only:** J_G and J_M (the share of samples inside B's 5–95% band), S2, S3, S4, the near-repeat rate,
E[1/n] and H(F1).

## Deviations from the audit
- **D1:** (iv) is set at ≤ 0.15, not 0.05. With n included G samples, a positive-control AUC whose per-sample
  percentiles are uniform has a 95% half-width of about 1.96 × 0.289/√n: 0.12 at n = 23. A 0.05 requirement would
  fail by construction. At ≤ 0.15, both definite labels remain reachable.
- **D2:** primary B is ZL with uncertain spaces merged, because the H track records no spacing. H and ZL with all
  spaces are sensitivities. The audit's E1 asked for definite-spaces B, and the H track cannot supply it.

## Outputs
`results/gibberish_control.json`, `results/run_log.txt`. Script: `scripts/gibberish_control.py`, using `scripts/g764.py`.

# Phase 672: PREFIX Positional Role on Fixed Frame

**Status:** COMPLETE
**Started:** 2026-05-01
**Goal:** Test whether PREFIX class carries within-line positional information beyond frame composition, articulator, LATE-class, and line-zone effects.

## Context (Origin Trail)

Phase 671 found that 4/5 a-HEAD r-TERM tokens share a bimodal line-position class profile (C1982), with okar (BC=0.490) as the lone outlier. Investigating okar revealed broader patterns: ok-prefix tokens are flat across most terminals, while sh, yk, te appear start-loaded, ot/ol/no_prefix end-loaded.

Both experts flagged the broad observation as likely confounded:
- C1426 (SPECIFICATION zone Q0 of every line) → would explain start-loading generically
- C539 (LATE-class al/ar/or end-loaded 3.78x) → would explain (no_prefix) end-loading
- C1417 (y-articulator PREFIX-LOCKED line-initial) → would explain yk start-loading
- C1808 (section significantly affects 13/14 PREFIX fractions, qo η²=0.60) → section confound

**Crazy-expert's discriminating test:** Hold HEAD+TERM frame fixed at e→y (the highest-power frame per C1457, n>3000), exclude articulators, vary only PREFIX. If different prefixes show different positional distributions, prefix carries independent info. If identical, prefix is passive (and the broad observation reduces to known constraints).

## Findings

### Descriptive (Currier B body-only, e→y frame, articulators excluded)

| Prefix | n | Mean | BC | Skew |
|--------|---|------|-----|------|
| ch | 1133 | 0.521 | 0.556 | +0.03 |
| **sh** | **783** | **0.433** | 0.564 | **+0.33** |
| ok | 377 | 0.508 | 0.485 | +0.02 |
| ot | 313 | 0.541 | 0.525 | -0.24 |
| lch | 176 | 0.497 | 0.598 | +0.20 |
| lk | 123 | 0.511 | 0.538 | +0.11 |
| yk | 97 | 0.411 | 0.580 | +0.18 |
| ke | 73 | 0.502 | 0.595 | +0.08 |
| lsh | 68 | 0.375 | 0.581 | +0.55 |

### Control 1: Paragraph-line ≥ 3 (header-leakage filter)

Skip first 2 lines of each paragraph (C1819 shows header signal extends through position-2):

| Prefix | n | Mean | BC | Skew |
|--------|---|------|-----|------|
| ch | 601 | 0.530 | 0.550 | -0.01 |
| **sh** | **476** | **0.430** | 0.583 | **+0.40** |
| ok | 183 | 0.537 | 0.475 | -0.07 |
| ot | 140 | 0.518 | 0.525 | -0.08 |

sh's start-loading STRENGTHENS under stricter para-position filtering. Not paragraph-leakage.

### Control 2: Section Stratification

| Section | Prefix | n | Mean | BC |
|---------|--------|---|------|-----|
| H (Herbal) | ch | 165 | 0.530 | 0.597 |
| H (Herbal) | sh | 66 | 0.379 | 0.682 |
| B (Biological) | ch | 414 | 0.527 | 0.552 |
| B (Biological) | sh | 440 | 0.450 | 0.558 |
| S (Stars) | ch | 499 | 0.510 | 0.556 |
| S (Stars) | sh | 241 | 0.411 | 0.557 |

sh is start-loaded in all 3 major sections. ch is flat in all 3. Not a section artifact.

### Permutation Test (formal)

Within-line label shuffles (10,000 permutations). For each line containing ≥1 sh-e→y or ch-e→y token, randomly relabel the prefixes preserving counts; compute the resulting sh-mean vs ch-mean difference.

| Filter | n_sh | n_ch | sh_mean | ch_mean | Diff | p-value |
|--------|------|------|---------|---------|------|---------|
| Body-only | 783 | 1133 | 0.433 | 0.521 | -0.088 | **0.0000** |
| Para-line ≥ 3 | 476 | 601 | 0.430 | 0.530 | -0.101 | **0.0001** |

The actual sh-vs-ch positional difference is more extreme than essentially any within-line random labeling.

## Verdict

**PREFIX carries within-line positional information beyond frame composition, articulator, LATE-class, and line-zone effects.** The discriminating test (frame held fixed at e→y) showed that sh-prefix is start-loaded (mean=0.433) while ch-prefix is flat (mean=0.521), with the difference surviving paragraph-leakage control, section stratification, and within-line permutation testing.

Crazy-expert's bet was 70% null after controls. Wrong on this test — the sh-vs-ch positional difference is real and robust.

## Constraint Updates

### C1983 (Tier 2): sh-prefix and ch-prefix differ in within-line position on fixed e→y frame

Currier B body-only, e→y frame (HEAD=e, TERM=y, no articulator):
- **sh-e→y** start-loaded: mean = 0.433 (n=783)
- **ch-e→y** flat: mean = 0.521 (n=1133)
- **Diff** = -0.088, p = 0.0000 (within-line permutation 10k)

Survives:
- Paragraph-line ≥ 3 (controls C1287/C1819 header register): diff = -0.101, p = 0.0001
- Section stratification (H, B, S): sh start-loaded in all 3, ch flat in all 3
- Articulator exclusion (controls C1417 y-articulator effect)
- LATE-class exclusion via no_prefix removal (controls C539)
- Frame held fixed at e→y (controls C1457 frame-composition effects)

PREFIX carries positional information beyond frame composition (HEAD/TERM identity), articulator presence (C1417), LATE-class membership (C539), and line-zone effects (C1426). The sh-prefix specifically is start-loaded; ch-prefix specifically is flat — same exact frame, different positional bias.

**Tier:** 2 (Currier B grammar)

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_prefix_position_ey_frame.py | Descriptive + paragraph-leakage control + section stratification + 10k permutation test | ~2 min |

## Relationship to Existing Constraints

- **C929** (sh = passive monitor, ch = active test): C1983 adds positional dimension to the semantic distinction. Passive monitoring tends to start lines (early observation register?); active testing distributes flat.
- **C1287/C1288** (header-line PREFIX enrichment): Controlled. sh start-loading is NOT a header artifact — strengthens after header removal.
- **C1417** (y-articulator PREFIX-LOCKED line-initial): Controlled. Articulators excluded from analysis.
- **C539** (LATE-class al/ar/or end-loaded 3.78x): Different prefix class. C1983 is on e-HEAD y-TERM frame which excludes a-HEAD r-TERM LATE class.
- **C1426** (SPECIFICATION zone Q0 of every line): Would predict generic start-loading for all prefixes. C1983 shows differential start-loading (sh vs ch) — not a generic line-zone effect.
- **C1808** (section significantly affects 13/14 PREFIX fractions): Controlled by section stratification — sh start-loaded in H, B, AND S.
- **C1457** (e→y frame highest-power frame): C1983 leverages this frame for power. PREFIX-positional effects on lower-power frames remain to be tested.
- **C1218-C1220** (intra-PREFIX positional grammar): Different scope. C1983 is at PREFIX-class level (within line); C1218 is at character level (within prefix).
- **C1001** (PREFIX dual encoding: content + line position): C1983 directly extends — provides quantified evidence of the position-encoding component.
- **C1982** (a-HEAD r-TERM bimodal class): C1983's discrimination (sh vs ch flat/start) shows that bimodality is one of several PREFIX-positional shapes. Different prefix classes have different shapes.

## Suggested Follow-up

- **Per-pair permutation tests** for ot vs ch (end-leaning vs flat), ok vs ch (flat vs flat), lsh vs sh (more start-loaded vs start-loaded)
- **Other frames:** Replicate the e→y test on k→y, t→y, and other frames with sufficient sample
- **PREFIX positional taxonomy:** With more pairs validated, claim a 3-4 class taxonomy (start-loaders / flat / end-loaders / bimodal interior)
- **Semantic alignment:** Test whether the positional shapes align with PREFIX glosses (sh="observe/begin" → start-loaded; ot="complete/end" → end-loaded; ok="correct" → flat)

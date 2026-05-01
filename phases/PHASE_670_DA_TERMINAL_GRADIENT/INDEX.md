# Phase 670: da-Prefix Terminal-Atom Positional Gradient

**Status:** COMPLETE
**Started:** 2026-05-01
**Goal:** Test whether terminal atoms within the da-prefix family carry distinct positional roles (line-internal placement bias) beyond the universal -m line-final pattern (C1486).

## Findings

Within the da-prefix family, terminal atoms encode a positional gradient. Tokens with the same prefix (da) sort to systematically different positions in their lines depending on which terminal atom closes them. The gradient is structural (10,000-shuffle permutation tests pass at p < 0.01 for 5 of 6 tokens) and persists under 4 kill tests (bimodality, body-only, dam-adjacency, folio-permutation).

A separate finding: dar, despite a near-uniform mean position (0.507), is bimodal — concentrating at line edges and avoiding the middle (decile distribution 13.3, 6.4, 11.7, 8.0, 6.9, 8.5, 8.0, 11.7, 12.2, 13.3; bimodality coefficient 0.581).

### C1979: PREFIX-conditional terminal-atom positional gradient (da family)

Within the da-prefix family in Currier B, terminal atoms encode position-of-line role at significance levels far beyond chance. The gradient distinguishes early-position tokens (-iin, -in, -ir), an end-anchored token (dal with -l), and a strict line-final token (dam with -m, also covered by C1486).

| Token | N | Mean position | Start% | Mid% | End% | Permutation p (within-line) | Folio-permutation p |
|-------|---|---------------|--------|------|------|------------------------------|---------------------|
| daiin | 310 | 0.413 | 45.8% | 27.4% | 26.8% | 0.0000 | 0.0000 |
| dain | 113 | 0.421 | 43.4% | 27.4% | 29.2% | 0.0077 | 0.0060 |
| dair | 49 | 0.345 | 51.0% | 20.4% | 28.6% | 0.0005 | 0.0000 |
| dar | 188 | 0.507 | 33.5% | 29.3% | 37.2% | 0.7533 (n.s.) | 0.7430 (n.s.) |
| dal | 130 | 0.618 | 19.2% | 33.8% | 46.9% | 0.0000 | 0.0000 |
| dam | 42 | 0.861 | 9.5% | 4.8% | 85.7% | 0.0000 | 0.0000 |

**Direction of gradient:** -ir/-iin/-in (early) → -l (late) → -m (final).

**Length control:** dar/dal/dam are all 3 chars; daiin is 5; dain/dair are 4. Length does not predict position (3-char dam is final, 5-char daiin is early).

**Cross-system check:** In Currier A the gradient compresses (dair=0.506, daiin=0.578, dair to dam range narrows), consistent with weaker grammatical organization in A.

**Tier:** 2 (B grammar)

### C1980: dar bimodal line-position distribution (observation)

Despite a mean position of 0.507 — superficially "uniform" — dar's line-position distribution is bimodal, concentrating at line edges and avoiding the middle.

| Metric | Value |
|--------|-------|
| N | 188 |
| Mean | 0.507 |
| Std | 0.320 |
| Variance / uniform-expected | 1.23 |
| Decile distribution (start→end, %) | 13.3, 6.4, 11.7, 8.0, 6.9, 8.5, 8.0, 11.7, 12.2, 13.3 |
| Bimodality coefficient | 0.581 (threshold 0.555) |
| Skew / kurtosis | -0.106 / 1.741 |

**This is registered as an observation, not an interpretation.** Possible mechanisms (clause-edge marker, deployment artifact, mixed populations) are not adjudicated here. The mean-position permutation test does not detect this — it requires a distributional test.

**Tier:** 3 (B observation, pending mechanistic test)

## Controls Passed

| Control | Purpose | Result |
|---------|---------|--------|
| Within-line permutation (10k) | Random-position null | All 5 non-dar tokens p < 0.01 |
| Folio-level permutation (10k) | Across-line null robustness | Matches within-line test |
| Body-only (excl. line-1) | Paragraph-initial enrichment confound | Means change by < 0.013 — gradient persists |
| dal-dam adjacency | Is dal-late driven by dam co-occurrence? | dal-with-dam: n=1 (effectively absent). dal-without-dam mean=0.616 — gradient is not adjacency-driven |
| Length control | Short tokens drift to edges? | Length and position uncorrelated within family |
| Bimodality decomposition | "Uniform" hides U-shape? | Confirmed for dar — registered separately as C1980 |

## Relationship to Existing Constraints

- **C1486** (m-terminal line-final closure): C1979 cross-references this directly. dam (mean=0.861, 85.7% line-final) is the m-terminal manifestation within the da family — fully consistent with C1486's universal claim that -m is the line-final marker (mean=0.914, 88.8% line-final across all 578 -m tokens corpus-wide).
- **C1925** (dar = material introduction): C1979/C1980 do not contradict C1925. dar's bimodality is positional, not semantic — material introduction can occur at either start-of-line (new step) or end-of-line (closing operation of previous step).
- **C1394** (HEAD+MOD*+TERM atom model): C1979 is direct evidence that TERM atoms carry positional information beyond their structural role.

## Non-Claims (explicit)

This phase does NOT claim:
- That -l is a "near-final" marker corpus-wide (only tested within da family)
- That -iin/-in/-ir are "early-position" markers corpus-wide
- That dar's bimodality reflects clause structure (untested)
- That the da-family gradient generalizes to other prefix families (qo, ch, sh, ok, ot remain to be tested)

These are candidate hypotheses for follow-up phases.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_da_terminal_position.py | Da-family position stats + within-line permutation + cross-system | ~2 min |
| s2_da_kill_tests.py | Bimodality, body-only, dal-dam adjacency, folio-level permutation | ~3 min |

## Suggested Follow-Up Phases

- **Replication:** Test the same gradient on qo/ch/sh/ok/ot prefix families. If the pattern is general (PREFIX-conditional terminal-role gradient), promote to a corpus-wide claim.
- **Bimodality mechanism:** Test whether dar's edge-concentration co-occurs with bare-token clustering or other clause-edge signatures. Pre-register a joint hypothesis about line-internal clause structure.

# Phase 690: AZC Annotation-Transcript Systematic Diff

**Status:** COMPLETE — 2 constraints registered (C2004 audit summary, C2005 nymph-page center systematic gap)
**Started:** 2026-05-07
**Completed:** 2026-05-07
**Goal:** Build a systematic per-folio diff between user manual annotations (13 files, ~28 folios) and H-track transcript encoding for AZC diagrams. Quantify and categorize discrepancies. Identify specific candidate transcript errors warranting follow-up.

## Result summary

**26 annotated AZC folios audited.** 20 of 26 (77%) flagged with non-zero discrepancy. **9 folios show center-token discrepancies, ALL in user > transcript direction (+1), 8 of 9 concentrated on nymph-page folios.** Hypergeometric p ≈ 0.0023 for the nymph-concentration; binomial p ≈ 0.0039 for the same-direction sign pattern. Both patterns statistically real.

**Specific candidate transcript errors (9 folios):** f70v2, f70v1, f71r, f71v, f72r1, f72r2, f72r3, f72v1, f73r — user observed 1+ center tokens that the H-track transcript does not encode under center placement codes (C, C1, C2, W, I, B). Mechanism (transcriber methodology vs missing transcription vs alternate placement encoding) reserved for follow-up.

## Background

`context/ARCHITECTURE/azc_transcript_encoding.md` (last updated 2026-01-19, AZC_INTERFACE_VALIDATION phase) validates 4 diagram types (STANDARD_RING, SCATTER, SEGMENTED, NYMPH) and notes that "many center tokens may be MISSING from transcript (not transcribed)." User manual annotations (`data/folio_annotations/azc/`) document specific cases where user-observed token counts differ from transcript encoding (e.g., f70v2 user_observed=2 center tokens vs transcript_token=1; f70v1 user_observed=1 vs transcript=none).

What hasn't been done:
- Systematic per-folio audit across all 13 annotation sets
- Quantitative count of discrepancies (how many folios, how systematic)
- Per-diagram-type stratification (does the missing-center pattern vary?)
- Identification of specific candidate transcript errors warranting follow-up

This is a **measurement phase, not a hypothesis test.** Pre-registration locks methodology and sample (the 13 annotation files), not predictions about what we'll find.

## Definitions (locked)

**User annotations:** the JSON files in `data/folio_annotations/azc/`, treated as ground-truth visual observations. 13 files covering 28 folios (some are foldouts containing multiple folios).

**H-track transcript counts:** per-folio token counts grouped by placement code, derived from `data/transcriptions/interlinear_full_words.txt` filtered to transcriber='H', no labels excluded (we want labels here since AZC uses many of them), no asterisks.

**Discrepancy types we will count:**
- **Total token count diff:** user_observed_total − transcript_total
- **Center-token diff:** user_observed_center − transcript_center
- **Ring count diff:** user_observed_rings − transcript_distinct_R/S/C placement layers
- **Placement code distribution:** what placement codes does the transcript use vs what user describes

**Diagram type:** as classified in architecture doc (STANDARD_RING, SCATTER, SEGMENTED, NYMPH).

## Locked methodology

| ID | Spec |
|----|------|
| M1 | Sample: 13 annotation JSON files in `data/folio_annotations/azc/` (locked at execution time) |
| M2 | Transcript: H-track only, all placement codes preserved (do not filter labels — labels are part of AZC structure) |
| M3 | Per-folio basis: each folio in each annotation file is one observation |
| M4 | For foldout files, each constituent folio is a separate observation |
| M5 | Token counts: total, per-placement-code, per-line-number distinct count |
| M6 | Diagram type: read from annotation file when present; otherwise infer from architecture doc table |
| M7 | Discrepancy magnitude: integer count of (user − transcript), preserving sign |
| M8 | No threshold for "significant" discrepancy — all are reported |

## What this phase will produce

Per-folio audit table with columns:
- folio
- annotation file
- diagram type
- user-observed total tokens
- transcript total tokens
- discrepancy (user − transcript)
- center tokens (user-observed)
- center tokens (transcript)
- center discrepancy
- ring count (user-observed)
- distinct ring/circle placement layers (transcript)
- ring discrepancy
- notable oddities listed in annotation
- candidate transcript error flag (boolean: any non-zero discrepancy)

Plus aggregate statistics:
- Total folios with non-zero discrepancy
- Distribution of discrepancy magnitudes
- Per-diagram-type breakdown
- Specific folios warranting follow-up

## Pre-registered measurements (not predictions)

This phase is descriptive. We do NOT pre-register hypotheses about what fraction of folios will show discrepancies — that would require prior data we don't have. Instead, we lock the methodology and report whatever is found.

After running, we will register:

**C2004:** Quantitative measurement of AZC annotation-transcript discrepancies. Tier 2 measurement.
- Form: "Of N annotated AZC folios, X show non-zero token-count discrepancy, Y show center-token discrepancy, Z show ring-count discrepancy. Discrepancy distribution: [details]. Candidate transcript errors: [folio list]."

**C2005 (conditional on patterns emerging):** If discrepancies stratify systematically by diagram type, register that pattern. Tier 2 measurement only — no mechanism inference.

If neither pattern is interesting (e.g., discrepancies are random and small), C2005 is not registered and only C2004 captures the audit summary.

## Anti-HARK commitments

- Methodology locked: counting rules, sample, no post-hoc inclusion/exclusion of annotations
- No predictions to revise — descriptive phase
- Constraint claims will reflect what was measured, not interpretation
- Per the C1998-C2002 hygiene-pass framework: at Tier 2 the constraint must be true regardless of any mechanism inference attached
- Specific candidate transcript errors will be listed as flagged for review, not asserted as confirmed errors

## Scope: what this phase does NOT do

- Does not investigate why discrepancies exist (production-side scribal habit? transcriber methodology? user mis-counting?)
- Does not propose corrections to the transcript
- Does not extend AZC source-matching investigation
- Does not test C468 (28× escape rate) or C1269-1276 (zone categories) or any existing AZC structural claims
- Does not retest AZC_INTERFACE_VALIDATION findings (4 diagram types, P-text reclassification, etc.)

The phase is an audit, not a research investigation. Follow-up phases could pursue specific candidate errors or interpretation of patterns.

## Computational plan

Single script `s1_annotation_diff.py`:
1. Load all 13 annotation JSON files
2. Load H-track transcript filtered to AZC folios
3. For each annotation, extract user-observed counts (total, center, rings)
4. For each folio in annotation, compute transcript counts for matching placement codes
5. Build per-folio diff table
6. Compute aggregate statistics
7. Output: `results/annotation_transcript_diff.json` + `results/audit_table.md`

Expected runtime: < 1 minute.

## Relationship to existing constraints

- **C302, C311, C313** — AZC positional grammar (infrastructure)
- **C468** — AZC vocabulary 28× escape rate correlation
- **C763, C764, C920-922** — f57v R2 single-char ring anomaly (specific case of unusual encoding)
- **C922** — single-char AZC h-exclusion
- **C1269-1276** — AZC zone categories
- **C1463-1467** — zone-hazard routing (B-section, not AZC)
- **C1516-1522** — AZC HEAD-level zone differentiation
- **AZC_INTERFACE_VALIDATION** — prior phase that produced the architecture doc; this phase audits the transcript at folio level rather than the structural classifications

## What this phase cannot establish

- Why discrepancies exist (mechanism is downstream)
- Whether user annotations are correct (they're our ground truth by assumption)
- Whether discrepancies indicate transcript errors vs scribal-original ambiguity
- Whether the same patterns extend to non-annotated AZC folios (sample is the 13 annotated)

## Detailed results

### Aggregate

| Metric | Value |
|--------|-------|
| Folios audited | 26 |
| Folios flagged (any discrepancy) | 20 (77%) |
| Folios with total-token diff ≠ 0 | 17 (65%) |
| Folios with center-token diff ≠ 0 | 9 (35%) |
| Folios with ring-layer diff ≠ 0 | 1 |

### Per-diagram-type breakdown

| Type | n folios | n flagged |
|------|----------|-----------|
| multi_ring_nymph | 8 | 7 |
| UNKNOWN (mostly nymph foldouts) | 7 | 6 |
| scatter_circular | 2 | 2 |
| Various single-instance types | 9 | 5 |

### Center-token discrepancies (all user > transcript)

| Folio | User center | Transcript center | Diagram description |
|-------|-------------|-------------------|---------------------|
| f70v2 | 2 | 1 | 5-ring nymph, fish center |
| f70v1 | 1 | 0 | 4-ring nymph, goat center |
| f71r | 1 | 0 | 5-ring nymph, clothed ladies |
| f71v | 1 | 0 | 5-ring nymph |
| f72r1 | 1 | 0 | 5-ring nymph |
| f72r2 | 1 | 0 | 6-ring nymph, man+woman center |
| f72r3 | 1 | 0 | 7-ring nymph (largest in series) |
| f72v1 | 1 | 0 | 5-ring nymph, balancing scale center |
| f73r | 1 | 0 | 5-ring nymph, reptile center |

12 of 26 audited folios are nymph-type. Random expected 9 × (12/26) ≈ 4.2 nymph-concentrations; observed 8/9. Hypergeometric p ≈ 0.0023.

All 9 discrepancies are in the user > transcript direction. Random expected 4.5 each direction; observed 9/9. Binomial p ≈ 0.0039.

## Constraints Registered

### C2004 (Tier 2, Scope: AZC): AZC annotation-transcript audit summary

Of 26 user-annotated AZC folios audited against H-track transcript encoding (sample: 13 annotation files in `data/folio_annotations/azc/`), 20 (77%) show non-zero discrepancy on at least one of three measures (total token count, center-token count, ring-layer count). 17 of 26 (65%) show non-zero total-token discrepancy. 9 of 26 (35%) show center-token discrepancy. 1 of 26 shows ring-layer count discrepancy. Total-token discrepancies are mostly small (+1 to +5); largest is f72v3 at +10. Methodology: H-track only (transcriber='H'), uncertain (asterisk) tokens excluded, center-token detection via placement codes C/C1/C2/W/I/B. The audit establishes that AZC transcript encoding has documented gaps relative to user visual inspection at scale; these are concentrated in specific folios (see C2005). Sample is the 13 annotated folios; results may not generalize to the ~12 non-annotated AZC folios. **Scope:** AZC. **Tier:** 2 (measurement; mechanism interpretation reserved).

| 2 | AZC, audit, transcript-encoding, annotation-diff, measurement, gaps, C302, C311, C313 | n_folios=26. n_flagged=20. flagged_pct=77pct. n_total_diff=17. n_center_diff=9. n_ring_diff=1. methodology_locked_phase_690. |

### C2005 (Tier 2, Scope: AZC): Nymph-page center-token systematic gap in H-track transcript

Of 26 audited AZC folios, 9 show user-observed center tokens that H-track transcript does not encode under center placement codes (C/C1/C2/W/I/B). All 9 discrepancies are in user > transcript direction (+1 in 8 cases, +1 in f70v2 where transcript already has 1). 8 of 9 are on nymph-page folios (f70v-f73r). Statistical sanity: 12 of 26 audited folios are nymph-type; expected nymph-concentration of 9 random center-discrepancies ≈ 4.2; observed 8. Hypergeometric p ≈ 0.0023. Direction: 9 of 9 same-sign; binomial p ≈ 0.0039 vs random direction. The systematic and directional pattern is too strong for noise. Specific candidate transcript errors (9 folios): f70v2, f70v1, f71r, f71v, f72r1, f72r2, f72r3, f72v1, f73r. **Mechanism reserved (Tier 2 measurement only):** the gap could reflect (a) transcriber methodological choice not to encode center figure-tokens on nymph pages, (b) genuine missing transcription, (c) center text encoded under non-center placement codes (e.g., R3 innermost ring or S0 top-position), or (d) user mis-counting figure elements as text tokens. Direct verification requires high-resolution scan inspection or independent OCR. **Scope:** AZC. **Tier:** 2 (statistical pattern in user-vs-transcript counts; no mechanism inference at Tier 2).

| 2 | AZC, nymph-page, center-token, transcript-gap, systematic, candidate-errors, audit, C302, C311, C313 | n_center_diffs=9. nymph_concentration=8of9. hypergeometric_p=0.0023. direction_p_binomial=0.0039. all_user_gt_transcript=true. candidate_folios=9. mechanism=reserved. |

## Methodological notes

- Pre-reg discipline preserved: methodology locked, descriptive measurement registered, mechanism reserved (per Phase 689 hygiene-pass framework).
- Per the new framework, both constraints are measurement-only at Tier 2; mechanism interpretation (which of (a)-(d) above explains the gap) is not registered.
- Direct verification requires either high-resolution scan inspection or independent OCR — both candidates for follow-up work.

## Follow-up candidates

1. **OCR verification of the 9 candidate folios.** If/when a Voynichese OCR model is built, the first validation target is whether nymph-page centers actually contain text.
2. **High-resolution scan inspection.** Manual review of the 9 flagged folios at higher resolution than current 1166×1536 JPEGs to determine whether center text exists.
3. **Placement-code remap audit.** Investigate whether the H-track transcript encodes center text under non-center codes (R3 innermost, S0 top-position) on nymph pages — this would convert the "missing token" interpretation into a "mis-classified placement" interpretation.

None committed in this phase.

## Scripts

- `s1_annotation_diff.py` — load 13 annotations, build per-folio diff vs H-track, report aggregate + per-folio + center-discrepancy details

## What this phase establishes

1. **AZC transcript encoding has measurable systematic gaps** — 77% of audited folios show some discrepancy.
2. **Center-token under-representation on nymph pages is statistically real** — direction and concentration both p<0.01.
3. **9 specific candidate transcript-error folios identified** for follow-up verification.
4. **AZC center-token statistics on nymph pages should be treated with a known caveat** in any analysis that depends on them.

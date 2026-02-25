# C1267: Mode A/B Distinction is B-Execution Only

**Tier:** 2
**Scope:** A, B
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

B's Mode A/Mode B distinction (C1258, C1231 suffix centroids) does not organize A records. PP MIDDLEs classified by mode affinity (69 A-enriched, 88 B-enriched, 81 neutral based on B-line mode counts) show no within-record clustering in A: mean concentration 0.692 vs null 0.690 (d=0.85, p=0.204). A records mix mode-A-enriched and mode-B-enriched vocabulary freely.

## Architecture

- **Mode is a B-execution phenomenon.** The Mode A/B distinction reflects how B uses vocabulary (specification vs execution), not how A organizes it.
- **A is mode-agnostic.** A's registry does not pre-sort vocabulary by how B will deploy it across mode tracks. Mode assignment happens at B execution time.
- **Orthogonality established.** Category organization (C1261, d=9.7) and mode affinity (C1267, null) are independent axes. A organizes by operational theme but not by execution mode.

## Key Findings

| Metric | Value |
|--------|-------|
| A records tested | 1,534 |
| Obs mean concentration | 0.692 |
| Null mean concentration | 0.690 +/- 0.003 |
| Cohen d | 0.85 |
| p-value | 0.204 |
| B lines classified | 2,406 (Mode A: 1,035; Mode B: 1,371) |
| PP with affinity | 238 (A-enr: 69, B-enr: 88, neutral: 81) |

## Provenance

- Tests C1258 (parallel mode tracks) backward into A
- Extends C1231 (suffix centroid mode classification)
- Null result establishes B-execution-only scope for mode distinction

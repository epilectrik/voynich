# C1112: P-Text Bridge Enrichment

**Tier:** 2 | **Scope:** A/AZC | **Status:** VALIDATED
**Phase:** 395 (original), 403 (revalidated)

## Statement

P-text (Currier A-like tokens on AZC folios) has extreme bridge MIDDLE enrichment: 45.5% bridge MIDDLEs (55/121 unique), at the 100th percentile of the Currier A bootstrap distribution (p95=12.4%, N=5000).

## Evidence

- P-text extraction: 397 tokens, 121 unique MIDDLEs, 9 folios (f65v, f67r1, f67r2, f68r1, f68r2, f68v2, f68v3, f69r, f70r2)
- Bridge fraction 0.4545 (55/121), vs A mean ~0.087
- Bootstrap: sample 121 MIDDLEs from A vocabulary 5000 times, p95=0.124
- P-text at 100th percentile (above all 5000 bootstrap samples)
- Rosettes bridge fraction: 0.215 (Phase 403) — P-text exceeds Rosettes by 2.1x

## Independence Note

This constraint's evidence depends entirely on P-text tokens from the main transcript (Transcript.azc() filtered by P placement) and the bridge MIDDLE set (85 MIDDLEs from C1013). It does NOT depend on Rosettes transcription data. Originally established in Phase 395 as C1112. Deleted in v4.10.10 as precaution during Rosettes data reset. Re-registered in Phase 403 after confirming evidence independence. Phase 403 reproduced the exact same values (0.4545, 100th percentile).

## Provenance

- Phase 395 (original): P1 test, PASS
- Phase 403 (revalidation): R1 test, PASS — identical values
- Supersedes: none (first establishment)

# Coverage Metrics

**Status:** FROZEN | **Tier:** 0-2

> **Status note (v7.25):** the token counts originally in this file appear to mix all-transcriber figures (B, A) with H-track figures (AZC). They are corrected below to the canonical H-track counts (CLAUDE.md; DATA/TRANSCRIPT_ARCHITECTURE.md); the originals are kept in parentheses. Current orientation: SYSTEM/STATUS_BRIEF.md.

---

## Corpus Coverage

| System | Tokens (H-track) | % | Folios |
|--------|--------|---|--------|
| Currier B | 23,243 (was "~75,248", apparently all-transcriber) | 61.2% | 83 |
| Currier A | 11,415 (was "~37,000", apparently all-transcriber) | 30.1% | 114 |
| AZC | 3,299 | 8.7% | 30 |
| Total | 37,957 (was "~121,649") | 100% | 227 |

---

## Grammar Coverage

| System | 49-Class Coverage | Constraint |
|--------|-------------------|------------|
| Currier B | 100% of the grammar's own 480 types = 69.5% of B tokens (HT/UN by exclusion, C566) | C124 (as corrected) |
| Currier A | 13.6% | C224 |
| AZC | N/A (hybrid) | C301 |

---

## Morphology Classification (C351)

| Category | % |
|----------|---|
| Explained | 92.66% |
| Ambiguous | 3.90% |
| Noise | 2.82% |
| TRUE ORPHAN | 0.62% |

---

## Human Track Coverage

| Metric | Value | Constraint |
|--------|-------|------------|
| Occurrences | ~40,000 (legacy figure; exceeds the H-track total of 37,957, so apparently pre-H-filter — see C566: 7,042 HT/UN tokens = 30.5% of Currier B) | - |
| % of corpus | 33.4% (legacy, same caveat) | - |
| Unique types | ~11,000 (legacy, same caveat) | - |
| Section-exclusive | 80.7% | C167 |
| Decomposable | 71.3% | C347 |
| Hapax rate | 67.5% | C406 |

---

## Vocabulary Integration

| Metric | Value | Constraint |
|--------|-------|------------|
| B tokens in A vocabulary | 69.8% | C335 |
| A-B shared types | 1,532 | C335 |
| Cross-folio pool uniformity | J=0.998 | C384 |

---

## Phase Coverage

| Metric | Value (v7.25, 2026-09-28) | Historical value (early snapshot) |
|--------|-------|-------|
| Completed phases | 763 | 118 |
| Live constraints (generated table) | 1,889 | 411 "validated" |
| Tier 0 constraints | 17 | ~15 |
| Tier 1 (falsifications) | 38 | ~20 |
| Tier 2 (structural) | 1,695 | ~375 |
| Tier 3 / Tier 4 (demoted or speculative) | 135 / 4 | — |

---

## Folio Coverage

| Category | Count |
|----------|-------|
| B folios enumerated | 83/83 (100%) |
| A folios analyzed | 114/114 (100%) |
| AZC folios analyzed | 30/30 (100%) |
| Restart-capable | 3 |
| Vocabulary outliers | 3 |

---

## Navigation

← [link_metrics.md](link_metrics.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

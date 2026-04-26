# C1964: o-Prefix Within-Line Interleaving Dominance

**Tier:** 2
**Scope:** B, PREFIX, line, paragraph, persistence, interleaving, run-length
**Phase:** PHASE_649_O_PREFIX_VALIDATION
**Date:** 2026-04-25
**Refines:** C1962 (4-axis o-prefix runtime channel taxonomy — adds explicit scope: token-scoped at prefix level, block-scoped at fire/vessel level)
**Extends:** C1228 (PREFIX channel switching within paragraphs at 73.2%), C1722-C1726 (line ordering is i.i.d.-like, position-invariant)
**Reinforces:** C1961 (fire-side / vessel-side paragraph-level partition — independent confirmation of block-level coherence)

---

## Statement

The 4-axis o-prefix architecture (C1962) is **token-scoped at the prefix level, NOT line-scoped**. Within Currier B lines, prefixes interleave rapidly: mean run length 1.27 tokens, median 1, **80.8% singletons**, max 10. **85.3% of prefix transitions occur within-line, not at line breaks.** Lines are not channel-coherent units.

Block-level (fire vs vessel) coherence is moderate: mean run 2.39, max 50, 50.3% singletons, 11.7% reach length 5, 2.4% reach length 10. **46% of paragraphs are >70% block-pure**, 13% >85%.

The architecture operates at **two distinct scopes** simultaneously:
- **Token / prefix:** rapid interleaving (channels switch token-by-token)
- **Paragraph / block:** moderate coherence (paragraphs specialize fire-side or vessel-side)

Line is not an architectural unit for this dimension.

---

## Empirical evidence

### Prefix-level run distribution

| Statistic | Value |
|---|---|
| Mean run length | **1.27** |
| Median | 1 |
| 25th percentile | 1 |
| 75th percentile | 1 |
| Max | 10 |
| Singletons (length 1) | **80.8%** |
| Long runs (≥5) | 0.5% |
| Long runs (≥10) | 0.0% |
| Total runs analyzed | 11,034 |

### Block-level (fire/vessel) run distribution

| Statistic | Value |
|---|---|
| Mean run length | 2.39 |
| Median | 1 |
| 75th percentile | 3 |
| Max | 50 |
| Singletons | 50.3% |
| Runs ≥5 | 11.7% |
| Runs ≥10 | 2.4% |
| Total runs | 5,836 |

### Transition location

| Level | Within-line | Line-break |
|---|:---:|:---:|
| Prefix-level | 8,999 (85.3%) | 1,557 (14.7%) |
| Block-level | 4,521 (84.4%) | 837 (15.6%) |

### Paragraph-level purity

| Level | Mean dominant fraction | >70% pure | >85% pure | 100% pure |
|---|:---:|:---:|:---:|:---:|
| Prefix-level | 37.3% | 0.2% | n/a | n/a |
| Block-level | **69.6%** | **46.4%** | 13.0% | 1.0% |

---

## What this falsifies

The "channels persist within lines" intuition (which I held entering Phase 649) is wrong at the prefix level. The bigram-enrichment of self-loops observed in Phase 649 T2 (ot→ot +0.99, or→or +1.05, etc.) is **relative enrichment** (~2× expected under marginal product null), not **absolute persistence**. With prefixes themselves being rare (5-15% of tokens each), even 2× enrichment leaves runs dominated by singletons.

Lines are NOT operational atomic units for the o-prefix architecture. The token is.

---

## What this confirms

- **C1228:** PREFIX channel switching within paragraphs at 73.2% — C1964 sharpens to within-LINE switching at 85% with mean run 1.27.
- **C1722-C1726:** line ordering is position-invariant; tokens are independent samples. C1964's 80.8%-singleton pattern is consistent with token-as-atomic-decision (per C1394 HEAD+MOD*+TERM) rather than channel-as-stream.
- **C1394:** atom-level token architecture — each token = one complete (HEAD, MOD*, TERM) decision. Prefix is part of that decision and changes per-token, not per-line.
- **C1961:** fire-side / vessel-side paragraph-level partition. C1964 independently confirms via block-level coherence: 46% of paragraphs >70% block-pure with block runs reaching length 50.

---

## Architectural implication

The prefix-channel architecture has a **two-level hierarchical structure**:

| Scale | Pattern | Scope |
|---|---|---|
| Token-by-token | Rapid interleaving (mean run 1.27, 80% singletons) | **Token = atomic instruction primitive** (per C1394) |
| Within line | Channels alternate without persistence | Line ≠ channel-coherent unit |
| Within paragraph (block-level) | Mean run 2.39, max 50; ~half singletons; moderate coherence | Block (fire vs vessel) is specialized |
| Across paragraph (block purity) | 46% >70% block-pure, 13% >85% | **Paragraph = block-specialized unit** (per C1961) |

This is consistent with crazy-expert's reading: each token is a complete instruction primitive (one observation/action over the prefix-channel grammar), not a sample from a continuously-monitored channel. The block-level paragraph specialization is the operator selecting which "panel" of channels to operate on; within that panel, individual instructions cycle rapidly across the panel's channels.

The architecture is **NOT** like a real-time process-control logger (which would show channel persistence). It is more like an **assembly-language program** with single-instruction-per-token discipline, where the program's procedural mode changes paragraph-by-paragraph and the operational primitives interleave token-by-token.

---

## Falsification

Would be falsified if:

1. Prefix-level mean run length exceeds 3 tokens with non-trivial frequency (would suggest channel persistence at line scale)
2. Block-level paragraph purity drops below 50% (>70%-pure fraction) — would indicate no block-level specialization
3. Within-line transitions drop below 60% (would suggest line-break is the architectural unit)

---

## Provenance

- `phases/PHASE_649_O_PREFIX_VALIDATION/scripts/s4_channel_run_analysis.py`
- `phases/PHASE_649_O_PREFIX_VALIDATION/results/channel_runs.json`

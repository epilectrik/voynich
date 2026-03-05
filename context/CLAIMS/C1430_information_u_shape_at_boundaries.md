# C1430: Information U-Shape at Line Boundaries

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, information, position, boundary
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C672 (line boundaries grammar-transparent), C964 (boundary-constrained free-interior)
**Relates to:** C958 (opener determines line length), C1219 (base character determines MIDDLE content), C531 (folio vocabulary uniqueness)

---

## Statement

Token information content (self-information in bits) forms a U-shape across line positions: Q0=10.29, Q1=9.61, Q2=9.58, Q3=9.62, Q4=10.11 bits. Boundaries carry more information than the interior. Initial tokens are most informative (opener = specification tokens, folio-specific vocabulary). Final tokens are second-most informative (routing/termination markers). Interior tokens are lower-information routine thermal operations using common MIDDLEs.

### Information by Quintile

| Quintile | Mean Info (bits) | N tokens |
|----------|-----------------|----------|
| Q0 (initial) | **10.291** | 5,014 |
| Q1 | 9.606 | 4,186 |
| Q2 | 9.575 | 4,135 |
| Q3 | 9.623 | 4,186 |
| Q4 (final) | **10.108** | 5,553 |

### Context Metrics

| Metric | Value |
|--------|-------|
| Global word entropy | 9.875 bits |
| Mean line entropy | 3.117 bits |
| Pos-1 PREFIX -> rest-of-line category MI | 0.084 bits |

### Implication

The U-shape reflects two distinct information roles:
1. **Initial tokens** specify the line's operational context using diverse, folio-specific vocabulary (high surprisal)
2. **Interior tokens** execute routine thermal operations using shared, high-frequency vocabulary (low surprisal)
3. **Final tokens** perform routing and state-change using specialized closure markers (high surprisal)

This pattern is consistent with the SPECIFICATION -> WORK -> CLOSURE architecture established by C556 and refined by C1428.

---

## Falsification Criteria

1. If information is flat across positions (no boundary enrichment)
2. If initial tokens are less informative than interior (would contradict specification role)
3. If final tokens are less informative than interior (would contradict closure role)

---

## Method

- Per-token self-information: -log2(P(word)) using corpus-wide unigram frequencies
- 23,096 tokens with normalized positions (0-1) binned into quintiles
- Line entropy: H(word distribution within single line)

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T8)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`

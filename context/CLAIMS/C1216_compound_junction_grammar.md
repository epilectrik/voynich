# C1216: Compound Junction Grammar

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** COMPOUND_SLOT_GRAMMAR (Phase 432)
**Relates to:** C1212 (cross-token sequential chaining), C1210 (MIDDLE slot syntax), C1177 (dark ordering consistent with C1065), C1141 (dark pipeline compounds built from bridge atoms)

---

## Statement

Within compound MIDDLEs, the transitions at junctions between embedded atoms show extremely strong grammar (V=0.415, MI=1.636 bits), 6x stronger than cross-token chaining (V=0.071) and comparable to within-MIDDLE atomic slot syntax (V=0.307). Junction grammar recreates PREFIX bigrams (c→h, o→l, s→h) as internal routing, and is a DIFFERENT system from cross-token sequential grammar (enrichment correlation r=0.089).

### Junction vs Other Scales

| Level | Cramer's V | MI (bits) | Context |
|-------|-----------|-----------|---------|
| Within-tile (atom-internal) | 0.604 | 1.659 | Character bigrams inside embedded atoms |
| **Junction (compound-internal)** | **0.415** | **1.636** | Where one embedded atom ends and next begins |
| Within-MIDDLE (C1210) | 0.307 | 1.071 | INITIAL→TERMINAL of whole MIDDLEs |
| Cross-token (C1212) | 0.071 | 0.064 | TERMINAL(N)→INITIAL(N+1) between tokens |

### Junction Enriched Pairs

| Pair | Obs | Exp | Ratio | Notes |
|------|-----|-----|-------|-------|
| c→h | 380 | 32.5 | 11.7x | PREFIX bigram "ch" |
| l→k | 69 | 6.1 | 11.3x | Energy pair |
| o→l | 343 | 37.6 | 9.1x | PREFIX bigram "ol" |
| h→e | 167 | 19.7 | 8.5x | Monitoring→stability |
| q→e | 42 | 5.0 | 8.4x | PREFIX-like "qe" |
| r→a | 38 | 4.6 | 8.3x | Iteration pair |
| p→c | 121 | 14.9 | 8.1x | Structural→monitoring |
| s→h | 81 | 10.0 | 8.1x | PREFIX bigram "sh" |
| r→o | 52 | 6.5 | 8.0x | Iteration→structural |
| k→h | 164 | 28.0 | 5.9x | Energy→monitoring |

### Junction Depleted Pairs (0-count, exp >= 5)

| Pair | Exp | Notes |
|------|-----|-------|
| c→y | 119.2 | Monitoring→closure forbidden |
| d→h | 175.2 | Closure→monitoring forbidden |
| c→n | 57.2 | Monitoring→iteration-terminal forbidden |
| c→i | 31.8 | Monitoring→iteration forbidden |
| c→c | 28.7 | Monitoring self-junction forbidden |
| c→e | 25.0 | Monitoring→stability forbidden |
| a→y | 24.4 | C1210 forbidden maintained |
| c→d | 18.2 | Monitoring→closure forbidden |
| c→l | 17.8 | Monitoring→energy forbidden |

The 'c' atom is the most constrained at junctions: it can ONLY be followed by 'h' (380 obs vs 32.5 exp = 11.7x). All other c→X junctions are near-zero or zero. This is because 'c' at a junction is constructing the PREFIX bigram "ch".

### C1210 Forbidden Pairs at Junctions

| Pair | Obs | Total | Rate |
|------|-----|-------|------|
| a→y | 0 | 82 | 0.000% |
| e→n | 0 | 1,569 | 0.000% |
| k→n | 0 | 345 | 0.000% |

All three forbidden pairs are strictly zero at junctions, even more categorical than within whole MIDDLEs.

### Junction vs Cross-Token Correlation

| Metric | Value |
|--------|-------|
| Common pairs tested | 116 |
| Enrichment ratio correlation | r=0.089 |

The two grammars are essentially uncorrelated. The strongest junction enrichments (c→h 11.7x, l→k 11.3x) are near-neutral at the cross-token level. Compound construction grammar and cross-token execution grammar are distinct systems.

### Compound Tiling Distribution

| Tiles per compound | Count |
|-------------------|-------|
| 2 | 7,118 |
| 3 | 520 |
| 4 | 129 |
| 5 | 38 |
| 6 | 12 |
| 7 | 1 |

91% of compounds are 2-tile (two embedded atoms with one junction).

---

## Interpretation

Compound MIDDLEs are built by fusing atomic operations with internal routing that uses PREFIX-like connection grammar. The junctions between embedded atoms recreate PREFIX bigrams (ch, ol, sh) — the same routing vocabulary that appears at the token level as actual PREFIXes. This means compound construction reuses the mode-selection grammar at a sub-token scale, creating bound multi-stage instructions where the intermediate routing is baked into the instruction itself.

The near-zero correlation with cross-token grammar (r=0.089) confirms that compound fabrication and sequential execution are distinct layers. Between tokens, the system is loosely coupled (C1212: V=0.071). Within compounds, operations are tightly bound with specific routing rules.

---

## Method

- 7,818 compound Currier B tokens (MiddleAnalyzer, 72 core types)
- Greedy left-to-right tiling: longest core MIDDLE match first, single-character residue if no match
- 8,763 junction transitions, 10,000 within-tile transitions
- Cross-token comparison: 13,737 consecutive within-line token pairs

**Script:** `phases/COMPOUND_SLOT_GRAMMAR/scripts/compound_slot_test.py` (T2, T3)
**Results:** `phases/COMPOUND_SLOT_GRAMMAR/results/compound_slot_results.json`

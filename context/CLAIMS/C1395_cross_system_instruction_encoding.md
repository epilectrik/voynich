# C1395: Cross-System Instruction Encoding

**Tier:** 2 (ESTABLISHED)
**Scope:** GLOBAL (A, B, cross-system)
**Phase:** INSTRUCTION_ENCODING_MAP (Phase 507)
**Depends on:** C1393 (composition grammar), C1394 (instruction encoding architecture), C233 (A↔B shared vocabulary), C234 (A registry function), C240 (A=population descriptions), C482 (within-folio compatibility), C484 (A→B pool relationship)

## Statement

The HEAD+MOD*+TERM instruction encoding architecture (C1393/C1394) is manuscript-wide, not B-specific. A-exclusive MIDDLEs follow the same slot grammar (modifier ordering p→f→i→c→d→s, Fisher p=0.90; pair-lock 84.2% agreement; atom distribution V=0.114). Bridge MIDDLEs show 100% category stability across systems (HEAD domain preserved with V=0.562). However, A and B use the encoding with different functional emphasis: A is enriched in state-describing terminals (l at 1.84x) and arrangement frames (o-HEAD 2.5-2.8x), while B is dominated by action-performing terminals (dy at 144x enrichment). A records exhibit internal positional grammar — [arrangement (o-HEAD)] → [parameters (e/k)] → [identity (headless)] — with within-folio PP compatibility exceeding between-folio by 1.22x (z=+20.9). Headless compounds are genuinely headless (HEAD recovery from PREFIX rejected at 9.1% accuracy).

## Key Findings

### T1: A-Exclusive MIDDLE Slot Grammar

579 A-exclusive MIDDLE types follow the same HEAD+MOD*+TERM encoding as B:

| Metric | A-exclusive | B reference | Divergence |
|--------|-------------|-------------|------------|
| Modifier ordering agreement | 61.5% | 62.5% | Fisher p=0.90 |
| Pair-lock agreement | 84.2% (16/19 atoms) | — | — |
| Atom distribution | — | — | V=0.114 (small) |
| Clean decomposition rate | 8.6% | 20.3% | o in medial positions |

- Modifier ordering is statistically indistinguishable between A-exclusive and B compounds
- Three atoms differ in pair-lock status, explained by A's different functional emphasis
- Clean decomposition rate is lower in A because o appears in medial positions more frequently (arrangement framing vs execution)
- **VERDICT:** SHARED_GRAMMAR — encoding is manuscript-wide

### T2: Headless HEAD Recovery

Testing whether headless compounds are abbreviations with PREFIX supplying the missing HEAD:

| Method | Accuracy | Baseline |
|--------|----------|----------|
| PREFIX-base → HEAD cosine | 0.220 | — |
| Assign PREFIX-base as HEAD | 9.1% | 25.2% (random) |

- PREFIX-base → HEAD mapping has terrible cosine similarity (0.220)
- Assigning PREFIX-base as HEAD gives worse-than-random accuracy (9.1% vs 25.2%)
- **VERDICT:** REJECTED — headless compounds are genuinely headless, not abbreviated. Resolves C1394 open question about HEAD recovery.

### T3: A Record HEAD Domain Coherence

Testing whether A records maintain HEAD-domain coherence within individual records:

| Metric | Value | Significance |
|--------|-------|-------------|
| Entropy reduction | 7.7% | z=-17.4 (highly significant) |
| All-same-HEAD records | 2.4% | Rare pure-domain records |
| Typical HEADs per record | 3+ | Mixed but coherent |
| A vs B coherence | 7.7% vs 5.2% | A MORE coherent than B |

- Records are domain-coherent beyond chance (z=-17.4)
- But records typically mix 3+ HEADs, not single-domain
- A records are more coherent than B lines (7.7% vs 5.2% entropy reduction)
- Positional structure: o-HEAD leads (37.5% first position), headless trails (55.5% last position)
- **VERDICT:** DOMAIN_COHERENT (statistically significant, weak absolute effect)

### T4: Cross-System HEAD Stability

Testing whether HEAD domain assignment is preserved for MIDDLEs shared between A and B:

| Metric | Value |
|--------|-------|
| Bridge MIDDLEs tested | 85 |
| Category match | 100% |
| HEAD × Category chi² | 18,499 |
| HEAD × Category V | 0.562 |
| PREFIX wrapping cosine | 0.675–0.998 |

- Every bridge MIDDLE has the same HEAD category in A and B — 100% stability
- HEAD domain is a cross-system semantic marker (V=0.562)
- PREFIX wrapping tracks HEAD domain cross-system (cosine range 0.675–0.998)
- **VERDICT:** HEAD domain is cross-system semantic marker

### T5: A-Exclusive Frames and TERMINAL Distribution

Comparing frame usage and terminal distribution between A and B:

| Feature | A | B | Ratio |
|---------|---|---|-------|
| A-exclusive frames | 2 (k+n, k+t) | — | — |
| B-only frames | — | 17 (edy, aiin, ar, am...) | — |
| o-frames enrichment | 2.5–2.8x | — | A arrangement emphasis |
| dy terminal | 0.1% | 14.4% | 144x B-enriched |
| l terminal | 1.84x enriched in A | — | State emphasis |

- Only 2 A-exclusive frames (both k-initial: k+n, k+t)
- 17 B-only frames represent execution verbs (edy, aiin, ar, am)
- A enriched in o-frames (arrangement) at 2.5-2.8x
- B dominated by e/k-frames with dynamic terminals
- The dy cliff: dy = 14.4% of B tokens but only 0.1% of A (144x B-enriched)
- A enriched in l-terminal (state) at 1.84x; B dominated by dy-terminal (seal)
- **VERDICT:** A = state descriptions, B = action instructions

### T6: A Record → B Folio Prediction

Testing whether A record content predicts which B folio it maps to:

| Metric | Value |
|--------|-------|
| Statistical significance | z=+8.60 |
| Practical effect | R²<5% |
| Connectivity | Each A record → ~81/82 B folios |
| Strongest signal | o-HEAD (z=+8.55) |

- Statistically significant but practically flat
- Near-saturation connectivity: each A record connects to ~81 of 82 B folios
- o-HEAD provides the strongest (still weak) signal
- **VERDICT:** WEAK_SIGNAL — A→B is uniform pool, not content routing (confirms C1136/C484)

### T7: Situation Description Tests (P6, P8, P10)

Three predictions testing the hypothesis that A records are situation descriptions:

| Prediction | Result | Key metric |
|------------|--------|-----------|
| P6: RI complexity → B coverage | PARTIAL | rho=-0.129 (p=3e-7), confounded by record length |
| P8: Within-folio compatibility | CONFIRMED | 1.22x Jaccard ratio, z=+20.9 |
| P10: Positional grammar | CONFIRMED | o-HEAD leads (0.439), headless trails (0.563), all p≈0 |

- P6 (RI complexity → B coverage): raw correlation negative (rho=-0.129) but confounded by record length
- P8 (within-folio compatibility): within-folio Jaccard 1.22x higher than between-folio (z=+20.9)
- P10 (positional grammar): o-HEAD leads (mean position 0.439), l-terminal medial (0.487), headless trails (0.563), all p≈0
- **VERDICT:** STRONG SUPPORT for situation description language hypothesis

## Cross-System Summary

```
A records (situation descriptions):
  [o-HEAD arrangement] → [e/k parameters] → [headless identity]
  State-focused: l-terminal enriched (1.84x), dy nearly absent (0.1%)
  Within-folio compatible (1.22x, z=+20.9)
  Pool relationship to B (uniform, not routed)

B folios (action instructions):
  [HEAD domain] + [MOD* parametrization] + [TERM exit]
  Action-focused: dy-terminal dominant (14.4%), execution frames (edy, aiin, ar)
  Dynamic e/k-frames with diverse modifier stacks

Shared infrastructure:
  Same slot grammar (Fisher p=0.90)
  Same atom inventory (pair-lock 84.2%, distribution V=0.114)
  100% HEAD category stability across bridge MIDDLEs (V=0.562)
```

## Open Questions

- Does the A record positional grammar (o-lead, headless-trail) extend to all sections equally?
- What are the 2 A-exclusive frames (k+n, k+t) used for?
- Can within-folio compatibility predict B REGIME alignment?

## Falsification

Would be falsified if:
1. A-exclusive MIDDLEs shown to follow different modifier ordering than B (currently Fisher p=0.90)
2. Bridge MIDDLE category assignment shown to differ between A and B contexts (currently 100% match)
3. Within-folio compatibility shown to be a section artifact (disappears within sections)

## Provenance

### Phase 507 Scripts
- `phases/INSTRUCTION_ENCODING_MAP/scripts/a_exclusive_slot_grammar.py` — T1 (A-exclusive slot grammar)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/headless_head_recovery.py` — T2 (headless HEAD recovery)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/a_record_head_coherence.py` — T3 (record HEAD coherence)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/cross_system_head_stability.py` — T4 (cross-system HEAD stability)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/a_exclusive_frames_and_terminals.py` — T5 (A-exclusive frames and terminals)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/a_record_b_folio_prediction.py` — T6 (A record → B folio prediction)
- `phases/INSTRUCTION_ENCODING_MAP/scripts/a_situation_description_tests.py` — T7 (situation description tests P6/P8/P10)

### Phase 507 Results
- `phases/INSTRUCTION_ENCODING_MAP/results/a_exclusive_slot_grammar.json` — T1 results
- `phases/INSTRUCTION_ENCODING_MAP/results/headless_head_recovery.json` — T2 results
- `phases/INSTRUCTION_ENCODING_MAP/results/a_record_head_coherence.json` — T3 results
- `phases/INSTRUCTION_ENCODING_MAP/results/cross_system_head_stability.json` — T4 results
- `phases/INSTRUCTION_ENCODING_MAP/results/a_exclusive_frames_and_terminals.json` — T5 results
- `phases/INSTRUCTION_ENCODING_MAP/results/a_record_b_folio_prediction.json` — T6 results
- `phases/INSTRUCTION_ENCODING_MAP/results/a_situation_description_tests.json` — T7 results

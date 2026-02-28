# C1376: Character-Level RTL Signal Is Grammar-Internal (Slot Syntax)

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** 489 (EVA_CHAR_ASYMMETRY_DECOMPOSITION)
**Depends on:** C1209, C1024, C521, C1117, C1375
**Cross-ref:** github.com/antenore/voynich-toolkit (Gatta RTL z=22.97)

## Statement

The character-level RTL directional signal in EVA Currier B text (replicated at z=36.8 within-token bigram conditional entropy) is **fully explained** by C1209's MIDDLE slot syntax (INITIAL→MEDIAL→TERMINAL character ordering). A slot-preserving shuffle — which maintains C1209 slot assignments per character position but randomizes character identity within each slot — preserves 102.0% of the observed asymmetry (mean 0.559 vs observed 0.548, z=-2.6). Destroying character order within MIDDLEs eliminates the signal entirely (z=79.8 from shuffled null). The asymmetry is grammar-internal; no encoding design feature beyond the grammar is required.

## Key Findings

### T1: Character-Level RTL Signal Replicated
- Bigram conditional entropy: LTR=1.953, RTL=1.846, diff=+0.107 bits
- Trigram conditional entropy: LTR=1.728, RTL=1.644, diff=+0.083 bits
- Bootstrap z=36.8 (1,000 line-level resamples)
- **RTL_FAVORED:** Characters within tokens are more predictable when read right-to-left

### T2: MIDDLE Dominates
- MIDDLE-internal: +0.548 bits (38% of total, dominant contributor)
- PREFIX→MIDDLE junction: +0.559 bits
- MIDDLE→SUFFIX junction: -0.563 bits (these two junctions nearly cancel)
- PREFIX-internal: -0.260 bits (PREFIX is symmetric/slightly LTR-favored)

### T3: Coarse Slot Syntax Explains 48.9%
- 4-category slot-level H asymmetry: +0.268 bits (48.9% of MIDDLE's +0.548)
- INITIAL→TERMINAL transitions: 4,936 (9.9x more frequent than TERMINAL→INITIAL: 501)
- The remaining 51.1% comes from within-slot character frequency distributions

### T4: Slot-Preserving Shuffle Explains ~100% (Decisive Test)
- Shuffled-within-MIDDLE: mean=+0.000, z=79.8 (destroying order kills asymmetry)
- Reversed-token: diff=-0.548 (sign flips, confirming directional property)
- Random frequency-matched: mean=+0.000, z=85.0 (character frequency alone insufficient)
- **Slot-preserving shuffle: mean=+0.559 vs observed=+0.548 (z=-2.6)**
  - Observed is WITHIN the slot-preserving distribution
  - C1209 slot structure + per-slot character frequencies = full explanation

### T5: Gallows Reduce Asymmetry
- Gallows contribute -35.7% (removing them increases asymmetry from +0.107 to +0.145)
- Consistent with C1209: k,t are FREE atoms (no slot preference)
- Gallows are more predictable from right context (MI=0.147) than left (MI=0.046)
- Mean gallows position: 0.325 (skew toward token-initial, per C841)

### T6: Kernel Opposes Main Gradient
- Kernel H asymmetry: -0.507 bits (LTR more predictable for kernel pairs)
- Kernel contribution: -10.3% of MIDDLE asymmetry (opposes RTL signal)
- Mechanism: C521's e→h block (0.00) and h→e facilitation (7x) creates LTR predictability for kernel, because e=INITIAL and h=TERMINAL — the kernel's one-way valve runs WITH the slot gradient
- Non-kernel H asymmetry: +0.434 bits (carries the RTL signal)

## Interpretation

Gatta's RTL finding (z=22.97) and our replication (z=36.8) detect a genuine statistical property of EVA text: characters within tokens are arranged in an INITIAL→MEDIAL→TERMINAL gradient (C1209) that makes right-to-left reading more predictable. This is because:

1. **INITIAL characters (a,q,e,o) are high-frequency.** They occur at token starts, making the first character highly predictable. Reading RTL, the first character you encounter is the TERMINAL (low-frequency, high-entropy) and the last is the INITIAL (high-frequency, low-entropy). The conditional entropy H(c2|c1) is lower RTL because the low-entropy INITIAL characters appear as the predicted variable, not the conditioning variable.

2. **The gradient is 9.9x.** INITIAL→TERMINAL transitions outnumber TERMINAL→INITIAL by 9.9x. This asymmetry is the direct cause of the directional signal.

3. **This is grammar, not encoding design.** The slot-preserving shuffle demonstrates that any text with C1209's slot structure would show the same RTL signal, regardless of which specific characters fill each slot.

**Reconciliation with C1117 (LTR at token level):** C1117 finds LTR at z=17 for token-sequence analysis (MI between adjacent tokens). This is at a different granularity — token ORDER is LTR-biased (C1024: MIDDLE predicts next token better than previous), but CHARACTER order within each token creates an INITIAL→TERMINAL gradient that appears RTL-biased. Both are correct at their respective levels. The apparent contradiction between Gatta's RTL and our LTR is resolved: they measure different structural layers.

## Evidence

- Script: `phases/EVA_CHAR_ASYMMETRY_DECOMPOSITION/scripts/eva_char_asymmetry_decomposition.py`
- Results: `phases/EVA_CHAR_ASYMMETRY_DECOMPOSITION/results/eva_char_asymmetry_decomposition.json`
- 23,096 tokens, 2,420 lines, 27,871 MIDDLE-internal character bigrams
- 6 tests: T1 replication, T2 decomposition, T3 slot prediction, T4 controls, T5 gallows, T6 kernel

## Falsification Conditions

This constraint would be revised if:
1. A different methodology for measuring character-level directionality produces a signal that slot-preserving shuffle does NOT preserve
2. The slot-preserving shuffle control is shown to be inadequate (e.g., it preserves more information than just slot structure)
3. Gatta's z=22.97 is shown to measure something structurally different from within-token bigram conditional entropy

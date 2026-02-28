# C1375: Hebrew Cipher Cross-Validation

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** 488 (HEBREW_CIPHER_CROSS_VALIDATION)
**Depends on:** C120, C130, C132, C109, C121, C124, C1250, C1365
**Cross-ref:** github.com/antenore/voynich-toolkit (Antenore Gatta)

## Statement

Cross-validation of our grammar against Gatta's Hebrew cipher hypothesis (EVA→Hebrew consonantal, RTL, context-sensitive mapping) yields **4/8 control program, 1/8 cipher, 3/8 ambiguous** = STRONG FALSIFICATION of the cipher hypothesis at the grammar layer. The Gatta decode **increases** character bigram entropy (+0.218 bits) and **decreases** token MI (-0.755 bits) — the opposite of what correct decipherment does, consistent with C130. Our 8 operational categories show zero Hebrew-space coherence (within/between ratio=0.991). Only 1/35 PREFIXes (ch→kaf=ke-) exactly matches a Hebrew morpheme. Morphological boundaries partially survive (55.2% consistency) because the transform is character-level and preserves string similarity, not because it preserves grammar. The T2 within-class Hebrew clustering (z=-15.5) is a confound: tokens sharing EVA morphology (same class ≈ similar PREFIX+MIDDLE patterns) remain similar after any character-level transform, regardless of target alphabet. **T8 (added post-initial):** Gatta's lexicon z=3.6-4.4 is explained by EVA's within-slot co-occurrence structure (C1209), not Hebrew-specific alignment. Random bijective mappings show comparable vocabulary concentration (z=-158 vs Gatta z=-131) when comparing real vs slot-shuffled decoded text.

## Key Findings

### T1: Morphological Boundary Survival — AMBIGUOUS
- Overall consistency: 55.2% (between collapse and survival thresholds)
- PREFIX edit distance ratio within/between: 0.579
- Key collisions: ch→kaf (2 chars→1), qo→STRIPPED, ok/da/ol→reversed to suffix position
- **Interpretation:** Partial survival is expected for any character-level transform that doesn't scramble character order. Does not favor either hypothesis.

### T2: 49-Class Grammar Preservation — CIPHER (with confound)
- Within/between class edit distance ratio: 0.781 (z=-15.5 vs null)
- Homophone collisions: 65 (16.9% of decoded types have cross-class duplicates)
- **Critical confound:** Our 49 classes are defined by behavioral equivalence (transition profiles). But class members often share EVA morphological patterns (same PREFIX families, similar MIDDLEs). Any character-level transform preserves character similarity, so within-class decoded strings cluster by construction. The z=-15.5 measures EVA morphological coherence surviving the transform, not Hebrew semantic coherence.
- f/p homophone merge creates 16.9% cross-class collisions — the f/p grammatical distinction (C865-C869) is destroyed.

### T3: Forbidden Transition Preservation — AMBIGUOUS
- 4/17 forbidden pairs share a Hebrew phonological feature (same initial consonant)
- Control pairs: 1-2/17 show same features
- Mildly elevated but not reaching significance threshold (5+/17)
- The 4 matches (dy→chey, l→chol, chey→chedy, chey→shedy) share 'S' (shin) or 'm' (mem) initials, but these arise because 'y' and 'l' are common EVA suffixes that map to common Hebrew letters.

### T4: Category Coherence — CONTROL PROGRAM
- Within/between category edit distance ratio: 0.991 (no clustering)
- Our 8 operational categories produce randomly distributed Hebrew strings
- **C171 semantic ceiling HOLDS.** The categories have no recoverable semantic content in Hebrew space.
- Sample decoded MIDDLEs show no domain coherence: THERMAL=[t, p, Spp], FLOW=[h, hy, J], CONTAINMENT=[Sr, EtA, tAp]

### T5: Information-Theoretic — CONTROL PROGRAM (strongest test)
- Character bigram entropy: EVA=2.009 → Decoded=2.228 (+0.218 bits)
- Token MI: EVA=5.675 → Decoded=4.921 (-0.755 bits)
- **The Gatta decode INCREASES entropy and DECREASES mutual information.** This is the OPPOSITE of what correct decipherment does. A correct decode reveals underlying language structure (lower entropy, higher MI). This transform adds noise.
- Consistent with C130: cipher transforms applied to Voynich text decrease structural signal.
- PREFIX-MIDDLE MI slightly increases (1.537→1.761) due to alphabet compression, not structural gain.

### T6: PREFIX Role Coherence — CONTROL PROGRAM
- Exact Hebrew morpheme matches: 1/35 (2.9%)
- Only ch→k (kaf = Hebrew ke- "like/as") is an exact match
- When using loose matching (startswith), 19/35 appear to match — but this is a combinatorial artifact: ch→k and o→w account for nearly all matches since kaf and vav are Hebrew prefix letters
- Base-modifier overlap: 0 (modifiers and bases map to non-overlapping Hebrew letter sets, but this is incidental, not structurally meaningful)

### T7: Directionality — AMBIGUOUS
- Token-level MI: forward=5.6747, reverse=5.6735 → SYMMETRIC (no direction preference)
- Decoded character entropy: LTR=RTL (no directional advantage)
- Gallows enrichment: line-initial=24.0%, line-final=4.4% → clearly LTR if gallows are openers
- **The token-level symmetry is surprising** given Phase 399's LTR finding. This may reflect the aggregation method (full corpus MI) vs Phase 399's line-by-line analysis.

### T8: Lexicon Signal Under Slot-Preserving Shuffle — CONTROL PROGRAM
- Slot-preserving shuffle (Phase 489 methodology, C1376) shows massive vocabulary concentration difference: real=4,118 unique decoded types vs shuffled=7,395 (z=-131)
- **Critical control:** Random bijective mappings show the SAME effect (z=-158). The vocabulary concentration is from EVA's within-slot co-occurrence structure (C1209), not Hebrew-specific alignment.
- Gatta's mapping is NOT special: random mappings actually show stronger real-vs-shuffled differentiation
- **Interpretation:** Gatta's z=3.6-4.4 lexicon match significance reflects EVA's rich character co-occurrence patterns interacting with Hebrew lexicon coverage probability. Any reasonable character mapping applied to EVA would produce above-chance matches against a large enough target lexicon, because EVA's concentrated vocabulary (from grammar) maps to a concentrated decoded vocabulary that overlaps with real word forms by statistical pressure.

## Interpretation

The Gatta Hebrew cipher hypothesis is **structurally falsified at the grammar layer.** The decode:

1. **Increases entropy** — wrong direction for decipherment
2. **Decreases MI** — destroys structural signal, doesn't reveal it
3. **Produces no category coherence** — semantic ceiling (C171) holds in Hebrew space
4. **Matches no PREFIX morphology** — our 35 PREFIXes are not Hebrew grammatical morphemes
5. **Lexicon signal explained by EVA grammar** — the z=3.6-4.4 lexicon match is not specific to Hebrew (T8)

The one finding that nominally favors the cipher (T2: within-class clustering at z=-15.5) is explained by a confound: character-level transforms preserve string similarity, and our class members share EVA morphological patterns. This is our grammar surviving the transform, not Hebrew structure being revealed.

**Fair assessment for Gatta's work:** Their decode operates at a layer below our grammar — character-level statistical patterns that are orthogonal to our token-level structural findings. Their z=3.6-4.4 lexicon match significance reflects EVA's concentrated vocabulary (from within-slot co-occurrence patterns) interacting with Hebrew lexicon coverage probability, not Hebrew-specific encoding. Random bijective mappings produce the same vocabulary concentration effect. Their own acknowledgment that "decoded text does not read as coherent Hebrew" is consistent with our findings.

## Evidence

- Script: `phases/HEBREW_CIPHER_CROSS_VALIDATION/scripts/hebrew_cipher_cross_validation.py`
- Results: `phases/HEBREW_CIPHER_CROSS_VALIDATION/results/hebrew_cipher_cross_validation.json`
- 23,096 tokens, 2,420 lines, 480 token types, 17 forbidden MIDDLE pairs
- Gatta mapping extracted from: `voynich-toolkit/src/voynich_toolkit/full_decode.py`
- T8 slot-preserving shuffle: 100 iterations Gatta + 20 random bijective mappings × 20 shuffles each

## Falsification Conditions

This constraint would be revised if:
1. A corrected implementation of the Gatta transform (verified against their toolkit output) produces different information-theoretic results
2. The T2 confound is shown to be insufficient to explain the z=-15.5 result (e.g., class-shuffled morphological controls)
3. Gatta produces a revised mapping that decreases entropy and increases MI
4. A test using Gatta's actual 491K-entry Hebrew lexicon shows their specific mapping outperforms random bijective mappings (controlling for slot structure)

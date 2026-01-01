# Voynich Manuscript Investigation Summary

## Session: Initial Analysis

### Data Acquired

| Resource | Location | Size |
|----------|----------|------|
| Manuscript PDF | `data/scans/Voynich_Manuscript.pdf` | 54 MB |
| EVA Transcription | `data/transcriptions/voynich_full_eva.txt` | - |
| Interlinear Corpus | `data/transcriptions/interlinear_full_words.txt` | 9 MB |
| Deciphervoynich Repo | `research/deciphervoynich/` | Analysis scripts |
| Voynich-public Corpus | `research/voynich-corpus/` | Partitioned corpora |

### Baseline Statistics

```
Total Words:        37,957
Unique Words:        8,151
Total Characters:  191,959
Unique Characters:      21 (*acdefghiklmnopqrstxy)
Number of Folios:      225
```

### Entropy Analysis

| Metric | Voynich | Natural Language |
|--------|---------|------------------|
| H1 (Character Entropy) | 3.87 bits | 4.0-4.5 bits |
| H2 (Conditional Entropy) | **2.37 bits** | 3.0-4.0 bits |
| Word Entropy | 10.47 bits | ~10 bits |
| Zipf Coefficient | -1.006 | -1.0 |

**Key Finding**: The H2 value of 2.37 confirms Voynichese has unusually predictable
character sequences. This is the manuscript's most distinctive statistical property.

### Positional Constraints

**Character Position Distribution:**

| Position | Dominant Characters | Notes |
|----------|---------------------|-------|
| First | o(22%), c(18%), q(14%) | Limited starting set |
| Second | h(25%), o(19%), k(10%) | 'h' often in digraphs |
| Middle | e(27%), h(12%), k(10%) | 'e' dominates |
| Penultimate | d(19%), o(18%), i(18%) | More variety |
| Last | **y(41%)**, n(16%), l(16%) | Extremely constrained |

**Word Structure Pattern:**
```
[INITIAL] + [MIDDLE] + [SUFFIX]
    |           |          |
 (ch,qo,sh,d)  (ol,eo,ai)  (y,dy,in,aiin)
```

### Currier Language A vs B Comparison

| Metric | Language A | Language B |
|--------|------------|------------|
| Word Count | 11,415 | 23,243 |
| H2 | 2.39 | 2.21 |
| Words ending in 'y' | 32% | 45% |
| Most common word | daiin | chedy |

**Conclusion**: The H2 difference of only 0.18 bits suggests Currier A and B may
not be fundamentally different encodings, but rather variations possibly due to
different scribes or sections.

### Scribal Hand Analysis

5 distinct hands identified in the corpus:
- Hand 1: 7,257 words (H2=2.31)
- Hand 2: 9,737 words (H2=2.14) - Highest 'y' ending rate (51%)
- Hand 3: 1,818 words (H2=2.25)
- Hand 4: 870 words (H2=2.34)
- Hand 5: 546 words (H2=2.16)

### Key Observations

1. **The text follows Zipf's Law** (coefficient -1.006), suggesting meaningful content

2. **Character sequences are highly predictable** (H2 ~2.4 vs 3-4 for natural languages)

3. **Strict positional constraints exist**:
   - Only 70.3% of possible character pairs ever occur
   - 'y' ends 41% of all words
   - Limited characters can start words

4. **Word structure is regular** - prefix + midfix + suffix pattern

5. **Currier A/B distinction is subtle** - may be scribal rather than linguistic

### Hypotheses to Test

1. **Verbose Cipher Hypothesis**: The regularity suggests a cipher that maps
   single plaintext letters to multiple ciphertext characters

2. **Constructed Language**: The strict grammar rules suggest an artificial
   language like Hildegard von Bingen's Lingua Ignota

3. **Abbreviation System**: Medieval shorthand systems could produce similar patterns

4. **Syllabic Script**: Characters may represent syllables rather than phonemes

### Next Steps

1. [ ] Implement verbose cipher testing tools
2. [ ] Compare word patterns to known abbreviation systems
3. [ ] Analyze illustration-text correlations
4. [ ] Test syllabic reading hypotheses
5. [ ] Apply ML clustering to word patterns
6. [ ] Cross-reference plant illustrations with 15th-century herbals

---

*Analysis conducted: 2025-12-30*
*Tools: Python statistical analysis pipeline*
*Data: EVA transcription from Yale Beinecke Library*

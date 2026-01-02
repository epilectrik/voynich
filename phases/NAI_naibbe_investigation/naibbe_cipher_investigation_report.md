# Naibbe Cipher Investigation Report

**Date:** 2025-12-31
**Status:** New cipher theory requires evaluation against our validated findings

---

## Executive Summary

Michael A. Greshko has published a peer-reviewed paper in *Cryptologia* describing the **Naibbe cipher**, a verbose homophonic substitution cipher that can encrypt Latin and Italian text into ciphertext that statistically mimics the Voynich Manuscript. This is significant because it demonstrates that meaningful encrypted content *could* produce Voynich-like statistical properties - but it is NOT a decipherment claim.

**Key Question for Our Project:** Does the Naibbe cipher model align with or contradict our 30 validated constraints?

---

## The Naibbe Cipher: Technical Description

### What It Is
- A **verbose homophonic substitution cipher** (multiple ciphertext symbols per plaintext letter)
- Named after "naibbe," a 14th-century Italian term for a card game
- Designed to be implementable entirely by hand using 15th-century materials (pen, paper, dice, playing cards)
- Published in: *Cryptologia* (2025), DOI: [10.1080/01611194.2025.2566408](https://www.tandfonline.com/doi/full/10.1080/01611194.2025.2566408)

### How It Works

1. **Text Segmentation:** Plaintext is randomly divided into unigrams (single letters) and bigrams (letter pairs) using dice rolls.
   - Example: "HELLO WORLD" → "H EL L OW OR L D"

2. **Position Encoding:** Each character maps to one of three positions:
   - Unigram → becomes a complete Voynichese "word"
   - Bigram prefix → becomes first part of a Voynichese word
   - Bigram suffix → becomes second part of a Voynichese word

3. **Multiple Encoding Tables:** Six encryption tables exist, selected randomly via playing cards:
   - A unigram can be represented 6 different ways
   - A bigram can be represented 36 different ways (6 prefix variants × 6 suffix variants)

4. **Decipherability:** Ciphertexts remain fully decipherable by reversing the process

### Statistical Properties Reproduced
- Letter frequency patterns
- Word length distributions
- Some measurable linguistic features
- Low entropy (~1/3 bit per letter vs English's ~1.25 bits)

### Known Limitations (from Greshko)
| Limitation | Detail |
|------------|--------|
| Vocabulary coverage | Only reproduces ~30% of unique words in Voynich B |
| Token coverage | Reproduces ~83% of total tokens |
| Long-range correlations | Naibbe lacks the long-distance patterns seen across Voynich pages |
| Flexibility | Less flexible than what the original manuscript appears to produce |

---

## Critical Evaluation Against Our Validated Findings

### POTENTIALLY COMPATIBLE Constraints

| Constraint | Naibbe Compatibility | Notes |
|------------|---------------------|-------|
| Compositional word structure (PREFIX + MIDDLE + SUFFIX) | **COMPATIBLE** | Bigram prefix/suffix mapping directly produces this |
| Position constraints (q first-only, y final-dominant) | **POTENTIALLY COMPATIBLE** | Would depend on specific table design |
| Low entropy | **COMPATIBLE** | Verbose cipher inherently produces low entropy |
| Zipf-like distribution | **POTENTIALLY COMPATIBLE** | Homophonic substitution can preserve word rank distributions |
| Three-part entry structure | **UNKNOWN** | Not addressed by cipher; would be plaintext feature |

### POTENTIALLY PROBLEMATIC Constraints

| Constraint | Issue | Severity |
|------------|-------|----------|
| **Two distinct populations (A/B)** | Why would cipher produce two statistically different populations? | HIGH |
| **Section-conditioned vocabulary (2-6x enrichment)** | Random dice/card selection shouldn't produce section clustering | HIGH |
| **Extremely low repetition (0.1-0.3%)** | Verbose homophonic cipher should produce MORE repetition, not less | CRITICAL |
| **B references A content** (INFINITE asymmetry) | This is a content property, not cipher property - but needs explanation | MEDIUM |
| **71.2% three-part structure agreement** | If random encoding, why would entries have consistent structure? | MEDIUM |
| **Hub headings as category labels** | Meaningful heading structure requires semantic plaintext organization | LOW (compatible if plaintext organized) |

### MOST CRITICAL CHALLENGE: Low Repetition

The Voynich has **0.1-0.3% trigram repetition** - lower than ANY known text genre.

A verbose homophonic cipher should **increase** apparent repetition because:
- Multiple plaintext sequences map to same ciphertext
- Common words/phrases in Latin would produce repeated patterns

Yet Voynich shows the opposite. Greshko's acknowledgment that his model lacks "long-range correlations" may relate to this.

**Question for Greshko's model:** What repetition rate does Naibbe-encrypted Latin produce?

---

## Comparison to Our Previous Cipher Hypotheses

| Hypothesis | Phase Tested | Result | Naibbe Relation |
|------------|--------------|--------|-----------------|
| Simple substitution | Phase 4 | FAILED (gibberish) | Naibbe is more complex |
| Verbose cipher | Phase 4 | FAILED (8,151 unique words too many) | Naibbe is verbose but with constraints |
| Morpheme cipher | Phase 4 | Partially plausible | Naibbe is letter-level, not morpheme |
| Syllabic cipher | Phase 4 | Partially plausible | Naibbe is letter-level |

**Key Difference:** Naibbe uses randomized chunking (dice) + multiple tables (cards), which could explain high word diversity. However, we need to test whether it reproduces our specific statistical signatures.

---

## Ray Dillinger's Critique (Schneier on Security Comments)

Cryptographer Ray Dillinger raised important objections:

> "The Voynichese exhibits 'ridiculous conditional probability' - if you see two letters, the following sequence is predictable with >50% accuracy."

This **supports** a cipher hypothesis (constrained character transitions) but challenges Naibbe specifically because:
- Random dice chunking shouldn't produce predictable sequences
- Card-selected tables introduce randomness that should reduce conditional predictability

**Dillinger's alternative:** The manuscript may be "asemic product" (meaningless text designed to look like language) created by institutional authors given the fine vellum and pigments.

---

## Specific Tests We Could Run

### Test 1: Encode Latin Herbal Text with Naibbe
1. Take a known 15th-century Latin herbal (e.g., excerpts from Herbarium Apuleii)
2. Encode using Naibbe cipher via Greshko's GitHub code
3. Compare statistical properties to our Currier A data:
   - Entropy (should match ~2.37 bits)
   - Vocabulary overlap with Voynich
   - Section enrichment patterns (should NOT match our 2-6x)
   - Repetition rate (should NOT match our 0.1-0.3%)

### Test 2: Currier A/B Simulation
1. Encode two different Latin texts (herbal + encyclopedia)
2. Check if they naturally produce A/B-like population separation
3. If NOT, the Currier A/B distinction argues against a simple Naibbe model

### Test 3: Cross-Reference Preservation
1. Create plaintext where Section B references Section A content
2. Encode with Naibbe
3. Check if cross-reference structure is detectable
4. Our finding that "B references A" with INFINITE asymmetry should survive encryption

---

## Implications for Our Project

### If Naibbe is Plausible:
1. Voynich plaintext would be Latin or Italian
2. Currier A/B difference might reflect different source texts (not different authors)
3. Prefix-visual correlations would need to be in the plaintext
4. Decipherment would require:
   - Recovering the specific encryption tables used
   - Determining the dice/card selection protocol
   - Having substantial ciphertext to exploit homophonic redundancy

### If Naibbe is Implausible:
1. Our findings on section-conditioned vocabulary and low repetition argue against it
2. The Currier A/B distinction suggests something other than random cipher variation
3. Alternative explanations remain viable:
   - Constructed language
   - Steganographic technique
   - Meaningful glossolalia
   - Sophisticated hoax

---

## Recommendations

### Immediate Actions
1. **Download Greshko's code** from GitHub: https://github.com/greshko/naibbe-cipher
2. **Run Test 1** (Latin herbal encoding) to compare statistical properties
3. **Check if Naibbe produces Currier-like population splits**

### Medium-Term
1. **Contact Greshko** to ask about:
   - Trigram repetition rates in Naibbe output
   - Whether section-conditioned vocabulary is reproducible
   - Conditional probability structure of Naibbe ciphertext
2. **Analyze the specific tables** - do any of our validated prefix patterns map to plausible Latin morphemes?

### Assessment
| Criterion | Rating | Justification |
|-----------|--------|---------------|
| Historical plausibility | HIGH | 15th-century materials only |
| Statistical match | MEDIUM | Matches some properties, fails others |
| Explanatory power | LOW-MEDIUM | Doesn't explain A/B split or low repetition |
| Testability | HIGH | Code available, can run experiments |
| Priority for our project | MEDIUM | Worth testing but unlikely to be complete solution |

---

## Conclusion

The Naibbe cipher is a **serious scholarly contribution** that demonstrates historical cipher techniques could produce some Voynich-like properties. However, it does NOT:
- Claim to be a solution
- Explain all Voynich statistical anomalies
- Account for our findings on section-conditioned vocabulary, Currier A/B distinction, or extremely low repetition

**Our recommendation:** Run empirical tests using Greshko's code against Latin texts comparable to medieval herbals. If the statistical signature doesn't match our validated constraints, we can confidently place Naibbe in the "plausible but insufficient" category alongside our other cipher hypotheses.

The most valuable aspect of this research is that it **strengthens the cipher hypothesis over the hoax/glossolalia hypotheses** by showing that meaningful content CAN hide behind Voynich-like statistics - even if the specific mechanism differs.

---

## Sources

- [Full Paper in Cryptologia](https://www.tandfonline.com/doi/full/10.1080/01611194.2025.2566408)
- [Greshko's Project Page](https://www.michaelgreshko.com/naibbe-cipher)
- [GitHub Repository](https://github.com/greshko/naibbe-cipher)
- [Schneier on Security Discussion](https://www.schneier.com/blog/archives/2025/12/substitution-cipher-based-on-the-voynich-manuscript.html)
- [IFLScience Article](https://www.iflscience.com/is-this-how-the-voynich-manuscript-was-made-a-new-cipher-offers-fascinating-clues-81786)

---

## Files Referenced

| File | Relevance |
|------|-----------|
| `validated_structural_findings.md` | Our 30 constraints to test against |
| `currier_genre_comparison_report.json` | A/B statistical differences |
| `exhaustive_correlation_report.md` | Visual-text correlation findings |
| `procedural_pattern_validation_report.json` | Randomization test methodology |

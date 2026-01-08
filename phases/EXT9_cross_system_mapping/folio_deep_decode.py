"""
Deep analysis of unclassified tokens from f38r.
Try to explain EVERY particle.
"""

from collections import Counter

# The unclassified tokens from f38r
UNCLASSIFIED = ['kos', 'r', 'ysho', 'ychok', 's']

# Context from the folio
CONTEXTS = {
    's': ['chody', 's', 'ytoiin'],  # Line 2: "chody s ytoiin"
    'r': ['chka', 'r', 'odaiin'],   # Line 4: "chka r odaiin"
    'ychok': ['ychok', 'chey'],     # Line 4 start
    'ysho': ['ysho', 'sho', 'kos'], # Line 6: "ysho sho kos daiin"
    'kos': ['ysho', 'sho', 'kos', 'daiin'],
}

print("=" * 80)
print("DEEP ANALYSIS OF UNCLASSIFIED TOKENS")
print("=" * 80)

# Analysis of each token
print("""
## TOKEN: 's' (appears 1x in line 2)

Context: "chody s ytoiin"

HYPOTHESIS 1: Scribal artifact / word break error
- Should be "chodys" (which appears elsewhere in line)
- The space before 's' may be a transcription error
- "chodys" would be CH-family + -dys (unknown suffix, but pattern exists)

HYPOTHESIS 2: Standalone primitive
- 's' is a kernel primitive in Currier B
- May have leaked into A as structural marker
- But this would violate A/B disjunction...

VERDICT: Likely TRANSCRIPTION_ARTIFACT (word break error)
""")

print("""
## TOKEN: 'r' (appears 1x in line 4)

Context: "chka r odaiin"

HYPOTHESIS 1: Scribal artifact / word break error
- Should be "chkar" (CH-family + -ar suffix)
- OR belongs to next word: "rodaiin"
- Looking at line 4: "chka r odaiin" vs "chka rodaiin" later in same line!
- The transcription itself shows "rodaiin" as single token elsewhere

VERDICT: Likely TRANSCRIPTION_ARTIFACT (should be "chkar" or part of "rodaiin")
""")

print("""
## TOKEN: 'ychok' (appears 1x in line 4)

Context: Line 4 starts with "ychok chey"

HYPOTHESIS 1: Initial prefix 'y-' + marker
- 'y' is a very common INITIAL in Voynichese
- 'chok' = CH-family + 'ok' (middle component)
- Structure: y- + chok = INITIAL_PREFIX + CH_MARKER

HYPOTHESIS 2: Compare to 'ychokchey' (also in line 4)
- 'ychokchey' = y- + chok + ch- + ey
- This shows 'y-' is likely a separable initial

VERDICT: INITIAL_PREFIX ('y-') + CH_MARKER ('chok')
- 'y-' appears to be an initial modifier, not part of the 8-prefix system
""")

print("""
## TOKEN: 'ysho' (appears 3x in line 6)

Context: "ysho sho kos daiin"

HYPOTHESIS 1: Initial prefix 'y-' + SH-family
- Same pattern as 'ychok'
- 'y-' + 'sho' = INITIAL_PREFIX + SH_MARKER
- Compare to 'sho' which immediately follows

HYPOTHESIS 2: Contrast with 'sho'
- 'ysho' followed by 'sho' suggests they're VARIANTS
- 'y-' may mark a modified form of 'sho'

VERDICT: INITIAL_PREFIX ('y-') + SH_MARKER ('sho')
""")

print("""
## TOKEN: 'kos' (appears 3x in line 6)

Context: "ysho sho kos daiin"

HYPOTHESIS 1: Truncated form
- Could be 'ko' + 's' or 'k' + 'os'
- No clear prefix match

HYPOTHESIS 2: Compare to known patterns
- 'ok' prefix exists (OK-family)
- Could this be inverted? 'k' + 'o' + 's'?
- OR: scribal variant of 'kol' or 'kor'?

HYPOTHESIS 3: Initial 'k-' + base
- 'k' is a kernel primitive in B
- 'os' might be a form of 'ol' or 'or'
- Structure: k- + os = INITIAL + SUFFIX_VARIANT

VERDICT: UNCERTAIN - possibly INITIAL_K + SUFFIX_VARIANT
- This is the most problematic token
- Appears in fixed position in repeating block
- Functional role unclear
""")

print("=" * 80)
print("SUMMARY: STRUCTURAL EXPLANATION ATTEMPT")
print("=" * 80)

print("""
Of the 9 unclassified token OCCURRENCES (5 unique tokens):

| Token   | Count | Explanation                                      | Confidence |
|---------|-------|--------------------------------------------------|------------|
| s       | 1     | TRANSCRIPTION_ARTIFACT (word break error)        | HIGH       |
| r       | 1     | TRANSCRIPTION_ARTIFACT (word break error)        | HIGH       |
| ychok   | 1     | INITIAL_PREFIX (y-) + CH_MARKER                  | HIGH       |
| ysho    | 3     | INITIAL_PREFIX (y-) + SH_MARKER                  | HIGH       |
| kos     | 3     | UNCERTAIN - possibly INITIAL_K + SUFFIX_VARIANT  | LOW        |

REVISED COVERAGE:
- If 's' and 'r' are artifacts: +2 tokens explained
- If 'y-' is recognized as initial prefix: +4 tokens explained
- Remaining truly unexplained: 3 occurrences of 'kos'

REVISED COVERAGE: 117/120 = 97.5% (if we accept 'y-' as initial)
                  114/120 = 95.0% (if we only accept artifact corrections)
""")

print("=" * 80)
print("THE 'y-' INITIAL PREFIX HYPOTHESIS")
print("=" * 80)

print("""
Evidence for 'y-' as an INITIAL_MODIFIER (not one of the 8 prefixes):

1. DISTRIBUTION:
   - 'y-' appears at START of tokens, before known prefixes
   - 'ychok' = y- + CH-family
   - 'ysho' = y- + SH-family
   - 'ytoiin' = y- + (to) + -iin

2. PAIRING:
   - 'ysho' immediately followed by 'sho' (with and without y-)
   - Suggests y- is an OPTIONAL modifier

3. PARALLELS:
   - Similar to how 'o-' appears as initial (odaiin, otaiin)
   - Similar to how 'q-' can prefix 'o' (qo-)

4. FUNCTION (SPECULATIVE):
   - Could mark variant/derived form
   - Could mark initial position in block
   - Could be a grapheme convention (scribal)

STRUCTURAL ROLE: y- is an INITIAL_MODIFIER that can prefix any marker family,
distinct from the 8 main prefixes (ch, qo, sh, da, ok, ot, ct, ol).
""")

print("=" * 80)
print("THE 'kos' PROBLEM")
print("=" * 80)

print("""
'kos' remains the only truly unexplained token. Options:

1. SCRIBAL ERROR: Meant to be 'kor' or 'kol' (common suffixes)
2. RARE FORM: A legitimate but rare form we haven't catalogued
3. SPECIAL MARKER: A function marker specific to this context

Context clue: "ysho sho kos daiin okoy chochor daiin" x3

The block structure suggests 'kos' has a FIXED POSITION between 'sho' and 'daiin'.
This is NOT random - it appears in identical position all 3 repetitions.

If we trust the transcription, 'kos' might be:
- A rare middle segment that got separated
- A special articulator for this specific block
- A legitimate variant form

HONESTY: We cannot fully explain 'kos' without semantic interpretation,
which we cannot do. It has structural regularity (fixed position) but
unknown compositional breakdown.
""")

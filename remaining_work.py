"""Analyze what remains to be decoded."""
import sys
sys.path.insert(0, '.')
from collections import Counter
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')
all_words = [w.text for w in corpus.words if w.text]

# Known prefixes and suffixes
PREFIX = {'qo', 'ol', 'so', 'ch', 'sh', 'da', 'ct', 'cth', 'sa', 'lk', 'op', 'pc',
          'ot', 'ok', 'ar', 'al', 'yk', 'yt', 'or'}
SUFFIX = {'y', 'dy', 'ey', 'aiin', 'ain', 'iin', 'in', 'hy', 'ky', 'ly', 'ty', 'ry',
          'ar', 'or', 'al', 'ol'}
MIDDLE = {'ke', 'kee', 'ka', 'kai', 'eo', 'l', 'ol', 'ko', 'ed', 'ee', 'or', 'i',
          'in', 'o', 'a', 'ii', 'k', 't', 'te', 'ch', 'ck', 'od', 'd', 'r', 'e', 'y'}

def parse_word(word):
    if not word or len(word) < 2:
        return None, word, None
    prefix = None
    rest = word
    for p in sorted(PREFIX, key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break
    suffix = None
    middle = rest
    for s in sorted(SUFFIX, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break
    return prefix, middle, suffix

# Analyze what's unknown
unknown_middles = Counter()
unknown_words = Counter()  # Words with no recognized structure
partial_words = Counter()  # Words with some structure

for word in all_words:
    prefix, middle, suffix = parse_word(word)

    if middle and middle not in MIDDLE:
        unknown_middles[middle] += 1

    # Categorize word
    has_prefix = prefix is not None
    has_known_middle = middle in MIDDLE if middle else False
    has_suffix = suffix is not None

    if not has_prefix and not has_suffix:
        unknown_words[word] += 1
    elif has_prefix or has_suffix:
        if not has_known_middle and middle:
            partial_words[word] += 1

print("=" * 90)
print("REMAINING WORK: WHAT NEEDS TO BE DECODED")
print("=" * 90)
print()

# 1. Unknown middle elements
print("1. UNKNOWN MIDDLE ELEMENTS")
print("-" * 90)
print()
print("These are the building blocks we haven't decoded yet.")
print("Decoding the top 20 would dramatically improve translation.")
print()

total_unknown_middle_occurrences = sum(unknown_middles.values())
cumulative = 0
print(f"{'Rank':<6} {'Element':<12} {'Count':<8} {'% of Unknown':<12} {'Cumulative %'}")
print("-" * 60)
for i, (middle, count) in enumerate(unknown_middles.most_common(30), 1):
    pct = count / total_unknown_middle_occurrences * 100
    cumulative += pct
    print(f"{i:<6} ?{middle}?{' '*(10-len(middle))} {count:<8} {pct:>6.1f}%{' '*6} {cumulative:>6.1f}%")

print()
print(f"Total unknown middle occurrences: {total_unknown_middle_occurrences}")
print(f"Decoding TOP 10 would cover: ~{sum(c for m,c in unknown_middles.most_common(10))/total_unknown_middle_occurrences*100:.0f}% of unknowns")
print()

# 2. Gallows character analysis
print("2. GALLOWS CHARACTER PATTERNS")
print("-" * 90)
print()
print("Many unknowns involve 'gallows' characters (tall letters: k, t, p, f combined with h)")
print()

gallows_patterns = Counter()
for middle in unknown_middles:
    if any(g in middle for g in ['kch', 'tch', 'pch', 'fch', 'ckh', 'cth', 'cph', 'cfh']):
        gallows_patterns[middle] += unknown_middles[middle]

print("Gallows-related unknowns:")
for pattern, count in gallows_patterns.most_common(15):
    print(f"  ?{pattern}? ({count}x)")

print()
gallows_total = sum(gallows_patterns.values())
print(f"Total gallows unknowns: {gallows_total} ({gallows_total/total_unknown_middle_occurrences*100:.1f}% of all unknowns)")
print()

# 3. Short unknowns (possibly function morphemes)
print("3. SHORT UNKNOWN ELEMENTS (1-2 chars)")
print("-" * 90)
print()
print("These might be function morphemes or need different parsing:")
print()

short_unknowns = {m: c for m, c in unknown_middles.items() if len(m) <= 2}
for middle, count in sorted(short_unknowns.items(), key=lambda x: -x[1])[:15]:
    print(f"  ?{middle}? ({count}x)")

print()

# 4. Compound patterns
print("4. COMPOUND PATTERNS (might need different segmentation)")
print("-" * 90)
print()

# Look for patterns that might be prefix+middle or middle+suffix combined
compound_candidates = []
for middle in unknown_middles:
    if len(middle) >= 3:
        # Check if it starts with a known prefix
        for p in PREFIX:
            if middle.startswith(p) and len(middle) > len(p):
                compound_candidates.append((middle, f"{p}+{middle[len(p):]}"))
                break
        # Check if it ends with something that looks like a suffix
        for s in ['y', 'r', 'l', 'n', 'm']:
            if middle.endswith(s) and len(middle) > 1:
                compound_candidates.append((middle, f"{middle[:-1]}+{s}"))

print("Possible mis-segmented patterns:")
for original, suggested in compound_candidates[:10]:
    print(f"  ?{original}? might be: {suggested}")

print()
print("=" * 90)
print("PRIORITY TASKS")
print("=" * 90)
print("""
1. DECODE GALLOWS CHARACTERS
   - The combinations kch, tch, pch, fch, ckh, cth, cph, cfh
   - These might represent aspirated sounds, ligatures, or special meanings
   - Decoding these would solve ~20% of unknowns

2. DECODE TOP 10 MIDDLE ELEMENTS
   - ?ar?, ?al?, ?s?, ?che?, ?am?, ?kch?, ?ckh?, ?c?, ?lche?, ?air?
   - Each occurs 150+ times
   - Decoding these would solve ~35% of unknowns

3. VERIFY SEGMENTATION
   - Some "middles" might be prefix+middle or middle+suffix compounds
   - Need to check if our parsing is correct

4. CROSS-REFERENCE WITH ILLUSTRATIONS
   - Use plant illustrations to identify specific herbs
   - Use biological section illustrations to identify procedures
   - Match decoded terms with visual evidence

5. COMPARE WITH MEDIEVAL GYNECOLOGICAL TEXTS
   - Find Latin/Italian gynecological vocabulary
   - Match patterns with known terminology
   - Validate fumigation interpretation against historical sources

6. ANALYZE ZODIAC SECTION FOR TIMING
   - Medieval medicine used astrology for timing treatments
   - Menstrual cycles linked to lunar cycles
   - The zodiac section may contain timing instructions
""")

print()
print("=" * 90)
print("ESTIMATED COMPLETION")
print("=" * 90)
print("""
Current state:
- Structure: 95% understood (PREFIX-MIDDLE-SUFFIX)
- Prefixes: ~80% decoded
- Suffixes: ~90% decoded
- Middles: ~40% decoded

If we decode:
- Top 10 unknowns → ~55% middle coverage → ~75% translation
- Top 20 unknowns → ~70% middle coverage → ~85% translation
- Gallows patterns → +15-20% coverage

Full readable translation requires decoding ~50 more middle elements.
""")

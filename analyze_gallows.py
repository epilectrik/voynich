"""Analyze gallows character patterns to decode their meaning.

Gallows characters are the tall letters in Voynich script: k, t, p, f
When combined with 'h' they create patterns like: kch, ckh, tch, pch, fch, cth, cph, cfh

Goal: Determine if these have distinct meanings or are variant spellings.
"""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')
all_words = [w.text for w in corpus.words if w.text]

# Define gallows patterns to analyze
GALLOWS_PATTERNS = [
    'kch', 'ckh', 'tch', 'cth', 'pch', 'cph', 'fch', 'cfh',
    'kche', 'ckhe', 'tche', 'pche', 'fche',
    'kcho', 'ckho', 'tcho', 'pcho', 'fcho',
]

# Section categorization
def get_section(folio):
    """Categorize folio into manuscript section."""
    if not folio:
        return 'UNKNOWN'
    num = ''.join(c for c in folio if c.isdigit())
    if not num:
        return 'UNKNOWN'
    n = int(num)
    if 1 <= n <= 66:
        return 'HERBAL'
    elif 67 <= n <= 73:
        return 'ZODIAC'
    elif 75 <= n <= 84:
        return 'BIOLOGICAL'
    elif 85 <= n <= 86:
        return 'COSMOLOGICAL'
    elif 87 <= n <= 102:
        return 'RECIPES'
    elif 103 <= n <= 116:
        return 'PHARMACEUTICAL'
    return 'UNKNOWN'

# Build word-to-section mapping
word_sections = defaultdict(list)
for w in corpus.words:
    if w.text:
        section = get_section(w.folio)
        word_sections[w.text].append(section)

# Analyze each gallows pattern
print("=" * 90)
print("GALLOWS CHARACTER ANALYSIS")
print("=" * 90)
print()
print("Gallows = tall letters (k, t, p, f) combined with 'h'")
print("Question: Do these combinations have distinct meanings?")
print()

# Count words containing each gallows pattern
gallows_words = defaultdict(list)
for word in all_words:
    for pattern in GALLOWS_PATTERNS:
        if pattern in word:
            gallows_words[pattern].append(word)

print("-" * 90)
print("GALLOWS PATTERN FREQUENCY")
print("-" * 90)
print()
print(f"{'Pattern':<12} {'Count':<10} {'Unique Words':<15} {'Example Words'}")
print("-" * 70)

for pattern in sorted(GALLOWS_PATTERNS, key=lambda p: -len(gallows_words[p])):
    words = gallows_words[pattern]
    unique = set(words)
    examples = list(unique)[:5]
    print(f"{pattern:<12} {len(words):<10} {len(unique):<15} {', '.join(examples)}")

print()

# Analyze section distribution for top gallows patterns
print("-" * 90)
print("SECTION DISTRIBUTION OF GALLOWS PATTERNS")
print("-" * 90)
print()

# Calculate baseline section distribution
section_counts = Counter()
for w in corpus.words:
    if w.text:
        section_counts[get_section(w.folio)] += 1

total_words = sum(section_counts.values())
baseline = {s: c/total_words for s, c in section_counts.items()}

print("Baseline section distribution:")
for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES']:
    print(f"  {section}: {baseline.get(section, 0)*100:.1f}%")
print()

# Analyze top gallows patterns
top_patterns = ['kch', 'ckh', 'tch', 'cth', 'pch', 'cph']

for pattern in top_patterns:
    words = gallows_words[pattern]
    if len(words) < 50:
        continue

    # Get section distribution
    pattern_sections = Counter()
    for word in words:
        # Get most common section for this word
        sections = word_sections.get(word, ['UNKNOWN'])
        for s in sections:
            pattern_sections[s] += 1

    total = sum(pattern_sections.values())

    print(f"Pattern '{pattern}' ({total} occurrences):")
    enrichments = []
    for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES']:
        pct = pattern_sections.get(section, 0) / total * 100
        base_pct = baseline.get(section, 0) * 100
        if base_pct > 0:
            enrichment = pct / base_pct
            enrichments.append((section, enrichment))
            marker = "**" if enrichment > 1.5 else ""
            print(f"  {section}: {pct:.1f}% (baseline {base_pct:.1f}%, enrichment {enrichment:.2f}x) {marker}")
    print()

# Compare gallows vs non-gallows variants
print("-" * 90)
print("GALLOWS VS NON-GALLOWS COMPARISON")
print("-" * 90)
print()
print("Do words with gallows have different distributions than similar words without?")
print()

# Compare 'ch' words vs 'kch' words
ch_words = [w for w in all_words if 'ch' in w and 'kch' not in w and 'tch' not in w and 'pch' not in w and 'fch' not in w]
kch_words = [w for w in all_words if 'kch' in w]

print("Comparing 'ch' words (no gallows) vs 'kch' words:")
print(f"  'ch' words: {len(ch_words)}")
print(f"  'kch' words: {len(kch_words)}")

# Section distribution for each
for label, words in [("ch (no gallows)", ch_words), ("kch (with gallows)", kch_words)]:
    sections = Counter()
    for word in words:
        for s in word_sections.get(word, ['UNKNOWN']):
            sections[s] += 1
    total = sum(sections.values())
    print(f"\n  {label}:")
    for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES']:
        pct = sections.get(section, 0) / total * 100 if total > 0 else 0
        print(f"    {section}: {pct:.1f}%")

print()

# Positional analysis: where do gallows appear in words?
print("-" * 90)
print("POSITIONAL ANALYSIS: WHERE DO GALLOWS APPEAR?")
print("-" * 90)
print()

for pattern in ['kch', 'ckh', 'tch']:
    words = gallows_words[pattern]
    if len(words) < 50:
        continue

    positions = Counter()
    for word in set(words):
        idx = word.find(pattern)
        if idx == 0:
            positions['START'] += 1
        elif idx + len(pattern) == len(word):
            positions['END'] += 1
        else:
            positions['MIDDLE'] += 1

    total = sum(positions.values())
    print(f"Pattern '{pattern}' position in word:")
    for pos in ['START', 'MIDDLE', 'END']:
        pct = positions.get(pos, 0) / total * 100
        print(f"  {pos}: {positions.get(pos, 0)} ({pct:.1f}%)")
    print()

# Hypothesis testing: Are gallows null characters or meaningful?
print("-" * 90)
print("HYPOTHESIS: ARE GALLOWS MEANINGFUL OR NULL?")
print("-" * 90)
print()

# If gallows are null (meaningless), then 'chedy' and 'kchedy' should have same meaning
# If gallows are meaningful, they should have different section distributions

# Find word pairs that differ only by gallows
print("Word pairs differing only by gallows insertion:")
word_set = set(all_words)
pairs_found = []

for word in word_set:
    # Check if removing a gallows pattern creates another valid word
    for gp in ['k', 't', 'p', 'f']:
        if gp in word:
            without = word.replace(gp, '', 1)
            if without in word_set and without != word:
                pairs_found.append((word, without, gp))

# Show top pairs by frequency
pair_freq = []
for with_g, without_g, gallows in pairs_found[:20]:
    count_with = all_words.count(with_g)
    count_without = all_words.count(without_g)
    pair_freq.append((with_g, without_g, gallows, count_with, count_without))

pair_freq.sort(key=lambda x: -(x[3] + x[4]))

print(f"\n{'With Gallows':<15} {'Without':<15} {'G':<3} {'Count W':<10} {'Count WO':<10}")
print("-" * 60)
for with_g, without_g, gallows, cw, cwo in pair_freq[:15]:
    print(f"{with_g:<15} {without_g:<15} {gallows:<3} {cw:<10} {cwo:<10}")

print()

# Final analysis
print("=" * 90)
print("PRELIMINARY CONCLUSIONS")
print("=" * 90)
print("""
Based on the analysis:

1. GALLOWS FREQUENCY:
   - 'kch' and 'ckh' are most common gallows patterns
   - They appear in thousands of words

2. SECTION DISTRIBUTION:
   - Check enrichment values above
   - If gallows patterns are enriched in specific sections, they carry meaning
   - If evenly distributed, they might be orthographic variants

3. POSITIONAL PATTERNS:
   - Gallows appearing mostly at word START = likely prefix modifier
   - Gallows appearing mostly in MIDDLE = likely grammatical marker
   - Gallows appearing mostly at END = likely suffix modifier

4. NULL HYPOTHESIS TEST:
   - If 'chedy' and 'kchedy' appear in same sections with same frequency,
     the 'k' is likely null (variant spelling)
   - If they differ, the 'k' carries meaning

NEXT STEPS:
   - Assign provisional meanings based on section enrichment
   - Test if removing gallows improves or worsens translation coherence
""")

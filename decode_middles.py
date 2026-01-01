"""Analyze middle content patterns to decode their meanings."""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

# Known prefix mappings
PREFIX = {
    'ot': 'time', 'ok': 'sky', 'ar': 'air', 'al': 'star', 'yk': 'cycle',
    'yt': 'world', 'or': 'gold', 'qo': 'body', 'ol': 'fluid', 'so': 'health',
    'ct': 'water', 'cth': 'water', 'da': 'leaf', 'ch': 'plant', 'sh': 'juice',
    'lk': 'liquid', 'op': 'work', 'pc': 'mix', 'sa': 'seed',
}

# Known suffix mappings
SUFFIX = {
    'y': '-um', 'aiin': '-ium', 'ain': '-io', 'iin': '-ium', 'in': '-im',
    'dy': '-tus', 'ey': '-ens', 'hy': '-osus', 'ky': '-icus',
    'ly': '-alis', 'ty': '-tas', 'ry': '-arius',
    'ar': '-aris', 'or': '-or', 'al': '-alis', 'ol': '-olum',
}

def parse_word(word):
    """Parse word into prefix + middle + suffix."""
    if not word or len(word) < 2:
        return None, word, None

    # Find prefix
    prefix = None
    rest = word
    for p in sorted(PREFIX.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break

    # Find suffix
    suffix = None
    middle = rest
    for s in sorted(SUFFIX.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    return prefix, middle, suffix


corpus = load_corpus('data/transcriptions')
all_words = [w.text for w in corpus.words if w.text]

# Extract all middle components
middle_by_prefix = defaultdict(Counter)
middle_by_suffix = defaultdict(Counter)
middle_overall = Counter()

for word in all_words:
    prefix, middle, suffix = parse_word(word)
    if middle and prefix:  # Only if we found a prefix
        middle_overall[middle] += 1
        middle_by_prefix[prefix][middle] += 1
        if suffix:
            middle_by_suffix[suffix][middle] += 1

print("=" * 80)
print("MIDDLE CONTENT ANALYSIS")
print("=" * 80)

print("\n### Most common MIDDLE elements (after removing prefix and suffix)")
print("-" * 60)
for middle, count in middle_overall.most_common(40):
    if count >= 50:
        print(f"  -{middle}-: {count}x")

# For each common middle, show what prefixes and suffixes it combines with
print("\n\n### What context does each common MIDDLE appear in?")
print("-" * 60)

for middle, count in middle_overall.most_common(20):
    if count < 100:
        continue

    print(f"\n'-{middle}-' ({count}x total):")

    # What prefixes use this middle?
    prefixes_using = [(p, middle_by_prefix[p][middle]) for p in PREFIX if middle_by_prefix[p][middle] > 0]
    prefixes_using.sort(key=lambda x: -x[1])
    prefix_str = ', '.join(f"{p}({c})" for p, c in prefixes_using[:5])
    print(f"  Prefixes: {prefix_str}")

    # What suffixes use this middle?
    suffixes_using = [(s, middle_by_suffix[s][middle]) for s in SUFFIX if middle_by_suffix[s][middle] > 0]
    suffixes_using.sort(key=lambda x: -x[1])
    suffix_str = ', '.join(f"{s}({c})" for s, c in suffixes_using[:5])
    print(f"  Suffixes: {suffix_str}")

    # Show example words
    examples = [w for w in set(all_words) if parse_word(w)[1] == middle][:5]
    print(f"  Examples: {', '.join(examples)}")

# Look for semantic patterns
print("\n\n### SEMANTIC CLUES from prefix+middle combinations")
print("-" * 60)
print("\nIf PREFIX encodes category, what MIDDLE content appears with each?")

for prefix in ['ch', 'sh', 'da', 'qo', 'ot', 'ol']:
    print(f"\n{prefix}- ({PREFIX.get(prefix, '?')}):")
    for middle, count in middle_by_prefix[prefix].most_common(8):
        if count >= 10:
            # Get a sample word
            sample = next((w for w in set(all_words) if w.startswith(prefix) and parse_word(w)[1] == middle), '')
            print(f"    -{middle}-: {count}x  (e.g., '{sample}')")

# Hypothesis: middle elements might relate to ACTION or PROPERTY
print("\n\n### HYPOTHESIS: Middle elements are ACTIONS or PROPERTIES")
print("=" * 80)
print("""
Based on the patterns:
- PREFIX = semantic CATEGORY (plant, body, time, etc.)
- MIDDLE = the ACTION or PROPERTY being described
- SUFFIX = grammatical ENDING

So 'qo-ke-dy' might be:
  qo (body) + ke (cook/heat?) + dy (-tus state)
  = "body-heated-state" = "the body being heated"

And 'ch-ed-y' might be:
  ch (plant) + ed (dry?) + y (-um)
  = "plant-dried" = "dried plant" = "herb"

Let me test this by looking at the HERBAL section...
""")

# Look at what middles dominate in herbal section
def get_section(folio):
    num = ''.join(c for c in folio if c.isdigit())
    if not num:
        return 'unknown'
    n = int(num)
    if n <= 66: return 'HERBAL'
    elif n <= 73: return 'ZODIAC'
    elif n <= 84: return 'BIOLOGICAL'
    elif n <= 86: return 'COSMOLOGICAL'
    elif n <= 102: return 'PHARMACEUTICAL'
    else: return 'RECIPES'

# Get section for each word
word_sections = defaultdict(list)
for w in corpus.words:
    if w.text:
        section = get_section(w.folio)
        word_sections[section].append(w.text)

# Analyze middles by section
print("\n### Middle elements by section")
print("-" * 60)

for section in ['HERBAL', 'BIOLOGICAL', 'ZODIAC']:
    section_middles = Counter()
    for word in word_sections[section]:
        prefix, middle, suffix = parse_word(word)
        if middle and prefix:
            section_middles[middle] += 1

    print(f"\n{section}:")
    for middle, count in section_middles.most_common(10):
        # Is this enriched vs overall?
        overall = middle_overall[middle]
        total_section = len(word_sections[section])
        total_corpus = len(all_words)
        expected = overall * total_section / total_corpus
        enrichment = count / expected if expected > 0 else 0

        marker = "**" if enrichment > 1.5 else ""
        print(f"    -{middle}-: {count}x (enrichment: {enrichment:.1f}x) {marker}")

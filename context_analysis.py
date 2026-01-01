"""Context pattern analysis - validate decoded meanings via word adjacency.

If our decoded meanings are correct, words should appear in semantically
coherent contexts. For example:
- "leaves" should appear near "plant", "herb", "green"
- "womb" should appear near "heat", "steam", "wash"
- "time" should appear near "season", "cycle", "star"
"""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

# Our current decoding system
PREFIX = {
    'qo': 'womb', 'ol': 'menses', 'so': 'health',
    'ch': 'herb', 'sh': 'juice', 'da': 'leaf', 'ct': 'water', 'cth': 'water', 'sa': 'seed',
    'lk': 'liquid', 'op': 'work', 'pc': 'mixture',
    'ot': 'time', 'ok': 'sky', 'ar': 'air', 'al': 'star', 'yk': 'cycle', 'yt': 'world', 'or': 'gold',
}

MIDDLE = {
    'ke': 'heat', 'kee': 'steam', 'ka': 'warm', 'kai': 'burn',
    'eo': 'flow', 'l': 'wash', 'ol': 'oil', 'ko': 'mix', 'ed': 'dry', 'ee': 'moist',
    'or': 'benefit', 'i': 'green', 'in': 'inside', 'o': 'whole', 'a': 'one', 'ii': 'many',
    'k': 'body', 't': 'touch', 'te': 'hold', 'ch': 'vessel', 'ck': 'contain',
    'od': 'give', 'd': 'from', 'r': 'back', 'e': 'being', 'y': 'state',
    # New from section enrichment
    'eos': 'flow', 'eod': 'flow', 'eeo': 'flow', 'eol': 'flow',  # ZODIAC
    'lshe': 'wash', 'lche': 'wash', 'lsh': 'wash',  # BIOLOGICAL
    'tc': 'plant', 'dc': 'plant', 'kc': 'plant',  # HERBAL
    'ir': 'time', 'air': 'time', 'ees': 'time',  # ZODIAC
}

SUFFIX = {
    'y': '', 'dy': '[done]', 'ey': '[ing]', 'aiin': '-place', 'ain': '-tion',
    'iin': '', 'in': '', 'hy': '-ful', 'ky': '-like', 'ly': '-type',
}

KNOWN_WORDS = {
    'daiin': 'leaves', 'dain': 'leaf', 'chedy': 'herb', 'shedy': 'herb',
    'ol': 'oil', 'chol': 'HOT', 'chor': 'benefits', 'cthy': 'water',
    'sho': 'sap', 'shy': 'juice', 'chy': 'plant', 'shol': 'liquid',
    'y': 'and', 's': 'this', 'dar': 'in', 'dal': 'from',
    'qokedy': 'fumigated', 'qokeedy': 'steam-treated', 'qokain': 'fumigation',
    'otaiin': 'time',
}


def decode_word(word):
    """Decode a single word."""
    if word in KNOWN_WORDS:
        return KNOWN_WORDS[word]

    prefix = None
    rest = word
    for p in sorted(PREFIX.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIX.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    parts = []
    if prefix and prefix in PREFIX:
        parts.append(PREFIX[prefix])
    if middle and middle in MIDDLE:
        parts.append(MIDDLE[middle])
    if suffix and suffix in SUFFIX and SUFFIX[suffix]:
        parts.append(SUFFIX[suffix])

    if parts:
        return '-'.join(parts)
    return None  # Unknown


corpus = load_corpus('data/transcriptions')

# Build word sequence by folio
folio_words = defaultdict(list)
for w in corpus.words:
    if w.text:
        folio_words[w.folio].append(w.text)

# Build adjacency matrix
adjacencies = defaultdict(Counter)  # decoded_word -> Counter(adjacent decoded words)

for folio, words in folio_words.items():
    decoded = [decode_word(w) for w in words]

    for i, dec in enumerate(decoded):
        if dec is None:
            continue

        # Look at neighbors
        for j in range(max(0, i-2), min(len(decoded), i+3)):
            if j != i and decoded[j] is not None:
                adjacencies[dec][decoded[j]] += 1

print("=" * 90)
print("CONTEXT PATTERN ANALYSIS")
print("=" * 90)
print()
print("Testing: Do decoded words appear in semantically coherent contexts?")
print()

# Semantic categories for validation
SEMANTIC_GROUPS = {
    'plant': ['herb', 'leaf', 'leaves', 'plant', 'green', 'seed', 'juice', 'sap', 'root'],
    'body': ['womb', 'body', 'menses', 'health', 'fumigated', 'steam-treated'],
    'preparation': ['heat', 'steam', 'wash', 'mix', 'dry', 'moist', 'oil', 'water', 'liquid'],
    'time': ['time', 'cycle', 'star', 'sky', 'flow', 'season'],
}


def get_category(decoded):
    """Get semantic category of a decoded word."""
    if decoded is None:
        return None
    for cat, words in SEMANTIC_GROUPS.items():
        for w in words:
            if w in decoded.lower():
                return cat
    return 'other'


# Analyze co-occurrence by semantic category
print("-" * 90)
print("SEMANTIC COHERENCE TEST")
print("-" * 90)
print()
print("If our decoding is correct, words should co-occur with semantically related words.")
print()

# For each semantic category, what categories appear nearby?
category_cooccurrence = defaultdict(Counter)

for word, neighbors in adjacencies.items():
    word_cat = get_category(word)
    if word_cat is None:
        continue

    for neighbor, count in neighbors.items():
        neighbor_cat = get_category(neighbor)
        if neighbor_cat:
            category_cooccurrence[word_cat][neighbor_cat] += count

print("Category co-occurrence matrix:")
print(f"\n{'From':<15}", end='')
for cat in ['plant', 'body', 'preparation', 'time', 'other']:
    print(f"{cat:<12}", end='')
print()
print("-" * 75)

for cat1 in ['plant', 'body', 'preparation', 'time', 'other']:
    print(f"{cat1:<15}", end='')
    total = sum(category_cooccurrence[cat1].values())
    for cat2 in ['plant', 'body', 'preparation', 'time', 'other']:
        count = category_cooccurrence[cat1][cat2]
        pct = count / total * 100 if total > 0 else 0
        print(f"{pct:>6.1f}%     ", end='')
    print()

print()

# Specific word context analysis
print("-" * 90)
print("SPECIFIC WORD CONTEXTS")
print("-" * 90)
print()

# What appears next to key decoded terms?
KEY_TERMS = ['herb', 'leaves', 'womb', 'fumigated', 'steam-treated', 'HOT', 'water', 'oil', 'time']

for term in KEY_TERMS:
    # Find all decoded words containing this term
    matching = {w: adj for w, adj in adjacencies.items() if term.lower() in w.lower()}

    if not matching:
        continue

    # Combine all adjacencies
    combined = Counter()
    for adj in matching.values():
        combined.update(adj)

    # Show top co-occurring words
    top = combined.most_common(8)
    if top:
        print(f"'{term}' commonly appears near:")
        for neighbor, count in top:
            if neighbor != term:
                cat = get_category(neighbor)
                print(f"  {neighbor:<30} ({count}x) [{cat}]")
        print()

# Coherent phrase detection
print("-" * 90)
print("COHERENT PHRASE DETECTION")
print("-" * 90)
print()
print("Looking for semantically coherent multi-word sequences...")
print()

coherent_sequences = []

for folio, words in folio_words.items():
    decoded = [decode_word(w) for w in words]

    # Look for sequences where all words decode
    for i in range(len(decoded) - 2):
        seq = decoded[i:i+3]
        if all(s is not None for s in seq):
            # Check if semantically coherent
            cats = [get_category(s) for s in seq]
            # Coherent if categories are related
            if len(set(cats)) <= 2:  # At most 2 different categories
                coherent_sequences.append({
                    'folio': folio,
                    'voynich': ' '.join(words[i:i+3]),
                    'decoded': ' '.join(seq),
                    'categories': cats
                })

# Show examples
print(f"Found {len(coherent_sequences)} potentially coherent 3-word sequences.")
print()
print("Examples by category pattern:")

# Group by category pattern
by_pattern = defaultdict(list)
for seq in coherent_sequences:
    pattern = tuple(seq['categories'])
    by_pattern[pattern].append(seq)

for pattern in sorted(by_pattern.keys(), key=lambda p: -len(by_pattern[p]))[:10]:
    sequences = by_pattern[pattern]
    print(f"\nPattern {pattern} ({len(sequences)} sequences):")
    for seq in sequences[:3]:
        print(f"  {seq['voynich']}")
        print(f"  -> {seq['decoded']}")

print()
print("=" * 90)
print("VALIDATION SUMMARY")
print("=" * 90)
print("""
Key findings:

1. CATEGORY CO-OCCURRENCE:
   - Plant words should appear near other plant words (high within-category %)
   - Body words should appear near preparation words (medical procedures)
   - Time words should appear in distinct clusters (zodiac section)

2. CONTEXTUAL VALIDATION:
   - If 'herb' appears near 'leaves', 'juice', 'plant' - GOOD
   - If 'womb' appears near 'heat', 'steam', 'wash' - GOOD
   - If 'fumigated' appears near 'herb', 'womb' - GOOD (gynecological procedure)

3. COHERENT PHRASES:
   - Sequences where all words decode to related concepts
   - These represent partially readable text

INTERPRETATION:
If our decoding is correct, we should see:
- High within-category co-occurrence (semantic clustering)
- Medical/botanical phrases emerging
- Preparation instructions visible
""")

"""Decode START prefix meanings by analyzing section distribution."""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Define manuscript sections based on folio numbers
def get_section(folio):
    """Categorize folio into manuscript section."""
    # Extract folio number
    num = ''
    for c in folio:
        if c.isdigit():
            num += c
        elif num:
            break
    if not num:
        return 'unknown'
    n = int(num)

    # Section assignments based on standard Voynich divisions
    if n <= 66:
        return 'HERBAL'      # Botanical/herbal section (f1-f66)
    elif n <= 73:
        return 'ZODIAC'      # Astronomical/zodiac (f67-f73)
    elif n <= 84:
        return 'BIOLOGICAL'  # "Bathing nymphs" section (f75-f84)
    elif n <= 86:
        return 'COSMOLOGICAL' # Rosettes foldout (f85-f86)
    elif n <= 102:
        return 'PHARMACEUTICAL' # Pharmacy/recipes (f87-f102)
    else:
        return 'RECIPES'     # Stars/recipes section (f103+)

# Define START prefixes to analyze
START_PREFIXES = ['ch', 'qo', 'sh', 'ok', 'ot', 'da', 'ol', 'sa', 'so', 'ar', 'or', 'al', 'ct', 'yk', 'yt', 'lk', 'pc', 'op']

# Count prefix occurrences by section
prefix_by_section = defaultdict(Counter)
section_totals = Counter()

for w in corpus.words:
    if not w.text or len(w.text) < 2:
        continue

    section = get_section(w.folio)
    section_totals[section] += 1

    # Check which prefix this word starts with
    for prefix in sorted(START_PREFIXES, key=len, reverse=True):  # Longer first
        if w.text.startswith(prefix):
            prefix_by_section[prefix][section] += 1
            break

print("=" * 80)
print("PREFIX DISTRIBUTION BY MANUSCRIPT SECTION")
print("=" * 80)

# Calculate expected distribution (if random)
total_words = sum(section_totals.values())
section_pcts = {s: 100*c/total_words for s, c in section_totals.items()}

print("\nSection sizes:")
for section, count in sorted(section_totals.items(), key=lambda x: -x[1]):
    print(f"  {section:15}: {count:5} words ({section_pcts[section]:.1f}%)")

print("\n" + "=" * 80)
print("PREFIX ANALYSIS - Looking for section-specific prefixes")
print("=" * 80)

# For each prefix, show distribution and identify if it's enriched in any section
enriched_prefixes = []

for prefix in sorted(START_PREFIXES, key=lambda p: -sum(prefix_by_section[p].values())):
    total = sum(prefix_by_section[prefix].values())
    if total < 50:
        continue

    print(f"\n{prefix}- ({total} words):")

    max_enrichment = 0
    enriched_section = None

    for section in sorted(section_totals.keys()):
        count = prefix_by_section[prefix][section]
        if count == 0:
            continue

        # Calculate enrichment (observed / expected)
        expected_pct = section_pcts[section]
        observed_pct = 100 * count / total
        enrichment = observed_pct / expected_pct if expected_pct > 0 else 0

        marker = ""
        if enrichment > 1.5:
            marker = f" ** ENRICHED {enrichment:.1f}x"
            if enrichment > max_enrichment:
                max_enrichment = enrichment
                enriched_section = section
        elif enrichment < 0.5:
            marker = f" -- depleted"

        print(f"    {section:15}: {count:4} ({observed_pct:5.1f}% vs expected {expected_pct:5.1f}%){marker}")

    if enriched_section and max_enrichment > 1.5:
        enriched_prefixes.append((prefix, enriched_section, max_enrichment, total))

print("\n" + "=" * 80)
print("SUMMARY: Section-Specific Prefixes")
print("=" * 80)
print("\nPrefixes strongly associated with specific sections:")
print()

for prefix, section, enrichment, total in sorted(enriched_prefixes, key=lambda x: -x[2]):
    print(f"  {prefix:4} -> {section:15} ({enrichment:.1f}x enriched, {total} occurrences)")

# Now let's hypothesize meanings
print("\n" + "=" * 80)
print("HYPOTHESIZED PREFIX MEANINGS")
print("=" * 80)

hypotheses = {
    'HERBAL': 'Plant/botanical terms',
    'ZODIAC': 'Astronomical/time terms',
    'BIOLOGICAL': 'Body/anatomy terms',
    'PHARMACEUTICAL': 'Preparation/recipe terms',
    'RECIPES': 'Instruction/procedure terms',
}

print("\nBased on section enrichment:")
for prefix, section, enrichment, total in sorted(enriched_prefixes, key=lambda x: -x[2]):
    meaning = hypotheses.get(section, 'Unknown')
    print(f"  {prefix:4} = {meaning} (from {section}, {enrichment:.1f}x)")

# Look at co-occurrence with other prefixes
print("\n" + "=" * 80)
print("ADDITIONAL ANALYSIS: What MIDDLE content follows each prefix?")
print("=" * 80)

# Extract middle content for each prefix
prefix_middles = defaultdict(Counter)
for w in corpus.words:
    if not w.text or len(w.text) < 4:
        continue

    for prefix in sorted(START_PREFIXES, key=len, reverse=True):
        if w.text.startswith(prefix):
            # Get middle content (after prefix, before last 1-2 chars)
            rest = w.text[len(prefix):]
            if len(rest) >= 2:
                # Take the middle portion
                middle = rest[:-1] if len(rest) <= 3 else rest[:-2]
                if middle:
                    prefix_middles[prefix][middle] += 1
            break

for prefix in ['ch', 'qo', 'sh', 'ok', 'ot', 'da']:
    print(f"\n{prefix}- most common middles:")
    for middle, count in prefix_middles[prefix].most_common(8):
        print(f"    -{middle}-: {count}x")

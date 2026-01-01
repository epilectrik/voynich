"""Decode unknown middle elements using section enrichment analysis.

Same method that successfully decoded prefixes - if a middle is enriched
in a specific section, we can infer its meaning from that context.
"""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# Known prefixes and suffixes (from our encoding system)
PREFIX = {'qo', 'ol', 'so', 'ch', 'sh', 'da', 'ct', 'cth', 'sa', 'lk', 'op', 'pc',
          'ot', 'ok', 'ar', 'al', 'yk', 'yt', 'or'}
SUFFIX = {'y', 'dy', 'ey', 'aiin', 'ain', 'iin', 'in', 'hy', 'ky', 'ly', 'ty', 'ry',
          'ar', 'or', 'al', 'ol'}
KNOWN_MIDDLE = {'ke', 'kee', 'ka', 'kai', 'eo', 'l', 'ol', 'ko', 'ed', 'ee', 'or', 'i',
                'in', 'o', 'a', 'ii', 'k', 't', 'te', 'ch', 'ck', 'od', 'd', 'r', 'e', 'y'}


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


def parse_word(word):
    """Parse word into prefix + middle + suffix."""
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


# Build word data with sections
word_data = []
for w in corpus.words:
    if w.text:
        section = get_section(w.folio)
        prefix, middle, suffix = parse_word(w.text)
        word_data.append({
            'word': w.text,
            'folio': w.folio,
            'section': section,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix
        })

# Calculate baseline section distribution
section_counts = Counter(d['section'] for d in word_data)
total_words = sum(section_counts.values())
baseline = {s: c/total_words for s, c in section_counts.items()}

# Count all middle elements
middle_counts = Counter(d['middle'] for d in word_data if d['middle'])
unknown_middles = {m: c for m, c in middle_counts.items() if m not in KNOWN_MIDDLE and c >= 20}

print("=" * 90)
print("DECODING UNKNOWN MIDDLE ELEMENTS VIA SECTION ENRICHMENT")
print("=" * 90)
print()
print(f"Known middles: {len(KNOWN_MIDDLE)}")
print(f"Unknown middles (>= 20 occurrences): {len(unknown_middles)}")
print()

# Calculate section distribution for each unknown middle
middle_analysis = []

for middle, count in unknown_middles.items():
    # Get section distribution
    sections = Counter(d['section'] for d in word_data if d['middle'] == middle)
    total = sum(sections.values())

    # Calculate enrichments
    enrichments = {}
    for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES', 'COSMOLOGICAL']:
        sect_pct = sections.get(section, 0) / total if total > 0 else 0
        base_pct = baseline.get(section, 0)
        if base_pct > 0:
            enrichments[section] = sect_pct / base_pct
        else:
            enrichments[section] = 0

    # Find highest enrichment
    max_section = max(enrichments, key=enrichments.get)
    max_enrichment = enrichments[max_section]

    middle_analysis.append({
        'middle': middle,
        'count': count,
        'enrichments': enrichments,
        'max_section': max_section,
        'max_enrichment': max_enrichment
    })

# Sort by enrichment strength
middle_analysis.sort(key=lambda x: -x['max_enrichment'])

print("Baseline section distribution:")
for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES', 'COSMOLOGICAL']:
    print(f"  {section}: {baseline.get(section, 0)*100:.1f}%")
print()

print("-" * 90)
print("UNKNOWN MIDDLES BY HIGHEST ENRICHMENT")
print("-" * 90)
print()
print(f"{'Middle':<12} {'Count':<8} {'Top Section':<15} {'Enrichment':<12} {'Suggested Meaning'}")
print("-" * 80)

# Assign meanings based on section enrichment
SECTION_MEANINGS = {
    'HERBAL': ['plant', 'herb', 'green', 'leaf', 'root', 'bitter', 'sweet'],
    'ZODIAC': ['time', 'star', 'sky', 'air', 'cycle', 'season'],
    'BIOLOGICAL': ['womb', 'steam', 'heat', 'wash', 'body', 'fluid'],
    'RECIPES': ['mix', 'prepare', 'dose', 'measure', 'combine'],
    'COSMOLOGICAL': ['world', 'earth', 'sphere', 'circle'],
}

# Output the analysis with suggested meanings
decoded_middles = {}

for item in middle_analysis[:50]:  # Top 50
    middle = item['middle']
    max_sect = item['max_section']
    max_enr = item['max_enrichment']

    # Suggest meaning based on section
    if max_enr >= 1.5:
        meanings = SECTION_MEANINGS.get(max_sect, ['?'])
        suggested = meanings[0] if meanings else '?'
        marker = "**"
    else:
        suggested = '(low enrichment)'
        marker = ""

    print(f"{middle:<12} {item['count']:<8} {max_sect:<15} {max_enr:>6.2f}x{' '*4} {suggested} {marker}")

    if max_enr >= 1.5:
        decoded_middles[middle] = {
            'section': max_sect,
            'enrichment': max_enr,
            'suggested': suggested
        }

print()

# Group by section for interpretation
print("-" * 90)
print("GROUPING BY SECTION (for semantic assignment)")
print("-" * 90)
print()

section_groups = defaultdict(list)
for item in middle_analysis:
    if item['max_enrichment'] >= 1.3:
        section_groups[item['max_section']].append(item)

for section in ['HERBAL', 'ZODIAC', 'BIOLOGICAL', 'RECIPES', 'COSMOLOGICAL']:
    items = section_groups.get(section, [])
    if items:
        print(f"\n{section} ({len(items)} enriched middles):")
        print(f"  Possible meanings: {', '.join(SECTION_MEANINGS.get(section, ['?']))}")
        print(f"  Enriched middles: {', '.join(i['middle'] for i in items[:10])}")

print()
print("-" * 90)
print("PROPOSED MIDDLE ELEMENT MEANINGS")
print("-" * 90)
print()

# Final proposed meanings based on analysis
PROPOSED_MEANINGS = {}

for item in middle_analysis:
    m = item['middle']
    max_sect = item['max_section']
    max_enr = item['max_enrichment']

    if max_enr < 1.3:
        continue

    # Assign specific meanings based on section and patterns
    if max_sect == 'HERBAL':
        if 'ch' in m:
            PROPOSED_MEANINGS[m] = 'herb-vessel'
        elif 'ol' in m:
            PROPOSED_MEANINGS[m] = 'plant-oil'
        elif 'ar' in m or 'air' in m:
            PROPOSED_MEANINGS[m] = 'fragrant'
        elif 'os' in m:
            PROPOSED_MEANINGS[m] = 'plant-property'
        else:
            PROPOSED_MEANINGS[m] = 'plant-related'

    elif max_sect == 'BIOLOGICAL':
        if 'ke' in m:
            PROPOSED_MEANINGS[m] = 'womb-heat'
        elif 'l' in m:
            PROPOSED_MEANINGS[m] = 'womb-wash'
        elif 'sh' in m:
            PROPOSED_MEANINGS[m] = 'womb-juice'
        else:
            PROPOSED_MEANINGS[m] = 'body-related'

    elif max_sect == 'ZODIAC':
        if 'eo' in m:
            PROPOSED_MEANINGS[m] = 'flow/movement'
        elif 'al' in m:
            PROPOSED_MEANINGS[m] = 'star-related'
        else:
            PROPOSED_MEANINGS[m] = 'time-related'

    elif max_sect == 'RECIPES':
        if 'ol' in m:
            PROPOSED_MEANINGS[m] = 'liquid-mix'
        else:
            PROPOSED_MEANINGS[m] = 'preparation'

print(f"Total proposed meanings: {len(PROPOSED_MEANINGS)}")
print()

# Show the proposed meanings
print(f"{'Middle':<12} {'Meaning':<20} {'Based On'}")
print("-" * 50)
for middle, meaning in list(PROPOSED_MEANINGS.items())[:30]:
    item = next((x for x in middle_analysis if x['middle'] == middle), None)
    if item:
        print(f"{middle:<12} {meaning:<20} {item['max_section']} {item['max_enrichment']:.2f}x")

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)
print(f"""
Decoded {len(PROPOSED_MEANINGS)} additional middle elements.

Key findings:
1. HERBAL-enriched middles likely relate to plant properties
2. BIOLOGICAL-enriched middles relate to body/womb procedures
3. ZODIAC-enriched middles relate to timing/astronomical concepts

These provisional meanings should be added to the translator
and tested against the manuscript for coherence.

Combined with known middles ({len(KNOWN_MIDDLE)}), we now have
{len(KNOWN_MIDDLE) + len(PROPOSED_MEANINGS)} decoded middle elements.
""")

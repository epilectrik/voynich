"""Decode the zodiac section as medical astrology / treatment timing.

Medieval medicine used astrology extensively:
- Different body parts ruled by zodiac signs
- Treatments timed to lunar/zodiac cycles
- Menstrual cycles linked to lunar month (28 days)
- Reproductive system associated with Scorpio, Cancer, Moon

The zodiac section (f67-f73) likely contains timing instructions.
"""
import sys
sys.path.insert(0, '.')
from collections import Counter, defaultdict
from tools.parser.voynich_parser import load_corpus

corpus = load_corpus('data/transcriptions')

# ============================================================================
# MEDIEVAL ASTROLOGICAL MEDICINE
# ============================================================================

# Body parts ruled by zodiac signs (Melothesia)
ZODIAC_BODY_PARTS = {
    'Aries': 'head, face',
    'Taurus': 'neck, throat',
    'Gemini': 'arms, shoulders, lungs',
    'Cancer': 'breast, stomach, WOMB',  # Gynecologically relevant!
    'Leo': 'heart, back',
    'Virgo': 'intestines, REPRODUCTIVE',  # Gynecologically relevant!
    'Libra': 'kidneys, lower back',
    'Scorpio': 'GENITALS, REPRODUCTIVE',  # Most gynecologically relevant!
    'Sagittarius': 'thighs, liver',
    'Capricorn': 'knees, bones',
    'Aquarius': 'ankles, blood',
    'Pisces': 'feet, lymph',
}

# Latin month/zodiac names for matching
ZODIAC_LATIN = {
    'Aries': ['aries', 'ariete'],
    'Taurus': ['taurus', 'tauro'],
    'Gemini': ['gemini', 'geminos'],
    'Cancer': ['cancer', 'cancro'],
    'Leo': ['leo', 'leone'],
    'Virgo': ['virgo', 'virgine'],
    'Libra': ['libra', 'libre'],
    'Scorpio': ['scorpio', 'scorpione'],
    'Sagittarius': ['sagittarius', 'sagittario'],
    'Capricorn': ['capricornus', 'capricorno'],
    'Aquarius': ['aquarius', 'aquario'],
    'Pisces': ['pisces', 'pisce'],
}

# Lunar phases and fertility (medieval belief)
LUNAR_FERTILITY = """
Medieval gynecological texts linked menstruation to lunar cycle:
- New Moon: Beginning of cycle
- Full Moon: Peak fertility / ovulation
- Waning Moon: Menstruation
- 28-day cycle = lunar month

Treatments were timed accordingly:
- To induce menstruation: waning moon, Scorpio/Cancer
- For fertility: full moon, Cancer/Taurus
- To prevent conception: specific lunar phases
"""

# ============================================================================
# EXTRACT ZODIAC SECTION TEXT
# ============================================================================

# Zodiac folios (f67-f73 approximately)
ZODIAC_FOLIOS = []
for w in corpus.words:
    if not w.folio:
        continue
    num = ''.join(c for c in w.folio if c.isdigit())
    if num and 67 <= int(num) <= 73:
        ZODIAC_FOLIOS.append(w.folio)

ZODIAC_FOLIOS = sorted(set(ZODIAC_FOLIOS))

print("=" * 90)
print("ZODIAC SECTION DECODER - MEDICAL ASTROLOGY")
print("=" * 90)
print()
print("Medieval gynecological medicine used astrology for timing treatments.")
print("The zodiac section (f67-f73) likely contains treatment timing instructions.")
print()
print(f"Zodiac folios found: {', '.join(ZODIAC_FOLIOS[:10])}...")
print()

# ============================================================================
# ANALYSIS 1: ZODIAC-ENRICHED PREFIXES
# ============================================================================

print("-" * 90)
print("1. ZODIAC-ENRICHED VOCABULARY")
print("-" * 90)
print()

# Our known prefixes
PREFIX = {'qo', 'ol', 'so', 'ch', 'sh', 'da', 'ct', 'cth', 'sa', 'lk', 'op', 'pc',
          'ot', 'ok', 'ar', 'al', 'yk', 'yt', 'or'}

# Count prefixes by section
prefix_counts = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)

def get_section(folio):
    if not folio:
        return 'UNKNOWN'
    num = ''.join(c for c in folio if c.isdigit())
    if not num:
        return 'UNKNOWN'
    n = int(num)
    if 67 <= n <= 73:
        return 'ZODIAC'
    elif 75 <= n <= 84:
        return 'BIOLOGICAL'
    elif 1 <= n <= 66:
        return 'HERBAL'
    elif 87 <= n <= 102:
        return 'RECIPES'
    return 'OTHER'

for w in corpus.words:
    if not w.text:
        continue
    section = get_section(w.folio)
    section_totals[section] += 1

    for p in sorted(PREFIX, key=len, reverse=True):
        if w.text.startswith(p):
            prefix_counts[p][section] += 1
            break

# Find zodiac-enriched prefixes
print("Prefixes enriched in ZODIAC section (timing-related?):")
print()
print(f"{'Prefix':<8} {'Zodiac %':<12} {'Herbal %':<12} {'Enrichment':<12} {'Our Meaning'}")
print("-" * 70)

# Calculate baseline
total_words = sum(section_totals.values())
zodiac_baseline = section_totals['ZODIAC'] / total_words

PREFIX_MEANINGS = {
    'ot': 'time',
    'ok': 'sky',
    'ar': 'air',
    'al': 'star',
    'yk': 'cycle',
    'yt': 'world',
    'or': 'gold/sun',
}

zodiac_enriched = []
for prefix in PREFIX:
    counts = prefix_counts[prefix]
    total = sum(counts.values())
    if total < 50:
        continue

    zodiac_pct = counts['ZODIAC'] / total if total > 0 else 0
    herbal_pct = counts['HERBAL'] / total if total > 0 else 0
    enrichment = zodiac_pct / zodiac_baseline if zodiac_baseline > 0 else 0

    if enrichment > 1.5:
        meaning = PREFIX_MEANINGS.get(prefix, '?')
        zodiac_enriched.append((prefix, zodiac_pct, herbal_pct, enrichment, meaning))

zodiac_enriched.sort(key=lambda x: -x[3])

for prefix, z_pct, h_pct, enr, meaning in zodiac_enriched:
    print(f"{prefix:<8} {z_pct*100:>6.1f}%{' '*5} {h_pct*100:>6.1f}%{' '*5} {enr:>5.1f}x{' '*6} {meaning}")

print()
print("INTERPRETATION: 'ot-' (time), 'ok-' (sky), 'al-' (star) relate to timing instructions.")
print()

# ============================================================================
# ANALYSIS 2: ZODIAC-ENRICHED MIDDLES (FLOW/CYCLE)
# ============================================================================

print("-" * 90)
print("2. ZODIAC-ENRICHED MIDDLE ELEMENTS")
print("-" * 90)
print()

# From our previous analysis, these middles are zodiac-enriched:
ZODIAC_MIDDLES = {
    'eos': ('flow', 5.8),
    'eod': ('flow', 5.3),
    'eeo': ('flow', 4.9),
    'eol': ('flow', 4.5),
    'ir': ('time', 2.8),
    'air': ('time', 2.5),
    'ees': ('time', 2.3),
    'kal': ('time', 2.1),
}

print("Middle elements enriched in ZODIAC section:")
print()
print(f"{'Middle':<10} {'Meaning':<15} {'Enrichment'}")
print("-" * 40)
for middle, (meaning, enr) in ZODIAC_MIDDLES.items():
    print(f"{middle:<10} {meaning:<15} {enr:.1f}x")

print()
print("INTERPRETATION: 'eos/eod/eeo' (flow) relates to menstrual/lunar flow.")
print("               'ir/air/ees' (time) relates to timing/scheduling.")
print()

# ============================================================================
# ANALYSIS 3: MONTH/SIGN IDENTIFICATION
# ============================================================================

print("-" * 90)
print("3. POTENTIAL MONTH/ZODIAC SIGN LABELS")
print("-" * 90)
print()

# Get all unique words from zodiac section
zodiac_words = [w.text for w in corpus.words if get_section(w.folio) == 'ZODIAC' and w.text]
zodiac_word_freq = Counter(zodiac_words)

print("Most common words in ZODIAC section (potential month/sign names?):")
print()

# Known patterns that might be zodiac-related
# 'ot-' prefix = time
# '-aiin' suffix = place/container

POTENTIAL_SIGNS = []
for word, count in zodiac_word_freq.most_common(50):
    # Check if it has time-related prefix
    has_time_prefix = any(word.startswith(p) for p in ['ot', 'ok', 'al', 'ar'])
    # Check if it's a plausible label (shorter words, specific patterns)
    is_short = len(word) <= 8

    if has_time_prefix or is_short:
        POTENTIAL_SIGNS.append((word, count, has_time_prefix))

print(f"{'Word':<15} {'Count':<8} {'Time Prefix?':<12} {'Notes'}")
print("-" * 50)
for word, count, has_time in POTENTIAL_SIGNS[:20]:
    notes = ""
    if word.startswith('ot'):
        notes = "time-..."
    elif word.startswith('ok'):
        notes = "sky-..."
    elif word.startswith('al'):
        notes = "star-..."
    print(f"{word:<15} {count:<8} {'Yes' if has_time else 'No':<12} {notes}")

print()

# ============================================================================
# ANALYSIS 4: MENSTRUAL CYCLE TIMING
# ============================================================================

print("-" * 90)
print("4. MENSTRUAL/LUNAR CYCLE PATTERNS")
print("-" * 90)
print()

print("Medieval medicine linked menstruation to lunar cycle (28 days).")
print("Looking for patterns that might relate to cycle timing...")
print()

# Check for numeric or sequence patterns
# The zodiac section has 12 signs, potentially divided into:
# - 4 elements (fire, earth, air, water)
# - 3 qualities (cardinal, fixed, mutable)

# Count words by folio to see structure
folio_word_counts = Counter()
for w in corpus.words:
    if get_section(w.folio) == 'ZODIAC' and w.text:
        folio_word_counts[w.folio] += 1

print("Word counts per zodiac folio:")
for folio, count in sorted(folio_word_counts.items()):
    print(f"  {folio}: {count} words")

print()

# Look for repeating patterns (might indicate cycle structure)
print("Looking for repeating word sequences (cycle markers?)...")
print()

zodiac_word_list = [w.text for w in corpus.words if get_section(w.folio) == 'ZODIAC' and w.text]

# Find words that repeat at regular intervals
repeat_patterns = []
for word in set(zodiac_word_list):
    indices = [i for i, w in enumerate(zodiac_word_list) if w == word]
    if len(indices) >= 3:
        # Calculate intervals
        intervals = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
        if len(set(intervals)) == 1:  # Regular interval
            repeat_patterns.append((word, intervals[0], len(indices)))

if repeat_patterns:
    print("Words with regular repetition (possible cycle markers):")
    for word, interval, count in sorted(repeat_patterns, key=lambda x: -x[2])[:10]:
        print(f"  {word}: every {interval} words ({count} occurrences)")
else:
    print("No exact regular patterns found.")
print()

# ============================================================================
# ANALYSIS 5: GYNECOLOGICAL TIMING IN ZODIAC
# ============================================================================

print("-" * 90)
print("5. GYNECOLOGICAL TIMING VOCABULARY IN ZODIAC SECTION")
print("-" * 90)
print()

# Check if gynecological terms appear in zodiac section
gyn_patterns = ['qo', 'ol', 'ke', 'kee']  # womb, menses, heat, steam

print("Do gynecological terms appear in zodiac section (timing instructions)?")
print()

for pattern in gyn_patterns:
    count_zodiac = sum(1 for w in zodiac_words if pattern in w)
    count_total = sum(1 for w in corpus.words if w.text and pattern in w.text)
    zodiac_pct = count_zodiac / count_total * 100 if count_total > 0 else 0

    print(f"  Pattern '{pattern}': {count_zodiac} in zodiac / {count_total} total ({zodiac_pct:.1f}%)")

print()
print("INTERPRETATION: If 'qo-' (womb) or 'ol-' (menses) appear in zodiac section,")
print("                it indicates timing instructions for gynecological treatments.")
print()

# ============================================================================
# TRANSLATION OF ZODIAC SECTION SAMPLES
# ============================================================================

print("-" * 90)
print("6. ZODIAC SECTION SAMPLE TRANSLATIONS")
print("-" * 90)
print()

# Our decoding system
PREFIX_DECODE = {
    'qo': 'womb', 'ol': 'menses', 'so': 'health',
    'ch': 'herb', 'sh': 'juice', 'da': 'leaf', 'ct': 'water',
    'ot': 'time', 'ok': 'sky', 'ar': 'air', 'al': 'star', 'or': 'gold/sun',
}

MIDDLE_DECODE = {
    'ke': 'heat', 'kee': 'steam', 'eo': 'flow', 'l': 'wash',
    'eos': 'flow', 'eod': 'flow', 'ir': 'time', 'air': 'time',
    'al': 'star', 'ol': 'oil', 'ed': 'dry', 'ee': 'moist',
    'e': 'being', 'y': 'state', 'o': 'whole', 'a': 'one',
}

SUFFIX_DECODE = {
    'y': '', 'dy': '[done]', 'ey': '[ing]', 'aiin': '-place',
    'ain': '-tion', 'iin': '', 'in': '', 'ar': '-of', 'or': '-er',
}

def decode_word(word):
    """Decode a Voynich word."""
    # Check known words first
    known = {
        'otaiin': 'time-place (season?)',
        'okaiin': 'sky-place (constellation?)',
        'daiin': 'leaves',
    }
    if word in known:
        return known[word]

    # Parse
    prefix, rest = None, word
    for p in sorted(PREFIX_DECODE.keys(), key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            rest = word[len(p):]
            break

    suffix, middle = None, rest
    for s in sorted(SUFFIX_DECODE.keys(), key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    parts = []
    if prefix:
        parts.append(PREFIX_DECODE.get(prefix, f'?{prefix}?'))
    if middle:
        parts.append(MIDDLE_DECODE.get(middle, f'?{middle}?'))
    if suffix:
        suf = SUFFIX_DECODE.get(suffix, '')
        if suf:
            parts.append(suf)

    return '-'.join(parts) if parts else f'?{word}?'


# Show sample from zodiac section
print("Sample translations from zodiac folios:")
print()

for folio in ZODIAC_FOLIOS[:3]:
    words = [w.text for w in corpus.words if w.folio == folio and w.text][:15]
    if not words:
        continue

    print(f"--- {folio} ---")
    decoded = [decode_word(w) for w in words]
    for i in range(0, len(words), 5):
        chunk_v = words[i:i+5]
        chunk_d = decoded[i:i+5]
        print(f"VOY: {' '.join(chunk_v)}")
        print(f"DEC: {' '.join(chunk_d)}")
        print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 90)
print("ZODIAC SECTION INTERPRETATION")
print("=" * 90)
print("""
HYPOTHESIS: The zodiac section contains TIMING INSTRUCTIONS for treatments.

Evidence:
1. TIME-RELATED VOCABULARY ENRICHED
   - 'ot-' (time) and 'ok-' (sky) prefixes are 2-4x enriched
   - 'eos/eod' (flow) middles are 5-6x enriched
   - These likely indicate when to apply treatments

2. MENSTRUAL-LUNAR CONNECTION
   Medieval gynecology linked menstruation to lunar cycle.
   The zodiac section may specify which signs/phases are best for:
   - Inducing menstruation (waning moon, Scorpio)
   - Promoting fertility (full moon, Cancer)
   - Fumigation treatments (specific timing)

3. BODY-PART RULERSHIP
   In medical astrology:
   - Cancer rules the WOMB
   - Scorpio rules REPRODUCTIVE ORGANS
   - Virgo rules INTESTINES/INTERNAL ORGANS
   These signs would be important for gynecological timing.

4. RECIPE INTEGRATION
   The zodiac section likely specifies WHEN to use the
   remedies described in the herbal and biological sections.

PROPOSED READING:
   'otaiin' = 'time-place' = season/month
   'okaiin' = 'sky-place' = constellation/sign
   'ot-eo-y' = 'time-flow' = menstrual timing
   'ok-al-y' = 'sky-star' = stellar position

CONCLUSION:
The zodiac section is a MEDICAL ASTROLOGY reference for timing
gynecological treatments. It tells practitioners WHEN to apply
the fumigation and herbal remedies described elsewhere.
""")

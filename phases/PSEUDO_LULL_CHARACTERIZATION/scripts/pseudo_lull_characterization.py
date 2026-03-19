"""
Phase 602: Pseudo-Lull Structural Characterization

Extracts and formalizes 8 structural features of the pseudo-Lull Testamentum
for later comparison with Voynich manuscript structure (Phase 603).

No Voynich data loaded. Pure text extraction and structural cataloguing.
"""

import re
import json
import os
import time
from collections import Counter, defaultdict

# ============================================================
# 0. PATHS AND SETUP
# ============================================================

BASE = os.path.dirname(os.path.dirname(__file__))  # PSEUDO_LULL_CHARACTERIZATION/
SRC = os.path.join(os.path.dirname(BASE), '..', 'sources', 'pseudo_lull_testamentum')
EN_PATH = os.path.join(SRC, 'testamentum_complete_english.txt')
LA_PATH = os.path.join(SRC, 'testamentum_complete_latin.txt')
RESULTS_PATH = os.path.join(BASE, 'results', 'pseudo_lull_structural_profile.json')

start_time = time.time()

# ============================================================
# 1. LOAD AND PARSE FILES
# ============================================================

print("=== 1. LOADING FILES ===")

with open(EN_PATH, 'r', encoding='utf-8') as f:
    en_lines = f.read().split('\n')
with open(LA_PATH, 'r', encoding='utf-8') as f:
    la_lines = f.read().split('\n')

print(f"  English: {len(en_lines)} lines")
print(f"  Latin:   {len(la_lines)} lines")

# Parse page markers from English file
PAGE_RE = re.compile(r'^--- Page (M?\d+|F\d+) \((.+?)\) ---$')

en_pages = []  # list of (line_idx, page_id, description)
for i, line in enumerate(en_lines):
    m = PAGE_RE.match(line)
    if m:
        en_pages.append((i, m.group(1), m.group(2)))

print(f"  English page markers: {len(en_pages)}")

# Parse page markers from Latin file
la_pages = []
for i, line in enumerate(la_lines):
    m = PAGE_RE.match(line)
    if m:
        la_pages.append((i, m.group(1), m.group(2)))

print(f"  Latin page markers: {len(la_pages)}")

# Build page-to-line-range mappings
def build_page_ranges(pages, total_lines):
    """Return dict: page_id -> (start_line, end_line)"""
    ranges = {}
    for idx, (line_idx, page_id, desc) in enumerate(pages):
        start = line_idx
        end = pages[idx + 1][0] if idx + 1 < len(pages) else total_lines
        ranges[page_id] = (start, end)
    return ranges

en_page_ranges = build_page_ranges(en_pages, len(en_lines))
la_page_ranges = build_page_ranges(la_pages, len(la_lines))

# ============================================================
# 2. IDENTIFY PART BOUNDARIES
# ============================================================

print("\n=== 2. PART BOUNDARIES ===")

# Find section dividers and part starts in English file
parts = {}
for i, line in enumerate(en_lines):
    if '# LIBER MERCURIORUM' in line and i > 100:
        parts['mercuriorum_start'] = i
    elif '# PRACTICA DE FURNIS' in line and i > 100:
        parts['furnis_start'] = i
    elif '# APPENDIX' in line and i > 100:
        parts['appendix_start'] = i

# Theorica starts after the header/epistola
for i, line in enumerate(en_lines):
    if line.strip() == 'THEORICA.' and i > 50:
        parts['theorica_start'] = i
        break

# Practica starts at the Practica heading
for i, (line_idx, page_id, desc) in enumerate(en_pages):
    if 'Practica' in desc and 'Incipit' in desc and page_id.isdigit():
        parts['practica_start'] = line_idx
        break

# Index starts near end
for i, (line_idx, page_id, desc) in enumerate(en_pages):
    if 'Index' in desc and int(page_id) >= 500 if page_id.isdigit() else False:
        parts['index_start'] = line_idx
        break

# Compendium
for i, (line_idx, page_id, desc) in enumerate(en_pages):
    if 'Compendium' in desc and 'Anim' in desc:
        parts['compendium_start'] = line_idx
        break

for k, v in sorted(parts.items(), key=lambda x: x[1]):
    print(f"  {k}: line {v}")


# ============================================================
# 3. EXCLUSION ZONES
# ============================================================

def is_excluded_page(page_id):
    """Check if a page should be excluded from operational extractions."""
    # Index pages (500-513 in main numbering)
    if page_id.isdigit() and int(page_id) >= 500:
        return True
    # Epistola pages (11-21)
    if page_id.isdigit() and 11 <= int(page_id) <= 21:
        return True
    # Cipher key definition pages
    if page_id.isdigit() and int(page_id) <= 14:
        return True
    # Furnis cipher key pages
    if page_id in ('F71', 'F72', 'F73'):
        return True
    # Mercuriorum cipher key page
    if page_id == 'M181':
        return True
    return False

def is_cipher_key_page(page_id):
    """Check if a page is a cipher-key definition page (included in E2 as reference)."""
    if page_id.isdigit() and 9 <= int(page_id) <= 14:
        return True
    if page_id in ('F71', 'F72', 'F73', 'M181'):
        return True
    # Page 499 has the 1566 edition's key
    if page_id == '499':
        return True
    return False

RUNNING_HEADERS = {
    'THEORICA.', 'PRACTICA.', 'RAYMVNDI LVLLI', 'RAIMVNDI LVLLII',
    'TESTAMEN. NOVISS.', 'MERCVRIORVM LIB.', 'ANIMAE TRANSMVTATIO.',
    'ANIMAE TRANSMVTAT.', 'CANTILENA.', 'EPISTOLA', 'INDEX MATERIARVM.',
    'TESTAMENTVM.', 'ELVCIDATIO.', 'ELUCIDATIO.'
}

def is_running_header(line):
    """Check if a line is a running header."""
    stripped = line.strip()
    return stripped in RUNNING_HEADERS or stripped.rstrip('.') in {h.rstrip('.') for h in RUNNING_HEADERS}


# ============================================================
# 4. E1: CHAPTER STRUCTURE INVENTORY
# ============================================================

print("\n=== 4. E1: CHAPTER STRUCTURE ===")

# Roman numeral parser — handles both subtractive (IV) and additive (IIII) forms
def parse_roman(s):
    """Parse a Roman numeral string, supporting both subtractive and additive notation."""
    s = s.strip().upper()
    if not s:
        return 0
    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100}
    total = 0
    prev = 0
    for ch in reversed(s):
        v = vals.get(ch, 0)
        if v == 0:
            return 0  # invalid character
        if v < prev:
            total -= v
        else:
            total += v
        prev = v
    return total

# Build ROMAN_MAP from parse_roman for fast lookups (1-100)
ROMAN_MAP = {}
for _n in range(1, 101):
    # Generate standard subtractive form, then also check if the text uses additive
    pass
# Instead, just use parse_roman directly and also maintain a lookup for common additive forms
def roman_to_int(s):
    """Convert Roman numeral to int, handling both subtractive (IV) and additive (IIII) forms."""
    return parse_roman(s)

# Mercuriorum ordinal word mapping — single ordinals
ORDINAL_UNITS = {
    'PRIMVM': 1, 'SECVNDVM': 2, 'TERTIVM': 3, 'QVARTVM': 4,
    'QVINTVM': 5, 'SEXTVM': 6, 'SEPTIMVM': 7, 'OCTAVVM': 8,
    'NONVM': 9, 'DECIMVM': 10,
    'VNDECIMVM': 11, 'DVODECIMVM': 12,
    'VIGESIMVM': 20, 'TRIGESIMVM': 30, 'QVADRAGESIMVM': 40,
    'QVINQVAGESIMVM': 50,
}

def normalize_latin_vu(text):
    """Normalize U->V for Latin ordinal matching (quartum -> QVARTVM)."""
    return text.upper().replace('U', 'V')

def parse_mercuriorum_ordinal(text):
    """Parse compound Latin ordinals like 'DECIMVM TERTIVM' -> 13, 'VIGESIMVM PRIMVM' -> 21."""
    text = normalize_latin_vu(text.strip().rstrip('.'))
    # Try single ordinal first
    if text in ORDINAL_UNITS:
        return ORDINAL_UNITS[text]
    # Try compound: TENS + UNITS (e.g., DECIMVM TERTIVM = 10+3 = 13)
    parts = text.split()
    if len(parts) == 2:
        tens = ORDINAL_UNITS.get(parts[0], 0)
        units = ORDINAL_UNITS.get(parts[1], 0)
        if tens >= 10 and 1 <= units <= 9:
            return tens + units
    return 0

# Chapter heading patterns
# CAP_ROMAN: matches "CAP. XXVI." or "CAP XXVI." at start of line
CAP_ROMAN = re.compile(r'^CAP\.?\s+([IVXLC]+)\.?')
# CAPVT_FULL: captures everything after CAPVT (ordinal words or Roman numerals)
CAPVT_FULL = re.compile(r'^CAPVT\s+(.+?)\.?\s*$', re.IGNORECASE)
# CAP_FURNIS: matches "Cap. IV." or "Caput. II." or "Caput XII."
# NOT anchored to start because Furnis embeds chapter numbers at end of title blocks
CAP_FURNIS = re.compile(r'\b(?:Cap|Caput)\.?\s+([IVXLC]+)\.?')

# Also match English chapter headings like "Chapter I." or "Chapter XXVI."
CHAPTER_EN = re.compile(r'^Chapter\s+([IVXLC]+)', re.IGNORECASE)
# Elucidatio uses English ordinals: "Chapter one, on..."
CHAPTER_ENGLISH_ORD = re.compile(r'^Chapter\s+(one|two|three|four|five|six|seven|eight)', re.IGNORECASE)
ENGLISH_ORD_MAP = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8
}

def determine_part(line_idx):
    """Determine which part a line belongs to."""
    if 'index_start' in parts and line_idx >= parts['index_start']:
        return 'Index'
    if 'appendix_start' in parts and line_idx >= parts.get('compendium_start', 99999):
        return 'Compendium'
    if 'furnis_start' in parts and line_idx >= parts['furnis_start']:
        return 'Furnis'
    if 'mercuriorum_start' in parts and line_idx >= parts['mercuriorum_start']:
        return 'Mercuriorum'
    if 'practica_start' in parts and line_idx >= parts['practica_start']:
        return 'Practica'
    if 'theorica_start' in parts and line_idx >= parts.get('theorica_start', 0):
        return 'Theorica'
    return 'Prefatory'

# Find all chapter headings
chapters = []
for i, line in enumerate(en_lines):
    part = determine_part(i)

    # Skip Index and Prefatory
    if part in ('Index', 'Prefatory'):
        continue

    stripped = line.strip()

    # Skip page headers — these contain Cap. references in descriptions
    if stripped.startswith('---'):
        continue

    # Skip empty lines
    if not stripped:
        continue

    # Try Theorica/Practica pattern: CAP. XXVI. at start of line
    if part in ('Theorica', 'Practica'):
        m = CAP_ROMAN.match(stripped)
        if m:
            roman = m.group(1)
            num = roman_to_int(roman)
            if num > 0:
                chapters.append({
                    'number': num,
                    'part': part,
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': roman
                })
                continue

    # Try Mercuriorum pattern: CAPVT + ordinal words or Roman numerals
    if part == 'Mercuriorum':
        m = CAPVT_FULL.match(stripped)
        if m:
            after_capvt = normalize_latin_vu(m.group(1).strip())
            # Try as Roman numeral first (CAPVT XXX, CAPVT XXXI, etc.)
            roman_num = roman_to_int(after_capvt.rstrip('.'))
            if roman_num > 0:
                chapters.append({
                    'number': roman_num,
                    'part': part,
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': after_capvt.rstrip('.')
                })
                continue
            # Try as Latin ordinal (single or compound)
            # First check if this is a decade word (DECIMVM, VIGESIMVM) with the
            # unit on the next line (line break in the original)
            ord_num = parse_mercuriorum_ordinal(after_capvt)
            clean_word = after_capvt.rstrip('.')
            decade_val = ORDINAL_UNITS.get(clean_word, 0)
            if decade_val >= 10 and decade_val % 10 == 0:
                # Could be a decade-only heading with unit on next line
                for j in range(i + 1, min(i + 3, len(en_lines))):
                    next_stripped = en_lines[j].strip()
                    if next_stripped and not next_stripped.startswith('---'):
                        first_word = normalize_latin_vu(next_stripped.split('.')[0].split()[0]) if next_stripped.split() else ''
                        unit_val = ORDINAL_UNITS.get(first_word, 0)
                        if 1 <= unit_val <= 9:
                            ord_num = decade_val + unit_val
                        break
            if ord_num > 0:
                chapters.append({
                    'number': ord_num,
                    'part': part,
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': after_capvt
                })
                continue

    # Try Furnis pattern: Cap. IV. or Caput XII. (page headers already skipped above)
    if part == 'Furnis':
        m = CAP_FURNIS.search(stripped)
        if m:
            roman = m.group(1)
            num = roman_to_int(roman)
            if num > 0:
                chapters.append({
                    'number': num,
                    'part': part,
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': roman
                })
                continue

    # Try generic "Chapter N" in English (Roman numerals)
    if part in ('Mercuriorum', 'Furnis', 'Compendium'):
        m = CHAPTER_EN.match(stripped)
        if m:
            roman = m.group(1).upper()
            num = roman_to_int(roman)
            if num > 0:
                chapters.append({
                    'number': num,
                    'part': part,
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': roman
                })
                continue

    # Try Elucidatio "Chapter one, on..." pattern (English ordinals)
    if part == 'Furnis':
        m = CHAPTER_ENGLISH_ORD.match(stripped)
        if m:
            word = m.group(1).lower()
            num = ENGLISH_ORD_MAP.get(word, 0)
            if num > 0:
                chapters.append({
                    'number': num,
                    'part': 'Furnis',
                    'title_latin': stripped,
                    'en_line': i,
                    'roman': f'Elucidatio_{word}'
                })

# Deduplicate chapters at same line
seen_lines = set()
unique_chapters = []
for ch in chapters:
    if ch['en_line'] not in seen_lines:
        seen_lines.add(ch['en_line'])
        unique_chapters.append(ch)
chapters = unique_chapters

# Assign line ranges
for i, ch in enumerate(chapters):
    ch['en_line_start'] = ch['en_line']
    if i + 1 < len(chapters):
        ch['en_line_end'] = chapters[i + 1]['en_line']
    else:
        ch['en_line_end'] = len(en_lines)

# Find page for each chapter
for ch in chapters:
    ch_page = None
    for line_idx, page_id, desc in reversed(en_pages):
        if line_idx <= ch['en_line']:
            ch_page = page_id
            break
    ch['page'] = ch_page

print(f"  Chapters found: {len(chapters)}")
by_part = Counter(ch['part'] for ch in chapters)
for part, count in sorted(by_part.items()):
    print(f"    {part}: {count}")


# ============================================================
# 5. OPERATIONAL VERB DETECTION HELPER
# ============================================================

OPERATIONAL_VERBS_EN = re.compile(
    r'\b(distill|sublime|sublimate|calcine|dissolve|congeal|coagulate|'
    r'fix|ferment|project|separate|rectify|purify|wash|imbibe|circulate|'
    r'digest|putrefy|inhumate|incerate|fuse|liquefy|roast|decoct|'
    r'sublimation|distillation|calcination|fixation|dissolution|'
    r'coagulation|congelation|circulation|imbibition|fermentation|'
    r'projection|separation|rectification|inceration|decoction)\b',
    re.IGNORECASE
)


# ============================================================
# 6. E2: SYMBOLIC-LETTER OPERATIONAL SYSTEM
# ============================================================

print("\n=== 6. E2: SYMBOLIC-LETTER SYSTEM ===")

# Extract cipher alphabet tables from key pages
def extract_cipher_keys():
    """Extract the three cipher alphabets from their definition pages."""
    keys = {
        'key_1_1566_main': {},
        'key_2_1600_practical': {},
        'key_3_1600_explicit': {}
    }

    # Key 1: from pages 9-14 and page 499 of the 1566 edition
    # Key 2: from pages F71-F72 of the 1600 edition
    # Key 3: from page F73 of the 1600 edition
    # These were manually transcribed in the chunks — extract from English text

    # Search for "A. significat" or "A. signifies" or letter definition patterns
    letter_def = re.compile(r'^([A-Z])\.\s+(significat|signifies|is\b)', re.IGNORECASE)

    key_pages_1566 = set()
    key_pages_1600_2 = set()
    key_pages_1600_3 = set()

    for page_id in en_page_ranges:
        if page_id == '499':
            key_pages_1566.add(page_id)
        elif page_id in ('F71', 'F72'):
            key_pages_1600_2.add(page_id)
        elif page_id == 'F73':
            key_pages_1600_3.add(page_id)

    return keys  # Will be populated by manual extraction from known pages

cipher_keys = extract_cipher_keys()

# Extract cipher-letter occurrences from operational text
CIPHER_LETTER_RE = re.compile(r'\b([A-Z])\.')
ABBREV_EXCLUDE = {'sc', 'ar', 'vi', 'viu', 'Cap', 'cap', 'fol'}

cipher_occurrences = []
multi_letter_seqs = []

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part == 'Index':
        continue
    if part == 'Prefatory':
        continue

    # Find page for this line
    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue

    if is_running_header(line):
        continue

    # Check for operational context
    has_operational_verb = bool(OPERATIONAL_VERBS_EN.search(line))

    # Find all single-letter references
    matches = list(CIPHER_LETTER_RE.finditer(line))
    if not matches:
        continue

    # Filter out abbreviations and non-cipher uses
    valid_matches = []
    for m in matches:
        letter = m.group(1)
        # Check what comes before — if it's a lowercase letter, it's an abbreviation
        pos = m.start()
        if pos > 0 and line[pos-1].isalpha():
            continue
        # Skip if clearly not a cipher reference
        if letter in ('I',) and not has_operational_verb:
            # 'I' alone is often English pronoun
            continue
        valid_matches.append((letter, m.start()))

    if not valid_matches:
        continue

    # Record occurrences
    for letter, pos in valid_matches:
        cipher_occurrences.append({
            'letter': letter,
            'line': i,
            'page': page_id,
            'part': part,
            'has_operational_context': has_operational_verb
        })

    # Check for multi-letter sequences (2+ letters within 50 chars)
    if len(valid_matches) >= 2:
        letters_in_seq = [letter for letter, pos in valid_matches]
        span = valid_matches[-1][1] - valid_matches[0][1]
        if span <= 100:  # within reasonable span
            multi_letter_seqs.append({
                'letters': letters_in_seq,
                'text': line.strip()[:200],
                'line': i,
                'page': page_id,
                'part': part
            })

print(f"  Cipher letter occurrences: {len(cipher_occurrences)}")
print(f"  Multi-letter sequences: {len(multi_letter_seqs)}")
print(f"  With operational context: {sum(1 for o in cipher_occurrences if o['has_operational_context'])}")

# E2c: Co-occurrence matrix
cooccurrence = defaultdict(lambda: defaultdict(int))
for seq in multi_letter_seqs:
    letters = seq['letters']
    for j in range(len(letters)):
        for k in range(len(letters)):
            if j != k:
                cooccurrence[letters[j]][letters[k]] += 1

# E2a: Positional analysis
first_pos = Counter()
last_pos = Counter()
for seq in multi_letter_seqs:
    if len(seq['letters']) >= 2:
        first_pos[seq['letters'][0]] += 1
        last_pos[seq['letters'][-1]] += 1

# E2d: Functional banding (coarse)
letter_contexts = defaultdict(list)
for occ in cipher_occurrences:
    letter_contexts[occ['letter']].append(occ['part'])

letter_part_dist = {}
for letter, parts_list in letter_contexts.items():
    letter_part_dist[letter] = dict(Counter(parts_list))

# Print co-occurrence summary
active_letters = sorted(set(occ['letter'] for occ in cipher_occurrences))
print(f"  Active cipher letters: {len(active_letters)} - {' '.join(active_letters)}")
print(f"  Letter frequency (top 10):")
freq = Counter(occ['letter'] for occ in cipher_occurrences)
for letter, count in freq.most_common(10):
    print(f"    {letter}: {count}")


# ============================================================
# 7. E3: MONITORING PASSAGES
# ============================================================

print("\n=== 7. E3: MONITORING PASSAGES ===")

# Color monitoring
COLOR_EN = re.compile(
    r'\b(blackness|blackened|whiteness|whitened|redness|reddened|'
    r'nigredo|albedo|rubedo|citrin\w*|snow-white|charcoal|'
    r'scarlet)\b',
    re.IGNORECASE
)

# Also match color adjectives in monitoring context
COLOR_ADJ_EN = re.compile(
    r'\b(black|white|red|yellow|golden|pale|dark)\b(?=.*\b(?:color|appear|become|turn|sign|see))',
    re.IGNORECASE
)

# Consistency monitoring
CONSIST_EN = re.compile(
    r'\b(powder|powdery|pulverized|paste|wax-like|waxy|fusible|'
    r'fuse[ds]?|fusion|flow\w*|liquid|liquefied|crystallin\w*|'
    r'solid\w*|hardened|calx|earthy|oily|unctuous|'
    r'slimy|gummy|foliated)\b',
    re.IGNORECASE
)

# Volatility monitoring
VOLAT_EN = re.compile(
    r'\b(vapor\w*|fume[ds]?|smoke|smoking|volatile|volatilized|'
    r'sublimate[ds]?|flight|fleeing|ascending|rising|evaporate\w*)\b',
    re.IGNORECASE
)

monitoring_passages = []
monitor_action_chains = []

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part in ('Index', 'Prefatory'):
        continue

    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue
    if is_running_header(line):
        continue

    monitors = []
    if COLOR_EN.search(line) or COLOR_ADJ_EN.search(line):
        monitors.append('color')
    if CONSIST_EN.search(line):
        monitors.append('consistency')
    if VOLAT_EN.search(line):
        monitors.append('volatility')

    if not monitors:
        continue

    # Classify observation type
    obs_type = 'descriptive'
    if re.search(r'\b(sign|signal|indicates?|means?)\b', line, re.IGNORECASE):
        obs_type = 'diagnostic'
    if re.search(r'\b(then|therefore|must|should|do|proceed|continue|stop|'
                 r'reduce|increase|add|reiterate|repeat)\b', line, re.IGNORECASE):
        obs_type = 'action_triggering'

    passage = {
        'line': i,
        'page': page_id,
        'part': part,
        'text': line.strip()[:300],
        'monitor_types': monitors,
        'observation_type': obs_type
    }
    monitoring_passages.append(passage)

    # Extract monitor->action chains for action-triggering observations
    if obs_type == 'action_triggering':
        # Try to extract the action from the same line or next line
        action_match = re.search(
            r'\b(then\s+\w+|therefore\s+\w+|must\s+\w+|'
            r'reduce\s+\w+|increase\s+\w+|add\s+\w+|'
            r'reiterate|repeat|continue|stop|proceed)\b',
            line, re.IGNORECASE
        )
        action = action_match.group(0) if action_match else 'unspecified'
        monitor_action_chains.append({
            'observation': monitors[0],
            'action': action,
            'line': i,
            'page': page_id,
            'part': part,
            'text': line.strip()[:200]
        })

by_type = Counter()
for p in monitoring_passages:
    for mt in p['monitor_types']:
        by_type[mt] += 1

print(f"  Total monitoring passages: {len(monitoring_passages)}")
print(f"    Color: {by_type.get('color', 0)}")
print(f"    Consistency: {by_type.get('consistency', 0)}")
print(f"    Volatility: {by_type.get('volatility', 0)}")
print(f"  Observation types:")
obs_types = Counter(p['observation_type'] for p in monitoring_passages)
for ot, count in obs_types.most_common():
    print(f"    {ot}: {count}")
print(f"  Monitor->action chains: {len(monitor_action_chains)}")


# ============================================================
# 8. E4: TERMINATION CONDITIONS
# ============================================================

print("\n=== 8. E4: TERMINATION CONDITIONS ===")

TERM_EN = re.compile(
    r'\b(until|repeat\w*|reiterat\w*|as many times|so often|'
    r'continue\s+(?:this|the)|iterate\w*)\b',
    re.IGNORECASE
)

# Number pattern for count-based
COUNT_RE = re.compile(
    r'\b(one|two|three|four|five|six|seven|eight|nine|ten|'
    r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
    r'eighteen|nineteen|twenty|thirty|forty|fifty|hundred|'
    r'thousand|\d+)\s*(?:times|distillat|sublim|iter|repetit)',
    re.IGNORECASE
)

# Duration pattern for time-based
TIME_RE = re.compile(
    r'\b(?:for|per)\s+(?:one|two|three|four|five|six|seven|eight|'
    r'nine|ten|eleven|twelve|\d+)\s*(?:day|night|hour|month|year|week)',
    re.IGNORECASE
)

# Quality-gate patterns
QUALITY_RE = re.compile(
    r'\b(?:until\s+it\s+(?:resists?|withstands?|flows?|passes?|endures?)|'
    r'until\s+it\s+(?:becomes?\s+(?:fusible|fixed|white|red|black))|'
    r'until\s+(?:the|it)\s+(?:volatile|mercury)\s+is\s+(?:fixed|entirely))',
    re.IGNORECASE
)

termination_conditions = []

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part in ('Index', 'Prefatory'):
        continue

    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue
    if is_running_header(line):
        continue

    if not TERM_EN.search(line):
        continue

    # Classify type
    term_type = 'threshold_based'  # default
    if COUNT_RE.search(line):
        term_type = 'count_based'
    elif TIME_RE.search(line):
        term_type = 'time_dependent'
    elif QUALITY_RE.search(line):
        term_type = 'quality_gated'
    elif re.search(r'\b(you\s+(?:judge|wish|desire)|as\s+(?:seems?|suffic))\b', line, re.IGNORECASE):
        term_type = 'externally_judged'
    elif re.search(r'\b(infinity|without\s+end|as\s+(?:long|many)\s+as\s+you\s+wish)\b', line, re.IGNORECASE):
        term_type = 'asymptotic'

    # Identify operation being iterated
    op_match = OPERATIONAL_VERBS_EN.search(line)
    operation = op_match.group(1).lower() if op_match else 'unspecified'

    # Is iteration bounded?
    bounded = term_type in ('count_based', 'time_dependent')

    # Does it depend on operator judgment?
    needs_judgment = term_type in ('externally_judged', 'quality_gated') or \
                     bool(re.search(r'\b(see|judge|know|observe|test)\b', line, re.IGNORECASE))

    termination_conditions.append({
        'line': i,
        'page': page_id,
        'part': part,
        'text': line.strip()[:300],
        'type': term_type,
        'operation': operation,
        'bounded': bounded,
        'needs_judgment': needs_judgment
    })

term_types = Counter(tc['type'] for tc in termination_conditions)
print(f"  Total termination conditions: {len(termination_conditions)}")
for tt, count in term_types.most_common():
    print(f"    {tt}: {count}")
print(f"  Bounded: {sum(1 for tc in termination_conditions if tc['bounded'])}")
print(f"  Needs judgment: {sum(1 for tc in termination_conditions if tc['needs_judgment'])}")


# ============================================================
# 9. E5: HEAT REGIME INVENTORY
# ============================================================

print("\n=== 9. E5: HEAT REGIME INVENTORY ===")

HEAT_EN = re.compile(
    r'\b(fire|heat\w*|degree|gentle|strong|moderate|fierce|slow|'
    r'balneum|bath|bain-marie|water\s+bath|ashes?|ash\s+(?:fire|bed)|'
    r'sand|sand\s+bath|athanor|furnace|dung|horse\s+dung|quicklime|'
    r'cinericium|cupel|crucible|tripod|oven|charcoal|'
    r'digestion\s+[A-Z])\b',
    re.IGNORECASE
)

HEAT_TRANSITION = re.compile(
    r'\b(increase\s+(?:the\s+)?(?:fire|heat)|'
    r'reduce\s+(?:the\s+)?(?:fire|heat)|'
    r'decrease\s+(?:the\s+)?(?:fire|heat)|'
    r'change\s+(?:the\s+)?(?:fire|heat)|'
    r'gentle\s+fire|'
    r'strong(?:er)?\s+fire|'
    r'with\s+(?:a\s+)?(?:small|great|moderate|fierce)\s+fire|'
    r'first\s+degree|second\s+degree|third\s+degree|fourth\s+degree)\b',
    re.IGNORECASE
)

heat_passages = []
heat_transitions = []
heat_modes = set()

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part in ('Index', 'Prefatory'):
        continue

    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue
    if is_running_header(line):
        continue

    heat_match = HEAT_EN.search(line)
    if not heat_match:
        continue

    # Identify specific heat mode
    mode = None
    if re.search(r'\bbalneum|bath|bain-marie|water\s+bath\b', line, re.IGNORECASE):
        mode = 'balneum_mariae'
    elif re.search(r'\bash(?:es)?\s*(?:fire|bed)?\b', line, re.IGNORECASE) and 'ash' in line.lower():
        mode = 'ash_fire'
    elif re.search(r'\bsand\s*(?:bath)?\b', line, re.IGNORECASE):
        mode = 'sand_bath'
    elif re.search(r'\bathanor\b', line, re.IGNORECASE):
        mode = 'athanor'
    elif re.search(r'\bdung|horse\s+dung|quicklime\b', line, re.IGNORECASE):
        mode = 'dung_fire'
    elif re.search(r'\bgentle\s+fire|small\s+fire|lento\b', line, re.IGNORECASE):
        mode = 'gentle_fire'
    elif re.search(r'\bstrong\s+fire|great\s+fire|fierce\b', line, re.IGNORECASE):
        mode = 'strong_fire'
    elif re.search(r'\bmoderate\s+fire\b', line, re.IGNORECASE):
        mode = 'moderate_fire'
    elif re.search(r'\bopen\s+fire|charcoal\b', line, re.IGNORECASE):
        mode = 'open_fire'
    elif re.search(r'\bcinericium|cupel\b', line, re.IGNORECASE):
        mode = 'cupellation'
    elif re.search(r'\bcrucible\b', line, re.IGNORECASE):
        mode = 'crucible'
    elif re.search(r'\btripod\b', line, re.IGNORECASE):
        mode = 'tripod_of_secrets'
    elif re.search(r'\bsun\b', line, re.IGNORECASE) and re.search(r'\bheat|warm|expose\b', line, re.IGNORECASE):
        mode = 'solar_heat'

    if mode:
        heat_modes.add(mode)

    heat_passages.append({
        'line': i,
        'page': page_id,
        'part': part,
        'mode': mode,
        'text': line.strip()[:200]
    })

    # Check for heat transitions
    trans_match = HEAT_TRANSITION.search(line)
    if trans_match:
        # Determine direction
        direction = 'unspecified'
        if re.search(r'\bincrease|strong|great|fierce\b', line, re.IGNORECASE):
            direction = 'increase'
        elif re.search(r'\breduce|decrease|gentle|small|slow\b', line, re.IGNORECASE):
            direction = 'decrease'
        elif re.search(r'\bchange\b', line, re.IGNORECASE):
            direction = 'change_type'

        heat_transitions.append({
            'line': i,
            'page': page_id,
            'part': part,
            'direction': direction,
            'text': line.strip()[:200]
        })

mode_counts = Counter(p['mode'] for p in heat_passages if p['mode'])
print(f"  Total heat passages: {len(heat_passages)}")
print(f"  Distinct heat modes: {len(heat_modes)}")
for mode, count in mode_counts.most_common():
    print(f"    {mode}: {count}")
print(f"  Heat transitions: {len(heat_transitions)}")
trans_dir = Counter(t['direction'] for t in heat_transitions)
for d, count in trans_dir.most_common():
    print(f"    {d}: {count}")


# ============================================================
# 10. E6: CORRECTION/RECOVERY PROCEDURES
# ============================================================

print("\n=== 10. E6: CORRECTION/RECOVERY ===")

CORRECT_EN = re.compile(
    r'\b(error|errors?|erring|correct\w*|defect\w*|trouble|'
    r'fail\w*|beware\s+lest|wrong|mistaken|sophisticat\w*|'
    r'deceiv\w*|ruin\w*|burn\w*|combust\w*|start\s+over|'
    r'begin\s+again|lost|irrecoverable)\b',
    re.IGNORECASE
)

correction_passages = []

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part in ('Index', 'Prefatory'):
        continue

    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue
    if is_running_header(line):
        continue

    if not CORRECT_EN.search(line):
        continue

    # Classify failure source
    failure_source = 'unspecified'
    if re.search(r'\bcolor|black|white|red|premature\b', line, re.IGNORECASE):
        failure_source = 'process_drift'
    elif re.search(r'\bvessel|seal|break|crack\b', line, re.IGNORECASE):
        failure_source = 'apparatus_failure'
    elif re.search(r'\btoo\s+much\s+(?:fire|heat)|opened?\s+too\s+(?:early|soon)\b', line, re.IGNORECASE):
        failure_source = 'operator_error'
    elif re.search(r'\bwrong\s+(?:substance|material)|contamin\b', line, re.IGNORECASE):
        failure_source = 'material_failure'
    elif re.search(r'\bstart\s+over|begin\s+again|irrecoverable|lost|cannot\b', line, re.IGNORECASE):
        failure_source = 'irrecoverable'
    elif re.search(r'\bburn|combust\b', line, re.IGNORECASE):
        failure_source = 'combustion'
    elif re.search(r'\bsophisticat|deceiv\b', line, re.IGNORECASE):
        failure_source = 'false_practitioners'

    # Look for correction procedure
    correction = 'unspecified'
    if re.search(r'\breiterate|repeat|again\b', line, re.IGNORECASE):
        correction = 'reiterate_operation'
    elif re.search(r'\breduce\s+(?:the\s+)?(?:fire|heat)\b', line, re.IGNORECASE):
        correction = 'reduce_heat'
    elif re.search(r'\badd\s+more\b', line, re.IGNORECASE):
        correction = 'add_more_reagent'
    elif re.search(r'\binhumat\b', line, re.IGNORECASE):
        correction = 'inhumate'
    elif re.search(r'\bstart\s+over|begin\s+again\b', line, re.IGNORECASE):
        correction = 'restart'

    recoverable = failure_source != 'irrecoverable'

    correction_passages.append({
        'line': i,
        'page': page_id,
        'part': part,
        'text': line.strip()[:300],
        'failure_source': failure_source,
        'correction': correction,
        'recoverable': recoverable
    })

fail_types = Counter(c['failure_source'] for c in correction_passages)
corr_types = Counter(c['correction'] for c in correction_passages)
print(f"  Total correction passages: {len(correction_passages)}")
print(f"  Failure sources:")
for ft, count in fail_types.most_common():
    print(f"    {ft}: {count}")
print(f"  Correction types:")
for ct, count in corr_types.most_common():
    print(f"    {ct}: {count}")
print(f"  Recoverable: {sum(1 for c in correction_passages if c['recoverable'])}")
print(f"  Irrecoverable: {sum(1 for c in correction_passages if not c['recoverable'])}")


# ============================================================
# 11. E7: OPERATION-FAMILY TAXONOMY
# ============================================================

print("\n=== 11. E7: OPERATION-FAMILY TAXONOMY ===")

OP_FAMILIES = {
    'distillation': re.compile(r'\b(distill\w*|alembic|cucurbit)\b', re.IGNORECASE),
    'sublimation': re.compile(r'\b(sublim\w*|ascending)\b', re.IGNORECASE),
    'calcination': re.compile(r'\b(calcin\w*|calx|calces)\b', re.IGNORECASE),
    'fixation': re.compile(r'\b(fix\w*|fixat\w*|fixio\w*|immobil\w*)\b', re.IGNORECASE),
    'dissolution': re.compile(r'\b(dissolv\w*|dissolut\w*|solut\w*|resolut\w*)\b', re.IGNORECASE),
    'coagulation': re.compile(r'\b(congeal\w*|coagulat\w*|congelat\w*)\b', re.IGNORECASE),
    'circulation': re.compile(r'\b(circulat\w*)\b', re.IGNORECASE),
    'imbibition': re.compile(r'\b(imbib\w*|moisten\w*|nourish\w*)\b', re.IGNORECASE),
    'fermentation': re.compile(r'\b(ferment\w*)\b', re.IGNORECASE),
    'projection': re.compile(r'\b(project\w*|cast\s+upon|proiect\w*)\b', re.IGNORECASE),
    'separation': re.compile(r'\b(separat\w*|rectif\w*|purif\w*|wash\w*)\b', re.IGNORECASE),
    'furnace_apparatus': re.compile(r'\b(furnace|vessel|athanor|instrument)\b', re.IGNORECASE),
    'theoretical': re.compile(r'\b(nature|element|principle|philoso\w*|theory)\b', re.IGNORECASE),
}

chapter_op_families = []

for ch in chapters:
    start = ch['en_line_start']
    end = ch['en_line_end']
    chapter_text = ' '.join(en_lines[start:end])

    # Count keywords per family
    family_scores = {}
    for family, pattern in OP_FAMILIES.items():
        matches = pattern.findall(chapter_text)
        family_scores[family] = len(matches)

    # Primary family = highest score
    if family_scores:
        sorted_families = sorted(family_scores.items(), key=lambda x: -x[1])
        primary = sorted_families[0][0] if sorted_families[0][1] > 0 else 'unclassified'
        primary_count = sorted_families[0][1]

        # Secondary if >50% of primary
        secondary = None
        if len(sorted_families) > 1 and sorted_families[1][1] > primary_count * 0.5:
            secondary = sorted_families[1][0]
    else:
        primary = 'unclassified'
        secondary = None

    # Theory vs practice confidence
    theory_score = family_scores.get('theoretical', 0)
    practice_score = sum(v for k, v in family_scores.items()
                        if k not in ('theoretical', 'furnace_apparatus'))
    if practice_score > theory_score * 2:
        theory_practice = 'practical'
    elif theory_score > practice_score * 2:
        theory_practice = 'theoretical'
    else:
        theory_practice = 'mixed'

    chapter_op_families.append({
        'chapter_number': ch['number'],
        'part': ch['part'],
        'primary_family': primary,
        'secondary_family': secondary,
        'theory_practice': theory_practice,
        'family_scores': {k: v for k, v in family_scores.items() if v > 0}
    })

# Assign back to chapters
for i, ch in enumerate(chapters):
    ch['primary_family'] = chapter_op_families[i]['primary_family']
    ch['secondary_family'] = chapter_op_families[i]['secondary_family']
    ch['theory_practice'] = chapter_op_families[i]['theory_practice']

# Summary
primary_dist = Counter(cf['primary_family'] for cf in chapter_op_families)
theory_dist = Counter(cf['theory_practice'] for cf in chapter_op_families)
print(f"  Operation families assigned to {len(chapter_op_families)} chapters")
print(f"  Primary family distribution:")
for fam, count in primary_dist.most_common():
    print(f"    {fam}: {count}")
print(f"  Theory/practice split:")
for tp, count in theory_dist.most_common():
    print(f"    {tp}: {count}")

# Distribution by part
print(f"  By part:")
for part_name in ['Theorica', 'Practica', 'Mercuriorum', 'Furnis']:
    part_chapters = [cf for cf in chapter_op_families if cf['part'] == part_name]
    part_fams = Counter(cf['primary_family'] for cf in part_chapters)
    top3 = part_fams.most_common(3)
    top3_str = ', '.join(f"{f}={c}" for f, c in top3)
    print(f"    {part_name} ({len(part_chapters)} ch): {top3_str}")


# ============================================================
# 12. E8: OPERATOR JUDGMENT CUES
# ============================================================

print("\n=== 12. E8: OPERATOR JUDGMENT CUES ===")

JUDGMENT_PATTERNS = [
    (r'\bif\s+you\s+see\b', 'if_you_see', 'visual'),
    (r'\bif\s+you\s+find\b', 'if_you_find', 'assessment'),
    (r'\byou\s+will\s+see\b', 'you_will_see', 'visual'),
    (r'\byou\s+will\s+find\b', 'you_will_find', 'assessment'),
    (r'\byou\s+shall\s+know\b', 'you_shall_know', 'diagnostic'),
    (r'\bthis\s+is\s+the\s+sign\b', 'this_is_the_sign', 'diagnostic'),
    (r'\bbeware\s+lest\b', 'beware_lest', 'warning'),
    (r'\btake\s+care\s+that\b', 'take_care', 'precaution'),
    (r'\bwhen\s+it\s+becomes?\b', 'when_it_becomes', 'state_change'),
    (r'\bwhen\s+it\s+no\s+longer\b', 'when_it_no_longer', 'cessation'),
    (r'\btest\s+whether\b', 'test_whether', 'assay'),
    (r'\bjudge\s+by\b', 'judge_by', 'subjective'),
    (r'\bknow\s+that\s+(?:the|it|when)\b', 'know_that', 'instructional'),
    (r'\bnote\s+(?:that|if|well)\b', 'note_that', 'attention'),
    (r'\bsign\s+(?:of|that|is)\b', 'sign_of', 'diagnostic'),
]

JUDGMENT_COMPILED = [(re.compile(pat, re.IGNORECASE), cue_type, obs_type) for pat, cue_type, obs_type in JUDGMENT_PATTERNS]

judgment_cues = []

for i, line in enumerate(en_lines):
    part = determine_part(i)
    if part in ('Index', 'Prefatory'):
        continue

    page_id = None
    for line_idx, pid, desc in reversed(en_pages):
        if line_idx <= i:
            page_id = pid
            break

    if page_id and is_excluded_page(page_id):
        continue
    if is_running_header(line):
        continue

    for pattern, cue_type, obs_type in JUDGMENT_COMPILED:
        if pattern.search(line):
            # Determine consequence
            consequence = 'continue'
            if re.search(r'\bstop|cease|desist|do\s+not\b', line, re.IGNORECASE):
                consequence = 'stop'
            elif re.search(r'\badjust|reduce|increase|change\b', line, re.IGNORECASE):
                consequence = 'adjust'
            elif re.search(r'\bcorrect|reiterate|repeat\b', line, re.IGNORECASE):
                consequence = 'correct'
            elif re.search(r'\babort|start\s+over|lost\b', line, re.IGNORECASE):
                consequence = 'abort'
            elif re.search(r'\bproceed|then|next\b', line, re.IGNORECASE):
                consequence = 'proceed'

            # Binary or graded?
            certainty = 'binary'
            if re.search(r'\bmore\s+or\s+less|degree|gradual|proportion\b', line, re.IGNORECASE):
                certainty = 'graded'

            # Formalized or discretionary?
            formalized = bool(re.search(r'\b(until|seven|three|four|days?|hours?|white|red|black)\b', line, re.IGNORECASE))

            judgment_cues.append({
                'line': i,
                'page': page_id,
                'part': part,
                'text': line.strip()[:300],
                'cue_type': cue_type,
                'observation_type': obs_type,
                'consequence': consequence,
                'certainty': certainty,
                'formalized': formalized
            })
            break  # Only first matching pattern per line

cue_types = Counter(jc['cue_type'] for jc in judgment_cues)
obs_types = Counter(jc['observation_type'] for jc in judgment_cues)
consequences = Counter(jc['consequence'] for jc in judgment_cues)
print(f"  Total judgment cues: {len(judgment_cues)}")
print(f"  Cue types:")
for ct, count in cue_types.most_common():
    print(f"    {ct}: {count}")
print(f"  Observation types:")
for ot, count in obs_types.most_common():
    print(f"    {ot}: {count}")
print(f"  Consequences:")
for c, count in consequences.most_common():
    print(f"    {c}: {count}")
print(f"  Formalized: {sum(1 for jc in judgment_cues if jc['formalized'])}")
print(f"  Discretionary: {sum(1 for jc in judgment_cues if not jc['formalized'])}")


# ============================================================
# 13. DERIVED SUMMARIES
# ============================================================

print("\n=== 13. DERIVED SUMMARIES ===")

# Per-chapter density scores
for ch in chapters:
    start = ch['en_line_start']
    end = ch['en_line_end']
    n_lines = end - start

    # Count passages in this chapter's range
    ch['monitoring_count'] = sum(1 for p in monitoring_passages if start <= p['line'] < end)
    ch['termination_count'] = sum(1 for tc in termination_conditions if start <= tc['line'] < end)
    ch['heat_count'] = sum(1 for hp in heat_passages if start <= hp['line'] < end)
    ch['correction_count'] = sum(1 for cp in correction_passages if start <= cp['line'] < end)
    ch['cipher_count'] = sum(1 for co in cipher_occurrences if start <= co['line'] < end)
    ch['judgment_count'] = sum(1 for jc in judgment_cues if start <= jc['line'] < end)
    ch['chain_count'] = sum(1 for mc in monitor_action_chains if start <= mc['line'] < end)

    # Density per page (approximate)
    pages_approx = max(n_lines / 30, 1)  # rough estimate
    ch['monitoring_density'] = round(ch['monitoring_count'] / pages_approx, 2)
    ch['symbolic_density'] = round(ch['cipher_count'] / pages_approx, 2)
    ch['judgment_density'] = round(ch['judgment_count'] / pages_approx, 2)

    # Operational density
    ch['operational_density'] = round(
        (ch['monitoring_count'] + ch['termination_count'] +
         ch['heat_count'] + ch['correction_count']) / pages_approx, 2
    )

# Aggregate summaries
operational_chapters = [ch for ch in chapters if ch['theory_practice'] in ('practical', 'mixed')]
theoretical_chapters = [ch for ch in chapters if ch['theory_practice'] == 'theoretical']

# Heat granularity
heat_granularity = len(heat_modes)

# Correction design pattern
n_failure_modes = len(set(c['failure_source'] for c in correction_passages if c['failure_source'] != 'unspecified'))
n_correction_strategies = len(set(c['correction'] for c in correction_passages if c['correction'] != 'unspecified'))
correction_ratio = round(n_correction_strategies / max(n_failure_modes, 1), 2)

# Operation family distribution by part
op_family_by_part = {}
for part_name in ['Theorica', 'Practica', 'Mercuriorum', 'Furnis', 'Compendium']:
    part_chs = [ch for ch in chapters if ch['part'] == part_name]
    if part_chs:
        op_family_by_part[part_name] = dict(Counter(ch['primary_family'] for ch in part_chs))

# Termination type distribution
term_type_dist = dict(Counter(tc['type'] for tc in termination_conditions))

summary = {
    'total_chapters': len(chapters),
    'operational_chapters': len(operational_chapters),
    'theoretical_chapters': len(theoretical_chapters),
    'cipher_letter_total': len(cipher_occurrences),
    'cipher_letter_density_per_op_chapter': round(
        len(cipher_occurrences) / max(len(operational_chapters), 1), 2
    ),
    'monitoring_total': len(monitoring_passages),
    'monitor_action_chains_total': len(monitor_action_chains),
    'monitoring_density_per_op_chapter': round(
        len(monitoring_passages) / max(len(operational_chapters), 1), 2
    ),
    'termination_total': len(termination_conditions),
    'termination_type_distribution': term_type_dist,
    'heat_total': len(heat_passages),
    'heat_granularity_distinct_modes': heat_granularity,
    'heat_modes_list': sorted(heat_modes),
    'heat_transitions_total': len(heat_transitions),
    'correction_total': len(correction_passages),
    'n_failure_modes': n_failure_modes,
    'n_correction_strategies': n_correction_strategies,
    'correction_ratio': correction_ratio,
    'judgment_cues_total': len(judgment_cues),
    'judgment_formalized_pct': round(
        100 * sum(1 for jc in judgment_cues if jc['formalized']) / max(len(judgment_cues), 1), 1
    ),
    'op_family_by_part': op_family_by_part,
}

print(f"  Operational chapters: {summary['operational_chapters']}")
print(f"  Theoretical chapters: {summary['theoretical_chapters']}")
print(f"  Heat granularity: {heat_granularity} distinct modes")
print(f"  Correction ratio (strategies/failures): {correction_ratio}")
print(f"  Judgment cues formalized: {summary['judgment_formalized_pct']}%")


# ============================================================
# 14. WRITE JSON OUTPUT
# ============================================================

print("\n=== 14. WRITING OUTPUT ===")

# Prepare chapter data for JSON (remove line references to keep compact)
chapters_json = []
for ch in chapters:
    chapters_json.append({
        'number': ch['number'],
        'part': ch['part'],
        'title_latin': ch['title_latin'][:200],
        'page': ch['page'],
        'en_line_start': ch['en_line_start'],
        'en_line_end': ch['en_line_end'],
        'primary_family': ch.get('primary_family', 'unclassified'),
        'secondary_family': ch.get('secondary_family'),
        'theory_practice': ch.get('theory_practice', 'mixed'),
        'monitoring_density': ch.get('monitoring_density', 0),
        'symbolic_density': ch.get('symbolic_density', 0),
        'judgment_density': ch.get('judgment_density', 0),
        'operational_density': ch.get('operational_density', 0),
        'monitoring_count': ch.get('monitoring_count', 0),
        'termination_count': ch.get('termination_count', 0),
        'heat_count': ch.get('heat_count', 0),
        'correction_count': ch.get('correction_count', 0),
        'cipher_count': ch.get('cipher_count', 0),
        'judgment_count': ch.get('judgment_count', 0),
        'chain_count': ch.get('chain_count', 0),
    })

# E2 co-occurrence as dict of dicts
cooccurrence_json = {}
for l1 in sorted(cooccurrence.keys()):
    cooccurrence_json[l1] = dict(sorted(cooccurrence[l1].items()))

output = {
    'metadata': {
        'phase': 602,
        'source_english': EN_PATH,
        'source_latin': LA_PATH,
        'english_lines': len(en_lines),
        'latin_lines': len(la_lines),
        'english_pages': len(en_pages),
        'latin_pages': len(la_pages),
        'runtime_s': round(time.time() - start_time, 1)
    },
    'E1_chapters': chapters_json,
    'E2_symbolic_system': {
        'total_occurrences': len(cipher_occurrences),
        'with_operational_context': sum(1 for o in cipher_occurrences if o['has_operational_context']),
        'multi_letter_sequences': len(multi_letter_seqs),
        'active_letters': active_letters,
        'letter_frequency': dict(freq.most_common()),
        'co_occurrence_matrix': cooccurrence_json,
        'first_position_freq': dict(first_pos.most_common()),
        'last_position_freq': dict(last_pos.most_common()),
        'letter_part_distribution': letter_part_dist,
        'sequences_sample': multi_letter_seqs[:50],
    },
    'E3_monitoring': {
        'total_passages': len(monitoring_passages),
        'by_monitor_type': dict(by_type),
        'by_observation_type': dict(obs_types),
        'monitor_action_chains': len(monitor_action_chains),
        'chains_sample': monitor_action_chains[:30],
        'by_part': dict(Counter(p['part'] for p in monitoring_passages)),
    },
    'E4_termination': {
        'total_conditions': len(termination_conditions),
        'by_type': dict(term_types),
        'bounded_count': sum(1 for tc in termination_conditions if tc['bounded']),
        'needs_judgment_count': sum(1 for tc in termination_conditions if tc['needs_judgment']),
        'by_operation': dict(Counter(tc['operation'] for tc in termination_conditions)),
        'by_part': dict(Counter(tc['part'] for tc in termination_conditions)),
        'sample': [{'type': tc['type'], 'operation': tc['operation'],
                    'text': tc['text'][:150], 'part': tc['part']}
                   for tc in termination_conditions[:30]],
    },
    'E5_heat_regimes': {
        'total_passages': len(heat_passages),
        'distinct_modes': heat_granularity,
        'modes_list': sorted(heat_modes),
        'mode_counts': dict(mode_counts),
        'transitions_total': len(heat_transitions),
        'transition_directions': dict(trans_dir),
        'by_part': dict(Counter(hp['part'] for hp in heat_passages)),
    },
    'E6_corrections': {
        'total_passages': len(correction_passages),
        'failure_sources': dict(fail_types),
        'correction_types': dict(corr_types),
        'recoverable': sum(1 for c in correction_passages if c['recoverable']),
        'irrecoverable': sum(1 for c in correction_passages if not c['recoverable']),
        'by_part': dict(Counter(cp['part'] for cp in correction_passages)),
        'design_pattern': {
            'n_failure_modes': n_failure_modes,
            'n_correction_strategies': n_correction_strategies,
            'ratio': correction_ratio,
        },
        'sample': [{'failure': cp['failure_source'], 'correction': cp['correction'],
                    'text': cp['text'][:150], 'part': cp['part']}
                   for cp in correction_passages[:20]],
    },
    'E7_operation_families': {
        'primary_distribution': dict(primary_dist),
        'theory_practice_split': dict(theory_dist),
        'by_part': op_family_by_part,
        'chapter_assignments': [
            {'chapter': cf['chapter_number'], 'part': cf['part'],
             'primary': cf['primary_family'], 'secondary': cf['secondary_family'],
             'theory_practice': cf['theory_practice']}
            for cf in chapter_op_families
        ],
    },
    'E8_judgment_cues': {
        'total_cues': len(judgment_cues),
        'by_cue_type': dict(cue_types),
        'by_observation_type': dict(obs_types),
        'by_consequence': dict(consequences),
        'formalized_count': sum(1 for jc in judgment_cues if jc['formalized']),
        'discretionary_count': sum(1 for jc in judgment_cues if not jc['formalized']),
        'by_part': dict(Counter(jc['part'] for jc in judgment_cues)),
        'sample': [{'cue': jc['cue_type'], 'obs': jc['observation_type'],
                    'consequence': jc['consequence'], 'formalized': jc['formalized'],
                    'text': jc['text'][:150], 'part': jc['part']}
                   for jc in judgment_cues[:30]],
    },
    'summary': summary,
}

os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

elapsed = time.time() - start_time
print(f"\nOutput: {RESULTS_PATH}")
print(f"File size: {os.path.getsize(RESULTS_PATH):,} bytes")
print(f"Runtime: {elapsed:.1f}s")

print(f"\n=== PHASE 602 COMPLETE ===")
print(f"  Chapters: {len(chapters)}")
print(f"  Cipher occurrences: {len(cipher_occurrences)}")
print(f"  Monitoring passages: {len(monitoring_passages)}")
print(f"  Monitor->action chains: {len(monitor_action_chains)}")
print(f"  Termination conditions: {len(termination_conditions)}")
print(f"  Heat passages: {len(heat_passages)}")
print(f"  Heat modes: {heat_granularity}")
print(f"  Correction passages: {len(correction_passages)}")
print(f"  Operation families: {len(set(ch['primary_family'] for ch in chapters))}")
print(f"  Judgment cues: {len(judgment_cues)}")

"""
Phase 641, Script 0: Latin Feature Extractor.

Segments testamentum_complete_latin.txt by chapter markers (CAP. / CAPVT) tracking
which book each chapter belongs to (Theorica / Practica / Mercuriorum / Furnis).
Applies pre-registered Latin regex patterns for 11 feature families.

Output: phases/B_GLOSS_RECIPE_CORRELATION/results/pl_channel_features_latin.json

Pre-registered regex patterns (LOCKED — do not modify after s2 runs):
  heat_mode, heat_transition, monitoring, material_addition, sealing,
  transition, intensity, termination, iteration, vessel, transfer
"""
import sys, io, os, json, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

LATIN_PATH = os.path.join(ROOT, 'sources', 'pseudo_lull_testamentum', 'testamentum_complete_latin.txt')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'pl_channel_features_latin.json')
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ============================================================
# PRE-REGISTERED LATIN REGEX PATTERNS (LOCKED)
# ============================================================
# All patterns use re.IGNORECASE and \b word boundaries.
# \w+ handles Latin inflection (e.g., distilla\w+ matches distillare, distillat, distillatio).

PATTERNS = {
    'heat_mode': re.compile(
        r'\b('
        r'ign\w+|calor\w+|calid\w+|'
        r'balneum|balnei|bain|'
        r'ciner\w+|'
        r'fornax|fornac\w+|'
        r'foco\w+|focus|focos|'
        r'igne\w+|'
        r'aren\w+|'
        r'stercor\w+|'
        r'vapor\w+|'
        r'carbon\w+'
        r')\b', re.IGNORECASE
    ),
    'heat_transition': re.compile(
        r'\b('
        r'augeat\w* (?:ign|calor|foco)\w*|'
        r'minuat\w* (?:ign|calor|foco)\w*|'
        r'intende\w+|intens\w+|'
        r'remitte\w+|remiss\w+|'
        r'fortiter (?:igne|calor|foco)\w*|'
        r'ignis (?:fortior|leni|paulatim)|'
        r'leni(?:ter)? (?:igne|calor|foco)\w*|'
        r'augmenta\w+ ign\w*|'
        r'diminu\w+ ign\w*|'
        r'(?:primo|secundo|tertio|quarto) grad\w+'
        r')\b', re.IGNORECASE
    ),
    'monitoring': re.compile(
        r'\b('
        r'vide\w+|videa\w+|'
        r'appare\w+|apparet|'
        r'signum|signa|signi|'
        r'manifest\w+|'
        r'observ\w+|'
        r'nota\w+|noscat\w*|'
        r'cognosc\w+|'
        r'inspice\w+|inspici\w+'
        r')\b', re.IGNORECASE
    ),
    'material_addition': re.compile(
        r'\b('
        r'accipe|accipia\w+|accepe\w+|'
        r'sume|suma\w+|sumpse\w*|'
        r'recipe|recipia\w+|'
        r'appone\w+|apponi\w+|'
        r'pone|pona\w+|posue\w+|positum|positi|'
        r'adde|adda\w+|addide\w+|'
        r'mitte|mitta\w+|mise\w+|'
        r'infunde\w+|infunda\w+|infudi\w+|infusum|'
        r'impone\w+|imponi\w+'
        r')\b', re.IGNORECASE
    ),
    'sealing': re.compile(
        r'\b('
        r'claude|clauda\w+|clausum|clausi|clausa|'
        r'obtur\w+|'
        r'sigilla\w+|sigilli|'
        r'lut(?:o|um|i|e)|lutet\w*|'
        r'pasta|pastam|pastæ|'
        r'cera|cerat\w+|ceram|'
        r'claud(?:e|ere|itur|atur)'
        r')\b', re.IGNORECASE
    ),
    'transition': re.compile(
        r'\b('
        r'postea|'
        r'deinde|'
        r'tunc|'
        r'mox|'
        r'statim|'
        r'postmodum|'
        r'postquam|'
        r'quando|quum|cum primum|'
        r'itaque|igitur'
        r')\b', re.IGNORECASE
    ),
    'intensity': re.compile(
        r'\b('
        r'fortiter|'
        r'leniter|'
        r'paulatim|'
        r'gradatim|'
        r'vehementer|'
        r'modice|modicum|'
        r'parum|'
        r'multum|multo|'
        r'magnum|magno'
        r')\b', re.IGNORECASE
    ),
    'termination': re.compile(
        r'\b('
        r'donec|'
        r'quousque|'
        r'usque quo|usquequo|'
        r'ad complementum|ad finem|'
        r'consumat\w+|consumpt\w+|'
        r'exsicce\w+|exsicca\w+|exsiccat\w+|'
        r'ad nihilum|'
        r'perfect\w+|'
        r'completus|completa|completum'
        r')\b', re.IGNORECASE
    ),
    'iteration': re.compile(
        r'\b('
        r'repete\w+|repeti\w+|repetit\w+|'
        r'iterum|'
        r'itera|itera\w+|'
        r'reitera\w+|'
        r'toties|quoties|'
        r'numer\w+|'
        r'vices|vice|vicibus|'
        r'(?:bis|ter|quater|quinqu?ies|sexies|septies|octies|noviens|deciens)'
        r')\b', re.IGNORECASE
    ),
    'vessel': re.compile(
        r'\b('
        r'vas|vasa|vasi|vase|vasis|vasum|'
        r'cucurbita\w+|cucurbitæ|cucurbiti|'
        r'alembic\w+|alembici|'
        r'ampull\w+|'
        r'retort\w+|'
        r'phial\w+|'
        r'fiola\w+|'
        r'olla\w+|'
        r'pate(?:lla|llæ|llam)|'
        r'crucibul\w+|'
        r'matra(?:cio|x|ce|cia|cis)'
        r')\b', re.IGNORECASE
    ),
    'transfer': re.compile(
        r'\b('
        r'transfer\w+|'
        r'vert(?:e|ere|at|atur|it|itur)|'
        r'verte\w+|'
        r'decant\w+|'
        r'effunde\w+|effundi\w+|effusum|'
        r'funde|funda\w+|fudi\w+|'
        r'refunde\w+|refunda\w+|'
        r'stilla\w+|destilla\w+|distilla\w+'
        r')\b', re.IGNORECASE
    ),
}

# ============================================================
# CHAPTER SEGMENTATION
# ============================================================
# Structure:
#   Lines 1-5413:      Theorica (CAP. I-XCVI)
#   Lines 5414-~6287:  Practica (CAP. I-XXXII)
#   Lines 6288-9186:   (6288 is start of Compendium, real Mercuriorum starts at CAPVT PRIMVM)
#   Lines 9231-11873:  Practica de Furnis
# We'll detect book-changes by seeing INCIPIT/FINIS markers and restarting chapter numbering.

ROMAN_MAP = {
    'I':1, 'II':2, 'III':3, 'IIII':4, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8,
    'IX':9, 'X':10, 'XI':11, 'XII':12, 'XIII':13, 'XIIII':14, 'XIV':14, 'XV':15,
    'XVI':16, 'XVII':17, 'XVIII':18, 'XIX':19, 'XX':20,
    'XXI':21, 'XXII':22, 'XXIII':23, 'XXIIII':24, 'XXIV':24, 'XXV':25,
    'XXVI':26, 'XXVII':27, 'XXVIII':28, 'XXIX':29, 'XXX':30,
    'XXXI':31, 'XXXII':32, 'XXXIII':33, 'XXXIIII':34, 'XXXIV':34, 'XXXV':35,
    'XXXVI':36, 'XXXVII':37, 'XXXVIII':38, 'XXXIX':39, 'XL':40,
    'XLI':41, 'XLII':42, 'XLIII':43, 'XLIIII':44, 'XLIV':44, 'XLV':45,
    'XLVI':46, 'XLVII':47, 'XLVIII':48, 'XLIX':49, 'L':50,
    'LI':51, 'LII':52, 'LIII':53, 'LIIII':54, 'LIV':54, 'LV':55,
    'LVI':56, 'LVII':57, 'LVIII':58, 'LIX':59, 'LX':60,
    'LXI':61, 'LXII':62, 'LXIII':63, 'LXIIII':64, 'LXIV':64, 'LXV':65,
    'LXVI':66, 'LXVII':67, 'LXVIII':68, 'LXIX':69, 'LXX':70,
    'LXXI':71, 'LXXII':72, 'LXXIII':73, 'LXXIIII':74, 'LXXIV':74, 'LXXV':75,
    'LXXVI':76, 'LXXVII':77, 'LXXVIII':78, 'LXXIX':79, 'LXXX':80,
    'LXXXI':81, 'LXXXII':82, 'LXXXIII':83, 'LXXXIIII':84, 'LXXXV':85,
    'LXXXVI':86, 'LXXXVII':87, 'LXXXVIII':88, 'LXXXIX':89, 'XC':90,
    'XCI':91, 'XCII':92, 'XCIII':93, 'XCIIII':94, 'XCV':95, 'XCVI':96,
    'PRIMVM':1, 'SECVNDVM':2, 'TERTIVM':3, 'QVARTVM':4, 'QVINTVM':5, 'SEXTVM':6,
    'SEPTIMVM':7, 'OCTAVVM':8, 'NONVM':9, 'DECIMVM':10,
    'VNDECIMVM':11, 'DVODECIMVM':12,
}

def parse_chapter_number(raw):
    """Parse various formats: 'CAP. XXII.', 'CAPVT VIGESIMVM SECVNDVM.', 'Caput XII.'"""
    raw = raw.strip()
    # Furnis "Caput XII." form — just roman numeral after
    if raw.startswith('Caput'):
        rest = re.sub(r'Caput\.?', '', raw).strip('. ').strip()
        tok = rest.split('.')[0].strip()
        if tok in ROMAN_MAP:
            return ROMAN_MAP[tok]
    # CAPVT compound forms
    if raw.startswith('CAPVT'):
        rest = raw.replace('CAPVT', '').strip('. ').strip()
        # Try compound: "VIGESIMVM SECVNDVM" -> 20 + 2 = 22
        # Compound: "DECIMVM TERTIVM" -> 10 + 3 = 13
        parts = rest.split()
        if not parts: return None
        # Full map
        compound_base = {
            'VIGESIMVM':20, 'TRIGESIMVM':30, 'QVADRAGESIMVM':40, 'QVINQVAGESIMVM':50,
        }
        ord_map = {
            'PRIMVM':1, 'SECVNDVM':2, 'TERTIVM':3, 'QVARTVM':4, 'QVINTVM':5,
            'SEXTVM':6, 'SEPTIMVM':7, 'OCTAVVM':8, 'NONVM':9, 'DECIMVM':10,
            'VNDECIMVM':11, 'DVODECIMVM':12,
        }
        if len(parts) == 1:
            w = parts[0]
            if w in ROMAN_MAP: return ROMAN_MAP[w]
            if w in compound_base: return compound_base[w]
        if len(parts) == 2:
            base, ext = parts
            if base in compound_base and ext in ord_map:
                return compound_base[base] + ord_map[ext]
            # "DECIMVM TERTIVM" pattern: 10+3 = 13
            if base == 'DECIMVM' and ext in ord_map:
                return 10 + ord_map[ext]
        return None
    # CAP. X. forms
    if raw.startswith('CAP'):
        rest = re.sub(r'CAP\.?', '', raw).strip('. ').strip()
        # Split at any period
        tok = rest.split('.')[0].strip()
        if tok in ROMAN_MAP:
            return ROMAN_MAP[tok]
    return None

def determine_part(line_no, current_part):
    """Track which book of the Testamentum a line belongs to."""
    # Structural markers in the Latin file:
    #   Line 5432: "INCIPIT PRACTICA" -> Practica begins
    #   Line 6288: "INCIPIT COMPENDIVM" -> Compendium/Mercuriorum-prologue begins
    #   Line 6304: "CAPVT PRIMVM" -> Mercuriorum proper begins
    #   Line 9186-ish: "FINIS MERCVRIO-" -> Mercuriorum ends
    #   Line 9231: "# PRACTICA DE FURNIS" -> Furnis begins
    return current_part  # caller tracks this

def segment_chapters(lines):
    """Return list of {part, number, start_line, end_line, text, line_count}."""
    chapters = []
    current_part = 'Theorica'
    pending = None  # {part, number, start_line, buffer}

    for i, line in enumerate(lines):
        ln = i + 1
        stripped = line.rstrip('\n')

        # Part transitions
        if 'INCIPIT PRACTICA MAGISTRI' in stripped.upper():
            current_part = 'Practica'
        elif 'INCIPIT COMPENDIVM' in stripped.upper():
            current_part = 'Compendium'
        elif stripped.startswith('CAPVT'):
            # First CAPVT means we've entered Mercuriorum
            if current_part != 'Mercuriorum':
                current_part = 'Mercuriorum'
        elif '# PRACTICA DE FURNIS' in stripped:
            current_part = 'Furnis'
            continue  # skip the comment line itself

        # Chapter marker detection
        # Testamentum Theorica/Practica: "CAP. I.", "CAP.  IIII." (possibly double space)
        # Mercuriorum: "CAPVT PRIMVM.", "CAPVT VIGESIMVM SECVNDVM."
        # Also handle multi-line: "CAPVT DECIMVM\nquartum." (line-broken compound ordinals)
        # Furnis: "Caput XII." (title-case Caput with period after roman)
        m = re.match(
            r'^(CAP\.?\s+[IVXLC]+\.?\s*$|'
            r'CAPVT(?:\.)?\s+[A-Z]+(?:\s+[A-Z]+)?\.?\s*$|'
            r'Caput\.?\s+[IVXLC]+\.?\s*$)',
            stripped
        )
        if m:
            full_marker = stripped
            # Handle line-broken compound ordinals: "CAPVT DECIMVM\nquartum."
            # Check next non-empty line for a lowercase ordinal suffix
            if stripped.startswith('CAPVT') and stripped.rstrip('.').rstrip() in {
                'CAPVT DECIMVM', 'CAPVT VIGESIMVM', 'CAPVT TRIGESIMVM',
                'CAPVT QVADRAGESIMVM', 'CAPVT QVINQVAGESIMVM',
            }:
                # Peek forward for ordinal suffix
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].rstrip('\n').strip()
                    if not next_line: continue
                    # Match lowercase ordinal: "quartum.", "sextum.", "octavum.", "primum."
                    om = re.match(r'^(primum|secundum|tertium|quartum|quintum|sextum|septimum|octavum|nonum)\b', next_line, re.IGNORECASE)
                    if om:
                        # Medieval Latin spelling: u -> v (QVARTVM not QUARTUM)
                        ord_upper = om.group(1).upper().replace('U', 'V')
                        full_marker = stripped.rstrip('.').rstrip() + ' ' + ord_upper + '.'
                    break
            num = parse_chapter_number(full_marker)
            # Close previous chapter
            if pending is not None:
                pending['end_line'] = ln - 1
                pending['text'] = '\n'.join(lines[pending['start_line']-1:pending['end_line']])
                pending['line_count'] = pending['end_line'] - pending['start_line'] + 1
                chapters.append(pending)
            pending = {
                'part': current_part,
                'number': num,
                'raw_marker': full_marker,
                'start_line': ln,
                'end_line': None,
                'text': None,
                'line_count': 0,
            }

    # Close final chapter
    if pending is not None:
        pending['end_line'] = len(lines)
        pending['text'] = '\n'.join(lines[pending['start_line']-1:pending['end_line']])
        pending['line_count'] = pending['end_line'] - pending['start_line'] + 1
        chapters.append(pending)

    # Strip trailing index material from last chapter if very long
    return chapters

# ============================================================
# FEATURE EXTRACTION
# ============================================================
def extract_features(chapter_text, line_count):
    feats = {}
    for name, pat in PATTERNS.items():
        matches = pat.findall(chapter_text)
        feats[name + '_count'] = len(matches)
        feats[name + '_rate'] = len(matches) / max(1, line_count)
    # Detailed heat_mode subtypes
    HEAT_SUB = {
        'balneum': re.compile(r'\b(balneum|balnei|bain)\b', re.IGNORECASE),
        'cineres': re.compile(r'\b(ciner\w+)\b', re.IGNORECASE),
        'fornax':  re.compile(r'\b(fornax|fornac\w+)\b', re.IGNORECASE),
        'ignis':   re.compile(r'\b(ign\w+|igne\w*)\b', re.IGNORECASE),
        'arena':   re.compile(r'\b(aren\w+)\b', re.IGNORECASE),
        'stercus': re.compile(r'\b(stercor\w+)\b', re.IGNORECASE),
    }
    feats['heat_subtypes'] = {k: len(p.findall(chapter_text)) for k, p in HEAT_SUB.items()}
    return feats

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"Reading: {LATIN_PATH}")
    with open(LATIN_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"  {len(lines)} lines")

    chapters = segment_chapters(lines)
    print(f"\nChapters detected: {len(chapters)}")

    by_part = Counter(c['part'] for c in chapters)
    for part, n in by_part.most_common():
        print(f"  {part}: {n}")

    # Extract features per chapter
    print("\nExtracting features...")
    for ch in chapters:
        feats = extract_features(ch['text'] or '', ch['line_count'])
        ch['features'] = feats
        # Don't emit full text in output (too large)
        del ch['text']

    # Build a lookup by (part, number)
    lookup = {}
    for ch in chapters:
        key = (ch['part'], ch['number'])
        # Some chapters duplicate (e.g. CAP. III. appears twice in Theorica — different content blocks)
        if key in lookup:
            if not isinstance(lookup[key], list):
                lookup[key] = [lookup[key]]
            lookup[key].append(ch)
        else:
            lookup[key] = ch

    # Summary output
    out = {
        'metadata': {
            'phase': 641,
            'script': 's0_latin_feature_extractor',
            'source': 'testamentum_complete_latin.txt',
            'n_chapters': len(chapters),
            'by_part': dict(by_part),
            'pattern_version': 'v1_locked',
            'pattern_count': len(PATTERNS),
        },
        'chapters': chapters,
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUT_PATH}")

    # Sanity: print feature totals
    print("\nFeature TOTALS across all chapters:")
    totals = defaultdict(int)
    for ch in chapters:
        for k, v in ch['features'].items():
            if k.endswith('_count'):
                totals[k] += v
    for k in sorted(totals):
        print(f"  {k:<30s}: {totals[k]}")

    # Spot check: Mercuriorum chapter 22 (Ch22M, lunaria maceration — f82r)
    print("\n--- Mercuriorum Ch22 (should match f82r Ch22M) ---")
    ch22 = lookup.get(('Mercuriorum', 22))
    if ch22:
        print(f"  Lines {ch22['start_line']}-{ch22['end_line']} ({ch22['line_count']} lines)")
        print(f"  Marker: {ch22['raw_marker']}")
        for k, v in ch22['features'].items():
            if k.endswith('_count') and v > 0:
                print(f"  {k}: {v}")
    else:
        print(f"  NOT FOUND. Keys near Mercuriorum: {[k for k in lookup if k[0]=='Mercuriorum'][:30]}")

    # Spot check: Mercuriorum Ch1 (f112v)
    print("\n--- Mercuriorum Ch1 (should match f112v Ch1M) ---")
    ch1 = lookup.get(('Mercuriorum', 1))
    if ch1:
        print(f"  Lines {ch1['start_line']}-{ch1['end_line']} ({ch1['line_count']} lines)")
        for k, v in ch1['features'].items():
            if k.endswith('_count') and v > 0:
                print(f"  {k}: {v}")

if __name__ == '__main__':
    main()

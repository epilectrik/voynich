"""
Puff Text Parser - Semantic Feature Extraction
Tier 4 SPECULATIVE - Extract therapeutic content from OCR'd Puff text

Extracts: humoral qualities, organs, application methods, severity, therapeutic actions
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SOURCES_DIR = Path(__file__).parent.parent.parent / "sources"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

# ============================================================
# GERMAN KEYWORD DICTIONARIES
# Early New High German with OCR spelling variants
# ============================================================

HUMORAL_KEYWORDS = {
    'warm': ['warm', 'wermt', 'wermet', 'warmẽ', 'warmm', 'warme', 'warntet', 'warmct', 'werm', 'bayß', 'bay$', 'hayß', 'hitzig'],
    'cold': ['kalt', 'kallt', 'keltin', 'kalte', 'kält', 'kült', 'kühl', 'küel', 'salt', 'talter', 'falt', 'kült', 'tület', 'külen'],
    'dry': ['trucken', 'trucke', 'truckẽ', 'dürr', 'durr', 'trocken', 'trucse', 'trucfc', 'truck'],
    'moist': ['feucht', 'feücht', 'feuchte', 'naß', 'nas', 'naſſ', 'feucbt', 'fcucht', 'naff']
}

ORGAN_KEYWORDS = {
    'head': ['haupt', 'haubt', 'hau£t', 'haugtba', 'hirn', 'hyrn', 'bym', 'augen', 'äugen', 'angen', 'augcn', 'auge',
             'ohren', 'oren', 'mund', 'mundt', 'zung', 'zungen', 'nasen', 'nas', '$ung'],
    'chest': ['hertz', 'hertzen', 'hertze', 'herz', 'bert$', 'bcrt', 'brust', 'bruſt', 'prusſt', 'ptuff', 'ptuft',
              'lung', 'lungen', 'atem', 'athem', 'odem', 'atemw'],
    'abdomen': ['magen', 'magẽ', 'leber', 'lebern', 'lebetn', 'lebet', 'miltz', 'milz', 'milt$', 'mtlt',
                'nieren', 'nyren', 'niern', 'ntcrcn', 'darm', 'därm', 'bauch', 'baůch', 'ftaucb', 'ffaueb',
                'gedärm', 'blaſe', 'blase', 'platem', 'plater'],
    'limbs': ['glieder', 'glider', 'gelider', 'geltber', 'hand', 'handt', 'hend', 'händt', 'benb', 'bcnb',
              'fuß', 'füß', 'fueß', 'bein', 'beyn', 'arm', 'arme', 'fuf', 'füf'],
    'skin': ['haut', 'hawt', 'wund', 'wunden', 'wundt', 'geschwer', 'geſchwer', 'gcfcbwcr', 'gefcbwern',
             'antlütz', 'antlitz', 'angesicht', 'fleysch', 'fleyſch', 'fleisch', 'fleyffcb']
}

APPLICATION_KEYWORDS = {
    'internal': ['trinck', 'trincken', 'trincke', 'trtncf', 'trmcK', 'niessen', 'nieſſen', 'niesen', 'niejfcn',
                 'essen', 'eſſen', 'geben', 'geb', 'getruncken', 'schluck', 'getrunctert', 'trtncKen'],
    'external': ['streich', 'streichen', 'gestrichen', 'flteicbm', 'flctcf', 'wasch', 'waschen', 'gewaschen', 'wäfcbe', 'wafcbe',
                 'leg', 'legen', 'gelegt', 'lege', 'lcgen', 'salb', 'salben', 'gesalbt', 'schmier', 'fcbmter',
                 'bad', 'baden', 'gebadt', 'genest', 'genezt', 'bestreichen', 'netzet', 'bab', 'babt']
}

SEVERITY_KEYWORDS = {
    'severe': ['gift', 'gifft', 'vergifft', 'gtfft', 'tod', 'todt', 'sterben', 'sterbẽ', 'flerbcn',
               'pest', 'pestilentz', 'pefltleuQ', 'pcflilenQ', 'fallend', 'vallend', 'siech', 'siechtag', 'ftccbtag',
               'aussatz', 'aussätz', 'krebs', 'aussetzigkeit', 'auffefctg'],
    'moderate': ['fieber', 'fyeber', 'fteber', 'schmertz', 'schmertzen', 'schmercz', 'fcbmert$',
                 'geschwer', 'geſchwer', 'gcfcbwer', 'gefcbwulß', 'apostem', 'apojtetcn', 'wee', 'we', 'grimmen',
                 'wunden', 'wundt', 'gebrech', 'siechheit', 'krankheit', 'fteebtag', 'ftccbtagen'],
    'mild': ['schön', 'schone', 'schönheit', 'fcbon', 'fcbönbayt', 'schlaf', 'schlaff', 'schlaffẽ', 'fcblaff',
             'stärck', 'sterck', 'krafft', 'kraft', 'lust', 'freud', 'frewt', 'frcwb',
             'gemüt', 'gemuet', 'erfrisch', 'erquick', 'erfrcwt', 'erquicK']
}

THERAPEUTIC_KEYWORDS = {
    'cooling': ['kühl', 'kuel', 'lösch', 'loesch', 'lescht', 'still', 'stillen', 'tület', 'lület', 'lejcbet', 'lefcb', 'lofcbt'],
    'warming': ['wärm', 'wermt', 'warm', 'treibt', 'treib', 'hitzig', 'wermet', 'wermct'],
    'cleansing': ['reinig', 'reynig', 'räum', 'raum', 'treib', 'treibt', 'ratmtget',
                  'außtreib', 'purgier', 'säuber', 'fäubert', 'rayntget'],
    'strengthening': ['stärck', 'sterck', 'kräfftig', 'kreftig', 'sterk', 'ftercK', 'fferctltcb', 'flercfet'],
    'healing': ['heyl', 'heilen', 'heylt', 'gesund', 'gesundt', 'curiert', 'baylet', 'batlet', 'gefunb', 'gefunbt']
}

# ============================================================
# CHAPTER BOUNDARY DETECTION
# ============================================================

# OCR-garbled patterns for "Von X wasser"
# "Von" appears as: SDon, 2Don, 5!?on, %>on, 33on, ü&on, *13on, yJen, €5f, etc.
CHAPTER_PATTERNS = [
    r'[SD25%ü\*y€3]+[!?&]*[Ddon]+\s+.*?wa\s*[fſj]+[efi]*[crlt]*',  # Various "Von X wasser" garbled
    r'btm\s+etffcn\s+von\s+bem',  # "Zum ersten von dem" - first chapter
    r'[SD25%ü\*y€3]+[!?&]*[Ddon]+\s+[A-Za-zäöüßẞ£]+\s+wa',  # Von X wa...
]

def is_chapter_header(line):
    """Check if line looks like a chapter header"""
    line = line.strip()
    if len(line) < 10 or len(line) > 100:
        return False

    line_lower = line.lower()

    # Check for Von-like patterns at start (first 15 chars)
    # OCR garbles "Von" as: SDon, 2Don, 5!?on, %>on, 33en, ü&on, Tfon, X7on, !0on, 23 on, %3cn, S0ott, 30ott, ©oit, etc.
    start = line_lower[:15]
    von_patterns = ['on ', 'on£', 'ott ', 'en ', '0on', '3on', '?on']
    has_von = any(p in start for p in von_patterns)

    # Check for wasser-like patterns anywhere
    # "wasser" appears as: wafict, waffcr, waflet, waffer, wa jfer, wajfer, waflfer, waföt, wajjcr, xv affet, wa flfer
    wasser_patterns = [
        'wafict', 'waffcr', 'waflet', 'wasser', 'waffer', 'wajfer', 'wafler',
        'waflfer', 'wajjcr', 'waffet', 'wafjer', 'wa f', 'wa jf', 'wa fl'
    ]
    has_wasser = any(p in line_lower for p in wasser_patterns)

    # Also check for pattern: ends with asterisk or dash after water word
    ends_water = bool(re.search(r'wa[fſsj][fſsj]*[aeiclrt]*[\*\-\.]?\s*$', line_lower))

    return has_von and (has_wasser or ends_water)

def detect_chapter_boundaries(text):
    """Find chapter start positions and names"""
    chapters = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        line_clean = line.strip()
        if is_chapter_header(line_clean):
            chapters.append({
                'line': i,
                'name': line_clean[:40],  # First 40 chars as name
                'header': line_clean
            })

    return chapters

def extract_chapter_text(text, chapters):
    """Extract text for each chapter (between boundaries)"""
    lines = text.split('\n')
    chapter_texts = []

    for i, ch in enumerate(chapters):
        start_line = ch['line']
        end_line = chapters[i + 1]['line'] if i + 1 < len(chapters) else len(lines)

        chapter_text = '\n'.join(lines[start_line:end_line])
        chapter_texts.append({
            'index': i,
            'name': ch['name'],
            'header': ch['header'],
            'text': chapter_text,
            'line_count': end_line - start_line
        })

    return chapter_texts

# ============================================================
# FEATURE EXTRACTION
# ============================================================

def count_keyword_matches(text, keyword_dict):
    """Count matches for each category in keyword dict"""
    text_lower = text.lower()
    counts = {}

    for category, keywords in keyword_dict.items():
        count = 0
        for kw in keywords:
            # Use word boundary-ish matching
            count += len(re.findall(r'\b' + re.escape(kw.lower()), text_lower))
        counts[category] = count

    return counts

def extract_humoral_quality(text):
    """Determine humoral classification"""
    counts = count_keyword_matches(text, HUMORAL_KEYWORDS)

    # Determine primary quality
    warm_cold = 'warm' if counts['warm'] > counts['cold'] else ('cold' if counts['cold'] > counts['warm'] else 'neutral')
    dry_moist = 'dry' if counts['dry'] > counts['moist'] else ('moist' if counts['moist'] > counts['dry'] else 'neutral')

    return {
        'warm_count': counts['warm'],
        'cold_count': counts['cold'],
        'dry_count': counts['dry'],
        'moist_count': counts['moist'],
        'primary_temp': warm_cold,
        'primary_moisture': dry_moist,
        'classification': f"{warm_cold}-{dry_moist}"
    }

def extract_organ_mentions(text):
    """Count organ/body part mentions"""
    counts = count_keyword_matches(text, ORGAN_KEYWORDS)
    total = sum(counts.values())

    # Find primary organ system
    if total > 0:
        primary = max(counts, key=counts.get)
    else:
        primary = 'none'

    return {
        'organ_counts': counts,
        'total_organ_mentions': total,
        'primary_organ_system': primary
    }

def extract_application_method(text):
    """Classify application method"""
    counts = count_keyword_matches(text, APPLICATION_KEYWORDS)

    internal = counts['internal']
    external = counts['external']
    total = internal + external

    if total == 0:
        method = 'unknown'
    elif internal > external * 1.5:
        method = 'internal'
    elif external > internal * 1.5:
        method = 'external'
    else:
        method = 'mixed'

    return {
        'internal_count': internal,
        'external_count': external,
        'primary_method': method,
        'internal_ratio': round(internal / total, 2) if total > 0 else 0
    }

def extract_severity(text):
    """Rate condition severity"""
    counts = count_keyword_matches(text, SEVERITY_KEYWORDS)

    severe = counts['severe']
    moderate = counts['moderate']
    mild = counts['mild']

    # Calculate severity score (0-2)
    if severe > 0:
        score = 2
    elif moderate > mild:
        score = 1
    else:
        score = 0

    return {
        'severe_count': severe,
        'moderate_count': moderate,
        'mild_count': mild,
        'severity_score': score,
        'severity_label': ['mild', 'moderate', 'severe'][score]
    }

def extract_therapeutic_actions(text):
    """Extract therapeutic action categories"""
    counts = count_keyword_matches(text, THERAPEUTIC_KEYWORDS)
    total = sum(counts.values())

    # Calculate therapeutic breadth (number of non-zero categories)
    breadth = sum(1 for c in counts.values() if c > 0)

    return {
        'action_counts': counts,
        'total_actions': total,
        'therapeutic_breadth': breadth,
        'primary_action': max(counts, key=counts.get) if total > 0 else 'none'
    }

# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_all_features(chapter):
    """Extract all semantic features from a chapter"""
    text = chapter['text']

    return {
        'index': chapter['index'],
        'name': chapter['name'],
        'header': chapter['header'],
        'line_count': chapter['line_count'],
        'humoral': extract_humoral_quality(text),
        'organs': extract_organ_mentions(text),
        'application': extract_application_method(text),
        'severity': extract_severity(text),
        'therapeutic': extract_therapeutic_actions(text)
    }

def main():
    print("=" * 60)
    print("PUFF TEXT PARSER - Semantic Feature Extraction")
    print("[TIER 4 SPECULATIVE]")
    print("=" * 60)

    # Load text
    with open(SOURCES_DIR / "puff_1501_text.txt", 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"\nLoaded text: {len(text)} characters, {len(text.split(chr(10)))} lines")

    # Detect chapters
    print("\n--- Chapter Detection ---")
    chapters = detect_chapter_boundaries(text)
    print(f"Found {len(chapters)} chapter boundaries")

    # Show first few
    for ch in chapters[:5]:
        print(f"  Line {ch['line']}: {ch['header'][:50]}...")

    # Extract chapter texts
    chapter_texts = extract_chapter_text(text, chapters)
    print(f"\nExtracted {len(chapter_texts)} chapter texts")

    # Extract features for all chapters
    print("\n--- Feature Extraction ---")
    all_features = []

    for ch in chapter_texts:
        features = extract_all_features(ch)
        all_features.append(features)

    print(f"Extracted features for {len(all_features)} chapters")

    # Summary statistics
    print("\n--- Summary Statistics ---")

    # Humoral distribution
    temp_counts = defaultdict(int)
    for f in all_features:
        temp_counts[f['humoral']['primary_temp']] += 1
    print(f"Temperature: {dict(temp_counts)}")

    # Organ distribution
    organ_totals = defaultdict(int)
    for f in all_features:
        for organ, count in f['organs']['organ_counts'].items():
            organ_totals[organ] += count
    print(f"Organ mentions: {dict(organ_totals)}")

    # Application method
    method_counts = defaultdict(int)
    for f in all_features:
        method_counts[f['application']['primary_method']] += 1
    print(f"Application: {dict(method_counts)}")

    # Severity
    severity_counts = defaultdict(int)
    for f in all_features:
        severity_counts[f['severity']['severity_label']] += 1
    print(f"Severity: {dict(severity_counts)}")

    # Save results
    output = {
        "tier": 4,
        "status": "HYPOTHETICAL",
        "source": "sources/puff_1501_text.txt",
        "date": "2026-01-14",
        "warning": "PURE SPECULATION - Model frozen",
        "extraction_stats": {
            "chapters_found": len(chapters),
            "chapters_extracted": len(all_features),
            "temperature_distribution": dict(temp_counts),
            "organ_totals": dict(organ_totals),
            "application_distribution": dict(method_counts),
            "severity_distribution": dict(severity_counts)
        },
        "chapters": all_features
    }

    with open(RESULTS_DIR / "puff_chapter_semantics.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to results/puff_chapter_semantics.json")

    return output

if __name__ == "__main__":
    main()

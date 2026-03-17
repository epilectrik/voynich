"""
Phase 598a: Extract and catalog recipes from Brunschwig 1512 (de compositis).

Scans the English translation for recipe boundaries and procedural features.
Outputs structured JSON for blind prediction test design.

Semi-automated: identifies candidates programmatically, extracts features,
flags ambiguous cases for review.
"""

import json
import re
from pathlib import Path
from collections import Counter

SRC = Path("sources/brunschwig_1512/brunschwig_1512_english.txt")
OUT = Path("phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/brunschwig_1512_recipes.json")

# --- Feature keyword maps ---

METHOD_KEYWORDS = {
    'balneum_mariae': [
        r'balneum mari[ae]', r'water bath', r'balneo mari',
        r'balneum marie', r"mary'?s bath"
    ],
    'horse_dung': [
        r'horse dung', r'horse manure', r'fimo equino',
        r'putref(?:y|ied|action)'
    ],
    'ashes': [
        r'in (?:the )?ashes', r'ash(?:es)? bath', r'in cineribus'
    ],
    'sand_bath': [
        r'sand bath', r'in (?:the )?sand', r'in arena'
    ],
    'open_fire': [
        r'open fire', r'strong fire', r'great fire',
        r'coal fire', r'fire of coals'
    ],
    'gentle_fire': [
        r'gentle fire', r'small fire', r'slow fire',
        r'mild fire', r'moderate fire'
    ],
    'circulation': [
        r'circulat(?:e|ion|ing|orio|orium)', r'pelican',
        r'pellican'
    ],
    'sun': [
        r'in the sun', r'sun ?light'
    ]
}

VESSEL_KEYWORDS = {
    'cucurbit': [r'cucurbit'],
    'alembic': [r'alembic', r'alembicum', r'helm'],
    'pelican': [r'pelican', r'pellican'],
    'circulatorium': [r'circulat(?:orium|orio)'],
    'retort': [r'retort'],
    'flask': [r'flask', r'glass vessel', r'glass bottle'],
    'receiver': [r'receiv(?:er|ing)', r'receptacl'],
}

FIRE_DEGREE_KEYWORDS = {
    1: [r'first degree', r'primo gradu', r'lukewarm'],
    2: [r'second degree', r'secundo gradu', r'perceptibly warm'],
    3: [r'third degree', r'tertio gradu'],
    4: [r'fourth degree', r'quarto gradu']
}

PRODUCT_TYPE_KEYWORDS = {
    'quintessence': [r'quint(?:a|am) essenti', r'fifth essence'],
    'aqua_vitae': [r'aqua vit[ae]', r'water of life'],
    'oil': [r'\boil\b', r'oleum'],
    'balsam': [r'balsam'],
    'water': [r'distilled water', r'water for', r'good water'],
    'theriac': [r'theriac', r'theriaca', r'triacle'],
    'mithridate': [r'mithridat'],
    'electuary': [r'electuar'],
    'syrup': [r'syrup', r'sirup'],
}

DURATION_PATTERN = re.compile(
    r'(?:for|during|after)\s+(\d+|one|two|three|four|five|six|seven|eight|'
    r'nine|ten|fourteen|thirty|forty)\s+'
    r'(day|week|month|moon|hour|night)s?',
    re.IGNORECASE
)

# --- Recipe boundary detection ---

# Chapter heading patterns
CHAPTER_PATTERNS = [
    re.compile(r'^(?:The\s+)?(?:Das\s+)?(?:\w+\s+)?Chapter', re.IGNORECASE),
    re.compile(r'^(?:Das\s+)?\w+\.?\s+Capitel', re.IGNORECASE),
]

# Recipe heading patterns (Third Book style)
RECIPE_HEADING_PATTERNS = [
    re.compile(r'^A\s+(?:good|noble|wonderful|common|water|useful|excellent|proven)', re.IGNORECASE),
    re.compile(r'^Another\s+(?:water|oil|balsam|good|noble)', re.IGNORECASE),
    re.compile(r'^(?:For|Against|Item,?\s+a)\s+', re.IGNORECASE),
]

# Page boundary pattern
PAGE_PATTERN = re.compile(r'^--- Page (\d+)\s*\(([^)]*)\)')

# "Take" pattern (ingredient list start)
TAKE_PATTERN = re.compile(r'^(?:Take|Recipe|Item,?\s+take)\s+', re.IGNORECASE)

# Woodcut/figure markers
FIGURE_PATTERN = re.compile(r'^\[(?:WOODCUT|FIGURE|ILLUSTRATION)', re.IGNORECASE)


def load_text():
    """Load the 1512 English translation."""
    with open(SRC, 'r', encoding='utf-8') as f:
        return f.readlines()


def infer_fire_degree(text_block):
    """Infer fire degree from method keywords in a recipe text block."""
    text_lower = text_block.lower()

    explicit_degrees = {}
    for degree, patterns in FIRE_DEGREE_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                explicit_degrees[degree] = True

    # Infer from method if no explicit degree
    method_degree = None
    if re.search(r'balneum|water bath|balneo|gentle fire|small fire', text_lower):
        method_degree = 1
    if re.search(r'in (?:the )?ashes|sand bath|in arena|in cineribus', text_lower):
        method_degree = 2 if method_degree is None else max(method_degree, 2)
    if re.search(r'strong fire|great fire|open fire|calcin', text_lower):
        method_degree = 3 if method_degree is None else max(method_degree, 3)
    # Only infer degree 4 from explicit fourth degree mention or truly extreme heat
    if re.search(r'fourth degree|unbearable|calcin(?:e|ed|ing) firmly', text_lower):
        method_degree = 4 if method_degree is None else max(method_degree, 4)

    # Explicit degrees take precedence
    if explicit_degrees:
        return {
            'explicit_degrees': sorted(explicit_degrees.keys()),
            'max_degree': max(explicit_degrees.keys()),
            'method_inferred': method_degree
        }
    elif method_degree:
        return {
            'explicit_degrees': [],
            'max_degree': method_degree,
            'method_inferred': method_degree
        }
    else:
        return {
            'explicit_degrees': [],
            'max_degree': None,
            'method_inferred': None
        }


def extract_methods(text_block):
    """Extract distillation methods mentioned in a recipe."""
    text_lower = text_block.lower()
    methods = []
    for method_name, patterns in METHOD_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                methods.append(method_name)
                break
    return methods


def extract_vessels(text_block):
    """Extract vessel types mentioned in a recipe."""
    text_lower = text_block.lower()
    vessels = []
    for vessel_name, patterns in VESSEL_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                vessels.append(vessel_name)
                break
    return vessels


def extract_product_types(text_block):
    """Extract product type indicators."""
    text_lower = text_block.lower()
    products = []
    for prod_name, patterns in PRODUCT_TYPE_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                products.append(prod_name)
                break
    return products


def extract_durations(text_block):
    """Extract duration specifications."""
    matches = DURATION_PATTERN.findall(text_block)
    return [f"{amt} {unit}{'s' if unit[-1] != 's' else ''}" for amt, unit in matches]


def has_ingredient_list(text_block):
    """Check if recipe has a 'Take X, Y, Z' ingredient list."""
    # Search within text block (not just at line start)
    return bool(re.search(
        r'(?:^|\.\s+|,\s+)(?:Take|Recipe)\s+(?!care|note|heed|it out)',
        text_block, re.IGNORECASE | re.MULTILINE
    ))


def count_distillation_steps(text_block):
    """Count references to distillation iterations."""
    text_lower = text_block.lower()
    step_words = re.findall(
        r'(?:first|second|third|fourth|fifth|sixth|seventh)\s+distillation',
        text_lower
    )
    # Also count "distill it" / "distill again" / "redistill"
    distill_refs = len(re.findall(r'distill(?:ed|ing)?', text_lower))
    return {
        'named_distillations': len(step_words),
        'distill_references': distill_refs,
        'max_named': max([0] + [
            {'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
             'fifth': 5, 'sixth': 6, 'seventh': 7}.get(w.split()[0], 0)
            for w in step_words
        ])
    }


def identify_book(page_num):
    """Identify which book a page belongs to.

    Based on page description analysis of the 1512 English translation.
    The 1512 has 1694 pages. Structure:
    - Pages 1-35: Front matter (Register, Preface)
    - Pages 36-544: First Book (Quinta Essentia, Aqua Vitae, Balsam, Theriac, Mithridate, Aurum Potabile)
    - Pages 544-870: Second Book (Simplicia & Composita by organ system, compound remedies)
    - Pages 870-1280: Third Book (Compound distilled waters for diseases, head-to-foot)
    - Pages 1280-1295: Fourth Book (Surgical waters)
    - Pages 1295-1680: Fifth Book (Thesaurus Pauperum, practical remedies)
    - Pages 1680+: Back matter (Errata, Colophon)
    """
    if page_num <= 35:
        return "front_matter"
    elif page_num <= 544:
        return "first_book"
    elif page_num <= 870:
        return "second_book"
    elif page_num <= 1280:
        return "third_book"
    elif page_num <= 1295:
        return "fourth_book"
    elif page_num <= 1680:
        return "fifth_book"
    else:
        return "back_matter"


def segment_recipes(lines):
    """
    Segment the text into recipe-like blocks.

    Strategy: Use page markers + chapter headings + recipe headings to
    identify boundaries. Each segment gets the text between boundaries.
    """
    segments = []
    current_segment = {
        'start_line': 0,
        'start_page': 1,
        'heading': '',
        'lines': [],
        'page_range': set()
    }
    current_page = 1
    current_page_desc = ''

    for i, line in enumerate(lines):
        line_stripped = line.rstrip('\n')

        # Track page numbers
        page_match = PAGE_PATTERN.match(line_stripped)
        if page_match:
            current_page = int(page_match.group(1))
            current_page_desc = page_match.group(2)
            continue

        # Skip empty lines, figures, woodcuts
        if not line_stripped.strip():
            continue
        if FIGURE_PATTERN.match(line_stripped):
            continue

        # Check for chapter/recipe heading (= new segment boundary)
        is_chapter = any(p.match(line_stripped) for p in CHAPTER_PATTERNS)
        is_recipe_heading = any(p.match(line_stripped) for p in RECIPE_HEADING_PATTERNS)

        if is_chapter or is_recipe_heading:
            # Save current segment if it has content
            if current_segment['lines']:
                segments.append(current_segment)

            # Start new segment
            current_segment = {
                'start_line': i + 1,
                'start_page': current_page,
                'heading': line_stripped.strip(),
                'heading_type': 'chapter' if is_chapter else 'recipe',
                'lines': [line_stripped],
                'page_range': {current_page}
            }
        else:
            current_segment['lines'].append(line_stripped)
            current_segment['page_range'].add(current_page)

    # Don't forget the last segment
    if current_segment['lines']:
        segments.append(current_segment)

    return segments


def classify_segment(segment):
    """
    Classify a segment as recipe, theory, pharmacology, or other.
    Recipes have procedural content (distillation methods, ingredients, etc.)
    """
    text = '\n'.join(segment['lines'])
    text_lower = text.lower()

    has_method = bool(extract_methods(text))
    has_vessel = bool(extract_vessels(text))
    has_ingredients = has_ingredient_list(text)
    has_distill = 'distill' in text_lower
    has_take = bool(TAKE_PATTERN.search(text))
    word_count = len(text.split())

    # Classify
    procedural_score = sum([
        has_method * 2,
        has_vessel,
        has_ingredients * 2,
        has_distill,
        has_take,
    ])

    if procedural_score >= 3:
        return 'recipe'
    elif procedural_score >= 1 and word_count > 100:
        return 'recipe_candidate'
    elif word_count < 30:
        return 'fragment'
    else:
        return 'text'


def build_recipe_record(segment, recipe_id):
    """Build a structured recipe record from a classified segment."""
    text = '\n'.join(segment['lines'])
    pages = sorted(segment['page_range'])

    fire_info = infer_fire_degree(text)
    methods = extract_methods(text)
    vessels = extract_vessels(text)
    products = extract_product_types(text)
    durations = extract_durations(text)
    distill_steps = count_distillation_steps(text)
    book = identify_book(pages[0]) if pages else 'unknown'

    # Infer overall fire degree class for prediction binning
    degree = fire_info['max_degree']
    if degree is None and methods:
        # Default inference from method alone
        if 'balneum_mariae' in methods and 'open_fire' not in methods:
            degree = 1
        elif 'horse_dung' in methods:
            degree = 1
        elif 'ashes' in methods or 'sand_bath' in methods:
            degree = 2
    fire_info['inferred_class'] = degree

    # Determine primary product type
    primary_product = None
    product_priority = ['quintessence', 'aqua_vitae', 'balsam', 'oil',
                        'theriac', 'mithridate', 'water']
    for p in product_priority:
        if p in products:
            primary_product = p
            break

    return {
        'id': recipe_id,
        'heading': segment['heading'],
        'heading_type': segment.get('heading_type', 'unknown'),
        'book': book,
        'pages': pages,
        'start_line': segment['start_line'],
        'word_count': len(text.split()),
        'fire_degree': fire_info,
        'methods': methods,
        'vessels': vessels,
        'product_types': products,
        'primary_product': primary_product,
        'has_ingredient_list': has_ingredient_list(text),
        'durations': durations,
        'distillation_steps': distill_steps,
        'classification': classify_segment(segment),
        'text_preview': text[:500],
    }


def main():
    print("Loading 1512 English translation...")
    lines = load_text()
    print(f"  {len(lines)} lines loaded")

    print("\nSegmenting into recipe blocks...")
    segments = segment_recipes(lines)
    print(f"  {len(segments)} segments identified")

    print("\nClassifying and extracting features...")
    recipes = []
    stats = Counter()
    recipe_counter = 0

    for seg in segments:
        classification = classify_segment(seg)
        stats[classification] += 1

        if classification in ('recipe', 'recipe_candidate'):
            recipe_counter += 1
            recipe_id = f"B1512-{recipe_counter:03d}"
            record = build_recipe_record(seg, recipe_id)
            recipes.append(record)

    print(f"\n--- Segment Classification ---")
    for cls, count in stats.most_common():
        print(f"  {cls}: {count}")

    print(f"\n--- Recipe Extraction ---")
    print(f"  Total recipes/candidates: {len(recipes)}")

    # Fire degree distribution
    degree_counts = Counter()
    for r in recipes:
        d = r['fire_degree']['inferred_class']
        degree_counts[d] += 1
    print(f"\n--- Fire Degree Distribution ---")
    for d in sorted(degree_counts.keys(), key=lambda x: (x is None, x)):
        print(f"  Degree {d}: {degree_counts[d]}")

    # Book distribution
    book_counts = Counter(r['book'] for r in recipes)
    print(f"\n--- Book Distribution ---")
    for b, c in book_counts.most_common():
        print(f"  {b}: {c}")

    # Product type distribution
    product_counts = Counter(r['primary_product'] for r in recipes)
    print(f"\n--- Primary Product Type Distribution ---")
    for p, c in product_counts.most_common():
        print(f"  {p}: {c}")

    # Method distribution
    method_counts = Counter()
    for r in recipes:
        for m in r['methods']:
            method_counts[m] += 1
    print(f"\n--- Method Distribution ---")
    for m, c in method_counts.most_common():
        print(f"  {m}: {c}")

    # Classification breakdown
    cls_counts = Counter(r['classification'] for r in recipes)
    print(f"\n--- Classification Breakdown ---")
    for c, n in cls_counts.most_common():
        print(f"  {c}: {n}")

    # Build output
    output = {
        'metadata': {
            'source': 'brunschwig_1512_english.txt',
            'source_lines': len(lines),
            'total_segments': len(segments),
            'segment_classification': dict(stats),
            'total_recipes': len(recipes),
            'extraction_date': '2026-03-15',
            'phase': '598a',
            'note': 'Semi-automated extraction. All recipes from 1512 de compositis. '
                    'Fire degrees inferred from method keywords when not explicit.'
        },
        'fire_degree_distribution': {
            str(k): v for k, v in sorted(degree_counts.items(),
                                         key=lambda x: (x[0] is None, x[0]))
        },
        'book_distribution': dict(book_counts),
        'product_distribution': dict(product_counts),
        'method_distribution': dict(method_counts),
        'recipes': recipes
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(recipes)} recipes to {OUT}")


if __name__ == '__main__':
    main()

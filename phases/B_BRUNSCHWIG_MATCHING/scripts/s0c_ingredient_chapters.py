"""
Phase 642, Script 0c: Segment Brunschwig 1512 ingredient-reference chapters.

The "Von X" ingredient-reference chapters of 1512 are dedicated descriptions
of individual ingredients used in compound preparations. Found 7 such chapters
clustered around pages 336-350 of the 1512 text:

  Von Piper (pepper varieties)
  Von Cinnamomum (cinnamon)
  Von Rosa (roses — included in ingredient-reference format)
  Von Scordeon (wild garlic)
  Von Opium (poppy juice)
  Von Agaricus (larch fungus)
  Von Crocus (saffron varieties)

Each chapter describes: etymology → botanical/mineral source → varieties/grades →
preparation methods → uses. Structurally similar to what PT-018 matched to f55r.

Additional source: Book 5 chapters have "Von X" markers for diseases/conditions,
not ingredients — these are DIFFERENT and excluded from this extraction.
"""
import sys, io, os, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

B1512 = os.path.join(ROOT, 'sources', 'brunchwig-zip', 'brunschwig_1512_english.txt')
OUT = os.path.join(os.path.dirname(__file__), '..', 'results', 'brunschwig_1512_ingredient_chapters.json')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Target: "Das XXXVI. Capitel — Von [Ingredient]" pattern, but also
# "Das ... Capitel — [Ingredient] continued" continuation pages
# The 7 ingredient chapters we identified are all in the XXXVI range.

with open(B1512, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all "Von X" markers — ingredient-reference signals
INGREDIENT_MARKER = re.compile(
    r'Das\s+[IVXLC]+\.\s+Capitel\s*[—-]\s*Von\s+([A-Z][a-zA-Z]+)',
    re.IGNORECASE
)

# Find all page-header lines with "Von X" inside
ingredient_starts = []
for i, line in enumerate(lines):
    m = INGREDIENT_MARKER.search(line)
    if m:
        ingredient = m.group(1)
        ingredient_starts.append({
            'line_no': i + 1,
            'ingredient': ingredient,
            'header_text': line.strip(),
        })

print(f"'Von X' ingredient-chapter markers found: {len(ingredient_starts)}")
for s in ingredient_starts:
    print(f"  L{s['line_no']:>5d}: Von {s['ingredient']:<15s} -- {s['header_text'][:80]}")

# Group by ingredient — collect all pages/continuations
# For each unique ingredient, find first "Von X" marker + all continuation lines
# until the next distinct ingredient
ingredient_blocks = {}
for s in ingredient_starts:
    ing = s['ingredient'].lower()
    if ing not in ingredient_blocks:
        ingredient_blocks[ing] = {
            'ingredient': s['ingredient'],
            'first_line': s['line_no'],
            'last_line': None,
            'header_lines': [s['line_no']],
        }
    else:
        ingredient_blocks[ing]['header_lines'].append(s['line_no'])

# For each ingredient block, figure out where it ends:
# either at the next DIFFERENT ingredient's first line, or at end of file
ordered_ingredients = sorted(ingredient_blocks.keys(), key=lambda k: ingredient_blocks[k]['first_line'])
for i, ing in enumerate(ordered_ingredients):
    block = ingredient_blocks[ing]
    last_header = max(block['header_lines'])
    # Find where the next distinct ingredient starts
    if i + 1 < len(ordered_ingredients):
        next_ing = ordered_ingredients[i+1]
        next_start = ingredient_blocks[next_ing]['first_line']
        block['last_line'] = next_start - 1
    else:
        # Last ingredient — bound at next major chapter header or +100 lines max
        # (avoids absorbing the rest of the file like Crocus did)
        search_start = last_header + 20
        search_end = min(len(lines), last_header + 120)
        block['last_line'] = last_header + 80  # default
        for k in range(search_start, search_end):
            if k < len(lines) and re.search(r'^(Das\s+[IVXLC]+\.\s+Capitel|---\s+Page\s+\d+\s+\(Des)', lines[k]):
                block['last_line'] = k
                break

# Filter to the actual ingredient-reference cluster (lines 17397-17700).
# Exclude:
#   - Von distillieren (L3268) — section header for "On distillation"
#   - Von digirierung (L3304) — "On digestion" is a broader topic, not an ingredient
#   - Von den (L13633) — "On the virtues and powers of Aqua vitae", not ingredient
#   - Any post-L17700 "Von X" markers (Book 5 is diseases/symptoms)
TRUE_INGREDIENT_RANGE = (17000, 17800)
filtered = {k: v for k, v in ingredient_blocks.items()
            if TRUE_INGREDIENT_RANGE[0] <= v['first_line'] <= TRUE_INGREDIENT_RANGE[1]}

# Also add Von Rosa manually — it's mentioned in-line on continuation header
# "Das XXXVI. Capitel — Cinnamomum concluded, Von Rosa / roses) ---"
# Scan line 17462 for this pattern
for i, line in enumerate(lines):
    if 17450 <= i+1 <= 17500 and re.search(r'Von\s+Rosa', line):
        # Rosa starts at the line where "Von Rosa" appears
        # bounded by next "Von X" header
        # Since line numbers are sorted, find where Von Cinnamomum ends
        cinnamon_block = filtered.get('cinnamomum')
        if cinnamon_block:
            # Rosa starts right after Cinnamon at line ~17462 (cinnamon's line 17450-ish + 12 lines of cinnamon)
            rosa_start = i + 1
            # Bound Rosa at where Scordeon starts
            scordeon_start = filtered.get('scordeon', {}).get('first_line', rosa_start + 30)
            filtered['rosa'] = {
                'ingredient': 'Rosa',
                'first_line': rosa_start,
                'last_line': scordeon_start - 1,
                'header_lines': [i+1],
            }
            # Also trim cinnamon's last_line to stop before Rosa
            cinnamon_block['last_line'] = rosa_start - 1
        break

print(f"\nFiltered to actual INGREDIENT-reference chapters (excluding Book 5 disease sections):")
print(f"  Kept: {len(filtered)}")
for ing, block in sorted(filtered.items(), key=lambda kv: kv[1]['first_line']):
    print(f"    Von {block['ingredient']:<15s}: L{block['first_line']}-L{block['last_line']} ({block['last_line'] - block['first_line']} lines)")

# Extract each ingredient chapter's text
output = {
    'metadata': {
        'phase': 642,
        'script': 's0c_ingredient_chapters',
        'n_ingredient_chapters': len(filtered),
    },
    'chapters': [],
}

for ing, block in sorted(filtered.items(), key=lambda kv: kv[1]['first_line']):
    chapter_text = ''.join(lines[block['first_line']-1:block['last_line']])
    # Also compute basic features
    feature_patterns = {
        'heat_mode':       re.compile(r'\b(fire|heat|warm|balneum|bath|sun|ashes|furnace|sand bath|dung)\b', re.IGNORECASE),
        'gentle_heat':     re.compile(r'\b(gentle|gently|mild|lukewarm|slow|soft)\s*(?:fire|heat|warm|bath|warmth)?\b', re.IGNORECASE),
        'extraction':      re.compile(r'\b(cut|pierce|pound|crush|grind|milk\s+runs|sap\s+flows|juice\s+flows|flows?\s+out|what\s+comes\s+out|drips?)\b', re.IGNORECASE),
        'sealing':         re.compile(r'\b(seal\w*|lute\w*|close\w*|cover\w*|paste|wax)\b', re.IGNORECASE),
        'monitoring':      re.compile(r'\b(see|appear|sign|watch|observe|note|until|when\s+you\s+see)\b', re.IGNORECASE),
        'multiple_methods':re.compile(r'\b(another\s+way|another\s+method|others?\s+(?:pound|cut|pierce|dry|do))\b', re.IGNORECASE),
        'dosage_specific': re.compile(r'\b\d+\s+(?:lot|quintin|dram|grain|ounce)\b', re.IGNORECASE),
        'drying':          re.compile(r'\b(dry|dried|dry\s+in\s+sun|sun-dried)\b', re.IGNORECASE),
        'vessel':          re.compile(r'\b(vessel|pot|jar|phial|vial|glass|alembic|cucurbit)\b', re.IGNORECASE),
        'topical':         re.compile(r'\b(rubbed|anointed|washed|soaked\s+(?:cloth|tow|linen)|cloth\s+(?:soaked|wetted)|laid\s+over|applied)\b', re.IGNORECASE),
        'internal':        re.compile(r'\b(drunk|consumed|eat|ingested|taken\s+in(?:side|ternally))\b', re.IGNORECASE),
    }

    feats = {}
    n_words = len(chapter_text.split())
    for name, p in feature_patterns.items():
        matches = p.findall(chapter_text)
        feats[name + '_count'] = len(matches)
        feats[name + '_rate'] = len(matches) / max(1, n_words / 100)  # per 100 words

    output['chapters'].append({
        'ingredient': block['ingredient'],
        'first_line': block['first_line'],
        'last_line': block['last_line'],
        'line_count': block['last_line'] - block['first_line'],
        'word_count': n_words,
        'features': feats,
    })

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote {OUT}")
print(f"\nFeature summary per chapter:")
for ch in output['chapters']:
    nonzero = [k for k, v in ch['features'].items() if k.endswith('_count') and v > 0]
    print(f"  Von {ch['ingredient']:<15s} ({ch['word_count']:>4d} words): {', '.join(nonzero[:6])}")

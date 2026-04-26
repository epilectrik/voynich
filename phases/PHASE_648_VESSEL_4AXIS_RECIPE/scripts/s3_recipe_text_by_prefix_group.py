"""
Phase 648 Step 3: Group matched folios by their dominant o-prefix,
then dump the Catalan recipe text for each group. Read directly to
derive what each prefix actually monitors physically.
"""
import sys
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

# Load profile
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/o_prefix_folio_profile.json') as f:
    profile = json.load(f)

# Load matched recipes
with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)

# Load corpus
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as f:
    corpus = json.load(f)

# Lookup chapter by part + chapter_num
def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

# For each matched folio, find dominant prefix (highest relative enrichment)
means = {'ok': 0.0691, 'ot': 0.0591, 'ol': 0.0543, 'or': 0.0214}

groups = {'ok': [], 'ot': [], 'ol': [], 'or': []}
folio_data = {}

for m in matches:
    folio = m['folio']
    if folio not in profile:
        continue
    p = profile[folio]
    rel = {pref: (p[f'{pref}_frac'] - means[pref]) / means[pref] for pref in means}
    sorted_rel = sorted(rel.items(), key=lambda x: -x[1])
    top = sorted_rel[0][0]
    chapter = get_chapter(m['part'], m['chapter_num'])
    if not chapter:
        continue

    folio_data[folio] = {
        'recipe_label': m['recipe_label'],
        'tier': m['tier'],
        'top_prefix': top,
        'top_rel': sorted_rel[0][1],
        'all_ranks': sorted_rel,
        'rates': {pref: p[f'{pref}_frac'] for pref in means},
        'chapter': chapter,
    }
    groups[top].append(folio)

# Print grouped recipe text
print("="*80)
print("FOLIOS GROUPED BY DOMINANT O-PREFIX")
print("="*80)

for prefix in ('ol', 'ot', 'ok', 'or'):
    flist = groups[prefix]
    print()
    print("#" * 80)
    print(f"# DOMINANT PREFIX: {prefix.upper()}  ({len(flist)} matched folios)")
    print("#" * 80)
    for f in flist:
        d = folio_data[f]
        print()
        print(f"--- {f}  [{d['tier']}]  {d['recipe_label']}")
        print(f"    rates: ok={d['rates']['ok']*100:.1f}% ot={d['rates']['ot']*100:.1f}% "
              f"ol={d['rates']['ol']*100:.1f}% or={d['rates']['or']*100:.1f}%")
        print(f"    Chapter: {d['chapter']['part']}.{d['chapter']['chapter_num']}")
        print(f"    Title (Catalan): {d['chapter']['title_catalan']}")
        print()
        for i, para in enumerate(d['chapter']['paragraphs']):
            text = para.get('catalan', '') or para.get('latin', '')
            if text:
                print(f"    [P{i}] {text[:600]}")
                if len(text) > 600:
                    print(f"          ... [+{len(text)-600} chars]")
                print()

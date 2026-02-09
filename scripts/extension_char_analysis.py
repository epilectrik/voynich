"""Do extension characters encode qualitative properties (sensory, color, smell)?

Tests whether per-folio extension character distributions correlate with:
1. Output category (WATER vs OIL)
2. Material category (ANIMAL vs DELICATE_PLANT)
3. Section (S vs H vs B)
4. Kernel balance
5. Brunschwig sensory modalities (cross-referenced)

Also checks: what do the existing single-char MIDDLE glosses say?
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

# --- Load data ---
tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer._core_middles

with open('data/middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)['middles']

with open('results/folio_operational_profiles.json', encoding='utf-8') as f:
    profiles = {p['folio']: p for p in json.load(f)['profiles']}

# --- Get single-char MIDDLE glosses (these ARE extension character meanings) ---
print("=" * 70)
print("EXISTING SINGLE-CHARACTER MIDDLE GLOSSES")
print("(These are the extension characters and their known meanings)")
print("=" * 70)

single_char_glosses = {}
for name, entry in sorted(mid_dict.items()):
    if len(name) == 1:
        gloss = entry.get('gloss')
        kernel = entry.get('kernel')
        regime = entry.get('regime')
        tc = entry.get('token_count', 0)
        fc = entry.get('folio_count', 0)
        single_char_glosses[name] = gloss
        print(f"  '{name}': gloss={str(gloss):20s} kernel={str(kernel):5s} "
              f"regime={str(regime):12s} tokens={tc:4d} folios={fc}")

# --- Build per-folio extension character profiles ---
folio_meta = {}
for t in tx.currier_b():
    if t.folio not in folio_meta:
        folio_meta[t.folio] = {'section': getattr(t, 'section', '?')}

b_folios = sorted(set(t.folio for t in tx.currier_b()))

folio_ext_profiles = {}
for folio in b_folios:
    tokens = [t for t in tx.currier_b() if t.folio == folio]
    ext_chars = Counter()
    total_ext_chars = 0
    total_tokens = len(tokens)

    for t in tokens:
        m = morph.extract(t.word)
        if m and m.middle and m.middle not in core_middles:
            # Decompose
            best = None
            for atom in sorted(core_middles, key=len, reverse=True):
                idx = m.middle.find(atom)
                if idx >= 0:
                    pre = m.middle[:idx]
                    post = m.middle[idx + len(atom):]
                    ext_len = len(pre) + len(post)
                    if ext_len <= 6 and (best is None or ext_len < best[2]):
                        best = (pre, post, ext_len)
            if best:
                for ch in best[0] + best[1]:
                    ext_chars[ch] += 1
                    total_ext_chars += 1

    # Normalize to proportions
    if total_ext_chars > 0:
        ext_props = {ch: count / total_ext_chars for ch, count in ext_chars.items()}
    else:
        ext_props = {}

    prof = profiles.get(folio, {})
    folio_ext_profiles[folio] = {
        'ext_chars': ext_chars,
        'ext_props': ext_props,
        'total_ext_chars': total_ext_chars,
        'token_count': total_tokens,
        'output': prof.get('output_category', '?'),
        'material': prof.get('material_category', '?'),
        'balance': prof.get('kernel_balance', '?'),
        'section': folio_meta.get(folio, {}).get('section', '?'),
    }

# --- Test 1: Extension chars by OUTPUT category ---
print(f"\n{'='*70}")
print("EXTENSION CHARACTERS BY OUTPUT CATEGORY (WATER vs OIL)")
print("=" * 70)

for output_cat in ['WATER', 'OIL']:
    folios_in_cat = [f for f, p in folio_ext_profiles.items() if p['output'] == output_cat]
    total = Counter()
    for f in folios_in_cat:
        total.update(folio_ext_profiles[f]['ext_chars'])

    grand = sum(total.values()) or 1
    print(f"\n  {output_cat} ({len(folios_in_cat)} folios):")
    for ch, count in total.most_common(15):
        pct = 100 * count / grand
        bar = '#' * int(pct * 2)
        gloss = single_char_glosses.get(ch, '?')
        print(f"    '{ch}': {pct:5.1f}% ({count:4d}) {bar:30s} [{gloss}]")

# --- Test 2: Extension chars by SECTION ---
print(f"\n{'='*70}")
print("EXTENSION CHARACTERS BY SECTION")
print("=" * 70)

sections = sorted(set(p['section'] for p in folio_ext_profiles.values()))
section_profiles = {}
for sec in sections:
    folios_in = [f for f, p in folio_ext_profiles.items() if p['section'] == sec]
    total = Counter()
    for f in folios_in:
        total.update(folio_ext_profiles[f]['ext_chars'])
    grand = sum(total.values()) or 1
    section_profiles[sec] = {ch: count / grand for ch, count in total.items()}

    print(f"\n  Section {sec} ({len(folios_in)} folios):")
    for ch, count in total.most_common(10):
        pct = 100 * count / grand
        gloss = single_char_glosses.get(ch, '?')
        print(f"    '{ch}': {pct:5.1f}% ({count:4d})  [{gloss}]")

# --- Test 3: Which extension characters DIFFERENTIATE sections? ---
print(f"\n{'='*70}")
print("EXTENSION CHARACTER ENRICHMENT BY SECTION")
print("(Which chars are over/under-represented vs corpus average)")
print("=" * 70)

# Corpus average
all_ext = Counter()
for p in folio_ext_profiles.values():
    all_ext.update(p['ext_chars'])
corpus_total = sum(all_ext.values()) or 1
corpus_avg = {ch: count / corpus_total for ch, count in all_ext.items()}

all_chars = sorted(all_ext.keys(), key=lambda c: all_ext[c], reverse=True)[:15]

# Header
header = f"{'char':>6s} {'gloss':>15s} {'corpus':>7s}"
for sec in sections:
    header += f" {sec:>7s}"
print(header)
print("-" * len(header))

for ch in all_chars:
    gloss = str(single_char_glosses.get(ch, '?'))[:15]
    row = f"  '{ch}' {gloss:>15s} {100*corpus_avg.get(ch,0):6.1f}%"
    for sec in sections:
        sec_rate = 100 * section_profiles.get(sec, {}).get(ch, 0)
        corp_rate = 100 * corpus_avg.get(ch, 0)
        if corp_rate > 0:
            enrichment = sec_rate / corp_rate
            if enrichment > 1.3:
                marker = '+++'
            elif enrichment > 1.1:
                marker = '+ '
            elif enrichment < 0.7:
                marker = '---'
            elif enrichment < 0.9:
                marker = '-  '
            else:
                marker = '   '
        else:
            marker = '   '
        row += f" {sec_rate:5.1f}%{marker}"
    print(row)

# --- Test 4: Extension chars by MATERIAL category ---
print(f"\n{'='*70}")
print("EXTENSION CHARACTER ENRICHMENT BY MATERIAL CATEGORY")
print("=" * 70)

mat_cats = ['ANIMAL', 'DELICATE_PLANT', 'ROOT']
mat_profiles = {}
for mat in mat_cats:
    folios_in = [f for f, p in folio_ext_profiles.items() if p['material'] == mat]
    total = Counter()
    for f in folios_in:
        total.update(folio_ext_profiles[f]['ext_chars'])
    grand = sum(total.values()) or 1
    mat_profiles[mat] = {ch: count / grand for ch, count in total.items()}

header = f"{'char':>6s} {'gloss':>15s} {'corpus':>7s}"
for mat in mat_cats:
    label = mat[:7]
    header += f" {label:>9s}"
print(header)
print("-" * len(header))

for ch in all_chars:
    gloss = str(single_char_glosses.get(ch, '?'))[:15]
    row = f"  '{ch}' {gloss:>15s} {100*corpus_avg.get(ch,0):6.1f}%"
    for mat in mat_cats:
        mat_rate = 100 * mat_profiles.get(mat, {}).get(ch, 0)
        corp_rate = 100 * corpus_avg.get(ch, 0)
        if corp_rate > 0:
            enrichment = mat_rate / corp_rate
            if enrichment > 1.3:
                marker = '+++'
            elif enrichment > 1.1:
                marker = '+ '
            elif enrichment < 0.7:
                marker = '---'
            elif enrichment < 0.9:
                marker = '-  '
            else:
                marker = '   '
        else:
            marker = '   '
        row += f"   {mat_rate:5.1f}%{marker}"
    print(row)

# --- Test 5: Brunschwig sensory cross-reference ---
print(f"\n{'='*70}")
print("BRUNSCHWIG SENSORY MODALITY CROSS-REFERENCE")
print("=" * 70)

with open('data/brunschwig_curated_v3.json', encoding='utf-8') as f:
    brun_data = json.load(f)

# What sensory modalities exist in Brunschwig?
sensory_dist = Counter()
for recipe in brun_data['recipes']:
    for mod in recipe.get('sensory_modality', ['NONE']):
        sensory_dist[mod] += 1

print(f"\nBrunschwig sensory modality distribution:")
for mod, count in sensory_dist.most_common():
    print(f"  {mod}: {count} recipes")

# Group recipes by primary sensory modality
sensory_recipes = defaultdict(list)
for recipe in brun_data['recipes']:
    mods = recipe.get('sensory_modality', ['NONE'])
    for mod in mods:
        sensory_recipes[mod].append(recipe)

# For each modality, what action patterns distinguish them?
print(f"\nAction patterns by sensory modality:")
for mod in ['SIGHT', 'SMELL', 'TASTE', 'TOUCH', 'SOUND']:
    recipes = sensory_recipes.get(mod, [])
    if not recipes:
        continue
    actions = Counter()
    for r in recipes:
        for step in (r.get('procedural_steps') or []):
            actions[step.get('action', 'UNKNOWN')] += 1
    total_a = sum(actions.values()) or 1
    top = ', '.join(f"{a}:{100*c/total_a:.0f}%" for a, c in actions.most_common(5))
    mat_classes = Counter(r.get('material_class', '?') for r in recipes)
    top_mats = ', '.join(f"{m}:{c}" for m, c in mat_classes.most_common(3))
    print(f"\n  {mod} ({len(recipes)} recipes): {top}")
    print(f"    Materials: {top_mats}")

# --- Test 6: Per-folio extension SIGNATURE clustering ---
print(f"\n{'='*70}")
print("FOLIO EXTENSION SIGNATURES (top-3 chars per folio)")
print("=" * 70)

# What are the most common top-3 extension signatures?
signatures = Counter()
for folio, p in folio_ext_profiles.items():
    if p['total_ext_chars'] >= 10:  # Skip very sparse folios
        top3 = tuple(ch for ch, _ in p['ext_chars'].most_common(3))
        signatures[top3] += 1

print(f"\nMost common top-3 extension signatures:")
for sig, count in signatures.most_common(15):
    example_folios = [f for f, p in folio_ext_profiles.items()
                      if p['total_ext_chars'] >= 10
                      and tuple(ch for ch, _ in p['ext_chars'].most_common(3)) == sig]
    secs = Counter(folio_ext_profiles[f]['section'] for f in example_folios)
    outs = Counter(folio_ext_profiles[f]['output'] for f in example_folios)
    sec_str = ','.join(f"{s}:{c}" for s, c in secs.most_common())
    out_str = ','.join(f"{o}:{c}" for o, c in outs.most_common())
    chars = ', '.join(f"'{c}'" for c in sig)
    print(f"  [{chars}]: {count} folios | sec={sec_str} | out={out_str}")

# --- Summary ---
print(f"\n{'='*70}")
print("SUMMARY: WHAT EXTENSION CHARACTERS MIGHT ENCODE")
print("=" * 70)

print(f"""
Known single-char MIDDLE glosses (operational meanings):
  'k' = heat        'e' = cool/settle   'h' = monitor
  'd' = mark        't' = transfer      's' = next/sequence
  'l' = frame       'r' = continue      'y' = end

Questions:
  'o' = ?  (most common extension, {all_ext['o']} occurrences)
  'c' = ?  ({all_ext.get('c',0)} occurrences)
  'a' = ?  ({all_ext.get('a',0)} occurrences)
  'f' = ?  ({all_ext.get('f',0)} occurrences)
  'i' = ?  ({all_ext.get('i',0)} occurrences)
  'p' = ?  ({all_ext.get('p',0)} occurrences)

If sensory hypothesis is correct:
  - Extension chars would show SECTION-specific enrichment (different
    sections deal with materials with different sensory properties)
  - OIL folios would have different extension profiles than WATER folios
    (oil extraction involves different sensory monitoring)
  - The unglossed chars (o, c, a, f, i, p) would need to map to
    qualitative properties NOT already covered by k/e/h/d/t/s/l/r/y
""")

# Write results
output_data = {
    'single_char_glosses': single_char_glosses,
    'corpus_extension_freq': dict(all_ext.most_common()),
    'section_enrichment': {
        sec: {ch: round(section_profiles.get(sec, {}).get(ch, 0) /
              max(corpus_avg.get(ch, 0), 0.001), 2)
              for ch in all_chars}
        for sec in sections
    },
}

with open('results/extension_char_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Wrote results to results/extension_char_analysis.json")

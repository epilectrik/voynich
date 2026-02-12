"""Deep analysis of folio-unique MIDDLEs.

Questions:
- Are unique MIDDLEs compound (atom+extension) or novel atoms?
- Do they share extension patterns?
- Do distinctive folios cluster by regime/section?
- What do the unique MIDDLEs look like morphologically?
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, BFolioDecoder

# --- Setup ---
tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer._core_middles

# Get regime/section per folio from transcript metadata
folio_meta = {}
for t in tx.currier_b():
    if t.folio not in folio_meta:
        folio_meta[t.folio] = {
            'section': getattr(t, 'section', '?'),
            'language': getattr(t, 'language', '?'),
        }

# Load operational profiles for regime info
with open('results/folio_operational_profiles.json', encoding='utf-8') as f:
    op_profiles = {p['folio']: p for p in json.load(f)['profiles']}

# --- Build folio-unique MIDDLE inventory ---
b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Collect all MIDDLEs per folio
folio_middles = defaultdict(Counter)
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        folio_middles[t.folio][m.middle] += 1

# Which MIDDLEs appear in only 1 folio?
middle_to_folios = defaultdict(set)
for folio, mids in folio_middles.items():
    for mid in mids:
        middle_to_folios[mid].add(folio)

unique_middles = {mid: list(folios)[0]
                  for mid, folios in middle_to_folios.items()
                  if len(folios) == 1}

print(f"Total unique MIDDLEs across corpus: {len(set().union(*folio_middles.values()))}")
print(f"Folio-unique MIDDLEs: {len(unique_middles)} "
      f"({100*len(unique_middles)/len(set().union(*folio_middles.values())):.1f}%)")

# --- Decompose each unique MIDDLE ---
def decompose(middle):
    """Try to decompose into core atom + extensions."""
    if middle in core_middles:
        return {'type': 'CORE_ATOM', 'atom': middle, 'pre_ext': '', 'suf_ext': ''}

    best = None
    for atom in sorted(core_middles, key=len, reverse=True):
        idx = middle.find(atom)
        if idx >= 0:
            pre = middle[:idx]
            post = middle[idx + len(atom):]
            ext_len = len(pre) + len(post)
            if best is None or ext_len < best['ext_len']:
                best = {
                    'type': 'COMPOUND',
                    'atom': atom,
                    'pre_ext': pre,
                    'suf_ext': post,
                    'ext_len': ext_len,
                }

    if best:
        del best['ext_len']
        return best

    return {'type': 'NOVEL', 'atom': None, 'pre_ext': '', 'suf_ext': ''}


decomposed = {}
for mid, folio in unique_middles.items():
    d = decompose(mid)
    d['middle'] = mid
    d['folio'] = folio
    d['count'] = folio_middles[folio][mid]
    d['length'] = len(mid)
    decomposed[mid] = d

# --- Categorize ---
types = Counter(d['type'] for d in decomposed.values())
print(f"\nDecomposition types:")
for t, c in types.most_common():
    print(f"  {t}: {c} ({100*c/len(decomposed):.1f}%)")

# --- COMPOUND analysis ---
compounds = [d for d in decomposed.values() if d['type'] == 'COMPOUND']
print(f"\n{'='*70}")
print(f"COMPOUND UNIQUE MIDDLEs ({len(compounds)})")
print(f"{'='*70}")

# Extension character frequency in unique compounds
ext_chars = Counter()
for d in compounds:
    for ch in d['pre_ext'] + d['suf_ext']:
        ext_chars[ch] += 1

print(f"\nExtension characters in folio-unique compounds:")
for ch, count in ext_chars.most_common(15):
    print(f"  '{ch}': {count}")

# Extension LENGTH distribution
ext_lens = Counter(len(d['pre_ext']) + len(d['suf_ext']) for d in compounds)
print(f"\nExtension length distribution:")
for l, c in sorted(ext_lens.items()):
    bar = '#' * c
    print(f"  {l} chars: {c} {bar}")

# Which core atoms are most extended in unique MIDDLEs?
atom_freq = Counter(d['atom'] for d in compounds)
print(f"\nCore atoms most extended in unique MIDDLEs:")
for atom, count in atom_freq.most_common(15):
    print(f"  '{atom}': {count} unique extensions")

# --- NOVEL analysis ---
novels = [d for d in decomposed.values() if d['type'] == 'NOVEL']
print(f"\n{'='*70}")
print(f"NOVEL UNIQUE MIDDLEs ({len(novels)}) - no known atom found")
print(f"{'='*70}")

# Length distribution
novel_lens = Counter(d['length'] for d in novels)
print(f"\nLength distribution:")
for l, c in sorted(novel_lens.items()):
    bar = '#' * c
    print(f"  {l} chars: {c} {bar}")

# Show examples grouped by length
for length in sorted(novel_lens.keys()):
    examples = [d for d in novels if d['length'] == length]
    if examples:
        sample = examples[:8]
        mids = ', '.join(d['middle'] for d in sample)
        print(f"  Length {length}: {mids}")

# --- Per-folio analysis: what makes distinctive folios distinctive? ---
print(f"\n{'='*70}")
print(f"DISTINCTIVE FOLIOS: WHAT MAKES THEM UNIQUE?")
print(f"{'='*70}")

folio_unique_list = defaultdict(list)
for d in decomposed.values():
    folio_unique_list[d['folio']].append(d)

# Sort by unique count
by_count = sorted(folio_unique_list.items(), key=lambda x: len(x[1]), reverse=True)

for folio, uniques in by_count[:15]:
    prof = op_profiles.get(folio, {})
    meta = folio_meta.get(folio, {})

    n_compound = sum(1 for u in uniques if u['type'] == 'COMPOUND')
    n_novel = sum(1 for u in uniques if u['type'] == 'NOVEL')
    n_core = sum(1 for u in uniques if u['type'] == 'CORE_ATOM')

    # Extension chars used
    ext_here = Counter()
    atoms_here = Counter()
    for u in uniques:
        if u['type'] == 'COMPOUND':
            for ch in u['pre_ext'] + u['suf_ext']:
                ext_here[ch] += 1
            atoms_here[u['atom']] += 1

    balance = prof.get('kernel_balance', '?')
    material = prof.get('material_category', '?')
    output = prof.get('output_category', '?')
    section = meta.get('section', '?')
    tc = prof.get('token_count', 0)

    print(f"\n  {folio} ({tc} tokens, section={section})")
    print(f"    Profile: {balance}, {material}, {output}")
    print(f"    Unique MIDDLEs: {len(uniques)} (compound={n_compound}, novel={n_novel}, core={n_core})")

    if atoms_here:
        top_atoms = ', '.join(f"'{a}'x{c}" for a, c in atoms_here.most_common(5))
        print(f"    Atoms extended: {top_atoms}")

    if ext_here:
        top_ext = ', '.join(f"'{ch}'x{c}" for ch, c in ext_here.most_common(5))
        print(f"    Extension chars: {top_ext}")

    # Show some examples
    examples = sorted(uniques, key=lambda u: u['count'], reverse=True)[:5]
    for ex in examples:
        if ex['type'] == 'COMPOUND':
            print(f"      '{ex['middle']}' (x{ex['count']}): {ex['pre_ext']}[{ex['atom']}]{ex['suf_ext']}")
        else:
            print(f"      '{ex['middle']}' (x{ex['count']}): {ex['type']}")

# --- Do distinctive folios cluster? ---
print(f"\n{'='*70}")
print(f"DO DISTINCTIVE FOLIOS CLUSTER?")
print(f"{'='*70}")

# Group folios by unique count tier
tiers = {'HIGH (20+)': [], 'MEDIUM (10-19)': [], 'LOW (1-9)': [], 'NONE (0)': []}
for folio in b_folios:
    uc = len(folio_unique_list.get(folio, []))
    prof = op_profiles.get(folio, {})
    meta = folio_meta.get(folio, {})
    entry = {
        'folio': folio,
        'unique_count': uc,
        'balance': prof.get('kernel_balance', '?'),
        'material': prof.get('material_category', '?'),
        'output': prof.get('output_category', '?'),
        'section': meta.get('section', '?'),
    }
    if uc >= 20:
        tiers['HIGH (20+)'].append(entry)
    elif uc >= 10:
        tiers['MEDIUM (10-19)'].append(entry)
    elif uc >= 1:
        tiers['LOW (1-9)'].append(entry)
    else:
        tiers['NONE (0)'].append(entry)

for tier_name, entries in tiers.items():
    print(f"\n  {tier_name}: {len(entries)} folios")

    # Distribution of properties within tier
    balances = Counter(e['balance'] for e in entries)
    materials = Counter(e['material'] for e in entries)
    outputs = Counter(e['output'] for e in entries)
    sections = Counter(e['section'] for e in entries)

    print(f"    Balance: {dict(balances)}")
    print(f"    Material: {dict(materials)}")
    print(f"    Output: {dict(outputs)}")
    print(f"    Section: {dict(sections)}")

    if len(entries) <= 15:
        for e in entries:
            print(f"      {e['folio']:8s} sec={e['section']:3s} {e['balance']:18s} {e['material']:15s} {e['output']}")

# --- Shared extension patterns between distinctive folios ---
print(f"\n{'='*70}")
print(f"EXTENSION PATTERN SIGNATURES")
print(f"{'='*70}")

# For HIGH folios, what extension chars dominate?
high_folios = [f for f, uniques in folio_unique_list.items() if len(uniques) >= 20]
for folio in sorted(high_folios):
    uniques = folio_unique_list[folio]
    ext_here = Counter()
    for u in uniques:
        if u['type'] == 'COMPOUND':
            for ch in u['pre_ext'] + u['suf_ext']:
                ext_here[ch] += 1

    if ext_here:
        sig = ' '.join(f"{ch}:{c}" for ch, c in ext_here.most_common(5))
        print(f"  {folio:8s}: {sig}")

# --- Write detailed results ---
output = {
    'total_unique_middles': len(unique_middles),
    'decomposition_types': dict(types),
    'compound_extension_chars': dict(ext_chars.most_common()),
    'compound_atom_freq': dict(atom_freq.most_common()),
    'novel_length_dist': dict(sorted(novel_lens.items())),
    'per_folio': {
        folio: {
            'unique_count': len(uniques),
            'compound': sum(1 for u in uniques if u['type'] == 'COMPOUND'),
            'novel': sum(1 for u in uniques if u['type'] == 'NOVEL'),
            'examples': [
                {'middle': u['middle'], 'type': u['type'],
                 'atom': u.get('atom'), 'count': u['count']}
                for u in sorted(uniques, key=lambda x: x['count'], reverse=True)[:10]
            ],
        }
        for folio, uniques in folio_unique_list.items()
        if uniques
    },
}

with open('results/folio_unique_middles.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote results to results/folio_unique_middles.json")

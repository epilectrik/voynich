"""
Phase 640 Sub-Phase 1: Populate baseline dictionary with structural data for all 479 B token types.

Outputs:
  results/b_dictionary_baseline.json — All tokens with structural features, no definitions yet
  results/b_dictionary_baseline.tsv — Flat table for review
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology, BFolioDecoder
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

# Collect all B tokens with context
print("Collecting all Currier B tokens...")
token_data = defaultdict(lambda: {
    'frequency': 0,
    'folios': set(),
    'sections': Counter(),
    'lines': [],
    'line_positions': [],  # Q0-Q4
    'par_initial': 0,
    'par_final': 0,
    'line_initial': 0,
    'line_final': 0,
})

folio_token_counts = Counter()
total_tokens = 0

for tok in tx.currier_b():
    word = tok.word.strip()
    if not word:
        continue
    total_tokens += 1
    d = token_data[word]
    d['frequency'] += 1
    d['folios'].add(tok.folio)
    d['sections'][tok.section or '?'] += 1
    folio_token_counts[tok.folio] += 1
    if tok.par_initial:
        d['par_initial'] += 1
    if tok.par_final:
        d['par_final'] += 1
    if tok.line_initial:
        d['line_initial'] += 1
    if tok.line_final:
        d['line_final'] += 1

print(f"Total tokens: {total_tokens}")
print(f"Unique types: {len(token_data)}")

# Build dictionary entries
print("Building dictionary entries...")
entries = {}

for word in sorted(token_data.keys(), key=lambda w: -token_data[w]['frequency']):
    d = token_data[word]
    m = morph.extract(word)
    a = morph.atomize(word)

    # Atom decomposition
    atoms = []
    if a and a.atoms:
        for at in a.atoms:
            atoms.append({
                'char': at[0],
                'role': at[1],
                'gloss': at[2],
            })

    # Section profile
    total_sec = sum(d['sections'].values())
    section_profile = {s: round(c / total_sec, 3) for s, c in d['sections'].most_common()}

    # Position profile
    freq = d['frequency']

    entry = {
        'token': word,
        'frequency': freq,
        'frequency_rank': 0,  # fill below
        'corpus_pct': round(100 * freq / total_tokens, 3),
        'folio_count': len(d['folios']),
        'folios': sorted(d['folios']),
        'section_profile': section_profile,
        # Morphology
        'prefix': m.prefix if m else None,
        'middle': m.middle if m else None,
        'suffix': m.suffix if m else None,
        'has_articulator': a.is_headless if a else None,  # approximate
        # Atoms
        'atom_count': len(atoms),
        'atoms': atoms,
        'atom_gloss': a.gloss if a else None,
        'e_depth': a.e_depth if a else None,
        'head_atom': atoms[0]['char'] if atoms else None,
        'terminal_atom': atoms[-1]['char'] if atoms else None,
        'is_headless': a.is_headless if a else None,
        # Positional
        'par_initial_rate': round(d['par_initial'] / freq, 3) if freq else 0,
        'par_final_rate': round(d['par_final'] / freq, 3) if freq else 0,
        'line_initial_rate': round(d['line_initial'] / freq, 3) if freq else 0,
        'line_final_rate': round(d['line_final'] / freq, 3) if freq else 0,
        # Definition (empty for now)
        'operational_def': None,
        'workshop_reading': None,
        'confidence': None,
        'evidence': [],
        'notes': None,
    }

    entries[word] = entry

# Assign frequency ranks
for rank, word in enumerate(sorted(entries.keys(), key=lambda w: -entries[w]['frequency']), 1):
    entries[word]['frequency_rank'] = rank

# Output JSON
output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(output_dir, exist_ok=True)

json_path = os.path.join(output_dir, 'b_dictionary_baseline.json')
# Convert sets to lists for JSON
for e in entries.values():
    if isinstance(e.get('folios'), set):
        e['folios'] = sorted(e['folios'])

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({
        'metadata': {
            'total_tokens': total_tokens,
            'unique_types': len(entries),
            'phase': 640,
            'sub_phase': 1,
            'description': 'Baseline structural data for all Currier B token types',
        },
        'entries': entries,
    }, f, indent=2, ensure_ascii=False)

print(f"Wrote {json_path}")

# Output TSV
tsv_path = os.path.join(output_dir, 'b_dictionary_baseline.tsv')
with open(tsv_path, 'w', encoding='utf-8') as f:
    headers = [
        'rank', 'token', 'frequency', 'corpus_pct', 'folio_count',
        'prefix', 'middle', 'suffix', 'atom_gloss', 'e_depth',
        'head_atom', 'terminal_atom', 'is_headless',
        'par_initial_rate', 'line_initial_rate', 'line_final_rate',
        'top_section', 'confidence', 'operational_def',
    ]
    f.write('\t'.join(headers) + '\n')

    for word in sorted(entries.keys(), key=lambda w: -entries[w]['frequency']):
        e = entries[word]
        top_sec = max(e['section_profile'], key=e['section_profile'].get) if e['section_profile'] else '?'
        row = [
            str(e['frequency_rank']),
            e['token'],
            str(e['frequency']),
            str(e['corpus_pct']),
            str(e['folio_count']),
            e['prefix'] or '',
            e['middle'] or '',
            e['suffix'] or '',
            e['atom_gloss'] or '',
            str(e['e_depth']) if e['e_depth'] is not None else '',
            e['head_atom'] or '',
            e['terminal_atom'] or '',
            str(e['is_headless']) if e['is_headless'] is not None else '',
            str(e['par_initial_rate']),
            str(e['line_initial_rate']),
            str(e['line_final_rate']),
            top_sec,
            e['confidence'] or '',
            e['operational_def'] or '',
        ]
        f.write('\t'.join(row) + '\n')

print(f"Wrote {tsv_path}")

# Summary
freq_sorted = sorted(entries.values(), key=lambda e: -e['frequency'])
print(f"\nTop 20 tokens by frequency:")
for e in freq_sorted[:20]:
    print(f"  {e['frequency_rank']:3d}. {e['token']:<20s} freq={e['frequency']:>4d}  folios={e['folio_count']:>2d}  gloss={e['atom_gloss']}")

print(f"\nFrequency distribution:")
brackets = [(1, 1), (2, 5), (6, 20), (21, 50), (51, 100), (101, 500), (501, 10000)]
for lo, hi in brackets:
    count = sum(1 for e in entries.values() if lo <= e['frequency'] <= hi)
    tokens = sum(e['frequency'] for e in entries.values() if lo <= e['frequency'] <= hi)
    print(f"  freq {lo:>4d}-{hi:>5d}: {count:>4d} types, {tokens:>5d} tokens ({100*tokens/total_tokens:.1f}%)")

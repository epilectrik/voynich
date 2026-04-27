"""
Full atom-level decode of f82r against matched recipe III.22
(lunaria maceration, 3-day sealed)
"""
import sys, io, json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

FOLIO = 'f82r'

tokens = list(tx.currier_b())
folio_tokens = [t for t in tokens if t.folio == FOLIO]

print(f'=== {FOLIO} DECODE ===')
print(f'Total tokens: {len(folio_tokens)}')

by_line = defaultdict(list)
for t in folio_tokens:
    by_line[t.line].append(t)

def line_sort_key(x):
    return (int(''.join(c for c in str(x) if c.isdigit()) or '0'), str(x))

GALLOWS = {'t', 'k', 'p', 'f'}
lines_sorted = sorted(by_line.keys(), key=line_sort_key)

para_breaks = []
for line in lines_sorted:
    first_word = by_line[line][0].word
    if first_word and first_word[0] in GALLOWS:
        para_breaks.append(line)

print(f'Lines: {len(lines_sorted)} ({lines_sorted[0]}-{lines_sorted[-1]})')
print(f'Gallows-initial lines: {para_breaks}')

paragraphs = []
current_para = []
current_start = lines_sorted[0]

for i, line in enumerate(lines_sorted):
    if line in para_breaks and current_para:
        paragraphs.append({
            'tokens': [t for group in current_para for t in group],
            'start': current_start,
        })
        current_para = []
        current_start = line
    current_para.append(by_line[line])

if current_para:
    paragraphs.append({
        'tokens': [t for group in current_para for t in group],
        'start': current_start,
    })

print(f'Paragraphs: {len(paragraphs)}')
for i, p in enumerate(paragraphs):
    unique_lines = sorted(set(t.line for t in p['tokens']), key=line_sort_key)
    print(f'  P{i+1}: {len(p["tokens"])} tokens, lines {unique_lines[0]}-{unique_lines[-1]}')

PREFIX_GLOSSES = {
    'qo': 'HEAT-OP', 'ch': 'MONITOR', 'sh': 'OBSERVE',
    'ok': 'VESSEL-CORRECT', 'ot': 'VESSEL-SEAL', 'ol': 'VESSEL-LOAD',
    'or': 'VESSEL-RESPOND', 'da': 'MATERIAL-ADD',
}

OBSERVE_MIDDLES = {
    'ckh': 'heat-level-check', 'cth': 'transfer-watch',
    'ecth': 'cooled-transfer-watch', 'cfh': 'flag-heat-check',
    'cthh': 'transfer-watch-extended', 'ecthe': 'cooled-transfer-watch-end',
    'ckhh': 'heat-watch-extended', 'cphh': 'pause-watch-extended',
}

print('\n' + '='*80)
print('SEQUENTIAL TOKEN DECODE')
print('='*80)

results = {'folio': FOLIO, 'paragraphs': []}

for pi, para in enumerate(paragraphs):
    unique_lines = sorted(set(t.line for t in para['tokens']), key=line_sort_key)
    print(f'\n{"="*60}')
    print(f'PARAGRAPH {pi+1} (lines {unique_lines[0]}-{unique_lines[-1]}, {len(para["tokens"])} tokens)')
    print(f'{"="*60}')

    prefix_counts = Counter()
    head_counts = Counter()
    dar_count = 0
    chekar_count = 0
    obs_middle_counts = Counter()
    e_depths = []
    hh_count = 0

    current_line = None
    for t in para['tokens']:
        if t.line != current_line:
            current_line = t.line
            print(f'\n  --- Line {t.line} ---')

        a = morph.atomize(t.word)
        m = morph.extract(t.word)

        pfx_label = PREFIX_GLOSSES.get(a.prefix, a.prefix or '?')
        atoms_str = '.'.join(at[2] for at in a.atoms) if a.atoms else '(none)'
        atom_codes = '.'.join(at[0] for at in a.atoms) if a.atoms else ''

        obs_note = ''
        if a.prefix in ('ch', 'sh') and m.middle:
            if m.middle in OBSERVE_MIDDLES:
                obs_note = f' << {OBSERVE_MIDDLES[m.middle]}'
                obs_middle_counts[m.middle] += 1

        atom_seq = ''.join(at[0] for at in a.atoms)
        if 'hh' in atom_seq:
            hh_count += 1
            if not obs_note:
                obs_note = ' << hh-EXTENDED'

        is_dar = (a.prefix == 'da')
        if is_dar:
            dar_count += 1

        is_chekar = (t.word.startswith('chek') or t.word.startswith('shek'))
        if is_chekar:
            chekar_count += 1

        prefix_counts[a.prefix or 'none'] += 1
        if a.atoms:
            head_counts[a.atoms[0][0]] += 1
        e_depths.append(a.e_depth)

        print(f'    {t.word:<22s} [{pfx_label:<16s}] {atom_codes:<15s} {atoms_str}{obs_note}')

    mean_e = sum(e_depths) / len(e_depths) if e_depths else 0

    print(f'\n  SUMMARY P{pi+1}:')
    print(f'    Prefixes: {dict(prefix_counts.most_common())}')
    print(f'    HEADs: {dict(head_counts.most_common())}')
    print(f'    dar(material-add): {dar_count}')
    print(f'    chekar(quality-check): {chekar_count}')
    print(f'    Mean e-depth: {mean_e:.2f}')
    print(f'    Observation MIDDLEs: {dict(obs_middle_counts)}')
    print(f'    hh-extended tokens: {hh_count}')

    results['paragraphs'].append({
        'paragraph': pi+1,
        'lines': f'{unique_lines[0]}-{unique_lines[-1]}',
        'n_tokens': len(para['tokens']),
        'prefix_counts': dict(prefix_counts),
        'head_counts': dict(head_counts),
        'dar_count': dar_count,
        'chekar_count': chekar_count,
        'mean_e_depth': round(mean_e, 3),
        'obs_middle_counts': dict(obs_middle_counts),
        'hh_count': hh_count,
    })

out_path = REPO_ROOT / 'phases' / 'PHASE_668_F76R_COLD_READ' / 'results' / 'f82r_decode_summary.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print(f'\nSaved to {out_path}')

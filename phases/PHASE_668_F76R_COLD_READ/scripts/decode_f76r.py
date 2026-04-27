"""
Phase 668 — f76r cold read decode

Paragraph-by-paragraph atom-level decode of f76r for comparison
against matched recipe II.16/II.18 (element separation, silver-plate test).
"""
import sys
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

tokens = [t for t in tx.currier_b() if t.folio == 'f76r']

paragraphs = []
current = []
for t in tokens:
    if t.par_initial and current:
        paragraphs.append(current)
        current = []
    current.append(t)
if current:
    paragraphs.append(current)

print(f'=== f76r: {len(tokens)} tokens, {len(paragraphs)} paragraphs ===\n')

folio_stats = {
    'total_tokens': len(tokens),
    'paragraphs': len(paragraphs),
    'par_data': [],
}

for pi, par in enumerate(paragraphs):
    lines = defaultdict(list)
    for t in par:
        lines[t.line].append(t)

    line_range = f'L{min(lines)}-L{max(lines)}'
    print(f'--- P{pi+1} ({len(par)} tokens, {line_range}) ---')

    prefix_counts = Counter()
    head_counts = Counter()
    edepths = []
    dar_count = 0
    chekar_count = 0

    for t in par:
        a = morph.atomize(t.word)
        m = morph.extract(t.word)

        if a.prefix:
            prefix_counts[a.prefix] += 1

        atom_str = '.'.join(at[0] for at in a.atoms)
        gloss_str = '.'.join(at[2] for at in a.atoms)
        edepths.append(a.e_depth)

        if a.atoms:
            head_counts[a.atoms[0][2]] += 1

        if t.word.startswith('dar'):
            dar_count += 1
        if 'chekar' in t.word or t.word == 'chekar':
            chekar_count += 1

        pfx = a.prefix or '-'
        print(f'  L{t.line:>2} {t.word:<20s} [{pfx:>3}] {atom_str:<15s} {gloss_str}  e={a.e_depth}')

    mean_e = sum(edepths) / len(edepths) if edepths else 0
    print(f'\n  Summary: prefixes={dict(prefix_counts)}')
    print(f'  dar={dar_count}, chekar={chekar_count}, mean_e_depth={mean_e:.3f}')
    print(f'  HEAD distribution: {dict(head_counts)}')
    print()

    folio_stats['par_data'].append({
        'par': pi + 1,
        'n_tokens': len(par),
        'line_range': line_range,
        'prefixes': dict(prefix_counts),
        'dar': dar_count,
        'chekar': chekar_count,
        'mean_e_depth': mean_e,
        'heads': dict(head_counts),
    })

# Folio-level summary
all_pfx = Counter()
total_dar = 0
total_chekar = 0
all_e = []
for pd in folio_stats['par_data']:
    for k, v in pd['prefixes'].items():
        all_pfx[k] += v
    total_dar += pd['dar']
    total_chekar += pd['chekar']
    all_e.append(pd['mean_e_depth'])

print(f'=== FOLIO SUMMARY ===')
print(f'Prefix totals: {dict(all_pfx)}')
print(f'dar total: {total_dar}')
print(f'chekar total: {total_chekar}')
print(f'Mean e_depth per paragraph: {[f"{e:.3f}" for e in all_e]}')

out_dir = REPO_ROOT / 'phases' / 'PHASE_668_F76R_COLD_READ' / 'results'
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'f76r_decode_summary.json').write_text(
    json.dumps(folio_stats, indent=2), encoding='utf-8')
print(f'\nWrote summary.')

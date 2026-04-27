"""
How does h (watch) stack? Compare to e (cool) and i (iterate) stacking.
Where does hh appear? Is it rare? Does it pattern differently from single h?
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

# Count stacking depths for e, i, h across all Currier B
e_depths = Counter()
i_depths = Counter()
h_depths = Counter()

# Track where hh+ appears
hh_tokens = []

for t in tx.currier_b():
    a = morph.atomize(t.word)
    if not a.atoms:
        continue

    atom_seq = [at[0] for at in a.atoms]

    # Count consecutive runs
    for atom_type, depth_counter in [('e', e_depths), ('i', i_depths), ('h', h_depths)]:
        run = 0
        for c in atom_seq:
            if c == atom_type:
                run += 1
            else:
                if run > 0:
                    depth_counter[run] += 1
                run = 0
        if run > 0:
            depth_counter[run] += 1

    # Find hh+ tokens
    atom_str = ''.join(atom_seq)
    if 'hh' in atom_str:
        hh_tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'prefix': a.prefix,
            'atoms': '.'.join(at[0] for at in a.atoms),
            'gloss': '.'.join(at[2] for at in a.atoms),
        })

print('=== Stacking depth distribution ===\n')
for name, counter in [('e (cool)', e_depths), ('i (iterate)', i_depths), ('h (watch)', h_depths)]:
    total = sum(counter.values())
    print(f'{name}: {total} total runs')
    for depth in sorted(counter.keys()):
        pct = 100 * counter[depth] / total
        print(f'  depth {depth}: {counter[depth]:>5} ({pct:>5.1f}%)')
    print()

print(f'=== hh+ tokens ({len(hh_tokens)} total) ===\n')

# Group by folio
by_folio = defaultdict(list)
for tok in hh_tokens:
    by_folio[tok['folio']].append(tok)

print(f'Folios with hh+: {len(by_folio)}')
for folio in sorted(by_folio.keys()):
    toks = by_folio[folio]
    print(f'\n  {folio} ({len(toks)} tokens):')
    for tok in toks[:8]:
        pfx = tok["prefix"] or '?'
        print(f'    L{tok["line"]} {tok["word"]:<22s} [{pfx:<5s}] {tok["atoms"]:<20s} {tok["gloss"]}')
    if len(toks) > 8:
        print(f'    ... and {len(toks)-8} more')

# Prefix distribution of hh tokens
hh_prefixes = Counter(tok['prefix'] for tok in hh_tokens)
print(f'\nhh+ by prefix: {dict(hh_prefixes.most_common())}')

# What atom precedes hh?
pre_hh = Counter()
for tok in hh_tokens:
    atoms = tok['atoms'].split('.')
    for j in range(1, len(atoms)):
        if atoms[j] == 'h' and j > 0 and atoms[j-1] == 'h':
            if j >= 2:
                pre_hh[atoms[j-2]] += 1
            else:
                pre_hh['(start)'] += 1
print(f'Atom before hh: {dict(pre_hh.most_common())}')

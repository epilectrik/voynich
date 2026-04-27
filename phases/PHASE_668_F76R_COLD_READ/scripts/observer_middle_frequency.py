"""
How many of the 266 observer-exclusive MIDDLEs are frequent enough
to be a real vocabulary vs one-off compositional artifacts?

If there's a rich observation vocabulary, we expect:
- Dozens of MIDDLEs at 5+ occurrences
- Folio spread (not concentrated on 1-2 folios)
- Distribution differences between ch and sh
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

OBSERVE = {'ch', 'sh'}
OPERATE = {'qo', 'ok', 'ot', 'ol', 'or'}

obs_middles = Counter()
oper_middles = Counter()
other_middles = Counter()
obs_by_prefix = defaultdict(Counter)
obs_folio_spread = defaultdict(set)
obs_folio_counts = defaultdict(lambda: defaultdict(int))

for t in tx.currier_b():
    mid = morph.extract(t.word).middle
    if not mid:
        continue
    a = morph.atomize(t.word)
    pfx = a.prefix
    if pfx in OBSERVE:
        obs_middles[mid] += 1
        obs_by_prefix[pfx][mid] += 1
        obs_folio_spread[mid].add(t.folio)
        obs_folio_counts[mid][t.folio] += 1
    elif pfx in OPERATE:
        oper_middles[mid] += 1
    else:
        other_middles[mid] += 1

obs_only = set(obs_middles.keys()) - set(oper_middles.keys()) - set(other_middles.keys())

print(f'Total observer-exclusive MIDDLEs: {len(obs_only)}')
print(f'Total observer-exclusive tokens: {sum(obs_middles[m] for m in obs_only)}')

# Frequency distribution
freq_bins = Counter()
for mid in obs_only:
    n = obs_middles[mid]
    if n >= 20:
        freq_bins['20+'] += 1
    elif n >= 10:
        freq_bins['10-19'] += 1
    elif n >= 5:
        freq_bins['5-9'] += 1
    elif n >= 3:
        freq_bins['3-4'] += 1
    elif n == 2:
        freq_bins['2'] += 1
    else:
        freq_bins['1'] += 1

print(f'\nFrequency distribution:')
for bin_name in ['20+', '10-19', '5-9', '3-4', '2', '1']:
    print(f'  {bin_name:>6}: {freq_bins.get(bin_name, 0):>3} MIDDLEs')

# The real vocabulary: observer-exclusive MIDDLEs with 3+ occurrences
print(f'\n=== Observer-exclusive MIDDLEs, n >= 3 ===')
print(f'{"MIDDLE":<20} {"n":>4} {"ch":>4} {"sh":>4} {"folios":>6} {"atoms"}')
for mid in sorted(obs_only, key=lambda m: -obs_middles[m]):
    n = obs_middles[mid]
    if n < 3:
        break
    ch_n = obs_by_prefix['ch'].get(mid, 0)
    sh_n = obs_by_prefix['sh'].get(mid, 0)
    n_folios = len(obs_folio_spread[mid])
    a = morph.atomize('ch' + mid)
    atoms = '.'.join(at[2] for at in a.atoms)
    print(f'  {mid:<20} {n:>4} {ch_n:>4} {sh_n:>4} {n_folios:>6}  {atoms}')

# Compare: shared MIDDLEs (appear on both obs and oper) with 3+ on each
shared = set(obs_middles.keys()) & set(oper_middles.keys())
print(f'\n=== Top SHARED MIDDLEs (obs + oper) ===')
print(f'{"MIDDLE":<20} {"obs":>4} {"oper":>4} {"ch":>4} {"sh":>4}')
for mid in sorted(shared, key=lambda m: -(obs_middles[m] + oper_middles[m]))[:20]:
    obs_n = obs_middles[mid]
    op_n = oper_middles[mid]
    ch_n = obs_by_prefix['ch'].get(mid, 0)
    sh_n = obs_by_prefix['sh'].get(mid, 0)
    print(f'  {mid:<20} {obs_n:>4} {op_n:>4} {ch_n:>4} {sh_n:>4}')

# Check: what fraction of observer tokens use exclusive vs shared MIDDLEs?
exc_tokens = sum(obs_middles[m] for m in obs_only)
shared_tokens = sum(obs_middles[m] for m in shared)
total_obs = exc_tokens + shared_tokens + sum(obs_middles[m] for m in obs_middles if m not in obs_only and m not in shared)
print(f'\nObserver token breakdown:')
print(f'  Exclusive MIDDLEs: {exc_tokens} tokens ({100*exc_tokens/total_obs:.1f}%)')
print(f'  Shared MIDDLEs: {shared_tokens} tokens ({100*shared_tokens/total_obs:.1f}%)')

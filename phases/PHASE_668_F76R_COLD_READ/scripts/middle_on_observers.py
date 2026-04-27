"""
Check MIDDLE diversity on observation-channel (ch/sh) tokens vs
operation-channel (qo/ok/ot/ol) tokens. Are there MIDDLEs that
appear ONLY on observers? Those could encode sensory modalities.
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
OPERATE = {'qo', 'ok', 'ot', 'ol'}

def get_middle(word):
    m = morph.extract(word)
    return m.middle if m.middle else None

# Collect MIDDLEs by prefix class, for f76r and corpus-wide
for scope, token_iter in [('f76r', lambda: (t for t in tx.currier_b() if t.folio == 'f76r')),
                           ('corpus', lambda: tx.currier_b())]:
    obs_middles = Counter()
    oper_middles = Counter()
    other_middles = Counter()
    obs_by_prefix = defaultdict(Counter)

    for t in token_iter():
        mid = get_middle(t.word)
        if not mid:
            continue
        a = morph.atomize(t.word)
        pfx = a.prefix

        if pfx in OBSERVE:
            obs_middles[mid] += 1
            obs_by_prefix[pfx][mid] += 1
        elif pfx in OPERATE:
            oper_middles[mid] += 1
        else:
            other_middles[mid] += 1

    print(f'\n=== {scope}: MIDDLE distribution by channel ===')
    print(f'Observation tokens (ch/sh): {sum(obs_middles.values())} tokens, {len(obs_middles)} distinct MIDDLEs')
    print(f'Operation tokens (qo/ok/ot/ol): {sum(oper_middles.values())} tokens, {len(oper_middles)} distinct MIDDLEs')

    # MIDDLEs exclusive to observation channel
    obs_only = set(obs_middles.keys()) - set(oper_middles.keys()) - set(other_middles.keys())
    oper_only = set(oper_middles.keys()) - set(obs_middles.keys()) - set(other_middles.keys())
    shared = set(obs_middles.keys()) & set(oper_middles.keys())

    print(f'\nObserver-EXCLUSIVE MIDDLEs ({len(obs_only)}):')
    for mid in sorted(obs_only, key=lambda m: -obs_middles[m]):
        a_str = morph.atomize('ch' + mid)  # use ch to get atom parse
        atoms = '.'.join(at[2] for at in a_str.atoms)
        ch_n = obs_by_prefix['ch'].get(mid, 0)
        sh_n = obs_by_prefix['sh'].get(mid, 0)
        print(f'  {mid:<15s} ch={ch_n:>3} sh={sh_n:>3}  atoms={atoms}')

    print(f'\nOperator-EXCLUSIVE MIDDLEs ({len(oper_only)}):')
    for mid in sorted(oper_only, key=lambda m: -oper_middles[m])[:15]:
        print(f'  {mid:<15s} n={oper_middles[mid]}')

    print(f'\nShared MIDDLEs ({len(shared)}), top 15:')
    for mid in sorted(shared, key=lambda m: -(obs_middles[m] + oper_middles[m]))[:15]:
        ch_n = obs_by_prefix['ch'].get(mid, 0)
        sh_n = obs_by_prefix['sh'].get(mid, 0)
        op_n = oper_middles[mid]
        print(f'  {mid:<15s} ch={ch_n:>3} sh={sh_n:>3} oper={op_n:>3}')

    # ch vs sh: do they use different MIDDLEs?
    ch_only = set(obs_by_prefix['ch'].keys()) - set(obs_by_prefix['sh'].keys())
    sh_only = set(obs_by_prefix['sh'].keys()) - set(obs_by_prefix['ch'].keys())
    print(f'\nch-only MIDDLEs ({len(ch_only)}):')
    for mid in sorted(ch_only, key=lambda m: -obs_by_prefix['ch'][m])[:10]:
        print(f'  {mid:<15s} n={obs_by_prefix["ch"][mid]}')
    print(f'sh-only MIDDLEs ({len(sh_only)}):')
    for mid in sorted(sh_only, key=lambda m: -obs_by_prefix['sh'][m])[:10]:
        print(f'  {mid:<15s} n={obs_by_prefix["sh"][mid]}')

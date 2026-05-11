import json
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
d = json.loads((PROJECT_ROOT / 'phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json').read_text())
pairs = [(t['source'], t['target']) for t in d['transitions']]
print('N=', len(pairs))
for s, t in pairs:
    print(f'  {s:>8s} -> {t:<8s}')

#!/usr/bin/env python3
"""Extract the 17 forbidden bigram pairs and save to data/."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]

src = PROJECT_ROOT / 'phases' / 'FORBIDDEN_TRANSITION_THERMODYNAMICS' / 'results' / 'forbidden_transition_thermodynamics.json'
data = json.loads(src.read_text())


def find_pairs(o):
    if isinstance(o, list):
        if o and isinstance(o[0], dict) and 'source' in o[0] and 'target' in o[0]:
            return o
        for x in o:
            r = find_pairs(x)
            if r:
                return r
    elif isinstance(o, dict):
        for v in o.values():
            r = find_pairs(v)
            if r:
                return r
    return None


pairs = find_pairs(data)
out = []
for p in pairs:
    out.append({
        'source': p['source'],
        'target': p['target'],
    })

out_path = PHASE_DIR / 'data' / 'forbidden_pairs.json'
out_path.write_text(json.dumps(out, indent=2))
print(f"Wrote {len(out)} pairs to {out_path}")
for p in out:
    print(f"  {p['source']} -> {p['target']}")

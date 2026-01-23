"""Check token_to_middle values for unfilterable classes."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

d = json.load(open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))

print("token_to_middle for unfilterable class tokens:")
print()

for cls in [7, 9, 11, 21, 22, 41]:
    tokens = d['class_to_tokens'][str(cls)]
    print(f"Class {cls} tokens: {tokens}")
    for t in tokens:
        mid = d['token_to_middle'].get(t)
        print(f"  {repr(t):15} -> MIDDLE: {repr(mid)}")
    print()

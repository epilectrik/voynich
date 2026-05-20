import json, sys
from pathlib import Path
ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript

d = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc = d['token_to_class']
print(f"Class map has {len(ttc)} tokens across {len(set(ttc.values()))} classes")

tx = Transcript()
total = 0
classified = 0
unclass_examples = []
for t in tx.all(h_only=True):
    if not t.word.strip() or '*' in t.word: continue
    if t.language != 'B': continue
    if not (t.placement and t.placement.startswith('P')): continue
    total += 1
    if t.word.lower() in ttc:
        classified += 1
    elif len(unclass_examples) < 10:
        unclass_examples.append(t.word.lower())

print(f"Total Currier B P-placement tokens: {total}")
print(f"Classified: {classified} ({100*classified/total:.1f}%)")
print(f"Unclassified examples: {unclass_examples}")

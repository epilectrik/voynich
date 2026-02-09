"""Restore F-BRU-012 prep operation verbs that were overcorrected by Test 21.

Test 21 replaced ALL ch-compound prefix glosses with generic structural
decompositions. But pch/tch/fch had Brunschwig-grounded prep verbs:
  pch = "chop" (F-BRU-012: herb preparation by cutting)
  tch = "pound" (F-BRU-012: grinding/pounding materials)
  fch = "prepare" (F-BRU-012: general preparation)

These are COMPATIBLE with C929 (ch = active interaction with material).
Chopping, pounding, and preparing ARE active material interactions.
The generic "prep-test" etc. lost semantic content without adding precision.

kch was "precision heat" which is also more descriptive than "heat-test".
dch, rch, sch were already structural ("divide-check" etc.) so "divide-test"
is fine.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Morphology

morph = Morphology()
td_path = Path('data/token_dictionary.json')
td = json.load(open(td_path, encoding='utf-8'))

# Restore these prefix verbs
RESTORE = {
    'pch': ('prep-test', 'chop'),
    'tch': ('transfer-test', 'pound'),
    'fch': ('final-test', 'prepare'),
    'kch': ('heat-test', 'precision-heat'),
}

changes = []
for token_key, entry in td['tokens'].items():
    gloss = entry.get('gloss')
    if not gloss:
        continue

    m = morph.extract(token_key)
    prefix = m.prefix or ''

    if prefix in RESTORE:
        old_verb, new_verb = RESTORE[prefix]
        if gloss.startswith(old_verb + ' '):
            new_gloss = new_verb + ' ' + gloss[len(old_verb) + 1:]
            changes.append((token_key, prefix, gloss, new_gloss))
            entry['gloss'] = new_gloss
        elif gloss == old_verb:
            changes.append((token_key, prefix, gloss, new_verb))
            entry['gloss'] = new_verb

print("=" * 80)
print("RESTORE F-BRU-012 PREP VERBS")
print("=" * 80)
print(f"\n  Total restorations: {len(changes)}\n")

from collections import defaultdict
by_prefix = defaultdict(list)
for token, prefix, old, new in changes:
    by_prefix[prefix].append((token, old, new))

for prefix in sorted(by_prefix):
    items = by_prefix[prefix]
    old_verb, new_verb = RESTORE[prefix]
    print(f"  PREFIX '{prefix}': '{old_verb}' -> '{new_verb}' ({len(items)} tokens)")
    for token, old, new in items:
        print(f"    {token:<25} '{old}' -> '{new}'")
    print()

with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)
print(f"  Saved to {td_path}")

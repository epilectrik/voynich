"""Fix redundant glosses created by vocabulary shift collisions.

After script 14, some token glosses have patterns like:
  - "sustain sustained heat" (double sustain)
  - "apply seal" (ok prefix+middle confusion)

These need targeted cleanup.
"""
import json, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Morphology

morph = Morphology()
td_path = 'data/token_dictionary.json'
td = json.load(open(td_path, encoding='utf-8'))

count = 0
changes = []

for tok, entry in td['tokens'].items():
    gloss = entry.get('gloss')
    if not gloss:
        continue

    new_gloss = gloss

    # --- "sustain sustained heat" -> "sustained heat" ---
    new_gloss = new_gloss.replace('sustain sustained heat', 'sustained heat')

    # --- "apply seal" -> "seal" (ok as middle, not prefix action) ---
    m = morph.extract(tok)
    if m.middle == 'ok' and 'apply seal' in new_gloss:
        new_gloss = new_gloss.replace('apply seal', 'seal')

    if new_gloss != gloss:
        entry['gloss'] = new_gloss
        count += 1
        changes.append((tok, gloss, new_gloss))

with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)

print(f"Fixed {count} redundant glosses\n")
for tok, old, new in sorted(changes, key=lambda x: x[0]):
    print(f"  {tok:<22} {old:<40} -> {new}")

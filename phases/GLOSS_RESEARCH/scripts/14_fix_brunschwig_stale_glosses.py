"""Fix token glosses that use pre-Brunschwig vocabulary.

After Test 12-13, middle dictionary was updated with Brunschwig-derived
refinements. Manual token glosses still use old vocabulary:
  - "gentle heat" -> "sustained heat" (ke middle)
  - "deep cool" -> "extended cool" (ee/eey/eeo/eee middles)
  - "lock" -> "seal" (ok middle)
  - "hard heat" -> "direct heat" (ck middle)
  - "cool-off" -> "standing cool" (eod middle)
  - "sustain-lock" -> "sustain seal" (olk middle)
  - "cool, open" -> "cool-open" (eo middle, hyphenation fix)
  - "energy lock" -> "seal" (ok compound forms)
"""
import json, sys
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

    m = morph.extract(tok)
    mid = m.middle or ''
    new_gloss = gloss

    # --- ke middle: "gentle heat" -> "sustained heat" ---
    if 'ke' in mid:
        new_gloss = new_gloss.replace('gentle heat', 'sustained heat')

    # --- ee/eey/eeo/eee middles: "deep cool" -> "extended cool" ---
    if mid.startswith('ee') or mid in ('eey', 'eeo', 'eee', 'eeeo', 'eeol'):
        new_gloss = new_gloss.replace('deep cool', 'extended cool')
        new_gloss = new_gloss.replace('deep settling', 'extended cool')

    # --- ok middle: "lock" -> "seal" ---
    # Be careful: only when ok is the middle, not when "lock" appears in other contexts
    if mid in ('ok', 'olk', 'okch', 'oksh', 'eok'):
        new_gloss = new_gloss.replace('lock,', 'seal,')
        new_gloss = new_gloss.replace('lock.', 'seal.')
        new_gloss = new_gloss.replace('lock ', 'seal ')

    # --- ck middle: "hard heat" -> "direct heat" ---
    if 'ck' in mid and 'hard heat' in new_gloss:
        new_gloss = new_gloss.replace('hard heat', 'direct heat')

    # --- eod middle: "cool-off" -> "standing cool" ---
    if mid in ('eod', 'eody'):
        new_gloss = new_gloss.replace('cool-off', 'standing cool')
        new_gloss = new_gloss.replace('cool off', 'standing cool')

    # --- eo middle: hyphenation "cool, open" -> "cool-open" ---
    # Only when eo IS the middle (not when "cool" and "open" are separate morphemes)
    if mid == 'eo' and 'cool, open' in new_gloss:
        new_gloss = new_gloss.replace('cool, open', 'cool-open')

    # --- olk middle: "sustain-lock" -> "sustain seal" ---
    if mid == 'olk':
        new_gloss = new_gloss.replace('sustain-lock', 'sustain seal')
        new_gloss = new_gloss.replace('sustain lock', 'sustain seal')

    # --- energy lock -> seal (ok in compound forms) ---
    if 'ok' in mid and 'energy lock' in new_gloss:
        new_gloss = new_gloss.replace('energy lock', 'seal')

    if new_gloss != gloss:
        entry['gloss'] = new_gloss
        count += 1
        changes.append((tok, mid, gloss, new_gloss))

# Update metadata
td['meta']['schema_notes'] = td['meta'].get('schema_notes', '')
glossed = sum(1 for e in td['tokens'].values() if e.get('gloss'))
td['meta']['glossed'] = glossed

with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)

print(f"Updated {count} token glosses\n")
print(f"{'Token':<22} {'Middle':<10} {'Old':<38} {'New':<38}")
print(f"{'-'*22} {'-'*10} {'-'*38} {'-'*38}")
for tok, mid, old, new in sorted(changes, key=lambda x: x[0]):
    print(f"{tok:<22} {mid:<10} {old:<38} {new:<38}")

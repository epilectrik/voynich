"""Fix token glosses that still use old vocabulary after the shift.

Targets:
  - "release" -> "set" (for -ey middle tokens)
  - "settling" -> "cool" (for e-family tokens)
  - "monitor" -> "check" (for ch-middle tokens)
  - "deep settling" -> "deep cool"
  - misc stale forms
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

    m = morph.extract(tok)
    new_gloss = gloss

    # --- ey middle: "release" -> "set" ---
    # Only for tokens whose MIDDLE is 'ey' (not suffix=ey which we already fixed)
    if m.middle == 'ey' or (m.middle and m.middle.endswith('ey') and 'release' in gloss):
        new_gloss = new_gloss.replace(', release.', ', set.')
        new_gloss = new_gloss.replace(' release.', ' set.')
        new_gloss = new_gloss.replace(', release,', ', set,')
        new_gloss = new_gloss.replace(' release,', ' set,')
        new_gloss = new_gloss.replace(' release ', ' set ')

    # --- e-family: "settling" -> "cool" ---
    # Compound forms first
    new_gloss = new_gloss.replace('deep settling', 'deep cool')
    new_gloss = new_gloss.replace('settling', 'cool')

    # --- ch middle: "monitor" -> "check" ---
    # Be careful not to double-check: "check, monitor" -> "check, check" is wrong
    # Only replace "monitor" when it's the ch-middle meaning, not the prefix
    if m.middle in ('ch', 'ckh', 'eck', 'eckh', 'kch', 'okch', 'olch'):
        # Replace standalone "monitor" but not when preceded by "check,"
        # (which would mean prefix=ch already contributed "check")
        if ', monitor' in new_gloss and not new_gloss.startswith('check, monitor'):
            new_gloss = new_gloss.replace(', monitor', ', check')
        elif new_gloss.startswith('monitor'):
            new_gloss = new_gloss.replace('monitor', 'check', 1)
        # "heat, monitor" -> "heat, check" (for ckh middle with ch prefix)
        if 'heat, monitor' in new_gloss:
            new_gloss = new_gloss.replace('heat, monitor', 'heat, check')

    # --- "mass" -> "precision marker" for m middle ---
    if m.middle == 'm' and 'mass' in new_gloss:
        new_gloss = new_gloss.replace('mass', 'precision marker')

    # --- specific fixes for known stale patterns ---
    # "check, release." for chey (middle=ey, prefix=ch)
    # Already handled above

    if new_gloss != gloss:
        entry['gloss'] = new_gloss
        count += 1
        changes.append((tok, gloss, new_gloss))

with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)

print(f"Updated {count} token glosses\n")
print(f"{'Token':<22} {'Old':<38} {'New':<38}")
print(f"{'-----':<22} {'---':<38} {'---':<38}")
for tok, old, new in sorted(changes, key=lambda x: x[0]):
    print(f"{tok:<22} {old:<38} {new:<38}")

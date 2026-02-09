"""Fix middle dictionary vocabulary to match the 2026-02-06 vocabulary shift."""
import json, re
from pathlib import Path

md_path = Path('data/middle_dictionary.json')
md = json.load(open(md_path, encoding='utf-8'))

count = 0
changes = []

for mid, entry in md['middles'].items():
    gloss = entry.get('gloss')
    if not gloss:
        continue

    new_gloss = gloss

    # Compound forms first, then simple
    new_gloss = new_gloss.replace('deep equilibrate', 'deep cool')
    new_gloss = new_gloss.replace('deep settle', 'deep cool')
    new_gloss = new_gloss.replace('settle open', 'cool, open')
    new_gloss = new_gloss.replace('settle off', 'cool off')
    new_gloss = new_gloss.replace('settle sequence', 'cool sequence')
    new_gloss = new_gloss.replace('settle end', 'cool end')
    new_gloss = new_gloss.replace('settle-cut', 'cool-cut')
    new_gloss = re.sub(r'\bsettle\b', 'cool', new_gloss)
    new_gloss = re.sub(r'\blet settle\b', 'let cool', new_gloss)  # already caught above
    new_gloss = re.sub(r'\blet cool\b', 'let cool', new_gloss)
    new_gloss = re.sub(r'\boperate\b', 'work', new_gloss)
    new_gloss = re.sub(r'\boutput\b', 'collect', new_gloss)
    new_gloss = re.sub(r'\bcheckpoint\b', 'check', new_gloss)
    new_gloss = re.sub(r'\bmonitor\b', 'check', new_gloss)

    # Special cases
    if mid == 'e':
        new_gloss = 'let cool'
    elif mid == 'ey':
        new_gloss = 'set'  # from GLOSS_RESEARCH Test 02
    elif mid == 'm':
        new_gloss = 'precision marker'  # C912, expert corrected

    if new_gloss != gloss:
        entry['gloss'] = new_gloss
        count += 1
        changes.append((mid, gloss, new_gloss))

# Update metadata
md['meta']['vocabulary_shift'] = 'Synced with token dictionary vocabulary (2026-02-06)'

with open(md_path, 'w', encoding='utf-8') as f:
    json.dump(md, f, indent=2, ensure_ascii=False)

print(f"Updated {count} middle glosses\n")
print(f"{'Middle':<14} {'Old':<25} {'New':<25}")
print(f"{'------':<14} {'---':<25} {'---':<25}")
for mid, old, new in sorted(changes, key=lambda x: x[0]):
    print(f"{mid:<14} {old:<25} {new:<25}")

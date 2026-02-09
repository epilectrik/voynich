"""Regloss middle 'edy' from 'standard' to 'batch'.

The 'standard' problem: edy is the most universal middle (1,763 tokens,
82/83 folios, 5% of all B tokens). Every prefix takes it. It was glossed
as 'standard' which is semantically empty.

Analysis (scratchpad/standard_problem.py + edy_*.py) showed:
  - edy is NOT a misparse of ed+y or e+dy (prep prefix test: pchedy/tchedy)
  - edy has no kernel (unique among common middles)
  - edy sits in heat-check-heat cycles (26.9% followed by heat)
  - Folio-level correlation with e and ed is near zero (r~0.13)
  - edy functions as the default object: 'the batch' / 'the work'

New gloss: 'batch' (the material being processed)
  shedy = 'monitor batch.'  (was: 'monitor standard.')
  chedy = 'test batch.'     (was: 'test standard.')
  pchedy = 'chop batch.'    (was: 'chop standard.')
  okedy = 'lock batch.'     (was: 'lock standard.')

Task 1: Update middle_dictionary.json
Task 2: Update all token glosses containing 'standard' from edy middle
"""
import json, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

morph = Morphology()
tx = Transcript()

md_path = Path('data/middle_dictionary.json')
td_path = Path('data/token_dictionary.json')
dm_path = Path('data/decoder_maps.json')

md = json.load(open(md_path, encoding='utf-8'))
td = json.load(open(td_path, encoding='utf-8'))
dm = json.load(open(dm_path, encoding='utf-8'))

# ============================================================
# TASK 1: Update middle_dictionary.json
# ============================================================

print("=" * 85)
print("TASK 1: UPDATE MIDDLE DICTIONARY")
print("=" * 85)

old_gloss = md['middles']['edy']['gloss']
md['middles']['edy']['gloss'] = 'batch'
print(f"\n  middle 'edy': '{old_gloss}' -> 'batch'")

with open(md_path, 'w', encoding='utf-8') as f:
    json.dump(md, f, indent=2, ensure_ascii=False)
print(f"  Saved to {md_path}")

# ============================================================
# TASK 2: Update token glosses
# ============================================================

print(f"\n{'='*85}")
print("TASK 2: UPDATE TOKEN GLOSSES")
print(f"{'='*85}")

# Load suffix punctuation from decoder_maps
SUFFIX_PUNCT = {}
for sfx_key, sfx_info in dm['maps']['suffix_gloss']['entries'].items():
    SUFFIX_PUNCT[sfx_key] = sfx_info['value']
SUFFIX_PUNCT.setdefault('(none)', ',')
SUFFIX_PUNCT.setdefault('', ',')

PREFIX_VERBS = {
    'ch': 'test', 'sh': 'monitor', 'qo': 'energy',
    'ol': 'continue', 'da': 'setup', 'ok': 'lock',
    'ot': 'scaffold', 'ct': 'control',
    'pch': 'chop', 'tch': 'pound', 'kch': 'precision-heat', 'fch': 'prepare',
    'lk': 'link-energy', 'lch': 'link-test', 'lsh': 'link-monitor',
    'ke': 'sustain', 'te': 'gather', 'se': 'scaffold-sustain',
    'de': 'divide-sustain', 'pe': 'start',
    'so': 'scaffold-work', 'po': 'pre-work', 'do': 'mark-work', 'ko': 'heat-work',
    'to': 'transfer-work',
    'ta': 'transfer-input', 'ka': 'heat-anchor', 'sa': 'scaffold-anchor',
    'dch': 'divide-test', 'rch': 'input-test', 'sch': 'scaffold-test',
    'yk': 'y-heat', 'or': 'portion-work', 'al': 'transfer-frame',
}

# Find all tokens with middle=edy
changes = []
for token_key, entry in td['tokens'].items():
    m = morph.extract(token_key)
    if m.middle != 'edy':
        continue

    old_gloss = entry.get('gloss', '')

    # Compose new gloss
    pfx_verb = PREFIX_VERBS.get(m.prefix, '')
    sfx = m.suffix or ''
    sfx_punct = SUFFIX_PUNCT.get(sfx, ',')

    if pfx_verb:
        new_gloss = f"{pfx_verb} batch{sfx_punct}"
    else:
        new_gloss = f"batch{sfx_punct}"
    new_gloss = new_gloss.strip()

    if old_gloss != new_gloss:
        changes.append((token_key, m.prefix or '-', old_gloss, new_gloss))
        entry['gloss'] = new_gloss

print(f"\n  Tokens updated: {len(changes)}")

# Show by prefix
from collections import defaultdict
by_prefix = defaultdict(list)
for token, pfx, old, new in changes:
    by_prefix[pfx].append((token, old, new))

for pfx in sorted(by_prefix, key=lambda p: -len(by_prefix[p])):
    items = by_prefix[pfx]
    print(f"\n  PREFIX '{pfx}' ({len(items)} tokens):")
    for token, old, new in items[:5]:
        print(f"    {token:<25} '{old}' -> '{new}'")
    if len(items) > 5:
        print(f"    ... and {len(items) - 5} more")

# Save
with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)
print(f"\n  Saved to {td_path}")

# ============================================================
# SUMMARY
# ============================================================

print(f"\n{'='*85}")
print("SUMMARY")
print(f"{'='*85}")

# Count B token coverage
b_tokens = Counter()
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    b_tokens[token.word] += 1

total = 0
glossed = 0
for token_word, count in b_tokens.items():
    total += count
    entry = td['tokens'].get(token_word, {})
    if entry.get('gloss'):
        glossed += count

print(f"\n  Middle 'edy': 'standard' -> 'batch'")
print(f"  Token glosses updated: {len(changes)}")
print(f"  Token coverage: {glossed}/{total} = {glossed/total*100:.1f}%")
print(f"\n  Key transformations:")
print(f"    shedy:   'monitor standard.' -> 'monitor batch.'")
print(f"    chedy:   'test standard.'    -> 'test batch.'")
print(f"    otedy:   'scaffold standard.'-> 'scaffold batch.'")
print(f"    okedy:   'lock standard.'    -> 'lock batch.'")
print(f"    pchedy:  'chop standard.'    -> 'chop batch.'")
print(f"    tchedy:  'pound standard.'   -> 'pound batch.'")
print(f"    lchedy:  'link-test standard.' -> 'link-test batch.'")

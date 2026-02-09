"""Full gloss refresh: suffix glosses + auto-composition + stale fix.

Task 1: Gloss 5 remaining suffixes (-eey, -ry, -eol, -om, -im)
Task 2: Auto-compose all unglossed tokens with glossed middles
Task 3: Fix stale prefix vocabulary in existing glosses

Uses decoder_maps.json suffix_gloss for punctuation mapping.
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

md_path = Path('data/middle_dictionary.json')
td_path = Path('data/token_dictionary.json')
dm_path = Path('data/decoder_maps.json')

md = json.load(open(md_path, encoding='utf-8'))
td = json.load(open(td_path, encoding='utf-8'))
dm = json.load(open(dm_path, encoding='utf-8'))

# ============================================================
# SUFFIX PUNCTUATION from decoder_maps
# ============================================================

SUFFIX_PUNCT = {}
for sfx_key, sfx_info in dm['maps']['suffix_gloss']['entries'].items():
    SUFFIX_PUNCT[sfx_key] = sfx_info['value']

# Fill in any missing common ones
SUFFIX_PUNCT.setdefault('(none)', ',')
SUFFIX_PUNCT.setdefault('', ',')

# ============================================================
# SUFFIX GLOSSES for GLOSSING.md
# These are the semantic meanings (separate from punctuation)
# ============================================================

SUFFIX_GLOSSES = {
    '(none)': '(bare)',
    'y': 'done', 'dy': 'close', 'hy': 'verify/maintain',
    'ey': 'set', 'ly': 'settled', 'am': 'finalize',
    'aiin': 'check', 'ain': 'check', 'al': 'complete',
    'ar': 'close', 'or': 'portion', 's': 'next/boundary',
    'edy': 'thorough', 'r': 'input', 'iin': 'iterate',
    'ol': 'continue', 'l': 'frame', 'd': 'mark',
    # NEW glosses for Task 1:
    'eey': 'extended',        # double-e = duration, -y = done. R1 peak, pos 0.416. Extended process completion.
    'ry': 'output',           # C839: OUTPUT marker. S-zone 3.18x. pos 0.748 (late).
    'eol': 'sustain',         # e + ol = cool + continue. R2 peak (1.51x), pos 0.380 (early). Sustain in balneum marie.
    'om': 'work-final',       # o + m. R3 peak (1.49x), pos 0.926 (line-final). Work completion.
    'im': 'iterate-final',    # i + m. R2 peak (2.60x!), pos 0.876 (line-final). Iteration completion in balneum marie.
}

# ============================================================
# PREFIX VERBS (current vocabulary after C929)
# ============================================================

PREFIX_VERBS = {
    'ch': 'test', 'sh': 'monitor', 'qo': 'energy',
    'ol': 'continue', 'da': 'setup', 'ok': 'lock',
    'ot': 'scaffold', 'ct': 'control',
    # F-BRU-012 prep operations (restored by Test 22)
    'pch': 'chop', 'tch': 'pound', 'kch': 'precision-heat', 'fch': 'prepare',
    # L-compounds
    'lk': 'link-energy', 'lch': 'link-test', 'lsh': 'link-monitor',
    # Compound [C]+e prefixes
    'ke': 'sustain', 'te': 'gather', 'se': 'scaffold-sustain',
    'de': 'divide-sustain', 'pe': 'start',
    # Compound [C]+o prefixes
    'so': 'scaffold-work', 'po': 'pre-work', 'do': 'mark-work', 'ko': 'heat-work',
    'to': 'transfer-work',
    # Compound [C]+a prefixes
    'ta': 'transfer-input', 'ka': 'heat-anchor', 'sa': 'scaffold-anchor',
    # Compound [C]+ch prefixes (C929: ch=physical contact)
    'dch': 'divide-test', 'rch': 'input-test', 'sch': 'scaffold-test',
    # Other known
    'yk': 'y-heat', 'or': 'portion-work', 'al': 'transfer-frame',
}

# Old prefix verbs to fix (Task 3)
OLD_PREFIX_VERBS = {
    'ch': ['check'],
    'sh': ['observe'],
}

# ============================================================
# TASK 1: Update suffix glosses in GLOSSING.md context
# (just report — actual GLOSSING.md update is manual)
# ============================================================

print("=" * 85)
print("TASK 1: NEW SUFFIX GLOSSES")
print("=" * 85)
print(f"""
  New suffix assignments:
    -eey  = 'extended'       (double-e duration + -y done. R1 peak, pos 0.416)
    -ry   = 'output'         (C839 OUTPUT marker. S-zone 3.18x, pos 0.748)
    -eol  = 'sustain'        (e-cool + ol-continue. R2 1.51x, pos 0.380)
    -om   = 'work-final'     (o-work + m-final. R3 1.49x, pos 0.926)
    -im   = 'iterate-final'  (i-iterate + m-final. R2 2.60x, pos 0.876)
""")

# ============================================================
# TASK 2: Auto-compose unglossed tokens
# ============================================================

print("=" * 85)
print("TASK 2: AUTO-COMPOSE UNGLOSSED TOKENS")
print("=" * 85)

# Build set of B tokens
b_tokens = Counter()
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    b_tokens[token.word] += 1

composed = 0
skipped_no_middle_gloss = 0
skipped_no_middle = 0
already_glossed = 0
composition_examples = []

for token_word, count in b_tokens.most_common():
    entry = td['tokens'].get(token_word, {})

    # Skip if already glossed
    if entry.get('gloss'):
        already_glossed += 1
        continue

    # Parse morphology
    m = morph.extract(token_word)
    if not m.middle:
        skipped_no_middle += 1
        continue

    # Get middle gloss
    mid_info = md['middles'].get(m.middle, {})
    mid_gloss = mid_info.get('gloss')
    if not mid_gloss:
        skipped_no_middle_gloss += 1
        continue

    # Get prefix verb
    pfx_verb = PREFIX_VERBS.get(m.prefix, '')

    # Get suffix punctuation
    sfx = m.suffix or ''
    sfx_punct = SUFFIX_PUNCT.get(sfx, ',')

    # Compose gloss
    if pfx_verb:
        gloss = f"{pfx_verb} {mid_gloss}{sfx_punct}"
    else:
        gloss = f"{mid_gloss}{sfx_punct}"

    # Clean up double spaces, trailing commas
    gloss = gloss.strip()

    # Store
    if token_word not in td['tokens']:
        td['tokens'][token_word] = {}
    td['tokens'][token_word]['gloss'] = gloss
    composed += 1

    if len(composition_examples) < 20:
        composition_examples.append((token_word, m.prefix or '-', m.middle, sfx or '-', gloss))

print(f"\n  Already glossed: {already_glossed}")
print(f"  Newly composed: {composed}")
print(f"  Skipped (no middle): {skipped_no_middle}")
print(f"  Skipped (middle unglossed): {skipped_no_middle_gloss}")

print(f"\n  Examples:")
print(f"  {'Token':<25} {'Prefix':<8} {'Middle':<12} {'Suffix':<8} {'Gloss'}")
print(f"  {'-'*25} {'-'*8} {'-'*12} {'-'*8} {'-'*40}")
for token, pfx, mid, sfx, gloss in composition_examples:
    print(f"  {token:<25} {pfx:<8} {mid:<12} {sfx:<8} {gloss}")

# ============================================================
# TASK 3: Fix stale prefix vocabulary in existing glosses
# ============================================================

print(f"\n{'='*85}")
print(f"TASK 3: FIX STALE PREFIX VOCABULARY")
print(f"{'='*85}")

stale_fixes = []
for token_word, entry in td['tokens'].items():
    gloss = entry.get('gloss', '')
    if not gloss:
        continue

    m = morph.extract(token_word)
    prefix = m.prefix or ''

    # Check for old vocabulary
    if prefix in OLD_PREFIX_VERBS:
        for old_verb in OLD_PREFIX_VERBS[prefix]:
            new_verb = PREFIX_VERBS[prefix]
            if gloss.startswith(old_verb + ' '):
                new_gloss = new_verb + ' ' + gloss[len(old_verb) + 1:]
                stale_fixes.append((token_word, prefix, gloss, new_gloss))
                entry['gloss'] = new_gloss
            elif gloss == old_verb:
                stale_fixes.append((token_word, prefix, gloss, new_verb))
                entry['gloss'] = new_verb

    # Also check for any prefix that has a current verb but the gloss
    # doesn't start with it (might be from pre-Test-18 era)
    # Only fix if the gloss starts with a known old verb pattern
    # Be conservative here to avoid breaking manually curated glosses

print(f"\n  Stale prefix fixes: {len(stale_fixes)}")
if stale_fixes:
    for token, pfx, old, new in stale_fixes[:15]:
        print(f"    {token:<25} '{old}' -> '{new}'")
    if len(stale_fixes) > 15:
        print(f"    ... and {len(stale_fixes) - 15} more")

# ============================================================
# SUMMARY & SAVE
# ============================================================

print(f"\n{'='*85}")
print(f"SUMMARY")
print(f"{'='*85}")

# Recount coverage
total = 0
glossed = 0
for token_word, count in b_tokens.items():
    total += count
    entry = td['tokens'].get(token_word, {})
    if entry.get('gloss'):
        glossed += count

print(f"\n  BEFORE: 15,669/23,096 = 67.8% token coverage")
print(f"  AFTER:  {glossed}/{total} = {glossed/total*100:.1f}% token coverage")
print(f"\n  Newly composed: {composed}")
print(f"  Stale fixes: {len(stale_fixes)}")
print(f"  New suffix glosses: 5 (-eey, -ry, -eol, -om, -im)")

# Save token dictionary
with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)
print(f"\n  Saved to {td_path}")

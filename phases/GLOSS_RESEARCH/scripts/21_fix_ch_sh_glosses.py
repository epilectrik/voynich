"""Fix token glosses to use C929 vocabulary: ch=test, sh=monitor.

Previous glosses used "check" for ch-prefix and "observe" for sh-prefix.
C929 establishes:
  ch = active state testing (discrete checkpoint)  -> "test"
  sh = passive process monitoring (continuous observation) -> "monitor"

Also updates compound prefixes:
  pch -> "prep-test" (was "prep-check" or "chop")
  tch -> "transfer-test" (was "transfer-check" or "pound")
  fch -> "final-test" (was "final-check" or "prepare")
  kch -> "heat-test" (was "precision heat")
  dch -> "divide-test" (was "divide-check")
  rch -> "input-test" (was "input-check")
  sch -> "scaffold-test" (was "scaffold-check")
  lch -> "link-test" (was L-compound check)
  lsh -> "link-monitor" (was L-compound observe)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Morphology

morph = Morphology()

td_path = Path('data/token_dictionary.json')
td = json.load(open(td_path, encoding='utf-8'))

# Prefix vocabulary mapping (old -> new)
PREFIX_UPDATES = {
    'ch': ('check', 'test'),
    'sh': ('observe', 'monitor'),
    'pch': ('chop', 'prep-test'),
    'tch': ('pound', 'transfer-test'),
    'fch': ('prepare', 'final-test'),
    'kch': ('precision heat', 'heat-test'),
    'dch': ('divide-check', 'divide-test'),
    'rch': ('input-check', 'input-test'),
    'sch': ('scaffold-check', 'scaffold-test'),
    'lch': ('link-check', 'link-test'),
    'lsh': ('link-observe', 'link-monitor'),
}

# Also handle compound forms where "check" or "observe" appears
# as the prefix verb in auto-composed glosses
WORD_REPLACEMENTS = [
    # ch prefix compounds: "check X" -> "test X"
    ('check ', 'test '),
    # sh prefix compounds: "observe X" -> "monitor X"
    ('observe ', 'monitor '),
    # Compound prefix forms
    ('chop ', 'prep-test '),
    ('pound ', 'transfer-test '),
    ('prepare ', 'final-test '),
    # Also fix any remaining "prep-check" etc from Test 18
    ('prep-check', 'prep-test'),
    ('transfer-check', 'transfer-test'),
    ('divide-check', 'divide-test'),
    ('input-check', 'input-test'),
    ('scaffold-check', 'scaffold-test'),
]

changes = []
skipped = []

for token_key, entry in td['tokens'].items():
    gloss = entry.get('gloss')
    if not gloss:
        continue

    original = gloss
    new_gloss = gloss

    # Get the prefix of this token
    m = morph.extract(token_key)
    prefix = m.prefix or ''

    # Strategy: only replace prefix-verb if the token actually has that prefix
    # This prevents false replacements (e.g., "check" in a middle gloss)

    if prefix in ('ch',) and new_gloss.startswith('check '):
        new_gloss = 'test ' + new_gloss[6:]
    elif prefix in ('ch',) and new_gloss == 'check':
        new_gloss = 'test'
    elif prefix in ('sh',) and new_gloss.startswith('observe '):
        new_gloss = 'monitor ' + new_gloss[8:]
    elif prefix in ('sh',) and new_gloss == 'observe':
        new_gloss = 'monitor'
    elif prefix in ('pch',):
        if new_gloss.startswith('chop '):
            new_gloss = 'prep-test ' + new_gloss[5:]
        elif new_gloss.startswith('prep-check '):
            new_gloss = 'prep-test ' + new_gloss[11:]
    elif prefix in ('tch',):
        if new_gloss.startswith('pound '):
            new_gloss = 'transfer-test ' + new_gloss[6:]
        elif new_gloss.startswith('transfer-check '):
            new_gloss = 'transfer-test ' + new_gloss[15:]
    elif prefix in ('fch',):
        if new_gloss.startswith('prepare '):
            new_gloss = 'final-test ' + new_gloss[8:]
        elif new_gloss.startswith('final-check '):
            new_gloss = 'final-test ' + new_gloss[12:]
    elif prefix in ('kch',):
        if new_gloss.startswith('precision heat '):
            new_gloss = 'heat-test ' + new_gloss[15:]
        elif new_gloss.startswith('heat-check '):
            new_gloss = 'heat-test ' + new_gloss[11:]
    elif prefix in ('dch',):
        if new_gloss.startswith('divide-check '):
            new_gloss = 'divide-test ' + new_gloss[13:]
    elif prefix in ('rch',):
        if new_gloss.startswith('input-check '):
            new_gloss = 'input-test ' + new_gloss[12:]
    elif prefix in ('sch',):
        if new_gloss.startswith('scaffold-check '):
            new_gloss = 'scaffold-test ' + new_gloss[15:]
    elif prefix in ('lch',):
        if new_gloss.startswith('link-check '):
            new_gloss = 'link-test ' + new_gloss[11:]
    elif prefix in ('lsh',):
        if new_gloss.startswith('link-observe '):
            new_gloss = 'link-monitor ' + new_gloss[13:]

    if new_gloss != original:
        changes.append((token_key, prefix, original, new_gloss))
        entry['gloss'] = new_gloss

# Report
print("=" * 85)
print("C929 TOKEN GLOSS UPDATE: ch=test, sh=monitor")
print("=" * 85)

# Group by prefix
from collections import Counter, defaultdict
by_prefix = defaultdict(list)
for token, prefix, old, new in changes:
    by_prefix[prefix].append((token, old, new))

print(f"\n  Total changes: {len(changes)}\n")

for prefix in sorted(by_prefix.keys()):
    items = by_prefix[prefix]
    print(f"  PREFIX '{prefix}' ({len(items)} tokens):")
    for token, old, new in items[:8]:
        print(f"    {token:<25} '{old}' -> '{new}'")
    if len(items) > 8:
        print(f"    ... and {len(items) - 8} more")
    print()

# Verify no "check " or "observe " remains in ch/sh tokens
remaining_issues = []
for token_key, entry in td['tokens'].items():
    gloss = entry.get('gloss', '')
    if not gloss:
        continue
    m = morph.extract(token_key)
    prefix = m.prefix or ''
    if prefix == 'ch' and 'check ' in gloss:
        remaining_issues.append((token_key, prefix, gloss))
    if prefix == 'sh' and 'observe ' in gloss:
        remaining_issues.append((token_key, prefix, gloss))

if remaining_issues:
    print(f"\n  WARNING: {len(remaining_issues)} tokens still have old vocabulary:")
    for token, prefix, gloss in remaining_issues[:10]:
        print(f"    {token}: '{gloss}'")
else:
    print(f"  No remaining 'check'/'observe' issues in ch/sh tokens.")

# Save
with open(td_path, 'w', encoding='utf-8') as f:
    json.dump(td, f, indent=2, ensure_ascii=False)
print(f"\n  Saved to {td_path}")
print(f"  {len(changes)} glosses updated.")

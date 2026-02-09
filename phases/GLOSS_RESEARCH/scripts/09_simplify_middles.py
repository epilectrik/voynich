"""Simplify middle glosses: strip prefix-verbs, keep bare operations.

Middle glosses should be PREFIX-independent so auto-composition works
for any prefix combination. Collapses are accepted where the middles
genuinely mean the same thing.

Accepted collapses:
  - "close": ar, dy, c (all mean close)
  - "check": aiin, ch (both mean check/verify)
  - "transfer": t, al (both mean transfer)
  - "deep cool": eey, ee (same operation, y is terminal marker)

Differentiated:
  - eeo = "deep cool, work" (not plain "deep cool" — has o component)
"""
import json
from pathlib import Path

md_path = Path('data/middle_dictionary.json')
md = json.load(open(md_path, encoding='utf-8'))

# Explicit mapping: middle -> new gloss
# Only change middles that need prefix-verb stripping or simplification
changes_map = {
    # Strip "apply" / "let" prefix-verbs
    'k': 'heat',               # was "apply heat"
    'e': 'cool',               # was "let cool"
    'ok': 'lock',              # was "apply lock"
    'ke': 'gentle heat',       # was "sustain gentle heat"
    'h': 'hazard',             # was "check hazards"

    # Hyphenate compounds for clarity
    'eo': 'cool-open',         # was "cool, open"
    'eod': 'cool-off',         # was "cool off"
    'eok': 'cool-down',        # was "cool down"
    'ck': 'hard heat',         # keep (no change needed)
    'ckh': 'heat-check',       # was "heat check" → hyphenate
    'kch': 'precision heat',   # was "precision heat pulse" → simplify
    'ek': 'precision',         # was "precision lock" → strip "lock"
    'eck': 'hard precision',   # was "hard lock" → reinterpret
    'eek': 'energy-lock',      # keep compound
    'eed': 'deep discharge',   # keep
    'ee': 'deep cool',         # keep
    'eey': 'deep cool',        # same as ee (collapse accepted)
    'eeo': 'deep cool, work',  # differentiated: has o component
    'opch': 'process',         # was "process check" → strip "check"
    'ly': 'cool-end',          # was "cool end" → hyphenate
    'ot': 'work-path',         # was "work path" → hyphenate
    'op': 'work-start',        # was "work start" → hyphenate
    'oiin': 'work-loop',       # was "work loop" → hyphenate
    'ko': 'heat-work',         # was "heat work" → hyphenate
    'kee': 'heat-cool',        # was "heat cool" → hyphenate
    'ked': 'heat-release',     # was "heat release" → hyphenate
    'keed': 'heat-discharge',  # was "heat discharge" → hyphenate
    'keeo': 'heat, deep cool', # was "heat deep cool" → clarify
    'ka': 'heat-attach',       # was "heat attach" → hyphenate
    'olk': 'sustain-lock',     # was "sustain lock" → hyphenate
    'lk': 'frame-lock',        # was "frame lock" → hyphenate
    'lo': 'frame-open',        # was "frame open" → hyphenate
    'et': 'energy-path',       # was "energy path" → hyphenate
    'ech': 'energy-check',     # was "energy check" → hyphenate
    'ect': 'energy-control',   # was "energy control" → hyphenate
    'eeol': 'deep sustain',    # keep
    'aii': 'open-wide',        # was "open double" → clearer
    'ry': 'collect-end',       # was "collect end" → hyphenate
    'es': 'cool-sequence',     # was "cool sequence" → hyphenate
    'ecth': 'cool-cut',        # keep
}

count = 0
log = []

for mid, new_gloss in changes_map.items():
    entry = md['middles'].get(mid)
    if not entry:
        continue
    old_gloss = entry.get('gloss', '')
    if old_gloss != new_gloss:
        entry['gloss'] = new_gloss
        count += 1
        n = entry.get('token_count', 0)
        log.append((mid, old_gloss, new_gloss, n))

md['meta']['gloss_simplification'] = 'Stripped prefix-verbs, bare operations only (2026-02-06)'
md['meta']['version'] = '1.4'

with open(md_path, 'w', encoding='utf-8') as f:
    json.dump(md, f, indent=2, ensure_ascii=False)

print(f"Updated {count} middle glosses\n")
print(f"{'Middle':<14} {'Old':<28} {'New':<28} {'Count':>6}")
print(f"{'-'*14} {'-'*28} {'-'*28} {'-'*6}")
for mid, old, new, n in sorted(log, key=lambda x: -x[3]):
    print(f"{mid:<14} {old:<28} {new:<28} {n:>6}")

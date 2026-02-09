"""Preview: what happens if we strip prefix-verbs from middle glosses?
Shows which middles would collapse to the same gloss."""
import json
from pathlib import Path
from collections import defaultdict

md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))
middles = md['middles']

# Proposed simplifications
# Rule: strip prefix-action verbs, keep the operation noun/state
proposed = {}
for mid, entry in middles.items():
    gloss = entry.get('gloss')
    if not gloss:
        continue

    new = gloss

    # Strip prefix-action verbs
    new = new.replace('apply heat', 'heat')
    new = new.replace('apply lock', 'lock')
    new = new.replace('let cool', 'cool')
    new = new.replace('sustain gentle heat', 'gentle heat')
    new = new.replace('sustain lock', 'sustain-lock')
    new = new.replace('heat work', 'heat-work')
    new = new.replace('heat attach', 'heat-attach')
    new = new.replace('heat check', 'heat-check')
    new = new.replace('heat operate', 'heat-work')
    new = new.replace('heat cool', 'heat-cool')
    new = new.replace('heat release', 'heat-release')
    new = new.replace('heat discharge', 'heat-discharge')
    new = new.replace('heat deep cool', 'heat + deep cool')
    new = new.replace('work start', 'work-start')
    new = new.replace('work path', 'work-path')
    new = new.replace('work loop', 'work-loop')
    new = new.replace('cool down', 'cool-down')
    new = new.replace('cool off', 'cool-off')
    new = new.replace('cool, open', 'cool-open')
    new = new.replace('cool sequence', 'cool-sequence')
    new = new.replace('cool end', 'cool-end')
    new = new.replace('cool-cut', 'cool-cut')
    new = new.replace('deep cool', 'deep-cool')
    new = new.replace('deep sustain', 'deep-sustain')
    new = new.replace('deep discharge', 'deep-discharge')
    new = new.replace('precision heat pulse', 'precision-heat')
    new = new.replace('precision lock', 'precision')
    new = new.replace('precision marker', 'precision-marker')
    new = new.replace('hard heat', 'hard-heat')
    new = new.replace('hard lock', 'hard-heat-lock')
    new = new.replace('energy path', 'energy-path')
    new = new.replace('energy lock', 'energy-lock')
    new = new.replace('energy check', 'energy-check')
    new = new.replace('energy control', 'energy-control')
    new = new.replace('process check', 'process')
    new = new.replace('frame lock', 'frame-lock')
    new = new.replace('frame open', 'frame-open')
    new = new.replace('open double', 'open-wide')
    new = new.replace('collect end', 'collect-end')
    new = new.replace('check hazards', 'hazard')
    new = new.replace('settle-cut', 'cool-cut')

    proposed[mid] = new

# Check for collapses
by_gloss = defaultdict(list)
for mid, gloss in proposed.items():
    count = middles[mid].get('token_count', 0)
    by_gloss[gloss].append((mid, count))

print(f"{'='*70}")
print(f"COLLAPSE CHECK: middles that would share the same gloss")
print(f"{'='*70}\n")

collapses = {g: mids for g, mids in by_gloss.items() if len(mids) > 1}
if collapses:
    for gloss, mids in sorted(collapses.items(), key=lambda x: -sum(m[1] for m in x[1])):
        total = sum(m[1] for m in mids)
        print(f"  '{gloss}' ({total} total tokens):")
        for mid, count in sorted(mids, key=lambda x: -x[1]):
            old = middles[mid]['gloss']
            print(f"    {mid:<14} n={count:>5}  was: '{old}'")
        print()
else:
    print("  No collapses!")

print(f"\n{'='*70}")
print(f"ALL PROPOSED CHANGES")
print(f"{'='*70}\n")
print(f"{'Middle':<14} {'Old':<28} {'New':<28} {'Count':>6}")
print(f"{'-'*14} {'-'*28} {'-'*28} {'-'*6}")
for mid in sorted(proposed.keys(), key=lambda m: -middles[m].get('token_count', 0)):
    old = middles[mid]['gloss']
    new = proposed[mid]
    count = middles[mid].get('token_count', 0)
    marker = ' ***' if old != new else ''
    print(f"{mid:<14} {old:<28} {new:<28} {count:>6}{marker}")

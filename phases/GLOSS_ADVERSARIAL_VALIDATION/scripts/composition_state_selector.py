#!/usr/bin/env python3
"""Exploratory: Does morphological composition systematically change
macro-state assignment?

If ar → FL_HAZ but aral → FL_SAFE, is this a general principle?
For every MIDDLE that appears both bare and with a PREFIX in the
49-class system, does the PREFIX change the token's macro state?

Tests whether composition is a general state-selection mechanism
across the entire grammar.
"""

import json
import sys
import functools
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── k=6 macro-state partition (C1010, Phase 328) ────────────────

STATE_PARTITION = {
    'AXM': {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm': {3,5,18,19,42,45},
    'FL_HAZ': {7,30},
    'FQ': {9,13,14,23},
    'CC': {10,11,12},
    'FL_SAFE': {38,40},
}

# Build class→state lookup
CLASS_TO_STATE = {}
for state, classes in STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

# ── Load data ────────────────────────────────────────────────────

print("Loading data...")

morph = Morphology()

with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
          encoding='utf-8') as f:
    cmap = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

print(f"  {len(token_to_class)} tokens mapped to classes")

# ── Extract morphology for each token ────────────────────────────

print("\nExtracting morphology...")

token_data = []
for token, cls in token_to_class.items():
    m = morph.extract(token)
    if not m or not m.middle:
        continue
    state = CLASS_TO_STATE.get(cls, 'UNKNOWN')
    token_data.append({
        'token': token,
        'class': cls,
        'state': state,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'has_prefix': m.prefix is not None,
    })

print(f"  {len(token_data)} tokens with morphology")

# ── Group by MIDDLE ──────────────────────────────────────────────

print("\nGrouping by MIDDLE...")

middle_groups = defaultdict(list)
for td in token_data:
    middle_groups[td['middle']].append(td)

# Find MIDDLEs that appear in multiple states
multi_state_middles = {}
for mid, tokens in middle_groups.items():
    states = set(td['state'] for td in tokens)
    if len(states) > 1:
        multi_state_middles[mid] = {
            'states': states,
            'tokens': tokens,
            'n_tokens': len(tokens),
        }

single_state_middles = {mid: tokens for mid, tokens in middle_groups.items()
                        if len(set(td['state'] for td in tokens)) == 1}

print(f"  {len(middle_groups)} unique MIDDLEs across all tokens")
print(f"  {len(multi_state_middles)} MIDDLEs span multiple macro states")
print(f"  {len(single_state_middles)} MIDDLEs confined to a single state")

# ── Analyze multi-state MIDDLEs ──────────────────────────────────

print("\n" + "=" * 70)
print("MIDDLEs THAT SPAN MULTIPLE MACRO STATES")
print("=" * 70)

# Sort by number of states spanned (most diverse first)
for mid, info in sorted(multi_state_middles.items(),
                        key=lambda x: (-len(x[1]['states']), -x[1]['n_tokens'])):
    states = info['states']
    tokens = info['tokens']
    print(f"\n  MIDDLE '{mid}' → {len(states)} states: {sorted(states)}")

    # Group tokens by state
    by_state = defaultdict(list)
    for td in tokens:
        by_state[td['state']].append(td)

    for state in sorted(by_state.keys()):
        toks = by_state[state]
        examples = [(td['token'], td['prefix'] or '—', td['class']) for td in toks[:5]]
        extra = f" +{len(toks)-5} more" if len(toks) > 5 else ""
        ex_str = ", ".join(f"{t}(pfx={p},c{c})" for t, p, c in examples)
        print(f"    {state:>10}: {len(toks):3d} tokens — {ex_str}{extra}")

# ── Analyze PREFIX-induced state changes ─────────────────────────

print("\n" + "=" * 70)
print("PREFIX-INDUCED STATE CHANGES")
print("=" * 70)
print("For MIDDLEs with both bare (no prefix) and prefixed forms:")

state_changes = []
no_changes = []

for mid, tokens in middle_groups.items():
    bare_tokens = [td for td in tokens if not td['has_prefix']]
    prefixed_tokens = [td for td in tokens if td['has_prefix']]

    if not bare_tokens or not prefixed_tokens:
        continue

    bare_states = set(td['state'] for td in bare_tokens)
    prefixed_states = set(td['state'] for td in prefixed_tokens)

    # Does PREFIX change the state?
    if bare_states != prefixed_states:
        state_changes.append({
            'middle': mid,
            'bare_states': bare_states,
            'prefixed_states': prefixed_states,
            'bare_tokens': bare_tokens,
            'prefixed_tokens': prefixed_tokens,
        })
    else:
        no_changes.append({
            'middle': mid,
            'states': bare_states,
            'bare_tokens': bare_tokens,
            'prefixed_tokens': prefixed_tokens,
        })

print(f"\n  MIDDLEs with both bare and prefixed forms: {len(state_changes) + len(no_changes)}")
print(f"  PREFIX changes state: {len(state_changes)}")
print(f"  PREFIX preserves state: {len(no_changes)}")
if state_changes or no_changes:
    rate = len(state_changes) / (len(state_changes) + len(no_changes))
    print(f"  State-change rate: {rate:.1%}")

print("\n  STATE-CHANGING MIDDLEs:")
for sc in sorted(state_changes, key=lambda x: x['middle']):
    mid = sc['middle']
    bare_st = sorted(sc['bare_states'])
    pfx_st = sorted(sc['prefixed_states'])
    bare_ex = [(td['token'], td['state']) for td in sc['bare_tokens'][:3]]
    pfx_ex = [(td['token'], td['prefix'], td['state']) for td in sc['prefixed_tokens'][:5]]
    print(f"\n    MIDDLE '{mid}':")
    print(f"      Bare  → {bare_st}: {', '.join(f'{t}→{s}' for t, s in bare_ex)}")
    print(f"      +Pfx  → {pfx_st}: {', '.join(f'{t}(pfx={p})→{s}' for t, p, s in pfx_ex)}")

# ── Specific PREFIX families as state selectors ──────────────────

print("\n" + "=" * 70)
print("PREFIX FAMILIES AS STATE SELECTORS")
print("=" * 70)
print("For each PREFIX: which states do its tokens land in?")

prefix_state_dist = defaultdict(Counter)
for td in token_data:
    pfx = td['prefix'] or '(bare)'
    prefix_state_dist[pfx][td['state']] += 1

# Sort by number of tokens
for pfx, state_counts in sorted(prefix_state_dist.items(),
                                  key=lambda x: -sum(x[1].values())):
    total = sum(state_counts.values())
    if total < 3:
        continue
    dominant = state_counts.most_common(1)[0]
    purity = dominant[1] / total
    states_str = ", ".join(f"{s}:{n}" for s, n in state_counts.most_common())
    n_states = len(state_counts)
    print(f"  {pfx:>6}: {total:4d} tokens → {n_states} state(s), "
          f"purity={purity:.1%} [{states_str}]")

# ── FL-specific analysis ─────────────────────────────────────────

print("\n" + "=" * 70)
print("FLOW-SPECIFIC: How does composition route FL tokens?")
print("=" * 70)

fl_middles = set()
for td in token_data:
    if td['state'] in ('FL_HAZ', 'FL_SAFE'):
        fl_middles.add(td['middle'])

print(f"\n  MIDDLEs appearing in FL states: {sorted(fl_middles)}")

for mid in sorted(fl_middles):
    tokens = middle_groups[mid]
    states = set(td['state'] for td in tokens)
    if len(states) > 1:
        by_state = defaultdict(list)
        for td in tokens:
            by_state[td['state']].append(td['token'])
        print(f"\n  MIDDLE '{mid}' spans: {sorted(states)}")
        for state in sorted(by_state.keys()):
            print(f"    {state:>10}: {by_state[state][:8]}")

# ── Summary statistics ───────────────────────────────────────────

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

total_middles = len(middle_groups)
multi_count = len(multi_state_middles)
print(f"  Total MIDDLEs: {total_middles}")
print(f"  Multi-state MIDDLEs: {multi_count} ({multi_count/total_middles:.1%})")
print(f"  PREFIX state-change rate: {len(state_changes)}/{len(state_changes)+len(no_changes)}"
      f" = {len(state_changes)/(len(state_changes)+len(no_changes)):.1%}" if (state_changes or no_changes) else "")

# State purity per MIDDLE
purities = []
for mid, tokens in middle_groups.items():
    if len(tokens) < 2:
        continue
    state_counts = Counter(td['state'] for td in tokens)
    dominant = state_counts.most_common(1)[0][1]
    purities.append(dominant / len(tokens))

import numpy as np
print(f"  Mean MIDDLE state purity: {np.mean(purities):.3f}")
print(f"  Median MIDDLE state purity: {np.median(purities):.3f}")
print(f"  MIDDLEs with 100% purity: {sum(1 for p in purities if p == 1.0)}/{len(purities)}")

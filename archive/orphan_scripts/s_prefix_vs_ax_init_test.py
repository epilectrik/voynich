#!/usr/bin/env python3
"""
Test: Is s-prefix special among AX_INIT tokens?

Expert question: Does the energy depletion pattern apply to ALL AX line-openers
or specifically to s-prefix?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    import json
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

# Build line data with positions
folio_lines = defaultdict(lambda: defaultdict(list))

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)

# Identify line-initial tokens and their prefixes
initial_tokens = []
non_initial_tokens = []

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        if not words:
            continue

        # First token is line-initial
        initial_word = words[0]
        initial_role = token_to_role.get(initial_word, 'UNKNOWN')
        initial_tokens.append({
            'word': initial_word,
            'prefix': initial_word[:2] if len(initial_word) >= 2 else initial_word,
            'role': initial_role,
            'line_words': words
        })

        # Rest are non-initial
        for word in words[1:]:
            non_initial_tokens.append({
                'word': word,
                'role': token_to_role.get(word, 'UNKNOWN'),
                'line_words': words
            })

print("="*70)
print("S-PREFIX vs OTHER AX LINE-OPENERS")
print("="*70)

# Group line-initial AUXILIARY tokens by prefix
ax_initials = [t for t in initial_tokens if t['role'] == 'AUXILIARY']

prefix_groups = defaultdict(list)
for t in ax_initials:
    prefix = t['prefix']
    prefix_groups[prefix].append(t)

print(f"\nTotal AX line-initial tokens: {len(ax_initials)}")
print(f"\nTop prefixes among AX line-openers:")

prefix_counts = [(p, len(tokens)) for p, tokens in prefix_groups.items()]
prefix_counts.sort(key=lambda x: -x[1])

for prefix, count in prefix_counts[:15]:
    print(f"  {prefix:<10} {count} tokens")

# For each major prefix group, compute energy content on their lines
print(f"\n{'='*70}")
print("ENERGY OPERATOR RATE BY AX PREFIX (on same line)")
print("="*70)

def compute_energy_rate(tokens):
    """Compute rate of ENERGY_OPERATOR on lines started by these tokens."""
    en_count = 0
    total_count = 0
    qo_count = 0

    for t in tokens:
        for word in t['line_words']:
            if word == t['word']:
                continue  # Skip the opener itself
            role = token_to_role.get(word, 'UNKNOWN')
            total_count += 1
            if role == 'ENERGY_OPERATOR':
                en_count += 1
            if word.startswith('qo'):
                qo_count += 1

    en_rate = en_count / total_count if total_count > 0 else 0
    qo_rate = qo_count / total_count if total_count > 0 else 0
    return en_rate, qo_rate, total_count

# Compare major AX prefixes
major_prefixes = [p for p, c in prefix_counts if c >= 10]

print(f"\n{'Prefix':<10} {'Count':<8} {'EN Rate':<12} {'qo Rate':<12}")
print("-"*45)

results = []
for prefix in major_prefixes:
    tokens = prefix_groups[prefix]
    en_rate, qo_rate, n = compute_energy_rate(tokens)
    results.append((prefix, len(tokens), en_rate, qo_rate))
    print(f"{prefix:<10} {len(tokens):<8} {100*en_rate:<12.1f} {100*qo_rate:<12.1f}")

# Baseline: all AX openers
all_ax_en, all_ax_qo, _ = compute_energy_rate(ax_initials)
print(f"\n{'ALL AX':<10} {len(ax_initials):<8} {100*all_ax_en:<12.1f} {100*all_ax_qo:<12.1f}")

# Compare to daiin (from C557: 47.1% ENERGY followers)
daiin_initials = [t for t in initial_tokens if t['word'] == 'daiin']
daiin_en, daiin_qo, _ = compute_energy_rate(daiin_initials)
print(f"{'daiin':<10} {len(daiin_initials):<8} {100*daiin_en:<12.1f} {100*daiin_qo:<12.1f}")

# S-prefix specifically
s_prefixes = ['sa', 'so', 'sr']  # Main s-prefix variants
s_tokens = [t for p in s_prefixes for t in prefix_groups.get(p, [])]
if s_tokens:
    s_en, s_qo, _ = compute_energy_rate(s_tokens)
    print(f"{'s-prefix':<10} {len(s_tokens):<8} {100*s_en:<12.1f} {100*s_qo:<12.1f}")

# Statistical comparison
print(f"\n{'='*70}")
print("IS S-PREFIX SPECIAL AMONG AX?")
print("="*70)

# Check if s-prefix has significantly different EN rate than other AX
other_ax = [t for t in ax_initials if t['prefix'] not in s_prefixes]
if s_tokens and other_ax:
    s_en_vals = []
    other_en_vals = []

    for t in s_tokens:
        line_en = sum(1 for w in t['line_words'][1:] if token_to_role.get(w) == 'ENERGY_OPERATOR')
        line_total = len(t['line_words']) - 1
        if line_total > 0:
            s_en_vals.append(line_en / line_total)

    for t in other_ax:
        line_en = sum(1 for w in t['line_words'][1:] if token_to_role.get(w) == 'ENERGY_OPERATOR')
        line_total = len(t['line_words']) - 1
        if line_total > 0:
            other_en_vals.append(line_en / line_total)

    from scipy import stats as scipy_stats
    u_stat, p_val = scipy_stats.mannwhitneyu(s_en_vals, other_en_vals, alternative='two-sided')

    print(f"\nS-prefix EN rate: {100*np.mean(s_en_vals):.1f}%")
    print(f"Other AX EN rate: {100*np.mean(other_en_vals):.1f}%")
    print(f"Mann-Whitney p = {p_val:.4f}")

    if p_val < 0.05:
        print("-> *S-prefix is SIGNIFICANTLY different from other AX openers!")
    else:
        print("-> S-prefix is similar to other AX openers (general AX pattern)")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print("""
If s-prefix shows similar EN rate to other AX openers:
-> Energy depletion is a GENERAL AX_INIT property
-> S-prefix is not special for apparatus

If s-prefix shows lower EN rate than other AX openers:
-> S-prefix is SPECIFICALLY energy-avoiding
-> Supports apparatus/setup hypothesis

Compare to daiin (CORE_CONTROL):
-> daiin triggers ENERGY (per C557)
-> If AX_INIT is energy-neutral and s-prefix is energy-depleted,
   then s-prefix is special even among line-openers
""")

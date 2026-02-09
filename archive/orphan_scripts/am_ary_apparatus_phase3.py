#!/usr/bin/env python3
"""
Phase 3: Key pattern deep-dive for -am/-ary apparatus.

From Phase 2 findings:
1. s-prefix (sain, saiin, sar, sor) follows -am/-ary on next line
2. daiin -> otam is a fixed pattern (4 occurrences)
3. Section S has 81.9% line-final rate (highest)

Questions:
1. Is s-prefix the "reset/setup" after collection?
2. Are there specific CONTROL -> APPARATUS pairings?
3. Does the -am/-ary variant correlate with section/process type?
4. Full cycle pattern: CONTROL -> ... -> APPARATUS -> s-prefix?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

AM_ARY_TOKENS = {'ary', 'am', 'otam', 'dam', 'daly', 'oly', 'oldy', 'ldy'}

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

print("="*70)
print("-AM/-ARY APPARATUS ANALYSIS - PHASE 3: CYCLE PATTERNS")
print("="*70)

# 1. S-PREFIX FOLLOWS APPARATUS
print(f"\n{'='*70}")
print("1. S-PREFIX FOLLOWS -AM/-ARY APPARATUS")
print("="*70)

# Find all line-final -am/-ary followed by new line
apparatus_cycles = []

for folio in folio_lines:
    lines_sorted = sorted(folio_lines[folio].keys())

    for idx, line in enumerate(lines_sorted):
        words = folio_lines[folio][line]
        if not words:
            continue

        last_word = words[-1]
        if last_word in AM_ARY_TOKENS:
            if idx + 1 < len(lines_sorted):
                next_line = lines_sorted[idx + 1]
                next_words = folio_lines[folio][next_line]
                if next_words:
                    next_first = next_words[0]
                    is_s_prefix = next_first.startswith('s') and len(next_first) > 1
                    is_gallows = next_first[0] in GALLOWS if next_first else False

                    apparatus_cycles.append({
                        'apparatus': last_word,
                        'next_first': next_first,
                        'is_s_prefix': is_s_prefix,
                        'is_gallows': is_gallows,
                        'folio': folio,
                        'section': folio_section.get(folio, '?')
                    })

total_cycles = len(apparatus_cycles)
s_prefix_follows = sum(1 for c in apparatus_cycles if c['is_s_prefix'])
gallows_follows = sum(1 for c in apparatus_cycles if c['is_gallows'])

print(f"\nTotal line-final -am/-ary with next line: {total_cycles}")
print(f"Followed by s-prefix: {s_prefix_follows} ({100*s_prefix_follows/total_cycles:.1f}%)")
print(f"Followed by gallows (new para): {gallows_follows} ({100*gallows_follows/total_cycles:.1f}%)")
print(f"Other followers: {total_cycles - s_prefix_follows - gallows_follows} ({100*(total_cycles - s_prefix_follows - gallows_follows)/total_cycles:.1f}%)")

# What s-prefix tokens specifically?
s_prefix_tokens = [c['next_first'] for c in apparatus_cycles if c['is_s_prefix']]
s_prefix_counts = Counter(s_prefix_tokens)
print(f"\nSpecific s-prefix tokens following apparatus:")
for tok, count in s_prefix_counts.most_common(10):
    role = token_to_role.get(tok, 'UNKNOWN')
    print(f"  {tok:<15} {count:<5} {role}")

# Compare: what follows NON-apparatus line-final tokens?
print(f"\n{'='*70}")
print("2. COMPARISON: WHAT FOLLOWS NON-APPARATUS LINE-FINAL TOKENS?")
print("="*70)

non_apparatus_cycles = []

for folio in folio_lines:
    lines_sorted = sorted(folio_lines[folio].keys())

    for idx, line in enumerate(lines_sorted):
        words = folio_lines[folio][line]
        if not words:
            continue

        last_word = words[-1]
        if last_word not in AM_ARY_TOKENS:  # NOT apparatus
            if idx + 1 < len(lines_sorted):
                next_line = lines_sorted[idx + 1]
                next_words = folio_lines[folio][next_line]
                if next_words:
                    next_first = next_words[0]
                    is_s_prefix = next_first.startswith('s') and len(next_first) > 1
                    is_gallows = next_first[0] in GALLOWS if next_first else False

                    non_apparatus_cycles.append({
                        'is_s_prefix': is_s_prefix,
                        'is_gallows': is_gallows,
                    })

non_total = len(non_apparatus_cycles)
non_s_prefix = sum(1 for c in non_apparatus_cycles if c['is_s_prefix'])
non_gallows = sum(1 for c in non_apparatus_cycles if c['is_gallows'])

print(f"\nNon-apparatus line-final tokens: {non_total}")
print(f"Followed by s-prefix: {non_s_prefix} ({100*non_s_prefix/non_total:.1f}%)")
print(f"Followed by gallows: {non_gallows} ({100*non_gallows/non_total:.1f}%)")

# Chi-square test
print(f"\nChi-square: s-prefix follows apparatus vs non-apparatus")
# Contingency: [s-prefix follows, doesn't follow] x [apparatus, non-apparatus]
observed = np.array([
    [s_prefix_follows, total_cycles - s_prefix_follows],  # apparatus
    [non_s_prefix, non_total - non_s_prefix]  # non-apparatus
])
chi2, p_val, dof, expected = scipy_stats.chi2_contingency(observed)
print(f"Chi-square = {chi2:.2f}, p = {p_val:.4f}")
if p_val < 0.05:
    ratio = (s_prefix_follows/total_cycles) / (non_s_prefix/non_total)
    print(f"-> *SIGNIFICANT: Apparatus is {ratio:.1f}x more likely to be followed by s-prefix")
else:
    print("-> Not significant")

# 3. CONTROL -> APPARATUS PAIRINGS
print(f"\n{'='*70}")
print("3. CONTROL -> APPARATUS PAIRINGS")
print("="*70)

# Find lines where CORE_CONTROL precedes apparatus (not necessarily adjacent)
control_apparatus_patterns = []

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        if len(words) < 2:
            continue

        # Find apparatus tokens
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS:
                # Look for CORE_CONTROL earlier in the line
                for j in range(i):
                    if token_to_role.get(words[j]) == 'CORE_CONTROL':
                        control_apparatus_patterns.append({
                            'control': words[j],
                            'apparatus': word,
                            'distance': i - j,
                            'intervening': words[j+1:i]
                        })

print(f"\nTotal CORE_CONTROL -> apparatus patterns: {len(control_apparatus_patterns)}")

# Group by control token
control_to_apparatus = defaultdict(Counter)
for p in control_apparatus_patterns:
    control_to_apparatus[p['control']][p['apparatus']] += 1

print(f"\nControl token preferences:")
for control in sorted(control_to_apparatus.keys()):
    targets = control_to_apparatus[control]
    total = sum(targets.values())
    if total >= 3:
        print(f"\n  {control} ({total} occurrences):")
        for apparatus, count in targets.most_common():
            pct = 100 * count / total
            print(f"    -> {apparatus:<12} {count} ({pct:.0f}%)")

# 4. APPARATUS BY VARIANT FUNCTION
print(f"\n{'='*70}")
print("4. APPARATUS VARIANT FUNCTION ANALYSIS")
print("="*70)

# Group by morphological class
am_class = {'am', 'dam', 'otam'}  # vessel
ary_class = {'ary'}  # collection point
y_class = {'oly', 'oldy', 'daly', 'ldy'}  # state

class_stats = {
    'VESSEL (-am)': {'tokens': am_class, 'predecessors': Counter(), 'followers_s': 0, 'total': 0},
    'COLLECT (-ary)': {'tokens': ary_class, 'predecessors': Counter(), 'followers_s': 0, 'total': 0},
    'STATE (-y)': {'tokens': y_class, 'predecessors': Counter(), 'followers_s': 0, 'total': 0},
}

for c in apparatus_cycles:
    for cls_name, cls_data in class_stats.items():
        if c['apparatus'] in cls_data['tokens']:
            cls_data['total'] += 1
            if c['is_s_prefix']:
                cls_data['followers_s'] += 1

# Add predecessor data
for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS and i > 0:
                pred = words[i-1]
                for cls_name, cls_data in class_stats.items():
                    if word in cls_data['tokens']:
                        cls_data['predecessors'][pred] += 1

print(f"\n{'Class':<20} {'Total':<8} {'s-prefix follows %':<20} {'Top predecessors':<30}")
print("-"*80)

for cls_name, cls_data in class_stats.items():
    total = cls_data['total']
    if total > 0:
        s_rate = 100 * cls_data['followers_s'] / total
        top_preds = ', '.join(f"{p}({c})" for p, c in cls_data['predecessors'].most_common(3))
        print(f"{cls_name:<20} {total:<8} {s_rate:<20.1f} {top_preds:<30}")

# 5. FULL CYCLE RECONSTRUCTION
print(f"\n{'='*70}")
print("5. FULL CYCLE PATTERN ANALYSIS")
print("="*70)

# Find complete cycles: s-prefix start -> ... -> apparatus end -> s-prefix start
complete_cycles = []

for folio in folio_lines:
    lines_sorted = sorted(folio_lines[folio].keys())

    current_cycle = None

    for idx, line in enumerate(lines_sorted):
        words = folio_lines[folio][line]
        if not words:
            continue

        first_word = words[0]
        last_word = words[-1]

        is_s_start = first_word.startswith('s') and len(first_word) > 1
        is_apparatus_end = last_word in AM_ARY_TOKENS

        # Start new cycle if s-prefix
        if is_s_start and current_cycle is None:
            current_cycle = {
                'start': first_word,
                'start_line': line,
                'lines': [line]
            }
        elif current_cycle is not None:
            current_cycle['lines'].append(line)

            # End cycle if apparatus-final AND next line is s-prefix
            if is_apparatus_end:
                if idx + 1 < len(lines_sorted):
                    next_line = lines_sorted[idx + 1]
                    next_words = folio_lines[folio][next_line]
                    if next_words and next_words[0].startswith('s') and len(next_words[0]) > 1:
                        current_cycle['end'] = last_word
                        current_cycle['end_line'] = line
                        current_cycle['length'] = len(current_cycle['lines'])
                        current_cycle['folio'] = folio
                        complete_cycles.append(current_cycle)
                        current_cycle = None

print(f"\nComplete s-prefix -> apparatus -> s-prefix cycles found: {len(complete_cycles)}")

if complete_cycles:
    lengths = [c['length'] for c in complete_cycles]
    print(f"Mean cycle length: {np.mean(lengths):.1f} lines")
    print(f"Median cycle length: {np.median(lengths):.1f} lines")
    print(f"Range: {min(lengths)} - {max(lengths)} lines")

    # Start-end pairs
    start_end_pairs = Counter((c['start'], c['end']) for c in complete_cycles)
    print(f"\nMost common start-end pairs:")
    for (start, end), count in start_end_pairs.most_common(10):
        print(f"  {start:<12} -> {end:<12} {count}")

# 6. SUMMARY
print(f"\n{'='*70}")
print("6. APPARATUS CYCLE MODEL")
print("="*70)

print(f"""
CYCLE STRUCTURE DISCOVERED:

1. S-PREFIX OPENER (setup/initialization)
   - sain, saiin, sar, sor
   - Role: AUXILIARY (cycle preparation)

2. PROCESSING SEQUENCE
   - ENERGY_OPERATOR, FREQUENT_OPERATOR
   - Kernel operations (h for phase, k for energy)

3. -AM/-ARY APPARATUS (collection/output)
   - VESSEL (-am): am, dam, otam - material containers
   - COLLECT (-ary): ary - collection points
   - STATE (-y): oly, oldy, daly, ldy - state markers

4. CYCLE REPEAT
   - s-prefix follows apparatus {100*s_prefix_follows/total_cycles:.1f}% of time
   - vs {100*non_s_prefix/non_total:.1f}% baseline

INTERPRETATION:
- Distillation apparatus cycle: heat -> collect -> reset
- s-prefix = "prepare/setup" (beginning of cycle)
- -am/-ary = "collect into/output to" (end of cycle)
- Cycle length varies by operation complexity
""")

# Save results
output = {
    's_prefix_follows_apparatus': s_prefix_follows,
    's_prefix_follows_non_apparatus': non_s_prefix,
    'apparatus_to_s_ratio': (s_prefix_follows/total_cycles) / (non_s_prefix/non_total) if non_s_prefix > 0 else 0,
    'chi_square_p': p_val,
    'complete_cycles_found': len(complete_cycles),
    'mean_cycle_length': float(np.mean(lengths)) if complete_cycles else 0,
}

output_path = Path(__file__).parent.parent / 'results' / 'am_ary_phase3.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

#!/usr/bin/env python3
"""
Phase 2: Deeper analysis of -am/-ary apparatus candidates.

From Phase 1:
- 72.7% line-final rate
- Lower kernel content than baseline
- Preceded by ENERGY_OPERATOR 27.3%
- Mean paragraph position 0.587

New questions:
1. What SPECIFIC tokens precede -am/-ary?
2. Morphological structure: what's the base before suffix?
3. REGIME correlation: do apparatus tokens cluster in specific regimes?
4. What follows on the NEXT line? (cycle continuation)
5. Fixed collocations (X + am/ary pairs)
6. Section-specific behavior differences
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Target tokens
AM_ARY_TOKENS = {'ary', 'am', 'otam', 'dam', 'daly', 'oly', 'oldy', 'ldy'}

# Build line and folio data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

# Load REGIME data if available
regime_path = Path(__file__).parent.parent / 'phases' / 'BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS' / 'results' / 'paragraph_kernel_analysis.json'
folio_regime = {}
if regime_path.exists():
    with open(regime_path) as f:
        regime_data = json.load(f)
    for entry in regime_data.get('paragraphs', []):
        folio = entry['folio']
        if folio not in folio_regime:
            folio_regime[folio] = entry.get('regime', 'UNKNOWN')

print("="*70)
print("-AM/-ARY APPARATUS ANALYSIS - PHASE 2")
print("="*70)

# 1. SPECIFIC PREDECESSOR ANALYSIS
print(f"\n{'='*70}")
print("1. SPECIFIC PREDECESSOR TOKENS")
print("="*70)

predecessor_pairs = []  # (predecessor, am_ary_token)

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS and i > 0:
                pred = words[i-1]
                predecessor_pairs.append({
                    'pred': pred,
                    'target': word,
                    'pred_role': token_to_role.get(pred, 'UNKNOWN'),
                    'folio': folio,
                    'section': folio_section.get(folio, '?')
                })

# Most common predecessors overall
pred_counts = Counter(p['pred'] for p in predecessor_pairs)
print(f"\nTop 20 tokens preceding -am/-ary:")
print(f"{'Token':<15} {'Count':<8} {'Role':<20} {'% of total':<10}")
print("-"*55)

total_preds = len(predecessor_pairs)
for pred, count in pred_counts.most_common(20):
    role = token_to_role.get(pred, 'UNKNOWN')
    pct = 100 * count / total_preds
    print(f"{pred:<15} {count:<8} {role:<20} {pct:<10.1f}")

# Predecessors by target token
print(f"\n{'='*70}")
print("2. PREDECESSORS BY -AM/-ARY VARIANT")
print("="*70)

for target in sorted(AM_ARY_TOKENS):
    target_pairs = [p for p in predecessor_pairs if p['target'] == target]
    if len(target_pairs) < 5:
        continue

    print(f"\n'{target}' ({len(target_pairs)} occurrences):")
    target_preds = Counter(p['pred'] for p in target_pairs)
    for pred, count in target_preds.most_common(5):
        role = token_to_role.get(pred, 'UNKNOWN')
        print(f"  {pred:<15} {count:<5} {role}")

# 3. MORPHOLOGICAL STRUCTURE
print(f"\n{'='*70}")
print("3. MORPHOLOGICAL STRUCTURE OF -AM/-ARY TOKENS")
print("="*70)

print(f"\n{'Token':<12} {'Prefix':<10} {'Middle':<12} {'Suffix':<10} {'Pattern':<20}")
print("-"*70)

for word in sorted(AM_ARY_TOKENS):
    count = sum(1 for f in folio_lines for l in folio_lines[f] if word in folio_lines[f][l])
    if count == 0:
        continue

    try:
        m = morph.extract(word)
        prefix = m.prefix or '-'
        middle = m.middle or '-'
        suffix = m.suffix or '-'

        # Determine pattern
        if word.endswith('ary'):
            pattern = 'X-ary (collection)'
        elif word.endswith('am'):
            pattern = 'X-am (vessel)'
        elif word.endswith('y'):
            pattern = 'X-y (state)'
        else:
            pattern = 'other'

    except:
        prefix = middle = suffix = '?'
        pattern = '?'

    print(f"{word:<12} {prefix:<10} {middle:<12} {suffix:<10} {pattern:<20}")

# 4. REGIME CORRELATION
print(f"\n{'='*70}")
print("4. REGIME CORRELATION")
print("="*70)

if folio_regime:
    am_ary_by_regime = Counter()
    folio_by_regime = Counter()

    for folio in folio_lines:
        regime = folio_regime.get(folio, 'UNKNOWN')
        folio_by_regime[regime] += 1

        has_am_ary = any(
            word in AM_ARY_TOKENS
            for line in folio_lines[folio]
            for word in folio_lines[folio][line]
        )
        if has_am_ary:
            am_ary_by_regime[regime] += 1

    print(f"\n{'Regime':<15} {'Folios':<10} {'With -am/-ary':<15} {'Rate %':<10}")
    print("-"*55)

    for regime in sorted(folio_by_regime.keys()):
        total = folio_by_regime[regime]
        with_am = am_ary_by_regime.get(regime, 0)
        rate = 100 * with_am / total if total > 0 else 0
        print(f"{regime:<15} {total:<10} {with_am:<15} {rate:<10.1f}")
else:
    print("REGIME data not available")

# 5. WHAT FOLLOWS ON NEXT LINE?
print(f"\n{'='*70}")
print("5. WHAT FOLLOWS -AM/-ARY ON NEXT LINE?")
print("="*70)

next_line_starters = []

for folio in folio_lines:
    lines_sorted = sorted(folio_lines[folio].keys())

    for idx, line in enumerate(lines_sorted):
        words = folio_lines[folio][line]
        if not words:
            continue

        last_word = words[-1]
        if last_word in AM_ARY_TOKENS:
            # Get next line's first word
            if idx + 1 < len(lines_sorted):
                next_line = lines_sorted[idx + 1]
                next_words = folio_lines[folio][next_line]
                if next_words:
                    next_line_starters.append({
                        'am_ary': last_word,
                        'next_first': next_words[0],
                        'next_role': token_to_role.get(next_words[0], 'UNKNOWN'),
                        'folio': folio
                    })

if next_line_starters:
    print(f"\nTotal line-final -am/-ary followed by new line: {len(next_line_starters)}")

    next_roles = Counter(n['next_role'] for n in next_line_starters)
    print(f"\nRole of NEXT line's first token:")
    for role, count in next_roles.most_common():
        pct = 100 * count / len(next_line_starters)
        print(f"  {role:<25} {count:<5} ({pct:.1f}%)")

    # Is next line gallows-initial (new paragraph)?
    next_gallows = sum(1 for n in next_line_starters if n['next_first'] and n['next_first'][0] in GALLOWS)
    print(f"\nNext line is gallows-initial (new paragraph): {next_gallows}/{len(next_line_starters)} ({100*next_gallows/len(next_line_starters):.1f}%)")

    # Specific next tokens
    next_tokens = Counter(n['next_first'] for n in next_line_starters)
    print(f"\nTop tokens starting next line:")
    for tok, count in next_tokens.most_common(10):
        role = token_to_role.get(tok, 'UNKNOWN')
        print(f"  {tok:<15} {count:<5} {role}")

# 6. FIXED COLLOCATIONS
print(f"\n{'='*70}")
print("6. FIXED COLLOCATIONS (BIGRAMS WITH -AM/-ARY)")
print("="*70)

bigrams = Counter()

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS and i > 0:
                bigram = (words[i-1], word)
                bigrams[bigram] += 1

print(f"\nMost frequent bigrams ending in -am/-ary:")
print(f"{'Bigram':<30} {'Count':<8} {'Pred Role':<20}")
print("-"*60)

for (pred, target), count in bigrams.most_common(20):
    role = token_to_role.get(pred, 'UNKNOWN')
    bigram_str = f"{pred} + {target}"
    print(f"{bigram_str:<30} {count:<8} {role:<20}")

# Check if any bigrams are "fixed" (appear consistently)
print(f"\nBigram consistency analysis:")
pred_target_counts = defaultdict(lambda: Counter())
for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS and i > 0:
                pred_target_counts[words[i-1]][word] += 1

fixed_pairs = []
for pred, targets in pred_target_counts.items():
    total = sum(targets.values())
    if total >= 5:  # At least 5 occurrences
        most_common = targets.most_common(1)[0]
        consistency = most_common[1] / total
        if consistency > 0.7:  # >70% goes to one target
            fixed_pairs.append((pred, most_common[0], total, consistency))

if fixed_pairs:
    print(f"\nFixed collocations (>70% consistency, n>=5):")
    for pred, target, count, cons in sorted(fixed_pairs, key=lambda x: -x[3])[:10]:
        role = token_to_role.get(pred, 'UNKNOWN')
        print(f"  {pred:<12} -> {target:<12} {count} occ, {100*cons:.0f}% consistent  [{role}]")

# 7. SECTION-SPECIFIC BEHAVIOR
print(f"\n{'='*70}")
print("7. SECTION-SPECIFIC BEHAVIOR")
print("="*70)

section_stats = defaultdict(lambda: {'total': 0, 'line_final': 0, 'predecessors': Counter()})

for folio in folio_lines:
    section = folio_section.get(folio, '?')
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        n = len(words)
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS:
                section_stats[section]['total'] += 1
                if i == n - 1:
                    section_stats[section]['line_final'] += 1
                if i > 0:
                    section_stats[section]['predecessors'][words[i-1]] += 1

print(f"\n{'Section':<10} {'Total':<8} {'Line-final %':<15} {'Top predecessors':<40}")
print("-"*75)

for section in ['H', 'S', 'B', 'C', 'T']:
    stats = section_stats.get(section)
    if not stats or stats['total'] == 0:
        continue

    total = stats['total']
    lf_rate = 100 * stats['line_final'] / total
    top_preds = ', '.join(f"{p}({c})" for p, c in stats['predecessors'].most_common(3))

    print(f"{section:<10} {total:<8} {lf_rate:<15.1f} {top_preds:<40}")

# 8. SUMMARY
print(f"\n{'='*70}")
print("8. APPARATUS INTERPRETATION SUMMARY")
print("="*70)

print("""
BRUNSCHWIG COLLECTION APPARATUS:
- Receiver (aludel): collects distillate at head
- Cucurbit: base vessel containing material
- Cooling trough: water bath for condenser

-AM/-ARY TOKENS AS APPARATUS MARKERS:

1. POSITIONAL BEHAVIOR:
   - 72.7% line-final: marks END of operation sequence
   - Mean paragraph position 0.587: late in processing sequence
   - Next line often starts with AUXILIARY (cycle continuation)

2. ENERGY CONTEXT:
   - Preceded by ENERGY_OPERATOR 27.3%
   - Lower kernel content on lines (24.6% vs 26.8% baseline)
   - Lower h-content (7.7% vs 8.6%) - not active phase management

3. MORPHOLOGICAL PATTERN:
   - -ary: pure collection marker
   - -am: vessel reference (dam, otam, am)
   - -y variants: state indicators (oly, oldy, daly, ldy)

4. FUNCTION HYPOTHESIS:
   If these mark collection apparatus:
   - Line-final = "collect into [apparatus]"
   - Low energy = passive collection, not active heating
   - Post-ENERGY = collect after distillation step
""")

# Save results
output = {
    'top_predecessors': [(pred, count) for pred, count in pred_counts.most_common(20)],
    'fixed_collocations': [(pred, target, count, cons) for pred, target, count, cons in fixed_pairs] if fixed_pairs else [],
    'next_line_roles': dict(Counter(n['next_role'] for n in next_line_starters)) if next_line_starters else {},
    'section_totals': {s: section_stats[s]['total'] for s in section_stats},
}

output_path = Path(__file__).parent.parent / 'results' / 'am_ary_phase2.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

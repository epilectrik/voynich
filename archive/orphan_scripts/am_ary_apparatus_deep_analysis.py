#!/usr/bin/env python3
"""
Deep analysis of -am/-ary suffix tokens as apparatus candidates.

From previous analysis:
- ary: 100% line-final, 0% ENERGY
- otam: 67.6% line-final, 16.7% ENERGY
- dam: 66.7% line-final, 21.4% ENERGY
- am: 80% line-final, 27.3% ENERGY

Questions:
1. Morphological structure - what are these tokens?
2. What PRECEDES them? (what operation ends with collection?)
3. Do they cluster in specific folios/paragraphs?
4. Are they associated with distillation (HIGH_H) paragraphs?
5. Do they appear at paragraph END as well as line end?
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
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

# Target tokens
AM_ARY_TOKENS = {'ary', 'am', 'otam', 'dam', 'daly', 'oly', 'oldy', 'ldy'}

# Build line and paragraph data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

def get_paragraphs(folio):
    lines = folio_lines[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        words = lines[line_num]
        if not words:
            continue
        first_word = words[0]
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, words)]
        else:
            current_para.append((line_num, words))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

print("="*70)
print("-AM/-ARY SUFFIX APPARATUS ANALYSIS")
print("="*70)

# 1. Morphological analysis
print(f"\n{'='*70}")
print("1. MORPHOLOGICAL STRUCTURE")
print("="*70)

print(f"\n{'Token':<12} {'Count':<8} {'Prefix':<10} {'Middle':<12} {'Suffix':<10} {'Role':<15}")
print("-"*75)

for word in sorted(AM_ARY_TOKENS):
    # Count occurrences
    count = sum(1 for f in folio_lines for l in folio_lines[f] if word in folio_lines[f][l])
    if count == 0:
        continue

    # Morphology
    try:
        m = morph.extract(word)
        prefix = m.prefix or '-'
        middle = m.middle or '-'
        suffix = m.suffix or '-'
    except:
        prefix = middle = suffix = '?'

    role = token_to_role.get(word, 'UNKNOWN')
    print(f"{word:<12} {count:<8} {prefix:<10} {middle:<12} {suffix:<10} {role:<15}")

# 2. What precedes these tokens?
print(f"\n{'='*70}")
print("2. WHAT PRECEDES -AM/-ARY TOKENS?")
print("="*70)

predecessors = defaultdict(Counter)

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in AM_ARY_TOKENS and i > 0:
                pred = words[i-1]
                predecessors[word][pred] += 1

for target in sorted(AM_ARY_TOKENS):
    if target in predecessors and predecessors[target]:
        print(f"\nTokens preceding '{target}':")
        for pred, count in predecessors[target].most_common(10):
            role = token_to_role.get(pred, '?')
            print(f"  {pred:<15} {count:<5} {role}")

# Aggregate predecessors
all_preds = Counter()
for target in AM_ARY_TOKENS:
    all_preds.update(predecessors.get(target, {}))

print(f"\nAll predecessors (aggregated):")
for pred, count in all_preds.most_common(15):
    role = token_to_role.get(pred, '?')
    print(f"  {pred:<15} {count:<5} {role}")

# Predecessor role distribution
pred_roles = Counter()
for pred, count in all_preds.items():
    role = token_to_role.get(pred, 'UNKNOWN')
    pred_roles[role] += count

print(f"\nPredecessor role distribution:")
total_preds = sum(pred_roles.values())
for role, count in pred_roles.most_common():
    print(f"  {role:<20} {count:<5} ({100*count/total_preds:.1f}%)")

# 3. Section and folio distribution
print(f"\n{'='*70}")
print("3. SECTION AND FOLIO DISTRIBUTION")
print("="*70)

am_ary_by_section = Counter()
am_ary_by_folio = Counter()

for folio in folio_lines:
    section = folio_section.get(folio, '?')
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for word in words:
            if word in AM_ARY_TOKENS:
                am_ary_by_section[section] += 1
                am_ary_by_folio[folio] += 1

print(f"\nBy section:")
for section, count in am_ary_by_section.most_common():
    print(f"  {section}: {count}")

print(f"\nTop folios:")
for folio, count in am_ary_by_folio.most_common(10):
    section = folio_section.get(folio, '?')
    print(f"  {folio} ({section}): {count}")

# 4. Paragraph position analysis
print(f"\n{'='*70}")
print("4. PARAGRAPH POSITION ANALYSIS")
print("="*70)

# Is -am/-ary at paragraph END?
para_positions = []

for folio in folio_lines:
    paras = get_paragraphs(folio)
    for para in paras:
        all_words = [w for _, words in para for w in words]
        n = len(all_words)
        if n < 3:
            continue

        for i, word in enumerate(all_words):
            if word in AM_ARY_TOKENS:
                norm_pos = i / (n - 1) if n > 1 else 0.5
                para_positions.append({
                    'word': word,
                    'pos': norm_pos,
                    'is_last': (i == n - 1),
                    'folio': folio
                })

print(f"\nTotal -am/-ary occurrences in paragraphs: {len(para_positions)}")
print(f"Mean paragraph position: {np.mean([p['pos'] for p in para_positions]):.3f}")
print(f"At paragraph end (last token): {sum(1 for p in para_positions if p['is_last'])} ({100*sum(1 for p in para_positions if p['is_last'])/len(para_positions):.1f}%)")

# Position by token
print(f"\n{'Token':<12} {'Count':<8} {'Mean Pos':<12} {'% Last':<10}")
print("-"*45)

for target in sorted(AM_ARY_TOKENS):
    positions = [p for p in para_positions if p['word'] == target]
    if len(positions) >= 3:
        mean_pos = np.mean([p['pos'] for p in positions])
        pct_last = 100 * sum(1 for p in positions if p['is_last']) / len(positions)
        print(f"{target:<12} {len(positions):<8} {mean_pos:<12.3f} {pct_last:<10.1f}")

# 5. Association with paragraph kernel type
print(f"\n{'='*70}")
print("5. ASSOCIATION WITH PARAGRAPH KERNEL TYPE")
print("="*70)

def classify_paragraph(words):
    if len(words) < 10:
        return None
    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total = k + h + e
    if total < 10:
        return None
    k_pct = 100 * k / total
    h_pct = 100 * h / total
    if k_pct > 35:
        return 'HIGH_K'
    elif h_pct > 35:
        return 'HIGH_H'
    else:
        return 'OTHER'

para_type_counts = Counter()
am_ary_in_para_type = Counter()

for folio in folio_lines:
    paras = get_paragraphs(folio)
    for para in paras:
        all_words = [w for _, words in para for w in words]
        ptype = classify_paragraph(all_words)
        if ptype:
            para_type_counts[ptype] += 1
            has_am_ary = any(w in AM_ARY_TOKENS for w in all_words)
            if has_am_ary:
                am_ary_in_para_type[ptype] += 1

print(f"\n{'Para Type':<12} {'Total':<10} {'With -am/-ary':<15} {'Rate %':<10}")
print("-"*50)

for ptype in ['HIGH_K', 'HIGH_H', 'OTHER']:
    total = para_type_counts.get(ptype, 0)
    with_am = am_ary_in_para_type.get(ptype, 0)
    rate = 100 * with_am / total if total > 0 else 0
    print(f"{ptype:<12} {total:<10} {with_am:<15} {rate:<10.1f}")

# Chi-square test
print(f"\nChi-square test: -am/-ary rate by paragraph type")
observed = [am_ary_in_para_type.get(t, 0) for t in ['HIGH_K', 'HIGH_H', 'OTHER']]
expected_rate = sum(observed) / sum(para_type_counts.values())
expected = [para_type_counts.get(t, 0) * expected_rate for t in ['HIGH_K', 'HIGH_H', 'OTHER']]

if all(e > 5 for e in expected):
    chi2, p_val = scipy_stats.chisquare(observed, expected)
    print(f"Chi-square = {chi2:.2f}, p = {p_val:.4f}")
    if p_val < 0.05:
        print("-> *Significant: -am/-ary rate varies by paragraph type")
    else:
        print("-> Not significant: -am/-ary evenly distributed")

# 6. Line context analysis
print(f"\n{'='*70}")
print("6. LINE CONTEXT: KERNEL CONTENT OF -AM/-ARY LINES")
print("="*70)

am_ary_lines = []
other_lines = []

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        has_am_ary = any(w in AM_ARY_TOKENS for w in words)

        k = sum(w.count('k') for w in words)
        h = sum(w.count('h') for w in words)
        e = sum(w.count('e') for w in words)
        total_chars = sum(len(w) for w in words)

        if total_chars > 0:
            kernel_rate = (k + h + e) / total_chars
            h_rate = h / total_chars

            if has_am_ary:
                am_ary_lines.append({'kernel': kernel_rate, 'h': h_rate, 'k': k/total_chars, 'e': e/total_chars})
            else:
                other_lines.append({'kernel': kernel_rate, 'h': h_rate, 'k': k/total_chars, 'e': e/total_chars})

print(f"\nLines with -am/-ary: {len(am_ary_lines)}")
print(f"Lines without: {len(other_lines)}")

print(f"\n{'Metric':<20} {'With -am/-ary':<15} {'Without':<15} {'Difference':<12}")
print("-"*60)

for metric in ['kernel', 'h', 'k', 'e']:
    am_val = 100 * np.mean([l[metric] for l in am_ary_lines])
    other_val = 100 * np.mean([l[metric] for l in other_lines])
    diff = am_val - other_val
    print(f"{metric:<20} {am_val:<15.2f} {other_val:<15.2f} {diff:+.2f}")

# Mann-Whitney for h-content
u_stat, p_val = scipy_stats.mannwhitneyu(
    [l['h'] for l in am_ary_lines],
    [l['h'] for l in other_lines],
    alternative='two-sided'
)
print(f"\nh-content Mann-Whitney: p = {p_val:.4f}")

# 7. Brunschwig interpretation
print(f"\n{'='*70}")
print("7. BRUNSCHWIG APPARATUS INTERPRETATION")
print("="*70)

print("""
If -am/-ary tokens encode collection/output apparatus:

BRUNSCHWIG COLLECTION APPARATUS:
- Receiver (collection vessel for distillate)
- Cucurbit body (contains material)
- Cooling trough (for condenser)

EXPECTED BEHAVIOR:
1. Appear at line END (collection happens after processing)
2. Low energy context (not active heating)
3. Follow phase operations (after distillation)
4. Associated with HIGH_H paragraphs (distillation)

OBSERVED BEHAVIOR:
""")

# Summary statistics
print(f"1. Line-final rate: {100*sum(1 for f in folio_lines for l in folio_lines[f] for i, w in enumerate(folio_lines[f][l]) if w in AM_ARY_TOKENS and i == len(folio_lines[f][l])-1) / max(1, sum(1 for f in folio_lines for l in folio_lines[f] for w in folio_lines[f][l] if w in AM_ARY_TOKENS)):.1f}%")

high_h_rate = 100 * am_ary_in_para_type.get('HIGH_H', 0) / para_type_counts.get('HIGH_H', 1)
high_k_rate = 100 * am_ary_in_para_type.get('HIGH_K', 0) / para_type_counts.get('HIGH_K', 1)
print(f"2. HIGH_H paragraph rate: {high_h_rate:.1f}%")
print(f"3. HIGH_K paragraph rate: {high_k_rate:.1f}%")
print(f"4. h-content on lines: {100*np.mean([l['h'] for l in am_ary_lines]):.2f}% (vs {100*np.mean([l['h'] for l in other_lines]):.2f}% baseline)")

# Save results
output = {
    'am_ary_tokens': list(AM_ARY_TOKENS),
    'section_distribution': dict(am_ary_by_section),
    'para_type_rates': {
        'HIGH_H': high_h_rate,
        'HIGH_K': high_k_rate,
    },
    'predecessor_roles': dict(pred_roles),
}

output_path = Path(__file__).parent.parent / 'results' / 'am_ary_apparatus.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

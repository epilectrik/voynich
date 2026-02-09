#!/usr/bin/env python3
"""
Map B paragraph kernel signatures to potential Brunschwig operations.

Goal: Determine what HIGH-K, HIGH-H, and BALANCED paragraphs encode
beyond just the k/h/e character content.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map for role analysis
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Build paragraph data
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs

def analyze_paragraph(para, folio, para_idx):
    """Extract comprehensive features from a paragraph"""
    all_tokens = []
    for line_num, tokens in para:
        all_tokens.extend(tokens)

    words = [t.word for t in all_tokens]
    if len(words) < 5:
        return None

    # Basic stats
    first_word = words[0]
    gallows = first_word[0] if first_word else '?'

    # Kernel analysis
    k_count = sum(w.count('k') for w in words)
    h_count = sum(w.count('h') for w in words)
    e_count = sum(w.count('e') for w in words)
    total_kernel = k_count + h_count + e_count

    if total_kernel < 10:
        return None

    k_pct = 100 * k_count / total_kernel
    h_pct = 100 * h_count / total_kernel
    e_pct = 100 * e_count / total_kernel

    # Classify kernel signature
    if k_pct > 35:
        kernel_type = 'HIGH_K'
    elif h_pct > 35:
        kernel_type = 'HIGH_H'
    elif e_pct > 60:
        kernel_type = 'HIGH_E'
    else:
        kernel_type = 'BALANCED'

    # Role distribution
    roles = defaultdict(int)
    for w in words:
        role = token_to_role.get(w, 'UNKNOWN')
        roles[role] += 1

    # Prefix analysis
    prefixes = defaultdict(int)
    for w in words:
        if w.startswith('qo'):
            prefixes['qo'] += 1
        elif w.startswith('ch'):
            prefixes['ch'] += 1
        elif w.startswith('sh'):
            prefixes['sh'] += 1
        elif w.startswith('ok'):
            prefixes['ok'] += 1
        elif w.startswith('ot'):
            prefixes['ot'] += 1
        elif w.startswith('ol'):
            prefixes['ol'] += 1
        elif w.startswith('po'):
            prefixes['po'] += 1
        elif w.startswith('da'):
            prefixes['da'] += 1
        elif w.startswith('ai'):
            prefixes['ai'] += 1

    # Suffix analysis
    suffixes = defaultdict(int)
    for w in words:
        if len(w) >= 2:
            if w.endswith('y'):
                suffixes['y'] += 1
            elif w.endswith('dy'):
                suffixes['dy'] += 1
            elif w.endswith('n'):
                suffixes['n'] += 1
            elif w.endswith('r'):
                suffixes['r'] += 1
            elif w.endswith('l'):
                suffixes['l'] += 1
            elif w.endswith('s'):
                suffixes['s'] += 1

    # LINK detection (ol-containing)
    link_count = sum(1 for w in words if 'ol' in w)

    # Specific token markers
    daiin_count = sum(1 for w in words if w == 'daiin')
    aiin_count = sum(1 for w in words if w == 'aiin')

    return {
        'folio': folio,
        'para_idx': para_idx,
        'gallows': gallows,
        'first_token': first_word,
        'n_tokens': len(words),
        'n_lines': len(para),
        'k_pct': k_pct,
        'h_pct': h_pct,
        'e_pct': e_pct,
        'kernel_type': kernel_type,
        'roles': dict(roles),
        'prefixes': dict(prefixes),
        'suffixes': dict(suffixes),
        'link_count': link_count,
        'link_rate': link_count / len(words),
        'daiin_count': daiin_count,
        'aiin_count': aiin_count,
        'words': words
    }

# Collect all paragraphs
print("="*70)
print("COLLECTING ALL B PARAGRAPHS")
print("="*70)

all_paragraphs = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        stats = analyze_paragraph(p, folio, i)
        if stats:
            all_paragraphs.append(stats)

print(f"\nTotal paragraphs analyzed: {len(all_paragraphs)}")

# Group by kernel type
by_type = defaultdict(list)
for p in all_paragraphs:
    by_type[p['kernel_type']].append(p)

print(f"\nBy kernel type:")
for kt, paras in sorted(by_type.items()):
    print(f"  {kt}: {len(paras)} paragraphs")

# ============================================================
# COMPARE KERNEL TYPES
# ============================================================
print(f"\n{'='*70}")
print("KERNEL TYPE PROFILES")
print("="*70)

def aggregate_stats(para_list):
    """Compute aggregate statistics for a list of paragraphs"""
    n = len(para_list)

    # Role distribution
    role_totals = defaultdict(int)
    total_tokens = 0
    for p in para_list:
        for role, count in p['roles'].items():
            role_totals[role] += count
        total_tokens += p['n_tokens']

    role_pcts = {r: 100*c/total_tokens for r, c in role_totals.items()}

    # Prefix distribution
    prefix_totals = defaultdict(int)
    for p in para_list:
        for prefix, count in p['prefixes'].items():
            prefix_totals[prefix] += count

    prefix_pcts = {pf: 100*c/total_tokens for pf, c in prefix_totals.items()}

    # Link rate
    mean_link_rate = np.mean([p['link_rate'] for p in para_list])

    # Gallows distribution
    gallows_counts = Counter(p['gallows'] for p in para_list)

    # Mean kernel
    mean_k = np.mean([p['k_pct'] for p in para_list])
    mean_h = np.mean([p['h_pct'] for p in para_list])
    mean_e = np.mean([p['e_pct'] for p in para_list])

    return {
        'n': n,
        'total_tokens': total_tokens,
        'role_pcts': role_pcts,
        'prefix_pcts': prefix_pcts,
        'mean_link_rate': mean_link_rate,
        'gallows': dict(gallows_counts),
        'mean_k': mean_k,
        'mean_h': mean_h,
        'mean_e': mean_e
    }

type_stats = {kt: aggregate_stats(paras) for kt, paras in by_type.items()}

# Print comparison table
print(f"\n{'Metric':<25} {'HIGH_K':<12} {'HIGH_H':<12} {'HIGH_E':<12} {'BALANCED':<12}")
print("-"*70)

# Kernel means
print(f"{'k% (mean)':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if kt in type_stats:
        print(f"{type_stats[kt]['mean_k']:<12.1f}", end="")
    else:
        print(f"{'-':<12}", end="")
print()

print(f"{'h% (mean)':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if kt in type_stats:
        print(f"{type_stats[kt]['mean_h']:<12.1f}", end="")
    else:
        print(f"{'-':<12}", end="")
print()

print(f"{'e% (mean)':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if kt in type_stats:
        print(f"{type_stats[kt]['mean_e']:<12.1f}", end="")
    else:
        print(f"{'-':<12}", end="")
print()

print("-"*70)

# Role distribution
major_roles = ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'CORE_CONTROL', 'UNKNOWN']
for role in major_roles:
    print(f"{role[:20]:<25}", end="")
    for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
        if kt in type_stats:
            pct = type_stats[kt]['role_pcts'].get(role, 0)
            print(f"{pct:<12.1f}", end="")
        else:
            print(f"{'-':<12}", end="")
    print()

print("-"*70)

# Prefix distribution
major_prefixes = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da']
for prefix in major_prefixes:
    print(f"{'PREFIX: '+prefix:<25}", end="")
    for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
        if kt in type_stats:
            pct = type_stats[kt]['prefix_pcts'].get(prefix, 0)
            print(f"{pct:<12.1f}", end="")
        else:
            print(f"{'-':<12}", end="")
    print()

print("-"*70)

# LINK rate
print(f"{'LINK rate':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if kt in type_stats:
        print(f"{100*type_stats[kt]['mean_link_rate']:<12.1f}", end="")
    else:
        print(f"{'-':<12}", end="")
print()

# ============================================================
# STATISTICAL TESTS
# ============================================================
print(f"\n{'='*70}")
print("STATISTICAL TESTS (HIGH_K vs HIGH_H)")
print("="*70)

if 'HIGH_K' in by_type and 'HIGH_H' in by_type:
    high_k = by_type['HIGH_K']
    high_h = by_type['HIGH_H']

    # Compare role distributions
    print("\nRole distribution comparison (Mann-Whitney U):")
    for role in ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'FLOW_OPERATOR']:
        k_rates = [p['roles'].get(role, 0) / p['n_tokens'] for p in high_k]
        h_rates = [p['roles'].get(role, 0) / p['n_tokens'] for p in high_h]

        u_stat, p_val = scipy_stats.mannwhitneyu(k_rates, h_rates, alternative='two-sided')
        k_mean = 100 * np.mean(k_rates)
        h_mean = 100 * np.mean(h_rates)
        sig = "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {role[:20]}: HIGH_K={k_mean:.1f}%, HIGH_H={h_mean:.1f}%, p={p_val:.4f} {sig}")

    # Compare prefix distributions
    print("\nPrefix distribution comparison:")
    for prefix in ['qo', 'ch', 'sh', 'ok']:
        k_rates = [p['prefixes'].get(prefix, 0) / p['n_tokens'] for p in high_k]
        h_rates = [p['prefixes'].get(prefix, 0) / p['n_tokens'] for p in high_h]

        u_stat, p_val = scipy_stats.mannwhitneyu(k_rates, h_rates, alternative='two-sided')
        k_mean = 100 * np.mean(k_rates)
        h_mean = 100 * np.mean(h_rates)
        sig = "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {prefix}: HIGH_K={k_mean:.1f}%, HIGH_H={h_mean:.1f}%, p={p_val:.4f} {sig}")

    # Compare LINK rate
    print("\nLINK rate comparison:")
    k_link = [p['link_rate'] for p in high_k]
    h_link = [p['link_rate'] for p in high_h]
    u_stat, p_val = scipy_stats.mannwhitneyu(k_link, h_link, alternative='two-sided')
    print(f"  HIGH_K={100*np.mean(k_link):.1f}%, HIGH_H={100*np.mean(h_link):.1f}%, p={p_val:.4f}")

# ============================================================
# DISTINCTIVE VOCABULARY
# ============================================================
print(f"\n{'='*70}")
print("DISTINCTIVE VOCABULARY BY KERNEL TYPE")
print("="*70)

def get_vocab_enrichment(target_paras, other_paras, min_count=5):
    """Find words enriched in target vs other paragraphs"""
    target_words = Counter()
    other_words = Counter()

    for p in target_paras:
        target_words.update(p['words'])
    for p in other_paras:
        other_words.update(p['words'])

    target_total = sum(target_words.values())
    other_total = sum(other_words.values())

    enriched = []
    for word, count in target_words.items():
        if count < min_count:
            continue
        target_rate = count / target_total
        other_rate = (other_words.get(word, 0) + 0.5) / (other_total + 0.5)  # Smoothing
        ratio = target_rate / other_rate
        if ratio > 1.5:
            enriched.append((word, count, ratio, target_rate, other_rate))

    enriched.sort(key=lambda x: -x[2])
    return enriched

for kt in ['HIGH_K', 'HIGH_H']:
    if kt not in by_type:
        continue

    target = by_type[kt]
    others = [p for kk, pp in by_type.items() if kk != kt for p in pp]

    enriched = get_vocab_enrichment(target, others, min_count=10)

    print(f"\n{kt} enriched vocabulary (vs all others):")
    print(f"  {'Word':<15} {'Count':<8} {'Ratio':<8} {'In-type%':<10} {'Other%':<10}")
    print("  " + "-"*55)
    for word, count, ratio, t_rate, o_rate in enriched[:15]:
        print(f"  {word:<15} {count:<8} {ratio:<8.2f} {100*t_rate:<10.2f} {100*o_rate:<10.2f}")

# ============================================================
# BRUNSCHWIG OPERATION MAPPING
# ============================================================
print(f"\n{'='*70}")
print("BRUNSCHWIG OPERATION MAPPING (SPECULATIVE)")
print("="*70)

print("""
Based on the distinctive features of each kernel type:

HIGH_K Paragraphs (k > 35%):
  - Lower FLOW_OPERATOR rate
  - Higher ok- prefix (kernel-adjacent operations)
  - Vocabulary: qokeey, okeey, olkeey, qokaiin (k-rich)

  BRUNSCHWIG MAPPING: "ENERGY INPUT PHASE"
  - Active heating operations
  - Applying fire/heat to material
  - "Distill with fire of the second degree"

HIGH_H Paragraphs (h > 35%):
  - Higher ch/sh prefix rate
  - Vocabulary: shedy, chedy, cheody (h-rich)

  BRUNSCHWIG MAPPING: "MONITORING/CHECKING PHASE"
  - Sensory monitoring (color, smell, behavior)
  - "Watch until it becomes clear"
  - "Check if it burns on linen"

BALANCED Paragraphs:
  - Mixed operations
  - Standard processing with all control types

  BRUNSCHWIG MAPPING: "GENERAL PROCEDURE"
  - Standard distillation steps
  - Combined heating and monitoring
""")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'n_paragraphs': len(all_paragraphs),
    'by_type_counts': {kt: len(pp) for kt, pp in by_type.items()},
    'type_stats': {kt: {
        'n': s['n'],
        'mean_k': s['mean_k'],
        'mean_h': s['mean_h'],
        'mean_e': s['mean_e'],
        'mean_link_rate': s['mean_link_rate'],
        'role_pcts': s['role_pcts'],
        'prefix_pcts': s['prefix_pcts']
    } for kt, s in type_stats.items()}
}

output_path = Path(__file__).parent.parent / 'results' / 'paragraph_operation_mapping.json'
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

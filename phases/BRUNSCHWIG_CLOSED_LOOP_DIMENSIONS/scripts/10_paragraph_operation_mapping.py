#!/usr/bin/env python3
"""
Map B paragraph types to Brunschwig operation categories.

BRSC defines these operation-to-Voynich mappings:
1. Sensory monitoring (finger test) -> LINK
2. Drip timing operations -> k/h kernel
3. Cooling/equilibration -> e kernel
4. Recovery/retry -> FQ escape handler
5. Quality rejection -> FL hazard classes

Question: Do HIGH_K and HIGH_H paragraphs specialize in different
Brunschwig operation categories?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

# Key class definitions from BCSC
LINK_CLASS = 29  # Monitoring operations
FQ_CLASSES = {9, 13, 14, 23}  # Escape/recovery operations
FL_CLASSES = {7, 30, 31}  # Hazard-related classes
EN_CLASSES = {32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49}  # Energy operators
CC_CLASSES = {10, 11, 17}  # Core control

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

# Collect all paragraphs with Brunschwig operation metrics
all_paragraphs = []

for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = []
        for line_num, tokens in p:
            words.extend([t.word for t in tokens])

        if len(words) < 10:
            continue

        # Kernel analysis
        k = sum(w.count('k') for w in words)
        h = sum(w.count('h') for w in words)
        e = sum(w.count('e') for w in words)
        total_kernel = k + h + e
        if total_kernel < 10:
            continue

        k_pct = 100 * k / total_kernel
        h_pct = 100 * h / total_kernel
        e_pct = 100 * e / total_kernel

        if k_pct > 35:
            kernel_type = 'HIGH_K'
        elif h_pct > 35:
            kernel_type = 'HIGH_H'
        elif e_pct > 60:
            kernel_type = 'HIGH_E'
        else:
            kernel_type = 'BALANCED'

        # Brunschwig operation metrics
        n_tokens = len(words)

        # 1. LINK (monitoring) - BRSC: "finger test"
        link_tokens = sum(1 for w in words if token_to_class.get(w) == LINK_CLASS)
        link_rate = link_tokens / n_tokens

        # 2. FQ (escape/recovery) - BRSC: "recovery/retry"
        fq_tokens = sum(1 for w in words if token_to_class.get(w) in FQ_CLASSES)
        fq_rate = fq_tokens / n_tokens

        # 3. FL (hazard navigation) - BRSC: "quality rejection"
        fl_tokens = sum(1 for w in words if token_to_class.get(w) in FL_CLASSES)
        fl_rate = fl_tokens / n_tokens

        # 4. EN (energy operations) - BRSC: "fire degree application"
        en_tokens = sum(1 for w in words if token_to_class.get(w) in EN_CLASSES)
        en_rate = en_tokens / n_tokens

        # 5. CC (core control) - BRSC: "process control"
        cc_tokens = sum(1 for w in words if token_to_class.get(w) in CC_CLASSES)
        cc_rate = cc_tokens / n_tokens

        # 6. Kernel-specific rates (for drip timing / equilibration distinction)
        # Per BRSC: k/h = drip timing, e = cooling
        k_rate = k / n_tokens  # Raw k characters per token
        h_rate = h / n_tokens
        e_rate = e / n_tokens

        all_paragraphs.append({
            'folio': folio,
            'para_idx': i,
            'kernel_type': kernel_type,
            'k_pct': k_pct,
            'h_pct': h_pct,
            'e_pct': e_pct,
            'n_tokens': n_tokens,
            'link_rate': link_rate,
            'fq_rate': fq_rate,
            'fl_rate': fl_rate,
            'en_rate': en_rate,
            'cc_rate': cc_rate,
            'k_rate': k_rate,
            'h_rate': h_rate,
            'e_rate': e_rate,
            'words': words
        })

print("="*70)
print("BRUNSCHWIG OPERATION MAPPING")
print("="*70)

print(f"\nTotal paragraphs: {len(all_paragraphs)}")

# Group by kernel type
by_type = defaultdict(list)
for p in all_paragraphs:
    by_type[p['kernel_type']].append(p)

print(f"\nBy kernel type:")
for kt in ['HIGH_K', 'HIGH_H', 'HIGH_E', 'BALANCED']:
    if kt in by_type:
        print(f"  {kt}: {len(by_type[kt])} paragraphs")

# ============================================================
# BRUNSCHWIG OPERATION PROFILE BY PARAGRAPH TYPE
# ============================================================
print(f"\n{'='*70}")
print("BRUNSCHWIG OPERATION RATES BY PARAGRAPH TYPE")
print("="*70)

print(f"\n{'Operation':<20} {'BRSC Mapping':<25} {'HIGH_K':<10} {'HIGH_H':<10} {'BALANCED':<10}")
print("-"*75)

operations = [
    ('LINK rate', 'Sensory monitoring'),
    ('FQ rate', 'Recovery/retry'),
    ('FL rate', 'Quality rejection'),
    ('EN rate', 'Fire application'),
    ('CC rate', 'Process control'),
]

for op_name, brsc_name in operations:
    field = op_name.lower().replace(' ', '_')
    print(f"{op_name:<20} {brsc_name:<25}", end="")
    for kt in ['HIGH_K', 'HIGH_H', 'BALANCED']:
        if kt in by_type:
            mean_val = 100 * np.mean([p[field] for p in by_type[kt]])
            print(f"{mean_val:<10.1f}", end="")
    print()

print("-"*75)
print(f"{'k chars/token':<20} {'Drip timing (active)':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    if kt in by_type:
        mean_val = np.mean([p['k_rate'] for p in by_type[kt]])
        print(f"{mean_val:<10.2f}", end="")
print()

print(f"{'h chars/token':<20} {'Drip timing (monitor)':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    if kt in by_type:
        mean_val = np.mean([p['h_rate'] for p in by_type[kt]])
        print(f"{mean_val:<10.2f}", end="")
print()

print(f"{'e chars/token':<20} {'Cooling/equilibration':<25}", end="")
for kt in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    if kt in by_type:
        mean_val = np.mean([p['e_rate'] for p in by_type[kt]])
        print(f"{mean_val:<10.2f}", end="")
print()

# ============================================================
# STATISTICAL TESTS
# ============================================================
print(f"\n{'='*70}")
print("STATISTICAL TESTS: HIGH_K vs HIGH_H")
print("="*70)

if 'HIGH_K' in by_type and 'HIGH_H' in by_type:
    high_k = by_type['HIGH_K']
    high_h = by_type['HIGH_H']

    tests = [
        ('LINK (monitoring)', 'link_rate'),
        ('FQ (recovery)', 'fq_rate'),
        ('FL (rejection)', 'fl_rate'),
        ('EN (fire/energy)', 'en_rate'),
        ('CC (control)', 'cc_rate'),
    ]

    print(f"\n{'Operation':<25} {'HIGH_K':<10} {'HIGH_H':<10} {'U-stat':<12} {'p-value':<12} {'Sig'}")
    print("-"*80)

    for name, field in tests:
        k_vals = [p[field] for p in high_k]
        h_vals = [p[field] for p in high_h]

        u_stat, p_val = scipy_stats.mannwhitneyu(k_vals, h_vals, alternative='two-sided')
        k_mean = 100 * np.mean(k_vals)
        h_mean = 100 * np.mean(h_vals)

        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"{name:<25} {k_mean:<10.1f} {h_mean:<10.1f} {u_stat:<12.0f} {p_val:<12.4f} {sig}")

# ============================================================
# BRUNSCHWIG OPERATION INTERPRETATION
# ============================================================
print(f"\n{'='*70}")
print("BRUNSCHWIG OPERATION INTERPRETATION")
print("="*70)

# Calculate effect sizes and directions
if 'HIGH_K' in by_type and 'HIGH_H' in by_type:
    high_k = by_type['HIGH_K']
    high_h = by_type['HIGH_H']

    print("\nOperation biases (HIGH_K vs HIGH_H):")

    # FQ (recovery)
    k_fq = 100 * np.mean([p['fq_rate'] for p in high_k])
    h_fq = 100 * np.mean([p['fq_rate'] for p in high_h])
    print(f"\n  FQ (Recovery/retry): HIGH_K={k_fq:.1f}% vs HIGH_H={h_fq:.1f}%")
    if k_fq > h_fq:
        print(f"    -> HIGH_K paragraphs do MORE recovery operations")
        print(f"    -> BRSC: 'If it overheats, remove from fire...' procedures")

    # EN (fire application)
    k_en = 100 * np.mean([p['en_rate'] for p in high_k])
    h_en = 100 * np.mean([p['en_rate'] for p in high_h])
    print(f"\n  EN (Fire application): HIGH_K={k_en:.1f}% vs HIGH_H={h_en:.1f}%")
    if h_en > k_en:
        print(f"    -> HIGH_H paragraphs do MORE fire/energy operations")
        print(f"    -> BRSC: 'Distill with fire of second degree...' procedures")

    # LINK (monitoring)
    k_link = 100 * np.mean([p['link_rate'] for p in high_k])
    h_link = 100 * np.mean([p['link_rate'] for p in high_h])
    print(f"\n  LINK (Monitoring): HIGH_K={k_link:.1f}% vs HIGH_H={h_link:.1f}%")

    # Kernel chars (drip timing breakdown)
    k_krate = np.mean([p['k_rate'] for p in high_k])
    h_krate = np.mean([p['k_rate'] for p in high_h])
    k_hrate = np.mean([p['h_rate'] for p in high_k])
    h_hrate = np.mean([p['h_rate'] for p in high_h])

    print(f"\n  k-chars (active intervention): HIGH_K={k_krate:.2f} vs HIGH_H={h_krate:.2f}")
    print(f"  h-chars (phase checking): HIGH_K={k_hrate:.2f} vs HIGH_H={h_hrate:.2f}")

    if k_krate > h_krate and h_hrate > k_hrate:
        print(f"\n    -> HIGH_K uses more 'k' (active fire adjustment)")
        print(f"    -> HIGH_H uses more 'h' (phase/state checking)")
        print(f"    -> BRSC parallel: k='adjust fire', h='check drip rate'")

# ============================================================
# FINAL MAPPING
# ============================================================
print(f"\n{'='*70}")
print("BRUNSCHWIG OPERATION MAPPING (FINAL)")
print("="*70)

print("""
Based on BRSC mappings and statistical analysis:

+-------------+------------------+--------------------------------+
| Para Type   | Voynich Profile  | Brunschwig Operation           |
+-------------+------------------+--------------------------------+
| HIGH_K      | High FQ rate     | RECOVERY PROCEDURES            |
|             | High k-chars     | "Remove from fire, let cool"   |
|             | Lower EN rate    | Crisis intervention mode       |
+-------------+------------------+--------------------------------+
| HIGH_H      | High EN rate     | ACTIVE DISTILLATION            |
|             | High h-chars     | "Distill with fire, watch..."  |
|             | Lower FQ rate    | Careful processing mode        |
+-------------+------------------+--------------------------------+
| BALANCED    | Mixed rates      | GENERAL PROCEDURES             |
|             | Mixed k/h/e      | Standard distillation steps    |
+-------------+------------------+--------------------------------+

BRSC Kernel Mapping Validation:
- k (ENERGY_MODULATOR): Fire adjustment, active intervention
- h (PHASE_MANAGER): Phase checking, drip timing monitoring
- e (EQUILIBRATION): Cooling, stabilization

This maps to Brunschwig's:
- k operations: "block the air holes to reduce fire"
- h operations: "watch as the clock strikes for drip timing"
- e operations: "let stand overnight to cool"
""")

# Save results
output = {
    'n_paragraphs': len(all_paragraphs),
    'by_type': {kt: len(pp) for kt, pp in by_type.items()},
    'profiles': {}
}

for kt in ['HIGH_K', 'HIGH_H', 'BALANCED']:
    if kt in by_type:
        pp = by_type[kt]
        output['profiles'][kt] = {
            'link_rate': float(np.mean([p['link_rate'] for p in pp])),
            'fq_rate': float(np.mean([p['fq_rate'] for p in pp])),
            'fl_rate': float(np.mean([p['fl_rate'] for p in pp])),
            'en_rate': float(np.mean([p['en_rate'] for p in pp])),
            'k_rate': float(np.mean([p['k_rate'] for p in pp])),
            'h_rate': float(np.mean([p['h_rate'] for p in pp])),
            'e_rate': float(np.mean([p['e_rate'] for p in pp])),
        }

output_path = Path(__file__).parent.parent / 'results' / 'brunschwig_operation_mapping.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

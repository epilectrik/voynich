#!/usr/bin/env python3
"""
Deep analysis of specialized folios.

From spatial analysis:
- Recovery-specialized: f39v, f40r (75% HIGH_K)
- Distillation-specialized: f34v, f43r, f46r, f46v (100% HIGH_H)

Questions:
1. What vocabulary distinguishes recovery-specialist folios?
2. What vocabulary distinguishes distillation-specialist folios?
3. Are there structural differences (paragraph length, token patterns)?
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

# Define folio groups
RECOVERY_FOLIOS = {'f39v', 'f40r', 'f94r', 'f107v', 'f50r', 'f50v'}  # >=50% HIGH_K
DISTILL_FOLIOS = {'f34v', 'f43r', 'f46r', 'f46v', 'f57r', 'f106v', 'f95v1', 'f39r', 'f94v', 'f115v'}  # >=70% HIGH_H

# Key classes from BCSC
FQ_CLASSES = {9, 13, 14, 23}  # Escape/recovery
EN_CLASSES = {32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49}  # Energy
FL_CLASSES = {7, 30, 31}  # Hazard
CC_CLASSES = {10, 11, 17}  # Core control
LINK_CLASS = 29  # Monitoring

# Build data by folio
folio_tokens = defaultdict(list)
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_tokens[token.folio].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

def analyze_folio_group(folios, name):
    """Analyze a group of specialized folios."""
    all_words = []
    vocab = Counter()
    role_counts = Counter()
    kernel_chars = {'k': 0, 'h': 0, 'e': 0}

    for folio in folios:
        words = folio_tokens.get(folio, [])
        all_words.extend(words)
        vocab.update(words)

        for w in words:
            cls = token_to_class.get(w)
            role = token_to_role.get(w, 'UNKNOWN')
            role_counts[role] += 1

            kernel_chars['k'] += w.count('k')
            kernel_chars['h'] += w.count('h')
            kernel_chars['e'] += w.count('e')

    n_tokens = len(all_words)
    total_kernel = sum(kernel_chars.values())

    # Compute rates
    fq_rate = sum(1 for w in all_words if token_to_class.get(w) in FQ_CLASSES) / n_tokens
    en_rate = sum(1 for w in all_words if token_to_class.get(w) in EN_CLASSES) / n_tokens
    fl_rate = sum(1 for w in all_words if token_to_class.get(w) in FL_CLASSES) / n_tokens
    link_rate = sum(1 for w in all_words if token_to_class.get(w) == LINK_CLASS) / n_tokens

    return {
        'name': name,
        'folios': list(folios),
        'n_folios': len(folios),
        'n_tokens': n_tokens,
        'vocab_size': len(vocab),
        'top_tokens': vocab.most_common(20),
        'role_dist': dict(role_counts),
        'fq_rate': fq_rate,
        'en_rate': en_rate,
        'fl_rate': fl_rate,
        'link_rate': link_rate,
        'k_pct': 100 * kernel_chars['k'] / total_kernel if total_kernel > 0 else 0,
        'h_pct': 100 * kernel_chars['h'] / total_kernel if total_kernel > 0 else 0,
        'e_pct': 100 * kernel_chars['e'] / total_kernel if total_kernel > 0 else 0,
    }

print("="*70)
print("SPECIALIZED FOLIO ANALYSIS")
print("="*70)

recovery_stats = analyze_folio_group(RECOVERY_FOLIOS, "RECOVERY (HIGH_K)")
distill_stats = analyze_folio_group(DISTILL_FOLIOS, "DISTILL (HIGH_H)")

# Get "normal" folios for comparison
all_folios = set(folio_tokens.keys())
normal_folios = all_folios - RECOVERY_FOLIOS - DISTILL_FOLIOS
normal_stats = analyze_folio_group(normal_folios, "BASELINE")

print(f"\n{'Metric':<25} {'RECOVERY':<15} {'DISTILL':<15} {'BASELINE':<15}")
print("-"*70)
print(f"{'Folios':<25} {recovery_stats['n_folios']:<15} {distill_stats['n_folios']:<15} {normal_stats['n_folios']:<15}")
print(f"{'Tokens':<25} {recovery_stats['n_tokens']:<15} {distill_stats['n_tokens']:<15} {normal_stats['n_tokens']:<15}")
print(f"{'Vocab size':<25} {recovery_stats['vocab_size']:<15} {distill_stats['vocab_size']:<15} {normal_stats['vocab_size']:<15}")

print(f"\n{'BRUNSCHWIG OPERATION RATES:':<70}")
print("-"*70)
print(f"{'FQ (recovery/escape)':<25} {100*recovery_stats['fq_rate']:<15.1f} {100*distill_stats['fq_rate']:<15.1f} {100*normal_stats['fq_rate']:<15.1f}")
print(f"{'EN (fire/energy)':<25} {100*recovery_stats['en_rate']:<15.1f} {100*distill_stats['en_rate']:<15.1f} {100*normal_stats['en_rate']:<15.1f}")
print(f"{'FL (hazard)':<25} {100*recovery_stats['fl_rate']:<15.1f} {100*distill_stats['fl_rate']:<15.1f} {100*normal_stats['fl_rate']:<15.1f}")
print(f"{'LINK (monitoring)':<25} {100*recovery_stats['link_rate']:<15.1f} {100*distill_stats['link_rate']:<15.1f} {100*normal_stats['link_rate']:<15.1f}")

print(f"\n{'KERNEL CHARACTER RATIOS:':<70}")
print("-"*70)
print(f"{'k% (energy modulation)':<25} {recovery_stats['k_pct']:<15.1f} {distill_stats['k_pct']:<15.1f} {normal_stats['k_pct']:<15.1f}")
print(f"{'h% (phase management)':<25} {recovery_stats['h_pct']:<15.1f} {distill_stats['h_pct']:<15.1f} {normal_stats['h_pct']:<15.1f}")
print(f"{'e% (equilibration)':<25} {recovery_stats['e_pct']:<15.1f} {distill_stats['e_pct']:<15.1f} {normal_stats['e_pct']:<15.1f}")

# Vocabulary comparison
print(f"\n{'='*70}")
print("DISTINCTIVE VOCABULARY")
print("="*70)

# Find tokens enriched in recovery vs distill
recovery_words = set()
for folio in RECOVERY_FOLIOS:
    recovery_words.update(folio_tokens.get(folio, []))

distill_words = set()
for folio in DISTILL_FOLIOS:
    distill_words.update(folio_tokens.get(folio, []))

recovery_only = recovery_words - distill_words
distill_only = distill_words - recovery_words
shared = recovery_words & distill_words

print(f"\nRecovery-only tokens: {len(recovery_only)}")
print(f"Distillation-only tokens: {len(distill_only)}")
print(f"Shared tokens: {len(shared)}")

# Count tokens to find most common exclusive ones
recovery_counts = Counter()
for folio in RECOVERY_FOLIOS:
    recovery_counts.update(folio_tokens.get(folio, []))

distill_counts = Counter()
for folio in DISTILL_FOLIOS:
    distill_counts.update(folio_tokens.get(folio, []))

print(f"\nTop RECOVERY-ONLY tokens (by count):")
recovery_only_counts = [(t, recovery_counts[t]) for t in recovery_only]
recovery_only_counts.sort(key=lambda x: -x[1])
for token, count in recovery_only_counts[:15]:
    role = token_to_role.get(token, '?')
    print(f"  {token:<15} count={count:<5} role={role}")

print(f"\nTop DISTILLATION-ONLY tokens (by count):")
distill_only_counts = [(t, distill_counts[t]) for t in distill_only]
distill_only_counts.sort(key=lambda x: -x[1])
for token, count in distill_only_counts[:15]:
    role = token_to_role.get(token, '?')
    print(f"  {token:<15} count={count:<5} role={role}")

# Enrichment analysis
print(f"\n{'='*70}")
print("ENRICHMENT ANALYSIS (shared tokens)")
print("="*70)

# For shared tokens, compute enrichment ratio
enrichments = []
for token in shared:
    r_count = recovery_counts[token]
    d_count = distill_counts[token]
    r_rate = r_count / recovery_stats['n_tokens']
    d_rate = d_count / distill_stats['n_tokens']
    if d_rate > 0:
        enrichment = r_rate / d_rate
        enrichments.append((token, enrichment, r_count, d_count))

enrichments.sort(key=lambda x: -x[1])

print(f"\nTokens enriched in RECOVERY folios (shared, ratio > 2x):")
for token, ratio, r_count, d_count in enrichments[:15]:
    if ratio > 2:
        role = token_to_role.get(token, '?')
        print(f"  {token:<15} {ratio:.1f}x enriched (R:{r_count} D:{d_count}) role={role}")

enrichments.sort(key=lambda x: x[1])
print(f"\nTokens enriched in DISTILLATION folios (shared, ratio < 0.5x):")
for token, ratio, r_count, d_count in enrichments[:15]:
    if ratio < 0.5:
        role = token_to_role.get(token, '?')
        print(f"  {token:<15} {1/ratio:.1f}x enriched in D (R:{r_count} D:{d_count}) role={role}")

# Brunschwig interpretation
print(f"\n{'='*70}")
print("BRUNSCHWIG INTERPRETATION")
print("="*70)

print("""
RECOVERY-SPECIALIZED FOLIOS (f39v, f40r, etc.):
""")
print(f"  FQ rate: {100*recovery_stats['fq_rate']:.1f}% (vs {100*normal_stats['fq_rate']:.1f}% baseline)")
print(f"  k%: {recovery_stats['k_pct']:.1f}% (vs {normal_stats['k_pct']:.1f}% baseline)")

if recovery_stats['fq_rate'] > normal_stats['fq_rate']:
    print("\n  -> These folios concentrate ESCAPE/RECOVERY operations")
    print("  -> BRSC mapping: 'If it overheats, remove from fire...' procedures")

print("""
DISTILLATION-SPECIALIZED FOLIOS (f34v, f43r, etc.):
""")
print(f"  EN rate: {100*distill_stats['en_rate']:.1f}% (vs {100*normal_stats['en_rate']:.1f}% baseline)")
print(f"  h%: {distill_stats['h_pct']:.1f}% (vs {normal_stats['h_pct']:.1f}% baseline)")

if distill_stats['en_rate'] > normal_stats['en_rate']:
    print("\n  -> These folios concentrate ENERGY/FIRE operations")
    print("  -> BRSC mapping: 'Distill with fire of second degree...' procedures")

# Statistical test: are the differences significant?
print(f"\n{'='*70}")
print("STATISTICAL VALIDATION")
print("="*70)

# Bootstrap test for FQ difference
recovery_fq_tokens = [1 if token_to_class.get(w) in FQ_CLASSES else 0
                       for folio in RECOVERY_FOLIOS for w in folio_tokens.get(folio, [])]
distill_fq_tokens = [1 if token_to_class.get(w) in FQ_CLASSES else 0
                      for folio in DISTILL_FOLIOS for w in folio_tokens.get(folio, [])]

u_stat, p_val = scipy_stats.mannwhitneyu(recovery_fq_tokens, distill_fq_tokens, alternative='greater')
print(f"\nFQ rate: RECOVERY vs DISTILL")
print(f"  Mann-Whitney U={u_stat:.0f}, p={p_val:.6f}")
if p_val < 0.001:
    print("  -> ***Highly significant: Recovery folios have more FQ")

# EN test
recovery_en_tokens = [1 if token_to_class.get(w) in EN_CLASSES else 0
                       for folio in RECOVERY_FOLIOS for w in folio_tokens.get(folio, [])]
distill_en_tokens = [1 if token_to_class.get(w) in EN_CLASSES else 0
                      for folio in DISTILL_FOLIOS for w in folio_tokens.get(folio, [])]

u_stat, p_val = scipy_stats.mannwhitneyu(distill_en_tokens, recovery_en_tokens, alternative='greater')
print(f"\nEN rate: DISTILL vs RECOVERY")
print(f"  Mann-Whitney U={u_stat:.0f}, p={p_val:.6f}")
if p_val < 0.001:
    print("  -> ***Highly significant: Distillation folios have more EN")

# Save results
output = {
    'recovery': recovery_stats,
    'distill': distill_stats,
    'baseline': normal_stats,
    'recovery_only_count': len(recovery_only),
    'distill_only_count': len(distill_only),
    'shared_count': len(shared),
}

# Remove non-serializable items
for key in ['top_tokens']:
    output['recovery'].pop(key, None)
    output['distill'].pop(key, None)
    output['baseline'].pop(key, None)

output_path = Path(__file__).parent.parent / 'results' / 'folio_specialization.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

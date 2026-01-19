#!/usr/bin/env python3
"""
DIRECTION B: LINK TEMPORAL STATE-SPACE MAPPING

Bounded, non-semantic analysis of LINK positioning relative to kernel states.

TESTS:
B-1: LINK probability conditioned on kernel state (P(LINK | prev=e/k/h))
B-2: LINK after kernel transitions (e->k->LINK?, k->e->LINK?, etc.)
B-3: LINK vs position-in-folio (early/middle/late)
B-4: LINK clustering vs sections

HARD STOP CONDITIONS:
1. No kernel OR positional conditioning -> waiting is human-managed
2. Weak effects (<10%) -> texture, not mechanism
3. No more than 1-2 Tier 2 constraints -> close permanently

Do NOT let LINK become a new kernel investigation.
"""

import os
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, mannwhitneyu
import random

os.chdir('C:/git/voynich')

print("=" * 70)
print("DIRECTION B: LINK TEMPORAL STATE-SPACE MAPPING")
print("Bounded, non-semantic analysis")
print("=" * 70)

# ==========================================================================
# LOAD DATA
# ==========================================================================

print("\nLoading data...")

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # MANDATORY: Filter to PRIMARY transcriber (H) only
        transcriber = row.get('transcriber', '').strip().strip('"')
        if transcriber != 'H':
            continue
        all_tokens.append(row)

b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']
print(f"Currier B tokens: {len(b_tokens)}")

# Extract words and folios
all_b_words = [t.get('word', '') for t in b_tokens]
all_b_folios = [t.get('folio', '') for t in b_tokens]

# ==========================================================================
# DEFINE KERNEL AND LINK
# ==========================================================================

def get_kernel_class(word):
    """Classify token by kernel contact. Returns 'k', 'h', 'e', or None."""
    if not word:
        return None
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy'):
        return 'e'
    return None

def is_link(word):
    """Check if token is LINK class (ol-containing)."""
    return 'ol' in word if word else False

# Classify all tokens
token_data = []
for i, (word, folio) in enumerate(zip(all_b_words, all_b_folios)):
    token_data.append({
        'idx': i,
        'word': word,
        'folio': folio,
        'kernel': get_kernel_class(word),
        'is_link': is_link(word)
    })

# Count basics
n_link = sum(1 for t in token_data if t['is_link'])
n_kernel = sum(1 for t in token_data if t['kernel'] is not None)
print(f"LINK tokens: {n_link} ({n_link/len(token_data)*100:.1f}%)")
print(f"Kernel tokens: {n_kernel} ({n_kernel/len(token_data)*100:.1f}%)")

# ==========================================================================
# B-1: LINK PROBABILITY CONDITIONED ON KERNEL STATE
# ==========================================================================

print("\n" + "=" * 70)
print("B-1: LINK PROBABILITY CONDITIONED ON KERNEL STATE")
print("Question: Is P(LINK | prev=e) different from P(LINK | prev=k/h)?")
print("=" * 70)

# Count: for each kernel class, how often is the NEXT token a LINK?
link_after_kernel = {'k': 0, 'h': 0, 'e': 0, 'none': 0}
total_after_kernel = {'k': 0, 'h': 0, 'e': 0, 'none': 0}

for i in range(len(token_data) - 1):
    curr = token_data[i]
    next_t = token_data[i + 1]

    # Only count within same folio
    if curr['folio'] != next_t['folio']:
        continue

    k_class = curr['kernel'] if curr['kernel'] else 'none'
    total_after_kernel[k_class] += 1
    if next_t['is_link']:
        link_after_kernel[k_class] += 1

print("\nP(LINK | previous token class):")
print(f"{'Prev Class':<12} {'LINK After':<12} {'Total After':<12} {'P(LINK)':<10}")
print("-" * 50)

base_p_link = n_link / len(token_data)
b1_results = {}

for k_class in ['k', 'h', 'e', 'none']:
    total = total_after_kernel[k_class]
    link_count = link_after_kernel[k_class]
    p_link = link_count / total if total > 0 else 0
    ratio = p_link / base_p_link if base_p_link > 0 else 0

    b1_results[k_class] = {
        'link_count': link_count,
        'total': total,
        'p_link': p_link,
        'ratio_to_baseline': ratio
    }

    print(f"{k_class:<12} {link_count:<12} {total:<12} {p_link:.4f} ({ratio:.2f}x base)")

# Chi-square test
observed = [[link_after_kernel[k], total_after_kernel[k] - link_after_kernel[k]]
            for k in ['k', 'h', 'e', 'none']]
chi2, p_chi, dof, expected = chi2_contingency(observed)
print(f"\nChi-square test: chi2={chi2:.2f}, p={p_chi:.6f}")

# Effect size: max difference from baseline
max_effect = max(abs(b1_results[k]['ratio_to_baseline'] - 1.0) for k in ['k', 'h', 'e'])
print(f"Max effect size (ratio - 1): {max_effect:.2%}")

# Null model: shuffle LINK within folio
print("\nNull model (LINK shuffled within folio):")
n_shuffles = 100
null_effects = []

for _ in range(n_shuffles):
    # Group by folio
    folio_tokens = defaultdict(list)
    for t in token_data:
        folio_tokens[t['folio']].append(t)

    # Shuffle is_link within each folio
    shuffled_data = []
    for folio in sorted(folio_tokens.keys()):
        tokens = folio_tokens[folio]
        link_flags = [t['is_link'] for t in tokens]
        random.shuffle(link_flags)
        for t, is_link_flag in zip(tokens, link_flags):
            shuffled_data.append({**t, 'is_link': is_link_flag})

    # Recompute
    null_link_after = {'k': 0, 'h': 0, 'e': 0}
    null_total_after = {'k': 0, 'h': 0, 'e': 0}

    for i in range(len(shuffled_data) - 1):
        curr = shuffled_data[i]
        next_t = shuffled_data[i + 1]
        if curr['folio'] != next_t['folio']:
            continue
        if curr['kernel']:
            null_total_after[curr['kernel']] += 1
            if next_t['is_link']:
                null_link_after[curr['kernel']] += 1

    null_effect = 0
    for k in ['k', 'h', 'e']:
        if null_total_after[k] > 0:
            null_p = null_link_after[k] / null_total_after[k]
            null_effect = max(null_effect, abs(null_p / base_p_link - 1.0))
    null_effects.append(null_effect)

null_mean = np.mean(null_effects)
null_std = np.std(null_effects)
z_score = (max_effect - null_mean) / null_std if null_std > 0 else 0
print(f"Null effect: {null_mean:.2%} +/- {null_std:.2%}")
print(f"Observed effect: {max_effect:.2%}")
print(f"Z-score: {z_score:.2f}")

b1_verdict = "SIGNAL" if max_effect > 0.10 and z_score > 2 else "WEAK/NONE"
print(f"\nB-1 VERDICT: {b1_verdict}")

# ==========================================================================
# B-2: LINK AFTER KERNEL TRANSITIONS
# ==========================================================================

print("\n" + "=" * 70)
print("B-2: LINK AFTER KERNEL TRANSITIONS")
print("Question: Do specific kernel transitions predict LINK?")
print("=" * 70)

# Look at trigrams: kernel1 -> kernel2 -> LINK?
transition_link = Counter()  # (k1, k2) -> count of LINK after
transition_total = Counter()  # (k1, k2) -> total count

# Find consecutive kernel tokens
kernel_positions = [(i, t['kernel']) for i, t in enumerate(token_data) if t['kernel']]

for i in range(len(kernel_positions) - 1):
    pos1, k1 = kernel_positions[i]
    pos2, k2 = kernel_positions[i + 1]

    # Only count if adjacent or near-adjacent (within 3 tokens)
    if pos2 - pos1 > 3:
        continue

    # Same folio check
    if token_data[pos1]['folio'] != token_data[pos2]['folio']:
        continue

    transition_total[(k1, k2)] += 1

    # Is there a LINK immediately after k2?
    if pos2 + 1 < len(token_data):
        if token_data[pos2 + 1]['is_link'] and token_data[pos2 + 1]['folio'] == token_data[pos2]['folio']:
            transition_link[(k1, k2)] += 1

print("\nP(LINK | kernel transition):")
print(f"{'Transition':<12} {'LINK After':<12} {'Total':<10} {'P(LINK)':<10} {'Ratio'}")
print("-" * 55)

b2_results = {}
for k1 in ['e', 'k', 'h']:
    for k2 in ['e', 'k', 'h']:
        trans = (k1, k2)
        total = transition_total[trans]
        link_count = transition_link[trans]
        p_link = link_count / total if total > 0 else 0
        ratio = p_link / base_p_link if base_p_link > 0 else 0

        b2_results[f"{k1}->{k2}"] = {
            'link_count': link_count,
            'total': total,
            'p_link': p_link,
            'ratio': ratio
        }

        if total >= 10:  # Only show meaningful ones
            print(f"{k1}->{k2}        {link_count:<12} {total:<10} {p_link:.4f}     {ratio:.2f}x")

# Key comparisons
print("\nKey comparisons:")
if b2_results['e->k']['total'] >= 10 and b2_results['k->e']['total'] >= 10:
    print(f"  e->k (escalation): {b2_results['e->k']['p_link']:.4f}")
    print(f"  k->e (recovery):   {b2_results['k->e']['p_link']:.4f}")
    diff_ek = abs(b2_results['e->k']['p_link'] - b2_results['k->e']['p_link'])
    print(f"  Difference: {diff_ek:.4f} ({diff_ek/base_p_link*100:.1f}% of baseline)")

# Max effect
max_trans_effect = max(abs(r['ratio'] - 1.0) for r in b2_results.values() if r['total'] >= 10)
print(f"\nMax transition effect: {max_trans_effect:.2%}")

b2_verdict = "SIGNAL" if max_trans_effect > 0.10 else "WEAK/NONE"
print(f"B-2 VERDICT: {b2_verdict}")

# ==========================================================================
# B-3: LINK VS POSITION-IN-FOLIO
# ==========================================================================

print("\n" + "=" * 70)
print("B-3: LINK VS POSITION-IN-FOLIO")
print("Question: Does LINK cluster early/middle/late in folios?")
print("=" * 70)

# Group by folio
folio_tokens = defaultdict(list)
for t in token_data:
    folio_tokens[t['folio']].append(t)

# For each token, compute relative position (0-1)
position_link = {'early': 0, 'middle': 0, 'late': 0}
position_total = {'early': 0, 'middle': 0, 'late': 0}

link_positions = []
all_positions = []

for folio, tokens in folio_tokens.items():
    n = len(tokens)
    if n < 10:  # Skip tiny folios
        continue

    for i, t in enumerate(tokens):
        rel_pos = i / n
        all_positions.append(rel_pos)

        if rel_pos < 0.33:
            zone = 'early'
        elif rel_pos < 0.67:
            zone = 'middle'
        else:
            zone = 'late'

        position_total[zone] += 1
        if t['is_link']:
            position_link[zone] += 1
            link_positions.append(rel_pos)

print("\nLINK by position zone:")
print(f"{'Zone':<10} {'LINK':<10} {'Total':<10} {'P(LINK)':<10} {'Ratio'}")
print("-" * 50)

b3_results = {}
for zone in ['early', 'middle', 'late']:
    total = position_total[zone]
    link_count = position_link[zone]
    p_link = link_count / total if total > 0 else 0
    ratio = p_link / base_p_link if base_p_link > 0 else 0

    b3_results[zone] = {
        'link_count': link_count,
        'total': total,
        'p_link': p_link,
        'ratio': ratio
    }

    print(f"{zone:<10} {link_count:<10} {total:<10} {p_link:.4f}     {ratio:.2f}x")

# Statistical test
early_mid_late = [position_link['early'], position_link['middle'], position_link['late']]
early_mid_late_total = [position_total['early'], position_total['middle'], position_total['late']]
chi2_pos, p_pos, _, _ = chi2_contingency([early_mid_late,
                                           [t - l for t, l in zip(early_mid_late_total, early_mid_late)]])
print(f"\nChi-square test: chi2={chi2_pos:.2f}, p={p_pos:.6f}")

# Effect size
max_pos_effect = max(abs(r['ratio'] - 1.0) for r in b3_results.values())
print(f"Max position effect: {max_pos_effect:.2%}")

# Gradient test
mean_link_pos = np.mean(link_positions)
mean_all_pos = np.mean(all_positions)
print(f"\nMean position of LINK tokens: {mean_link_pos:.3f}")
print(f"Mean position of all tokens: {mean_all_pos:.3f}")
print(f"LINK position bias: {mean_link_pos - mean_all_pos:+.3f}")

b3_verdict = "SIGNAL" if max_pos_effect > 0.10 and p_pos < 0.01 else "WEAK/NONE"
print(f"\nB-3 VERDICT: {b3_verdict}")

# ==========================================================================
# B-4: LINK CLUSTERING VS SECTIONS
# ==========================================================================

print("\n" + "=" * 70)
print("B-4: LINK CLUSTERING VS SECTIONS")
print("Question: Do sections encode waiting differently?")
print("=" * 70)

# Get section from folio (using existing section mapping)
def get_section(folio):
    """Extract section from folio name."""
    if not folio:
        return 'unknown'
    # Section is typically encoded in folio prefix or mapped
    # For Currier B, sections are H, S, B, C, etc.
    # This is a simplified extraction
    if 'f' in folio:
        # Try to map based on folio ranges (approximate)
        try:
            num = int(''.join(c for c in folio if c.isdigit())[:3])
            if num <= 57:
                return 'H'  # Herbal
            elif num <= 67:
                return 'S'  # Stars
            elif num <= 86:
                return 'B'  # Biological
            else:
                return 'C'  # Cosmological/Other
        except:
            return 'unknown'
    return 'unknown'

section_link = Counter()
section_total = Counter()

for t in token_data:
    section = get_section(t['folio'])
    section_total[section] += 1
    if t['is_link']:
        section_link[section] += 1

print("\nLINK density by section:")
print(f"{'Section':<10} {'LINK':<10} {'Total':<10} {'Density':<10} {'Ratio'}")
print("-" * 50)

b4_results = {}
for section in sorted(section_total.keys()):
    if section == 'unknown':
        continue
    total = section_total[section]
    link_count = section_link[section]
    density = link_count / total if total > 0 else 0
    ratio = density / base_p_link if base_p_link > 0 else 0

    b4_results[section] = {
        'link_count': link_count,
        'total': total,
        'density': density,
        'ratio': ratio
    }

    print(f"{section:<10} {link_count:<10} {total:<10} {density:.4f}     {ratio:.2f}x")

# Max section effect
if b4_results:
    max_section_effect = max(abs(r['ratio'] - 1.0) for r in b4_results.values())
    print(f"\nMax section effect: {max_section_effect:.2%}")

    # Compare to AZC (which has 7.6% LINK)
    print(f"\nFor reference: AZC has 7.6% LINK density (highest in manuscript)")
    print(f"Currier B baseline: {base_p_link*100:.1f}%")
else:
    max_section_effect = 0

b4_verdict = "SIGNAL" if max_section_effect > 0.10 else "WEAK/NONE"
print(f"\nB-4 VERDICT: {b4_verdict}")

# ==========================================================================
# SUMMARY AND HARD STOP EVALUATION
# ==========================================================================

print("\n" + "=" * 70)
print("DIRECTION B: SUMMARY")
print("=" * 70)

verdicts = {
    'B-1 (kernel conditioning)': b1_verdict,
    'B-2 (transition conditioning)': b2_verdict,
    'B-3 (position conditioning)': b3_verdict,
    'B-4 (section conditioning)': b4_verdict
}

print("\nTest Results:")
for test, verdict in verdicts.items():
    print(f"  {test}: {verdict}")

signals = sum(1 for v in verdicts.values() if v == "SIGNAL")
print(f"\nSignals found: {signals}/4")

# Hard stop evaluation
print("\n" + "-" * 70)
print("HARD STOP EVALUATION")
print("-" * 70)

# Condition 1: No kernel OR positional conditioning
no_kernel_cond = b1_verdict == "WEAK/NONE" and b2_verdict == "WEAK/NONE"
no_pos_cond = b3_verdict == "WEAK/NONE"

if no_kernel_cond and no_pos_cond:
    print("STOP CONDITION 1 MET: No kernel OR positional conditioning")
    print("CONCLUSION: Waiting is purely human-managed")
    overall_verdict = "HUMAN_MANAGED"
elif signals == 0:
    print("All effects weak (<10%)")
    print("CONCLUSION: LINK is texture, not mechanism")
    overall_verdict = "TEXTURE_ONLY"
else:
    print(f"Found {signals} signal(s)")
    if signals <= 2:
        print("CONCLUSION: 1-2 Tier 2 constraints, then close")
        overall_verdict = "LIMITED_STRUCTURE"
    else:
        print("CONCLUSION: Significant LINK structure exists")
        overall_verdict = "STRUCTURED"

print(f"\nOVERALL VERDICT: {overall_verdict}")

# Effect size summary
print("\n" + "-" * 70)
print("EFFECT SIZES")
print("-" * 70)
print(f"B-1 (kernel): {max_effect:.1%}")
print(f"B-2 (transition): {max_trans_effect:.1%}")
print(f"B-3 (position): {max_pos_effect:.1%}")
print(f"B-4 (section): {max_section_effect:.1%}")

max_overall = max(max_effect, max_trans_effect, max_pos_effect, max_section_effect)
print(f"\nLargest effect: {max_overall:.1%}")

# ==========================================================================
# CONSTRAINTS TO ADD (if any)
# ==========================================================================

print("\n" + "=" * 70)
print("CONSTRAINTS")
print("=" * 70)

constraints = []

if b1_verdict == "SIGNAL":
    constraints.append(f"LINK kernel conditioning: P(LINK|prev=k)={b1_results['k']['p_link']:.3f}, P(LINK|prev=e)={b1_results['e']['p_link']:.3f}; max effect {max_effect:.1%}")

if b3_verdict == "SIGNAL":
    constraints.append(f"LINK positional bias: {b3_results}")

if b4_verdict == "SIGNAL":
    constraints.append(f"LINK section variation: max effect {max_section_effect:.1%}")

if constraints:
    print("\nProposed Tier 2 constraints:")
    for i, c in enumerate(constraints, 1):
        print(f"  {i}. {c}")
else:
    print("\nNo constraints to add (effects too weak or absent)")

print("\n" + "=" * 70)
print("DIRECTION B: CLOSED")
print("=" * 70)

# Save results
results = {
    'b1_kernel_conditioning': {
        'results': b1_results,
        'max_effect': max_effect,
        'z_score': z_score,
        'verdict': b1_verdict
    },
    'b2_transition_conditioning': {
        'results': b2_results,
        'max_effect': max_trans_effect,
        'verdict': b2_verdict
    },
    'b3_position_conditioning': {
        'results': b3_results,
        'max_effect': max_pos_effect,
        'p_value': p_pos,
        'verdict': b3_verdict
    },
    'b4_section_conditioning': {
        'results': b4_results,
        'max_effect': max_section_effect,
        'verdict': b4_verdict
    },
    'overall_verdict': overall_verdict,
    'signals_found': signals,
    'constraints': constraints
}

os.makedirs('phases/LINK_temporal_state_space', exist_ok=True)
with open('phases/LINK_temporal_state_space/link_temporal_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to phases/LINK_temporal_state_space/link_temporal_results.json")

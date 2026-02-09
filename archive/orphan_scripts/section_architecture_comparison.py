#!/usr/bin/env python3
"""
Section-Specific Record Architecture Comparison

Investigates whether Currier A sections (H, P, T) have fundamentally
different registry architectures or just different content with same structure.

Metrics compared:
1. Record length distribution
2. PP diversity
3. RI density and distribution
4. Paragraph structure (WITH-RI vs WITHOUT-RI)
5. PREFIX profiles
6. MIDDLE vocabulary overlap
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("SECTION-SPECIFIC RECORD ARCHITECTURE COMPARISON")
print("="*70)

# Build paragraph data with section info
paragraphs = []
current_folio = None
current_para = []
current_line = None
current_section = None

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'section': current_section,
                'tokens': [t.word for t in current_para]
            })
        current_folio = token.folio
        current_section = token.section
        current_para = [token]
        current_line = token.line
        continue

    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'section': current_section,
                'tokens': [t.word for t in current_para]
            })
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'section': current_section,
        'tokens': [t.word for t in current_para]
    })

# Group by section
section_paragraphs = defaultdict(list)
section_folios = defaultdict(set)
for para in paragraphs:
    section_paragraphs[para['section']].append(para)
    section_folios[para['section']].add(para['folio'])

print(f"\nSection distribution:")
for section in sorted(section_paragraphs.keys()):
    n_para = len(section_paragraphs[section])
    n_folio = len(section_folios[section])
    print(f"  {section}: {n_para} paragraphs across {n_folio} folios")

# =========================================================================
# METRIC 1: Record Length Distribution
# =========================================================================
print("\n" + "="*70)
print("METRIC 1: RECORD LENGTH DISTRIBUTION")
print("="*70)

section_lengths = {}
for section, paras in section_paragraphs.items():
    lengths = [len(p['tokens']) for p in paras]
    section_lengths[section] = lengths
    print(f"\n{section}:")
    print(f"  Mean: {np.mean(lengths):.1f} tokens")
    print(f"  Median: {np.median(lengths):.1f}")
    print(f"  Std: {np.std(lengths):.1f}")
    print(f"  Range: {min(lengths)} - {max(lengths)}")

# Statistical comparison H vs P
if 'H' in section_lengths and 'P' in section_lengths:
    t_stat, p_val = stats.ttest_ind(section_lengths['H'], section_lengths['P'])
    print(f"\nH vs P length comparison: t={t_stat:.3f}, p={p_val:.4f}")
    if p_val < 0.05:
        longer = 'H' if np.mean(section_lengths['H']) > np.mean(section_lengths['P']) else 'P'
        print(f"  ** SIGNIFICANT: {longer} has longer records **")

# =========================================================================
# METRIC 2: PP Diversity (unique MIDDLEs per record)
# =========================================================================
print("\n" + "="*70)
print("METRIC 2: PP DIVERSITY (Unique MIDDLEs per record)")
print("="*70)

section_diversity = {}
for section, paras in section_paragraphs.items():
    diversities = []
    for para in paras:
        middles = set()
        for token in para['tokens']:
            try:
                m = morph.extract(token)
                if m.middle:
                    middles.add(m.middle)
            except:
                pass
        diversities.append(len(middles))

    section_diversity[section] = diversities
    print(f"\n{section}:")
    print(f"  Mean unique MIDDLEs: {np.mean(diversities):.1f}")
    print(f"  Median: {np.median(diversities):.1f}")

    # Diversity ratio (unique / total)
    mean_length = np.mean([len(p['tokens']) for p in paras])
    diversity_ratio = np.mean(diversities) / mean_length if mean_length > 0 else 0
    print(f"  Diversity ratio: {diversity_ratio:.2f}")

# =========================================================================
# METRIC 3: RI Density and Distribution
# =========================================================================
print("\n" + "="*70)
print("METRIC 3: RI DENSITY AND DISTRIBUTION")
print("="*70)

def get_ri_rate(para):
    """Calculate RI token rate in paragraph."""
    tokens = para['tokens']
    if len(tokens) < 4:
        return 0, 0, 0

    initial_ri = tokens[:3]
    final_ri = tokens[-3:]

    # Count tokens that look like RI (certain PREFIX patterns)
    ri_prefixes = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh', 'ct'}

    initial_count = 0
    final_count = 0

    for token in initial_ri:
        try:
            m = morph.extract(token)
            if m.prefix in ri_prefixes:
                initial_count += 1
        except:
            pass

    for token in final_ri:
        try:
            m = morph.extract(token)
            if m.prefix in ri_prefixes:
                final_count += 1
        except:
            pass

    total = len(tokens)
    return initial_count / 3, final_count / 3, (initial_count + final_count) / 6

section_ri = {}
for section, paras in section_paragraphs.items():
    initial_rates = []
    final_rates = []
    total_rates = []

    for para in paras:
        init_r, final_r, total_r = get_ri_rate(para)
        initial_rates.append(init_r)
        final_rates.append(final_r)
        total_rates.append(total_r)

    section_ri[section] = {
        'initial': initial_rates,
        'final': final_rates,
        'total': total_rates
    }

    print(f"\n{section}:")
    print(f"  INITIAL zone RI rate: {np.mean(initial_rates)*100:.1f}%")
    print(f"  FINAL zone RI rate: {np.mean(final_rates)*100:.1f}%")
    print(f"  Combined RI rate: {np.mean(total_rates)*100:.1f}%")

    # Initial/Final asymmetry
    asymmetry = np.mean(initial_rates) / np.mean(final_rates) if np.mean(final_rates) > 0 else float('inf')
    print(f"  INITIAL/FINAL asymmetry: {asymmetry:.2f}x")

# =========================================================================
# METRIC 4: Paragraph Structure (WITH-RI vs WITHOUT-RI)
# =========================================================================
print("\n" + "="*70)
print("METRIC 4: PARAGRAPH STRUCTURE (WITH-RI vs WITHOUT-RI)")
print("="*70)

def is_with_ri(para):
    """Check if paragraph starts with RI tokens."""
    tokens = para['tokens']
    if len(tokens) < 1:
        return False

    first_token = tokens[0]
    try:
        m = morph.extract(first_token)
        # WITH-RI if first token has RI-associated prefix
        ri_prefixes = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}
        return m.prefix in ri_prefixes
    except:
        return False

section_structure = {}
for section, paras in section_paragraphs.items():
    with_ri = sum(1 for p in paras if is_with_ri(p))
    without_ri = len(paras) - with_ri

    section_structure[section] = {
        'with_ri': with_ri,
        'without_ri': without_ri,
        'with_ri_rate': with_ri / len(paras) if paras else 0
    }

    print(f"\n{section}:")
    print(f"  WITH-RI: {with_ri} ({100*with_ri/len(paras):.1f}%)")
    print(f"  WITHOUT-RI: {without_ri} ({100*without_ri/len(paras):.1f}%)")

# Chi-square test for structure difference
if 'H' in section_structure and 'P' in section_structure:
    h = section_structure['H']
    p = section_structure['P']

    contingency = [[h['with_ri'], h['without_ri']],
                   [p['with_ri'], p['without_ri']]]

    chi2, pval, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nH vs P structure chi-square: chi2={chi2:.2f}, p={pval:.4f}")
    if pval < 0.05:
        print(f"  ** SIGNIFICANT: Sections have different WITH-RI/WITHOUT-RI ratios **")

# =========================================================================
# METRIC 5: PREFIX Profiles
# =========================================================================
print("\n" + "="*70)
print("METRIC 5: PREFIX PROFILES")
print("="*70)

section_prefixes = {}
for section, paras in section_paragraphs.items():
    prefix_counts = Counter()
    total_tokens = 0

    for para in paras:
        for token in para['tokens']:
            try:
                m = morph.extract(token)
                if m.prefix:
                    prefix_counts[m.prefix] += 1
                    total_tokens += 1
            except:
                pass

    section_prefixes[section] = {
        'counts': prefix_counts,
        'total': total_tokens
    }

# Compare top prefixes across sections
print("\nTop PREFIX rates by section:")
all_prefixes = set()
for sp in section_prefixes.values():
    all_prefixes.update(sp['counts'].keys())

# Get top 10 overall prefixes
overall_counts = Counter()
for sp in section_prefixes.values():
    overall_counts.update(sp['counts'])

top_prefixes = [p for p, _ in overall_counts.most_common(12)]

print(f"\n{'PREFIX':<8}", end="")
for section in sorted(section_prefixes.keys()):
    print(f"{section:>10}", end="")
print()
print("-" * 40)

for prefix in top_prefixes:
    print(f"{prefix:<8}", end="")
    for section in sorted(section_prefixes.keys()):
        sp = section_prefixes[section]
        rate = sp['counts'].get(prefix, 0) / sp['total'] * 100 if sp['total'] > 0 else 0
        print(f"{rate:>9.1f}%", end="")
    print()

# Identify section-distinctive prefixes
print("\nSection-distinctive PREFIXes (>2x enrichment vs others):")
for section in sorted(section_prefixes.keys()):
    sp = section_prefixes[section]
    other_total = sum(section_prefixes[s]['total'] for s in section_prefixes if s != section)
    other_counts = Counter()
    for s in section_prefixes:
        if s != section:
            other_counts.update(section_prefixes[s]['counts'])

    distinctive = []
    for prefix in sp['counts']:
        if sp['counts'][prefix] >= 5:  # Minimum count
            section_rate = sp['counts'][prefix] / sp['total']
            other_rate = other_counts.get(prefix, 0) / other_total if other_total > 0 else 0
            if other_rate > 0:
                ratio = section_rate / other_rate
                if ratio > 2.0:
                    distinctive.append((prefix, ratio, sp['counts'][prefix]))

    distinctive.sort(key=lambda x: -x[1])
    if distinctive:
        print(f"\n  {section}: ", end="")
        for prefix, ratio, count in distinctive[:5]:
            print(f"{prefix}({ratio:.1f}x, n={count}) ", end="")
        print()

# =========================================================================
# METRIC 6: MIDDLE Vocabulary Overlap
# =========================================================================
print("\n" + "="*70)
print("METRIC 6: MIDDLE VOCABULARY OVERLAP")
print("="*70)

section_middles = {}
for section, paras in section_paragraphs.items():
    middles = set()
    for para in paras:
        for token in para['tokens']:
            try:
                m = morph.extract(token)
                if m.middle:
                    middles.add(m.middle)
            except:
                pass
    section_middles[section] = middles

print("\nMIDDLE vocabulary sizes:")
for section in sorted(section_middles.keys()):
    print(f"  {section}: {len(section_middles[section])} unique MIDDLEs")

# Pairwise Jaccard
sections = sorted(section_middles.keys())
print("\nPairwise Jaccard similarity:")
for i, s1 in enumerate(sections):
    for s2 in sections[i+1:]:
        intersection = section_middles[s1] & section_middles[s2]
        union = section_middles[s1] | section_middles[s2]
        jaccard = len(intersection) / len(union) if union else 0
        print(f"  {s1}-{s2}: {jaccard:.3f} ({len(intersection)} shared)")

# Section-exclusive MIDDLEs
print("\nSection-exclusive MIDDLEs:")
for section in sections:
    exclusive = section_middles[section] - set().union(*[section_middles[s] for s in sections if s != section])
    print(f"  {section}: {len(exclusive)} exclusive MIDDLEs")
    if exclusive and len(exclusive) <= 10:
        print(f"    {sorted(exclusive)}")

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: ARCHITECTURAL DIFFERENCES")
print("="*70)

print("""
Comparing sections across 6 structural dimensions:
""")

# Build summary table
summary = {}
for section in ['H', 'P', 'T']:
    if section not in section_paragraphs:
        continue

    paras = section_paragraphs[section]
    lengths = [len(p['tokens']) for p in paras]

    summary[section] = {
        'n_paragraphs': len(paras),
        'n_folios': len(section_folios[section]),
        'mean_length': np.mean(lengths),
        'with_ri_rate': section_structure[section]['with_ri_rate'],
        'n_middles': len(section_middles[section])
    }

print(f"{'Metric':<25}", end="")
for section in ['H', 'P', 'T']:
    if section in summary:
        print(f"{section:>12}", end="")
print()
print("-" * 55)

metrics = [
    ('Paragraphs', 'n_paragraphs', '{:.0f}'),
    ('Folios', 'n_folios', '{:.0f}'),
    ('Mean record length', 'mean_length', '{:.1f}'),
    ('WITH-RI rate', 'with_ri_rate', '{:.1%}'),
    ('Unique MIDDLEs', 'n_middles', '{:.0f}')
]

for label, key, fmt in metrics:
    print(f"{label:<25}", end="")
    for section in ['H', 'P', 'T']:
        if section in summary:
            val = summary[section][key]
            print(f"{fmt.format(val):>12}", end="")
    print()

print("""
INTERPRETATION:

If sections show DIFFERENT structural profiles:
  → Different registry modes for different content domains
  → Architecture adapts to material type

If sections show SIMILAR structural profiles:
  → Same registry architecture, different content
  → Universal organizational principle
""")

# Save results
output = {
    'section_summary': summary,
    'section_lengths': {s: {'mean': float(np.mean(l)), 'std': float(np.std(l))}
                        for s, l in section_lengths.items()},
    'section_structure': section_structure,
    'vocabulary_overlap': {f"{s1}-{s2}": len(section_middles[s1] & section_middles[s2]) / len(section_middles[s1] | section_middles[s2])
                           for i, s1 in enumerate(sections) for s2 in sections[i+1:]}
}

output_path = Path(__file__).parent.parent / 'results' / 'section_architecture_comparison.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")

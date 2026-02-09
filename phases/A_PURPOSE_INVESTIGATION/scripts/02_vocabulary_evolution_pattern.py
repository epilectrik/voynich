"""
02_vocabulary_evolution_pattern.py - Test if A is a vocabulary evolution log

Hypothesis H5: A is a chronological log of vocabulary development.
New words were logged in A as the system evolved.

Test: Does A folio order correlate with vocabulary novelty?

If A is a vocabulary log:
- Novel vocabulary rate should show temporal pattern
- Earlier folios should have higher shared-with-B rate (foundational)
- Later folios should have higher RI rate (specialized extensions)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
from scipy import stats
import json
import numpy as np

tx = Transcript()
morph = Morphology()

# Get all tokens
a_tokens = list(tx.currier_a())
b_tokens = list(tx.currier_b())

print(f"Currier A tokens: {len(a_tokens)}")
print(f"Currier B tokens: {len(b_tokens)}")

# Build B vocabulary (the "operational" set)
b_middles = set()
for t in b_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

print(f"B unique MIDDLEs: {len(b_middles)}")

# ============================================================
# Build A folio vocabulary with ordering
# ============================================================
print("\n" + "="*70)
print("BUILDING A FOLIO VOCABULARY WITH ORDERING")
print("="*70)

# Get A folios in manuscript order
a_folio_data = defaultdict(lambda: {'middles': set(), 'tokens': []})

for t in a_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        a_folio_data[t.folio]['middles'].add(m.middle)
        a_folio_data[t.folio]['tokens'].append(t)

# Sort folios by manuscript order (alphabetically works for folio names like f1r, f2v, etc.)
# But we need numeric sorting
def folio_sort_key(folio):
    """Convert folio name to sortable tuple."""
    import re
    match = re.match(r'f(\d+)([rv]?)(\d*)', folio)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (999, 0, 0)

a_folios_ordered = sorted(a_folio_data.keys(), key=folio_sort_key)
print(f"A folios in order: {len(a_folios_ordered)}")
print(f"First 5: {a_folios_ordered[:5]}")
print(f"Last 5: {a_folios_ordered[-5:]}")

# ============================================================
# Compute cumulative vocabulary and novelty rate
# ============================================================
print("\n" + "="*70)
print("VOCABULARY EVOLUTION ANALYSIS")
print("="*70)

cumulative_vocab = set()
evolution_data = []

for i, folio in enumerate(a_folios_ordered):
    folio_vocab = a_folio_data[folio]['middles']

    # Novel MIDDLEs (not seen in previous folios)
    novel = folio_vocab - cumulative_vocab
    novel_rate = len(novel) / len(folio_vocab) if folio_vocab else 0

    # Shared with B (PP vocabulary)
    shared_with_b = folio_vocab & b_middles
    shared_rate = len(shared_with_b) / len(folio_vocab) if folio_vocab else 0

    # RI vocabulary (not in B)
    ri_vocab = folio_vocab - b_middles
    ri_rate = len(ri_vocab) / len(folio_vocab) if folio_vocab else 0

    evolution_data.append({
        'folio': folio,
        'order': i,
        'vocab_size': len(folio_vocab),
        'novel_count': len(novel),
        'novel_rate': novel_rate,
        'cumulative_vocab': len(cumulative_vocab),
        'shared_with_b': len(shared_with_b),
        'shared_rate': shared_rate,
        'ri_count': len(ri_vocab),
        'ri_rate': ri_rate
    })

    cumulative_vocab |= folio_vocab

print(f"\nFinal cumulative A vocabulary: {len(cumulative_vocab)} MIDDLEs")

# ============================================================
# Test for temporal patterns
# ============================================================
print("\n" + "="*70)
print("TEMPORAL PATTERN TESTS")
print("="*70)

orders = [d['order'] for d in evolution_data]
novel_rates = [d['novel_rate'] for d in evolution_data]
shared_rates = [d['shared_rate'] for d in evolution_data]
ri_rates = [d['ri_rate'] for d in evolution_data]

# Correlation: order vs novelty rate
# If A is a log, early folios should have HIGH novelty (everything is new)
# and later folios should have LOWER novelty (vocabulary saturates)
corr_novelty, p_novelty = stats.spearmanr(orders, novel_rates)
print(f"\nNovelty rate vs folio order:")
print(f"  Spearman rho: {corr_novelty:.3f}")
print(f"  p-value: {p_novelty:.4f}")
if corr_novelty < -0.3 and p_novelty < 0.01:
    print("  -> Significant DECREASE in novelty over time (consistent with log)")
elif corr_novelty > 0.3 and p_novelty < 0.01:
    print("  -> Significant INCREASE in novelty over time (inconsistent with log)")
else:
    print("  -> No significant temporal pattern")

# Correlation: order vs shared-with-B rate
# If early folios are foundational, they should have HIGHER shared rate
corr_shared, p_shared = stats.spearmanr(orders, shared_rates)
print(f"\nShared-with-B rate vs folio order:")
print(f"  Spearman rho: {corr_shared:.3f}")
print(f"  p-value: {p_shared:.4f}")
if corr_shared < -0.3 and p_shared < 0.01:
    print("  -> Early folios have MORE shared vocabulary (foundational)")
elif corr_shared > 0.3 and p_shared < 0.01:
    print("  -> Late folios have MORE shared vocabulary (unexpected)")
else:
    print("  -> No significant temporal pattern")

# Correlation: order vs RI rate
# If later folios are specialized extensions, RI rate should INCREASE
corr_ri, p_ri = stats.spearmanr(orders, ri_rates)
print(f"\nRI rate vs folio order:")
print(f"  Spearman rho: {corr_ri:.3f}")
print(f"  p-value: {p_ri:.4f}")
if corr_ri > 0.3 and p_ri < 0.01:
    print("  -> RI rate INCREASES over time (consistent with log of extensions)")
elif corr_ri < -0.3 and p_ri < 0.01:
    print("  -> RI rate DECREASES over time (inconsistent with log)")
else:
    print("  -> No significant temporal pattern")

# ============================================================
# Early vs Late comparison
# ============================================================
print("\n" + "="*70)
print("EARLY vs LATE A FOLIOS")
print("="*70)

n_folios = len(evolution_data)
early = evolution_data[:n_folios//3]
late = evolution_data[-n_folios//3:]

early_shared = np.mean([d['shared_rate'] for d in early])
late_shared = np.mean([d['shared_rate'] for d in late])

early_ri = np.mean([d['ri_rate'] for d in early])
late_ri = np.mean([d['ri_rate'] for d in late])

early_novelty = np.mean([d['novel_rate'] for d in early])
late_novelty = np.mean([d['novel_rate'] for d in late])

print(f"\nEarly A folios (first third, n={len(early)}):")
print(f"  Mean shared-with-B rate: {early_shared:.1%}")
print(f"  Mean RI rate: {early_ri:.1%}")
print(f"  Mean novelty rate: {early_novelty:.1%}")

print(f"\nLate A folios (last third, n={len(late)}):")
print(f"  Mean shared-with-B rate: {late_shared:.1%}")
print(f"  Mean RI rate: {late_ri:.1%}")
print(f"  Mean novelty rate: {late_novelty:.1%}")

# Statistical tests
early_shared_vals = [d['shared_rate'] for d in early]
late_shared_vals = [d['shared_rate'] for d in late]
t_shared, p_t_shared = stats.ttest_ind(early_shared_vals, late_shared_vals)

print(f"\nEarly vs Late shared rate t-test:")
print(f"  t-statistic: {t_shared:.3f}")
print(f"  p-value: {p_t_shared:.4f}")

early_ri_vals = [d['ri_rate'] for d in early]
late_ri_vals = [d['ri_rate'] for d in late]
t_ri, p_t_ri = stats.ttest_ind(early_ri_vals, late_ri_vals)

print(f"\nEarly vs Late RI rate t-test:")
print(f"  t-statistic: {t_ri:.3f}")
print(f"  p-value: {p_t_ri:.4f}")

# ============================================================
# Section analysis (do sections show different patterns?)
# ============================================================
print("\n" + "="*70)
print("SECTION-LEVEL ANALYSIS")
print("="*70)

# Get section for each A folio
a_folio_sections = {}
for t in a_tokens:
    if t.folio not in a_folio_sections:
        a_folio_sections[t.folio] = t.section

section_data = defaultdict(list)
for d in evolution_data:
    section = a_folio_sections.get(d['folio'], 'Unknown')
    section_data[section].append(d)

print("\nBy section:")
for section in sorted(section_data.keys()):
    data = section_data[section]
    mean_shared = np.mean([d['shared_rate'] for d in data])
    mean_ri = np.mean([d['ri_rate'] for d in data])
    mean_novelty = np.mean([d['novel_rate'] for d in data])
    print(f"  {section}: {len(data)} folios, shared={mean_shared:.1%}, RI={mean_ri:.1%}, novelty={mean_novelty:.1%}")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY: VOCABULARY EVOLUTION HYPOTHESIS")
print("="*70)

supports_log = 0
contradicts_log = 0

# Check predictions
if corr_novelty < -0.2 and p_novelty < 0.05:
    print("+ Novelty decreases over time (consistent with log)")
    supports_log += 1
elif corr_novelty > 0.2 and p_novelty < 0.05:
    print("- Novelty increases over time (inconsistent with log)")
    contradicts_log += 1
else:
    print("? No clear novelty pattern")

if early_shared > late_shared and p_t_shared < 0.05:
    print("+ Early folios have more foundational (shared) vocabulary")
    supports_log += 1
elif late_shared > early_shared and p_t_shared < 0.05:
    print("- Late folios have more shared vocabulary (inconsistent)")
    contradicts_log += 1
else:
    print("? No clear early/late shared pattern")

if corr_ri > 0.2 and p_ri < 0.05:
    print("+ RI rate increases over time (extensions logged later)")
    supports_log += 1
elif corr_ri < -0.2 and p_ri < 0.05:
    print("- RI rate decreases over time (inconsistent)")
    contradicts_log += 1
else:
    print("? No clear RI evolution pattern")

print(f"\nScore: {supports_log} supporting, {contradicts_log} contradicting")

if supports_log >= 2 and contradicts_log == 0:
    verdict = "SUPPORTS"
    print("\nVerdict: SUPPORTS vocabulary evolution hypothesis")
elif contradicts_log >= 2:
    verdict = "CONTRADICTS"
    print("\nVerdict: CONTRADICTS vocabulary evolution hypothesis")
else:
    verdict = "INCONCLUSIVE"
    print("\nVerdict: INCONCLUSIVE - no clear temporal pattern")

# Save results
output = {
    'evolution_data': evolution_data,
    'correlations': {
        'novelty_vs_order': {'rho': float(corr_novelty), 'p': float(p_novelty)},
        'shared_vs_order': {'rho': float(corr_shared), 'p': float(p_shared)},
        'ri_vs_order': {'rho': float(corr_ri), 'p': float(p_ri)}
    },
    'early_late_comparison': {
        'early_shared': float(early_shared),
        'late_shared': float(late_shared),
        'early_ri': float(early_ri),
        'late_ri': float(late_ri),
        't_shared': float(t_shared),
        'p_shared': float(p_t_shared)
    },
    'verdict': verdict
}

with open('C:/git/voynich/phases/A_PURPOSE_INVESTIGATION/results/vocabulary_evolution_pattern.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to vocabulary_evolution_pattern.json")

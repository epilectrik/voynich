"""
03_label_folio_recipe_cluster.py - Test if label-rich A folios connect to specific B recipe clusters

Question: Do A folios with high label density connect to B folios with specific Brunschwig recipe affinity?

Method:
1. Identify A folios with high label count (from PHARMA_LABEL_DECODING)
2. Trace label PP bases to B folio appearances
3. Compute B folio concentration for label-rich vs label-poor A folios
4. Test if label-rich A folios -> concentrated B folio connections
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 3: LABEL-RICH FOLIOS -> B FOLIO CONCENTRATION")
print("="*70)

# ============================================================
# STEP 1: COUNT LABELS PER A FOLIO
# ============================================================
print("\n--- Step 1: Loading Label Counts per Folio ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

folio_label_count = Counter()
folio_labels = defaultdict(list)

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        # Count all labels
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            folio_label_count[folio] += 1
            folio_labels[folio].append(jar)

        for item in group.get('roots', []) + group.get('leaves', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                folio_label_count[folio] += 1
                folio_labels[folio].append(token)

print(f"Folios with labels: {len(folio_label_count)}")
print(f"Total labels: {sum(folio_label_count.values())}")

# Show distribution
print("\nLabel count distribution:")
for folio, count in folio_label_count.most_common():
    print(f"  {folio}: {count} labels")

# ============================================================
# STEP 2: EXTRACT PP BASES FROM LABELS
# ============================================================
print("\n--- Step 2: Extracting Label PP Bases ---")

folio_pp_bases = defaultdict(set)

for folio, labels in folio_labels.items():
    for label in labels:
        m = morph.extract(label)
        if m and m.middle:
            # PP base is the core MIDDLE
            folio_pp_bases[folio].add(m.middle)

for folio in sorted(folio_pp_bases.keys())[:5]:
    print(f"  {folio}: {len(folio_pp_bases[folio])} unique PP bases")

# ============================================================
# STEP 3: MAP PP BASES TO B FOLIOS
# ============================================================
print("\n--- Step 3: Mapping PP Bases to B Folios ---")

# Build MIDDLE -> B folio mapping
middle_to_b_folios = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        middle_to_b_folios[m.middle][t.folio] += 1

print(f"Unique MIDDLEs in B: {len(middle_to_b_folios)}")

# For each A folio, find which B folios its label PP bases appear in
folio_b_connections = {}

for a_folio, pp_bases in folio_pp_bases.items():
    b_folio_counts = Counter()

    for pp in pp_bases:
        for b_folio, count in middle_to_b_folios.get(pp, {}).items():
            b_folio_counts[b_folio] += count

    folio_b_connections[a_folio] = {
        'pp_bases': len(pp_bases),
        'b_folios_reached': len(b_folio_counts),
        'total_b_tokens': sum(b_folio_counts.values()),
        'b_distribution': dict(b_folio_counts.most_common(10))
    }

# ============================================================
# STEP 4: CONCENTRATION ANALYSIS
# ============================================================
print("\n--- Step 4: B Folio Concentration Analysis ---")

# Compute concentration metric: Gini coefficient of B folio distribution
def gini_coefficient(values):
    """Compute Gini coefficient (0 = perfect equality, 1 = max inequality)"""
    if not values or sum(values) == 0:
        return 0
    values = sorted(values)
    n = len(values)
    cumsum = np.cumsum(values)
    return (2 * sum((i + 1) * v for i, v in enumerate(values)) - (n + 1) * cumsum[-1]) / (n * cumsum[-1])

# Split folios by label count (high vs low)
median_labels = np.median(list(folio_label_count.values()))
high_label_folios = [f for f, c in folio_label_count.items() if c >= median_labels]
low_label_folios = [f for f, c in folio_label_count.items() if c < median_labels]

print(f"\nMedian label count: {median_labels}")
print(f"High-label folios (>= median): {len(high_label_folios)}")
print(f"Low-label folios (< median): {len(low_label_folios)}")

# Compute Gini for each group
high_ginis = []
low_ginis = []

for a_folio in high_label_folios:
    conn = folio_b_connections.get(a_folio, {})
    b_dist = conn.get('b_distribution', {})
    if b_dist:
        g = gini_coefficient(list(b_dist.values()))
        high_ginis.append(g)

for a_folio in low_label_folios:
    conn = folio_b_connections.get(a_folio, {})
    b_dist = conn.get('b_distribution', {})
    if b_dist:
        g = gini_coefficient(list(b_dist.values()))
        low_ginis.append(g)

if high_ginis and low_ginis:
    mean_high_gini = np.mean(high_ginis)
    mean_low_gini = np.mean(low_ginis)

    print(f"\nB folio concentration (Gini coefficient):")
    print(f"  High-label folios: mean Gini = {mean_high_gini:.3f}")
    print(f"  Low-label folios: mean Gini = {mean_low_gini:.3f}")

    # T-test
    t, p_value = stats.ttest_ind(high_ginis, low_ginis)
    print(f"\nT-test: t = {t:.2f}, p = {p_value:.4f}")
    print(f"{'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'} difference")
else:
    mean_high_gini = 0
    mean_low_gini = 0
    t, p_value = 0, 1
    print("Insufficient data for Gini comparison")

# ============================================================
# STEP 5: B FOLIO REACH COMPARISON
# ============================================================
print("\n--- Step 5: B Folio Reach Comparison ---")

high_b_reach = [folio_b_connections.get(f, {}).get('b_folios_reached', 0) for f in high_label_folios]
low_b_reach = [folio_b_connections.get(f, {}).get('b_folios_reached', 0) for f in low_label_folios]

mean_high_reach = np.mean(high_b_reach) if high_b_reach else 0
mean_low_reach = np.mean(low_b_reach) if low_b_reach else 0

print(f"Mean B folios reached:")
print(f"  High-label folios: {mean_high_reach:.1f}")
print(f"  Low-label folios: {mean_low_reach:.1f}")

if high_b_reach and low_b_reach:
    t_reach, p_reach = stats.ttest_ind(high_b_reach, low_b_reach)
    print(f"\nT-test: t = {t_reach:.2f}, p = {p_reach:.4f}")
else:
    t_reach, p_reach = 0, 1

# ============================================================
# STEP 6: TOP CONNECTED B FOLIOS
# ============================================================
print("\n--- Step 6: Most Connected B Folios ---")

# Aggregate all B folio connections
all_b_connections = Counter()
for conn in folio_b_connections.values():
    for b_folio, count in conn.get('b_distribution', {}).items():
        all_b_connections[b_folio] += count

print("\nTop 10 B folios connected to label vocabulary:")
print(f"{'B Folio':<12} {'Token Count':<12} {'% of Total'}")
print("-" * 35)
total_b = sum(all_b_connections.values())
for b_folio, count in all_b_connections.most_common(10):
    pct = 100 * count / total_b if total_b > 0 else 0
    print(f"{b_folio:<12} {count:<12} {pct:.1f}%")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'label_folio_recipe_cluster',
    'question': 'Do label-rich A folios connect to specific B folio clusters?',
    'sample': {
        'a_folios_with_labels': len(folio_label_count),
        'total_labels': sum(folio_label_count.values()),
        'median_labels': float(median_labels),
        'high_label_folios': len(high_label_folios),
        'low_label_folios': len(low_label_folios)
    },
    'concentration': {
        'high_label_mean_gini': float(mean_high_gini),
        'low_label_mean_gini': float(mean_low_gini),
        't_statistic': float(t),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05)
    },
    'reach': {
        'high_label_mean_b_folios': float(mean_high_reach),
        'low_label_mean_b_folios': float(mean_low_reach),
        't_statistic': float(t_reach),
        'p_value': float(p_reach)
    },
    'top_b_folios': dict(all_b_connections.most_common(20)),
    'per_folio_connections': folio_b_connections
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results' / 'label_folio_recipe_cluster.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: LABEL-RICH FOLIOS -> B FOLIO CONCENTRATION")
print("="*70)

print(f"""
Do label-rich A folios connect to specific B folio clusters?

Sample:
  A folios with labels: {len(folio_label_count)}
  High-label folios: {len(high_label_folios)}
  Low-label folios: {len(low_label_folios)}

B Folio Concentration (Gini):
  High-label mean: {mean_high_gini:.3f}
  Low-label mean: {mean_low_gini:.3f}
  T-test p = {p_value:.4f}

B Folio Reach:
  High-label mean: {mean_high_reach:.1f} folios
  Low-label mean: {mean_low_reach:.1f} folios
  T-test p = {p_reach:.4f}

Verdict: {'CONCENTRATED CONNECTIONS' if p_value < 0.05 and mean_high_gini > mean_low_gini else 'NO SIGNIFICANT CONCENTRATION'}

{'Label-rich folios show more concentrated B folio connections.' if p_value < 0.05 and mean_high_gini > mean_low_gini else 'Label-rich folios do NOT show more concentrated B connections than label-poor folios.'}
""")

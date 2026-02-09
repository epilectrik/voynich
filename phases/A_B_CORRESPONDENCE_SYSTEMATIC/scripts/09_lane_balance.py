"""
09_lane_balance.py

Test lane balance prediction from A to B.

From C646-647: 20/99 PP MIDDLEs predict QO vs CHSH lane.
- k-rich MIDDLEs → QO lane
- e-rich MIDDLEs → CHSH lane

Hypothesis: A paragraphs with k-rich PP should match B paragraphs with high QO fraction.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("LANE BALANCE PREDICTION")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# Lane prefixes
QO_LANE = {'qo'}  # Escape lane
CHSH_LANE = {'ch', 'sh'}  # Phase lane

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

def build_paragraphs(tokens_iter):
    by_folio_line = defaultdict(list)
    for t in tokens_iter:
        if t.word and '*' not in t.word:
            by_folio_line[(t.folio, t.line)].append(t)

    paragraphs = []
    current_para = {'tokens': [], 'folio': None}
    current_folio = None

    for (folio, line) in sorted(by_folio_line.keys()):
        tokens = by_folio_line[(folio, line)]
        if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'tokens': [], 'folio': folio}
            current_folio = folio
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs

def compute_lane_profile(tokens):
    """Compute lane balance for a token list."""
    qo_count = 0
    chsh_count = 0
    k_count = 0
    e_count = 0
    total = 0

    for t in tokens:
        word = t.word if hasattr(t, 'word') else t['word']
        try:
            m = morph.extract(word)
            if m.prefix:
                total += 1
                if m.prefix in QO_LANE:
                    qo_count += 1
                elif m.prefix in CHSH_LANE:
                    chsh_count += 1

            if m.middle:
                if 'k' in m.middle:
                    k_count += 1
                if 'e' in m.middle:
                    e_count += 1
        except:
            pass

    return {
        'qo_rate': qo_count / total if total > 0 else 0,
        'chsh_rate': chsh_count / total if total > 0 else 0,
        'k_rate': k_count / len(tokens) if tokens else 0,
        'e_rate': e_count / len(tokens) if tokens else 0,
        'lane_balance': qo_count / (qo_count + chsh_count) if (qo_count + chsh_count) > 0 else 0.5,
        'kernel_balance': k_count / (k_count + e_count) if (k_count + e_count) > 0 else 0.5,
    }

# =============================================================
# BUILD PARAGRAPHS
# =============================================================
print("\nBuilding paragraphs...")

a_paras = build_paragraphs(tx.currier_a())
b_paras = build_paragraphs(tx.currier_b())

print(f"A paragraphs: {len(a_paras)}")
print(f"B paragraphs: {len(b_paras)}")

# =============================================================
# COMPUTE LANE PROFILES
# =============================================================
print("\n" + "="*70)
print("COMPUTING LANE PROFILES")
print("="*70)

a_profiles = []
for i, para in enumerate(a_paras):
    profile = compute_lane_profile(para['tokens'])
    profile['idx'] = i
    profile['folio'] = para['folio']
    a_profiles.append(profile)

b_profiles = []
for i, para in enumerate(b_paras):
    profile = compute_lane_profile(para['tokens'])
    profile['idx'] = i
    profile['folio'] = para['folio']
    b_profiles.append(profile)

# Summary stats
a_qo_rates = [p['qo_rate'] for p in a_profiles]
b_qo_rates = [p['qo_rate'] for p in b_profiles]
a_lane_balances = [p['lane_balance'] for p in a_profiles]
b_lane_balances = [p['lane_balance'] for p in b_profiles]

print(f"\nQO rate (escape lane):")
print(f"  A mean: {sum(a_qo_rates)/len(a_qo_rates):.3f}")
print(f"  B mean: {sum(b_qo_rates)/len(b_qo_rates):.3f}")

print(f"\nLane balance (QO / (QO+CHSH)):")
print(f"  A mean: {sum(a_lane_balances)/len(a_lane_balances):.3f}")
print(f"  B mean: {sum(b_lane_balances)/len(b_lane_balances):.3f}")

# =============================================================
# LANE BALANCE MATCHING
# =============================================================
print("\n" + "="*70)
print("LANE BALANCE MATCHING")
print("="*70)

def lane_distance(a_prof, b_prof):
    """Distance between lane profiles."""
    d1 = abs(a_prof['lane_balance'] - b_prof['lane_balance'])
    d2 = abs(a_prof['kernel_balance'] - b_prof['kernel_balance'])
    return (d1 + d2) / 2

# For each A paragraph, find best lane-matching B paragraph
results = []
for a in a_profiles:
    best_b = None
    best_dist = float('inf')

    for b in b_profiles:
        dist = lane_distance(a, b)
        if dist < best_dist:
            best_dist = dist
            best_b = b

    results.append({
        'a_idx': a['idx'],
        'a_folio': a['folio'],
        'a_lane': a['lane_balance'],
        'a_kernel': a['kernel_balance'],
        'best_b_idx': best_b['idx'] if best_b else -1,
        'best_b_folio': best_b['folio'] if best_b else None,
        'b_lane': best_b['lane_balance'] if best_b else 0,
        'b_kernel': best_b['kernel_balance'] if best_b else 0,
        'distance': best_dist
    })

distances = [r['distance'] for r in results]
print(f"\nLane distance (0 = perfect match):")
print(f"  Mean: {sum(distances)/len(distances):.3f}")
print(f"  Min: {min(distances):.3f}")
print(f"  Max: {max(distances):.3f}")
print(f"  Close matches (<0.1): {sum(1 for d in distances if d < 0.1)}")

# =============================================================
# CORRELATION TEST
# =============================================================
print("\n" + "="*70)
print("CORRELATION: A kernel balance -> B kernel balance")
print("="*70)

# For matched pairs, is there correlation?
a_kernels = [r['a_kernel'] for r in results]
b_kernels = [r['b_kernel'] for r in results]

def correlation(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = sum((xi - mx)**2 for xi in x) ** 0.5
    den_y = sum((yi - my)**2 for yi in y) ** 0.5
    return num / (den_x * den_y) if den_x * den_y > 0 else 0

corr = correlation(a_kernels, b_kernels)
print(f"\nCorrelation (A kernel -> matched B kernel): {corr:.3f}")

# Correlation between A lane and B lane
a_lanes = [r['a_lane'] for r in results]
b_lanes = [r['b_lane'] for r in results]
lane_corr = correlation(a_lanes, b_lanes)
print(f"Correlation (A lane -> matched B lane): {lane_corr:.3f}")

# =============================================================
# HIGH-QO vs LOW-QO ANALYSIS
# =============================================================
print("\n" + "="*70)
print("HIGH-QO vs LOW-QO GROUPS")
print("="*70)

# Split A paragraphs by QO rate
median_qo = sorted(a_qo_rates)[len(a_qo_rates)//2]
high_qo_a = [p for p in a_profiles if p['qo_rate'] > median_qo]
low_qo_a = [p for p in a_profiles if p['qo_rate'] <= median_qo]

# Get their matched B paragraphs
high_qo_matched_b = []
low_qo_matched_b = []

for r in results:
    if r['a_idx'] in [p['idx'] for p in high_qo_a]:
        high_qo_matched_b.append(r['b_lane'])
    else:
        low_qo_matched_b.append(r['b_lane'])

print(f"\nHigh-QO A paragraphs: {len(high_qo_a)}")
print(f"  Mean matched B lane balance: {sum(high_qo_matched_b)/len(high_qo_matched_b):.3f}")

print(f"\nLow-QO A paragraphs: {len(low_qo_a)}")
print(f"  Mean matched B lane balance: {sum(low_qo_matched_b)/len(low_qo_matched_b):.3f}")

diff = sum(high_qo_matched_b)/len(high_qo_matched_b) - sum(low_qo_matched_b)/len(low_qo_matched_b)
print(f"\nDifference: {diff:+.3f}")

# =============================================================
# SAVE RESULTS
# =============================================================
out_path = Path(__file__).parent.parent / 'results' / 'lane_balance.json'
with open(out_path, 'w') as f:
    json.dump({
        'n_a_paras': len(a_paras),
        'n_b_paras': len(b_paras),
        'mean_lane_distance': sum(distances)/len(distances),
        'kernel_correlation': corr,
        'lane_correlation': lane_corr,
        'high_qo_b_lane': sum(high_qo_matched_b)/len(high_qo_matched_b),
        'low_qo_b_lane': sum(low_qo_matched_b)/len(low_qo_matched_b),
    }, f, indent=2)

print(f"\nSaved to {out_path.name}")

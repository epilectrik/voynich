"""
HT_RECONCILIATION - Script 3: HT Lane Participation
T4: HT PREFIX lane distribution
T5: HT lane transition behavior

Requires T1 PASS.
"""
import json, sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
rng = np.random.RandomState(42)

# --- Load classified set ---
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())


def get_lane(prefix):
    """Classify prefix into lane: QO, CHSH, or OTHER."""
    if prefix == 'qo':
        return 'QO'
    elif prefix in ('ch', 'sh'):
        return 'CHSH'
    else:
        return 'OTHER'


# --- Collect B tokens with lane info, ordered by line ---
line_ordered_tokens = defaultdict(list)  # (folio, line) -> ordered token list

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    is_ht = w not in classified_tokens
    m = morph.extract(w)
    lane = get_lane(m.prefix) if m.prefix else 'NONE'
    line_ordered_tokens[(token.folio, token.line)].append({
        'word': w,
        'is_ht': is_ht,
        'prefix': m.prefix,
        'lane': lane,
        'folio': token.folio,
    })

# ===================================================================
# T4: HT PREFIX Lane Distribution
# ===================================================================
print("=== T4: HT PREFIX Lane Distribution ===")

ht_lane_counts = Counter()
cl_lane_counts = Counter()
ht_prefix_counts = Counter()
cl_prefix_counts = Counter()

for tokens in line_ordered_tokens.values():
    for t in tokens:
        if t['is_ht']:
            ht_lane_counts[t['lane']] += 1
            if t['prefix']:
                ht_prefix_counts[t['prefix']] += 1
        else:
            cl_lane_counts[t['lane']] += 1
            if t['prefix']:
                cl_prefix_counts[t['prefix']] += 1

ht_total = sum(ht_lane_counts.values())
cl_total = sum(cl_lane_counts.values())

print(f"\nHT lane distribution (n={ht_total}):")
for lane in ['QO', 'CHSH', 'OTHER', 'NONE']:
    cnt = ht_lane_counts[lane]
    print(f"  {lane}: {cnt} ({cnt/ht_total*100:.1f}%)")

print(f"\nClassified lane distribution (n={cl_total}):")
for lane in ['QO', 'CHSH', 'OTHER', 'NONE']:
    cnt = cl_lane_counts[lane]
    print(f"  {lane}: {cnt} ({cnt/cl_total*100:.1f}%)")

# Chi-squared test: compare HT vs classified lane distributions
# Use only QO, CHSH, OTHER (exclude NONE for chi-squared)
lanes_for_test = ['QO', 'CHSH', 'OTHER', 'NONE']
ht_obs = np.array([ht_lane_counts[l] for l in lanes_for_test])
cl_obs = np.array([cl_lane_counts[l] for l in lanes_for_test])

# Contingency table: rows = [HT, CL], cols = [QO, CHSH, OTHER, NONE]
contingency = np.array([ht_obs, cl_obs])
chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-squared test (HT vs Classified):")
print(f"  Chi2 = {chi2:.2f}, p = {chi_p:.2e}, dof = {dof}")

# HT top prefixes
print(f"\nHT top 15 prefixes:")
for pfx, cnt in ht_prefix_counts.most_common(15):
    cl_cnt = cl_prefix_counts.get(pfx, 0)
    print(f"  {pfx}: HT={cnt}, CL={cl_cnt}")

# T4 verdict
if chi_p > 0.05:
    t4_verdict = "INTEGRATED"
    t4_detail = f"Chi2={chi2:.2f}, p={chi_p:.4f} > 0.05 - same lane distribution"
elif chi_p < 0.01:
    t4_verdict = "SEGREGATED"
    # Identify over/under-represented lanes
    ht_pcts = {l: ht_lane_counts[l] / ht_total for l in lanes_for_test}
    cl_pcts = {l: cl_lane_counts[l] / cl_total for l in lanes_for_test}
    diffs = {l: ht_pcts[l] - cl_pcts[l] for l in lanes_for_test}
    over = max(diffs, key=diffs.get)
    under = min(diffs, key=diffs.get)
    t4_detail = (f"Chi2={chi2:.2f}, p={chi_p:.2e} - different distribution. "
                 f"HT over-represented in {over} (+{diffs[over]*100:.1f}pp), "
                 f"under-represented in {under} ({diffs[under]*100:.1f}pp)")
else:
    t4_verdict = "MARGINAL"
    t4_detail = f"Chi2={chi2:.2f}, p={chi_p:.4f} - marginal difference"

print(f"\nT4 VERDICT: {t4_verdict} - {t4_detail}")

# ===================================================================
# T5: HT Lane Transition Behavior
# ===================================================================
print()
print("=== T5: HT Lane Transition Behavior ===")

# For adjacent HT-classified pairs on same line, compare lanes
same_lane = 0
diff_lane = 0
total_adj = 0

# Also track by direction
ht_cl_same = 0  # HT then classified, same lane
cl_ht_same = 0  # Classified then HT, same lane
ht_cl_total = 0
cl_ht_total = 0

for tokens in line_ordered_tokens.values():
    for i in range(len(tokens) - 1):
        t1 = tokens[i]
        t2 = tokens[i + 1]

        # Skip if both same category
        if t1['is_ht'] == t2['is_ht']:
            continue

        # Skip if either has no lane (NONE)
        if t1['lane'] == 'NONE' or t2['lane'] == 'NONE':
            continue

        total_adj += 1
        is_same = t1['lane'] == t2['lane']
        if is_same:
            same_lane += 1

        if t1['is_ht'] and not t2['is_ht']:
            ht_cl_total += 1
            if is_same:
                ht_cl_same += 1
        else:
            cl_ht_total += 1
            if is_same:
                cl_ht_same += 1

if total_adj > 0:
    same_rate = same_lane / total_adj
    print(f"HT-Classified adjacent pairs (both with prefix): {total_adj}")
    print(f"  Same lane: {same_lane} ({same_rate*100:.1f}%)")
    print(f"  Different lane: {diff_lane} ({(1-same_rate)*100:.1f}%)")
    if ht_cl_total > 0:
        print(f"  HT->CL transitions: {ht_cl_total}, same lane: {ht_cl_same} ({ht_cl_same/ht_cl_total*100:.1f}%)")
    if cl_ht_total > 0:
        print(f"  CL->HT transitions: {cl_ht_total}, same lane: {cl_ht_same} ({cl_ht_same/cl_ht_total*100:.1f}%)")
else:
    same_rate = 0
    print("No adjacent HT-Classified pairs with prefixes found")

# --- Permutation baseline ---
# Compute expected same-lane rate if HT lanes were randomly assigned
# based on marginal HT lane frequencies (excluding NONE)
ht_lane_with_prefix = {l: ht_lane_counts[l] for l in ['QO', 'CHSH', 'OTHER']}
ht_prefix_total = sum(ht_lane_with_prefix.values())
ht_lane_probs = {l: c / ht_prefix_total for l, c in ht_lane_with_prefix.items()} if ht_prefix_total > 0 else {}

cl_lane_with_prefix = {l: cl_lane_counts[l] for l in ['QO', 'CHSH', 'OTHER']}
cl_prefix_total = sum(cl_lane_with_prefix.values())
cl_lane_probs = {l: c / cl_prefix_total for l, c in cl_lane_with_prefix.items()} if cl_prefix_total > 0 else {}

# Expected same-lane rate under independence
expected_same_rate = sum(ht_lane_probs.get(l, 0) * cl_lane_probs.get(l, 0) for l in ['QO', 'CHSH', 'OTHER'])
print(f"\nExpected same-lane rate (marginal independence): {expected_same_rate*100:.1f}%")
if same_rate > 0:
    lift = same_rate / expected_same_rate if expected_same_rate > 0 else float('inf')
    print(f"Observed/Expected ratio: {lift:.3f}x")

# Permutation test: shuffle HT lane assignments within folio
print("\n=== T5 Permutation Test (1000 shuffles) ===")

# Pre-compute: for each folio, collect HT token lanes and adjacency structure
folio_adj_data = defaultdict(lambda: {'ht_lanes': [], 'adj_pairs': []})

for (folio, line), tokens in line_ordered_tokens.items():
    for i in range(len(tokens) - 1):
        t1 = tokens[i]
        t2 = tokens[i + 1]
        if t1['is_ht'] == t2['is_ht']:
            continue
        if t1['lane'] == 'NONE' or t2['lane'] == 'NONE':
            continue

        if t1['is_ht']:
            folio_adj_data[folio]['adj_pairs'].append(('ht', t1['lane'], t2['lane']))
        else:
            folio_adj_data[folio]['adj_pairs'].append(('cl', t2['lane'], t1['lane']))

    # Collect all HT lanes in this folio (for shuffling)
    for t in tokens:
        if t['is_ht'] and t['lane'] != 'NONE':
            folio_adj_data[folio]['ht_lanes'].append(t['lane'])

null_same_counts = []

for p in range(1000):
    perm_same = 0
    perm_total = 0

    for folio, data in folio_adj_data.items():
        if not data['ht_lanes'] or not data['adj_pairs']:
            continue

        # Shuffle HT lanes within folio
        shuffled_lanes = list(data['ht_lanes'])
        rng.shuffle(shuffled_lanes)

        # Create lane pool for random assignment
        lane_pool = list(shuffled_lanes)
        lane_idx = 0

        for adj_type, lane_a, lane_b in data['adj_pairs']:
            # Assign a random lane from the shuffled pool
            if lane_idx < len(lane_pool):
                rand_lane = lane_pool[lane_idx]
                lane_idx += 1
            else:
                # Wrap around
                lane_idx = 0
                rand_lane = lane_pool[lane_idx]
                lane_idx += 1

            perm_total += 1
            if adj_type == 'ht':
                # HT had lane_a, classified has lane_b
                if rand_lane == lane_b:
                    perm_same += 1
            else:
                # Classified had lane_b, HT had lane_a
                if rand_lane == lane_b:
                    perm_same += 1

    null_same_counts.append(perm_same)

if null_same_counts and total_adj > 0:
    null_mean = np.mean(null_same_counts)
    null_std = np.std(null_same_counts)
    z_score = (same_lane - null_mean) / null_std if null_std > 0 else 0
    p_above = np.mean([ns >= same_lane for ns in null_same_counts])
    p_below = np.mean([ns <= same_lane for ns in null_same_counts])

    print(f"Observed same-lane: {same_lane}")
    print(f"Null mean: {null_mean:.1f}")
    print(f"Null std: {null_std:.2f}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P(more same than observed): {p_above:.4f}")
    print(f"P(fewer same than observed): {p_below:.4f}")

    if same_lane > null_mean * 1.2 and p_above < 0.01:
        t5_verdict = "LANE_AWARE"
        t5_detail = f"Same-lane rate {same_rate*100:.1f}% > 1.2x null ({null_mean/total_adj*100:.1f}%), p={p_above:.4f}"
    elif same_lane < null_mean * 0.8 and p_below < 0.01:
        t5_verdict = "LANE_AVOIDANT"
        t5_detail = f"Same-lane rate {same_rate*100:.1f}% < 0.8x null ({null_mean/total_adj*100:.1f}%), p={p_below:.4f}"
    else:
        t5_verdict = "NEUTRAL"
        t5_detail = f"Same-lane rate {same_rate*100:.1f}% ~ null ({null_mean/total_adj*100:.1f}%), z={z_score:.2f}"
else:
    t5_verdict = "INSUFFICIENT_DATA"
    t5_detail = "Not enough adjacent HT-classified pairs"
    null_mean = 0
    null_std = 0
    z_score = 0
    p_above = 1.0
    p_below = 1.0

print(f"\nT5 VERDICT: {t5_verdict} - {t5_detail}")

# --- Save results ---
results = {
    "metadata": {
        "phase": "HT_RECONCILIATION",
        "script": "ht_lane_participation.py",
        "tests": ["T4", "T5"]
    },
    "T4_lane_distribution": {
        "ht_lanes": {l: ht_lane_counts[l] for l in ['QO', 'CHSH', 'OTHER', 'NONE']},
        "ht_total": ht_total,
        "cl_lanes": {l: cl_lane_counts[l] for l in ['QO', 'CHSH', 'OTHER', 'NONE']},
        "cl_total": cl_total,
        "chi2": round(float(chi2), 4),
        "chi_p": float(chi_p),
        "dof": int(dof),
        "ht_top_prefixes": {pfx: cnt for pfx, cnt in ht_prefix_counts.most_common(15)},
        "verdict": t4_verdict,
        "detail": t4_detail
    },
    "T5_lane_transitions": {
        "total_adj_pairs": total_adj,
        "same_lane": same_lane,
        "diff_lane": total_adj - same_lane,
        "same_rate": round(same_rate, 6) if total_adj > 0 else None,
        "expected_same_rate": round(expected_same_rate, 6),
        "lift": round(same_rate / expected_same_rate, 4) if expected_same_rate > 0 and total_adj > 0 else None,
        "ht_cl_transitions": ht_cl_total,
        "ht_cl_same_lane": ht_cl_same,
        "cl_ht_transitions": cl_ht_total,
        "cl_ht_same_lane": cl_ht_same,
        "permutation": {
            "n_permutations": 1000,
            "observed_same": same_lane,
            "null_mean": round(float(null_mean), 2),
            "null_std": round(float(null_std), 4),
            "z_score": round(float(z_score), 4),
            "p_above": round(float(p_above), 6),
            "p_below": round(float(p_below), 6)
        },
        "verdict": t5_verdict,
        "detail": t5_detail
    }
}

out_path = PROJECT_ROOT / 'phases' / 'HT_RECONCILIATION' / 'results' / 'ht_lane_participation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print()
print(f"Results saved to {out_path}")

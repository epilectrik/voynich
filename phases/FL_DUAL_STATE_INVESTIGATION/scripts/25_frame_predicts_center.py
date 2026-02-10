"""
25_frame_predicts_center.py

Test whether the outer-left + outer-right "frame" predicts center content.
If the nesting is real structure, knowing the OL+OR tokens should narrow
the vocabulary of what appears in the center.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Fit GMMs
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# ============================================================
# Build line profiles with frame + center
# ============================================================
line_profiles = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'class': cls, 'role': role, 'prefix': prefix}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    if len(gap) < 3:
        continue

    ol = gap[0]
    oright = gap[-1]
    center = gap[1:-1]

    # Build frame key from prefix pairs
    frame_prefix = (ol['prefix'], oright['prefix'])
    # Build frame key from class pairs
    frame_class = (ol['class'], oright['class'])

    line_profiles.append({
        'ol': ol,
        'or': oright,
        'center': center,
        'frame_prefix': frame_prefix,
        'frame_class': frame_class,
        'center_words': [t['word'] for t in center],
        'center_roles': [t['role'] for t in center],
        'center_prefixes': [t['prefix'] for t in center],
    })

print(f"Lines with frame+center: {len(line_profiles)}")

# ============================================================
# TEST 1: Does prefix-frame predict center prefix distribution?
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: PREFIX FRAME -> CENTER PREFIX DISTRIBUTION")
print(f"{'='*60}")

# Group lines by frame prefix pair
frame_prefix_groups = defaultdict(list)
for lp in line_profiles:
    frame_prefix_groups[lp['frame_prefix']].append(lp)

# For common frames, compute center prefix distribution
common_frames = [(f, lps) for f, lps in frame_prefix_groups.items() if len(lps) >= 15]
common_frames.sort(key=lambda x: -len(x[1]))

print(f"  Common prefix frames (n>=15): {len(common_frames)}")

# Overall center prefix distribution (baseline)
all_center_prefixes = Counter()
for lp in line_profiles:
    all_center_prefixes.update(lp['center_prefixes'])
total_center = sum(all_center_prefixes.values())
baseline_dist = {p: c/total_center for p, c in all_center_prefixes.items()}

print(f"\n  Baseline center prefix distribution (n={total_center}):")
for pfx, count in all_center_prefixes.most_common(8):
    print(f"    {pfx:>8}: {count/total_center*100:.1f}%")

print(f"\n  Frame-specific center prefix distributions:")
for frame, lps in common_frames[:12]:
    center_pfx = Counter()
    for lp in lps:
        center_pfx.update(lp['center_prefixes'])
    total = sum(center_pfx.values())
    if total < 10:
        continue
    top3 = center_pfx.most_common(3)
    top3_str = ', '.join(f"{p}({c/total*100:.0f}%)" for p, c in top3)
    # Compute KL divergence from baseline
    kl = 0
    for pfx, count in center_pfx.items():
        p = count / total
        q = baseline_dist.get(pfx, 1e-6)
        if p > 0:
            kl += p * np.log2(p / q)
    print(f"    {str(frame):>20} (n={len(lps):>3}, center={total:>4}): "
          f"{top3_str}  KL={kl:.3f}")

# Chi-squared: frame x center prefix
top_center_prefixes = [p for p, _ in all_center_prefixes.most_common(10)]
top_frame_keys = [f for f, lps in common_frames[:15]]

table_rows = []
for frame in top_frame_keys:
    lps = frame_prefix_groups[frame]
    pfx_counts = Counter()
    for lp in lps:
        pfx_counts.update(lp['center_prefixes'])
    table_rows.append([pfx_counts.get(p, 0) for p in top_center_prefixes])

table = np.array(table_rows)
# Remove zero rows/cols
row_mask = table.sum(axis=1) > 0
col_mask = table.sum(axis=0) > 0
table = table[row_mask][:, col_mask]

if table.shape[0] >= 2 and table.shape[1] >= 2:
    chi2, p_val, dof, _ = chi2_contingency(table)
    v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
    print(f"\n  Frame x Center-prefix: chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")
    frame_prefix_v = v
else:
    print("\n  Insufficient data for chi-squared test")
    frame_prefix_v = 0

# ============================================================
# TEST 2: Does prefix-frame predict center ROLE distribution?
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: PREFIX FRAME -> CENTER ROLE DISTRIBUTION")
print(f"{'='*60}")

roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']

# Baseline role distribution
all_center_roles = Counter()
for lp in line_profiles:
    all_center_roles.update(lp['center_roles'])
total_roles = sum(all_center_roles.values())

print(f"  Baseline center role distribution (n={total_roles}):")
for r in roles:
    pct = all_center_roles.get(r, 0) / total_roles * 100
    print(f"    {r:>20}: {pct:.1f}%")

table_rows = []
for frame in top_frame_keys:
    lps = frame_prefix_groups[frame]
    role_counts = Counter()
    for lp in lps:
        role_counts.update(lp['center_roles'])
    table_rows.append([role_counts.get(r, 0) for r in roles])

table = np.array(table_rows)
row_mask = table.sum(axis=1) > 0
col_mask = table.sum(axis=0) > 0
table = table[row_mask][:, col_mask]

if table.shape[0] >= 2 and table.shape[1] >= 2:
    chi2, p_val, dof, _ = chi2_contingency(table)
    v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
    print(f"\n  Frame x Center-role: chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")
    frame_role_v = v
else:
    frame_role_v = 0

# ============================================================
# TEST 3: Does class-frame predict center word distribution?
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: CLASS FRAME -> CENTER WORD DISTRIBUTION")
print(f"{'='*60}")

frame_class_groups = defaultdict(list)
for lp in line_profiles:
    if lp['frame_class'][0] is not None and lp['frame_class'][1] is not None:
        frame_class_groups[lp['frame_class']].append(lp)

common_class_frames = [(f, lps) for f, lps in frame_class_groups.items() if len(lps) >= 12]
common_class_frames.sort(key=lambda x: -len(x[1]))
print(f"  Common class frames (n>=12): {len(common_class_frames)}")

# For each common class frame, compute center word entropy
all_center_words = Counter()
for lp in line_profiles:
    all_center_words.update(lp['center_words'])

def word_entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0
    probs = [c/total for c in counter.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

baseline_entropy = word_entropy(all_center_words)
print(f"  Baseline center word entropy: {baseline_entropy:.2f} bits")

print(f"\n  {'Frame':>15} {'n_lines':>8} {'Center n':>9} {'Entropy':>8} {'Reduction':>10}")
print(f"  {'-'*55}")

entropy_reductions = []
for frame, lps in common_class_frames[:15]:
    center_words = Counter()
    for lp in lps:
        center_words.update(lp['center_words'])
    total = sum(center_words.values())
    if total < 10:
        continue
    h = word_entropy(center_words)
    reduction = (baseline_entropy - h) / baseline_entropy * 100
    entropy_reductions.append(reduction)
    label = f"C{frame[0]},C{frame[1]}"
    print(f"  {label:>15} {len(lps):>8} {total:>9} {h:>8.2f} {reduction:>+9.1f}%")

mean_reduction = np.mean(entropy_reductions) if entropy_reductions else 0
print(f"\n  Mean entropy reduction: {mean_reduction:.1f}%")

# ============================================================
# TEST 4: Mutual information: frame -> center words
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: MUTUAL INFORMATION: FRAME -> CENTER")
print(f"{'='*60}")

# Use prefix-frame for larger sample
# MI(frame; center_word) using top frames and top center words
top_words = [w for w, _ in all_center_words.most_common(50)]

# Build joint distribution: frame x word
joint_counts = defaultdict(Counter)
for lp in line_profiles:
    frame = lp['frame_prefix']
    if frame not in dict(common_frames[:15]):
        continue
    for w in lp['center_words']:
        if w in top_words:
            joint_counts[frame][w] += 1

# Compute MI
total = sum(sum(wc.values()) for wc in joint_counts.values())
if total > 0:
    # P(frame)
    frame_marginal = {}
    for f, wc in joint_counts.items():
        frame_marginal[f] = sum(wc.values()) / total

    # P(word)
    word_marginal = Counter()
    for f, wc in joint_counts.items():
        for w, c in wc.items():
            word_marginal[w] += c
    word_marginal = {w: c/total for w, c in word_marginal.items()}

    # MI
    mi = 0
    for f, wc in joint_counts.items():
        for w, c in wc.items():
            p_joint = c / total
            p_f = frame_marginal[f]
            p_w = word_marginal[w]
            if p_joint > 0 and p_f > 0 and p_w > 0:
                mi += p_joint * np.log2(p_joint / (p_f * p_w))

    # Normalized MI
    h_frame = -sum(p * np.log2(p) for p in frame_marginal.values() if p > 0)
    h_word = -sum(p * np.log2(p) for p in word_marginal.values() if p > 0)
    nmi = mi / min(h_frame, h_word) if min(h_frame, h_word) > 0 else 0

    print(f"  MI(prefix_frame; center_word) = {mi:.4f} bits")
    print(f"  H(frame) = {h_frame:.2f}, H(word) = {h_word:.2f}")
    print(f"  NMI = {nmi:.4f}")
    mi_val = mi
    nmi_val = nmi
else:
    mi_val = 0
    nmi_val = 0

# ============================================================
# TEST 5: Permutation test - is frame->center association real?
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: PERMUTATION TEST")
print(f"{'='*60}")

import random
random.seed(42)

# Shuffle center words across lines, recompute MI
n_perms = 500
perm_mis = []

# Collect all center word lists
all_centers = [lp['center_words'] for lp in line_profiles]
all_frames = [lp['frame_prefix'] for lp in line_profiles]

for _ in range(n_perms):
    shuffled_centers = all_centers.copy()
    random.shuffle(shuffled_centers)

    perm_joint = defaultdict(Counter)
    for frame, center_words in zip(all_frames, shuffled_centers):
        if frame not in dict(common_frames[:15]):
            continue
        for w in center_words:
            if w in top_words:
                perm_joint[frame][w] += 1

    perm_total = sum(sum(wc.values()) for wc in perm_joint.values())
    if perm_total == 0:
        perm_mis.append(0)
        continue

    perm_frame_marginal = {}
    for f, wc in perm_joint.items():
        perm_frame_marginal[f] = sum(wc.values()) / perm_total

    perm_word_marginal = Counter()
    for f, wc in perm_joint.items():
        for w, c in wc.items():
            perm_word_marginal[w] += c
    perm_word_marginal = {w: c/perm_total for w, c in perm_word_marginal.items()}

    perm_mi = 0
    for f, wc in perm_joint.items():
        for w, c in wc.items():
            p_joint = c / perm_total
            p_f = perm_frame_marginal[f]
            p_w = perm_word_marginal[w]
            if p_joint > 0 and p_f > 0 and p_w > 0:
                perm_mi += p_joint * np.log2(p_joint / (p_f * p_w))

    perm_mis.append(perm_mi)

perm_mean = np.mean(perm_mis)
perm_std = np.std(perm_mis)
z_score = (mi_val - perm_mean) / perm_std if perm_std > 0 else 0
p_perm = np.mean([1 for pm in perm_mis if pm >= mi_val])

print(f"  Observed MI: {mi_val:.4f}")
print(f"  Permuted MI: {perm_mean:.4f} +/- {perm_std:.4f}")
print(f"  Z-score: {z_score:.2f}")
print(f"  Permutation p-value: {p_perm:.4f}")
print(f"  MI lift over null: {mi_val/perm_mean:.2f}x" if perm_mean > 0 else "  Null MI = 0")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

frame_constrains_prefix = frame_prefix_v > 0.10
frame_constrains_role = frame_role_v > 0.08
mi_significant = p_perm < 0.05 and mi_val > perm_mean * 1.5
entropy_reduced = mean_reduction > 5

if frame_constrains_prefix and mi_significant:
    verdict = "FRAME_CONSTRAINS_CENTER"
    explanation = ("The OL+OR frame significantly constrains center content: "
                   f"prefix V={frame_prefix_v:.3f}, MI z={z_score:.1f}")
elif frame_constrains_prefix or mi_significant:
    verdict = "WEAK_FRAME_EFFECT"
    explanation = "Some frame->center association but not strong enough to confirm constraint"
else:
    verdict = "NO_FRAME_EFFECT"
    explanation = "The frame does not meaningfully constrain center content"

print(f"  {verdict}")
print(f"  {explanation}")

# Save
result = {
    'n_lines': len(line_profiles),
    'frame_prefix_cramers_v': round(float(frame_prefix_v), 3),
    'frame_role_cramers_v': round(float(frame_role_v), 3),
    'mi_frame_center': round(float(mi_val), 4),
    'nmi': round(float(nmi_val), 4),
    'mi_perm_mean': round(float(perm_mean), 4),
    'mi_z_score': round(float(z_score), 2),
    'mi_perm_p': round(float(p_perm), 4),
    'mean_entropy_reduction': round(float(mean_reduction), 1),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "25_frame_predicts_center.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")

"""
34_four_coordinate_test.py

Are there 4 coordinate tokens per line?

Hypothesis: each line has a 4-dimensional address:
  1. FL-LOW  = action intensity (stage)
  2. OUTER-L = monitoring mode (which specific observation)
  3. OUTER-R = action mode (which specific intervention)
  4. FL-HIGH = oversight level (stage)

If OL and OR are coordinates (not content), they should:
  A. Have a SMALL discrete vocabulary (coordinate-like)
  B. Be INDEPENDENT of each other (separate dimensions)
  C. Each PARTITION center content differently
  D. Have LOW entropy (few choices per line, not random)
  E. Together with FL pair, provide a COMPLETE address
     (knowing all 4 should tightly predict center vocabulary)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, spearmanr

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
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

# Build line tokens
line_tokens = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)

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
# Extract 4 coordinates + center for each line
# ============================================================
line_records = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]

        prefix = m.prefix if m and m.prefix else 'NONE'
        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')

        all_info.append({
            'word': t.word, 'idx': idx, 'is_fl': is_fl,
            'mode': mode, 'stage': stage, 'prefix': prefix,
            'class': cls, 'role': role,
            'middle': m.middle if m else None,
        })

    low_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'LOW']
    high_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)

    gap = [a for a in all_info if not a['is_fl']
           and a['idx'] > max_low_idx and a['idx'] < min_high_idx]

    if len(gap) < 2:
        continue

    # OL = first gap token, OR = last gap token, CENTER = everything between
    ol_token = gap[0]
    or_token = gap[-1]
    center = gap[1:-1] if len(gap) > 2 else []

    line_records.append({
        'low_stage': low_stage,
        'high_stage': high_stage,
        'ol_word': ol_token['word'],
        'ol_prefix': ol_token['prefix'],
        'ol_class': ol_token['class'],
        'ol_role': ol_token['role'],
        'or_word': or_token['word'],
        'or_prefix': or_token['prefix'],
        'or_class': or_token['class'],
        'or_role': or_token['role'],
        'center_words': [c['word'] for c in center],
        'center_prefixes': [c['prefix'] for c in center],
        'center_roles': [c['role'] for c in center],
        'n_center': len(center),
    })

print(f"Lines with full 4-coordinate extraction: {len(line_records)}")

# ============================================================
# TEST A: Vocabulary size (coordinate-likeness)
# ============================================================
print(f"\n{'='*70}")
print("TEST A: VOCABULARY SIZE (coordinate-likeness)")
print(f"{'='*70}")

ol_words = Counter(r['ol_word'] for r in line_records)
or_words = Counter(r['or_word'] for r in line_records)
center_words = Counter(w for r in line_records for w in r['center_words'])

ol_prefixes = Counter(r['ol_prefix'] for r in line_records)
or_prefixes = Counter(r['or_prefix'] for r in line_records)
center_prefixes = Counter(p for r in line_records for p in r['center_prefixes'])

# Unique types
n_ol_types = len(ol_words)
n_or_types = len(or_words)
n_center_types = len(center_words)
n_ol_tokens = sum(ol_words.values())
n_or_tokens = sum(or_words.values())
n_center_tokens = sum(center_words.values())

# Type-token ratio
ol_ttr = n_ol_types / n_ol_tokens if n_ol_tokens > 0 else 0
or_ttr = n_or_types / n_or_tokens if n_or_tokens > 0 else 0
center_ttr = n_center_types / n_center_tokens if n_center_tokens > 0 else 0

print(f"\n  {'Position':<10} {'Types':>6} {'Tokens':>7} {'TTR':>6} {'Top5 coverage':>14}")

# Top-5 coverage
ol_top5 = sum(c for _, c in ol_words.most_common(5)) / n_ol_tokens * 100
or_top5 = sum(c for _, c in or_words.most_common(5)) / n_or_tokens * 100
center_top5 = sum(c for _, c in center_words.most_common(5)) / n_center_tokens * 100 if n_center_tokens > 0 else 0

print(f"  {'OL':<10} {n_ol_types:>6} {n_ol_tokens:>7} {ol_ttr:>5.3f} {ol_top5:>13.1f}%")
print(f"  {'OR':<10} {n_or_types:>6} {n_or_tokens:>7} {or_ttr:>5.3f} {or_top5:>13.1f}%")
print(f"  {'CENTER':<10} {n_center_types:>6} {n_center_tokens:>7} {center_ttr:>5.3f} {center_top5:>13.1f}%")

# Top words per position
print(f"\n  Top 10 OL words:")
for w, c in ol_words.most_common(10):
    pct = c / n_ol_tokens * 100
    role = token_to_role.get(w, 'UNK')
    print(f"    {w:<14} {c:>5} ({pct:>4.1f}%) role={role}")

print(f"\n  Top 10 OR words:")
for w, c in or_words.most_common(10):
    pct = c / n_or_tokens * 100
    role = token_to_role.get(w, 'UNK')
    print(f"    {w:<14} {c:>5} ({pct:>4.1f}%) role={role}")

print(f"\n  Top 10 CENTER words:")
for w, c in center_words.most_common(10):
    pct = c / n_center_tokens * 100
    role = token_to_role.get(w, 'UNK')
    print(f"    {w:<14} {c:>5} ({pct:>4.1f}%) role={role}")

# Prefix distributions
print(f"\n  Prefix distributions:")
all_pfx = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot']
print(f"  {'Pos':<10}", end='')
for p in all_pfx:
    print(f" {p:>6}", end='')
print()
print(f"  {'-'*50}")
for label, counter in [('OL', ol_prefixes), ('OR', or_prefixes), ('CENTER', center_prefixes)]:
    total = sum(counter.values())
    print(f"  {label:<10}", end='')
    for p in all_pfx:
        pct = counter.get(p, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>5.1f}%", end='')
    print()

# Entropy
def entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0
    probs = [c / total for c in counter.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

ol_entropy = entropy(ol_words)
or_entropy = entropy(or_words)
center_entropy = entropy(center_words)

# Normalized entropy (0=deterministic, 1=uniform)
ol_max_ent = np.log2(n_ol_types) if n_ol_types > 1 else 1
or_max_ent = np.log2(n_or_types) if n_or_types > 1 else 1
center_max_ent = np.log2(n_center_types) if n_center_types > 1 else 1

print(f"\n  Entropy (bits) and normalized entropy:")
print(f"  {'OL':<10}: H={ol_entropy:.2f} bits, H_norm={ol_entropy/ol_max_ent:.3f}")
print(f"  {'OR':<10}: H={or_entropy:.2f} bits, H_norm={or_entropy/or_max_ent:.3f}")
print(f"  {'CENTER':<10}: H={center_entropy:.2f} bits, H_norm={center_entropy/center_max_ent:.3f}")

# ============================================================
# TEST B: OL-OR INDEPENDENCE
# ============================================================
print(f"\n{'='*70}")
print("TEST B: OL-OR INDEPENDENCE")
print(f"{'='*70}")

# If OL and OR are separate coordinate dimensions, they should be
# relatively independent (low mutual information)

# Use prefix as the dimension (more tractable than full word)
ol_or_pfx_table = Counter((r['ol_prefix'], r['or_prefix']) for r in line_records)

# Build contingency
ol_pfx_list = sorted(set(r['ol_prefix'] for r in line_records))
or_pfx_list = sorted(set(r['or_prefix'] for r in line_records))

matrix = np.zeros((len(ol_pfx_list), len(or_pfx_list)))
ol_idx = {p: i for i, p in enumerate(ol_pfx_list)}
or_idx = {p: i for i, p in enumerate(or_pfx_list)}

for (olp, orp), c in ol_or_pfx_table.items():
    matrix[ol_idx[olp], or_idx[orp]] = c

# Remove empty rows/cols
row_sums = matrix.sum(axis=1)
col_sums = matrix.sum(axis=0)
keep_rows = row_sums > 5
keep_cols = col_sums > 5
matrix_clean = matrix[keep_rows][:, keep_cols]

if matrix_clean.shape[0] >= 2 and matrix_clean.shape[1] >= 2:
    chi2, p_val, dof, expected = chi2_contingency(matrix_clean)
    v = np.sqrt(chi2 / (matrix_clean.sum() * (min(matrix_clean.shape) - 1)))
    print(f"\n  OL_prefix x OR_prefix: chi2={chi2:.1f}, V={v:.3f}, p={p_val:.2e}")
    if v < 0.1:
        print(f"  -> INDEPENDENT (V<0.1): OL and OR are separate dimensions")
    elif v < 0.2:
        print(f"  -> WEAKLY COUPLED (0.1<V<0.2): mostly independent")
    else:
        print(f"  -> COUPLED (V>0.2): not independent dimensions")

# Also test OL vs FL-LOW and OR vs FL-HIGH
ol_low_table = Counter((r['ol_prefix'], r['low_stage']) for r in line_records)
or_high_table = Counter((r['or_prefix'], r['high_stage']) for r in line_records)

# OL vs FL-LOW
low_stage_list = sorted(set(r['low_stage'] for r in line_records))
m1 = np.zeros((len(ol_pfx_list), len(low_stage_list)))
low_idx = {s: i for i, s in enumerate(low_stage_list)}
for (olp, ls), c in ol_low_table.items():
    m1[ol_idx[olp], low_idx[ls]] = c
m1_clean = m1[m1.sum(axis=1) > 5][:, m1.sum(axis=0) > 5]
if m1_clean.shape[0] >= 2 and m1_clean.shape[1] >= 2:
    chi2_ol, p_ol, _, _ = chi2_contingency(m1_clean)
    v_ol = np.sqrt(chi2_ol / (m1_clean.sum() * (min(m1_clean.shape) - 1)))
    print(f"\n  OL_prefix x FL-LOW stage: V={v_ol:.3f}, p={p_ol:.2e}")

# OR vs FL-HIGH
high_stage_list = sorted(set(r['high_stage'] for r in line_records))
m2 = np.zeros((len(or_pfx_list), len(high_stage_list)))
high_idx = {s: i for i, s in enumerate(high_stage_list)}
for (orp, hs), c in or_high_table.items():
    m2[or_idx[orp], high_idx[hs]] = c
m2_clean = m2[m2.sum(axis=1) > 5][:, m2.sum(axis=0) > 5]
if m2_clean.shape[0] >= 2 and m2_clean.shape[1] >= 2:
    chi2_or, p_or, _, _ = chi2_contingency(m2_clean)
    v_or = np.sqrt(chi2_or / (m2_clean.sum() * (min(m2_clean.shape) - 1)))
    print(f"  OR_prefix x FL-HIGH stage: V={v_or:.3f}, p={p_or:.2e}")

# Cross: OL vs FL-HIGH and OR vs FL-LOW
ol_high_table = Counter((r['ol_prefix'], r['high_stage']) for r in line_records)
or_low_table = Counter((r['or_prefix'], r['low_stage']) for r in line_records)

m3 = np.zeros((len(ol_pfx_list), len(high_stage_list)))
for (olp, hs), c in ol_high_table.items():
    m3[ol_idx[olp], high_idx[hs]] = c
m3_clean = m3[m3.sum(axis=1) > 5][:, m3.sum(axis=0) > 5]
if m3_clean.shape[0] >= 2 and m3_clean.shape[1] >= 2:
    chi2_olh, p_olh, _, _ = chi2_contingency(m3_clean)
    v_olh = np.sqrt(chi2_olh / (m3_clean.sum() * (min(m3_clean.shape) - 1)))
    print(f"  OL_prefix x FL-HIGH stage: V={v_olh:.3f}, p={p_olh:.2e}")

m4 = np.zeros((len(or_pfx_list), len(low_stage_list)))
for (orp, ls), c in or_low_table.items():
    m4[or_idx[orp], low_idx[ls]] = c
m4_clean = m4[m4.sum(axis=1) > 5][:, m4.sum(axis=0) > 5]
if m4_clean.shape[0] >= 2 and m4_clean.shape[1] >= 2:
    chi2_orl, p_orl, _, _ = chi2_contingency(m4_clean)
    v_orl = np.sqrt(chi2_orl / (m4_clean.sum() * (min(m4_clean.shape) - 1)))
    print(f"  OR_prefix x FL-LOW stage: V={v_orl:.3f}, p={p_orl:.2e}")

# ============================================================
# TEST C: Do OL/OR partition center content?
# ============================================================
print(f"\n{'='*70}")
print("TEST C: DO OL/OR PARTITION CENTER CONTENT?")
print(f"{'='*70}")

# For each OL prefix, what center words appear?
# Compare vocabulary overlap between different OL values
ol_prefix_centers = defaultdict(Counter)
or_prefix_centers = defaultdict(Counter)

for r in line_records:
    for w in r['center_words']:
        ol_prefix_centers[r['ol_prefix']][w] += 1
        or_prefix_centers[r['or_prefix']][w] += 1

# Jaccard between center vocabularies for different OL prefixes
top_ol_pfx = [p for p, c in ol_prefixes.most_common(6) if c >= 30]
top_or_pfx = [p for p, c in or_prefixes.most_common(6) if c >= 30]

print(f"\n  Center vocabulary overlap by OL prefix (Jaccard):")
if len(top_ol_pfx) >= 2:
    print(f"  {'':>8}", end='')
    for p in top_ol_pfx:
        print(f" {p:>6}", end='')
    print()
    for i, p1 in enumerate(top_ol_pfx):
        print(f"  {p1:>8}", end='')
        s1 = set(w for w, c in ol_prefix_centers[p1].items() if c >= 2)
        for j, p2 in enumerate(top_ol_pfx):
            s2 = set(w for w, c in ol_prefix_centers[p2].items() if c >= 2)
            if i == j:
                print(f"  {'--':>5}", end='')
            else:
                inter = len(s1 & s2)
                union = len(s1 | s2)
                jacc = inter / union if union > 0 else 0
                print(f" {jacc:>5.2f}", end='')
        print()

print(f"\n  Center vocabulary overlap by OR prefix (Jaccard):")
if len(top_or_pfx) >= 2:
    print(f"  {'':>8}", end='')
    for p in top_or_pfx:
        print(f" {p:>6}", end='')
    print()
    for i, p1 in enumerate(top_or_pfx):
        print(f"  {p1:>8}", end='')
        s1 = set(w for w, c in or_prefix_centers[p1].items() if c >= 2)
        for j, p2 in enumerate(top_or_pfx):
            s2 = set(w for w, c in or_prefix_centers[p2].items() if c >= 2)
            if i == j:
                print(f"  {'--':>5}", end='')
            else:
                inter = len(s1 & s2)
                union = len(s1 | s2)
                jacc = inter / union if union > 0 else 0
                print(f" {jacc:>5.2f}", end='')
        print()

# Mean Jaccard for OL vs OR partitioning
ol_jaccards = []
for i in range(len(top_ol_pfx)):
    s1 = set(w for w, c in ol_prefix_centers[top_ol_pfx[i]].items() if c >= 2)
    for j in range(i+1, len(top_ol_pfx)):
        s2 = set(w for w, c in ol_prefix_centers[top_ol_pfx[j]].items() if c >= 2)
        inter = len(s1 & s2)
        union = len(s1 | s2)
        ol_jaccards.append(inter / union if union > 0 else 0)

or_jaccards = []
for i in range(len(top_or_pfx)):
    s1 = set(w for w, c in or_prefix_centers[top_or_pfx[i]].items() if c >= 2)
    for j in range(i+1, len(top_or_pfx)):
        s2 = set(w for w, c in or_prefix_centers[top_or_pfx[j]].items() if c >= 2)
        inter = len(s1 & s2)
        union = len(s1 | s2)
        or_jaccards.append(inter / union if union > 0 else 0)

print(f"\n  Mean center Jaccard across OL prefixes: {np.mean(ol_jaccards):.3f}")
print(f"  Mean center Jaccard across OR prefixes: {np.mean(or_jaccards):.3f}")
print(f"  (Lower = more partitioning, higher = same vocabulary)")

# ============================================================
# TEST D: Predictive power comparison
# ============================================================
print(f"\n{'='*70}")
print("TEST D: PREDICTIVE POWER OF EACH COORDINATE")
print(f"{'='*70}")

# How much does each coordinate narrow down center prefix?
# Use conditional entropy: H(center_prefix | coordinate)

def conditional_entropy(condition_values, target_values):
    """H(target | condition)"""
    joint = Counter(zip(condition_values, target_values))
    cond_counts = Counter(condition_values)
    total = len(condition_values)

    h = 0
    for (c, t), count in joint.items():
        p_joint = count / total
        p_cond = cond_counts[c] / total
        p_t_given_c = count / cond_counts[c]
        if p_t_given_c > 0:
            h -= p_joint * np.log2(p_t_given_c)
    return h

# Only lines with center tokens
lines_with_center = [r for r in line_records if r['n_center'] > 0]
print(f"\n  Lines with center tokens: {len(lines_with_center)}")

# For each center token, what's its prefix?
# Flatten: each center token gets the line's coordinates
center_entries = []
for r in lines_with_center:
    for cp in r['center_prefixes']:
        center_entries.append({
            'low': r['low_stage'],
            'high': r['high_stage'],
            'ol_pfx': r['ol_prefix'],
            'or_pfx': r['or_prefix'],
            'center_pfx': cp,
        })

if center_entries:
    center_pfxs = [e['center_pfx'] for e in center_entries]
    h_baseline = entropy(Counter(center_pfxs))

    h_given_low = conditional_entropy(
        [e['low'] for e in center_entries], center_pfxs)
    h_given_high = conditional_entropy(
        [e['high'] for e in center_entries], center_pfxs)
    h_given_ol = conditional_entropy(
        [e['ol_pfx'] for e in center_entries], center_pfxs)
    h_given_or = conditional_entropy(
        [e['or_pfx'] for e in center_entries], center_pfxs)

    # Combined: all 4 coordinates
    h_given_all4 = conditional_entropy(
        [(e['low'], e['high'], e['ol_pfx'], e['or_pfx']) for e in center_entries],
        center_pfxs)

    # Just FL pair
    h_given_fl = conditional_entropy(
        [(e['low'], e['high']) for e in center_entries], center_pfxs)

    # Just OL+OR
    h_given_olor = conditional_entropy(
        [(e['ol_pfx'], e['or_pfx']) for e in center_entries], center_pfxs)

    print(f"\n  Conditional entropy of center prefix:")
    print(f"  {'Condition':<25} {'H(center|cond)':>15} {'Reduction':>10}")
    print(f"  {'-'*55}")
    print(f"  {'(none = baseline)':<25} {h_baseline:>14.3f} {'--':>10}")
    print(f"  {'FL-LOW':<25} {h_given_low:>14.3f} {(h_baseline-h_given_low)/h_baseline*100:>9.1f}%")
    print(f"  {'FL-HIGH':<25} {h_given_high:>14.3f} {(h_baseline-h_given_high)/h_baseline*100:>9.1f}%")
    print(f"  {'OL prefix':<25} {h_given_ol:>14.3f} {(h_baseline-h_given_ol)/h_baseline*100:>9.1f}%")
    print(f"  {'OR prefix':<25} {h_given_or:>14.3f} {(h_baseline-h_given_or)/h_baseline*100:>9.1f}%")
    print(f"  {'FL pair (LOW+HIGH)':<25} {h_given_fl:>14.3f} {(h_baseline-h_given_fl)/h_baseline*100:>9.1f}%")
    print(f"  {'OL+OR':<25} {h_given_olor:>14.3f} {(h_baseline-h_given_olor)/h_baseline*100:>9.1f}%")
    print(f"  {'All 4 coordinates':<25} {h_given_all4:>14.3f} {(h_baseline-h_given_all4)/h_baseline*100:>9.1f}%")

# ============================================================
# TEST E: Role composition of OL vs OR vs CENTER
# ============================================================
print(f"\n{'='*70}")
print("TEST E: ROLE COMPOSITION COMPARISON")
print(f"{'='*70}")

ol_roles = Counter(r['ol_role'] for r in line_records)
or_roles = Counter(r['or_role'] for r in line_records)
center_roles = Counter(cr for r in line_records for cr in r['center_roles'])

roles_list = ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'AUXILIARY', 'UNKNOWN']
print(f"\n  {'Position':<10}", end='')
for r in roles_list:
    print(f" {r[:8]:>9}", end='')
print()
print(f"  {'-'*58}")
for label, counter in [('OL', ol_roles), ('OR', or_roles), ('CENTER', center_roles)]:
    total = sum(counter.values())
    print(f"  {label:<10}", end='')
    for r in roles_list:
        pct = counter.get(r, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>8.1f}%", end='')
    print()

# ============================================================
# VERDICT
# ============================================================
print(f"\n{'='*70}")
print("VERDICT")
print(f"{'='*70}")

# Assess coordinate-likeness
ol_is_coordinate = ol_ttr < center_ttr * 0.8  # Lower TTR = more constrained
or_is_coordinate = or_ttr < center_ttr * 0.8
ol_or_independent = v < 0.15 if 'v' in dir() else True

# How much do all 4 predict center?
if center_entries:
    total_reduction_4 = (h_baseline - h_given_all4) / h_baseline * 100
    fl_only_reduction = (h_baseline - h_given_fl) / h_baseline * 100
    olor_only_reduction = (h_baseline - h_given_olor) / h_baseline * 100
    additive = fl_only_reduction + olor_only_reduction
else:
    total_reduction_4 = 0
    fl_only_reduction = 0
    olor_only_reduction = 0
    additive = 0

checks = {
    'ol_constrained_vocab': bool(ol_ttr < center_ttr * 0.9),
    'or_constrained_vocab': bool(or_ttr < center_ttr * 0.9),
    'ol_or_independent': bool(v < 0.15) if 'v' in dir() else False,
    'four_coords_predict_center': bool(total_reduction_4 > 10),
    'olor_adds_to_fl': bool(total_reduction_4 > fl_only_reduction * 1.3),
}

n_pass = sum(checks.values())

print(f"\n  Checks ({n_pass}/5):")
for name, val in checks.items():
    print(f"    {name:>30}: {'YES' if val else 'NO'}")

if n_pass >= 4:
    verdict = "FOUR_COORDINATE_SYSTEM"
    explanation = "OL and OR are additional coordinate dimensions beyond FL pair"
elif n_pass >= 3:
    verdict = "PARTIAL_COORDINATES"
    explanation = "OL/OR are semi-coordinate: constrained but not fully independent"
elif n_pass >= 2:
    verdict = "FRAME_OPERATORS"
    explanation = "OL/OR are operations (not coordinates) that frame the center content"
else:
    verdict = "CONTENT_NOT_COORDINATES"
    explanation = "OL/OR are regular content tokens, not addressing dimensions"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# SAVE
# ============================================================
result = {
    'n_lines': len(line_records),
    'vocabulary': {
        'ol_types': n_ol_types, 'or_types': n_or_types, 'center_types': n_center_types,
        'ol_ttr': round(float(ol_ttr), 4),
        'or_ttr': round(float(or_ttr), 4),
        'center_ttr': round(float(center_ttr), 4),
        'ol_entropy_norm': round(float(ol_entropy / ol_max_ent), 3),
        'or_entropy_norm': round(float(or_entropy / or_max_ent), 3),
        'center_entropy_norm': round(float(center_entropy / center_max_ent), 3),
    },
    'independence': {
        'ol_or_cramers_v': round(float(v), 3) if 'v' in dir() else None,
        'ol_vs_fl_low_v': round(float(v_ol), 3),
        'or_vs_fl_high_v': round(float(v_or), 3),
    },
    'predictive_power': {
        'baseline_entropy': round(float(h_baseline), 3) if center_entries else None,
        'fl_pair_reduction_pct': round(float(fl_only_reduction), 1) if center_entries else None,
        'olor_reduction_pct': round(float(olor_only_reduction), 1) if center_entries else None,
        'all4_reduction_pct': round(float(total_reduction_4), 1) if center_entries else None,
    },
    'checks': {k: bool(v) for k, v in checks.items()},
    'n_pass': int(n_pass),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "34_four_coordinate_test.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")

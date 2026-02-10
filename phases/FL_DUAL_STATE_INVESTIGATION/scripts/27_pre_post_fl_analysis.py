"""
27_pre_post_fl_analysis.py

Characterize the tokens OUTSIDE the nesting structure:
  - pre-FL: tokens before the first LOW FL bookend
  - post-FL: tokens after the last HIGH FL bookend

Are these a fourth layer? Preamble/epilogue? Or noise?
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
# Build full line profiles with all layers
# ============================================================
pre_fl_tokens = []
post_fl_tokens = []
outer_left_tokens = []
outer_right_tokens = []
center_tokens = []
all_fl_low_tokens = []
all_fl_high_tokens = []

lines_with_pre = 0
lines_with_post = 0
lines_with_both = 0
lines_total = 0

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
        middle = m.middle if m and m.middle else None
        suffix = m.suffix if m and m.suffix else 'NONE'
        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'class': cls, 'role': role,
                 'prefix': prefix, 'middle': middle, 'suffix': suffix,
                 'folio': line_key[0], 'line': line_key[1]}
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

    lines_total += 1

    # Classify all tokens
    ol_idx = gap[0]['idx']
    or_idx = gap[-1]['idx']
    gap_indices = set(g['idx'] for g in gap)

    pre = []
    post = []
    for t in all_info:
        if t['is_fl']:
            if t['mode'] == 'LOW':
                all_fl_low_tokens.append(t)
            elif t['mode'] == 'HIGH':
                all_fl_high_tokens.append(t)
        elif t['idx'] < min(f['idx'] for f in low_fls):
            pre.append(t)
        elif t['idx'] > max(f['idx'] for f in high_fls):
            post.append(t)
        elif t['idx'] == ol_idx:
            outer_left_tokens.append(t)
        elif t['idx'] == or_idx:
            outer_right_tokens.append(t)
        elif t['idx'] in gap_indices:
            center_tokens.append(t)
        # Tokens between FL clusters but outside gap (between LOW FLs,
        # or between gap and non-gap FL) are skipped

    pre_fl_tokens.extend(pre)
    post_fl_tokens.extend(post)

    has_pre = len(pre) > 0
    has_post = len(post) > 0
    if has_pre:
        lines_with_pre += 1
    if has_post:
        lines_with_post += 1
    if has_pre and has_post:
        lines_with_both += 1

print(f"Lines analyzed: {lines_total}")
print(f"Lines with pre-FL tokens: {lines_with_pre} ({lines_with_pre/lines_total*100:.0f}%)")
print(f"Lines with post-FL tokens: {lines_with_post} ({lines_with_post/lines_total*100:.0f}%)")
print(f"Lines with both: {lines_with_both} ({lines_with_both/lines_total*100:.0f}%)")
print(f"\nToken counts:")
print(f"  pre-FL:    {len(pre_fl_tokens)}")
print(f"  FL-LOW:    {len(all_fl_low_tokens)}")
print(f"  OUTER-L:   {len(outer_left_tokens)}")
print(f"  CENTER:    {len(center_tokens)}")
print(f"  OUTER-R:   {len(outer_right_tokens)}")
print(f"  FL-HIGH:   {len(all_fl_high_tokens)}")
print(f"  post-FL:   {len(post_fl_tokens)}")

# ============================================================
# TEST 1: Role distribution comparison
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: ROLE DISTRIBUTION BY LAYER (including pre/post)")
print(f"{'='*60}")

all_layers = [
    ('pre-FL', pre_fl_tokens),
    ('OUTER-L', outer_left_tokens),
    ('CENTER', center_tokens),
    ('OUTER-R', outer_right_tokens),
    ('post-FL', post_fl_tokens),
]

roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR',
         'CORE_CONTROL', 'FLOW_OPERATOR']

print(f"\n  {'Layer':>10}", end='')
for r in roles:
    print(f" {r[:6]:>7}", end='')
print(f" {'n':>6}")
print(f"  {'-'*65}")

for label, tokens in all_layers:
    total = len(tokens)
    if total == 0:
        continue
    role_counts = Counter(t['role'] for t in tokens)
    print(f"  {label:>10}", end='')
    for r in roles:
        pct = role_counts.get(r, 0) / total * 100
        print(f" {pct:>6.1f}%", end='')
    print(f" {total:>6}")

# ============================================================
# TEST 2: Prefix distribution comparison
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: PREFIX DISTRIBUTION BY LAYER")
print(f"{'='*60}")

top_prefixes = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot', 'ol', 'da', 'lk', 'pch']

print(f"\n  {'Layer':>10}", end='')
for p in top_prefixes:
    print(f" {p:>6}", end='')
print(f" {'n':>6}")
print(f"  {'-'*80}")

for label, tokens in all_layers:
    total = len(tokens)
    if total == 0:
        continue
    pfx_counts = Counter(t['prefix'] for t in tokens)
    print(f"  {label:>10}", end='')
    for p in top_prefixes:
        pct = pfx_counts.get(p, 0) / total * 100
        print(f" {pct:>5.1f}%", end='')
    print(f" {total:>6}")

# Chi-squared: layer x prefix (including pre/post)
table_rows = []
for label, tokens in all_layers:
    if len(tokens) < 10:
        continue
    pfx_counts = Counter(t['prefix'] for t in tokens)
    table_rows.append([pfx_counts.get(p, 0) for p in top_prefixes])

table = np.array(table_rows)
col_mask = table.sum(axis=0) > 0
table = table[:, col_mask]
if table.shape[0] >= 2 and table.shape[1] >= 2:
    chi2, p_val, dof, _ = chi2_contingency(table)
    v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
    print(f"\n  Layer x Prefix (5 layers): chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")

# ============================================================
# TEST 3: Class distribution comparison
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: CLASS DISTRIBUTION (pre/post vs inner layers)")
print(f"{'='*60}")

for label, tokens in [('pre-FL', pre_fl_tokens), ('post-FL', post_fl_tokens)]:
    cls_counts = Counter(t['class'] for t in tokens if t['class'] is not None)
    total_cls = sum(cls_counts.values())
    total = len(tokens)
    unclassified = total - total_cls
    print(f"\n  {label} (n={total}, classified={total_cls}, unclassified={unclassified} [{unclassified/total*100:.0f}%]):")
    for cls, count in cls_counts.most_common(10):
        print(f"    Class {cls:>3}: {count:>5} ({count/total_cls*100:.1f}%)")

# ============================================================
# TEST 4: Token length and morphological complexity
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: TOKEN LENGTH AND COMPLEXITY")
print(f"{'='*60}")

def morph_complexity(token):
    slots = 0
    if token['prefix'] != 'NONE':
        slots += 1
    if token['middle']:
        slots += 1
    if token['suffix'] != 'NONE':
        slots += 1
    return slots

print(f"\n  {'Layer':>10} {'mean_len':>9} {'med_len':>8} {'mean_slots':>11} {'3-slot%':>8}")
print(f"  {'-'*50}")

for label, tokens in all_layers:
    if not tokens:
        continue
    lengths = [len(t['word']) for t in tokens]
    complexities = [morph_complexity(t) for t in tokens]
    three_slot = sum(1 for c in complexities if c == 3) / len(complexities) * 100
    print(f"  {label:>10} {np.mean(lengths):>9.1f} {np.median(lengths):>8.0f} "
          f"{np.mean(complexities):>11.2f} {three_slot:>7.1f}%")

# ============================================================
# TEST 5: Unclassified rate by layer
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: UNCLASSIFIED TOKEN RATE")
print(f"{'='*60}")

for label, tokens in all_layers:
    if not tokens:
        continue
    unclassified = sum(1 for t in tokens if t['class'] is None)
    total = len(tokens)
    print(f"  {label:>10}: {unclassified}/{total} ({unclassified/total*100:.1f}%) unclassified")

# ============================================================
# TEST 6: Do pre-FL tokens predict the FL pair?
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: DO PRE-FL TOKENS PREDICT THE FL PAIR?")
print(f"{'='*60}")

# Rebuild with pair info
pair_pre_words = defaultdict(Counter)
pair_post_words = defaultdict(Counter)

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
        stage = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]

        role = token_to_role.get(t.word, 'UNKNOWN')
        all_info.append({'word': t.word, 'idx': idx, 'is_fl': is_fl,
                         'mode': mode, 'stage': stage, 'role': role})
        if is_fl and mode:
            fl_info.append({'word': t.word, 'idx': idx, 'mode': mode, 'stage': stage})

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    pair = (low_stage, high_stage)

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]
    if len(gap) < 3:
        continue

    min_fl_idx = min(f['idx'] for f in low_fls)
    max_fl_idx = max(f['idx'] for f in high_fls)

    pre = [t for t in all_info if not t['is_fl'] and t['idx'] < min_fl_idx]
    post = [t for t in all_info if not t['is_fl'] and t['idx'] > max_fl_idx]

    for t in pre:
        pair_pre_words[pair][t['word']] += 1
    for t in post:
        pair_post_words[pair][t['word']] += 1

# Cramer's V for pre-FL words x pair
top_pairs = [p for p, c in Counter(pair_pre_words.keys()).items()
             if sum(pair_pre_words[p].values()) >= 15]

if not top_pairs:
    # Use pairs with enough data
    pair_totals = {p: sum(wc.values()) for p, wc in pair_pre_words.items()}
    top_pairs = [p for p, t in sorted(pair_totals.items(), key=lambda x: -x[1]) if t >= 15]

all_pre_words = Counter()
for p, wc in pair_pre_words.items():
    all_pre_words += wc
top_pre_words = [w for w, _ in all_pre_words.most_common(30)]

if len(top_pairs) >= 2 and len(top_pre_words) >= 2:
    table = np.array([[pair_pre_words[p].get(w, 0) for w in top_pre_words]
                       for p in top_pairs])
    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table = table[row_mask][:, col_mask]
    if table.shape[0] >= 2 and table.shape[1] >= 2:
        chi2, p_val, dof, _ = chi2_contingency(table)
        v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
        print(f"  Pre-FL words x Pair: chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")
        pre_v = v
    else:
        print("  Insufficient data for pre-FL x pair test")
        pre_v = 0
else:
    print(f"  Only {len(top_pairs)} pairs with enough pre-FL data")
    pre_v = 0

# Same for post-FL
all_post_words = Counter()
for p, wc in pair_post_words.items():
    all_post_words += wc
top_post_words = [w for w, _ in all_post_words.most_common(30)]

post_pairs = [p for p in pair_post_words if sum(pair_post_words[p].values()) >= 15]

if len(post_pairs) >= 2 and len(top_post_words) >= 2:
    table = np.array([[pair_post_words[p].get(w, 0) for w in top_post_words]
                       for p in post_pairs])
    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table = table[row_mask][:, col_mask]
    if table.shape[0] >= 2 and table.shape[1] >= 2:
        chi2, p_val, dof, _ = chi2_contingency(table)
        v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
        print(f"  Post-FL words x Pair: chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")
        post_v = v
    else:
        print("  Insufficient data for post-FL x pair test")
        post_v = 0
else:
    print(f"  Only {len(post_pairs)} pairs with enough post-FL data")
    post_v = 0

# ============================================================
# TEST 7: Top words in pre-FL and post-FL
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: TOP WORDS IN PRE-FL AND POST-FL")
print(f"{'='*60}")

print("\n  Pre-FL top words:")
for w, c in all_pre_words.most_common(15):
    cls = token_to_class.get(w, '?')
    role = token_to_role.get(w, 'UNKNOWN')
    print(f"    {w:>14} ({c:>3}) class={cls} role={role}")

print("\n  Post-FL top words:")
for w, c in all_post_words.most_common(15):
    cls = token_to_class.get(w, '?')
    role = token_to_role.get(w, 'UNKNOWN')
    print(f"    {w:>14} ({c:>3}) class={cls} role={role}")

# ============================================================
# TEST 8: Are pre/post tokens FL-like (contain FL MIDDLEs)?
# ============================================================
print(f"\n{'='*60}")
print("TEST 8: FL-LIKE CONTENT IN PRE/POST TOKENS")
print(f"{'='*60}")

for label, tokens in [('pre-FL', pre_fl_tokens), ('post-FL', post_fl_tokens)]:
    fl_like = sum(1 for t in tokens if t['middle'] and t['middle'] in FL_STAGE_MAP)
    total = len(tokens)
    print(f"  {label:>10}: {fl_like}/{total} ({fl_like/total*100:.1f}%) contain FL MIDDLEs")

    # What MIDDLEs do they have?
    mid_counts = Counter(t['middle'] for t in tokens if t['middle'] and t['middle'] in FL_STAGE_MAP)
    if mid_counts:
        top3 = mid_counts.most_common(5)
        mid_str = ', '.join(f"{m}({c})" for m, c in top3)
        print(f"             FL MIDDLEs: {mid_str}")

# ============================================================
# TEST 9: Position within line
# ============================================================
print(f"\n{'='*60}")
print("TEST 9: MEAN POSITION IN LINE")
print(f"{'='*60}")

for label, tokens in all_layers:
    if not tokens:
        continue
    positions = [t['pos'] for t in tokens]
    print(f"  {label:>10}: mean={np.mean(positions):.3f}, std={np.std(positions):.3f}")

# Also FL positions
print(f"  {'FL-LOW':>10}: mean={np.mean([t['pos'] for t in all_fl_low_tokens]):.3f}")
print(f"  {'FL-HIGH':>10}: mean={np.mean([t['pos'] for t in all_fl_high_tokens]):.3f}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

# Compare pre/post to inner layers
pre_unk_rate = sum(1 for t in pre_fl_tokens if t['role'] == 'UNKNOWN') / len(pre_fl_tokens) if pre_fl_tokens else 0
post_unk_rate = sum(1 for t in post_fl_tokens if t['role'] == 'UNKNOWN') / len(post_fl_tokens) if post_fl_tokens else 0
center_unk_rate = sum(1 for t in center_tokens if t['role'] == 'UNKNOWN') / len(center_tokens) if center_tokens else 0

pre_uncls_rate = sum(1 for t in pre_fl_tokens if t['class'] is None) / len(pre_fl_tokens) if pre_fl_tokens else 0
post_uncls_rate = sum(1 for t in post_fl_tokens if t['class'] is None) / len(post_fl_tokens) if post_fl_tokens else 0
center_uncls_rate = sum(1 for t in center_tokens if t['class'] is None) / len(center_tokens) if center_tokens else 0

pre_longer = np.mean([len(t['word']) for t in pre_fl_tokens]) if pre_fl_tokens else 0
post_longer = np.mean([len(t['word']) for t in post_fl_tokens]) if post_fl_tokens else 0
center_len = np.mean([len(t['word']) for t in center_tokens]) if center_tokens else 0

# Pre/post are more UNKNOWN and unclassified -> they are DIFFERENT from inner layers
pre_distinct = pre_unk_rate > center_unk_rate + 0.05 or pre_uncls_rate > center_uncls_rate + 0.05
post_distinct = post_unk_rate > center_unk_rate + 0.05 or post_uncls_rate > center_uncls_rate + 0.05

# Do they predict the pair?
pre_predictive = pre_v > 0.15
post_predictive = post_v > 0.15

print(f"  Pre-FL distinct from center: {'YES' if pre_distinct else 'NO'}")
print(f"    UNKNOWN rate: pre={pre_unk_rate:.1%} vs center={center_unk_rate:.1%}")
print(f"    Unclassified: pre={pre_uncls_rate:.1%} vs center={center_uncls_rate:.1%}")
print(f"    Mean length:  pre={pre_longer:.1f} vs center={center_len:.1f}")

print(f"  Post-FL distinct from center: {'YES' if post_distinct else 'NO'}")
print(f"    UNKNOWN rate: post={post_unk_rate:.1%} vs center={center_unk_rate:.1%}")
print(f"    Unclassified: post={post_uncls_rate:.1%} vs center={center_uncls_rate:.1%}")
print(f"    Mean length:  post={post_longer:.1f} vs center={center_len:.1f}")

print(f"  Pre-FL predicts pair: {'YES' if pre_predictive else 'NO'} (V={pre_v:.3f})")
print(f"  Post-FL predicts pair: {'YES' if post_predictive else 'NO'} (V={post_v:.3f})")

if pre_distinct and post_distinct:
    if pre_predictive or post_predictive:
        verdict = "FOURTH_LAYER_ADDRESSING"
        explanation = "Pre/post tokens are distinct from center AND carry pair-specific information"
    else:
        verdict = "FOURTH_LAYER_GENERIC"
        explanation = "Pre/post tokens are morphologically distinct but don't address the FL pair"
elif pre_distinct or post_distinct:
    verdict = "ASYMMETRIC_FRINGE"
    explanation = "One side (pre or post) is distinct, the other resembles center"
else:
    verdict = "NO_FOURTH_LAYER"
    explanation = "Pre/post tokens are not meaningfully different from center"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# Full layer model
print(f"\n  FULL LINE MODEL:")
print(f"  [pre-FL?] [FL-LOW] [OUTER-L] [CENTER...] [OUTER-R] [FL-HIGH] [post-FL?]")
print(f"  present:  {lines_with_pre/lines_total*100:.0f}%       100%      100%     100%        100%      100%       {lines_with_post/lines_total*100:.0f}%")

# Save
result = {
    'n_lines': lines_total,
    'n_pre_fl_tokens': len(pre_fl_tokens),
    'n_post_fl_tokens': len(post_fl_tokens),
    'pct_lines_with_pre': round(lines_with_pre / lines_total * 100, 1),
    'pct_lines_with_post': round(lines_with_post / lines_total * 100, 1),
    'pre_unknown_rate': round(pre_unk_rate, 3),
    'post_unknown_rate': round(post_unk_rate, 3),
    'center_unknown_rate': round(center_unk_rate, 3),
    'pre_unclassified_rate': round(pre_uncls_rate, 3),
    'post_unclassified_rate': round(post_uncls_rate, 3),
    'pre_pair_cramers_v': round(float(pre_v), 3),
    'post_pair_cramers_v': round(float(post_v), 3),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "27_pre_post_fl_analysis.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")

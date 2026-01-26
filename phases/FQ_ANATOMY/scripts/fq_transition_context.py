"""
FQ_ANATOMY Script 2: Transition and Context Analysis

Internal FQ transition grammar, context differentiation,
FQ-FL class-level symbiosis, boundary behavior.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
SR_FEATURES = BASE / 'phases/SMALL_ROLE_ANATOMY/results/sr_features.json'
RESULTS = BASE / 'phases/FQ_ANATOMY/results'

FQ_CLASSES = {9, 13, 14, 23}
FL_CLASSES = {7, 30, 38, 40}
FQ_BARE = {9, 23}
FQ_PREFIXED = {13, 14}

# Corrected role mapping
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 14, 23}

def get_role(cls):
    if cls is None:
        return 'UN'
    if cls in ICC_CC:
        return 'CC'
    if cls in ICC_EN:
        return 'EN'
    if cls in ICC_FL:
        return 'FL'
    if cls in ICC_FQ:
        return 'FQ'
    return 'AX'

# Load data
print("=" * 70)
print("FQ TRANSITION AND CONTEXT ANALYSIS")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

with open(SR_FEATURES) as f:
    sr_features = json.load(f)

# Build line structures
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    role = get_role(cls)
    lines[(token.folio, token.line)].append({
        'word': word, 'class': cls, 'role': role, 'folio': token.folio
    })

results = {}

# ============================================================
# SECTION 1: FQ INTERNAL TRANSITION MATRIX
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: FQ INTERNAL TRANSITION MATRIX")
print("=" * 70)

fq_sorted = sorted(FQ_CLASSES)
trans_matrix = defaultdict(lambda: defaultdict(int))
fq_fq_pairs = 0

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        src_cls = line_tokens[i]['class']
        dst_cls = line_tokens[i + 1]['class']
        if src_cls in FQ_CLASSES and dst_cls in FQ_CLASSES:
            trans_matrix[src_cls][dst_cls] += 1
            fq_fq_pairs += 1

print(f"\nTotal FQ->FQ adjacent pairs: {fq_fq_pairs}")

# Count per-class as source
src_totals = {cls: sum(trans_matrix[cls].values()) for cls in fq_sorted}

# Print matrix
print(f"\nTransition matrix (raw counts):")
print(f"{'':>8}", end='')
for c in fq_sorted:
    print(f" {c:>5}", end='')
print(f" {'Total':>6}")
for src in fq_sorted:
    print(f"  {src:>4}:", end='')
    for dst in fq_sorted:
        print(f" {trans_matrix[src][dst]:>5}", end='')
    print(f" {src_totals[src]:>6}")

# Expected under independence
class_as_dst = defaultdict(int)
for src in fq_sorted:
    for dst in fq_sorted:
        class_as_dst[dst] += trans_matrix[src][dst]

total_dst = sum(class_as_dst.values())
dst_probs = {cls: class_as_dst[cls] / total_dst if total_dst > 0 else 0 for cls in fq_sorted}

# Enrichment
print(f"\nEnrichment matrix (observed / expected):")
enrichment_matrix = {}
print(f"{'':>8}", end='')
for c in fq_sorted:
    print(f" {c:>6}", end='')
print()
for src in fq_sorted:
    print(f"  {src:>4}:", end='')
    enrichment_matrix[src] = {}
    for dst in fq_sorted:
        observed = trans_matrix[src][dst] / src_totals[src] if src_totals[src] > 0 else 0
        expected = dst_probs[dst]
        enrich = observed / expected if expected > 0 else 0
        enrichment_matrix[src][dst] = enrich
        marker = '+' if enrich > 1.3 else '-' if enrich < 0.7 else ' '
        print(f" {enrich:5.2f}{marker}", end='')
    print()

# Chi-squared for overall non-randomness
observed_flat = []
expected_flat = []
for src in fq_sorted:
    for dst in fq_sorted:
        observed_flat.append(trans_matrix[src][dst])
        expected_flat.append(src_totals[src] * dst_probs[dst] if src_totals[src] > 0 else 0)

obs_arr = np.array(observed_flat)
exp_arr = np.array(expected_flat)
# Only use cells with expected >= 1
mask = exp_arr >= 1
if mask.sum() > 1:
    chi2_overall = float(np.sum((obs_arr[mask] - exp_arr[mask]) ** 2 / exp_arr[mask]))
    df = int(mask.sum()) - 1
    p_overall = 1 - stats.chi2.cdf(chi2_overall, df)
    print(f"\nOverall chi-squared: {chi2_overall:.2f}, df={df}, p={p_overall:.4f}")
    print(f"Non-random: {'YES' if p_overall < 0.01 else 'NO'}")
else:
    chi2_overall = 0
    p_overall = 1.0
    print(f"\nInsufficient expected counts for chi-squared")

# Directional asymmetry
print(f"\nDirectional asymmetry (A->B vs B->A):")
for i, c1 in enumerate(fq_sorted):
    for j, c2 in enumerate(fq_sorted):
        if j <= i:
            continue
        ab = trans_matrix[c1][c2]
        ba = trans_matrix[c2][c1]
        total = ab + ba
        if total >= 5:
            ratio = ab / ba if ba > 0 else float('inf')
            print(f"  {c1}->{c2}: {ab}  {c2}->{c1}: {ba}  ratio={ratio:.2f}")

# Aggregate to 2x2: BARE/PREFIXED
print(f"\n2x2 Aggregate (BARE vs PREFIXED):")
agg = [[0, 0], [0, 0]]  # [bare->bare, bare->pref], [pref->bare, pref->pref]
for src in fq_sorted:
    for dst in fq_sorted:
        si = 0 if src in FQ_BARE else 1
        di = 0 if dst in FQ_BARE else 1
        agg[si][di] += trans_matrix[src][dst]

agg_arr = np.array(agg)
print(f"         BARE  PREF")
print(f"  BARE  {agg[0][0]:5d} {agg[0][1]:5d}")
print(f"  PREF  {agg[1][0]:5d} {agg[1][1]:5d}")

if all(agg_arr.flatten() > 0):
    chi2_agg, p_agg, dof_agg, exp_agg = stats.chi2_contingency(agg_arr)
    print(f"  chi2={chi2_agg:.2f}, p={p_agg:.4f}")
else:
    odds_agg, p_agg = stats.fisher_exact(agg_arr)
    chi2_agg = None
    print(f"  Fisher exact p={p_agg:.4f}")

results['internal_transitions'] = {
    'total_pairs': fq_fq_pairs,
    'matrix': {str(src): {str(dst): trans_matrix[src][dst] for dst in fq_sorted} for src in fq_sorted},
    'enrichment': {str(src): {str(dst): round(enrichment_matrix[src][dst], 3) for dst in fq_sorted} for src in fq_sorted},
    'chi2_overall': round(chi2_overall, 2),
    'p_overall': float(p_overall),
    'non_random': p_overall < 0.01,
    'aggregate_2x2': agg,
    'aggregate_p': float(p_agg),
}

# ============================================================
# SECTION 2: FQ-NON-FQ CONTEXT PROFILES
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: FQ CONTEXT PROFILES")
print("=" * 70)

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
left_ctx = defaultdict(lambda: Counter())
right_ctx = defaultdict(lambda: Counter())

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls not in FQ_CLASSES:
            continue
        # Left context
        if i > 0:
            left_ctx[cls][line_tokens[i - 1]['role']] += 1
        # Right context
        if i < n - 1:
            right_ctx[cls][line_tokens[i + 1]['role']] += 1

# JS divergence between classes on context profiles
print(f"\nContext profile JS divergence (pairwise):")
ctx_js = {}
for i, c1 in enumerate(fq_sorted):
    for j, c2 in enumerate(fq_sorted):
        if j <= i:
            continue
        # Build combined left+right vector
        v1 = np.array([left_ctx[c1].get(r, 0) for r in ROLES] + [right_ctx[c1].get(r, 0) for r in ROLES], dtype=float)
        v2 = np.array([left_ctx[c2].get(r, 0) for r in ROLES] + [right_ctx[c2].get(r, 0) for r in ROLES], dtype=float)
        v1_n = v1 / v1.sum() if v1.sum() > 0 else v1
        v2_n = v2 / v2.sum() if v2.sum() > 0 else v2
        m = (v1_n + v2_n) / 2
        # KL
        def kl(p, q):
            mask = (p > 0) & (q > 0)
            return float(np.sum(p[mask] * np.log2(p[mask] / q[mask])))
        js = 0.5 * kl(v1_n, m) + 0.5 * kl(v2_n, m)
        ctx_js[f"{c1}-{c2}"] = round(js, 6)
        print(f"  {c1} vs {c2}: JS={js:.6f}")

# Largest context differences
print(f"\nPer-class context summary (left/right EN rate):")
for cls in fq_sorted:
    l_total = sum(left_ctx[cls].values())
    r_total = sum(right_ctx[cls].values())
    l_en = left_ctx[cls].get('EN', 0) / l_total if l_total > 0 else 0
    r_en = right_ctx[cls].get('EN', 0) / r_total if r_total > 0 else 0
    l_fl = left_ctx[cls].get('FL', 0) / l_total if l_total > 0 else 0
    r_fl = right_ctx[cls].get('FL', 0) / r_total if r_total > 0 else 0
    print(f"  Class {cls}: left_EN={l_en:.3f} right_EN={r_en:.3f}  left_FL={l_fl:.3f} right_FL={r_fl:.3f}")

results['context_profiles'] = {
    'pairwise_js': ctx_js,
    'left_context': {str(cls): dict(left_ctx[cls]) for cls in fq_sorted},
    'right_context': {str(cls): dict(right_ctx[cls]) for cls in fq_sorted},
}

# ============================================================
# SECTION 3: CONTEXT CLASSIFIER
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: CONTEXT CLASSIFIER")
print("=" * 70)

# Build dataset: (left_role, right_role) -> FQ class
context_data = []
for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls not in FQ_CLASSES:
            continue
        left_role = line_tokens[i - 1]['role'] if i > 0 else 'BND'
        right_role = line_tokens[i + 1]['role'] if i < n - 1 else 'BND'
        context_data.append((left_role, right_role, cls))

# Majority baseline
class_counts = Counter(d[2] for d in context_data)
majority_class = class_counts.most_common(1)[0][0]
majority_rate = class_counts[majority_class] / len(context_data) if context_data else 0

# Weighted random baseline
total_n = len(context_data)
weighted_random = sum((cnt / total_n) ** 2 for cnt in class_counts.values())

# Rule-based classifier: for each (left, right), predict most common class
context_to_class = defaultdict(Counter)
for left, right, cls in context_data:
    context_to_class[(left, right)][cls] += 1

correct = 0
for left, right, cls in context_data:
    predicted = context_to_class[(left, right)].most_common(1)[0][0]
    if predicted == cls:
        correct += 1

accuracy = correct / len(context_data) if context_data else 0
improvement = accuracy - majority_rate

print(f"\nDataset: {len(context_data)} FQ tokens with context")
print(f"Class distribution: {dict(class_counts)}")
print(f"Majority baseline (Class {majority_class}): {majority_rate:.4f}")
print(f"Weighted random baseline: {weighted_random:.4f}")
print(f"Classifier accuracy: {accuracy:.4f}")
print(f"Improvement over majority: {improvement:+.4f}")
print(f"Improvement over weighted random: {accuracy - weighted_random:+.4f}")

results['context_classifier'] = {
    'n_samples': len(context_data),
    'class_distribution': dict(class_counts),
    'majority_baseline': round(majority_rate, 4),
    'weighted_random': round(weighted_random, 4),
    'accuracy': round(accuracy, 4),
    'improvement_majority': round(improvement, 4),
    'improvement_weighted': round(accuracy - weighted_random, 4),
}

# ============================================================
# SECTION 4: FQ-FL CLASS-LEVEL SYMBIOSIS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: FQ-FL CLASS-LEVEL SYMBIOSIS")
print("=" * 70)

fl_sorted = sorted(FL_CLASSES)
fq_fl_adj = defaultdict(lambda: defaultdict(int))
fl_fq_adj = defaultdict(lambda: defaultdict(int))
fq_fl_total = 0
fl_fq_total = 0

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        src = line_tokens[i]
        dst = line_tokens[i + 1]
        if src['class'] in FQ_CLASSES and dst['class'] in FL_CLASSES:
            fq_fl_adj[src['class']][dst['class']] += 1
            fq_fl_total += 1
        if src['class'] in FL_CLASSES and dst['class'] in FQ_CLASSES:
            fl_fq_adj[src['class']][dst['class']] += 1
            fl_fq_total += 1

print(f"\nFQ->FL adjacent pairs: {fq_fl_total}")
print(f"FL->FQ adjacent pairs: {fl_fq_total}")

# FQ->FL matrix
print(f"\nFQ->FL matrix:")
print(f"{'':>8}", end='')
for c in fl_sorted:
    print(f" FL{c:>3}", end='')
print(f" {'Total':>6}")
fq_fl_matrix = {}
for src in fq_sorted:
    print(f"  FQ{src:>2}:", end='')
    row_total = sum(fq_fl_adj[src][dst] for dst in fl_sorted)
    fq_fl_matrix[src] = {}
    for dst in fl_sorted:
        cnt = fq_fl_adj[src][dst]
        fq_fl_matrix[src][dst] = cnt
        print(f" {cnt:>5}", end='')
    print(f" {row_total:>6}")

# FL->FQ matrix
print(f"\nFL->FQ matrix:")
print(f"{'':>8}", end='')
for c in fq_sorted:
    print(f" FQ{c:>3}", end='')
print(f" {'Total':>6}")
fl_fq_matrix = {}
for src in fl_sorted:
    print(f"  FL{src:>2}:", end='')
    row_total = sum(fl_fq_adj[src][dst] for dst in fq_sorted)
    fl_fq_matrix[src] = {}
    for dst in fq_sorted:
        cnt = fl_fq_adj[src][dst]
        fl_fq_matrix[src][dst] = cnt
        print(f" {cnt:>5}", end='')
    print(f" {row_total:>6}")

# Chi-squared or Fisher on FQ->FL 4x4
fq_fl_arr = np.array([[fq_fl_adj[src][dst] for dst in fl_sorted] for src in fq_sorted])
# Check minimum expected counts
row_sums = fq_fl_arr.sum(axis=1)
col_sums = fq_fl_arr.sum(axis=0)
total = fq_fl_arr.sum()
if total > 0:
    expected = np.outer(row_sums, col_sums) / total
    min_expected = expected.min()
    print(f"\nFQ->FL expected min cell: {min_expected:.2f}")

    if min_expected >= 5:
        chi2_fqfl, p_fqfl, dof_fqfl, _ = stats.chi2_contingency(fq_fl_arr)
        print(f"Chi-squared: {chi2_fqfl:.2f}, df={dof_fqfl}, p={p_fqfl:.4f}")
        test_type = 'chi2'
    else:
        # Use chi-squared anyway with caveat
        chi2_fqfl, p_fqfl, dof_fqfl, _ = stats.chi2_contingency(fq_fl_arr)
        print(f"Chi-squared (caveat: min expected={min_expected:.2f}<5): {chi2_fqfl:.2f}, df={dof_fqfl}, p={p_fqfl:.4f}")
        test_type = 'chi2_sparse'
else:
    chi2_fqfl = 0
    p_fqfl = 1.0
    test_type = 'no_data'
    print(f"No FQ->FL transitions found")

# Hazard alignment check
print(f"\nHazard alignment in FQ-FL:")
FQ_HAZ = {9, 23}
FL_HAZ = {7, 30}
FQ_SAFE_SET = {13, 14}
FL_SAFE_SET = {38, 40}

haz_haz = sum(fq_fl_adj[s][d] + fl_fq_adj[d][s] for s in FQ_HAZ for d in FL_HAZ)
haz_safe = sum(fq_fl_adj[s][d] + fl_fq_adj[d][s] for s in FQ_HAZ for d in FL_SAFE_SET)
safe_haz = sum(fq_fl_adj[s][d] + fl_fq_adj[d][s] for s in FQ_SAFE_SET for d in FL_HAZ)
safe_safe = sum(fq_fl_adj[s][d] + fl_fq_adj[d][s] for s in FQ_SAFE_SET for d in FL_SAFE_SET)

print(f"  Haz-Haz: {haz_haz}  Haz-Safe: {haz_safe}")
print(f"  Safe-Haz: {safe_haz}  Safe-Safe: {safe_safe}")

haz_arr = np.array([[haz_haz, haz_safe], [safe_haz, safe_safe]])
if haz_arr.sum() > 0 and all(haz_arr.flatten() >= 0):
    if any(haz_arr.flatten() < 5):
        odds_haz, p_haz = stats.fisher_exact(haz_arr)
        print(f"  Fisher exact: odds={odds_haz:.2f}, p={p_haz:.4f}")
    else:
        chi2_h, p_haz, _, _ = stats.chi2_contingency(haz_arr)
        odds_haz = (haz_haz * safe_safe) / (haz_safe * safe_haz) if haz_safe > 0 and safe_haz > 0 else float('inf')
        print(f"  Chi-squared: {chi2_h:.2f}, p={p_haz:.4f}, odds={odds_haz:.2f}")
else:
    p_haz = 1.0
    odds_haz = 1.0

results['fq_fl_symbiosis'] = {
    'fq_fl_total': fq_fl_total,
    'fl_fq_total': fl_fq_total,
    'fq_fl_matrix': {str(s): {str(d): fq_fl_adj[s][d] for d in fl_sorted} for s in fq_sorted},
    'fl_fq_matrix': {str(s): {str(d): fl_fq_adj[s][d] for d in fq_sorted} for s in fl_sorted},
    'chi2_fqfl': round(chi2_fqfl, 2) if chi2_fqfl else None,
    'p_fqfl': float(p_fqfl),
    'test_type': test_type,
    'hazard_alignment': {
        'haz_haz': haz_haz, 'haz_safe': haz_safe,
        'safe_haz': safe_haz, 'safe_safe': safe_safe,
        'p': float(p_haz),
    },
}

# ============================================================
# SECTION 5: FQ BOUNDARY BEHAVIOR
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: FQ BOUNDARY BEHAVIOR")
print("=" * 70)

# Per-class initial/final rates and FQ run lengths
class_initial = defaultdict(int)
class_final = defaultdict(int)
class_total = defaultdict(int)

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n == 0:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls in FQ_CLASSES:
            class_total[cls] += 1
            if i == 0:
                class_initial[cls] += 1
            if i == n - 1:
                class_final[cls] += 1

print(f"\nPer-class boundary rates:")
print(f"{'Class':>6} {'Tokens':>7} {'Initial%':>9} {'Final%':>8}")
for cls in fq_sorted:
    n = class_total[cls]
    init_r = class_initial[cls] / n if n > 0 else 0
    fin_r = class_final[cls] / n if n > 0 else 0
    print(f"  {cls:>4} {n:>7} {init_r*100:>8.1f}% {fin_r*100:>7.1f}%")

# FQ final enrichment source
total_fq_final = sum(class_final[cls] for cls in fq_sorted)
print(f"\nFQ final tokens: {total_fq_final}")
for cls in fq_sorted:
    share = class_final[cls] / total_fq_final if total_fq_final > 0 else 0
    print(f"  Class {cls}: {class_final[cls]} ({share*100:.1f}% of FQ finals)")

# FQ run lengths
fq_runs = []
for (folio, line_id), line_tokens in lines.items():
    current_run = 0
    current_cls = None
    for tok in line_tokens:
        cls = tok['class']
        if cls in FQ_CLASSES:
            current_run += 1
        else:
            if current_run > 0:
                fq_runs.append(current_run)
            current_run = 0
    if current_run > 0:
        fq_runs.append(current_run)

run_counter = Counter(fq_runs)
mean_run = np.mean(fq_runs) if fq_runs else 0
print(f"\nFQ run lengths:")
print(f"  Total runs: {len(fq_runs)}")
print(f"  Mean run length: {mean_run:.2f}")
print(f"  Distribution: {dict(sorted(run_counter.items()))}")

results['boundary_behavior'] = {
    'per_class': {
        str(cls): {
            'tokens': class_total[cls],
            'initial': class_initial[cls],
            'final': class_final[cls],
            'initial_rate': round(class_initial[cls] / class_total[cls], 4) if class_total[cls] > 0 else 0,
            'final_rate': round(class_final[cls] / class_total[cls], 4) if class_total[cls] > 0 else 0,
        }
        for cls in fq_sorted
    },
    'final_share': {
        str(cls): round(class_final[cls] / total_fq_final, 4) if total_fq_final > 0 else 0
        for cls in fq_sorted
    },
    'run_lengths': {
        'total_runs': len(fq_runs),
        'mean': round(float(mean_run), 2),
        'distribution': dict(sorted(run_counter.items())),
    },
}

# Save results
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'fq_transition_context.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'fq_transition_context.json'}")

"""
16_kernel_gap_analysis.py

Test whether kernel operators in the gap between FL LOW and FL HIGH clusters
show profiles that correlate with the LOW->HIGH stage relationship.

If LOW = input specification and HIGH = resulting state, then:
- The kernel operators between them should differ based on the stage gap
- Lines where LOW and HIGH are at the same stage should have different
  kernel profiles than lines where HIGH is advanced from LOW
- The kernel "work" should predict the stage transition

Approach:
1. For each multi-FL line, identify the LOW cluster, gap, and HIGH cluster
2. Characterize the gap tokens: what roles, how many, what kernel profile
3. Test: does gap composition correlate with (HIGH_stage - LOW_stage)?
4. Test: do specific kernel operators predict stage advancement?
"""
import sys
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import spearmanr, kruskal

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

MIN_N = 50
tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']
token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}

# ============================================================
# Build line data and assign FL modes
# ============================================================
from sklearn.mixture import GaussianMixture

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Collect FL positions per MIDDLE for GMM
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

# Fit GMMs
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
# For each line, identify LOW cluster, gap, HIGH cluster
# ============================================================
line_decompositions = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 3:
        continue

    # Annotate each token
    annotated = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP
        pos = idx / (n - 1)

        mode = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        role = token_to_role.get(t.word, 'UNKNOWN')
        cls = token_to_class.get(t.word, -1)

        # Kernel character analysis
        has_k = 'k' in t.word and mid != 'k' if m else False
        has_t = 't' in t.word if m else False
        has_p = 'p' in t.word if m else False
        has_f = 'f' in t.word if m else False

        annotated.append({
            'word': t.word,
            'idx': idx,
            'pos': pos,
            'is_fl': is_fl,
            'fl_middle': mid if is_fl else None,
            'fl_stage': FL_STAGE_MAP[mid][0] if is_fl and mid in FL_STAGE_MAP else None,
            'fl_stage_order': STAGE_ORDER.get(FL_STAGE_MAP[mid][0], -1) if is_fl and mid in FL_STAGE_MAP else -1,
            'fl_mode': mode,
            'role': role,
            'token_class': cls,
        })

    # Find LOW and HIGH FL tokens
    low_fls = [a for a in annotated if a['fl_mode'] == 'LOW']
    high_fls = [a for a in annotated if a['fl_mode'] == 'HIGH']

    if not low_fls or not high_fls:
        continue

    # Define the gap: tokens between last LOW FL and first HIGH FL
    last_low_idx = max(a['idx'] for a in low_fls)
    first_high_idx = min(a['idx'] for a in high_fls)

    # Only consider lines where LOW comes before HIGH
    if last_low_idx >= first_high_idx:
        continue

    gap_tokens = [a for a in annotated
                  if last_low_idx < a['idx'] < first_high_idx
                  and not a['is_fl']]

    # Characterize LOW cluster
    low_stages = [a['fl_stage_order'] for a in low_fls]
    low_mean_stage = statistics.mean(low_stages)
    low_max_stage = max(low_stages)
    low_dominant_stage = Counter(a['fl_stage'] for a in low_fls).most_common(1)[0][0]

    # Characterize HIGH cluster
    high_stages = [a['fl_stage_order'] for a in high_fls]
    high_mean_stage = statistics.mean(high_stages)
    high_min_stage = min(high_stages)
    high_dominant_stage = Counter(a['fl_stage'] for a in high_fls).most_common(1)[0][0]

    # Stage gap: how much did the stage advance?
    stage_gap = high_mean_stage - low_mean_stage

    # Gap characterization
    gap_roles = Counter(a['role'] for a in gap_tokens)
    gap_n = len(gap_tokens)

    # Kernel density in gap
    gap_classes = [a['token_class'] for a in gap_tokens if a['token_class'] != -1]

    line_decompositions.append({
        'line_key': line_key,
        'n_tokens': n,
        'n_low_fl': len(low_fls),
        'n_high_fl': len(high_fls),
        'low_mean_stage': low_mean_stage,
        'high_mean_stage': high_mean_stage,
        'low_dominant_stage': low_dominant_stage,
        'high_dominant_stage': high_dominant_stage,
        'stage_gap': stage_gap,
        'gap_n': gap_n,
        'gap_roles': dict(gap_roles),
        'gap_classes': gap_classes,
    })

print(f"Lines with LOW->gap->HIGH structure: {len(line_decompositions)}")

# ============================================================
# Test 1: Does gap SIZE correlate with stage gap?
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: Gap size vs stage advancement")

stage_gaps = [d['stage_gap'] for d in line_decompositions]
gap_sizes = [d['gap_n'] for d in line_decompositions]

if len(stage_gaps) >= 10:
    rho, p = spearmanr(stage_gaps, gap_sizes)
    print(f"  Spearman rho(stage_gap, gap_size) = {rho:.3f}, p = {p:.4f}")

# Bin by stage gap
gap_bins = defaultdict(list)
for d in line_decompositions:
    sg = d['stage_gap']
    if sg <= 0:
        bin_name = 'SAME_OR_BACK'
    elif sg <= 1:
        bin_name = 'SMALL_ADVANCE'
    elif sg <= 2:
        bin_name = 'MEDIUM_ADVANCE'
    else:
        bin_name = 'LARGE_ADVANCE'
    gap_bins[bin_name].append(d)

print(f"\n  Gap size by stage advancement:")
for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
    items = gap_bins.get(bin_name, [])
    if not items:
        continue
    sizes = [d['gap_n'] for d in items]
    print(f"    {bin_name:>20}: n={len(items):>4}, "
          f"mean_gap_size={statistics.mean(sizes):.1f}, "
          f"median={statistics.median(sizes):.1f}")

# ============================================================
# Test 2: Gap COMPOSITION by stage gap
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: Gap role composition by stage advancement")

for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
    items = gap_bins.get(bin_name, [])
    if len(items) < 10:
        continue

    # Aggregate roles across all gaps in this bin
    total_roles = Counter()
    total_gap_tokens = 0
    for d in items:
        for role, count in d['gap_roles'].items():
            total_roles[role] += count
            total_gap_tokens += count

    print(f"\n  {bin_name} (n={len(items)} lines, {total_gap_tokens} gap tokens):")
    for role, count in total_roles.most_common():
        pct = count / total_gap_tokens * 100 if total_gap_tokens > 0 else 0
        print(f"    {role:>25}: {count:>4} ({pct:.1f}%)")

# ============================================================
# Test 3: Specific role rates by stage gap
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: Key role rates by stage advancement")

key_roles = ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR', 'AUXILIARY', 'FLOW_OPERATOR']

print(f"\n  {'Role':>25} {'SAME/BACK':>10} {'SMALL':>10} {'MEDIUM':>10} {'LARGE':>10}")
print("  " + "-" * 70)

role_by_gap = {}
for role in key_roles:
    rates = {}
    for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
        items = gap_bins.get(bin_name, [])
        if not items:
            continue
        total_gap = sum(d['gap_n'] for d in items)
        role_count = sum(d['gap_roles'].get(role, 0) for d in items)
        rate = role_count / total_gap * 100 if total_gap > 0 else 0
        rates[bin_name] = rate

    role_by_gap[role] = rates
    vals = [f"{rates.get(b, 0):>8.1f}%" for b in
            ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']]
    print(f"  {role:>25} {'  '.join(vals)}")

# ============================================================
# Test 4: Does EN (ENERGY_OPERATOR) kernel profile differ?
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: EN token count in gap by stage advancement")

for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
    items = gap_bins.get(bin_name, [])
    if len(items) < 10:
        continue
    en_counts = [d['gap_roles'].get('ENERGY_OPERATOR', 0) for d in items]
    en_rate = [d['gap_roles'].get('ENERGY_OPERATOR', 0) / d['gap_n']
               if d['gap_n'] > 0 else 0 for d in items]
    print(f"  {bin_name:>20}: mean_EN_count={statistics.mean(en_counts):.2f}, "
          f"mean_EN_rate={statistics.mean(en_rate):.3f}")

# Kruskal-Wallis: EN rate across gap bins
en_rate_groups = []
en_rate_labels = []
for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
    items = gap_bins.get(bin_name, [])
    if len(items) >= 10:
        rates = [d['gap_roles'].get('ENERGY_OPERATOR', 0) / d['gap_n']
                 if d['gap_n'] > 0 else 0 for d in items]
        en_rate_groups.append(rates)
        en_rate_labels.append(bin_name)

if len(en_rate_groups) >= 2:
    H, p = kruskal(*en_rate_groups)
    print(f"\n  Kruskal-Wallis (EN rate ~ stage_gap): H={H:.2f}, p={p:.4f}")

# ============================================================
# Test 5: Does CC (CORE_CONTROL) predict advancement?
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: CC (CORE_CONTROL) in gap by stage advancement")

for bin_name in ['SAME_OR_BACK', 'SMALL_ADVANCE', 'MEDIUM_ADVANCE', 'LARGE_ADVANCE']:
    items = gap_bins.get(bin_name, [])
    if len(items) < 10:
        continue
    cc_counts = [d['gap_roles'].get('CORE_CONTROL', 0) for d in items]
    cc_present = sum(1 for c in cc_counts if c > 0)
    print(f"  {bin_name:>20}: CC_present={cc_present}/{len(items)} "
          f"({cc_present/len(items)*100:.1f}%), "
          f"mean_CC={statistics.mean(cc_counts):.2f}")

# ============================================================
# Test 6: LOW dominant stage -> HIGH dominant stage transition matrix
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: LOW stage -> HIGH stage transition matrix")

transition_matrix = Counter()
for d in line_decompositions:
    transition_matrix[(d['low_dominant_stage'], d['high_dominant_stage'])] += 1

stages_seen = sorted(set(s for pair in transition_matrix for s in pair),
                     key=lambda x: STAGE_ORDER.get(x, 99))

# Print matrix
label = 'LOW\\HIGH'
header = f"{label:>12}" + "".join(f"{s:>10}" for s in stages_seen)
print(f"  {header}")
for low_s in stages_seen:
    row = f"  {low_s:>12}"
    for high_s in stages_seen:
        count = transition_matrix.get((low_s, high_s), 0)
        row += f"{count:>10}"
    print(row)

# Forward vs backward vs same
forward_trans = sum(v for (l, h), v in transition_matrix.items()
                    if STAGE_ORDER.get(h, 0) > STAGE_ORDER.get(l, 0))
same_trans = sum(v for (l, h), v in transition_matrix.items()
                 if STAGE_ORDER.get(h, 0) == STAGE_ORDER.get(l, 0))
backward_trans = sum(v for (l, h), v in transition_matrix.items()
                     if STAGE_ORDER.get(h, 0) < STAGE_ORDER.get(l, 0))
total_trans = forward_trans + same_trans + backward_trans

print(f"\n  Forward (HIGH > LOW): {forward_trans} ({forward_trans/total_trans*100:.1f}%)")
print(f"  Same stage:          {same_trans} ({same_trans/total_trans*100:.1f}%)")
print(f"  Backward (HIGH < LOW):{backward_trans} ({backward_trans/total_trans*100:.1f}%)")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

# Check if gap composition differs by stage advancement
en_differs = len(en_rate_groups) >= 2 and p < 0.05
role_gradient = any(
    abs(role_by_gap.get(role, {}).get('LARGE_ADVANCE', 0) -
        role_by_gap.get(role, {}).get('SAME_OR_BACK', 0)) > 5
    for role in key_roles
)

if en_differs and role_gradient:
    verdict = "KERNEL_CORRELATES_WITH_TRANSITION"
    explanation = ("Gap kernel composition significantly differs by stage advancement. "
                   "EN rate and role profiles change with LOW->HIGH gap size. "
                   "Consistent with input->process->result interpretation.")
elif en_differs or role_gradient:
    verdict = "PARTIAL_CORRELATION"
    explanation = ("Some gap composition differences by stage advancement, "
                   "but not comprehensive.")
else:
    verdict = "NO_CORRELATION"
    explanation = ("Gap kernel composition does not vary with stage advancement. "
                   "Kernel operators behave the same regardless of FL transition.")

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'n_decomposed_lines': len(line_decompositions),
    'gap_size_vs_stage': {
        'rho': round(float(rho), 4) if len(stage_gaps) >= 10 else None,
        'p': round(float(p), 4) if len(stage_gaps) >= 10 else None,
    },
    'gap_bins': {
        bin_name: {
            'n_lines': len(items),
            'mean_gap_size': round(statistics.mean([d['gap_n'] for d in items]), 2) if items else 0,
        }
        for bin_name, items in gap_bins.items()
    },
    'role_rates_by_gap': role_by_gap,
    'transition_matrix': {f"{l}->{h}": v for (l, h), v in transition_matrix.items()},
    'forward_pct': round(forward_trans / total_trans * 100, 1) if total_trans > 0 else 0,
    'same_pct': round(same_trans / total_trans * 100, 1) if total_trans > 0 else 0,
    'backward_pct': round(backward_trans / total_trans * 100, 1) if total_trans > 0 else 0,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "16_kernel_gap_analysis.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")

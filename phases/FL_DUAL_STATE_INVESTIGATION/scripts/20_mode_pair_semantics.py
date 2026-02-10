"""
20_mode_pair_semantics.py

Does the LOW+HIGH stage PAIR predict operational content?
Not just "what stage is LOW" but the specific combination:
LOW=MEDIAL + HIGH=TERMINAL vs LOW=MEDIAL + HIGH=LATE etc.

Tests:
1. Do specific LOW+HIGH pairs have distinct gap operator profiles?
2. Do pairs predict section, folio, or paragraph position?
3. Are certain pairs preferred or forbidden?
4. Does the pair carry more information than either mode alone?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, entropy

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

MIN_N = 50
tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# ============================================================
# Collect tokens, fit GMMs
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio,
                          'par_initial': t.par_initial, 'par_final': t.par_final}
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

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
# Build line profiles with LOW+HIGH pairs
# ============================================================
line_profiles = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1)
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
        entry = {
            'word': t.word, 'pos': pos, 'is_fl': is_fl,
            'mode': mode, 'stage': stage, 'role': role,
            'middle': m.middle if m else None,
        }
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']

    if not low_fls or not high_fls:
        continue

    # Dominant stages
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]

    # Gap tokens
    max_low_pos = max(f['pos'] for f in low_fls)
    min_high_pos = min(f['pos'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['pos'] > max_low_pos and t['pos'] < min_high_pos]

    # Gap role profile
    gap_roles = Counter(t['role'] for t in gap)
    gap_words = Counter(t['word'] for t in gap)
    gap_middles = Counter(t['middle'] for t in gap if t['middle'])

    line_profiles.append({
        'key': line_key,
        'low_stage': low_stage,
        'high_stage': high_stage,
        'pair': (low_stage, high_stage),
        'n_tokens': n,
        'n_gap': len(gap),
        'gap_roles': gap_roles,
        'gap_words': gap_words,
        'gap_middles': gap_middles,
        'section': line_meta[line_key]['section'],
        'folio': line_key[0],
        'par_initial': line_meta[line_key].get('par_initial', False),
        'par_final': line_meta[line_key].get('par_final', False),
        'low_middles': [f['middle'] for f in low_fls],
        'high_middles': [f['middle'] for f in high_fls],
    })

print(f"Lines with LOW+HIGH pairs: {len(line_profiles)}")

# ============================================================
# TEST 1: Pair frequency matrix
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: LOW+HIGH STAGE PAIR FREQUENCY MATRIX")
print(f"{'='*70}")

pair_counts = Counter(lp['pair'] for lp in line_profiles)

# Print matrix
label = 'LOW \\ HIGH'
header = f"{label:>12}"
for hs in STAGES:
    header += f" {hs[:5]:>7}"
header += "    Total"
print(header)
print("-" * 70)

for ls in STAGES:
    row = f"{ls:>12}"
    row_total = 0
    for hs in STAGES:
        count = pair_counts.get((ls, hs), 0)
        row_total += count
        if count > 0:
            row += f" {count:>7}"
        else:
            row += f" {'':>7}"
    row += f" {row_total:>7}"
    print(row)

total_row = f"{'Total':>12}"
for hs in STAGES:
    col_total = sum(pair_counts.get((ls, hs), 0) for ls in STAGES)
    total_row += f" {col_total:>7}"
print(total_row)

# ============================================================
# TEST 2: Are certain pairs preferred or forbidden?
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: PAIR PREFERENCES (observed / expected)")
print(f"{'='*70}")

# Expected under independence
low_marginal = Counter(lp['low_stage'] for lp in line_profiles)
high_marginal = Counter(lp['high_stage'] for lp in line_profiles)
total = len(line_profiles)

print(f"{label:>12}", end="")
for hs in STAGES:
    print(f" {hs[:5]:>7}", end="")
print()
print("-" * 60)

enriched_pairs = {}
depleted_pairs = {}

for ls in STAGES:
    row = f"{ls:>12}"
    for hs in STAGES:
        observed = pair_counts.get((ls, hs), 0)
        expected = low_marginal[ls] * high_marginal[hs] / total
        if expected > 5 and observed > 0:
            ratio = observed / expected
            row += f" {ratio:>7.2f}"
            if ratio > 1.5 and observed >= 10:
                enriched_pairs[(ls, hs)] = {'obs': observed, 'exp': round(expected, 1), 'ratio': round(ratio, 2)}
            elif ratio < 0.5 and expected >= 10:
                depleted_pairs[(ls, hs)] = {'obs': observed, 'exp': round(expected, 1), 'ratio': round(ratio, 2)}
        elif expected > 5:
            row += f" {0:>7.2f}"
        else:
            row += f" {'':>7}"
    print(row)

if enriched_pairs:
    print(f"\nENRICHED pairs (obs/exp > 1.5, n >= 10):")
    for pair, info in sorted(enriched_pairs.items(), key=lambda x: -x[1]['ratio']):
        print(f"  {pair[0]:>10} -> {pair[1]:<10}: obs={info['obs']}, exp={info['exp']}, ratio={info['ratio']}")

if depleted_pairs:
    print(f"\nDEPLETED pairs (obs/exp < 0.5, exp >= 10):")
    for pair, info in sorted(depleted_pairs.items(), key=lambda x: x[1]['ratio']):
        print(f"  {pair[0]:>10} -> {pair[1]:<10}: obs={info['obs']}, exp={info['exp']}, ratio={info['ratio']}")

# Chi-squared on pair matrix
pair_table = np.array([[pair_counts.get((ls, hs), 0) for hs in STAGES] for ls in STAGES])
# Remove zero rows/cols
row_mask = pair_table.sum(axis=1) > 0
col_mask = pair_table.sum(axis=0) > 0
pair_table_clean = pair_table[row_mask][:, col_mask]
if pair_table_clean.shape[0] >= 2 and pair_table_clean.shape[1] >= 2:
    chi2, p_val, dof, expected = chi2_contingency(pair_table_clean)
    cramers_v = np.sqrt(chi2 / (pair_table_clean.sum() * (min(pair_table_clean.shape) - 1)))
    print(f"\n  Chi-squared: chi2={chi2:.1f}, p={p_val:.2e}, dof={dof}, Cramer's V={cramers_v:.3f}")

# ============================================================
# TEST 3: Do pairs predict gap role profiles?
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: GAP ROLE PROFILES BY PAIR")
print(f"{'='*70}")

# Group by pair, get role distributions
top_pairs = [p for p, c in pair_counts.most_common(15) if c >= 20]
all_roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']

header = f"{'Pair':>22}"
for role in all_roles:
    header += f" {role[:6]:>7}"
header += "     n"
print(header)
print("-" * 70)

pair_role_profiles = {}
for pair in top_pairs:
    pair_lines = [lp for lp in line_profiles if lp['pair'] == pair]
    all_gap_roles = Counter()
    for lp in pair_lines:
        all_gap_roles += lp['gap_roles']
    total_gap = sum(all_gap_roles.values())
    if total_gap < 20:
        continue

    profile = {}
    row = f"{pair[0][:4]+'>'+pair[1][:4]:>22}"
    for role in all_roles:
        pct = all_gap_roles.get(role, 0) / total_gap * 100
        profile[role] = round(pct, 1)
        row += f" {pct:>6.1f}%"
    row += f" {total_gap:>5}"
    pair_role_profiles[f"{pair[0]}->{pair[1]}"] = profile
    print(row)

# Chi-squared: pair x gap role
if len(top_pairs) >= 2:
    role_table = []
    valid_pairs_for_chi = []
    for pair in top_pairs:
        pair_lines = [lp for lp in line_profiles if lp['pair'] == pair]
        all_gap_roles = Counter()
        for lp in pair_lines:
            all_gap_roles += lp['gap_roles']
        if sum(all_gap_roles.values()) >= 30:
            role_table.append([all_gap_roles.get(r, 0) for r in all_roles])
            valid_pairs_for_chi.append(pair)

    if len(role_table) >= 2:
        role_arr = np.array(role_table)
        nonzero = role_arr.sum(axis=0) > 0
        role_arr = role_arr[:, nonzero]
        chi2_role, p_role, dof_role, _ = chi2_contingency(role_arr)
        v_role = np.sqrt(chi2_role / (role_arr.sum() * (min(role_arr.shape) - 1)))
        print(f"\n  Chi-squared (pair x role): chi2={chi2_role:.1f}, p={p_role:.2e}, Cramer's V={v_role:.3f}")

# ============================================================
# TEST 4: Do pairs predict gap WORDS?
# ============================================================
print(f"\n{'='*70}")
print("TEST 4: TOP GAP WORDS BY PAIR (top 5 pairs)")
print(f"{'='*70}")

for pair in [p for p, c in pair_counts.most_common(5)]:
    pair_lines = [lp for lp in line_profiles if lp['pair'] == pair]
    all_gap_words = Counter()
    for lp in pair_lines:
        all_gap_words += lp['gap_words']
    top = all_gap_words.most_common(8)
    words_str = ', '.join(f"{w}({c})" for w, c in top)
    print(f"  {pair[0]:>10} -> {pair[1]:<10} (n={len(pair_lines)}): {words_str}")

# Vocabulary overlap between top pairs
print(f"\n  Pairwise vocabulary Jaccard (top-30 words):")
top5 = [p for p, c in pair_counts.most_common(5)]
pair_vocabs = {}
for pair in top5:
    pair_lines = [lp for lp in line_profiles if lp['pair'] == pair]
    all_gap_words = Counter()
    for lp in pair_lines:
        all_gap_words += lp['gap_words']
    pair_vocabs[pair] = set(w for w, _ in all_gap_words.most_common(30))

for i, p1 in enumerate(top5):
    for p2 in top5[i+1:]:
        inter = pair_vocabs[p1] & pair_vocabs[p2]
        union = pair_vocabs[p1] | pair_vocabs[p2]
        j = len(inter) / len(union) if union else 0
        label1 = f"{p1[0][:4]}>{p1[1][:4]}"
        label2 = f"{p2[0][:4]}>{p2[1][:4]}"
        print(f"    {label1} vs {label2}: {j:.2f}")

# ============================================================
# TEST 5: Do pairs predict SECTION?
# ============================================================
print(f"\n{'='*70}")
print("TEST 5: PAIR x SECTION")
print(f"{'='*70}")

pair_section = defaultdict(Counter)
for lp in line_profiles:
    pair_section[lp['pair']][lp['section']] += 1

sections = sorted(set(lp['section'] for lp in line_profiles))
header = f"{'Pair':>22}"
for s in sections:
    header += f" {s:>7}"
print(header)
print("-" * 60)

for pair in [p for p, c in pair_counts.most_common(10)]:
    total_pair = sum(pair_section[pair].values())
    row = f"{pair[0][:4]+'>'+pair[1][:4]:>22}"
    for s in sections:
        pct = pair_section[pair].get(s, 0) / total_pair * 100
        row += f" {pct:>6.1f}%"
    print(row)

# Base rates
print(f"{'BASE RATE':>22}", end="")
section_totals = Counter(lp['section'] for lp in line_profiles)
for s in sections:
    print(f" {section_totals[s]/total*100:>6.1f}%", end="")
print()

# Chi-squared
section_table = []
for pair in [p for p, c in pair_counts.most_common(10) if c >= 20]:
    section_table.append([pair_section[pair].get(s, 0) for s in sections])
if len(section_table) >= 2:
    sec_arr = np.array(section_table)
    nonzero_sec = sec_arr.sum(axis=0) > 0
    sec_arr = sec_arr[:, nonzero_sec]
    chi2_sec, p_sec, dof_sec, _ = chi2_contingency(sec_arr)
    v_sec = np.sqrt(chi2_sec / (sec_arr.sum() * (min(sec_arr.shape) - 1)))
    print(f"\n  Chi-squared (pair x section): chi2={chi2_sec:.1f}, p={p_sec:.2e}, Cramer's V={v_sec:.3f}")

# ============================================================
# TEST 6: Information content — pair vs single
# ============================================================
print(f"\n{'='*70}")
print("TEST 6: MUTUAL INFORMATION — PAIR vs GAP CONTENT")
print(f"{'='*70}")

# Discretize gap content into dominant role
def dominant_role(gap_roles):
    if not gap_roles:
        return 'EMPTY'
    return gap_roles.most_common(1)[0][0]

# MI(pair, gap_dominant_role) vs MI(low_stage, gap_dominant_role) vs MI(high_stage, gap_dominant_role)
pair_labels = [lp['pair'] for lp in line_profiles]
low_labels = [lp['low_stage'] for lp in line_profiles]
high_labels = [lp['high_stage'] for lp in line_profiles]
gap_labels = [dominant_role(lp['gap_roles']) for lp in line_profiles]

def mutual_info(labels_a, labels_b):
    """Compute MI between two categorical variables."""
    n = len(labels_a)
    joint = Counter(zip(labels_a, labels_b))
    marginal_a = Counter(labels_a)
    marginal_b = Counter(labels_b)

    mi = 0.0
    for (a, b), count_ab in joint.items():
        p_ab = count_ab / n
        p_a = marginal_a[a] / n
        p_b = marginal_b[b] / n
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * np.log2(p_ab / (p_a * p_b))
    return mi

mi_pair_gap = mutual_info(pair_labels, gap_labels)
mi_low_gap = mutual_info(low_labels, gap_labels)
mi_high_gap = mutual_info(high_labels, gap_labels)
mi_low_high = mutual_info(low_labels, high_labels)

# Also: entropy of each
h_pair = entropy([c/total for c in Counter(pair_labels).values()], base=2)
h_low = entropy([c/total for c in Counter(low_labels).values()], base=2)
h_high = entropy([c/total for c in Counter(high_labels).values()], base=2)
h_gap = entropy([c/total for c in Counter(gap_labels).values()], base=2)

print(f"  H(pair)      = {h_pair:.3f} bits")
print(f"  H(low_stage) = {h_low:.3f} bits")
print(f"  H(high_stage)= {h_high:.3f} bits")
print(f"  H(gap_role)  = {h_gap:.3f} bits")
print()
print(f"  MI(pair, gap_role)       = {mi_pair_gap:.4f} bits")
print(f"  MI(low_stage, gap_role)  = {mi_low_gap:.4f} bits")
print(f"  MI(high_stage, gap_role) = {mi_high_gap:.4f} bits")
print(f"  MI(low_stage, high_stage)= {mi_low_high:.4f} bits")
print()
pair_gain = mi_pair_gap - max(mi_low_gap, mi_high_gap)
print(f"  Information gain from pair vs best single: {pair_gain:.4f} bits")
print(f"  Pair synergy: {'YES' if pair_gain > 0.01 else 'NO'} (threshold: 0.01 bits)")

# ============================================================
# TEST 7: Direction analysis — forward, same, backward pairs
# ============================================================
print(f"\n{'='*70}")
print("TEST 7: PAIR DIRECTION ANALYSIS")
print(f"{'='*70}")

forward = [(ls, hs) for (ls, hs), c in pair_counts.items()
           if STAGE_ORDER[hs] > STAGE_ORDER[ls]]
same = [(ls, hs) for (ls, hs), c in pair_counts.items()
        if STAGE_ORDER[hs] == STAGE_ORDER[ls]]
backward = [(ls, hs) for (ls, hs), c in pair_counts.items()
            if STAGE_ORDER[hs] < STAGE_ORDER[ls]]

n_forward = sum(pair_counts[p] for p in forward)
n_same = sum(pair_counts[p] for p in same)
n_backward = sum(pair_counts[p] for p in backward)

print(f"  Forward  (LOW < HIGH stage): {n_forward:>4} ({n_forward/total*100:.1f}%)")
print(f"  Same     (LOW = HIGH stage): {n_same:>4} ({n_same/total*100:.1f}%)")
print(f"  Backward (LOW > HIGH stage): {n_backward:>4} ({n_backward/total*100:.1f}%)")
print(f"  Forward:Backward ratio: {n_forward/n_backward:.2f}:1" if n_backward > 0 else "  No backward pairs")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*70}")

pair_independent = True
pair_predicts_content = False
pair_predicts_section = False
pair_has_synergy = False

if 'cramers_v' in dir() and cramers_v > 0.10:
    pair_independent = False
if 'v_role' in dir() and v_role > 0.05:
    pair_predicts_content = True
if 'v_sec' in dir() and v_sec > 0.10:
    pair_predicts_section = True
if pair_gain > 0.01:
    pair_has_synergy = True

if pair_has_synergy and pair_predicts_content:
    verdict = "PAIR_CARRIES_MEANING"
    explanation = "The LOW+HIGH pair encodes information beyond either mode alone"
elif not pair_independent:
    verdict = "PAIR_STRUCTURED_NOT_PREDICTIVE"
    explanation = "LOW and HIGH stages are non-independent (preferred pairs exist) but don't predict content"
elif pair_predicts_section:
    verdict = "PAIR_CONTEXT_DEPENDENT"
    explanation = "Pairs vary by section but don't predict operational content"
else:
    verdict = "PAIR_UNINFORMATIVE"
    explanation = "The pair carries no more information than individual modes"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# Save results
# ============================================================
result = {
    'n_lines_with_pairs': len(line_profiles),
    'pair_frequency': {f"{ls}->{hs}": c for (ls, hs), c in pair_counts.most_common()},
    'enriched_pairs': {f"{k[0]}->{k[1]}": v for k, v in enriched_pairs.items()},
    'depleted_pairs': {f"{k[0]}->{k[1]}": v for k, v in depleted_pairs.items()},
    'chi_squared_pair_independence': {
        'chi2': round(float(chi2), 1),
        'p': float(p_val),
        'cramers_v': round(float(cramers_v), 3),
    },
    'pair_role_profiles': pair_role_profiles,
    'chi_squared_pair_role': {
        'chi2': round(float(chi2_role), 1) if 'chi2_role' in dir() else None,
        'p': float(p_role) if 'p_role' in dir() else None,
        'cramers_v': round(float(v_role), 3) if 'v_role' in dir() else None,
    },
    'chi_squared_pair_section': {
        'chi2': round(float(chi2_sec), 1) if 'chi2_sec' in dir() else None,
        'p': float(p_sec) if 'p_sec' in dir() else None,
        'cramers_v': round(float(v_sec), 3) if 'v_sec' in dir() else None,
    },
    'mutual_information': {
        'pair_gap': round(float(mi_pair_gap), 4),
        'low_gap': round(float(mi_low_gap), 4),
        'high_gap': round(float(mi_high_gap), 4),
        'low_high': round(float(mi_low_high), 4),
        'pair_gain': round(float(pair_gain), 4),
    },
    'direction': {
        'forward': n_forward,
        'same': n_same,
        'backward': n_backward,
        'ratio': round(n_forward / n_backward, 2) if n_backward > 0 else None,
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "20_mode_pair_semantics.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")

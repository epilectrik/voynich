#!/usr/bin/env python3
"""
Phase 369: Affordance Bin Paragraph Dynamics

Tests whether the 9 affordance bins (C995-C1000) have distinct paragraph-gradient
trajectories. Key prediction: HUB_UNIVERSAL dominates the execution zone,
connecting C932+C935+C475+C995+C1000+C1053 into a single arc.

Hypotheses:
  H1: HUB_UNIVERSAL dominates execution zone (Q4 > 65%, monotonic increase)
  H2: Non-HUB specialized bins concentrate in specification zone
  H3: HUB sub-roles have distinct gradient profiles
  H4: Bin-to-bin transition grammar changes across gradient (JSD > 0.10)
  H5: Section parameterizes gradient magnitude not direction

Output: results/affordance_bin_paragraph_dynamics.json
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

AFFORDANCE_PATH = PROJECT_ROOT / 'data' / 'middle_affordance_table.json'
HUB_SUBROLE_PATH = (PROJECT_ROOT / 'phases' / 'HUB_ROLE_DECOMPOSITION'
                     / 'results' / 't1_hub_sub_role_partition.json')

MIN_PARAGRAPH_LINES = 8
N_QUINTILES = 5

# Bin labels for reference
BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPECIALIZED', 2: 'PRECISION_SPECIALIZED',
    3: 'COMPOUND_TERMINAL', 4: 'BULK_OPERATIONAL', 5: 'SETTLING_SPECIALIZED',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPECIALIZED', 8: 'STABILITY_CRITICAL',
    9: 'PHASE_SENSITIVE'
}
# Functional bins (exclude bin 4 = BULK_OPERATIONAL)
FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]
# Specialized (non-HUB) bins for H2
SPECIALIZED_BINS = [0, 1, 2, 3, 5, 7, 8, 9]

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


print("=" * 70)
print("Phase 369: Affordance Bin Paragraph Dynamics")
print("=" * 70)

# ============================================================
# S1: Load Data
# ============================================================
print("\n--- S1: Load Data ---")

tx = Transcript()
morph = Morphology()

morph_cache = {}
def get_middle(word):
    if word not in morph_cache:
        m = morph.extract(word)
        morph_cache[word] = m.middle if m.middle else None
    return morph_cache[word]

# Load affordance bin assignments
with open(AFFORDANCE_PATH, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)

mid_to_bin = {}  # MIDDLE -> bin number
mid_to_label = {}  # MIDDLE -> bin label
for mid_name, entry in aff_data['middles'].items():
    mid_to_bin[mid_name] = entry['affordance_bin']
    mid_to_label[mid_name] = entry['affordance_label']

print(f"  Affordance table: {len(mid_to_bin)} MIDDLEs")
bin_counts = Counter(mid_to_bin.values())
for b in sorted(bin_counts):
    print(f"    Bin {b} ({BIN_LABELS[b]}): {bin_counts[b]} MIDDLEs")

# Load HUB sub-role assignments
with open(HUB_SUBROLE_PATH, 'r', encoding='utf-8') as f:
    hub_data = json.load(f)

hub_middles = set(hub_data['hub_middle_list'])
mid_to_subroles = {}  # MIDDLE -> list of sub-role strings
for mid, roles in hub_data['sub_roles'].items():
    mid_to_subroles[mid] = roles

# Assign primary sub-role (first listed, or multi-role indicator)
mid_to_primary_subrole = {}
for mid, roles in mid_to_subroles.items():
    if len(roles) == 1:
        mid_to_primary_subrole[mid] = roles[0]
    else:
        # For multi-role, use first role as primary
        mid_to_primary_subrole[mid] = roles[0]

subrole_counts = Counter(mid_to_primary_subrole.values())
print(f"  HUB sub-roles: {dict(subrole_counts)}")

# ============================================================
# S2: Build B Paragraphs with Quintile Assignment
# ============================================================
print("\n--- S2: Build B Paragraphs ---")

b_data = defaultdict(lambda: defaultdict(list))
b_folio_section = {}
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    b_data[token.folio][token.line].append(token)
    if token.folio not in b_folio_section:
        b_folio_section[token.folio] = token.section

paragraphs = []
for folio in sorted(b_data.keys()):
    section = b_folio_section.get(folio, '?')
    if section not in ('B', 'H', 'S'):
        continue

    lines = sorted(b_data[folio].keys())
    if not lines:
        continue

    current_para_lines = []
    for line_num in lines:
        tokens = b_data[folio][line_num]
        is_para_start = any(t.par_initial for t in tokens)

        if is_para_start and current_para_lines:
            paragraphs.append({
                'folio': folio, 'section': section,
                'lines': current_para_lines
            })
            current_para_lines = []

        line_middles = []
        for t in tokens:
            mid = get_middle(t.word)
            if mid:
                line_middles.append(mid)
        current_para_lines.append({
            'line_num': line_num, 'middles': line_middles
        })

    if current_para_lines:
        paragraphs.append({
            'folio': folio, 'section': section,
            'lines': current_para_lines
        })

long_paras = [p for p in paragraphs if len(p['lines']) >= MIN_PARAGRAPH_LINES]
print(f"  Total paragraphs: {len(paragraphs)}")
print(f"  Long paragraphs (8+ lines): {len(long_paras)}")

section_counts = Counter(p['section'] for p in long_paras)
for s in ['B', 'H', 'S']:
    print(f"    Section {s}: {section_counts.get(s, 0)}")

# Assign quintiles to body lines
for para in long_paras:
    body_lines = para['lines'][1:]  # skip header
    n_body = len(body_lines)
    for bi, line in enumerate(body_lines):
        line['quintile'] = min(int(5 * bi / n_body), 4)
    para['body_lines'] = body_lines

# Pre-compute per-quintile token lists with bin assignments
# Each token = (middle, bin, subroles_or_None)
for para in long_paras:
    para['quintile_tokens'] = defaultdict(list)  # q -> [(mid, bin)]
    for line in para['body_lines']:
        q = line['quintile']
        for mid in line['middles']:
            if mid in mid_to_bin:
                para['quintile_tokens'][q].append((mid, mid_to_bin[mid]))

# Coverage check
all_tokens = 0
assigned_tokens = 0
for para in long_paras:
    for line in para['body_lines']:
        for mid in line['middles']:
            all_tokens += 1
            if mid in mid_to_bin:
                assigned_tokens += 1

print(f"  Token coverage: {assigned_tokens}/{all_tokens} ({assigned_tokens/all_tokens:.1%})")

# ============================================================
# S3: H1 — HUB_UNIVERSAL Dominates Execution Zone
# ============================================================
print("\n--- S3: H1 — HUB_UNIVERSAL Dominates Execution Zone ---")

# HUB_UNIVERSAL fraction by quintile
hub_fracs_by_q = {}
for q in range(N_QUINTILES):
    n_hub = 0
    n_total = 0
    for para in long_paras:
        for mid, b in para['quintile_tokens'][q]:
            if b != 4:  # exclude BULK
                n_total += 1
                if b == 6:  # HUB_UNIVERSAL
                    n_hub += 1
    hub_fracs_by_q[q] = n_hub / n_total if n_total > 0 else 0
    print(f"  Q{q}: HUB fraction = {hub_fracs_by_q[q]:.4f} ({n_hub}/{n_total})")

# Spearman correlation with quintile position
q_values = list(range(N_QUINTILES))
hub_values = [hub_fracs_by_q[q] for q in q_values]
rho_h1, p_h1 = stats.spearmanr(q_values, hub_values)
print(f"  Spearman rho = {rho_h1:.4f}, p = {p_h1:.4f}")

q4_fraction = hub_fracs_by_q[4]
monotonic_increase = all(hub_fracs_by_q[i] <= hub_fracs_by_q[i+1] for i in range(4))

h1_pass = (rho_h1 >= 0.80) and (q4_fraction > 0.65)
print(f"  Q4 fraction > 0.65: {q4_fraction > 0.65} ({q4_fraction:.4f})")
print(f"  rho >= 0.80: {rho_h1 >= 0.80}")
print(f"  Monotonic: {monotonic_increase}")
print(f"  H1 PASS: {h1_pass}")

h1_results = {
    'hub_fraction_by_quintile': {f'Q{q}': float(v) for q, v in hub_fracs_by_q.items()},
    'spearman_rho': float(rho_h1),
    'spearman_p': float(p_h1),
    'q4_fraction': float(q4_fraction),
    'monotonic_increase': bool(monotonic_increase),
    'pass': bool(h1_pass)
}

# ============================================================
# S4: H2 — Non-HUB Specialized Bins in Specification Zone
# ============================================================
print("\n--- S4: H2 — Non-HUB Specialized Bins in Specification Zone ---")

# Per-bin fraction by quintile
bin_fracs = {}  # bin -> {q -> fraction}
for b in FUNCTIONAL_BINS:
    q_fracs = {}
    for q in range(N_QUINTILES):
        n_this = 0
        n_total = 0
        for para in long_paras:
            for mid, bn in para['quintile_tokens'][q]:
                if bn != 4:
                    n_total += 1
                    if bn == b:
                        n_this += 1
        q_fracs[q] = n_this / n_total if n_total > 0 else 0
    bin_fracs[b] = q_fracs

# Combined non-HUB specialized fraction
combined_spec = {}
for q in range(N_QUINTILES):
    combined_spec[q] = sum(bin_fracs[b][q] for b in SPECIALIZED_BINS)

rho_combined, p_combined = stats.spearmanr(q_values, [combined_spec[q] for q in q_values])
print(f"  Combined non-HUB fraction by quintile:")
for q in range(N_QUINTILES):
    print(f"    Q{q}: {combined_spec[q]:.4f}")
print(f"  Combined rho = {rho_combined:.4f}")

# Per-bin Spearman with Bonferroni correction
n_declining = 0
bin_rho_results = {}
alpha_corrected = 0.01 / len(SPECIALIZED_BINS)  # Bonferroni

for b in SPECIALIZED_BINS:
    vals = [bin_fracs[b][q] for q in q_values]
    if len(set(vals)) <= 1:
        rho_b, p_b = 0.0, 1.0
    else:
        rho_b, p_b = stats.spearmanr(q_values, vals)
    significant_decline = (rho_b < 0) and (p_b < alpha_corrected)
    if significant_decline:
        n_declining += 1
    bin_rho_results[b] = {
        'label': BIN_LABELS[b],
        'rho': float(rho_b),
        'p': float(p_b),
        'significant_decline': bool(significant_decline),
        'Q0': float(bin_fracs[b][0]),
        'Q4': float(bin_fracs[b][4])
    }
    print(f"  Bin {b} ({BIN_LABELS[b]}): rho={rho_b:.3f}, p={p_b:.3f}, "
          f"Q0={bin_fracs[b][0]:.4f}, Q4={bin_fracs[b][4]:.4f}")

h2_pass = (rho_combined <= -0.70) and (n_declining >= 3)
print(f"  Combined rho <= -0.70: {rho_combined <= -0.70}")
print(f"  Bins with significant decline: {n_declining}/8 (need >= 3)")
print(f"  H2 PASS: {h2_pass}")

h2_results = {
    'combined_non_hub_rho': float(rho_combined),
    'combined_non_hub_by_quintile': {f'Q{q}': float(v) for q, v in combined_spec.items()},
    'per_bin': bin_rho_results,
    'n_declining': n_declining,
    'pass': bool(h2_pass)
}

# ============================================================
# S5: H3 — HUB Sub-Roles Have Distinct Gradient Profiles
# ============================================================
print("\n--- S5: H3 — HUB Sub-Roles Gradient Profiles ---")

# Per sub-role fraction within HUB tokens by quintile
subrole_fracs = defaultdict(lambda: defaultdict(int))  # subrole -> {q -> count}
hub_totals_by_q = defaultdict(int)  # q -> total HUB tokens

for para in long_paras:
    for q in range(N_QUINTILES):
        for mid, b in para['quintile_tokens'][q]:
            if b == 6 and mid in mid_to_primary_subrole:
                subrole_fracs[mid_to_primary_subrole[mid]][q] += 1
                hub_totals_by_q[q] += 1

subrole_names = ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']
subrole_frac_values = {}  # subrole -> {q -> fraction}

n_significant = 0
subrole_kw_results = {}

for sr in subrole_names:
    fracs = {}
    for q in range(N_QUINTILES):
        total = hub_totals_by_q[q]
        fracs[q] = subrole_fracs[sr][q] / total if total > 0 else 0
    subrole_frac_values[sr] = fracs
    print(f"  {sr}:")
    for q in range(N_QUINTILES):
        print(f"    Q{q}: {fracs[q]:.4f} ({subrole_fracs[sr][q]})")

    # KW test: do per-paragraph sub-role fractions differ by quintile?
    # Build per-paragraph per-quintile sub-role proportions
    q_groups = defaultdict(list)
    for para in long_paras:
        for q in range(N_QUINTILES):
            hub_tokens = [(mid, b) for mid, b in para['quintile_tokens'][q] if b == 6]
            if not hub_tokens:
                continue
            n_sr = sum(1 for mid, _ in hub_tokens
                       if mid in mid_to_primary_subrole and mid_to_primary_subrole[mid] == sr)
            q_groups[q].append(n_sr / len(hub_tokens))

    if all(len(q_groups[q]) >= 5 for q in range(N_QUINTILES)):
        kw_stat, kw_p = stats.kruskal(*[q_groups[q] for q in range(N_QUINTILES)])
        is_sig = kw_p < 0.01
        if is_sig:
            n_significant += 1
        print(f"    KW: H={kw_stat:.2f}, p={kw_p:.4f}")
    else:
        kw_stat, kw_p = 0.0, 1.0
        is_sig = False
        print(f"    KW: insufficient data")

    subrole_kw_results[sr] = {
        'fracs': {f'Q{q}': float(fracs[q]) for q in range(N_QUINTILES)},
        'kw_H': float(kw_stat),
        'kw_p': float(kw_p),
        'significant': bool(is_sig)
    }

h3_pass = n_significant >= 2
print(f"  Sub-roles with significant quintile dependence: {n_significant}/4 (need >= 2)")
print(f"  H3 PASS: {h3_pass}")

h3_results = {
    'subroles': subrole_kw_results,
    'n_significant': n_significant,
    'pass': bool(h3_pass)
}

# ============================================================
# S6: H4 — Bin Transition Grammar Changes Across Gradient
# ============================================================
print("\n--- S6: H4 — Bin Transition Grammar Across Gradient ---")

def build_bin_transition_matrix(paras, quintile_set):
    """Build bin-to-bin transition matrix for given quintiles."""
    transitions = defaultdict(lambda: defaultdict(int))
    for para in paras:
        for line in para['body_lines']:
            if line['quintile'] not in quintile_set:
                continue
            # Get bin sequence for this line
            bin_seq = []
            for mid in line['middles']:
                if mid in mid_to_bin and mid_to_bin[mid] != 4:
                    bin_seq.append(mid_to_bin[mid])
            for i in range(len(bin_seq) - 1):
                transitions[bin_seq[i]][bin_seq[i+1]] += 1
    return transitions

def transitions_to_probs(transitions):
    """Convert count dict to probability matrix."""
    all_bins = sorted(set(list(transitions.keys()) +
                          [b for d in transitions.values() for b in d.keys()]))
    n = len(all_bins)
    bin_idx = {b: i for i, b in enumerate(all_bins)}
    mat = np.zeros((n, n))
    for src, targets in transitions.items():
        for tgt, count in targets.items():
            mat[bin_idx[src], bin_idx[tgt]] = count
    # Normalize rows
    row_sums = mat.sum(axis=1, keepdims=True)
    mat = np.divide(mat, row_sums, where=row_sums > 0, out=np.zeros_like(mat))
    return mat, all_bins

def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# Spec zone (Q0-Q1) vs Exec zone (Q3-Q4)
spec_trans = build_bin_transition_matrix(long_paras, {0, 1})
exec_trans = build_bin_transition_matrix(long_paras, {3, 4})

spec_mat, spec_bins = transitions_to_probs(spec_trans)
exec_mat, exec_bins = transitions_to_probs(exec_trans)

# Align matrices to same bin set
all_bins_union = sorted(set(spec_bins) | set(exec_bins))
n_bins = len(all_bins_union)

def align_matrix(mat, mat_bins, target_bins):
    n = len(target_bins)
    aligned = np.zeros((n, n))
    old_idx = {b: i for i, b in enumerate(mat_bins)}
    new_idx = {b: i for i, b in enumerate(target_bins)}
    for b in mat_bins:
        if b in new_idx:
            for b2 in mat_bins:
                if b2 in new_idx:
                    aligned[new_idx[b], new_idx[b2]] = mat[old_idx[b], old_idx[b2]]
    return aligned

spec_aligned = align_matrix(spec_mat, spec_bins, all_bins_union)
exec_aligned = align_matrix(exec_mat, exec_bins, all_bins_union)

# Compute JSD row by row, then average
row_jsds = []
for i in range(n_bins):
    if spec_aligned[i].sum() > 0 and exec_aligned[i].sum() > 0:
        row_jsds.append(jsd(spec_aligned[i], exec_aligned[i]))
mean_jsd = np.mean(row_jsds) if row_jsds else 0.0
print(f"  Mean row-wise JSD (spec vs exec): {mean_jsd:.4f}")

# HUB self-transition rate comparison
hub_bin_idx = all_bins_union.index(6) if 6 in all_bins_union else None
if hub_bin_idx is not None:
    spec_hub_self = spec_aligned[hub_bin_idx, hub_bin_idx]
    exec_hub_self = exec_aligned[hub_bin_idx, hub_bin_idx]
    hub_self_diff = exec_hub_self - spec_hub_self
    print(f"  HUB self-transition: spec={spec_hub_self:.4f}, exec={exec_hub_self:.4f}, "
          f"diff={hub_self_diff:+.4f}")
else:
    spec_hub_self, exec_hub_self, hub_self_diff = 0, 0, 0

h4_pass = (mean_jsd > 0.10) and (hub_self_diff > 0.05)
print(f"  JSD > 0.10: {mean_jsd > 0.10}")
print(f"  HUB self-transition increase > 5pp: {hub_self_diff > 0.05}")
print(f"  H4 PASS: {h4_pass}")

h4_results = {
    'mean_row_jsd': float(mean_jsd),
    'n_bins_compared': len(row_jsds),
    'hub_self_spec': float(spec_hub_self),
    'hub_self_exec': float(exec_hub_self),
    'hub_self_diff': float(hub_self_diff),
    'pass': bool(h4_pass)
}

# ============================================================
# S7: H5 — Section Parameterizes Gradient Magnitude Not Direction
# ============================================================
print("\n--- S7: H5 — Section Parameterizes Gradient Magnitude ---")

# Per-section HUB gradient
section_hub_gradients = {}
section_hub_slopes = []
sections_used = []

for sect in ['B', 'H', 'S']:
    sect_paras = [p for p in long_paras if p['section'] == sect]
    if len(sect_paras) < 3:
        print(f"  Section {sect}: too few paragraphs ({len(sect_paras)})")
        continue

    q_fracs = {}
    for q in range(N_QUINTILES):
        n_hub = 0
        n_total = 0
        for para in sect_paras:
            for mid, b in para['quintile_tokens'][q]:
                if b != 4:
                    n_total += 1
                    if b == 6:
                        n_hub += 1
        q_fracs[q] = n_hub / n_total if n_total > 0 else 0

    slope = q_fracs[4] - q_fracs[0]
    section_hub_gradients[sect] = q_fracs
    section_hub_slopes.append(slope)
    sections_used.append(sect)
    print(f"  Section {sect} (n={len(sect_paras)}): "
          f"Q0={q_fracs[0]:.4f}, Q4={q_fracs[4]:.4f}, slope={slope:+.4f}")

# Check: all positive direction?
all_positive = all(s > 0 for s in section_hub_slopes)
# Check: slopes differ by > 2x
if section_hub_slopes:
    max_slope = max(section_hub_slopes)
    min_slope = min(section_hub_slopes)
    slope_ratio = max_slope / min_slope if min_slope > 0 else float('inf')
else:
    slope_ratio = 0

# KW on per-paragraph HUB fraction slopes across sections
section_para_slopes = defaultdict(list)
for para in long_paras:
    if para['section'] not in ('B', 'H', 'S'):
        continue
    q0_tokens = para['quintile_tokens'][0]
    q4_tokens = para['quintile_tokens'][4]
    q0_hub = sum(1 for _, b in q0_tokens if b == 6) / max(1, sum(1 for _, b in q0_tokens if b != 4))
    q4_hub = sum(1 for _, b in q4_tokens if b == 6) / max(1, sum(1 for _, b in q4_tokens if b != 4))
    section_para_slopes[para['section']].append(q4_hub - q0_hub)

if all(len(section_para_slopes[s]) >= 5 for s in ['B', 'H', 'S']):
    kw_stat, kw_p = stats.kruskal(section_para_slopes['B'],
                                    section_para_slopes['H'],
                                    section_para_slopes['S'])
    print(f"  KW on per-paragraph slopes: H={kw_stat:.2f}, p={kw_p:.4f}")
else:
    kw_stat, kw_p = 0, 1.0
    print("  KW: insufficient data")

# Direction consistency: any section negative?
any_negative = any(s < 0 for s in section_hub_slopes)

h5_pass = all_positive and (slope_ratio > 2.0 or kw_p < 0.05) and not any_negative
print(f"  All positive: {all_positive}")
print(f"  Slope ratio max/min: {slope_ratio:.2f}")
print(f"  KW p < 0.05: {kw_p < 0.05}")
print(f"  H5 PASS: {h5_pass}")

h5_results = {
    'section_gradients': {},
    'all_positive': bool(all_positive),
    'slope_ratio': float(slope_ratio) if slope_ratio != float('inf') else None,
    'kw_stat': float(kw_stat),
    'kw_p': float(kw_p),
    'pass': bool(h5_pass)
}
for sect in sections_used:
    h5_results['section_gradients'][sect] = {
        f'Q{q}': float(v) for q, v in section_hub_gradients[sect].items()
    }
    h5_results['section_gradients'][sect]['slope'] = float(
        section_hub_gradients[sect][4] - section_hub_gradients[sect][0])
    h5_results['section_gradients'][sect]['n_paras'] = section_counts.get(sect, 0)

# ============================================================
# S8: Verdict Synthesis
# ============================================================
print("\n--- S8: Verdict Synthesis ---")

n_pass = sum([h1_pass, h2_pass, h3_pass, h4_pass, h5_pass])
print(f"\nResults: {n_pass}/5 hypotheses pass")
print(f"  H1 (HUB dominates execution):     {'PASS' if h1_pass else 'FAIL'}")
print(f"  H2 (non-HUB in specification):     {'PASS' if h2_pass else 'FAIL'}")
print(f"  H3 (HUB sub-role gradient):        {'PASS' if h3_pass else 'FAIL'}")
print(f"  H4 (transition grammar changes):   {'PASS' if h4_pass else 'FAIL'}")
print(f"  H5 (section parameterizes slope):  {'PASS' if h5_pass else 'FAIL'}")

if h1_pass and h2_pass:
    verdict = 'HUB_CONVERGENCE_CONFIRMED'
elif h1_pass:
    verdict = 'HUB_DOMINANCE_PARTIAL'
elif n_pass == 0:
    verdict = 'NO_GRADIENT_BIN_INTERACTION'
else:
    verdict = f'PARTIAL_{n_pass}_OF_5'

print(f"\nVerdict: {verdict} ({n_pass}/5)")

results = {
    'phase': 'AFFORDANCE_BIN_PARAGRAPH_DYNAMICS',
    'phase_number': 369,
    'timestamp': datetime.now().isoformat(),
    'analysis_set': {
        'total_paragraphs': len(paragraphs),
        'long_paragraphs': len(long_paras),
        'section_counts': dict(section_counts),
        'token_coverage': f'{assigned_tokens}/{all_tokens} ({assigned_tokens/all_tokens:.1%})',
        'functional_bins': len(FUNCTIONAL_BINS)
    },
    'H1_hub_dominance': h1_results,
    'H2_nonhub_specification': h2_results,
    'H3_subrole_gradient': h3_results,
    'H4_transition_grammar': h4_results,
    'H5_section_parameterization': h5_results,
    'verdict': verdict,
    'verdict_score': f'{n_pass}/5'
}

out_path = RESULTS_DIR / 'affordance_bin_paragraph_dynamics.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults written to {out_path}")
print("\nDone.")

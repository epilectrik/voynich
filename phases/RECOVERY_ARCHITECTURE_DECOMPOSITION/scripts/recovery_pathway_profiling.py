"""
RECOVERY_ARCHITECTURE_DECOMPOSITION - Script 1: Recovery Pathway Profiling

Per-REGIME kernel absorption rates, recovery path length distributions,
post-kernel destination classes, and KW tests of REGIME prediction.

Sections:
  1. Per-folio kernel absorption rates (e/h/k rates, kernel exit rate)
  2. Recovery path length distributions (hazard -> kernel sequences)
  3. Post-kernel destination classes (role-level routing after kernel)
  4. Summary (per-REGIME profiles, KW tests, verdict)

Output: results/recovery_pathway_profiling.json
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import kruskal

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

# =============================================================================
# Constants
# =============================================================================

KERNEL_CLASSES = {1, 2, 3}  # k=1, h=2, e=3
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

CLASS_TO_ROLE = {
    1: 'AX', 2: 'AX', 3: 'AX', 4: 'AX', 5: 'AX', 6: 'AX',
    7: 'FL', 8: 'EN', 9: 'FQ', 10: 'CC', 11: 'CC', 12: 'CC',
    13: 'FQ', 14: 'FQ', 15: 'AX', 16: 'AX', 17: 'AX', 18: 'AX',
    19: 'AX', 20: 'AX', 21: 'AX', 22: 'AX', 23: 'FQ', 24: 'AX',
    25: 'AX', 26: 'AX', 27: 'AX', 28: 'AX', 29: 'AX', 30: 'FL',
    31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN', 36: 'EN',
    37: 'EN', 38: 'FL', 39: 'EN', 40: 'FL', 41: 'EN', 42: 'EN',
    43: 'EN', 44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN',
    49: 'EN'
}

# =============================================================================
# Load data
# =============================================================================

print("Loading data...")

# Load class token map
class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path, 'r', encoding='utf-8') as f:
    class_data = json.load(f)

token_to_class = class_data['token_to_class']

# Load regime folio map
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

# Build folio -> regime map
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"  Regime coverage: {len(folio_to_regime)} folios across {len(regime_data)} REGIMEs")

# Load transcript
tx = Transcript()
b_tokens = list(tx.currier_b())
print(f"  Currier B tokens: {len(b_tokens)}")

# =============================================================================
# Build per-folio token class sequences
# =============================================================================

print("\nBuilding per-folio class sequences...")

# Group tokens by folio+line, preserving order
folio_line_tokens = defaultdict(list)
for t in b_tokens:
    if not t.word.strip() or '*' in t.word:
        continue
    cls = token_to_class.get(t.word)
    if cls is None:
        continue
    folio_line_tokens[(t.folio, t.line)].append(cls)

# Get unique folios
all_folios = sorted(set(t.folio for t in b_tokens if t.word.strip() and '*' not in t.word))
print(f"  Unique B folios: {len(all_folios)}")
print(f"  Folios with REGIME: {sum(1 for f in all_folios if f in folio_to_regime)}")
print(f"  Folios without REGIME: {sum(1 for f in all_folios if f not in folio_to_regime)}")

# Build per-folio flat class sequences (line boundaries preserved for recovery paths)
folio_lines = defaultdict(list)  # folio -> list of [class_seq_line1, class_seq_line2, ...]
for (folio, line), classes in sorted(folio_line_tokens.items()):
    folio_lines[folio].append(classes)

# =============================================================================
# Section 1: Per-Folio Kernel Absorption Rates
# =============================================================================

print("\n=== Section 1: Per-Folio Kernel Absorption Rates ===")

folio_kernel_stats = {}

for folio in all_folios:
    lines = folio_lines.get(folio, [])

    # Count: when current token is kernel, what class follows?
    kernel_to_e = 0
    kernel_to_h = 0
    kernel_to_k = 0
    kernel_to_nonkernel = 0
    total_kernel_transitions = 0

    for line_classes in lines:
        for i in range(len(line_classes) - 1):
            src_cls = line_classes[i]
            dst_cls = line_classes[i + 1]

            if src_cls in KERNEL_CLASSES:
                total_kernel_transitions += 1
                if dst_cls == 3:  # e
                    kernel_to_e += 1
                elif dst_cls == 2:  # h
                    kernel_to_h += 1
                elif dst_cls == 1:  # k
                    kernel_to_k += 1
                else:
                    kernel_to_nonkernel += 1

    if total_kernel_transitions > 0:
        e_rate = kernel_to_e / total_kernel_transitions
        h_rate = kernel_to_h / total_kernel_transitions
        k_rate = kernel_to_k / total_kernel_transitions
        exit_rate = kernel_to_nonkernel / total_kernel_transitions
    else:
        e_rate = h_rate = k_rate = exit_rate = 0.0

    folio_kernel_stats[folio] = {
        'e_rate': round(e_rate, 4),
        'h_rate': round(h_rate, 4),
        'k_rate': round(k_rate, 4),
        'exit_rate': round(exit_rate, 4),
        'total_kernel_transitions': total_kernel_transitions
    }

# Group by REGIME
regime_kernel = defaultdict(lambda: {'e_rates': [], 'h_rates': [], 'k_rates': [], 'exit_rates': []})
for folio, stats in folio_kernel_stats.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['total_kernel_transitions'] > 0:
        regime_kernel[regime]['e_rates'].append(stats['e_rate'])
        regime_kernel[regime]['h_rates'].append(stats['h_rate'])
        regime_kernel[regime]['k_rates'].append(stats['k_rate'])
        regime_kernel[regime]['exit_rates'].append(stats['exit_rate'])

# KW tests
kw_kernel_results = {}
for metric in ['e_rates', 'h_rates', 'k_rates', 'exit_rates']:
    groups = [regime_kernel[r][metric] for r in sorted(regime_kernel.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_kernel_results[metric.replace('_rates', '_rate')] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': p_val < 0.05
            }
        except ValueError:
            kw_kernel_results[metric.replace('_rates', '_rate')] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

# Print summary
print("\nPer-REGIME kernel absorption rates:")
for regime in sorted(regime_kernel.keys()):
    rk = regime_kernel[regime]
    print(f"  {regime}: e={np.mean(rk['e_rates']):.3f}+-{np.std(rk['e_rates']):.3f}, "
          f"h={np.mean(rk['h_rates']):.3f}+-{np.std(rk['h_rates']):.3f}, "
          f"k={np.mean(rk['k_rates']):.3f}+-{np.std(rk['k_rates']):.3f}, "
          f"exit={np.mean(rk['exit_rates']):.3f}+-{np.std(rk['exit_rates']):.3f} "
          f"(n={len(rk['e_rates'])})")

print("\nKW tests (kernel rates):")
for metric, res in kw_kernel_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {metric}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 2: Recovery Path Length Distributions
# =============================================================================

print("\n=== Section 2: Recovery Path Length Distributions ===")

folio_recovery_paths = {}

for folio in all_folios:
    lines = folio_lines.get(folio, [])
    path_lengths = []

    for line_classes in lines:
        # Find recovery sequences: hazard token -> ... -> kernel token
        i = 0
        while i < len(line_classes):
            if line_classes[i] in HAZARD_CLASSES:
                # Start of a potential recovery sequence
                j = i + 1
                while j < len(line_classes) and line_classes[j] not in KERNEL_CLASSES:
                    j += 1
                # Recovery path = tokens between hazard and kernel (exclusive of both)
                path_len = j - i - 1
                if j < len(line_classes):
                    # Found kernel: complete recovery path
                    path_lengths.append(path_len)
                else:
                    # End of line without kernel: incomplete recovery (still count)
                    path_lengths.append(path_len)
                i = j + 1
            else:
                i += 1

    if path_lengths:
        folio_recovery_paths[folio] = {
            'mean_path_length': round(float(np.mean(path_lengths)), 4),
            'median_path_length': round(float(np.median(path_lengths)), 4),
            'max_path_length': int(max(path_lengths)),
            'std_path_length': round(float(np.std(path_lengths)), 4),
            'n_recovery_paths': len(path_lengths)
        }
    else:
        folio_recovery_paths[folio] = {
            'mean_path_length': 0.0,
            'median_path_length': 0.0,
            'max_path_length': 0,
            'std_path_length': 0.0,
            'n_recovery_paths': 0
        }

# Group by REGIME
regime_recovery = defaultdict(lambda: {'mean_lengths': [], 'median_lengths': [], 'max_lengths': [], 'n_paths': []})
for folio, stats in folio_recovery_paths.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['n_recovery_paths'] > 0:
        regime_recovery[regime]['mean_lengths'].append(stats['mean_path_length'])
        regime_recovery[regime]['median_lengths'].append(stats['median_path_length'])
        regime_recovery[regime]['max_lengths'].append(stats['max_path_length'])
        regime_recovery[regime]['n_paths'].append(stats['n_recovery_paths'])

# KW tests
kw_recovery_results = {}
for metric in ['mean_lengths', 'median_lengths', 'max_lengths', 'n_paths']:
    groups = [regime_recovery[r][metric] for r in sorted(regime_recovery.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_recovery_results[metric] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': p_val < 0.05
            }
        except ValueError:
            kw_recovery_results[metric] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

print("\nPer-REGIME recovery path lengths:")
for regime in sorted(regime_recovery.keys()):
    rr = regime_recovery[regime]
    print(f"  {regime}: mean_len={np.mean(rr['mean_lengths']):.2f}+-{np.std(rr['mean_lengths']):.2f}, "
          f"max={np.mean(rr['max_lengths']):.1f}, "
          f"n_paths={np.mean(rr['n_paths']):.1f} "
          f"(n={len(rr['mean_lengths'])})")

print("\nKW tests (recovery paths):")
for metric, res in kw_recovery_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {metric}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 3: Post-Kernel Destination Classes
# =============================================================================

print("\n=== Section 3: Post-Kernel Destination Classes ===")

folio_post_kernel = {}

for folio in all_folios:
    lines = folio_lines.get(folio, [])

    # Track destinations after kernel tokens
    dest_role_counts = Counter()
    dest_class_counts = Counter()
    total_post_kernel = 0

    for line_classes in lines:
        for i in range(len(line_classes) - 1):
            if line_classes[i] in KERNEL_CLASSES:
                dst = line_classes[i + 1]
                if dst not in KERNEL_CLASSES:  # Only non-kernel destinations
                    role = CLASS_TO_ROLE.get(dst, 'UNK')
                    dest_role_counts[role] += 1
                    dest_class_counts[dst] += 1
                    total_post_kernel += 1

    if total_post_kernel > 0:
        role_fracs = {role: round(count / total_post_kernel, 4) for role, count in dest_role_counts.items()}
        top_classes = dest_class_counts.most_common(5)
    else:
        role_fracs = {}
        top_classes = []

    folio_post_kernel[folio] = {
        'role_fractions': role_fracs,
        'top_destination_classes': [{'class': c, 'count': n, 'fraction': round(n / total_post_kernel, 4) if total_post_kernel > 0 else 0} for c, n in top_classes],
        'total_post_kernel_exits': total_post_kernel
    }

# Group by REGIME for role fractions
regime_post_kernel = defaultdict(lambda: {r: [] for r in ['AX', 'EN', 'FL', 'FQ', 'CC']})
for folio, stats in folio_post_kernel.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['total_post_kernel_exits'] > 0:
        for role in ['AX', 'EN', 'FL', 'FQ', 'CC']:
            regime_post_kernel[regime][role].append(stats['role_fractions'].get(role, 0.0))

# KW tests on role fractions
kw_post_kernel_results = {}
for role in ['AX', 'EN', 'FL', 'FQ', 'CC']:
    groups = [regime_post_kernel[r][role] for r in sorted(regime_post_kernel.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_post_kernel_results[role] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': p_val < 0.05
            }
        except ValueError:
            kw_post_kernel_results[role] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

print("\nPer-REGIME post-kernel destination roles:")
for regime in sorted(regime_post_kernel.keys()):
    rpk = regime_post_kernel[regime]
    parts = []
    for role in ['AX', 'EN', 'FL', 'FQ', 'CC']:
        if rpk[role]:
            parts.append(f"{role}={np.mean(rpk[role]):.3f}")
    print(f"  {regime}: {', '.join(parts)} (n={len(rpk['AX'])})")

print("\nKW tests (post-kernel routing):")
for role, res in kw_post_kernel_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {role}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 4: Summary
# =============================================================================

print("\n=== Section 4: Summary ===")

# Count significant KW tests
all_kw = {}
all_kw.update({f"kernel_{k}": v for k, v in kw_kernel_results.items()})
all_kw.update({f"recovery_{k}": v for k, v in kw_recovery_results.items()})
all_kw.update({f"post_kernel_{k}": v for k, v in kw_post_kernel_results.items()})

n_sig = sum(1 for v in all_kw.values() if v['significant'])
n_total_tests = len(all_kw)

print(f"\nSignificant KW tests: {n_sig}/{n_total_tests}")
for name, res in sorted(all_kw.items(), key=lambda x: x[1]['p']):
    sig = "***" if res['significant'] else ""
    print(f"  {name}: p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

if n_sig == 0:
    verdict = "NOT_REGIME_STRATIFIED"
    verdict_detail = "No recovery pathway metric shows significant REGIME dependence"
elif n_sig <= 3:
    verdict = "WEAKLY_REGIME_STRATIFIED"
    verdict_detail = f"{n_sig}/{n_total_tests} metrics show REGIME dependence"
else:
    verdict = "REGIME_STRATIFIED"
    verdict_detail = f"{n_sig}/{n_total_tests} metrics show REGIME dependence"

print(f"\nVerdict: {verdict}")
print(f"  {verdict_detail}")

# =============================================================================
# Build REGIME summary profiles
# =============================================================================

regime_profiles = {}
for regime in sorted(regime_kernel.keys()):
    rk = regime_kernel[regime]
    rr = regime_recovery.get(regime, {'mean_lengths': [], 'max_lengths': [], 'n_paths': []})
    rpk = regime_post_kernel.get(regime, {r: [] for r in ['AX', 'EN', 'FL', 'FQ', 'CC']})

    profile = {
        'n_folios': len(rk['e_rates']),
        'kernel_absorption': {
            'e_rate': {'mean': round(float(np.mean(rk['e_rates'])), 4), 'std': round(float(np.std(rk['e_rates'])), 4)},
            'h_rate': {'mean': round(float(np.mean(rk['h_rates'])), 4), 'std': round(float(np.std(rk['h_rates'])), 4)},
            'k_rate': {'mean': round(float(np.mean(rk['k_rates'])), 4), 'std': round(float(np.std(rk['k_rates'])), 4)},
            'exit_rate': {'mean': round(float(np.mean(rk['exit_rates'])), 4), 'std': round(float(np.std(rk['exit_rates'])), 4)}
        },
        'recovery_paths': {
            'mean_length': {'mean': round(float(np.mean(rr['mean_lengths'])), 4) if rr['mean_lengths'] else 0,
                          'std': round(float(np.std(rr['mean_lengths'])), 4) if rr['mean_lengths'] else 0},
            'mean_max_length': round(float(np.mean(rr['max_lengths'])), 2) if rr['max_lengths'] else 0,
            'mean_n_paths': round(float(np.mean(rr['n_paths'])), 2) if rr['n_paths'] else 0
        },
        'post_kernel_routing': {}
    }
    for role in ['AX', 'EN', 'FL', 'FQ', 'CC']:
        vals = rpk.get(role, [])
        if vals:
            profile['post_kernel_routing'][role] = {
                'mean': round(float(np.mean(vals)), 4),
                'std': round(float(np.std(vals)), 4)
            }

    regime_profiles[regime] = profile

# =============================================================================
# Output JSON
# =============================================================================

output = {
    'metadata': {
        'phase': 'RECOVERY_ARCHITECTURE_DECOMPOSITION',
        'script': 'recovery_pathway_profiling.py',
        'description': 'Per-REGIME kernel absorption rates, recovery path lengths, post-kernel destinations',
        'n_folios': len(all_folios),
        'n_folios_with_regime': sum(1 for f in all_folios if f in folio_to_regime),
        'kernel_classes': sorted(KERNEL_CLASSES),
        'hazard_classes': sorted(HAZARD_CLASSES)
    },
    'regime_profiles': regime_profiles,
    'kw_tests': {
        'kernel_absorption': kw_kernel_results,
        'recovery_paths': kw_recovery_results,
        'post_kernel_routing': kw_post_kernel_results
    },
    'all_kw_summary': {
        'n_tests': n_total_tests,
        'n_significant': n_sig,
        'verdict': verdict,
        'verdict_detail': verdict_detail
    },
    'per_folio': {
        'kernel_stats': folio_kernel_stats,
        'recovery_paths': folio_recovery_paths,
        'post_kernel': {f: {
            'role_fractions': s['role_fractions'],
            'total_exits': s['total_post_kernel_exits']
        } for f, s in folio_post_kernel.items()}
    }
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

output_path = Path(__file__).parent.parent / 'results' / 'recovery_pathway_profiling.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

print(f"\nOutput: {output_path}")
print("Done.")

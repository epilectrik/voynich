"""
RECOVERY_ARCHITECTURE_DECOMPOSITION - Script 2: Escape Strategy Decomposition

Per-REGIME escape strategy fingerprints: EN/CC sub-group routing in recovery
zones, first-EN-after-hazard routing, CC trigger composition.

Sections:
  1. QO-escape class distribution in recovery zones
  2. First-EN-after-hazard routing
  3. CC trigger composition in recovery zones
  4. Escape strategy fingerprints (per-REGIME composite, JS divergence)

Output: results/escape_strategy_decomposition.json
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import kruskal, fisher_exact, chi2_contingency
from scipy.spatial.distance import jensenshannon

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

# =============================================================================
# Constants
# =============================================================================

KERNEL_CLASSES = {1, 2, 3}
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

CLASS_TO_SUBGROUP = {
    7: 'FL_HAZ', 8: 'EN_CHSH', 9: 'FQ_CONN', 10: 'CC_DAIIN',
    11: 'CC_OL', 12: 'CC_OL_D', 13: 'FQ_PAIR', 14: 'FQ_PAIR',
    17: 'CC_OL_D', 23: 'FQ_CLOSER', 30: 'FL_HAZ', 31: 'EN_CHSH',
    32: 'EN_QO', 33: 'EN_QO', 34: 'EN_QO', 35: 'EN_QO',
    36: 'EN_QO', 37: 'EN_MINOR', 38: 'FL_SAFE', 39: 'EN_MINOR',
    40: 'FL_SAFE', 41: 'EN_QO', 42: 'EN_MINOR', 43: 'EN_MINOR',
    44: 'EN_QO', 45: 'EN_QO', 46: 'EN_QO', 47: 'EN_MINOR',
    48: 'EN_MINOR', 49: 'EN_QO'
}

EN_SUBGROUPS = {'EN_QO', 'EN_CHSH', 'EN_MINOR'}
CC_SUBGROUPS = {'CC_DAIIN', 'CC_OL', 'CC_OL_D'}

# =============================================================================
# JSON encoder
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

# =============================================================================
# Load data
# =============================================================================

print("Loading data...")

class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path, 'r', encoding='utf-8') as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']

regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

tx = Transcript()
b_tokens = list(tx.currier_b())
print(f"  Currier B tokens: {len(b_tokens)}")

# Build per-folio line-level class sequences
folio_line_tokens = defaultdict(list)
for t in b_tokens:
    if not t.word.strip() or '*' in t.word:
        continue
    cls = token_to_class.get(t.word)
    if cls is None:
        continue
    folio_line_tokens[(t.folio, t.line)].append(cls)

folio_lines = defaultdict(list)
for (folio, line), classes in sorted(folio_line_tokens.items()):
    folio_lines[folio].append(classes)

all_folios = sorted(folio_lines.keys())
print(f"  Unique B folios: {len(all_folios)}")

# =============================================================================
# Helper: Extract recovery zones from a line
# =============================================================================

def extract_recovery_zones(line_classes):
    """Extract recovery zones: sequences between hazard token and next kernel token."""
    zones = []
    i = 0
    while i < len(line_classes):
        if line_classes[i] in HAZARD_CLASSES:
            # Start collecting after hazard
            zone = []
            j = i + 1
            while j < len(line_classes) and line_classes[j] not in KERNEL_CLASSES:
                zone.append(line_classes[j])
                j += 1
            if zone:  # Only non-empty zones
                zones.append(zone)
            i = j + 1 if j < len(line_classes) else j
        else:
            i += 1
    return zones

# =============================================================================
# Section 1: QO-Escape Class Distribution in Recovery Zones
# =============================================================================

print("\n=== Section 1: EN Sub-Group Distribution in Recovery Zones ===")

folio_en_recovery = {}

for folio in all_folios:
    en_counts = Counter()
    total_en = 0

    for line_classes in folio_lines[folio]:
        zones = extract_recovery_zones(line_classes)
        for zone in zones:
            for cls in zone:
                sg = CLASS_TO_SUBGROUP.get(cls)
                if sg in EN_SUBGROUPS:
                    en_counts[sg] += 1
                    total_en += 1

    if total_en > 0:
        fracs = {sg: round(en_counts[sg] / total_en, 4) for sg in sorted(EN_SUBGROUPS)}
    else:
        fracs = {sg: 0.0 for sg in sorted(EN_SUBGROUPS)}

    folio_en_recovery[folio] = {
        'en_subgroup_fractions': fracs,
        'total_en_in_recovery': total_en,
        'en_subgroup_counts': {sg: en_counts[sg] for sg in sorted(EN_SUBGROUPS)}
    }

# Group by REGIME
regime_en = defaultdict(lambda: {sg: [] for sg in sorted(EN_SUBGROUPS)})
for folio, stats in folio_en_recovery.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['total_en_in_recovery'] > 0:
        for sg in sorted(EN_SUBGROUPS):
            regime_en[regime][sg].append(stats['en_subgroup_fractions'][sg])

# KW tests
kw_en_results = {}
for sg in sorted(EN_SUBGROUPS):
    groups = [regime_en[r][sg] for r in sorted(regime_en.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_en_results[sg] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': bool(p_val < 0.05)
            }
        except ValueError:
            kw_en_results[sg] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

print("\nPer-REGIME EN sub-group fractions in recovery zones:")
for regime in sorted(regime_en.keys()):
    parts = []
    for sg in sorted(EN_SUBGROUPS):
        vals = regime_en[regime][sg]
        if vals:
            parts.append(f"{sg}={np.mean(vals):.3f}")
    print(f"  {regime}: {', '.join(parts)} (n={len(regime_en[regime][sorted(EN_SUBGROUPS)[0]])})")

print("\nKW tests (EN sub-groups in recovery):")
for sg, res in kw_en_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {sg}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 2: First-EN-After-Hazard Routing
# =============================================================================

print("\n=== Section 2: First-EN-After-Hazard Routing ===")

folio_first_en = {}

for folio in all_folios:
    first_en_counts = Counter()
    total_hazard_events = 0

    for line_classes in folio_lines[folio]:
        for i, cls in enumerate(line_classes):
            if cls in HAZARD_CLASSES:
                total_hazard_events += 1
                # Find first EN-role token after this hazard
                for j in range(i + 1, len(line_classes)):
                    next_cls = line_classes[j]
                    sg = CLASS_TO_SUBGROUP.get(next_cls)
                    if sg in EN_SUBGROUPS:
                        first_en_counts[sg] += 1
                        break

    total_first_en = sum(first_en_counts.values())
    if total_first_en > 0:
        fracs = {sg: round(first_en_counts[sg] / total_first_en, 4) for sg in sorted(EN_SUBGROUPS)}
    else:
        fracs = {sg: 0.0 for sg in sorted(EN_SUBGROUPS)}

    folio_first_en[folio] = {
        'first_en_fractions': fracs,
        'total_hazard_events': total_hazard_events,
        'total_first_en_found': total_first_en,
        'first_en_counts': {sg: first_en_counts[sg] for sg in sorted(EN_SUBGROUPS)}
    }

# Group by REGIME
regime_first_en = defaultdict(lambda: {sg: [] for sg in sorted(EN_SUBGROUPS)})
for folio, stats in folio_first_en.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['total_first_en_found'] > 0:
        for sg in sorted(EN_SUBGROUPS):
            regime_first_en[regime][sg].append(stats['first_en_fractions'][sg])

# KW tests
kw_first_en_results = {}
for sg in sorted(EN_SUBGROUPS):
    groups = [regime_first_en[r][sg] for r in sorted(regime_first_en.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_first_en_results[sg] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': bool(p_val < 0.05)
            }
        except ValueError:
            kw_first_en_results[sg] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

# Also aggregate: chi-squared on total counts by REGIME
print("\nPer-REGIME first-EN-after-hazard fractions:")
regime_total_first_en = {}
for regime in sorted(regime_first_en.keys()):
    parts = []
    for sg in sorted(EN_SUBGROUPS):
        vals = regime_first_en[regime][sg]
        if vals:
            parts.append(f"{sg}={np.mean(vals):.3f}")
    print(f"  {regime}: {', '.join(parts)} (n={len(regime_first_en[regime][sorted(EN_SUBGROUPS)[0]])})")

    # Aggregate counts for chi-squared
    total_counts = Counter()
    for folio, stats in folio_first_en.items():
        if folio_to_regime.get(folio) == regime:
            for sg, cnt in stats['first_en_counts'].items():
                total_counts[sg] += cnt
    regime_total_first_en[regime] = total_counts

# Chi-squared on contingency table (REGIME x EN_subgroup)
contingency = []
for regime in sorted(regime_total_first_en.keys()):
    row = [regime_total_first_en[regime].get(sg, 0) for sg in sorted(EN_SUBGROUPS)]
    contingency.append(row)
contingency = np.array(contingency)

if contingency.sum() > 0 and all(contingency.sum(axis=0) > 0):
    try:
        chi2, chi2_p, dof, expected = chi2_contingency(contingency)
        chi2_result = {
            'chi2': round(float(chi2), 4),
            'p': round(float(chi2_p), 6),
            'dof': int(dof),
            'significant': bool(chi2_p < 0.05)
        }
    except ValueError:
        chi2_result = {'chi2': 0, 'p': 1.0, 'dof': 0, 'significant': False}
else:
    chi2_result = {'chi2': 0, 'p': 1.0, 'dof': 0, 'significant': False}

print(f"\nChi-squared (REGIME x first-EN subgroup): chi2={chi2_result['chi2']:.2f}, p={chi2_result['p']:.4f}, "
      f"dof={chi2_result['dof']} {'***' if chi2_result['significant'] else ''}")

print("\nKW tests (first-EN-after-hazard):")
for sg, res in kw_first_en_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {sg}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 3: CC Trigger Composition in Recovery Zones
# =============================================================================

print("\n=== Section 3: CC Trigger Composition in Recovery Zones ===")

folio_cc_recovery = {}

for folio in all_folios:
    cc_counts = Counter()
    total_cc = 0

    for line_classes in folio_lines[folio]:
        zones = extract_recovery_zones(line_classes)
        for zone in zones:
            for cls in zone:
                sg = CLASS_TO_SUBGROUP.get(cls)
                if sg in CC_SUBGROUPS:
                    cc_counts[sg] += 1
                    total_cc += 1

    if total_cc > 0:
        fracs = {sg: round(cc_counts[sg] / total_cc, 4) for sg in sorted(CC_SUBGROUPS)}
    else:
        fracs = {sg: 0.0 for sg in sorted(CC_SUBGROUPS)}

    folio_cc_recovery[folio] = {
        'cc_subgroup_fractions': fracs,
        'total_cc_in_recovery': total_cc,
        'cc_subgroup_counts': {sg: cc_counts[sg] for sg in sorted(CC_SUBGROUPS)}
    }

# Group by REGIME
regime_cc = defaultdict(lambda: {sg: [] for sg in sorted(CC_SUBGROUPS)})
for folio, stats in folio_cc_recovery.items():
    regime = folio_to_regime.get(folio)
    if regime and stats['total_cc_in_recovery'] > 0:
        for sg in sorted(CC_SUBGROUPS):
            regime_cc[regime][sg].append(stats['cc_subgroup_fractions'][sg])

# KW tests
kw_cc_results = {}
for sg in sorted(CC_SUBGROUPS):
    groups = [regime_cc[r][sg] for r in sorted(regime_cc.keys())]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) >= 2:
        try:
            h_stat, p_val = kruskal(*groups)
            n_total = sum(len(g) for g in groups)
            eta_sq = (h_stat - len(groups) + 1) / (n_total - len(groups))
            kw_cc_results[sg] = {
                'H': round(h_stat, 4),
                'p': round(p_val, 6),
                'eta_sq': round(max(0, eta_sq), 4),
                'significant': bool(p_val < 0.05)
            }
        except ValueError:
            kw_cc_results[sg] = {'H': 0, 'p': 1.0, 'eta_sq': 0, 'significant': False}

print("\nPer-REGIME CC sub-group fractions in recovery zones:")
for regime in sorted(regime_cc.keys()):
    parts = []
    for sg in sorted(CC_SUBGROUPS):
        vals = regime_cc[regime][sg]
        if vals:
            parts.append(f"{sg}={np.mean(vals):.3f}")
    n_vals = max(len(regime_cc[regime][sg]) for sg in sorted(CC_SUBGROUPS))
    print(f"  {regime}: {', '.join(parts)} (n={n_vals})")

print("\nKW tests (CC sub-groups in recovery):")
for sg, res in kw_cc_results.items():
    sig = "***" if res['significant'] else ""
    print(f"  {sg}: H={res['H']:.2f}, p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

# =============================================================================
# Section 4: Escape Strategy Fingerprints
# =============================================================================

print("\n=== Section 4: Escape Strategy Fingerprints ===")

# Build composite fingerprint per REGIME
fingerprint_keys = sorted(EN_SUBGROUPS) + sorted(CC_SUBGROUPS)
regime_fingerprints = {}

for regime in sorted(regime_data.keys()):
    fp = {}
    # EN recovery zone fractions (mean across folios)
    for sg in sorted(EN_SUBGROUPS):
        vals = regime_en.get(regime, {}).get(sg, [])
        fp[sg] = round(float(np.mean(vals)), 4) if vals else 0.0

    # First-EN fractions
    for sg in sorted(EN_SUBGROUPS):
        vals = regime_first_en.get(regime, {}).get(sg, [])
        fp[f'first_{sg}'] = round(float(np.mean(vals)), 4) if vals else 0.0

    # CC recovery zone fractions
    for sg in sorted(CC_SUBGROUPS):
        vals = regime_cc.get(regime, {}).get(sg, [])
        fp[sg] = round(float(np.mean(vals)), 4) if vals else 0.0

    regime_fingerprints[regime] = fp

# Compute pairwise JS divergence between REGIME fingerprints
# Use EN recovery + CC recovery fractions as the distribution
fp_vectors = {}
fp_keys = sorted(EN_SUBGROUPS) + sorted(CC_SUBGROUPS)
for regime, fp in regime_fingerprints.items():
    vec = [fp.get(k, 0.0) for k in fp_keys]
    total = sum(vec)
    if total > 0:
        vec = [v / total for v in vec]
    fp_vectors[regime] = vec

print("\nEscape strategy fingerprints (normalized):")
for regime in sorted(fp_vectors.keys()):
    parts = [f"{k}={v:.3f}" for k, v in zip(fp_keys, fp_vectors[regime])]
    print(f"  {regime}: {', '.join(parts)}")

# Pairwise JS divergence
regimes = sorted(fp_vectors.keys())
jsd_matrix = {}
print("\nPairwise JS divergence:")
for i, r1 in enumerate(regimes):
    for j, r2 in enumerate(regimes):
        if i < j:
            jsd = jensenshannon(fp_vectors[r1], fp_vectors[r2])
            jsd_matrix[f"{r1}_vs_{r2}"] = round(float(jsd), 4)
            print(f"  {r1} vs {r2}: JSD={jsd:.4f}")

# =============================================================================
# Overall Summary
# =============================================================================

print("\n=== Overall Summary ===")

all_kw = {}
for sg, res in kw_en_results.items():
    all_kw[f'en_recovery_{sg}'] = res
for sg, res in kw_first_en_results.items():
    all_kw[f'first_en_{sg}'] = res
for sg, res in kw_cc_results.items():
    all_kw[f'cc_recovery_{sg}'] = res

n_sig = sum(1 for v in all_kw.values() if v['significant'])
n_total = len(all_kw)

print(f"\nSignificant KW tests: {n_sig}/{n_total}")
for name, res in sorted(all_kw.items(), key=lambda x: x[1]['p']):
    sig = "***" if res['significant'] else ""
    print(f"  {name}: p={res['p']:.4f}, eta_sq={res['eta_sq']:.3f} {sig}")

print(f"\nChi-squared (first-EN routing): chi2={chi2_result['chi2']:.2f}, p={chi2_result['p']:.4f} "
      f"{'***' if chi2_result['significant'] else ''}")

if n_sig == 0 and not chi2_result['significant']:
    verdict = "NOT_REGIME_STRATIFIED"
    verdict_detail = "No escape strategy metric shows significant REGIME dependence"
elif n_sig <= 2:
    verdict = "WEAKLY_REGIME_STRATIFIED"
    verdict_detail = f"{n_sig}/{n_total} metrics show REGIME dependence"
else:
    verdict = "REGIME_STRATIFIED"
    verdict_detail = f"{n_sig}/{n_total} metrics show REGIME dependence"

print(f"\nVerdict: {verdict}")
print(f"  {verdict_detail}")

# =============================================================================
# Output JSON
# =============================================================================

output = {
    'metadata': {
        'phase': 'RECOVERY_ARCHITECTURE_DECOMPOSITION',
        'script': 'escape_strategy_decomposition.py',
        'description': 'Per-REGIME escape strategy fingerprints and sub-group routing',
        'n_folios': len(all_folios),
        'hazard_classes': sorted(HAZARD_CLASSES),
        'en_subgroups': sorted(EN_SUBGROUPS),
        'cc_subgroups': sorted(CC_SUBGROUPS)
    },
    'kw_tests': {
        'en_recovery_zones': kw_en_results,
        'first_en_after_hazard': kw_first_en_results,
        'cc_recovery_zones': kw_cc_results
    },
    'chi2_first_en': chi2_result,
    'regime_fingerprints': regime_fingerprints,
    'fingerprint_jsd_matrix': jsd_matrix,
    'all_kw_summary': {
        'n_tests': n_total,
        'n_significant': n_sig,
        'verdict': verdict,
        'verdict_detail': verdict_detail
    },
    'per_folio': {
        'en_recovery': {f: {
            'fractions': s['en_subgroup_fractions'],
            'total': s['total_en_in_recovery']
        } for f, s in folio_en_recovery.items()},
        'first_en': {f: {
            'fractions': s['first_en_fractions'],
            'total_hazard': s['total_hazard_events'],
            'total_first_en': s['total_first_en_found']
        } for f, s in folio_first_en.items()},
        'cc_recovery': {f: {
            'fractions': s['cc_subgroup_fractions'],
            'total': s['total_cc_in_recovery']
        } for f, s in folio_cc_recovery.items()}
    }
}

output_path = Path(__file__).parent.parent / 'results' / 'escape_strategy_decomposition.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

print(f"\nOutput: {output_path}")
print("Done.")

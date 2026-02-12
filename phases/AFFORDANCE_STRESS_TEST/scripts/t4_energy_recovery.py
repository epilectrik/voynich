#!/usr/bin/env python3
"""T4: Energy-Recovery Vector Mapping per Affordance Bin.

Maps bins to constraint energy functional and recovery architecture.
Expert predictions:
  - STABILITY_CRITICAL: high e-correlation, high recovery adjacency
  - PHASE_SENSITIVE: deep radial position, high structural coupling
  - ENERGY_SPECIALIZED: high k-ratio, energy-driven
"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Load data ──────────────────────────────────────────────────────

with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
middle_to_sig = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
    middle_to_sig[mid] = data.get('behavioral_signature', {})
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# Load class → token map for FQ identification
with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}

# Load hazard exposure anatomy for role assignments
with open(PROJECT / 'phases' / 'HAZARD_CLASS_VULNERABILITY' / 'results' / 'hazard_exposure_anatomy.json') as f:
    haz_anatomy = json.load(f)

# Build class → role mapping
class_to_role = {}
for cls_str, info in haz_anatomy['section1_class_routing']['per_class'].items():
    class_to_role[int(cls_str)] = info['role']

# FQ classes = FREQUENT_OPERATOR role
FQ_CLASSES = {c for c, r in class_to_role.items() if r == 'FREQUENT_OPERATOR'}

# ── Build corpus lines ─────────────────────────────────────────────

tx = Transcript()
morph = Morphology()

lines_dict = defaultdict(list)
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)
    sig = middle_to_sig.get(mid, {})
    cls = token_to_class.get(word, -1)
    role = class_to_role.get(cls, 'UNKNOWN')
    lines_dict[(token.folio, token.line)].append({
        'word': word,
        'middle': mid,
        'bin': b,
        'cls': cls,
        'role': role,
        'depth': sig.get('radial_depth', 0) if sig else 0,
        'e_ratio': sig.get('e_ratio', 0) if sig else 0,
        'k_ratio': sig.get('k_ratio', 0) if sig else 0,
    })

# Pre-compute per-MIDDLE depth from the affordance table directly
middle_depth_raw = {}
for mid, data in aff['middles'].items():
    middle_depth_raw[mid] = data.get('radial_depth', 0)

print("=" * 70)
print("T4: ENERGY-RECOVERY VECTOR MAPPING PER AFFORDANCE BIN")
print("=" * 70)
print(f"\nCorpus: {len(lines_dict)} lines")
print(f"FQ classes: {sorted(FQ_CLASSES)}")

# ── ANALYSIS 1: Per-bin energy profile ─────────────────────────────

print(f"\n{'=' * 70}")
print("PER-BIN ENERGY PROFILE (from behavioral_signature)")
print("=" * 70)

# Collect per-bin distributions from affordance table
bin_depths = defaultdict(list)
bin_e_ratios = defaultdict(list)
bin_k_ratios = defaultdict(list)
bin_regime_entropy = defaultdict(list)

for mid, data in aff['middles'].items():
    b = data['affordance_bin']
    if b == 4:
        continue
    sig = data.get('behavioral_signature', {})
    if sig:
        bin_depths[b].append(data.get('radial_depth', 0))
        bin_e_ratios[b].append(sig.get('e_ratio', 0))
        bin_k_ratios[b].append(sig.get('k_ratio', 0))
        bin_regime_entropy[b].append(sig.get('regime_entropy', 0))

print(f"\n  {'Bin':>4} {'Label':>25} {'N':>4} {'Depth':>7} {'e_ratio':>8} {'k_ratio':>8} {'R_Entropy':>10}")
print(f"  {'-' * 70}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    n = len(bin_depths[b])
    d = np.mean(bin_depths[b]) if bin_depths[b] else 0
    e = np.mean(bin_e_ratios[b]) if bin_e_ratios[b] else 0
    k = np.mean(bin_k_ratios[b]) if bin_k_ratios[b] else 0
    re = np.mean(bin_regime_entropy[b]) if bin_regime_entropy[b] else 0
    print(f"  {b:>4} {label:>25} {n:>4} {d:>7.3f} {e:>8.3f} {k:>8.3f} {re:>10.3f}")

# ── ANALYSIS 2: FQ adjacency (recovery proximity) ─────────────────

print(f"\n{'=' * 70}")
print("FQ ADJACENCY (Recovery Proximity)")
print("=" * 70)

bin_total = Counter()
bin_fq_adj = Counter()  # adjacent to FQ token
bin_fq_dist = defaultdict(list)  # distance to nearest FQ

for key, tokens in lines_dict.items():
    n = len(tokens)
    # Find FQ positions
    fq_positions = set()
    for i, tok in enumerate(tokens):
        if tok['cls'] in FQ_CLASSES:
            fq_positions.add(i)

    for i, tok in enumerate(tokens):
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        if tok['cls'] in FQ_CLASSES:
            continue  # skip FQ tokens themselves
        bin_total[b] += 1

        # Distance to nearest FQ
        if fq_positions:
            dist = min(abs(i - fp) for fp in fq_positions)
            bin_fq_dist[b].append(dist)

            # Adjacent?
            if dist <= 1:
                bin_fq_adj[b] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Total':>7} {'FQ_adj%':>8} {'MeanDist':>9} {'MedDist':>8}")
print(f"  {'-' * 64}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total[b]
    adj_pct = 100 * bin_fq_adj[b] / total if total > 0 else 0
    mean_d = float(np.mean(bin_fq_dist[b])) if bin_fq_dist[b] else float('nan')
    med_d = float(np.median(bin_fq_dist[b])) if bin_fq_dist[b] else float('nan')
    print(f"  {b:>4} {label:>25} {total:>7} {adj_pct:>7.1f}% {mean_d:>9.2f} {med_d:>8.1f}")

# ── ANALYSIS 3: Post-bin recovery depth ────────────────────────────

print(f"\n{'=' * 70}")
print("POST-BIN RECOVERY DEPTH")
print("=" * 70)
print("(Distance to next e-dominant token after bin's token)")

E_DOMINANT_THRESH = 0.3  # MIDDLE e_ratio > 0.3

bin_recovery_depth = defaultdict(list)

for key, tokens in lines_dict.items():
    n = len(tokens)
    # Find e-dominant positions
    e_dom_positions = set()
    for i, tok in enumerate(tokens):
        sig = middle_to_sig.get(tok['middle'], {})
        if sig and sig.get('e_ratio', 0) > E_DOMINANT_THRESH:
            e_dom_positions.add(i)

    for i, tok in enumerate(tokens):
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        # Distance to next e-dominant token AFTER this position
        forward_dists = [ep - i for ep in e_dom_positions if ep > i]
        if forward_dists:
            bin_recovery_depth[b].append(min(forward_dists))

print(f"\n  {'Bin':>4} {'Label':>25} {'N':>7} {'MeanRecov':>10} {'MedRecov':>9} {'P25':>5} {'P75':>5}")
print(f"  {'-' * 68}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    vals = bin_recovery_depth[b]
    n = len(vals)
    mean_r = np.mean(vals) if vals else float('nan')
    med_r = np.median(vals) if vals else float('nan')
    p25 = np.percentile(vals, 25) if vals else float('nan')
    p75 = np.percentile(vals, 75) if vals else float('nan')
    print(f"  {b:>4} {label:>25} {n:>7} {mean_r:>10.2f} {med_r:>9.1f} {p25:>5.1f} {p75:>5.1f}")

# ── ANALYSIS 4: Regime × bin interaction ───────────────────────────

print(f"\n{'=' * 70}")
print("REGIME x BIN INTERACTION")
print("=" * 70)

# Load regime mapping
with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_to_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Count tokens per (bin, regime)
bin_regime = defaultdict(Counter)  # bin → {REGIME_1: n, ...}

for (folio, line_num), tokens in lines_dict.items():
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    if regime == 'UNKNOWN':
        continue
    for tok in tokens:
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        bin_regime[b][regime] += 1

regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

print(f"\n  {'Bin':>4} {'Label':>25} {'R1%':>6} {'R2%':>6} {'R3%':>6} {'R4%':>6} {'Dominant':>10}")
print(f"  {'-' * 68}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = sum(bin_regime[b][r] for r in regimes)
    pcts = [100 * bin_regime[b][r] / total if total > 0 else 0 for r in regimes]
    dominant = regimes[np.argmax(pcts)] if total > 0 else '?'
    print(f"  {b:>4} {label:>25} {pcts[0]:>5.1f}% {pcts[1]:>5.1f}% {pcts[2]:>5.1f}% {pcts[3]:>5.1f}% {dominant:>10}")

# ── STATISTICAL TESTS ──────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("STATISTICAL TESTS")
print("=" * 70)

stat_results = {}

# KW on radial_depth across bins (from affordance table, not corpus)
depth_groups = [bin_depths[b] for b in FUNCTIONAL_BINS if len(bin_depths[b]) >= 3]
depth_labels = [b for b in FUNCTIONAL_BINS if len(bin_depths[b]) >= 3]
if len(depth_groups) >= 2:
    h, p = stats.kruskal(*depth_groups)
    print(f"\n  Kruskal-Wallis on radial_depth across bins:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_depth'] = {'H': float(h), 'p': float(p)}

# KW on FQ distance across bins
fq_groups = [bin_fq_dist[b] for b in FUNCTIONAL_BINS if len(bin_fq_dist[b]) >= 5]
fq_labels = [b for b in FUNCTIONAL_BINS if len(bin_fq_dist[b]) >= 5]
if len(fq_groups) >= 2:
    h, p = stats.kruskal(*fq_groups)
    print(f"\n  Kruskal-Wallis on FQ distance across bins:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_fq_dist'] = {'H': float(h), 'p': float(p)}

# KW on recovery depth across bins
recov_groups = [bin_recovery_depth[b] for b in FUNCTIONAL_BINS if len(bin_recovery_depth[b]) >= 5]
recov_labels = [b for b in FUNCTIONAL_BINS if len(bin_recovery_depth[b]) >= 5]
if len(recov_groups) >= 2:
    h, p = stats.kruskal(*recov_groups)
    print(f"\n  Kruskal-Wallis on recovery depth across bins:")
    print(f"    H = {h:.3f}, p = {p:.2e}")
    stat_results['kruskal_recovery_depth'] = {'H': float(h), 'p': float(p)}

# Spearman: depth vs FQ adjacency across bins
bin_mean_depth = [np.mean(bin_depths[b]) for b in FUNCTIONAL_BINS if bin_depths[b] and bin_fq_dist[b]]
bin_mean_fq = [np.mean(bin_fq_dist[b]) for b in FUNCTIONAL_BINS if bin_depths[b] and bin_fq_dist[b]]
if len(bin_mean_depth) >= 4:
    rho, p = stats.spearmanr(bin_mean_depth, bin_mean_fq)
    print(f"\n  Spearman: radial_depth vs FQ_distance (bin-level):")
    print(f"    rho = {rho:.3f}, p = {p:.4f}")
    stat_results['spearman_depth_fq'] = {'rho': float(rho), 'p': float(p)}

# Chi-square on bin × regime
regime_contingency = np.array([
    [bin_regime[b][r] for r in regimes]
    for b in FUNCTIONAL_BINS
])
if regime_contingency.sum() > 0:
    chi2, p, dof, exp = stats.chi2_contingency(regime_contingency)
    print(f"\n  Chi-square on bin x regime:")
    print(f"    chi2 = {chi2:.3f}, df = {dof}, p = {p:.2e}")
    stat_results['chi2_bin_regime'] = {'chi2': float(chi2), 'df': int(dof), 'p': float(p)}

# ── EXPERT PREDICTION VERIFICATION ────────────────────────────────

print(f"\n{'=' * 70}")
print("EXPERT PREDICTION VERIFICATION")
print("=" * 70)

predictions = []

# P1: STABILITY_CRITICAL (8) high e-ratio
b8_e = np.mean(bin_e_ratios[8]) if bin_e_ratios[8] else 0
all_e = [np.mean(bin_e_ratios[b]) for b in FUNCTIONAL_BINS if bin_e_ratios[b]]
median_e = np.median(all_e) if all_e else 0
p1 = b8_e > median_e
predictions.append(('STABILITY_CRITICAL high e_ratio', p1, f"e_ratio={b8_e:.3f} vs median={median_e:.3f}"))

# P2: STABILITY_CRITICAL (8) high recovery adjacency (low FQ distance)
b8_fq = np.mean(bin_fq_dist[8]) if bin_fq_dist[8] else float('inf')
all_fq = [np.mean(bin_fq_dist[b]) for b in FUNCTIONAL_BINS if bin_fq_dist[b]]
median_fq = np.median(all_fq)
p2 = b8_fq < median_fq
predictions.append(('STABILITY_CRITICAL close to FQ (recovery)', p2, f"fq_dist={b8_fq:.2f} vs median={median_fq:.2f}"))

# P3: PHASE_SENSITIVE (9) deep radial position
b9_d = np.mean(bin_depths[9]) if bin_depths[9] else 0
all_d = [np.mean(bin_depths[b]) for b in FUNCTIONAL_BINS if bin_depths[b]]
max_d = max(all_d) if all_d else 0
p3 = b9_d >= max_d * 0.9  # within 90% of deepest
predictions.append(('PHASE_SENSITIVE deepest radial depth', p3, f"depth={b9_d:.3f} vs max={max_d:.3f}"))

# P4: ENERGY_SPECIALIZED (7) high k-ratio
b7_k = np.mean(bin_k_ratios[7]) if bin_k_ratios[7] else 0
all_k = [np.mean(bin_k_ratios[b]) for b in FUNCTIONAL_BINS if bin_k_ratios[b]]
max_k = max(all_k) if all_k else 0
p4 = b7_k >= max_k * 0.9  # within 90% of highest k
predictions.append(('ENERGY_SPECIALIZED highest k_ratio', p4, f"k_ratio={b7_k:.3f} vs max={max_k:.3f}"))

# P5: HUB_UNIVERSAL (6) shallow depth
b6_d = np.mean(bin_depths[6]) if bin_depths[6] else float('inf')
min_d = min(all_d) if all_d else 0
p5 = b6_d <= min_d * 1.1  # within 110% of shallowest
predictions.append(('HUB_UNIVERSAL shallowest depth', p5, f"depth={b6_d:.3f} vs min={min_d:.3f}"))

# P6: STABILITY_CRITICAL (8) enriched in REGIME_2 (per C894, recovery→R2)
b8_r2 = bin_regime[8].get('REGIME_2', 0)
b8_total_r = sum(bin_regime[8][r] for r in regimes)
b8_r2_frac = b8_r2 / b8_total_r if b8_total_r > 0 else 0
p6 = b8_r2_frac > 0.25  # R2 fraction above 25%
predictions.append(('STABILITY_CRITICAL R2-enriched', p6, f"R2_fraction={b8_r2_frac:.3f}"))

for name, result, detail in predictions:
    status = "CONFIRMED" if result else "REJECTED"
    print(f"\n  [{status}] {name}")
    print(f"    {detail}")

confirmed = sum(1 for _, r, _ in predictions if r)
print(f"\n  SCORE: {confirmed}/{len(predictions)} predictions confirmed")

# ── Save results ───────────────────────────────────────────────────

results = {
    'metadata': {
        'phase': 'AFFORDANCE_STRESS_TEST',
        'test': 'T4_ENERGY_RECOVERY',
        'fq_classes': sorted(FQ_CLASSES),
        'e_dominant_threshold': E_DOMINANT_THRESH,
    },
    'per_bin': {},
    'statistical_tests': stat_results,
    'predictions': {name: {'confirmed': bool(result), 'detail': detail} for name, result, detail in predictions},
}

for b in FUNCTIONAL_BINS:
    total = bin_total[b]
    results['per_bin'][str(b)] = {
        'label': bin_labels.get(b, '?'),
        'mean_radial_depth': round(float(np.mean(bin_depths[b])), 4) if bin_depths[b] else None,
        'mean_e_ratio': round(float(np.mean(bin_e_ratios[b])), 4) if bin_e_ratios[b] else None,
        'mean_k_ratio': round(float(np.mean(bin_k_ratios[b])), 4) if bin_k_ratios[b] else None,
        'mean_regime_entropy': round(float(np.mean(bin_regime_entropy[b])), 4) if bin_regime_entropy[b] else None,
        'fq_adjacency_rate': round(bin_fq_adj[b] / total, 4) if total > 0 else 0,
        'mean_fq_distance': round(float(np.mean(bin_fq_dist[b])), 3) if bin_fq_dist[b] else None,
        'mean_recovery_depth': round(float(np.mean(bin_recovery_depth[b])), 3) if bin_recovery_depth[b] else None,
        'regime_distribution': {r: bin_regime[b][r] for r in regimes},
    }

out_path = PROJECT / 'phases' / 'AFFORDANCE_STRESS_TEST' / 'results' / 't4_energy_recovery.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")

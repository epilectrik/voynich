#!/usr/bin/env python3
"""T1: Hazard-Exposure Profiling per Affordance Bin.

Tests whether bins map to distinct positions in hazard topology.
Expert predictions:
  - PHASE_SENSITIVE and STABILITY_CRITICAL concentrate near hazard
  - ENERGY_SPECIALIZED is hazard-distant
  - FLOW_TERMINAL is structurally outside forbidden topology
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

# Affordance table → MIDDLE→bin mapping
with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
    aff = json.load(f)

middle_to_bin = {}
bin_labels = {}
for mid, data in aff['middles'].items():
    middle_to_bin[mid] = data['affordance_bin']
for b, meta in aff['_metadata']['affordance_bins'].items():
    bin_labels[int(b)] = meta['label']

FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]

# Forbidden transitions (17 token-level bigrams)
with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json') as f:
    inv = json.load(f)

forbidden_pairs = set()
forbidden_sources = set()
forbidden_targets = set()
for t in inv['transitions']:
    forbidden_pairs.add((t['source'], t['target']))
    forbidden_sources.add(t['source'])
    forbidden_targets.add(t['target'])

# Class → token map (for hazard class identification)
with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    class_map = json.load(f)

token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

# ── Build corpus lines ─────────────────────────────────────────────

tx = Transcript()
morph = Morphology()

# Group tokens by (folio, line)
lines_dict = defaultdict(list)
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    mid = m.middle if m.middle else ''
    b = middle_to_bin.get(mid, -1)
    lines_dict[(token.folio, token.line)].append({
        'word': word,
        'middle': mid,
        'bin': b,
        'cls': token_to_class.get(word, -1),
    })

print("=" * 70)
print("T1: HAZARD-EXPOSURE PROFILING PER AFFORDANCE BIN")
print("=" * 70)
print(f"\nCorpus: {len(lines_dict)} lines, {sum(len(v) for v in lines_dict.values())} tokens")

# ── ANALYSIS 1: Forbidden transition MIDDLE involvement ────────────

# Extract MIDDLEs from forbidden transition tokens
source_middles = set()
target_middles = set()
for s in forbidden_sources:
    m = morph.extract(s)
    if m.middle:
        source_middles.add(m.middle)
for t in forbidden_targets:
    m = morph.extract(t)
    if m.middle:
        target_middles.add(m.middle)
hazard_middles = source_middles | target_middles

print(f"\nForbidden transition MIDDLEs:")
print(f"  Sources: {sorted(source_middles)}")
print(f"  Targets: {sorted(target_middles)}")
print(f"  Combined: {len(hazard_middles)} unique MIDDLEs")

# Map hazard MIDDLEs to bins
print(f"\n  Hazard MIDDLE -> Bin:")
for mid in sorted(hazard_middles):
    b = middle_to_bin.get(mid, -1)
    label = bin_labels.get(b, 'UNKNOWN')
    role = 'SOURCE' if mid in source_middles else ''
    role += '+TARGET' if mid in target_middles else ''
    if role.startswith('+'):
        role = role[1:]
    print(f"    {mid:>10} -> Bin {b:>2} ({label:>25}) [{role}]")

# ── ANALYSIS 2: Class-based hazard proximity ───────────────────────

print(f"\n{'=' * 70}")
print("CLASS-BASED HAZARD PROXIMITY")
print("=" * 70)

bin_total = Counter()
bin_hazard_cls = Counter()
bin_adj_hazard = Counter()
bin_distances_cls = defaultdict(list)

for key, tokens in lines_dict.items():
    n = len(tokens)
    # Identify hazard positions (tokens whose ICC class is hazard)
    hazard_positions = set()
    for i, tok in enumerate(tokens):
        if tok['cls'] in HAZARD_CLASSES:
            hazard_positions.add(i)

    for i, tok in enumerate(tokens):
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        bin_total[b] += 1

        is_haz = tok['cls'] in HAZARD_CLASSES
        if is_haz:
            bin_hazard_cls[b] += 1

        # Distance to nearest hazard token
        if hazard_positions:
            dist = min(abs(i - hp) for hp in hazard_positions)
            bin_distances_cls[b].append(dist)

        # Adjacent to hazard (but not itself hazard)?
        if not is_haz:
            adj = False
            if i > 0 and (i - 1) in hazard_positions:
                adj = True
            if i < n - 1 and (i + 1) in hazard_positions:
                adj = True
            if adj:
                bin_adj_hazard[b] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'Total':>7} {'Hazard%':>8} {'AdjHaz%':>8} {'MeanDist':>9} {'MedDist':>8}")
print(f"  {'-' * 72}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total[b]
    haz_pct = 100 * bin_hazard_cls[b] / total if total > 0 else 0
    non_haz = total - bin_hazard_cls[b]
    adj_pct = 100 * bin_adj_hazard[b] / non_haz if non_haz > 0 else 0
    mean_d = float(np.mean(bin_distances_cls[b])) if bin_distances_cls[b] else float('nan')
    med_d = float(np.median(bin_distances_cls[b])) if bin_distances_cls[b] else float('nan')
    print(f"  {b:>4} {label:>25} {total:>7} {haz_pct:>7.1f}% {adj_pct:>7.1f}% {mean_d:>9.2f} {med_d:>8.1f}")

# ── ANALYSIS 3: Forbidden-MIDDLE proximity ─────────────────────────

print(f"\n{'=' * 70}")
print("FORBIDDEN-MIDDLE PROXIMITY")
print("=" * 70)

bin_has_hazard_mid = Counter()
bin_adj_hazard_mid = Counter()
bin_hazard_mid_dist = defaultdict(list)

for key, tokens in lines_dict.items():
    n = len(tokens)
    hazard_mid_positions = set()
    for i, tok in enumerate(tokens):
        if tok['middle'] in hazard_middles:
            hazard_mid_positions.add(i)

    for i, tok in enumerate(tokens):
        b = tok['bin']
        if b == 4 or b == -1:
            continue
        if tok['middle'] in hazard_middles:
            bin_has_hazard_mid[b] += 1

        if hazard_mid_positions:
            dist = min(abs(i - hp) for hp in hazard_mid_positions)
            bin_hazard_mid_dist[b].append(dist)

        if tok['middle'] not in hazard_middles:
            adj = False
            if i > 0 and tokens[i - 1]['middle'] in hazard_middles:
                adj = True
            if i < n - 1 and tokens[i + 1]['middle'] in hazard_middles:
                adj = True
            if adj:
                bin_adj_hazard_mid[b] += 1

print(f"\n  {'Bin':>4} {'Label':>25} {'HazMid%':>8} {'AdjHzM%':>8} {'MeanDist':>9} {'MedDist':>8}")
print(f"  {'-' * 64}")
for b in FUNCTIONAL_BINS:
    label = bin_labels.get(b, '?')
    total = bin_total[b]
    hm_pct = 100 * bin_has_hazard_mid[b] / total if total > 0 else 0
    non_hm = total - bin_has_hazard_mid[b]
    adj_pct = 100 * bin_adj_hazard_mid[b] / non_hm if non_hm > 0 else 0
    mean_d = float(np.mean(bin_hazard_mid_dist[b])) if bin_hazard_mid_dist[b] else float('nan')
    med_d = float(np.median(bin_hazard_mid_dist[b])) if bin_hazard_mid_dist[b] else float('nan')
    print(f"  {b:>4} {label:>25} {hm_pct:>7.1f}% {adj_pct:>7.1f}% {mean_d:>9.2f} {med_d:>8.1f}")

# ── STATISTICAL TESTS ──────────────────────────────────────────────

print(f"\n{'=' * 70}")
print("STATISTICAL TESTS")
print("=" * 70)

stat_results = {}

# KW on class-based hazard distance
groups_cls = [bin_distances_cls[b] for b in FUNCTIONAL_BINS if len(bin_distances_cls[b]) >= 5]
labels_cls = [b for b in FUNCTIONAL_BINS if len(bin_distances_cls[b]) >= 5]
if len(groups_cls) >= 2:
    h_stat, p_val = stats.kruskal(*groups_cls)
    print(f"\n  Kruskal-Wallis on distance to nearest hazard-class token:")
    print(f"    H = {h_stat:.3f}, p = {p_val:.2e}")
    print(f"    Bins tested: {labels_cls}")
    stat_results['kruskal_hazard_class_distance'] = {'H': float(h_stat), 'p': float(p_val)}

# KW on forbidden-MIDDLE distance
groups_mid = [bin_hazard_mid_dist[b] for b in FUNCTIONAL_BINS if len(bin_hazard_mid_dist[b]) >= 5]
labels_mid = [b for b in FUNCTIONAL_BINS if len(bin_hazard_mid_dist[b]) >= 5]
if len(groups_mid) >= 2:
    h_stat2, p_val2 = stats.kruskal(*groups_mid)
    print(f"\n  Kruskal-Wallis on distance to nearest forbidden-MIDDLE token:")
    print(f"    H = {h_stat2:.3f}, p = {p_val2:.2e}")
    stat_results['kruskal_forbidden_middle_distance'] = {'H': float(h_stat2), 'p': float(p_val2)}

# Chi-square on bin × hazard class membership
obs = np.array([[bin_hazard_cls[b], bin_total[b] - bin_hazard_cls[b]] for b in FUNCTIONAL_BINS])
if obs.min() >= 0 and obs.sum() > 0:
    chi2, p, dof, expected = stats.chi2_contingency(obs)
    print(f"\n  Chi-square on bin x hazard-class membership:")
    print(f"    chi2 = {chi2:.3f}, df = {dof}, p = {p:.2e}")
    stat_results['chi2_hazard_membership'] = {'chi2': float(chi2), 'df': int(dof), 'p': float(p)}

# Chi-square on bin × forbidden-MIDDLE membership
obs2 = np.array([[bin_has_hazard_mid[b], bin_total[b] - bin_has_hazard_mid[b]] for b in FUNCTIONAL_BINS])
if obs2.min() >= 0 and obs2.sum() > 0:
    chi2_2, p_2, dof_2, exp_2 = stats.chi2_contingency(obs2)
    print(f"\n  Chi-square on bin x forbidden-MIDDLE membership:")
    print(f"    chi2 = {chi2_2:.3f}, df = {dof_2}, p = {p_2:.2e}")
    stat_results['chi2_forbidden_middle'] = {'chi2': float(chi2_2), 'df': int(dof_2), 'p': float(p_2)}

# ── ANALYSIS 4: Bin × Bin forbidden topology ──────────────────────

print(f"\n{'=' * 70}")
print("BIN x BIN FORBIDDEN TOPOLOGY")
print("=" * 70)

print(f"\n  Forbidden transitions mapped to bin pairs:")
forbidden_bin_pairs = Counter()
for t in inv['transitions']:
    s_mid = morph.extract(t['source']).middle or '?'
    t_mid = morph.extract(t['target']).middle or '?'
    s_bin = middle_to_bin.get(s_mid, -1)
    t_bin = middle_to_bin.get(t_mid, -1)
    s_label = bin_labels.get(s_bin, 'UNK')[:12]
    t_label = bin_labels.get(t_bin, 'UNK')[:12]
    print(f"    {t['source']:>8} (mid={s_mid:>6}, B{s_bin:>2}) -> {t['target']:>8} (mid={t_mid:>6}, B{t_bin:>2})")
    if s_bin >= 0 and t_bin >= 0 and s_bin != 4 and t_bin != 4:
        forbidden_bin_pairs[(s_bin, t_bin)] += 1

print(f"\n  Bin-pair forbidden counts (excluding BULK):")
for (sb, tb), count in sorted(forbidden_bin_pairs.items()):
    print(f"    B{sb} ({bin_labels.get(sb, '?'):>25}) -> B{tb} ({bin_labels.get(tb, '?'):>25}): {count}")

# ── EXPERT PREDICTION CHECK ───────────────────────────────────────

print(f"\n{'=' * 70}")
print("EXPERT PREDICTION VERIFICATION")
print("=" * 70)

predictions = []

# P1: PHASE_SENSITIVE (9) near hazard — low mean distance
b9_dist = np.mean(bin_distances_cls[9]) if bin_distances_cls[9] else float('inf')
all_dists = [np.mean(bin_distances_cls[b]) for b in FUNCTIONAL_BINS if bin_distances_cls[b]]
median_dist = np.median(all_dists)
p1 = b9_dist < median_dist
predictions.append(('PHASE_SENSITIVE near hazard', p1, f"mean_dist={b9_dist:.2f} vs median={median_dist:.2f}"))

# P2: STABILITY_CRITICAL (8) near hazard
b8_dist = np.mean(bin_distances_cls[8]) if bin_distances_cls[8] else float('inf')
p2 = b8_dist < median_dist
predictions.append(('STABILITY_CRITICAL near hazard', p2, f"mean_dist={b8_dist:.2f} vs median={median_dist:.2f}"))

# P3: ENERGY_SPECIALIZED (7) hazard-distant
b7_dist = np.mean(bin_distances_cls[7]) if bin_distances_cls[7] else 0
p3 = b7_dist > median_dist
predictions.append(('ENERGY_SPECIALIZED hazard-distant', p3, f"mean_dist={b7_dist:.2f} vs median={median_dist:.2f}"))

# P4: FLOW_TERMINAL (0) outside forbidden topology — low forbidden_middle_rate
b0_fm = bin_has_hazard_mid[0] / bin_total[0] if bin_total[0] > 0 else 1
all_fm = [bin_has_hazard_mid[b] / bin_total[b] for b in FUNCTIONAL_BINS if bin_total[b] > 0]
median_fm = np.median(all_fm)
p4 = b0_fm < median_fm
predictions.append(('FLOW_TERMINAL outside forbidden topology', p4, f"forbidden_mid_rate={b0_fm:.3f} vs median={median_fm:.3f}"))

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
        'test': 'T1_HAZARD_EXPOSURE',
        'n_functional_bins': len(FUNCTIONAL_BINS),
        'n_forbidden_transitions': 17,
        'hazard_classes': sorted(HAZARD_CLASSES),
        'hazard_middles': sorted(hazard_middles),
    },
    'per_bin': {},
    'statistical_tests': stat_results,
    'forbidden_bin_topology': {},
    'predictions': {name: {'confirmed': bool(result), 'detail': detail} for name, result, detail in predictions},
}

for b in FUNCTIONAL_BINS:
    total = bin_total[b]
    non_haz = total - bin_hazard_cls[b]
    non_hm = total - bin_has_hazard_mid[b]
    results['per_bin'][str(b)] = {
        'label': bin_labels.get(b, '?'),
        'total_tokens': total,
        'hazard_class_rate': round(bin_hazard_cls[b] / total, 4) if total > 0 else 0,
        'hazard_adjacent_rate': round(bin_adj_hazard[b] / non_haz, 4) if non_haz > 0 else 0,
        'mean_distance_to_hazard_class': round(float(np.mean(bin_distances_cls[b])), 3) if bin_distances_cls[b] else None,
        'median_distance_to_hazard_class': round(float(np.median(bin_distances_cls[b])), 1) if bin_distances_cls[b] else None,
        'forbidden_middle_rate': round(bin_has_hazard_mid[b] / total, 4) if total > 0 else 0,
        'mean_distance_to_forbidden_middle': round(float(np.mean(bin_hazard_mid_dist[b])), 3) if bin_hazard_mid_dist[b] else None,
    }

for (sb, tb), count in forbidden_bin_pairs.items():
    results['forbidden_bin_topology'][f"{sb}_{tb}"] = {
        'source_bin': sb, 'source_label': bin_labels.get(sb, '?'),
        'target_bin': tb, 'target_label': bin_labels.get(tb, '?'),
        'forbidden_count': count,
    }

out_path = PROJECT / 'phases' / 'AFFORDANCE_STRESS_TEST' / 'results' / 't1_hazard_exposure.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")

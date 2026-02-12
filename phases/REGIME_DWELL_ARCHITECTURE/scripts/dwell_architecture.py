"""
REGIME Dwell Architecture (Phase 326)

Probes dwell-time interactions and memory architecture:
  T1: Dwell geometry in 6-state macro automaton (uniform vs selective stretching)
  T2: Dwell vs hazard class density
  T3: Dwell vs energy-depth geometry (spectral radial depth)
  T4: HT density vs dwell (cognitive pacing)
  T5: Empirical hazard function h(t) at 3 resolution levels
  T5b: First-order Markov null model (is non-geometric dwell a topology artifact?)
  T6: Non-geometric test for all 6 macro-states
  T6b: Within-AXM compositional drift (early-run vs late-run class entropy)
  T7: Weibull shape parameter x REGIME (does REGIME modulate memory shape?)
  T8: AXM exit trigger analysis (exit skyline + boundary class enrichment)

All tests include section controls per C1005 methodology.
Decision gate: T5b determines whether non-geometric dwell is genuine memory
or a topology artifact of 6-state compression (phase-type distribution).
"""

import json
import sys
import os
from collections import defaultdict

import numpy as np
from scipy import stats
from numpy.linalg import lstsq

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

# ── Constants ──────────────────────────────────────────────────────────────

REGIME_ORDER = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
REGIME_RANK = {r: i for i, r in enumerate(REGIME_ORDER)}
REGIME_CEI = {'REGIME_2': 0.367, 'REGIME_1': 0.510, 'REGIME_4': 0.584, 'REGIME_3': 0.717}

# 6-state macro partition (C976, from t3_merged_automaton.json)
MACRO_NAMES = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']
MACRO_PARTITION = {
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'AXm':     {3, 5, 18, 19, 42, 45},
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}
CLASS_TO_MACRO = {}
for macro, classes in MACRO_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = macro

# ── Load data ──────────────────────────────────────────────────────────────

with open('data/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_map = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# ── Build per-folio token sequences with macro-state labels ───────────────

folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}
folio_ht_body = defaultdict(lambda: {'ht': 0, 'total': 0})
folio_ht_line1 = defaultdict(lambda: {'ht': 0, 'total': 0})
folio_link_count = defaultdict(int)
folio_token_count = defaultdict(int)

# Track paragraph starts for line-1 identification
# Line 1 of each paragraph = first line after a paragraph break
# Simplification: use line number within folio (line "1" per section)
para_first_lines = set()  # Will identify based on paragraph structure

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = token.line
    folio_section[folio] = token.section
    folio_token_count[folio] += 1

    # Macro-state assignment (classified tokens only)
    cls = token_to_class.get(w)
    macro = CLASS_TO_MACRO.get(cls) if cls else None

    # HT identification
    analysis = decoder.analyze_token(w)
    is_ht = getattr(analysis, 'is_ht', False) if analysis else False

    # LINK identification (for C665 stationarity check)
    m = morph.extract(w)
    if m.middle and m.middle.startswith('l') and m.prefix in ('ch', 'sh'):
        folio_link_count[folio] += 1

    # Store macro-state sequence (excluding HT for T1)
    if macro:
        folio_lines[folio][line].append({
            'word': w,
            'macro': macro,
            'class': cls,
            'middle': m.middle,
        })

    # HT density tracking
    # Use line number to approximate line-1 vs body
    # Line-1 heuristic: first line in each group (paragraph)
    if line == '1' or line == 1:
        folio_ht_line1[folio]['total'] += 1
        if is_ht:
            folio_ht_line1[folio]['ht'] += 1
    else:
        folio_ht_body[folio]['total'] += 1
        if is_ht:
            folio_ht_body[folio]['ht'] += 1

print(f"Folios with macro-state data: {len(folio_lines)}")
total_classified = sum(len(t) for lines in folio_lines.values() for t in lines.values())
print(f"Total classified tokens: {total_classified}")

# ── Run-length computation ─────────────────────────────────────────────────

def compute_run_lengths_by_state(line_sequences):
    """Compute run lengths per macro-state across all lines."""
    state_runs = defaultdict(list)
    for seq in line_sequences:
        if len(seq) < 2:
            continue
        current_state = seq[0]['macro']
        current_run = 1
        for tok in seq[1:]:
            if tok['macro'] == current_state:
                current_run += 1
            else:
                state_runs[current_state].append(current_run)
                current_state = tok['macro']
                current_run = 1
        state_runs[current_state].append(current_run)
    return state_runs


def compute_occupancy(line_sequences):
    """Fraction of tokens in each macro-state."""
    counts = defaultdict(int)
    total = 0
    for seq in line_sequences:
        for tok in seq:
            counts[tok['macro']] += 1
            total += 1
    return {s: counts[s] / total if total > 0 else 0 for s in MACRO_NAMES}


def compute_overall_run_length(line_sequences):
    """Mean run length across all states."""
    all_runs = []
    for seq in line_sequences:
        if len(seq) < 2:
            continue
        current_state = seq[0]['macro']
        current_run = 1
        for tok in seq[1:]:
            if tok['macro'] == current_state:
                current_run += 1
            else:
                all_runs.append(current_run)
                current_state = tok['macro']
                current_run = 1
        all_runs.append(current_run)
    return float(np.mean(all_runs)) if all_runs else None


def section_residualize(x, y, sections, section_map={'B': 0, 'H': 1, 'S': 2}):
    """Partial correlation controlling for section using dummy regression."""
    s = np.array([section_map.get(sec, 0) for sec in sections])
    S_dummies = np.column_stack([(s == i).astype(float) for i in range(3)])
    cx, _, _, _ = lstsq(S_dummies, x, rcond=None)
    cy, _, _, _ = lstsq(S_dummies, y, rcond=None)
    return x - S_dummies @ cx, y - S_dummies @ cy

# ── Per-folio metrics ──────────────────────────────────────────────────────

folio_metrics = []

for folio, lines_dict in folio_lines.items():
    regime = regime_map.get(folio)
    if not regime:
        continue

    line_seqs = [v for v in lines_dict.values() if len(v) >= 2]
    if not line_seqs:
        continue

    state_runs = compute_run_lengths_by_state(line_seqs)
    occupancy = compute_occupancy(line_seqs)
    overall_rl = compute_overall_run_length(line_seqs)

    # Per-state mean run lengths
    state_mean_rl = {}
    for s in MACRO_NAMES:
        runs = state_runs.get(s, [])
        state_mean_rl[s] = float(np.mean(runs)) if runs else None

    # HT density
    body = folio_ht_body[folio]
    body_ht_density = body['ht'] / body['total'] if body['total'] > 0 else None
    l1 = folio_ht_line1[folio]
    line1_ht_density = l1['ht'] / l1['total'] if l1['total'] > 0 else None

    # LINK density
    link_density = folio_link_count[folio] / folio_token_count[folio] if folio_token_count[folio] > 0 else None

    # Hazard class density (tokens in FL_HAZ classes / total classified)
    n_classified = sum(len(seq) for seq in line_seqs)
    n_hazard = sum(1 for seq in line_seqs for tok in seq if tok['macro'] == 'FL_HAZ')
    hazard_density = n_hazard / n_classified if n_classified > 0 else None

    folio_metrics.append({
        'folio': folio,
        'regime': regime,
        'section': folio_section.get(folio, 'UNK'),
        'overall_run_length': overall_rl,
        'state_run_lengths': state_mean_rl,
        'occupancy': occupancy,
        'body_ht_density': body_ht_density,
        'line1_ht_density': line1_ht_density,
        'link_density': link_density,
        'hazard_density': hazard_density,
        'n_classified': n_classified,
    })

print(f"Folios with metrics: {len(folio_metrics)}")

# Verify AXM occupancy
axm_occ = np.mean([m['occupancy']['AXM'] for m in folio_metrics])
print(f"Mean AXM occupancy: {axm_occ:.3f} (expected ~0.677)")

# ═══════════════════════════════════════════════════════════════════════════
# T1: DWELL-TIME GEOMETRY IN 6-STATE AUTOMATON
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T1: DWELL-TIME GEOMETRY IN 6-STATE AUTOMATON")
print("=" * 70)

# Per REGIME, per state: mean run length
t1_regime_state = {}
for regime in REGIME_ORDER:
    sub = [m for m in folio_metrics if m['regime'] == regime]
    t1_regime_state[regime] = {}
    for state in MACRO_NAMES:
        vals = [m['state_run_lengths'][state] for m in sub if m['state_run_lengths'][state] is not None]
        t1_regime_state[regime][state] = {
            'n': len(vals),
            'mean': float(np.mean(vals)) if vals else None,
            'std': float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
        }

print("\nMean run length by REGIME x State:")
header = f"{'REGIME':<12}" + "".join(f"{s:<10}" for s in MACRO_NAMES)
print(header)
for regime in REGIME_ORDER:
    row = f"{regime:<12}"
    for state in MACRO_NAMES:
        v = t1_regime_state[regime][state]['mean']
        row += f"{v:<10.3f}" if v else f"{'N/A':<10}"
    print(row)

# Per-state Spearman(REGIME rank, run length) — does rho vary by state?
t1_per_state_spearman = {}
print("\nPer-state Spearman (REGIME rank vs run length):")
for state in MACRO_NAMES:
    valid = [(REGIME_RANK[m['regime']], m['state_run_lengths'][state])
             for m in folio_metrics if m['state_run_lengths'][state] is not None]
    if len(valid) < 5:
        print(f"  {state}: n={len(valid)} (too few)")
        t1_per_state_spearman[state] = {'n': len(valid), 'status': 'skipped'}
        continue
    ranks, vals = zip(*valid)
    rho, p = stats.spearmanr(ranks, vals)
    print(f"  {state}: rho={rho:+.4f}, p={p:.4f}, n={len(valid)}")

    # Section-controlled
    sections = [m['section'] for m in folio_metrics if m['state_run_lengths'][state] is not None]
    x_r, y_r = section_residualize(np.array(ranks, dtype=float), np.array(vals), sections)
    rho_s, p_s = stats.spearmanr(x_r, y_r)
    print(f"    section-controlled: rho={rho_s:+.4f}, p={p_s:.4f}")

    t1_per_state_spearman[state] = {
        'n': len(valid),
        'raw_rho': float(rho), 'raw_p': float(p),
        'section_controlled_rho': float(rho_s), 'section_controlled_p': float(p_s),
    }

# Geometric distribution test: are run lengths memoryless?
print("\nGeometric distribution test (AXM, largest sample):")
all_axm_runs = []
for folio, lines_dict in folio_lines.items():
    line_seqs = [v for v in lines_dict.values() if len(v) >= 2]
    state_runs = compute_run_lengths_by_state(line_seqs)
    all_axm_runs.extend(state_runs.get('AXM', []))

if all_axm_runs:
    observed_mean = np.mean(all_axm_runs)
    # Geometric with parameter p has mean 1/p
    p_geo = 1.0 / observed_mean
    # Compare observed distribution to geometric
    max_run = max(all_axm_runs)
    observed_hist = np.bincount(all_axm_runs, minlength=max_run + 1)[1:]  # skip 0
    expected_hist = np.array([p_geo * (1 - p_geo) ** (k - 1) for k in range(1, max_run + 1)]) * len(all_axm_runs)
    # Truncate to bins with expected >= 5, normalize expected to match observed
    mask = expected_hist >= 5
    if mask.sum() >= 3:
        obs_masked = observed_hist[mask]
        exp_masked = expected_hist[mask]
        exp_masked = exp_masked * (obs_masked.sum() / exp_masked.sum())  # normalize
        chi2, chi2_p = stats.chisquare(obs_masked, exp_masked)
        print(f"  AXM runs: n={len(all_axm_runs)}, mean={observed_mean:.3f}, p_geo={p_geo:.3f}")
        print(f"  Chi2 vs geometric: chi2={chi2:.2f}, p={chi2_p:.4f}")
        geo_test = {'mean': float(observed_mean), 'p_geo': float(p_geo),
                    'chi2': float(chi2), 'chi2_p': float(chi2_p),
                    'is_geometric': bool(chi2_p > 0.05)}
    else:
        print(f"  AXM runs: n={len(all_axm_runs)}, mean={observed_mean:.3f} (too few bins for chi2)")
        geo_test = {'mean': float(observed_mean), 'status': 'insufficient_bins'}
else:
    geo_test = {'status': 'no_data'}

t1_result = {
    'regime_state_means': t1_regime_state,
    'per_state_spearman': t1_per_state_spearman,
    'geometric_test_AXM': geo_test,
}

# ═══════════════════════════════════════════════════════════════════════════
# T2: DWELL VS HAZARD CLASS DENSITY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T2: DWELL VS HAZARD CLASS DENSITY")
print("=" * 70)

valid2 = [m for m in folio_metrics if m['overall_run_length'] is not None and m['hazard_density'] is not None]
dwell_vals = np.array([m['overall_run_length'] for m in valid2])
haz_vals = np.array([m['hazard_density'] for m in valid2])
sections2 = [m['section'] for m in valid2]

rho2, p2 = stats.spearmanr(dwell_vals, haz_vals)
print(f"  Raw Spearman (dwell vs hazard density): rho={rho2:+.4f}, p={p2:.4f}, n={len(valid2)}")

x_r2, y_r2 = section_residualize(dwell_vals, haz_vals, sections2)
rho2s, p2s = stats.spearmanr(x_r2, y_r2)
print(f"  Section-controlled: rho={rho2s:+.4f}, p={p2s:.4f}")

t2_result = {
    'n': len(valid2),
    'raw_rho': float(rho2), 'raw_p': float(p2),
    'section_controlled_rho': float(rho2s), 'section_controlled_p': float(p2s),
}

# ═══════════════════════════════════════════════════════════════════════════
# T3: DWELL VS ENERGY-DEPTH
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T3: DWELL VS ENERGY-DEPTH (SPECTRAL RADIAL DEPTH)")
print("=" * 70)

# Reconstruct MIDDLE list (same as t1_definitive_matrix.py)
all_middles_set = set()
for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        all_middles_set.add(m.middle)
all_middles = sorted(all_middles_set)
mid_to_idx = {m: i for i, m in enumerate(all_middles)}
print(f"  Reconstructed MIDDLE list: {len(all_middles)} MIDDLEs")

# Load compatibility matrix and compute spectral embedding
compat_path = 'phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_compat_matrix.npy'
compat = np.load(compat_path)
print(f"  Compatibility matrix: {compat.shape}")

# Compute eigenvectors (symmetric matrix)
eigenvalues, eigenvectors = np.linalg.eigh(compat.astype(float))
# Sort descending
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Remove hub eigenmode (C986: first eigenvalue is frequency gradient)
# Use dimensions 2-100 (skip first, which is frequency)
n_dims = min(100, len(eigenvalues) - 1)
residual_embedding = eigenvectors[:, 1:n_dims + 1] * np.sqrt(np.abs(eigenvalues[1:n_dims + 1]))

# Radial depth = L2 norm in residual embedding
radial_depth = np.linalg.norm(residual_embedding, axis=1)
middle_depth = {all_middles[i]: float(radial_depth[i]) for i in range(len(all_middles))}
print(f"  Radial depth computed for {len(middle_depth)} MIDDLEs")
print(f"  Depth range: {radial_depth.min():.3f} - {radial_depth.max():.3f}")

# Compute per-folio mean depth (using classified EN tokens' MIDDLEs)
for m in folio_metrics:
    folio = m['folio']
    lines_dict = folio_lines[folio]
    depths = []
    for line_toks in lines_dict.values():
        for tok in line_toks:
            mid = tok.get('middle')
            if mid and mid in middle_depth:
                depths.append(middle_depth[mid])
    m['mean_depth'] = float(np.mean(depths)) if depths else None

valid3 = [m for m in folio_metrics if m['overall_run_length'] is not None and m['mean_depth'] is not None]
dwell3 = np.array([m['overall_run_length'] for m in valid3])
depth3 = np.array([m['mean_depth'] for m in valid3])
sections3 = [m['section'] for m in valid3]

rho3, p3 = stats.spearmanr(dwell3, depth3)
print(f"\n  Raw Spearman (dwell vs depth): rho={rho3:+.4f}, p={p3:.4f}, n={len(valid3)}")

x_r3, y_r3 = section_residualize(dwell3, depth3, sections3)
rho3s, p3s = stats.spearmanr(x_r3, y_r3)
print(f"  Section-controlled: rho={rho3s:+.4f}, p={p3s:.4f}")

# Also: REGIME-controlled (does depth predict dwell beyond REGIME?)
regime3 = np.array([REGIME_RANK[m['regime']] for m in valid3], dtype=float)
DR = np.column_stack([
    np.array([{'B': 0, 'H': 1, 'S': 2}.get(s, 0) for s in sections3]) == 0,
    np.array([{'B': 0, 'H': 1, 'S': 2}.get(s, 0) for s in sections3]) == 1,
    np.array([{'B': 0, 'H': 1, 'S': 2}.get(s, 0) for s in sections3]) == 2,
    regime3,
]).astype(float)
cx3, _, _, _ = lstsq(DR, dwell3, rcond=None)
cy3, _, _, _ = lstsq(DR, depth3, rcond=None)
dwell3_r = dwell3 - DR @ cx3
depth3_r = depth3 - DR @ cy3
rho3sr, p3sr = stats.spearmanr(dwell3_r, depth3_r)
print(f"  Section+REGIME controlled: rho={rho3sr:+.4f}, p={p3sr:.4f}")

t3_result = {
    'n': len(valid3),
    'raw_rho': float(rho3), 'raw_p': float(p3),
    'section_controlled_rho': float(rho3s), 'section_controlled_p': float(p3s),
    'section_regime_controlled_rho': float(rho3sr), 'section_regime_controlled_p': float(p3sr),
    'depth_range': [float(radial_depth.min()), float(radial_depth.max())],
}

# ═══════════════════════════════════════════════════════════════════════════
# T4: HT DENSITY VS DWELL (COGNITIVE PACING)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T4: HT DENSITY VS DWELL (COGNITIVE PACING)")
print("=" * 70)

valid4 = [m for m in folio_metrics if m['overall_run_length'] is not None and m['body_ht_density'] is not None]
dwell4 = np.array([m['overall_run_length'] for m in valid4])
ht4 = np.array([m['body_ht_density'] for m in valid4])
sections4 = [m['section'] for m in valid4]

rho4, p4 = stats.spearmanr(dwell4, ht4)
print(f"  Raw Spearman (dwell vs body HT density): rho={rho4:+.4f}, p={p4:.4f}, n={len(valid4)}")

# Section control
x_r4, y_r4 = section_residualize(dwell4, ht4, sections4)
rho4s, p4s = stats.spearmanr(x_r4, y_r4)
print(f"  Section-controlled: rho={rho4s:+.4f}, p={p4s:.4f}")

# Multi-control: section + depth (proxy for tail_pressure C477)
depths4 = np.array([m.get('mean_depth', 0) or 0 for m in valid4])
sec_arr4 = np.array([{'B': 0, 'H': 1, 'S': 2}.get(s, 0) for s in sections4])
controls4 = np.column_stack([
    (sec_arr4 == 0).astype(float),
    (sec_arr4 == 1).astype(float),
    (sec_arr4 == 2).astype(float),
    depths4,  # proxy for tail_pressure / MIDDLE rarity
])
cx4, _, _, _ = lstsq(controls4, dwell4, rcond=None)
cy4, _, _, _ = lstsq(controls4, ht4, rcond=None)
dwell4_r = dwell4 - controls4 @ cx4
ht4_r = ht4 - controls4 @ cy4
rho4m, p4m = stats.spearmanr(dwell4_r, ht4_r)
print(f"  Multi-controlled (section + depth): rho={rho4m:+.4f}, p={p4m:.4f}")

# LINK density check (C665: stationary)
valid_link = [m for m in folio_metrics if m['overall_run_length'] is not None and m['link_density'] is not None]
if len(valid_link) > 10:
    dwell_l = np.array([m['overall_run_length'] for m in valid_link])
    link_l = np.array([m['link_density'] for m in valid_link])
    rho_link, p_link = stats.spearmanr(dwell_l, link_l)
    print(f"\n  LINK density vs dwell: rho={rho_link:+.4f}, p={p_link:.4f}")
    link_result = {'rho': float(rho_link), 'p': float(p_link)}
else:
    link_result = {'status': 'insufficient_data'}

t4_result = {
    'n': len(valid4),
    'raw_rho': float(rho4), 'raw_p': float(p4),
    'section_controlled_rho': float(rho4s), 'section_controlled_p': float(p4s),
    'multi_controlled_rho': float(rho4m), 'multi_controlled_p': float(p4m),
    'link_density_check': link_result,
}

# ═══════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE RUN EXTRACTION (T5-T8 shared infrastructure)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("COMPREHENSIVE RUN EXTRACTION FOR MEMORY ANALYSIS")
print("=" * 70)

EN_MACROS = {'AXm', 'AXM'}

# Build global sequences and extract detailed run information
all_macro_sequences = []   # list of lists of (macro, class_id, folio) per line
all_runs_detailed = []     # detailed run records

for folio, lines_dict in folio_lines.items():
    for line_key, tokens in sorted(lines_dict.items()):
        if len(tokens) < 2:
            continue

        macro_seq = [(t['macro'], t['class'], folio) for t in tokens]
        all_macro_sequences.append(macro_seq)

        # Extract runs with full detail
        current_state = tokens[0]['macro']
        current_classes = [tokens[0]['class']]
        prev_state = None

        for i in range(1, len(tokens)):
            if tokens[i]['macro'] == current_state:
                current_classes.append(tokens[i]['class'])
            else:
                all_runs_detailed.append({
                    'state': current_state,
                    'length': len(current_classes),
                    'folio': folio,
                    'classes': current_classes[:],
                    'next_state': tokens[i]['macro'],
                    'prev_state': prev_state,
                })
                prev_state = current_state
                current_state = tokens[i]['macro']
                current_classes = [tokens[i]['class']]

        # Last run in line (next_state = None = line end)
        all_runs_detailed.append({
            'state': current_state,
            'length': len(current_classes),
            'folio': folio,
            'classes': current_classes[:],
            'next_state': None,
            'prev_state': prev_state,
        })

# Build 6x6 transition matrix
macro_idx = {s: i for i, s in enumerate(MACRO_NAMES)}
trans_6x6 = np.zeros((6, 6))
for seq in all_macro_sequences:
    for i in range(len(seq) - 1):
        s_from = macro_idx[seq[i][0]]
        s_to = macro_idx[seq[i + 1][0]]
        trans_6x6[s_from][s_to] += 1

# Row-normalize to transition probabilities
row_sums_6 = trans_6x6.sum(axis=1, keepdims=True)
row_sums_6[row_sums_6 == 0] = 1
trans_6x6_prob = trans_6x6 / row_sums_6

# Compute stationary distribution
evals_stat, evecs_stat = np.linalg.eig(trans_6x6_prob.T)
stat_idx = np.argmin(np.abs(evals_stat - 1.0))
stationary = np.abs(evecs_stat[:, stat_idx].real)
stationary /= stationary.sum()

# Collect global runs per state
global_state_runs = defaultdict(list)
for r in all_runs_detailed:
    global_state_runs[r['state']].append(r['length'])

# Line lengths for matched simulation
real_line_lengths = [len(seq) for seq in all_macro_sequences]

print(f"Total runs extracted: {len(all_runs_detailed)}")
print(f"Total lines: {len(all_macro_sequences)}")
print(f"6x6 self-transition (AXM): {trans_6x6_prob[macro_idx['AXM'], macro_idx['AXM']]:.4f}")
print(f"Stationary dist: { {s: f'{stationary[i]:.4f}' for s, i in macro_idx.items()} }")
for s in MACRO_NAMES:
    runs = global_state_runs[s]
    print(f"  {s}: {len(runs)} runs, mean={np.mean(runs):.3f}" if runs else f"  {s}: 0 runs")


# ── Hazard function helper ────────────────────────────────────────────────

def compute_hazard_function(run_lengths, max_t=None, min_at_risk=10):
    """Discrete hazard h(t) = d(t) / n(t). Returns (h_vals, n_at_risk) for t=1..max_t."""
    if not run_lengths:
        return [], []
    runs = np.array(run_lengths)
    if max_t is None:
        max_t = min(int(runs.max()), 25)

    h_vals = []
    n_vals = []
    for t in range(1, max_t + 1):
        n_t = int(np.sum(runs >= t))
        d_t = int(np.sum(runs == t))
        n_vals.append(n_t)
        h_vals.append(float(d_t / n_t) if n_t >= min_at_risk else None)

    return h_vals, n_vals


def classify_hazard_trend(h_vals):
    """Classify hazard shape: constant, decreasing, increasing."""
    valid = [(t + 1, v) for t, v in enumerate(h_vals) if v is not None]
    if len(valid) < 4:
        return 'insufficient_data', None, None
    ts, vs = zip(*valid)
    rho, p = stats.spearmanr(ts, vs)
    if p > 0.1:
        return 'constant (memoryless)', float(rho), float(p)
    elif rho < 0:
        return 'decreasing (momentum/inertia)', float(rho), float(p)
    else:
        return 'increasing (fatigue/deadline)', float(rho), float(p)


# ═══════════════════════════════════════════════════════════════════════════
# T5: EMPIRICAL HAZARD FUNCTION (3 resolution levels)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T5: EMPIRICAL HAZARD FUNCTION")
print("=" * 70)

# Level 1: 6-state macro level (AXM runs)
axm_runs_global = global_state_runs['AXM']
h_axm_6state, n_axm_6state = compute_hazard_function(axm_runs_global)
shape_6state, shape_6state_rho, shape_6state_p = classify_hazard_trend(h_axm_6state)
print(f"\n  Level 1 (6-state, AXM): n_runs={len(axm_runs_global)}, mean={np.mean(axm_runs_global):.3f}")
print(f"  Hazard h(t) for t=1..10: {[f'{v:.3f}' if v else 'N/A' for v in h_axm_6state[:10]]}")
print(f"  Hazard shape: {shape_6state} (rho={shape_6state_rho}, p={shape_6state_p})")

# Level 2: 49-class level - run lengths within individual classes
class_runs_global = defaultdict(list)
for seq in all_macro_sequences:
    if len(seq) < 2:
        continue
    current_cls = seq[0][1]
    current_run = 1
    for i in range(1, len(seq)):
        if seq[i][1] == current_cls:
            current_run += 1
        else:
            class_runs_global[current_cls].append(current_run)
            current_cls = seq[i][1]
            current_run = 1
    class_runs_global[current_cls].append(current_run)

# Pool runs from AXM classes
axm_class_ids = sorted(MACRO_PARTITION['AXM'])
axm_runs_49class = []
for cls_id in axm_class_ids:
    axm_runs_49class.extend(class_runs_global.get(cls_id, []))

h_axm_49class, n_axm_49class = compute_hazard_function(axm_runs_49class)
shape_49class, shape_49class_rho, shape_49class_p = classify_hazard_trend(h_axm_49class)
print(f"\n  Level 2 (49-class, AXM classes pooled): n_runs={len(axm_runs_49class)}, "
      f"mean={np.mean(axm_runs_49class):.3f}" if axm_runs_49class else "  Level 2: no data")
print(f"  Hazard h(t) for t=1..10: {[f'{v:.3f}' if v else 'N/A' for v in h_axm_49class[:10]]}")
print(f"  Hazard shape: {shape_49class}")

# Level 3: EN-only (binary: EN vs non-EN)
en_runs_global = []
for seq in all_macro_sequences:
    if len(seq) < 2:
        continue
    current_en = seq[0][0] in EN_MACROS
    current_run = 1
    for i in range(1, len(seq)):
        is_en = seq[i][0] in EN_MACROS
        if is_en == current_en:
            current_run += 1
        else:
            if current_en:
                en_runs_global.append(current_run)
            current_en = is_en
            current_run = 1
    if current_en:
        en_runs_global.append(current_run)

h_en, n_en = compute_hazard_function(en_runs_global)
shape_en, shape_en_rho, shape_en_p = classify_hazard_trend(h_en)
print(f"\n  Level 3 (EN-only binary): n_runs={len(en_runs_global)}, "
      f"mean={np.mean(en_runs_global):.3f}" if en_runs_global else "  Level 3: no data")
print(f"  Hazard h(t) for t=1..10: {[f'{v:.3f}' if v else 'N/A' for v in h_en[:10]]}")
print(f"  Hazard shape: {shape_en}")

# Key comparison: if 49-class is geometric but 6-state is not -> aggregation artifact
print(f"\n  RESOLUTION COMPARISON:")
print(f"    6-state AXM:  {shape_6state}")
print(f"    49-class AXM: {shape_49class}")
print(f"    EN-only:      {shape_en}")

t5_result = {
    'level_6state_AXM': {
        'n_runs': len(axm_runs_global),
        'mean_run': float(np.mean(axm_runs_global)),
        'hazard': [float(v) if v is not None else None for v in h_axm_6state],
        'n_at_risk': [int(v) for v in n_axm_6state],
        'shape': shape_6state,
        'shape_rho': shape_6state_rho,
        'shape_p': shape_6state_p,
    },
    'level_49class_AXM': {
        'n_runs': len(axm_runs_49class),
        'mean_run': float(np.mean(axm_runs_49class)) if axm_runs_49class else None,
        'hazard': [float(v) if v is not None else None for v in h_axm_49class],
        'n_at_risk': [int(v) for v in n_axm_49class],
        'shape': shape_49class,
        'shape_rho': shape_49class_rho,
        'shape_p': shape_49class_p,
    },
    'level_EN_only': {
        'n_runs': len(en_runs_global),
        'mean_run': float(np.mean(en_runs_global)) if en_runs_global else None,
        'hazard': [float(v) if v is not None else None for v in h_en],
        'n_at_risk': [int(v) for v in n_en],
        'shape': shape_en,
        'shape_rho': shape_en_rho,
        'shape_p': shape_en_p,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# T5b: FIRST-ORDER MARKOV NULL MODEL (100 simulations)
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T5b: FIRST-ORDER MARKOV NULL MODEL (100 simulations)")
print("=" * 70)

N_SIMS = 100
np.random.seed(42)

# Simulate line-matched Markov chains
sim_axm_runs_per_sim = []  # list of run-length lists, one per simulation
total_sim_tokens = sum(real_line_lengths)

for sim_i in range(N_SIMS):
    sim_state_runs = defaultdict(list)
    for line_len in real_line_lengths:
        if line_len < 2:
            continue
        # Start from stationary distribution
        state = np.random.choice(6, p=stationary)
        current_run = 1

        for step in range(line_len - 1):
            next_state = np.random.choice(6, p=trans_6x6_prob[state])
            if next_state == state:
                current_run += 1
            else:
                sim_state_runs[state].append(current_run)
                state = next_state
                current_run = 1
        sim_state_runs[state].append(current_run)

    axm_idx = macro_idx['AXM']
    sim_axm_runs_per_sim.append(sim_state_runs.get(axm_idx, []))

# 2-sample KS test: empirical vs pooled simulated
sim_pooled = []
for runs in sim_axm_runs_per_sim:
    sim_pooled.extend(runs)

ks_stat, ks_p = stats.ks_2samp(axm_runs_global, sim_pooled)
print(f"  KS test (empirical vs pooled simulated): D={ks_stat:.4f}, p={ks_p:.4f}")

# Simulated hazard envelope (95% CI)
max_t_sim = 20
sim_hazards = np.full((N_SIMS, max_t_sim), np.nan)
for sim_i, runs in enumerate(sim_axm_runs_per_sim):
    if not runs:
        continue
    h_sim, _ = compute_hazard_function(runs, max_t=max_t_sim)
    for t in range(min(len(h_sim), max_t_sim)):
        if h_sim[t] is not None:
            sim_hazards[sim_i, t] = h_sim[t]

sim_h_mean = np.nanmean(sim_hazards, axis=0)
sim_h_lo = np.nanpercentile(sim_hazards, 2.5, axis=0)
sim_h_hi = np.nanpercentile(sim_hazards, 97.5, axis=0)

# Check: does empirical h(t) fall within 95% CI?
empirical_outside = 0
empirical_total = 0
for t in range(min(len(h_axm_6state), max_t_sim)):
    if h_axm_6state[t] is not None and not np.isnan(sim_h_lo[t]):
        empirical_total += 1
        if h_axm_6state[t] < sim_h_lo[t] or h_axm_6state[t] > sim_h_hi[t]:
            empirical_outside += 1

outside_frac = empirical_outside / empirical_total if empirical_total > 0 else None
if outside_frac is not None:
    print(f"  Empirical points outside 95% CI: {empirical_outside}/{empirical_total} ({outside_frac:.1%})")
else:
    print("  Insufficient data for CI comparison")

# Mean comparison
sim_means = [float(np.mean(runs)) for runs in sim_axm_runs_per_sim if runs]
emp_mean = float(np.mean(axm_runs_global))
print(f"  Empirical mean AXM run: {emp_mean:.3f}")
if sim_means:
    print(f"  Simulated mean AXM run: {np.mean(sim_means):.3f} "
          f"(95% CI: {np.percentile(sim_means, 2.5):.3f}-{np.percentile(sim_means, 97.5):.3f})")

# Per-simulation KS tests (distribution of KS statistics)
per_sim_ks = []
for runs in sim_axm_runs_per_sim:
    if len(runs) >= 20:
        ks_s, _ = stats.ks_2samp(axm_runs_global, runs)
        per_sim_ks.append(ks_s)

# Also: run chi-squared geometric test on pooled simulated (should ALSO be non-geometric
# if topology produces phase-type distribution)
if sim_pooled:
    sim_mean = np.mean(sim_pooled)
    sim_p_geo = 1.0 / sim_mean
    sim_max = max(sim_pooled)
    sim_obs = np.bincount(sim_pooled, minlength=sim_max + 1)[1:]
    sim_exp = np.array([sim_p_geo * (1 - sim_p_geo) ** (k - 1)
                        for k in range(1, sim_max + 1)]) * len(sim_pooled)
    sim_mask = sim_exp >= 5
    if sim_mask.sum() >= 3:
        sim_obs_m = sim_obs[sim_mask]
        sim_exp_m = sim_exp[sim_mask]
        sim_exp_m = sim_exp_m * (sim_obs_m.sum() / sim_exp_m.sum())
        sim_chi2, sim_chi2_p = stats.chisquare(sim_obs_m, sim_exp_m)
        print(f"\n  Simulated pooled geometric test: chi2={sim_chi2:.2f}, p={sim_chi2_p:.4f}")
        print(f"  (If simulated is ALSO non-geometric -> topology produces phase-type distribution)")
        sim_geo_test = {'chi2': float(sim_chi2), 'p': float(sim_chi2_p),
                        'is_geometric': bool(sim_chi2_p > 0.05)}
    else:
        sim_geo_test = {'status': 'insufficient_bins'}
else:
    sim_geo_test = {'status': 'no_data'}

# VERDICT
null_reproduces = ks_p > 0.05
print(f"\n  VERDICT: First-order null {'REPRODUCES' if null_reproduces else 'FAILS to reproduce'} "
      f"empirical AXM dwell (KS p={ks_p:.4f})")
if null_reproduces:
    print("  -> Non-geometric dwell is likely a TOPOLOGY ARTIFACT of 6-state compression")
    print("  -> Phase-type distribution from 32-class aggregation explains apparent memory")
else:
    print("  -> Persistence memory EXISTS beyond first-order transitions")
    print("  -> Proceed to T6b/T7 for characterization")

t5b_result = {
    'n_simulations': N_SIMS,
    'ks_statistic': float(ks_stat),
    'ks_p': float(ks_p),
    'null_reproduces': bool(null_reproduces),
    'empirical_mean': emp_mean,
    'simulated_mean': float(np.mean(sim_means)) if sim_means else None,
    'simulated_mean_95ci': ([float(np.percentile(sim_means, 2.5)),
                             float(np.percentile(sim_means, 97.5))] if sim_means else None),
    'hazard_outside_95ci': f"{empirical_outside}/{empirical_total}",
    'outside_fraction': float(outside_frac) if outside_frac is not None else None,
    'sim_hazard_mean': [float(v) if not np.isnan(v) else None for v in sim_h_mean],
    'sim_hazard_95ci_lo': [float(v) if not np.isnan(v) else None for v in sim_h_lo],
    'sim_hazard_95ci_hi': [float(v) if not np.isnan(v) else None for v in sim_h_hi],
    'sim_geometric_test': sim_geo_test,
    'verdict': 'TOPOLOGY_ARTIFACT' if null_reproduces else 'GENUINE_MEMORY',
}


# ═══════════════════════════════════════════════════════════════════════════
# T6: ALL-STATE GEOMETRIC TEST
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T6: ALL-STATE GEOMETRIC TEST")
print("=" * 70)

t6_results = {}
for state in MACRO_NAMES:
    runs = global_state_runs.get(state, [])
    if len(runs) < 30:
        t6_results[state] = {'n': len(runs), 'status': 'insufficient'}
        print(f"  {state}: n={len(runs)} (insufficient)")
        continue

    obs_mean = np.mean(runs)
    p_geo = 1.0 / obs_mean
    max_run = max(runs)
    observed_hist = np.bincount(runs, minlength=max_run + 1)[1:]
    expected_hist = np.array([p_geo * (1 - p_geo) ** (k - 1)
                              for k in range(1, max_run + 1)]) * len(runs)

    mask = expected_hist >= 5
    if mask.sum() >= 3:
        obs_m = observed_hist[mask]
        exp_m = expected_hist[mask]
        exp_m = exp_m * (obs_m.sum() / exp_m.sum())
        chi2_s, chi2_p_s = stats.chisquare(obs_m, exp_m)
        is_geo = bool(chi2_p_s > 0.05)
        t6_results[state] = {
            'n': len(runs), 'mean': float(obs_mean), 'p_geo': float(p_geo),
            'chi2': float(chi2_s), 'p': float(chi2_p_s), 'is_geometric': is_geo,
        }
        label = 'GEOMETRIC' if is_geo else 'NON-GEOMETRIC'
        print(f"  {state}: n={len(runs)}, mean={obs_mean:.3f}, chi2={chi2_s:.2f}, "
              f"p={chi2_p_s:.4f} {label}")
    else:
        t6_results[state] = {'n': len(runs), 'mean': float(obs_mean), 'status': 'insufficient_bins'}
        print(f"  {state}: n={len(runs)}, mean={obs_mean:.3f} (insufficient bins for chi2)")

non_geo_states = [s for s, v in t6_results.items() if v.get('is_geometric') is False]
geo_states = [s for s, v in t6_results.items() if v.get('is_geometric') is True]
print(f"\n  Non-geometric states: {non_geo_states or 'NONE'}")
print(f"  Geometric states: {geo_states or 'NONE'}")
if non_geo_states == ['AXM']:
    print("  -> Memory is AXM-specific (execution mass inertia)")
elif len(non_geo_states) > 1:
    print(f"  -> Memory is distributed across {len(non_geo_states)} states (global property)")
elif not non_geo_states:
    print("  -> All states are geometric (no memory at any state)")


# ═══════════════════════════════════════════════════════════════════════════
# T6b: WITHIN-AXM COMPOSITIONAL DRIFT
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T6b: WITHIN-AXM COMPOSITIONAL DRIFT (early-run vs late-run)")
print("=" * 70)

MIN_RUN_FOR_DRIFT = 6
long_axm_runs = [r for r in all_runs_detailed
                 if r['state'] == 'AXM' and r['length'] >= MIN_RUN_FOR_DRIFT]

early_class_counts = defaultdict(int)
late_class_counts = defaultdict(int)

for r in long_axm_runs:
    mid_pt = len(r['classes']) // 2
    for c in r['classes'][:mid_pt]:
        early_class_counts[c] += 1
    for c in r['classes'][mid_pt:]:
        late_class_counts[c] += 1

# Build aligned count vectors over all observed AXM classes
all_observed_cls = sorted(set(early_class_counts.keys()) | set(late_class_counts.keys()))
early_vec = np.array([early_class_counts.get(c, 0) for c in all_observed_cls])
late_vec = np.array([late_class_counts.get(c, 0) for c in all_observed_cls])

# Remove classes with 0 in both halves
nonzero_drift = (early_vec + late_vec) > 0
early_nz = early_vec[nonzero_drift]
late_nz = late_vec[nonzero_drift]

print(f"  Long AXM runs (len >= {MIN_RUN_FOR_DRIFT}): n={len(long_axm_runs)}")
print(f"  Early-half tokens: {early_nz.sum()}, Late-half tokens: {late_nz.sum()}")

if early_nz.sum() >= 50 and late_nz.sum() >= 50:
    contingency_drift = np.array([early_nz, late_nz])
    chi2_drift, p_drift, dof_drift, _ = stats.chi2_contingency(contingency_drift)

    def shannon_entropy(counts):
        p = counts / counts.sum()
        p = p[p > 0]
        return float(-np.sum(p * np.log2(p)))

    early_H = shannon_entropy(early_nz)
    late_H = shannon_entropy(late_nz)
    drift_detected = bool(p_drift < 0.05)

    print(f"  Early-half entropy: {early_H:.3f} bits, Late-half entropy: {late_H:.3f} bits")
    print(f"  Chi2 homogeneity: chi2={chi2_drift:.2f}, p={p_drift:.4f}, dof={dof_drift}")
    print(f"  Compositional drift: {'DETECTED' if drift_detected else 'NOT DETECTED'}")
    if drift_detected:
        print("  -> Memory may be compositional heterogeneity within AXM (C977 internal structure)")
    else:
        print("  -> Class composition is stable within runs (genuine temporal persistence)")

    t6b_result = {
        'n_long_runs': len(long_axm_runs),
        'min_run_length': MIN_RUN_FOR_DRIFT,
        'early_entropy': early_H,
        'late_entropy': late_H,
        'chi2': float(chi2_drift),
        'p': float(p_drift),
        'dof': int(dof_drift),
        'drift_detected': drift_detected,
    }
else:
    print("  Insufficient data for drift analysis")
    t6b_result = {'n_long_runs': len(long_axm_runs), 'status': 'insufficient_data'}


# ═══════════════════════════════════════════════════════════════════════════
# T7: WEIBULL SHAPE PARAMETER x REGIME
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T7: WEIBULL SHAPE PARAMETER x REGIME")
print("=" * 70)

# Global Weibull fit on all AXM runs
all_axm_arr = np.array(axm_runs_global, dtype=float)
try:
    global_k, global_loc, global_lam = stats.weibull_min.fit(all_axm_arr, floc=0)
    print(f"  Global AXM Weibull: k={global_k:.3f}, lambda={global_lam:.3f} (n={len(all_axm_arr)})")
    if abs(global_k - 1.0) < 0.15:
        print(f"  -> k ~ 1.0: approximately memoryless")
    elif global_k < 1.0:
        print(f"  -> k < 1: decreasing hazard (inertia/momentum)")
    else:
        print(f"  -> k > 1: increasing hazard (deadline/fatigue)")
    global_weibull = {'k': float(global_k), 'lambda': float(global_lam), 'n': len(all_axm_arr)}
except Exception as e:
    print(f"  Global Weibull fit failed: {e}")
    global_weibull = {'status': f'fit_failed: {e}'}

# Per-REGIME Weibull
t7_per_regime = {}
regime_k_vals = []
print()
for regime in REGIME_ORDER:
    regime_folios = {f for f, r in regime_map.items() if r == regime}
    regime_runs = [r['length'] for r in all_runs_detailed
                   if r['state'] == 'AXM' and r['folio'] in regime_folios]

    if len(regime_runs) < 30:
        t7_per_regime[regime] = {'n': len(regime_runs), 'status': 'insufficient'}
        print(f"  {regime}: n={len(regime_runs)} (insufficient)")
        continue

    runs_arr = np.array(regime_runs, dtype=float)
    try:
        k_r, loc_r, lam_r = stats.weibull_min.fit(runs_arr, floc=0)
        interp = ('memoryless' if abs(k_r - 1.0) < 0.15
                  else ('inertia' if k_r < 1.0 else 'deadline'))
        t7_per_regime[regime] = {
            'n': len(regime_runs), 'mean': float(runs_arr.mean()),
            'weibull_k': float(k_r), 'weibull_lambda': float(lam_r),
            'interpretation': interp,
        }
        regime_k_vals.append(float(k_r))
        print(f"  {regime}: n={len(regime_runs)}, mean={runs_arr.mean():.3f}, "
              f"k={k_r:.3f}, lambda={lam_r:.3f} -> {interp}")
    except Exception as e:
        t7_per_regime[regime] = {'n': len(regime_runs), 'status': f'fit_failed: {e}'}
        print(f"  {regime}: fit failed ({e})")

# Does k vary by REGIME?
t7_regime_test = {}
if len(regime_k_vals) == 4:
    k_range = max(regime_k_vals) - min(regime_k_vals)
    k_mean = np.mean(regime_k_vals)
    # Spearman: does k correlate with REGIME intensity?
    rho_k, p_k = stats.spearmanr(list(range(4)), regime_k_vals)
    print(f"\n  Weibull k range: {k_range:.3f} (mean {k_mean:.3f})")
    print(f"  k values (R2,R1,R4,R3): {[f'{v:.3f}' for v in regime_k_vals]}")
    print(f"  Spearman(REGIME rank, k): rho={rho_k:+.3f}, p={p_k:.3f}")
    if p_k < 0.05:
        print("  -> REGIME modulates memory SHAPE (architectural)")
    else:
        print("  -> REGIME does not modulate shape (scale-only or no effect)")

    t7_regime_test = {
        'k_range': float(k_range), 'k_mean': float(k_mean),
        'k_values': regime_k_vals,
        'regime_k_rho': float(rho_k), 'regime_k_p': float(p_k),
        'regime_modulates_shape': bool(p_k < 0.05),
    }

t7_result = {
    'global_weibull': global_weibull,
    'per_regime': t7_per_regime,
    'regime_shape_test': t7_regime_test,
}


# ═══════════════════════════════════════════════════════════════════════════
# T8: AXM EXIT TRIGGER ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("T8: AXM EXIT TRIGGER ANALYSIS")
print("=" * 70)

# Exit skyline: which state does AXM exit to?
exit_to_counts = defaultdict(int)
exit_total = 0
for r in all_runs_detailed:
    if r['state'] == 'AXM' and r['next_state'] is not None:
        exit_to_counts[r['next_state']] += 1
        exit_total += 1

print(f"\n  AXM exit skyline (n={exit_total}):")
for state in MACRO_NAMES:
    if state == 'AXM':
        continue
    n_exit = exit_to_counts.get(state, 0)
    frac = n_exit / exit_total if exit_total > 0 else 0
    print(f"    -> {state}: {n_exit} ({frac:.1%})")

# Entry skyline: which state enters AXM?
entry_from_counts = defaultdict(int)
entry_total = 0
for r in all_runs_detailed:
    if r['state'] == 'AXM' and r['prev_state'] is not None:
        entry_from_counts[r['prev_state']] += 1
        entry_total += 1

print(f"\n  AXM entry skyline (n={entry_total}):")
for state in MACRO_NAMES:
    if state == 'AXM':
        continue
    n_entry = entry_from_counts.get(state, 0)
    frac = n_entry / entry_total if entry_total > 0 else 0
    print(f"    <- {state}: {n_entry} ({frac:.1%})")

# Boundary class enrichment: last class in AXM run vs mid-run classes
boundary_last_counts = defaultdict(int)
midrun_class_counts = defaultdict(int)
boundary_last_total = 0
midrun_class_total = 0

for r in all_runs_detailed:
    if r['state'] == 'AXM' and r['length'] >= 3:
        boundary_last_counts[r['classes'][-1]] += 1
        boundary_last_total += 1
        for c in r['classes'][1:-1]:
            midrun_class_counts[c] += 1
            midrun_class_total += 1

# Compute enrichment ratios
all_cls_exit = sorted(set(boundary_last_counts.keys()) | set(midrun_class_counts.keys()))
exit_enrichment = {}
for c in all_cls_exit:
    b_frac = boundary_last_counts[c] / boundary_last_total if boundary_last_total > 0 else 0
    m_frac = midrun_class_counts[c] / midrun_class_total if midrun_class_total > 0 else 0
    if m_frac > 0:
        enrichment = b_frac / m_frac
    else:
        enrichment = 999.0 if b_frac > 0 else 1.0
    exit_enrichment[c] = {'boundary_frac': float(b_frac), 'midrun_frac': float(m_frac),
                          'enrichment': float(enrichment)}

sorted_enriched = sorted([(c, d['enrichment']) for c, d in exit_enrichment.items()],
                         key=lambda x: x[1], reverse=True)
print(f"\n  Exit-boundary enriched classes (top 5 of {len(sorted_enriched)}):")
for cls, enr in sorted_enriched[:5]:
    bf = exit_enrichment[cls]['boundary_frac']
    mf = exit_enrichment[cls]['midrun_frac']
    print(f"    Class {cls}: {enr:.2f}x enriched (boundary={bf:.3f}, midrun={mf:.3f})")

# Chi-squared: is exit-boundary distribution different from mid-run?
exit_vec = np.array([boundary_last_counts.get(c, 0) for c in all_cls_exit])
mid_vec = np.array([midrun_class_counts.get(c, 0) for c in all_cls_exit])
nonzero_exit = (exit_vec + mid_vec) > 0

if nonzero_exit.sum() >= 5:
    cont_exit = np.array([exit_vec[nonzero_exit], mid_vec[nonzero_exit]])
    chi2_exit, p_exit, dof_exit, _ = stats.chi2_contingency(cont_exit)
    gatekeeper_detected = bool(p_exit < 0.05)
    print(f"\n  Chi2 (exit-boundary vs mid-run): chi2={chi2_exit:.2f}, p={p_exit:.4f}")
    if gatekeeper_detected:
        print("  -> GATEKEEPER SUBSET detected: specific classes trigger AXM exit")
    else:
        print("  -> No gatekeeper: exit-boundary classes are representative of mid-run")
else:
    chi2_exit, p_exit, dof_exit = None, None, None
    gatekeeper_detected = False

t8_result = {
    'exit_skyline': {state: int(exit_to_counts.get(state, 0))
                     for state in MACRO_NAMES if state != 'AXM'},
    'exit_total': exit_total,
    'exit_fractions': {state: float(exit_to_counts.get(state, 0) / exit_total)
                       if exit_total > 0 else 0.0
                       for state in MACRO_NAMES if state != 'AXM'},
    'entry_skyline': {state: int(entry_from_counts.get(state, 0))
                      for state in MACRO_NAMES if state != 'AXM'},
    'entry_total': entry_total,
    'boundary_vs_midrun_chi2': float(chi2_exit) if chi2_exit is not None else None,
    'boundary_vs_midrun_p': float(p_exit) if p_exit is not None else None,
    'gatekeeper_detected': gatekeeper_detected,
    'top_exit_enriched': [{'class': int(c), 'enrichment': float(e)}
                          for c, e in sorted_enriched[:10]],
}


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

findings = []

# T1 summary
sig_states = [s for s, v in t1_per_state_spearman.items()
              if isinstance(v, dict) and 'section_controlled_p' in v and v['section_controlled_p'] < 0.05]
print(f"\nT1: States with REGIME-dependent dwell (p<0.05): {sig_states or 'NONE'}")
if sig_states:
    findings.append(f"REGIME selectively modulates dwell in: {', '.join(sig_states)}")
else:
    findings.append("REGIME does not selectively modulate dwell in any macro-state after section control")

# T2 summary
print(f"T2: Dwell vs hazard density: section-ctrl rho={rho2s:+.3f} p={p2s:.3f}")
if p2s < 0.05:
    findings.append(f"Dwell correlates with hazard density (rho={rho2s:+.3f})")
else:
    findings.append("No independent dwell-hazard relationship")

# T3 summary
print(f"T3: Dwell vs depth: section-ctrl rho={rho3s:+.3f} p={p3s:.3f}")
if p3s < 0.05:
    findings.append(f"Depth predicts dwell (rho={rho3s:+.3f})")
else:
    findings.append("No independent dwell-depth relationship")

# T4 summary
print(f"T4: HT density vs dwell: multi-ctrl rho={rho4m:+.3f} p={p4m:.3f}")
if p4m < 0.05:
    findings.append(f"HT density independently predicts dwell (rho={rho4m:+.3f})")
else:
    findings.append("HT density does not independently predict dwell")

# T5 summary
print(f"\nT5: Hazard shape -- 6-state: {shape_6state}, 49-class: {shape_49class}, EN-only: {shape_en}")
findings.append(f"Hazard shape at 6-state level: {shape_6state}")

# T5b summary (DECISION GATE)
print(f"T5b: First-order null {'REPRODUCES' if null_reproduces else 'FAILS'} (KS p={ks_p:.4f})")
if null_reproduces:
    findings.append(f"NON-GEOMETRIC DWELL IS TOPOLOGY ARTIFACT (KS p={ks_p:.4f})")
else:
    findings.append(f"GENUINE PERSISTENCE MEMORY beyond first-order transitions (KS p={ks_p:.4f})")

# T6 summary
print(f"T6: Non-geometric states: {non_geo_states}, Geometric: {geo_states}")
findings.append(f"Non-geometric states: {non_geo_states or 'NONE'}")

# T6b summary
drift_flag = t6b_result.get('drift_detected')
if drift_flag is not None:
    print(f"T6b: Compositional drift {'DETECTED' if drift_flag else 'NOT DETECTED'} (p={t6b_result.get('p', 'N/A')})")
    if drift_flag:
        findings.append("Compositional drift within AXM runs (C977 internal structure)")
    else:
        findings.append("No compositional drift -- class composition stable within AXM runs")
else:
    print("T6b: Insufficient data")

# T7 summary
global_k_val = global_weibull.get('k')
if global_k_val:
    print(f"T7: Global Weibull k={global_k_val:.3f}, REGIME modulates shape: "
          f"{t7_regime_test.get('regime_modulates_shape', 'N/A')}")
    findings.append(f"Global Weibull k={global_k_val:.3f} "
                    f"({'memoryless' if abs(global_k_val - 1.0) < 0.15 else 'non-memoryless'})")
    if t7_regime_test.get('regime_modulates_shape'):
        findings.append("REGIME modulates memory shape parameter (architectural)")

# T8 summary
print(f"T8: Gatekeeper detected: {gatekeeper_detected}")
if gatekeeper_detected:
    top_gate = sorted_enriched[0] if sorted_enriched else None
    findings.append(f"Gatekeeper subset detected in AXM exit boundary (top enriched: class {top_gate[0]})")
else:
    findings.append("No gatekeeper subset -- AXM exit boundary is representative of mid-run")

print(f"\nTotal findings: {len(findings)}")
for fi, f in enumerate(findings, 1):
    print(f"  {fi}. {f}")

# ── Save results ──────────────────────────────────────────────────────────

results = {
    'phase': 'REGIME_DWELL_ARCHITECTURE',
    'n_folios': len(folio_metrics),
    'total_classified_tokens': total_classified,
    'mean_AXM_occupancy': float(axm_occ),
    'T1_dwell_geometry': t1_result,
    'T2_hazard_proximity': t2_result,
    'T3_energy_depth': t3_result,
    'T4_ht_cognitive_pacing': t4_result,
    'T5_hazard_function': t5_result,
    'T5b_null_model': t5b_result,
    'T6_all_state_geometric': t6_results,
    'T6b_compositional_drift': t6b_result,
    'T7_weibull_regime': t7_result,
    'T8_exit_triggers': t8_result,
    'findings': findings,
    'folio_details': [{k: v for k, v in m.items()} for m in folio_metrics],
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'dwell_architecture.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")

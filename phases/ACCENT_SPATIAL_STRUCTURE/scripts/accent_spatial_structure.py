#!/usr/bin/env python3
"""
Phase 482: ACCENT SPATIAL STRUCTURE
====================================
Tests whether the accent (M2.1 generative residual) has spatial/sequential
structure across the manuscript, or whether the folio_position signal
detected in C1368 PC2 is a section confound.

Gating test: Partial R² of folio_position beyond section for all 3 PCs.
  partial R² < 0.02 for all PCs → section confound
  partial R² >= 0.02 for PC2   → genuine spatial signal

Tests:
  T1: GATE — Position partial R² beyond section
  T2: Adjacent-folio accent similarity (within-section)
  T3: Within-quire clustering (Herbal, within-section)
  T4: Lag autocorrelation (within-section)
  T5: Section-boundary discontinuity
  T6: Archetype spatial clustering

Depends on: C1368, C1367, C1366, C1120, C968, C638, C367, C361
"""

import json
import sys
import math
import re
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from numpy.linalg import lstsq
from scipy.stats import pearsonr

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

SEED = 482
N_PERM = 1000


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def folio_sort_key(folio_id):
    """Sort key for physical folio ordering."""
    m = re.match(r'f(\d+)([rv]?)(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0 if m.group(2) == 'r' else 1
        sub = int(m.group(3)) if m.group(3) else 0
        return (num, side, sub)
    return (9999, 0, 0)


def folio_position(folio_id):
    """Numeric position for regression."""
    m = re.match(r'f(\d+)([rv]?)(\d*)', folio_id)
    if m:
        num = int(m.group(1))
        side = 0.0 if m.group(2) == 'r' else 0.5
        sub = int(m.group(3)) * 0.01 if m.group(3) else 0
        return num + side + sub
    return 9999.0


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load PC scores, section/regime/archetype metadata, quire assignments."""
    print("Loading data...")

    # Phase 480 results (for PC scores)
    with open(PROJECT / 'phases' / 'FOLIO_ACCENT_VECTOR' / 'results' /
              'folio_accent_vector.json', encoding='utf-8') as f:
        p480 = json.load(f)
    folio_scores = p480['T1_pca']['folio_scores']

    # Phase 479 results (for metadata)
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        p479 = json.load(f)
    per_folio_479 = p479['per_folio']

    # Unified folio profiles (for quire)
    with open(PROJECT / 'results' / 'unified_folio_profiles.json', encoding='utf-8') as f:
        profiles = json.load(f)

    # Build folio list sorted by manuscript order
    folios = sorted(folio_scores.keys(), key=folio_sort_key)
    print(f"  {len(folios)} folios")

    # Build per-folio data
    data = {}
    for folio in folios:
        fp = per_folio_479.get(folio, {})
        prof = profiles.get(folio, {})
        data[folio] = {
            'PC1': folio_scores[folio]['PC1'],
            'PC2': folio_scores[folio]['PC2'],
            'PC3': folio_scores[folio]['PC3'],
            'section': fp.get('section', 'UNK'),
            'regime': fp.get('regime', 'UNK'),
            'archetype': fp.get('archetype'),
            'quire': prof.get('quire') if isinstance(prof, dict) else None,
            'position': folio_position(folio),
        }

    return folios, data


# ── Test Functions ───────────────────────────────────────────────────

def test1_gate(folios, data):
    """T1: GATE — Partial R² of folio_position beyond section for each PC."""
    print("\n=== T1: GATE — Position Partial R² Beyond Section ===")

    n = len(folios)
    positions = np.array([data[f]['position'] for f in folios])

    # Section dummies
    sections = sorted(set(data[f]['section'] for f in folios))
    section_dummies = np.zeros((n, max(len(sections) - 1, 1)))
    section_map = {s: i for i, s in enumerate(sections)}
    for idx, f in enumerate(folios):
        s_idx = section_map[data[f]['section']]
        if s_idx > 0:
            section_dummies[idx, s_idx - 1] = 1.0

    results = {}
    gate_passed = False

    for pc in ['PC1', 'PC2', 'PC3']:
        y = np.array([data[f][pc] for f in folios])

        # Model 1: section only
        X_sect = np.column_stack([section_dummies, np.ones(n)])
        beta1, _, _, _ = lstsq(X_sect, y, rcond=None)
        ss_res_sect = np.sum((y - X_sect @ beta1) ** 2)

        # Model 2: section + position
        X_full = np.column_stack([section_dummies, positions, np.ones(n)])
        beta2, _, _, _ = lstsq(X_full, y, rcond=None)
        ss_res_full = np.sum((y - X_full @ beta2) ** 2)

        # Total SS
        ss_total = np.sum((y - np.mean(y)) ** 2)

        # R² values
        r2_sect = 1 - ss_res_sect / max(ss_total, 1e-10)
        r2_full = 1 - ss_res_full / max(ss_total, 1e-10)
        partial_r2 = r2_full - r2_sect

        # F-test for position term
        df_num = 1
        df_denom = n - X_full.shape[1]
        if df_denom > 0 and ss_res_full > 0:
            f_stat = ((ss_res_sect - ss_res_full) / df_num) / (ss_res_full / df_denom)
            from scipy.stats import f as f_dist
            p_val = 1 - f_dist.cdf(f_stat, df_num, df_denom)
        else:
            f_stat, p_val = 0.0, 1.0

        print(f"  {pc}: R²(sect)={r2_sect:.3f}, R²(sect+pos)={r2_full:.3f}, "
              f"partial_R²={partial_r2:.4f}, F={f_stat:.2f}, p={p_val:.4f}")

        results[pc] = {
            'r2_section_only': float(r2_sect),
            'r2_section_plus_position': float(r2_full),
            'partial_r2_position': float(partial_r2),
            'F': float(f_stat),
            'p': float(p_val),
        }

        if pc == 'PC2' and partial_r2 >= 0.02:
            gate_passed = True

    gate_decision = 'GENUINE_SPATIAL' if gate_passed else 'SECTION_CONFOUND'
    print(f"\n  GATE DECISION: {gate_decision}")
    results['gate_decision'] = gate_decision

    return results


def test2_adjacent_similarity(folios, data):
    """T2: Adjacent-folio accent similarity within section."""
    print("\n=== T2: Adjacent-Folio Accent Similarity (within-section) ===")

    rng = np.random.default_rng(SEED)

    # Group folios by section, sorted by manuscript order
    section_folios = defaultdict(list)
    for f in folios:
        section_folios[data[f]['section']].append(f)

    results = {}
    for section, sfolios in sorted(section_folios.items()):
        if len(sfolios) < 10:
            continue

        # Accent vectors (3-PC)
        vectors = np.array([[data[f]['PC1'], data[f]['PC2'], data[f]['PC3']] for f in sfolios])

        # Mean distance between adjacent pairs
        adj_dists = [np.linalg.norm(vectors[i+1] - vectors[i]) for i in range(len(sfolios) - 1)]
        observed_mean = np.mean(adj_dists)

        # Permutation null: shuffle order within section
        null_means = []
        for _ in range(N_PERM):
            perm = rng.permutation(len(sfolios))
            perm_vecs = vectors[perm]
            perm_dists = [np.linalg.norm(perm_vecs[i+1] - perm_vecs[i])
                          for i in range(len(sfolios) - 1)]
            null_means.append(np.mean(perm_dists))

        null_means = np.array(null_means)
        p_val = np.mean(null_means <= observed_mean)  # One-sided: is observed smaller?

        print(f"  Section {section} (n={len(sfolios)}): "
              f"observed={observed_mean:.3f}, null_mean={np.mean(null_means):.3f}, "
              f"p={p_val:.3f}")

        results[section] = {
            'n': len(sfolios),
            'observed_mean_dist': float(observed_mean),
            'null_mean_dist': float(np.mean(null_means)),
            'null_std': float(np.std(null_means)),
            'p': float(p_val),
            'significant': p_val < 0.05,
        }

    # Pooled test: combine across sections
    all_observed = []
    all_null = np.zeros(N_PERM)
    count = 0
    for section, r in results.items():
        if r['n'] >= 10:
            all_observed.append(r['observed_mean_dist'] * (r['n'] - 1))
            count += r['n'] - 1

    pooled_significant = any(r['significant'] for r in results.values())
    print(f"  Any section significant: {pooled_significant}")

    results['any_significant'] = pooled_significant
    return results


def test3_quire_clustering(folios, data):
    """T3: Within-quire clustering in Herbal section."""
    print("\n=== T3: Within-Quire Clustering (Herbal) ===")

    rng = np.random.default_rng(SEED + 1)

    # Herbal folios
    h_folios = [f for f in folios if data[f]['section'] == 'H']
    if len(h_folios) < 10:
        print("  Insufficient Herbal folios")
        return {'test_possible': False}

    vectors = np.array([[data[f]['PC1'], data[f]['PC2'], data[f]['PC3']] for f in h_folios])
    quires = [data[f]['quire'] for f in h_folios]

    # Compute within-quire vs between-quire distances
    within_dists = []
    between_dists = []
    for i, j in combinations(range(len(h_folios)), 2):
        d = float(np.linalg.norm(vectors[i] - vectors[j]))
        if quires[i] and quires[j] and quires[i] == quires[j]:
            within_dists.append(d)
        elif quires[i] and quires[j]:
            between_dists.append(d)

    if not within_dists or not between_dists:
        print("  Insufficient quire data for comparison")
        return {'test_possible': False}

    observed_ratio = np.mean(within_dists) / max(np.mean(between_dists), 1e-10)
    print(f"  Within-quire mean dist: {np.mean(within_dists):.3f} (n={len(within_dists)})")
    print(f"  Between-quire mean dist: {np.mean(between_dists):.3f} (n={len(between_dists)})")
    print(f"  Ratio (within/between): {observed_ratio:.3f}")

    # Permutation: shuffle quire labels within Herbal
    null_ratios = []
    for _ in range(N_PERM):
        perm_quires = rng.permutation(quires).tolist()
        w_dists = []
        b_dists = []
        for i, j in combinations(range(len(h_folios)), 2):
            d = float(np.linalg.norm(vectors[i] - vectors[j]))
            if perm_quires[i] and perm_quires[j] and perm_quires[i] == perm_quires[j]:
                w_dists.append(d)
            elif perm_quires[i] and perm_quires[j]:
                b_dists.append(d)
        if w_dists and b_dists:
            null_ratios.append(np.mean(w_dists) / max(np.mean(b_dists), 1e-10))

    if null_ratios:
        null_ratios = np.array(null_ratios)
        p_val = np.mean(null_ratios <= observed_ratio)  # Is observed smaller?
        print(f"  Permutation p={p_val:.3f} (null mean ratio={np.mean(null_ratios):.3f})")
    else:
        p_val = 1.0

    return {
        'test_possible': True,
        'n_herbal': len(h_folios),
        'within_quire_mean_dist': float(np.mean(within_dists)),
        'between_quire_mean_dist': float(np.mean(between_dists)),
        'observed_ratio': float(observed_ratio),
        'null_mean_ratio': float(np.mean(null_ratios)) if len(null_ratios) > 0 else None,
        'p': float(p_val),
        'significant': p_val < 0.05,
    }


def test4_autocorrelation(folios, data):
    """T4: Lag autocorrelation of PC scores within section."""
    print("\n=== T4: Lag Autocorrelation (within-section) ===")

    section_folios = defaultdict(list)
    for f in folios:
        section_folios[data[f]['section']].append(f)

    results = {}
    for section, sfolios in sorted(section_folios.items()):
        if len(sfolios) < 10:
            continue

        section_results = {}
        for pc in ['PC1', 'PC2', 'PC3']:
            vals = np.array([data[f][pc] for f in sfolios])
            lag_results = {}
            for lag in [1, 2, 3]:
                if len(vals) <= lag + 2:
                    continue
                x = vals[:-lag]
                y = vals[lag:]
                if np.std(x) > 1e-10 and np.std(y) > 1e-10:
                    r, p = pearsonr(x, y)
                else:
                    r, p = 0.0, 1.0
                lag_results[f'lag{lag}'] = {'r': float(r), 'p': float(p)}

            section_results[pc] = lag_results

        results[section] = section_results

        # Report lag-1 for each PC
        for pc in ['PC1', 'PC2', 'PC3']:
            l1 = section_results[pc].get('lag1', {})
            r_val = l1.get('r', 0)
            p_val = l1.get('p', 1)
            sig = '*' if p_val < 0.05 else ''
            print(f"  Section {section} {pc} lag-1: r={r_val:.3f}, p={p_val:.3f} {sig}")

    # Count significant lag-1 autocorrelations
    sig_count = sum(
        1 for section in results.values()
        for pc, lags in section.items()
        if 'lag1' in lags and lags['lag1']['p'] < 0.05
    )
    print(f"  Significant lag-1 autocorrelations: {sig_count}")

    results['significant_lag1_count'] = sig_count
    return results


def test5_boundary_discontinuity(folios, data):
    """T5: Section-boundary discontinuity test."""
    print("\n=== T5: Section-Boundary Discontinuity ===")

    # Find consecutive folio pairs
    within_section_dists = []
    boundary_dists = []

    for i in range(len(folios) - 1):
        f1, f2 = folios[i], folios[i + 1]
        v1 = np.array([data[f1]['PC1'], data[f1]['PC2'], data[f1]['PC3']])
        v2 = np.array([data[f2]['PC1'], data[f2]['PC2'], data[f2]['PC3']])
        dist = float(np.linalg.norm(v2 - v1))

        if data[f1]['section'] == data[f2]['section']:
            within_section_dists.append(dist)
        else:
            boundary_dists.append(dist)

    within_mean = float(np.mean(within_section_dists)) if within_section_dists else 0
    boundary_mean = float(np.mean(boundary_dists)) if boundary_dists else 0
    ratio = boundary_mean / max(within_mean, 1e-10)

    print(f"  Within-section adjacent pairs: n={len(within_section_dists)}, "
          f"mean_dist={within_mean:.3f}")
    print(f"  Boundary pairs: n={len(boundary_dists)}, "
          f"mean_dist={boundary_mean:.3f}")
    print(f"  Boundary/within ratio: {ratio:.3f}")

    interpretation = ("Section-driven" if ratio > 1.5
                      else "Smooth" if ratio < 1.1
                      else "Moderate discontinuity")
    print(f"  Interpretation: {interpretation}")

    return {
        'within_section_n': len(within_section_dists),
        'within_section_mean_dist': within_mean,
        'boundary_n': len(boundary_dists),
        'boundary_mean_dist': boundary_mean,
        'boundary_to_within_ratio': ratio,
        'interpretation': interpretation,
    }


def test6_archetype_spatial(folios, data):
    """T6: Archetype spatial clustering."""
    print("\n=== T6: Archetype Spatial Clustering ===")

    rng = np.random.default_rng(SEED + 2)

    # Folio positions (index in manuscript order)
    folio_idx = {f: i for i, f in enumerate(folios)}
    archetypes = {f: data[f]['archetype'] for f in folios if data[f]['archetype'] is not None}

    # Group by archetype
    arch_groups = defaultdict(list)
    for f, a in archetypes.items():
        arch_groups[a].append(folio_idx[f])

    results = {}
    for arch, positions in sorted(arch_groups.items()):
        if len(positions) < 5:
            continue

        # Mean pairwise position distance
        observed_mean = np.mean([abs(positions[i] - positions[j])
                                  for i, j in combinations(range(len(positions)), 2)])

        # Permutation: sample same number of positions from all folios
        all_positions = list(range(len(folios)))
        null_means = []
        for _ in range(N_PERM):
            sample = rng.choice(all_positions, size=len(positions), replace=False)
            null_mean = np.mean([abs(sample[i] - sample[j])
                                  for i, j in combinations(range(len(sample)), 2)])
            null_means.append(null_mean)

        null_means = np.array(null_means)
        p_val = np.mean(null_means <= observed_mean)  # Is observed smaller (more clustered)?

        print(f"  Archetype {arch} (n={len(positions)}): "
              f"observed={observed_mean:.1f}, null={np.mean(null_means):.1f}, p={p_val:.3f}")

        results[str(arch)] = {
            'n': len(positions),
            'observed_mean_dist': float(observed_mean),
            'null_mean_dist': float(np.mean(null_means)),
            'p': float(p_val),
            'spatially_clustered': p_val < 0.05,
        }

    clustered_archetypes = [a for a, r in results.items() if r.get('spatially_clustered')]
    print(f"  Spatially clustered archetypes: {clustered_archetypes if clustered_archetypes else 'NONE'}")

    results['clustered_archetypes'] = clustered_archetypes
    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    folios, data = load_data()

    # T1: Gate test
    t1 = test1_gate(folios, data)
    gate = t1['gate_decision']

    # T2-T6: Run regardless (informative even if gate fails)
    t2 = test2_adjacent_similarity(folios, data)
    t3 = test3_quire_clustering(folios, data)
    t4 = test4_autocorrelation(folios, data)
    t5 = test5_boundary_discontinuity(folios, data)
    t6 = test6_archetype_spatial(folios, data)

    # ── Verdict ──────────────────────────────────────────────────
    print(f"\n{'='*60}")

    # Gate
    pc2_partial = t1['PC2']['partial_r2_position']
    print(f"GATE: PC2 partial R² (position beyond section) = {pc2_partial:.4f} → {gate}")

    # Adjacent similarity
    adj_sig = t2.get('any_significant', False)
    print(f"Adjacent similarity within-section: {'SIGNIFICANT' if adj_sig else 'NOT significant'}")

    # Quire clustering
    quire_sig = t3.get('significant', False) if t3.get('test_possible') else 'N/A'
    print(f"Quire clustering (Herbal): {quire_sig}")

    # Autocorrelation
    auto_count = t4.get('significant_lag1_count', 0)
    print(f"Significant lag-1 autocorrelations: {auto_count}")

    # Boundary
    ratio = t5.get('boundary_to_within_ratio', 0)
    print(f"Section boundary ratio: {ratio:.3f} ({t5.get('interpretation', '')})")

    # Archetype
    clustered = t6.get('clustered_archetypes', [])
    print(f"Spatially clustered archetypes: {clustered if clustered else 'NONE'}")

    # Final verdict
    if gate == 'SECTION_CONFOUND':
        verdict = (f"SECTION_CONFOUND: PC2 position partial R²={pc2_partial:.4f} < 0.02. "
                   f"The folio_position signal in C1368 is section-mediated. "
                   f"Boundary ratio={ratio:.2f}. "
                   f"Lag-1 significant={auto_count}.")
    else:
        verdict = (f"GENUINE_SPATIAL: PC2 position partial R²={pc2_partial:.4f}. "
                   f"Adjacent similarity significant={adj_sig}. "
                   f"Lag-1 autocorrelations={auto_count}.")

    print(f"\nVERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save results
    results = {
        'metadata': {
            'phase': 482,
            'name': 'ACCENT_SPATIAL_STRUCTURE',
            'n_folios': len(folios),
            'n_permutations': N_PERM,
            'seed': SEED,
            'elapsed_seconds': elapsed,
        },
        'T1_gate': t1,
        'T2_adjacent': t2,
        'T3_quire': t3,
        'T4_autocorrelation': t4,
        'T5_boundary': t5,
        'T6_archetype': t6,
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'accent_spatial_structure.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

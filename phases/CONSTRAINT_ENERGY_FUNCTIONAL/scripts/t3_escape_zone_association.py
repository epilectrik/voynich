#!/usr/bin/env python3
"""
T3: Escape and Zone Association
CONSTRAINT_ENERGY_FUNCTIONAL phase

Test whether E(line) associates with:
1. AZC source zone of constituent MIDDLEs (C443: escape decreases C→R→S)
2. Embedding radial depth (norm in residual space)
3. MIDDLE escape potential (geometric closure test)
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

# Zone restrictiveness (higher = more restricted, lower escape rate)
# Based on C443: C ~1.4%, R1 ~2.0%, R2 ~1.2%, R3 ~0%, S ~0%
ZONE_ESCAPE_RATE = {'C': 1.4, 'R1': 2.0, 'R2': 1.2, 'R3': 0.0, 'S1': 0.0, 'S2': 0.0}


def reconstruct_middle_list():
    tx = Transcript()
    morph = Morphology()
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
    return all_middles, mid_to_idx


def build_residual_embedding(compat_matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    res_scaling = np.sqrt(np.maximum(res_evals, 0))
    res_emb = res_evecs * res_scaling[np.newaxis, :]
    return res_emb


def compute_line_energy(indices, embedding):
    if len(indices) < 2:
        return None
    vecs = embedding[indices]
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    valid = (norms.flatten() > 1e-10)
    if valid.sum() < 2:
        return None
    vecs = vecs[valid]
    norms = norms[valid]
    normed = vecs / norms
    cos_matrix = normed @ normed.T
    n = len(normed)
    triu_idx = np.triu_indices(n, k=1)
    return float(np.mean(cos_matrix[triu_idx]))


def parse_zone(placement):
    """Parse AZC placement code to zone."""
    if not placement:
        return None
    if placement.startswith('P'):
        return None  # Paragraph text, not diagram
    if placement.startswith('C'):
        return 'C'
    if placement.startswith('R'):
        # R1, R2, R3 etc. — extract ring number
        for i, ch in enumerate(placement[1:], 1):
            if ch.isdigit():
                return f'R{ch}'
        return 'R1'  # Fallback
    if placement.startswith('S'):
        for i, ch in enumerate(placement[1:], 1):
            if ch.isdigit():
                return f'S{ch}'
        return 'S1'
    return None


def build_azc_middle_zones(mid_to_idx):
    """Map each MIDDLE to its AZC zone appearances."""
    tx = Transcript()
    morph = Morphology()

    # MIDDLE -> {zone -> count}
    middle_zones = defaultdict(lambda: defaultdict(int))
    zone_counts = Counter()

    for token in tx.azc():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        placement = getattr(token, 'placement', None)
        zone = parse_zone(placement)
        if zone is None:
            continue
        m = morph.extract(word)
        if m.middle and m.middle in mid_to_idx:
            middle_zones[m.middle][zone] += 1
            zone_counts[zone] += 1

    return dict(middle_zones), dict(zone_counts)


def compute_middle_escape_score(middle_zones):
    """Compute weighted escape score per MIDDLE based on AZC zones."""
    # Weighted mean escape rate across zones where MIDDLE appears
    middle_escape = {}
    for mid, zones in middle_zones.items():
        total = sum(zones.values())
        if total == 0:
            continue
        weighted_escape = sum(
            ZONE_ESCAPE_RATE.get(z, 1.0) * count
            for z, count in zones.items()
        ) / total
        middle_escape[mid] = weighted_escape
    return middle_escape


def main():
    print("=" * 60)
    print("T3: Escape and Zone Association")
    print("=" * 60)

    # Step 1: Setup
    print("\n[1] Loading embedding and building AZC zone mapping...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles, mid_to_idx = reconstruct_middle_list()
    res_emb = build_residual_embedding(compat_matrix)

    middle_zones, zone_counts = build_azc_middle_zones(mid_to_idx)
    middle_escape = compute_middle_escape_score(middle_zones)
    print(f"  MIDDLEs with AZC zone data: {len(middle_zones)}")
    print(f"  Zone counts: {dict(sorted(zone_counts.items()))}")
    print(f"  MIDDLEs with escape scores: {len(middle_escape)}")

    # Step 2: Compute per-MIDDLE radial depth (norm in residual space)
    print("\n[2] Computing per-MIDDLE radial depth...")
    mid_norms = np.linalg.norm(res_emb, axis=1)
    print(f"  Norm range: [{mid_norms.min():.4f}, {mid_norms.max():.4f}]")
    print(f"  Norm mean: {mid_norms.mean():.4f}")

    # Correlate radial depth with escape score
    escape_scores = []
    norms_for_escape = []
    for mid, esc in middle_escape.items():
        idx = mid_to_idx[mid]
        escape_scores.append(esc)
        norms_for_escape.append(mid_norms[idx])

    escape_scores = np.array(escape_scores)
    norms_for_escape = np.array(norms_for_escape)
    rho_escape_norm, p_escape_norm = stats.spearmanr(escape_scores, norms_for_escape)
    print(f"\n  Escape score vs radial depth:")
    print(f"  Spearman rho: {rho_escape_norm:.4f} (p={p_escape_norm:.2e})")

    # Per-zone mean radial depth
    zone_norms = defaultdict(list)
    for mid, zones in middle_zones.items():
        idx = mid_to_idx[mid]
        norm = mid_norms[idx]
        for z in zones:
            zone_norms[z].append(norm)

    zone_norm_results = {}
    print("\n  Per-zone radial depth:")
    for z in ['C', 'R1', 'R2', 'R3', 'S1', 'S2']:
        vals = zone_norms.get(z, [])
        if vals:
            zone_norm_results[z] = {
                'n': len(vals),
                'mean_norm': float(np.mean(vals)),
                'escape_rate': ZONE_ESCAPE_RATE.get(z, 0),
            }
            print(f"    {z:>3s}: n={len(vals):>4d}, "
                  f"mean_norm={np.mean(vals):.4f}, "
                  f"escape_rate={ZONE_ESCAPE_RATE.get(z, 0):.1f}%")

    # Step 3: Per-B-line escape score and energy
    print("\n[3] Computing per-line escape score and energy...")
    tx = Transcript()
    morph = Morphology()

    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        key = (token.folio, token.line)
        line_tokens[key].append({
            'middle': m.middle,
            'mid_idx': mid_to_idx.get(m.middle) if m.middle else None,
        })

    line_energies = []
    line_escape_scores = []
    line_mean_norms = []
    line_azc_coverage = []  # Fraction of MIDDLEs with AZC data

    for key, tokens in line_tokens.items():
        # Energy
        a_indices = list(set(t['mid_idx'] for t in tokens if t['mid_idx'] is not None))
        energy = compute_line_energy(a_indices, res_emb)
        if energy is None:
            continue

        # Escape score: mean escape score of MIDDLEs on line
        mid_escapes = [middle_escape[t['middle']]
                       for t in tokens
                       if t['middle'] and t['middle'] in middle_escape]
        if not mid_escapes:
            continue

        line_energies.append(energy)
        line_escape_scores.append(np.mean(mid_escapes))
        line_mean_norms.append(np.mean([mid_norms[i] for i in a_indices]))
        line_azc_coverage.append(len(mid_escapes) / len(tokens))

    line_energies = np.array(line_energies)
    line_escape_scores = np.array(line_escape_scores)
    line_mean_norms = np.array(line_mean_norms)
    line_azc_coverage = np.array(line_azc_coverage)

    print(f"  Lines with both energy and escape: {len(line_energies)}")
    print(f"  Mean AZC coverage per line: {np.mean(line_azc_coverage):.1%}")

    # Step 4: Correlations
    print("\n[4] Correlations...")

    # E vs escape score
    rho_e_esc, p_e_esc = stats.spearmanr(line_escape_scores, line_energies)
    print(f"  E vs escape score: rho={rho_e_esc:.4f} (p={p_e_esc:.2e})")

    # E vs mean radial depth
    rho_e_norm, p_e_norm = stats.spearmanr(line_mean_norms, line_energies)
    print(f"  E vs mean radial depth: rho={rho_e_norm:.4f} (p={p_e_norm:.2e})")

    # Escape score vs radial depth (at line level)
    rho_esc_norm, p_esc_norm = stats.spearmanr(line_escape_scores, line_mean_norms)
    print(f"  Escape score vs radial depth: rho={rho_esc_norm:.4f} (p={p_esc_norm:.2e})")

    # Step 5: Escape score bins
    print("\n[5] Energy by escape score bins...")
    esc_pcts = np.percentile(line_escape_scores, [25, 50, 75])
    esc_bin_labels = ['low_escape', 'med_low', 'med_high', 'high_escape']
    esc_bins = {}
    for e, esc in zip(line_energies, line_escape_scores):
        if esc <= esc_pcts[0]:
            b = 'low_escape'
        elif esc <= esc_pcts[1]:
            b = 'med_low'
        elif esc <= esc_pcts[2]:
            b = 'med_high'
        else:
            b = 'high_escape'
        esc_bins.setdefault(b, []).append(e)

    esc_bin_results = {}
    for b in esc_bin_labels:
        vals = esc_bins.get(b, [])
        if vals:
            esc_bin_results[b] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
            }
            print(f"    {b:>12s}: n={len(vals):>4d}, E={np.mean(vals):+.5f}")

    # Step 6: Radial depth bins
    print("\n[6] Energy by radial depth bins...")
    norm_pcts = np.percentile(line_mean_norms, [25, 50, 75])
    norm_bin_labels = ['shallow', 'mid_shallow', 'mid_deep', 'deep']
    norm_bins = {}
    for e, n in zip(line_energies, line_mean_norms):
        if n <= norm_pcts[0]:
            b = 'shallow'
        elif n <= norm_pcts[1]:
            b = 'mid_shallow'
        elif n <= norm_pcts[2]:
            b = 'mid_deep'
        else:
            b = 'deep'
        norm_bins.setdefault(b, []).append(e)

    norm_bin_results = {}
    for b in norm_bin_labels:
        vals = norm_bins.get(b, [])
        if vals:
            norm_bin_results[b] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
            }
            print(f"    {b:>12s}: n={len(vals):>4d}, E={np.mean(vals):+.5f}")

    # Step 7: Zone-specific MIDDLE energy contribution
    print("\n[7] Per-zone MIDDLE mean energy contribution...")
    # For each zone, compute mean energy of lines that USE MIDDLEs from that zone
    zone_line_energies = defaultdict(list)
    for key, tokens in line_tokens.items():
        a_indices = list(set(t['mid_idx'] for t in tokens if t['mid_idx'] is not None))
        energy = compute_line_energy(a_indices, res_emb)
        if energy is None:
            continue
        # Which zones are represented on this line?
        line_zones = set()
        for t in tokens:
            if t['middle'] and t['middle'] in middle_zones:
                for z in middle_zones[t['middle']]:
                    line_zones.add(z)
        for z in line_zones:
            zone_line_energies[z].append(energy)

    zone_energy_results = {}
    for z in ['C', 'R1', 'R2', 'R3', 'S1', 'S2']:
        vals = zone_line_energies.get(z, [])
        if vals:
            zone_energy_results[z] = {
                'n_lines': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
            }
            print(f"    {z:>3s}: n_lines={len(vals):>4d}, E={np.mean(vals):+.5f}")

    # Step 8: Verdict
    print("\n" + "=" * 60)

    has_escape_energy = abs(rho_e_esc) > 0.05 and p_e_esc < 0.01
    has_norm_energy = abs(rho_e_norm) > 0.05 and p_e_norm < 0.01
    has_escape_norm = abs(rho_escape_norm) > 0.05 and p_escape_norm < 0.01

    n_sig = sum([has_escape_energy, has_norm_energy, has_escape_norm])

    if n_sig >= 2:
        verdict = "GEOMETRIC_CLOSURE"
    elif n_sig >= 1:
        verdict = "PARTIAL_CLOSURE"
    else:
        verdict = "NO_CLOSURE"

    findings = []
    if has_escape_energy:
        findings.append(f"escape→energy (rho={rho_e_esc:.3f})")
    if has_norm_energy:
        findings.append(f"depth→energy (rho={rho_e_norm:.3f})")
    if has_escape_norm:
        findings.append(f"escape→depth (rho={rho_escape_norm:.3f})")

    explanation = (
        f"{n_sig}/3 geometric links significant. "
        + ("; ".join(findings) if findings else "No significant links.")
    )
    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save
    results = {
        'test': 'T3_escape_zone_association',
        'n_middles_with_azc': len(middle_zones),
        'zone_counts': dict(zone_counts),
        'escape_norm_correlation': {
            'rho': float(rho_escape_norm),
            'p': float(p_escape_norm),
            'description': 'MIDDLE-level: escape score vs residual norm',
        },
        'zone_radial_depth': zone_norm_results,
        'n_lines': len(line_energies),
        'mean_azc_coverage': float(np.mean(line_azc_coverage)),
        'energy_escape_correlation': {
            'rho': float(rho_e_esc),
            'p': float(p_e_esc),
            'description': 'Line-level: E vs mean escape score',
        },
        'energy_norm_correlation': {
            'rho': float(rho_e_norm),
            'p': float(p_e_norm),
            'description': 'Line-level: E vs mean radial depth',
        },
        'escape_norm_line_correlation': {
            'rho': float(rho_esc_norm),
            'p': float(p_esc_norm),
            'description': 'Line-level: escape score vs radial depth',
        },
        'escape_bin_energy': esc_bin_results,
        'depth_bin_energy': norm_bin_results,
        'zone_line_energy': zone_energy_results,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't3_escape_zone_association.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't3_escape_zone_association.json'}")


if __name__ == '__main__':
    main()

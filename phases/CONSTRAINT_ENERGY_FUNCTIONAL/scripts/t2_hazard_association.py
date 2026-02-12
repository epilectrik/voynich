#!/usr/bin/env python3
"""
T2: Hazard Association
CONSTRAINT_ENERGY_FUNCTIONAL phase

Test whether constraint energy E(line) associates with hazard proximity,
EN lane identity, REGIME, and folio position.

Predictions from C669:
- E drops (more tension) as hazard proximity tightens
- QO lane tightens (rho=-0.082), CHSH static
- REGIME_2/3 strongest tightening, REGIME_4 flat

Key definitions:
- EN tokens = energy operators (QO + CHSH lanes) where hazard events occur
- Hazard density = fraction of EN tokens on a line
- Lane = dominant EN type (QO vs CHSH) on a line
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
REGIME_FILE = Path(__file__).resolve().parents[3] / 'results' / 'regime_folio_mapping.json'
K_RESIDUAL = 99

# Lane prefix sets (from voynich.py _get_prefix_lane)
QO_PREFIXES = {'qo', 'o', 'ok', 'ot', 'ko', 'to', 'po'}
CHSH_PREFIXES = {'ch', 'sh', 'lsh'}
EN_PREFIXES = QO_PREFIXES | CHSH_PREFIXES  # All energy operators


def reconstruct_middle_list():
    """Reconstruct the MIDDLE ordering from T1."""
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
    """Build residual embedding: eigenvectors 2-100, hub removed."""
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
    """Compute E(line) = mean pairwise cosine similarity in residual space."""
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
    cosines = cos_matrix[triu_idx]
    return float(np.mean(cosines))


def load_regime_mapping():
    """Load REGIME assignment per folio."""
    with open(REGIME_FILE) as f:
        raw = json.load(f)
    folio_to_regime = {}
    for regime, folios in raw.items():
        for folio in folios:
            folio_to_regime[folio] = regime
    return folio_to_regime


def extract_b_line_data(mid_to_idx, res_emb, folio_to_regime):
    """Extract per-line energy, hazard density, lane, REGIME, folio position."""
    tx = Transcript()
    morph = Morphology()

    # First pass: collect per-line token data
    # key = (folio, line)
    line_tokens = defaultdict(list)  # (folio, line) -> [(word, prefix, middle, mid_idx)]
    folio_lines = defaultdict(set)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        key = (token.folio, token.line)
        mid_idx = mid_to_idx.get(m.middle) if m.middle else None
        line_tokens[key].append({
            'word': word,
            'prefix': m.prefix,
            'middle': m.middle,
            'mid_idx': mid_idx,
        })
        folio_lines[token.folio].add(token.line)

    # Pre-compute folio line ordering for position calculation
    folio_line_order = {}
    for folio, lines in folio_lines.items():
        sorted_lines = sorted(lines)
        n = len(sorted_lines)
        for i, line in enumerate(sorted_lines):
            folio_line_order[(folio, line)] = i / max(n - 1, 1)  # 0 to 1

    # Second pass: compute per-line features
    line_data = []
    for key, tokens in line_tokens.items():
        folio, line = key

        # Energy: from A-space MIDDLEs
        a_indices = [t['mid_idx'] for t in tokens if t['mid_idx'] is not None]
        unique_indices = list(set(a_indices))
        energy = compute_line_energy(unique_indices, res_emb)
        if energy is None:
            continue

        # Token counts
        n_tokens = len(tokens)
        n_en = sum(1 for t in tokens if t['prefix'] in EN_PREFIXES)
        n_qo = sum(1 for t in tokens if t['prefix'] in QO_PREFIXES)
        n_chsh = sum(1 for t in tokens if t['prefix'] in CHSH_PREFIXES)

        # Hazard density = fraction of EN tokens
        en_frac = n_en / n_tokens if n_tokens > 0 else 0

        # Lane classification
        if n_qo > n_chsh and n_qo > 0:
            lane = 'QO'
        elif n_chsh > n_qo and n_chsh > 0:
            lane = 'CHSH'
        elif n_qo == n_chsh and n_qo > 0:
            lane = 'MIXED'
        else:
            lane = 'OTHER'

        # QO fraction among EN tokens
        qo_frac = n_qo / n_en if n_en > 0 else None

        # REGIME
        regime = folio_to_regime.get(folio, None)

        # Folio position (normalized 0-1)
        position = folio_line_order.get(key, 0.5)

        line_data.append({
            'folio': folio,
            'line': line,
            'energy': energy,
            'n_tokens': n_tokens,
            'n_a_middles': len(unique_indices),
            'n_en': n_en,
            'en_frac': en_frac,
            'n_qo': n_qo,
            'n_chsh': n_chsh,
            'lane': lane,
            'qo_frac': qo_frac,
            'regime': regime,
            'position': position,
        })

    return line_data


def main():
    print("=" * 60)
    print("T2: Hazard Association")
    print("=" * 60)

    # Step 1: Setup
    print("\n[1] Loading embedding and REGIME mapping...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles, mid_to_idx = reconstruct_middle_list()
    res_emb = build_residual_embedding(compat_matrix)
    folio_to_regime = load_regime_mapping()
    print(f"  MIDDLEs: {len(all_middles)}, REGIMEs: {len(folio_to_regime)} folios")

    # Step 2: Extract line data
    print("\n[2] Extracting per-line data...")
    line_data = extract_b_line_data(mid_to_idx, res_emb, folio_to_regime)
    print(f"  Lines with valid energy: {len(line_data)}")

    energies = np.array([d['energy'] for d in line_data])
    en_fracs = np.array([d['en_frac'] for d in line_data])
    positions = np.array([d['position'] for d in line_data])

    # Step 3: E vs EN fraction (hazard density proxy)
    print("\n[3] E vs EN fraction (hazard density)...")
    rho_en, p_en = stats.spearmanr(en_fracs, energies)
    print(f"  Spearman rho(EN_frac, E): {rho_en:.4f} (p={p_en:.2e})")

    # Bin by EN fraction quartiles
    en_quartiles = np.percentile(en_fracs[en_fracs > 0], [25, 50, 75])
    en_bins = ['low_EN', 'med_low_EN', 'med_high_EN', 'high_EN']
    en_bin_data = {}
    for d in line_data:
        ef = d['en_frac']
        if ef <= en_quartiles[0]:
            b = 'low_EN'
        elif ef <= en_quartiles[1]:
            b = 'med_low_EN'
        elif ef <= en_quartiles[2]:
            b = 'med_high_EN'
        else:
            b = 'high_EN'
        en_bin_data.setdefault(b, []).append(d['energy'])

    print(f"  EN fraction quartile boundaries: {en_quartiles}")
    en_bin_results = {}
    for b in en_bins:
        vals = en_bin_data.get(b, [])
        if vals:
            en_bin_results[b] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
            }
            print(f"    {b}: n={len(vals)}, E={np.mean(vals):.5f} ± {np.std(vals):.5f}")

    # Lines with zero EN vs nonzero EN
    zero_en = [d['energy'] for d in line_data if d['n_en'] == 0]
    nonzero_en = [d['energy'] for d in line_data if d['n_en'] > 0]
    if zero_en and nonzero_en:
        mw_stat, mw_p = stats.mannwhitneyu(zero_en, nonzero_en, alternative='two-sided')
        print(f"\n  Zero-EN lines: n={len(zero_en)}, E={np.mean(zero_en):.5f}")
        print(f"  Nonzero-EN lines: n={len(nonzero_en)}, E={np.mean(nonzero_en):.5f}")
        print(f"  Mann-Whitney p={mw_p:.2e}")

    # Step 4: E by lane
    print("\n[4] E by lane (QO vs CHSH)...")
    lane_data = defaultdict(list)
    for d in line_data:
        lane_data[d['lane']].append(d['energy'])

    lane_results = {}
    for lane in ['QO', 'CHSH', 'MIXED', 'OTHER']:
        vals = lane_data.get(lane, [])
        if vals:
            lane_results[lane] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
                'median_E': float(np.median(vals)),
            }
            print(f"  {lane:>6s}: n={len(vals):>5d}, "
                  f"E={np.mean(vals):+.5f} ± {np.std(vals):.5f}")

    # QO vs CHSH direct comparison
    qo_e = lane_data.get('QO', [])
    chsh_e = lane_data.get('CHSH', [])
    if qo_e and chsh_e:
        mw_lane, p_lane = stats.mannwhitneyu(qo_e, chsh_e, alternative='two-sided')
        print(f"\n  QO vs CHSH: Mann-Whitney p={p_lane:.2e}")
        print(f"  QO mean - CHSH mean: {np.mean(qo_e) - np.mean(chsh_e):+.5f}")

    # Step 5: E by REGIME
    print("\n[5] E by REGIME...")
    regime_data = defaultdict(list)
    for d in line_data:
        if d['regime']:
            regime_data[d['regime']].append(d['energy'])

    regime_results = {}
    for regime in sorted(regime_data.keys()):
        vals = regime_data[regime]
        regime_results[regime] = {
            'n': len(vals),
            'mean_E': float(np.mean(vals)),
            'std_E': float(np.std(vals)),
            'median_E': float(np.median(vals)),
        }
        print(f"  {regime}: n={len(vals):>4d}, "
              f"E={np.mean(vals):+.5f} ± {np.std(vals):.5f}")

    # KW test across REGIMEs
    regime_groups = [regime_data[r] for r in sorted(regime_data.keys())]
    if len(regime_groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*regime_groups)
        print(f"\n  Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.2e}")

    # REGIME variance comparison (C979: REGIME modulates variance, not mean?)
    print("\n  REGIME variance comparison:")
    for regime in sorted(regime_data.keys()):
        vals = regime_data[regime]
        print(f"    {regime}: var={np.var(vals):.6f}, IQR={np.percentile(vals, 75) - np.percentile(vals, 25):.5f}")

    # Step 6: E vs folio position (program progression)
    print("\n[6] E vs folio position...")
    rho_pos, p_pos = stats.spearmanr(positions, energies)
    print(f"  Spearman rho(position, E): {rho_pos:.4f} (p={p_pos:.2e})")

    # Quartile analysis
    pos_quartile_bounds = [0.25, 0.5, 0.75]
    pos_labels = ['Q1 (early)', 'Q2', 'Q3', 'Q4 (late)']
    pos_quartile_data = {l: [] for l in pos_labels}
    for d in line_data:
        p = d['position']
        if p <= 0.25:
            pos_quartile_data['Q1 (early)'].append(d['energy'])
        elif p <= 0.50:
            pos_quartile_data['Q2'].append(d['energy'])
        elif p <= 0.75:
            pos_quartile_data['Q3'].append(d['energy'])
        else:
            pos_quartile_data['Q4 (late)'].append(d['energy'])

    pos_results = {}
    for label in pos_labels:
        vals = pos_quartile_data[label]
        if vals:
            pos_results[label] = {
                'n': len(vals),
                'mean_E': float(np.mean(vals)),
                'std_E': float(np.std(vals)),
            }
            print(f"  {label:>12s}: n={len(vals):>4d}, E={np.mean(vals):+.5f} ± {np.std(vals):.5f}")

    # Step 7: E by lane × position (QO tightens, CHSH static per C669)
    print("\n[7] Lane × position interaction...")
    for lane in ['QO', 'CHSH']:
        lane_lines = [d for d in line_data if d['lane'] == lane]
        if len(lane_lines) < 20:
            print(f"  {lane}: too few lines ({len(lane_lines)})")
            continue

        lane_pos = np.array([d['position'] for d in lane_lines])
        lane_e = np.array([d['energy'] for d in lane_lines])
        rho_lp, p_lp = stats.spearmanr(lane_pos, lane_e)
        print(f"  {lane}: rho(position, E) = {rho_lp:.4f} (p={p_lp:.2e}), n={len(lane_lines)}")

        # Quartile split
        early = [d['energy'] for d in lane_lines if d['position'] <= 0.25]
        late = [d['energy'] for d in lane_lines if d['position'] > 0.75]
        if early and late:
            shift = np.mean(late) - np.mean(early)
            print(f"    Early (Q1): E={np.mean(early):+.5f} (n={len(early)})")
            print(f"    Late (Q4):  E={np.mean(late):+.5f} (n={len(late)})")
            print(f"    Shift (late - early): {shift:+.5f}")

    # Step 8: E by REGIME × position
    print("\n[8] REGIME × position interaction...")
    regime_pos_results = {}
    for regime in sorted(regime_data.keys()):
        regime_lines = [d for d in line_data if d['regime'] == regime]
        if len(regime_lines) < 20:
            continue
        r_pos = np.array([d['position'] for d in regime_lines])
        r_e = np.array([d['energy'] for d in regime_lines])
        rho_rp, p_rp = stats.spearmanr(r_pos, r_e)

        early = [d['energy'] for d in regime_lines if d['position'] <= 0.25]
        late = [d['energy'] for d in regime_lines if d['position'] > 0.75]
        shift = (np.mean(late) - np.mean(early)) if early and late else 0

        regime_pos_results[regime] = {
            'rho': float(rho_rp),
            'p': float(p_rp),
            'n': len(regime_lines),
            'early_mean': float(np.mean(early)) if early else None,
            'late_mean': float(np.mean(late)) if late else None,
            'shift': float(shift),
        }
        print(f"  {regime}: rho={rho_rp:+.4f} (p={p_rp:.2e}), "
              f"shift={shift:+.5f}")

    # Step 9: High-EN lines as hazard proxy
    print("\n[9] High-EN-density lines (top 25%) vs rest...")
    en_threshold = np.percentile(en_fracs, 75)
    high_en = [d['energy'] for d in line_data if d['en_frac'] > en_threshold]
    low_en = [d['energy'] for d in line_data if d['en_frac'] <= en_threshold]
    if high_en and low_en:
        mw_hi, p_hi = stats.mannwhitneyu(high_en, low_en, alternative='two-sided')
        print(f"  High-EN (top 25%, EN>{en_threshold:.2f}): n={len(high_en)}, E={np.mean(high_en):+.5f}")
        print(f"  Rest: n={len(low_en)}, E={np.mean(low_en):+.5f}")
        print(f"  Shift (high - rest): {np.mean(high_en) - np.mean(low_en):+.5f}")
        print(f"  Mann-Whitney p={p_hi:.2e}")

    # Step 10: Verdict
    print("\n" + "=" * 60)

    has_en_correlation = abs(rho_en) > 0.05 and p_en < 0.01
    has_lane_difference = p_lane < 0.01 if qo_e and chsh_e else False
    has_regime_effect = kw_p < 0.01 if len(regime_groups) >= 2 else False
    has_position_trend = abs(rho_pos) > 0.05 and p_pos < 0.01

    n_associations = sum([has_en_correlation, has_lane_difference,
                          has_regime_effect, has_position_trend])

    if n_associations >= 3:
        verdict = "STRONG_HAZARD_ASSOCIATION"
    elif n_associations >= 1:
        verdict = "PARTIAL_HAZARD_ASSOCIATION"
    else:
        verdict = "NO_HAZARD_ASSOCIATION"

    associations = []
    if has_en_correlation:
        associations.append(f"EN density (rho={rho_en:.3f}, p={p_en:.1e})")
    if has_lane_difference:
        associations.append(f"Lane difference (QO vs CHSH, p={p_lane:.1e})")
    if has_regime_effect:
        associations.append(f"REGIME (KW p={kw_p:.1e})")
    if has_position_trend:
        associations.append(f"Folio position (rho={rho_pos:.3f}, p={p_pos:.1e})")

    explanation = (
        f"{n_associations}/4 associations significant. "
        + ("; ".join(associations) if associations else "None significant.")
    )
    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save results
    results = {
        'test': 'T2_hazard_association',
        'n_lines': len(line_data),
        'en_correlation': {
            'rho': float(rho_en),
            'p': float(p_en),
            'direction': 'positive' if rho_en > 0 else 'negative',
        },
        'en_quartile_energy': en_bin_results,
        'zero_vs_nonzero_en': {
            'zero_n': len(zero_en) if zero_en else 0,
            'zero_mean': float(np.mean(zero_en)) if zero_en else None,
            'nonzero_n': len(nonzero_en) if nonzero_en else 0,
            'nonzero_mean': float(np.mean(nonzero_en)) if nonzero_en else None,
        },
        'lane_energy': lane_results,
        'qo_vs_chsh': {
            'shift': float(np.mean(qo_e) - np.mean(chsh_e)) if qo_e and chsh_e else None,
            'p': float(p_lane) if qo_e and chsh_e else None,
        },
        'regime_energy': regime_results,
        'regime_kw': {
            'H': float(kw_stat) if len(regime_groups) >= 2 else None,
            'p': float(kw_p) if len(regime_groups) >= 2 else None,
        },
        'position_correlation': {
            'rho': float(rho_pos),
            'p': float(p_pos),
        },
        'position_quartile_energy': pos_results,
        'regime_x_position': regime_pos_results,
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't2_hazard_association.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't2_hazard_association.json'}")


if __name__ == '__main__':
    main()

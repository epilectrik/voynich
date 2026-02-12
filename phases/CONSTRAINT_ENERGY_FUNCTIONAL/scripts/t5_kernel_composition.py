#!/usr/bin/env python3
"""
T5: Kernel Composition Shift
CONSTRAINT_ENERGY_FUNCTIONAL phase

Test whether:
1. E correlates with h/e kernel fraction — C965
2. Safe-pool vs hazard-pool energy differs
3. Compound MIDDLEs vs simple MIDDLEs energy differs
4. Line-1 (HT specification) energy vs body energy by kernel composition
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DISC_RESULTS = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
K_RESIDUAL = 99

# Kernel characters (from BCSC: k, h, e are the three core operators)
KERNEL_CHARS = {'k', 'h', 'e'}

# EN lane prefixes (hazard-adjacent = CHSH, hazard-distant = QO)
CHSH_PREFIXES = {'ch', 'sh', 'lsh'}
QO_PREFIXES = {'qo', 'o', 'ok', 'ot', 'ko', 'to', 'po'}
EN_PREFIXES = CHSH_PREFIXES | QO_PREFIXES


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
    return res_evecs * res_scaling[np.newaxis, :]


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


def get_middle_kernels(middle):
    """Identify which kernel characters (k, h, e) appear in a MIDDLE."""
    if not middle:
        return set()
    return {c for c in middle if c in KERNEL_CHARS}


def is_compound_middle(middle, core_middles):
    """Check if MIDDLE contains other core MIDDLEs as substrings."""
    if not middle or len(middle) < 4:
        return False
    for core in core_middles:
        if core != middle and core in middle and len(core) >= 2:
            return True
    return False


def main():
    print("=" * 60)
    print("T5: Kernel Composition Shift")
    print("=" * 60)

    # Setup
    print("\n[1] Loading...")
    compat_matrix = np.load(DISC_RESULTS / 't1_compat_matrix.npy')
    all_middles, mid_to_idx = reconstruct_middle_list()
    res_emb = build_residual_embedding(compat_matrix)

    # Build core MIDDLE set (short, frequent) for compound detection
    core_middles = {m for m in all_middles if len(m) <= 3}
    print(f"  A-space MIDDLEs: {len(all_middles)}")
    print(f"  Core MIDDLEs (len<=3): {len(core_middles)}")

    # Per-MIDDLE kernel composition
    mid_kernels = {}
    for mid in all_middles:
        mid_kernels[mid] = get_middle_kernels(mid)

    # Distribution of kernel types
    k_count = sum(1 for k in mid_kernels.values() if 'k' in k)
    h_count = sum(1 for k in mid_kernels.values() if 'h' in k)
    e_count = sum(1 for k in mid_kernels.values() if 'e' in k)
    print(f"  MIDDLEs containing k: {k_count}")
    print(f"  MIDDLEs containing h: {h_count}")
    print(f"  MIDDLEs containing e: {e_count}")

    # Step 2: Extract per-line data
    print("\n[2] Extracting per-line kernel composition and energy...")
    tx = Transcript()
    morph = Morphology()

    line_data_raw = defaultdict(list)
    folio_lines = defaultdict(set)

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        key = (token.folio, token.line)
        mid_idx = mid_to_idx.get(m.middle) if m.middle else None
        kernels = get_middle_kernels(m.middle) if m.middle else set()
        compound = is_compound_middle(m.middle, core_middles) if m.middle else False

        line_data_raw[key].append({
            'middle': m.middle,
            'prefix': m.prefix,
            'mid_idx': mid_idx,
            'kernels': kernels,
            'has_k': 'k' in kernels,
            'has_h': 'h' in kernels,
            'has_e': 'e' in kernels,
            'is_en': m.prefix in EN_PREFIXES if m.prefix else False,
            'is_chsh': m.prefix in CHSH_PREFIXES if m.prefix else False,
            'is_qo': m.prefix in QO_PREFIXES if m.prefix else False,
            'compound': compound,
        })
        folio_lines[token.folio].add(token.line)

    # Folio line ordering for position
    folio_ordered = {f: sorted(lines) for f, lines in folio_lines.items()}

    # Compute per-line features
    line_records = []
    for key, tokens in line_data_raw.items():
        folio, line = key
        a_indices = list(set(t['mid_idx'] for t in tokens if t['mid_idx'] is not None))
        energy = compute_line_energy(a_indices, res_emb)
        if energy is None:
            continue

        n = len(tokens)
        n_with_k = sum(1 for t in tokens if t['has_k'])
        n_with_h = sum(1 for t in tokens if t['has_h'])
        n_with_e = sum(1 for t in tokens if t['has_e'])
        n_en = sum(1 for t in tokens if t['is_en'])
        n_compound = sum(1 for t in tokens if t['compound'])

        # Folio position
        ordered = folio_ordered.get(folio, [])
        if line in ordered and len(ordered) > 1:
            pos = ordered.index(line) / (len(ordered) - 1)
        else:
            pos = 0.5

        # Is first line?
        is_first = (ordered and line == ordered[0])

        line_records.append({
            'folio': folio,
            'line': line,
            'energy': energy,
            'n_tokens': n,
            'k_frac': n_with_k / n,
            'h_frac': n_with_h / n,
            'e_frac': n_with_e / n,
            'en_frac': n_en / n,
            'compound_frac': n_compound / n,
            'position': pos,
            'is_first': is_first,
        })

    print(f"  Lines with valid energy: {len(line_records)}")

    energies = np.array([r['energy'] for r in line_records])
    h_fracs = np.array([r['h_frac'] for r in line_records])
    e_fracs = np.array([r['e_frac'] for r in line_records])
    k_fracs = np.array([r['k_frac'] for r in line_records])
    compound_fracs = np.array([r['compound_frac'] for r in line_records])
    positions = np.array([r['position'] for r in line_records])

    # Step 3: E vs kernel fractions
    print("\n[3] E vs kernel fractions...")
    rho_h, p_h = stats.spearmanr(h_fracs, energies)
    rho_e, p_e = stats.spearmanr(e_fracs, energies)
    rho_k, p_k = stats.spearmanr(k_fracs, energies)
    print(f"  E vs h_frac: rho={rho_h:+.4f} (p={p_h:.2e})")
    print(f"  E vs e_frac: rho={rho_e:+.4f} (p={p_e:.2e})")
    print(f"  E vs k_frac: rho={rho_k:+.4f} (p={p_k:.2e})")

    # Step 4: Kernel fraction bins
    print("\n[4] E by h-fraction bins...")
    h_pcts = np.percentile(h_fracs, [25, 50, 75])
    h_bin_labels = ['low_h', 'med_low_h', 'med_high_h', 'high_h']
    h_bins = defaultdict(list)
    for r in line_records:
        hf = r['h_frac']
        if hf <= h_pcts[0]:
            h_bins['low_h'].append(r['energy'])
        elif hf <= h_pcts[1]:
            h_bins['med_low_h'].append(r['energy'])
        elif hf <= h_pcts[2]:
            h_bins['med_high_h'].append(r['energy'])
        else:
            h_bins['high_h'].append(r['energy'])

    h_bin_results = {}
    for b in h_bin_labels:
        vals = h_bins[b]
        if vals:
            h_bin_results[b] = {'n': len(vals), 'mean_E': float(np.mean(vals))}
            print(f"    {b:>12s}: n={len(vals):>4d}, E={np.mean(vals):+.5f}")

    print("\n  E by e-fraction bins...")
    e_pcts = np.percentile(e_fracs, [25, 50, 75])
    e_bin_labels = ['low_e', 'med_low_e', 'med_high_e', 'high_e']
    e_bins = defaultdict(list)
    for r in line_records:
        ef = r['e_frac']
        if ef <= e_pcts[0]:
            e_bins['low_e'].append(r['energy'])
        elif ef <= e_pcts[1]:
            e_bins['med_low_e'].append(r['energy'])
        elif ef <= e_pcts[2]:
            e_bins['med_high_e'].append(r['energy'])
        else:
            e_bins['high_e'].append(r['energy'])

    e_bin_results = {}
    for b in e_bin_labels:
        vals = e_bins[b]
        if vals:
            e_bin_results[b] = {'n': len(vals), 'mean_E': float(np.mean(vals))}
            print(f"    {b:>12s}: n={len(vals):>4d}, E={np.mean(vals):+.5f}")

    # Step 5: E vs compound fraction
    print("\n[5] E vs compound MIDDLE fraction...")
    rho_cmp, p_cmp = stats.spearmanr(compound_fracs, energies)
    print(f"  E vs compound_frac: rho={rho_cmp:+.4f} (p={p_cmp:.2e})")

    # Compound-heavy (top 25%) vs rest
    cmp_thresh = np.percentile(compound_fracs, 75)
    high_cmp = [r['energy'] for r in line_records if r['compound_frac'] > cmp_thresh]
    low_cmp = [r['energy'] for r in line_records if r['compound_frac'] <= cmp_thresh]
    if high_cmp and low_cmp:
        mw_cmp, p_cmp_mw = stats.mannwhitneyu(high_cmp, low_cmp, alternative='two-sided')
        print(f"  High-compound (top 25%): n={len(high_cmp)}, E={np.mean(high_cmp):+.5f}")
        print(f"  Rest: n={len(low_cmp)}, E={np.mean(low_cmp):+.5f}")
        print(f"  Shift: {np.mean(high_cmp) - np.mean(low_cmp):+.5f}")
        print(f"  Mann-Whitney p={p_cmp_mw:.2e}")

    # Step 6: Kernel shift × energy trajectory (C965 test)
    print("\n[6] Kernel shift × energy trajectory...")
    # Split by position quintile, compute h_frac and E
    for kernel_name, kernel_arr in [('h', h_fracs), ('e', e_fracs), ('k', k_fracs)]:
        early = [(kernel_arr[i], energies[i])
                 for i, r in enumerate(line_records) if r['position'] <= 0.2]
        late = [(kernel_arr[i], energies[i])
                for i, r in enumerate(line_records) if r['position'] >= 0.8]

        if early and late:
            early_k = np.mean([x[0] for x in early])
            late_k = np.mean([x[0] for x in late])
            early_e = np.mean([x[1] for x in early])
            late_e = np.mean([x[1] for x in late])
            print(f"\n  {kernel_name}-kernel: early={early_k:.3f}, late={late_k:.3f}, "
                  f"shift={late_k - early_k:+.3f}")
            print(f"    Energy: early={early_e:+.5f}, late={late_e:+.5f}, "
                  f"shift={late_e - early_e:+.5f}")

    # Step 7: Safe-pool vs hazard-pool energy
    print("\n[7] Safe-pool vs hazard-pool energy (EN vs non-EN)...")
    # EN-heavy lines (>50% EN) vs EN-light (<25% EN)
    en_fracs = np.array([r['en_frac'] for r in line_records])
    en_heavy = [r['energy'] for r in line_records if r['en_frac'] > 0.5]
    en_light = [r['energy'] for r in line_records if r['en_frac'] < 0.25]
    if en_heavy and en_light:
        mw_en, p_en_mw = stats.mannwhitneyu(en_heavy, en_light, alternative='two-sided')
        print(f"  EN-heavy (>50%): n={len(en_heavy)}, E={np.mean(en_heavy):+.5f}")
        print(f"  EN-light (<25%): n={len(en_light)}, E={np.mean(en_light):+.5f}")
        print(f"  Shift: {np.mean(en_heavy) - np.mean(en_light):+.5f}")
        print(f"  Mann-Whitney p={p_en_mw:.2e}")

    # Step 8: First line vs body by kernel composition
    print("\n[8] First-line vs body by kernel composition...")
    first_records = [r for r in line_records if r['is_first']]
    body_records = [r for r in line_records if not r['is_first']]

    if first_records and body_records:
        print(f"  First lines: n={len(first_records)}")
        print(f"    h_frac: {np.mean([r['h_frac'] for r in first_records]):.3f}")
        print(f"    e_frac: {np.mean([r['e_frac'] for r in first_records]):.3f}")
        print(f"    compound_frac: {np.mean([r['compound_frac'] for r in first_records]):.3f}")
        print(f"    E: {np.mean([r['energy'] for r in first_records]):+.5f}")

        print(f"  Body lines: n={len(body_records)}")
        print(f"    h_frac: {np.mean([r['h_frac'] for r in body_records]):.3f}")
        print(f"    e_frac: {np.mean([r['e_frac'] for r in body_records]):.3f}")
        print(f"    compound_frac: {np.mean([r['compound_frac'] for r in body_records]):.3f}")
        print(f"    E: {np.mean([r['energy'] for r in body_records]):+.5f}")

    # Step 9: Verdict
    print("\n" + "=" * 60)

    has_h_correlation = abs(rho_h) > 0.05 and p_h < 0.01
    has_e_correlation = abs(rho_e) > 0.05 and p_e < 0.01
    has_compound_effect = abs(rho_cmp) > 0.05 and p_cmp < 0.01
    # Check if h and e go in opposite directions (the C965 signature)
    has_opposing_kernels = (rho_h > 0 and rho_e < 0) or (rho_h < 0 and rho_e > 0)

    n_effects = sum([has_h_correlation, has_e_correlation,
                     has_compound_effect, has_opposing_kernels])

    if has_opposing_kernels and (has_h_correlation or has_e_correlation):
        verdict = "KERNEL_ENERGY_LINKAGE"
    elif n_effects >= 2:
        verdict = "PARTIAL_KERNEL_LINKAGE"
    elif n_effects >= 1:
        verdict = "WEAK_KERNEL_LINKAGE"
    else:
        verdict = "NO_KERNEL_LINKAGE"

    effects = []
    if has_h_correlation:
        effects.append(f"h→E (rho={rho_h:+.3f})")
    if has_e_correlation:
        effects.append(f"e→E (rho={rho_e:+.3f})")
    if has_compound_effect:
        effects.append(f"compound→E (rho={rho_cmp:+.3f})")
    if has_opposing_kernels:
        effects.append("h/e opposing")

    explanation = (
        f"Kernel effects: {'; '.join(effects) if effects else 'None significant'}. "
        f"h rho={rho_h:+.3f}, e rho={rho_e:+.3f}, k rho={rho_k:+.3f}."
    )
    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save
    results = {
        'test': 'T5_kernel_composition',
        'n_lines': len(line_records),
        'kernel_correlations': {
            'h': {'rho': float(rho_h), 'p': float(p_h)},
            'e': {'rho': float(rho_e), 'p': float(p_e)},
            'k': {'rho': float(rho_k), 'p': float(p_k)},
        },
        'h_bin_energy': h_bin_results,
        'e_bin_energy': e_bin_results,
        'compound_correlation': {
            'rho': float(rho_cmp),
            'p': float(p_cmp),
        },
        'first_vs_body': {
            'first_h_frac': float(np.mean([r['h_frac'] for r in first_records])) if first_records else None,
            'first_e_frac': float(np.mean([r['e_frac'] for r in first_records])) if first_records else None,
            'first_compound_frac': float(np.mean([r['compound_frac'] for r in first_records])) if first_records else None,
            'first_E': float(np.mean([r['energy'] for r in first_records])) if first_records else None,
            'body_h_frac': float(np.mean([r['h_frac'] for r in body_records])) if body_records else None,
            'body_e_frac': float(np.mean([r['e_frac'] for r in body_records])) if body_records else None,
            'body_compound_frac': float(np.mean([r['compound_frac'] for r in body_records])) if body_records else None,
            'body_E': float(np.mean([r['energy'] for r in body_records])) if body_records else None,
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't5_kernel_composition.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't5_kernel_composition.json'}")


if __name__ == '__main__':
    main()

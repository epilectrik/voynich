"""
T3: Cross-Bin Forbidden Anatomy
================================
Phase: HUB_ROLE_DECOMPOSITION

Maps the complete forbidden transition anatomy across ALL bins.
Tests whether HUB concentration is structural or frequency-driven.

Tests:
  3a: Full directed bin-pair matrix for all 17 forbidden transitions
  3b: Source vs target behavioral signature comparison (Mann-Whitney U)
  3c: Non-HUB bin participation rates
  3d: Permutation test (is 13/17 HUB concentration significant?)

Output: t3_cross_bin_forbidden_anatomy.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

HUB_BIN = 6
SIGNATURE_DIMS = [
    'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound',
    'qo_affinity', 'regime_1_enrichment', 'regime_2_enrichment',
    'regime_3_enrichment', 'regime_4_enrichment', 'regime_entropy',
    'initial_rate', 'final_rate', 'folio_spread',
]


def main():
    morph = Morphology()

    # ── Load affordance table ──────────────────────────────
    with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
        aff = json.load(f)

    middle_to_bin = {}
    bin_sizes = Counter()
    middle_signatures = {}
    for mid, data in aff['middles'].items():
        b = data['affordance_bin']
        middle_to_bin[mid] = b
        bin_sizes[b] += 1
        middle_signatures[mid] = data.get('behavioral_signature', {})

    bin_labels = {}
    for b, meta in aff['_metadata']['affordance_bins'].items():
        bin_labels[int(b)] = meta['label']

    # ── Load forbidden inventory ───────────────────────────
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' /
              'phase18a_forbidden_inventory.json') as f:
        inv = json.load(f)

    # ══════════════════════════════════════════════════════
    # TEST 3a: FULL DIRECTED BIN-PAIR MATRIX
    # ══════════════════════════════════════════════════════
    print(f"{'='*70}")
    print(f"T3a: FORBIDDEN TRANSITION BIN-PAIR MATRIX")
    print(f"{'='*70}")

    bin_pair_counts = Counter()
    transition_details = []
    source_middles_set = set()
    target_middles_set = set()
    all_hazard_middles = set()

    for tr in inv['transitions']:
        src_morph = morph.extract(tr['source'])
        tgt_morph = morph.extract(tr['target'])
        src_mid = src_morph.middle or ''
        tgt_mid = tgt_morph.middle or ''
        src_bin = middle_to_bin.get(src_mid, -1)
        tgt_bin = middle_to_bin.get(tgt_mid, -1)

        bin_pair_counts[(src_bin, tgt_bin)] += 1
        source_middles_set.add(src_mid)
        target_middles_set.add(tgt_mid)
        all_hazard_middles.add(src_mid)
        all_hazard_middles.add(tgt_mid)

        transition_details.append({
            'id': tr['id'],
            'source_token': tr['source'],
            'target_token': tr['target'],
            'source_middle': src_mid,
            'target_middle': tgt_mid,
            'source_bin': src_bin,
            'target_bin': tgt_bin,
            'source_bin_label': bin_labels.get(src_bin, 'UNKNOWN'),
            'target_bin_label': bin_labels.get(tgt_bin, 'UNKNOWN'),
        })

    print(f"\n  {'Source Bin':<30s} {'Target Bin':<30s} {'Count':>6s}")
    print(f"  {'-'*30} {'-'*30} {'-'*6}")
    for (sb, tb), count in sorted(bin_pair_counts.items(), key=lambda x: -x[1]):
        sl = bin_labels.get(sb, f'Bin{sb}')
        tl = bin_labels.get(tb, f'Bin{tb}')
        print(f"  {sl:<30s} {tl:<30s} {count:>6d}")

    # Count per-bin involvement
    bin_involvement = Counter()
    for (sb, tb), count in bin_pair_counts.items():
        bin_involvement[sb] += count
        bin_involvement[tb] += count

    hub_count = bin_involvement.get(HUB_BIN, 0)
    print(f"\n  HUB involvement: {hub_count}/17 transitions")
    print(f"  Unique source MIDDLEs: {len(source_middles_set)} {sorted(source_middles_set)}")
    print(f"  Unique target MIDDLEs: {len(target_middles_set)} {sorted(target_middles_set)}")
    print(f"  Total unique hazard MIDDLEs: {len(all_hazard_middles)}")

    # ══════════════════════════════════════════════════════
    # TEST 3b: SOURCE vs TARGET BEHAVIORAL SIGNATURES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3b: SOURCE vs TARGET BEHAVIORAL SIGNATURES")
    print(f"{'='*70}")

    # Get signatures for source and target MIDDLEs
    source_sigs = []
    for mid in source_middles_set:
        sig = middle_signatures.get(mid, {})
        if sig:
            source_sigs.append([sig.get(d, 0.0) for d in SIGNATURE_DIMS])
    target_sigs = []
    for mid in target_middles_set:
        sig = middle_signatures.get(mid, {})
        if sig:
            target_sigs.append([sig.get(d, 0.0) for d in SIGNATURE_DIMS])

    source_arr = np.array(source_sigs) if source_sigs else np.empty((0, len(SIGNATURE_DIMS)))
    target_arr = np.array(target_sigs) if target_sigs else np.empty((0, len(SIGNATURE_DIMS)))

    print(f"\n  Source MIDDLEs: {source_arr.shape[0]}, "
          f"Target MIDDLEs: {target_arr.shape[0]}")
    print(f"\n  {'Dimension':<24s} {'U':>8s} {'p':>10s} {'Src mean':>10s} "
          f"{'Tgt mean':>10s} {'Delta':>8s}")
    print(f"  {'-'*24} {'-'*8} {'-'*10} {'-'*10} {'-'*10} {'-'*8}")

    source_target_comparison = {}
    for i, dim in enumerate(SIGNATURE_DIMS):
        s_vals = source_arr[:, i] if source_arr.shape[0] > 0 else np.array([])
        t_vals = target_arr[:, i] if target_arr.shape[0] > 0 else np.array([])

        if len(s_vals) >= 2 and len(t_vals) >= 2:
            U_stat, p_val = stats.mannwhitneyu(s_vals, t_vals,
                                                alternative='two-sided')
            # Effect size: r = Z / sqrt(N)
            n1, n2 = len(s_vals), len(t_vals)
            z = stats.norm.ppf(1 - p_val / 2) if p_val < 1.0 else 0.0
            effect_r = z / np.sqrt(n1 + n2) if (n1 + n2) > 0 else 0.0
        else:
            U_stat, p_val, effect_r = 0.0, 1.0, 0.0

        s_mean = float(np.mean(s_vals)) if len(s_vals) > 0 else 0.0
        t_mean = float(np.mean(t_vals)) if len(t_vals) > 0 else 0.0
        delta = s_mean - t_mean

        source_target_comparison[dim] = {
            'U': float(U_stat), 'p': float(p_val),
            'effect_r': float(effect_r),
            'source_mean': s_mean, 'target_mean': t_mean,
        }

        sig = '*' if p_val < 0.05 else ''
        print(f"  {dim:<22s} {U_stat:>8.1f} {p_val:>10.4f} "
              f"{s_mean:>10.3f} {t_mean:>10.3f} {delta:>+8.3f} {sig}")

    # ══════════════════════════════════════════════════════
    # TEST 3c: NON-HUB BIN PARTICIPATION RATES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3c: PER-BIN FORBIDDEN PARTICIPATION RATES")
    print(f"{'='*70}")

    bin_hazard_middles = defaultdict(set)
    for mid in all_hazard_middles:
        b = middle_to_bin.get(mid, -1)
        bin_hazard_middles[b].add(mid)

    print(f"\n  {'Bin':<30s} {'Size':>6s} {'Hazard':>8s} {'Rate':>8s} {'MIDDLEs'}")
    print(f"  {'-'*30} {'-'*6} {'-'*8} {'-'*8} {'-'*30}")

    participation_rates = {}
    for b in sorted(set(list(bin_sizes.keys()) + list(bin_hazard_middles.keys()))):
        label = bin_labels.get(b, f'Bin{b}')
        size = bin_sizes.get(b, 0)
        hazard_count = len(bin_hazard_middles.get(b, set()))
        rate = hazard_count / size if size > 0 else 0
        middles = sorted(bin_hazard_middles.get(b, set()))

        participation_rates[b] = {
            'label': label, 'bin_size': size,
            'hazard_middles': hazard_count,
            'participation_rate': float(rate),
            'middles': middles,
        }
        print(f"  {label:<30s} {size:>6d} {hazard_count:>8d} "
              f"{rate:>7.1%} {middles}")

    # ══════════════════════════════════════════════════════
    # TEST 3d: PERMUTATION TEST — HUB CONCENTRATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T3d: PERMUTATION TEST (HUB CONCENTRATION)")
    print(f"{'='*70}")

    # Observed: how many of 17 transitions involve HUB MIDDLEs?
    # Count transitions where source OR target MIDDLE maps to HUB
    observed_hub_transitions = 0
    for tr in transition_details:
        if tr['source_bin'] == HUB_BIN or tr['target_bin'] == HUB_BIN:
            observed_hub_transitions += 1

    print(f"\n  Observed: {observed_hub_transitions}/17 transitions "
          f"involve HUB MIDDLEs")

    # Build arrays for permutation
    all_middles_list = sorted(middle_to_bin.keys())
    all_bins_arr = np.array([middle_to_bin[m] for m in all_middles_list])
    middle_to_idx = {m: i for i, m in enumerate(all_middles_list)}

    # Get indices of hazard source and target MIDDLEs
    transition_middle_pairs = []
    for tr in transition_details:
        src_idx = middle_to_idx.get(tr['source_middle'], -1)
        tgt_idx = middle_to_idx.get(tr['target_middle'], -1)
        if src_idx >= 0 and tgt_idx >= 0:
            transition_middle_pairs.append((src_idx, tgt_idx))

    transition_pairs_arr = np.array(transition_middle_pairs)
    n_perms = 10000
    rng = np.random.default_rng(42)
    null_hub_counts = np.zeros(n_perms, dtype=int)

    # Vectorized permutation test
    for p in range(n_perms):
        perm_bins = rng.permutation(all_bins_arr)
        # Count how many transitions involve HUB under this permutation
        if len(transition_pairs_arr) > 0:
            src_bins = perm_bins[transition_pairs_arr[:, 0]]
            tgt_bins = perm_bins[transition_pairs_arr[:, 1]]
            hub_involved = np.sum((src_bins == HUB_BIN) | (tgt_bins == HUB_BIN))
            null_hub_counts[p] = hub_involved

    null_mean = float(np.mean(null_hub_counts))
    null_std = float(np.std(null_hub_counts))
    p_perm = float(np.mean(null_hub_counts >= observed_hub_transitions))

    print(f"  Null distribution: mean={null_mean:.2f}, std={null_std:.2f}")
    print(f"  p-value (obs >= {observed_hub_transitions}): {p_perm:.4f}")

    if p_perm < 0.001:
        concentration_verdict = 'HUB_MONOPOLY_STRUCTURAL'
        conc_detail = (f'HUB concentration ({observed_hub_transitions}/17) is '
                       f'highly significant (p={p_perm:.4f}). Not a frequency '
                       f'artifact.')
    elif p_perm < 0.05:
        concentration_verdict = 'HUB_CONCENTRATION_SIGNIFICANT'
        conc_detail = (f'HUB concentration is significant (p={p_perm:.4f}) '
                       f'but not extreme.')
    else:
        concentration_verdict = 'HUB_MONOPOLY_FREQUENCY_ARTIFACT'
        conc_detail = (f'HUB concentration (p={p_perm:.4f}) is explained by '
                       f'frequency — HUB MIDDLEs are the most common, so '
                       f'random assignment would produce similar concentration.')

    print(f"\n  Verdict: {concentration_verdict}")
    print(f"  {conc_detail}")

    # ── Overall summary ────────────────────────────────────
    sig_dims_src_tgt = sum(1 for d in source_target_comparison.values()
                           if d['p'] < 0.05)

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Bin-pair matrix: {len(bin_pair_counts)} unique pairs")
    print(f"  Source vs target: {sig_dims_src_tgt}/{len(SIGNATURE_DIMS)} "
          f"dimensions significant")
    print(f"  Concentration: {concentration_verdict}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'HUB_ROLE_DECOMPOSITION',
            'test': 'T3_CROSS_BIN_FORBIDDEN_ANATOMY',
        },
        'bin_pair_matrix': {
            f"({sb},{tb})": count
            for (sb, tb), count in sorted(bin_pair_counts.items(),
                                          key=lambda x: -x[1])
        },
        'transition_details': transition_details,
        'source_middles': sorted(source_middles_set),
        'target_middles': sorted(target_middles_set),
        'all_hazard_middles': sorted(all_hazard_middles),
        'source_target_comparison': source_target_comparison,
        'participation_rates': {
            str(b): v for b, v in participation_rates.items()
        },
        'permutation_test': {
            'observed_hub_transitions': observed_hub_transitions,
            'n_permutations': n_perms,
            'null_mean': null_mean,
            'null_std': null_std,
            'p_value': p_perm,
        },
        'concentration_verdict': concentration_verdict,
        'concentration_detail': conc_detail,
    }

    out_path = RESULTS_DIR / 't3_cross_bin_forbidden_anatomy.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()

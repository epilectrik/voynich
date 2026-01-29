"""
PP_LINE_LEVEL_STRUCTURE - Script 4: PREFIX Residual Tests (T10-T11)

T10: PREFIX residual after MIDDLE conditioning.
     Does PREFIX clustering exist BEYOND what MIDDLE composition predicts?

T11: Adjacent-line PREFIX vs MIDDLE decomposition.
     Do adjacent lines share PREFIXes independently of sharing MIDDLEs?

Phase: PP_LINE_LEVEL_STRUCTURE
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_PERM = 1000
rng = np.random.RandomState(42)


def load_data():
    """Pre-compute per-folio, per-line PP structures."""
    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    folio_line_pp = {}  # folio -> [[(prefix, middle, suffix, word), ...], ...]

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        lines = []
        for rec in records:
            tokens = []
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    tokens.append((t.prefix, t.middle, t.suffix, t.word))
            lines.append(tokens)
        folio_line_pp[fol] = lines

    return folios, folio_line_pp


def build_folio_prefix_given_middle(folio_line_pp):
    """For each folio, compute P(prefix | middle) from all PP tokens."""
    folio_pgm = {}  # folio -> {middle -> {prefix -> probability}}

    for fol, lines in folio_line_pp.items():
        mid_prefix_counts = defaultdict(Counter)
        for line_tokens in lines:
            for (pref, mid, suf, word) in line_tokens:
                p = pref if pref else '_NONE_'
                mid_prefix_counts[mid][p] += 1

        pgm = {}
        for mid, pcounts in mid_prefix_counts.items():
            total = sum(pcounts.values())
            pgm[mid] = {p: c / total for p, c in pcounts.items()}
        folio_pgm[fol] = pgm

    return folio_pgm


def test_T10(folios, folio_line_pp):
    """T10: PREFIX Residual After MIDDLE Conditioning.

    For each line, predict PREFIX distribution from MIDDLE composition
    using folio-level P(prefix | middle). Measure whether observed PREFIX
    distribution deviates from prediction.
    """
    print("=== T10: PREFIX Residual After MIDDLE Conditioning ===")

    folio_pgm = build_folio_prefix_given_middle(folio_line_pp)

    # For each line with 2+ PP tokens:
    # 1. Observed PREFIX counts
    # 2. Expected PREFIX counts from sum of P(prefix | middle_i) for each token
    # 3. Compute PREFIX concentration: fraction of tokens sharing the modal PREFIX
    # 4. Compare observed concentration to expected concentration

    obs_concentrations = []
    exp_concentrations = []
    residuals = []
    lines_used = 0

    for fol, lines in folio_line_pp.items():
        pgm = folio_pgm[fol]
        for line_tokens in lines:
            if len(line_tokens) < 2:
                continue
            lines_used += 1

            # Observed PREFIX distribution
            obs_prefixes = [p if p else '_NONE_' for (p, m, s, w) in line_tokens]
            obs_counts = Counter(obs_prefixes)
            n = len(obs_prefixes)
            obs_modal_frac = max(obs_counts.values()) / n

            # Expected: for each token position, P(prefix | middle_i)
            # Expected modal fraction: probability that all tokens share the
            # most likely common prefix
            # Simpler metric: expected Herfindahl index (sum of squared prefix shares)
            # vs observed Herfindahl

            # Observed Herfindahl (PREFIX concentration)
            obs_herf = sum((c / n) ** 2 for c in obs_counts.values())

            # Expected Herfindahl from MIDDLE composition:
            # For each prefix p: E[share(p)] = (1/n) * sum_i P(p | middle_i)
            # E[Herfindahl] = sum_p E[share(p)]^2
            # But this is the expectation of the MEAN, not mean of squares.
            # Better: simulate expected by sampling from P(prefix | middle_i)

            # Monte Carlo expected Herfindahl (100 samples)
            mc_herfs = []
            for _ in range(100):
                sampled_prefixes = []
                for (pref, mid, suf, word) in line_tokens:
                    if mid in pgm:
                        probs = pgm[mid]
                        prefixes = list(probs.keys())
                        weights = list(probs.values())
                        chosen = rng.choice(prefixes, p=weights)
                        sampled_prefixes.append(chosen)
                    else:
                        sampled_prefixes.append(pref if pref else '_NONE_')
                sc = Counter(sampled_prefixes)
                mc_herfs.append(sum((c / n) ** 2 for c in sc.values()))

            exp_herf = float(np.mean(mc_herfs))

            obs_concentrations.append(obs_herf)
            exp_concentrations.append(exp_herf)
            residuals.append(obs_herf - exp_herf)

    obs_concentrations = np.array(obs_concentrations)
    exp_concentrations = np.array(exp_concentrations)
    residuals = np.array(residuals)

    mean_obs = float(np.mean(obs_concentrations))
    mean_exp = float(np.mean(exp_concentrations))
    mean_residual = float(np.mean(residuals))
    std_residual = float(np.std(residuals))

    print(f"Lines analyzed: {lines_used}")
    print(f"Mean observed PREFIX Herfindahl: {mean_obs:.4f}")
    print(f"Mean expected PREFIX Herfindahl (from MIDDLE): {mean_exp:.4f}")
    print(f"Mean residual (obs - exp): {mean_residual:.4f}")
    print(f"SD residual: {std_residual:.4f}")

    # Bootstrap CI for mean residual
    n_boot = 5000
    boot_means = []
    for _ in range(n_boot):
        sample = rng.choice(residuals, size=len(residuals), replace=True)
        boot_means.append(float(np.mean(sample)))
    boot_means = np.array(boot_means)
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    ci_excludes_zero = ci_lower > 0 or ci_upper < 0

    effect_size = abs(mean_residual) / std_residual if std_residual > 0 else 0

    print(f"Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"CI excludes zero: {ci_excludes_zero}")
    print(f"Effect size: {effect_size:.4f}")
    print(f"Direction: {'MORE concentrated' if mean_residual > 0 else 'LESS concentrated'} than MIDDLE predicts")

    # Permutation test: shuffle PREFIX assignments within folio,
    # conditioned on MIDDLE (for each MIDDLE, shuffle its prefix assignments)
    null_residuals = []
    for i in range(N_PERM):
        perm_residuals = []
        for fol, lines in folio_line_pp.items():
            pgm = folio_pgm[fol]

            # Build MIDDLE -> list of observed prefixes across folio
            mid_prefixes = defaultdict(list)
            for line_tokens in lines:
                for (pref, mid, suf, word) in line_tokens:
                    p = pref if pref else '_NONE_'
                    mid_prefixes[mid].append(p)

            # Shuffle prefixes within each MIDDLE
            mid_pref_shuffled = {}
            for mid, prefs in mid_prefixes.items():
                shuffled = list(prefs)
                rng.shuffle(shuffled)
                mid_pref_shuffled[mid] = iter(shuffled)

            # Reconstruct lines with shuffled prefixes
            for line_tokens in lines:
                if len(line_tokens) < 2:
                    continue
                n = len(line_tokens)
                shuffled_prefs = []
                for (pref, mid, suf, word) in line_tokens:
                    shuffled_prefs.append(next(mid_pref_shuffled[mid]))

                sc = Counter(shuffled_prefs)
                perm_herf = sum((c / n) ** 2 for c in sc.values())

                # Expected is same (MIDDLE composition unchanged)
                # So we just collect the shuffled Herfindahl
                perm_residuals.append(perm_herf)

        # Compare: mean shuffled Herfindahl vs mean observed
        null_residuals.append(float(np.mean(perm_residuals)))
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_residuals = np.array(null_residuals)
    p_concentration = float(np.mean(null_residuals >= mean_obs))

    print(f"\nObserved mean Herfindahl: {mean_obs:.4f}")
    print(f"Null mean Herfindahl (PREFIX shuffled within MIDDLE): {np.mean(null_residuals):.4f} +/- {np.std(null_residuals):.4f}")
    print(f"p (observed >= null): {p_concentration:.4f}")

    t10_pass = ci_excludes_zero and p_concentration < 0.01

    # Decompose: what fraction of observed concentration is explained by MIDDLE?
    total_concentration = mean_obs
    middle_explained = mean_exp
    residual_concentration = mean_residual
    pct_explained = (middle_explained / total_concentration * 100) if total_concentration > 0 else 0
    pct_residual = (residual_concentration / total_concentration * 100) if total_concentration > 0 else 0

    print(f"\nDecomposition:")
    print(f"  Total PREFIX concentration: {total_concentration:.4f}")
    print(f"  MIDDLE-explained: {middle_explained:.4f} ({pct_explained:.1f}%)")
    print(f"  Residual (independent): {residual_concentration:.4f} ({pct_residual:.1f}%)")

    result = {
        'test': 'T10_prefix_residual',
        'lines_analyzed': lines_used,
        'mean_observed_herfindahl': mean_obs,
        'mean_expected_herfindahl': mean_exp,
        'mean_residual': mean_residual,
        'std_residual': std_residual,
        'bootstrap_CI_95': [ci_lower, ci_upper],
        'CI_excludes_zero': ci_excludes_zero,
        'effect_size': effect_size,
        'direction': 'MORE_CONCENTRATED' if mean_residual > 0 else 'LESS_CONCENTRATED',
        'null_herfindahl_mean': float(np.mean(null_residuals)),
        'null_herfindahl_std': float(np.std(null_residuals)),
        'p_concentration': p_concentration,
        'pct_middle_explained': pct_explained,
        'pct_residual': pct_residual,
        'PASS': t10_pass,
        'verdict': 'PASS' if t10_pass else 'FAIL'
    }

    print(f"\nT10 verdict: {'PASS' if t10_pass else 'FAIL'}")
    return result


def test_T11(folios, folio_line_pp):
    """T11: Adjacent-Line PREFIX vs MIDDLE Decomposition.

    Decompose C731's adjacent-line similarity into:
    - MIDDLE sharing (do adjacent lines use the same MIDDLEs?)
    - PREFIX sharing (do adjacent lines use the same PREFIXes?)
    - Conditional: given shared MIDDLEs, do they carry the same PREFIX?
    """
    print("\n=== T11: Adjacent-Line PREFIX vs MIDDLE Decomposition ===")

    # For each pair of lines (adjacent and non-adjacent):
    # 1. MIDDLE Jaccard
    # 2. PREFIX Jaccard (set of prefixes used)
    # 3. Among shared MIDDLEs: PREFIX match rate

    adj_mid_jacc = []
    adj_pref_jacc = []
    adj_pref_match = []  # among shared MIDDLEs, do they carry same PREFIX?

    nonadj_mid_jacc = []
    nonadj_pref_jacc = []
    nonadj_pref_match = []

    for fol, lines in folio_line_pp.items():
        n = len(lines)
        if n < 2:
            continue

        # Pre-compute per-line sets and maps
        line_mid_sets = []
        line_pref_sets = []
        line_mid_to_pref = []  # middle -> set of prefixes on that line

        for line_tokens in lines:
            mids = set()
            prefs = set()
            m2p = defaultdict(set)
            for (pref, mid, suf, word) in line_tokens:
                mids.add(mid)
                p = pref if pref else '_NONE_'
                prefs.add(p)
                m2p[mid].add(p)
            line_mid_sets.append(mids)
            line_pref_sets.append(prefs)
            line_mid_to_pref.append(m2p)

        for i in range(n):
            if not line_mid_sets[i]:
                continue
            for j in range(i + 1, n):
                if not line_mid_sets[j]:
                    continue

                # MIDDLE Jaccard
                m_inter = len(line_mid_sets[i] & line_mid_sets[j])
                m_union = len(line_mid_sets[i] | line_mid_sets[j])
                m_jacc = m_inter / m_union if m_union > 0 else 0

                # PREFIX Jaccard
                p_inter = len(line_pref_sets[i] & line_pref_sets[j])
                p_union = len(line_pref_sets[i] | line_pref_sets[j])
                p_jacc = p_inter / p_union if p_union > 0 else 0

                # Among shared MIDDLEs: PREFIX match rate
                shared_mids = line_mid_sets[i] & line_mid_sets[j]
                if shared_mids:
                    matches = 0
                    total = 0
                    for mid in shared_mids:
                        prefs_i = line_mid_to_pref[i][mid]
                        prefs_j = line_mid_to_pref[j][mid]
                        # Do they share at least one prefix for this MIDDLE?
                        if prefs_i & prefs_j:
                            matches += 1
                        total += 1
                    pref_match = matches / total if total > 0 else 0
                else:
                    pref_match = None  # no shared MIDDLEs

                is_adj = (j == i + 1)
                if is_adj:
                    adj_mid_jacc.append(m_jacc)
                    adj_pref_jacc.append(p_jacc)
                    if pref_match is not None:
                        adj_pref_match.append(pref_match)
                else:
                    nonadj_mid_jacc.append(m_jacc)
                    nonadj_pref_jacc.append(p_jacc)
                    if pref_match is not None:
                        nonadj_pref_match.append(pref_match)

    # Results
    adj_mid_mean = float(np.mean(adj_mid_jacc))
    nonadj_mid_mean = float(np.mean(nonadj_mid_jacc))
    mid_ratio = adj_mid_mean / nonadj_mid_mean if nonadj_mid_mean > 0 else 0

    adj_pref_mean = float(np.mean(adj_pref_jacc))
    nonadj_pref_mean = float(np.mean(nonadj_pref_jacc))
    pref_ratio = adj_pref_mean / nonadj_pref_mean if nonadj_pref_mean > 0 else 0

    adj_match_mean = float(np.mean(adj_pref_match)) if adj_pref_match else 0
    nonadj_match_mean = float(np.mean(nonadj_pref_match)) if nonadj_pref_match else 0
    match_ratio = adj_match_mean / nonadj_match_mean if nonadj_match_mean > 0 else 0

    print(f"Adjacent pairs: {len(adj_mid_jacc)}")
    print(f"Non-adjacent pairs: {len(nonadj_mid_jacc)}")
    print(f"\nMIDDLE Jaccard:")
    print(f"  Adjacent: {adj_mid_mean:.4f}")
    print(f"  Non-adjacent: {nonadj_mid_mean:.4f}")
    print(f"  Ratio: {mid_ratio:.4f}")
    print(f"\nPREFIX Jaccard:")
    print(f"  Adjacent: {adj_pref_mean:.4f}")
    print(f"  Non-adjacent: {nonadj_pref_mean:.4f}")
    print(f"  Ratio: {pref_ratio:.4f}")
    print(f"\nShared-MIDDLE PREFIX match rate:")
    print(f"  Adjacent (n={len(adj_pref_match)}): {adj_match_mean:.4f}")
    print(f"  Non-adjacent (n={len(nonadj_pref_match)}): {nonadj_match_mean:.4f}")
    print(f"  Ratio: {match_ratio:.4f}")

    # Permutation test for PREFIX ratio: shuffle line order within folio
    null_pref_ratios = []
    null_match_ratios = []
    for i in range(N_PERM):
        perm_adj_pref = []
        perm_nonadj_pref = []
        perm_adj_match = []
        perm_nonadj_match = []

        for fol, lines in folio_line_pp.items():
            n = len(lines)
            if n < 2:
                continue

            perm_order = rng.permutation(n)

            # Recompute with shuffled order
            shuf_mid_sets = [line_mid_sets_cache[fol][idx] for idx in perm_order] \
                if fol in line_mid_sets_cache else []
            shuf_pref_sets = [line_pref_sets_cache[fol][idx] for idx in perm_order] \
                if fol in line_pref_sets_cache else []
            shuf_m2p = [line_m2p_cache[fol][idx] for idx in perm_order] \
                if fol in line_m2p_cache else []

            for ii in range(n):
                if not shuf_mid_sets[ii]:
                    continue
                for jj in range(ii + 1, n):
                    if not shuf_mid_sets[jj]:
                        continue

                    p_inter = len(shuf_pref_sets[ii] & shuf_pref_sets[jj])
                    p_union = len(shuf_pref_sets[ii] | shuf_pref_sets[jj])
                    p_jacc = p_inter / p_union if p_union > 0 else 0

                    shared = shuf_mid_sets[ii] & shuf_mid_sets[jj]
                    if shared:
                        m_count = 0
                        m_total = 0
                        for mid in shared:
                            if shuf_m2p[ii][mid] & shuf_m2p[jj][mid]:
                                m_count += 1
                            m_total += 1
                        pm = m_count / m_total if m_total > 0 else 0
                    else:
                        pm = None

                    if jj == ii + 1:
                        perm_adj_pref.append(p_jacc)
                        if pm is not None:
                            perm_adj_match.append(pm)
                    else:
                        perm_nonadj_pref.append(p_jacc)
                        if pm is not None:
                            perm_nonadj_match.append(pm)

        pa = float(np.mean(perm_adj_pref)) if perm_adj_pref else 0
        pna = float(np.mean(perm_nonadj_pref)) if perm_nonadj_pref else 0
        null_pref_ratios.append(pa / pna if pna > 0 else 0)

        pam = float(np.mean(perm_adj_match)) if perm_adj_match else 0
        pnam = float(np.mean(perm_nonadj_match)) if perm_nonadj_match else 0
        null_match_ratios.append(pam / pnam if pnam > 0 else 0)

        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_pref_ratios = np.array(null_pref_ratios)
    null_match_ratios = np.array(null_match_ratios)

    p_pref_ratio = float(np.mean(null_pref_ratios >= pref_ratio))
    p_match_ratio = float(np.mean(null_match_ratios >= match_ratio))

    print(f"\nPREFIX Jaccard ratio null: {np.mean(null_pref_ratios):.4f} +/- {np.std(null_pref_ratios):.4f}")
    print(f"p (PREFIX ratio): {p_pref_ratio:.4f}")
    print(f"PREFIX match ratio null: {np.mean(null_match_ratios):.4f} +/- {np.std(null_match_ratios):.4f}")
    print(f"p (match ratio): {p_match_ratio:.4f}")

    # The key diagnostic question:
    # Is PREFIX ratio > MIDDLE ratio? (PREFIX more adjacent-similar than MIDDLE)
    # Is PREFIX ratio < MIDDLE ratio? (PREFIX less adjacent-similar than MIDDLE)
    # Are they equal? (PREFIX follows MIDDLE, no independence)

    print(f"\n--- Diagnostic ---")
    print(f"MIDDLE adj/nonadj ratio: {mid_ratio:.4f}")
    print(f"PREFIX adj/nonadj ratio: {pref_ratio:.4f}")
    if pref_ratio > mid_ratio * 1.05:
        diag = "PREFIX_MORE_ADJACENT"
        print("PREFIX shows MORE adjacency enrichment than MIDDLE")
        print("-> PREFIX has independent adjacent-line continuity")
    elif pref_ratio < mid_ratio * 0.95:
        diag = "PREFIX_LESS_ADJACENT"
        print("PREFIX shows LESS adjacency enrichment than MIDDLE")
        print("-> Adjacent lines share content but vary in mode")
    else:
        diag = "PREFIX_TRACKS_MIDDLE"
        print("PREFIX adjacency tracks MIDDLE adjacency")
        print("-> PREFIX follows MIDDLE, no independent signal")

    t11_pass = p_pref_ratio < 0.05

    result = {
        'test': 'T11_adjacent_prefix_decomposition',
        'adjacent_pairs': len(adj_mid_jacc),
        'nonadjacent_pairs': len(nonadj_mid_jacc),
        'middle_jaccard_adj': adj_mid_mean,
        'middle_jaccard_nonadj': nonadj_mid_mean,
        'middle_ratio': mid_ratio,
        'prefix_jaccard_adj': adj_pref_mean,
        'prefix_jaccard_nonadj': nonadj_pref_mean,
        'prefix_ratio': pref_ratio,
        'shared_mid_prefix_match_adj': adj_match_mean,
        'shared_mid_prefix_match_nonadj': nonadj_match_mean,
        'match_ratio': match_ratio,
        'null_prefix_ratio_mean': float(np.mean(null_pref_ratios)),
        'null_prefix_ratio_std': float(np.std(null_pref_ratios)),
        'p_prefix_ratio': p_pref_ratio,
        'null_match_ratio_mean': float(np.mean(null_match_ratios)),
        'null_match_ratio_std': float(np.std(null_match_ratios)),
        'p_match_ratio': p_match_ratio,
        'diagnostic': diag,
        'PASS': t11_pass,
        'verdict': 'PASS' if t11_pass else 'FAIL'
    }

    print(f"\nT11 verdict: {'PASS' if t11_pass else 'FAIL'}")
    return result


def main():
    print("PP_LINE_LEVEL_STRUCTURE - Script 4: PREFIX Residual Tests")
    print("=" * 60)

    print("\nLoading data...")
    folios, folio_line_pp = load_data()

    # Pre-cache line-level sets for T11 permutation
    global line_mid_sets_cache, line_pref_sets_cache, line_m2p_cache
    line_mid_sets_cache = {}
    line_pref_sets_cache = {}
    line_m2p_cache = {}

    for fol, lines in folio_line_pp.items():
        mid_sets = []
        pref_sets = []
        m2ps = []
        for line_tokens in lines:
            mids = set()
            prefs = set()
            m2p = defaultdict(set)
            for (pref, mid, suf, word) in line_tokens:
                mids.add(mid)
                p = pref if pref else '_NONE_'
                prefs.add(p)
                m2p[mid].add(p)
            mid_sets.append(mids)
            pref_sets.append(prefs)
            m2ps.append(m2p)
        line_mid_sets_cache[fol] = mid_sets
        line_pref_sets_cache[fol] = pref_sets
        line_m2p_cache[fol] = m2ps

    results = {}

    # T10: PREFIX residual after MIDDLE conditioning
    results['T10_prefix_residual'] = test_T10(folios, folio_line_pp)

    # T11: Adjacent-line PREFIX vs MIDDLE decomposition
    results['T11_adjacent_prefix_decomposition'] = test_T11(folios, folio_line_pp)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key in ['T10_prefix_residual', 'T11_adjacent_prefix_decomposition']:
        r = results[key]
        print(f"  {key}: {r['verdict']}")

    t10 = results['T10_prefix_residual']
    t11 = results['T11_adjacent_prefix_decomposition']

    print(f"\n--- Interpretation ---")
    if t10['PASS']:
        print("T10 PASS: PREFIX clustering is NOT fully explained by MIDDLE composition.")
        print(f"  MIDDLE explains {t10['pct_middle_explained']:.1f}% of PREFIX concentration.")
        print(f"  Residual independent PREFIX coordination: {t10['pct_residual']:.1f}%.")
        print("  -> PREFIX IS an independent line-level dimension.")
    else:
        print("T10 FAIL: PREFIX clustering IS explained by MIDDLE composition.")
        print("  -> PREFIX is a byproduct of MIDDLE selection, not independent.")

    if t11['PASS']:
        print(f"T11 PASS: Adjacent lines share PREFIXes beyond line-order expectation.")
        print(f"  Diagnostic: {t11['diagnostic']}")
    else:
        print(f"T11 FAIL: Adjacent-line PREFIX sharing is not significant.")

    # Save
    output_path = RESULTS_DIR / 'pp_prefix_residual_tests.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()

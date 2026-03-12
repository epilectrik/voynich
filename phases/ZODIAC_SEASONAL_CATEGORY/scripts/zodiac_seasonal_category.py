"""
Phase 583: ZODIAC_SEASONAL_CATEGORY — Seasonal Category Clustering Test

Does AZC zodiac page vocabulary cluster by season when classified into
operational categories? If zodiac pages encode seasonal apparatus-configuration
legality gates (motivated by Brunschwig 1512 zodiac-conditional instructions),
then THERMAL/CONTAINMENT categories should show seasonal variation because
environmental conditions physically constrain which apparatus configurations
are viable.

Null hypothesis: Category profiles uniform across zodiac pages.
Alternative: Local vocabulary variation (C472) carries seasonal signal,
especially in THERMAL and CONTAINMENT categories.

Tests:
  Step 0: Data assembly (per-folio and per-season category profiles)
  Step 1: Season-level chi-squared (4x8 contingency)
  Step 2: Permutation test on seasonal labels (10,000 shuffles)
  Step 3: Per-category seasonal gradient (Kruskal-Wallis)
  Step 4: Pairwise Jensen-Shannon divergence (seasonal gradient structure)
  Step 5: Within-season vs between-season coherence (Mann-Whitney U)

References: C322, C431, C472, C1250
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "ZODIAC_SEASONAL_CATEGORY" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 10_000
SEED = 42

# ================================================================
# ZODIAC FOLIO MAP (from phases/ZOD_zodiac_analysis)
# ================================================================
ZODIAC_FOLIO_MAP = {
    'f70r1': 'Pisces', 'f70r2': 'Pisces', 'f70v1': 'Pisces',
    'f70v2': 'Aries', 'f71r': 'Taurus', 'f71v': 'Taurus',
    'f72r1': 'Gemini', 'f72r2': 'Cancer', 'f72r3': 'Leo',
    'f72v1': 'Virgo', 'f72v2': 'Libra', 'f72v3': 'Scorpio',
    'f73r': 'Sagittarius', 'f73v': 'Capricorn',
}

# Seasonal grouping (astronomical seasons, Northern Hemisphere)
SIGN_TO_SEASON = {
    'Pisces': 'Spring', 'Aries': 'Spring', 'Taurus': 'Spring',
    'Gemini': 'Summer', 'Cancer': 'Summer', 'Leo': 'Summer',
    'Virgo': 'Autumn', 'Libra': 'Autumn', 'Scorpio': 'Autumn',
    'Sagittarius': 'Winter', 'Capricorn': 'Winter',
}

FOLIO_TO_SEASON = {f: SIGN_TO_SEASON[s] for f, s in ZODIAC_FOLIO_MAP.items()}

SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter']
CATEGORIES = list(CategoryClassifier.CATEGORIES)

# ================================================================
# STEP 0: DATA ASSEMBLY
# ================================================================
def assemble_data():
    """Load AZC tokens from zodiac folios, classify MIDDLEs into categories."""
    t0 = time.time()
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Per-folio category counts
    folio_cat_counts = {f: Counter() for f in ZODIAC_FOLIO_MAP}
    folio_token_counts = {f: 0 for f in ZODIAC_FOLIO_MAP}
    folio_classified = {f: 0 for f in ZODIAC_FOLIO_MAP}
    folio_unclassified = {f: 0 for f in ZODIAC_FOLIO_MAP}

    zodiac_folios = set(ZODIAC_FOLIO_MAP.keys())

    for token in tx.azc():
        if token.folio not in zodiac_folios:
            continue
        if token.is_uncertain:
            continue

        folio = token.folio
        folio_token_counts[folio] += 1

        m = morph.extract(token.word)
        if not m.middle:
            folio_unclassified[folio] += 1
            continue

        cat = cc.classify(m.middle)
        if cat:
            folio_cat_counts[folio][cat] += 1
            folio_classified[folio] += 1
        else:
            folio_unclassified[folio] += 1

    # Build per-season aggregated counts
    season_cat_counts = {s: Counter() for s in SEASONS}
    for folio, counts in folio_cat_counts.items():
        season = FOLIO_TO_SEASON[folio]
        season_cat_counts[season] += counts

    elapsed = time.time() - t0

    # Report
    total_tokens = sum(folio_token_counts.values())
    total_classified = sum(folio_classified.values())
    total_unclassified = sum(folio_unclassified.values())

    print("=" * 70)
    print("STEP 0: DATA ASSEMBLY")
    print("=" * 70)
    print(f"\nTotal zodiac folio tokens (H-track, AZC, non-uncertain): {total_tokens}")
    print(f"Classified into categories: {total_classified} ({100*total_classified/max(total_tokens,1):.1f}%)")
    print(f"Unclassified (no MIDDLE or no category): {total_unclassified} ({100*total_unclassified/max(total_tokens,1):.1f}%)")
    print(f"\nPer-folio breakdown:")
    for f in sorted(ZODIAC_FOLIO_MAP.keys()):
        sign = ZODIAC_FOLIO_MAP[f]
        season = FOLIO_TO_SEASON[f]
        n = folio_token_counts[f]
        c = folio_classified[f]
        print(f"  {f:8s} ({sign:12s}, {season:6s}): {n:4d} tokens, {c:4d} classified")

    print(f"\nPer-season aggregated:")
    for s in SEASONS:
        total_s = sum(season_cat_counts[s].values())
        print(f"  {s:6s}: {total_s:4d} classified tokens")
        for cat in CATEGORIES:
            cnt = season_cat_counts[s].get(cat, 0)
            pct = 100 * cnt / max(total_s, 1)
            print(f"    {cat:14s}: {cnt:4d} ({pct:5.1f}%)")

    print(f"\nData assembly: {elapsed:.2f}s")

    return folio_cat_counts, season_cat_counts, folio_token_counts


# ================================================================
# STEP 1: SEASON-LEVEL CHI-SQUARED
# ================================================================
def step1_chi_squared(season_cat_counts):
    """4x8 contingency table: seasons x categories. Chi-squared + Cramer's V."""
    print("\n" + "=" * 70)
    print("STEP 1: SEASON-LEVEL CHI-SQUARED")
    print("=" * 70)

    # Build contingency table
    table = np.zeros((len(SEASONS), len(CATEGORIES)), dtype=int)
    for i, s in enumerate(SEASONS):
        for j, cat in enumerate(CATEGORIES):
            table[i, j] = season_cat_counts[s].get(cat, 0)

    print("\nContingency table (seasons x categories):")
    header = f"{'':10s}" + "".join(f"{cat[:6]:>8s}" for cat in CATEGORIES)
    print(header)
    for i, s in enumerate(SEASONS):
        row = f"{s:10s}" + "".join(f"{table[i, j]:8d}" for j in range(len(CATEGORIES)))
        print(row)

    # Chi-squared test
    chi2, p, dof, expected = sp_stats.chi2_contingency(table)
    n_total = table.sum()
    k = min(table.shape)
    cramers_v = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 else 0

    print(f"\nChi-squared = {chi2:.3f}, dof = {dof}, p = {p:.6f}")
    print(f"Cramer's V = {cramers_v:.4f}")
    print(f"N = {n_total}")

    sig = p < 0.05
    meaningful = cramers_v > 0.1
    verdict = "SIGNIFICANT" if sig else "NOT SIGNIFICANT"
    if sig and meaningful:
        verdict += " + MEANINGFUL (V > 0.1)"
    elif sig:
        verdict += " but SMALL EFFECT (V <= 0.1)"

    print(f"Verdict: {verdict}")

    return {
        'chi2': float(chi2), 'p': float(p), 'dof': int(dof),
        'cramers_v': float(cramers_v), 'n': int(n_total),
        'significant': bool(sig), 'meaningful_effect': bool(meaningful),
        'table': table.tolist(),
    }


# ================================================================
# STEP 2: PERMUTATION TEST
# ================================================================
def step2_permutation(folio_cat_counts, observed_chi2):
    """Shuffle season labels across folios (10,000 permutations)."""
    print("\n" + "=" * 70)
    print("STEP 2: PERMUTATION TEST (season label shuffle)")
    print("=" * 70)

    rng = np.random.default_rng(SEED)
    folios = sorted(ZODIAC_FOLIO_MAP.keys())
    season_labels = [FOLIO_TO_SEASON[f] for f in folios]

    # Pre-compute per-folio category vectors
    folio_vectors = {}
    for f in folios:
        vec = np.array([folio_cat_counts[f].get(cat, 0) for cat in CATEGORIES])
        folio_vectors[f] = vec

    n_ge = 0
    perm_chi2s = []

    for perm_i in range(N_PERM):
        # Shuffle season assignments
        shuffled = list(season_labels)
        rng.shuffle(shuffled)

        # Build shuffled season contingency table
        perm_season_counts = {s: np.zeros(len(CATEGORIES)) for s in SEASONS}
        for f_idx, f in enumerate(folios):
            s = shuffled[f_idx]
            perm_season_counts[s] += folio_vectors[f]

        table = np.array([perm_season_counts[s] for s in SEASONS])

        # Skip if any row or column is all zeros (chi2 undefined)
        if np.any(table.sum(axis=1) == 0) or np.any(table.sum(axis=0) == 0):
            continue

        try:
            chi2, _, _, _ = sp_stats.chi2_contingency(table)
            perm_chi2s.append(chi2)
            if chi2 >= observed_chi2:
                n_ge += 1
        except ValueError:
            continue

    valid_perms = len(perm_chi2s)
    perm_p = n_ge / max(valid_perms, 1)

    print(f"Valid permutations: {valid_perms}/{N_PERM}")
    print(f"Observed chi2: {observed_chi2:.3f}")
    print(f"Permutations >= observed: {n_ge}")
    print(f"Permutation p-value: {perm_p:.6f}")
    print(f"Verdict: {'CONFIRMED' if perm_p < 0.05 else 'NOT CONFIRMED'} by permutation")

    return {
        'observed_chi2': float(observed_chi2),
        'n_permutations': N_PERM,
        'valid_permutations': int(valid_perms),
        'n_ge_observed': int(n_ge),
        'perm_p': float(perm_p),
        'confirmed': bool(perm_p < 0.05),
        'perm_chi2_mean': float(np.mean(perm_chi2s)) if perm_chi2s else 0,
        'perm_chi2_95th': float(np.percentile(perm_chi2s, 95)) if perm_chi2s else 0,
    }


# ================================================================
# STEP 3: PER-CATEGORY SEASONAL GRADIENT
# ================================================================
def step3_per_category_gradient(folio_cat_counts):
    """For each category: proportion per folio grouped by season, Kruskal-Wallis."""
    print("\n" + "=" * 70)
    print("STEP 3: PER-CATEGORY SEASONAL GRADIENT")
    print("=" * 70)

    folios = sorted(ZODIAC_FOLIO_MAP.keys())

    # Compute per-folio proportions
    folio_totals = {}
    folio_props = {}
    for f in folios:
        total = sum(folio_cat_counts[f].values())
        folio_totals[f] = total
        folio_props[f] = {}
        for cat in CATEGORIES:
            folio_props[f][cat] = folio_cat_counts[f].get(cat, 0) / max(total, 1)

    results = {}
    print(f"\n{'Category':14s} {'H-stat':>8s} {'p-value':>10s} {'Verdict':>15s}  Season means")
    print("-" * 90)

    for cat in CATEGORIES:
        # Group folio proportions by season
        season_groups = {s: [] for s in SEASONS}
        for f in folios:
            s = FOLIO_TO_SEASON[f]
            season_groups[s].append(folio_props[f][cat])

        # Compute season means
        season_means = {s: np.mean(vals) if vals else 0 for s, vals in season_groups.items()}

        # Kruskal-Wallis (needs at least 2 groups with data)
        groups = [np.array(season_groups[s]) for s in SEASONS if len(season_groups[s]) > 0]
        if len(groups) >= 2 and all(len(g) > 0 for g in groups):
            try:
                h_stat, p_val = sp_stats.kruskal(*groups)
            except ValueError:
                h_stat, p_val = 0.0, 1.0
        else:
            h_stat, p_val = 0.0, 1.0

        sig = p_val < 0.05
        verdict = "SIGNIFICANT" if sig else "not significant"

        means_str = "  ".join(f"{s[:2]}={season_means[s]:.3f}" for s in SEASONS)
        print(f"{cat:14s} {h_stat:8.3f} {p_val:10.6f} {verdict:>15s}  {means_str}")

        results[cat] = {
            'h_stat': float(h_stat), 'p': float(p_val), 'significant': bool(sig),
            'season_means': {s: float(season_means[s]) for s in SEASONS},
            'season_values': {s: [float(v) for v in season_groups[s]] for s in SEASONS},
        }

    # Identify which categories drive the signal
    sig_cats = [cat for cat in CATEGORIES if results[cat]['significant']]
    print(f"\nSignificant categories (p < 0.05): {sig_cats if sig_cats else 'NONE'}")

    thermal_sig = results.get('THERMAL', {}).get('significant', False)
    contain_sig = results.get('CONTAINMENT', {}).get('significant', False)
    print(f"THERMAL significant: {thermal_sig}")
    print(f"CONTAINMENT significant: {contain_sig}")

    if thermal_sig or contain_sig:
        print("-> Apparatus-configuration prediction SUPPORTED (THERMAL/CONTAINMENT show seasonal gradient)")
    else:
        print("-> Apparatus-configuration prediction NOT supported by per-category test")

    return results


# ================================================================
# STEP 4: PAIRWISE JENSEN-SHANNON DIVERGENCE
# ================================================================
def step4_seasonal_jsd(season_cat_counts):
    """JSD between season category distributions. Test gradient structure."""
    print("\n" + "=" * 70)
    print("STEP 4: PAIRWISE JENSEN-SHANNON DIVERGENCE (seasons)")
    print("=" * 70)

    # Build normalized probability vectors per season
    season_probs = {}
    for s in SEASONS:
        vec = np.array([season_cat_counts[s].get(cat, 0) for cat in CATEGORIES], dtype=float)
        total = vec.sum()
        if total > 0:
            season_probs[s] = vec / total
        else:
            season_probs[s] = np.ones(len(CATEGORIES)) / len(CATEGORIES)

    # Pairwise JSD
    pairs = list(combinations(SEASONS, 2))
    jsd_values = {}
    print(f"\n{'Pair':>25s} {'JSD':>10s} {'Adjacency':>12s}")
    print("-" * 50)

    # Define adjacency (circular calendar)
    adjacent_pairs = {
        ('Spring', 'Summer'), ('Summer', 'Autumn'),
        ('Autumn', 'Winter'), ('Winter', 'Spring'),
    }

    adjacent_jsds = []
    distant_jsds = []

    for s1, s2 in pairs:
        jsd_val = float(jensenshannon(season_probs[s1], season_probs[s2]) ** 2)  # squared for JSD
        jsd_values[(s1, s2)] = jsd_val

        is_adj = (s1, s2) in adjacent_pairs or (s2, s1) in adjacent_pairs
        adj_label = "ADJACENT" if is_adj else "distant"
        print(f"{s1 + '-' + s2:>25s} {jsd_val:10.6f} {adj_label:>12s}")

        if is_adj:
            adjacent_jsds.append(jsd_val)
        else:
            distant_jsds.append(jsd_val)

    # Test: adjacent < distant? (gradient structure)
    adj_mean = np.mean(adjacent_jsds) if adjacent_jsds else 0
    dist_mean = np.mean(distant_jsds) if distant_jsds else 0
    print(f"\nAdjacent mean JSD: {adj_mean:.6f}")
    print(f"Distant mean JSD: {dist_mean:.6f}")

    if len(adjacent_jsds) >= 2 and len(distant_jsds) >= 2:
        u_stat, u_p = sp_stats.mannwhitneyu(adjacent_jsds, distant_jsds, alternative='less')
        print(f"Mann-Whitney U (adjacent < distant): U={u_stat:.1f}, p={u_p:.4f}")
        gradient = u_p < 0.05
    else:
        u_stat, u_p = 0, 1.0
        gradient = False
        print("Insufficient pairs for Mann-Whitney U test")

    print(f"Gradient structure: {'YES' if gradient else 'NO'}")

    return {
        'pairwise_jsd': {f"{s1}-{s2}": float(v) for (s1, s2), v in jsd_values.items()},
        'adjacent_mean': float(adj_mean),
        'distant_mean': float(dist_mean),
        'u_stat': float(u_stat), 'u_p': float(u_p),
        'gradient_structure': bool(gradient),
    }


# ================================================================
# STEP 5: WITHIN-SEASON vs BETWEEN-SEASON COHERENCE
# ================================================================
def step5_coherence(folio_cat_counts):
    """Compare within-season folio-pair JSD vs between-season pairs."""
    print("\n" + "=" * 70)
    print("STEP 5: WITHIN-SEASON vs BETWEEN-SEASON COHERENCE")
    print("=" * 70)

    folios = sorted(ZODIAC_FOLIO_MAP.keys())

    # Build normalized probability vectors per folio
    folio_probs = {}
    for f in folios:
        vec = np.array([folio_cat_counts[f].get(cat, 0) for cat in CATEGORIES], dtype=float)
        total = vec.sum()
        if total > 0:
            folio_probs[f] = vec / total
        else:
            folio_probs[f] = np.ones(len(CATEGORIES)) / len(CATEGORIES)

    # Compute all pairwise JSD values
    within_jsds = []
    between_jsds = []
    within_pairs = []
    between_pairs = []

    for f1, f2 in combinations(folios, 2):
        jsd_val = float(jensenshannon(folio_probs[f1], folio_probs[f2]) ** 2)
        s1 = FOLIO_TO_SEASON[f1]
        s2 = FOLIO_TO_SEASON[f2]

        if s1 == s2:
            within_jsds.append(jsd_val)
            within_pairs.append((f1, f2, jsd_val))
        else:
            between_jsds.append(jsd_val)
            between_pairs.append((f1, f2, jsd_val))

    print(f"\nWithin-season pairs: {len(within_jsds)}")
    for f1, f2, v in sorted(within_pairs, key=lambda x: x[2]):
        s = FOLIO_TO_SEASON[f1]
        print(f"  {f1:8s} - {f2:8s} ({s:6s}): JSD = {v:.6f}")

    print(f"\nBetween-season pairs: {len(between_jsds)}")
    # Just show summary statistics for between (too many pairs)
    if between_jsds:
        print(f"  Min: {min(between_jsds):.6f}, Max: {max(between_jsds):.6f}")
        print(f"  Mean: {np.mean(between_jsds):.6f}, Median: {np.median(between_jsds):.6f}")

    within_mean = np.mean(within_jsds) if within_jsds else 0
    between_mean = np.mean(between_jsds) if between_jsds else 0

    print(f"\nWithin-season mean JSD:  {within_mean:.6f}")
    print(f"Between-season mean JSD: {between_mean:.6f}")

    if len(within_jsds) >= 2 and len(between_jsds) >= 2:
        u_stat, u_p = sp_stats.mannwhitneyu(within_jsds, between_jsds, alternative='less')
        print(f"Mann-Whitney U (within < between): U={u_stat:.1f}, p={u_p:.4f}")
        coherent = u_p < 0.05
    else:
        u_stat, u_p = 0, 1.0
        coherent = False
        print("Insufficient pairs for Mann-Whitney U test")

    print(f"Within-season coherence: {'YES' if coherent else 'NO'}")

    return {
        'within_count': len(within_jsds),
        'between_count': len(between_jsds),
        'within_mean': float(within_mean),
        'between_mean': float(between_mean),
        'u_stat': float(u_stat), 'u_p': float(u_p),
        'within_coherent': bool(coherent),
        'within_pairs': [(f1, f2, float(v)) for f1, f2, v in within_pairs],
    }


# ================================================================
# MAIN
# ================================================================
def main():
    t_start = time.time()
    print("Phase 583: ZODIAC_SEASONAL_CATEGORY")
    print("Zodiac Seasonal Category Clustering Test")
    print("=" * 70)

    # Step 0: Data Assembly
    folio_cat_counts, season_cat_counts, folio_token_counts = assemble_data()

    # Step 1: Chi-squared
    chi2_results = step1_chi_squared(season_cat_counts)

    # Step 2: Permutation test
    perm_results = step2_permutation(folio_cat_counts, chi2_results['chi2'])

    # Step 3: Per-category gradient
    gradient_results = step3_per_category_gradient(folio_cat_counts)

    # Step 4: Seasonal JSD
    jsd_results = step4_seasonal_jsd(season_cat_counts)

    # Step 5: Within/between coherence
    coherence_results = step5_coherence(folio_cat_counts)

    # ============================================================
    # FINAL VERDICTS
    # ============================================================
    print("\n" + "=" * 70)
    print("FINAL VERDICTS")
    print("=" * 70)

    # C1681: SEASONAL_CATEGORY_SIGNAL
    c1675 = chi2_results['significant'] and chi2_results['meaningful_effect']
    c1675_text = (f"SEASONAL_CATEGORY_SIGNAL: chi2={chi2_results['chi2']:.3f}, "
                  f"p={chi2_results['p']:.6f}, V={chi2_results['cramers_v']:.4f}, "
                  f"perm_p={perm_results['perm_p']:.6f}")
    if c1675:
        c1675_text += " -> CONFIRMED"
    elif chi2_results['significant']:
        c1675_text += " -> SIGNIFICANT but SMALL EFFECT"
    else:
        c1675_text += " -> NOT CONFIRMED"
    print(f"\nC1681: {c1675_text}")

    # C1682: THERMAL_SEASONAL_GRADIENT
    thermal_sig = gradient_results.get('THERMAL', {}).get('significant', False)
    contain_sig = gradient_results.get('CONTAINMENT', {}).get('significant', False)
    c1676_text = (f"THERMAL_SEASONAL_GRADIENT: thermal_p={gradient_results.get('THERMAL', {}).get('p', 1):.6f}, "
                  f"containment_p={gradient_results.get('CONTAINMENT', {}).get('p', 1):.6f}")
    if thermal_sig:
        c1676_text += " -> THERMAL CONFIRMED"
    elif contain_sig:
        c1676_text += " -> CONTAINMENT CONFIRMED (not thermal)"
    else:
        c1676_text += " -> NOT CONFIRMED"
    print(f"C1682: {c1676_text}")

    # C1683: WITHIN_SEASON_COHERENCE
    c1677 = coherence_results['within_coherent']
    c1677_text = (f"WITHIN_SEASON_COHERENCE: within_mean={coherence_results['within_mean']:.6f}, "
                  f"between_mean={coherence_results['between_mean']:.6f}, "
                  f"p={coherence_results['u_p']:.6f}")
    c1677_text += " -> CONFIRMED" if c1677 else " -> NOT CONFIRMED"
    print(f"C1683: {c1677_text}")

    # C1684: APPARATUS_SEASON_COUPLING
    sig_cats = [cat for cat in CATEGORIES if gradient_results[cat]['significant']]
    c1678 = len(sig_cats) >= 2
    c1678_text = f"APPARATUS_SEASON_COUPLING: {len(sig_cats)} categories significant: {sig_cats}"
    c1678_text += " -> CONFIRMED (multi-category)" if c1678 else " -> NOT CONFIRMED"
    print(f"C1684: {c1678_text}")

    # Overall verdict
    print("\n" + "-" * 70)
    if c1675 and perm_results['confirmed'] and (thermal_sig or contain_sig):
        overall = "SEASONAL_CATEGORY_CONFIRMED"
        print(f"OVERALL: {overall}")
        print("Strong support for apparatus-configuration seasonal gating")
    elif chi2_results['significant'] and perm_results['confirmed']:
        overall = "SEASONAL_SIGNAL_PRESENT_MECHANISM_UNCLEAR"
        print(f"OVERALL: {overall}")
        print("Seasonal structure exists but THERMAL/CONTAINMENT don't drive it")
    elif chi2_results['significant']:
        overall = "SEASONAL_SIGNAL_WEAK"
        print(f"OVERALL: {overall}")
        print("Chi-squared significant but not confirmed by permutation")
    else:
        overall = "SEASONAL_CATEGORY_ABSENT"
        print(f"OVERALL: {overall}")
        print("No evidence that category composition varies by season")

    elapsed = time.time() - t_start
    print(f"\nTotal runtime: {elapsed:.2f}s")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    output = {
        'phase': 'ZODIAC_SEASONAL_CATEGORY',
        'phase_number': 583,
        'overall_verdict': overall,
        'runtime_s': round(elapsed, 2),
        'data': {
            'total_tokens': sum(folio_token_counts.values()),
            'folio_token_counts': folio_token_counts,
            'season_category_counts': {s: dict(c) for s, c in season_cat_counts.items()},
        },
        'step1_chi_squared': chi2_results,
        'step2_permutation': perm_results,
        'step3_per_category_gradient': {
            cat: {k: v for k, v in r.items() if k != 'season_values'}
            for cat, r in gradient_results.items()
        },
        'step4_seasonal_jsd': jsd_results,
        'step5_coherence': coherence_results,
        'constraints': {
            'C1681': {'claim': 'SEASONAL_CATEGORY_SIGNAL', 'confirmed': bool(c1675)},
            'C1682': {'claim': 'THERMAL_SEASONAL_GRADIENT', 'confirmed': bool(thermal_sig)},
            'C1683': {'claim': 'WITHIN_SEASON_COHERENCE', 'confirmed': bool(c1677)},
            'C1684': {'claim': 'APPARATUS_SEASON_COUPLING', 'confirmed': bool(c1678)},
        },
    }

    out_path = RESULTS_DIR / "zodiac_seasonal_category.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

"""
Phase 584: ZODIAC_ASSIGNMENT_INFERENCE — Zodiac Sign Assignment by Category Coherence

Brute-force enumeration of all 12 valid zodiac assignments for the 5
unidentified nymph folios. 7 folios are anchored by visual evidence
(Phase 583). The remaining 5 are constrained:
  - f70v1, f71r (goats): must be {Aries, Taurus} (C1684: Spring behavior)
  - f71v, f72r1, f72r3 (generic animals): must be {Cancer, Capricorn, Aquarius}

Search space: 2! x 3! = 12 assignments. Full enumeration.

References: C1681-C1684, C322, C472, C1250
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter
from itertools import permutations, combinations
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "ZODIAC_ASSIGNMENT_INFERENCE" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 10_000
SEED = 42

# ================================================================
# ANCHORS + UNKNOWNS
# ================================================================
ANCHORS = {
    'f70v2': 'Pisces',
    'f72r2': 'Gemini',
    'f72v1': 'Libra',
    'f72v3': 'Leo',
    'f72v2': 'Virgo',
    'f73r':  'Scorpio',
    'f73v':  'Sagittarius',
}

GOAT_FOLIOS = ['f70v1', 'f71r']
GOAT_SIGNS = ['Aries', 'Taurus']

UNKNOWN_FOLIOS = ['f71v', 'f72r1', 'f72r3']
UNKNOWN_SIGNS = ['Cancer', 'Capricorn', 'Aquarius']

ALL_NYMPH_FOLIOS = [
    'f70v2', 'f70v1', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
]

SIGN_TO_SEASON = {
    'Pisces': 'Spring', 'Aries': 'Spring', 'Taurus': 'Spring',
    'Gemini': 'Summer', 'Cancer': 'Summer', 'Leo': 'Summer',
    'Virgo': 'Autumn', 'Libra': 'Autumn', 'Scorpio': 'Autumn',
    'Sagittarius': 'Winter', 'Capricorn': 'Winter', 'Aquarius': 'Winter',
}

SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter']
CATEGORIES = list(CategoryClassifier.CATEGORIES)


# ================================================================
# STEP 0: PRE-COMPUTE FOLIO CATEGORY VECTORS
# ================================================================
def precompute_folio_data():
    """Load and classify all nymph-page tokens once."""
    t0 = time.time()
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    folio_cat_counts = {f: Counter() for f in ALL_NYMPH_FOLIOS}
    folio_token_counts = {f: 0 for f in ALL_NYMPH_FOLIOS}
    nymph_set = set(ALL_NYMPH_FOLIOS)

    for token in tx.azc():
        if token.folio not in nymph_set:
            continue
        if token.is_uncertain:
            continue
        folio_token_counts[token.folio] += 1
        m = morph.extract(token.word)
        if not m.middle:
            continue
        cat = cc.classify(m.middle)
        if cat:
            folio_cat_counts[token.folio][cat] += 1

    # Pre-compute numpy vectors
    folio_vectors = {}
    for f in ALL_NYMPH_FOLIOS:
        folio_vectors[f] = np.array([folio_cat_counts[f].get(cat, 0) for cat in CATEGORIES])

    total = sum(folio_token_counts.values())
    classified = sum(sum(folio_cat_counts[f].values()) for f in ALL_NYMPH_FOLIOS)
    elapsed = time.time() - t0

    print(f"Pre-computed: {total} tokens, {classified} classified ({100*classified/max(total,1):.1f}%)")
    print(f"  Elapsed: {elapsed:.2f}s")
    for f in ALL_NYMPH_FOLIOS:
        n = folio_token_counts[f]
        c = sum(folio_cat_counts[f].values())
        print(f"  {f:8s}: {n:4d} tokens, {c:4d} classified")

    return folio_cat_counts, folio_vectors, folio_token_counts


# ================================================================
# SCORING FUNCTION
# ================================================================
def score_assignment(zodiac_map, folio_vectors):
    """Compute chi-squared and Cramer's V for a given zodiac assignment."""
    # Build season contingency table
    season_vecs = {s: np.zeros(len(CATEGORIES)) for s in SEASONS}
    for f, sign in zodiac_map.items():
        season = SIGN_TO_SEASON[sign]
        season_vecs[season] += folio_vectors[f]

    table = np.array([season_vecs[s] for s in SEASONS])

    # Remove empty rows/columns
    row_sums = table.sum(axis=1)
    col_sums = table.sum(axis=0)
    nonempty_rows = row_sums > 0
    nonempty_cols = col_sums > 0
    table_clean = table[np.ix_(nonempty_rows, nonempty_cols)]

    if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
        return 0, 1.0, 0

    chi2, p, dof, _ = sp_stats.chi2_contingency(table_clean)
    n = table_clean.sum()
    k = min(table_clean.shape)
    v = np.sqrt(chi2 / (n * (k - 1))) if n > 0 else 0

    return chi2, p, v


# ================================================================
# STEP 1-2: ENUMERATE AND RANK ALL 12 ASSIGNMENTS
# ================================================================
def enumerate_assignments(folio_vectors):
    """Generate all 12 valid assignments, score and rank."""
    print("\n" + "=" * 70)
    print("STEP 1-2: ENUMERATE ALL 12 VALID ASSIGNMENTS")
    print("=" * 70)

    results = []

    for goat_perm in permutations(GOAT_SIGNS):
        for unk_perm in permutations(UNKNOWN_SIGNS):
            # Build full map
            zodiac_map = dict(ANCHORS)
            for i, f in enumerate(GOAT_FOLIOS):
                zodiac_map[f] = goat_perm[i]
            for i, f in enumerate(UNKNOWN_FOLIOS):
                zodiac_map[f] = unk_perm[i]

            chi2, p, v = score_assignment(zodiac_map, folio_vectors)

            # Build readable description
            goat_desc = f"f70v1={goat_perm[0]}, f71r={goat_perm[1]}"
            unk_desc = f"f71v={unk_perm[0]}, f72r1={unk_perm[1]}, f72r3={unk_perm[2]}"

            results.append({
                'zodiac_map': zodiac_map,
                'goat_perm': goat_perm,
                'unk_perm': unk_perm,
                'goat_desc': goat_desc,
                'unk_desc': unk_desc,
                'chi2': chi2,
                'p': p,
                'cramers_v': v,
            })

    # Sort by Cramer's V descending
    results.sort(key=lambda x: x['cramers_v'], reverse=True)

    print(f"\n{'Rank':>4s} {'V':>8s} {'chi2':>8s} {'p':>10s}  Goats                  Unknowns")
    print("-" * 100)
    for i, r in enumerate(results):
        marker = " <<<" if i == 0 else ""
        print(f"{i+1:4d} {r['cramers_v']:8.4f} {r['chi2']:8.2f} {r['p']:10.6f}  "
              f"{r['goat_desc']:<23s} {r['unk_desc']}{marker}")

    return results


# ================================================================
# STEP 3: PERMUTATION VALIDATION OF BEST ASSIGNMENT
# ================================================================
def permutation_validation(best_map, folio_vectors, observed_chi2):
    """Run 10K permutation test on the best assignment."""
    print("\n" + "=" * 70)
    print("STEP 3: PERMUTATION VALIDATION (best assignment)")
    print("=" * 70)

    rng = np.random.default_rng(SEED)
    folios = sorted(best_map.keys())
    season_labels = [SIGN_TO_SEASON[best_map[f]] for f in folios]

    n_ge = 0
    valid = 0
    perm_chi2s = []

    for _ in range(N_PERM):
        shuffled = list(season_labels)
        rng.shuffle(shuffled)

        season_vecs = {s: np.zeros(len(CATEGORIES)) for s in SEASONS}
        for idx, f in enumerate(folios):
            season_vecs[shuffled[idx]] += folio_vectors[f]

        table = np.array([season_vecs[s] for s in SEASONS])
        col_sums = table.sum(axis=0)
        row_sums = table.sum(axis=1)
        if np.any(row_sums == 0) or np.any(col_sums == 0):
            continue

        try:
            chi2, _, _, _ = sp_stats.chi2_contingency(table)
            perm_chi2s.append(chi2)
            valid += 1
            if chi2 >= observed_chi2:
                n_ge += 1
        except ValueError:
            continue

    perm_p = n_ge / max(valid, 1)
    print(f"Observed chi2: {observed_chi2:.3f}")
    print(f"Valid permutations: {valid}/{N_PERM}")
    print(f"Permutations >= observed: {n_ge}")
    print(f"Permutation p-value: {perm_p:.6f}")
    print(f"Verdict: {'CONFIRMED' if perm_p < 0.05 else 'NOT CONFIRMED'}")

    return {
        'perm_p': float(perm_p),
        'n_ge': n_ge,
        'valid': valid,
        'perm_chi2_mean': float(np.mean(perm_chi2s)) if perm_chi2s else 0,
        'perm_chi2_95th': float(np.percentile(perm_chi2s, 95)) if perm_chi2s else 0,
    }


# ================================================================
# STEP 4: SENSITIVITY ANALYSIS
# ================================================================
def sensitivity_analysis(ranked_results, folio_vectors):
    """Analyze robustness of the best assignment."""
    print("\n" + "=" * 70)
    print("STEP 4: SENSITIVITY ANALYSIS")
    print("=" * 70)

    best = ranked_results[0]
    second = ranked_results[1]
    v_gap = best['cramers_v'] - second['cramers_v']

    print(f"\n#1 V={best['cramers_v']:.4f}: {best['goat_desc']}; {best['unk_desc']}")
    print(f"#2 V={second['cramers_v']:.4f}: {second['goat_desc']}; {second['unk_desc']}")
    print(f"V gap: {v_gap:.4f} ({'ROBUST (>0.01)' if v_gap > 0.01 else 'THIN (<= 0.01)'})")

    # Goat sensitivity: average V for each goat ordering
    goat_orderings = {}
    for r in ranked_results:
        key = r['goat_perm']
        if key not in goat_orderings:
            goat_orderings[key] = []
        goat_orderings[key].append(r['cramers_v'])

    print(f"\nGoat ordering sensitivity:")
    for perm, vs in goat_orderings.items():
        mean_v = np.mean(vs)
        max_v = max(vs)
        print(f"  f70v1={perm[0]}, f71r={perm[1]}: mean V={mean_v:.4f}, max V={max_v:.4f}")

    # Unknown sensitivity: average V for each unknown ordering
    unk_orderings = {}
    for r in ranked_results:
        key = r['unk_perm']
        if key not in unk_orderings:
            unk_orderings[key] = []
        unk_orderings[key].append(r['cramers_v'])

    print(f"\nUnknown ordering sensitivity:")
    for perm, vs in sorted(unk_orderings.items(), key=lambda x: -max(x[1])):
        mean_v = np.mean(vs)
        max_v = max(vs)
        print(f"  f71v={perm[0]}, f72r1={perm[1]}, f72r3={perm[2]}: "
              f"mean V={mean_v:.4f}, max V={max_v:.4f}")

    # Within/between coherence for best assignment
    best_map = best['zodiac_map']
    folios = sorted(best_map.keys())
    folio_probs = {}
    for f in folios:
        vec = folio_vectors[f].astype(float)
        total = vec.sum()
        folio_probs[f] = vec / total if total > 0 else np.ones(len(CATEGORIES)) / len(CATEGORIES)

    within, between = [], []
    for f1, f2 in combinations(folios, 2):
        jsd = float(jensenshannon(folio_probs[f1], folio_probs[f2]) ** 2)
        s1 = SIGN_TO_SEASON[best_map[f1]]
        s2 = SIGN_TO_SEASON[best_map[f2]]
        if s1 == s2:
            within.append(jsd)
        else:
            between.append(jsd)

    w_mean = np.mean(within) if within else 0
    b_mean = np.mean(between) if between else 0
    if len(within) >= 2 and len(between) >= 2:
        u, u_p = sp_stats.mannwhitneyu(within, between, alternative='less')
    else:
        u, u_p = 0, 1.0

    print(f"\nWithin/between coherence (best assignment):")
    print(f"  Within-season: {w_mean:.6f} ({len(within)} pairs)")
    print(f"  Between-season: {b_mean:.6f} ({len(between)} pairs)")
    print(f"  Mann-Whitney U p={u_p:.4f} {'SIGNIFICANT' if u_p < 0.05 else 'not significant'}")

    return {
        'v_gap': float(v_gap),
        'robust': v_gap > 0.01,
        'goat_sensitivity': {str(k): {'mean_v': float(np.mean(v)), 'max_v': float(max(v))}
                            for k, v in goat_orderings.items()},
        'coherence': {
            'within_mean': float(w_mean), 'between_mean': float(b_mean),
            'u_p': float(u_p), 'within_count': len(within), 'between_count': len(between),
        },
    }


# ================================================================
# STEP 5: COMPARE VS CONFIDENT-ONLY
# ================================================================
def compare_vs_confident(best, confident_v=0.157, confident_perm_p=0.018):
    """Compare best full map against confident-only baseline from Phase 583."""
    print("\n" + "=" * 70)
    print("STEP 5: COMPARE BEST FULL MAP vs CONFIDENT-ONLY (Phase 583)")
    print("=" * 70)

    best_v = best['cramers_v']
    print(f"\nConfident-only (7 folios): V={confident_v:.4f}, perm_p={confident_perm_p:.4f}")
    print(f"Best full map (12 folios): V={best_v:.4f}")
    print(f"Difference: {best_v - confident_v:+.4f}")

    if best_v > confident_v:
        print("-> Full map BEATS confident-only: unknown folios ADD signal")
        beats = True
    else:
        print("-> Full map does NOT beat confident-only: unknowns add noise even at best assignment")
        beats = False

    return {'best_v': float(best_v), 'confident_v': confident_v,
            'beats_confident': beats}


# ================================================================
# MAIN
# ================================================================
def main():
    t_start = time.time()
    print("=" * 70)
    print("Phase 584: ZODIAC_ASSIGNMENT_INFERENCE")
    print("Brute-force zodiac sign assignment for 5 unknown folios")
    print("=" * 70)

    # Step 0
    folio_cat_counts, folio_vectors, folio_token_counts = precompute_folio_data()

    # Step 1-2
    ranked = enumerate_assignments(folio_vectors)

    # Step 3
    best = ranked[0]
    perm_results = permutation_validation(best['zodiac_map'], folio_vectors, best['chi2'])

    # Step 4
    sensitivity = sensitivity_analysis(ranked, folio_vectors)

    # Step 5
    comparison = compare_vs_confident(best)

    # ============================================================
    # FINAL VERDICTS
    # ============================================================
    print("\n" + "=" * 70)
    print("FINAL VERDICTS")
    print("=" * 70)

    confirmed = perm_results['perm_p'] < 0.05
    robust = sensitivity['v_gap'] > 0.01
    beats = comparison['beats_confident']

    # C1685: MAP_INFERRED
    print(f"\nC1685 ZODIAC_MAP_INFERRED: perm_p={perm_results['perm_p']:.4f} "
          f"-> {'CONFIRMED' if confirmed else 'NOT CONFIRMED'}")

    # C1686: ASSIGNMENT_ROBUST
    print(f"C1686 ASSIGNMENT_ROBUST: V gap={sensitivity['v_gap']:.4f} "
          f"-> {'ROBUST' if robust else 'THIN'}")

    # C1687: FULL_MAP_BEATS_CONFIDENT
    print(f"C1687 FULL_MAP_BEATS_CONFIDENT: best V={best['cramers_v']:.4f} vs 0.157 "
          f"-> {'YES' if beats else 'NO'}")

    # C1688: GOAT_ORDER_RESOLVED
    goat_sens = sensitivity['goat_sensitivity']
    goat_keys = list(goat_sens.keys())
    if len(goat_keys) == 2:
        v1 = goat_sens[goat_keys[0]]['mean_v']
        v2 = goat_sens[goat_keys[1]]['mean_v']
        goat_gap = abs(v1 - v2)
        goat_resolved = goat_gap > 0.005
        better_goat = goat_keys[0] if v1 > v2 else goat_keys[1]
        print(f"C1688 GOAT_ORDER_RESOLVED: gap={goat_gap:.4f} "
              f"-> {'RESOLVED: ' + better_goat if goat_resolved else 'NOT RESOLVED (too close)'}")
    else:
        goat_resolved = False

    # Overall
    print("\n" + "-" * 70)
    if confirmed and robust:
        overall = "MAP_INFERRED"
    elif confirmed:
        overall = "MAP_TENTATIVE"
    elif not beats:
        overall = "UNKNOWNS_ADD_NOISE"
    else:
        overall = "MAP_WEAK"

    print(f"OVERALL: {overall}")
    print(f"\nBEST ZODIAC MAP:")
    for f in ALL_NYMPH_FOLIOS:
        sign = best['zodiac_map'][f]
        season = SIGN_TO_SEASON[sign]
        source = "ANCHOR" if f in ANCHORS else "INFERRED"
        print(f"  {f:8s} → {sign:12s} ({season:6s})  [{source}]")

    elapsed = time.time() - t_start
    print(f"\nTotal runtime: {elapsed:.2f}s")

    # ============================================================
    # SAVE
    # ============================================================
    output = {
        'phase': 'ZODIAC_ASSIGNMENT_INFERENCE',
        'phase_number': 584,
        'overall_verdict': overall,
        'runtime_s': round(elapsed, 2),
        'best_assignment': {
            'zodiac_map': best['zodiac_map'],
            'chi2': best['chi2'],
            'cramers_v': best['cramers_v'],
            'p': best['p'],
            'goat_desc': best['goat_desc'],
            'unk_desc': best['unk_desc'],
        },
        'permutation': perm_results,
        'all_assignments': [
            {'rank': i+1, 'cramers_v': r['cramers_v'], 'chi2': r['chi2'],
             'p': r['p'], 'goat_desc': r['goat_desc'], 'unk_desc': r['unk_desc']}
            for i, r in enumerate(ranked)
        ],
        'sensitivity': sensitivity,
        'comparison_vs_confident': comparison,
        'constraints': {
            'C1685': {'claim': 'ZODIAC_MAP_INFERRED', 'confirmed': bool(confirmed)},
            'C1686': {'claim': 'ASSIGNMENT_ROBUST', 'confirmed': bool(robust)},
            'C1687': {'claim': 'FULL_MAP_BEATS_CONFIDENT', 'confirmed': bool(beats)},
            'C1688': {'claim': 'GOAT_ORDER_RESOLVED', 'confirmed': bool(goat_resolved)},
        },
    }

    out_path = RESULTS_DIR / "zodiac_assignment_inference.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

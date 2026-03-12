"""
Phase 583b: ZODIAC_SEASONAL_CATEGORY v2 — Corrected Zodiac Mapping

Re-run of Phase 583 with three corrections:
1. EXCLUDE f70r1/f70r2 (non-figurative diagrams, not nymph/zodiac pages)
2. USE visual-evidence zodiac assignments instead of standard scholarship order
3. RUN both "all 12 nymph pages" and "confident-only" (7 pages) subsets

Visual identification from user's folio annotations (data/folio_annotations/azc/):
  f70v2: Fish → Pisces (confident)
  f70v1: Goat → ambiguous (Capricorn or Aries)
  f71r:  Goat+plant → ambiguous (Taurus or Capricorn)
  f71v:  "Animal" → UNKNOWN (generic, unidentifiable)
  f72r1: "Animal" → UNKNOWN
  f72r2: Man+woman → Gemini (confident)
  f72r3: "Animal" → UNKNOWN
  f72v1: Scale → Libra (confident)
  f72v3: Feline → Leo (confident)
  f72v2: Lady → Virgo (confident)
  f73r:  Reptile → Scorpio (confident, reasonable)
  f73v:  Crossbow → Sagittarius (confident)

References: C322, C431, C472, C1250, C1681-C1684
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
# CORRECTED ZODIAC MAPS (visual-evidence based)
# ================================================================

# Map A: Visual evidence, best-guess for ambiguous, exclude unknowns
# Goats assigned to Capricorn (visual match), unknowns excluded
VISUAL_MAP_CAPRICORN = {
    'f70v2': 'Pisces',         # Fish (confident)
    'f70v1': 'Capricorn',      # Goat → Capricorn (visual best-guess)
    'f71r':  'Capricorn',      # Goat+plant → Capricorn (visual best-guess)
    # f71v: EXCLUDED (generic "animal", unidentifiable)
    # f72r1: EXCLUDED (generic "animal", unidentifiable)
    'f72r2': 'Gemini',         # Man+woman (confident)
    # f72r3: EXCLUDED (generic "animal", unidentifiable)
    'f72v1': 'Libra',          # Balancing scale (confident)
    'f72v3': 'Leo',            # Tiger/feline (confident)
    'f72v2': 'Virgo',          # Lady of status (confident)
    'f73r':  'Scorpio',        # Reptile (confident, reasonable)
    'f73v':  'Sagittarius',    # Lady+crossbow (confident)
}

# Map B: Same but goats assigned to Aries (alternative interpretation)
VISUAL_MAP_ARIES = dict(VISUAL_MAP_CAPRICORN)
VISUAL_MAP_ARIES['f70v1'] = 'Aries'     # Goat → Aries (ram interpretation)
VISUAL_MAP_ARIES['f71r'] = 'Taurus'     # Goat+plant → Taurus (grazing animal)

# Map C: Confident-only (7 pages, no ambiguous goats)
CONFIDENT_ONLY_MAP = {
    'f70v2': 'Pisces',
    'f72r2': 'Gemini',
    'f72v1': 'Libra',
    'f72v3': 'Leo',
    'f72v2': 'Virgo',
    'f73r':  'Scorpio',
    'f73v':  'Sagittarius',
}

# Map D: Original (for comparison) -- but excluding f70r1/f70r2
ORIGINAL_NYMPH_ONLY = {
    'f70v2': 'Aries', 'f70v1': 'Pisces',
    'f71r': 'Taurus', 'f71v': 'Taurus',
    'f72r1': 'Gemini', 'f72r2': 'Cancer', 'f72r3': 'Leo',
    'f72v1': 'Virgo', 'f72v2': 'Libra', 'f72v3': 'Scorpio',
    'f73r': 'Sagittarius', 'f73v': 'Capricorn',
}

SIGN_TO_SEASON = {
    'Pisces': 'Spring', 'Aries': 'Spring', 'Taurus': 'Spring',
    'Gemini': 'Summer', 'Cancer': 'Summer', 'Leo': 'Summer',
    'Virgo': 'Autumn', 'Libra': 'Autumn', 'Scorpio': 'Autumn',
    'Sagittarius': 'Winter', 'Capricorn': 'Winter',
}

SEASONS = ['Spring', 'Summer', 'Autumn', 'Winter']
CATEGORIES = list(CategoryClassifier.CATEGORIES)


def assemble_data(zodiac_map, label):
    """Load AZC tokens from specified zodiac folios, classify MIDDLEs."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    folio_cat_counts = {f: Counter() for f in zodiac_map}
    folio_token_counts = {f: 0 for f in zodiac_map}
    folio_classified = {f: 0 for f in zodiac_map}
    zodiac_folios = set(zodiac_map.keys())

    for token in tx.azc():
        if token.folio not in zodiac_folios:
            continue
        if token.is_uncertain:
            continue
        folio = token.folio
        folio_token_counts[folio] += 1
        m = morph.extract(token.word)
        if not m.middle:
            continue
        cat = cc.classify(m.middle)
        if cat:
            folio_cat_counts[folio][cat] += 1
            folio_classified[folio] += 1

    # Build season aggregates
    folio_to_season = {f: SIGN_TO_SEASON[s] for f, s in zodiac_map.items()}
    season_cat_counts = {s: Counter() for s in SEASONS}
    for folio, counts in folio_cat_counts.items():
        season = folio_to_season[folio]
        season_cat_counts[season] += counts

    total_tokens = sum(folio_token_counts.values())
    total_classified = sum(folio_classified.values())

    print(f"\n  [{label}] {len(zodiac_map)} folios, {total_tokens} tokens, "
          f"{total_classified} classified ({100*total_classified/max(total_tokens,1):.1f}%)")
    for f in sorted(zodiac_map.keys()):
        sign = zodiac_map[f]
        season = folio_to_season[f]
        n = folio_token_counts[f]
        c = folio_classified[f]
        print(f"    {f:8s} → {sign:12s} ({season:6s}): {n:4d} tok, {c:4d} classified")

    # Season summary
    for s in SEASONS:
        total_s = sum(season_cat_counts[s].values())
        if total_s > 0:
            top_cats = season_cat_counts[s].most_common(3)
            top_str = ", ".join(f"{c}={100*n/total_s:.0f}%" for c, n in top_cats)
            print(f"    {s:6s}: {total_s:4d} tokens — top: {top_str}")

    return folio_cat_counts, season_cat_counts, folio_token_counts, folio_to_season


def run_battery(folio_cat_counts, season_cat_counts, folio_to_season, label):
    """Run the full test battery on a given mapping."""
    results = {}

    # Filter to seasons with data
    active_seasons = [s for s in SEASONS if sum(season_cat_counts[s].values()) > 0]
    n_seasons = len(active_seasons)

    if n_seasons < 2:
        print(f"  [{label}] Only {n_seasons} season(s) with data — SKIPPING")
        return {'skipped': True, 'reason': f'only {n_seasons} seasons'}

    # --- Step 1: Chi-squared ---
    table = np.zeros((n_seasons, len(CATEGORIES)), dtype=int)
    for i, s in enumerate(active_seasons):
        for j, cat in enumerate(CATEGORIES):
            table[i, j] = season_cat_counts[s].get(cat, 0)

    # Remove empty columns
    col_sums = table.sum(axis=0)
    nonempty = col_sums > 0
    table_clean = table[:, nonempty]
    cats_clean = [CATEGORIES[j] for j in range(len(CATEGORIES)) if nonempty[j]]

    if table_clean.shape[0] < 2 or table_clean.shape[1] < 2:
        print(f"  [{label}] Degenerate table — SKIPPING")
        return {'skipped': True, 'reason': 'degenerate table'}

    chi2, p, dof, expected = sp_stats.chi2_contingency(table_clean)
    n_total = table_clean.sum()
    k = min(table_clean.shape)
    cramers_v = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 else 0

    print(f"\n  [{label}] Chi-squared: χ²={chi2:.3f}, p={p:.6f}, V={cramers_v:.4f}, "
          f"N={n_total}, seasons={n_seasons}")
    results['chi2'] = {'chi2': float(chi2), 'p': float(p), 'cramers_v': float(cramers_v),
                       'n': int(n_total), 'n_seasons': n_seasons}

    # --- Step 2: Permutation ---
    rng = np.random.default_rng(SEED)
    folios = sorted(folio_to_season.keys())
    season_labels = [folio_to_season[f] for f in folios]

    folio_vectors = {}
    for f in folios:
        folio_vectors[f] = np.array([folio_cat_counts[f].get(cat, 0) for cat in CATEGORIES])

    n_ge = 0
    valid = 0
    for _ in range(N_PERM):
        shuffled = list(season_labels)
        rng.shuffle(shuffled)
        perm_season = {s: np.zeros(len(CATEGORIES)) for s in active_seasons}
        for idx, f in enumerate(folios):
            s = shuffled[idx]
            if s in perm_season:
                perm_season[s] += folio_vectors[f]
        ptable = np.array([perm_season[s] for s in active_seasons])
        ptable_clean = ptable[:, nonempty]
        if np.any(ptable_clean.sum(axis=1) == 0) or np.any(ptable_clean.sum(axis=0) == 0):
            continue
        try:
            pc, _, _, _ = sp_stats.chi2_contingency(ptable_clean)
            valid += 1
            if pc >= chi2:
                n_ge += 1
        except ValueError:
            continue

    perm_p = n_ge / max(valid, 1)
    print(f"  [{label}] Permutation: p={perm_p:.4f} ({n_ge}/{valid} valid)")
    results['permutation'] = {'perm_p': float(perm_p), 'n_ge': n_ge, 'valid': valid}

    # --- Step 3: Per-category gradient ---
    folios_list = sorted(folio_to_season.keys())
    folio_props = {}
    for f in folios_list:
        total = sum(folio_cat_counts[f].values())
        folio_props[f] = {cat: folio_cat_counts[f].get(cat, 0) / max(total, 1) for cat in CATEGORIES}

    sig_cats = []
    print(f"  [{label}] Per-category Kruskal-Wallis:")
    for cat in CATEGORIES:
        groups = defaultdict(list)
        for f in folios_list:
            s = folio_to_season[f]
            groups[s].append(folio_props[f][cat])
        group_list = [np.array(groups[s]) for s in active_seasons if len(groups[s]) > 0]
        if len(group_list) >= 2:
            try:
                h, kw_p = sp_stats.kruskal(*group_list)
            except ValueError:
                h, kw_p = 0, 1
        else:
            h, kw_p = 0, 1
        sig = kw_p < 0.05
        if sig:
            sig_cats.append(cat)
        means = {s: np.mean(groups[s]) if groups[s] else 0 for s in active_seasons}
        means_str = " ".join(f"{s[:2]}={means[s]:.3f}" for s in active_seasons)
        marker = " ***" if sig else ""
        print(f"    {cat:14s} H={h:6.2f} p={kw_p:.4f}  {means_str}{marker}")

    results['per_category'] = {cat: cat in sig_cats for cat in CATEGORIES}
    results['sig_cats'] = sig_cats

    # --- Step 4: Seasonal JSD ---
    season_probs = {}
    for s in active_seasons:
        vec = np.array([season_cat_counts[s].get(cat, 0) for cat in CATEGORIES], dtype=float)
        total = vec.sum()
        season_probs[s] = vec / total if total > 0 else np.ones(len(CATEGORIES)) / len(CATEGORIES)

    adjacent_pairs = {('Spring', 'Summer'), ('Summer', 'Autumn'),
                      ('Autumn', 'Winter'), ('Winter', 'Spring')}
    adj_jsds, dist_jsds = [], []
    for s1, s2 in combinations(active_seasons, 2):
        jsd = float(jensenshannon(season_probs[s1], season_probs[s2]) ** 2)
        is_adj = (s1, s2) in adjacent_pairs or (s2, s1) in adjacent_pairs
        (adj_jsds if is_adj else dist_jsds).append(jsd)

    adj_mean = np.mean(adj_jsds) if adj_jsds else 0
    dist_mean = np.mean(dist_jsds) if dist_jsds else 0
    print(f"  [{label}] Seasonal JSD: adj={adj_mean:.6f}, dist={dist_mean:.6f}")
    results['jsd'] = {'adj_mean': float(adj_mean), 'dist_mean': float(dist_mean)}

    # --- Step 5: Within/between coherence ---
    folio_probs = {}
    for f in folios_list:
        vec = np.array([folio_cat_counts[f].get(cat, 0) for cat in CATEGORIES], dtype=float)
        total = vec.sum()
        folio_probs[f] = vec / total if total > 0 else np.ones(len(CATEGORIES)) / len(CATEGORIES)

    within, between = [], []
    for f1, f2 in combinations(folios_list, 2):
        jsd = float(jensenshannon(folio_probs[f1], folio_probs[f2]) ** 2)
        if folio_to_season[f1] == folio_to_season[f2]:
            within.append(jsd)
        else:
            between.append(jsd)

    w_mean = np.mean(within) if within else 0
    b_mean = np.mean(between) if between else 0
    if len(within) >= 2 and len(between) >= 2:
        u, u_p = sp_stats.mannwhitneyu(within, between, alternative='less')
    else:
        u, u_p = 0, 1.0
    print(f"  [{label}] Coherence: within={w_mean:.6f} ({len(within)} pairs), "
          f"between={b_mean:.6f} ({len(between)} pairs), p={u_p:.4f}")
    results['coherence'] = {'within_mean': float(w_mean), 'between_mean': float(b_mean),
                            'u_p': float(u_p), 'within_count': len(within),
                            'between_count': len(between)}

    return results


def main():
    t_start = time.time()
    print("=" * 70)
    print("Phase 583b: ZODIAC_SEASONAL_CATEGORY v2 — Corrected Zodiac Mapping")
    print("=" * 70)

    maps = {
        'A_visual_capricorn': VISUAL_MAP_CAPRICORN,
        'B_visual_aries': VISUAL_MAP_ARIES,
        'C_confident_only': CONFIDENT_ONLY_MAP,
        'D_original_nymph_only': ORIGINAL_NYMPH_ONLY,
    }

    all_results = {}
    for label, zodiac_map in maps.items():
        print(f"\n{'='*70}")
        print(f"MAP: {label}")
        print(f"{'='*70}")

        folio_cat_counts, season_cat_counts, folio_token_counts, folio_to_season = \
            assemble_data(zodiac_map, label)
        results = run_battery(folio_cat_counts, season_cat_counts, folio_to_season, label)
        all_results[label] = results

    # ============================================================
    # COMPARISON SUMMARY
    # ============================================================
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}")

    print(f"\n{'Map':<30s} {'Folios':>6s} {'χ²':>8s} {'p(χ²)':>10s} {'V':>8s} "
          f"{'perm_p':>8s} {'sig_cats':>10s} {'w<b p':>8s}")
    print("-" * 95)

    for label, r in all_results.items():
        if r.get('skipped'):
            print(f"{label:<30s} {'SKIPPED':>6s}  ({r['reason']})")
            continue
        chi = r['chi2']
        perm = r['permutation']
        coh = r['coherence']
        sc = r.get('sig_cats', [])
        print(f"{label:<30s} {chi['n']:6d} {chi['chi2']:8.2f} {chi['p']:10.6f} "
              f"{chi['cramers_v']:8.4f} {perm['perm_p']:8.4f} "
              f"{','.join(sc) if sc else 'none':>10s} {coh['u_p']:8.4f}")

    # Key question: does correction change the verdict?
    print(f"\n{'='*70}")
    print("KEY QUESTION: Does correcting zodiac assignments change the verdict?")
    print(f"{'='*70}")

    for label, r in all_results.items():
        if r.get('skipped'):
            continue
        chi = r['chi2']
        perm = r['permutation']
        sc = r.get('sig_cats', [])
        thermal = 'THERMAL' in sc
        contain = 'CONTAINMENT' in sc

        if chi['p'] < 0.05 and perm['perm_p'] < 0.05 and (thermal or contain):
            verdict = "SEASONAL_CATEGORY_CONFIRMED"
        elif chi['p'] < 0.05 and perm['perm_p'] < 0.05:
            verdict = "SEASONAL_SIGNAL_CONFIRMED_MECHANISM_UNCLEAR"
        elif chi['p'] < 0.05:
            verdict = "SEASONAL_SIGNAL_WEAK"
        else:
            verdict = "SEASONAL_CATEGORY_ABSENT"

        print(f"  {label}: {verdict}")

    elapsed = time.time() - t_start
    print(f"\nTotal runtime: {elapsed:.2f}s")

    # Save results
    output = {
        'phase': 'ZODIAC_SEASONAL_CATEGORY_v2',
        'runtime_s': round(elapsed, 2),
        'maps': {label: {
            'zodiac_map': maps[label],
            'results': r
        } for label, r in all_results.items()},
    }
    out_path = RESULTS_DIR / "zodiac_seasonal_category_v2.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"Results saved to {out_path}")


if __name__ == '__main__':
    main()

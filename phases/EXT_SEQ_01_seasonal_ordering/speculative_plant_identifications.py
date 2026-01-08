"""
EXT-SEQ-01B: Speculative Plant Identification and Finer-Grained Seasonal Analysis

STATUS: TIER 4 SPECULATIVE
This file contains SPECULATIVE plant identifications based on:
- PIAA morphological descriptions
- Historical availability in 15th century Central Europe / Northern Italy
- Aromatic/perfumery relevance

These identifications are NOT proven. They are hypotheses for testing seasonal ordering.
"""

import random
import numpy as np
from scipy import stats as scipy_stats
from collections import Counter

# SPECULATIVE PLANT IDENTIFICATIONS
# Format: folio -> {
#   'piaa_desc': original PIAA description,
#   'best_guess': (plant_name, confidence),
#   'second_choice': (plant_name, confidence),
#   'peak_month': primary flowering/harvest month (1-12),
#   'month_range': (start, end) of useful period,
#   'rationale': why this identification
# }

SPECULATIVE_IDS = {
    'f2r': {
        'piaa_desc': 'palmate divided leaves, prominent root, flowering head; umbellifer or ranunculus',
        'best_guess': ('Angelica', 'MEDIUM'),
        'second_choice': ('Lovage', 'LOW'),
        'peak_month': 7,  # July - flowering
        'month_range': (6, 8),
        'rationale': 'Divided leaves + prominent root + flowering head suggests Apiaceae; angelica most aromatic'
    },
    'f3v': {
        'piaa_desc': 'lobed leaves, large dark blue spherical flower',
        'best_guess': ('Echinops/Globe Thistle', 'MEDIUM'),
        'second_choice': ('Eryngium/Sea Holly', 'LOW'),
        'peak_month': 8,  # August
        'month_range': (7, 9),
        'rationale': 'Spherical blue flower head distinctive; both used medicinally'
    },
    'f5r': {
        'piaa_desc': 'large rounded/heart-shaped leaves, bulbous base; violet-type',
        'best_guess': ('Violet', 'HIGH'),
        'second_choice': ('Cyclamen', 'MEDIUM'),
        'peak_month': 4,  # April - early spring
        'month_range': (3, 5),
        'rationale': 'Heart-shaped leaves + bulbous base classic violet morphology; major perfumery flower'
    },
    'f5v': {
        'piaa_desc': 'bushy with ivy-like leaves, small red/pink flowers',
        'best_guess': ('Geranium', 'HIGH'),
        'second_choice': ('Herb Robert', 'MEDIUM'),
        'peak_month': 6,  # June
        'month_range': (5, 9),
        'rationale': 'Ivy-like leaves + pink flowers = classic geranium; aromatic leaves used in perfumery'
    },
    'f9r': {
        'piaa_desc': 'feathery divided leaves, central spike, red root',
        'best_guess': ('Fennel', 'HIGH'),
        'second_choice': ('Dill', 'HIGH'),
        'peak_month': 7,  # July - flowering
        'month_range': (6, 9),
        'rationale': 'Feathery leaves + spike = classic umbellifer; fennel most aromatic, red root may be artistic'
    },
    'f9v': {
        'piaa_desc': 'palmate leaves with striking blue/violet flowers',
        'best_guess': ('Larkspur/Delphinium', 'HIGH'),
        'second_choice': ('Aconite', 'MEDIUM'),
        'peak_month': 6,  # June - early summer
        'month_range': (5, 7),
        'rationale': 'Palmate leaves + tall blue spikes = larkspur; common in medieval gardens'
    },
    'f11r': {
        'piaa_desc': 'shrubby with dense small leaves, multiple stems',
        'best_guess': ('Lavender', 'HIGH'),
        'second_choice': ('Thyme', 'HIGH'),
        'peak_month': 7,  # July - peak harvest
        'month_range': (6, 8),
        'rationale': 'Shrubby habit + small leaves = Mediterranean subshrub; lavender most aromatic'
    },
    'f11v': {
        'piaa_desc': 'tree-like form, dense oval leaves',
        'best_guess': ('Bay Laurel', 'HIGH'),
        'second_choice': ('Myrtle', 'MEDIUM'),
        'peak_month': 5,  # May - flowering, but leaves year-round
        'month_range': (1, 12),  # Evergreen
        'rationale': 'Tree-like + dense oval leaves = bay or myrtle; bay more common in distillation'
    },
    'f17r': {
        'piaa_desc': 'large oval leaves, tall blue/purple flower spike',
        'best_guess': ('Borage', 'HIGH'),
        'second_choice': ('Comfrey', 'MEDIUM'),
        'peak_month': 7,  # July
        'month_range': (6, 9),
        'rationale': 'Large leaves + blue flower spike = Boraginaceae; borage flowers distilled'
    },
    'f18r': {
        'piaa_desc': 'fern-like/palm fronds, blue flower',
        'best_guess': ('Nigella/Love-in-a-mist', 'MEDIUM'),
        'second_choice': ('Carrot family', 'LOW'),
        'peak_month': 6,  # June
        'month_range': (5, 7),
        'rationale': 'Fern-like leaves + blue = nigella; seeds aromatic'
    },
    'f19r': {
        'piaa_desc': 'very fine feathery leaves',
        'best_guess': ('Dill', 'HIGH'),
        'second_choice': ('Fennel', 'HIGH'),
        'peak_month': 7,  # July
        'month_range': (6, 8),
        'rationale': 'Very fine feathery = Apiaceae; dill finer than fennel'
    },
    'f21r': {
        'piaa_desc': 'rounded basal leaves, tall flowering spike',
        'best_guess': ('Valerian', 'MEDIUM'),
        'second_choice': ('Primrose', 'LOW'),
        'peak_month': 6,  # June
        'month_range': (5, 7),
        'rationale': 'Basal leaves + spike = valerian type; root highly aromatic'
    },
    'f22r': {
        'piaa_desc': 'divided leaves, small blue flowers, spreading habit',
        'best_guess': ('Speedwell/Veronica', 'MEDIUM'),
        'second_choice': ('Germander', 'LOW'),
        'peak_month': 6,  # June
        'month_range': (5, 8),
        'rationale': 'Small blue flowers + spreading = speedwell; medicinal'
    },
    'f22v': {
        'piaa_desc': 'bushy with scalloped leaves, prominent blue flower',
        'best_guess': ('Chicory', 'HIGH'),
        'second_choice': ('Borage', 'MEDIUM'),
        'peak_month': 7,  # July-August
        'month_range': (6, 9),
        'rationale': 'Scalloped leaves + large blue = chicory; roadside plant, root used'
    },
    'f24v': {
        'piaa_desc': 'deeply palmate/divided leaves',
        'best_guess': ('Hemp/Cannabis', 'MEDIUM'),
        'second_choice': ('Marsh Mallow', 'LOW'),
        'peak_month': 8,  # August
        'month_range': (7, 9),
        'rationale': 'Deeply palmate = cannabis type; fiber and medicine'
    },
    'f25r': {
        'piaa_desc': 'rounded ivy-like leaves, branching stem',
        'best_guess': ('Mallow', 'HIGH'),
        'second_choice': ('Ground Ivy', 'MEDIUM'),
        'peak_month': 7,  # July
        'month_range': (6, 9),
        'rationale': 'Rounded leaves + branching = mallow family; mucilaginous, medicinal'
    },
    'f29v': {
        'piaa_desc': 'serrated leaves, curling flower spikes',
        'best_guess': ("Solomon's Seal", 'MEDIUM'),
        'second_choice': ('Lily of the Valley', 'MEDIUM'),
        'peak_month': 5,  # May
        'month_range': (4, 6),
        'rationale': 'Curling spikes = Solomon\'s seal or lily; both aromatic'
    },
    'f30v': {
        'piaa_desc': 'conifer/juniper type + broad-leaved herb (two plants)',
        'best_guess': ('Juniper', 'HIGH'),
        'second_choice': ('Cypress', 'LOW'),
        'peak_month': 10,  # October - berry harvest
        'month_range': (9, 11),
        'rationale': 'Conifer type = juniper; berries aromatic, distilled'
    },
    'f32v': {
        'piaa_desc': 'stellate/radial leaf arrangement, seed pods',
        'best_guess': ('Clary Sage', 'MEDIUM'),
        'second_choice': ('Woad', 'LOW'),
        'peak_month': 7,  # July
        'month_range': (6, 8),
        'rationale': 'Stellate leaves + seed pods; clary sage highly aromatic'
    },
    'f35v': {
        'piaa_desc': 'stellate/palmate leaves on stem',
        'best_guess': ('Geranium/Cranesbill', 'MEDIUM'),
        'second_choice': ('Potentilla', 'LOW'),
        'peak_month': 6,  # June
        'month_range': (5, 8),
        'rationale': 'Stellate palmate = geranium type'
    },
    'f36r': {
        'piaa_desc': 'oval leaves, clustered flower heads',
        'best_guess': ('Tansy', 'MEDIUM'),
        'second_choice': ('Feverfew', 'MEDIUM'),
        'peak_month': 8,  # August
        'month_range': (7, 9),
        'rationale': 'Clustered heads = composite; tansy aromatic, insecticidal'
    },
    'f37v': {
        'piaa_desc': 'tree-like with diamond-shaped leaves',
        'best_guess': ('Myrtle', 'HIGH'),
        'second_choice': ('Bay Laurel', 'MEDIUM'),
        'peak_month': 6,  # June - flowering
        'month_range': (5, 7),
        'rationale': 'Diamond leaves + tree-like = myrtle; major Mediterranean aromatic'
    },
    'f38r': {
        'piaa_desc': 'iris-type with connected rhizomes, blue flower',
        'best_guess': ('Iris/Orris', 'VERY HIGH'),
        'second_choice': ('Flag Iris', 'HIGH'),
        'peak_month': 5,  # May - flowering; roots harvested summer
        'month_range': (5, 6),
        'rationale': 'Unmistakable iris morphology; orris root = major perfumery fixative'
    },
    'f38v': {
        'piaa_desc': 'oval leaves along central stem',
        'best_guess': ('Sage', 'HIGH'),
        'second_choice': ('Lemon Balm', 'MEDIUM'),
        'peak_month': 6,  # June
        'month_range': (5, 7),
        'rationale': 'Opposite oval leaves = Lamiaceae; sage most aromatic'
    },
    'f42r': {
        'piaa_desc': 'multiple connected plants with flower heads, extensive roots',
        'best_guess': ('Elecampane', 'MEDIUM'),
        'second_choice': ('Comfrey', 'LOW'),
        'peak_month': 8,  # August
        'month_range': (7, 9),
        'rationale': 'Connected rhizomes + extensive roots = elecampane; root aromatic'
    },
    'f45v': {
        'piaa_desc': 'deeply serrated/spiny leaves, round flower heads',
        'best_guess': ('Artichoke/Cardoon', 'HIGH'),
        'second_choice': ('Thistle', 'HIGH'),
        'peak_month': 8,  # August-September
        'month_range': (8, 9),
        'rationale': 'Spiny leaves + round heads = Cynara; cardoon used medicinally'
    },
    'f47v': {
        'piaa_desc': 'scattered leaf study page, ivy-like leaves',
        'best_guess': ('Ground Ivy/Alehoof', 'MEDIUM'),
        'second_choice': ('Ivy', 'LOW'),
        'peak_month': 5,  # May
        'month_range': (4, 6),
        'rationale': 'Ivy-like scattered = ground ivy; aromatic medicinal'
    },
    'f49v': {
        'piaa_desc': 'large basal leaves, dramatic blue feathery flower',
        'best_guess': ('Cornflower', 'HIGH'),
        'second_choice': ('Centaurea/Knapweed', 'MEDIUM'),
        'peak_month': 7,  # July
        'month_range': (6, 8),
        'rationale': 'Large blue feathery = cornflower; medieval eye remedy, ornamental'
    },
    'f51v': {
        'piaa_desc': 'spiny/serrated leaves on stem',
        'best_guess': ('Blessed Thistle', 'MEDIUM'),
        'second_choice': ('Milk Thistle', 'MEDIUM'),
        'peak_month': 8,  # August
        'month_range': (7, 9),
        'rationale': 'Spiny serrated = thistle; blessed thistle medicinal'
    },
    'f56r': {
        'piaa_desc': 'bushy palmate leaves, small blue flowers',
        'best_guess': ('Germander', 'MEDIUM'),
        'second_choice': ('Scullcap', 'LOW'),
        'peak_month': 7,  # July
        'month_range': (6, 8),
        'rationale': 'Bushy palmate + blue = germander; aromatic medicinal'
    },
}

# Folio order (as bound)
FOLIO_ORDER = [
    'f2r', 'f3v', 'f5r', 'f5v', 'f9r', 'f9v', 'f11r', 'f11v',
    'f17r', 'f18r', 'f19r', 'f21r', 'f22r', 'f22v', 'f24v', 'f25r',
    'f29v', 'f30v', 'f32v', 'f35v', 'f36r', 'f37v', 'f38r', 'f38v',
    'f42r', 'f45v', 'f47v', 'f49v', 'f51v', 'f56r'
]

# Month names for display
MONTH_NAMES = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Finer seasonal bins (bimonthly)
def get_fine_season(month):
    """Map month to finer seasonal bin."""
    if month in [3, 4]:
        return 'EARLY_SPRING'
    elif month in [5, 6]:
        return 'LATE_SPRING'
    elif month in [7, 8]:
        return 'SUMMER'
    elif month in [9, 10]:
        return 'AUTUMN'
    elif month in [11, 12, 1, 2]:
        return 'WINTER'
    else:
        return 'AMBIGUOUS'

# Neighbors for finer bins
FINE_SEASON_NEIGHBORS = {
    'EARLY_SPRING': {'WINTER', 'EARLY_SPRING', 'LATE_SPRING'},
    'LATE_SPRING': {'EARLY_SPRING', 'LATE_SPRING', 'SUMMER'},
    'SUMMER': {'LATE_SPRING', 'SUMMER', 'AUTUMN'},
    'AUTUMN': {'SUMMER', 'AUTUMN', 'WINTER'},
    'WINTER': {'AUTUMN', 'WINTER', 'EARLY_SPRING'},
    'AMBIGUOUS': {'EARLY_SPRING', 'LATE_SPRING', 'SUMMER', 'AUTUMN', 'WINTER'}
}


def get_peak_month(folio):
    """Get peak month for a folio."""
    if folio in SPECULATIVE_IDS:
        return SPECULATIVE_IDS[folio]['peak_month']
    return 7  # Default to July if unknown


def get_fine_season_for_folio(folio):
    """Get fine seasonal bin for a folio."""
    return get_fine_season(get_peak_month(folio))


def adjacency_same_or_neighbor(seq, get_season_func, neighbors_dict):
    """Count adjacent pairs in same or neighboring seasonal bin."""
    count = 0
    for i in range(len(seq) - 1):
        s1 = get_season_func(seq[i])
        s2 = get_season_func(seq[i+1])
        if s2 in neighbors_dict.get(s1, set()):
            count += 1
    return count / (len(seq) - 1) if len(seq) > 1 else 0


def monotonic_drift(seq, get_month_func):
    """Compute Spearman correlation between position and month."""
    positions = list(range(len(seq)))
    months = [get_month_func(f) for f in seq]
    if len(set(months)) < 2:
        return 0, 1.0
    rho, p = scipy_stats.spearmanr(positions, months)
    return rho, p


def find_clusters(seq, get_season_func):
    """Find contiguous clusters of same seasonal bin."""
    if not seq:
        return []
    clusters = []
    current_bin = get_season_func(seq[0])
    current_size = 1
    for i in range(1, len(seq)):
        bin_i = get_season_func(seq[i])
        if bin_i == current_bin:
            current_size += 1
        else:
            clusters.append((current_bin, current_size))
            current_bin = bin_i
            current_size = 1
    clusters.append((current_bin, current_size))
    return clusters


def run_permutation_test(observed_stat, stat_func, seq, n_perms=10000):
    """Run permutation test comparing observed to shuffled."""
    null_stats = []
    for _ in range(n_perms):
        shuffled = seq.copy()
        random.shuffle(shuffled)
        null_stats.append(stat_func(shuffled))

    null_stats = np.array(null_stats)
    if observed_stat >= np.mean(null_stats):
        p = np.mean(null_stats >= observed_stat)
    else:
        p = np.mean(null_stats <= observed_stat)
    p = min(p * 2, 1.0)

    effect_size = (observed_stat - np.mean(null_stats)) / np.std(null_stats) if np.std(null_stats) > 0 else 0

    return p, np.mean(null_stats), np.std(null_stats), effect_size


def main():
    print("="*70)
    print("EXT-SEQ-01B: SPECULATIVE PLANT ID + FINER-GRAINED SEASONAL ANALYSIS")
    print("="*70)
    print("\n*** TIER 4 SPECULATIVE - NOT PROVEN ***\n")

    random.seed(42)
    np.random.seed(42)

    # Display speculative identifications
    print("="*70)
    print("SECTION 1: SPECULATIVE PLANT IDENTIFICATIONS")
    print("="*70)
    print("\nBased on: PIAA morphology + 15th c. European aromatic availability\n")

    print(f"{'Folio':<8} {'Best Guess':<20} {'Conf':<8} {'Month':<6} {'Season':<12}")
    print("-" * 60)

    for folio in FOLIO_ORDER:
        if folio in SPECULATIVE_IDS:
            data = SPECULATIVE_IDS[folio]
            plant, conf = data['best_guess']
            month = data['peak_month']
            season = get_fine_season(month)
            print(f"{folio:<8} {plant:<20} {conf:<8} {MONTH_NAMES[month]:<6} {season:<12}")

    # Show distribution
    print("\n" + "="*70)
    print("SECTION 2: FINER SEASONAL DISTRIBUTION")
    print("="*70)

    seasons = [get_fine_season_for_folio(f) for f in FOLIO_ORDER]
    season_counts = Counter(seasons)

    print("\nBimonthly Bins:")
    for season in ['EARLY_SPRING', 'LATE_SPRING', 'SUMMER', 'AUTUMN', 'WINTER']:
        count = season_counts.get(season, 0)
        pct = count / len(FOLIO_ORDER) * 100
        bar = '#' * int(pct / 2)
        print(f"  {season:<12}: {count:>2} ({pct:>5.1f}%) {bar}")

    # Monthly distribution
    print("\nMonthly Distribution:")
    months = [get_peak_month(f) for f in FOLIO_ORDER]
    month_counts = Counter(months)
    for m in range(1, 13):
        count = month_counts.get(m, 0)
        bar = '#' * count
        print(f"  {MONTH_NAMES[m]:<4}: {count:>2} {bar}")

    # Run tests
    print("\n" + "="*70)
    print("SECTION 3: ORDERING TESTS (FINER BINS)")
    print("="*70)

    # A. Adjacency Test
    print("\n--- A. ADJACENCY BIAS TEST (Bimonthly Bins) ---")

    def adj_stat(seq):
        return adjacency_same_or_neighbor(seq, get_fine_season_for_folio, FINE_SEASON_NEIGHBORS)

    obs_adj = adj_stat(FOLIO_ORDER)
    p_adj, null_mean_adj, null_std_adj, d_adj = run_permutation_test(obs_adj, adj_stat, FOLIO_ORDER, 10000)

    print(f"  Observed adjacency rate: {obs_adj:.3f}")
    print(f"  Null mean (shuffled):    {null_mean_adj:.3f}")
    print(f"  Effect size (Cohen's d): {d_adj:.3f}")
    print(f"  p-value (two-tailed):    {p_adj:.4f}")

    adj_verdict = "SIGNIFICANT" if p_adj < 0.05 and abs(d_adj) > 0.5 else "NOT SIGNIFICANT"
    print(f"  Verdict: {adj_verdict}")

    # B. Monotonic Drift Test
    print("\n--- B. MONOTONIC DRIFT TEST (Monthly Resolution) ---")

    def drift_stat(seq):
        r, _ = monotonic_drift(seq, get_peak_month)
        return r

    obs_rho, obs_p = monotonic_drift(FOLIO_ORDER, get_peak_month)
    p_drift, null_mean_rho, null_std_rho, d_rho = run_permutation_test(obs_rho, drift_stat, FOLIO_ORDER, 10000)

    print(f"  Observed Spearman rho:   {obs_rho:.3f}")
    print(f"  Parametric p-value:      {obs_p:.4f}")
    print(f"  Null mean (shuffled):    {null_mean_rho:.3f}")
    print(f"  Effect size (Cohen's d): {d_rho:.3f}")
    print(f"  Permutation p-value:     {p_drift:.4f}")

    drift_verdict = "WEAK DRIFT" if p_drift < 0.05 else "NO DRIFT"
    print(f"  Verdict: {drift_verdict}")

    # C. Clustering Test
    print("\n--- C. CLUSTERING TEST (Bimonthly Bins) ---")

    def max_cluster_stat(seq):
        clusters = find_clusters(seq, get_fine_season_for_folio)
        sizes = [c[1] for c in clusters]
        return max(sizes) if sizes else 0

    obs_clusters = find_clusters(FOLIO_ORDER, get_fine_season_for_folio)
    obs_max = max(c[1] for c in obs_clusters) if obs_clusters else 0

    p_cluster, null_mean_max, null_std_max, d_cluster = run_permutation_test(
        obs_max, max_cluster_stat, FOLIO_ORDER, 10000
    )

    print(f"  Number of clusters:      {len(obs_clusters)}")
    print(f"  Max cluster size:        {obs_max}")
    print(f"  Null mean max size:      {null_mean_max:.2f}")
    print(f"  Effect size (Cohen's d): {d_cluster:.3f}")
    print(f"  p-value (max cluster):   {p_cluster:.4f}")

    cluster_verdict = "SIGNIFICANT" if p_cluster < 0.05 and d_cluster > 0.5 else "NOT SIGNIFICANT"
    print(f"  Verdict: {cluster_verdict}")

    print("\n  Observed clusters:")
    for i, (season, size) in enumerate(obs_clusters):
        print(f"    {i+1}. {season:<12} (size={size})")

    # D. Summary
    print("\n" + "="*70)
    print("SECTION 4: SUMMARY")
    print("="*70)

    print(f"\n{'Test':<30} {'Observed':>10} {'Null':>10} {'p-value':>10} {'Effect d':>10}")
    print("-" * 72)
    print(f"{'Adjacency (bimonthly)':<30} {obs_adj:>10.3f} {null_mean_adj:>10.3f} {p_adj:>10.4f} {d_adj:>10.3f}")
    print(f"{'Monotonic Drift (monthly)':<30} {obs_rho:>10.3f} {null_mean_rho:>10.3f} {p_drift:>10.4f} {d_rho:>10.3f}")
    print(f"{'Max Cluster (bimonthly)':<30} {obs_max:>10.1f} {null_mean_max:>10.2f} {p_cluster:>10.4f} {d_cluster:>10.3f}")

    sig_count = sum([p_adj < 0.05, p_drift < 0.05, p_cluster < 0.05])

    print(f"\n  Tests with p < 0.05: {sig_count}/3")

    if sig_count >= 2:
        outcome = "WEAK_SEASONAL_PATTERN"
    elif sig_count == 1:
        outcome = "MARGINAL_SIGNAL"
    else:
        outcome = "NO_ORDERING_SIGNAL"

    print(f"\n  OUTCOME: {outcome}")

    # Interpretation
    print("\n" + "="*70)
    print("SECTION 5: INTERPRETATION BOUNDARY")
    print("="*70)
    print("""
*** TIER 4 SPECULATIVE ***

This analysis uses SPECULATIVE plant identifications that are NOT proven.
The identifications are based on morphological similarity and historical
availability, but individual folios could be misidentified.

Even if seasonal patterns exist, they do NOT imply:
- harvest calendar
- recipe ingredients
- instructional sequence
- correspondence with text

Seasonal patterns, if present, may reflect:
- material availability during manuscript production
- copying order from an exemplar
- organizational convenience
- coincidence
""")

    print("="*70)
    print("EXT-SEQ-01B COMPLETE")
    print("="*70)

    return outcome


if __name__ == "__main__":
    main()

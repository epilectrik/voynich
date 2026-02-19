#!/usr/bin/env python3
"""
visual_vocabulary_correlation.py

Tests whether visual themes of the 9 Rosettes positions correlate with
their vocabulary profiles.

The f85v2 folio has 16 region codes:
  DESCRIPTION regions (confirmed rosette mappings):
    CENTER = C2 (apparatus/alembic vessels)
    NORTH  = N1, N2 (sharp blue spokes, heat/energy)
    SOUTH  = V1, V2 (matches NORTH, heat/energy)
  LABEL regions (unknown rosette mappings):
    B1, B2, B3, M1, M2, U1, U2, W1
  OTHER regions:
    D1, M3, U3

Visual themes:
  Cardinals: NORTH/SOUTH = sharp/heat, WEST = soft/condensation, EAST = water/liquid/bubbles
  Corners:   NW = botanical, NE = architectural/castle, SW = aqueous/eye-lens, SE = overhead-map/garden
  CENTER   = apparatus hub

5 Analyses:
  1. DESCRIPTION region vocabulary comparison (C2, N1+N2, V1+V2)
  2. LABEL region clustering (pairwise Jaccard + hierarchical clustering)
  3. Visual feature vocabulary signatures
  4. Unique vocabulary by region (signature MIDDLEs)
  5. B-corpus section correlation

Run from project root:
    python phases/ROSETTES_FUNCTIONAL_ANATOMY/scripts/visual_vocabulary_correlation.py
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    Transcript, Morphology, RosettesAnalyzer,
    BFolioDecoder, BTokenAnalysis
)

RESULTS = ROOT / 'phases' / 'ROSETTES_FUNCTIONAL_ANATOMY' / 'results'
RESULTS.mkdir(parents=True, exist_ok=True)

# ── Constants ────────────────────────────────────────────────────────────────

BIN_LABELS = {
    0: 'FLOW_TERMINAL', 1: 'ROUTINE_SPEC', 2: 'PRECISION_SPEC',
    3: 'COMPOUND_TERM', 4: 'BULK_OP', 5: 'SETTLING_SPEC',
    6: 'HUB_UNIVERSAL', 7: 'ENERGY_SPEC', 8: 'STABILITY_CRIT',
    9: 'PHASE_SENS'
}
FUNCTIONAL_BINS = [0, 1, 2, 3, 5, 6, 7, 8, 9]  # exclude bin 4

DESCRIPTION_REGIONS = {
    'CENTER': ['C2'],
    'NORTH': ['N1', 'N2'],
    'SOUTH': ['V1', 'V2'],
}

LABEL_REGIONS = ['B1', 'B2', 'B3', 'M1', 'M2', 'U1', 'U2', 'W1']

# Visual feature tags by rosette position
# (Only CENTER, NORTH, SOUTH can be directly tested with DESCRIPTION regions)
VISUAL_TAGS = {
    'WATER': ['EAST', 'SW', 'SE'],
    'STARS': ['NORTH', 'SOUTH', 'WEST', 'SW', 'NE', 'SE'],
    'NO_STARS': ['EAST'],
    'BOTANICAL': ['NW'],
    'ARCHITECTURAL': ['NE'],
    'APPARATUS': ['CENTER'],
    'BUBBLE_RING': ['EAST', 'SW', 'NW'],
    'EYE_LENS': ['SW', 'NW'],
}

# ── Utilities ────────────────────────────────────────────────────────────────

def round_floats(obj, decimals=4):
    """Recursively round floats and handle numpy types."""
    try:
        import numpy as np
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return round(float(obj), decimals)
    except ImportError:
        if isinstance(obj, float):
            return round(obj, decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    if isinstance(obj, set):
        return sorted(list(obj))
    return obj


def jaccard(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    return intersection / union


def print_matrix(labels, matrix, title):
    """Print a pairwise matrix in ASCII-safe format."""
    print()
    print(title)
    print('-' * len(title))
    col_w = max(max(len(lb) for lb in labels) + 1, 7)
    row_label_w = max(len(lb) for lb in labels) + 1

    # Header
    header = ' ' * (row_label_w + 2)
    for lb in labels:
        header += lb.rjust(col_w + 1)
    print(header)

    for i, row_lb in enumerate(labels):
        row = row_lb.rjust(row_label_w) + '  '
        for j in range(len(labels)):
            val = matrix[i][j]
            row += f'{val:.3f}'.rjust(col_w + 1)
        print(row)


def safe_pct(num, denom):
    """Safe percentage computation."""
    if denom == 0:
        return 0.0
    return num / denom


# ── Initialize ───────────────────────────────────────────────────────────────

print('=' * 72)
print('VISUAL-VOCABULARY CORRELATION ANALYSIS')
print('Rosettes f85v2: Do visual themes predict vocabulary profiles?')
print('=' * 72)
print()

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()

# Morphology cache
_morph_cache = {}
def get_middle(word):
    if not word or not word.strip() or '*' in word:
        return None
    if word not in _morph_cache:
        m = morph.extract(word)
        mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
        _morph_cache[word] = mid
    return _morph_cache[word]


def get_prefix(word):
    if not word or not word.strip() or '*' in word:
        return None
    if word not in _morph_cache:
        get_middle(word)  # populate cache side-effect
    m = morph.extract(word)
    return m.prefix if m and m.prefix else None


# Load bridge MIDDLEs
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f'Bridge MIDDLEs loaded: {len(bridge_middles)}')

# Load affordance table
aff_path = ROOT / 'data' / 'middle_affordance_table.json'
with open(aff_path, 'r', encoding='utf-8') as f:
    aff_data = json.load(f)
mid_to_bin = {}
for mid_key, mid_val in aff_data.get('middles', {}).items():
    if isinstance(mid_val, dict) and 'affordance_bin' in mid_val:
        mid_to_bin[mid_key] = mid_val['affordance_bin']
print(f'Affordance table loaded: {len(mid_to_bin)} MIDDLEs')

# HUB MIDDLEs (bin 6)
hub_middles = set(m for m, b in mid_to_bin.items() if b == 6)

# Build B-corpus per-section MIDDLE sets
print('Building B-corpus section MIDDLE sets...')
b_section_middles = defaultdict(set)   # section -> set of middles
b_folio_section = {}                   # folio -> section
b_folio_middles = defaultdict(set)     # folio -> set of middles
for tok in tx.currier_b():
    mid = get_middle(tok.word)
    if mid:
        b_section_middles[tok.section].add(mid)
        b_folio_middles[tok.folio].add(mid)
    b_folio_section[tok.folio] = tok.section
b_sections = sorted(b_section_middles.keys())
print(f'  B sections: {b_sections}')
print(f'  B folios: {len(b_folio_middles)}')

# ── Extract region vocabularies ──────────────────────────────────────────────

print()
print('Extracting region vocabularies...')

folio = 'f85v2'
all_regions = sorted(ra.get_regions(folio))

region_middles = {}     # region -> set of middles
region_tokens = {}      # region -> list of token words
region_prefixes = {}    # region -> Counter of prefixes
region_bin_counts = {}  # region -> Counter of bin labels

for region in all_regions:
    tokens = ra.get_tokens(folio, region)
    middles = set()
    words = []
    prefix_counter = Counter()
    bin_counter = Counter()

    for t in tokens:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        words.append(w)
        mid = get_middle(w)
        if mid:
            middles.add(mid)
            bn = mid_to_bin.get(mid)
            if bn is not None and bn in FUNCTIONAL_BINS:
                bin_counter[BIN_LABELS[bn]] += 1
        m = morph.extract(w)
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            prefix_counter[lane] += 1

    region_middles[region] = middles
    region_tokens[region] = words
    region_prefixes[region] = prefix_counter
    region_bin_counts[region] = bin_counter
    print(f'  {region:4s}: {len(words):3d} tokens, {len(middles):3d} unique MIDDLEs')


# Build combined DESCRIPTION region sets
desc_middles = {}
desc_words = {}
desc_prefixes = {}
desc_bin_counts = {}

for name, regions in DESCRIPTION_REGIONS.items():
    combined_middles = set()
    combined_words = []
    combined_prefixes = Counter()
    combined_bins = Counter()
    for r in regions:
        combined_middles |= region_middles.get(r, set())
        combined_words.extend(region_tokens.get(r, []))
        combined_prefixes += region_prefixes.get(r, Counter())
        combined_bins += region_bin_counts.get(r, Counter())
    desc_middles[name] = combined_middles
    desc_words[name] = combined_words
    desc_prefixes[name] = combined_prefixes
    desc_bin_counts[name] = combined_bins

print()
print('Combined DESCRIPTION regions:')
for name in DESCRIPTION_REGIONS:
    print(f'  {name:8s}: {len(desc_words[name]):3d} tokens, {len(desc_middles[name]):3d} unique MIDDLEs')

# All f85v2 middles (union of all regions)
all_f85v2_middles = set()
for mids in region_middles.values():
    all_f85v2_middles |= mids


# =====================================================================
# ANALYSIS 1: DESCRIPTION region vocabulary comparison
# =====================================================================
print()
print('=' * 72)
print('ANALYSIS 1: DESCRIPTION REGION VOCABULARY COMPARISON')
print('Comparing CENTER (C2), NORTH (N1+N2), SOUTH (V1+V2)')
print('=' * 72)

# 1a. Basic profile comparison
desc_names = ['CENTER', 'NORTH', 'SOUTH']
print()
print('Profile comparison:')
print(f'{"Region":<10} {"Tokens":<8} {"Middles":<9} {"Bridge%":<10} {"HUB%":<8}')
print('-' * 50)

analysis1 = {}
for name in desc_names:
    n_tok = len(desc_words[name])
    n_mid = len(desc_middles[name])
    n_bridge_tok = sum(1 for w in desc_words[name] if get_middle(w) in bridge_middles)
    bridge_pct = safe_pct(n_bridge_tok, n_tok)
    n_hub_tok = sum(1 for w in desc_words[name] if get_middle(w) in hub_middles)
    hub_pct = safe_pct(n_hub_tok, n_tok)
    print(f'{name:<10} {n_tok:<8} {n_mid:<9} {bridge_pct:<10.1%} {hub_pct:<8.1%}')
    analysis1[name] = {
        'n_tokens': n_tok,
        'n_unique_middles': n_mid,
        'bridge_pct': bridge_pct,
        'hub_pct': hub_pct,
    }

# 1b. Affordance bin distribution
print()
print('Affordance bin distribution (token counts):')
all_bins_used = sorted(set(
    b for bc in desc_bin_counts.values() for b in bc
))
header = f'{"Bin":<22}'
for name in desc_names:
    header += f'{name:>10}'
print(header)
print('-' * (22 + 10 * len(desc_names)))
for bn in all_bins_used:
    row = f'{bn:<22}'
    for name in desc_names:
        row += f'{desc_bin_counts[name].get(bn, 0):>10}'
    print(row)

for name in desc_names:
    analysis1[name]['bin_distribution'] = dict(desc_bin_counts[name])

# 1c. Prefix lane distribution
print()
print('Prefix lane distribution (token counts):')
all_lanes_used = sorted(set(
    l for pc in desc_prefixes.values() for l in pc
))
header = f'{"Lane":<12}'
for name in desc_names:
    header += f'{name:>10}'
print(header)
print('-' * (12 + 10 * len(desc_names)))
for lane in all_lanes_used:
    row = f'{lane:<12}'
    for name in desc_names:
        row += f'{desc_prefixes[name].get(lane, 0):>10}'
    print(row)

for name in desc_names:
    analysis1[name]['lane_distribution'] = dict(desc_prefixes[name])

# 1d. Pairwise Jaccard on MIDDLE sets
print()
desc_labels = desc_names
dn = len(desc_labels)
desc_jac_matrix = [[jaccard(desc_middles[desc_labels[i]], desc_middles[desc_labels[j]])
                     for j in range(dn)] for i in range(dn)]
print_matrix(desc_labels, desc_jac_matrix,
             'Pairwise Jaccard on MIDDLE sets (DESCRIPTION regions)')

# Key question: NORTH-SOUTH vs NORTH-CENTER vs SOUTH-CENTER
ns_jac = jaccard(desc_middles['NORTH'], desc_middles['SOUTH'])
nc_jac = jaccard(desc_middles['NORTH'], desc_middles['CENTER'])
sc_jac = jaccard(desc_middles['SOUTH'], desc_middles['CENTER'])

print()
print('KEY QUESTION: Do NORTH and SOUTH share more vocabulary (both "heat")?')
print(f'  NORTH-SOUTH  Jaccard = {ns_jac:.4f}')
print(f'  NORTH-CENTER Jaccard = {nc_jac:.4f}')
print(f'  SOUTH-CENTER Jaccard = {sc_jac:.4f}')

if ns_jac > nc_jac and ns_jac > sc_jac:
    verdict1 = 'YES: NORTH-SOUTH share most vocabulary (consistent with shared heat theme)'
elif ns_jac > nc_jac or ns_jac > sc_jac:
    verdict1 = 'PARTIAL: NORTH-SOUTH overlap is higher than one cardinal-center pair but not both'
else:
    verdict1 = 'NO: NORTH-SOUTH do NOT share the most vocabulary'
print(f'  VERDICT: {verdict1}')

# Shared MIDDLEs
ns_shared = desc_middles['NORTH'] & desc_middles['SOUTH']
nc_shared = desc_middles['NORTH'] & desc_middles['CENTER']
sc_shared = desc_middles['SOUTH'] & desc_middles['CENTER']
all_three = desc_middles['NORTH'] & desc_middles['SOUTH'] & desc_middles['CENTER']

print()
print('Shared MIDDLE counts:')
print(f'  NORTH & SOUTH:  {len(ns_shared):3d}  (exclusive to N+S: {len(ns_shared - desc_middles["CENTER"])})')
print(f'  NORTH & CENTER: {len(nc_shared):3d}  (exclusive to N+C: {len(nc_shared - desc_middles["SOUTH"])})')
print(f'  SOUTH & CENTER: {len(sc_shared):3d}  (exclusive to S+C: {len(sc_shared - desc_middles["NORTH"])})')
print(f'  All three:      {len(all_three):3d}')

analysis1['pairwise_jaccard'] = {
    'NORTH_SOUTH': ns_jac,
    'NORTH_CENTER': nc_jac,
    'SOUTH_CENTER': sc_jac,
}
analysis1['shared_middles'] = {
    'NORTH_SOUTH': len(ns_shared),
    'NORTH_CENTER': len(nc_shared),
    'SOUTH_CENTER': len(sc_shared),
    'all_three': len(all_three),
    'NS_exclusive': len(ns_shared - desc_middles['CENTER']),
    'NC_exclusive': len(nc_shared - desc_middles['SOUTH']),
    'SC_exclusive': len(sc_shared - desc_middles['NORTH']),
}
analysis1['verdict'] = verdict1


# =====================================================================
# ANALYSIS 2: LABEL region clustering
# =====================================================================
print()
print('=' * 72)
print('ANALYSIS 2: LABEL REGION CLUSTERING')
print('Which label regions share vocabulary? (could indicate same rosette)')
print('=' * 72)

# 2a. Pairwise Jaccard between all LABEL regions
label_n = len(LABEL_REGIONS)
label_jac_matrix = [[jaccard(region_middles.get(LABEL_REGIONS[i], set()),
                              region_middles.get(LABEL_REGIONS[j], set()))
                      for j in range(label_n)] for i in range(label_n)]
print_matrix(LABEL_REGIONS, label_jac_matrix,
             'Pairwise Jaccard between LABEL regions')

# 2b. Each LABEL vs each DESCRIPTION region
print()
print('LABEL-to-DESCRIPTION proximity (Jaccard):')
print(f'{"LABEL":<8}', end='')
for dname in desc_names:
    print(f'{dname:>10}', end='')
print(f'{"  Closest":>12}')
print('-' * (8 + 10 * len(desc_names) + 12))

label_desc_proximity = {}
for lr in LABEL_REGIONS:
    lr_mids = region_middles.get(lr, set())
    row = f'{lr:<8}'
    jacs = {}
    for dname in desc_names:
        j = jaccard(lr_mids, desc_middles[dname])
        jacs[dname] = j
        row += f'{j:>10.4f}'
    closest = max(jacs, key=jacs.get) if jacs else '?'
    row += f'  {closest:>10}'
    print(row)
    label_desc_proximity[lr] = {'jaccards': jacs, 'closest': closest}

# 2c. Hierarchical clustering if scipy available
analysis2 = {
    'label_jaccard_matrix': label_jac_matrix,
    'label_regions': LABEL_REGIONS,
    'label_desc_proximity': label_desc_proximity,
}

try:
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import squareform

    # Convert Jaccard similarity to distance (1 - Jaccard)
    dist_matrix = [[1.0 - label_jac_matrix[i][j]
                     for j in range(label_n)] for i in range(label_n)]
    # squareform expects condensed form
    condensed = []
    for i in range(label_n):
        for j in range(i + 1, label_n):
            condensed.append(dist_matrix[i][j])

    Z = linkage(condensed, method='average')

    print()
    print('Hierarchical clustering (average linkage):')
    print('  Merge order (distance = 1 - Jaccard):')
    for step_i in range(len(Z)):
        c1 = int(Z[step_i][0])
        c2 = int(Z[step_i][1])
        dist = Z[step_i][2]
        n_members = int(Z[step_i][3])

        def cluster_label(idx):
            if idx < label_n:
                return LABEL_REGIONS[idx]
            else:
                return f'cluster_{idx - label_n}'

        print(f'  Step {step_i + 1}: merge {cluster_label(c1)} + {cluster_label(c2)}'
              f'  dist={dist:.4f}  size={n_members}')

    # Cut at threshold for interpretable clusters
    for n_clust in [2, 3, 4]:
        clusters = fcluster(Z, t=n_clust, criterion='maxclust')
        print(f'  {n_clust} clusters: ', end='')
        cluster_groups = defaultdict(list)
        for idx, cl in enumerate(clusters):
            cluster_groups[cl].append(LABEL_REGIONS[idx])
        for cl in sorted(cluster_groups):
            print(f'  [{", ".join(cluster_groups[cl])}]', end='')
        print()

    analysis2['clustering_available'] = True
    analysis2['linkage'] = [[float(x) for x in row] for row in Z]

except ImportError:
    print()
    print('(scipy not available -- printing distance matrix only)')
    print()
    print('Distance matrix (1 - Jaccard):')
    dist_matrix = [[1.0 - label_jac_matrix[i][j]
                     for j in range(label_n)] for i in range(label_n)]
    print_matrix(LABEL_REGIONS, dist_matrix, 'LABEL Distance Matrix')
    analysis2['clustering_available'] = False


# =====================================================================
# ANALYSIS 3: Visual feature vocabulary signatures
# =====================================================================
print()
print('=' * 72)
print('ANALYSIS 3: VISUAL FEATURE VOCABULARY SIGNATURES')
print('Testing: visual similarity = vocabulary similarity?')
print('=' * 72)

# Which DESCRIPTION regions can we test?
# CENTER, NORTH, SOUTH are the only ones with confirmed region mappings
# Corners and other cardinals (EAST, WEST, NW, NE, SW, SE) have no mapped regions

# Tags that include testable positions:
testable_tags = {}
for tag, positions in VISUAL_TAGS.items():
    testable = [p for p in positions if p in desc_middles]
    if testable:
        testable_tags[tag] = testable

print()
print('Visual tags with testable positions (from DESCRIPTION regions):')
for tag, positions in sorted(testable_tags.items()):
    print(f'  {tag:<18}: {", ".join(positions)}')

print()
print('Tags with NO testable positions (need LABEL mapping):')
for tag, positions in sorted(VISUAL_TAGS.items()):
    testable = [p for p in positions if p in desc_middles]
    if not testable:
        print(f'  {tag:<18}: {", ".join(positions)} -- all unmapped')

# Pool MIDDLEs for each testable tag
tag_middles = {}
for tag, positions in testable_tags.items():
    pooled = set()
    for pos in positions:
        pooled |= desc_middles[pos]
    tag_middles[tag] = pooled

# Key test: NORTH+SOUTH overlap vs NORTH+CENTER and SOUTH+CENTER
# Visual prediction: NORTH and SOUTH both have "sharp/heat" theme
# If visual = vocab, then NORTH-SOUTH overlap > NORTH-CENTER and SOUTH-CENTER

print()
print('CORE TEST: Visual similarity predicts vocabulary similarity?')
print()
print('Visual similarity groupings (from observation):')
print('  NORTH + SOUTH = both sharp/heat/energy')
print('  CENTER = apparatus (different visual theme)')
print()
print('Vocabulary similarity (Jaccard):')
print(f'  NORTH-SOUTH (same visual):  {ns_jac:.4f}')
print(f'  NORTH-CENTER (diff visual): {nc_jac:.4f}')
print(f'  SOUTH-CENTER (diff visual): {sc_jac:.4f}')
print()

# Also compare: which affordance bins are shared?
print('Shared affordance bin profile (NORTH vs SOUTH):')
ns_shared_binned = Counter()
for mid in ns_shared:
    bn = mid_to_bin.get(mid)
    if bn is not None and bn in FUNCTIONAL_BINS:
        ns_shared_binned[BIN_LABELS[bn]] += 1
for bn_label, count in ns_shared_binned.most_common():
    print(f'  {bn_label:<22}: {count}')

print()
print('Shared affordance bin profile (NORTH vs CENTER):')
nc_shared_binned = Counter()
for mid in nc_shared:
    bn = mid_to_bin.get(mid)
    if bn is not None and bn in FUNCTIONAL_BINS:
        nc_shared_binned[BIN_LABELS[bn]] += 1
for bn_label, count in nc_shared_binned.most_common():
    print(f'  {bn_label:<22}: {count}')

print()
print('Shared affordance bin profile (SOUTH vs CENTER):')
sc_shared_binned = Counter()
for mid in sc_shared:
    bn = mid_to_bin.get(mid)
    if bn is not None and bn in FUNCTIONAL_BINS:
        sc_shared_binned[BIN_LABELS[bn]] += 1
for bn_label, count in sc_shared_binned.most_common():
    print(f'  {bn_label:<22}: {count}')

# STARS tag: NORTH + SOUTH both have stars, CENTER does not
stars_positions = [p for p in VISUAL_TAGS['STARS'] if p in desc_middles]
apparatus_positions = [p for p in VISUAL_TAGS['APPARATUS'] if p in desc_middles]

if stars_positions and apparatus_positions:
    stars_pool = set()
    for p in stars_positions:
        stars_pool |= desc_middles[p]
    apparatus_pool = set()
    for p in apparatus_positions:
        apparatus_pool |= desc_middles[p]
    stars_apparatus_jac = jaccard(stars_pool, apparatus_pool)
    print()
    print(f'STARS pool ({", ".join(stars_positions)}) vs APPARATUS pool ({", ".join(apparatus_positions)}):')
    print(f'  Jaccard = {stars_apparatus_jac:.4f}')
    print(f'  STARS unique MIDDLEs (not in APPARATUS): {len(stars_pool - apparatus_pool)}')
    print(f'  APPARATUS unique MIDDLEs (not in STARS): {len(apparatus_pool - stars_pool)}')

analysis3 = {
    'testable_tags': {t: p for t, p in testable_tags.items()},
    'tag_middle_counts': {t: len(m) for t, m in tag_middles.items()},
    'ns_jac': ns_jac,
    'nc_jac': nc_jac,
    'sc_jac': sc_jac,
    'ns_shared_bins': dict(ns_shared_binned),
    'nc_shared_bins': dict(nc_shared_binned),
    'sc_shared_bins': dict(sc_shared_binned),
}


# =====================================================================
# ANALYSIS 4: Unique vocabulary by region
# =====================================================================
print()
print('=' * 72)
print('ANALYSIS 4: UNIQUE VOCABULARY BY REGION')
print('MIDDLEs appearing in ONLY one DESCRIPTION region on f85v2')
print('=' * 72)

# For each DESCRIPTION region, find MIDDLEs unique to that region
# "unique" = appears in that region and no other region on f85v2

all_desc_names = list(DESCRIPTION_REGIONS.keys())

analysis4 = {}
for name in all_desc_names:
    my_middles = desc_middles[name]
    other_middles = set()
    # Union of all OTHER regions (both DESC and LABEL)
    for other_name in all_desc_names:
        if other_name != name:
            other_middles |= desc_middles[other_name]
    for lr in LABEL_REGIONS:
        other_middles |= region_middles.get(lr, set())
    # Also include D1, M3, U3 (OTHER regions)
    for other_r in ['D1', 'M3', 'U3']:
        other_middles |= region_middles.get(other_r, set())

    unique = my_middles - other_middles
    print()
    print(f'{name} signature MIDDLEs ({len(unique)} unique to this region):')

    unique_bins = Counter()
    unique_list = []
    for mid in sorted(unique):
        bn = mid_to_bin.get(mid)
        bn_label = BIN_LABELS.get(bn, '?') if bn is not None else '?'
        is_bridge = mid in bridge_middles
        flag = ' [BRIDGE]' if is_bridge else ''
        print(f'  {mid:<14} bin={bn_label:<22}{flag}')
        if bn is not None and bn in FUNCTIONAL_BINS:
            unique_bins[BIN_LABELS[bn]] += 1
        unique_list.append({
            'middle': mid,
            'bin': bn_label if bn is not None else None,
            'is_bridge': is_bridge,
        })

    if unique_bins:
        print(f'  Bin summary: ', end='')
        for bn_label, count in unique_bins.most_common():
            print(f'{bn_label}={count}  ', end='')
        print()
    else:
        print('  (no bins assigned)')

    analysis4[name] = {
        'n_unique': len(unique),
        'middles': unique_list,
        'bin_summary': dict(unique_bins),
    }

# Cross-region comparison
print()
print('Unique MIDDLE counts summary:')
for name in all_desc_names:
    total = len(desc_middles[name])
    uniq = analysis4[name]['n_unique']
    pct = safe_pct(uniq, total)
    print(f'  {name:<10}: {uniq:3d}/{total:3d} unique ({pct:.1%})')


# =====================================================================
# ANALYSIS 5: B-corpus section correlation
# =====================================================================
print()
print('=' * 72)
print('ANALYSIS 5: B-CORPUS SECTION CORRELATION')
print('Which B sections share vocabulary with each DESCRIPTION region?')
print('=' * 72)

analysis5 = {}

for name in all_desc_names:
    my_middles = desc_middles[name]
    if not my_middles:
        continue

    section_overlap = {}
    for sec in b_sections:
        sec_mids = b_section_middles[sec]
        shared = my_middles & sec_mids
        jac = jaccard(my_middles, sec_mids)
        coverage = safe_pct(len(shared), len(my_middles))
        section_overlap[sec] = {
            'shared': len(shared),
            'jaccard': jac,
            'coverage': coverage,
        }

    print()
    print(f'{name} ({len(my_middles)} MIDDLEs) vs B sections:')
    print(f'  {"Section":<15} {"Shared":<8} {"Coverage":<12} {"Jaccard":<10}')
    print(f'  {"-" * 45}')
    for sec in sorted(section_overlap, key=lambda s: -section_overlap[s]['coverage']):
        so = section_overlap[sec]
        print(f'  {sec:<15} {so["shared"]:<8} {so["coverage"]:<12.1%} {so["jaccard"]:<10.4f}')

    analysis5[name] = section_overlap

# Cross-region comparison: do regions differ in their B-section affinity?
print()
print('Comparative B-section affinity (coverage %):')
header = f'{"Section":<15}'
for name in all_desc_names:
    header += f'{name:>10}'
print(header)
print('-' * (15 + 10 * len(all_desc_names)))
for sec in b_sections:
    row = f'{sec:<15}'
    for name in all_desc_names:
        cov = analysis5.get(name, {}).get(sec, {}).get('coverage', 0.0)
        row += f'{cov:>10.1%}'
    print(row)

# Highlight biggest differences
print()
print('Largest section affinity differences between regions:')
diffs = []
for sec in b_sections:
    coverages = []
    for name in all_desc_names:
        cov = analysis5.get(name, {}).get(sec, {}).get('coverage', 0.0)
        coverages.append((name, cov))
    coverages.sort(key=lambda x: x[1])
    spread = coverages[-1][1] - coverages[0][1]
    diffs.append((sec, spread, coverages[0], coverages[-1]))
diffs.sort(key=lambda x: -x[1])
for sec, spread, (low_name, low_val), (high_name, high_val) in diffs[:5]:
    print(f'  {sec:<15}: spread={spread:.1%}  '
          f'(low: {low_name}={low_val:.1%}, high: {high_name}={high_val:.1%})')


# =====================================================================
# SUMMARY
# =====================================================================
print()
print('=' * 72)
print('SUMMARY OF FINDINGS')
print('=' * 72)

print()
print('1. DESCRIPTION REGION COMPARISON:')
print(f'   NORTH-SOUTH Jaccard: {ns_jac:.4f}')
print(f'   NORTH-CENTER Jaccard: {nc_jac:.4f}')
print(f'   SOUTH-CENTER Jaccard: {sc_jac:.4f}')
print(f'   Verdict: {verdict1}')

print()
print('2. LABEL CLUSTERING:')
closest_counts = Counter(v['closest'] for v in label_desc_proximity.values())
for desc_name, count in closest_counts.most_common():
    labels_closest = [lr for lr in LABEL_REGIONS if label_desc_proximity[lr]['closest'] == desc_name]
    print(f'   {count} label regions closest to {desc_name}: {", ".join(labels_closest)}')

print()
print('3. VISUAL-VOCABULARY CORRELATION:')
if ns_jac > max(nc_jac, sc_jac):
    print('   Visually similar rosettes (NORTH+SOUTH) DO share more vocabulary')
    print('   than visually dissimilar pairs (cardinal vs CENTER).')
    vis_verdict = 'SUPPORTED'
else:
    print('   Visually similar rosettes (NORTH+SOUTH) do NOT clearly share more')
    print('   vocabulary than visually dissimilar pairs.')
    vis_verdict = 'NOT_SUPPORTED'
print(f'   Visual-vocabulary correlation: {vis_verdict}')

print()
print('4. SIGNATURE MIDDLEs:')
for name in all_desc_names:
    n_uniq = analysis4[name]['n_unique']
    dominant_bin = 'none'
    if analysis4[name]['bin_summary']:
        dominant_bin = max(analysis4[name]['bin_summary'], key=analysis4[name]['bin_summary'].get)
    print(f'   {name}: {n_uniq} unique MIDDLEs, dominant bin: {dominant_bin}')

print()
print('5. B-SECTION AFFINITY:')
for name in all_desc_names:
    if name in analysis5:
        top_sec = max(analysis5[name], key=lambda s: analysis5[name][s]['coverage'])
        top_cov = analysis5[name][top_sec]['coverage']
        print(f'   {name}: highest affinity with {top_sec} ({top_cov:.1%} coverage)')


# ── Save results ─────────────────────────────────────────────────────────────

output = {
    'analysis_1_description_comparison': analysis1,
    'analysis_2_label_clustering': {
        'label_regions': LABEL_REGIONS,
        'jaccard_matrix': label_jac_matrix,
        'label_desc_proximity': {
            lr: {
                'jaccards': v['jaccards'],
                'closest': v['closest'],
            } for lr, v in label_desc_proximity.items()
        },
        'clustering_available': analysis2.get('clustering_available', False),
    },
    'analysis_3_visual_signatures': analysis3,
    'analysis_4_unique_vocabulary': analysis4,
    'analysis_5_b_section_correlation': analysis5,
    'summary': {
        'ns_jaccard': ns_jac,
        'nc_jaccard': nc_jac,
        'sc_jaccard': sc_jac,
        'visual_vocab_verdict': vis_verdict,
        'analysis1_verdict': verdict1,
        'label_closest_counts': dict(closest_counts),
    },
}

out_path = RESULTS / 'visual_vocabulary_correlation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(output), f, indent=2)
print()
print(f'Results saved to: {out_path}')
print('Done.')

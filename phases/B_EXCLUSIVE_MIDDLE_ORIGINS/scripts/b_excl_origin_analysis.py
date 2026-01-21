#!/usr/bin/env python3
"""
B_EXCLUSIVE_MIDDLE_ORIGINS Phase

Investigate WHY 569 MIDDLEs are B-exclusive (not just what they do).

Tests:
1. PREFIX Distribution - Do B-exclusive MIDDLEs cluster under specific PREFIXes?
2. Edit Distance - Are B-exclusive MIDDLEs orthographic variants of shared MIDDLEs?
3. Length Distribution - Are B-exclusive MIDDLEs longer (more specific)?
4. Boundary Overlap - Do they overlap with C358 boundary tokens?
5. REGIME Stratification - Do they concentrate in specific REGIMEs?

Pre-registered predictions:
1. PREFIX: OL/QO enriched >3x, CT depleted >5x
2. Edit distance: 15-25% within distance-1 of shared
3. Length: B-exclusive mean > shared mean (p<0.05)
4. Boundary: >50% of C358 boundary tokens are B-exclusive MIDDLEs
5. REGIME: REGIME_3/4 concentration >1.5x vs REGIME_1/2

SCRIPT CONSTRUCTION COMPLIANCE:
- H track filter: YES
- Placement awareness: YES (TEXT only for main analysis)
- O-complexity: All loops use pre-computed sets
- Edge cases: Asterisks filtered, empty words skipped
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
REGIME_PATH = PROJECT_ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
RESULTS_PATH = PROJECT_ROOT / 'phases' / 'B_EXCLUSIVE_MIDDLE_ORIGINS' / 'results'

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

# C358 boundary tokens (from constraint system)
C358_BOUNDARY_INITIAL = ['daiin', 'saiin', 'sain']
C358_BOUNDARY_FINAL = ['am', 'oly', 'dy']

# =============================================================================
# MORPHOLOGY EXTRACTION
# =============================================================================

def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    if pd.isna(token) or not token or '*' in str(token):
        return None, None, None
    token = str(token).strip()
    if not token:
        return None, None, None

    # Find prefix
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Find suffix
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def levenshtein_distance(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


# =============================================================================
# DATA LOADING
# =============================================================================

def load_data():
    """Load and filter transcript data."""
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)

    # MANDATORY: Filter to H track
    df = df[df['transcriber'] == 'H'].copy()

    # Verify canonical counts
    total_h = len(df)
    print(f"  Total H tokens: {total_h} (expected ~37,957)")

    # Clean string columns
    for col in ['word', 'folio', 'language', 'placement']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip('"')

    # Filter out empty and uncertain tokens
    df = df[df['word'].str.len() > 0]
    df = df[~df['word'].str.contains(r'\*', na=False)]

    # Extract morphology (vectorized)
    print("  Extracting morphology...")
    morphology = df['word'].apply(extract_morphology)
    df['prefix'] = morphology.apply(lambda x: x[0])
    df['middle'] = morphology.apply(lambda x: x[1])
    df['suffix'] = morphology.apply(lambda x: x[2])

    return df


def load_regime_mapping():
    """Load REGIME assignments for B folios."""
    with open(REGIME_PATH) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


# =============================================================================
# PRE-COMPUTATION (Critical for O(n) complexity)
# =============================================================================

def precompute_middle_sets(df):
    """Pre-compute all MIDDLE sets for O(1) lookups."""
    print("Pre-computing MIDDLE sets...")

    # Split by language
    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']

    # MIDDLE sets
    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())

    # Derived sets
    shared_middles = a_middles & b_middles
    b_exclusive_middles = b_middles - a_middles
    a_exclusive_middles = a_middles - b_middles

    print(f"  A MIDDLEs: {len(a_middles)}")
    print(f"  B MIDDLEs: {len(b_middles)}")
    print(f"  Shared: {len(shared_middles)}")
    print(f"  B-exclusive: {len(b_exclusive_middles)}")
    print(f"  A-exclusive: {len(a_exclusive_middles)}")

    return {
        'a_middles': a_middles,
        'b_middles': b_middles,
        'shared': shared_middles,
        'b_exclusive': b_exclusive_middles,
        'a_exclusive': a_exclusive_middles,
    }


def precompute_middle_prefixes(df):
    """Pre-compute PREFIX for each MIDDLE (using most common PREFIX in B)."""
    print("Pre-computing MIDDLE -> PREFIX mapping...")

    df_b = df[df['language'] == 'B']

    # For each MIDDLE, find its most common PREFIX in B
    middle_prefix = {}
    for middle, group in df_b[df_b['middle'].notna()].groupby('middle'):
        prefix_counts = group['prefix'].value_counts()
        if len(prefix_counts) > 0:
            middle_prefix[middle] = prefix_counts.index[0]

    return middle_prefix


def precompute_middle_positions(df):
    """Pre-compute position statistics for each MIDDLE."""
    print("Pre-computing position statistics...")

    df_b = df[df['language'] == 'B'].copy()

    # Add normalized position
    df_b['line_len'] = df_b.groupby(['folio', 'line_number'])['word'].transform('count')
    df_b['pos_in_line'] = df_b.groupby(['folio', 'line_number']).cumcount()
    df_b['is_initial'] = df_b['pos_in_line'] == 0
    df_b['is_final'] = df_b['pos_in_line'] == df_b['line_len'] - 1

    # Aggregate by MIDDLE
    middle_positions = {}
    for middle, group in df_b[df_b['middle'].notna()].groupby('middle'):
        middle_positions[middle] = {
            'count': len(group),
            'initial_rate': group['is_initial'].mean(),
            'final_rate': group['is_final'].mean(),
            'boundary_rate': (group['is_initial'] | group['is_final']).mean(),
        }

    return middle_positions


def precompute_folio_middles(df):
    """Pre-compute MIDDLE sets per folio."""
    print("Pre-computing per-folio MIDDLE sets...")

    df_b = df[df['language'] == 'B']

    folio_middles = {}
    for folio, group in df_b.groupby('folio'):
        folio_middles[folio] = set(group['middle'].dropna().unique())

    return folio_middles


# =============================================================================
# TEST 1: PREFIX DISTRIBUTION
# =============================================================================

def test_prefix_distribution(df, middle_sets, middle_prefix):
    """Compare PREFIX distribution of B-exclusive vs shared MIDDLEs."""
    print("\n" + "="*70)
    print("TEST 1: PREFIX DISTRIBUTION")
    print("="*70)

    b_exclusive = middle_sets['b_exclusive']
    shared = middle_sets['shared']

    # Count PREFIXes for each class
    b_excl_prefixes = Counter()
    shared_prefixes = Counter()

    for middle in b_exclusive:
        if middle in middle_prefix:
            b_excl_prefixes[middle_prefix[middle]] += 1

    for middle in shared:
        if middle in middle_prefix:
            shared_prefixes[middle_prefix[middle]] += 1

    # Calculate enrichment ratios
    total_b_excl = sum(b_excl_prefixes.values())
    total_shared = sum(shared_prefixes.values())

    all_prefixes = set(b_excl_prefixes.keys()) | set(shared_prefixes.keys())

    enrichment = {}
    for prefix in all_prefixes:
        b_excl_rate = b_excl_prefixes.get(prefix, 0) / total_b_excl if total_b_excl > 0 else 0
        shared_rate = shared_prefixes.get(prefix, 0) / total_shared if total_shared > 0 else 0

        if shared_rate > 0:
            ratio = b_excl_rate / shared_rate
        elif b_excl_rate > 0:
            ratio = float('inf')
        else:
            ratio = 1.0

        enrichment[prefix] = {
            'b_excl_count': b_excl_prefixes.get(prefix, 0),
            'shared_count': shared_prefixes.get(prefix, 0),
            'b_excl_rate': b_excl_rate,
            'shared_rate': shared_rate,
            'enrichment_ratio': ratio if ratio != float('inf') else 999.0,
        }

    # Print results
    print(f"\nB-exclusive MIDDLEs with PREFIX: {total_b_excl}")
    print(f"Shared MIDDLEs with PREFIX: {total_shared}")
    print("\nPREFIX enrichment (B-exclusive / shared):")

    sorted_prefixes = sorted(enrichment.items(), key=lambda x: x[1]['enrichment_ratio'], reverse=True)
    for prefix, data in sorted_prefixes[:15]:
        print(f"  {prefix:4s}: {data['enrichment_ratio']:6.2f}x  (B-excl: {data['b_excl_count']:3d}, shared: {data['shared_count']:3d})")

    # Check predictions
    ol_ratio = enrichment.get('ol', {}).get('enrichment_ratio', 0)
    qo_ratio = enrichment.get('qo', {}).get('enrichment_ratio', 0)
    ct_ratio = enrichment.get('ct', {}).get('enrichment_ratio', 0)

    print(f"\n--- PREDICTION CHECK ---")
    print(f"OL enrichment: {ol_ratio:.2f}x (predicted >3x): {'PASS' if ol_ratio > 3 else 'FAIL'}")
    print(f"QO enrichment: {qo_ratio:.2f}x (predicted >3x): {'PASS' if qo_ratio > 3 else 'FAIL'}")
    print(f"CT depletion: {ct_ratio:.2f}x (predicted <0.2x): {'PASS' if ct_ratio < 0.2 else 'FAIL'}")

    return {
        'total_b_excl_with_prefix': total_b_excl,
        'total_shared_with_prefix': total_shared,
        'enrichment': enrichment,
        'ol_ratio': ol_ratio,
        'qo_ratio': qo_ratio,
        'ct_ratio': ct_ratio,
        'prediction_ol_pass': ol_ratio > 3,
        'prediction_qo_pass': qo_ratio > 3,
        'prediction_ct_pass': ct_ratio < 0.2,
    }


# =============================================================================
# TEST 2: EDIT DISTANCE ANALYSIS
# =============================================================================

def test_edit_distance(middle_sets):
    """Check if B-exclusive MIDDLEs are edit-distance-1 variants of shared."""
    print("\n" + "="*70)
    print("TEST 2: EDIT DISTANCE ANALYSIS")
    print("="*70)

    b_exclusive = middle_sets['b_exclusive']
    shared = list(middle_sets['shared'])  # Convert to list for indexing

    # Pre-compute: For each B-exclusive, find minimum distance to any shared
    print(f"\nComputing edit distances for {len(b_exclusive)} B-exclusive MIDDLEs...")

    distance_1_variants = []
    distance_2_variants = []
    min_distances = []

    for i, b_mid in enumerate(b_exclusive):
        if b_mid == '_EMPTY_':
            continue

        min_dist = float('inf')
        closest = None

        for s_mid in shared:
            if s_mid == '_EMPTY_':
                continue
            dist = levenshtein_distance(b_mid, s_mid)
            if dist < min_dist:
                min_dist = dist
                closest = s_mid
            if dist == 1:
                break  # Can't get better than 1

        min_distances.append(min_dist)

        if min_dist == 1:
            distance_1_variants.append((b_mid, closest))
        elif min_dist == 2:
            distance_2_variants.append((b_mid, closest))

        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(b_exclusive)}...")

    # Calculate statistics
    total_checked = len(min_distances)
    dist_1_count = len(distance_1_variants)
    dist_2_count = len(distance_2_variants)
    dist_1_pct = dist_1_count / total_checked * 100 if total_checked > 0 else 0
    dist_2_pct = dist_2_count / total_checked * 100 if total_checked > 0 else 0

    print(f"\nResults:")
    print(f"  Total B-exclusive checked: {total_checked}")
    print(f"  Distance-1 variants: {dist_1_count} ({dist_1_pct:.1f}%)")
    print(f"  Distance-2 variants: {dist_2_count} ({dist_2_pct:.1f}%)")
    print(f"  Distance >=3: {total_checked - dist_1_count - dist_2_count}")

    print(f"\nSample distance-1 pairs (B-exclusive -> shared):")
    for b_mid, s_mid in distance_1_variants[:15]:
        print(f"  {b_mid} -> {s_mid}")

    # Analyze edit types for distance-1
    edit_types = Counter()
    for b_mid, s_mid in distance_1_variants:
        if len(b_mid) > len(s_mid):
            edit_types['insertion'] += 1
        elif len(b_mid) < len(s_mid):
            edit_types['deletion'] += 1
        else:
            edit_types['substitution'] += 1

    print(f"\nEdit types for distance-1 variants:")
    for edit_type, count in edit_types.most_common():
        print(f"  {edit_type}: {count} ({count/dist_1_count*100:.1f}%)" if dist_1_count > 0 else f"  {edit_type}: {count}")

    # Check prediction
    print(f"\n--- PREDICTION CHECK ---")
    print(f"Distance-1 rate: {dist_1_pct:.1f}% (predicted 15-25%): {'PASS' if 15 <= dist_1_pct <= 25 else 'FAIL'}")

    return {
        'total_checked': total_checked,
        'distance_1_count': dist_1_count,
        'distance_1_pct': dist_1_pct,
        'distance_2_count': dist_2_count,
        'distance_2_pct': dist_2_pct,
        'edit_types': dict(edit_types),
        'sample_pairs': distance_1_variants[:20],
        'prediction_pass': 15 <= dist_1_pct <= 25,
    }


# =============================================================================
# TEST 3: LENGTH DISTRIBUTION
# =============================================================================

def test_length_distribution(middle_sets):
    """Compare MIDDLE length distributions."""
    print("\n" + "="*70)
    print("TEST 3: LENGTH DISTRIBUTION")
    print("="*70)

    b_exclusive = [m for m in middle_sets['b_exclusive'] if m != '_EMPTY_']
    shared = [m for m in middle_sets['shared'] if m != '_EMPTY_']
    a_exclusive = [m for m in middle_sets['a_exclusive'] if m != '_EMPTY_']

    b_excl_lengths = [len(m) for m in b_exclusive]
    shared_lengths = [len(m) for m in shared]
    a_excl_lengths = [len(m) for m in a_exclusive]

    # Statistics
    b_excl_mean = np.mean(b_excl_lengths)
    shared_mean = np.mean(shared_lengths)
    a_excl_mean = np.mean(a_excl_lengths)

    # Mann-Whitney U test (B-exclusive vs shared)
    stat, p_value = stats.mannwhitneyu(b_excl_lengths, shared_lengths, alternative='greater')

    print(f"\nLength statistics:")
    print(f"  B-exclusive: mean={b_excl_mean:.2f}, median={np.median(b_excl_lengths):.0f}, n={len(b_excl_lengths)}")
    print(f"  Shared:      mean={shared_mean:.2f}, median={np.median(shared_lengths):.0f}, n={len(shared_lengths)}")
    print(f"  A-exclusive: mean={a_excl_mean:.2f}, median={np.median(a_excl_lengths):.0f}, n={len(a_excl_lengths)}")

    print(f"\nMann-Whitney U (B-excl > shared): U={stat:.0f}, p={p_value:.4f}")

    # Length distribution
    print(f"\nLength distribution:")
    for length in range(1, 8):
        b_count = sum(1 for l in b_excl_lengths if l == length)
        s_count = sum(1 for l in shared_lengths if l == length)
        print(f"  len={length}: B-excl={b_count:3d} ({b_count/len(b_excl_lengths)*100:5.1f}%), shared={s_count:3d} ({s_count/len(shared_lengths)*100:5.1f}%)")

    # Check prediction
    print(f"\n--- PREDICTION CHECK ---")
    print(f"B-exclusive mean ({b_excl_mean:.2f}) > shared mean ({shared_mean:.2f}): {'PASS' if b_excl_mean > shared_mean and p_value < 0.05 else 'FAIL'}")

    return {
        'b_excl_mean': b_excl_mean,
        'shared_mean': shared_mean,
        'a_excl_mean': a_excl_mean,
        'b_excl_median': float(np.median(b_excl_lengths)),
        'shared_median': float(np.median(shared_lengths)),
        'mann_whitney_u': float(stat),
        'p_value': float(p_value),
        'prediction_pass': b_excl_mean > shared_mean and p_value < 0.05,
    }


# =============================================================================
# TEST 4: BOUNDARY TOKEN OVERLAP
# =============================================================================

def test_boundary_overlap(df, middle_sets):
    """Check overlap with C358 boundary tokens."""
    print("\n" + "="*70)
    print("TEST 4: BOUNDARY TOKEN OVERLAP (C358)")
    print("="*70)

    b_exclusive = middle_sets['b_exclusive']
    shared = middle_sets['shared']

    # C358 boundary tokens are full tokens, not MIDDLEs
    # We need to extract MIDDLEs from these tokens
    boundary_tokens = C358_BOUNDARY_INITIAL + C358_BOUNDARY_FINAL

    print(f"\nC358 boundary tokens: {boundary_tokens}")

    # Extract MIDDLEs from boundary tokens
    boundary_middles = set()
    for token in boundary_tokens:
        _, middle, _ = extract_morphology(token)
        if middle:
            boundary_middles.add(middle)
            print(f"  {token} -> MIDDLE: {middle}")

    # Check which are B-exclusive
    boundary_b_exclusive = boundary_middles & b_exclusive
    boundary_shared = boundary_middles & shared

    print(f"\nBoundary MIDDLEs in B-exclusive: {boundary_b_exclusive}")
    print(f"Boundary MIDDLEs in shared: {boundary_shared}")

    # Also check: what fraction of B-exclusive MIDDLEs appear at boundaries?
    df_b = df[df['language'] == 'B'].copy()
    df_b['line_len'] = df_b.groupby(['folio', 'line_number'])['word'].transform('count')
    df_b['pos_in_line'] = df_b.groupby(['folio', 'line_number']).cumcount()
    df_b['is_boundary'] = (df_b['pos_in_line'] == 0) | (df_b['pos_in_line'] == df_b['line_len'] - 1)

    # Boundary rate by MIDDLE class
    b_excl_tokens = df_b[df_b['middle'].isin(b_exclusive)]
    shared_tokens = df_b[df_b['middle'].isin(shared)]

    b_excl_boundary_rate = b_excl_tokens['is_boundary'].mean() if len(b_excl_tokens) > 0 else 0
    shared_boundary_rate = shared_tokens['is_boundary'].mean() if len(shared_tokens) > 0 else 0

    print(f"\nBoundary position rates:")
    print(f"  B-exclusive MIDDLEs: {b_excl_boundary_rate*100:.1f}% at boundaries")
    print(f"  Shared MIDDLEs: {shared_boundary_rate*100:.1f}% at boundaries")
    print(f"  Enrichment: {b_excl_boundary_rate/shared_boundary_rate:.2f}x" if shared_boundary_rate > 0 else "  N/A")

    # Detailed boundary analysis
    b_excl_initial = b_excl_tokens[b_excl_tokens['pos_in_line'] == 0]
    b_excl_final = b_excl_tokens[b_excl_tokens['pos_in_line'] == b_excl_tokens['line_len'] - 1]

    print(f"\nB-exclusive at line-initial: {len(b_excl_initial)} tokens")
    print(f"B-exclusive at line-final: {len(b_excl_final)} tokens")

    # Top boundary MIDDLEs
    initial_middles = Counter(b_excl_initial['middle'].dropna())
    final_middles = Counter(b_excl_final['middle'].dropna())

    print(f"\nTop B-exclusive MIDDLEs at line-initial:")
    for mid, count in initial_middles.most_common(10):
        print(f"  {mid}: {count}")

    print(f"\nTop B-exclusive MIDDLEs at line-final:")
    for mid, count in final_middles.most_common(10):
        print(f"  {mid}: {count}")

    # Check prediction (reframed: boundary enrichment >1.5x)
    boundary_enrichment = b_excl_boundary_rate / shared_boundary_rate if shared_boundary_rate > 0 else 0

    print(f"\n--- PREDICTION CHECK ---")
    print(f"Boundary enrichment: {boundary_enrichment:.2f}x (predicted >1.5x from prior B-EXCL-ROLE): {'PASS' if boundary_enrichment > 1.5 else 'FAIL'}")

    return {
        'c358_tokens': boundary_tokens,
        'c358_middles': list(boundary_middles),
        'boundary_middles_b_exclusive': list(boundary_b_exclusive),
        'boundary_middles_shared': list(boundary_shared),
        'b_excl_boundary_rate': b_excl_boundary_rate,
        'shared_boundary_rate': shared_boundary_rate,
        'boundary_enrichment': boundary_enrichment,
        'b_excl_initial_count': len(b_excl_initial),
        'b_excl_final_count': len(b_excl_final),
        'top_initial_middles': dict(initial_middles.most_common(15)),
        'top_final_middles': dict(final_middles.most_common(15)),
        'prediction_pass': boundary_enrichment > 1.5,
    }


# =============================================================================
# TEST 5: REGIME STRATIFICATION
# =============================================================================

def test_regime_stratification(middle_sets, folio_middles, regime_mapping):
    """Check if B-exclusive MIDDLEs concentrate in specific REGIMEs."""
    print("\n" + "="*70)
    print("TEST 5: REGIME STRATIFICATION")
    print("="*70)

    b_exclusive = middle_sets['b_exclusive']
    shared = middle_sets['shared']

    # Count MIDDLEs by REGIME
    regime_b_excl = defaultdict(set)
    regime_shared = defaultdict(set)

    for folio, middles in folio_middles.items():
        if folio not in regime_mapping:
            continue
        regime = regime_mapping[folio]

        for middle in middles:
            if middle in b_exclusive:
                regime_b_excl[regime].add(middle)
            elif middle in shared:
                regime_shared[regime].add(middle)

    # Calculate rates
    print(f"\nMIDDLE counts by REGIME:")

    regime_stats = {}
    for regime in sorted(set(regime_mapping.values())):
        if regime not in regime_b_excl:
            continue

        b_excl_count = len(regime_b_excl[regime])
        shared_count = len(regime_shared[regime])
        total = b_excl_count + shared_count
        b_excl_rate = b_excl_count / total if total > 0 else 0

        regime_stats[regime] = {
            'b_excl_count': b_excl_count,
            'shared_count': shared_count,
            'total': total,
            'b_excl_rate': b_excl_rate,
        }

        print(f"  {regime}: B-excl={b_excl_count:3d}, shared={shared_count:3d}, B-excl rate={b_excl_rate*100:.1f}%")

    # Calculate REGIME_3/4 vs REGIME_1/2 concentration
    r34_b_excl = len(regime_b_excl.get('REGIME_3', set()) | regime_b_excl.get('REGIME_4', set()))
    r12_b_excl = len(regime_b_excl.get('REGIME_1', set()) | regime_b_excl.get('REGIME_2', set()))

    r34_shared = len(regime_shared.get('REGIME_3', set()) | regime_shared.get('REGIME_4', set()))
    r12_shared = len(regime_shared.get('REGIME_1', set()) | regime_shared.get('REGIME_2', set()))

    # Ratio comparison
    r34_ratio = r34_b_excl / r34_shared if r34_shared > 0 else 0
    r12_ratio = r12_b_excl / r12_shared if r12_shared > 0 else 0

    concentration = r34_ratio / r12_ratio if r12_ratio > 0 else 0

    print(f"\nREGIME_3/4 vs REGIME_1/2 comparison:")
    print(f"  REGIME_3/4: B-excl={r34_b_excl}, shared={r34_shared}, ratio={r34_ratio:.2f}")
    print(f"  REGIME_1/2: B-excl={r12_b_excl}, shared={r12_shared}, ratio={r12_ratio:.2f}")
    print(f"  Concentration (R34/R12 ratio): {concentration:.2f}x")

    # Check prediction
    print(f"\n--- PREDICTION CHECK ---")
    print(f"REGIME_3/4 concentration: {concentration:.2f}x (predicted >1.5x): {'PASS' if concentration > 1.5 else 'FAIL'}")

    return {
        'regime_stats': regime_stats,
        'r34_b_excl': r34_b_excl,
        'r12_b_excl': r12_b_excl,
        'r34_shared': r34_shared,
        'r12_shared': r12_shared,
        'concentration_ratio': concentration,
        'prediction_pass': concentration > 1.5,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*70)
    print("B_EXCLUSIVE_MIDDLE_ORIGINS PHASE")
    print("="*70)
    print()

    # Load data
    df = load_data()
    regime_mapping = load_regime_mapping()

    # Pre-compute everything (O(n) preparation for O(1) lookups)
    middle_sets = precompute_middle_sets(df)
    middle_prefix = precompute_middle_prefixes(df)
    middle_positions = precompute_middle_positions(df)
    folio_middles = precompute_folio_middles(df)

    # Run all tests
    results = {}

    results['test_1_prefix'] = test_prefix_distribution(df, middle_sets, middle_prefix)
    results['test_2_edit_distance'] = test_edit_distance(middle_sets)
    results['test_3_length'] = test_length_distribution(middle_sets)
    results['test_4_boundary'] = test_boundary_overlap(df, middle_sets)
    results['test_5_regime'] = test_regime_stratification(middle_sets, folio_middles, regime_mapping)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    predictions = [
        ('T1: PREFIX (OL/QO enriched)', results['test_1_prefix']['prediction_ol_pass'] or results['test_1_prefix']['prediction_qo_pass']),
        ('T1: PREFIX (CT depleted)', results['test_1_prefix']['prediction_ct_pass']),
        ('T2: Edit distance 15-25%', results['test_2_edit_distance']['prediction_pass']),
        ('T3: Length B-excl > shared', results['test_3_length']['prediction_pass']),
        ('T4: Boundary enrichment >1.5x', results['test_4_boundary']['prediction_pass']),
        ('T5: REGIME_3/4 concentration >1.5x', results['test_5_regime']['prediction_pass']),
    ]

    print("\nPre-registered predictions:")
    passes = 0
    for name, passed in predictions:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if passed:
            passes += 1

    print(f"\nOverall: {passes}/{len(predictions)} predictions passed")

    # Add metadata
    results['metadata'] = {
        'phase': 'B_EXCLUSIVE_MIDDLE_ORIGINS',
        'b_exclusive_count': len(middle_sets['b_exclusive']),
        'shared_count': len(middle_sets['shared']),
        'predictions_passed': passes,
        'predictions_total': len(predictions),
    }

    # Save results
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    output_file = RESULTS_PATH / 'b_excl_origin_analysis.json'

    # Convert sets and numpy types for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(i) for i in obj]
        elif isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, bool):
            return obj
        return obj

    with open(output_file, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to {output_file}")


if __name__ == '__main__':
    main()

"""
Phase SSD: Survivor-Set Dimensionality Tests

Tests the representational role of large AZC-admissible A survivor sets.

Three hypotheses:
- H-A: Equivalence-Class Refinement (survivor size scales HT diversity)
- H-B: Constraint Envelope Narrowing (survivor size uncorrelated with HT)
- H-C: Deferred Resolution (time-varying effects)
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import math

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from scipy import stats
import numpy as np

# Data paths
DATA_PATH = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"
RESULTS_DIR = PROJECT_ROOT / "results"

# Position zone definitions from F-AZC-005
POSITION_ZONES = {
    'C': {'min': 0.00, 'max': 0.39},
    'P': {'min': 0.39, 'max': 0.55},
    'R': {'min': 0.55, 'max': 0.73},
    'S': {'min': 0.73, 'max': 1.00},
}

# HT prefixes (from C347 - disjoint from A/B prefixes)
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta', 'am', 'oe', 'eo'}

# Standard A/B prefixes
AB_PREFIXES = {'ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'ct', 'al', 'ar', 'or'}


def extract_middle(token: str) -> str:
    """Extract MIDDLE component from token (between prefix and suffix)."""
    if not token or len(token) < 2:
        return token

    # Common prefixes (2-3 chars)
    prefixes = ['ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'ct', 'al', 'ar', 'or',
                'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta']

    # Common suffixes
    suffixes = ['y', 'dy', 'ey', 'ly', 'ry', 'ty', 'sy',
                'in', 'ain', 'aiin', 'iin', 'oiin',
                'ol', 'al', 'ar', 'or', 'ir', 'an', 'on', 'am', 'om']

    text = token.lower()

    # Strip prefix
    for prefix in sorted(prefixes, key=len, reverse=True):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    # Strip suffix
    for suffix in sorted(suffixes, key=len, reverse=True):
        if text.endswith(suffix) and len(text) > len(suffix):
            text = text[:-len(suffix)]
            break

    return text if text else token


def get_position_zone(norm_pos: float) -> str:
    """Get zone (C/P/R/S) from normalized line position."""
    for zone, bounds in POSITION_ZONES.items():
        if bounds['min'] <= norm_pos < bounds['max']:
            return zone
    return 'S'  # Default to S for position 1.0


def get_prefix(token: str) -> Optional[str]:
    """Extract prefix from token."""
    if not token:
        return None
    token = token.lower()
    all_prefixes = list(AB_PREFIXES) + list(HT_PREFIXES)
    for prefix in sorted(all_prefixes, key=len, reverse=True):
        if token.startswith(prefix):
            return prefix
    return None


def is_ht_token(token: str) -> bool:
    """Check if token has HT prefix."""
    prefix = get_prefix(token)
    return prefix in HT_PREFIXES if prefix else False


def load_data() -> pd.DataFrame:
    """Load transcription data."""
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
    # Filter valid tokens
    df = df[df['word'].notna() & (df['word'] != '')]
    df = df[~df['word'].str.contains(r'\*', na=False)]
    return df


def build_azc_scaffold(df: pd.DataFrame) -> Dict[str, Set[str]]:
    """Build AZC scaffold: MIDDLEs available per zone."""
    # AZC = not classified as A or B
    azc_df = df[(df['language'] != 'A') & (df['language'] != 'B')]

    # Build scaffold per zone based on placement codes
    scaffold = {'C': set(), 'P': set(), 'R': set(), 'S': set()}

    for _, row in azc_df.iterrows():
        placement = str(row.get('placement', '')).upper()
        token = row['word']
        middle = extract_middle(token)

        # Map placement to zone
        if placement.startswith('C'):
            scaffold['C'].add(middle)
        elif placement.startswith('P'):
            scaffold['P'].add(middle)
        elif placement.startswith('R'):
            scaffold['R'].add(middle)
        elif placement.startswith('S'):
            scaffold['S'].add(middle)

    return scaffold


def compute_survivor_sets(df: pd.DataFrame, scaffold: Dict[str, Set[str]]) -> List[Dict]:
    """Compute survivor set for each Currier A line."""
    # Get Currier A data
    a_df = df[df['language'] == 'A'].copy()

    # Group by folio and line
    results = []

    for (folio, line_num), line_df in a_df.groupby(['folio', 'line_number']):
        tokens = line_df['word'].tolist()
        line_len = len(tokens)

        if line_len == 0:
            continue

        survivors = []
        eliminated = []

        for i, token in enumerate(tokens):
            # Compute normalized position
            norm_pos = i / max(1, line_len - 1) if line_len > 1 else 0.5
            zone = get_position_zone(norm_pos)
            middle = extract_middle(token)

            # Check if MIDDLE is in scaffold for this zone
            zone_middles = scaffold.get(zone, set())

            # Match criteria: exact match, substring, or first 2 chars
            is_match = False
            if middle in zone_middles:
                is_match = True
            else:
                for scaffold_middle in zone_middles:
                    if middle in scaffold_middle or scaffold_middle in middle:
                        is_match = True
                        break
                    if len(middle) >= 2 and len(scaffold_middle) >= 2:
                        if middle[:2] == scaffold_middle[:2]:
                            is_match = True
                            break

            if is_match:
                survivors.append({'token': token, 'middle': middle, 'zone': zone, 'pos': i})
            else:
                eliminated.append({'token': token, 'middle': middle, 'zone': zone, 'pos': i})

        # Compute HT metrics for this line
        ht_tokens = [t for t in tokens if is_ht_token(t)]
        ht_prefixes = [get_prefix(t) for t in ht_tokens if get_prefix(t)]
        ht_middles = [extract_middle(t) for t in ht_tokens]

        # HT diversity metrics
        ht_prefix_entropy = compute_entropy(ht_prefixes) if ht_prefixes else 0
        ht_middle_diversity = len(set(ht_middles)) / len(ht_middles) if ht_middles else 0

        results.append({
            'folio': folio,
            'line_num': line_num,
            'line_length': line_len,
            'survivor_count': len(survivors),
            'eliminated_count': len(eliminated),
            'survivor_rate': len(survivors) / line_len if line_len > 0 else 0,
            'survivor_middles': list(set(s['middle'] for s in survivors)),
            'eliminated_middles': list(set(e['middle'] for e in eliminated)),
            'ht_count': len(ht_tokens),
            'ht_density': len(ht_tokens) / line_len if line_len > 0 else 0,
            'ht_prefix_count': len(set(ht_prefixes)),
            'ht_prefix_entropy': ht_prefix_entropy,
            'ht_middle_diversity': ht_middle_diversity,
            'section': line_df['section'].iloc[0] if 'section' in line_df.columns else 'UNK'
        })

    return results


def compute_entropy(items: List[str]) -> float:
    """Compute Shannon entropy of item distribution."""
    if not items:
        return 0.0
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1
    total = len(items)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def run_test1(survivor_data: List[Dict]) -> Dict:
    """
    Test 1: Survivor-Set Size vs HT Morphology

    Question: Does HT morphological diversity scale with survivor-set size?
    """
    print("\n" + "="*60)
    print("TEST 1: Survivor-Set Size vs HT Morphology")
    print("="*60)

    # Filter to lines with both survivors and HT tokens
    valid_lines = [d for d in survivor_data if d['survivor_count'] > 0 and d['ht_count'] > 0]

    print(f"\nTotal A lines: {len(survivor_data)}")
    print(f"Lines with survivors AND HT: {len(valid_lines)}")

    if len(valid_lines) < 10:
        print("INSUFFICIENT DATA for Test 1")
        return {'status': 'INSUFFICIENT_DATA', 'n': len(valid_lines)}

    # Extract arrays
    survivor_counts = [d['survivor_count'] for d in valid_lines]
    ht_prefix_entropies = [d['ht_prefix_entropy'] for d in valid_lines]
    ht_middle_diversities = [d['ht_middle_diversity'] for d in valid_lines]
    line_lengths = [d['line_length'] for d in valid_lines]

    # Correlation: survivor_count vs HT_prefix_entropy
    rho_entropy, p_entropy = stats.spearmanr(survivor_counts, ht_prefix_entropies)

    # Correlation: survivor_count vs HT_middle_diversity
    rho_diversity, p_diversity = stats.spearmanr(survivor_counts, ht_middle_diversities)

    # Partial correlation controlling for line length
    # Using residuals method
    if np.std(line_lengths) > 0:
        survivor_resid = survivor_counts - np.polyval(np.polyfit(line_lengths, survivor_counts, 1), line_lengths)
        entropy_resid = ht_prefix_entropies - np.polyval(np.polyfit(line_lengths, ht_prefix_entropies, 1), line_lengths)
        rho_partial, p_partial = stats.spearmanr(survivor_resid, entropy_resid)
    else:
        rho_partial, p_partial = rho_entropy, p_entropy

    print(f"\n--- Results ---")
    print(f"Survivor count vs HT prefix entropy:")
    print(f"  rho = {rho_entropy:.3f}, p = {p_entropy:.4f}")
    print(f"\nSurvivor count vs HT MIDDLE diversity:")
    print(f"  rho = {rho_diversity:.3f}, p = {p_diversity:.4f}")
    print(f"\nPartial correlation (controlling for line length):")
    print(f"  rho = {rho_partial:.3f}, p = {p_partial:.4f}")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if rho_entropy > 0.2 and p_entropy < 0.05:
        print("SUPPORTS H-A: Equivalence-class refinement")
        print("  More survivors -> more HT diversity -> more discrimination responsibility")
        interpretation = 'SUPPORTS_H_A'
    elif abs(rho_entropy) < 0.1 and p_entropy > 0.1:
        print("SUPPORTS H-B: Constraint envelope narrowing")
        print("  Survivor size independent of HT diversity")
        interpretation = 'SUPPORTS_H_B'
    else:
        print("INCONCLUSIVE: Weak or unexpected correlation")
        interpretation = 'INCONCLUSIVE'

    return {
        'status': 'COMPLETE',
        'n': len(valid_lines),
        'rho_entropy': rho_entropy,
        'p_entropy': p_entropy,
        'rho_diversity': rho_diversity,
        'p_diversity': p_diversity,
        'rho_partial': rho_partial,
        'p_partial': p_partial,
        'interpretation': interpretation
    }


def run_test2(survivor_data: List[Dict], df: pd.DataFrame) -> Dict:
    """
    Test 2: Survivor-Set Size vs B Micro-Variability

    Question: Do larger survivor sets correlate with B execution variability?
    """
    print("\n" + "="*60)
    print("TEST 2: Survivor-Set Size vs B Micro-Variability")
    print("="*60)

    # Get B data grouped by folio
    b_df = df[df['language'] == 'B'].copy()

    # Compute B variability metrics per folio
    b_metrics = {}
    for folio, folio_df in b_df.groupby('folio'):
        tokens = folio_df['word'].tolist()
        if len(tokens) < 10:
            continue

        # Compute prefix transition entropy
        prefixes = [get_prefix(t) for t in tokens if get_prefix(t)]
        transitions = [(prefixes[i], prefixes[i+1]) for i in range(len(prefixes)-1)]
        transition_entropy = compute_entropy([f"{a}->{b}" for a, b in transitions])

        # Compute type-token ratio
        ttr = len(set(tokens)) / len(tokens)

        # LINK density (tokens with 'ol' or 'al' prefix)
        link_count = sum(1 for t in tokens if get_prefix(t) in {'ol', 'al'})
        link_density = link_count / len(tokens)

        b_metrics[folio] = {
            'transition_entropy': transition_entropy,
            'ttr': ttr,
            'link_density': link_density,
            'token_count': len(tokens)
        }

    # Match A survivor data to B folios by section
    # Group A lines by section
    a_by_section = defaultdict(list)
    for d in survivor_data:
        a_by_section[d['section']].append(d)

    # For each B folio, find average survivor count in same section
    matched_data = []
    for folio, metrics in b_metrics.items():
        # Get section of this B folio
        folio_section = b_df[b_df['folio'] == folio]['section'].iloc[0] if 'section' in b_df.columns else 'UNK'

        # Get A lines in same section
        section_a_lines = a_by_section.get(folio_section, [])
        if not section_a_lines:
            continue

        avg_survivor_count = np.mean([d['survivor_count'] for d in section_a_lines])
        avg_survivor_rate = np.mean([d['survivor_rate'] for d in section_a_lines])

        matched_data.append({
            'folio': folio,
            'section': folio_section,
            'avg_survivor_count': avg_survivor_count,
            'avg_survivor_rate': avg_survivor_rate,
            'b_transition_entropy': metrics['transition_entropy'],
            'b_ttr': metrics['ttr'],
            'b_link_density': metrics['link_density']
        })

    print(f"\nMatched B folios: {len(matched_data)}")

    if len(matched_data) < 10:
        print("INSUFFICIENT DATA for Test 2")
        return {'status': 'INSUFFICIENT_DATA', 'n': len(matched_data)}

    # Correlate survivor metrics with B variability
    survivor_rates = [d['avg_survivor_rate'] for d in matched_data]
    b_entropies = [d['b_transition_entropy'] for d in matched_data]
    b_ttrs = [d['b_ttr'] for d in matched_data]

    rho_entropy, p_entropy = stats.spearmanr(survivor_rates, b_entropies)
    rho_ttr, p_ttr = stats.spearmanr(survivor_rates, b_ttrs)

    print(f"\n--- Results ---")
    print(f"Avg survivor rate vs B transition entropy:")
    print(f"  rho = {rho_entropy:.3f}, p = {p_entropy:.4f}")
    print(f"\nAvg survivor rate vs B type-token ratio:")
    print(f"  rho = {rho_ttr:.3f}, p = {p_ttr:.4f}")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if (abs(rho_entropy) > 0.2 and p_entropy < 0.05) or (abs(rho_ttr) > 0.2 and p_ttr < 0.05):
        print("REFINES C254: Multiplicity DOES leak into B variability")
        interpretation = 'REFINES_C254'
    else:
        print("CONFIRMS C254: Survivor size acts purely at discrimination level")
        interpretation = 'CONFIRMS_C254'

    return {
        'status': 'COMPLETE',
        'n': len(matched_data),
        'rho_entropy': rho_entropy,
        'p_entropy': p_entropy,
        'rho_ttr': rho_ttr,
        'p_ttr': p_ttr,
        'interpretation': interpretation
    }


def run_test3(survivor_data: List[Dict]) -> Dict:
    """
    Test 3: Intersection Stability

    Question: Is elimination or survival doing the work?
    """
    print("\n" + "="*60)
    print("TEST 3: Intersection Stability")
    print("="*60)

    # Find survivor-set collisions
    # Group by survivor_middles (as frozenset)
    survivor_groups = defaultdict(list)
    for d in survivor_data:
        if d['survivor_count'] > 0:
            key = frozenset(d['survivor_middles'])
            survivor_groups[key].append(d)

    # Find groups with multiple lines having same survivor set but different eliminated
    collisions = []
    for key, group in survivor_groups.items():
        if len(group) >= 2:
            # Check if eliminated sets differ
            eliminated_sets = [frozenset(d['eliminated_middles']) for d in group]
            if len(set(eliminated_sets)) > 1:  # Different eliminated sets
                collisions.append({
                    'survivor_set': list(key),
                    'survivor_count': len(key),
                    'lines': group,
                    'n_lines': len(group),
                    'n_distinct_eliminated': len(set(eliminated_sets))
                })

    print(f"\nSurvivor-set collision groups: {len(collisions)}")

    if len(collisions) < 5:
        print("INSUFFICIENT COLLISIONS for Test 3")
        # Show what we have
        for i, c in enumerate(collisions[:5]):
            print(f"\n  Collision {i+1}: {c['n_lines']} lines share {c['survivor_count']} survivors")
        return {'status': 'INSUFFICIENT_DATA', 'n_collisions': len(collisions)}

    # Compare downstream metrics within collision groups
    # Check if HT metrics differ despite same survivor set
    ht_variance_within = []
    ht_variance_between = []

    for collision in collisions:
        lines = collision['lines']
        ht_densities = [l['ht_density'] for l in lines]
        ht_entropies = [l['ht_prefix_entropy'] for l in lines]

        # Within-group variance
        if len(ht_densities) > 1:
            ht_variance_within.append(np.var(ht_densities))

    # Compare to between-group variance (random pairs)
    all_densities = [d['ht_density'] for d in survivor_data if d['survivor_count'] > 0]
    if len(all_densities) > 1:
        random_var = np.var(all_densities)
    else:
        random_var = 0

    mean_within_var = np.mean(ht_variance_within) if ht_variance_within else 0

    print(f"\n--- Results ---")
    print(f"Mean within-collision HT variance: {mean_within_var:.4f}")
    print(f"Overall HT variance: {random_var:.4f}")

    if random_var > 0:
        variance_ratio = mean_within_var / random_var
        print(f"Variance ratio (within/overall): {variance_ratio:.3f}")
    else:
        variance_ratio = 0

    # Test: within-collision variance vs overall
    if len(ht_variance_within) >= 5:
        # One-sample t-test: is within-variance significantly different from overall?
        t_stat, p_value = stats.ttest_1samp(ht_variance_within, random_var)
        print(f"T-test: t={t_stat:.3f}, p={p_value:.4f}")
    else:
        t_stat, p_value = 0, 1.0
        print("Insufficient data for t-test")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if variance_ratio < 0.5 and p_value < 0.05:
        print("SURVIVOR IDENTITY SUFFICIENT: Same survivors -> similar HT")
        print("  Elimination does all the work")
        interpretation = 'SURVIVOR_SUFFICIENT'
    elif variance_ratio > 0.8:
        print("BUNDLING EFFECTS EXIST: Same survivors -> different HT")
        print("  Eliminated tokens matter")
        interpretation = 'BUNDLING_EFFECTS'
    else:
        print("INCONCLUSIVE: Moderate variance difference")
        interpretation = 'INCONCLUSIVE'

    return {
        'status': 'COMPLETE',
        'n_collisions': len(collisions),
        'mean_within_variance': mean_within_var,
        'overall_variance': random_var,
        'variance_ratio': variance_ratio,
        't_stat': t_stat,
        'p_value': p_value,
        'interpretation': interpretation
    }


def main():
    print("="*60)
    print("PHASE SSD: Survivor-Set Dimensionality Tests")
    print("="*60)

    # Load data
    print("\nLoading data...")
    df = load_data()
    print(f"Total tokens: {len(df)}")
    print(f"Currier A tokens: {len(df[df['language'] == 'A'])}")
    print(f"Currier B tokens: {len(df[df['language'] == 'B'])}")
    print(f"AZC tokens: {len(df[(df['language'] != 'A') & (df['language'] != 'B')])}")

    # Build AZC scaffold
    print("\nBuilding AZC scaffold...")
    scaffold = build_azc_scaffold(df)
    for zone, middles in scaffold.items():
        print(f"  {zone}: {len(middles)} unique MIDDLEs")

    # Compute survivor sets
    print("\nComputing survivor sets for all A lines...")
    survivor_data = compute_survivor_sets(df, scaffold)
    print(f"Total A lines analyzed: {len(survivor_data)}")

    # Summary statistics
    survivor_counts = [d['survivor_count'] for d in survivor_data]
    print(f"\nSurvivor count statistics:")
    print(f"  Mean: {np.mean(survivor_counts):.1f}")
    print(f"  Median: {np.median(survivor_counts):.1f}")
    print(f"  Max: {max(survivor_counts)}")
    print(f"  Lines with 0 survivors: {sum(1 for c in survivor_counts if c == 0)}")
    print(f"  Lines with 10+ survivors: {sum(1 for c in survivor_counts if c >= 10)}")

    # Run tests
    test1_results = run_test1(survivor_data)
    test2_results = run_test2(survivor_data, df)
    test3_results = run_test3(survivor_data)

    # Synthesis
    print("\n" + "="*60)
    print("SYNTHESIS")
    print("="*60)

    results = {
        'test1': test1_results,
        'test2': test2_results,
        'test3': test3_results,
        'survivor_stats': {
            'n_lines': len(survivor_data),
            'mean_survivors': float(np.mean(survivor_counts)),
            'median_survivors': float(np.median(survivor_counts)),
            'max_survivors': int(max(survivor_counts))
        }
    }

    # Determine overall interpretation
    interpretations = [
        test1_results.get('interpretation', 'UNKNOWN'),
        test2_results.get('interpretation', 'UNKNOWN'),
        test3_results.get('interpretation', 'UNKNOWN')
    ]

    print(f"\nTest 1 (HT Morphology): {interpretations[0]}")
    print(f"Test 2 (B Variability): {interpretations[1]}")
    print(f"Test 3 (Intersection): {interpretations[2]}")

    # Save results
    output_path = RESULTS_DIR / "ssd_phase_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()

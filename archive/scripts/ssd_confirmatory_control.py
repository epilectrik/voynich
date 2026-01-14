"""
SSD Confirmatory Control for P-C480

Tests whether survivor-set vs B-variability correlation survives:
1. Within-regime control (single regime class)
2. Tail-pressure control (partial correlation)
3. Section stratification (H/P/T separately)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import math

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from scipy import stats
import numpy as np

DATA_PATH = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"
RESULTS_DIR = PROJECT_ROOT / "results"

# Load previous results for survivor data
SSD_RESULTS = RESULTS_DIR / "ssd_phase_results.json"


def extract_middle(token: str) -> str:
    """Extract MIDDLE component from token."""
    if not token or len(token) < 2:
        return token

    prefixes = ['ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'ct', 'al', 'ar', 'or',
                'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta']
    suffixes = ['y', 'dy', 'ey', 'ly', 'ry', 'ty', 'sy',
                'in', 'ain', 'aiin', 'iin', 'oiin',
                'ol', 'al', 'ar', 'or', 'ir', 'an', 'on', 'am', 'om']

    text = token.lower()

    for prefix in sorted(prefixes, key=len, reverse=True):
        if text.startswith(prefix):
            text = text[len(prefix):]
            break

    for suffix in sorted(suffixes, key=len, reverse=True):
        if text.endswith(suffix) and len(text) > len(suffix):
            text = text[:-len(suffix)]
            break

    return text if text else token


def get_prefix(token: str) -> str:
    """Extract prefix from token."""
    if not token:
        return ''
    token = token.lower()
    prefixes = ['ch', 'sh', 'qo', 'da', 'ol', 'ok', 'ot', 'ct', 'al', 'ar', 'or']
    for prefix in sorted(prefixes, key=len, reverse=True):
        if token.startswith(prefix):
            return prefix
    return ''


def compute_entropy(items: list) -> float:
    """Compute Shannon entropy."""
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


def load_data():
    """Load transcription data."""
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
    df = df[df['word'].notna() & (df['word'] != '')]
    df = df[~df['word'].str.contains(r'\*', na=False)]
    return df


def compute_b_metrics(df: pd.DataFrame) -> dict:
    """Compute B metrics per folio including regime indicators."""
    b_df = df[df['language'] == 'B'].copy()

    b_metrics = {}
    for folio, folio_df in b_df.groupby('folio'):
        tokens = folio_df['word'].tolist()
        if len(tokens) < 10:
            continue

        # Prefixes and transitions
        prefixes = [get_prefix(t) for t in tokens if get_prefix(t)]
        transitions = [(prefixes[i], prefixes[i+1]) for i in range(len(prefixes)-1)]
        transition_entropy = compute_entropy([f"{a}->{b}" for a, b in transitions])

        # LINK density (ol/al prefixes) - proxy for waiting regime
        link_count = sum(1 for t in tokens if get_prefix(t) in {'ol', 'al'})
        link_density = link_count / len(tokens)

        # Tail pressure: fraction of rare MIDDLEs (appear <5 times globally)
        middles = [extract_middle(t) for t in tokens]

        # Type-token ratio
        ttr = len(set(tokens)) / len(tokens)

        section = folio_df['section'].iloc[0] if 'section' in folio_df.columns else 'UNK'

        b_metrics[folio] = {
            'transition_entropy': transition_entropy,
            'ttr': ttr,
            'link_density': link_density,
            'token_count': len(tokens),
            'section': section,
            'middles': middles
        }

    return b_metrics


def compute_middle_rarity(df: pd.DataFrame) -> dict:
    """Compute global MIDDLE frequency for rarity scoring."""
    all_middles = []
    for _, row in df.iterrows():
        if pd.notna(row['word']):
            all_middles.append(extract_middle(row['word']))

    middle_counts = defaultdict(int)
    for m in all_middles:
        middle_counts[m] += 1

    return middle_counts


POSITION_ZONES = {
    'C': {'min': 0.00, 'max': 0.39},
    'P': {'min': 0.39, 'max': 0.55},
    'R': {'min': 0.55, 'max': 0.73},
    'S': {'min': 0.73, 'max': 1.00},
}


def build_azc_scaffold(df: pd.DataFrame) -> dict:
    """Build AZC scaffold: MIDDLEs available per zone."""
    azc_df = df[(df['language'] != 'A') & (df['language'] != 'B')]

    scaffold = {'C': set(), 'P': set(), 'R': set(), 'S': set()}

    for _, row in azc_df.iterrows():
        placement = str(row.get('placement', '')).upper()
        token = row['word']
        middle = extract_middle(token)

        if placement.startswith('C'):
            scaffold['C'].add(middle)
        elif placement.startswith('P'):
            scaffold['P'].add(middle)
        elif placement.startswith('R'):
            scaffold['R'].add(middle)
        elif placement.startswith('S'):
            scaffold['S'].add(middle)

    return scaffold


def compute_a_survivor_metrics(df: pd.DataFrame, middle_counts: dict) -> dict:
    """Compute A line metrics including tail pressure."""
    scaffold = build_azc_scaffold(df)
    a_df = df[df['language'] == 'A'].copy()

    results_by_section = defaultdict(list)

    for (folio, line_num), line_df in a_df.groupby(['folio', 'line_number']):
        tokens = line_df['word'].tolist()
        line_len = len(tokens)
        if line_len == 0:
            continue

        survivor_count = 0
        tail_tokens = 0  # MIDDLEs appearing <10 times globally

        for i, token in enumerate(tokens):
            norm_pos = i / max(1, line_len - 1) if line_len > 1 else 0.5

            # Position zone
            zone = 'S'
            for z, bounds in POSITION_ZONES.items():
                if bounds['min'] <= norm_pos < bounds['max']:
                    zone = z
                    break

            middle = extract_middle(token)
            zone_middles = scaffold.get(zone, set())

            # Check match
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
                survivor_count += 1

            # Tail pressure
            if middle_counts.get(middle, 0) < 10:
                tail_tokens += 1

        section = line_df['section'].iloc[0] if 'section' in line_df.columns else 'UNK'

        results_by_section[section].append({
            'folio': folio,
            'line_num': line_num,
            'line_length': line_len,
            'survivor_count': survivor_count,
            'survivor_rate': survivor_count / line_len if line_len > 0 else 0,
            'tail_pressure': tail_tokens / line_len if line_len > 0 else 0,
            'section': section
        })

    return results_by_section


def run_confirmatory_controls():
    """Run all confirmatory controls."""
    print("="*60)
    print("SSD CONFIRMATORY CONTROLS FOR P-C480")
    print("="*60)

    # Load data
    print("\nLoading data...")
    df = load_data()

    # Compute global MIDDLE rarity
    print("Computing MIDDLE rarity...")
    middle_counts = compute_middle_rarity(df)

    # Compute B metrics
    print("Computing B metrics...")
    b_metrics = compute_b_metrics(df)

    # Compute A survivor metrics by section
    print("Computing A survivor metrics...")
    a_by_section = compute_a_survivor_metrics(df, middle_counts)

    results = {}

    # ===================
    # Control 1: Within-regime (high LINK density = EXTREME waiting)
    # ===================
    print("\n" + "-"*60)
    print("CONTROL 1: Within-Regime (EXTREME waiting programs)")
    print("-"*60)

    # Split B folios by LINK density quartiles
    link_densities = [m['link_density'] for m in b_metrics.values()]
    q75 = np.percentile(link_densities, 75)

    extreme_folios = {f: m for f, m in b_metrics.items() if m['link_density'] >= q75}
    print(f"EXTREME waiting folios (top 25% LINK): {len(extreme_folios)}")

    # Match to A survivor rates
    matched_extreme = []
    for folio, metrics in extreme_folios.items():
        section = metrics['section']
        section_a = []
        for s, lines in a_by_section.items():
            if s == section:
                section_a.extend(lines)

        if section_a:
            avg_survivor_rate = np.mean([l['survivor_rate'] for l in section_a])
            matched_extreme.append({
                'folio': folio,
                'survivor_rate': avg_survivor_rate,
                'transition_entropy': metrics['transition_entropy']
            })

    if len(matched_extreme) >= 5:
        rates = [m['survivor_rate'] for m in matched_extreme]
        entropies = [m['transition_entropy'] for m in matched_extreme]
        rho, p = stats.spearmanr(rates, entropies)
        print(f"n = {len(matched_extreme)}")
        print(f"rho = {rho:.3f}, p = {p:.4f}")

        if p < 0.1:
            print("SURVIVES within-regime control")
            control1_status = 'PASS'
        else:
            print("FAILS within-regime control (may be power issue)")
            control1_status = 'FAIL_POWER'
    else:
        print("Insufficient data for within-regime control")
        rho, p = None, None
        control1_status = 'INSUFFICIENT'

    results['control1_within_regime'] = {
        'n': len(matched_extreme),
        'rho': rho,
        'p': p,
        'status': control1_status
    }

    # ===================
    # Control 2: Tail-pressure control
    # ===================
    print("\n" + "-"*60)
    print("CONTROL 2: Tail-Pressure Control (partial correlation)")
    print("-"*60)

    # Collect all matched data with tail pressure
    all_matched = []
    for folio, metrics in b_metrics.items():
        section = metrics['section']
        section_a = []
        for s, lines in a_by_section.items():
            if s == section:
                section_a.extend(lines)

        if section_a:
            avg_survivor_rate = np.mean([l['survivor_rate'] for l in section_a])
            avg_tail_pressure = np.mean([l['tail_pressure'] for l in section_a])
            all_matched.append({
                'folio': folio,
                'survivor_rate': avg_survivor_rate,
                'tail_pressure': avg_tail_pressure,
                'transition_entropy': metrics['transition_entropy']
            })

    if len(all_matched) >= 10:
        rates = np.array([m['survivor_rate'] for m in all_matched])
        tails = np.array([m['tail_pressure'] for m in all_matched])
        entropies = np.array([m['transition_entropy'] for m in all_matched])

        print(f"n = {len(all_matched)}")
        print(f"Rate range: {rates.min():.3f} - {rates.max():.3f}")
        print(f"Tail range: {tails.min():.3f} - {tails.max():.3f}")

        rho_raw, p_raw = stats.spearmanr(rates, entropies)
        print(f"Raw correlation: rho = {rho_raw:.3f}, p = {p_raw:.4f}")

        # Partial correlation: residualize both on tail pressure
        if np.std(tails) > 0.001 and np.std(rates) > 0.001:
            rate_resid = rates - np.polyval(np.polyfit(tails, rates, 1), tails)
            entropy_resid = entropies - np.polyval(np.polyfit(tails, entropies, 1), tails)
            if np.std(rate_resid) > 0.001 and np.std(entropy_resid) > 0.001:
                rho_partial, p_partial = stats.spearmanr(rate_resid, entropy_resid)
            else:
                rho_partial, p_partial = rho_raw, p_raw
                print("  (residuals near-constant, using raw)")
        else:
            rho_partial, p_partial = rho_raw, p_raw
            print("  (inputs near-constant, using raw)")

        print(f"Partial (tail-controlled): rho = {rho_partial:.3f}, p = {p_partial:.4f}")

        if rho_partial > 0.2 and p_partial < 0.1:
            print("SURVIVES tail-pressure control")
            control2_status = 'PASS'
        elif rho_partial > 0.15:
            print("WEAKENED but present after tail control")
            control2_status = 'WEAKENED'
        else:
            print("FAILS tail-pressure control")
            control2_status = 'FAIL'
    else:
        print("Insufficient data")
        rho_partial, p_partial = None, None
        control2_status = 'INSUFFICIENT'

    results['control2_tail_pressure'] = {
        'n': len(all_matched),
        'rho_partial': rho_partial,
        'p_partial': p_partial,
        'status': control2_status
    }

    # ===================
    # Control 3: Section stratification
    # ===================
    print("\n" + "-"*60)
    print("CONTROL 3: Section Stratification")
    print("-"*60)

    section_results = {}
    for section in ['H', 'P', 'T']:
        section_b = {f: m for f, m in b_metrics.items() if m['section'] == section}
        section_a_lines = a_by_section.get(section, [])

        if len(section_b) < 5 or len(section_a_lines) < 5:
            print(f"Section {section}: Insufficient data")
            section_results[section] = {'status': 'INSUFFICIENT'}
            continue

        # Overall section survivor rate
        avg_rate = np.mean([l['survivor_rate'] for l in section_a_lines])

        # B entropy for this section
        b_entropies = [m['transition_entropy'] for m in section_b.values()]
        avg_entropy = np.mean(b_entropies)

        print(f"Section {section}: n_B={len(section_b)}, n_A_lines={len(section_a_lines)}")
        print(f"  Avg survivor rate: {avg_rate:.3f}")
        print(f"  Avg B entropy: {avg_entropy:.3f}")

        section_results[section] = {
            'n_b': len(section_b),
            'n_a': len(section_a_lines),
            'avg_survivor_rate': avg_rate,
            'avg_b_entropy': avg_entropy
        }

    # Check if pattern holds across sections
    valid_sections = [s for s, r in section_results.items() if 'avg_survivor_rate' in r]
    if len(valid_sections) >= 2:
        rates = [section_results[s]['avg_survivor_rate'] for s in valid_sections]
        entropies = [section_results[s]['avg_b_entropy'] for s in valid_sections]

        # With only 2-3 points, just check direction
        if len(valid_sections) == 3:
            rho, p = stats.spearmanr(rates, entropies)
            print(f"\nCross-section correlation: rho = {rho:.3f}")
            control3_status = 'DIRECTIONAL_CHECK'
        else:
            rho, p = None, None
            control3_status = 'TOO_FEW_SECTIONS'
    else:
        rho, p = None, None
        control3_status = 'INSUFFICIENT'

    results['control3_section'] = {
        'section_results': section_results,
        'rho': rho,
        'status': control3_status
    }

    # ===================
    # SYNTHESIS
    # ===================
    print("\n" + "="*60)
    print("SYNTHESIS")
    print("="*60)

    print(f"\nControl 1 (within-regime): {results['control1_within_regime']['status']}")
    print(f"Control 2 (tail-pressure): {results['control2_tail_pressure']['status']}")
    print(f"Control 3 (section): {results['control3_section']['status']}")

    # Overall verdict
    passes = sum(1 for r in [
        results['control1_within_regime']['status'],
        results['control2_tail_pressure']['status']
    ] if r in ['PASS', 'WEAKENED'])

    if passes >= 1:
        print("\n=> P-C480 SURVIVES at least one confirmatory control")
        print("=> Recommended: Promote to Tier 2 with scoped language")
        overall = 'PROMOTION_JUSTIFIED'
    else:
        print("\n=> P-C480 does not survive controls")
        print("=> Recommended: Keep at Tier 3 or investigate further")
        overall = 'KEEP_TIER_3'

    results['overall'] = overall

    # Save
    output_path = RESULTS_DIR / "ssd_confirmatory_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_confirmatory_controls()

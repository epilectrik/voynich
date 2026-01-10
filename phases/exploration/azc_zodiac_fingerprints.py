#!/usr/bin/env python3
"""
D2: AZC Zodiac Individual Fingerprints

Despite template reuse, where do Zodiac folios subtly diverge?
Those divergences are almost certainly intentional.

Questions:
1. Which Zodiac folios are "monitoring-heavy" vs "transition-heavy"?
2. Is there a gradient across the 12 Zodiac folios (manuscript order)?
3. Are some optimized for watching, others for checking?

Output: results/azc_zodiac_fingerprints.json
"""

import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
DATA = BASE / "data" / "transcriptions"

# Input
AZC_FEATURES = RESULTS / "azc_folio_features.json"
AZC_CLUSTERS = RESULTS / "azc_folio_clusters.json"
HT_FEATURES = RESULTS / "ht_folio_features.json"
TRANSCRIPTION = DATA / "interlinear_full_words.txt"

# Output
OUTPUT = RESULTS / "azc_zodiac_fingerprints.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_transcription():
    """Load full transcription."""
    rows = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            rows.append(row)
    return rows


def get_zodiac_folios(azc_features):
    """Get list of Zodiac (section='Z') folios."""
    zodiac = []
    for folio, features in azc_features['folios'].items():
        if features.get('section') == 'Z':
            zodiac.append(folio)
    return sorted(zodiac)


def extract_placement_sequences(rows, zodiac_folios):
    """
    Extract placement sequences for each Zodiac folio.
    Returns dict: folio -> list of placements in order
    """
    sequences = defaultdict(list)

    for row in rows:
        folio = row.get('folio', '').strip('"')
        if folio not in zodiac_folios:
            continue

        language = row.get('language', '').strip('"')
        placement = row.get('placement', '').strip('"')

        # Only AZC tokens (language == 'NA')
        if language != 'NA':
            continue

        if placement:
            sequences[folio].append(placement)

    return sequences


def compute_fingerprint_metrics(sequences, azc_features, ht_features, zodiac_folios):
    """
    Compute fingerprint metrics for each Zodiac folio.
    """
    fingerprints = {}

    for folio in zodiac_folios:
        placements = sequences.get(folio, [])

        if not placements:
            continue

        # Count R and S placements
        r_count = sum(1 for p in placements if p.startswith('R'))
        s_count = sum(1 for p in placements if p.startswith('S'))
        total = r_count + s_count

        # Metric 1: S/(S+R) ratio - boundary vs interior
        sr_ratio = s_count / total if total > 0 else 0

        # Metric 2: Spiral tightness - R<->S alternations
        alternations = 0
        for i in range(1, len(placements)):
            prev_family = 'R' if placements[i-1].startswith('R') else 'S' if placements[i-1].startswith('S') else None
            curr_family = 'R' if placements[i].startswith('R') else 'S' if placements[i].startswith('S') else None
            if prev_family and curr_family and prev_family != curr_family:
                alternations += 1

        spiral_tightness = alternations / len(placements) if placements else 0

        # Metric 3: Boundary density - S / total placements
        boundary_density = s_count / len(placements) if placements else 0

        # Metric 4: Placement entropy (from existing features)
        placement_entropy = azc_features['folios'].get(folio, {}).get('placement_entropy', 0)

        # Metric 5: HT-weighted boundary
        ht_density = ht_features['folios'].get(folio, {}).get('ht_density', 0)
        ht_weighted_boundary = sr_ratio * ht_density

        # Additional metrics
        placement_counts = Counter(placements)

        fingerprints[folio] = {
            'folio': folio,
            'total_placements': len(placements),
            'r_count': r_count,
            's_count': s_count,
            'metrics': {
                'sr_ratio': round(sr_ratio, 4),
                'spiral_tightness': round(spiral_tightness, 4),
                'boundary_density': round(boundary_density, 4),
                'placement_entropy': round(placement_entropy, 4),
                'ht_density': round(ht_density, 4),
                'ht_weighted_boundary': round(ht_weighted_boundary, 4)
            },
            'placement_distribution': dict(placement_counts)
        }

    return fingerprints


def analyze_variation(fingerprints, zodiac_folios):
    """
    Analyze variation across Zodiac folios.
    """
    metrics = ['sr_ratio', 'spiral_tightness', 'boundary_density', 'placement_entropy', 'ht_density', 'ht_weighted_boundary']

    variation = {}
    for metric in metrics:
        values = [fingerprints[f]['metrics'][metric] for f in zodiac_folios if f in fingerprints]
        if len(values) >= 2:
            cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
            variation[metric] = {
                'mean': round(np.mean(values), 4),
                'std': round(np.std(values), 4),
                'cv': round(cv, 4),
                'min': round(min(values), 4),
                'max': round(max(values), 4),
                'range': round(max(values) - min(values), 4)
            }

    return variation


def find_extremes(fingerprints, zodiac_folios):
    """
    Identify extreme folios for each metric.
    """
    metrics = ['sr_ratio', 'spiral_tightness', 'boundary_density', 'placement_entropy', 'ht_density']

    extremes = {}
    for metric in metrics:
        sorted_folios = sorted(
            [f for f in zodiac_folios if f in fingerprints],
            key=lambda f: fingerprints[f]['metrics'][metric],
            reverse=True
        )
        if sorted_folios:
            extremes[metric] = {
                'highest': sorted_folios[0],
                'highest_value': fingerprints[sorted_folios[0]]['metrics'][metric],
                'lowest': sorted_folios[-1],
                'lowest_value': fingerprints[sorted_folios[-1]]['metrics'][metric]
            }

    return extremes


def check_ordering_effects(fingerprints, zodiac_folios):
    """
    Check if metrics correlate with folio position (manuscript order).
    """
    # Sort folios by position
    sorted_folios = sorted([f for f in zodiac_folios if f in fingerprints])

    positions = list(range(len(sorted_folios)))
    metrics = ['sr_ratio', 'spiral_tightness', 'boundary_density', 'placement_entropy', 'ht_density']

    correlations = {}
    for metric in metrics:
        values = [fingerprints[f]['metrics'][metric] for f in sorted_folios]
        if len(values) >= 3:
            r, p = stats.spearmanr(positions, values)
            correlations[metric] = {
                'spearman_r': round(float(r), 3),
                'p_value': round(float(p), 4),
                'significant': bool(p < 0.05)
            }

    return correlations


def identify_folio_character(fingerprints):
    """
    Classify each folio's character based on metrics.
    """
    characters = {}

    for folio, fp in fingerprints.items():
        m = fp['metrics']

        # Classify based on sr_ratio
        if m['sr_ratio'] > 0.45:
            spatial_focus = "transition-heavy"
        elif m['sr_ratio'] < 0.35:
            spatial_focus = "monitoring-heavy"
        else:
            spatial_focus = "balanced"

        # Classify based on spiral_tightness
        if m['spiral_tightness'] > 0.15:
            attention_pattern = "frequent-shifts"
        else:
            attention_pattern = "sustained-focus"

        # Classify based on HT
        if m['ht_density'] > 0.20:
            human_load = "high-HT"
        elif m['ht_density'] < 0.10:
            human_load = "low-HT"
        else:
            human_load = "moderate-HT"

        characters[folio] = {
            'spatial_focus': spatial_focus,
            'attention_pattern': attention_pattern,
            'human_load': human_load,
            'summary': f"{spatial_focus}, {attention_pattern}, {human_load}"
        }

    return characters


def main():
    print("=" * 70)
    print("D2: AZC Zodiac Individual Fingerprints")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    azc_features = load_json(AZC_FEATURES)
    azc_clusters = load_json(AZC_CLUSTERS)
    ht_features = load_json(HT_FEATURES)
    rows = load_transcription()

    zodiac_folios = get_zodiac_folios(azc_features)
    print(f"    Zodiac folios: {len(zodiac_folios)}")
    print(f"    Folios: {', '.join(zodiac_folios)}")

    # Extract sequences
    print("\n[2] Extracting placement sequences...")
    sequences = extract_placement_sequences(rows, zodiac_folios)
    print(f"    Folios with sequences: {len(sequences)}")

    # Compute fingerprints
    print("\n[3] Computing fingerprint metrics...")
    fingerprints = compute_fingerprint_metrics(sequences, azc_features, ht_features, zodiac_folios)

    # Display per-folio metrics
    print("\n    Per-folio metrics:")
    print(f"    {'Folio':<8} {'S/R':>6} {'Spiral':>8} {'Bound':>7} {'Entropy':>8} {'HT':>6}")
    print("    " + "-" * 50)
    for folio in sorted(fingerprints.keys()):
        fp = fingerprints[folio]
        m = fp['metrics']
        print(f"    {folio:<8} {m['sr_ratio']:>6.3f} {m['spiral_tightness']:>8.3f} {m['boundary_density']:>7.3f} {m['placement_entropy']:>8.3f} {m['ht_density']:>6.3f}")

    # Analyze variation
    print("\n[4] Analyzing variation across folios...")
    variation = analyze_variation(fingerprints, zodiac_folios)

    print("\n    Metric variation (CV = coefficient of variation):")
    for metric, v in sorted(variation.items(), key=lambda x: x[1]['cv'], reverse=True):
        print(f"    {metric:<20} CV={v['cv']:.3f} range=[{v['min']:.3f}, {v['max']:.3f}]")

    # Find extremes
    print("\n[5] Finding extreme folios...")
    extremes = find_extremes(fingerprints, zodiac_folios)

    for metric, e in extremes.items():
        print(f"    {metric}: highest={e['highest']} ({e['highest_value']:.3f}), lowest={e['lowest']} ({e['lowest_value']:.3f})")

    # Check ordering effects
    print("\n[6] Checking manuscript ordering effects...")
    ordering = check_ordering_effects(fingerprints, zodiac_folios)

    for metric, corr in ordering.items():
        sig = "***" if corr['p_value'] < 0.001 else "**" if corr['p_value'] < 0.01 else "*" if corr['p_value'] < 0.05 else ""
        print(f"    {metric}: r={corr['spearman_r']:.3f}, p={corr['p_value']:.4f} {sig}")

    # Classify folio characters
    print("\n[7] Classifying folio characters...")
    characters = identify_folio_character(fingerprints)

    for folio in sorted(characters.keys()):
        c = characters[folio]
        print(f"    {folio}: {c['summary']}")

    # Key findings
    print("\n[8] Key findings...")
    findings = []

    # Check if variation is systematic or random
    high_cv_metrics = [m for m, v in variation.items() if v['cv'] > 0.2]
    if high_cv_metrics:
        findings.append({
            'finding': 'Non-uniform variation across Zodiac',
            'high_cv_metrics': high_cv_metrics,
            'interpretation': 'Some metrics vary substantially despite template reuse'
        })

    # Check for ordering effects
    sig_ordering = [m for m, c in ordering.items() if c['significant']]
    if sig_ordering:
        findings.append({
            'finding': 'Position gradient detected',
            'metrics': sig_ordering,
            'interpretation': 'Some metrics correlate with manuscript position'
        })
    else:
        findings.append({
            'finding': 'No position gradient',
            'interpretation': 'Variation is not ordered by manuscript position'
        })

    # Check for distinct folio types
    transition_heavy = [f for f, c in characters.items() if c['spatial_focus'] == 'transition-heavy']
    monitoring_heavy = [f for f, c in characters.items() if c['spatial_focus'] == 'monitoring-heavy']

    if len(transition_heavy) >= 2 and len(monitoring_heavy) >= 2:
        findings.append({
            'finding': 'Distinct folio types exist',
            'transition_heavy': transition_heavy,
            'monitoring_heavy': monitoring_heavy,
            'interpretation': 'Zodiac folios specialize - some for transitions, some for monitoring'
        })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    # Save output
    print("\n[9] Saving output...")

    output = {
        'metadata': {
            'analysis': 'D2 - AZC Zodiac Individual Fingerprints',
            'description': 'Finding intentional variations within Zodiac template',
            'n_zodiac_folios': len(zodiac_folios),
            'folios_analyzed': len(fingerprints)
        },
        'fingerprints': fingerprints,
        'variation': variation,
        'extremes': extremes,
        'ordering_effects': ordering,
        'characters': characters,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("D2 COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()

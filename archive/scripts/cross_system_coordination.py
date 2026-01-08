"""
CROSS-SYSTEM COORDINATION PROBE

Theory: Different B program "families" might correspond to different processes,
drawing from different A sections or coordinated by AZC.

Questions:
1. Do B folios cluster by which A-sections they reference?
2. Do control regimes correlate with A-section preference?
3. Does AZC vocabulary correlate with specific B program types?
4. Are there distinct "process families" visible in cross-system patterns?

This probes whether the 5+ execution families map to different physical processes.
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, chi2_contingency

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_all_data():
    """Load A, B, and AZC data with section/folio info."""
    a_data = defaultdict(lambda: {'tokens': [], 'section': None})
    b_data = defaultdict(list)
    azc_data = defaultdict(list)

    # Track A vocabulary by section
    a_section_vocab = defaultdict(set)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            lang = row.get('language', '')
            section = row.get('section', '')

            if lang == 'A':
                a_data[folio]['tokens'].append(token)
                a_data[folio]['section'] = section
                a_section_vocab[section].add(token)
            elif lang == 'B':
                b_data[folio].append(token)
            else:
                # AZC (unclassified)
                azc_data[folio].append(token)

    return a_data, b_data, azc_data, a_section_vocab

def analyze_b_a_section_profiles():
    """For each B folio, compute A-section reference profile."""
    print("="*70)
    print("B PROGRAM x A SECTION REFERENCE ANALYSIS")
    print("="*70)

    a_data, b_data, azc_data, a_section_vocab = load_all_data()

    # Build global A vocabulary by section
    print(f"\nA-section vocabulary sizes:")
    for section in sorted(a_section_vocab.keys()):
        if section:
            print(f"  Section {section}: {len(a_section_vocab[section])} types")

    # For each B folio, compute section reference profile
    b_profiles = {}

    for b_folio, b_tokens in b_data.items():
        b_vocab = set(b_tokens)

        profile = {}
        for section in ['H', 'P', 'T']:
            if section in a_section_vocab:
                overlap = len(b_vocab & a_section_vocab[section])
                profile[section] = overlap

        total_overlap = sum(profile.values())
        if total_overlap > 0:
            profile_normalized = {s: v/total_overlap for s, v in profile.items()}
        else:
            profile_normalized = {s: 0 for s in profile}

        b_profiles[b_folio] = {
            'raw': profile,
            'normalized': profile_normalized,
            'total_overlap': total_overlap,
            'b_vocab_size': len(b_vocab)
        }

    print(f"\nB folios analyzed: {len(b_profiles)}")

    # Analyze distribution of profiles
    print("\n" + "-"*70)
    print("B FOLIO A-SECTION REFERENCE DISTRIBUTION")
    print("-"*70)

    h_fracs = [p['normalized'].get('H', 0) for p in b_profiles.values()]
    p_fracs = [p['normalized'].get('P', 0) for p in b_profiles.values()]
    t_fracs = [p['normalized'].get('T', 0) for p in b_profiles.values()]

    print(f"\nSection H reference fraction:")
    print(f"  Mean: {np.mean(h_fracs):.3f}, Std: {np.std(h_fracs):.3f}")
    print(f"  Min: {np.min(h_fracs):.3f}, Max: {np.max(h_fracs):.3f}")

    print(f"\nSection P reference fraction:")
    print(f"  Mean: {np.mean(p_fracs):.3f}, Std: {np.std(p_fracs):.3f}")
    print(f"  Min: {np.min(p_fracs):.3f}, Max: {np.max(p_fracs):.3f}")

    print(f"\nSection T reference fraction:")
    print(f"  Mean: {np.mean(t_fracs):.3f}, Std: {np.std(t_fracs):.3f}")

    # Are there distinct clusters?
    print("\n" + "-"*70)
    print("CLUSTERING ANALYSIS")
    print("-"*70)

    # Check if there's bimodality in H-fraction
    h_high = sum(1 for h in h_fracs if h > 0.8)
    h_medium = sum(1 for h in h_fracs if 0.5 <= h <= 0.8)
    h_low = sum(1 for h in h_fracs if h < 0.5)

    print(f"\nH-fraction distribution:")
    print(f"  High (>0.8): {h_high} folios")
    print(f"  Medium (0.5-0.8): {h_medium} folios")
    print(f"  Low (<0.5): {h_low} folios")

    # Show extreme folios
    print("\n" + "-"*70)
    print("EXTREME B FOLIOS (by A-section profile)")
    print("-"*70)

    sorted_by_h = sorted(b_profiles.items(), key=lambda x: x[1]['normalized'].get('H', 0))

    print("\nLowest H-fraction (most P-leaning):")
    for folio, prof in sorted_by_h[:10]:
        h = prof['normalized'].get('H', 0)
        p = prof['normalized'].get('P', 0)
        print(f"  {folio}: H={h:.3f}, P={p:.3f}")

    print("\nHighest H-fraction:")
    for folio, prof in sorted_by_h[-5:]:
        h = prof['normalized'].get('H', 0)
        p = prof['normalized'].get('P', 0)
        print(f"  {folio}: H={h:.3f}, P={p:.3f}")

    return b_profiles

def analyze_regime_section_correlation(b_profiles):
    """Check if control regimes correlate with A-section preference."""
    print("\n" + "="*70)
    print("CONTROL REGIME x A-SECTION CORRELATION")
    print("="*70)

    # We don't have regime data loaded, but we can proxy via LINK density
    # For now, just report that this would need regime data
    print("\nNote: Full regime analysis requires loading control_signatures.json")
    print("Proxy analysis using vocabulary characteristics...")

    # Compute vocabulary diversity as proxy
    h_fracs = [(f, p['normalized'].get('H', 0)) for f, p in b_profiles.items()]
    vocab_sizes = [(f, p['b_vocab_size']) for f, p in b_profiles.items()]

    # Correlation between H-fraction and vocab size
    h_vals = [x[1] for x in h_fracs]
    v_vals = [b_profiles[x[0]]['b_vocab_size'] for x in h_fracs]

    rho, p = spearmanr(h_vals, v_vals)
    print(f"\nH-fraction vs vocabulary size: rho={rho:.3f}, p={p:.4f}")

    if abs(rho) > 0.3:
        print("-> CORRELATION: Different section profiles have different complexity")
    else:
        print("-> NO CORRELATION: Section profile independent of complexity")

def analyze_azc_b_coordination():
    """Check if AZC vocabulary correlates with B program types."""
    print("\n" + "="*70)
    print("AZC x B COORDINATION ANALYSIS")
    print("="*70)

    a_data, b_data, azc_data, a_section_vocab = load_all_data()

    # Get AZC vocabulary
    azc_vocab = set()
    for tokens in azc_data.values():
        azc_vocab.update(tokens)

    print(f"\nAZC vocabulary: {len(azc_vocab)} types across {len(azc_data)} folios")

    # Check AZC vocabulary overlap with each A section
    print("\nAZC overlap with A sections:")
    for section in ['H', 'P', 'T']:
        if section in a_section_vocab:
            overlap = len(azc_vocab & a_section_vocab[section])
            pct = 100 * overlap / len(azc_vocab) if azc_vocab else 0
            print(f"  Section {section}: {overlap} tokens ({pct:.1f}%)")

    # Check AZC overlap with B vocabulary
    b_vocab = set()
    for tokens in b_data.values():
        b_vocab.update(tokens)

    azc_b_overlap = len(azc_vocab & b_vocab)
    print(f"\nAZC-B vocabulary overlap: {azc_b_overlap} tokens ({100*azc_b_overlap/len(azc_vocab):.1f}%)")

    # Check if AZC folios appear near specific B program types
    print("\n" + "-"*70)
    print("AZC FOLIO POSITIONING")
    print("-"*70)

    # Get folio ordering
    all_folios = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            folio = row['folio']
            if folio not in all_folios:
                all_folios.append(folio)

    # Find AZC folios and their neighbors
    azc_folios = set(azc_data.keys())
    b_folios = set(b_data.keys())

    print(f"\nAZC folios: {len(azc_folios)}")
    print(f"B folios: {len(b_folios)}")

    # Check adjacency
    azc_near_b = 0
    for i, folio in enumerate(all_folios):
        if folio in azc_folios:
            # Check neighbors
            neighbors = []
            if i > 0:
                neighbors.append(all_folios[i-1])
            if i < len(all_folios) - 1:
                neighbors.append(all_folios[i+1])

            b_neighbors = sum(1 for n in neighbors if n in b_folios)
            if b_neighbors > 0:
                azc_near_b += 1

    print(f"AZC folios adjacent to B: {azc_near_b}/{len(azc_folios)}")

def analyze_a_internal_categories():
    """Check if Currier A has internal category structure."""
    print("\n" + "="*70)
    print("CURRIER A INTERNAL CATEGORY ANALYSIS")
    print("="*70)

    a_data, b_data, azc_data, a_section_vocab = load_all_data()

    # Marker prefixes
    MARKERS = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # For each section, compute marker distribution
    section_marker_dist = defaultdict(Counter)

    for folio, data in a_data.items():
        section = data['section']
        if not section:
            continue

        for token in data['tokens']:
            for marker in MARKERS:
                if token.startswith(marker):
                    section_marker_dist[section][marker] += 1
                    break

    print("\nMarker distribution by A-section:")
    print(f"\n{'Marker':<8}", end="")
    for section in sorted(section_marker_dist.keys()):
        print(f"{section:>10}", end="")
    print()
    print("-" * 40)

    for marker in MARKERS:
        print(f"{marker:<8}", end="")
        for section in sorted(section_marker_dist.keys()):
            count = section_marker_dist[section].get(marker, 0)
            total = sum(section_marker_dist[section].values())
            pct = 100 * count / total if total > 0 else 0
            print(f"{pct:>9.1f}%", end="")
        print()

    # Chi-square test for marker x section independence
    sections = sorted(section_marker_dist.keys())
    if len(sections) >= 2:
        contingency = []
        for marker in MARKERS:
            row = [section_marker_dist[s].get(marker, 0) for s in sections]
            contingency.append(row)

        contingency = np.array(contingency)
        # Remove rows/cols with all zeros
        contingency = contingency[contingency.sum(axis=1) > 0]

        if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
            chi2, p, dof, expected = chi2_contingency(contingency)
            print(f"\nMarker x Section independence test:")
            print(f"  Chi2 = {chi2:.1f}, p = {p:.2e}")

            if p < 0.001:
                print("  -> STRONG ASSOCIATION: Markers are section-specific")
            else:
                print("  -> INDEPENDENT: Markers distribute uniformly")

def summarize():
    """Summarize findings."""
    print("\n" + "="*70)
    print("SUMMARY: CROSS-SYSTEM COORDINATION")
    print("="*70)

    print("""
Key questions addressed:

1. Do B programs cluster by A-section reference?
   -> Check H-fraction distribution for bimodality

2. Do control regimes correlate with A-section preference?
   -> Would need regime data; proxy shows weak/no correlation

3. Does AZC coordinate B program types?
   -> Check AZC positioning and vocabulary overlap

4. Are there distinct "process families"?
   -> Look for multimodal distributions or strong clustering

If B programs uniformly reference H-section, the theory of
"different processes for different sections" is weakened.

If there are distinct B clusters with different A-profiles,
the theory is supported.
""")

def main():
    b_profiles = analyze_b_a_section_profiles()
    analyze_regime_section_correlation(b_profiles)
    analyze_azc_b_coordination()
    analyze_a_internal_categories()
    summarize()

if __name__ == '__main__':
    main()

"""
Folio Gap Analysis - Testing for Post-Composition Folio Removal

Tests whether folios may have been removed after the manuscript was composed,
using purely structural evidence from the grammar, HT patterns, and state transitions.

Phase: FG (Folio Gap)
Tests: FG-1 through FG-4
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import random

# Paths
BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
CONTROL_SIG = BASE / "results" / "control_signatures.json"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

# HT prefixes (known from prior analysis) - core set
HT_PREFIXES = ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'do', 'ta',
               'ke', 'al', 'ko', 'se', 'to', 'yd', 'od', 'pk', 'dk', 'sk']

# Extended HT prefixes (compositional forms observed at line starts)
HT_EXTENDED = ['psh', 'tsh', 'ksh', 'ksch', 'pch', 'tch', 'dch', 'fch', 'rch', 'sch',
               'po', 'te', 'ps', 'ts', 'ks', 'ds', 'ckh', 'cth', 'cph', 'cks']

# B-grammar prefixes (not full token list, just prefix patterns)
B_GRAMMAR_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'ar', 'or', 'dy']

# All known morphological prefixes (combined)
ALL_KNOWN_PREFIXES = HT_PREFIXES + HT_EXTENDED + B_GRAMMAR_PREFIXES

def load_transcription():
    """Load and parse the transcription file."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)
    return data

def load_control_signatures():
    """Load folio control signatures."""
    with open(CONTROL_SIG, 'r') as f:
        return json.load(f)

def load_grammar():
    """Load canonical grammar."""
    with open(GRAMMAR, 'r') as f:
        return json.load(f)

def get_currier_b_folios(data):
    """Get list of Currier B folios in manuscript order."""
    b_folios = sorted(set(
        row['folio'] for row in data
        if row.get('language') == 'B'
    ), key=folio_sort_key)
    return b_folios

def folio_sort_key(folio):
    """Sort folios by manuscript order."""
    # Extract number and side (r/v)
    import re
    match = re.match(r'f(\d+)([rv]?)', folio)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        return (num, side)
    return (999, 0)

def get_folio_tokens(data, folio):
    """Get all tokens for a specific folio."""
    return [row['word'] for row in data if row['folio'] == folio]

def classify_ht_prefix(token):
    """Classify which HT prefix a token has, if any."""
    for prefix in HT_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return None

def test_fg1_state_continuity(signatures, b_folios):
    """
    FG-1: State Continuity Break Test

    Compare state vectors between consecutive folios.
    Look for extreme discontinuities that might indicate removal.
    """
    print("\n" + "="*60)
    print("TEST FG-1: State Continuity Break Test")
    print("="*60)

    # Build state vectors for each folio
    folio_vectors = {}
    for folio in b_folios:
        if folio not in signatures['signatures']:
            continue
        sig = signatures['signatures'][folio]

        # State vector: [terminal_state_code, link_density, kernel_dominance_code, hazard_density]
        terminal_code = {'STATE-C': 0, 'other': 1, 'initial': 2}.get(sig.get('terminal_state', 'other'), 1)
        kernel_code = {'e': 0, 'k': 1, 'h': 2}.get(sig.get('kernel_dominance', 'e'), 0)

        folio_vectors[folio] = np.array([
            terminal_code,
            sig.get('link_density', 0.3),
            kernel_code,
            sig.get('hazard_density', 0.5),
            sig.get('cycle_regularity', 3.0)
        ])

    # Compute distances between consecutive folios
    ordered_folios = [f for f in b_folios if f in folio_vectors]
    observed_distances = []

    for i in range(len(ordered_folios) - 1):
        f1, f2 = ordered_folios[i], ordered_folios[i+1]
        dist = np.linalg.norm(folio_vectors[f1] - folio_vectors[f2])
        observed_distances.append((f1, f2, dist))

    if not observed_distances:
        print("ERROR: No consecutive folio pairs found")
        return None

    # Sort by distance to find outliers
    observed_distances.sort(key=lambda x: x[2], reverse=True)

    # Generate null distribution (random order)
    all_distances = []
    for _ in range(1000):
        shuffled = list(folio_vectors.keys())
        random.shuffle(shuffled)
        for i in range(len(shuffled) - 1):
            d = np.linalg.norm(folio_vectors[shuffled[i]] - folio_vectors[shuffled[i+1]])
            all_distances.append(d)

    null_mean = np.mean(all_distances)
    null_std = np.std(all_distances)

    # Observed mean
    obs_mean = np.mean([d[2] for d in observed_distances])

    # Count extreme outliers (>3 sigma)
    extreme_count = sum(1 for _, _, d in observed_distances if d > null_mean + 3*null_std)

    print(f"\nFolios analyzed: {len(ordered_folios)}")
    print(f"Consecutive pairs: {len(observed_distances)}")
    print(f"\nNull distribution: mean={null_mean:.3f}, std={null_std:.3f}")
    print(f"Observed mean distance: {obs_mean:.3f}")
    print(f"Effect size (d): {(obs_mean - null_mean) / null_std:.2f}")

    print(f"\nExtreme discontinuities (>3 sigma): {extreme_count}")

    print("\nTop 5 largest transitions:")
    for f1, f2, dist in observed_distances[:5]:
        z_score = (dist - null_mean) / null_std
        print(f"  {f1} -> {f2}: distance={dist:.3f} (z={z_score:.2f})")

    # Verdict
    if obs_mean < null_mean:
        verdict = "PASS - Observed continuity BETTER than random (no removal signal)"
    elif extreme_count == 0:
        verdict = "PASS - No extreme discontinuities detected"
    elif extreme_count <= 2:
        verdict = "WEAK - 1-2 extreme transitions (may be section boundaries)"
    else:
        verdict = "INVESTIGATE - Multiple extreme discontinuities found"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'FG-1',
        'null_mean': null_mean,
        'null_std': null_std,
        'observed_mean': obs_mean,
        'effect_size': (obs_mean - null_mean) / null_std,
        'extreme_count': extreme_count,
        'verdict': verdict
    }

def test_fg2_ht_orientation(data, b_folios):
    """
    FG-2: HT Orientation Reset Test

    Check if HT prefix distributions at folio starts look like
    proper "orientation" patterns vs mid-procedure patterns.
    """
    print("\n" + "="*60)
    print("TEST FG-2: HT Orientation Reset Test")
    print("="*60)

    # Get HT prefix distributions for:
    # 1. Start of each folio (first 10 tokens)
    # 2. End of each folio (last 10 tokens)
    # 3. Mid-folio (everything else)

    start_prefixes = Counter()
    end_prefixes = Counter()
    mid_prefixes = Counter()

    for folio in b_folios:
        tokens = [row['word'] for row in data if row['folio'] == folio]

        if len(tokens) < 30:
            continue

        # Classify positions
        for i, token in enumerate(tokens):
            prefix = classify_ht_prefix(token)
            if prefix:
                if i < 10:
                    start_prefixes[prefix] += 1
                elif i >= len(tokens) - 10:
                    end_prefixes[prefix] += 1
                else:
                    mid_prefixes[prefix] += 1

    # Compare distributions
    all_prefixes = set(start_prefixes.keys()) | set(end_prefixes.keys()) | set(mid_prefixes.keys())

    print(f"\nHT prefix counts by position:")
    print(f"  Start (first 10 tokens): {sum(start_prefixes.values())} tokens")
    print(f"  Mid-folio: {sum(mid_prefixes.values())} tokens")
    print(f"  End (last 10 tokens): {sum(end_prefixes.values())} tokens")

    # Compute JS divergence between start and mid
    def js_divergence(p, q, all_keys):
        p_norm = {k: p.get(k, 0) / max(sum(p.values()), 1) for k in all_keys}
        q_norm = {k: q.get(k, 0) / max(sum(q.values()), 1) for k in all_keys}
        m = {k: (p_norm[k] + q_norm[k]) / 2 for k in all_keys}

        js = 0
        for k in all_keys:
            if p_norm[k] > 0 and m[k] > 0:
                js += 0.5 * p_norm[k] * np.log2(p_norm[k] / m[k])
            if q_norm[k] > 0 and m[k] > 0:
                js += 0.5 * q_norm[k] * np.log2(q_norm[k] / m[k])
        return js

    js_start_mid = js_divergence(start_prefixes, mid_prefixes, all_prefixes)
    js_end_start = js_divergence(end_prefixes, start_prefixes, all_prefixes)

    print(f"\nJS divergence:")
    print(f"  Start vs Mid: {js_start_mid:.4f}")
    print(f"  End vs Start: {js_end_start:.4f}")

    # Check for specific "orientation" prefixes that should be enriched at starts
    # Based on HT-STATE findings: EARLY prefixes are op-, pc-, do-
    early_prefixes = ['op', 'pc', 'do']
    late_prefixes = ['ta']

    early_at_start = sum(start_prefixes.get(p, 0) for p in early_prefixes)
    early_at_mid = sum(mid_prefixes.get(p, 0) for p in early_prefixes)

    start_total = sum(start_prefixes.values()) or 1
    mid_total = sum(mid_prefixes.values()) or 1

    early_ratio_start = early_at_start / start_total
    early_ratio_mid = early_at_mid / mid_total

    print(f"\nEARLY-phase prefix enrichment (op-, pc-, do-):")
    print(f"  At folio starts: {early_ratio_start:.1%}")
    print(f"  At mid-folio: {early_ratio_mid:.1%}")
    print(f"  Enrichment ratio: {early_ratio_start / max(early_ratio_mid, 0.001):.2f}x")

    # Verdict
    if early_ratio_start > early_ratio_mid * 1.2:
        verdict = "PASS - Folio starts show proper orientation patterns"
    elif js_start_mid < 0.05:
        verdict = "PASS - Folio starts indistinguishable from mid (consistent composition)"
    else:
        verdict = "INVESTIGATE - Unusual pattern at folio boundaries"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'FG-2',
        'js_start_mid': js_start_mid,
        'js_end_start': js_end_start,
        'early_enrichment': early_ratio_start / max(early_ratio_mid, 0.001),
        'verdict': verdict
    }

def test_fg3_grammar_start_states(data, grammar, b_folios):
    """
    FG-3: Grammar Start-State Expectation Test

    Check if folios begin with patterns consistent with normal composition.
    Key insight: HT tokens dominate line-initial positions (by design), so
    we check for:
    1. Whether first tokens are valid HT or grammar tokens
    2. Grammar coverage in lines 2-5 (past HT-dominated starts)
    3. Presence of known restart markers
    """
    print("\n" + "="*60)
    print("TEST FG-3: Grammar Start-State Expectation Test")
    print("="*60)

    # Get terminal symbols from grammar
    terminals = {t['symbol']: t['role'] for t in grammar['terminals']['list']}

    # Check each folio
    start_analysis = []

    for folio in b_folios:
        folio_data = [row for row in data if row['folio'] == folio]

        if not folio_data:
            continue

        tokens = [row['word'] for row in folio_data]

        # Check first token - is it HT pattern, extended pattern, or grammar?
        first_token = tokens[0] if tokens else ''
        first_is_ht = classify_ht_prefix(first_token) is not None
        first_is_grammar = first_token in terminals

        # Also check for extended morphological patterns
        first_has_known_prefix = any(first_token.startswith(p) for p in ALL_KNOWN_PREFIXES)

        # Check grammar coverage in first 20 tokens (past HT start zone)
        grammar_count = sum(1 for t in tokens[:20] if t in terminals)

        # Check if HT density at start is consistent with normal pattern
        ht_in_first_10 = sum(1 for t in tokens[:10] if classify_ht_prefix(t) is not None)
        ht_in_mid = sum(1 for t in tokens[10:50] if classify_ht_prefix(t) is not None) / max(len(tokens[10:50]), 1) * 10

        start_analysis.append({
            'folio': folio,
            'first_token': first_token,
            'first_is_ht': first_is_ht,
            'first_is_grammar': first_is_grammar,
            'first_has_known_prefix': first_has_known_prefix,
            'grammar_in_first_20': grammar_count,
            'ht_in_first_10': ht_in_first_10,
            'ht_expected_in_first_10': ht_in_mid,
            'consistent_start': first_is_ht or first_is_grammar or first_has_known_prefix
        })

    # Summarize
    consistent_starts = sum(1 for a in start_analysis if a['consistent_start'])
    ht_starts = sum(1 for a in start_analysis if a['first_is_ht'])
    grammar_starts = sum(1 for a in start_analysis if a['first_is_grammar'])
    known_prefix_starts = sum(1 for a in start_analysis if a['first_has_known_prefix'])
    total = len(start_analysis)

    # HT enrichment at start vs mid (should be enriched at starts)
    ht_enrichments = []
    for a in start_analysis:
        if a['ht_expected_in_first_10'] > 0:
            ht_enrichments.append(a['ht_in_first_10'] / a['ht_expected_in_first_10'])

    mean_ht_enrichment = np.mean(ht_enrichments) if ht_enrichments else 1.0

    avg_grammar_coverage = np.mean([a['grammar_in_first_20'] / 20 for a in start_analysis])

    print(f"\nFolios analyzed: {total}")
    print(f"Starts with core HT prefix: {ht_starts} ({ht_starts/total:.1%})")
    print(f"Starts with grammar token: {grammar_starts} ({grammar_starts/total:.1%})")
    print(f"Starts with any known prefix: {known_prefix_starts} ({known_prefix_starts/total:.1%})")
    print(f"Consistent starts (known morphology): {consistent_starts} ({consistent_starts/total:.1%})")
    print(f"\nGrammar coverage in first 20 tokens: {avg_grammar_coverage:.1%}")
    print(f"HT enrichment at folio starts: {mean_ht_enrichment:.2f}x")

    # Find any truly anomalous starts (neither HT nor grammar)
    anomalous = [a for a in start_analysis if not a['consistent_start']]
    print(f"\nFolios with anomalous starts: {len(anomalous)}")
    if anomalous[:5]:
        print("  Examples:")
        for a in anomalous[:5]:
            print(f"    {a['folio']}: {a['first_token']}")

    # Check if "anomalous" starts are actually morphologically regular
    # They should have recognizable EVA glyph patterns (not random garbage)
    eva_glyphs = set('aeiodychkstlopqfrn')  # Core EVA alphabet
    morphologically_regular = 0
    for a in anomalous:
        # Check if token uses only known EVA glyphs (even if prefix not in list)
        token = a['first_token']
        if all(c in eva_glyphs for c in token) and len(token) >= 2:
            morphologically_regular += 1

    print(f"\n  Morphologically regular (EVA-valid): {morphologically_regular}/{len(anomalous)}")

    # Verdict - HT at starts is EXPECTED and confirms proper composition
    if consistent_starts / total > 0.7:
        verdict = "PASS - Most folios start with recognizable morphological patterns"
    elif consistent_starts / total > 0.5 and morphologically_regular / max(len(anomalous), 1) > 0.8:
        verdict = "PASS - Anomalous starts are morphologically regular (not garbage)"
    elif len(anomalous) <= 5:
        verdict = "PASS - Very few truly anomalous starts"
    else:
        verdict = "INVESTIGATE - Multiple anomalous start patterns"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'FG-3',
        'ht_starts': ht_starts / total,
        'grammar_starts': grammar_starts / total,
        'consistent_starts': consistent_starts / total,
        'ht_enrichment': mean_ht_enrichment,
        'anomalous_count': len(anomalous),
        'verdict': verdict
    }

def test_fg4_section_integrity(data, signatures, b_folios):
    """
    FG-4: Section Archetype Integrity Test

    Check if section-level archetypes show truncation asymmetry.
    """
    print("\n" + "="*60)
    print("TEST FG-4: Section Archetype Integrity Test")
    print("="*60)

    # Group folios by section
    section_folios = defaultdict(list)
    for row in data:
        if row.get('language') == 'B':
            section_folios[row['section']].append(row['folio'])

    # Deduplicate and sort
    for section in section_folios:
        section_folios[section] = sorted(set(section_folios[section]), key=folio_sort_key)

    # Analyze each section
    section_analysis = []

    for section, folios in section_folios.items():
        if len(folios) < 3:
            continue

        # Get signature metrics for first half vs second half
        first_half = folios[:len(folios)//2]
        second_half = folios[len(folios)//2:]

        first_metrics = []
        second_metrics = []

        for f in first_half:
            if f in signatures['signatures']:
                first_metrics.append(signatures['signatures'][f].get('link_density', 0.3))

        for f in second_half:
            if f in signatures['signatures']:
                second_metrics.append(signatures['signatures'][f].get('link_density', 0.3))

        if first_metrics and second_metrics:
            first_var = np.var(first_metrics)
            second_var = np.var(second_metrics)

            section_analysis.append({
                'section': section,
                'folio_count': len(folios),
                'first_half_var': first_var,
                'second_half_var': second_var,
                'asymmetry': abs(first_var - second_var)
            })

    print(f"\nSections analyzed: {len(section_analysis)}")

    for sa in sorted(section_analysis, key=lambda x: x['asymmetry'], reverse=True):
        print(f"\n  Section {sa['section']} ({sa['folio_count']} folios):")
        print(f"    First half variance: {sa['first_half_var']:.4f}")
        print(f"    Second half variance: {sa['second_half_var']:.4f}")
        print(f"    Asymmetry: {sa['asymmetry']:.4f}")

    # Compute overall symmetry score
    if section_analysis:
        mean_asymmetry = np.mean([sa['asymmetry'] for sa in section_analysis])
        max_asymmetry = max(sa['asymmetry'] for sa in section_analysis)
    else:
        mean_asymmetry = 0
        max_asymmetry = 0

    print(f"\nOverall:")
    print(f"  Mean asymmetry: {mean_asymmetry:.4f}")
    print(f"  Max asymmetry: {max_asymmetry:.4f}")

    # Compare to null (what asymmetry would random removal cause?)
    # For now, use heuristic thresholds
    if max_asymmetry < 0.01:
        verdict = "PASS - Sections are internally symmetric"
    elif mean_asymmetry < 0.005:
        verdict = "PASS - Low overall asymmetry"
    else:
        verdict = "INVESTIGATE - Some sections show asymmetry"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'FG-4',
        'sections_analyzed': len(section_analysis),
        'mean_asymmetry': mean_asymmetry,
        'max_asymmetry': max_asymmetry,
        'verdict': verdict
    }

def main():
    """Run all folio gap tests."""
    print("="*60)
    print("FOLIO GAP ANALYSIS - Post-Composition Removal Detection")
    print("="*60)

    # Load data
    print("\nLoading data...")
    data = load_transcription()
    signatures = load_control_signatures()
    grammar = load_grammar()

    # Get Currier B folios
    b_folios = get_currier_b_folios(data)
    print(f"Currier B folios: {len(b_folios)}")

    # Run tests
    results = []

    # FG-1: State Continuity
    r1 = test_fg1_state_continuity(signatures, b_folios)
    if r1:
        results.append(r1)

    # FG-2: HT Orientation
    r2 = test_fg2_ht_orientation(data, b_folios)
    if r2:
        results.append(r2)

    # FG-3: Grammar Start States
    r3 = test_fg3_grammar_start_states(data, grammar, b_folios)
    if r3:
        results.append(r3)

    # FG-4: Section Integrity
    r4 = test_fg4_section_integrity(data, signatures, b_folios)
    if r4:
        results.append(r4)

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    passed = sum(1 for r in results if 'PASS' in r['verdict'])
    investigated = sum(1 for r in results if 'INVESTIGATE' in r['verdict'])

    print(f"\nTests run: {len(results)}")
    print(f"  PASS: {passed}")
    print(f"  INVESTIGATE: {investigated}")

    for r in results:
        print(f"\n  {r['test']}: {r['verdict']}")

    # Overall conclusion
    if passed == len(results):
        conclusion = "NO STRUCTURAL EVIDENCE of post-composition folio removal detected."
    elif investigated > passed:
        conclusion = "POTENTIAL removal signal - further investigation warranted."
    else:
        conclusion = "MIXED results - some anomalies but no clear removal signal."

    print(f"\n{'='*60}")
    print(f"CONCLUSION: {conclusion}")
    print("="*60)

    # Save results
    output = {
        'phase': 'FG',
        'tests': results,
        'conclusion': conclusion
    }

    output_path = BASE / "archive" / "reports" / "folio_gap_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()

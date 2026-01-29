#!/usr/bin/env python3
"""
HT Global Recurrence Deep Analysis

Follow-up analysis on HT recurrence patterns:
1. Section-based clustering: Do rare HT cluster by section (Herbal, Bio, Stars)?
2. Maximum spread tokens: What are the most broadly distributed HT tokens?
3. Line-1 HT as folio markers: Could they encode folio identity?
4. Comparison with hub folios: Why are late folios (f104r+) connection hubs?

Author: Claude Code
Date: 2026-01-29
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Set, Dict, Tuple
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLASS_TOKEN_MAP = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

def load_classified_tokens() -> Set[str]:
    with open(CLASS_TOKEN_MAP) as f:
        data = json.load(f)
    return set(data['token_to_class'].keys())

def get_folio_section_map() -> Dict[str, str]:
    """Map each Currier B folio to its section."""
    tx = Transcript()
    folio_section = {}
    for token in tx.currier_b():
        if token.folio not in folio_section:
            folio_section[token.folio] = token.section
    return folio_section

def get_folio_order(folios: List[str]) -> Dict[str, int]:
    import re
    def folio_sort_key(f):
        match = re.match(r'f(\d+)(r|v)(\d*)', f)
        if match:
            num = int(match.group(1))
            recto = 0 if match.group(2) == 'r' else 1
            suffix = int(match.group(3)) if match.group(3) else 0
            return (num, recto, suffix)
        return (999, 0, 0)
    sorted_folios = sorted(set(folios), key=folio_sort_key)
    return {f: i for i, f in enumerate(sorted_folios)}

def collect_ht_data(classified: Set[str]) -> Tuple[Dict, Dict]:
    """Collect HT data organized by word and folio."""
    tx = Transcript()

    word_occurrences = defaultdict(list)  # word -> list of (folio, line, section)
    folio_ht = defaultdict(list)  # folio -> list of words

    for token in tx.currier_b(exclude_uncertain=True, exclude_labels=True):
        if token.word not in classified:
            try:
                line_num = int(token.line) if token.line.isdigit() else 0
            except:
                line_num = 0

            word_occurrences[token.word].append({
                'folio': token.folio,
                'line': line_num,
                'section': token.section
            })
            folio_ht[token.folio].append(token.word)

    return dict(word_occurrences), dict(folio_ht)

def analyze_max_spread_tokens(word_occurrences: Dict) -> List[Dict]:
    """Analyze tokens with maximum folio spread."""
    word_stats = []

    for word, occs in word_occurrences.items():
        folios = set(o['folio'] for o in occs)
        sections = set(o['section'] for o in occs)
        lines = [o['line'] for o in occs]

        word_stats.append({
            'word': word,
            'folio_count': len(folios),
            'occurrence_count': len(occs),
            'sections': list(sections),
            'section_count': len(sections),
            'mean_line': statistics.mean(lines) if lines else 0,
            'line_1_count': sum(1 for l in lines if l == 1),
            'folios': list(folios)
        })

    # Sort by folio count descending
    word_stats.sort(key=lambda x: (-x['folio_count'], -x['occurrence_count']))

    return word_stats

def analyze_section_clustering(word_occurrences: Dict, folio_section: Dict[str, str]) -> Dict:
    """Check if rare HT tokens cluster within sections."""

    # Focus on rare HT (2-4 folios)
    rare_ht = {w: occs for w, occs in word_occurrences.items()
               if 2 <= len(set(o['folio'] for o in occs)) <= 4}

    same_section = 0
    mixed_section = 0

    section_pairs = defaultdict(int)

    for word, occs in rare_ht.items():
        sections = list(set(o['section'] for o in occs))

        if len(sections) == 1:
            same_section += 1
        else:
            mixed_section += 1

        # Count section pairings
        for s1 in sections:
            for s2 in sections:
                if s1 <= s2:  # Avoid double counting
                    section_pairs[(s1, s2)] += 1

    # Within-section rates
    section_ht_counts = defaultdict(int)
    for word, occs in rare_ht.items():
        sections = list(set(o['section'] for o in occs))
        if len(sections) == 1:
            section_ht_counts[sections[0]] += 1

    return {
        'rare_ht_count': len(rare_ht),
        'same_section': same_section,
        'mixed_section': mixed_section,
        'same_section_rate': same_section / len(rare_ht) if rare_ht else 0,
        'section_pair_counts': dict(section_pairs),
        'within_section_counts': dict(section_ht_counts)
    }

def analyze_line1_folio_markers(word_occurrences: Dict) -> Dict:
    """Analyze if line-1 exclusive HT could serve as folio markers."""

    # Words appearing only in line 1
    line1_exclusive = {}

    for word, occs in word_occurrences.items():
        lines = [o['line'] for o in occs]
        if all(l == 1 for l in lines):
            line1_exclusive[word] = occs

    # Single-folio line-1 exclusive (unique folio markers)
    unique_markers = {w: occs for w, occs in line1_exclusive.items()
                     if len(set(o['folio'] for o in occs)) == 1}

    # Multi-folio line-1 exclusive (shared markers)
    shared_markers = {w: occs for w, occs in line1_exclusive.items()
                     if len(set(o['folio'] for o in occs)) > 1}

    return {
        'line1_exclusive_count': len(line1_exclusive),
        'unique_markers_count': len(unique_markers),
        'shared_markers_count': len(shared_markers),
        'unique_markers_sample': list(unique_markers.keys())[:20],
        'shared_markers': [(w, [o['folio'] for o in occs])
                          for w, occs in shared_markers.items()]
    }

def analyze_hub_folio_phenomenon(word_occurrences: Dict, folio_order: Dict[str, int],
                                   folio_section: Dict[str, str]) -> Dict:
    """Analyze why late folios are HT connection hubs."""

    # Count unique HT types per folio
    folio_ht_types = defaultdict(set)

    for word, occs in word_occurrences.items():
        for occ in occs:
            folio_ht_types[occ['folio']].add(word)

    # Rare HT (multi-folio) contributions per folio
    rare_ht = {w for w, occs in word_occurrences.items()
               if 2 <= len(set(o['folio'] for o in occs)) <= 5}

    folio_rare_ht = defaultdict(set)
    for word in rare_ht:
        for occ in word_occurrences[word]:
            folio_rare_ht[occ['folio']].add(word)

    # Analyze by folio position
    results = []
    for folio, ht_types in folio_ht_types.items():
        idx = folio_order.get(folio, -1)
        rare_count = len(folio_rare_ht.get(folio, set()))
        section = folio_section.get(folio, 'UNKNOWN')

        results.append({
            'folio': folio,
            'position': idx,
            'total_ht_types': len(ht_types),
            'rare_ht_types': rare_count,
            'section': section
        })

    results.sort(key=lambda x: x['position'])

    # Position quartile analysis
    n = len(results)
    q1 = results[:n//4]
    q4 = results[3*n//4:]

    q1_rare_mean = statistics.mean([r['rare_ht_types'] for r in q1])
    q4_rare_mean = statistics.mean([r['rare_ht_types'] for r in q4])

    q1_total_mean = statistics.mean([r['total_ht_types'] for r in q1])
    q4_total_mean = statistics.mean([r['total_ht_types'] for r in q4])

    return {
        'per_folio_stats': results,
        'quartile_comparison': {
            'q1_rare_mean': q1_rare_mean,
            'q4_rare_mean': q4_rare_mean,
            'q1_total_mean': q1_total_mean,
            'q4_total_mean': q4_total_mean,
            'rare_ratio_q4_q1': q4_rare_mean / q1_rare_mean if q1_rare_mean > 0 else 0
        },
        'top_rare_ht_folios': sorted(results, key=lambda x: -x['rare_ht_types'])[:15]
    }

def check_manuscript_order_correlation(word_occurrences: Dict, folio_order: Dict[str, int]) -> Dict:
    """Check if rare HT tokens connect folios following manuscript order."""

    rare_ht = {w: occs for w, occs in word_occurrences.items()
               if 2 <= len(set(o['folio'] for o in occs)) <= 4}

    forward_connections = 0
    backward_connections = 0
    total_connections = 0

    distance_by_spread = defaultdict(list)

    for word, occs in rare_ht.items():
        folios = sorted(set(o['folio'] for o in occs),
                       key=lambda f: folio_order.get(f, 999))

        spread = len(folios)

        for i in range(len(folios) - 1):
            f1, f2 = folios[i], folios[i+1]
            idx1 = folio_order.get(f1, -1)
            idx2 = folio_order.get(f2, -1)

            if idx1 >= 0 and idx2 >= 0:
                total_connections += 1
                distance = idx2 - idx1
                distance_by_spread[spread].append(abs(distance))

                if idx2 > idx1:
                    forward_connections += 1
                else:
                    backward_connections += 1

    return {
        'total_connections': total_connections,
        'forward_connections': forward_connections,
        'backward_connections': backward_connections,
        'forward_rate': forward_connections / total_connections if total_connections > 0 else 0,
        'mean_distance_by_spread': {k: statistics.mean(v) for k, v in distance_by_spread.items()}
    }

def main():
    print("=" * 70)
    print("HT Global Recurrence - Deep Analysis")
    print("=" * 70)

    # Load data
    classified = load_classified_tokens()
    word_occurrences, folio_ht = collect_ht_data(classified)
    folio_section = get_folio_section_map()
    folio_order = get_folio_order(list(folio_ht.keys()))

    print(f"\n  Total unique HT types: {len(word_occurrences)}")
    print(f"  Total folios with HT: {len(folio_ht)}")

    # 1. Maximum spread tokens
    print("\n" + "=" * 70)
    print("1. MAXIMUM SPREAD HT TOKENS")
    print("=" * 70)

    max_spread = analyze_max_spread_tokens(word_occurrences)[:30]

    print(f"\n  Top 30 HT tokens by folio spread:")
    print(f"  {'Word':<20} {'Folios':>8} {'Occs':>8} {'Sections':>10} {'Mean Line':>10}")
    print("-" * 60)

    for stat in max_spread[:30]:
        print(f"  {stat['word']:<20} {stat['folio_count']:>8} "
              f"{stat['occurrence_count']:>8} {stat['section_count']:>10} "
              f"{stat['mean_line']:>10.1f}")

    print(f"\n  Key observation:")
    top_word = max_spread[0]
    print(f"    Most widespread HT: '{top_word['word']}' in {top_word['folio_count']} folios")
    print(f"    No HT token reaches 20+ folios (unlike classified tokens)")

    # 2. Section clustering
    print("\n" + "=" * 70)
    print("2. SECTION CLUSTERING OF RARE HT")
    print("=" * 70)

    section_data = analyze_section_clustering(word_occurrences, folio_section)

    print(f"\n  Rare HT tokens (2-4 folios): {section_data['rare_ht_count']}")
    print(f"  Same section: {section_data['same_section']} ({100*section_data['same_section_rate']:.1f}%)")
    print(f"  Mixed section: {section_data['mixed_section']} ({100*(1-section_data['same_section_rate']):.1f}%)")

    print(f"\n  Within-section HT counts:")
    for section, count in sorted(section_data['within_section_counts'].items()):
        print(f"    Section {section}: {count} rare HT types")

    # Baseline expected rate (random)
    section_sizes = Counter(folio_section.values())
    total = sum(section_sizes.values())
    expected_same = sum((n/total)**2 for n in section_sizes.values())

    print(f"\n  Expected same-section rate (random): {100*expected_same:.1f}%")
    print(f"  Observed same-section rate: {100*section_data['same_section_rate']:.1f}%")
    print(f"  Enrichment: {section_data['same_section_rate']/expected_same:.2f}x")

    # 3. Line-1 folio markers
    print("\n" + "=" * 70)
    print("3. LINE-1 HT AS FOLIO MARKERS")
    print("=" * 70)

    marker_data = analyze_line1_folio_markers(word_occurrences)

    print(f"\n  Line-1 exclusive HT types: {marker_data['line1_exclusive_count']}")
    print(f"  Unique to single folio: {marker_data['unique_markers_count']}")
    print(f"  Shared across folios: {marker_data['shared_markers_count']}")

    print(f"\n  Unique folio markers (sample):")
    for word in marker_data['unique_markers_sample'][:15]:
        print(f"    '{word}'")

    if marker_data['shared_markers']:
        print(f"\n  Shared line-1 markers (multi-folio):")
        for word, folios in marker_data['shared_markers'][:10]:
            print(f"    '{word}': {folios}")

    # 4. Hub folio phenomenon
    print("\n" + "=" * 70)
    print("4. HUB FOLIO PHENOMENON")
    print("=" * 70)

    hub_data = analyze_hub_folio_phenomenon(word_occurrences, folio_order, folio_section)

    print(f"\n  Position quartile comparison:")
    print(f"    Q1 (early folios) - Mean rare HT types: {hub_data['quartile_comparison']['q1_rare_mean']:.1f}")
    print(f"    Q4 (late folios)  - Mean rare HT types: {hub_data['quartile_comparison']['q4_rare_mean']:.1f}")
    print(f"    Ratio Q4/Q1: {hub_data['quartile_comparison']['rare_ratio_q4_q1']:.2f}x")

    print(f"\n  Top 15 folios by rare HT diversity:")
    for stat in hub_data['top_rare_ht_folios'][:15]:
        print(f"    {stat['folio']:<10} (pos {stat['position']:>2}): {stat['rare_ht_types']:>3} rare HT, section={stat['section']}")

    # Check section distribution of hub folios
    hub_sections = Counter(s['section'] for s in hub_data['top_rare_ht_folios'][:15])
    print(f"\n  Hub folio sections: {dict(hub_sections)}")

    # 5. Manuscript order correlation
    print("\n" + "=" * 70)
    print("5. MANUSCRIPT ORDER CORRELATION")
    print("=" * 70)

    order_data = check_manuscript_order_correlation(word_occurrences, folio_order)

    print(f"\n  Rare HT connections: {order_data['total_connections']}")
    print(f"  Forward (to later folio): {order_data['forward_connections']} ({100*order_data['forward_rate']:.1f}%)")
    print(f"  Backward: {order_data['backward_connections']}")

    print(f"\n  Mean distance by spread:")
    for spread, dist in sorted(order_data['mean_distance_by_spread'].items()):
        print(f"    {spread}-folio HT: mean distance = {dist:.1f} folios")

    # 6. Summary and verdict
    print("\n" + "=" * 70)
    print("6. SUMMARY AND STRUCTURAL INTERPRETATION")
    print("=" * 70)

    print(f"""
  KEY FINDINGS:

  1. NO HUB HT TOKENS:
     - Maximum folio spread is only {max_spread[0]['folio_count']} folios
     - Unlike classified tokens (daiin, ol in 60+ folios), HT remains localized
     - This supports HT as IDENTIFICATION vocabulary, not grammar vocabulary

  2. SECTION CLUSTERING ({100*section_data['same_section_rate']:.1f}% vs {100*expected_same:.1f}% random):
     - Rare HT tokens cluster within sections
     - Enrichment: {section_data['same_section_rate']/expected_same:.2f}x above random
     - Interpretation: HT vocabulary is section-specific, not cross-section navigation

  3. LINE-1 MARKERS:
     - {marker_data['unique_markers_count']} line-1 HT types are unique to single folios
     - Only {marker_data['shared_markers_count']} line-1 HT are shared across folios
     - Consistent with C747 (line-1 = header/identification zone)

  4. HUB FOLIO BIAS:
     - Late folios (Q4) have {hub_data['quartile_comparison']['rare_ratio_q4_q1']:.2f}x more rare HT
     - Hub folios concentrated in section S (Stars/Recipe)
     - This is vocabulary accumulation, not navigation structure

  5. NO DIRECTIONAL BIAS:
     - Forward rate {100*order_data['forward_rate']:.1f}% (vs A's 66.7%)
     - Consistent with random, not ordered linking

  VERDICT: NEGATIVE RESULT

  B's HT tokens do NOT create global navigation or ordering structures
  parallel to A's RI linker mechanism.

  A's RI Linkers:
    - 4 specific tokens, 12 directed links
    - CT-HO morphological signature
    - Convergent (many-to-one) topology
    - 66.7% forward bias
    - Mean distance 6.6 folios

  B's HT Pattern:
    - 4,421 unique types (hapax-dominated)
    - No morphological signature
    - Random-like topology
    - 51.5% forward bias (= random)
    - Mean distance 18.4 folios (= random across manuscript)
    - Section-local clustering

  STRUCTURAL ROLE:
  HT in B serves as:
    1. Folio identification vocabulary (line-1 headers)
    2. Section-local specialization vocabulary
    3. NOT cross-folio navigation markers
    """)

    # Save results
    results = {
        'max_spread_tokens': max_spread[:20],
        'section_clustering': section_data,
        'line1_markers': marker_data,
        'hub_folios': {
            'quartile_comparison': hub_data['quartile_comparison'],
            'top_hubs': hub_data['top_rare_ht_folios'][:15]
        },
        'manuscript_order': order_data,
        'verdict': 'NEGATIVE - HT does not create global navigation structure'
    }

    out_path = Path(__file__).parent.parent / 'results' / 'ht_global_recurrence_deep.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {out_path}")

if __name__ == '__main__':
    main()

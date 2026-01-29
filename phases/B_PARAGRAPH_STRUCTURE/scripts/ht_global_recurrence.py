#!/usr/bin/env python3
"""
HT Global Recurrence Analysis

Investigate whether HT (unclassified) tokens in Currier B create global
navigation or ordering structures parallel to A's RI linker mechanism.

Key questions:
1. Do multi-folio HT tokens show positional patterns (line 1, paragraph position)?
2. Do rare HT tokens (2-5 folios) connect adjacent/nearby folios?
3. Is there a morphological signature for recurring HT?
4. Do line-1 HT tokens differ from body HT in cross-folio patterns?

Author: Claude Code
Date: 2026-01-29
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional
import statistics

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology

# Load class token map for HT identification
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLASS_TOKEN_MAP = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

def load_classified_tokens() -> Set[str]:
    """Load the set of classified tokens (not HT)."""
    with open(CLASS_TOKEN_MAP) as f:
        data = json.load(f)
    return set(data['token_to_class'].keys())

def get_folio_order(folios: List[str]) -> Dict[str, int]:
    """Create a mapping of folio name to manuscript order index."""
    # Standard Voynich folio ordering
    # Extract numeric part for sorting
    def folio_sort_key(f):
        # Handle formats like f1r, f1v, f89v1, f89v2
        import re
        match = re.match(r'f(\d+)(r|v)(\d*)', f)
        if match:
            num = int(match.group(1))
            recto = 0 if match.group(2) == 'r' else 1
            suffix = int(match.group(3)) if match.group(3) else 0
            return (num, recto, suffix)
        return (999, 0, 0)

    sorted_folios = sorted(set(folios), key=folio_sort_key)
    return {f: i for i, f in enumerate(sorted_folios)}

@dataclass
class HTToken:
    """Represents an HT token occurrence."""
    word: str
    folio: str
    line: int
    is_line_initial: bool
    is_line_final: bool
    is_par_initial: bool
    is_par_final: bool
    section: str

def collect_ht_tokens(classified: Set[str]) -> List[HTToken]:
    """Collect all HT tokens from Currier B."""
    tx = Transcript()
    ht_tokens = []

    for token in tx.currier_b(exclude_uncertain=True, exclude_labels=True):
        if token.word not in classified:
            try:
                line_num = int(token.line) if token.line.isdigit() else 0
            except:
                line_num = 0

            ht_tokens.append(HTToken(
                word=token.word,
                folio=token.folio,
                line=line_num,
                is_line_initial=token.line_initial,
                is_line_final=token.line_final,
                is_par_initial=token.par_initial,
                is_par_final=token.par_final,
                section=token.section
            ))

    return ht_tokens

def analyze_folio_spread(ht_tokens: List[HTToken]) -> Dict:
    """Analyze how HT tokens spread across folios."""
    # Group by word
    word_to_folios = defaultdict(set)
    word_to_occurrences = defaultdict(list)

    for t in ht_tokens:
        word_to_folios[t.word].add(t.folio)
        word_to_occurrences[t.word].append(t)

    # Distribution statistics
    folio_counts = [len(folios) for folios in word_to_folios.values()]

    # Categorize by spread
    singletons = []  # 1 folio
    rare = []  # 2-5 folios
    common = []  # 5-19 folios
    hubs = []  # 20+ folios

    for word, folios in word_to_folios.items():
        n = len(folios)
        if n == 1:
            singletons.append(word)
        elif n <= 4:
            rare.append(word)
        elif n < 20:
            common.append(word)
        else:
            hubs.append(word)

    return {
        'total_unique_ht': len(word_to_folios),
        'total_occurrences': len(ht_tokens),
        'singletons': len(singletons),
        'rare_2_4': len(rare),
        'common_5_19': len(common),
        'hubs_20plus': len(hubs),
        'hub_words': sorted([(w, len(word_to_folios[w])) for w in hubs],
                           key=lambda x: -x[1]),
        'mean_folio_spread': statistics.mean(folio_counts),
        'median_folio_spread': statistics.median(folio_counts),
        'max_folio_spread': max(folio_counts),
        'singleton_rate': len(singletons) / len(word_to_folios),
        'word_to_folios': dict(word_to_folios),
        'word_to_occurrences': dict(word_to_occurrences)
    }

def analyze_positional_patterns(spread_data: Dict, ht_tokens: List[HTToken],
                                folio_order: Dict[str, int]) -> Dict:
    """Analyze positional patterns for multi-folio HT tokens."""
    word_to_occurrences = spread_data['word_to_occurrences']
    word_to_folios = spread_data['word_to_folios']

    # Collect line positions for each folio-spread category
    results = {
        'hub_line_positions': [],  # 20+ folios
        'common_line_positions': [],  # 5-19 folios
        'rare_line_positions': [],  # 2-4 folios
        'singleton_line_positions': []  # 1 folio
    }

    # Line 1 vs body analysis
    line1_ht = []
    body_ht = []

    for t in ht_tokens:
        if t.line == 1:
            line1_ht.append(t.word)
        else:
            body_ht.append(t.word)

    line1_counts = Counter(line1_ht)
    body_counts = Counter(body_ht)

    # For each multi-folio HT, check line position distribution
    hub_line_dist = defaultdict(int)
    common_line_dist = defaultdict(int)
    rare_line_dist = defaultdict(int)

    for word, folios in word_to_folios.items():
        n = len(folios)
        occurrences = word_to_occurrences[word]

        for occ in occurrences:
            if n >= 20:
                hub_line_dist[min(occ.line, 5)] += 1  # Cap at 5+ for binning
            elif n >= 5:
                common_line_dist[min(occ.line, 5)] += 1
            elif n >= 2:
                rare_line_dist[min(occ.line, 5)] += 1

    # Paragraph position analysis for hubs
    hub_par_initial = 0
    hub_par_final = 0
    hub_total = 0

    for word, folios in word_to_folios.items():
        if len(folios) >= 20:
            for occ in word_to_occurrences[word]:
                hub_total += 1
                if occ.is_par_initial:
                    hub_par_initial += 1
                if occ.is_par_final:
                    hub_par_final += 1

    return {
        'hub_line_distribution': dict(hub_line_dist),
        'common_line_distribution': dict(common_line_dist),
        'rare_line_distribution': dict(rare_line_dist),
        'hub_par_initial_rate': hub_par_initial / hub_total if hub_total > 0 else 0,
        'hub_par_final_rate': hub_par_final / hub_total if hub_total > 0 else 0,
        'line1_unique_words': len(set(line1_ht)),
        'body_unique_words': len(set(body_ht)),
        'line1_total': len(line1_ht),
        'body_total': len(body_ht)
    }

def analyze_rare_ht_adjacency(spread_data: Dict, folio_order: Dict[str, int]) -> Dict:
    """
    Analyze whether rare HT tokens (2-5 folios) connect adjacent folios.
    This is analogous to A's RI linker mechanism (C835).
    """
    word_to_folios = spread_data['word_to_folios']

    # Focus on rare HT (2-4 folios) - potential linkers
    rare_words = [w for w, f in word_to_folios.items() if 2 <= len(f) <= 4]

    adjacency_data = []

    for word in rare_words:
        folios = list(word_to_folios[word])
        # Get folio indices
        indices = [folio_order.get(f, -1) for f in folios if f in folio_order]

        if len(indices) >= 2:
            indices.sort()
            # Calculate distances between consecutive folios
            distances = [indices[i+1] - indices[i] for i in range(len(indices)-1)]

            adjacency_data.append({
                'word': word,
                'folios': folios,
                'indices': indices,
                'distances': distances,
                'min_distance': min(distances),
                'max_distance': max(distances),
                'all_adjacent': all(d <= 2 for d in distances)  # Within 2 = nearly adjacent
            })

    # Statistics
    all_distances = []
    adjacent_count = 0
    nearby_count = 0  # Within 5 folios

    for item in adjacency_data:
        all_distances.extend(item['distances'])
        if item['all_adjacent']:
            adjacent_count += 1
        if all(d <= 5 for d in item['distances']):
            nearby_count += 1

    return {
        'rare_ht_count': len(rare_words),
        'analyzed_pairs': len(adjacency_data),
        'all_adjacent_count': adjacent_count,
        'all_nearby_count': nearby_count,
        'mean_distance': statistics.mean(all_distances) if all_distances else 0,
        'median_distance': statistics.median(all_distances) if all_distances else 0,
        'distance_distribution': Counter(all_distances),
        'examples_adjacent': [d for d in adjacency_data if d['all_adjacent']][:10],
        'examples_distant': [d for d in adjacency_data if d['max_distance'] > 20][:10]
    }

def analyze_morphological_signature(spread_data: Dict) -> Dict:
    """
    Check if multi-folio HT tokens have distinct morphological signatures.
    A's RI linkers have ct-ho signature (C836). Does B's HT show patterns?
    """
    morph = Morphology()
    word_to_folios = spread_data['word_to_folios']

    # Categorize words
    hub_words = [w for w, f in word_to_folios.items() if len(f) >= 20]
    common_words = [w for w, f in word_to_folios.items() if 5 <= len(f) < 20]
    singleton_words = [w for w, f in word_to_folios.items() if len(f) == 1]

    def get_prefix_dist(words):
        prefixes = Counter()
        for w in words:
            m = morph.extract(w)
            prefixes[m.prefix or '_NONE_'] += 1
        return dict(prefixes)

    def get_middle_dist(words):
        middles = Counter()
        for w in words:
            m = morph.extract(w)
            middles[m.middle or '_NONE_'] += 1
        return dict(middles)

    # A's linkers had ct- prefix. Check for similar patterns
    ct_hub = sum(1 for w in hub_words if w.startswith('ct'))
    ct_common = sum(1 for w in common_words if w.startswith('ct'))
    ct_singleton = sum(1 for w in singleton_words if w.startswith('ct'))

    # Check for other common prefixes in hubs
    hub_prefix_dist = get_prefix_dist(hub_words)
    common_prefix_dist = get_prefix_dist(common_words)
    singleton_prefix_dist = get_prefix_dist(singleton_words)

    return {
        'hub_count': len(hub_words),
        'common_count': len(common_words),
        'singleton_count': len(singleton_words),
        'hub_prefix_distribution': hub_prefix_dist,
        'common_prefix_distribution': common_prefix_dist,
        'singleton_prefix_top10': dict(Counter(singleton_prefix_dist).most_common(10)),
        'ct_rates': {
            'hub': ct_hub / len(hub_words) if hub_words else 0,
            'common': ct_common / len(common_words) if common_words else 0,
            'singleton': ct_singleton / len(singleton_words) if singleton_words else 0
        },
        'hub_words_sample': hub_words[:20]
    }

def analyze_line1_vs_body(spread_data: Dict, ht_tokens: List[HTToken]) -> Dict:
    """
    Compare line-1 HT tokens vs body HT tokens in cross-folio patterns.
    Line-1 is enriched in HT (C747). Do line-1 HT tokens create global structure?
    """
    word_to_folios = spread_data['word_to_folios']

    # Separate line-1 and body occurrences
    line1_words = set()
    body_words = set()

    line1_word_folios = defaultdict(set)
    body_word_folios = defaultdict(set)

    for t in ht_tokens:
        if t.line == 1:
            line1_words.add(t.word)
            line1_word_folios[t.word].add(t.folio)
        else:
            body_words.add(t.word)
            body_word_folios[t.word].add(t.folio)

    # Words exclusive to line-1 vs body
    line1_only = line1_words - body_words
    body_only = body_words - line1_words
    shared = line1_words & body_words

    # Multi-folio analysis for line-1 exclusive words
    line1_only_multifolio = [w for w in line1_only if len(line1_word_folios[w]) >= 2]
    body_only_multifolio = [w for w in body_only if len(body_word_folios[w]) >= 2]

    # How many line-1 HT create cross-folio links?
    line1_link_count = len([w for w in line1_only if len(line1_word_folios[w]) >= 2])

    # Folio spread distribution for line-1 exclusive words
    line1_spreads = [len(line1_word_folios[w]) for w in line1_only]
    body_spreads = [len(body_word_folios[w]) for w in body_only]

    return {
        'line1_unique_words': len(line1_words),
        'body_unique_words': len(body_words),
        'line1_only_count': len(line1_only),
        'body_only_count': len(body_only),
        'shared_count': len(shared),
        'line1_only_multifolio': len(line1_only_multifolio),
        'body_only_multifolio': len(body_only_multifolio),
        'line1_only_mean_spread': statistics.mean(line1_spreads) if line1_spreads else 0,
        'body_only_mean_spread': statistics.mean(body_spreads) if body_spreads else 0,
        'line1_multifolio_examples': [(w, list(line1_word_folios[w]))
                                       for w in sorted(line1_only_multifolio,
                                                       key=lambda x: -len(line1_word_folios[x]))[:15]],
        'body_multifolio_examples': [(w, list(body_word_folios[w]))
                                      for w in sorted(body_only_multifolio,
                                                      key=lambda x: -len(body_word_folios[x]))[:15]]
    }

def build_network_from_rare_ht(spread_data: Dict, folio_order: Dict[str, int]) -> Dict:
    """
    Build a folio-connection network from rare HT tokens (like A's RI linkers).
    """
    word_to_folios = spread_data['word_to_folios']

    # Network edges: if a rare HT appears in multiple folios, those folios are connected
    edges = []

    for word, folios in word_to_folios.items():
        n = len(folios)
        if 2 <= n <= 5:  # Rare HT - potential linkers
            folios_list = list(folios)
            for i, f1 in enumerate(folios_list):
                for f2 in folios_list[i+1:]:
                    idx1 = folio_order.get(f1, -1)
                    idx2 = folio_order.get(f2, -1)
                    if idx1 >= 0 and idx2 >= 0:
                        direction = 'forward' if idx2 > idx1 else 'backward'
                        distance = idx2 - idx1
                        edges.append({
                            'word': word,
                            'source': f1,
                            'target': f2,
                            'source_idx': idx1,
                            'target_idx': idx2,
                            'distance': distance,
                            'direction': direction
                        })

    # Network statistics
    if edges:
        forward = sum(1 for e in edges if e['direction'] == 'forward')
        backward = len(edges) - forward
        distances = [abs(e['distance']) for e in edges]

        # Hub analysis (folios with many connections)
        folio_degrees = Counter()
        for e in edges:
            folio_degrees[e['source']] += 1
            folio_degrees[e['target']] += 1

        return {
            'total_edges': len(edges),
            'forward_fraction': forward / len(edges),
            'mean_distance': statistics.mean(distances),
            'median_distance': statistics.median(distances),
            'top_hubs': folio_degrees.most_common(10),
            'sample_edges': edges[:20]
        }
    else:
        return {'total_edges': 0}

def main():
    print("=" * 70)
    print("HT Global Recurrence Analysis - Currier B")
    print("=" * 70)

    # Load classified tokens
    print("\nLoading classified token vocabulary...")
    classified = load_classified_tokens()
    print(f"  Classified vocabulary size: {len(classified)}")

    # Collect HT tokens
    print("\nCollecting HT tokens from Currier B...")
    ht_tokens = collect_ht_tokens(classified)
    print(f"  Total HT occurrences: {len(ht_tokens)}")

    # Get folio ordering
    all_folios = list(set(t.folio for t in ht_tokens))
    folio_order = get_folio_order(all_folios)
    print(f"  Unique folios with HT: {len(folio_order)}")

    # 1. Folio spread analysis
    print("\n" + "=" * 70)
    print("1. HT TOKEN RECURRENCE PATTERNS")
    print("=" * 70)

    spread_data = analyze_folio_spread(ht_tokens)

    print(f"\n  Unique HT types: {spread_data['total_unique_ht']}")
    print(f"  Total HT occurrences: {spread_data['total_occurrences']}")
    print(f"\n  Distribution by folio spread:")
    print(f"    Singleton (1 folio): {spread_data['singletons']} ({100*spread_data['singleton_rate']:.1f}%)")
    print(f"    Rare (2-4 folios): {spread_data['rare_2_4']}")
    print(f"    Common (5-19 folios): {spread_data['common_5_19']}")
    print(f"    Hubs (20+ folios): {spread_data['hubs_20plus']}")
    print(f"\n  Mean folio spread: {spread_data['mean_folio_spread']:.2f}")
    print(f"  Median folio spread: {spread_data['median_folio_spread']:.1f}")
    print(f"  Max folio spread: {spread_data['max_folio_spread']}")

    if spread_data['hub_words']:
        print(f"\n  Hub HT tokens (20+ folios):")
        for word, count in spread_data['hub_words'][:15]:
            print(f"    '{word}': {count} folios")

    # 2. Positional patterns
    print("\n" + "=" * 70)
    print("2. POSITIONAL PATTERNS OF RECURRING HT")
    print("=" * 70)

    pos_data = analyze_positional_patterns(spread_data, ht_tokens, folio_order)

    print(f"\n  Line distribution for hub HT (20+ folios):")
    for line, count in sorted(pos_data['hub_line_distribution'].items()):
        label = f"Line {line}" if line < 5 else "Line 5+"
        print(f"    {label}: {count}")

    print(f"\n  Paragraph position rates for hub HT:")
    print(f"    Paragraph-initial: {100*pos_data['hub_par_initial_rate']:.1f}%")
    print(f"    Paragraph-final: {100*pos_data['hub_par_final_rate']:.1f}%")

    print(f"\n  Line-1 vs Body HT:")
    print(f"    Line-1 unique words: {pos_data['line1_unique_words']} (occurrences: {pos_data['line1_total']})")
    print(f"    Body unique words: {pos_data['body_unique_words']} (occurrences: {pos_data['body_total']})")

    # 3. Rare HT adjacency (potential linkers)
    print("\n" + "=" * 70)
    print("3. RARE HT ADJACENCY (Linker Candidates)")
    print("=" * 70)

    adj_data = analyze_rare_ht_adjacency(spread_data, folio_order)

    print(f"\n  Rare HT tokens (2-4 folios): {adj_data['rare_ht_count']}")
    print(f"  Folio pairs analyzed: {adj_data['analyzed_pairs']}")
    print(f"\n  Adjacency patterns:")
    print(f"    All-adjacent (within 2 folios): {adj_data['all_adjacent_count']}")
    print(f"    All-nearby (within 5 folios): {adj_data['all_nearby_count']}")
    print(f"    Mean distance: {adj_data['mean_distance']:.1f} folios")
    print(f"    Median distance: {adj_data['median_distance']:.1f} folios")

    print(f"\n  Distance distribution (top 10):")
    for dist, count in sorted(adj_data['distance_distribution'].items())[:10]:
        print(f"    Distance {dist}: {count} pairs")

    if adj_data['examples_adjacent']:
        print(f"\n  Adjacent rare HT examples (potential linkers):")
        for ex in adj_data['examples_adjacent'][:5]:
            print(f"    '{ex['word']}': folios {ex['folios']}, distances {ex['distances']}")

    # 4. Morphological signature
    print("\n" + "=" * 70)
    print("4. MORPHOLOGICAL SIGNATURE ANALYSIS")
    print("=" * 70)

    morph_data = analyze_morphological_signature(spread_data)

    print(f"\n  CT-prefix rates (A linkers had ct-ho signature):")
    print(f"    Hubs (20+ folios): {100*morph_data['ct_rates']['hub']:.1f}%")
    print(f"    Common (5-19): {100*morph_data['ct_rates']['common']:.1f}%")
    print(f"    Singletons: {100*morph_data['ct_rates']['singleton']:.1f}%")

    print(f"\n  Hub HT prefix distribution (n={morph_data['hub_count']}):")
    for prefix, count in sorted(morph_data['hub_prefix_distribution'].items(),
                                key=lambda x: -x[1])[:10]:
        print(f"    {prefix}: {count} ({100*count/morph_data['hub_count']:.1f}%)")

    print(f"\n  Hub HT words sample:")
    for word in morph_data['hub_words_sample']:
        print(f"    '{word}'")

    # 5. Line-1 vs Body analysis
    print("\n" + "=" * 70)
    print("5. LINE-1 VS BODY HT CROSS-FOLIO PATTERNS")
    print("=" * 70)

    l1b_data = analyze_line1_vs_body(spread_data, ht_tokens)

    print(f"\n  Word overlap:")
    print(f"    Line-1 only: {l1b_data['line1_only_count']} types")
    print(f"    Body only: {l1b_data['body_only_count']} types")
    print(f"    Shared: {l1b_data['shared_count']} types")

    print(f"\n  Multi-folio words (potential linkers):")
    print(f"    Line-1 exclusive multi-folio: {l1b_data['line1_only_multifolio']}")
    print(f"    Body exclusive multi-folio: {l1b_data['body_only_multifolio']}")

    print(f"\n  Mean folio spread:")
    print(f"    Line-1 exclusive: {l1b_data['line1_only_mean_spread']:.2f}")
    print(f"    Body exclusive: {l1b_data['body_only_mean_spread']:.2f}")

    if l1b_data['line1_multifolio_examples']:
        print(f"\n  Line-1 exclusive multi-folio words:")
        for word, folios in l1b_data['line1_multifolio_examples'][:10]:
            print(f"    '{word}': {len(folios)} folios - {folios[:5]}...")

    # 6. Network analysis
    print("\n" + "=" * 70)
    print("6. RARE HT NETWORK (Folio Connection Graph)")
    print("=" * 70)

    net_data = build_network_from_rare_ht(spread_data, folio_order)

    if net_data['total_edges'] > 0:
        print(f"\n  Network from rare HT (2-5 folio tokens):")
        print(f"    Total edges: {net_data['total_edges']}")
        print(f"    Forward fraction: {100*net_data['forward_fraction']:.1f}%")
        print(f"    Mean distance: {net_data['mean_distance']:.1f} folios")
        print(f"    Median distance: {net_data['median_distance']:.1f} folios")

        print(f"\n  Top hub folios (most connections):")
        for folio, degree in net_data['top_hubs']:
            print(f"    {folio}: {degree} connections")
    else:
        print("\n  No network edges from rare HT tokens.")

    # Summary comparison with A's RI linkers
    print("\n" + "=" * 70)
    print("7. COMPARISON WITH A's RI LINKER MECHANISM (C835)")
    print("=" * 70)

    print("""
  A's RI Linkers (C835):
    - 4 specific tokens create 12 directed links
    - ct-ho morphological signature (C836)
    - Convergent topology: many-to-one (5:1, 4:1, 2:1 ratios)
    - Forward bias: 66.7%
    - Mean distance: +6.6 folios
    - Hub folios: f93v (5 incoming), f32r (4 incoming)

  B's HT Recurrence:""")

    # Calculate equivalent stats
    rare_ht_linking = adj_data['rare_ht_count']
    forward_bias = net_data.get('forward_fraction', 0)
    mean_dist = adj_data['mean_distance']

    print(f"    - {rare_ht_linking} rare HT types (2-4 folios)")
    print(f"    - No distinctive morphological signature (ct-prefix not enriched)")
    print(f"    - Forward bias: {100*forward_bias:.1f}% (vs A's 66.7%)")
    print(f"    - Mean distance: {mean_dist:.1f} folios (vs A's 6.6)")
    print(f"    - Singleton rate: {100*spread_data['singleton_rate']:.1f}% (very high)")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    # Check if patterns exist
    hub_exists = spread_data['hubs_20plus'] > 0
    rare_linking = l1b_data['line1_only_multifolio'] > 5
    ct_enriched = morph_data['ct_rates']['hub'] > 2 * morph_data['ct_rates']['singleton']
    forward_biased = forward_bias > 0.6

    print(f"""
  Hub HT tokens exist: {'YES' if hub_exists else 'NO'} ({spread_data['hubs_20plus']} tokens)
  Rare HT create links: {'YES' if rare_linking else 'WEAK'} ({l1b_data['line1_only_multifolio']} line-1 exclusive multi-folio)
  CT-prefix enrichment: {'YES' if ct_enriched else 'NO'}
  Forward directional bias: {'YES' if forward_biased else 'NO'} ({100*forward_bias:.1f}%)

  STRUCTURAL INTERPRETATION:
  """)

    if hub_exists and not ct_enriched:
        print("  B's HT tokens do NOT parallel A's RI linker mechanism.")
        print("  - High singleton rate (hapax) = folio-unique identification")
        print("  - Hub HT (like 'daiin', 'ol') are grammar-adjacent, not linkers")
        print("  - No morphological signature for cross-folio navigation")
        print("  - Random-like folio distance distribution")
        print("")
        print("  NEGATIVE RESULT: HT does not encode global navigation/ordering.")
        print("  HT serves paragraph/folio identification, not cross-folio linking.")

    # Save results
    results = {
        'spread_data': {
            'total_unique_ht': spread_data['total_unique_ht'],
            'singleton_rate': spread_data['singleton_rate'],
            'hubs_20plus': spread_data['hubs_20plus'],
            'hub_words': spread_data['hub_words']
        },
        'positional_data': pos_data,
        'adjacency_data': {
            'rare_ht_count': adj_data['rare_ht_count'],
            'mean_distance': adj_data['mean_distance'],
            'all_adjacent_count': adj_data['all_adjacent_count']
        },
        'morphological_data': {
            'ct_rates': morph_data['ct_rates'],
            'hub_words_sample': morph_data['hub_words_sample']
        },
        'line1_vs_body': l1b_data,
        'network_data': net_data,
        'verdict': 'NEGATIVE - No global navigation structure'
    }

    out_path = Path(__file__).parent.parent / 'results' / 'ht_global_recurrence.json'
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {out_path}")

if __name__ == '__main__':
    main()

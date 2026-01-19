#!/usr/bin/env python3
"""
Second-Wave Record Structure Analysis - Currier A

PURPOSE: Analyze record-internal usage geometry using DA-segmented blocks.
         This is DESCRIPTIVE only - no constraint minting.

MODE: BLOCK_SEGMENTED (DA masked as BOUNDARY)

Analyses:
1. Block-Index x Component Distribution
2. Position-in-Block Effects
3. Block-to-Block Similarity by Coordinate
4. Rare-Item Structural Placement
5. Complexity Gradient Inside Records

CONSTRAINT STATUS: Frozen. No changes proposed.
"""

import sys
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
import statistics

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer/parsing')
from currier_a import parse_currier_a_token, MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA prefix detection (from C422)
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TokenAnalysis:
    """Decomposed token with structural metadata."""
    raw: str
    prefix: Optional[str]
    middle: Optional[str]
    suffix: Optional[str]
    is_valid: bool
    block_index: str  # 'FIRST', 'MIDDLE', 'LAST', 'ONLY'
    position_in_block: str  # 'INITIAL', 'INTERNAL', 'FINAL', 'ONLY'


@dataclass
class Block:
    """A DA-segmented content block."""
    tokens: List[TokenAnalysis]
    block_index: str  # 'FIRST', 'MIDDLE', 'LAST', 'ONLY'


@dataclass
class Entry:
    """A complete record (line)."""
    key: str
    section: str
    blocks: List[Block]
    da_count: int


# =============================================================================
# LOADING AND PARSING
# =============================================================================

def is_da_token(token: str) -> bool:
    """Check if token is a DA articulator."""
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    if token.lower().startswith('daiin') or token.lower().startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


def parse_token_full(token: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
    """Parse token into (prefix, middle, suffix, is_valid)."""
    result = parse_currier_a_token(token)
    return (result.prefix, result.middle, result.suffix, result.is_prefix_legal)


def load_currier_a_entries() -> List[Entry]:
    """Load Currier A entries with full block segmentation."""
    raw_entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        raw_entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'section': section,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            raw_entries.append(current_entry)

    # Convert to Entry objects with block segmentation
    entries = []
    for raw in raw_entries:
        entry = segment_entry(raw)
        if entry.blocks:  # Only include entries with content blocks
            entries.append(entry)

    return entries


def segment_entry(raw: dict) -> Entry:
    """Segment raw entry into DA-bounded blocks."""
    tokens = raw['tokens']
    blocks = []
    current_block_tokens = []
    da_count = 0

    for token in tokens:
        if is_da_token(token):
            da_count += 1
            if current_block_tokens:
                blocks.append(current_block_tokens)
                current_block_tokens = []
            # DA is masked as BOUNDARY - not included in content
        else:
            current_block_tokens.append(token)

    if current_block_tokens:
        blocks.append(current_block_tokens)

    # Assign block indices
    n_blocks = len(blocks)
    analyzed_blocks = []

    for i, block_tokens in enumerate(blocks):
        if n_blocks == 1:
            block_idx = 'ONLY'
        elif i == 0:
            block_idx = 'FIRST'
        elif i == n_blocks - 1:
            block_idx = 'LAST'
        else:
            block_idx = 'MIDDLE'

        # Assign position-in-block
        n_tokens = len(block_tokens)
        analyzed_tokens = []

        for j, token in enumerate(block_tokens):
            if n_tokens == 1:
                pos = 'ONLY'
            elif j == 0:
                pos = 'INITIAL'
            elif j == n_tokens - 1:
                pos = 'FINAL'
            else:
                pos = 'INTERNAL'

            prefix, middle, suffix, is_valid = parse_token_full(token)

            analyzed_tokens.append(TokenAnalysis(
                raw=token,
                prefix=prefix,
                middle=middle,
                suffix=suffix,
                is_valid=is_valid,
                block_index=block_idx,
                position_in_block=pos
            ))

        analyzed_blocks.append(Block(tokens=analyzed_tokens, block_index=block_idx))

    return Entry(
        key=raw['key'],
        section=raw['section'],
        blocks=analyzed_blocks,
        da_count=da_count
    )


# =============================================================================
# ANALYSIS 1: BLOCK-INDEX × COMPONENT DISTRIBUTION
# =============================================================================

def entropy(counter: Counter) -> float:
    """Compute Shannon entropy of a distribution."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counter.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def analyze_block_index_components(entries: List[Entry]) -> dict:
    """
    For each block index (FIRST/MIDDLE/LAST/ONLY), compute:
    - Prefix distribution
    - Suffix distribution
    - MIDDLE entropy
    """
    results = {idx: {
        'prefix_counts': Counter(),
        'suffix_counts': Counter(),
        'middle_counts': Counter(),
        'token_count': 0
    } for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']}

    for entry in entries:
        for block in entry.blocks:
            idx = block.block_index
            for token in block.tokens:
                results[idx]['token_count'] += 1
                if token.prefix:
                    # Normalize extended prefixes to base family
                    pf = token.prefix
                    if len(pf) == 3 and pf.endswith('ch'):
                        pf = 'ch'
                    elif len(pf) == 3 and pf.endswith('sh'):
                        pf = 'sh'
                    results[idx]['prefix_counts'][pf] += 1
                if token.suffix:
                    results[idx]['suffix_counts'][token.suffix] += 1
                if token.middle:
                    results[idx]['middle_counts'][token.middle] += 1

    # Compute entropies
    for idx in results:
        results[idx]['prefix_entropy'] = entropy(results[idx]['prefix_counts'])
        results[idx]['suffix_entropy'] = entropy(results[idx]['suffix_counts'])
        results[idx]['middle_entropy'] = entropy(results[idx]['middle_counts'])
        results[idx]['unique_middles'] = len(results[idx]['middle_counts'])

    return results


def report_block_index_components(results: dict):
    """Report block-index component analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 1: BLOCK-INDEX × COMPONENT DISTRIBUTION")
    print("=" * 70)

    # Summary table
    print("\n{:<10} {:>10} {:>12} {:>12} {:>12} {:>10}".format(
        "Block Idx", "Tokens", "Pfx Entropy", "Sfx Entropy", "Mid Entropy", "Uniq Mid"))
    print("-" * 70)

    for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
        r = results[idx]
        if r['token_count'] > 0:
            print("{:<10} {:>10} {:>12.3f} {:>12.3f} {:>12.3f} {:>10}".format(
                idx, r['token_count'],
                r['prefix_entropy'], r['suffix_entropy'], r['middle_entropy'],
                r['unique_middles']))

    # Prefix distribution by block index
    print("\n" + "-" * 50)
    print("Prefix distribution by block index:")
    print("-" * 50)

    all_prefixes = set()
    for idx in results:
        all_prefixes.update(results[idx]['prefix_counts'].keys())

    core_prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'ct', 'da']

    print("\n{:<8}".format("Prefix"), end="")
    for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
        print("{:>10}".format(idx), end="")
    print()
    print("-" * 50)

    for pf in core_prefixes:
        print("{:<8}".format(pf), end="")
        for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
            total = results[idx]['token_count']
            count = results[idx]['prefix_counts'].get(pf, 0)
            pct = 100 * count / total if total > 0 else 0
            print("{:>9.1f}%".format(pct), end="")
        print()

    # Suffix distribution by block index
    print("\n" + "-" * 50)
    print("Top suffixes by block index:")
    print("-" * 50)

    for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
        top5 = results[idx]['suffix_counts'].most_common(5)
        total = sum(results[idx]['suffix_counts'].values())
        if total > 0:
            top5_str = ", ".join(f"{s}({100*c/total:.1f}%)" for s, c in top5)
            print(f"{idx}: {top5_str}")


# =============================================================================
# ANALYSIS 2: POSITION-IN-BLOCK EFFECTS
# =============================================================================

def analyze_position_in_block(entries: List[Entry]) -> dict:
    """
    Analyze prefix/suffix enrichment by position within blocks.
    """
    results = {pos: {
        'prefix_counts': Counter(),
        'suffix_counts': Counter(),
        'token_count': 0
    } for pos in ['INITIAL', 'INTERNAL', 'FINAL', 'ONLY']}

    for entry in entries:
        for block in entry.blocks:
            for token in block.tokens:
                pos = token.position_in_block
                results[pos]['token_count'] += 1
                if token.prefix:
                    pf = token.prefix
                    if len(pf) == 3 and pf.endswith('ch'):
                        pf = 'ch'
                    elif len(pf) == 3 and pf.endswith('sh'):
                        pf = 'sh'
                    results[pos]['prefix_counts'][pf] += 1
                if token.suffix:
                    results[pos]['suffix_counts'][token.suffix] += 1

    return results


def generate_shuffled_baseline(entries: List[Entry], n_shuffles: int = 100) -> dict:
    """Generate shuffled baseline for position-in-block effects."""
    # Collect all tokens from multi-token blocks
    all_tokens = []
    block_sizes = []

    for entry in entries:
        for block in entry.blocks:
            if len(block.tokens) >= 2:
                all_tokens.extend(block.tokens)
                block_sizes.append(len(block.tokens))

    # Initialize accumulators
    shuffled_prefix_by_pos = {pos: Counter() for pos in ['INITIAL', 'INTERNAL', 'FINAL']}
    shuffled_count_by_pos = {pos: 0 for pos in ['INITIAL', 'INTERNAL', 'FINAL']}

    random.seed(42)

    for _ in range(n_shuffles):
        # Shuffle tokens
        shuffled = list(all_tokens)
        random.shuffle(shuffled)

        # Assign to positions based on block structure
        idx = 0
        for size in block_sizes:
            for j in range(size):
                if j == 0:
                    pos = 'INITIAL'
                elif j == size - 1:
                    pos = 'FINAL'
                else:
                    pos = 'INTERNAL'

                token = shuffled[idx]
                shuffled_count_by_pos[pos] += 1
                if token.prefix:
                    pf = token.prefix
                    if len(pf) == 3 and pf.endswith('ch'):
                        pf = 'ch'
                    elif len(pf) == 3 and pf.endswith('sh'):
                        pf = 'sh'
                    shuffled_prefix_by_pos[pos][pf] += 1
                idx += 1

    # Normalize
    for pos in shuffled_prefix_by_pos:
        for pf in shuffled_prefix_by_pos[pos]:
            shuffled_prefix_by_pos[pos][pf] /= n_shuffles
        shuffled_count_by_pos[pos] /= n_shuffles

    return {'prefix': shuffled_prefix_by_pos, 'counts': shuffled_count_by_pos}


def report_position_in_block(results: dict, baseline: dict):
    """Report position-in-block analysis with baseline comparison."""
    print("\n" + "=" * 70)
    print("ANALYSIS 2: POSITION-IN-BLOCK EFFECTS")
    print("=" * 70)

    print("\nToken counts by position:")
    for pos in ['INITIAL', 'INTERNAL', 'FINAL', 'ONLY']:
        print(f"  {pos}: {results[pos]['token_count']}")

    # Prefix enrichment
    print("\n" + "-" * 60)
    print("Prefix enrichment by position (vs shuffled baseline):")
    print("-" * 60)

    core_prefixes = ['ch', 'sh', 'qo', 'ok', 'ot', 'ol', 'ct']

    print("\n{:<8} {:>12} {:>12} {:>12} {:>12}".format(
        "Prefix", "INITIAL", "INTERNAL", "FINAL", "Baseline"))
    print("-" * 60)

    for pf in core_prefixes:
        print("{:<8}".format(pf), end="")
        for pos in ['INITIAL', 'INTERNAL', 'FINAL']:
            total = results[pos]['token_count']
            count = results[pos]['prefix_counts'].get(pf, 0)
            pct = 100 * count / total if total > 0 else 0

            # Compare to baseline
            baseline_count = baseline['prefix'][pos].get(pf, 0)
            baseline_total = baseline['counts'][pos]
            baseline_pct = 100 * baseline_count / baseline_total if baseline_total > 0 else 0

            delta = pct - baseline_pct
            marker = "+" if delta > 2 else ("-" if delta < -2 else " ")
            print("{:>11.1f}%{}".format(pct, marker), end="")

        # Average baseline
        avg_baseline = 0
        for pos in ['INITIAL', 'INTERNAL', 'FINAL']:
            baseline_count = baseline['prefix'][pos].get(pf, 0)
            baseline_total = baseline['counts'][pos]
            avg_baseline += 100 * baseline_count / baseline_total if baseline_total > 0 else 0
        avg_baseline /= 3
        print("{:>12.1f}%".format(avg_baseline))

    # Suffix enrichment
    print("\n" + "-" * 60)
    print("Top suffixes by position:")
    print("-" * 60)

    for pos in ['INITIAL', 'INTERNAL', 'FINAL', 'ONLY']:
        top5 = results[pos]['suffix_counts'].most_common(5)
        total = sum(results[pos]['suffix_counts'].values())
        if total > 0:
            top5_str = ", ".join(f"{s}({100*c/total:.1f}%)" for s, c in top5)
            print(f"{pos}: {top5_str}")


# =============================================================================
# ANALYSIS 3: BLOCK-TO-BLOCK SIMILARITY BY COORDINATE
# =============================================================================

def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Compute Jaccard similarity."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def get_middles_from_block(block: Block) -> Set[str]:
    """Extract set of MIDDLEs from a block."""
    middles = set()
    for token in block.tokens:
        if token.middle:
            middles.add(token.middle)
    return middles


def get_full_tokens_from_block(block: Block) -> Set[str]:
    """Extract set of full tokens from a block."""
    return {t.raw for t in block.tokens}


def analyze_block_similarity_by_coordinate(entries: List[Entry]) -> dict:
    """
    Compare blocks by their coordinate (FIRST, LAST, etc.)
    across different entries.
    """
    # Collect blocks by index
    blocks_by_index = defaultdict(list)

    for entry in entries:
        if len(entry.blocks) >= 2:  # Only multi-block entries
            for block in entry.blocks:
                blocks_by_index[block.block_index].append(block)

    # Compute within-coordinate similarity (sample for efficiency)
    within_coord_sim = {}
    random.seed(42)

    for idx in ['FIRST', 'LAST']:
        blocks = blocks_by_index[idx]
        if len(blocks) >= 2:
            # Sample pairs
            n_samples = min(500, len(blocks) * (len(blocks) - 1) // 2)
            similarities_middle = []
            similarities_full = []

            for _ in range(n_samples):
                i, j = random.sample(range(len(blocks)), 2)
                mid1 = get_middles_from_block(blocks[i])
                mid2 = get_middles_from_block(blocks[j])
                full1 = get_full_tokens_from_block(blocks[i])
                full2 = get_full_tokens_from_block(blocks[j])

                if mid1 and mid2:
                    similarities_middle.append(jaccard_similarity(mid1, mid2))
                similarities_full.append(jaccard_similarity(full1, full2))

            within_coord_sim[idx] = {
                'middle_mean': statistics.mean(similarities_middle) if similarities_middle else 0,
                'full_mean': statistics.mean(similarities_full) if similarities_full else 0,
                'n_blocks': len(blocks)
            }

    # Compute cross-coordinate similarity (FIRST vs LAST)
    first_blocks = blocks_by_index['FIRST']
    last_blocks = blocks_by_index['LAST']

    cross_sim_middle = []
    cross_sim_full = []

    n_samples = min(500, len(first_blocks) * len(last_blocks))

    for _ in range(n_samples):
        i = random.randrange(len(first_blocks))
        j = random.randrange(len(last_blocks))

        mid1 = get_middles_from_block(first_blocks[i])
        mid2 = get_middles_from_block(last_blocks[j])
        full1 = get_full_tokens_from_block(first_blocks[i])
        full2 = get_full_tokens_from_block(last_blocks[j])

        if mid1 and mid2:
            cross_sim_middle.append(jaccard_similarity(mid1, mid2))
        cross_sim_full.append(jaccard_similarity(full1, full2))

    cross_coord = {
        'middle_mean': statistics.mean(cross_sim_middle) if cross_sim_middle else 0,
        'full_mean': statistics.mean(cross_sim_full) if cross_sim_full else 0
    }

    return {'within': within_coord_sim, 'cross': cross_coord}


def report_block_similarity(results: dict):
    """Report block-to-block similarity analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 3: BLOCK-TO-BLOCK SIMILARITY BY COORDINATE")
    print("=" * 70)

    print("\nWithin-coordinate similarity (same position, different entries):")
    print("-" * 50)
    print("{:<10} {:>15} {:>15} {:>10}".format("Coord", "Middle-Jaccard", "Full-Jaccard", "N blocks"))
    print("-" * 50)

    for idx in ['FIRST', 'LAST']:
        if idx in results['within']:
            r = results['within'][idx]
            print("{:<10} {:>15.3f} {:>15.3f} {:>10}".format(
                idx, r['middle_mean'], r['full_mean'], r['n_blocks']))

    print("\nCross-coordinate similarity (FIRST vs LAST across entries):")
    print("-" * 50)
    r = results['cross']
    print(f"  Middle-Jaccard: {r['middle_mean']:.3f}")
    print(f"  Full-Jaccard: {r['full_mean']:.3f}")

    # Interpretation
    print("\n" + "-" * 50)
    print("Interpretation:")
    print("-" * 50)

    if 'FIRST' in results['within'] and 'LAST' in results['within']:
        first_sim = results['within']['FIRST']['middle_mean']
        last_sim = results['within']['LAST']['middle_mean']
        cross_sim = results['cross']['middle_mean']

        if first_sim > cross_sim and last_sim > cross_sim:
            print("  FIRST blocks share more vocabulary with other FIRST blocks")
            print("  LAST blocks share more vocabulary with other LAST blocks")
            print("  -> Domain continuity by position (soft tendency)")
        else:
            print("  No strong coordinate-based vocabulary clustering")


# =============================================================================
# ANALYSIS 4: RARE-ITEM STRUCTURAL PLACEMENT
# =============================================================================

def analyze_rare_item_placement(entries: List[Entry]) -> dict:
    """
    Test whether rare MIDDLEs cluster in specific structural positions.
    RARE = lowest-frequency decile.
    """
    # First pass: count all MIDDLEs
    middle_counts = Counter()
    total_middles = 0

    for entry in entries:
        for block in entry.blocks:
            for token in block.tokens:
                if token.middle:
                    middle_counts[token.middle] += 1
                    total_middles += 1

    if not middle_counts:
        return {'error': 'No MIDDLEs found'}

    # Define RARE as lowest 10% by frequency
    sorted_middles = sorted(middle_counts.items(), key=lambda x: x[1])
    n_rare = max(1, len(sorted_middles) // 10)
    rare_middles = {m for m, c in sorted_middles[:n_rare]}
    rare_threshold = sorted_middles[n_rare - 1][1] if n_rare > 0 else 0

    # Second pass: track rare MIDDLE placement
    placement = {
        'by_block_index': {idx: {'rare': 0, 'total': 0} for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']},
        'by_entry_complexity': {'single_block': {'rare': 0, 'total': 0},
                                'multi_block': {'rare': 0, 'total': 0}},
        'by_articulation': {'low': {'rare': 0, 'total': 0},  # 0-1 DA
                            'high': {'rare': 0, 'total': 0}}  # 2+ DA
    }

    for entry in entries:
        is_single = len(entry.blocks) == 1
        is_high_articulation = entry.da_count >= 2

        for block in entry.blocks:
            for token in block.tokens:
                if token.middle:
                    is_rare = token.middle in rare_middles

                    # Block index
                    placement['by_block_index'][block.block_index]['total'] += 1
                    if is_rare:
                        placement['by_block_index'][block.block_index]['rare'] += 1

                    # Entry complexity
                    key = 'single_block' if is_single else 'multi_block'
                    placement['by_entry_complexity'][key]['total'] += 1
                    if is_rare:
                        placement['by_entry_complexity'][key]['rare'] += 1

                    # Articulation level
                    key = 'high' if is_high_articulation else 'low'
                    placement['by_articulation'][key]['total'] += 1
                    if is_rare:
                        placement['by_articulation'][key]['rare'] += 1

    return {
        'n_unique_middles': len(middle_counts),
        'n_rare': n_rare,
        'rare_threshold': rare_threshold,
        'rare_middles_sample': list(rare_middles)[:10],
        'placement': placement
    }


def report_rare_item_placement(results: dict):
    """Report rare-item placement analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 4: RARE-ITEM STRUCTURAL PLACEMENT")
    print("=" * 70)

    if 'error' in results:
        print(f"Error: {results['error']}")
        return

    print(f"\nTotal unique MIDDLEs: {results['n_unique_middles']}")
    print(f"RARE defined as: bottom {results['n_rare']} (freq <= {results['rare_threshold']})")
    print(f"Sample rare MIDDLEs: {', '.join(results['rare_middles_sample'])}")

    placement = results['placement']

    # By block index
    print("\n" + "-" * 50)
    print("Rare MIDDLE rate by block index:")
    print("-" * 50)
    print("{:<12} {:>10} {:>10} {:>10}".format("Block Idx", "Rare", "Total", "Rate %"))
    print("-" * 50)

    for idx in ['FIRST', 'MIDDLE', 'LAST', 'ONLY']:
        r = placement['by_block_index'][idx]
        rate = 100 * r['rare'] / r['total'] if r['total'] > 0 else 0
        print("{:<12} {:>10} {:>10} {:>9.2f}%".format(idx, r['rare'], r['total'], rate))

    # By entry complexity
    print("\n" + "-" * 50)
    print("Rare MIDDLE rate by entry complexity:")
    print("-" * 50)

    for key in ['single_block', 'multi_block']:
        r = placement['by_entry_complexity'][key]
        rate = 100 * r['rare'] / r['total'] if r['total'] > 0 else 0
        print(f"  {key}: {rate:.2f}% ({r['rare']}/{r['total']})")

    # By articulation
    print("\n" + "-" * 50)
    print("Rare MIDDLE rate by articulation level:")
    print("-" * 50)

    for key in ['low', 'high']:
        r = placement['by_articulation'][key]
        rate = 100 * r['rare'] / r['total'] if r['total'] > 0 else 0
        print(f"  {key} articulation: {rate:.2f}% ({r['rare']}/{r['total']})")


# =============================================================================
# ANALYSIS 5: COMPLEXITY GRADIENT INSIDE RECORDS
# =============================================================================

def analyze_complexity_gradient(entries: List[Entry]) -> dict:
    """
    Test whether block index correlates with complexity measures.
    """
    # Only analyze multi-block entries
    multi_block = [e for e in entries if len(e.blocks) >= 2]

    metrics_by_index = {idx: {
        'token_counts': [],
        'prefix_sets': [],
        'suffix_sets': [],
        'middle_sets': []
    } for idx in ['FIRST', 'MIDDLE', 'LAST']}

    for entry in multi_block:
        for block in entry.blocks:
            idx = block.block_index
            if idx == 'ONLY':
                continue  # Skip single-block entries

            tokens = block.tokens
            metrics_by_index[idx]['token_counts'].append(len(tokens))

            prefixes = {t.prefix for t in tokens if t.prefix}
            suffixes = {t.suffix for t in tokens if t.suffix}
            middles = {t.middle for t in tokens if t.middle}

            metrics_by_index[idx]['prefix_sets'].append(len(prefixes))
            metrics_by_index[idx]['suffix_sets'].append(len(suffixes))
            metrics_by_index[idx]['middle_sets'].append(len(middles))

    # Compute statistics
    results = {}
    for idx in ['FIRST', 'MIDDLE', 'LAST']:
        m = metrics_by_index[idx]
        if m['token_counts']:
            results[idx] = {
                'mean_tokens': statistics.mean(m['token_counts']),
                'median_tokens': statistics.median(m['token_counts']),
                'mean_prefix_diversity': statistics.mean(m['prefix_sets']),
                'mean_suffix_diversity': statistics.mean(m['suffix_sets']),
                'mean_middle_diversity': statistics.mean(m['middle_sets']),
                'n_blocks': len(m['token_counts'])
            }

    return results


def report_complexity_gradient(results: dict):
    """Report complexity gradient analysis."""
    print("\n" + "=" * 70)
    print("ANALYSIS 5: COMPLEXITY GRADIENT INSIDE RECORDS")
    print("=" * 70)

    print("\n{:<10} {:>10} {:>10} {:>10} {:>10} {:>10} {:>8}".format(
        "Block", "Mean Tok", "Med Tok", "Pfx Div", "Sfx Div", "Mid Div", "N"))
    print("-" * 70)

    for idx in ['FIRST', 'MIDDLE', 'LAST']:
        if idx in results:
            r = results[idx]
            print("{:<10} {:>10.1f} {:>10.1f} {:>10.2f} {:>10.2f} {:>10.2f} {:>8}".format(
                idx, r['mean_tokens'], r['median_tokens'],
                r['mean_prefix_diversity'], r['mean_suffix_diversity'],
                r['mean_middle_diversity'], r['n_blocks']))

    # Interpretation
    print("\n" + "-" * 50)
    print("Interpretation:")
    print("-" * 50)

    if 'FIRST' in results and 'LAST' in results:
        first_size = results['FIRST']['mean_tokens']
        last_size = results['LAST']['mean_tokens']

        if first_size > last_size * 1.5:
            print("  CONFIRMED: FRONT-HEAVY structure (first block > 1.5x last)")
        elif first_size > last_size:
            print("  MODEST: First block larger than last (tendency, not rule)")
        else:
            print("  NO GRADIENT: Block sizes roughly equal")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("SECOND-WAVE RECORD GEOMETRY ANALYSIS - CURRIER A")
    print("Mode: BLOCK_SEGMENTED (DA masked as BOUNDARY)")
    print("=" * 70)

    entries = load_currier_a_entries()
    print(f"\nLoaded {len(entries)} Currier A entries")

    multi_block = [e for e in entries if len(e.blocks) >= 2]
    print(f"Multi-block entries: {len(multi_block)}")

    # Analysis 1
    block_idx_results = analyze_block_index_components(entries)
    report_block_index_components(block_idx_results)

    # Analysis 2
    pos_results = analyze_position_in_block(entries)
    baseline = generate_shuffled_baseline(entries)
    report_position_in_block(pos_results, baseline)

    # Analysis 3
    sim_results = analyze_block_similarity_by_coordinate(entries)
    report_block_similarity(sim_results)

    # Analysis 4
    rare_results = analyze_rare_item_placement(entries)
    report_rare_item_placement(rare_results)

    # Analysis 5
    gradient_results = analyze_complexity_gradient(entries)
    report_complexity_gradient(gradient_results)

    # Final summary
    print("\n" + "=" * 70)
    print("SUMMARY: RECORD GEOMETRY FINDINGS")
    print("=" * 70)

    print("""
All results are DESCRIPTIVE. No constraint modifications proposed.

Key observations:
1. Block-Index Components: [see above for entropy/diversity by position]
2. Position-in-Block: [see above for enrichment vs baseline]
3. Block Similarity: [see above for within/cross coordinate similarity]
4. Rare Items: [see above for structural placement patterns]
5. Complexity Gradient: [see above for front-heavy confirmation]

CONSTRAINT STATUS: Frozen. Findings describe USAGE, not DESIGN LIMITS.
""")


if __name__ == "__main__":
    main()

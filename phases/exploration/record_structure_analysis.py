#!/usr/bin/env python3
"""
Record Structure Analysis for Currier A

Now that DA articulation is established (C422), we can analyze record-level
structure properly for the first time.

This script examines:
1. Block-count distribution per entry
2. Block-size signatures
3. Correlation with entry length, prefix diversity, section

Research question (Tier-2 safe):
> Do Currier A entries fall into a small number of recurring record-structure
> templates defined by the number, size, and composition of DA-segmented blocks?
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import statistics

# Add apps to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "script_explorer" / "parsing"))

from currier_a import parse_currier_a_token, CurrierAParseResult


# Known DA prefixes
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}

def is_da_token(token: str) -> bool:
    """Check if token belongs to DA family."""
    result = parse_currier_a_token(token)
    if result.prefix in DA_PREFIXES:
        return True
    # Also check for daiin specifically
    if token.startswith('daiin') or token.startswith('dain'):
        return True
    return result.prefix and result.prefix.startswith('da')


@dataclass
class Block:
    """A DA-segmented block within an entry."""
    tokens: List[str]
    prefixes: List[str]
    middles: List[str]

    @property
    def size(self) -> int:
        return len(self.tokens)

    @property
    def unique_prefixes(self) -> set:
        return set(p for p in self.prefixes if p)

    @property
    def dominant_prefix(self) -> Optional[str]:
        """Most common prefix in block."""
        if not self.prefixes:
            return None
        counts = Counter(p for p in self.prefixes if p)
        if counts:
            return counts.most_common(1)[0][0]
        return None


@dataclass
class RecordStructure:
    """Complete structure of a Currier A entry."""
    entry_id: str
    folio: str
    section: str
    total_tokens: int
    da_count: int
    blocks: List[Block]
    raw_tokens: List[str]

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def block_sizes(self) -> List[int]:
        return [b.size for b in self.blocks]

    @property
    def content_tokens(self) -> int:
        """Tokens excluding DA."""
        return self.total_tokens - self.da_count

    @property
    def unique_prefixes(self) -> set:
        all_prefixes = set()
        for block in self.blocks:
            all_prefixes.update(block.unique_prefixes)
        return all_prefixes

    @property
    def prefix_diversity(self) -> int:
        return len(self.unique_prefixes)

    @property
    def block_signature(self) -> str:
        """String signature of block sizes for clustering."""
        return '-'.join(str(s) for s in self.block_sizes)


def segment_entry_by_da(tokens: List[str]) -> Tuple[List[Block], int]:
    """
    Segment an entry into blocks using DA as delimiter.
    Returns (blocks, da_count).
    """
    blocks = []
    current_block_tokens = []
    current_block_prefixes = []
    current_block_middles = []
    da_count = 0

    for token in tokens:
        if is_da_token(token):
            da_count += 1
            # If we have accumulated tokens, save as block
            if current_block_tokens:
                blocks.append(Block(
                    tokens=current_block_tokens,
                    prefixes=current_block_prefixes,
                    middles=current_block_middles
                ))
                current_block_tokens = []
                current_block_prefixes = []
                current_block_middles = []
        else:
            current_block_tokens.append(token)
            result = parse_currier_a_token(token)
            current_block_prefixes.append(result.prefix)
            current_block_middles.append(result.middle)

    # Don't forget final block
    if current_block_tokens:
        blocks.append(Block(
            tokens=current_block_tokens,
            prefixes=current_block_prefixes,
            middles=current_block_middles
        ))

    return blocks, da_count


def get_section(folio: str) -> str:
    """Get section (H/P/T) from folio ID."""
    # Simplified section mapping
    # H = Herbal (f1-f57)
    # P = Pharma (f87-f90, f99-f102)
    # T = Text (rest)
    try:
        # Extract folio number
        num_str = ''.join(c for c in folio if c.isdigit())
        if num_str:
            num = int(num_str)
            if num <= 57:
                return 'H'
            elif 87 <= num <= 102:
                return 'P'
    except:
        pass
    return 'T'


DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_currier_a_entries() -> List[Dict]:
    """Load Currier A entries from interlinear transcription."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
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
                        entries.append({
                            'id': current_entry['key'],
                            'folio': current_entry['folio'],
                            'section': current_entry['section'],
                            'tokens': current_entry['tokens']
                        })
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append({
                'id': current_entry['key'],
                'folio': current_entry['folio'],
                'section': current_entry['section'],
                'tokens': current_entry['tokens']
            })

    return entries


def analyze_record_structures(entries: List[Dict]) -> List[RecordStructure]:
    """Analyze structure of all entries."""
    structures = []

    for entry in entries:
        tokens = entry.get('tokens', [])
        if not tokens:
            continue

        folio = entry.get('folio', 'unknown')
        # Use section from data if available, otherwise derive from folio
        section = entry.get('section', get_section(folio))

        blocks, da_count = segment_entry_by_da(tokens)

        structures.append(RecordStructure(
            entry_id=entry.get('id', 'unknown'),
            folio=folio,
            section=section,
            total_tokens=len(tokens),
            da_count=da_count,
            blocks=blocks,
            raw_tokens=tokens
        ))

    return structures


def print_block_count_distribution(structures: List[RecordStructure]):
    """Analysis 1: Block count distribution."""
    print("\n" + "="*70)
    print("ANALYSIS 1: BLOCK COUNT DISTRIBUTION")
    print("="*70)

    block_counts = Counter(s.block_count for s in structures)
    total = len(structures)

    print(f"\nTotal entries analyzed: {total}")
    print("\nBlock count distribution:")
    print("-" * 40)
    print(f"{'Blocks':<10} {'Count':<10} {'%':<10} {'Cumulative %':<15}")
    print("-" * 40)

    cumulative = 0
    for blocks in sorted(block_counts.keys()):
        count = block_counts[blocks]
        pct = 100 * count / total
        cumulative += pct
        print(f"{blocks:<10} {count:<10} {pct:>6.1f}%    {cumulative:>6.1f}%")

    # Cross with entry length
    print("\n\nBlock count vs Entry length (tokens):")
    print("-" * 50)
    print(f"{'Blocks':<10} {'Mean len':<12} {'Median':<10} {'Std':<10} {'N':<8}")
    print("-" * 50)

    for blocks in sorted(block_counts.keys()):
        lengths = [s.total_tokens for s in structures if s.block_count == blocks]
        if lengths:
            mean_len = statistics.mean(lengths)
            median_len = statistics.median(lengths)
            std_len = statistics.stdev(lengths) if len(lengths) > 1 else 0
            print(f"{blocks:<10} {mean_len:<12.1f} {median_len:<10.1f} {std_len:<10.1f} {len(lengths):<8}")

    # Cross with prefix diversity
    print("\n\nBlock count vs Prefix diversity:")
    print("-" * 50)
    print(f"{'Blocks':<10} {'Mean prefixes':<15} {'Median':<10} {'N':<8}")
    print("-" * 50)

    for blocks in sorted(block_counts.keys()):
        diversities = [s.prefix_diversity for s in structures if s.block_count == blocks]
        if diversities:
            mean_div = statistics.mean(diversities)
            median_div = statistics.median(diversities)
            print(f"{blocks:<10} {mean_div:<15.2f} {median_div:<10.1f} {len(diversities):<8}")

    # Cross with section
    print("\n\nBlock count by Section:")
    print("-" * 60)

    section_blocks = defaultdict(Counter)
    for s in structures:
        section_blocks[s.section][s.block_count] += 1

    sections = sorted(section_blocks.keys())
    max_blocks = max(block_counts.keys())

    header = f"{'Section':<10}"
    for b in range(max_blocks + 1):
        header += f"{b} blk    "
    print(header)
    print("-" * 60)

    for section in sections:
        row = f"{section:<10}"
        section_total = sum(section_blocks[section].values())
        for b in range(max_blocks + 1):
            count = section_blocks[section][b]
            pct = 100 * count / section_total if section_total > 0 else 0
            row += f"{count:>3} ({pct:>4.1f}%) "
        print(row)


def print_block_size_signatures(structures: List[RecordStructure]):
    """Analysis 2: Block size signatures."""
    print("\n" + "="*70)
    print("ANALYSIS 2: BLOCK SIZE SIGNATURES")
    print("="*70)

    # Only look at entries with blocks
    multi_block = [s for s in structures if s.block_count >= 1]

    print(f"\nEntries with 1+ blocks: {len(multi_block)}")

    # Signature frequency
    signatures = Counter(s.block_signature for s in multi_block)

    print("\nTop 20 block-size signatures:")
    print("-" * 50)
    print(f"{'Signature':<25} {'Count':<10} {'%':<10}")
    print("-" * 50)

    total = len(multi_block)
    for sig, count in signatures.most_common(20):
        pct = 100 * count / total
        print(f"{sig:<25} {count:<10} {pct:>6.1f}%")

    # Analyze block size patterns
    print("\n\nBlock size statistics (for multi-block entries):")
    print("-" * 50)

    multi_blocks = [s for s in structures if s.block_count >= 2]
    if multi_blocks:
        # Size variance within entries
        variances = []
        for s in multi_blocks:
            if len(s.block_sizes) > 1:
                variances.append(statistics.variance(s.block_sizes))

        if variances:
            print(f"Mean within-entry size variance: {statistics.mean(variances):.2f}")
            print(f"Median within-entry size variance: {statistics.median(variances):.2f}")

        # Balanced vs skewed
        balanced = 0  # all blocks within 20% of mean
        skewed = 0

        for s in multi_blocks:
            sizes = s.block_sizes
            if len(sizes) > 1:
                mean_size = statistics.mean(sizes)
                if mean_size > 0:
                    deviations = [abs(sz - mean_size) / mean_size for sz in sizes]
                    if max(deviations) <= 0.3:  # 30% tolerance
                        balanced += 1
                    else:
                        skewed += 1

        print(f"\nBlock balance in multi-block entries:")
        print(f"  Balanced (within 30%): {balanced} ({100*balanced/(balanced+skewed):.1f}%)")
        print(f"  Skewed: {skewed} ({100*skewed/(balanced+skewed):.1f}%)")

    # Block size by position
    print("\n\nMean block size by position:")
    print("-" * 40)

    position_sizes = defaultdict(list)
    for s in multi_block:
        for i, size in enumerate(s.block_sizes):
            position_sizes[i].append(size)

    print(f"{'Position':<12} {'Mean size':<12} {'Median':<10} {'N':<8}")
    print("-" * 40)

    for pos in sorted(position_sizes.keys())[:5]:  # First 5 positions
        sizes = position_sizes[pos]
        mean_sz = statistics.mean(sizes)
        median_sz = statistics.median(sizes)
        print(f"{pos:<12} {mean_sz:<12.1f} {median_sz:<10.1f} {len(sizes):<8}")


def print_prefix_profile_by_position(structures: List[RecordStructure]):
    """Analysis 3: Prefix profile by block position."""
    print("\n" + "="*70)
    print("ANALYSIS 3: PREFIX PROFILE BY BLOCK POSITION")
    print("="*70)

    # Collect dominant prefix by position
    position_prefixes = defaultdict(Counter)

    for s in structures:
        for i, block in enumerate(s.blocks):
            dominant = block.dominant_prefix
            if dominant:
                position_prefixes[i][dominant] += 1

    print("\nDominant prefix distribution by block position:")
    print("-" * 70)

    # Get all prefixes
    all_prefixes = set()
    for pos_counts in position_prefixes.values():
        all_prefixes.update(pos_counts.keys())
    prefixes = sorted(all_prefixes)

    # Header
    header = f"{'Pos':<6}"
    for p in prefixes[:8]:  # Top 8 prefixes
        header += f"{p:<8}"
    print(header)
    print("-" * 70)

    for pos in sorted(position_prefixes.keys())[:5]:
        total = sum(position_prefixes[pos].values())
        row = f"{pos:<6}"
        for p in prefixes[:8]:
            count = position_prefixes[pos][p]
            pct = 100 * count / total if total > 0 else 0
            row += f"{pct:>5.1f}%  "
        print(row)

    # First block vs last block comparison
    print("\n\nFirst block vs Last block prefix comparison:")
    print("-" * 50)

    first_block_prefixes = Counter()
    last_block_prefixes = Counter()

    multi_block = [s for s in structures if s.block_count >= 2]

    for s in multi_block:
        first_dom = s.blocks[0].dominant_prefix
        last_dom = s.blocks[-1].dominant_prefix
        if first_dom:
            first_block_prefixes[first_dom] += 1
        if last_dom:
            last_block_prefixes[last_dom] += 1

    print(f"{'Prefix':<10} {'First %':<12} {'Last %':<12} {'Delta':<10}")
    print("-" * 50)

    first_total = sum(first_block_prefixes.values())
    last_total = sum(last_block_prefixes.values())

    for prefix in sorted(all_prefixes):
        first_pct = 100 * first_block_prefixes[prefix] / first_total if first_total > 0 else 0
        last_pct = 100 * last_block_prefixes[prefix] / last_total if last_total > 0 else 0
        delta = last_pct - first_pct
        if abs(delta) > 1:  # Only show meaningful differences
            print(f"{prefix:<10} {first_pct:>8.1f}%    {last_pct:>8.1f}%    {delta:>+6.1f}%")


def identify_record_templates(structures: List[RecordStructure]):
    """Attempt to identify common record templates."""
    print("\n" + "="*70)
    print("ANALYSIS 4: RECORD TEMPLATE IDENTIFICATION")
    print("="*70)

    # Define template features
    # Template = (block_count_category, size_pattern, prefix_pattern)

    templates = Counter()
    template_examples = defaultdict(list)

    for s in structures:
        # Block count category
        if s.block_count == 0:
            bc_cat = "NO_DA"
        elif s.block_count == 1:
            bc_cat = "SINGLE"
        elif s.block_count == 2:
            bc_cat = "DUAL"
        else:
            bc_cat = "MULTI"

        # Size pattern (for multi-block)
        if s.block_count >= 2:
            sizes = s.block_sizes
            mean_sz = statistics.mean(sizes)
            if mean_sz > 0:
                # Classify as balanced/first-heavy/last-heavy
                first_ratio = sizes[0] / mean_sz
                last_ratio = sizes[-1] / mean_sz

                if first_ratio > 1.3:
                    sz_pat = "FRONT_HEAVY"
                elif last_ratio > 1.3:
                    sz_pat = "BACK_HEAVY"
                elif max(sizes) / min(sizes) < 1.5:
                    sz_pat = "BALANCED"
                else:
                    sz_pat = "VARIABLE"
            else:
                sz_pat = "UNKNOWN"
        else:
            sz_pat = "NA"

        # Prefix pattern
        unique_pf = s.unique_prefixes
        if len(unique_pf) == 1:
            pf_pat = "MONO"
        elif len(unique_pf) == 2:
            pf_pat = "DUAL_PF"
        else:
            pf_pat = "POLY"

        template = (bc_cat, sz_pat, pf_pat)
        templates[template] += 1

        if len(template_examples[template]) < 3:
            template_examples[template].append(s.entry_id)

    print(f"\nIdentified {len(templates)} unique template combinations")
    print("\nTop 15 record templates:")
    print("-" * 70)
    print(f"{'Block Cat':<12} {'Size Pat':<14} {'Prefix Pat':<12} {'Count':<8} {'%':<8}")
    print("-" * 70)

    total = len(structures)
    cumulative = 0

    for template, count in templates.most_common(15):
        bc_cat, sz_pat, pf_pat = template
        pct = 100 * count / total
        cumulative += pct
        print(f"{bc_cat:<12} {sz_pat:<14} {pf_pat:<12} {count:<8} {pct:>5.1f}%")

    print("-" * 70)
    print(f"{'Top 15 coverage:':<38} {'':<8} {cumulative:>5.1f}%")

    # Show examples
    print("\n\nExample entries for top templates:")
    print("-" * 50)

    for template, count in templates.most_common(5):
        bc_cat, sz_pat, pf_pat = template
        examples = template_examples[template][:3]
        print(f"\n{bc_cat}/{sz_pat}/{pf_pat} ({count} entries):")
        for ex in examples:
            print(f"  - {ex}")


def main():
    print("="*70)
    print("CURRIER A RECORD STRUCTURE ANALYSIS")
    print("="*70)
    print("\nLoading Currier A entries...")

    entries = load_currier_a_entries()

    if not entries:
        print("ERROR: No entries found!")
        return

    print(f"Loaded {len(entries)} entries")

    print("\nAnalyzing record structures...")
    structures = analyze_record_structures(entries)
    print(f"Analyzed {len(structures)} records")

    # Run analyses
    print_block_count_distribution(structures)
    print_block_size_signatures(structures)
    print_prefix_profile_by_position(structures)
    identify_record_templates(structures)

    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)

    with_da = sum(1 for s in structures if s.da_count > 0)
    without_da = len(structures) - with_da

    print(f"\nEntries with DA: {with_da} ({100*with_da/len(structures):.1f}%)")
    print(f"Entries without DA: {without_da} ({100*without_da/len(structures):.1f}%)")

    avg_blocks = statistics.mean(s.block_count for s in structures)
    avg_tokens = statistics.mean(s.total_tokens for s in structures)
    avg_content = statistics.mean(s.content_tokens for s in structures)

    print(f"\nMean blocks per entry: {avg_blocks:.2f}")
    print(f"Mean tokens per entry: {avg_tokens:.1f}")
    print(f"Mean content tokens (excl DA): {avg_content:.1f}")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

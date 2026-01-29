#!/usr/bin/env python3
"""
Test B paragraph HT linker behavior - parallel to A's RI linker mechanism (C835-C838).

In Currier A:
- RI tokens concentrate in paragraph INITIAL (first line) and FINAL (last line) positions
- ~0.6% of RI appear in both positions, creating "linkers"
- Linkers have ct-ho morphological signature
- Creates convergent network between paragraphs

Test if B has a parallel mechanism using HT tokens.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# Load the 479-type classified grammar to identify HT tokens
CLASS_TOKEN_MAP_PATH = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'


def load_classified_tokens():
    """Load the set of tokens that are part of the 49-class grammar."""
    with open(CLASS_TOKEN_MAP_PATH) as f:
        data = json.load(f)
    return set(data['token_to_class'].keys())


def is_ht_token(word: str, classified: set) -> bool:
    """Check if a token is HT (unclassified) - not in the 49-class grammar."""
    return word not in classified


def main():
    print("=" * 80)
    print("B PARAGRAPH HT LINKER TEST")
    print("Testing whether B has linking mechanism through HT tokens")
    print("=" * 80)

    # Load transcript and classified tokens
    tx = Transcript()
    morph = Morphology()
    classified_tokens = load_classified_tokens()

    print(f"\nLoaded {len(classified_tokens)} classified token types from 49-class grammar")

    # Build paragraph structure for B
    # A paragraph is identified by: tokens on lines between par_initial=True markers
    # For each paragraph, identify INITIAL (first line) and FINAL (last line) tokens

    # Step 1: Group tokens by folio and line, tracking paragraph membership
    folio_data = defaultdict(lambda: defaultdict(list))  # folio -> line -> tokens

    for token in tx.currier_b():
        if not token.word or '*' in token.word:
            continue
        folio_data[token.folio][token.line].append(token)

    # Step 2: Identify paragraphs and their INITIAL/FINAL positions
    # Track HT tokens by position
    ht_initial_tokens = defaultdict(list)  # word -> [(folio, para_idx)]
    ht_final_tokens = defaultdict(list)    # word -> [(folio, para_idx)]
    ht_all_tokens = defaultdict(list)      # word -> [(folio, para_idx, position)]

    all_ht_tokens = set()
    total_paragraphs = 0
    total_ht_initial = 0
    total_ht_final = 0

    for folio, lines in sorted(folio_data.items()):
        # Sort lines numerically
        sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

        # Find paragraph boundaries (lines with par_initial=True)
        current_para_lines = []
        para_idx = 0

        for line in sorted_lines:
            tokens = lines[line]
            has_par_initial = any(t.par_initial for t in tokens)

            if has_par_initial and current_para_lines:
                # Process previous paragraph
                total_paragraphs += 1
                para_idx += 1

                # Get INITIAL line (first line of paragraph)
                initial_line = current_para_lines[0]
                # Get FINAL line (last line of paragraph)
                final_line = current_para_lines[-1]

                # Extract HT tokens from INITIAL and FINAL
                for t in lines[initial_line]:
                    if is_ht_token(t.word, classified_tokens):
                        ht_initial_tokens[t.word].append((folio, para_idx))
                        ht_all_tokens[t.word].append((folio, para_idx, 'INITIAL'))
                        all_ht_tokens.add(t.word)
                        total_ht_initial += 1

                # If paragraph has multiple lines, also get FINAL
                if len(current_para_lines) > 1:
                    for t in lines[final_line]:
                        if is_ht_token(t.word, classified_tokens):
                            ht_final_tokens[t.word].append((folio, para_idx))
                            ht_all_tokens[t.word].append((folio, para_idx, 'FINAL'))
                            all_ht_tokens.add(t.word)
                            total_ht_final += 1

                current_para_lines = [line]
            else:
                current_para_lines.append(line)

        # Process last paragraph
        if current_para_lines:
            total_paragraphs += 1
            para_idx += 1

            initial_line = current_para_lines[0]
            final_line = current_para_lines[-1]

            for t in lines[initial_line]:
                if is_ht_token(t.word, classified_tokens):
                    ht_initial_tokens[t.word].append((folio, para_idx))
                    ht_all_tokens[t.word].append((folio, para_idx, 'INITIAL'))
                    all_ht_tokens.add(t.word)
                    total_ht_initial += 1

            if len(current_para_lines) > 1:
                for t in lines[final_line]:
                    if is_ht_token(t.word, classified_tokens):
                        ht_final_tokens[t.word].append((folio, para_idx))
                        ht_all_tokens[t.word].append((folio, para_idx, 'FINAL'))
                        all_ht_tokens.add(t.word)
                        total_ht_final += 1

    print(f"\n{'='*80}")
    print("PARAGRAPH COUNTS")
    print(f"{'='*80}")
    print(f"Total B paragraphs: {total_paragraphs}")
    print(f"Total HT tokens in INITIAL position: {total_ht_initial}")
    print(f"Total HT tokens in FINAL position: {total_ht_final}")
    print(f"Unique HT token types in positions: {len(all_ht_tokens)}")

    # Step 3: Categorize HT tokens by positional behavior
    initial_only = set()
    final_only = set()
    both_positions = set()

    for word in all_ht_tokens:
        in_initial = word in ht_initial_tokens and len(ht_initial_tokens[word]) > 0
        in_final = word in ht_final_tokens and len(ht_final_tokens[word]) > 0

        if in_initial and in_final:
            both_positions.add(word)
        elif in_initial:
            initial_only.add(word)
        elif in_final:
            final_only.add(word)

    print(f"\n{'='*80}")
    print("HT POSITIONAL CATEGORIES")
    print(f"{'='*80}")
    print(f"INITIAL-only types: {len(initial_only)} ({100*len(initial_only)/len(all_ht_tokens):.1f}%)")
    print(f"FINAL-only types: {len(final_only)} ({100*len(final_only)/len(all_ht_tokens):.1f}%)")
    print(f"BOTH positions (potential linkers): {len(both_positions)} ({100*len(both_positions)/len(all_ht_tokens):.1f}%)")

    # Step 4: Analyze singleton vs repeater structure
    # Count occurrences of each HT token in positional contexts
    ht_position_counts = {}
    for word in all_ht_tokens:
        initial_ct = len(ht_initial_tokens.get(word, []))
        final_ct = len(ht_final_tokens.get(word, []))
        total = initial_ct + final_ct
        ht_position_counts[word] = {
            'initial': initial_ct,
            'final': final_ct,
            'total': total
        }

    singletons = [w for w, c in ht_position_counts.items() if c['total'] == 1]
    repeaters = [w for w, c in ht_position_counts.items() if c['total'] > 1]

    print(f"\n{'='*80}")
    print("HT REPETITION STRUCTURE (in INITIAL/FINAL positions)")
    print(f"{'='*80}")
    print(f"Singletons (1 occurrence): {len(singletons)} ({100*len(singletons)/len(all_ht_tokens):.1f}%)")
    print(f"Repeaters (2+ occurrences): {len(repeaters)} ({100*len(repeaters)/len(all_ht_tokens):.1f}%)")

    # Step 5: Detailed analysis of potential linkers
    print(f"\n{'='*80}")
    print("POTENTIAL LINKER ANALYSIS")
    print(f"{'='*80}")

    if both_positions:
        print(f"\nHT tokens appearing in BOTH INITIAL and FINAL positions ({len(both_positions)} types):\n")

        linker_details = []
        for word in sorted(both_positions):
            initial_locs = ht_initial_tokens[word]
            final_locs = ht_final_tokens[word]

            # Morphological analysis
            m = morph.extract(word)

            # Compute link potential
            # A link is FINAL in para X -> INITIAL in para Y
            initial_folios = set(f for f, p in initial_locs)
            final_folios = set(f for f, p in final_locs)

            linker_details.append({
                'word': word,
                'initial_count': len(initial_locs),
                'final_count': len(final_locs),
                'initial_folios': len(initial_folios),
                'final_folios': len(final_folios),
                'prefix': m.prefix,
                'middle': m.middle,
                'suffix': m.suffix
            })

        # Sort by total occurrences
        linker_details.sort(key=lambda x: -(x['initial_count'] + x['final_count']))

        print(f"{'Token':<20} {'INIT':<6} {'FINAL':<6} {'PREFIX':<8} {'MIDDLE':<12} {'SUFFIX':<8}")
        print("-" * 70)
        for d in linker_details[:30]:  # Show top 30
            print(f"{d['word']:<20} {d['initial_count']:<6} {d['final_count']:<6} "
                  f"{str(d['prefix']):<8} {str(d['middle']):<12} {str(d['suffix']):<8}")

        if len(linker_details) > 30:
            print(f"... and {len(linker_details) - 30} more")

        # Morphological profile of linkers
        print(f"\n{'='*80}")
        print("LINKER MORPHOLOGICAL PROFILE")
        print(f"{'='*80}")

        prefix_counts = Counter(d['prefix'] for d in linker_details)
        middle_counts = Counter(d['middle'] for d in linker_details)
        suffix_counts = Counter(d['suffix'] for d in linker_details)

        print("\nPREFIX distribution:")
        for p, c in prefix_counts.most_common(10):
            print(f"  {str(p):<10}: {c} ({100*c/len(linker_details):.1f}%)")

        print("\nMIDDLE distribution:")
        for m, c in middle_counts.most_common(10):
            print(f"  {str(m):<10}: {c} ({100*c/len(linker_details):.1f}%)")

        print("\nSUFFIX distribution:")
        for s, c in suffix_counts.most_common(10):
            print(f"  {str(s):<10}: {c} ({100*c/len(linker_details):.1f}%)")

        # Check for ct-ho signature (like A's linkers)
        ct_ho_count = sum(1 for d in linker_details
                         if d['prefix'] == 'ct' and d['middle'] and 'h' in d['middle'])
        print(f"\nct-prefix with h-MIDDLE (A's signature): {ct_ho_count} ({100*ct_ho_count/len(linker_details):.1f}%)")

    else:
        print("\nNo HT tokens appear in both INITIAL and FINAL positions.")
        print("This suggests B does NOT have an A-style linker mechanism.")

    # Step 6: Network analysis if linkers exist
    if len(both_positions) >= 4:
        print(f"\n{'='*80}")
        print("NETWORK ANALYSIS")
        print(f"{'='*80}")

        # For each linker, compute links
        links = []
        for word in both_positions:
            final_locs = ht_final_tokens[word]
            initial_locs = ht_initial_tokens[word]

            # Each FINAL location creates potential links to each INITIAL location
            for final_folio, final_para in final_locs:
                for init_folio, init_para in initial_locs:
                    # Skip self-links within same paragraph
                    if final_folio == init_folio and final_para == init_para:
                        continue
                    links.append({
                        'word': word,
                        'from_folio': final_folio,
                        'from_para': final_para,
                        'to_folio': init_folio,
                        'to_para': init_para
                    })

        print(f"\nTotal potential links: {len(links)}")

        # Analyze link topology
        within_folio = sum(1 for l in links if l['from_folio'] == l['to_folio'])
        cross_folio = len(links) - within_folio
        print(f"Within-folio links: {within_folio} ({100*within_folio/len(links):.1f}%)")
        print(f"Cross-folio links: {cross_folio} ({100*cross_folio/len(links):.1f}%)")

        # Link direction (forward vs backward in folio order)
        folio_order = sorted(folio_data.keys())
        folio_rank = {f: i for i, f in enumerate(folio_order)}

        forward = sum(1 for l in links
                     if folio_rank.get(l['to_folio'], 0) > folio_rank.get(l['from_folio'], 0))
        backward = sum(1 for l in links
                      if folio_rank.get(l['to_folio'], 0) < folio_rank.get(l['from_folio'], 0))
        same = len(links) - forward - backward

        print(f"\nLink direction (by folio order):")
        print(f"  Forward: {forward} ({100*forward/len(links):.1f}%)")
        print(f"  Backward: {backward} ({100*backward/len(links):.1f}%)")
        print(f"  Same folio: {same} ({100*same/len(links):.1f}%)")

    # Step 7: Comparison to A's structure
    print(f"\n{'='*80}")
    print("COMPARISON TO CURRIER A (C835-C838)")
    print(f"{'='*80}")
    print("""
Currier A RI structure (from C831):
- Singletons: 95.3% (674 types)
- Position-locked: ~4% (29 types)
- Linkers: 0.6% (4 types)
- Linker signature: ct-prefix + ho/heo MIDDLE (75%)

Currier B HT structure:
""")

    if all_ht_tokens:
        print(f"- Singletons: {100*len(singletons)/len(all_ht_tokens):.1f}% ({len(singletons)} types)")
        position_locked = len(initial_only) + len(final_only) - len(singletons)
        print(f"- Linkers (both positions): {100*len(both_positions)/len(all_ht_tokens):.1f}% ({len(both_positions)} types)")

        if both_positions:
            ct_count = sum(1 for w in both_positions if morph.extract(w).prefix == 'ct')
            print(f"- ct-prefix linkers: {ct_count} ({100*ct_count/len(both_positions):.1f}%)")

    # Step 8: Save results
    results = {
        'total_paragraphs': total_paragraphs,
        'total_ht_initial': total_ht_initial,
        'total_ht_final': total_ht_final,
        'unique_ht_types': len(all_ht_tokens),
        'initial_only_count': len(initial_only),
        'final_only_count': len(final_only),
        'both_positions_count': len(both_positions),
        'singleton_count': len(singletons),
        'repeater_count': len(repeaters),
        'linker_tokens': list(both_positions)[:50],
        'has_linking_mechanism': len(both_positions) >= 4  # Threshold: at least as many as A
    }

    output_path = Path(__file__).parent.parent / 'results' / 'b_ht_linker_test.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Final verdict
    print(f"\n{'='*80}")
    print("VERDICT")
    print(f"{'='*80}")

    if len(both_positions) >= 4:
        linker_rate = 100*len(both_positions)/len(all_ht_tokens)
        if linker_rate < 2:
            print(f"""
B shows WEAK linking behavior:
- {len(both_positions)} HT types appear in both INITIAL and FINAL positions
- Linker rate: {linker_rate:.2f}% (vs A's 0.6%)
- This suggests B MAY have a parallel linking mechanism, but weaker than A's
""")
        else:
            print(f"""
B shows DIFFERENT behavior from A:
- {len(both_positions)} HT types appear in both positions ({linker_rate:.1f}%)
- Much higher than A's 0.6% linker rate
- This suggests B's HT tokens have less positional specialization than A's RI
- May indicate a different structural function for HT in B
""")
    else:
        print(f"""
B does NOT show A-style linking behavior:
- Only {len(both_positions)} HT types appear in both INITIAL and FINAL positions
- A has 4 linker tokens with specific ct-ho signature
- B's HT population appears to lack this positional bridging function
""")


if __name__ == '__main__':
    main()

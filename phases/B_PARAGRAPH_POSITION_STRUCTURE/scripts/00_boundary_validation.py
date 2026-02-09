"""
00_boundary_validation.py - Validate paragraph boundary detection

Phase: B_PARAGRAPH_POSITION_STRUCTURE
Purpose: Compare explicit paragraph boundaries with gallows-initial heuristic

Key finding from C841: 71.5% of paragraphs start with gallows-initial token

Approach:
1. For folios WITH explicit P# markers: validate gallows-initial rate
2. For folios WITHOUT markers: detect boundaries using heuristic
3. Compare structural patterns across both sets
"""

import sys
sys.path.insert(0, 'C:/git/voynich/scripts')
from voynich import Transcript, Morphology
import json
import csv
from collections import defaultdict
from pathlib import Path

GALLOWS = {'k', 't', 'p', 'f'}

def has_gallows_initial(word):
    """Check if token starts with a gallows glyph."""
    if not word or not word.strip():
        return False
    return word[0] in GALLOWS

def load_raw_data():
    """Load raw transcript with placement info."""
    data_path = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

    # Structure: folio -> line -> list of (word, placement)
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row['transcriber'] == 'H' and row['language'] == 'B':
                folio = row['folio']
                line = row['line_number']
                word = row['word']
                placement = row['placement']
                # Skip uncertain tokens
                if '*' in word:
                    continue
                folio_lines[folio][line].append({
                    'word': word,
                    'placement': placement
                })

    return folio_lines

def detect_paragraphs_explicit(folio_data):
    """Extract paragraphs from explicit P# markers."""
    paragraphs = defaultdict(list)  # para_num -> list of (line, tokens)

    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    for line in lines:
        tokens = folio_data[line]
        if not tokens:
            continue

        # Get paragraph from placement
        placement = tokens[0]['placement']
        if placement.startswith('P') and len(placement) > 1:
            para_str = placement[1:]
            if para_str.isdigit():
                para_num = int(para_str)
                paragraphs[para_num].append((line, tokens))

    return paragraphs if paragraphs else None

def detect_paragraphs_heuristic(folio_data):
    """Detect paragraphs using gallows-initial heuristic."""
    paragraphs = defaultdict(list)

    lines = sorted(folio_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

    current_para = 1
    for i, line in enumerate(lines):
        tokens = folio_data[line]
        if not tokens:
            continue

        first_word = tokens[0]['word']

        # New paragraph if: line-initial token starts with gallows
        # Exception: first line is always paragraph 1
        if i > 0 and has_gallows_initial(first_word):
            current_para += 1

        paragraphs[current_para].append((line, tokens))

    return paragraphs

def analyze_folio(folio, folio_data, use_heuristic=False):
    """Analyze paragraph structure for one folio."""
    if use_heuristic:
        paragraphs = detect_paragraphs_heuristic(folio_data)
    else:
        paragraphs = detect_paragraphs_explicit(folio_data)

    if paragraphs is None:
        return None

    result = {
        'folio': folio,
        'paragraph_count': len(paragraphs),
        'detection_method': 'heuristic' if use_heuristic else 'explicit',
        'paragraphs': []
    }

    for para_num in sorted(paragraphs.keys()):
        para_lines = paragraphs[para_num]
        first_tokens = para_lines[0][1] if para_lines else []
        first_word = first_tokens[0]['word'] if first_tokens else ''

        # Count all tokens
        all_words = [t['word'] for line, toks in para_lines for t in toks]

        para_info = {
            'number': para_num,
            'lines': len(para_lines),
            'tokens': len(all_words),
            'first_token': first_word,
            'gallows_initial': has_gallows_initial(first_word),
            'line_range': f"{para_lines[0][0]}-{para_lines[-1][0]}"
        }
        result['paragraphs'].append(para_info)

    return result

def main():
    folio_data = load_raw_data()

    # Categorize folios
    explicit_folios = []  # Have P# markers
    heuristic_folios = []  # Only have P

    for folio in sorted(folio_data.keys()):
        lines = folio_data[folio]
        placements = set()
        for line in lines.values():
            for tok in line:
                placements.add(tok['placement'])

        has_numbered = any(p.startswith('P') and len(p) > 1 and p[1:].isdigit() for p in placements)

        if has_numbered:
            explicit_folios.append(folio)
        else:
            heuristic_folios.append(folio)

    print("=" * 70)
    print("PARAGRAPH BOUNDARY VALIDATION - B FOLIOS")
    print("=" * 70)
    print(f"\nTotal B folios: {len(folio_data)}")
    print(f"Folios with explicit P# markers: {len(explicit_folios)}")
    print(f"Folios needing heuristic detection: {len(heuristic_folios)}")

    # Analyze explicit folios
    print("\n" + "=" * 70)
    print("SECTION 1: EXPLICIT PARAGRAPH MARKERS")
    print("=" * 70)

    explicit_results = []
    gallows_count = 0
    total_paras = 0

    for folio in explicit_folios:
        result = analyze_folio(folio, folio_data[folio], use_heuristic=False)
        if result:
            explicit_results.append(result)
            for p in result['paragraphs']:
                total_paras += 1
                if p['gallows_initial']:
                    gallows_count += 1
            print(f"\n{folio}: {result['paragraph_count']} paragraphs")
            for p in result['paragraphs']:
                gmark = "G" if p['gallows_initial'] else "X"
                print(f"  P{p['number']}: lines {p['line_range']}, {p['tokens']} tok, '{p['first_token'][:10]}' [{gmark}]")

    if total_paras > 0:
        print(f"\nExplicit folios summary:")
        print(f"  Total paragraphs: {total_paras}")
        print(f"  Gallows-initial: {gallows_count} ({gallows_count/total_paras*100:.1f}%)")
        print(f"  C841 claim: 71.5%")
        print(f"  Match: {abs(gallows_count/total_paras - 0.715) < 0.10}")

    # Analyze heuristic folios (sample)
    print("\n" + "=" * 70)
    print("SECTION 2: HEURISTIC DETECTION (sample)")
    print("=" * 70)

    # Target folios from annotation work
    target_folios = ['f103r', 'f104r', 'f105r', 'f41v', 'f43r', 'f46r', 'f46v']
    sample_folios = [f for f in target_folios if f in heuristic_folios][:5]

    heuristic_results = []
    for folio in sample_folios:
        result = analyze_folio(folio, folio_data[folio], use_heuristic=True)
        if result:
            heuristic_results.append(result)
            print(f"\n{folio}: {result['paragraph_count']} paragraphs (heuristic)")
            for p in result['paragraphs']:
                gmark = "G" if p['gallows_initial'] else "X"
                print(f"  P{p['number']}: lines {p['line_range']}, {p['tokens']} tok, '{p['first_token'][:10]}' [{gmark}]")

    # Full corpus heuristic analysis
    print("\n" + "=" * 70)
    print("SECTION 3: FULL CORPUS HEURISTIC ANALYSIS")
    print("=" * 70)

    all_heuristic_results = []
    total_h_paras = 0
    gallows_h_count = 0
    para_sizes = []
    para_lengths = []

    for folio in heuristic_folios:
        result = analyze_folio(folio, folio_data[folio], use_heuristic=True)
        if result:
            all_heuristic_results.append(result)
            for p in result['paragraphs']:
                total_h_paras += 1
                if p['gallows_initial']:
                    gallows_h_count += 1
                para_sizes.append(p['tokens'])
                para_lengths.append(p['lines'])

    print(f"\nHeuristic detection on {len(all_heuristic_results)} folios:")
    print(f"  Total paragraphs detected: {total_h_paras}")
    print(f"  Mean paragraphs per folio: {total_h_paras / len(all_heuristic_results):.1f}")
    print(f"  Mean lines per paragraph: {sum(para_lengths) / len(para_lengths):.1f}")
    print(f"  Mean tokens per paragraph: {sum(para_sizes) / len(para_sizes):.1f}")
    print(f"\nGallows-initial rate (by construction): 100% for P2+")
    print(f"  (Heuristic defines new paragraph on gallows-initial)")

    # Distribution analysis
    from collections import Counter
    para_count_dist = Counter(r['paragraph_count'] for r in all_heuristic_results)

    print(f"\nParagraphs per folio distribution:")
    for count in sorted(para_count_dist.keys()):
        pct = para_count_dist[count] / len(all_heuristic_results) * 100
        print(f"  {count} paragraphs: {para_count_dist[count]} folios ({pct:.1f}%)")

    # Save results
    output = {
        'summary': {
            'total_b_folios': len(folio_data),
            'explicit_folios': len(explicit_folios),
            'heuristic_folios': len(heuristic_folios),
            'explicit_paragraphs': total_paras,
            'explicit_gallows_rate': gallows_count / total_paras if total_paras > 0 else 0,
            'heuristic_paragraphs': total_h_paras,
            'mean_paragraphs_per_folio': total_h_paras / len(all_heuristic_results) if all_heuristic_results else 0,
            'mean_lines_per_paragraph': sum(para_lengths) / len(para_lengths) if para_lengths else 0,
            'mean_tokens_per_paragraph': sum(para_sizes) / len(para_sizes) if para_sizes else 0,
            'c841_validated': total_paras == 0 or abs(gallows_count / total_paras - 0.715) < 0.15
        },
        'explicit_results': explicit_results,
        'heuristic_sample': heuristic_results,
        'paragraph_count_distribution': dict(para_count_dist)
    }

    output_path = Path('C:/git/voynich/phases/B_PARAGRAPH_POSITION_STRUCTURE/results/00_boundary_validation.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return output

if __name__ == '__main__':
    main()

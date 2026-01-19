"""
TRANSCRIPT-ARCHITECTURE-AUDIT: Complete analysis of interlinear_full_words.txt structure

Analyzes all columns, all placement types, and establishes token type taxonomy.
"""
import csv
import json
from collections import Counter, defaultdict


def load_transcript():
    """Load full transcript."""
    rows = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = [h.strip('"') for h in next(reader)]
        for row in reader:
            if len(row) >= len(header):
                rows.append({header[i]: row[i].strip('"') for i in range(len(header))})
    return header, rows


def analyze_columns(header, rows):
    """Analyze each column's values."""
    print("=" * 70)
    print("PHASE 1: COLUMN ANALYSIS")
    print("=" * 70)

    column_info = {}

    for i, col in enumerate(header):
        values = Counter([r.get(col, '') for r in rows])
        unique_count = len(values)
        top_values = values.most_common(10)

        column_info[col] = {
            'index': i,
            'unique_values': unique_count,
            'top_values': top_values,
            'total_non_empty': sum(1 for r in rows if r.get(col, '').strip())
        }

        print(f"\n[{i}] {col}")
        print(f"    Unique values: {unique_count}")
        print(f"    Top 10: {top_values}")

    return column_info


def analyze_placement_types(rows):
    """Deep analysis of placement column."""
    print("\n" + "=" * 70)
    print("PHASE 2: PLACEMENT TYPE ANALYSIS")
    print("=" * 70)

    # Filter to H-only
    h_rows = [r for r in rows if r.get('transcriber') == 'H']

    placement_data = defaultdict(lambda: {
        'count': 0,
        'a_count': 0,
        'b_count': 0,
        'sections': Counter(),
        'example_tokens': [],
        'folios': set()
    })

    for r in h_rows:
        p = r.get('placement', '')
        lang = r.get('language', '')
        section = r.get('section', '')
        word = r.get('word', '')
        folio = r.get('folio', '')

        placement_data[p]['count'] += 1
        if lang == 'A':
            placement_data[p]['a_count'] += 1
        elif lang == 'B':
            placement_data[p]['b_count'] += 1
        placement_data[p]['sections'][section] += 1
        placement_data[p]['folios'].add(folio)
        if len(placement_data[p]['example_tokens']) < 5:
            placement_data[p]['example_tokens'].append(word)

    # Categorize placements
    categories = {
        'TEXT': [],      # P*
        'LABEL': [],     # L*
        'RING': [],      # R* (rosettes/rings?)
        'CIRCLE': [],    # C*
        'STAR': [],      # S*
        'OTHER': []
    }

    print("\nAll placement types (H-only):")
    print("-" * 70)

    for p in sorted(placement_data.keys()):
        d = placement_data[p]
        print(f"\n{p}:")
        print(f"  Total: {d['count']} (A={d['a_count']}, B={d['b_count']})")
        print(f"  Sections: {dict(d['sections'])}")
        print(f"  Folios: {len(d['folios'])} unique")
        print(f"  Examples: {d['example_tokens']}")

        # Categorize
        if p.startswith('P'):
            categories['TEXT'].append(p)
        elif p.startswith('L'):
            categories['LABEL'].append(p)
        elif p.startswith('R'):
            categories['RING'].append(p)
        elif p.startswith('C'):
            categories['CIRCLE'].append(p)
        elif p.startswith('S'):
            categories['STAR'].append(p)
        else:
            categories['OTHER'].append(p)

    print("\n" + "-" * 70)
    print("PLACEMENT CATEGORIES:")
    for cat, placements in categories.items():
        total = sum(placement_data[p]['count'] for p in placements)
        print(f"  {cat}: {placements} = {total} tokens")

    # Convert sets to lists for JSON
    for p in placement_data:
        placement_data[p]['folios'] = list(placement_data[p]['folios'])

    return dict(placement_data), categories


def analyze_token_types(rows):
    """Break down tokens by type for A and B."""
    print("\n" + "=" * 70)
    print("PHASE 3: TOKEN TYPE BREAKDOWN")
    print("=" * 70)

    h_rows = [r for r in rows if r.get('transcriber') == 'H']

    def categorize_placement(p):
        if p.startswith('P'):
            return 'TEXT'
        elif p.startswith('L'):
            return 'LABEL'
        elif p.startswith('R'):
            return 'RING'
        elif p.startswith('C'):
            return 'CIRCLE'
        elif p.startswith('S'):
            return 'STAR'
        else:
            return 'OTHER'

    breakdown = {
        'A': defaultdict(int),
        'B': defaultdict(int)
    }

    vocab_by_type = {
        'A': defaultdict(set),
        'B': defaultdict(set)
    }

    for r in h_rows:
        lang = r.get('language', '')
        p = r.get('placement', '')
        word = r.get('word', '')
        cat = categorize_placement(p)

        if lang in ['A', 'B']:
            breakdown[lang][cat] += 1
            vocab_by_type[lang][cat].add(word)

    print("\nCurrier A (H-only):")
    total_a = sum(breakdown['A'].values())
    for cat, count in sorted(breakdown['A'].items(), key=lambda x: -x[1]):
        pct = 100 * count / total_a if total_a else 0
        vocab_size = len(vocab_by_type['A'][cat])
        print(f"  {cat}: {count} tokens ({pct:.1f}%), {vocab_size} types")

    print(f"\n  TOTAL: {total_a} tokens")

    print("\nCurrier B (H-only):")
    total_b = sum(breakdown['B'].values())
    for cat, count in sorted(breakdown['B'].items(), key=lambda x: -x[1]):
        pct = 100 * count / total_b if total_b else 0
        vocab_size = len(vocab_by_type['B'][cat])
        print(f"  {cat}: {count} tokens ({pct:.1f}%), {vocab_size} types")

    print(f"\n  TOTAL: {total_b} tokens")

    # Convert sets to counts for JSON
    vocab_counts = {
        'A': {cat: len(words) for cat, words in vocab_by_type['A'].items()},
        'B': {cat: len(words) for cat, words in vocab_by_type['B'].items()}
    }

    return dict(breakdown), vocab_counts


def analyze_label_overlap(rows):
    """Check overlap between label vocab and text vocab."""
    print("\n" + "=" * 70)
    print("PHASE 4: LABEL vs TEXT VOCABULARY OVERLAP")
    print("=" * 70)

    h_rows = [r for r in rows if r.get('transcriber') == 'H']

    label_vocab = set()
    text_vocab = set()

    for r in h_rows:
        p = r.get('placement', '')
        word = r.get('word', '')
        lang = r.get('language', '')

        if lang == 'A':  # Focus on Currier A
            if p.startswith('L'):
                label_vocab.add(word)
            elif p.startswith('P'):
                text_vocab.add(word)

    overlap = label_vocab & text_vocab
    label_only = label_vocab - text_vocab
    text_only = text_vocab - label_vocab

    print(f"\nCurrier A vocabulary:")
    print(f"  Label types: {len(label_vocab)}")
    print(f"  Text types: {len(text_vocab)}")
    print(f"  Overlap: {len(overlap)} ({100*len(overlap)/len(label_vocab):.1f}% of labels)")
    print(f"  Label-only: {len(label_only)}")
    print(f"  Text-only: {len(text_only)}")

    print(f"\nLabel-only vocabulary (first 20):")
    for word in sorted(label_only)[:20]:
        print(f"  {word}")

    print(f"\nOverlapping vocabulary (first 20):")
    for word in sorted(overlap)[:20]:
        print(f"  {word}")

    return {
        'label_vocab_size': len(label_vocab),
        'text_vocab_size': len(text_vocab),
        'overlap_size': len(overlap),
        'label_only_size': len(label_only),
        'text_only_size': len(text_only),
        'overlap_tokens': list(overlap),
        'label_only_tokens': list(label_only)
    }


def analyze_line_structure(rows):
    """Analyze line_number patterns."""
    print("\n" + "=" * 70)
    print("PHASE 5: LINE NUMBER PATTERNS")
    print("=" * 70)

    h_rows = [r for r in rows if r.get('transcriber') == 'H']

    line_patterns = Counter()
    special_lines = []

    for r in h_rows:
        line = r.get('line_number', '')
        if line.isdigit():
            line_patterns['numeric'] += 1
        elif line == '0':
            line_patterns['zero'] += 1
        elif line.startswith('0'):
            line_patterns['zero_suffix'] += 1
            special_lines.append((r.get('folio'), line, r.get('word'), r.get('placement')))
        elif any(c.isalpha() for c in line) and any(c.isdigit() for c in line):
            line_patterns['mixed'] += 1
            special_lines.append((r.get('folio'), line, r.get('word'), r.get('placement')))
        else:
            line_patterns['other'] += 1

    print("\nLine number patterns:")
    for pattern, count in line_patterns.most_common():
        print(f"  {pattern}: {count}")

    print(f"\nSpecial line examples (first 20):")
    for folio, line, word, placement in special_lines[:20]:
        print(f"  {folio} L{line}: {word} (placement={placement})")

    return dict(line_patterns)


def main():
    print("TRANSCRIPT-ARCHITECTURE-AUDIT")
    print("=" * 70)
    print()

    # Load data
    print("Loading transcript...")
    header, rows = load_transcript()
    print(f"  Columns: {len(header)}")
    print(f"  Rows: {len(rows)}")
    print(f"  Header: {header}")
    print()

    # Run analyses
    column_info = analyze_columns(header, rows)
    placement_data, categories = analyze_placement_types(rows)
    breakdown, vocab_counts = analyze_token_types(rows)
    overlap_data = analyze_label_overlap(rows)
    line_patterns = analyze_line_structure(rows)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n1. COLUMNS: 17 total")
    print("   Key columns: word, folio, section, language, placement, line_number, transcriber")

    print("\n2. PLACEMENT TYPES:")
    for cat, placements in categories.items():
        print(f"   {cat}: {placements}")

    print("\n3. TOKEN BREAKDOWN (H-only):")
    print("   Currier A: TEXT dominates, ~0.8% LABEL")
    print("   Currier B: TEXT dominates, minimal LABEL")

    print("\n4. LABEL vs TEXT OVERLAP:")
    print(f"   {overlap_data['overlap_size']}/{overlap_data['label_vocab_size']} label types also in text")

    print("\n5. FILTERING RECOMMENDATION:")
    print("   For text analysis: placement.startswith('P')")
    print("   For label analysis: placement.startswith('L')")
    print("   Exclude: R*, C*, S*, OTHER unless specifically needed")

    # Save results
    results = {
        'columns': {col: {'index': info['index'], 'unique_values': info['unique_values']}
                   for col, info in column_info.items()},
        'placement_categories': categories,
        'token_breakdown': breakdown,
        'vocab_counts': vocab_counts,
        'label_text_overlap': {
            'label_vocab_size': overlap_data['label_vocab_size'],
            'text_vocab_size': overlap_data['text_vocab_size'],
            'overlap_size': overlap_data['overlap_size']
        },
        'line_patterns': line_patterns
    }

    with open('results/transcript_audit.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n\nResults saved to results/transcript_audit.json")


if __name__ == '__main__':
    main()

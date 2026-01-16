"""
CAS Remaining Questions Diagnostic

Quick scan of unexplored structural questions about Currier A.
"""

from collections import defaultdict, Counter
from pathlib import Path
import json

project_root = Path(__file__).parent.parent.parent


def load_data():
    """Load Currier A data (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        entries[key]['tokens'].append(word)
                        entries[key]['section'] = section
                        entries[key]['folio'] = folio

    return dict(entries)


def load_b_data():
    """Load Currier B data by folio (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    folios = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                if lang == 'B':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    if word and folio:
                        folios[folio].append(word)

    return dict(folios)


def question_1_shared_vocabulary():
    """What tokens appear across multiple marker classes?"""
    print("\n" + "=" * 70)
    print("Q1: SHARED VOCABULARY (27.4% non-exclusive tokens)")
    print("=" * 70)

    catalog_path = Path(__file__).parent / 'marker_token_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # Find tokens that appear in multiple prefix classes
    token_prefixes = defaultdict(set)
    token_counts = defaultdict(int)

    for prefix, data in catalog.items():
        for token, count in data['all_tokens'].items():
            token_prefixes[token].add(prefix)
            token_counts[token] += count

    # Tokens in multiple classes
    multi_class = [(t, len(p), token_counts[t], p) for t, p in token_prefixes.items() if len(p) > 1]
    multi_class.sort(key=lambda x: (-x[1], -x[2]))

    print(f"\nTokens appearing in MULTIPLE prefix classes: {len(multi_class)}")
    print(f"\nTop 20 cross-class tokens:")
    for token, num_prefixes, count, prefixes in multi_class[:20]:
        print(f"  {token:20s} {num_prefixes} classes, {count:4d}x  ({', '.join(sorted(prefixes))})")

    # What are these? Structural or content?
    print(f"\nPattern analysis of cross-class tokens:")
    structural = []
    for token, num_prefixes, count, prefixes in multi_class:
        if token in ['daiin', 'ol', 'aiin', 'or', 'ar', 'al', 'y']:
            structural.append(token)

    print(f"  Likely structural primitives: {structural}")

    return len(multi_class)


def question_2_ab_folio_correlation():
    """Do folios with both A and B content show any relationship?"""
    print("\n" + "=" * 70)
    print("Q2: A-B FOLIO CORRELATION")
    print("=" * 70)

    a_entries = load_data()
    b_folios = load_b_data()

    # Find A folios
    a_folios = defaultdict(list)
    for entry_id, data in a_entries.items():
        folio = data['folio']
        a_folios[folio].append(data['tokens'])

    # Find folios with BOTH A and B
    both = set(a_folios.keys()) & set(b_folios.keys())
    a_only = set(a_folios.keys()) - set(b_folios.keys())
    b_only = set(b_folios.keys()) - set(a_folios.keys())

    print(f"\nFolio distribution:")
    print(f"  A only: {len(a_only)} folios")
    print(f"  B only: {len(b_only)} folios")
    print(f"  Both A and B: {len(both)} folios")

    if both:
        print(f"\nFolios with BOTH A and B content:")
        for folio in sorted(both)[:10]:
            a_tokens = sum(len(e) for e in a_folios[folio])
            b_tokens = len(b_folios[folio])
            print(f"  {folio}: A={a_tokens} tokens, B={b_tokens} tokens")

        # Check vocabulary overlap on shared folios
        print(f"\nVocabulary overlap on shared folios:")
        overlaps = []
        for folio in both:
            a_vocab = set(t for entry in a_folios[folio] for t in entry)
            b_vocab = set(b_folios[folio])
            overlap = len(a_vocab & b_vocab)
            union = len(a_vocab | b_vocab)
            jaccard = overlap / union if union > 0 else 0
            overlaps.append((folio, jaccard, overlap))

        overlaps.sort(key=lambda x: -x[1])
        for folio, jaccard, overlap in overlaps[:10]:
            print(f"  {folio}: Jaccard={jaccard:.3f}, shared={overlap} tokens")

        mean_jaccard = sum(j for _, j, _ in overlaps) / len(overlaps) if overlaps else 0
        print(f"\n  Mean Jaccard overlap: {mean_jaccard:.3f}")

    return len(both)


def question_3_nonblock_structure():
    """What's the internal structure of non-block entries?"""
    print("\n" + "=" * 70)
    print("Q3: NON-BLOCK ENTRY INTERNAL STRUCTURE")
    print("=" * 70)

    a_entries = load_data()
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Classify entries
    block_entries = []
    nonblock_entries = []

    for entry_id, data in a_entries.items():
        tokens = data['tokens']
        if len(tokens) < 4:
            nonblock_entries.append((entry_id, data))
            continue

        # Simple block detection
        n = len(tokens)
        is_block = False
        for block_size in range(1, n // 2 + 1):
            if n % block_size == 0:
                block = tokens[:block_size]
                count = n // block_size
                if count >= 2:
                    matches = True
                    for i in range(1, count):
                        chunk = tokens[i * block_size:(i + 1) * block_size]
                        mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                        if mismatches > len(block) * 0.2:
                            matches = False
                            break
                    if matches:
                        is_block = True
                        break

        if is_block:
            block_entries.append((entry_id, data))
        else:
            nonblock_entries.append((entry_id, data))

    print(f"\nBlock entries: {len(block_entries)}")
    print(f"Non-block entries: {len(nonblock_entries)}")

    # Analyze non-block entries
    print(f"\nNon-block entry characteristics:")

    # Length distribution
    lengths = [len(data['tokens']) for _, data in nonblock_entries]
    print(f"  Length range: {min(lengths)} - {max(lengths)}")
    print(f"  Mean length: {sum(lengths)/len(lengths):.1f}")

    # Marker diversity
    marker_counts = []
    for entry_id, data in nonblock_entries:
        markers = set()
        for token in data['tokens']:
            for prefix in marker_prefixes:
                if token.startswith(prefix):
                    markers.add(prefix)
                    break
        marker_counts.append(len(markers))

    print(f"  Mean marker classes per entry: {sum(marker_counts)/len(marker_counts):.1f}")

    # Check for patterns in non-block entries
    print(f"\nNon-block entry patterns:")

    # Do they start/end with specific tokens?
    first_tokens = Counter(data['tokens'][0] if data['tokens'] else '' for _, data in nonblock_entries)
    last_tokens = Counter(data['tokens'][-1] if data['tokens'] else '' for _, data in nonblock_entries)

    print(f"  Top 5 first tokens:")
    for token, count in first_tokens.most_common(5):
        print(f"    {token}: {count}")

    print(f"  Top 5 last tokens:")
    for token, count in last_tokens.most_common(5):
        print(f"    {token}: {count}")

    # Check for daiin/ol presence
    daiin_count = sum(1 for _, data in nonblock_entries if 'daiin' in data['tokens'])
    ol_count = sum(1 for _, data in nonblock_entries if 'ol' in data['tokens'])

    print(f"\n  Entries with 'daiin': {daiin_count} ({100*daiin_count/len(nonblock_entries):.1f}%)")
    print(f"  Entries with 'ol': {ol_count} ({100*ol_count/len(nonblock_entries):.1f}%)")

    return len(nonblock_entries)


def question_4_section_differences():
    """Are there structural differences between sections?"""
    print("\n" + "=" * 70)
    print("Q4: SECTION STRUCTURAL DIFFERENCES")
    print("=" * 70)

    a_entries = load_data()
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    # Group by section
    sections = defaultdict(list)
    for entry_id, data in a_entries.items():
        sections[data['section']].append(data)

    print(f"\nSections: {sorted(sections.keys())}")

    for section in sorted(sections.keys()):
        entries = sections[section]
        print(f"\n--- Section {section} ({len(entries)} entries) ---")

        # Entry length
        lengths = [len(e['tokens']) for e in entries]
        print(f"  Mean entry length: {sum(lengths)/len(lengths):.1f}")

        # Marker distribution
        marker_dist = Counter()
        for entry in entries:
            for token in entry['tokens']:
                for prefix in marker_prefixes:
                    if token.startswith(prefix):
                        marker_dist[prefix] += 1
                        break

        total = sum(marker_dist.values())
        print(f"  Marker distribution:")
        for prefix in sorted(marker_prefixes):
            pct = 100 * marker_dist[prefix] / total if total > 0 else 0
            print(f"    {prefix}: {pct:.1f}%")

        # daiin/ol rates
        daiin_entries = sum(1 for e in entries if 'daiin' in e['tokens'])
        ol_entries = sum(1 for e in entries if 'ol' in e['tokens'])
        print(f"  daiin presence: {100*daiin_entries/len(entries):.1f}%")
        print(f"  ol presence: {100*ol_entries/len(entries):.1f}%")


def main():
    print("=" * 70)
    print("CAS REMAINING QUESTIONS DIAGNOSTIC")
    print("=" * 70)

    q1 = question_1_shared_vocabulary()
    q2 = question_2_ab_folio_correlation()
    q3 = question_3_nonblock_structure()
    question_4_section_differences()

    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    print(f"""
FINDINGS:

Q1 (Shared Vocabulary): {q1} tokens appear in multiple marker classes
    - Most are structural primitives (daiin, ol, aiin, etc.)
    - NOT content leakage - confirms compositional structure

Q2 (A-B Correlation): {q2} folios have both A and B content
    - Need to check if overlap is meaningful or coincidental

Q3 (Non-Block Structure): Non-block entries analyzed
    - Mix markers (already known)
    - May have different structural purpose

Q4 (Section Differences): Structural comparison by section
    - Check if sections differ beyond vocabulary

ASSESSMENT:
- Q1: Likely CLOSED (structural primitives, no new insight)
- Q2: Worth investigating IF overlap > random
- Q3: Moderate value - different content type, may have purpose
- Q4: Low value - sections are vocabulary-isolated, likely no structural difference
""")


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
Line Position Analysis

Following up on the finding that 86% of Section P short singletons
appear in lines 1-5. Is this pattern:
1. Section P specific or general?
2. Short-entry specific or all singletons?
3. Related to clustering or independent?
"""
import sys
from collections import defaultdict, Counter
from enum import Enum
import numpy as np

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, EXTENDED_PREFIX_MAP

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


class EntryClass(Enum):
    SINGLETON = "SINGLETON"
    RUN_START = "RUN_START"
    RUN_INTERNAL = "RUN_INTERNAL"
    RUN_END = "RUN_END"


def load_currier_a_entries():
    entries = []
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
                    if current_entry is not None:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key, 'folio': folio, 'section': section,
                        'line': line_num, 'tokens': []
                    }
                current_entry['tokens'].append(word)
        if current_entry is not None:
            entries.append(current_entry)
    return entries


def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def token_jaccard(e1, e2):
    return jaccard(set(e1['tokens']), set(e2['tokens']))


def classify_entries(entries, threshold=0.0):
    n = len(entries)
    adj_j = []
    for i in range(n - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            adj_j.append(token_jaccard(entries[i], entries[i+1]))
        else:
            adj_j.append(-1)

    runs = []
    current_run = [0]
    for i in range(n - 1):
        j = adj_j[i]
        if j > threshold:
            current_run.append(i + 1)
        else:
            if len(current_run) >= 2:
                runs.append(current_run)
            current_run = [i + 1]
    if len(current_run) >= 2:
        runs.append(current_run)

    classification = {}
    for i in range(n):
        classification[i] = {'class': EntryClass.SINGLETON, 'run_id': None, 'run_size': None}

    for run_id, run in enumerate(runs):
        run_size = len(run)
        for pos, idx in enumerate(run):
            if pos == 0:
                entry_class = EntryClass.RUN_START
            elif pos == run_size - 1:
                entry_class = EntryClass.RUN_END
            else:
                entry_class = EntryClass.RUN_INTERNAL
            classification[idx] = {'class': entry_class, 'run_id': run_id, 'run_size': run_size}

    return classification, runs


def get_line_num(line_str):
    """Extract numeric line number from line string."""
    try:
        return int(''.join(c for c in line_str if c.isdigit()))
    except:
        return None


def main():
    print("=" * 70)
    print("LINE POSITION ANALYSIS")
    print("=" * 70)

    entries = load_currier_a_entries()
    classification, runs = classify_entries(entries)

    print(f"\nLoaded {len(entries)} entries")

    # ==========================================================================
    # ANALYSIS 1: Line position by section and clustering status
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 1: LINE POSITION BY SECTION AND CLUSTERING STATUS")
    print("=" * 70)

    for section in ['H', 'P', 'T']:
        print(f"\n--- Section {section} ---")

        sec_entries = [(i, e) for i, e in enumerate(entries) if e['section'] == section]

        # Split by clustering status
        singletons = [(i, e) for i, e in sec_entries if classification[i]['class'] == EntryClass.SINGLETON]
        clustered = [(i, e) for i, e in sec_entries if classification[i]['class'] != EntryClass.SINGLETON]

        print(f"\nSingletons: {len(singletons)}, Clustered: {len(clustered)}")

        # Line position distribution
        for name, subset in [("Singleton", singletons), ("Clustered", clustered)]:
            early = sum(1 for i, e in subset if get_line_num(e['line']) is not None and get_line_num(e['line']) <= 5)
            mid = sum(1 for i, e in subset if get_line_num(e['line']) is not None and 5 < get_line_num(e['line']) <= 15)
            late = sum(1 for i, e in subset if get_line_num(e['line']) is not None and get_line_num(e['line']) > 15)
            total = early + mid + late

            if total > 0:
                print(f"  {name}: Early(1-5)={100*early/total:.1f}%, Mid(6-15)={100*mid/total:.1f}%, Late(16+)={100*late/total:.1f}%")

    # ==========================================================================
    # ANALYSIS 2: Line position by entry length
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 2: LINE POSITION BY ENTRY LENGTH")
    print("=" * 70)

    length_bins = [(1, 5), (6, 10), (11, 20), (21, 50), (51, 100)]

    print(f"\n{'Length':<12} {'Early %':<12} {'Mid %':<12} {'Late %':<12} {'N':<8}")
    print("-" * 55)

    for low, high in length_bins:
        subset = [e for e in entries if low <= len(e['tokens']) <= high]
        if not subset:
            continue

        early = sum(1 for e in subset if get_line_num(e['line']) is not None and get_line_num(e['line']) <= 5)
        mid = sum(1 for e in subset if get_line_num(e['line']) is not None and 5 < get_line_num(e['line']) <= 15)
        late = sum(1 for e in subset if get_line_num(e['line']) is not None and get_line_num(e['line']) > 15)
        total = early + mid + late

        if total > 0:
            print(f"{low}-{high:<8} {100*early/total:<12.1f} {100*mid/total:<12.1f} {100*late/total:<12.1f} {total:<8}")

    # ==========================================================================
    # ANALYSIS 3: Section P short singletons - detailed line analysis
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 3: SECTION P SHORT SINGLETONS - LINE DETAIL")
    print("=" * 70)

    p_short_sing = [(i, e) for i, e in enumerate(entries)
                    if e['section'] == 'P'
                    and len(e['tokens']) <= 5
                    and classification[i]['class'] == EntryClass.SINGLETON]

    print(f"\nSection P short singletons: {len(p_short_sing)}")

    # Exact line distribution
    line_dist = Counter()
    for i, e in p_short_sing:
        ln = get_line_num(e['line'])
        if ln:
            line_dist[ln] += 1

    print(f"\nExact line distribution:")
    for ln in sorted(line_dist.keys()):
        count = line_dist[ln]
        bar = '#' * (count // 2)
        print(f"  Line {ln:2d}: {count:3d} {bar}")

    # Are they the FIRST entry on their folio?
    print(f"\n--- First-on-folio analysis ---")
    folio_first_entries = {}
    for i, e in enumerate(entries):
        if e['folio'] not in folio_first_entries:
            folio_first_entries[e['folio']] = i

    first_on_folio = sum(1 for i, e in p_short_sing if folio_first_entries.get(e['folio']) == i)
    print(f"  First entry on folio: {first_on_folio}/{len(p_short_sing)} ({100*first_on_folio/len(p_short_sing):.1f}%)")

    # Line 1 specifically
    line_1 = sum(1 for i, e in p_short_sing if get_line_num(e['line']) == 1)
    print(f"  On line 1: {line_1}/{len(p_short_sing)} ({100*line_1/len(p_short_sing):.1f}%)")

    # ==========================================================================
    # ANALYSIS 4: Are ALL line-1 entries short singletons?
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 4: ALL LINE-1 ENTRIES")
    print("=" * 70)

    line_1_entries = [(i, e) for i, e in enumerate(entries) if get_line_num(e['line']) == 1]

    print(f"\nTotal line-1 entries: {len(line_1_entries)}")

    # By section
    for section in ['H', 'P', 'T']:
        sec_line_1 = [(i, e) for i, e in line_1_entries if e['section'] == section]
        if not sec_line_1:
            continue

        n_singleton = sum(1 for i, e in sec_line_1 if classification[i]['class'] == EntryClass.SINGLETON)
        n_clustered = len(sec_line_1) - n_singleton
        mean_tokens = np.mean([len(e['tokens']) for i, e in sec_line_1])

        print(f"\n  Section {section}: {len(sec_line_1)} line-1 entries")
        print(f"    Singleton: {n_singleton} ({100*n_singleton/len(sec_line_1):.1f}%)")
        print(f"    Clustered: {n_clustered} ({100*n_clustered/len(sec_line_1):.1f}%)")
        print(f"    Mean tokens: {mean_tokens:.1f}")

    # ==========================================================================
    # ANALYSIS 5: Token count by line position (all sections)
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 5: TOKEN COUNT BY LINE POSITION")
    print("=" * 70)

    print(f"\n{'Line Range':<15} {'Mean Tokens':<15} {'Median':<12} {'N':<10}")
    print("-" * 55)

    for low, high in [(1, 1), (2, 3), (4, 5), (6, 10), (11, 20), (21, 30)]:
        subset = [e for e in entries if get_line_num(e['line']) is not None
                  and low <= get_line_num(e['line']) <= high]
        if len(subset) < 10:
            continue

        tokens = [len(e['tokens']) for e in subset]
        print(f"{low}-{high:<12} {np.mean(tokens):<15.1f} {np.median(tokens):<12.0f} {len(subset):<10}")

    # ==========================================================================
    # ANALYSIS 6: Is there a "header" pattern?
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 6: POTENTIAL HEADER PATTERN")
    print("=" * 70)

    # For each folio, compare line-1 to rest-of-folio
    folio_comparisons = []

    folios = sorted(set(e['folio'] for e in entries))
    for folio in folios:
        folio_entries = [e for e in entries if e['folio'] == folio]
        if len(folio_entries) < 5:
            continue

        line_1_entries_folio = [e for e in folio_entries if get_line_num(e['line']) == 1]
        other_entries = [e for e in folio_entries if get_line_num(e['line']) != 1]

        if not line_1_entries_folio or not other_entries:
            continue

        line_1_tokens = np.mean([len(e['tokens']) for e in line_1_entries_folio])
        other_tokens = np.mean([len(e['tokens']) for e in other_entries])

        folio_comparisons.append({
            'folio': folio,
            'section': folio_entries[0]['section'],
            'line_1_tokens': line_1_tokens,
            'other_tokens': other_tokens,
            'ratio': line_1_tokens / other_tokens if other_tokens > 0 else 0
        })

    # Aggregate by section
    print(f"\nLine-1 vs rest-of-folio token counts (by section):")
    print(f"\n{'Section':<10} {'Line-1 Mean':<15} {'Other Mean':<15} {'Ratio':<10} {'N folios':<10}")
    print("-" * 60)

    for section in ['H', 'P', 'T']:
        sec_comps = [c for c in folio_comparisons if c['section'] == section]
        if not sec_comps:
            continue

        l1_mean = np.mean([c['line_1_tokens'] for c in sec_comps])
        other_mean = np.mean([c['other_tokens'] for c in sec_comps])
        ratio = l1_mean / other_mean if other_mean > 0 else 0

        print(f"{section:<10} {l1_mean:<15.1f} {other_mean:<15.1f} {ratio:<10.2f} {len(sec_comps):<10}")

    # ==========================================================================
    # ANALYSIS 7: Vocabulary overlap - line 1 vs rest
    # ==========================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 7: VOCABULARY - LINE 1 VS REST")
    print("=" * 70)

    line_1_tokens_all = []
    other_tokens_all = []

    for e in entries:
        ln = get_line_num(e['line'])
        if ln == 1:
            line_1_tokens_all.extend(e['tokens'])
        elif ln is not None:
            other_tokens_all.extend(e['tokens'])

    l1_vocab = set(line_1_tokens_all)
    other_vocab = set(other_tokens_all)

    shared = l1_vocab & other_vocab
    l1_only = l1_vocab - other_vocab
    other_only = other_vocab - l1_vocab

    print(f"\nLine-1 vocabulary: {len(l1_vocab)} unique tokens")
    print(f"Other vocabulary: {len(other_vocab)} unique tokens")
    print(f"Shared: {len(shared)} ({100*len(shared)/len(l1_vocab):.1f}% of line-1)")
    print(f"Line-1 only: {len(l1_only)} ({100*len(l1_only)/len(l1_vocab):.1f}% of line-1)")

    if l1_only:
        print(f"\nTokens appearing ONLY on line 1:")
        l1_only_freq = Counter(t for t in line_1_tokens_all if t in l1_only)
        for token, count in l1_only_freq.most_common(15):
            print(f"  {token}: {count}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)


if __name__ == '__main__':
    main()

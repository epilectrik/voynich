#!/usr/bin/env python
"""
Cluster Deep Dive Analysis

Pursuing open questions from cluster characterization:
1. Section P short-entry population - What ARE these entries?
2. Large run (size 5+) vocabulary - What vocabulary is shared?

All analyses remain purely descriptive - no semantic claims.
"""
import sys
from collections import defaultdict, Counter
from enum import Enum
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES, EXTENDED_PREFIX_MAP

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


class EntryClass(Enum):
    SINGLETON = "SINGLETON"
    RUN_START = "RUN_START"
    RUN_INTERNAL = "RUN_INTERNAL"
    RUN_END = "RUN_END"


# =============================================================================
# REUSED FUNCTIONS
# =============================================================================

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


def extract_prefix(token):
    token_lower = token.lower()
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            return EXTENDED_PREFIX_MAP[prefix3]
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            return prefix2
    return None


def extract_middle(token):
    token_lower = token.lower()
    prefix_len = 0
    if len(token_lower) >= 3 and token_lower[:3] in EXTENDED_PREFIX_MAP:
        prefix_len = 3
    elif len(token_lower) >= 2 and token_lower[:2] in MARKER_FAMILIES:
        prefix_len = 2
    suffix_len = 0
    for sl in range(min(5, len(token_lower) - prefix_len), 0, -1):
        if token_lower[-sl:] in A_UNIVERSAL_SUFFIXES:
            suffix_len = sl
            break
    if prefix_len + suffix_len < len(token_lower):
        return token_lower[prefix_len:-suffix_len] if suffix_len > 0 else token_lower[prefix_len:]
    return ''


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
        classification[i] = {
            'class': EntryClass.SINGLETON, 'run_id': None,
            'run_size': None, 'position_in_run': None
        }

    for run_id, run in enumerate(runs):
        run_size = len(run)
        for pos, idx in enumerate(run):
            if pos == 0:
                entry_class = EntryClass.RUN_START
            elif pos == run_size - 1:
                entry_class = EntryClass.RUN_END
            else:
                entry_class = EntryClass.RUN_INTERNAL
            classification[idx] = {
                'class': entry_class, 'run_id': run_id,
                'run_size': run_size, 'position_in_run': pos
            }

    return classification, runs, adj_j


# =============================================================================
# SECTION P DEEP DIVE
# =============================================================================

def analyze_section_p_short_entries(entries, classification):
    """Deep investigation of Section P short singleton entries."""
    print("\n" + "=" * 70)
    print("SECTION P SHORT-ENTRY POPULATION ANALYSIS")
    print("=" * 70)

    # Get Section P short singletons (1-5 tokens)
    p_short_singletons = []
    for i, e in enumerate(entries):
        if (e['section'] == 'P' and
            len(e['tokens']) <= 5 and
            classification[i]['class'] == EntryClass.SINGLETON):
            p_short_singletons.append(i)

    print(f"\nSection P short singletons (1-5 tokens): {len(p_short_singletons)} entries")

    # Folio distribution
    print("\n--- Folio Distribution ---")
    folio_counts = Counter(entries[i]['folio'] for i in p_short_singletons)

    print(f"\nFolios with short singletons: {len(folio_counts)}")
    print(f"\nTop 15 folios by count:")
    for folio, count in folio_counts.most_common(15):
        print(f"  {folio}: {count} entries")

    # Check if concentrated or dispersed
    total_p_folios = len(set(e['folio'] for e in entries if e['section'] == 'P'))
    folios_with_short = len(folio_counts)
    print(f"\nDispersion: {folios_with_short}/{total_p_folios} Section P folios have short singletons ({100*folios_with_short/total_p_folios:.1f}%)")

    # Token count distribution
    print("\n--- Token Count Distribution ---")
    token_counts = Counter(len(entries[i]['tokens']) for i in p_short_singletons)
    for tc in sorted(token_counts.keys()):
        count = token_counts[tc]
        pct = 100 * count / len(p_short_singletons)
        bar = '#' * int(pct / 2)
        print(f"  {tc} tokens: {count:4d} ({pct:5.1f}%) {bar}")

    # Actual token inventory
    print("\n--- Token Inventory ---")
    all_tokens = []
    for i in p_short_singletons:
        all_tokens.extend(entries[i]['tokens'])

    token_freq = Counter(all_tokens)
    print(f"\nTotal tokens: {len(all_tokens)}")
    print(f"Unique tokens: {len(token_freq)}")
    print(f"Type-token ratio: {len(token_freq)/len(all_tokens):.3f}")

    print(f"\nMost common tokens:")
    for token, count in token_freq.most_common(20):
        pct = 100 * count / len(all_tokens)
        print(f"  {token}: {count} ({pct:.1f}%)")

    # Prefix distribution
    print("\n--- Prefix Distribution ---")
    prefix_counts = Counter()
    for i in p_short_singletons:
        for t in entries[i]['tokens']:
            p = extract_prefix(t)
            if p:
                prefix_counts[p] += 1

    total_prefixes = sum(prefix_counts.values())
    print(f"\nTokens with recognized prefix: {total_prefixes}/{len(all_tokens)} ({100*total_prefixes/len(all_tokens):.1f}%)")

    for prefix, count in prefix_counts.most_common():
        pct = 100 * count / total_prefixes if total_prefixes > 0 else 0
        print(f"  {prefix}: {count} ({pct:.1f}%)")

    # Entry structure patterns
    print("\n--- Entry Structure Patterns ---")

    # Single-token entries
    single_token = [i for i in p_short_singletons if len(entries[i]['tokens']) == 1]
    print(f"\nSingle-token entries: {len(single_token)}")
    if single_token:
        single_tokens = [entries[i]['tokens'][0] for i in single_token]
        single_freq = Counter(single_tokens)
        print(f"  Unique single tokens: {len(single_freq)}")
        print(f"  Most common:")
        for token, count in single_freq.most_common(10):
            print(f"    {token}: {count}")

    # Two-token entries
    two_token = [i for i in p_short_singletons if len(entries[i]['tokens']) == 2]
    print(f"\nTwo-token entries: {len(two_token)}")
    if two_token:
        # Check for patterns
        patterns = Counter()
        for i in two_token:
            t1, t2 = entries[i]['tokens']
            p1, p2 = extract_prefix(t1), extract_prefix(t2)
            pattern = f"{p1 or '?'}-{p2 or '?'}"
            patterns[pattern] += 1
        print(f"  Prefix patterns:")
        for pattern, count in patterns.most_common(10):
            print(f"    {pattern}: {count}")

    # Compare to Section P clustered entries
    print("\n--- Comparison to Section P Clustered Entries ---")

    p_clustered = [i for i, e in enumerate(entries)
                   if e['section'] == 'P' and classification[i]['class'] != EntryClass.SINGLETON]

    p_clust_tokens = []
    for i in p_clustered:
        p_clust_tokens.extend(entries[i]['tokens'])

    clust_token_freq = Counter(p_clust_tokens)

    # Find tokens unique to short singletons
    short_only = set(token_freq.keys()) - set(clust_token_freq.keys())
    clust_only = set(clust_token_freq.keys()) - set(token_freq.keys())
    shared = set(token_freq.keys()) & set(clust_token_freq.keys())

    print(f"\nVocabulary overlap:")
    print(f"  Short singleton vocabulary: {len(token_freq)} unique tokens")
    print(f"  Clustered vocabulary: {len(clust_token_freq)} unique tokens")
    print(f"  Shared: {len(shared)} ({100*len(shared)/len(token_freq):.1f}% of short)")
    print(f"  Short-only: {len(short_only)} ({100*len(short_only)/len(token_freq):.1f}% of short)")
    print(f"  Clustered-only: {len(clust_only)}")

    if short_only:
        print(f"\n  Tokens appearing ONLY in short singletons:")
        short_only_freq = [(t, token_freq[t]) for t in short_only]
        short_only_freq.sort(key=lambda x: -x[1])
        for token, count in short_only_freq[:15]:
            print(f"    {token}: {count}")

    # Check for line position patterns
    print("\n--- Line Position Analysis ---")
    line_positions = Counter()
    for i in p_short_singletons:
        line = entries[i]['line']
        # Extract numeric part if possible
        try:
            line_num = int(''.join(c for c in line if c.isdigit()))
            if line_num <= 5:
                line_positions['early (1-5)'] += 1
            elif line_num <= 10:
                line_positions['middle (6-10)'] += 1
            else:
                line_positions['late (11+)'] += 1
        except:
            line_positions['unknown'] += 1

    print(f"\nLine position distribution:")
    for pos, count in line_positions.most_common():
        pct = 100 * count / len(p_short_singletons)
        print(f"  {pos}: {count} ({pct:.1f}%)")


# =============================================================================
# LARGE RUN VOCABULARY ANALYSIS
# =============================================================================

def analyze_large_run_vocabulary(entries, classification, runs):
    """Analyze what vocabulary is shared in size-5+ runs."""
    print("\n" + "=" * 70)
    print("LARGE RUN (SIZE 5+) VOCABULARY ANALYSIS")
    print("=" * 70)

    large_runs = [r for r in runs if len(r) >= 5]
    print(f"\nSize 5+ runs: {len(large_runs)}")
    print(f"Sizes: {sorted([len(r) for r in large_runs], reverse=True)}")

    # Analyze each large run
    run_analyses = []

    for run_id, run in enumerate(large_runs):
        # Collect all tokens in this run
        all_tokens = []
        token_sets = []
        for idx in run:
            tokens = entries[idx]['tokens']
            all_tokens.extend(tokens)
            token_sets.append(set(tokens))

        # Find tokens shared by ALL entries in the run
        shared_by_all = token_sets[0].copy()
        for ts in token_sets[1:]:
            shared_by_all &= ts

        # Find tokens shared by MAJORITY (>50%)
        token_counts = Counter(all_tokens)
        threshold = len(run) / 2
        shared_by_majority = {t for t, c in token_counts.items()
                             if sum(1 for ts in token_sets if t in ts) > threshold}

        # Compute within-run Jaccard
        within_j = []
        for i in range(len(run)):
            for j in range(i+1, len(run)):
                within_j.append(token_jaccard(entries[run[i]], entries[run[j]]))

        run_analyses.append({
            'run_id': run_id,
            'size': len(run),
            'total_tokens': len(all_tokens),
            'unique_tokens': len(set(all_tokens)),
            'shared_by_all': shared_by_all,
            'shared_by_majority': shared_by_majority,
            'mean_within_j': np.mean(within_j),
            'indices': run,
            'folios': [entries[idx]['folio'] for idx in run],
            'section': entries[run[0]]['section']
        })

    # Summary statistics
    print(f"\n--- Run-Level Statistics ---")
    print(f"\n{'Run':<6} {'Size':<6} {'Section':<8} {'Within J':<10} {'Shared All':<12} {'Shared Maj':<12}")
    print("-" * 60)

    for ra in sorted(run_analyses, key=lambda x: -x['size']):
        print(f"{ra['run_id']:<6} {ra['size']:<6} {ra['section']:<8} {ra['mean_within_j']:<10.3f} {len(ra['shared_by_all']):<12} {len(ra['shared_by_majority']):<12}")

    # Examine the largest run in detail
    print(f"\n--- Detailed Analysis: Largest Run ---")
    largest = max(run_analyses, key=lambda x: x['size'])
    print(f"\nRun size: {largest['size']}")
    print(f"Section: {largest['section']}")
    print(f"Folios: {largest['folios']}")
    print(f"Mean within-run Jaccard: {largest['mean_within_j']:.3f}")

    print(f"\nTokens shared by ALL {largest['size']} entries:")
    if largest['shared_by_all']:
        for t in sorted(largest['shared_by_all']):
            print(f"  {t}")
    else:
        print("  (none)")

    print(f"\nTokens shared by MAJORITY (>{largest['size']//2} entries):")
    for t in sorted(largest['shared_by_majority']):
        print(f"  {t}")

    # Show actual entries in largest run
    print(f"\n--- Entries in Largest Run ---")
    for idx in largest['indices']:
        e = entries[idx]
        tokens_str = ' '.join(e['tokens'][:10])
        if len(e['tokens']) > 10:
            tokens_str += f"... (+{len(e['tokens'])-10} more)"
        print(f"  {e['folio']}_{e['line']}: {tokens_str}")

    # Aggregate: what vocabulary characterizes large runs?
    print(f"\n--- Aggregate Vocabulary in Large Runs ---")

    all_large_run_tokens = []
    for ra in run_analyses:
        for idx in ra['indices']:
            all_large_run_tokens.extend(entries[idx]['tokens'])

    large_run_vocab = Counter(all_large_run_tokens)

    # Compare to overall Currier A vocabulary
    all_a_tokens = []
    for e in entries:
        all_a_tokens.extend(e['tokens'])
    overall_vocab = Counter(all_a_tokens)

    print(f"\nLarge run vocabulary: {len(large_run_vocab)} unique tokens")
    print(f"Overall Currier A vocabulary: {len(overall_vocab)} unique tokens")

    # Find tokens enriched in large runs
    print(f"\nTokens enriched in large runs (vs overall frequency):")
    enriched = []
    for token, count in large_run_vocab.items():
        large_run_rate = count / len(all_large_run_tokens)
        overall_rate = overall_vocab[token] / len(all_a_tokens)
        if overall_rate > 0:
            enrichment = large_run_rate / overall_rate
            if enrichment > 2 and count >= 5:  # At least 2x enriched, min 5 occurrences
                enriched.append((token, count, enrichment))

    enriched.sort(key=lambda x: -x[2])
    for token, count, enrich in enriched[:20]:
        print(f"  {token}: {count} occurrences, {enrich:.2f}x enriched")

    # Prefix analysis for large runs
    print(f"\n--- Prefix Distribution in Large Runs ---")
    large_run_prefixes = Counter()
    for ra in run_analyses:
        for idx in ra['indices']:
            for t in entries[idx]['tokens']:
                p = extract_prefix(t)
                if p:
                    large_run_prefixes[p] += 1

    overall_prefixes = Counter()
    for e in entries:
        for t in e['tokens']:
            p = extract_prefix(t)
            if p:
                overall_prefixes[p] += 1

    print(f"\n{'Prefix':<8} {'Large Run %':<15} {'Overall %':<15} {'Ratio':<10}")
    print("-" * 50)

    total_large = sum(large_run_prefixes.values())
    total_overall = sum(overall_prefixes.values())

    for prefix in sorted(MARKER_FAMILIES):
        large_pct = 100 * large_run_prefixes.get(prefix, 0) / total_large if total_large > 0 else 0
        overall_pct = 100 * overall_prefixes.get(prefix, 0) / total_overall if total_overall > 0 else 0
        ratio = large_pct / overall_pct if overall_pct > 0 else 0
        print(f"{prefix:<8} {large_pct:<15.1f} {overall_pct:<15.1f} {ratio:<10.2f}x")


# =============================================================================
# SINGLETON VS CLUSTERED VOCABULARY DIVERGENCE
# =============================================================================

def analyze_vocabulary_divergence(entries, classification):
    """Check if singletons and clustered entries have distinct vocabularies."""
    print("\n" + "=" * 70)
    print("SINGLETON VS CLUSTERED VOCABULARY DIVERGENCE")
    print("=" * 70)

    singleton_tokens = []
    clustered_tokens = []

    for i, e in enumerate(entries):
        if classification[i]['class'] == EntryClass.SINGLETON:
            singleton_tokens.extend(e['tokens'])
        else:
            clustered_tokens.extend(e['tokens'])

    sing_vocab = Counter(singleton_tokens)
    clust_vocab = Counter(clustered_tokens)

    print(f"\nSingleton vocabulary: {len(sing_vocab)} unique tokens ({len(singleton_tokens)} total)")
    print(f"Clustered vocabulary: {len(clust_vocab)} unique tokens ({len(clustered_tokens)} total)")

    # Overlap
    shared = set(sing_vocab.keys()) & set(clust_vocab.keys())
    sing_only = set(sing_vocab.keys()) - set(clust_vocab.keys())
    clust_only = set(clust_vocab.keys()) - set(sing_vocab.keys())

    print(f"\nVocabulary overlap:")
    print(f"  Shared: {len(shared)} tokens")
    print(f"  Singleton-only: {len(sing_only)} tokens ({100*len(sing_only)/len(sing_vocab):.1f}%)")
    print(f"  Clustered-only: {len(clust_only)} tokens ({100*len(clust_only)/len(clust_vocab):.1f}%)")

    # Tokens strongly associated with each class
    print(f"\n--- Tokens Enriched in Singletons ---")
    sing_enriched = []
    for token in sing_vocab:
        sing_rate = sing_vocab[token] / len(singleton_tokens)
        clust_rate = clust_vocab.get(token, 0) / len(clustered_tokens)
        if clust_rate > 0:
            ratio = sing_rate / clust_rate
        else:
            ratio = float('inf')
        if ratio > 2 and sing_vocab[token] >= 10:
            sing_enriched.append((token, sing_vocab[token], ratio))

    sing_enriched.sort(key=lambda x: -x[2] if x[2] != float('inf') else -1000000)
    for token, count, ratio in sing_enriched[:15]:
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "ONLY"
        print(f"  {token}: {count} occurrences, {ratio_str} enriched")

    print(f"\n--- Tokens Enriched in Clustered ---")
    clust_enriched = []
    for token in clust_vocab:
        clust_rate = clust_vocab[token] / len(clustered_tokens)
        sing_rate = sing_vocab.get(token, 0) / len(singleton_tokens)
        if sing_rate > 0:
            ratio = clust_rate / sing_rate
        else:
            ratio = float('inf')
        if ratio > 2 and clust_vocab[token] >= 10:
            clust_enriched.append((token, clust_vocab[token], ratio))

    clust_enriched.sort(key=lambda x: -x[2] if x[2] != float('inf') else -1000000)
    for token, count, ratio in clust_enriched[:15]:
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "ONLY"
        print(f"  {token}: {count} occurrences, {ratio_str} enriched")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("CLUSTER DEEP DIVE ANALYSIS")
    print("=" * 70)
    print("\nPursuing open questions from cluster characterization.")

    print("\nLoading entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries")

    classification, runs, adj_j = classify_entries(entries, threshold=0.0)
    print(f"Classified entries into {len(runs)} runs")

    # Run analyses
    analyze_section_p_short_entries(entries, classification)
    analyze_large_run_vocabulary(entries, classification, runs)
    analyze_vocabulary_divergence(entries, classification)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()

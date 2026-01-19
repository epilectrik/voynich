#!/usr/bin/env python
"""
Extended Cluster Analysis

Following up on cluster_characterization.py findings, this script investigates:
1. Section P anomaly - Why such extreme clustering asymmetry?
2. Short-entry clustering drivers - What makes 1-10 token clusters special?
3. Within-run similarity decay - Does similarity decrease across run length?
4. Vocabulary component sharing - PREFIX vs MIDDLE vs SUFFIX in clusters
5. Cluster homogeneity - Do runs share dominant prefix families?
6. Run-size effects - How do small vs large runs differ?

All analyses treat clusters as statistical phenomena, not entities.
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
# REUSED FUNCTIONS FROM cluster_characterization.py
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


def extract_suffix(token):
    token_lower = token.lower()
    for sl in range(min(5, len(token_lower)), 0, -1):
        if token_lower[-sl:] in A_UNIVERSAL_SUFFIXES:
            return token_lower[-sl:]
    return ''


def is_da(token):
    token_lower = token.lower()
    return any(token_lower.startswith(p) for p in DA_PREFIXES)


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
# ANALYSIS 1: SECTION P ANOMALY
# =============================================================================

def analyze_section_p_anomaly(entries, classification):
    """Deep dive into Section P's extreme clustering asymmetry."""
    print("\n" + "=" * 70)
    print("ANALYSIS 1: SECTION P ANOMALY")
    print("=" * 70)

    # Get section P entries
    p_indices = [i for i, e in enumerate(entries) if e['section'] == 'P']

    if not p_indices:
        print("No section P entries found.")
        return

    p_clustered = [i for i in p_indices if classification[i]['class'] != EntryClass.SINGLETON]
    p_singleton = [i for i in p_indices if classification[i]['class'] == EntryClass.SINGLETON]

    print(f"\nSection P overview:")
    print(f"  Total entries: {len(p_indices)}")
    print(f"  Clustered: {len(p_clustered)} ({100*len(p_clustered)/len(p_indices):.1f}%)")
    print(f"  Singleton: {len(p_singleton)} ({100*len(p_singleton)/len(p_indices):.1f}%)")

    # Token count distributions
    c_tokens = [len(entries[i]['tokens']) for i in p_clustered]
    s_tokens = [len(entries[i]['tokens']) for i in p_singleton]

    print(f"\nToken count statistics:")
    print(f"  Clustered: mean={np.mean(c_tokens):.1f}, median={np.median(c_tokens):.0f}, min={min(c_tokens)}, max={max(c_tokens)}")
    print(f"  Singleton: mean={np.mean(s_tokens):.1f}, median={np.median(s_tokens):.0f}, min={min(s_tokens)}, max={max(s_tokens)}")

    # What's driving the singleton shortness?
    print(f"\nSingleton token count distribution (Section P):")
    s_bins = Counter()
    for t in s_tokens:
        if t <= 5:
            s_bins['1-5'] += 1
        elif t <= 10:
            s_bins['6-10'] += 1
        elif t <= 15:
            s_bins['11-15'] += 1
        else:
            s_bins['16+'] += 1

    for bin_name in ['1-5', '6-10', '11-15', '16+']:
        count = s_bins.get(bin_name, 0)
        pct = 100 * count / len(s_tokens) if s_tokens else 0
        print(f"    {bin_name} tokens: {count} ({pct:.1f}%)")

    # Compare to other sections
    print(f"\nComparison across sections:")
    print(f"{'Section':<10} {'Total':<8} {'Clust %':<10} {'Clust Tok':<12} {'Sing Tok':<12} {'Ratio':<8}")
    print("-" * 60)

    for section in ['H', 'P', 'T']:
        sec_indices = [i for i, e in enumerate(entries) if e['section'] == section]
        sec_clust = [i for i in sec_indices if classification[i]['class'] != EntryClass.SINGLETON]
        sec_sing = [i for i in sec_indices if classification[i]['class'] == EntryClass.SINGLETON]

        if not sec_clust or not sec_sing:
            continue

        c_mean = np.mean([len(entries[i]['tokens']) for i in sec_clust])
        s_mean = np.mean([len(entries[i]['tokens']) for i in sec_sing])
        ratio = c_mean / s_mean if s_mean > 0 else 0
        clust_pct = 100 * len(sec_clust) / len(sec_indices)

        print(f"{section:<10} {len(sec_indices):<8} {clust_pct:<10.1f}% {c_mean:<12.1f} {s_mean:<12.1f} {ratio:<8.2f}x")

    # Check if P singletons are fundamentally different entries
    print(f"\nSection P singleton characteristics:")

    # Prefix distribution in P singletons vs P clustered
    p_sing_prefixes = Counter()
    p_clust_prefixes = Counter()

    for i in p_singleton:
        for t in entries[i]['tokens']:
            p = extract_prefix(t)
            if p:
                p_sing_prefixes[p] += 1

    for i in p_clustered:
        for t in entries[i]['tokens']:
            p = extract_prefix(t)
            if p:
                p_clust_prefixes[p] += 1

    # Normalize
    sing_total = sum(p_sing_prefixes.values())
    clust_total = sum(p_clust_prefixes.values())

    print(f"\n  Prefix distribution (normalized):")
    print(f"  {'Prefix':<8} {'Singleton %':<15} {'Clustered %':<15}")
    print("  " + "-" * 40)

    all_prefixes = set(p_sing_prefixes.keys()) | set(p_clust_prefixes.keys())
    for prefix in sorted(all_prefixes):
        s_pct = 100 * p_sing_prefixes.get(prefix, 0) / sing_total if sing_total > 0 else 0
        c_pct = 100 * p_clust_prefixes.get(prefix, 0) / clust_total if clust_total > 0 else 0
        if abs(s_pct - c_pct) > 3:  # Show only notable differences
            print(f"  {prefix:<8} {s_pct:<15.1f} {c_pct:<15.1f}")


# =============================================================================
# ANALYSIS 2: SHORT-ENTRY CLUSTERING DRIVERS
# =============================================================================

def analyze_short_entry_clustering(entries, classification):
    """What makes 1-10 token clustered entries special?"""
    print("\n" + "=" * 70)
    print("ANALYSIS 2: SHORT-ENTRY CLUSTERING DRIVERS")
    print("=" * 70)

    # Get short entries (1-10 tokens)
    short_indices = [i for i, e in enumerate(entries) if len(e['tokens']) <= 10]

    if not short_indices:
        print("No short entries found.")
        return

    short_clustered = [i for i in short_indices if classification[i]['class'] != EntryClass.SINGLETON]
    short_singleton = [i for i in short_indices if classification[i]['class'] == EntryClass.SINGLETON]

    print(f"\nShort entries (1-10 tokens):")
    print(f"  Total: {len(short_indices)}")
    print(f"  Clustered: {len(short_clustered)} ({100*len(short_clustered)/len(short_indices):.1f}%)")
    print(f"  Singleton: {len(short_singleton)} ({100*len(short_singleton)/len(short_indices):.1f}%)")

    # What vocabulary do short clustered entries share?
    print(f"\nAnalyzing what short clustered entries share with their neighbors...")

    shared_tokens = Counter()
    shared_prefixes = Counter()
    shared_middles = Counter()
    shared_suffixes = Counter()

    for i in short_clustered:
        clf = classification[i]
        run_id = clf['run_id']

        # Find neighbors in the same run
        neighbors = []
        for j, jclf in classification.items():
            if jclf['run_id'] == run_id and j != i:
                neighbors.append(j)

        if not neighbors:
            continue

        my_tokens = set(entries[i]['tokens'])
        my_prefixes = set(extract_prefix(t) for t in entries[i]['tokens'])
        my_middles = set(extract_middle(t) for t in entries[i]['tokens'])
        my_suffixes = set(extract_suffix(t) for t in entries[i]['tokens'])

        for j in neighbors:
            their_tokens = set(entries[j]['tokens'])
            their_prefixes = set(extract_prefix(t) for t in entries[j]['tokens'])
            their_middles = set(extract_middle(t) for t in entries[j]['tokens'])
            their_suffixes = set(extract_suffix(t) for t in entries[j]['tokens'])

            for t in my_tokens & their_tokens:
                shared_tokens[t] += 1
            for p in my_prefixes & their_prefixes:
                if p:
                    shared_prefixes[p] += 1
            for m in my_middles & their_middles:
                if m:
                    shared_middles[m] += 1
            for s in my_suffixes & their_suffixes:
                if s:
                    shared_suffixes[s] += 1

    print(f"\nMost commonly shared tokens (short entries):")
    for token, count in shared_tokens.most_common(10):
        print(f"    {token}: {count}")

    print(f"\nMost commonly shared prefixes:")
    for prefix, count in shared_prefixes.most_common(8):
        print(f"    {prefix}: {count}")

    print(f"\nMost commonly shared MIDDLEs:")
    for middle, count in shared_middles.most_common(10):
        print(f"    {middle}: {count}")

    # Token overlap rate comparison
    print(f"\nVocabulary sharing patterns (short clustered entries):")

    token_overlaps = []
    prefix_overlaps = []
    middle_overlaps = []

    for i in short_clustered:
        clf = classification[i]
        run_id = clf['run_id']
        neighbors = [j for j, jclf in classification.items() if jclf['run_id'] == run_id and j != i]

        if not neighbors:
            continue

        my_tokens = set(entries[i]['tokens'])
        my_prefixes = set(extract_prefix(t) for t in entries[i]['tokens'])
        my_middles = set(extract_middle(t) for t in entries[i]['tokens'])

        for j in neighbors:
            their_tokens = set(entries[j]['tokens'])
            their_prefixes = set(extract_prefix(t) for t in entries[j]['tokens'])
            their_middles = set(extract_middle(t) for t in entries[j]['tokens'])

            if my_tokens and their_tokens:
                token_overlaps.append(len(my_tokens & their_tokens))
            if my_prefixes and their_prefixes:
                prefix_overlaps.append(len(my_prefixes & their_prefixes))
            if my_middles and their_middles:
                middle_overlaps.append(len(my_middles & their_middles))

    print(f"  Mean shared tokens per pair: {np.mean(token_overlaps):.2f}")
    print(f"  Mean shared prefixes per pair: {np.mean(prefix_overlaps):.2f}")
    print(f"  Mean shared MIDDLEs per pair: {np.mean(middle_overlaps):.2f}")


# =============================================================================
# ANALYSIS 3: WITHIN-RUN SIMILARITY DECAY
# =============================================================================

def analyze_within_run_decay(entries, classification, runs):
    """Does similarity decrease from run-start to run-end?"""
    print("\n" + "=" * 70)
    print("ANALYSIS 3: WITHIN-RUN SIMILARITY DECAY")
    print("=" * 70)

    # Only analyze runs of size 4+
    large_runs = [r for r in runs if len(r) >= 4]

    if not large_runs:
        print("No runs of size 4+ found.")
        return

    print(f"\nAnalyzing {len(large_runs)} runs of size 4+")

    # For each run, compute similarity at each position gap
    decay_by_gap = defaultdict(list)

    for run in large_runs:
        for i in range(len(run)):
            for j in range(i + 1, len(run)):
                gap = j - i
                sim = token_jaccard(entries[run[i]], entries[run[j]])
                decay_by_gap[gap].append(sim)

    print(f"\nMean Jaccard by position gap within runs:")
    print(f"{'Gap':<10} {'Mean J':<12} {'N pairs':<12}")
    print("-" * 35)

    for gap in sorted(decay_by_gap.keys()):
        if gap <= 6:
            values = decay_by_gap[gap]
            print(f"{gap:<10} {np.mean(values):<12.4f} {len(values):<12}")

    # Test for decay trend
    gaps = []
    means = []
    for gap in sorted(decay_by_gap.keys()):
        if gap <= 6 and len(decay_by_gap[gap]) >= 10:
            gaps.append(gap)
            means.append(np.mean(decay_by_gap[gap]))

    if len(gaps) >= 3:
        corr, p_value = stats.pearsonr(gaps, means)
        print(f"\nDecay correlation: r = {corr:.3f} (p = {p_value:.4f})")

        if corr < -0.5 and p_value < 0.05:
            print("-> SIGNIFICANT DECAY: Similarity decreases with distance within runs")
        elif corr > 0.3:
            print("-> NO DECAY: Similarity stable or increases within runs")
        else:
            print("-> WEAK/NO DECAY: No clear pattern")


# =============================================================================
# ANALYSIS 4: VOCABULARY COMPONENT SHARING
# =============================================================================

def analyze_component_sharing(entries, classification, runs):
    """What component type drives clustering - PREFIX, MIDDLE, or SUFFIX?"""
    print("\n" + "=" * 70)
    print("ANALYSIS 4: VOCABULARY COMPONENT SHARING")
    print("=" * 70)

    # For clustered pairs, decompose what's shared
    prefix_sharing = []
    middle_sharing = []
    suffix_sharing = []
    token_sharing = []

    for run in runs:
        for i in range(len(run) - 1):
            e1 = entries[run[i]]
            e2 = entries[run[i + 1]]

            t1 = set(e1['tokens'])
            t2 = set(e2['tokens'])
            p1 = set(extract_prefix(t) for t in e1['tokens'])
            p2 = set(extract_prefix(t) for t in e2['tokens'])
            m1 = set(extract_middle(t) for t in e1['tokens'])
            m2 = set(extract_middle(t) for t in e2['tokens'])
            s1 = set(extract_suffix(t) for t in e1['tokens'])
            s2 = set(extract_suffix(t) for t in e2['tokens'])

            p1.discard(None)
            p2.discard(None)
            m1.discard('')
            m2.discard('')
            s1.discard('')
            s2.discard('')

            token_sharing.append(jaccard(t1, t2))
            prefix_sharing.append(jaccard(p1, p2))
            middle_sharing.append(jaccard(m1, m2))
            suffix_sharing.append(jaccard(s1, s2))

    print(f"\nComponent Jaccard similarity for adjacent pairs in runs:")
    print(f"\n  {'Component':<15} {'Mean J':<12} {'Median J':<12}")
    print("  " + "-" * 40)
    print(f"  {'TOKEN':<15} {np.mean(token_sharing):<12.4f} {np.median(token_sharing):<12.4f}")
    print(f"  {'PREFIX':<15} {np.mean(prefix_sharing):<12.4f} {np.median(prefix_sharing):<12.4f}")
    print(f"  {'MIDDLE':<15} {np.mean(middle_sharing):<12.4f} {np.median(middle_sharing):<12.4f}")
    print(f"  {'SUFFIX':<15} {np.mean(suffix_sharing):<12.4f} {np.median(suffix_sharing):<12.4f}")

    # Compare to baseline (random pairs)
    print(f"\nComparing to random pairs (same section)...")

    random_token = []
    random_prefix = []
    random_middle = []
    random_suffix = []

    by_section = defaultdict(list)
    for i, e in enumerate(entries):
        by_section[e['section']].append(i)

    np.random.seed(42)
    for section, indices in by_section.items():
        if len(indices) < 10:
            continue
        for _ in range(min(500, len(indices) * 2)):
            i, j = np.random.choice(indices, 2, replace=False)
            if abs(i - j) > 3:  # Non-adjacent
                e1, e2 = entries[i], entries[j]

                t1 = set(e1['tokens'])
                t2 = set(e2['tokens'])
                p1 = set(extract_prefix(t) for t in e1['tokens'])
                p2 = set(extract_prefix(t) for t in e2['tokens'])
                m1 = set(extract_middle(t) for t in e1['tokens'])
                m2 = set(extract_middle(t) for t in e2['tokens'])
                s1 = set(extract_suffix(t) for t in e1['tokens'])
                s2 = set(extract_suffix(t) for t in e2['tokens'])

                p1.discard(None)
                p2.discard(None)
                m1.discard('')
                m2.discard('')
                s1.discard('')
                s2.discard('')

                random_token.append(jaccard(t1, t2))
                random_prefix.append(jaccard(p1, p2))
                random_middle.append(jaccard(m1, m2))
                random_suffix.append(jaccard(s1, s2))

    print(f"\n  {'Component':<15} {'Clustered':<12} {'Random':<12} {'Ratio':<10}")
    print("  " + "-" * 50)

    for name, clust, rand in [
        ('TOKEN', token_sharing, random_token),
        ('PREFIX', prefix_sharing, random_prefix),
        ('MIDDLE', middle_sharing, random_middle),
        ('SUFFIX', suffix_sharing, random_suffix)
    ]:
        c_mean = np.mean(clust)
        r_mean = np.mean(rand)
        ratio = c_mean / r_mean if r_mean > 0 else 0
        print(f"  {name:<15} {c_mean:<12.4f} {r_mean:<12.4f} {ratio:<10.2f}x")


# =============================================================================
# ANALYSIS 5: CLUSTER HOMOGENEITY
# =============================================================================

def analyze_cluster_homogeneity(entries, classification, runs):
    """Do runs share a dominant prefix family?"""
    print("\n" + "=" * 70)
    print("ANALYSIS 5: CLUSTER HOMOGENEITY (PREFIX DOMINANCE)")
    print("=" * 70)

    # For each run, compute prefix distribution
    run_stats = []

    for run_id, run in enumerate(runs):
        all_prefixes = []
        for idx in run:
            for t in entries[idx]['tokens']:
                p = extract_prefix(t)
                if p:
                    all_prefixes.append(p)

        if not all_prefixes:
            continue

        prefix_counts = Counter(all_prefixes)
        total = len(all_prefixes)
        dominant_prefix = prefix_counts.most_common(1)[0]
        dominance = dominant_prefix[1] / total

        # Count unique prefixes
        n_unique = len(prefix_counts)

        run_stats.append({
            'run_id': run_id,
            'run_size': len(run),
            'dominant_prefix': dominant_prefix[0],
            'dominance': dominance,
            'n_unique_prefixes': n_unique,
            'total_tokens': total
        })

    if not run_stats:
        print("No run statistics computed.")
        return

    dominances = [r['dominance'] for r in run_stats]
    n_uniques = [r['n_unique_prefixes'] for r in run_stats]

    print(f"\nRun-level prefix dominance statistics (n={len(run_stats)} runs):")
    print(f"  Mean dominance: {np.mean(dominances):.3f}")
    print(f"  Median dominance: {np.median(dominances):.3f}")
    print(f"  Min dominance: {min(dominances):.3f}")
    print(f"  Max dominance: {max(dominances):.3f}")

    print(f"\n  Mean unique prefixes per run: {np.mean(n_uniques):.2f}")
    print(f"  Median unique prefixes per run: {np.median(n_uniques):.0f}")

    # Distribution of dominance
    print(f"\nDominance distribution:")
    bins = [(0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0)]
    for low, high in bins:
        count = sum(1 for d in dominances if low < d <= high)
        pct = 100 * count / len(dominances)
        print(f"    {low:.1f}-{high:.1f}: {count} runs ({pct:.1f}%)")

    # Check if larger runs are more or less homogeneous
    print(f"\nDominance by run size:")
    size_groups = [(2, 2), (3, 3), (4, 5), (6, 20)]

    for min_size, max_size in size_groups:
        group = [r for r in run_stats if min_size <= r['run_size'] <= max_size]
        if group:
            mean_dom = np.mean([r['dominance'] for r in group])
            print(f"    Size {min_size}-{max_size}: mean dominance = {mean_dom:.3f} (n={len(group)})")


# =============================================================================
# ANALYSIS 6: RUN-SIZE EFFECTS
# =============================================================================

def analyze_run_size_effects(entries, classification, runs):
    """How do small vs large runs differ?"""
    print("\n" + "=" * 70)
    print("ANALYSIS 6: RUN-SIZE EFFECTS")
    print("=" * 70)

    # Split runs by size
    small_runs = [r for r in runs if len(r) == 2]
    medium_runs = [r for r in runs if 3 <= len(r) <= 4]
    large_runs = [r for r in runs if len(r) >= 5]

    print(f"\nRun size distribution:")
    print(f"  Size 2: {len(small_runs)} runs")
    print(f"  Size 3-4: {len(medium_runs)} runs")
    print(f"  Size 5+: {len(large_runs)} runs ({[len(r) for r in large_runs]})")

    # Compare entry characteristics by run size
    def run_entry_stats(run_list, name):
        if not run_list:
            return None

        all_entries = []
        for run in run_list:
            all_entries.extend(run)

        token_counts = [len(entries[i]['tokens']) for i in all_entries]
        prefix_counts = [len(set(extract_prefix(t) for t in entries[i]['tokens'])) for i in all_entries]

        # Within-run similarity
        within_sims = []
        for run in run_list:
            for i in range(len(run)):
                for j in range(i + 1, len(run)):
                    within_sims.append(token_jaccard(entries[run[i]], entries[run[j]]))

        return {
            'name': name,
            'n_runs': len(run_list),
            'n_entries': len(all_entries),
            'mean_tokens': np.mean(token_counts),
            'mean_prefixes': np.mean(prefix_counts),
            'mean_within_sim': np.mean(within_sims) if within_sims else 0
        }

    run_stats = []
    for runs_list, name in [(small_runs, 'Size 2'), (medium_runs, 'Size 3-4'), (large_runs, 'Size 5+')]:
        s = run_entry_stats(runs_list, name)
        if s:
            run_stats.append(s)

    print(f"\n{'Group':<12} {'Runs':<8} {'Entries':<10} {'Mean Tok':<12} {'Mean Pfx':<12} {'Within J':<12}")
    print("-" * 70)
    for s in run_stats:
        print(f"{s['name']:<12} {s['n_runs']:<8} {s['n_entries']:<10} {s['mean_tokens']:<12.1f} {s['mean_prefixes']:<12.2f} {s['mean_within_sim']:<12.4f}")

    # Check if there's a trend
    if len(run_stats) >= 2:
        sizes = [2, 3.5, 7][:len(run_stats)]  # Approximate centers
        within_sims = [s['mean_within_sim'] for s in run_stats]

        if len(sizes) >= 3:
            from scipy.stats import pearsonr as pr
            corr, p = pr(sizes, within_sims)
            print(f"\nWithin-similarity vs run size correlation: r = {corr:.3f} (p = {p:.4f})")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("EXTENDED CLUSTER ANALYSIS")
    print("=" * 70)
    print("\nFollowing up on cluster_characterization.py findings.")
    print("All analyses treat clusters as statistical phenomena, not entities.")

    print("\nLoading entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries")

    classification, runs, adj_j = classify_entries(entries, threshold=0.0)
    print(f"Classified entries into {len(runs)} runs")

    # Run all analyses
    analyze_section_p_anomaly(entries, classification)
    analyze_short_entry_clustering(entries, classification)
    analyze_within_run_decay(entries, classification, runs)
    analyze_component_sharing(entries, classification, runs)
    analyze_cluster_homogeneity(entries, classification, runs)
    analyze_run_size_effects(entries, classification, runs)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nSee detailed findings above for each analysis.")
    print("Key patterns to note:")
    print("  1. Section P anomaly characteristics")
    print("  2. What short entries share when they cluster")
    print("  3. Whether similarity decays within runs")
    print("  4. Which component (PREFIX/MIDDLE/SUFFIX) drives sharing")
    print("  5. Whether runs are prefix-homogeneous")
    print("  6. How run size affects characteristics")


if __name__ == '__main__':
    main()

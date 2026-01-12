"""
Currier A Modeling Data Preparation

Prepares comprehensive data for predictive modeling:
- Target 1: Token decomposition census (PREFIX x MIDDLE x SUFFIX)
- Target 2: Sister-pair feature matrix
- Target 3: Multiplicity distribution
- Target 4: Entry clustering sequence

Tier 4 - Exploratory
"""

import os
import json
from collections import defaultdict, Counter
import math

# Known prefixes and suffixes from CAS-MORPH phase
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SISTER_PAIRS = [('ch', 'sh'), ('ok', 'ot')]

# Extended suffixes for better coverage
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def load_currier_a_full():
    """Load Currier A tokens with full metadata (matches original CAS-MULT methodology)."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()  # lowercase like original
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    quire = parts[4].strip('"').strip() if len(parts) > 4 else ''
                    line_num = parts[11].strip('"').strip()
                    line_init = parts[13].strip('"').strip() if len(parts) > 13 else '0'
                    line_final = parts[14].strip('"').strip() if len(parts) > 14 else '0'

                    if token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section,
                            'quire': quire,
                            'line_num': line_num,
                            'line_init': line_init == '1',
                            'line_final': line_final == '1'
                        })

    return tokens


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        # No recognized suffix - take last 1-2 chars as suffix
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def prepare_token_census():
    """Target 1: Full token decomposition census."""
    print("=" * 60)
    print("TARGET 1: TOKEN DECOMPOSITION CENSUS")
    print("=" * 60)

    tokens = load_currier_a_full()

    # Decompose all tokens
    decomposed = []
    failed = []

    for t in tokens:
        prefix, middle, suffix = decompose_token(t['token'])
        if prefix:
            decomposed.append({
                **t,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })
        else:
            failed.append(t['token'])

    print(f"Total A tokens: {len(tokens)}")
    print(f"Decomposed: {len(decomposed)} ({100*len(decomposed)/len(tokens):.1f}%)")
    print(f"Failed: {len(failed)} ({100*len(failed)/len(tokens):.1f}%)")

    # Check what's failing
    failed_counter = Counter(failed)
    print(f"\nTop 20 failed tokens:")
    for token, count in failed_counter.most_common(20):
        print(f"  {token}: {count}")

    # Build probability tables
    prefix_counts = Counter(d['prefix'] for d in decomposed)
    middle_given_prefix = defaultdict(Counter)
    suffix_given_prefix_middle = defaultdict(Counter)

    for d in decomposed:
        middle_given_prefix[d['prefix']][d['middle']] += 1
        suffix_given_prefix_middle[(d['prefix'], d['middle'])][d['suffix']] += 1

    # Convert to probabilities
    total = len(decomposed)
    p_prefix = {p: c/total for p, c in prefix_counts.items()}

    p_middle_given_prefix = {}
    for prefix, middles in middle_given_prefix.items():
        total_p = sum(middles.values())
        p_middle_given_prefix[prefix] = {m: c/total_p for m, c in middles.items()}

    p_suffix_given_pm = {}
    for (prefix, middle), suffixes in suffix_given_prefix_middle.items():
        total_pm = sum(suffixes.values())
        p_suffix_given_pm[f"{prefix}|{middle}"] = {s: c/total_pm for s, c in suffixes.items()}

    census = {
        'total_tokens': len(tokens),
        'decomposed_tokens': len(decomposed),
        'coverage_rate': len(decomposed) / len(tokens),
        'unique_combinations': len(set((d['prefix'], d['middle'], d['suffix']) for d in decomposed)),
        'unique_middles': len(set(d['middle'] for d in decomposed)),
        'p_prefix': p_prefix,
        'p_middle_given_prefix': p_middle_given_prefix,
        'suffix_given_pm_sample': {k: v for k, v in list(p_suffix_given_pm.items())[:100]},
        'prefix_counts': dict(prefix_counts),
        'failed_tokens': dict(failed_counter.most_common(50))
    }

    return census, decomposed


def prepare_sister_pair_data(decomposed):
    """Target 2: Sister-pair feature matrix."""
    print("\n" + "=" * 60)
    print("TARGET 2: SISTER-PAIR FEATURE MATRIX")
    print("=" * 60)

    # Filter to sister-pair tokens
    ch_sh_tokens = [d for d in decomposed if d['prefix'] in ('ch', 'sh')]
    ok_ot_tokens = [d for d in decomposed if d['prefix'] in ('ok', 'ot')]

    print(f"ch/sh tokens: {len(ch_sh_tokens)}")
    print(f"ok/ot tokens: {len(ok_ot_tokens)}")

    # Build feature matrix for ch/sh
    features = []
    for i, d in enumerate(ch_sh_tokens):
        # Get preceding token if exists
        prev_prefix = None
        if i > 0 and ch_sh_tokens[i-1]['folio'] == d['folio']:
            prev_prefix = ch_sh_tokens[i-1]['prefix']

        features.append({
            'label': 1 if d['prefix'] == 'ch' else 0,  # 1=ch, 0=sh
            'middle': d['middle'],
            'suffix': d['suffix'],
            'section': d['section'],
            'quire': d['quire'],
            'line_init': d['line_init'],
            'prev_same': prev_prefix == d['prefix'] if prev_prefix else None,
            'prev_is_ch': prev_prefix == 'ch' if prev_prefix else None
        })

    # Calculate basic statistics
    ch_count = sum(1 for f in features if f['label'] == 1)
    sh_count = len(features) - ch_count

    # Section distribution
    section_dist = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for f in features:
        prefix = 'ch' if f['label'] == 1 else 'sh'
        section_dist[f['section']][prefix] += 1

    # Middle distribution (top 10)
    middle_dist = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for f in features:
        prefix = 'ch' if f['label'] == 1 else 'sh'
        middle_dist[f['middle']][prefix] += 1

    top_middles = sorted(middle_dist.items(), key=lambda x: x[1]['ch']+x[1]['sh'], reverse=True)[:20]

    print(f"\nch: {ch_count} ({100*ch_count/len(features):.1f}%)")
    print(f"sh: {sh_count} ({100*sh_count/len(features):.1f}%)")

    print("\nSection distribution (ch:sh):")
    for section in sorted(section_dist.keys()):
        d = section_dist[section]
        total = d['ch'] + d['sh']
        print(f"  {section}: {d['ch']}:{d['sh']} ({100*d['ch']/total:.0f}%:{100*d['sh']/total:.0f}%)")

    print("\nTop 10 MIDDLEs (ch:sh):")
    for middle, counts in top_middles[:10]:
        total = counts['ch'] + counts['sh']
        pct_ch = 100 * counts['ch'] / total if total > 0 else 0
        print(f"  '{middle}': {counts['ch']}:{counts['sh']} ({pct_ch:.0f}% ch)")

    sister_data = {
        'pair': 'ch_sh',
        'total_samples': len(features),
        'ch_count': ch_count,
        'sh_count': sh_count,
        'baseline_accuracy': max(ch_count, sh_count) / len(features),
        'section_distribution': {k: dict(v) for k, v in section_dist.items()},
        'middle_distribution': {k: dict(v) for k, v in top_middles[:50]},
        'features_sample': features[:100]
    }

    return sister_data, features


def get_prefix(token):
    """Extract prefix from token."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return 'OTHER'


def prepare_multiplicity_data():
    """Target 3: Multiplicity distribution from entries."""
    print("\n" + "=" * 60)
    print("TARGET 3: MULTIPLICITY DISTRIBUTION")
    print("=" * 60)

    # Load raw data to identify entries
    # Entries in Currier A are typically line-bounded
    tokens = load_currier_a_full()

    # Group by folio + line to get entries
    entries = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line_num'])
        entries[key].append(t['token'])

    print(f"Total entries (folio+line): {len(entries)}")

    # Detect repetition patterns using PREFIX sequences
    def detect_prefix_repetition(token_list):
        """Detect if entry shows PREFIX-block repetition."""
        if len(token_list) < 2:
            return 1, None

        # Convert to prefix sequence
        prefix_seq = [get_prefix(t) for t in token_list]

        # Try to find repeating prefix pattern
        for unit_size in range(1, len(prefix_seq)//2 + 1):
            unit = prefix_seq[:unit_size]
            reps = 1
            pos = unit_size
            while pos + unit_size <= len(prefix_seq):
                if prefix_seq[pos:pos+unit_size] == unit:
                    reps += 1
                    pos += unit_size
                else:
                    break
            if reps >= 2 and pos == len(prefix_seq):
                return reps, tuple(unit)

        return 1, None

    # Also try similarity-based detection (Jaccard of adjacent windows)
    def detect_similarity_repetition(token_list):
        """Detect repetition via token similarity between halves."""
        if len(token_list) < 4:
            return 1, 0.0

        # Try different block sizes
        for block_size in range(1, len(token_list)//2 + 1):
            blocks = []
            for i in range(0, len(token_list), block_size):
                if i + block_size <= len(token_list):
                    blocks.append(set(token_list[i:i+block_size]))

            if len(blocks) < 2:
                continue

            # Check if blocks are similar (high Jaccard)
            similarities = []
            for i in range(len(blocks) - 1):
                inter = len(blocks[i] & blocks[i+1])
                union = len(blocks[i] | blocks[i+1])
                if union > 0:
                    similarities.append(inter / union)

            if similarities and sum(similarities)/len(similarities) > 0.5:
                return len(blocks), sum(similarities)/len(similarities)

        return 1, 0.0

    # Use original CAS-MULT methodology with tolerance
    def find_repeating_blocks(tokens):
        """Find repeating block pattern with scribal variation tolerance."""
        n = len(tokens)
        if n < 4:  # Need at least 4 tokens for 2x2 repetition
            return tokens, 1

        # Try different block sizes
        for block_size in range(1, n // 2 + 1):
            if n % block_size == 0:
                block = tokens[:block_size]
                count = n // block_size

                # Verify all repetitions match (allow 20% mismatch)
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break

                if matches and count >= 2:
                    return block, count

        # Try non-exact divisions
        for block_size in range(2, n // 2 + 1):
            block = tokens[:block_size]
            count = 1
            i = block_size

            while i + block_size <= n:
                chunk = tokens[i:i + block_size]
                mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                if mismatches <= len(block) * 0.25:  # 25% tolerance
                    count += 1
                    i += block_size
                else:
                    break

            if count >= 2:
                return block, count

        return tokens, 1

    # Analyze each entry for repetition
    repetition_counts = Counter()
    entries_with_reps = []
    block_sizes = Counter()

    for (folio, line), token_list in entries.items():
        block, reps = find_repeating_blocks(token_list)
        repetition_counts[reps] += 1
        if reps >= 2:
            block_sizes[len(block)] += 1
            entries_with_reps.append({
                'folio': folio,
                'line': line,
                'reps': reps,
                'block': block,
                'block_size': len(block),
                'tokens': token_list
            })

    # Distribution
    total_entries = len(entries)
    rep_entries = sum(c for r, c in repetition_counts.items() if r >= 2)

    print(f"\nRepetition distribution:")
    for reps in sorted(repetition_counts.keys()):
        count = repetition_counts[reps]
        print(f"  {reps}x: {count} ({100*count/total_entries:.1f}%)")

    print(f"\nEntries with repetition (2x+): {rep_entries} ({100*rep_entries/total_entries:.1f}%)")

    if entries_with_reps:
        mean_reps = sum(e['reps'] for e in entries_with_reps) / len(entries_with_reps)
        print(f"Mean repetition (among repeaters): {mean_reps:.2f}x")

    print(f"\nBlock size distribution:")
    for size in sorted(block_sizes.keys())[:15]:
        print(f"  {size} tokens: {block_sizes[size]} entries")

    # Section breakdown
    section_reps = defaultdict(Counter)
    for e in entries_with_reps:
        # Get section from first token of entry
        for t in load_currier_a_full():
            if t['folio'] == e['folio'] and t['line_num'] == e['line']:
                section_reps[t['section']][e['reps']] += 1
                break

    print("\nSection breakdown (reps >= 2):")
    for section in sorted(section_reps.keys()):
        dist = section_reps[section]
        total = sum(dist.values())
        mean_reps = sum(r*c for r, c in dist.items()) / total if total > 0 else 0
        print(f"  {section}: {total} entries, mean reps = {mean_reps:.2f}")

    multiplicity_data = {
        'total_entries': total_entries,
        'entries_with_repetition': rep_entries,
        'repetition_rate': rep_entries / total_entries,
        'distribution': dict(repetition_counts),
        'mean_reps_overall': sum(r*c for r, c in repetition_counts.items()) / total_entries,
        'section_breakdown': {k: dict(v) for k, v in section_reps.items()},
        'examples': entries_with_reps[:20]
    }

    return multiplicity_data


def prepare_clustering_data():
    """Target 4: Entry clustering sequence."""
    print("\n" + "=" * 60)
    print("TARGET 4: ENTRY CLUSTERING SEQUENCE")
    print("=" * 60)

    tokens = load_currier_a_full()

    # Group by folio + line to get entries
    entries = defaultdict(set)
    entry_order = []  # Maintain order
    seen = set()

    for t in tokens:
        key = (t['folio'], t['line_num'], t['section'])
        entries[key].add(t['token'])
        if key not in seen:
            seen.add(key)
            entry_order.append(key)

    print(f"Total entries: {len(entry_order)}")

    # Calculate vocabulary overlap between adjacent entries
    overlaps = []
    for i in range(len(entry_order) - 1):
        e1 = entries[entry_order[i]]
        e2 = entries[entry_order[i+1]]

        # Jaccard similarity
        intersection = len(e1 & e2)
        union = len(e1 | e2)
        jaccard = intersection / union if union > 0 else 0

        overlaps.append({
            'idx': i,
            'folio1': entry_order[i][0],
            'folio2': entry_order[i+1][0],
            'section1': entry_order[i][2],
            'section2': entry_order[i+1][2],
            'jaccard': jaccard,
            'same_folio': entry_order[i][0] == entry_order[i+1][0]
        })

    # Binary classification: clustered (J > 0) vs singleton (J = 0)
    clustered_threshold = 0.0  # Any overlap = clustered
    binary_sequence = [1 if o['jaccard'] > clustered_threshold else 0 for o in overlaps]

    # Calculate transition counts
    transitions = {'00': 0, '01': 0, '10': 0, '11': 0}
    for i in range(len(binary_sequence) - 1):
        key = f"{binary_sequence[i]}{binary_sequence[i+1]}"
        transitions[key] += 1

    # Autocorrelation
    n = len(binary_sequence)
    mean = sum(binary_sequence) / n
    var = sum((x - mean)**2 for x in binary_sequence) / n
    if var > 0:
        autocorr = sum((binary_sequence[i] - mean) * (binary_sequence[i+1] - mean)
                      for i in range(n-1)) / ((n-1) * var)
    else:
        autocorr = 0

    # Run-length distribution
    runs = []
    current_run = 1
    current_val = binary_sequence[0] if binary_sequence else 0
    for i in range(1, len(binary_sequence)):
        if binary_sequence[i] == current_val:
            current_run += 1
        else:
            runs.append((current_val, current_run))
            current_val = binary_sequence[i]
            current_run = 1
    if binary_sequence:
        runs.append((current_val, current_run))

    run_lengths = Counter(r[1] for r in runs if r[0] == 1)  # Clustered runs

    clustered_count = sum(binary_sequence)
    singleton_count = len(binary_sequence) - clustered_count

    print(f"\nClustered (J>0): {clustered_count} ({100*clustered_count/len(binary_sequence):.1f}%)")
    print(f"Singleton (J=0): {singleton_count} ({100*singleton_count/len(binary_sequence):.1f}%)")
    print(f"\nTransition counts:")
    for k, v in transitions.items():
        print(f"  {k[0]}->{k[1]}: {v}")
    print(f"\nAutocorrelation: {autocorr:.3f}")

    print(f"\nClustered run-length distribution:")
    for length in sorted(run_lengths.keys()):
        print(f"  length {length}: {run_lengths[length]}")

    clustering_data = {
        'total_transitions': len(binary_sequence),
        'clustered_count': clustered_count,
        'singleton_count': singleton_count,
        'clustered_rate': clustered_count / len(binary_sequence),
        'transitions': transitions,
        'autocorrelation': autocorr,
        'run_length_distribution': dict(run_lengths),
        'mean_run_length': sum(l*c for l, c in run_lengths.items()) / sum(run_lengths.values()) if run_lengths else 0,
        'binary_sequence_sample': binary_sequence[:200],
        'overlaps_sample': overlaps[:50]
    }

    return clustering_data


def main():
    """Prepare all modeling data."""

    # Target 1: Token census
    census, decomposed = prepare_token_census()

    # Target 2: Sister-pair features
    sister_data, features = prepare_sister_pair_data(decomposed)

    # Target 3: Multiplicity
    multiplicity_data = prepare_multiplicity_data()

    # Target 4: Clustering
    clustering_data = prepare_clustering_data()

    # Save all data
    output = {
        'target_1_token_census': census,
        'target_2_sister_pairs': sister_data,
        'target_3_multiplicity': multiplicity_data,
        'target_4_clustering': clustering_data
    }

    output_path = r'C:\git\voynich\results\currier_a_modeling_data.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"All data saved to: {output_path}")
    print("=" * 60)

    return output


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
PRE-REGISTERED TEST: Low-Frequency MIDDLE Hazard Correlation

HYPOTHESIS: Low-frequency MIDDLEs (bottom 3 quartiles by token frequency)
from clustered A entries correlate with higher B hazard, independent of
token frequency effects.

BINARY OUTCOME:
- PASS: p < 0.05 AND rho > 0 after frequency matching
- FAIL: Otherwise

This test is pre-registered before running. No additional degrees of freedom.
"""
import json
import sys
from collections import defaultdict, Counter
from enum import Enum
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'
B_SIGNATURES_FILE = 'C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json'


class EntryClass(Enum):
    SINGLETON = "SINGLETON"
    CLUSTERED = "CLUSTERED"


def load_currier_a_entries():
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
                    if current_entry is not None:
                        entries.append(current_entry)
                    current_entry = {'key': key, 'folio': folio, 'section': section,
                                     'line': line_num, 'tokens': []}
                current_entry['tokens'].append(word)
        if current_entry is not None:
            entries.append(current_entry)
    return entries


def load_currier_b_data():
    folio_tokens = defaultdict(list)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                if language == 'B':
                    folio_tokens[folio].append(word)
    return folio_tokens


def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def classify_entries(entries, threshold=0.0):
    n = len(entries)
    adj_j = []
    for i in range(n - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            j = jaccard(set(entries[i]['tokens']), set(entries[i+1]['tokens']))
            adj_j.append(j)
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
    run_indices = set()
    for run in runs:
        run_indices.update(run)

    for i in range(n):
        if i in run_indices:
            classification[i] = EntryClass.CLUSTERED
        else:
            classification[i] = EntryClass.SINGLETON

    return classification


def extract_middle(token):
    """Extract MIDDLE component from token."""
    result = parse_currier_a_token(token)
    if result.middle:
        return result.middle
    return None


def main():
    print("=" * 70)
    print("PRE-REGISTERED TEST: Low-Frequency MIDDLE Hazard Correlation")
    print("=" * 70)
    print("\nHYPOTHESIS: Low-frequency MIDDLEs from clustered A entries")
    print("correlate with higher B hazard, independent of token frequency.")
    print("\nBINARY OUTCOME: PASS if p < 0.05 AND rho > 0; FAIL otherwise")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    entries = load_currier_a_entries()
    classification = classify_entries(entries)
    b_folios = load_currier_b_data()

    with open(B_SIGNATURES_FILE, 'r') as f:
        b_data = json.load(f)
        b_signatures = b_data['signatures']

    # Extract MIDDLEs and their frequencies
    print("\nExtracting MIDDLEs...")
    middle_freq = Counter()
    middle_source = defaultdict(set)  # middle -> {'clustered', 'singleton'}

    for i, entry in enumerate(entries):
        is_clustered = classification[i] == EntryClass.CLUSTERED
        source = 'clustered' if is_clustered else 'singleton'
        for token in entry['tokens']:
            middle = extract_middle(token)
            if middle:
                middle_freq[middle] += 1
                middle_source[middle].add(source)

    total_middles = len(middle_freq)
    print(f"  Total unique MIDDLEs: {total_middles}")

    # Determine frequency quartiles
    freqs = list(middle_freq.values())
    q75 = np.percentile(freqs, 75)
    print(f"  75th percentile frequency: {q75}")

    # Get LOW-FREQUENCY MIDDLEs (bottom 3 quartiles)
    low_freq_middles = {m for m, f in middle_freq.items() if f <= q75}
    print(f"  Low-frequency MIDDLEs (f <= {q75}): {len(low_freq_middles)}")

    # Get exclusive vocabularies among low-frequency MIDDLEs
    clustered_low = {m for m in low_freq_middles
                     if middle_source[m] == {'clustered'}}
    singleton_low = {m for m in low_freq_middles
                     if middle_source[m] == {'singleton'}}

    print(f"\n  Clustered-exclusive low-freq MIDDLEs: {len(clustered_low)}")
    print(f"  Singleton-exclusive low-freq MIDDLEs: {len(singleton_low)}")

    if len(clustered_low) < 50 or len(singleton_low) < 50:
        print("\n  INSUFFICIENT DATA for robust test")
        print("\n  RESULT: INCONCLUSIVE (cannot run test)")
        return

    # Frequency-match the samples
    freq_bins = defaultdict(list)
    for m in singleton_low:
        freq_bins[middle_freq[m]].append(m)

    matched_singleton = set()
    matched_clustered = set()

    for m in clustered_low:
        freq = middle_freq[m]
        # Try exact match, then adjacent
        for delta in [0, 1, -1, 2, -2]:
            adj_freq = freq + delta
            if freq_bins[adj_freq]:
                matched_m = freq_bins[adj_freq].pop()
                matched_singleton.add(matched_m)
                matched_clustered.add(m)
                break

    print(f"\n  Frequency-matched pairs: {len(matched_clustered)}")

    if len(matched_clustered) < 50:
        print("\n  INSUFFICIENT MATCHED DATA")
        print("\n  RESULT: INCONCLUSIVE")
        return

    # Verify frequency matching
    mc_freqs = [middle_freq[m] for m in matched_clustered]
    ms_freqs = [middle_freq[m] for m in matched_singleton]
    print(f"  Matched clustered freq: mean={np.mean(mc_freqs):.2f}")
    print(f"  Matched singleton freq: mean={np.mean(ms_freqs):.2f}")

    # Now compute correlation with B hazard using ONLY matched low-freq MIDDLEs
    print("\n" + "=" * 70)
    print("RUNNING TEST")
    print("=" * 70)

    folio_scores = []

    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue

        # Extract MIDDLEs from B folio
        folio_middles = set()
        for token in tokens:
            m = extract_middle(token)
            if m:
                folio_middles.add(m)

        # Count matched low-freq MIDDLEs by source
        from_clustered = len(folio_middles & matched_clustered)
        from_singleton = len(folio_middles & matched_singleton)
        total = from_clustered + from_singleton

        if total == 0:
            continue

        ratio = from_clustered / total
        hazard = b_signatures[folio]['hazard_metrics']['hazard_density']

        folio_scores.append({'folio': folio, 'ratio': ratio, 'hazard': hazard})

    print(f"\n  Folios with matched low-freq MIDDLEs: {len(folio_scores)}")

    if len(folio_scores) < 20:
        print("\n  INSUFFICIENT FOLIO DATA")
        print("\n  RESULT: INCONCLUSIVE")
        return

    # Compute correlation
    ratios = [f['ratio'] for f in folio_scores]
    hazards = [f['hazard'] for f in folio_scores]

    rho, p = stats.spearmanr(ratios, hazards)

    print(f"\n  Spearman rho = {rho:.4f}")
    print(f"  p-value = {p:.4f}")

    # Binary outcome
    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)

    if p < 0.05 and rho > 0:
        print("\n  *** PASS ***")
        print(f"\n  Low-frequency MIDDLEs from clustered A entries")
        print(f"  correlate with higher B hazard (rho={rho:.3f}, p={p:.4f})")
        print(f"\n  This survives frequency matching.")
        print(f"  Strengthens failure-memory interpretation.")
        result = "PASS"
    else:
        print("\n  *** FAIL ***")
        print(f"\n  Low-frequency MIDDLEs do NOT show significant correlation")
        print(f"  after frequency matching (rho={rho:.3f}, p={p:.4f})")
        print(f"\n  Failure-memory hypothesis downgraded.")
        print(f"  Interpret A as complexity-aligned, not risk-encoding.")
        result = "FAIL"

    # Save result
    output = {
        'test': 'preregistered_low_freq_middle',
        'hypothesis': 'Low-freq MIDDLEs from clustered A correlate with B hazard',
        'binary_criterion': 'p < 0.05 AND rho > 0',
        'n_matched_middles': len(matched_clustered),
        'n_folios': len(folio_scores),
        'spearman_rho': rho,
        'p_value': p,
        'result': result
    }

    output_file = 'C:/git/voynich/phases/exploration/preregistered_test_result.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Result saved to: {output_file}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Validation tests for pharma label constraint.

Tests:
1. Is the 60/43 PP/RI ratio different from baseline Currier A?
2. Do labeled illustrations cluster by MIDDLE incompatibility (C475)?
3. Statistical significance of 50% overlap with Currier A
"""

import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent

def extract_middle(token):
    """Extract MIDDLE from token."""
    prefixes = ['qok', 'qot', 'cph', 'cth', 'pch', 'tch', 'ckh', 'qo', 'ch', 'sh',
                'ok', 'ot', 'op', 'ol', 'or', 'da', 'sa', 'so', 'ct', 'yk', 'do',
                'ar', 'po', 'oe', 'os', 'al', 'of', 'cp', 'ko', 'yd', 'sy']
    suffixes = ['aiin', 'oiin', 'iin', 'ain', 'dy', 'hy', 'ky', 'ly', 'my', 'ny',
                'ry', 'sy', 'ty', 'am', 'an', 'al', 'ar', 'ol', 'or', 'y', 's',
                'g', 'd', 'l', 'r', 'n', 'm']

    middle = str(token).strip()
    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            middle = middle[len(p):]
            break
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            middle = middle[:-len(s)]
            break
    return middle if middle and middle != token else token

def load_pharma_labels_with_context():
    """Load pharma labels with folio/row context."""
    pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
    labels = []

    for json_file in pharma_dir.glob('*_mapping.json'):
        with open(json_file) as f:
            data = json.load(f)

        folio = data.get('folio', json_file.stem)

        if 'groups' in data:
            for group in data['groups']:
                row = group.get('row', group.get('placement', '?'))

                jar = group.get('jar')
                if jar and isinstance(jar, str):
                    labels.append({'token': jar, 'folio': folio, 'row': row, 'type': 'jar'})

                for key in ['roots', 'leaves', 'labels']:
                    if key in group:
                        for item in group[key]:
                            if isinstance(item, dict):
                                token = item.get('token', '')
                            else:
                                token = item
                            if token and isinstance(token, str) and '*' not in token:
                                labels.append({'token': token, 'folio': folio, 'row': row, 'type': 'content'})

        if 'labels' in data and 'groups' not in data:
            for label in data['labels']:
                if isinstance(label, dict):
                    token = label.get('token', '')
                else:
                    token = label
                if token and isinstance(token, str) and '*' not in token:
                    labels.append({'token': token, 'folio': folio, 'row': '?', 'type': 'content'})

    return labels

if __name__ == '__main__':
    print("=" * 70)
    print("PHARMA LABEL CONSTRAINT VALIDATION")
    print("=" * 70)

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    df_text = df[~df['placement'].str.startswith('L', na=False)]

    a_tokens = set(df_text[df_text['language'] == 'A']['word'].dropna().unique())
    b_tokens = set(df_text[df_text['language'] == 'B']['word'].dropna().unique())

    pp_tokens = a_tokens & b_tokens
    ri_tokens = a_tokens - b_tokens

    print(f"\nBaseline Currier A vocabulary:")
    print(f"  Total unique tokens: {len(a_tokens)}")
    print(f"  PP (shared with B): {len(pp_tokens)} ({100*len(pp_tokens)/len(a_tokens):.1f}%)")
    print(f"  RI (A-exclusive): {len(ri_tokens)} ({100*len(ri_tokens)/len(a_tokens):.1f}%)")

    # Load pharma labels
    labels = load_pharma_labels_with_context()
    label_tokens = set(l['token'] for l in labels)

    labels_in_a = label_tokens & a_tokens
    labels_pp = label_tokens & pp_tokens
    labels_ri = label_tokens & ri_tokens

    print(f"\nPharma labels:")
    print(f"  Total unique: {len(label_tokens)}")
    print(f"  In Currier A: {len(labels_in_a)} ({100*len(labels_in_a)/len(label_tokens):.1f}%)")
    print(f"  As PP: {len(labels_pp)} ({100*len(labels_pp)/len(labels_in_a):.1f}% of A-matches)")
    print(f"  As RI: {len(labels_ri)} ({100*len(labels_ri)/len(labels_in_a):.1f}% of A-matches)")

    # =========================================================================
    # TEST 1: PP/RI Ratio Comparison
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: PP/RI RATIO COMPARISON")
    print("=" * 70)

    # Baseline ratio
    baseline_pp_ratio = len(pp_tokens) / len(a_tokens)
    baseline_ri_ratio = len(ri_tokens) / len(a_tokens)

    # Label ratio (among those in A)
    label_pp_ratio = len(labels_pp) / len(labels_in_a) if labels_in_a else 0
    label_ri_ratio = len(labels_ri) / len(labels_in_a) if labels_in_a else 0

    print(f"\nBaseline Currier A: {100*baseline_pp_ratio:.1f}% PP, {100*baseline_ri_ratio:.1f}% RI")
    print(f"Pharma labels:      {100*label_pp_ratio:.1f}% PP, {100*label_ri_ratio:.1f}% RI")

    # Chi-square test
    # Observed: labels_pp, labels_ri
    # Expected based on baseline proportions
    expected_pp = len(labels_in_a) * baseline_pp_ratio
    expected_ri = len(labels_in_a) * baseline_ri_ratio

    observed = [len(labels_pp), len(labels_ri)]
    expected = [expected_pp, expected_ri]

    chi2, p_value = stats.chisquare(observed, expected)

    print(f"\nChi-square test:")
    print(f"  Observed: PP={len(labels_pp)}, RI={len(labels_ri)}")
    print(f"  Expected: PP={expected_pp:.1f}, RI={expected_ri:.1f}")
    print(f"  Chi-square = {chi2:.3f}, p = {p_value:.6f}")

    if p_value < 0.05:
        direction = "MORE PP" if label_pp_ratio > baseline_pp_ratio else "MORE RI"
        print(f"  RESULT: Significant difference - labels are {direction} than baseline")
    else:
        print(f"  RESULT: No significant difference from baseline")

    # =========================================================================
    # TEST 2: MIDDLE Incompatibility Clustering
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: MIDDLE INCOMPATIBILITY CLUSTERING")
    print("=" * 70)

    # Extract MIDDLEs for labels
    label_middles = []
    for l in labels:
        mid = extract_middle(l['token'])
        if mid and len(mid) >= 2:
            label_middles.append({
                'token': l['token'],
                'middle': mid,
                'folio': l['folio'],
                'row': l['row']
            })

    print(f"\nLabels with extractable MIDDLEs: {len(label_middles)}")

    # Group by folio
    by_folio = defaultdict(list)
    for lm in label_middles:
        by_folio[lm['folio']].append(lm['middle'])

    # Compute within-folio MIDDLE similarity (Jaccard of character sets)
    def middle_similarity(m1, m2):
        """Character-level Jaccard similarity."""
        s1, s2 = set(m1), set(m2)
        if not s1 or not s2:
            return 0
        return len(s1 & s2) / len(s1 | s2)

    within_folio_sims = []
    for folio, middles in by_folio.items():
        if len(middles) >= 2:
            for i in range(len(middles)):
                for j in range(i+1, len(middles)):
                    sim = middle_similarity(middles[i], middles[j])
                    within_folio_sims.append(sim)

    # Between-folio similarity (random pairs from different folios)
    between_folio_sims = []
    folio_list = list(by_folio.keys())
    for _ in range(len(within_folio_sims)):  # Same number of comparisons
        f1, f2 = random.sample(folio_list, 2)
        m1 = random.choice(by_folio[f1])
        m2 = random.choice(by_folio[f2])
        sim = middle_similarity(m1, m2)
        between_folio_sims.append(sim)

    mean_within = np.mean(within_folio_sims) if within_folio_sims else 0
    mean_between = np.mean(between_folio_sims) if between_folio_sims else 0

    print(f"\nWithin-folio MIDDLE similarity: {mean_within:.3f} (n={len(within_folio_sims)})")
    print(f"Between-folio MIDDLE similarity: {mean_between:.3f} (n={len(between_folio_sims)})")
    print(f"Ratio: {mean_within/mean_between:.2f}x" if mean_between > 0 else "N/A")

    # Mann-Whitney U test
    if within_folio_sims and between_folio_sims:
        u_stat, u_p = stats.mannwhitneyu(within_folio_sims, between_folio_sims, alternative='greater')
        print(f"\nMann-Whitney U test (within > between):")
        print(f"  U = {u_stat:.1f}, p = {u_p:.6f}")

        if u_p < 0.05:
            print(f"  RESULT: Significant clustering - labels on same folio have MORE similar MIDDLEs")
        else:
            print(f"  RESULT: No significant clustering")

    # =========================================================================
    # TEST 3: Statistical Significance of 50% Overlap
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: SIGNIFICANCE OF 50% OVERLAP WITH CURRIER A")
    print("=" * 70)

    # Null hypothesis: labels are random tokens from the full vocabulary
    # What's the probability of 50%+ being in Currier A by chance?

    # Get full vocabulary (all unique tokens in manuscript)
    all_tokens = set(df_text['word'].dropna().unique())
    print(f"\nFull manuscript vocabulary: {len(all_tokens)} unique tokens")
    print(f"Currier A tokens: {len(a_tokens)} ({100*len(a_tokens)/len(all_tokens):.1f}% of total)")

    # Permutation test
    n_labels = len(label_tokens)
    observed_overlap = len(labels_in_a)
    observed_ratio = observed_overlap / n_labels

    n_permutations = 10000
    random_overlaps = []

    all_tokens_list = list(all_tokens)
    for _ in range(n_permutations):
        random_sample = set(random.sample(all_tokens_list, min(n_labels, len(all_tokens_list))))
        overlap = len(random_sample & a_tokens)
        random_overlaps.append(overlap / len(random_sample))

    mean_random = np.mean(random_overlaps)
    std_random = np.std(random_overlaps)
    p_permutation = sum(1 for r in random_overlaps if r >= observed_ratio) / n_permutations

    print(f"\nObserved overlap: {observed_overlap}/{n_labels} = {100*observed_ratio:.1f}%")
    print(f"Random baseline: {100*mean_random:.1f}% ± {100*std_random:.1f}%")
    print(f"Z-score: {(observed_ratio - mean_random) / std_random:.2f}")
    print(f"Permutation p-value: {p_permutation:.6f}")

    if p_permutation < 0.05:
        print(f"  RESULT: Significant - labels overlap with Currier A MORE than random")
    else:
        print(f"  RESULT: Not significant - overlap could be random")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    results = {
        'test1_pp_ri_ratio': {
            'baseline_pp': baseline_pp_ratio,
            'label_pp': label_pp_ratio,
            'chi2': chi2,
            'p_value': p_value,
            'significant': p_value < 0.05
        },
        'test2_middle_clustering': {
            'within_folio_sim': mean_within,
            'between_folio_sim': mean_between,
            'ratio': mean_within / mean_between if mean_between > 0 else None,
            'p_value': u_p if within_folio_sims and between_folio_sims else None,
            'significant': u_p < 0.05 if within_folio_sims and between_folio_sims else False
        },
        'test3_overlap_significance': {
            'observed_ratio': observed_ratio,
            'random_mean': mean_random,
            'z_score': (observed_ratio - mean_random) / std_random,
            'p_value': p_permutation,
            'significant': p_permutation < 0.05
        }
    }

    print(f"""
TEST 1 - PP/RI Ratio:
  Baseline: {100*baseline_pp_ratio:.1f}% PP
  Labels:   {100*label_pp_ratio:.1f}% PP
  p = {p_value:.4f} → {"SIGNIFICANT" if p_value < 0.05 else "NOT SIGNIFICANT"}

TEST 2 - MIDDLE Clustering:
  Within-folio similarity:  {mean_within:.3f}
  Between-folio similarity: {mean_between:.3f}
  Ratio: {mean_within/mean_between:.2f}x
  p = {u_p:.4f} → {"SIGNIFICANT" if u_p < 0.05 else "NOT SIGNIFICANT"}

TEST 3 - Overlap Significance:
  Observed: {100*observed_ratio:.1f}% in Currier A
  Random:   {100*mean_random:.1f}%
  Z = {(observed_ratio - mean_random) / std_random:.2f}
  p = {p_permutation:.4f} → {"SIGNIFICANT" if p_permutation < 0.05 else "NOT SIGNIFICANT"}

OVERALL: {"CONSTRAINT VALIDATED" if all([p_value < 0.05 or label_pp_ratio > 0.5, u_p < 0.05 if 'u_p' in dir() else True, p_permutation < 0.05]) else "NEEDS REVIEW"}
""")

    # Save results
    with open(PROJECT_ROOT / 'results' / 'pharma_label_validation.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to results/pharma_label_validation.json")

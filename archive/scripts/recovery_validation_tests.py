"""
Recovery Validation Tests (R-1 through R-5)

Validates that the damaged token recovery system improves hygiene
without changing structural conclusions.

Tests:
  R-1: Frequency Stability (global)
  R-2: Grammar Coverage Stability (Currier B)
  R-3: HT Morphology Stability
  R-4: Orphan Rate Reduction (expected to change)
  R-5: Recovery Confidence Thresholding (sensitivity)
"""

import sys
from pathlib import Path
from collections import Counter
from math import log2
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib import load_transcription

# Known grammar prefixes/suffixes for classification
B_GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'ls']
B_GRAMMAR_SUFFIXES = ['aiin', 'ain', 'dy', 'edy', 'eedy', 'ey', 'eey', 'y', 'ol', 'or', 'ar', 'al', 'o', 'hy', 'chy']
HT_PREFIXES = ['yk', 'yp', 'yt', 'yc', 'yd', 'ys', 'op', 'oc', 'oe', 'of', 'pc', 'tc', 'dc', 'kc', 'sc', 'fc', 'sa', 'so', 'ka', 'ke', 'ko', 'ta', 'te', 'to', 'po', 'do', 'lo', 'ro']
HT_SUFFIXES = ['dy', 'ey', 'hy', 'ry', 'ly', 'ty', 'sy', 'ky', 'ny', 'my', 'in', 'ir', 'im', 'il', 'ar', 'or', 'er', 'al', 'ol', 'el', 'am', 'om', 'an', 'on', 'as', 'os', 'es']

def spearman_rank_correlation(ranks1, ranks2):
    """Compute Spearman rank correlation between two rank lists."""
    n = len(ranks1)
    if n != len(ranks2):
        # Use intersection
        common = set(ranks1.keys()) & set(ranks2.keys())
        n = len(common)
        if n == 0:
            return 0
        d_squared = sum((ranks1[k] - ranks2[k])**2 for k in common)
    else:
        d_squared = sum((ranks1.get(k, n) - ranks2.get(k, n))**2 for k in set(ranks1.keys()) | set(ranks2.keys()))

    return 1 - (6 * d_squared) / (n * (n**2 - 1))

def jsd_divergence(p, q):
    """Jensen-Shannon divergence between two distributions."""
    # Normalize
    total_p = sum(p.values())
    total_q = sum(q.values())

    all_keys = set(p.keys()) | set(q.keys())

    # Add small epsilon to avoid log(0)
    eps = 1e-10

    jsd = 0
    for k in all_keys:
        p_k = p.get(k, 0) / total_p + eps
        q_k = q.get(k, 0) / total_q + eps
        m_k = (p_k + q_k) / 2
        jsd += 0.5 * (p_k * log2(p_k / m_k) + q_k * log2(q_k / m_k))

    return jsd

def classify_token(word, currier):
    """Classify a token into grammar categories."""
    if not word or '*' in word:
        return 'DAMAGED'

    has_b_prefix = any(word.startswith(p) for p in B_GRAMMAR_PREFIXES)
    has_b_suffix = any(word.endswith(s) for s in B_GRAMMAR_SUFFIXES)
    has_ht_prefix = any(word.startswith(p) for p in HT_PREFIXES)
    has_ht_suffix = any(word.endswith(s) for s in HT_SUFFIXES)

    if has_b_prefix and has_b_suffix:
        return 'B_GRAMMAR_FULL'
    elif has_b_prefix:
        return 'B_PREFIX_ONLY'
    elif has_b_suffix:
        return 'B_SUFFIX_ONLY'
    elif has_ht_prefix or has_ht_suffix:
        return 'HT'
    else:
        return 'ORPHAN'

def get_ht_components(word):
    """Extract HT prefix/middle/suffix if present."""
    prefix = None
    suffix = None

    for p in sorted(HT_PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            break

    for s in sorted(HT_SUFFIXES, key=len, reverse=True):
        if word.endswith(s):
            suffix = s
            break

    if prefix and suffix and len(word) > len(prefix) + len(suffix):
        middle = word[len(prefix):-len(suffix)]
    elif prefix:
        middle = word[len(prefix):]
    elif suffix:
        middle = word[:-len(suffix)]
    else:
        middle = word

    return prefix, middle, suffix

# ============================================================================
# TEST R-1: Frequency Stability
# ============================================================================

def test_r1_frequency_stability():
    """Compare token frequency distributions before/after recovery."""
    print("\n" + "=" * 70)
    print("TEST R-1: FREQUENCY STABILITY")
    print("=" * 70)

    results = {'test': 'R-1', 'name': 'Frequency Stability', 'metrics': {}}

    # Load original and recovered
    original = load_transcription(apply_recovery=False)
    recovered = load_transcription(apply_recovery=True, min_confidence='HIGH')

    # Compute frequencies
    orig_freq = Counter(t for t in original if '*' not in t)
    rec_freq = Counter(t for t in recovered if '*' not in t)

    # Test at different N values
    for n in [50, 100, 200]:
        # Get top N ranks
        orig_top = {tok: rank for rank, (tok, _) in enumerate(orig_freq.most_common(n))}
        rec_top = {tok: rank for rank, (tok, _) in enumerate(rec_freq.most_common(n))}

        # Spearman correlation
        rho = spearman_rank_correlation(orig_top, rec_top)

        # JSD
        orig_n = Counter({k: v for k, v in orig_freq.most_common(n)})
        rec_n = Counter({k: v for k, v in rec_freq.most_common(n)})
        jsd = jsd_divergence(orig_n, rec_n)

        results['metrics'][f'top_{n}_spearman'] = rho
        results['metrics'][f'top_{n}_jsd'] = jsd

        print(f"\nTop {n} tokens:")
        print(f"  Spearman rho: {rho:.4f} (threshold >= 0.99)")
        print(f"  JSD: {jsd:.6f} (threshold ~= 0)")

    # Overall verdict
    all_pass = all(results['metrics'][f'top_{n}_spearman'] >= 0.99 for n in [50, 100, 200])
    results['verdict'] = 'PASS' if all_pass else 'FAIL'
    print(f"\nVerdict: {results['verdict']}")

    return results

# ============================================================================
# TEST R-2: Grammar Coverage Stability
# ============================================================================

def test_r2_grammar_coverage():
    """Check if grammar classification changes."""
    print("\n" + "=" * 70)
    print("TEST R-2: GRAMMAR COVERAGE STABILITY")
    print("=" * 70)

    results = {'test': 'R-2', 'name': 'Grammar Coverage Stability', 'metrics': {}}

    # Load Currier B only
    orig_entries = load_transcription(apply_recovery=False, include_metadata=True)
    rec_entries = load_transcription(apply_recovery=True, min_confidence='HIGH', include_metadata=True)

    orig_b = [e for e in orig_entries if e['currier'] == 'B']
    rec_b = [e for e in rec_entries if e['currier'] == 'B']

    # Classify tokens
    orig_classes = Counter(classify_token(e['word'], 'B') for e in orig_b)
    rec_classes = Counter(classify_token(e['word'], 'B') for e in rec_b)

    # Grammar coverage (B_GRAMMAR_FULL + B_PREFIX_ONLY + B_SUFFIX_ONLY)
    orig_grammar = (orig_classes['B_GRAMMAR_FULL'] + orig_classes['B_PREFIX_ONLY'] + orig_classes['B_SUFFIX_ONLY'])
    rec_grammar = (rec_classes['B_GRAMMAR_FULL'] + rec_classes['B_PREFIX_ONLY'] + rec_classes['B_SUFFIX_ONLY'])

    orig_pct = 100 * orig_grammar / len(orig_b)
    rec_pct = 100 * rec_grammar / len(rec_b)
    diff = abs(rec_pct - orig_pct)

    results['metrics']['orig_grammar_pct'] = orig_pct
    results['metrics']['rec_grammar_pct'] = rec_pct
    results['metrics']['difference_pp'] = diff

    print(f"\nGrammar coverage:")
    print(f"  Original: {orig_pct:.2f}%")
    print(f"  Recovered: {rec_pct:.2f}%")
    print(f"  Difference: {diff:.2f} pp (threshold < 0.5)")

    # Class distribution correlation
    all_classes = set(orig_classes.keys()) | set(rec_classes.keys())
    orig_vec = [orig_classes.get(c, 0) for c in sorted(all_classes)]
    rec_vec = [rec_classes.get(c, 0) for c in sorted(all_classes)]

    # Pearson-like correlation
    mean_o = sum(orig_vec) / len(orig_vec)
    mean_r = sum(rec_vec) / len(rec_vec)
    num = sum((o - mean_o) * (r - mean_r) for o, r in zip(orig_vec, rec_vec))
    den_o = sum((o - mean_o)**2 for o in orig_vec) ** 0.5
    den_r = sum((r - mean_r)**2 for r in rec_vec) ** 0.5
    corr = num / (den_o * den_r) if den_o > 0 and den_r > 0 else 0

    results['metrics']['class_correlation'] = corr
    print(f"\nClass distribution correlation: {corr:.4f} (threshold >= 0.98)")

    print("\nClass distribution:")
    print(f"  {'Class':<20} {'Original':>10} {'Recovered':>10} {'Change':>10}")
    print("  " + "-" * 55)
    for c in sorted(all_classes):
        o = orig_classes.get(c, 0)
        r = rec_classes.get(c, 0)
        change = r - o
        print(f"  {c:<20} {o:>10} {r:>10} {change:>+10}")

    # Verdict
    coverage_ok = diff < 0.5
    corr_ok = corr >= 0.98
    results['verdict'] = 'PASS' if (coverage_ok and corr_ok) else 'FAIL'
    print(f"\nVerdict: {results['verdict']}")

    return results

# ============================================================================
# TEST R-3: HT Morphology Stability
# ============================================================================

def test_r3_ht_morphology():
    """Check if HT structure ratios change."""
    print("\n" + "=" * 70)
    print("TEST R-3: HT MORPHOLOGY STABILITY")
    print("=" * 70)

    results = {'test': 'R-3', 'name': 'HT Morphology Stability', 'metrics': {}}

    # Load data
    orig_entries = load_transcription(apply_recovery=False, include_metadata=True)
    rec_entries = load_transcription(apply_recovery=True, min_confidence='HIGH', include_metadata=True)

    def get_ht_stats(entries):
        ht_tokens = []
        for e in entries:
            if classify_token(e['word'], e['currier']) == 'HT':
                ht_tokens.append(e['word'])

        prefix_counts = Counter()
        suffix_counts = Counter()
        decomposable = 0

        for tok in ht_tokens:
            prefix, middle, suffix = get_ht_components(tok)
            if prefix:
                prefix_counts[prefix] += 1
            if suffix:
                suffix_counts[suffix] += 1
            if prefix or suffix:
                decomposable += 1

        return {
            'total': len(ht_tokens),
            'decomposable': decomposable,
            'decomposable_pct': 100 * decomposable / len(ht_tokens) if ht_tokens else 0,
            'prefix_counts': prefix_counts,
            'suffix_counts': suffix_counts
        }

    orig_stats = get_ht_stats(orig_entries)
    rec_stats = get_ht_stats(rec_entries)

    print(f"\nHT token counts:")
    print(f"  Original: {orig_stats['total']}")
    print(f"  Recovered: {rec_stats['total']}")

    print(f"\nDecomposable rate:")
    print(f"  Original: {orig_stats['decomposable_pct']:.1f}%")
    print(f"  Recovered: {rec_stats['decomposable_pct']:.1f}%")

    decomp_diff = abs(rec_stats['decomposable_pct'] - orig_stats['decomposable_pct'])
    results['metrics']['decomposable_diff_pp'] = decomp_diff

    # Compare top prefixes
    print("\nTop 10 HT prefixes:")
    print(f"  {'Prefix':<10} {'Original':>10} {'Recovered':>10} {'Change%':>10}")
    print("  " + "-" * 45)

    all_prefixes = set(orig_stats['prefix_counts'].keys()) | set(rec_stats['prefix_counts'].keys())
    max_change = 0
    for p in sorted(all_prefixes, key=lambda x: -orig_stats['prefix_counts'].get(x, 0))[:10]:
        o = orig_stats['prefix_counts'].get(p, 0)
        r = rec_stats['prefix_counts'].get(p, 0)
        change_pct = 100 * (r - o) / o if o > 0 else 0
        max_change = max(max_change, abs(change_pct))
        print(f"  {p:<10} {o:>10} {r:>10} {change_pct:>+9.1f}%")

    results['metrics']['max_prefix_change_pct'] = max_change
    print(f"\nMax prefix frequency change: {max_change:.1f}% (threshold <= 5%)")

    # Verdict
    decomp_ok = decomp_diff <= 5
    prefix_ok = max_change <= 5
    results['verdict'] = 'PASS' if (decomp_ok and prefix_ok) else 'MARGINAL' if max_change <= 10 else 'FAIL'
    print(f"\nVerdict: {results['verdict']}")

    return results

# ============================================================================
# TEST R-4: Orphan Rate Reduction (EXPECTED TO CHANGE)
# ============================================================================

def test_r4_orphan_reduction():
    """Check if recovery reduces orphan rate (expected improvement)."""
    print("\n" + "=" * 70)
    print("TEST R-4: ORPHAN RATE REDUCTION (Expected to improve)")
    print("=" * 70)

    results = {'test': 'R-4', 'name': 'Orphan Rate Reduction', 'metrics': {}}

    # Load data
    original = load_transcription(apply_recovery=False)
    recovered = load_transcription(apply_recovery=True, min_confidence='HIGH')

    # Count orphans (tokens that don't match any grammar pattern)
    def count_orphans_and_hapax(tokens):
        freq = Counter(t for t in tokens if '*' not in t)

        orphans = 0
        for tok in freq:
            if classify_token(tok, '') == 'ORPHAN':
                orphans += freq[tok]

        hapax = sum(1 for t, c in freq.items() if c == 1)

        return orphans, hapax, len(freq)

    orig_orphans, orig_hapax, orig_types = count_orphans_and_hapax(original)
    rec_orphans, rec_hapax, rec_types = count_orphans_and_hapax(recovered)

    orig_total = sum(1 for t in original if '*' not in t)
    rec_total = sum(1 for t in recovered if '*' not in t)

    orig_orphan_pct = 100 * orig_orphans / orig_total
    rec_orphan_pct = 100 * rec_orphans / rec_total
    orphan_reduction = orig_orphan_pct - rec_orphan_pct

    print(f"\nOrphan rate:")
    print(f"  Original: {orig_orphan_pct:.2f}% ({orig_orphans} tokens)")
    print(f"  Recovered: {rec_orphan_pct:.2f}% ({rec_orphans} tokens)")
    print(f"  Reduction: {orphan_reduction:.2f} pp")

    results['metrics']['orig_orphan_pct'] = orig_orphan_pct
    results['metrics']['rec_orphan_pct'] = rec_orphan_pct
    results['metrics']['orphan_reduction_pp'] = orphan_reduction

    print(f"\nHapax legomena:")
    print(f"  Original: {orig_hapax} ({100*orig_hapax/orig_types:.1f}% of types)")
    print(f"  Recovered: {rec_hapax} ({100*rec_hapax/rec_types:.1f}% of types)")
    print(f"  Change: {rec_hapax - orig_hapax}")

    results['metrics']['orig_hapax'] = orig_hapax
    results['metrics']['rec_hapax'] = rec_hapax
    results['metrics']['hapax_change'] = rec_hapax - orig_hapax

    # Check for new mid-frequency types (should not appear)
    orig_freq = Counter(t for t in original if '*' not in t)
    rec_freq = Counter(t for t in recovered if '*' not in t)

    new_types = set(rec_freq.keys()) - set(orig_freq.keys())
    new_mid_freq = [t for t in new_types if rec_freq[t] >= 5]

    print(f"\nNew mid-frequency types (freq >= 5): {len(new_mid_freq)}")
    if new_mid_freq:
        print(f"  Examples: {new_mid_freq[:5]}")

    results['metrics']['new_mid_freq_types'] = len(new_mid_freq)

    # Verdict (orphan reduction is GOOD, but no new types)
    reduced = orphan_reduction > 0
    no_new = len(new_mid_freq) == 0
    results['verdict'] = 'PASS (expected improvement)' if (reduced and no_new) else 'UNEXPECTED'
    print(f"\nVerdict: {results['verdict']}")

    return results

# ============================================================================
# TEST R-5: Recovery Confidence Thresholding
# ============================================================================

def test_r5_sensitivity():
    """Test sensitivity to recovery confidence threshold."""
    print("\n" + "=" * 70)
    print("TEST R-5: RECOVERY CONFIDENCE THRESHOLDING")
    print("=" * 70)

    results = {'test': 'R-5', 'name': 'Confidence Sensitivity', 'metrics': {}}

    thresholds = ['CERTAIN', 'HIGH', 'AMBIGUOUS']

    print("\nComparing stability across confidence thresholds:")
    print(f"\n{'Threshold':<12} {'Damaged':>10} {'Orphan%':>10} {'HT count':>10} {'Grammar%':>10}")
    print("-" * 55)

    baseline_metrics = None

    for threshold in thresholds:
        entries = load_transcription(
            apply_recovery=True if threshold != 'NONE' else False,
            min_confidence=threshold,
            include_metadata=True
        )

        b_entries = [e for e in entries if e['currier'] == 'B']

        damaged = sum(1 for e in entries if '*' in e['word'])

        classes = Counter(classify_token(e['word'], 'B') for e in b_entries)
        orphan_pct = 100 * classes['ORPHAN'] / len(b_entries)
        ht_count = classes['HT']
        grammar_pct = 100 * (classes['B_GRAMMAR_FULL'] + classes['B_PREFIX_ONLY'] + classes['B_SUFFIX_ONLY']) / len(b_entries)

        print(f"{threshold:<12} {damaged:>10} {orphan_pct:>9.2f}% {ht_count:>10} {grammar_pct:>9.2f}%")

        results['metrics'][f'{threshold}_damaged'] = damaged
        results['metrics'][f'{threshold}_orphan_pct'] = orphan_pct
        results['metrics'][f'{threshold}_ht_count'] = ht_count
        results['metrics'][f'{threshold}_grammar_pct'] = grammar_pct

        if baseline_metrics is None:
            baseline_metrics = {'orphan': orphan_pct, 'ht': ht_count, 'grammar': grammar_pct}

    # Check stability (differences between CERTAIN and AMBIGUOUS)
    orphan_range = abs(results['metrics']['AMBIGUOUS_orphan_pct'] - results['metrics']['CERTAIN_orphan_pct'])
    grammar_range = abs(results['metrics']['AMBIGUOUS_grammar_pct'] - results['metrics']['CERTAIN_grammar_pct'])

    print(f"\nStability range:")
    print(f"  Orphan % range: {orphan_range:.2f} pp")
    print(f"  Grammar % range: {grammar_range:.2f} pp")

    results['metrics']['orphan_range'] = orphan_range
    results['metrics']['grammar_range'] = grammar_range

    # Verdict (core results should be insensitive)
    stable = orphan_range < 2 and grammar_range < 1
    results['verdict'] = 'PASS (insensitive)' if stable else 'SENSITIVE'
    print(f"\nVerdict: {results['verdict']}")

    return results

# ============================================================================
# MAIN
# ============================================================================

def run_all_tests():
    """Run all validation tests and return results."""
    print("=" * 70)
    print("RECOVERY VALIDATION TEST SUITE")
    print("=" * 70)
    print("\nRunning 5 validation tests to verify recovery improves hygiene")
    print("without changing structural conclusions.")

    all_results = []

    all_results.append(test_r1_frequency_stability())
    all_results.append(test_r2_grammar_coverage())
    all_results.append(test_r3_ht_morphology())
    all_results.append(test_r4_orphan_reduction())
    all_results.append(test_r5_sensitivity())

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"\n{'Test':<35} {'Verdict':<25}")
    print("-" * 60)

    for r in all_results:
        print(f"{r['test']}: {r['name']:<30} {r['verdict']:<25}")

    # Overall verdict
    passes = sum(1 for r in all_results if 'PASS' in r['verdict'])
    print(f"\nOverall: {passes}/5 tests passed")

    if passes == 5:
        print("\nCONCLUSION: Recovery is safe and improves data hygiene.")
        print("No structural conclusions depend on recovered tokens.")
    elif passes >= 4:
        print("\nCONCLUSION: Recovery is largely safe with minor sensitivity.")
    else:
        print("\nWARNING: Recovery may be too aggressive. Review failed tests.")

    return all_results

if __name__ == '__main__':
    results = run_all_tests()

    # Save results to JSON
    output_path = Path(__file__).parent.parent.parent / 'archive' / 'reports' / 'recovery_validation_results.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Counter objects to dicts for JSON serialization
    def serialize(obj):
        if isinstance(obj, Counter):
            return dict(obj)
        return obj

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=serialize)

    print(f"\nResults saved to: {output_path}")

"""
PHYS Phase: Physics Plausibility Stress Test

Tests whether the grammar's behavioral properties are consistent with
controlling a physical system with inertia, irreversibility, and
equilibrium-seeking dynamics.

SCOPE CONSTRAINTS:
- NO semantic mappings (heat, moisture, growth, etc.)
- NO external historical references
- NO physical quantity inference
- Only constraint-based, directional invariants

Tests:
- PH-1: Irreversibility Audit (Monotonic Control)
- PH-2: Stabilization Dominance Test
- PH-3: Rate-Limiting via WAIT (LINK Buffering)
- PH-4: Oscillation Suppression Test
- PH-5: Abort Cost Asymmetry Test
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats


def load_currier_b_tokens():
    """Load tokens from Currier B folios only."""
    data_path = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")

    tokens = []
    with open(data_path, 'r', encoding='utf-8') as f:
        header = next(f)  # Skip header

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"') if parts[0] else ''
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''
                transcriber = parts[12].strip('"').strip()

                # Filter to PRIMARY transcriber (H) only
                if transcriber != 'H':
                    continue

                # Currier B classification
                if language == 'B':
                    if word and word != '.' and word != '=' and word != 'NA':
                        tokens.append({
                            'word': word,
                            'folio': folio,
                            'section': section
                        })

    return tokens


def get_kernel_class(word):
    """Returns 'k', 'h', 'e', or None based on kernel classification."""
    if not word:
        return None

    # k-class: ends in k or specific k-tokens
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'

    # h-class: ends in h or specific h-tokens
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'

    # e-class: specific e-endings indicating stability
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy') or word.endswith('dy'):
        return 'e'

    return None


def is_link(word):
    """Returns True if word contains 'ol' (LINK/wait marker)."""
    return 'ol' in word if word else False


def is_escalation(word):
    """Returns True if k or h class (disruptive transitions)."""
    kc = get_kernel_class(word)
    return kc in ['k', 'h']


def test_ph1_irreversibility(tokens):
    """
    PH-1: Irreversibility Audit (Monotonic Control)

    Question: Does the grammar enforce forward-only progression after escalation?

    Method:
    - After escalation (k or h), measure steps to return to e-dominant state
    - Compare forward vs backward asymmetry
    """
    print("\n=== PH-1: Irreversibility Audit ===")

    words = [t['word'] for t in tokens]

    # Find escalation events and measure recovery
    recovery_lengths = []
    immediate_reversals = 0
    total_escalations = 0

    for i, word in enumerate(words):
        if is_escalation(word):
            total_escalations += 1

            # Check for immediate reversal (e-class within 2 tokens)
            immediate = False
            for j in range(i+1, min(i+3, len(words))):
                if get_kernel_class(words[j]) == 'e':
                    immediate = True
                    break
            if immediate:
                immediate_reversals += 1

            # Measure steps to next e-class token
            for j in range(i+1, min(i+50, len(words))):
                if get_kernel_class(words[j]) == 'e':
                    recovery_lengths.append(j - i)
                    break

    # Calculate metrics
    if total_escalations == 0:
        return {
            'test': 'PH-1',
            'verdict': 'NO_DATA',
            'reason': 'No escalation events found'
        }

    immediate_rate = immediate_reversals / total_escalations
    mean_recovery = np.mean(recovery_lengths) if recovery_lengths else 0

    # Compare to null: if random, immediate reversal rate would be ~baseline e-class rate
    e_class_rate = sum(1 for w in words if get_kernel_class(w) == 'e') / len(words)

    # Asymmetry: recovery should take longer than baseline would predict
    # If immediate reversals are LESS than random e-class rate, that's asymmetry
    asymmetry_ratio = immediate_rate / e_class_rate if e_class_rate > 0 else 0

    print(f"Total escalations: {total_escalations}")
    print(f"Immediate reversals (e within 2): {immediate_reversals} ({immediate_rate:.1%})")
    print(f"Baseline e-class rate: {e_class_rate:.1%}")
    print(f"Asymmetry ratio: {asymmetry_ratio:.3f}")
    print(f"Mean recovery length: {mean_recovery:.1f} tokens")

    # PASS if asymmetry ratio < 0.85 (recovery is slower than random would predict)
    # This means escalation creates "inertia" - can't immediately return
    passed = asymmetry_ratio < 0.85 and mean_recovery > 3

    return {
        'test': 'PH-1',
        'total_escalations': total_escalations,
        'immediate_reversals': immediate_reversals,
        'immediate_rate': immediate_rate,
        'baseline_e_rate': e_class_rate,
        'asymmetry_ratio': asymmetry_ratio,
        'mean_recovery_length': mean_recovery,
        'verdict': 'PASS' if passed else 'FAIL',
        'effect_size': 1 - asymmetry_ratio
    }


def test_ph2_stabilization(tokens):
    """
    PH-2: Stabilization Dominance Test

    Question: Is stabilization the dominant attractor after perturbation?

    Method:
    - After k or h token, measure probability of returning to e-dominant state
    - Compare against null shuffle
    """
    print("\n=== PH-2: Stabilization Dominance ===")

    words = [t['word'] for t in tokens]

    # After each k or h, count e-class in next 5 tokens
    post_escalation_e = []

    for i, word in enumerate(words):
        if is_escalation(word):
            window = words[i+1:i+6]
            e_count = sum(1 for w in window if get_kernel_class(w) == 'e')
            post_escalation_e.append(e_count / len(window) if window else 0)

    # Baseline: e-class rate in random windows
    baseline_rates = []
    for _ in range(1000):
        start = random.randint(0, len(words) - 6)
        window = words[start:start+5]
        e_count = sum(1 for w in window if get_kernel_class(w) == 'e')
        baseline_rates.append(e_count / len(window) if window else 0)

    if not post_escalation_e:
        return {
            'test': 'PH-2',
            'verdict': 'NO_DATA',
            'reason': 'No post-escalation windows'
        }

    mean_post_esc = np.mean(post_escalation_e)
    mean_baseline = np.mean(baseline_rates)

    # Statistical test
    stat, pvalue = stats.mannwhitneyu(post_escalation_e, baseline_rates, alternative='greater')

    # Effect size
    effect = mean_post_esc - mean_baseline

    print(f"Post-escalation e-rate: {mean_post_esc:.1%}")
    print(f"Baseline e-rate: {mean_baseline:.1%}")
    print(f"Effect: {effect:+.1%}")
    print(f"Mann-Whitney p-value: {pvalue:.6f}")

    # PASS if post-escalation has higher e-rate than baseline (pull back to stability)
    passed = effect > 0.10 and pvalue < 0.05

    return {
        'test': 'PH-2',
        'post_escalation_e_rate': mean_post_esc,
        'baseline_e_rate': mean_baseline,
        'effect': effect,
        'pvalue': pvalue,
        'verdict': 'PASS' if passed else 'FAIL',
        'effect_size': effect
    }


def test_ph3_link_buffering(tokens):
    """
    PH-3: Rate-Limiting via WAIT (LINK Buffering)

    Question: Are disruptive transitions buffered by LINK more than neutral ones?

    Method:
    - Count LINK tokens within +/-3 window around escalation events
    - Compare to random positions
    """
    print("\n=== PH-3: LINK Buffering ===")

    words = [t['word'] for t in tokens]
    window_size = 3

    # LINK density around escalation events
    escalation_link_counts = []
    for i, word in enumerate(words):
        if is_escalation(word):
            start = max(0, i - window_size)
            end = min(len(words), i + window_size + 1)
            window = words[start:end]
            link_count = sum(1 for w in window if is_link(w))
            escalation_link_counts.append(link_count)

    # LINK density around random positions (excluding escalations)
    non_escalation_indices = [i for i, w in enumerate(words) if not is_escalation(w)]
    random_link_counts = []
    for _ in range(min(1000, len(non_escalation_indices))):
        i = random.choice(non_escalation_indices)
        start = max(0, i - window_size)
        end = min(len(words), i + window_size + 1)
        window = words[start:end]
        link_count = sum(1 for w in window if is_link(w))
        random_link_counts.append(link_count)

    if not escalation_link_counts:
        return {
            'test': 'PH-3',
            'verdict': 'NO_DATA',
            'reason': 'No escalation events'
        }

    mean_esc_link = np.mean(escalation_link_counts)
    mean_random_link = np.mean(random_link_counts)

    # Statistical test
    stat, pvalue = stats.mannwhitneyu(escalation_link_counts, random_link_counts, alternative='greater')

    effect = mean_esc_link - mean_random_link
    ratio = mean_esc_link / mean_random_link if mean_random_link > 0 else 0

    print(f"LINK density near escalation: {mean_esc_link:.3f}")
    print(f"LINK density at random: {mean_random_link:.3f}")
    print(f"Enrichment ratio: {ratio:.3f}")
    print(f"Mann-Whitney p-value: {pvalue:.6f}")

    # PASS if escalations have MORE LINK nearby (rate-limited)
    passed = ratio > 1.10 and pvalue < 0.05

    return {
        'test': 'PH-3',
        'escalation_link_density': mean_esc_link,
        'random_link_density': mean_random_link,
        'enrichment_ratio': ratio,
        'pvalue': pvalue,
        'verdict': 'PASS' if passed else 'NEUTRAL',  # Either result informative
        'effect_size': ratio - 1
    }


def test_ph4_oscillation_suppression(tokens):
    """
    PH-4: Oscillation Suppression Test

    Question: Does the grammar actively suppress rapid oscillation between disruptive states?

    Method:
    - Count alternating patterns (k-h-k, h-k-h)
    - Compare against Markov-matched null
    """
    print("\n=== PH-4: Oscillation Suppression ===")

    words = [t['word'] for t in tokens]

    # Get kernel sequences
    kernel_seq = [get_kernel_class(w) for w in words]
    kernel_seq = [k for k in kernel_seq if k is not None]

    if len(kernel_seq) < 10:
        return {
            'test': 'PH-4',
            'verdict': 'NO_DATA',
            'reason': 'Insufficient kernel tokens'
        }

    # Count observed alternating patterns
    def count_alternations(seq):
        khk = 0
        hkh = 0
        for i in range(len(seq) - 2):
            if seq[i] == 'k' and seq[i+1] == 'h' and seq[i+2] == 'k':
                khk += 1
            if seq[i] == 'h' and seq[i+1] == 'k' and seq[i+2] == 'h':
                hkh += 1
        return khk + hkh

    observed_alt = count_alternations(kernel_seq)

    # Build Markov model (bigram frequencies)
    bigrams = Counter()
    for i in range(len(kernel_seq) - 1):
        bigrams[(kernel_seq[i], kernel_seq[i+1])] += 1

    # Normalize to transition probabilities
    from_counts = Counter(kernel_seq[:-1])
    trans_prob = {}
    for (a, b), count in bigrams.items():
        trans_prob[(a, b)] = count / from_counts[a]

    # Generate null sequences with same Markov structure
    null_alternations = []
    for _ in range(1000):
        # Start with observed distribution
        null_seq = [random.choice(kernel_seq)]
        for _ in range(len(kernel_seq) - 1):
            current = null_seq[-1]
            # Sample next based on transition probs
            candidates = [k for k in ['k', 'h', 'e'] if (current, k) in trans_prob]
            if candidates:
                probs = [trans_prob.get((current, k), 0) for k in candidates]
                total = sum(probs)
                probs = [p/total for p in probs]
                next_k = random.choices(candidates, weights=probs)[0]
                null_seq.append(next_k)
            else:
                null_seq.append(random.choice(['k', 'h', 'e']))

        null_alternations.append(count_alternations(null_seq))

    mean_null = np.mean(null_alternations)
    std_null = np.std(null_alternations)

    # Z-score: how many SDs below expected?
    z_score = (observed_alt - mean_null) / std_null if std_null > 0 else 0

    # P-value: what fraction of null have >= observed?
    pvalue = sum(1 for n in null_alternations if n <= observed_alt) / len(null_alternations)

    suppression_ratio = observed_alt / mean_null if mean_null > 0 else 0

    print(f"Observed alternations: {observed_alt}")
    print(f"Expected (Markov null): {mean_null:.1f} +/- {std_null:.1f}")
    print(f"Suppression ratio: {suppression_ratio:.3f}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P-value: {pvalue:.4f}")

    # PASS if alternations are suppressed (ratio < 0.85)
    passed = suppression_ratio < 0.85 and pvalue < 0.05

    return {
        'test': 'PH-4',
        'observed_alternations': observed_alt,
        'expected_alternations': mean_null,
        'suppression_ratio': suppression_ratio,
        'z_score': z_score,
        'pvalue': pvalue,
        'verdict': 'PASS' if passed else 'FAIL',
        'effect_size': 1 - suppression_ratio
    }


def test_ph5_abort_cost(tokens):
    """
    PH-5: Abort Cost Asymmetry Test

    Question: Are abort/restart paths rarer, longer, or constrained compared to continuation?

    Method:
    - Compare restart-capable folios (f50v, f57r, f82v) vs others
    - Measure structural differences
    """
    print("\n=== PH-5: Abort Cost Asymmetry ===")

    # Group by folio
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t['folio']].append(t['word'])

    # Known restart-capable folios
    restart_folios = ['f50v', 'f57r', 'f82v']

    restart_data = []
    normal_data = []

    for folio, words in folio_tokens.items():
        if len(words) < 10:
            continue

        # Calculate metrics
        kernel_classes = [get_kernel_class(w) for w in words]
        kernel_classes = [k for k in kernel_classes if k is not None]

        if len(kernel_classes) < 5:
            continue

        # Kernel composition
        k_rate = kernel_classes.count('k') / len(kernel_classes)
        h_rate = kernel_classes.count('h') / len(kernel_classes)
        e_rate = kernel_classes.count('e') / len(kernel_classes)

        # LINK density
        link_rate = sum(1 for w in words if is_link(w)) / len(words)

        # Entropy of kernel distribution
        from scipy.stats import entropy as sp_entropy
        counts = [kernel_classes.count(k) for k in ['k', 'h', 'e']]
        total = sum(counts)
        probs = [c/total for c in counts] if total > 0 else [1/3, 1/3, 1/3]
        kernel_entropy = sp_entropy(probs)

        metrics = {
            'folio': folio,
            'token_count': len(words),
            'k_rate': k_rate,
            'h_rate': h_rate,
            'e_rate': e_rate,
            'link_rate': link_rate,
            'kernel_entropy': kernel_entropy,
            'escalation_rate': k_rate + h_rate
        }

        if any(restart in folio for restart in restart_folios):
            restart_data.append(metrics)
        else:
            normal_data.append(metrics)

    if len(restart_data) < 2:
        return {
            'test': 'PH-5',
            'verdict': 'NO_DATA',
            'reason': f'Only {len(restart_data)} restart folios found'
        }

    # Compare metrics
    results = {}

    for metric in ['e_rate', 'link_rate', 'kernel_entropy', 'escalation_rate']:
        restart_vals = [d[metric] for d in restart_data]
        normal_vals = [d[metric] for d in normal_data]

        restart_mean = np.mean(restart_vals)
        normal_mean = np.mean(normal_vals)

        stat, pval = stats.mannwhitneyu(restart_vals, normal_vals, alternative='two-sided')

        results[metric] = {
            'restart_mean': restart_mean,
            'normal_mean': normal_mean,
            'difference': restart_mean - normal_mean,
            'pvalue': pval
        }

        print(f"{metric}: restart={restart_mean:.3f}, normal={normal_mean:.3f}, diff={restart_mean-normal_mean:+.3f}, p={pval:.4f}")

    # PASS if restart folios show distinct structural signature
    # (higher stability, lower escalation, different entropy)
    significant_diffs = sum(1 for m in results.values() if m['pvalue'] < 0.1)

    # Key check: restart folios should have higher stability (e_rate) or lower escalation
    e_diff = results['e_rate']['difference']
    esc_diff = results['escalation_rate']['difference']

    # Restart paths are "costly" if they require special conditions
    passed = significant_diffs >= 2 or (e_diff > 0.05 and esc_diff < -0.02)

    return {
        'test': 'PH-5',
        'restart_folio_count': len(restart_data),
        'normal_folio_count': len(normal_data),
        'metrics': results,
        'significant_differences': significant_diffs,
        'verdict': 'PASS' if passed else 'FAIL',
        'effect_size': abs(e_diff) + abs(esc_diff)
    }


def main():
    """Run all PHYS tests."""
    print("=" * 60)
    print("PHYS Phase: Physics Plausibility Stress Test")
    print("=" * 60)

    # Load data
    print("\nLoading Currier B tokens...")
    tokens = load_currier_b_tokens()
    print(f"Loaded {len(tokens)} tokens from Currier B sections")

    # Run tests
    results = {}

    # PH-1: Irreversibility
    results['PH-1'] = test_ph1_irreversibility(tokens)

    # PH-2: Stabilization
    results['PH-2'] = test_ph2_stabilization(tokens)

    # PH-3: LINK Buffering
    results['PH-3'] = test_ph3_link_buffering(tokens)

    # PH-4: Oscillation Suppression
    results['PH-4'] = test_ph4_oscillation_suppression(tokens)

    # PH-5: Abort Cost
    results['PH-5'] = test_ph5_abort_cost(tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = []
    for test_id in ['PH-1', 'PH-2', 'PH-3', 'PH-4', 'PH-5']:
        r = results[test_id]
        verdict = r.get('verdict', 'ERROR')
        effect = r.get('effect_size', 0)
        verdicts.append(verdict)
        print(f"{test_id}: {verdict} (effect size: {effect:.3f})")

    # Check stop conditions
    print("\n--- Stop Condition Check ---")
    pass_count = verdicts.count('PASS')
    fail_count = verdicts.count('FAIL')
    neutral_count = verdicts.count('NEUTRAL')

    print(f"PASS: {pass_count}, FAIL: {fail_count}, NEUTRAL: {neutral_count}")

    # Significant effects (>= 10-15%)
    significant = sum(1 for r in results.values()
                     if r.get('effect_size', 0) >= 0.10)
    print(f"Tests with >= 10% effect: {significant}")

    # Overall verdict
    if pass_count >= 3:
        overall = "PHYSICS_CONSISTENT"
        print("\nOVERALL: Grammar shows physics-consistent behavior")
    elif pass_count >= 2 and significant >= 2:
        overall = "PARTIAL_SUPPORT"
        print("\nOVERALL: Partial support for physical plausibility")
    else:
        overall = "INSUFFICIENT"
        print("\nOVERALL: Insufficient evidence for physics-consistent interpretation")

    results['overall'] = {
        'verdict': overall,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'significant_effects': significant
    }

    # Save results
    output_path = Path("C:/git/voynich/phases/PHYS_physics_stress_test/phys_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")

    return results


if __name__ == '__main__':
    main()

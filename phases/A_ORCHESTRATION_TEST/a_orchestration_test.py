"""
A-ORCHESTRATION HYPOTHESIS TEST

Question: Does token position within multi-token Currier A entries
encode a trajectory through B programs (REGIMEs)?

Hypothesis: Early position tokens correlate with lower REGIME (gentle),
late position tokens correlate with higher REGIME (intense).

Test:
1. Identify multi-token A entries (3+ tokens per line)
2. For each token at each position, find B folios containing that vocabulary
3. Get REGIME ordinal of those B folios
4. Compute Kendall's tau: position vs mean REGIME ordinal
5. Control: shuffle positions within entries, re-run

Success criteria:
- tau > 0.15, p < 0.01, shuffled = null -> SUPPORTS
- tau ~ 0, p > 0.05 -> FALSIFIED
- tau > 0 but shuffled also > 0 -> VOCABULARY EFFECT (already covered by C234)
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
import random

project_root = Path(__file__).parent.parent.parent

# REGIME ordinal mapping (lower = gentler, higher = more intense)
REGIME_ORDINAL = {
    'REGIME_2': 1,  # Lowest CEI, gentlest
    'REGIME_1': 2,  # Baseline
    'REGIME_4': 3,  # Elevated engagement
    'REGIME_3': 4,  # High throughput, most aggressive
}


def load_data():
    """Load transcription data with line grouping."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        header = [h.strip('"') for h in header]

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''
                transcriber = parts[12].strip('"').strip()
                line_number = parts[11].strip('"') if len(parts) > 11 else ''

                # Filter to H (PRIMARY) transcriber only
                if transcriber != 'H':
                    continue

                if word and folio:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'currier': language,
                        'line_number': line_number
                    })

    return data


def load_regime_mapping():
    """Load REGIME to folio mapping and create folio to REGIME lookup."""
    filepath = project_root / 'results' / 'regime_folio_mapping.json'

    with open(filepath, 'r') as f:
        regime_folios = json.load(f)

    # Create reverse mapping: folio -> REGIME
    folio_to_regime = {}
    for regime, folios in regime_folios.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    return folio_to_regime


def build_a_entries(data):
    """Group A tokens into entries (lines) and filter to 3+ token entries."""
    a_data = [d for d in data if d['currier'] == 'A']

    # Group by folio + line
    entries = defaultdict(list)
    for d in a_data:
        key = (d['folio'], d['line_number'])
        entries[key].append(d['token'])

    # Filter to 3+ token entries
    multi_token_entries = {
        k: v for k, v in entries.items()
        if len(v) >= 3
    }

    return multi_token_entries


def build_b_vocabulary(data, folio_to_regime):
    """Build mapping: token -> set of B folios where it appears."""
    b_data = [d for d in data if d['currier'] == 'B']

    token_to_b_folios = defaultdict(set)
    for d in b_data:
        folio = d['folio']
        if folio in folio_to_regime:  # Only count folios with REGIME assignment
            token_to_b_folios[d['token']].add(folio)

    return token_to_b_folios


def get_token_regime_ordinal(token, token_to_b_folios, folio_to_regime):
    """Get mean REGIME ordinal for a token based on B folios it appears in."""
    b_folios = token_to_b_folios.get(token, set())

    if not b_folios:
        return None

    ordinals = []
    for folio in b_folios:
        regime = folio_to_regime.get(folio)
        if regime and regime in REGIME_ORDINAL:
            ordinals.append(REGIME_ORDINAL[regime])

    if not ordinals:
        return None

    return np.mean(ordinals)


def compute_position_regime_correlation(entries, token_to_b_folios, folio_to_regime, shuffle=False):
    """
    Compute correlation between token position and REGIME ordinal.

    Returns:
        positions: list of positions (1, 2, 3, ...)
        ordinals: list of mean REGIME ordinals
        tau: Kendall's tau
        p_value: p-value for tau
    """
    positions = []
    ordinals = []

    for (folio, line), tokens in entries.items():
        if shuffle:
            tokens = tokens.copy()
            random.shuffle(tokens)

        for pos, token in enumerate(tokens, 1):
            regime_ordinal = get_token_regime_ordinal(token, token_to_b_folios, folio_to_regime)
            if regime_ordinal is not None:
                positions.append(pos)
                ordinals.append(regime_ordinal)

    if len(positions) < 10:
        return positions, ordinals, None, None

    tau, p_value = stats.kendalltau(positions, ordinals)
    return positions, ordinals, tau, p_value


def run_permutation_test(entries, token_to_b_folios, folio_to_regime, n_permutations=1000):
    """Run permutation test to get null distribution."""
    null_taus = []

    for _ in range(n_permutations):
        _, _, tau, _ = compute_position_regime_correlation(
            entries, token_to_b_folios, folio_to_regime, shuffle=True
        )
        if tau is not None:
            null_taus.append(tau)

    return null_taus


def main():
    print("=" * 70)
    print("A-ORCHESTRATION HYPOTHESIS TEST")
    print("Does token position within A entries encode REGIME trajectory?")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    data = load_data()
    folio_to_regime = load_regime_mapping()

    print(f"    Total tokens: {len(data)}")
    print(f"    Folios with REGIME: {len(folio_to_regime)}")

    # Build A entries
    print("\n[2] Building A entries (3+ tokens)...")
    entries = build_a_entries(data)

    total_entries = len(entries)
    total_tokens = sum(len(v) for v in entries.values())
    avg_length = total_tokens / total_entries if total_entries > 0 else 0

    print(f"    Multi-token entries (3+): {total_entries}")
    print(f"    Total tokens in entries: {total_tokens}")
    print(f"    Average entry length: {avg_length:.1f}")

    # Length distribution
    lengths = [len(v) for v in entries.values()]
    length_dist = Counter(lengths)
    print(f"    Length distribution: {dict(sorted(length_dist.items()))}")

    # Build B vocabulary
    print("\n[3] Building B vocabulary index...")
    token_to_b_folios = build_b_vocabulary(data, folio_to_regime)

    # Check A->B vocabulary overlap
    a_vocab = set()
    for tokens in entries.values():
        a_vocab.update(tokens)

    a_in_b = sum(1 for t in a_vocab if t in token_to_b_folios)
    print(f"    Unique A tokens: {len(a_vocab)}")
    print(f"    A tokens appearing in B: {a_in_b} ({100*a_in_b/len(a_vocab):.1f}%)")

    # Main test
    print("\n[4] Computing position-REGIME correlation...")
    positions, ordinals, tau, p_value = compute_position_regime_correlation(
        entries, token_to_b_folios, folio_to_regime, shuffle=False
    )

    print(f"    Data points: {len(positions)}")
    print(f"    Kendall's tau: {tau:.4f}" if tau else "    Insufficient data")
    print(f"    p-value: {p_value:.6f}" if p_value else "")

    # Position-wise analysis
    print("\n[5] Position-wise REGIME ordinal breakdown:")
    pos_ordinals = defaultdict(list)
    for p, o in zip(positions, ordinals):
        pos_ordinals[p].append(o)

    print(f"    {'Position':<10} {'Mean Ordinal':<15} {'N':<8} {'Std':<10}")
    print("    " + "-" * 45)
    for pos in sorted(pos_ordinals.keys())[:10]:  # First 10 positions
        vals = pos_ordinals[pos]
        mean_ord = np.mean(vals)
        std_ord = np.std(vals)
        print(f"    {pos:<10} {mean_ord:<15.3f} {len(vals):<8} {std_ord:<10.3f}")

    # Permutation test
    print("\n[6] Running permutation test (1000 shuffles)...")
    null_taus = run_permutation_test(entries, token_to_b_folios, folio_to_regime, n_permutations=1000)

    null_mean = np.mean(null_taus)
    null_std = np.std(null_taus)
    null_95 = np.percentile(null_taus, 95)

    print(f"    Null distribution: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"    95th percentile: {null_95:.4f}")
    print(f"    Observed tau: {tau:.4f}" if tau else "    Insufficient data")

    if tau is not None:
        # How many null taus are >= observed?
        p_perm = sum(1 for t in null_taus if t >= tau) / len(null_taus)
        print(f"    Permutation p-value: {p_perm:.4f}")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if tau is None:
        verdict = "INSUFFICIENT_DATA"
        explanation = "Not enough data points to compute correlation"
    elif abs(tau) < 0.05:
        verdict = "FALSIFIED"
        explanation = f"No meaningful correlation (tau={tau:.4f})"
    elif tau > 0 and p_value < 0.01:
        # Check if effect survives shuffling
        if null_mean > 0.05:
            verdict = "VOCABULARY_EFFECT"
            explanation = f"Correlation exists (tau={tau:.4f}) but survives shuffling - vocabulary-driven, not position-driven"
        else:
            verdict = "SUPPORTS"
            explanation = f"Positive correlation (tau={tau:.4f}, p={p_value:.6f}) that disappears with shuffling"
    elif tau < 0 and p_value < 0.01:
        verdict = "INVERTED"
        explanation = f"Negative correlation (tau={tau:.4f}) - opposite of prediction"
    else:
        verdict = "INCONCLUSIVE"
        explanation = f"tau={tau:.4f}, p={p_value:.4f} - weak or non-significant effect"

    print(f"\n    Result: {verdict}")
    print(f"    Explanation: {explanation}")

    # Save results
    results = {
        'hypothesis': 'A token position encodes REGIME trajectory',
        'entries_tested': total_entries,
        'tokens_tested': total_tokens,
        'data_points': len(positions),
        'kendall_tau': tau,
        'p_value': p_value,
        'null_distribution': {
            'mean': null_mean,
            'std': null_std,
            'p95': null_95
        },
        'position_ordinals': {
            str(k): {'mean': np.mean(v), 'std': np.std(v), 'n': len(v)}
            for k, v in pos_ordinals.items()
        },
        'verdict': verdict,
        'explanation': explanation
    }

    output_path = project_root / 'results' / 'a_orchestration_test.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n    Results saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()

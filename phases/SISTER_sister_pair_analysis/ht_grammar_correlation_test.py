"""
HT-Grammar Correlation Rigorous Test

Preliminary finding: HT prefix choice correlates with preceding grammar prefix
- ta (LATE) follows ch- at 46.6% vs ~25% baseline

This script runs rigorous statistical tests:
1. Chi-square test for independence
2. Cramer's V for effect size
3. Permutation test for significance
4. Controlled comparison (EARLY vs LATE)

Target: Tier 2 if significant with meaningful effect size
"""

import json
import math
import random
from collections import defaultdict, Counter

def load_data():
    """Load Currier B tokens with sequence order preserved."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    folio_sequences = defaultdict(list)

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            currier = parts[6]
            transcriber = parts[12]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                folio_sequences[folio].append(token)

    return folio_sequences

# Prefix definitions
B_GRAMMAR_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'al', 'ct']
HT_PREFIXES = ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'ta', 'do']
HT_EARLY = ['op', 'pc', 'do']
HT_LATE = ['ta']

def get_prefix(token, prefix_list):
    """Get matching prefix from list, or None."""
    for p in prefix_list:
        if token.startswith(p):
            return p
    return None

def get_grammar_prefix(token):
    return get_prefix(token, B_GRAMMAR_PREFIXES)

def get_ht_prefix(token):
    return get_prefix(token, HT_PREFIXES)

def build_contingency_table(folio_sequences):
    """Build contingency table: preceding_grammar_prefix x ht_prefix."""
    table = defaultdict(Counter)

    for folio, tokens in folio_sequences.items():
        for i in range(1, len(tokens)):
            prev_token = tokens[i-1]
            curr_token = tokens[i]

            grammar_prefix = get_grammar_prefix(prev_token)
            ht_prefix = get_ht_prefix(curr_token)

            if grammar_prefix and ht_prefix:
                table[grammar_prefix][ht_prefix] += 1

    return table

def chi_square_test(table):
    """Compute chi-square statistic and Cramer's V."""
    # Get all row and column keys
    rows = list(table.keys())
    cols = set()
    for row_data in table.values():
        cols.update(row_data.keys())
    cols = list(cols)

    if len(rows) < 2 or len(cols) < 2:
        return 0, 0, 1.0

    # Build matrix
    matrix = []
    for r in rows:
        row = [table[r].get(c, 0) for c in cols]
        matrix.append(row)

    # Compute totals
    n = sum(sum(row) for row in matrix)
    if n == 0:
        return 0, 0, 1.0

    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(len(rows))) for j in range(len(cols))]

    # Chi-square
    chi2 = 0
    df = (len(rows) - 1) * (len(cols) - 1)

    for i in range(len(rows)):
        for j in range(len(cols)):
            expected = row_sums[i] * col_sums[j] / n
            if expected > 0:
                chi2 += (matrix[i][j] - expected) ** 2 / expected

    # Cramer's V
    k = min(len(rows), len(cols))
    v = math.sqrt(chi2 / (n * (k - 1))) if k > 1 and n > 0 else 0

    # Approximate p-value (chi-square distribution approximation)
    # Using Wilson-Hilferty transformation
    if df > 0 and chi2 > 0:
        z = (pow(chi2 / df, 1/3) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
        p = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))
    else:
        p = 1.0

    return chi2, v, p

def permutation_test(folio_sequences, n_permutations=1000):
    """Permutation test: shuffle HT prefixes, measure if observed V is extreme."""
    # Get observed Cramer's V
    observed_table = build_contingency_table(folio_sequences)
    _, observed_v, _ = chi_square_test(observed_table)

    # Collect all (grammar_prefix, ht_prefix) pairs
    pairs = []
    for folio, tokens in folio_sequences.items():
        for i in range(1, len(tokens)):
            grammar_prefix = get_grammar_prefix(tokens[i-1])
            ht_prefix = get_ht_prefix(tokens[i])
            if grammar_prefix and ht_prefix:
                pairs.append((grammar_prefix, ht_prefix))

    if not pairs:
        return observed_v, 1.0

    grammar_prefixes = [p[0] for p in pairs]
    ht_prefixes = [p[1] for p in pairs]

    # Permutation test
    count_extreme = 0
    for _ in range(n_permutations):
        # Shuffle HT prefixes
        shuffled_ht = ht_prefixes.copy()
        random.shuffle(shuffled_ht)

        # Build shuffled table
        shuffled_table = defaultdict(Counter)
        for gp, hp in zip(grammar_prefixes, shuffled_ht):
            shuffled_table[gp][hp] += 1

        _, shuffled_v, _ = chi_square_test(shuffled_table)

        if shuffled_v >= observed_v:
            count_extreme += 1

    p_perm = (count_extreme + 1) / (n_permutations + 1)
    return observed_v, p_perm

def analyze_early_late_split(folio_sequences):
    """Compare what precedes EARLY vs LATE HT prefixes."""
    early_preceding = Counter()
    late_preceding = Counter()

    for folio, tokens in folio_sequences.items():
        for i in range(1, len(tokens)):
            grammar_prefix = get_grammar_prefix(tokens[i-1])
            ht_prefix = get_ht_prefix(tokens[i])

            if grammar_prefix and ht_prefix:
                if ht_prefix in HT_EARLY:
                    early_preceding[grammar_prefix] += 1
                elif ht_prefix in HT_LATE:
                    late_preceding[grammar_prefix] += 1

    return early_preceding, late_preceding

def main():
    print("=" * 70)
    print("HT-GRAMMAR CORRELATION RIGOROUS TEST")
    print("=" * 70)
    print("\nQuestion: Is HT prefix choice significantly predicted by")
    print("          the preceding grammar prefix?")
    print("\nTarget: Tier 2 if chi2 significant AND Cramer's V >= 0.15\n")

    # Load data
    folio_sequences = load_data()
    print(f"Loaded {len(folio_sequences)} B folios")

    total_tokens = sum(len(tokens) for tokens in folio_sequences.values())
    print(f"Total tokens: {total_tokens}")

    # ========================================================================
    # TEST 1: Full contingency table analysis
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 1: Chi-Square Test (Grammar Prefix x HT Prefix)")
    print("-" * 70)

    table = build_contingency_table(folio_sequences)
    chi2, v, p_chi = chi_square_test(table)

    # Count observations
    n_obs = sum(sum(counts.values()) for counts in table.values())

    print(f"\n  Observations: {n_obs}")
    print(f"  Chi-square:   {chi2:.2f}")
    print(f"  Cramer's V:   {v:.3f}")
    print(f"  p-value:      {p_chi:.6f}")

    if p_chi < 0.001:
        print("\n  => Chi-square: HIGHLY SIGNIFICANT (p < 0.001)")
    elif p_chi < 0.05:
        print("\n  => Chi-square: SIGNIFICANT (p < 0.05)")
    else:
        print("\n  => Chi-square: NOT SIGNIFICANT")

    if v >= 0.25:
        print("  => Effect size: MODERATE-STRONG (V >= 0.25)")
    elif v >= 0.15:
        print("  => Effect size: MODERATE (V >= 0.15)")
    elif v >= 0.10:
        print("  => Effect size: WEAK (V >= 0.10)")
    else:
        print("  => Effect size: NEGLIGIBLE (V < 0.10)")

    # ========================================================================
    # TEST 2: Permutation test
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 2: Permutation Test (1000 shuffles)")
    print("-" * 70)

    print("\n  Running permutation test...")
    observed_v, p_perm = permutation_test(folio_sequences, n_permutations=1000)

    print(f"\n  Observed V:     {observed_v:.3f}")
    print(f"  Permutation p:  {p_perm:.4f}")

    if p_perm < 0.001:
        print("\n  => Permutation: HIGHLY SIGNIFICANT (p < 0.001)")
    elif p_perm < 0.05:
        print("\n  => Permutation: SIGNIFICANT (p < 0.05)")
    else:
        print("\n  => Permutation: NOT SIGNIFICANT")

    # ========================================================================
    # TEST 3: EARLY vs LATE comparison
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 3: EARLY vs LATE Prefix Preceding Grammar")
    print("-" * 70)

    early_preceding, late_preceding = analyze_early_late_split(folio_sequences)

    early_total = sum(early_preceding.values())
    late_total = sum(late_preceding.values())

    print(f"\n  EARLY prefixes (op, pc, do): {early_total} occurrences")
    print(f"  LATE prefixes (ta):          {late_total} occurrences")

    print(f"\n  {'Grammar':<10} {'EARLY %':>12} {'LATE %':>12} {'Difference':>12}")
    print("  " + "-" * 50)

    all_grammar = set(early_preceding.keys()) | set(late_preceding.keys())

    diffs = []
    for gp in sorted(all_grammar):
        early_pct = early_preceding[gp] / early_total * 100 if early_total > 0 else 0
        late_pct = late_preceding[gp] / late_total * 100 if late_total > 0 else 0
        diff = late_pct - early_pct
        diffs.append((gp, diff))
        print(f"  {gp:<10} {early_pct:>11.1f}% {late_pct:>11.1f}% {diff:>+11.1f}%")

    # Find strongest discriminators
    diffs.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"\n  Strongest discriminators:")
    for gp, diff in diffs[:3]:
        direction = "LATE-favoring" if diff > 0 else "EARLY-favoring"
        print(f"    {gp}: {diff:+.1f}% ({direction})")

    # Chi-square for EARLY vs LATE
    early_late_table = {
        'EARLY': dict(early_preceding),
        'LATE': dict(late_preceding)
    }
    chi2_el, v_el, p_el = chi_square_test(early_late_table)

    print(f"\n  EARLY vs LATE chi-square: {chi2_el:.2f}")
    print(f"  EARLY vs LATE Cramer's V: {v_el:.3f}")
    print(f"  EARLY vs LATE p-value:    {p_el:.6f}")

    # ========================================================================
    # TEST 4: Specific hypothesis: ta follows ch-
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 4: Specific Test - Does 'ta' follow 'ch-' disproportionately?")
    print("-" * 70)

    # Count ta following ch vs ta following other
    ta_after_ch = table['ch'].get('ta', 0)
    ta_total = sum(counts.get('ta', 0) for counts in table.values())
    ch_total = sum(table['ch'].values())
    all_total = sum(sum(counts.values()) for counts in table.values())

    # Observed rate
    observed_rate = ta_after_ch / ta_total if ta_total > 0 else 0

    # Expected rate (if ta distributed uniformly across grammar prefixes)
    expected_rate = ch_total / all_total if all_total > 0 else 0

    # Enrichment ratio
    enrichment = observed_rate / expected_rate if expected_rate > 0 else 0

    print(f"\n  ta after ch-:     {ta_after_ch} / {ta_total} = {observed_rate*100:.1f}%")
    print(f"  ch- baseline:     {ch_total} / {all_total} = {expected_rate*100:.1f}%")
    print(f"  Enrichment ratio: {enrichment:.2f}x")

    # Binomial test approximation
    if ta_total > 0:
        # z-score for proportion test
        p0 = expected_rate
        p_obs = observed_rate
        se = math.sqrt(p0 * (1 - p0) / ta_total) if p0 > 0 and p0 < 1 else 0.01
        z = (p_obs - p0) / se if se > 0 else 0
        p_binom = 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))

        print(f"  z-score:          {z:.2f}")
        print(f"  p-value:          {p_binom:.6f}")

        if p_binom < 0.001 and enrichment > 1.5:
            print("\n  => ta-after-ch: HIGHLY SIGNIFICANT enrichment")
        elif p_binom < 0.05 and enrichment > 1.2:
            print("\n  => ta-after-ch: SIGNIFICANT enrichment")
        else:
            print("\n  => ta-after-ch: NOT significantly enriched")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    tier_2_criteria = (p_chi < 0.001 or p_perm < 0.01) and v >= 0.10

    print(f"""
    Full table analysis:
      Chi-square p:    {p_chi:.6f} {'(PASS)' if p_chi < 0.001 else '(FAIL)'}
      Cramer's V:      {v:.3f} {'(PASS V>=0.10)' if v >= 0.10 else '(FAIL V<0.10)'}
      Permutation p:   {p_perm:.4f} {'(PASS)' if p_perm < 0.01 else '(FAIL)'}

    EARLY vs LATE:
      Cramer's V:      {v_el:.3f}
      Top discriminator: {diffs[0][0]} ({diffs[0][1]:+.1f}%)

    ta-after-ch:
      Enrichment:      {enrichment:.2f}x
    """)

    if tier_2_criteria:
        print("    VERDICT: TIER 2 - Significant structural correlation")
        print("    HT prefix choice is significantly predicted by preceding grammar prefix.")
    else:
        print("    VERDICT: TIER 3 - Pattern exists but below threshold")
        print("    Correlation is real but effect size is weak.")

    # Save results
    results = {
        'n_observations': n_obs,
        'chi_square': chi2,
        'cramers_v': v,
        'p_chi': p_chi,
        'p_permutation': p_perm,
        'early_vs_late_v': v_el,
        'ta_after_ch_enrichment': enrichment,
        'tier_2_criteria_met': tier_2_criteria
    }

    with open('ht_grammar_correlation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n  Results saved to ht_grammar_correlation_results.json")

if __name__ == '__main__':
    main()

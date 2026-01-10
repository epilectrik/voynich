"""
C412 Verification: Sister-Escape Anticorrelation

Replicates EXACT methodology from original SISTER phase to verify C412.

Original claim: ch-preference anticorrelated with qo-escape density in Currier B
               rho = -0.326, p = 0.002, N = 82 folios
"""

from collections import defaultdict
from scipy import stats

DATA_PATH = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

# ============================================================================
# DATA LOADING - Exact replication of original methodology
# ============================================================================

def load_currier_b_data():
    """Load Currier B tokens by folio - EXACT original methodology."""
    folios = defaultdict(list)

    with open(DATA_PATH, 'r', encoding='latin-1') as f:
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

            # EXACT original filters: currier == 'B' AND transcriber == 'H'
            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                folios[folio].append(token)

    return folios

# ============================================================================
# METRICS - Exact replication
# ============================================================================

def is_escape_token(token):
    """Check if token is qo-prefixed escape route."""
    return token.startswith('qo')

def compute_folio_metrics(tokens):
    """Compute ch-preference and escape-density for a folio."""
    if len(tokens) < 10:
        return None

    # Count ch- and sh- prefixed tokens
    ch_count = sum(1 for t in tokens if t.startswith('ch'))
    sh_count = sum(1 for t in tokens if t.startswith('sh'))

    # Require minimum sister pair tokens
    ch_sh_total = ch_count + sh_count
    if ch_sh_total < 5:
        return None

    # CH-PREFERENCE = ch / (ch + sh) - THIS IS THE KEY METRIC
    ch_preference = ch_count / ch_sh_total

    # Escape density = qo-count / total
    escape_count = sum(1 for t in tokens if is_escape_token(t))
    escape_density = escape_count / len(tokens)

    return {
        'ch_count': ch_count,
        'sh_count': sh_count,
        'ch_sh_total': ch_sh_total,
        'ch_preference': ch_preference,
        'escape_count': escape_count,
        'escape_density': escape_density,
        'total_tokens': len(tokens)
    }

# ============================================================================
# MAIN VERIFICATION
# ============================================================================

def main():
    print("=" * 70)
    print("C412 VERIFICATION: Sister-Escape Anticorrelation")
    print("=" * 70)
    print("\nOriginal claim: rho = -0.326, p = 0.002, N = 82")
    print("\nMethodology:")
    print("  - Filter: currier == 'B' AND transcriber == 'H'")
    print("  - ch_preference = ch / (ch + sh)")
    print("  - escape_density = qo_count / total")
    print()

    # Load data with EXACT original filters
    print("Loading Currier B data (transcriber H only)...")
    folios = load_currier_b_data()
    print(f"  Loaded {len(folios)} B folios")

    # Compute metrics for each folio
    print("\nComputing per-folio metrics...")
    folio_metrics = {}

    for folio, tokens in folios.items():
        metrics = compute_folio_metrics(tokens)
        if metrics:
            folio_metrics[folio] = metrics

    print(f"  Valid folios (>=10 tokens, >=5 ch+sh): {len(folio_metrics)}")

    # Extract arrays for correlation
    ch_preferences = [m['ch_preference'] for m in folio_metrics.values()]
    escape_densities = [m['escape_density'] for m in folio_metrics.values()]

    # Compute Spearman correlation
    rho, p = stats.spearmanr(ch_preferences, escape_densities)

    print("\n" + "-" * 70)
    print("VERIFICATION RESULTS")
    print("-" * 70)

    print(f"\n  N (folios):    {len(folio_metrics)}")
    print(f"  Spearman rho:  {rho:.3f}")
    print(f"  p-value:       {p:.4f}")

    print("\n" + "-" * 70)
    print("COMPARISON TO ORIGINAL")
    print("-" * 70)

    print(f"\n  {'Metric':<15} {'Original':<12} {'Verified':<12} {'Match?'}")
    print(f"  {'-'*15} {'-'*12} {'-'*12} {'-'*8}")

    n_match = abs(len(folio_metrics) - 82) <= 2
    rho_match = abs(rho - (-0.326)) < 0.05
    p_match = p < 0.01

    print(f"  {'N':<15} {'82':<12} {len(folio_metrics):<12} {'YES' if n_match else 'NO'}")
    print(f"  {'rho':<15} {'-0.326':<12} {rho:<12.3f} {'YES' if rho_match else 'NO'}")
    print(f"  {'p-value':<15} {'0.002':<12} {p:<12.4f} {'YES' if p_match else 'NO'}")

    print("\n" + "=" * 70)
    if n_match and rho_match and p_match:
        print("VERDICT: C412 CONFIRMED")
        print("  Original results reproduced. Remove review flag.")
    elif rho < -0.2 and p < 0.05:
        print("VERDICT: C412 CONFIRMED (minor variance)")
        print(f"  Effect present but values differ slightly.")
        print(f"  Consider updating C412 with verified values.")
    else:
        print("VERDICT: C412 NOT CONFIRMED")
        print("  Original results NOT reproduced.")
        print("  Requires investigation or constraint revision.")
    print("=" * 70)

    # Additional diagnostics
    print("\n" + "-" * 70)
    print("DIAGNOSTIC: Quartile Analysis")
    print("-" * 70)

    sorted_by_escape = sorted(folio_metrics.items(), key=lambda x: x[1]['escape_density'])
    n = len(sorted_by_escape)
    quartiles = [
        ('Q1 (Low escape)', sorted_by_escape[:n//4]),
        ('Q2', sorted_by_escape[n//4:n//2]),
        ('Q3', sorted_by_escape[n//2:3*n//4]),
        ('Q4 (High escape)', sorted_by_escape[3*n//4:])
    ]

    print(f"\n  {'Quartile':<20} {'N':>5} {'ch-pref':>10} {'escape':>10}")
    print(f"  {'-'*20} {'-'*5} {'-'*10} {'-'*10}")

    for label, members in quartiles:
        if members:
            ch_mean = sum(m['ch_preference'] for _, m in members) / len(members)
            esc_mean = sum(m['escape_density'] for _, m in members) / len(members)
            print(f"  {label:<20} {len(members):>5} {ch_mean:>10.3f} {esc_mean:>10.3f}")

    # Check if pattern is monotonic (ch-pref should decrease as escape increases)
    q_prefs = [sum(m['ch_preference'] for _, m in q[1]) / len(q[1]) if q[1] else 0 for q in quartiles]
    if q_prefs[0] > q_prefs[-1]:
        print("\n  Pattern: ch-preference DECREASES with escape density (as expected)")
    else:
        print("\n  Pattern: ch-preference does NOT decrease with escape density")

if __name__ == '__main__':
    main()

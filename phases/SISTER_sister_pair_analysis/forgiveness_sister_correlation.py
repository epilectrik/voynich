"""
Forgiveness vs Sister Pair Choice Correlation Test

Question: Does sister pair choice (ch vs sh, ok vs ot) correlate with
program forgiveness (hazard density, escape availability)?

Hypothesis: If ch-forms correlate with brittle programs, sister pairs may
encode risk tolerance or operator competency requirements.

Tier 2 investigation - structural correlation test.
"""

import json
import math
from collections import defaultdict, Counter
import statistics

# ============================================================================
# DATA LOADING
# ============================================================================

def load_currier_b_data():
    """Load Currier B tokens by folio with full context."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    folios = defaultdict(list)
    folio_sections = {}

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
            section = parts[3]
            currier = parts[6]
            transcriber = parts[12]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                folios[folio].append(token)
                folio_sections[folio] = section

    return folios, folio_sections

# ============================================================================
# FORGIVENESS METRICS (from SITD phase)
# ============================================================================

# Known hazard tokens
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_TOKENS = HAZARD_SOURCES | HAZARD_TARGETS

def is_hazard_token(token):
    return token in HAZARD_TOKENS

def is_escape_token(token):
    return token.startswith('qo')

def compute_forgiveness_metrics(tokens):
    """Compute forgiveness score for a program."""
    if len(tokens) < 10:
        return None

    # Hazard density
    hazard_count = sum(1 for t in tokens if is_hazard_token(t))
    hazard_density = hazard_count / len(tokens)

    # Escape density
    escape_count = sum(1 for t in tokens if is_escape_token(t))
    escape_density = escape_count / len(tokens)

    # Max safe run
    max_safe_run = 0
    current_run = 0
    for t in tokens:
        if is_hazard_token(t):
            max_safe_run = max(max_safe_run, current_run)
            current_run = 0
        else:
            current_run += 1
    max_safe_run = max(max_safe_run, current_run)

    # Combined forgiveness score
    score = 0
    score -= hazard_density * 10
    score += escape_density * 10
    score += min(max_safe_run, 50) / 50

    return {
        'hazard_density': hazard_density,
        'escape_density': escape_density,
        'max_safe_run': max_safe_run,
        'forgiveness': score
    }

# ============================================================================
# SISTER PAIR METRICS
# ============================================================================

def compute_sister_pair_metrics(tokens):
    """Compute sister pair preference ratios for a program."""
    # Count ch- vs sh- prefixed tokens
    ch_count = sum(1 for t in tokens if t.startswith('ch'))
    sh_count = sum(1 for t in tokens if t.startswith('sh'))

    # Count ok- vs ot- prefixed tokens
    ok_count = sum(1 for t in tokens if t.startswith('ok'))
    ot_count = sum(1 for t in tokens if t.startswith('ot'))

    # Compute preference ratios (0 = all sh/ot, 1 = all ch/ok)
    ch_sh_total = ch_count + sh_count
    ch_preference = ch_count / ch_sh_total if ch_sh_total > 0 else 0.5

    ok_ot_total = ok_count + ot_count
    ok_preference = ok_count / ok_ot_total if ok_ot_total > 0 else 0.5

    return {
        'ch_count': ch_count,
        'sh_count': sh_count,
        'ch_sh_total': ch_sh_total,
        'ch_preference': ch_preference,
        'ok_count': ok_count,
        'ot_count': ot_count,
        'ok_ot_total': ok_ot_total,
        'ok_preference': ok_preference
    }

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

def pearson_correlation(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return 0, 1.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
    std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) / n)
    std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y) / n)

    if std_x == 0 or std_y == 0:
        return 0, 1.0

    r = cov / (std_x * std_y)

    # Approximate p-value using t-distribution approximation
    if abs(r) >= 1:
        p = 0.0
    else:
        t = r * math.sqrt((n - 2) / (1 - r * r))
        # Rough p-value approximation
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))

    return r, p

def spearman_correlation(x, y):
    """Compute Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0, 1.0

    # Convert to ranks
    def rank(values):
        sorted_indices = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0] * len(values)
        for rank_val, idx in enumerate(sorted_indices):
            ranks[idx] = rank_val + 1
        return ranks

    rank_x = rank(x)
    rank_y = rank(y)

    return pearson_correlation(rank_x, rank_y)

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 70)
    print("FORGIVENESS VS SISTER PAIR CHOICE CORRELATION")
    print("=" * 70)
    print("\nHypothesis: Sister pair choice correlates with program forgiveness")
    print("  - ch-forms may indicate higher-risk/brittle programs")
    print("  - sh-forms may indicate forgiving/recovery-friendly programs")
    print()

    # Load data
    print("Loading Currier B data...")
    folios, folio_sections = load_currier_b_data()
    print(f"  Loaded {len(folios)} B folios")

    # Compute metrics for each program
    print("\nComputing metrics...")
    program_data = {}

    for folio, tokens in folios.items():
        forg = compute_forgiveness_metrics(tokens)
        sister = compute_sister_pair_metrics(tokens)

        if forg and sister['ch_sh_total'] >= 5:  # Need minimum data
            program_data[folio] = {
                **forg,
                **sister,
                'section': folio_sections.get(folio, '?'),
                'token_count': len(tokens)
            }

    print(f"  Programs with sufficient data: {len(program_data)}")

    # ========================================================================
    # TEST 1: Forgiveness vs ch-preference correlation
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 1: Forgiveness Score vs ch-Preference")
    print("-" * 70)

    forgiveness = [m['forgiveness'] for m in program_data.values()]
    ch_pref = [m['ch_preference'] for m in program_data.values()]

    r_pearson, p_pearson = pearson_correlation(forgiveness, ch_pref)
    r_spearman, p_spearman = spearman_correlation(forgiveness, ch_pref)

    print(f"\n  Pearson r   = {r_pearson:+.3f} (p = {p_pearson:.4f})")
    print(f"  Spearman rho = {r_spearman:+.3f} (p = {p_spearman:.4f})")

    if abs(r_spearman) > 0.3 and p_spearman < 0.05:
        print("\n  => SIGNIFICANT CORRELATION DETECTED")
        if r_spearman > 0:
            print("  => More forgiving programs prefer ch-forms")
        else:
            print("  => More brittle programs prefer ch-forms")
    else:
        print("\n  => NO significant correlation (independent axes)")

    # ========================================================================
    # TEST 2: Component-level correlations
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 2: Component-Level Correlations")
    print("-" * 70)

    hazard = [m['hazard_density'] for m in program_data.values()]
    escape = [m['escape_density'] for m in program_data.values()]
    safe_run = [m['max_safe_run'] for m in program_data.values()]

    r_haz, p_haz = spearman_correlation(hazard, ch_pref)
    r_esc, p_esc = spearman_correlation(escape, ch_pref)
    r_safe, p_safe = spearman_correlation(safe_run, ch_pref)

    print(f"\n  Hazard density vs ch-pref:   rho = {r_haz:+.3f} (p = {p_haz:.4f})")
    print(f"  Escape density vs ch-pref:   rho = {r_esc:+.3f} (p = {p_esc:.4f})")
    print(f"  Max safe run vs ch-pref:     rho = {r_safe:+.3f} (p = {p_safe:.4f})")

    # ========================================================================
    # TEST 3: ok/ot pair correlation
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 3: ok/ot Preference Correlation")
    print("-" * 70)

    # Filter to programs with sufficient ok/ot tokens
    ok_data = {f: m for f, m in program_data.items() if m['ok_ot_total'] >= 5}
    print(f"\n  Programs with >=5 ok/ot tokens: {len(ok_data)}")

    if len(ok_data) >= 10:
        forgiveness_ok = [m['forgiveness'] for m in ok_data.values()]
        ok_pref = [m['ok_preference'] for m in ok_data.values()]

        r_ok, p_ok = spearman_correlation(forgiveness_ok, ok_pref)
        print(f"  Forgiveness vs ok-preference: rho = {r_ok:+.3f} (p = {p_ok:.4f})")

        # Test if ch and ok preferences correlate
        ch_from_ok = [program_data[f]['ch_preference'] for f in ok_data.keys()]
        r_chok, p_chok = spearman_correlation(ch_from_ok, ok_pref)
        print(f"  ch-preference vs ok-preference: rho = {r_chok:+.3f} (p = {p_chok:.4f})")
    else:
        print("  Insufficient data for ok/ot analysis")

    # ========================================================================
    # TEST 4: Section breakdown
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 4: Section-Stratified Analysis")
    print("-" * 70)

    by_section = defaultdict(list)
    for folio, m in program_data.items():
        by_section[m['section']].append(m)

    print(f"\n  {'Section':<10} {'N':>5} {'Forg_mean':>10} {'ch_pref':>10} {'Correlation':>12}")
    print("  " + "-" * 50)

    for section in sorted(by_section.keys()):
        programs = by_section[section]
        if len(programs) >= 5:
            forg_vals = [m['forgiveness'] for m in programs]
            ch_vals = [m['ch_preference'] for m in programs]

            r_sect, p_sect = spearman_correlation(forg_vals, ch_vals) if len(programs) >= 5 else (0, 1)

            print(f"  {section:<10} {len(programs):>5} {statistics.mean(forg_vals):>10.3f} "
                  f"{statistics.mean(ch_vals):>10.3f} {r_sect:>+.3f} (p={p_sect:.2f})")

    # ========================================================================
    # TEST 5: Quartile analysis
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 5: Forgiveness Quartile vs Sister Pair Preference")
    print("-" * 70)

    sorted_by_forg = sorted(program_data.items(), key=lambda x: x[1]['forgiveness'])
    n = len(sorted_by_forg)
    quartiles = [
        ('Q1 (Brittle)', sorted_by_forg[:n//4]),
        ('Q2', sorted_by_forg[n//4:n//2]),
        ('Q3', sorted_by_forg[n//2:3*n//4]),
        ('Q4 (Forgiving)', sorted_by_forg[3*n//4:])
    ]

    print(f"\n  {'Quartile':<16} {'N':>5} {'Forgiveness':>12} {'ch_pref':>10} {'ch_count':>10} {'sh_count':>10}")
    print("  " + "-" * 70)

    quartile_ch_prefs = []
    for label, members in quartiles:
        if members:
            forg_mean = statistics.mean([m['forgiveness'] for _, m in members])
            ch_pref_mean = statistics.mean([m['ch_preference'] for _, m in members])
            ch_sum = sum(m['ch_count'] for _, m in members)
            sh_sum = sum(m['sh_count'] for _, m in members)

            quartile_ch_prefs.append((label, ch_pref_mean))

            print(f"  {label:<16} {len(members):>5} {forg_mean:>12.3f} "
                  f"{ch_pref_mean:>10.3f} {ch_sum:>10} {sh_sum:>10}")

    # Test monotonicity
    if len(quartile_ch_prefs) == 4:
        prefs = [p for _, p in quartile_ch_prefs]
        if prefs == sorted(prefs):
            print("\n  => ch-preference INCREASES with forgiveness (monotonic)")
        elif prefs == sorted(prefs, reverse=True):
            print("\n  => ch-preference DECREASES with forgiveness (monotonic)")
        else:
            print("\n  => No monotonic relationship detected")

    # ========================================================================
    # TEST 6: Extreme program analysis
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 6: Extreme Programs")
    print("-" * 70)

    # Top 5 most brittle
    print("\n  Most BRITTLE programs (lowest forgiveness):")
    print(f"  {'Folio':<10} {'Forgiveness':>12} {'ch_pref':>10} {'ch':>6} {'sh':>6}")
    for folio, m in sorted_by_forg[:5]:
        print(f"  {folio:<10} {m['forgiveness']:>12.3f} {m['ch_preference']:>10.3f} "
              f"{m['ch_count']:>6} {m['sh_count']:>6}")

    # Top 5 most forgiving
    print("\n  Most FORGIVING programs (highest forgiveness):")
    for folio, m in sorted_by_forg[-5:]:
        print(f"  {folio:<10} {m['forgiveness']:>12.3f} {m['ch_preference']:>10.3f} "
              f"{m['ch_count']:>6} {m['sh_count']:>6}")

    # ========================================================================
    # TEST 7: Restart folios analysis
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 7: Restart-Capable Folios")
    print("-" * 70)

    restart_folios = ['f50v', 'f57r', 'f82v']
    restart_data = {f: program_data[f] for f in restart_folios if f in program_data}

    if restart_data:
        print("\n  Restart-capable programs:")
        print(f"  {'Folio':<10} {'Forgiveness':>12} {'ch_pref':>10} {'Quartile':>12}")

        forg_values = [m['forgiveness'] for m in program_data.values()]
        q1 = sorted(forg_values)[len(forg_values)//4]
        q2 = sorted(forg_values)[len(forg_values)//2]
        q3 = sorted(forg_values)[3*len(forg_values)//4]

        for folio, m in restart_data.items():
            if m['forgiveness'] <= q1:
                q = 'Q1 (Brittle)'
            elif m['forgiveness'] <= q2:
                q = 'Q2'
            elif m['forgiveness'] <= q3:
                q = 'Q3'
            else:
                q = 'Q4 (Forgiving)'
            print(f"  {folio:<10} {m['forgiveness']:>12.3f} {m['ch_preference']:>10.3f} {q:>12}")

        # Compare to population
        pop_forg = statistics.mean(forg_values)
        restart_forg = statistics.mean([m['forgiveness'] for m in restart_data.values()])
        print(f"\n  Population mean forgiveness: {pop_forg:.3f}")
        print(f"  Restart programs mean:       {restart_forg:.3f}")

        if restart_forg > pop_forg:
            print("  => Restart programs are MORE forgiving than average")
        else:
            print("  => Restart programs are LESS forgiving than average")
    else:
        print("  No restart folio data available")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
    Main correlation (Forgiveness vs ch-preference):
      Spearman rho = {r_spearman:+.3f} (p = {p_spearman:.4f})

    Component correlations:
      Hazard density vs ch-pref:  rho = {r_haz:+.3f}
      Escape density vs ch-pref:  rho = {r_esc:+.3f}
      Max safe run vs ch-pref:    rho = {r_safe:+.3f}
    """)

    # Interpretation
    if abs(r_spearman) > 0.3 and p_spearman < 0.05:
        print("    FINDING: SIGNIFICANT CORRELATION")
        print("    Sister pair choice is NOT independent of program forgiveness.")
        if r_spearman > 0:
            print("    Direction: Forgiving programs prefer ch-forms.")
        else:
            print("    Direction: Brittle programs prefer ch-forms.")
        print("\n    Tier assessment: Tier 2 (structural correlation)")
    elif abs(r_spearman) > 0.15:
        print("    FINDING: WEAK CORRELATION")
        print("    There is a trend but it's not statistically robust.")
        print("\n    Tier assessment: Tier 3 (suggestive but not conclusive)")
    else:
        print("    FINDING: NO CORRELATION")
        print("    Sister pair choice and forgiveness are INDEPENDENT axes.")
        print("    They encode different program properties.")
        print("\n    Tier assessment: Closure (independent design dimensions)")

    # Save results
    results = {
        'n_programs': len(program_data),
        'correlation_forgiveness_ch': {
            'spearman_rho': r_spearman,
            'spearman_p': p_spearman,
            'pearson_r': r_pearson,
            'pearson_p': p_pearson
        },
        'component_correlations': {
            'hazard_vs_ch': {'rho': r_haz, 'p': p_haz},
            'escape_vs_ch': {'rho': r_esc, 'p': p_esc},
            'safe_run_vs_ch': {'rho': r_safe, 'p': p_safe}
        },
        'quartile_ch_prefs': dict(quartile_ch_prefs)
    }

    with open('forgiveness_sister_correlation_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n  Results saved to forgiveness_sister_correlation_results.json")

if __name__ == '__main__':
    main()

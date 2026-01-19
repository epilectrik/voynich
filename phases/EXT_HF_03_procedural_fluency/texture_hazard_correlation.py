"""
Cognitive Texture vs Hazard Distribution

Question: Are hazards concentrated in "autopilot" (dense/repetitive) regions
or "attention-demanding" (sparse/varied) regions?

Hypothesis A: Hazards in autopilot regions (operator relaxed, more risk)
Hypothesis B: Hazards in attention regions (demanding work is inherently riskier)
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent

HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}


def load_data():
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # CRITICAL: Filter to H (PRIMARY) transcriber only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip()
                folio = parts[1].strip('"') if len(parts) > 1 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and folio:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'section': section
                    })
    return data


def main():
    print("=" * 70)
    print("COGNITIVE TEXTURE vs HAZARD DISTRIBUTION")
    print("=" * 70)

    data = load_data()

    # Calculate per-folio metrics
    folio_data = defaultdict(lambda: {
        'tokens': [],
        'unique': set(),
        'hazard_count': 0,
        'section': ''
    })

    for d in data:
        token = d['token']
        folio = d['folio']
        section = d['section']

        folio_data[folio]['tokens'].append(token)
        folio_data[folio]['unique'].add(token)
        folio_data[folio]['section'] = section

        if token in HAZARD_TOKENS:
            folio_data[folio]['hazard_count'] += 1

    # Calculate diversity and hazard density per folio
    folio_metrics = []
    for folio, fd in folio_data.items():
        total = len(fd['tokens'])
        if total < 5:  # Skip very short folios
            continue

        diversity = len(fd['unique']) / total
        hazard_density = fd['hazard_count'] / total
        tokens_count = total

        folio_metrics.append({
            'folio': folio,
            'section': fd['section'],
            'diversity': diversity,
            'hazard_density': hazard_density,
            'tokens': tokens_count,
            'hazard_count': fd['hazard_count']
        })

    print(f"\nAnalyzing {len(folio_metrics)} folios (min 5 tokens)")

    # Correlation: diversity vs hazard density
    diversities = [f['diversity'] for f in folio_metrics]
    hazard_densities = [f['hazard_density'] for f in folio_metrics]

    r, p = sp_stats.pearsonr(diversities, hazard_densities)
    rho, p_rho = sp_stats.spearmanr(diversities, hazard_densities)

    print("\n" + "=" * 70)
    print("TEST 1: Folio-Level Diversity vs Hazard Density")
    print("=" * 70)

    print(f"\nPearson r: {r:.3f} (p={p:.4f})")
    print(f"Spearman rho: {rho:.3f} (p={p_rho:.4f})")

    if r < -0.2 and p < 0.05:
        print("\n** NEGATIVE CORRELATION ** More hazards in LOW-diversity (autopilot) regions")
    elif r > 0.2 and p < 0.05:
        print("\n** POSITIVE CORRELATION ** More hazards in HIGH-diversity (attention) regions")
    else:
        print("\n** NO SIGNIFICANT CORRELATION **")

    # Tertile analysis
    print("\n" + "=" * 70)
    print("TEST 2: Tertile Comparison")
    print("=" * 70)

    sorted_by_div = sorted(folio_metrics, key=lambda x: x['diversity'])
    n = len(sorted_by_div)
    low_div = sorted_by_div[:n//3]
    mid_div = sorted_by_div[n//3:2*n//3]
    high_div = sorted_by_div[2*n//3:]

    def tertile_stats(folios, label):
        mean_div = np.mean([f['diversity'] for f in folios])
        mean_haz = np.mean([f['hazard_density'] for f in folios])
        total_haz = sum(f['hazard_count'] for f in folios)
        total_tok = sum(f['tokens'] for f in folios)
        return {
            'label': label,
            'n': len(folios),
            'mean_div': mean_div,
            'mean_haz_density': mean_haz,
            'total_hazards': total_haz,
            'total_tokens': total_tok,
            'hazard_rate': total_haz / total_tok if total_tok > 0 else 0
        }

    low_stats = tertile_stats(low_div, 'Low Diversity (autopilot)')
    mid_stats = tertile_stats(mid_div, 'Mid Diversity')
    high_stats = tertile_stats(high_div, 'High Diversity (attention)')

    print(f"\n{'Tertile':<30} {'N':<6} {'MeanDiv':<10} {'HazRate':<10} {'TotalHaz':<10}")
    print("-" * 70)
    for stats in [low_stats, mid_stats, high_stats]:
        print(f"{stats['label']:<30} {stats['n']:<6} {stats['mean_div']:<10.3f} {stats['hazard_rate']:<10.4f} {stats['total_hazards']:<10}")

    # Statistical test between low and high
    low_haz_rates = [f['hazard_density'] for f in low_div]
    high_haz_rates = [f['hazard_density'] for f in high_div]

    t_stat, t_p = sp_stats.ttest_ind(low_haz_rates, high_haz_rates)
    u_stat, u_p = sp_stats.mannwhitneyu(low_haz_rates, high_haz_rates, alternative='two-sided')

    print(f"\nLow vs High diversity hazard comparison:")
    print(f"  t-test: t={t_stat:.3f}, p={t_p:.4f}")
    print(f"  Mann-Whitney: U={u_stat:.1f}, p={u_p:.4f}")

    # Within-section analysis
    print("\n" + "=" * 70)
    print("TEST 3: Within-Section Texture-Hazard Correlation")
    print("=" * 70)

    sections = set(f['section'] for f in folio_metrics)
    print(f"\n{'Section':<8} {'N':<6} {'r':<10} {'p':<10} {'Direction'}")
    print("-" * 50)

    section_correlations = []
    for section in sorted(sections):
        section_folios = [f for f in folio_metrics if f['section'] == section]
        if len(section_folios) < 10:
            continue

        sec_div = [f['diversity'] for f in section_folios]
        sec_haz = [f['hazard_density'] for f in section_folios]

        r_sec, p_sec = sp_stats.pearsonr(sec_div, sec_haz)
        direction = "+" if r_sec > 0 else "-"
        sig = "*" if p_sec < 0.05 else ""

        section_correlations.append((section, r_sec, p_sec))
        print(f"{section:<8} {len(section_folios):<6} {r_sec:<10.3f} {p_sec:<10.4f} {direction}{sig}")

    # Recipe family analysis (using section as proxy)
    print("\n" + "=" * 70)
    print("TEST 4: Cognitive Texture Profiles")
    print("=" * 70)

    print("\nSection cognitive profiles:")
    print(f"\n{'Section':<8} {'Type':<15} {'MeanDiv':<10} {'MeanHaz':<10} {'Risk Profile'}")
    print("-" * 60)

    for section in sorted(sections):
        section_folios = [f for f in folio_metrics if f['section'] == section]
        if len(section_folios) < 5:
            continue

        mean_div = np.mean([f['diversity'] for f in section_folios])
        mean_haz = np.mean([f['hazard_density'] for f in section_folios])

        if mean_div > 0.25:
            cog_type = "Attention"
        elif mean_div < 0.15:
            cog_type = "Autopilot"
        else:
            cog_type = "Mixed"

        if mean_haz > 0.15:
            risk = "HIGH"
        elif mean_haz < 0.10:
            risk = "LOW"
        else:
            risk = "MODERATE"

        print(f"{section:<8} {cog_type:<15} {mean_div:<10.3f} {mean_haz:<10.3f} {risk}")

    # Synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    print(f"""
Global correlation (diversity vs hazard density):
  r = {r:.3f}, p = {p:.4f}

Tertile hazard rates:
  Low diversity (autopilot): {low_stats['hazard_rate']:.4f}
  High diversity (attention): {high_stats['hazard_rate']:.4f}
  Ratio: {low_stats['hazard_rate']/(high_stats['hazard_rate'] + 0.0001):.2f}x
""")

    if low_stats['hazard_rate'] > high_stats['hazard_rate'] * 1.2:
        print("** FINDING: Hazards concentrate in AUTOPILOT regions **")
        print("   Interpretation: Dense/repetitive work carries more risk")
        print("   Implication: Operator vigilance may decrease during routine procedures")
    elif high_stats['hazard_rate'] > low_stats['hazard_rate'] * 1.2:
        print("** FINDING: Hazards concentrate in ATTENTION regions **")
        print("   Interpretation: Varied work is inherently riskier")
        print("   Implication: Complex procedures require more hazard management")
    else:
        print("** FINDING: Hazards distributed evenly across cognitive textures **")
        print("   Interpretation: Risk is process-inherent, not attention-dependent")


if __name__ == '__main__':
    main()

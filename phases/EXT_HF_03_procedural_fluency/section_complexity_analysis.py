"""
Section Complexity Analysis

Question: What makes sections Z, A more operationally complex than B, H?

Exec diversity:
  Z: 0.333 (highest)
  A: 0.308
  T: 0.253
  C: 0.224
  P: 0.181
  S: 0.114
  H: 0.105
  B: 0.070 (lowest)
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent

HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}
KERNEL_TOKENS = {'k', 'h', 'e', 's', 't', 'd', 'l', 'o', 'c', 'r'}
LINK_TOKENS = {'ol', 'or', 'ar', 'al', 'ain', 'aiin'}


def is_grammar_token(token):
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def load_data():
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').strip()
                folio = parts[1].strip('"') if len(parts) > 1 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and section:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'section': section
                    })
    return data


def main():
    print("=" * 70)
    print("SECTION COMPLEXITY ANALYSIS")
    print("=" * 70)
    print("\nQuestion: What makes Z, A more complex than B, H?")

    data = load_data()

    # Aggregate by section
    section_data = defaultdict(lambda: {
        'tokens': [],
        'unique': set(),
        'hazard_count': 0,
        'link_count': 0,
        'kernel_count': 0,
        'grammar_count': 0,
        'folios': set(),
    })

    for d in data:
        token = d['token']
        section = d['section']
        folio = d['folio']

        section_data[section]['tokens'].append(token)
        section_data[section]['unique'].add(token)
        section_data[section]['folios'].add(folio)

        if token in HAZARD_TOKENS:
            section_data[section]['hazard_count'] += 1
        if token in LINK_TOKENS:
            section_data[section]['link_count'] += 1
        if token in KERNEL_TOKENS:
            section_data[section]['kernel_count'] += 1
        if is_grammar_token(token):
            section_data[section]['grammar_count'] += 1

    sections = sorted(section_data.keys())

    # Calculate metrics
    print("\n" + "=" * 70)
    print("BASIC METRICS BY SECTION")
    print("=" * 70)

    print(f"\n{'Sec':<4} {'Tokens':<8} {'Unique':<8} {'Divers':<8} {'Folios':<8} {'Tok/Fol':<8}")
    print("-" * 48)

    metrics = {}
    for s in sections:
        total = len(section_data[s]['tokens'])
        unique = len(section_data[s]['unique'])
        diversity = unique / total if total > 0 else 0
        folios = len(section_data[s]['folios'])
        tok_per_folio = total / folios if folios > 0 else 0

        metrics[s] = {
            'total': total,
            'unique': unique,
            'diversity': diversity,
            'folios': folios,
            'tok_per_folio': tok_per_folio,
        }
        print(f"{s:<4} {total:<8} {unique:<8} {diversity:<8.3f} {folios:<8} {tok_per_folio:<8.1f}")

    # Operational character
    print("\n" + "=" * 70)
    print("OPERATIONAL CHARACTER BY SECTION")
    print("=" * 70)

    print(f"\n{'Sec':<4} {'Hazard%':<10} {'LINK%':<10} {'Kernel%':<10} {'Grammar%':<10}")
    print("-" * 48)

    for s in sections:
        total = len(section_data[s]['tokens'])
        hazard_pct = 100 * section_data[s]['hazard_count'] / total if total > 0 else 0
        link_pct = 100 * section_data[s]['link_count'] / total if total > 0 else 0
        kernel_pct = 100 * section_data[s]['kernel_count'] / total if total > 0 else 0
        grammar_pct = 100 * section_data[s]['grammar_count'] / total if total > 0 else 0

        metrics[s]['hazard_pct'] = hazard_pct
        metrics[s]['link_pct'] = link_pct
        metrics[s]['kernel_pct'] = kernel_pct
        metrics[s]['grammar_pct'] = grammar_pct

        print(f"{s:<4} {hazard_pct:<10.1f} {link_pct:<10.1f} {kernel_pct:<10.1f} {grammar_pct:<10.1f}")

    # Token frequency distribution (Zipf analysis)
    print("\n" + "=" * 70)
    print("VOCABULARY CONCENTRATION (Top-10 Token Share)")
    print("=" * 70)

    print(f"\n{'Sec':<4} {'Top10%':<10} {'Top1 Token':<15} {'Top1%':<10}")
    print("-" * 48)

    for s in sections:
        token_counts = Counter(section_data[s]['tokens'])
        total = len(section_data[s]['tokens'])
        top_10 = token_counts.most_common(10)
        top_10_count = sum(c for _, c in top_10)
        top_10_pct = 100 * top_10_count / total if total > 0 else 0

        top_1_token, top_1_count = top_10[0] if top_10 else ('', 0)
        top_1_pct = 100 * top_1_count / total if total > 0 else 0

        metrics[s]['top10_pct'] = top_10_pct
        metrics[s]['top1_token'] = top_1_token
        metrics[s]['top1_pct'] = top_1_pct

        print(f"{s:<4} {top_10_pct:<10.1f} {top_1_token:<15} {top_1_pct:<10.1f}")

    # Token length distribution
    print("\n" + "=" * 70)
    print("TOKEN LENGTH DISTRIBUTION")
    print("=" * 70)

    print(f"\n{'Sec':<4} {'MeanLen':<10} {'StdLen':<10} {'Short%':<10} {'Long%':<10}")
    print("-" * 48)

    for s in sections:
        lengths = [len(t) for t in section_data[s]['tokens']]
        mean_len = np.mean(lengths)
        std_len = np.std(lengths)
        short_pct = 100 * sum(1 for l in lengths if l <= 3) / len(lengths)
        long_pct = 100 * sum(1 for l in lengths if l >= 7) / len(lengths)

        metrics[s]['mean_len'] = mean_len
        metrics[s]['std_len'] = std_len

        print(f"{s:<4} {mean_len:<10.2f} {std_len:<10.2f} {short_pct:<10.1f} {long_pct:<10.1f}")

    # Unique prefix/suffix analysis
    print("\n" + "=" * 70)
    print("MORPHOLOGICAL VARIETY (Unique Prefixes/Suffixes)")
    print("=" * 70)

    print(f"\n{'Sec':<4} {'UniqPfx':<10} {'UniqSfx':<10} {'PfxDiv':<10} {'SfxDiv':<10}")
    print("-" * 48)

    for s in sections:
        prefixes = Counter()
        suffixes = Counter()
        for token in section_data[s]['tokens']:
            if len(token) >= 2:
                prefixes[token[:2]] += 1
                suffixes[token[-2:]] += 1

        total_pfx = sum(prefixes.values())
        total_sfx = sum(suffixes.values())
        uniq_pfx = len(prefixes)
        uniq_sfx = len(suffixes)
        pfx_div = uniq_pfx / total_pfx if total_pfx > 0 else 0
        sfx_div = uniq_sfx / total_sfx if total_sfx > 0 else 0

        metrics[s]['uniq_pfx'] = uniq_pfx
        metrics[s]['uniq_sfx'] = uniq_sfx

        print(f"{s:<4} {uniq_pfx:<10} {uniq_sfx:<10} {pfx_div:<10.4f} {sfx_div:<10.4f}")

    # Section-exclusive tokens
    print("\n" + "=" * 70)
    print("SECTION-EXCLUSIVE TOKEN ANALYSIS")
    print("=" * 70)

    # Find tokens that appear in only one section
    token_sections = defaultdict(set)
    for s in sections:
        for token in section_data[s]['unique']:
            token_sections[token].add(s)

    exclusive_by_section = defaultdict(set)
    for token, secs in token_sections.items():
        if len(secs) == 1:
            exclusive_by_section[list(secs)[0]].add(token)

    print(f"\n{'Sec':<4} {'Exclusive':<12} {'Excl%':<10} {'Sample Exclusive Tokens'}")
    print("-" * 70)

    for s in sections:
        excl = len(exclusive_by_section[s])
        excl_pct = 100 * excl / len(section_data[s]['unique']) if section_data[s]['unique'] else 0
        samples = list(exclusive_by_section[s])[:5]

        metrics[s]['exclusive_pct'] = excl_pct

        print(f"{s:<4} {excl:<12} {excl_pct:<10.1f} {samples}")

    # Synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS: WHAT MAKES Z, A MORE COMPLEX?")
    print("=" * 70)

    # Sort sections by diversity
    sorted_sections = sorted(sections, key=lambda s: metrics[s]['diversity'], reverse=True)

    print("\nSections ranked by exec diversity:")
    for rank, s in enumerate(sorted_sections, 1):
        print(f"  {rank}. {s}: diversity={metrics[s]['diversity']:.3f}")

    print("\n" + "-" * 70)
    print("KEY DIFFERENTIATORS:")
    print("-" * 70)

    # Compare high-diversity (Z, A, T) vs low-diversity (B, H)
    high_div = ['Z', 'A', 'T']
    low_div = ['B', 'H']

    def avg_metric(sections_list, metric_name):
        return np.mean([metrics[s][metric_name] for s in sections_list if s in metrics])

    comparisons = [
        ('Tokens per folio', 'tok_per_folio'),
        ('Top-10 concentration', 'top10_pct'),
        ('Top-1 concentration', 'top1_pct'),
        ('Hazard %', 'hazard_pct'),
        ('LINK %', 'link_pct'),
        ('Mean token length', 'mean_len'),
        ('Exclusive token %', 'exclusive_pct'),
    ]

    print(f"\n{'Metric':<25} {'High-Div (Z,A,T)':<18} {'Low-Div (B,H)':<18} {'Difference'}")
    print("-" * 70)

    for name, metric in comparisons:
        high_avg = avg_metric(high_div, metric)
        low_avg = avg_metric(low_div, metric)
        diff = high_avg - low_avg
        print(f"{name:<25} {high_avg:<18.2f} {low_avg:<18.2f} {diff:+.2f}")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Check which factors correlate most with diversity
    diversities = [metrics[s]['diversity'] for s in sections]

    from scipy import stats as sp_stats

    print("\nCorrelation with exec diversity:")
    for name, metric in comparisons:
        values = [metrics[s][metric] for s in sections]
        r, p = sp_stats.pearsonr(diversities, values)
        sig = "**" if p < 0.05 else ""
        print(f"  {name:<25}: r={r:+.3f} (p={p:.3f}) {sig}")


if __name__ == '__main__':
    main()

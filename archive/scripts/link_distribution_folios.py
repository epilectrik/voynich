"""
Phase LDF: LINK Distribution within Folios

Investigates whether LINK tokens are clustered or evenly distributed within folios,
and whether they mark specific positions.

Prior knowledge:
- LINK density = 38% overall
- LINK is section-conditioned (B=19.6% vs H=9.1%)
- LINK suppressed at line boundaries (0.60x)
- LINK-CEI correlation = -0.7057
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import random

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR_FILE = BASE / "results" / "canonical_grammar.json"

# LINK tokens from Phase 16
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

def load_data():
    """Load transcription and grammar."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)

    with open(GRAMMAR_FILE, 'r') as f:
        grammar = json.load(f)

    return data, grammar

def get_b_folio_tokens(data):
    """Get Currier B tokens grouped by folio, preserving order."""
    folio_tokens = defaultdict(list)
    for row in data:
        if row.get('language') == 'B' and row.get('transcriber') == 'H':
            folio_tokens[row['folio']].append(row)
    return dict(folio_tokens)

def test_ldf1_positional_distribution(folio_tokens):
    """
    LDF-1: Are LINKs uniform across folio positions, or clustered at start/middle/end?
    """
    print("\n" + "="*70)
    print("LDF-1: POSITIONAL DISTRIBUTION")
    print("="*70)
    print("\nQuestion: Are LINKs uniform across folio positions?")

    # Collect normalized positions of LINK tokens
    link_positions = []
    all_positions = []

    for folio, tokens in folio_tokens.items():
        n_tokens = len(tokens)
        if n_tokens < 10:
            continue

        for i, tok in enumerate(tokens):
            pos = i / (n_tokens - 1) if n_tokens > 1 else 0.5
            all_positions.append(pos)
            if tok['word'] in LINK_TOKENS:
                link_positions.append(pos)

    # Bin into 5 quintiles
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    link_hist, _ = np.histogram(link_positions, bins=bins)
    all_hist, _ = np.histogram(all_positions, bins=bins)

    # Expected LINK per bin if uniform
    total_link = len(link_positions)
    total_all = len(all_positions)
    link_rate = total_link / total_all
    expected = all_hist * link_rate

    # Chi-square test
    chi2, p_value = stats.chisquare(link_hist, expected)

    print(f"\nTotal tokens analyzed: {total_all:,}")
    print(f"Total LINK tokens: {total_link:,} ({link_rate:.1%})")

    print(f"\nLINK distribution by folio position:")
    labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    for i, label in enumerate(labels):
        obs_rate = link_hist[i] / all_hist[i] if all_hist[i] > 0 else 0
        ratio = obs_rate / link_rate if link_rate > 0 else 0
        print(f"  {label}: {link_hist[i]:4} LINK / {all_hist[i]:5} total = {obs_rate:.1%} ({ratio:.2f}x baseline)")

    print(f"\nChi-square: {chi2:.2f}, p = {p_value:.6f}")

    # Effect size: max deviation from uniform
    ratios = [(link_hist[i] / all_hist[i]) / link_rate if all_hist[i] > 0 and link_rate > 0 else 1
              for i in range(5)]
    max_dev = max(abs(r - 1) for r in ratios)

    if p_value < 0.001:
        verdict = "SIGNAL"
        interp = f"LINK tokens show NON-UNIFORM positional distribution (max deviation {max_dev:.1%})"
    else:
        verdict = "NULL"
        interp = "LINK tokens are uniformly distributed across folio positions"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'LDF-1',
        'total_tokens': total_all,
        'total_link': total_link,
        'link_rate': link_rate,
        'position_rates': {labels[i]: link_hist[i] / all_hist[i] if all_hist[i] > 0 else 0 for i in range(5)},
        'chi2': chi2,
        'p_value': p_value,
        'max_deviation': max_dev,
        'verdict': verdict
    }

def test_ldf2_run_length(folio_tokens):
    """
    LDF-2: Do LINKs occur in consecutive runs, or are they interspersed?
    """
    print("\n" + "="*70)
    print("LDF-2: RUN LENGTH ANALYSIS")
    print("="*70)
    print("\nQuestion: Do LINK tokens cluster into consecutive runs?")

    # Collect run lengths
    observed_runs = []

    for folio, tokens in folio_tokens.items():
        if len(tokens) < 10:
            continue

        # Convert to binary sequence
        is_link = [1 if t['word'] in LINK_TOKENS else 0 for t in tokens]

        # Find runs
        current_run = 0
        for val in is_link:
            if val == 1:
                current_run += 1
            else:
                if current_run > 0:
                    observed_runs.append(current_run)
                    current_run = 0
        if current_run > 0:
            observed_runs.append(current_run)

    if not observed_runs:
        print("No LINK runs found")
        return {'test': 'LDF-2', 'verdict': 'NULL'}

    obs_mean = np.mean(observed_runs)
    obs_max = max(observed_runs)

    # Null model: random placement with same density per folio
    null_runs = []
    for _ in range(1000):
        for folio, tokens in folio_tokens.items():
            if len(tokens) < 10:
                continue
            n = len(tokens)
            n_link = sum(1 for t in tokens if t['word'] in LINK_TOKENS)
            if n_link == 0:
                continue

            # Random placement
            positions = sorted(random.sample(range(n), min(n_link, n)))

            # Find runs in random placement
            current_run = 0
            prev_pos = -2
            for pos in positions:
                if pos == prev_pos + 1:
                    current_run += 1
                else:
                    if current_run > 0:
                        null_runs.append(current_run)
                    current_run = 1
                prev_pos = pos
            if current_run > 0:
                null_runs.append(current_run)

    null_mean = np.mean(null_runs) if null_runs else 1
    null_std = np.std(null_runs) if null_runs else 0

    # Z-score
    z_score = (obs_mean - null_mean) / null_std if null_std > 0 else 0

    print(f"\nObserved LINK runs: {len(observed_runs):,}")
    print(f"Mean run length: {obs_mean:.3f}")
    print(f"Max run length: {obs_max}")

    # Run length distribution
    run_counter = Counter(observed_runs)
    print(f"\nRun length distribution:")
    for length in sorted(run_counter.keys())[:10]:
        print(f"  Length {length}: {run_counter[length]} runs")

    print(f"\nNull model (random placement):")
    print(f"  Mean run length: {null_mean:.3f}")
    print(f"  Std: {null_std:.3f}")
    print(f"  Z-score: {z_score:.2f}")

    ratio = obs_mean / null_mean if null_mean > 0 else 1

    if z_score > 2:
        verdict = "SIGNAL"
        interp = f"LINK tokens cluster into runs {ratio:.2f}x longer than random"
    elif z_score < -2:
        verdict = "SIGNAL"
        interp = f"LINK tokens are MORE dispersed than random ({ratio:.2f}x)"
    else:
        verdict = "NULL"
        interp = "LINK run lengths match random placement expectation"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'LDF-2',
        'n_runs': len(observed_runs),
        'obs_mean': obs_mean,
        'obs_max': obs_max,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'ratio': ratio,
        'verdict': verdict
    }

def test_ldf3_line_position(folio_tokens):
    """
    LDF-3: Does LINK density vary by position within lines?
    """
    print("\n" + "="*70)
    print("LDF-3: LINE-POSITION LINK DENSITY")
    print("="*70)
    print("\nQuestion: Does LINK density vary by position within lines?")

    # Reconstruct lines
    lines = defaultdict(list)
    for folio, tokens in folio_tokens.items():
        for tok in tokens:
            key = (folio, tok.get('line_number', '1'))
            lines[key].append(tok)

    # Collect by normalized position within line
    position_link = defaultdict(list)  # position bin -> list of (is_link)

    for key, line_tokens in lines.items():
        n = len(line_tokens)
        if n < 3:
            continue

        for i, tok in enumerate(line_tokens):
            # Normalize to 0-1
            pos = i / (n - 1) if n > 1 else 0.5

            # Bin into thirds: initial, middle, final
            if pos < 0.33:
                bin_name = 'initial'
            elif pos < 0.67:
                bin_name = 'middle'
            else:
                bin_name = 'final'

            is_link = 1 if tok['word'] in LINK_TOKENS else 0
            position_link[bin_name].append(is_link)

    # Calculate rates
    rates = {}
    total_link = 0
    total_all = 0

    for pos in ['initial', 'middle', 'final']:
        vals = position_link[pos]
        n_link = sum(vals)
        n_total = len(vals)
        rate = n_link / n_total if n_total > 0 else 0
        rates[pos] = {'n_link': n_link, 'n_total': n_total, 'rate': rate}
        total_link += n_link
        total_all += n_total

    baseline = total_link / total_all if total_all > 0 else 0

    print(f"\nBaseline LINK rate: {baseline:.1%}")
    print(f"\nLINK rate by line position:")
    for pos in ['initial', 'middle', 'final']:
        r = rates[pos]
        ratio = r['rate'] / baseline if baseline > 0 else 1
        print(f"  {pos:8}: {r['n_link']:5} / {r['n_total']:6} = {r['rate']:.1%} ({ratio:.2f}x baseline)")

    # Chi-square test
    observed = [rates[p]['n_link'] for p in ['initial', 'middle', 'final']]
    expected = [rates[p]['n_total'] * baseline for p in ['initial', 'middle', 'final']]

    chi2, p_value = stats.chisquare(observed, expected)

    print(f"\nChi-square: {chi2:.2f}, p = {p_value:.6f}")

    # Effect size
    ratios = [rates[p]['rate'] / baseline if baseline > 0 else 1 for p in ['initial', 'middle', 'final']]
    max_dev = max(abs(r - 1) for r in ratios)

    if p_value < 0.001:
        verdict = "SIGNAL"
        # Find which position is most deviant
        min_ratio = min(ratios)
        max_ratio = max(ratios)
        if max_ratio - 1 > 1 - min_ratio:
            peak_pos = ['initial', 'middle', 'final'][ratios.index(max_ratio)]
            interp = f"LINK density peaks at {peak_pos} position ({max_ratio:.2f}x)"
        else:
            trough_pos = ['initial', 'middle', 'final'][ratios.index(min_ratio)]
            interp = f"LINK density depleted at {trough_pos} position ({min_ratio:.2f}x)"
    else:
        verdict = "NULL"
        interp = "LINK density uniform across line positions"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'LDF-3',
        'baseline': baseline,
        'rates': rates,
        'chi2': chi2,
        'p_value': p_value,
        'verdict': verdict
    }

def test_ldf4_grammar_context(folio_tokens, grammar):
    """
    LDF-4: Do specific grammar classes precede/follow LINK tokens?
    """
    print("\n" + "="*70)
    print("LDF-4: LINK-GRAMMAR CONTEXT")
    print("="*70)
    print("\nQuestion: Do specific grammar classes precede/follow LINK tokens?")

    # Build token -> role mapping from grammar terminals
    token_to_class = {}
    for term in grammar.get('terminals', {}).get('list', []):
        token_to_class[term['symbol']] = term['role']

    # Collect bigrams
    pre_link = []  # classes that precede LINK
    post_link = []  # classes that follow LINK
    all_classes = []

    for folio, tokens in folio_tokens.items():
        for i in range(len(tokens) - 1):
            t1 = tokens[i]['word']
            t2 = tokens[i + 1]['word']

            c1 = token_to_class.get(t1, 'UNKNOWN')
            c2 = token_to_class.get(t2, 'UNKNOWN')

            all_classes.append(c1)

            if t2 in LINK_TOKENS:
                pre_link.append(c1)
            if t1 in LINK_TOKENS:
                post_link.append(c2)

        # Last token
        if tokens:
            all_classes.append(token_to_class.get(tokens[-1]['word'], 'UNKNOWN'))

    # Baseline class distribution
    baseline_counter = Counter(all_classes)
    baseline_total = len(all_classes)

    # Pre-LINK distribution
    pre_counter = Counter(pre_link)
    pre_total = len(pre_link)

    # Post-LINK distribution
    post_counter = Counter(post_link)
    post_total = len(post_link)

    print(f"\nTotal transitions analyzed: {baseline_total:,}")
    print(f"Pre-LINK contexts: {pre_total:,}")
    print(f"Post-LINK contexts: {post_total:,}")

    # Find enriched/depleted classes
    print(f"\nTop 10 ENRICHED classes BEFORE LINK:")
    enrichments_pre = []
    for cls in baseline_counter:
        baseline_rate = baseline_counter[cls] / baseline_total
        pre_rate = pre_counter[cls] / pre_total if pre_total > 0 else 0
        ratio = pre_rate / baseline_rate if baseline_rate > 0 else 0
        if pre_counter[cls] >= 10:  # minimum count
            enrichments_pre.append((cls, ratio, pre_counter[cls], baseline_rate, pre_rate))

    enrichments_pre.sort(key=lambda x: x[1], reverse=True)
    for cls, ratio, count, base_r, pre_r in enrichments_pre[:10]:
        print(f"  {cls:20}: {ratio:.2f}x ({count} instances)")

    print(f"\nTop 10 ENRICHED classes AFTER LINK:")
    enrichments_post = []
    for cls in baseline_counter:
        baseline_rate = baseline_counter[cls] / baseline_total
        post_rate = post_counter[cls] / post_total if post_total > 0 else 0
        ratio = post_rate / baseline_rate if baseline_rate > 0 else 0
        if post_counter[cls] >= 10:
            enrichments_post.append((cls, ratio, post_counter[cls], baseline_rate, post_rate))

    enrichments_post.sort(key=lambda x: x[1], reverse=True)
    for cls, ratio, count, base_r, post_r in enrichments_post[:10]:
        print(f"  {cls:20}: {ratio:.2f}x ({count} instances)")

    # Find depleted classes
    print(f"\nTop 10 DEPLETED classes BEFORE LINK:")
    enrichments_pre.sort(key=lambda x: x[1])
    for cls, ratio, count, base_r, pre_r in enrichments_pre[:10]:
        if ratio < 1:
            print(f"  {cls:20}: {ratio:.2f}x ({count} instances)")

    print(f"\nTop 10 DEPLETED classes AFTER LINK:")
    enrichments_post.sort(key=lambda x: x[1])
    for cls, ratio, count, base_r, post_r in enrichments_post[:10]:
        if ratio < 1:
            print(f"  {cls:20}: {ratio:.2f}x ({count} instances)")

    # Statistical test: chi-square for overall distribution difference
    # Compare pre-LINK distribution to baseline
    common_classes = [c for c in baseline_counter if baseline_counter[c] >= 50]

    pre_obs = [pre_counter[c] for c in common_classes]
    pre_exp = [baseline_counter[c] / baseline_total * pre_total for c in common_classes]

    if pre_obs and all(e > 0 for e in pre_exp):
        chi2_pre, p_pre = stats.chisquare(pre_obs, pre_exp)
    else:
        chi2_pre, p_pre = 0, 1

    post_obs = [post_counter[c] for c in common_classes]
    post_exp = [baseline_counter[c] / baseline_total * post_total for c in common_classes]

    if post_obs and all(e > 0 for e in post_exp):
        chi2_post, p_post = stats.chisquare(post_obs, post_exp)
    else:
        chi2_post, p_post = 0, 1

    print(f"\nChi-square (pre-LINK vs baseline): {chi2_pre:.2f}, p = {p_pre:.2e}")
    print(f"Chi-square (post-LINK vs baseline): {chi2_post:.2f}, p = {p_post:.2e}")

    # Max enrichment/depletion
    max_enrich_pre = max(e[1] for e in enrichments_pre) if enrichments_pre else 1
    max_enrich_post = max(e[1] for e in enrichments_post) if enrichments_post else 1

    if p_pre < 0.001 or p_post < 0.001:
        verdict = "SIGNAL"
        interp = f"LINK contexts are grammar-selective (max enrichment: {max(max_enrich_pre, max_enrich_post):.2f}x)"
    else:
        verdict = "NULL"
        interp = "LINK contexts match baseline grammar distribution"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interp}")

    return {
        'test': 'LDF-4',
        'pre_total': pre_total,
        'post_total': post_total,
        'chi2_pre': chi2_pre,
        'p_pre': p_pre,
        'chi2_post': chi2_post,
        'p_post': p_post,
        'max_enrich_pre': max_enrich_pre,
        'max_enrich_post': max_enrich_post,
        'verdict': verdict
    }

def main():
    print("="*70)
    print("PHASE LDF: LINK DISTRIBUTION WITHIN FOLIOS")
    print("="*70)
    print("\nCore Question: Are LINK tokens clustered or evenly distributed?")
    print("Do they mark specific positions within folios or lines?")

    data, grammar = load_data()
    folio_tokens = get_b_folio_tokens(data)

    print(f"\nLoaded {len(folio_tokens)} Currier B folios")

    # Run tests
    results = {}

    results['ldf1'] = test_ldf1_positional_distribution(folio_tokens)
    results['ldf2'] = test_ldf2_run_length(folio_tokens)
    results['ldf3'] = test_ldf3_line_position(folio_tokens)
    results['ldf4'] = test_ldf4_grammar_context(folio_tokens, grammar)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    signal_count = sum(1 for r in results.values() if r.get('verdict') == 'SIGNAL')
    null_count = sum(1 for r in results.values() if r.get('verdict') == 'NULL')

    print(f"\nResults: {signal_count} SIGNAL, {null_count} NULL")

    print("\n| Test | Finding | Verdict |")
    print("|------|---------|---------|")

    for key, r in results.items():
        test_name = r.get('test', key)
        verdict = r.get('verdict', 'UNKNOWN')

        if key == 'ldf1':
            if verdict == 'SIGNAL':
                finding = f"Non-uniform distribution (max dev {r.get('max_deviation', 0):.1%})"
            else:
                finding = "Uniform across folio positions"
        elif key == 'ldf2':
            if verdict == 'SIGNAL':
                finding = f"Run length {r.get('ratio', 1):.2f}x random (z={r.get('z_score', 0):.2f})"
            else:
                finding = f"Run lengths match random (z={r.get('z_score', 0):.2f})"
        elif key == 'ldf3':
            if verdict == 'SIGNAL':
                rates = r.get('rates', {})
                baseline = r.get('baseline', 0)
                ratios = {p: rates[p]['rate']/baseline if baseline > 0 else 1 for p in rates}
                min_pos = min(ratios, key=ratios.get)
                finding = f"Depleted at {min_pos} ({ratios[min_pos]:.2f}x)"
            else:
                finding = "Uniform within lines"
        elif key == 'ldf4':
            if verdict == 'SIGNAL':
                finding = f"Grammar-selective (max {max(r.get('max_enrich_pre', 1), r.get('max_enrich_post', 1)):.1f}x)"
            else:
                finding = "Context-independent"
        else:
            finding = "See details"

        print(f"| {test_name} | {finding} | **{verdict}** |")

    # Interpretation
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    if signal_count >= 2:
        print("""
LINK tokens show STRUCTURED distribution patterns:
- They are not randomly scattered throughout folios
- Their placement follows grammar and/or positional rules
- This supports LINK as a FORMAL control element, not just padding
""")
    else:
        print("""
LINK tokens appear to be UNIFORMLY distributed:
- No strong positional preferences
- No significant clustering
- LINK may function as neutral "waiting" markers without positional semantics
""")

    # Save results
    output_file = BASE / "archive" / "reports" / "link_distribution_folios.json"
    with open(output_file, 'w') as f:
        # Convert numpy types for JSON
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj

        json.dump(convert(results), f, indent=2)

    print(f"\nResults saved to {output_file}")

if __name__ == '__main__':
    main()

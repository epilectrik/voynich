"""
Phase LINE: Line-Level Control Architecture Analysis

Core Question: Are lines formal control blocks (micro-stages), or merely scribal segmentation?

Four Tests:
- LINE-1: Line-Initial/Line-Final Constraint Test
- LINE-2: Line-Internal Length Regularity
- LINE-3: LINK Placement Relative to Line Breaks
- LINE-4: Cross-Line Illegal Transition Suppression
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import random

# Paths
BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

# LINK tokens (waiting/hold markers)
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}

# Forbidden transitions (from Phase 18)
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('qokeey', 'al'), ('qokeey', 'aiin'),
    ('qokeey', 'ar'), ('qokeey', 'or'), ('okeey', 'al'),
    ('okeey', 'ar'), ('okeey', 'or')
]

def load_transcription():
    """Load and parse the transcription file."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)
    return data

def get_currier_b_data(data):
    """Filter to Currier B and deduplicate by primary hand (H)."""
    b_data = []
    for row in data:
        if row.get('language') == 'B' and row.get('transcriber') == 'H':
            b_data.append(row)
    return b_data

def reconstruct_lines(b_data):
    """Reconstruct line structure from token data."""
    # Group by (folio, line_number)
    lines = defaultdict(list)
    for row in b_data:
        key = (row['folio'], row.get('line_number', '1'))
        lines[key].append(row)

    # Sort tokens within each line by position
    # Use line_initial/line_final to help ordering
    for key in lines:
        tokens = lines[key]
        # Simple heuristic: line_initial=1 goes first, line_final=1 goes last
        # For middle tokens, preserve original order
        initial = [t for t in tokens if str(t.get('line_initial', '')).strip() == '1']
        final = [t for t in tokens if str(t.get('line_final', '')).strip() == '1']
        middle = [t for t in tokens if t not in initial and t not in final]
        lines[key] = initial + middle + final

    return dict(lines)

def test_line1_boundary_constraints(lines, b_data):
    """
    LINE-1: Line-Initial/Line-Final Constraint Test

    Are certain tokens enriched or suppressed at line boundaries?
    """
    print("\n" + "="*60)
    print("TEST LINE-1: Line-Initial/Line-Final Constraint Test")
    print("="*60)

    # Collect tokens by position
    line_initial_tokens = []
    line_final_tokens = []
    mid_line_tokens = []

    for key, tokens in lines.items():
        if len(tokens) < 3:
            continue
        for i, t in enumerate(tokens):
            word = t['word']
            if i == 0:
                line_initial_tokens.append(word)
            elif i == len(tokens) - 1:
                line_final_tokens.append(word)
            else:
                mid_line_tokens.append(word)

    print(f"\nToken counts:")
    print(f"  Line-initial: {len(line_initial_tokens)}")
    print(f"  Line-final: {len(line_final_tokens)}")
    print(f"  Mid-line: {len(mid_line_tokens)}")

    # Count LINK tokens by position
    link_initial = sum(1 for t in line_initial_tokens if t in LINK_TOKENS)
    link_final = sum(1 for t in line_final_tokens if t in LINK_TOKENS)
    link_mid = sum(1 for t in mid_line_tokens if t in LINK_TOKENS)

    link_initial_rate = link_initial / len(line_initial_tokens) if line_initial_tokens else 0
    link_final_rate = link_final / len(line_final_tokens) if line_final_tokens else 0
    link_mid_rate = link_mid / len(mid_line_tokens) if mid_line_tokens else 0

    print(f"\nLINK token rates:")
    print(f"  Line-initial: {link_initial_rate:.1%} ({link_initial}/{len(line_initial_tokens)})")
    print(f"  Line-final: {link_final_rate:.1%} ({link_final}/{len(line_final_tokens)})")
    print(f"  Mid-line: {link_mid_rate:.1%} ({link_mid}/{len(mid_line_tokens)})")

    # Enrichment ratios
    if link_mid_rate > 0:
        initial_enrichment = link_initial_rate / link_mid_rate
        final_enrichment = link_final_rate / link_mid_rate
    else:
        initial_enrichment = 0
        final_enrichment = 0

    print(f"\nEnrichment vs mid-line:")
    print(f"  Line-initial: {initial_enrichment:.2f}x")
    print(f"  Line-final: {final_enrichment:.2f}x")

    # Chi-square test for position independence
    observed = np.array([[link_initial, len(line_initial_tokens) - link_initial],
                         [link_final, len(line_final_tokens) - link_final],
                         [link_mid, len(mid_line_tokens) - link_mid]])
    chi2, p_value, dof, expected = stats.chi2_contingency(observed)

    print(f"\nChi-square test (LINK x position):")
    print(f"  Chi2 = {chi2:.2f}, p = {p_value:.4e}")

    # Top tokens at each position
    initial_counter = Counter(line_initial_tokens)
    final_counter = Counter(line_final_tokens)
    mid_counter = Counter(mid_line_tokens)

    print(f"\nTop 5 line-initial tokens:")
    for token, count in initial_counter.most_common(5):
        rate = count / len(line_initial_tokens)
        mid_rate = mid_counter.get(token, 0) / len(mid_line_tokens) if mid_line_tokens else 0
        enrichment = rate / mid_rate if mid_rate > 0 else float('inf')
        print(f"  {token}: {rate:.1%} (enrichment: {enrichment:.2f}x)")

    print(f"\nTop 5 line-final tokens:")
    for token, count in final_counter.most_common(5):
        rate = count / len(line_final_tokens)
        mid_rate = mid_counter.get(token, 0) / len(mid_line_tokens) if mid_line_tokens else 0
        enrichment = rate / mid_rate if mid_rate > 0 else float('inf')
        print(f"  {token}: {rate:.1%} (enrichment: {enrichment:.2f}x)")

    # Verdict
    if p_value < 0.001 and (initial_enrichment > 1.5 or final_enrichment > 1.5):
        verdict = "SIGNAL - Line boundaries show LINK enrichment"
    elif p_value < 0.05:
        verdict = "WEAK SIGNAL - Some position effect detected"
    else:
        verdict = "NULL - LINK distribution position-independent"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'LINE-1',
        'line_initial_count': len(line_initial_tokens),
        'line_final_count': len(line_final_tokens),
        'mid_line_count': len(mid_line_tokens),
        'link_initial_rate': link_initial_rate,
        'link_final_rate': link_final_rate,
        'link_mid_rate': link_mid_rate,
        'initial_enrichment': initial_enrichment,
        'final_enrichment': final_enrichment,
        'chi2': chi2,
        'p_value': p_value,
        'verdict': verdict
    }

def test_line2_length_regularity(lines):
    """
    LINE-2: Line-Internal Length Regularity

    Do B lines have controlled length distributions?
    """
    print("\n" + "="*60)
    print("TEST LINE-2: Line-Internal Length Regularity")
    print("="*60)

    # Group lines by folio
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in lines.items():
        folio_lines[folio].append(len(tokens))

    # Calculate CV (coefficient of variation) for each folio
    folio_cvs = {}
    for folio, lengths in folio_lines.items():
        if len(lengths) >= 3:
            mean_len = np.mean(lengths)
            std_len = np.std(lengths)
            cv = std_len / mean_len if mean_len > 0 else 0
            folio_cvs[folio] = cv

    observed_cv = np.mean(list(folio_cvs.values()))
    observed_std = np.std(list(folio_cvs.values()))

    print(f"\nFolios analyzed: {len(folio_cvs)}")
    print(f"Mean CV across folios: {observed_cv:.3f}")
    print(f"Std of CV: {observed_std:.3f}")

    # Generate null distribution by shuffling line breaks
    null_cvs = []
    for _ in range(1000):
        # For each folio, shuffle all tokens and re-split into random lines
        for folio, lengths in folio_lines.items():
            if len(lengths) >= 3:
                total_tokens = sum(lengths)
                n_lines = len(lengths)
                # Random line breaks
                breaks = sorted(random.sample(range(1, total_tokens), n_lines - 1))
                random_lengths = [breaks[0]]
                for i in range(1, len(breaks)):
                    random_lengths.append(breaks[i] - breaks[i-1])
                random_lengths.append(total_tokens - breaks[-1])

                mean_len = np.mean(random_lengths)
                std_len = np.std(random_lengths)
                if mean_len > 0:
                    null_cvs.append(std_len / mean_len)

    null_mean = np.mean(null_cvs)
    null_std = np.std(null_cvs)

    print(f"\nNull distribution (random line breaks):")
    print(f"  Mean CV: {null_mean:.3f}")
    print(f"  Std CV: {null_std:.3f}")

    # Z-score
    z_score = (observed_cv - null_mean) / null_std if null_std > 0 else 0
    print(f"\nZ-score: {z_score:.2f}")

    # Distribution of line lengths
    all_lengths = []
    for lengths in folio_lines.values():
        all_lengths.extend(lengths)

    print(f"\nLine length distribution:")
    print(f"  Min: {min(all_lengths)}")
    print(f"  Max: {max(all_lengths)}")
    print(f"  Mean: {np.mean(all_lengths):.1f}")
    print(f"  Median: {np.median(all_lengths):.1f}")
    print(f"  Std: {np.std(all_lengths):.1f}")

    # Verdict
    if z_score < -2:
        verdict = "SIGNAL - Lines MORE regular than random (deliberate chunking)"
    elif z_score > 2:
        verdict = "SIGNAL - Lines LESS regular than random (unexpected)"
    else:
        verdict = "NULL - Line lengths match scribal variability"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'LINE-2',
        'folios_analyzed': len(folio_cvs),
        'observed_cv': observed_cv,
        'null_cv': null_mean,
        'z_score': z_score,
        'mean_line_length': np.mean(all_lengths),
        'std_line_length': np.std(all_lengths),
        'verdict': verdict
    }

def test_line3_link_placement(lines):
    """
    LINE-3: LINK Placement Relative to Line Breaks

    Are LINK tokens preferentially placed near line boundaries?
    """
    print("\n" + "="*60)
    print("TEST LINE-3: LINK Placement Relative to Line Breaks")
    print("="*60)

    # Collect normalized positions of LINK tokens
    link_positions = []
    all_positions = []

    for (folio, line_num), tokens in lines.items():
        n = len(tokens)
        if n < 3:
            continue
        for i, t in enumerate(tokens):
            # Normalized position: 0 = start, 1 = end
            pos = i / (n - 1) if n > 1 else 0.5
            all_positions.append(pos)
            if t['word'] in LINK_TOKENS:
                link_positions.append(pos)

    print(f"\nTotal tokens: {len(all_positions)}")
    print(f"LINK tokens: {len(link_positions)} ({len(link_positions)/len(all_positions):.1%})")

    if not link_positions:
        print("No LINK tokens found!")
        return {'test': 'LINE-3', 'verdict': 'NO DATA'}

    # Bin positions into thirds
    def bin_position(p):
        if p < 0.33:
            return 'START'
        elif p < 0.67:
            return 'MIDDLE'
        else:
            return 'END'

    link_binned = Counter(bin_position(p) for p in link_positions)
    all_binned = Counter(bin_position(p) for p in all_positions)

    # Expected vs observed
    total_link = len(link_positions)
    total_all = len(all_positions)

    print(f"\nLINK position distribution:")
    for pos in ['START', 'MIDDLE', 'END']:
        obs = link_binned.get(pos, 0)
        exp_rate = all_binned.get(pos, 0) / total_all
        exp = exp_rate * total_link
        enrichment = (obs / total_link) / exp_rate if exp_rate > 0 else 0
        print(f"  {pos}: {obs} ({obs/total_link:.1%}), expected: {exp:.0f}, enrichment: {enrichment:.2f}x")

    # KS test comparing LINK positions to uniform
    ks_stat, ks_p = stats.kstest(link_positions, 'uniform', args=(0, 1))
    print(f"\nKS test (LINK vs uniform):")
    print(f"  KS statistic: {ks_stat:.3f}")
    print(f"  p-value: {ks_p:.4e}")

    # Compare LINK distribution to all tokens distribution
    ks_stat2, ks_p2 = stats.ks_2samp(link_positions, all_positions)
    print(f"\nKS test (LINK vs all tokens):")
    print(f"  KS statistic: {ks_stat2:.3f}")
    print(f"  p-value: {ks_p2:.4e}")

    # Mean position
    link_mean = np.mean(link_positions)
    all_mean = np.mean(all_positions)
    print(f"\nMean position:")
    print(f"  LINK: {link_mean:.3f}")
    print(f"  All tokens: {all_mean:.3f}")

    # Verdict
    end_enrichment = link_binned.get('END', 0) / (total_link * (all_binned.get('END', 0) / total_all)) if all_binned.get('END', 0) > 0 else 0
    start_enrichment = link_binned.get('START', 0) / (total_link * (all_binned.get('START', 0) / total_all)) if all_binned.get('START', 0) > 0 else 0

    if ks_p2 < 0.001 and (end_enrichment > 1.3 or start_enrichment > 1.3):
        verdict = "SIGNAL - LINK clustering at line boundaries"
    elif ks_p2 < 0.05:
        verdict = "WEAK SIGNAL - Some position bias detected"
    else:
        verdict = "NULL - LINK distribution matches overall token distribution"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'LINE-3',
        'link_count': len(link_positions),
        'link_mean_position': link_mean,
        'all_mean_position': all_mean,
        'ks_stat': ks_stat2,
        'ks_p': ks_p2,
        'end_enrichment': end_enrichment,
        'start_enrichment': start_enrichment,
        'verdict': verdict
    }

def test_line4_cross_line_transitions(lines):
    """
    LINE-4: Cross-Line Illegal Transition Suppression

    Are illegal transitions less likely across line breaks than within lines?
    """
    print("\n" + "="*60)
    print("TEST LINE-4: Cross-Line Illegal Transition Suppression")
    print("="*60)

    # Convert forbidden transitions to set for fast lookup
    forbidden_set = set(FORBIDDEN_TRANSITIONS)

    # Collect bigrams
    within_line_bigrams = []
    cross_line_bigrams = []

    # Group lines by folio and sort by line number
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in lines.items():
        folio_lines[folio].append((line_num, tokens))

    for folio, line_list in folio_lines.items():
        # Sort by line number
        line_list.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

        for i, (line_num, tokens) in enumerate(line_list):
            words = [t['word'] for t in tokens]

            # Within-line bigrams
            for j in range(len(words) - 1):
                within_line_bigrams.append((words[j], words[j+1]))

            # Cross-line bigram (last token of this line, first token of next line)
            if i < len(line_list) - 1:
                next_tokens = line_list[i+1][1]
                if tokens and next_tokens:
                    last_token = tokens[-1]['word']
                    first_token = next_tokens[0]['word']
                    cross_line_bigrams.append((last_token, first_token))

    print(f"\nBigram counts:")
    print(f"  Within-line: {len(within_line_bigrams)}")
    print(f"  Cross-line: {len(cross_line_bigrams)}")

    # Count forbidden transitions
    within_forbidden = sum(1 for bg in within_line_bigrams if bg in forbidden_set)
    cross_forbidden = sum(1 for bg in cross_line_bigrams if bg in forbidden_set)

    within_rate = within_forbidden / len(within_line_bigrams) if within_line_bigrams else 0
    cross_rate = cross_forbidden / len(cross_line_bigrams) if cross_line_bigrams else 0

    print(f"\nForbidden transitions:")
    print(f"  Within-line: {within_forbidden} ({within_rate:.4%})")
    print(f"  Cross-line: {cross_forbidden} ({cross_rate:.4%})")

    # Fisher's exact test
    # Contingency table: [forbidden, allowed] x [within, cross]
    contingency = np.array([
        [within_forbidden, len(within_line_bigrams) - within_forbidden],
        [cross_forbidden, len(cross_line_bigrams) - cross_forbidden]
    ])

    try:
        odds_ratio, fisher_p = stats.fisher_exact(contingency)
        print(f"\nFisher's exact test:")
        print(f"  Odds ratio: {odds_ratio:.3f}")
        print(f"  p-value: {fisher_p:.4e}")
    except:
        fisher_p = 1.0
        odds_ratio = 1.0
        print(f"\nFisher's exact test: Could not compute (insufficient forbidden transitions)")

    # Also check near-misses (one character different from forbidden)
    def is_near_miss(bg):
        for fb in FORBIDDEN_TRANSITIONS:
            # Check if only one character different
            if (bg[0] == fb[0] and len(bg[1]) == len(fb[1]) and
                sum(a != b for a, b in zip(bg[1], fb[1])) == 1):
                return True
            if (bg[1] == fb[1] and len(bg[0]) == len(fb[0]) and
                sum(a != b for a, b in zip(bg[0], fb[0])) == 1):
                return True
        return False

    within_near_miss = sum(1 for bg in within_line_bigrams if is_near_miss(bg))
    cross_near_miss = sum(1 for bg in cross_line_bigrams if is_near_miss(bg))

    print(f"\nNear-miss transitions:")
    print(f"  Within-line: {within_near_miss} ({within_near_miss/len(within_line_bigrams):.4%})")
    print(f"  Cross-line: {cross_near_miss} ({cross_near_miss/len(cross_line_bigrams):.4%})")

    # Verdict
    if fisher_p < 0.05 and cross_rate < within_rate * 0.5:
        verdict = "SIGNAL - Cross-line transitions safer (lines = safe breakpoints)"
    elif within_forbidden == 0 and cross_forbidden == 0:
        verdict = "NULL - No forbidden transitions found (grammar well-enforced)"
    else:
        verdict = "NULL - No significant difference between within/cross line"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'LINE-4',
        'within_line_bigrams': len(within_line_bigrams),
        'cross_line_bigrams': len(cross_line_bigrams),
        'within_forbidden': within_forbidden,
        'cross_forbidden': cross_forbidden,
        'within_rate': within_rate,
        'cross_rate': cross_rate,
        'fisher_p': fisher_p,
        'odds_ratio': odds_ratio,
        'verdict': verdict
    }

def main():
    """Run all line-level tests."""
    print("="*60)
    print("PHASE LINE: Line-Level Control Architecture Analysis")
    print("="*60)
    print("\nCore Question: Are lines formal control blocks or scribal segmentation?")

    # Load data
    print("\nLoading data...")
    data = load_transcription()
    b_data = get_currier_b_data(data)
    print(f"Currier B tokens (hand H): {len(b_data)}")

    # Reconstruct lines
    lines = reconstruct_lines(b_data)
    print(f"Lines reconstructed: {len(lines)}")

    # Run tests
    results = []

    r1 = test_line1_boundary_constraints(lines, b_data)
    results.append(r1)

    r2 = test_line2_length_regularity(lines)
    results.append(r2)

    r3 = test_line3_link_placement(lines)
    results.append(r3)

    r4 = test_line4_cross_line_transitions(lines)
    results.append(r4)

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)

    signals = sum(1 for r in results if 'SIGNAL' in r['verdict'] and 'NULL' not in r['verdict'])
    nulls = sum(1 for r in results if 'NULL' in r['verdict'])

    print(f"\nTests run: {len(results)}")
    print(f"  SIGNAL: {signals}")
    print(f"  NULL: {nulls}")

    for r in results:
        print(f"\n  {r['test']}: {r['verdict']}")

    # Overall conclusion
    if signals >= 2:
        conclusion = "LINES ARE FORMAL CONTROL BLOCKS - Add constraints"
    elif signals == 1:
        conclusion = "WEAK EVIDENCE for line structure - Investigate further"
    else:
        conclusion = "LINES ARE SCRIBAL SEGMENTATION - Model complete at token/folio level"

    print(f"\n{'='*60}")
    print(f"CONCLUSION: {conclusion}")
    print("="*60)

    # Save results
    output = {
        'phase': 'LINE',
        'tests': results,
        'signals': signals,
        'nulls': nulls,
        'conclusion': conclusion
    }

    output_path = BASE / "archive" / "reports" / "line_level_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()

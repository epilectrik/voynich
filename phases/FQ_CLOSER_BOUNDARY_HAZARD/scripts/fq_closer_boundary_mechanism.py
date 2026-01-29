#!/usr/bin/env python3
"""
FQ_CLOSER_BOUNDARY_HAZARD - Script 3: Boundary Mechanism Integration

Tests whether Class 23's boundary function (29.8% final, 84% singletons,
2.85x restart loop) mechanistically explains the 3 forbidden pairs.
Computes expected pair counts under independence to distinguish genuine
prohibitions from frequency artifacts.

Sections:
  1. Boundary transition asymmetry (final-source x initial-target)
  2. Restart loop conflict test (23->9 dominance vs EN_CHSH avoidance)
  3. Expected pair count under independence (Poisson model)
  4. Integrated verdict

Constraint references:
  C595: 23->9 enrichment 2.85x
  C597: Class 23 boundary dominance (29.8% final)
  C627: 3 unexplained forbidden pairs
"""

import json
import sys
import math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

# ============================================================
# CONSTANTS
# ============================================================
CLASS_23_TOKENS = {'dy', 'y', 'am', 's', 'r', 'l', 'd'}
FORBIDDEN_SOURCES = {'dy', 'l'}
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}
EN_CHSH_CLASSES = {8, 31}

FORBIDDEN_PAIRS = [
    ('dy', 'aiin', 23, 9, 'CROSS_GROUP'),
    ('dy', 'chey', 23, 31, 'FORWARD'),
    ('l', 'chol', 23, 8, 'FORWARD'),
]

# Known allowed pairs in same class-pair contexts (from C627 data)
ALLOWED_PAIRS = {
    (23, 9): [('s', 'aiin', 18), ('r', 'aiin', 7), ('y', 'or', 2), ('l', 'or', 1)],
    (23, 31): [('y', 'shey', 2), ('l', 'chey', 1), ('am', 'shey', 1),
               ('am', 'chdy', 1), ('y', 'chy', 1), ('y', 'shor', 1),
               ('dy', 'shey', 1), ('l', 'shey', 1)],
    (23, 8): [('l', 'chedy', 2), ('l', 'shedy', 2), ('y', 'chedy', 1),
              ('y', 'shedy', 1), ('r', 'chedy', 1), ('dy', 'chedy', 1)],
}

RESULTS_PATH = PROJECT_ROOT / 'phases' / 'FQ_CLOSER_BOUNDARY_HAZARD' / 'results' / 'fq_closer_boundary_mechanism.json'


# ============================================================
# LOAD DATA
# ============================================================
def load_class_token_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_b_lines():
    tx = Transcript()
    lines = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        lines[key].append(token.word)
    return lines


# ============================================================
# SECTION 1: BOUNDARY TRANSITION ASYMMETRY
# ============================================================
def section1_boundary_asymmetry(lines, token_to_class):
    print("=" * 70)
    print("SECTION 1: BOUNDARY TRANSITION ASYMMETRY")
    print("=" * 70)
    print()

    # Compute initial and final rates for all tokens of interest
    token_positions = defaultdict(list)  # token -> list of (line_pos, line_len)
    for key in sorted(lines.keys()):
        words = lines[key]
        n = len(words)
        for i, w in enumerate(words):
            token_positions[w].append((i, n))

    def compute_rates(tok):
        positions = token_positions.get(tok, [])
        if not positions:
            return 0, 0, 0
        count = len(positions)
        initial = sum(1 for i, n in positions if i == 0)
        final = sum(1 for i, n in positions if i == n - 1)
        return count, initial / count, final / count

    # For each forbidden pair: boundary gap probability = source_final × target_initial
    print("  Forbidden pairs:")
    print(f"  {'Pair':<18} {'SrcFinal%':>9} {'TgtInit%':>9} {'GapProb':>8} {'Direction'}")
    forbidden_results = []

    for src, tgt, src_cls, tgt_cls, direction in FORBIDDEN_PAIRS:
        sc, s_init, s_final = compute_rates(src)
        tc, t_init, t_final = compute_rates(tgt)
        gap_prob = s_final * t_init
        print(f"  {src}->{tgt:<12} {s_final*100:>8.1f}% {t_init*100:>8.1f}% {gap_prob:>8.4f} {direction}")
        forbidden_results.append({
            'source': src, 'target': tgt, 'direction': direction,
            'src_count': sc, 'src_final_rate': round(s_final, 4),
            'tgt_count': tc, 'tgt_initial_rate': round(t_init, 4),
            'boundary_gap_prob': round(gap_prob, 6),
        })

    # For allowed pairs in same contexts
    print("\n  Allowed pairs (controls):")
    print(f"  {'Pair':<18} {'SrcFinal%':>9} {'TgtInit%':>9} {'GapProb':>8} {'Observed':>8}")
    allowed_results = []

    for (src_cls, tgt_cls), pairs in sorted(ALLOWED_PAIRS.items()):
        for a_src, a_tgt, a_count in pairs:
            sc, s_init, s_final = compute_rates(a_src)
            tc, t_init, t_final = compute_rates(a_tgt)
            gap_prob = s_final * t_init
            print(f"  {a_src}->{a_tgt:<12} {s_final*100:>8.1f}% {t_init*100:>8.1f}% {gap_prob:>8.4f} {a_count:>8}")
            allowed_results.append({
                'source': a_src, 'target': a_tgt, 'context': f'c{src_cls}->c{tgt_cls}',
                'src_final_rate': round(s_final, 4),
                'tgt_initial_rate': round(t_init, 4),
                'boundary_gap_prob': round(gap_prob, 6),
                'observed_count': a_count,
            })

    # Compare: are forbidden pairs' gap probs higher than allowed pairs'?
    forb_gaps = [r['boundary_gap_prob'] for r in forbidden_results]
    allw_gaps = [r['boundary_gap_prob'] for r in allowed_results]
    print(f"\n  Mean boundary gap: forbidden={sum(forb_gaps)/len(forb_gaps):.4f}, "
          f"allowed={sum(allw_gaps)/len(allw_gaps):.4f}")
    if sum(forb_gaps)/len(forb_gaps) > sum(allw_gaps)/len(allw_gaps):
        print("  -> Forbidden pairs have HIGHER boundary gap (supports positional explanation)")
    else:
        print("  -> Forbidden pairs do NOT have higher boundary gap (positional explanation weakened)")

    return {'forbidden': forbidden_results, 'allowed': allowed_results}


# ============================================================
# SECTION 2: RESTART LOOP CONFLICT TEST
# ============================================================
def section2_restart_loop(lines, token_to_class):
    print()
    print("=" * 70)
    print("SECTION 2: RESTART LOOP CONFLICT TEST")
    print("=" * 70)
    print()

    # For each Class 23 token: successor class distribution
    successor_classes = defaultdict(lambda: Counter())
    for key in sorted(lines.keys()):
        words = lines[key]
        for i, w in enumerate(words):
            if w in CLASS_23_TOKENS and i < len(words) - 1:
                succ = words[i + 1]
                succ_cls = token_to_class.get(succ)
                if succ_cls is not None:
                    successor_classes[w][succ_cls] += 1

    results = {}
    print(f"  {'Token':<6} {'Total':>5} {'c9':>4} {'c9%':>5} {'c8':>4} {'c31':>4} {'EN%':>5} {'Forb?'}")
    print(f"  {'-'*6} {'-'*5} {'-'*4} {'-'*5} {'-'*4} {'-'*4} {'-'*5} {'-'*5}")

    for tok in sorted(CLASS_23_TOKENS, key=lambda t: -sum(successor_classes[t].values())):
        sc = successor_classes[tok]
        total = sum(sc.values())
        if total == 0:
            continue

        c9 = sc.get(9, 0)
        c8 = sc.get(8, 0)
        c31 = sc.get(31, 0)
        c9_rate = c9 / total
        en_rate = (c8 + c31) / total

        is_forb = tok in FORBIDDEN_SOURCES
        flag = 'YES' if is_forb else 'no'
        print(f"  {tok:<6} {total:>5} {c9:>4} {c9_rate*100:>4.1f}% {c8:>4} {c31:>4} {en_rate*100:>4.1f}% {flag}")

        results[tok] = {
            'total_successors': total,
            'c9_count': c9, 'c9_rate': round(c9_rate, 4),
            'c8_count': c8, 'c31_count': c31,
            'en_chsh_rate': round(en_rate, 4),
            'is_forbidden_source': is_forb,
        }

    # Correlation: does high restart (c9%) predict low EN_CHSH%?
    c9_rates = [(results[t]['c9_rate'], results[t]['en_chsh_rate']) for t in CLASS_23_TOKENS if t in results]
    if len(c9_rates) >= 3:
        c9_vals = [x[0] for x in c9_rates]
        en_vals = [x[1] for x in c9_rates]
        r = spearman_rho(c9_vals, en_vals)
        print(f"\n  Spearman(c9_rate, EN_CHSH_rate) = {r:.3f}")
        if r < -0.3:
            print("  -> Negative correlation: high restart tokens tend to avoid EN_CHSH")
        else:
            print("  -> No strong negative correlation: restart and EN_CHSH are independent")

    return results


def spearman_rho(x, y):
    """Simple Spearman rank correlation."""
    n = len(x)
    rx = rank_data(x)
    ry = rank_data(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1))


def rank_data(vals):
    """Compute ranks with tie handling."""
    indexed = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and vals[indexed[j]] == vals[indexed[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k]] = avg_rank
        i = j
    return ranks


# ============================================================
# SECTION 3: EXPECTED PAIR COUNT UNDER INDEPENDENCE
# ============================================================
def section3_expected_counts(lines, token_to_class):
    print()
    print("=" * 70)
    print("SECTION 3: EXPECTED PAIR COUNT UNDER INDEPENDENCE")
    print("=" * 70)
    print()

    # Count total bigrams and unigram frequencies
    total_bigrams = 0
    token_freq = Counter()
    bigram_counts = Counter()

    for key in sorted(lines.keys()):
        words = lines[key]
        for w in words:
            token_freq[w] += 1
        for i in range(len(words) - 1):
            total_bigrams += 1
            bigram_counts[(words[i], words[i + 1])] += 1

    print(f"  Total bigrams in Currier B: {total_bigrams}")
    print()

    # Forbidden pairs
    print("  FORBIDDEN PAIRS:")
    print(f"  {'Pair':<18} {'f(src)':>6} {'f(tgt)':>6} {'Expected':>8} {'Observed':>8} {'P(0)':>8} {'Verdict'}")
    print(f"  {'-'*18} {'-'*6} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

    forbidden_results = []
    for src, tgt, src_cls, tgt_cls, direction in FORBIDDEN_PAIRS:
        f_src = token_freq[src]
        f_tgt = token_freq[tgt]
        expected = f_src * f_tgt / total_bigrams
        observed = bigram_counts.get((src, tgt), 0)
        p_zero = math.exp(-expected) if expected > 0 else 1.0

        if p_zero < 0.05:
            verdict = 'GENUINE'
        elif p_zero < 0.20:
            verdict = 'LIKELY'
        elif p_zero < 0.50:
            verdict = 'BORDERLINE'
        else:
            verdict = 'ARTIFACT'

        print(f"  {src}->{tgt:<12} {f_src:>6} {f_tgt:>6} {expected:>8.3f} {observed:>8} {p_zero:>8.4f} {verdict}")
        forbidden_results.append({
            'source': src, 'target': tgt, 'direction': direction,
            'src_freq': f_src, 'tgt_freq': f_tgt,
            'expected': round(expected, 4),
            'observed': observed,
            'p_zero': round(p_zero, 6),
            'verdict': verdict,
        })

    # Allowed pairs for comparison
    print("\n  ALLOWED PAIRS (controls):")
    print(f"  {'Pair':<18} {'f(src)':>6} {'f(tgt)':>6} {'Expected':>8} {'Observed':>8} {'P(0)':>8} {'O/E':>6}")

    allowed_results = []
    for (src_cls, tgt_cls), pairs in sorted(ALLOWED_PAIRS.items()):
        for a_src, a_tgt, a_count in pairs:
            f_src = token_freq[a_src]
            f_tgt = token_freq[a_tgt]
            expected = f_src * f_tgt / total_bigrams
            observed = bigram_counts.get((a_src, a_tgt), 0)
            oe_ratio = observed / expected if expected > 0 else float('inf')

            print(f"  {a_src}->{a_tgt:<12} {f_src:>6} {f_tgt:>6} {expected:>8.3f} {observed:>8} "
                  f"{math.exp(-expected) if expected > 0 else 1.0:>8.4f} {oe_ratio:>5.2f}")
            allowed_results.append({
                'source': a_src, 'target': a_tgt,
                'context': f'c{src_cls}->c{tgt_cls}',
                'src_freq': f_src, 'tgt_freq': f_tgt,
                'expected': round(expected, 4),
                'observed': observed,
                'oe_ratio': round(oe_ratio, 3),
            })

    return {'total_bigrams': total_bigrams, 'forbidden': forbidden_results, 'allowed': allowed_results}


# ============================================================
# SECTION 4: INTEGRATED VERDICT
# ============================================================
def section4_integrated_verdict(boundary_results, restart_results, expected_results,
                                 overlap_path):
    print()
    print("=" * 70)
    print("SECTION 4: INTEGRATED VERDICT")
    print("=" * 70)
    print()

    # Load positional overlap data from Script 1 results
    overlap_data = None
    if overlap_path.exists():
        with open(overlap_path, 'r', encoding='utf-8') as f:
            overlap_data = json.load(f)

    verdicts = []

    for i, (src, tgt, src_cls, tgt_cls, direction) in enumerate(FORBIDDEN_PAIRS):
        key = f"{src}->{tgt}"
        print(f"--- {key} (c{src_cls}->c{tgt_cls}, {direction}) ---")

        # Gather evidence
        boundary = boundary_results['forbidden'][i]
        expected = expected_results['forbidden'][i]

        # From Script 1 overlap data
        positional_verdict = 'UNKNOWN'
        adj_to_class = 0
        if overlap_data and 'section4_verdict' in overlap_data:
            ov = overlap_data['section4_verdict'].get(key, {})
            positional_verdict = ov.get('verdict', 'UNKNOWN')
            adj_to_class = ov.get('n_adj_to_class', 0)

        # Restart loop data
        src_restart = restart_results.get(src, {})
        c9_rate = src_restart.get('c9_rate', 0)

        print(f"  Positional verdict (Script 1): {positional_verdict}")
        print(f"  Boundary gap probability: {boundary['boundary_gap_prob']:.4f}")
        print(f"  Expected count (independence): {expected['expected']:.3f}")
        print(f"  P(0 | independence): {expected['p_zero']:.4f}")
        print(f"  Source restart rate (c9): {c9_rate:.3f}")
        print(f"  Source adjacent to target class: {adj_to_class}")

        # Determine overall verdict
        if positional_verdict == 'SEGREGATED':
            verdict = 'POSITIONAL_SEGREGATION'
            explanation = 'Source and target never appear in adjacent-eligible positions'
        elif expected['p_zero'] > 0.50:
            verdict = 'FREQUENCY_ARTIFACT'
            explanation = f"Expected count {expected['expected']:.3f} too low; P(0)={expected['p_zero']:.3f}"
        elif positional_verdict == 'GENUINE_PROHIBITION' and expected['p_zero'] < 0.20:
            verdict = 'TOKEN_SPECIFIC_PROHIBITION'
            explanation = (f"Source adjacent to target class ({adj_to_class}x) but never to specific target; "
                          f"expected={expected['expected']:.3f}, P(0)={expected['p_zero']:.3f}")
        elif positional_verdict == 'GENUINE_PROHIBITION':
            verdict = 'LIKELY_PROHIBITION'
            explanation = (f"Source adjacent to target class ({adj_to_class}x) but never to target; "
                          f"expected={expected['expected']:.3f}, P(0)={expected['p_zero']:.3f} (borderline)")
        elif positional_verdict == 'POSITIONALLY_SEPARATED':
            verdict = 'POSITIONAL_PLUS_FREQUENCY'
            explanation = 'Source never adjacent to target class; partially positional, partially frequency'
        else:
            verdict = 'INDETERMINATE'
            explanation = f'Positional={positional_verdict}, P(0)={expected["p_zero"]:.3f}'

        print(f"  => VERDICT: {verdict}")
        print(f"     {explanation}")
        print()

        verdicts.append({
            'source': src, 'target': tgt, 'direction': direction,
            'positional_verdict': positional_verdict,
            'boundary_gap': boundary['boundary_gap_prob'],
            'expected_count': expected['expected'],
            'p_zero': expected['p_zero'],
            'src_restart_rate': c9_rate,
            'adj_to_class': adj_to_class,
            'verdict': verdict,
            'explanation': explanation,
        })

    # Final summary
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    v_counts = Counter(v['verdict'] for v in verdicts)
    for v, c in v_counts.most_common():
        print(f"  {v}: {c}")

    genuine = sum(1 for v in verdicts if v['verdict'] in ('TOKEN_SPECIFIC_PROHIBITION', 'LIKELY_PROHIBITION'))
    artifact = sum(1 for v in verdicts if v['verdict'] in ('FREQUENCY_ARTIFACT', 'POSITIONAL_SEGREGATION'))
    print(f"\n  Genuine prohibitions: {genuine}/3")
    print(f"  Artifacts/positional: {artifact}/3")

    if genuine >= 2:
        print("\n  CONCLUSION: Majority of FQ_CLOSER forbidden pairs are GENUINE prohibitions")
        print("  -> Class 23's boundary role does NOT trivially explain the 25% gap from C627")
    elif artifact >= 2:
        print("\n  CONCLUSION: Majority of FQ_CLOSER forbidden pairs are ARTIFACTS")
        print("  -> The 25% gap from C627 is likely a boundary/frequency effect, not structural prohibition")
    else:
        print("\n  CONCLUSION: Mixed results -- FQ_CLOSER forbidden pairs have heterogeneous explanations")

    return verdicts


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("FQ_CLOSER_BOUNDARY_HAZARD: BOUNDARY MECHANISM INTEGRATION")
    print("=" * 70)
    print()
    print("Loading data...")

    ctm = load_class_token_map()
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    lines = build_b_lines()
    print(f"  Lines: {len(lines)}, Tokens: {sum(len(v) for v in lines.values())}")
    print()

    s1 = section1_boundary_asymmetry(lines, token_to_class)
    s2 = section2_restart_loop(lines, token_to_class)
    s3 = section3_expected_counts(lines, token_to_class)

    # Script 1 results path (for integrated verdict)
    overlap_path = PROJECT_ROOT / 'phases' / 'FQ_CLOSER_BOUNDARY_HAZARD' / 'results' / 'fq_closer_positional_segregation.json'

    s4 = section4_integrated_verdict(s1, s2, s3, overlap_path)

    output = {
        'metadata': {
            'phase': 'FQ_CLOSER_BOUNDARY_HAZARD',
            'script': 'fq_closer_boundary_mechanism',
            'timestamp': datetime.now().isoformat(),
        },
        'section1_boundary_asymmetry': s1,
        'section2_restart_loop': s2,
        'section3_expected_counts': s3,
        'section4_integrated_verdict': s4,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == '__main__':
    main()

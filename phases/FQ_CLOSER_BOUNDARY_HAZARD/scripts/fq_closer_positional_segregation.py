#!/usr/bin/env python3
"""
FQ_CLOSER_BOUNDARY_HAZARD - Script 1: Positional Segregation Test

Tests whether the 3 unexplained forbidden pairs from C627 are zero-observed
due to positional segregation (source in final, target in initial position)
or despite positional overlap (genuine prohibition).

Sections:
  1. Per-token positional profile (Class 23 + forbidden targets)
  2. Position overlap test (adjacency opportunities)
  3. Allowed pair positional comparison (Mann-Whitney U)
  4. Positional segregation verdict

Constraint references:
  C597: Class 23 boundary dominance (29.8% final)
  C627: 3 unexplained forbidden pairs from FQ_CLOSER
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import math

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

# ============================================================
# CONSTANTS
# ============================================================
HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

# The 3 unexplained forbidden pairs (all from FQ_CLOSER)
FORBIDDEN_PAIRS = [
    ('dy', 'aiin', 23, 9, 'CROSS_GROUP'),
    ('dy', 'chey', 23, 31, 'FORWARD'),
    ('l', 'chol', 23, 8, 'FORWARD'),
]

# Class 23 members
CLASS_23_TOKENS = {'dy', 'y', 'am', 's', 'r', 'l', 'd'}
FORBIDDEN_SOURCES = {'dy', 'l'}

RESULTS_PATH = PROJECT_ROOT / 'phases' / 'FQ_CLOSER_BOUNDARY_HAZARD' / 'results' / 'fq_closer_positional_segregation.json'


# ============================================================
# LOAD DATA
# ============================================================
def load_class_token_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_b_lines():
    """Build per-line token sequences with positional data."""
    tx = Transcript()
    lines = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        lines[key].append(token.word)
    return lines


# ============================================================
# SECTION 1: PER-TOKEN POSITIONAL PROFILE
# ============================================================
def section1_positional_profiles(lines, token_to_class, class_to_tokens):
    print("=" * 70)
    print("SECTION 1: PER-TOKEN POSITIONAL PROFILE")
    print("=" * 70)
    print()

    # Collect normalized positions for each token
    token_positions = defaultdict(list)
    for key in sorted(lines.keys()):
        words = lines[key]
        n = len(words)
        for i, w in enumerate(words):
            pos = i / (n - 1) if n > 1 else 0.5
            token_positions[w].append(pos)

    # Tokens of interest: Class 23 + targets from forbidden pairs + classmates
    # Class 23: {dy, y, am, s, r, l, d}
    # Target classes: c8 members, c9 members, c31 members
    c8_tokens = set(class_to_tokens.get('8', []))
    c9_tokens = set(class_to_tokens.get('9', []))
    c31_tokens = set(class_to_tokens.get('31', []))

    target_tokens = {
        'chey': ('c31', True), 'chol': ('c8', True), 'aiin': ('c9', True),
    }

    results = {}

    def profile(token, role_label, is_forbidden):
        positions = token_positions.get(token, [])
        count = len(positions)
        if count == 0:
            return None
        mean_pos = sum(positions) / count
        initial_rate = sum(1 for p in positions if p == 0.0) / count
        final_rate = sum(1 for p in positions if p == 1.0) / count
        q1 = sum(1 for p in positions if p <= 0.25) / count
        q2 = sum(1 for p in positions if 0.25 < p <= 0.50) / count
        q3 = sum(1 for p in positions if 0.50 < p <= 0.75) / count
        q4 = sum(1 for p in positions if 0.75 < p) / count
        return {
            'token': token, 'role': role_label, 'is_forbidden': is_forbidden,
            'count': count, 'mean_position': round(mean_pos, 4),
            'initial_rate': round(initial_rate, 4),
            'final_rate': round(final_rate, 4),
            'Q1': round(q1, 4), 'Q2': round(q2, 4),
            'Q3': round(q3, 4), 'Q4': round(q4, 4),
        }

    print("--- Class 23 (FQ_CLOSER) Token Positional Profiles ---")
    print(f"  {'Token':<8} {'Count':>6} {'Mean':>6} {'Init%':>6} {'Final%':>7} {'Q1':>6} {'Q2':>6} {'Q3':>6} {'Q4':>6} {'Forb?'}")
    c23_profiles = []
    for tok in sorted(CLASS_23_TOKENS, key=lambda t: -len(token_positions.get(t, []))):
        is_forb = tok in FORBIDDEN_SOURCES
        p = profile(tok, 'FQ_CLOSER_SRC', is_forb)
        if p:
            c23_profiles.append(p)
            flag = 'YES' if is_forb else 'no'
            print(f"  {tok:<8} {p['count']:>6} {p['mean_position']:>6.3f} {p['initial_rate']*100:>5.1f}% {p['final_rate']*100:>6.1f}% "
                  f"{p['Q1']*100:>5.1f} {p['Q2']*100:>5.1f} {p['Q3']*100:>5.1f} {p['Q4']*100:>5.1f} {flag}")
    results['class_23'] = c23_profiles

    # Forbidden targets and their classmates
    for cls_id, cls_tokens, cls_label in [('8', c8_tokens, 'EN_CHSH_c8'),
                                           ('9', c9_tokens, 'FQ_CONN_c9'),
                                           ('31', c31_tokens, 'EN_CHSH_c31')]:
        print(f"\n--- Class {cls_id} ({cls_label}) Token Positional Profiles ---")
        print(f"  {'Token':<12} {'Count':>6} {'Mean':>6} {'Init%':>6} {'Final%':>7} {'Q1':>6} {'Q2':>6} {'Q3':>6} {'Q4':>6} {'ForbTgt?'}")
        cls_profiles = []
        forbidden_targets_in_cls = {'chey', 'chol', 'aiin'}
        for tok in sorted(cls_tokens, key=lambda t: -len(token_positions.get(t, []))):
            is_forb = tok in forbidden_targets_in_cls
            p = profile(tok, cls_label, is_forb)
            if p:
                cls_profiles.append(p)
                flag = 'YES' if is_forb else 'no'
                print(f"  {tok:<12} {p['count']:>6} {p['mean_position']:>6.3f} {p['initial_rate']*100:>5.1f}% {p['final_rate']*100:>6.1f}% "
                      f"{p['Q1']*100:>5.1f} {p['Q2']*100:>5.1f} {p['Q3']*100:>5.1f} {p['Q4']*100:>5.1f} {flag}")
        results[f'class_{cls_id}'] = cls_profiles

    return results, token_positions


# ============================================================
# SECTION 2: POSITION OVERLAP TEST (CRITICAL)
# ============================================================
def section2_position_overlap(lines, token_to_class):
    print()
    print("=" * 70)
    print("SECTION 2: POSITION OVERLAP TEST (ADJACENCY OPPORTUNITIES)")
    print("=" * 70)
    print()

    results = {}

    # For each forbidden pair and its allowed alternatives, count:
    # - Lines where source appears
    # - Lines where source appears in non-final position
    # - Lines where source is non-final AND target-class token follows anywhere
    # - Lines where source is immediately followed by target-class token (adjacency)
    # - Actual observed bigrams (source, target)

    # Also compute for allowed pairs in same class-pair context
    # Allowed pairs from C627 data:
    allowed_pairs_by_context = {
        (23, 9): [('s', 'aiin', 18), ('r', 'aiin', 7), ('y', 'or', 2), ('l', 'or', 1)],
        (23, 31): [('y', 'shey', 2), ('l', 'chey', 1), ('am', 'shey', 1),
                   ('am', 'chdy', 1), ('y', 'chy', 1), ('y', 'shor', 1),
                   ('dy', 'shey', 1), ('l', 'shey', 1)],
        (23, 8): [('l', 'chedy', 2), ('l', 'shedy', 2), ('y', 'chedy', 1),
                  ('y', 'shedy', 1), ('r', 'chedy', 1), ('dy', 'chedy', 1)],
    }

    # Build class lookup for target class membership
    # Pre-compute: for each line, annotate with classes
    line_annotated = {}
    for key in sorted(lines.keys()):
        words = lines[key]
        classes = [token_to_class.get(w) for w in words]
        line_annotated[key] = list(zip(words, classes))

    def compute_overlap(src_token, tgt_token, tgt_class):
        n_src_lines = 0
        n_src_nonfinal = 0
        n_tgt_class_after_src = 0
        n_actual_adjacent = 0
        n_src_adjacent_to_tgt_class = 0

        for key, annotated in line_annotated.items():
            words_classes = annotated
            n = len(words_classes)
            src_positions = [i for i, (w, c) in enumerate(words_classes) if w == src_token]
            if not src_positions:
                continue
            n_src_lines += 1

            for sp in src_positions:
                if sp < n - 1:
                    n_src_nonfinal += 1
                    # Check if any token after src is in target class
                    tgt_class_found = False
                    for j in range(sp + 1, n):
                        if words_classes[j][1] == tgt_class:
                            tgt_class_found = True
                            break
                    if tgt_class_found:
                        n_tgt_class_after_src += 1

                    # Check immediate successor
                    next_word, next_class = words_classes[sp + 1]
                    if next_class == tgt_class:
                        n_src_adjacent_to_tgt_class += 1
                    if next_word == tgt_token:
                        n_actual_adjacent += 1

        return {
            'source': src_token, 'target': tgt_token, 'target_class': tgt_class,
            'n_src_lines': n_src_lines,
            'n_src_nonfinal': n_src_nonfinal,
            'n_tgt_class_after_src': n_tgt_class_after_src,
            'n_src_adjacent_to_tgt_class': n_src_adjacent_to_tgt_class,
            'n_actual_adjacent': n_actual_adjacent,
        }

    for src, tgt, src_cls, tgt_cls, direction in FORBIDDEN_PAIRS:
        ctx_key = (src_cls, tgt_cls)
        print(f"--- Forbidden: {src} -> {tgt} (c{src_cls} -> c{tgt_cls}, {direction}) ---")
        r = compute_overlap(src, tgt, tgt_cls)
        print(f"  Source '{src}' lines: {r['n_src_lines']}")
        print(f"  Source non-final positions: {r['n_src_nonfinal']}")
        print(f"  Target class c{tgt_cls} found after source: {r['n_tgt_class_after_src']}")
        print(f"  Source adjacent to ANY c{tgt_cls} token: {r['n_src_adjacent_to_tgt_class']}")
        print(f"  Source adjacent to '{tgt}' specifically: {r['n_actual_adjacent']} [FORBIDDEN]")

        # Now show allowed pairs in same context
        allowed_list = allowed_pairs_by_context.get(ctx_key, [])
        allowed_results = []
        print(f"\n  Allowed pairs in c{src_cls}->c{tgt_cls}:")
        for a_src, a_tgt, a_count in allowed_list:
            ar = compute_overlap(a_src, a_tgt, tgt_cls)
            allowed_results.append(ar)
            print(f"    {a_src} -> {a_tgt}: adj_to_tgt_class={ar['n_src_adjacent_to_tgt_class']}, "
                  f"adj_to_exact={ar['n_actual_adjacent']}, observed={a_count}")

        results[f"{src}->{tgt}"] = {
            'forbidden': r,
            'allowed': allowed_results,
            'direction': direction,
        }
        print()

    return results


# ============================================================
# SECTION 3: ALLOWED PAIR POSITIONAL COMPARISON
# ============================================================
def section3_positional_comparison(token_positions, token_to_class, class_to_tokens):
    print("=" * 70)
    print("SECTION 3: ALLOWED PAIR POSITIONAL COMPARISON (MANN-WHITNEY U)")
    print("=" * 70)
    print()

    results = {}

    # For each class-pair context, compare source positional distributions
    # forbidden source vs non-forbidden sources in same class pair
    contexts = [
        ('c23->c9', 'dy', ['s', 'r', 'y', 'l'], 'aiin', ['or', 'o']),
        ('c23->c31', 'dy', ['y', 'l', 'am'], 'chey', ['shey', 'chdy', 'shol', 'chy', 'char', 'shy', 'cheo', 'chor', 'shor', 'sho', 'cho']),
        ('c23->c8', 'l', ['dy', 'y', 'r'], 'chol', ['chedy', 'shedy']),
    ]

    for ctx_label, forb_src, allowed_srcs, forb_tgt, allowed_tgts in contexts:
        print(f"--- {ctx_label} ---")

        # Source comparison: forbidden source vs allowed sources
        forb_src_pos = token_positions.get(forb_src, [])
        all_allowed_src_pos = []
        for a in allowed_srcs:
            all_allowed_src_pos.extend(token_positions.get(a, []))

        src_result = {
            'forbidden_source': forb_src,
            'forbidden_source_n': len(forb_src_pos),
            'forbidden_source_mean': round(sum(forb_src_pos) / len(forb_src_pos), 4) if forb_src_pos else None,
            'allowed_sources': allowed_srcs,
            'allowed_source_n': len(all_allowed_src_pos),
            'allowed_source_mean': round(sum(all_allowed_src_pos) / len(all_allowed_src_pos), 4) if all_allowed_src_pos else None,
        }

        # Mann-Whitney U test
        if len(forb_src_pos) >= 5 and len(all_allowed_src_pos) >= 5:
            u, p = mann_whitney_u(forb_src_pos, all_allowed_src_pos)
            src_result['mw_U'] = u
            src_result['mw_p'] = round(p, 6)
            print(f"  Source: '{forb_src}' mean={src_result['forbidden_source_mean']:.3f} (n={len(forb_src_pos)}) "
                  f"vs allowed mean={src_result['allowed_source_mean']:.3f} (n={len(all_allowed_src_pos)})")
            print(f"  Mann-Whitney U={u}, p={p:.6f}")
        else:
            src_result['mw_U'] = None
            src_result['mw_p'] = None
            print(f"  Source: insufficient data for Mann-Whitney")

        # Target comparison: forbidden target vs allowed targets
        forb_tgt_pos = token_positions.get(forb_tgt, [])
        all_allowed_tgt_pos = []
        for a in allowed_tgts:
            all_allowed_tgt_pos.extend(token_positions.get(a, []))

        tgt_result = {
            'forbidden_target': forb_tgt,
            'forbidden_target_n': len(forb_tgt_pos),
            'forbidden_target_mean': round(sum(forb_tgt_pos) / len(forb_tgt_pos), 4) if forb_tgt_pos else None,
            'allowed_targets': allowed_tgts,
            'allowed_target_n': len(all_allowed_tgt_pos),
            'allowed_target_mean': round(sum(all_allowed_tgt_pos) / len(all_allowed_tgt_pos), 4) if all_allowed_tgt_pos else None,
        }

        if len(forb_tgt_pos) >= 5 and len(all_allowed_tgt_pos) >= 5:
            u, p = mann_whitney_u(forb_tgt_pos, all_allowed_tgt_pos)
            tgt_result['mw_U'] = u
            tgt_result['mw_p'] = round(p, 6)
            print(f"  Target: '{forb_tgt}' mean={tgt_result['forbidden_target_mean']:.3f} (n={len(forb_tgt_pos)}) "
                  f"vs allowed mean={tgt_result['allowed_target_mean']:.3f} (n={len(all_allowed_tgt_pos)})")
            print(f"  Mann-Whitney U={u}, p={p:.6f}")
        else:
            tgt_result['mw_U'] = None
            tgt_result['mw_p'] = None
            print(f"  Target: insufficient data for Mann-Whitney")

        results[ctx_label] = {'source': src_result, 'target': tgt_result}
        print()

    return results


def mann_whitney_u(x, y):
    """Simple Mann-Whitney U test (two-sided, normal approximation)."""
    nx, ny = len(x), len(y)
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties by averaging)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            if k not in ranks:
                ranks[k] = []
            ranks[k] = avg_rank
        i = j

    r_x = sum(ranks[i] for i in range(len(combined)) if combined[i][1] == 'x')
    u_x = r_x - nx * (nx + 1) / 2.0
    u_y = nx * ny - u_x
    u = min(u_x, u_y)

    # Normal approximation
    mu = nx * ny / 2.0
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12.0)
    if sigma == 0:
        return int(u), 1.0
    z = abs(u - mu) / sigma
    p = 2 * (1 - norm_cdf(z))
    return int(u), p


def norm_cdf(z):
    """Approximate standard normal CDF."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ============================================================
# SECTION 4: POSITIONAL SEGREGATION VERDICT
# ============================================================
def section4_verdict(overlap_results, positional_comparison):
    print("=" * 70)
    print("SECTION 4: POSITIONAL SEGREGATION VERDICT")
    print("=" * 70)
    print()

    verdicts = {}

    for src, tgt, src_cls, tgt_cls, direction in FORBIDDEN_PAIRS:
        key = f"{src}->{tgt}"
        ov = overlap_results[key]
        forb = ov['forbidden']

        n_nonfinal = forb['n_src_nonfinal']
        n_tgt_after = forb['n_tgt_class_after_src']
        n_adj_class = forb['n_src_adjacent_to_tgt_class']
        n_adj_exact = forb['n_actual_adjacent']

        # Determine verdict
        if n_nonfinal == 0:
            verdict = 'SEGREGATED'
            reason = 'Source is always line-final (never has a successor)'
        elif n_tgt_after == 0:
            verdict = 'SEGREGATED'
            reason = 'Target class never appears after source in any line'
        elif n_adj_class == 0:
            verdict = 'POSITIONALLY_SEPARATED'
            reason = 'Source reaches non-final positions but never adjacent to target class'
        elif n_adj_exact == 0 and n_adj_class > 0:
            verdict = 'GENUINE_PROHIBITION'
            reason = f'Source is adjacent to target CLASS ({n_adj_class}x) but never to specific target token'
        else:
            verdict = 'NOT_FORBIDDEN'
            reason = 'Source-target adjacency observed (should not happen for forbidden pairs)'

        verdicts[key] = {
            'source': src, 'target': tgt, 'direction': direction,
            'n_src_nonfinal': n_nonfinal,
            'n_tgt_class_after': n_tgt_after,
            'n_adj_to_class': n_adj_class,
            'n_adj_to_exact': n_adj_exact,
            'verdict': verdict,
            'reason': reason,
        }

        print(f"  {key} ({direction}): {verdict}")
        print(f"    {reason}")
        print(f"    non-final={n_nonfinal}, tgt_class_after={n_tgt_after}, adj_class={n_adj_class}, adj_exact={n_adj_exact}")
        print()

    # Summary
    v_counts = Counter(v['verdict'] for v in verdicts.values())
    print("Summary:")
    for v, c in v_counts.most_common():
        print(f"  {v}: {c}")

    return verdicts


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("FQ_CLOSER_BOUNDARY_HAZARD: POSITIONAL SEGREGATION TEST")
    print("=" * 70)
    print()
    print("Loading data...")

    ctm = load_class_token_map()
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_tokens = ctm.get('class_to_tokens', {})

    lines = build_b_lines()
    print(f"  Lines: {len(lines)}, Tokens: {sum(len(v) for v in lines.values())}")
    print()

    # Section 1
    s1_results, token_positions = section1_positional_profiles(lines, token_to_class, class_to_tokens)

    # Section 2
    s2_results = section2_position_overlap(lines, token_to_class)

    # Section 3
    s3_results = section3_positional_comparison(token_positions, token_to_class, class_to_tokens)

    # Section 4
    s4_results = section4_verdict(s2_results, s3_results)

    # Save results
    output = {
        'metadata': {
            'phase': 'FQ_CLOSER_BOUNDARY_HAZARD',
            'script': 'fq_closer_positional_segregation',
            'timestamp': datetime.now().isoformat(),
        },
        'section1_positional_profiles': s1_results,
        'section2_position_overlap': s2_results,
        'section3_positional_comparison': s3_results,
        'section4_verdict': s4_results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == '__main__':
    main()

"""
Phase 450 Follow-up: PARAGRAPH CONTINUATION HYPOTHESIS

Tests whether Mode-B-opening paragraphs inherit state from predecessors.

Questions:
  Q1: Do Mode-B-opening paragraphs share more vocabulary with their
      predecessor than Mode-A-opening paragraphs do?
  Q2: Is vocabulary flow asymmetric (forward > backward)?
  Q3: Do Mode-B-opening paragraphs cluster later in the folio sequence?
  Q4: Are Mode-B-opening paragraphs shorter (less setup needed)?
  Q5: Do Mode-B-opening paragraphs have fewer Mode-A lines overall?

References: C845, C855, C1229, C1231, C959, T2, T7
"""

import sys, json
import numpy as np
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RNG = np.random.RandomState(42)
N_PERM = 1000

# Suffix classification (from C1231)
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])


def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]
    for tok in line_toks:
        sfx = tok['suffix']
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


def load_data():
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        tokens.append({
            'folio': t.folio,
            'line': t.line,
            'word': t.word,
            'middle': m.middle if m else '',
            'suffix': m.suffix if m else '',
            'par_initial': t.par_initial,
            'par_final': t.par_final,
        })

    # Group into folios -> paragraphs -> lines
    folio_tokens = defaultdict(list)
    for tok in tokens:
        folio_tokens[tok['folio']].append(tok)

    folios = {}
    for folio, ftoks in folio_tokens.items():
        ftoks.sort(key=lambda t: t['line'])
        lines_dict = defaultdict(list)
        for tok in ftoks:
            lines_dict[tok['line']].append(tok)
        line_nums = sorted(lines_dict.keys())

        paragraphs = []
        current_para = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append((ln, line_toks))
        if current_para:
            paragraphs.append(current_para)

        folios[folio] = paragraphs

    return folios


def analyze_paragraphs(folios):
    """Build per-paragraph summaries with opening mode."""
    folio_para_data = {}

    for folio, paragraphs in folios.items():
        para_list = []
        for pi, para in enumerate(paragraphs):
            # All tokens
            all_toks = []
            for ln, toks in para:
                all_toks.extend(toks)
            if len(all_toks) < 5:
                continue

            middles = set(t['middle'] for t in all_toks if t['middle'])

            # Body lines (skip header = first line)
            body_lines = para[1:] if len(para) > 1 else para
            if not body_lines:
                continue

            # First body line's suffix mode
            first_body_toks = body_lines[0][1]
            opening_mode = classify_suffix_mode(first_body_toks)

            # All body line modes
            all_modes = []
            for ln, toks in body_lines:
                m = classify_suffix_mode(toks)
                if m:
                    all_modes.append(m)

            n_mode_a = sum(1 for m in all_modes if m == 'A')
            n_mode_b = sum(1 for m in all_modes if m == 'B')
            mode_a_frac = n_mode_a / len(all_modes) if all_modes else 0.5

            para_list.append({
                'index': pi,
                'middles': middles,
                'opening_mode': opening_mode,
                'n_tokens': len(all_toks),
                'n_body_lines': len(body_lines),
                'n_lines': len(para),
                'mode_a_frac': mode_a_frac,
                'n_mode_a': n_mode_a,
                'n_mode_b': n_mode_b,
            })

        if len(para_list) >= 2:
            folio_para_data[folio] = para_list

    return folio_para_data


def q1_mode_b_vocabulary_inheritance(folio_para_data):
    """Q1: Do Mode-B-opening paragraphs share more vocabulary with predecessor?"""
    print("\nQ1: Mode-B-opening paragraphs vs predecessor vocabulary")
    print("-" * 60)

    mode_a_jaccards = []  # Jaccard with predecessor when opening Mode A
    mode_b_jaccards = []  # Jaccard with predecessor when opening Mode B

    for folio, paras in folio_para_data.items():
        for i in range(1, len(paras)):
            prev = paras[i - 1]
            curr = paras[i]
            if curr['opening_mode'] is None:
                continue
            j = jaccard(prev['middles'], curr['middles'])
            if curr['opening_mode'] == 'A':
                mode_a_jaccards.append(j)
            else:
                mode_b_jaccards.append(j)

    if not mode_a_jaccards or not mode_b_jaccards:
        print("  SKIP: insufficient data")
        return {'verdict': 'SKIP'}

    mean_a = np.mean(mode_a_jaccards)
    mean_b = np.mean(mode_b_jaccards)
    diff = mean_b - mean_a

    # Permutation: shuffle opening mode labels across all consecutive pairs
    all_jaccards = mode_a_jaccards + mode_b_jaccards
    all_labels = ['A'] * len(mode_a_jaccards) + ['B'] * len(mode_b_jaccards)
    n_b = len(mode_b_jaccards)

    perm_diffs = []
    for _ in range(N_PERM):
        perm_labels = list(all_labels)
        RNG.shuffle(perm_labels)
        perm_a = [all_jaccards[i] for i in range(len(all_jaccards)) if perm_labels[i] == 'A']
        perm_b = [all_jaccards[i] for i in range(len(all_jaccards)) if perm_labels[i] == 'B']
        pd = np.mean(perm_b) - np.mean(perm_a) if perm_a and perm_b else 0.0
        perm_diffs.append(pd)

    p_value = np.mean([pd >= diff for pd in perm_diffs])

    print(f"  Mode A opening: mean Jaccard with predecessor = {mean_a:.4f} (n={len(mode_a_jaccards)})")
    print(f"  Mode B opening: mean Jaccard with predecessor = {mean_b:.4f} (n={len(mode_b_jaccards)})")
    print(f"  Difference (B - A): {diff:+.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  {'PASS' if p_value < 0.01 else 'FAIL'}: Mode-B-opening paragraphs "
          f"{'DO' if p_value < 0.01 else 'do NOT'} share more vocabulary with predecessor")

    return {
        'test': 'Q1_mode_b_vocabulary_inheritance',
        'mode_a_mean_jaccard': round(mean_a, 4),
        'mode_b_mean_jaccard': round(mean_b, 4),
        'diff': round(diff, 4),
        'p_value': round(p_value, 4),
        'n_mode_a': len(mode_a_jaccards),
        'n_mode_b': len(mode_b_jaccards),
        'pass': bool(p_value < 0.01),
        'verdict': 'PASS' if p_value < 0.01 else 'FAIL',
    }


def q2_asymmetric_vocabulary_flow(folio_para_data):
    """Q2: Is vocabulary flow asymmetric (forward > backward)?

    For consecutive paragraphs (N, N+1):
    - Forward: fraction of N+1's middles that appear in N
    - Backward: fraction of N's middles that appear in N+1
    If state flows forward, forward coverage > backward coverage.
    """
    print("\nQ2: Asymmetric vocabulary flow (forward vs backward)")
    print("-" * 60)

    forward_coverages = []   # fraction of N+1 middles found in N
    backward_coverages = []  # fraction of N middles found in N+1

    for folio, paras in folio_para_data.items():
        for i in range(len(paras) - 1):
            m_n = paras[i]['middles']
            m_n1 = paras[i + 1]['middles']
            if not m_n or not m_n1:
                continue
            inter = m_n & m_n1
            forward_coverages.append(len(inter) / len(m_n1))   # how much of N+1 was in N
            backward_coverages.append(len(inter) / len(m_n))    # how much of N is in N+1

    if len(forward_coverages) < 10:
        print("  SKIP: insufficient pairs")
        return {'verdict': 'SKIP'}

    mean_forward = np.mean(forward_coverages)
    mean_backward = np.mean(backward_coverages)
    asymmetry = mean_forward - mean_backward

    # Permutation: shuffle direction (swap N and N+1 randomly)
    perm_asymmetries = []
    for _ in range(N_PERM):
        pf, pb = [], []
        for f, b in zip(forward_coverages, backward_coverages):
            if RNG.random() < 0.5:
                pf.append(f)
                pb.append(b)
            else:
                pf.append(b)
                pb.append(f)
        perm_asymmetries.append(np.mean(pf) - np.mean(pb))

    p_value = np.mean([pa >= asymmetry for pa in perm_asymmetries])

    print(f"  Forward coverage (N+1 middles in N): {mean_forward:.4f}")
    print(f"  Backward coverage (N middles in N+1): {mean_backward:.4f}")
    print(f"  Asymmetry (forward - backward): {asymmetry:+.4f}")
    print(f"  p-value: {p_value:.4f}")

    if asymmetry > 0:
        direction = "FORWARD (N predicts N+1 more than reverse)"
    elif asymmetry < 0:
        direction = "BACKWARD (N+1 predicts N more -- later paragraphs are subsets)"
    else:
        direction = "SYMMETRIC"
    print(f"  Direction: {direction}")
    print(f"  {'PASS' if p_value < 0.01 else 'FAIL'}")

    return {
        'test': 'Q2_asymmetric_vocabulary_flow',
        'mean_forward_coverage': round(mean_forward, 4),
        'mean_backward_coverage': round(mean_backward, 4),
        'asymmetry': round(asymmetry, 4),
        'direction': direction,
        'p_value': round(p_value, 4),
        'n_pairs': len(forward_coverages),
        'pass': bool(p_value < 0.01),
        'verdict': 'PASS' if p_value < 0.01 else 'FAIL',
    }


def q3_mode_b_position_in_folio(folio_para_data):
    """Q3: Do Mode-B-opening paragraphs cluster later in folio sequence?"""
    print("\nQ3: Mode-B-opening position in folio sequence")
    print("-" * 60)

    mode_a_positions = []  # normalized position (0=first, 1=last)
    mode_b_positions = []

    for folio, paras in folio_para_data.items():
        n = len(paras)
        if n < 2:
            continue
        for i, p in enumerate(paras):
            if p['opening_mode'] is None:
                continue
            norm_pos = i / (n - 1) if n > 1 else 0.0
            if p['opening_mode'] == 'A':
                mode_a_positions.append(norm_pos)
            else:
                mode_b_positions.append(norm_pos)

    if not mode_a_positions or not mode_b_positions:
        print("  SKIP: insufficient data")
        return {'verdict': 'SKIP'}

    mean_a_pos = np.mean(mode_a_positions)
    mean_b_pos = np.mean(mode_b_positions)
    diff = mean_b_pos - mean_a_pos

    # Permutation
    all_pos = mode_a_positions + mode_b_positions
    all_labels = ['A'] * len(mode_a_positions) + ['B'] * len(mode_b_positions)

    perm_diffs = []
    for _ in range(N_PERM):
        perm_labels = list(all_labels)
        RNG.shuffle(perm_labels)
        pa = [all_pos[i] for i in range(len(all_pos)) if perm_labels[i] == 'A']
        pb = [all_pos[i] for i in range(len(all_pos)) if perm_labels[i] == 'B']
        perm_diffs.append(np.mean(pb) - np.mean(pa) if pa and pb else 0.0)

    p_value = np.mean([pd >= diff for pd in perm_diffs])

    print(f"  Mode A opening: mean position = {mean_a_pos:.4f} (n={len(mode_a_positions)})")
    print(f"  Mode B opening: mean position = {mean_b_pos:.4f} (n={len(mode_b_positions)})")
    print(f"  Difference (B - A): {diff:+.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  {'PASS' if p_value < 0.01 else 'FAIL'}: Mode-B-opening paragraphs "
          f"{'DO' if p_value < 0.01 else 'do NOT'} cluster later in folio")

    return {
        'test': 'Q3_mode_b_position',
        'mode_a_mean_position': round(mean_a_pos, 4),
        'mode_b_mean_position': round(mean_b_pos, 4),
        'diff': round(diff, 4),
        'p_value': round(p_value, 4),
        'n_mode_a': len(mode_a_positions),
        'n_mode_b': len(mode_b_positions),
        'pass': bool(p_value < 0.01),
        'verdict': 'PASS' if p_value < 0.01 else 'FAIL',
    }


def q4_mode_b_paragraph_length(folio_para_data):
    """Q4: Are Mode-B-opening paragraphs shorter?"""
    print("\nQ4: Mode-B-opening paragraph length")
    print("-" * 60)

    mode_a_lengths = []
    mode_b_lengths = []

    for folio, paras in folio_para_data.items():
        for p in paras:
            if p['opening_mode'] is None:
                continue
            if p['opening_mode'] == 'A':
                mode_a_lengths.append(p['n_tokens'])
            else:
                mode_b_lengths.append(p['n_tokens'])

    if not mode_a_lengths or not mode_b_lengths:
        print("  SKIP: insufficient data")
        return {'verdict': 'SKIP'}

    mean_a = np.mean(mode_a_lengths)
    mean_b = np.mean(mode_b_lengths)
    diff = mean_b - mean_a
    ratio = mean_b / mean_a if mean_a > 0 else 0.0

    # Permutation
    all_lengths = mode_a_lengths + mode_b_lengths
    all_labels = ['A'] * len(mode_a_lengths) + ['B'] * len(mode_b_lengths)

    perm_diffs = []
    for _ in range(N_PERM):
        perm_labels = list(all_labels)
        RNG.shuffle(perm_labels)
        pa = [all_lengths[i] for i in range(len(all_lengths)) if perm_labels[i] == 'A']
        pb = [all_lengths[i] for i in range(len(all_lengths)) if perm_labels[i] == 'B']
        perm_diffs.append(np.mean(pb) - np.mean(pa) if pa and pb else 0.0)

    # Two-sided test (could be shorter OR longer)
    p_value = np.mean([abs(pd) >= abs(diff) for pd in perm_diffs])

    print(f"  Mode A opening: mean tokens = {mean_a:.1f} (n={len(mode_a_lengths)})")
    print(f"  Mode B opening: mean tokens = {mean_b:.1f} (n={len(mode_b_lengths)})")
    print(f"  Ratio (B/A): {ratio:.3f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  {'PASS' if p_value < 0.01 else 'FAIL'}: Mode-B-opening paragraphs "
          f"{'ARE' if p_value < 0.01 else 'are NOT'} significantly different in length")

    return {
        'test': 'Q4_mode_b_length',
        'mode_a_mean_tokens': round(mean_a, 1),
        'mode_b_mean_tokens': round(mean_b, 1),
        'ratio': round(ratio, 3),
        'diff': round(diff, 1),
        'p_value': round(p_value, 4),
        'n_mode_a': len(mode_a_lengths),
        'n_mode_b': len(mode_b_lengths),
        'pass': bool(p_value < 0.01),
        'verdict': 'PASS' if p_value < 0.01 else 'FAIL',
    }


def q5_mode_b_internal_composition(folio_para_data):
    """Q5: Do Mode-B-opening paragraphs have fewer Mode-A lines overall?"""
    print("\nQ5: Mode-B-opening paragraph internal composition")
    print("-" * 60)

    mode_a_open_fracs = []  # Mode A fraction for paragraphs that open Mode A
    mode_b_open_fracs = []  # Mode A fraction for paragraphs that open Mode B

    for folio, paras in folio_para_data.items():
        for p in paras:
            if p['opening_mode'] is None:
                continue
            if p['n_mode_a'] + p['n_mode_b'] < 3:
                continue
            if p['opening_mode'] == 'A':
                mode_a_open_fracs.append(p['mode_a_frac'])
            else:
                mode_b_open_fracs.append(p['mode_a_frac'])

    if not mode_a_open_fracs or not mode_b_open_fracs:
        print("  SKIP: insufficient data")
        return {'verdict': 'SKIP'}

    mean_a = np.mean(mode_a_open_fracs)
    mean_b = np.mean(mode_b_open_fracs)
    diff = mean_b - mean_a

    # Permutation
    all_fracs = mode_a_open_fracs + mode_b_open_fracs
    all_labels = ['A'] * len(mode_a_open_fracs) + ['B'] * len(mode_b_open_fracs)

    perm_diffs = []
    for _ in range(N_PERM):
        perm_labels = list(all_labels)
        RNG.shuffle(perm_labels)
        pa = [all_fracs[i] for i in range(len(all_fracs)) if perm_labels[i] == 'A']
        pb = [all_fracs[i] for i in range(len(all_fracs)) if perm_labels[i] == 'B']
        perm_diffs.append(np.mean(pb) - np.mean(pa) if pa and pb else 0.0)

    p_value = np.mean([abs(pd) >= abs(diff) for pd in perm_diffs])

    print(f"  Mode-A-opening paragraphs: mean Mode A fraction = {mean_a:.4f} (n={len(mode_a_open_fracs)})")
    print(f"  Mode-B-opening paragraphs: mean Mode A fraction = {mean_b:.4f} (n={len(mode_b_open_fracs)})")
    print(f"  Difference: {diff:+.4f}")
    print(f"  p-value: {p_value:.4f}")

    if p_value < 0.01:
        if diff < 0:
            interp = "Mode-B-opening paragraphs have FEWER Mode-A lines (less internal specification)"
        else:
            interp = "Mode-B-opening paragraphs have MORE Mode-A lines (compensatory specification)"
    else:
        interp = "No difference in internal composition"
    print(f"  {interp}")
    print(f"  {'PASS' if p_value < 0.01 else 'FAIL'}")

    return {
        'test': 'Q5_mode_b_internal_composition',
        'mode_a_open_mean_frac': round(mean_a, 4),
        'mode_b_open_mean_frac': round(mean_b, 4),
        'diff': round(diff, 4),
        'p_value': round(p_value, 4),
        'interpretation': interp,
        'n_mode_a_open': len(mode_a_open_fracs),
        'n_mode_b_open': len(mode_b_open_fracs),
        'pass': bool(p_value < 0.01),
        'verdict': 'PASS' if p_value < 0.01 else 'FAIL',
    }


def opening_mode_distribution(folio_para_data):
    """Report basic distribution of opening modes."""
    print("\nOpening Mode Distribution")
    print("-" * 60)

    counts = {'A': 0, 'B': 0, 'None': 0}
    first_para_counts = {'A': 0, 'B': 0, 'None': 0}
    later_para_counts = {'A': 0, 'B': 0, 'None': 0}

    for folio, paras in folio_para_data.items():
        for i, p in enumerate(paras):
            m = p['opening_mode'] or 'None'
            counts[m] += 1
            if i == 0:
                first_para_counts[m] += 1
            else:
                later_para_counts[m] += 1

    total = sum(counts.values())
    print(f"  Total paragraphs: {total}")
    for m in ['A', 'B', 'None']:
        print(f"    Opening Mode {m}: {counts[m]} ({100*counts[m]/total:.1f}%)")

    print(f"\n  First paragraph on folio:")
    ft = sum(first_para_counts.values())
    for m in ['A', 'B', 'None']:
        print(f"    Mode {m}: {first_para_counts[m]} ({100*first_para_counts[m]/ft:.1f}%)")

    print(f"\n  Later paragraphs (2nd, 3rd, ...):")
    lt = sum(later_para_counts.values())
    for m in ['A', 'B', 'None']:
        print(f"    Mode {m}: {later_para_counts[m]} ({100*later_para_counts[m]/lt:.1f}%)")

    return {
        'total': total,
        'mode_a': counts['A'],
        'mode_b': counts['B'],
        'mode_none': counts['None'],
        'first_para': first_para_counts,
        'later_para': later_para_counts,
    }


def main():
    print("Phase 450 Follow-up: PARAGRAPH CONTINUATION HYPOTHESIS")
    print("=" * 60)

    print("\nLoading data...")
    folios = load_data()
    folio_para_data = analyze_paragraphs(folios)
    total_paras = sum(len(p) for p in folio_para_data.values())
    print(f"  {total_paras} paragraphs across {len(folio_para_data)} folios")

    dist = opening_mode_distribution(folio_para_data)
    r1 = q1_mode_b_vocabulary_inheritance(folio_para_data)
    r2 = q2_asymmetric_vocabulary_flow(folio_para_data)
    r3 = q3_mode_b_position_in_folio(folio_para_data)
    r4 = q4_mode_b_paragraph_length(folio_para_data)
    r5 = q5_mode_b_internal_composition(folio_para_data)

    results = [r1, r2, r3, r4, r5]
    n_pass = sum(1 for r in results if r.get('pass'))
    n_total = sum(1 for r in results if r.get('verdict') != 'SKIP')

    print("\n" + "=" * 60)
    print(f"SUMMARY: {n_pass}/{n_total} questions answered YES")

    if n_pass >= 3:
        verdict = "SUPPORTED -- paragraph continuation hypothesis has multiple lines of evidence"
    elif n_pass >= 1:
        verdict = "PARTIAL -- some evidence for continuation, not systematic"
    else:
        verdict = "NOT_SUPPORTED -- paragraphs appear operationally independent"
    print(f"  OVERALL: {verdict}")

    output = {
        'phase': 'Phase 450 Follow-up: PARAGRAPH_CONTINUATION_HYPOTHESIS',
        'n_pass': n_pass,
        'n_tested': n_total,
        'overall_verdict': verdict,
        'opening_mode_distribution': dist,
        'Q1_vocabulary_inheritance': r1,
        'Q2_asymmetric_flow': r2,
        'Q3_position_in_folio': r3,
        'Q4_paragraph_length': r4,
        'Q5_internal_composition': r5,
    }

    out_path = Path(__file__).resolve().parents[1] / 'results' / 'paragraph_continuation_test.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

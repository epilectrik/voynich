"""
Phase 518: Suffix Mode Cycling Mechanism
=========================================

Investigates what drives the alternation between suffix Mode A and Mode B
within paragraphs (C1229).  C1412 showed that MIDDLE TERMINAL atoms gate
suffix mode selection (V=0.503).  This phase tests whether the cycling is
fully explained by MIDDLE TERMINAL alternation, or if there is an
independent paragraph-level rhythm.

CRITICAL: C1229 defines suffix modes at the LINE level (k-means on suffix
atom frequency vectors per line), not at the token level.  Interleaving
(80%) is between consecutive LINES within a paragraph.  This script
operates at both levels as appropriate:
  - Token-level: T1-T2, T4-T6, T8 (TERMINAL/HEAD alternation, mapping)
  - Line-level: T3, T7, T9, T10 (mode cycling, interleaving, decomposition)

Tests T1-T10 (see REPORT.md for details).

Output: phases/SUFFIX_MODE_CYCLING_MECHANISM/results/suffix_mode_mechanism.json
"""

import sys
import os
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy import stats as sp_stats
from scipy.stats import chi2_contingency

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = RESULTS_DIR / 'suffix_mode_mechanism.json'

np.random.seed(42)

# ============================================================
# ATOM AND SLOT DEFINITIONS (from C1393, C1408, C1410)
# ============================================================

# MIDDLE atom roles (C1393 / C1209 / C1210)
MID_HEAD_ONLY = {'a', 'o'}           # Always initial
MID_TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}  # Always terminal
MID_FREE = {'k', 't'}                # HEAD when first, TERM when last
MID_MOD = {'p', 'c', 'i', 'f', 'd', 's'}  # Medial modifiers
MID_EXTENSIBLE = {'e', 'i'}          # Can repeat (C1197)

MID_HEAD_SET = MID_HEAD_ONLY | MID_FREE | {'e'}  # e can be HEAD
MID_TERM_SET = MID_TERM_ONLY | MID_FREE          # k/t can be TERM

# Suffix mode partition (C1410)
MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}          # THERMAL/MONITORING
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}  # STAGING/FLOW


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def atomize(s):
    """Split a string into individual atoms, respecting extensibility (e, i)."""
    if not s:
        return []
    atoms = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in MID_EXTENSIBLE:
            run = ch
            while i + 1 < len(s) and s[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def decompose_middle(middle):
    """Decompose MIDDLE into (head, mod_stack, term).

    Returns base chars for head/term (matching Phase 516 convention).
    Single-atom MIDDLEs: (atom, [], None) -- HEAD only, no TERM.
    """
    atoms = atomize(middle)
    if not atoms:
        return None, [], None
    if len(atoms) == 1:
        return atoms[0][0], [], None  # base char of HEAD

    head = None
    head_base = atoms[0][0]
    if head_base in MID_HEAD_SET or head_base in MID_FREE:
        head = atoms[0][0]  # base char
    else:
        return None, atoms, None

    term = None
    if len(atoms) >= 2:
        term_base = atoms[-1][0]
        if term_base in MID_TERM_SET:
            term = atoms[-1][0]  # base char

    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def get_suffix_mode_token(suffix):
    """Classify a single token's suffix into Mode A or Mode B.

    Uses C1410 atom partition. Returns 'A', 'B', or 'MIXED' for ties.
    Returns None if no suffix or no recognized atoms.
    """
    if not suffix:
        return None
    atoms = atomize(suffix)
    if not atoms:
        return None
    a_count = sum(1 for a in atoms if a in MODE_A_ATOMS)
    b_count = sum(1 for a in atoms if a in MODE_B_ATOMS)
    if a_count > b_count:
        return 'A'
    elif b_count > a_count:
        return 'B'
    elif a_count > 0:
        return 'MIXED'  # Tie -- exclude from analysis
    return None  # No recognized atoms


def get_line_mode(line_tokens):
    """Assign suffix mode to a LINE by aggregating suffix atoms across all tokens.

    This matches C1229/C1410 methodology: modes are line-level constructs.
    Returns 'A', 'B', 'MIXED', or None.
    """
    a_count = 0
    b_count = 0
    for t in line_tokens:
        if t['suffix']:
            for a in atomize(t['suffix']):
                if a in MODE_A_ATOMS:
                    a_count += 1
                elif a in MODE_B_ATOMS:
                    b_count += 1
    if a_count + b_count == 0:
        return None
    if a_count > b_count:
        return 'A'
    elif b_count > a_count:
        return 'B'
    else:
        return 'MIXED'


def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table (2D numpy array)."""
    ct = np.array(contingency_table, dtype=float)
    n = ct.sum()
    if n == 0:
        return 0.0, 1.0
    try:
        chi2, p, dof, _ = chi2_contingency(ct)
    except ValueError:
        return 0.0, 1.0
    k = min(ct.shape) - 1
    if k == 0 or n <= 1:
        return 0.0, 1.0
    return math.sqrt(chi2 / (n * k)), p


def mutual_info(x_vals, y_vals):
    """Compute mutual information I(X;Y) in bits."""
    joint = Counter(zip(x_vals, y_vals))
    x_counts = Counter(x_vals)
    y_counts = Counter(y_vals)
    n = len(x_vals)
    if n == 0:
        return 0.0
    mi = 0.0
    for (x, y), jc in joint.items():
        pxy = jc / n
        px = x_counts[x] / n
        py = y_counts[y] / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * math.log2(pxy / (px * py))
    return mi


def entropy_bits(values):
    """Shannon entropy in bits."""
    c = Counter(values)
    n = sum(c.values())
    if n == 0:
        return 0.0
    h = 0.0
    for count in c.values():
        p = count / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def conditional_entropy(x_vals, y_vals):
    """H(Y|X) in bits."""
    return entropy_bits(y_vals) - mutual_info(x_vals, y_vals)


# ============================================================
# DATA LOADING
# ============================================================

def load_b_tokens():
    """Load all Currier B tokens with morphological decomposition.

    Returns list of dicts, one per token, in document order.
    Each dict has: word, folio, line, section, prefix, middle, suffix,
    par_initial, par_final, line_initial, line_final,
    mid_head, mid_term, suffix_mode_token.

    mid_head and mid_term are BASE CHARS (matching Phase 516 convention).
    suffix_mode_token is token-level mode ('A', 'B', 'MIXED', or None).
    """
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        if '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        if not m.middle:
            continue

        mid_head, mid_mods, mid_term = decompose_middle(m.middle)
        suf_mode = get_suffix_mode_token(m.suffix)

        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
            'mid_head': mid_head,  # base char
            'mid_term': mid_term,  # base char
            'suffix_mode_token': suf_mode,
        })

    return tokens


def build_paragraphs(tokens):
    """Build paragraphs from token sequence using par_initial/par_final markers.

    Returns list of paragraphs, each paragraph is a list of token dicts.
    """
    paragraphs = []
    current = []
    current_folio = None

    for t in tokens:
        # Folio break = new paragraph
        if t['folio'] != current_folio:
            if current:
                paragraphs.append(current)
            current = [t]
            current_folio = t['folio']
            continue

        # par_initial = start of new paragraph
        if t['par_initial'] and current:
            paragraphs.append(current)
            current = [t]
        else:
            current.append(t)

    if current:
        paragraphs.append(current)

    return paragraphs


def build_lines_per_paragraph(paragraphs):
    """For each paragraph, group tokens by line and assign line-level modes.

    Returns list of paragraphs, where each paragraph is a list of
    (line_key, line_mode, line_tokens) tuples.
    Only includes lines with a non-MIXED, non-None mode.
    """
    para_lines = []
    for para in paragraphs:
        # Group tokens by (folio, line)
        line_groups = defaultdict(list)
        line_order = []
        for t in para:
            key = (t['folio'], t['line'])
            if key not in line_groups:
                line_order.append(key)
            line_groups[key].append(t)

        lines = []
        for key in line_order:
            toks = line_groups[key]
            mode = get_line_mode(toks)
            if mode is not None and mode != 'MIXED':
                # Compute dominant terminal for this line
                term_counts = Counter()
                for t in toks:
                    if t['mid_term'] is not None:
                        term_counts[t['mid_term']] += 1
                dominant_term = term_counts.most_common(1)[0][0] if term_counts else None

                lines.append({
                    'key': key,
                    'mode': mode,
                    'tokens': toks,
                    'dominant_term': dominant_term,
                    'n_tokens': len(toks),
                    'n_suffixed': sum(1 for t in toks if t['suffix']),
                })

        if len(lines) >= 2:  # Need at least 2 lines for alternation
            para_lines.append(lines)

    return para_lines


# ============================================================
# TEST IMPLEMENTATIONS
# ============================================================

def test_T1_terminal_alternation(paragraphs):
    """T1: Do MIDDLE TERMINAL atoms alternate within paragraphs?

    Computes lag-1 transition statistics between consecutive TERMINALs (token-level).
    Uses base chars for TERMINAL identity.
    """
    print("\n=== T1: MIDDLE TERMINAL Alternation Within Paragraphs ===")

    same_count = 0
    diff_count = 0
    transition_counts = Counter()

    for para in paragraphs:
        terms = [t['mid_term'] for t in para if t['mid_term'] is not None]
        if len(terms) < 3:
            continue
        for i in range(len(terms) - 1):
            transition_counts[(terms[i], terms[i+1])] += 1
            if terms[i] == terms[i+1]:
                same_count += 1
            else:
                diff_count += 1

    total = same_count + diff_count
    switch_rate = diff_count / total if total > 0 else 0
    same_rate = same_count / total if total > 0 else 0

    # Build transition matrix
    all_terms = sorted(set(a for (a, b) in transition_counts) |
                       set(b for (a, b) in transition_counts))
    term_idx = {t: i for i, t in enumerate(all_terms)}
    matrix = np.zeros((len(all_terms), len(all_terms)), dtype=float)
    for (a, b), cnt in transition_counts.items():
        matrix[term_idx[a], term_idx[b]] = cnt

    # Row-normalize
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    prob_matrix = matrix / row_sums

    # Expected same-rate under random (self-transition from marginals)
    marginal_counts = Counter()
    for (a, b), cnt in transition_counts.items():
        marginal_counts[a] += cnt
    total_trans = sum(transition_counts.values())
    marginal = {a: c / total_trans for a, c in marginal_counts.items()}
    expected_same = sum(p * marginal.get(a, 0) for a, p in marginal.items())

    # Chi-squared test on transition matrix
    chi2_v, chi2_p = 0.0, 1.0
    if matrix.sum() > 0 and matrix.shape[0] >= 2:
        try:
            chi2_v, chi2_p, _, _ = chi2_contingency(matrix)
        except ValueError:
            pass

    # Top self-transitions and cross-transitions
    top_self = sorted(
        [(t, prob_matrix[term_idx[t], term_idx[t]], int(matrix[term_idx[t], term_idx[t]]))
         for t in all_terms if term_idx[t] < prob_matrix.shape[0]],
        key=lambda x: -x[1]
    )[:5]

    top_cross = sorted(
        [((a, b), prob_matrix[term_idx[a], term_idx[b]], int(matrix[term_idx[a], term_idx[b]]))
         for (a, b) in transition_counts if a != b],
        key=lambda x: -x[2]
    )[:10]

    result = {
        'total_transitions': total,
        'same_rate': round(same_rate, 4),
        'switch_rate': round(switch_rate, 4),
        'expected_same_rate': round(expected_same, 4),
        'switch_vs_expected': round(switch_rate / (1 - expected_same), 4) if expected_same < 1 else None,
        'chi2': round(chi2_v, 2),
        'chi2_p': f'{chi2_p:.2e}',
        'n_terminal_types': len(all_terms),
        'top_self_transitions': [(t, round(p, 3), c) for t, p, c in top_self],
        'top_cross_transitions': [(f'{a}->{b}', round(p, 3), c) for (a, b), p, c in top_cross],
    }

    print(f"  Total TERM->TERM transitions: {total}")
    print(f"  Same-TERM rate: {same_rate:.4f} (expected under marginals: {expected_same:.4f})")
    print(f"  Switch rate: {switch_rate:.4f}")
    print(f"  Chi-squared: {chi2_v:.2f}, p={chi2_p:.2e}")

    return result


def test_T2_terminal_mode_mapping(tokens):
    """T2: How cleanly do TERMINAL atoms map to suffix modes?

    For each TERMINAL atom, compute P(Mode A) and P(Mode B).
    Uses TOKEN-level mode and base char TERMINAL (matching Phase 516).
    Excludes MIXED modes.
    """
    print("\n=== T2: TERMINAL -> Suffix Mode Mapping ===")

    # Filter to tokens with both TERMINAL and non-MIXED suffix mode
    valid = [(t['mid_term'], t['suffix_mode_token'])
             for t in tokens
             if t['mid_term'] is not None
             and t['suffix_mode_token'] is not None
             and t['suffix_mode_token'] != 'MIXED']

    if not valid:
        return {'error': 'No valid tokens'}

    terms, modes = zip(*valid)
    n = len(valid)

    # Per-terminal mode distribution
    term_mode = defaultdict(Counter)
    for te, mo in valid:
        term_mode[te][mo] += 1

    mapping = {}
    for te in sorted(term_mode.keys()):
        total_t = sum(term_mode[te].values())
        a_frac = term_mode[te].get('A', 0) / total_t
        b_frac = term_mode[te].get('B', 0) / total_t
        dominant = 'A' if a_frac >= b_frac else 'B'
        purity = max(a_frac, b_frac)
        mapping[te] = {
            'count': total_t,
            'mode_A_frac': round(a_frac, 4),
            'mode_B_frac': round(b_frac, 4),
            'dominant_mode': dominant,
            'purity': round(purity, 4),
        }

    # H(mode | terminal)
    h_mode = entropy_bits(modes)
    h_mode_given_term = conditional_entropy(terms, modes)
    mi_term_mode = mutual_info(terms, modes)

    # Cramers V
    term_set = sorted(set(terms))
    mode_set = sorted(set(modes))
    ct = np.zeros((len(term_set), len(mode_set)), dtype=float)
    t_idx = {t: i for i, t in enumerate(term_set)}
    m_idx = {m: i for i, m in enumerate(mode_set)}
    for te, mo in valid:
        ct[t_idx[te], m_idx[mo]] += 1
    v, v_p = cramers_v(ct)

    result = {
        'n_tokens': n,
        'H_mode': round(h_mode, 4),
        'H_mode_given_terminal': round(h_mode_given_term, 4),
        'MI_terminal_mode': round(mi_term_mode, 4),
        'fraction_explained': round(mi_term_mode / h_mode, 4) if h_mode > 0 else 0,
        'cramers_v': round(v, 4),
        'cramers_v_p': f'{v_p:.2e}',
        'per_terminal': mapping,
    }

    print(f"  Tokens with TERM + suffix mode: {n}")
    print(f"  H(mode): {h_mode:.4f} bits")
    print(f"  H(mode | TERMINAL): {h_mode_given_term:.4f} bits")
    print(f"  MI(TERMINAL; mode): {mi_term_mode:.4f} bits ({mi_term_mode/h_mode*100:.1f}% of H(mode))")
    print(f"  Cramer's V: {v:.4f}")
    for te in sorted(mapping, key=lambda x: -mapping[x]['count']):
        m = mapping[te]
        print(f"    {te:3s}: n={m['count']:5d}  A={m['mode_A_frac']:.3f}  B={m['mode_B_frac']:.3f}  dominant={m['dominant_mode']}  purity={m['purity']:.3f}")

    return result


def test_T3_line_mode_prediction(para_lines):
    """T3: Can we predict LINE-level suffix mode from line's dominant TERMINAL?

    Compare accuracy of:
    1. Dominant-TERMINAL-based prediction (majority class per TERMINAL)
    2. Position-based prediction (odd/even LINE index in paragraph)
    3. Baseline (majority class overall)

    Operates at LINE level to match C1229.
    """
    print("\n=== T3: Line Mode Prediction: TERMINAL vs Position ===")

    # Build TERMINAL -> majority mode from training data
    term_mode = defaultdict(Counter)
    overall_mode = Counter()
    for para in para_lines:
        for line in para:
            overall_mode[line['mode']] += 1
            if line['dominant_term']:
                term_mode[line['dominant_term']][line['mode']] += 1

    term_majority = {}
    for te, counts in term_mode.items():
        term_majority[te] = counts.most_common(1)[0][0]

    baseline_mode = overall_mode.most_common(1)[0][0]
    total_lines = sum(overall_mode.values())
    baseline_rate = overall_mode[baseline_mode] / total_lines

    # Evaluate
    correct_term = 0
    correct_base = 0
    total_pred = 0

    for para in para_lines:
        for line in para:
            actual = line['mode']
            total_pred += 1

            if baseline_mode == actual:
                correct_base += 1

            if line['dominant_term'] and line['dominant_term'] in term_majority:
                if term_majority[line['dominant_term']] == actual:
                    correct_term += 1
            else:
                if baseline_mode == actual:
                    correct_term += 1

    # Position prediction at LINE level: try both orientations
    correct_pos_ab = 0  # even=A, odd=B
    correct_pos_ba = 0  # even=B, odd=A
    for para in para_lines:
        for i, line in enumerate(para):
            if i % 2 == 0:
                if line['mode'] == 'A':
                    correct_pos_ab += 1
                else:
                    correct_pos_ba += 1
            else:
                if line['mode'] == 'B':
                    correct_pos_ab += 1
                else:
                    correct_pos_ba += 1

    correct_pos = max(correct_pos_ab, correct_pos_ba)
    pos_orientation = 'even=A,odd=B' if correct_pos_ab >= correct_pos_ba else 'even=B,odd=A'

    acc_base = correct_base / total_pred if total_pred > 0 else 0
    acc_term = correct_term / total_pred if total_pred > 0 else 0
    acc_pos = correct_pos / total_pred if total_pred > 0 else 0

    result = {
        'n_lines': total_pred,
        'baseline_accuracy': round(acc_base, 4),
        'baseline_mode': baseline_mode,
        'terminal_accuracy': round(acc_term, 4),
        'position_accuracy': round(acc_pos, 4),
        'position_orientation': pos_orientation,
        'terminal_lift_over_baseline': round(acc_term / acc_base, 4) if acc_base > 0 else None,
        'position_lift_over_baseline': round(acc_pos / acc_base, 4) if acc_base > 0 else None,
    }

    print(f"  Lines evaluated: {total_pred}")
    print(f"  Baseline (majority={baseline_mode}): {acc_base:.4f}")
    print(f"  Dominant TERMINAL prediction: {acc_term:.4f} ({acc_term/acc_base:.2f}x baseline)")
    print(f"  Position alternation ({pos_orientation}): {acc_pos:.4f} ({acc_pos/acc_base:.2f}x baseline)")

    return result


def test_T4_head_alternation(paragraphs, tokens):
    """T4: Do MIDDLE HEAD atoms alternate within paragraphs? (Token-level)"""
    print("\n=== T4: MIDDLE HEAD Alternation Within Paragraphs ===")

    same_count = 0
    diff_count = 0

    for para in paragraphs:
        heads = [t['mid_head'] for t in para if t['mid_head'] is not None]
        if len(heads) < 3:
            continue
        for i in range(len(heads) - 1):
            if heads[i] == heads[i+1]:
                same_count += 1
            else:
                diff_count += 1

    total = same_count + diff_count
    switch_rate = diff_count / total if total > 0 else 0
    same_rate = same_count / total if total > 0 else 0

    # HEAD -> suffix mode MI (token-level, excluding MIXED)
    valid_hm = [(t['mid_head'], t['suffix_mode_token'])
                for t in tokens
                if t['mid_head'] is not None
                and t['suffix_mode_token'] is not None
                and t['suffix_mode_token'] != 'MIXED']
    mi_head_mode = mutual_info([h for h, m in valid_hm], [m for h, m in valid_hm]) if valid_hm else 0
    h_mode_total = entropy_bits([m for _, m in valid_hm]) if valid_hm else 0

    # HEAD-TERMINAL correlation at token level
    valid_ht = [(t['mid_head'], t['mid_term'])
                for t in tokens
                if t['mid_head'] is not None and t['mid_term'] is not None]
    mi_head_term = mutual_info([h for h, t in valid_ht], [t for h, t in valid_ht]) if valid_ht else 0

    result = {
        'total_transitions': total,
        'same_rate': round(same_rate, 4),
        'switch_rate': round(switch_rate, 4),
        'MI_head_mode': round(mi_head_mode, 4),
        'MI_head_mode_pct': round(mi_head_mode / h_mode_total * 100, 1) if h_mode_total > 0 else 0,
        'MI_head_terminal': round(mi_head_term, 4),
    }

    print(f"  Total HEAD->HEAD transitions: {total}")
    print(f"  Same-HEAD rate: {same_rate:.4f}")
    print(f"  Switch rate: {switch_rate:.4f}")
    print(f"  MI(HEAD; suffix_mode): {mi_head_mode:.4f} bits ({result['MI_head_mode_pct']:.1f}% of H(mode))")
    print(f"  MI(HEAD; TERMINAL): {mi_head_term:.4f} bits")

    return result


def test_T5_prefix_alternation(paragraphs, tokens):
    """T5: Do PREFIXes alternate within paragraphs? (Token-level)"""
    print("\n=== T5: PREFIX Alternation Within Paragraphs ===")

    same_count = 0
    diff_count = 0

    for para in paragraphs:
        pfxs = [t['prefix'] or 'BARE' for t in para]
        for i in range(len(pfxs) - 1):
            if pfxs[i] == pfxs[i+1]:
                same_count += 1
            else:
                diff_count += 1

    total = same_count + diff_count
    switch_rate = diff_count / total if total > 0 else 0

    # PREFIX -> suffix mode MI (token-level, excluding MIXED)
    valid_pm = [(t['prefix'] or 'BARE', t['suffix_mode_token'])
                for t in tokens
                if t['suffix_mode_token'] is not None
                and t['suffix_mode_token'] != 'MIXED']
    mi_pfx_mode = mutual_info([p for p, m in valid_pm], [m for p, m in valid_pm]) if valid_pm else 0
    h_mode_total = entropy_bits([m for _, m in valid_pm]) if valid_pm else 0

    # PREFIX -> TERMINAL MI
    valid_pt = [(t['prefix'] or 'BARE', t['mid_term'])
                for t in tokens if t['mid_term'] is not None]
    mi_pfx_term = mutual_info([p for p, t in valid_pt], [t for p, t in valid_pt]) if valid_pt else 0

    result = {
        'total_transitions': total,
        'same_rate': round(1 - switch_rate, 4),
        'switch_rate': round(switch_rate, 4),
        'MI_prefix_mode': round(mi_pfx_mode, 4),
        'MI_prefix_mode_pct': round(mi_pfx_mode / h_mode_total * 100, 1) if h_mode_total > 0 else 0,
        'MI_prefix_terminal': round(mi_pfx_term, 4),
    }

    print(f"  Total PREFIX->PREFIX transitions: {total}")
    print(f"  Same-PREFIX rate: {1-switch_rate:.4f}")
    print(f"  Switch rate: {switch_rate:.4f}")
    print(f"  MI(PREFIX; suffix_mode): {mi_pfx_mode:.4f} bits ({result['MI_prefix_mode_pct']:.1f}%)")
    print(f"  MI(PREFIX; TERMINAL): {mi_pfx_term:.4f} bits")

    return result


def test_T6_token_level_prediction(tokens, paragraphs):
    """T6: Multi-predictor model for token-level suffix mode.

    Can PREFIX + HEAD + TERMINAL predict mode? Does previous mode help?
    Uses token-level mode, excluding MIXED.
    """
    print("\n=== T6: Token-Level Mode Prediction Model ===")

    # Build feature vectors for tokens with non-MIXED suffix mode
    valid = [(t['prefix'] or 'BARE', t['mid_head'] or 'NONE',
              t['mid_term'] or 'NONE', t['suffix_mode_token'])
             for t in tokens
             if t['suffix_mode_token'] is not None
             and t['suffix_mode_token'] != 'MIXED']

    n = len(valid)
    pfxs, heads, terms, modes = zip(*valid)

    h_mode = entropy_bits(modes)

    # Individual MIs
    mi_pfx = mutual_info(pfxs, modes)
    mi_head = mutual_info(heads, modes)
    mi_term = mutual_info(terms, modes)

    # Joint feature: PREFIX+HEAD+TERMINAL
    joint_features = [f'{p}|{h}|{t}' for p, h, t in zip(pfxs, heads, terms)]
    mi_joint = mutual_info(joint_features, modes)

    # Accuracy using majority vote per joint feature
    joint_mode = defaultdict(Counter)
    for jf, mo in zip(joint_features, modes):
        joint_mode[jf][mo] += 1
    joint_majority = {jf: counts.most_common(1)[0][0] for jf, counts in joint_mode.items()}
    acc_joint = sum(1 for jf, mo in zip(joint_features, modes)
                    if joint_majority[jf] == mo) / n

    baseline_mode = Counter(modes).most_common(1)[0][0]
    acc_base = sum(1 for mo in modes if mo == baseline_mode) / n

    # Sequential: does previous mode help? (within paragraphs, token-level)
    prev_modes = []
    curr_modes = []
    curr_features = []
    for para in paragraphs:
        suffixed = [t for t in para
                    if t['suffix_mode_token'] is not None
                    and t['suffix_mode_token'] != 'MIXED']
        for i in range(1, len(suffixed)):
            prev_modes.append(suffixed[i-1]['suffix_mode_token'])
            curr_modes.append(suffixed[i]['suffix_mode_token'])
            t = suffixed[i]
            curr_features.append(f"{t['prefix'] or 'BARE'}|{t['mid_head'] or 'NONE'}|{t['mid_term'] or 'NONE'}")

    if prev_modes:
        mi_prev_curr = mutual_info(prev_modes, curr_modes)
        mi_feat_curr = mutual_info(curr_features, curr_modes)
        combined = [f'{f}|{p}' for f, p in zip(curr_features, prev_modes)]
        mi_combined = mutual_info(combined, curr_modes)
        cmi_prev_given_features = mi_combined - mi_feat_curr
    else:
        mi_prev_curr = mi_feat_curr = mi_combined = cmi_prev_given_features = 0

    h_curr_mode = entropy_bits(curr_modes) if curr_modes else h_mode

    result = {
        'n_tokens': n,
        'H_mode': round(h_mode, 4),
        'MI_prefix_mode': round(mi_pfx, 4),
        'MI_head_mode': round(mi_head, 4),
        'MI_terminal_mode': round(mi_term, 4),
        'MI_joint_mode': round(mi_joint, 4),
        'pct_explained_by_joint': round(mi_joint / h_mode * 100, 1) if h_mode > 0 else 0,
        'accuracy_joint': round(acc_joint, 4),
        'accuracy_baseline': round(acc_base, 4),
        'lift_joint': round(acc_joint / acc_base, 4) if acc_base > 0 else None,
        'n_sequential_pairs': len(prev_modes),
        'MI_prev_mode_curr_mode': round(mi_prev_curr, 4),
        'MI_features_curr_mode': round(mi_feat_curr, 4),
        'MI_combined_curr_mode': round(mi_combined, 4),
        'CMI_prev_given_features': round(cmi_prev_given_features, 4),
        'CMI_prev_pct_of_H': round(cmi_prev_given_features / h_curr_mode * 100, 2) if h_curr_mode > 0 else 0,
    }

    print(f"  N tokens: {n}")
    print(f"  H(mode): {h_mode:.4f} bits")
    print(f"  MI(PREFIX; mode): {mi_pfx:.4f} ({mi_pfx/h_mode*100:.1f}%)")
    print(f"  MI(HEAD; mode): {mi_head:.4f} ({mi_head/h_mode*100:.1f}%)")
    print(f"  MI(TERMINAL; mode): {mi_term:.4f} ({mi_term/h_mode*100:.1f}%)")
    print(f"  MI(joint; mode): {mi_joint:.4f} ({mi_joint/h_mode*100:.1f}%)")
    print(f"  Accuracy: joint={acc_joint:.4f}, baseline={acc_base:.4f}, lift={acc_joint/acc_base:.2f}x")
    print(f"  Sequential pairs: {len(prev_modes)}")
    print(f"  MI(prev_mode; curr_mode): {mi_prev_curr:.4f}")
    print(f"  CMI(prev_mode; curr_mode | features): {cmi_prev_given_features:.4f} ({cmi_prev_given_features/h_curr_mode*100:.2f}%)")

    return result


def test_T7_line_sequential_dependency(para_lines):
    """T7: Is LINE-level suffix mode at N predicted by mode at N-1,
    AFTER controlling for the line's dominant TERMINAL?

    Uses LINE-level mode (C1229 granularity) with stratification by
    dominant TERMINAL atom.
    """
    print("\n=== T7: Line-Level Sequential Dependency After Controlling for TERMINAL ===")

    # Collect (prev_mode, curr_dominant_term, curr_mode) triples
    triples = []
    for para in para_lines:
        for i in range(1, len(para)):
            prev_m = para[i-1]['mode']
            curr_term = para[i]['dominant_term'] or 'NONE'
            curr_m = para[i]['mode']
            triples.append((prev_m, curr_term, curr_m))

    if not triples:
        return {'error': 'No sequential line pairs'}

    prev_modes, curr_terms, curr_modes = zip(*triples)
    n = len(triples)

    # Overall: does prev line mode predict curr line mode?
    mode_idx = {'A': 0, 'B': 1}
    ct_overall = np.zeros((2, 2), dtype=float)
    for pm, cm in zip(prev_modes, curr_modes):
        ct_overall[mode_idx[pm], mode_idx[cm]] += 1

    same_mode_rate = (ct_overall[0, 0] + ct_overall[1, 1]) / n
    switch_mode_rate = 1 - same_mode_rate

    # Within each TERMINAL: does prev_mode still predict?
    strat_results = {}
    significant_strata = 0
    n_strata_tested = 0

    for term_val in sorted(set(curr_terms)):
        mask = [i for i in range(n) if curr_terms[i] == term_val]
        if len(mask) < 20:
            continue

        sub_prev = [prev_modes[i] for i in mask]
        sub_curr = [curr_modes[i] for i in mask]

        ct_strat = np.zeros((2, 2), dtype=float)
        for pm, cm in zip(sub_prev, sub_curr):
            ct_strat[mode_idx[pm], mode_idx[cm]] += 1

        n_strat = ct_strat.sum()
        n_strata_tested += 1
        same_in_strat = (ct_strat[0, 0] + ct_strat[1, 1]) / n_strat if n_strat > 0 else 0

        try:
            chi2_s, p_s, _, _ = chi2_contingency(ct_strat, correction=True)
            sig = p_s < 0.05
            if sig:
                significant_strata += 1
        except ValueError:
            chi2_s, p_s, sig = 0, 1.0, False

        strat_results[term_val] = {
            'n': int(n_strat),
            'same_mode_rate': round(same_in_strat, 4),
            'chi2': round(chi2_s, 2),
            'p': round(p_s, 4),
            'significant': str(sig),
        }

    # MI analysis at line level
    mi_prev_curr = mutual_info(list(prev_modes), list(curr_modes))
    mi_term_curr = mutual_info(list(curr_terms), list(curr_modes))
    combined = [f'{t}|{p}' for t, p in zip(curr_terms, prev_modes)]
    mi_combined = mutual_info(combined, list(curr_modes))
    cmi_prev_given_term = mi_combined - mi_term_curr
    h_curr = entropy_bits(list(curr_modes))

    result = {
        'n_line_pairs': n,
        'overall_same_mode_rate': round(same_mode_rate, 4),
        'overall_switch_rate': round(switch_mode_rate, 4),
        'n_strata_tested': n_strata_tested,
        'significant_strata': significant_strata,
        'MI_prev_curr_mode': round(mi_prev_curr, 4),
        'MI_term_curr_mode': round(mi_term_curr, 4),
        'MI_combined': round(mi_combined, 4),
        'CMI_prev_given_term': round(cmi_prev_given_term, 4),
        'CMI_prev_pct_of_H': round(cmi_prev_given_term / h_curr * 100, 2) if h_curr > 0 else 0,
        'per_terminal': strat_results,
    }

    print(f"  Line pairs: {n}")
    print(f"  Overall same-mode rate: {same_mode_rate:.4f} (switch: {switch_mode_rate:.4f})")
    print(f"  MI(prev_line_mode; curr_line_mode): {mi_prev_curr:.4f}")
    print(f"  MI(dominant_TERM; curr_line_mode): {mi_term_curr:.4f}")
    print(f"  CMI(prev_mode; curr_mode | TERM): {cmi_prev_given_term:.4f} ({result['CMI_prev_pct_of_H']:.2f}% of H)")
    print(f"  Strata tested: {n_strata_tested}, significant: {significant_strata}")
    for te in sorted(strat_results, key=lambda x: -strat_results[x]['n']):
        sr = strat_results[te]
        sig_str = '*' if sr['significant'] == 'True' else ' '
        print(f"    {te:5s}: n={sr['n']:5d}  same={sr['same_mode_rate']:.3f}  chi2={sr['chi2']:.1f}  p={sr['p']:.4f} {sig_str}")

    return result


def test_T8_terminal_transition_constraints(paragraphs):
    """T8: Are there forbidden TERMINAL->TERMINAL transitions within paragraphs?

    Token-level analysis of TERMINAL bigram constraints.
    """
    print("\n=== T8: TERMINAL Transition Constraints ===")

    transition_counts = Counter()
    source_counts = Counter()

    for para in paragraphs:
        terms = [t['mid_term'] for t in para if t['mid_term'] is not None]
        for i in range(len(terms) - 1):
            transition_counts[(terms[i], terms[i+1])] += 1
            source_counts[terms[i]] += 1

    all_terms = sorted(set(a for (a, b) in transition_counts) |
                       set(b for (a, b) in transition_counts))
    total = sum(transition_counts.values())

    dest_counts = Counter()
    for (a, b), cnt in transition_counts.items():
        dest_counts[b] += cnt

    pair_analysis = []
    forbidden_candidates = []
    enriched_candidates = []

    for a in all_terms:
        for b in all_terms:
            obs = transition_counts.get((a, b), 0)
            exp = source_counts.get(a, 0) * dest_counts.get(b, 0) / total if total > 0 else 0
            if exp > 5:
                ratio = obs / exp if exp > 0 else 0
                pair_analysis.append({
                    'pair': f'{a}->{b}',
                    'observed': obs,
                    'expected': round(exp, 1),
                    'ratio': round(ratio, 3),
                })
                if ratio < 0.2 and obs < 3:
                    forbidden_candidates.append(f'{a}->{b}')
                if ratio > 2.5:
                    enriched_candidates.append((f'{a}->{b}', ratio, obs))

    pair_analysis.sort(key=lambda x: x['ratio'])

    # Self-transition analysis
    self_rates = {}
    for te in all_terms:
        if source_counts[te] > 50:
            self_obs = transition_counts.get((te, te), 0)
            self_rate = self_obs / source_counts[te]
            exp_rate = dest_counts.get(te, 0) / total
            self_rates[te] = {
                'self_rate': round(self_rate, 4),
                'expected': round(exp_rate, 4),
                'ratio': round(self_rate / exp_rate, 3) if exp_rate > 0 else 0,
                'n': source_counts[te],
            }

    result = {
        'total_transitions': total,
        'n_terminal_types': len(all_terms),
        'n_forbidden_candidates': len(forbidden_candidates),
        'forbidden_candidates': forbidden_candidates[:10],
        'n_enriched': len(enriched_candidates),
        'top_enriched': [(p, round(r, 2), o) for p, r, o in
                         sorted(enriched_candidates, key=lambda x: -x[1])[:10]],
        'top_depleted': pair_analysis[:10],
        'self_transition_rates': self_rates,
    }

    print(f"  Total transitions: {total}")
    print(f"  Terminal types: {len(all_terms)}")
    print(f"  Forbidden candidates: {len(forbidden_candidates)}")
    print(f"  Self-transition rates:")
    for te in sorted(self_rates, key=lambda x: -self_rates[x]['n']):
        sr = self_rates[te]
        print(f"    {te}: rate={sr['self_rate']:.3f} (exp={sr['expected']:.3f}, ratio={sr['ratio']:.2f}, n={sr['n']})")

    return result


def test_T9_line_boundary_mode_reset(para_lines):
    """T9: Does suffix mode reset at line boundaries?

    Compare within-line token-to-token mode switches vs cross-line mode switches.
    Also compare LINE-level mode persistence across line boundaries.
    """
    print("\n=== T9: Mode and Line Boundaries ===")

    # TOKEN-LEVEL: within-line vs cross-line token mode switches
    within_same = 0
    within_switch = 0
    cross_same = 0
    cross_switch = 0

    for para in para_lines:
        for line_data in para:
            toks = [t for t in line_data['tokens']
                    if t['suffix_mode_token'] and t['suffix_mode_token'] != 'MIXED']
            for i in range(1, len(toks)):
                if toks[i-1]['suffix_mode_token'] == toks[i]['suffix_mode_token']:
                    within_same += 1
                else:
                    within_switch += 1

    # Cross-line token pairs: last suffixed token of line N, first of line N+1
    for para in para_lines:
        for i in range(1, len(para)):
            prev_toks = [t for t in para[i-1]['tokens']
                         if t['suffix_mode_token'] and t['suffix_mode_token'] != 'MIXED']
            curr_toks = [t for t in para[i]['tokens']
                         if t['suffix_mode_token'] and t['suffix_mode_token'] != 'MIXED']
            if prev_toks and curr_toks:
                if prev_toks[-1]['suffix_mode_token'] == curr_toks[0]['suffix_mode_token']:
                    cross_same += 1
                else:
                    cross_switch += 1

    within_total = within_same + within_switch
    cross_total = cross_same + cross_switch

    within_switch_rate = within_switch / within_total if within_total > 0 else 0
    cross_switch_rate = cross_switch / cross_total if cross_total > 0 else 0

    ct = np.array([[within_same, within_switch], [cross_same, cross_switch]], dtype=float)
    try:
        chi2, p, _, _ = chi2_contingency(ct, correction=True)
    except ValueError:
        chi2, p = 0, 1

    # LINE-LEVEL: consecutive line mode switches
    line_same = 0
    line_switch = 0
    for para in para_lines:
        for i in range(1, len(para)):
            if para[i-1]['mode'] == para[i]['mode']:
                line_same += 1
            else:
                line_switch += 1

    line_total = line_same + line_switch
    line_switch_rate = line_switch / line_total if line_total > 0 else 0

    result = {
        'token_within_line_transitions': within_total,
        'token_within_line_switch_rate': round(within_switch_rate, 4),
        'token_cross_line_transitions': cross_total,
        'token_cross_line_switch_rate': round(cross_switch_rate, 4),
        'token_switch_rate_difference': round(cross_switch_rate - within_switch_rate, 4),
        'token_chi2': round(chi2, 2),
        'token_p': f'{p:.4e}',
        'line_level_total_pairs': line_total,
        'line_level_switch_rate': round(line_switch_rate, 4),
        'line_level_same_rate': round(1 - line_switch_rate, 4),
        'verdict': 'LINE_BOUNDARY_AFFECTS_TOKEN_MODE' if p < 0.01 else 'LINE_BOUNDARY_NEUTRAL',
    }

    print(f"  TOKEN-level within-line: {within_total} transitions, switch rate: {within_switch_rate:.4f}")
    print(f"  TOKEN-level cross-line: {cross_total} transitions, switch rate: {cross_switch_rate:.4f}")
    print(f"  Difference: {cross_switch_rate - within_switch_rate:+.4f}, chi2={chi2:.2f}, p={p:.4e}")
    print(f"  LINE-level consecutive pairs: {line_total}")
    print(f"  LINE-level mode switch rate: {line_switch_rate:.4f}")

    return result


def test_T10_decompose_C1229(para_lines, tokens):
    """T10: Decompose the C1229 interleaving pattern at LINE level.

    C1229 found 80% interleaving (silhouette 0.459) at the LINE level.
    Decompose: how much is explained by TERMINAL alternation vs
    positional rhythm vs residual?
    """
    print("\n=== T10: Decomposing C1229 Line-Level Interleaving ===")

    # Reproduce C1229 interleaving rate at LINE level
    total_pairs = 0
    interleaved_pairs = 0

    for para in para_lines:
        for i in range(1, len(para)):
            total_pairs += 1
            if para[i-1]['mode'] != para[i]['mode']:
                interleaved_pairs += 1

    interleave_rate = interleaved_pairs / total_pairs if total_pairs > 0 else 0

    # What fraction would we get from dominant-TERMINAL switching alone?
    same_term_switch = 0
    same_term_total = 0
    diff_term_switch = 0
    diff_term_total = 0

    for para in para_lines:
        for i in range(1, len(para)):
            mode_switch = para[i-1]['mode'] != para[i]['mode']
            term_prev = para[i-1]['dominant_term']
            term_curr = para[i]['dominant_term']

            if term_prev is not None and term_curr is not None:
                if term_prev == term_curr:
                    same_term_total += 1
                    if mode_switch:
                        same_term_switch += 1
                else:
                    diff_term_total += 1
                    if mode_switch:
                        diff_term_switch += 1

    same_term_switch_rate = same_term_switch / same_term_total if same_term_total > 0 else 0
    diff_term_switch_rate = diff_term_switch / diff_term_total if diff_term_total > 0 else 0

    # Dominant-TERMINAL switch rate between consecutive lines
    term_switch_count = 0
    term_total = 0
    for para in para_lines:
        for i in range(1, len(para)):
            t1 = para[i-1]['dominant_term']
            t2 = para[i]['dominant_term']
            if t1 is not None and t2 is not None:
                term_total += 1
                if t1 != t2:
                    term_switch_count += 1
    term_switch_rate = term_switch_count / term_total if term_total > 0 else 0

    # Predicted interleaving from TERMINAL switching
    predicted_from_term = (term_switch_rate * diff_term_switch_rate +
                           (1 - term_switch_rate) * same_term_switch_rate)

    # Under random model
    mode_counts = Counter()
    for para in para_lines:
        for line in para:
            mode_counts[line['mode']] += 1
    total_modes = sum(mode_counts.values())
    pa = mode_counts.get('A', 0) / total_modes
    pb = mode_counts.get('B', 0) / total_modes
    random_switch = 2 * pa * pb

    # Decomposition
    total_excess = interleave_rate - random_switch
    term_contribution = predicted_from_term - random_switch

    # Permutation test: shuffle line modes within paragraphs to test significance
    n_perms = 1000
    perm_interleave_rates = []
    for _ in range(n_perms):
        perm_count = 0
        perm_total = 0
        for para in para_lines:
            modes = [line['mode'] for line in para]
            np.random.shuffle(modes)
            for i in range(1, len(modes)):
                perm_total += 1
                if modes[i-1] != modes[i]:
                    perm_count += 1
        if perm_total > 0:
            perm_interleave_rates.append(perm_count / perm_total)

    perm_mean = np.mean(perm_interleave_rates) if perm_interleave_rates else 0
    perm_p = np.mean([r >= interleave_rate for r in perm_interleave_rates]) if perm_interleave_rates else 1

    result = {
        'total_line_pairs': total_pairs,
        'observed_interleave_rate': round(interleave_rate, 4),
        'C1229_reference': 0.80,
        'random_switch_rate': round(random_switch, 4),
        'perm_mean_switch_rate': round(perm_mean, 4),
        'perm_p_value': round(perm_p, 4),
        'dominant_term_switch_rate': round(term_switch_rate, 4),
        'mode_switch_when_same_term': round(same_term_switch_rate, 4),
        'mode_switch_when_diff_term': round(diff_term_switch_rate, 4),
        'n_same_term_pairs': same_term_total,
        'n_diff_term_pairs': diff_term_total,
        'predicted_interleave_from_terminal': round(predicted_from_term, 4),
        'excess_over_random': round(total_excess, 4),
        'terminal_contribution_to_excess': round(term_contribution, 4),
        'terminal_pct_of_excess': round(term_contribution / total_excess * 100, 1) if abs(total_excess) > 0.001 else 0,
        'residual_pct': round((1 - term_contribution / total_excess) * 100, 1) if abs(total_excess) > 0.001 else 100,
        'mode_A_proportion': round(pa, 4),
        'mode_B_proportion': round(pb, 4),
    }

    print(f"  Observed line-level interleave rate: {interleave_rate:.4f} (C1229 reference: 0.80)")
    print(f"  Random switch rate (independence): {random_switch:.4f}")
    print(f"  Permutation mean: {perm_mean:.4f}, p={perm_p:.4f}")
    print(f"  Dominant-TERM switch rate between lines: {term_switch_rate:.4f}")
    print(f"  Mode switch when SAME dominant term: {same_term_switch_rate:.4f} (n={same_term_total})")
    print(f"  Mode switch when DIFF dominant term: {diff_term_switch_rate:.4f} (n={diff_term_total})")
    print(f"  Predicted interleave from TERMINAL: {predicted_from_term:.4f}")
    print(f"  Excess over random: {total_excess:.4f}")
    if abs(total_excess) > 0.001:
        print(f"  TERMINAL contribution to excess: {term_contribution:.4f} ({term_contribution/total_excess*100:.1f}%)")
        print(f"  Residual: {(1 - term_contribution/total_excess)*100:.1f}%")
    else:
        print(f"  No excess over random to decompose")

    return result


# ============================================================
# SUPPLEMENTARY STATS
# ============================================================

def supplementary_stats(tokens, para_lines):
    """Compute summary statistics about suffix modes at token and line level."""
    print("\n=== Supplementary: Suffix Mode Statistics ===")

    n_total = len(tokens)
    n_suffixed = sum(1 for t in tokens if t['suffix'] is not None)
    n_with_mode = sum(1 for t in tokens if t['suffix_mode_token'] is not None and t['suffix_mode_token'] != 'MIXED')
    n_mixed = sum(1 for t in tokens if t['suffix_mode_token'] == 'MIXED')
    n_with_term = sum(1 for t in tokens if t['mid_term'] is not None)
    n_with_head = sum(1 for t in tokens if t['mid_head'] is not None)

    mode_counts = Counter(t['suffix_mode_token'] for t in tokens
                          if t['suffix_mode_token'] and t['suffix_mode_token'] != 'MIXED')

    # Line-level stats
    total_lines = sum(len(para) for para in para_lines)
    line_modes = Counter()
    for para in para_lines:
        for line in para:
            line_modes[line['mode']] += 1
    n_paras = len(para_lines)

    result = {
        'total_B_tokens': n_total,
        'suffixed_tokens': n_suffixed,
        'suffixed_rate': round(n_suffixed / n_total, 4),
        'tokens_with_mode': n_with_mode,
        'tokens_mixed_mode': n_mixed,
        'tokens_with_terminal': n_with_term,
        'tokens_with_head': n_with_head,
        'token_mode_A_count': mode_counts.get('A', 0),
        'token_mode_B_count': mode_counts.get('B', 0),
        'token_mode_A_fraction': round(mode_counts.get('A', 0) / n_with_mode, 4) if n_with_mode > 0 else 0,
        'line_level_total': total_lines,
        'line_mode_A_count': line_modes.get('A', 0),
        'line_mode_B_count': line_modes.get('B', 0),
        'line_mode_A_fraction': round(line_modes.get('A', 0) / total_lines, 4) if total_lines > 0 else 0,
        'n_paragraphs': n_paras,
    }

    print(f"  Total B tokens: {n_total}")
    print(f"  Suffixed: {n_suffixed} ({n_suffixed/n_total*100:.1f}%)")
    print(f"  With non-MIXED suffix mode: {n_with_mode} (MIXED excluded: {n_mixed})")
    print(f"  With MIDDLE TERMINAL: {n_with_term} ({n_with_term/n_total*100:.1f}%)")
    print(f"  Token Mode A: {mode_counts.get('A',0)} ({result['token_mode_A_fraction']*100:.1f}%)")
    print(f"  Token Mode B: {mode_counts.get('B',0)} ({(1-result['token_mode_A_fraction'])*100:.1f}%)")
    print(f"  Lines (with mode, in paragraphs with 2+ lines): {total_lines}")
    print(f"  Line Mode A: {line_modes.get('A',0)} ({result['line_mode_A_fraction']*100:.1f}%)")
    print(f"  Line Mode B: {line_modes.get('B',0)}")
    print(f"  Paragraphs with 2+ mode-assigned lines: {n_paras}")

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 518: Suffix Mode Cycling Mechanism")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    tokens = load_b_tokens()
    print(f"  Loaded {len(tokens)} Currier B tokens")

    # Build paragraphs (token-level)
    all_paras = build_paragraphs(tokens)
    MIN_SUFFIXED = 4
    paragraphs = [p for p in all_paras
                  if sum(1 for t in p if t['suffix_mode_token'] is not None
                         and t['suffix_mode_token'] != 'MIXED') >= MIN_SUFFIXED]
    print(f"  Total paragraphs: {len(all_paras)}")
    print(f"  Paragraphs with {MIN_SUFFIXED}+ non-MIXED suffixed tokens: {len(paragraphs)}")

    # Build line-level paragraph structure (for C1229-aligned tests)
    para_lines = build_lines_per_paragraph(all_paras)
    print(f"  Paragraphs with 2+ mode-assigned lines: {len(para_lines)}")
    total_lines_in_paras = sum(len(p) for p in para_lines)
    print(f"  Total lines in those paragraphs: {total_lines_in_paras}")

    results = {}

    # Supplementary stats
    results['supplementary'] = supplementary_stats(tokens, para_lines)

    # Run all tests
    results['T1_terminal_alternation'] = test_T1_terminal_alternation(paragraphs)
    results['T2_terminal_mode_mapping'] = test_T2_terminal_mode_mapping(tokens)
    results['T3_line_mode_prediction'] = test_T3_line_mode_prediction(para_lines)
    results['T4_head_alternation'] = test_T4_head_alternation(paragraphs, tokens)
    results['T5_prefix_alternation'] = test_T5_prefix_alternation(paragraphs, tokens)
    results['T6_token_level_prediction'] = test_T6_token_level_prediction(tokens, paragraphs)
    results['T7_line_sequential_dependency'] = test_T7_line_sequential_dependency(para_lines)
    results['T8_terminal_constraints'] = test_T8_terminal_transition_constraints(paragraphs)
    results['T9_line_boundaries'] = test_T9_line_boundary_mode_reset(para_lines)
    results['T10_C1229_decomposition'] = test_T10_decompose_C1229(para_lines, tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    t2 = results['T2_terminal_mode_mapping']
    t3 = results['T3_line_mode_prediction']
    t6 = results['T6_token_level_prediction']
    t7 = results['T7_line_sequential_dependency']
    t10 = results['T10_C1229_decomposition']

    print(f"\n  TOKEN-LEVEL:")
    print(f"    TERMINAL explains {t2['fraction_explained']*100:.1f}% of suffix mode entropy (V={t2['cramers_v']:.4f})")
    print(f"    Full token features explain {t6['pct_explained_by_joint']:.1f}% of mode entropy")
    print(f"    Previous token mode adds {t6['CMI_prev_pct_of_H']:.2f}% beyond token features")
    print(f"    Joint feature accuracy: {t6['accuracy_joint']:.4f} ({t6['lift_joint']:.2f}x baseline)")

    print(f"\n  LINE-LEVEL (C1229 aligned):")
    print(f"    Observed interleave rate: {t10['observed_interleave_rate']:.4f} (C1229 ref: 0.80)")
    print(f"    Random baseline: {t10['random_switch_rate']:.4f}")
    print(f"    Permutation mean: {t10['perm_mean_switch_rate']:.4f}")
    print(f"    Dominant-TERM prediction accuracy: {t3['terminal_accuracy']:.4f} ({t3['terminal_lift_over_baseline']:.2f}x baseline)")
    print(f"    Position alternation accuracy: {t3['position_accuracy']:.4f} ({t3['position_lift_over_baseline']:.2f}x baseline)")
    print(f"    Line sequential CMI(prev | TERM): {t7['CMI_prev_given_term']:.4f} ({t7['CMI_prev_pct_of_H']:.2f}% of H)")
    if abs(t10.get('excess_over_random', 0)) > 0.001:
        print(f"    TERMINAL contribution to excess interleaving: {t10['terminal_pct_of_excess']:.1f}%")
        print(f"    Residual (unexplained): {t10['residual_pct']:.1f}%")

    # Build verdict
    verdict_items = []
    if t2['fraction_explained'] > 0.15:
        verdict_items.append('TERMINAL_GATES_TOKEN_MODE')

    if t6['CMI_prev_pct_of_H'] < 2.0:
        verdict_items.append('NO_TOKEN_SEQUENTIAL_DEPENDENCY')
    elif t6['CMI_prev_pct_of_H'] < 5.0:
        verdict_items.append('WEAK_TOKEN_SEQUENTIAL_DEPENDENCY')

    if t7['CMI_prev_pct_of_H'] < 2.0:
        verdict_items.append('NO_LINE_SEQUENTIAL_DEPENDENCY')
    elif t7['CMI_prev_pct_of_H'] < 5.0:
        verdict_items.append('WEAK_LINE_SEQUENTIAL_DEPENDENCY')
    else:
        verdict_items.append('LINE_SEQUENTIAL_DEPENDENCY_PRESENT')

    excess = t10.get('excess_over_random', 0)
    if abs(excess) > 0.001:
        term_pct = t10.get('terminal_pct_of_excess', 0)
        if term_pct > 70:
            verdict_items.append('LINE_CYCLING_EXPLAINED_BY_TERMINAL')
        elif term_pct > 40:
            verdict_items.append('LINE_CYCLING_PARTIALLY_BY_TERMINAL')
        else:
            verdict_items.append('LINE_CYCLING_NOT_EXPLAINED_BY_TERMINAL')
    else:
        verdict_items.append('NO_EXCESS_INTERLEAVING')

    results['verdict'] = verdict_items
    print(f"\n  VERDICT: {' + '.join(verdict_items)}")

    # Write results
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Results written to {OUT_FILE}")


if __name__ == '__main__':
    main()

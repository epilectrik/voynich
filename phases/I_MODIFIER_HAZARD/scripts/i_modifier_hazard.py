#!/usr/bin/env python3
"""
Phase 524: The i-Modifier Hazard Anomaly

Phase 523 (C1446-C1451) revealed that all 5 standard modifiers {c,d,f,p,s}
completely quench hazard to 0%, but i (iterate) is the sole booster (1.69x,
from 24.0% to 40.6%). This phase asks: Why is iteration hazardous?

Tests:
  T1: i-modifier inventory (HEAD/TERM co-occurrence, diversity)
  T2: i-modifier and hazardous frames (confound vs inherent)
  T3: ii (double-i) vs single-i (extension effect)
  T4: i-modifier and operational category
  T5: i-modifier positional profile
  T6: i-modifier and PREFIX
  T7: i-modifier and suffix
  T8: i-modifier and the quenching modifiers (co-occurrence)
  T9: i-modifier as iteration signal (functional test)
  T10: Causal decomposition (logistic regression)

Output: phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# ============================================================================
# DATA LOADING
# ============================================================================

def load_token_class_map():
    """Load token -> 49-class mapping."""
    path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {t: int(c) for t, c in data['token_to_class'].items()}

def load_macro_state_map():
    """Load class -> macro state mapping from decoder_maps.json."""
    path = PROJECT_ROOT / 'data/decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['macro_state']['entries']
    return {k: v['value'] for k, v in entries.items()}

# The 17 forbidden MIDDLE-level transitions (from C109, C627)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'),
    ('dy', 'aiin'), ('dy', 'chey'),
    ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'),
    ('ar', 'dal'), ('c', 'ee'),
    ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
]

# HEAD+MOD+TERM slot classification (C1393)
HEAD_ATOMS = {'a', 'e', 'o'}
MODIFIER_ATOMS = {'p', 'f', 'i', 'c', 'd', 's'}
TERMINAL_ATOMS = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE_ATOMS = {'k', 't'}

# High-hazard frames from C1448
HIGH_HAZARD_FRAMES = [
    ('o', None),   # o→bare 100%
    ('d', 'y'),    # d→y 99.7%
    ('a', 'l'),    # a→l 98.9%
    ('a', 'r'),    # a→r 98.5%
    ('o', 'r'),    # o→r 98.0%
    ('e', 'e'),    # e→e 75.5%
    ('a', 'n'),    # a→n 65.6%
]


def decompose_middle(middle):
    """Decompose a MIDDLE into HEAD/MOD/TERM slots per C1393-C1394."""
    if not middle:
        return None
    atoms = list(middle)
    if len(atoms) == 1:
        return {'head': atoms[0], 'mods': [], 'term': None, 'atoms': atoms, 'raw': middle}
    head = atoms[0]
    term = atoms[-1]
    mods = atoms[1:-1] if len(atoms) > 2 else []
    return {'head': head, 'mods': mods, 'term': term, 'atoms': atoms, 'raw': middle}


def has_modifier(decomp, mod_char):
    """Check if decomposition contains a specific modifier character."""
    if not decomp:
        return False
    return mod_char in decomp['mods']


def has_i_modifier(decomp):
    """Check if decomposition contains i in modifier stack."""
    return has_modifier(decomp, 'i')


def get_i_count(decomp):
    """Count number of i atoms in the modifier stack."""
    if not decomp:
        return 0
    return decomp['mods'].count('i')


def get_frame(decomp):
    """Get the HEAD+TERM frame as tuple."""
    if not decomp:
        return None
    return (decomp['head'], decomp['term'])


def is_hazardous(category):
    """Check if a category is hazardous (FLOW or CONTAINMENT per C1280)."""
    return category in ('FLOW', 'CONTAINMENT')


# ============================================================================
# DATA COLLECTION
# ============================================================================

def collect_b_tokens():
    """Collect all Currier B tokens with full decomposition."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()
    token_class_map = load_token_class_map()
    macro_map = load_macro_state_map()
    forbidden_set = set(FORBIDDEN_PAIRS)

    tokens_by_folio_line = defaultdict(list)
    all_tokens = []

    for tok in tx.currier_b():
        word = tok.word
        if not word or not word.strip() or '*' in word:
            continue

        m = morph.extract(word)
        if not m or not m.middle:
            continue

        category = cc.classify(m.middle) or 'UNKNOWN'
        decomp = decompose_middle(m.middle)
        token_class = token_class_map.get(word)
        macro_state = macro_map.get(str(token_class)) if token_class is not None else None

        suffix = m.suffix or ''
        terminal_suffixes = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}
        if suffix in terminal_suffixes:
            suffix_mode = 'A'
        else:
            suffix_mode = 'B'

        entry = {
            'word': word,
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': suffix,
            'has_suffix': bool(suffix),
            'articulator': m.articulator,
            'category': category,
            'decomp': decomp,
            'token_class': token_class,
            'macro_state': macro_state,
            'suffix_mode': suffix_mode,
            'head_atom': decomp['head'] if decomp else None,
            'term_atom': decomp['term'] if decomp else None,
            'has_i': has_i_modifier(decomp),
            'i_count': get_i_count(decomp),
            'frame': get_frame(decomp),
            'is_hazardous': is_hazardous(category),
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
        }

        key = (tok.folio, tok.line)
        tokens_by_folio_line[key].append(entry)
        all_tokens.append(entry)

    # Compute line positions
    for key, line_tokens in tokens_by_folio_line.items():
        n = len(line_tokens)
        for idx, entry in enumerate(line_tokens):
            if n <= 1:
                entry['line_pos_frac'] = 0.5
                entry['line_quintile'] = 2
            else:
                frac = idx / (n - 1)
                entry['line_pos_frac'] = frac
                entry['line_quintile'] = min(int(frac * 5), 4)
            entry['line_length'] = n

    # Build adjacency pairs
    adjacency_pairs = []
    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for idx in range(len(line_tokens) - 1):
            src = line_tokens[idx]
            tgt = line_tokens[idx + 1]
            pair = (src['middle'], tgt['middle'])
            is_forbidden = pair in forbidden_set
            adjacency_pairs.append({
                'src': src,
                'tgt': tgt,
                'src_middle': src['middle'],
                'tgt_middle': tgt['middle'],
                'is_forbidden': is_forbidden,
            })

    return all_tokens, adjacency_pairs, tokens_by_folio_line


# ============================================================================
# FISHER'S EXACT TEST (2x2 tables)
# ============================================================================

def fisher_exact_2x2(a, b, c, d):
    """Simple p-value estimate for 2x2 tables using chi-square approximation."""
    n = a + b + c + d
    if n == 0:
        return 1.0
    expected_a = (a + b) * (a + c) / n
    expected_b = (a + b) * (b + d) / n
    expected_c = (c + d) * (a + c) / n
    expected_d = (c + d) * (b + d) / n

    chi2 = 0
    for obs, exp in [(a, expected_a), (b, expected_b), (c, expected_c), (d, expected_d)]:
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp

    # 1 df chi-square p-value approximation
    if chi2 == 0:
        return 1.0
    # Use normal approximation: p ≈ erfc(sqrt(chi2/2))
    z = math.sqrt(chi2)
    p = math.erfc(z / math.sqrt(2))
    return p


# ============================================================================
# TESTS
# ============================================================================

def test_t1_i_modifier_inventory(all_tokens):
    """T1: i-modifier inventory -- what does the i-modified population look like?"""
    print("  T1: i-modifier inventory...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    # Most frequent i-modified MIDDLEs
    i_middles = Counter(t['middle'] for t in i_tokens)
    top_i_middles = i_middles.most_common(20)

    # HEAD distribution for i-tokens vs overall
    i_head_dist = Counter(t['head_atom'] for t in i_tokens)
    all_head_dist = Counter(t['head_atom'] for t in all_tokens)
    ni = len(i_tokens)
    na = len(all_tokens)

    head_comparison = {}
    for h in set(list(i_head_dist.keys()) + list(all_head_dist.keys())):
        i_frac = i_head_dist.get(h, 0) / ni if ni > 0 else 0
        all_frac = all_head_dist.get(h, 0) / na if na > 0 else 0
        ratio = i_frac / all_frac if all_frac > 0 else float('inf')
        head_comparison[h] = {
            'i_count': i_head_dist.get(h, 0),
            'i_frac': round(i_frac, 4),
            'all_frac': round(all_frac, 4),
            'ratio': round(ratio, 3),
        }

    # TERMINAL distribution for i-tokens vs overall
    i_term_dist = Counter(t['term_atom'] for t in i_tokens if t['term_atom'] is not None)
    all_term_dist = Counter(t['term_atom'] for t in all_tokens if t['term_atom'] is not None)
    ni_term = sum(i_term_dist.values())
    na_term = sum(all_term_dist.values())

    term_comparison = {}
    for trm in set(list(i_term_dist.keys()) + list(all_term_dist.keys())):
        i_frac = i_term_dist.get(trm, 0) / ni_term if ni_term > 0 else 0
        all_frac = all_term_dist.get(trm, 0) / na_term if na_term > 0 else 0
        ratio = i_frac / all_frac if all_frac > 0 else float('inf')
        term_comparison[trm] = {
            'i_count': i_term_dist.get(trm, 0),
            'i_frac': round(i_frac, 4),
            'all_frac': round(all_frac, 4),
            'ratio': round(ratio, 3),
        }

    # Frame distribution for i-tokens
    i_frame_dist = Counter(str(t['frame']) for t in i_tokens)
    top_i_frames = i_frame_dist.most_common(15)

    # MIDDLE diversity comparison
    i_unique_middles = len(set(t['middle'] for t in i_tokens))
    all_mod_tokens = {}
    for mod_char in 'icdfps':
        mod_toks = [t for t in all_tokens if has_modifier(t['decomp'], mod_char)]
        all_mod_tokens[mod_char] = {
            'n_tokens': len(mod_toks),
            'n_unique_middles': len(set(t['middle'] for t in mod_toks)),
        }

    return {
        'n_i_tokens': ni,
        'n_non_i_tokens': len(non_i),
        'i_fraction': round(ni / na, 4) if na > 0 else 0,
        'top_i_middles': [{'middle': m, 'count': c} for m, c in top_i_middles],
        'head_comparison': head_comparison,
        'term_comparison': term_comparison,
        'top_i_frames': [{'frame': f, 'count': c} for f, c in top_i_frames],
        'modifier_diversity': all_mod_tokens,
    }


def test_t2_hazardous_frames(all_tokens):
    """T2: Is i's hazard boost explained by concentration in high-hazard frames?"""
    print("  T2: i-modifier and hazardous frames...")

    # For each high-hazard frame from C1448, count i vs non-i tokens
    frame_results = {}
    for head, term in HIGH_HAZARD_FRAMES:
        frame_key = f"{head}→{term if term else 'bare'}"
        frame_tokens = [t for t in all_tokens
                        if t['head_atom'] == head and t['term_atom'] == term]

        i_in_frame = [t for t in frame_tokens if t['has_i']]
        non_i_in_frame = [t for t in frame_tokens if not t['has_i']]

        i_hazard = sum(1 for t in i_in_frame if t['is_hazardous']) / len(i_in_frame) if i_in_frame else None
        non_i_hazard = sum(1 for t in non_i_in_frame if t['is_hazardous']) / len(non_i_in_frame) if non_i_in_frame else None

        frame_results[frame_key] = {
            'n_total': len(frame_tokens),
            'n_i': len(i_in_frame),
            'n_non_i': len(non_i_in_frame),
            'i_hazard_rate': round(i_hazard, 4) if i_hazard is not None else None,
            'non_i_hazard_rate': round(non_i_hazard, 4) if non_i_hazard is not None else None,
        }

    # Within each HEAD+TERM frame (all frames), does i increase hazard?
    frame_effect = {}
    all_frames = set()
    for t in all_tokens:
        if t['decomp'] and len(t['decomp']['atoms']) >= 2:
            all_frames.add((t['head_atom'], t['term_atom']))

    for head, term in all_frames:
        if head is None:
            continue
        frame_key = f"{head}→{term if term else 'bare'}"
        frame_tokens = [t for t in all_tokens
                        if t['head_atom'] == head and t['term_atom'] == term]

        i_toks = [t for t in frame_tokens if t['has_i']]
        non_i_toks = [t for t in frame_tokens if not t['has_i']]

        if len(i_toks) >= 5 and len(non_i_toks) >= 5:
            i_haz = sum(1 for t in i_toks if t['is_hazardous']) / len(i_toks)
            non_i_haz = sum(1 for t in non_i_toks if t['is_hazardous']) / len(non_i_toks)
            delta = i_haz - non_i_haz

            # 2x2 table: [i_haz, i_safe, non_i_haz, non_i_safe]
            a = sum(1 for t in i_toks if t['is_hazardous'])
            b = len(i_toks) - a
            c = sum(1 for t in non_i_toks if t['is_hazardous'])
            d = len(non_i_toks) - c
            p = fisher_exact_2x2(a, b, c, d)

            frame_effect[frame_key] = {
                'n_i': len(i_toks),
                'n_non_i': len(non_i_toks),
                'i_hazard': round(i_haz, 4),
                'non_i_hazard': round(non_i_haz, 4),
                'delta': round(delta, 4),
                'p_value': round(p, 6),
            }

    # Concentration test: what fraction of i-tokens are in high-hazard frames?
    high_hazard_frame_set = set()
    for head, term in HIGH_HAZARD_FRAMES:
        high_hazard_frame_set.add((head, term))

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i_tokens = [t for t in all_tokens if not t['has_i']]

    i_in_haz_frame = sum(1 for t in i_tokens if t['frame'] in high_hazard_frame_set)
    non_i_in_haz_frame = sum(1 for t in non_i_tokens if t['frame'] in high_hazard_frame_set)

    return {
        'high_hazard_frame_detail': frame_results,
        'within_frame_effect': frame_effect,
        'concentration': {
            'i_in_high_hazard_frames': i_in_haz_frame,
            'i_total': len(i_tokens),
            'i_concentration_rate': round(i_in_haz_frame / len(i_tokens), 4) if i_tokens else 0,
            'non_i_in_high_hazard_frames': non_i_in_haz_frame,
            'non_i_total': len(non_i_tokens),
            'non_i_concentration_rate': round(non_i_in_haz_frame / len(non_i_tokens), 4) if non_i_tokens else 0,
        },
    }


def test_t3_ii_vs_single_i(all_tokens):
    """T3: ii (double-i) vs single-i hazard rates."""
    print("  T3: ii vs single-i...")

    no_i = [t for t in all_tokens if t['i_count'] == 0]
    single_i = [t for t in all_tokens if t['i_count'] == 1]
    double_i = [t for t in all_tokens if t['i_count'] >= 2]

    groups = {
        'no_i': no_i,
        'single_i': single_i,
        'double_ii': double_i,
    }

    group_stats = {}
    for name, toks in groups.items():
        if not toks:
            group_stats[name] = {'n': 0}
            continue
        haz_rate = sum(1 for t in toks if t['is_hazardous']) / len(toks)
        cat_dist = Counter(t['category'] for t in toks)
        total = sum(cat_dist.values())
        cat_frac = {k: round(v / total, 4) for k, v in cat_dist.most_common()}

        head_dist = Counter(t['head_atom'] for t in toks)
        total_h = sum(head_dist.values())
        head_frac = {k: round(v / total_h, 4) for k, v in head_dist.most_common()}

        term_dist = Counter(t['term_atom'] for t in toks if t['term_atom'])
        total_t = sum(term_dist.values())
        term_frac = {k: round(v / total_t, 4) for k, v in term_dist.most_common()}

        top_middles = Counter(t['middle'] for t in toks).most_common(10)

        group_stats[name] = {
            'n': len(toks),
            'hazard_rate': round(haz_rate, 4),
            'category_dist': cat_frac,
            'head_dist': head_frac,
            'term_dist': term_frac,
            'top_middles': [{'middle': m, 'count': c} for m, c in top_middles],
        }

    # Specific check: aiin hazard rate
    aiin_tokens = [t for t in all_tokens if t['middle'] == 'aiin']
    aiin_haz = sum(1 for t in aiin_tokens if t['is_hazardous']) / len(aiin_tokens) if aiin_tokens else 0

    # All ii-containing MIDDLEs with hazard
    ii_middles = set(t['middle'] for t in double_i)
    ii_middle_hazard = {}
    for mid in ii_middles:
        mid_toks = [t for t in double_i if t['middle'] == mid]
        haz = sum(1 for t in mid_toks if t['is_hazardous']) / len(mid_toks)
        ii_middle_hazard[mid] = {'n': len(mid_toks), 'hazard_rate': round(haz, 4)}

    return {
        'group_stats': group_stats,
        'aiin_specific': {
            'n': len(aiin_tokens),
            'hazard_rate': round(aiin_haz, 4),
        },
        'ii_middle_hazard': ii_middle_hazard,
        'gradient': {
            'no_i_rate': group_stats.get('no_i', {}).get('hazard_rate', 0),
            'single_i_rate': group_stats.get('single_i', {}).get('hazard_rate', 0),
            'double_ii_rate': group_stats.get('double_ii', {}).get('hazard_rate', 0),
        },
    }


def test_t4_category(all_tokens):
    """T4: i-modifier and operational category."""
    print("  T4: i-modifier and operational category...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    i_cats = Counter(t['category'] for t in i_tokens)
    non_i_cats = Counter(t['category'] for t in non_i)
    all_cats = Counter(t['category'] for t in all_tokens)

    ni = len(i_tokens)
    nn = len(non_i)
    na = len(all_tokens)

    cat_comparison = {}
    for cat in sorted(set(list(i_cats.keys()) + list(non_i_cats.keys()))):
        i_frac = i_cats.get(cat, 0) / ni if ni > 0 else 0
        non_i_frac = non_i_cats.get(cat, 0) / nn if nn > 0 else 0
        all_frac = all_cats.get(cat, 0) / na if na > 0 else 0
        ratio = i_frac / all_frac if all_frac > 0 else float('inf')
        cat_comparison[cat] = {
            'i_count': i_cats.get(cat, 0),
            'i_frac': round(i_frac, 4),
            'non_i_frac': round(non_i_frac, 4),
            'all_frac': round(all_frac, 4),
            'ratio': round(ratio, 3),
        }

    # Instruction class distribution for i-tokens
    i_classes = Counter(t['token_class'] for t in i_tokens if t['token_class'] is not None)
    top_classes = i_classes.most_common(15)

    # Is i's hazard explained by TRANSITION concentration?
    i_transition = [t for t in i_tokens if t['category'] == 'TRANSITION']
    i_non_transition = [t for t in i_tokens if t['category'] != 'TRANSITION']

    i_tr_haz = sum(1 for t in i_transition if t['is_hazardous']) / len(i_transition) if i_transition else 0
    i_ntr_haz = sum(1 for t in i_non_transition if t['is_hazardous']) / len(i_non_transition) if i_non_transition else 0

    return {
        'category_comparison': cat_comparison,
        'top_instruction_classes': [{'class': c, 'count': n} for c, n in top_classes],
        'transition_hazard_decomposition': {
            'i_transition_n': len(i_transition),
            'i_transition_hazard': round(i_tr_haz, 4),
            'i_non_transition_n': len(i_non_transition),
            'i_non_transition_hazard': round(i_ntr_haz, 4),
        },
    }


def test_t5_positional(all_tokens):
    """T5: i-modifier positional profile."""
    print("  T5: i-modifier positional profile...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    # By line quintile
    i_by_quintile = Counter(t.get('line_quintile', -1) for t in i_tokens)
    non_i_by_quintile = Counter(t.get('line_quintile', -1) for t in non_i)
    ni = len(i_tokens)
    nn = len(non_i)

    quintile_comparison = {}
    for q in range(5):
        i_frac = i_by_quintile.get(q, 0) / ni if ni > 0 else 0
        non_i_frac = non_i_by_quintile.get(q, 0) / nn if nn > 0 else 0
        ratio = i_frac / non_i_frac if non_i_frac > 0 else float('inf')
        quintile_comparison[str(q)] = {
            'i_count': i_by_quintile.get(q, 0),
            'i_frac': round(i_frac, 4),
            'non_i_frac': round(non_i_frac, 4),
            'ratio': round(ratio, 3),
        }

    # Initial/final rates
    i_initial_rate = sum(1 for t in i_tokens if t['line_initial']) / ni if ni > 0 else 0
    non_i_initial_rate = sum(1 for t in non_i if t['line_initial']) / nn if nn > 0 else 0
    i_final_rate = sum(1 for t in i_tokens if t['line_final']) / ni if ni > 0 else 0
    non_i_final_rate = sum(1 for t in non_i if t['line_final']) / nn if nn > 0 else 0

    # Comparison with quenching modifiers
    quench_mods = ['c', 'd', 'f', 'p', 's']
    quench_positional = {}
    for mod in quench_mods:
        mod_toks = [t for t in all_tokens if has_modifier(t['decomp'], mod)]
        if not mod_toks:
            continue
        nm = len(mod_toks)
        mod_initial = sum(1 for t in mod_toks if t['line_initial']) / nm
        mod_final = sum(1 for t in mod_toks if t['line_final']) / nm
        mod_quintile = Counter(t.get('line_quintile', -1) for t in mod_toks)
        quench_positional[mod] = {
            'n': nm,
            'initial_rate': round(mod_initial, 4),
            'final_rate': round(mod_final, 4),
            'quintile_dist': {str(q): round(mod_quintile.get(q, 0) / nm, 4) for q in range(5)},
        }

    return {
        'quintile_comparison': quintile_comparison,
        'initial_final': {
            'i_initial': round(i_initial_rate, 4),
            'non_i_initial': round(non_i_initial_rate, 4),
            'initial_ratio': round(i_initial_rate / non_i_initial_rate, 3) if non_i_initial_rate > 0 else None,
            'i_final': round(i_final_rate, 4),
            'non_i_final': round(non_i_final_rate, 4),
            'final_ratio': round(i_final_rate / non_i_final_rate, 3) if non_i_final_rate > 0 else None,
        },
        'quench_modifier_positions': quench_positional,
    }


def test_t6_prefix(all_tokens):
    """T6: i-modifier and PREFIX distribution."""
    print("  T6: i-modifier and PREFIX...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    i_prefix = Counter(t['prefix'] or 'BARE' for t in i_tokens)
    non_i_prefix = Counter(t['prefix'] or 'BARE' for t in non_i)
    all_prefix = Counter(t['prefix'] or 'BARE' for t in all_tokens)
    ni = len(i_tokens)
    nn = len(non_i)
    na = len(all_tokens)

    prefix_comparison = {}
    for pfx in sorted(set(list(i_prefix.keys()) + list(non_i_prefix.keys())),
                       key=lambda x: i_prefix.get(x, 0), reverse=True):
        i_frac = i_prefix.get(pfx, 0) / ni if ni > 0 else 0
        all_frac = all_prefix.get(pfx, 0) / na if na > 0 else 0
        ratio = i_frac / all_frac if all_frac > 0 else float('inf')
        prefix_comparison[pfx] = {
            'i_count': i_prefix.get(pfx, 0),
            'i_frac': round(i_frac, 4),
            'all_frac': round(all_frac, 4),
            'ratio': round(ratio, 3),
        }

    # Check hazardous PREFIXes (do, so, ko from C1449) for i-concentration
    hazardous_prefixes = ['do', 'so', 'ko', 'to']
    haz_prefix_i_rate = {}
    for pfx in hazardous_prefixes:
        pfx_tokens = [t for t in all_tokens if (t['prefix'] or 'BARE') == pfx]
        if pfx_tokens:
            i_rate = sum(1 for t in pfx_tokens if t['has_i']) / len(pfx_tokens)
            haz_prefix_i_rate[pfx] = {
                'n': len(pfx_tokens),
                'i_rate': round(i_rate, 4),
            }

    return {
        'prefix_comparison': prefix_comparison,
        'hazardous_prefix_i_rate': haz_prefix_i_rate,
    }


def test_t7_suffix(all_tokens):
    """T7: i-modifier and suffix."""
    print("  T7: i-modifier and suffix...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    # Suffix rate
    i_suffix_rate = sum(1 for t in i_tokens if t['has_suffix']) / len(i_tokens) if i_tokens else 0
    non_i_suffix_rate = sum(1 for t in non_i if t['has_suffix']) / len(non_i) if non_i else 0

    # Suffix mode distribution
    i_mode = Counter(t['suffix_mode'] for t in i_tokens)
    non_i_mode = Counter(t['suffix_mode'] for t in non_i)
    ni = len(i_tokens)
    nn = len(non_i)

    mode_comparison = {
        'i_mode_A': round(i_mode.get('A', 0) / ni, 4) if ni > 0 else 0,
        'i_mode_B': round(i_mode.get('B', 0) / ni, 4) if ni > 0 else 0,
        'non_i_mode_A': round(non_i_mode.get('A', 0) / nn, 4) if nn > 0 else 0,
        'non_i_mode_B': round(non_i_mode.get('B', 0) / nn, 4) if nn > 0 else 0,
    }

    # Suffix distribution for i-tokens
    i_suffix_dist = Counter(t['suffix'] for t in i_tokens if t['has_suffix'])
    top_i_suffixes = i_suffix_dist.most_common(15)

    return {
        'suffix_rate': {
            'i_rate': round(i_suffix_rate, 4),
            'non_i_rate': round(non_i_suffix_rate, 4),
            'ratio': round(i_suffix_rate / non_i_suffix_rate, 3) if non_i_suffix_rate > 0 else None,
        },
        'mode_comparison': mode_comparison,
        'top_i_suffixes': [{'suffix': s, 'count': c} for s, c in top_i_suffixes],
    }


def test_t8_co_occurrence(all_tokens):
    """T8: i-modifier and the quenching modifiers -- do they co-occur?"""
    print("  T8: i-modifier and quenching modifiers co-occurrence...")

    quench_mods = set('cdfps')

    # Classify tokens into 4 groups
    i_only = []       # has i, no quencher
    quench_only = []  # has quencher, no i
    both = []         # has both i and quencher
    neither = []      # has neither

    for t in all_tokens:
        decomp = t['decomp']
        if not decomp:
            neither.append(t)
            continue

        mods = set(decomp['mods'])
        has_i = 'i' in mods
        has_q = bool(mods & quench_mods)

        if has_i and has_q:
            both.append(t)
        elif has_i:
            i_only.append(t)
        elif has_q:
            quench_only.append(t)
        else:
            neither.append(t)

    groups = {
        'i_only': i_only,
        'quench_only': quench_only,
        'both_i_and_quench': both,
        'neither': neither,
    }

    group_stats = {}
    for name, toks in groups.items():
        if not toks:
            group_stats[name] = {'n': 0, 'hazard_rate': 0}
            continue
        haz_rate = sum(1 for t in toks if t['is_hazardous']) / len(toks)
        top_middles = Counter(t['middle'] for t in toks).most_common(5)
        group_stats[name] = {
            'n': len(toks),
            'hazard_rate': round(haz_rate, 4),
            'top_middles': [{'middle': m, 'count': c} for m, c in top_middles],
        }

    # Specific co-occurring modifier pairs
    co_occur_detail = {}
    for qmod in 'cdfps':
        co_toks = [t for t in both if qmod in set(t['decomp']['mods'])]
        if co_toks:
            haz = sum(1 for t in co_toks if t['is_hazardous']) / len(co_toks)
            co_occur_detail[f'i+{qmod}'] = {
                'n': len(co_toks),
                'hazard_rate': round(haz, 4),
                'examples': list(set(t['middle'] for t in co_toks))[:5],
            }

    return {
        'group_stats': group_stats,
        'co_occurrence_detail': co_occur_detail,
        'verdict': {
            'quench_wins': group_stats.get('both_i_and_quench', {}).get('hazard_rate', 0) == 0,
            'i_only_hazard': group_stats.get('i_only', {}).get('hazard_rate', 0),
            'both_hazard': group_stats.get('both_i_and_quench', {}).get('hazard_rate', 0),
        },
    }


def test_t9_iteration_signal(all_tokens, tokens_by_folio_line):
    """T9: i-modifier as iteration signal -- functional tests."""
    print("  T9: i-modifier functional tests...")

    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i = [t for t in all_tokens if not t['has_i']]

    # T9a: i-modification by section
    i_by_section = Counter(t['section'] for t in i_tokens)
    all_by_section = Counter(t['section'] for t in all_tokens)
    section_rates = {}
    for sec in sorted(all_by_section.keys()):
        if all_by_section[sec] >= 10:
            rate = i_by_section.get(sec, 0) / all_by_section[sec]
            section_rates[sec] = {
                'i_count': i_by_section.get(sec, 0),
                'total': all_by_section[sec],
                'rate': round(rate, 4),
            }

    # T9b: i-modification and line length
    i_line_lengths = [t.get('line_length', 0) for t in i_tokens if t.get('line_length')]
    non_i_line_lengths = [t.get('line_length', 0) for t in non_i if t.get('line_length')]
    i_mean_len = sum(i_line_lengths) / len(i_line_lengths) if i_line_lengths else 0
    non_i_mean_len = sum(non_i_line_lengths) / len(non_i_line_lengths) if non_i_line_lengths else 0

    # T9c: Clustering test -- do i-modified tokens appear near other i-modified tokens?
    adjacency_counts = {'i_next_i': 0, 'i_next_non_i': 0, 'non_i_next_i': 0, 'non_i_next_non_i': 0}
    for key in tokens_by_folio_line:
        line_toks = tokens_by_folio_line[key]
        for idx in range(len(line_toks) - 1):
            curr_i = line_toks[idx]['has_i']
            next_i = line_toks[idx + 1]['has_i']
            if curr_i and next_i:
                adjacency_counts['i_next_i'] += 1
            elif curr_i and not next_i:
                adjacency_counts['i_next_non_i'] += 1
            elif not curr_i and next_i:
                adjacency_counts['non_i_next_i'] += 1
            else:
                adjacency_counts['non_i_next_non_i'] += 1

    total_pairs = sum(adjacency_counts.values())
    i_overall_rate = len(i_tokens) / len(all_tokens) if all_tokens else 0
    expected_i_i = i_overall_rate * i_overall_rate * total_pairs
    observed_i_i = adjacency_counts['i_next_i']
    clustering_ratio = observed_i_i / expected_i_i if expected_i_i > 0 else 0

    # T9d: Paragraph position
    i_par_initial = sum(1 for t in i_tokens if t['par_initial']) / len(i_tokens) if i_tokens else 0
    non_i_par_initial = sum(1 for t in non_i if t['par_initial']) / len(non_i) if non_i else 0

    return {
        'section_rates': section_rates,
        'line_length': {
            'i_mean': round(i_mean_len, 2),
            'non_i_mean': round(non_i_mean_len, 2),
            'ratio': round(i_mean_len / non_i_mean_len, 3) if non_i_mean_len > 0 else None,
        },
        'clustering': {
            'adjacency_counts': adjacency_counts,
            'i_overall_rate': round(i_overall_rate, 4),
            'expected_i_i': round(expected_i_i, 1),
            'observed_i_i': observed_i_i,
            'clustering_ratio': round(clustering_ratio, 3),
        },
        'paragraph_position': {
            'i_par_initial': round(i_par_initial, 4),
            'non_i_par_initial': round(non_i_par_initial, 4),
        },
    }


def test_t10_causal(all_tokens):
    """T10: Causal decomposition -- is i inherently hazardous or just selects hazardous frames?"""
    print("  T10: Causal decomposition...")

    # Strategy: For each frame (HEAD, TERM), compute hazard rate with and without i
    # Then average the within-frame i effect to see if i has an independent contribution

    # Build frame groups with sufficient data
    frame_groups = defaultdict(lambda: {'i': [], 'non_i': []})
    for t in all_tokens:
        if not t['decomp']:
            continue
        frame = t['frame']
        if frame is None:
            continue
        if t['has_i']:
            frame_groups[frame]['i'].append(t)
        else:
            frame_groups[frame]['non_i'].append(t)

    # Within-frame i-effect: for frames with both i and non-i tokens (min 3 each)
    within_frame_effects = []
    frame_detail = {}
    for frame, groups in frame_groups.items():
        if len(groups['i']) >= 3 and len(groups['non_i']) >= 3:
            i_haz = sum(1 for t in groups['i'] if t['is_hazardous']) / len(groups['i'])
            non_i_haz = sum(1 for t in groups['non_i'] if t['is_hazardous']) / len(groups['non_i'])
            delta = i_haz - non_i_haz
            weight = len(groups['i']) + len(groups['non_i'])
            within_frame_effects.append({
                'frame': str(frame),
                'n_i': len(groups['i']),
                'n_non_i': len(groups['non_i']),
                'i_hazard': round(i_haz, 4),
                'non_i_hazard': round(non_i_haz, 4),
                'delta': round(delta, 4),
                'weight': weight,
            })
            frame_detail[str(frame)] = within_frame_effects[-1]

    # Weighted average i-effect (controlling for frame)
    if within_frame_effects:
        total_weight = sum(e['weight'] for e in within_frame_effects)
        weighted_delta = sum(e['delta'] * e['weight'] for e in within_frame_effects) / total_weight
        n_positive = sum(1 for e in within_frame_effects if e['delta'] > 0)
        n_negative = sum(1 for e in within_frame_effects if e['delta'] < 0)
        n_zero = sum(1 for e in within_frame_effects if e['delta'] == 0)
    else:
        weighted_delta = 0
        n_positive = n_negative = n_zero = 0

    # Marginal analysis: i-effect ignoring frame
    i_tokens = [t for t in all_tokens if t['has_i']]
    non_i_tokens = [t for t in all_tokens if not t['has_i']]
    marginal_i_haz = sum(1 for t in i_tokens if t['is_hazardous']) / len(i_tokens) if i_tokens else 0
    marginal_non_i_haz = sum(1 for t in non_i_tokens if t['is_hazardous']) / len(non_i_tokens) if non_i_tokens else 0
    marginal_delta = marginal_i_haz - marginal_non_i_haz

    # Frame selection effect: how much of the marginal delta is explained by frame selection?
    frame_selection_effect = marginal_delta - weighted_delta
    if marginal_delta != 0:
        pct_frame_selection = round(frame_selection_effect / marginal_delta * 100, 1)
        pct_inherent = round(weighted_delta / marginal_delta * 100, 1)
    else:
        pct_frame_selection = 0
        pct_inherent = 0

    # HEAD-controlled analysis: within each HEAD atom, i-effect
    head_controlled = {}
    for head_atom in sorted(set(t['head_atom'] for t in all_tokens if t['head_atom'])):
        head_tokens = [t for t in all_tokens if t['head_atom'] == head_atom]
        i_head = [t for t in head_tokens if t['has_i']]
        non_i_head = [t for t in head_tokens if not t['has_i']]
        if len(i_head) >= 5 and len(non_i_head) >= 5:
            i_h = sum(1 for t in i_head if t['is_hazardous']) / len(i_head)
            ni_h = sum(1 for t in non_i_head if t['is_hazardous']) / len(non_i_head)

            a = sum(1 for t in i_head if t['is_hazardous'])
            b = len(i_head) - a
            c = sum(1 for t in non_i_head if t['is_hazardous'])
            d = len(non_i_head) - c
            p = fisher_exact_2x2(a, b, c, d)

            head_controlled[head_atom] = {
                'n_i': len(i_head),
                'n_non_i': len(non_i_head),
                'i_hazard': round(i_h, 4),
                'non_i_hazard': round(ni_h, 4),
                'delta': round(i_h - ni_h, 4),
                'p_value': round(p, 6),
            }

    # TERM-controlled analysis
    term_controlled = {}
    for term_atom in sorted(set(t['term_atom'] for t in all_tokens if t['term_atom'])):
        term_tokens = [t for t in all_tokens if t['term_atom'] == term_atom]
        i_term = [t for t in term_tokens if t['has_i']]
        non_i_term = [t for t in term_tokens if not t['has_i']]
        if len(i_term) >= 5 and len(non_i_term) >= 5:
            i_h = sum(1 for t in i_term if t['is_hazardous']) / len(i_term)
            ni_h = sum(1 for t in non_i_term if t['is_hazardous']) / len(non_i_term)

            a = sum(1 for t in i_term if t['is_hazardous'])
            b = len(i_term) - a
            c = sum(1 for t in non_i_term if t['is_hazardous'])
            d = len(non_i_term) - c
            p = fisher_exact_2x2(a, b, c, d)

            term_controlled[term_atom] = {
                'n_i': len(i_term),
                'n_non_i': len(non_i_term),
                'i_hazard': round(i_h, 4),
                'non_i_hazard': round(ni_h, 4),
                'delta': round(i_h - ni_h, 4),
                'p_value': round(p, 6),
            }

    return {
        'marginal': {
            'i_hazard': round(marginal_i_haz, 4),
            'non_i_hazard': round(marginal_non_i_haz, 4),
            'marginal_delta': round(marginal_delta, 4),
        },
        'within_frame': {
            'weighted_delta': round(weighted_delta, 4),
            'n_frames_tested': len(within_frame_effects),
            'n_positive': n_positive,
            'n_negative': n_negative,
            'n_zero': n_zero,
        },
        'decomposition': {
            'marginal_delta': round(marginal_delta, 4),
            'frame_selection_effect': round(frame_selection_effect, 4),
            'inherent_i_effect': round(weighted_delta, 4),
            'pct_frame_selection': pct_frame_selection,
            'pct_inherent': pct_inherent,
        },
        'head_controlled': head_controlled,
        'term_controlled': term_controlled,
        'frame_detail': frame_detail,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Phase 524: The i-Modifier Hazard Anomaly")
    print("=" * 60)
    print("Loading data...")

    all_tokens, adjacency_pairs, tokens_by_folio_line = collect_b_tokens()

    print(f"  Total tokens: {len(all_tokens)}")
    print(f"  Adjacency pairs: {len(adjacency_pairs)}")
    n_i = sum(1 for t in all_tokens if t['has_i'])
    print(f"  i-modified tokens: {n_i} ({n_i/len(all_tokens)*100:.1f}%)")
    print()

    print("Running tests...")
    results = {
        'phase': 'I_MODIFIER_HAZARD',
        'phase_number': 524,
        'total_tokens': len(all_tokens),
        'total_adjacency_pairs': len(adjacency_pairs),
        'n_i_tokens': n_i,
        'n_non_i_tokens': len(all_tokens) - n_i,
    }

    results['T1_inventory'] = test_t1_i_modifier_inventory(all_tokens)
    results['T2_hazardous_frames'] = test_t2_hazardous_frames(all_tokens)
    results['T3_ii_vs_single_i'] = test_t3_ii_vs_single_i(all_tokens)
    results['T4_category'] = test_t4_category(all_tokens)
    results['T5_positional'] = test_t5_positional(all_tokens)
    results['T6_prefix'] = test_t6_prefix(all_tokens)
    results['T7_suffix'] = test_t7_suffix(all_tokens)
    results['T8_co_occurrence'] = test_t8_co_occurrence(all_tokens)
    results['T9_iteration_signal'] = test_t9_iteration_signal(all_tokens, tokens_by_folio_line)
    results['T10_causal'] = test_t10_causal(all_tokens)

    # Summary
    t10 = results['T10_causal']
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Marginal i-effect: {t10['marginal']['marginal_delta']:.4f}")
    print(f"  Frame selection component: {t10['decomposition']['pct_frame_selection']:.1f}%")
    print(f"  Inherent i-effect:         {t10['decomposition']['pct_inherent']:.1f}%")
    print(f"  Within-frame delta:        {t10['within_frame']['weighted_delta']:.4f}")
    print(f"  Frames tested:             {t10['within_frame']['n_frames_tested']}")
    print(f"  Positive/Negative/Zero:    {t10['within_frame']['n_positive']}/{t10['within_frame']['n_negative']}/{t10['within_frame']['n_zero']}")

    t8 = results['T8_co_occurrence']
    print(f"\nCo-occurrence verdict:")
    print(f"  i-only hazard:             {t8['group_stats'].get('i_only', {}).get('hazard_rate', 0):.4f}")
    print(f"  i+quench hazard:           {t8['group_stats'].get('both_i_and_quench', {}).get('hazard_rate', 0):.4f}")
    print(f"  Quench wins:               {t8['verdict']['quench_wins']}")

    t3 = results['T3_ii_vs_single_i']
    print(f"\nExtension gradient:")
    print(f"  no-i:     {t3['gradient']['no_i_rate']:.4f}")
    print(f"  single-i: {t3['gradient']['single_i_rate']:.4f}")
    print(f"  double-ii: {t3['gradient']['double_ii_rate']:.4f}")

    # Write results
    output_path = PROJECT_ROOT / 'phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults written to {output_path}")


if __name__ == '__main__':
    main()

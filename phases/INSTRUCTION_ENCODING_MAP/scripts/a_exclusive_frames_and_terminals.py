"""
A-Exclusive HEAD x TERM Frames and TERMINAL Distribution Comparison
====================================================================

Two tests:

Test A: What HEAD x TERM frame combinations exist in A-exclusive MIDDLEs
        that never appear in B? These are specification-only constructs.

Test B: Do A and B MIDDLEs favor different TERMINAL atoms? If A uses more
        'l' (state) and less 'r' (respond), that's consistent with
        specification vs execution.

Uses decomposition logic from Phase 505 instruction_map.py (C1393/C1394).
"""

import sys
import os
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1209 / C1210 / C1393 / C1394
HEAD_ONLY = {'a', 'o'}       # Always initial
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}  # Always terminal
FREE = {'k', 't'}             # HEAD when first, TERM when last
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}   # Medial modifiers
EXTENSIBLE = {'e', 'i'}       # Can repeat consecutively (C1197)

HEAD_SET = HEAD_ONLY | FREE | {'e'}   # e can be HEAD (e-initial very common)
TERM_SET = TERM_ONLY | FREE           # k/t terminal when last

# dy is treated as a single fused TERM atom
FUSED_TERM = 'dy'

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt', 'dy': 'seal',
}

# Category biases for TERMINAL atoms (from C1394 T5)
TERM_CATEGORY_BIAS = {
    'r': '99% FLOW',
    'm': '87% TRANSITION',
    'n': '64% TRANSITION',
    'y': '56% OPERATION',
    'l': '47% STAGING',
    'h': 'transparent',
    'k': 'THERMAL-biased',
    't': 'MONITORING-biased',
    'dy': 'seal/END-class',
}


# --- Atom Decomposition -------------------------------------------

def atomize(middle):
    """Split a MIDDLE string into atoms, handling dy fused pair and extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        # Check for fused 'dy' terminal at the end
        if i == len(middle) - 2 and middle[i:] == 'dy':
            atoms.append('dy')
            i += 2
            continue

        ch = middle[i]
        # Collect runs of extensible atoms
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def decompose(middle):
    """Decompose a MIDDLE into HEAD, MOD_STACK, TERM.

    Returns (head, mod_stack, term) where:
    - head: first atom if it can be HEAD, else None
    - term: last atom if it can be TERM (including 'dy' fused), else None
    - mod_stack: everything in between
    """
    atoms = atomize(middle)

    if len(atoms) == 0:
        return None, [], None

    if len(atoms) == 1:
        return atoms[0], [], None

    # Determine HEAD: first atom
    head = None
    head_base = atoms[0][0]  # First char (handles 'ee', 'ii')
    if head_base in HEAD_SET or head_base in FREE:
        head = atoms[0]
    else:
        # First atom isn't a valid HEAD
        return None, atoms, None

    # Determine TERM: last atom
    term = None
    last = atoms[-1]
    if last == 'dy':
        term = 'dy'
    elif last[0] in TERM_SET:
        term = last
    elif last[0] in MOD_ONLY:
        term = None  # Modifier at end, no terminal

    # MOD stack: everything between HEAD and TERM
    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def get_frame(head, term):
    """Return the HEAD x TERM frame string, normalizing extensible atoms."""
    h = head[0] if head else '_'  # Normalize ee->e, ii->i for frame
    if term == 'dy':
        t = 'dy'
    elif term:
        t = term[0]  # Normalize
    else:
        t = '_'
    return f'{h}x{t}'


# --- Data Loading -------------------------------------------------

def load_all_middles():
    """Load MIDDLEs from all three systems with token counts."""
    tx = Transcript()
    morph = Morphology()

    a_middles = Counter()  # All A MIDDLEs with counts
    b_middles = Counter()  # All B MIDDLEs with counts

    for tok in tx.currier_a():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle and m.middle != '_EMPTY_':
            a_middles[m.middle] += 1

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle and m.middle != '_EMPTY_':
            b_middles[m.middle] += 1

    return a_middles, b_middles


# --- TEST A: A-Exclusive HEAD x TERM Frames -----------------------

def test_a_frames(a_middles, b_middles):
    """Find HEAD x TERM frames that are A-exclusive or B-exclusive."""
    print("=" * 80)
    print("TEST A: A-Exclusive HEAD x TERM Frames")
    print("=" * 80)

    a_types = set(a_middles.keys())
    b_types = set(b_middles.keys())
    a_exclusive = a_types - b_types
    b_exclusive = b_types - a_types
    shared = a_types & b_types

    print(f"\nVocabulary partition:")
    print(f"  A-exclusive MIDDLEs: {len(a_exclusive)} types")
    print(f"  B-exclusive MIDDLEs: {len(b_exclusive)} types")
    print(f"  Shared MIDDLEs:      {len(shared)} types")

    # Decompose all compound MIDDLEs (length >= 2)
    def get_frames(middle_set, counts):
        """Get frame distribution from a set of MIDDLEs."""
        frame_counter = Counter()
        frame_types = defaultdict(set)
        frame_tokens = Counter()
        frame_examples = defaultdict(list)
        decomp_count = 0
        headless_count = 0
        termless_count = 0
        single_atom = 0

        for mid in middle_set:
            if len(mid) < 2:
                single_atom += 1
                continue

            head, mods, term = decompose(mid)
            decomp_count += 1

            if head is None:
                headless_count += 1
                continue

            frame = get_frame(head, term)
            frame_counter[frame] += 1
            frame_types[frame].add(mid)
            frame_tokens[frame] += counts.get(mid, 1)
            if len(frame_examples[frame]) < 5:
                frame_examples[frame].append(mid)

        stats = {
            'total_compounds': decomp_count,
            'single_atoms': single_atom,
            'headless': headless_count,
            'termless': termless_count,
        }
        return frame_counter, frame_types, frame_tokens, frame_examples, stats

    # Build frames for each population
    a_excl_frames, a_excl_types, a_excl_tokens, a_excl_ex, a_excl_stats = \
        get_frames(a_exclusive, a_middles)
    b_frames, b_types_map, b_tokens, b_ex, b_stats = \
        get_frames(b_types, b_middles)
    a_all_frames, a_all_types, a_all_tokens, a_all_ex, a_all_stats = \
        get_frames(a_types, a_middles)

    print(f"\n--- A-exclusive decomposition ---")
    print(f"  Compounds (len>=2): {a_excl_stats['total_compounds']}")
    print(f"  Single atoms:       {a_excl_stats['single_atoms']}")
    print(f"  Headless (no valid HEAD): {a_excl_stats['headless']}")
    print(f"  Unique frames:      {len(a_excl_frames)}")

    print(f"\n--- B (all) decomposition ---")
    print(f"  Compounds (len>=2): {b_stats['total_compounds']}")
    print(f"  Single atoms:       {b_stats['single_atoms']}")
    print(f"  Headless:           {b_stats['headless']}")
    print(f"  Unique frames:      {len(b_frames)}")

    # Find frames exclusive to A-exclusive MIDDLEs
    a_excl_frame_set = set(a_excl_frames.keys())
    b_frame_set = set(b_frames.keys())
    a_only_frames = a_excl_frame_set - b_frame_set
    b_only_frames = b_frame_set - a_excl_frame_set
    shared_frames = a_excl_frame_set & b_frame_set

    print(f"\n--- Frame Exclusivity ---")
    print(f"  Frames in A-exclusive only: {len(a_only_frames)}")
    print(f"  Frames in B only:           {len(b_only_frames)}")
    print(f"  Frames shared:              {len(shared_frames)}")

    if a_only_frames:
        print(f"\n  A-ONLY frames (specification constructs never used in execution):")
        for frame in sorted(a_only_frames):
            n_types = a_excl_frames[frame]
            n_tokens = a_excl_tokens[frame]
            examples = a_excl_ex[frame][:5]
            h, t = frame.split('x')
            h_gloss = ATOM_GLOSS.get(h, '?')
            t_gloss = ATOM_GLOSS.get(t, '?') if t != '_' else 'NONE'
            print(f"    {frame:8s} ({h_gloss}+{t_gloss}): {n_types} types, {n_tokens} tokens")
            print(f"             examples: {', '.join(examples)}")

    if b_only_frames:
        print(f"\n  B-ONLY frames (execution constructs absent from A-exclusive):")
        for frame in sorted(b_only_frames):
            n_types = b_frames[frame]
            n_tokens = b_tokens[frame]
            examples = b_ex[frame][:5]
            h, t = frame.split('x')
            h_gloss = ATOM_GLOSS.get(h, '?')
            t_gloss = ATOM_GLOSS.get(t, '?') if t != '_' else 'NONE'
            print(f"    {frame:8s} ({h_gloss}+{t_gloss}): {n_types} types, {n_tokens} tokens")
            print(f"             examples: {', '.join(examples)}")

    # For shared frames, compare relative frequencies
    print(f"\n--- Shared Frame Frequency Comparison ---")
    print(f"  {'Frame':<10s} {'A-excl types':>14s} {'B types':>10s} {'A/B ratio':>10s}  HEAD+TERM")

    shared_comparison = []
    for frame in sorted(shared_frames, key=lambda f: a_excl_frames[f], reverse=True):
        a_n = a_excl_frames[frame]
        b_n = b_frames[frame]
        # Normalize by total frames
        a_frac = a_n / sum(a_excl_frames.values()) if sum(a_excl_frames.values()) > 0 else 0
        b_frac = b_n / sum(b_frames.values()) if sum(b_frames.values()) > 0 else 0
        ratio = a_frac / b_frac if b_frac > 0 else float('inf')
        h, t = frame.split('x')
        h_gloss = ATOM_GLOSS.get(h, '?')
        t_gloss = ATOM_GLOSS.get(t, '?') if t != '_' else 'NONE'
        print(f"  {frame:<10s} {a_n:>14d} {b_n:>10d} {ratio:>10.3f}  {h_gloss}+{t_gloss}")
        shared_comparison.append({
            'frame': frame,
            'a_excl_types': a_n,
            'b_types': b_n,
            'a_frac': round(a_frac, 4),
            'b_frac': round(b_frac, 4),
            'ratio': round(ratio, 3),
            'head_gloss': h_gloss,
            'term_gloss': t_gloss,
        })

    # HEAD concentration in A-only frames
    if a_only_frames:
        a_only_heads = Counter()
        a_only_terms = Counter()
        for frame in a_only_frames:
            h, t = frame.split('x')
            a_only_heads[h] += a_excl_frames[frame]
            a_only_terms[t] += a_excl_frames[frame]

        print(f"\n  HEAD concentration in A-only frames:")
        for h, c in a_only_heads.most_common():
            print(f"    {h} ({ATOM_GLOSS.get(h, '?')}): {c} types")

        print(f"\n  TERM concentration in A-only frames:")
        for t, c in a_only_terms.most_common():
            gloss = ATOM_GLOSS.get(t, '?') if t != '_' else 'NONE'
            print(f"    {t} ({gloss}): {c} types")

    # Prepare results
    results_a = {
        'vocabulary_partition': {
            'a_exclusive': len(a_exclusive),
            'b_exclusive': len(b_exclusive),
            'shared': len(shared),
        },
        'a_excl_stats': a_excl_stats,
        'b_stats': b_stats,
        'frame_exclusivity': {
            'a_only_frames': len(a_only_frames),
            'b_only_frames': len(b_only_frames),
            'shared_frames': len(shared_frames),
        },
        'a_only_frames': {
            frame: {
                'types': a_excl_frames[frame],
                'tokens': a_excl_tokens[frame],
                'examples': a_excl_ex[frame][:5],
                'head_gloss': ATOM_GLOSS.get(frame.split('x')[0], '?'),
                'term_gloss': ATOM_GLOSS.get(frame.split('x')[1], '?') if frame.split('x')[1] != '_' else 'NONE',
            }
            for frame in sorted(a_only_frames)
        },
        'b_only_frames': {
            frame: {
                'types': b_frames[frame],
                'tokens': b_tokens[frame],
                'examples': b_ex[frame][:5],
                'head_gloss': ATOM_GLOSS.get(frame.split('x')[0], '?'),
                'term_gloss': ATOM_GLOSS.get(frame.split('x')[1], '?') if frame.split('x')[1] != '_' else 'NONE',
            }
            for frame in sorted(b_only_frames)
        },
        'shared_frame_comparison': shared_comparison,
    }

    return results_a


# --- TEST B: TERMINAL Distribution Comparison ---------------------

def test_b_terminals(a_middles, b_middles):
    """Compare TERMINAL atom distributions between A and B."""
    print("\n" + "=" * 80)
    print("TEST B: TERMINAL Atom Distribution Comparison (A vs B)")
    print("=" * 80)

    a_types = set(a_middles.keys())
    b_types = set(b_middles.keys())
    a_exclusive = a_types - b_types
    b_exclusive = b_types - a_types
    shared = a_types & b_types

    def get_terminal_dist(middle_set, counts, weighted=False):
        """Get TERMINAL atom distribution for a set of MIDDLEs.

        If weighted=True, weight by token count. Otherwise count by type.
        """
        term_counter = Counter()
        total = 0
        for mid in middle_set:
            if len(mid) < 2:
                continue
            head, mods, term = decompose(mid)
            if head is None:
                continue  # Skip headless
            if term is None:
                term_label = '_NONE_'
            elif term == 'dy':
                term_label = 'dy'
            else:
                term_label = term[0]  # Normalize extensible

            w = counts.get(mid, 1) if weighted else 1
            term_counter[term_label] += w
            total += w

        return term_counter, total

    # Type-level distributions
    a_all_terms, a_all_total = get_terminal_dist(a_types, a_middles, weighted=False)
    b_all_terms, b_all_total = get_terminal_dist(b_types, b_middles, weighted=False)

    a_excl_terms, a_excl_total = get_terminal_dist(a_exclusive, a_middles, weighted=False)
    b_excl_terms, b_excl_total = get_terminal_dist(b_exclusive, b_middles, weighted=False)
    shared_terms, shared_total = get_terminal_dist(shared, a_middles, weighted=False)

    # Token-weighted distributions
    a_all_terms_w, a_all_total_w = get_terminal_dist(a_types, a_middles, weighted=True)
    b_all_terms_w, b_all_total_w = get_terminal_dist(b_types, b_middles, weighted=True)
    a_excl_terms_w, a_excl_total_w = get_terminal_dist(a_exclusive, a_middles, weighted=True)
    b_excl_terms_w, b_excl_total_w = get_terminal_dist(b_exclusive, b_middles, weighted=True)

    # All terminal atoms found
    all_terms = sorted(set(list(a_all_terms.keys()) + list(b_all_terms.keys())),
                       key=lambda x: (x == '_NONE_', x))

    print(f"\n--- TYPE-level TERMINAL Distribution ---")
    print(f"  {'TERM':<8s} {'A-all':>8s} {'A%':>7s} {'B-all':>8s} {'B%':>7s} {'A/B ratio':>10s} {'A-excl':>8s} {'B-excl':>8s} {'Gloss':<16s} {'Category Bias'}")
    print(f"  {'-'*120}")

    enrichment_data = []
    for t in all_terms:
        a_n = a_all_terms.get(t, 0)
        b_n = b_all_terms.get(t, 0)
        a_pct = 100.0 * a_n / a_all_total if a_all_total > 0 else 0
        b_pct = 100.0 * b_n / b_all_total if b_all_total > 0 else 0
        ratio = a_pct / b_pct if b_pct > 0 else float('inf')
        a_e = a_excl_terms.get(t, 0)
        b_e = b_excl_terms.get(t, 0)
        gloss = ATOM_GLOSS.get(t, '?') if t != '_NONE_' else 'none'
        cat_bias = TERM_CATEGORY_BIAS.get(t, '?')

        print(f"  {t:<8s} {a_n:>8d} {a_pct:>6.1f}% {b_n:>8d} {b_pct:>6.1f}% {ratio:>10.3f} {a_e:>8d} {b_e:>8d} {gloss:<16s} {cat_bias}")

        enrichment_data.append({
            'terminal': t,
            'a_all_types': a_n,
            'a_pct': round(a_pct, 2),
            'b_all_types': b_n,
            'b_pct': round(b_pct, 2),
            'ratio_a_over_b': round(ratio, 3) if ratio != float('inf') else 'inf',
            'a_exclusive_types': a_e,
            'b_exclusive_types': b_e,
            'gloss': gloss,
            'category_bias': cat_bias,
        })

    print(f"\n  Totals: A={a_all_total} compound types, B={b_all_total} compound types")

    # Token-weighted version
    print(f"\n--- TOKEN-weighted TERMINAL Distribution ---")
    print(f"  {'TERM':<8s} {'A tokens':>10s} {'A%':>7s} {'B tokens':>10s} {'B%':>7s} {'A/B ratio':>10s}")
    print(f"  {'-'*60}")

    token_enrichment = []
    for t in all_terms:
        a_n = a_all_terms_w.get(t, 0)
        b_n = b_all_terms_w.get(t, 0)
        a_pct = 100.0 * a_n / a_all_total_w if a_all_total_w > 0 else 0
        b_pct = 100.0 * b_n / b_all_total_w if b_all_total_w > 0 else 0
        ratio = a_pct / b_pct if b_pct > 0 else float('inf')
        print(f"  {t:<8s} {a_n:>10d} {a_pct:>6.1f}% {b_n:>10d} {b_pct:>6.1f}% {ratio:>10.3f}")
        token_enrichment.append({
            'terminal': t,
            'a_tokens': a_n,
            'a_pct': round(a_pct, 2),
            'b_tokens': b_n,
            'b_pct': round(b_pct, 2),
            'ratio': round(ratio, 3) if ratio != float('inf') else 'inf',
        })

    # Chi-squared test (type-level, A-all vs B-all)
    # Build aligned arrays
    common_terms = sorted(set(list(a_all_terms.keys()) + list(b_all_terms.keys())))
    a_vec = [a_all_terms.get(t, 0) for t in common_terms]
    b_vec = [b_all_terms.get(t, 0) for t in common_terms]

    # Chi-squared on contingency table
    import numpy as np
    observed = np.array([a_vec, b_vec])
    # Filter out columns with zero totals
    col_sums = observed.sum(axis=0)
    mask = col_sums > 0
    observed = observed[:, mask]
    filtered_terms = [t for t, m in zip(common_terms, mask.tolist()) if m]

    chi2, p_val, dof, expected = stats.chi2_contingency(observed)
    n_total = observed.sum()
    k = min(observed.shape)
    cramers_v = (chi2 / (n_total * (k - 1))) ** 0.5 if n_total > 0 else 0

    print(f"\n--- Chi-squared Test (type-level, A-all vs B-all) ---")
    print(f"  chi2 = {chi2:.2f}, dof = {dof}, p = {p_val:.2e}")
    print(f"  Cramer's V = {cramers_v:.4f}")
    print(f"  N = {n_total} (compound MIDDLE types)")

    # Repeat for A-exclusive vs B-exclusive
    ae_vec = [a_excl_terms.get(t, 0) for t in common_terms]
    be_vec = [b_excl_terms.get(t, 0) for t in common_terms]
    observed2 = np.array([ae_vec, be_vec])
    col_sums2 = observed2.sum(axis=0)
    mask2 = col_sums2 > 0
    observed2 = observed2[:, mask2]

    if observed2.shape[1] > 1 and all(observed2.sum(axis=1) > 0):
        chi2_e, p_val_e, dof_e, expected_e = stats.chi2_contingency(observed2)
        n_e = observed2.sum()
        cramers_v_e = (chi2_e / (n_e * (min(observed2.shape) - 1))) ** 0.5 if n_e > 0 else 0
        print(f"\n--- Chi-squared Test (A-exclusive vs B-exclusive) ---")
        print(f"  chi2 = {chi2_e:.2f}, dof = {dof_e}, p = {p_val_e:.2e}")
        print(f"  Cramer's V = {cramers_v_e:.4f}")
        print(f"  N = {n_e}")
    else:
        chi2_e, p_val_e, cramers_v_e = None, None, None
        print(f"\n--- Chi-squared Test (A-exclusive vs B-exclusive): insufficient data ---")

    # Interpretation
    print(f"\n--- INTERPRETATION ---")

    # Find most A-enriched and B-enriched terminals
    a_enriched = [(d['terminal'], d['ratio_a_over_b'], d['gloss'], d['category_bias'])
                  for d in enrichment_data
                  if isinstance(d['ratio_a_over_b'], (int, float)) and d['ratio_a_over_b'] > 1.2
                  and d['a_all_types'] >= 5]
    b_enriched = [(d['terminal'], d['ratio_a_over_b'], d['gloss'], d['category_bias'])
                  for d in enrichment_data
                  if isinstance(d['ratio_a_over_b'], (int, float)) and d['ratio_a_over_b'] < 0.8
                  and d['b_all_types'] >= 5]

    a_enriched.sort(key=lambda x: -x[1])
    b_enriched.sort(key=lambda x: x[1])

    print(f"\n  A-enriched TERMINALs (ratio > 1.2x, >= 5 types):")
    for t, r, g, cat in a_enriched:
        print(f"    {t:<8s} {r:.2f}x  ({g})  B category: {cat}")

    print(f"\n  B-enriched TERMINALs (ratio < 0.8x, >= 5 types):")
    for t, r, g, cat in b_enriched:
        print(f"    {t:<8s} {r:.2f}x  ({g})  B category: {cat}")

    # Test the specific prediction: A uses more l (state), less r (respond)
    a_l = a_all_terms.get('l', 0) / a_all_total * 100 if a_all_total > 0 else 0
    b_l = b_all_terms.get('l', 0) / b_all_total * 100 if b_all_total > 0 else 0
    a_r = a_all_terms.get('r', 0) / a_all_total * 100 if a_all_total > 0 else 0
    b_r = b_all_terms.get('r', 0) / b_all_total * 100 if b_all_total > 0 else 0

    print(f"\n  Prediction: A uses more l (state), less r (respond)")
    print(f"    l: A={a_l:.1f}% vs B={b_l:.1f}% -> {'CONFIRMED' if a_l > b_l else 'NOT CONFIRMED'} (ratio {a_l/b_l:.2f}x)" if b_l > 0 else f"    l: A={a_l:.1f}%, B=0%")
    print(f"    r: A={a_r:.1f}% vs B={b_r:.1f}% -> {'CONFIRMED' if a_r < b_r else 'NOT CONFIRMED'} (ratio {a_r/b_r:.2f}x)" if b_r > 0 else f"    r: A={a_r:.1f}%, B=0%")

    results_b = {
        'type_level': {
            'a_all_total': a_all_total,
            'b_all_total': b_all_total,
            'enrichment': enrichment_data,
        },
        'token_level': {
            'a_all_total': a_all_total_w,
            'b_all_total': b_all_total_w,
            'enrichment': token_enrichment,
        },
        'chi_squared_all': {
            'chi2': round(chi2, 2),
            'p': p_val,
            'dof': dof,
            'cramers_v': round(cramers_v, 4),
            'n': int(n_total),
        },
        'chi_squared_exclusive': {
            'chi2': round(chi2_e, 2) if chi2_e else None,
            'p': p_val_e if p_val_e else None,
            'cramers_v': round(cramers_v_e, 4) if cramers_v_e else None,
        },
        'a_enriched_terminals': [
            {'terminal': t, 'ratio': r, 'gloss': g, 'category_bias': cat}
            for t, r, g, cat in a_enriched
        ],
        'b_enriched_terminals': [
            {'terminal': t, 'ratio': r, 'gloss': g, 'category_bias': cat}
            for t, r, g, cat in b_enriched
        ],
        'l_r_prediction': {
            'l_a_pct': round(a_l, 2),
            'l_b_pct': round(b_l, 2),
            'l_confirmed': a_l > b_l,
            'r_a_pct': round(a_r, 2),
            'r_b_pct': round(b_r, 2),
            'r_confirmed': a_r < b_r,
        },
    }

    return results_b


# --- Main ---------------------------------------------------------

def main():
    print("Loading transcript data...")
    a_middles, b_middles = load_all_middles()
    print(f"  A: {len(a_middles)} types, {sum(a_middles.values())} tokens")
    print(f"  B: {len(b_middles)} types, {sum(b_middles.values())} tokens")

    results_a = test_a_frames(a_middles, b_middles)
    results_b = test_b_terminals(a_middles, b_middles)

    # Save combined results
    results = {
        'test_a_frames': results_a,
        'test_b_terminals': results_b,
    }

    out_path = RESULTS_DIR / 'a_exclusive_frames_and_terminals.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {out_path}")


if __name__ == '__main__':
    main()

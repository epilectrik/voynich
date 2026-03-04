"""
Phase 506 Test 3: Modifier Ordering Semantics
==============================================

C1394 found modifiers follow a fixed stacking order:
  p(0.22) -> f(0.40) -> i(0.52) -> c(0.53) -> d(0.70) -> s(0.71)

This script tests whether the ordering has semantic content:
  1. Order Violation Consequences - do reversed pairs change category?
  2. Order vs Category Correlation - does stack position correlate with effect size?
  3. Progressive Category Shift - does each modifier incrementally shift category?
  4. Modifier Ordering as Pipeline - GATE->LOOP->TUNE->SEAL stage model
  5. Suffix Mode Correlation - do early/late modifiers cluster with suffix modes?
"""

import sys
import os
import io
import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ---------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1209 / C1210 / C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}
TERM_SET = TERM_ONLY | FREE

# Canonical modifier order from C1394
CANONICAL_ORDER = {'p': 0.22, 'f': 0.40, 'i': 0.52, 'c': 0.53, 'd': 0.70, 's': 0.71}
CANONICAL_RANK = {m: i for i, m in enumerate(['p', 'f', 'i', 'c', 'd', 's'])}

# Atom glosses from C1195
ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}

# Modifier category-shift V values from C1394 T6
MOD_V = {'d': 0.657, 'c': 0.505, 'i': 0.418, 'p': 0.368, 'f': 0.351, 's': 0.245}

# Pipeline stage mapping
PIPELINE_STAGE = {
    'p': 'GATE', 'f': 'GATE',
    'i': 'LOOP',
    'c': 'TUNE',
    'd': 'SEAL', 's': 'SEAL',
}

ALL_CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
                  'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']


# --- Atom decomposition (from Phase 505) ----------------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms, respecting extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
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
    """Decompose a MIDDLE into HEAD, MOD_STACK, TERM."""
    atoms = atomize(middle)
    if len(atoms) == 0:
        return None, [], None
    if len(atoms) == 1:
        return atoms[0], [], None

    head = None
    head_base = atoms[0][0]
    if head_base in HEAD_SET or head_base in FREE:
        head = atoms[0]
    else:
        return None, atoms, None

    term = None
    term_base = atoms[-1][0]
    if len(atoms) >= 2:
        if term_base in TERM_SET:
            term = atoms[-1]
        elif term_base in MOD_ONLY:
            term = None

    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def get_mod_bases(mods):
    """Extract base characters from modifier atoms list."""
    return [m[0] for m in mods]


# --- Data Loading ----------------------------------------------

def load_data():
    """Load Currier B MIDDLEs with frequencies, categories, and line-level context."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Token-level data with line context
    middles = Counter()
    middle_line_data = defaultdict(list)  # middle -> list of (folio, line, prefix, suffix)

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle:
            middles[m.middle] += 1
            middle_line_data[m.middle].append({
                'folio': tok.folio,
                'line': tok.line,
                'prefix': m.prefix,
                'suffix': m.suffix,
            })

    categories = {}
    for mid in middles:
        categories[mid] = cc.classify(mid) or 'UNKNOWN'

    # Pre-compute all decompositions
    decompositions = {}
    for mid in middles:
        if len(mid) >= 2:
            decompositions[mid] = decompose(mid)

    return middles, categories, decompositions, middle_line_data


# --- Test 1: Order Violation Consequences ----------------------

def test1_order_violations(middles, categories, decompositions):
    """When canonical order is violated, does the category change?"""
    print("=" * 80)
    print("TEST 1: Order Violation Consequences")
    print("=" * 80)
    print("Question: When modifier order is reversed, does the category change?")

    # Collect modifier pairs from all multi-mod compounds
    # For each (A,B) pair where A appears before B, record category
    pair_order_cats = defaultdict(lambda: {'canonical': Counter(), 'reversed': Counter()})

    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 2:
            continue

        mod_bases = get_mod_bases(mods)
        cat = categories.get(mid, 'UNKNOWN')

        # Check all adjacent modifier pairs
        for i in range(len(mod_bases) - 1):
            a, b = mod_bases[i], mod_bases[i + 1]
            if a not in CANONICAL_RANK or b not in CANONICAL_RANK:
                continue
            if a == b:
                continue

            pair_key = tuple(sorted([a, b]))
            if CANONICAL_RANK[a] < CANONICAL_RANK[b]:
                pair_order_cats[pair_key]['canonical'][cat] += count
            else:
                pair_order_cats[pair_key]['reversed'][cat] += count

    # Also check non-adjacent pairs for same-set different-order
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 2:
            continue

        mod_bases = get_mod_bases(mods)
        cat = categories.get(mid, 'UNKNOWN')

        # All pairs (not just adjacent)
        mods_in_canon = [m for m in mod_bases if m in CANONICAL_RANK]
        for i in range(len(mods_in_canon)):
            for j in range(i + 1, len(mods_in_canon)):
                a, b = mods_in_canon[i], mods_in_canon[j]
                if a == b:
                    continue
                pair_key = tuple(sorted([a, b]))
                if CANONICAL_RANK[a] < CANONICAL_RANK[b]:
                    # Already counted via adjacent, skip double-count
                    pass

    print(f"\n  Modifier pairs with BOTH canonical and reversed orderings:")
    print(f"  {'Pair':>8} {'Canon.N':>8} {'Rev.N':>8} {'Canon.Dom':>14} {'Rev.Dom':>14} {'Same?':>6} {'Chi2':>8} {'p':>10}")

    results = {}
    pairs_with_both = 0
    pairs_same_cat = 0
    pairs_diff_cat = 0

    for pair_key in sorted(pair_order_cats.keys()):
        data = pair_order_cats[pair_key]
        can_total = sum(data['canonical'].values())
        rev_total = sum(data['reversed'].values())

        if can_total == 0 or rev_total == 0:
            continue

        pairs_with_both += 1

        can_dom = data['canonical'].most_common(1)[0][0] if data['canonical'] else '-'
        rev_dom = data['reversed'].most_common(1)[0][0] if data['reversed'] else '-'
        same = 'YES' if can_dom == rev_dom else 'NO'

        if can_dom == rev_dom:
            pairs_same_cat += 1
        else:
            pairs_diff_cat += 1

        # Chi-squared if enough data
        all_cats = sorted(set(list(data['canonical'].keys()) + list(data['reversed'].keys())))
        if len(all_cats) >= 2 and can_total >= 5 and rev_total >= 5:
            contingency = [
                [data['canonical'].get(c, 0) for c in all_cats],
                [data['reversed'].get(c, 0) for c in all_cats]
            ]
            try:
                chi2, p, dof, exp = stats.chi2_contingency(contingency)
            except ValueError:
                chi2, p = 0, 1.0
        else:
            chi2, p = 0, 1.0

        pair_str = f"{pair_key[0]},{pair_key[1]}"
        sig = '*' if p < 0.05 else ''
        print(f"  {pair_str:>8} {can_total:>8} {rev_total:>8} {can_dom:>14} {rev_dom:>14} {same:>6} {chi2:>8.1f} {p:>10.4f} {sig}")

        results[pair_str] = {
            'canonical_n': can_total, 'reversed_n': rev_total,
            'canonical_dominant': can_dom, 'reversed_dominant': rev_dom,
            'same_dominant': can_dom == rev_dom,
            'chi2': round(chi2, 1), 'p': p,
        }

    print(f"\n  Summary: {pairs_with_both} pairs appear in both orderings")
    print(f"    Same dominant category: {pairs_same_cat} ({100*pairs_same_cat/max(1,pairs_with_both):.0f}%)")
    print(f"    Different dominant category: {pairs_diff_cat} ({100*pairs_diff_cat/max(1,pairs_with_both):.0f}%)")

    if pairs_with_both > 0:
        verdict = "ORDER_MATTERS" if pairs_diff_cat > pairs_same_cat else "ORDER_CONVENTION"
        print(f"  Verdict: {verdict}")
    else:
        verdict = "INSUFFICIENT_DATA"
        print(f"  Verdict: {verdict} (no pairs appear in both orderings)")

    return {
        'pairs_with_both': pairs_with_both,
        'same_category': pairs_same_cat,
        'different_category': pairs_diff_cat,
        'verdict': verdict,
        'pairs': results,
    }


# --- Test 2: Order vs Category Correlation --------------------

def test2_order_effect_correlation(middles, categories, decompositions):
    """Correlate modifier stack position with category-shifting effect size."""
    print("\n" + "=" * 80)
    print("TEST 2: Order vs Category Effect Correlation")
    print("=" * 80)
    print("Question: Does position in the stack correlate with effect magnitude?")

    # Canonical positions from C1394
    positions = np.array([CANONICAL_ORDER[m] for m in ['p', 'f', 'i', 'c', 'd', 's']])
    effects = np.array([MOD_V[m] for m in ['p', 'f', 'i', 'c', 'd', 's']])

    rho, p_rho = stats.spearmanr(positions, effects)
    r_pearson, p_pearson = stats.pearsonr(positions, effects)

    print(f"\n  Canonical position vs Cramer's V (category-shifting effect):")
    print(f"  {'Mod':>4} {'Pos':>6} {'V':>6} {'Gloss':>10}")
    for m in ['p', 'f', 'i', 'c', 'd', 's']:
        print(f"  {m:>4} {CANONICAL_ORDER[m]:>6.2f} {MOD_V[m]:>6.3f} {ATOM_GLOSS[m]:>10}")

    print(f"\n  Spearman rho = {rho:+.3f}, p = {p_rho:.4f}")
    print(f"  Pearson  r   = {r_pearson:+.3f}, p = {p_pearson:.4f}")

    if rho > 0:
        interp = "Later modifiers have STRONGER category effects (inner = more impact)"
    else:
        interp = "Earlier modifiers have STRONGER category effects (outer = more impact)"

    print(f"\n  Direction: {interp}")

    # Compute observed mean position within multi-mod compounds
    mod_positions_observed = defaultdict(list)  # mod_char -> list of positions in stack

    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 2:
            continue

        mod_bases = get_mod_bases(mods)
        n_mods = len(mod_bases)

        for idx, mb in enumerate(mod_bases):
            if mb in MOD_ONLY:
                # Normalized position (0 = first modifier, 1 = last modifier)
                norm_pos = idx / (n_mods - 1) if n_mods > 1 else 0.5
                for _ in range(count):
                    mod_positions_observed[mb].append(norm_pos)

    print(f"\n  Observed mean position in multi-modifier stacks:")
    print(f"  {'Mod':>4} {'Canonical':>10} {'Observed':>10} {'N':>6} {'Gloss':>10}")

    obs_positions = {}
    for m in ['p', 'f', 'i', 'c', 'd', 's']:
        positions_list = mod_positions_observed.get(m, [])
        if positions_list:
            mean_pos = np.mean(positions_list)
            print(f"  {m:>4} {CANONICAL_ORDER[m]:>10.3f} {mean_pos:>10.3f} {len(positions_list):>6} {ATOM_GLOSS[m]:>10}")
            obs_positions[m] = mean_pos
        else:
            print(f"  {m:>4} {CANONICAL_ORDER[m]:>10.3f} {'(none)':>10} {0:>6} {ATOM_GLOSS[m]:>10}")

    # Correlate observed position with effect size
    if len(obs_positions) >= 4:
        obs_mods = sorted(obs_positions.keys())
        obs_pos_arr = np.array([obs_positions[m] for m in obs_mods])
        obs_eff_arr = np.array([MOD_V[m] for m in obs_mods])
        rho_obs, p_obs = stats.spearmanr(obs_pos_arr, obs_eff_arr)
        print(f"\n  Observed position vs V: Spearman rho = {rho_obs:+.3f}, p = {p_obs:.4f}")

    return {
        'canonical_spearman': round(float(rho), 3),
        'canonical_p': float(p_rho),
        'canonical_pearson': round(float(r_pearson), 3),
        'direction': 'later_stronger' if rho > 0 else 'earlier_stronger',
        'observed_positions': {m: round(v, 3) for m, v in obs_positions.items()},
    }


# --- Test 3: Progressive Category Shift -----------------------

def test3_progressive_shift(middles, categories, decompositions):
    """Trace category as modifiers are added one by one."""
    print("\n" + "=" * 80)
    print("TEST 3: Progressive Category Shift")
    print("=" * 80)
    print("Question: Does each modifier progressively shift the category?")

    cc = CategoryClassifier()

    # For compounds with 2+ modifiers, build the stripping chain:
    # full compound -> remove last mod -> remove next mod -> ... -> bare frame
    # Then check category at each stage

    shift_records = []
    stage_dominance = Counter()  # which modifier position dominates

    for mid, count in middles.items():
        if len(mid) < 2 or count < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 2:
            continue

        mod_bases = get_mod_bases(mods)
        full_cat = categories.get(mid, 'UNKNOWN')

        # Build the chain from innermost to outermost removal
        # Start with full compound, remove modifiers from left (outermost first)
        chain = []
        chain.append(('full', mid, full_cat, mod_bases[:]))

        # Also classify the bare frame (head + term only)
        if term:
            bare = head + term
        else:
            bare = head
        bare_cat = cc.classify(bare) or 'UNKNOWN'
        chain.append(('bare', bare, bare_cat, []))

        # Intermediate steps: add modifiers one by one to bare frame
        intermediates = []
        for i in range(len(mods)):
            # Build compound with just first i+1 modifiers
            partial_mid = head + ''.join(mods[:i+1]) + (term if term else '')
            partial_cat = cc.classify(partial_mid) or 'UNKNOWN'
            intermediates.append((f'mod_{i+1}', partial_mid, partial_cat, mod_bases[:i+1]))

        # Find which modifier addition first changes the category
        prev_cat = bare_cat
        decisive_mod = None
        for i, (label, pmid, pcat, pmods) in enumerate(intermediates):
            if pcat != prev_cat and decisive_mod is None:
                decisive_mod = i  # 0-indexed modifier position
            prev_cat = pcat

        if decisive_mod is not None:
            stage_dominance[decisive_mod] += count

        shift_records.append({
            'middle': mid,
            'freq': count,
            'n_mods': len(mods),
            'bare_cat': bare_cat,
            'full_cat': full_cat,
            'changed': bare_cat != full_cat,
            'decisive_mod_position': decisive_mod,
            'chain': [(t[0], t[1], t[2]) for t in
                      [('bare', bare, bare_cat)] + [(l, m, c) for l, m, c, _ in intermediates] + [('full', mid, full_cat)]]
        })

    # Analysis
    changed = [r for r in shift_records if r['changed']]
    unchanged = [r for r in shift_records if not r['changed']]

    print(f"\n  Compounds with 2+ modifiers: {len(shift_records)}")
    print(f"  Category changes from bare to full: {len(changed)} ({100*len(changed)/max(1,len(shift_records)):.1f}%)")
    print(f"  Category preserved: {len(unchanged)} ({100*len(unchanged)/max(1,len(shift_records)):.1f}%)")

    # Which modifier position is decisive?
    print(f"\n  Decisive modifier position (first modifier that changes category):")
    total_decisive = sum(stage_dominance.values())
    for pos in sorted(stage_dominance.keys()):
        cnt = stage_dominance[pos]
        pct = 100 * cnt / total_decisive if total_decisive > 0 else 0
        label = f"mod_{pos+1}" if pos < 6 else f"mod_{pos+1}"
        print(f"    Position {pos+1} ({label}): {cnt} tokens ({pct:.1f}%)")

    # Show example chains
    print(f"\n  Example progressive chains (top by freq):")
    for rec in sorted(changed, key=lambda x: -x['freq'])[:10]:
        chain_str = ' -> '.join(f"{label}:{cat}" for label, mid_str, cat in rec['chain'])
        print(f"    {rec['middle']:>12} (n={rec['freq']:>3}): {chain_str}")

    # Does first modifier or last modifier dominate?
    first_mod_decisive = stage_dominance.get(0, 0)
    last_positions = [r['n_mods'] - 1 for r in changed if r['decisive_mod_position'] is not None]
    last_mod_decisive = sum(1 for r in changed
                           if r['decisive_mod_position'] == r['n_mods'] - 1)

    print(f"\n  First modifier decisive: {first_mod_decisive} tokens")
    print(f"  Last modifier decisive: {last_mod_decisive} compounds")

    if total_decisive > 0:
        # Mean position of decisive modifier
        weighted_pos = sum(pos * cnt for pos, cnt in stage_dominance.items()) / total_decisive
        print(f"  Token-weighted mean decisive position: {weighted_pos:.2f}")
        verdict = "FIRST_DOMINATES" if weighted_pos < 0.5 else "LAST_DOMINATES"
        print(f"  Verdict: {verdict}")
    else:
        weighted_pos = None
        verdict = "NO_SHIFTS"

    return {
        'total_compounds': len(shift_records),
        'changed_count': len(changed),
        'unchanged_count': len(unchanged),
        'stage_dominance': dict(stage_dominance),
        'mean_decisive_position': round(float(weighted_pos), 3) if weighted_pos is not None else None,
        'verdict': verdict,
    }


# --- Test 4: Modifier Ordering as Pipeline --------------------

def test4_pipeline_stages(middles, categories, decompositions):
    """Test the GATE->LOOP->TUNE->SEAL pipeline model."""
    print("\n" + "=" * 80)
    print("TEST 4: Modifier Ordering as Pipeline")
    print("=" * 80)
    print("Pipeline stages: GATE(p,f) -> LOOP(i) -> TUNE(c) -> SEAL(d,s)")

    # Classify each multi-modifier compound by its stage span
    single_stage = Counter()   # compounds using modifiers from one stage only
    multi_stage = Counter()    # compounds spanning multiple stages
    stage_combo_cats = defaultdict(Counter)  # stage combo -> category distribution

    stage_span_data = []

    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 1:
            continue

        mod_bases = get_mod_bases(mods)
        stages_used = set()
        for mb in mod_bases:
            if mb in PIPELINE_STAGE:
                stages_used.add(PIPELINE_STAGE[mb])

        if not stages_used:
            continue

        cat = categories.get(mid, 'UNKNOWN')
        stage_combo = tuple(sorted(stages_used))
        stage_combo_cats[stage_combo][cat] += count

        if len(stages_used) == 1:
            single_stage[list(stages_used)[0]] += count
        else:
            multi_stage[stage_combo] += count

        stage_span_data.append({
            'middle': mid, 'freq': count, 'cat': cat,
            'stages': stage_combo, 'n_stages': len(stages_used),
        })

    # Results
    print(f"\n  Single-stage compounds (one pipeline stage):")
    for stage, cnt in single_stage.most_common():
        cats = stage_combo_cats[(stage,)]
        dom = cats.most_common(1)[0] if cats else ('-', 0)
        print(f"    {stage:>6}: {cnt:>5} tokens, dominant = {dom[0]} ({100*dom[1]/cnt:.0f}%)")

    print(f"\n  Multi-stage compounds (spanning 2+ stages):")
    for combo, cnt in sorted(multi_stage.items(), key=lambda x: -x[1])[:15]:
        cats = stage_combo_cats[combo]
        dom = cats.most_common(1)[0] if cats else ('-', 0)
        combo_str = '+'.join(combo)
        print(f"    {combo_str:>20}: {cnt:>5} tokens, dominant = {dom[0]} ({100*dom[1]/cnt:.0f}%)")

    # Compare single-stage vs multi-stage category distributions
    single_cats = Counter()
    multi_cats = Counter()
    for rec in stage_span_data:
        if rec['n_stages'] == 1:
            single_cats[rec['cat']] += rec['freq']
        else:
            multi_cats[rec['cat']] += rec['freq']

    single_total = sum(single_cats.values())
    multi_total = sum(multi_cats.values())

    print(f"\n  Category comparison: single-stage vs multi-stage:")
    print(f"  {'Category':>15} {'Single%':>8} {'Multi%':>8} {'Delta':>8}")

    all_cats = sorted(set(list(single_cats.keys()) + list(multi_cats.keys())))
    for cat in all_cats:
        sp = 100 * single_cats.get(cat, 0) / max(1, single_total)
        mp = 100 * multi_cats.get(cat, 0) / max(1, multi_total)
        print(f"  {cat:>15} {sp:>7.1f}% {mp:>7.1f}% {mp-sp:>+7.1f}%")

    # Chi-squared test
    if single_total > 0 and multi_total > 0:
        contingency = [
            [single_cats.get(c, 0) for c in all_cats],
            [multi_cats.get(c, 0) for c in all_cats]
        ]
        chi2, p, dof, exp = stats.chi2_contingency(contingency)
        n = single_total + multi_total
        v = (chi2 / (n * (min(2, len(all_cats)) - 1))) ** 0.5 if n > 0 else 0
        print(f"\n  Chi2 = {chi2:.1f}, p = {p:.2e}, V = {v:.3f}")
    else:
        chi2, p, v = 0, 1, 0

    # Test whether spanning more stages predicts category more strongly
    print(f"\n  Stage span vs category:")
    for n_stages in sorted(set(r['n_stages'] for r in stage_span_data)):
        subset = [r for r in stage_span_data if r['n_stages'] == n_stages]
        cat_dist = Counter()
        for r in subset:
            cat_dist[r['cat']] += r['freq']
        total = sum(cat_dist.values())
        dom = cat_dist.most_common(1)[0]
        n_types = len(subset)
        print(f"    {n_stages} stage(s): {total:>5} tokens, {n_types:>3} types, "
              f"dominant = {dom[0]} ({100*dom[1]/total:.0f}%)")

    return {
        'single_stage_totals': dict(single_stage),
        'multi_stage_count': multi_total,
        'single_stage_count': single_total,
        'chi2': round(chi2, 1),
        'p': p,
        'cramers_v': round(v, 3),
    }


# --- Test 5: Suffix Mode Correlation --------------------------

def test5_suffix_mode(middles, categories, decompositions, middle_line_data):
    """Do early/late modifiers cluster with different suffix modes?"""
    print("\n" + "=" * 80)
    print("TEST 5: Suffix Mode Correlation")
    print("=" * 80)
    print("Question: Do lines with early-order modifiers cluster in one suffix mode?")

    morph = Morphology()

    # Classify MIDDLEs by their modifier content
    early_mods = {'p', 'f'}    # GATE stage
    late_mods = {'d', 's'}     # SEAL stage
    mid_mods = {'i', 'c'}      # LOOP/TUNE stage

    # For each MIDDLE with modifiers, determine its modifier profile
    middle_mod_class = {}  # middle -> 'EARLY', 'LATE', 'MID', 'MIXED'
    for mid in middles:
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 1:
            continue

        mod_bases = set(get_mod_bases(mods)) & MOD_ONLY
        if not mod_bases:
            continue

        has_early = bool(mod_bases & early_mods)
        has_late = bool(mod_bases & late_mods)
        has_mid_mod = bool(mod_bases & mid_mods)

        if has_early and not has_late and not has_mid_mod:
            middle_mod_class[mid] = 'EARLY_ONLY'
        elif has_late and not has_early and not has_mid_mod:
            middle_mod_class[mid] = 'LATE_ONLY'
        elif has_mid_mod and not has_early and not has_late:
            middle_mod_class[mid] = 'MID_ONLY'
        elif has_early and has_late:
            middle_mod_class[mid] = 'EARLY+LATE'
        else:
            middle_mod_class[mid] = 'MIXED'

    # Now classify suffixes
    # Suffix type classification: Terminal suffixes = Mode A leaning,
    # Bare/Connector = Mode B leaning (from C1229, C1236)
    terminal_suffixes = {'y', 'dy', 'ry', 'hy', 'ly', 'my', 'n', 'im', 'm',
                         'edy', 'ey', 'eey', 'eedy'}
    checkpoint_suffixes = {'aiin', 'ain', 'oiin', 'iin', 'in', 'aiiin'}

    # Count suffix types per modifier class
    mod_class_suffix = defaultdict(Counter)  # mod_class -> suffix_type counts

    for mid, mod_class in middle_mod_class.items():
        for usage in middle_line_data.get(mid, []):
            sfx = usage['suffix']
            if sfx in terminal_suffixes:
                stype = 'TERMINAL'
            elif sfx in checkpoint_suffixes:
                stype = 'CHECKPOINT'
            elif sfx is None or sfx == '':
                stype = 'BARE'
            else:
                stype = 'OTHER'
            mod_class_suffix[mod_class][stype] += 1

    # Display
    print(f"\n  MIDDLEs classified by modifier stage:")
    for mc in sorted(middle_mod_class.values()):
        pass
    mc_counts = Counter(middle_mod_class.values())
    for mc, cnt in mc_counts.most_common():
        print(f"    {mc:>12}: {cnt} MIDDLE types")

    print(f"\n  Suffix type distribution by modifier class:")
    print(f"  {'Mod Class':>12} {'TERMINAL':>10} {'CHECK':>10} {'BARE':>10} {'OTHER':>10} {'Total':>8} {'Term%':>7}")

    mod_class_results = {}
    for mc in sorted(mod_class_suffix.keys()):
        counts = mod_class_suffix[mc]
        total = sum(counts.values())
        term_pct = 100 * counts.get('TERMINAL', 0) / max(1, total)
        bare_pct = 100 * counts.get('BARE', 0) / max(1, total)
        print(f"  {mc:>12} {counts.get('TERMINAL',0):>10} {counts.get('CHECKPOINT',0):>10} "
              f"{counts.get('BARE',0):>10} {counts.get('OTHER',0):>10} {total:>8} {term_pct:>6.1f}%")
        mod_class_results[mc] = {
            'terminal_pct': round(term_pct, 1),
            'bare_pct': round(bare_pct, 1),
            'total': total,
        }

    # Chi-squared test: EARLY vs LATE modifier classes
    early_sfx = mod_class_suffix.get('EARLY_ONLY', Counter())
    late_sfx = mod_class_suffix.get('LATE_ONLY', Counter())

    stypes = ['TERMINAL', 'CHECKPOINT', 'BARE', 'OTHER']
    early_total = sum(early_sfx.values())
    late_total = sum(late_sfx.values())

    if early_total > 10 and late_total > 10:
        contingency = [
            [early_sfx.get(s, 0) for s in stypes],
            [late_sfx.get(s, 0) for s in stypes]
        ]
        # Remove columns with all zeros
        non_zero = [i for i in range(len(stypes))
                    if contingency[0][i] + contingency[1][i] > 0]
        if len(non_zero) >= 2:
            contingency_filtered = [[contingency[r][c] for c in non_zero] for r in range(2)]
            chi2, p, dof, exp = stats.chi2_contingency(contingency_filtered)
            n = early_total + late_total
            k = len(non_zero)
            v = (chi2 / (n * (min(2, k) - 1))) ** 0.5 if n > 0 else 0
            print(f"\n  EARLY vs LATE chi2 = {chi2:.1f}, p = {p:.4f}, V = {v:.3f}")
        else:
            chi2, p, v = 0, 1, 0
    else:
        chi2, p, v = 0, 1, 0
        print(f"\n  EARLY ({early_total}) or LATE ({late_total}) too few for chi2")

    # Suffix mode inference
    # Mode A = high terminal, Mode B = high bare (from C1229/C1236)
    print(f"\n  Suffix mode mapping:")
    print(f"    Mode A (specification): TERMINAL-heavy -> early-order modifiers?")
    print(f"    Mode B (continuation): BARE-heavy -> late-order modifiers?")

    for mc in ['EARLY_ONLY', 'LATE_ONLY', 'MID_ONLY']:
        sfx = mod_class_suffix.get(mc, Counter())
        total = sum(sfx.values())
        if total > 0:
            term = sfx.get('TERMINAL', 0)
            bare = sfx.get('BARE', 0)
            term_r = term / total
            bare_r = bare / total
            mode = 'A-leaning' if term_r > bare_r else 'B-leaning'
            print(f"    {mc:>12}: terminal={term_r:.1%} bare={bare_r:.1%} -> {mode}")

    return {
        'mod_class_counts': dict(mc_counts),
        'mod_class_suffix': mod_class_results,
        'early_vs_late_chi2': round(chi2, 1),
        'early_vs_late_p': p,
        'early_vs_late_v': round(v, 3),
    }


# --- Main -----------------------------------------------------

def main():
    print("Phase 506 Test 3: Modifier Ordering Semantics")
    print("=" * 80)
    print()

    middles, categories, decompositions, middle_line_data = load_data()
    print(f"Loaded {len(middles)} unique MIDDLEs, {sum(middles.values())} tokens")
    print()

    t1 = test1_order_violations(middles, categories, decompositions)
    t2 = test2_order_effect_correlation(middles, categories, decompositions)
    t3 = test3_progressive_shift(middles, categories, decompositions)
    t4 = test4_pipeline_stages(middles, categories, decompositions)
    t5 = test5_suffix_mode(middles, categories, decompositions, middle_line_data)

    # --- Synthesis ---
    print("\n" + "=" * 80)
    print("SYNTHESIS")
    print("=" * 80)

    print(f"\n  T1 Order violations: {t1['verdict']}")
    print(f"     {t1['pairs_with_both']} pairs with both orderings, "
          f"{t1['same_category']} same / {t1['different_category']} different")

    print(f"\n  T2 Position-effect correlation: rho={t2['canonical_spearman']:+.3f} (p={t2['canonical_p']:.4f})")
    print(f"     Direction: {t2['direction']}")

    print(f"\n  T3 Progressive shift: {t3['verdict']}")
    print(f"     {t3['changed_count']}/{t3['total_compounds']} compounds shift category")
    if t3['mean_decisive_position'] is not None:
        print(f"     Mean decisive position: {t3['mean_decisive_position']:.2f}")

    print(f"\n  T4 Pipeline stages: V={t4['cramers_v']:.3f} (single vs multi-stage)")
    print(f"     Single-stage: {t4['single_stage_count']} tokens, "
          f"Multi-stage: {t4['multi_stage_count']} tokens")

    print(f"\n  T5 Suffix mode: EARLY vs LATE V={t5['early_vs_late_v']:.3f} (p={t5['early_vs_late_p']:.4f})")

    # Overall verdict
    print(f"\n  {'='*60}")
    order_matters = (t1['verdict'] == 'ORDER_MATTERS')
    strong_corr = (abs(t2['canonical_spearman']) > 0.6 and t2['canonical_p'] < 0.05)
    pipeline_valid = (t4['cramers_v'] > 0.15)
    mode_coupling = (t5['early_vs_late_v'] > 0.1 and t5['early_vs_late_p'] < 0.05)

    evidence_for = sum([order_matters, strong_corr, pipeline_valid, mode_coupling])
    evidence_against = 4 - evidence_for

    print(f"\n  EVIDENCE FOR semantic ordering: {evidence_for}/4")
    print(f"  EVIDENCE AGAINST: {evidence_against}/4")

    if evidence_for >= 3:
        overall = "ORDERING_SEMANTIC"
        print(f"\n  OVERALL VERDICT: {overall}")
        print(f"  The modifier stacking order carries procedural meaning.")
    elif evidence_for >= 2:
        overall = "ORDERING_PARTIAL"
        print(f"\n  OVERALL VERDICT: {overall}")
        print(f"  The modifier order has SOME semantic content but is not purely procedural.")
    else:
        overall = "ORDERING_CONVENTIONAL"
        print(f"\n  OVERALL VERDICT: {overall}")
        print(f"  The modifier order is a grammatical convention, not a semantic pipeline.")

    # Save results
    json_results = {
        'test1_order_violations': t1,
        'test2_order_effect_correlation': t2,
        'test3_progressive_shift': {k: v for k, v in t3.items() if k != 'chain'},
        'test4_pipeline_stages': t4,
        'test5_suffix_mode': t5,
        'synthesis': {
            'order_matters': order_matters,
            'strong_correlation': strong_corr,
            'pipeline_valid': pipeline_valid,
            'mode_coupling': mode_coupling,
            'evidence_for': evidence_for,
            'evidence_against': evidence_against,
            'overall_verdict': overall,
        }
    }

    json_path = RESULTS_DIR / 'modifier_order_semantics.json'
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"\nJSON results saved to: {json_path}")


if __name__ == '__main__':
    main()

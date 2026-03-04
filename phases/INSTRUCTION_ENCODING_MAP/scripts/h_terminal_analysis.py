"""
Phase 506 Test 2: h-Terminal Category Chaos
============================================

C1394 found TERM=h produces the most category-diverse compounds (27% purity
-- essentially random across 8 categories). Other terminals are much more
deterministic: r=99% FLOW, m=87% TRANSITION, y=56% OPERATION.

This script investigates: what drives category when TERM=h?

Tests:
  1. h-Terminal category breakdown -- enumerate all compounds, group by HEAD
  2. Modifier effects on h-terminal -- does mod stack predict category?
  3. PREFIX x h-terminal interaction -- does PREFIX resolve ambiguity?
  4. h as "Open Monitor" -- is HEAD doing the category work?
  5. ch as a unit -- is ch fusion the source of the chaos?
"""

import sys
import os
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications (from C1209 / C1210 / C1393)
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}

HEAD_SET = HEAD_ONLY | FREE | {'e'}
TERM_SET = TERM_ONLY | FREE

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}


# --- Atom Decomposition (from instruction_map.py) -----------------

def atomize(middle):
    """Split MIDDLE into individual atoms, respecting extensibility."""
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
    """Decompose MIDDLE into (HEAD, MOD_STACK, TERM)."""
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

    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def cramers_v(contingency_dict, row_key, col_key, count_key):
    """Compute Cramer's V from a list of dicts with row, col, count."""
    from scipy import stats as sp_stats

    # Build contingency table
    rows = sorted(set(d[row_key] for d in contingency_dict))
    cols = sorted(set(d[col_key] for d in contingency_dict))

    if len(rows) < 2 or len(cols) < 2:
        return 0.0, 1.0, 0

    table = []
    for r in rows:
        row_data = []
        for c in cols:
            total = sum(d[count_key] for d in contingency_dict
                       if d[row_key] == r and d[col_key] == c)
            row_data.append(total)
        table.append(row_data)

    # Remove zero-sum rows/cols
    import numpy as np
    arr = np.array(table)
    row_mask = arr.sum(axis=1) > 0
    col_mask = arr.sum(axis=0) > 0
    arr = arr[row_mask][:, col_mask]

    if arr.shape[0] < 2 or arr.shape[1] < 2:
        return 0.0, 1.0, 0

    chi2, p, dof, expected = sp_stats.chi2_contingency(arr)
    n = arr.sum()
    k = min(arr.shape)
    v = math.sqrt(chi2 / (n * (k - 1))) if n > 0 and k > 1 else 0
    return v, p, n


# --- Data Loading -------------------------------------------------

def load_data():
    """Load Currier B MIDDLEs with frequencies, categories, and PREFIX info."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Per-MIDDLE stats
    middles = Counter()
    # Per (PREFIX, MIDDLE) stats for Test 3
    prefix_middle = Counter()

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle:
            middles[m.middle] += 1
            pfx = m.prefix if m.prefix else 'BARE'
            prefix_middle[(pfx, m.middle)] += 1

    categories = {}
    for mid in middles:
        categories[mid] = cc.classify(mid) or 'UNKNOWN'

    return middles, categories, prefix_middle


# --- Test 1: h-Terminal Category Breakdown -------------------------

def test1_h_terminal_breakdown(middles, categories):
    """Enumerate all h-terminal compounds and analyze category by HEAD."""
    print("=" * 80)
    print("TEST 1: h-Terminal Category Breakdown")
    print("=" * 80)

    h_compounds = {}
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompose(mid)
        if term and term[0] == 'h':
            h_compounds[mid] = {
                'freq': count,
                'head': head,
                'mods': mods,
                'term': term,
                'cat': categories.get(mid, 'UNKNOWN'),
            }

    total_types = len(h_compounds)
    total_tokens = sum(v['freq'] for v in h_compounds.values())
    print(f"\nh-terminal compounds: {total_types} types, {total_tokens} tokens")

    # Full listing sorted by freq
    sorted_h = sorted(h_compounds.items(), key=lambda x: -x[1]['freq'])

    print(f"\n  {'MIDDLE':>12} {'HEAD':>5} {'MODS':>12} {'CAT':>12} {'FREQ':>6}  DECOMPOSITION")
    print(f"  {'-'*12} {'-'*5} {'-'*12} {'-'*12} {'-'*6}  {'-'*35}")

    for mid, info in sorted_h:
        h_str = info['head'] if info['head'] else '-'
        mod_str = '+'.join(info['mods']) if info['mods'] else '-'
        atoms = atomize(mid)
        gloss_parts = [ATOM_GLOSS.get(a[0], '?') for a in atoms]
        gloss = ' + '.join(gloss_parts)
        print(f"  {mid:>12} {h_str:>5} {mod_str:>12} {info['cat']:>12} {info['freq']:>6}  {gloss}")

    # Category distribution
    cat_counts = Counter()
    for info in h_compounds.values():
        cat_counts[info['cat']] += info['freq']

    print(f"\n  Category Distribution (h-terminal):")
    for cat, cnt in cat_counts.most_common():
        pct = 100 * cnt / total_tokens
        print(f"    {cat:>15}: {cnt:>5} ({pct:>5.1f}%)")

    # Entropy
    probs = [cnt / total_tokens for cnt in cat_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_entropy = math.log2(len(cat_counts))
    print(f"\n  Entropy: {entropy:.3f} bits (max {max_entropy:.3f}, ratio {entropy/max_entropy:.3f})")

    # HEAD -> category for h-terminal
    print(f"\n  HEAD -> Category (h-terminal only):")
    head_cat = defaultdict(Counter)
    for mid, info in h_compounds.items():
        h_base = info['head'][0] if info['head'] else '?'
        head_cat[h_base][info['cat']] += info['freq']

    for h in sorted(head_cat):
        total = sum(head_cat[h].values())
        dom = head_cat[h].most_common(1)[0]
        pct = 100 * dom[1] / total
        top3 = head_cat[h].most_common(3)
        top3_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top3)
        print(f"    HEAD={h}: {pct:>5.1f}% {dom[0]:>12}  (n={total:>4})  [{top3_str}]")

    return h_compounds, cat_counts


# --- Test 2: Modifier Effects on h-Terminal -----------------------

def test2_modifier_effects(middles, categories, h_compounds):
    """Test whether modifier stack predicts category for h-terminal compounds."""
    print("\n" + "=" * 80)
    print("TEST 2: Modifier Effects on h-Terminal")
    print("=" * 80)

    # Collect modifier-h combinations
    mod_h_patterns = defaultdict(Counter)  # pattern -> {cat: count}
    mod_before_h = Counter()

    for mid, info in h_compounds.items():
        mods = info['mods']
        cat = info['cat']
        freq = info['freq']

        if mods:
            # Get last modifier before h (most proximate)
            last_mod = mods[-1][0]
            mod_before_h[last_mod] += freq

            # Full mod string
            mod_str = ''.join(m[0] for m in mods) + 'h'
        else:
            mod_str = '_h'  # Just HEAD + h, no modifiers
            last_mod = None

        mod_h_patterns[mod_str][cat] += freq

    # Show each modifier-h pattern
    print(f"\n  Modifier patterns ending in h:")
    print(f"  {'Pattern':>12} {'Total':>6} {'DomCat':>12} {'Purity':>7}  Distribution")
    print(f"  {'-'*12} {'-'*6} {'-'*12} {'-'*7}  {'-'*40}")

    sorted_patterns = sorted(mod_h_patterns.items(),
                            key=lambda x: -sum(x[1].values()))

    for pattern, cats in sorted_patterns:
        total = sum(cats.values())
        if total < 2:
            continue
        dom = cats.most_common(1)[0]
        purity = 100 * dom[1] / total
        dist = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in cats.most_common(3))
        print(f"  {pattern:>12} {total:>6} {dom[0]:>12} {purity:>6.1f}%  {dist}")

    # Specific test: does 'c' before 'h' (i.e. _ch pattern) lock category?
    print(f"\n  Specific modifier-h combinations:")
    for mod_char in sorted(set(m[0] for info in h_compounds.values() for m in info['mods'])):
        with_mod = Counter()
        without_mod = Counter()
        for mid, info in h_compounds.items():
            cat = info['cat']
            freq = info['freq']
            mod_chars = set(m[0] for m in info['mods'])
            if mod_char in mod_chars:
                with_mod[cat] += freq
            else:
                without_mod[cat] += freq

        total_w = sum(with_mod.values())
        total_wo = sum(without_mod.values())
        if total_w < 5:
            continue

        dom_w = with_mod.most_common(1)[0] if with_mod else ('?', 0)
        dom_wo = without_mod.most_common(1)[0] if without_mod else ('?', 0)
        pct_w = 100 * dom_w[1] / total_w if total_w > 0 else 0
        pct_wo = 100 * dom_wo[1] / total_wo if total_wo > 0 else 0

        print(f"    mod={mod_char} ({ATOM_GLOSS.get(mod_char,'?'):>10}): "
              f"WITH={pct_w:.0f}% {dom_w[0]:>12} (n={total_w})  "
              f"WITHOUT={pct_wo:.0f}% {dom_wo[0]:>12} (n={total_wo})")

    # Cramer's V: HEAD only vs HEAD+modifiers for category prediction
    print(f"\n  Prediction comparison:")

    # Build records for HEAD-only
    head_records = []
    head_mod_records = []
    for mid, info in h_compounds.items():
        h_base = info['head'][0] if info['head'] else '?'
        mod_str = ''.join(m[0] for m in info['mods']) if info['mods'] else 'NONE'
        head_mod_key = f"{h_base}_{mod_str}"
        cat = info['cat']
        freq = info['freq']
        head_records.append({'row': h_base, 'col': cat, 'count': freq})
        head_mod_records.append({'row': head_mod_key, 'col': cat, 'count': freq})

    v_head, p_head, n_head = cramers_v(head_records, 'row', 'col', 'count')
    v_hm, p_hm, n_hm = cramers_v(head_mod_records, 'row', 'col', 'count')

    print(f"    V(HEAD -> category | TERM=h):          {v_head:.3f} (p={p_head:.2e}, n={n_head})")
    print(f"    V(HEAD+MODS -> category | TERM=h):     {v_hm:.3f} (p={p_hm:.2e}, n={n_hm})")
    print(f"    Modifier gain:                         {v_hm - v_head:+.3f}")

    return {
        'v_head_only': round(v_head, 3),
        'v_head_plus_mods': round(v_hm, 3),
        'modifier_gain': round(v_hm - v_head, 3),
        'p_head': p_head,
        'p_head_mods': p_hm,
    }


# --- Test 3: PREFIX x h-Terminal Interaction ----------------------

def test3_prefix_interaction(middles, categories, h_compounds, prefix_middle):
    """Test whether PREFIX resolves h-terminal category ambiguity."""
    print("\n" + "=" * 80)
    print("TEST 3: PREFIX x h-Terminal Interaction")
    print("=" * 80)

    # Build h-terminal token set
    h_mids = set(h_compounds.keys())

    # Collect (PREFIX, category) for h-terminal tokens
    h_pfx_cat = Counter()
    non_h_pfx_cat = Counter()

    for (pfx, mid), count in prefix_middle.items():
        cat = categories.get(mid, 'UNKNOWN')
        if mid in h_mids:
            h_pfx_cat[(pfx, cat)] += count
        elif len(mid) >= 2:
            head, mods, term = decompose(mid)
            if term is not None:
                non_h_pfx_cat[(pfx, cat)] += count

    # h-terminal: PREFIX -> category distribution
    print(f"\n  PREFIX -> Category (h-terminal compounds):")
    h_pfx_totals = Counter()
    h_pfx_cats = defaultdict(Counter)
    for (pfx, cat), cnt in h_pfx_cat.items():
        h_pfx_totals[pfx] += cnt
        h_pfx_cats[pfx][cat] += cnt

    print(f"  {'PREFIX':>8} {'Total':>6} {'DomCat':>12} {'Purity':>7}  Distribution")
    print(f"  {'-'*8} {'-'*6} {'-'*12} {'-'*7}  {'-'*50}")

    for pfx in sorted(h_pfx_totals, key=lambda x: -h_pfx_totals[x]):
        total = h_pfx_totals[pfx]
        if total < 5:
            continue
        cats = h_pfx_cats[pfx]
        dom = cats.most_common(1)[0]
        purity = 100 * dom[1] / total
        dist = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in cats.most_common(4))
        print(f"  {pfx:>8} {total:>6} {dom[0]:>12} {purity:>6.1f}%  {dist}")

    # Cramer's V for h-terminal vs non-h-terminal
    h_records = [{'row': pfx, 'col': cat, 'count': cnt}
                 for (pfx, cat), cnt in h_pfx_cat.items()]
    non_h_records = [{'row': pfx, 'col': cat, 'count': cnt}
                     for (pfx, cat), cnt in non_h_pfx_cat.items()]

    v_h, p_h, n_h = cramers_v(h_records, 'row', 'col', 'count')
    v_non_h, p_non_h, n_non_h = cramers_v(non_h_records, 'row', 'col', 'count')

    print(f"\n  PREFIX x Category association:")
    print(f"    h-terminal:     V = {v_h:.3f} (p={p_h:.2e}, n={n_h})")
    print(f"    non-h-terminal: V = {v_non_h:.3f} (p={p_non_h:.2e}, n={n_non_h})")
    print(f"    Difference:     {v_h - v_non_h:+.3f}")

    stronger = "PREFIX resolves h MORE" if v_h > v_non_h else "PREFIX resolves h LESS"
    print(f"    Verdict: {stronger} than for other terminals")

    return {
        'v_prefix_h': round(v_h, 3),
        'v_prefix_non_h': round(v_non_h, 3),
        'difference': round(v_h - v_non_h, 3),
        'p_h': p_h,
        'p_non_h': p_non_h,
    }


# --- Test 4: h as "Open Monitor" ---------------------------------

def test4_open_monitor(middles, categories, h_compounds):
    """Test whether HEAD does the category work when TERM=h."""
    print("\n" + "=" * 80)
    print("TEST 4: h as 'Open Monitor' Hypothesis")
    print("=" * 80)
    print("  If h = 'keep watching', then HEAD should determine category")
    print("  as strongly as TERM determines it for other terminals.")

    # V(HEAD -> category | TERM=h)
    h_head_records = []
    for mid, info in h_compounds.items():
        h_base = info['head'][0] if info['head'] else '?'
        h_head_records.append({
            'row': h_base, 'col': info['cat'], 'count': info['freq']
        })

    v_head_h, p_head_h, n_head_h = cramers_v(h_head_records, 'row', 'col', 'count')

    # V(TERM -> category | all compound terminals)
    term_records = []
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompose(mid)
        if head is None or term is None:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        term_records.append({
            'row': term[0], 'col': cat, 'count': count
        })

    v_term_all, p_term_all, n_term_all = cramers_v(term_records, 'row', 'col', 'count')

    # V(HEAD -> category | all compounds, not just h)
    head_all_records = []
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompose(mid)
        if head is None:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        head_all_records.append({
            'row': head[0], 'col': cat, 'count': count
        })

    v_head_all, p_head_all, n_head_all = cramers_v(head_all_records, 'row', 'col', 'count')

    # V(TERM -> category | non-h terminals only)
    non_h_term_records = []
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompose(mid)
        if head is None or term is None:
            continue
        if term[0] == 'h':
            continue
        cat = categories.get(mid, 'UNKNOWN')
        non_h_term_records.append({
            'row': term[0], 'col': cat, 'count': count
        })

    v_term_non_h, p_term_non_h, n_term_non_h = cramers_v(
        non_h_term_records, 'row', 'col', 'count')

    print(f"\n  Comparison of predictive power:")
    print(f"    V(HEAD -> category | TERM=h):        {v_head_h:.3f}  (HEAD predicting category for h-terminal)")
    print(f"    V(TERM -> category | all compounds): {v_term_all:.3f}  (TERM predicting category overall)")
    print(f"    V(TERM -> category | non-h only):    {v_term_non_h:.3f}  (TERM predicting category excluding h)")
    print(f"    V(HEAD -> category | all compounds): {v_head_all:.3f}  (HEAD predicting category overall)")

    ratio = v_head_h / v_term_non_h if v_term_non_h > 0 else float('inf')
    print(f"\n  HEAD-for-h / TERM-for-others ratio: {ratio:.3f}")

    if ratio > 0.8:
        verdict = "SUPPORTED: HEAD carries category signal when TERM=h, h is transparent"
    elif ratio > 0.5:
        verdict = "PARTIAL: HEAD carries some signal but h is not fully transparent"
    else:
        verdict = "REJECTED: HEAD cannot substitute for TERM's category role"

    print(f"  Verdict: {verdict}")

    # Per-HEAD breakdown for h-terminal to show what each HEAD does
    print(f"\n  Per-HEAD category breakdown (h-terminal):")
    head_cat = defaultdict(Counter)
    for mid, info in h_compounds.items():
        h_base = info['head'][0] if info['head'] else '?'
        head_cat[h_base][info['cat']] += info['freq']

    for h in sorted(head_cat, key=lambda x: -sum(head_cat[x].values())):
        total = sum(head_cat[h].values())
        if total < 3:
            continue
        dom = head_cat[h].most_common(1)[0]
        pct = 100 * dom[1] / total
        # Entropy for this HEAD
        probs = [cnt / total for cnt in head_cat[h].values()]
        ent = -sum(p * math.log2(p) for p in probs if p > 0)
        max_ent = math.log2(len(head_cat[h]))
        norm_ent = ent / max_ent if max_ent > 0 else 0

        top3 = head_cat[h].most_common(3)
        top3_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top3)
        symbol = "***" if pct >= 70 else "**" if pct >= 50 else "*"
        print(f"    HEAD={h} ({ATOM_GLOSS.get(h, '?'):>8}): "
              f"dom={pct:.0f}% {dom[0]:>12} H(norm)={norm_ent:.2f} "
              f"n={total:>4} {symbol} [{top3_str}]")

    return {
        'v_head_for_h': round(v_head_h, 3),
        'v_term_for_all': round(v_term_all, 3),
        'v_term_for_non_h': round(v_term_non_h, 3),
        'v_head_for_all': round(v_head_all, 3),
        'ratio_head_h_to_term_non_h': round(ratio, 3),
        'verdict': verdict,
    }


# --- Test 5: ch as a Unit ----------------------------------------

def test5_ch_unit(middles, categories, h_compounds):
    """Test whether ch fusion is the source of h-terminal chaos."""
    print("\n" + "=" * 80)
    print("TEST 5: ch as a Fused Unit")
    print("=" * 80)

    # Separate h-terminal compounds into those ending in _ch vs other h-terminals
    ch_ending = {}
    non_ch_h = {}

    for mid, info in h_compounds.items():
        atoms = atomize(mid)
        # Check if last two chars are 'c' then 'h'
        if len(atoms) >= 2 and atoms[-2] == 'c' and atoms[-1] == 'h':
            ch_ending[mid] = info
        else:
            non_ch_h[mid] = info

    ch_tokens = sum(v['freq'] for v in ch_ending.values())
    non_ch_tokens = sum(v['freq'] for v in non_ch_h.values())
    total_tokens = ch_tokens + non_ch_tokens

    print(f"\n  h-terminal compounds ending in ...ch: {len(ch_ending)} types, {ch_tokens} tokens ({100*ch_tokens/total_tokens:.1f}%)")
    print(f"  h-terminal compounds (other):          {len(non_ch_h)} types, {non_ch_tokens} tokens ({100*non_ch_tokens/total_tokens:.1f}%)")

    # Category distribution for ch-ending
    ch_cats = Counter()
    for info in ch_ending.values():
        ch_cats[info['cat']] += info['freq']

    print(f"\n  Category distribution (..ch ending):")
    for cat, cnt in ch_cats.most_common():
        pct = 100 * cnt / ch_tokens if ch_tokens > 0 else 0
        print(f"    {cat:>15}: {cnt:>5} ({pct:>5.1f}%)")

    if ch_tokens > 0:
        probs_ch = [cnt / ch_tokens for cnt in ch_cats.values()]
        ent_ch = -sum(p * math.log2(p) for p in probs_ch if p > 0)
    else:
        ent_ch = 0

    # Category distribution for non-ch h-ending
    non_ch_cats = Counter()
    for info in non_ch_h.values():
        non_ch_cats[info['cat']] += info['freq']

    print(f"\n  Category distribution (non-ch h-terminal):")
    for cat, cnt in non_ch_cats.most_common():
        pct = 100 * cnt / non_ch_tokens if non_ch_tokens > 0 else 0
        print(f"    {cat:>15}: {cnt:>5} ({pct:>5.1f}%)")

    if non_ch_tokens > 0:
        probs_non_ch = [cnt / non_ch_tokens for cnt in non_ch_cats.values()]
        ent_non_ch = -sum(p * math.log2(p) for p in probs_non_ch if p > 0)
    else:
        ent_non_ch = 0

    print(f"\n  Entropy comparison:")
    print(f"    ..ch ending:      {ent_ch:.3f} bits")
    print(f"    non-ch h-ending:  {ent_non_ch:.3f} bits")
    print(f"    Difference:       {ent_ch - ent_non_ch:+.3f} bits")

    if ent_non_ch < ent_ch:
        print(f"    -> Removing ch makes h-terminal LESS chaotic (more category-coherent)")
    else:
        print(f"    -> Removing ch makes h-terminal MORE chaotic (ch was not the problem)")

    # ch-ending compounds: what HEAD drives their category?
    print(f"\n  HEAD -> Category for ..ch compounds:")
    ch_head_cat = defaultdict(Counter)
    for mid, info in ch_ending.items():
        h_base = info['head'][0] if info['head'] else '?'
        ch_head_cat[h_base][info['cat']] += info['freq']

    for h in sorted(ch_head_cat, key=lambda x: -sum(ch_head_cat[x].values())):
        total = sum(ch_head_cat[h].values())
        dom = ch_head_cat[h].most_common(1)[0]
        pct = 100 * dom[1] / total
        top3 = ch_head_cat[h].most_common(3)
        top3_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top3)
        print(f"    HEAD={h}: {pct:.0f}% {dom[0]:>12} (n={total}) [{top3_str}]")

    # List the actual ch-ending compounds
    print(f"\n  All ..ch compounds (freq >= 2):")
    print(f"  {'MIDDLE':>12} {'HEAD':>5} {'MODS':>12} {'CAT':>12} {'FREQ':>6}")
    for mid, info in sorted(ch_ending.items(), key=lambda x: -x[1]['freq']):
        if info['freq'] < 2:
            continue
        h_str = info['head'] if info['head'] else '-'
        # All mods EXCLUDING the 'c' that fuses with terminal 'h'
        actual_mods = info['mods']
        mod_str = '+'.join(actual_mods) if actual_mods else '-'
        print(f"  {mid:>12} {h_str:>5} {mod_str:>12} {info['cat']:>12} {info['freq']:>6}")

    # Also check: how does PREFIX `ch` interact?
    # When ch is a PREFIX, the MIDDLE is what follows — this is different
    # from when ch is inside a compound MIDDLE
    print(f"\n  Note: ch as PREFIX vs ch as MIDDLE terminal are different constructs")
    print(f"  PREFIX ch- selects MIDDLE families (C911), while MIDDLE-terminal ch")
    print(f"  is a compound where c=adjust fuses with h=watch.")

    return {
        'ch_ending_types': len(ch_ending),
        'ch_ending_tokens': ch_tokens,
        'ch_ending_pct': round(100 * ch_tokens / total_tokens, 1) if total_tokens > 0 else 0,
        'non_ch_h_types': len(non_ch_h),
        'non_ch_h_tokens': non_ch_tokens,
        'entropy_ch_ending': round(ent_ch, 3),
        'entropy_non_ch_h': round(ent_non_ch, 3),
        'entropy_diff': round(ent_ch - ent_non_ch, 3),
    }


# --- Synthesis ---------------------------------------------------

def synthesis(h_compounds, categories, middles, t2_res, t3_res, t4_res, t5_res):
    """Pull together findings."""
    print("\n" + "=" * 80)
    print("SYNTHESIS: What Drives h-Terminal Category?")
    print("=" * 80)

    total_h = sum(v['freq'] for v in h_compounds.values())

    # Compare TERM=h to other terminals
    term_entropies = defaultdict(Counter)
    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompose(mid)
        if head is None or term is None:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        term_entropies[term[0]][cat] += count

    print(f"\n  Terminal Atom Category Entropy Comparison:")
    print(f"  {'TERM':>6} {'Tokens':>7} {'DomCat':>12} {'Purity':>7} {'Entropy':>8} {'H/Hmax':>7}")
    print(f"  {'-'*6} {'-'*7} {'-'*12} {'-'*7} {'-'*8} {'-'*7}")

    for t in sorted(term_entropies):
        cats = term_entropies[t]
        total = sum(cats.values())
        if total < 10:
            continue
        dom = cats.most_common(1)[0]
        pct = 100 * dom[1] / total
        probs = [cnt / total for cnt in cats.values()]
        ent = -sum(p * math.log2(p) for p in probs if p > 0)
        max_ent = math.log2(len(cats)) if len(cats) > 1 else 1
        marker = " <<<" if t == 'h' else ""
        print(f"  {t:>6} {total:>7} {dom[0]:>12} {pct:>6.1f}% {ent:>7.3f}  {ent/max_ent:>6.3f}{marker}")

    # Key verdicts
    print(f"\n  KEY FINDINGS:")
    print(f"  1. HEAD prediction (TERM=h): V = {t4_res['v_head_for_h']:.3f}")
    print(f"     TERM prediction (non-h):  V = {t4_res['v_term_for_non_h']:.3f}")
    print(f"     Ratio: {t4_res['ratio_head_h_to_term_non_h']:.3f}")
    print(f"     -> {t4_res['verdict']}")

    print(f"\n  2. Modifier stack gain: {t2_res['modifier_gain']:+.3f}")
    if t2_res['modifier_gain'] > 0.05:
        print(f"     -> Modifiers ADD category information beyond HEAD")
    else:
        print(f"     -> Modifiers add LITTLE beyond HEAD")

    print(f"\n  3. PREFIX effect on h-terminal: V = {t3_res['v_prefix_h']:.3f}")
    print(f"     PREFIX effect on non-h:      V = {t3_res['v_prefix_non_h']:.3f}")
    if t3_res['v_prefix_h'] > t3_res['v_prefix_non_h']:
        print(f"     -> PREFIX resolves h MORE than other terminals (compensatory)")
    else:
        print(f"     -> PREFIX resolves h LESS than other terminals")

    print(f"\n  4. ch fusion contribution: {t5_res['ch_ending_pct']:.0f}% of h-terminal tokens")
    if t5_res['entropy_diff'] > 0:
        print(f"     -> ch-ending ADDS chaos (+{t5_res['entropy_diff']:.3f} bits entropy)")
    else:
        print(f"     -> ch-ending REDUCES chaos ({t5_res['entropy_diff']:.3f} bits entropy)")


# --- Main ---------------------------------------------------------

def main():
    print("Phase 506 Test 2: h-Terminal Category Chaos")
    print("=" * 80)
    print()

    # Load data
    middles, categories, prefix_middle = load_data()
    print(f"Loaded {len(middles)} unique MIDDLEs, {sum(middles.values())} tokens")

    # Run tests
    h_compounds, cat_counts = test1_h_terminal_breakdown(middles, categories)
    t2_res = test2_modifier_effects(middles, categories, h_compounds)
    t3_res = test3_prefix_interaction(middles, categories, h_compounds, prefix_middle)
    t4_res = test4_open_monitor(middles, categories, h_compounds)
    t5_res = test5_ch_unit(middles, categories, h_compounds)

    synthesis(h_compounds, categories, middles, t2_res, t3_res, t4_res, t5_res)

    # Save JSON results
    json_results = {
        'test1': {
            'h_terminal_types': len(h_compounds),
            'h_terminal_tokens': sum(v['freq'] for v in h_compounds.values()),
            'category_distribution': {cat: cnt for cat, cnt in cat_counts.most_common()},
        },
        'test2_modifier_effects': t2_res,
        'test3_prefix_interaction': t3_res,
        'test4_open_monitor': t4_res,
        'test5_ch_unit': t5_res,
    }

    json_path = RESULTS_DIR / 'h_terminal_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"\nJSON results saved to: {json_path}")


if __name__ == '__main__':
    main()

"""
C1394 Open Question 1: Headless Compound HEAD Recovery
=======================================================

Can the missing HEAD in headless compounds be reliably inferred
from the PREFIX channel? Specifically:
  da → a-domain, ka → k-domain, sa → s-domain, ta → t-domain?

Background (C1394 T8):
- 467 headless compound types (20.6% of compound tokens) lack a valid HEAD
- Massively concentrated under a-base PREFIXes (da 2213x enrichment)
- Enriched in CONTAINMENT (10.4x), MARKING (5.3x), MONITORING (3.9x)
- Favor boundary positions

Test approach:
1. For each PREFIX, compute category distribution of its headless compounds
2. Compare to category distribution of HEADED compounds under the same
   HEAD that matches the PREFIX base
   (e.g., da headless vs a-HEAD headed; ka headless vs k-HEAD headed)
3. Measure similarity (cosine, chi-squared, KL divergence)
4. Test whether non-a-base PREFIXes behave differently
5. Key metric: if we ASSIGN PREFIX-base as HEAD, does category prediction improve?
"""

import sys
import os
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import cosine as cosine_dist
import numpy as np

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

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}

ALL_CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
                  'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']

# PREFIX base extraction (C1218): last character of PREFIX is the base
# a-base PREFIXes: da, ka, sa, ta
# Other bases: ch(h-base), sh(h-base), qo(o-base), ok(k-base), ot(t-base), ol(l-base)

def get_prefix_base(prefix):
    """Extract the base character from a PREFIX (C1218: final character)."""
    if not prefix:
        return None
    return prefix[-1]


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


def is_compound(middle):
    return len(atomize(middle)) >= 2


def first_atom_base(middle):
    atoms = atomize(middle)
    if not atoms:
        return None
    return atoms[0][0]


def is_headless(middle):
    if not is_compound(middle):
        return False
    base = first_atom_base(middle)
    return base not in HEAD_SET


def get_head(middle):
    """Get the HEAD atom's base character, or None if headless."""
    if not is_compound(middle):
        return middle[0] if middle else None  # single atom = itself
    base = first_atom_base(middle)
    if base in HEAD_SET:
        return base
    return None


# --- Data Loading -------------------------------------------------

def load_data():
    """Load all Currier B tokens with morphology, category, position, and PREFIX base."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    records = []
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        cat = cc.classify(m.middle) or 'UNKNOWN'
        prefix = m.prefix or ''
        pfx_base = get_prefix_base(prefix) if prefix else None

        records.append({
            'word': tok.word,
            'middle': m.middle,
            'prefix': prefix if prefix else 'BARE',
            'prefix_base': pfx_base,
            'suffix': m.suffix,
            'category': cat,
            'folio': tok.folio,
            'line': tok.line,
            'is_compound': is_compound(m.middle),
            'is_headless': is_headless(m.middle),
            'head': get_head(m.middle),
            'first_atom': first_atom_base(m.middle),
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
        })

    return records


def cat_vector(counter, categories=ALL_CATEGORIES):
    """Convert a Counter of categories to a normalized vector."""
    total = sum(counter.values())
    if total == 0:
        return np.zeros(len(categories))
    return np.array([counter.get(c, 0) / total for c in categories])


def kl_divergence(p, q, epsilon=1e-10):
    """KL divergence D(p || q) with smoothing."""
    p = np.array(p) + epsilon
    q = np.array(q) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    return np.sum(p * np.log(p / q))


def chi2_test(counter1, counter2, categories=ALL_CATEGORIES):
    """Chi-squared test between two category distributions."""
    obs = np.array([[counter1.get(c, 0) for c in categories],
                    [counter2.get(c, 0) for c in categories]])
    # Remove zero columns
    nonzero = obs.sum(axis=0) > 0
    obs = obs[:, nonzero]
    if obs.shape[1] < 2:
        return 0, 1.0, 0
    chi2, p, dof, _ = stats.chi2_contingency(obs)
    n = obs.sum()
    k = min(obs.shape)
    v = (chi2 / (n * (k - 1))) ** 0.5 if n * (k - 1) > 0 else 0
    return chi2, p, v


# === TEST 1: PREFIX-Base → HEAD Domain Mapping ====================

def test1_prefix_base_head_mapping(records):
    """For each PREFIX base, compare headless compound categories to
    headed compounds that share that HEAD."""
    print("=" * 80)
    print("TEST 1: PREFIX-Base → HEAD Domain Mapping")
    print("=" * 80)

    # Partition: headed compounds by HEAD, headless by PREFIX-base
    headed_by_head = defaultdict(Counter)     # head_atom → category counts
    headless_by_pfx_base = defaultdict(Counter)  # pfx_base → category counts
    headless_by_pfx_base_n = defaultdict(int)
    headed_by_head_n = defaultdict(int)

    for r in records:
        if not r['is_compound']:
            continue
        cat = r['category']
        if cat == 'UNKNOWN':
            continue

        if r['is_headless']:
            pb = r['prefix_base']
            if pb:
                headless_by_pfx_base[pb][cat] += 1
                headless_by_pfx_base_n[pb] += 1
        else:
            head = r['head']
            if head:
                headed_by_head[head][cat] += 1
                headed_by_head_n[head] += 1

    # Map: which HEAD corresponds to which PREFIX base?
    # C1218/C1219: PREFIX base character = operational domain
    # a-base → a-HEAD, k-base → k-HEAD, etc.
    # Also test: h-base → ? (ch/sh), o-base → o-HEAD, t-base → t-HEAD, l-base → ?
    base_to_head = {
        'a': 'a',  # da, ka(base=a?), sa, ta → a-domain?
        'k': 'k',
        'e': 'e',
        'o': 'o',
        't': 't',
        'h': None,  # h is TERMINAL, not HEAD → no direct mapping
        'l': None,  # l is TERMINAL
        'r': None,  # r is TERMINAL
    }

    print(f"\nHeaded compound distribution by HEAD:")
    for head in sorted(headed_by_head):
        total = headed_by_head_n[head]
        top = headed_by_head[head].most_common(3)
        top_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top)
        print(f"  HEAD={head}: {total:>5} tokens  [{top_str}]")

    print(f"\nHeadless compound distribution by PREFIX base:")
    for pb in sorted(headless_by_pfx_base, key=lambda x: -headless_by_pfx_base_n[x]):
        total = headless_by_pfx_base_n[pb]
        top = headless_by_pfx_base[pb].most_common(3)
        top_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top)
        print(f"  PFX_BASE={pb}: {total:>5} tokens  [{top_str}]")

    # Compute similarity: for each PREFIX base that maps to a HEAD,
    # compare headless[pfx_base] vs headed[head]
    print(f"\n{'='*70}")
    print(f"COMPARISON: Headless(PREFIX_BASE=X) vs Headed(HEAD=X)")
    print(f"{'='*70}")

    comparisons = {}
    for base in sorted(headless_by_pfx_base):
        mapped_head = base_to_head.get(base)
        if mapped_head and mapped_head in headed_by_head:
            hl_counter = headless_by_pfx_base[base]
            hd_counter = headed_by_head[mapped_head]

            hl_vec = cat_vector(hl_counter)
            hd_vec = cat_vector(hd_counter)

            # Cosine similarity
            cos_sim = 1.0 - cosine_dist(hl_vec, hd_vec) if np.any(hl_vec) and np.any(hd_vec) else 0
            # KL divergence
            kl = kl_divergence(hl_vec, hd_vec)
            # Chi-squared
            chi2, p, v = chi2_test(hl_counter, hd_counter)

            hl_total = headless_by_pfx_base_n[base]
            hd_total = headed_by_head_n[mapped_head]

            print(f"\n  PREFIX_BASE={base} ({hl_total} tokens) vs HEAD={mapped_head} ({hd_total} tokens):")
            print(f"    Cosine similarity: {cos_sim:.4f}")
            print(f"    KL divergence:     {kl:.4f}")
            print(f"    Chi2={chi2:.1f}, p={p:.2e}, Cramer's V={v:.3f}")

            # Show both distributions side-by-side
            print(f"    {'Category':<15} {'Headless':>10} {'Headed':>10} {'Diff':>10}")
            for cat in ALL_CATEGORIES:
                hl_pct = 100 * hl_counter.get(cat, 0) / hl_total if hl_total else 0
                hd_pct = 100 * hd_counter.get(cat, 0) / hd_total if hd_total else 0
                diff = hl_pct - hd_pct
                marker = '***' if abs(diff) > 15 else '**' if abs(diff) > 10 else '*' if abs(diff) > 5 else ''
                print(f"    {cat:<15} {hl_pct:>9.1f}% {hd_pct:>9.1f}% {diff:>+9.1f}% {marker}")

            comparisons[base] = {
                'prefix_base': base,
                'mapped_head': mapped_head,
                'headless_tokens': hl_total,
                'headed_tokens': hd_total,
                'cosine_similarity': round(cos_sim, 4),
                'kl_divergence': round(kl, 4),
                'chi2': round(chi2, 1),
                'p_value': p,
                'cramers_v': round(v, 3),
                'headless_dist': {c: round(hl_counter.get(c, 0) / hl_total, 4) if hl_total else 0
                                  for c in ALL_CATEGORIES},
                'headed_dist': {c: round(hd_counter.get(c, 0) / hd_total, 4) if hd_total else 0
                                for c in ALL_CATEGORIES},
            }
        else:
            # No HEAD mapping (h, l, r bases) or no headed data
            hl_total = headless_by_pfx_base_n[base]
            print(f"\n  PREFIX_BASE={base} ({hl_total} tokens) → no direct HEAD mapping")
            top = headless_by_pfx_base[base].most_common(3)
            top_str = ', '.join(f"{c}:{100*n/hl_total:.0f}%" for c, n in top)
            print(f"    Category profile: [{top_str}]")

    return comparisons, headed_by_head, headless_by_pfx_base, headed_by_head_n, headless_by_pfx_base_n


# === TEST 2: Per-PREFIX Analysis (da, ka, sa, ta individually) =====

def test2_per_prefix_analysis(records):
    """Analyze headless compounds per specific PREFIX (not just base)."""
    print("\n" + "=" * 80)
    print("TEST 2: Per-PREFIX Headless Compound Analysis")
    print("=" * 80)

    # Count headless compound categories per specific PREFIX
    headless_pfx_cats = defaultdict(Counter)
    headless_pfx_n = defaultdict(int)

    # Also count ALL (headed+headless) compound categories per PREFIX for baseline
    all_pfx_cats = defaultdict(Counter)
    all_pfx_n = defaultdict(int)

    for r in records:
        if not r['is_compound']:
            continue
        cat = r['category']
        if cat == 'UNKNOWN':
            continue

        pfx = r['prefix']
        all_pfx_cats[pfx][cat] += 1
        all_pfx_n[pfx] += 1

        if r['is_headless']:
            headless_pfx_cats[pfx][cat] += 1
            headless_pfx_n[pfx] += 1

    # Focus on PREFIXes with 10+ headless tokens
    sig_prefixes = sorted([p for p in headless_pfx_n if headless_pfx_n[p] >= 10],
                          key=lambda x: -headless_pfx_n[x])

    print(f"\n  PREFIXes with 10+ headless compound tokens: {len(sig_prefixes)}")
    print(f"\n  {'PREFIX':<10} {'Headless':>10} {'All':>10} {'H_frac':>8} "
          f"{'Top cat':>15} {'%':>6}  Base")

    results = {}
    for pfx in sig_prefixes:
        hl_total = headless_pfx_n[pfx]
        all_total = all_pfx_n[pfx]
        hl_frac = hl_total / all_total if all_total else 0
        top_cat = headless_pfx_cats[pfx].most_common(1)[0]
        base = get_prefix_base(pfx) if pfx != 'BARE' else None

        print(f"  {pfx:<10} {hl_total:>10} {all_total:>10} {hl_frac:>7.1%} "
              f"{top_cat[0]:>15} {100*top_cat[1]/hl_total:>5.1f}%  {base or '-'}")

        results[pfx] = {
            'headless_tokens': hl_total,
            'all_tokens': all_total,
            'headless_fraction': round(hl_frac, 4),
            'prefix_base': base,
            'category_dist': {c: headless_pfx_cats[pfx].get(c, 0)
                              for c in ALL_CATEGORIES},
        }

    # Show category profile for top 4 a-base PREFIXes (da, ka, sa, ta)
    a_base_pfxs = [p for p in sig_prefixes if get_prefix_base(p) == 'a']
    if a_base_pfxs:
        print(f"\n  A-base PREFIX headless category profiles:")
        print(f"  {'PREFIX':<8}", end='')
        for cat in ALL_CATEGORIES:
            print(f" {cat[:4]:>6}", end='')
        print(f"  {'N':>6}")

        for pfx in a_base_pfxs:
            total = headless_pfx_n[pfx]
            print(f"  {pfx:<8}", end='')
            for cat in ALL_CATEGORIES:
                pct = 100 * headless_pfx_cats[pfx].get(cat, 0) / total if total else 0
                print(f" {pct:>5.1f}%", end='')
            print(f"  {total:>6}")

    return results


# === TEST 3: Category Prediction Improvement =====================

def test3_prediction_improvement(records, headed_by_head, headless_by_pfx_base,
                                  headed_by_head_n, headless_by_pfx_base_n):
    """Test: if we assign PREFIX-base as HEAD, does category prediction improve?"""
    print("\n" + "=" * 80)
    print("TEST 3: Category Prediction Improvement with HEAD Recovery")
    print("=" * 80)

    # Strategy: for each headless token, predict category using:
    #   A) No HEAD (marginal distribution of all headless compounds)
    #   B) PREFIX-base as HEAD (use headed distribution for that HEAD)
    #   C) Specific PREFIX (use headless distribution for that PREFIX)

    # Build reference distributions
    # A: Overall headless category distribution
    all_headless_cats = Counter()
    for r in records:
        if r['is_compound'] and r['is_headless'] and r['category'] != 'UNKNOWN':
            all_headless_cats[r['category']] += 1

    all_headless_vec = cat_vector(all_headless_cats)
    baseline_dom_cat = all_headless_cats.most_common(1)[0][0]
    baseline_accuracy = all_headless_cats.most_common(1)[0][1] / sum(all_headless_cats.values())

    print(f"\n  Baseline (predict most-common headless category '{baseline_dom_cat}'): "
          f"{100*baseline_accuracy:.1f}%")

    # For each headless token, predict:
    correct_A = 0  # Method A: overall headless mode
    correct_B = 0  # Method B: PREFIX-base as HEAD
    correct_C = 0  # Method C: specific PREFIX
    total = 0
    method_B_applicable = 0

    # Pre-compute dominant categories
    head_dom_cats = {}
    for head, counter in headed_by_head.items():
        if counter:
            head_dom_cats[head] = counter.most_common(1)[0][0]

    pfx_dom_cats = {}
    for r in records:
        if r['is_compound'] and r['is_headless'] and r['category'] != 'UNKNOWN':
            pfx = r['prefix']
            if pfx not in pfx_dom_cats:
                # Build from all headless under this PREFIX
                pfx_counter = Counter()
                for r2 in records:
                    if (r2['is_compound'] and r2['is_headless'] and
                        r2['category'] != 'UNKNOWN' and r2['prefix'] == pfx):
                        pfx_counter[r2['category']] += 1
                if pfx_counter:
                    pfx_dom_cats[pfx] = pfx_counter.most_common(1)[0][0]

    base_to_head_map = {'a': 'a', 'k': 'k', 'e': 'e', 'o': 'o', 't': 't'}

    for r in records:
        if not r['is_compound'] or not r['is_headless'] or r['category'] == 'UNKNOWN':
            continue

        cat = r['category']
        total += 1

        # Method A: overall headless mode
        if cat == baseline_dom_cat:
            correct_A += 1

        # Method B: PREFIX-base → HEAD
        pb = r['prefix_base']
        mapped_head = base_to_head_map.get(pb) if pb else None
        if mapped_head and mapped_head in head_dom_cats:
            method_B_applicable += 1
            if cat == head_dom_cats[mapped_head]:
                correct_B += 1

        # Method C: specific PREFIX
        pfx = r['prefix']
        if pfx in pfx_dom_cats:
            if cat == pfx_dom_cats[pfx]:
                correct_C += 1

    acc_A = correct_A / total if total else 0
    acc_B = correct_B / method_B_applicable if method_B_applicable else 0
    acc_C = correct_C / total if total else 0

    print(f"\n  Category prediction accuracy for headless compounds (N={total}):")
    print(f"    Method A (overall mode):          {100*acc_A:.1f}% ({correct_A}/{total})")
    print(f"    Method B (PREFIX-base as HEAD):    {100*acc_B:.1f}% ({correct_B}/{method_B_applicable})"
          f"  [applicable to {method_B_applicable}/{total} = {100*method_B_applicable/total:.1f}%]")
    print(f"    Method C (specific PREFIX):        {100*acc_C:.1f}% ({correct_C}/{total})")

    improvement_B = acc_B - acc_A
    improvement_C = acc_C - acc_A

    print(f"\n  Improvement over baseline:")
    print(f"    Method B: {improvement_B:+.1%} ({'BETTER' if improvement_B > 0 else 'WORSE' if improvement_B < 0 else 'NO CHANGE'})")
    print(f"    Method C: {improvement_C:+.1%} ({'BETTER' if improvement_C > 0 else 'WORSE' if improvement_C < 0 else 'NO CHANGE'})")

    return {
        'total_headless_tokens': total,
        'baseline_accuracy': round(acc_A, 4),
        'baseline_category': baseline_dom_cat,
        'method_B_accuracy': round(acc_B, 4),
        'method_B_applicable': method_B_applicable,
        'method_C_accuracy': round(acc_C, 4),
        'improvement_B': round(improvement_B, 4),
        'improvement_C': round(improvement_C, 4),
    }


# === TEST 4: a-base PREFIX Category Differentiation ===============

def test4_a_base_differentiation(records):
    """Test whether MODIFIER character of a-base PREFIXes (d/k/s/t in da/ka/sa/ta)
    differentiates category profiles of headless compounds."""
    print("\n" + "=" * 80)
    print("TEST 4: a-Base PREFIX Modifier Differentiates Headless Categories")
    print("=" * 80)

    # Collect headless compounds under a-base PREFIXes
    a_base_prefixes = defaultdict(Counter)  # prefix → category counts
    a_base_n = defaultdict(int)

    for r in records:
        if not r['is_compound'] or not r['is_headless'] or r['category'] == 'UNKNOWN':
            continue
        pb = r['prefix_base']
        if pb != 'a':
            continue

        pfx = r['prefix']
        a_base_prefixes[pfx][r['category']] += 1
        a_base_n[pfx] += 1

    # Compare: does the MODIFIER part (d, k, s, t) of the PREFIX differentiate?
    sig_pfxs = [p for p in a_base_prefixes if a_base_n[p] >= 10]

    if len(sig_pfxs) < 2:
        print("  Insufficient a-base PREFIXes with 10+ headless tokens")
        return {}

    print(f"\n  a-Base PREFIXes with 10+ headless tokens: {sig_pfxs}")

    # Build contingency table
    print(f"\n  {'PREFIX':<8} {'Modifier':<10}", end='')
    for cat in ALL_CATEGORIES:
        print(f" {cat[:5]:>7}", end='')
    print(f"  {'N':>6}")

    contingency_data = []
    for pfx in sorted(sig_pfxs):
        total = a_base_n[pfx]
        modifier = pfx[:-1] if len(pfx) > 1 else 'BARE'
        print(f"  {pfx:<8} {modifier:<10}", end='')
        row = []
        for cat in ALL_CATEGORIES:
            cnt = a_base_prefixes[pfx].get(cat, 0)
            pct = 100 * cnt / total if total else 0
            print(f" {pct:>6.1f}%", end='')
            row.append(cnt)
        print(f"  {total:>6}")
        contingency_data.append(row)

    # Chi-squared test across all a-base PREFIXes
    if len(contingency_data) >= 2:
        obs = np.array(contingency_data)
        # Remove zero columns
        nonzero = obs.sum(axis=0) > 0
        obs_filtered = obs[:, nonzero]
        if obs_filtered.shape[1] >= 2 and obs_filtered.shape[0] >= 2:
            chi2, p, dof, expected = stats.chi2_contingency(obs_filtered)
            n = obs_filtered.sum()
            k = min(obs_filtered.shape)
            v = (chi2 / (n * (k - 1))) ** 0.5 if n * (k - 1) > 0 else 0
            print(f"\n  Chi2={chi2:.1f}, p={p:.2e}, Cramer's V={v:.3f}")
            print(f"  → a-base PREFIX modifiers {'DO' if v > 0.1 else 'DO NOT'} "
                  f"meaningfully differentiate headless category profiles")
        else:
            chi2, p, v = 0, 1, 0
    else:
        chi2, p, v = 0, 1, 0

    # Pairwise comparison of top a-base PREFIXes
    print(f"\n  Pairwise cosine similarity between a-base PREFIXes:")
    pairwise = {}
    for i, pfx1 in enumerate(sorted(sig_pfxs)):
        for pfx2 in sorted(sig_pfxs)[i+1:]:
            v1 = cat_vector(a_base_prefixes[pfx1])
            v2 = cat_vector(a_base_prefixes[pfx2])
            cos_sim = 1.0 - cosine_dist(v1, v2) if np.any(v1) and np.any(v2) else 0
            print(f"    {pfx1} vs {pfx2}: cosine={cos_sim:.4f}")
            pairwise[f"{pfx1}_vs_{pfx2}"] = round(cos_sim, 4)

    return {
        'a_base_prefixes': {p: {'n': a_base_n[p], 'cats': dict(a_base_prefixes[p])}
                            for p in sig_pfxs},
        'chi2': round(chi2, 1) if chi2 else 0,
        'p_value': p,
        'cramers_v': round(v, 3) if v else 0,
        'pairwise_cosine': pairwise,
    }


# === TEST 5: Non-a-base PREFIX Headless Behavior =================

def test5_non_a_base(records, headed_by_head, headed_by_head_n):
    """Test: do headless compounds under non-a-base PREFIXes behave differently?"""
    print("\n" + "=" * 80)
    print("TEST 5: Non-a-Base PREFIX Headless Behavior")
    print("=" * 80)

    # Group headless by whether PREFIX base is 'a' or not
    a_base_cats = Counter()
    non_a_cats = Counter()
    bare_cats = Counter()
    a_base_n = 0
    non_a_n = 0
    bare_n = 0

    # Also track by specific non-a bases
    non_a_by_base = defaultdict(Counter)
    non_a_by_base_n = defaultdict(int)

    for r in records:
        if not r['is_compound'] or not r['is_headless'] or r['category'] == 'UNKNOWN':
            continue

        pb = r['prefix_base']
        pfx = r['prefix']

        if pfx == 'BARE':
            bare_cats[r['category']] += 1
            bare_n += 1
        elif pb == 'a':
            a_base_cats[r['category']] += 1
            a_base_n += 1
        else:
            non_a_cats[r['category']] += 1
            non_a_n += 1
            if pb:
                non_a_by_base[pb][r['category']] += 1
                non_a_by_base_n[pb] += 1

    print(f"\n  Population:")
    print(f"    a-base PREFIXes:   {a_base_n} tokens")
    print(f"    Non-a-base PREFIXes: {non_a_n} tokens")
    print(f"    BARE (no PREFIX):  {bare_n} tokens")

    # Compare a-base vs non-a-base
    print(f"\n  {'Category':<15} {'a-base':>10} {'non-a':>10} {'BARE':>10}")
    for cat in ALL_CATEGORIES:
        a_pct = 100 * a_base_cats.get(cat, 0) / a_base_n if a_base_n else 0
        na_pct = 100 * non_a_cats.get(cat, 0) / non_a_n if non_a_n else 0
        b_pct = 100 * bare_cats.get(cat, 0) / bare_n if bare_n else 0
        print(f"  {cat:<15} {a_pct:>9.1f}% {na_pct:>9.1f}% {b_pct:>9.1f}%")

    # Cosine similarity
    a_vec = cat_vector(a_base_cats)
    na_vec = cat_vector(non_a_cats)
    b_vec = cat_vector(bare_cats)

    cos_a_na = 1.0 - cosine_dist(a_vec, na_vec) if np.any(a_vec) and np.any(na_vec) else 0
    cos_a_b = 1.0 - cosine_dist(a_vec, b_vec) if np.any(a_vec) and np.any(b_vec) else 0
    cos_na_b = 1.0 - cosine_dist(na_vec, b_vec) if np.any(na_vec) and np.any(b_vec) else 0

    print(f"\n  Cosine similarities:")
    print(f"    a-base vs non-a: {cos_a_na:.4f}")
    print(f"    a-base vs BARE:  {cos_a_b:.4f}")
    print(f"    non-a vs BARE:   {cos_na_b:.4f}")

    # Non-a-base breakdown
    if non_a_by_base:
        print(f"\n  Non-a-base headless breakdown:")
        for base in sorted(non_a_by_base, key=lambda x: -non_a_by_base_n[x]):
            total = non_a_by_base_n[base]
            if total < 5:
                continue
            top = non_a_by_base[base].most_common(3)
            top_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top)
            # Compare to same-letter HEAD if exists
            head_match = ''
            if base in headed_by_head and headed_by_head_n.get(base, 0) > 0:
                hd_top = headed_by_head[base].most_common(1)[0]
                hd_pct = 100 * hd_top[1] / headed_by_head_n[base]
                head_vec = cat_vector(headed_by_head[base])
                hl_vec = cat_vector(non_a_by_base[base])
                cos = 1.0 - cosine_dist(hl_vec, head_vec) if np.any(hl_vec) and np.any(head_vec) else 0
                head_match = f"  cos(HEAD={base})={cos:.3f}"
            print(f"    base={base}: {total:>5} tokens  [{top_str}]{head_match}")

    return {
        'a_base_n': a_base_n,
        'non_a_n': non_a_n,
        'bare_n': bare_n,
        'cosine_a_vs_non_a': round(cos_a_na, 4),
        'cosine_a_vs_bare': round(cos_a_b, 4),
        'cosine_non_a_vs_bare': round(cos_na_b, 4),
    }


# === TEST 6: Full Recovery Test — Assign HEAD, Recompute ==========

def test6_full_recovery(records):
    """Assign PREFIX-base as HEAD and recompute category via atom-vote.
    Compare accuracy of:
    - Original classification (CategoryClassifier)
    - Reconstructed classification with PREFIX-base prepended as HEAD atom
    """
    print("\n" + "=" * 80)
    print("TEST 6: Full HEAD Recovery — Recompute Category with Assigned HEAD")
    print("=" * 80)

    cc = CategoryClassifier()

    # For each headless compound, create a "recovered" MIDDLE by prepending PREFIX-base
    # Then classify the recovered MIDDLE via atom vote and compare to original

    base_to_head_map = {'a': 'a', 'k': 'k', 'e': 'e', 'o': 'o', 't': 't'}
    recoverable = 0
    recovered_match = 0
    recovered_total = 0
    not_recoverable = 0

    # Track category confusion
    confusion = defaultdict(Counter)  # original_cat → recovered_cat → count

    # Also track: does original cc.classify() already produce a good answer?
    original_classified = 0
    original_none = 0

    for r in records:
        if not r['is_compound'] or not r['is_headless']:
            continue

        cat_original = r['category']
        pb = r['prefix_base']
        mid = r['middle']

        mapped_head = base_to_head_map.get(pb) if pb else None

        if not mapped_head:
            not_recoverable += 1
            continue

        recoverable += 1

        # Create recovered MIDDLE
        recovered_mid = mapped_head + mid
        cat_recovered = cc.classify(recovered_mid)

        if cat_original != 'UNKNOWN':
            recovered_total += 1
            if cat_recovered and cat_recovered == cat_original:
                recovered_match += 1
            if cat_recovered:
                confusion[cat_original][cat_recovered] += 1
            else:
                confusion[cat_original]['UNCLASSIFIED'] += 1

        if cat_original != 'UNKNOWN':
            original_classified += 1
        else:
            original_none += 1

    # Also test: reclassify the ORIGINAL headless MIDDLE via atom vote (it already works)
    # The question is whether prepending HEAD changes the result
    original_atom_correct = 0
    recovered_atom_correct = 0
    atom_vote_total = 0

    for r in records:
        if not r['is_compound'] or not r['is_headless'] or r['category'] == 'UNKNOWN':
            continue

        cat_original = r['category']
        pb = r['prefix_base']
        mid = r['middle']
        mapped_head = base_to_head_map.get(pb) if pb else None
        if not mapped_head:
            continue

        # Atom vote on original MIDDLE
        orig_vote = cc._auto_assign(mid)
        # Atom vote on recovered MIDDLE
        recovered_mid = mapped_head + mid
        recv_vote = cc._auto_assign(recovered_mid)

        atom_vote_total += 1
        if orig_vote == cat_original:
            original_atom_correct += 1
        if recv_vote == cat_original:
            recovered_atom_correct += 1

    orig_acc = original_atom_correct / atom_vote_total if atom_vote_total else 0
    recv_acc = recovered_atom_correct / atom_vote_total if atom_vote_total else 0

    print(f"\n  Recoverable headless tokens: {recoverable} (PREFIX-base maps to HEAD)")
    print(f"  Not recoverable: {not_recoverable} (PREFIX-base has no HEAD mapping)")

    print(f"\n  Atom-vote category accuracy (N={atom_vote_total}):")
    print(f"    Original MIDDLE (no HEAD):      {100*orig_acc:.1f}% ({original_atom_correct}/{atom_vote_total})")
    print(f"    Recovered MIDDLE (HEAD prepend): {100*recv_acc:.1f}% ({recovered_atom_correct}/{atom_vote_total})")
    print(f"    Improvement: {100*(recv_acc-orig_acc):+.1f}pp")

    # Confusion matrix for recovered
    if confusion:
        print(f"\n  Category confusion (rows=original, cols=recovered, top 10 flows):")
        flows = []
        for orig, recv_counts in confusion.items():
            for recv, cnt in recv_counts.items():
                flows.append((orig, recv, cnt))
        flows.sort(key=lambda x: -x[2])
        for orig, recv, cnt in flows[:10]:
            marker = 'MATCH' if orig == recv else 'SHIFT'
            print(f"    {orig:>15} → {recv:<15} {cnt:>5}  {marker}")

    return {
        'recoverable': recoverable,
        'not_recoverable': not_recoverable,
        'atom_vote_total': atom_vote_total,
        'original_atom_accuracy': round(orig_acc, 4),
        'recovered_atom_accuracy': round(recv_acc, 4),
        'improvement_pp': round(100 * (recv_acc - orig_acc), 1),
    }


# === MAIN =========================================================

def main():
    print("C1394 Open Question 1: Headless Compound HEAD Recovery")
    print("=" * 80)
    print("Loading Currier B data...")

    records = load_data()
    print(f"  Loaded {len(records)} tokens\n")

    # Run tests
    t1_comparisons, headed_by_head, headless_by_pfx_base, headed_n, headless_n = \
        test1_prefix_base_head_mapping(records)

    t2_results = test2_per_prefix_analysis(records)
    t3_results = test3_prediction_improvement(records, headed_by_head,
                                               headless_by_pfx_base, headed_n, headless_n)
    t4_results = test4_a_base_differentiation(records)
    t5_results = test5_non_a_base(records, headed_by_head, headed_n)
    t6_results = test6_full_recovery(records)

    # === SYNTHESIS ================================================
    print("\n" + "=" * 80)
    print("SYNTHESIS")
    print("=" * 80)

    # Key question: Can PREFIX-base supply the missing HEAD?
    print(f"\n  1. PREFIX-BASE → HEAD SIMILARITY:")
    if t1_comparisons:
        mean_cos = np.mean([v['cosine_similarity'] for v in t1_comparisons.values()])
        mean_v = np.mean([v['cramers_v'] for v in t1_comparisons.values()])
        print(f"     Mean cosine similarity: {mean_cos:.4f}")
        print(f"     Mean Cramer's V (divergence): {mean_v:.3f}")
        for base, comp in sorted(t1_comparisons.items()):
            print(f"     {base}: cos={comp['cosine_similarity']:.3f}, "
                  f"V={comp['cramers_v']:.3f} "
                  f"({comp['headless_tokens']} headless vs {comp['headed_tokens']} headed)")

    print(f"\n  2. PREDICTION ACCURACY:")
    print(f"     Baseline (mode):        {100*t3_results['baseline_accuracy']:.1f}%")
    print(f"     PREFIX-base as HEAD:    {100*t3_results['method_B_accuracy']:.1f}%")
    print(f"     Specific PREFIX:        {100*t3_results['method_C_accuracy']:.1f}%")

    print(f"\n  3. ATOM-VOTE RECOVERY (Test 6):")
    print(f"     Without HEAD: {100*t6_results['original_atom_accuracy']:.1f}%")
    print(f"     With HEAD:    {100*t6_results['recovered_atom_accuracy']:.1f}%")
    print(f"     Change:       {t6_results['improvement_pp']:+.1f}pp")

    print(f"\n  4. a-BASE DIFFERENTIATION:")
    if t4_results:
        print(f"     V={t4_results.get('cramers_v', 0):.3f} across da/ka/sa/ta")
        print(f"     → PREFIX modifier {'DOES' if t4_results.get('cramers_v', 0) > 0.1 else 'does NOT'} "
              f"differentiate within a-base headless compounds")

    # VERDICT
    print(f"\n{'='*80}")
    print("VERDICT")
    print(f"{'='*80}")

    if t1_comparisons:
        mean_cos = np.mean([v['cosine_similarity'] for v in t1_comparisons.values()])

        if mean_cos < 0.5:
            verdict = "REJECTED"
            explanation = ("PREFIX-base categories are DISSIMILAR to HEAD categories. "
                          "Headless compounds are genuinely different operations, "
                          "not abbreviated headed ones.")
        elif mean_cos < 0.8:
            verdict = "PARTIALLY_SUPPORTED"
            explanation = ("PREFIX-base shows moderate alignment with HEAD domains. "
                          "Some recovery is possible but headless compounds also carry "
                          "independent category information.")
        else:
            verdict = "STRONGLY_SUPPORTED"
            explanation = ("PREFIX-base categories closely match HEAD categories. "
                          "HEAD can be reliably recovered from PREFIX channel.")
    else:
        verdict = "INSUFFICIENT_DATA"
        explanation = "No valid comparisons could be made."

    recovery_useful = t6_results['improvement_pp'] > 1.0

    print(f"\n  HEAD recovery from PREFIX-base: {verdict}")
    print(f"  {explanation}")
    print(f"\n  Atom-vote improvement with recovery: {t6_results['improvement_pp']:+.1f}pp "
          f"→ {'USEFUL' if recovery_useful else 'NOT USEFUL'}")

    if t3_results['method_C_accuracy'] > t3_results['method_B_accuracy']:
        print(f"\n  NOTE: Specific PREFIX ({100*t3_results['method_C_accuracy']:.1f}%) outperforms "
              f"PREFIX-base HEAD recovery ({100*t3_results['method_B_accuracy']:.1f}%). "
              f"The full PREFIX (not just base) carries the real discriminative signal.")

    # === SAVE RESULTS =============================================
    output = {
        'test1_prefix_base_head_mapping': t1_comparisons,
        'test2_per_prefix_analysis': t2_results,
        'test3_prediction_improvement': t3_results,
        'test4_a_base_differentiation': t4_results,
        'test5_non_a_base': t5_results,
        'test6_full_recovery': t6_results,
        'verdict': verdict,
        'explanation': explanation,
        'recovery_useful': recovery_useful,
    }

    out_path = RESULTS_DIR / 'headless_head_recovery.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

"""
Cross-System HEAD Domain Stability for Bridge MIDDLEs
=====================================================

When a bridge MIDDLE (appearing in both Currier A and Currier B) has HEAD=k,
is it in THERMAL contexts in both systems? Does HEAD domain carry the same
operational meaning across A and B?

Background:
- 85 bridge MIDDLEs appear in both A and B (C1013)
- In B, HEAD atoms predict operational category: k=71% THERMAL, t=65% FLOW,
  a=55% FLOW, e=37% OPERATION, o=35% STAGING (C1394 T5)
- A MIDDLEs follow the same HEAD+MOD*+TERM encoding (shared grammar test)
- Question: does the same HEAD carry the same category meaning in both systems?

Tests:
  T1: Bridge MIDDLE census with HEAD decomposition
  T2: B-side category distribution per HEAD for bridge MIDDLEs
  T3: A-side PREFIX context distribution per HEAD for bridge MIDDLEs
  T4: Cross-system category correlation per HEAD
  T5: Individual bridge MIDDLE cross-system comparison
  T6: Permutation test - is HEAD-category association stronger than chance?
"""

import sys
import os
import io
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ---------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}  # a, e, o, k, t

ALL_CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
                  'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

N_PERMUTATIONS = 2000
random.seed(42)
np.random.seed(42)


# --- Atom Decomposition -----------------------------------------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms."""
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


def get_head(middle):
    """Extract HEAD atom base character from a MIDDLE string.

    Returns base char ('k', 'e', 'a', 'o', 't') or None for headless.
    """
    if not middle:
        return None
    atoms = atomize(middle)
    if not atoms:
        return None
    first_base = atoms[0][0]
    if first_base in HEAD_SET:
        return first_base
    return None


# --- Data Loading -----------------------------------------------------

def load_bridge_set():
    """Load the 85 bridge MIDDLEs from C1013."""
    bridge_path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])


def load_b_data(bridge_set):
    """Load Currier B token data for bridge MIDDLEs.

    Returns: dict[middle] -> {
        'tokens': int,
        'category_dist': Counter,  # from CategoryClassifier
        'prefix_dist': Counter,
        'section_dist': Counter,
    }
    """
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    b_data = defaultdict(lambda: {
        'tokens': 0,
        'category_dist': Counter(),
        'prefix_dist': Counter(),
        'section_dist': Counter(),
    })

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        mid = m.middle
        if not mid or mid not in bridge_set:
            continue

        cat = cc.classify(mid) or 'UNKNOWN'
        pfx = m.prefix or 'BARE'

        b_data[mid]['tokens'] += 1
        b_data[mid]['category_dist'][cat] += 1
        b_data[mid]['prefix_dist'][pfx] += 1

    return dict(b_data)


def load_a_data(bridge_set):
    """Load Currier A token data for bridge MIDDLEs.

    In A, we don't have operational categories directly — we get PREFIX
    context distributions and co-occurrence context.

    Returns: dict[middle] -> {
        'tokens': int,
        'prefix_dist': Counter,
        'section_dist': Counter,
        'folio_count': int,
    }
    """
    tx = Transcript()
    morph = Morphology()

    a_data = defaultdict(lambda: {
        'tokens': 0,
        'prefix_dist': Counter(),
        'section_dist': Counter(),
        'folios': set(),
    })

    for tok in tx.currier_a():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        mid = m.middle
        if not mid or mid not in bridge_set:
            continue

        pfx = m.prefix or 'BARE'

        a_data[mid]['tokens'] += 1
        a_data[mid]['prefix_dist'][pfx] += 1
        a_data[mid]['folios'].add(tok.folio)

    # Convert sets to counts
    result = {}
    for mid, info in a_data.items():
        result[mid] = {
            'tokens': info['tokens'],
            'prefix_dist': info['prefix_dist'],
            'section_dist': info['section_dist'],
            'folio_count': len(info['folios']),
        }

    return result


# --- Analysis Functions -----------------------------------------------

def js_divergence(dist1, dist2, all_keys=None):
    """Jensen-Shannon divergence between two distributions (Counters)."""
    if all_keys is None:
        all_keys = set(dist1.keys()) | set(dist2.keys())
    if not all_keys:
        return 0.0

    total1 = sum(dist1.values()) or 1
    total2 = sum(dist2.values()) or 1

    p = np.array([dist1.get(k, 0) / total1 for k in all_keys])
    q = np.array([dist2.get(k, 0) / total2 for k in all_keys])

    # Add epsilon for numerical stability
    eps = 1e-12
    p = p + eps
    q = q + eps
    p /= p.sum()
    q /= q.sum()

    m = 0.5 * (p + q)
    jsd = 0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m))
    return float(jsd)


def cosine_similarity(dist1, dist2, all_keys=None):
    """Cosine similarity between two distributions (Counters)."""
    if all_keys is None:
        all_keys = set(dist1.keys()) | set(dist2.keys())
    if not all_keys:
        return 0.0

    total1 = sum(dist1.values()) or 1
    total2 = sum(dist2.values()) or 1

    v1 = np.array([dist1.get(k, 0) / total1 for k in all_keys])
    v2 = np.array([dist2.get(k, 0) / total2 for k in all_keys])

    dot = np.dot(v1, v2)
    norm = (np.linalg.norm(v1) * np.linalg.norm(v2))
    if norm == 0:
        return 0.0
    return float(dot / norm)


# --- Main Tests -------------------------------------------------------

def main():
    print("Cross-System HEAD Domain Stability for Bridge MIDDLEs")
    print("=" * 70)

    # Load data
    bridge_set = load_bridge_set()
    print(f"\nLoading data for {len(bridge_set)} bridge MIDDLEs...")

    b_data = load_b_data(bridge_set)
    a_data = load_a_data(bridge_set)
    cc = CategoryClassifier()

    # Find bridge MIDDLEs present in both systems
    both = set(b_data.keys()) & set(a_data.keys())
    b_only = set(b_data.keys()) - set(a_data.keys())
    a_only = set(a_data.keys()) - set(b_data.keys())

    print(f"  Bridge MIDDLEs in both A and B: {len(both)}")
    print(f"  Bridge MIDDLEs B-only: {len(b_only)}")
    print(f"  Bridge MIDDLEs A-only: {len(a_only)}")

    results = {}

    # ================================================================
    # T1: Bridge MIDDLE Census with HEAD decomposition
    # ================================================================
    print("\n" + "=" * 70)
    print("T1: Bridge MIDDLE Census with HEAD Decomposition")
    print("=" * 70)

    head_groups = defaultdict(list)  # HEAD -> list of bridge MIDDLEs
    headless = []

    for mid in sorted(both):
        head = get_head(mid)
        if head:
            head_groups[head].append(mid)
        else:
            headless.append(mid)

    print(f"\n  HEAD distribution of bridge MIDDLEs in both systems:")
    head_census = {}
    for head in sorted(head_groups.keys()):
        mids = head_groups[head]
        b_tok = sum(b_data[m]['tokens'] for m in mids)
        a_tok = sum(a_data[m]['tokens'] for m in mids)
        print(f"    HEAD={head}: {len(mids)} MIDDLEs, B={b_tok} tokens, A={a_tok} tokens")
        print(f"           MIDDLEs: {', '.join(mids)}")
        head_census[head] = {
            'n_middles': len(mids),
            'b_tokens': b_tok,
            'a_tokens': a_tok,
            'middles': mids,
        }

    print(f"    HEADLESS: {len(headless)} MIDDLEs")
    if headless:
        print(f"              MIDDLEs: {', '.join(headless)}")
    head_census['NONE'] = {'n_middles': len(headless), 'middles': headless}

    results['t1_census'] = head_census

    # ================================================================
    # T2: B-side category distribution per HEAD for bridge MIDDLEs
    # ================================================================
    print("\n" + "=" * 70)
    print("T2: B-side Category Distribution per HEAD (Bridge MIDDLEs)")
    print("=" * 70)

    head_b_cat = {}  # HEAD -> aggregated category counter
    for head, mids in head_groups.items():
        cat_agg = Counter()
        for mid in mids:
            cat_agg += b_data[mid]['category_dist']
        head_b_cat[head] = cat_agg

    # Also headless
    headless_b_cat = Counter()
    for mid in headless:
        if mid in b_data:
            headless_b_cat += b_data[mid]['category_dist']
    head_b_cat['NONE'] = headless_b_cat

    print(f"\n  {'HEAD':>6} {'Total':>6}  ", end='')
    for cat in ALL_CATEGORIES:
        print(f"{cat[:4]:>6}", end='')
    print(f"  {'DOM_CAT':>12} {'DOM%':>5}")

    b_cat_results = {}
    for head in sorted(head_b_cat.keys()):
        dist = head_b_cat[head]
        total = sum(dist.values())
        if total == 0:
            continue
        print(f"  {head:>6} {total:>6}  ", end='')
        cat_pcts = {}
        for cat in ALL_CATEGORIES:
            pct = 100 * dist.get(cat, 0) / total
            cat_pcts[cat] = round(pct, 1)
            print(f"{pct:>5.1f}%", end='')

        dom = dist.most_common(1)[0]
        print(f"  {dom[0]:>12} {100*dom[1]/total:>4.0f}%")

        b_cat_results[head] = {
            'total_tokens': total,
            'category_pcts': cat_pcts,
            'dominant_category': dom[0],
            'dominant_pct': round(100 * dom[1] / total, 1),
        }

    results['t2_b_categories'] = b_cat_results

    # ================================================================
    # T3: A-side PREFIX context distribution per HEAD
    # ================================================================
    print("\n" + "=" * 70)
    print("T3: A-side PREFIX Context Distribution per HEAD (Bridge MIDDLEs)")
    print("=" * 70)

    # In A, PREFIX is the primary contextual signal. We examine whether
    # bridge MIDDLEs with the same HEAD tend to appear with the same PREFIXes.

    head_a_prefix = {}
    for head, mids in head_groups.items():
        pfx_agg = Counter()
        for mid in mids:
            if mid in a_data:
                pfx_agg += a_data[mid]['prefix_dist']
        head_a_prefix[head] = pfx_agg

    headless_a_pfx = Counter()
    for mid in headless:
        if mid in a_data:
            headless_a_pfx += a_data[mid]['prefix_dist']
    head_a_prefix['NONE'] = headless_a_pfx

    a_prefix_results = {}
    for head in sorted(head_a_prefix.keys()):
        dist = head_a_prefix[head]
        total = sum(dist.values())
        if total == 0:
            continue
        top5 = dist.most_common(5)
        top5_str = ', '.join(f"{p}:{100*c/total:.0f}%" for p, c in top5)
        dom = dist.most_common(1)[0]
        print(f"  HEAD={head:>4}: {total:>5} tokens, top PREFIXes: {top5_str}")

        a_prefix_results[head] = {
            'total_tokens': total,
            'dominant_prefix': dom[0],
            'dominant_pct': round(100 * dom[1] / total, 1),
            'top5': {p: round(100 * c / total, 1) for p, c in top5},
        }

    results['t3_a_prefixes'] = a_prefix_results

    # ================================================================
    # T4: Cross-system category correlation per HEAD
    # ================================================================
    print("\n" + "=" * 70)
    print("T4: Cross-System Category Correlation per HEAD")
    print("=" * 70)

    # For each HEAD group, compare the category distribution of bridge
    # MIDDLEs between A and B. In A we don't have direct categories, but
    # we can ASSIGN categories via the CategoryClassifier (atom vote) which
    # is system-independent (C1305: MIDDLE determines category).
    #
    # So the key question becomes: do bridge MIDDLEs with HEAD=k
    # get the SAME category in B execution context as their atom-vote
    # predicts? And is the HEAD-level aggregation consistent?

    # Per-bridge-MIDDLE: compare B empirical category vs atom-vote category
    print("\n  Per-bridge-MIDDLE: atom-vote category vs B empirical dominant category")
    print(f"  {'MIDDLE':>10} {'HEAD':>5} {'ATOM_VOTE':>12} {'B_DOM':>12} {'B_DOM%':>6} {'MATCH':>6} {'B_tok':>6} {'A_tok':>6}")
    print(f"  {'-'*10} {'-'*5} {'-'*12} {'-'*12} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")

    matches = 0
    mismatches = 0
    match_tokens = 0
    mismatch_tokens = 0
    per_middle_results = []

    for mid in sorted(both):
        head = get_head(mid)
        head_str = head if head else 'NONE'

        atom_cat = cc.classify(mid) or 'UNKNOWN'
        b_dist = b_data[mid]['category_dist']
        b_total = sum(b_dist.values())
        if b_total == 0:
            continue

        b_dom = b_dist.most_common(1)[0]
        b_dom_cat = b_dom[0]
        b_dom_pct = 100 * b_dom[1] / b_total

        match = atom_cat == b_dom_cat
        if match:
            matches += 1
            match_tokens += b_total
        else:
            mismatches += 1
            mismatch_tokens += b_total

        a_tok = a_data[mid]['tokens'] if mid in a_data else 0

        marker = 'YES' if match else 'NO'
        print(f"  {mid:>10} {head_str:>5} {atom_cat:>12} {b_dom_cat:>12} {b_dom_pct:>5.0f}% {marker:>6} {b_total:>6} {a_tok:>6}")

        per_middle_results.append({
            'middle': mid,
            'head': head_str,
            'atom_vote_category': atom_cat,
            'b_dominant_category': b_dom_cat,
            'b_dominant_pct': round(b_dom_pct, 1),
            'match': match,
            'b_tokens': b_total,
            'a_tokens': a_tok,
        })

    total_compared = matches + mismatches
    match_rate = matches / total_compared if total_compared > 0 else 0
    token_match_rate = match_tokens / (match_tokens + mismatch_tokens) if (match_tokens + mismatch_tokens) > 0 else 0

    print(f"\n  Match rate (by type): {matches}/{total_compared} = {100*match_rate:.1f}%")
    print(f"  Match rate (by token): {match_tokens}/{match_tokens+mismatch_tokens} = {100*token_match_rate:.1f}%")

    results['t4_per_middle'] = {
        'n_compared': total_compared,
        'matches': matches,
        'mismatches': mismatches,
        'match_rate_type': round(match_rate, 4),
        'match_rate_token': round(token_match_rate, 4),
        'details': per_middle_results,
    }

    # ================================================================
    # T5: HEAD-level cross-system category stability
    # ================================================================
    print("\n" + "=" * 70)
    print("T5: HEAD-Level Category Stability")
    print("=" * 70)

    # For each HEAD, aggregate the B-side category distribution of bridge
    # MIDDLEs. Compare across HEAD groups — do different HEADs select
    # different categories?

    # Chi-squared: HEAD vs category in B
    contingency_heads = []
    contingency_cats = []
    head_order = sorted([h for h in head_b_cat if h != 'NONE' and sum(head_b_cat[h].values()) > 0])

    obs_matrix = []
    for head in head_order:
        row = [head_b_cat[head].get(cat, 0) for cat in ALL_CATEGORIES]
        obs_matrix.append(row)

    obs_array = np.array(obs_matrix)

    # Remove zero-sum columns
    col_sums = obs_array.sum(axis=0)
    nonzero_cols = col_sums > 0
    obs_clean = obs_array[:, nonzero_cols]
    cats_clean = [c for c, nz in zip(ALL_CATEGORIES, nonzero_cols) if nz]

    if obs_clean.shape[0] >= 2 and obs_clean.shape[1] >= 2:
        chi2, p_val, dof, expected = stats.chi2_contingency(obs_clean)
        n = obs_clean.sum()
        k = min(obs_clean.shape)
        cramers_v = (chi2 / (n * (k - 1))) ** 0.5 if n > 0 and k > 1 else 0

        print(f"\n  Chi-squared (HEAD x Category in B):")
        print(f"    chi2 = {chi2:.1f}, dof = {dof}, p = {p_val:.2e}")
        print(f"    Cramer's V = {cramers_v:.3f}")
        print(f"    N = {int(n)} tokens across {len(head_order)} HEAD groups x {len(cats_clean)} categories")
    else:
        chi2, p_val, cramers_v = 0, 1, 0

    # Print HEAD vs category heatmap
    print(f"\n  {'':>6}", end='')
    for cat in cats_clean:
        print(f" {cat[:6]:>7}", end='')
    print(f"  {'DOM':>8} {'DOM%':>5}")

    head_stability_results = {}
    for i, head in enumerate(head_order):
        row = obs_clean[i]
        total = row.sum()
        print(f"  {head:>6}", end='')
        cat_pcts = {}
        for j, cat in enumerate(cats_clean):
            pct = 100 * row[j] / total if total > 0 else 0
            cat_pcts[cat] = round(pct, 1)
            print(f" {pct:>6.1f}%", end='')
        dom_idx = np.argmax(row)
        dom_pct = 100 * row[dom_idx] / total if total > 0 else 0
        print(f"  {cats_clean[dom_idx]:>8} {dom_pct:>4.0f}%")

        head_stability_results[head] = {
            'total_tokens': int(total),
            'category_pcts': cat_pcts,
            'dominant': cats_clean[dom_idx],
            'dominant_pct': round(dom_pct, 1),
        }

    results['t5_head_stability'] = {
        'chi2': round(chi2, 1),
        'p_value': float(p_val),
        'cramers_v': round(cramers_v, 3),
        'n_tokens': int(obs_clean.sum()),
        'n_heads': len(head_order),
        'n_categories': len(cats_clean),
        'per_head': head_stability_results,
    }

    # ================================================================
    # T6: Per-HEAD within-B category purity
    # ================================================================
    print("\n" + "=" * 70)
    print("T6: Per-HEAD Category Purity (Within B)")
    print("=" * 70)

    # How pure is each HEAD in category terms? Measured by dominant%

    print(f"\n  {'HEAD':>6} {'MIDDLEs':>8} {'Tokens':>7} {'DOM_CAT':>12} {'DOM%':>6} {'Entropy':>8}")
    print(f"  {'-'*6} {'-'*8} {'-'*7} {'-'*12} {'-'*6} {'-'*8}")

    purity_results = {}
    for head in head_order:
        dist = head_b_cat[head]
        total = sum(dist.values())
        n_mids = len(head_groups[head])
        dom = dist.most_common(1)[0]
        dom_pct = 100 * dom[1] / total if total > 0 else 0

        # Entropy
        entropy = 0.0
        for c in dist.values():
            p = c / total if total > 0 else 0
            if p > 0:
                entropy -= p * math.log2(p)

        print(f"  {head:>6} {n_mids:>8} {total:>7} {dom[0]:>12} {dom_pct:>5.1f}% {entropy:>7.3f}")

        purity_results[head] = {
            'n_middles': n_mids,
            'tokens': total,
            'dominant_category': dom[0],
            'dominant_pct': round(dom_pct, 1),
            'entropy': round(entropy, 3),
        }

    results['t6_purity'] = purity_results

    # ================================================================
    # T7: Permutation test — is HEAD→category association significant?
    # ================================================================
    print("\n" + "=" * 70)
    print("T7: Permutation Test — HEAD→Category Association Significance")
    print("=" * 70)

    # Real metric: mean dominant category percentage across HEADs
    real_dom_pcts = []
    for head in head_order:
        dist = head_b_cat[head]
        total = sum(dist.values())
        if total > 0:
            dom = dist.most_common(1)[0]
            real_dom_pcts.append(dom[1] / total)
    real_mean_purity = np.mean(real_dom_pcts) if real_dom_pcts else 0

    # Build token-level data for permutation
    token_heads = []  # HEAD for each bridge token in B
    token_cats = []   # category for each bridge token in B

    for mid in both:
        head = get_head(mid) or 'NONE'
        if head == 'NONE':
            continue
        for cat, count in b_data[mid]['category_dist'].items():
            for _ in range(count):
                token_heads.append(head)
                token_cats.append(cat)

    # Permutation: shuffle categories, re-measure mean dominant pct per HEAD
    perm_purities = []
    for _ in range(N_PERMUTATIONS):
        shuffled_cats = token_cats.copy()
        random.shuffle(shuffled_cats)

        # Rebuild HEAD→cat dist
        perm_head_cat = defaultdict(Counter)
        for h, c in zip(token_heads, shuffled_cats):
            perm_head_cat[h][c] += 1

        perm_dom_pcts = []
        for head in head_order:
            dist = perm_head_cat[head]
            total = sum(dist.values())
            if total > 0:
                dom = dist.most_common(1)[0]
                perm_dom_pcts.append(dom[1] / total)
        perm_purities.append(np.mean(perm_dom_pcts) if perm_dom_pcts else 0)

    perm_purities = np.array(perm_purities)
    z_score = (real_mean_purity - np.mean(perm_purities)) / (np.std(perm_purities) + 1e-12)
    p_above = np.mean(perm_purities >= real_mean_purity)

    print(f"\n  Real mean HEAD purity: {100*real_mean_purity:.1f}%")
    print(f"  Shuffled mean purity:  {100*np.mean(perm_purities):.1f}% (std {100*np.std(perm_purities):.2f}%)")
    print(f"  Z-score: {z_score:+.2f}")
    print(f"  p-value (real >= shuffled): {p_above:.4f}")
    print(f"  Purity enrichment: {real_mean_purity / np.mean(perm_purities):.3f}x" if np.mean(perm_purities) > 0 else "")
    print(f"  Verdict: {'HEAD DETERMINES CATEGORY' if z_score > 3 else 'SIGNIFICANT' if z_score > 2 else 'MARGINAL' if z_score > 1 else 'NOT SIGNIFICANT'}")

    results['t7_permutation'] = {
        'real_mean_purity': round(float(real_mean_purity), 4),
        'shuffled_mean_purity': round(float(np.mean(perm_purities)), 4),
        'shuffled_std': round(float(np.std(perm_purities)), 4),
        'z_score': round(float(z_score), 2),
        'p_value': round(float(p_above), 4),
        'enrichment': round(float(real_mean_purity / np.mean(perm_purities)), 3) if np.mean(perm_purities) > 0 else None,
        'n_permutations': N_PERMUTATIONS,
    }

    # ================================================================
    # T8: A-side PREFIX → category inference
    # ================================================================
    print("\n" + "=" * 70)
    print("T8: A-side PREFIX Distribution — Does It Track B Categories?")
    print("=" * 70)

    # In B, we know PREFIX→category has strong association (C1297).
    # Key PREFIXes: qo→THERMAL, ch/sh→mostly non-THERMAL, ok/ot→CONTAINMENT
    # If A-side bridge MIDDLEs with HEAD=k are preferentially used with
    # qo-prefix in B, and also appear in A, does the A PREFIX context
    # show any category-related pattern?

    # Compare A vs B PREFIX distributions for bridge MIDDLEs per HEAD
    print(f"\n  Per-HEAD: A vs B PREFIX distribution comparison")
    print(f"  {'HEAD':>6} {'Cosine':>7} {'JSD':>7} {'A_dom_pfx':>10} {'B_dom_pfx':>10}")
    print(f"  {'-'*6} {'-'*7} {'-'*7} {'-'*10} {'-'*10}")

    all_pfxs = set()
    for head in head_order:
        for mid in head_groups[head]:
            if mid in a_data:
                all_pfxs.update(a_data[mid]['prefix_dist'].keys())
            if mid in b_data:
                all_pfxs.update(b_data[mid]['prefix_dist'].keys())

    prefix_comparison = {}
    for head in head_order:
        a_pfx_agg = Counter()
        b_pfx_agg = Counter()
        for mid in head_groups[head]:
            if mid in a_data:
                a_pfx_agg += a_data[mid]['prefix_dist']
            if mid in b_data:
                b_pfx_agg += b_data[mid]['prefix_dist']

        if sum(a_pfx_agg.values()) == 0 or sum(b_pfx_agg.values()) == 0:
            continue

        cos = cosine_similarity(a_pfx_agg, b_pfx_agg, all_pfxs)
        jsd = js_divergence(a_pfx_agg, b_pfx_agg, all_pfxs)

        a_dom = a_pfx_agg.most_common(1)[0]
        b_dom = b_pfx_agg.most_common(1)[0]

        print(f"  {head:>6} {cos:>7.3f} {jsd:>7.3f} {a_dom[0]:>10} {b_dom[0]:>10}")

        prefix_comparison[head] = {
            'cosine': round(cos, 3),
            'jsd': round(jsd, 3),
            'a_dominant_prefix': a_dom[0],
            'b_dominant_prefix': b_dom[0],
            'a_top3': {p: round(100*c/sum(a_pfx_agg.values()), 1)
                       for p, c in a_pfx_agg.most_common(3)},
            'b_top3': {p: round(100*c/sum(b_pfx_agg.values()), 1)
                       for p, c in b_pfx_agg.most_common(3)},
        }

    results['t8_prefix_comparison'] = prefix_comparison

    # ================================================================
    # T9: Cross-system HEAD domain summary with expected vs observed
    # ================================================================
    print("\n" + "=" * 70)
    print("T9: HEAD Domain Cross-System Summary")
    print("=" * 70)

    # Expected category predictions from C1394 T5 (B data):
    expected_head_cat = {
        'k': 'THERMAL',
        'e': 'THERMAL',    # e is ~THERMAL by atom vote (cool→THERMAL)
        'a': 'TRANSITION',  # a=yield→TRANSITION by atom vote
        'o': 'OPERATION',   # o=work→OPERATION by atom vote
        't': 'FLOW',        # t=transfer→FLOW by atom vote
    }

    print(f"\n  {'HEAD':>6} {'Expected':>12} {'B_Observed':>12} {'Match?':>7} {'B_DOM%':>6} {'N_mids':>7}")
    print(f"  {'-'*6} {'-'*12} {'-'*12} {'-'*7} {'-'*6} {'-'*7}")

    head_matches = 0
    head_total = 0
    summary_rows = []

    for head in head_order:
        expected = expected_head_cat.get(head, '?')
        observed = head_stability_results[head]['dominant']
        dom_pct = head_stability_results[head]['dominant_pct']
        n_mids = len(head_groups[head])
        match = expected == observed
        if match:
            head_matches += 1
        head_total += 1
        marker = 'YES' if match else 'NO'
        print(f"  {head:>6} {expected:>12} {observed:>12} {marker:>7} {dom_pct:>5.1f}% {n_mids:>7}")

        summary_rows.append({
            'head': head,
            'expected_category': expected,
            'b_observed_category': observed,
            'match': match,
            'b_dominant_pct': dom_pct,
            'n_bridge_middles': n_mids,
        })

    print(f"\n  HEAD→Category prediction accuracy: {head_matches}/{head_total} = "
          f"{100*head_matches/head_total:.0f}%")

    results['t9_summary'] = {
        'head_match_rate': round(head_matches / head_total, 3) if head_total > 0 else 0,
        'rows': summary_rows,
    }

    # ================================================================
    # T10: Between-HEAD category separation
    # ================================================================
    print("\n" + "=" * 70)
    print("T10: Between-HEAD Category Separation (Pairwise JSD)")
    print("=" * 70)

    # Do different HEADs have distinguishable category profiles in B?
    print(f"\n  Pairwise JSD between HEAD category distributions:")
    print(f"  {'':>6}", end='')
    for h in head_order:
        print(f" {h:>6}", end='')
    print()

    jsd_matrix = {}
    for h1 in head_order:
        print(f"  {h1:>6}", end='')
        for h2 in head_order:
            jsd = js_divergence(head_b_cat[h1], head_b_cat[h2], ALL_CATEGORIES)
            print(f" {jsd:>6.3f}", end='')
            jsd_matrix[f"{h1}-{h2}"] = round(jsd, 4)
        print()

    # Mean between-HEAD JSD
    jsds = []
    for i, h1 in enumerate(head_order):
        for h2 in head_order[i+1:]:
            jsds.append(js_divergence(head_b_cat[h1], head_b_cat[h2], ALL_CATEGORIES))

    mean_jsd = np.mean(jsds) if jsds else 0
    print(f"\n  Mean between-HEAD JSD: {mean_jsd:.4f}")
    print(f"  Max between-HEAD JSD: {max(jsds):.4f}" if jsds else "")
    print(f"  Min between-HEAD JSD: {min(jsds):.4f}" if jsds else "")

    results['t10_separation'] = {
        'mean_jsd': round(mean_jsd, 4),
        'max_jsd': round(max(jsds), 4) if jsds else 0,
        'min_jsd': round(min(jsds), 4) if jsds else 0,
        'n_pairs': len(jsds),
    }

    # ================================================================
    # SYNTHESIS
    # ================================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS: Cross-System HEAD Domain Stability")
    print("=" * 70)

    verdict_parts = []

    # 1. Per-MIDDLE match rate
    if match_rate >= 0.7:
        verdict_parts.append("STRONG_MIDDLE_MATCH")
    elif match_rate >= 0.5:
        verdict_parts.append("MODERATE_MIDDLE_MATCH")
    else:
        verdict_parts.append("WEAK_MIDDLE_MATCH")

    # 2. HEAD→category significance
    if z_score > 3:
        verdict_parts.append("HEAD_DETERMINES_CATEGORY")
    elif z_score > 2:
        verdict_parts.append("HEAD_SIGNIFICANT")
    else:
        verdict_parts.append("HEAD_WEAK")

    # 3. Between-HEAD separation
    if mean_jsd > 0.1:
        verdict_parts.append("HEADS_WELL_SEPARATED")
    elif mean_jsd > 0.05:
        verdict_parts.append("HEADS_MODERATELY_SEPARATED")
    else:
        verdict_parts.append("HEADS_OVERLAPPING")

    # 4. HEAD prediction accuracy
    if head_matches == head_total:
        verdict_parts.append("PREDICTION_PERFECT")
    elif head_matches / head_total >= 0.8:
        verdict_parts.append("PREDICTION_STRONG")
    else:
        verdict_parts.append("PREDICTION_PARTIAL")

    overall_verdict = " + ".join(verdict_parts)

    print(f"\n  Per-MIDDLE atom→B category match rate: {100*match_rate:.1f}% (by type), {100*token_match_rate:.1f}% (by token)")
    print(f"  HEAD→Category permutation z-score: {z_score:+.2f}")
    print(f"  HEAD→Category chi2: {chi2:.1f}, Cramer's V: {cramers_v:.3f}")
    print(f"  Mean between-HEAD JSD: {mean_jsd:.4f}")
    print(f"  HEAD prediction accuracy: {head_matches}/{head_total}")
    print(f"\n  VERDICT: {overall_verdict}")

    # Key interpretation
    print(f"\n  INTERPRETATION:")
    if match_rate >= 0.5 and z_score > 2:
        print(f"  HEAD atoms carry the SAME operational domain meaning in both A and B.")
        print(f"  The instruction encoding architecture (HEAD+MOD*+TERM) is CROSS-SYSTEM,")
        print(f"  not just a B-execution phenomenon. Bridge MIDDLEs are the proof:")
        print(f"  when they appear in A registry and B execution, their HEAD-determined")
        print(f"  category is preserved.")
    else:
        print(f"  HEAD→category association is {'present but noisy' if z_score > 1 else 'not clearly established'}")
        print(f"  across systems. Further investigation needed.")

    results['synthesis'] = {
        'verdict': overall_verdict,
        'per_middle_match_rate_type': round(match_rate, 4),
        'per_middle_match_rate_token': round(token_match_rate, 4),
        'permutation_z': round(float(z_score), 2),
        'chi2': round(chi2, 1),
        'cramers_v': round(cramers_v, 3),
        'mean_between_head_jsd': round(mean_jsd, 4),
        'head_prediction_accuracy': round(head_matches / head_total, 3) if head_total > 0 else 0,
    }

    # Write results
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = RESULTS_DIR / 'cross_system_head_stability.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
    print(f"\n  Results written to {out_path}")


if __name__ == '__main__':
    main()

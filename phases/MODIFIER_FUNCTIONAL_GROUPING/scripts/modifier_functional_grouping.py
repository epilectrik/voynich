#!/usr/bin/env python3
"""
Phase 532: Modifier Functional Grouping Analysis

Research question: Do the 8 modifier pair avoidance patterns discovered in C1472
reveal meaningful functional groups among the 6 modifier atoms {p,c,i,f,d,s}?

C1472 found that modifier co-occurrence avoidance dominates ordering:
  Empty pairs (NEVER co-occur): (p,f), (p,i), (p,c), (p,d), (f,c), (f,d), (i,c), (i,d)
  Co-occurring pairs: (p,s), (f,i), (f,s), (i,s), (c,d), (c,s), (d,s)

This suggests two avoidance groups: {p,f,i} avoid {c,d}, with s as universal connector.

Tests:
  T1: Per-modifier behavioral profiles (6 dimensions)
  T2: Modifier pair behavioral similarity (JSD between profiles)
  T3: Avoidance group vs co-occurrence group behavioral coherence
  T4: Hypothesis A: {p,f,i} vs {c,d} vs {s}
  T5: Hypothesis B: avoidance = functional redundancy
  T6: Hypothesis C: avoidance = incompatible operational contexts
  T7: s universality mechanism
  T8: Modifier-HEAD compatibility patterns
  T9: Modifier-TERMINAL compatibility patterns
  T10: Category-level grouping alignment

Dependencies: C1472, C1393, C1394, C1397, C1389-C1392, C1448, C1450, C1452-C1456
"""

import sys
import os
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# =============================================================================
# CONFIGURATION
# =============================================================================

MOD_ATOMS = {'p', 'c', 'i', 'f', 'd', 's'}
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
TERM_ATOMS = {'y', 'l', 'r', 'h', 'm', 'n'}

# From C1472: avoidance structure
EMPTY_PAIRS = {
    frozenset({'p', 'f'}), frozenset({'p', 'i'}), frozenset({'p', 'c'}),
    frozenset({'p', 'd'}), frozenset({'f', 'c'}), frozenset({'f', 'd'}),
    frozenset({'i', 'c'}), frozenset({'i', 'd'})
}
COOCCURRING_PAIRS = {
    frozenset({'p', 's'}), frozenset({'f', 'i'}), frozenset({'f', 's'}),
    frozenset({'i', 's'}), frozenset({'c', 'd'}), frozenset({'c', 's'}),
    frozenset({'d', 's'})
}

# Hypothesis A grouping
GROUP_PFI = {'p', 'f', 'i'}
GROUP_CD = {'c', 'd'}
GROUP_S = {'s'}

# Frame hazard map (from decoder_maps.json / C1448)
FRAME_HAZARD = {
    'o->bare': 'HIGH', 'd->y': 'HIGH', 'a->l': 'HIGH', 'a->r': 'HIGH',
    'o->r': 'HIGH', 'e->e': 'HIGH', 'a->n': 'HIGH',
    'e->y': 'ZERO', 'e->l': 'ZERO', 'i->n': 'ZERO',
    'k->y': 'IMMUNE', 'k->l': 'IMMUNE', 'k->r': 'IMMUNE',
    'k->h': 'IMMUNE', 'k->m': 'IMMUNE', 'k->n': 'IMMUNE',
    'k->bare': 'IMMUNE',
}

# Atom-to-category mapping (from decoder_maps.json)
ATOM_TO_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'MONITORING', 'y': 'TRANSITION',
    'i': 'STAGING', 'n': 'TRANSITION', 'a': 'TRANSITION', 'm': 'TRANSITION',
    'd': 'MARKING', 't': 'FLOW', 'c': 'MARKING', 'p': 'MARKING',
    'f': 'MARKING', 's': 'STAGING', 'o': 'OPERATION', 'l': 'CONTAINMENT',
    'r': 'FLOW'
}

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

SECTION_MAP = {'S': 'STARS', 'H': 'HERBAL', 'B': 'BIO', 'P': 'PHARMA',
               'C': 'COSMO', 'T': 'TEXT'}
SECTIONS = ['BIO', 'HERBAL', 'STARS', 'PHARMA', 'COSMO']

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def jsd(p_dict, q_dict, keys=None):
    """Jensen-Shannon divergence between two distributions (as dicts)."""
    if keys is None:
        keys = sorted(set(list(p_dict.keys()) + list(q_dict.keys())))
    total_p = sum(p_dict.get(k, 0) for k in keys)
    total_q = sum(q_dict.get(k, 0) for k in keys)
    if total_p == 0 or total_q == 0:
        return 1.0
    p = [p_dict.get(k, 0) / total_p for k in keys]
    q = [q_dict.get(k, 0) / total_q for k in keys]
    m = [(pi + qi) / 2 for pi, qi in zip(p, q)]
    div = 0.0
    for pi, qi, mi in zip(p, q, m):
        if pi > 0 and mi > 0:
            div += 0.5 * pi * math.log2(pi / mi)
        if qi > 0 and mi > 0:
            div += 0.5 * qi * math.log2(qi / mi)
    return div


def cosine_sim(v1, v2):
    """Cosine similarity between two vectors (as lists)."""
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def entropy(dist_dict):
    """Shannon entropy in bits."""
    total = sum(dist_dict.values())
    if total == 0:
        return 0.0
    h = 0.0
    for v in dist_dict.values():
        if v > 0:
            p = v / total
            h -= p * math.log2(p)
    return h


def get_frame(head, term, bare=False):
    """Get frame string from HEAD and TERM atoms."""
    if bare or not term:
        return f"{head}->bare"
    return f"{head}->{term}"


def chi2_independence(table):
    """Chi-squared test for independence on a 2D contingency table (dict of dicts).
    Returns chi2, dof, p_approx (using normal approx for large chi2)."""
    rows = sorted(table.keys())
    cols = sorted(set(c for r in table.values() for c in r.keys()))
    n = sum(sum(table[r].get(c, 0) for c in cols) for r in rows)
    if n == 0:
        return 0.0, 0, 1.0
    row_totals = {r: sum(table[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(table[r].get(c, 0) for r in rows) for c in cols}
    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = table[r].get(c, 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
    dof = max((len(rows) - 1) * (len(cols) - 1), 1)
    # Cramer's V
    v = math.sqrt(chi2 / (n * (min(len(rows), len(cols)) - 1))) if n > 0 and min(len(rows), len(cols)) > 1 else 0
    return chi2, dof, v


# =============================================================================
# DATA LOADING
# =============================================================================

def load_data():
    """Load Currier B tokens and decompose MIDDLEs."""
    tx = Transcript()
    morph = Morphology()
    tokens_b = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w:
            continue
        m = morph.extract(w)
        section = SECTION_MAP.get(token.section, token.section)
        tokens_b.append({
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'section': section,
            'prefix': m.prefix if m.prefix else 'BARE',
            'middle': m.middle,
            'suffix': m.suffix if m.suffix else '',
            'line_initial': token.line_initial,
            'line_final': token.line_final,
            'par_initial': token.par_initial,
            'par_final': token.par_final,
        })

    print(f"Loaded {len(tokens_b)} Currier B tokens")
    return tokens_b


def decompose_all(tokens_b):
    """Decompose all MIDDLEs and identify modifier-bearing tokens."""
    middle_decomps = {}  # middle -> (head, mods, term, frame)
    mod_tokens = []  # tokens with at least 1 modifier
    multi_mod_tokens = []  # tokens with 2+ modifiers

    for t in tokens_b:
        mid = t['middle']
        if mid not in middle_decomps:
            head, mods, term, frame = decompose_middle_hmt(mid)
            middle_decomps[mid] = (head, mods, term, frame)

        head, mods, term, frame = middle_decomps[mid]
        t['head'] = head
        t['mods'] = mods
        t['term'] = term
        t['frame'] = frame
        t['mod_set'] = set(mods) & MOD_ATOMS if mods else set()
        t['has_mod'] = len(t['mod_set']) > 0
        t['mod_count'] = len(t['mod_set'])

        if t['has_mod']:
            mod_tokens.append(t)
        if t['mod_count'] >= 2:
            multi_mod_tokens.append(t)

    print(f"MIDDLEs decomposed: {len(middle_decomps)} unique")
    print(f"Modifier-bearing tokens: {len(mod_tokens)}")
    print(f"Multi-modifier tokens: {len(multi_mod_tokens)}")
    return tokens_b, mod_tokens, multi_mod_tokens, middle_decomps


# =============================================================================
# T1: PER-MODIFIER BEHAVIORAL PROFILES
# =============================================================================

def compute_modifier_profiles(tokens_b, mod_tokens, middle_decomps):
    """Compute 6-dimensional behavioral profile for each modifier atom."""
    print("\n=== T1: Per-Modifier Behavioral Profiles ===")

    profiles = {}

    for mod in sorted(MOD_ATOMS):
        # Tokens containing this modifier
        mod_toks = [t for t in mod_tokens if mod in t['mod_set']]
        n_tokens = len(mod_toks)

        # 1. LINE POSITIONAL DISTRIBUTION
        pos_dist = Counter()
        for t in mod_toks:
            if t['line_initial']:
                pos_dist['initial'] += 1
            elif t['line_final']:
                pos_dist['final'] += 1
            else:
                pos_dist['medial'] += 1

        # 2. CATEGORY DISTRIBUTION (using atom_to_category on HEAD)
        cat_dist = Counter()
        for t in mod_toks:
            if t['head']:
                cat = ATOM_TO_CATEGORY.get(t['head'], 'UNKNOWN')
                cat_dist[cat] += 1
            else:
                cat_dist['HEADLESS'] += 1

        # 3. HEAD COMPATIBILITY
        head_dist = Counter()
        for t in mod_toks:
            if t['head']:
                head_dist[t['head']] += 1
            else:
                head_dist['HEADLESS'] += 1

        # 4. TERMINAL COMPATIBILITY
        term_dist = Counter()
        for t in mod_toks:
            if t['term']:
                term_dist[t['term']] += 1
            else:
                term_dist['BARE'] += 1

        # 5. FRAME HAZARD PROFILE
        hazard_dist = Counter()
        for t in mod_toks:
            if t['frame'] and t['frame'] in FRAME_HAZARD:
                hazard_dist[FRAME_HAZARD[t['frame']]] += 1
            else:
                hazard_dist['UNCLASSIFIED'] += 1

        # 6. SECTION DISTRIBUTION
        section_dist = Counter()
        for t in mod_toks:
            section_dist[t['section']] += 1

        # 7. FOLIO DISTRIBUTION
        folio_set = set(t['folio'] for t in mod_toks)

        # 8. PREFIX DISTRIBUTION
        prefix_dist = Counter()
        for t in mod_toks:
            prefix_dist[t['prefix']] += 1

        # 9. SUFFIX PRESENCE
        suffix_count = sum(1 for t in mod_toks if t['suffix'])
        suffix_rate = suffix_count / n_tokens if n_tokens > 0 else 0

        # 10. PARAGRAPH POSITION
        par_initial_count = sum(1 for t in mod_toks if t['par_initial'])
        par_final_count = sum(1 for t in mod_toks if t['par_final'])

        profiles[mod] = {
            'n_tokens': n_tokens,
            'n_folios': len(folio_set),
            'position': dict(pos_dist),
            'category': dict(cat_dist),
            'head': dict(head_dist),
            'terminal': dict(term_dist),
            'frame_hazard': dict(hazard_dist),
            'section': dict(section_dist),
            'prefix_top5': dict(prefix_dist.most_common(5)),
            'suffix_rate': round(suffix_rate, 4),
            'par_initial_rate': round(par_initial_count / n_tokens, 4) if n_tokens > 0 else 0,
            'par_final_rate': round(par_final_count / n_tokens, 4) if n_tokens > 0 else 0,
        }

        print(f"\n  {mod}: {n_tokens} tokens, {len(folio_set)} folios")
        print(f"    Position: {dict(pos_dist)}")
        print(f"    Category (via HEAD): {dict(cat_dist)}")
        print(f"    HEAD: {dict(head_dist)}")
        print(f"    TERM: {dict(term_dist)}")
        print(f"    Hazard: {dict(hazard_dist)}")
        print(f"    Suffix rate: {suffix_rate:.3f}")

    return profiles


# =============================================================================
# T2: MODIFIER PAIR BEHAVIORAL SIMILARITY
# =============================================================================

def compute_pair_similarity(profiles):
    """Compute JSD between all modifier pairs across multiple dimensions."""
    print("\n=== T2: Modifier Pair Behavioral Similarity ===")

    dimensions = ['category', 'head', 'terminal', 'frame_hazard', 'section', 'position']
    pair_jsd = {}

    mods = sorted(MOD_ATOMS)
    for i, m1 in enumerate(mods):
        for m2 in mods[i+1:]:
            pair_key = f"{m1}-{m2}"
            dim_jsds = {}
            for dim in dimensions:
                d1 = profiles[m1][dim]
                d2 = profiles[m2][dim]
                dim_jsds[dim] = round(jsd(d1, d2), 4)
            mean_jsd = round(sum(dim_jsds.values()) / len(dim_jsds), 4)
            dim_jsds['mean'] = mean_jsd
            pair_jsd[pair_key] = dim_jsds

    # Print sorted by mean JSD
    sorted_pairs = sorted(pair_jsd.items(), key=lambda x: x[1]['mean'])
    print("\n  Pair similarity (sorted by mean JSD, lower = more similar):")
    for pair, jsds in sorted_pairs:
        is_empty = frozenset(pair.split('-')) in EMPTY_PAIRS
        marker = " [AVOID]" if is_empty else " [CO-OC]"
        print(f"    {pair}: mean={jsds['mean']:.4f}{marker}")
        for dim in dimensions:
            print(f"      {dim}: {jsds[dim]:.4f}")

    return pair_jsd


# =============================================================================
# T3: AVOIDANCE vs CO-OCCURRENCE GROUP COHERENCE
# =============================================================================

def test_group_coherence(pair_jsd):
    """Test whether avoiding pairs are more similar or less similar than co-occurring pairs."""
    print("\n=== T3: Avoidance vs Co-occurrence Group Coherence ===")

    avoid_jsds = []
    cooc_jsds = []

    for pair_key, jsds in pair_jsd.items():
        pair_set = frozenset(pair_key.split('-'))
        if pair_set in EMPTY_PAIRS:
            avoid_jsds.append(jsds['mean'])
        elif pair_set in COOCCURRING_PAIRS:
            cooc_jsds.append(jsds['mean'])

    mean_avoid = sum(avoid_jsds) / len(avoid_jsds) if avoid_jsds else 0
    mean_cooc = sum(cooc_jsds) / len(cooc_jsds) if cooc_jsds else 0

    print(f"\n  Avoiding pairs (n={len(avoid_jsds)}): mean JSD = {mean_avoid:.4f}")
    print(f"    Values: {[round(v, 4) for v in sorted(avoid_jsds)]}")
    print(f"  Co-occurring pairs (n={len(cooc_jsds)}): mean JSD = {mean_cooc:.4f}")
    print(f"    Values: {[round(v, 4) for v in sorted(cooc_jsds)]}")

    if mean_avoid < mean_cooc:
        print(f"\n  RESULT: Avoiding pairs are MORE SIMILAR (ratio {mean_cooc/mean_avoid:.2f}x)")
        print(f"  -> Supports Hypothesis B: avoidance = functional REDUNDANCY")
        verdict_b = 'SUPPORTED'
    elif mean_avoid > mean_cooc:
        print(f"\n  RESULT: Avoiding pairs are LESS SIMILAR (ratio {mean_avoid/mean_cooc:.2f}x)")
        print(f"  -> Supports Hypothesis C: avoidance = incompatible CONTEXTS")
        verdict_b = 'REJECTED'
    else:
        print(f"\n  RESULT: No difference")
        verdict_b = 'NULL'

    # Per-dimension comparison
    dimensions = ['category', 'head', 'terminal', 'frame_hazard', 'section', 'position']
    dim_verdicts = {}
    for dim in dimensions:
        avoid_dim = []
        cooc_dim = []
        for pair_key, jsds in pair_jsd.items():
            pair_set = frozenset(pair_key.split('-'))
            if pair_set in EMPTY_PAIRS:
                avoid_dim.append(jsds[dim])
            elif pair_set in COOCCURRING_PAIRS:
                cooc_dim.append(jsds[dim])
        mean_a = sum(avoid_dim) / len(avoid_dim) if avoid_dim else 0
        mean_c = sum(cooc_dim) / len(cooc_dim) if cooc_dim else 0
        ratio = mean_a / mean_c if mean_c > 0 else float('inf')
        direction = 'AVOID_MORE_SIMILAR' if ratio < 1 else 'COOC_MORE_SIMILAR' if ratio > 1 else 'EQUAL'
        dim_verdicts[dim] = {
            'avoid_mean': round(mean_a, 4),
            'cooc_mean': round(mean_c, 4),
            'ratio': round(ratio, 4),
            'direction': direction
        }
        print(f"    {dim}: avoid={mean_a:.4f} cooc={mean_c:.4f} ratio={ratio:.3f} -> {direction}")

    return {
        'avoid_mean_jsd': round(mean_avoid, 4),
        'cooc_mean_jsd': round(mean_cooc, 4),
        'verdict_b': verdict_b,
        'per_dimension': dim_verdicts
    }


# =============================================================================
# T4: HYPOTHESIS A - {p,f,i} vs {c,d} vs {s}
# =============================================================================

def test_hypothesis_a(profiles, pair_jsd):
    """Test whether {p,f,i}, {c,d}, and {s} form coherent behavioral groups."""
    print("\n=== T4: Hypothesis A - {p,f,i} vs {c,d} vs {s} ===")

    # Within-group similarity
    pfi_pairs = ['f-p', 'i-p', 'f-i']
    cd_pairs = ['c-d']

    # Normalize pair keys (sort alphabetically)
    def normalize_pair(m1, m2):
        return '-'.join(sorted([m1, m2]))

    pfi_jsds = [pair_jsd[normalize_pair(p.split('-')[0], p.split('-')[1])]['mean']
                for p in pfi_pairs if normalize_pair(p.split('-')[0], p.split('-')[1]) in pair_jsd]
    cd_jsds = [pair_jsd[normalize_pair('c', 'd')]['mean']]

    # Between-group similarity
    between_pairs = []
    for m1 in GROUP_PFI:
        for m2 in GROUP_CD:
            key = normalize_pair(m1, m2)
            if key in pair_jsd:
                between_pairs.append(pair_jsd[key]['mean'])

    # s-to-each-group
    s_to_pfi = [pair_jsd[normalize_pair('s', m)]['mean'] for m in GROUP_PFI
                if normalize_pair('s', m) in pair_jsd]
    s_to_cd = [pair_jsd[normalize_pair('s', m)]['mean'] for m in GROUP_CD
               if normalize_pair('s', m) in pair_jsd]

    mean_pfi = sum(pfi_jsds) / len(pfi_jsds) if pfi_jsds else 0
    mean_cd = sum(cd_jsds) / len(cd_jsds) if cd_jsds else 0
    mean_between = sum(between_pairs) / len(between_pairs) if between_pairs else 0
    mean_s_pfi = sum(s_to_pfi) / len(s_to_pfi) if s_to_pfi else 0
    mean_s_cd = sum(s_to_cd) / len(s_to_cd) if s_to_cd else 0

    print(f"\n  Within {list(GROUP_PFI)} mean JSD: {mean_pfi:.4f} (n={len(pfi_jsds)})")
    print(f"    {pfi_jsds}")
    print(f"  Within {list(GROUP_CD)} mean JSD: {mean_cd:.4f} (n={len(cd_jsds)})")
    print(f"  Between groups mean JSD: {mean_between:.4f} (n={len(between_pairs)})")
    print(f"  s to {{p,f,i}} mean JSD: {mean_s_pfi:.4f}")
    print(f"  s to {{c,d}} mean JSD: {mean_s_cd:.4f}")

    # Hypothesis A passes if within-group < between-group
    within_mean = (mean_pfi * len(pfi_jsds) + mean_cd * len(cd_jsds)) / (len(pfi_jsds) + len(cd_jsds)) if (len(pfi_jsds) + len(cd_jsds)) > 0 else 0
    separation = mean_between / within_mean if within_mean > 0 else 0

    verdict = 'SUPPORTED' if separation > 1.2 else 'WEAK' if separation > 1.0 else 'REJECTED'
    print(f"\n  Within-group mean: {within_mean:.4f}")
    print(f"  Between-group mean: {mean_between:.4f}")
    print(f"  Separation ratio: {separation:.3f}")
    print(f"  Verdict: {verdict}")

    # Check if s is equidistant or biased
    s_bias = 'PFI' if mean_s_pfi < mean_s_cd else 'CD' if mean_s_cd < mean_s_pfi else 'EQUIDISTANT'
    print(f"  s bias: {s_bias} (closer to {s_bias if s_bias != 'EQUIDISTANT' else 'neither'})")

    return {
        'within_pfi_mean': round(mean_pfi, 4),
        'within_cd_mean': round(mean_cd, 4),
        'between_mean': round(mean_between, 4),
        's_to_pfi': round(mean_s_pfi, 4),
        's_to_cd': round(mean_s_cd, 4),
        'separation_ratio': round(separation, 3),
        'verdict': verdict,
        's_bias': s_bias
    }


# =============================================================================
# T5-T6: REDUNDANCY vs INCOMPATIBILITY
# =============================================================================

def test_redundancy_vs_incompatibility(profiles, mod_tokens):
    """Test whether avoiding modifiers are functionally redundant or contextually incompatible."""
    print("\n=== T5-T6: Redundancy vs Incompatibility ===")

    # For each modifier, compute its operational domain vector
    # Domain = normalized (HEAD_dist, TERM_dist, section_dist)
    # If redundant: avoiding pairs have SAME domain
    # If incompatible: avoiding pairs have DIFFERENT domains

    # Also test: do avoiding modifiers appear in the SAME folios or DIFFERENT folios?
    mod_folios = {}
    for mod in sorted(MOD_ATOMS):
        mod_toks = [t for t in mod_tokens if mod in t['mod_set']]
        mod_folios[mod] = set(t['folio'] for t in mod_toks)

    # Jaccard similarity of folio sets
    print("\n  Folio overlap (Jaccard):")
    folio_jaccards = {}
    for m1 in sorted(MOD_ATOMS):
        for m2 in sorted(MOD_ATOMS):
            if m1 >= m2:
                continue
            pair_key = f"{m1}-{m2}"
            intersection = len(mod_folios[m1] & mod_folios[m2])
            union = len(mod_folios[m1] | mod_folios[m2])
            jacc = intersection / union if union > 0 else 0
            folio_jaccards[pair_key] = round(jacc, 4)
            is_empty = frozenset({m1, m2}) in EMPTY_PAIRS
            marker = " [AVOID]" if is_empty else " [CO-OC]"
            print(f"    {pair_key}: {jacc:.4f}{marker}")

    # Mean folio Jaccard for avoid vs co-occur
    avoid_folio_jacc = [folio_jaccards[f"{min(a,b)}-{max(a,b)}"]
                        for a, b in [(list(p)[0], list(p)[1]) for p in EMPTY_PAIRS]
                        if f"{min(a,b)}-{max(a,b)}" in folio_jaccards]
    cooc_folio_jacc = [folio_jaccards[f"{min(a,b)}-{max(a,b)}"]
                       for a, b in [(list(p)[0], list(p)[1]) for p in COOCCURRING_PAIRS]
                       if f"{min(a,b)}-{max(a,b)}" in folio_jaccards]

    mean_avoid_folio = sum(avoid_folio_jacc) / len(avoid_folio_jacc) if avoid_folio_jacc else 0
    mean_cooc_folio = sum(cooc_folio_jacc) / len(cooc_folio_jacc) if cooc_folio_jacc else 0

    print(f"\n  Avoid pairs mean folio Jaccard: {mean_avoid_folio:.4f}")
    print(f"  Co-occur pairs mean folio Jaccard: {mean_cooc_folio:.4f}")

    if mean_avoid_folio > mean_cooc_folio:
        folio_verdict = 'SAME_CONTEXT'
        print(f"  -> Avoiding pairs in SAME folios (redundancy model)")
    else:
        folio_verdict = 'DIFFERENT_CONTEXT'
        print(f"  -> Avoiding pairs in DIFFERENT folios (incompatibility model)")

    # HEAD overlap: do avoiding pairs attach to same or different HEADs?
    mod_heads = {}
    for mod in sorted(MOD_ATOMS):
        mod_toks = [t for t in mod_tokens if mod in t['mod_set']]
        mod_heads[mod] = Counter(t['head'] for t in mod_toks if t['head'])

    print("\n  HEAD overlap (Jaccard of HEAD sets):")
    head_jaccards = {}
    for m1 in sorted(MOD_ATOMS):
        for m2 in sorted(MOD_ATOMS):
            if m1 >= m2:
                continue
            pair_key = f"{m1}-{m2}"
            s1 = set(mod_heads[m1].keys())
            s2 = set(mod_heads[m2].keys())
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            jacc = intersection / union if union > 0 else 0
            head_jaccards[pair_key] = round(jacc, 4)

    avoid_head_jacc = [head_jaccards[f"{min(a,b)}-{max(a,b)}"]
                       for a, b in [(list(p)[0], list(p)[1]) for p in EMPTY_PAIRS]
                       if f"{min(a,b)}-{max(a,b)}" in head_jaccards]
    cooc_head_jacc = [head_jaccards[f"{min(a,b)}-{max(a,b)}"]
                      for a, b in [(list(p)[0], list(p)[1]) for p in COOCCURRING_PAIRS]
                      if f"{min(a,b)}-{max(a,b)}" in head_jaccards]

    mean_avoid_head = sum(avoid_head_jacc) / len(avoid_head_jacc) if avoid_head_jacc else 0
    mean_cooc_head = sum(cooc_head_jacc) / len(cooc_head_jacc) if cooc_head_jacc else 0

    print(f"\n  Avoid pairs mean HEAD Jaccard: {mean_avoid_head:.4f}")
    print(f"  Co-occur pairs mean HEAD Jaccard: {mean_cooc_head:.4f}")

    if mean_avoid_head > mean_cooc_head:
        head_verdict = 'SAME_HEADS'
        print(f"  -> Avoiding pairs use SAME HEADs (redundancy model)")
    else:
        head_verdict = 'DIFFERENT_HEADS'
        print(f"  -> Avoiding pairs use DIFFERENT HEADs (incompatibility model)")

    return {
        'folio_jaccards': folio_jaccards,
        'avoid_folio_mean': round(mean_avoid_folio, 4),
        'cooc_folio_mean': round(mean_cooc_folio, 4),
        'folio_verdict': folio_verdict,
        'head_jaccards': head_jaccards,
        'avoid_head_mean': round(mean_avoid_head, 4),
        'cooc_head_mean': round(mean_cooc_head, 4),
        'head_verdict': head_verdict,
    }


# =============================================================================
# T7: s UNIVERSALITY MECHANISM
# =============================================================================

def test_s_universality(profiles, mod_tokens, pair_jsd):
    """Test why s can co-occur with all other modifiers."""
    print("\n=== T7: s Universality Mechanism ===")

    # s co-occurs with ALL 5 other modifiers. Why?
    # Hypothesis: s occupies a unique behavioral niche that complements all others

    s_profile = profiles['s']
    other_mods = sorted(MOD_ATOMS - {'s'})

    # How similar is s to each other modifier?
    s_distances = {}
    for m in other_mods:
        key = '-'.join(sorted(['s', m]))
        s_distances[m] = pair_jsd[key]['mean']
        print(f"  s-{m} JSD: {pair_jsd[key]['mean']:.4f}")

    # Is s the most dissimilar from all others? (universal compatibility through uniqueness)
    mean_s_dist = sum(s_distances.values()) / len(s_distances)
    other_mean_dists = {}
    for m in other_mods:
        dists = []
        for m2 in other_mods:
            if m2 != m:
                key = '-'.join(sorted([m, m2]))
                if key in pair_jsd:
                    dists.append(pair_jsd[key]['mean'])
        other_mean_dists[m] = sum(dists) / len(dists) if dists else 0

    print(f"\n  Mean distance from s to all others: {mean_s_dist:.4f}")
    for m, d in sorted(other_mean_dists.items()):
        print(f"  Mean distance from {m} to non-{m} others: {d:.4f}")

    # s section distribution - is it more uniform?
    s_section_entropy = entropy(profiles['s']['section'])
    other_section_entropies = {m: entropy(profiles[m]['section']) for m in other_mods}

    print(f"\n  Section entropy:")
    print(f"    s: {s_section_entropy:.3f}")
    for m, e in sorted(other_section_entropies.items()):
        print(f"    {m}: {e:.3f}")

    # s HEAD entropy - does s combine with more diverse HEADs?
    s_head_entropy = entropy(profiles['s']['head'])
    other_head_entropies = {m: entropy(profiles[m]['head']) for m in other_mods}

    print(f"\n  HEAD entropy:")
    print(f"    s: {s_head_entropy:.3f}")
    for m, e in sorted(other_head_entropies.items()):
        print(f"    {m}: {e:.3f}")

    # s position - does s have unique position preference?
    s_pos = profiles['s']['position']
    print(f"\n  s position distribution: {s_pos}")

    mechanism = []
    if mean_s_dist > max(other_mean_dists.values()):
        mechanism.append('MAXIMAL_DISTANCE')
    if s_head_entropy > max(other_head_entropies.values()):
        mechanism.append('BROADEST_HEAD_RANGE')
    if s_section_entropy > max(other_section_entropies.values()):
        mechanism.append('BROADEST_SECTION_RANGE')

    # Check s FQ macro-state (from C1391)
    # s is 64.6% FQ (3.59x) - NOT AXM-confined
    # While p,c are AXM-confined (88.7% and 93.5%)
    # This means s operates in a DIFFERENT execution context
    mechanism.append('FQ_MACRO_STATE')  # s operates in cycling, others in main loop

    print(f"\n  s universality mechanisms: {mechanism}")

    return {
        's_distances': {k: round(v, 4) for k, v in s_distances.items()},
        'mean_s_distance': round(mean_s_dist, 4),
        'other_mean_distances': {k: round(v, 4) for k, v in other_mean_dists.items()},
        's_section_entropy': round(s_section_entropy, 3),
        'other_section_entropies': {k: round(v, 3) for k, v in other_section_entropies.items()},
        's_head_entropy': round(s_head_entropy, 3),
        'other_head_entropies': {k: round(v, 3) for k, v in other_head_entropies.items()},
        'mechanisms': mechanism,
    }


# =============================================================================
# T8-T9: HEAD AND TERMINAL COMPATIBILITY
# =============================================================================

def test_head_term_compatibility(profiles, mod_tokens):
    """Test modifier-HEAD and modifier-TERMINAL compatibility patterns."""
    print("\n=== T8-T9: HEAD and TERMINAL Compatibility ===")

    # For each modifier, what HEAD atoms does it attach to?
    # Compute chi-squared for modifier x HEAD independence
    mod_head_table = {}
    mod_term_table = {}

    for mod in sorted(MOD_ATOMS):
        mod_toks = [t for t in mod_tokens if mod in t['mod_set']]
        mod_head_table[mod] = Counter(t['head'] for t in mod_toks if t['head'])
        mod_term_table[mod] = Counter(t['term'] for t in mod_toks if t['term'])

    # Chi-squared: modifier x HEAD
    chi2_head, dof_head, v_head = chi2_independence(
        {m: dict(mod_head_table[m]) for m in sorted(MOD_ATOMS)})
    print(f"\n  Modifier x HEAD: chi2={chi2_head:.1f}, V={v_head:.3f}")

    # Chi-squared: modifier x TERMINAL
    chi2_term, dof_term, v_term = chi2_independence(
        {m: dict(mod_term_table[m]) for m in sorted(MOD_ATOMS)})
    print(f"  Modifier x TERMINAL: chi2={chi2_term:.1f}, V={v_term:.3f}")

    # Print HEAD profiles
    print("\n  HEAD profiles (% within modifier):")
    for mod in sorted(MOD_ATOMS):
        total = sum(mod_head_table[mod].values())
        if total > 0:
            pcts = {h: f"{c/total*100:.1f}%" for h, c in sorted(mod_head_table[mod].items())}
            print(f"    {mod}: {pcts} (n={total})")

    # Print TERMINAL profiles
    print("\n  TERMINAL profiles (% within modifier):")
    for mod in sorted(MOD_ATOMS):
        total = sum(mod_term_table[mod].values())
        if total > 0:
            pcts = {t: f"{c/total*100:.1f}%" for t, c in sorted(mod_term_table[mod].items())}
            print(f"    {mod}: {pcts} (n={total})")

    # Do avoiding pairs have more similar or different HEAD profiles?
    # Already computed in T5-T6, but let's do HEAD JSD specifically
    head_jsds_avoid = []
    head_jsds_cooc = []
    for m1 in sorted(MOD_ATOMS):
        for m2 in sorted(MOD_ATOMS):
            if m1 >= m2:
                continue
            j = jsd(dict(mod_head_table[m1]), dict(mod_head_table[m2]),
                     keys=sorted(HEAD_ATOMS | {'HEADLESS'}))
            pair_set = frozenset({m1, m2})
            if pair_set in EMPTY_PAIRS:
                head_jsds_avoid.append(j)
            elif pair_set in COOCCURRING_PAIRS:
                head_jsds_cooc.append(j)

    mean_avoid_head_jsd = sum(head_jsds_avoid) / len(head_jsds_avoid) if head_jsds_avoid else 0
    mean_cooc_head_jsd = sum(head_jsds_cooc) / len(head_jsds_cooc) if head_jsds_cooc else 0

    print(f"\n  HEAD JSD: avoid={mean_avoid_head_jsd:.4f} cooc={mean_cooc_head_jsd:.4f}")

    # TERMINAL JSD
    term_jsds_avoid = []
    term_jsds_cooc = []
    for m1 in sorted(MOD_ATOMS):
        for m2 in sorted(MOD_ATOMS):
            if m1 >= m2:
                continue
            j = jsd(dict(mod_term_table[m1]), dict(mod_term_table[m2]),
                     keys=sorted(TERM_ATOMS | {'BARE'}))
            pair_set = frozenset({m1, m2})
            if pair_set in EMPTY_PAIRS:
                term_jsds_avoid.append(j)
            elif pair_set in COOCCURRING_PAIRS:
                term_jsds_cooc.append(j)

    mean_avoid_term_jsd = sum(term_jsds_avoid) / len(term_jsds_avoid) if term_jsds_avoid else 0
    mean_cooc_term_jsd = sum(term_jsds_cooc) / len(term_jsds_cooc) if term_jsds_cooc else 0

    print(f"  TERM JSD: avoid={mean_avoid_term_jsd:.4f} cooc={mean_cooc_term_jsd:.4f}")

    return {
        'chi2_head': round(chi2_head, 1),
        'v_head': round(v_head, 3),
        'chi2_term': round(chi2_term, 1),
        'v_term': round(v_term, 3),
        'head_profiles': {m: dict(mod_head_table[m]) for m in sorted(MOD_ATOMS)},
        'term_profiles': {m: dict(mod_term_table[m]) for m in sorted(MOD_ATOMS)},
        'avoid_head_jsd': round(mean_avoid_head_jsd, 4),
        'cooc_head_jsd': round(mean_cooc_head_jsd, 4),
        'avoid_term_jsd': round(mean_avoid_term_jsd, 4),
        'cooc_term_jsd': round(mean_cooc_term_jsd, 4),
    }


# =============================================================================
# T10: CATEGORY-LEVEL GROUPING ALIGNMENT
# =============================================================================

def test_category_alignment(profiles):
    """Test whether avoidance groups align with operational category boundaries."""
    print("\n=== T10: Category-Level Grouping Alignment ===")

    # Category labels from existing constraints
    known_categories = {
        'p': 'MARKING',   # C1390: 12.033x, #1
        'f': 'MARKING',   # C1392: 12.009x, #2
        'c': 'MARKING',   # C1389: MONITORING 12.237x but also adjust/main-loop
        'd': 'MARKING',   # C1397: CONTAINMENT 84% via headless
        'i': 'STAGING',   # C1452: STAGING, frame selector
        's': 'STAGING',   # C1391: STAGING 6.721x, #1
    }

    # From C1397 headless compound grammar (d/i as pseudo-HEAD):
    headless_categories = {
        'd': 'CONTAINMENT',  # 84%
        'i': 'STAGING',      # 66%
        'p': 'MARKING',      # 92%
        'f': 'MARKING',      # 91%
    }

    print("\n  Atom category assignments:")
    for mod in sorted(MOD_ATOMS):
        cat = known_categories.get(mod, '?')
        headless = headless_categories.get(mod, 'N/A')
        print(f"    {mod}: atom_cat={cat}, headless_cat={headless}")

    # Does avoidance correspond to SAME category?
    # {p,f} avoid each other AND are both MARKING -> SAME category avoidance
    # {p,c} avoid AND both MARKING -> SAME category avoidance
    # {p,d} avoid: p=MARKING, d=CONTAINMENT(headless) -> DIFFERENT
    # {p,i} avoid: p=MARKING, i=STAGING -> DIFFERENT
    # {f,c} avoid: f=MARKING, c=MARKING -> SAME
    # {f,d} avoid: f=MARKING, d=CONTAINMENT -> DIFFERENT
    # {i,c} avoid: i=STAGING, c=MARKING -> DIFFERENT
    # {i,d} avoid: i=STAGING, d=CONTAINMENT -> DIFFERENT

    # Using headless categories for d,i,p,f
    same_cat_avoid = 0
    diff_cat_avoid = 0
    for pair in EMPTY_PAIRS:
        mods = list(pair)
        c1 = headless_categories.get(mods[0], known_categories.get(mods[0], '?'))
        c2 = headless_categories.get(mods[1], known_categories.get(mods[1], '?'))
        if c1 == c2:
            same_cat_avoid += 1
            print(f"    AVOID {mods[0]}-{mods[1]}: SAME ({c1})")
        else:
            diff_cat_avoid += 1
            print(f"    AVOID {mods[0]}-{mods[1]}: DIFFERENT ({c1} vs {c2})")

    same_cat_cooc = 0
    diff_cat_cooc = 0
    for pair in COOCCURRING_PAIRS:
        mods = list(pair)
        c1 = headless_categories.get(mods[0], known_categories.get(mods[0], '?'))
        c2 = headless_categories.get(mods[1], known_categories.get(mods[1], '?'))
        if c1 == c2:
            same_cat_cooc += 1
        else:
            diff_cat_cooc += 1

    print(f"\n  Avoiding pairs: {same_cat_avoid} same-category, {diff_cat_avoid} different-category")
    print(f"  Co-occurring pairs: {same_cat_cooc} same-category, {diff_cat_cooc} different-category")

    # If avoidance = redundancy, we'd expect high same-category in avoid
    avoid_same_rate = same_cat_avoid / (same_cat_avoid + diff_cat_avoid) if (same_cat_avoid + diff_cat_avoid) > 0 else 0
    cooc_same_rate = same_cat_cooc / (same_cat_cooc + diff_cat_cooc) if (same_cat_cooc + diff_cat_cooc) > 0 else 0

    print(f"\n  Avoid same-category rate: {avoid_same_rate:.2%}")
    print(f"  Co-occur same-category rate: {cooc_same_rate:.2%}")

    # Alternative: use MARKING vs non-MARKING as key distinction
    marking_mods = {'p', 'f', 'c'}  # all MARKING-associated
    non_marking_mods = {'d', 'i', 's'}  # d=CONTAINMENT(headless), i=STAGING, s=STAGING

    # Do avoidance pairs cross this boundary?
    cross_boundary = 0
    within_boundary = 0
    for pair in EMPTY_PAIRS:
        mods = list(pair)
        m_in = [m in marking_mods for m in mods]
        if m_in[0] != m_in[1]:
            cross_boundary += 1
        else:
            within_boundary += 1

    print(f"\n  MARKING vs non-MARKING boundary crossing:")
    print(f"    Avoid pairs crossing: {cross_boundary}/8")
    print(f"    Avoid pairs within: {within_boundary}/8")

    return {
        'known_categories': known_categories,
        'headless_categories': headless_categories,
        'avoid_same_category': same_cat_avoid,
        'avoid_diff_category': diff_cat_avoid,
        'cooc_same_category': same_cat_cooc,
        'cooc_diff_category': diff_cat_cooc,
        'avoid_same_rate': round(avoid_same_rate, 4),
        'cooc_same_rate': round(cooc_same_rate, 4),
        'marking_cross_boundary': cross_boundary,
        'marking_within_boundary': within_boundary,
    }


# =============================================================================
# ADDITIONAL: MULTI-MODIFIER COMPOUND ANALYSIS
# =============================================================================

def analyze_multi_modifier_compounds(multi_mod_tokens, middle_decomps):
    """Analyze the actual multi-modifier compounds to understand grouping."""
    print("\n=== MULTI-MODIFIER COMPOUND ANALYSIS ===")

    # For each co-occurring pair, what MIDDLEs contain them?
    pair_middles = defaultdict(Counter)
    for t in multi_mod_tokens:
        mid = t['middle']
        mods_present = t['mod_set']
        for m1 in sorted(mods_present):
            for m2 in sorted(mods_present):
                if m1 < m2:
                    pair_middles[f"{m1}+{m2}"][mid] += 1

    print("\n  Co-occurring pairs and their MIDDLEs:")
    for pair_key in sorted(pair_middles.keys()):
        middles = pair_middles[pair_key]
        total = sum(middles.values())
        top5 = middles.most_common(5)
        print(f"    {pair_key}: {total} tokens, {len(middles)} types")
        for mid, count in top5:
            head, mods, term, frame = middle_decomps.get(mid, (None, None, None, None))
            print(f"      {mid} ({count}x) -> H:{head} M:{mods} T:{term}")

    # Compound size distribution by pair
    pair_summaries = {}
    for pair_key, middles in sorted(pair_middles.items()):
        total = sum(middles.values())
        n_types = len(middles)
        # Average MIDDLE length
        mean_len = sum(len(mid) * count for mid, count in middles.items()) / total if total > 0 else 0
        pair_summaries[pair_key] = {
            'total_tokens': total,
            'unique_types': n_types,
            'mean_middle_length': round(mean_len, 2),
            'top_middles': [(mid, count) for mid, count in middles.most_common(3)]
        }

    return pair_summaries


# =============================================================================
# SYNTHESIS
# =============================================================================

def synthesize(profiles, pair_jsd, coherence, hyp_a, redund, s_universal, compat, cat_align, pair_summaries):
    """Synthesize all findings into a verdict."""
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # 1. Overall grouping verdict
    print("\n1. GROUPING STRUCTURE:")
    print(f"   Hypothesis A ({list(GROUP_PFI)} vs {list(GROUP_CD)} vs s): {hyp_a['verdict']}")
    print(f"   Separation ratio: {hyp_a['separation_ratio']:.3f}")

    # 2. Avoidance mechanism
    print(f"\n2. AVOIDANCE MECHANISM:")
    print(f"   Hypothesis B (redundancy): {coherence['verdict_b']}")
    print(f"   Avoid pairs mean JSD: {coherence['avoid_mean_jsd']:.4f}")
    print(f"   Co-occur pairs mean JSD: {coherence['cooc_mean_jsd']:.4f}")
    print(f"   Folio overlap: avoid={redund['avoid_folio_mean']:.4f} cooc={redund['cooc_folio_mean']:.4f}")
    print(f"   HEAD overlap: avoid={redund['avoid_head_mean']:.4f} cooc={redund['cooc_head_mean']:.4f}")

    # 3. Category alignment
    print(f"\n3. CATEGORY ALIGNMENT:")
    print(f"   Avoid same-cat rate: {cat_align['avoid_same_rate']:.2%}")
    print(f"   Co-occur same-cat rate: {cat_align['cooc_same_rate']:.2%}")
    print(f"   MARKING boundary crossing: {cat_align['marking_cross_boundary']}/8")

    # 4. s universality
    print(f"\n4. s UNIVERSALITY:")
    print(f"   Mechanisms: {s_universal['mechanisms']}")
    print(f"   Mean distance to others: {s_universal['mean_s_distance']:.4f}")

    # 5. HEAD/TERM compatibility
    print(f"\n5. HEAD/TERM COMPATIBILITY:")
    print(f"   Modifier x HEAD: V={compat['v_head']:.3f}")
    print(f"   Modifier x TERM: V={compat['v_term']:.3f}")
    print(f"   HEAD JSD: avoid={compat['avoid_head_jsd']:.4f} cooc={compat['cooc_head_jsd']:.4f}")
    print(f"   TERM JSD: avoid={compat['avoid_term_jsd']:.4f} cooc={compat['cooc_term_jsd']:.4f}")

    # Determine overall verdict
    verdicts = {
        'grouping': hyp_a['verdict'],
        'mechanism': coherence['verdict_b'],
        'folio_context': redund['folio_verdict'],
        'head_context': redund['head_verdict'],
    }

    # Count evidence directions
    redundancy_evidence = 0
    incompatibility_evidence = 0

    if coherence['avoid_mean_jsd'] < coherence['cooc_mean_jsd']:
        redundancy_evidence += 1
    else:
        incompatibility_evidence += 1

    if redund['folio_verdict'] == 'SAME_CONTEXT':
        redundancy_evidence += 1
    else:
        incompatibility_evidence += 1

    if redund['head_verdict'] == 'SAME_HEADS':
        redundancy_evidence += 1
    else:
        incompatibility_evidence += 1

    if cat_align['avoid_same_rate'] > 0.5:
        redundancy_evidence += 1
    else:
        incompatibility_evidence += 1

    if compat['avoid_head_jsd'] < compat['cooc_head_jsd']:
        redundancy_evidence += 1
    else:
        incompatibility_evidence += 1

    print(f"\n6. OVERALL EVIDENCE:")
    print(f"   Redundancy signals: {redundancy_evidence}/5")
    print(f"   Incompatibility signals: {incompatibility_evidence}/5")

    if redundancy_evidence >= 4:
        overall = 'REDUNDANCY_DOMINANT'
    elif incompatibility_evidence >= 4:
        overall = 'INCOMPATIBILITY_DOMINANT'
    else:
        overall = 'MIXED'

    print(f"   OVERALL VERDICT: {overall}")

    return {
        'verdicts': verdicts,
        'redundancy_evidence': redundancy_evidence,
        'incompatibility_evidence': incompatibility_evidence,
        'overall': overall,
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Phase 532: Modifier Functional Grouping Analysis")
    print("=" * 60)

    # Load data
    tokens_b = load_data()
    tokens_b, mod_tokens, multi_mod_tokens, middle_decomps = decompose_all(tokens_b)

    # T1: Per-modifier profiles
    profiles = compute_modifier_profiles(tokens_b, mod_tokens, middle_decomps)

    # T2: Pair similarity
    pair_jsd = compute_pair_similarity(profiles)

    # T3: Group coherence
    coherence = test_group_coherence(pair_jsd)

    # T4: Hypothesis A
    hyp_a = test_hypothesis_a(profiles, pair_jsd)

    # T5-T6: Redundancy vs incompatibility
    redund = test_redundancy_vs_incompatibility(profiles, mod_tokens)

    # T7: s universality
    s_universal = test_s_universality(profiles, mod_tokens, pair_jsd)

    # T8-T9: HEAD/TERM compatibility
    compat = test_head_term_compatibility(profiles, mod_tokens)

    # T10: Category alignment
    cat_align = test_category_alignment(profiles)

    # Multi-modifier compounds
    pair_summaries = analyze_multi_modifier_compounds(multi_mod_tokens, middle_decomps)

    # Synthesis
    synthesis = synthesize(profiles, pair_jsd, coherence, hyp_a, redund, s_universal, compat, cat_align, pair_summaries)

    # Save results
    results = {
        'phase': 532,
        'title': 'Modifier Functional Grouping Analysis',
        'token_counts': {
            'total_b': len(tokens_b),
            'modifier_bearing': len(mod_tokens),
            'multi_modifier': len(multi_mod_tokens),
        },
        'profiles': profiles,
        'pair_similarity': pair_jsd,
        'coherence': coherence,
        'hypothesis_a': hyp_a,
        'redundancy_incompatibility': redund,
        's_universality': s_universal,
        'head_term_compatibility': compat,
        'category_alignment': cat_align,
        'pair_compound_summaries': {k: {kk: vv for kk, vv in v.items() if kk != 'top_middles'}
                                    for k, v in pair_summaries.items()},
        'synthesis': synthesis,
    }

    output_path = RESULTS_DIR / 'modifier_functional_grouping.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")
    return results


if __name__ == '__main__':
    main()

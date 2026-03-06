#!/usr/bin/env python3
"""
Phase 538: Cross-Layer Atom Decomposition — Bridge vs Dark Pipeline

RESEARCH QUESTION: Is the HEAD+MOD*+TERM atom grammar (C1393-C1395) a
manuscript-wide substrate, or merely a B-local refinement? Do bridge MIDDLEs
(85, cross-system backbone) and dark pipeline MIDDLEs (300+, identification
substrate) show different atom profiles at the HEAD/MOD/TERM level?

Expert predictions:
  P1: Bridge enriched in e/k/t HEADs (executable backbone)
  P2: Dark enriched in o-HEAD and headless (identification substrate)
  P3: Dark prefers transparent/channeled terminals (h, n, y)
  P4: Bridge tolerates more locked terminals (m, r)
  P5: Dark = same atoms, different slot proportions (non-executable nominalization)

Key references:
  C1141: Dark pipeline built from bridge atoms at 96.5% coverage
  C1176: Dark hyper-modulation is atom-selection dominated
  C1264/C1347/C1349: Bridge and dark are categorically different
  C1395: Manuscript-wide HEAD+MOD*+TERM slot grammar
  C1475-C1479: HEAD domain taxonomy
  C1483-C1487: TERMINAL taxonomy
  C1488-C1493: Headless compound subgrammar
"""

import sys, json, os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import math

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, decompose_middle_hmt
)

RESULTS_DIR = PROJECT_ROOT / 'phases' / 'CROSS_LAYER_ATOM_DECOMPOSITION' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIERS = {'p', 'c', 'i', 'f', 'd', 's'}

# Terminal tiers (C1487)
LOCKED = {'r', 'm'}
CHANNELED = {'l', 'y', 'n'}
DIFFUSE = {'h'}

HEAD_LABELS = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_LABELS = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
MOD_LABELS = ['p', 'c', 'i', 'f', 'd', 's']
TIER_LABELS = ['LOCKED', 'CHANNELED', 'DIFFUSE', 'bare']


def jsd(p: Dict, q: Dict, labels: List[str]) -> float:
    """Jensen-Shannon Divergence between two distributions."""
    epsilon = 1e-10
    pv = [p.get(k, 0) + epsilon for k in labels]
    qv = [q.get(k, 0) + epsilon for k in labels]
    sp, sq = sum(pv), sum(qv)
    pv = [x / sp for x in pv]
    qv = [x / sq for x in qv]
    mv = [(a + b) / 2 for a, b in zip(pv, qv)]

    def kl(a, b):
        return sum(ai * math.log2(ai / bi) for ai, bi in zip(a, b) if ai > 0)

    return (kl(pv, mv) + kl(qv, mv)) / 2


def normalize(counts: Dict, labels: List[str]) -> Dict:
    """Convert counts to proportions."""
    total = sum(counts.get(k, 0) for k in labels)
    if total == 0:
        return {k: 0.0 for k in labels}
    return {k: counts.get(k, 0) / total for k in labels}


def enrichment(channel_dist: Dict, baseline_dist: Dict, labels: List[str]) -> Dict:
    """Compute enrichment ratios vs baseline."""
    result = {}
    for k in labels:
        ch = channel_dist.get(k, 0)
        bl = baseline_dist.get(k, 0)
        if bl > 0:
            result[k] = round(ch / bl, 3)
        else:
            result[k] = float('inf') if ch > 0 else 1.0
    return result


def chi2_test_2xN(counts_a: Dict, counts_b: Dict, labels: List[str]):
    """Simple chi-squared test for 2xN contingency table."""
    obs_a = [counts_a.get(k, 0) for k in labels]
    obs_b = [counts_b.get(k, 0) for k in labels]
    total_a, total_b = sum(obs_a), sum(obs_b)
    total = total_a + total_b
    if total == 0 or total_a == 0 or total_b == 0:
        return 0.0, 1.0, 0.0

    chi2 = 0.0
    for i, k in enumerate(labels):
        col_total = obs_a[i] + obs_b[i]
        if col_total == 0:
            continue
        exp_a = total_a * col_total / total
        exp_b = total_b * col_total / total
        if exp_a > 0:
            chi2 += (obs_a[i] - exp_a) ** 2 / exp_a
        if exp_b > 0:
            chi2 += (obs_b[i] - exp_b) ** 2 / exp_b

    df = sum(1 for k in labels if (counts_a.get(k, 0) + counts_b.get(k, 0)) > 0) - 1
    if df <= 0:
        return chi2, 1.0, 0.0

    # Cramer's V
    n = total
    k_val = 2  # 2 rows
    v = math.sqrt(chi2 / (n * (min(k_val, len(labels)) - 1))) if n > 0 else 0

    return chi2, df, v


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("=" * 72)
    print("PHASE 538: Cross-Layer Atom Decomposition — Bridge vs Dark Pipeline")
    print("=" * 72)

    # ----- Load infrastructure -----
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Load bridge and dark pipeline MIDDLE sets
    bridge_path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path, 'r', encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_set = set(dark_data['middles'])

    print(f"\nBridge MIDDLEs: {len(bridge_set)}")
    print(f"Dark pipeline MIDDLEs: {len(dark_set)}")

    # ----- Collect MIDDLEs by system -----
    # B MIDDLEs
    b_middles = Counter()
    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle and m.middle != '_EMPTY_':
            b_middles[m.middle] += 1

    # A MIDDLEs
    a_middles = Counter()
    for token in tx.currier_a():
        m = morph.extract(token.word)
        if m.middle and m.middle != '_EMPTY_':
            a_middles[m.middle] += 1

    # AZC MIDDLEs
    azc_middles = Counter()
    for token in tx.azc():
        if '*' in token.word:
            continue
        m = morph.extract(token.word)
        if m.middle and m.middle != '_EMPTY_':
            azc_middles[m.middle] += 1

    # A-exclusive MIDDLEs (in A but NOT in B)
    a_exclusive_set = set(a_middles.keys()) - set(b_middles.keys())

    # All MIDDLEs appearing in B (for baseline)
    b_middle_set = set(b_middles.keys())

    print(f"\nUnique B MIDDLEs: {len(b_middle_set)}")
    print(f"Unique A MIDDLEs: {len(set(a_middles.keys()))}")
    print(f"Unique AZC MIDDLEs: {len(set(azc_middles.keys()))}")
    print(f"A-exclusive MIDDLEs: {len(a_exclusive_set)}")

    # ----- Classify MIDDLEs into channels -----
    # Channel: bridge, dark, a_exclusive, b_exclusive, azc_exclusive
    channels = {
        'bridge': bridge_set,
        'dark': dark_set,
        'a_exclusive': a_exclusive_set,
        'b_only': b_middle_set - set(a_middles.keys()) - bridge_set - dark_set,
    }

    # For B baseline, use ALL B MIDDLEs weighted by token frequency
    # For channel profiles, use type-level (each MIDDLE counted once)

    # ============================================================
    # TEST (a): HEAD domain profile by pipeline channel
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (a): HEAD Domain Profile by Pipeline Channel")
    print("=" * 72)

    def head_profile(middles: Set[str], weighted_counts: Counter = None) -> Tuple[Counter, Dict]:
        """Compute HEAD distribution for a set of MIDDLEs.
        If weighted_counts provided, weight by token frequency."""
        counts = Counter()
        for mid in middles:
            head, mods, term, frame = decompose_middle_hmt(mid)
            label = head if head else 'headless'
            weight = weighted_counts[mid] if weighted_counts else 1
            counts[label] += weight
        return counts, normalize(counts, HEAD_LABELS)

    # B baseline (token-weighted)
    b_head_counts, b_head_dist = head_profile(b_middle_set, b_middles)

    # Channel profiles (type-level)
    results_head = {}
    for ch_name, ch_set in channels.items():
        ch_counts, ch_dist = head_profile(ch_set)
        enr = enrichment(ch_dist, b_head_dist, HEAD_LABELS)
        results_head[ch_name] = {
            'n_types': len(ch_set),
            'counts': {k: ch_counts.get(k, 0) for k in HEAD_LABELS},
            'distribution': {k: round(v, 4) for k, v in ch_dist.items()},
            'enrichment_vs_b': enr,
        }
        print(f"\n{ch_name.upper()} ({len(ch_set)} types):")
        for h in HEAD_LABELS:
            print(f"  {h:10s}: {ch_dist.get(h, 0):.3f}  [{enr.get(h, 0):.2f}x vs B]")

    # Also compute for A-system MIDDLEs (all) and AZC MIDDLEs
    for sys_name, sys_middles in [('all_A', set(a_middles.keys())), ('all_AZC', set(azc_middles.keys()))]:
        ch_counts, ch_dist = head_profile(sys_middles)
        enr = enrichment(ch_dist, b_head_dist, HEAD_LABELS)
        results_head[sys_name] = {
            'n_types': len(sys_middles),
            'counts': {k: ch_counts.get(k, 0) for k in HEAD_LABELS},
            'distribution': {k: round(v, 4) for k, v in ch_dist.items()},
            'enrichment_vs_b': enr,
        }
        print(f"\n{sys_name.upper()} ({len(sys_middles)} types):")
        for h in HEAD_LABELS:
            print(f"  {h:10s}: {ch_dist.get(h, 0):.3f}  [{enr.get(h, 0):.2f}x vs B]")

    # B baseline
    print(f"\nB BASELINE (token-weighted):")
    for h in HEAD_LABELS:
        print(f"  {h:10s}: {b_head_dist.get(h, 0):.3f}")
    results_head['b_baseline'] = {
        'n_tokens': sum(b_head_counts.values()),
        'distribution': {k: round(v, 4) for k, v in b_head_dist.items()},
    }

    # Expert prediction check
    bridge_dist = results_head['bridge']['distribution']
    dark_dist = results_head['dark']['distribution']

    ekt_bridge = bridge_dist.get('e', 0) + bridge_dist.get('k', 0) + bridge_dist.get('t', 0)
    ekt_dark = dark_dist.get('e', 0) + dark_dist.get('k', 0) + dark_dist.get('t', 0)
    o_headless_bridge = bridge_dist.get('o', 0) + bridge_dist.get('headless', 0)
    o_headless_dark = dark_dist.get('o', 0) + dark_dist.get('headless', 0)

    p1_pass = ekt_bridge > ekt_dark
    p2_pass = o_headless_dark > o_headless_bridge

    print(f"\n--- Expert Prediction Check ---")
    print(f"P1 (bridge e/k/t enriched): bridge={ekt_bridge:.3f} dark={ekt_dark:.3f} -> {'PASS' if p1_pass else 'FAIL'}")
    print(f"P2 (dark o+headless enriched): dark={o_headless_dark:.3f} bridge={o_headless_bridge:.3f} -> {'PASS' if p2_pass else 'FAIL'}")

    # ============================================================
    # TEST (b): TERMINAL profile by pipeline channel
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (b): TERMINAL Profile by Pipeline Channel")
    print("=" * 72)

    def term_profile(middles: Set[str], weighted_counts: Counter = None) -> Tuple[Counter, Dict]:
        counts = Counter()
        for mid in middles:
            head, mods, term, frame = decompose_middle_hmt(mid)
            weight = weighted_counts[mid] if weighted_counts else 1
            counts[term] += weight
        return counts, normalize(counts, TERM_LABELS)

    b_term_counts, b_term_dist = term_profile(b_middle_set, b_middles)

    results_term = {}
    for ch_name, ch_set in list(channels.items()) + [('all_A', set(a_middles.keys())), ('all_AZC', set(azc_middles.keys()))]:
        ch_counts, ch_dist = term_profile(ch_set)
        enr = enrichment(ch_dist, b_term_dist, TERM_LABELS)

        # Terminal tier aggregation
        locked_frac = ch_dist.get('r', 0) + ch_dist.get('m', 0)
        channeled_frac = ch_dist.get('l', 0) + ch_dist.get('y', 0) + ch_dist.get('n', 0)
        diffuse_frac = ch_dist.get('h', 0)
        bare_frac = ch_dist.get('bare', 0)

        tier_dist = {
            'LOCKED': locked_frac,
            'CHANNELED': channeled_frac,
            'DIFFUSE': diffuse_frac,
            'bare': bare_frac,
        }

        results_term[ch_name] = {
            'n_types': len(ch_set) if isinstance(ch_set, set) else 0,
            'counts': {k: ch_counts.get(k, 0) for k in TERM_LABELS},
            'distribution': {k: round(v, 4) for k, v in ch_dist.items()},
            'enrichment_vs_b': enr,
            'tier_distribution': {k: round(v, 4) for k, v in tier_dist.items()},
        }
        print(f"\n{ch_name.upper()}:")
        for t in TERM_LABELS:
            print(f"  {t:6s}: {ch_dist.get(t, 0):.3f}  [{enr.get(t, 0):.2f}x vs B]")
        print(f"  --- Tiers: LOCKED={locked_frac:.3f}  CHANNELED={channeled_frac:.3f}  "
              f"DIFFUSE={diffuse_frac:.3f}  bare={bare_frac:.3f}")

    # B baseline
    locked_b = b_term_dist.get('r', 0) + b_term_dist.get('m', 0)
    channeled_b = b_term_dist.get('l', 0) + b_term_dist.get('y', 0) + b_term_dist.get('n', 0)
    diffuse_b = b_term_dist.get('h', 0)
    bare_b = b_term_dist.get('bare', 0)

    print(f"\nB BASELINE (token-weighted):")
    for t in TERM_LABELS:
        print(f"  {t:6s}: {b_term_dist.get(t, 0):.3f}")
    print(f"  --- Tiers: LOCKED={locked_b:.3f}  CHANNELED={channeled_b:.3f}  "
          f"DIFFUSE={diffuse_b:.3f}  bare={bare_b:.3f}")
    results_term['b_baseline'] = {
        'distribution': {k: round(v, 4) for k, v in b_term_dist.items()},
        'tier_distribution': {
            'LOCKED': round(locked_b, 4),
            'CHANNELED': round(channeled_b, 4),
            'DIFFUSE': round(diffuse_b, 4),
            'bare': round(bare_b, 4),
        }
    }

    # Expert predictions
    dark_td = results_term['dark']['tier_distribution']
    bridge_td = results_term['bridge']['tier_distribution']

    p3_pass = (dark_td['DIFFUSE'] + dark_td['CHANNELED']) > (bridge_td['DIFFUSE'] + bridge_td['CHANNELED'])
    p4_pass = bridge_td['LOCKED'] > dark_td['LOCKED']

    print(f"\n--- Expert Prediction Check ---")
    print(f"P3 (dark prefers DIFFUSE+CHANNELED): dark={dark_td['DIFFUSE']+dark_td['CHANNELED']:.3f} "
          f"bridge={bridge_td['DIFFUSE']+bridge_td['CHANNELED']:.3f} -> {'PASS' if p3_pass else 'FAIL'}")
    print(f"P4 (bridge tolerates LOCKED): bridge={bridge_td['LOCKED']:.3f} "
          f"dark={dark_td['LOCKED']:.3f} -> {'PASS' if p4_pass else 'FAIL'}")

    # ============================================================
    # TEST (c): Modifier profile by pipeline channel
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (c): Modifier Profile by Pipeline Channel")
    print("=" * 72)

    def mod_profile(middles: Set[str]) -> Tuple[Counter, float]:
        """Count modifier usage (type-level). Return counts and fraction with any modifier."""
        counts = Counter()
        n_with_mod = 0
        n_total = 0
        for mid in middles:
            head, mods, term, frame = decompose_middle_hmt(mid)
            n_total += 1
            if mods:
                n_with_mod += 1
                for c in mods:
                    if c in MODIFIERS:
                        counts[c] += 1
        mod_rate = n_with_mod / n_total if n_total > 0 else 0
        return counts, mod_rate

    results_mod = {}
    for ch_name, ch_set in list(channels.items()) + [('all_A', set(a_middles.keys())), ('all_AZC', set(azc_middles.keys()))]:
        ch_counts, mod_rate = mod_profile(ch_set)
        ch_dist = normalize(ch_counts, MOD_LABELS)
        results_mod[ch_name] = {
            'modifier_rate': round(mod_rate, 4),
            'counts': {k: ch_counts.get(k, 0) for k in MOD_LABELS},
            'distribution': {k: round(v, 4) for k, v in ch_dist.items()},
        }
        print(f"\n{ch_name.upper()} (modifier rate: {mod_rate:.3f}):")
        for m in MOD_LABELS:
            print(f"  {m}: {ch_counts.get(m, 0):4d}  ({ch_dist.get(m, 0):.3f})")

    # B baseline
    b_mod_counts, b_mod_rate = mod_profile(b_middle_set)
    b_mod_dist = normalize(b_mod_counts, MOD_LABELS)
    print(f"\nB BASELINE (modifier rate: {b_mod_rate:.3f}):")
    for m in MOD_LABELS:
        print(f"  {m}: {b_mod_counts.get(m, 0):4d}  ({b_mod_dist.get(m, 0):.3f})")
    results_mod['b_baseline'] = {
        'modifier_rate': round(b_mod_rate, 4),
        'distribution': {k: round(v, 4) for k, v in b_mod_dist.items()},
    }

    # ============================================================
    # TEST (d): Headless abundance by channel
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (d): Headless Abundance by Channel")
    print("=" * 72)

    results_headless = {}
    for ch_name, ch_set in list(channels.items()) + [('all_A', set(a_middles.keys())), ('all_AZC', set(azc_middles.keys()))]:
        n_headless = sum(1 for mid in ch_set if mid[0] not in HEADS) if ch_set else 0
        rate = n_headless / len(ch_set) if ch_set else 0
        results_headless[ch_name] = {
            'n_headless': n_headless,
            'n_total': len(ch_set),
            'headless_rate': round(rate, 4),
        }
        print(f"  {ch_name:15s}: {n_headless:4d} / {len(ch_set):4d} = {rate:.3f}")

    b_headless = sum(1 for mid in b_middle_set if mid[0] not in HEADS)
    b_headless_rate = b_headless / len(b_middle_set)
    results_headless['b_baseline'] = {'headless_rate': round(b_headless_rate, 4)}
    print(f"  {'b_baseline':15s}: {b_headless:4d} / {len(b_middle_set):4d} = {b_headless_rate:.3f}")

    # ============================================================
    # TEST (e): Category stability for bridge MIDDLEs across A and B
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (e): Bridge MIDDLE Category Stability Across A and B")
    print("=" * 72)

    # For each bridge MIDDLE, get category from classifier (which uses B-derived glosses)
    # Then check: does the HEAD atom of the bridge MIDDLE predict its category?
    # And does HEAD remain constant across systems?

    bridge_categories = {}
    head_category_map = defaultdict(Counter)  # head -> category counts

    for mid in bridge_set:
        cat = cc.classify(mid)
        head, mods, term, frame = decompose_middle_hmt(mid)
        head_label = head if head else 'headless'
        bridge_categories[mid] = {
            'category': cat,
            'head': head_label,
            'term': term,
            'mods': mods,
        }
        if cat:
            head_category_map[head_label][cat] += 1

    print("\nHEAD -> Category mapping for bridge MIDDLEs:")
    head_category_results = {}
    for h in HEAD_LABELS:
        cats = head_category_map[h]
        total = sum(cats.values())
        if total == 0:
            continue
        dominant = cats.most_common(1)[0]
        purity = dominant[1] / total
        print(f"  {h:10s} (N={total}): dominant={dominant[0]} ({purity:.1%})")
        for cat, count in sorted(cats.items()):
            print(f"    {cat}: {count} ({count/total:.1%})")
        head_category_results[h] = {
            'total': total,
            'dominant_category': dominant[0],
            'dominant_purity': round(purity, 4),
            'all_categories': dict(cats),
        }

    # Category stability: bridge MIDDLEs decompose identically in A and B
    # (same MIDDLE string = same HEAD/MOD/TERM = same predicted category)
    # This is trivially true by C1395 — the question is whether bridge atom
    # profiles GROUP differently when viewed in A vs B TOKEN context

    # Compute bridge HEAD distribution when weighted by A frequency vs B frequency
    bridge_in_a = {mid: a_middles.get(mid, 0) for mid in bridge_set}
    bridge_in_b = {mid: b_middles.get(mid, 0) for mid in bridge_set}

    head_in_a = Counter()
    head_in_b = Counter()
    for mid in bridge_set:
        head, mods, term, frame = decompose_middle_hmt(mid)
        label = head if head else 'headless'
        head_in_a[label] += bridge_in_a.get(mid, 0)
        head_in_b[label] += bridge_in_b.get(mid, 0)

    a_dist = normalize(head_in_a, HEAD_LABELS)
    b_dist = normalize(head_in_b, HEAD_LABELS)
    bridge_head_jsd = jsd(a_dist, b_dist, HEAD_LABELS)

    print(f"\nBridge HEAD distribution: A-weighted vs B-weighted")
    print(f"  JSD = {bridge_head_jsd:.4f}")
    for h in HEAD_LABELS:
        print(f"  {h:10s}: A={a_dist.get(h,0):.3f}  B={b_dist.get(h,0):.3f}  "
              f"ratio={a_dist.get(h,0)/b_dist.get(h,0):.2f}" if b_dist.get(h,0) > 0 else
              f"  {h:10s}: A={a_dist.get(h,0):.3f}  B={b_dist.get(h,0):.3f}")

    results_category_stability = {
        'head_category_map': head_category_results,
        'bridge_head_a_vs_b': {
            'jsd': round(bridge_head_jsd, 6),
            'a_weighted': {k: round(v, 4) for k, v in a_dist.items()},
            'b_weighted': {k: round(v, 4) for k, v in b_dist.items()},
        }
    }

    # ============================================================
    # TEST (f): Category distribution by channel (with bridge vs dark chi2)
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (f): Category Distribution by Channel")
    print("=" * 72)

    ALL_CATS = list(CategoryClassifier.CATEGORIES)

    results_channel_cat = {}
    for ch_name, ch_set in list(channels.items()) + [('all_A', set(a_middles.keys())), ('all_AZC', set(azc_middles.keys()))]:
        cat_counts = Counter()
        n_classified = 0
        for mid in ch_set:
            cat = cc.classify(mid)
            if cat:
                cat_counts[cat] += 1
                n_classified += 1
        cat_dist = normalize(cat_counts, ALL_CATS)
        classified_rate = n_classified / len(ch_set) if ch_set else 0

        results_channel_cat[ch_name] = {
            'n_classified': n_classified,
            'classified_rate': round(classified_rate, 4),
            'counts': dict(cat_counts),
            'distribution': {k: round(v, 4) for k, v in cat_dist.items()},
        }

        print(f"\n{ch_name.upper()} ({n_classified}/{len(ch_set)} classified = {classified_rate:.1%}):")
        for cat in ALL_CATS:
            print(f"  {cat:14s}: {cat_counts.get(cat, 0):4d}  ({cat_dist.get(cat, 0):.3f})")

    # Bridge vs Dark chi-squared on category
    bridge_cats = Counter()
    dark_cats = Counter()
    for mid in bridge_set:
        cat = cc.classify(mid)
        if cat:
            bridge_cats[cat] += 1
    for mid in dark_set:
        cat = cc.classify(mid)
        if cat:
            dark_cats[cat] += 1

    chi2_val, df, cramers_v = chi2_test_2xN(bridge_cats, dark_cats, ALL_CATS)
    print(f"\nBridge vs Dark category chi2={chi2_val:.1f}, df={df}, V={cramers_v:.3f}")

    # ============================================================
    # TEST (g): Atom-role redistribution — bridge in A vs B context
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (g): Bridge MIDDLE Atom Usage in A vs B Context")
    print("=" * 72)

    # For bridge MIDDLEs, compare their suffix ecology in A vs B
    bridge_suffix_a = Counter()
    bridge_suffix_b = Counter()
    bridge_prefix_a = Counter()
    bridge_prefix_b = Counter()

    for token in tx.currier_a():
        m = morph.extract(token.word)
        if m.middle and m.middle in bridge_set:
            sfx = m.suffix if m.suffix else 'bare'
            pfx = m.prefix if m.prefix else 'BARE'
            bridge_suffix_a[sfx] += 1
            bridge_prefix_a[pfx] += 1

    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle and m.middle in bridge_set:
            sfx = m.suffix if m.suffix else 'bare'
            pfx = m.prefix if m.prefix else 'BARE'
            bridge_suffix_b[sfx] += 1
            bridge_prefix_b[pfx] += 1

    # Top suffixes in each system
    print("\nBridge MIDDLE suffix ecology:")
    print(f"  A total: {sum(bridge_suffix_a.values())} tokens")
    print(f"  B total: {sum(bridge_suffix_b.values())} tokens")

    all_sfx = sorted(set(bridge_suffix_a.keys()) | set(bridge_suffix_b.keys()))
    sfx_a_total = sum(bridge_suffix_a.values())
    sfx_b_total = sum(bridge_suffix_b.values())

    print(f"\n  {'Suffix':10s}  {'A count':>8s}  {'A %':>6s}  {'B count':>8s}  {'B %':>6s}  {'A/B ratio':>9s}")
    for sfx in sorted(all_sfx, key=lambda s: bridge_suffix_a.get(s, 0) + bridge_suffix_b.get(s, 0), reverse=True)[:15]:
        a_n = bridge_suffix_a.get(sfx, 0)
        b_n = bridge_suffix_b.get(sfx, 0)
        a_pct = a_n / sfx_a_total if sfx_a_total > 0 else 0
        b_pct = b_n / sfx_b_total if sfx_b_total > 0 else 0
        ratio = a_pct / b_pct if b_pct > 0 else float('inf')
        print(f"  {sfx:10s}  {a_n:8d}  {a_pct:5.1%}  {b_n:8d}  {b_pct:5.1%}  {ratio:8.2f}x")

    # Bridge prefix ecology
    print(f"\nBridge MIDDLE prefix ecology (top 10 in each):")
    print(f"  {'Prefix':10s}  {'A count':>8s}  {'A %':>6s}  {'B count':>8s}  {'B %':>6s}")
    pfx_a_total = sum(bridge_prefix_a.values())
    pfx_b_total = sum(bridge_prefix_b.values())
    all_pfx = sorted(set(bridge_prefix_a.keys()) | set(bridge_prefix_b.keys()),
                     key=lambda p: bridge_prefix_a.get(p, 0) + bridge_prefix_b.get(p, 0), reverse=True)
    for pfx in all_pfx[:15]:
        a_n = bridge_prefix_a.get(pfx, 0)
        b_n = bridge_prefix_b.get(pfx, 0)
        a_pct = a_n / pfx_a_total if pfx_a_total > 0 else 0
        b_pct = b_n / pfx_b_total if pfx_b_total > 0 else 0
        print(f"  {pfx:10s}  {a_n:8d}  {a_pct:5.1%}  {b_n:8d}  {b_pct:5.1%}")

    results_redistribution = {
        'bridge_suffix_a': dict(bridge_suffix_a.most_common(20)),
        'bridge_suffix_b': dict(bridge_suffix_b.most_common(20)),
        'bridge_prefix_a': dict(bridge_prefix_a.most_common(20)),
        'bridge_prefix_b': dict(bridge_prefix_b.most_common(20)),
        'a_total_tokens': sfx_a_total,
        'b_total_tokens': sfx_b_total,
    }

    # ============================================================
    # TEST (h): AZC atomization — HEAD domain profile
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (h): AZC HEAD Domain Profile")
    print("=" * 72)

    azc_set = set(azc_middles.keys())
    azc_head_counts, azc_head_dist = head_profile(azc_set)
    azc_head_enr = enrichment(azc_head_dist, b_head_dist, HEAD_LABELS)

    print(f"\nAZC HEAD profile ({len(azc_set)} unique MIDDLEs, {sum(azc_middles.values())} tokens):")
    for h in HEAD_LABELS:
        print(f"  {h:10s}: {azc_head_dist.get(h, 0):.3f}  [{azc_head_enr.get(h, 0):.2f}x vs B]")

    # Token-weighted AZC
    azc_head_tw_counts, azc_head_tw_dist = head_profile(azc_set, azc_middles)
    print(f"\nAZC HEAD profile (token-weighted):")
    for h in HEAD_LABELS:
        enr_tw = azc_head_tw_dist.get(h, 0) / b_head_dist.get(h, 1) if b_head_dist.get(h, 0) > 0 else 0
        print(f"  {h:10s}: {azc_head_tw_dist.get(h, 0):.3f}  [{enr_tw:.2f}x vs B]")

    # o-HEAD test (C1381)
    o_azc = azc_head_dist.get('o', 0)
    o_b = b_head_dist.get('o', 0)
    o_enrichment = o_azc / o_b if o_b > 0 else 0
    print(f"\no-HEAD: AZC={o_azc:.3f} vs B={o_b:.3f} -> {o_enrichment:.2f}x (C1381 confirms o-initial enrichment)")

    results_azc = {
        'type_level': {
            'counts': {k: azc_head_counts.get(k, 0) for k in HEAD_LABELS},
            'distribution': {k: round(v, 4) for k, v in azc_head_dist.items()},
            'enrichment_vs_b': azc_head_enr,
        },
        'token_weighted': {
            'distribution': {k: round(v, 4) for k, v in azc_head_tw_dist.items()},
        },
        'o_head_enrichment': round(o_enrichment, 3),
    }

    # ============================================================
    # TEST (i): Overall atom ontology — pairwise JSD
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (i): Pairwise JSD Between Systems/Channels")
    print("=" * 72)

    # Compute HEAD, TERM, MOD distributions for each system/channel
    all_channels = {
        'bridge': bridge_set,
        'dark': dark_set,
        'a_exclusive': a_exclusive_set,
        'b_only': channels['b_only'],
        'all_A': set(a_middles.keys()),
        'all_B': b_middle_set,
        'all_AZC': azc_set,
    }

    head_dists = {}
    term_dists = {}
    mod_dists = {}

    for name, midset in all_channels.items():
        _, hd = head_profile(midset)
        _, td = term_profile(midset)
        mc, _ = mod_profile(midset)
        md = normalize(mc, MOD_LABELS)
        head_dists[name] = hd
        term_dists[name] = td
        mod_dists[name] = md

    # Pairwise JSD matrices
    ch_names = sorted(all_channels.keys())

    print("\nHEAD JSD matrix:")
    head_jsd_matrix = {}
    print(f"  {'':15s}", end='')
    for n in ch_names:
        print(f"  {n[:8]:>8s}", end='')
    print()
    for n1 in ch_names:
        head_jsd_matrix[n1] = {}
        print(f"  {n1:15s}", end='')
        for n2 in ch_names:
            val = jsd(head_dists[n1], head_dists[n2], HEAD_LABELS)
            head_jsd_matrix[n1][n2] = round(val, 4)
            print(f"  {val:8.4f}", end='')
        print()

    print("\nTERM JSD matrix:")
    term_jsd_matrix = {}
    print(f"  {'':15s}", end='')
    for n in ch_names:
        print(f"  {n[:8]:>8s}", end='')
    print()
    for n1 in ch_names:
        term_jsd_matrix[n1] = {}
        print(f"  {n1:15s}", end='')
        for n2 in ch_names:
            val = jsd(term_dists[n1], term_dists[n2], TERM_LABELS)
            term_jsd_matrix[n1][n2] = round(val, 4)
            print(f"  {val:8.4f}", end='')
        print()

    print("\nMOD JSD matrix:")
    mod_jsd_matrix = {}
    print(f"  {'':15s}", end='')
    for n in ch_names:
        print(f"  {n[:8]:>8s}", end='')
    print()
    for n1 in ch_names:
        mod_jsd_matrix[n1] = {}
        print(f"  {n1:15s}", end='')
        for n2 in ch_names:
            val = jsd(mod_dists[n1], mod_dists[n2], MOD_LABELS)
            mod_jsd_matrix[n1][n2] = round(val, 4)
            print(f"  {val:8.4f}", end='')
        print()

    # Summary: average JSD to understand ontological unity
    print("\nAverage JSD (lower = more similar):")
    for dim_name, matrix in [('HEAD', head_jsd_matrix), ('TERM', term_jsd_matrix), ('MOD', mod_jsd_matrix)]:
        vals = []
        for n1 in ch_names:
            for n2 in ch_names:
                if n1 < n2:
                    vals.append(matrix[n1][n2])
        avg = sum(vals) / len(vals) if vals else 0
        max_val = max(vals) if vals else 0
        min_val = min(vals) if vals else 0
        print(f"  {dim_name}: mean={avg:.4f}  range=[{min_val:.4f}, {max_val:.4f}]")

    # Find most similar and most different pairs
    print("\nMost similar pairs by HEAD:")
    head_pairs = [(head_jsd_matrix[n1][n2], n1, n2)
                  for n1 in ch_names for n2 in ch_names if n1 < n2]
    for val, n1, n2 in sorted(head_pairs)[:3]:
        print(f"  {n1} <-> {n2}: {val:.4f}")
    print("Most different pairs by HEAD:")
    for val, n1, n2 in sorted(head_pairs, reverse=True)[:3]:
        print(f"  {n1} <-> {n2}: {val:.4f}")

    results_jsd = {
        'head_jsd': head_jsd_matrix,
        'term_jsd': term_jsd_matrix,
        'mod_jsd': mod_jsd_matrix,
    }

    # ============================================================
    # TEST (j): Compound depth and atom overlap
    # ============================================================
    print("\n" + "=" * 72)
    print("TEST (j): Compound Depth and Atom Overlap by Channel")
    print("=" * 72)

    results_depth = {}
    for ch_name, ch_set in all_channels.items():
        lengths = [len(mid) for mid in ch_set]
        mean_len = sum(lengths) / len(lengths) if lengths else 0
        n_compound = sum(1 for mid in ch_set if len(mid) > 2)
        compound_rate = n_compound / len(ch_set) if ch_set else 0

        # Atom inventory
        all_atoms = set()
        for mid in ch_set:
            for c in mid:
                all_atoms.add(c)

        results_depth[ch_name] = {
            'n_types': len(ch_set),
            'mean_length': round(mean_len, 2),
            'compound_rate': round(compound_rate, 4),
            'n_unique_atoms': len(all_atoms),
            'atoms': sorted(all_atoms),
        }
        print(f"  {ch_name:15s}: mean_len={mean_len:.2f}  compound={compound_rate:.1%}  atoms={len(all_atoms)}")

    # Atom overlap matrix
    print("\nAtom inventory overlap (Jaccard):")
    atom_sets = {name: set(c for mid in midset for c in mid) for name, midset in all_channels.items()}
    print(f"  {'':15s}", end='')
    for n in ch_names:
        print(f"  {n[:8]:>8s}", end='')
    print()
    atom_jaccard = {}
    for n1 in ch_names:
        atom_jaccard[n1] = {}
        print(f"  {n1:15s}", end='')
        for n2 in ch_names:
            inter = len(atom_sets[n1] & atom_sets[n2])
            union = len(atom_sets[n1] | atom_sets[n2])
            j = inter / union if union > 0 else 0
            atom_jaccard[n1][n2] = round(j, 3)
            print(f"  {j:8.3f}", end='')
        print()

    results_depth['atom_jaccard'] = atom_jaccard

    # ============================================================
    # SYNTHESIS: Expert Prediction Summary
    # ============================================================
    print("\n" + "=" * 72)
    print("SYNTHESIS: Expert Prediction Summary")
    print("=" * 72)

    predictions = {
        'P1': {
            'description': 'Bridge enriched in e/k/t HEADs (executable backbone)',
            'bridge_ekt': round(ekt_bridge, 4),
            'dark_ekt': round(ekt_dark, 4),
            'pass': p1_pass,
        },
        'P2': {
            'description': 'Dark enriched in o-HEAD and headless (identification substrate)',
            'dark_o_headless': round(o_headless_dark, 4),
            'bridge_o_headless': round(o_headless_bridge, 4),
            'pass': p2_pass,
        },
        'P3': {
            'description': 'Dark prefers transparent/channeled terminals (h, n, y)',
            'dark_diffuse_channeled': round(dark_td['DIFFUSE'] + dark_td['CHANNELED'], 4),
            'bridge_diffuse_channeled': round(bridge_td['DIFFUSE'] + bridge_td['CHANNELED'], 4),
            'pass': p3_pass,
        },
        'P4': {
            'description': 'Bridge tolerates more locked terminals (m, r)',
            'bridge_locked': round(bridge_td['LOCKED'], 4),
            'dark_locked': round(dark_td['LOCKED'], 4),
            'pass': p4_pass,
        },
    }

    # P5: same atoms, different slot proportions
    bridge_dark_head_jsd = head_jsd_matrix.get('bridge', {}).get('dark', 0)
    bridge_dark_term_jsd = term_jsd_matrix.get('bridge', {}).get('dark', 0)
    bridge_dark_mod_jsd = mod_jsd_matrix.get('bridge', {}).get('dark', 0)
    bridge_dark_atom_jaccard = atom_jaccard.get('bridge', {}).get('dark', 0)

    p5_pass = bridge_dark_atom_jaccard > 0.8 and max(bridge_dark_head_jsd, bridge_dark_term_jsd) > 0.01
    predictions['P5'] = {
        'description': 'Dark = same atoms, different slot proportions (non-executable nominalization)',
        'atom_jaccard': bridge_dark_atom_jaccard,
        'head_jsd': bridge_dark_head_jsd,
        'term_jsd': bridge_dark_term_jsd,
        'mod_jsd': bridge_dark_mod_jsd,
        'pass': p5_pass,
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    for pid, pdata in sorted(predictions.items()):
        status = 'PASS' if pdata['pass'] else 'FAIL'
        print(f"  {pid}: {status} - {pdata['description']}")

    print(f"\n  Total: {n_pass}/{n_total} predictions confirmed")

    # ============================================================
    # OVERALL SYNTHESIS
    # ============================================================
    print("\n" + "=" * 72)
    print("OVERALL SYNTHESIS")
    print("=" * 72)

    # Key findings
    # 1. Is atom grammar manuscript-wide?
    max_head_jsd = max(head_jsd_matrix[n1][n2] for n1 in ch_names for n2 in ch_names if n1 != n2)
    avg_head_jsd = sum(head_jsd_matrix[n1][n2] for n1 in ch_names for n2 in ch_names if n1 < n2) / len([1 for n1 in ch_names for n2 in ch_names if n1 < n2])

    # Atom overlap
    min_jaccard = min(atom_jaccard[n1][n2] for n1 in ch_names for n2 in ch_names if n1 != n2)

    print(f"\n1. ATOM ONTOLOGY UNIVERSALITY:")
    print(f"   Atom inventory overlap: min Jaccard = {min_jaccard:.3f}")
    print(f"   HEAD slot JSD: mean = {avg_head_jsd:.4f}, max = {max_head_jsd:.4f}")

    if min_jaccard > 0.7 and avg_head_jsd < 0.1:
        print(f"   VERDICT: SHARED atom substrate with GRADED slot proportions")
    elif min_jaccard > 0.7:
        print(f"   VERDICT: SHARED atoms, DIFFERENT slot usage")
    else:
        print(f"   VERDICT: PARTIALLY SHARED atom repertoire")

    print(f"\n2. BRIDGE vs DARK DIFFERENTIATION:")
    print(f"   HEAD JSD = {bridge_dark_head_jsd:.4f}")
    print(f"   TERM JSD = {bridge_dark_term_jsd:.4f}")
    print(f"   MOD JSD = {bridge_dark_mod_jsd:.4f}")
    print(f"   Atom Jaccard = {bridge_dark_atom_jaccard:.3f}")

    print(f"\n3. AZC o-HEAD ENRICHMENT:")
    print(f"   AZC o-HEAD rate = {azc_head_dist.get('o', 0):.3f} vs B = {b_head_dist.get('o', 0):.3f} "
          f"({o_enrichment:.2f}x)")

    print(f"\n4. HEADLESS GRADIENT:")
    for ch_name in ['bridge', 'dark', 'a_exclusive', 'all_A', 'all_AZC', 'b_only']:
        rate = results_headless.get(ch_name, {}).get('headless_rate', 0)
        print(f"   {ch_name:15s}: {rate:.3f}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================

    results = {
        'phase': 'CROSS_LAYER_ATOM_DECOMPOSITION',
        'phase_number': 538,
        'question': 'Is HEAD+MOD*+TERM atom grammar manuscript-wide or B-local?',
        'channel_counts': {
            'bridge': len(bridge_set),
            'dark': len(dark_set),
            'a_exclusive': len(a_exclusive_set),
            'b_only': len(channels['b_only']),
            'all_A': len(set(a_middles.keys())),
            'all_B': len(b_middle_set),
            'all_AZC': len(azc_set),
        },
        'head_profiles': results_head,
        'terminal_profiles': results_term,
        'modifier_profiles': results_mod,
        'headless_rates': results_headless,
        'category_stability': results_category_stability,
        'channel_categories': results_channel_cat,
        'bridge_category_chi2': {
            'chi2': round(chi2_val, 2),
            'df': df,
            'cramers_v': round(cramers_v, 4),
        },
        'bridge_redistribution': results_redistribution,
        'azc_head_profile': results_azc,
        'jsd_matrices': results_jsd,
        'compound_depth': results_depth,
        'predictions': predictions,
        'prediction_summary': f'{n_pass}/{n_total}',
    }

    out_path = RESULTS_DIR / 'cross_layer_atoms.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

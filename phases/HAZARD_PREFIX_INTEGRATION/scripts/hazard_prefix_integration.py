#!/usr/bin/env python3
"""
Phase 546: Hazard x PREFIX Integration
Joins hazard-class atlas (C1528-C1533) with PREFIX atom taxonomy (C1534-C1539)
to determine whether PREFIX bases/modifiers actively route hazard exposure.

Research questions:
1. Do different PREFIX bases feed into different hazard classes?
2. Do PREFIX modifiers shift hazard exposure within same base?
3. Do sister pairs differ in hazard-class exposure?
4. Is a-base the primary hazard feeder via headless -> PHASE_ORDERING?
5. Does qo's k-HEAD routing create systematic safety via hazard immunity?
6. Why is PHASE_ORDERING CHSH-specific? (mechanism)
7. Do safe tokens cluster under specific PREFIX types?
"""

import sys
import json
import os
from collections import Counter, defaultdict
from math import log2, sqrt

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ---------- CONSTANTS ----------

HEAD_ATOMS = set('aeokt')
MOD_ATOMS = set('picfds')
TERM_ATOMS = set('ylrhmn')

# Forbidden transitions from C109 / Phase 543
# Format: (source_middle, target_middle, hazard_class)
FORBIDDEN_PAIRS = [
    # PHASE_ORDERING (7 pairs)
    ('dy', 'ain', 'PHASE_ORDERING'),
    ('dy', 'aiin', 'PHASE_ORDERING'),
    ('dy', 'aiiin', 'PHASE_ORDERING'),
    ('shey', 'ain', 'PHASE_ORDERING'),
    ('shey', 'aiin', 'PHASE_ORDERING'),
    ('chey', 'ain', 'PHASE_ORDERING'),
    ('chey', 'aiin', 'PHASE_ORDERING'),
    # COMPOSITION_JUMP (4 pairs)
    ('chedy', 'ain', 'COMPOSITION_JUMP'),
    ('chedy', 'aiin', 'COMPOSITION_JUMP'),
    ('shedy', 'ain', 'COMPOSITION_JUMP'),
    ('shedy', 'aiin', 'COMPOSITION_JUMP'),
    # CONTAINMENT_TIMING (4 pairs)
    ('chol', 'ar', 'CONTAINMENT_TIMING'),
    ('chol', 'or', 'CONTAINMENT_TIMING'),
    ('l', 'ar', 'CONTAINMENT_TIMING'),
    ('l', 'or', 'CONTAINMENT_TIMING'),
    # RATE_MISMATCH (1 pair)
    ('c', 'he', 'RATE_MISMATCH'),
    # ENERGY_OVERSHOOT (1 pair)
    ('he', 'dy', 'ENERGY_OVERSHOOT'),
]

# Hazard source MIDDLEs (from forbidden pairs)
HAZARD_SOURCE_MIDDLES = set(p[0] for p in FORBIDDEN_PAIRS)
# Hazard target MIDDLEs
HAZARD_TARGET_MIDDLES = set(p[1] for p in FORBIDDEN_PAIRS)

# Source MIDDLEs by hazard class
HAZARD_CLASS_SOURCES = defaultdict(set)
for src, tgt, cls in FORBIDDEN_PAIRS:
    HAZARD_CLASS_SOURCES[cls].add(src)

HAZARD_CLASSES = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
                  'RATE_MISMATCH', 'ENERGY_OVERSHOOT']

# PREFIX base extraction
def get_prefix_base(prefix):
    """Get the base character of a PREFIX (last character)."""
    if not prefix:
        return None
    return prefix[-1]

def get_prefix_modifier(prefix):
    """Get the modifier character of a PREFIX (first character for len>=2)."""
    if not prefix or len(prefix) < 2:
        return None
    return prefix[0]

def get_head(middle):
    """Get HEAD atom (first char if in HEAD set, else HEADLESS)."""
    if not middle:
        return None
    return middle[0] if middle[0] in HEAD_ATOMS else 'HEADLESS'

def get_terminal(middle):
    """Get terminal atom (last char in TERM set, else 'bare')."""
    if not middle:
        return None
    for i in range(len(middle) - 1, -1, -1):
        if middle[i] in TERM_ATOMS:
            return middle[i]
    return 'bare'

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table (dict of dicts)."""
    rows = list(contingency_table.keys())
    cols = set()
    for r in rows:
        cols.update(contingency_table[r].keys())
    cols = list(cols)

    n = sum(contingency_table[r].get(c, 0) for r in rows for c in cols)
    if n == 0:
        return 0.0

    row_totals = {r: sum(contingency_table[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency_table[r].get(c, 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            observed = contingency_table[r].get(c, 0)
            expected = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    k = min(len(rows), len(cols))
    if k <= 1:
        return 0.0
    return sqrt(chi2 / (n * (k - 1)))

def chi2_stat(contingency_table):
    """Compute chi-squared statistic from contingency table."""
    rows = list(contingency_table.keys())
    cols = set()
    for r in rows:
        cols.update(contingency_table[r].keys())
    cols = list(cols)

    n = sum(contingency_table[r].get(c, 0) for r in rows for c in cols)
    if n == 0:
        return 0.0

    row_totals = {r: sum(contingency_table[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency_table[r].get(c, 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            observed = contingency_table[r].get(c, 0)
            expected = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if expected > 0:
                chi2 += (observed - expected) ** 2 / expected

    return chi2

def enrichment_ratio(count, total, base_count, base_total):
    """Compute enrichment ratio with continuity correction."""
    if total == 0 or base_total == 0:
        return 0.0
    obs_rate = count / total
    base_rate = base_count / base_total
    if base_rate == 0:
        return float('inf') if count > 0 else 0.0
    return obs_rate / base_rate


# ---------- MAIN ANALYSIS ----------

def main():
    print("Phase 546: Hazard x PREFIX Integration")
    print("=" * 60)

    tx = Transcript()
    morph = Morphology()

    # Collect all B tokens with morphological decomposition
    tokens = []
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if not m.middle:
            continue

        prefix = m.prefix if m.prefix else 'BARE'
        middle = m.middle

        head = get_head(middle)
        terminal = get_terminal(middle)

        base = get_prefix_base(m.prefix) if m.prefix else 'BARE'
        modifier = get_prefix_modifier(m.prefix) if m.prefix else 'BARE'

        is_hazard_source = middle in HAZARD_SOURCE_MIDDLES
        is_hazard_target = middle in HAZARD_TARGET_MIDDLES

        # Which hazard class(es) is this MIDDLE a source for?
        source_classes = []
        for cls in HAZARD_CLASSES:
            if middle in HAZARD_CLASS_SOURCES[cls]:
                source_classes.append(cls)

        tokens.append({
            'word': tok.word,
            'folio': tok.folio,
            'prefix': prefix,
            'middle': middle,
            'head': head,
            'terminal': terminal,
            'base': base,
            'modifier': modifier,
            'is_hazard_source': is_hazard_source,
            'is_hazard_target': is_hazard_target,
            'source_classes': source_classes,
        })

    total_tokens = len(tokens)
    hazard_source_tokens = [t for t in tokens if t['is_hazard_source']]
    hazard_target_tokens = [t for t in tokens if t['is_hazard_target']]
    safe_tokens = [t for t in tokens if not t['is_hazard_source'] and not t['is_hazard_target']]

    print(f"\nTotal B tokens: {total_tokens}")
    print(f"Hazard source tokens: {len(hazard_source_tokens)} ({100*len(hazard_source_tokens)/total_tokens:.1f}%)")
    print(f"Hazard target tokens: {len(hazard_target_tokens)} ({100*len(hazard_target_tokens)/total_tokens:.1f}%)")
    print(f"Safe tokens: {len(safe_tokens)} ({100*len(safe_tokens)/total_tokens:.1f}%)")

    results = {
        'phase': 'Phase 546: Hazard x PREFIX Integration',
        'date': '2026-03-06',
        'token_counts': {
            'total_B': total_tokens,
            'hazard_source': len(hazard_source_tokens),
            'hazard_target': len(hazard_target_tokens),
            'safe': len(safe_tokens),
        }
    }

    # ===== STEP 1: PREFIX-level hazard profile =====
    print("\n" + "=" * 60)
    print("STEP 1: PREFIX-level hazard profile")
    print("=" * 60)

    prefix_hazard = defaultdict(lambda: {'total': 0, 'source': 0, 'target': 0,
                                          'class_counts': Counter()})
    for t in tokens:
        pfx = t['prefix']
        prefix_hazard[pfx]['total'] += 1
        if t['is_hazard_source']:
            prefix_hazard[pfx]['source'] += 1
            for cls in t['source_classes']:
                prefix_hazard[pfx]['class_counts'][cls] += 1
        if t['is_hazard_target']:
            prefix_hazard[pfx]['target'] += 1

    # Top PREFIXes by source rate
    prefix_source_rates = {}
    for pfx, data in prefix_hazard.items():
        if data['total'] >= 20:
            rate = data['source'] / data['total']
            prefix_source_rates[pfx] = {
                'total': data['total'],
                'source_count': data['source'],
                'source_rate': round(rate * 100, 2),
                'target_count': data['target'],
                'target_rate': round(data['target'] / data['total'] * 100, 2),
                'class_distribution': {cls: data['class_counts'].get(cls, 0)
                                       for cls in HAZARD_CLASSES}
            }

    sorted_pfx = sorted(prefix_source_rates.items(), key=lambda x: -x[1]['source_rate'])
    print("\nPREFIX hazard source rates (N>=20):")
    print(f"{'PREFIX':<10} {'N':>6} {'Source%':>8} {'Target%':>8} {'PH_ORD':>7} {'COMP_J':>7} {'CONT_T':>7}")
    for pfx, d in sorted_pfx[:20]:
        print(f"{pfx:<10} {d['total']:>6} {d['source_rate']:>7.1f}% {d['target_rate']:>7.1f}% "
              f"{d['class_distribution']['PHASE_ORDERING']:>7} {d['class_distribution']['COMPOSITION_JUMP']:>7} "
              f"{d['class_distribution']['CONTAINMENT_TIMING']:>7}")

    results['prefix_hazard_profiles'] = prefix_source_rates

    # ===== STEP 2: BASE-level hazard profile =====
    print("\n" + "=" * 60)
    print("STEP 2: BASE-level hazard profile")
    print("=" * 60)

    base_hazard = defaultdict(lambda: {'total': 0, 'source': 0, 'target': 0,
                                        'class_counts': Counter(), 'head_counts': Counter()})
    for t in tokens:
        b = t['base']
        base_hazard[b]['total'] += 1
        base_hazard[b]['head_counts'][t['head']] += 1
        if t['is_hazard_source']:
            base_hazard[b]['source'] += 1
            for cls in t['source_classes']:
                base_hazard[b]['class_counts'][cls] += 1
        if t['is_hazard_target']:
            base_hazard[b]['target'] += 1

    base_results = {}
    total_source = len(hazard_source_tokens)
    total_target = len(hazard_target_tokens)
    baseline_source_rate = total_source / total_tokens
    baseline_target_rate = total_target / total_tokens

    print(f"\nBaseline hazard source rate: {baseline_source_rate*100:.2f}%")
    print(f"Baseline hazard target rate: {baseline_target_rate*100:.2f}%")

    print(f"\n{'Base':<8} {'N':>7} {'Src%':>7} {'Tgt%':>7} {'SrcEnr':>8} {'TgtEnr':>8} "
          f"{'PH_ORD':>7} {'COMP_J':>7} {'CONT_T':>7} {'RATE_M':>7} {'E_OVER':>7}")

    for b in sorted(base_hazard.keys()):
        d = base_hazard[b]
        if d['total'] < 20:
            continue
        src_rate = d['source'] / d['total']
        tgt_rate = d['target'] / d['total']
        src_enr = src_rate / baseline_source_rate if baseline_source_rate > 0 else 0
        tgt_enr = tgt_rate / baseline_target_rate if baseline_target_rate > 0 else 0

        base_results[b] = {
            'total': d['total'],
            'source_count': d['source'],
            'source_rate': round(src_rate * 100, 2),
            'source_enrichment': round(src_enr, 3),
            'target_count': d['target'],
            'target_rate': round(tgt_rate * 100, 2),
            'target_enrichment': round(tgt_enr, 3),
            'class_distribution': {cls: d['class_counts'].get(cls, 0) for cls in HAZARD_CLASSES},
            'head_distribution': dict(d['head_counts']),
        }

        print(f"{b:<8} {d['total']:>7} {src_rate*100:>6.1f}% {tgt_rate*100:>6.1f}% "
              f"{src_enr:>7.2f}x {tgt_enr:>7.2f}x "
              f"{d['class_counts'].get('PHASE_ORDERING',0):>7} "
              f"{d['class_counts'].get('COMPOSITION_JUMP',0):>7} "
              f"{d['class_counts'].get('CONTAINMENT_TIMING',0):>7} "
              f"{d['class_counts'].get('RATE_MISMATCH',0):>7} "
              f"{d['class_counts'].get('ENERGY_OVERSHOOT',0):>7}")

    # Test base -> hazard class association
    base_class_table = {}
    for b in base_hazard:
        if base_hazard[b]['total'] >= 20:
            base_class_table[b] = {}
            for cls in HAZARD_CLASSES:
                base_class_table[b][cls] = base_hazard[b]['class_counts'].get(cls, 0)
            base_class_table[b]['SAFE'] = base_hazard[b]['total'] - base_hazard[b]['source']

    base_v = cramers_v(base_class_table)
    base_chi2 = chi2_stat(base_class_table)
    print(f"\nBase -> hazard class+safe: chi2={base_chi2:.1f}, V={base_v:.3f}")

    results['base_hazard_profiles'] = base_results
    results['base_hazard_association'] = {
        'chi2': round(base_chi2, 1),
        'cramers_v': round(base_v, 4),
    }

    # ===== STEP 3: MODIFIER effects on hazard within base =====
    print("\n" + "=" * 60)
    print("STEP 3: MODIFIER effects on hazard (within base)")
    print("=" * 60)

    base_mod_hazard = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'source': 0,
                                                                 'class_counts': Counter()}))
    for t in tokens:
        b = t['base']
        mod = t['modifier']
        base_mod_hazard[b][mod]['total'] += 1
        if t['is_hazard_source']:
            base_mod_hazard[b][mod]['source'] += 1
            for cls in t['source_classes']:
                base_mod_hazard[b][mod]['class_counts'][cls] += 1

    modifier_effects = {}
    for b in sorted(base_mod_hazard.keys()):
        if base_hazard[b]['total'] < 50:
            continue
        print(f"\nBase '{b}' modifiers:")
        mods = base_mod_hazard[b]
        base_total_src = base_hazard[b]['source']
        base_total_n = base_hazard[b]['total']
        base_rate = base_total_src / base_total_n if base_total_n > 0 else 0

        modifier_effects[b] = {'base_rate': round(base_rate * 100, 2), 'modifiers': {}}

        for mod in sorted(mods.keys()):
            d = mods[mod]
            if d['total'] < 10:
                continue
            rate = d['source'] / d['total']
            enr = rate / base_rate if base_rate > 0 else (float('inf') if d['source'] > 0 else 0)

            modifier_effects[b]['modifiers'][str(mod)] = {
                'total': d['total'],
                'source_count': d['source'],
                'source_rate': round(rate * 100, 2),
                'enrichment_vs_base': round(enr, 3) if enr != float('inf') else 'inf',
                'class_counts': {cls: d['class_counts'].get(cls, 0) for cls in HAZARD_CLASSES}
            }

            print(f"  mod={str(mod):<6} N={d['total']:>5} src={d['source']:>4} "
                  f"rate={rate*100:>6.1f}% enr={enr:>5.2f}x "
                  f"PO={d['class_counts'].get('PHASE_ORDERING',0)} "
                  f"CJ={d['class_counts'].get('COMPOSITION_JUMP',0)} "
                  f"CT={d['class_counts'].get('CONTAINMENT_TIMING',0)}")

    results['modifier_effects'] = modifier_effects

    # ===== STEP 4: Sister pair hazard comparison =====
    print("\n" + "=" * 60)
    print("STEP 4: Sister pair hazard comparison")
    print("=" * 60)

    sister_pairs = {
        'ch_vs_sh': ('ch', 'sh'),
        'ok_vs_ot': ('ok', 'ot'),
        'da_vs_sa': ('da', 'sa'),
        'da_vs_ta': ('da', 'ta'),
        'da_vs_ka': ('da', 'ka'),
    }

    sister_results = {}
    for name, (s1, s2) in sister_pairs.items():
        d1 = prefix_hazard.get(s1, {'total': 0, 'source': 0, 'target': 0, 'class_counts': Counter()})
        d2 = prefix_hazard.get(s2, {'total': 0, 'source': 0, 'target': 0, 'class_counts': Counter()})

        if d1['total'] < 10 or d2['total'] < 10:
            continue

        r1 = d1['source'] / d1['total']
        r2 = d2['source'] / d2['total']
        ratio = r1 / r2 if r2 > 0 else float('inf')

        sister_results[name] = {
            s1: {
                'total': d1['total'],
                'source_count': d1['source'],
                'source_rate': round(r1 * 100, 2),
                'target_count': d1['target'],
                'target_rate': round(d1['target'] / d1['total'] * 100, 2),
                'class_distribution': {cls: d1['class_counts'].get(cls, 0) for cls in HAZARD_CLASSES}
            },
            s2: {
                'total': d2['total'],
                'source_count': d2['source'],
                'source_rate': round(r2 * 100, 2),
                'target_count': d2['target'],
                'target_rate': round(d2['target'] / d2['total'] * 100, 2),
                'class_distribution': {cls: d2['class_counts'].get(cls, 0) for cls in HAZARD_CLASSES}
            },
            'rate_ratio': round(ratio, 3) if ratio != float('inf') else 'inf',
        }

        print(f"\n{name}:")
        print(f"  {s1}: N={d1['total']}, source={d1['source']} ({r1*100:.1f}%), target={d1['target']}")
        print(f"  {s2}: N={d2['total']}, source={d2['source']} ({r2*100:.1f}%), target={d2['target']}")
        print(f"  Rate ratio ({s1}/{s2}): {ratio:.3f}")
        for cls in HAZARD_CLASSES:
            c1 = d1['class_counts'].get(cls, 0)
            c2 = d2['class_counts'].get(cls, 0)
            if c1 > 0 or c2 > 0:
                print(f"  {cls}: {s1}={c1}, {s2}={c2}")

    results['sister_pair_hazard'] = sister_results

    # ===== STEP 5: a-base headless -> PHASE_ORDERING pathway =====
    print("\n" + "=" * 60)
    print("STEP 5: a-base headless -> PHASE_ORDERING pathway")
    print("=" * 60)

    # Headless tokens that are hazard sources
    headless_source = [t for t in tokens if t['head'] == 'HEADLESS' and t['is_hazard_source']]
    headed_source = [t for t in tokens if t['head'] != 'HEADLESS' and t['is_hazard_source']]
    headless_total = sum(1 for t in tokens if t['head'] == 'HEADLESS')
    headed_total = sum(1 for t in tokens if t['head'] != 'HEADLESS')

    headless_rate = len(headless_source) / headless_total if headless_total > 0 else 0
    headed_rate = len(headed_source) / headed_total if headed_total > 0 else 0

    print(f"\nHeadless tokens: {headless_total} ({100*headless_total/total_tokens:.1f}%)")
    print(f"Headless hazard source: {len(headless_source)} ({headless_rate*100:.2f}%)")
    print(f"Headed hazard source: {len(headed_source)} ({headed_rate*100:.2f}%)")
    print(f"Headless/headed source ratio: {headless_rate/headed_rate:.3f}x" if headed_rate > 0 else "  headed rate=0")

    # a-base tokens specifically
    a_base_tokens = [t for t in tokens if t['base'] == 'a']
    a_base_source = [t for t in a_base_tokens if t['is_hazard_source']]

    print(f"\na-base tokens: {len(a_base_tokens)}")
    print(f"a-base hazard sources: {len(a_base_source)}")
    if a_base_source:
        a_source_middles = Counter(t['middle'] for t in a_base_source)
        print(f"a-base source MIDDLEs: {dict(a_source_middles)}")
        a_source_classes = Counter()
        for t in a_base_source:
            for cls in t['source_classes']:
                a_source_classes[cls] += 1
        print(f"a-base source by class: {dict(a_source_classes)}")

    # Which bases contribute to PHASE_ORDERING specifically?
    po_source_by_base = Counter()
    po_source_by_prefix = Counter()
    po_total_by_base = Counter()
    for t in tokens:
        po_total_by_base[t['base']] += 1
        if 'PHASE_ORDERING' in t['source_classes']:
            po_source_by_base[t['base']] += 1
            po_source_by_prefix[t['prefix']] += 1

    print(f"\nPHASE_ORDERING sources by base:")
    for b in sorted(po_source_by_base.keys(), key=lambda x: -po_source_by_base[x]):
        n = po_source_by_base[b]
        tot = po_total_by_base[b]
        print(f"  base={b}: {n} sources ({n/tot*100:.2f}% of {tot} tokens)")

    print(f"\nPHASE_ORDERING sources by PREFIX:")
    for pfx in sorted(po_source_by_prefix.keys(), key=lambda x: -po_source_by_prefix[x]):
        print(f"  PREFIX={pfx}: {po_source_by_prefix[pfx]}")

    results['headless_hazard_pathway'] = {
        'headless_total': headless_total,
        'headless_source_count': len(headless_source),
        'headless_source_rate': round(headless_rate * 100, 3),
        'headed_total': headed_total,
        'headed_source_count': len(headed_source),
        'headed_source_rate': round(headed_rate * 100, 3),
        'headless_headed_ratio': round(headless_rate / headed_rate, 3) if headed_rate > 0 else None,
        'a_base_total': len(a_base_tokens),
        'a_base_source_count': len(a_base_source),
        'po_source_by_base': dict(po_source_by_base),
        'po_source_by_prefix': dict(po_source_by_prefix),
    }

    # ===== STEP 6: qo k-HEAD routing -> hazard immunity =====
    print("\n" + "=" * 60)
    print("STEP 6: qo k-HEAD routing -> hazard immunity")
    print("=" * 60)

    # k-HEAD tokens hazard profile
    k_head_tokens = [t for t in tokens if t['head'] == 'k']
    k_head_source = [t for t in k_head_tokens if t['is_hazard_source']]

    # qo tokens hazard profile
    qo_tokens = [t for t in tokens if t['prefix'] == 'qo']
    qo_source = [t for t in qo_tokens if t['is_hazard_source']]
    qo_k_head = [t for t in qo_tokens if t['head'] == 'k']
    qo_non_k = [t for t in qo_tokens if t['head'] != 'k']
    qo_non_k_source = [t for t in qo_non_k if t['is_hazard_source']]

    print(f"\nk-HEAD total: {len(k_head_tokens)}")
    print(f"k-HEAD hazard sources: {len(k_head_source)} ({len(k_head_source)/len(k_head_tokens)*100:.2f}%)" if k_head_tokens else "  k-HEAD: 0 tokens")
    print(f"\nqo total: {len(qo_tokens)}")
    print(f"qo hazard sources: {len(qo_source)} ({len(qo_source)/len(qo_tokens)*100:.2f}%)" if qo_tokens else "  qo: 0 tokens")
    print(f"qo k-HEAD: {len(qo_k_head)} ({len(qo_k_head)/len(qo_tokens)*100:.1f}%)" if qo_tokens else "")
    print(f"qo non-k-HEAD: {len(qo_non_k)} (source: {len(qo_non_k_source)})")

    # Per-HEAD hazard rates
    head_hazard = defaultdict(lambda: {'total': 0, 'source': 0})
    for t in tokens:
        head_hazard[t['head']]['total'] += 1
        if t['is_hazard_source']:
            head_hazard[t['head']]['source'] += 1

    print(f"\nHazard source rate by HEAD atom:")
    for h in sorted(head_hazard.keys()):
        d = head_hazard[h]
        rate = d['source'] / d['total'] * 100 if d['total'] > 0 else 0
        print(f"  {h}: {d['source']}/{d['total']} = {rate:.2f}%")

    # o-base modifiers -> hazard rate (is q special?)
    o_base_mods = base_mod_hazard.get('o', {})
    print(f"\no-base modifier hazard rates:")
    for mod in sorted(o_base_mods.keys()):
        d = o_base_mods[mod]
        if d['total'] < 10:
            continue
        rate = d['source'] / d['total'] * 100
        print(f"  {mod}o: N={d['total']}, source={d['source']}, rate={rate:.2f}%")

    results['khead_qo_immunity'] = {
        'k_head_total': len(k_head_tokens),
        'k_head_source': len(k_head_source),
        'k_head_source_rate': round(len(k_head_source)/len(k_head_tokens)*100, 3) if k_head_tokens else 0,
        'qo_total': len(qo_tokens),
        'qo_source': len(qo_source),
        'qo_source_rate': round(len(qo_source)/len(qo_tokens)*100, 3) if qo_tokens else 0,
        'qo_k_head_count': len(qo_k_head),
        'qo_non_k_source': len(qo_non_k_source),
        'head_hazard_rates': {h: {'total': d['total'], 'source': d['source'],
                                   'rate': round(d['source']/d['total']*100, 3) if d['total'] > 0 else 0}
                              for h, d in head_hazard.items()},
    }

    # ===== STEP 7: CHSH PHASE_ORDERING mechanism =====
    print("\n" + "=" * 60)
    print("STEP 7: CHSH PHASE_ORDERING mechanism")
    print("=" * 60)

    # PHASE_ORDERING source MIDDLEs: dy, shey, chey
    po_middles = HAZARD_CLASS_SOURCES['PHASE_ORDERING']
    print(f"\nPHASE_ORDERING source MIDDLEs: {po_middles}")

    # For each PO source MIDDLE, what PREFIX is it used with?
    po_prefix_middle = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        if t['middle'] in po_middles:
            po_prefix_middle[t['middle']][t['prefix']] += 1

    print(f"\nPHASE_ORDERING source MIDDLE x PREFIX distribution:")
    for mid in sorted(po_middles):
        pfx_dist = po_prefix_middle[mid]
        total = sum(pfx_dist.values())
        print(f"\n  MIDDLE '{mid}' (N={total}):")
        for pfx in sorted(pfx_dist.keys(), key=lambda x: -pfx_dist[x]):
            print(f"    {pfx}: {pfx_dist[pfx]} ({pfx_dist[pfx]/total*100:.1f}%)")

    # HEAD and TERMINAL of PHASE_ORDERING sources
    po_head_dist = Counter()
    po_term_dist = Counter()
    for t in tokens:
        if 'PHASE_ORDERING' in t['source_classes']:
            po_head_dist[t['head']] += 1
            po_term_dist[t['terminal']] += 1

    print(f"\nPHASE_ORDERING source HEAD distribution: {dict(po_head_dist)}")
    print(f"PHASE_ORDERING source TERMINAL distribution: {dict(po_term_dist)}")

    # COMPOSITION_JUMP similarly
    cj_middles = HAZARD_CLASS_SOURCES['COMPOSITION_JUMP']
    print(f"\nCOMPOSITION_JUMP source MIDDLEs: {cj_middles}")
    cj_prefix_middle = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        if t['middle'] in cj_middles:
            cj_prefix_middle[t['middle']][t['prefix']] += 1

    for mid in sorted(cj_middles):
        pfx_dist = cj_prefix_middle[mid]
        total = sum(pfx_dist.values())
        if total > 0:
            print(f"\n  MIDDLE '{mid}' (N={total}):")
            for pfx in sorted(pfx_dist.keys(), key=lambda x: -pfx_dist[x]):
                print(f"    {pfx}: {pfx_dist[pfx]} ({pfx_dist[pfx]/total*100:.1f}%)")
        else:
            print(f"\n  MIDDLE '{mid}': PHANTOM (0 corpus tokens)")

    # CONTAINMENT_TIMING sources
    ct_middles = HAZARD_CLASS_SOURCES['CONTAINMENT_TIMING']
    print(f"\nCONTAINMENT_TIMING source MIDDLEs: {ct_middles}")
    ct_prefix_middle = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        if t['middle'] in ct_middles:
            ct_prefix_middle[t['middle']][t['prefix']] += 1

    for mid in sorted(ct_middles):
        pfx_dist = ct_prefix_middle[mid]
        total = sum(pfx_dist.values())
        if total > 0:
            print(f"\n  MIDDLE '{mid}' (N={total}):")
            for pfx in sorted(pfx_dist.keys(), key=lambda x: -pfx_dist[x]):
                print(f"    {pfx}: {pfx_dist[pfx]} ({pfx_dist[pfx]/total*100:.1f}%)")
        else:
            print(f"\n  MIDDLE '{mid}': PHANTOM (0 corpus tokens)")

    # Mechanism: why CHSH-specific?
    # ch/sh = h-base per C1534. h-base selects e-HEAD at 65.7%.
    # dy, chey, shey are all y-terminal = OPERATION/TRANSITION.
    # dy HEAD = 'd' = headless. chey HEAD = 'HEADLESS' (c not in HEAD_ATOMS). shey HEAD = 'HEADLESS'.
    # Wait - let's check actual HEADs of these MIDDLEs
    print(f"\nMechanism analysis:")
    for mid in ['dy', 'chey', 'shey', 'chedy', 'shedy', 'chol', 'l', 'c', 'he']:
        head = get_head(mid)
        term = get_terminal(mid)
        print(f"  '{mid}': HEAD={head}, TERMINAL={term}")

    results['chsh_mechanism'] = {
        'po_source_middles': {mid: dict(po_prefix_middle[mid]) for mid in po_middles},
        'cj_source_middles': {mid: dict(cj_prefix_middle[mid]) for mid in cj_middles},
        'ct_source_middles': {mid: dict(ct_prefix_middle[mid]) for mid in ct_middles},
        'po_head_distribution': dict(po_head_dist),
        'po_terminal_distribution': dict(po_term_dist),
    }

    # ===== STEP 8: Safe token PREFIX clustering =====
    print("\n" + "=" * 60)
    print("STEP 8: Safe token clustering by PREFIX")
    print("=" * 60)

    # "Immune" = k-HEAD (C1446)
    immune_tokens = [t for t in tokens if t['head'] == 'k']
    immune_by_prefix = Counter(t['prefix'] for t in immune_tokens)
    immune_by_base = Counter(t['base'] for t in immune_tokens)

    print(f"\nk-HEAD (immune) tokens by PREFIX base:")
    for b in sorted(immune_by_base.keys(), key=lambda x: -immune_by_base[x]):
        n = immune_by_base[b]
        base_n = base_hazard[b]['total']
        print(f"  base={b}: {n} ({n/base_n*100:.1f}% of base, {n/len(immune_tokens)*100:.1f}% of immune)")

    # e->y safe pathway (C1457-C1462)
    ey_frame = [t for t in tokens if t['head'] == 'e' and t['terminal'] == 'y']
    ey_by_prefix = Counter(t['prefix'] for t in ey_frame)
    ey_by_base = Counter(t['base'] for t in ey_frame)

    print(f"\ne->y frame (zero hazard anchor) by PREFIX base:")
    for b in sorted(ey_by_base.keys(), key=lambda x: -ey_by_base[x]):
        n = ey_by_base[b]
        base_n = base_hazard[b]['total']
        print(f"  base={b}: {n} ({n/base_n*100:.1f}% of base, {n/len(ey_frame)*100:.1f}% of e->y)")

    # Full safety profile: ZERO hazard source rate PREFIXes (N>=50)
    zero_hazard_prefixes = []
    for pfx, d in prefix_hazard.items():
        if d['total'] >= 50 and d['source'] == 0:
            zero_hazard_prefixes.append((pfx, d['total']))

    zero_hazard_prefixes.sort(key=lambda x: -x[1])
    print(f"\nPREFIXes with ZERO hazard source (N>=50):")
    for pfx, n in zero_hazard_prefixes:
        print(f"  {pfx}: N={n}")

    results['safe_clustering'] = {
        'immune_by_base': dict(immune_by_base),
        'ey_frame_by_base': dict(ey_by_base),
        'zero_hazard_prefixes': {pfx: n for pfx, n in zero_hazard_prefixes},
    }

    # ===== STEP 9: HEAD x hazard_class contingency =====
    print("\n" + "=" * 60)
    print("STEP 9: HEAD x hazard class contingency")
    print("=" * 60)

    head_class_table = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        h = t['head']
        if t['source_classes']:
            for cls in t['source_classes']:
                head_class_table[h][cls] += 1
        else:
            head_class_table[h]['SAFE'] += 1

    head_v = cramers_v(dict(head_class_table))
    head_chi2 = chi2_stat(dict(head_class_table))
    print(f"\nHEAD x hazard_class+SAFE: chi2={head_chi2:.1f}, V={head_v:.4f}")

    print(f"\n{'HEAD':<12} {'SAFE':>7} {'PH_ORD':>7} {'COMP_J':>7} {'CONT_T':>7} {'RATE_M':>7} {'E_OVER':>7}")
    for h in sorted(head_class_table.keys()):
        d = head_class_table[h]
        print(f"{h:<12} {d.get('SAFE',0):>7} {d.get('PHASE_ORDERING',0):>7} "
              f"{d.get('COMPOSITION_JUMP',0):>7} {d.get('CONTAINMENT_TIMING',0):>7} "
              f"{d.get('RATE_MISMATCH',0):>7} {d.get('ENERGY_OVERSHOOT',0):>7}")

    results['head_hazard_contingency'] = {
        'chi2': round(head_chi2, 1),
        'cramers_v': round(head_v, 4),
        'table': {h: dict(d) for h, d in head_class_table.items()},
    }

    # ===== STEP 10: TERMINAL x hazard class =====
    print("\n" + "=" * 60)
    print("STEP 10: TERMINAL x hazard class")
    print("=" * 60)

    term_class_table = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        term = t['terminal']
        if t['source_classes']:
            for cls in t['source_classes']:
                term_class_table[term][cls] += 1
        else:
            term_class_table[term]['SAFE'] += 1

    term_v = cramers_v(dict(term_class_table))
    term_chi2 = chi2_stat(dict(term_class_table))
    print(f"\nTERMINAL x hazard_class+SAFE: chi2={term_chi2:.1f}, V={term_v:.4f}")

    print(f"\n{'TERM':<10} {'SAFE':>7} {'PH_ORD':>7} {'COMP_J':>7} {'CONT_T':>7} {'RATE_M':>7} {'E_OVER':>7}")
    for term in sorted(term_class_table.keys()):
        d = term_class_table[term]
        print(f"{term:<10} {d.get('SAFE',0):>7} {d.get('PHASE_ORDERING',0):>7} "
              f"{d.get('COMPOSITION_JUMP',0):>7} {d.get('CONTAINMENT_TIMING',0):>7} "
              f"{d.get('RATE_MISMATCH',0):>7} {d.get('ENERGY_OVERSHOOT',0):>7}")

    results['terminal_hazard_contingency'] = {
        'chi2': round(term_chi2, 1),
        'cramers_v': round(term_v, 4),
        'table': {t: dict(d) for t, d in term_class_table.items()},
    }

    # ===== STEP 11: Full PREFIX base x HEAD x hazard interaction =====
    print("\n" + "=" * 60)
    print("STEP 11: Base x HEAD x hazard three-way")
    print("=" * 60)

    # For each base, what HEAD domains does it route hazard sources through?
    base_head_hazard = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'source': 0}))
    for t in tokens:
        b = t['base']
        h = t['head']
        base_head_hazard[b][h]['total'] += 1
        if t['is_hazard_source']:
            base_head_hazard[b][h]['source'] += 1

    print(f"\nBase x HEAD hazard source rates (N>=20):")
    for b in sorted(base_head_hazard.keys()):
        if base_hazard[b]['total'] < 50:
            continue
        print(f"\n  Base '{b}':")
        for h in sorted(base_head_hazard[b].keys()):
            d = base_head_hazard[b][h]
            if d['total'] < 5:
                continue
            rate = d['source'] / d['total'] * 100
            print(f"    HEAD={h}: {d['source']}/{d['total']} = {rate:.2f}%")

    results['base_head_hazard'] = {
        b: {h: {'total': d['total'], 'source': d['source'],
                'rate': round(d['source']/d['total']*100, 3) if d['total'] > 0 else 0}
            for h, d in heads.items() if d['total'] >= 5}
        for b, heads in base_head_hazard.items()
        if base_hazard[b]['total'] >= 50
    }

    # ===== SYNTHESIS =====
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    # Key finding 1: Which bases are hazard feeders vs hazard-free?
    hazard_bases = [(b, d['source_rate']) for b, d in base_results.items() if d['source_rate'] > baseline_source_rate * 100]
    safe_bases = [(b, d['source_rate']) for b, d in base_results.items() if d['source_rate'] == 0]

    print(f"\nHazard-enriched bases: {[(b, f'{r:.1f}%') for b, r in sorted(hazard_bases, key=lambda x: -x[1])]}")
    print(f"Zero-hazard bases: {[(b, f'{r:.1f}%') for b, r in safe_bases]}")

    # Key finding 2: Does base predict hazard class?
    print(f"\nBase -> hazard+safe association: V={base_v:.4f}")

    # Key finding 3: k-HEAD immunity chain
    k_immune_pct = results['khead_qo_immunity']['k_head_source_rate']
    qo_immune_pct = results['khead_qo_immunity']['qo_source_rate']
    print(f"\nk-HEAD hazard source rate: {k_immune_pct:.3f}%")
    print(f"qo hazard source rate: {qo_immune_pct:.3f}%")
    print(f"Chain: qo -> 64% k-HEAD (C1538) -> 0% hazard source (C1476) -> near-total PREFIX-level immunity")

    # Key finding 4: PHASE_ORDERING = headless pathway
    po_headless = po_head_dist.get('HEADLESS', 0)
    po_total = sum(po_head_dist.values())
    print(f"\nPHASE_ORDERING is {po_headless/po_total*100:.1f}% HEADLESS-origin" if po_total > 0 else "")

    # Save results
    outpath = 'C:/git/voynich/phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json'
    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")


if __name__ == '__main__':
    main()

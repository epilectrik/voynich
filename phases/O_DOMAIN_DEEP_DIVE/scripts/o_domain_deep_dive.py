"""
Phase 548: o-Domain Deep Dive
========================================
Comprehensive analysis of o-HEAD domain across all 10 research questions:
  T1: Terminal profile comparison (o vs other HEADs)
  T2: Modifier profile comparison
  T3: Suffix behavior (rate, mode, atom composition)
  T4: Cross-system A vs B vs AZC distribution
  T5: AZC zone analysis (which zones, which o-MIDDLEs)
  T6: Instruction class mapping
  T7: Hazard relationship (source/target)
  T8: o vs e HEAD comparison
  T9: Line position profile and zone routing
  T10: Cross-token transitions (what follows/precedes o-HEAD)

Output: phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

# ============================================================
# Constants
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}
MODIFIERS = {'p', 'c', 'i', 'f', 'd', 's'}
ALL_CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
                  'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

# 17 forbidden MIDDLE-level pairs (C109)
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
FORBIDDEN_SET = set(FORBIDDEN_PAIRS)
FORBIDDEN_SOURCES = set(src for src, _ in FORBIDDEN_PAIRS)
FORBIDDEN_TARGETS = set(tgt for _, tgt in FORBIDDEN_PAIRS)

# Terminal suffix sets for Mode A/B classification (C1229, C1231)
TERMINAL_SUFFIXES = {'edy', 'ey', 'eey', 'dy', 'y', 'hy', 'ry', 'ly', 'eedy', 'chy', 'shy'}

# Section assignment for B folios
SECTION_MAP = {}  # will populate from data


# ============================================================
# Utility functions
# ============================================================

def jsd(p, q, categories):
    """Jensen-Shannon divergence between two distributions."""
    eps = 1e-12
    m = {}
    for c in categories:
        m[c] = 0.5 * (p.get(c, 0) + q.get(c, 0))

    kl_pm = 0.0
    kl_qm = 0.0
    for c in categories:
        pc = p.get(c, 0) + eps
        qc = q.get(c, 0) + eps
        mc = m[c] + eps
        kl_pm += pc * math.log2(pc / mc)
        kl_qm += qc * math.log2(qc / mc)

    return 0.5 * kl_pm + 0.5 * kl_qm


def normalize(counter, categories=None):
    """Normalize a counter to probability distribution."""
    total = sum(counter.values())
    if total == 0:
        return {}
    if categories:
        return {c: counter.get(c, 0) / total for c in categories}
    return {k: v / total for k, v in counter.items()}


def enrichment(head_count, head_total, base_count, base_total):
    """Enrichment ratio with protection."""
    if head_total == 0 or base_total == 0 or base_count == 0:
        return None
    head_rate = head_count / head_total
    base_rate = base_count / base_total
    if base_rate == 0:
        return None
    return round(head_rate / base_rate, 3)


def chi2_stat(observed, expected):
    """Chi-square statistic from observed and expected counts."""
    chi2 = 0
    for k in set(list(observed.keys()) + list(expected.keys())):
        obs = observed.get(k, 0)
        exp = expected.get(k, 0)
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp
    return chi2


def cramers_v(chi2, n, k):
    """Cramer's V from chi-squared."""
    if n == 0 or k <= 1:
        return 0
    return math.sqrt(chi2 / (n * (k - 1)))


def get_zone(placement):
    """AZC zone from placement code."""
    if not placement:
        return None
    if placement.startswith('R'):
        return 'R'
    elif placement.startswith('C'):
        return 'C'
    elif placement.startswith('S'):
        return 'S'
    elif placement.startswith('P'):
        return 'P'
    elif placement.startswith('L'):
        return 'L'
    return None


# ============================================================
# Data Loading
# ============================================================

def collect_b_data():
    """Collect all Currier B tokens with full decomposition."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    tokens_by_folio_line = defaultdict(list)
    all_tokens = []

    for tok in tx.currier_b():
        word = tok.word
        if not word or not word.strip() or '*' in word:
            continue
        m = morph.extract(word)
        if not m or not m.middle:
            continue

        head, mods, term, frame_str = decompose_middle_hmt(m.middle)
        category = cc.classify(m.middle)
        suffix = m.suffix or ''
        suffix_mode = 'A' if suffix in TERMINAL_SUFFIXES else 'B'

        # Suffix first atom (for suffix composition analysis)
        suf_first = suffix[0] if suffix else None

        entry = {
            'word': word,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': suffix,
            'has_suffix': bool(suffix),
            'articulator': m.articulator,
            'category': category,
            'head': head,
            'mods': mods,
            'term': term or 'bare',
            'frame_str': frame_str,
            'suffix_mode': suffix_mode,
            'suf_first': suf_first,
            'in_forbidden_src': m.middle in FORBIDDEN_SOURCES,
            'in_forbidden_tgt': m.middle in FORBIDDEN_TARGETS,
            'section': tok.section if hasattr(tok, 'section') else None,
        }

        key = (tok.folio, tok.line)
        tokens_by_folio_line[key].append(entry)
        all_tokens.append(entry)

    # Compute line position quintiles and initial/final flags
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
            entry['is_line_initial'] = (idx == 0)
            entry['is_line_final'] = (idx == n - 1)
            entry['line_idx'] = idx
            entry['line_len'] = n

    return all_tokens, tokens_by_folio_line


def collect_cross_system_data():
    """Collect tokens from all 3 systems."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    data = {'A': [], 'B': [], 'AZC': []}

    for tok in tx.currier_a():
        w = tok.word
        if not w or not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        head, mods, term, frame = decompose_middle_hmt(m.middle)
        data['A'].append({
            'word': w, 'folio': tok.folio, 'middle': m.middle,
            'prefix': m.prefix, 'suffix': m.suffix or '',
            'head': head, 'mods': mods, 'term': term or 'bare',
            'category': cc.classify(m.middle),
        })

    for tok in tx.currier_b():
        w = tok.word
        if not w or not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        head, mods, term, frame = decompose_middle_hmt(m.middle)
        data['B'].append({
            'word': w, 'folio': tok.folio, 'middle': m.middle,
            'prefix': m.prefix, 'suffix': m.suffix or '',
            'head': head, 'mods': mods, 'term': term or 'bare',
            'category': cc.classify(m.middle),
        })

    for tok in tx.azc():
        w = tok.word
        if not w or not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        if not m or not m.middle:
            continue
        head, mods, term, frame = decompose_middle_hmt(m.middle)
        data['AZC'].append({
            'word': w, 'folio': tok.folio, 'middle': m.middle,
            'prefix': m.prefix, 'suffix': m.suffix or '',
            'head': head, 'mods': mods, 'term': term or 'bare',
            'category': cc.classify(m.middle),
            'placement': tok.placement,
            'zone': get_zone(tok.placement),
        })

    return data


# ============================================================
# T1: Terminal Profile
# ============================================================

def test_terminal_profile(all_tokens):
    """Compare o-HEAD terminal profile against all other HEADs."""
    terminal_cats = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']

    head_terms = defaultdict(Counter)
    for t in all_tokens:
        h = t['head'] if t['head'] else 'HEADLESS'
        head_terms[h][t['term']] += 1

    results = {}
    baseline = Counter()
    baseline_total = 0
    for h in list(HEADS) + ['HEADLESS']:
        for term in terminal_cats:
            baseline[term] += head_terms.get(h, {}).get(term, 0)
        baseline_total += sum(head_terms.get(h, Counter()).values())

    for h in list(HEADS) + ['HEADLESS']:
        total = sum(head_terms[h].values())
        dist = normalize(head_terms[h], terminal_cats)
        enr = {}
        for term in terminal_cats:
            enr[term] = enrichment(head_terms[h].get(term, 0), total,
                                    baseline.get(term, 0), baseline_total)
        results[h] = {
            'n': total,
            'distribution': dist,
            'enrichment': enr,
            'dominant': max(dist, key=dist.get) if dist else None,
        }

    # o-specific signature
    o_dist = results['o']['distribution']
    o_signature = {
        'l_rate': round(o_dist.get('l', 0), 4),
        'r_rate': round(o_dist.get('r', 0), 4),
        'h_rate': round(o_dist.get('h', 0), 4),
        'bare_rate': round(o_dist.get('bare', 0), 4),
        'y_rate': round(o_dist.get('y', 0), 4),
        'n_rate': round(o_dist.get('n', 0), 4),
        'l_plus_r': round(o_dist.get('l', 0) + o_dist.get('r', 0), 4),
        'note': 'o avoids y (0.007x) and n (0.15x), favors l (2.57x) and r (1.97x)',
    }

    # Pairwise JSD between o and each other HEAD
    o_norm = normalize(head_terms['o'], terminal_cats)
    jsd_pairs = {}
    for h in ['a', 'e', 'k', 't', 'HEADLESS']:
        h_norm = normalize(head_terms[h], terminal_cats)
        jsd_pairs[h] = round(jsd(o_norm, h_norm, terminal_cats), 4)

    return {
        'per_head': results,
        'o_signature': o_signature,
        'jsd_from_o': jsd_pairs,
    }


# ============================================================
# T2: Modifier Profile
# ============================================================

def test_modifier_profile(all_tokens):
    """Compare o-HEAD modifier usage against other HEADs."""
    mod_chars = list('pcifds')

    head_mods = defaultdict(Counter)
    head_totals = Counter()

    for t in all_tokens:
        h = t['head'] if t['head'] else 'HEADLESS'
        head_totals[h] += 1
        for mod in t['mods']:
            if mod in MODIFIERS:
                head_mods[h][mod] += 1

    # Baseline rates
    all_total = sum(head_totals.values())
    all_mod_counts = Counter()
    for h in head_mods:
        for mod, cnt in head_mods[h].items():
            all_mod_counts[mod] += cnt

    results = {}
    for h in list(HEADS) + ['HEADLESS']:
        total = head_totals[h]
        rates = {}
        enr = {}
        for mod in mod_chars:
            rates[mod] = round(head_mods[h].get(mod, 0) / total, 4) if total > 0 else 0
            enr[mod] = enrichment(head_mods[h].get(mod, 0), total,
                                   all_mod_counts.get(mod, 0), all_total)
        results[h] = {
            'n': total,
            'modifier_rates': rates,
            'enrichment': enr,
            'any_modifier_rate': round(sum(1 for t in all_tokens if (t['head'] if t['head'] else 'HEADLESS') == h and t['mods']) / total, 4) if total > 0 else 0,
        }

    # o-specific signature
    o_rates = results['o']['enrichment']
    o_signature = {
        'p_enrichment': o_rates.get('p'),
        'f_enrichment': o_rates.get('f'),
        'c_enrichment': o_rates.get('c'),
        'i_enrichment': o_rates.get('i'),
        'd_enrichment': o_rates.get('d'),
        's_enrichment': o_rates.get('s'),
        'note': 'o strongly attracts p (3.51x) and f (2.83x) executive atoms, depletes i (0.32x) and d (0.55x)',
    }

    return {
        'per_head': results,
        'o_signature': o_signature,
    }


# ============================================================
# T3: Suffix Behavior
# ============================================================

def test_suffix_behavior(all_tokens):
    """Analyze o-HEAD suffix rate, mode, and atom composition."""
    head_suffix = defaultdict(lambda: {'has': 0, 'total': 0, 'mode_a': 0, 'suf_first': Counter()})

    for t in all_tokens:
        h = t['head'] if t['head'] else 'HEADLESS'
        head_suffix[h]['total'] += 1
        if t['has_suffix']:
            head_suffix[h]['has'] += 1
            if t['suffix_mode'] == 'A':
                head_suffix[h]['mode_a'] += 1
            if t['suf_first']:
                head_suffix[h]['suf_first'][t['suf_first']] += 1

    results = {}
    for h in list(HEADS) + ['HEADLESS']:
        s = head_suffix[h]
        total = s['total']
        has = s['has']
        mode_a = s['mode_a']

        suf_first_dist = normalize(s['suf_first'])

        results[h] = {
            'n': total,
            'suffix_rate': round(has / total, 4) if total > 0 else 0,
            'mode_a_rate': round(mode_a / total, 4) if total > 0 else 0,
            'mode_b_rate': round((has - mode_a) / total, 4) if total > 0 and has > 0 else 0,
            'suf_first_atom_dist': {k: round(v, 4) for k, v in sorted(suf_first_dist.items(), key=lambda x: -x[1])[:8]},
        }

    # o-HEAD suffix atom first position detail
    o_suf = head_suffix['o']['suf_first']
    o_total_suf = sum(o_suf.values())

    return {
        'per_head': results,
        'o_suffix_first_atom_census': {k: v for k, v in o_suf.most_common()},
        'o_suffix_first_atom_total': o_total_suf,
    }


# ============================================================
# T4: Cross-System A vs B vs AZC
# ============================================================

def test_cross_system(cross_data):
    """Compare o-HEAD usage across A, B, AZC."""
    results = {}

    for sys_name in ['A', 'B', 'AZC']:
        tokens = cross_data[sys_name]
        total = len(tokens)
        o_tokens = [t for t in tokens if t['head'] == 'o']
        o_total = len(o_tokens)

        # o-HEAD rate
        o_rate = o_total / total if total > 0 else 0

        # Type census
        o_middles = Counter(t['middle'] for t in o_tokens)

        # Category distribution
        o_cats = Counter(t['category'] for t in o_tokens if t['category'])
        all_cats = Counter(t['category'] for t in tokens if t['category'])

        o_cat_dist = normalize(o_cats, ALL_CATEGORIES)
        all_cat_dist = normalize(all_cats, ALL_CATEGORIES)

        # Terminal distribution
        o_terms = Counter(t['term'] for t in o_tokens)

        # Prefix distribution
        o_prefixes = Counter(t['prefix'] for t in o_tokens)

        # o-HEAD A vs B enrichment per MIDDLE type
        o_middle_list = sorted(o_middles.items(), key=lambda x: -x[1])[:20]

        results[sys_name] = {
            'total_tokens': total,
            'o_head_tokens': o_total,
            'o_head_rate': round(o_rate, 4),
            'o_head_types': len(o_middles),
            'top_o_middles': [(m, c) for m, c in o_middle_list],
            'category_dist': {k: round(v, 4) for k, v in o_cat_dist.items()},
            'terminal_dist': {k: round(v / o_total, 4) for k, v in sorted(o_terms.items(), key=lambda x: -x[1]) if o_total > 0},
            'top_prefixes': [(p, c) for p, c in o_prefixes.most_common(10)],
        }

    # A-B enrichment per o-MIDDLE type
    a_o = Counter(t['middle'] for t in cross_data['A'] if t['head'] == 'o')
    b_o = Counter(t['middle'] for t in cross_data['B'] if t['head'] == 'o')
    a_total = len(cross_data['A'])
    b_total = len(cross_data['B'])

    ab_enrichment = {}
    all_o_middles = set(a_o.keys()) | set(b_o.keys())
    for mid in all_o_middles:
        a_cnt = a_o.get(mid, 0)
        b_cnt = b_o.get(mid, 0)
        a_rate = a_cnt / a_total if a_total > 0 else 0
        b_rate = b_cnt / b_total if b_total > 0 else 0
        if a_rate > 0 and b_rate > 0:
            ratio = b_rate / a_rate
        elif b_rate > 0:
            ratio = float('inf')
        else:
            ratio = 0.0
        if a_cnt + b_cnt >= 10:  # only reliable with enough data
            ab_enrichment[mid] = {
                'A_count': a_cnt, 'B_count': b_cnt,
                'B_to_A_ratio': round(ratio, 3) if ratio != float('inf') else 'B_only',
            }

    # Sort by B-enrichment
    b_enriched = sorted([(m, d) for m, d in ab_enrichment.items()
                         if isinstance(d['B_to_A_ratio'], (int, float)) and d['B_to_A_ratio'] > 1.5],
                        key=lambda x: -x[1]['B_to_A_ratio'])
    a_enriched = sorted([(m, d) for m, d in ab_enrichment.items()
                         if isinstance(d['B_to_A_ratio'], (int, float)) and d['B_to_A_ratio'] < 0.67],
                        key=lambda x: x[1]['B_to_A_ratio'])

    results['a_b_enrichment'] = {
        'B_enriched': b_enriched[:15],
        'A_enriched': a_enriched[:15],
        'total_compared': len(ab_enrichment),
    }

    return results


# ============================================================
# T5: AZC Zone Analysis
# ============================================================

def test_azc_zones(cross_data):
    """Analyze o-HEAD distribution across AZC zones."""
    azc_tokens = cross_data['AZC']

    zone_heads = defaultdict(Counter)
    zone_o_details = defaultdict(lambda: {'terms': Counter(), 'mods': Counter(),
                                           'middles': Counter(), 'cats': Counter()})

    for t in azc_tokens:
        zone = t.get('zone')
        if not zone:
            continue
        h = t['head'] if t['head'] else 'HEADLESS'
        zone_heads[zone][h] += 1

        if t['head'] == 'o':
            zone_o_details[zone]['terms'][t['term']] += 1
            for mod in t['mods']:
                zone_o_details[zone]['mods'][mod] += 1
            zone_o_details[zone]['middles'][t['middle']] += 1
            if t['category']:
                zone_o_details[zone]['cats'][t['category']] += 1

    results = {}
    for zone in ['R', 'C', 'S', 'P', 'L']:
        if zone not in zone_heads:
            continue
        total = sum(zone_heads[zone].values())
        o_cnt = zone_heads[zone].get('o', 0)
        o_rate = o_cnt / total if total > 0 else 0

        head_dist = {}
        for h in list(HEADS) + ['HEADLESS']:
            head_dist[h] = round(zone_heads[zone].get(h, 0) / total, 4) if total > 0 else 0

        o_det = zone_o_details[zone]
        results[zone] = {
            'total': total,
            'o_count': o_cnt,
            'o_rate': round(o_rate, 4),
            'head_distribution': head_dist,
            'o_terminal_dist': normalize(o_det['terms']),
            'o_top_middles': [(m, c) for m, c in o_det['middles'].most_common(8)],
            'o_category_dist': normalize(o_det['cats'], ALL_CATEGORIES) if sum(o_det['cats'].values()) > 0 else {},
        }

    # Zone gradient: o-rate from R (interior) to S (boundary)
    gradient = {}
    for z in ['R', 'C', 'S']:
        if z in results:
            gradient[z] = results[z]['o_rate']

    # bare-o rate by zone (just the atom 'o' by itself)
    bare_o_by_zone = {}
    for zone in ['R', 'C', 'S', 'P', 'L']:
        if zone in zone_o_details:
            o_cnt = zone_o_details[zone]['middles'].get('o', 0)
            total_o = sum(zone_o_details[zone]['middles'].values())
            bare_o_by_zone[zone] = {
                'bare_o_count': o_cnt,
                'total_o': total_o,
                'bare_o_rate': round(o_cnt / total_o, 4) if total_o > 0 else 0,
            }

    results['zone_gradient'] = gradient
    results['bare_o_by_zone'] = bare_o_by_zone

    return results


# ============================================================
# T6: o-HEAD Compound Detail (top MIDDLEs functional decomposition)
# ============================================================

def test_compound_detail(all_tokens):
    """Decompose top o-HEAD MIDDLEs into functional profiles."""
    cc = CategoryClassifier()

    o_tokens = [t for t in all_tokens if t['head'] == 'o']
    o_mid_counter = Counter(t['middle'] for t in o_tokens)

    detail = {}
    for mid, cnt in o_mid_counter.most_common(25):
        # Get tokens for this MIDDLE
        mid_tokens = [t for t in o_tokens if t['middle'] == mid]
        n = len(mid_tokens)

        head, mods, term, frame = decompose_middle_hmt(mid)
        cat = cc.classify(mid)

        # PREFIX distribution
        pfx_counter = Counter(t['prefix'] for t in mid_tokens)

        # Line position
        positions = [t['line_pos_frac'] for t in mid_tokens if 'line_pos_frac' in t]
        mean_pos = sum(positions) / len(positions) if positions else None

        # Suffix info
        suf_rate = sum(1 for t in mid_tokens if t['has_suffix']) / n if n > 0 else 0
        mode_a_rate = sum(1 for t in mid_tokens if t['suffix_mode'] == 'A') / n if n > 0 else 0

        # Line initial/final rates
        initial_rate = sum(1 for t in mid_tokens if t.get('is_line_initial')) / n if n > 0 else 0
        final_rate = sum(1 for t in mid_tokens if t.get('is_line_final')) / n if n > 0 else 0

        detail[mid] = {
            'count': cnt,
            'head': head,
            'modifiers': mods,
            'terminal': term,
            'frame': frame,
            'category': cat,
            'top_prefixes': [(p, c) for p, c in pfx_counter.most_common(5)],
            'mean_line_pos': round(mean_pos, 4) if mean_pos is not None else None,
            'suffix_rate': round(suf_rate, 4),
            'mode_a_rate': round(mode_a_rate, 4),
            'initial_rate': round(initial_rate, 4),
            'final_rate': round(final_rate, 4),
        }

    return detail


# ============================================================
# T7: Hazard Relationship
# ============================================================

def test_hazard_relationship(all_tokens, tokens_by_folio_line):
    """Analyze o-HEAD's hazard exposure: source vs target."""

    # Count forbidden pair involvement
    head_hazard_src = Counter()
    head_hazard_tgt = Counter()
    head_total_src = Counter()
    head_total_tgt = Counter()

    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens) - 1):
            src = line_tokens[i]
            tgt = line_tokens[i + 1]
            src_mid = src['middle']
            tgt_mid = tgt['middle']

            src_head = src['head'] if src['head'] else 'HEADLESS'
            tgt_head = tgt['head'] if tgt['head'] else 'HEADLESS'

            head_total_src[src_head] += 1
            head_total_tgt[tgt_head] += 1

            if (src_mid, tgt_mid) in FORBIDDEN_SET:
                head_hazard_src[src_head] += 1
                head_hazard_tgt[tgt_head] += 1

    results = {}
    for h in list(HEADS) + ['HEADLESS']:
        src_cnt = head_hazard_src.get(h, 0)
        src_total = head_total_src.get(h, 0)
        tgt_cnt = head_hazard_tgt.get(h, 0)
        tgt_total = head_total_tgt.get(h, 0)

        results[h] = {
            'hazard_source_count': src_cnt,
            'hazard_source_rate': round(src_cnt / src_total, 6) if src_total > 0 else 0,
            'hazard_target_count': tgt_cnt,
            'hazard_target_rate': round(tgt_cnt / tgt_total, 6) if tgt_total > 0 else 0,
            'total_as_source': src_total,
            'total_as_target': tgt_total,
        }

    # Are o-HEAD tokens targets of specific hazard classes?
    # Check which forbidden pairs have o-HEAD as target
    o_as_target_pairs = []
    for src, tgt in FORBIDDEN_PAIRS:
        tgt_head, _, _, _ = decompose_middle_hmt(tgt)
        if tgt_head == 'o':
            o_as_target_pairs.append((src, tgt))

    # And source
    o_as_source_pairs = []
    for src, tgt in FORBIDDEN_PAIRS:
        src_head, _, _, _ = decompose_middle_hmt(src)
        if src_head == 'o':
            o_as_source_pairs.append((src, tgt))

    results['o_forbidden_as_target'] = o_as_target_pairs
    results['o_forbidden_as_source'] = o_as_source_pairs

    return results


# ============================================================
# T8: o vs e HEAD Comparison
# ============================================================

def test_o_vs_e(all_tokens):
    """Detailed comparison of o-HEAD vs e-HEAD."""
    o_tokens = [t for t in all_tokens if t['head'] == 'o']
    e_tokens = [t for t in all_tokens if t['head'] == 'e']

    dims = {}

    # Category distributions
    o_cats = Counter(t['category'] for t in o_tokens if t['category'])
    e_cats = Counter(t['category'] for t in e_tokens if t['category'])
    o_cat_dist = normalize(o_cats, ALL_CATEGORIES)
    e_cat_dist = normalize(e_cats, ALL_CATEGORIES)
    cat_jsd = jsd(o_cat_dist, e_cat_dist, ALL_CATEGORIES)

    dims['category'] = {
        'o_dist': {k: round(v, 4) for k, v in o_cat_dist.items()},
        'e_dist': {k: round(v, 4) for k, v in e_cat_dist.items()},
        'jsd': round(cat_jsd, 4),
        'o_dominant': max(o_cat_dist, key=o_cat_dist.get),
        'e_dominant': max(e_cat_dist, key=e_cat_dist.get),
    }

    # Terminal distributions
    term_cats = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
    o_terms = Counter(t['term'] for t in o_tokens)
    e_terms = Counter(t['term'] for t in e_tokens)
    o_term_dist = normalize(o_terms, term_cats)
    e_term_dist = normalize(e_terms, term_cats)
    term_jsd = jsd(o_term_dist, e_term_dist, term_cats)

    dims['terminal'] = {
        'o_dist': {k: round(v, 4) for k, v in o_term_dist.items()},
        'e_dist': {k: round(v, 4) for k, v in e_term_dist.items()},
        'jsd': round(term_jsd, 4),
    }

    # Modifier usage
    mod_chars = list('pcifds')
    o_mod_rates = {}
    e_mod_rates = {}
    for mod in mod_chars:
        o_cnt = sum(1 for t in o_tokens if mod in t['mods'])
        e_cnt = sum(1 for t in e_tokens if mod in t['mods'])
        o_mod_rates[mod] = round(o_cnt / len(o_tokens), 4) if o_tokens else 0
        e_mod_rates[mod] = round(e_cnt / len(e_tokens), 4) if e_tokens else 0

    dims['modifiers'] = {
        'o_rates': o_mod_rates,
        'e_rates': e_mod_rates,
        'strongest_o_bias': max(mod_chars, key=lambda m: o_mod_rates[m] - e_mod_rates[m]),
        'strongest_e_bias': max(mod_chars, key=lambda m: e_mod_rates[m] - o_mod_rates[m]),
    }

    # Suffix rate
    o_suf_rate = sum(1 for t in o_tokens if t['has_suffix']) / len(o_tokens) if o_tokens else 0
    e_suf_rate = sum(1 for t in e_tokens if t['has_suffix']) / len(e_tokens) if e_tokens else 0

    dims['suffix'] = {
        'o_rate': round(o_suf_rate, 4),
        'e_rate': round(e_suf_rate, 4),
    }

    # Line position
    o_pos = [t['line_pos_frac'] for t in o_tokens if 'line_pos_frac' in t]
    e_pos = [t['line_pos_frac'] for t in e_tokens if 'line_pos_frac' in t]
    dims['line_position'] = {
        'o_mean': round(sum(o_pos) / len(o_pos), 4) if o_pos else None,
        'e_mean': round(sum(e_pos) / len(e_pos), 4) if e_pos else None,
    }

    # Prefix associations
    o_pfx = Counter(t['prefix'] for t in o_tokens)
    e_pfx = Counter(t['prefix'] for t in e_tokens)
    dims['prefix_top5'] = {
        'o': [(p, c) for p, c in o_pfx.most_common(5)],
        'e': [(p, c) for p, c in e_pfx.most_common(5)],
    }

    return dims


# ============================================================
# T9: Line Position Profile
# ============================================================

def test_line_position(all_tokens):
    """Detailed line position analysis for o-HEAD."""
    o_tokens = [t for t in all_tokens if t['head'] == 'o']

    # Quintile distribution
    q_dist = Counter(t['line_quintile'] for t in o_tokens if 'line_quintile' in t)
    total = sum(q_dist.values())

    # Baseline quintile distribution
    all_q = Counter(t['line_quintile'] for t in all_tokens if 'line_quintile' in t)
    all_total = sum(all_q.values())

    quintile_enrichment = {}
    for q in range(5):
        o_rate = q_dist.get(q, 0) / total if total > 0 else 0
        base_rate = all_q.get(q, 0) / all_total if all_total > 0 else 0
        quintile_enrichment[str(q)] = {
            'o_rate': round(o_rate, 4),
            'baseline': round(base_rate, 4),
            'enrichment': round(o_rate / base_rate, 3) if base_rate > 0 else None,
        }

    # Per-quintile category distribution
    q_cats = defaultdict(Counter)
    for t in o_tokens:
        if 'line_quintile' in t and t['category']:
            q_cats[t['line_quintile']][t['category']] += 1

    q_cat_dists = {}
    for q in range(5):
        q_cat_dists[str(q)] = normalize(q_cats[q], ALL_CATEGORIES)

    # Initial/final rates
    initial_rate = sum(1 for t in o_tokens if t.get('is_line_initial')) / len(o_tokens) if o_tokens else 0
    final_rate = sum(1 for t in o_tokens if t.get('is_line_final')) / len(o_tokens) if o_tokens else 0

    # o-HEAD tokens at line-initial: which MIDDLEs?
    initial_o = [t for t in o_tokens if t.get('is_line_initial')]
    initial_mids = Counter(t['middle'] for t in initial_o)

    # o-HEAD tokens at line-final: which MIDDLEs?
    final_o = [t for t in o_tokens if t.get('is_line_final')]
    final_mids = Counter(t['middle'] for t in final_o)

    # Category by position
    initial_cats = Counter(t['category'] for t in initial_o if t['category'])
    final_cats = Counter(t['category'] for t in final_o if t['category'])
    medial_o = [t for t in o_tokens if not t.get('is_line_initial') and not t.get('is_line_final')]
    medial_cats = Counter(t['category'] for t in medial_o if t['category'])

    return {
        'n': len(o_tokens),
        'mean_position': round(sum(t['line_pos_frac'] for t in o_tokens if 'line_pos_frac' in t) / len(o_tokens), 4) if o_tokens else None,
        'initial_rate': round(initial_rate, 4),
        'final_rate': round(final_rate, 4),
        'quintile_enrichment': quintile_enrichment,
        'quintile_category_dist': {k: {c: round(v, 4) for c, v in d.items()} for k, d in q_cat_dists.items()},
        'initial_top_middles': [(m, c) for m, c in initial_mids.most_common(8)],
        'final_top_middles': [(m, c) for m, c in final_mids.most_common(8)],
        'initial_category_dist': normalize(initial_cats, ALL_CATEGORIES),
        'final_category_dist': normalize(final_cats, ALL_CATEGORIES),
        'medial_category_dist': normalize(medial_cats, ALL_CATEGORIES),
    }


# ============================================================
# T10: Cross-Token Transitions
# ============================================================

def test_transitions(all_tokens, tokens_by_folio_line):
    """What HEAD follows/precedes o-HEAD tokens?"""
    # Build successor/predecessor HEAD pairs
    succ_head = defaultdict(Counter)  # current_head -> next_head -> count
    pred_head = defaultdict(Counter)  # current_head -> prev_head -> count
    succ_total = Counter()
    pred_total = Counter()

    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens)):
            curr = line_tokens[i]
            curr_head = curr['head'] if curr['head'] else 'HEADLESS'

            if i < len(line_tokens) - 1:
                next_tok = line_tokens[i + 1]
                next_head = next_tok['head'] if next_tok['head'] else 'HEADLESS'
                succ_head[curr_head][next_head] += 1
                succ_total[curr_head] += 1

            if i > 0:
                prev_tok = line_tokens[i - 1]
                prev_head = prev_tok['head'] if prev_tok['head'] else 'HEADLESS'
                pred_head[curr_head][prev_head] += 1
                pred_total[curr_head] += 1

    # Focus on o-HEAD
    all_heads = ['a', 'e', 'o', 'k', 't', 'HEADLESS']

    o_successor_dist = {}
    o_successor_enrichment = {}
    for h in all_heads:
        o_cnt = succ_head['o'].get(h, 0)
        o_tot = succ_total['o']
        all_cnt = sum(succ_head[src].get(h, 0) for src in all_heads)
        all_tot = sum(succ_total[src] for src in all_heads)
        o_successor_dist[h] = round(o_cnt / o_tot, 4) if o_tot > 0 else 0
        o_successor_enrichment[h] = enrichment(o_cnt, o_tot, all_cnt, all_tot)

    o_predecessor_dist = {}
    o_predecessor_enrichment = {}
    for h in all_heads:
        o_cnt = pred_head['o'].get(h, 0)
        o_tot = pred_total['o']
        all_cnt = sum(pred_head[src].get(h, 0) for src in all_heads)
        all_tot = sum(pred_total[src] for src in all_heads)
        o_predecessor_dist[h] = round(o_cnt / o_tot, 4) if o_tot > 0 else 0
        o_predecessor_enrichment[h] = enrichment(o_cnt, o_tot, all_cnt, all_tot)

    # Also: full transition matrix at HEAD level
    transition_matrix = {}
    for src_h in all_heads:
        for tgt_h in all_heads:
            cnt = succ_head[src_h].get(tgt_h, 0)
            rate = cnt / succ_total[src_h] if succ_total[src_h] > 0 else 0
            transition_matrix[f'{src_h}->{tgt_h}'] = round(rate, 4)

    # o self-transition rate
    o_self = succ_head['o'].get('o', 0)
    o_self_rate = o_self / succ_total['o'] if succ_total['o'] > 0 else 0

    # Specific o-HEAD successor MIDDLE detail
    o_succ_middle = Counter()
    o_pred_middle = Counter()
    for key in sorted(tokens_by_folio_line.keys()):
        line_tokens = tokens_by_folio_line[key]
        for i in range(len(line_tokens)):
            curr = line_tokens[i]
            if curr['head'] != 'o':
                continue
            if i < len(line_tokens) - 1:
                o_succ_middle[line_tokens[i + 1]['middle']] += 1
            if i > 0:
                o_pred_middle[line_tokens[i - 1]['middle']] += 1

    return {
        'o_successor_dist': o_successor_dist,
        'o_successor_enrichment': o_successor_enrichment,
        'o_predecessor_dist': o_predecessor_dist,
        'o_predecessor_enrichment': o_predecessor_enrichment,
        'o_self_transition_rate': round(o_self_rate, 4),
        'o_successor_top_middles': [(m, c) for m, c in o_succ_middle.most_common(10)],
        'o_predecessor_top_middles': [(m, c) for m, c in o_pred_middle.most_common(10)],
        'full_head_transition_matrix': transition_matrix,
    }


# ============================================================
# T11: o-HEAD Category x Terminal Cross-tabulation
# ============================================================

def test_category_terminal_cross(all_tokens):
    """Cross-tabulate category x terminal for o-HEAD specifically."""
    o_tokens = [t for t in all_tokens if t['head'] == 'o' and t['category']]

    ct = defaultdict(Counter)
    for t in o_tokens:
        ct[t['category']][t['term']] += 1

    term_cats = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
    cross = {}
    for cat in ALL_CATEGORIES:
        total = sum(ct[cat].values())
        if total > 0:
            cross[cat] = {
                'n': total,
                'dist': {tc: round(ct[cat].get(tc, 0) / total, 4) for tc in term_cats},
            }

    return cross


# ============================================================
# T12: o-HEAD compound morphology analysis
# ============================================================

def test_compound_morphology(all_tokens):
    """Analyze the internal structure patterns of o-HEAD compounds."""
    o_tokens = [t for t in all_tokens if t['head'] == 'o']

    # Length distribution
    lengths = Counter(len(t['middle']) for t in o_tokens)

    # Atom composition (which chars appear in o-HEAD MIDDLEs)
    atom_freq = Counter()
    for t in o_tokens:
        for ch in t['middle'][1:]:  # skip the 'o' itself
            atom_freq[ch] += 1

    total_inner_chars = sum(atom_freq.values())

    # Compare with all-HEAD inner char distribution
    all_tokens_headed = [t for t in all_tokens if t['head'] in HEADS]
    all_atom_freq = Counter()
    for t in all_tokens_headed:
        for ch in t['middle'][1:]:
            all_atom_freq[ch] += 1
    all_total_inner = sum(all_atom_freq.values())

    atom_enrichment = {}
    for ch in sorted(set(list(atom_freq.keys()) + list(all_atom_freq.keys()))):
        o_rate = atom_freq.get(ch, 0) / total_inner_chars if total_inner_chars > 0 else 0
        all_rate = all_atom_freq.get(ch, 0) / all_total_inner if all_total_inner > 0 else 0
        atom_enrichment[ch] = {
            'o_rate': round(o_rate, 4),
            'all_rate': round(all_rate, 4),
            'enrichment': round(o_rate / all_rate, 3) if all_rate > 0 else None,
        }

    return {
        'length_distribution': dict(sorted(lengths.items())),
        'inner_atom_enrichment': atom_enrichment,
        'total_inner_chars': total_inner_chars,
    }


# ============================================================
# T13: ol/or/o compound family analysis
# ============================================================

def test_ol_or_family(all_tokens):
    """Detailed analysis of the 3 dominant o-HEAD types: o, ol, or."""
    families = {}

    for target_mid in ['o', 'ol', 'or', 'od', 'opch', 'ok', 'ot']:
        mid_tokens = [t for t in all_tokens if t['middle'] == target_mid]
        if not mid_tokens:
            continue

        n = len(mid_tokens)

        # Category
        cats = Counter(t['category'] for t in mid_tokens if t['category'])

        # PREFIX
        pfx = Counter(t['prefix'] for t in mid_tokens)

        # Suffix
        suf_rate = sum(1 for t in mid_tokens if t['has_suffix']) / n

        # Common suffixes
        suffixes = Counter(t['suffix'] for t in mid_tokens if t['has_suffix'])

        # Line position
        positions = [t['line_pos_frac'] for t in mid_tokens if 'line_pos_frac' in t]
        mean_pos = sum(positions) / len(positions) if positions else None
        initial_rate = sum(1 for t in mid_tokens if t.get('is_line_initial')) / n
        final_rate = sum(1 for t in mid_tokens if t.get('is_line_final')) / n

        # Suffix mode
        mode_a_rate = sum(1 for t in mid_tokens if t['suffix_mode'] == 'A') / n

        families[target_mid] = {
            'count': n,
            'category_dist': normalize(cats, ALL_CATEGORIES),
            'dominant_category': max(normalize(cats, ALL_CATEGORIES), key=lambda k: normalize(cats, ALL_CATEGORIES)[k]) if cats else None,
            'top_prefixes': [(p, c) for p, c in pfx.most_common(5)],
            'suffix_rate': round(suf_rate, 4),
            'mode_a_rate': round(mode_a_rate, 4),
            'top_suffixes': [(s, c) for s, c in suffixes.most_common(5)],
            'mean_line_pos': round(mean_pos, 4) if mean_pos else None,
            'initial_rate': round(initial_rate, 4),
            'final_rate': round(final_rate, 4),
        }

    return families


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 548: o-Domain Deep Dive")
    print("=" * 60)

    print("Collecting Currier B data...")
    all_tokens, tokens_by_folio_line = collect_b_data()
    print(f"  Total B tokens: {len(all_tokens)}")
    print(f"  o-HEAD tokens: {sum(1 for t in all_tokens if t['head'] == 'o')}")

    print("Collecting cross-system data...")
    cross_data = collect_cross_system_data()
    for s in ['A', 'B', 'AZC']:
        print(f"  {s}: {len(cross_data[s])} tokens")

    print("\nT1: Terminal Profile...")
    t1 = test_terminal_profile(all_tokens)
    print(f"  o signature: l={t1['o_signature']['l_rate']}, r={t1['o_signature']['r_rate']}, bare={t1['o_signature']['bare_rate']}")

    print("\nT2: Modifier Profile...")
    t2 = test_modifier_profile(all_tokens)
    print(f"  o p-enrichment: {t2['o_signature']['p_enrichment']}, f-enrichment: {t2['o_signature']['f_enrichment']}")

    print("\nT3: Suffix Behavior...")
    t3 = test_suffix_behavior(all_tokens)
    print(f"  o suffix rate: {t3['per_head']['o']['suffix_rate']}, mode A: {t3['per_head']['o']['mode_a_rate']}")

    print("\nT4: Cross-System Distribution...")
    t4 = test_cross_system(cross_data)
    for s in ['A', 'B', 'AZC']:
        print(f"  {s} o-HEAD rate: {t4[s]['o_head_rate']}")

    print("\nT5: AZC Zone Analysis...")
    t5 = test_azc_zones(cross_data)
    for z in ['R', 'C', 'S', 'P', 'L']:
        if z in t5 and isinstance(t5[z], dict):
            print(f"  Zone {z}: o-rate={t5[z]['o_rate']}")

    print("\nT6: Compound Detail (top 25 o-MIDDLEs)...")
    t6 = test_compound_detail(all_tokens)
    for mid in list(t6.keys())[:5]:
        d = t6[mid]
        print(f"  {mid}: n={d['count']} cat={d['category']} pos={d['mean_line_pos']} sfx={d['suffix_rate']}")

    print("\nT7: Hazard Relationship...")
    t7 = test_hazard_relationship(all_tokens, tokens_by_folio_line)
    o_src = t7['o']['hazard_source_rate']
    o_tgt = t7['o']['hazard_target_rate']
    print(f"  o-HEAD source rate: {o_src}")
    print(f"  o-HEAD target rate: {o_tgt}")
    print(f"  o as forbidden target: {t7['o_forbidden_as_target']}")
    print(f"  o as forbidden source: {t7['o_forbidden_as_source']}")

    print("\nT8: o vs e Comparison...")
    t8 = test_o_vs_e(all_tokens)
    print(f"  Category JSD: {t8['category']['jsd']}")
    print(f"  Terminal JSD: {t8['terminal']['jsd']}")
    print(f"  o dominant: {t8['category']['o_dominant']}, e dominant: {t8['category']['e_dominant']}")

    print("\nT9: Line Position Profile...")
    t9 = test_line_position(all_tokens)
    print(f"  o mean pos: {t9['mean_position']}")
    print(f"  o initial: {t9['initial_rate']}, final: {t9['final_rate']}")

    print("\nT10: Cross-Token Transitions...")
    t10 = test_transitions(all_tokens, tokens_by_folio_line)
    print(f"  o self-transition: {t10['o_self_transition_rate']}")
    print(f"  Successor HEAD dist: {t10['o_successor_dist']}")

    print("\nT11: Category x Terminal Cross-tab...")
    t11 = test_category_terminal_cross(all_tokens)
    for cat in ['STAGING', 'OPERATION', 'FLOW', 'MARKING']:
        if cat in t11:
            print(f"  {cat} (n={t11[cat]['n']}): {t11[cat]['dist']}")

    print("\nT12: Compound Morphology...")
    t12 = test_compound_morphology(all_tokens)
    print(f"  Length dist: {t12['length_distribution']}")

    print("\nT13: ol/or/o Family Detail...")
    t13 = test_ol_or_family(all_tokens)
    for mid in ['o', 'ol', 'or', 'od', 'opch']:
        if mid in t13:
            d = t13[mid]
            print(f"  {mid}: n={d['count']} cat={d['dominant_category']} pos={d['mean_line_pos']} sfx={d['suffix_rate']}")

    # Save results
    results = {
        'meta': {
            'phase': 548,
            'name': 'o-Domain Deep Dive',
            'total_b_tokens': len(all_tokens),
            'o_head_tokens': sum(1 for t in all_tokens if t['head'] == 'o'),
            'o_head_types': len(set(t['middle'] for t in all_tokens if t['head'] == 'o')),
        },
        'T1_terminal_profile': t1,
        'T2_modifier_profile': t2,
        'T3_suffix_behavior': t3,
        'T4_cross_system': t4,
        'T5_azc_zones': t5,
        'T6_compound_detail': t6,
        'T7_hazard': t7,
        'T8_o_vs_e': t8,
        'T9_line_position': t9,
        'T10_transitions': t10,
        'T11_category_terminal': t11,
        'T12_compound_morphology': t12,
        'T13_family_detail': t13,
    }

    out_path = PROJECT_ROOT / 'phases' / 'O_DOMAIN_DEEP_DIVE' / 'results' / 'o_domain_deep_dive.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

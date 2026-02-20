"""Phase 405: Section Program Architecture and Rosettes Targeting — 8-test battery.

C1125 says all 9 rosettes correlate most strongly with Section T. But Section T
has only 2 B folios: f66r (329 tokens) and f85r1 (a Rosettes foldout folio,
excluded from the analysis). So the "Section T correlation" is effectively
correlation with a single folio (f66r).

This phase decomposes the C1125 finding:
- Part A (T1-T4): Is the Rosettes targeting a section effect, a folio effect, or
  a vocabulary-size artifact?
- Part B (T5-T8): Section-level vocabulary architecture comparison.
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import defaultdict, Counter

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer,
                              load_middle_classes)

# ============================================================
# CONSTANTS
# ============================================================

KERNEL_CHARS = set('khe')
ROSETTES_FOLIOS = {'f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# ============================================================
# UTILITY
# ============================================================

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    return obj


def jaccard(a, b):
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def cosine_sim(vec_a, vec_b):
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in keys)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def shannon_entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def jensen_shannon(p_counts, q_counts):
    all_keys = set(p_counts) | set(q_counts)
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return 1.0
    jsd = 0.0
    for k in all_keys:
        pk = p_counts.get(k, 0) / p_total
        qk = q_counts.get(k, 0) / q_total
        mk = (pk + qk) / 2
        if pk > 0:
            jsd += pk * math.log2(pk / mk) / 2
        if qk > 0:
            jsd += qk * math.log2(qk / mk) / 2
    return jsd


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load per-folio and per-section data for all B folios."""
    print("Loading data...")
    morph = Morphology()
    tx = Transcript()
    ra = RosettesAnalyzer()

    # --- Per-folio data ---
    folio_middles = defaultdict(set)
    folio_tokens = defaultdict(list)
    folio_section = {}
    folio_token_count = defaultdict(int)

    for tok in tx.currier_b():
        if tok.folio in ROSETTES_FOLIOS:
            continue
        m = morph.extract(tok.word)
        folio_token_count[tok.folio] += 1
        folio_section[tok.folio] = tok.section
        folio_tokens[tok.folio].append({
            'word': tok.word,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        })
        if m.middle:
            folio_middles[tok.folio].add(m.middle)

    # --- Per-section aggregation ---
    section_folios = defaultdict(list)
    section_middles = defaultdict(set)
    section_tokens = defaultdict(list)
    for folio, section in folio_section.items():
        section_folios[section].append(folio)
        section_middles[section] |= folio_middles[folio]
        section_tokens[section].extend(folio_tokens[folio])

    print(f"  B folios (excl. Rosettes): {len(folio_section)}")
    for s in sorted(section_folios):
        print(f"    Section {s}: {len(section_folios[s])} folios, "
              f"{len(section_middles[s])} unique MIDDLEs, "
              f"{len(section_tokens[s])} tokens")

    # --- Rosettes MIDDLEs ---
    rosettes_middles = ra.all_middles()
    print(f"  Rosettes MIDDLEs: {len(rosettes_middles)}")

    # --- Bridge set ---
    bridge_path = PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bd = json.load(f)
    bridge_set = set(bd['t5_structural_profile']['bridge_middles'])

    # --- 49-class mapping ---
    ctm_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}
    token_to_role = ctm_data.get('token_to_role', {})

    # --- REGIME mapping ---
    regime_path = PROJECT / 'data' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    regime_assignments = regime_data.get('regime_assignments', {})
    folio_regime = {}
    for f, info in regime_assignments.items():
        if isinstance(info, dict):
            folio_regime[f] = info.get('regime', 'UNKNOWN')
        else:
            folio_regime[f] = str(info)

    # --- RI/PP sets ---
    ri_set, pp_set = load_middle_classes()

    print("  Data loaded.")

    return {
        'folio_middles': dict(folio_middles),
        'folio_tokens': dict(folio_tokens),
        'folio_section': folio_section,
        'folio_token_count': dict(folio_token_count),
        'section_folios': dict(section_folios),
        'section_middles': dict(section_middles),
        'section_tokens': dict(section_tokens),
        'rosettes_middles': rosettes_middles,
        'bridge_set': bridge_set,
        'token_to_class': token_to_class,
        'token_to_role': token_to_role,
        'folio_regime': folio_regime,
        'ri_set': ri_set,
        'pp_set': pp_set,
    }


# ============================================================
# PART A: ROSETTES TARGETING DECOMPOSITION
# ============================================================

def t1_per_folio_rosettes_overlap(data):
    """T1: Compute Jaccard(rosettes, folio) for every B folio."""
    print("\n=== T1: Per-Folio Rosettes Overlap ===")

    ros_mids = data['rosettes_middles']
    folio_jaccards = {}
    for folio, mids in sorted(data['folio_middles'].items()):
        folio_jaccards[folio] = jaccard(ros_mids, mids)

    # Rank by Jaccard (descending)
    ranked = sorted(folio_jaccards.items(), key=lambda x: -x[1])
    f66r_rank = next(i + 1 for i, (f, _) in enumerate(ranked) if f == 'f66r')
    f66r_jaccard = folio_jaccards.get('f66r', 0)

    print(f"  Total folios: {len(ranked)}")
    print(f"  f66r rank: #{f66r_rank} (Jaccard = {f66r_jaccard:.4f})")
    print(f"  Top 10 folios:")
    for i, (f, j) in enumerate(ranked[:10]):
        section = data['folio_section'].get(f, '?')
        regime = data['folio_regime'].get(f, '?')
        n_mids = len(data['folio_middles'].get(f, set()))
        marker = " <-- f66r" if f == 'f66r' else ""
        print(f"    #{i+1}: {f} (section={section}, regime={regime}, "
              f"mids={n_mids}) Jaccard={j:.4f}{marker}")

    # Section distribution of top 10
    top10_sections = Counter(data['folio_section'].get(f, '?') for f, _ in ranked[:10])
    print(f"  Top-10 section distribution: {dict(top10_sections)}")

    # Percentile of f66r
    f66r_pct = (1 - f66r_rank / len(ranked)) * 100

    return {
        'total_folios': len(ranked),
        'f66r_rank': f66r_rank,
        'f66r_jaccard': f66r_jaccard,
        'f66r_percentile': f66r_pct,
        'top10': [(f, j, data['folio_section'].get(f, '?')) for f, j in ranked[:10]],
        'top10_sections': dict(top10_sections),
        'all_jaccards': {f: j for f, j in ranked},
    }


def t2_per_folio_bridge_density(data):
    """T2: Bridge MIDDLE fraction for every B folio."""
    print("\n=== T2: Per-Folio Bridge Density ===")

    bridge = data['bridge_set']
    folio_bridge = {}
    for folio, mids in sorted(data['folio_middles'].items()):
        if not mids:
            continue
        bridge_count = len(mids & bridge)
        folio_bridge[folio] = bridge_count / len(mids)

    ranked = sorted(folio_bridge.items(), key=lambda x: -x[1])
    f66r_rank = next((i + 1 for i, (f, _) in enumerate(ranked) if f == 'f66r'), None)
    f66r_bridge = folio_bridge.get('f66r', 0)

    print(f"  f66r bridge density: {f66r_bridge:.4f} (rank #{f66r_rank}/{len(ranked)})")
    print(f"  Top 10 bridge-dense folios:")
    for i, (f, bd) in enumerate(ranked[:10]):
        section = data['folio_section'].get(f, '?')
        n_mids = len(data['folio_middles'].get(f, set()))
        marker = " <-- f66r" if f == 'f66r' else ""
        print(f"    #{i+1}: {f} (section={section}, mids={n_mids}) bridge={bd:.4f}{marker}")

    # Per-section bridge density distribution
    section_bridge = defaultdict(list)
    for folio, bd in folio_bridge.items():
        section_bridge[data['folio_section'].get(folio, '?')].append(bd)

    print(f"\n  Per-section bridge density (mean):")
    for s in sorted(section_bridge):
        vals = section_bridge[s]
        mean_bd = sum(vals) / len(vals) if vals else 0
        print(f"    Section {s}: mean={mean_bd:.4f} ({len(vals)} folios)")

    # Correlation: bridge density vs rosettes overlap
    t1_jaccards = {f: jaccard(data['rosettes_middles'], data['folio_middles'][f])
                   for f in folio_bridge}
    folio_list = sorted(folio_bridge.keys())
    x = [folio_bridge[f] for f in folio_list]
    y = [t1_jaccards[f] for f in folio_list]

    # Spearman rank correlation
    def _rank(vals):
        indexed = sorted(enumerate(vals), key=lambda iv: iv[1])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed) - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rx = _rank(x)
    ry = _rank(y)
    n = len(folio_list)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    std_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    rho = cov / (std_x * std_y) if std_x > 0 and std_y > 0 else 0

    print(f"\n  Spearman rho(bridge_density, rosettes_overlap): {rho:.4f}")

    return {
        'f66r_bridge_density': f66r_bridge,
        'f66r_rank': f66r_rank,
        'total_folios': len(ranked),
        'f66r_percentile': (1 - f66r_rank / len(ranked)) * 100 if f66r_rank else 0,
        'top10': [(f, bd, data['folio_section'].get(f, '?')) for f, bd in ranked[:10]],
        'section_mean_bridge': {s: sum(v) / len(v) for s, v in section_bridge.items()},
        'spearman_rho_bridge_vs_overlap': rho,
        'all_bridge_densities': {f: bd for f, bd in ranked},
    }


def t3_overlap_decomposition(data):
    """T3: Which MIDDLEs drive the f66r-Rosettes overlap?"""
    print("\n=== T3: Overlap Decomposition (f66r) ===")

    ros_mids = data['rosettes_middles']
    f66r_mids = data['folio_middles'].get('f66r', set())
    bridge = data['bridge_set']

    shared = ros_mids & f66r_mids
    shared_bridge = shared & bridge
    shared_non_bridge = shared - bridge

    print(f"  f66r MIDDLEs: {len(f66r_mids)}")
    print(f"  Rosettes MIDDLEs: {len(ros_mids)}")
    print(f"  Shared: {len(shared)}")
    print(f"  Shared bridge: {len(shared_bridge)} ({len(shared_bridge)/len(shared)*100:.1f}%)" if shared else "")
    print(f"  Shared non-bridge: {len(shared_non_bridge)}")

    # f66r-only and rosettes-only
    f66r_only = f66r_mids - ros_mids
    ros_only = ros_mids - f66r_mids

    print(f"  f66r-only: {len(f66r_only)} (bridge: {len(f66r_only & bridge)})")
    print(f"  Rosettes-only: {len(ros_only)} (bridge: {len(ros_only & bridge)})")

    # f66r bridge density
    f66r_bridge = f66r_mids & bridge
    f66r_bridge_frac = len(f66r_bridge) / len(f66r_mids) if f66r_mids else 0
    print(f"  f66r total bridge density: {f66r_bridge_frac:.4f} ({len(f66r_bridge)}/{len(f66r_mids)})")

    # Is f66r bridge-enriched compared to B corpus?
    # (Reference: typical B folio bridge density from T2)

    return {
        'f66r_middles': len(f66r_mids),
        'rosettes_middles': len(ros_mids),
        'shared_count': len(shared),
        'shared_bridge_count': len(shared_bridge),
        'shared_bridge_fraction': len(shared_bridge) / len(shared) if shared else 0,
        'shared_non_bridge_count': len(shared_non_bridge),
        'f66r_bridge_density': f66r_bridge_frac,
        'f66r_only_count': len(f66r_only),
        'rosettes_only_count': len(ros_only),
        'shared_middles': sorted(shared),
        'shared_bridge_middles': sorted(shared_bridge),
    }


def t4_size_controlled_comparison(data):
    """T4: Bootstrap size-controlled section comparison."""
    print("\n=== T4: Size-Controlled Section Comparison ===")

    ros_mids = data['rosettes_middles']
    target_size = len(data['folio_middles'].get('f66r', set()))
    f66r_jaccard = jaccard(ros_mids, data['folio_middles'].get('f66r', set()))

    print(f"  Target vocabulary size: {target_size} (f66r)")
    print(f"  f66r actual Jaccard: {f66r_jaccard:.4f}")

    random.seed(42)
    section_bootstrap = {}

    for section, mids in sorted(data['section_middles'].items()):
        mid_list = sorted(mids)
        if len(mid_list) < target_size:
            # Section too small to sample — use actual size
            actual_j = jaccard(ros_mids, mids)
            section_bootstrap[section] = {
                'mean': actual_j,
                'p5': actual_j,
                'p95': actual_j,
                'n_samples': 0,
                'note': f'Section has only {len(mid_list)} MIDDLEs (< {target_size})',
            }
            print(f"  Section {section}: too small ({len(mid_list)} mids), "
                  f"actual Jaccard = {actual_j:.4f}")
            continue

        bootstrap_jaccards = []
        for _ in range(5000):
            sample = set(random.sample(mid_list, target_size))
            bootstrap_jaccards.append(jaccard(ros_mids, sample))
        bootstrap_jaccards.sort()

        mean_j = sum(bootstrap_jaccards) / len(bootstrap_jaccards)
        p5 = bootstrap_jaccards[int(0.05 * len(bootstrap_jaccards))]
        p50 = bootstrap_jaccards[int(0.50 * len(bootstrap_jaccards))]
        p95 = bootstrap_jaccards[int(0.95 * len(bootstrap_jaccards))]

        # What percentile is f66r's actual Jaccard in this bootstrap?
        f66r_pct = sum(1 for j in bootstrap_jaccards if j <= f66r_jaccard) / len(bootstrap_jaccards) * 100

        section_bootstrap[section] = {
            'mean': mean_j,
            'p5': p5,
            'p50': p50,
            'p95': p95,
            'f66r_percentile': f66r_pct,
            'n_samples': 5000,
        }
        print(f"  Section {section}: bootstrap mean={mean_j:.4f}, "
              f"p50={p50:.4f}, p95={p95:.4f} | "
              f"f66r ({f66r_jaccard:.4f}) at {f66r_pct:.1f}th percentile")

    # Determine if size artifact
    # If f66r_jaccard < p95 of most sections -> SIZE_ARTIFACT
    sections_exceeding = 0
    for s, bs in section_bootstrap.items():
        if s == 'T':
            continue
        if bs.get('f66r_percentile', 100) < 95:
            sections_exceeding += 1

    is_size_artifact = sections_exceeding >= len(section_bootstrap) - 1  # all non-T sections
    print(f"\n  Sections where f66r < bootstrap p95: {sections_exceeding}/{len(section_bootstrap) - 1}")
    print(f"  SIZE_ARTIFACT: {is_size_artifact}")

    return {
        'target_size': target_size,
        'f66r_jaccard': f66r_jaccard,
        'section_bootstrap': section_bootstrap,
        'is_size_artifact': is_size_artifact,
        'sections_exceeding_f66r': sections_exceeding,
    }


# ============================================================
# PART B: SECTION VOCABULARY ARCHITECTURE
# ============================================================

def t5_section_bridge_density(data):
    """T5: Bridge MIDDLE fraction per section."""
    print("\n=== T5: Per-Section Bridge Density ===")

    bridge = data['bridge_set']
    results = {}

    for section in sorted(data['section_middles']):
        mids = data['section_middles'][section]
        bridge_mids = mids & bridge
        frac = len(bridge_mids) / len(mids) if mids else 0
        n_folios = len(data['section_folios'][section])
        results[section] = {
            'bridge_count': len(bridge_mids),
            'total_middles': len(mids),
            'bridge_fraction': frac,
            'n_folios': n_folios,
        }
        print(f"  Section {section}: {len(bridge_mids)}/{len(mids)} = {frac:.4f} "
              f"({n_folios} folios)")

    # Gradient: rank by bridge density
    ranked = sorted(results.items(), key=lambda x: -x[1]['bridge_fraction'])
    gradient = [s for s, _ in ranked]
    print(f"  Bridge density ranking: {' > '.join(gradient)}")

    return {
        'per_section': results,
        'gradient': gradient,
    }


def t6_section_class_distribution(data):
    """T6: Instruction class distribution per section."""
    print("\n=== T6: Per-Section Instruction Class Distribution ===")

    section_class_counts = {}
    for section in sorted(data['section_tokens']):
        cc = Counter()
        for tok in data['section_tokens'][section]:
            cls = data['token_to_class'].get(tok['word'])
            if cls is not None:
                cc[cls] += 1
        section_class_counts[section] = cc

    # JS divergence matrix
    sections = sorted(section_class_counts.keys())
    js_matrix = {}
    for i, s1 in enumerate(sections):
        for j, s2 in enumerate(sections):
            if i < j:
                js = jensen_shannon(section_class_counts[s1], section_class_counts[s2])
                js_matrix[f"{s1}-{s2}"] = js

    print(f"  JS divergence matrix:")
    for pair, js in sorted(js_matrix.items(), key=lambda x: x[1]):
        print(f"    {pair}: {js:.4f}")

    # Coverage per section
    for section, cc in sorted(section_class_counts.items()):
        total_tokens = len(data['section_tokens'][section])
        mapped = sum(cc.values())
        n_classes = len(cc)
        print(f"  Section {section}: {mapped}/{total_tokens} mapped ({mapped/total_tokens:.1%}), "
              f"{n_classes} classes")

    # Class entropy per section
    class_entropies = {}
    for section, cc in section_class_counts.items():
        class_entropies[section] = shannon_entropy(cc)

    return {
        'section_class_counts': {s: dict(cc) for s, cc in section_class_counts.items()},
        'js_divergence_matrix': js_matrix,
        'class_entropies': class_entropies,
    }


def t7_section_role_profiles(data):
    """T7: 5-role distribution per section."""
    print("\n=== T7: Per-Section Role Profiles ===")

    all_roles = ['AUXILIARY', 'FLOW_OPERATOR', 'ENERGY_OPERATOR',
                 'FREQUENT_OPERATOR', 'CORE_CONTROL']

    section_role_counts = {}
    for section in sorted(data['section_tokens']):
        rc = Counter()
        for tok in data['section_tokens'][section]:
            role = data['token_to_role'].get(tok['word'])
            if role:
                rc[role] += 1
        section_role_counts[section] = rc

    print(f"  {'Section':8s} | {'AUXILIARY':10s} | {'FLOW_OP':10s} | {'ENERGY_OP':10s} | "
          f"{'FREQ_OP':10s} | {'CORE_CTL':10s}")
    print(f"  {'-'*8} | {'-'*10} | {'-'*10} | {'-'*10} | {'-'*10} | {'-'*10}")
    for section in sorted(section_role_counts):
        rc = section_role_counts[section]
        total = sum(rc.values())
        if total == 0:
            continue
        fracs = [rc.get(r, 0) / total for r in all_roles]
        print(f"  {section:8s} | {fracs[0]:9.1%} | {fracs[1]:9.1%} | {fracs[2]:9.1%} | "
              f"{fracs[3]:9.1%} | {fracs[4]:9.1%}")

    # Role-level section ordering
    role_rankings = {}
    for role in all_roles:
        by_role = []
        for section, rc in section_role_counts.items():
            total = sum(rc.values())
            if total > 0:
                by_role.append((section, rc.get(role, 0) / total))
        by_role.sort(key=lambda x: -x[1])
        role_rankings[role] = [s for s, _ in by_role]
        print(f"  {role}: {' > '.join(role_rankings[role])}")

    return {
        'section_role_counts': {s: dict(rc) for s, rc in section_role_counts.items()},
        'role_rankings': role_rankings,
    }


def t8_section_kernel_balance(data):
    """T8: k/h/e fractions per section."""
    print("\n=== T8: Per-Section Kernel Balance ===")

    section_kernel = {}
    for section in sorted(data['section_tokens']):
        k_count = 0
        h_count = 0
        e_count = 0
        total_with_middle = 0

        for tok in data['section_tokens'][section]:
            mid = tok.get('middle')
            if not mid:
                continue
            total_with_middle += 1
            if 'k' in mid:
                k_count += 1
            if 'h' in mid:
                h_count += 1
            if 'e' in mid:
                e_count += 1

        if total_with_middle > 0:
            section_kernel[section] = {
                'k_fraction': k_count / total_with_middle,
                'h_fraction': h_count / total_with_middle,
                'e_fraction': e_count / total_with_middle,
                'any_kernel': sum(1 for t in data['section_tokens'][section]
                                  if t.get('middle') and
                                  any(c in KERNEL_CHARS for c in t['middle'])) / total_with_middle,
                'total_with_middle': total_with_middle,
            }

    print(f"  {'Section':8s} | {'k':8s} | {'h':8s} | {'e':8s} | {'any kernel':12s}")
    print(f"  {'-'*8} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*12}")
    for section in sorted(section_kernel):
        sk = section_kernel[section]
        print(f"  {section:8s} | {sk['k_fraction']:7.1%} | {sk['h_fraction']:7.1%} | "
              f"{sk['e_fraction']:7.1%} | {sk['any_kernel']:11.1%}")

    return {
        'per_section': section_kernel,
    }


# ============================================================
# VERDICT
# ============================================================

def verdict(results):
    """Synthesize all test results into a verdict."""
    print("\n" + "=" * 70)
    print("VERDICT ASSIGNMENT")
    print("=" * 70)

    t1 = results['T1']
    t2 = results['T2']
    t3 = results['T3']
    t4 = results['T4']
    t5 = results['T5']

    # Key metrics
    f66r_overlap_rank = t1['f66r_rank']
    f66r_bridge_rank = t2['f66r_rank']
    f66r_bridge_density = t2['f66r_bridge_density']
    rho_bridge_overlap = t2['spearman_rho_bridge_vs_overlap']
    shared_bridge_frac = t3['shared_bridge_fraction']
    is_size_artifact = t4['is_size_artifact']

    print(f"\n  f66r Rosettes overlap rank: #{f66r_overlap_rank}/{t1['total_folios']}")
    print(f"  f66r bridge density rank: #{f66r_bridge_rank}/{t2['total_folios']}")
    print(f"  f66r bridge density: {f66r_bridge_density:.4f}")
    print(f"  Spearman rho(bridge, overlap): {rho_bridge_overlap:.4f}")
    print(f"  Shared MIDDLE bridge fraction: {shared_bridge_frac:.1%}")
    print(f"  Size artifact (T4): {is_size_artifact}")

    # Decision tree
    if is_size_artifact:
        v = 'SIZE_ARTIFACT'
        reason = ("The C1125 Section T correlation is a vocabulary-size artifact. "
                  f"When vocabulary size is controlled to {t4['target_size']} MIDDLEs, "
                  "other sections achieve similar or higher Jaccard with Rosettes. "
                  "Rosettes target bridge vocabulary generically; T 'wins' because its "
                  "small vocabulary inflates Jaccard's denominator.")
    elif f66r_bridge_density > 0 and t2['f66r_percentile'] > 90:
        v = 'BRIDGE_HUB_FOLIO'
        reason = (f"f66r is individually a bridge-dense folio "
                  f"(bridge density {f66r_bridge_density:.1%}, "
                  f"rank #{f66r_bridge_rank}, {t2['f66r_percentile']:.0f}th percentile). "
                  f"The Rosettes correlation is folio-level, not section-level. "
                  f"Bridge density correlates with Rosettes overlap (rho={rho_bridge_overlap:.3f}).")
    elif rho_bridge_overlap > 0.5:
        v = 'BRIDGE_MEDIATED'
        reason = (f"Bridge MIDDLE density strongly predicts Rosettes overlap "
                  f"(Spearman rho={rho_bridge_overlap:.3f}). "
                  f"The targeting is mediated by bridge vocabulary concentration, "
                  f"not section identity per se.")
    else:
        v = 'VOCABULARY_AFFINITY'
        reason = (f"f66r shares vocabulary with Rosettes beyond what bridge density alone predicts. "
                  f"The overlap includes {t3['shared_non_bridge_count']} non-bridge MIDDLEs "
                  f"({1 - shared_bridge_frac:.1%} of shared vocabulary).")

    print(f"\n  TARGETING VERDICT: {v}")
    print(f"  REASON: {reason}")

    # Section architecture summary
    t5_data = t5['per_section']
    bridge_gradient = t5['gradient']
    print(f"\n  Section bridge density gradient: {' > '.join(bridge_gradient)}")

    # Section diversity (from T6/T7)
    t6 = results['T6']
    js_values = list(t6['js_divergence_matrix'].values())
    mean_js = sum(js_values) / len(js_values) if js_values else 0
    max_js = max(js_values) if js_values else 0
    min_js = min(js_values) if js_values else 0
    print(f"  Section class JS divergence: mean={mean_js:.4f}, "
          f"range [{min_js:.4f}, {max_js:.4f}]")

    section_verdict = 'SECTION_DIFFERENTIATED' if mean_js > 0.02 else 'SECTION_HOMOGENEOUS'
    print(f"  SECTION VERDICT: {section_verdict}")

    return {
        'targeting_verdict': v,
        'targeting_reason': reason,
        'section_verdict': section_verdict,
        'key_metrics': {
            'f66r_overlap_rank': f66r_overlap_rank,
            'f66r_bridge_rank': f66r_bridge_rank,
            'f66r_bridge_density': f66r_bridge_density,
            'rho_bridge_overlap': rho_bridge_overlap,
            'shared_bridge_fraction': shared_bridge_frac,
            'is_size_artifact': is_size_artifact,
            'bridge_gradient': bridge_gradient,
            'mean_section_js': mean_js,
        },
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 405: Section Program Architecture and Rosettes Targeting")
    print("=" * 70)

    data = load_data()

    results = {}
    results['T1'] = t1_per_folio_rosettes_overlap(data)
    results['T2'] = t2_per_folio_bridge_density(data)
    results['T3'] = t3_overlap_decomposition(data)
    results['T4'] = t4_size_controlled_comparison(data)
    results['T5'] = t5_section_bridge_density(data)
    results['T6'] = t6_section_class_distribution(data)
    results['T7'] = t7_section_role_profiles(data)
    results['T8'] = t8_section_kernel_balance(data)

    v = verdict(results)

    output = {
        'phase': 405,
        'name': 'SECTION_PROGRAM_ARCHITECTURE',
        'test_count': 8,
        'note': 'Section T = "Text" (text-only pages), NOT "Pharmaceutical" (P). '
                'C1125 parenthetical "(pharmaceutical)" is incorrect.',
        'b_section_sizes': {
            s: {'folios': len(data['section_folios'][s]),
                'tokens': len(data['section_tokens'][s]),
                'middles': len(data['section_middles'][s])}
            for s in data['section_folios']
        },
        'T1': results['T1'],
        'T2': results['T2'],
        'T3': results['T3'],
        'T4': results['T4'],
        'T5': results['T5'],
        'T6': results['T6'],
        'T7': results['T7'],
        'T8': results['T8'],
        'verdict': v,
    }

    # Remove large intermediate data to keep JSON manageable
    if 'all_jaccards' in output['T1']:
        del output['T1']['all_jaccards']
    if 'all_bridge_densities' in output['T2']:
        del output['T2']['all_bridge_densities']

    out_path = PROJECT / 'phases' / 'ROSETTES_SYSTEM_REVALIDATION' / 'results' / 'section_program_architecture.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()

"""
Phase 472: DARK_PIPELINE_STRUCTURE

Characterizes whether dark pipeline MIDDLEs (300 MIDDLEs, identification channel)
behave structurally like material referents, process identifiers, or something else.
Phase 471 showed dark preserves category structure near-perfectly (rho=0.976) while
bridge gets reshaped. This phase tests what structural role dark MIDDLEs play.

Tests:
  T1: Within-folio co-occurrence (section-controlled)
  T2: Successor profile entropy
  T3: Folio span distribution shape
  T4: Dark-bridge relative ordering
  T5: Dark-dark adjacency rate

References: C1135, C1148, C1141, C1176, C1177, C1147, C942, C1349
"""

import json
import sys
import math
import time
import random
import functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

# Phase 452: data loading
sys.path.insert(0, str(ROOT / 'phases' / 'A_CATEGORY_SCATTERSHOT' / 'scripts'))
from a_category_scattershot import load_all_data, build_category_map, ALL_CATEGORIES

# Phase 462: stats
sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import (
    jsd, normalize_profile, mann_whitney_u, normal_cdf, chi2_sf, jaccard
)

# Phase 469: MI, chi2, entropy
sys.path.insert(0, str(ROOT / 'phases' / 'SUFFIX_MODE_ASSIGNMENT' / 'scripts'))
from suffix_mode_assignment import (
    mutual_information, chi2_independence, entropy_from_counts
)

# Phase 463: Spearman
sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "DARK_PIPELINE_STRUCTURE" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42
MIN_DARK_FREQ = 5  # Dark MIDDLEs with >= 5 B tokens for statistical reliability


# ── Data loading ────────────────────────────────────────────────

def build_data():
    """Load and pre-compute all data structures needed across tests."""
    a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles, bridge_middles, dark_middles = load_all_data()

    # Load 49-class token map for T2
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build ordered B tokens per (folio, line), annotated with is_dark/is_bridge
    b_line_tokens = defaultdict(list)
    folio_to_section = {}
    for tok in b_tokens:
        mid = tok.get('middle')
        tok['is_dark'] = (mid in dark_middles) if mid else False
        tok['is_bridge'] = (mid in bridge_middles) if mid else False
        key = (tok['folio'], tok['line'])
        b_line_tokens[key].append(tok)
        folio_to_section[tok['folio']] = tok['section']

    # Per-MIDDLE aggregates for dark pipeline
    dark_mid_folios = defaultdict(set)
    dark_mid_tokens = defaultdict(list)
    dark_mid_sections = defaultdict(set)
    for tok in b_tokens:
        mid = tok.get('middle')
        if mid and mid in dark_middles:
            dark_mid_folios[mid].add(tok['folio'])
            dark_mid_tokens[mid].append(tok)
            dark_mid_sections[mid].add(tok['section'])

    reliable_dark = {m for m, toks in dark_mid_tokens.items() if len(toks) >= MIN_DARK_FREQ}

    return {
        'b_tokens': b_tokens,
        'b_line_tokens': dict(b_line_tokens),
        'dark_middles': dark_middles,
        'bridge_middles': bridge_middles,
        'dark_mid_folios': dict(dark_mid_folios),
        'dark_mid_tokens': dict(dark_mid_tokens),
        'dark_mid_sections': dict(dark_mid_sections),
        'reliable_dark': reliable_dark,
        'token_to_class': token_to_class,
        'folio_to_section': folio_to_section,
    }


# ── T1: Within-Folio Co-occurrence (Section-Controlled) ────────

def test_t1(data, rng):
    print("\n── T1: Within-Folio Co-occurrence Structure ──")
    dark_mid_folios = data['dark_mid_folios']
    reliable = sorted(data['reliable_dark'])
    folio_to_section = data['folio_to_section']

    if len(reliable) < 10:
        print("  Too few reliable dark MIDDLEs for co-occurrence analysis")
        return {'test': 'T1_cooccurrence', 'verdict': 'INSUFFICIENT_DATA',
                'n_reliable': len(reliable)}

    # ── Global Jaccard ──
    global_jaccards = []
    for i in range(len(reliable)):
        for j in range(i + 1, len(reliable)):
            fa = dark_mid_folios.get(reliable[i], set())
            fb = dark_mid_folios.get(reliable[j], set())
            if fa or fb:
                inter = len(fa & fb)
                union = len(fa | fb)
                jac = inter / union if union > 0 else 0.0
                global_jaccards.append(jac)

    n_pairs = len(global_jaccards)
    frac_zero = sum(1 for j in global_jaccards if j == 0.0) / n_pairs if n_pairs else 0.0
    non_zero = [j for j in global_jaccards if j > 0.0]
    non_zero_mean = sum(non_zero) / len(non_zero) if non_zero else 0.0
    non_zero_median = sorted(non_zero)[len(non_zero) // 2] if non_zero else 0.0
    global_mean = sum(global_jaccards) / n_pairs if n_pairs else 0.0

    print(f"  Global: {len(reliable)} reliable dark MIDDLEs, {n_pairs} pairs")
    print(f"  Fraction at zero: {frac_zero:.3f}")
    print(f"  Non-zero mean: {non_zero_mean:.4f}, median: {non_zero_median:.4f}")
    print(f"  Global mean Jaccard: {global_mean:.4f}")

    # ── Section-controlled Jaccard ──
    sections = sorted(set(folio_to_section.values()))
    section_folios = {s: {f for f, sec in folio_to_section.items() if sec == s}
                      for s in sections}

    section_results = {}
    all_within_jaccards = []

    for sec in sections:
        sec_fols = section_folios[sec]
        # Dark MIDDLEs that appear in this section
        sec_darks = [m for m in reliable
                     if dark_mid_folios.get(m, set()) & sec_fols]
        if len(sec_darks) < 5:
            section_results[sec] = {'n_middles': len(sec_darks), 'skipped': True}
            continue

        # Section-restricted folio sets
        sec_mid_folios = {m: dark_mid_folios.get(m, set()) & sec_fols
                          for m in sec_darks}

        jacs = []
        for i in range(len(sec_darks)):
            for j in range(i + 1, len(sec_darks)):
                fa = sec_mid_folios[sec_darks[i]]
                fb = sec_mid_folios[sec_darks[j]]
                inter = len(fa & fb)
                union = len(fa | fb)
                jac = inter / union if union > 0 else 0.0
                jacs.append(jac)

        if not jacs:
            section_results[sec] = {'n_middles': len(sec_darks), 'n_pairs': 0}
            continue

        sec_frac_zero = sum(1 for j in jacs if j == 0.0) / len(jacs)
        sec_nz = [j for j in jacs if j > 0.0]
        sec_nz_mean = sum(sec_nz) / len(sec_nz) if sec_nz else 0.0
        sec_mean = sum(jacs) / len(jacs)
        all_within_jaccards.extend(jacs)

        # Permutation null: shuffle folio assignments within section
        null_means = []
        mid_spans = [len(sec_mid_folios[m]) for m in sec_darks]
        sec_fol_list = sorted(sec_fols)
        for _ in range(N_PERM):
            perm_folios = {}
            for k, m in enumerate(sec_darks):
                span = mid_spans[k]
                perm_folios[m] = set(rng.sample(sec_fol_list,
                                                min(span, len(sec_fol_list))))
            perm_jacs = []
            for i in range(len(sec_darks)):
                for j in range(i + 1, len(sec_darks)):
                    fa = perm_folios[sec_darks[i]]
                    fb = perm_folios[sec_darks[j]]
                    inter = len(fa & fb)
                    union = len(fa | fb)
                    perm_jacs.append(inter / union if union > 0 else 0.0)
            null_means.append(sum(perm_jacs) / len(perm_jacs) if perm_jacs else 0.0)

        null_mean = sum(null_means) / len(null_means)
        perm_p = sum(1 for nm in null_means if nm >= sec_mean) / len(null_means)

        section_results[sec] = {
            'n_middles': len(sec_darks),
            'n_pairs': len(jacs),
            'frac_zero': round(sec_frac_zero, 4),
            'mean_jaccard': round(sec_mean, 4),
            'nz_mean': round(sec_nz_mean, 4),
            'null_mean': round(null_mean, 4),
            'perm_p': round(perm_p, 4),
        }
        print(f"  Section {sec}: {len(sec_darks)} MIDDLEs, "
              f"mean Jaccard {sec_mean:.4f} (null {null_mean:.4f}), "
              f"frac_zero {sec_frac_zero:.3f}, perm_p={perm_p:.4f}")

    # Within-section aggregate
    ws_frac_zero = (sum(1 for j in all_within_jaccards if j == 0.0) / len(all_within_jaccards)
                    if all_within_jaccards else 0.0)
    ws_mean = sum(all_within_jaccards) / len(all_within_jaccards) if all_within_jaccards else 0.0

    # Did section control collapse the structure?
    section_collapsed = ws_mean < global_mean * 0.5

    # Verdict
    significant_sections = sum(1 for s, r in section_results.items()
                               if not r.get('skipped') and r.get('perm_p', 1.0) < 0.05)
    if significant_sections >= 2 and ws_mean > 0.02:
        verdict = 'CLUSTERED'
    elif section_collapsed:
        verdict = 'SECTION_ONLY'
    elif frac_zero < 0.20:
        verdict = 'CONTINUOUS'
    else:
        verdict = 'MIXED'

    print(f"  Within-section aggregate: mean={ws_mean:.4f}, frac_zero={ws_frac_zero:.3f}")
    print(f"  Section collapsed: {section_collapsed}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T1_cooccurrence',
        'verdict': verdict,
        'n_reliable': len(reliable),
        'n_pairs_global': n_pairs,
        'global_frac_zero': round(frac_zero, 4),
        'global_mean_jaccard': round(global_mean, 4),
        'global_nz_mean': round(non_zero_mean, 4),
        'global_nz_median': round(non_zero_median, 4),
        'within_section_mean': round(ws_mean, 4),
        'within_section_frac_zero': round(ws_frac_zero, 4),
        'section_collapsed': section_collapsed,
        'significant_sections': significant_sections,
        'section_results': section_results,
    }


# ── T2: Successor Profile Entropy ──────────────────────────────

def test_t2(data, rng):
    print("\n── T2: Successor Profile Entropy ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    bridge_middles = data['bridge_middles']
    token_to_class = data['token_to_class']

    # Build successor profiles
    dark_successors = defaultdict(Counter)
    bridge_successors = defaultdict(Counter)
    dark_class_count = 0
    dark_noclass_count = 0
    bridge_class_count = 0
    bridge_noclass_count = 0

    for key, toks in b_line_tokens.items():
        for i in range(len(toks) - 1):
            mid = toks[i].get('middle')
            if not mid:
                continue
            succ_word = toks[i + 1]['word']
            succ_class = token_to_class.get(succ_word)

            if mid in dark_middles:
                if succ_class is not None:
                    dark_successors[mid][succ_class] += 1
                    dark_class_count += 1
                else:
                    dark_noclass_count += 1
            elif mid in bridge_middles:
                if succ_class is not None:
                    bridge_successors[mid][succ_class] += 1
                    bridge_class_count += 1
                else:
                    bridge_noclass_count += 1

    dark_noclass_rate = (dark_noclass_count / (dark_class_count + dark_noclass_count)
                         if (dark_class_count + dark_noclass_count) > 0 else 0.0)
    bridge_noclass_rate = (bridge_noclass_count / (bridge_class_count + bridge_noclass_count)
                           if (bridge_class_count + bridge_noclass_count) > 0 else 0.0)

    print(f"  Dark successors: {dark_class_count} classified, "
          f"{dark_noclass_count} unclassified ({dark_noclass_rate:.1%} no-class)")
    print(f"  Bridge successors: {bridge_class_count} classified, "
          f"{bridge_noclass_count} unclassified ({bridge_noclass_rate:.1%} no-class)")

    # Compute per-MIDDLE entropy (only MIDDLEs with enough classified successors)
    min_succ = MIN_DARK_FREQ
    dark_entropies = []
    dark_entropy_details = []
    for mid in sorted(dark_successors):
        total = sum(dark_successors[mid].values())
        if total >= min_succ:
            h = entropy_from_counts(dark_successors[mid])
            n_classes = len(dark_successors[mid])
            dark_entropies.append(h)
            dark_entropy_details.append({
                'middle': mid, 'entropy': round(h, 4),
                'n_observations': total, 'n_classes': n_classes
            })

    bridge_entropies = []
    for mid in sorted(bridge_successors):
        total = sum(bridge_successors[mid].values())
        if total >= min_succ:
            h = entropy_from_counts(bridge_successors[mid])
            bridge_entropies.append(h)

    print(f"  Dark MIDDLEs with >={min_succ} classified successors: {len(dark_entropies)}")
    print(f"  Bridge MIDDLEs with >={min_succ} classified successors: {len(bridge_entropies)}")

    if not dark_entropies or not bridge_entropies:
        print("  Insufficient data for comparison")
        return {
            'test': 'T2_successor_entropy',
            'verdict': 'INSUFFICIENT_DATA',
            'n_dark_qualified': len(dark_entropies),
            'n_bridge_qualified': len(bridge_entropies),
            'dark_noclass_rate': round(dark_noclass_rate, 4),
        }

    dark_median = sorted(dark_entropies)[len(dark_entropies) // 2]
    bridge_median = sorted(bridge_entropies)[len(bridge_entropies) // 2]
    dark_mean = sum(dark_entropies) / len(dark_entropies)
    bridge_mean = sum(bridge_entropies) / len(bridge_entropies)

    # Mann-Whitney comparison
    u, z, p = mann_whitney_u(dark_entropies, bridge_entropies)

    print(f"  Dark entropy: median={dark_median:.3f}, mean={dark_mean:.3f}")
    print(f"  Bridge entropy: median={bridge_median:.3f}, mean={bridge_mean:.3f}")
    print(f"  Mann-Whitney: Z={z:.3f}, p={p:.4f}")

    # Verdict
    if p < 0.01 and dark_mean > bridge_mean:
        verdict = 'WIDE'
    elif p < 0.01 and dark_mean < bridge_mean:
        verdict = 'NARROW'
    else:
        verdict = 'COMPARABLE'

    print(f"  Verdict: {verdict}")

    # Top/bottom dark MIDDLE details
    sorted_details = sorted(dark_entropy_details, key=lambda x: x['entropy'])

    return {
        'test': 'T2_successor_entropy',
        'verdict': verdict,
        'n_dark_qualified': len(dark_entropies),
        'n_bridge_qualified': len(bridge_entropies),
        'dark_median_entropy': round(dark_median, 4),
        'dark_mean_entropy': round(dark_mean, 4),
        'bridge_median_entropy': round(bridge_median, 4),
        'bridge_mean_entropy': round(bridge_mean, 4),
        'mann_whitney_z': round(z, 4),
        'mann_whitney_p': round(p, 4),
        'dark_noclass_rate': round(dark_noclass_rate, 4),
        'bridge_noclass_rate': round(bridge_noclass_rate, 4),
        'lowest_entropy_dark': sorted_details[:5] if sorted_details else [],
        'highest_entropy_dark': sorted_details[-5:] if sorted_details else [],
    }


# ── T3: Folio Span Distribution Shape ──────────────────────────

def test_t3(data, rng):
    print("\n── T3: Folio Span Distribution Shape ──")
    dark_mid_folios = data['dark_mid_folios']
    dark_mid_tokens = data['dark_mid_tokens']
    reliable = sorted(data['reliable_dark'])

    # Folio weights (proportional to B token count)
    folio_counts = Counter()
    for tok in data['b_tokens']:
        folio_counts[tok['folio']] += 1
    folios_list = sorted(folio_counts.keys())
    folio_weights = [folio_counts[f] for f in folios_list]

    span_results = []
    n_concentrated = 0
    n_dispersed = 0
    n_expected = 0

    for mid in reliable:
        n_tokens = len(dark_mid_tokens[mid])
        obs_span = len(dark_mid_folios.get(mid, set()))

        # Null: distribute n_tokens across folios proportional to folio size
        null_spans = []
        for _ in range(N_PERM):
            sampled = rng.choices(folios_list, weights=folio_weights, k=n_tokens)
            null_spans.append(len(set(sampled)))

        null_mean = sum(null_spans) / len(null_spans)
        null_std = (sum((s - null_mean) ** 2 for s in null_spans) / len(null_spans)) ** 0.5
        z = (obs_span - null_mean) / null_std if null_std > 0 else 0.0

        if z < -2:
            n_concentrated += 1
        elif z > 2:
            n_dispersed += 1
        else:
            n_expected += 1

        span_results.append({
            'middle': mid,
            'n_tokens': n_tokens,
            'obs_span': obs_span,
            'null_mean': round(null_mean, 2),
            'null_std': round(null_std, 2),
            'z': round(z, 2),
        })

    total = len(reliable)
    frac_conc = n_concentrated / total if total else 0.0
    frac_disp = n_dispersed / total if total else 0.0
    frac_exp = n_expected / total if total else 0.0

    print(f"  Reliable dark MIDDLEs: {total}")
    print(f"  Concentrated (z<-2): {n_concentrated} ({frac_conc:.1%})")
    print(f"  Expected (-2<z<2): {n_expected} ({frac_exp:.1%})")
    print(f"  Dispersed (z>2): {n_dispersed} ({frac_disp:.1%})")

    # Distribution of observed spans
    obs_spans = [r['obs_span'] for r in span_results]
    span_dist = Counter(obs_spans)
    mean_span = sum(obs_spans) / len(obs_spans) if obs_spans else 0.0
    median_span = sorted(obs_spans)[len(obs_spans) // 2] if obs_spans else 0

    print(f"  Span distribution: mean={mean_span:.1f}, median={median_span}")
    print(f"  Span=1: {span_dist.get(1, 0)}, Span=2: {span_dist.get(2, 0)}, "
          f"Span>=5: {sum(v for k, v in span_dist.items() if k >= 5)}")

    # Verdict
    if frac_conc > 0.60:
        verdict = 'CONCENTRATED'
    elif frac_disp > 0.60:
        verdict = 'DISPERSED'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    # Most extreme examples
    sorted_by_z = sorted(span_results, key=lambda x: x['z'])

    return {
        'test': 'T3_folio_span',
        'verdict': verdict,
        'n_reliable': total,
        'n_concentrated': n_concentrated,
        'n_expected': n_expected,
        'n_dispersed': n_dispersed,
        'frac_concentrated': round(frac_conc, 4),
        'frac_dispersed': round(frac_disp, 4),
        'mean_span': round(mean_span, 2),
        'median_span': median_span,
        'span_distribution': {str(k): v for k, v in sorted(span_dist.items())},
        'most_concentrated': sorted_by_z[:5],
        'most_dispersed': sorted_by_z[-5:],
    }


# ── T4: Dark-Bridge Relative Ordering ──────────────────────────

def test_t4(data, rng):
    print("\n── T4: Dark-Bridge Relative Ordering ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    bridge_middles = data['bridge_middles']

    dark_before = 0
    total_pairs = 0
    section_stats = defaultdict(lambda: [0, 0])  # section -> [dark_before, total]

    # Per-line data for permutation
    mixed_lines = []  # [(section, dark_positions, bridge_positions), ...]

    for key, toks in b_line_tokens.items():
        dark_pos = []
        bridge_pos = []
        section = toks[0]['section'] if toks else None
        for i, tok in enumerate(toks):
            mid = tok.get('middle')
            if not mid:
                continue
            if mid in dark_middles:
                dark_pos.append(i)
            elif mid in bridge_middles:
                bridge_pos.append(i)

        if not dark_pos or not bridge_pos:
            continue

        mixed_lines.append((section, dark_pos, bridge_pos))

        for dp in dark_pos:
            for bp in bridge_pos:
                total_pairs += 1
                if dp < bp:
                    dark_before += 1
                if section:
                    section_stats[section][1] += 1
                    if dp < bp:
                        section_stats[section][0] += 1

    if total_pairs == 0:
        print("  No mixed lines found")
        return {'test': 'T4_ordering', 'verdict': 'INSUFFICIENT_DATA',
                'total_pairs': 0}

    obs_frac = dark_before / total_pairs

    print(f"  Mixed lines: {len(mixed_lines)}")
    print(f"  Total dark-bridge pairs: {total_pairs}")
    print(f"  Dark-before-bridge fraction: {obs_frac:.4f}")

    # Section breakdown
    sec_fracs = {}
    for sec in sorted(section_stats):
        db, tp = section_stats[sec]
        sec_fracs[sec] = {'dark_before': db, 'total': tp,
                          'fraction': round(db / tp, 4) if tp > 0 else 0.0}
        print(f"  Section {sec}: {db}/{tp} = {db / tp:.3f}" if tp else f"  Section {sec}: 0/0")

    # Permutation null: on each mixed line, shuffle dark/bridge labels among
    # the occupied positions while preserving counts
    null_fracs = []
    for _ in range(N_PERM):
        perm_db = 0
        perm_total = 0
        for section, dark_pos, bridge_pos in mixed_lines:
            all_pos = dark_pos + bridge_pos
            rng.shuffle(all_pos)
            n_dark = len(dark_pos)
            perm_dark = set(all_pos[:n_dark])
            perm_bridge = set(all_pos[n_dark:])
            for dp in perm_dark:
                for bp in perm_bridge:
                    perm_total += 1
                    if dp < bp:
                        perm_db += 1
        null_fracs.append(perm_db / perm_total if perm_total > 0 else 0.5)

    null_mean = sum(null_fracs) / len(null_fracs)
    null_std = (sum((f - null_mean) ** 2 for f in null_fracs) / len(null_fracs)) ** 0.5
    z = (obs_frac - null_mean) / null_std if null_std > 0 else 0.0
    perm_p = sum(1 for nf in null_fracs if abs(nf - 0.5) >= abs(obs_frac - 0.5)) / len(null_fracs)

    print(f"  Null mean: {null_mean:.4f}, Z={z:.3f}, perm_p={perm_p:.4f}")

    # Verdict
    if perm_p < 0.01 and (obs_frac < 0.40 or obs_frac > 0.60):
        verdict = 'ORDERED'
    elif 0.45 <= obs_frac <= 0.55 and perm_p > 0.05:
        verdict = 'UNORDERED'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T4_ordering',
        'verdict': verdict,
        'n_mixed_lines': len(mixed_lines),
        'total_pairs': total_pairs,
        'dark_before': dark_before,
        'obs_fraction': round(obs_frac, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z': round(z, 3),
        'perm_p': round(perm_p, 4),
        'section_fractions': sec_fracs,
    }


# ── T5: Dark-Dark Adjacency Rate ───────────────────────────────

def test_t5(data, rng):
    print("\n── T5: Dark-Dark Adjacency Rate ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']

    obs_dd = 0
    obs_total = 0
    section_stats = defaultdict(lambda: [0, 0])  # section -> [dd_pairs, total_pairs]

    # Per-line data for permutation
    line_data = []  # [(n_tokens, n_dark, section), ...]

    for key, toks in b_line_tokens.items():
        n = len(toks)
        if n < 2:
            continue

        dark_positions = set()
        section = toks[0]['section'] if toks else None
        for i, tok in enumerate(toks):
            mid = tok.get('middle')
            if mid and mid in dark_middles:
                dark_positions.add(i)

        n_dark = len(dark_positions)
        line_data.append((n, n_dark, section))

        for i in range(n - 1):
            obs_total += 1
            if section:
                section_stats[section][1] += 1
            if i in dark_positions and (i + 1) in dark_positions:
                obs_dd += 1
                if section:
                    section_stats[section][0] += 1

    obs_rate = obs_dd / obs_total if obs_total > 0 else 0.0

    print(f"  Total adjacent pairs: {obs_total}")
    print(f"  Dark-dark adjacent pairs: {obs_dd}")
    print(f"  Observed rate: {obs_rate:.6f}")

    # Section breakdown
    sec_rates = {}
    for sec in sorted(section_stats):
        dd, tp = section_stats[sec]
        sec_rates[sec] = {'dd_pairs': dd, 'total_pairs': tp,
                          'rate': round(dd / tp, 6) if tp > 0 else 0.0}
        print(f"  Section {sec}: {dd}/{tp} = {dd / tp:.6f}" if tp else f"  Section {sec}: 0/0")

    # Permutation null: per line, preserve n_dark but shuffle positions
    null_rates = []
    for _ in range(N_PERM):
        perm_dd = 0
        perm_total = 0
        for n, n_dark, section in line_data:
            if n < 2:
                continue
            perm_total += n - 1
            if n_dark == 0 or n_dark >= n:
                # If all or none are dark, adjacency is deterministic
                if n_dark >= n:
                    perm_dd += n - 1
                continue
            positions = set(rng.sample(range(n), n_dark))
            for i in range(n - 1):
                if i in positions and (i + 1) in positions:
                    perm_dd += 1
        null_rates.append(perm_dd / perm_total if perm_total > 0 else 0.0)

    null_mean = sum(null_rates) / len(null_rates)
    null_std = (sum((r - null_mean) ** 2 for r in null_rates) / len(null_rates)) ** 0.5
    ratio = obs_rate / null_mean if null_mean > 0 else float('inf')
    perm_p_high = sum(1 for nr in null_rates if nr >= obs_rate) / len(null_rates)
    perm_p_low = sum(1 for nr in null_rates if nr <= obs_rate) / len(null_rates)
    perm_p = min(perm_p_high, perm_p_low) * 2  # two-sided

    print(f"  Null mean: {null_mean:.6f}")
    print(f"  Observed/null ratio: {ratio:.3f}")
    print(f"  Perm p (two-sided): {perm_p:.4f}")

    # Verdict
    if ratio > 1.5 and perm_p < 0.01:
        verdict = 'CLUSTERED'
    elif ratio < 0.67 and perm_p < 0.01:
        verdict = 'DISPERSED'
    elif 0.8 <= ratio <= 1.2:
        verdict = 'RANDOM'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T5_adjacency',
        'verdict': verdict,
        'obs_dd_pairs': obs_dd,
        'obs_total_pairs': obs_total,
        'obs_rate': round(obs_rate, 6),
        'null_mean': round(null_mean, 6),
        'null_std': round(null_std, 6),
        'ratio': round(ratio, 4),
        'perm_p': round(perm_p, 4),
        'section_rates': sec_rates,
    }


# ── Main ────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("Phase 472: DARK_PIPELINE_STRUCTURE")
    print("=" * 60)

    print("\nLoading data...")
    data = build_data()
    print(f"  Dark MIDDLEs: {len(data['dark_middles'])}")
    print(f"  Bridge MIDDLEs: {len(data['bridge_middles'])}")
    print(f"  Reliable dark (>={MIN_DARK_FREQ} tokens): {len(data['reliable_dark'])}")
    print(f"  B lines: {len(data['b_line_tokens'])}")
    print(f"  49-class tokens: {len(data['token_to_class'])}")

    results = {}
    results['T1'] = test_t1(data, rng)
    results['T2'] = test_t2(data, rng)
    results['T3'] = test_t3(data, rng)
    results['T4'] = test_t4(data, rng)
    results['T5'] = test_t5(data, rng)

    dt = time.time() - t0
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    verdicts = {}
    for key in ['T1', 'T2', 'T3', 'T4', 'T5']:
        v = results[key]['verdict']
        verdicts[key] = v
        print(f"  {key}: {v}")

    results['meta'] = {
        'phase': 472,
        'name': 'DARK_PIPELINE_STRUCTURE',
        'n_dark_middles': len(data['dark_middles']),
        'n_bridge_middles': len(data['bridge_middles']),
        'n_reliable_dark': len(data['reliable_dark']),
        'min_dark_freq': MIN_DARK_FREQ,
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
        'verdicts': verdicts,
    }

    out_path = RESULTS_DIR / "dark_pipeline_structure.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")
    print(f"Runtime: {dt:.1f}s")


if __name__ == '__main__':
    main()

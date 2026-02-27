"""
Phase 473: LAYERED_GRAMMAR_TEST

Tests whether Currier B grammar has three tiers rather than a binary
grammar/non-grammar split:
  Tier 1 (Context):   Dark MIDDLEs -- set execution context
  Tier 2 (Execution): Bridge MIDDLEs -- 49-class instruction grammar
  Tier 3 (Mode):      Suffix system -- terminal/connector/iterate/bare

Two gate tests (T1, T2) must pass before core tests (T3-T5) are meaningful.

Tests:
  T1: Frequency-matched entropy control (GATE)
  T2: PREFIX independence (GATE)
  T3: Dark MIDDLE conditions bridge transitions (CORE)
  T4: Dark proximity modulates suffix (CORE)
  T5: Dark removal genericizes transitions (CORE)

References: C1351, C1138, C405, C1004, C1003, C1342, C1346
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
    jsd, normalize_profile, mann_whitney_u, normal_cdf, chi2_sf
)

# Phase 469: MI, chi2, entropy
sys.path.insert(0, str(ROOT / 'phases' / 'SUFFIX_MODE_ASSIGNMENT' / 'scripts'))
from suffix_mode_assignment import (
    mutual_information, chi2_independence, entropy_from_counts, suffix_category
)

# Phase 463: Spearman
sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "LAYERED_GRAMMAR_TEST" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
SEED = 42
MIN_FREQ = 5


# ── Data loading ────────────────────────────────────────────────

def build_data():
    """Load and pre-compute all data structures."""
    a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles, bridge_middles, dark_middles = load_all_data()
    morph = Morphology()

    # Load 49-class token map
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build ordered B tokens per (folio, line) with annotations
    b_line_tokens = defaultdict(list)
    folio_to_section = {}
    for tok in b_tokens:
        mid = tok.get('middle')
        word = tok.get('word', '')
        tok['is_dark'] = (mid in dark_middles) if mid else False
        tok['is_bridge'] = (mid in bridge_middles) if mid else False
        tok['class_id'] = token_to_class.get(word)
        tok['suffix_cat'] = suffix_category(tok.get('suffix'))
        key = (tok['folio'], tok['line'])
        b_line_tokens[key].append(tok)
        folio_to_section[tok['folio']] = tok['section']

    # Per-MIDDLE token counts in B
    mid_b_counts = Counter()
    for tok in b_tokens:
        mid = tok.get('middle')
        if mid:
            mid_b_counts[mid] += 1

    return {
        'b_tokens': b_tokens,
        'b_line_tokens': dict(b_line_tokens),
        'dark_middles': dark_middles,
        'bridge_middles': bridge_middles,
        'token_to_class': token_to_class,
        'folio_to_section': folio_to_section,
        'mid_b_counts': mid_b_counts,
        'morph': morph,
    }


# ── T1: Frequency-Matched Entropy Control (GATE) ───────────────

def test_t1(data, rng):
    print("\n── T1: Frequency-Matched Entropy Control (GATE) ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    bridge_middles = data['bridge_middles']
    token_to_class = data['token_to_class']
    mid_b_counts = data['mid_b_counts']

    # Build successor profiles for all MIDDLEs
    mid_successors = defaultdict(Counter)
    for key, toks in b_line_tokens.items():
        for i in range(len(toks) - 1):
            mid = toks[i].get('middle')
            if not mid:
                continue
            succ_word = toks[i + 1]['word']
            succ_class = token_to_class.get(succ_word)
            if succ_class is not None:
                mid_successors[mid][succ_class] += 1

    # Build entropy + frequency for qualified MIDDLEs
    dark_data = []
    bridge_data = []
    for mid, succs in mid_successors.items():
        total_succ = sum(succs.values())
        if total_succ < MIN_FREQ:
            continue
        h = entropy_from_counts(succs)
        freq = mid_b_counts[mid]
        if mid in dark_middles:
            dark_data.append({'middle': mid, 'entropy': h, 'freq': freq,
                              'n_succ': total_succ})
        elif mid in bridge_middles:
            bridge_data.append({'middle': mid, 'entropy': h, 'freq': freq,
                                'n_succ': total_succ})

    print(f"  Qualified dark MIDDLEs: {len(dark_data)}")
    print(f"  Qualified bridge MIDDLEs: {len(bridge_data)}")

    if not dark_data or not bridge_data:
        return {'test': 'T1_frequency_gate', 'verdict': 'INSUFFICIENT_DATA'}

    # ── Frequency-matched comparison ──
    # For each dark MIDDLE, find bridge MIDDLEs within 2x frequency window
    matched_bridge = []
    unmatched_dark = 0
    for dd in dark_data:
        lo = dd['freq'] / 2
        hi = dd['freq'] * 2
        candidates = [bd for bd in bridge_data if lo <= bd['freq'] <= hi]
        if candidates:
            matched_bridge.extend(candidates)
        else:
            unmatched_dark += 1

    # Deduplicate matched bridge
    matched_bridge_set = {bd['middle']: bd for bd in matched_bridge}
    matched_bridge_unique = list(matched_bridge_set.values())

    dark_entropies = [d['entropy'] for d in dark_data]
    matched_entropies = [b['entropy'] for b in matched_bridge_unique]

    if len(matched_bridge_unique) < 5:
        print(f"  Too few frequency-matched bridge MIDDLEs: {len(matched_bridge_unique)}")
        # Fall back to subsampling
        matched_entropies = []

    dark_median = sorted(dark_entropies)[len(dark_entropies) // 2]
    dark_mean = sum(dark_entropies) / len(dark_entropies)

    # ── Subsampling approach (more robust) ──
    # For each bridge MIDDLE, subsample its successor observations to match
    # median dark successor count, recompute entropy
    dark_n_succs = [d['n_succ'] for d in dark_data]
    median_dark_n = sorted(dark_n_succs)[len(dark_n_succs) // 2]

    subsample_entropies = []
    for bd in bridge_data:
        if bd['n_succ'] < median_dark_n:
            continue
        # Expand successor Counter to list, subsample
        succ_list = []
        for cls, cnt in mid_successors[bd['middle']].items():
            succ_list.extend([cls] * cnt)
        # Subsample N_PERM times, take mean entropy
        sub_hs = []
        for _ in range(100):
            sample = rng.sample(succ_list, median_dark_n)
            sub_hs.append(entropy_from_counts(Counter(sample)))
        subsample_entropies.append(sum(sub_hs) / len(sub_hs))

    print(f"  Subsampled bridge MIDDLEs (to n={median_dark_n}): {len(subsample_entropies)}")

    # Compare: dark vs frequency-matched bridge
    if matched_entropies and len(matched_entropies) >= 5:
        u1, z1, p1 = mann_whitney_u(dark_entropies, matched_entropies)
        matched_median = sorted(matched_entropies)[len(matched_entropies) // 2]
        matched_mean = sum(matched_entropies) / len(matched_entropies)
        print(f"  Frequency-matched: dark median={dark_median:.3f}, "
              f"bridge median={matched_median:.3f}, Z={z1:.3f}, p={p1:.4f}")
    else:
        z1, p1 = 0.0, 1.0
        matched_median, matched_mean = 0.0, 0.0

    # Compare: dark vs subsampled bridge
    if subsample_entropies:
        u2, z2, p2 = mann_whitney_u(dark_entropies, subsample_entropies)
        sub_median = sorted(subsample_entropies)[len(subsample_entropies) // 2]
        sub_mean = sum(subsample_entropies) / len(subsample_entropies)
        print(f"  Subsampled: dark median={dark_median:.3f}, "
              f"bridge median={sub_median:.3f}, Z={z2:.3f}, p={p2:.4f}")
    else:
        z2, p2 = 0.0, 1.0
        sub_median, sub_mean = 0.0, 0.0

    # Dark frequency stats
    dark_freqs = [d['freq'] for d in dark_data]
    bridge_freqs = [b['freq'] for b in bridge_data]

    # Verdict: gate passes if EITHER method shows significant difference
    if (p1 < 0.01 and z1 < 0) or (p2 < 0.01 and z2 < 0):
        verdict = 'GATE_OPEN'
    elif p1 < 0.05 or p2 < 0.05:
        verdict = 'GATE_MARGINAL'
    else:
        verdict = 'GATE_CLOSED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T1_frequency_gate',
        'verdict': verdict,
        'n_dark': len(dark_data),
        'n_bridge': len(bridge_data),
        'n_freq_matched_bridge': len(matched_bridge_unique),
        'n_subsampled_bridge': len(subsample_entropies),
        'median_dark_n_succ': median_dark_n,
        'dark_median_entropy': round(dark_median, 4),
        'dark_mean_entropy': round(dark_mean, 4),
        'dark_median_freq': sorted(dark_freqs)[len(dark_freqs) // 2],
        'bridge_median_freq': sorted(bridge_freqs)[len(bridge_freqs) // 2],
        'freq_matched_z': round(z1, 4),
        'freq_matched_p': round(p1, 4),
        'freq_matched_median': round(matched_median, 4),
        'subsample_z': round(z2, 4),
        'subsample_p': round(p2, 4),
        'subsample_median': round(sub_median, 4),
    }


# ── T2: PREFIX Independence (GATE) ─────────────────────────────

def test_t2(data, rng):
    print("\n── T2: PREFIX Independence (GATE) ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    token_to_class = data['token_to_class']

    # Collect dark-token → successor-class observations with PREFIX context
    # For each dark token, record: (dark_prefix, dark_middle, successor_class)
    observations = []
    for key, toks in b_line_tokens.items():
        for i in range(len(toks) - 1):
            tok = toks[i]
            mid = tok.get('middle')
            if not mid or mid not in dark_middles:
                continue
            succ_class = toks[i + 1].get('class_id')
            if succ_class is None:
                continue
            pfx = tok.get('prefix') or 'BARE'
            observations.append((pfx, mid, succ_class))

    print(f"  Dark→classified successor observations: {len(observations)}")

    if len(observations) < 50:
        return {'test': 'T2_prefix_independence', 'verdict': 'INSUFFICIENT_DATA',
                'n_observations': len(observations)}

    # Group by PREFIX
    pfx_groups = defaultdict(list)
    for pfx, mid, cls in observations:
        pfx_groups[pfx].append((mid, cls))

    # Within each PREFIX group, compute MI(dark_MIDDLE; successor_class)
    # Then weight-average by group size
    total_obs = 0
    weighted_mi = 0.0
    prefix_details = {}

    for pfx, pairs in sorted(pfx_groups.items()):
        if len(pairs) < 10:
            continue
        mids = [p[0] for p in pairs]
        classes = [p[1] for p in pairs]
        # Need at least 2 distinct values on each axis
        if len(set(mids)) < 2 or len(set(classes)) < 2:
            continue
        mi = mutual_information(mids, classes)
        n = len(pairs)
        weighted_mi += mi * n
        total_obs += n
        prefix_details[pfx] = {
            'n': n,
            'n_middles': len(set(mids)),
            'n_classes': len(set(classes)),
            'mi': round(mi, 4),
        }

    if total_obs == 0:
        return {'test': 'T2_prefix_independence', 'verdict': 'INSUFFICIENT_DATA',
                'n_observations': len(observations)}

    obs_cmi = weighted_mi / total_obs
    print(f"  Conditional MI(dark_MIDDLE; succ_class | PREFIX): {obs_cmi:.4f} bits")
    print(f"  PREFIX groups analyzed: {len(prefix_details)}")
    for pfx, det in sorted(prefix_details.items(), key=lambda x: -x[1]['mi']):
        print(f"    {pfx}: MI={det['mi']:.4f}, n={det['n']}, "
              f"middles={det['n_middles']}, classes={det['n_classes']}")

    # Permutation null: shuffle dark MIDDLE labels within each PREFIX group
    null_cmis = []
    for _ in range(N_PERM):
        perm_weighted = 0.0
        perm_total = 0
        for pfx, pairs in pfx_groups.items():
            if len(pairs) < 10:
                continue
            mids = [p[0] for p in pairs]
            classes = [p[1] for p in pairs]
            if len(set(mids)) < 2 or len(set(classes)) < 2:
                continue
            rng.shuffle(mids)
            mi = mutual_information(mids, classes)
            n = len(pairs)
            perm_weighted += mi * n
            perm_total += n
        if perm_total > 0:
            null_cmis.append(perm_weighted / perm_total)

    null_mean = sum(null_cmis) / len(null_cmis) if null_cmis else 0.0
    null_std = ((sum((x - null_mean) ** 2 for x in null_cmis) / len(null_cmis)) ** 0.5
                if null_cmis else 0.0)
    perm_p = sum(1 for nc in null_cmis if nc >= obs_cmi) / len(null_cmis) if null_cmis else 1.0
    z = (obs_cmi - null_mean) / null_std if null_std > 0 else 0.0

    print(f"  Null mean: {null_mean:.4f}, Z={z:.3f}, perm_p={perm_p:.4f}")

    # Verdict
    if perm_p < 0.01:
        verdict = 'GATE_OPEN'
    elif perm_p < 0.05:
        verdict = 'GATE_MARGINAL'
    else:
        verdict = 'GATE_CLOSED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T2_prefix_independence',
        'verdict': verdict,
        'n_observations': len(observations),
        'n_prefix_groups': len(prefix_details),
        'obs_conditional_mi': round(obs_cmi, 4),
        'null_mean_mi': round(null_mean, 4),
        'null_std_mi': round(null_std, 4),
        'z': round(z, 3),
        'perm_p': round(perm_p, 4),
        'prefix_details': prefix_details,
    }


# ── T3: Dark MIDDLE Conditions Bridge Transitions ──────────────

def test_t3(data, rng):
    print("\n── T3: Dark MIDDLE Conditions Bridge Transitions ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    bridge_middles = data['bridge_middles']
    token_to_class = data['token_to_class']
    folio_to_section = data['folio_to_section']

    # For each line: collect (bridge_current_class, bridge_next_class, dark_middles_on_line, section)
    transition_obs = []
    for key, toks in b_line_tokens.items():
        folio = key[0]
        section = folio_to_section.get(folio, '?')

        # Find dark MIDDLEs on this line
        line_darks = set()
        for tok in toks:
            mid = tok.get('middle')
            if mid and mid in dark_middles:
                line_darks.add(mid)

        # Find bridge-to-bridge classified transitions
        classified = [(i, tok) for i, tok in enumerate(toks) if tok.get('class_id') is not None]
        for idx in range(len(classified) - 1):
            pos_a, tok_a = classified[idx]
            pos_b, tok_b = classified[idx + 1]
            c_a = tok_a['class_id']
            c_b = tok_b['class_id']

            # Is there a dark token between these two classified tokens?
            dark_between = set()
            for j in range(pos_a + 1, pos_b):
                mid = toks[j].get('middle')
                if mid and mid in dark_middles:
                    dark_between.add(mid)

            has_dark = len(line_darks) > 0
            has_dark_between = len(dark_between) > 0

            transition_obs.append({
                'c_a': c_a, 'c_b': c_b,
                'section': section,
                'has_dark_on_line': has_dark,
                'has_dark_between': has_dark_between,
                'dark_between': frozenset(dark_between) if dark_between else None,
                'line_darks': frozenset(line_darks) if line_darks else None,
            })

    print(f"  Bridge-to-bridge classified transitions: {len(transition_obs)}")

    # Split: transitions with dark on line vs without
    with_dark = [t for t in transition_obs if t['has_dark_on_line']]
    without_dark = [t for t in transition_obs if not t['has_dark_on_line']]
    with_dark_between = [t for t in transition_obs if t['has_dark_between']]

    print(f"  With dark on line: {len(with_dark)}")
    print(f"  Without dark: {len(without_dark)}")
    print(f"  With dark between transitions: {len(with_dark_between)}")

    # Compute transition entropy for each group
    def transition_entropy(obs_list):
        pair_counts = Counter()
        for obs in obs_list:
            pair_counts[(obs['c_a'], obs['c_b'])] += 1
        return entropy_from_counts(pair_counts)

    h_with = transition_entropy(with_dark)
    h_without = transition_entropy(without_dark)
    h_between = transition_entropy(with_dark_between) if with_dark_between else 0.0

    print(f"  Transition entropy with dark: {h_with:.4f} bits")
    print(f"  Transition entropy without: {h_without:.4f} bits")
    if with_dark_between:
        print(f"  Transition entropy with dark between: {h_between:.4f} bits")

    # MI(bridge_next; dark_presence | bridge_current)
    # Within each bridge_current class, does dark presence predict bridge_next?
    by_current = defaultdict(list)
    for obs in transition_obs:
        by_current[obs['c_a']].append(obs)

    weighted_mi = 0.0
    total_n = 0
    significant_classes = 0
    for c_a, obs_list in by_current.items():
        if len(obs_list) < 20:
            continue
        dark_labels = ['dark' if o['has_dark_on_line'] else 'no_dark' for o in obs_list]
        next_classes = [o['c_b'] for o in obs_list]
        if len(set(dark_labels)) < 2 or len(set(next_classes)) < 2:
            continue
        mi = mutual_information(dark_labels, next_classes)
        n = len(obs_list)
        weighted_mi += mi * n
        total_n += n
        if mi > 0.01:
            significant_classes += 1

    obs_cmi = weighted_mi / total_n if total_n > 0 else 0.0
    print(f"  Conditional MI(next; dark_presence | current): {obs_cmi:.4f} bits")
    print(f"  Classes with MI>0.01: {significant_classes}")

    # Permutation null: shuffle dark presence labels within each current class
    null_cmis = []
    for _ in range(N_PERM):
        perm_w = 0.0
        perm_n = 0
        for c_a, obs_list in by_current.items():
            if len(obs_list) < 20:
                continue
            dark_labels = ['dark' if o['has_dark_on_line'] else 'no_dark' for o in obs_list]
            next_classes = [o['c_b'] for o in obs_list]
            if len(set(dark_labels)) < 2 or len(set(next_classes)) < 2:
                continue
            rng.shuffle(dark_labels)
            mi = mutual_information(dark_labels, next_classes)
            n = len(obs_list)
            perm_w += mi * n
            perm_n += n
        if perm_n > 0:
            null_cmis.append(perm_w / perm_n)

    null_mean = sum(null_cmis) / len(null_cmis) if null_cmis else 0.0
    perm_p = sum(1 for nc in null_cmis if nc >= obs_cmi) / len(null_cmis) if null_cmis else 1.0

    print(f"  Null mean: {null_mean:.4f}, perm_p={perm_p:.4f}")

    # Verdict
    if perm_p < 0.01 and obs_cmi > null_mean * 1.5:
        verdict = 'CONDITIONED'
    elif perm_p > 0.05:
        verdict = 'INDEPENDENT'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T3_dark_conditions_transitions',
        'verdict': verdict,
        'n_transitions': len(transition_obs),
        'n_with_dark': len(with_dark),
        'n_without_dark': len(without_dark),
        'n_with_dark_between': len(with_dark_between),
        'h_with_dark': round(h_with, 4),
        'h_without_dark': round(h_without, 4),
        'h_with_dark_between': round(h_between, 4),
        'conditional_mi': round(obs_cmi, 4),
        'null_mean': round(null_mean, 4),
        'perm_p': round(perm_p, 4),
        'significant_classes': significant_classes,
    }


# ── T4: Dark Proximity Modulates Suffix ────────────────────────

def test_t4(data, rng):
    print("\n── T4: Dark Proximity Modulates Suffix ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    bridge_middles = data['bridge_middles']

    # For each bridge token, compute distance to nearest dark token
    near_suffixes = Counter()    # distance <= 1
    far_suffixes = Counter()     # distance >= 3 or no dark on line
    near_by_pfx = defaultdict(Counter)
    far_by_pfx = defaultdict(Counter)
    total_near = 0
    total_far = 0

    for key, toks in b_line_tokens.items():
        # Find dark positions
        dark_positions = [i for i, t in enumerate(toks)
                          if t.get('middle') and t['middle'] in dark_middles]

        for i, tok in enumerate(toks):
            mid = tok.get('middle')
            if not mid or mid not in bridge_middles:
                continue
            scat = tok.get('suffix_cat', 'bare')
            pfx = tok.get('prefix') or 'BARE'

            if not dark_positions:
                # No dark on line → far
                far_suffixes[scat] += 1
                far_by_pfx[pfx][scat] += 1
                total_far += 1
            else:
                min_dist = min(abs(i - dp) for dp in dark_positions)
                if min_dist <= 1:
                    near_suffixes[scat] += 1
                    near_by_pfx[pfx][scat] += 1
                    total_near += 1
                elif min_dist >= 3:
                    far_suffixes[scat] += 1
                    far_by_pfx[pfx][scat] += 1
                    total_far += 1

    print(f"  Bridge tokens near dark (dist≤1): {total_near}")
    print(f"  Bridge tokens far from dark (dist≥3): {total_far}")

    if total_near < 50 or total_far < 50:
        return {'test': 'T4_dark_suffix', 'verdict': 'INSUFFICIENT_DATA',
                'n_near': total_near, 'n_far': total_far}

    # Overall suffix distribution comparison
    cats = ['terminal', 'connector', 'iterate', 'bare']
    near_dist = {c: near_suffixes.get(c, 0) / total_near for c in cats}
    far_dist = {c: far_suffixes.get(c, 0) / total_far for c in cats}

    print(f"  Near dark suffix profile: " +
          ", ".join(f"{c}={near_dist[c]:.3f}" for c in cats))
    print(f"  Far from dark suffix profile: " +
          ", ".join(f"{c}={far_dist[c]:.3f}" for c in cats))

    # Chi-squared test
    contingency = {
        'near': Counter({c: near_suffixes.get(c, 0) for c in cats}),
        'far': Counter({c: far_suffixes.get(c, 0) for c in cats}),
    }
    chi2_val, chi2_p, chi2_n = chi2_independence(contingency)
    v = (chi2_val / (chi2_n * (min(len(contingency), len(cats)) - 1))) ** 0.5 if chi2_n > 0 else 0.0

    print(f"  Chi-squared: {chi2_val:.2f}, p={chi2_p:.4f}, V={v:.4f}")

    # Terminal fraction comparison
    near_terminal = near_suffixes.get('terminal', 0) / total_near
    far_terminal = far_suffixes.get('terminal', 0) / total_far
    near_t_list = [1] * near_suffixes.get('terminal', 0) + [0] * (total_near - near_suffixes.get('terminal', 0))
    far_t_list = [1] * far_suffixes.get('terminal', 0) + [0] * (total_far - far_suffixes.get('terminal', 0))
    u_t, z_t, p_t = mann_whitney_u(near_t_list, far_t_list)
    print(f"  Terminal fraction: near={near_terminal:.4f}, far={far_terminal:.4f}, Z={z_t:.3f}, p={p_t:.4f}")

    # PREFIX-controlled comparison
    pfx_controlled_results = {}
    for pfx in sorted(set(list(near_by_pfx.keys()) + list(far_by_pfx.keys()))):
        n_near_pfx = sum(near_by_pfx[pfx].values())
        n_far_pfx = sum(far_by_pfx[pfx].values())
        if n_near_pfx < 20 or n_far_pfx < 20:
            continue
        near_t_pfx = near_by_pfx[pfx].get('terminal', 0) / n_near_pfx
        far_t_pfx = far_by_pfx[pfx].get('terminal', 0) / n_far_pfx
        pfx_controlled_results[pfx] = {
            'n_near': n_near_pfx, 'n_far': n_far_pfx,
            'near_terminal': round(near_t_pfx, 4),
            'far_terminal': round(far_t_pfx, 4),
            'diff': round(near_t_pfx - far_t_pfx, 4),
        }
        print(f"    PREFIX {pfx}: near_term={near_t_pfx:.3f}, "
              f"far_term={far_t_pfx:.3f}, diff={near_t_pfx - far_t_pfx:+.3f}")

    # Verdict
    if chi2_p < 0.01 and v > 0.05:
        verdict = 'COUPLED'
    elif chi2_p > 0.05:
        verdict = 'INDEPENDENT'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T4_dark_suffix',
        'verdict': verdict,
        'n_near': total_near,
        'n_far': total_far,
        'near_profile': {c: round(v, 4) for c, v in near_dist.items()},
        'far_profile': {c: round(v, 4) for c, v in far_dist.items()},
        'chi2': round(chi2_val, 2),
        'chi2_p': round(chi2_p, 4),
        'cramers_v': round(v, 4),
        'near_terminal': round(near_terminal, 4),
        'far_terminal': round(far_terminal, 4),
        'terminal_z': round(z_t, 3),
        'terminal_p': round(p_t, 4),
        'prefix_controlled': pfx_controlled_results,
    }


# ── T5: Dark Removal Genericizes Transitions ───────────────────

def test_t5(data, rng):
    print("\n── T5: Dark Removal Genericizes Transitions ──")
    b_line_tokens = data['b_line_tokens']
    dark_middles = data['dark_middles']
    token_to_class = data['token_to_class']

    # For lines containing dark tokens:
    # 1. Compute bridge transition matrix WITH dark tokens (as gaps)
    # 2. Compute bridge transition matrix WITHOUT dark tokens (closed gaps)
    # 3. Compare entropies

    # "With dark" = classified transitions that have dark tokens between them
    # "Without dark" = after removing dark tokens, same positions become adjacent
    # We need lines that actually have dark tokens between classified tokens

    transitions_with = Counter()      # transitions with dark between
    transitions_without = Counter()   # same transitions after dark removal (next classified)
    transitions_nodark_lines = Counter()  # transitions on lines with no dark at all

    lines_with_dark_transitions = 0

    for key, toks in b_line_tokens.items():
        # Get classified positions
        classified = [(i, tok['class_id']) for i, tok in enumerate(toks)
                      if tok.get('class_id') is not None]
        if len(classified) < 2:
            continue

        # Check if any dark tokens exist on this line
        has_dark = any(tok.get('is_dark') for tok in toks)

        if not has_dark:
            # No dark on line: record transitions for baseline
            for idx in range(len(classified) - 1):
                c_a = classified[idx][1]
                c_b = classified[idx + 1][1]
                transitions_nodark_lines[(c_a, c_b)] += 1
            continue

        # Line has dark tokens
        # For consecutive classified token pairs, check if dark is between
        found_dark_between = False
        for idx in range(len(classified) - 1):
            pos_a, c_a = classified[idx]
            pos_b, c_b = classified[idx + 1]

            # Check for dark tokens between pos_a and pos_b
            dark_between = any(toks[j].get('is_dark')
                               for j in range(pos_a + 1, pos_b))

            if dark_between:
                transitions_with[(c_a, c_b)] += 1
                found_dark_between = True

            # After dark removal, this transition still exists
            transitions_without[(c_a, c_b)] += 1

        if found_dark_between:
            lines_with_dark_transitions += 1

    n_with = sum(transitions_with.values())
    n_without = sum(transitions_without.values())
    n_nodark = sum(transitions_nodark_lines.values())

    print(f"  Lines with dark between classified: {lines_with_dark_transitions}")
    print(f"  Transitions with dark between: {n_with}")
    print(f"  All transitions on dark lines (after removal): {n_without}")
    print(f"  Transitions on no-dark lines: {n_nodark}")

    if n_with < 50:
        print("  Too few dark-between transitions")
        return {'test': 'T5_removal', 'verdict': 'INSUFFICIENT_DATA',
                'n_dark_between': n_with}

    # Entropy comparison
    h_with = entropy_from_counts(transitions_with)
    h_without = entropy_from_counts(transitions_without)
    h_nodark = entropy_from_counts(transitions_nodark_lines)

    print(f"  Entropy of dark-between transitions: {h_with:.4f} bits")
    print(f"  Entropy of all transitions on dark lines: {h_without:.4f} bits")
    print(f"  Entropy of no-dark line transitions: {h_nodark:.4f} bits")

    # The key comparison: are dark-between transitions more constrained (lower entropy)
    # than no-dark transitions?
    # Also: compute conditional entropy (per source class)

    def per_class_entropy(trans_counts):
        """Average entropy of next-class distribution per source class."""
        by_source = defaultdict(Counter)
        for (c_a, c_b), cnt in trans_counts.items():
            by_source[c_a][c_b] += cnt
        total = sum(trans_counts.values())
        weighted_h = 0.0
        for c_a, next_dist in by_source.items():
            n = sum(next_dist.values())
            h = entropy_from_counts(next_dist)
            weighted_h += h * n / total
        return weighted_h

    h_cond_with = per_class_entropy(transitions_with)
    h_cond_nodark = per_class_entropy(transitions_nodark_lines)

    print(f"  Conditional entropy (per source): dark-between={h_cond_with:.4f}, "
          f"no-dark={h_cond_nodark:.4f}")
    entropy_diff = h_cond_nodark - h_cond_with
    print(f"  Difference (no-dark minus dark-between): {entropy_diff:+.4f} bits")

    # Permutation null: shuffle "dark-between" labels among all transitions
    # on dark lines (preserving total count)
    all_dark_line_transitions = list(transitions_without.elements())
    n_dark_between = n_with

    null_diffs = []
    for _ in range(N_PERM):
        # Sample n_dark_between transitions from all dark-line transitions
        if len(all_dark_line_transitions) <= n_dark_between:
            perm_sample = all_dark_line_transitions
        else:
            perm_sample = rng.sample(all_dark_line_transitions, n_dark_between)
        perm_counts = Counter(perm_sample)
        perm_h = per_class_entropy(perm_counts)
        null_diffs.append(h_cond_nodark - perm_h)

    null_mean_diff = sum(null_diffs) / len(null_diffs) if null_diffs else 0.0
    perm_p = (sum(1 for nd in null_diffs if nd >= entropy_diff) / len(null_diffs)
              if null_diffs else 1.0)

    print(f"  Null mean diff: {null_mean_diff:.4f}, perm_p={perm_p:.4f}")

    # Verdict
    if entropy_diff > 0 and perm_p < 0.01:
        verdict = 'CONTEXT_SETTING'
    elif abs(entropy_diff) < 0.1 or perm_p > 0.05:
        verdict = 'INERT'
    else:
        verdict = 'MIXED'

    print(f"  Verdict: {verdict}")

    return {
        'test': 'T5_removal',
        'verdict': verdict,
        'n_dark_between': n_with,
        'n_dark_line_transitions': n_without,
        'n_nodark_transitions': n_nodark,
        'h_dark_between': round(h_with, 4),
        'h_dark_line_all': round(h_without, 4),
        'h_nodark_lines': round(h_nodark, 4),
        'h_cond_dark_between': round(h_cond_with, 4),
        'h_cond_nodark': round(h_cond_nodark, 4),
        'entropy_diff': round(entropy_diff, 4),
        'null_mean_diff': round(null_mean_diff, 4),
        'perm_p': round(perm_p, 4),
    }


# ── Main ────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("Phase 473: LAYERED_GRAMMAR_TEST")
    print("=" * 60)

    print("\nLoading data...")
    data = build_data()
    print(f"  Dark MIDDLEs: {len(data['dark_middles'])}")
    print(f"  Bridge MIDDLEs: {len(data['bridge_middles'])}")
    print(f"  49-class types: {len(data['token_to_class'])}")
    print(f"  B lines: {len(data['b_line_tokens'])}")

    results = {}

    # Gate tests
    results['T1'] = test_t1(data, rng)
    results['T2'] = test_t2(data, rng)

    gate1 = results['T1']['verdict'] in ('GATE_OPEN', 'GATE_MARGINAL')
    gate2 = results['T2']['verdict'] in ('GATE_OPEN', 'GATE_MARGINAL')
    gates_pass = gate1 and gate2

    print(f"\n  GATE STATUS: T1={'PASS' if gate1 else 'FAIL'}, "
          f"T2={'PASS' if gate2 else 'FAIL'} → "
          f"{'PROCEED' if gates_pass else 'CORE TESTS MOOT'}")

    # Core tests (run regardless, but interpretation depends on gates)
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
        gate_label = ' (GATE)' if key in ('T1', 'T2') else ''
        print(f"  {key}{gate_label}: {v}")

    print(f"\n  Gates: {'BOTH PASS' if gates_pass else 'BLOCKED'}")

    # Overall interpretation
    if not gates_pass:
        overall = 'GATES_BLOCKED'
    else:
        core_support = sum(1 for k in ['T3', 'T4', 'T5']
                           if verdicts[k] in ('CONDITIONED', 'COUPLED', 'CONTEXT_SETTING'))
        if core_support >= 2:
            overall = 'THREE_TIER_CONFIRMED'
        elif core_support == 1:
            overall = 'THREE_TIER_PARTIAL'
        else:
            overall = 'BINARY_PRESERVED'

    print(f"  Overall: {overall}")

    results['meta'] = {
        'phase': 473,
        'name': 'LAYERED_GRAMMAR_TEST',
        'n_dark': len(data['dark_middles']),
        'n_bridge': len(data['bridge_middles']),
        'n_class_types': len(data['token_to_class']),
        'n_perm': N_PERM,
        'seed': SEED,
        'runtime_s': round(dt, 1),
        'gates_pass': gates_pass,
        'verdicts': verdicts,
        'overall': overall,
    }

    out_path = RESULTS_DIR / "layered_grammar_test.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")
    print(f"Runtime: {dt:.1f}s")


if __name__ == '__main__':
    main()

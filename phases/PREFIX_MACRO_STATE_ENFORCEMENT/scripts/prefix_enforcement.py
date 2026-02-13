"""
Phase 330: PREFIX_MACRO_STATE_ENFORCEMENT
=========================================
Test whether the 102 forbidden PREFIX × MIDDLE combinations (C911) enforce
the 6-state macro-automaton's transition topology at the token level.

Mechanism: PREFIX + MIDDLE -> token -> class (1-49) -> macro-state (1-6)
Question: Do prohibitions disproportionately target cross-state combinations?
"""

import json
import sys
import time
import numpy as np
from pathlib import Path
from collections import defaultdict

# Add project root to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

# ── Macro-state partition (C976/C1010) ────────────────────────────────
MACRO_STATE_PARTITION = {
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'AXm':     {3, 5, 18, 19, 42, 45},
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}

# Build class -> macro-state lookup
CLASS_TO_MACRO = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = state

# Depleted pairs (forbidden transitions) — from BCSC C109
DEPLETED_PAIRS = [
    (11, 36), (13, 40), (9, 33), (24, 30), (14, 46), (9, 27),
    (9, 32), (5, 34), (47, 11), (19, 33), (7, 32), (11, 14),
    (3, 33), (33, 38), (18, 28), (7, 47), (13, 5), (10, 28),
]


def load_data():
    """Load all precomputed data files."""
    results = {}

    # 1. 102 forbidden PREFIX × MIDDLE pairs
    path = ROOT / 'phases' / 'MIDDLE_SEMANTIC_DEEPENING' / 'results' / 'prefix_middle_interaction.json'
    with open(path) as f:
        data = json.load(f)
    results['forbidden_pairs'] = [(p['prefix'], p['middle']) for p in data['forbidden_pairs']]

    # 2. Token -> class mapping
    path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    results['token_to_class'] = {k: int(v) for k, v in data['token_to_class'].items()}
    results['class_to_role'] = {int(k): v for k, v in data['class_to_role'].items()}
    results['class_to_middles'] = {int(k): v for k, v in data['class_to_middles'].items()}

    # 3. Build MIDDLE -> classes lookup from class_to_middles
    middle_to_classes = defaultdict(set)
    for cls, middles in results['class_to_middles'].items():
        for m in middles:
            middle_to_classes[m].add(cls)
    results['middle_to_classes'] = dict(middle_to_classes)

    return results


def build_token_table(data):
    """Single pass over B tokens to build PREFIX × class × macro-state table."""
    tx = Transcript()
    morph = Morphology()
    token_to_class = data['token_to_class']

    records = []  # (prefix_str, class_id, macro_state, line_pos_norm)
    prefix_counts = defaultdict(lambda: defaultdict(int))  # prefix -> macro_state -> count
    prefix_total = defaultdict(int)
    unmapped = 0

    for token in tx.currier_b():
        word = token.word
        if not word.strip() or '*' in word:
            continue

        cls = token_to_class.get(word)
        if cls is None:
            unmapped += 1
            continue

        macro = CLASS_TO_MACRO.get(cls)
        if macro is None:
            continue

        m = morph.extract(word)
        prefix_str = m.prefix if m.prefix else '(none)'

        # Compute normalized line position
        line_tokens = token.line_tokens if hasattr(token, 'line_tokens') else None
        line_pos = token.line_position if hasattr(token, 'line_position') else None

        records.append({
            'prefix': prefix_str,
            'class': cls,
            'macro': macro,
            'middle': m.middle,
            'folio': token.folio,
            'line': token.line,
        })

        prefix_counts[prefix_str][macro] += 1
        prefix_total[prefix_str] += 1

    return records, dict(prefix_counts), dict(prefix_total), unmapped


def compute_line_positions(records):
    """Compute normalized line positions for T4."""
    # Group by folio+line
    line_groups = defaultdict(list)
    for i, rec in enumerate(records):
        key = (rec['folio'], rec['line'])
        line_groups[key].append(i)

    # Assign normalized positions
    positions = np.zeros(len(records))
    for key, indices in line_groups.items():
        n = len(indices)
        for rank, idx in enumerate(indices):
            positions[idx] = rank / max(n - 1, 1)

    return positions


def run_t1(records, prefix_counts, prefix_total):
    """T1: PREFIX Macro-State Selectivity."""
    print("\n=== T1: PREFIX Macro-State Selectivity ===")

    macro_states = sorted(MACRO_STATE_PARTITION.keys())
    n_states = len(macro_states)
    max_entropy = np.log2(n_states)

    # Build contingency table
    prefixes = sorted(prefix_counts.keys())
    contingency = np.zeros((len(prefixes), n_states), dtype=int)
    for i, pfx in enumerate(prefixes):
        for j, state in enumerate(macro_states):
            contingency[i, j] = prefix_counts[pfx].get(state, 0)

    # Per-PREFIX entropy
    prefix_entropies = {}
    prefix_concentrations = {}
    for i, pfx in enumerate(prefixes):
        row = contingency[i]
        total = row.sum()
        if total == 0:
            continue
        probs = row / total
        probs = probs[probs > 0]
        ent = -np.sum(probs * np.log2(probs))
        prefix_entropies[pfx] = float(ent)
        prefix_concentrations[pfx] = float(row.max() / total)

    # Weighted mean entropy
    weights = np.array([prefix_total.get(pfx, 0) for pfx in prefix_entropies])
    ents = np.array(list(prefix_entropies.values()))
    weighted_mean_entropy = float(np.average(ents, weights=weights))
    entropy_reduction = float(1 - weighted_mean_entropy / max_entropy)

    # Chi-square test
    from scipy.stats import chi2_contingency
    # Filter to prefixes with > 0 tokens
    mask = contingency.sum(axis=1) > 0
    chi2, p_chi2, dof, _ = chi2_contingency(contingency[mask])

    # Permutation null
    n_tokens = len(records)
    macro_arr = np.array([macro_states.index(r['macro']) for r in records])
    prefix_arr = np.array([r['prefix'] for r in records])

    rng = np.random.default_rng(42)
    null_entropy_reductions = []
    for _ in range(1000):
        perm_macro = rng.permutation(macro_arr)
        # Compute weighted mean entropy under permutation
        perm_counts = defaultdict(lambda: np.zeros(n_states, dtype=int))
        for pfx, ms in zip(prefix_arr, perm_macro):
            perm_counts[pfx][ms] += 1

        perm_ents = []
        perm_weights = []
        for pfx, row in perm_counts.items():
            total = row.sum()
            if total == 0:
                continue
            probs = row / total
            probs_pos = probs[probs > 0]
            ent = -np.sum(probs_pos * np.log2(probs_pos))
            perm_ents.append(ent)
            perm_weights.append(total)

        perm_ents = np.array(perm_ents)
        perm_weights = np.array(perm_weights)
        perm_mean = float(np.average(perm_ents, weights=perm_weights))
        null_entropy_reductions.append(1 - perm_mean / max_entropy)

    null_mean = float(np.mean(null_entropy_reductions))
    null_std = float(np.std(null_entropy_reductions))
    z_score = (entropy_reduction - null_mean) / null_std if null_std > 0 else 0
    p_perm = float(np.mean(np.array(null_entropy_reductions) >= entropy_reduction))

    print(f"  Weighted mean entropy: {weighted_mean_entropy:.3f} / {max_entropy:.3f}")
    print(f"  Entropy reduction: {entropy_reduction:.3f} ({entropy_reduction*100:.1f}%)")
    print(f"  Chi-square: {chi2:.1f}, p={p_chi2:.2e}")
    print(f"  Permutation z={z_score:.2f}, p={p_perm:.4f}")

    # Top PREFIX concentrations
    top_pfx = sorted(prefix_concentrations.items(), key=lambda x: -x[1])[:10]
    print(f"  Top PREFIX concentrations:")
    for pfx, conc in top_pfx:
        modal = max(prefix_counts[pfx].items(), key=lambda x: x[1])
        print(f"    {pfx:>8}: {conc:.3f} -> {modal[0]} (n={prefix_total[pfx]})")

    return {
        'weighted_mean_entropy': weighted_mean_entropy,
        'max_entropy': float(max_entropy),
        'entropy_reduction': entropy_reduction,
        'chi2': float(chi2),
        'chi2_p': float(p_chi2),
        'chi2_dof': int(dof),
        'perm_z': z_score,
        'perm_p': p_perm,
        'null_mean': null_mean,
        'null_std': null_std,
        'n_prefixes': len(prefix_entropies),
        'per_prefix_entropy': prefix_entropies,
        'per_prefix_concentration': prefix_concentrations,
    }


def run_t2(records, prefix_counts, prefix_total, data):
    """T2: Cross-State Prohibition Targeting."""
    print("\n=== T2: Cross-State Prohibition Targeting ===")

    forbidden = data['forbidden_pairs']
    middle_to_classes = data['middle_to_classes']

    # PREFIX "home" macro-state = modal macro-state
    prefix_home = {}
    for pfx, state_counts in prefix_counts.items():
        if state_counts:
            prefix_home[pfx] = max(state_counts.items(), key=lambda x: x[1])[0]

    # Classify each prohibition
    classifications = []
    for pfx, mid in forbidden:
        home = prefix_home.get(pfx)
        if home is None:
            classifications.append({'prefix': pfx, 'middle': mid, 'type': 'UNMAPPED_PREFIX'})
            continue

        mid_classes = middle_to_classes.get(mid, set())
        if not mid_classes:
            classifications.append({'prefix': pfx, 'middle': mid, 'type': 'UNMAPPED_MIDDLE'})
            continue

        mid_macros = {CLASS_TO_MACRO[c] for c in mid_classes if c in CLASS_TO_MACRO}
        if not mid_macros:
            classifications.append({'prefix': pfx, 'middle': mid, 'type': 'UNMAPPED_MACRO'})
            continue

        if home not in mid_macros:
            ctype = 'CROSS_STATE'
        elif mid_macros == {home}:
            ctype = 'WITHIN_STATE'
        else:
            ctype = 'MIXED'

        classifications.append({
            'prefix': pfx,
            'middle': mid,
            'type': ctype,
            'prefix_home': home,
            'middle_macros': sorted(mid_macros),
        })

    # Count
    type_counts = defaultdict(int)
    for c in classifications:
        type_counts[c['type']] += 1

    n_classifiable = sum(1 for c in classifications if c['type'] in ('CROSS_STATE', 'WITHIN_STATE', 'MIXED'))
    n_cross = type_counts.get('CROSS_STATE', 0)
    n_within = type_counts.get('WITHIN_STATE', 0)
    n_mixed = type_counts.get('MIXED', 0)
    cross_fraction = n_cross / n_classifiable if n_classifiable > 0 else 0

    # Permutation null: randomly reassign 102 prohibitions among eligible PREFIX × MIDDLE pairs
    # Build set of all pairs with expected >= 5 (approximate using prefix_total and middle frequencies)
    # For the null, we permute which (PREFIX, MIDDLE) pairs are forbidden
    # Simpler approach: for each forbidden pair, randomly reassign the MIDDLE while keeping PREFIX fixed
    rng = np.random.default_rng(42)

    # Get list of all MIDDLEs that appear in the forbidden set
    all_middles_in_data = list(middle_to_classes.keys())

    null_cross_fractions = []
    for _ in range(1000):
        perm_n_cross = 0
        perm_n_classifiable = 0
        for pfx, mid in forbidden:
            home = prefix_home.get(pfx)
            if home is None:
                continue
            # Pick a random MIDDLE from the known MIDDLEs
            rand_mid = rng.choice(all_middles_in_data)
            rand_classes = middle_to_classes.get(rand_mid, set())
            if not rand_classes:
                continue
            rand_macros = {CLASS_TO_MACRO[c] for c in rand_classes if c in CLASS_TO_MACRO}
            if not rand_macros:
                continue
            perm_n_classifiable += 1
            if home not in rand_macros:
                perm_n_cross += 1

        if perm_n_classifiable > 0:
            null_cross_fractions.append(perm_n_cross / perm_n_classifiable)

    null_mean = float(np.mean(null_cross_fractions))
    null_std = float(np.std(null_cross_fractions))
    z_score = (cross_fraction - null_mean) / null_std if null_std > 0 else 0
    p_perm = float(np.mean(np.array(null_cross_fractions) >= cross_fraction))

    print(f"  Total prohibitions: {len(forbidden)}")
    print(f"  Classifiable: {n_classifiable}")
    print(f"  CROSS_STATE: {n_cross} ({cross_fraction:.3f})")
    print(f"  WITHIN_STATE: {n_within}")
    print(f"  MIXED: {n_mixed}")
    print(f"  Unmapped: {type_counts.get('UNMAPPED_PREFIX', 0) + type_counts.get('UNMAPPED_MIDDLE', 0) + type_counts.get('UNMAPPED_MACRO', 0)}")
    print(f"  Null cross fraction: {null_mean:.3f} ± {null_std:.3f}")
    print(f"  z={z_score:.2f}, p={p_perm:.4f}")

    return {
        'n_forbidden': len(forbidden),
        'n_classifiable': n_classifiable,
        'n_cross_state': n_cross,
        'n_within_state': n_within,
        'n_mixed': n_mixed,
        'cross_state_fraction': float(cross_fraction),
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'p_perm': p_perm,
        'type_counts': dict(type_counts),
        'classifications': classifications,
    }


def run_t3(records, prefix_counts, data):
    """T3: Forbidden Transition Coverage."""
    print("\n=== T3: Forbidden Transition Coverage ===")

    forbidden_pairs_set = set(data['forbidden_pairs'])
    middle_to_classes = data['middle_to_classes']
    class_to_middles = data['class_to_middles']

    # Build PREFIX -> set of observed classes
    prefix_to_classes = defaultdict(set)
    for rec in records:
        prefix_to_classes[rec['prefix']].add(rec['class'])

    # For each depleted pair (class_i, class_j), check morphological backing
    def has_prohibition_backing(ci, cj):
        """Check if any PREFIX used with class_i has a forbidden pair with a MIDDLE of class_j."""
        prefixes_for_ci = set()
        for pfx, classes in prefix_to_classes.items():
            if ci in classes:
                prefixes_for_ci.add(pfx)

        middles_for_cj = set(class_to_middles.get(cj, []))

        for pfx in prefixes_for_ci:
            for mid in middles_for_cj:
                if (pfx, mid) in forbidden_pairs_set:
                    return True, pfx, mid
        return False, None, None

    # Check forbidden transitions
    forbidden_backed = 0
    forbidden_details = []
    for ci, cj in DEPLETED_PAIRS:
        backed, pfx, mid = has_prohibition_backing(ci, cj)
        # Also check reverse
        backed_rev, pfx_rev, mid_rev = has_prohibition_backing(cj, ci)
        either_backed = backed or backed_rev
        if either_backed:
            forbidden_backed += 1
        forbidden_details.append({
            'class_i': ci,
            'class_j': cj,
            'macro_i': CLASS_TO_MACRO.get(ci),
            'macro_j': CLASS_TO_MACRO.get(cj),
            'forward_backed': backed,
            'forward_prefix': pfx,
            'forward_middle': mid,
            'reverse_backed': backed_rev,
            'reverse_prefix': pfx_rev,
            'reverse_middle': mid_rev,
            'either_backed': either_backed,
        })

    forbidden_coverage = forbidden_backed / len(DEPLETED_PAIRS)

    # Null: random sets of class pairs from ALLOWED transitions
    all_classes = sorted(CLASS_TO_MACRO.keys())
    depleted_set = set((min(a, b), max(a, b)) for a, b in DEPLETED_PAIRS)

    # Build allowed pairs (all cross-class pairs minus depleted)
    allowed_pairs = []
    for i in range(len(all_classes)):
        for j in range(i + 1, len(all_classes)):
            ci, cj = all_classes[i], all_classes[j]
            if (ci, cj) not in depleted_set:
                allowed_pairs.append((ci, cj))

    rng = np.random.default_rng(42)
    null_coverages = []
    n_depleted = len(DEPLETED_PAIRS)
    for _ in range(1000):
        sample = rng.choice(len(allowed_pairs), size=min(n_depleted, len(allowed_pairs)), replace=False)
        sample_pairs = [allowed_pairs[s] for s in sample]
        n_backed = 0
        for ci, cj in sample_pairs:
            b1, _, _ = has_prohibition_backing(ci, cj)
            b2, _, _ = has_prohibition_backing(cj, ci)
            if b1 or b2:
                n_backed += 1
        null_coverages.append(n_backed / len(sample_pairs))

    null_mean = float(np.mean(null_coverages))
    null_std = float(np.std(null_coverages))
    z_score = (forbidden_coverage - null_mean) / null_std if null_std > 0 else 0
    p_perm = float(np.mean(np.array(null_coverages) >= forbidden_coverage))

    print(f"  Depleted pairs: {len(DEPLETED_PAIRS)}")
    print(f"  Morphologically backed: {forbidden_backed} ({forbidden_coverage:.3f})")
    print(f"  Null coverage: {null_mean:.3f} ± {null_std:.3f}")
    print(f"  z={z_score:.2f}, p={p_perm:.4f}")
    print(f"  Details:")
    for d in forbidden_details:
        backed_str = "BACKED" if d['either_backed'] else "not backed"
        print(f"    ({d['class_i']},{d['class_j']}) {d['macro_i']}->{d['macro_j']}: {backed_str}")

    return {
        'n_depleted': len(DEPLETED_PAIRS),
        'n_backed': forbidden_backed,
        'forbidden_coverage': float(forbidden_coverage),
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'p_perm': p_perm,
        'details': forbidden_details,
    }


def run_t4(records, prefix_counts, prefix_total):
    """T4: Positional Mediation."""
    print("\n=== T4: Positional Mediation ===")

    # Compute line positions
    positions = compute_line_positions(records)

    # Assign quartiles
    quartile_edges = [0, 0.25, 0.5, 0.75, 1.01]
    quartiles = np.digitize(positions, quartile_edges) - 1  # 0-3
    quartiles = np.clip(quartiles, 0, 3)

    macro_states = sorted(MACRO_STATE_PARTITION.keys())
    macro_arr = np.array([macro_states.index(r['macro']) for r in records])
    prefix_arr = np.array([r['prefix'] for r in records])

    n_q = 4
    n_s = len(macro_states)

    # I(position; macro-state)
    def compute_mi(x, y, nx, ny):
        """Compute mutual information between categorical x and y."""
        joint = np.zeros((nx, ny), dtype=float)
        for xi, yi in zip(x, y):
            joint[xi, yi] += 1
        joint /= joint.sum()

        mx = joint.sum(axis=1)
        my = joint.sum(axis=0)

        mi = 0.0
        for i in range(nx):
            for j in range(ny):
                if joint[i, j] > 0 and mx[i] > 0 and my[j] > 0:
                    mi += joint[i, j] * np.log2(joint[i, j] / (mx[i] * my[j]))
        return mi

    mi_pos_macro = compute_mi(quartiles, macro_arr, n_q, n_s)

    # I(position; macro-state | PREFIX) = sum_pfx P(pfx) * I(pos; macro | pfx)
    unique_prefixes = sorted(set(prefix_arr))
    prefix_indices = {p: i for i, p in enumerate(unique_prefixes)}
    prefix_int_arr = np.array([prefix_indices[p] for p in prefix_arr])

    conditional_mi = 0.0
    n_total = len(records)
    for pfx in unique_prefixes:
        mask = prefix_arr == pfx
        n_pfx = mask.sum()
        if n_pfx < 10:
            continue
        p_pfx = n_pfx / n_total
        mi_given_pfx = compute_mi(quartiles[mask], macro_arr[mask], n_q, n_s)
        conditional_mi += p_pfx * mi_given_pfx

    mediation_fraction = 1.0 - conditional_mi / mi_pos_macro if mi_pos_macro > 0 else 0.0

    # I(PREFIX; macro-state)
    mi_pfx_macro = compute_mi(prefix_int_arr, macro_arr, len(unique_prefixes), n_s)

    # Per-quartile macro-state distributions
    quartile_distributions = {}
    for q in range(4):
        mask = quartiles == q
        dist = {}
        for s_idx, state in enumerate(macro_states):
            dist[state] = int((macro_arr[mask] == s_idx).sum())
        quartile_distributions[f'Q{q+1}'] = dist

    # Permutation null for MI
    rng = np.random.default_rng(42)
    null_mis = []
    for _ in range(1000):
        perm_q = rng.permutation(quartiles)
        null_mis.append(compute_mi(perm_q, macro_arr, n_q, n_s))

    null_mean = float(np.mean(null_mis))
    null_std = float(np.std(null_mis))
    z_mi = (mi_pos_macro - null_mean) / null_std if null_std > 0 else 0
    p_mi = float(np.mean(np.array(null_mis) >= mi_pos_macro))

    print(f"  I(position; macro-state) = {mi_pos_macro:.4f} bits")
    print(f"  I(position; macro-state | PREFIX) = {conditional_mi:.4f} bits")
    print(f"  I(PREFIX; macro-state) = {mi_pfx_macro:.4f} bits")
    print(f"  Mediation fraction: {mediation_fraction:.3f} ({mediation_fraction*100:.1f}%)")
    print(f"  MI null: {null_mean:.4f} ± {null_std:.4f}, z={z_mi:.2f}, p={p_mi:.4f}")
    print(f"  Per-quartile distributions:")
    for q_name, dist in quartile_distributions.items():
        total = sum(dist.values())
        top = max(dist.items(), key=lambda x: x[1])
        print(f"    {q_name}: n={total}, modal={top[0]} ({top[1]/total*100:.1f}%)")

    return {
        'mi_position_macro': float(mi_pos_macro),
        'mi_position_macro_given_prefix': float(conditional_mi),
        'mi_prefix_macro': float(mi_pfx_macro),
        'mediation_fraction': float(mediation_fraction),
        'mi_null_mean': null_mean,
        'mi_null_std': null_std,
        'mi_z': z_mi,
        'mi_p': p_mi,
        'quartile_distributions': quartile_distributions,
    }


def run_t5(t1, t2, t3, t4, prefix_counts, prefix_total):
    """T5: Synthesis — evaluate pre-registered predictions."""
    print("\n=== T5: Synthesis ===")

    macro_states = sorted(MACRO_STATE_PARTITION.keys())

    # P1: PREFIX predicts macro-state (entropy reduction > 10%)
    p1_pass = t1['entropy_reduction'] > 0.10 and t1['chi2_p'] < 0.001
    print(f"  P1 (PREFIX selectivity > 10%): entropy_reduction={t1['entropy_reduction']:.3f} -> {'PASS' if p1_pass else 'FAIL'}")

    # P2: >60% of prohibitions are cross-state
    p2_pass = t2['cross_state_fraction'] > 0.60
    print(f"  P2 (>60% cross-state): fraction={t2['cross_state_fraction']:.3f} -> {'PASS' if p2_pass else 'FAIL'}")

    # P3: Forbidden coverage > allowed (ratio > 1.5)
    ratio = t3['forbidden_coverage'] / t3['null_mean'] if t3['null_mean'] > 0 else float('inf')
    p3_pass = ratio > 1.5 and t3['p_perm'] < 0.05
    print(f"  P3 (forbidden coverage ratio > 1.5): ratio={ratio:.2f}, p={t3['p_perm']:.4f} -> {'PASS' if p3_pass else 'FAIL'}")

    # P4: Position predicts macro-state, >50% mediated by PREFIX
    p4_pass = t4['mi_p'] < 0.001 and t4['mediation_fraction'] > 0.50
    print(f"  P4 (positional mediation > 50%): mediation={t4['mediation_fraction']:.3f}, mi_p={t4['mi_p']:.4f} -> {'PASS' if p4_pass else 'FAIL'}")

    # P5: EN PREFIXes (ch, sh) channel >90% to AXM+AXm
    en_prefixes = ['ch', 'sh']
    en_axm_total = 0
    en_total = 0
    for pfx in en_prefixes:
        counts = prefix_counts.get(pfx, {})
        for state, count in counts.items():
            en_total += count
            if state in ('AXM', 'AXm'):
                en_axm_total += count
    en_concentration = en_axm_total / en_total if en_total > 0 else 0
    p5_pass = en_concentration > 0.90
    print(f"  P5 (EN PREFIX -> AXM+AXm > 90%): fraction={en_concentration:.3f} -> {'PASS' if p5_pass else 'FAIL'}")

    # P6: FL_HAZ and CC prohibitions over-represented (enrichment > 2x)
    # Count prohibitions whose MIDDLE maps to FL_HAZ or CC classes
    middle_to_classes = {}
    for cls, middles in data_global['class_to_middles'].items():
        for m in middles:
            if m not in middle_to_classes:
                middle_to_classes[m] = set()
            middle_to_classes[m].add(cls)

    fl_haz_cc_classes = MACRO_STATE_PARTITION['FL_HAZ'] | MACRO_STATE_PARTITION['CC']
    fl_haz_cc_token_share = (
        sum(prefix_counts.get(pfx, {}).get('FL_HAZ', 0) + prefix_counts.get(pfx, {}).get('CC', 0)
            for pfx in prefix_counts)
    ) / sum(prefix_total.values())

    n_fl_cc_prohibitions = 0
    for pfx, mid in data_global['forbidden_pairs']:
        mid_classes = middle_to_classes.get(mid, set())
        mid_macros = {CLASS_TO_MACRO.get(c) for c in mid_classes} - {None}
        if mid_macros & {'FL_HAZ', 'CC'}:
            n_fl_cc_prohibitions += 1

    fl_cc_prohibition_share = n_fl_cc_prohibitions / len(data_global['forbidden_pairs'])
    enrichment = fl_cc_prohibition_share / fl_haz_cc_token_share if fl_haz_cc_token_share > 0 else 0
    p6_pass = enrichment > 2.0
    print(f"  P6 (FL_HAZ+CC enrichment > 2x): enrichment={enrichment:.2f} -> {'PASS' if p6_pass else 'FAIL'}")

    predictions = {
        'P1_selectivity': {'value': t1['entropy_reduction'], 'threshold': 0.10, 'pass': p1_pass},
        'P2_cross_state': {'value': t2['cross_state_fraction'], 'threshold': 0.60, 'pass': p2_pass},
        'P3_forbidden_coverage': {'ratio': ratio, 'p': t3['p_perm'], 'pass': p3_pass},
        'P4_mediation': {'mediation': t4['mediation_fraction'], 'mi_p': t4['mi_p'], 'pass': p4_pass},
        'P5_en_channeling': {'value': en_concentration, 'threshold': 0.90, 'pass': p5_pass},
        'P6_fl_cc_enrichment': {'enrichment': enrichment, 'threshold': 2.0, 'pass': p6_pass},
    }

    n_pass = sum(1 for p in predictions.values() if p['pass'])

    # Verdict
    if n_pass >= 5 and p2_pass and p3_pass:
        verdict = 'MORPHOLOGICAL_ENFORCEMENT'
    elif 3 <= n_pass <= 4:
        verdict = 'PARTIAL_ENFORCEMENT'
    elif p1_pass and not p2_pass and not p3_pass:
        verdict = 'SELECTIVITY_WITHOUT_ENFORCEMENT'
    else:
        verdict = 'INDEPENDENT_LAYERS'

    print(f"\n  Predictions: {n_pass}/6 passed")
    print(f"\n  *** VERDICT: {verdict} ***")

    return {
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': 6,
        'verdict': verdict,
    }


if __name__ == '__main__':
    t0 = time.time()

    print("Phase 330: PREFIX_MACRO_STATE_ENFORCEMENT")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    data_global = load_data()

    # Build token table
    print("Building token table from B corpus...")
    records, prefix_counts, prefix_total, unmapped = build_token_table(data_global)
    print(f"  Mapped: {len(records)}, Unmapped: {unmapped}")

    # Run tests
    t1 = run_t1(records, prefix_counts, prefix_total)
    t2 = run_t2(records, prefix_counts, prefix_total, data_global)
    t3 = run_t3(records, prefix_counts, data_global)
    t4 = run_t4(records, prefix_counts, prefix_total)
    t5 = run_t5(t1, t2, t3, t4, prefix_counts, prefix_total)

    elapsed = time.time() - t0

    # Save results
    results = {
        'phase': 'PREFIX_MACRO_STATE_ENFORCEMENT',
        'phase_number': 330,
        'question': 'Do the 102 forbidden PREFIX × MIDDLE combinations enforce the 6-state macro-automaton topology?',
        'n_tokens_mapped': len(records),
        'n_tokens_unmapped': unmapped,
        't1_selectivity': t1,
        't2_cross_state': {k: v for k, v in t2.items() if k != 'classifications'},
        't2_classifications': t2['classifications'],
        't3_forbidden_coverage': {k: v for k, v in t3.items() if k != 'details'},
        't3_details': t3['details'],
        't4_positional_mediation': t4,
        't5_synthesis': t5,
        'elapsed_seconds': round(elapsed, 1),
    }

    out_path = ROOT / 'phases' / 'PREFIX_MACRO_STATE_ENFORCEMENT' / 'results' / 'prefix_enforcement.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")

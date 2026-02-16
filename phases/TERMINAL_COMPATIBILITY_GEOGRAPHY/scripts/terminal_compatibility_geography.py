#!/usr/bin/env python3
"""
Phase 382: Terminal Compatibility Geography

5-test battery examining WHY terminal characters predict C475 compatibility.
Cross-references terminal neighborhoods with role (C591), macro-state (C976),
affordance bins (C995), and HUB sub-roles (C1000).

T1: Terminal-Character Neighborhood Role Composition
T2: Terminal-Character x Macro-State Correspondence
T3: INITIAL vs FINAL Terminal Asymmetry Mechanism
T4: Terminal Neighborhood x Affordance Bin Alignment
T5: Terminal Neighborhood Transitivity Test

All Tier 2 targets. Expert-advisor validated.
"""

import sys
import json
import functools
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy.stats import chi2_contingency, fisher_exact

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS = ROOT / "phases" / "TERMINAL_COMPATIBILITY_GEOGRAPHY" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table."""
    table = np.array(contingency_table)
    if table.sum() == 0:
        return 0.0
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    r, k = table.shape
    return float(np.sqrt(chi2 / (n * (min(r, k) - 1)))) if min(r, k) > 1 else 0.0


def save_result(data, filename):
    """Save result JSON."""
    path = RESULTS / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved: {path}")


def clean_table(table):
    """Remove zero-sum rows and columns from a contingency table."""
    t = np.array(table)
    row_mask = t.sum(axis=1) > 0
    col_mask = t.sum(axis=0) > 0
    return t[row_mask][:, col_mask]


# ============================================================
# DATA LOADING
# ============================================================

def reconstruct_middle_list():
    """Reconstruct the 972-element MIDDLE ordering matching t1_compat_matrix.npy."""
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    return all_middles, mid_to_idx


def load_data():
    """Load all shared data for the 5-test battery."""
    morph = Morphology()

    # 1. Compatibility matrix (972x972)
    compat_path = ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    compat_matrix = np.load(compat_path)
    all_middles, mid_to_idx = reconstruct_middle_list()
    print(f"  Compatibility matrix: {compat_matrix.shape}, MIDDLEs: {len(all_middles)}")

    # 2. Affordance table (per-MIDDLE) — MIDDLEs nested under 'middles' key
    aff_path = ROOT / 'data' / 'middle_affordance_table.json'
    with open(aff_path, 'r', encoding='utf-8') as f:
        aff_raw = json.load(f)
    affordance_table = aff_raw['middles']  # {middle_name: {affordance_bin, token_frequency, ...}}
    aff_metadata = aff_raw.get('_metadata', {})
    print(f"  Affordance table: {len(affordance_table)} MIDDLEs")

    # 3. HUB sub-roles (23 MIDDLEs)
    hub_path = ROOT / 'phases' / 'HUB_ROLE_DECOMPOSITION' / 'results' / 't1_hub_sub_role_partition.json'
    with open(hub_path, 'r', encoding='utf-8') as f:
        hub_data = json.load(f)
    print(f"  HUB sub-roles: {hub_data['hub_middles']} MIDDLEs")

    # 4. Token-to-class map
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm_data = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm_data['token_to_class'].items()}
    print(f"  Token-to-class: {len(token_to_class)} mappings")

    # 5. Role census (C591) -> class_to_role
    role_path = ROOT / 'phases' / 'SMALL_ROLE_ANATOMY' / 'results' / 'sr_census.json'
    with open(role_path, 'r', encoding='utf-8') as f:
        role_data = json.load(f)
    class_to_role = {}
    for role_name, info in role_data['resolved_roles'].items():
        for cls_id in info['classes']:
            class_to_role[cls_id] = role_name
    print(f"  Class-to-role (C591): {len(class_to_role)} classes -> {len(role_data['resolved_roles'])} roles")

    # 6. Final partition (6 states) -> class_to_state
    part_path = ROOT / 'phases' / 'MINIMAL_STATE_AUTOMATON' / 'results' / 't3_merged_automaton.json'
    with open(part_path, 'r', encoding='utf-8') as f:
        part_data = json.load(f)
    final_partition = part_data['final_partition']
    class_to_state = {}
    for state_idx, class_list in enumerate(final_partition):
        for cls_id in class_list:
            class_to_state[cls_id] = state_idx
    print(f"  6-state partition: {len(final_partition)} states, {len(class_to_state)} classes mapped")

    # 7. State labels
    topo_path = ROOT / 'phases' / 'MINIMAL_STATE_AUTOMATON' / 'results' / 't6_state_topology.json'
    with open(topo_path, 'r', encoding='utf-8') as f:
        topo_data = json.load(f)
    state_labels_raw = topo_data['state_labels']
    # Extract short labels: "S0: FL_HAZ" -> "FL_HAZ"
    state_labels = [s.split(': ')[1] if ': ' in s else s for s in state_labels_raw]
    print(f"  State labels: {state_labels}")

    # 8. C1072 results
    c1072_path = ROOT / 'phases' / 'MULTI_LAYER_COMPATIBILITY_ARCHITECTURE' / 'results' / 't5_terminal_compatibility.json'
    with open(c1072_path, 'r', encoding='utf-8') as f:
        c1072_data = json.load(f)
    print(f"  C1072 data: {c1072_data['n_significant_groups']} significant groups")

    # 9. Currier B tokens with morphology
    tx = Transcript()
    b_tokens = []
    for t in tx.currier_b():
        word = t.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        b_tokens.append({
            'word': word,
            'folio': t.folio,
            'line': t.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
        })
    print(f"  Currier B tokens: {len(b_tokens)}")

    return (compat_matrix, all_middles, mid_to_idx,
            affordance_table, hub_data, token_to_class,
            class_to_role, class_to_state, state_labels,
            c1072_data, b_tokens, morph)


def build_terminal_groups(all_middles):
    """Group 972 MIDDLEs by their terminal (last) character."""
    terminal_groups = defaultdict(list)
    for i, mid in enumerate(all_middles):
        if mid:
            terminal_groups[mid[-1]].append(i)
    return dict(terminal_groups)


# ============================================================
# T1: Terminal-Character Neighborhood Role Composition
# ============================================================

def run_t1(all_middles, mid_to_idx, terminal_groups, b_tokens,
           token_to_class, class_to_role):
    """T1: Terminal-Character Neighborhood Role Composition (C591 x terminal char)."""
    print("\n" + "=" * 60)
    print("T1: Terminal-Character Neighborhood Role Composition")
    print("    Prior: C777 (FL 'y' terminal), C770 (FL excludes k/h/e)")
    print("=" * 60)

    # 1. For each Currier B token, get (terminal_char, role)
    token_records = []
    mid_role_counts = defaultdict(Counter)  # for permutation null
    for t in b_tokens:
        mid = t['middle']
        if not mid or mid not in mid_to_idx:
            continue
        terminal = mid[-1]
        cls_id = token_to_class.get(t['word'])
        if cls_id is None:
            continue
        role = class_to_role.get(cls_id)
        if role is None:
            continue
        token_records.append((terminal, role))
        mid_role_counts[mid][role] += 1

    print(f"  Token records with role assignment: {len(token_records)}")

    # 2. Build contingency table: terminal_char x role
    roles_list = sorted(set(r for _, r in token_records))
    terminals_list = sorted(set(tc for tc, _ in token_records))
    role_idx = {r: i for i, r in enumerate(roles_list)}
    term_idx = {t: i for i, t in enumerate(terminals_list)}

    table = np.zeros((len(terminals_list), len(roles_list)), dtype=int)
    for tc, r in token_records:
        table[term_idx[tc], role_idx[r]] += 1

    # 3. Chi-squared + Cramer's V
    table_clean = clean_table(table)
    chi2, p, dof, expected = chi2_contingency(table_clean)
    v = cramers_v(table_clean)
    print(f"  Contingency: {table_clean.shape}, chi2={chi2:.1f}, p={p:.2e}, V={v:.4f}")

    # 4. Per-terminal-group role profiles
    significant_terminals = ['n', 'm', 'y', 'r', 'l']
    per_group = {}
    for tc in terminals_list:
        row = table[term_idx[tc]]
        total = int(row.sum())
        if total == 0:
            continue
        profile = {roles_list[j]: int(row[j]) for j in range(len(roles_list))}
        pct = {roles_list[j]: round(row[j] / total, 4) for j in range(len(roles_list))}
        per_group[tc] = {'counts': profile, 'pct': pct, 'total': total}

    # 5. C777/C770 notes
    notes = []
    if 'y' in per_group:
        fl_pct = per_group['y']['pct'].get('FL', 0)
        notes.append(f"C777 quantification: 'y' terminal FL={fl_pct:.1%} (known FL terminal bias)")
    for khe in ['k', 'h', 'e']:
        if khe in per_group:
            fl_pct = per_group[khe]['pct'].get('FL', 0)
            notes.append(f"C770 tautology: '{khe}' terminal FL={fl_pct:.1%} (FL excludes kernel chars by construction)")
    for khe in ['k', 'h', 'e']:
        if khe in per_group:
            notes.append(f"C908 consistency: '{khe}' terminal role profile is kernel-correlation check, not novelty")

    # 6. Permutation null (1000 shuffles of terminal labels across MIDDLEs)
    print("  Running permutation null (1000 shuffles)...")
    rng = np.random.default_rng(42)
    middles_in_matrix = [m for m in all_middles if m in mid_role_counts and mid_role_counts[m]]
    original_terminals = [m[-1] for m in middles_in_matrix]

    null_vs = []
    for _ in range(1000):
        shuffled = list(original_terminals)
        rng.shuffle(shuffled)
        perm_table = np.zeros((len(terminals_list), len(roles_list)), dtype=int)
        for mid_name, perm_tc in zip(middles_in_matrix, shuffled):
            if perm_tc not in term_idx:
                continue
            for role, cnt in mid_role_counts[mid_name].items():
                if role in role_idx:
                    perm_table[term_idx[perm_tc], role_idx[role]] += cnt
        pt_clean = clean_table(perm_table)
        if pt_clean.shape[0] >= 2 and pt_clean.shape[1] >= 2:
            null_vs.append(cramers_v(pt_clean))

    perm_p = float(np.mean([nv >= v for nv in null_vs])) if null_vs else 1.0
    null_v_mean = float(np.mean(null_vs)) if null_vs else 0.0
    print(f"  Permutation: null_V_mean={null_v_mean:.4f}, perm_p={perm_p:.4f}")

    # 7. Verdict
    if v > 0.15 and perm_p < 0.01:
        verdict = "PASS"
    elif v > 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"  -> Verdict: {verdict} (V={v:.4f}, perm_p={perm_p:.4f})")

    result = {
        'test': 'T1_role_composition',
        'verdict': verdict,
        'n_tokens_analyzed': len(token_records),
        'n_terminal_groups': len(terminals_list),
        'n_roles': len(roles_list),
        'roles': roles_list,
        'chi2': round(chi2, 1),
        'p': p,
        'cramers_v': round(v, 4),
        'null_v_mean': round(null_v_mean, 4),
        'perm_p': round(perm_p, 4),
        'per_group_profiles': per_group,
        'significant_terminals_focus': significant_terminals,
        'notes': notes,
        'constraints_referenced': ['C591', 'C777', 'C770', 'C908', 'C1072', 'C475', 'C986'],
    }
    save_result(result, 't1_role_composition.json')
    return result


# ============================================================
# T2: Terminal-Character x Macro-State Correspondence
# ============================================================

def run_t2(all_middles, mid_to_idx, terminal_groups, b_tokens,
           token_to_class, class_to_state, state_labels):
    """T2: Terminal-Character x Macro-State Correspondence (C976 x terminal char)."""
    print("\n" + "=" * 60)
    print("T2: Terminal-Character x Macro-State Correspondence")
    print("    Prior: AXM dominates 67.7%, FL_SAFE only 0.8%")
    print("=" * 60)

    # 1. For each Currier B token, get (terminal_char, state_index)
    token_records = []
    mid_state_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t['middle']
        if not mid or mid not in mid_to_idx:
            continue
        terminal = mid[-1]
        cls_id = token_to_class.get(t['word'])
        if cls_id is None:
            continue
        state_idx = class_to_state.get(cls_id)
        if state_idx is None:
            continue
        token_records.append((terminal, state_idx))
        mid_state_counts[mid][state_idx] += 1

    print(f"  Token records with state assignment: {len(token_records)}")

    terminals_list = sorted(set(tc for tc, _ in token_records))
    n_states = len(state_labels)
    term_idx = {t: i for i, t in enumerate(terminals_list)}

    # 2. Full contingency table: terminal_char x 6 states
    table_full = np.zeros((len(terminals_list), n_states), dtype=int)
    for tc, si in token_records:
        table_full[term_idx[tc], si] += 1

    tc_full = clean_table(table_full)
    chi2_full, p_full, _, expected_full = chi2_contingency(tc_full)
    v_full = cramers_v(tc_full)
    print(f"  Full: chi2={chi2_full:.1f}, p={p_full:.2e}, V={v_full:.4f}")

    # Check FL_SAFE expected counts
    fl_safe_expected = expected_full[:, -1] if expected_full.shape[1] == n_states else None
    min_expected = float(expected_full.min()) if expected_full is not None else 0
    print(f"  Min expected cell count: {min_expected:.2f}")

    # 3. Non-AXM conditioned table (exclude state 4 = AXM)
    axm_idx = state_labels.index('AX/EN major') if 'AX/EN major' in state_labels else 4
    non_axm_records = [(tc, si) for tc, si in token_records if si != axm_idx]
    non_axm_states = [i for i in range(n_states) if i != axm_idx]
    non_axm_labels = [state_labels[i] for i in non_axm_states]
    state_remap = {old: new for new, old in enumerate(non_axm_states)}

    table_nonaxm = np.zeros((len(terminals_list), len(non_axm_states)), dtype=int)
    for tc, si in non_axm_records:
        if si in state_remap:
            table_nonaxm[term_idx[tc], state_remap[si]] += 1

    tc_nonaxm = clean_table(table_nonaxm)
    chi2_nonaxm, p_nonaxm, _, _ = chi2_contingency(tc_nonaxm)
    v_nonaxm = cramers_v(tc_nonaxm)
    print(f"  Non-AXM: chi2={chi2_nonaxm:.1f}, p={p_nonaxm:.2e}, V={v_nonaxm:.4f}")
    print(f"  Non-AXM tokens: {len(non_axm_records)}/{len(token_records)}")

    # 4. FL collapsed table (FL_HAZ + FL_SAFE -> FL)
    # State 0=FL_HAZ, State 5=FL_SAFE -> merge
    fl_haz_idx = 0
    fl_safe_idx = 5
    collapsed_states = []
    collapse_map = {}
    for i in range(n_states):
        if i == fl_safe_idx:
            collapse_map[i] = collapse_map[fl_haz_idx]  # map to FL_HAZ's new index
        else:
            collapse_map[i] = len(collapsed_states)
            collapsed_states.append(state_labels[i] if i != fl_haz_idx else 'FL')

    table_collapsed = np.zeros((len(terminals_list), len(collapsed_states)), dtype=int)
    for tc, si in token_records:
        table_collapsed[term_idx[tc], collapse_map[si]] += 1

    tc_coll = clean_table(table_collapsed)
    chi2_coll, p_coll, _, _ = chi2_contingency(tc_coll)
    v_coll = cramers_v(tc_coll)
    print(f"  FL-collapsed: chi2={chi2_coll:.1f}, V={v_coll:.4f}")

    # 5. Permutation null for non-AXM V
    print("  Running permutation null for non-AXM (1000 shuffles)...")
    rng = np.random.default_rng(42)
    middles_in = [m for m in all_middles if m in mid_state_counts and mid_state_counts[m]]
    orig_terms = [m[-1] for m in middles_in]

    null_vs = []
    for _ in range(1000):
        shuffled = list(orig_terms)
        rng.shuffle(shuffled)
        perm_table = np.zeros((len(terminals_list), len(non_axm_states)), dtype=int)
        for mid_name, perm_tc in zip(middles_in, shuffled):
            if perm_tc not in term_idx:
                continue
            for si, cnt in mid_state_counts[mid_name].items():
                if si in state_remap:
                    perm_table[term_idx[perm_tc], state_remap[si]] += cnt
        pt_clean = clean_table(perm_table)
        if pt_clean.shape[0] >= 2 and pt_clean.shape[1] >= 2:
            null_vs.append(cramers_v(pt_clean))

    perm_p = float(np.mean([nv >= v_nonaxm for nv in null_vs])) if null_vs else 1.0
    null_v_mean = float(np.mean(null_vs)) if null_vs else 0.0
    print(f"  Perm null: mean_V={null_v_mean:.4f}, perm_p={perm_p:.4f}")

    # 6. Per-terminal state profiles for significant groups
    sig_terms = ['n', 'm', 'y', 'r', 'l']
    per_group = {}
    for tc in terminals_list:
        row = table_full[term_idx[tc]]
        total = int(row.sum())
        if total == 0:
            continue
        profile = {state_labels[j]: int(row[j]) for j in range(n_states)}
        pct = {state_labels[j]: round(row[j] / total, 4) for j in range(n_states)}
        per_group[tc] = {'counts': profile, 'pct': pct, 'total': total}

    # 7. Verdict
    if v_nonaxm > 0.10 and perm_p < 0.01:
        verdict = "PASS"
    elif v_nonaxm > 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"  -> Verdict: {verdict} (V_nonAXM={v_nonaxm:.4f}, perm_p={perm_p:.4f})")

    result = {
        'test': 'T2_macro_state_correspondence',
        'verdict': verdict,
        'n_tokens_analyzed': len(token_records),
        'full': {'chi2': round(chi2_full, 1), 'p': p_full, 'cramers_v': round(v_full, 4)},
        'non_axm': {
            'chi2': round(chi2_nonaxm, 1), 'p': p_nonaxm, 'cramers_v': round(v_nonaxm, 4),
            'n_tokens': len(non_axm_records), 'states': non_axm_labels,
        },
        'fl_collapsed': {'chi2': round(chi2_coll, 1), 'cramers_v': round(v_coll, 4)},
        'min_expected_cell': round(min_expected, 2),
        'null_v_mean': round(null_v_mean, 4),
        'perm_p': round(perm_p, 4),
        'per_group_profiles': per_group,
        'orthogonality_note': 'T1 discriminates EN vs AX (merged here); T2 discriminates FL_HAZ vs FL_SAFE (merged in T1)',
        'constraints_referenced': ['C976', 'C977', 'C1015', 'C1072', 'C986'],
    }
    save_result(result, 't2_macro_state_correspondence.json')
    return result


# ============================================================
# T3: INITIAL vs FINAL Terminal Asymmetry Mechanism
# ============================================================

def run_t3(compat_matrix, all_middles, mid_to_idx, affordance_table,
           b_tokens, morph):
    """T3: INITIAL vs FINAL Terminal Asymmetry Mechanism (logistic regression)."""
    print("\n" + "=" * 60)
    print("T3: INITIAL vs FINAL Terminal Asymmetry Mechanism")
    print("    Prior: C1072 3.2x INITIAL>FINAL. Controls: length, freq, C517 hinge")
    print("=" * 60)

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    n = len(all_middles)

    # Pre-compute per-MIDDLE properties
    mid_length = np.array([len(m) for m in all_middles], dtype=float)
    mid_first = np.array([m[0] if m else '' for m in all_middles])
    mid_last = np.array([m[-1] if m else '' for m in all_middles])

    # Log-frequency from affordance table
    mid_freq = np.zeros(n)
    mid_bin = np.full(n, -1, dtype=int)
    for i, m in enumerate(all_middles):
        entry = affordance_table.get(m, {})
        if entry and 'token_frequency' in entry:
            mid_freq[i] = entry.get('token_frequency', 0)
            mid_bin[i] = entry.get('affordance_bin', -1)
    mid_log_freq = np.log1p(mid_freq)

    # C517 hinge letters (kernel primitives used as superstring hinges)
    hinge_set = set('setdlokr')
    mid_hinge_chars = [set(m) & hinge_set for m in all_middles]

    # Dominant prefix per MIDDLE
    mid_prefix_counts = defaultdict(Counter)
    for t in b_tokens:
        mid = t['middle']
        if mid and mid in mid_to_idx:
            mid_prefix_counts[mid][t['prefix'] or '_BARE_'] += 1
    mid_dom_prefix = np.array([
        mid_prefix_counts[m].most_common(1)[0][0] if mid_prefix_counts[m] else '_BARE_'
        for m in all_middles
    ])

    # Build pair indices (upper triangle)
    print("  Building pair feature matrix...")
    pairs_i = []
    pairs_j = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs_i.append(i)
            pairs_j.append(j)
    pairs_i = np.array(pairs_i)
    pairs_j = np.array(pairs_j)
    n_pairs = len(pairs_i)
    print(f"  Total pairs: {n_pairs}")

    # Features (vectorized)
    initial_match = (mid_first[pairs_i] == mid_first[pairs_j]).astype(float)
    final_match = (mid_last[pairs_i] == mid_last[pairs_j]).astype(float)
    initial_x_final = initial_match * final_match  # C1003 interaction
    length_sum = mid_length[pairs_i] + mid_length[pairs_j]
    freq_sum = mid_log_freq[pairs_i] + mid_log_freq[pairs_j]
    same_bin = (mid_bin[pairs_i] == mid_bin[pairs_j]).astype(float)
    same_prefix = (mid_dom_prefix[pairs_i] == mid_dom_prefix[pairs_j]).astype(float)

    # Shared hinge: 1 if both MIDDLEs share at least one hinge letter
    shared_hinge = np.array([
        1.0 if mid_hinge_chars[pairs_i[k]] & mid_hinge_chars[pairs_j[k]] else 0.0
        for k in range(n_pairs)
    ])

    X_all = np.column_stack([initial_match, final_match, initial_x_final,
                             length_sum, freq_sum, same_bin, same_prefix, shared_hinge])
    feature_names = ['INITIAL_match', 'FINAL_match', 'INITIAL_x_FINAL',
                     'length_sum', 'freq_sum', 'same_bin', 'same_prefix', 'shared_hinge']

    # Target
    y_all = np.array([compat_matrix[pairs_i[k], pairs_j[k]] > 0 for k in range(n_pairs)], dtype=int)
    print(f"  Positive rate: {y_all.mean():.4f} ({y_all.sum()}/{n_pairs})")

    # Singleton exclusion: both MIDDLEs have token_frequency <= 1
    both_singleton = (mid_freq[pairs_i] <= 1) & (mid_freq[pairs_j] <= 1)
    mask = ~both_singleton
    n_excluded = int(both_singleton.sum())
    coverage_pct = mask.sum() / n_pairs * 100
    print(f"  Singleton exclusion: {n_excluded} pairs removed ({100-coverage_pct:.1f}%), {mask.sum()} remaining")

    X = X_all[mask]
    y = y_all[mask]

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Logistic regression
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, penalty='l2',
                            solver='lbfgs', C=1.0)
    lr.fit(X_scaled, y)
    coefs = lr.coef_[0]

    print(f"\n  Standardized coefficients:")
    for name, coef in zip(feature_names, coefs):
        print(f"    {name:20s}: {coef:+.4f}")

    # McFadden pseudo R-squared
    from sklearn.metrics import log_loss
    y_pred_proba = lr.predict_proba(X_scaled)[:, 1]
    ll_model = -log_loss(y, y_pred_proba, normalize=False)
    # Null model: predict mean probability
    p_null = y.mean()
    ll_null = y.sum() * np.log(p_null) + (len(y) - y.sum()) * np.log(1 - p_null)
    pseudo_r2 = 1 - (ll_model / ll_null) if ll_null != 0 else 0
    print(f"  McFadden pseudo-R2: {pseudo_r2:.4f}")

    # Bootstrap 95% CI (100 samples)
    print("  Running bootstrap (100 samples)...")
    rng = np.random.default_rng(42)
    boot_coefs = np.zeros((100, len(feature_names)))
    for b in range(100):
        idx = rng.choice(len(y), size=len(y), replace=True)
        X_b, y_b = X_scaled[idx], y[idx]
        if len(np.unique(y_b)) < 2:
            boot_coefs[b] = coefs
            continue
        lr_b = LogisticRegression(class_weight='balanced', max_iter=1000,
                                  penalty='l2', solver='lbfgs', C=1.0)
        lr_b.fit(X_b, y_b)
        boot_coefs[b] = lr_b.coef_[0]

    ci_low = np.percentile(boot_coefs, 2.5, axis=0)
    ci_high = np.percentile(boot_coefs, 97.5, axis=0)

    coef_results = {}
    for i_f, name in enumerate(feature_names):
        sig = (ci_low[i_f] > 0) or (ci_high[i_f] < 0)  # CI doesn't cross zero
        coef_results[name] = {
            'std_coef': round(float(coefs[i_f]), 4),
            'ci_low': round(float(ci_low[i_f]), 4),
            'ci_high': round(float(ci_high[i_f]), 4),
            'significant': bool(sig),
        }

    # Sensitivity: re-run with singletons included
    print("  Sensitivity: running with singletons included...")
    scaler_all = StandardScaler()
    X_all_scaled = scaler_all.fit_transform(X_all)
    lr_all = LogisticRegression(class_weight='balanced', max_iter=1000,
                                penalty='l2', solver='lbfgs', C=1.0)
    lr_all.fit(X_all_scaled, y_all)
    sensitivity_coefs = {name: round(float(lr_all.coef_[0][i_f]), 4)
                        for i_f, name in enumerate(feature_names)}
    print(f"  Sensitivity coefs: {sensitivity_coefs}")

    # C1003 interaction check
    interaction_coef = coef_results['INITIAL_x_FINAL']['std_coef']
    interaction_sig = coef_results['INITIAL_x_FINAL']['significant']
    c1003_note = (f"INITIAL_x_FINAL interaction: {interaction_coef:+.4f}, "
                  f"{'SIGNIFICANT (flags against C1003)' if interaction_sig else 'not significant (consistent with C1003)'}")

    # Verdict
    init_sig = coef_results['INITIAL_match']['significant'] and abs(coef_results['INITIAL_match']['std_coef']) > 0.10
    final_sig = coef_results['FINAL_match']['significant'] and abs(coef_results['FINAL_match']['std_coef']) > 0.10
    length_only = (coef_results['length_sum']['significant'] and
                   not init_sig and not final_sig)

    if init_sig or final_sig:
        verdict = "PASS"
    elif length_only or coef_results['freq_sum']['significant']:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"  -> Verdict: {verdict}")

    result = {
        'test': 'T3_asymmetry_mechanism',
        'verdict': verdict,
        'n_pairs_total': n_pairs,
        'n_pairs_after_exclusion': int(mask.sum()),
        'n_excluded_singleton': n_excluded,
        'coverage_pct': round(coverage_pct, 1),
        'positive_rate': round(float(y.mean()), 4),
        'pseudo_r2': round(pseudo_r2, 4),
        'coefficients': coef_results,
        'sensitivity_with_singletons': sensitivity_coefs,
        'c1003_interaction_note': c1003_note,
        'constraints_referenced': ['C1072', 'C985', 'C986', 'C475', 'C517', 'C1003', 'C513'],
    }
    save_result(result, 't3_asymmetry_mechanism.json')
    return result


# ============================================================
# T4: Terminal Neighborhood x Affordance Bin Alignment
# ============================================================

def run_t4(all_middles, mid_to_idx, terminal_groups, affordance_table, hub_data):
    """T4: Terminal Neighborhood x Affordance Bin Alignment (C995 x terminal char)."""
    print("\n" + "=" * 60)
    print("T4: Terminal Neighborhood x Affordance Bin Alignment")
    print("    Prior: BULK_OPERATIONAL dominates (566/972)")
    print("=" * 60)

    # 1. MIDDLE -> affordance bin
    mid_to_bin = {}
    bin_labels = {}
    for mid in all_middles:
        entry = affordance_table.get(mid, {})
        if entry and 'affordance_bin' in entry:
            mid_to_bin[mid] = entry['affordance_bin']
            if 'affordance_label' in entry:
                bin_labels[entry['affordance_bin']] = entry['affordance_label']

    all_bins = sorted(set(mid_to_bin.values()))
    print(f"  Affordance bins found: {len(all_bins)} -> {all_bins}")
    for b in all_bins:
        label = bin_labels.get(b, '?')
        count = sum(1 for m in all_middles if mid_to_bin.get(m) == b)
        print(f"    Bin {b} ({label}): {count} MIDDLEs")

    terminals_list = sorted(terminal_groups.keys())
    term_idx = {t: i for i, t in enumerate(terminals_list)}
    bin_idx_map = {b: i for i, b in enumerate(all_bins)}

    # 2. Full contingency table: terminal char x affordance bin
    table_full = np.zeros((len(terminals_list), len(all_bins)), dtype=int)
    for mid in all_middles:
        if not mid or mid not in mid_to_idx:
            continue
        tc = mid[-1]
        b = mid_to_bin.get(mid, -1)
        if b == -1 or tc not in term_idx or b not in bin_idx_map:
            continue
        table_full[term_idx[tc], bin_idx_map[b]] += 1

    tc_full = clean_table(table_full)
    chi2_full, p_full, _, _ = chi2_contingency(tc_full)
    v_full = cramers_v(tc_full)
    print(f"  Full: chi2={chi2_full:.1f}, p={p_full:.2e}, V={v_full:.4f}")

    # 3. Non-BULK table (exclude bin 4 = BULK_OPERATIONAL)
    bulk_bin = 4
    non_bulk_bins = [b for b in all_bins if b != bulk_bin]
    non_bulk_idx = {b: i for i, b in enumerate(non_bulk_bins)}

    table_nonbulk = np.zeros((len(terminals_list), len(non_bulk_bins)), dtype=int)
    n_nonbulk = 0
    for mid in all_middles:
        if not mid or mid not in mid_to_idx:
            continue
        tc = mid[-1]
        b = mid_to_bin.get(mid, -1)
        if b == bulk_bin or b == -1 or tc not in term_idx or b not in non_bulk_idx:
            continue
        table_nonbulk[term_idx[tc], non_bulk_idx[b]] += 1
        n_nonbulk += 1

    tc_nb = clean_table(table_nonbulk)
    if tc_nb.shape[0] >= 2 and tc_nb.shape[1] >= 2:
        chi2_nb, p_nb, _, _ = chi2_contingency(tc_nb)
        v_nb = cramers_v(tc_nb)
    else:
        chi2_nb, p_nb, v_nb = 0, 1, 0
    print(f"  Non-BULK: {n_nonbulk} MIDDLEs, chi2={chi2_nb:.1f}, p={p_nb:.2e}, V={v_nb:.4f}")

    # 4. Permutation null for non-BULK V
    print("  Running permutation null for non-BULK (1000 shuffles)...")
    rng = np.random.default_rng(42)
    # Only non-BULK MIDDLEs participate
    nb_middles = [m for m in all_middles if m and mid_to_bin.get(m, -1) != bulk_bin and mid_to_bin.get(m, -1) != -1]
    orig_terms_nb = [m[-1] for m in nb_middles]
    nb_bins = [mid_to_bin[m] for m in nb_middles]

    null_vs = []
    for _ in range(1000):
        shuffled = list(orig_terms_nb)
        rng.shuffle(shuffled)
        perm_table = np.zeros((len(terminals_list), len(non_bulk_bins)), dtype=int)
        for perm_tc, b in zip(shuffled, nb_bins):
            if perm_tc in term_idx and b in non_bulk_idx:
                perm_table[term_idx[perm_tc], non_bulk_idx[b]] += 1
        pt_clean = clean_table(perm_table)
        if pt_clean.shape[0] >= 2 and pt_clean.shape[1] >= 2:
            null_vs.append(cramers_v(pt_clean))

    perm_p = float(np.mean([nv >= v_nb for nv in null_vs])) if null_vs else 1.0
    null_v_mean = float(np.mean(null_vs)) if null_vs else 0.0
    print(f"  Perm null: mean_V={null_v_mean:.4f}, perm_p={perm_p:.4f}")

    # 5. HUB sub-role analysis (23 MIDDLEs)
    hub_primary = hub_data['primary_roles']
    hub_by_terminal = defaultdict(list)
    for mid, role in hub_primary.items():
        if mid:
            hub_by_terminal[mid[-1]].append({'middle': mid, 'sub_role': role})

    hub_terminal_summary = {}
    for tc, entries in sorted(hub_by_terminal.items()):
        role_counts = Counter(e['sub_role'] for e in entries)
        hub_terminal_summary[tc] = {
            'n_hub_middles': len(entries),
            'middles': [e['middle'] for e in entries],
            'sub_role_counts': dict(role_counts),
        }

    print(f"  HUB by terminal: {dict((k, v['n_hub_middles']) for k, v in hub_terminal_summary.items())}")

    # 6. Per-terminal bin profiles for significant groups
    sig_terms = ['n', 'm', 'y', 'r', 'l']
    per_group = {}
    for tc in terminals_list:
        row = table_full[term_idx[tc]]
        total = int(row.sum())
        if total == 0:
            continue
        profile = {bin_labels.get(all_bins[j], str(all_bins[j])): int(row[j])
                   for j in range(len(all_bins))}
        pct = {bin_labels.get(all_bins[j], str(all_bins[j])): round(row[j] / total, 4)
               for j in range(len(all_bins))}
        per_group[tc] = {'counts': profile, 'pct': pct, 'total': total}

    # 7. Verdict
    if v_nb > 0.10 and perm_p < 0.01:
        verdict = "PASS"
    elif v_nb > 0.05:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"  -> Verdict: {verdict} (V_nonBULK={v_nb:.4f}, perm_p={perm_p:.4f})")

    result = {
        'test': 'T4_affordance_bin_alignment',
        'verdict': verdict,
        'n_bins': len(all_bins),
        'bin_labels': bin_labels,
        'full': {'chi2': round(chi2_full, 1), 'p': p_full, 'cramers_v': round(v_full, 4)},
        'non_bulk': {
            'n_middles': n_nonbulk, 'chi2': round(chi2_nb, 1),
            'p': p_nb, 'cramers_v': round(v_nb, 4),
        },
        'null_v_mean': round(null_v_mean, 4),
        'perm_p': round(perm_p, 4),
        'hub_sub_role_by_terminal': hub_terminal_summary,
        'per_group_profiles': per_group,
        'constraints_referenced': ['C995', 'C1000', 'C1072', 'C986'],
    }
    save_result(result, 't4_affordance_bin_alignment.json')
    return result


# ============================================================
# T5: Terminal Neighborhood Transitivity Test
# ============================================================

def run_t5(compat_matrix, all_middles, mid_to_idx, terminal_groups, affordance_table):
    """T5: Terminal Neighborhood Transitivity Test (clique fraction)."""
    print("\n" + "=" * 60)
    print("T5: Terminal Neighborhood Transitivity Test")
    print("    Prior: C983 global clustering=0.873. 5 pre-registered groups from C1072.")
    print("=" * 60)

    significant_terminals = ['n', 'm', 'y', 'r', 'l']

    # Frequency for band matching
    n = len(all_middles)
    mid_freq = np.zeros(n)
    for i, m in enumerate(all_middles):
        entry = affordance_table.get(m, {})
        if entry:
            mid_freq[i] = entry.get('token_frequency', 0)
    log_freq = np.log1p(mid_freq)
    q25, q50, q75 = np.percentile(log_freq, [25, 50, 75])

    def freq_band(lf):
        if lf <= q25: return 0
        if lf <= q50: return 1
        if lf <= q75: return 2
        return 3

    mid_band = np.array([freq_band(lf) for lf in log_freq])

    # Pools by frequency band
    band_pools = defaultdict(list)
    for i in range(n):
        band_pools[mid_band[i]].append(i)

    # Global clustering coefficient for context (C983)
    global_compat = int(np.triu(compat_matrix, k=1).sum())
    global_possible = n * (n - 1) // 2
    global_rate = global_compat / global_possible if global_possible > 0 else 0
    print(f"  Global compatibility rate: {global_rate:.4f} ({global_compat}/{global_possible})")

    rng = np.random.default_rng(42)
    results_per_group = []

    for tc in significant_terminals:
        if tc not in terminal_groups:
            print(f"  '{tc}': not in terminal groups, skipping")
            continue

        indices = terminal_groups[tc]
        group_n = len(indices)
        if group_n < 2:
            continue

        idx_arr = np.array(indices)
        submatrix = compat_matrix[np.ix_(idx_arr, idx_arr)]
        possible = group_n * (group_n - 1) // 2
        actual = int(np.triu(submatrix, k=1).sum())
        clique_fraction = actual / possible if possible > 0 else 0

        # Null: random groups matching frequency band distribution
        group_bands = mid_band[idx_arr]
        band_counts = Counter(int(b) for b in group_bands)

        null_fractions = []
        for _ in range(1000):
            sampled = []
            valid = True
            for band, count in band_counts.items():
                pool = band_pools[band]
                if len(pool) < count:
                    valid = False
                    break
                chosen = rng.choice(pool, size=count, replace=False)
                sampled.extend(chosen.tolist())
            if not valid or len(sampled) != group_n:
                continue
            s_arr = np.array(sampled)
            sub = compat_matrix[np.ix_(s_arr, s_arr)]
            null_actual = int(np.triu(sub, k=1).sum())
            null_fractions.append(null_actual / possible)

        null_mean = float(np.mean(null_fractions)) if null_fractions else 0
        ratio = clique_fraction / null_mean if null_mean > 0 else float('inf')
        p_val = float(np.mean([nf >= clique_fraction for nf in null_fractions])) if null_fractions else 1.0

        elevated = ratio > 2.0 and p_val < 0.05

        print(f"  '{tc}': n={group_n}, clique={clique_fraction:.4f}, null={null_mean:.4f}, "
              f"ratio={ratio:.2f}x, p={p_val:.4f} {'*ELEVATED*' if elevated else ''}")

        results_per_group.append({
            'terminal_char': tc,
            'n_middles': group_n,
            'possible_pairs': possible,
            'actual_compatible': actual,
            'clique_fraction': round(clique_fraction, 4),
            'null_mean_fraction': round(null_mean, 4),
            'ratio_vs_null': round(ratio, 2),
            'p': round(p_val, 4),
            'elevated': elevated,
        })

    n_elevated = sum(1 for r in results_per_group if r['elevated'])

    if n_elevated >= 3:
        verdict = "PASS"
    elif n_elevated >= 1:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"  -> Verdict: {verdict} ({n_elevated}/5 elevated)")

    result = {
        'test': 'T5_transitivity_test',
        'verdict': verdict,
        'n_groups_tested': len(results_per_group),
        'n_elevated': n_elevated,
        'global_compatibility_rate': round(global_rate, 4),
        'c983_note': 'Global clustering=0.873. Absolute clique fractions reported alongside ratio-to-null.',
        'groups': results_per_group,
        'constraints_referenced': ['C1072', 'C475', 'C983', 'C986', 'C995'],
    }
    save_result(result, 't5_transitivity_test.json')
    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 382: Terminal Compatibility Geography")
    print("5-test battery | Tier 2 targets | Expert-validated")
    print("=" * 60)

    print("\nLoading data...")
    (compat_matrix, all_middles, mid_to_idx,
     affordance_table, hub_data, token_to_class,
     class_to_role, class_to_state, state_labels,
     c1072_data, b_tokens, morph) = load_data()

    terminal_groups = build_terminal_groups(all_middles)
    print(f"\n  Terminal groups: {len(terminal_groups)} unique chars")
    for tc in sorted(terminal_groups.keys()):
        print(f"    '{tc}': {len(terminal_groups[tc])} MIDDLEs")

    # Run all tests
    t1 = run_t1(all_middles, mid_to_idx, terminal_groups, b_tokens,
                token_to_class, class_to_role)
    t2 = run_t2(all_middles, mid_to_idx, terminal_groups, b_tokens,
                token_to_class, class_to_state, state_labels)
    t3 = run_t3(compat_matrix, all_middles, mid_to_idx, affordance_table,
                b_tokens, morph)
    t4 = run_t4(all_middles, mid_to_idx, terminal_groups, affordance_table, hub_data)
    t5 = run_t5(compat_matrix, all_middles, mid_to_idx, terminal_groups, affordance_table)

    # Summary
    tests = [
        {'id': 'T1', 'name': 'Role Composition', 'verdict': t1['verdict']},
        {'id': 'T2', 'name': 'Macro-State Correspondence', 'verdict': t2['verdict']},
        {'id': 'T3', 'name': 'Asymmetry Mechanism', 'verdict': t3['verdict']},
        {'id': 'T4', 'name': 'Affordance Bin Alignment', 'verdict': t4['verdict']},
        {'id': 'T5', 'name': 'Transitivity Test', 'verdict': t5['verdict']},
    ]

    all_refs = set()
    for t in [t1, t2, t3, t4, t5]:
        all_refs.update(t.get('constraints_referenced', []))

    summary = {
        'phase': 382,
        'name': 'TERMINAL_COMPATIBILITY_GEOGRAPHY',
        'description': '5-test battery: role composition, macro-state correspondence, '
                      'asymmetry mechanism, affordance bin alignment, transitivity test',
        'tier': 2,
        'tests': tests,
        'constraints_referenced': sorted(all_refs),
    }
    save_result(summary, 'terminal_compatibility_geography_summary.json')

    print("\n" + "=" * 60)
    print("RESULTS:")
    for t in tests:
        print(f"  {t['id']}: {t['name']:30s} -> {t['verdict']}")
    print("=" * 60)


if __name__ == '__main__':
    main()

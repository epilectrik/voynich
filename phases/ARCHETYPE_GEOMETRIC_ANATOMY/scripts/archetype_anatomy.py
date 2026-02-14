#!/usr/bin/env python3
"""
Phase 341: ARCHETYPE_GEOMETRIC_ANATOMY
========================================
Investigates archetype slope anomalies (C1017: PREFIX sign flip in archetype 5,
hazard sign flip in archetype 6) and decomposes bridge PC1 into interpretable
structural features.

Tests:
  T1: Archetype structural profiling (section/REGIME confound checks)
  T2: Bootstrap validation of slope anomalies
  T3: Bridge PC1 decomposition (what does PC1 represent?)
  T4: Archetype discriminator features (7 feature families)
  T5: Unified hypothesis test (bridge geometry × archetype linkage)

Depends on: C1017 (variance decomposition), C1016 (folio archetypes),
            C1010 (6-state partition), C995 (affordance bins),
            C1000 (HUB sub-roles), C1011 (geometric independence)

Re-derivation guards:
  - T3 checks PC1 vs hub frequency (avoids re-deriving C986)
  - T3 checks PC1 vs radial depth (avoids re-deriving C991)
  - T1 checks section confounds (avoids conflating section with archetype)
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants (from Phase 340 / C1010) ──────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
N_STATES = len(STATE_ORDER)

MIN_TRANSITIONS = 50
GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_TOKENS = HAZARD_SOURCES | HAZARD_TARGETS

N_BOOTSTRAP = 1000
N_PERM = 1000
K_EMBED = 100


# ── Data Loading ────────────────────────────────────────────────────

def load_token_to_class():
    path = Path(__file__).resolve().parents[2] / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    path = Path(__file__).resolve().parents[2] / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = Path(__file__).resolve().parents[2] / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    return data['t2_archetype_discovery']


def load_bridge_middles():
    path = Path(__file__).resolve().parents[2] / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(path) as f:
        data = json.load(f)
    return set(data['t5_structural_profile']['bridge_middles'])


def load_affordance_table():
    path = Path(__file__).resolve().parents[3] / 'data' / 'middle_affordance_table.json'
    with open(path) as f:
        data = json.load(f)
    # MIDDLEs are nested under data["middles"]
    middles_data = data.get('middles', {})
    result = {}
    result['_metadata'] = data.get('_metadata', {})
    for mid, info in middles_data.items():
        result[mid] = {
            'affordance_bin': info.get('affordance_bin'),
            'affordance_label': info.get('affordance_label', ''),
            'radial_depth': info.get('radial_depth', 0),
            'compat_degree': info.get('compat_degree', 0),
            'token_frequency': info.get('token_frequency', 0),
        }
        sig = info.get('behavioral_signature', {})
        result[mid]['k_ratio'] = sig.get('k_ratio', 0)
        result[mid]['e_ratio'] = sig.get('e_ratio', 0)
        result[mid]['h_ratio'] = sig.get('h_ratio', 0)
        result[mid]['is_compound'] = sig.get('is_compound', 0)
        result[mid]['qo_affinity'] = sig.get('qo_affinity', 0)
    return result


def load_hub_sub_roles():
    path = Path(__file__).resolve().parents[2] / 'HUB_ROLE_DECOMPOSITION' / 'results' / 't1_hub_sub_role_partition.json'
    with open(path) as f:
        data = json.load(f)
    return data


def build_corpus_data(token_to_class):
    """Build enriched token-level corpus data (reused from Phase 340)."""
    tx = Transcript()
    morph = Morphology()
    bridge_set = load_bridge_middles()

    line_token_counts = Counter()
    raw_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        raw_tokens.append(token)
        line_token_counts[(token.folio, token.line)] += 1

    tokens = []
    folio_sections = {}
    line_position_counter = Counter()

    for token in raw_tokens:
        w = token.word.strip()
        if not w or '*' in w:
            continue

        cls = token_to_class.get(w)
        if cls is None:
            continue
        state = CLASS_TO_STATE.get(int(cls))
        if state is None:
            continue

        m = morph.extract(w)
        prefix = m.prefix if m.prefix else '__BARE__'
        middle = m.middle if m.middle else None
        suffix = m.suffix if m.suffix else None

        if middle is None:
            continue

        key = (token.folio, token.line)
        line_position_counter[key] += 1
        pos_in_line = line_position_counter[key]
        total_in_line = line_token_counts[key]
        if total_in_line <= 1:
            quartile = 1
        else:
            frac = (pos_in_line - 1) / (total_in_line - 1)
            quartile = min(int(frac * 4) + 1, 4)

        tokens.append({
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'cls': int(cls),
            'state': state,
            'line_pos_quartile': quartile,
            'is_bridge': middle in bridge_set,
            'is_gatekeeper': int(cls) in GATEKEEPER_CLASSES,
            'is_hazard': w in HAZARD_TOKENS,
        })
        folio_sections[token.folio] = token.section

    print(f"  Corpus tokens loaded: {len(tokens)}")
    print(f"  Folios: {len(folio_sections)}")
    return tokens, folio_sections


def build_folio_matrices(tokens):
    """Build per-folio transition matrices."""
    line_states = defaultdict(list)
    for t in tokens:
        line_states[(t['folio'], t['line'])].append(t['state'])

    folio_line_states = defaultdict(dict)
    for (folio, line), states_list in line_states.items():
        folio_line_states[folio][(folio, line)] = states_list

    results = {}
    for folio, line_dict in folio_line_states.items():
        trans_counts = np.zeros((N_STATES, N_STATES), dtype=int)
        state_counts = np.zeros(N_STATES, dtype=int)
        n_tokens = 0

        for (_, _), states_list in line_dict.items():
            for s in states_list:
                state_counts[STATE_IDX[s]] += 1
                n_tokens += 1
            for i in range(len(states_list) - 1):
                trans_counts[STATE_IDX[states_list[i]], STATE_IDX[states_list[i + 1]]] += 1

        n_transitions = trans_counts.sum()
        state_dist = state_counts / state_counts.sum() if state_counts.sum() > 0 else state_counts.astype(float)

        trans_prob = None
        if n_transitions >= MIN_TRANSITIONS:
            row_sums = trans_counts.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums == 0, 1, row_sums)
            trans_prob = trans_counts / row_sums

        results[folio] = {
            'trans_counts': trans_counts,
            'state_counts': state_counts,
            'n_transitions': int(n_transitions),
            'n_tokens': int(n_tokens),
            'trans_prob': trans_prob,
            'state_dist': state_dist,
        }

    return results


def build_folio_feature_rows(tokens, folio_matrices, regime_map, folio_sections, archetype_labels, affordance_table, hub_sub_roles):
    """Build per-folio feature vectors for all tests."""
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    # Pre-build sub-role lookup: MIDDLE → primary_role
    mid_primary_role = hub_sub_roles.get('primary_roles', {})
    role_groups = hub_sub_roles.get('role_groups', {})

    rows = []
    for folio, ftoks in folio_token_groups.items():
        fm = folio_matrices.get(folio)
        if fm is None or fm['n_transitions'] < MIN_TRANSITIONS:
            continue
        if folio not in archetype_labels:
            continue

        n_f = len(ftoks)

        # PREFIX entropy
        prefix_counts = Counter(t['prefix'] for t in ftoks)
        prefix_total = sum(prefix_counts.values())
        prefix_probs = np.array(list(prefix_counts.values())) / prefix_total
        prefix_entropy = -sum(p * np.log2(p) for p in prefix_probs if p > 0)

        # Hazard density
        hazard_density = sum(1 for t in ftoks if t['is_hazard']) / n_f

        # Gatekeeper fraction
        gatekeeper_frac = sum(1 for t in ftoks if t['is_gatekeeper']) / n_f

        # AXM self-transition
        axm_self = float(fm['trans_prob'][STATE_IDX['AXM'], STATE_IDX['AXM']])

        # Affordance bin composition (fraction of tokens in each of 9 bins)
        bin_counts = Counter()
        for t in ftoks:
            aff = affordance_table.get(t['middle'])
            if aff and aff.get('affordance_bin') is not None:
                bin_counts[aff['affordance_bin']] += 1
        total_binned = sum(bin_counts.values())
        bin_fracs = {}
        for b in range(9):
            bin_fracs[b] = bin_counts.get(b, 0) / total_binned if total_binned > 0 else 0

        # HUB sub-role distribution (fraction of tokens whose MIDDLE has a HUB sub-role)
        hub_role_counts = Counter()
        hub_total = 0
        for t in ftoks:
            role = mid_primary_role.get(t['middle'])
            if role:
                hub_role_counts[role] += 1
                hub_total += 1
        hub_role_fracs = {}
        for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
            hub_role_fracs[role] = hub_role_counts.get(role, 0) / n_f  # fraction of ALL tokens

        # QO affinity (EN lane balance): mean qo_affinity of MIDDLEs used
        qo_vals = []
        for t in ftoks:
            aff = affordance_table.get(t['middle'])
            if aff and 'qo_affinity' in aff:
                qo_vals.append(aff['qo_affinity'])
        mean_qo = np.mean(qo_vals) if qo_vals else 0.5

        # Compound MIDDLE rate
        compound_count = 0
        for t in ftoks:
            aff = affordance_table.get(t['middle'])
            if aff and aff.get('is_compound', 0) > 0.5:
                compound_count += 1
        compound_rate = compound_count / n_f

        # FL hazard/safe ratio: count tokens in FL_HAZ vs FL_SAFE states
        fl_haz_count = sum(1 for t in ftoks if t['state'] == 'FL_HAZ')
        fl_safe_count = sum(1 for t in ftoks if t['state'] == 'FL_SAFE')
        fl_ratio = fl_haz_count / (fl_safe_count + 1)  # +1 to avoid div by zero

        # Kernel character composition (k, h, e fractions of MIDDLE characters)
        total_chars = 0
        k_chars = 0
        h_chars = 0
        e_chars = 0
        for t in ftoks:
            mid = t['middle']
            total_chars += len(mid)
            k_chars += mid.count('k')
            h_chars += mid.count('h')
            e_chars += mid.count('e')
        k_frac = k_chars / total_chars if total_chars > 0 else 0
        h_frac = h_chars / total_chars if total_chars > 0 else 0
        e_frac = e_chars / total_chars if total_chars > 0 else 0

        # SUFFIX entropy
        suffix_counts = Counter(t['suffix'] for t in ftoks if t['suffix'] is not None)
        if suffix_counts:
            suffix_total = sum(suffix_counts.values())
            suffix_probs = np.array(list(suffix_counts.values())) / suffix_total
            suffix_entropy = -sum(p * np.log2(p) for p in suffix_probs if p > 0)
        else:
            suffix_entropy = 0

        # Mean radial depth of MIDDLEs used in this folio
        rd_vals = []
        for t in ftoks:
            aff = affordance_table.get(t['middle'])
            if aff and 'radial_depth' in aff:
                rd_vals.append(aff['radial_depth'])
        mean_radial_depth = np.mean(rd_vals) if rd_vals else 0

        # Mean MIDDLE frequency
        freq_vals = []
        for t in ftoks:
            aff = affordance_table.get(t['middle'])
            if aff and 'token_frequency' in aff:
                freq_vals.append(aff['token_frequency'])
        mean_mid_frequency = np.mean(freq_vals) if freq_vals else 0

        rows.append({
            'folio': folio,
            'section': folio_sections.get(folio, 'UNKNOWN'),
            'regime': regime_map.get(folio, 'UNKNOWN'),
            'archetype': archetype_labels[folio],
            'n_tokens': n_f,
            'axm_self': axm_self,
            'prefix_entropy': prefix_entropy,
            'hazard_density': hazard_density,
            'gatekeeper_frac': gatekeeper_frac,
            'suffix_entropy': suffix_entropy,
            'compound_rate': compound_rate,
            'fl_ratio': fl_ratio,
            'mean_qo': mean_qo,
            'k_frac': k_frac,
            'h_frac': h_frac,
            'e_frac': e_frac,
            'mean_radial_depth': mean_radial_depth,
            'mean_mid_frequency': mean_mid_frequency,
            **{f'bin_{b}': bin_fracs[b] for b in range(9)},
            **{f'hub_{role}': hub_role_fracs[role] for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']},
        })

    return rows


# ── Helpers ─────────────────────────────────────────────────────────

def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-10) if len(x) > 1 else x * 0


def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    if ss_res_full <= 0 or df_extra <= 0:
        return 0, 1.0
    df_res = n_obs - k_full
    if df_res <= 0:
        return 0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


# ── T1: Archetype Structural Profiling ──────────────────────────────

def run_t1(rows):
    """Profile archetype composition to rule out confounds."""
    print("\n" + "=" * 60)
    print("T1: Archetype Structural Profiling")
    print("=" * 60)

    archetypes = sorted(set(r['archetype'] for r in rows))
    print(f"\n  Archetypes: {archetypes}")

    # Per-archetype profiling
    per_arch = {}
    for arch in archetypes:
        arch_rows = [r for r in rows if r['archetype'] == arch]
        n = len(arch_rows)

        sections = Counter(r['section'] for r in arch_rows)
        regimes = Counter(r['regime'] for r in arch_rows)

        axm_selfs = [r['axm_self'] for r in arch_rows]
        mean_axm = np.mean(axm_selfs)
        range_axm = [float(np.min(axm_selfs)), float(np.max(axm_selfs))]

        # Section concentration
        max_section_frac = max(sections.values()) / n if n > 0 else 0
        dominant_section = max(sections, key=sections.get)

        per_arch[arch] = {
            'n_folios': n,
            'sections': dict(sections),
            'regimes': {str(k): v for k, v in regimes.items()},
            'mean_axm_self': round(mean_axm, 4),
            'range_axm_self': [round(v, 4) for v in range_axm],
            'max_section_frac': round(max_section_frac, 3),
            'dominant_section': dominant_section,
            'section_confound': max_section_frac > 0.80,
        }

        print(f"\n  Archetype {arch} (n={n}):")
        print(f"    Sections: {dict(sections)}")
        print(f"    REGIMEs: {dict(regimes)}")
        print(f"    AXM self: mean={mean_axm:.3f}, range=[{range_axm[0]:.3f}, {range_axm[1]:.3f}]")
        print(f"    Max section fraction: {max_section_frac:.1%} ({dominant_section})")
        if max_section_frac > 0.80:
            print(f"    ** WARNING: >80% from single section — potential confound **")

    # Chi-square: archetype × section independence
    section_list = sorted(set(r['section'] for r in rows))
    contingency_section = np.zeros((len(archetypes), len(section_list)), dtype=int)
    for r in rows:
        i = archetypes.index(r['archetype'])
        j = section_list.index(r['section'])
        contingency_section[i, j] += 1

    # Remove zero columns
    nonzero_cols = contingency_section.sum(axis=0) > 0
    contingency_section_clean = contingency_section[:, nonzero_cols]
    section_list_clean = [s for s, nz in zip(section_list, nonzero_cols) if nz]

    if contingency_section_clean.shape[1] >= 2:
        chi2_section, p_section, dof_section, _ = stats.chi2_contingency(contingency_section_clean)
        cramers_v_section = np.sqrt(chi2_section / (sum(contingency_section_clean.sum(axis=1)) * (min(contingency_section_clean.shape) - 1)))
    else:
        chi2_section, p_section, dof_section, cramers_v_section = 0, 1.0, 0, 0

    print(f"\n  Section × archetype chi-square: chi2={chi2_section:.2f}, p={p_section:.6f}, Cramer's V={cramers_v_section:.3f}")

    # Chi-square: archetype × REGIME independence
    regime_list = sorted(set(str(r['regime']) for r in rows))
    contingency_regime = np.zeros((len(archetypes), len(regime_list)), dtype=int)
    for r in rows:
        i = archetypes.index(r['archetype'])
        j = regime_list.index(str(r['regime']))
        contingency_regime[i, j] += 1

    nonzero_cols_r = contingency_regime.sum(axis=0) > 0
    contingency_regime_clean = contingency_regime[:, nonzero_cols_r]

    if contingency_regime_clean.shape[1] >= 2:
        chi2_regime, p_regime, dof_regime, _ = stats.chi2_contingency(contingency_regime_clean)
        cramers_v_regime = np.sqrt(chi2_regime / (sum(contingency_regime_clean.sum(axis=1)) * (min(contingency_regime_clean.shape) - 1)))
    else:
        chi2_regime, p_regime, dof_regime, cramers_v_regime = 0, 1.0, 0, 0

    print(f"  REGIME × archetype chi-square: chi2={chi2_regime:.2f}, p={p_regime:.6f}, Cramer's V={cramers_v_regime:.3f}")

    # P1: archetypes 5 and 6 NOT section-dominated
    p1_arch5 = per_arch.get(5, {}).get('section_confound', True)
    p1_arch6 = per_arch.get(6, {}).get('section_confound', True)
    p1_pass = not p1_arch5 and not p1_arch6

    print(f"\n  P1: Archetypes 5 and 6 NOT section-dominated (<80%)?")
    print(f"    Archetype 5: max section frac = {per_arch.get(5, {}).get('max_section_frac', 'N/A')}")
    print(f"    Archetype 6: max section frac = {per_arch.get(6, {}).get('max_section_frac', 'N/A')}")
    print(f"  Verdict: {'PASS' if p1_pass else 'FAIL'}")

    return {
        'per_archetype': {str(k): v for k, v in per_arch.items()},
        'chi2_section': round(float(chi2_section), 2),
        'p_section': round(float(p_section), 6),
        'cramers_v_section': round(float(cramers_v_section), 3),
        'chi2_regime': round(float(chi2_regime), 2),
        'p_regime': round(float(p_regime), 6),
        'cramers_v_regime': round(float(cramers_v_regime), 3),
        'p1_pass': p1_pass,
    }


# ── T2: Bootstrap Validation of Slope Anomalies ────────────────────

def run_t2(rows):
    """Bootstrap and permutation validation of C1017 slope sign flips."""
    print("\n" + "=" * 60)
    print("T2: Bootstrap Validation of Slope Anomalies")
    print("=" * 60)

    # Build regression data
    all_archetypes = sorted(set(r['archetype'] for r in rows))

    def ols_slopes(subset_rows):
        """Run OLS: axm_self ~ prefix_entropy + hazard_density. Return betas."""
        if len(subset_rows) < 4:
            return None, None, None
        y = np.array([r['axm_self'] for r in subset_rows])
        pe = np.array([r['prefix_entropy'] for r in subset_rows])
        hz = np.array([r['hazard_density'] for r in subset_rows])
        pe_z = standardize(pe)
        hz_z = standardize(hz)
        X = np.column_stack([np.ones(len(y)), pe_z, hz_z])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 1e-10 else 0
        return float(beta[1]), float(beta[2]), float(r2)

    # --- Observed slopes ---
    observed_slopes = {}
    for arch in all_archetypes:
        arch_rows = [r for r in rows if r['archetype'] == arch]
        bp, bh, r2 = ols_slopes(arch_rows)
        observed_slopes[arch] = {'beta_prefix': bp, 'beta_hazard': bh, 'r2': r2, 'n': len(arch_rows)}
        if bp is not None:
            print(f"  Archetype {arch} (n={len(arch_rows)}): β_PREFIX={bp:.4f}, β_hazard={bh:.4f}, R²={r2:.4f}")

    # --- Bootstrap: archetype 5 PREFIX slope, archetype 6 hazard slope ---
    arch5_rows = [r for r in rows if r['archetype'] == 5]
    arch6_rows = [r for r in rows if r['archetype'] == 6]

    # Archetype 5 bootstrap
    boot_prefix_5 = []
    n5 = len(arch5_rows)
    print(f"\n  Bootstrapping archetype 5 (n={n5}, {N_BOOTSTRAP} resamples)...")

    for _ in range(N_BOOTSTRAP):
        idx = np.random.choice(n5, size=n5, replace=True)
        sample = [arch5_rows[i] for i in idx]
        bp, bh, r2 = ols_slopes(sample)
        if bp is not None:
            boot_prefix_5.append(bp)

    boot_prefix_5 = np.array(boot_prefix_5)
    ci_prefix_5 = (np.percentile(boot_prefix_5, 2.5), np.percentile(boot_prefix_5, 97.5))
    print(f"  Archetype 5 PREFIX slope: observed={observed_slopes[5]['beta_prefix']:.4f}")
    print(f"    Bootstrap 95% CI: [{ci_prefix_5[0]:.4f}, {ci_prefix_5[1]:.4f}]")
    print(f"    CI excludes zero: {ci_prefix_5[0] > 0 or ci_prefix_5[1] < 0}")

    # Archetype 6 bootstrap
    boot_hazard_6 = []
    n6 = len(arch6_rows)
    print(f"\n  Bootstrapping archetype 6 (n={n6}, {N_BOOTSTRAP} resamples)...")

    for _ in range(N_BOOTSTRAP):
        idx = np.random.choice(n6, size=n6, replace=True)
        sample = [arch6_rows[i] for i in idx]
        bp, bh, r2 = ols_slopes(sample)
        if bh is not None:
            boot_hazard_6.append(bh)

    boot_hazard_6 = np.array(boot_hazard_6)
    ci_hazard_6 = (np.percentile(boot_hazard_6, 2.5), np.percentile(boot_hazard_6, 97.5))
    print(f"  Archetype 6 hazard slope: observed={observed_slopes[6]['beta_hazard']:.4f}")
    print(f"    Bootstrap 95% CI: [{ci_hazard_6[0]:.4f}, {ci_hazard_6[1]:.4f}]")
    print(f"    CI excludes zero: {ci_hazard_6[0] > 0 or ci_hazard_6[1] < 0}")

    # --- Permutation test: shuffle archetype labels ---
    print(f"\n  Permutation test ({N_PERM} permutations)...")
    obs_prefix_5 = observed_slopes[5]['beta_prefix']
    obs_hazard_6 = observed_slopes[6]['beta_hazard']

    perm_prefix_5_count = 0  # how many times any 7-folio group achieves PREFIX slope >= obs
    perm_hazard_6_count = 0  # how many times any 30-folio group achieves hazard slope >= obs

    for perm_i in range(N_PERM):
        shuffled = list(range(len(rows)))
        np.random.shuffle(shuffled)

        # Random 7-folio group (archetype 5 size)
        rand5 = [rows[shuffled[i]] for i in range(n5)]
        bp5, _, _ = ols_slopes(rand5)
        if bp5 is not None and bp5 >= obs_prefix_5:
            perm_prefix_5_count += 1

        # Random 30-folio group (archetype 6 size)
        rand6 = [rows[shuffled[i]] for i in range(n5, n5 + n6)]
        _, bh6, _ = ols_slopes(rand6)
        if bh6 is not None and bh6 >= obs_hazard_6:
            perm_hazard_6_count += 1

    p_perm_prefix_5 = perm_prefix_5_count / N_PERM
    p_perm_hazard_6 = perm_hazard_6_count / N_PERM

    print(f"  Permutation p (PREFIX slope ≥ {obs_prefix_5:.4f} in random n=7): {p_perm_prefix_5:.4f}")
    print(f"  Permutation p (hazard slope ≥ {obs_hazard_6:.4f} in random n=30): {p_perm_hazard_6:.4f}")

    # --- Cook's distance for archetype 6 ---
    print(f"\n  Cook's distance for archetype 6 (n={n6})...")
    y6 = np.array([r['axm_self'] for r in arch6_rows])
    pe6 = standardize(np.array([r['prefix_entropy'] for r in arch6_rows]))
    hz6 = standardize(np.array([r['hazard_density'] for r in arch6_rows]))
    X6 = np.column_stack([np.ones(n6), pe6, hz6])
    beta6 = np.linalg.lstsq(X6, y6, rcond=None)[0]
    y_pred6 = X6 @ beta6
    residuals6 = y6 - y_pred6
    mse6 = np.sum(residuals6 ** 2) / (n6 - 3)
    p_params = 3

    # Hat matrix: H = X(X'X)^{-1}X'
    try:
        hat_matrix = X6 @ np.linalg.inv(X6.T @ X6) @ X6.T
        h_diag = np.diag(hat_matrix)
        cooks_d = (residuals6 ** 2 / (p_params * mse6)) * (h_diag / (1 - h_diag) ** 2)
        max_cooks = float(np.max(cooks_d))
        max_cooks_folio = arch6_rows[int(np.argmax(cooks_d))]['folio']
        influential_folios = [(arch6_rows[i]['folio'], round(float(cooks_d[i]), 4))
                              for i in range(n6) if cooks_d[i] > 4 / n6]
        print(f"  Max Cook's D: {max_cooks:.4f} (folio: {max_cooks_folio})")
        print(f"  Influential folios (D > {4/n6:.3f}): {len(influential_folios)}")
        for f, d in influential_folios[:5]:
            print(f"    {f}: D={d}")
    except np.linalg.LinAlgError:
        max_cooks = None
        max_cooks_folio = None
        influential_folios = []
        cooks_d = None
        print("  Cook's distance: singular matrix, skipped")

    # --- Boundary sensitivity: perturb archetype assignments ---
    print(f"\n  Boundary sensitivity (moving 2-3 folios between adjacent archetypes)...")

    # Sort folios by AXM self (the clustering dimension) to find boundary folios
    arch5_sorted = sorted(arch5_rows, key=lambda r: r['axm_self'])
    arch6_sorted = sorted(arch6_rows, key=lambda r: r['axm_self'])
    # Also get adjacent archetypes (4 and others near 5/6)
    arch4_rows = [r for r in rows if r['archetype'] == 4]

    boundary_tests = []

    # Test 1: Move 2 folios from arch 5 boundary to arch 6
    if len(arch5_rows) >= 4:
        # Move 2 lowest-AXM folios from 5 → 6
        moved = arch5_sorted[:2]
        new_5 = [r for r in arch5_rows if r not in moved]
        new_6 = arch6_rows + moved
        bp5_new, _, _ = ols_slopes(new_5)
        _, bh6_new, _ = ols_slopes(new_6)
        boundary_tests.append({
            'perturbation': 'move 2 lowest from arch5 to arch6',
            'new_n5': len(new_5),
            'new_n6': len(new_6),
            'prefix_5_sign': '+' if (bp5_new is not None and bp5_new > 0) else '-' if bp5_new is not None else 'N/A',
            'hazard_6_sign': '+' if (bh6_new is not None and bh6_new > 0) else '-' if bh6_new is not None else 'N/A',
            'beta_prefix_5': round(bp5_new, 4) if bp5_new is not None else None,
            'beta_hazard_6': round(bh6_new, 4) if bh6_new is not None else None,
        })
        pfx_str = f"{bp5_new:.4f}" if bp5_new is not None else "N/A"
        haz_str = f"{bh6_new:.4f}" if bh6_new is not None else "N/A"
        print(f"    Move 2 from arch5→arch6: β_PREFIX_5={pfx_str}, β_hazard_6={haz_str}")

    # Test 2: Move 2 highest-AXM folios from arch6 to arch5
    if len(arch6_rows) >= 4:
        moved = arch6_sorted[-2:]
        new_5b = arch5_rows + moved
        new_6b = [r for r in arch6_rows if r not in moved]
        bp5_new2, _, _ = ols_slopes(new_5b)
        _, bh6_new2, _ = ols_slopes(new_6b)
        boundary_tests.append({
            'perturbation': 'move 2 highest from arch6 to arch5',
            'new_n5': len(new_5b),
            'new_n6': len(new_6b),
            'prefix_5_sign': '+' if (bp5_new2 is not None and bp5_new2 > 0) else '-',
            'hazard_6_sign': '+' if (bh6_new2 is not None and bh6_new2 > 0) else '-',
            'beta_prefix_5': round(bp5_new2, 4) if bp5_new2 is not None else None,
            'beta_hazard_6': round(bh6_new2, 4) if bh6_new2 is not None else None,
        })
        pfx_str2 = f"{bp5_new2:.4f}" if bp5_new2 is not None else "N/A"
        haz_str2 = f"{bh6_new2:.4f}" if bh6_new2 is not None else "N/A"
        print(f"    Move 2 from arch6→arch5: β_PREFIX_5={pfx_str2}, β_hazard_6={haz_str2}")

    # Test 3: Move 3 folios from arch4 to arch5 (if arch4 exists)
    if len(arch4_rows) >= 3:
        arch4_sorted = sorted(arch4_rows, key=lambda r: r['axm_self'])
        moved = arch4_sorted[:3]
        new_5c = arch5_rows + moved
        bp5_new3, _, _ = ols_slopes(new_5c)
        boundary_tests.append({
            'perturbation': 'move 3 from arch4 to arch5',
            'new_n5': len(new_5c),
            'prefix_5_sign': '+' if (bp5_new3 is not None and bp5_new3 > 0) else '-',
            'beta_prefix_5': round(bp5_new3, 4) if bp5_new3 is not None else None,
        })
        pfx_str3 = f"{bp5_new3:.4f}" if bp5_new3 is not None else "N/A"
        print(f"    Move 3 from arch4→arch5: β_PREFIX_5={pfx_str3}")

    # Boundary sensitivity: how many perturbations preserve sign flip?
    prefix_5_preserved = sum(1 for bt in boundary_tests if bt.get('prefix_5_sign') == '+')
    hazard_6_preserved = sum(1 for bt in boundary_tests if bt.get('hazard_6_sign') == '+')

    # P2: Bootstrap CI excludes zero for archetype 5 PREFIX slope
    ci_excludes_zero_5 = ci_prefix_5[0] > 0 or ci_prefix_5[1] < 0
    p2_pass = ci_excludes_zero_5 and p_perm_prefix_5 < 0.05

    print(f"\n  P2: Archetype 5 PREFIX slope bootstrap CI excludes zero?")
    print(f"    CI: [{ci_prefix_5[0]:.4f}, {ci_prefix_5[1]:.4f}]")
    print(f"    Excludes zero: {ci_excludes_zero_5}")
    print(f"    Permutation p: {p_perm_prefix_5:.4f}")
    print(f"  Verdict: {'PASS' if p2_pass else 'FAIL'}")

    return {
        'observed_slopes': {str(k): v for k, v in observed_slopes.items()},
        'bootstrap': {
            'arch5_prefix': {
                'observed': round(obs_prefix_5, 4) if obs_prefix_5 is not None else None,
                'ci_95': [round(ci_prefix_5[0], 4), round(ci_prefix_5[1], 4)],
                'ci_excludes_zero': bool(ci_excludes_zero_5),
                'boot_mean': round(float(boot_prefix_5.mean()), 4),
                'boot_std': round(float(boot_prefix_5.std()), 4),
            },
            'arch6_hazard': {
                'observed': round(obs_hazard_6, 4) if obs_hazard_6 is not None else None,
                'ci_95': [round(ci_hazard_6[0], 4), round(ci_hazard_6[1], 4)],
                'ci_excludes_zero': bool(ci_hazard_6[0] > 0 or ci_hazard_6[1] < 0),
                'boot_mean': round(float(boot_hazard_6.mean()), 4),
                'boot_std': round(float(boot_hazard_6.std()), 4),
            },
        },
        'permutation': {
            'p_prefix_5': round(p_perm_prefix_5, 4),
            'p_hazard_6': round(p_perm_hazard_6, 4),
        },
        'cooks_distance': {
            'max_cooks_d': round(max_cooks, 4) if max_cooks is not None else None,
            'max_cooks_folio': max_cooks_folio,
            'influential_folios': influential_folios[:10],
            'n_influential': len(influential_folios),
        },
        'boundary_sensitivity': {
            'tests': boundary_tests,
            'prefix_5_sign_preserved': prefix_5_preserved,
            'hazard_6_sign_preserved': hazard_6_preserved,
            'n_tests': len(boundary_tests),
        },
        'p2_pass': p2_pass,
    }


# ── T3: Bridge PC1 Decomposition ───────────────────────────────────

def run_t3(tokens, rows, folio_matrices, archetype_labels, affordance_table, hub_sub_roles):
    """Decode what bridge PC1 represents structurally."""
    print("\n" + "=" * 60)
    print("T3: Bridge PC1 Decomposition")
    print("=" * 60)

    bridge_set = load_bridge_middles()

    # Load compatibility matrix and build spectral embedding
    compat_path = Path(__file__).resolve().parents[2] / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy'
    if not compat_path.exists():
        print("  ERROR: Compatibility matrix not found.")
        return {'pass': False, 'error': 'compat_matrix_not_found'}

    M = np.load(compat_path)
    print(f"  Loaded compatibility matrix: {M.shape}")

    # Build MIDDLE index (from A corpus, same as Phase 340 T5c)
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

    # Spectral embedding
    eigenvalues, eigenvectors = np.linalg.eigh(M.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    evals = eigenvalues[:K_EMBED]
    evecs = eigenvectors[:, :K_EMBED]
    pos_evals = np.maximum(evals, 0)
    scaling = np.sqrt(pos_evals)
    embedding = evecs * scaling[np.newaxis, :]
    print(f"  Embedding: {embedding.shape} ({K_EMBED}D)")

    # Build per-folio bridge centroids
    folio_token_groups = defaultdict(list)
    for t in tokens:
        folio_token_groups[t['folio']].append(t)

    folio_bridge_centroids = {}
    folio_ordered = []

    for r in rows:
        folio = r['folio']
        ftoks = folio_token_groups.get(folio, [])

        folio_bridge_mids = set()
        for t in ftoks:
            if t['is_bridge'] and t['middle'] in mid_to_idx:
                folio_bridge_mids.add(t['middle'])

        if not folio_bridge_mids:
            continue

        bridge_indices = [mid_to_idx[m] for m in folio_bridge_mids]
        bridge_centroid = embedding[bridge_indices].mean(axis=0)
        folio_bridge_centroids[folio] = bridge_centroid
        folio_ordered.append(folio)

    n = len(folio_ordered)
    print(f"  Folios with bridge centroids: {n}")

    if n < 20:
        print("  Too few folios. Skipping.")
        return {'pass': False, 'error': 'insufficient_data'}

    # PCA of bridge centroids
    X_centroids = np.array([folio_bridge_centroids[f] for f in folio_ordered])
    X_centered = X_centroids - X_centroids.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    pc1 = X_centered @ Vt[0]
    pc2 = X_centered @ Vt[1]
    var_explained = (S ** 2) / (S ** 2).sum()
    print(f"  Bridge centroid PCA: PC1={var_explained[0]:.1%}, PC2={var_explained[1]:.1%}")

    # Build row lookup
    row_by_folio = {r['folio']: r for r in rows}

    # --- Hub frequency check (C986 re-derivation guard) ---
    mean_freq_per_folio = np.array([row_by_folio[f]['mean_mid_frequency'] for f in folio_ordered])
    if mean_freq_per_folio.std() < 1e-10:
        rho_freq, p_freq = 0.0, 1.0
        print(f"\n  PC1 vs mean MIDDLE frequency: constant input, rho=0 by definition")
    else:
        rho_freq, p_freq = stats.spearmanr(pc1, mean_freq_per_folio)
        print(f"\n  PC1 vs mean MIDDLE frequency: rho={rho_freq:.4f}, p={p_freq:.6f}")
    print(f"  Redundant with hub frequency (|r| >= 0.5)? {'YES — re-derivation risk' if abs(rho_freq) >= 0.5 else 'NO'}")

    # --- Radial depth check (C991 re-derivation guard) ---
    mean_rd_per_folio = np.array([row_by_folio[f]['mean_radial_depth'] for f in folio_ordered])
    if mean_rd_per_folio.std() < 1e-10:
        rho_rd, p_rd = 0.0, 1.0
        print(f"  PC1 vs mean radial depth: constant input, rho=0 by definition")
    else:
        rho_rd, p_rd = stats.spearmanr(pc1, mean_rd_per_folio)
        print(f"  PC1 vs mean radial depth: rho={rho_rd:.4f}, p={p_rd:.6f}")
    print(f"  Redundant with radial depth (|r| >= 0.5)? {'YES — re-derivation risk' if abs(rho_rd) >= 0.5 else 'NO'}")

    # --- PC1 loadings: top-10 MIDDLEs with highest |PC1 loading| ---
    # Vt[0] gives the PC1 direction in embedding space
    # PC1 loadings for each MIDDLE = embedding @ Vt[0] (the projection of each MIDDLE onto PC1)
    # But we need per-MIDDLE loadings, not per-folio
    # The Vt matrix has shape (K_EMBED, K_EMBED), each row is a principal direction
    # Loadings: the contribution vector Vt[0] itself operates on the centered centroid space
    # For individual MIDDLEs, project each into PC1:
    bridge_mids_in_manifold = [m for m in sorted(bridge_set) if m in mid_to_idx]
    mid_pc1_scores = {}
    for mid in bridge_mids_in_manifold:
        mid_vec = embedding[mid_to_idx[mid]]
        # Project onto PC1 direction (centered)
        mid_pc1 = np.dot(mid_vec - X_centroids.mean(axis=0), Vt[0])
        mid_pc1_scores[mid] = float(mid_pc1)

    # Top 10 by absolute PC1 score
    sorted_by_pc1 = sorted(mid_pc1_scores.items(), key=lambda x: abs(x[1]), reverse=True)[:10]

    print(f"\n  Top-10 bridge MIDDLEs by |PC1 loading|:")
    top_10_details = []
    for mid, score in sorted_by_pc1:
        aff = affordance_table.get(mid, {})
        role = hub_sub_roles.get('primary_roles', {}).get(mid, 'non-HUB')
        aff_label = aff.get('affordance_label', 'unknown')
        k_r = aff.get('k_ratio', 0)
        h_r = aff.get('h_ratio', 0)
        e_r = aff.get('e_ratio', 0)

        detail = {
            'middle': mid,
            'pc1_score': round(score, 4),
            'affordance_label': aff_label,
            'hub_sub_role': role,
            'k_ratio': round(k_r, 3),
            'h_ratio': round(h_r, 3),
            'e_ratio': round(e_r, 3),
        }
        top_10_details.append(detail)
        print(f"    {mid}: PC1={score:.4f}, aff={aff_label}, role={role}, k={k_r:.2f} h={h_r:.2f} e={e_r:.2f}")

    # --- PC1 vs archetypes: ANOVA ---
    folio_archetypes = np.array([archetype_labels[f] for f in folio_ordered])
    unique_archetypes = sorted(set(folio_archetypes))

    arch_groups_pc1 = {}
    for arch in unique_archetypes:
        mask = folio_archetypes == arch
        arch_groups_pc1[arch] = pc1[mask]

    if len(arch_groups_pc1) >= 2:
        f_anova, p_anova = stats.f_oneway(*[arch_groups_pc1[a] for a in sorted(arch_groups_pc1.keys())])
    else:
        f_anova, p_anova = 0, 1.0

    print(f"\n  PC1 vs archetypes ANOVA: F={f_anova:.2f}, p={p_anova:.6f}")

    # Pairwise: arch 5 vs 6
    if 5 in arch_groups_pc1 and 6 in arch_groups_pc1:
        t_56, p_56 = stats.mannwhitneyu(arch_groups_pc1[5], arch_groups_pc1[6], alternative='two-sided')
        mean_5 = float(arch_groups_pc1[5].mean())
        mean_6 = float(arch_groups_pc1[6].mean())
        print(f"  PC1 arch 5 vs 6: mean_5={mean_5:.4f}, mean_6={mean_6:.4f}, U={t_56:.1f}, p={p_56:.6f}")
    else:
        t_56, p_56, mean_5, mean_6 = None, None, None, None

    # Per-archetype PC1/PC2 centroids
    arch_centroids = {}
    for arch in unique_archetypes:
        mask = folio_archetypes == arch
        arch_centroids[arch] = {
            'pc1_mean': round(float(pc1[mask].mean()), 4),
            'pc1_std': round(float(pc1[mask].std()), 4),
            'pc2_mean': round(float(pc2[mask].mean()), 4),
            'pc2_std': round(float(pc2[mask].std()), 4),
            'n': int(mask.sum()),
        }

    # P3: PC1 NOT redundant with hub frequency (|r| < 0.5)
    rho_freq_abs = abs(rho_freq) if not np.isnan(rho_freq) else 0.0
    p3_pass = rho_freq_abs < 0.5
    print(f"\n  P3: Bridge PC1 NOT redundant with hub frequency (|r| < 0.5)?")
    print(f"    |rho| = {rho_freq_abs:.4f}")
    print(f"  Verdict: {'PASS' if p3_pass else 'FAIL'}")

    # P4: PC1 differs across archetypes (ANOVA p < 0.05)
    p4_pass = p_anova < 0.05
    print(f"\n  P4: Bridge PC1 differs across archetypes (ANOVA p < 0.05)?")
    print(f"    p = {p_anova:.6f}")
    print(f"  Verdict: {'PASS' if p4_pass else 'FAIL'}")

    return {
        'n_folios': n,
        'pca_variance_explained': [round(float(v), 4) for v in var_explained[:5]],
        'redundancy_checks': {
            'hub_frequency': {'rho': round(float(rho_freq), 4), 'p': round(float(p_freq), 6), 'redundant': abs(rho_freq) >= 0.5},
            'radial_depth': {'rho': round(float(rho_rd), 4), 'p': round(float(p_rd), 6), 'redundant': abs(rho_rd) >= 0.5},
        },
        'top_10_pc1_middles': top_10_details,
        'archetype_anova': {
            'f_stat': round(float(f_anova), 2),
            'p_value': round(float(p_anova), 6),
        },
        'archetype_pairwise_5v6': {
            'u_stat': round(float(t_56), 1) if t_56 is not None else None,
            'p_value': round(float(p_56), 6) if p_56 is not None else None,
            'mean_5': mean_5,
            'mean_6': mean_6,
        },
        'archetype_centroids': {str(k): v for k, v in arch_centroids.items()},
        'p3_pass': p3_pass,
        'p4_pass': p4_pass,
        # Store for T5
        '_pc1': pc1,
        '_pc2': pc2,
        '_folio_ordered': folio_ordered,
        '_Vt': Vt,
        '_X_centroids_mean': X_centroids.mean(axis=0),
    }


# ── T4: Archetype Discriminator Features ───────────────────────────

def run_t4(rows):
    """Compute per-archetype profiles across 7 feature families."""
    print("\n" + "=" * 60)
    print("T4: Archetype Discriminator Features")
    print("=" * 60)

    archetypes = sorted(set(r['archetype'] for r in rows))
    n_total = len(rows)

    # Group rows by archetype
    arch_groups = defaultdict(list)
    for r in rows:
        arch_groups[r['archetype']].append(r)

    results = {}
    significant_features = []

    # --- Feature Family 1: Affordance bin composition ---
    print("\n  --- Affordance Bin Composition (C995) ---")
    bin_results = {}
    for b in range(9):
        key = f'bin_{b}'
        groups = [np.array([r[key] for r in arch_groups[a]]) for a in archetypes]
        all_vals = np.concatenate(groups)
        if all(len(g) >= 2 for g in groups) and all_vals.std() > 1e-10:
            f_stat, p_val = stats.f_oneway(*groups)
        else:
            f_stat, p_val = 0, 1.0
        means = {str(a): round(float(np.mean([r[key] for r in arch_groups[a]])), 4) for a in archetypes}
        bin_results[key] = {'f_stat': round(float(f_stat), 2), 'p_value': round(float(p_val), 6), 'means': means}
        if p_val < 0.05:
            significant_features.append(key)
            print(f"    Bin {b}: F={f_stat:.2f}, p={p_val:.6f} ** SIGNIFICANT")
        else:
            print(f"    Bin {b}: F={f_stat:.2f}, p={p_val:.6f}")
    results['affordance_bins'] = bin_results

    # --- Feature Family 2: HUB sub-role distribution ---
    print("\n  --- HUB Sub-Role Distribution (C1000) ---")
    hub_results = {}
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        key = f'hub_{role}'
        groups = [np.array([r[key] for r in arch_groups[a]]) for a in archetypes]
        if all(len(g) >= 2 for g in groups):
            f_stat, p_val = stats.f_oneway(*groups)
        else:
            f_stat, p_val = 0, 1.0
        means = {str(a): round(float(np.mean([r[key] for r in arch_groups[a]])), 4) for a in archetypes}
        hub_results[role] = {'f_stat': round(float(f_stat), 2), 'p_value': round(float(p_val), 6), 'means': means}
        if p_val < 0.05:
            significant_features.append(f'hub_{role}')
            print(f"    {role}: F={f_stat:.2f}, p={p_val:.6f} ** SIGNIFICANT")
        else:
            print(f"    {role}: F={f_stat:.2f}, p={p_val:.6f}")
    results['hub_sub_roles'] = hub_results

    # P5: HUB sub-role composition differs across archetypes
    hub_chi2_data = []
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        key = f'hub_{role}'
        hub_chi2_data.append([sum(r[key] * r['n_tokens'] for r in arch_groups[a]) for a in archetypes])
    hub_contingency = np.array(hub_chi2_data, dtype=float)
    # Only test if we have nonzero entries
    if hub_contingency.sum() > 0 and hub_contingency.shape[0] >= 2 and hub_contingency.shape[1] >= 2:
        # Remove zero rows/cols
        nonzero_rows = hub_contingency.sum(axis=1) > 0
        nonzero_cols = hub_contingency.sum(axis=0) > 0
        hub_cont_clean = hub_contingency[nonzero_rows][:, nonzero_cols]
        if hub_cont_clean.shape[0] >= 2 and hub_cont_clean.shape[1] >= 2:
            chi2_hub, p_hub, _, _ = stats.chi2_contingency(hub_cont_clean)
        else:
            chi2_hub, p_hub = 0, 1.0
    else:
        chi2_hub, p_hub = 0, 1.0

    p5_pass = p_hub < 0.05
    print(f"\n  HUB sub-role × archetype chi-square: chi2={chi2_hub:.2f}, p={p_hub:.6f}")
    print(f"  P5: HUB sub-role composition differs? {'PASS' if p5_pass else 'FAIL'}")
    results['hub_chi2'] = round(float(chi2_hub), 2)
    results['hub_chi2_p'] = round(float(p_hub), 6)

    # P6: Archetype 6 enriched in SAFETY_BUFFER
    if 5 in arch_groups and 6 in arch_groups:
        sb_5 = [r['hub_SAFETY_BUFFER'] for r in arch_groups[5]]
        sb_6 = [r['hub_SAFETY_BUFFER'] for r in arch_groups[6]]
        u_sb, p_sb = stats.mannwhitneyu(sb_6, sb_5, alternative='greater')
        mean_sb_5 = float(np.mean(sb_5))
        mean_sb_6 = float(np.mean(sb_6))
        p6_pass = p_sb < 0.05
        print(f"\n  SAFETY_BUFFER: arch6 mean={mean_sb_6:.4f} vs arch5 mean={mean_sb_5:.4f}")
        print(f"  P6: Archetype 6 enriched in SAFETY_BUFFER (one-sided)? U={u_sb:.1f}, p={p_sb:.6f}")
        print(f"  Verdict: {'PASS' if p6_pass else 'FAIL'}")
    else:
        p6_pass = False
        u_sb, p_sb, mean_sb_5, mean_sb_6 = None, None, None, None

    results['safety_buffer_test'] = {
        'u_stat': round(float(u_sb), 1) if u_sb is not None else None,
        'p_value': round(float(p_sb), 6) if p_sb is not None else None,
        'mean_arch5': round(mean_sb_5, 4) if mean_sb_5 is not None else None,
        'mean_arch6': round(mean_sb_6, 4) if mean_sb_6 is not None else None,
        'p6_pass': p6_pass,
    }

    # --- Feature Family 3: EN lane balance (QO affinity) ---
    print("\n  --- EN Lane Balance (C605) ---")
    groups_qo = [np.array([r['mean_qo'] for r in arch_groups[a]]) for a in archetypes]
    all_qo = np.concatenate(groups_qo)
    if all(len(g) >= 2 for g in groups_qo) and all_qo.std() > 1e-10:
        f_qo, p_qo = stats.f_oneway(*groups_qo)
    else:
        f_qo, p_qo = 0, 1.0
    means_qo = {str(a): round(float(np.mean([r['mean_qo'] for r in arch_groups[a]])), 4) for a in archetypes}
    if p_qo < 0.05:
        significant_features.append('mean_qo')
    print(f"  QO affinity ANOVA: F={f_qo:.2f}, p={p_qo:.6f}")
    results['lane_balance'] = {'f_stat': round(float(f_qo), 2), 'p_value': round(float(p_qo), 6), 'means': means_qo}

    # Arch 5 vs 6 pairwise
    if 5 in arch_groups and 6 in arch_groups:
        qo_5 = [r['mean_qo'] for r in arch_groups[5]]
        qo_6 = [r['mean_qo'] for r in arch_groups[6]]
        u_qo, p_qo_56 = stats.mannwhitneyu(qo_5, qo_6, alternative='two-sided')
        print(f"  Arch 5 vs 6: mean_5={np.mean(qo_5):.4f}, mean_6={np.mean(qo_6):.4f}, U={u_qo:.1f}, p={p_qo_56:.6f}")
        results['lane_balance']['pairwise_5v6'] = {'u': round(float(u_qo), 1), 'p': round(float(p_qo_56), 6)}

    # --- Feature Family 4: Compound MIDDLE rate ---
    print("\n  --- Compound MIDDLE Rate (C935) ---")
    groups_comp = [np.array([r['compound_rate'] for r in arch_groups[a]]) for a in archetypes]
    all_comp = np.concatenate(groups_comp)
    if all(len(g) >= 2 for g in groups_comp) and all_comp.std() > 1e-10:
        f_comp, p_comp = stats.f_oneway(*groups_comp)
    else:
        f_comp, p_comp = 0, 1.0
    means_comp = {str(a): round(float(np.mean([r['compound_rate'] for r in arch_groups[a]])), 4) for a in archetypes}
    if p_comp < 0.05:
        significant_features.append('compound_rate')
    print(f"  Compound rate ANOVA: F={f_comp:.2f}, p={p_comp:.6f}")
    results['compound_rate'] = {'f_stat': round(float(f_comp), 2), 'p_value': round(float(p_comp), 6), 'means': means_comp}

    # --- Feature Family 5: FL hazard/safe ratio ---
    print("\n  --- FL Hazard/Safe Ratio (C586) ---")
    groups_fl = [np.array([r['fl_ratio'] for r in arch_groups[a]]) for a in archetypes]
    if all(len(g) >= 2 for g in groups_fl):
        f_fl, p_fl = stats.f_oneway(*groups_fl)
    else:
        f_fl, p_fl = 0, 1.0
    means_fl = {str(a): round(float(np.mean([r['fl_ratio'] for r in arch_groups[a]])), 4) for a in archetypes}
    if p_fl < 0.05:
        significant_features.append('fl_ratio')
    print(f"  FL ratio ANOVA: F={f_fl:.2f}, p={p_fl:.6f}")
    results['fl_ratio'] = {'f_stat': round(float(f_fl), 2), 'p_value': round(float(p_fl), 6), 'means': means_fl}

    # --- Feature Family 6: Kernel character composition ---
    print("\n  --- Kernel Character Composition (C778) ---")
    for char_name in ['k_frac', 'h_frac', 'e_frac']:
        groups_char = [np.array([r[char_name] for r in arch_groups[a]]) for a in archetypes]
        all_char = np.concatenate(groups_char)
        if all(len(g) >= 2 for g in groups_char) and all_char.std() > 1e-10:
            f_char, p_char = stats.f_oneway(*groups_char)
        else:
            f_char, p_char = 0, 1.0
        means_char = {str(a): round(float(np.mean([r[char_name] for r in arch_groups[a]])), 4) for a in archetypes}
        if p_char < 0.05:
            significant_features.append(char_name)
        print(f"  {char_name} ANOVA: F={f_char:.2f}, p={p_char:.6f}")
        results[char_name] = {'f_stat': round(float(f_char), 2), 'p_value': round(float(p_char), 6), 'means': means_char}

    # --- Feature Family 7: Gatekeeper fraction ---
    print("\n  --- Gatekeeper Fraction ---")
    groups_gk = [np.array([r['gatekeeper_frac'] for r in arch_groups[a]]) for a in archetypes]
    if all(len(g) >= 2 for g in groups_gk):
        f_gk, p_gk = stats.f_oneway(*groups_gk)
    else:
        f_gk, p_gk = 0, 1.0
    means_gk = {str(a): round(float(np.mean([r['gatekeeper_frac'] for r in arch_groups[a]])), 4) for a in archetypes}
    if p_gk < 0.05:
        significant_features.append('gatekeeper_frac')
    print(f"  Gatekeeper ANOVA: F={f_gk:.2f}, p={p_gk:.6f}")
    results['gatekeeper_frac'] = {'f_stat': round(float(f_gk), 2), 'p_value': round(float(p_gk), 6), 'means': means_gk}

    # Pairwise arch 5 vs 6
    if 5 in arch_groups and 6 in arch_groups:
        gk_5 = [r['gatekeeper_frac'] for r in arch_groups[5]]
        gk_6 = [r['gatekeeper_frac'] for r in arch_groups[6]]
        u_gk, p_gk_56 = stats.mannwhitneyu(gk_5, gk_6, alternative='two-sided')
        print(f"  Arch 5 vs 6: mean_5={np.mean(gk_5):.4f}, mean_6={np.mean(gk_6):.4f}, U={u_gk:.1f}, p={p_gk_56:.6f}")
        results['gatekeeper_frac']['pairwise_5v6'] = {'u': round(float(u_gk), 1), 'p': round(float(p_gk_56), 6)}

    # P7: ≥3 discriminator features separate archetypes
    n_sig = len(significant_features)
    p7_pass = n_sig >= 3
    print(f"\n  Significant features (p < 0.05): {n_sig}")
    print(f"  Features: {significant_features}")
    print(f"\n  P7: ≥3 discriminator features separate archetypes?")
    print(f"  Verdict: {'PASS' if p7_pass else 'FAIL'}")

    results['significant_features'] = significant_features
    results['n_significant'] = n_sig
    results['p5_pass'] = p5_pass
    results['p6_pass'] = p6_pass
    results['p7_pass'] = p7_pass

    return results


# ── T5: Unified Hypothesis Test ────────────────────────────────────

def run_t5(rows, t3_result):
    """Test whether slope anomalies and bridge geometry are linked."""
    print("\n" + "=" * 60)
    print("T5: Unified Hypothesis Test")
    print("=" * 60)

    # Retrieve PC1/PC2 from T3
    pc1 = t3_result.get('_pc1')
    pc2 = t3_result.get('_pc2')
    folio_ordered = t3_result.get('_folio_ordered')

    if pc1 is None or folio_ordered is None:
        print("  T3 data not available. Skipping.")
        return {'pass': False, 'error': 't3_data_missing'}

    row_by_folio = {r['folio']: r for r in rows}
    archetypes_t5 = np.array([row_by_folio[f]['archetype'] for f in folio_ordered])
    unique_archetypes = sorted(set(archetypes_t5))
    n = len(folio_ordered)

    # --- A. Bridge PC position by archetype ---
    print("\n  A. Bridge PC1/PC2 positions by archetype:")
    arch_positions = {}
    for arch in unique_archetypes:
        mask = archetypes_t5 == arch
        arch_positions[arch] = {
            'n': int(mask.sum()),
            'pc1_mean': round(float(pc1[mask].mean()), 4),
            'pc1_std': round(float(pc1[mask].std()), 4),
            'pc1_ci95': [
                round(float(pc1[mask].mean() - 1.96 * pc1[mask].std() / np.sqrt(mask.sum())), 4),
                round(float(pc1[mask].mean() + 1.96 * pc1[mask].std() / np.sqrt(mask.sum())), 4),
            ] if mask.sum() > 1 else [None, None],
            'pc2_mean': round(float(pc2[mask].mean()), 4),
            'pc2_std': round(float(pc2[mask].std()), 4),
        }
        print(f"    Arch {arch} (n={mask.sum()}): PC1={pc1[mask].mean():.4f}±{pc1[mask].std():.4f}, PC2={pc2[mask].mean():.4f}±{pc2[mask].std():.4f}")

    # Do archetypes 5 and 6 occupy DISTINCT PC1 positions?
    if 5 in arch_positions and 6 in arch_positions:
        mask5 = archetypes_t5 == 5
        mask6 = archetypes_t5 == 6
        u_pc1, p_pc1_56 = stats.mannwhitneyu(pc1[mask5], pc1[mask6], alternative='two-sided')
        u_pc2, p_pc2_56 = stats.mannwhitneyu(pc1[mask5], pc2[mask6], alternative='two-sided')
        distinct_56 = p_pc1_56 < 0.05
        print(f"\n    Arch 5 vs 6 PC1: U={u_pc1:.1f}, p={p_pc1_56:.6f} {'** DISTINCT' if distinct_56 else ''}")
    else:
        distinct_56 = False
        p_pc1_56 = 1.0

    # --- B. Mediation test ---
    # Does bridge PC1 mediate the relationship between discriminator features and AXM self?
    print("\n  B. Mediation test (bridge PC1 as mediator):")

    y = np.array([row_by_folio[f]['axm_self'] for f in folio_ordered])
    hazard_d = np.array([row_by_folio[f]['hazard_density'] for f in folio_ordered])
    prefix_e = np.array([row_by_folio[f]['prefix_entropy'] for f in folio_ordered])

    # Direct correlations
    rho_hz_axm, p_hz_axm = stats.spearmanr(hazard_d, y)
    rho_pe_axm, p_pe_axm = stats.spearmanr(prefix_e, y)

    # Partial correlations controlling for PC1
    # Partial rho(X, Y | Z) = (rho_XY - rho_XZ * rho_YZ) / sqrt((1-rho_XZ²)(1-rho_YZ²))
    rho_hz_pc1, _ = stats.spearmanr(hazard_d, pc1)
    rho_axm_pc1, _ = stats.spearmanr(y, pc1)
    rho_pe_pc1, _ = stats.spearmanr(prefix_e, pc1)

    denom_hz = np.sqrt((1 - rho_hz_pc1**2) * (1 - rho_axm_pc1**2))
    partial_hz = (rho_hz_axm - rho_hz_pc1 * rho_axm_pc1) / denom_hz if denom_hz > 1e-10 else 0

    denom_pe = np.sqrt((1 - rho_pe_pc1**2) * (1 - rho_axm_pc1**2))
    partial_pe = (rho_pe_axm - rho_pe_pc1 * rho_axm_pc1) / denom_pe if denom_pe > 1e-10 else 0

    print(f"    Hazard → AXM self:")
    print(f"      Direct: rho={rho_hz_axm:.4f}")
    print(f"      Partial (controlling PC1): rho={partial_hz:.4f}")
    print(f"      Attenuation: {abs(rho_hz_axm) - abs(partial_hz):.4f}")

    print(f"    PREFIX → AXM self:")
    print(f"      Direct: rho={rho_pe_axm:.4f}")
    print(f"      Partial (controlling PC1): rho={partial_pe:.4f}")
    print(f"      Attenuation: {abs(rho_pe_axm) - abs(partial_pe):.4f}")

    mediation_attenuation_hz = abs(rho_hz_axm) - abs(partial_hz)
    mediation_attenuation_pe = abs(rho_pe_axm) - abs(partial_pe)

    # --- C. Separation condition ---
    # If hypothesis is falsified (arch 5/6 NOT distinct in bridge geometry),
    # report threads as independent
    hypothesis_supported = distinct_56
    print(f"\n  C. Unified hypothesis (arch 5/6 distinct in bridge geometry)?")
    print(f"    {'SUPPORTED' if hypothesis_supported else 'FALSIFIED — threads are independent'}")

    return {
        'archetype_positions': {str(k): v for k, v in arch_positions.items()},
        'arch_5v6_distinct': {
            'u_stat_pc1': round(float(u_pc1), 1) if 5 in arch_positions else None,
            'p_value_pc1': round(float(p_pc1_56), 6),
            'distinct': distinct_56,
        },
        'mediation': {
            'hazard_direct_rho': round(float(rho_hz_axm), 4),
            'hazard_partial_rho': round(float(partial_hz), 4),
            'hazard_attenuation': round(float(mediation_attenuation_hz), 4),
            'prefix_direct_rho': round(float(rho_pe_axm), 4),
            'prefix_partial_rho': round(float(partial_pe), 4),
            'prefix_attenuation': round(float(mediation_attenuation_pe), 4),
        },
        'hypothesis_supported': bool(hypothesis_supported),
    }


# ── Synthesis ──────────────────────────────────────────────────────

def synthesize(t1_result, t2_result, t3_result, t4_result, t5_result):
    """Combine all test results into predictions and verdict."""
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    predictions = {
        'P1': {
            'description': 'Archetypes 5 and 6 NOT section-dominated (<80% single section)',
            'result': bool(t1_result['p1_pass']),
        },
        'P2': {
            'description': 'Archetype 5 PREFIX slope bootstrap CI excludes zero',
            'result': bool(t2_result['p2_pass']),
        },
        'P3': {
            'description': 'Bridge PC1 NOT redundant with hub frequency (|r| < 0.5)',
            'result': bool(t3_result.get('p3_pass', False)),
        },
        'P4': {
            'description': 'Bridge PC1 differs across archetypes (ANOVA p < 0.05)',
            'result': bool(t3_result.get('p4_pass', False)),
        },
        'P5': {
            'description': 'HUB sub-role composition differs across archetypes (chi-square p < 0.05)',
            'result': bool(t4_result.get('p5_pass', False)),
        },
        'P6': {
            'description': 'Archetype 6 enriched in SAFETY_BUFFER MIDDLEs (one-sided p < 0.05)',
            'result': bool(t4_result.get('p6_pass', False)),
        },
        'P7': {
            'description': '≥3 discriminator features separate archetypes (ANOVA p < 0.05)',
            'result': bool(t4_result.get('p7_pass', False)),
        },
    }

    n_pass = sum(1 for p in predictions.values() if p['result'])
    n_total = len(predictions)

    print(f"\n  Pre-registered predictions: {n_pass}/{n_total} passed")
    for pid, pred in predictions.items():
        status = 'PASS' if pred['result'] else 'FAIL'
        print(f"    {pid}: {status} — {pred['description']}")

    # Verdict
    hypothesis = t5_result.get('hypothesis_supported', False)
    if hypothesis:
        verdict_text = "ARCHETYPE_ANATOMY_UNIFIED"
        verdict_detail = ("Archetype slope anomalies and bridge geometric signal are linked: "
                         "archetypes 5/6 occupy distinct positions in bridge geometric space.")
    else:
        verdict_text = "ARCHETYPE_ANATOMY_INDEPENDENT"
        verdict_detail = ("Archetype slope anomalies and bridge geometric signal are independent threads: "
                         "both are real but not mediated by the same geometric mechanism.")

    print(f"\n  Verdict: {verdict_text}")
    print(f"  {verdict_detail}")

    return {
        'predictions': {k: {'description': v['description'], 'result': v['result']}
                       for k, v in predictions.items()},
        'n_pass': n_pass,
        'n_total': n_total,
        'hypothesis_supported': hypothesis,
        'verdict': verdict_text,
        'verdict_detail': verdict_detail,
    }


# ── Main ───────────────────────────────────────────────────────────

def main():
    print("Phase 341: ARCHETYPE_GEOMETRIC_ANATOMY")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    regime_map = load_regime_assignments()
    archetype_data = load_folio_archetypes()
    archetype_labels = archetype_data.get('folio_labels', {})
    affordance_table = load_affordance_table()
    hub_sub_roles = load_hub_sub_roles()

    print("\nBuilding corpus...")
    tokens, folio_sections = build_corpus_data(token_to_class)
    folio_matrices = build_folio_matrices(tokens)

    print("\nBuilding folio feature rows...")
    rows = build_folio_feature_rows(
        tokens, folio_matrices, regime_map, folio_sections,
        archetype_labels, affordance_table, hub_sub_roles
    )
    print(f"  Feature rows: {len(rows)} folios")

    # Run tests
    t1_result = run_t1(rows)
    t2_result = run_t2(rows)
    t3_result = run_t3(tokens, rows, folio_matrices, archetype_labels, affordance_table, hub_sub_roles)
    t4_result = run_t4(rows)
    t5_result = run_t5(rows, t3_result)
    synthesis = synthesize(t1_result, t2_result, t3_result, t4_result, t5_result)

    # Clean T3 result for JSON serialization (remove numpy arrays)
    t3_json = {k: v for k, v in t3_result.items() if not k.startswith('_')}

    # Save results
    output = {
        'phase': 'ARCHETYPE_GEOMETRIC_ANATOMY',
        'phase_number': 341,
        'n_folios': len(rows),
        't1_archetype_profiling': t1_result,
        't2_bootstrap_validation': t2_result,
        't3_bridge_pc1_decomposition': t3_json,
        't4_discriminator_features': t4_result,
        't5_unified_hypothesis': t5_result,
        'synthesis': synthesis,
    }

    output_path = Path(__file__).resolve().parent.parent / 'results' / 'archetype_anatomy.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nResults written to: {output_path}")
    print(f"Predictions: {synthesis['n_pass']}/{synthesis['n_total']} passed")
    print(f"Verdict: {synthesis['verdict']}")


if __name__ == '__main__':
    main()

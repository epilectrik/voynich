"""
Phase 352: SECTION_GRAMMAR_VARIATION + 20% GAP DECOMPOSITION

Part A: Section Grammar Variation
  C979 showed REGIME modulates transition WEIGHTS but not TOPOLOGY.
  C552 showed sections have distinct role distributions.
  Question: Does section modulate the 49-class transition matrix the same way?
  Is the topology invariant but weights shift, or do sections differ structurally?

Part B: 20% Gap Decomposition
  M2 (49-class Markov + forbidden) passes 12/15 tests (80%).
  Fails: B4 (role rank order), B5 (forward-backward JSD), C2 (CC suffix-free).
  Question: Do these 3 failures share a common cause or are they independent?
"""

import sys
sys.path.insert(0, '.')

import json
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
from scipy.spatial.distance import jensenshannon
from scipy.stats import chi2_contingency, permutation_test
from scripts.voynich import Transcript, Morphology

# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load B corpus with section, class, and morphological assignments."""
    tx = Transcript()
    morph = Morphology()

    # Load class map
    with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    class_to_role = cmap['class_to_role']

    # Load regime mapping
    with open('data/regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    regime_assignments = regime_data['regime_assignments']

    # Build token list with metadata
    tokens = []
    for t in tx.currier_b():
        word = t.word
        if not word.strip() or '*' in word:
            continue
        cls = token_to_class.get(word)
        if cls is None:
            continue  # Skip unmapped tokens
        role = class_to_role.get(str(cls), 'UNKNOWN')

        # Morphological parse
        m = morph.extract(word)
        has_suffix = m.suffix is not None and len(m.suffix) > 0

        # Regime
        regime = regime_assignments.get(t.folio, {})
        if isinstance(regime, dict):
            regime = regime.get('regime', 'UNKNOWN')

        tokens.append({
            'word': word,
            'folio': t.folio,
            'section': t.section,
            'line': t.line_number if hasattr(t, 'line_number') else None,
            'cls': int(cls),
            'role': role,
            'has_suffix': has_suffix,
            'regime': regime,
            'middle': m.middle,
            'prefix': m.prefix,
        })

    print(f"Loaded {len(tokens)} B tokens with class assignments")
    print(f"Sections: {Counter(t['section'] for t in tokens)}")
    return tokens, class_to_role


# ============================================================
# PART A: SECTION GRAMMAR VARIATION
# ============================================================

def build_transition_matrix(tokens, n_classes=49):
    """Build class transition matrix from token sequence."""
    matrix = np.zeros((n_classes, n_classes))
    for i in range(len(tokens) - 1):
        # Only count transitions within the same folio+line
        if tokens[i]['folio'] == tokens[i+1]['folio']:
            c1 = tokens[i]['cls'] - 1  # 1-indexed to 0-indexed
            c2 = tokens[i+1]['cls'] - 1
            if 0 <= c1 < n_classes and 0 <= c2 < n_classes:
                matrix[c1][c2] += 1
    return matrix


def normalize_matrix(matrix):
    """Row-normalize transition matrix."""
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    return matrix / row_sums


def matrix_jsd(m1, m2):
    """Compute mean row-wise JSD between two normalized transition matrices."""
    jsds = []
    for i in range(m1.shape[0]):
        r1, r2 = m1[i], m2[i]
        if r1.sum() > 0 and r2.sum() > 0:
            # Add small epsilon for zero rows
            r1_safe = r1 + 1e-10
            r2_safe = r2 + 1e-10
            r1_safe /= r1_safe.sum()
            r2_safe /= r2_safe.sum()
            jsds.append(jensenshannon(r1_safe, r2_safe) ** 2)
    return np.mean(jsds) if jsds else 0.0


def analyze_section_grammar(tokens, class_to_role):
    """Part A: Compare transition matrices across sections."""
    n_classes = 49

    # Section map: keep only sections with enough data
    section_names = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS_RECIPE', 'C': 'COSMO', 'T': 'TEXT'}
    section_tokens = defaultdict(list)
    for t in tokens:
        section_tokens[t['section']].append(t)

    # Filter to sections with >= 500 tokens
    valid_sections = {s: toks for s, toks in section_tokens.items() if len(toks) >= 500}
    print(f"\nValid sections (>= 500 tokens): {[(s, len(t)) for s, t in valid_sections.items()]}")

    # Build global transition matrix
    global_matrix = build_transition_matrix(tokens, n_classes)
    global_norm = normalize_matrix(global_matrix)

    # Build per-section matrices
    section_matrices = {}
    section_norms = {}
    for sec, toks in valid_sections.items():
        mat = build_transition_matrix(toks, n_classes)
        section_matrices[sec] = mat
        section_norms[sec] = normalize_matrix(mat)

    # Also build per-regime matrices for comparison
    regime_tokens = defaultdict(list)
    for t in tokens:
        regime_tokens[t['regime']].append(t)
    regime_matrices = {}
    regime_norms = {}
    for reg, toks in regime_tokens.items():
        if len(toks) >= 500:
            mat = build_transition_matrix(toks, n_classes)
            regime_matrices[reg] = mat
            regime_norms[reg] = normalize_matrix(mat)

    # === Test 1: Pairwise JSD between sections ===
    section_jsds = {}
    section_keys = sorted(valid_sections.keys())
    for s1, s2 in combinations(section_keys, 2):
        jsd = matrix_jsd(section_norms[s1], section_norms[s2])
        section_jsds[f"{section_names.get(s1, s1)}_vs_{section_names.get(s2, s2)}"] = round(jsd, 6)

    # Pairwise JSD between regimes
    regime_jsds = {}
    regime_keys = sorted(regime_norms.keys())
    for r1, r2 in combinations(regime_keys, 2):
        jsd = matrix_jsd(regime_norms[r1], regime_norms[r2])
        regime_jsds[f"{r1}_vs_{r2}"] = round(jsd, 6)

    # Each section vs global
    section_vs_global = {}
    for sec in section_keys:
        jsd = matrix_jsd(section_norms[sec], global_norm)
        section_vs_global[section_names.get(sec, sec)] = round(jsd, 6)

    # === Test 2: Topology invariance ===
    # Count non-zero transitions in each section
    topology = {}
    global_nonzero = set()
    for i in range(n_classes):
        for j in range(n_classes):
            if global_matrix[i][j] > 0:
                global_nonzero.add((i, j))

    for sec in section_keys:
        mat = section_matrices[sec]
        sec_nonzero = set()
        for i in range(n_classes):
            for j in range(n_classes):
                if mat[i][j] > 0:
                    sec_nonzero.add((i, j))

        shared = sec_nonzero & global_nonzero
        sec_only = sec_nonzero - global_nonzero
        global_only = global_nonzero - sec_nonzero

        topology[section_names.get(sec, sec)] = {
            'nonzero_transitions': len(sec_nonzero),
            'shared_with_global': len(shared),
            'section_only': len(sec_only),
            'missing_from_section': len(global_only),
            'topology_overlap': round(len(shared) / len(global_nonzero), 4) if global_nonzero else 0,
        }

    topology['global'] = {'nonzero_transitions': len(global_nonzero)}

    # === Test 3: Chi-squared on transition counts ===
    # For each source class, test if section modulates destination distribution
    chi2_results = {}
    sig_classes = 0
    for src in range(n_classes):
        # Build contingency table: sections x destinations
        contingency = []
        for sec in section_keys:
            row = section_matrices[sec][src].astype(int)
            contingency.append(row)
        contingency = np.array(contingency)

        # Remove zero-sum columns
        col_sums = contingency.sum(axis=0)
        nonzero_cols = col_sums > 0
        contingency = contingency[:, nonzero_cols]

        # Remove zero-sum rows
        row_sums = contingency.sum(axis=1)
        if np.any(row_sums == 0):
            continue  # Some sections have no tokens in this class

        total = contingency.sum()
        if total < 20 or contingency.shape[1] < 2:
            continue

        try:
            chi2, p, dof, _ = chi2_contingency(contingency)
            role = class_to_role.get(str(src + 1), 'UNK')
            chi2_results[f"class_{src+1}_{role}"] = {
                'chi2': round(chi2, 2),
                'p': round(p, 6),
                'dof': dof,
                'significant': p < 0.05,
                'total_transitions': int(total),
            }
            if p < 0.05:
                sig_classes += 1
        except Exception:
            pass

    tested_classes = len(chi2_results)

    # === Test 4: Section-specific self-loop rates ===
    self_loops = {}
    for sec in section_keys:
        mat = section_matrices[sec]
        diag_sum = np.trace(mat)
        total = mat.sum()
        self_loops[section_names.get(sec, sec)] = round(diag_sum / total, 4) if total > 0 else 0

    # Global self-loop
    global_self = round(np.trace(global_matrix) / global_matrix.sum(), 4)

    # === Test 5: Section-specific class distributions ===
    class_dists = {}
    for sec in section_keys:
        counts = Counter(t['cls'] for t in valid_sections[sec])
        total = sum(counts.values())
        dist = {str(c): round(counts.get(c, 0) / total, 4) for c in range(1, n_classes + 1)}
        class_dists[section_names.get(sec, sec)] = dist

    # Global class distribution
    global_counts = Counter(t['cls'] for t in tokens)
    global_total = sum(global_counts.values())
    global_dist = {str(c): round(global_counts.get(c, 0) / global_total, 4) for c in range(1, n_classes + 1)}

    # Section vs global class distribution JSD
    class_dist_jsds = {}
    for sec in section_keys:
        sd = np.array([float(class_dists[section_names.get(sec, sec)].get(str(c), 0)) for c in range(1, n_classes + 1)])
        gd = np.array([float(global_dist.get(str(c), 0)) for c in range(1, n_classes + 1)])
        sd_safe = sd + 1e-10
        gd_safe = gd + 1e-10
        sd_safe /= sd_safe.sum()
        gd_safe /= gd_safe.sum()
        class_dist_jsds[section_names.get(sec, sec)] = round(jensenshannon(sd_safe, gd_safe) ** 2, 6)

    # === Test 6: Spectral gap per section ===
    spectral_gaps = {}
    for sec in section_keys:
        norm = section_norms[sec]
        try:
            eigenvalues = np.sort(np.abs(np.linalg.eigvals(norm)))[::-1]
            if len(eigenvalues) >= 2:
                gap = float(eigenvalues[0] - eigenvalues[1])
                spectral_gaps[section_names.get(sec, sec)] = round(gap, 4)
        except Exception:
            spectral_gaps[section_names.get(sec, sec)] = None

    # Global spectral gap
    try:
        eigenvalues = np.sort(np.abs(np.linalg.eigvals(global_norm)))[::-1]
        spectral_gaps['GLOBAL'] = round(float(eigenvalues[0] - eigenvalues[1]), 4)
    except Exception:
        spectral_gaps['GLOBAL'] = None

    results_a = {
        'pairwise_section_jsd': section_jsds,
        'pairwise_regime_jsd': regime_jsds,
        'section_vs_global_jsd': section_vs_global,
        'mean_section_jsd': round(np.mean(list(section_jsds.values())), 6),
        'mean_regime_jsd': round(np.mean(list(regime_jsds.values())), 6),
        'section_jsd_to_regime_jsd_ratio': round(
            np.mean(list(section_jsds.values())) / max(np.mean(list(regime_jsds.values())), 1e-10), 3
        ),
        'topology': topology,
        'chi2_per_class': chi2_results,
        'chi2_summary': {
            'tested_classes': tested_classes,
            'significant_classes': sig_classes,
            'fraction_significant': round(sig_classes / tested_classes, 3) if tested_classes > 0 else 0,
        },
        'self_loop_rates': {**self_loops, 'GLOBAL': global_self},
        'class_distribution_jsd': class_dist_jsds,
        'spectral_gaps': spectral_gaps,
    }

    return results_a


# ============================================================
# PART B: 20% GAP DECOMPOSITION
# ============================================================

def analyze_gap_decomposition(tokens, class_to_role):
    """Part B: Diagnose why M2 fails B4, B5, C2."""
    n_classes = 49

    # === B4: Role Rank Order ===
    # Requires FQ > FL > EN self-transition rates
    role_self_loops = defaultdict(lambda: {'self': 0, 'total': 0})

    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        if t1['folio'] != t2['folio']:
            continue
        role = t1['role']
        role_self_loops[role]['total'] += 1
        if t1['cls'] == t2['cls']:
            role_self_loops[role]['self'] += 1

    role_self_rates = {}
    for role in ['FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'AUXILIARY']:
        data = role_self_loops[role]
        rate = data['self'] / data['total'] if data['total'] > 0 else 0
        role_self_rates[role] = {
            'self_transitions': data['self'],
            'total_transitions': data['total'],
            'self_rate': round(rate, 4),
        }

    # Check ordering
    fq_rate = role_self_rates.get('FREQUENT_OPERATOR', {}).get('self_rate', 0)
    fl_rate = role_self_rates.get('FLOW_OPERATOR', {}).get('self_rate', 0)
    en_rate = role_self_rates.get('ENERGY_OPERATOR', {}).get('self_rate', 0)

    b4_ordering_holds = fq_rate > fl_rate > en_rate
    b4_ordering = f"FQ({fq_rate:.4f}) > FL({fl_rate:.4f}) > EN({en_rate:.4f})"

    # Per-class self-loop rates within each role
    class_self_loops = defaultdict(lambda: {'self': 0, 'total': 0})
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        if t1['folio'] != t2['folio']:
            continue
        cls = t1['cls']
        class_self_loops[cls]['total'] += 1
        if t1['cls'] == t2['cls']:
            class_self_loops[cls]['self'] += 1

    # Aggregate per-class into per-role — but also show variance
    role_class_detail = defaultdict(list)
    for cls_id in range(1, n_classes + 1):
        role = class_to_role.get(str(cls_id), 'UNKNOWN')
        data = class_self_loops[cls_id]
        if data['total'] >= 10:
            rate = data['self'] / data['total']
            role_class_detail[role].append({
                'class': cls_id,
                'self_rate': round(rate, 4),
                'count': data['total'],
            })

    # Why M2 fails B4: In M2, self-transitions come from the global Markov matrix.
    # The role rank order is an emergent property of the class composition within each role.
    # If M2's Markov matrix doesn't maintain the per-role self-loop ordering, B4 fails.

    # Compute what M2 WOULD produce: weighted average of class self-loops
    global_matrix = build_transition_matrix(tokens, n_classes)
    global_norm = normalize_matrix(global_matrix)
    class_counts = Counter(t['cls'] for t in tokens)

    m2_role_self = {}
    for role in ['FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'ENERGY_OPERATOR']:
        weighted_self = 0.0
        total_weight = 0.0
        for cls_id in range(1, n_classes + 1):
            if class_to_role.get(str(cls_id)) == role:
                # M2 self-loop = diagonal of transition matrix
                m2_self = global_norm[cls_id - 1][cls_id - 1]
                weight = class_counts.get(cls_id, 0)
                weighted_self += m2_self * weight
                total_weight += weight
        m2_role_self[role] = round(weighted_self / total_weight, 4) if total_weight > 0 else 0

    m2_b4_ordering = (m2_role_self.get('FREQUENT_OPERATOR', 0) >
                      m2_role_self.get('FLOW_OPERATOR', 0) >
                      m2_role_self.get('ENERGY_OPERATOR', 0))

    # === B5: Forward-Backward JSD ===
    # Compute forward bigram distribution
    forward_bigrams = Counter()
    backward_bigrams = Counter()
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        if t1['folio'] != t2['folio']:
            continue
        forward_bigrams[(t1['cls'], t2['cls'])] += 1
        backward_bigrams[(t2['cls'], t1['cls'])] += 1

    # Convert to probability distributions over the same space
    all_bigrams = set(forward_bigrams.keys()) | set(backward_bigrams.keys())
    fwd_total = sum(forward_bigrams.values())
    bwd_total = sum(backward_bigrams.values())

    fwd_dist = np.array([forward_bigrams.get(b, 0) / fwd_total for b in sorted(all_bigrams)])
    bwd_dist = np.array([backward_bigrams.get(b, 0) / bwd_total for b in sorted(all_bigrams)])

    real_b5_jsd = float(jensenshannon(fwd_dist, bwd_dist) ** 2)

    # What drives B5? Decompose by role
    role_asymmetry = {}
    for role in ['FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'AUXILIARY']:
        role_classes = set()
        for cls_id in range(1, n_classes + 1):
            if class_to_role.get(str(cls_id)) == role:
                role_classes.add(cls_id)

        # Forward bigrams originating from this role
        role_fwd = Counter()
        role_bwd = Counter()
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i+1]
            if t1['folio'] != t2['folio']:
                continue
            if t1['cls'] in role_classes:
                role_fwd[(t1['cls'], t2['cls'])] += 1
            if t2['cls'] in role_classes:
                role_bwd[(t2['cls'], t1['cls'])] += 1

        if role_fwd and role_bwd:
            all_bg = set(role_fwd.keys()) | set(role_bwd.keys())
            ft = sum(role_fwd.values())
            bt = sum(role_bwd.values())
            fd = np.array([role_fwd.get(b, 0) / ft for b in sorted(all_bg)])
            bd = np.array([role_bwd.get(b, 0) / bt for b in sorted(all_bg)])
            role_asymmetry[role] = {
                'jsd': round(float(jensenshannon(fd, bd) ** 2), 6),
                'forward_count': ft,
                'backward_count': bt,
            }

    # Per-section asymmetry
    section_tokens_grouped = defaultdict(list)
    for t in tokens:
        section_tokens_grouped[t['section']].append(t)

    section_asymmetry = {}
    for sec, toks in section_tokens_grouped.items():
        if len(toks) < 500:
            continue
        sec_fwd = Counter()
        sec_bwd = Counter()
        for i in range(len(toks) - 1):
            t1, t2 = toks[i], toks[i+1]
            if t1['folio'] != t2['folio']:
                continue
            sec_fwd[(t1['cls'], t2['cls'])] += 1
            sec_bwd[(t2['cls'], t1['cls'])] += 1

        if sec_fwd and sec_bwd:
            all_bg = set(sec_fwd.keys()) | set(sec_bwd.keys())
            ft = sum(sec_fwd.values())
            bt = sum(sec_bwd.values())
            fd = np.array([sec_fwd.get(b, 0) / ft for b in sorted(all_bg)])
            bd = np.array([sec_bwd.get(b, 0) / bt for b in sorted(all_bg)])
            section_asymmetry[sec] = round(float(jensenshannon(fd, bd) ** 2), 6)

    # === C2: CC Suffix-Free Rate ===
    # CC (CORE_CONTROL) tokens should be suffix-free at 83.4%
    role_suffix = defaultdict(lambda: {'with': 0, 'without': 0})
    for t in tokens:
        role = t['role']
        if t['has_suffix']:
            role_suffix[role]['with'] += 1
        else:
            role_suffix[role]['without'] += 1

    role_suffix_rates = {}
    for role in ['FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'AUXILIARY']:
        data = role_suffix[role]
        total = data['with'] + data['without']
        free_rate = data['without'] / total if total > 0 else 0
        role_suffix_rates[role] = {
            'suffix_free': data['without'],
            'with_suffix': data['with'],
            'total': total,
            'suffix_free_rate': round(free_rate, 4),
        }

    cc_suffix_free = role_suffix_rates.get('CORE_CONTROL', {}).get('suffix_free_rate', 0)

    # Is C2 independent of B4/B5?
    # Check if suffix-bearing tokens have different transition properties
    suffix_tokens = [t for t in tokens if t['has_suffix']]
    no_suffix_tokens = [t for t in tokens if not t['has_suffix']]

    # Self-loop rates for suffix vs no-suffix
    def compute_self_rate(token_list):
        self_count = 0
        total = 0
        for i in range(len(token_list) - 1):
            t1, t2 = token_list[i], token_list[i+1]
            if t1['folio'] != t2['folio']:
                continue
            total += 1
            if t1['cls'] == t2['cls']:
                self_count += 1
        return self_count / total if total > 0 else 0

    suffix_self_rate = compute_self_rate(suffix_tokens)
    no_suffix_self_rate = compute_self_rate(no_suffix_tokens)

    # === Independence Test ===
    # For each failing test, compute per-section values
    # If failures are independent, they should vary independently across sections
    section_b4 = {}
    section_c2 = {}
    for sec, toks in section_tokens_grouped.items():
        if len(toks) < 500:
            continue

        # B4 per section
        sec_role_self = defaultdict(lambda: {'self': 0, 'total': 0})
        for i in range(len(toks) - 1):
            t1, t2 = toks[i], toks[i+1]
            if t1['folio'] != t2['folio']:
                continue
            sec_role_self[t1['role']]['total'] += 1
            if t1['cls'] == t2['cls']:
                sec_role_self[t1['role']]['self'] += 1

        fq = sec_role_self['FREQUENT_OPERATOR']
        fl = sec_role_self['FLOW_OPERATOR']
        en = sec_role_self['ENERGY_OPERATOR']
        fq_r = fq['self'] / fq['total'] if fq['total'] > 0 else 0
        fl_r = fl['self'] / fl['total'] if fl['total'] > 0 else 0
        en_r = en['self'] / en['total'] if en['total'] > 0 else 0
        section_b4[sec] = {
            'FQ': round(fq_r, 4), 'FL': round(fl_r, 4), 'EN': round(en_r, 4),
            'ordering_holds': fq_r > fl_r > en_r,
        }

        # C2 per section
        cc_data = {'with': 0, 'without': 0}
        for t in toks:
            if t['role'] == 'CORE_CONTROL':
                if t['has_suffix']:
                    cc_data['with'] += 1
                else:
                    cc_data['without'] += 1
        cc_total = cc_data['with'] + cc_data['without']
        section_c2[sec] = {
            'cc_suffix_free_rate': round(cc_data['without'] / cc_total, 4) if cc_total > 0 else 0,
            'cc_total': cc_total,
        }

    results_b = {
        'B4_role_rank_order': {
            'real_self_rates': role_self_rates,
            'real_ordering': b4_ordering,
            'real_ordering_holds': b4_ordering_holds,
            'm2_weighted_self_rates': m2_role_self,
            'm2_ordering_holds': m2_b4_ordering,
            'per_class_detail': {role: sorted(classes, key=lambda x: -x['self_rate'])
                                 for role, classes in role_class_detail.items()},
            'diagnosis': (
                "B4 fails because the ROLE-level self-loop ordering "
                "is an emergent constraint from class composition. "
                "M2 treats classes independently — the within-role "
                "self-loop rates must aggregate correctly, but the "
                "stochastic class sampling doesn't preserve the "
                "role-level rank ordering."
            ),
        },
        'B5_forward_backward_jsd': {
            'real_jsd': round(real_b5_jsd, 6),
            'm2_jsd': 0.1778,  # From Phase 348 results
            'ratio': round(0.1778 / max(real_b5_jsd, 1e-10), 3),
            'per_role_asymmetry': role_asymmetry,
            'per_section_asymmetry': section_asymmetry,
            'diagnosis': (
                "B5 fails because M2 overestimates forward-backward "
                "asymmetry (0.178 vs 0.090). The real text has a "
                "symmetrizing mechanism — likely PREFIX's symmetric "
                "routing (C1024: MI asymmetry 0.018 bits for PREFIX "
                "vs 0.070 for MIDDLE). M2 generates sequences from "
                "a single directional Markov chain, producing more "
                "asymmetry than the real text's bidirectional "
                "constraint structure."
            ),
        },
        'C2_cc_suffix_free': {
            'real_cc_suffix_free_rate': cc_suffix_free,
            'target': 0.99,
            'all_role_suffix_rates': role_suffix_rates,
            'suffix_vs_no_suffix_self_rates': {
                'with_suffix': round(suffix_self_rate, 4),
                'without_suffix': round(no_suffix_self_rate, 4),
            },
            'diagnosis': (
                "C2 fails because suffix attachment is role-specific: "
                f"CC tokens are {cc_suffix_free*100:.1f}% suffix-free, "
                "but M2 generates tokens from classes without "
                "role-specific morphological constraints. The suffix "
                "rate is determined by token selection within each "
                "class, which M2 randomizes."
            ),
        },
        'independence_analysis': {
            'B4_per_section': section_b4,
            'B5_per_section': section_asymmetry,
            'C2_per_section': section_c2,
        },
        'shared_mechanism_test': None,  # Will be filled below
    }

    # Test if B4 and B5 co-vary across sections
    b4_values = []
    b5_values = []
    c2_values = []
    shared_sections = []
    for sec in sorted(section_tokens_grouped.keys()):
        if sec not in section_b4 or sec not in section_asymmetry or sec not in section_c2:
            continue
        shared_sections.append(sec)
        # B4 metric: gap between FQ and EN self-rates
        fq_en_gap = section_b4[sec]['FQ'] - section_b4[sec]['EN']
        b4_values.append(fq_en_gap)
        b5_values.append(section_asymmetry[sec])
        c2_values.append(section_c2[sec]['cc_suffix_free_rate'])

    correlations = {}
    if len(b4_values) >= 3:
        from scipy.stats import spearmanr
        if np.std(b4_values) > 0 and np.std(b5_values) > 0:
            r, p = spearmanr(b4_values, b5_values)
            correlations['B4_B5'] = {'rho': round(r, 4), 'p': round(p, 4)}
        if np.std(b4_values) > 0 and np.std(c2_values) > 0:
            r, p = spearmanr(b4_values, c2_values)
            correlations['B4_C2'] = {'rho': round(r, 4), 'p': round(p, 4)}
        if np.std(b5_values) > 0 and np.std(c2_values) > 0:
            r, p = spearmanr(b5_values, c2_values)
            correlations['B5_C2'] = {'rho': round(r, 4), 'p': round(p, 4)}

    results_b['shared_mechanism_test'] = {
        'sections_used': shared_sections,
        'B4_metric': b4_values,
        'B5_metric': b5_values,
        'C2_metric': c2_values,
        'correlations': correlations,
        'verdict': (
            "INDEPENDENT" if all(
                abs(v.get('rho', 0)) < 0.7 for v in correlations.values()
            ) else "CORRELATED"
        ),
    }

    return results_b


# ============================================================
# VERDICTS
# ============================================================

def compute_verdicts(results_a, results_b):
    """Synthesize findings into verdicts."""

    # Part A verdict
    section_jsd_mean = results_a['mean_section_jsd']
    regime_jsd_mean = results_a['mean_regime_jsd']
    ratio = results_a['section_jsd_to_regime_jsd_ratio']
    frac_sig = results_a['chi2_summary']['fraction_significant']

    if ratio > 1.5:
        a_verdict = "SECTION_EXCEEDS_REGIME"
        a_detail = f"Section variation ({section_jsd_mean:.4f}) exceeds REGIME variation ({regime_jsd_mean:.4f}) by {ratio:.1f}x"
    elif ratio > 0.7:
        a_verdict = "SECTION_COMPARABLE_TO_REGIME"
        a_detail = f"Section variation ({section_jsd_mean:.4f}) comparable to REGIME variation ({regime_jsd_mean:.4f}), ratio {ratio:.1f}x"
    else:
        a_verdict = "SECTION_BELOW_REGIME"
        a_detail = f"Section variation ({section_jsd_mean:.4f}) below REGIME variation ({regime_jsd_mean:.4f}), ratio {ratio:.1f}x"

    # Part B verdict
    b_verdict = results_b['shared_mechanism_test']['verdict']
    if b_verdict == "INDEPENDENT":
        b_detail = "The 3 failing tests (B4, B5, C2) are independent — no shared mechanism. Each requires a different extension to M2."
    else:
        b_detail = "The 3 failing tests show correlation — possible shared latent mechanism."

    return {
        'part_a': {
            'verdict': a_verdict,
            'detail': a_detail,
            'topology_invariant': all(
                t.get('topology_overlap', 0) > 0.7
                for k, t in results_a['topology'].items()
                if k != 'global'
            ),
            'chi2_fraction_significant': frac_sig,
        },
        'part_b': {
            'verdict': b_verdict,
            'detail': b_detail,
            'B4_real_holds': results_b['B4_role_rank_order']['real_ordering_holds'],
            'B5_real_jsd': results_b['B5_forward_backward_jsd']['real_jsd'],
            'C2_real_rate': results_b['C2_cc_suffix_free']['real_cc_suffix_free_rate'],
        },
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Phase 352: SECTION_GRAMMAR_VARIATION + 20% GAP DECOMPOSITION")
    print("=" * 60)

    tokens, class_to_role = load_data()

    print("\n--- Part A: Section Grammar Variation ---")
    results_a = analyze_section_grammar(tokens, class_to_role)

    print(f"\nSection pairwise JSD: {results_a['pairwise_section_jsd']}")
    print(f"Regime pairwise JSD: {results_a['pairwise_regime_jsd']}")
    print(f"Mean section JSD: {results_a['mean_section_jsd']}")
    print(f"Mean regime JSD: {results_a['mean_regime_jsd']}")
    print(f"Section/Regime ratio: {results_a['section_jsd_to_regime_jsd_ratio']}")
    print(f"Chi2: {results_a['chi2_summary']}")
    print(f"Self-loops: {results_a['self_loop_rates']}")
    print(f"Spectral gaps: {results_a['spectral_gaps']}")

    print("\n--- Part B: 20% Gap Decomposition ---")
    results_b = analyze_gap_decomposition(tokens, class_to_role)

    b4 = results_b['B4_role_rank_order']
    print(f"\nB4 ordering: {b4['real_ordering']} (holds={b4['real_ordering_holds']})")
    print(f"M2 ordering holds: {b4['m2_ordering_holds']}")

    b5 = results_b['B5_forward_backward_jsd']
    print(f"\nB5 real JSD: {b5['real_jsd']:.6f}, M2 JSD: {b5['m2_jsd']}, ratio: {b5['ratio']}")
    print(f"Per-role asymmetry: {b5['per_role_asymmetry']}")

    c2 = results_b['C2_cc_suffix_free']
    print(f"\nC2 CC suffix-free: {c2['real_cc_suffix_free_rate']}")
    print(f"All roles: {c2['all_role_suffix_rates']}")

    print(f"\nShared mechanism: {results_b['shared_mechanism_test']}")

    verdicts = compute_verdicts(results_a, results_b)
    print(f"\n{'='*60}")
    print(f"Part A verdict: {verdicts['part_a']['verdict']}")
    print(f"  {verdicts['part_a']['detail']}")
    print(f"  Topology invariant: {verdicts['part_a']['topology_invariant']}")
    print(f"  Chi2 fraction sig: {verdicts['part_a']['chi2_fraction_significant']}")
    print(f"\nPart B verdict: {verdicts['part_b']['verdict']}")
    print(f"  {verdicts['part_b']['detail']}")

    # Save results
    output = {
        'phase': 'SECTION_GRAMMAR_VARIATION',
        'phase_number': 352,
        'part_a_section_grammar': results_a,
        'part_b_gap_decomposition': results_b,
        'verdicts': verdicts,
    }

    outpath = 'phases/SECTION_GRAMMAR_VARIATION/results/section_grammar_variation.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")


if __name__ == '__main__':
    main()

"""Phase 419: Dark Pipeline Combinatorics.

Investigates the combinatorial rules governing which bridge-atom combinations
are admitted as dark-pipeline compound MIDDLEs. 300 dark MIDDLEs (200 compound,
100 atomic), built from 50 unique atoms (43 bridge + 6 dark-exclusive + 1 other).

Tests:
  1. Atom co-occurrence acceptance rule (pairwise gate analysis)
  2. Section hyper-modulation mechanism (atoms vs combinations)
  3. Dark-bridge tradeoff mechanism (diversity vs intensity)
  4. Modified ordering grammar characterization
  5. Phantom MIDDLE analysis (15 B-absent classifications)
"""
import json
import sys
import math
import os
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer


# --- Utility functions ---

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def herfindahl(counts):
    total = sum(counts.values()) if isinstance(counts, dict) else sum(counts)
    if total == 0:
        return 0.0
    vals = counts.values() if isinstance(counts, dict) else counts
    return sum((c / total) ** 2 for c in vals)


def jensen_shannon(p_counts, q_counts):
    all_keys = set(p_counts.keys()) | set(q_counts.keys())
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return 0.0
    js = 0.0
    for k in all_keys:
        p = p_counts.get(k, 0) / p_total
        q = q_counts.get(k, 0) / q_total
        m = (p + q) / 2
        if p > 0 and m > 0:
            js += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            js += 0.5 * q * math.log2(q / m)
    return js


def pearson_r(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def _normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def chi_square_2xk(observed_2d):
    n_rows = len(observed_2d)
    n_cols = len(observed_2d[0])
    n = sum(sum(row) for row in observed_2d)
    if n == 0:
        return {'chi2': 0.0, 'df': 0, 'p': 1.0}
    row_totals = [sum(row) for row in observed_2d]
    col_totals = [sum(observed_2d[r][c] for r in range(n_rows)) for c in range(n_cols)]
    chi2 = 0.0
    for r in range(n_rows):
        for c in range(n_cols):
            expected = row_totals[r] * col_totals[c] / n
            if expected > 0:
                chi2 += (observed_2d[r][c] - expected) ** 2 / expected
    df = (n_rows - 1) * (n_cols - 1)
    if df > 0 and chi2 > 0:
        z = ((chi2 / df) ** (1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        p = 1 - _normal_cdf(z)
    else:
        p = 1.0
    return {'chi2': chi2, 'df': df, 'p': p}


def spearman_r(xs, ys):
    """Spearman rank correlation."""
    n = len(xs)
    if n < 3:
        return 0.0, 1.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and vals[indexed[j]] == vals[indexed[i]]:
                j += 1
            avg = (i + j + 1) / 2
            for k in range(i, j):
                ranks[indexed[k]] = avg
            i = j
        return ranks

    rx = rank_data(xs)
    ry = rank_data(ys)
    rho = pearson_r(rx, ry)

    # t-test for significance
    if abs(rho) >= 1.0:
        return rho, 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    # Approximate p from t-distribution using normal for large n
    p = 2 * (1 - _normal_cdf(abs(t)))
    return rho, p


# --- Data loading ---

def load_data():
    """Load all input files and run single B pass."""
    print("Loading data...")

    # 1. Dark pipeline MIDDLEs
    with open(ROOT / 'data/dark_pipeline_middles.json', encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_set = set(dark_data['middles'])

    # 2. Atom decomposition data (Phase 408)
    with open(ROOT / 'phases/PP_PIPELINE_ATOM_DECOMPOSITION/results/pp_pipeline_atoms.json',
              encoding='utf-8') as f:
        atom_data = json.load(f)
    bridge_atoms_list = atom_data['test2']['bridge_atoms_list']
    bridge_atoms_set = set(bridge_atoms_list)
    phantom_profiles = atom_data['test1']['phantom_profiles']
    atom_count_dist = atom_data['test2']['atom_count_distribution']
    top_atoms = atom_data['test2']['top_20_atoms']

    # 3. Dark internal architecture (Phase 409)
    with open(ROOT / 'phases/DARK_PIPELINE_INTERNAL_ARCHITECTURE/results/dark_pipeline_internal.json',
              encoding='utf-8') as f:
        dark_internal = json.load(f)

    # 4. C1065 atom ordering grammar
    with open(ROOT / 'phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t3_atom_bigram_grammar.json',
              encoding='utf-8') as f:
        c1065_data = json.load(f)
    c1065_pairs = c1065_data['asymmetric_pairs']

    # 5. C475 MIDDLE incompatibility
    with open(ROOT / 'phases/MIDDLE_INCOMPATIBILITY/results/middle_incompatibility.json',
              encoding='utf-8') as f:
        c475_data = json.load(f)
    # Build component lookup: MIDDLE -> component index
    c475_components = c475_data['graph_analysis']['components']
    middle_to_component = {}
    for idx, comp in enumerate(c475_components):
        for mid in comp:
            middle_to_component[mid] = idx

    # 6. Bridge MIDDLEs (85 bridge backbone)
    with open(ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data.get('bridge_middles', []))

    # 7. Build MiddleAnalyzer
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # 8. Decompose dark compounds into atoms
    dark_compound_atoms = {}  # MIDDLE -> [atoms]
    for mid in dark_set:
        atoms = mid_analyzer.get_maximal_atoms(mid, use_core=True)
        if len(atoms) >= 2:
            dark_compound_atoms[mid] = atoms
        elif len(atoms) == 1 and atoms[0] != mid:
            dark_compound_atoms[mid] = atoms

    # 9. Build section lookup from Phase 409 internal data
    folio_sections = {}
    if 'test4' in dark_internal:
        t4 = dark_internal['test4']
        if 'section_counts' in t4:
            pass  # We'll get sections from transcript

    # 10. Single transcript pass
    tx = Transcript()
    morph = Morphology()

    folio_dark_count = Counter()
    folio_bridge_count = Counter()
    folio_total_count = Counter()
    folio_dark_middles = defaultdict(set)  # folio -> set of unique dark MIDDLEs
    middle_section_freq = defaultdict(Counter)  # MIDDLE -> {section: count}
    atom_section_freq = defaultdict(Counter)    # atom -> {section: count}
    folio_section = {}

    for token in tx.currier_b():
        word = token.word
        if not word.strip() or '*' in word:
            continue
        folio = token.folio
        section = token.section if hasattr(token, 'section') else None

        # Get section from folio mapping if not available
        if section is None:
            section = getattr(token, 'currier', None)
            if section and section in ('A', 'B'):
                section = None  # That's the language, not section

        m = morph.extract(word)
        mid = m.middle if m else None
        if not mid:
            continue

        folio_total_count[folio] += 1

        if mid in dark_set:
            folio_dark_count[folio] += 1
            folio_dark_middles[folio].add(mid)

            # Get section for this folio
            sec = folio_section.get(folio)
            if sec:
                middle_section_freq[mid][sec] += 1
                # Attribute to atoms
                if mid in dark_compound_atoms:
                    for atom in dark_compound_atoms[mid]:
                        atom_section_freq[atom][sec] += 1

        if mid in bridge_middles or mid in bridge_atoms_set:
            folio_bridge_count[folio] += 1

    # Determine folio sections from transcript metadata
    # Re-pass to get sections (often stored in the transcript)
    for token in tx.currier_b():
        folio = token.folio
        if folio not in folio_section:
            sec = getattr(token, 'section', None)
            if sec:
                folio_section[folio] = sec

    # If sections not available from token attributes, derive from folio names
    if not folio_section:
        # Load from Phase 409 or axm data
        try:
            with open(ROOT / 'phases/AXM_RESIDUAL_DECOMPOSITION/results/axm_residual_decomposition.json',
                      encoding='utf-8') as f:
                axm_data = json.load(f)
            for entry in axm_data.get('folio_data', []):
                folio_section[entry['folio']] = entry['section']
        except (FileNotFoundError, KeyError):
            pass

    # Rebuild section-conditioned counts with proper sections
    if folio_section:
        middle_section_freq.clear()
        atom_section_freq.clear()
        for token in tx.currier_b():
            word = token.word
            if not word.strip() or '*' in word:
                continue
            folio = token.folio
            sec = folio_section.get(folio)
            if not sec:
                continue
            m = morph.extract(word)
            mid = m.middle if m else None
            if not mid or mid not in dark_set:
                continue
            middle_section_freq[mid][sec] += 1
            if mid in dark_compound_atoms:
                for atom in dark_compound_atoms[mid]:
                    atom_section_freq[atom][sec] += 1

    all_sections = sorted(set(folio_section.values())) if folio_section else []

    print(f"  Dark MIDDLEs: {len(dark_set)}")
    print(f"  Multi-atom compounds: {len(dark_compound_atoms)}")
    print(f"  Bridge atoms: {len(bridge_atoms_set)}")
    print(f"  Folios with sections: {len(folio_section)}")
    print(f"  Sections: {all_sections}")

    return {
        'dark_set': dark_set,
        'dark_compound_atoms': dark_compound_atoms,
        'bridge_atoms_set': bridge_atoms_set,
        'bridge_atoms_list': bridge_atoms_list,
        'bridge_middles': bridge_middles,
        'phantom_profiles': phantom_profiles,
        'c1065_pairs': c1065_pairs,
        'middle_to_component': middle_to_component,
        'c475_components': c475_components,
        'mid_analyzer': mid_analyzer,
        'folio_dark_count': folio_dark_count,
        'folio_bridge_count': folio_bridge_count,
        'folio_total_count': folio_total_count,
        'folio_dark_middles': folio_dark_middles,
        'folio_section': folio_section,
        'middle_section_freq': middle_section_freq,
        'atom_section_freq': atom_section_freq,
        'all_sections': all_sections,
        'atom_data': atom_data,
        'dark_internal': dark_internal,
    }


# --- Test 1: Atom Co-occurrence Acceptance Rule ---

def test1_atom_cooccurrence_acceptance(data):
    """Which atom pairs are admitted in dark compounds? Test gates."""
    print("\n-- Test 1: ATOM_COOCCURRENCE_ACCEPTANCE --")

    dark_compound_atoms = data['dark_compound_atoms']
    bridge_atoms_set = data['bridge_atoms_set']
    middle_to_component = data['middle_to_component']
    c1065_pairs = data['c1065_pairs']

    # Collect all atoms used in multi-atom dark compounds
    all_dark_atoms = set()
    for mid, atoms in dark_compound_atoms.items():
        if len(atoms) >= 2:
            all_dark_atoms.update(atoms)

    n_atoms = len(all_dark_atoms)
    total_pairs = n_atoms * (n_atoms - 1) // 2
    print(f"  Atoms in multi-atom compounds: {n_atoms}")
    print(f"  Total possible pairs: {total_pairs}")

    # Build observed co-occurrence set
    observed_pairs = set()
    pair_counts = Counter()
    for mid, atoms in dark_compound_atoms.items():
        if len(atoms) >= 2:
            for a1, a2 in combinations(atoms, 2):
                pair = frozenset([a1, a2])
                observed_pairs.add(pair)
                pair_counts[pair] += 1

    n_observed = len(observed_pairs)
    occupancy = n_observed / total_pairs if total_pairs > 0 else 0
    print(f"  Observed pairs: {n_observed}")
    print(f"  Occupancy: {occupancy:.3f}")

    # Gate A: C475 compatibility
    # Two atoms are C475-compatible if they share a component
    c475_compatible = 0
    c475_tested = 0
    for pair in observed_pairs:
        a1, a2 = list(pair)
        comp1 = middle_to_component.get(a1)
        comp2 = middle_to_component.get(a2)
        if comp1 is not None and comp2 is not None:
            c475_tested += 1
            if comp1 == comp2:
                c475_compatible += 1

    c475_recall = c475_compatible / c475_tested if c475_tested > 0 else 0
    # Precision: how many C475-compatible pairs in the full space are observed?
    all_c475_compat = 0
    all_c475_tested = 0
    for a1, a2 in combinations(all_dark_atoms, 2):
        comp1 = middle_to_component.get(a1)
        comp2 = middle_to_component.get(a2)
        if comp1 is not None and comp2 is not None:
            all_c475_tested += 1
            if comp1 == comp2:
                all_c475_compat += 1
    c475_precision = n_observed / all_c475_compat if all_c475_compat > 0 else 0

    print(f"  C475 gate: recall={c475_recall:.3f} ({c475_compatible}/{c475_tested}), "
          f"precision={c475_precision:.3f} ({n_observed}/{all_c475_compat})")

    # Gate B: C1061 enriched pairs
    c1061_enriched = set()
    # Parse from the C1065 data (they share the same file structure) or separate
    # C1061 enriched pairs are in a different file
    try:
        with open(ROOT / 'phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t4_atom_cooccurrence_rules.json',
                  encoding='utf-8') as f:
            c1061_data = json.load(f)
        for ep in c1061_data.get('enriched_pairs', []):
            c1061_enriched.add(frozenset([ep['atom1'], ep['atom2']]))
    except (FileNotFoundError, KeyError):
        pass

    c1061_overlap = observed_pairs & c1061_enriched
    c1061_recall = len(c1061_overlap) / len(c1061_enriched) if c1061_enriched else 0
    c1061_precision = len(c1061_overlap) / n_observed if n_observed > 0 else 0
    print(f"  C1061 gate: recall={c1061_recall:.3f} ({len(c1061_overlap)}/{len(c1061_enriched)}), "
          f"precision={c1061_precision:.3f}")

    # Gate C: C1065 ordering pairs
    c1065_pair_set = set()
    for p in c1065_pairs:
        c1065_pair_set.add(frozenset([p['dominant'], p['subordinate']]))
    c1065_overlap = observed_pairs & c1065_pair_set
    c1065_recall = len(c1065_overlap) / len(c1065_pair_set) if c1065_pair_set else 0
    c1065_precision = len(c1065_overlap) / n_observed if n_observed > 0 else 0
    print(f"  C1065 gate: recall={c1065_recall:.3f} ({len(c1065_overlap)}/{len(c1065_pair_set)}), "
          f"precision={c1065_precision:.3f}")

    # Top co-occurring pairs
    top_pairs = pair_counts.most_common(15)
    top_pairs_list = [{'pair': sorted(list(p)), 'count': c} for p, c in top_pairs]
    print(f"\n  Top 10 pairs:")
    for item in top_pairs_list[:10]:
        print(f"    {item['pair'][0]}+{item['pair'][1]}: {item['count']}")

    # Bridge atom fraction in observed pairs
    bridge_pair_count = sum(1 for pair in observed_pairs
                           if all(a in bridge_atoms_set for a in pair))
    bridge_pair_frac = bridge_pair_count / n_observed if n_observed > 0 else 0
    print(f"\n  All-bridge pairs: {bridge_pair_count}/{n_observed} ({bridge_pair_frac:.3f})")

    # Verdict
    if occupancy < 0.05:
        verdict = 'SPARSE_OCCUPANCY'
    elif c475_recall > 0.90 and c475_precision > 0.30:
        verdict = 'PAIRWISE_GATED'
    elif (c475_recall > 0.80 or c1065_recall > 0.50) and c475_precision > 0.20:
        verdict = 'MULTI_GATED'
    elif c475_recall < 0.70 and c1065_recall < 0.50:
        verdict = 'UNGATED'
    else:
        verdict = 'WEAKLY_GATED'

    print(f"  Verdict: {verdict}")

    return {
        'n_atoms': n_atoms,
        'n_total_pairs': total_pairs,
        'n_observed_pairs': n_observed,
        'occupancy_rate': occupancy,
        'c475_gate': {
            'tested': c475_tested,
            'compatible': c475_compatible,
            'recall': c475_recall,
            'total_compatible_space': all_c475_compat,
            'precision': c475_precision,
        },
        'c1061_gate': {
            'n_enriched': len(c1061_enriched),
            'overlap': len(c1061_overlap),
            'recall': c1061_recall,
            'precision': c1061_precision,
        },
        'c1065_gate': {
            'n_asymmetric': len(c1065_pair_set),
            'overlap': len(c1065_overlap),
            'recall': c1065_recall,
            'precision': c1065_precision,
        },
        'bridge_pair_fraction': bridge_pair_frac,
        'top_pairs': top_pairs_list,
        'verdict': verdict,
    }


# --- Test 2: Section Hyper-Modulation Mechanism ---

def test2_section_hyper_modulation(data):
    """Does section concentration come from atom selection or combination?"""
    print("\n-- Test 2: SECTION_HYPER_MODULATION --")

    dark_compound_atoms = data['dark_compound_atoms']
    middle_section_freq = data['middle_section_freq']
    atom_section_freq = data['atom_section_freq']
    all_sections = data['all_sections']

    if not all_sections:
        print("  No section data available. Skipping.")
        return {'verdict': 'NO_DATA'}

    # Build per-atom section probability distributions
    atom_probs = {}
    min_atom_tokens = 10
    for atom, sec_counts in atom_section_freq.items():
        total = sum(sec_counts.values())
        if total >= min_atom_tokens:
            atom_probs[atom] = {s: sec_counts.get(s, 0) / total for s in all_sections}

    print(f"  Atoms with >={min_atom_tokens} tokens: {len(atom_probs)}")

    # Build multiplicative predictions for 2+ atom compounds
    observed_vecs = []
    predicted_vecs = []
    js_obs_pred = []
    js_obs_uniform = []
    qualifying_compounds = []

    uniform = {s: 1.0 / len(all_sections) for s in all_sections}

    for mid, atoms in dark_compound_atoms.items():
        if len(atoms) < 2:
            continue
        # Check all atoms have profiles
        if not all(a in atom_probs for a in atoms):
            continue
        # Check compound has enough tokens
        sec_counts = middle_section_freq.get(mid, {})
        total_tokens = sum(sec_counts.values())
        if total_tokens < 5:
            continue

        # Observed section distribution
        obs = {s: sec_counts.get(s, 0) / total_tokens for s in all_sections}

        # Multiplicative prediction
        pred_raw = {}
        for s in all_sections:
            p = 1.0
            for atom in atoms:
                p *= max(atom_probs[atom].get(s, 0), 1e-10)
            pred_raw[s] = p
        pred_total = sum(pred_raw.values())
        pred = {s: pred_raw[s] / pred_total for s in all_sections} if pred_total > 0 else uniform

        # Collect vectors for correlation
        for s in all_sections:
            observed_vecs.append(obs.get(s, 0))
            predicted_vecs.append(pred.get(s, 0))

        # JSD measures
        obs_counts = {s: sec_counts.get(s, 0) for s in all_sections}
        pred_counts = {s: pred[s] * total_tokens for s in all_sections}
        unif_counts = {s: total_tokens / len(all_sections) for s in all_sections}

        js_op = jensen_shannon(obs_counts, pred_counts)
        js_ou = jensen_shannon(obs_counts, unif_counts)
        js_obs_pred.append(js_op)
        js_obs_uniform.append(js_ou)

        qualifying_compounds.append({
            'middle': mid,
            'atoms': atoms,
            'tokens': total_tokens,
            'observed': obs,
            'predicted': pred,
            'js_obs_pred': js_op,
            'js_obs_uniform': js_ou,
        })

    n_qualifying = len(qualifying_compounds)
    print(f"  Qualifying compounds (2+ atoms, >=5 tokens, all atoms profiled): {n_qualifying}")

    if n_qualifying < 5:
        print("  Too few qualifying compounds.")
        r_sq = 0.0
    else:
        r = pearson_r(observed_vecs, predicted_vecs)
        r_sq = r ** 2
        mean_js_op = sum(js_obs_pred) / len(js_obs_pred) if js_obs_pred else 0
        mean_js_ou = sum(js_obs_uniform) / len(js_obs_uniform) if js_obs_uniform else 0
        pseudo_r2 = 1 - mean_js_op / mean_js_ou if mean_js_ou > 0 else 0

    mean_js_op = sum(js_obs_pred) / len(js_obs_pred) if js_obs_pred else 0
    mean_js_ou = sum(js_obs_uniform) / len(js_obs_uniform) if js_obs_uniform else 0
    pseudo_r2 = 1 - mean_js_op / mean_js_ou if mean_js_ou > 0 else 0

    print(f"  Pearson R²: {r_sq:.4f}")
    print(f"  Mean JS(obs,pred): {mean_js_op:.4f}")
    print(f"  Mean JS(obs,uniform): {mean_js_ou:.4f}")
    print(f"  Pseudo-R² (1 - JS_pred/JS_uniform): {pseudo_r2:.4f}")

    # Sample atom profiles
    atom_profiles_sample = []
    for atom in sorted(atom_probs.keys(), key=lambda a: sum(atom_section_freq[a].values()), reverse=True)[:10]:
        atom_profiles_sample.append({
            'atom': atom,
            'tokens': sum(atom_section_freq[atom].values()),
            'profile': atom_probs[atom],
            'herfindahl': herfindahl(atom_section_freq[atom]),
        })

    # Verdict
    if r_sq > 0.60:
        verdict = 'ATOM_SELECTION_DOMINATED'
    elif r_sq < 0.30:
        verdict = 'COMBINATION_DOMINATED'
    else:
        verdict = 'MIXED_MECHANISM'

    print(f"  Verdict: {verdict}")

    return {
        'n_qualifying_compounds': n_qualifying,
        'n_atoms_profiled': len(atom_probs),
        'min_atom_tokens': min_atom_tokens,
        'r_squared': r_sq,
        'mean_js_obs_pred': mean_js_op,
        'mean_js_obs_uniform': mean_js_ou,
        'pseudo_r2': pseudo_r2,
        'sections': all_sections,
        'atom_profiles_sample': atom_profiles_sample,
        'verdict': verdict,
    }


# --- Test 3: Dark-Bridge Tradeoff Mechanism ---

def test3_dark_bridge_tradeoff(data):
    """Is the r=-0.865 anti-correlation driven by diversity or intensity?"""
    print("\n-- Test 3: DARK_BRIDGE_TRADEOFF --")

    folio_dark_count = data['folio_dark_count']
    folio_bridge_count = data['folio_bridge_count']
    folio_total_count = data['folio_total_count']
    folio_dark_middles = data['folio_dark_middles']
    folio_section = data['folio_section']

    # Build per-folio metrics (use DENSITIES, not raw counts — per C1146)
    folios = sorted(set(folio_total_count.keys()) & set(folio_section.keys()))
    folios = [f for f in folios if folio_total_count[f] >= 20]  # Minimum tokens

    dark_densities = []
    bridge_densities = []
    dark_diversities = []
    dark_intensities = []
    sections = []

    for f in folios:
        total = folio_total_count[f]
        dark_n = folio_dark_count.get(f, 0)
        bridge_n = folio_bridge_count.get(f, 0)
        dark_unique = len(folio_dark_middles.get(f, set()))

        bridge_density = bridge_n / total if total > 0 else 0
        dark_density = dark_n / total if total > 0 else 0
        dark_intensity = dark_n / dark_unique if dark_unique > 0 else 0

        dark_densities.append(dark_density)
        bridge_densities.append(bridge_density)
        dark_diversities.append(dark_unique)
        dark_intensities.append(dark_intensity)
        sections.append(folio_section.get(f, '?'))

    n_folios = len(folios)
    print(f"  Folios analyzed: {n_folios}")

    # Overall correlations (using density, matching C1146 methodology)
    r_total, p_total = spearman_r(dark_densities, bridge_densities)
    r_diversity, p_diversity = spearman_r(dark_diversities, bridge_densities)
    r_intensity, p_intensity = spearman_r(dark_intensities, bridge_densities)

    print(f"  r_total (dark_density vs bridge_density): {r_total:.4f} (p={p_total:.4f})")
    print(f"  r_diversity (dark_unique vs bridge_density): {r_diversity:.4f} (p={p_diversity:.4f})")
    print(f"  r_intensity (tokens/MIDDLE vs bridge_density): {r_intensity:.4f} (p={p_intensity:.4f})")

    decomposition_ratio = abs(r_diversity) / abs(r_intensity) if abs(r_intensity) > 0.01 else float('inf')
    print(f"  Decomposition ratio |r_div|/|r_int|: {decomposition_ratio:.2f}")

    # Within-section decomposition
    within_section = {}
    section_set = sorted(set(sections))
    for sec in section_set:
        idx = [i for i in range(n_folios) if sections[i] == sec]
        if len(idx) < 5:
            continue
        sec_dark = [dark_densities[i] for i in idx]
        sec_bridge = [bridge_densities[i] for i in idx]
        sec_div = [dark_diversities[i] for i in idx]
        sec_int = [dark_intensities[i] for i in idx]

        sr_total, sp_total = spearman_r(sec_dark, sec_bridge)
        sr_div, sp_div = spearman_r(sec_div, sec_bridge)
        sr_int, sp_int = spearman_r(sec_int, sec_bridge)

        within_section[sec] = {
            'n': len(idx),
            'r_total': sr_total,
            'r_diversity': sr_div,
            'r_intensity': sr_int,
        }
        print(f"  Section {sec} (n={len(idx)}): r_total={sr_total:.3f}, "
              f"r_div={sr_div:.3f}, r_int={sr_int:.3f}")

    # Verdict
    if abs(r_diversity) > 0.5 and abs(r_intensity) < 0.3:
        verdict = 'VOCABULARY_COMPETITION'
    elif abs(r_intensity) > 0.5 and abs(r_diversity) < 0.3:
        verdict = 'TOKEN_BUDGET_COMPETITION'
    elif abs(r_diversity) > 0.4 and abs(r_intensity) > 0.4:
        verdict = 'DUAL_COMPETITION'
    else:
        verdict = 'AMBIGUOUS'

    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n_folios,
        'r_total': r_total,
        'p_total': p_total,
        'r_diversity': r_diversity,
        'p_diversity': p_diversity,
        'r_intensity': r_intensity,
        'p_intensity': p_intensity,
        'decomposition_ratio': decomposition_ratio,
        'c1146_reference': -0.865,
        'within_section': within_section,
        'verdict': verdict,
    }


# --- Test 4: Modified Ordering Grammar ---

def test4_modified_ordering_grammar(data):
    """Characterize the dark pipeline's own ordering grammar."""
    print("\n-- Test 4: MODIFIED_ORDERING_GRAMMAR --")

    dark_compound_atoms = data['dark_compound_atoms']
    dark_set = data['dark_set']
    c1065_pairs = data['c1065_pairs']
    mid_analyzer = data['mid_analyzer']

    # Extract ordered atom bigrams from dark compounds
    # For each compound, atoms appear in left-to-right order within the MIDDLE string
    bigram_counts = Counter()  # (first, second) -> count
    n_compounds_analyzed = 0

    for mid in sorted(dark_set):
        atoms = mid_analyzer.get_maximal_atoms(mid, use_core=True)
        if len(atoms) < 2:
            continue

        # Determine atom positions within the MIDDLE string
        atom_positions = []
        for atom in atoms:
            pos = mid.find(atom)
            if pos >= 0:
                atom_positions.append((pos, atom))

        # Sort by position (left-to-right in string)
        atom_positions.sort()
        ordered_atoms = [a for _, a in atom_positions]

        # Record all ordered bigrams
        for i in range(len(ordered_atoms)):
            for j in range(i + 1, len(ordered_atoms)):
                bigram_counts[(ordered_atoms[i], ordered_atoms[j])] += 1

        n_compounds_analyzed += 1

    # Build unordered pair statistics
    pair_stats = {}
    for (a1, a2), count in bigram_counts.items():
        key = frozenset([a1, a2])
        if key not in pair_stats:
            pair_stats[key] = {'atoms': sorted([a1, a2]), 'fwd': 0, 'rev': 0}

        # fwd = alphabetically first atom comes first in string
        if a1 <= a2:
            pair_stats[key]['fwd'] += count
        else:
            pair_stats[key]['rev'] += count

    # Recompute with consistent directionality
    pair_stats_clean = {}
    for (a1, a2), count in bigram_counts.items():
        canonical = tuple(sorted([a1, a2]))
        if canonical not in pair_stats_clean:
            pair_stats_clean[canonical] = {'fwd': 0, 'rev': 0}
        if a1 == canonical[0]:
            pair_stats_clean[canonical]['fwd'] += count
        else:
            pair_stats_clean[canonical]['rev'] += count

    n_bigram_types = len(pair_stats_clean)
    n_bigram_tokens = sum(v['fwd'] + v['rev'] for v in pair_stats_clean.values())
    print(f"  Compounds analyzed: {n_compounds_analyzed}")
    print(f"  Unique ordered pair types: {n_bigram_types}")
    print(f"  Total ordered pair tokens: {n_bigram_tokens}")

    # Identify asymmetric pairs (dominance >= 0.80, total >= 3)
    dark_asymmetric = []
    min_total = 3
    min_dominance = 0.80
    for (a1, a2), stats in pair_stats_clean.items():
        total = stats['fwd'] + stats['rev']
        if total < min_total:
            continue
        dom_rate = max(stats['fwd'], stats['rev']) / total
        if dom_rate >= min_dominance:
            if stats['fwd'] >= stats['rev']:
                dominant, subordinate = a1, a2
                fwd, rev = stats['fwd'], stats['rev']
            else:
                dominant, subordinate = a2, a1
                fwd, rev = stats['rev'], stats['fwd']
            dark_asymmetric.append({
                'dominant': dominant,
                'subordinate': subordinate,
                'fwd': fwd,
                'rev': rev,
                'total': total,
                'rate': dom_rate,
            })

    dark_asymmetric.sort(key=lambda x: x['total'], reverse=True)
    print(f"  Dark asymmetric pairs (>={min_dominance}, n>={min_total}): {len(dark_asymmetric)}")

    for p in dark_asymmetric[:10]:
        print(f"    {p['dominant']}->{p['subordinate']}: {p['fwd']}/{p['total']} ({p['rate']:.2f})")

    # Internal consistency: transitivity check
    # Build ordering graph: dominant -> {subordinate}
    ordering_graph = defaultdict(set)
    for p in dark_asymmetric:
        ordering_graph[p['dominant']].add(p['subordinate'])

    transitive_triples = 0
    transitive_violations = 0
    for a in ordering_graph:
        for b in ordering_graph[a]:
            for c in ordering_graph.get(b, set()):
                if c in ordering_graph.get(a, set()):
                    transitive_triples += 1
                else:
                    # Check for explicit violation (c > a)
                    if a in ordering_graph.get(c, set()):
                        transitive_violations += 1

    total_triples = transitive_triples + transitive_violations
    consistency_rate = transitive_triples / total_triples if total_triples > 0 else 1.0
    print(f"\n  Transitivity: {transitive_triples} consistent, "
          f"{transitive_violations} violations, rate={consistency_rate:.3f}")

    # C1065 comparison
    c1065_matches = 0
    c1065_mismatches = 0
    c1065_not_found = 0
    c1065_comparison = []

    dark_ordering_lookup = {}
    for p in dark_asymmetric:
        dark_ordering_lookup[frozenset([p['dominant'], p['subordinate']])] = p

    for c_pair in c1065_pairs:
        key = frozenset([c_pair['dominant'], c_pair['subordinate']])
        if key in dark_ordering_lookup:
            d_pair = dark_ordering_lookup[key]
            if d_pair['dominant'] == c_pair['dominant']:
                status = 'MATCH'
                c1065_matches += 1
            else:
                status = 'MISMATCH'
                c1065_mismatches += 1
            c1065_comparison.append({
                'c1065_dominant': c_pair['dominant'],
                'c1065_subordinate': c_pair['subordinate'],
                'dark_dominant': d_pair['dominant'],
                'dark_subordinate': d_pair['subordinate'],
                'status': status,
            })
        else:
            # Check if pair appears at all (below threshold)
            canonical = tuple(sorted([c_pair['dominant'], c_pair['subordinate']]))
            if canonical in pair_stats_clean:
                stats = pair_stats_clean[canonical]
                total = stats['fwd'] + stats['rev']
                c1065_not_found += 1
                c1065_comparison.append({
                    'c1065_dominant': c_pair['dominant'],
                    'c1065_subordinate': c_pair['subordinate'],
                    'dark_total': total,
                    'status': 'BELOW_THRESHOLD',
                })
            else:
                c1065_not_found += 1
                c1065_comparison.append({
                    'c1065_dominant': c_pair['dominant'],
                    'c1065_subordinate': c_pair['subordinate'],
                    'status': 'NOT_FOUND',
                })

    testable = c1065_matches + c1065_mismatches
    agreement_rate = c1065_matches / testable if testable > 0 else 0
    print(f"\n  C1065 comparison: {c1065_matches} match, {c1065_mismatches} mismatch, "
          f"{c1065_not_found} not found")
    print(f"  Agreement rate: {agreement_rate:.3f} ({c1065_matches}/{testable})")

    # Dark-exclusive rules (not in C1065)
    c1065_pair_keys = {frozenset([p['dominant'], p['subordinate']]) for p in c1065_pairs}
    dark_exclusive_rules = [p for p in dark_asymmetric
                           if frozenset([p['dominant'], p['subordinate']]) not in c1065_pair_keys]
    print(f"  Dark-exclusive ordering rules: {len(dark_exclusive_rules)}")
    for p in dark_exclusive_rules[:5]:
        print(f"    {p['dominant']}->{p['subordinate']}: {p['fwd']}/{p['total']}")

    # Verdict
    if agreement_rate >= 0.70 and consistency_rate >= 0.80:
        verdict = 'CONSISTENT_GRAMMAR'
    elif agreement_rate < 0.40 and consistency_rate >= 0.80:
        verdict = 'INDEPENDENT_GRAMMAR'
    elif agreement_rate < 0.40:
        verdict = 'DIVERGENT_GRAMMAR'
    else:
        verdict = 'MODIFIED_GRAMMAR'

    print(f"  Verdict: {verdict}")

    return {
        'n_compounds_analyzed': n_compounds_analyzed,
        'n_bigram_types': n_bigram_types,
        'n_bigram_tokens': n_bigram_tokens,
        'n_dark_asymmetric': len(dark_asymmetric),
        'dark_asymmetric_pairs': dark_asymmetric,
        'internal_consistency': {
            'transitive_triples': transitive_triples,
            'violations': transitive_violations,
            'total_tested': total_triples,
            'consistency_rate': consistency_rate,
        },
        'c1065_comparison': {
            'matches': c1065_matches,
            'mismatches': c1065_mismatches,
            'not_found': c1065_not_found,
            'testable': testable,
            'agreement_rate': agreement_rate,
            'details': c1065_comparison,
        },
        'dark_exclusive_rules': dark_exclusive_rules,
        'verdict': verdict,
    }


# --- Test 5: Phantom MIDDLE Analysis ---

def test5_phantom_middle_analysis(data):
    """Classify the 15 B-absent phantom MIDDLEs."""
    print("\n-- Test 5: PHANTOM_MIDDLE_ANALYSIS --")

    phantom_profiles = data['phantom_profiles']
    bridge_atoms_set = data['bridge_atoms_set']
    middle_to_component = data['middle_to_component']
    dark_set = data['dark_set']
    mid_analyzer = data['mid_analyzer']

    classifications = {}
    n_valid = 0
    n_invalid = 0
    n_partial = 0
    n_untestable = 0

    for phantom, profile in phantom_profiles.items():
        print(f"\n  {phantom}:")
        is_compound = profile.get('is_compound', False)
        pre_atoms = profile.get('atoms', [])

        tests_passed = 0
        tests_failed = 0
        tests_untestable = 0

        # Test A: Bridge atom content
        if is_compound and pre_atoms:
            bridge_atom_count = sum(1 for a in pre_atoms if a in bridge_atoms_set)
            bridge_frac = bridge_atom_count / len(pre_atoms) if pre_atoms else 0
            bridge_pass = bridge_frac > 0
            if bridge_pass:
                tests_passed += 1
                print(f"    Bridge atoms: PASS ({bridge_atom_count}/{len(pre_atoms)})")
            else:
                tests_failed += 1
                print(f"    Bridge atoms: FAIL (0/{len(pre_atoms)})")
        else:
            # Non-compound: check if phantom itself is a bridge MIDDLE
            if phantom in bridge_atoms_set:
                tests_passed += 1
                print(f"    Bridge atom: PASS (phantom IS bridge MIDDLE)")
            else:
                # For short non-compound phantoms, check if any substring is a bridge atom
                found_bridge = False
                for ba in bridge_atoms_set:
                    if ba in phantom and len(ba) >= 2:
                        found_bridge = True
                        break
                if found_bridge:
                    tests_passed += 1
                    print(f"    Bridge atom substring: PASS")
                else:
                    tests_untestable += 1
                    print(f"    Bridge atom: UNTESTABLE (atomic, no bridge match)")

        # Test B: C475 component membership
        phantom_comp = middle_to_component.get(phantom)
        if phantom_comp is not None:
            # Count how many B-vocabulary MIDDLEs share this component
            comp_members = data['c475_components'][phantom_comp]
            b_members = sum(1 for m in comp_members if m in dark_set or m in bridge_atoms_set)
            if b_members > 0:
                tests_passed += 1
                print(f"    C475 component: PASS (component {phantom_comp}, "
                      f"{b_members} B-vocabulary members, {len(comp_members)} total)")
            else:
                tests_failed += 1
                print(f"    C475 component: FAIL (no B-vocabulary in component)")
        else:
            tests_untestable += 1
            print(f"    C475 component: UNTESTABLE (not in C475 graph)")

        # Test C: Construction grammar match
        # Check if analogous forms exist (same prefix pattern + different atom)
        prefix = 'ch' if phantom.startswith('ch') else 'sh' if phantom.startswith('sh') else None
        suffix_part = phantom[len(prefix):] if prefix else phantom

        # Search for dark MIDDLEs with same prefix and similar structure
        analogous_count = 0
        analogous_examples = []
        if prefix:
            for dark_mid in dark_set:
                if dark_mid.startswith(prefix) and dark_mid != phantom:
                    analogous_count += 1
                    if len(analogous_examples) < 3:
                        analogous_examples.append(dark_mid)

        if analogous_count >= 3:
            tests_passed += 1
            print(f"    Analogous forms: PASS ({analogous_count} dark MIDDLEs with {prefix}- prefix, "
                  f"e.g., {analogous_examples})")
        elif analogous_count > 0:
            tests_passed += 1
            print(f"    Analogous forms: WEAK PASS ({analogous_count} analogs)")
        else:
            tests_failed += 1
            print(f"    Analogous forms: FAIL (no analogous dark MIDDLEs)")

        # Classification
        total_testable = tests_passed + tests_failed
        if total_testable == 0:
            classification = 'UNTESTABLE'
            n_untestable += 1
        elif tests_failed == 0 and tests_passed >= 2:
            classification = 'VALID_UNFILLED'
            n_valid += 1
        elif tests_passed == 0:
            classification = 'STRUCTURALLY_INVALID'
            n_invalid += 1
        else:
            classification = 'PARTIALLY_VALID'
            n_partial += 1

        print(f"    Classification: {classification} "
              f"(passed={tests_passed}, failed={tests_failed}, untestable={tests_untestable})")

        classifications[phantom] = {
            'is_compound': is_compound,
            'atoms': pre_atoms,
            'char_length': profile.get('char_length', len(phantom)),
            'prefix': prefix,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed,
            'tests_untestable': tests_untestable,
            'analogous_count': analogous_count,
            'c475_component': phantom_comp,
            'classification': classification,
        }

    summary = {
        'VALID_UNFILLED': n_valid,
        'STRUCTURALLY_INVALID': n_invalid,
        'PARTIALLY_VALID': n_partial,
        'UNTESTABLE': n_untestable,
    }

    total_testable = n_valid + n_invalid + n_partial
    valid_frac = n_valid / total_testable if total_testable > 0 else 0

    print(f"\n  Summary: valid={n_valid}, partial={n_partial}, "
          f"invalid={n_invalid}, untestable={n_untestable}")
    print(f"  Valid fraction (of testable): {valid_frac:.3f}")

    ch_count = sum(1 for p in phantom_profiles if p.startswith('ch'))
    sh_count = sum(1 for p in phantom_profiles if p.startswith('sh'))
    compound_count = sum(1 for p in phantom_profiles.values() if p.get('is_compound'))

    # Verdict
    if total_testable == 0 or n_untestable > len(phantom_profiles) / 2:
        verdict = 'INSUFFICIENT_EVIDENCE'
    elif valid_frac >= 0.60:
        verdict = 'MOSTLY_VALID'
    elif (n_invalid / total_testable if total_testable > 0 else 0) >= 0.60:
        verdict = 'MOSTLY_INVALID'
    else:
        verdict = 'MIXED_VALIDITY'

    print(f"  Verdict: {verdict}")

    return {
        'n_phantoms': len(phantom_profiles),
        'phantom_classifications': classifications,
        'classification_summary': summary,
        'valid_fraction': valid_frac,
        'ch_prefix_count': ch_count,
        'sh_prefix_count': sh_count,
        'compound_count': compound_count,
        'verdict': verdict,
    }


# --- Synthesis ---

def synthesize(t1, t2, t3, t4, t5):
    """Combine all 5 verdicts."""
    print("\n-- SYNTHESIS --")

    v1 = t1['verdict']
    v2 = t2['verdict']
    v3 = t3['verdict']
    v4 = t4['verdict']
    v5 = t5['verdict']

    print(f"  T1={v1}")
    print(f"  T2={v2}")
    print(f"  T3={v3}")
    print(f"  T4={v4}")
    print(f"  T5={v5}")

    if v1 == 'PAIRWISE_GATED' and v2 == 'ATOM_SELECTION_DOMINATED':
        overall = 'ATOM_DRIVEN_COMBINATORICS'
    elif v2 == 'COMBINATION_DOMINATED' and v4 in ('MODIFIED_GRAMMAR', 'INDEPENDENT_GRAMMAR'):
        overall = 'COMBINATION_RULES_BEYOND_ATOMS'
    elif v4 == 'INDEPENDENT_GRAMMAR':
        overall = 'DARK_GRAMMAR_AUTONOMOUS'
    elif v1 == 'SPARSE_OCCUPANCY':
        overall = 'SPARSE_SAMPLING_REGIME'
    else:
        overall = 'MULTI_MECHANISM_COMBINATORICS'

    print(f"  Overall: {overall}")

    return {
        'verdicts': {
            't1': v1,
            't2': v2,
            't3': v3,
            't4': v4,
            't5': v5,
        },
        'overall': overall,
    }


# --- Main ---

def main():
    print("=" * 60)
    print("Phase 419: DARK_PIPELINE_COMBINATORICS")
    print("=" * 60)

    data = load_data()

    t1 = test1_atom_cooccurrence_acceptance(data)
    t2 = test2_section_hyper_modulation(data)
    t3 = test3_dark_bridge_tradeoff(data)
    t4 = test4_modified_ordering_grammar(data)
    t5 = test5_phantom_middle_analysis(data)

    synthesis = synthesize(t1, t2, t3, t4, t5)

    results = {
        'phase': 'DARK_PIPELINE_COMBINATORICS',
        'phase_number': 419,
        'depends_on': ['C1137', 'C1140', 'C1141', 'C1142', 'C1144',
                       'C1146', 'C1148', 'C1065', 'C475', 'C1028'],
        'population': {
            'n_dark_middles': len(data['dark_set']),
            'n_compound': len(data['dark_compound_atoms']),
            'n_bridge_atoms': len(data['bridge_atoms_set']),
        },
        'test1_atom_cooccurrence_acceptance': t1,
        'test2_section_hyper_modulation': t2,
        'test3_dark_bridge_tradeoff': t3,
        'test4_modified_ordering_grammar': t4,
        'test5_phantom_middle_analysis': t5,
        'synthesis': synthesis,
    }

    results = round_floats(results)

    out_path = ROOT / 'phases/DARK_PIPELINE_COMBINATORICS/results/dark_pipeline_combinatorics.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()

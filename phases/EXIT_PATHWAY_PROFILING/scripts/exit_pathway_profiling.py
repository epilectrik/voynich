#!/usr/bin/env python3
"""
EXIT_PATHWAY_PROFILING -- Phase 358
====================================
When the system leaves AXM, where does it go? Tests whether C458's
hazard/recovery asymmetry manifests at the exit-conditional level.

Critical predecessor: C1016 T3 tested C458 at raw transition probability
and found the OPPOSITE pattern (hazard CV=1.81, recovery CV=0.29).
Explanation: rare transitions inherently have high variance. This phase
uses EXIT-CONDITIONAL framing: "given that AXM IS exited, what fraction
of exits go to each target?" This normalizes out AXM attractor strength
(self-loop = 0.697) and removes the rare-event confound.

4 exit pathways (FL_HAZ + FL_SAFE merged -- FL_SAFE has ~1.4 exits/folio):
  FQ, FL, CC, AXm

Corpus-level expected (C1007): FQ=57.1%, FL=19.6%, CC=13.8%, AXm=9.4%

Pre-registered hypotheses:
  P1: FL exit fraction has LOWEST cross-folio CV (C458 hazard clamped)
  P2: FQ exit fraction has HIGHEST cross-folio CV (C458 recovery free)
  P3: FQ CV > FL CV (C458 asymmetry)
  P4: CV ranking stable under odd/even line split (robustness)
  P5: No pathway confounded with folio length (|rho| < 0.3)
  P6: FL variance not dominated by REGIME+section (eta2 < 0.50)
  P7: Effect size: CV(FQ) - CV(FL) >= 0.10 (structural separation)

Pipeline: S1-S8
  S1: Build per-folio 6x6 transition matrices + odd/even splits
  S2: Extract AXM exit distributions (exit-conditional, FL merged)
  S3: Cross-folio CV per pathway + folio length control + N_exits-weighted CV
  S4: Deviation profiles (folio delta from corpus-level expected)
  S5: Variance decomposition (eta-squared by REGIME, section, archetype)
  S6: Exit pathway correlations (pairwise Spearman + compositional null)
  S7: Odd/even stability (split-half CV ranking agreement)
  S8: Evaluate P1-P7
  S9: Into-AXM ingress analysis (mirror of egress)
  S10: AXM dwell duration analysis (time-to-exit by pathway)

Constraints respected:
  C976-C980: 6-state partition is fixed
  C1010: Canonical partition (AXM 32 classes, AXm 6 incl. class 45)
  C458: Hazard clamped, recovery free
  C1007: AXM exit skyline
  C1015: Full 6x6 transition matrix
  C1016: Folio archetypes, T3 reversal
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# -- Constants (C1010 canonical partition, Phase 339 canonical) --

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

# Exit pathways: FL merges FL_HAZ + FL_SAFE
EXIT_PATHWAYS = ['FQ', 'FL', 'CC', 'AXm']
CORPUS_EXIT_FRACTIONS = {'FQ': 0.571, 'FL': 0.196, 'CC': 0.138, 'AXm': 0.094}

MIN_TRANSITIONS = 50
MIN_AXM_EXITS = 5


# -- Data Loading --

def load_token_to_class():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        data = json.load(f)
    return data['token_to_class']


def load_regime_assignments():
    path = PROJECT_ROOT / 'phases' / 'OPS2_control_strategy_clustering' / 'ops2_folio_cluster_assignments.json'
    with open(path) as f:
        data = json.load(f)
    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def load_folio_archetypes():
    path = PROJECT_ROOT / 'phases' / 'FOLIO_MACRO_AUTOMATON_DECOMPOSITION' / 'results' / 'folio_macro_decomposition.json'
    with open(path) as f:
        data = json.load(f)
    folio_labels = data['t2_archetype_discovery'].get('folio_labels', {})
    return {k: int(v) for k, v in folio_labels.items()}


# -- S1: Build Per-Folio Transition Matrices --

def build_folio_data(token_to_class):
    """Build per-folio token sequences with odd/even line tracking.

    Returns:
        folio_line_states: {folio: {line_id: [state1, state2, ...]}}
        folio_sections: {folio: section}
        folio_line_numbers: {folio: {line_id: int}} for odd/even split
    """
    tx = Transcript()

    lines = defaultdict(list)
    folio_sections = {}
    folio_line_numbers = defaultdict(dict)

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        key = (token.folio, token.line)
        lines[key].append(w)
        folio_sections[token.folio] = token.section
        # Store line number for odd/even split
        line_num = int(token.line) if token.line.isdigit() else 0
        folio_line_numbers[token.folio][token.line] = line_num

    folio_line_states = defaultdict(dict)
    n_unmapped = 0

    for (folio, line_id), words in lines.items():
        line_states = []
        for w in words:
            cls = token_to_class.get(w)
            if cls is None:
                n_unmapped += 1
                continue
            state = CLASS_TO_STATE.get(int(cls))
            if state is None:
                n_unmapped += 1
                continue
            line_states.append(state)
        if line_states:
            folio_line_states[folio][line_id] = line_states

    print(f"  Loaded {len(folio_line_states)} folios, {n_unmapped} unmapped tokens")
    return dict(folio_line_states), folio_sections, dict(folio_line_numbers)


def compute_transitions_from_lines(line_dict):
    """Compute 6x6 transition count matrix from {line_id: [states]} dict."""
    trans_counts = np.zeros((N_STATES, N_STATES), dtype=int)
    state_counts = np.zeros(N_STATES, dtype=int)

    for states in line_dict.values():
        for s in states:
            state_counts[STATE_IDX[s]] += 1
        for i in range(len(states) - 1):
            trans_counts[STATE_IDX[states[i]], STATE_IDX[states[i+1]]] += 1

    return trans_counts, state_counts


def build_folio_matrices(folio_line_states, folio_line_numbers):
    """Build per-folio 6x6 matrices with odd/even line splits."""
    results = {}

    for folio, line_dict in folio_line_states.items():
        # Full matrix
        trans_counts, state_counts = compute_transitions_from_lines(line_dict)
        n_transitions = int(trans_counts.sum())

        trans_prob = None
        if n_transitions >= MIN_TRANSITIONS:
            row_sums = trans_counts.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums == 0, 1, row_sums)
            trans_prob = trans_counts / row_sums

        # Odd/even line split
        line_nums = folio_line_numbers.get(folio, {})
        odd_lines = {lid: states for lid, states in line_dict.items()
                     if line_nums.get(lid, 0) % 2 == 1}
        even_lines = {lid: states for lid, states in line_dict.items()
                      if line_nums.get(lid, 0) % 2 == 0}

        odd_counts, _ = compute_transitions_from_lines(odd_lines)
        even_counts, _ = compute_transitions_from_lines(even_lines)

        results[folio] = {
            'trans_counts': trans_counts,
            'state_counts': state_counts,
            'n_transitions': n_transitions,
            'trans_prob': trans_prob,
            'odd_counts': odd_counts,
            'even_counts': even_counts,
        }

    return results


# -- S2: Extract AXM Exit Distributions --

def extract_exit_distribution(trans_counts):
    """Extract exit-conditional distribution from AXM row.

    "Given that AXM IS exited, what fraction of exits go to each target?"
    Merges FL_HAZ + FL_SAFE into FL.

    Returns: dict {pathway: fraction} or None if insufficient exits.
    """
    axm_row = trans_counts[STATE_IDX['AXM'], :]
    axm_self = axm_row[STATE_IDX['AXM']]
    total_exits = axm_row.sum() - axm_self

    if total_exits < MIN_AXM_EXITS:
        return None, int(total_exits)

    # Map to 4 exit pathways (merge FL_HAZ + FL_SAFE)
    exit_counts = {
        'FQ':  int(axm_row[STATE_IDX['FQ']]),
        'FL':  int(axm_row[STATE_IDX['FL_HAZ']] + axm_row[STATE_IDX['FL_SAFE']]),
        'CC':  int(axm_row[STATE_IDX['CC']]),
        'AXm': int(axm_row[STATE_IDX['AXm']]),
    }

    exit_fracs = {p: c / total_exits for p, c in exit_counts.items()}

    return exit_fracs, int(total_exits)


def compute_all_exit_distributions(folio_matrices):
    """Compute exit distributions for all valid folios.

    Returns:
        exit_data: {folio: {'fracs': {pathway: frac}, 'n_exits': int}}
        Also computes odd/even splits.
    """
    exit_data = {}
    n_excluded_transitions = 0
    n_excluded_exits = 0

    for folio, fmat in folio_matrices.items():
        if fmat['trans_prob'] is None:
            n_excluded_transitions += 1
            continue

        fracs, n_exits = extract_exit_distribution(fmat['trans_counts'])
        if fracs is None:
            n_excluded_exits += 1
            continue

        # Odd/even splits
        odd_fracs, odd_n = extract_exit_distribution(fmat['odd_counts'])
        even_fracs, even_n = extract_exit_distribution(fmat['even_counts'])

        exit_data[folio] = {
            'fracs': fracs,
            'n_exits': n_exits,
            'odd_fracs': odd_fracs,
            'odd_n_exits': odd_n,
            'even_fracs': even_fracs,
            'even_n_exits': even_n,
        }

    print(f"  {len(exit_data)} folios with valid exit distributions")
    print(f"  Excluded: {n_excluded_transitions} (insufficient transitions), "
          f"{n_excluded_exits} (insufficient AXM exits)")

    return exit_data


# -- S3: Cross-Folio CV Analysis --

def compute_pathway_cvs(exit_data, folios):
    """Compute cross-folio CV for each exit pathway."""
    pathway_values = {p: [] for p in EXIT_PATHWAYS}
    n_exits_list = []

    for f in folios:
        fracs = exit_data[f]['fracs']
        for p in EXIT_PATHWAYS:
            pathway_values[p].append(fracs[p])
        n_exits_list.append(exit_data[f]['n_exits'])

    n_exits_arr = np.array(n_exits_list)
    results = {}

    for p in EXIT_PATHWAYS:
        vals = np.array(pathway_values[p])
        mean_val = vals.mean()
        std_val = vals.std()
        cv = std_val / mean_val if mean_val > 0 else float('inf')

        # N_exits-weighted CV (sensitivity check per expert recommendation)
        weights = n_exits_arr / n_exits_arr.sum()
        weighted_mean = np.average(vals, weights=weights)
        weighted_var = np.average((vals - weighted_mean) ** 2, weights=weights)
        weighted_std = np.sqrt(weighted_var)
        weighted_cv = weighted_std / weighted_mean if weighted_mean > 0 else float('inf')

        results[p] = {
            'mean': float(mean_val),
            'std': float(std_val),
            'cv': float(cv),
            'min': float(vals.min()),
            'max': float(vals.max()),
            'weighted_cv': float(weighted_cv),
        }

    return results


# -- S4: Deviation Profiles --

def compute_deviation_profiles(exit_data, folios):
    """Compute per-folio deviation from corpus-level expected exit rates."""
    profiles = {}
    for f in folios:
        fracs = exit_data[f]['fracs']
        deltas = {p: fracs[p] - CORPUS_EXIT_FRACTIONS[p] for p in EXIT_PATHWAYS}
        profiles[f] = deltas
    return profiles


# -- S5: Variance Decomposition --

def eta_squared_one_way(values, groups):
    """Compute eta-squared for one-way grouping."""
    grand_mean = np.mean(values)
    ss_total = np.sum((values - grand_mean) ** 2)
    if ss_total < 1e-15:
        return 0.0

    ss_between = 0
    for g in set(groups):
        mask = [i for i, gl in enumerate(groups) if gl == g]
        if mask:
            group_mean = np.mean([values[i] for i in mask])
            ss_between += len(mask) * (group_mean - grand_mean) ** 2

    return ss_between / ss_total


def variance_decomposition(exit_data, folios, regimes, sections, archetypes):
    """Eta-squared by REGIME, section, archetype per exit pathway."""
    regime_labels = [regimes.get(f, 'R0') for f in folios]
    section_labels = [sections.get(f, 'X') for f in folios]
    archetype_labels = [str(archetypes.get(f, -1)) for f in folios]
    combined_labels = [f"{r}_{s}" for r, s in zip(regime_labels, section_labels)]

    results = {}
    for p in EXIT_PATHWAYS:
        vals = np.array([exit_data[f]['fracs'][p] for f in folios])
        eta_regime = eta_squared_one_way(vals, regime_labels)
        eta_section = eta_squared_one_way(vals, section_labels)
        eta_combined = eta_squared_one_way(vals, combined_labels)
        eta_archetype = eta_squared_one_way(vals, archetype_labels)

        results[p] = {
            'eta2_regime': round(float(eta_regime), 4),
            'eta2_section': round(float(eta_section), 4),
            'eta2_regime_section': round(float(eta_combined), 4),
            'eta2_archetype': round(float(eta_archetype), 4),
            'residual_regime_section': round(float(1 - eta_combined), 4),
        }

    return results


# -- S6: Exit Pathway Correlations --

def pathway_correlations(exit_data, folios):
    """Pairwise Spearman correlations between exit pathways.

    Compositional null: K=4 pathways sum to 1, so null rho = -1/(K-1) = -0.333
    """
    pathway_arrs = {}
    for p in EXIT_PATHWAYS:
        pathway_arrs[p] = np.array([exit_data[f]['fracs'][p] for f in folios])

    null_rho = -1.0 / (len(EXIT_PATHWAYS) - 1)  # -0.333

    results = {'null_rho': round(null_rho, 4), 'pairs': {}}

    for i in range(len(EXIT_PATHWAYS)):
        for j in range(i + 1, len(EXIT_PATHWAYS)):
            p1, p2 = EXIT_PATHWAYS[i], EXIT_PATHWAYS[j]
            rho, p_val = stats.spearmanr(pathway_arrs[p1], pathway_arrs[p2])
            # Deviation from compositional null
            delta_rho = rho - null_rho
            key = f"{p1}_vs_{p2}"
            results['pairs'][key] = {
                'rho': round(float(rho), 4),
                'p_value': round(float(p_val), 6),
                'delta_from_null': round(float(delta_rho), 4),
                'exceeds_null': abs(delta_rho) > 0.15,
            }

    return results


# -- S7: Odd/Even Stability --

def compute_split_stability(exit_data, folios):
    """Compute CV from odd and even line splits, test ranking agreement."""
    # Only folios with valid splits
    split_folios = [f for f in folios
                    if exit_data[f]['odd_fracs'] is not None
                    and exit_data[f]['even_fracs'] is not None]

    if len(split_folios) < 20:
        return {'error': f'Only {len(split_folios)} folios with valid odd/even splits'}

    odd_cvs = {}
    even_cvs = {}

    for p in EXIT_PATHWAYS:
        odd_vals = np.array([exit_data[f]['odd_fracs'][p] for f in split_folios])
        even_vals = np.array([exit_data[f]['even_fracs'][p] for f in split_folios])

        odd_mean = odd_vals.mean()
        odd_std = odd_vals.std()
        odd_cvs[p] = float(odd_std / odd_mean) if odd_mean > 0 else float('inf')

        even_mean = even_vals.mean()
        even_std = even_vals.std()
        even_cvs[p] = float(even_std / even_mean) if even_mean > 0 else float('inf')

    # CV ranking agreement: do odd and even agree on which pathway has highest/lowest CV?
    odd_ranking = sorted(EXIT_PATHWAYS, key=lambda p: odd_cvs[p])
    even_ranking = sorted(EXIT_PATHWAYS, key=lambda p: even_cvs[p])

    # Spearman rank correlation on CV values
    odd_cv_arr = np.array([odd_cvs[p] for p in EXIT_PATHWAYS])
    even_cv_arr = np.array([even_cvs[p] for p in EXIT_PATHWAYS])
    rank_rho, rank_p = stats.spearmanr(odd_cv_arr, even_cv_arr)

    # Key checks: does lowest CV match? Does highest CV match?
    lowest_agrees = odd_ranking[0] == even_ranking[0]
    highest_agrees = odd_ranking[-1] == even_ranking[-1]

    return {
        'n_split_folios': len(split_folios),
        'odd_cvs': odd_cvs,
        'even_cvs': even_cvs,
        'odd_ranking': odd_ranking,
        'even_ranking': even_ranking,
        'rank_rho': round(float(rank_rho), 4),
        'rank_p': round(float(rank_p), 4),
        'lowest_cv_agrees': lowest_agrees,
        'highest_cv_agrees': highest_agrees,
    }


# -- S9: Into-AXM Ingress Analysis --

def extract_ingress_distribution(trans_counts):
    """Extract ingress-conditional distribution into AXM column.

    "Given that AXM IS entered (from outside), where did the system come from?"
    Merges FL_HAZ + FL_SAFE into FL.

    Returns: dict {pathway: fraction} or None if insufficient entries.
    """
    axm_col = trans_counts[:, STATE_IDX['AXM']]
    axm_self = axm_col[STATE_IDX['AXM']]
    total_entries = axm_col.sum() - axm_self

    if total_entries < MIN_AXM_EXITS:
        return None, int(total_entries)

    entry_counts = {
        'FQ':  int(axm_col[STATE_IDX['FQ']]),
        'FL':  int(axm_col[STATE_IDX['FL_HAZ']] + axm_col[STATE_IDX['FL_SAFE']]),
        'CC':  int(axm_col[STATE_IDX['CC']]),
        'AXm': int(axm_col[STATE_IDX['AXm']]),
    }

    entry_fracs = {p: c / total_entries for p, c in entry_counts.items()}
    return entry_fracs, int(total_entries)


def compute_all_ingress_distributions(folio_matrices):
    """Compute ingress distributions for all valid folios."""
    ingress_data = {}

    for folio, fmat in folio_matrices.items():
        if fmat['trans_prob'] is None:
            continue
        fracs, n_entries = extract_ingress_distribution(fmat['trans_counts'])
        if fracs is None:
            continue
        ingress_data[folio] = {'fracs': fracs, 'n_entries': n_entries}

    return ingress_data


def compute_ingress_cvs(ingress_data, folios):
    """Compute cross-folio CV for each ingress pathway."""
    pathway_values = {p: [] for p in EXIT_PATHWAYS}
    for f in folios:
        fracs = ingress_data[f]['fracs']
        for p in EXIT_PATHWAYS:
            pathway_values[p].append(fracs[p])

    results = {}
    for p in EXIT_PATHWAYS:
        vals = np.array(pathway_values[p])
        mean_val = vals.mean()
        std_val = vals.std()
        cv = std_val / mean_val if mean_val > 0 else float('inf')
        results[p] = {
            'mean': round(float(mean_val), 4),
            'std': round(float(std_val), 4),
            'cv': round(float(cv), 4),
        }
    return results


# -- S10: AXM Dwell Duration Analysis --

def extract_dwell_episodes(folio_line_states):
    """Extract AXM dwell episodes from per-folio line sequences.

    A dwell episode is a maximal consecutive run of AXM-state tokens within a line.
    For each episode, records: length, exit_target (state after run, or None if
    line-terminal), entry_source (state before run, or None if line-initial).

    Returns: {folio: [{'length': int, 'exit_target': str|None, 'entry_source': str|None}]}
    """
    folio_episodes = defaultdict(list)

    for folio, line_dict in folio_line_states.items():
        for line_id, states in line_dict.items():
            i = 0
            while i < len(states):
                if states[i] == 'AXM':
                    # Start of AXM run
                    run_start = i
                    entry_source = states[i - 1] if i > 0 else None
                    while i < len(states) and states[i] == 'AXM':
                        i += 1
                    run_length = i - run_start
                    exit_target = states[i] if i < len(states) else None

                    folio_episodes[folio].append({
                        'length': run_length,
                        'exit_target': exit_target,
                        'entry_source': entry_source,
                    })
                else:
                    i += 1

    return dict(folio_episodes)


def map_to_merged_pathway(state):
    """Map a 6-state name to the 4-pathway merge (FL_HAZ/FL_SAFE -> FL)."""
    if state in ('FL_HAZ', 'FL_SAFE'):
        return 'FL'
    if state in EXIT_PATHWAYS:
        return state
    return None


def analyze_dwell_durations(folio_episodes, valid_folios):
    """Per-folio and per-pathway dwell duration analysis.

    Tests: Does dwell-before-FL have lower CV than dwell-before-FQ?
    (C458 prediction: hazard exposure timing is clamped)
    """
    # Per-folio aggregate dwell stats
    folio_dwell_stats = {}
    # Per-pathway dwell collections (across all folios)
    pathway_dwells_all = {p: [] for p in EXIT_PATHWAYS}
    # Per-folio, per-pathway mean dwell
    folio_pathway_mean_dwell = {p: {} for p in EXIT_PATHWAYS}

    for folio in valid_folios:
        episodes = folio_episodes.get(folio, [])
        if not episodes:
            continue

        all_lengths = [e['length'] for e in episodes]
        # Only episodes with observed exits (not line-terminal)
        exited = [e for e in episodes if e['exit_target'] is not None]

        folio_dwell_stats[folio] = {
            'n_episodes': len(episodes),
            'n_exited': len(exited),
            'mean_dwell': float(np.mean(all_lengths)),
            'median_dwell': float(np.median(all_lengths)),
            'std_dwell': float(np.std(all_lengths)),
        }

        # Group exited episodes by pathway
        for e in exited:
            pathway = map_to_merged_pathway(e['exit_target'])
            if pathway:
                pathway_dwells_all[pathway].append(e['length'])

        # Per-pathway mean for this folio (for cross-folio CV)
        pathway_lengths = defaultdict(list)
        for e in exited:
            pathway = map_to_merged_pathway(e['exit_target'])
            if pathway:
                pathway_lengths[pathway].append(e['length'])

        for p in EXIT_PATHWAYS:
            if pathway_lengths[p]:
                folio_pathway_mean_dwell[p][folio] = float(np.mean(pathway_lengths[p]))

    # Corpus-level pathway dwell stats
    pathway_dwell_stats = {}
    for p in EXIT_PATHWAYS:
        if pathway_dwells_all[p]:
            vals = np.array(pathway_dwells_all[p])
            pathway_dwell_stats[p] = {
                'n_episodes': len(vals),
                'mean': round(float(vals.mean()), 3),
                'median': float(np.median(vals)),
                'std': round(float(vals.std()), 3),
                'cv': round(float(vals.std() / vals.mean()), 4) if vals.mean() > 0 else None,
            }

    # Cross-folio CV of per-folio mean dwell (per pathway)
    # This tests: is the typical dwell-before-FL consistent across programs?
    pathway_crossfolio_cv = {}
    for p in EXIT_PATHWAYS:
        means = list(folio_pathway_mean_dwell[p].values())
        if len(means) >= 10:
            arr = np.array(means)
            cv = float(arr.std() / arr.mean()) if arr.mean() > 0 else None
            pathway_crossfolio_cv[p] = {
                'n_folios': len(means),
                'mean_of_means': round(float(arr.mean()), 3),
                'std_of_means': round(float(arr.std()), 3),
                'cv_of_means': round(cv, 4) if cv is not None else None,
            }

    return folio_dwell_stats, pathway_dwell_stats, pathway_crossfolio_cv


# -- Main --

def main():
    start = time.time()

    print("Phase 358: EXIT_PATHWAY_PROFILING")
    print("=" * 70)

    # ---- Load data ----
    print("\nLoading data...")
    token_to_class = load_token_to_class()
    regimes = load_regime_assignments()
    archetypes = load_folio_archetypes()

    # ---- S1: Build per-folio matrices ----
    print("\n--- S1: BUILD PER-FOLIO TRANSITION MATRICES ---")
    folio_line_states, folio_sections, folio_line_numbers = build_folio_data(token_to_class)
    folio_matrices = build_folio_matrices(folio_line_states, folio_line_numbers)

    n_sufficient = sum(1 for d in folio_matrices.values() if d['trans_prob'] is not None)
    print(f"  {n_sufficient} folios with >= {MIN_TRANSITIONS} transitions")

    # ---- S2: Extract exit distributions ----
    print("\n--- S2: EXTRACT AXM EXIT DISTRIBUTIONS ---")
    exit_data = compute_all_exit_distributions(folio_matrices)
    valid_folios = sorted(exit_data.keys())
    n = len(valid_folios)

    # Corpus-level exit fractions (sanity check vs C1007)
    total_exits_corpus = sum(exit_data[f]['n_exits'] for f in valid_folios)
    corpus_fracs = {p: 0.0 for p in EXIT_PATHWAYS}
    for f in valid_folios:
        for p in EXIT_PATHWAYS:
            corpus_fracs[p] += exit_data[f]['fracs'][p] * exit_data[f]['n_exits']
    corpus_fracs = {p: v / total_exits_corpus for p, v in corpus_fracs.items()}

    print(f"\n  Corpus-level exit fractions (exit-count weighted):")
    print(f"  {'Pathway':<8} {'Observed':>10} {'Expected':>10} {'Delta':>10}")
    for p in EXIT_PATHWAYS:
        delta = corpus_fracs[p] - CORPUS_EXIT_FRACTIONS[p]
        print(f"  {p:<8} {corpus_fracs[p]:>10.4f} {CORPUS_EXIT_FRACTIONS[p]:>10.4f} {delta:>+10.4f}")

    # ---- S3: Cross-folio CV analysis ----
    print(f"\n--- S3: CROSS-FOLIO CV ANALYSIS (n={n}) ---")
    cv_results = compute_pathway_cvs(exit_data, valid_folios)

    print(f"\n  {'Pathway':<8} {'Mean':>8} {'Std':>8} {'CV':>8} {'WtCV':>8} {'Min':>8} {'Max':>8}")
    for p in EXIT_PATHWAYS:
        r = cv_results[p]
        print(f"  {p:<8} {r['mean']:>8.4f} {r['std']:>8.4f} {r['cv']:>8.4f} "
              f"{r['weighted_cv']:>8.4f} {r['min']:>8.4f} {r['max']:>8.4f}")

    # CV ranking
    cv_ranking = sorted(EXIT_PATHWAYS, key=lambda p: cv_results[p]['cv'])
    print(f"\n  CV ranking (low to high): {' < '.join(cv_ranking)}")

    # Folio length control (Spearman)
    folio_lengths = np.array([folio_matrices[f]['state_counts'].sum() for f in valid_folios])
    print(f"\n  Folio length confound check (Spearman with token count):")
    length_confounds = {}
    for p in EXIT_PATHWAYS:
        vals = np.array([exit_data[f]['fracs'][p] for f in valid_folios])
        rho, p_val = stats.spearmanr(vals, folio_lengths)
        length_confounds[p] = {'rho': round(float(rho), 4), 'p_value': round(float(p_val), 4)}
        marker = " ***CONFOUNDED" if abs(rho) >= 0.3 else ""
        print(f"    {p:<8} rho={rho:+.4f} (p={p_val:.4f}){marker}")

    # ---- S4: Deviation profiles ----
    print(f"\n--- S4: DEVIATION PROFILES ---")
    deviations = compute_deviation_profiles(exit_data, valid_folios)

    # Summarize deviation magnitudes
    print(f"\n  Mean absolute deviation from corpus expected:")
    for p in EXIT_PATHWAYS:
        devs = [abs(deviations[f][p]) for f in valid_folios]
        print(f"    {p:<8} MAD={np.mean(devs):.4f}  Max|dev|={max(devs):.4f}")

    # ---- S5: Variance decomposition ----
    print(f"\n--- S5: VARIANCE DECOMPOSITION (eta-squared) ---")
    eta_results = variance_decomposition(exit_data, valid_folios, regimes, folio_sections, archetypes)

    print(f"\n  {'Pathway':<8} {'REGIME':>10} {'Section':>10} {'R+S':>10} {'Archetype':>10} {'Residual':>10}")
    for p in EXIT_PATHWAYS:
        r = eta_results[p]
        print(f"  {p:<8} {r['eta2_regime']:>10.4f} {r['eta2_section']:>10.4f} "
              f"{r['eta2_regime_section']:>10.4f} {r['eta2_archetype']:>10.4f} "
              f"{r['residual_regime_section']:>10.4f}")

    # ---- S6: Exit pathway correlations ----
    print(f"\n--- S6: EXIT PATHWAY CORRELATIONS ---")
    corr_results = pathway_correlations(exit_data, valid_folios)

    print(f"\n  Compositional null rho = {corr_results['null_rho']}")
    print(f"\n  {'Pair':<15} {'rho':>8} {'p':>10} {'delta':>8} {'Exceeds null?':>15}")
    for key, pair in corr_results['pairs'].items():
        exceeds = "YES" if pair['exceeds_null'] else "no"
        print(f"  {key:<15} {pair['rho']:>8.4f} {pair['p_value']:>10.6f} "
              f"{pair['delta_from_null']:>+8.4f} {exceeds:>15}")

    # ---- S7: Odd/even stability ----
    print(f"\n--- S7: ODD/EVEN STABILITY ---")
    stability = compute_split_stability(exit_data, valid_folios)

    if 'error' not in stability:
        print(f"\n  n={stability['n_split_folios']} folios with valid splits")
        print(f"\n  {'Pathway':<8} {'Odd CV':>10} {'Even CV':>10}")
        for p in EXIT_PATHWAYS:
            print(f"  {p:<8} {stability['odd_cvs'][p]:>10.4f} {stability['even_cvs'][p]:>10.4f}")
        print(f"\n  Odd ranking:  {' < '.join(stability['odd_ranking'])}")
        print(f"  Even ranking: {' < '.join(stability['even_ranking'])}")
        print(f"  Rank correlation: rho={stability['rank_rho']}, p={stability['rank_p']}")
        print(f"  Lowest CV agrees:  {stability['lowest_cv_agrees']}")
        print(f"  Highest CV agrees: {stability['highest_cv_agrees']}")
    else:
        print(f"  {stability['error']}")

    # ---- S8: Evaluate P1-P7 ----
    print(f"\n{'='*70}")
    print("  S8: HYPOTHESIS EVALUATION")
    print(f"{'='*70}")

    predictions = {}

    # P1: FL exit fraction has LOWEST cross-folio CV
    lowest_cv_pathway = cv_ranking[0]
    p1_pass = lowest_cv_pathway == 'FL'
    predictions['P1'] = {
        'description': 'FL exit fraction has LOWEST cross-folio CV (C458 hazard clamped)',
        'result': f'Lowest CV pathway: {lowest_cv_pathway} (CV={cv_results[lowest_cv_pathway]["cv"]:.4f})',
        'fl_cv': cv_results['FL']['cv'],
        'pass': p1_pass,
    }

    # P2: FQ exit fraction has HIGHEST cross-folio CV
    highest_cv_pathway = cv_ranking[-1]
    p2_pass = highest_cv_pathway == 'FQ'
    predictions['P2'] = {
        'description': 'FQ exit fraction has HIGHEST cross-folio CV (C458 recovery free)',
        'result': f'Highest CV pathway: {highest_cv_pathway} (CV={cv_results[highest_cv_pathway]["cv"]:.4f})',
        'fq_cv': cv_results['FQ']['cv'],
        'pass': p2_pass,
    }

    # P3: FQ CV > FL CV
    fq_cv = cv_results['FQ']['cv']
    fl_cv = cv_results['FL']['cv']
    p3_pass = fq_cv > fl_cv
    predictions['P3'] = {
        'description': 'FQ CV > FL CV (C458 asymmetry)',
        'result': f'FQ CV={fq_cv:.4f}, FL CV={fl_cv:.4f}, diff={fq_cv - fl_cv:.4f}',
        'pass': p3_pass,
    }

    # P4: CV ranking stable under odd/even split
    if 'error' not in stability:
        p4_pass = stability['lowest_cv_agrees'] and stability['highest_cv_agrees']
        predictions['P4'] = {
            'description': 'CV ranking stable under odd/even line split',
            'result': f'Lowest agrees={stability["lowest_cv_agrees"]}, '
                      f'Highest agrees={stability["highest_cv_agrees"]}, '
                      f'rank rho={stability["rank_rho"]}',
            'pass': p4_pass,
        }
    else:
        predictions['P4'] = {
            'description': 'CV ranking stable under odd/even line split',
            'result': stability['error'],
            'pass': False,
        }

    # P5: No pathway confounded with folio length (|rho| < 0.3)
    max_length_rho = max(abs(length_confounds[p]['rho']) for p in EXIT_PATHWAYS)
    p5_pass = max_length_rho < 0.3
    worst_p = max(EXIT_PATHWAYS, key=lambda p: abs(length_confounds[p]['rho']))
    predictions['P5'] = {
        'description': 'No pathway confounded with folio length (|rho| < 0.3)',
        'result': f'Max |rho|={max_length_rho:.4f} ({worst_p})',
        'length_confounds': length_confounds,
        'pass': p5_pass,
    }

    # P6: FL variance not dominated by REGIME+section (eta2 < 0.50)
    fl_eta2 = eta_results['FL']['eta2_regime_section']
    p6_pass = fl_eta2 < 0.50
    predictions['P6'] = {
        'description': 'FL variance not dominated by REGIME+section (eta2 < 0.50)',
        'result': f'FL eta2(REGIME+section)={fl_eta2:.4f}',
        'pass': p6_pass,
    }

    # P7: Effect size: CV(FQ) - CV(FL) >= 0.10
    cv_diff = fq_cv - fl_cv
    p7_pass = cv_diff >= 0.10
    predictions['P7'] = {
        'description': 'Effect size: CV(FQ) - CV(FL) >= 0.10',
        'result': f'CV(FQ) - CV(FL) = {cv_diff:.4f}',
        'pass': p7_pass,
    }

    # Print summary
    n_pass = sum(1 for p in predictions.values() if p['pass'])
    n_total = len(predictions)

    for pk, pv in sorted(predictions.items()):
        status = 'PASS' if pv['pass'] else 'FAIL'
        print(f"  {pk}: {pv['description']}")
        print(f"      {pv['result']} -> {status}")

    print(f"\n  VERDICT: {n_pass}/{n_total} PASS")

    if n_pass >= 5:
        verdict = 'EXIT_PATHWAY_ASYMMETRY_CONFIRMED'
    elif n_pass >= 3:
        verdict = 'EXIT_PATHWAY_ASYMMETRY_SUPPORTED'
    else:
        verdict = 'EXIT_PATHWAY_ASYMMETRY_NOT_FOUND'
    print(f"  {verdict}")

    # ---- S9: Into-AXM Ingress Analysis ----
    print(f"\n{'='*70}")
    print("  S9: INTO-AXM INGRESS ANALYSIS (mirror of egress)")
    print(f"{'='*70}")

    ingress_data = compute_all_ingress_distributions(folio_matrices)
    ingress_folios = sorted(f for f in ingress_data if f in set(valid_folios))
    print(f"\n  {len(ingress_folios)} folios with valid ingress distributions")

    # Corpus-level ingress fractions
    total_entries = sum(ingress_data[f]['n_entries'] for f in ingress_folios)
    corpus_ingress = {p: 0.0 for p in EXIT_PATHWAYS}
    for f in ingress_folios:
        for p in EXIT_PATHWAYS:
            corpus_ingress[p] += ingress_data[f]['fracs'][p] * ingress_data[f]['n_entries']
    corpus_ingress = {p: v / total_entries for p, v in corpus_ingress.items()}

    print(f"\n  Corpus-level ingress fractions (entry-count weighted):")
    print(f"  {'Source':<8} {'Ingress':>10} {'Egress':>10}")
    for p in EXIT_PATHWAYS:
        print(f"  {p:<8} {corpus_ingress[p]:>10.4f} {corpus_fracs[p]:>10.4f}")

    # Ingress CVs
    ingress_cvs = compute_ingress_cvs(ingress_data, ingress_folios)
    print(f"\n  Cross-folio CV comparison (Ingress vs Egress):")
    print(f"  {'Pathway':<8} {'Ingress CV':>12} {'Egress CV':>12} {'Delta':>10}")
    for p in EXIT_PATHWAYS:
        i_cv = ingress_cvs[p]['cv']
        e_cv = cv_results[p]['cv']
        delta = i_cv - e_cv
        print(f"  {p:<8} {i_cv:>12.4f} {e_cv:>12.4f} {delta:>+10.4f}")

    ingress_cv_ranking = sorted(EXIT_PATHWAYS, key=lambda p: ingress_cvs[p]['cv'])
    print(f"\n  Ingress CV ranking: {' < '.join(ingress_cv_ranking)}")
    print(f"  Egress CV ranking:  {' < '.join(cv_ranking)}")

    # Ingress-egress symmetry: is the ranking the same?
    ingress_egress_same_ranking = ingress_cv_ranking == cv_ranking
    print(f"  Rankings identical: {ingress_egress_same_ranking}")

    # Ingress pathway correlations
    ingress_corrs = {}
    for p in EXIT_PATHWAYS:
        egress_vals = np.array([exit_data[f]['fracs'][p] for f in ingress_folios])
        ingress_vals = np.array([ingress_data[f]['fracs'][p] for f in ingress_folios])
        rho, p_val = stats.spearmanr(egress_vals, ingress_vals)
        ingress_corrs[p] = {'rho': round(float(rho), 4), 'p_value': round(float(p_val), 6)}
        print(f"  Ingress-egress correlation ({p}): rho={rho:.4f} (p={p_val:.6f})")

    s9_results = {
        'n_folios': len(ingress_folios),
        'total_entries': total_entries,
        'corpus_ingress_fractions': {p: round(v, 4) for p, v in corpus_ingress.items()},
        'ingress_cvs': ingress_cvs,
        'ingress_cv_ranking': ingress_cv_ranking,
        'ingress_egress_same_ranking': ingress_egress_same_ranking,
        'ingress_egress_correlations': ingress_corrs,
    }

    # ---- S10: AXM Dwell Duration Analysis ----
    print(f"\n{'='*70}")
    print("  S10: AXM DWELL DURATION ANALYSIS")
    print(f"{'='*70}")

    folio_episodes = extract_dwell_episodes(folio_line_states)
    folio_dwell_stats, pathway_dwell_stats, pathway_crossfolio_cv = \
        analyze_dwell_durations(folio_episodes, valid_folios)

    print(f"\n  {len(folio_dwell_stats)} folios with dwell episodes")

    # Corpus-level pathway dwell stats
    print(f"\n  Corpus-level dwell before exit (all episodes):")
    print(f"  {'Pathway':<8} {'N':>8} {'Mean':>8} {'Median':>8} {'Std':>8} {'CV':>8}")
    for p in EXIT_PATHWAYS:
        if p in pathway_dwell_stats:
            s = pathway_dwell_stats[p]
            cv_str = f"{s['cv']:.4f}" if s['cv'] is not None else "N/A"
            print(f"  {p:<8} {s['n_episodes']:>8} {s['mean']:>8.3f} {s['median']:>8.1f} "
                  f"{s['std']:>8.3f} {cv_str:>8}")

    # Cross-folio CV of per-folio mean dwell
    print(f"\n  Cross-folio CV of per-folio mean dwell-before-exit:")
    print(f"  {'Pathway':<8} {'N folios':>10} {'Mean':>8} {'Std':>8} {'CV':>8}")
    dwell_cv_ranking = []
    for p in EXIT_PATHWAYS:
        if p in pathway_crossfolio_cv:
            s = pathway_crossfolio_cv[p]
            cv_str = f"{s['cv_of_means']:.4f}" if s['cv_of_means'] is not None else "N/A"
            print(f"  {p:<8} {s['n_folios']:>10} {s['mean_of_means']:>8.3f} "
                  f"{s['std_of_means']:>8.3f} {cv_str:>8}")
            if s['cv_of_means'] is not None:
                dwell_cv_ranking.append((p, s['cv_of_means']))

    if dwell_cv_ranking:
        dwell_cv_ranking.sort(key=lambda x: x[1])
        print(f"\n  Dwell CV ranking: {' < '.join(p for p, _ in dwell_cv_ranking)}")

        # Key test: does FL dwell have lower cross-folio CV than FQ dwell?
        fl_dwell_cv = dict(dwell_cv_ranking).get('FL')
        fq_dwell_cv = dict(dwell_cv_ranking).get('FQ')
        if fl_dwell_cv is not None and fq_dwell_cv is not None:
            print(f"\n  C458 timing test: FL dwell CV={fl_dwell_cv:.4f}, FQ dwell CV={fq_dwell_cv:.4f}")
            if fl_dwell_cv < fq_dwell_cv:
                print(f"    FL dwell MORE consistent -> C458 timing signal PRESENT")
            else:
                print(f"    FL dwell NOT more consistent -> C458 timing signal ABSENT")

    s10_results = {
        'n_folios_with_episodes': len(folio_dwell_stats),
        'pathway_dwell_stats': pathway_dwell_stats,
        'pathway_crossfolio_cv': pathway_crossfolio_cv,
        'dwell_cv_ranking': [(p, cv) for p, cv in dwell_cv_ranking] if dwell_cv_ranking else [],
    }

    # ---- Write results ----
    results = {
        'phase_name': 'EXIT_PATHWAY_PROFILING',
        'phase_number': 358,
        'n_folios': n,
        'total_exits': total_exits_corpus,
        'corpus_exit_fractions_observed': {p: round(v, 4) for p, v in corpus_fracs.items()},
        'corpus_exit_fractions_expected': CORPUS_EXIT_FRACTIONS,
        's3_cv_analysis': cv_results,
        's3_cv_ranking': cv_ranking,
        's3_length_confounds': length_confounds,
        's4_deviation_summary': {
            p: {
                'mean_abs_deviation': round(float(np.mean([abs(deviations[f][p]) for f in valid_folios])), 4),
                'max_abs_deviation': round(float(max(abs(deviations[f][p]) for f in valid_folios)), 4),
            }
            for p in EXIT_PATHWAYS
        },
        's5_variance_decomposition': eta_results,
        's6_pathway_correlations': corr_results,
        's7_stability': stability,
        's9_ingress_analysis': s9_results,
        's10_dwell_analysis': s10_results,
        'predictions': predictions,
        'n_pass': n_pass,
        'n_total': n_total,
        'verdict': verdict,
        'folio_data': {
            f: {
                'exit_fracs': exit_data[f]['fracs'],
                'n_exits': exit_data[f]['n_exits'],
                'deviations': deviations[f],
                'regime': regimes.get(f, 'R0'),
                'section': folio_sections.get(f, 'X'),
                'archetype': archetypes.get(f, -1),
                'n_tokens': int(folio_matrices[f]['state_counts'].sum()),
            }
            for f in valid_folios
        },
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'exit_pathway_profiling.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - start
    print(f"\nResults written to: {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == '__main__':
    main()

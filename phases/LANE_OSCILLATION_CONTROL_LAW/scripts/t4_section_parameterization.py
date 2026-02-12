#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4: Section Parameterization

Tests whether section-specific first-order Markov transition matrices fully
account for observed oscillation dynamics. Compares predicted vs observed
statistics across multiple metrics (alternation rate, run-length distributions,
stationary distribution, transition entropy).

Method:
  - Load T1 section-stratified transition matrices
  - Compute observed per-section statistics from raw data
  - Simulate 10,000 synthetic EN lane sequences per section using T1 matrices
  - Compare observed vs simulated across all metrics with 95% CIs

Targets (C650):
  - BIO alternation ~ 0.593-0.608
  - HERBAL alternation ~ 0.427-0.464
  - Predicted within 0.02 of observed for all sections
  - Run-length distributions should match
  - Transition entropy within 0.1 bits

Falsification:
  - Any metric observed value outside simulated 95% CI for majority of sections
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load T1 Results & Rebuild Observed Data
# ============================================================
print("=" * 60)
print("T4: Section Parameterization")
print("=" * 60)

# Load T1 results for section transition matrices
with open(RESULTS_DIR / 't1_transition_matrices.json') as f:
    t1 = json.load(f)

section_names = {'B': 'BIO', 'H': 'HERBAL_B', 'S': 'STARS', 'C': 'COSMO', 'T': 'RECIPE'}

# Load class token map and EN census (same pattern as T1)
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'

with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data (identical to T1)
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = token_to_class.get(w)
    m = morph.extract(w)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_cc = cls in CC_CLASSES if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False

    lines[(token.folio, token.line)].append({
        'word': w,
        'class': cls,
        'en_subfamily': en_subfamily,
        'is_cc': is_cc,
        'is_haz': is_haz,
        'section': token.section,
        'folio': token.folio,
    })

# Build EN sequences with filtering (identical to T1)
MIN_EN = 2

en_line_data = []
for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue

        near_haz = False
        near_cc = False
        for j in range(max(0, i - 2), min(len(toks), i + 3)):
            if j == i:
                continue
            if toks[j]['is_haz']:
                near_haz = True
            if toks[j]['is_cc']:
                near_cc = True

        en_positions.append({
            'pos': i,
            'lane': t['en_subfamily'],
            'near_haz': near_haz,
            'near_cc': near_cc,
        })

    if len(en_positions) >= MIN_EN:
        en_line_data.append({
            'folio': folio,
            'line': line_num,
            'section': toks[0]['section'],
            'en_positions': en_positions,
            'en_seq': [e['lane'] for e in en_positions],
        })

print(f"Lines with >= {MIN_EN} EN tokens: {len(en_line_data)}")

# Group by section
section_lines = defaultdict(list)
for d in en_line_data:
    section_lines[d['section']].append(d)


# ============================================================
# SECTION 2: Extract Filtered EN Lane Sequences Per Section
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Extract Filtered EN Lane Sequences Per Section")
print("=" * 60)

MIN_TRANSITIONS = 50  # Skip sections with fewer than 50 transitions


def get_filtered_sequences(line_data):
    """Extract filtered lane sequences (excluding hazard/CC-adjacent).

    Returns list of lane sequences (one per line), where each sequence
    contains only the filtered EN tokens for that line.
    """
    sequences = []
    for d in line_data:
        seq = d['en_positions']
        filtered_lanes = []
        for i in range(len(seq)):
            if seq[i]['near_haz'] or seq[i]['near_cc']:
                continue
            filtered_lanes.append(seq[i]['lane'])
        if len(filtered_lanes) >= 2:
            sequences.append(filtered_lanes)
    return sequences


def get_filtered_transitions(line_data):
    """Extract filtered transitions (both endpoints must be clean)."""
    transitions = []
    for d in line_data:
        seq = d['en_positions']
        for i in range(len(seq) - 1):
            if seq[i]['near_haz'] or seq[i]['near_cc']:
                continue
            if seq[i + 1]['near_haz'] or seq[i + 1]['near_cc']:
                continue
            transitions.append((seq[i]['lane'], seq[i + 1]['lane']))
    return transitions


# ============================================================
# SECTION 3: Compute Observed Statistics
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Compute Observed Statistics Per Section")
print("=" * 60)


def compute_run_lengths(sequences, lane):
    """Compute run-length distribution for a specific lane across all sequences.

    A run = consecutive tokens in the same lane within a single sequence (line).
    """
    runs = []
    for seq in sequences:
        current_run = 0
        for token in seq:
            if token == lane:
                current_run += 1
            else:
                if current_run > 0:
                    runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)
    return runs


def compute_alternation_rate(sequences):
    """Compute alternation rate: fraction of transitions that change lane."""
    n_alt = 0
    n_total = 0
    for seq in sequences:
        for i in range(len(seq) - 1):
            n_total += 1
            if seq[i] != seq[i + 1]:
                n_alt += 1
    if n_total == 0:
        return 0.0
    return n_alt / n_total


def compute_qo_fraction(sequences):
    """Compute QO fraction (stationary distribution estimate)."""
    n_qo = 0
    n_total = 0
    for seq in sequences:
        for token in seq:
            n_total += 1
            if token == 'QO':
                n_qo += 1
    if n_total == 0:
        return 0.0
    return n_qo / n_total


def compute_transition_entropy(transitions):
    """Compute transition entropy.

    H = pi_QO * H_QO + pi_CHSH * H_CHSH
    where H_s = -sum(T[s][t] * log2(T[s][t]) for t in states)
    and pi is the empirical state frequency among transition origins.
    """
    counts = {'QO': {'QO': 0, 'CHSH': 0}, 'CHSH': {'QO': 0, 'CHSH': 0}}
    for fr, to in transitions:
        counts[fr][to] += 1

    # State frequencies (from origin states)
    n_from_qo = counts['QO']['QO'] + counts['QO']['CHSH']
    n_from_chsh = counts['CHSH']['QO'] + counts['CHSH']['CHSH']
    n_total = n_from_qo + n_from_chsh
    if n_total == 0:
        return 0.0

    pi_qo = n_from_qo / n_total
    pi_chsh = n_from_chsh / n_total

    # Per-state entropy
    def state_entropy(from_state):
        total = sum(counts[from_state].values())
        if total == 0:
            return 0.0
        h = 0.0
        for to_state in ['QO', 'CHSH']:
            p = counts[from_state][to_state] / total
            if p > 0:
                h -= p * np.log2(p)
        return h

    h_qo = state_entropy('QO')
    h_chsh = state_entropy('CHSH')

    return pi_qo * h_qo + pi_chsh * h_chsh


def compute_run_length_histogram(runs, max_run=10):
    """Compute run-length histogram up to max_run (last bin is max_run+)."""
    hist = {}
    for r in runs:
        key = min(r, max_run)
        hist[key] = hist.get(key, 0) + 1
    total = len(runs)
    if total == 0:
        return {}
    return {str(k): v / total for k, v in sorted(hist.items())}


def compute_all_observed_stats(sequences, transitions):
    """Compute all observed statistics for a section."""
    alt_rate = compute_alternation_rate(sequences)
    qo_fraction = compute_qo_fraction(sequences)
    trans_entropy = compute_transition_entropy(transitions)

    qo_runs = compute_run_lengths(sequences, 'QO')
    chsh_runs = compute_run_lengths(sequences, 'CHSH')

    stats = {
        'alternation_rate': float(alt_rate),
        'qo_fraction': float(qo_fraction),
        'transition_entropy': float(trans_entropy),
        'n_transitions': len(transitions),
        'n_sequences': len(sequences),
        'n_tokens': sum(len(s) for s in sequences),
        'qo_run_lengths': {
            'mean': float(np.mean(qo_runs)) if qo_runs else 0.0,
            'median': float(np.median(qo_runs)) if qo_runs else 0.0,
            'max': int(max(qo_runs)) if qo_runs else 0,
            'count': len(qo_runs),
            'histogram': compute_run_length_histogram(qo_runs),
        },
        'chsh_run_lengths': {
            'mean': float(np.mean(chsh_runs)) if chsh_runs else 0.0,
            'median': float(np.median(chsh_runs)) if chsh_runs else 0.0,
            'max': int(max(chsh_runs)) if chsh_runs else 0,
            'count': len(chsh_runs),
            'histogram': compute_run_length_histogram(chsh_runs),
        },
    }
    return stats


# Compute observed stats per section
observed_stats = {}
for sec in sorted(section_lines.keys()):
    seqs = get_filtered_sequences(section_lines[sec])
    trans = get_filtered_transitions(section_lines[sec])

    if len(trans) < MIN_TRANSITIONS:
        print(f"  Section {sec} ({section_names.get(sec, sec)}): {len(trans)} transitions < {MIN_TRANSITIONS}, SKIPPING")
        continue

    stats = compute_all_observed_stats(seqs, trans)
    observed_stats[sec] = stats
    name = section_names.get(sec, sec)
    print(f"\n  Section {sec} ({name}): n_trans={stats['n_transitions']}, n_seq={stats['n_sequences']}")
    print(f"    Alternation rate: {stats['alternation_rate']:.4f}")
    print(f"    QO fraction:     {stats['qo_fraction']:.4f}")
    print(f"    Trans entropy:   {stats['transition_entropy']:.4f} bits")
    print(f"    QO runs:  mean={stats['qo_run_lengths']['mean']:.3f}, median={stats['qo_run_lengths']['median']:.1f}, max={stats['qo_run_lengths']['max']}")
    print(f"    CHSH runs: mean={stats['chsh_run_lengths']['mean']:.3f}, median={stats['chsh_run_lengths']['median']:.1f}, max={stats['chsh_run_lengths']['max']}")


# ============================================================
# SECTION 4: Simulate from T1 Transition Matrices
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Simulate from T1 Transition Matrices")
print("=" * 60)

N_SIMS = 10000
rng = np.random.default_rng(42)


def simulate_lane_sequence(matrix, length, rng):
    """Simulate a single lane sequence from a 2-state Markov chain.

    matrix: dict with QO->QO, QO->CHSH, CHSH->QO, CHSH->CHSH probabilities
    length: number of tokens in the sequence
    rng: numpy random generator

    Returns: list of 'QO' or 'CHSH' strings
    """
    if length < 1:
        return []

    # Stationary distribution for initial state
    p_qc = matrix['CHSH']['QO']
    p_cq = matrix['QO']['CHSH']
    denom = p_qc + p_cq
    if denom == 0:
        pi_qo = 0.5
    else:
        pi_qo = p_qc / denom

    # Draw initial state from stationary distribution
    state = 'QO' if rng.random() < pi_qo else 'CHSH'
    seq = [state]

    for _ in range(length - 1):
        p_switch = matrix[state]['CHSH' if state == 'QO' else 'QO']
        if rng.random() < p_switch:
            state = 'CHSH' if state == 'QO' else 'QO'
        seq.append(state)

    return seq


def simulate_section(matrix, line_lengths, n_sims, rng):
    """Run n_sims simulations for a section.

    For each simulation, generate synthetic sequences matching observed line lengths,
    then compute all statistics.

    Returns dict of metric arrays (each length n_sims).
    """
    sim_alt = np.zeros(n_sims)
    sim_qo_frac = np.zeros(n_sims)
    sim_entropy = np.zeros(n_sims)
    sim_qo_run_mean = np.zeros(n_sims)
    sim_chsh_run_mean = np.zeros(n_sims)

    for sim_i in range(n_sims):
        all_seqs = []
        all_trans = []

        for length in line_lengths:
            seq = simulate_lane_sequence(matrix, length, rng)
            all_seqs.append(seq)
            for j in range(len(seq) - 1):
                all_trans.append((seq[j], seq[j + 1]))

        sim_alt[sim_i] = compute_alternation_rate(all_seqs)
        sim_qo_frac[sim_i] = compute_qo_fraction(all_seqs)
        sim_entropy[sim_i] = compute_transition_entropy(all_trans)

        qo_runs = compute_run_lengths(all_seqs, 'QO')
        chsh_runs = compute_run_lengths(all_seqs, 'CHSH')
        sim_qo_run_mean[sim_i] = float(np.mean(qo_runs)) if qo_runs else 0.0
        sim_chsh_run_mean[sim_i] = float(np.mean(chsh_runs)) if chsh_runs else 0.0

    return {
        'alternation_rate': sim_alt,
        'qo_fraction': sim_qo_frac,
        'transition_entropy': sim_entropy,
        'qo_run_mean': sim_qo_run_mean,
        'chsh_run_mean': sim_chsh_run_mean,
    }


# Build transition matrix dicts from T1 results for simulation
def build_matrix_dict(sec_data):
    """Build nested dict matrix from T1 section data."""
    return {
        'QO': {
            'QO': 1.0 - sec_data['QO_to_CHSH'],
            'CHSH': sec_data['QO_to_CHSH'],
        },
        'CHSH': {
            'QO': sec_data['CHSH_to_QO'],
            'CHSH': 1.0 - sec_data['CHSH_to_QO'],
        },
    }


# Run simulations per section
simulated_stats = {}
for sec in sorted(observed_stats.keys()):
    if sec not in t1['section_matrices']:
        print(f"  Section {sec}: no T1 matrix available, skipping")
        continue

    name = section_names.get(sec, sec)
    sec_mat = build_matrix_dict(t1['section_matrices'][sec])

    # Get observed line lengths (filtered sequence lengths)
    seqs = get_filtered_sequences(section_lines[sec])
    line_lengths = [len(s) for s in seqs]

    print(f"\n  Simulating section {sec} ({name}): {N_SIMS} simulations, {len(line_lengths)} lines...")

    sim_results = simulate_section(sec_mat, line_lengths, N_SIMS, rng)

    # Compute 95% CIs
    sim_summary = {}
    for metric, values in sim_results.items():
        ci_low = float(np.percentile(values, 2.5))
        ci_high = float(np.percentile(values, 97.5))
        sim_summary[metric] = {
            'mean': float(np.mean(values)),
            'ci_low': ci_low,
            'ci_high': ci_high,
            'std': float(np.std(values)),
        }

    simulated_stats[sec] = sim_summary

    print(f"    Alternation: sim mean={sim_summary['alternation_rate']['mean']:.4f}  "
          f"95% CI=[{sim_summary['alternation_rate']['ci_low']:.4f}, {sim_summary['alternation_rate']['ci_high']:.4f}]")
    print(f"    QO fraction: sim mean={sim_summary['qo_fraction']['mean']:.4f}  "
          f"95% CI=[{sim_summary['qo_fraction']['ci_low']:.4f}, {sim_summary['qo_fraction']['ci_high']:.4f}]")
    print(f"    Trans entropy: sim mean={sim_summary['transition_entropy']['mean']:.4f}  "
          f"95% CI=[{sim_summary['transition_entropy']['ci_low']:.4f}, {sim_summary['transition_entropy']['ci_high']:.4f}]")
    print(f"    QO run mean: sim mean={sim_summary['qo_run_mean']['mean']:.3f}  "
          f"95% CI=[{sim_summary['qo_run_mean']['ci_low']:.3f}, {sim_summary['qo_run_mean']['ci_high']:.3f}]")
    print(f"    CHSH run mean: sim mean={sim_summary['chsh_run_mean']['mean']:.3f}  "
          f"95% CI=[{sim_summary['chsh_run_mean']['ci_low']:.3f}, {sim_summary['chsh_run_mean']['ci_high']:.3f}]")


# ============================================================
# SECTION 5: Compare Observed vs Simulated
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Compare Observed vs Simulated")
print("=" * 60)


def in_ci(value, ci_low, ci_high):
    """Check if observed value falls within simulated 95% CI."""
    return ci_low <= value <= ci_high


section_results = {}
overall_passes = []
overall_fails = []

for sec in sorted(observed_stats.keys()):
    if sec not in simulated_stats:
        continue

    obs = observed_stats[sec]
    sim = simulated_stats[sec]
    name = section_names.get(sec, sec)

    print(f"\n  Section {sec} ({name}):")

    checks = {}

    # 1. Alternation rate
    obs_alt = obs['alternation_rate']
    alt_in_ci = in_ci(obs_alt, sim['alternation_rate']['ci_low'], sim['alternation_rate']['ci_high'])
    alt_delta = abs(obs_alt - sim['alternation_rate']['mean'])
    alt_within_002 = alt_delta <= 0.02
    checks['alternation_rate'] = {
        'observed': float(obs_alt),
        'sim_mean': float(sim['alternation_rate']['mean']),
        'sim_ci': [float(sim['alternation_rate']['ci_low']), float(sim['alternation_rate']['ci_high'])],
        'delta': float(alt_delta),
        'in_95ci': bool(alt_in_ci),
        'within_002': bool(alt_within_002),
        'pass': bool(alt_in_ci),
    }
    status = "PASS" if alt_in_ci else "FAIL"
    print(f"    Alternation: obs={obs_alt:.4f}, sim={sim['alternation_rate']['mean']:.4f}, "
          f"delta={alt_delta:.4f}, in CI={alt_in_ci} [{status}]")

    # 2. QO fraction (stationary distribution)
    obs_qo = obs['qo_fraction']
    qo_in_ci = in_ci(obs_qo, sim['qo_fraction']['ci_low'], sim['qo_fraction']['ci_high'])
    qo_delta = abs(obs_qo - sim['qo_fraction']['mean'])
    checks['qo_fraction'] = {
        'observed': float(obs_qo),
        'sim_mean': float(sim['qo_fraction']['mean']),
        'sim_ci': [float(sim['qo_fraction']['ci_low']), float(sim['qo_fraction']['ci_high'])],
        'delta': float(qo_delta),
        'in_95ci': bool(qo_in_ci),
        'pass': bool(qo_in_ci),
    }
    status = "PASS" if qo_in_ci else "FAIL"
    print(f"    QO fraction: obs={obs_qo:.4f}, sim={sim['qo_fraction']['mean']:.4f}, "
          f"delta={qo_delta:.4f}, in CI={qo_in_ci} [{status}]")

    # 3. Transition entropy
    obs_ent = obs['transition_entropy']
    ent_in_ci = in_ci(obs_ent, sim['transition_entropy']['ci_low'], sim['transition_entropy']['ci_high'])
    ent_delta = abs(obs_ent - sim['transition_entropy']['mean'])
    ent_within_01 = ent_delta <= 0.1
    checks['transition_entropy'] = {
        'observed': float(obs_ent),
        'sim_mean': float(sim['transition_entropy']['mean']),
        'sim_ci': [float(sim['transition_entropy']['ci_low']), float(sim['transition_entropy']['ci_high'])],
        'delta_bits': float(ent_delta),
        'in_95ci': bool(ent_in_ci),
        'within_01_bits': bool(ent_within_01),
        'pass': bool(ent_in_ci),
    }
    status = "PASS" if ent_in_ci else "FAIL"
    print(f"    Trans entropy: obs={obs_ent:.4f}, sim={sim['transition_entropy']['mean']:.4f}, "
          f"delta={ent_delta:.4f} bits, in CI={ent_in_ci} [{status}]")

    # 4. QO run-length mean
    obs_qo_rm = obs['qo_run_lengths']['mean']
    qo_rm_in_ci = in_ci(obs_qo_rm, sim['qo_run_mean']['ci_low'], sim['qo_run_mean']['ci_high'])
    qo_rm_delta = abs(obs_qo_rm - sim['qo_run_mean']['mean'])
    checks['qo_run_mean'] = {
        'observed': float(obs_qo_rm),
        'sim_mean': float(sim['qo_run_mean']['mean']),
        'sim_ci': [float(sim['qo_run_mean']['ci_low']), float(sim['qo_run_mean']['ci_high'])],
        'delta': float(qo_rm_delta),
        'in_95ci': bool(qo_rm_in_ci),
        'pass': bool(qo_rm_in_ci),
    }
    status = "PASS" if qo_rm_in_ci else "FAIL"
    print(f"    QO run mean: obs={obs_qo_rm:.3f}, sim={sim['qo_run_mean']['mean']:.3f}, "
          f"delta={qo_rm_delta:.3f}, in CI={qo_rm_in_ci} [{status}]")

    # 5. CHSH run-length mean
    obs_chsh_rm = obs['chsh_run_lengths']['mean']
    chsh_rm_in_ci = in_ci(obs_chsh_rm, sim['chsh_run_mean']['ci_low'], sim['chsh_run_mean']['ci_high'])
    chsh_rm_delta = abs(obs_chsh_rm - sim['chsh_run_mean']['mean'])
    checks['chsh_run_mean'] = {
        'observed': float(obs_chsh_rm),
        'sim_mean': float(sim['chsh_run_mean']['mean']),
        'sim_ci': [float(sim['chsh_run_mean']['ci_low']), float(sim['chsh_run_mean']['ci_high'])],
        'delta': float(chsh_rm_delta),
        'in_95ci': bool(chsh_rm_in_ci),
        'pass': bool(chsh_rm_in_ci),
    }
    status = "PASS" if chsh_rm_in_ci else "FAIL"
    print(f"    CHSH run mean: obs={obs_chsh_rm:.3f}, sim={sim['chsh_run_mean']['mean']:.3f}, "
          f"delta={chsh_rm_delta:.3f}, in CI={chsh_rm_in_ci} [{status}]")

    # Section-level verdict
    n_pass = sum(1 for c in checks.values() if c['pass'])
    n_total = len(checks)
    sec_pass = n_pass == n_total
    overall_passes.append(n_pass)
    overall_fails.append(n_total - n_pass)

    section_results[sec] = {
        'name': name,
        'n_transitions': obs['n_transitions'],
        'observed': {
            'alternation_rate': float(obs['alternation_rate']),
            'qo_fraction': float(obs['qo_fraction']),
            'transition_entropy': float(obs['transition_entropy']),
            'qo_run_lengths': obs['qo_run_lengths'],
            'chsh_run_lengths': obs['chsh_run_lengths'],
        },
        'simulated': {
            'alternation_rate': sim['alternation_rate'],
            'qo_fraction': sim['qo_fraction'],
            'transition_entropy': sim['transition_entropy'],
            'qo_run_mean': sim['qo_run_mean'],
            'chsh_run_mean': sim['chsh_run_mean'],
        },
        'checks': checks,
        'metrics_passed': int(n_pass),
        'metrics_total': int(n_total),
        'section_pass': bool(sec_pass),
    }

    sec_verdict = "PASS" if sec_pass else f"PARTIAL ({n_pass}/{n_total})"
    print(f"    Section verdict: {sec_verdict}")


# ============================================================
# SECTION 6: C650 Target Comparison
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: C650 Target Comparison")
print("=" * 60)

c650_checks = {}

# BIO alternation ~ 0.593-0.608
if 'B' in observed_stats:
    bio_alt = observed_stats['B']['alternation_rate']
    bio_in_range = 0.593 <= bio_alt <= 0.608
    c650_checks['bio_alternation'] = {
        'observed': float(bio_alt),
        'target_range': [0.593, 0.608],
        'in_range': bool(bio_in_range),
    }
    status = "PASS" if bio_in_range else "FAIL"
    print(f"  BIO alternation: {bio_alt:.4f} (target 0.593-0.608) [{status}]")

# HERBAL alternation ~ 0.427-0.464
if 'H' in observed_stats:
    herb_alt = observed_stats['H']['alternation_rate']
    herb_in_range = 0.427 <= herb_alt <= 0.464
    c650_checks['herbal_alternation'] = {
        'observed': float(herb_alt),
        'target_range': [0.427, 0.464],
        'in_range': bool(herb_in_range),
    }
    status = "PASS" if herb_in_range else "FAIL"
    print(f"  HERBAL alternation: {herb_alt:.4f} (target 0.427-0.464) [{status}]")

# Predicted within 0.02 of observed for all sections
within_002_all = True
for sec, res in section_results.items():
    delta = res['checks']['alternation_rate']['delta']
    if delta > 0.02:
        within_002_all = False
        print(f"  Section {sec}: alternation delta {delta:.4f} > 0.02")
if within_002_all:
    print(f"  All sections alternation predicted within 0.02: PASS")
else:
    print(f"  All sections alternation predicted within 0.02: FAIL")
c650_checks['all_within_002'] = bool(within_002_all)

# Transition entropy within 0.1 bits for all sections
entropy_ok_all = True
for sec, res in section_results.items():
    delta = res['checks']['transition_entropy']['delta_bits']
    if delta > 0.1:
        entropy_ok_all = False
        print(f"  Section {sec}: entropy delta {delta:.4f} > 0.1 bits")
if entropy_ok_all:
    print(f"  All sections entropy within 0.1 bits: PASS")
else:
    print(f"  All sections entropy within 0.1 bits: FAIL")
c650_checks['all_entropy_within_01'] = bool(entropy_ok_all)


# ============================================================
# SECTION 7: Overall Verdict & Save
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Overall Verdict")
print("=" * 60)

total_metric_passes = sum(overall_passes)
total_metric_checks = sum(overall_passes) + sum(overall_fails)
all_sections_pass = all(r['section_pass'] for r in section_results.values())

# Verdict logic:
# PASS = all metrics in all sections within 95% CI
# PARTIAL = majority of metrics pass but not all
# FAIL = majority of metrics fail
if all_sections_pass:
    verdict = 'PASS'
elif total_metric_passes / total_metric_checks >= 0.5:
    verdict = 'PARTIAL'
else:
    verdict = 'FAIL'

print(f"  Sections tested: {len(section_results)}")
print(f"  Total metric checks: {total_metric_checks}")
print(f"  Total metric passes: {total_metric_passes}")
print(f"  Pass rate: {total_metric_passes / total_metric_checks:.1%}" if total_metric_checks > 0 else "  No checks")
for sec, res in sorted(section_results.items()):
    sec_status = "PASS" if res['section_pass'] else f"PARTIAL ({res['metrics_passed']}/{res['metrics_total']})"
    print(f"    {sec} ({res['name']}): {sec_status}")

print(f"\n  T4 VERDICT: {verdict}")

# Build results
results = {
    'test': 'T4_section_parameterization',
    'description': 'Test whether section-specific Markov matrices fully account for observed oscillation dynamics',
    'n_simulations': N_SIMS,
    'min_transitions_threshold': MIN_TRANSITIONS,
    'seed': 42,
    'sections_tested': sorted(list(section_results.keys())),
    'sections_skipped': sorted([s for s in section_lines.keys() if s not in observed_stats]),
    'section_results': section_results,
    'c650_comparison': c650_checks,
    'summary': {
        'total_sections': int(len(section_results)),
        'total_metric_checks': int(total_metric_checks),
        'total_metric_passes': int(total_metric_passes),
        'pass_rate': float(total_metric_passes / total_metric_checks) if total_metric_checks > 0 else 0.0,
        'all_sections_pass': bool(all_sections_pass),
    },
    'verdict': verdict,
}

out_path = RESULTS_DIR / 't4_section_parameters.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")

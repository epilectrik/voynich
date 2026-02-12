#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T1: Baseline Transition Matrix Estimation

Estimates section-stratified first-order Markov transition matrices for EN lane
sequences (QO/CHSH), excluding hazard-adjacent and CC-adjacent positions.

Method:
  - State-conditional likelihood with ridge smoothing (Dirichlet prior alpha=1)
  - Bootstrap CIs (1000 resamples at line level)
  - Compare filtered vs unfiltered matrices to validate isolation assumption

Target values (C643):
  - QO->CHSH ~ 0.60
  - CHSH->QO ~ 0.53
  - Overall alternation ~ 0.563

Falsification:
  - Removing hazard/CC-adjacent positions shifts any matrix cell by > 0.05
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("T1: Baseline Transition Matrix Estimation")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction

# Load EN census
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

# Build line-organized B token data with full annotations
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

print(f"B lines: {len(lines)}")

# ============================================================
# SECTION 2: Build EN Sequences with Context Annotations
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Build EN Sequences")
print("=" * 60)

MIN_EN = 2  # Need at least 2 EN tokens for a transition

en_line_data = []
for (folio, line_num), toks in lines.items():
    # Find EN positions and annotate context
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is None:
            continue

        # Check if within 2 positions of hazard or CC
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

n_lines = len(en_line_data)
n_en = sum(len(d['en_seq']) for d in en_line_data)
n_pairs = sum(len(d['en_seq']) - 1 for d in en_line_data)
print(f"Lines with >= {MIN_EN} EN tokens: {n_lines}")
print(f"Total EN tokens in sequences: {n_en}")
print(f"Total EN-to-EN transitions: {n_pairs}")


# ============================================================
# SECTION 3: Estimate Transition Matrices
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Estimate Transition Matrices")
print("=" * 60)


def estimate_matrix(transitions, alpha=1.0):
    """Estimate 2x2 transition matrix with Dirichlet smoothing.

    transitions: list of (from_lane, to_lane) tuples
    alpha: Dirichlet prior (ridge smoothing)

    Returns: dict with transition probabilities and counts
    """
    counts = {'QO': {'QO': 0, 'CHSH': 0}, 'CHSH': {'QO': 0, 'CHSH': 0}}
    for fr, to in transitions:
        if fr in counts and to in counts[fr]:
            counts[fr][to] += 1

    result = {}
    for state in ['QO', 'CHSH']:
        total = sum(counts[state].values()) + 2 * alpha
        result[state] = {}
        for next_state in ['QO', 'CHSH']:
            result[state][next_state] = (counts[state][next_state] + alpha) / total

    n_total = sum(counts[s][t] for s in counts for t in counts[s])
    return {
        'matrix': result,
        'counts': counts,
        'n_transitions': n_total,
        'alternation_rate': (counts['QO']['CHSH'] + counts['CHSH']['QO']) / n_total if n_total > 0 else 0,
    }


def extract_transitions(line_data, filtered=True):
    """Extract lane transitions, optionally filtering hazard/CC-adjacent."""
    transitions = []
    for d in line_data:
        seq = d['en_positions']
        for i in range(len(seq) - 1):
            if filtered:
                if seq[i]['near_haz'] or seq[i]['near_cc']:
                    continue
                if seq[i + 1]['near_haz'] or seq[i + 1]['near_cc']:
                    continue
            transitions.append((seq[i]['lane'], seq[i + 1]['lane']))
    return transitions


# 3a. Unfiltered (all transitions)
all_trans = extract_transitions(en_line_data, filtered=False)
unfiltered = estimate_matrix(all_trans)

print("\nUNFILTERED transition matrix (all EN pairs):")
print(f"  n = {unfiltered['n_transitions']}")
print(f"  QO->QO:   {unfiltered['matrix']['QO']['QO']:.4f}  QO->CHSH:  {unfiltered['matrix']['QO']['CHSH']:.4f}")
print(f"  CHSH->QO: {unfiltered['matrix']['CHSH']['QO']:.4f}  CHSH->CHSH:{unfiltered['matrix']['CHSH']['CHSH']:.4f}")
print(f"  Alternation rate: {unfiltered['alternation_rate']:.4f}")

# 3b. Filtered (excluding hazard/CC-adjacent)
filt_trans = extract_transitions(en_line_data, filtered=True)
filtered = estimate_matrix(filt_trans)

print("\nFILTERED transition matrix (hazard/CC-adjacent removed):")
print(f"  n = {filtered['n_transitions']}")
print(f"  QO->QO:   {filtered['matrix']['QO']['QO']:.4f}  QO->CHSH:  {filtered['matrix']['QO']['CHSH']:.4f}")
print(f"  CHSH->QO: {filtered['matrix']['CHSH']['QO']:.4f}  CHSH->CHSH:{filtered['matrix']['CHSH']['CHSH']:.4f}")
print(f"  Alternation rate: {filtered['alternation_rate']:.4f}")

# 3c. Check isolation assumption: |filtered - unfiltered| < 0.05
print("\nIsolation check (|filtered - unfiltered| per cell):")
max_delta = 0
for s in ['QO', 'CHSH']:
    for t in ['QO', 'CHSH']:
        delta = abs(filtered['matrix'][s][t] - unfiltered['matrix'][s][t])
        max_delta = max(max_delta, delta)
        status = "OK" if delta < 0.05 else "FAIL"
        print(f"  {s}->{t}: delta = {delta:.4f} [{status}]")
isolation_pass = max_delta < 0.05
print(f"  Isolation assumption: {'PASS' if isolation_pass else 'FAIL'} (max delta = {max_delta:.4f})")


# ============================================================
# SECTION 4: Section-Stratified Matrices
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Section-Stratified Matrices")
print("=" * 60)

# Group lines by section
section_lines = defaultdict(list)
for d in en_line_data:
    section_lines[d['section']].append(d)

section_matrices = {}
section_names = {'B': 'BIO', 'H': 'HERBAL_B', 'S': 'STARS', 'C': 'COSMO', 'T': 'RECIPE'}

for sec in sorted(section_lines.keys()):
    sec_trans = extract_transitions(section_lines[sec], filtered=True)
    if len(sec_trans) < 10:
        print(f"\n  Section {sec} ({section_names.get(sec, sec)}): too few transitions ({len(sec_trans)}), skipping")
        continue

    mat = estimate_matrix(sec_trans)
    section_matrices[sec] = mat
    name = section_names.get(sec, sec)
    print(f"\n  Section {sec} ({name}): n={mat['n_transitions']}")
    print(f"    QO->CHSH:  {mat['matrix']['QO']['CHSH']:.4f}")
    print(f"    CHSH->QO:  {mat['matrix']['CHSH']['QO']:.4f}")
    print(f"    Alternation: {mat['alternation_rate']:.4f}")

    # Compute stationary distribution: pi_QO = p(CHSH->QO) / (p(QO->CHSH) + p(CHSH->QO))
    p_qc = mat['matrix']['QO']['CHSH']
    p_cq = mat['matrix']['CHSH']['QO']
    pi_qo = p_cq / (p_qc + p_cq)
    pi_chsh = 1 - pi_qo
    print(f"    Stationary: QO={pi_qo:.4f}, CHSH={pi_chsh:.4f}")


# ============================================================
# SECTION 5: Bootstrap Confidence Intervals
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Bootstrap Confidence Intervals")
print("=" * 60)

N_BOOTSTRAP = 1000
rng = np.random.default_rng(42)

# Bootstrap overall filtered matrix
print("\nOverall matrix bootstrap (1000 resamples, line-level):")

# Collect per-line transition lists for resampling
line_trans_lists = []
for d in en_line_data:
    seq = d['en_positions']
    line_t = []
    for i in range(len(seq) - 1):
        if seq[i]['near_haz'] or seq[i]['near_cc']:
            continue
        if seq[i + 1]['near_haz'] or seq[i + 1]['near_cc']:
            continue
        line_t.append((seq[i]['lane'], seq[i + 1]['lane']))
    if line_t:
        line_trans_lists.append(line_t)

n_boot_lines = len(line_trans_lists)
print(f"  Lines with filtered transitions: {n_boot_lines}")

boot_qc = []
boot_cq = []
boot_alt = []
for _ in range(N_BOOTSTRAP):
    idx = rng.choice(n_boot_lines, size=n_boot_lines, replace=True)
    boot_trans = []
    for i in idx:
        boot_trans.extend(line_trans_lists[i])
    bmat = estimate_matrix(boot_trans)
    boot_qc.append(bmat['matrix']['QO']['CHSH'])
    boot_cq.append(bmat['matrix']['CHSH']['QO'])
    boot_alt.append(bmat['alternation_rate'])

boot_qc = np.array(boot_qc)
boot_cq = np.array(boot_cq)
boot_alt = np.array(boot_alt)

ci_qc = (np.percentile(boot_qc, 2.5), np.percentile(boot_qc, 97.5))
ci_cq = (np.percentile(boot_cq, 2.5), np.percentile(boot_cq, 97.5))
ci_alt = (np.percentile(boot_alt, 2.5), np.percentile(boot_alt, 97.5))

print(f"  QO->CHSH:  {filtered['matrix']['QO']['CHSH']:.4f}  95% CI: [{ci_qc[0]:.4f}, {ci_qc[1]:.4f}]  width: {ci_qc[1]-ci_qc[0]:.4f}")
print(f"  CHSH->QO:  {filtered['matrix']['CHSH']['QO']:.4f}  95% CI: [{ci_cq[0]:.4f}, {ci_cq[1]:.4f}]  width: {ci_cq[1]-ci_cq[0]:.4f}")
print(f"  Alternation: {filtered['alternation_rate']:.4f}  95% CI: [{ci_alt[0]:.4f}, {ci_alt[1]:.4f}]  width: {ci_alt[1]-ci_alt[0]:.4f}")

ci_width_ok = (ci_qc[1] - ci_qc[0] < 0.05) and (ci_cq[1] - ci_cq[0] < 0.05)
print(f"  CI width < 0.05: {'PASS' if ci_width_ok else 'FAIL'}")

# Section-level bootstrap
print("\nSection-level bootstrap:")
section_boot_results = {}
for sec in sorted(section_matrices.keys()):
    sec_line_trans = []
    for d in section_lines[sec]:
        seq = d['en_positions']
        line_t = []
        for i in range(len(seq) - 1):
            if seq[i]['near_haz'] or seq[i]['near_cc']:
                continue
            if seq[i + 1]['near_haz'] or seq[i + 1]['near_cc']:
                continue
            line_t.append((seq[i]['lane'], seq[i + 1]['lane']))
        if line_t:
            sec_line_trans.append(line_t)

    if len(sec_line_trans) < 10:
        continue

    n_sec_lines = len(sec_line_trans)
    s_boot_qc = []
    s_boot_cq = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.choice(n_sec_lines, size=n_sec_lines, replace=True)
        bt = []
        for i in idx:
            bt.extend(sec_line_trans[i])
        bm = estimate_matrix(bt)
        s_boot_qc.append(bm['matrix']['QO']['CHSH'])
        s_boot_cq.append(bm['matrix']['CHSH']['QO'])

    s_boot_qc = np.array(s_boot_qc)
    s_boot_cq = np.array(s_boot_cq)
    sec_ci_qc = (float(np.percentile(s_boot_qc, 2.5)), float(np.percentile(s_boot_qc, 97.5)))
    sec_ci_cq = (float(np.percentile(s_boot_cq, 2.5)), float(np.percentile(s_boot_cq, 97.5)))
    name = section_names.get(sec, sec)

    section_boot_results[sec] = {
        'name': name,
        'QO_CHSH_ci': sec_ci_qc,
        'CHSH_QO_ci': sec_ci_cq,
    }
    print(f"  {sec} ({name}): QO->CHSH CI [{sec_ci_qc[0]:.4f}, {sec_ci_qc[1]:.4f}]  CHSH->QO CI [{sec_ci_cq[0]:.4f}, {sec_ci_cq[1]:.4f}]")


# ============================================================
# SECTION 6: Save Results
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Results Summary")
print("=" * 60)

results = {
    'test': 'T1_baseline_transition_matrix',
    'description': 'Section-stratified first-order Markov transition matrices for EN lane sequences',
    'n_lines': n_lines,
    'n_en_tokens': n_en,
    'n_transitions_unfiltered': unfiltered['n_transitions'],
    'n_transitions_filtered': filtered['n_transitions'],
    'unfiltered_matrix': {
        'QO_to_QO': unfiltered['matrix']['QO']['QO'],
        'QO_to_CHSH': unfiltered['matrix']['QO']['CHSH'],
        'CHSH_to_QO': unfiltered['matrix']['CHSH']['QO'],
        'CHSH_to_CHSH': unfiltered['matrix']['CHSH']['CHSH'],
        'alternation_rate': unfiltered['alternation_rate'],
    },
    'filtered_matrix': {
        'QO_to_QO': filtered['matrix']['QO']['QO'],
        'QO_to_CHSH': filtered['matrix']['QO']['CHSH'],
        'CHSH_to_QO': filtered['matrix']['CHSH']['QO'],
        'CHSH_to_CHSH': filtered['matrix']['CHSH']['CHSH'],
        'alternation_rate': filtered['alternation_rate'],
    },
    'isolation_check': {
        'max_delta': float(max_delta),
        'pass': bool(isolation_pass),
        'threshold': 0.05,
    },
    'bootstrap': {
        'n_resamples': N_BOOTSTRAP,
        'resample_unit': 'line',
        'QO_to_CHSH_ci': [float(ci_qc[0]), float(ci_qc[1])],
        'CHSH_to_QO_ci': [float(ci_cq[0]), float(ci_cq[1])],
        'alternation_ci': [float(ci_alt[0]), float(ci_alt[1])],
        'ci_width_ok': bool(ci_width_ok),
    },
    'section_matrices': {},
}

for sec, mat in section_matrices.items():
    name = section_names.get(sec, sec)
    p_qc = mat['matrix']['QO']['CHSH']
    p_cq = mat['matrix']['CHSH']['QO']
    pi_qo = p_cq / (p_qc + p_cq)

    sec_result = {
        'name': name,
        'n_transitions': mat['n_transitions'],
        'QO_to_CHSH': p_qc,
        'CHSH_to_QO': p_cq,
        'alternation_rate': mat['alternation_rate'],
        'stationary_QO': pi_qo,
        'stationary_CHSH': 1 - pi_qo,
    }
    if sec in section_boot_results:
        sec_result['bootstrap'] = section_boot_results[sec]
    results['section_matrices'][sec] = sec_result

# C643 target comparison
target_qc = 0.60
target_cq = 0.53
actual_qc = filtered['matrix']['QO']['CHSH']
actual_cq = filtered['matrix']['CHSH']['QO']
results['c643_comparison'] = {
    'target_QO_CHSH': target_qc,
    'actual_QO_CHSH': actual_qc,
    'delta_QO_CHSH': abs(actual_qc - target_qc),
    'target_CHSH_QO': target_cq,
    'actual_CHSH_QO': actual_cq,
    'delta_CHSH_QO': abs(actual_cq - target_cq),
}

print(f"\nC643 target comparison:")
print(f"  QO->CHSH: target={target_qc:.3f}, actual={actual_qc:.4f}, delta={abs(actual_qc - target_qc):.4f}")
print(f"  CHSH->QO: target={target_cq:.3f}, actual={actual_cq:.4f}, delta={abs(actual_cq - target_cq):.4f}")

# Verdict
all_checks = [isolation_pass, ci_width_ok]
verdict = 'PASS' if all(all_checks) else 'PARTIAL' if any(all_checks) else 'FAIL'
results['verdict'] = verdict
print(f"\nT1 VERDICT: {verdict}")

out_path = RESULTS_DIR / 't1_transition_matrices.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved: {out_path}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T2: Hazard Gate Estimation

Characterizes the exact perturbation to lane transition probabilities caused by
hazard tokens (classes 7 and 30).

Method:
  - For each hazard token, find subsequent EN tokens in the same line
  - Record EN lane (QO/CHSH) at offsets +1..+5 (offset = EN tokens away from hazard)
  - Compare lane distributions at each offset to T1 baseline
  - Compute KL divergence, Cramer's V, chi-squared test (Bonferroni corrected)
  - Determine gate duration: offset at which distribution returns to baseline
  - Test class 7 vs 30 for differential gate effects

Targets (from C645):
  - Offset +1 should show ~75% CHSH
  - Gate should decay to baseline by offset +2 or +3
  - No significant difference between class 7 and 30 (matching C651)
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

MAX_OFFSET = 5  # EN tokens +1 through +5

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("T2: Hazard Gate Estimation")
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

# Load T1 baseline results
t1_path = RESULTS_DIR / 't1_transition_matrices.json'
with open(t1_path) as f:
    t1_results = json.load(f)

# Baseline lane distribution from T1 unfiltered matrix stationary distribution
# Use unfiltered matrix for overall EN lane baseline
t1_unfiltered = t1_results['unfiltered_matrix']
# Compute stationary distribution from unfiltered matrix
p_qc = t1_unfiltered['QO_to_CHSH']
p_cq = t1_unfiltered['CHSH_to_QO']
baseline_chsh_frac = 1 - p_cq / (p_qc + p_cq)  # stationary CHSH fraction
baseline_qo_frac = 1 - baseline_chsh_frac

print(f"T1 baseline stationary: QO={baseline_qo_frac:.4f}, CHSH={baseline_chsh_frac:.4f}")

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
# SECTION 2: Collect Post-Hazard EN Observations
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Collect Post-Hazard EN Observations")
print("=" * 60)

# For each hazard token, find subsequent EN tokens in the same line
# Offset = how many EN tokens away from hazard (1st EN after = offset 1, etc.)

# Structure: per_offset[offset] = list of lane labels ('QO' or 'CHSH')
per_offset_all = {off: [] for off in range(1, MAX_OFFSET + 1)}
per_offset_c7 = {off: [] for off in range(1, MAX_OFFSET + 1)}
per_offset_c30 = {off: [] for off in range(1, MAX_OFFSET + 1)}

n_hazard_events = 0
n_hazard_with_en = 0

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if not t['is_haz']:
            continue
        n_hazard_events += 1
        haz_class = t['class']

        # Find subsequent EN tokens in same line
        en_count = 0
        for j in range(i + 1, len(toks)):
            if toks[j]['en_subfamily'] is not None:
                en_count += 1
                if en_count <= MAX_OFFSET:
                    lane = toks[j]['en_subfamily']
                    per_offset_all[en_count].append(lane)
                    if haz_class == 7:
                        per_offset_c7[en_count].append(lane)
                    elif haz_class == 30:
                        per_offset_c30[en_count].append(lane)
                else:
                    break  # No need to look further

        if en_count > 0:
            n_hazard_with_en += 1

print(f"Total hazard events: {n_hazard_events}")
print(f"Hazard events with >= 1 subsequent EN: {n_hazard_with_en}")
print(f"\nPer-offset sample sizes (all):")
for off in range(1, MAX_OFFSET + 1):
    n = len(per_offset_all[off])
    n7 = len(per_offset_c7[off])
    n30 = len(per_offset_c30[off])
    print(f"  Offset +{off}: n={n} (class 7: {n7}, class 30: {n30})")


# ============================================================
# SECTION 3: Compute Per-Offset Statistics
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Per-Offset Statistics vs Baseline")
print("=" * 60)

# Baseline distribution as array: [QO_frac, CHSH_frac]
baseline_dist = np.array([baseline_qo_frac, baseline_chsh_frac])

BONFERRONI_ALPHA = 0.05 / MAX_OFFSET  # Corrected for 5 tests


def kl_divergence(p, q, epsilon=1e-10):
    """KL divergence D(p || q) with epsilon smoothing."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = np.clip(p, epsilon, 1.0)
    q = np.clip(q, epsilon, 1.0)
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))


def cramers_v(observed, expected_dist, n):
    """Cramer's V for 1x2 table (2 categories).

    observed: array [n_QO, n_CHSH]
    expected_dist: array [p_QO, p_CHSH]
    n: total observations
    """
    expected = expected_dist * n
    if np.any(expected == 0):
        return 0.0
    chi2 = np.sum((observed - expected) ** 2 / expected)
    # For a 1x2 table, df = 1, k = 2 categories
    # Cramer's V = sqrt(chi2 / (n * (min(r,c)-1))) = sqrt(chi2 / n) for 1x2
    return float(np.sqrt(chi2 / n)) if n > 0 else 0.0


offset_results = {}

for off in range(1, MAX_OFFSET + 1):
    lanes = per_offset_all[off]
    n = len(lanes)

    if n < 5:
        print(f"\n  Offset +{off}: n={n} -- TOO FEW, skipping")
        offset_results[str(off)] = {
            'n': n,
            'skip': True,
            'reason': 'insufficient data',
        }
        continue

    n_qo = sum(1 for l in lanes if l == 'QO')
    n_chsh = sum(1 for l in lanes if l == 'CHSH')
    chsh_frac = n_chsh / n
    qo_frac = n_qo / n
    observed_dist = np.array([qo_frac, chsh_frac])
    observed_counts = np.array([n_qo, n_chsh])

    # KL divergence: D(observed || baseline)
    kl = kl_divergence(observed_dist, baseline_dist)

    # Cramer's V
    cv = cramers_v(observed_counts, baseline_dist, n)

    # Chi-squared goodness of fit test vs baseline
    expected_counts = baseline_dist * n
    chi2_stat, chi2_p = stats.chisquare(observed_counts, f_exp=expected_counts)

    # Is this offset significantly different from baseline? (Bonferroni corrected)
    sig = bool(chi2_p < BONFERRONI_ALPHA)

    print(f"\n  Offset +{off}: n={n}")
    print(f"    CHSH frac: {chsh_frac:.4f} (baseline: {baseline_chsh_frac:.4f})")
    print(f"    KL divergence: {kl:.6f}")
    print(f"    Cramer's V: {cv:.4f}")
    print(f"    Chi2={chi2_stat:.3f}, p={chi2_p:.6f} {'*' if sig else ''} (Bonferroni alpha={BONFERRONI_ALPHA:.4f})")

    offset_results[str(off)] = {
        'n': n,
        'n_QO': n_qo,
        'n_CHSH': n_chsh,
        'CHSH_fraction': float(chsh_frac),
        'QO_fraction': float(qo_frac),
        'KL_divergence': float(kl),
        'cramers_V': float(cv),
        'chi2_statistic': float(chi2_stat),
        'chi2_p_value': float(chi2_p),
        'bonferroni_alpha': float(BONFERRONI_ALPHA),
        'significant': sig,
    }


# ============================================================
# SECTION 4: Gate Duration Estimation
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Gate Duration Estimation")
print("=" * 60)

# Gate duration = first offset where KL < 0.01 OR chi2 p > bonferroni alpha
gate_duration = None
for off in range(1, MAX_OFFSET + 1):
    r = offset_results.get(str(off), {})
    if r.get('skip'):
        continue
    kl = r.get('KL_divergence', 999)
    p = r.get('chi2_p_value', 0)
    if kl < 0.01 or p > BONFERRONI_ALPHA:
        gate_duration = off
        break

if gate_duration is None:
    gate_duration_note = 'Gate persists beyond offset +5'
    print(f"Gate duration: NOT RESOLVED (persists beyond +{MAX_OFFSET})")
else:
    gate_duration_note = f'Returns to baseline at offset +{gate_duration}'
    print(f"Gate duration: {gate_duration_note}")
    print(f"  (KL={offset_results[str(gate_duration)].get('KL_divergence', 'N/A'):.6f}, "
          f"p={offset_results[str(gate_duration)].get('chi2_p_value', 'N/A'):.6f})")


# ============================================================
# SECTION 5: Gate Transition Matrix at Offset +1
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Gate Transition Matrix (Offset +1)")
print("=" * 60)

# P(lane | post_hazard) at offset +1
lanes_off1 = per_offset_all.get(1, [])
n_off1 = len(lanes_off1)
if n_off1 > 0:
    n_qo_off1 = sum(1 for l in lanes_off1 if l == 'QO')
    n_chsh_off1 = sum(1 for l in lanes_off1 if l == 'CHSH')
    gate_matrix = {
        'P_QO_given_post_hazard': float(n_qo_off1 / n_off1),
        'P_CHSH_given_post_hazard': float(n_chsh_off1 / n_off1),
        'n': n_off1,
    }
    print(f"  P(QO | post_hazard) = {gate_matrix['P_QO_given_post_hazard']:.4f}")
    print(f"  P(CHSH | post_hazard) = {gate_matrix['P_CHSH_given_post_hazard']:.4f}")
    print(f"  n = {n_off1}")
else:
    gate_matrix = {'note': 'no data at offset +1'}
    print("  No data at offset +1")


# ============================================================
# SECTION 6: Class 7 vs Class 30 Comparison
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Class 7 vs Class 30 Comparison")
print("=" * 60)

class_comparison = {}

for off in range(1, MAX_OFFSET + 1):
    c7_lanes = per_offset_c7[off]
    c30_lanes = per_offset_c30[off]

    n7 = len(c7_lanes)
    n30 = len(c30_lanes)

    if n7 < 5 or n30 < 5:
        class_comparison[str(off)] = {
            'n_class7': n7,
            'n_class30': n30,
            'skip': True,
            'reason': f'insufficient data (n7={n7}, n30={n30})',
        }
        print(f"  Offset +{off}: n7={n7}, n30={n30} -- TOO FEW, skipping")
        continue

    n7_chsh = sum(1 for l in c7_lanes if l == 'CHSH')
    n7_qo = n7 - n7_chsh
    n30_chsh = sum(1 for l in c30_lanes if l == 'CHSH')
    n30_qo = n30 - n30_chsh

    chsh7 = n7_chsh / n7
    chsh30 = n30_chsh / n30

    # 2x2 contingency table: rows=class(7,30), cols=lane(QO,CHSH)
    contingency = np.array([[n7_qo, n7_chsh], [n30_qo, n30_chsh]])

    # Use Fisher's exact test if any expected cell < 5, else chi-squared
    expected_min = min(
        (n7_qo + n30_qo) * n7 / (n7 + n30),
        (n7_chsh + n30_chsh) * n7 / (n7 + n30),
        (n7_qo + n30_qo) * n30 / (n7 + n30),
        (n7_chsh + n30_chsh) * n30 / (n7 + n30),
    )

    if expected_min < 5:
        _, p_val = stats.fisher_exact(contingency)
        test_used = 'fisher_exact'
    else:
        chi2_res = stats.chi2_contingency(contingency, correction=True)
        p_val = chi2_res[1]
        test_used = 'chi2_yates'

    sig = bool(p_val < 0.05)

    class_comparison[str(off)] = {
        'n_class7': n7,
        'n_class30': n30,
        'CHSH_frac_class7': float(chsh7),
        'CHSH_frac_class30': float(chsh30),
        'delta_CHSH': float(abs(chsh7 - chsh30)),
        'test': test_used,
        'p_value': float(p_val),
        'significant': sig,
    }

    print(f"  Offset +{off}: class7 CHSH={chsh7:.3f} (n={n7}), class30 CHSH={chsh30:.3f} (n={n30}), "
          f"delta={abs(chsh7 - chsh30):.3f}, p={p_val:.4f} [{test_used}] {'*' if sig else ''}")

# Overall class comparison: pool offsets 1-3 for maximum power
c7_pool = []
c30_pool = []
for off in range(1, min(4, MAX_OFFSET + 1)):
    c7_pool.extend(per_offset_c7[off])
    c30_pool.extend(per_offset_c30[off])

n7_pool = len(c7_pool)
n30_pool = len(c30_pool)

if n7_pool >= 10 and n30_pool >= 10:
    n7p_chsh = sum(1 for l in c7_pool if l == 'CHSH')
    n7p_qo = n7_pool - n7p_chsh
    n30p_chsh = sum(1 for l in c30_pool if l == 'CHSH')
    n30p_qo = n30_pool - n30p_chsh

    pool_table = np.array([[n7p_qo, n7p_chsh], [n30p_qo, n30p_chsh]])
    chi2_pool = stats.chi2_contingency(pool_table, correction=True)
    pool_p = chi2_pool[1]

    class_comparison_pooled = {
        'offsets_pooled': '1-3',
        'n_class7': n7_pool,
        'n_class30': n30_pool,
        'CHSH_frac_class7': float(n7p_chsh / n7_pool),
        'CHSH_frac_class30': float(n30p_chsh / n30_pool),
        'chi2_statistic': float(chi2_pool[0]),
        'p_value': float(pool_p),
        'significant': bool(pool_p < 0.05),
        'c651_match': bool(pool_p >= 0.05),  # C651: no difference
    }
    print(f"\n  Pooled (offsets 1-3): class7 CHSH={n7p_chsh/n7_pool:.3f}, "
          f"class30 CHSH={n30p_chsh/n30_pool:.3f}, p={pool_p:.4f}")
    print(f"  C651 match (no difference): {class_comparison_pooled['c651_match']}")
else:
    class_comparison_pooled = {
        'offsets_pooled': '1-3',
        'n_class7': n7_pool,
        'n_class30': n30_pool,
        'note': 'insufficient pooled data',
    }
    print(f"\n  Pooled: insufficient data (n7={n7_pool}, n30={n30_pool})")


# ============================================================
# SECTION 7: Verdict
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: Verdict")
print("=" * 60)

# Check C645 target: offset +1 CHSH ~75%
off1 = offset_results.get('1', {})
chsh_off1 = off1.get('CHSH_fraction', 0)
c645_chsh_match = chsh_off1 > 0.70  # Loose threshold: >70%
print(f"C645: Offset +1 CHSH = {chsh_off1:.4f} (target ~75%, pass threshold >70%): "
      f"{'PASS' if c645_chsh_match else 'FAIL'}")

# Gate decay check: should return to baseline by offset +2 or +3
gate_decay_ok = gate_duration is not None and gate_duration <= 3
print(f"Gate decay: duration = {gate_duration} "
      f"(target <= 3): {'PASS' if gate_decay_ok else 'FAIL'}")

# C651 check: no class 7 vs 30 difference
c651_ok = class_comparison_pooled.get('c651_match', False)
print(f"C651 (class 7 == class 30): {'PASS' if c651_ok else 'FAIL/INCONCLUSIVE'}")

# Overall
checks = [c645_chsh_match, gate_decay_ok, c651_ok]
if all(checks):
    verdict = 'PASS'
elif sum(checks) >= 2:
    verdict = 'PARTIAL'
else:
    verdict = 'FAIL'

print(f"\nT2 VERDICT: {verdict}")


# ============================================================
# SECTION 8: Save Results
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: Save Results")
print("=" * 60)

results = {
    'test': 'T2_hazard_gate_estimation',
    'description': 'Characterization of lane transition perturbation caused by hazard tokens',
    'n_hazard_events': n_hazard_events,
    'n_hazard_with_subsequent_en': n_hazard_with_en,
    'max_offset': MAX_OFFSET,
    'baseline': {
        'source': 't1_transition_matrices.json',
        'QO_fraction': float(baseline_qo_frac),
        'CHSH_fraction': float(baseline_chsh_frac),
    },
    'per_offset': offset_results,
    'gate_duration': {
        'offset': gate_duration,
        'note': gate_duration_note,
        'criterion': 'KL < 0.01 or chi2 p > bonferroni_alpha',
        'bonferroni_alpha': float(BONFERRONI_ALPHA),
    },
    'gate_transition_matrix': gate_matrix,
    'class_comparison_per_offset': class_comparison,
    'class_comparison_pooled': class_comparison_pooled,
    'targets': {
        'c645_offset1_chsh': {
            'target': 0.75,
            'actual': float(chsh_off1),
            'pass': bool(c645_chsh_match),
        },
        'gate_decay_by_offset3': {
            'estimated_duration': gate_duration,
            'pass': bool(gate_decay_ok),
        },
        'c651_no_class_difference': {
            'pooled_p': float(class_comparison_pooled.get('p_value', -1)),
            'pass': bool(c651_ok),
        },
    },
    'verdict': verdict,
}

out_path = RESULTS_DIR / 't2_hazard_gate.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results saved: {out_path}")

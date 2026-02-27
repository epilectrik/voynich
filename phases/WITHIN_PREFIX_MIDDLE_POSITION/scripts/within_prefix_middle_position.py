#!/usr/bin/env python3
"""
Phase 487: WITHIN-PREFIX MIDDLE POSITIONAL SELECTION
=====================================================
Investigates how specific MIDDLEs within each PREFIX change across line
positions. C1373 showed the thermal arc exists within PREFIXes — this
phase resolves the mechanism: which MIDDLEs drive the gradient, how
concentrated is the effect, and do ch/sh show parallel patterns.

Tests:
  T1: Within-PREFIX MIDDLE positional entropy (JSD Q1 vs Q5)
  T2: MIDDLE position specialist census (per PREFIX)
  T3: Concentration of category gradient explanation (within ch)
  T4: ch/sh parallel positional gradient
  T5: QO vs CHSH positional MIDDLE divergence
  T6: BARE positional MIDDLE selection (contrast control)
  T7: Position specialist vs compatibility constraint overlap

Depends on: C1373, C1371, C1305, C1012, C1001, C911, C576, C649
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, chi2_contingency, mannwhitneyu, fisher_exact
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)
N_QUINTILES = 5
MAJOR_PREFIXES = ['ch', 'sh', 'qo', 'ok', 'ot', 'da', '']  # '' = BARE


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def quintile_index(pos, line_len):
    if line_len <= 1:
        return 2
    frac = pos / (line_len - 1)
    q = int(frac * N_QUINTILES)
    return min(q, N_QUINTILES - 1)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with PREFIX, MIDDLE, category, quintile."""
    print("Loading data...")

    morph = Morphology()
    cc = CategoryClassifier()

    line_tokens = defaultdict(list)

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        if not cat:
            continue

        prefix = (m.prefix if m else '') or ''
        key = (token.folio, token.line)
        line_tokens[key].append((prefix, mid, cat))

    # Build records with quintile assignments
    records = []  # [(prefix, middle, cat_idx, quintile)]
    n_lines = 0

    for key, tokens in line_tokens.items():
        line_len = len(tokens)
        if line_len < 2:
            continue
        n_lines += 1
        for pos, (prefix, mid, cat) in enumerate(tokens):
            q = quintile_index(pos, line_len)
            ci = CAT_IDX[cat]
            records.append((prefix, mid, ci, q))

    n_tokens = len(records)
    print(f"  Lines: {n_lines}, Tokens: {n_tokens}")

    # Pre-compute: PREFIX -> {quintile -> Counter(MIDDLE)}
    prefix_q_mid = defaultdict(lambda: defaultdict(Counter))
    # PREFIX -> Counter(MIDDLE)
    prefix_mid_total = defaultdict(Counter)
    # PREFIX -> MIDDLE -> quintile counts
    prefix_mid_qcounts = defaultdict(lambda: defaultdict(lambda: np.zeros(N_QUINTILES, dtype=int)))
    # PREFIX -> MIDDLE -> category
    mid_to_cat = {}

    for prefix, mid, ci, q in records:
        prefix_q_mid[prefix][q][mid] += 1
        prefix_mid_total[prefix][mid] += 1
        prefix_mid_qcounts[prefix][mid][q] += 1
        mid_to_cat[mid] = ci  # last-write-wins (same mid always same cat per C1305)

    print(f"  Unique PREFIXes: {len(prefix_mid_total)}")
    print(f"  Unique MIDDLEs: {len(mid_to_cat)}")

    return {
        'records': records,
        'prefix_q_mid': dict(prefix_q_mid),
        'prefix_mid_total': dict(prefix_mid_total),
        'prefix_mid_qcounts': dict(prefix_mid_qcounts),
        'mid_to_cat': mid_to_cat,
        'n_lines': n_lines,
        'n_tokens': n_tokens,
    }


# ── T1: Within-PREFIX MIDDLE Positional Entropy ──────────────────────

def test1_positional_entropy(data):
    """T1: JSD between Q1 and Q5 MIDDLE distributions within each PREFIX."""
    print("\n=== T1: Within-PREFIX MIDDLE Positional Entropy ===")

    n_perm = 1000
    rng = np.random.default_rng(42)
    results = {}
    sig_count = 0

    for prefix in MAJOR_PREFIXES:
        label = prefix or 'BARE'
        q_mids = data['prefix_q_mid'].get(prefix, {})
        q1_counts = q_mids.get(0, Counter())
        q5_counts = q_mids.get(4, Counter())

        # Union of MIDDLEs
        all_mids = sorted(set(q1_counts.keys()) | set(q5_counts.keys()))
        if len(all_mids) < 3:
            print(f"  {label}: too few MIDDLEs ({len(all_mids)})")
            results[label] = {'n_middles': len(all_mids), 'verdict': 'INSUFFICIENT'}
            continue

        # Build vectors
        q1_vec = np.array([q1_counts.get(m, 0) for m in all_mids], dtype=float)
        q5_vec = np.array([q5_counts.get(m, 0) for m in all_mids], dtype=float)

        # JSD
        eps = 1e-10
        q1_norm = (q1_vec + eps) / (q1_vec + eps).sum()
        q5_norm = (q5_vec + eps) / (q5_vec + eps).sum()
        observed_jsd = float(jensenshannon(q1_norm, q5_norm) ** 2)

        # Permutation null: shuffle quintile labels within this PREFIX
        all_records = [(mid, q) for mid, q in
                       [(mid, q) for p, mid, ci, q in data['records'] if p == prefix]]
        perm_jsds = []
        for _ in range(n_perm):
            shuffled_q = rng.permutation([q for _, q in all_records])
            pq1 = Counter()
            pq5 = Counter()
            for i, (mid, _) in enumerate(all_records):
                sq = shuffled_q[i]
                if sq == 0:
                    pq1[mid] += 1
                elif sq == 4:
                    pq5[mid] += 1
            pv1 = np.array([pq1.get(m, 0) for m in all_mids], dtype=float)
            pv5 = np.array([pq5.get(m, 0) for m in all_mids], dtype=float)
            pv1 = (pv1 + eps) / (pv1 + eps).sum()
            pv5 = (pv5 + eps) / (pv5 + eps).sum()
            perm_jsds.append(jensenshannon(pv1, pv5) ** 2)

        p_perm = float(np.mean(np.array(perm_jsds) >= observed_jsd))
        sig = p_perm < 0.05
        if sig:
            sig_count += 1

        print(f"  {label:8s}: JSD(Q1,Q5)={observed_jsd:.6f}, perm_p={p_perm:.4f}, "
              f"n_mid={len(all_mids)}, q1_n={int(q1_vec.sum())}, q5_n={int(q5_vec.sum())} "
              f"{'*' if sig else ''}")

        results[label] = {
            'jsd_q1_q5': observed_jsd,
            'perm_p': p_perm,
            'significant': sig,
            'n_middles': len(all_mids),
            'q1_n': int(q1_vec.sum()),
            'q5_n': int(q5_vec.sum()),
        }

    passed = sig_count >= 4
    print(f"\n  Significant: {sig_count}/7. PASS (>=4): {passed}")
    results['sig_count'] = sig_count
    results['passed'] = passed
    return results


# ── T2: MIDDLE Position Specialist Census ────────────────────────────

def test2_specialist_census(data):
    """T2: How many MIDDLEs within each PREFIX are position-specialists?"""
    print("\n=== T2: MIDDLE Position Specialist Census ===")

    results = {}

    for prefix in MAJOR_PREFIXES:
        label = prefix or 'BARE'
        mid_qcounts = data['prefix_mid_qcounts'].get(prefix, {})
        mid_totals = data['prefix_mid_total'].get(prefix, Counter())

        n_testable = 0
        n_specialist = 0
        n_early = 0
        n_late = 0
        specialists = []

        for mid, total in mid_totals.items():
            if total < 10:
                continue
            n_testable += 1

            qc = mid_qcounts[mid]
            # Expected uniform
            expected = total / N_QUINTILES

            # Chi-squared
            chi2 = float(sum((qc[q] - expected) ** 2 / max(expected, 1e-10) for q in range(N_QUINTILES)))
            dof = N_QUINTILES - 1
            from scipy.stats import chi2 as chi2_dist
            p = float(1 - chi2_dist.cdf(chi2, dof))

            # Bonferroni correction
            if n_testable > 0:
                p_bonf = min(p * max(n_testable, 1), 1.0)
            else:
                p_bonf = p

            # Direction
            early_rate = (qc[0] + qc[1]) / max(total, 1)
            late_rate = (qc[3] + qc[4]) / max(total, 1)

            if p_bonf < 0.05:
                n_specialist += 1
                if early_rate > 2 * late_rate:
                    direction = 'EARLY'
                    n_early += 1
                elif late_rate > 2 * early_rate:
                    direction = 'LATE'
                    n_late += 1
                else:
                    direction = 'MIXED'
                cat = CATEGORIES[data['mid_to_cat'].get(mid, 0)]
                specialists.append((mid, direction, cat, total, float(chi2), float(p_bonf)))

        specialist_rate = n_specialist / max(n_testable, 1)
        print(f"  {label:8s}: {n_specialist}/{n_testable} specialists ({specialist_rate:.1%})"
              f" [{n_early} early, {n_late} late]")

        # Show top specialists
        specialists.sort(key=lambda x: -x[4])
        for mid, direction, cat, total, chi2, p in specialists[:5]:
            print(f"    {mid:12s} {direction:6s} {cat:12s} n={total:4d} chi2={chi2:6.1f} p={p:.4f}")

        results[label] = {
            'n_testable': n_testable,
            'n_specialist': n_specialist,
            'specialist_rate': specialist_rate,
            'n_early': n_early,
            'n_late': n_late,
            'top_specialists': [(m, d, c, n, chi, p) for m, d, c, n, chi, p in specialists[:10]],
        }

    # Pass criterion: ch has >= 20% specialists
    ch_rate = results.get('ch', {}).get('specialist_rate', 0)
    passed = ch_rate >= 0.20
    print(f"\n  ch specialist rate: {ch_rate:.1%}. PASS (>=20%): {passed}")
    results['passed'] = passed
    return results


# ── T3: Concentration of Category Gradient ───────────────────────────

def test3_gradient_concentration(data):
    """T3: How many MIDDLEs explain the within-ch THERMAL decline?"""
    print("\n=== T3: Gradient Concentration (within ch) ===")

    prefix = 'ch'
    mid_qcounts = data['prefix_mid_qcounts'].get(prefix, {})
    mid_totals = data['prefix_mid_total'].get(prefix, Counter())

    # Overall ch THERMAL fractions at Q1 and Q5
    q_totals = defaultdict(int)
    q_thermal = defaultdict(int)
    for mid, total in mid_totals.items():
        ci = data['mid_to_cat'].get(mid)
        if ci is None:
            continue
        for q in range(N_QUINTILES):
            count = mid_qcounts[mid][q]
            q_totals[q] += count
            if ci == CAT_IDX['THERMAL']:
                q_thermal[q] += count

    thermal_q1 = q_thermal[0] / max(q_totals[0], 1)
    thermal_q5 = q_thermal[4] / max(q_totals[4], 1)
    total_decline = thermal_q1 - thermal_q5
    print(f"  ch THERMAL: Q1={thermal_q1:.3f}, Q5={thermal_q5:.3f}, decline={total_decline:.4f}")

    # Per-MIDDLE contribution to THERMAL decline
    contributions = []
    for mid, total in mid_totals.items():
        ci = data['mid_to_cat'].get(mid)
        if ci is None:
            continue
        is_thermal = (ci == CAT_IDX['THERMAL'])

        q1_count = mid_qcounts[mid][0]
        q5_count = mid_qcounts[mid][4]
        q1_frac = q1_count / max(q_totals[0], 1)
        q5_frac = q5_count / max(q_totals[4], 1)

        if is_thermal:
            # THERMAL MIDDLE: contributes to decline if Q1 fraction > Q5 fraction
            contrib = q1_frac - q5_frac
        else:
            # Non-THERMAL MIDDLE: contributes to decline if Q5 fraction > Q1 fraction
            # (displacing THERMAL at Q5)
            contrib = -(q5_frac - q1_frac)

        contributions.append((mid, contrib, is_thermal, total, CATEGORIES[ci]))

    # Sort by contribution (positive = helps explain THERMAL decline)
    contributions.sort(key=lambda x: -x[1])

    # Cumulative explanation
    cumulative = 0.0
    n_50 = n_75 = n_90 = None

    print(f"\n  Top MIDDLE contributors to THERMAL decline:")
    print(f"  {'MIDDLE':12s} {'Contrib':>8s} {'Cumul':>8s} {'Cat':12s} {'N':>5s}")

    for i, (mid, contrib, is_thermal, total, cat) in enumerate(contributions[:15]):
        cumulative += contrib
        pct = cumulative / max(abs(total_decline), 1e-10)

        if n_50 is None and pct >= 0.50:
            n_50 = i + 1
        if n_75 is None and pct >= 0.75:
            n_75 = i + 1
        if n_90 is None and pct >= 0.90:
            n_90 = i + 1

        print(f"  {mid:12s} {contrib:+8.4f} {pct:8.1%} {cat:12s} {total:5d}")

    print(f"\n  MIDDLEs for 50% explanation: {n_50}")
    print(f"  MIDDLEs for 75% explanation: {n_75}")
    print(f"  MIDDLEs for 90% explanation: {n_90}")

    passed = n_50 is not None and n_50 <= 3
    strong = n_75 is not None and n_75 <= 7
    print(f"  PASS (top 3 >= 50%): {passed}. STRONG (top 7 >= 75%): {strong}")

    return {
        'thermal_q1': thermal_q1,
        'thermal_q5': thermal_q5,
        'total_decline': total_decline,
        'n_for_50pct': n_50,
        'n_for_75pct': n_75,
        'n_for_90pct': n_90,
        'top_contributors': [(m, float(c), t, n, cat) for m, c, t, n, cat in contributions[:15]],
        'passed': passed,
        'strong': strong,
    }


# ── T4: ch/sh Parallel Positional Gradient ───────────────────────────

def test4_ch_sh_parallel(data):
    """T4: Do shared MIDDLEs show parallel positional gradients under ch and sh?"""
    print("\n=== T4: ch/sh Parallel Positional Gradient ===")

    ch_mids = set(data['prefix_mid_total'].get('ch', {}).keys())
    sh_mids = set(data['prefix_mid_total'].get('sh', {}).keys())
    shared = ch_mids & sh_mids
    ch_only = ch_mids - sh_mids
    sh_only = sh_mids - ch_mids

    print(f"  ch MIDDLEs: {len(ch_mids)}, sh MIDDLEs: {len(sh_mids)}, shared: {len(shared)}")
    print(f"  ch-only: {len(ch_only)}, sh-only: {len(sh_only)}")

    # For shared MIDDLEs with sufficient data: compare positional profiles
    ch_qcounts = data['prefix_mid_qcounts'].get('ch', {})
    sh_qcounts = data['prefix_mid_qcounts'].get('sh', {})

    shared_profiles = []
    for mid in sorted(shared):
        ch_total = data['prefix_mid_total']['ch'][mid]
        sh_total = data['prefix_mid_total']['sh'][mid]
        if ch_total < 10 or sh_total < 10:
            continue

        # Normalized quintile profiles
        ch_q = ch_qcounts[mid].astype(float)
        sh_q = sh_qcounts[mid].astype(float)
        ch_norm = ch_q / max(ch_q.sum(), 1)
        sh_norm = sh_q / max(sh_q.sum(), 1)

        # Center of mass
        quintiles = np.arange(N_QUINTILES, dtype=float)
        ch_com = float(np.dot(quintiles, ch_norm))
        sh_com = float(np.dot(quintiles, sh_norm))

        shared_profiles.append((mid, ch_com, sh_com, ch_total, sh_total))

    print(f"  Shared MIDDLEs with N>=10 under both: {len(shared_profiles)}")

    if len(shared_profiles) >= 5:
        ch_coms = [x[1] for x in shared_profiles]
        sh_coms = [x[2] for x in shared_profiles]
        rho, p = spearmanr(ch_coms, sh_coms)
        print(f"  Position COM correlation (shared MIDDLEs): rho={rho:.3f}, p={p:.4f}")

        print(f"\n  {'MIDDLE':12s} {'ch_COM':>7s} {'sh_COM':>7s} {'ch_n':>5s} {'sh_n':>5s}")
        for mid, ch_com, sh_com, ch_n, sh_n in sorted(shared_profiles, key=lambda x: x[1])[:10]:
            print(f"  {mid:12s} {ch_com:7.3f} {sh_com:7.3f} {ch_n:5d} {sh_n:5d}")
    else:
        rho, p = 0.0, 1.0
        print(f"  Insufficient shared MIDDLEs for correlation")

    # Non-shared: compare direction (mean COM of ch-only vs sh-only)
    def mean_com(prefix, mid_set, qcounts, totals):
        coms = []
        weights = []
        for mid in mid_set:
            t = totals.get(mid, 0)
            if t < 5:
                continue
            qc = qcounts.get(mid, np.zeros(N_QUINTILES))
            qn = qc.astype(float) / max(qc.sum(), 1)
            com = float(np.dot(np.arange(N_QUINTILES, dtype=float), qn))
            coms.append(com)
            weights.append(t)
        if coms:
            return float(np.average(coms, weights=weights))
        return 2.0

    ch_only_com = mean_com('ch', ch_only, ch_qcounts, data['prefix_mid_total']['ch'])
    sh_only_com = mean_com('sh', sh_only, sh_qcounts, data['prefix_mid_total']['sh'])
    print(f"\n  ch-only MIDDLEs mean COM: {ch_only_com:.3f}")
    print(f"  sh-only MIDDLEs mean COM: {sh_only_com:.3f}")

    passed = len(shared_profiles) >= 5 and rho >= 0.60
    print(f"  PASS (shared rho >= 0.60): {passed}")

    return {
        'n_shared': len(shared),
        'n_ch_only': len(ch_only),
        'n_sh_only': len(sh_only),
        'n_shared_testable': len(shared_profiles),
        'shared_rho': float(rho),
        'shared_p': float(p),
        'ch_only_mean_com': ch_only_com,
        'sh_only_mean_com': sh_only_com,
        'passed': passed,
    }


# ── T5: QO vs CHSH Positional MIDDLE Divergence ─────────────────────

def test5_qo_vs_chsh(data):
    """T5: Do QO-lane MIDDLEs appear earlier than CHSH-lane MIDDLEs?"""
    print("\n=== T5: QO vs CHSH Positional MIDDLE Divergence ===")

    qo_mids = set(data['prefix_mid_total'].get('qo', {}).keys())
    ch_mids = set(data['prefix_mid_total'].get('ch', {}).keys())
    sh_mids = set(data['prefix_mid_total'].get('sh', {}).keys())
    chsh_mids = ch_mids | sh_mids

    qo_only = qo_mids - chsh_mids
    chsh_only = chsh_mids - qo_mids

    print(f"  QO-only MIDDLEs: {len(qo_only)}, CHSH-only: {len(chsh_only)}")

    # Compute mean position for each group under their respective PREFIXes
    def mid_positions(prefix, mid_set, qcounts, totals):
        positions = []
        for mid in mid_set:
            t = totals.get(mid, 0)
            if t < 5:
                continue
            qc = qcounts.get(mid, np.zeros(N_QUINTILES))
            qn = qc.astype(float) / max(qc.sum(), 1)
            com = float(np.dot(np.arange(N_QUINTILES, dtype=float), qn))
            positions.append(com)
        return positions

    qo_positions = mid_positions('qo', qo_only,
                                  data['prefix_mid_qcounts'].get('qo', {}),
                                  data['prefix_mid_total'].get('qo', {}))
    chsh_positions = []
    for prefix in ['ch', 'sh']:
        chsh_positions.extend(mid_positions(prefix, chsh_only,
                                             data['prefix_mid_qcounts'].get(prefix, {}),
                                             data['prefix_mid_total'].get(prefix, {})))

    if qo_positions and chsh_positions:
        qo_mean = float(np.mean(qo_positions))
        chsh_mean = float(np.mean(chsh_positions))
        stat, p = mannwhitneyu(qo_positions, chsh_positions, alternative='less')
        print(f"  QO-only mean position: {qo_mean:.3f} (n={len(qo_positions)})")
        print(f"  CHSH-only mean position: {chsh_mean:.3f} (n={len(chsh_positions)})")
        print(f"  Mann-Whitney U (QO < CHSH): U={stat:.1f}, p={p:.4f}")

        passed = bool(qo_mean <= 2.25 and p < 0.01)
    else:
        qo_mean = chsh_mean = None
        p = 1.0
        stat = 0
        passed = False
        print(f"  Insufficient data")

    # Within qo: k-atom MIDDLEs vs non-k
    qo_qcounts = data['prefix_mid_qcounts'].get('qo', {})
    qo_totals = data['prefix_mid_total'].get('qo', {})
    k_positions = []
    nonk_positions = []
    for mid, total in qo_totals.items():
        if total < 5:
            continue
        qc = qo_qcounts[mid].astype(float)
        com = float(np.dot(np.arange(N_QUINTILES, dtype=float), qc / max(qc.sum(), 1)))
        if 'k' in mid:
            k_positions.append(com)
        else:
            nonk_positions.append(com)

    if k_positions and nonk_positions:
        k_mean = float(np.mean(k_positions))
        nonk_mean = float(np.mean(nonk_positions))
        print(f"\n  Within qo: k-MIDDLEs mean pos={k_mean:.3f} (n={len(k_positions)}), "
              f"non-k mean pos={nonk_mean:.3f} (n={len(nonk_positions)})")
    else:
        k_mean = nonk_mean = None

    print(f"  PASS (QO-only mean <= 2.25, p < 0.01): {passed}")

    return {
        'n_qo_only': len(qo_only),
        'n_chsh_only': len(chsh_only),
        'qo_mean_position': qo_mean,
        'chsh_mean_position': chsh_mean,
        'mann_whitney_p': float(p),
        'k_mean_position': k_mean,
        'nonk_mean_position': nonk_mean,
        'passed': passed,
    }


# ── T6: BARE Positional MIDDLE Selection ─────────────────────────────

def test6_bare_contrast(data):
    """T6: Does BARE show weaker MIDDLE positional selection than prefixed tokens?"""
    print("\n=== T6: BARE Positional MIDDLE Selection (Contrast) ===")

    # Compute JSD(Q1,Q5) for all PREFIXes with >= 100 tokens
    prefix_jsds = {}
    for prefix, mid_total in data['prefix_mid_total'].items():
        total = sum(mid_total.values())
        if total < 100:
            continue

        q_mids = data['prefix_q_mid'].get(prefix, {})
        q1 = q_mids.get(0, Counter())
        q5 = q_mids.get(4, Counter())

        all_mids = sorted(set(q1.keys()) | set(q5.keys()))
        if len(all_mids) < 3:
            continue

        q1_vec = np.array([q1.get(m, 0) for m in all_mids], dtype=float)
        q5_vec = np.array([q5.get(m, 0) for m in all_mids], dtype=float)
        eps = 1e-10
        q1_norm = (q1_vec + eps) / (q1_vec + eps).sum()
        q5_norm = (q5_vec + eps) / (q5_vec + eps).sum()
        jsd = float(jensenshannon(q1_norm, q5_norm) ** 2)

        label = prefix or 'BARE'
        prefix_jsds[label] = jsd

    # Sort and show
    sorted_jsds = sorted(prefix_jsds.items(), key=lambda x: x[1])
    print(f"  PREFIX JSD(Q1,Q5) ranking (lowest = least positional selection):")
    for label, jsd in sorted_jsds:
        marker = ' <-- BARE' if label == 'BARE' else ''
        print(f"    {label:8s}: JSD={jsd:.6f}{marker}")

    bare_jsd = prefix_jsds.get('BARE', 0)
    all_jsds = list(prefix_jsds.values())
    median_jsd = float(np.median(all_jsds))
    bare_rank = sorted([j for j in all_jsds]).index(bare_jsd) + 1 if bare_jsd in all_jsds else 0

    print(f"\n  BARE JSD: {bare_jsd:.6f}, median: {median_jsd:.6f}")
    print(f"  BARE rank: {bare_rank}/{len(all_jsds)} (1=weakest)")

    passed = bare_jsd < median_jsd
    print(f"  PASS (BARE below median): {passed}")

    return {
        'prefix_jsds': prefix_jsds,
        'bare_jsd': bare_jsd,
        'median_jsd': median_jsd,
        'bare_rank': bare_rank,
        'total_prefixes': len(all_jsds),
        'passed': passed,
    }


# ── T7: Position Specialists vs Compatibility Constraints ────────────

def test7_specialist_compatibility(data):
    """T7: Are position-specialist MIDDLEs enriched in being PREFIX-restricted?"""
    print("\n=== T7: Position Specialists vs Compatibility Constraints ===")

    # Compute which MIDDLEs appear under which PREFIXes
    mid_prefix_set = defaultdict(set)
    for prefix, mid_total in data['prefix_mid_total'].items():
        for mid in mid_total:
            mid_prefix_set[mid].add(prefix)

    # Total PREFIXes that have >= 20 tokens (to define the "expected" set)
    active_prefixes = set()
    for prefix, mid_total in data['prefix_mid_total'].items():
        if sum(mid_total.values()) >= 20:
            active_prefixes.add(prefix)
    n_active = len(active_prefixes)
    print(f"  Active PREFIXes (N>=20): {n_active}")

    # For each MIDDLE: compute PREFIX breadth (how many PREFIXes it appears under)
    mid_breadth = {mid: len(prefixes & active_prefixes) for mid, prefixes in mid_prefix_set.items()}

    # Classify MIDDLEs as position-specialists vs flat (using ch and sh from T2 logic)
    # Recompute for simplicity: specialist = chi2 significant at p<0.05 within ch or sh
    from scipy.stats import chi2 as chi2_dist

    specialist_mids = set()
    flat_mids = set()

    for prefix in ['ch', 'sh', 'qo']:
        mid_qcounts = data['prefix_mid_qcounts'].get(prefix, {})
        mid_totals = data['prefix_mid_total'].get(prefix, Counter())

        for mid, total in mid_totals.items():
            if total < 10:
                continue

            qc = mid_qcounts[mid]
            expected = total / N_QUINTILES
            chi2_val = float(sum((qc[q] - expected) ** 2 / max(expected, 1e-10) for q in range(N_QUINTILES)))
            p = float(1 - chi2_dist.cdf(chi2_val, N_QUINTILES - 1))

            if p < 0.05:
                specialist_mids.add(mid)
            else:
                flat_mids.add(mid)

    # Remove overlap (if a mid is specialist under one prefix and flat under another, call it specialist)
    flat_mids = flat_mids - specialist_mids

    print(f"  Position specialists: {len(specialist_mids)}")
    print(f"  Flat MIDDLEs: {len(flat_mids)}")

    # Compare PREFIX breadth
    spec_breadths = [mid_breadth.get(m, 0) for m in specialist_mids if m in mid_breadth]
    flat_breadths = [mid_breadth.get(m, 0) for m in flat_mids if m in mid_breadth]

    if spec_breadths and flat_breadths:
        spec_mean = float(np.mean(spec_breadths))
        flat_mean = float(np.mean(flat_breadths))
        print(f"\n  Specialist mean PREFIX breadth: {spec_mean:.2f}")
        print(f"  Flat mean PREFIX breadth: {flat_mean:.2f}")

        # Are specialists MORE or LESS PREFIX-restricted?
        stat, p = mannwhitneyu(spec_breadths, flat_breadths, alternative='two-sided')
        print(f"  Mann-Whitney: U={stat:.1f}, p={p:.4f}")

        # Interpretation: if specialists have LOWER breadth, they're more PREFIX-restricted
        # (consistent with C911 forbidden pairs limiting where they can go)
        if spec_mean < flat_mean and p < 0.05:
            verdict = 'ENRICHED: specialists are more PREFIX-restricted'
        elif spec_mean > flat_mean and p < 0.05:
            verdict = 'DEPLETED: specialists are LESS restricted (more versatile)'
        else:
            verdict = 'NO_DIFFERENCE: positional specialization independent of restriction'
    else:
        spec_mean = flat_mean = None
        p = 1.0
        stat = 0
        verdict = 'INSUFFICIENT_DATA'

    print(f"  T7 verdict: {verdict}")

    return {
        'n_specialists': len(specialist_mids),
        'n_flat': len(flat_mids),
        'specialist_mean_breadth': spec_mean,
        'flat_mean_breadth': flat_mean,
        'mann_whitney_p': float(p),
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()

    t1 = test1_positional_entropy(data)
    t2 = test2_specialist_census(data)
    t3 = test3_gradient_concentration(data)
    t4 = test4_ch_sh_parallel(data)
    t5 = test5_qo_vs_chsh(data)
    t6 = test6_bare_contrast(data)
    t7 = test7_specialist_compatibility(data)

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  T1 (positional entropy):    {'PASS' if t1.get('passed') else 'FAIL'} "
          f"({t1.get('sig_count', 0)}/7 significant)")
    print(f"  T2 (specialist census):     {'PASS' if t2.get('passed') else 'FAIL'}")
    print(f"  T3 (gradient concentration): {'PASS' if t3.get('passed') else 'FAIL'} "
          f"(top {t3.get('n_for_50pct', '?')} for 50%)")
    print(f"  T4 (ch/sh parallel):        {'PASS' if t4.get('passed') else 'FAIL'} "
          f"(rho={t4.get('shared_rho', 0):.3f})")
    print(f"  T5 (QO vs CHSH):            {'PASS' if t5.get('passed') else 'FAIL'}")
    print(f"  T6 (BARE contrast):         {'PASS' if t6.get('passed') else 'FAIL'}")
    print(f"  T7 (specialist breadth):     {t7.get('verdict', '?')}")

    tests_passed = sum(1 for t in [t1, t2, t3, t4, t5, t6] if t.get('passed'))
    print(f"\n  Tests passed: {tests_passed}/6")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    results = {
        'metadata': {
            'phase': 487,
            'name': 'WITHIN_PREFIX_MIDDLE_POSITION',
            'n_tokens': data['n_tokens'],
            'n_lines': data['n_lines'],
            'n_middles': len(data['mid_to_cat']),
            'elapsed_seconds': elapsed,
        },
        'T1_positional_entropy': t1,
        'T2_specialist_census': t2,
        'T3_gradient_concentration': t3,
        'T4_ch_sh_parallel': t4,
        'T5_qo_vs_chsh': t5,
        'T6_bare_contrast': t6,
        'T7_specialist_compatibility': t7,
        'tests_passed': tests_passed,
    }

    out_path = RESULTS_DIR / 'within_prefix_middle_position.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

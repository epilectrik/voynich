"""
T4: Controlled Excursion Validation Battery
=============================================
Phase 568 - CONTROLLED_EXCURSION_METRICS

Loads T1 (primary runs), T2 (null/baseline runs), and T3 (COF observability)
results and runs the full validation battery:

  P2       - Anchor: Line Packet Shape Recovery (Spearman, must pass)
  EP1-EP7  - Primary excursion/precision tests
  ED1-ED7  - Diagnostics (informational, no pass/fail gate)

Inputs:
  - t1_controlled_excursion_runs.json       (T1 primary runs)
  - t2_controlled_excursion_null_runs.json   (T2 reference, baselines, nulls)
  - t3_cof_observability.json                (T3 COF observability analyses)
  - t3_line_packets.json                     (line packet profiles, P2 anchor)
  - t2b_supervisory_interface_unrouted.json  (token contributions, P2 anchor)

Output:
  - t4_controlled_excursion_validation.json
"""

import json
import math
import random
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
RESULTS_DIR = PHASE_DIR / 'results'
PROJECT_ROOT = PHASE_DIR.parent.parent

T1_PATH = RESULTS_DIR / 't1_controlled_excursion_runs.json'
T2_PATH = RESULTS_DIR / 't2_controlled_excursion_null_runs.json'
T3_PATH = RESULTS_DIR / 't3_cof_observability.json'

LINE_PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                     / 'results' / 't3_line_packets.json')
T2B_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
            / 'results' / 't2b_supervisory_interface_unrouted.json')

OUTPUT_PATH = RESULTS_DIR / 't4_controlled_excursion_validation.json'

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STATE_VARS = ['T', 'RC', 'S', 'C', 'TR', 'X', 'Y']
N_SVS = len(STATE_VARS)

PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r',
    'f40v', 'f43v', 'f34r', 'f31r', 'f39v',
    'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]

N_PILOT = len(PILOT_FOLIOS)

# COF variant keys (from T3)
CCY_VARIANTS = ['CCY', 'CCY_cof1', 'CCY_cof2', 'CCY_cof3']


# ---------------------------------------------------------------------------
# Statistical helpers (no scipy dependency)
# ---------------------------------------------------------------------------
def _normal_cdf(x):
    """Standard normal CDF via math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _rank(arr):
    """Compute fractional ranks for an array."""
    n = len(arr)
    indexed = sorted(enumerate(arr), key=lambda p: p[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
            j += 1
        mean_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = mean_rank
        i = j + 1
    return ranks


def spearman_r(x, y):
    """Spearman rank correlation with t-test p-value approximation."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    rx = _rank(x)
    ry = _rank(y)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rs = 1.0 - 6.0 * d2 / (n * (n * n - 1))
    # Clamp for numerical safety
    rs = max(-1.0, min(1.0, rs))
    if abs(rs) >= 1.0:
        return rs, 0.0
    t_stat = rs * math.sqrt((n - 2) / (1.0 - rs * rs))
    p = 2.0 * (1.0 - _normal_cdf(abs(t_stat)))
    return rs, p


def pearson_r(x, y):
    """Pearson product-moment correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    denom = (sxx * syy) ** 0.5
    return sxy / denom if denom > 1e-10 else 0.0


def cohens_d(group1, group2):
    """Cohen's d effect size between two independent groups."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0
    mean1 = sum(group1) / n1
    mean2 = sum(group2) / n2
    var1 = sum((x - mean1) ** 2 for x in group1) / max(n1 - 1, 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / max(n2 - 1, 1)
    pooled_std = ((var1 * (n1 - 1) + var2 * (n2 - 1)) / max(n1 + n2 - 2, 1)) ** 0.5
    return (mean1 - mean2) / pooled_std if pooled_std > 1e-10 else 0.0


def bootstrap_p(full_vals, b10_vals, n_resamples=1000, seed=42):
    """Permutation-based bootstrap p-value for mean difference."""
    if not full_vals or not b10_vals:
        return 1.0
    rng = random.Random(seed)
    observed_delta = sum(full_vals) / len(full_vals) - sum(b10_vals) / len(b10_vals)
    combined = list(full_vals) + list(b10_vals)
    n1 = len(full_vals)
    count_extreme = 0
    for _ in range(n_resamples):
        rng.shuffle(combined)
        g1 = combined[:n1]
        g2 = combined[n1:]
        perm_delta = sum(g1) / len(g1) - sum(g2) / len(g2)
        if abs(perm_delta) >= abs(observed_delta):
            count_extreme += 1
    return count_extreme / n_resamples


# ---------------------------------------------------------------------------
# Helpers: extract preferred-profile metrics from T1
# ---------------------------------------------------------------------------
def get_preferred_runs(t1_primary_runs, preferred_profiles):
    """
    For each folio in PILOT_FOLIOS, extract T1 metrics for the preferred
    profile. Returns dict: folio -> metric_dict.
    """
    preferred = {}
    for folio in PILOT_FOLIOS:
        prof_name = preferred_profiles.get(folio)
        if prof_name is None:
            continue
        folio_profiles = t1_primary_runs.get(folio, {})
        run = folio_profiles.get(prof_name)
        if run is None:
            continue
        preferred[folio] = run
    return preferred


def get_null_mean(null_runs, null_key, folio, metric_key):
    """Get mean_{metric} from null_runs[null_key][folio]."""
    folio_data = null_runs.get(null_key, {}).get(folio, {})
    return folio_data.get(f'mean_{metric_key}', 0.0)


def get_baseline_by_folio(baseline_runs, baseline_key):
    """Return dict: folio -> run_dict for a given baseline."""
    out = {}
    for entry in baseline_runs.get(baseline_key, []):
        fo = entry.get('folio', '')
        if fo:
            out[fo] = entry
    return out


# ===================================================================
# P2: Line Packet Shape Recovery (anchor test)
# ===================================================================
def run_p2(line_packets, t2b_tokens):
    """
    For each line, sum token contributions per SV.
    For each SV index i, Spearman-correlate the per-line contribution
    sum with the per-line packet profile[i].

    PASS if >= 5/7 SVs have p < 0.05.
    """
    print("\n" + "=" * 70)
    print("P2: Line Packet Shape Recovery (anchor)")
    print("=" * 70)

    # Build per-line contribution sums (keyed by "folio|line")
    line_contrib_sums = defaultdict(lambda: [0.0] * N_SVS)
    line_token_counts = defaultdict(int)

    for tok in t2b_tokens:
        folio = tok['folio']
        line = tok['line']
        key = f"{folio}|{line}"
        contribs = tok['contributions']
        for i in range(N_SVS):
            line_contrib_sums[key][i] += contribs[i]
        line_token_counts[key] += 1

    # Collect matched line keys (must exist in both line_packets and contribs)
    packet_keys = set(line_packets.keys())
    contrib_keys = set(line_contrib_sums.keys())
    matched_keys = sorted(packet_keys & contrib_keys)

    print(f"  Lines in packets: {len(packet_keys)}")
    print(f"  Lines with contributions: {len(contrib_keys)}")
    print(f"  Matched lines: {len(matched_keys)}")

    if len(matched_keys) < 10:
        print("  WARNING: too few matched lines for reliable correlation")

    # For each SV, correlate contribution sum with profile[sv_idx]
    per_sv = {}
    n_sig = 0

    for sv_idx, sv_name in enumerate(STATE_VARS):
        x_vals = []
        y_vals = []
        for key in matched_keys:
            x_vals.append(line_contrib_sums[key][sv_idx])
            profile = line_packets[key]['profile']
            # Use profile[sv_idx] as the "corresponding" packet profile value
            # Profile is 15D; first 7 indices map to SVs by position
            if sv_idx < len(profile):
                y_vals.append(profile[sv_idx])
            else:
                y_vals.append(0.0)

        rs, p_val = spearman_r(x_vals, y_vals)
        sig = p_val < 0.05
        if sig:
            n_sig += 1

        per_sv[sv_name] = {
            'spearman_r': round(rs, 6),
            'p_value': round(p_val, 6),
            'significant': sig,
            'n_lines': len(x_vals),
        }
        tag = "***" if sig else "   "
        print(f"  {sv_name:<3}: r={rs:+.4f}  p={p_val:.6f}  n={len(x_vals)} {tag}")

    result = "PASS" if n_sig >= 5 else "FAIL"
    print(f"\n  P2 result: {result} ({n_sig}/7 significant, gate=5)")

    return {
        'result': result,
        'n_significant': n_sig,
        'gate': 5,
        'n_matched_lines': len(matched_keys),
        'per_sv': per_sv,
    }


# ===================================================================
# EP1: Full WCU > N1 WCU for >= 14/20 folios
# ===================================================================
def run_ep1(preferred, null_runs):
    """HARD gate: full WCU > N1 mean WCU for >= 14/20 folios."""
    print("\n" + "-" * 70)
    print("EP1: Full WCU > N1 WCU (gate=14/20)")
    print("-" * 70)

    per_folio = {}
    n_pass = 0

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing'}
            continue

        full_wcu = run.get('WCU', 0.0)
        null_wcu = get_null_mean(null_runs, 'N1', folio, 'WCU')
        passed = full_wcu > null_wcu

        if passed:
            n_pass += 1

        per_folio[folio] = {
            'full_WCU': round(full_wcu, 6),
            'N1_mean_WCU': round(null_wcu, 6),
            'pass': passed,
        }
        tag = "PASS" if passed else "FAIL"
        print(f"  {folio:<8}: full={full_wcu:.4f}  N1={null_wcu:.4f}  [{tag}]")

    result = "PASS" if n_pass >= 14 else "FAIL"
    print(f"\n  EP1 result: {result} ({n_pass}/20, gate=14)")

    return {
        'result': result,
        'n_pass': n_pass,
        'gate': 14,
        'n_total': N_PILOT,
        'per_folio': per_folio,
    }


# ===================================================================
# EP2: Full SLR > mean(N1-N4) SLR for >= 14/20 folios
# ===================================================================
def run_ep2(preferred, null_runs):
    """HARD gate: full SLR > average of N1-N4 mean SLR for >= 14/20."""
    print("\n" + "-" * 70)
    print("EP2: Full SLR > mean(N1-N4) SLR (gate=14/20)")
    print("-" * 70)

    per_folio = {}
    n_pass = 0

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing'}
            continue

        full_slr = run.get('SLR_mean', 0.0)
        null_slrs = []
        for nk in ['N1', 'N2', 'N3', 'N4']:
            null_slrs.append(get_null_mean(null_runs, nk, folio, 'SLR_mean'))
        avg_null_slr = sum(null_slrs) / len(null_slrs) if null_slrs else 0.0
        passed = full_slr > avg_null_slr

        if passed:
            n_pass += 1

        per_folio[folio] = {
            'full_SLR': round(full_slr, 6),
            'null_avg_SLR': round(avg_null_slr, 6),
            'pass': passed,
        }
        tag = "PASS" if passed else "FAIL"
        print(f"  {folio:<8}: full={full_slr:.4f}  null_avg={avg_null_slr:.4f}  [{tag}]")

    result = "PASS" if n_pass >= 14 else "FAIL"
    print(f"\n  EP2 result: {result} ({n_pass}/20, gate=14)")

    return {
        'result': result,
        'n_pass': n_pass,
        'gate': 14,
        'n_total': N_PILOT,
        'per_folio': per_folio,
    }


# ===================================================================
# EP3: Full UEB < mean(N1-N4) UEB for >= 14/20 folios
# ===================================================================
def run_ep3(preferred, null_runs):
    """HARD gate: full UEB < average of N1-N4 mean UEB for >= 14/20."""
    print("\n" + "-" * 70)
    print("EP3: Full UEB < mean(N1-N4) UEB (gate=14/20)")
    print("-" * 70)

    per_folio = {}
    n_pass = 0

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing'}
            continue

        full_ueb = run.get('UEB', 0.0)
        null_uebs = []
        for nk in ['N1', 'N2', 'N3', 'N4']:
            null_uebs.append(get_null_mean(null_runs, nk, folio, 'UEB'))
        avg_null_ueb = sum(null_uebs) / len(null_uebs) if null_uebs else 0.0
        passed = full_ueb < avg_null_ueb

        if passed:
            n_pass += 1

        per_folio[folio] = {
            'full_UEB': round(full_ueb, 6),
            'null_avg_UEB': round(avg_null_ueb, 6),
            'pass': passed,
        }
        tag = "PASS" if passed else "FAIL"
        print(f"  {folio:<8}: full={full_ueb:.4f}  null_avg={avg_null_ueb:.4f}  [{tag}]")

    result = "PASS" if n_pass >= 14 else "FAIL"
    print(f"\n  EP3 result: {result} ({n_pass}/20, gate=14)")

    return {
        'result': result,
        'n_pass': n_pass,
        'gate': 14,
        'n_total': N_PILOT,
        'per_folio': per_folio,
    }


# ===================================================================
# EP4: Full CCY > N2 CCY AND N4 CCY for >= 12/20 or 14/eligible
# ===================================================================
def run_ep4(preferred, null_runs):
    """SOFT gate: full CCY > N2 AND N4 CCY."""
    print("\n" + "-" * 70)
    print("EP4: Full CCY > N2 CCY AND N4 CCY (gate=12/20 or 14/eligible)")
    print("-" * 70)

    per_folio = {}
    n_pass_all = 0
    n_eligible = 0
    n_pass_eligible = 0

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing'}
            continue

        full_ccy = run.get('CCY', 0.0)
        n2_ccy = get_null_mean(null_runs, 'N2', folio, 'CCY')
        n4_ccy = get_null_mean(null_runs, 'N4', folio, 'CCY')

        passed = (full_ccy > n2_ccy) and (full_ccy > n4_ccy)

        # Eligibility: a folio is structurally ineligible if full CCY == 0
        # AND all null CCY == 0
        all_null_zero = (abs(n2_ccy) < 1e-10) and (abs(n4_ccy) < 1e-10)
        structurally_ineligible = (abs(full_ccy) < 1e-10) and all_null_zero

        if not structurally_ineligible:
            n_eligible += 1
            if passed:
                n_pass_eligible += 1

        if passed:
            n_pass_all += 1

        per_folio[folio] = {
            'full_CCY': round(full_ccy, 6),
            'N2_mean_CCY': round(n2_ccy, 6),
            'N4_mean_CCY': round(n4_ccy, 6),
            'pass': passed,
            'eligible': not structurally_ineligible,
        }
        tag = "PASS" if passed else "FAIL"
        elig_tag = "" if not structurally_ineligible else " (ineligible)"
        print(f"  {folio:<8}: full={full_ccy:.4f}  N2={n2_ccy:.4f}  "
              f"N4={n4_ccy:.4f}  [{tag}]{elig_tag}")

    # PASS if EP4_all >= 12 OR (EP4_eligible_count >= 14 and eligible > 0)
    pass_all_gate = n_pass_all >= 12
    pass_eligible_gate = (n_pass_eligible >= 14) and (n_eligible > 0)
    result = "PASS" if (pass_all_gate or pass_eligible_gate) else "FAIL"

    print(f"\n  EP4 all:      {n_pass_all}/20 (gate=12)")
    print(f"  EP4 eligible: {n_pass_eligible}/{n_eligible} (gate=14)")
    print(f"  EP4 result:   {result}")

    return {
        'result': result,
        'EP4_all': n_pass_all,
        'EP4_eligible': n_pass_eligible,
        'eligible_count': n_eligible,
        'gate_all': 12,
        'gate_eligible': 14,
        'n_total': N_PILOT,
        'per_folio': per_folio,
    }


# ===================================================================
# EP5: B10 delta significant on WCU OR SLR OR CCY
# ===================================================================
def run_ep5(preferred, baseline_runs):
    """
    HARD gate: at least one of WCU, SLR_mean, CCY shows significant
    difference between full model and B10 baseline.
    """
    print("\n" + "-" * 70)
    print("EP5: B10 Delta Significance (WCU / SLR / CCY)")
    print("-" * 70)

    b10_by_folio = get_baseline_by_folio(baseline_runs, 'B10')

    # Metric ranges for 0.01 threshold
    metric_ranges = {
        'WCU': 3.0,     # [-2.0, 1.0]
        'SLR_mean': 2.0, # [-1.0, 1.0]
        'CCY': 1.0,      # [0, ~1.0]
    }

    # T1 uses WCP_mean but WCU/SLR_mean/CCY are direct keys
    metric_keys_t1 = {'WCU': 'WCU', 'SLR_mean': 'SLR_mean', 'CCY': 'CCY'}
    metric_keys_b10 = {'WCU': 'WCU', 'SLR_mean': 'SLR_mean', 'CCY': 'CCY'}

    ep5_metrics = {}
    any_significant = False

    for metric_name in ['WCU', 'SLR_mean', 'CCY']:
        full_vals = []
        b10_vals = []

        for folio in PILOT_FOLIOS:
            run = preferred.get(folio)
            b10 = b10_by_folio.get(folio)
            if run is None or b10 is None:
                continue

            full_vals.append(run.get(metric_keys_t1[metric_name], 0.0))
            b10_vals.append(b10.get(metric_keys_b10[metric_name], 0.0))

        if not full_vals:
            ep5_metrics[metric_name] = {
                'delta': 0.0, 'cohens_d': 0.0, 'bootstrap_p': 1.0,
                'significant': False, 'n_pairs': 0,
            }
            continue

        full_mean = sum(full_vals) / len(full_vals)
        b10_mean = sum(b10_vals) / len(b10_vals)
        delta = abs(full_mean - b10_mean)
        d = cohens_d(full_vals, b10_vals)
        bp = bootstrap_p(full_vals, b10_vals)

        range_threshold = 0.01 * metric_ranges[metric_name]
        sig = (delta > range_threshold) or (abs(d) > 0.35) or (bp < 0.05)

        if sig:
            any_significant = True

        ep5_metrics[metric_name] = {
            'full_mean': round(full_mean, 6),
            'b10_mean': round(b10_mean, 6),
            'delta': round(delta, 6),
            'range_threshold': round(range_threshold, 6),
            'cohens_d': round(d, 6),
            'bootstrap_p': round(bp, 6),
            'significant': sig,
            'n_pairs': len(full_vals),
        }

        tag = "SIG" if sig else "   "
        print(f"  {metric_name:<10}: delta={delta:.4f} (thr={range_threshold:.4f})  "
              f"d={d:.4f}  p_boot={bp:.4f}  [{tag}]")

    result = "PASS" if any_significant else "FAIL"
    print(f"\n  EP5 result: {result} (any metric significant = {any_significant})")

    return {
        'result': result,
        'any_significant': any_significant,
        'per_metric': ep5_metrics,
    }


# ===================================================================
# EP6: Full WCP > N1 WCP for >= 14/20 folios
# ===================================================================
def run_ep6(preferred, null_runs):
    """HARD gate: full WCP > N1 mean WCP for >= 14/20 folios."""
    print("\n" + "-" * 70)
    print("EP6: Full WCP > N1 WCP (gate=14/20)")
    print("-" * 70)

    per_folio = {}
    n_pass = 0

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing'}
            continue

        # T2 reference uses 'WCP', T1 uses 'WCP_mean'
        full_wcp = run.get('WCP', run.get('WCP_mean', 0.0))
        null_wcp = get_null_mean(null_runs, 'N1', folio, 'WCP')
        passed = full_wcp > null_wcp

        if passed:
            n_pass += 1

        per_folio[folio] = {
            'full_WCP': round(full_wcp, 6),
            'N1_mean_WCP': round(null_wcp, 6),
            'pass': passed,
        }
        tag = "PASS" if passed else "FAIL"
        print(f"  {folio:<8}: full={full_wcp:.4f}  N1={null_wcp:.4f}  [{tag}]")

    result = "PASS" if n_pass >= 14 else "FAIL"
    print(f"\n  EP6 result: {result} ({n_pass}/20, gate=14)")

    return {
        'result': result,
        'n_pass': n_pass,
        'gate': 14,
        'n_total': N_PILOT,
        'per_folio': per_folio,
    }


# ===================================================================
# EP7: Best COF variant improves >= 1 criterion without > 5% degradation
# ===================================================================
def run_ep7(t3_data):
    """
    SOFT gate: does any COF variant improve at least one criterion
    without degrading any other by > 5%?

    Criteria checked from T3:
      - OA3 (B10 sensitivity): higher |delta| or |d| than base CCY
      - OA5 (eligibility expansion): more non-zero folios than base CCY
      - OA2 (closure-excursion overlap): higher overlap fraction if available
    """
    print("\n" + "-" * 70)
    print("EP7: Best COF Variant (improve >= 1, no > 5% degradation)")
    print("-" * 70)

    if t3_data is None:
        print("  T3 data not available -- EP7 SKIPPED (treated as FAIL)")
        return {
            'result': 'FAIL',
            'reason': 'T3 data not available',
            'best_variant': None,
        }

    # Extract OA3 (B10 sensitivity)
    oa3 = t3_data.get('OA3_b10_sensitivity', {})
    oa3_per_variant = oa3.get('per_variant', {})

    # Extract OA5 (eligibility expansion)
    oa5 = t3_data.get('OA5_eligibility_expansion', {})
    oa5_per_variant = oa5.get('per_variant', {})

    # Extract OA2 (closure-excursion overlap) if available
    oa2 = t3_data.get('OA2_closure_excursion_overlap', {})
    oa2_per_variant = oa2.get('per_variant', {})

    # Base CCY values
    base_d = abs(oa3_per_variant.get('CCY', {}).get('cohens_d', 0.0))
    base_delta = abs(oa3_per_variant.get('CCY', {}).get('delta', 0.0))
    base_nonzero = oa5_per_variant.get('CCY', {}).get('n_nonzero', 0)

    # OA2 uses short names: CTS, COF1, COF2, COF3
    oa2_key_map = {
        'CCY_cof1': 'COF1',
        'CCY_cof2': 'COF2',
        'CCY_cof3': 'COF3',
    }
    base_overlap = oa2_per_variant.get('CTS', {}).get('overlap_frac', 0.0)

    cof_variants = ['CCY_cof1', 'CCY_cof2', 'CCY_cof3']
    best_variant = None
    best_detail = None

    for cof_key in cof_variants:
        # OA3 criteria
        cof_d = abs(oa3_per_variant.get(cof_key, {}).get('cohens_d', 0.0))
        cof_delta = abs(oa3_per_variant.get(cof_key, {}).get('delta', 0.0))

        # OA5 criteria
        cof_nonzero = oa5_per_variant.get(cof_key, {}).get('n_nonzero', 0)

        # OA2 criteria
        oa2_short = oa2_key_map.get(cof_key, '')
        cof_overlap = oa2_per_variant.get(oa2_short, {}).get('overlap_frac', 0.0)

        # Check improvements
        improves_b10_d = cof_d > base_d
        improves_b10_delta = cof_delta > base_delta
        improves_eligibility = cof_nonzero > base_nonzero
        improves_overlap = cof_overlap > base_overlap

        any_improvement = (improves_b10_d or improves_b10_delta
                           or improves_eligibility or improves_overlap)

        # Check degradation (> 5%)
        degradations = []

        # B10 sensitivity degradation
        if base_d > 1e-10:
            d_pct_change = (cof_d - base_d) / base_d
            if d_pct_change < -0.05:
                degradations.append(f"B10_d: {d_pct_change:.3f}")

        if base_delta > 1e-10:
            delta_pct_change = (cof_delta - base_delta) / base_delta
            if delta_pct_change < -0.05:
                degradations.append(f"B10_delta: {delta_pct_change:.3f}")

        # Eligibility degradation
        if base_nonzero > 0:
            nz_pct_change = (cof_nonzero - base_nonzero) / base_nonzero
            if nz_pct_change < -0.05:
                degradations.append(f"eligibility: {nz_pct_change:.3f}")

        # Overlap degradation
        if base_overlap > 1e-10:
            ov_pct_change = (cof_overlap - base_overlap) / base_overlap
            if ov_pct_change < -0.05:
                degradations.append(f"overlap: {ov_pct_change:.3f}")

        passes = any_improvement and len(degradations) == 0

        detail = {
            'improves_b10_d': improves_b10_d,
            'improves_b10_delta': improves_b10_delta,
            'improves_eligibility': improves_eligibility,
            'improves_overlap': improves_overlap,
            'any_improvement': any_improvement,
            'degradations': degradations,
            'passes': passes,
            'cof_d': round(cof_d, 6),
            'cof_delta': round(cof_delta, 6),
            'cof_nonzero': cof_nonzero,
            'cof_overlap': round(cof_overlap, 6),
        }

        tag = "PASS" if passes else "FAIL"
        print(f"  {cof_key}: improve={any_improvement}  "
              f"degrad={degradations}  [{tag}]")

        if passes and best_variant is None:
            best_variant = cof_key
            best_detail = detail

    result = "PASS" if best_variant is not None else "FAIL"
    print(f"\n  EP7 result: {result}")
    if best_variant:
        print(f"  Best variant: {best_variant}")

    return {
        'result': result,
        'best_variant': best_variant,
        'base_values': {
            'base_d': round(base_d, 6),
            'base_delta': round(base_delta, 6),
            'base_nonzero': base_nonzero,
            'base_overlap': round(base_overlap, 6),
        },
        'per_variant': {
            cof_key: {
                'cof_d': round(abs(oa3_per_variant.get(cof_key, {}).get('cohens_d', 0.0)), 6),
                'cof_nonzero': oa5_per_variant.get(cof_key, {}).get('n_nonzero', 0),
            }
            for cof_key in cof_variants
        },
    }


# ===================================================================
# ED1: WCU vs PCV correlation
# ===================================================================
def run_ed1(preferred):
    """Diagnostic: Pearson r between full WCU and PCV across pilot folios."""
    print("\n" + "-" * 70)
    print("ED1: WCU vs PCV Correlation")
    print("-" * 70)

    wcu_vals = []
    pcv_vals = []
    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        wcu_vals.append(run.get('WCU', 0.0))
        pcv_vals.append(run.get('PCV', 0.0))

    r = pearson_r(wcu_vals, pcv_vals) if len(wcu_vals) >= 3 else 0.0
    print(f"  Pearson r(WCU, PCV) = {r:.4f}  (n={len(wcu_vals)})")

    return {
        'wcu_pcv_pearson_r': round(r, 6),
        'n_folios': len(wcu_vals),
    }


# ===================================================================
# ED2: UEB vs SAHB comparison
# ===================================================================
def run_ed2(preferred, null_runs):
    """Diagnostic: compare full and null UEB vs SAHB means."""
    print("\n" + "-" * 70)
    print("ED2: UEB vs SAHB Comparison")
    print("-" * 70)

    full_uebs = []
    full_sahbs = []
    null_uebs = []
    null_sahbs = []

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        full_uebs.append(run.get('UEB', 0.0))
        full_sahbs.append(run.get('SAHB', 0.0))

        n1_ueb = get_null_mean(null_runs, 'N1', folio, 'UEB')
        n1_sahb = get_null_mean(null_runs, 'N1', folio, 'SAHB')
        null_uebs.append(n1_ueb)
        null_sahbs.append(n1_sahb)

    n = len(full_uebs)
    full_mean_ueb = sum(full_uebs) / n if n > 0 else 0.0
    full_mean_sahb = sum(full_sahbs) / n if n > 0 else 0.0
    null_mean_ueb = sum(null_uebs) / n if n > 0 else 0.0
    null_mean_sahb = sum(null_sahbs) / n if n > 0 else 0.0

    ueb_fixes_inversion = (full_mean_ueb < null_mean_ueb) and (full_mean_sahb >= null_mean_sahb)

    print(f"  Full mean UEB:  {full_mean_ueb:.4f}")
    print(f"  Full mean SAHB: {full_mean_sahb:.4f}")
    print(f"  Null mean UEB:  {null_mean_ueb:.4f}")
    print(f"  Null mean SAHB: {null_mean_sahb:.4f}")
    print(f"  UEB fixes burden inversion: {ueb_fixes_inversion}")

    return {
        'full_mean_UEB': round(full_mean_ueb, 6),
        'full_mean_SAHB': round(full_mean_sahb, 6),
        'null_mean_UEB': round(null_mean_ueb, 6),
        'null_mean_SAHB': round(null_mean_sahb, 6),
        'ueb_fixes_inversion': ueb_fixes_inversion,
        'n_folios': n,
    }


# ===================================================================
# ED3: CCY vs QGY by model type
# ===================================================================
def run_ed3(preferred, null_runs):
    """Diagnostic: CCY vs QGY for full model and N2 null."""
    print("\n" + "-" * 70)
    print("ED3: CCY vs QGY by Model Type")
    print("-" * 70)

    full_ccys = []
    full_qgys = []
    n2_ccys = []
    n2_qgys = []

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        full_ccys.append(run.get('CCY', 0.0))
        full_qgys.append(run.get('QGY', 0.0))

        n2_ccy = get_null_mean(null_runs, 'N2', folio, 'CCY')
        n2_qgy = get_null_mean(null_runs, 'N2', folio, 'QGY')
        n2_ccys.append(n2_ccy)
        n2_qgys.append(n2_qgy)

    n = len(full_ccys)
    full_ccy_mean = sum(full_ccys) / n if n > 0 else 0.0
    full_qgy_mean = sum(full_qgys) / n if n > 0 else 0.0
    n2_ccy_mean = sum(n2_ccys) / n if n > 0 else 0.0
    n2_qgy_mean = sum(n2_qgys) / n if n > 0 else 0.0

    stricter_gating_inverts = (full_ccy_mean > full_qgy_mean) and (n2_ccy_mean < n2_qgy_mean)

    print(f"  Full CCY mean: {full_ccy_mean:.4f}")
    print(f"  Full QGY mean: {full_qgy_mean:.4f}")
    print(f"  N2 CCY mean:   {n2_ccy_mean:.4f}")
    print(f"  N2 QGY mean:   {n2_qgy_mean:.4f}")
    print(f"  Stricter gating further inverts N2: {stricter_gating_inverts}")

    return {
        'full_CCY_mean': round(full_ccy_mean, 6),
        'full_QGY_mean': round(full_qgy_mean, 6),
        'N2_CCY_mean': round(n2_ccy_mean, 6),
        'N2_QGY_mean': round(n2_qgy_mean, 6),
        'stricter_gating_inverts_N2': stricter_gating_inverts,
        'n_folios': n,
    }


# ===================================================================
# ED4: SLR vs REF correlation
# ===================================================================
def run_ed4(preferred):
    """Diagnostic: Pearson r between full SLR and REF across pilot folios."""
    print("\n" + "-" * 70)
    print("ED4: SLR vs REF Correlation")
    print("-" * 70)

    slr_vals = []
    ref_vals = []
    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        slr_vals.append(run.get('SLR_mean', 0.0))
        ref_vals.append(run.get('REF_mean', 0.0))

    r = pearson_r(slr_vals, ref_vals) if len(slr_vals) >= 3 else 0.0
    adds_beyond_ref = abs(r) < 0.9  # SLR adds info if not perfectly correlated

    print(f"  Pearson r(SLR, REF) = {r:.4f}  (n={len(slr_vals)})")
    print(f"  SLR adds beyond REF: {adds_beyond_ref}")

    return {
        'slr_ref_pearson_r': round(r, 6),
        'slr_adds_beyond_ref': adds_beyond_ref,
        'n_folios': len(slr_vals),
    }


# ===================================================================
# ED5: WCP by model type
# ===================================================================
def run_ed5(preferred, null_runs):
    """Diagnostic: WCP means for full and all null models."""
    print("\n" + "-" * 70)
    print("ED5: WCP by Model Type")
    print("-" * 70)

    full_wcps = []
    null_wcps = {nk: [] for nk in ['N1', 'N2', 'N3', 'N4']}

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        # T2 reference uses 'WCP', T1 uses 'WCP_mean'
        full_wcps.append(run.get('WCP', run.get('WCP_mean', 0.0)))

        for nk in ['N1', 'N2', 'N3', 'N4']:
            null_wcps[nk].append(get_null_mean(null_runs, nk, folio, 'WCP'))

    n = len(full_wcps)
    full_wcp_mean = sum(full_wcps) / n if n > 0 else 0.0

    result = {
        'full_WCP_mean': round(full_wcp_mean, 6),
        'n_folios': n,
    }

    print(f"  Full WCP mean: {full_wcp_mean:.4f}")

    for nk in ['N1', 'N2', 'N3', 'N4']:
        vals = null_wcps[nk]
        nk_mean = sum(vals) / len(vals) if vals else 0.0
        result[f'{nk}_WCP_mean'] = round(nk_mean, 6)
        print(f"  {nk} WCP mean:  {nk_mean:.4f}")

    return result


# ===================================================================
# ED6: EWP sanity check
# ===================================================================
def run_ed6(preferred, null_runs):
    """Diagnostic: full EWP vs null EWP; flag if full EWP high but WCU/SLR pass."""
    print("\n" + "-" * 70)
    print("ED6: EWP Sanity Check")
    print("-" * 70)

    full_ewps = []
    null_ewps = []

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        full_ewps.append(run.get('EWP', 0.0))
        null_ewps.append(get_null_mean(null_runs, 'N1', folio, 'EWP'))

    n = len(full_ewps)
    full_ewp_mean = sum(full_ewps) / n if n > 0 else 0.0
    null_ewp_mean = sum(null_ewps) / n if n > 0 else 0.0

    # Flag if full EWP > 5.0 (arbitrary threshold for "high")
    high_flag = full_ewp_mean > 5.0

    print(f"  Full EWP mean: {full_ewp_mean:.4f}")
    print(f"  Null EWP mean: {null_ewp_mean:.4f}")
    print(f"  High EWP flag: {high_flag}")

    return {
        'full_EWP_mean': round(full_ewp_mean, 6),
        'null_EWP_mean': round(null_ewp_mean, 6),
        'high_ewp_flag': high_flag,
        'n_folios': n,
    }


# ===================================================================
# ED7: Burden inversion test
# ===================================================================
def run_ed7(preferred, null_runs):
    """
    Diagnostic: does full SAHB > null SAHB BUT full UEB < null UEB?
    If yes, burden inversion is confirmed.
    """
    print("\n" + "-" * 70)
    print("ED7: Burden Inversion Test")
    print("-" * 70)

    full_sahbs = []
    full_uebs = []
    null_sahbs = []
    null_uebs = []

    for folio in PILOT_FOLIOS:
        run = preferred.get(folio)
        if run is None:
            continue
        full_sahbs.append(run.get('SAHB', 0.0))
        full_uebs.append(run.get('UEB', 0.0))

        # Average across N1-N4 for null
        null_sahb_vals = []
        null_ueb_vals = []
        for nk in ['N1', 'N2', 'N3', 'N4']:
            null_sahb_vals.append(get_null_mean(null_runs, nk, folio, 'SAHB'))
            null_ueb_vals.append(get_null_mean(null_runs, nk, folio, 'UEB'))
        null_sahbs.append(sum(null_sahb_vals) / len(null_sahb_vals))
        null_uebs.append(sum(null_ueb_vals) / len(null_ueb_vals))

    n = len(full_sahbs)
    full_sahb_mean = sum(full_sahbs) / n if n > 0 else 0.0
    full_ueb_mean = sum(full_uebs) / n if n > 0 else 0.0
    null_sahb_mean = sum(null_sahbs) / n if n > 0 else 0.0
    null_ueb_mean = sum(null_uebs) / n if n > 0 else 0.0

    full_sahb_gt_null = full_sahb_mean > null_sahb_mean
    full_ueb_lt_null = full_ueb_mean < null_ueb_mean
    inversion_confirmed = full_sahb_gt_null and full_ueb_lt_null

    print(f"  Full SAHB mean: {full_sahb_mean:.4f}")
    print(f"  Null SAHB mean: {null_sahb_mean:.4f}")
    print(f"  Full SAHB > Null SAHB: {full_sahb_gt_null}")
    print(f"  Full UEB mean:  {full_ueb_mean:.4f}")
    print(f"  Null UEB mean:  {null_ueb_mean:.4f}")
    print(f"  Full UEB < Null UEB:  {full_ueb_lt_null}")
    print(f"  Burden inversion confirmed: {inversion_confirmed}")

    return {
        'full_sahb_mean': round(full_sahb_mean, 6),
        'null_sahb_mean': round(null_sahb_mean, 6),
        'full_ueb_mean': round(full_ueb_mean, 6),
        'null_ueb_mean': round(null_ueb_mean, 6),
        'full_sahb_gt_null': full_sahb_gt_null,
        'full_ueb_lt_null': full_ueb_lt_null,
        'inversion_confirmed': inversion_confirmed,
        'n_folios': n,
    }


# ===================================================================
# Main
# ===================================================================
def main():
    t0 = time.time()
    print("=" * 70)
    print("T4: Controlled Excursion Validation Battery")
    print("Phase 568 - CONTROLLED_EXCURSION_METRICS")
    print("=" * 70)

    # =================================================================
    # Load inputs
    # =================================================================
    print("\n[1/5] Loading T1 results...")
    with open(T1_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    primary_runs = t1_data['primary_runs']
    print(f"  T1 folios: {len(primary_runs)}")

    print("[2/5] Loading T2 results...")
    with open(T2_PATH, 'r', encoding='utf-8') as f:
        t2_data = json.load(f)
    t2_reference = t2_data['reference']
    baseline_runs = t2_data['baseline_runs']
    null_runs = t2_data['null_runs']
    preferred_profiles = t2_data['metadata']['preferred_profiles']
    print(f"  T2 reference folios: {len(t2_reference)}")
    print(f"  T2 baselines: {sorted(baseline_runs.keys())}")
    print(f"  T2 nulls: {sorted(null_runs.keys())}")

    print("[3/5] Loading T3 results...")
    t3_data = None
    if T3_PATH.exists():
        with open(T3_PATH, 'r', encoding='utf-8') as f:
            t3_data = json.load(f)
        print(f"  T3 loaded: {sorted(t3_data.keys())}")
    else:
        print(f"  T3 file not found: {T3_PATH}")
        print("  EP7 (COF variant test) will be skipped.")

    print("[4/5] Loading line packets (P2 anchor)...")
    with open(LINE_PACKETS_PATH, 'r', encoding='utf-8') as f:
        lp_data = json.load(f)
    line_packets = lp_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    print("[5/5] Loading t2b token signals (P2 anchor)...")
    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    t2b_tokens = t2b_data['token_signals']
    print(f"  Token signals: {len(t2b_tokens)}")

    # =================================================================
    # Build preferred-profile run data from T1 (for display/context)
    # =================================================================
    print("\nBuilding preferred-profile runs from T1...")
    t1_preferred = get_preferred_runs(primary_runs, preferred_profiles)
    print(f"  T1 preferred runs: {len(t1_preferred)} folios")
    for fo in PILOT_FOLIOS:
        prof = preferred_profiles.get(fo, '?')
        has = fo in t1_preferred
        print(f"    {fo:<8} -> {prof:<28} {'OK' if has else 'MISSING'}")

    # =================================================================
    # Use T2 REFERENCE as the "full" comparison baseline for EP tests
    # (T2 reference and null use identical metric implementations,
    # ensuring fair comparison. T1 uses a different implementation for
    # some metrics like SLR, WCP, EWP, UEB.)
    # =================================================================
    print("\nUsing T2 reference runs as 'full' baseline for EP tests...")
    preferred = dict(t2_reference)
    print(f"  T2 reference runs: {len(preferred)} folios")

    # =================================================================
    # P2: Line Packet Shape Recovery (anchor test)
    # =================================================================
    p2 = run_p2(line_packets, t2b_tokens)

    # =================================================================
    # EP tests
    # =================================================================
    print("\n" + "=" * 70)
    print("EXCURSION-PRECISION TESTS (EP1-EP7)")
    print("=" * 70)

    ep1 = run_ep1(preferred, null_runs)
    ep2 = run_ep2(preferred, null_runs)
    ep3 = run_ep3(preferred, null_runs)
    ep4 = run_ep4(preferred, null_runs)
    ep5 = run_ep5(preferred, baseline_runs)
    ep6 = run_ep6(preferred, null_runs)
    ep7 = run_ep7(t3_data)

    # =================================================================
    # Diagnostics (ED1-ED7)
    # =================================================================
    print("\n" + "=" * 70)
    print("DIAGNOSTICS (ED1-ED7)")
    print("=" * 70)

    ed1 = run_ed1(preferred)
    ed2 = run_ed2(preferred, null_runs)
    ed3 = run_ed3(preferred, null_runs)
    ed4 = run_ed4(preferred)
    ed5 = run_ed5(preferred, null_runs)
    ed6 = run_ed6(preferred, null_runs)
    ed7 = run_ed7(preferred, null_runs)

    # =================================================================
    # Score summary
    # =================================================================
    ep_tests = {
        'EP1': ep1, 'EP2': ep2, 'EP3': ep3, 'EP4': ep4,
        'EP5': ep5, 'EP6': ep6, 'EP7': ep7,
    }

    ep_pass_count = sum(1 for ep in ep_tests.values() if ep['result'] == 'PASS')

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"\n  P2 (anchor):  {p2['result']}  ({p2['n_significant']}/7 SVs significant)")
    print()
    for name, ep in ep_tests.items():
        hard_soft = "(SOFT)" if name in ('EP4', 'EP7') else "(HARD)"
        print(f"  {name} {hard_soft:<7}: {ep['result']}")
    print(f"\n  EP pass count: {ep_pass_count}/7")

    # =================================================================
    # Assemble output
    # =================================================================
    elapsed = round(time.time() - t0, 2)

    output = {
        'metadata': {
            'phase': 568,
            'script': 't4_controlled_excursion_validation.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': elapsed,
            'n_pilot_folios': N_PILOT,
            'pilot_folios': PILOT_FOLIOS,
            'preferred_profiles': preferred_profiles,
            'inputs': {
                't1': str(T1_PATH),
                't2': str(T2_PATH),
                't3': str(T3_PATH) if t3_data else None,
                'line_packets': str(LINE_PACKETS_PATH),
                't2b': str(T2B_PATH),
            },
        },
        'P2': p2,
        'EP_tests': ep_tests,
        'diagnostics': {
            'ED1': ed1,
            'ED2': ed2,
            'ED3': ed3,
            'ED4': ed4,
            'ED5': ed5,
            'ED6': ed6,
            'ED7': ed7,
        },
        'score_summary': {
            'P2': p2['result'],
            'EP_pass_count': ep_pass_count,
            'EP_total': 7,
            'EP_results': {name: ep['result'] for name, ep in ep_tests.items()},
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"\n  Output: {OUTPUT_PATH}")
    print(f"  Size: {file_size_kb:.1f} KB")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"\n  Done.")


if __name__ == '__main__':
    main()

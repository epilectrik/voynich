"""
T4: Event Validation Battery
==============================
Phase 569 - EVENTIVE_CLOSURE_PACKETS

Computes P2 anchor test, PT1-PT5 primary tests, and D1-D8 diagnostics.
Uses frozen event-type priority order from shared_metrics.

Inputs:
  - t1_event_taxonomy.json       (event map, thresholds)
  - t2_event_runs.json           (60 primary + 30 ablation)
  - t3_event_null_runs.json      (reference + baselines + nulls)
  - t3_line_packets.json         (from SECTION_TEMPLATE_TRACE_EXECUTOR, for P2)
  - t2b_supervisory_interface_unrouted.json (from VIRTUAL_APPARATUS_COUPLING, for P2)

Output:
  - t4_event_validation.json
"""

import sys
import os
import json
import math
import time
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASES_BASE = os.path.dirname(BASE)
PROJECT_ROOT = os.path.dirname(PHASES_BASE)

RESULTS_DIR = os.path.join(BASE, 'results')
OUTPUT_PATH = os.path.join(RESULTS_DIR, 't4_event_validation.json')

LINE_PACKETS_PATH = os.path.join(PHASES_BASE, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                                  'results', 't3_line_packets.json')
T2B_PATH = os.path.join(PHASES_BASE, 'VIRTUAL_APPARATUS_COUPLING',
                         'results', 't2b_supervisory_interface_unrouted.json')

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STATE_VARS = ['T', 'RC', 'S', 'C', 'TR', 'X', 'Y']
N_SVS = len(STATE_VARS)

PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]

EVENT_TYPE_PRIORITY = [
    'E_decisive',
    'E_opaque_decisive',
    'E_compound',
    'E_mcb',
    'E_cts50',
    'E_opaque',
    'E_armed',
    'E_any',
]

# Folios with 0 CLOSE lines (excluded from Tier 1)
ZERO_CLOSE_FOLIOS = {'f40v', 'f81v'}

R = 6  # decimal rounding


# ===========================================================================
# Statistical helpers
# ===========================================================================
def _normal_cdf(x):
    """Approximation of the standard normal CDF."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = d * math.exp(-x * x / 2.0) * (
        t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 +
        t * (-1.821255978 + t * 1.330274429))))
    )
    return 1.0 - p if x >= 0 else p


def _rank(values):
    """Assign ranks with averaging for ties."""
    n = len(values)
    indexed = sorted(enumerate(values), key=lambda x: x[1])
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
    """Cohen's d between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    m1, m2 = sum(group1) / n1, sum(group2) / n2
    var1 = sum((x - m1) ** 2 for x in group1) / (n1 - 1)
    var2 = sum((x - m2) ** 2 for x in group2) / (n2 - 1)
    pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-10:
        return 0.0
    return (m1 - m2) / pooled_std


def paired_cohens_d(vals1, vals2):
    """Cohen's d for paired samples (same folios)."""
    diffs = [a - b for a, b in zip(vals1, vals2)]
    n = len(diffs)
    if n < 2:
        return 0.0
    m = sum(diffs) / n
    var = sum((d - m) ** 2 for d in diffs) / (n - 1)
    sd = math.sqrt(var)
    if sd < 1e-10:
        return 0.0
    return m / sd


# ===========================================================================
# Data loading
# ===========================================================================
def load_all_data():
    """Load all input files."""
    print("Loading input data...")

    print("  [1/5] T1 event taxonomy...")
    with open(os.path.join(RESULTS_DIR, 't1_event_taxonomy.json'), 'r', encoding='utf-8') as f:
        t1 = json.load(f)
    print(f"    Event map entries: {len(t1.get('event_map', {}))}")

    print("  [2/5] T2 event runs...")
    with open(os.path.join(RESULTS_DIR, 't2_event_runs.json'), 'r', encoding='utf-8') as f:
        t2 = json.load(f)
    print(f"    Primary runs: {t2['metadata']['n_primary_runs']}")
    print(f"    Ablation runs: {t2['metadata']['n_ablation_runs']}")

    print("  [3/5] T3 event null runs...")
    with open(os.path.join(RESULTS_DIR, 't3_event_null_runs.json'), 'r', encoding='utf-8') as f:
        t3 = json.load(f)
    print(f"    Baselines: {sorted(t3['baselines'].keys())}")
    print(f"    Nulls: {sorted(t3['nulls'].keys())}")

    print("  [4/5] Line packets (P2 anchor)...")
    with open(LINE_PACKETS_PATH, 'r', encoding='utf-8') as f:
        lp_raw = json.load(f)
    line_packets = lp_raw['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    print("  [5/5] T2b token signals (P2 anchor)...")
    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_raw = json.load(f)
    t2b_tokens = t2b_raw['token_signals']
    print(f"    Token signals: {len(t2b_tokens)}")

    return t1, t2, t3, line_packets, t2b_tokens


def extract_preferred_runs(t2):
    """Extract preferred-profile runs from T2 for each pilot folio."""
    preferred_profiles = t2['metadata']['preferred_profiles']
    t2_preferred = {}
    for folio in PILOT_FOLIOS:
        prof = preferred_profiles.get(folio, 'A1_BATH_REFLUX')
        key = f"{folio}|{prof}"
        if key in t2['primary_runs']:
            t2_preferred[folio] = t2['primary_runs'][key]
    return t2_preferred, preferred_profiles


# ===========================================================================
# P2: Line Packet Shape Recovery (ANCHOR)
# ===========================================================================
def run_p2(line_packets, t2b_tokens):
    """
    For each line, sum token contributions per SV.
    For each SV, Spearman-correlate per-line contribution sum with
    per-line packet profile[sv_idx].
    PASS if >= 5/7 SVs have p < 0.05.
    """
    print("\n" + "=" * 70)
    print("P2: Line Packet Shape Recovery (anchor)")
    print("=" * 70)

    # Build per-line contribution sums
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

    # Match line keys
    packet_keys = set(line_packets.keys())
    contrib_keys = set(line_contrib_sums.keys())
    matched_keys = sorted(packet_keys & contrib_keys)

    print(f"  Lines in packets: {len(packet_keys)}")
    print(f"  Lines with contributions: {len(contrib_keys)}")
    print(f"  Matched lines: {len(matched_keys)}")

    if len(matched_keys) < 10:
        print("  WARNING: too few matched lines for reliable correlation")

    per_sv = {}
    n_sig = 0

    for sv_idx, sv_name in enumerate(STATE_VARS):
        x_vals = []
        y_vals = []
        for key in matched_keys:
            x_vals.append(line_contrib_sums[key][sv_idx])
            profile = line_packets[key]['profile']
            if sv_idx < len(profile):
                y_vals.append(profile[sv_idx])
            else:
                y_vals.append(0.0)

        rs, p_val = spearman_r(x_vals, y_vals)
        sig = p_val < 0.05
        if sig:
            n_sig += 1

        per_sv[sv_name] = {
            'rho': round(rs, R),
            'p': round(p_val, R),
            'significant': sig,
            'n_lines': len(x_vals),
        }
        tag = "***" if sig else "   "
        print(f"  {sv_name:<3}: rho={rs:+.4f}  p={p_val:.6f}  n={len(x_vals)} {tag}")

    result = "PASS" if n_sig >= 5 else "FAIL"
    print(f"\n  P2 result: {result} ({n_sig}/7 significant, gate=5)")

    return {
        'result': result,
        'n_significant': n_sig,
        'gate': 5,
        'n_matched_lines': len(matched_keys),
        'per_sv': per_sv,
    }


# ===========================================================================
# Priority event type selection
# ===========================================================================
def select_priority_type(t2_preferred, min_tier2_folios=10):
    """Select highest-priority event type with >= min_tier2_folios at Tier 2."""
    for etype in EVENT_TYPE_PRIORITY:
        tier2_count = 0
        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            evt = run.get('events_by_type', {}).get(etype, {})
            if evt.get('count', 0) >= 3:
                tier2_count += 1
        if tier2_count >= min_tier2_folios:
            return etype, tier2_count
    # Fallback
    return 'E_any', 20


def get_tier1_folios():
    """Return Tier 1 folios: those with >= 1 CLOSE line (exclude f40v, f81v)."""
    return [f for f in PILOT_FOLIOS if f not in ZERO_CLOSE_FOLIOS]


# ===========================================================================
# Null event metric extraction
# ===========================================================================
def get_null_mean_event_metrics(t3, folio, etype):
    """Get mean event metrics for folio/etype across N1-N4 nulls (phase-native)."""
    erm_vals, esq_vals, ew_vals = [], [], []
    for ntype in ['N1', 'N2', 'N3', 'N4']:
        nm = t3['nulls'][ntype]['mean'].get(folio, {})
        # Use phase-native event scoring
        evt_key = 'events_by_type_phase_native'
        if evt_key not in nm:
            evt_key = 'events_by_type'
        evt = nm.get(evt_key, {}).get(etype, {})
        if evt:
            erm_vals.append(evt.get('mean_ERM', 0.0))
            esq_vals.append(evt.get('mean_ESQ', 0.0))
            ew_vals.append(evt.get('mean_EW', 1.0))
    if not erm_vals:
        return None
    return {
        'ERM': sum(erm_vals) / len(erm_vals),
        'ESQ': sum(esq_vals) / len(esq_vals),
        'EW': sum(ew_vals) / len(ew_vals),
    }


def get_null_mean_metric(t3, folio, metric_key):
    """Get mean of a top-level metric across N1-N4 nulls."""
    vals = []
    for ntype in ['N1', 'N2', 'N3', 'N4']:
        nm = t3['nulls'][ntype]['mean'].get(folio, {})
        m = nm.get('metrics', {})
        if metric_key in m:
            vals.append(m[metric_key])
    if not vals:
        return None
    return sum(vals) / len(vals)


# ===========================================================================
# PT3: Anchor Stability (checked FIRST)
# ===========================================================================
def run_pt3(t2_preferred, t3):
    """
    UEB: full < mean(N1-N4) UEB for >= 14/20 folios
    WCP: full > N1 WCP for >= 14/20 folios
    """
    print("\n" + "-" * 70)
    print("PT3: Anchor Stability (UEB + WCP from Phase 568)")
    print("-" * 70)

    per_folio = {}
    ueb_pass_count = 0
    wcp_pass_count = 0

    for folio in PILOT_FOLIOS:
        run = t2_preferred.get(folio)
        if run is None:
            per_folio[folio] = {'ueb_pass': False, 'wcp_pass': False, 'reason': 'missing'}
            continue

        full_ueb = run['metrics']['UEB']
        full_wcp = run['metrics']['WCP']

        # Mean null UEB across N1-N4
        null_uebs = []
        for ntype in ['N1', 'N2', 'N3', 'N4']:
            nm = t3['nulls'][ntype]['mean'].get(folio, {})
            null_uebs.append(nm.get('metrics', {}).get('UEB', 0.0))
        null_mean_ueb = sum(null_uebs) / len(null_uebs) if null_uebs else 0.0

        # N1 mean WCP
        n1_mean_wcp = t3['nulls']['N1']['mean'].get(folio, {}).get('metrics', {}).get('WCP', 0.0)

        ueb_ok = full_ueb < null_mean_ueb
        wcp_ok = full_wcp > n1_mean_wcp

        if ueb_ok:
            ueb_pass_count += 1
        if wcp_ok:
            wcp_pass_count += 1

        per_folio[folio] = {
            'full_UEB': round(full_ueb, R),
            'null_mean_UEB': round(null_mean_ueb, R),
            'ueb_pass': ueb_ok,
            'full_WCP': round(full_wcp, R),
            'N1_mean_WCP': round(n1_mean_wcp, R),
            'wcp_pass': wcp_ok,
        }

        tag_u = "ok" if ueb_ok else "FAIL"
        tag_w = "ok" if wcp_ok else "FAIL"
        print(f"  {folio:<8} UEB: {full_ueb:.4f} vs {null_mean_ueb:.4f} [{tag_u}]  "
              f"WCP: {full_wcp:.4f} vs {n1_mean_wcp:.4f} [{tag_w}]")

    ueb_gate = ueb_pass_count >= 14
    wcp_gate = wcp_pass_count >= 14
    result = "PASS" if (ueb_gate and wcp_gate) else "FAIL"

    print(f"\n  PT3 result: {result}  UEB: {ueb_pass_count}/20 (gate=14)  "
          f"WCP: {wcp_pass_count}/20 (gate=14)")

    return {
        'result': result,
        'ueb_pass': ueb_pass_count,
        'ueb_gate': 14,
        'wcp_pass': wcp_pass_count,
        'wcp_gate': 14,
        'per_folio': per_folio,
    }


# ===========================================================================
# PT1: Per-Folio Event Metric Dominance (HARD)
# ===========================================================================
def run_pt1(t2_preferred, t3, priority_type, tier1_folios):
    """
    For Tier 1 folios with events of the priority type:
    full beats nulls on >= 2 of 3 continuous metrics (ERM, ESQ, 1-EW).
    PASS if >= 12 folios show dominance.
    """
    print("\n" + "-" * 70)
    print(f"PT1: Per-Folio Event Metric Dominance [{priority_type}]")
    print("-" * 70)

    per_folio = {}
    n_pass = 0
    n_eligible = 0

    for folio in tier1_folios:
        run = t2_preferred.get(folio)
        if run is None:
            per_folio[folio] = {'pass': False, 'reason': 'missing_run'}
            continue

        full_evt = run.get('events_by_type', {}).get(priority_type, {})
        if full_evt.get('count', 0) == 0:
            per_folio[folio] = {'pass': False, 'reason': 'no_events'}
            continue

        null_mean = get_null_mean_event_metrics(t3, folio, priority_type)
        if null_mean is None:
            per_folio[folio] = {'pass': False, 'reason': 'no_null_data'}
            continue

        n_eligible += 1

        full_erm = full_evt.get('mean_ERM', 0.0)
        full_esq = full_evt.get('mean_ESQ', 0.0)
        full_1mew = 1.0 - full_evt.get('mean_EW', 1.0)

        null_erm = null_mean['ERM']
        null_esq = null_mean['ESQ']
        null_1mew = 1.0 - null_mean['EW']

        n_dominated = 0
        if full_erm > null_erm:
            n_dominated += 1
        if full_esq > null_esq:
            n_dominated += 1
        if full_1mew > null_1mew:
            n_dominated += 1

        folio_pass = n_dominated >= 2
        if folio_pass:
            n_pass += 1

        per_folio[folio] = {
            'full_ERM': round(full_erm, R),
            'null_ERM': round(null_erm, R),
            'full_ESQ': round(full_esq, R),
            'null_ESQ': round(null_esq, R),
            'full_1mEW': round(full_1mew, R),
            'null_1mEW': round(null_1mew, R),
            'n_dominated': n_dominated,
            'pass': folio_pass,
        }

        tag = "PASS" if folio_pass else "fail"
        print(f"  {folio:<8} ERM:{full_erm:.4f}>{null_erm:.4f}  "
              f"ESQ:{full_esq:.4f}>{null_esq:.4f}  "
              f"1-EW:{full_1mew:.2f}>{null_1mew:.2f}  dom={n_dominated} [{tag}]")

    result = "PASS" if n_pass >= 12 else "FAIL"
    print(f"\n  PT1 result: {result}  {n_pass}/{n_eligible} tier1 folios dominate (gate=12)")

    return {
        'result': result,
        'n_pass': n_pass,
        'gate': 12,
        'n_tier1': len(tier1_folios),
        'n_eligible': n_eligible,
        'event_type': priority_type,
        'per_folio': per_folio,
    }


# ===========================================================================
# PT2: B10 Event Sensitivity (HARD)
# ===========================================================================
def run_pt2(t2_preferred, t3, priority_type, tier1_folios):
    """
    Full ERM vs B10 ERM for priority event type. Cohen's d > 0.35.
    """
    print("\n" + "-" * 70)
    print(f"PT2: B10 Event Sensitivity [{priority_type}]")
    print("-" * 70)

    b10_data = t3['baselines']['B10']

    full_erms = []
    b10_erms = []
    folio_details = []

    for folio in tier1_folios:
        run = t2_preferred.get(folio)
        if run is None:
            continue
        full_evt = run.get('events_by_type', {}).get(priority_type, {})
        b10_run = b10_data.get(folio, {})
        b10_evt = b10_run.get('events_by_type', {}).get(priority_type, {})

        if (full_evt.get('count', 0) > 0 and b10_evt.get('count', 0) > 0):
            full_erms.append(full_evt['mean_ERM'])
            b10_erms.append(b10_evt['mean_ERM'])
            folio_details.append({
                'folio': folio,
                'full_ERM': round(full_evt['mean_ERM'], R),
                'B10_ERM': round(b10_evt['mean_ERM'], R),
            })
            print(f"  {folio:<8} full_ERM={full_evt['mean_ERM']:.4f}  "
                  f"B10_ERM={b10_evt['mean_ERM']:.4f}")

    d = paired_cohens_d(full_erms, b10_erms) if full_erms else 0.0
    result = "PASS" if d > 0.35 else "FAIL"

    full_mean = sum(full_erms) / len(full_erms) if full_erms else 0.0
    b10_mean = sum(b10_erms) / len(b10_erms) if b10_erms else 0.0

    print(f"\n  PT2 result: {result}  d={d:.4f} (gate=0.35)  "
          f"n={len(full_erms)}  full_mean={full_mean:.4f}  b10_mean={b10_mean:.4f}")

    return {
        'result': result,
        'cohens_d': round(d, R),
        'gate': 0.35,
        'event_type': priority_type,
        'n_folios_compared': len(full_erms),
        'full_mean_ERM': round(full_mean, R),
        'b10_mean_ERM': round(b10_mean, R),
        'per_folio': folio_details,
    }


# ===========================================================================
# PT4: Multi-Type Discrimination (SOFT)
# ===========================================================================
def run_pt4(t2_preferred, t3):
    """
    At least 2 event types independently show full ERM > null ERM with d > 0.20
    across Tier 2+ folios for that type.
    """
    print("\n" + "-" * 70)
    print("PT4: Multi-Type Discrimination")
    print("-" * 70)

    per_type = {}
    n_discriminating = 0

    for etype in EVENT_TYPE_PRIORITY:
        full_erms = []
        null_erms = []
        qualifying_folios = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            full_evt = run.get('events_by_type', {}).get(etype, {})
            if full_evt.get('count', 0) < 3:
                continue

            null_mean = get_null_mean_event_metrics(t3, folio, etype)
            if null_mean is None:
                continue

            full_erms.append(full_evt['mean_ERM'])
            null_erms.append(null_mean['ERM'])
            qualifying_folios.append(folio)

        d = 0.0
        passes = False
        if len(full_erms) >= 5:
            d = cohens_d(full_erms, null_erms)
            passes = d > 0.20

        if passes:
            n_discriminating += 1

        full_mean = sum(full_erms) / len(full_erms) if full_erms else 0.0
        null_mean_val = sum(null_erms) / len(null_erms) if null_erms else 0.0

        per_type[etype] = {
            'cohens_d': round(d, R),
            'n_folios': len(full_erms),
            'full_mean_ERM': round(full_mean, R),
            'null_mean_ERM': round(null_mean_val, R),
            'pass': passes,
        }

        tag = "PASS" if passes else "fail"
        print(f"  {etype:<22} d={d:+.4f}  n={len(full_erms):2d}  "
              f"full={full_mean:.4f}  null={null_mean_val:.4f}  [{tag}]")

    result = "PASS" if n_discriminating >= 2 else "FAIL"
    print(f"\n  PT4 result: {result}  {n_discriminating} types discriminating (gate=2)")

    return {
        'result': result,
        'n_types_discriminating': n_discriminating,
        'gate': 2,
        'per_type': per_type,
    }


# ===========================================================================
# PT5: Demand-Conditioned Advantage (SOFT)
# ===========================================================================
def run_pt5(t2_preferred, t3, priority_type):
    """
    For the priority event type, compare demand-conditioned (work_preceded) events
    in full model vs overall null ERM. Cohen's d > 0.25.

    Since N1-N4 nulls don't store events_by_demand, we compare
    full demand-conditioned ERM against null overall ERM for the same event type.
    """
    print("\n" + "-" * 70)
    print(f"PT5: Demand-Conditioned Advantage [{priority_type}]")
    print("-" * 70)

    # Determine which demand qualifier is available
    # T2 stores events_by_type_demand with keys like "E_decisive__work_preceded"
    demand_qualifier = 'work_preceded'
    demand_key = f"{priority_type}__{demand_qualifier}"

    full_erms = []
    null_erms = []
    folio_details = []

    for folio in PILOT_FOLIOS:
        run = t2_preferred.get(folio)
        if run is None:
            continue

        # Get demand-conditioned event data from T2
        etd = run.get('events_by_type_demand', {}).get(demand_key, {})
        if etd.get('count', 0) == 0:
            continue

        # Get null mean ERM (overall, not demand-conditioned)
        null_mean = get_null_mean_event_metrics(t3, folio, priority_type)
        if null_mean is None:
            continue

        full_erms.append(etd['mean_ERM'])
        null_erms.append(null_mean['ERM'])
        folio_details.append({
            'folio': folio,
            'full_demanded_ERM': round(etd['mean_ERM'], R),
            'null_overall_ERM': round(null_mean['ERM'], R),
            'demand_count': etd['count'],
        })
        print(f"  {folio:<8} demanded_ERM={etd['mean_ERM']:.4f}  "
              f"null_ERM={null_mean['ERM']:.4f}  n_events={etd['count']}")

    d = cohens_d(full_erms, null_erms) if len(full_erms) >= 2 else 0.0
    result = "PASS" if d > 0.25 else "FAIL"

    print(f"\n  PT5 result: {result}  d={d:.4f} (gate=0.25)  n_folios={len(full_erms)}")

    return {
        'result': result,
        'cohens_d': round(d, R),
        'gate': 0.25,
        'event_type': priority_type,
        'qualifier': demand_qualifier,
        'n_folios_compared': len(full_erms),
        'per_folio': folio_details,
    }


# ===========================================================================
# D1: Event Frequency by Model Type
# ===========================================================================
def run_d1(t2_preferred, t3):
    """Compare event counts per type between full model and null means."""
    print("\n" + "-" * 70)
    print("D1: Event Frequency by Model Type")
    print("-" * 70)

    per_type = {}
    for etype in EVENT_TYPE_PRIORITY:
        full_counts = []
        null_counts = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            full_evt = run.get('events_by_type', {}).get(etype, {})
            full_counts.append(full_evt.get('count', 0))

            # Null mean count (phase-native)
            null_count_vals = []
            for ntype in ['N1', 'N2', 'N3', 'N4']:
                nm = t3['nulls'][ntype]['mean'].get(folio, {})
                evt_key = 'events_by_type_phase_native'
                if evt_key not in nm:
                    evt_key = 'events_by_type'
                evt = nm.get(evt_key, {}).get(etype, {})
                null_count_vals.append(evt.get('count', 0))
            null_counts.append(sum(null_count_vals) / len(null_count_vals) if null_count_vals else 0)

        full_mean = sum(full_counts) / len(full_counts) if full_counts else 0
        null_mean = sum(null_counts) / len(null_counts) if null_counts else 0
        ratio = full_mean / null_mean if null_mean > 0.001 else float('inf')

        per_type[etype] = {
            'full_mean_count': round(full_mean, R),
            'null_mean_count': round(null_mean, R),
            'ratio': round(ratio, R) if ratio != float('inf') else 'inf',
        }
        print(f"  {etype:<22} full={full_mean:.2f}  null={null_mean:.2f}  ratio={ratio:.3f}")

    return per_type


# ===========================================================================
# D2: Event Success by Event Type
# ===========================================================================
def run_d2(t2_preferred, t3):
    """Per event type: full vs null EIR, ERM, ESQ, EW, Cohen's d."""
    print("\n" + "-" * 70)
    print("D2: Event Success by Event Type")
    print("-" * 70)

    per_type = {}
    for etype in EVENT_TYPE_PRIORITY:
        full_erms = []
        null_erms = []
        full_eirs = []
        null_eirs = []
        full_esqs = []
        null_esqs = []
        full_ews = []
        null_ews = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            full_evt = run.get('events_by_type', {}).get(etype, {})
            if full_evt.get('count', 0) == 0:
                continue

            null_mean = get_null_mean_event_metrics(t3, folio, etype)
            if null_mean is None:
                continue

            full_erms.append(full_evt.get('mean_ERM', 0.0))
            null_erms.append(null_mean['ERM'])
            full_eirs.append(full_evt.get('EIR', 0.0))
            null_eirs.append(0.0)  # placeholder
            full_esqs.append(full_evt.get('mean_ESQ', 0.0))
            null_esqs.append(null_mean['ESQ'])
            full_ews.append(full_evt.get('mean_EW', 1.0))
            null_ews.append(null_mean['EW'])

        d_erm = cohens_d(full_erms, null_erms) if len(full_erms) >= 2 else 0.0

        per_type[etype] = {
            'n_folios': len(full_erms),
            'full_mean_ERM': round(sum(full_erms) / len(full_erms), R) if full_erms else 0.0,
            'null_mean_ERM': round(sum(null_erms) / len(null_erms), R) if null_erms else 0.0,
            'full_mean_ESQ': round(sum(full_esqs) / len(full_esqs), R) if full_esqs else 0.0,
            'null_mean_ESQ': round(sum(null_esqs) / len(null_esqs), R) if null_esqs else 0.0,
            'full_mean_EW': round(sum(full_ews) / len(full_ews), R) if full_ews else 0.0,
            'null_mean_EW': round(sum(null_ews) / len(null_ews), R) if null_ews else 0.0,
            'cohens_d_ERM': round(d_erm, R),
        }
        print(f"  {etype:<22} n={len(full_erms):2d}  "
              f"d_ERM={d_erm:+.4f}  "
              f"full_ERM={per_type[etype]['full_mean_ERM']:.4f}  "
              f"null_ERM={per_type[etype]['null_mean_ERM']:.4f}")

    return per_type


# ===========================================================================
# D3: Folio Eligibility Map
# ===========================================================================
def run_d3(t2_preferred):
    """For each event type, show which folios are Tier 0/1/2/3."""
    print("\n" + "-" * 70)
    print("D3: Folio Eligibility Map")
    print("-" * 70)

    per_type = {}
    for etype in EVENT_TYPE_PRIORITY:
        folio_tiers = {}
        tier_counts = {0: 0, 1: 0, 2: 0, 3: 0}

        for folio in PILOT_FOLIOS:
            if folio in ZERO_CLOSE_FOLIOS:
                folio_tiers[folio] = 0
                tier_counts[0] += 1
                continue
            run = t2_preferred.get(folio)
            if run is None:
                folio_tiers[folio] = 0
                tier_counts[0] += 1
                continue
            evt = run.get('events_by_type', {}).get(etype, {})
            count = evt.get('count', 0)
            if count == 0:
                folio_tiers[folio] = 0
                tier_counts[0] += 1
            elif count < 3:
                folio_tiers[folio] = 1
                tier_counts[1] += 1
            elif count < 5:
                folio_tiers[folio] = 2
                tier_counts[2] += 1
            else:
                folio_tiers[folio] = 3
                tier_counts[3] += 1

        per_type[etype] = {
            'tier_counts': tier_counts,
            'per_folio': folio_tiers,
        }
        print(f"  {etype:<22} T0={tier_counts[0]:2d}  T1={tier_counts[1]:2d}  "
              f"T2={tier_counts[2]:2d}  T3={tier_counts[3]:2d}")

    return per_type


# ===========================================================================
# D4: B10 Event Cascade
# ===========================================================================
def run_d4(t2_preferred, t3):
    """Does B10 removal affect event frequency, success, or both?"""
    print("\n" + "-" * 70)
    print("D4: B10 Event Cascade")
    print("-" * 70)

    b10_data = t3['baselines']['B10']
    per_type = {}

    for etype in EVENT_TYPE_PRIORITY:
        full_counts = []
        b10_counts = []
        full_erms = []
        b10_erms = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            b10_run = b10_data.get(folio, {})
            if run is None:
                continue

            full_evt = run.get('events_by_type', {}).get(etype, {})
            b10_evt = b10_run.get('events_by_type', {}).get(etype, {})

            full_counts.append(full_evt.get('count', 0))
            b10_counts.append(b10_evt.get('count', 0))

            if full_evt.get('count', 0) > 0 and b10_evt.get('count', 0) > 0:
                full_erms.append(full_evt['mean_ERM'])
                b10_erms.append(b10_evt['mean_ERM'])

        full_mean_count = sum(full_counts) / len(full_counts) if full_counts else 0
        b10_mean_count = sum(b10_counts) / len(b10_counts) if b10_counts else 0
        d_erm = paired_cohens_d(full_erms, b10_erms) if len(full_erms) >= 2 else 0.0
        full_mean_erm = sum(full_erms) / len(full_erms) if full_erms else 0.0
        b10_mean_erm = sum(b10_erms) / len(b10_erms) if b10_erms else 0.0

        per_type[etype] = {
            'full_mean_count': round(full_mean_count, R),
            'b10_mean_count': round(b10_mean_count, R),
            'count_delta': round(full_mean_count - b10_mean_count, R),
            'full_mean_ERM': round(full_mean_erm, R),
            'b10_mean_ERM': round(b10_mean_erm, R),
            'cohens_d_ERM': round(d_erm, R),
            'n_paired': len(full_erms),
        }
        print(f"  {etype:<22} count: {full_mean_count:.1f}->{b10_mean_count:.1f}  "
              f"ERM d={d_erm:+.4f}  n_paired={len(full_erms)}")

    return per_type


# ===========================================================================
# D5: Comparison to 568 CCY
# ===========================================================================
def run_d5(t2_preferred, t3, priority_type):
    """Pearson r between per-folio ERM and CCY from T2."""
    print("\n" + "-" * 70)
    print(f"D5: ERM vs CCY Correlation [{priority_type}]")
    print("-" * 70)

    erm_vals = []
    ccy_vals = []
    folio_details = []

    for folio in PILOT_FOLIOS:
        run = t2_preferred.get(folio)
        if run is None:
            continue
        full_evt = run.get('events_by_type', {}).get(priority_type, {})
        if full_evt.get('count', 0) == 0:
            continue
        ccy = run.get('metrics', {}).get('CCY', 0.0)

        erm_vals.append(full_evt['mean_ERM'])
        ccy_vals.append(ccy)
        folio_details.append({
            'folio': folio,
            'ERM': round(full_evt['mean_ERM'], R),
            'CCY': round(ccy, R),
        })

    r_val = pearson_r(erm_vals, ccy_vals) if len(erm_vals) >= 3 else 0.0
    print(f"  Pearson r(ERM, CCY) = {r_val:.4f}  n={len(erm_vals)}")

    return {
        'pearson_r': round(r_val, R),
        'n_folios': len(erm_vals),
        'event_type': priority_type,
        'per_folio': folio_details,
    }


# ===========================================================================
# D6: Threshold Regime Comparison
# ===========================================================================
def run_d6(t2_preferred, t3, t1):
    """
    Compare global vs section-normalized event types.
    Since T2 stores events_by_type using global types and per_event_detail has
    packet_types_section, we aggregate from per_event_detail for section regime.
    """
    print("\n" + "-" * 70)
    print("D6: Threshold Regime Comparison")
    print("-" * 70)

    # Aggregate section-normalized event data from per_event_detail
    # per_event_detail has packet_types_section for each event
    per_type_global = {}
    per_type_section = {}

    for etype in EVENT_TYPE_PRIORITY:
        global_erms = []
        section_erms = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue

            # Global (from events_by_type)
            full_evt = run.get('events_by_type', {}).get(etype, {})
            if full_evt.get('count', 0) > 0:
                global_erms.append(full_evt['mean_ERM'])

            # Section-normalized: aggregate from per_event_detail
            ped = run.get('per_event_detail', [])
            section_erms_folio = []
            for evt in ped:
                if etype in evt.get('packet_types_section', []):
                    section_erms_folio.append(evt.get('ERM', 0.0))
            if section_erms_folio:
                section_erms.append(sum(section_erms_folio) / len(section_erms_folio))

        global_mean = sum(global_erms) / len(global_erms) if global_erms else 0.0
        section_mean = sum(section_erms) / len(section_erms) if section_erms else 0.0

        per_type_global[etype] = {
            'mean_ERM': round(global_mean, R),
            'n_folios': len(global_erms),
        }
        per_type_section[etype] = {
            'mean_ERM': round(section_mean, R),
            'n_folios': len(section_erms),
        }

        print(f"  {etype:<22} global_ERM={global_mean:.4f} (n={len(global_erms):2d})  "
              f"section_ERM={section_mean:.4f} (n={len(section_erms):2d})")

    return {
        'global': per_type_global,
        'section_normalized': per_type_section,
        'note': 'Section-normalized aggregated from per_event_detail.packet_types_section',
    }


# ===========================================================================
# D7: Phase-native vs Structure-native Scoring
# ===========================================================================
def run_d7(t3, priority_type):
    """
    For N1 (phase-shuffle), compare discrimination under both regimes.
    """
    print("\n" + "-" * 70)
    print(f"D7: Phase-native vs Structure-native Scoring [{priority_type}]")
    print("-" * 70)

    per_folio = {}

    for folio in PILOT_FOLIOS:
        n1_mean = t3['nulls']['N1']['mean'].get(folio, {})

        pn = n1_mean.get('events_by_type_phase_native', {}).get(priority_type, {})
        sn = n1_mean.get('events_by_type_structure_native', {}).get(priority_type, {})

        pn_erm = pn.get('mean_ERM', 0.0)
        pn_count = pn.get('count', 0)
        sn_erm = sn.get('mean_ERM', 0.0)
        sn_count = sn.get('count', 0)

        per_folio[folio] = {
            'phase_native_ERM': round(pn_erm, R),
            'phase_native_count': round(pn_count, R),
            'structure_native_ERM': round(sn_erm, R),
            'structure_native_count': round(sn_count, R),
        }
        print(f"  {folio:<8} PN: ERM={pn_erm:.4f} count={pn_count:.1f}  "
              f"SN: ERM={sn_erm:.4f} count={sn_count:.1f}")

    # Aggregate comparison
    pn_erms = [v['phase_native_ERM'] for v in per_folio.values() if v['phase_native_count'] > 0]
    sn_erms = [v['structure_native_ERM'] for v in per_folio.values() if v['structure_native_count'] > 0]

    pn_mean = sum(pn_erms) / len(pn_erms) if pn_erms else 0.0
    sn_mean = sum(sn_erms) / len(sn_erms) if sn_erms else 0.0

    print(f"\n  Aggregate: PN mean ERM={pn_mean:.4f} (n={len(pn_erms)})  "
          f"SN mean ERM={sn_mean:.4f} (n={len(sn_erms)})")

    return {
        'event_type': priority_type,
        'phase_native_mean_ERM': round(pn_mean, R),
        'structure_native_mean_ERM': round(sn_mean, R),
        'n_phase_native': len(pn_erms),
        'n_structure_native': len(sn_erms),
        'per_folio': per_folio,
    }


# ===========================================================================
# D8: Demand Qualifier Analysis
# ===========================================================================
def run_d8(t2_preferred):
    """Break down event success by demand qualifier from T2 events_by_demand."""
    print("\n" + "-" * 70)
    print("D8: Demand Qualifier Analysis")
    print("-" * 70)

    # Collect all demand qualifiers across folios
    all_qualifiers = set()
    for folio in PILOT_FOLIOS:
        run = t2_preferred.get(folio)
        if run is None:
            continue
        ebd = run.get('events_by_demand', {})
        all_qualifiers.update(ebd.keys())

    per_qualifier = {}
    for qual in sorted(all_qualifiers):
        erms = []
        esqs = []
        ews = []
        counts = []

        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            ebd = run.get('events_by_demand', {}).get(qual, {})
            if ebd.get('count', 0) > 0:
                erms.append(ebd.get('mean_ERM', 0.0))
                esqs.append(ebd.get('mean_ESQ', 0.0))
                ews.append(ebd.get('mean_EW', 1.0))
                counts.append(ebd['count'])

        mean_erm = sum(erms) / len(erms) if erms else 0.0
        mean_esq = sum(esqs) / len(esqs) if esqs else 0.0
        mean_ew = sum(ews) / len(ews) if ews else 0.0
        total_count = sum(counts)

        per_qualifier[qual] = {
            'n_folios': len(erms),
            'total_events': total_count,
            'mean_ERM': round(mean_erm, R),
            'mean_ESQ': round(mean_esq, R),
            'mean_EW': round(mean_ew, R),
        }
        print(f"  {qual:<20} n_folios={len(erms):2d}  total={total_count:3d}  "
              f"ERM={mean_erm:.4f}  ESQ={mean_esq:.4f}  EW={mean_ew:.3f}")

    # Also show events_by_type_demand breakdown
    type_demand = {}
    all_td_keys = set()
    for folio in PILOT_FOLIOS:
        run = t2_preferred.get(folio)
        if run is None:
            continue
        all_td_keys.update(run.get('events_by_type_demand', {}).keys())

    for td_key in sorted(all_td_keys):
        erms = []
        counts = []
        for folio in PILOT_FOLIOS:
            run = t2_preferred.get(folio)
            if run is None:
                continue
            etd = run.get('events_by_type_demand', {}).get(td_key, {})
            if etd.get('count', 0) > 0:
                erms.append(etd.get('mean_ERM', 0.0))
                counts.append(etd['count'])

        mean_erm = sum(erms) / len(erms) if erms else 0.0
        type_demand[td_key] = {
            'n_folios': len(erms),
            'total_events': sum(counts),
            'mean_ERM': round(mean_erm, R),
        }

    if not all_qualifiers:
        print("  (no demand-qualified events found)")

    return {
        'by_qualifier': per_qualifier,
        'by_type_demand': type_demand,
    }


# ===========================================================================
# Main
# ===========================================================================
def main():
    t_start = time.time()
    print("=" * 70)
    print("T4: Event Validation Battery (Phase 569)")
    print("=" * 70)

    # Load data
    t1, t2, t3, line_packets, t2b_tokens = load_all_data()

    # Extract preferred runs
    t2_preferred, preferred_profiles = extract_preferred_runs(t2)
    print(f"\nPreferred runs extracted: {len(t2_preferred)}/{len(PILOT_FOLIOS)} folios")
    for fo in PILOT_FOLIOS:
        prof = preferred_profiles.get(fo, '?')
        has = fo in t2_preferred
        print(f"  {fo:<8} -> {prof:<28} {'OK' if has else 'MISSING'}")

    # ===================================================================
    # P2: Line Packet Shape Recovery (ANCHOR)
    # ===================================================================
    p2 = run_p2(line_packets, t2b_tokens)

    # ===================================================================
    # PT3: Anchor Stability (CHECK FIRST)
    # ===================================================================
    pt3 = run_pt3(t2_preferred, t3)
    if pt3['result'] == 'FAIL':
        print("\n  *** WARNING: PT3 (Anchor Stability) FAILED ***")
        print("  *** UEB/WCP anchors from Phase 568 have regressed ***")

    # ===================================================================
    # Select priority event type
    # ===================================================================
    priority_type, priority_tier2_count = select_priority_type(t2_preferred)
    print(f"\nPriority event type: {priority_type} (Tier 2+ folios: {priority_tier2_count})")

    tier1_folios = get_tier1_folios()
    print(f"Tier 1 folios (>= 1 CLOSE line): {len(tier1_folios)}")

    # ===================================================================
    # PT1-PT2, PT4-PT5
    # ===================================================================
    pt1 = run_pt1(t2_preferred, t3, priority_type, tier1_folios)
    pt2 = run_pt2(t2_preferred, t3, priority_type, tier1_folios)
    pt4 = run_pt4(t2_preferred, t3)
    pt5 = run_pt5(t2_preferred, t3, priority_type)

    # ===================================================================
    # Diagnostics D1-D8
    # ===================================================================
    print("\n" + "=" * 70)
    print("DIAGNOSTICS (D1-D8)")
    print("=" * 70)

    d1 = run_d1(t2_preferred, t3)
    d2 = run_d2(t2_preferred, t3)
    d3 = run_d3(t2_preferred)
    d4 = run_d4(t2_preferred, t3)
    d5 = run_d5(t2_preferred, t3, priority_type)
    d6 = run_d6(t2_preferred, t3, t1)
    d7 = run_d7(t3, priority_type)
    d8 = run_d8(t2_preferred)

    # ===================================================================
    # Score summary
    # ===================================================================
    pt_results = {
        'PT1': pt1['result'],
        'PT2': pt2['result'],
        'PT3': pt3['result'],
        'PT4': pt4['result'],
        'PT5': pt5['result'],
    }
    pt_pass_count = sum(1 for v in pt_results.values() if v == 'PASS')
    tests_passed = [k for k, v in pt_results.items() if v == 'PASS']

    score_summary = {
        'P2': p2['result'],
        'PT_pass_count': pt_pass_count,
        'PT_results': pt_results,
        'tests_passed': tests_passed,
    }

    # ===================================================================
    # Print summary
    # ===================================================================
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  P2 (anchor):     {p2['result']}  ({p2['n_significant']}/7 SVs significant)")
    print(f"  PT3 (stability): {pt3['result']}  UEB={pt3['ueb_pass']}/20  WCP={pt3['wcp_pass']}/20")
    print(f"  PT1 (dominance): {pt1['result']}  {pt1['n_pass']}/{pt1.get('n_eligible', '?')} folios (gate=12)")
    print(f"  PT2 (B10 sens):  {pt2['result']}  d={pt2['cohens_d']:.4f} (gate=0.35)")
    print(f"  PT4 (multi-type): {pt4['result']}  {pt4['n_types_discriminating']} types (gate=2)")
    print(f"  PT5 (demand):    {pt5['result']}  d={pt5['cohens_d']:.4f} (gate=0.25)")
    print(f"\n  Priority event type: {priority_type}")
    print(f"  PT pass count: {pt_pass_count}/5")
    print(f"  Tests passed: {tests_passed}")

    # ===================================================================
    # Build output
    # ===================================================================
    output = {
        'metadata': {
            'phase': 569,
            'script': 't4_event_validation.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pilot_folios': PILOT_FOLIOS,
            'priority_event_type': priority_type,
            'priority_tier2_count': priority_tier2_count,
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'P2': p2,
        'PT_tests': {
            'PT1': pt1,
            'PT2': pt2,
            'PT3': pt3,
            'PT4': pt4,
            'PT5': pt5,
        },
        'diagnostics': {
            'D1': d1,
            'D2': d2,
            'D3': d3,
            'D4': d4,
            'D5': d5,
            'D6': d6,
            'D7': d7,
            'D8': d8,
        },
        'score_summary': score_summary,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput written to: {OUTPUT_PATH}")
    print(f"Elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()

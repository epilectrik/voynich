"""
T4 Metric Computation - Phase 570b
===================================
Loads T2 (full model runs) and T3 (null runs) outputs and computes
the new metric family: TRA, nTRA, DRS, SCP, YGA, DBP
"""

import json
import math
import os
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, "results")
T2_PATH = os.path.join(RESULTS, "t2_full_model_runs.json")
T3_PATH = os.path.join(RESULTS, "t3_null_runs.json")
OUTPUT_PATH = os.path.join(RESULTS, "t4_metrics.json")

EQUILIBRIUM = 0.5
STATE_VARS = ["T", "RC", "S", "C", "TR", "X", "Y"]
PROCESS_SVS = ["T", "RC", "S", "C", "TR", "X"]
Y_IDX = 6
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}

Q1 = 0.08
Q2_BASE = {"T": 0.24, "RC": 0.28, "S": 0.24, "C": 0.24, "TR": 0.28, "X": 0.21, "Y": 0.35}
Q3_OFFSET = 0.05
HAZARD_DEV = {"T": 0.35, "RC": 0.40, "S": 0.35, "C": 0.35, "TR": 0.40, "X": 0.30, "Y": 1.0}


def aggregate_dev(state):
    return sum(abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS) / len(PROCESS_SVS)


def zone_quality(state, sv):
    i = SV_INDEX[sv]
    if sv == "S" and state[i] > EQUILIBRIUM:
        return 4
    dev = abs(state[i] - EQUILIBRIUM)
    q2 = Q2_BASE[sv]
    q3 = q2 + Q3_OFFSET
    haz = HAZARD_DEV[sv]
    if dev < Q1:
        return 4
    elif dev < q2:
        return 3
    elif dev < q3:
        return 2
    elif dev < haz:
        return 1
    else:
        return 0


def select_demanded_events(per_event_detail):
    wp = [e for e in per_event_detail if "work_preceded" in e.get("demand_qualifiers", [])]
    if len(wp) >= 2:
        return wp, "work_preceded"
    dem = [e for e in per_event_detail if "demanded" in e.get("demand_qualifiers", [])]
    if len(dem) >= 2:
        return dem, "demanded"
    return per_event_detail, "E_any"


def select_m4f_matched_events(perm, selection_tier):
    matched = perm["matched_events"]
    if selection_tier == "work_preceded":
        filt = [e for e in matched if "work_preceded" in e.get("demand_qualifiers", [])]
        if len(filt) >= 1:
            return filt
    elif selection_tier == "demanded":
        filt = [e for e in matched if "demanded" in e.get("demand_qualifiers", [])]
        if len(filt) >= 1:
            return filt
    return matched


def _abs_recovery(event):
    pre = aggregate_dev(event["close_pre_state"])
    end = aggregate_dev(event["line_end_state"])
    return pre - end


def compute_tra(m1_events, m4f_perms_matched_events):
    m1_recs = [_abs_recovery(e) for e in m1_events]
    m1_mean = sum(m1_recs) / len(m1_recs) if m1_recs else 0.0
    perm_means = []
    for pe in m4f_perms_matched_events:
        if pe:
            recs = [_abs_recovery(e) for e in pe]
            perm_means.append(sum(recs) / len(recs))
    m4f_mean = sum(perm_means) / len(perm_means) if perm_means else 0.0
    return {
        "TRA": round(m1_mean - m4f_mean, 8),
        "M1_mean_recovery": round(m1_mean, 8),
        "M4f_mean_recovery": round(m4f_mean, 8),
        "n_m1_events": len(m1_events),
        "n_perms": len(perm_means),
    }


def compute_ntra(m1_events, m4f_perms_matched_events):
    EPSILON = 0.001
    def norm_rec(event):
        pre = aggregate_dev(event["close_pre_state"])
        end = aggregate_dev(event["line_end_state"])
        return (pre - end) / max(pre, EPSILON)
    m1_norms = [norm_rec(e) for e in m1_events]
    m1_mean = sum(m1_norms) / len(m1_norms) if m1_norms else 0.0
    perm_means = []
    for pe in m4f_perms_matched_events:
        if pe:
            norms = [norm_rec(e) for e in pe]
            perm_means.append(sum(norms) / len(norms))
    m4f_mean = sum(perm_means) / len(perm_means) if perm_means else 0.0
    return {
        "nTRA": round(m1_mean - m4f_mean, 8),
        "M1_mean_nrecovery": round(m1_mean, 8),
        "M4f_mean_nrecovery": round(m4f_mean, 8),
    }


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return dot / (na * nb)


def spearman_rank_correlation(a, b):
    n = len(a)
    if n < 2:
        return 0.0
    def rankdata(x):
        indexed = sorted(enumerate(x), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and indexed[j + 1][1] == indexed[j][1]:
                j += 1
            mean_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[indexed[k][0]] = mean_rank
            i = j + 1
        return ranks
    ra = rankdata(a)
    rb = rankdata(b)
    d_sq = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1.0 - (6.0 * d_sq) / (n * (n * n - 1)) if n > 1 else 0.0


def compute_drs_event(event):
    demand = [abs(event["close_pre_state"][SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS]
    recovery = [abs(event["close_pre_state"][SV_INDEX[sv]] - EQUILIBRIUM) -
                abs(event["line_end_state"][SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS]
    return cosine_similarity(demand, recovery), spearman_rank_correlation(demand, recovery)


def compute_drs(m1_events, m4f_perms_matched_events):
    m1_mags, m1_ranks = [], []
    for e in m1_events:
        mg, rk = compute_drs_event(e)
        m1_mags.append(mg)
        m1_ranks.append(rk)
    m1_mm = sum(m1_mags) / len(m1_mags) if m1_mags else 0.0
    m1_mr = sum(m1_ranks) / len(m1_ranks) if m1_ranks else 0.0
    m1_comb = 0.6 * m1_mm + 0.4 * m1_mr
    pm_mags, pm_ranks = [], []
    for pe in m4f_perms_matched_events:
        if pe:
            ms, rs = [], []
            for e in pe:
                mg, rk = compute_drs_event(e)
                ms.append(mg)
                rs.append(rk)
            pm_mags.append(sum(ms) / len(ms))
            pm_ranks.append(sum(rs) / len(rs))
    m4f_mm = sum(pm_mags) / len(pm_mags) if pm_mags else 0.0
    m4f_mr = sum(pm_ranks) / len(pm_ranks) if pm_ranks else 0.0
    m4f_comb = 0.6 * m4f_mm + 0.4 * m4f_mr
    return {
        "DRS_mag_M1": round(m1_mm, 8), "DRS_rank_M1": round(m1_mr, 8),
        "DRS_combined_M1": round(m1_comb, 8),
        "DRS_mag_M4f": round(m4f_mm, 8), "DRS_rank_M4f": round(m4f_mr, 8),
        "DRS_combined_M4f": round(m4f_comb, 8),
        "DRS_advantage": round(m1_comb - m4f_comb, 8),
        "DRS_mag_advantage": round(m1_mm - m4f_mm, 8),
        "DRS_rank_advantage": round(m1_mr - m4f_mr, 8),
    }


def compute_scp(m1_events, m4f_perms_matched_events):
    m1_zones = []
    for e in m1_events:
        for sv in PROCESS_SVS:
            m1_zones.append(zone_quality(e["line_end_state"], sv))
    m1_mean = sum(m1_zones) / len(m1_zones) if m1_zones else 2.0
    perm_means = []
    for pe in m4f_perms_matched_events:
        zones = []
        for e in pe:
            for sv in PROCESS_SVS:
                zones.append(zone_quality(e["line_end_state"], sv))
        if zones:
            perm_means.append(sum(zones) / len(zones))
    m4f_mean = sum(perm_means) / len(perm_means) if perm_means else 2.0
    strict_ct = sum(1 for pm in perm_means if m1_mean > pm)
    loose_ct = sum(1 for pm in perm_means if m1_mean >= pm)
    delta = m1_mean - m4f_mean
    return {
        "SCP_strict": round(strict_ct / len(perm_means), 8) if perm_means else 0.5,
        "SCP_loose": round(loose_ct / len(perm_means), 8) if perm_means else 0.5,
        "SCP_delta": round(delta, 8),
        "M1_mean_zone": round(m1_mean, 8),
        "M4f_mean_zone": round(m4f_mean, 8),
    }


def compute_yga(m1_events, m4f_perms_matched_events):
    m1_yg = [e["y_gain_event"] for e in m1_events]
    m1_mean = sum(m1_yg) / len(m1_yg) if m1_yg else 0.0
    perm_means = []
    for pe in m4f_perms_matched_events:
        if pe:
            yg = [e["y_gain_event"] for e in pe]
            perm_means.append(sum(yg) / len(yg))
    m4f_mean = sum(perm_means) / len(perm_means) if perm_means else 0.0
    return {
        "YGA": round(m1_mean - m4f_mean, 8),
        "M1_mean_ygain": round(m1_mean, 8),
        "M4f_mean_ygain": round(m4f_mean, 8),
    }


def compute_dbp(m0_events, m1_events, m2a_events, m2b_events):
    mask_keys = set(e["line_key"] for e in m1_events)
    def mean_rec(events, mask):
        filt = [e for e in events if e["line_key"] in mask]
        if not filt:
            return 0.0
        return sum(_abs_recovery(e) for e in filt) / len(filt)
    m0r = mean_rec(m0_events, mask_keys)
    m1r = mean_rec(m1_events, mask_keys)
    m2ar = mean_rec(m2a_events, mask_keys)
    m2br = mean_rec(m2b_events, mask_keys)
    dbp = (m1r - m2br) - (m0r - m2ar)
    return {
        "DBP": round(dbp, 8),
        "M1_recovery": round(m1r, 8),
        "M2b_recovery": round(m2br, 8),
        "M0_recovery": round(m0r, 8),
        "M2a_recovery": round(m2ar, 8),
        "M1_B10_delta": round(m1r - m2br, 8),
        "M0_B10_delta": round(m0r - m2ar, 8),
        "mask_size": len(mask_keys),
    }


def extract_old_metrics(m1_data, m4f_perms, selection_tier):
    ebd = m1_data.get("events_by_demand", {})
    m1_dem_erm = None
    if selection_tier in ebd:
        m1_dem_erm = ebd[selection_tier].get("mean_ERM")
    elif "work_preceded" in ebd:
        m1_dem_erm = ebd["work_preceded"].get("mean_ERM")
    ebt = m1_data.get("events_by_type", {})
    m1_eany_erm = ebt.get("E_any", {}).get("mean_ERM")
    m4f_erms = []
    for perm in m4f_perms:
        pebt = perm.get("events_by_type", {})
        ea = pebt.get("E_any", {})
        if "mean_ERM" in ea:
            m4f_erms.append(ea["mean_ERM"])
    m4f_me = sum(m4f_erms) / len(m4f_erms) if m4f_erms else None
    ap2 = None
    if m1_dem_erm is not None and m4f_me is not None:
        ap2 = round(m1_dem_erm - m4f_me, 8)
    return {
        "M1_demanded_ERM": round(m1_dem_erm, 8) if m1_dem_erm is not None else None,
        "M1_E_any_ERM": round(m1_eany_erm, 8) if m1_eany_erm is not None else None,
        "M4f_mean_E_any_ERM": round(m4f_me, 8) if m4f_me is not None else None,
        "AP2_delta": ap2,
    }


def main():
    print("T4 Metric Computation - Phase 570b")
    print("=" * 50)
    print("Loading T2 data...")
    with open(T2_PATH, "r") as f:
        t2 = json.load(f)
    print("Loading T3 data...")
    with open(T3_PATH, "r") as f:
        t3 = json.load(f)
    folios = list(t2["primary_runs"].keys())
    print("Folios: %s" % folios)
    print()

    per_folio = {}
    demand_strong_folios = []

    for folio in folios:
        print("--- %s ---" % folio)
        m0d = t2["primary_runs"][folio]["M0"]
        m1d = t2["primary_runs"][folio]["M1"]
        m2ad = t2["primary_runs"][folio]["M2a"]
        m2bd = t2["primary_runs"][folio]["M2b"]

        m1_all = m1d["per_event_detail"]
        m1_ev, sel_tier = select_demanded_events(m1_all)
        dem_fb = (sel_tier != "work_preceded")
        n_dem = len(m1_ev)
        dem_strong = (sel_tier == "work_preceded" and n_dem >= 3)
        print("  Event selection: %s (n=%d, strong=%s)" % (sel_tier, n_dem, dem_strong))
        if dem_strong:
            demand_strong_folios.append(folio)

        m4f_raw = t3["m4f_demand_matched"][folio]["all_perms"]
        m4f_matched = [select_m4f_matched_events(p, sel_tier) for p in m4f_raw]
        print("  M4f perms: %d, matched per perm: %s..." % (
            len(m4f_matched), [len(x) for x in m4f_matched[:3]]))

        tra = compute_tra(m1_ev, m4f_matched)
        ntra = compute_ntra(m1_ev, m4f_matched)
        drs = compute_drs(m1_ev, m4f_matched)
        scp = compute_scp(m1_ev, m4f_matched)
        yga = compute_yga(m1_ev, m4f_matched)
        dbp = compute_dbp(m0d["per_event_detail"], m1_ev,
                          m2ad["per_event_detail"], m2bd["per_event_detail"])
        old_m = extract_old_metrics(m1d, m4f_raw, sel_tier)

        print("  TRA=%+.6f  nTRA=%+.6f  DRS_adv=%+.6f" % (
            tra["TRA"], ntra["nTRA"], drs["DRS_advantage"]))
        print("  SCP_delta=%+.6f  YGA=%+.6f  DBP=%+.6f" % (
            scp["SCP_delta"], yga["YGA"], dbp["DBP"]))

        per_folio[folio] = {
            "event_selection": sel_tier,
            "demand_fallback": dem_fb,
            "n_m1_demanded_events": n_dem,
            "TRA": tra, "nTRA": ntra, "DRS": drs,
            "SCP": scp, "YGA": yga, "DBP": dbp,
            "old_metrics": old_m,
            "demand_strong": dem_strong,
        }

    output = {
        "metadata": {
            "phase": "570b",
            "script": "t4_metric_computation.py",
            "timestamp": datetime.now().isoformat(),
            "folios": folios,
            "n_folios": len(folios),
            "metrics_computed": ["TRA", "nTRA", "DRS", "SCP", "YGA", "DBP"],
            "inputs": {"t2": os.path.basename(T2_PATH), "t3": os.path.basename(T3_PATH)},
        },
        "per_folio": per_folio,
        "demand_strong_folios": demand_strong_folios,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print()
    print("Output written to %s" % OUTPUT_PATH)

    # Summary table
    print()
    print("=" * 105)
    print("%-8s %4s %3s %10s %10s %10s %10s %10s %10s %6s" % (
        "Folio", "Sel", "N", "TRA", "nTRA", "DRS_adv", "SCP_delta", "YGA", "DBP", "Strong"))
    print("-" * 105)
    for folio in folios:
        fd = per_folio[folio]
        sel = fd["event_selection"][:4]
        n = fd["n_m1_demanded_events"]
        strong = "YES" if fd["demand_strong"] else "no"
        print("%-8s %4s %3d %+10.6f %+10.6f %+10.6f %+10.6f %+10.6f %+10.6f %6s" % (
            folio, sel, n,
            fd["TRA"]["TRA"], fd["nTRA"]["nTRA"], fd["DRS"]["DRS_advantage"],
            fd["SCP"]["SCP_delta"], fd["YGA"]["YGA"], fd["DBP"]["DBP"], strong))
    print("=" * 105)

    # DRS channels
    print()
    print("DRS Channel Detail:")
    print("%-8s %11s %12s %12s %13s %12s %13s" % (
        "Folio", "DRS_mag_M1", "DRS_mag_M4f", "DRS_rank_M1",
        "DRS_rank_M4f", "Combined_M1", "Combined_M4f"))
    print("-" * 85)
    for folio in folios:
        dd = per_folio[folio]["DRS"]
        print("%-8s %11.6f %12.6f %12.6f %13.6f %12.6f %13.6f" % (
            folio, dd["DRS_mag_M1"], dd["DRS_mag_M4f"],
            dd["DRS_rank_M1"], dd["DRS_rank_M4f"],
            dd["DRS_combined_M1"], dd["DRS_combined_M4f"]))
    print()

    # SCP win rates + old ERM
    print("SCP Win Rates + Old ERM:")
    print("%-8s %10s %10s %8s %9s %11s %10s %10s" % (
        "Folio", "SCP_strict", "SCP_loose", "M1_zone",
        "M4f_zone", "M1_dem_ERM", "M4f_E_ERM", "AP2_delta"))
    print("-" * 85)
    for folio in folios:
        sd = per_folio[folio]["SCP"]
        od = per_folio[folio]["old_metrics"]
        m1e = od.get("M1_demanded_ERM") or 0.0
        m4e = od.get("M4f_mean_E_any_ERM") or 0.0
        ap2 = od.get("AP2_delta") or 0.0
        print("%-8s %10.4f %10.4f %8.4f %9.4f %11.6f %10.6f %+10.6f" % (
            folio, sd["SCP_strict"], sd["SCP_loose"],
            sd["M1_mean_zone"], sd["M4f_mean_zone"], m1e, m4e, ap2))
    print()
    print("Demand-strong folios (%d): %s" % (len(demand_strong_folios), demand_strong_folios))
    print()
    print("Done.")


if __name__ == "__main__":
    main()

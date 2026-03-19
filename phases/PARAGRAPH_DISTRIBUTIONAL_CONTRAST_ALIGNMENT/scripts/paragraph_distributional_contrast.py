"""
Phase 606: Paragraph Distributional Contrast Alignment

Tests whether pseudo-Lull procedure-family contrasts predict Voynich folio
paragraph-mixture shape, using EMD-based shape margin as the primary object.

Predictions hash: b3fcb63c79c974b341835eb888bf0255c1451c3ed21a01d232cfa00b17134655
"""

import json
import os
import hashlib
import math
import numpy as np
from scipy import stats
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

# ── 0. Pre-registration hash verification ────────────────────────────

pred_path = os.path.join(ROOT, "phases", "PARAGRAPH_DISTRIBUTIONAL_CONTRAST_ALIGNMENT",
                         "PREDICTIONS.md")
with open(pred_path, "rb") as f:
    pred_hash = hashlib.sha256(f.read()).hexdigest()
expected_hash = "b3fcb63c79c974b341835eb888bf0255c1451c3ed21a01d232cfa00b17134655"
assert pred_hash == expected_hash, f"Hash mismatch: {pred_hash} != {expected_hash}"
print(f"Pre-registration hash verified: {pred_hash[:16]}...")

# ── 1. Load data sources ─────────────────────────────────────────────

# Source 1: Paragraph labels (264 paragraphs, 4 zones)
with open(os.path.join(ROOT, "phases", "PARAGRAPH_PROGRAM_TYPING", "results",
                        "paragraph_program_typing.json")) as f:
    para_data = json.load(f)
para_labels = para_data["paragraph_labels"]

# Source 2: Folio operational profiles
with open(os.path.join(ROOT, "results", "folio_operational_profiles.json")) as f:
    ops_data = json.load(f)
ops_profiles = {p["folio"]: p for p in ops_data["profiles"]}

# Source 3: Section labels
with open(os.path.join(ROOT, "phases", "A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES",
                        "results", "t0_opportunity_normalization.json")) as f:
    a2_data = json.load(f)
section_map = {f: v["section"] for f, v in a2_data["covariates"].items()}

# Source 4: Phase 602 PL characterization (for profile derivation)
with open(os.path.join(ROOT, "phases", "PSEUDO_LULL_CHARACTERIZATION", "results",
                        "pseudo_lull_structural_profile.json")) as f:
    pl_data = json.load(f)

# Source 5: REGIME labels
with open(os.path.join(ROOT, "results", "b_macro_scaffold_audit.json")) as f:
    scaffold_data = json.load(f)
regime_map = {f: v.get("regime", "UNKNOWN") for f, v in scaffold_data["features"].items()}

# ── 2. Recompute PL zone profiles from Phase 602 ────────────────────

SELECTED_FAMILIES = ["distillation", "sublimation", "dissolution"]
OPERATIONAL_PARTS = {"Practica", "Mercuriorum", "Furnis"}
DIM_NAMES = ["monitoring_density", "correction_rate", "heat_rate",
             "judgment_rate", "termination_rate", "chain_rate", "operational_density"]

family_chapters = defaultdict(list)
for ch in pl_data["E1_chapters"]:
    fam = ch.get("primary_family")
    if fam not in SELECTED_FAMILIES:
        continue
    if ch.get("part") not in OPERATIONAL_PARTS:
        continue
    if ch.get("theory_practice") == "theoretical":
        continue
    chapter_lines = max(ch["en_line_end"] - ch["en_line_start"], 1)
    sig = {
        "monitoring_density": ch.get("monitoring_density", 0.0),
        "correction_rate": ch.get("correction_count", 0) / chapter_lines * 100,
        "heat_rate": ch.get("heat_count", 0) / chapter_lines * 100,
        "judgment_rate": ch.get("judgment_count", 0) / chapter_lines * 100,
        "termination_rate": ch.get("termination_count", 0) / chapter_lines * 100,
        "chain_rate": ch.get("chain_count", 0) / chapter_lines * 100,
        "operational_density": ch.get("operational_density", 0.0),
    }
    family_chapters[fam].append(sig)

# Also compute theoretical_neg for N3
for ch in pl_data["E1_chapters"]:
    fam = ch.get("primary_family")
    if fam != "theoretical":
        continue
    if ch.get("part") not in OPERATIONAL_PARTS:
        continue
    chapter_lines = max(ch["en_line_end"] - ch["en_line_start"], 1)
    sig = {
        "monitoring_density": ch.get("monitoring_density", 0.0),
        "correction_rate": ch.get("correction_count", 0) / chapter_lines * 100,
        "heat_rate": ch.get("heat_count", 0) / chapter_lines * 100,
        "judgment_rate": ch.get("judgment_count", 0) / chapter_lines * 100,
        "termination_rate": ch.get("termination_count", 0) / chapter_lines * 100,
        "chain_rate": ch.get("chain_count", 0) / chapter_lines * 100,
        "operational_density": ch.get("operational_density", 0.0),
    }
    family_chapters["theoretical_neg"].append(sig)

print(f"PL chapters: " + ", ".join(f"{k}={len(v)}" for k, v in family_chapters.items()))

# Compute mean prototypes
family_prototypes = {}
for fam, chapters in family_chapters.items():
    proto = {}
    for dim in DIM_NAMES:
        proto[dim] = np.mean([ch[dim] for ch in chapters])
    family_prototypes[fam] = np.array([proto[d] for d in DIM_NAMES])

# Z-score against pooled mean/std of operational families only
op_families = ["distillation", "sublimation", "dissolution"]
proto_matrix = np.array([family_prototypes[f] for f in op_families])
proto_mean = proto_matrix.mean(axis=0)
proto_std = proto_matrix.std(axis=0)
proto_std[proto_std == 0] = 1.0

family_z = {}
for fam in list(family_prototypes.keys()):
    family_z[fam] = (family_prototypes[fam] - proto_mean) / proto_std


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


def derive_zone_profile(z_vec):
    """Derive C1398 zone weights from z-scored 7D PL prototype.
    DIM indices: monitoring(0), correction(1), heat(2), judgment(3),
                 termination(4), chain(5), operational(6)
    """
    zone0 = 0.5 * z_vec[2] + 0.3 * z_vec[6] + 0.2 * z_vec[4]  # THERMAL
    zone1 = 0.4 * z_vec[1] + 0.3 * z_vec[4] + 0.3 * z_vec[3]  # CONTAINMENT
    zone2 = 0.4 * z_vec[5] + 0.3 * z_vec[6] + 0.3 * z_vec[2]  # ITERATION
    zone3 = 0.5 * z_vec[0] + 0.3 * z_vec[3] + 0.2 * z_vec[1]  # MONITORING
    raw = np.array([zone0, zone1, zone2, zone3])
    return softmax(raw)


# Derive profiles
distill_profile = derive_zone_profile(family_z["distillation"])
sub_profile = derive_zone_profile(family_z["sublimation"])
diss_profile = derive_zone_profile(family_z["dissolution"])
basin_profile = (sub_profile + diss_profile) / 2.0
basin_profile = basin_profile / basin_profile.sum()  # renormalize
theo_profile = derive_zone_profile(family_z["theoretical_neg"])

print("PL zone profiles (recomputed):")
for name, prof in [("distillation", distill_profile), ("sublimation", sub_profile),
                   ("dissolution", diss_profile), ("basin", basin_profile),
                   ("theoretical_neg", theo_profile)]:
    print(f"  {name}: [{', '.join(f'{v:.3f}' for v in prof)}]")

# ── 3. Build per-folio 4D zone distributions ─────────────────────────

folio_paras = defaultdict(list)
for pl in para_labels:
    folio_paras[pl["folio"]].append(pl)

MIN_PARAS = 3
folio_zone_dist = {}
folio_para_count = {}
for folio, paras in folio_paras.items():
    if len(paras) < MIN_PARAS:
        continue
    n = len(paras)
    zone_counts = Counter(p["cluster"] for p in paras)
    dist = np.array([
        zone_counts.get(0, 0) / n,  # THERMAL-QO
        zone_counts.get(1, 0) / n,  # CONTAINMENT-Sealing
        zone_counts.get(2, 0) / n,  # OPERATION-Iteration
        zone_counts.get(3, 0) / n,  # MONITORING-Phase
    ])
    folio_zone_dist[folio] = dist
    folio_para_count[folio] = n

print(f"Folios with {MIN_PARAS}+ paragraphs: {len(folio_zone_dist)}")

# ── 4. Compute EMD distances and shape margin ────────────────────────


def emd_1d(p, q):
    """Earth mover's distance between two probability distributions."""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    ps, qs = p.sum(), q.sum()
    if ps > 0:
        p = p / ps
    if qs > 0:
        q = q / qs
    return float(np.sum(np.abs(np.cumsum(p) - np.cumsum(q))))


def jsd(p, q):
    """Jensen-Shannon divergence."""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    eps = 1e-10
    p = p + eps
    q = q + eps
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


folio_emd_distill = {}
folio_emd_basin = {}
folio_shape_margin = {}
folio_jsd_distill = {}
folio_jsd_basin = {}
folio_jsd_margin = {}

for folio, dist in folio_zone_dist.items():
    ed = emd_1d(dist, distill_profile)
    eb = emd_1d(dist, basin_profile)
    folio_emd_distill[folio] = ed
    folio_emd_basin[folio] = eb
    folio_shape_margin[folio] = ed - eb  # positive = closer to basin

    jd = jsd(dist, distill_profile)
    jb = jsd(dist, basin_profile)
    folio_jsd_distill[folio] = jd
    folio_jsd_basin[folio] = jb
    folio_jsd_margin[folio] = jd - jb

# ── 5. Build h_resid (OLS, identical to Phase 605) ──────────────────

# Intersect folios: need zone dist + ops profiles + section
common_folios = sorted(
    f for f in folio_zone_dist
    if f in ops_profiles and f in section_map
    and section_map[f] in ("S", "H", "B")
)

n_folios = len(common_folios)
print(f"Common folios (S/H/B with zone dist): {n_folios}")

# Build arrays
h_arr = np.array([ops_profiles[f]["h_ratio"] for f in common_folios])
k_arr = np.array([ops_profiles[f]["k_ratio"] for f in common_folios])
sections = [section_map[f] for f in common_folios]
thermo_ke = np.array([ops_profiles[f]["thermo_ke"] for f in common_folios])

# OLS: h_ratio ~ section_S + section_B + k_ratio (H = reference)
X = np.ones((n_folios, 4))
for i in range(n_folios):
    X[i, 1] = 1.0 if sections[i] == "S" else 0.0
    X[i, 2] = 1.0 if sections[i] == "B" else 0.0
    X[i, 3] = k_arr[i]

beta = np.linalg.lstsq(X, h_arr, rcond=None)[0]
h_resid = h_arr - X @ beta
h_resid_lookup = {common_folios[i]: h_resid[i] for i in range(n_folios)}

print(f"h_ratio_resid: mean={h_resid.mean():.6f}, std={h_resid.std():.6f}")

# Build lookup arrays for common folios
margin_arr = np.array([folio_shape_margin[f] for f in common_folios])
thermo_arr = thermo_ke
zone_dists = np.array([folio_zone_dist[f] for f in common_folios])
jsd_margin_arr = np.array([folio_jsd_margin[f] for f in common_folios])

results = {
    "phase": 606,
    "predictions_hash": pred_hash,
    "n_folios": n_folios,
    "n_paragraphs": len(para_labels),
    "zone_counts": {str(k): v for k, v in
                    Counter(p["cluster"] for p in para_labels).items()},
    "reference_profiles": {
        "distillation": distill_profile.tolist(),
        "basin": basin_profile.tolist(),
        "sublimation": sub_profile.tolist(),
        "dissolution": diss_profile.tolist(),
        "theoretical_neg": theo_profile.tolist(),
    },
    "h_resid": {
        "mean": float(h_resid.mean()),
        "std": float(h_resid.std()),
        "n": n_folios,
    },
}

# ── Helper functions ─────────────────────────────────────────────────


def spearman_one_sided(x, y, positive=True):
    """One-sided Spearman correlation. Returns (rho, p_one_sided)."""
    rho, p_two = stats.spearmanr(x, y)
    if positive:
        p_one = p_two / 2 if rho > 0 else 1 - p_two / 2
    else:
        p_one = p_two / 2 if rho < 0 else 1 - p_two / 2
    return float(rho), float(p_one)


# ── 6. S0/S1 Gates ──────────────────────────────────────────────────

s0_pass = n_folios >= 40
print(f"\nS0 {'PASS' if s0_pass else 'FAIL'}: n_folios={n_folios} (need >=40)")
results["S0"] = {"pass": s0_pass, "n_folios": n_folios}

if s0_pass:
    # S1: h_resid vs THERMAL zone fraction, one-sided negative, p<0.01
    thermal_frac = zone_dists[:, 0]
    s1_rho, s1_p = spearman_one_sided(h_resid, thermal_frac, positive=False)
    s1_pass = s1_p < 0.01
    print(f"S1 {'PASS' if s1_pass else 'FAIL'}: h_resid vs THERMAL_frac "
          f"rho={s1_rho:.4f}, p={s1_p:.6f}")
    results["S1"] = {"pass": s1_pass, "rho": s1_rho, "p": s1_p}

    if s1_pass:

        # ── 7. Primary Battery ───────────────────────────────────────

        print("\n=== PRIMARY PREDICTION BATTERY ===")

        # P1: shape_margin vs h_resid, positive
        p1_rho, p1_p = spearman_one_sided(margin_arr, h_resid, positive=True)
        p1_pass = p1_p < 0.05
        print(f"  P1 (margin vs h_resid): rho={p1_rho:.4f}, p={p1_p:.4f}, "
              f"{'PASS' if p1_pass else 'FAIL'} (n={n_folios})")

        # P2: shape_margin vs thermo_ke, negative
        p2_rho, p2_p = spearman_one_sided(margin_arr, thermo_arr, positive=False)
        p2_pass = p2_p < 0.05
        print(f"  P2 (margin vs thermo_ke): rho={p2_rho:.4f}, p={p2_p:.4f}, "
              f"{'PASS' if p2_pass else 'FAIL'} (n={n_folios})")

        # P3: Within-section shape discrimination
        p3_results = {}
        p3_pass = False
        for sec in ["H", "S"]:
            sec_idx = [i for i in range(n_folios) if sections[i] == sec]
            sec_name = "Herbal" if sec == "H" else "Stars"
            if len(sec_idx) < 10:
                p3_results[sec_name] = {"n": len(sec_idx), "skip": True}
                print(f"  P3 within-{sec_name}: SKIP (n={len(sec_idx)})")
                continue
            sec_margin = margin_arr[sec_idx]
            sec_hresid = h_resid[sec_idx]
            rho, p_val = spearman_one_sided(sec_margin, sec_hresid, positive=True)
            passes = p_val < 0.05
            if passes:
                p3_pass = True
            p3_results[sec_name] = {
                "n": len(sec_idx), "rho": float(rho), "p": float(p_val),
                "pass": passes,
            }
            print(f"  P3 within-{sec_name}: rho={rho:.4f}, p={p_val:.4f}, "
                  f"{'PASS' if passes else 'FAIL'} (n={len(sec_idx)})")
        print(f"  P3 overall: {'PASS' if p3_pass else 'FAIL'} "
              f"(at least one section passes)")

        primary_results = [
            {"id": "P1_MARGIN_HRESID", "rho": p1_rho, "p": p1_p,
             "pass": p1_pass, "n": n_folios},
            {"id": "P2_MARGIN_THERMO", "rho": p2_rho, "p": p2_p,
             "pass": p2_pass, "n": n_folios},
            {"id": "P3_WITHIN_SECTION", "details": p3_results,
             "pass": p3_pass},
        ]

        K = sum(1 for r in primary_results if r["pass"])
        print(f"\nPrimary passes: {K}/3")

        # ── 8. Secondary Battery ─────────────────────────────────────

        print("\n=== SECONDARY BATTERY ===")

        # S2: h_resid vs MONITORING zone fraction, positive
        monitoring_frac = zone_dists[:, 3]
        s2_rho, s2_p = spearman_one_sided(h_resid, monitoring_frac, positive=True)
        s2_pass = s2_p < 0.05
        print(f"  S2 (h_resid vs MONITORING_frac): rho={s2_rho:.4f}, "
              f"p={s2_p:.4f}, {'PASS' if s2_pass else 'FAIL'} (n={n_folios})")

        # S3: shape_margin vs (OPERATION + MONITORING) combined fraction
        op_mon_frac = zone_dists[:, 2] + zone_dists[:, 3]
        s3_rho, s3_p = spearman_one_sided(margin_arr, op_mon_frac, positive=True)
        s3_pass = s3_p < 0.05
        print(f"  S3 (margin vs OP+MON_frac): rho={s3_rho:.4f}, "
              f"p={s3_p:.4f}, {'PASS' if s3_pass else 'FAIL'} (n={n_folios})")

        secondary_results = [
            {"id": "S2_HRESID_MONITORING", "rho": s2_rho, "p": s2_p,
             "pass": s2_pass, "n": n_folios},
            {"id": "S3_MARGIN_OPMON", "rho": s3_rho, "p": s3_p,
             "pass": s3_pass, "n": n_folios},
        ]

        # ── 9. Exploratory Diagnostics ───────────────────────────────

        print("\n=== EXPLORATORY DIAGNOSTICS ===")

        # D1: h_resid vs OPERATION zone fraction
        op_frac = zone_dists[:, 2]
        d1_rho, d1_p_two = stats.spearmanr(h_resid, op_frac)
        print(f"  D1 (h_resid vs OPERATION_frac): rho={d1_rho:.4f}, "
              f"p_two={d1_p_two:.4f} (n={n_folios})")

        # D2: JSD-based margin vs h_resid
        d2_rho, d2_p = spearman_one_sided(jsd_margin_arr, h_resid, positive=True)
        print(f"  D2 (JSD margin vs h_resid): rho={d2_rho:.4f}, "
              f"p={d2_p:.4f} (n={n_folios})")

        exploratory_results = [
            {"id": "D1_OPERATION", "rho": float(d1_rho),
             "p_two_sided": float(d1_p_two), "n": n_folios},
            {"id": "D2_JSD_MARGIN", "rho": d2_rho, "p": d2_p, "n": n_folios},
        ]

        # ── 10. N1: Cross-folio zone permutation ────────────────────

        print("\n=== N1: CROSS-FOLIO ZONE PERMUTATION ===")
        rng = np.random.RandomState(42)
        N_PERM = 500

        # Build paragraph pool: list of (folio, zone) pairs
        all_zones = []
        folio_sizes = {}
        for folio in common_folios:
            paras = folio_paras.get(folio, [])
            qualified = [p for p in paras if folio in folio_zone_dist]
            if not qualified:
                continue
            folio_sizes[folio] = len(qualified)
            for p in qualified:
                all_zones.append(p["cluster"])

        # For each permutation: shuffle zone assignments across folios
        # preserving folio paragraph counts and global zone pool
        perm_rhos_p1 = []
        perm_rhos_p2 = []
        zone_pool = np.array(all_zones)

        for _ in range(N_PERM):
            shuffled = rng.permutation(zone_pool)
            idx = 0
            perm_margin = np.zeros(n_folios)
            for fi, folio in enumerate(common_folios):
                n_para = folio_sizes.get(folio, 0)
                if n_para == 0:
                    continue
                assigned = shuffled[idx:idx + n_para]
                idx += n_para
                zone_counts = Counter(int(z) for z in assigned)
                dist = np.array([
                    zone_counts.get(0, 0) / n_para,
                    zone_counts.get(1, 0) / n_para,
                    zone_counts.get(2, 0) / n_para,
                    zone_counts.get(3, 0) / n_para,
                ])
                ed = emd_1d(dist, distill_profile)
                eb = emd_1d(dist, basin_profile)
                perm_margin[fi] = ed - eb

            rho1, _ = stats.spearmanr(perm_margin, h_resid)
            rho2, _ = stats.spearmanr(perm_margin, thermo_arr)
            perm_rhos_p1.append(abs(rho1))
            perm_rhos_p2.append(abs(rho2))

        n1_p1_frac = np.mean(np.array(perm_rhos_p1) >= abs(p1_rho))
        n1_p2_frac = np.mean(np.array(perm_rhos_p2) >= abs(p2_rho))
        n1_p1_survives = n1_p1_frac < 0.05
        n1_p2_survives = n1_p2_frac < 0.05

        print(f"  P1: |rho|={abs(p1_rho):.4f}, frac_exceeding={n1_p1_frac:.3f}, "
              f"{'SURVIVES' if n1_p1_survives else 'FAILS'}")
        print(f"  P2: |rho|={abs(p2_rho):.4f}, frac_exceeding={n1_p2_frac:.3f}, "
              f"{'SURVIVES' if n1_p2_survives else 'FAILS'}")

        n1_results = {
            "n_shuffles": N_PERM,
            "P1_frac_exceeding": float(n1_p1_frac),
            "P1_survives": n1_p1_survives,
            "P2_frac_exceeding": float(n1_p2_frac),
            "P2_survives": n1_p2_survives,
        }

        # ── 11. N2: Random Dirichlet profiles ───────────────────────

        print("\n=== N2: RANDOM DIRICHLET PROFILES ===")
        N_RANDOM = 500
        random_rhos_p1 = []

        for _ in range(N_RANDOM):
            # Draw two random 4D profiles from Dirichlet(1,1,1,1)
            rand_distill = rng.dirichlet(np.ones(4))
            rand_basin = rng.dirichlet(np.ones(4))
            rand_margin = np.zeros(n_folios)
            for fi, folio in enumerate(common_folios):
                dist = folio_zone_dist[folio]
                ed = emd_1d(dist, rand_distill)
                eb = emd_1d(dist, rand_basin)
                rand_margin[fi] = ed - eb
            rho, _ = stats.spearmanr(rand_margin, h_resid)
            random_rhos_p1.append(abs(rho))

        n2_frac = np.mean(np.array(random_rhos_p1) >= abs(p1_rho))
        n2_pass = n2_frac < 0.05
        print(f"  P1 |rho|={abs(p1_rho):.4f}, frac_exceeding={n2_frac:.3f}, "
              f"{'PASS' if n2_pass else 'FAIL'}")

        n2_results = {
            "n_random": N_RANDOM,
            "P1_frac_exceeding": float(n2_frac),
            "pass": n2_pass,
        }

        # ── 12. N3: Theoretical_neg profile null ─────────────────────

        print("\n=== N3: THEORETICAL_NEG PROFILE NULL ===")
        # Compute shape margin using theoretical_neg profile vs basin
        theo_margin = np.zeros(n_folios)
        for fi, folio in enumerate(common_folios):
            dist = folio_zone_dist[folio]
            ed = emd_1d(dist, theo_profile)
            eb = emd_1d(dist, basin_profile)
            theo_margin[fi] = ed - eb

        n3_rho, n3_p_two = stats.spearmanr(theo_margin, h_resid)
        n3_clean = abs(n3_p_two) > 0.10  # no significant correlation
        print(f"  theo_margin vs h_resid: rho={n3_rho:.4f}, p_two={n3_p_two:.4f}, "
              f"{'CLEAN' if n3_clean else 'DIRTY'}")

        n3_results = {
            "rho": float(n3_rho),
            "p_two_sided": float(n3_p_two),
            "clean": n3_clean,
        }

        # ── 13. Sensitivity Analyses ─────────────────────────────────

        print("\n=== SENSITIVITY: WITHIN-HERBAL ===")
        herbal_idx = [i for i in range(n_folios) if sections[i] == "H"]
        sens_herbal = {}
        if len(herbal_idx) >= 10:
            h_m = margin_arr[herbal_idx]
            h_hr = h_resid[herbal_idx]
            h_tk = thermo_arr[herbal_idx]
            rho1, p1 = spearman_one_sided(h_m, h_hr, positive=True)
            rho2, p2 = spearman_one_sided(h_m, h_tk, positive=False)
            sens_herbal = {
                "n": len(herbal_idx),
                "P1": {"rho": float(rho1), "p": float(p1)},
                "P2": {"rho": float(rho2), "p": float(p2)},
            }
            print(f"  P1: rho={rho1:.4f}, p={p1:.4f} (n={len(herbal_idx)})")
            print(f"  P2: rho={rho2:.4f}, p={p2:.4f} (n={len(herbal_idx)})")
        else:
            print(f"  SKIP (n={len(herbal_idx)})")
            sens_herbal = {"n": len(herbal_idx), "skip": True}

        print("\n=== SENSITIVITY: WITHIN-STARS ===")
        stars_idx = [i for i in range(n_folios) if sections[i] == "S"]
        sens_stars = {}
        if len(stars_idx) >= 10:
            s_m = margin_arr[stars_idx]
            s_hr = h_resid[stars_idx]
            s_tk = thermo_arr[stars_idx]
            rho1, p1 = spearman_one_sided(s_m, s_hr, positive=True)
            rho2, p2 = spearman_one_sided(s_m, s_tk, positive=False)
            sens_stars = {
                "n": len(stars_idx),
                "P1": {"rho": float(rho1), "p": float(p1)},
                "P2": {"rho": float(rho2), "p": float(p2)},
            }
            print(f"  P1: rho={rho1:.4f}, p={p1:.4f} (n={len(stars_idx)})")
            print(f"  P2: rho={rho2:.4f}, p={p2:.4f} (n={len(stars_idx)})")
        else:
            print(f"  SKIP (n={len(stars_idx)})")
            sens_stars = {"n": len(stars_idx), "skip": True}

        print("\n=== SENSITIVITY: SECTION+REGIME CONTROL ===")
        regimes = [regime_map.get(f, "UNKNOWN") for f in common_folios]
        unique_regimes = sorted(set(regimes))
        X2 = np.ones((n_folios, 4 + len(unique_regimes) - 1))
        for i in range(n_folios):
            X2[i, 1] = 1.0 if sections[i] == "S" else 0.0
            X2[i, 2] = 1.0 if sections[i] == "B" else 0.0
            X2[i, 3] = k_arr[i]
            for j, reg in enumerate(unique_regimes[1:]):
                X2[i, 4 + j] = 1.0 if regimes[i] == reg else 0.0

        beta2 = np.linalg.lstsq(X2, h_arr, rcond=None)[0]
        h_resid_regime = h_arr - X2 @ beta2
        rho_reg_p1, p_reg_p1 = spearman_one_sided(
            margin_arr, h_resid_regime, positive=True)
        rho_reg_p2, p_reg_p2 = spearman_one_sided(
            margin_arr, thermo_arr, positive=False)  # thermo unchanged
        print(f"  P1 (margin vs h_resid_regime): rho={rho_reg_p1:.4f}, "
              f"p={p_reg_p1:.4f}")
        print(f"  P2 (margin vs thermo_ke): rho={rho_reg_p2:.4f}, "
              f"p={p_reg_p2:.4f}")

        sens_regime = {
            "P1": {"rho": float(rho_reg_p1), "p": float(p_reg_p1)},
            "P2": {"rho": float(rho_reg_p2), "p": float(p_reg_p2)},
        }

        print("\n=== SENSITIVITY: JSD AS METRIC ===")
        jsd_rho_p1, jsd_p_p1 = spearman_one_sided(
            jsd_margin_arr, h_resid, positive=True)
        jsd_rho_p2, jsd_p_p2 = spearman_one_sided(
            jsd_margin_arr, thermo_arr, positive=False)
        print(f"  P1 (JSD margin vs h_resid): rho={jsd_rho_p1:.4f}, "
              f"p={jsd_p_p1:.4f}")
        print(f"  P2 (JSD margin vs thermo_ke): rho={jsd_rho_p2:.4f}, "
              f"p={jsd_p_p2:.4f}")

        sens_jsd = {
            "P1": {"rho": float(jsd_rho_p1), "p": float(jsd_p_p1)},
            "P2": {"rho": float(jsd_rho_p2), "p": float(jsd_p_p2)},
        }

        # ── 14. Verdict Determination ────────────────────────────────

        # K_perm: primary predictions that pass AND survive controls
        # P1: must survive N1 + N2
        # P2: must survive N1
        # P3: within-section (N1 not directly applicable)
        p1_survives_all = p1_pass and n1_p1_survives and n2_pass
        p2_survives_all = p2_pass and n1_p2_survives
        p3_survives = p3_pass  # within-section is its own control

        K_perm = sum([p1_survives_all, p2_survives_all, p3_survives])

        if K_perm >= 3 and n3_clean:
            verdict = "PARAGRAPH_DISTRIBUTIONAL_ALIGNMENT_CONFIRMED"
        elif K_perm == 2:
            verdict = "PARTIAL_DISTRIBUTIONAL_ALIGNMENT"
        elif K_perm == 1:
            verdict = "WEAK_SIGNAL"
        else:
            verdict = "NOT_CONFIRMED"

        print(f"\n{'='*60}")
        print(f"Verdict: {verdict}")
        print(f"  Primary passes (K): {K}/3")
        print(f"  Permutation+control survivors (K_perm): {K_perm}")
        print(f"  N3 theoretical_neg: {'CLEAN' if n3_clean else 'DIRTY'}")
        print(f"{'='*60}")

        results["verdict"] = verdict
        results["primary_battery"] = primary_results
        results["secondary_battery"] = secondary_results
        results["exploratory"] = exploratory_results
        results["K"] = K
        results["K_perm"] = K_perm
        results["N1_permutation"] = n1_results
        results["N2_dirichlet"] = n2_results
        results["N3_theoretical_neg"] = n3_results
        results["sensitivity"] = {
            "within_herbal": sens_herbal,
            "within_stars": sens_stars,
            "section_regime_control": sens_regime,
            "jsd_metric": sens_jsd,
        }

    else:
        print("\nS1 FAILED — stopping.")
        results["verdict"] = "CALIBRATION_FAILURE"
else:
    print("\nS0 FAILED — stopping.")
    results["verdict"] = "INSUFFICIENT_DATA"

# ── 15. Write results ────────────────────────────────────────────────


def convert_numpy(obj):
    """Recursively convert numpy types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    return obj


out_path = os.path.join(ROOT, "phases", "PARAGRAPH_DISTRIBUTIONAL_CONTRAST_ALIGNMENT",
                        "results", "paragraph_distributional_contrast_results.json")
with open(out_path, "w") as f:
    json.dump(convert_numpy(results), f, indent=2)
print(f"\nResults written to {out_path}")
print(f"VERDICT: {results.get('verdict', 'N/A')}")

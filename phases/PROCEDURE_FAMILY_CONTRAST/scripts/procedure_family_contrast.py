"""
Phase 605: Procedure-Family Contrast Alignment
Tests whether the pseudo-Lull distillation-sublimation contrast predicts
Voynich feature contrasts along the residualized monitoring axis.
"""
import json
import os
import math
import hashlib
import numpy as np
from scipy import stats
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ── 0. Pre-registration hash verification ──────────────────────────────
pred_path = os.path.join(ROOT, "phases", "PROCEDURE_FAMILY_CONTRAST", "PREDICTIONS.md")
with open(pred_path, "rb") as f:
    pred_hash = hashlib.sha256(f.read()).hexdigest()
EXPECTED_HASH = "18af376293e8062b741feca71ec7ba49df0064ef01cfc6590890b0c0451cce44"
assert pred_hash == EXPECTED_HASH, f"PREDICTIONS.md hash mismatch: {pred_hash}"
print(f"Pre-registration hash verified: {pred_hash[:16]}...")

# ── 1. Load data sources ───────────────────────────────────────────────

# Phase 604 results (prototypes for S1 calibration re-derivation)
with open(os.path.join(ROOT, "phases", "PROCEDURE_FAMILY_ALIGNMENT", "results",
                        "procedure_family_alignment_results.json")) as f:
    p604 = json.load(f)

# Phase 602 profile (for PL family density verification)
with open(os.path.join(ROOT, "phases", "PSEUDO_LULL_CHARACTERIZATION", "results",
                        "pseudo_lull_structural_profile.json")) as f:
    pl_profile = json.load(f)

# Folio operational profiles (h_ratio, k_ratio, terminal_rate, iteration_rate, thermo_ke, checkpoint_rate)
with open(os.path.join(ROOT, "results", "folio_operational_profiles.json")) as f:
    fop_data = json.load(f)

# Macro scaffold audit (cycle_regularity, intervention_frequency, recovery_ops_count)
with open(os.path.join(ROOT, "results", "b_macro_scaffold_audit.json")) as f:
    scaffold_data = json.load(f)

# Closure/opportunity normalization (strong_close_fraction, opaque_close_fraction, section)
with open(os.path.join(ROOT, "phases", "A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES", "results",
                        "t0_opportunity_normalization.json")) as f:
    closure_data = json.load(f)

# Paragraph program typing (cluster assignments for THERMAL zone fraction)
with open(os.path.join(ROOT, "phases", "PARAGRAPH_PROGRAM_TYPING", "results",
                        "paragraph_program_typing.json")) as f:
    para_data = json.load(f)

# ── 2. Build unified folio feature matrix ──────────────────────────────

# Build folio lookup from operational profiles
fop_lookup = {}
for p in fop_data["profiles"]:
    fop_lookup[p["folio"]] = p

# Get section from closure data
section_lookup = {}
for folio, cov in closure_data["covariates"].items():
    section_lookup[folio] = cov["section"]

# Get REGIME from scaffold
regime_lookup = {}
for folio, feat in scaffold_data["features"].items():
    regime_lookup[folio] = feat.get("regime", "?")

# Compute per-folio thermal paragraph fraction (fraction of paragraphs in cluster 0)
# Cluster 0 = THERMAL-heavy (centroid THERMAL=0.424)
para_cluster_counts = defaultdict(lambda: defaultdict(int))
for pl in para_data["paragraph_labels"]:
    para_cluster_counts[pl["folio"]][pl["cluster"]] += 1

folio_thermal_frac = {}
for folio, cluster_counts in para_cluster_counts.items():
    total = sum(cluster_counts.values())
    if total >= 3:  # minimum qualifying paragraphs
        folio_thermal_frac[folio] = cluster_counts.get(0, 0) / total

# Build unified matrix: folios that have ALL required features
folios = []
features = {}  # folio -> dict of features

for folio in fop_lookup:
    if folio not in section_lookup:
        continue
    if folio not in scaffold_data["features"]:
        continue
    section = section_lookup[folio]
    # Drop T/C for small n
    if section not in ("S", "H", "B"):
        continue

    fp = fop_lookup[folio]
    sc = scaffold_data["features"][folio]
    cl = closure_data["covariates"].get(folio, {})

    features[folio] = {
        "h_ratio": fp["h_ratio"],
        "k_ratio": fp["k_ratio"],
        "terminal_rate": fp["terminal_rate"],
        "iteration_rate": fp["iteration_rate"],
        "thermo_ke": fp["thermo_ke"],
        "checkpoint_rate": fp["checkpoint_rate"],
        "section": section,
        "regime": regime_lookup.get(folio, "?"),
        "cycle_regularity": sc["cycle_regularity"],
        "intervention_frequency": sc["intervention_frequency"],
        "recovery_ops_count": sc["recovery_ops_count"],
        "n_tokens": fp["token_count"],
        "strong_close_fraction": cl.get("strong_close_fraction"),
        "opaque_close_fraction": cl.get("opaque_close_fraction"),
        "thermal_para_frac": folio_thermal_frac.get(folio),
    }
    folios.append(folio)

n_folios = len(folios)
print(f"Unified folio matrix: {n_folios} folios (S/H/B only)")

# ── 3. Compute h_ratio_resid ──────────────────────────────────────────

h_arr = np.array([features[f]["h_ratio"] for f in folios])
k_arr = np.array([features[f]["k_ratio"] for f in folios])
sections = [features[f]["section"] for f in folios]

# Build design matrix: section dummies (S, H, B -> 2 dummies + intercept) + k_ratio
# Use H as reference category
X = np.ones((n_folios, 4))  # intercept, S_dummy, B_dummy, k_ratio
for i, sec in enumerate(sections):
    X[i, 1] = 1.0 if sec == "S" else 0.0
    X[i, 2] = 1.0 if sec == "B" else 0.0
    X[i, 3] = k_arr[i]

# OLS: h_ratio ~ section + k_ratio
beta = np.linalg.lstsq(X, h_arr, rcond=None)[0]
h_predicted = X @ beta
h_resid = h_arr - h_predicted

print(f"h_ratio_resid: mean={h_resid.mean():.6f}, std={h_resid.std():.6f}")
print(f"  Correlation with k_ratio: {np.corrcoef(h_resid, k_arr)[0,1]:.4f}")

# Build h_resid lookup
h_resid_lookup = {folios[i]: h_resid[i] for i in range(n_folios)}

# ── 4. S0: Data Sufficiency Gate ──────────────────────────────────────

results = {
    "phase": 605,
    "predictions_hash": pred_hash,
    "n_folios": n_folios,
}

if n_folios < 60:
    results["verdict"] = "INSUFFICIENT_DATA"
    print(f"S0 FAIL: n_folios={n_folios} < 60")
else:
    print(f"S0 PASS: n_folios={n_folios} >= 60")
    results["S0"] = {"pass": True, "n_folios": n_folios}

    # ── 5. S1: Calibration Anchor ─────────────────────────────────────

    # Re-derive Phase 604 Approach A assignments using prototypes from results
    # prototypes are in p604["stage1"]["prototypes"] (7D)
    # Approach A used 3D: monitoring_density(0), correction_rate(1), heat_rate(2)
    # mapped to h_ratio, safety_balance, k_ratio
    # We need to re-derive which folios got sublimation vs distillation
    # Instead of full re-derivation, use prototype directions in z-scored space

    # Load prototypes
    prototypes = p604["stage1"]["prototypes"]
    proto_dims = p604["stage1"]["prototype_dims"]

    # Get 3D prototypes (monitoring, correction, heat)
    families_op = ["distillation", "fixation", "sublimation", "dissolution"]
    proto_3d = {}
    for fam in families_op:
        pv = prototypes[fam]
        proto_3d[fam] = np.array([pv[0], pv[1], pv[2]])  # monitoring, correction, heat

    # Z-score prototypes across families
    all_proto = np.array([proto_3d[f] for f in families_op])
    proto_mean = all_proto.mean(axis=0)
    proto_std = all_proto.std(axis=0)
    proto_std[proto_std == 0] = 1
    proto_z = {fam: (proto_3d[fam] - proto_mean) / proto_std for fam in families_op}

    # For V folios, use h_ratio, safety_balance, k_ratio
    # Need safety_balance - compute from transcript
    import sys
    sys.path.insert(0, ROOT)
    from scripts.voynich import Transcript, Morphology

    tx = Transcript()
    morph = Morphology()

    def decompose_middle_hmt(token):
        m = morph.extract(token.word)
        if not m or not m.middle:
            return None
        mid = m.middle
        head = mid[0] if mid else None
        term = mid[-1] if mid else None
        return head, term

    # Compute per-folio safety_balance
    folio_ey = defaultdict(int)
    folio_ii = defaultdict(int)
    folio_tok = defaultdict(int)
    for token in tx.currier_b():
        if token.placement.startswith("L"):
            continue
        if not token.word.strip() or "*" in token.word:
            continue
        folio_tok[token.folio] += 1
        result = decompose_middle_hmt(token)
        if not result:
            continue
        head, term = result
        m = morph.extract(token.word)
        mid = m.middle
        if head == "e" and term == "y":
            folio_ey[token.folio] += 1
        max_consec_i = 0
        cur = 0
        for c in mid:
            if c == "i":
                cur += 1
                max_consec_i = max(max_consec_i, cur)
            else:
                cur = 0
        if max_consec_i >= 2:
            folio_ii[token.folio] += 1

    safety_balance = {}
    for f in folios:
        n = folio_tok.get(f, 0)
        if n > 0:
            ey_rate = folio_ey.get(f, 0) / n
            ii_rate = folio_ii.get(f, 0) / n
            safety_balance[f] = ey_rate - ii_rate

    # Build V folio signatures (h_ratio, safety_balance, k_ratio)
    v_sigs = {}
    for f in folios:
        if f in safety_balance:
            v_sigs[f] = np.array([features[f]["h_ratio"], safety_balance[f], features[f]["k_ratio"]])

    # Z-score V signatures
    v_folios_cal = [f for f in folios if f in v_sigs]
    v_mat = np.array([v_sigs[f] for f in v_folios_cal])
    v_mean = v_mat.mean(axis=0)
    v_std = v_mat.std(axis=0)
    v_std[v_std == 0] = 1
    v_z = {f: (v_sigs[f] - v_mean) / v_std for f in v_folios_cal}

    # Assign each folio to nearest operational family by cosine
    def cosine_sim(a, b):
        dot = np.dot(a, b)
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0
        return dot / (na * nb)

    folio_assignments = {}
    for f in v_folios_cal:
        best_fam = None
        best_cos = -999
        for fam in families_op:
            c = cosine_sim(v_z[f], proto_z[fam])
            if c > best_cos:
                best_cos = c
                best_fam = fam
        folio_assignments[f] = best_fam

    # S1: sublimation-assigned folios have higher h_ratio_resid than distillation-assigned
    sub_resids = [h_resid_lookup[f] for f in v_folios_cal
                  if folio_assignments[f] == "sublimation" and f in h_resid_lookup]
    dist_resids = [h_resid_lookup[f] for f in v_folios_cal
                   if folio_assignments[f] == "distillation" and f in h_resid_lookup]

    U_s1, p_s1 = stats.mannwhitneyu(sub_resids, dist_resids, alternative="greater")
    s1_pass = p_s1 < 0.01

    results["S1"] = {
        "pass": s1_pass,
        "sublimation_n": len(sub_resids),
        "distillation_n": len(dist_resids),
        "sublimation_mean_h_resid": float(np.mean(sub_resids)),
        "distillation_mean_h_resid": float(np.mean(dist_resids)),
        "U": float(U_s1),
        "p": float(p_s1),
    }
    print(f"\nS1 Calibration: {'PASS' if s1_pass else 'FAIL'}")
    print(f"  Sublimation h_resid: {np.mean(sub_resids):.4f} (n={len(sub_resids)})")
    print(f"  Distillation h_resid: {np.mean(dist_resids):.4f} (n={len(dist_resids)})")
    print(f"  U={U_s1:.0f}, p={p_s1:.6f}")

    if not s1_pass:
        results["verdict"] = "CALIBRATION_FAILURE"
    else:
        # ── 6. Primary Prediction Battery ─────────────────────────────

        def spearman_one_sided(x, y, predicted_positive):
            """Spearman correlation with one-sided p-value in predicted direction."""
            rho, p_two = stats.spearmanr(x, y)
            if predicted_positive:
                p_one = p_two / 2 if rho > 0 else 1 - p_two / 2
            else:
                p_one = p_two / 2 if rho < 0 else 1 - p_two / 2
            return rho, p_one

        # Build arrays for each prediction
        primary_predictions = [
            {
                "id": "P1_TERM",
                "feature": "terminal_rate",
                "direction": "positive",
                "pl_basis": "sublimation termination_rate 2.5x distillation",
            },
            {
                "id": "P2_ITER",
                "feature": "iteration_rate",
                "direction": "positive",
                "pl_basis": "sublimation chain_rate 2.4x distillation",
            },
            {
                "id": "P3_HEAT_NEG",
                "feature": "thermo_ke",
                "direction": "negative",
                "pl_basis": "distillation heat_rate 1.17x sublimation",
            },
            {
                "id": "P4_THERMAL_NEG",
                "feature": "thermal_para_frac",
                "direction": "negative",
                "pl_basis": "distillation heat-dominant family",
            },
        ]

        secondary_predictions = [
            {
                "id": "S1_CYCLE",
                "feature": "cycle_regularity",
                "direction": "positive",
                "pl_basis": "sublimation chain_rate 2.4x distillation",
            },
            {
                "id": "S2_CHECKPOINT",
                "feature": "checkpoint_rate",
                "direction": "positive",
                "pl_basis": "sublimation monitoring_density 2.0x distillation",
            },
        ]

        exploratory_diagnostics = [
            {"id": "D1_OPAQUE", "feature": "opaque_close_fraction", "direction": "positive"},
            {"id": "D2_STRONG", "feature": "strong_close_fraction", "direction": "negative"},
            {"id": "D3_INTV", "feature": "intervention_frequency", "direction": "negative"},
            {"id": "D4_RECOV", "feature": "recovery_ops_count", "direction": "negative"},
        ]

        def run_prediction(pred, h_res, feature_dict, folio_list):
            """Run a single prediction test. Returns result dict."""
            feat_name = pred["feature"]
            positive = pred["direction"] == "positive"

            # Get valid folios (those with non-None feature values)
            valid = [(h_res[f], feature_dict[f][feat_name])
                     for f in folio_list
                     if feature_dict[f].get(feat_name) is not None]

            if len(valid) < 20:
                return {"id": pred["id"], "n": len(valid), "skip": True,
                        "reason": f"insufficient data (n={len(valid)})"}

            x = np.array([v[0] for v in valid])
            y = np.array([v[1] for v in valid])

            rho, p_one = spearman_one_sided(x, y, positive)
            passes = p_one < 0.05

            return {
                "id": pred["id"],
                "feature": feat_name,
                "predicted_direction": pred["direction"],
                "n": len(valid),
                "rho": float(rho),
                "p_one_sided": float(p_one),
                "pass": bool(passes),
                "pl_basis": pred.get("pl_basis", ""),
            }

        # Run primary battery
        print("\n=== PRIMARY PREDICTION BATTERY ===")
        primary_results = []
        for pred in primary_predictions:
            r = run_prediction(pred, h_resid_lookup, features, folios)
            primary_results.append(r)
            status = "PASS" if r.get("pass") else "FAIL"
            if r.get("skip"):
                status = "SKIP"
            print(f"  {r['id']}: rho={r.get('rho', 'N/A'):.4f}, "
                  f"p={r.get('p_one_sided', 'N/A'):.4f}, {status} (n={r['n']})")

        K = sum(1 for r in primary_results if r.get("pass"))
        print(f"\nPrimary passes: {K}/4")

        # Run secondary battery
        print("\n=== SECONDARY BATTERY ===")
        secondary_results = []
        for pred in secondary_predictions:
            r = run_prediction(pred, h_resid_lookup, features, folios)
            secondary_results.append(r)
            status = "PASS" if r.get("pass") else "FAIL"
            print(f"  {r['id']}: rho={r.get('rho', 'N/A'):.4f}, "
                  f"p={r.get('p_one_sided', 'N/A'):.4f}, {status} (n={r['n']})")

        # Run exploratory diagnostics
        print("\n=== EXPLORATORY DIAGNOSTICS ===")
        exploratory_results = []
        for pred in exploratory_diagnostics:
            r = run_prediction(pred, h_resid_lookup, features, folios)
            exploratory_results.append(r)
            print(f"  {r['id']}: rho={r.get('rho', 'N/A'):.4f}, "
                  f"p={r.get('p_one_sided', 'N/A'):.4f} (n={r['n']})")

        # ── 7. N1: Permutation Control ────────────────────────────────

        print("\n=== N1: PERMUTATION CONTROL ===")
        N_PERM = 1000
        rng = np.random.RandomState(42)

        perm_results = {}
        for pred, result in zip(primary_predictions, primary_results):
            if not result.get("pass"):
                continue

            feat_name = pred["feature"]
            positive = pred["direction"] == "positive"

            valid = [(h_resid_lookup[f], features[f][feat_name])
                     for f in folios
                     if features[f].get(feat_name) is not None]
            x_real = np.array([v[0] for v in valid])
            y_real = np.array([v[1] for v in valid])
            real_rho = abs(result["rho"])

            exceed_count = 0
            for _ in range(N_PERM):
                x_shuf = rng.permutation(x_real)
                rho_shuf, _ = stats.spearmanr(x_shuf, y_real)
                if abs(rho_shuf) >= real_rho:
                    exceed_count += 1

            frac = exceed_count / N_PERM
            survives = frac < 0.05

            perm_results[result["id"]] = {
                "real_abs_rho": float(real_rho),
                "fraction_exceeding": float(frac),
                "survives_permutation": bool(survives),
            }
            print(f"  {result['id']}: |rho|={real_rho:.4f}, "
                  f"frac_exceeding={frac:.3f}, {'SURVIVES' if survives else 'FAILS'}")

        K_perm = sum(1 for v in perm_results.values() if v["survives_permutation"])
        print(f"K_perm = {K_perm}")

        # ── 8. N2: Random Axis Control ────────────────────────────────

        print("\n=== N2: RANDOM AXIS CONTROL ===")
        rng2 = np.random.RandomState(123)
        random_axis = rng2.randn(n_folios)
        random_lookup = {folios[i]: random_axis[i] for i in range(n_folios)}

        n2_pass_count = 0
        n2_results = []
        for pred in primary_predictions:
            r = run_prediction(pred, random_lookup, features, folios)
            n2_results.append(r)
            if r.get("pass"):
                n2_pass_count += 1
            print(f"  {r['id']}: rho={r.get('rho', 'N/A'):.4f}, "
                  f"p={r.get('p_one_sided', 'N/A'):.4f}, "
                  f"{'PASS' if r.get('pass') else 'fail'}")

        n2_passes = n2_pass_count < 2
        print(f"Random axis passes: {n2_pass_count}/4 -> N2 {'PASS' if n2_passes else 'FAIL'}")

        # ── 9. N3: Wrong-Direction Check ──────────────────────────────

        print("\n=== N3: WRONG-DIRECTION CHECK ===")
        n3_results = {}
        for pred, result in zip(primary_predictions, primary_results):
            if not result.get("pass"):
                continue
            feat_name = pred["feature"]
            opposite = pred["direction"] != "positive"  # flip

            valid = [(h_resid_lookup[f], features[f][feat_name])
                     for f in folios
                     if features[f].get(feat_name) is not None]
            x = np.array([v[0] for v in valid])
            y = np.array([v[1] for v in valid])

            _, p_wrong = spearman_one_sided(x, y, opposite)
            flagged = p_wrong < 0.05

            n3_results[result["id"]] = {
                "wrong_direction_p": float(p_wrong),
                "flagged": bool(flagged),
            }
            print(f"  {result['id']}: wrong-dir p={p_wrong:.4f} {'FLAGGED' if flagged else 'ok'}")

        # ── 10. N4: Dissolution Contrast Diagnostic ───────────────────

        print("\n=== N4: DISSOLUTION CONTRAST ===")
        # Dissolution monitoring_density=0.58 < distillation=0.77
        # Sublimation=1.57 >> distillation=0.77
        # So dissolution is OPPOSITE direction from sublimation on monitoring axis
        # If dissolution predictions match sublimation's, the test is not family-specific
        #
        # Method: for each primary prediction, note whether the sublimation direction
        # matches what dissolution-vs-distillation would predict.

        dissolution_proto = prototypes["dissolution"]  # 7D
        distillation_proto = prototypes["distillation"]
        sublimation_proto = prototypes["sublimation"]

        # PL dimension mapping: 0=monitoring, 1=correction, 2=heat, 4=termination, 5=chain
        pl_dim_map = {
            "P1_TERM": 4,    # termination_rate
            "P2_ITER": 5,    # chain_rate
            "P3_HEAT_NEG": 2, # heat_rate
            "P4_THERMAL_NEG": 2, # heat_rate
        }

        n4_results = {}
        for pred, result in zip(primary_predictions, primary_results):
            dim_idx = pl_dim_map[pred["id"]]
            sub_val = sublimation_proto[dim_idx]
            dist_val = distillation_proto[dim_idx]
            diss_val = dissolution_proto[dim_idx]

            sub_direction = "positive" if sub_val > dist_val else "negative"
            diss_direction = "positive" if diss_val > dist_val else "negative"
            same = sub_direction == diss_direction

            n4_results[pred["id"]] = {
                "sublimation_value": float(sub_val),
                "dissolution_value": float(diss_val),
                "distillation_value": float(dist_val),
                "sublimation_direction": sub_direction,
                "dissolution_direction": diss_direction,
                "directions_match": bool(same),
            }
            print(f"  {pred['id']}: sub={sub_val:.2f} diss={diss_val:.2f} dist={dist_val:.2f} "
                  f"sub_dir={sub_direction} diss_dir={diss_direction} "
                  f"{'MATCH' if same else 'DIVERGE'}")

        n_diverge = sum(1 for v in n4_results.values() if not v["directions_match"])
        print(f"Dissolution diverges on {n_diverge}/4 predictions")

        # ── 11. Sensitivity Analyses ──────────────────────────────────

        print("\n=== SENSITIVITY: WITHIN-HERBAL ===")
        herbal_folios = [f for f in folios if features[f]["section"] == "H"]
        herbal_results = []
        for pred in primary_predictions:
            r = run_prediction(pred, h_resid_lookup, features, herbal_folios)
            herbal_results.append(r)
            if r.get("skip"):
                print(f"  {r['id']}: SKIP ({r.get('reason', 'n/a')})")
            else:
                print(f"  {r['id']}: rho={r['rho']:.4f}, "
                      f"p={r['p_one_sided']:.4f} (n={r['n']})")

        print("\n=== SENSITIVITY: RAW h_ratio ===")
        raw_h_lookup = {folios[i]: h_arr[i] for i in range(n_folios)}
        raw_results = []
        for pred in primary_predictions:
            r = run_prediction(pred, raw_h_lookup, features, folios)
            raw_results.append(r)
            if r.get("skip"):
                print(f"  {r['id']}: SKIP ({r.get('reason', 'n/a')})")
            else:
                print(f"  {r['id']}: rho={r['rho']:.4f}, "
                      f"p={r['p_one_sided']:.4f} (n={r['n']})")

        print("\n=== SENSITIVITY: SECTION + REGIME CONTROL ===")
        # Residualize h_ratio on section + REGIME + k_ratio
        regimes = [features[f]["regime"] for f in folios]
        unique_regimes = sorted(set(regimes))
        # Build expanded design matrix
        X2 = np.ones((n_folios, 4 + len(unique_regimes) - 1))
        for i in range(n_folios):
            X2[i, 1] = 1.0 if sections[i] == "S" else 0.0
            X2[i, 2] = 1.0 if sections[i] == "B" else 0.0
            X2[i, 3] = k_arr[i]
            for j, reg in enumerate(unique_regimes[1:]):  # skip first as reference
                X2[i, 4 + j] = 1.0 if regimes[i] == reg else 0.0

        beta2 = np.linalg.lstsq(X2, h_arr, rcond=None)[0]
        h_resid_regime = h_arr - X2 @ beta2
        h_resid_regime_lookup = {folios[i]: h_resid_regime[i] for i in range(n_folios)}

        regime_results = []
        for pred in primary_predictions:
            r = run_prediction(pred, h_resid_regime_lookup, features, folios)
            regime_results.append(r)
            if r.get("skip"):
                print(f"  {r['id']}: SKIP ({r.get('reason', 'n/a')})")
            else:
                print(f"  {r['id']}: rho={r['rho']:.4f}, "
                      f"p={r['p_one_sided']:.4f} (n={r['n']})")

        # ── 12. Verdict Determination ─────────────────────────────────

        if not n2_passes:
            verdict = "SPECIFICITY_FAILURE"
        elif K_perm >= 3:
            verdict = "FAMILY_CONTRAST_ALIGNMENT_CONFIRMED"
        elif K_perm == 2:
            verdict = "PARTIAL_FAMILY_CONTRAST"
        elif K_perm == 1:
            verdict = "WEAK_SIGNAL_ONLY"
        else:
            verdict = "FAMILY_CONTRAST_NOT_CONFIRMED"

        print(f"\n{'='*60}")
        print(f"Verdict: {verdict}")
        print(f"  Primary passes (K): {K}/4")
        print(f"  Permutation survivors (K_perm): {K_perm}")
        print(f"  N2 random axis: {'PASS' if n2_passes else 'FAIL'} ({n2_pass_count} passes)")
        print(f"{'='*60}")

        results["verdict"] = verdict
        results["primary_battery"] = primary_results
        results["secondary_battery"] = secondary_results
        results["exploratory"] = exploratory_results
        results["K"] = K
        results["K_perm"] = K_perm
        results["N1_permutation"] = perm_results
        results["N2_random_axis"] = {
            "pass": bool(n2_passes),
            "n_passes": n2_pass_count,
            "details": n2_results,
        }
        results["N3_wrong_direction"] = n3_results
        results["N4_dissolution"] = {
            "n_diverge": n_diverge,
            "details": n4_results,
        }
        results["sensitivity"] = {
            "within_herbal": herbal_results,
            "raw_h_ratio": raw_results,
            "section_regime_control": regime_results,
        }
        results["summary"] = {
            "n_primary_pass": K,
            "n_perm_survivors": K_perm,
            "n2_passes": bool(n2_passes),
            "tests": {r["id"]: "PASS" if r.get("pass") else "FAIL"
                      for r in primary_results},
        }

# ── 13. Write results ─────────────────────────────────────────────────

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

out_path = os.path.join(ROOT, "phases", "PROCEDURE_FAMILY_CONTRAST", "results",
                        "procedure_family_contrast_results.json")
with open(out_path, "w") as f:
    json.dump(convert_numpy(results), f, indent=2)
print(f"\nResults written to {out_path}")
print(f"VERDICT: {results.get('verdict', 'N/A')}")

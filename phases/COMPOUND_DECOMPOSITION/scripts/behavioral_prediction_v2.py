"""
COMPOUND DECOMPOSITION: Behavioral Prediction Test v2
======================================================
Addresses circularity concern: kernel assignments may be derived FROM
character content, making kernel features tautological.

Runs THREE variants:
  A. Full features (including kernel) — as before
  B. NO KERNEL features — purely behavioral (position, section, suffix, prefix)
  C. KERNEL ONLY — to measure how much kernel drives the result

Also adds prefix co-occurrence profile as a purely behavioral feature:
  what fraction of tokens with this MIDDLE use qo/ch/sh/da/ok/ot/ol/other prefix.
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
import random
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/COMPOUND_DECOMPOSITION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PREFIX_BINS = ["qo", "ch", "sh", "da", "sa", "ok", "ot", "ol", "other", "none"]


def compute_behavioral_profiles():
    """Compute per-MIDDLE behavioral profiles from raw token data."""
    tx = Transcript()
    morph = Morphology()
    mid_dict_raw = {}
    with open("data/middle_dictionary.json") as f:
        mid_dict_raw = json.load(f)["middles"]

    b_tokens = [t for t in tx.currier_b()
                if not t.is_label and not t.is_uncertain and t.word.strip()]

    # Normalized line positions
    line_groups = defaultdict(list)
    for token in b_tokens:
        line_groups[(token.folio, token.line)].append(token)

    token_positions = {}
    for (folio, line), toks in line_groups.items():
        n = len(toks)
        for idx, tok in enumerate(toks):
            token_positions[id(tok)] = idx / max(n - 1, 1)

    sections = sorted(set(t.section for t in b_tokens))
    tokens_by_middle = defaultdict(list)

    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue

        prefix = m.prefix if m.prefix else None
        prefix_bin = prefix if prefix in PREFIX_BINS[:-2] else ("none" if prefix is None else "other")

        kernel = mid_dict_raw.get(m.middle, {}).get("kernel", None)

        tokens_by_middle[m.middle].append({
            "norm_pos": token_positions.get(id(token), 0.5),
            "section": token.section,
            "line_initial": token.line_initial,
            "line_final": token.line_final,
            "par_initial": token.par_initial,
            "par_final": token.par_final,
            "has_suffix": m.suffix is not None,
            "has_articulator": m.has_articulator,
            "prefix_bin": prefix_bin,
            "kernel": kernel,
        })

    profiles = {}
    for mid, toks in tokens_by_middle.items():
        n = len(toks)
        if n < 5:
            continue

        mean_pos = sum(t["norm_pos"] for t in toks) / n
        sec_counts = Counter(t["section"] for t in toks)
        sec_vec = [sec_counts.get(s, 0) / n for s in sections]
        li_rate = sum(1 for t in toks if t["line_initial"]) / n
        lf_rate = sum(1 for t in toks if t["line_final"]) / n
        pi_rate = sum(1 for t in toks if t["par_initial"]) / n
        pf_rate = sum(1 for t in toks if t["par_final"]) / n
        sfx_rate = sum(1 for t in toks if t["has_suffix"]) / n
        art_rate = sum(1 for t in toks if t["has_articulator"]) / n

        # Prefix co-occurrence profile (purely behavioral)
        pfx_counts = Counter(t["prefix_bin"] for t in toks)
        pfx_vec = [pfx_counts.get(p, 0) / n for p in PREFIX_BINS]

        # Kernel profile (potentially circular)
        kernel = toks[0]["kernel"]
        k_vec = [0.0, 0.0, 0.0]
        if kernel:
            for ch in kernel:
                if ch == "K": k_vec[0] = 1.0
                elif ch == "E": k_vec[1] = 1.0
                elif ch == "H": k_vec[2] = 1.0

        profiles[mid] = {
            "n_tokens": n,
            # Behavioral (non-kernel)
            "mean_pos": mean_pos,
            "sec_vec": sec_vec,
            "li_rate": li_rate,
            "lf_rate": lf_rate,
            "pi_rate": pi_rate,
            "pf_rate": pf_rate,
            "sfx_rate": sfx_rate,
            "art_rate": art_rate,
            "pfx_vec": pfx_vec,
            # Kernel (potentially circular)
            "k_vec": k_vec,
        }

    return profiles, sections


def profile_to_vector(p, mode="full"):
    """Flatten profile to vector. mode: full, no_kernel, kernel_only."""
    behavioral = ([p["mean_pos"], p["li_rate"], p["lf_rate"],
                   p["pi_rate"], p["pf_rate"],
                   p["sfx_rate"], p["art_rate"]]
                  + p["sec_vec"] + p["pfx_vec"])
    kernel = p["k_vec"]

    if mode == "full":
        return behavioral + kernel
    elif mode == "no_kernel":
        return behavioral
    elif mode == "kernel_only":
        return kernel
    else:
        raise ValueError(f"Unknown mode: {mode}")


def vec_correlation(v1, v2):
    """Pearson correlation between two vectors."""
    n = len(v1)
    if n < 2:
        return 0.0
    m1 = sum(v1) / n
    m2 = sum(v2) / n
    num = sum((a - m1) * (b - m2) for a, b in zip(v1, v2))
    d1 = math.sqrt(sum((a - m1) ** 2 for a in v1))
    d2 = math.sqrt(sum((b - m2) ** 2 for b in v2))
    if d1 == 0 or d2 == 0:
        return 0.0
    return num / (d1 * d2)


def predict_compound(compound_mid, atom_profiles, mode="full"):
    """Predict compound profile by averaging atom profiles."""
    atom_vecs = []
    for ch in compound_mid:
        if ch in atom_profiles:
            atom_vecs.append(profile_to_vector(atom_profiles[ch], mode))
    if not atom_vecs:
        return None
    n = len(atom_vecs)
    return [sum(atom_vecs[j][i] for j in range(n)) / n
            for i in range(len(atom_vecs[0]))]


def run_permutation_test(all_test_mids, atom_profiles, mode, n_perms=1000):
    """Run permutation test for a given feature mode."""
    # Real score
    real_corrs = []
    for mid, actual in all_test_mids:
        predicted = predict_compound(mid, atom_profiles, mode)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual, mode)
        real_corrs.append(vec_correlation(predicted, actual_vec))

    real_mean = sum(real_corrs) / max(len(real_corrs), 1)

    # Permutations
    atom_keys = list(atom_profiles.keys())
    perm_scores = []
    random.seed(42)

    for _ in range(n_perms):
        shuffled = atom_keys[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(atom_keys, shuffled))
        perm_profs = {k: atom_profiles[perm_map[k]] for k in atom_keys}

        perm_corrs = []
        for mid, actual in all_test_mids:
            pred = predict_compound(mid, perm_profs, mode)
            if pred is None:
                continue
            actual_vec = profile_to_vector(actual, mode)
            perm_corrs.append(vec_correlation(pred, actual_vec))

        if perm_corrs:
            perm_scores.append(sum(perm_corrs) / len(perm_corrs))

    perm_mean = sum(perm_scores) / max(len(perm_scores), 1)
    perm_std = math.sqrt(sum((s - perm_mean) ** 2 for s in perm_scores)
                         / max(len(perm_scores), 1))
    n_better = sum(1 for s in perm_scores if s >= real_mean)
    p_value = n_better / max(len(perm_scores), 1)

    return {
        "real_mean": real_mean,
        "perm_mean": perm_mean,
        "perm_std": perm_std,
        "z_score": (real_mean - perm_mean) / max(perm_std, 0.0001),
        "n_better": n_better,
        "p_value": p_value,
        "n_test": len(real_corrs),
    }


def run_feature_correlations(all_test_mids, atom_profiles, sections, mode="no_kernel"):
    """Per-feature prediction accuracy."""
    if mode == "no_kernel":
        names = (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate",
                  "sfx_rate", "art_rate"]
                 + [f"sec_{s}" for s in sections]
                 + [f"pfx_{p}" for p in PREFIX_BINS])
    elif mode == "full":
        names = (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate",
                  "sfx_rate", "art_rate"]
                 + [f"sec_{s}" for s in sections]
                 + [f"pfx_{p}" for p in PREFIX_BINS]
                 + ["kernel_K", "kernel_E", "kernel_H"])
    else:
        names = ["kernel_K", "kernel_E", "kernel_H"]

    feature_pairs = {f: ([], []) for f in names}

    for mid, actual in all_test_mids:
        predicted = predict_compound(mid, atom_profiles, mode)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual, mode)
        for i, fname in enumerate(names):
            feature_pairs[fname][0].append(predicted[i])
            feature_pairs[fname][1].append(actual_vec[i])

    results = {}
    for fname in names:
        pred, act = feature_pairs[fname]
        r = vec_correlation(pred, act)
        results[fname] = r

    return results


def main():
    print("=" * 72)
    print("COMPOUND DECOMPOSITION: Behavioral Prediction Test v2")
    print("Circularity control: tests WITH and WITHOUT kernel features")
    print("=" * 72)
    print()

    profiles, sections = compute_behavioral_profiles()
    print(f"Behavioral profiles for {len(profiles)} MIDDLEs")
    print(f"Sections: {sections}")
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    test_mids = [(m, p) for m, p in profiles.items()
                 if len(m) >= 2 and all(ch in atom_profiles for ch in m)]

    print(f"Atoms (1-char): {len(atom_profiles)}")
    print(f"Testable compounds (2+ char, all atoms known): {len(test_mids)}")
    print()

    # === Variant A: Full features ===
    print("=" * 72)
    print("VARIANT A: ALL FEATURES (including kernel)")
    print("=" * 72)
    r_a = run_permutation_test(test_mids, atom_profiles, "full")
    print(f"  Real mean correlation:  {r_a['real_mean']:.4f}")
    print(f"  Permutation mean:       {r_a['perm_mean']:.4f} +/- {r_a['perm_std']:.4f}")
    print(f"  Z-score:                {r_a['z_score']:.2f}")
    print(f"  p-value:                {r_a['p_value']:.4f}  ({r_a['n_better']}/{1000})")
    print()

    # === Variant B: No kernel ===
    print("=" * 72)
    print("VARIANT B: NO KERNEL FEATURES (purely behavioral)")
    print("This is the circularity-free test.")
    print("=" * 72)
    r_b = run_permutation_test(test_mids, atom_profiles, "no_kernel")
    print(f"  Real mean correlation:  {r_b['real_mean']:.4f}")
    print(f"  Permutation mean:       {r_b['perm_mean']:.4f} +/- {r_b['perm_std']:.4f}")
    print(f"  Z-score:                {r_b['z_score']:.2f}")
    print(f"  p-value:                {r_b['p_value']:.4f}  ({r_b['n_better']}/{1000})")
    print()

    # === Variant C: Kernel only ===
    print("=" * 72)
    print("VARIANT C: KERNEL FEATURES ONLY (measuring circularity)")
    print("=" * 72)
    r_c = run_permutation_test(test_mids, atom_profiles, "kernel_only")
    print(f"  Real mean correlation:  {r_c['real_mean']:.4f}")
    print(f"  Permutation mean:       {r_c['perm_mean']:.4f} +/- {r_c['perm_std']:.4f}")
    print(f"  Z-score:                {r_c['z_score']:.2f}")
    print(f"  p-value:                {r_c['p_value']:.4f}  ({r_c['n_better']}/{1000})")
    print()

    # === Summary ===
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print()
    print(f"  {'Variant':30s} {'Real r':>8s} {'Perm r':>8s} {'Z':>6s} {'p':>8s}")
    print(f"  {'-'*30:30s} {'------':>8s} {'------':>8s} {'---':>6s} {'---':>8s}")
    print(f"  {'A: All features':30s} {r_a['real_mean']:8.4f} {r_a['perm_mean']:8.4f} {r_a['z_score']:6.2f} {r_a['p_value']:8.4f}")
    print(f"  {'B: No kernel (circularity-free)':30s} {r_b['real_mean']:8.4f} {r_b['perm_mean']:8.4f} {r_b['z_score']:6.2f} {r_b['p_value']:8.4f}")
    print(f"  {'C: Kernel only (circularity)':30s} {r_c['real_mean']:8.4f} {r_c['perm_mean']:8.4f} {r_c['z_score']:6.2f} {r_c['p_value']:8.4f}")
    print()

    if r_b['p_value'] < 0.01:
        print(">>> VARIANT B (circularity-free): HIGHLY SIGNIFICANT (p < 0.01)")
        print(">>> Compositionality is REAL and not driven by kernel circularity.")
    elif r_b['p_value'] < 0.05:
        print(">>> VARIANT B (circularity-free): SIGNIFICANT (p < 0.05)")
        print(">>> Compositionality holds without kernel features.")
    elif r_b['p_value'] < 0.10:
        print(">>> VARIANT B (circularity-free): MARGINAL (p < 0.10)")
    else:
        print(">>> VARIANT B (circularity-free): NOT SIGNIFICANT")
        print(">>> Compositionality may be driven entirely by kernel circularity.")

    print()

    # === Feature-by-feature (no-kernel mode) ===
    print("=" * 72)
    print("FEATURE-BY-FEATURE (no-kernel mode)")
    print("=" * 72)
    print()
    feat_corrs = run_feature_correlations(test_mids, atom_profiles, sections, "no_kernel")
    print(f"  {'Feature':15s} {'R':>7s}")
    print(f"  {'-'*15:15s} {'---':>7s}")
    for fname, r in sorted(feat_corrs.items(), key=lambda x: abs(x[1]), reverse=True):
        marker = " ***" if abs(r) > 0.4 else " **" if abs(r) > 0.3 else ""
        print(f"  {fname:15s} {r:7.3f}{marker}")

    # Save
    results = {
        "variant_a": r_a, "variant_b": r_b, "variant_c": r_c,
        "feature_correlations_no_kernel": feat_corrs,
        "n_atoms": len(atom_profiles),
        "n_testable": len(test_mids),
    }
    out_path = RESULTS_DIR / "behavioral_prediction_v2.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()

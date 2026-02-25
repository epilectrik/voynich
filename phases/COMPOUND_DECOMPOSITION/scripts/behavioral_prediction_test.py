"""
COMPOUND DECOMPOSITION: Behavioral Prediction Test
====================================================
Pre-registered test per expert recommendation:

  Given atom behavioral signatures derived ONLY from simple MIDDLEs (1-2 chars),
  predict the behavioral profiles of compound MIDDLEs (3+ chars) by combining
  atom signatures. Compare prediction accuracy to null model (random atom
  assignment via permutation).

  This tests the STRUCTURAL claim without relying on glosses at all.

Behavioral features (per-MIDDLE, measured from raw token data):
  1. Mean normalized line position (0.0 - 1.0)
  2. Section distribution vector (8 sections)
  3. Line-initial rate
  4. Line-final rate
  5. Suffix rate (fraction of tokens that have a suffix)
  6. Kernel profile vector (fraction of tokens with K, E, H kernel)

Prediction method:
  Compound profile = mean of atom profiles (order-independent baseline).
  Then: order-dependent model uses positional weighting.

Null model:
  Randomly permute atom-to-letter assignments 1000x and re-predict.
  Real assignment should predict better than 95% of permutations.
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


def load_regime_mapping():
    with open("data/regime_folio_mapping.json") as f:
        return json.load(f)


def load_middle_dict():
    with open("data/middle_dictionary.json") as f:
        return json.load(f)["middles"]


def compute_behavioral_profiles():
    """Compute per-MIDDLE behavioral profiles from raw token data."""
    tx = Transcript()
    morph = Morphology()
    regime_map = load_regime_mapping()
    mid_dict = load_middle_dict()

    # Collect all B tokens with morphology
    tokens_by_middle = defaultdict(list)
    line_token_counts = defaultdict(int)  # (folio, line) -> count
    line_token_positions = {}  # (folio, line, word) -> position

    # First pass: count tokens per line for normalization
    b_tokens = []
    for token in tx.currier_b():
        if token.is_label or token.is_uncertain:
            continue
        if not token.word.strip():
            continue
        b_tokens.append(token)

    # Group by folio+line for position computation
    line_groups = defaultdict(list)
    for token in b_tokens:
        line_groups[(token.folio, token.line)].append(token)

    # Assign normalized positions
    token_positions = {}
    for (folio, line), toks in line_groups.items():
        n = len(toks)
        for idx, tok in enumerate(toks):
            norm_pos = idx / max(n - 1, 1)
            token_positions[id(tok)] = norm_pos

    # Second pass: extract MIDDLE and collect behavioral data
    sections = sorted(set(t.section for t in b_tokens))
    section_idx = {s: i for i, s in enumerate(sections)}
    n_sections = len(sections)

    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue
        mid = m.middle
        norm_pos = token_positions.get(id(token), 0.5)

        # Kernel from dictionary
        kernel = mid_dict.get(mid, {}).get("kernel", None)

        tokens_by_middle[mid].append({
            "norm_pos": norm_pos,
            "section": token.section,
            "line_initial": token.line_initial,
            "line_final": token.line_final,
            "has_suffix": m.suffix is not None,
            "kernel": kernel,
            "folio": token.folio,
        })

    # Compute profiles
    profiles = {}
    for mid, toks in tokens_by_middle.items():
        n = len(toks)
        if n < 5:
            continue

        # Mean position
        mean_pos = sum(t["norm_pos"] for t in toks) / n

        # Section distribution
        sec_counts = Counter(t["section"] for t in toks)
        sec_vec = [sec_counts.get(s, 0) / n for s in sections]

        # Line boundary rates
        li_rate = sum(1 for t in toks if t["line_initial"]) / n
        lf_rate = sum(1 for t in toks if t["line_final"]) / n

        # Suffix rate
        sfx_rate = sum(1 for t in toks if t["has_suffix"]) / n

        # Kernel profile from dictionary (K/E/H/None proportions)
        kernel = toks[0]["kernel"]  # Same for all tokens of this MIDDLE
        k_vec = [0.0, 0.0, 0.0]  # K, E, H
        if kernel:
            for ch in kernel:
                if ch == "K":
                    k_vec[0] = 1.0
                elif ch == "E":
                    k_vec[1] = 1.0
                elif ch == "H":
                    k_vec[2] = 1.0

        profiles[mid] = {
            "n_tokens": n,
            "mean_pos": mean_pos,
            "sec_vec": sec_vec,
            "li_rate": li_rate,
            "lf_rate": lf_rate,
            "sfx_rate": sfx_rate,
            "k_vec": k_vec,
        }

    return profiles, sections


def profile_to_vector(p):
    """Flatten a profile into a single numeric vector for comparison."""
    v = [p["mean_pos"], p["li_rate"], p["lf_rate"], p["sfx_rate"]]
    v.extend(p["sec_vec"])
    v.extend(p["k_vec"])
    return v


def vec_distance(v1, v2):
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def vec_correlation(v1, v2):
    """Pearson correlation between two vectors."""
    n = len(v1)
    if n == 0:
        return 0.0
    m1 = sum(v1) / n
    m2 = sum(v2) / n
    num = sum((a - m1) * (b - m2) for a, b in zip(v1, v2))
    d1 = math.sqrt(sum((a - m1) ** 2 for a in v1))
    d2 = math.sqrt(sum((b - m2) ** 2 for b in v2))
    if d1 == 0 or d2 == 0:
        return 0.0
    return num / (d1 * d2)


def predict_compound(compound_mid, atom_profiles):
    """Predict a compound MIDDLE's profile by averaging its atom profiles."""
    atom_vecs = []
    for ch in compound_mid:
        if ch in atom_profiles:
            atom_vecs.append(profile_to_vector(atom_profiles[ch]))

    if not atom_vecs:
        return None

    # Average the atom vectors
    n = len(atom_vecs)
    avg = [sum(atom_vecs[j][i] for j in range(n)) / n
           for i in range(len(atom_vecs[0]))]
    return avg


def main():
    print("=" * 72)
    print("COMPOUND DECOMPOSITION: Behavioral Prediction Test")
    print("=" * 72)
    print()

    profiles, sections = compute_behavioral_profiles()
    print(f"Computed behavioral profiles for {len(profiles)} MIDDLEs")
    print(f"Sections: {sections}")
    print()

    # Split into atoms (1 char) and compounds (3+ chars)
    # 2-char MIDDLEs are ambiguous — could be atom or compound
    # Per expert: train on 1-2 char, predict 3+ char
    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    pair_profiles = {m: p for m, p in profiles.items() if len(m) == 2}
    compound_profiles = {m: p for m, p in profiles.items() if len(m) >= 3}

    print(f"Atoms (1-char):     {len(atom_profiles)}")
    print(f"Pairs (2-char):     {len(pair_profiles)}")
    print(f"Compounds (3+ char): {len(compound_profiles)}")
    print()

    # --- Test 1: Predict 2-char MIDDLEs from 1-char atoms ---
    print("=" * 72)
    print("TEST 1: Predict 2-char MIDDLE profiles from 1-char atom averages")
    print("=" * 72)
    print()

    pair_results = []
    for mid, actual in pair_profiles.items():
        predicted = predict_compound(mid, atom_profiles)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual)
        dist = vec_distance(predicted, actual_vec)
        corr = vec_correlation(predicted, actual_vec)
        pair_results.append((mid, actual["n_tokens"], dist, corr))

    pair_results.sort(key=lambda x: x[3], reverse=True)
    print(f"Testable 2-char MIDDLEs (all atoms known): {len(pair_results)}")
    mean_corr = sum(r[3] for r in pair_results) / max(len(pair_results), 1)
    mean_dist = sum(r[2] for r in pair_results) / max(len(pair_results), 1)
    print(f"Mean correlation (predicted vs actual): {mean_corr:.4f}")
    print(f"Mean distance (predicted vs actual):    {mean_dist:.4f}")
    print()

    print(f"  {'MIDDLE':8s} {'tokens':>6s} {'corr':>7s} {'dist':>7s}")
    print(f"  {'------':8s} {'------':>6s} {'----':>7s} {'----':>7s}")
    for mid, n, dist, corr in pair_results[:25]:
        marker = " ***" if corr > 0.8 else " **" if corr > 0.5 else ""
        print(f"  {mid:8s} {n:6d} {corr:7.3f} {dist:7.4f}{marker}")
    if len(pair_results) > 25:
        print(f"  ... ({len(pair_results) - 25} more)")
    print()

    # --- Test 2: Predict 3+ char MIDDLEs from 1-char atoms ---
    print("=" * 72)
    print("TEST 2: Predict 3+ char MIDDLE profiles from 1-char atom averages")
    print("=" * 72)
    print()

    compound_results = []
    for mid, actual in compound_profiles.items():
        predicted = predict_compound(mid, atom_profiles)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual)
        dist = vec_distance(predicted, actual_vec)
        corr = vec_correlation(predicted, actual_vec)
        compound_results.append((mid, actual["n_tokens"], dist, corr))

    compound_results.sort(key=lambda x: x[3], reverse=True)
    print(f"Testable 3+ char MIDDLEs (all atoms known): {len(compound_results)}")
    mean_corr_c = sum(r[3] for r in compound_results) / max(len(compound_results), 1)
    mean_dist_c = sum(r[2] for r in compound_results) / max(len(compound_results), 1)
    print(f"Mean correlation (predicted vs actual): {mean_corr_c:.4f}")
    print(f"Mean distance (predicted vs actual):    {mean_dist_c:.4f}")
    print()

    print(f"  {'MIDDLE':10s} {'tokens':>6s} {'corr':>7s} {'dist':>7s}")
    print(f"  {'------':10s} {'------':>6s} {'----':>7s} {'----':>7s}")
    for mid, n, dist, corr in compound_results[:30]:
        marker = " ***" if corr > 0.8 else " **" if corr > 0.5 else ""
        print(f"  {mid:10s} {n:6d} {corr:7.3f} {dist:7.4f}{marker}")
    if len(compound_results) > 30:
        print(f"  ... ({len(compound_results) - 30} more)")
    print()

    # --- Test 3: Permutation null model ---
    print("=" * 72)
    print("TEST 3: Permutation null model (1000 shuffles)")
    print("=" * 72)
    print()
    print("Randomly reassigning atom letter identities and re-predicting.")
    print("If real assignment beats 95%+ of permutations, composition is real.")
    print()

    all_test_mids = [(m, p) for m, p in pair_profiles.items()
                     if all(ch in atom_profiles for ch in m)]
    all_test_mids += [(m, p) for m, p in compound_profiles.items()
                      if all(ch in atom_profiles for ch in m)]

    if not all_test_mids:
        print("ERROR: No testable MIDDLEs found.")
        return

    # Real score
    real_corrs = []
    for mid, actual in all_test_mids:
        predicted = predict_compound(mid, atom_profiles)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual)
        corr = vec_correlation(predicted, actual_vec)
        real_corrs.append(corr)

    real_mean_corr = sum(real_corrs) / max(len(real_corrs), 1)

    # Permutation test
    atom_keys = list(atom_profiles.keys())
    n_perms = 1000
    perm_scores = []
    random.seed(42)

    for perm_i in range(n_perms):
        # Shuffle atom letter assignments
        shuffled_keys = atom_keys[:]
        random.shuffle(shuffled_keys)
        perm_map = dict(zip(atom_keys, shuffled_keys))

        # Build permuted atom profiles
        perm_profiles = {k: atom_profiles[perm_map[k]] for k in atom_keys
                         if perm_map[k] in atom_profiles}

        perm_corrs = []
        for mid, actual in all_test_mids:
            # Map compound characters through permutation
            perm_predicted = predict_compound(mid, perm_profiles)
            if perm_predicted is None:
                continue
            actual_vec = profile_to_vector(actual)
            corr = vec_correlation(perm_predicted, actual_vec)
            perm_corrs.append(corr)

        if perm_corrs:
            perm_scores.append(sum(perm_corrs) / len(perm_corrs))

    # Results
    perm_mean = sum(perm_scores) / max(len(perm_scores), 1)
    perm_std = math.sqrt(sum((s - perm_mean) ** 2 for s in perm_scores)
                         / max(len(perm_scores), 1))
    n_better = sum(1 for s in perm_scores if s >= real_mean_corr)
    p_value = n_better / max(len(perm_scores), 1)

    print(f"Testable compounds: {len(all_test_mids)}")
    print(f"Real mean correlation:        {real_mean_corr:.4f}")
    print(f"Permutation mean correlation: {perm_mean:.4f} +/- {perm_std:.4f}")
    print(f"Z-score:                      {(real_mean_corr - perm_mean) / max(perm_std, 0.0001):.2f}")
    print(f"Permutations beating real:    {n_better}/{len(perm_scores)}")
    print(f"p-value:                      {p_value:.4f}")
    print()

    if p_value < 0.01:
        print(">>> RESULT: HIGHLY SIGNIFICANT (p < 0.01)")
        print(">>> Atom composition predicts compound behavior better than chance.")
    elif p_value < 0.05:
        print(">>> RESULT: SIGNIFICANT (p < 0.05)")
        print(">>> Atom composition predicts compound behavior better than chance.")
    elif p_value < 0.10:
        print(">>> RESULT: MARGINAL (p < 0.10)")
        print(">>> Weak evidence for compositional prediction.")
    else:
        print(">>> RESULT: NOT SIGNIFICANT (p >= 0.10)")
        print(">>> Atom composition does NOT predict compound behavior.")

    print()

    # --- Test 4: Feature-by-feature breakdown ---
    print("=" * 72)
    print("TEST 4: Feature-by-feature prediction accuracy")
    print("=" * 72)
    print()
    print("Which behavioral features are best predicted by atom composition?")
    print()

    feature_names = ["mean_pos", "li_rate", "lf_rate", "sfx_rate"]
    feature_names += [f"sec_{s}" for s in sections]
    feature_names += ["kernel_K", "kernel_E", "kernel_H"]

    feature_corrs = {f: [] for f in feature_names}

    for mid, actual in all_test_mids:
        predicted = predict_compound(mid, atom_profiles)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual)
        for i, fname in enumerate(feature_names):
            feature_corrs[fname].append((predicted[i], actual_vec[i]))

    print(f"  {'Feature':15s} {'R':>7s} {'N':>5s}")
    print(f"  {'-------':15s} {'---':>7s} {'---':>5s}")
    for fname in feature_names:
        pairs = feature_corrs[fname]
        if not pairs:
            continue
        pred_vals = [p[0] for p in pairs]
        actual_vals = [p[1] for p in pairs]
        r = vec_correlation(pred_vals, actual_vals)
        print(f"  {fname:15s} {r:7.3f} {len(pairs):5d}")

    print()

    # --- Save results ---
    results = {
        "pair_results": [(m, n, d, c) for m, n, d, c in pair_results],
        "compound_results": [(m, n, d, c) for m, n, d, c in compound_results],
        "real_mean_corr": real_mean_corr,
        "perm_mean": perm_mean,
        "perm_std": perm_std,
        "p_value": p_value,
        "n_permutations": n_perms,
        "n_testable": len(all_test_mids),
    }
    out_path = RESULTS_DIR / "behavioral_prediction_test.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()

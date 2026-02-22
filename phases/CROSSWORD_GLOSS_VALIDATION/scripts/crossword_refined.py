"""
CROSSWORD GLOSS VALIDATION — Refined Analysis
===============================================
Addresses issues from initial run:
1. BCS penalizes high-frequency atoms — normalize by compound count
2. DPS is underpowered when averaging with other atoms — test atom isolation
3. T3 word overlap is too naive — use prediction error per atom instead

New tests:
  T1R: Per-atom prediction error (which atoms degrade predictions most?)
  T2R: c-divergence deep dive (why does c flip across positions?)
  T3R: Crossword constraint solver (for each atom, what gloss family
       would make ALL compounds work simultaneously?)

Output: phases/CROSSWORD_GLOSS_VALIDATION/results/crossword_refined.json
"""
import json
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/CROSSWORD_GLOSS_VALIDATION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PREFIX_BINS = ["qo", "ch", "sh", "da", "sa", "ok", "ot", "ol", "other", "none"]


def load_middle_dictionary():
    with open("data/middle_dictionary.json", encoding="utf-8") as f:
        return json.load(f)["middles"]


def vec_correlation(v1, v2):
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


def vec_mean(vecs):
    if not vecs:
        return None
    n = len(vecs)
    dim = len(vecs[0])
    return [sum(vecs[j][i] for j in range(n)) / n for i in range(dim)]


def vec_rmse(v1, v2):
    """Root mean squared error."""
    n = len(v1)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)) / n)


def compute_profiles():
    """Compute per-MIDDLE behavioral profiles (C1190 methodology)."""
    tx = Transcript()
    morph = Morphology()
    mid_dict = load_middle_dictionary()

    b_tokens = [t for t in tx.currier_b()
                if not t.is_label and not t.is_uncertain and t.word.strip()]

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
    # Also track per-character, per-position for T2R
    char_position_tokens = defaultdict(lambda: defaultdict(list))

    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue

        prefix = m.prefix if m.prefix else None
        prefix_bin = prefix if prefix in PREFIX_BINS[:-2] else (
            "none" if prefix is None else "other")

        tok_data = {
            "norm_pos": token_positions.get(id(token), 0.5),
            "section": token.section,
            "line_initial": token.line_initial,
            "line_final": token.line_final,
            "par_initial": token.par_initial,
            "par_final": token.par_final,
            "has_suffix": m.suffix is not None,
            "has_articulator": m.has_articulator,
            "prefix_bin": prefix_bin,
        }

        tokens_by_middle[m.middle].append(tok_data)

        # Track per-character positions
        for ch in m.middle:
            char_position_tokens[ch]["MIDDLE"].append(tok_data)
        if prefix:
            for ch in prefix:
                char_position_tokens[ch]["PREFIX"].append(tok_data)
        if m.suffix:
            for ch in m.suffix:
                char_position_tokens[ch]["SUFFIX"].append(tok_data)

    profiles = {}
    for mid, toks in tokens_by_middle.items():
        n = len(toks)
        if n < 5:
            continue
        profiles[mid] = _build_profile(toks, sections)

    return profiles, sections, char_position_tokens


def _build_profile(toks, sections):
    n = len(toks)
    mean_pos = sum(t["norm_pos"] for t in toks) / n
    sec_counts = Counter(t["section"] for t in toks)
    sec_vec = [sec_counts.get(s, 0) / n for s in sections]
    li_rate = sum(1 for t in toks if t["line_initial"]) / n
    lf_rate = sum(1 for t in toks if t["line_final"]) / n
    pi_rate = sum(1 for t in toks if t["par_initial"]) / n
    pf_rate = sum(1 for t in toks if t["par_final"]) / n
    sfx_rate = sum(1 for t in toks if t["has_suffix"]) / n
    art_rate = sum(1 for t in toks if t["has_articulator"]) / n
    pfx_counts = Counter(t["prefix_bin"] for t in toks)
    pfx_vec = [pfx_counts.get(p, 0) / n for p in PREFIX_BINS]

    return {
        "n_tokens": n,
        "vec": ([mean_pos, li_rate, lf_rate, pi_rate, pf_rate,
                 sfx_rate, art_rate] + sec_vec + pfx_vec),
    }


# ============================================================
# T1R: PER-ATOM PREDICTION ERROR
# ============================================================

def test_1r_prediction_error(profiles, sections):
    """For each compound, measure prediction error. Then attribute error
    to specific atoms — which atoms make predictions WORSE?

    Method:
      1. For each compound C with atoms {A1, A2, ...}:
         prediction = mean(profile(A1), profile(A2), ...)
         error = RMSE(prediction, actual)
      2. For each atom A, compute:
         mean_error_with_A = mean error of compounds containing A
         mean_error_without_A = mean error of compounds NOT containing A
         error_delta = with - without
      3. Atoms with POSITIVE error_delta make predictions worse
         (their profile doesn't compose well with others)
    """
    print("=" * 72)
    print("T1R: PER-ATOM PREDICTION ERROR ATTRIBUTION")
    print("Which atoms degrade compound predictions the most?")
    print("(Circularity-free: no glosses used)")
    print("=" * 72)
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    atom_keys = sorted(atom_profiles.keys())

    # Compute prediction error for each testable compound
    compound_errors = {}
    for mid, prof in profiles.items():
        if len(mid) < 2:
            continue
        if not all(ch in atom_profiles for ch in mid):
            continue

        # Predict from atoms
        atom_vecs = [atom_profiles[ch]["vec"] for ch in mid]
        predicted = vec_mean(atom_vecs)
        actual = prof["vec"]
        error = vec_rmse(predicted, actual)
        compound_errors[mid] = error

    if not compound_errors:
        print("  No testable compounds found!")
        return {}

    global_mean_error = sum(compound_errors.values()) / len(compound_errors)
    print(f"  Global mean prediction RMSE: {global_mean_error:.4f}")
    print(f"  Testable compounds: {len(compound_errors)}")
    print()

    # Per-atom error attribution
    results = {}
    for atom in atom_keys:
        with_atom = [e for mid, e in compound_errors.items() if atom in mid]
        without_atom = [e for mid, e in compound_errors.items()
                        if atom not in mid]

        if not with_atom or not without_atom:
            results[atom] = {"error_delta": None, "status": "INSUFFICIENT"}
            continue

        mean_with = sum(with_atom) / len(with_atom)
        mean_without = sum(without_atom) / len(without_atom)
        delta = mean_with - mean_without

        results[atom] = {
            "mean_error_with": round(mean_with, 5),
            "mean_error_without": round(mean_without, 5),
            "error_delta": round(delta, 5),
            "n_compounds_with": len(with_atom),
            "n_compounds_without": len(without_atom),
            "status": ("GOOD" if delta <= 0 else
                       "ACCEPTABLE" if delta < 0.005 else
                       "DEGRADING" if delta < 0.015 else
                       "PROBLEMATIC")
        }

    # Null test: permute and compute deltas
    random.seed(42)
    null_deltas = defaultdict(list)
    for _ in range(500):
        shuffled = atom_keys[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(atom_keys, shuffled))
        perm_profs = {k: atom_profiles[perm_map[k]] for k in atom_keys}

        perm_errors = {}
        for mid, prof in profiles.items():
            if len(mid) < 2 or mid not in compound_errors:
                continue
            atom_vecs = [perm_profs.get(ch, atom_profiles.get(ch, {})).get(
                "vec", [0]*22) for ch in mid]
            if any(len(v) != len(prof["vec"]) for v in atom_vecs):
                continue
            predicted = vec_mean(atom_vecs)
            perm_errors[mid] = vec_rmse(predicted, prof["vec"])

        for atom in atom_keys:
            with_a = [e for m, e in perm_errors.items() if atom in m]
            without_a = [e for m, e in perm_errors.items() if atom not in m]
            if with_a and without_a:
                d = sum(with_a)/len(with_a) - sum(without_a)/len(without_a)
                null_deltas[atom].append(d)

    # Add null percentile
    for atom in results:
        if results[atom]["error_delta"] is None:
            results[atom]["null_percentile"] = None
            continue
        null_d = null_deltas.get(atom, [])
        if not null_d:
            results[atom]["null_percentile"] = None
            continue
        real_d = results[atom]["error_delta"]
        # Lower delta is better, so percentile = fraction of null WORSE than real
        pct = sum(1 for d in null_d if d > real_d) / len(null_d)
        results[atom]["null_percentile"] = round(pct * 100, 1)

    # Display
    mid_dict = load_middle_dictionary()
    print(f"  {'Atom':4s} {'Gloss':12s} {'ErrWith':>8s} {'ErrW/o':>8s} "
          f"{'Delta':>8s} {'Null%':>6s} {'N':>4s} {'Status':14s}")
    print(f"  {'----':4s} {'-----':12s} {'-------':>8s} {'------':>8s} "
          f"{'-----':>8s} {'-----':>6s} {'--':>4s} {'------':14s}")

    for atom in sorted(results.keys(),
                       key=lambda x: results[x].get("error_delta") or 99):
        r = results[atom]
        gloss = mid_dict.get(atom, {}).get("gloss") or "?"
        if r["error_delta"] is None:
            print(f"  {atom:4s} {gloss:12s} {'N/A':>8s} {'N/A':>8s} "
                  f"{'N/A':>8s} {'N/A':>6s} {'0':>4s} {r['status']:14s}")
        else:
            null_str = (f"{r['null_percentile']:5.1f}"
                        if r.get('null_percentile') is not None else "  N/A")
            print(f"  {atom:4s} {gloss:12s} "
                  f"{r['mean_error_with']:8.5f} "
                  f"{r['mean_error_without']:8.5f} "
                  f"{r['error_delta']:+8.5f} "
                  f"{null_str:>6s} "
                  f"{r['n_compounds_with']:4d} {r['status']:14s}")

    print()

    # Show worst compounds (highest prediction error)
    print("  WORST-PREDICTED COMPOUNDS (top 15 by RMSE):")
    sorted_errors = sorted(compound_errors.items(), key=lambda x: x[1],
                           reverse=True)[:15]
    for mid, err in sorted_errors:
        gloss = mid_dict.get(mid, {}).get("gloss") or "?"
        atoms_str = "+".join(mid)
        toks = mid_dict.get(mid, {}).get("token_count", 0)
        print(f"    {mid:10s} RMSE={err:.4f}  ({toks:4d} tokens)  "
              f"\"{gloss}\"  [{atoms_str}]")

    print()
    return results


# ============================================================
# T2R: c-DIVERGENCE DEEP DIVE
# ============================================================

def test_2r_c_divergence(char_position_tokens, sections):
    """Investigate why 'c' has DIVERGENT cross-position behavior.

    Compare behavioral profiles of 'c' in PREFIX vs MIDDLE positions.
    Identify which features diverge most.
    """
    print("=" * 72)
    print("T2R: CROSS-POSITION DIVERGENCE ANALYSIS")
    print("For atoms with DIVERGENT/MODERATE cross-position behavior,")
    print("which behavioral features cause the divergence?")
    print("=" * 72)
    print()

    feature_names = (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate"]
                     + [f"sec_{s}" for s in sections])

    divergent_chars = ['c', 'p', 'f']  # From T2 results

    results = {}
    for ch in divergent_chars:
        positions = char_position_tokens.get(ch, {})
        if len(positions) < 2:
            continue

        print(f"  CHARACTER '{ch}':")
        pos_profiles = {}
        for pos_name, toks in positions.items():
            if len(toks) < 10:
                continue
            n = len(toks)
            mean_pos = sum(t["norm_pos"] for t in toks) / n
            sec_counts = Counter(t["section"] for t in toks)
            sec_vec = [sec_counts.get(s, 0) / n for s in sections]
            li_rate = sum(1 for t in toks if t["line_initial"]) / n
            lf_rate = sum(1 for t in toks if t["line_final"]) / n
            pi_rate = sum(1 for t in toks if t["par_initial"]) / n
            pf_rate = sum(1 for t in toks if t["par_final"]) / n

            pos_profiles[pos_name] = {
                "n": n,
                "vec": [mean_pos, li_rate, lf_rate, pi_rate, pf_rate]
                       + sec_vec,
            }
            print(f"    {pos_name:8s} (n={n:5d}): "
                  f"pos={mean_pos:.3f} li={li_rate:.3f} lf={lf_rate:.3f}")

        # Feature-by-feature comparison
        if "PREFIX" in pos_profiles and "MIDDLE" in pos_profiles:
            p_vec = pos_profiles["PREFIX"]["vec"]
            m_vec = pos_profiles["MIDDLE"]["vec"]

            print(f"\n    Feature differences (PREFIX - MIDDLE):")
            print(f"    {'Feature':12s} {'PREFIX':>8s} {'MIDDLE':>8s} "
                  f"{'Delta':>8s}")
            print(f"    {'-------':12s} {'------':>8s} {'------':>8s} "
                  f"{'-----':>8s}")

            feature_deltas = {}
            for i, fname in enumerate(feature_names):
                delta = p_vec[i] - m_vec[i]
                feature_deltas[fname] = {
                    "prefix": round(p_vec[i], 4),
                    "middle": round(m_vec[i], 4),
                    "delta": round(delta, 4),
                }
                marker = " ***" if abs(delta) > 0.1 else \
                         " **" if abs(delta) > 0.05 else ""
                print(f"    {fname:12s} {p_vec[i]:8.4f} {m_vec[i]:8.4f} "
                      f"{delta:+8.4f}{marker}")

            results[ch] = {
                "positions": {k: v["n"]
                              for k, v in pos_profiles.items()},
                "feature_deltas": feature_deltas,
            }

        print()

    return results


# ============================================================
# T3R: CROSSWORD CONSTRAINT ENUMERATION
# ============================================================

def test_3r_crossword_constraints(profiles, mid_dict, sections):
    """For each atom, enumerate ALL compounds it appears in and what
    the other atoms' glosses constrain it to mean.

    This is the human-evaluable crossword board: for each atom,
    show what meaning would make ALL its compounds work simultaneously.
    """
    print("=" * 72)
    print("T3R: CROSSWORD CONSTRAINT BOARD")
    print("For each atom: what compounds constrain its meaning?")
    print("Focus on atoms with uncertain glosses.")
    print("=" * 72)
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    priority_atoms = ['o', 'c', 'a', 'n', 'l', 'r', 'i', 'd', 's', 'p',
                      'm', 'f', 'k', 'e', 'h', 'y', 't']

    results = {}
    for atom in priority_atoms:
        if atom not in atom_profiles:
            continue

        gloss = mid_dict.get(atom, {}).get("gloss") or "?"

        # Find all glossed compounds containing this atom
        compounds = []
        for mid, info in mid_dict.items():
            if len(mid) < 2 or atom not in mid:
                continue
            if not info.get("gloss"):
                continue
            tc = info.get("token_count", 0)
            if tc < 5:
                continue

            other_atoms = []
            for ch in mid:
                if ch != atom:
                    other_gloss = mid_dict.get(ch, {}).get("gloss") or "?"
                    other_atoms.append((ch, other_gloss))

            compounds.append({
                "compound": mid,
                "compound_gloss": info["gloss"],
                "tokens": tc,
                "other_atoms": other_atoms,
            })

        compounds.sort(key=lambda x: x["tokens"], reverse=True)

        if not compounds:
            continue

        print(f"  ATOM '{atom}' (current gloss: \"{gloss}\", "
              f"{mid_dict.get(atom, {}).get('token_count', 0)} tokens)")
        print(f"  Appears in {len(compounds)} glossed compounds.")
        print(f"  What single meaning for '{atom}' makes ALL these work?\n")

        print(f"    {'Compound':10s} {'Tokens':>5s}  {'Compound Gloss':18s}  "
              f"{'Other Atoms':30s}  {'Need from {atom}'}")
        print(f"    {'--------':10s} {'-----':>5s}  {'-----':18s}  "
              f"{'-----':30s}  {'-----'}")

        for c in compounds[:20]:
            others = ", ".join(f"{ch}={g}" for ch, g in c["other_atoms"])
            if len(others) > 30:
                others = others[:27] + "..."

            # What does atom need to mean for this compound to work?
            other_glosses = [g for _, g in c["other_atoms"]]
            need = f"{c['compound_gloss']} minus [{', '.join(other_glosses)}]"
            if len(need) > 35:
                need = need[:32] + "..."

            print(f"    {c['compound']:10s} {c['tokens']:5d}  "
                  f"{c['compound_gloss']:18s}  {others:30s}  {need}")

        print()
        results[atom] = {
            "current_gloss": gloss,
            "n_compounds": len(compounds),
            "compounds": compounds,
        }

    return results


# ============================================================
# BEHAVIORAL FEATURE RANKING
# ============================================================

def test_feature_ranking(profiles, sections):
    """Which behavioral features best discriminate between atoms?

    For each feature, compute the variance across atom profiles.
    High-variance features are the most discriminative.
    """
    print("=" * 72)
    print("BEHAVIORAL FEATURE RANKING")
    print("Which features most distinguish atoms from each other?")
    print("=" * 72)
    print()

    feature_names = (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate",
                      "sfx_rate", "art_rate"]
                     + [f"sec_{s}" for s in sections]
                     + [f"pfx_{p}" for p in PREFIX_BINS])

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}

    # Compute per-feature variance across atoms
    feature_vars = {}
    for i, fname in enumerate(feature_names):
        values = [p["vec"][i] for p in atom_profiles.values()]
        mean_val = sum(values) / len(values)
        var = sum((v - mean_val) ** 2 for v in values) / len(values)
        feature_vars[fname] = {
            "variance": round(var, 6),
            "mean": round(mean_val, 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "range": round(max(values) - min(values), 4),
        }

    print(f"  {'Feature':15s} {'Variance':>10s} {'Range':>8s} "
          f"{'Min':>8s} {'Max':>8s} {'Mean':>8s}")
    print(f"  {'-------':15s} {'--------':>10s} {'-----':>8s} "
          f"{'---':>8s} {'---':>8s} {'----':>8s}")

    for fname in sorted(feature_vars.keys(),
                        key=lambda x: feature_vars[x]["variance"],
                        reverse=True):
        fv = feature_vars[fname]
        print(f"  {fname:15s} {fv['variance']:10.6f} {fv['range']:8.4f} "
              f"{fv['min']:8.4f} {fv['max']:8.4f} {fv['mean']:8.4f}")

    print()

    # Show atom profiles on top 5 discriminative features
    top_features = sorted(feature_vars.keys(),
                          key=lambda x: feature_vars[x]["variance"],
                          reverse=True)[:7]

    print("  ATOM PROFILES ON TOP DISCRIMINATIVE FEATURES:")
    header = f"  {'Atom':4s} {'Gloss':12s} {'Toks':>5s}"
    for f in top_features:
        header += f" {f:>8s}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    mid_dict = load_middle_dictionary()
    for atom in sorted(atom_profiles.keys(),
                       key=lambda x: atom_profiles[x]["n_tokens"],
                       reverse=True):
        gloss = mid_dict.get(atom, {}).get("gloss") or "?"
        toks = atom_profiles[atom]["n_tokens"]
        line = f"  {atom:4s} {gloss:12s} {toks:5d}"
        for f in top_features:
            idx = feature_names.index(f)
            val = atom_profiles[atom]["vec"][idx]
            line += f" {val:8.3f}"
        print(line)

    print()
    return feature_vars


# ============================================================
# ATOM SIMILARITY CLUSTERS
# ============================================================

def test_atom_clusters(profiles):
    """Compute pairwise similarity between atoms to find natural clusters.

    Atoms in the same cluster have similar behavioral profiles —
    if two atoms cluster together but have very different glosses,
    one may be wrong.
    """
    print("=" * 72)
    print("ATOM SIMILARITY MATRIX")
    print("Which atoms behave most similarly? Clusters may indicate")
    print("shared function or gloss errors.")
    print("=" * 72)
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    atoms = sorted(atom_profiles.keys(),
                   key=lambda x: atom_profiles[x]["n_tokens"],
                   reverse=True)

    mid_dict = load_middle_dictionary()

    # Pairwise correlations
    sim_matrix = {}
    for a1 in atoms:
        for a2 in atoms:
            if a1 >= a2:
                continue
            r = vec_correlation(atom_profiles[a1]["vec"],
                                atom_profiles[a2]["vec"])
            sim_matrix[(a1, a2)] = round(r, 3)

    # Show top similar pairs
    top_pairs = sorted(sim_matrix.items(), key=lambda x: x[1], reverse=True)

    print("  TOP SIMILAR ATOM PAIRS (r > 0.8):")
    print(f"  {'Pair':10s} {'r':>6s}  {'Gloss A':12s} {'Gloss B':12s}  "
          f"{'Same gloss?'}")
    print(f"  {'----':10s} {'--':>6s}  {'-------':12s} {'-------':12s}  "
          f"{'----------'}")

    for (a1, a2), r in top_pairs:
        if r < 0.8:
            break
        g1 = mid_dict.get(a1, {}).get("gloss") or "?"
        g2 = mid_dict.get(a2, {}).get("gloss") or "?"
        same = "SIMILAR" if g1 == g2 else "DIFFERENT"
        print(f"  {a1+'-'+a2:10s} {r:6.3f}  {g1:12s} {g2:12s}  {same}")

    print()

    # Show most DISSIMILAR pairs (potential opposites)
    print("  TOP DISSIMILAR ATOM PAIRS (r < 0.0):")
    bottom_pairs = sorted(sim_matrix.items(), key=lambda x: x[1])
    for (a1, a2), r in bottom_pairs:
        if r >= 0.0:
            break
        g1 = mid_dict.get(a1, {}).get("gloss") or "?"
        g2 = mid_dict.get(a2, {}).get("gloss") or "?"
        print(f"  {a1+'-'+a2:10s} {r:6.3f}  {g1:12s} {g2:12s}")

    print()

    # Find each atom's nearest neighbor
    print("  NEAREST NEIGHBOR FOR EACH ATOM:")
    print(f"  {'Atom':4s} {'Gloss':12s} {'NN':4s} {'NN Gloss':12s} "
          f"{'r':>6s}  {'Implication'}")
    print(f"  {'----':4s} {'-----':12s} {'--':4s} {'--------':12s} "
          f"{'--':>6s}  {'----------'}")

    for atom in atoms:
        best_nn = None
        best_r = -1
        for other in atoms:
            if other == atom:
                continue
            key = (min(atom, other), max(atom, other))
            r = sim_matrix.get(key, 0)
            if r > best_r:
                best_r = r
                best_nn = other

        g_atom = mid_dict.get(atom, {}).get("gloss") or "?"
        g_nn = mid_dict.get(best_nn, {}).get("gloss") or "?"

        impl = ""
        if best_r > 0.95:
            impl = "NEAR-IDENTICAL profiles"
        elif best_r > 0.9:
            impl = "very similar"
        elif best_r > 0.8:
            impl = "similar"

        print(f"  {atom:4s} {g_atom:12s} {best_nn:4s} {g_nn:12s} "
              f"{best_r:6.3f}  {impl}")

    print()
    return sim_matrix


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 72)
    print("CROSSWORD GLOSS VALIDATION — Refined Analysis")
    print("=" * 72)
    print()

    mid_dict = load_middle_dictionary()

    print("Computing behavioral profiles...")
    profiles, sections, char_pos_tokens = compute_profiles()
    print(f"  Profiles: {len(profiles)} MIDDLEs")
    atom_count = sum(1 for m in profiles if len(m) == 1)
    compound_count = sum(1 for m in profiles if len(m) >= 2)
    print(f"  Atoms: {atom_count}, Compounds: {compound_count}")
    print()

    # Run refined tests
    t1r = test_1r_prediction_error(profiles, sections)
    t2r = test_2r_c_divergence(char_pos_tokens, sections)
    feat = test_feature_ranking(profiles, sections)
    clusters = test_atom_clusters(profiles)
    t3r = test_3r_crossword_constraints(profiles, mid_dict, sections)

    # Save
    results = {
        "t1r_prediction_error": t1r,
        "t2r_divergence": t2r,
        "feature_ranking": feat,
        "atom_clusters": {f"{a}-{b}": r for (a, b), r in clusters.items()},
        "t3r_constraints": {
            k: {"current_gloss": v["current_gloss"],
                "n_compounds": v["n_compounds"]}
            for k, v in t3r.items()
        },
    }

    out_path = RESULTS_DIR / "crossword_refined.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()

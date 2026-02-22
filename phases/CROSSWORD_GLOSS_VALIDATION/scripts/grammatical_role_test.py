"""
GRAMMATICAL ROLE SHIFT TEST — Phase 422
========================================
Tests whether atoms systematically shift behavioral profiles between
MIDDLE position (verb/active) and PREFIX position (modifier/adjective).

Hypothesis: Morphological position selects grammatical role. Atoms in
MIDDLE act as verbs ("heat", "stabilize"), atoms in PREFIX act as
modifiers ("hot/heated", "stable"). If this shift is SYSTEMATIC across
atoms, it's a grammatical rule (promotable to Tier 2).

Method:
  1. For each atom appearing in both PREFIX and MIDDLE positions,
     compute the behavioral shift vector: PREFIX_profile - MIDDLE_profile
  2. Test whether shift vectors are CORRELATED across atoms
     (systematic shift = grammatical rule) vs UNCORRELATED (random = no rule)
  3. Null test: permute atom-position assignments, compare correlation

Also tests SUFFIX position where data is available.

Output: phases/CROSSWORD_GLOSS_VALIDATION/results/grammatical_role_test.json
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


def compute_position_profiles():
    """Compute per-character, per-position behavioral profiles."""
    tx = Transcript()
    morph = Morphology()

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

    # Collect tokens by character AND morphological position
    char_pos_tokens = defaultdict(lambda: defaultdict(list))

    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue

        tok_data = {
            "norm_pos": token_positions.get(id(token), 0.5),
            "section": token.section,
            "line_initial": token.line_initial,
            "line_final": token.line_final,
            "par_initial": token.par_initial,
            "par_final": token.par_final,
            "has_suffix": m.suffix is not None,
            "has_articulator": m.has_articulator,
        }

        # Track by morphological position
        for ch in m.middle:
            char_pos_tokens[ch]["MIDDLE"].append(tok_data)
        if m.prefix:
            for ch in m.prefix:
                char_pos_tokens[ch]["PREFIX"].append(tok_data)
        if m.suffix:
            for ch in m.suffix:
                char_pos_tokens[ch]["SUFFIX"].append(tok_data)

    return char_pos_tokens, sections


def build_profile_vec(toks, sections):
    """Build shared-feature profile vector for cross-position comparison.
    Uses features that are meaningful across all positions."""
    n = len(toks)
    if n < 10:
        return None

    mean_pos = sum(t["norm_pos"] for t in toks) / n
    li_rate = sum(1 for t in toks if t["line_initial"]) / n
    lf_rate = sum(1 for t in toks if t["line_final"]) / n
    pi_rate = sum(1 for t in toks if t["par_initial"]) / n
    pf_rate = sum(1 for t in toks if t["par_final"]) / n
    sfx_rate = sum(1 for t in toks if t["has_suffix"]) / n
    sec_counts = Counter(t["section"] for t in toks)
    sec_vec = [sec_counts.get(s, 0) / n for s in sections]

    return [mean_pos, li_rate, lf_rate, pi_rate, pf_rate, sfx_rate] + sec_vec


def main():
    print("=" * 72)
    print("GRAMMATICAL ROLE SHIFT TEST — Phase 422")
    print("Do atoms systematically shift behavior between positions?")
    print("=" * 72)
    print()

    char_pos_tokens, sections = compute_position_profiles()

    feature_names = (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate",
                      "sfx_rate"]
                     + [f"sec_{s}" for s in sections])

    # ================================================================
    # PART 1: Compute shift vectors (PREFIX - MIDDLE) for each atom
    # ================================================================
    print("PART 1: PREFIX->MIDDLE SHIFT VECTORS")
    print("-" * 72)

    shift_vectors = {}
    atom_profiles_by_pos = {}

    with open("data/middle_dictionary.json", encoding="utf-8") as f:
        mid_dict = json.load(f)["middles"]

    for ch in sorted(char_pos_tokens.keys()):
        positions = char_pos_tokens[ch]
        mid_toks = positions.get("MIDDLE", [])
        pfx_toks = positions.get("PREFIX", [])

        mid_vec = build_profile_vec(mid_toks, sections)
        pfx_vec = build_profile_vec(pfx_toks, sections)

        if mid_vec is None or pfx_vec is None:
            continue

        shift = [p - m for p, m in zip(pfx_vec, mid_vec)]
        shift_vectors[ch] = shift
        atom_profiles_by_pos[ch] = {"MIDDLE": mid_vec, "PREFIX": pfx_vec}

    print(f"  Atoms with both PREFIX and MIDDLE profiles: {len(shift_vectors)}")
    print()

    # Display shift vectors
    gloss_lookup = lambda ch: mid_dict.get(ch, {}).get("gloss") or "?"

    header = f"  {'Atom':4s} {'Gloss':10s}"
    for f in feature_names:
        header += f" {f[:7]:>8s}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for ch in sorted(shift_vectors.keys(),
                     key=lambda x: len(char_pos_tokens[x].get("PREFIX", [])),
                     reverse=True):
        sv = shift_vectors[ch]
        n_pfx = len(char_pos_tokens[ch].get("PREFIX", []))
        n_mid = len(char_pos_tokens[ch].get("MIDDLE", []))
        line = f"  {ch:4s} {gloss_lookup(ch):10s}"
        for val in sv:
            marker = "*" if abs(val) > 0.1 else " "
            line += f" {val:+7.3f}{marker}"
        print(line + f"  (P:{n_pfx} M:{n_mid})")

    print()

    # ================================================================
    # PART 2: Pairwise correlation of shift vectors
    # ================================================================
    print("PART 2: SYSTEMATIC SHIFT TEST")
    print("Are shift vectors correlated across atoms?")
    print("High correlation = systematic grammatical rule")
    print("Low correlation = random per-atom variation")
    print("-" * 72)

    atoms = sorted(shift_vectors.keys())
    n_atoms = len(atoms)

    if n_atoms < 3:
        print("  Not enough atoms for systematic test!")
        return

    # Pairwise correlations of shift vectors
    pair_corrs = []
    pair_labels = []
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            r = vec_correlation(shift_vectors[atoms[i]],
                                shift_vectors[atoms[j]])
            pair_corrs.append(r)
            pair_labels.append(f"{atoms[i]}-{atoms[j]}")

    mean_corr = sum(pair_corrs) / len(pair_corrs)
    median_corr = sorted(pair_corrs)[len(pair_corrs) // 2]

    print(f"  Atom pairs tested: {len(pair_corrs)}")
    print(f"  Mean pairwise shift correlation: {mean_corr:.4f}")
    print(f"  Median pairwise shift correlation: {median_corr:.4f}")
    print()

    # Show top correlated shift pairs (shift in same direction)
    sorted_pairs = sorted(zip(pair_labels, pair_corrs),
                          key=lambda x: x[1], reverse=True)

    print("  TOP CORRELATED SHIFTS (atoms shift the SAME way):")
    for label, r in sorted_pairs[:10]:
        a1, a2 = label.split("-")
        print(f"    {label:6s}  r={r:+.3f}  ({gloss_lookup(a1):10s} "
              f"<> {gloss_lookup(a2):10s})")

    print()
    print("  TOP ANTI-CORRELATED SHIFTS (atoms shift OPPOSITE ways):")
    for label, r in sorted_pairs[-5:]:
        a1, a2 = label.split("-")
        print(f"    {label:6s}  r={r:+.3f}  ({gloss_lookup(a1):10s} "
              f"<> {gloss_lookup(a2):10s})")
    print()

    # ================================================================
    # PART 3: Null distribution
    # ================================================================
    print("PART 3: NULL DISTRIBUTION")
    print("Permutation test: shuffle position assignments per atom")
    print("-" * 72)

    random.seed(42)
    null_means = []
    n_perms = 1000

    for _ in range(n_perms):
        # For each atom, randomly swap PREFIX/MIDDLE assignment
        null_shifts = {}
        for ch in atoms:
            mid_toks = char_pos_tokens[ch].get("MIDDLE", [])
            pfx_toks = char_pos_tokens[ch].get("PREFIX", [])
            combined = mid_toks + pfx_toks
            random.shuffle(combined)
            # Split randomly into two groups of same sizes
            n_mid = len(mid_toks)
            group_a = combined[:n_mid]
            group_b = combined[n_mid:]

            vec_a = build_profile_vec(group_a, sections)
            vec_b = build_profile_vec(group_b, sections)
            if vec_a is None or vec_b is None:
                continue
            null_shifts[ch] = [b - a for a, b in zip(vec_a, vec_b)]

        if len(null_shifts) < 3:
            continue

        null_atoms = sorted(null_shifts.keys())
        null_corrs = []
        for i in range(len(null_atoms)):
            for j in range(i + 1, len(null_atoms)):
                r = vec_correlation(null_shifts[null_atoms[i]],
                                    null_shifts[null_atoms[j]])
                null_corrs.append(r)
        if null_corrs:
            null_means.append(sum(null_corrs) / len(null_corrs))

    null_mean = sum(null_means) / len(null_means) if null_means else 0
    null_std = (math.sqrt(sum((s - null_mean) ** 2 for s in null_means)
                          / len(null_means)) if null_means else 0)
    n_better = sum(1 for s in null_means if s >= mean_corr)
    z_score = ((mean_corr - null_mean) / null_std) if null_std > 0 else 0
    p_value = n_better / len(null_means) if null_means else 1

    print(f"  Real mean shift correlation:  {mean_corr:.4f}")
    print(f"  Null mean:                    {null_mean:.4f} +/- {null_std:.4f}")
    print(f"  Z-score:                      {z_score:.2f}")
    print(f"  p-value:                      {p_value:.4f} ({n_better}/{len(null_means)})")
    print()

    if p_value < 0.01:
        print("  >>> HIGHLY SIGNIFICANT (p < 0.01)")
        print("  >>> Position-dependent shift is SYSTEMATIC — grammatical rule.")
    elif p_value < 0.05:
        print("  >>> SIGNIFICANT (p < 0.05)")
        print("  >>> Position-dependent shift is systematic.")
    elif p_value < 0.10:
        print("  >>> MARGINAL (p < 0.10)")
    else:
        print("  >>> NOT SIGNIFICANT")
        print("  >>> Shifts are per-atom, not systematic.")
    print()

    # ================================================================
    # PART 4: Feature-level shift analysis
    # ================================================================
    print("PART 4: WHICH FEATURES SHIFT SYSTEMATICALLY?")
    print("Mean shift (PREFIX - MIDDLE) across all atoms")
    print("-" * 72)

    n_feat = len(feature_names)
    mean_shifts = []
    for fi in range(n_feat):
        vals = [shift_vectors[ch][fi] for ch in atoms]
        mean_s = sum(vals) / len(vals)
        std_s = math.sqrt(sum((v - mean_s) ** 2 for v in vals) / len(vals))
        # t-test: is mean shift significantly different from 0?
        se = std_s / math.sqrt(len(vals)) if len(vals) > 1 else 1
        t_stat = mean_s / se if se > 0 else 0
        mean_shifts.append((feature_names[fi], mean_s, std_s, t_stat))

    print(f"  {'Feature':12s} {'MeanShift':>10s} {'StdDev':>8s} "
          f"{'t-stat':>8s} {'Interpretation'}")
    print(f"  {'-------':12s} {'---------':>10s} {'------':>8s} "
          f"{'------':>8s} {'-------------'}")

    for fname, ms, sd, t in sorted(mean_shifts, key=lambda x: abs(x[3]),
                                    reverse=True):
        sig = "***" if abs(t) > 3 else "**" if abs(t) > 2 else "*" if abs(t) > 1.5 else ""
        if abs(t) > 1.5:
            if fname == "mean_pos" and ms < 0:
                interp = "PREFIX = earlier in line"
            elif fname == "li_rate" and ms > 0:
                interp = "PREFIX = more line-initial"
            elif fname == "lf_rate" and ms < 0:
                interp = "PREFIX = less line-final"
            elif fname == "sfx_rate" and ms < 0:
                interp = "PREFIX = less often suffixed"
            elif fname == "pi_rate" and ms > 0:
                interp = "PREFIX = more paragraph-initial"
            elif "sec_" in fname:
                interp = f"Section distribution shift"
            else:
                interp = "systematic shift"
        else:
            interp = ""

        print(f"  {fname:12s} {ms:+10.4f} {sd:8.4f} {t:+8.2f}  {sig:3s} "
              f"{interp}")

    print()

    # ================================================================
    # PART 5: Suffix shift analysis
    # ================================================================
    print("PART 5: SUFFIX SHIFT (MIDDLE->SUFFIX)")
    print("-" * 72)

    sfx_shift_vectors = {}
    for ch in sorted(char_pos_tokens.keys()):
        positions = char_pos_tokens[ch]
        mid_toks = positions.get("MIDDLE", [])
        sfx_toks = positions.get("SUFFIX", [])

        mid_vec = build_profile_vec(mid_toks, sections)
        sfx_vec = build_profile_vec(sfx_toks, sections)

        if mid_vec is None or sfx_vec is None:
            continue

        shift = [s - m for s, m in zip(sfx_vec, mid_vec)]
        sfx_shift_vectors[ch] = shift

    print(f"  Atoms with both SUFFIX and MIDDLE profiles: "
          f"{len(sfx_shift_vectors)}")

    if len(sfx_shift_vectors) >= 3:
        sfx_atoms = sorted(sfx_shift_vectors.keys())
        sfx_corrs = []
        for i in range(len(sfx_atoms)):
            for j in range(i + 1, len(sfx_atoms)):
                r = vec_correlation(sfx_shift_vectors[sfx_atoms[i]],
                                    sfx_shift_vectors[sfx_atoms[j]])
                sfx_corrs.append(r)

        sfx_mean = sum(sfx_corrs) / len(sfx_corrs)
        print(f"  Mean pairwise SUFFIX shift correlation: {sfx_mean:.4f}")

        # Compare to PREFIX shift
        print(f"  (Compare PREFIX shift correlation: {mean_corr:.4f})")
    print()

    # ================================================================
    # PART 6: Summary
    # ================================================================
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print()
    print(f"  PREFIX->MIDDLE shift correlation: {mean_corr:.4f}")
    print(f"  Null distribution: {null_mean:.4f} +/- {null_std:.4f}")
    print(f"  Z-score: {z_score:.2f}, p={p_value:.4f}")
    print()

    if p_value < 0.05:
        print("  FINDING: Atoms shift SYSTEMATICALLY between PREFIX and")
        print("  MIDDLE positions. This is consistent with a grammatical")
        print("  rule: morphological position selects behavioral role.")
        print()
        print("  Key systematic shifts:")
        for fname, ms, sd, t in sorted(mean_shifts,
                                        key=lambda x: abs(x[3]),
                                        reverse=True)[:5]:
            if abs(t) > 1.5:
                direction = "UP" if ms > 0 else "DOWN"
                print(f"    {fname:12s}: PREFIX {direction} "
                      f"(shift={ms:+.4f}, t={t:+.2f})")
    else:
        print("  FINDING: Shifts are NOT systematic. Each atom shifts")
        print("  independently, not according to a shared grammatical rule.")

    # Save results
    results = {
        "n_atoms_tested": n_atoms,
        "mean_shift_correlation": round(mean_corr, 4),
        "median_shift_correlation": round(median_corr, 4),
        "null_mean": round(null_mean, 4),
        "null_std": round(null_std, 4),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "n_permutations": n_perms,
        "shift_vectors": {ch: [round(v, 5) for v in sv]
                          for ch, sv in shift_vectors.items()},
        "feature_shifts": {fname: {"mean": round(ms, 5), "std": round(sd, 5),
                                   "t_stat": round(t, 3)}
                          for fname, ms, sd, t in mean_shifts},
        "suffix_shift_atoms": len(sfx_shift_vectors),
    }

    out_path = RESULTS_DIR / "grammatical_role_test.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()

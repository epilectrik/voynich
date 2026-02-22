"""
POSITIONAL_ATOMICITY: Universal Additive Composition Test
=========================================================
Phase 423 — Tests whether composition is universally additive when
using position-specific atom profiles.

Core hypothesis: The "emergence" found in PREFIX compounds (Phase 422,
C1191) is an artifact of using MIDDLE-position atom profiles to predict
PREFIX-position compound behavior. If atoms have position-specific
behavioral variants (analogous to German word stems shifting between
verb/adjective/noun by grammatical context), composition may be
additive everywhere — you just need the right variant of each atom.

Pre-registered hypotheses:
  H1 (strong): Position-specific profiles make ALL compounds predictable
               additively across all positions.
  H2 (moderate): Position-specific profiles substantially improve PREFIX
                 compound prediction, but ch/sh remain genuinely emergent
                 (consistent with C929).

Tests:
  PRE-FLIGHT: Atom-by-position token count table
  T1: PREFIX-specific additive prediction (leave-one-out + permutation)
  T2: SUFFIX-specific additive prediction (same controls)
  T3: Near-identical pair separation under position-specific profiles
  T4: PREFIX shift subgroup structure validation

Controls:
  - Leave-one-out compound exclusion (circularity control)
  - 1000-permutation null distribution
  - Cross-position baseline comparison (MIDDLE profiles predicting
    PREFIX/SUFFIX compounds — the "wrong variant" baseline)

Provenance: C1190, C1191, C929, C521, C522
"""
import json
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/POSITIONAL_ATOMICITY/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PREFIX_BINS = ["qo", "ch", "sh", "da", "sa", "ok", "ot", "ol", "other", "none"]
MIN_TOKENS = 30  # Minimum tokens for reliable profile


# ============================================================
# UTILITY
# ============================================================

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


def cosine_similarity(v1, v2):
    """Cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


# ============================================================
# DATA LOADING & PROFILE COMPUTATION
# ============================================================

def load_token_data():
    """Load all Currier B tokens with morphological decomposition and
    positional metadata. Returns list of enriched token dicts."""
    tx = Transcript()
    morph = Morphology()

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

    enriched = []
    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue

        prefix = m.prefix if m.prefix else None
        prefix_bin = prefix if prefix in PREFIX_BINS[:-2] else (
            "none" if prefix is None else "other")

        enriched.append({
            "word": token.word,
            "folio": token.folio,
            "section": token.section,
            "prefix": m.prefix,
            "middle": m.middle,
            "suffix": m.suffix,
            "norm_pos": token_positions.get(id(token), 0.5),
            "line_initial": token.line_initial,
            "line_final": token.line_final,
            "par_initial": token.par_initial,
            "par_final": token.par_final,
            "has_articulator": m.has_articulator,
            "prefix_bin": prefix_bin,
        })

    return enriched, sections


def compute_profile(tokens, sections):
    """Compute behavioral profile from a list of token dicts.
    Returns dict of behavioral features."""
    n = len(tokens)
    if n < 1:
        return None

    mean_pos = sum(t["norm_pos"] for t in tokens) / n
    sec_counts = Counter(t["section"] for t in tokens)
    sec_vec = [sec_counts.get(s, 0) / n for s in sections]
    li_rate = sum(1 for t in tokens if t["line_initial"]) / n
    lf_rate = sum(1 for t in tokens if t["line_final"]) / n
    pi_rate = sum(1 for t in tokens if t["par_initial"]) / n
    pf_rate = sum(1 for t in tokens if t["par_final"]) / n
    sfx_rate = sum(1 for t in tokens if t["suffix"] is not None) / n
    art_rate = sum(1 for t in tokens if t["has_articulator"]) / n

    pfx_counts = Counter(t["prefix_bin"] for t in tokens)
    pfx_vec = [pfx_counts.get(p, 0) / n for p in PREFIX_BINS]

    return {
        "n_tokens": n,
        "mean_pos": mean_pos,
        "sec_vec": sec_vec,
        "li_rate": li_rate,
        "lf_rate": lf_rate,
        "pi_rate": pi_rate,
        "pf_rate": pf_rate,
        "sfx_rate": sfx_rate,
        "art_rate": art_rate,
        "pfx_vec": pfx_vec,
    }


def profile_to_vector(p):
    """Flatten profile dict to feature vector (no kernel)."""
    return ([p["mean_pos"], p["li_rate"], p["lf_rate"],
             p["pi_rate"], p["pf_rate"],
             p["sfx_rate"], p["art_rate"]]
            + p["sec_vec"] + p["pfx_vec"])


FEATURE_NAMES = None  # Set after sections are known


def get_feature_names(sections):
    return (["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate",
             "sfx_rate", "art_rate"]
            + [f"sec_{s}" for s in sections]
            + [f"pfx_{p}" for p in PREFIX_BINS])


# ============================================================
# POSITION-SPECIFIC PROFILE COMPUTATION
# ============================================================

def decompose_prefix_to_atoms(prefix_str):
    """Decompose a compound prefix into its constituent single-char atoms.
    E.g. 'ch' -> ['c', 'h'], 'qo' -> ['q', 'o'], 'pch' -> ['p', 'c', 'h']"""
    return list(prefix_str)


def decompose_suffix_to_atoms(suffix_str):
    """Decompose a suffix into its constituent single-char atoms.
    E.g. 'dy' -> ['d', 'y'], 'aiin' -> ['a', 'i', 'n']"""
    return list(suffix_str)


def compute_atom_position_profiles(all_tokens, sections):
    """Compute per-atom, per-position behavioral profiles.

    For each single-character atom, compute separate profiles for when
    that atom appears in PREFIX, MIDDLE, and SUFFIX position.

    For PREFIX: atom 'c' in PREFIX means tokens where the prefix contains 'c'
                (e.g. ch, ckh, pch all contribute to c-in-PREFIX)
    For MIDDLE: atom 'k' in MIDDLE means tokens where the MIDDLE contains 'k'
                (standalone 'k' or compounds like 'ke', 'ok')
    For SUFFIX: atom 'y' in SUFFIX means tokens where the suffix contains 'y'
                (e.g. -y, -dy, -ey)

    Returns: {position: {atom: profile_dict}}
    """
    # Collect tokens by (atom, position)
    atom_pos_tokens = defaultdict(lambda: defaultdict(list))

    for t in all_tokens:
        # PREFIX atoms
        if t["prefix"]:
            pfx_atoms = decompose_prefix_to_atoms(t["prefix"])
            for atom in set(pfx_atoms):  # unique atoms in this prefix
                atom_pos_tokens["PREFIX"][atom].append(t)

        # MIDDLE atoms
        mid_atoms = list(t["middle"])
        for atom in set(mid_atoms):
            atom_pos_tokens["MIDDLE"][atom].append(t)

        # SUFFIX atoms
        if t["suffix"]:
            sfx_atoms = decompose_suffix_to_atoms(t["suffix"])
            for atom in set(sfx_atoms):
                atom_pos_tokens["SUFFIX"][atom].append(t)

    # Compute profiles
    result = {}
    for position in ["PREFIX", "MIDDLE", "SUFFIX"]:
        result[position] = {}
        for atom, tokens in atom_pos_tokens[position].items():
            if len(atom) != 1:
                continue
            if len(tokens) >= MIN_TOKENS:
                result[position][atom] = compute_profile(tokens, sections)
            else:
                result[position][atom] = None  # underpowered

    return result, atom_pos_tokens


def compute_atom_profile_leave_one_out(atom, position, compound_str,
                                       atom_pos_tokens, sections):
    """Compute atom profile EXCLUDING tokens where the atom appears in
    a specific compound. This is the circularity control.

    For PREFIX: exclude tokens where prefix == compound_str
    For MIDDLE: exclude tokens where middle == compound_str
    For SUFFIX: exclude tokens where suffix == compound_str
    """
    all_tokens = atom_pos_tokens[position][atom]

    if position == "PREFIX":
        filtered = [t for t in all_tokens if t["prefix"] != compound_str]
    elif position == "MIDDLE":
        filtered = [t for t in all_tokens if t["middle"] != compound_str]
    elif position == "SUFFIX":
        filtered = [t for t in all_tokens if t["suffix"] != compound_str]
    else:
        filtered = all_tokens

    if len(filtered) < MIN_TOKENS:
        return None

    return compute_profile(filtered, sections)


# ============================================================
# COMPOUND PROFILE COMPUTATION
# ============================================================

def compute_compound_profiles(all_tokens, sections, position):
    """Compute observed behavioral profiles for multi-char compounds
    in a specific position.

    Returns: {compound_str: profile_dict}
    """
    compound_tokens = defaultdict(list)

    for t in all_tokens:
        if position == "PREFIX" and t["prefix"] and len(t["prefix"]) >= 2:
            compound_tokens[t["prefix"]].append(t)
        elif position == "MIDDLE" and len(t["middle"]) >= 2:
            compound_tokens[t["middle"]].append(t)
        elif position == "SUFFIX" and t["suffix"] and len(t["suffix"]) >= 2:
            compound_tokens[t["suffix"]].append(t)

    result = {}
    for compound, tokens in compound_tokens.items():
        # All atoms must be single characters
        atoms = list(compound)
        if not all(len(a) == 1 for a in atoms):
            continue
        if len(tokens) >= MIN_TOKENS:
            result[compound] = compute_profile(tokens, sections)

    return result


# ============================================================
# ADDITIVE PREDICTION
# ============================================================

def predict_compound_additive(compound_str, atom_profiles):
    """Predict compound profile by averaging atom profiles (additive model)."""
    atoms = list(compound_str)
    atom_vecs = []
    for a in atoms:
        if a not in atom_profiles or atom_profiles[a] is None:
            return None
        atom_vecs.append(profile_to_vector(atom_profiles[a]))

    if not atom_vecs:
        return None

    n = len(atom_vecs)
    return [sum(atom_vecs[j][i] for j in range(n)) / n
            for i in range(len(atom_vecs[0]))]


def predict_compound_loo(compound_str, position, atom_pos_tokens, sections):
    """Predict compound using leave-one-out atom profiles.
    Each atom's profile is computed EXCLUDING tokens where
    that atom appears in this specific compound."""
    atoms = list(compound_str)
    atom_vecs = []
    for a in atoms:
        loo_profile = compute_atom_profile_leave_one_out(
            a, position, compound_str, atom_pos_tokens, sections)
        if loo_profile is None:
            return None
        atom_vecs.append(profile_to_vector(loo_profile))

    if not atom_vecs:
        return None

    n = len(atom_vecs)
    return [sum(atom_vecs[j][i] for j in range(n)) / n
            for i in range(len(atom_vecs[0]))]


# ============================================================
# PRE-FLIGHT: Token Count Table
# ============================================================

def preflight(all_tokens, atom_pos_profiles):
    """Print atom-by-position token count table."""
    print("=" * 72)
    print("PRE-FLIGHT: Atom-by-Position Token Counts")
    print("=" * 72)
    print()

    all_atoms = sorted(set(
        list(atom_pos_profiles.get("PREFIX", {}).keys()) +
        list(atom_pos_profiles.get("MIDDLE", {}).keys()) +
        list(atom_pos_profiles.get("SUFFIX", {}).keys())
    ))

    print(f"  {'Atom':>6s}  {'PREFIX':>8s}  {'MIDDLE':>8s}  {'SUFFIX':>8s}  {'Status':>12s}")
    print(f"  {'----':>6s}  {'------':>8s}  {'------':>8s}  {'------':>8s}  {'------':>12s}")

    preflight_data = {}
    for atom in all_atoms:
        counts = {}
        for pos in ["PREFIX", "MIDDLE", "SUFFIX"]:
            p = atom_pos_profiles.get(pos, {}).get(atom)
            counts[pos] = p["n_tokens"] if p else 0

        status_parts = []
        for pos in ["PREFIX", "MIDDLE", "SUFFIX"]:
            if counts[pos] >= MIN_TOKENS:
                status_parts.append(pos[0])
            elif counts[pos] > 0:
                status_parts.append(pos[0].lower())

        status = "".join(status_parts) if status_parts else "NONE"
        if all(counts[p] >= MIN_TOKENS for p in ["PREFIX", "MIDDLE", "SUFFIX"]):
            status = "ALL"

        print(f"  {atom:>6s}  {counts['PREFIX']:>8d}  {counts['MIDDLE']:>8d}  {counts['SUFFIX']:>8d}  {status:>12s}")

        preflight_data[atom] = {
            "prefix_n": counts["PREFIX"],
            "middle_n": counts["MIDDLE"],
            "suffix_n": counts["SUFFIX"],
            "status": status,
        }

    print()
    n_all = sum(1 for d in preflight_data.values() if d["status"] == "ALL")
    n_pm = sum(1 for d in preflight_data.values()
               if d["prefix_n"] >= MIN_TOKENS and d["middle_n"] >= MIN_TOKENS)
    n_ms = sum(1 for d in preflight_data.values()
               if d["middle_n"] >= MIN_TOKENS and d["suffix_n"] >= MIN_TOKENS)
    print(f"  Atoms with all 3 positions powered (n>={MIN_TOKENS}): {n_all}")
    print(f"  Atoms with PREFIX+MIDDLE powered: {n_pm}")
    print(f"  Atoms with MIDDLE+SUFFIX powered: {n_ms}")
    print()

    return preflight_data


# ============================================================
# T1: PREFIX-Specific Additive Prediction
# ============================================================

def test_prefix_additivity(all_tokens, atom_pos_profiles, atom_pos_tokens,
                           sections):
    """Test whether PREFIX compounds are additively predictable
    from PREFIX-specific atom profiles."""
    print("=" * 72)
    print("T1: PREFIX-Specific Additive Prediction")
    print("    H1: Compounds predictable from position-specific atom profiles")
    print("    Control: Leave-one-out compound exclusion + permutation null")
    print("=" * 72)
    print()

    prefix_compounds = compute_compound_profiles(all_tokens, sections, "PREFIX")
    prefix_atoms = atom_pos_profiles.get("PREFIX", {})
    middle_atoms = atom_pos_profiles.get("MIDDLE", {})

    # Filter to testable compounds (all atoms have PREFIX profiles)
    testable = {}
    for comp, profile in prefix_compounds.items():
        atoms = list(comp)
        if all(a in prefix_atoms and prefix_atoms[a] is not None for a in atoms):
            testable[comp] = profile

    print(f"  PREFIX compounds with n>={MIN_TOKENS}: {len(prefix_compounds)}")
    print(f"  Testable (all atoms have PREFIX profiles): {len(testable)}")
    print()

    if len(testable) < 3:
        print("  INSUFFICIENT DATA for PREFIX additivity test.")
        return {"status": "INSUFFICIENT_DATA", "n_testable": len(testable)}

    # === Method A: Direct prediction (position-specific profiles) ===
    print("  --- Method A: PREFIX-specific profiles (position-matched) ---")
    corrs_pos_specific = []
    per_compound_a = {}
    for comp, actual_prof in testable.items():
        predicted = predict_compound_loo(comp, "PREFIX", atom_pos_tokens, sections)
        if predicted is None:
            per_compound_a[comp] = {"status": "LOO_FAILED"}
            continue
        actual_vec = profile_to_vector(actual_prof)
        r = vec_correlation(predicted, actual_vec)
        corrs_pos_specific.append(r)
        per_compound_a[comp] = {"r": round(r, 4), "n": actual_prof["n_tokens"]}

    mean_pos_specific = sum(corrs_pos_specific) / max(len(corrs_pos_specific), 1)

    # === Method B: Cross-position baseline (MIDDLE profiles predicting PREFIX) ===
    print("  --- Method B: MIDDLE profiles predicting PREFIX (wrong variant) ---")
    corrs_cross_pos = []
    per_compound_b = {}
    for comp, actual_prof in testable.items():
        atoms = list(comp)
        if not all(a in middle_atoms and middle_atoms[a] is not None for a in atoms):
            per_compound_b[comp] = {"status": "NO_MIDDLE_PROFILE"}
            continue
        predicted = predict_compound_additive(comp, middle_atoms)
        if predicted is None:
            per_compound_b[comp] = {"status": "PREDICT_FAILED"}
            continue
        actual_vec = profile_to_vector(actual_prof)
        r = vec_correlation(predicted, actual_vec)
        corrs_cross_pos.append(r)
        per_compound_b[comp] = {"r": round(r, 4)}

    mean_cross_pos = sum(corrs_cross_pos) / max(len(corrs_cross_pos), 1)

    # === Permutation test (position-specific) ===
    print("  --- Permutation null (1000 permutations) ---")
    atom_keys = [a for a in prefix_atoms if prefix_atoms[a] is not None]
    random.seed(42)
    perm_scores = []

    for _ in range(1000):
        shuffled = atom_keys[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(atom_keys, shuffled))
        perm_profs = {k: prefix_atoms[perm_map[k]] for k in atom_keys
                      if perm_map[k] in prefix_atoms and prefix_atoms[perm_map[k]] is not None}

        perm_corrs = []
        for comp, actual_prof in testable.items():
            pred = predict_compound_additive(comp, perm_profs)
            if pred is None:
                continue
            actual_vec = profile_to_vector(actual_prof)
            perm_corrs.append(vec_correlation(pred, actual_vec))

        if perm_corrs:
            perm_scores.append(sum(perm_corrs) / len(perm_corrs))

    perm_mean = sum(perm_scores) / max(len(perm_scores), 1)
    perm_std = math.sqrt(sum((s - perm_mean) ** 2 for s in perm_scores)
                         / max(len(perm_scores), 1))
    n_better = sum(1 for s in perm_scores if s >= mean_pos_specific)
    p_value = n_better / max(len(perm_scores), 1)
    z_score = (mean_pos_specific - perm_mean) / max(perm_std, 0.0001)

    # === Results ===
    print()
    print(f"  RESULTS:")
    print(f"    Position-specific (LOO):  r = {mean_pos_specific:.4f}  (n={len(corrs_pos_specific)})")
    print(f"    Cross-position baseline:  r = {mean_cross_pos:.4f}  (n={len(corrs_cross_pos)})")
    print(f"    Improvement:              delta = {mean_pos_specific - mean_cross_pos:+.4f}")
    print(f"    Permutation null:         r = {perm_mean:.4f} +/- {perm_std:.4f}")
    print(f"    Z-score:                  {z_score:.2f}")
    print(f"    p-value:                  {p_value:.4f}  ({n_better}/1000)")
    print()

    # Per-compound breakdown
    print(f"  PER-COMPOUND BREAKDOWN:")
    print(f"    {'Compound':>10s}  {'N':>6s}  {'Pos-Spec':>9s}  {'Cross-Pos':>9s}  {'Delta':>7s}  {'Verdict'}")
    print(f"    {'--------':>10s}  {'---':>6s}  {'---------':>9s}  {'---------':>9s}  {'-----':>7s}  {'-------'}")
    for comp in sorted(testable.keys()):
        r_a = per_compound_a.get(comp, {}).get("r")
        r_b = per_compound_b.get(comp, {}).get("r")
        n = testable[comp]["n_tokens"]
        if r_a is not None and r_b is not None:
            delta = r_a - r_b
            verdict = "IMPROVED" if delta > 0.05 else "SAME" if delta > -0.05 else "WORSE"
            print(f"    {comp:>10s}  {n:>6d}  {r_a:>9.4f}  {r_b:>9.4f}  {delta:>+7.3f}  {verdict}")
        elif r_a is not None:
            print(f"    {comp:>10s}  {n:>6d}  {r_a:>9.4f}  {'---':>9s}  {'---':>7s}  NO_BASELINE")
        else:
            print(f"    {comp:>10s}  {n:>6d}  {'LOO_FAIL':>9s}  {'---':>9s}  {'---':>7s}  EXCLUDED")
    print()

    # Verdict
    if p_value < 0.01 and mean_pos_specific > mean_cross_pos:
        verdict = "H1_SUPPORTED"
        print(f"  VERDICT: {verdict} - Position-specific profiles significantly predict")
        print(f"           PREFIX compounds (p<0.01) and outperform cross-position baseline.")
    elif p_value < 0.05 and mean_pos_specific > mean_cross_pos:
        verdict = "H1_MARGINAL"
        print(f"  VERDICT: {verdict} - Significant (p<0.05) but marginal improvement.")
    elif mean_pos_specific > mean_cross_pos:
        verdict = "H2_PARTIAL"
        print(f"  VERDICT: {verdict} - Improvement but not significant against null.")
    else:
        verdict = "FALSIFIED"
        print(f"  VERDICT: {verdict} - Position-specific profiles do NOT improve prediction.")
    print()

    return {
        "position_specific_r": round(mean_pos_specific, 4),
        "cross_position_r": round(mean_cross_pos, 4),
        "delta": round(mean_pos_specific - mean_cross_pos, 4),
        "perm_mean": round(perm_mean, 4),
        "perm_std": round(perm_std, 4),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "n_testable": len(testable),
        "n_tested": len(corrs_pos_specific),
        "verdict": verdict,
        "per_compound": per_compound_a,
    }


# ============================================================
# T2: SUFFIX-Specific Additive Prediction
# ============================================================

def test_suffix_additivity(all_tokens, atom_pos_profiles, atom_pos_tokens,
                           sections):
    """Test whether SUFFIX compounds are additively predictable
    from SUFFIX-specific atom profiles."""
    print("=" * 72)
    print("T2: SUFFIX-Specific Additive Prediction")
    print("=" * 72)
    print()

    suffix_compounds = compute_compound_profiles(all_tokens, sections, "SUFFIX")
    suffix_atoms = atom_pos_profiles.get("SUFFIX", {})
    middle_atoms = atom_pos_profiles.get("MIDDLE", {})

    testable = {}
    for comp, profile in suffix_compounds.items():
        atoms = list(comp)
        if all(a in suffix_atoms and suffix_atoms[a] is not None for a in atoms):
            testable[comp] = profile

    print(f"  SUFFIX compounds with n>={MIN_TOKENS}: {len(suffix_compounds)}")
    print(f"  Testable (all atoms have SUFFIX profiles): {len(testable)}")
    print()

    if len(testable) < 3:
        print("  INSUFFICIENT DATA for SUFFIX additivity test.")
        return {"status": "INSUFFICIENT_DATA", "n_testable": len(testable)}

    # Position-specific prediction (LOO)
    corrs_pos_specific = []
    per_compound = {}
    for comp, actual_prof in testable.items():
        predicted = predict_compound_loo(comp, "SUFFIX", atom_pos_tokens, sections)
        if predicted is None:
            per_compound[comp] = {"status": "LOO_FAILED"}
            continue
        actual_vec = profile_to_vector(actual_prof)
        r = vec_correlation(predicted, actual_vec)
        corrs_pos_specific.append(r)
        per_compound[comp] = {"r": round(r, 4), "n": actual_prof["n_tokens"]}

    mean_pos_specific = sum(corrs_pos_specific) / max(len(corrs_pos_specific), 1)

    # Cross-position baseline (MIDDLE profiles)
    corrs_cross_pos = []
    for comp, actual_prof in testable.items():
        atoms = list(comp)
        if not all(a in middle_atoms and middle_atoms[a] is not None for a in atoms):
            continue
        predicted = predict_compound_additive(comp, middle_atoms)
        if predicted is None:
            continue
        actual_vec = profile_to_vector(actual_prof)
        corrs_cross_pos.append(vec_correlation(predicted, actual_vec))

    mean_cross_pos = sum(corrs_cross_pos) / max(len(corrs_cross_pos), 1)

    # Permutation test
    atom_keys = [a for a in suffix_atoms if suffix_atoms[a] is not None]
    random.seed(42)
    perm_scores = []

    for _ in range(1000):
        shuffled = atom_keys[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(atom_keys, shuffled))
        perm_profs = {k: suffix_atoms[perm_map[k]] for k in atom_keys
                      if perm_map[k] in suffix_atoms and suffix_atoms[perm_map[k]] is not None}

        perm_corrs = []
        for comp, actual_prof in testable.items():
            pred = predict_compound_additive(comp, perm_profs)
            if pred is None:
                continue
            actual_vec = profile_to_vector(actual_prof)
            perm_corrs.append(vec_correlation(pred, actual_vec))

        if perm_corrs:
            perm_scores.append(sum(perm_corrs) / len(perm_corrs))

    perm_mean = sum(perm_scores) / max(len(perm_scores), 1)
    perm_std = math.sqrt(sum((s - perm_mean) ** 2 for s in perm_scores)
                         / max(len(perm_scores), 1))
    n_better = sum(1 for s in perm_scores if s >= mean_pos_specific)
    p_value = n_better / max(len(perm_scores), 1)
    z_score = (mean_pos_specific - perm_mean) / max(perm_std, 0.0001)

    print(f"  RESULTS:")
    print(f"    Position-specific (LOO):  r = {mean_pos_specific:.4f}  (n={len(corrs_pos_specific)})")
    print(f"    Cross-position baseline:  r = {mean_cross_pos:.4f}  (n={len(corrs_cross_pos)})")
    print(f"    Improvement:              delta = {mean_pos_specific - mean_cross_pos:+.4f}")
    print(f"    Permutation null:         r = {perm_mean:.4f} +/- {perm_std:.4f}")
    print(f"    Z-score:                  {z_score:.2f}")
    print(f"    p-value:                  {p_value:.4f}  ({n_better}/1000)")
    print()

    # Per-compound breakdown
    print(f"  PER-COMPOUND BREAKDOWN:")
    print(f"    {'Compound':>10s}  {'N':>6s}  {'Pos-Spec':>9s}  {'Verdict'}")
    print(f"    {'--------':>10s}  {'---':>6s}  {'---------':>9s}  {'-------'}")
    for comp in sorted(per_compound.keys()):
        info = per_compound[comp]
        if "r" in info:
            print(f"    {comp:>10s}  {info['n']:>6d}  {info['r']:>9.4f}  OK")
        else:
            print(f"    {comp:>10s}  {'---':>6s}  {'LOO_FAIL':>9s}  EXCLUDED")
    print()

    if p_value < 0.01 and mean_pos_specific > mean_cross_pos:
        verdict = "H1_SUPPORTED"
    elif p_value < 0.05 and mean_pos_specific > mean_cross_pos:
        verdict = "H1_MARGINAL"
    elif mean_pos_specific > mean_cross_pos:
        verdict = "H2_PARTIAL"
    else:
        verdict = "FALSIFIED"

    print(f"  VERDICT: {verdict}")
    print()

    return {
        "position_specific_r": round(mean_pos_specific, 4),
        "cross_position_r": round(mean_cross_pos, 4),
        "delta": round(mean_pos_specific - mean_cross_pos, 4),
        "perm_mean": round(perm_mean, 4),
        "perm_std": round(perm_std, 4),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "n_testable": len(testable),
        "n_tested": len(corrs_pos_specific),
        "verdict": verdict,
        "per_compound": per_compound,
    }


# ============================================================
# T3: Near-Identical Pair Separation
# ============================================================

def test_pair_separation(atom_pos_profiles):
    """Test whether near-identical pairs (k-t, d-o, p-t, l-r) separate
    under position-specific profiles."""
    print("=" * 72)
    print("T3: Near-Identical Pair Separation")
    print("    Phase 422 found k-t r=0.993, d-o r=0.945 with global profiles.")
    print("    Do they separate with position-specific profiles?")
    print("=" * 72)
    print()

    test_pairs = [
        ("k", "t", 0.993),
        ("d", "o", 0.945),
        ("p", "t", 0.935),
        ("l", "r", 0.919),
    ]

    pair_results = {}
    print(f"  {'Pair':>6s}  {'Global':>7s}  {'PREFIX':>7s}  {'MIDDLE':>7s}  {'SUFFIX':>7s}  {'Min':>7s}  {'Verdict'}")
    print(f"  {'----':>6s}  {'------':>7s}  {'------':>7s}  {'------':>7s}  {'------':>7s}  {'---':>7s}  {'-------'}")

    for a, b, global_r in test_pairs:
        pos_corrs = {}
        for pos in ["PREFIX", "MIDDLE", "SUFFIX"]:
            prof_a = atom_pos_profiles.get(pos, {}).get(a)
            prof_b = atom_pos_profiles.get(pos, {}).get(b)
            if prof_a is not None and prof_b is not None:
                vec_a = profile_to_vector(prof_a)
                vec_b = profile_to_vector(prof_b)
                pos_corrs[pos] = round(vec_correlation(vec_a, vec_b), 4)
            else:
                pos_corrs[pos] = None

        valid_corrs = [v for v in pos_corrs.values() if v is not None]
        min_corr = min(valid_corrs) if valid_corrs else None

        if min_corr is not None and min_corr < global_r - 0.05:
            verdict = "SEPARATED"
        elif min_corr is not None and min_corr < global_r:
            verdict = "MARGINAL"
        else:
            verdict = "STILL_IDENTICAL"

        pfx_str = f"{pos_corrs['PREFIX']:.3f}" if pos_corrs['PREFIX'] is not None else "---"
        mid_str = f"{pos_corrs['MIDDLE']:.3f}" if pos_corrs['MIDDLE'] is not None else "---"
        sfx_str = f"{pos_corrs['SUFFIX']:.3f}" if pos_corrs['SUFFIX'] is not None else "---"
        min_str = f"{min_corr:.3f}" if min_corr is not None else "---"

        print(f"  {a}-{b:>4s}  {global_r:>7.3f}  {pfx_str:>7s}  {mid_str:>7s}  {sfx_str:>7s}  {min_str:>7s}  {verdict}")

        pair_results[f"{a}-{b}"] = {
            "global_r": global_r,
            "prefix_r": pos_corrs["PREFIX"],
            "middle_r": pos_corrs["MIDDLE"],
            "suffix_r": pos_corrs["SUFFIX"],
            "min_r": min_corr,
            "verdict": verdict,
        }

    print()

    # Full pairwise matrix for all atoms in MIDDLE
    print("  FULL PAIRWISE SIMILARITY (MIDDLE-specific profiles):")
    mid_atoms = sorted([a for a in atom_pos_profiles.get("MIDDLE", {})
                        if atom_pos_profiles["MIDDLE"][a] is not None])

    # Find most similar pairs
    all_pairs = []
    for i, a in enumerate(mid_atoms):
        for b in mid_atoms[i+1:]:
            va = profile_to_vector(atom_pos_profiles["MIDDLE"][a])
            vb = profile_to_vector(atom_pos_profiles["MIDDLE"][b])
            r = vec_correlation(va, vb)
            all_pairs.append((a, b, r))

    all_pairs.sort(key=lambda x: x[2], reverse=True)
    print(f"    Top 10 most similar MIDDLE pairs:")
    for a, b, r in all_pairs[:10]:
        print(f"      {a}-{b}: {r:.4f}")
    print()

    # Do same for PREFIX
    pfx_atoms = sorted([a for a in atom_pos_profiles.get("PREFIX", {})
                        if atom_pos_profiles["PREFIX"][a] is not None])
    if len(pfx_atoms) >= 2:
        pfx_pairs = []
        for i, a in enumerate(pfx_atoms):
            for b in pfx_atoms[i+1:]:
                va = profile_to_vector(atom_pos_profiles["PREFIX"][a])
                vb = profile_to_vector(atom_pos_profiles["PREFIX"][b])
                r = vec_correlation(va, vb)
                pfx_pairs.append((a, b, r))

        pfx_pairs.sort(key=lambda x: x[2], reverse=True)
        print(f"    Top 10 most similar PREFIX pairs:")
        for a, b, r in pfx_pairs[:10]:
            print(f"      {a}-{b}: {r:.4f}")
        print()

    return pair_results


# ============================================================
# T4: PREFIX Shift Subgroup Validation
# ============================================================

def test_subgroup_structure(atom_pos_profiles):
    """Validate the PREFIX shift subgroup structure from Phase 422.
    Test whether {c,h,k,t,f,s} vs {q} vs {a,d} have distinct
    position-specific profile differences."""
    print("=" * 72)
    print("T4: PREFIX Shift Subgroup Validation")
    print("    Phase 422 found {c,h,k,t,f,s} shift identically (r=0.91-0.98)")
    print("    Testing whether these subgroups have distinct PREFIX vs MIDDLE")
    print("    profile differences.")
    print("=" * 72)
    print()

    # Compute PREFIX-MIDDLE shift vectors for each atom
    shift_vectors = {}
    for atom in sorted(set(
        list(atom_pos_profiles.get("PREFIX", {}).keys()) +
        list(atom_pos_profiles.get("MIDDLE", {}).keys())
    )):
        pfx = atom_pos_profiles.get("PREFIX", {}).get(atom)
        mid = atom_pos_profiles.get("MIDDLE", {}).get(atom)
        if pfx is not None and mid is not None:
            v_pfx = profile_to_vector(pfx)
            v_mid = profile_to_vector(mid)
            shift = [p - m for p, m in zip(v_pfx, v_mid)]
            shift_vectors[atom] = shift

    if len(shift_vectors) < 4:
        print("  INSUFFICIENT DATA for subgroup analysis.")
        return {"status": "INSUFFICIENT_DATA"}

    print(f"  Atoms with PREFIX-MIDDLE shift vectors: {len(shift_vectors)}")
    print()

    # Expected subgroups from Phase 422
    expected_groups = {
        "primary": list("chktsf"),
        "anti": list("q"),
        "moderate": list("ad"),
    }

    # Compute intra-group and inter-group shift correlations
    all_atoms_with_shifts = sorted(shift_vectors.keys())

    print(f"  SHIFT VECTOR PAIRWISE CORRELATIONS:")
    print(f"    {'A':>3s}-{'B':>3s}  {'r':>7s}  {'Group'}")
    print(f"    {'--':>3s}-{'--':>3s}  {'---':>7s}  {'-----'}")

    intra_primary = []
    inter_primary = []
    pairwise = {}

    for i, a in enumerate(all_atoms_with_shifts):
        for b in all_atoms_with_shifts[i+1:]:
            r = vec_correlation(shift_vectors[a], shift_vectors[b])
            pairwise[f"{a}-{b}"] = round(r, 4)

            a_in_primary = a in expected_groups["primary"]
            b_in_primary = b in expected_groups["primary"]

            if a_in_primary and b_in_primary:
                intra_primary.append(r)
                group = "PRIMARY-INTRA"
            elif a_in_primary or b_in_primary:
                inter_primary.append(r)
                group = "PRIMARY-INTER"
            else:
                group = "OTHER"

            print(f"    {a:>3s}-{b:>3s}  {r:>7.4f}  {group}")

    print()

    mean_intra = sum(intra_primary) / max(len(intra_primary), 1) if intra_primary else None
    mean_inter = sum(inter_primary) / max(len(inter_primary), 1) if inter_primary else None

    if mean_intra is not None:
        print(f"  PRIMARY subgroup {set(expected_groups['primary']) & set(all_atoms_with_shifts)}:")
        print(f"    Mean intra-group shift r: {mean_intra:.4f}  (n={len(intra_primary)})")
    if mean_inter is not None:
        print(f"    Mean inter-group shift r: {mean_inter:.4f}  (n={len(inter_primary)})")
    if mean_intra is not None and mean_inter is not None:
        delta = mean_intra - mean_inter
        print(f"    Separation:               {delta:+.4f}")
        if delta > 0.2:
            verdict = "CONFIRMED"
            print(f"    VERDICT: Subgroup structure CONFIRMED (intra >> inter)")
        elif delta > 0.05:
            verdict = "PARTIAL"
            print(f"    VERDICT: PARTIAL confirmation (intra > inter)")
        else:
            verdict = "NOT_CONFIRMED"
            print(f"    VERDICT: Subgroup structure NOT confirmed")
    else:
        verdict = "INSUFFICIENT_DATA"
    print()

    return {
        "n_atoms": len(shift_vectors),
        "mean_intra_primary": round(mean_intra, 4) if mean_intra else None,
        "mean_inter_primary": round(mean_inter, 4) if mean_inter else None,
        "pairwise": pairwise,
        "verdict": verdict,
    }


# ============================================================
# T5: Discrete Role Clustering
# ============================================================

def test_role_clustering(atom_pos_profiles):
    """Test whether position-specific behavioral shifts cluster into
    discrete role categories (suggesting grammatical roles like
    verb/adjective/noun) or form a smooth continuum.

    Method: For each atom with both PREFIX and MIDDLE profiles, compute
    the shift vector (PREFIX - MIDDLE). Then test whether these shift
    vectors cluster into discrete groups using gap analysis:
    compare intra-cluster vs inter-cluster distances across candidate
    cluster counts (k=2,3,4).

    Also test MIDDLE-SUFFIX shifts for atoms with both profiles.
    """
    print("=" * 72)
    print("T5: Discrete Role Clustering")
    print("    Do positional shifts fall into discrete categories")
    print("    (suggesting distinct grammatical roles)?")
    print("=" * 72)
    print()

    results = {}

    for shift_name, pos_a, pos_b in [
        ("PREFIX_vs_MIDDLE", "PREFIX", "MIDDLE"),
        ("SUFFIX_vs_MIDDLE", "SUFFIX", "MIDDLE"),
    ]:
        print(f"  --- {shift_name} ---")
        print()

        # Compute shift vectors
        shift_vectors = {}
        for atom in sorted(
            set(atom_pos_profiles.get(pos_a, {}).keys()) &
            set(atom_pos_profiles.get(pos_b, {}).keys())
        ):
            prof_a = atom_pos_profiles.get(pos_a, {}).get(atom)
            prof_b = atom_pos_profiles.get(pos_b, {}).get(atom)
            if prof_a is not None and prof_b is not None:
                v_a = profile_to_vector(prof_a)
                v_b = profile_to_vector(prof_b)
                shift = [a - b for a, b in zip(v_a, v_b)]
                shift_vectors[atom] = shift

        n_atoms = len(shift_vectors)
        print(f"  Atoms with {shift_name} shift vectors: {n_atoms}")

        if n_atoms < 4:
            print(f"  INSUFFICIENT DATA for clustering.")
            results[shift_name] = {"status": "INSUFFICIENT_DATA"}
            print()
            continue

        atoms = sorted(shift_vectors.keys())
        vecs = [shift_vectors[a] for a in atoms]

        # Compute full pairwise distance matrix (1 - correlation)
        dist_matrix = {}
        for i, a in enumerate(atoms):
            for j, b in enumerate(atoms):
                if i < j:
                    r = vec_correlation(vecs[i], vecs[j])
                    dist_matrix[(a, b)] = 1.0 - r

        # K-means-style clustering (simple greedy, no numpy dependency)
        # Try k=1,2,3,4 and measure within-cluster vs between-cluster distance
        def assign_clusters(atoms, vecs, k, seed=42):
            """Simple k-medoids clustering."""
            random.seed(seed)
            n = len(atoms)
            if k >= n:
                return {a: i for i, a in enumerate(atoms)}, float('inf')

            # Initialize: pick k random medoids
            medoid_indices = random.sample(range(n), k)

            for _ in range(20):  # max iterations
                # Assign each atom to nearest medoid
                assignments = {}
                for i, a in enumerate(atoms):
                    best_dist = float('inf')
                    best_k = 0
                    for ki, mi in enumerate(medoid_indices):
                        d = 1.0 - vec_correlation(vecs[i], vecs[mi])
                        if d < best_dist:
                            best_dist = d
                            best_k = ki
                    assignments[a] = best_k

                # Update medoids: pick atom with lowest total distance to cluster
                new_medoids = []
                for ki in range(k):
                    cluster_atoms = [i for i, a in enumerate(atoms)
                                     if assignments[a] == ki]
                    if not cluster_atoms:
                        new_medoids.append(medoid_indices[ki])
                        continue
                    best_total = float('inf')
                    best_idx = cluster_atoms[0]
                    for ci in cluster_atoms:
                        total = sum(1.0 - vec_correlation(vecs[ci], vecs[cj])
                                    for cj in cluster_atoms)
                        if total < best_total:
                            best_total = total
                            best_idx = ci
                    new_medoids.append(best_idx)

                if sorted(new_medoids) == sorted(medoid_indices):
                    break
                medoid_indices = new_medoids

            # Compute within-cluster distance
            within = []
            for ki in range(k):
                cluster = [i for i, a in enumerate(atoms) if assignments[a] == ki]
                for ci in cluster:
                    for cj in cluster:
                        if ci < cj:
                            within.append(1.0 - vec_correlation(vecs[ci], vecs[cj]))

            mean_within = sum(within) / max(len(within), 1)
            return assignments, mean_within

        # Try multiple k values with multiple random seeds
        print(f"  Cluster analysis (k-medoids, 10 seeds per k):")
        print()

        k_results = {}
        for k in [1, 2, 3, 4]:
            if k >= n_atoms:
                continue
            best_within = float('inf')
            best_assignments = None
            for seed in range(10):
                assignments, within = assign_clusters(atoms, vecs, k, seed=seed*7+k)
                if within < best_within:
                    best_within = within
                    best_assignments = assignments

            # Compute between-cluster distance
            between = []
            for i, a in enumerate(atoms):
                for j, b in enumerate(atoms):
                    if i < j and best_assignments[a] != best_assignments[b]:
                        between.append(1.0 - vec_correlation(vecs[i], vecs[j]))

            mean_between = sum(between) / max(len(between), 1) if between else 0

            ratio = best_within / max(mean_between, 0.0001) if mean_between > 0 else float('inf')

            # Show clusters
            clusters = defaultdict(list)
            for a, ki in best_assignments.items():
                clusters[ki].append(a)

            cluster_strs = []
            for ki in sorted(clusters.keys()):
                members = sorted(clusters[ki])
                cluster_strs.append("{" + ",".join(members) + "}")

            print(f"    k={k}: within={best_within:.4f}  between={mean_between:.4f}  "
                  f"ratio={ratio:.4f}")
            print(f"         clusters: {' | '.join(cluster_strs)}")

            k_results[k] = {
                "within": round(best_within, 4),
                "between": round(mean_between, 4),
                "ratio": round(ratio, 4),
                "clusters": {str(ki): sorted(members)
                             for ki, members in clusters.items()},
            }

        print()

        # Gap analysis: biggest improvement in within/between ratio
        if len(k_results) >= 2:
            k_vals = sorted(k_results.keys())
            best_k = k_vals[0]
            best_gap = 0

            for i in range(1, len(k_vals)):
                k_prev = k_vals[i-1]
                k_curr = k_vals[i]
                gap = k_results[k_prev]["ratio"] - k_results[k_curr]["ratio"]
                if gap > best_gap:
                    best_gap = gap
                    best_k = k_curr

            # Also check: is the best k significantly better than k=1?
            if 1 in k_results and best_k in k_results:
                improvement = k_results[1]["ratio"] - k_results[best_k]["ratio"]
            else:
                improvement = 0

            if improvement > 0.1 and best_k > 1:
                verdict = f"DISCRETE_k{best_k}"
                print(f"  VERDICT: {verdict} - Shift vectors cluster into {best_k} "
                      f"discrete groups")
                print(f"           (ratio improvement from k=1: {improvement:.4f})")
            elif improvement > 0.03 and best_k > 1:
                verdict = f"WEAK_k{best_k}"
                print(f"  VERDICT: {verdict} - Weak clustering into {best_k} groups")
                print(f"           (ratio improvement: {improvement:.4f})")
            else:
                verdict = "CONTINUUM"
                print(f"  VERDICT: {verdict} - No discrete clusters; shifts form continuum")
        else:
            verdict = "INSUFFICIENT_K"
            best_k = 1

        print()

        results[shift_name] = {
            "n_atoms": n_atoms,
            "k_analysis": k_results,
            "best_k": best_k,
            "verdict": verdict,
        }

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 72)
    print("POSITIONAL_ATOMICITY: Universal Additive Composition Test")
    print("Phase 423")
    print("=" * 72)
    print()
    print("H1 (strong):   Composition universally additive with position-specific profiles")
    print("H2 (moderate): Position-specific profiles improve prediction, ch/sh still emergent")
    print()

    # Load data
    print("Loading data...")
    all_tokens, sections = load_token_data()
    print(f"  Loaded {len(all_tokens)} tokens, {len(sections)} sections")
    print()

    # Compute position-specific profiles
    print("Computing position-specific atom profiles...")
    atom_pos_profiles, atom_pos_tokens = compute_atom_position_profiles(
        all_tokens, sections)
    for pos in ["PREFIX", "MIDDLE", "SUFFIX"]:
        powered = sum(1 for a, p in atom_pos_profiles.get(pos, {}).items()
                      if p is not None)
        total = len(atom_pos_profiles.get(pos, {}))
        print(f"  {pos}: {powered}/{total} atoms powered (n>={MIN_TOKENS})")
    print()

    # Pre-flight
    preflight_data = preflight(all_tokens, atom_pos_profiles)

    # T1: PREFIX additivity
    t1_results = test_prefix_additivity(
        all_tokens, atom_pos_profiles, atom_pos_tokens, sections)

    # T2: SUFFIX additivity
    t2_results = test_suffix_additivity(
        all_tokens, atom_pos_profiles, atom_pos_tokens, sections)

    # T3: Near-identical pair separation
    t3_results = test_pair_separation(atom_pos_profiles)

    # T4: Subgroup structure
    t4_results = test_subgroup_structure(atom_pos_profiles)

    # T5: Discrete role clustering
    t5_results = test_role_clustering(atom_pos_profiles)

    # === OVERALL SUMMARY ===
    print("=" * 72)
    print("OVERALL SUMMARY")
    print("=" * 72)
    print()

    t1v = t1_results.get("verdict", "N/A")
    t2v = t2_results.get("verdict", "N/A")

    print(f"  T1 PREFIX additivity:     {t1v}")
    if "position_specific_r" in t1_results:
        print(f"     pos-specific r={t1_results['position_specific_r']:.4f}  "
              f"cross-pos r={t1_results['cross_position_r']:.4f}  "
              f"delta={t1_results['delta']:+.4f}  "
              f"p={t1_results['p_value']:.4f}")
    print(f"  T2 SUFFIX additivity:     {t2v}")
    if "position_specific_r" in t2_results:
        print(f"     pos-specific r={t2_results['position_specific_r']:.4f}  "
              f"cross-pos r={t2_results['cross_position_r']:.4f}  "
              f"delta={t2_results['delta']:+.4f}  "
              f"p={t2_results['p_value']:.4f}")

    n_sep = sum(1 for v in t3_results.values()
                if isinstance(v, dict) and v.get("verdict") == "SEPARATED")
    n_pairs = sum(1 for v in t3_results.values() if isinstance(v, dict))
    print(f"  T3 Pair separation:       {n_sep}/{n_pairs} pairs separated")

    t4v = t4_results.get("verdict", "N/A")
    print(f"  T4 Subgroup structure:    {t4v}")

    for shift_name in ["PREFIX_vs_MIDDLE", "SUFFIX_vs_MIDDLE"]:
        t5r = t5_results.get(shift_name, {})
        t5v = t5r.get("verdict", "N/A")
        best_k = t5r.get("best_k", "?")
        print(f"  T5 {shift_name}: {t5v} (best k={best_k})")
    print()

    # H1 vs H2
    if (t1v in ("H1_SUPPORTED",) and t2v in ("H1_SUPPORTED",)):
        print("  >>> H1 (STRONG): Universal additive composition CONFIRMED")
    elif t1v in ("H1_SUPPORTED", "H1_MARGINAL") or t2v in ("H1_SUPPORTED", "H1_MARGINAL"):
        print("  >>> H2 (MODERATE): Position-specific profiles improve prediction")
        print("  >>>   but universal additivity not fully confirmed")
    elif t1v in ("H2_PARTIAL",) or t2v in ("H2_PARTIAL",):
        print("  >>> H2 (PARTIAL): Some improvement, further investigation needed")
    else:
        print("  >>> NEITHER H1 NOR H2: Position-specific profiles do not help")
        print("  >>>   Emergence is genuine, not a cross-position artifact")
    print()

    # Save results
    results = {
        "phase": "POSITIONAL_ATOMICITY",
        "phase_number": 423,
        "preflight": preflight_data,
        "t1_prefix_additivity": t1_results,
        "t2_suffix_additivity": t2_results,
        "t3_pair_separation": t3_results,
        "t4_subgroup_structure": t4_results,
        "t5_role_clustering": t5_results,
        "min_tokens": MIN_TOKENS,
    }

    out_path = RESULTS_DIR / "positional_atomicity_test.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()

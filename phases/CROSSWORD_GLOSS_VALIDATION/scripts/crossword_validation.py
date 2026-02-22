"""
CROSSWORD GLOSS VALIDATION — Phase 422
=======================================
Tests whether single-character atom glosses are internally consistent
across all compound appearances, using behavioral crossword constraints.

Test Battery:
  T1. Atom Behavioral Consistency — Does each atom contribute the SAME
      behavioral signature in every compound it appears in?
  T2. Cross-Position Consistency — Same atom across PREFIX/MIDDLE/SUFFIX
      positions? (Validates C1190 position-independence claim)
  T3. Compound Gloss Audit — For each glossed compound, show atom
      decomposition alongside actual compound gloss for human evaluation.
  T4. Discriminative Power — Can any other atom substitute for this one
      without loss of behavioral prediction accuracy?

Methodology notes:
  - T1 and T2 are CIRCULARITY-FREE (no glosses used, pure behavioral)
  - T3 is semi-automated (generates audit table for human review)
  - T4 is behavioral (tests uniqueness of atom profiles)
  - C120 semantic ceiling: glosses = role-level function, not specific actions
  - C1190: atoms compose at construction layer, NOT execution layer

Output: phases/CROSSWORD_GLOSS_VALIDATION/results/crossword_validation.json
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

# Shared features usable across all morphological positions
# (excludes sfx_rate, art_rate, prefix co-occurrence — position-dependent)
SHARED_FEATURE_NAMES = ["mean_pos", "li_rate", "lf_rate", "pi_rate", "pf_rate"]
# section names are added dynamically


# ============================================================
# DATA LOADING
# ============================================================

def load_middle_dictionary():
    with open("data/middle_dictionary.json", encoding="utf-8") as f:
        return json.load(f)["middles"]


def get_atoms(middles):
    """Extract single-character MIDDLEs as the atomic alphabet."""
    atoms = {}
    for name, info in middles.items():
        if len(name) == 1:
            atoms[name] = {
                "gloss": info.get("gloss"),
                "kernel": info.get("kernel"),
                "tokens": info.get("token_count", 0),
                "regime": info.get("regime"),
            }
    return atoms


def get_glossed_compounds(middles, atoms):
    """Get multi-char MIDDLEs with glosses whose atoms are all known."""
    compounds = []
    for name, info in middles.items():
        if len(name) < 2 or not info.get("gloss"):
            continue
        if info.get("token_count", 0) < 5:
            continue
        all_atoms_known = all(ch in atoms for ch in name)
        compounds.append({
            "middle": name,
            "gloss": info["gloss"],
            "kernel": info.get("kernel"),
            "tokens": info.get("token_count", 0),
            "all_atoms_known": all_atoms_known,
            "atom_glosses": [(ch, atoms[ch]["gloss"]) for ch in name if ch in atoms],
        })
    compounds.sort(key=lambda x: x["tokens"], reverse=True)
    return compounds


# ============================================================
# BEHAVIORAL PROFILES (reuses C1190 methodology)
# ============================================================

def compute_behavioral_profiles():
    """Compute per-MIDDLE behavioral profiles from raw Currier B token data."""
    tx = Transcript()
    morph = Morphology()
    mid_dict = load_middle_dictionary()

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

    # Collect tokens by MIDDLE
    tokens_by_middle = defaultdict(list)
    # Also collect by morphological position for T2
    tokens_by_prefix_char = defaultdict(list)
    tokens_by_suffix_char = defaultdict(list)

    for token in b_tokens:
        m = morph.extract(token.word)
        if not m.middle or m.is_empty_middle:
            continue

        prefix = m.prefix if m.prefix else None
        prefix_bin = prefix if prefix in PREFIX_BINS[:-2] else (
            "none" if prefix is None else "other")

        kernel = mid_dict.get(m.middle, {}).get("kernel", None)

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
            "kernel": kernel,
        }

        tokens_by_middle[m.middle].append(tok_data)

        # Track character appearances in PREFIX position
        if prefix:
            for ch in prefix:
                tokens_by_prefix_char[ch].append(tok_data)

        # Track character appearances in SUFFIX position
        if m.suffix:
            for ch in m.suffix:
                tokens_by_suffix_char[ch].append(tok_data)

    # Build MIDDLE profiles (full 22-feature vector, same as C1190)
    profiles = {}
    for mid, toks in tokens_by_middle.items():
        n = len(toks)
        if n < 5:
            continue
        profiles[mid] = _build_profile(toks, sections)

    # Build PREFIX-position profiles (shared features only)
    prefix_profiles = {}
    for ch, toks in tokens_by_prefix_char.items():
        if len(toks) >= 10:
            prefix_profiles[ch] = _build_shared_profile(toks, sections)

    # Build SUFFIX-position profiles (shared features only)
    suffix_profiles = {}
    for ch, toks in tokens_by_suffix_char.items():
        if len(toks) >= 10:
            suffix_profiles[ch] = _build_shared_profile(toks, sections)

    # Build MIDDLE-position shared profiles (for cross-position comparison)
    middle_shared_profiles = {}
    for mid, toks in tokens_by_middle.items():
        if len(mid) == 1 and len(toks) >= 5:
            middle_shared_profiles[mid] = _build_shared_profile(toks, sections)

    return (profiles, prefix_profiles, suffix_profiles,
            middle_shared_profiles, sections)


def _build_profile(toks, sections):
    """Build full 22-feature behavioral profile."""
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


def _build_shared_profile(toks, sections):
    """Build shared-feature profile (position + section only, for T2)."""
    n = len(toks)
    mean_pos = sum(t["norm_pos"] for t in toks) / n
    sec_counts = Counter(t["section"] for t in toks)
    sec_vec = [sec_counts.get(s, 0) / n for s in sections]
    li_rate = sum(1 for t in toks if t["line_initial"]) / n
    lf_rate = sum(1 for t in toks if t["line_final"]) / n
    pi_rate = sum(1 for t in toks if t["par_initial"]) / n
    pf_rate = sum(1 for t in toks if t["par_final"]) / n
    return {
        "n_tokens": n,
        "mean_pos": mean_pos,
        "sec_vec": sec_vec,
        "li_rate": li_rate,
        "lf_rate": lf_rate,
        "pi_rate": pi_rate,
        "pf_rate": pf_rate,
    }


def profile_to_vector(p, mode="no_kernel"):
    """Flatten profile to vector (no-kernel mode from C1190)."""
    return ([p["mean_pos"], p["li_rate"], p["lf_rate"],
             p["pi_rate"], p["pf_rate"],
             p["sfx_rate"], p["art_rate"]]
            + p["sec_vec"] + p["pfx_vec"])


def shared_profile_to_vector(p):
    """Flatten shared-feature profile to vector."""
    return ([p["mean_pos"], p["li_rate"], p["lf_rate"],
             p["pi_rate"], p["pf_rate"]]
            + p["sec_vec"])


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


def vec_subtract(v1, v2):
    """Element-wise subtraction."""
    return [a - b for a, b in zip(v1, v2)]


def vec_mean(vecs):
    """Element-wise mean of multiple vectors."""
    if not vecs:
        return None
    n = len(vecs)
    dim = len(vecs[0])
    return [sum(vecs[j][i] for j in range(n)) / n for i in range(dim)]


# ============================================================
# T1: ATOM BEHAVIORAL CONSISTENCY
# ============================================================

def test_1_behavioral_consistency(profiles, sections):
    """For each atom, measure how consistently it contributes to compounds.

    Method: For each compound containing atom A, compute A's "contribution"
    as compound_profile - mean(other_atoms_profiles). Then measure pairwise
    correlation of A's contributions across all compounds.
    """
    print("=" * 72)
    print("T1: ATOM BEHAVIORAL CONSISTENCY")
    print("Does each atom contribute the SAME behavioral signature")
    print("in every compound it appears in? (No glosses used)")
    print("=" * 72)
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}

    results = {}
    for atom in sorted(atom_profiles.keys(),
                       key=lambda x: atom_profiles[x]["n_tokens"],
                       reverse=True):
        # Find all compounds containing this atom
        contributions = []
        compound_names = []

        for mid, prof in profiles.items():
            if len(mid) < 2:
                continue
            if atom not in mid:
                continue
            # Check all other chars are known atoms
            other_chars = [ch for ch in mid if ch != atom]
            if not all(ch in atom_profiles for ch in other_chars):
                continue
            if not other_chars:
                continue  # Skip pure repeats like 'ee' for atom 'e'

            # Compute other atoms' mean profile
            other_vecs = [profile_to_vector(atom_profiles[ch])
                          for ch in other_chars]
            other_mean = vec_mean(other_vecs)

            # A's contribution = compound - other_mean
            compound_vec = profile_to_vector(prof)
            contribution = vec_subtract(compound_vec, other_mean)
            contributions.append(contribution)
            compound_names.append(mid)

        if len(contributions) < 2:
            results[atom] = {
                "bcs": None, "n_compounds": len(contributions),
                "status": "INSUFFICIENT_DATA"
            }
            continue

        # Pairwise correlations of contributions
        n_pairs = 0
        corr_sum = 0.0
        for i in range(len(contributions)):
            for j in range(i + 1, len(contributions)):
                r = vec_correlation(contributions[i], contributions[j])
                corr_sum += r
                n_pairs += 1

        bcs = corr_sum / n_pairs if n_pairs > 0 else 0.0

        results[atom] = {
            "bcs": round(bcs, 4),
            "n_compounds": len(contributions),
            "compounds": compound_names,
            "status": "STRONG" if bcs >= 0.6 else
                      "MODERATE" if bcs >= 0.3 else
                      "WEAK" if bcs >= 0.0 else "INCONSISTENT"
        }

    # Null distribution: permute atom profiles
    random.seed(42)
    atom_keys = list(atom_profiles.keys())
    null_bcs = defaultdict(list)
    n_perms = 500

    for _ in range(n_perms):
        shuffled = atom_keys[:]
        random.shuffle(shuffled)
        perm_map = dict(zip(atom_keys, shuffled))
        perm_profs = {k: atom_profiles[perm_map[k]] for k in atom_keys}

        for atom in atom_keys:
            compounds_for_atom = results.get(atom, {}).get("compounds", [])
            if len(compounds_for_atom) < 2:
                continue

            contribs = []
            for mid in compounds_for_atom:
                if mid not in profiles:
                    continue
                other_chars = [ch for ch in mid if ch != atom]
                if not all(ch in perm_profs for ch in other_chars):
                    continue
                if not other_chars:
                    continue
                other_vecs = [profile_to_vector(perm_profs[ch])
                              for ch in other_chars]
                other_mean = vec_mean(other_vecs)
                compound_vec = profile_to_vector(profiles[mid])
                contribs.append(vec_subtract(compound_vec, other_mean))

            if len(contribs) >= 2:
                pairs = 0
                cs = 0.0
                for i in range(len(contribs)):
                    for j in range(i + 1, len(contribs)):
                        cs += vec_correlation(contribs[i], contribs[j])
                        pairs += 1
                null_bcs[atom].append(cs / pairs if pairs > 0 else 0.0)

    # Add null percentile to results
    for atom in results:
        if results[atom]["bcs"] is None:
            results[atom]["null_percentile"] = None
            continue
        null_scores = null_bcs.get(atom, [])
        if not null_scores:
            results[atom]["null_percentile"] = None
            continue
        real = results[atom]["bcs"]
        pct = sum(1 for s in null_scores if s < real) / len(null_scores)
        results[atom]["null_percentile"] = round(pct * 100, 1)

    # Display
    print(f"  {'Atom':4s} {'Gloss':12s} {'BCS':>6s} {'Null%':>6s} "
          f"{'Compounds':>9s} {'Status':15s}")
    print(f"  {'----':4s} {'-----':12s} {'---':>6s} {'-----':>6s} "
          f"{'---------':>9s} {'------':15s}")

    mid_dict = load_middle_dictionary()
    for atom in sorted(results.keys(),
                       key=lambda x: (results[x]["bcs"] or -1),
                       reverse=True):
        r = results[atom]
        gloss = mid_dict.get(atom, {}).get("gloss") or "?"
        bcs_str = f"{r['bcs']:.3f}" if r["bcs"] is not None else "  N/A"
        null_str = (f"{r['null_percentile']:5.1f}"
                    if r.get("null_percentile") is not None else "  N/A")
        print(f"  {atom:4s} {gloss:12s} {bcs_str:>6s} {null_str:>6s} "
              f"{r['n_compounds']:9d} {r['status']:15s}")

    print()
    return results


# ============================================================
# T2: CROSS-POSITION CONSISTENCY
# ============================================================

def test_2_cross_position(middle_shared, prefix_profiles,
                          suffix_profiles, sections):
    """Test whether atoms behave the same across PREFIX/MIDDLE/SUFFIX."""
    print("=" * 72)
    print("T2: CROSS-POSITION CONSISTENCY")
    print("Does each atom carry the same behavioral signature")
    print("regardless of morphological position? (No glosses used)")
    print("=" * 72)
    print()

    all_chars = set(middle_shared.keys()) | set(prefix_profiles.keys()) | \
                set(suffix_profiles.keys())

    results = {}
    for ch in sorted(all_chars):
        positions_present = []
        vecs = {}

        if ch in middle_shared:
            positions_present.append("M")
            vecs["M"] = shared_profile_to_vector(middle_shared[ch])
        if ch in prefix_profiles:
            positions_present.append("P")
            vecs["P"] = shared_profile_to_vector(prefix_profiles[ch])
        if ch in suffix_profiles:
            positions_present.append("S")
            vecs["S"] = shared_profile_to_vector(suffix_profiles[ch])

        if len(positions_present) < 2:
            results[ch] = {
                "cpc": None,
                "positions": positions_present,
                "status": "SINGLE_POSITION"
            }
            continue

        # Pairwise correlation
        pairs = []
        pair_labels = []
        pos_list = list(vecs.keys())
        for i in range(len(pos_list)):
            for j in range(i + 1, len(pos_list)):
                r = vec_correlation(vecs[pos_list[i]], vecs[pos_list[j]])
                pairs.append(r)
                pair_labels.append(f"{pos_list[i]}-{pos_list[j]}")

        cpc = sum(pairs) / len(pairs)

        results[ch] = {
            "cpc": round(cpc, 4),
            "positions": positions_present,
            "pair_correlations": {lbl: round(r, 4)
                                  for lbl, r in zip(pair_labels, pairs)},
            "n_positions": len(positions_present),
            "status": "CONSISTENT" if cpc >= 0.7 else
                      "MODERATE" if cpc >= 0.3 else
                      "DIVERGENT"
        }

    # Display
    mid_dict = load_middle_dictionary()
    print(f"  {'Char':4s} {'Gloss':12s} {'CPC':>6s} {'Positions':10s} "
          f"{'Pairs':30s} {'Status':12s}")
    print(f"  {'----':4s} {'-----':12s} {'---':>6s} {'---':10s} "
          f"{'-----':30s} {'------':12s}")

    for ch in sorted(results.keys(),
                     key=lambda x: (results[x]["cpc"] or -99),
                     reverse=True):
        r = results[ch]
        gloss = mid_dict.get(ch, {}).get("gloss") or "?"
        cpc_str = f"{r['cpc']:.3f}" if r["cpc"] is not None else "  N/A"
        pos_str = "/".join(r["positions"])
        pair_str = ", ".join(f"{k}:{v:.2f}"
                            for k, v in r.get("pair_correlations", {}).items())
        if len(pair_str) > 30:
            pair_str = pair_str[:27] + "..."
        print(f"  {ch:4s} {gloss:12s} {cpc_str:>6s} {pos_str:10s} "
              f"{pair_str:30s} {r['status']:12s}")

    print()
    return results


# ============================================================
# T3: COMPOUND GLOSS AUDIT
# ============================================================

def test_3_gloss_audit(mid_dict, atoms):
    """Generate human-evaluable decomposition table.

    For each glossed compound, shows:
    - Compound MIDDLE and its gloss
    - Atom decomposition with individual glosses
    - Composed reading (atom glosses joined)
    - Human should evaluate: CONSISTENT / COMPATIBLE / INCONSISTENT
    """
    print("=" * 72)
    print("T3: COMPOUND GLOSS AUDIT")
    print("For each glossed compound: does atom composition match?")
    print("Mark: [C]onsistent / [~]Compatible / [X]Inconsistent")
    print("=" * 72)
    print()

    compounds = get_glossed_compounds(mid_dict, atoms)

    # Group by evaluation category
    full_decomp = []  # All atoms have glosses
    partial_decomp = []  # Some atoms lack glosses

    for c in compounds:
        atom_parts = []
        all_glossed = True
        for ch in c["middle"]:
            if ch in atoms and atoms[ch]["gloss"]:
                atom_parts.append(f"{ch}({atoms[ch]['gloss']})")
            elif ch in atoms:
                atom_parts.append(f"{ch}(?)")
                all_glossed = False
            else:
                atom_parts.append(f"{ch}(??)")
                all_glossed = False

        composed = " + ".join(atom_parts)
        entry = {
            "middle": c["middle"],
            "tokens": c["tokens"],
            "compound_gloss": c["gloss"],
            "composed": composed,
            "all_glossed": all_glossed,
        }

        if all_glossed:
            full_decomp.append(entry)
        else:
            partial_decomp.append(entry)

    print(f"FULLY DECOMPOSABLE ({len(full_decomp)} compounds, all atoms glossed)")
    print("-" * 72)
    print(f"  {'MIDDLE':10s} {'Tokens':>5s}  {'Compound Gloss':20s}  "
          f"{'Atom Decomposition'}")
    print(f"  {'------':10s} {'-----':>5s}  {'-----':20s}  {'-----'}")

    # Track per-atom scores for crossword consistency
    atom_compound_fits = defaultdict(list)

    for e in full_decomp:
        marker = ""
        # Simple automated check: word overlap between composed and actual
        comp_words = set(e["compound_gloss"].lower().replace("-", " ").split())
        atom_words = set()
        for ch in e["middle"]:
            if atoms.get(ch, {}).get("gloss"):
                atom_words.add(atoms[ch]["gloss"].lower())

        overlap = comp_words & atom_words
        if overlap:
            marker = " [C]"
        elif len(comp_words) == 1 and len(e["middle"]) == 2:
            marker = " [?]"

        print(f"  {e['middle']:10s} {e['tokens']:5d}  {e['compound_gloss']:20s}  "
              f"{e['composed']}{marker}")

        for ch in e["middle"]:
            atom_compound_fits[ch].append({
                "compound": e["middle"],
                "compound_gloss": e["compound_gloss"],
                "has_overlap": bool(overlap),
            })

    print()

    if partial_decomp:
        print(f"PARTIAL ({len(partial_decomp)} compounds, some atoms unglossed)")
        print("-" * 72)
        for e in partial_decomp:
            print(f"  {e['middle']:10s} {e['tokens']:5d}  "
                  f"{e['compound_gloss']:20s}  {e['composed']}")
        print()

    # Per-atom crossword summary
    print("PER-ATOM CROSSWORD SUMMARY")
    print("How many compounds does each atom appear in? How many overlap?")
    print("-" * 72)
    print(f"  {'Atom':4s} {'Gloss':12s} {'Total':>5s} {'Overlap':>7s} "
          f"{'Rate':>6s} {'Status':12s}")
    print(f"  {'----':4s} {'-----':12s} {'-----':>5s} {'-------':>7s} "
          f"{'----':>6s} {'------':12s}")

    atom_ccs = {}
    for atom in sorted(atom_compound_fits.keys(),
                       key=lambda x: len(atom_compound_fits[x]),
                       reverse=True):
        fits = atom_compound_fits[atom]
        n_total = len(fits)
        n_overlap = sum(1 for f in fits if f["has_overlap"])
        rate = n_overlap / n_total if n_total > 0 else 0
        gloss = atoms.get(atom, {}).get("gloss", "?")

        status = ("STRONG" if rate >= 0.5 else
                  "MODERATE" if rate >= 0.3 else
                  "WEAK" if rate >= 0.1 else "POOR")

        atom_ccs[atom] = {
            "n_compounds": n_total,
            "n_overlap": n_overlap,
            "overlap_rate": round(rate, 3),
            "status": status,
            "compounds": fits,
        }
        print(f"  {atom:4s} {gloss:12s} {n_total:5d} {n_overlap:7d} "
              f"{rate:6.2f} {status:12s}")

    print()
    return {"full_decomp": full_decomp, "partial_decomp": partial_decomp,
            "atom_ccs": atom_ccs}


# ============================================================
# T4: DISCRIMINATIVE POWER
# ============================================================

def test_4_discriminative_power(profiles, sections):
    """Test whether each atom's behavioral profile is unique.

    For each atom A, compute how well A's profile predicts compounds
    containing A. Then try substituting every other atom's profile for A.
    DPS = real_accuracy - best_substitute_accuracy.
    """
    print("=" * 72)
    print("T4: DISCRIMINATIVE POWER")
    print("Is each atom's behavioral profile unique, or could another")
    print("atom substitute without loss? (No glosses used)")
    print("=" * 72)
    print()

    atom_profiles = {m: p for m, p in profiles.items() if len(m) == 1}
    atom_keys = sorted(atom_profiles.keys())

    results = {}
    for atom in atom_keys:
        # Find compounds containing this atom
        test_compounds = []
        for mid, prof in profiles.items():
            if len(mid) < 2 or atom not in mid:
                continue
            other_chars = [ch for ch in mid if ch != atom]
            if not all(ch in atom_profiles for ch in other_chars):
                continue
            if not other_chars:
                continue
            test_compounds.append((mid, prof))

        if len(test_compounds) < 3:
            results[atom] = {"dps": None, "status": "INSUFFICIENT_DATA",
                             "n_compounds": len(test_compounds)}
            continue

        # Real prediction accuracy: predict compound = mean(atom profiles)
        def predict_accuracy(atom_id, use_profile):
            corrs = []
            for mid, actual_prof in test_compounds:
                # Build prediction from atoms (using use_profile for atom_id)
                atom_vecs = []
                for ch in mid:
                    if ch == atom:
                        atom_vecs.append(profile_to_vector(use_profile))
                    else:
                        atom_vecs.append(
                            profile_to_vector(atom_profiles[ch]))
                pred = vec_mean(atom_vecs)
                actual = profile_to_vector(actual_prof)
                corrs.append(vec_correlation(pred, actual))
            return sum(corrs) / len(corrs) if corrs else 0.0

        real_acc = predict_accuracy(atom, atom_profiles[atom])

        # Try substituting each other atom's profile
        best_sub = None
        best_sub_acc = -1
        for other in atom_keys:
            if other == atom:
                continue
            sub_acc = predict_accuracy(atom, atom_profiles[other])
            if sub_acc > best_sub_acc:
                best_sub_acc = sub_acc
                best_sub = other

        dps = real_acc - best_sub_acc

        results[atom] = {
            "dps": round(dps, 4),
            "real_accuracy": round(real_acc, 4),
            "best_substitute": best_sub,
            "best_sub_accuracy": round(best_sub_acc, 4),
            "n_compounds": len(test_compounds),
            "status": ("UNIQUE" if dps >= 0.1 else
                       "MODERATE" if dps >= 0.03 else
                       "REPLACEABLE" if dps >= 0.0 else
                       "WORSE_THAN_SUB")
        }

    # Display
    mid_dict = load_middle_dictionary()
    print(f"  {'Atom':4s} {'Gloss':12s} {'Real':>6s} {'BestSub':>7s} "
          f"{'Sub':3s} {'DPS':>6s} {'N':>4s} {'Status':15s}")
    print(f"  {'----':4s} {'-----':12s} {'----':>6s} {'-------':>7s} "
          f"{'---':3s} {'---':>6s} {'--':>4s} {'------':15s}")

    for atom in sorted(results.keys(),
                       key=lambda x: (results[x]["dps"] or -99),
                       reverse=True):
        r = results[atom]
        gloss = mid_dict.get(atom, {}).get("gloss") or "?"
        if r["dps"] is None:
            print(f"  {atom:4s} {gloss:12s} {'N/A':>6s} {'N/A':>7s} "
                  f"{'':3s} {'N/A':>6s} {r['n_compounds']:4d} "
                  f"{r['status']:15s}")
        else:
            print(f"  {atom:4s} {gloss:12s} {r['real_accuracy']:6.3f} "
                  f"{r['best_sub_accuracy']:7.3f} "
                  f"{r['best_substitute']:3s} {r['dps']:6.3f} "
                  f"{r['n_compounds']:4d} {r['status']:15s}")

    print()
    return results


# ============================================================
# INTEGRATED SCORECARD
# ============================================================

def build_scorecard(t1_results, t2_results, t3_results, t4_results):
    """Combine all test results into a unified atom scorecard."""
    print("=" * 72)
    print("INTEGRATED ATOM SCORECARD")
    print("=" * 72)
    print()

    mid_dict = load_middle_dictionary()
    all_atoms = sorted(set(list(t1_results.keys()) +
                           list(t2_results.keys()) +
                           list(t4_results.keys())),
                       key=lambda x: mid_dict.get(x, {}).get(
                           "token_count", 0), reverse=True)

    # Only include actual single-char atoms
    all_atoms = [a for a in all_atoms if len(a) == 1 and
                 a in mid_dict and mid_dict[a].get("token_count", 0) >= 5]

    print(f"  {'Atom':4s} {'Gloss':12s} {'Tokens':>6s} "
          f"{'T1:BCS':>7s} {'Null%':>6s} "
          f"{'T2:CPC':>7s} "
          f"{'T4:DPS':>7s} "
          f"{'Verdict':20s}")
    print(f"  {'----':4s} {'-----':12s} {'------':>6s} "
          f"{'------':>7s} {'-----':>6s} "
          f"{'------':>7s} "
          f"{'------':>7s} "
          f"{'-------':20s}")

    scorecard = {}
    for atom in all_atoms:
        gloss = mid_dict.get(atom, {}).get("gloss") or "?"
        tokens = mid_dict.get(atom, {}).get("token_count", 0)

        bcs = t1_results.get(atom, {}).get("bcs")
        null_pct = t1_results.get(atom, {}).get("null_percentile")
        cpc = t2_results.get(atom, {}).get("cpc")
        dps = t4_results.get(atom, {}).get("dps")
        t3_atom = t3_results.get("atom_ccs", {}).get(atom, {})
        overlap_rate = t3_atom.get("overlap_rate")

        # Compute verdict
        issues = []
        if bcs is not None and bcs < 0.3:
            issues.append("LOW_CONSISTENCY")
        if null_pct is not None and null_pct < 80:
            issues.append("NEAR_NULL")
        if cpc is not None and cpc < 0.3:
            issues.append("POSITION_DIVERGENT")
        if dps is not None and dps < 0.0:
            issues.append("WORSE_THAN_SUB")
        elif dps is not None and dps < 0.03:
            issues.append("REPLACEABLE")

        if not issues:
            if bcs is not None and bcs >= 0.6 and (dps is None or dps >= 0.1):
                verdict = "VALIDATED"
            elif bcs is not None and bcs >= 0.3:
                verdict = "ACCEPTABLE"
            else:
                verdict = "INSUFFICIENT_DATA"
        else:
            verdict = "REVIEW: " + ", ".join(issues[:2])

        bcs_str = f"{bcs:.3f}" if bcs is not None else "  N/A"
        null_str = f"{null_pct:5.1f}" if null_pct is not None else "  N/A"
        cpc_str = f"{cpc:.3f}" if cpc is not None else "  N/A"
        dps_str = f"{dps:.3f}" if dps is not None else "  N/A"

        print(f"  {atom:4s} {gloss:12s} {tokens:6d} "
              f"{bcs_str:>7s} {null_str:>6s} "
              f"{cpc_str:>7s} "
              f"{dps_str:>7s} "
              f"{verdict:20s}")

        scorecard[atom] = {
            "gloss": gloss,
            "tokens": tokens,
            "t1_bcs": bcs,
            "t1_null_percentile": null_pct,
            "t2_cpc": cpc,
            "t3_overlap_rate": overlap_rate,
            "t4_dps": dps,
            "verdict": verdict,
        }

    print()

    # Summary statistics
    verdicts = Counter(v["verdict"].split(":")[0].strip()
                       for v in scorecard.values())
    print(f"  Summary: {dict(verdicts)}")
    print()

    # Flag atoms needing review
    flagged = [(a, v) for a, v in scorecard.items()
               if v["verdict"].startswith("REVIEW")]
    if flagged:
        print("  ATOMS FLAGGED FOR REVIEW:")
        for atom, v in flagged:
            print(f"    {atom} ({v['gloss']}): {v['verdict']}")
        print()

    return scorecard


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 72)
    print("CROSSWORD GLOSS VALIDATION — Phase 422")
    print("Tests atom gloss consistency via behavioral crossword constraints")
    print("=" * 72)
    print()

    # Load data
    mid_dict = load_middle_dictionary()
    atoms = get_atoms(mid_dict)
    print(f"Loaded {len(mid_dict)} MIDDLEs, {len(atoms)} single-char atoms")
    print(f"Atoms with glosses: "
          f"{sum(1 for a in atoms.values() if a['gloss'])}/{len(atoms)}")
    print()

    # Compute behavioral profiles
    print("Computing behavioral profiles...")
    (profiles, prefix_profiles, suffix_profiles,
     middle_shared_profiles, sections) = compute_behavioral_profiles()
    print(f"  MIDDLE profiles: {len(profiles)} (>= 5 tokens)")
    print(f"  PREFIX-position profiles: {len(prefix_profiles)} characters")
    print(f"  SUFFIX-position profiles: {len(suffix_profiles)} characters")
    print(f"  Sections: {sections}")
    print()

    # Run test battery
    t1 = test_1_behavioral_consistency(profiles, sections)
    t2 = test_2_cross_position(middle_shared_profiles, prefix_profiles,
                               suffix_profiles, sections)
    t3 = test_3_gloss_audit(mid_dict, atoms)
    t4 = test_4_discriminative_power(profiles, sections)

    # Integrated scorecard
    scorecard = build_scorecard(t1, t2, t3, t4)

    # Save results
    results = {
        "t1_behavioral_consistency": {
            k: {kk: vv for kk, vv in v.items() if kk != "compounds"}
            for k, v in t1.items()
        },
        "t2_cross_position": t2,
        "t3_gloss_audit": {
            "n_full": len(t3["full_decomp"]),
            "n_partial": len(t3["partial_decomp"]),
            "atom_ccs": {
                k: {kk: vv for kk, vv in v.items() if kk != "compounds"}
                for k, v in t3.get("atom_ccs", {}).items()
            },
        },
        "t4_discriminative_power": t4,
        "scorecard": scorecard,
    }

    out_path = RESULTS_DIR / "crossword_validation.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()

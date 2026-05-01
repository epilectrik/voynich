"""
Phase 671 Script 1: dar bimodality vs clause-structure hypothesis.

Pre-registered falsifiers (run BEFORE joint test):
  F1. Pre-screen: do "headless" tokens (no HEAD atom at MIDDLE position 0)
      themselves cluster within lines? If uniform, abandon.
  F2. a-HEAD frame leakage: do other a-HEAD r-terminal tokens (kar, tar, ar,
      etc.) share dar's bimodal profile? If yes, finding is a-HEAD-frame, not
      dar-specific.
  F3. Paragraph-zone residualization: residualize dar position by
      (par_initial × line_position_in_paragraph). Does BC drop below 0.4?
      If yes, dar bimodality is paragraph-position aggregation artifact.

Joint test (only if F1 passes and F3 doesn't kill):
  J1. Length-conditional peak tracking: do dar's bimodal peaks SHIFT with
      line length, or stay position-absolute? Shifting → clause structure.
  J2. Mutual information: I(dar_pos_decile; nearest_headless_offset |
      length_bin) — significant MI vs shuffle null = clause-structure signal.

Output: phases/PHASE_671_DAR_CLAUSE_STRUCTURE/results/dar_clause_structure.json
"""
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "dar_clause_structure.json"

HEAD_ATOMS = frozenset("aeokt")
TERM_ATOMS = frozenset("ynmhlrkt")


# ============================================================
# Helpers
# ============================================================

def is_headless_token(word: str, morph: Morphology) -> bool:
    """True if MIDDLE has no HEAD atom at position 0."""
    if not word.strip() or "*" in word:
        return False
    a = morph.atomize(word)
    return a.is_headless


def is_a_head_r_term(word: str, morph: Morphology) -> bool:
    """True if token is an a-HEAD r-TERM token (e.g., dar, kar, tar, ar, qokar)."""
    if not word.strip() or "*" in word or not word.endswith("r"):
        return False
    a = morph.atomize(word)
    if a.is_headless:
        return False
    if not a.atoms:
        return False
    head_char, head_role, _ = a.atoms[0]
    return head_role == "HEAD" and head_char == "a"


def gather_lines(tokens):
    """Group H-track B tokens into actual lines, recording per-token attrs."""
    by_line = defaultdict(list)
    for t in tokens:
        if "*" in t.word or not t.word.strip():
            continue
        if t.is_label:
            continue
        by_line[(t.folio, t.line)].append({
            "word": t.word,
            "par_initial": t.par_initial,
            "line_initial": t.line_initial,
            "line_final": t.line_final,
        })
    return by_line


def position_distribution(positions):
    """Return mean, std, var, deciles, skew, kurt, BC."""
    n = len(positions)
    if n == 0:
        return None
    m = sum(positions) / n
    var = sum((p - m) ** 2 for p in positions) / n
    std = var ** 0.5
    bins = [0] * 10
    for p in positions:
        bins[min(9, int(p * 10))] += 1
    deciles = [b / n * 100 for b in bins]
    if std > 0:
        skew = sum(((p - m) / std) ** 3 for p in positions) / n
        kurt = sum(((p - m) / std) ** 4 for p in positions) / n
    else:
        skew, kurt = 0, 0
    bc = (skew * skew + 1) / kurt if kurt > 0 else 0
    return {"n": n, "mean": m, "std": std, "var": var, "deciles": deciles,
            "skew": skew, "kurt": kurt, "bimod_coef": bc, "bimodal": bc > 0.555}


# ============================================================
# F1: Headless pre-screen
# ============================================================

def f1_headless_prescreen(by_line, morph):
    """Compute headless-token positions across lines (len>=4, body-only)."""
    print("\n=== F1: HEADLESS PRE-SCREEN ===")
    positions = []
    para_zone_positions = defaultdict(list)
    headless_words = set()

    for (folio, _), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        # Body-only: skip if first token is line_initial AND par_initial
        if tokens_in_line[0]["par_initial"]:
            continue
        for i, t in enumerate(tokens_in_line):
            if is_headless_token(t["word"], morph):
                pos = i / (n - 1)
                positions.append(pos)
                headless_words.add(t["word"])

    stats = position_distribution(positions)
    print(f"  Headless tokens (body-only, line>=4): n={stats['n']}")
    print(f"  Mean={stats['mean']:.3f}  std={stats['std']:.3f}  BC={stats['bimod_coef']:.3f}")
    print(f"  Deciles: " + " ".join(f"{d:5.2f}" for d in stats["deciles"]))
    print(f"  Unique headless word forms: {len(headless_words)}")
    # Verdict: do they cluster (non-uniform) at all?
    chi_sq = sum((d - 10) ** 2 / 10 for d in stats["deciles"])
    print(f"  Chi-sq (uniform null): {chi_sq:.2f}  (df=9, crit=16.92 at p=0.05)")
    return {"stats": stats, "chi_sq": chi_sq, "n_unique_words": len(headless_words),
            "non_uniform": chi_sq > 16.92}


# ============================================================
# F2: a-HEAD frame leakage control
# ============================================================

def f2_a_head_control(by_line, morph):
    """Compare dar's bimodality against other a-HEAD r-terminal tokens."""
    print("\n=== F2: a-HEAD r-TERMINAL CONTROL ===")
    a_head_r_term_positions = defaultdict(list)
    for (folio, _), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        if tokens_in_line[0]["par_initial"]:
            continue
        for i, t in enumerate(tokens_in_line):
            if is_a_head_r_term(t["word"], morph):
                pos = i / (n - 1)
                a_head_r_term_positions[t["word"]].append(pos)

    out = {}
    print(f"  {'Token':<12} {'N':>5} {'Mean':>6}  {'BC':>6}  Bimodal?")
    for w, positions in sorted(a_head_r_term_positions.items(), key=lambda x: -len(x[1])):
        if len(positions) < 30:
            continue
        s = position_distribution(positions)
        out[w] = s
        flag = "YES" if s["bimodal"] else "no"
        print(f"  {w:<12} {s['n']:>5} {s['mean']:>6.3f}  {s['bimod_coef']:>6.3f}  {flag}")
    return out


# ============================================================
# F3: Paragraph-zone residualization
# ============================================================

def line_position_in_paragraph(by_line):
    """Assign each line an ordinal position within its paragraph.

    Approximation: par_initial flag marks first token of a paragraph. We
    group lines by paragraph (consecutive lines on same folio, separated
    when par_initial appears). Returns dict (folio, line) → (zone_idx, total).
    """
    # Sort lines per folio in line-number order
    folios = defaultdict(list)
    for (folio, line), tokens in by_line.items():
        folios[folio].append((line, tokens))
    pos_map = {}
    for folio, line_list in folios.items():
        # Sort by line number lexicographically (numeric prefix first)
        def line_key(item):
            ln = item[0]
            try:
                return (int(ln.split(".")[0]), ln)
            except Exception:
                return (999, ln)
        line_list.sort(key=line_key)
        # Group into paragraphs based on par_initial of first token
        current_para = []
        for line, tokens in line_list:
            if tokens and tokens[0]["par_initial"] and current_para:
                # Flush current paragraph
                total = len(current_para)
                for idx, (l, _) in enumerate(current_para):
                    pos_map[(folio, l)] = (idx, total)
                current_para = []
            current_para.append((line, tokens))
        if current_para:
            total = len(current_para)
            for idx, (l, _) in enumerate(current_para):
                pos_map[(folio, l)] = (idx, total)
    return pos_map


def f3_paragraph_residualization(by_line, morph, pos_map):
    """Residualize dar position by (paragraph zone × line_position_in_paragraph).

    Compute per-zone mean dar position. Subtract zone-mean from each dar
    position. Recompute BC on residuals (rescaled to [0,1]).
    """
    print("\n=== F3: PARAGRAPH-ZONE RESIDUALIZATION ===")
    # Bin paragraph position into 3 zones: Z1 (first), Z2 (middle), Z3 (last)
    def zone(idx, total):
        if total <= 1:
            return "Z_solo"
        if idx == 0:
            return "Z1_first"
        if idx == total - 1:
            return "Z3_last"
        return "Z2_middle"

    dar_by_zone = defaultdict(list)
    raw_dar_positions = []
    for (folio, line), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        # Skip line 1 of paragraph
        if tokens_in_line[0]["par_initial"]:
            continue
        idx_total = pos_map.get((folio, line))
        if idx_total is None:
            continue
        z = zone(*idx_total)
        for i, t in enumerate(tokens_in_line):
            if t["word"] == "dar":
                pos = i / (n - 1)
                dar_by_zone[z].append(pos)
                raw_dar_positions.append(pos)

    # Per-zone stats
    raw_stats = position_distribution(raw_dar_positions)
    print(f"  Raw dar (body-only): n={raw_stats['n']} mean={raw_stats['mean']:.3f} BC={raw_stats['bimod_coef']:.3f}")
    zone_stats = {}
    for z, positions in sorted(dar_by_zone.items()):
        zone_stats[z] = position_distribution(positions)
        s = zone_stats[z]
        print(f"    {z:<12} n={s['n']:>4} mean={s['mean']:.3f}  BC={s['bimod_coef']:.3f}")

    # Residuals: subtract zone mean from each instance
    residuals = []
    for z, positions in dar_by_zone.items():
        zm = zone_stats[z]["mean"]
        for p in positions:
            residuals.append(p - zm)

    # Rescale residuals to [0,1] to compute BC
    rmin, rmax = min(residuals), max(residuals)
    rescaled = [(r - rmin) / (rmax - rmin) for r in residuals] if rmax > rmin else residuals
    res_stats = position_distribution(rescaled)
    print(f"  Residualized BC: {res_stats['bimod_coef']:.3f}")
    print(f"  BC drop: {raw_stats['bimod_coef']:.3f} -> {res_stats['bimod_coef']:.3f}")
    collapse = res_stats["bimod_coef"] < 0.4
    print(f"  Verdict: {'COLLAPSE (BC<0.4)' if collapse else 'SURVIVES'}")

    return {"raw": raw_stats, "by_zone": zone_stats,
            "residualized": res_stats, "collapse": collapse}


# ============================================================
# J1: Length-conditional peak tracking
# ============================================================

def j1_length_conditional_peaks(by_line):
    """Bin lines by length. Compute dar position distribution per bin.

    If dar marks clause boundaries, peaks should SCALE with length (shift
    inward as length grows). If position-absolute (line-edge artifact),
    peaks stay at 0.0 and 1.0 regardless.
    """
    print("\n=== J1: LENGTH-CONDITIONAL PEAK TRACKING ===")
    bins = {"4-7": [], "8-12": [], "13+": []}
    for (folio, line), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        if tokens_in_line[0]["par_initial"]:
            continue
        if n <= 7:
            key = "4-7"
        elif n <= 12:
            key = "8-12"
        else:
            key = "13+"
        for i, t in enumerate(tokens_in_line):
            if t["word"] == "dar":
                bins[key].append(i / (n - 1))

    out = {}
    print(f"  {'Bin':<6} {'N':>5} {'Mean':>6} {'BC':>6} {'Peak1':>6} {'Peak2':>6}  Deciles")
    for key, positions in bins.items():
        s = position_distribution(positions)
        if s is None or s["n"] < 10:
            continue
        # Find two peaks: highest deciles
        decile_idx = sorted(range(10), key=lambda i: -s["deciles"][i])
        peak1, peak2 = sorted(decile_idx[:2])
        out[key] = {"stats": s, "peaks_decile_idx": [peak1, peak2]}
        peak1_pos = (peak1 + 0.5) / 10
        peak2_pos = (peak2 + 0.5) / 10
        print(f"  {key:<6} {s['n']:>5} {s['mean']:>6.3f} {s['bimod_coef']:>6.3f} "
              f"{peak1_pos:>6.2f} {peak2_pos:>6.2f}  " + " ".join(f"{d:4.1f}" for d in s["deciles"]))
    return out


# ============================================================
# J2: Mutual information dar_pos × headless_offset | length_bin
# ============================================================

def j2_mutual_information(by_line, morph, n_perm=2000):
    """Compute MI(dar_pos_decile; nearest_headless_offset | length_bin).

    For each line containing dar:
      - Compute dar position decile
      - Find nearest headless token; compute signed offset (in tokens, normalized)
    MI captures whether dar systematically lands near (or far from) headless tokens.

    Permutation null: shuffle dar's position within the line (preserving line
    membership and dar count), recompute MI 2000 times.
    """
    print("\n=== J2: MUTUAL INFORMATION ===")
    samples = []  # (dar_decile, nearest_headless_offset_decile, length_bin)

    line_data = []
    for (folio, line), tokens_in_line in by_line.items():
        n = len(tokens_in_line)
        if n < 4:
            continue
        if tokens_in_line[0]["par_initial"]:
            continue
        word_list = [t["word"] for t in tokens_in_line]
        headless_indices = [i for i, w in enumerate(word_list) if is_headless_token(w, morph)]
        if not headless_indices:
            continue
        dar_indices = [i for i, w in enumerate(word_list) if w == "dar"]
        if not dar_indices:
            continue
        line_data.append({"word_list": word_list, "n": n,
                          "headless": headless_indices, "dar": dar_indices})

    def compute_mi(line_data_local, dar_overrides=None):
        samples = []
        for ld in line_data_local:
            n = ld["n"]
            length_bin = "S" if n <= 7 else "M" if n <= 12 else "L"
            dar_idx_list = dar_overrides.get(id(ld), ld["dar"]) if dar_overrides else ld["dar"]
            for di in dar_idx_list:
                # Nearest headless distance
                offsets = [hi - di for hi in ld["headless"]]
                nearest = min(offsets, key=abs)
                norm_offset = nearest / (n - 1)
                # Bin both into deciles (-5 to +5 for offset)
                dar_bin = min(9, int(di / (n - 1) * 10))
                offset_bin = max(-5, min(5, int(norm_offset * 10)))
                samples.append((dar_bin, offset_bin, length_bin))

        # Compute conditional MI: I(D; O | L)
        # Group by length_bin, compute MI per bin, weight by P(L)
        from collections import Counter
        by_bin = defaultdict(list)
        for d, o, l in samples:
            by_bin[l].append((d, o))
        total = sum(len(v) for v in by_bin.values())
        if total == 0:
            return 0
        mi = 0
        for l, pairs in by_bin.items():
            n_l = len(pairs)
            p_l = n_l / total
            # MI within this length bin
            joint = Counter(pairs)
            d_marg = Counter(d for d, o in pairs)
            o_marg = Counter(o for d, o in pairs)
            mi_bin = 0
            for (d, o), c in joint.items():
                p_do = c / n_l
                p_d = d_marg[d] / n_l
                p_o = o_marg[o] / n_l
                if p_d > 0 and p_o > 0 and p_do > 0:
                    mi_bin += p_do * math.log2(p_do / (p_d * p_o))
            mi += p_l * mi_bin
        return mi

    actual_mi = compute_mi(line_data)
    print(f"  Actual conditional MI(dar; headless_offset | length): {actual_mi:.4f} bits")

    # Permutation: shuffle dar positions within each line (uniformly random,
    # preserve count)
    rand_mis = []
    for _ in range(n_perm):
        overrides = {}
        for ld in line_data:
            n_dar = len(ld["dar"])
            new_indices = random.sample(range(ld["n"]), n_dar)
            overrides[id(ld)] = new_indices
        rand_mis.append(compute_mi(line_data, overrides))
    rand_mean = sum(rand_mis) / len(rand_mis)
    p_value = sum(1 for m in rand_mis if m >= actual_mi) / len(rand_mis)
    print(f"  Random null mean MI: {rand_mean:.4f}  p(actual >= random): {p_value:.4f}")
    return {"actual_mi": actual_mi, "random_mean_mi": rand_mean,
            "p_value": p_value, "significant": p_value < 0.01,
            "exciting": actual_mi > 0.05}


# ============================================================
# Main
# ============================================================

def main():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    by_line = gather_lines(b_tokens)
    pos_map = line_position_in_paragraph(by_line)
    print(f"  B tokens (post-filter): {sum(len(v) for v in by_line.values())}")
    print(f"  B lines (post-filter): {len(by_line)}")
    print(f"  Body-only lines (no par-initial): {sum(1 for ts in by_line.values() if not ts[0]['par_initial'])}")

    results = {}

    f1 = f1_headless_prescreen(by_line, morph)
    results["F1_headless_prescreen"] = f1

    f2 = f2_a_head_control(by_line, morph)
    results["F2_a_head_control"] = f2

    f3 = f3_paragraph_residualization(by_line, morph, pos_map)
    results["F3_paragraph_residualization"] = f3

    # Conditional execution
    if not f1["non_uniform"]:
        print("\n!!! F1 FAILED: Headless tokens are uniformly distributed. ABANDONING joint test.")
        results["joint_test_executed"] = False
    elif f3["collapse"]:
        print("\n!!! F3 KILLED IT: dar bimodality collapsed under residualization. SKIPPING joint test.")
        results["joint_test_executed"] = False
    else:
        results["joint_test_executed"] = True
        j1 = j1_length_conditional_peaks(by_line)
        results["J1_length_conditional"] = j1
        j2 = j2_mutual_information(by_line, morph, n_perm=2000)
        results["J2_mutual_information"] = j2

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

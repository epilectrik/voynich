"""
Phase 680 Script 2: Falsifiers for the rosette spatial-pattern claim.

Both experts converged: the apparent spatial pattern (bottom-row fixation,
top-center potable gold, east/west transformations) is likely arithmetic
artifact of rosettes' AZC-like fingerprint preferring low-thermal recipes.

THREE PROBES:
  F1 PERMUTATION NULL: shuffle rosette↔spatial-position 10k times, recompute
     spatial coherence. If real pattern is in top 5% of random arrangements,
     the spatial structure survives.
  F2 SUB-REGION PREDICTIVE TEST (crazy-expert's killer): if rosette sub-region
     composition predicts closest-match better than spatial position, the
     spatial story collapses to fingerprint dominated by sub-region weight.
  F3 WHITELIST SENSITIVITY: re-run with random non-matched B folios as pool.
     If similar spatial pattern persists, geometry is artifact.
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)
OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "falsifier_results.json"

ROSETTES = ["CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW"]
GRID_POSITIONS = {
    "NW": (0, 0), "NORTH": (0, 1), "NE": (0, 2),
    "WEST": (1, 0), "CENTER": (1, 1), "EAST": (1, 2),
    "SW": (2, 0), "SOUTH": (2, 1), "SE": (2, 2),
}
MATCHED_FOLIOS = ["f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v",
                  "f112v", "f103r", "f116r", "f112r"]
FOLIO_LABELS = {
    "f75r": "aqua_vitae", "f76r": "element_separation", "f84r": "gold_dissolution",
    "f79r": "mercury_sublimation", "f82r": "multi_recipe", "f76v": "ferment_conv",
    "f81v": "potable_gold", "f112v": "lunaria_quicksilver", "f103r": "ferment_multipl",
    "f116r": "fixation", "f112r": "red_mercury_tincture",
}


# Reuse fingerprint code structure from s1
def fingerprint_from_words(words, morph):
    n = len(words)
    if n == 0:
        return None
    prefix_count = Counter()
    head_count = Counter()
    term_count = Counter()
    kernel_count = Counter()
    edepth_values = []
    bare_count = 0
    n_atomized = 0
    for w in words:
        word_str = w.get("word") if isinstance(w, dict) else w
        if not word_str:
            continue
        clean = word_str.replace(".", "").replace(",", "").replace("'", "").strip()
        if not clean or "*" in clean:
            continue
        a = morph.atomize(clean)
        prefix_count[a.prefix or "BARE"] += 1
        if not a.prefix:
            bare_count += 1
        if a.atoms:
            n_atomized += 1
            head_char, head_role, _ = a.atoms[0]
            if head_role == "HEAD":
                head_count[head_char] += 1
            term_char, term_role, _ = a.atoms[-1]
            if term_role == "TERM":
                term_count[term_char] += 1
            for ch, role, _ in a.atoms:
                if ch in "kehpc":
                    kernel_count[ch] += 1
            edepth_values.append(a.e_depth)
    if n_atomized == 0:
        return None
    return {
        "n": n, "n_atomized": n_atomized,
        "prefix_rates": {p: c / n for p, c in prefix_count.items()},
        "head_rates": {h: c / n_atomized for h, c in head_count.items()},
        "term_rates": {t: c / n_atomized for t, c in term_count.items()},
        "kernel_rates": {k: c / n_atomized for k, c in kernel_count.items()},
        "edepth_mean": mean(edepth_values) if edepth_values else 0,
        "bare_rate": bare_count / n,
    }


def fingerprint_distance(f1, f2):
    if f1 is None or f2 is None:
        return None
    keys_dict = ["prefix_rates", "head_rates", "term_rates", "kernel_rates"]
    total = 0
    for k in keys_dict:
        d1 = f1.get(k, {})
        d2 = f2.get(k, {})
        all_subkeys = set(d1.keys()) | set(d2.keys())
        for sk in all_subkeys:
            total += abs(d1.get(sk, 0) - d2.get(sk, 0))
    total += abs(f1.get("edepth_mean", 0) - f2.get("edepth_mean", 0))
    total += abs(f1.get("bare_rate", 0) - f2.get("bare_rate", 0))
    return total


def collect_words(rosette_data):
    words = []
    for sub_name, sub in rosette_data.get("sub_regions", {}).items():
        for locus in sub.get("loci", []):
            for w in locus.get("words", []):
                words.append({**w, "sub_region": sub_name})
    return words


def collect_words_by_subregion(rosette_data):
    by_sub = defaultdict(list)
    for sub_name, sub in rosette_data.get("sub_regions", {}).items():
        for locus in sub.get("loci", []):
            for w in locus.get("words", []):
                by_sub[sub_name].append(w)
    return by_sub


def fingerprint_folio(folio, b_tokens, morph):
    folio_tokens = [t for t in b_tokens if t.folio == folio
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    return fingerprint_from_words([{"word": t.word} for t in folio_tokens], morph)


def closest_match(fp, candidate_fps):
    distances = {}
    for k, cfp in candidate_fps.items():
        d = fingerprint_distance(fp, cfp)
        if d is not None:
            distances[k] = d
    if not distances:
        return None, None
    best = min(distances.items(), key=lambda x: x[1])
    return best[0], best[1]


def spatial_coherence_score(closest_assignment):
    """Score the spatial pattern.

    Components:
      1. Bottom-row uniformity: how many of {SW, SOUTH, SE} share same closest match?
      2. Center clustering: does CENTER share closest with adjacent rosettes?
      3. Adjacency uniformity: average pairwise same-match for adjacent cells.

    Returns float; higher = more spatially coherent.
    """
    bottom_row = ["SW", "SOUTH", "SE"]
    bottom_matches = [closest_assignment.get(r) for r in bottom_row if r in closest_assignment]
    bottom_uniform = max(Counter(bottom_matches).values()) if bottom_matches else 0

    top_row = ["NW", "NORTH", "NE"]
    top_matches = [closest_assignment.get(r) for r in top_row if r in closest_assignment]
    top_uniform = max(Counter(top_matches).values()) if top_matches else 0

    # Adjacent same-match (king moves)
    adjacent_pairs = []
    coords = {r: GRID_POSITIONS[r] for r in ROSETTES if r in closest_assignment}
    for r1 in coords:
        for r2 in coords:
            if r1 >= r2:
                continue
            (x1, y1), (x2, y2) = coords[r1], coords[r2]
            if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                if closest_assignment[r1] == closest_assignment[r2]:
                    adjacent_pairs.append(1)
                else:
                    adjacent_pairs.append(0)
    adj_score = mean(adjacent_pairs) if adjacent_pairs else 0

    # Combine: bottom-row uniform + top-row uniform + adjacency
    return {
        "bottom_uniform": bottom_uniform,
        "top_uniform": top_uniform,
        "adjacency_score": adj_score,
        "combined": bottom_uniform + top_uniform + adj_score * 4,
    }


def main():
    print("Loading...")
    rosettes_data = json.load(open(Path(__file__).resolve().parents[3] / "data" / "rosettes_annotated.json", encoding="utf-8"))
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Build rosette fingerprints
    rosette_fps = {}
    for ros in ROSETTES:
        words = collect_words(rosettes_data["entities"].get(ros, {}))
        fp = fingerprint_from_words(words, morph)
        if fp:
            rosette_fps[ros] = fp

    # Build matched folio fingerprints
    folio_fps = {f: fingerprint_folio(f, b_tokens, morph) for f in MATCHED_FOLIOS}
    folio_fps = {k: v for k, v in folio_fps.items() if v is not None}

    # Real assignment
    real_assignment = {ros: closest_match(rosette_fps[ros], folio_fps)[0] for ros in ROSETTES if ros in rosette_fps}
    real_score = spatial_coherence_score(real_assignment)
    print(f"Real assignment: {real_assignment}")
    print(f"Real spatial coherence: {real_score}")

    # === F1: PERMUTATION NULL ON SPATIAL POSITIONS ===
    # Shuffle which rosette is in which spatial position; recompute coherence.
    print("\n=== F1: PERMUTATION NULL ON SPATIAL POSITIONS ===")
    n_perm = 10000
    null_combined = []
    null_bottom = []
    null_top = []
    rosette_list = list(rosette_fps.keys())
    for _ in range(n_perm):
        shuffled = rosette_list[:]
        random.shuffle(shuffled)
        # Assign shuffled rosettes to grid positions in canonical order
        permuted_assignment = {ROSETTES[i]: real_assignment[shuffled[i]] for i in range(len(ROSETTES))}
        score = spatial_coherence_score(permuted_assignment)
        null_combined.append(score["combined"])
        null_bottom.append(score["bottom_uniform"])
        null_top.append(score["top_uniform"])
    p_combined = sum(1 for v in null_combined if v >= real_score["combined"]) / n_perm
    p_bottom = sum(1 for v in null_bottom if v >= real_score["bottom_uniform"]) / n_perm
    p_top = sum(1 for v in null_top if v >= real_score["top_uniform"]) / n_perm
    print(f"  Real combined score: {real_score['combined']:.3f}")
    print(f"  Null mean combined: {mean(null_combined):.3f}")
    print(f"  p(null >= real, combined): {p_combined:.4f}")
    print(f"  p(null >= real, bottom uniform): {p_bottom:.4f}")
    print(f"  p(null >= real, top uniform): {p_top:.4f}")

    # === F2: SUB-REGION VS SPATIAL PREDICTION ===
    # For each rosette, compute fingerprint per sub-region. Does sub-region-dominant
    # composition predict closest-match better than spatial position?
    print("\n=== F2: SUB-REGION vs SPATIAL PREDICTION ===")
    sub_region_assignments = {}
    for ros in ROSETTES:
        if ros not in rosettes_data["entities"]:
            continue
        by_sub = collect_words_by_subregion(rosettes_data["entities"][ros])
        for sub_name, words in by_sub.items():
            if len(words) < 5:
                continue
            fp = fingerprint_from_words(words, morph)
            if fp:
                match, dist = closest_match(fp, folio_fps)
                if match:
                    sub_region_assignments[(ros, sub_name)] = (match, dist)

    print(f"  {'Rosette':<8} {'Sub-region':<14} {'Closest folio':<20} {'distance':<10}")
    for (ros, sub), (match, dist) in sorted(sub_region_assignments.items()):
        print(f"  {ros:<8} {sub:<14} {match} ({FOLIO_LABELS.get(match, '')[:14]}) {dist:.3f}")

    # Compare: does each rosette's whole-fingerprint match align with its
    # dominant sub-region match?
    print("\n  Whole-fingerprint vs dominant sub-region:")
    for ros in ROSETTES:
        if ros not in rosette_fps:
            continue
        whole_match = real_assignment.get(ros)
        sub_matches = [(s, m_d) for (r, s), m_d in sub_region_assignments.items() if r == ros]
        if not sub_matches:
            continue
        # Find largest sub-region by word count
        by_sub = collect_words_by_subregion(rosettes_data["entities"][ros])
        sub_sizes = sorted(((s, len(by_sub[s])) for s in by_sub), key=lambda x: -x[1])
        dominant_sub = sub_sizes[0][0] if sub_sizes else None
        dom_match = sub_region_assignments.get((ros, dominant_sub))
        dom_match_folio = dom_match[0] if dom_match else None
        agree = "AGREE" if whole_match == dom_match_folio else "DIFFER"
        print(f"    {ros:<8} whole->{whole_match} ({FOLIO_LABELS.get(whole_match, '')[:14]}) "
              f"vs dominant_sub={dominant_sub}->{dom_match_folio} ({FOLIO_LABELS.get(dom_match_folio, '')[:14] if dom_match_folio else 'none'}) {agree}")

    # === F3: WHITELIST SENSITIVITY ===
    # Run with random non-matched B folios as pool. Does spatial pattern persist?
    print("\n=== F3: WHITELIST SENSITIVITY (random non-matched folios) ===")
    all_b_folios = sorted(set(t.folio for t in b_tokens))
    non_matched = [f for f in all_b_folios if f not in MATCHED_FOLIOS]
    n_trials = 100
    persist_count = 0
    pattern_examples = []
    for trial in range(n_trials):
        random.seed(trial)
        sample = random.sample(non_matched, 11)
        sample_fps = {f: fingerprint_folio(f, b_tokens, morph) for f in sample}
        sample_fps = {k: v for k, v in sample_fps.items() if v is not None}
        if len(sample_fps) < 4:
            continue
        sample_assignment = {ros: closest_match(rosette_fps[ros], sample_fps)[0] for ros in ROSETTES if ros in rosette_fps}
        sample_score = spatial_coherence_score(sample_assignment)
        if sample_score["combined"] >= real_score["combined"]:
            persist_count += 1
            if len(pattern_examples) < 3:
                pattern_examples.append(sample_assignment)
    print(f"  In {persist_count}/{n_trials} trials with random non-matched pools,")
    print(f"  spatial coherence >= real (combined score {real_score['combined']:.2f})")
    print(f"  -> p(arbitrary pool reproduces pattern): {persist_count/n_trials:.3f}")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "real_assignment": real_assignment,
        "real_score": real_score,
        "F1_permutation_null": {
            "n_perm": n_perm,
            "p_combined": p_combined,
            "p_bottom_uniform": p_bottom,
            "p_top_uniform": p_top,
            "null_mean_combined": mean(null_combined),
        },
        "F2_subregion_assignments": {f"{r}|{s}": {"match": m, "distance": d}
                                       for (r, s), (m, d) in sub_region_assignments.items()},
        "F3_whitelist_sensitivity": {
            "n_trials": n_trials,
            "persist_count": persist_count,
            "p_arbitrary_pool": persist_count / n_trials,
        },
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

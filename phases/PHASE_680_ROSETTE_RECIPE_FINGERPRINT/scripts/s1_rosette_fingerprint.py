"""
Phase 680: Rosette ↔ matched-recipe operational fingerprint comparison.

CONTEXT: Phase 402 (ROSETTES_SYSTEM_REVALIDATION, C1124-C1130) confirmed:
  - Rosettes are AZC-like METALAYER, not B-grammar text
  - 3.05x bridge MIDDLE enrichment
  - All 9 rosettes correlate with Section T (vocab-size artifact)
  - Generic indexing — same B folio set in top-5 for all rosettes
  - Forbidden-bigram compliant but random transition structure

WHAT'S NEW: Phase 668 established 11 matched folio↔recipe pairs (C1971);
C1394 atom model; C1987 cipher invariance; C1988 cardinality. We can now
ask whether specific rosettes resemble specific OPERATIONAL CLASSES
corresponding to matched recipes.

QUESTION: For each of 9 rosettes, compute operational fingerprint (PREFIX
rates, HEAD/TERM atom rates, kernel composition). Compare to fingerprints
of the 11 matched-recipe folios. Identify whether any rosette specifically
resembles an operational class (heat-cycling, fixation, observation, etc.)
encoded in a matched recipe.

NOT pre-registered as a hypothesis test — exploratory inspection.

Output: phases/PHASE_680_ROSETTE_RECIPE_FINGERPRINT/results/
        rosette_fingerprint.json
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "rosette_fingerprint.json"

ROSETTES = ["CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW"]

MATCHED_FOLIOS = ["f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v",
                  "f112v", "f103r", "f116r", "f112r"]
FOLIO_LABELS = {
    "f75r": "aqua_vitae",
    "f76r": "element_separation",
    "f84r": "gold_dissolution",
    "f79r": "mercury_sublimation",
    "f82r": "multi_recipe_aqua",
    "f76v": "ferment_conversion",
    "f81v": "potable_gold",
    "f112v": "lunaria_quicksilver",
    "f103r": "ferment_multipl",
    "f116r": "fixation",
    "f112r": "red_mercury_tincture",
}


def collect_rosette_words(rosette_data):
    """Extract all words from a rosette's sub-regions."""
    words = []
    for sub_name, sub in rosette_data.get("sub_regions", {}).items():
        for locus in sub.get("loci", []):
            for w in locus.get("words", []):
                words.append({
                    "word": w.get("word", ""),
                    "articulator": w.get("articulator"),
                    "prefix": w.get("prefix"),
                    "middle": w.get("middle"),
                    "term": w.get("suffix") or w.get("terminal"),
                    "sub_region": sub_name,
                })
    return words


def fingerprint_from_words(words, morph):
    """Compute operational fingerprint from a list of words.

    For rosettes: words come pre-parsed. We use both pre-parsed prefix and
    re-atomize for HEAD/TERM to ensure consistency with B atomization.
    """
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
        # Drop punctuation/uncertain markers from rosette words
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
        "n": n,
        "n_atomized": n_atomized,
        "prefix_rates": {p: c / n for p, c in prefix_count.items()},
        "head_rates": {h: c / n_atomized for h, c in head_count.items()},
        "term_rates": {t: c / n_atomized for t, c in term_count.items()},
        "kernel_rates": {k: c / n_atomized for k, c in kernel_count.items()},
        "edepth_mean": mean(edepth_values) if edepth_values else 0,
        "bare_rate": bare_count / n,
    }


def fingerprint_folio(folio, b_tokens, morph):
    folio_tokens = [t for t in b_tokens if t.folio == folio
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    return fingerprint_from_words(
        [{"word": t.word} for t in folio_tokens], morph
    )


def fingerprint_distance(f1, f2):
    """Aggregate distance across operational dimensions."""
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
    # e-depth diff
    total += abs(f1.get("edepth_mean", 0) - f2.get("edepth_mean", 0))
    total += abs(f1.get("bare_rate", 0) - f2.get("bare_rate", 0))
    return total


def main():
    print("Loading data...")
    rosettes_data = json.load(open(Path(__file__).resolve().parents[3] / "data" / "rosettes_annotated.json", encoding="utf-8"))
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Build rosette fingerprints
    print("\n=== ROSETTE FINGERPRINTS ===\n")
    rosette_fps = {}
    print(f"  {'Rosette':<8} {'N':>4} {'BARE':>6} {'qo':>5} {'ot':>5} {'ok':>5} {'ch':>5} {'sh':>5}  {'edep':>5}  {'a-H':>5} {'o-H':>5} {'k-H':>5} {'e-H':>5}")
    for ros in ROSETTES:
        words = collect_rosette_words(rosettes_data["entities"].get(ros, {}))
        fp = fingerprint_from_words(words, morph)
        if fp is None:
            print(f"  {ros:<8} (no data)")
            continue
        rosette_fps[ros] = fp
        pr = fp["prefix_rates"]
        hr = fp["head_rates"]
        print(f"  {ros:<8} {fp['n']:>4} "
              f"{fp.get('bare_rate', 0)*100:>5.1f}% "
              f"{pr.get('qo', 0)*100:>4.1f}% {pr.get('ot', 0)*100:>4.1f}% "
              f"{pr.get('ok', 0)*100:>4.1f}% {pr.get('ch', 0)*100:>4.1f}% "
              f"{pr.get('sh', 0)*100:>4.1f}%  "
              f"{fp.get('edepth_mean', 0):>5.2f}  "
              f"{hr.get('a', 0)*100:>4.1f}% {hr.get('o', 0)*100:>4.1f}% "
              f"{hr.get('k', 0)*100:>4.1f}% {hr.get('e', 0)*100:>4.1f}%")

    # Matched folio fingerprints
    print("\n=== MATCHED RECIPE FOLIO FINGERPRINTS ===\n")
    folio_fps = {}
    print(f"  {'Folio':<8} {'Recipe':<22} {'N':>5} {'BARE':>6} {'qo':>5} {'ot':>5} {'ok':>5} {'ch':>5} {'sh':>5}  {'edep':>5}  {'a-H':>5} {'o-H':>5} {'k-H':>5} {'e-H':>5}")
    for folio in MATCHED_FOLIOS:
        fp = fingerprint_folio(folio, b_tokens, morph)
        if fp is None:
            continue
        folio_fps[folio] = fp
        pr = fp["prefix_rates"]
        hr = fp["head_rates"]
        print(f"  {folio:<8} {FOLIO_LABELS[folio]:<22} {fp['n']:>5} "
              f"{fp.get('bare_rate', 0)*100:>5.1f}% "
              f"{pr.get('qo', 0)*100:>4.1f}% {pr.get('ot', 0)*100:>4.1f}% "
              f"{pr.get('ok', 0)*100:>4.1f}% {pr.get('ch', 0)*100:>4.1f}% "
              f"{pr.get('sh', 0)*100:>4.1f}%  "
              f"{fp.get('edepth_mean', 0):>5.2f}  "
              f"{hr.get('a', 0)*100:>4.1f}% {hr.get('o', 0)*100:>4.1f}% "
              f"{hr.get('k', 0)*100:>4.1f}% {hr.get('e', 0)*100:>4.1f}%")

    # === DISTANCE MATRIX ===
    print("\n=== ROSETTE -> CLOSEST MATCHED-RECIPE FOLIO ===\n")
    print(f"  {'Rosette':<8} -> {'Closest folio':<10} {'Recipe':<22} {'distance':<10} (alternatives)")
    distance_matrix = {}
    for ros, ros_fp in rosette_fps.items():
        distances = {}
        for folio, folio_fp in folio_fps.items():
            d = fingerprint_distance(ros_fp, folio_fp)
            if d is not None:
                distances[folio] = d
        sorted_dists = sorted(distances.items(), key=lambda x: x[1])
        distance_matrix[ros] = distances
        if not sorted_dists:
            continue
        top_folio, top_dist = sorted_dists[0]
        alternatives = ", ".join(f"{f}({d:.3f})" for f, d in sorted_dists[1:4])
        print(f"  {ros:<8} -> {top_folio:<10} {FOLIO_LABELS[top_folio]:<22} {top_dist:.3f}      {alternatives}")

    # === FOLIO -> CLOSEST ROSETTE (reverse) ===
    print("\n=== MATCHED-RECIPE FOLIO -> CLOSEST ROSETTE (reverse) ===\n")
    print(f"  {'Folio':<8} {'Recipe':<22} -> {'Closest rosette':<10} {'distance':<10}")
    for folio, folio_fp in folio_fps.items():
        distances = {}
        for ros, ros_fp in rosette_fps.items():
            d = fingerprint_distance(folio_fp, ros_fp)
            if d is not None:
                distances[ros] = d
        sorted_dists = sorted(distances.items(), key=lambda x: x[1])
        if not sorted_dists:
            continue
        top_ros, top_dist = sorted_dists[0]
        print(f"  {folio:<8} {FOLIO_LABELS[folio]:<22} -> {top_ros:<10} {top_dist:.3f}")

    # === SPATIAL PATTERN: 3x3 GRID ===
    print("\n=== SPATIAL GRID (closest-matched recipe per rosette) ===\n")
    grid = {
        "NW": "TL", "NORTH": "TC", "NE": "TR",
        "WEST": "ML", "CENTER": "MC", "EAST": "MR",
        "SW": "BL", "SOUTH": "BC", "SE": "BR",
    }
    closest = {}
    for ros, dists in distance_matrix.items():
        if dists:
            best = min(dists.items(), key=lambda x: x[1])
            closest[ros] = (best[0], FOLIO_LABELS[best[0]], best[1])
    print("       NW                NORTH               NE")
    for row in [("NW", "NORTH", "NE"), ("WEST", "CENTER", "EAST"), ("SW", "SOUTH", "SE")]:
        line = ""
        for ros in row:
            if ros in closest:
                folio, label, dist = closest[ros]
                line += f"  [{ros:<6} {folio} {label[:14]:<14} d={dist:.2f}]"
            else:
                line += f"  [{ros:<6} (no data)]"
        print(line)
    print()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "rosette_fingerprints": rosette_fps,
        "folio_fingerprints": folio_fps,
        "distance_matrix": distance_matrix,
        "closest_matched_per_rosette": {k: list(v) for k, v in closest.items()},
    }, indent=2, default=str))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

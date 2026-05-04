"""
Phase 682 Script 1: Test recipes-as-transitions hypothesis.

Pre-registered protocol locked in PRE_REGISTRATION.md.

Tests:
  1. Recipe start_node != end_node (recipes are transitions)
  2. Recipe (start, end) edges align with rosette paths
  3. Operationally-ordered recipes walk coherent path through rosette graph
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

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "recipe_transitions.json"

ROSETTES = ["CENTER", "NORTH", "NE", "EAST", "SE", "SOUTH", "SW", "WEST", "NW"]

# Octagonal cycle paths
ROSETTE_PATHS = [
    ("NW", "NORTH"), ("NORTH", "NE"), ("NE", "EAST"), ("EAST", "SE"),
    ("SE", "SOUTH"), ("SOUTH", "SW"), ("SW", "WEST"), ("WEST", "NW"),
]
# CENTER is connected to all outer rosettes (treated as universal hub)
CENTER_PATHS = [("CENTER", r) for r in ROSETTES if r != "CENTER"]

# Pre-registered recipe ordering (raw → finished)
RECIPE_ORDER = [
    "f112v", "f76v", "f75r", "f82r", "f76r", "f103r",
    "f79r", "f112r", "f84r", "f81v", "f116r",
]
RECIPE_LABELS = {
    "f112v": "lunaria_quicksilver",
    "f76v": "ferment_conversion",
    "f75r": "aqua_vitae",
    "f82r": "multi_recipe_aqua",
    "f76r": "element_separation",
    "f103r": "ferment_multipl",
    "f79r": "mercury_sublim",
    "f112r": "red_mercury_tincture",
    "f84r": "gold_dissolution",
    "f81v": "potable_gold",
    "f116r": "fixation",
}


def gather_paragraphs(folio, b_tokens):
    folio_tokens = [t for t in b_tokens if t.folio == folio
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    if not folio_tokens:
        return []
    lines = defaultdict(list)
    for t in folio_tokens:
        lines[t.line].append(t)
    sorted_lines = sorted(lines.items(), key=lambda x: (
        int(x[0].split(".")[0]) if x[0].split(".")[0].isdigit() else 999, x[0]))
    paragraphs = []
    current = []
    for line_id, tokens in sorted_lines:
        if tokens and tokens[0].par_initial and current:
            paragraphs.append(current)
            current = []
        current.extend(tokens)
    if current:
        paragraphs.append(current)
    return paragraphs


def fingerprint(token_list, morph):
    n = len(token_list)
    if n == 0:
        return None
    prefix_count = Counter()
    head_count = Counter()
    term_count = Counter()
    edepth_values = []
    bare_count = 0
    n_atomized = 0
    for t in token_list:
        word = t.word if hasattr(t, "word") else t
        if not word:
            continue
        clean = word.replace(".", "").replace(",", "").replace("'", "").strip()
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
            edepth_values.append(a.e_depth)
    if n_atomized == 0:
        return None
    return {
        "n": n, "n_atomized": n_atomized,
        "prefix_rates": {p: c / n for p, c in prefix_count.items()},
        "head_rates": {h: c / n_atomized for h, c in head_count.items()},
        "term_rates": {t: c / n_atomized for t, c in term_count.items()},
        "edepth_mean": mean(edepth_values) if edepth_values else 0,
        "bare_rate": bare_count / n,
    }


def fingerprint_distance(f1, f2):
    if f1 is None or f2 is None:
        return float("inf")
    keys = ["prefix_rates", "head_rates", "term_rates"]
    total = 0
    for k in keys:
        d1 = f1.get(k, {})
        d2 = f2.get(k, {})
        sub = set(d1.keys()) | set(d2.keys())
        for s in sub:
            total += abs(d1.get(s, 0) - d2.get(s, 0))
    total += abs(f1.get("edepth_mean", 0) - f2.get("edepth_mean", 0))
    total += abs(f1.get("bare_rate", 0) - f2.get("bare_rate", 0))
    return total


def collect_rosette_words(rosette_data):
    words = []
    for sub_name, sub in rosette_data.get("sub_regions", {}).items():
        for locus in sub.get("loci", []):
            for w in locus.get("words", []):
                words.append({**w, "sub_region": sub_name})
    return words


def fingerprint_from_word_dicts(word_dicts, morph):
    """Adapt fingerprint() for rosettes data which has dict words."""
    class FakeT:
        def __init__(self, word):
            self.word = word
    tokens = [FakeT(w.get("word", "")) for w in word_dicts]
    return fingerprint(tokens, morph)


def closest_rosette(fp, rosette_fps):
    best = None
    best_d = float("inf")
    for r, rfp in rosette_fps.items():
        d = fingerprint_distance(fp, rfp)
        if d < best_d:
            best_d = d
            best = r
    return best, best_d


def is_adjacent(node1, node2):
    """Check if two rosette nodes are connected by a rosette path."""
    pair = (node1, node2)
    rev = (node2, node1)
    return pair in ROSETTE_PATHS or rev in ROSETTE_PATHS or pair in CENTER_PATHS or rev in CENTER_PATHS


def main():
    print("Loading...")
    rosettes_data = json.load(open(Path(__file__).resolve().parents[3] / "data" / "rosettes_annotated.json", encoding="utf-8"))
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Build rosette node fingerprints
    rosette_fps = {}
    for ros in ROSETTES:
        words = collect_rosette_words(rosettes_data["entities"].get(ros, {}))
        rosette_fps[ros] = fingerprint_from_word_dicts(words, morph)

    # Per recipe: compute start fingerprint (early) and end fingerprint (late)
    print("\n=== RECIPE START vs END FINGERPRINT MAPPING ===\n")
    recipe_results = {}
    for folio in RECIPE_ORDER:
        paragraphs = gather_paragraphs(folio, b_tokens)
        n_paras = len(paragraphs)
        if n_paras < 4:
            print(f"  {folio}: only {n_paras} paragraphs, skipping")
            continue
        start_n = max(1, n_paras // 3) if n_paras < 9 else 3
        end_n = max(1, n_paras // 3) if n_paras < 9 else 3
        start_paras = paragraphs[:start_n]
        end_paras = paragraphs[-end_n:]
        start_tokens = [t for p in start_paras for t in p]
        end_tokens = [t for p in end_paras for t in p]

        start_fp = fingerprint(start_tokens, morph)
        end_fp = fingerprint(end_tokens, morph)
        start_node, start_d = closest_rosette(start_fp, rosette_fps)
        end_node, end_d = closest_rosette(end_fp, rosette_fps)
        adjacent = is_adjacent(start_node, end_node)
        same = start_node == end_node

        recipe_results[folio] = {
            "label": RECIPE_LABELS[folio],
            "n_paragraphs": n_paras,
            "start_paragraphs": start_n,
            "end_paragraphs": end_n,
            "start_node": start_node,
            "start_distance": start_d,
            "end_node": end_node,
            "end_distance": end_d,
            "same_node": same,
            "adjacent_path": adjacent,
        }

        flag = "SAME" if same else ("PATH" if adjacent else "non-adjacent")
        print(f"  {folio:<8} {RECIPE_LABELS[folio]:<22} P{start_n}+P{end_n} of {n_paras:>2}  "
              f"start={start_node:<7} (d={start_d:.2f}) -> end={end_node:<7} (d={end_d:.2f})  [{flag}]")

    # === TEST 1: start != end (recipes are transitions) ===
    n_recipes = len(recipe_results)
    n_diff = sum(1 for r in recipe_results.values() if not r["same_node"])
    print(f"\n=== TEST 1: RECIPES ARE TRANSITIONS ===")
    print(f"  start_node != end_node: {n_diff}/{n_recipes}")
    null_p_diff = 8 / 9  # P(different under random)
    expected = n_recipes * null_p_diff
    print(f"  Null expected: {expected:.1f}/{n_recipes} (random with 9 nodes)")
    pass_test1 = n_diff >= 10  # >= 10 of 11 (above 89% null)
    print(f"  PASS criterion >=10/11: {'PASS' if pass_test1 else 'FAIL'}")

    # === TEST 2: start->end is a rosette path ===
    n_adjacent = sum(1 for r in recipe_results.values() if r["adjacent_path"] and not r["same_node"])
    p_adjacent_random = (8 + 8) / (9 * 8)  # 8 outer paths × 2 directions / 72 = ~0.22
    # Plus 8 center paths × 2 = 16 / 72 = 0.22
    # Total adjacent including center: (16 + 16) / 72 = 0.44 actually
    # Recompute: 8 outer-outer pairs + 8 center-outer pairs = 16 pairs
    # Total pairs (excluding self): 9*8 = 72
    # P(adjacent) = 16 * 2 / 72 = 32/72 = 0.444 with directionality, or 16/36 = 0.444 unordered
    # Wait: 8 outer-outer unordered + 8 center-outer = 16 paths. Total unordered pairs = 36. P=16/36=0.444
    p_adjacent = 16 / 36
    expected_adj = n_recipes * p_adjacent
    print(f"\n=== TEST 2: START->END EDGE IS A ROSETTE PATH ===")
    print(f"  start->end is adjacent: {n_adjacent}/{n_recipes}")
    print(f"  Null expected: {expected_adj:.1f}/{n_recipes} (random with 16/36 paths adjacency)")
    # Binomial pass: P(X >= n_adjacent | n_recipes, p_adjacent) < 0.05
    # We want at least 8/11 to be confident
    pass_test2 = n_adjacent >= 8
    print(f"  PASS criterion >=8/11: {'PASS' if pass_test2 else 'FAIL'}")

    # Permutation null
    n_perm = 10000
    null_n_adjacent = []
    for _ in range(n_perm):
        # Random assignment of (start, end) for each recipe
        n_random = 0
        for _ in range(n_recipes):
            s = random.choice(ROSETTES)
            e = random.choice([r for r in ROSETTES if r != s])
            if is_adjacent(s, e):
                n_random += 1
        null_n_adjacent.append(n_random)
    p_emp = sum(1 for v in null_n_adjacent if v >= n_adjacent) / n_perm
    print(f"  Permutation null mean: {mean(null_n_adjacent):.2f}/{n_recipes}")
    print(f"  p(null >= observed): {p_emp:.4f}")

    # === TEST 3: ordered recipes walk coherent path ===
    print(f"\n=== TEST 3: ORDERED RECIPES WALK COHERENT PATH ===")
    print(f"  Recipe order (raw -> finished): {RECIPE_ORDER}")
    walk = [recipe_results[f]["start_node"] for f in RECIPE_ORDER if f in recipe_results]
    print(f"  Start-node walk: {walk}")
    walk_steps = []
    for i in range(len(walk) - 1):
        n1, n2 = walk[i], walk[i + 1]
        if n1 == n2:
            walk_steps.append(("same", n1, n2))
        elif is_adjacent(n1, n2):
            walk_steps.append(("adjacent", n1, n2))
        else:
            walk_steps.append(("jump", n1, n2))
    n_coherent = sum(1 for s, _, _ in walk_steps if s in ("same", "adjacent"))
    print(f"  Coherent steps (same or adjacent): {n_coherent}/{len(walk_steps)}")
    pass_test3 = n_coherent >= 7

    for step, n1, n2 in walk_steps:
        marker = {"same": "=", "adjacent": "->", "jump": "JUMP"}[step]
        print(f"    {n1} {marker} {n2}")
    print(f"  PASS criterion >=7/{len(walk_steps)}: {'PASS' if pass_test3 else 'FAIL'}")

    # Permutation null for walk coherence
    walk_nulls = []
    for _ in range(n_perm):
        random_walk = [random.choice(ROSETTES) for _ in range(len(walk))]
        n_c = sum(1 for i in range(len(random_walk) - 1)
                  if random_walk[i] == random_walk[i + 1] or is_adjacent(random_walk[i], random_walk[i + 1]))
        walk_nulls.append(n_c)
    p_walk = sum(1 for v in walk_nulls if v >= n_coherent) / n_perm
    print(f"  Permutation null mean coherent steps: {mean(walk_nulls):.2f}/{len(walk_steps)}")
    print(f"  p(null >= observed): {p_walk:.4f}")

    # === VERDICT ===
    print("\n=== VERDICT ===")
    print(f"  Test 1 (transitions, >=10/11): {'PASS' if pass_test1 else 'FAIL'} (got {n_diff}/{n_recipes})")
    print(f"  Test 2 (path-aligned, >=8/11): {'PASS' if pass_test2 else 'FAIL'} (got {n_adjacent}/{n_recipes}, p={p_emp:.4f})")
    print(f"  Test 3 (coherent walk, >=7): {'PASS' if pass_test3 else 'FAIL'} (got {n_coherent}/{len(walk_steps)}, p={p_walk:.4f})")

    if pass_test1 and pass_test2:
        if pass_test3:
            verdict = "STRONG: recipes-as-transitions supported with coherent walk; Tier 3 candidate"
        else:
            verdict = "PARTIAL: recipes are transitions aligned with paths but no clean walk"
    else:
        verdict = "Recipes-as-transitions NOT supported; no registration"
    print(f"  VERDICT: {verdict}")

    # Save
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "recipe_results": recipe_results,
        "n_diff": n_diff,
        "n_adjacent": n_adjacent,
        "n_coherent_walk": n_coherent,
        "p_test2_perm": p_emp,
        "p_test3_perm": p_walk,
        "pass_test1": pass_test1,
        "pass_test2": pass_test2,
        "pass_test3": pass_test3,
        "verdict": verdict,
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

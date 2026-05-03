"""
Phase 677 Stage 2: Test pre-registered iteration cardinality on matched folios.

PRE-REGISTERED counts (locked from Stage 1 source extraction):

  f75r  N=9  qok-class  (TEMPLATE — already confirmed C1965)
  f82r  N=9  qok-class  (same source recipe as f75r)
  f79r  N=3  qok-class  ("third time distill" - III.12)
  f112r N=3  qok-class  ("distill...three times" - III.11)
  f103r N=8  chamber/material count (weak: "four or eight chambers")
  f84r  N=3  weak duration ("three natural days")

  EXCLUDED (no iteration count in source): f76r, f76v, f81v, f112v, f116r

TEST DESIGN:
  For each (folio, N, qok-class) pre-registration:
    1. Find clusters of exactly N qok-class tokens within a 2-line window
    2. Report cluster locations
    3. Compute folio-relative rarity: how often do N-clusters occur on
       OTHER folios in 2-line windows? Lower rate -> more specific.

QOK-CLASS DEFINITION:
  Tokens beginning with qok or qo+k+letter combinations: qokedy, qokeedy,
  qokey, qokeey, qokchdy, qokal, qokar, qokain, qokaiin, qokchy, qokol, etc.
  (per memory's f75r ×9 cluster description)

PASS CRITERION (per crazy-expert):
  >= 5/7 hit within +/-1 of source N. With 6 testable recipes, that means
  at least 4 hits.

  But for clean test: 4 strong cases (f75r/f82r ×9, f79r/f112r ×3) — if
  3-4/4 hit, finding is real. If <2/4 hit, f75r was singular.

OUTPUT: phases/PHASE_677_ITERATION_CARDINALITY/results/cardinality_test.json
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "cardinality_test.json"

# Pre-registered tests
PREREG = [
    {"folio": "f75r",  "N": 9, "class": "qok",       "strength": "strong (template)", "source": "III.19 aqua vitae 9x reflux"},
    {"folio": "f82r",  "N": 9, "class": "qok",       "strength": "strong",            "source": "III.19.1-5 (same chapter as f75r)"},
    {"folio": "f79r",  "N": 3, "class": "qok",       "strength": "strong",            "source": "III.12 'third time distill'"},
    {"folio": "f112r", "N": 3, "class": "qok",       "strength": "strong",            "source": "III.11 'distill...three times'"},
    {"folio": "f103r", "N": 8, "class": "qok",       "strength": "weak",              "source": "III.16 'four or eight chambers'"},
    {"folio": "f84r",  "N": 3, "class": "qok",       "strength": "weak",              "source": "II.12 'three natural days'"},
]

ALL_MATCHED = [p["folio"] for p in PREREG] + ["f76r", "f76v", "f81v", "f112v", "f116r"]


def is_qok_class(word, morph):
    """Token is qok-class if its prefix is 'qok' or 'qo' with k as first MIDDLE atom."""
    if not word.startswith("qo"):
        return False
    a = morph.atomize(word)
    # qok prefix directly
    if a.prefix == "qok":
        return True
    # qo prefix with k as first middle atom (HEAD or PSEUDO_HEAD)
    if a.prefix == "qo" and a.atoms:
        h, _, _ = a.atoms[0]
        if h == "k":
            return True
    return False


def gather_folio_lines(folio_target, b_tokens):
    by_line = defaultdict(list)
    for t in b_tokens:
        if t.folio != folio_target or "*" in t.word or not t.word.strip() or t.is_label:
            continue
        by_line[t.line].append(t)
    sorted_lines = sorted(by_line.items(), key=lambda x: (
        int(x[0].split(".")[0]) if x[0].split(".")[0].isdigit() else 999, x[0]))
    return sorted_lines


def find_clusters_in_folio(folio, b_tokens, morph, target_N, class_check):
    """Find clusters of exactly N qok-class tokens in 2-line windows.

    Returns list of (start_line, end_line, count, words).
    Also returns max-cluster-size on folio.
    """
    lines = gather_folio_lines(folio, b_tokens)
    # Sliding 2-line window
    clusters_at_target = []
    max_cluster = 0
    cluster_distribution = defaultdict(int)

    for i in range(len(lines)):
        # Window of 1 line
        for window_size in [1, 2]:
            if i + window_size > len(lines):
                continue
            window_tokens = []
            for line_id, tokens in lines[i:i+window_size]:
                window_tokens.extend(tokens)
            qok_count = sum(1 for t in window_tokens if class_check(t.word, morph))
            qok_words = [t.word for t in window_tokens if class_check(t.word, morph)]
            cluster_distribution[qok_count] += 1
            if qok_count > max_cluster:
                max_cluster = qok_count
            if qok_count == target_N:
                clusters_at_target.append({
                    "window_size": window_size,
                    "start_line": lines[i][0],
                    "end_line": lines[i+window_size-1][0],
                    "count": qok_count,
                    "qok_words": qok_words,
                })

    return clusters_at_target, max_cluster, dict(cluster_distribution)


def folio_relative_rarity(target_N, all_b_folios, b_tokens, morph, class_check):
    """How rare are clusters of size N in 2-line windows across all folios?"""
    folio_max_clusters = {}
    for folio in all_b_folios:
        _, mx, _ = find_clusters_in_folio(folio, b_tokens, morph, target_N, class_check)
        folio_max_clusters[folio] = mx
    # Folios where max cluster >= N
    n_folios_at_or_above = sum(1 for mx in folio_max_clusters.values() if mx >= target_N)
    pct = n_folios_at_or_above / len(folio_max_clusters) * 100
    return n_folios_at_or_above, len(folio_max_clusters), pct


def main():
    print("Loading...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())
    all_b_folios = sorted(set(t.folio for t in b_tokens))

    results = []
    print("\n=== ITERATION CARDINALITY TEST ===\n")

    # Pre-compute folio-relative rarity for each unique target N
    rarity = {}
    for N in sorted(set(p["N"] for p in PREREG)):
        n_at, n_total, pct = folio_relative_rarity(N, all_b_folios, b_tokens, morph, is_qok_class)
        rarity[N] = {"n_folios_with_max_>=N": n_at, "n_total": n_total, "pct": pct}
        print(f"  N={N}: {n_at}/{n_total} folios ({pct:.1f}%) have max qok-cluster >= N in 2-line window")
    print()

    for prereg in PREREG:
        folio = prereg["folio"]
        N = prereg["N"]
        class_name = prereg["class"]
        strength = prereg["strength"]
        source = prereg["source"]
        clusters, max_cluster, dist = find_clusters_in_folio(folio, b_tokens, morph, N, is_qok_class)
        hit = max_cluster >= N
        within_one = abs(max_cluster - N) <= 1
        result = {
            "folio": folio, "predicted_N": N, "max_observed": max_cluster,
            "hit_at_or_above": hit, "within_pm_1": within_one,
            "clusters_at_N": clusters, "cluster_distribution": dist,
            "strength": strength, "source": source,
        }
        results.append(result)

        verdict = "HIT" if hit else f"MISS (max={max_cluster})"
        verdict_pm = " (within ±1)" if within_one and not hit else ""
        print(f"=== {folio} ({source}) ===")
        print(f"  Predicted: N={N} qok-class cluster (2-line window)")
        print(f"  Observed: max qok-cluster size = {max_cluster}  -> {verdict}{verdict_pm}")
        print(f"  Folio-relative rarity: {rarity[N]['n_folios_with_max_>=N']}/{rarity[N]['n_total']} folios reach N>=this size ({rarity[N]['pct']:.0f}%)")
        if clusters:
            print(f"  Clusters at exactly N={N}:")
            for c in clusters[:3]:
                print(f"    L{c['start_line']}-L{c['end_line']} ({c['window_size']}-line window): {c['qok_words']}")
        else:
            print(f"  No clusters at exactly N={N}.")
        print()

    # === SUMMARY ===
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    n_strong = sum(1 for r in results if r["strength"].startswith("strong"))
    n_strong_hits = sum(1 for r in results if r["strength"].startswith("strong") and r["hit_at_or_above"])
    n_strong_within_1 = sum(1 for r in results if r["strength"].startswith("strong") and r["within_pm_1"])
    n_all = len(results)
    n_all_hits = sum(1 for r in results if r["hit_at_or_above"])
    n_all_within_1 = sum(1 for r in results if r["within_pm_1"])

    print(f"\n  Strong cases (incl. f75r template):")
    print(f"    Hits at N or above:  {n_strong_hits}/{n_strong}")
    print(f"    Within ±1 of N:      {n_strong_within_1}/{n_strong}")
    print(f"\n  All cases (strong + weak):")
    print(f"    Hits at N or above:  {n_all_hits}/{n_all}")
    print(f"    Within ±1 of N:      {n_all_within_1}/{n_all}")

    # Excluding template f75r
    n_test = sum(1 for r in results if r["folio"] != "f75r")
    n_test_hits = sum(1 for r in results if r["folio"] != "f75r" and r["hit_at_or_above"])
    n_test_within_1 = sum(1 for r in results if r["folio"] != "f75r" and r["within_pm_1"])
    print(f"\n  Test cases (excluding f75r template):")
    print(f"    Hits at N or above:  {n_test_hits}/{n_test}")
    print(f"    Within ±1 of N:      {n_test_within_1}/{n_test}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "preregistered": PREREG,
        "rarity_by_N": rarity,
        "results": results,
        "summary": {
            "n_strong": n_strong, "n_strong_hits": n_strong_hits,
            "n_strong_within_1": n_strong_within_1,
            "n_all": n_all, "n_all_hits": n_all_hits,
            "n_all_within_1": n_all_within_1,
            "n_test_excluding_template": n_test,
            "n_test_hits": n_test_hits,
            "n_test_within_1": n_test_within_1,
        },
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

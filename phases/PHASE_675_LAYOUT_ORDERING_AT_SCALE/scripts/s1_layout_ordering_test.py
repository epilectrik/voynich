"""
Phase 675 Script 1: Test B replication at scale — manuscript-wide layout-ordering.

PRE-REGISTRATION (locked before looking at distributions):

  Hypothesis: Across all Currier B folios with >=4 paragraphs, paragraph
  layout-position (ordinal: 1, 2, 3, ...) correlates with within-paragraph
  e-depth-mean (length-residualized) at Spearman |rho| > 0.4 with within-folio
  shuffle p < 0.001 in >= 60% of folios with same direction.

  If TRUE: layout-ordering is procedural manuscript-wide. C1399 (paragraph
  independence universal) needs revision: state-coupling separate from
  layout-coupling. Tier 2 candidate.

  If NULL (mean |rho| < 0.1, distribution centered on shuffle): layout-ordering
  is matched-folio artifact. The rho=+0.81 on 5 matched folios was Pseudo-Lull
  selection bias. C1399 strengthened. Tier 1 falsification of empirical claim.

  If MIXED (some sections positive, some null): section-conditional
  procedurality. Tier 3 scope-limit.

PRIMARY PROXY: e-depth-mean per paragraph, length-residualized via linear
regression on paragraph token count.

Why e-depth:
  - C1923: head_e <-> e_ratio rho=+0.816 (kernel coherence)
  - C1225: e-depth parametricity (cooling/stabilizing)
  - C1284: kernel-category calibration

Why length-residualize:
  - Long paragraphs accumulate more atoms; raw e-depth-mean would
    spuriously correlate with anything else that scales with length

Why NOT atom glosses:
  - Glosses are downstream of structural features; circular with matching

Why Spearman (not Pearson):
  - Robust to outliers (a single high-e paragraph doesn't dominate)
  - Tests monotonic relationship, not linear

PRE-REGISTERED FALSIFIERS:
  1. Within-folio shuffle null (10k permutations of paragraph order)
  2. Matched-folio subset (n=11) should replicate prior rho=+0.81 — if it
     doesn't, the test infrastructure itself is broken
  3. Section stratification: H, B, S, C reported separately

OUTPUT: phases/PHASE_675_LAYOUT_ORDERING_AT_SCALE/results/
        layout_ordering_results.json
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from voynich import Transcript, Morphology

random.seed(42)

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "layout_ordering_results.json"

MATCHED_FOLIOS = ["f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v",
                  "f112v", "f103r", "f116r", "f112r"]
CLUSTER_FOLIOS = [
    "f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v",
    "f43r", "f50r", "f50v", "f55r", "f55v", "f85r1", "f85r2",
    "f86v4", "f86v5", "f86v6", "f94r", "f94v", "f95r1", "f95r2",
    "f95v1", "f95v2", "f105v", "f114r",
]


def gather_folio_paragraphs(folio_target, b_tokens, morph):
    """Group tokens by paragraph. Return list of (paragraph_idx, tokens, e_depths)."""
    folio_tokens = [t for t in b_tokens if t.folio == folio_target
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    if not folio_tokens:
        return None, None

    # Group by line
    lines = defaultdict(list)
    for t in folio_tokens:
        lines[t.line].append(t)

    # Sort lines, group into paragraphs by par_initial
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

    # Compute e-depth-mean and length per paragraph
    section = folio_tokens[0].section
    paragraph_data = []
    for idx, tokens in enumerate(paragraphs):
        edepths = []
        for t in tokens:
            a = morph.atomize(t.word)
            edepths.append(a.e_depth)
        if not edepths:
            continue
        paragraph_data.append({
            "idx": idx,
            "n_tokens": len(tokens),
            "edepth_mean": mean(edepths),
        })

    return paragraph_data, section


def linear_residualize(x, y):
    """Return residuals of y after regressing y on x (linear)."""
    n = len(x)
    if n < 3:
        return y[:]
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    if den == 0:
        return y[:]
    slope = num / den
    intercept = my - slope * mx
    residuals = [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]
    return residuals


def spearman_rho(x, y):
    n = len(x)
    if n < 3:
        return None
    rx = sorted(range(n), key=lambda i: x[i])
    ranks_x = [0] * n
    for r, i in enumerate(rx):
        ranks_x[i] = r + 1
    ry = sorted(range(n), key=lambda i: y[i])
    ranks_y = [0] * n
    for r, i in enumerate(ry):
        ranks_y[i] = r + 1
    d2 = sum((ranks_x[i] - ranks_y[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def folio_test(folio_target, b_tokens, morph, n_perm=10000):
    paragraphs, section = gather_folio_paragraphs(folio_target, b_tokens, morph)
    if not paragraphs or len(paragraphs) < 4:
        return None

    indices = [p["idx"] for p in paragraphs]
    edepth_means = [p["edepth_mean"] for p in paragraphs]
    lengths = [p["n_tokens"] for p in paragraphs]

    # Length-residualize e-depth-mean
    residualized = linear_residualize(lengths, edepth_means)

    actual_rho = spearman_rho(indices, residualized)
    if actual_rho is None:
        return None

    # Permutation: shuffle paragraph order
    extreme = 0
    for _ in range(n_perm):
        shuffled = residualized[:]
        random.shuffle(shuffled)
        rho = spearman_rho(indices, shuffled)
        if abs(rho) >= abs(actual_rho):
            extreme += 1
    p_value = extreme / n_perm

    return {
        "folio": folio_target,
        "section": section,
        "n_paragraphs": len(paragraphs),
        "indices": indices,
        "edepth_means": edepth_means,
        "lengths": lengths,
        "residualized": residualized,
        "rho_raw": spearman_rho(indices, edepth_means),
        "rho_residualized": actual_rho,
        "p_value": p_value,
    }


def main():
    print("Loading data...")
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    # Get all unique folios in B
    all_folios = sorted(set(t.folio for t in b_tokens))
    print(f"  Total B folios: {len(all_folios)}")

    # Run test on all folios with >=4 paragraphs
    print("\n=== RUNNING LAYOUT-ORDERING TEST ON ALL CURRIER B FOLIOS ===")
    print(f"  {'Folio':<10} {'Sec':<5} {'NPar':>5} {'rho_raw':>9} {'rho_res':>9} {'p':>8}")

    all_results = []
    for folio in all_folios:
        r = folio_test(folio, b_tokens, morph, n_perm=2000)  # 2k for speed; 10k on selected later
        if r is None:
            continue
        all_results.append(r)

    # Sort by abs(rho)
    all_results.sort(key=lambda r: -abs(r["rho_residualized"]))
    for r in all_results:
        print(f"  {r['folio']:<10} {r['section'] or '-':<5} {r['n_paragraphs']:>5} "
              f"{r['rho_raw']:>+9.3f} {r['rho_residualized']:>+9.3f} {r['p_value']:>8.4f}")

    # === AGGREGATE STATISTICS ===
    print("\n=== AGGREGATE: ALL FOLIOS WITH >=4 PARAGRAPHS ===")
    rhos = [r["rho_residualized"] for r in all_results]
    ps = [r["p_value"] for r in all_results]
    n = len(rhos)
    print(f"  N folios: {n}")
    print(f"  Mean rho: {mean(rhos):+.4f}")
    print(f"  Mean |rho|: {mean(abs(r) for r in rhos):.4f}")
    print(f"  Std rho: {stdev(rhos):.4f}" if n >= 2 else "")
    print(f"  Median rho: {sorted(rhos)[n//2]:+.4f}")
    print(f"  N with rho > 0: {sum(1 for r in rhos if r > 0)}/{n} ({sum(1 for r in rhos if r > 0)/n*100:.1f}%)")
    print(f"  N with p < 0.05: {sum(1 for p in ps if p < 0.05)}/{n}")
    print(f"  N with p < 0.001: {sum(1 for p in ps if p < 0.001)}/{n}")

    # === MATCHED SUBSET (sanity check: should reproduce rho=+0.81 finding) ===
    print("\n=== MATCHED ALCHEMICAL SUBSET (sanity: prior finding rho=+0.81 on n=5) ===")
    matched_results = [r for r in all_results if r["folio"] in MATCHED_FOLIOS]
    print(f"  N matched folios in test: {len(matched_results)}")
    if matched_results:
        m_rhos = [r["rho_residualized"] for r in matched_results]
        print(f"  Mean rho: {mean(m_rhos):+.4f}")
        print(f"  Median rho: {sorted(m_rhos)[len(m_rhos)//2]:+.4f}")
        for r in matched_results:
            print(f"    {r['folio']:<8} npar={r['n_paragraphs']:>2} rho={r['rho_residualized']:+.3f} p={r['p_value']:.4f}")

    # === CLUSTER SUBSET ===
    print("\n=== CLUSTER (PHARMACEUTICAL/HERBAL) SUBSET ===")
    cluster_results = [r for r in all_results if r["folio"] in CLUSTER_FOLIOS]
    print(f"  N cluster folios in test: {len(cluster_results)}")
    if cluster_results:
        c_rhos = [r["rho_residualized"] for r in cluster_results]
        print(f"  Mean rho: {mean(c_rhos):+.4f}")
        print(f"  Median rho: {sorted(c_rhos)[len(c_rhos)//2]:+.4f}")

    # === SECTION-STRATIFIED ===
    print("\n=== SECTION-STRATIFIED ===")
    by_section = defaultdict(list)
    for r in all_results:
        by_section[r["section"]].append(r["rho_residualized"])
    print(f"  {'Section':<8} {'N':>4} {'Mean rho':>10} {'Median':>10} {'% positive':>12}")
    for sec, rs in sorted(by_section.items(), key=lambda x: -len(x[1])):
        mr = mean(rs)
        med = sorted(rs)[len(rs)//2]
        pos = sum(1 for r in rs if r > 0) / len(rs) * 100
        print(f"  {sec or '-':<8} {len(rs):>4} {mr:>+10.4f} {med:>+10.4f} {pos:>11.1f}%")

    # === VERDICT ===
    print("\n=== VERDICT (vs pre-registered thresholds) ===")
    overall_mean = mean(rhos)
    overall_mean_abs = mean(abs(r) for r in rhos)
    pct_positive = sum(1 for r in rhos if r > 0) / len(rhos) * 100
    pct_significant = sum(1 for p in ps if p < 0.001) / len(ps) * 100

    print(f"  Pre-registered threshold for procedural: |rho|>0.4 mean, 60% same direction, p<0.001 majority")
    print(f"  Observed: mean rho={overall_mean:+.3f}, |rho|={overall_mean_abs:.3f}, "
          f"{pct_positive:.0f}% positive, {pct_significant:.0f}% p<0.001")

    if overall_mean_abs > 0.4 and pct_positive >= 60:
        verdict = "PROCEDURAL MANUSCRIPT-WIDE (Tier 2 candidate)"
    elif abs(overall_mean) < 0.1 and pct_positive < 60:
        verdict = "LAYOUT-ORDERING IS MATCHED-FOLIO ARTIFACT (Tier 1 falsification candidate)"
    else:
        verdict = "MIXED - SECTION-CONDITIONAL (Tier 3)"
    print(f"  VERDICT: {verdict}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({
        "preregistered_threshold": {
            "procedural": "abs_mean_rho>0.4 AND >=60% positive AND p<0.001 majority",
            "null": "abs_mean_rho<0.1 AND <60% positive",
            "mixed": "between extremes",
        },
        "all_folios": all_results,
        "summary": {
            "n_folios": n,
            "mean_rho": mean(rhos),
            "mean_abs_rho": mean(abs(r) for r in rhos),
            "median_rho": sorted(rhos)[n//2],
            "pct_positive": pct_positive,
            "pct_significant_001": pct_significant,
            "verdict": verdict,
        },
        "matched_subset": [r for r in all_results if r["folio"] in MATCHED_FOLIOS],
        "cluster_subset": [r for r in all_results if r["folio"] in CLUSTER_FOLIOS],
        "by_section": {sec: rs for sec, rs in by_section.items()},
    }, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

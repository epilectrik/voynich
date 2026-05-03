"""
Phase 675 Script 2: Falsifiers for the section-conditional layout-ordering finding.

Both experts identified three required falsifiers BEFORE registering:

  F1. PARAGRAPH-1 ABLATION (most likely killer per crazy-expert):
      Header/setup paragraphs are MARKING-enriched (C1287, C1565). Higher
      specification vocab -> spuriously higher e-depth in paragraph 1,
      pulling all rho negative. Drop paragraph 1, recompute. If |rho| drops
      below 0.1, finding is a header artifact.

  F2. H-SECTION DROP ON CLUSTER:
      Cluster signal is dominated by H-section folios. C939 (low-heat herbal)
      could explain the H signature. Drop H-section folios from cluster,
      recompute on remaining cluster folios.

  F3. SECTION-MEAN RESIDUALIZATION:
      Is Herbal's gradient just the static "low-heat herbal" property? Subtract
      section mean e-depth from each paragraph's e-depth before computing
      gradient.
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

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "falsifier_results.json"

MATCHED_FOLIOS = ["f75r", "f76r", "f84r", "f79r", "f82r", "f76v", "f81v",
                  "f112v", "f103r", "f116r", "f112r"]
CLUSTER_FOLIOS = [
    "f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v",
    "f43r", "f50r", "f50v", "f55r", "f55v", "f85r1", "f85r2",
    "f86v4", "f86v5", "f86v6", "f94r", "f94v", "f95r1", "f95r2",
    "f95v1", "f95v2", "f105v", "f114r",
]


def gather_paragraphs(folio_target, b_tokens, morph):
    folio_tokens = [t for t in b_tokens if t.folio == folio_target
                    and "*" not in t.word and t.word.strip() and not t.is_label]
    if not folio_tokens:
        return None, None
    section = folio_tokens[0].section
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
    para_data = []
    for idx, tokens in enumerate(paragraphs):
        edepths = [morph.atomize(t.word).e_depth for t in tokens]
        if not edepths:
            continue
        para_data.append({"idx": idx, "n_tokens": len(tokens),
                          "edepth_mean": mean(edepths)})
    return para_data, section


def linear_residualize(x, y):
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
    return [yi - (slope * xi + intercept) for xi, yi in zip(x, y)]


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


def folio_rho(paragraphs, drop_first=False, length_residualize=True, section_demean=None):
    paras = paragraphs[1:] if drop_first else paragraphs[:]
    if len(paras) < 3:
        return None
    indices = [p["idx"] for p in paras]
    edepth_means = [p["edepth_mean"] for p in paras]
    lengths = [p["n_tokens"] for p in paras]
    if section_demean is not None:
        edepth_means = [e - section_demean for e in edepth_means]
    if length_residualize:
        edepth_means = linear_residualize(lengths, edepth_means)
    return spearman_rho(indices, edepth_means)


def main():
    tx = Transcript()
    morph = Morphology()
    b_tokens = list(tx.currier_b())

    all_folios = sorted(set(t.folio for t in b_tokens))
    folio_data = {}
    for f in all_folios:
        paras, section = gather_paragraphs(f, b_tokens, morph)
        if paras and len(paras) >= 4:
            folio_data[f] = {"paras": paras, "section": section}

    print(f"Folios with >=4 paragraphs: {len(folio_data)}")

    # Section-mean e-depth (per section, all paragraphs pooled)
    section_para_edepth = defaultdict(list)
    for f, d in folio_data.items():
        for p in d["paras"]:
            section_para_edepth[d["section"]].append(p["edepth_mean"])
    section_means = {sec: mean(vals) for sec, vals in section_para_edepth.items()}
    print(f"Section means: {section_means}")
    print()

    def aggregate(rhos):
        if not rhos:
            return None
        n = len(rhos)
        return {
            "n": n,
            "mean_rho": mean(rhos),
            "mean_abs_rho": mean(abs(r) for r in rhos),
            "median_rho": sorted(rhos)[n // 2],
            "pct_negative": sum(1 for r in rhos if r < 0) / n * 100,
        }

    def by_section(rho_dict, sec_filter=None, folio_filter=None):
        rhos = []
        for f, r in rho_dict.items():
            if r is None:
                continue
            if folio_filter is not None and f not in folio_filter:
                continue
            if sec_filter is not None and folio_data[f]["section"] != sec_filter:
                continue
            rhos.append(r)
        return aggregate(rhos)

    # ============================================================
    # BASELINE (length-residualized only) — same as Script 1
    # ============================================================
    baseline_rhos = {f: folio_rho(d["paras"]) for f, d in folio_data.items()}
    print("=== BASELINE (length-residualized, all paragraphs) ===")
    print(f"  All:     {by_section(baseline_rhos)}")
    print(f"  H:       {by_section(baseline_rhos, 'H')}")
    print(f"  B:       {by_section(baseline_rhos, 'B')}")
    print(f"  S:       {by_section(baseline_rhos, 'S')}")
    print(f"  Cluster: {by_section(baseline_rhos, folio_filter=CLUSTER_FOLIOS)}")
    cluster_no_h = [f for f in CLUSTER_FOLIOS if f in folio_data and folio_data[f]['section'] != 'H']
    print(f"  Cluster non-H ({len(cluster_no_h)}): {by_section(baseline_rhos, folio_filter=cluster_no_h)}")
    print(f"  Matched: {by_section(baseline_rhos, folio_filter=MATCHED_FOLIOS)}")
    print()

    # ============================================================
    # F1. PARAGRAPH-1 ABLATION
    # ============================================================
    print("=== F1. PARAGRAPH-1 ABLATION (drop paragraph 1) ===")
    p1_rhos = {f: folio_rho(d["paras"], drop_first=True)
               for f, d in folio_data.items()}
    p1_rhos = {f: r for f, r in p1_rhos.items() if r is not None}
    print(f"  All:     {by_section(p1_rhos)}")
    print(f"  H:       {by_section(p1_rhos, 'H')}")
    print(f"  B:       {by_section(p1_rhos, 'B')}")
    print(f"  S:       {by_section(p1_rhos, 'S')}")
    print(f"  Cluster: {by_section(p1_rhos, folio_filter=CLUSTER_FOLIOS)}")
    print(f"  Cluster non-H: {by_section(p1_rhos, folio_filter=cluster_no_h)}")
    print(f"  Matched: {by_section(p1_rhos, folio_filter=MATCHED_FOLIOS)}")
    print()

    # ============================================================
    # F2. H-SECTION DROP ON CLUSTER (already covered above)
    # ============================================================
    print("=== F2. CLUSTER NON-H SUBSET ===")
    print(f"  Baseline (with H):  {by_section(baseline_rhos, folio_filter=CLUSTER_FOLIOS)}")
    print(f"  Without H:          {by_section(baseline_rhos, folio_filter=cluster_no_h)}")
    print(f"  Cluster non-H folios: {cluster_no_h}")
    print()

    # ============================================================
    # F3. SECTION-MEAN RESIDUALIZATION (subtract section mean e-depth)
    # ============================================================
    print("=== F3. SECTION-MEAN RESIDUALIZATION ===")
    sm_rhos = {f: folio_rho(d["paras"], section_demean=section_means.get(d["section"], 0))
               for f, d in folio_data.items()}
    sm_rhos = {f: r for f, r in sm_rhos.items() if r is not None}
    print(f"  All:     {by_section(sm_rhos)}")
    print(f"  H:       {by_section(sm_rhos, 'H')}")
    print(f"  B:       {by_section(sm_rhos, 'B')}")
    print(f"  S:       {by_section(sm_rhos, 'S')}")
    print(f"  Cluster: {by_section(sm_rhos, folio_filter=CLUSTER_FOLIOS)}")
    print()

    # Save
    out = {
        "section_means": section_means,
        "n_folios": len(folio_data),
        "baseline": {
            "all": by_section(baseline_rhos),
            "H": by_section(baseline_rhos, "H"),
            "B": by_section(baseline_rhos, "B"),
            "S": by_section(baseline_rhos, "S"),
            "cluster": by_section(baseline_rhos, folio_filter=CLUSTER_FOLIOS),
            "cluster_non_H": by_section(baseline_rhos, folio_filter=cluster_no_h),
            "matched": by_section(baseline_rhos, folio_filter=MATCHED_FOLIOS),
        },
        "F1_p1_drop": {
            "all": by_section(p1_rhos),
            "H": by_section(p1_rhos, "H"),
            "B": by_section(p1_rhos, "B"),
            "S": by_section(p1_rhos, "S"),
            "cluster": by_section(p1_rhos, folio_filter=CLUSTER_FOLIOS),
            "cluster_non_H": by_section(p1_rhos, folio_filter=cluster_no_h),
            "matched": by_section(p1_rhos, folio_filter=MATCHED_FOLIOS),
        },
        "F3_section_demean": {
            "all": by_section(sm_rhos),
            "H": by_section(sm_rhos, "H"),
            "B": by_section(sm_rhos, "B"),
            "S": by_section(sm_rhos, "S"),
            "cluster": by_section(sm_rhos, folio_filter=CLUSTER_FOLIOS),
        },
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

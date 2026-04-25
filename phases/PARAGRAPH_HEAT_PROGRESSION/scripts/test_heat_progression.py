"""Test whether per-paragraph heat metrics on confirmed-match folios track
the matched recipe's expected fire-degree progression.

Predictions LOCKED in results/predictions.md before this script runs.
This script computes atom-derived heat metrics and tests correlation.

Heat metrics computed per paragraph:
  - mean_e_depth: average e_depth across paragraph tokens
  - qokeedy_frac: qokeedy / total tokens (gentle balneum signature)
  - qokedy_frac: qokedy / total tokens (moderate hot signature)
  - qok_class_frac: qok-class total / paragraph length (heat density)
  - gentle_ratio: tokens with e_depth >= 2 / total
  - balneum_score: qokeedy_frac - qokedy_frac

Test: Spearman rho between predicted heat-degree and each measured metric,
per folio + aggregate.
"""
from __future__ import annotations
import io, sys, json
from pathlib import Path
from collections import defaultdict

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

# Predictions LOCKED in predictions.md
PREDICTIONS = {
    "f75r":  [2, 1, 2],
    "f84r":  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1],
    "f78r":  [3, 2, 2, 2, 2, 2, 2, 2],
    "f86v3": [3, 2, 2, 2, 2, 2, 1],
    "f82r":  [1, 1, 3, 2],
    "f108v": [1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
    "f79v":  [1, 1, 2, 2, 2, 1, 1],
}

HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}


def get_paragraph_data(folio):
    """Return list of paragraphs, each a list of token info dicts."""
    tx = Transcript()
    morph = Morphology()
    paragraphs = []
    current = []
    for t in tx.currier_b():
        if t.folio != folio:
            continue
        if t.placement and t.placement.startswith("L"):
            continue
        if t.par_initial and current:
            paragraphs.append(current)
            current = []
        a = morph.atomize(t.word)
        current.append({"word": t.word, "e_depth": a.e_depth})
    if current:
        paragraphs.append(current)
    return paragraphs


def paragraph_heat_metrics(para_tokens):
    """Compute heat metrics for one paragraph."""
    n = len(para_tokens)
    if n == 0:
        return {"n": 0}
    mean_e = sum(t["e_depth"] for t in para_tokens) / n
    qokeedy = sum(1 for t in para_tokens if t["word"] == "qokeedy")
    qokedy = sum(1 for t in para_tokens if t["word"] == "qokedy")
    qok_class = sum(1 for t in para_tokens if t["word"] in HEAT)
    gentle = sum(1 for t in para_tokens if t["e_depth"] >= 2)
    return {
        "n": n,
        "mean_e_depth": mean_e,
        "qokeedy_frac": qokeedy / n,
        "qokedy_frac": qokedy / n,
        "qok_class_frac": qok_class / n,
        "gentle_ratio": gentle / n,
        "balneum_score": (qokeedy - qokedy) / n,
    }


def spearman_rho(xs, ys):
    """Average-rank Spearman correlation."""
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    def rank(arr):
        sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0.0] * len(arr)
        i = 0
        while i < len(arr):
            j = i
            while j + 1 < len(arr) and arr[sorted_idx[j+1]] == arr[sorted_idx[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j+1):
                ranks[sorted_idx[k]] = avg
            i = j + 1
        return ranks
    n = len(xs)
    rx = rank(xs); ry = rank(ys)
    mx = sum(rx) / n; my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    vx = sum((r - mx)**2 for r in rx) ** 0.5
    vy = sum((r - my)**2 for r in ry) ** 0.5
    if vx == 0 or vy == 0:
        return 0.0
    return cov / (vx * vy)


def perm_p(xs, ys, rho_obs, n_perm=2000, seed=42):
    import random
    rng = random.Random(seed)
    target = abs(rho_obs)
    count = 0
    ys_perm = list(ys)
    for _ in range(n_perm):
        rng.shuffle(ys_perm)
        if abs(spearman_rho(xs, ys_perm)) >= target - 1e-12:
            count += 1
    return (count + 1) / (n_perm + 1)


# Run analysis
print("Heat-Progression Test — predicted vs measured per paragraph")
print("=" * 80)

results = []
metrics_to_test = ["mean_e_depth", "qokeedy_frac", "qok_class_frac",
                   "gentle_ratio", "balneum_score"]

for folio, predicted in PREDICTIONS.items():
    paragraphs = get_paragraph_data(folio)
    if len(paragraphs) != len(predicted):
        print(f"\n⚠️  {folio}: paragraph count mismatch "
              f"(actual={len(paragraphs)}, predicted={len(predicted)})")
        # Truncate or pad
        if len(paragraphs) > len(predicted):
            paragraphs = paragraphs[:len(predicted)]
        else:
            predicted = predicted[:len(paragraphs)]

    # Compute metrics per paragraph
    para_metrics = [paragraph_heat_metrics(p) for p in paragraphs]

    print(f"\n{folio}: {len(paragraphs)} paragraphs, predicted {predicted}")

    folio_result = {"folio": folio, "predicted": predicted, "metrics": {}}

    # Print per-paragraph profile
    for i, m in enumerate(para_metrics):
        if m["n"] == 0:
            continue
        pred = predicted[i]
        print(f"  P{i+1} (n={m['n']:>3}, pred={pred}):  "
              f"e_depth={m['mean_e_depth']:.2f}  "
              f"qokeedy_frac={m['qokeedy_frac']:.3f}  "
              f"qok%={m['qok_class_frac']:.2f}  "
              f"gentle%={m['gentle_ratio']:.2f}  "
              f"balneum={m['balneum_score']:+.3f}")

    # Correlate predicted vs each metric
    for metric in metrics_to_test:
        ys = [m[metric] for m in para_metrics if m["n"] > 0]
        xs = predicted[:len(ys)]
        if len(set(xs)) > 1 and len(set(ys)) > 1:
            rho = spearman_rho(xs, ys)
            p = perm_p(xs, ys, rho, n_perm=2000)
        else:
            rho = 0.0
            p = 1.0
        folio_result["metrics"][metric] = {"rho": rho, "p": p}

    print(f"  Correlations (predicted vs measured):")
    for metric in metrics_to_test:
        r = folio_result["metrics"][metric]
        sig = "★" if r["p"] < 0.05 else ("✓" if r["p"] < 0.10 else "·")
        print(f"    {metric:<18s}  rho={r['rho']:+.3f}  p={r['p']:.3f}  {sig}")

    results.append(folio_result)

# Aggregate
print("\n" + "=" * 80)
print("AGGREGATE")
print("=" * 80)

print(f"\n{'Metric':<18s} {'mean rho':>10s} {'positive':>10s} {'p<0.10':>8s} {'p<0.05':>8s}")
print("-" * 64)

aggregate = {}
for metric in metrics_to_test:
    rhos = [r["metrics"][metric]["rho"] for r in results]
    ps = [r["metrics"][metric]["p"] for r in results]
    mean_rho = sum(rhos) / len(rhos)
    n_pos = sum(1 for r in rhos if r > 0)
    n_p10 = sum(1 for p in ps if p < 0.10)
    n_p05 = sum(1 for p in ps if p < 0.05)
    n = len(rhos)
    print(f"{metric:<18s}    {mean_rho:+.3f}      {n_pos}/{n}        {n_p10}/{n}      {n_p05}/{n}")
    aggregate[metric] = {"mean_rho": mean_rho, "n_positive": n_pos,
                         "n_p_lt_010": n_p10, "n_p_lt_005": n_p05,
                         "n_total": n}

# Best metric
best_metric = max(metrics_to_test,
                  key=lambda m: aggregate[m]["mean_rho"])
print(f"\nBest metric: {best_metric} (mean rho = {aggregate[best_metric]['mean_rho']:+.3f})")

# Verdict
print()
mr = aggregate[best_metric]["mean_rho"]
np_ = aggregate[best_metric]["n_positive"]
n = aggregate[best_metric]["n_total"]
if mr > 0.5 and np_ >= 5:
    print("  VERDICT: STRONG SUPPORT for heat-mode encoding via paragraph layout-order.")
elif mr > 0.3 and np_ >= 4:
    print("  VERDICT: MODERATE SUPPORT for heat-mode encoding.")
elif mr > 0.1:
    print("  VERDICT: WEAK support — direction consistent but signal modest.")
else:
    print("  VERDICT: NULL / INCONCLUSIVE — heat-mode does not cleanly track recipe-phase progression.")

# Write JSON
out = ROOT / "phases" / "PARAGRAPH_HEAT_PROGRESSION" / "results" / "test_results.json"
out.write_text(json.dumps({
    "test": "Paragraph Heat-Mode Progression",
    "predictions_locked": True,
    "n_folios": len(results),
    "folio_results": results,
    "aggregate": aggregate,
    "best_metric": best_metric,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")

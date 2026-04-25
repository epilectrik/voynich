"""Phase 645b: refined heat-progression test on heat-phase-distinct subset.

Predictions locked in results/predictions.md before this script runs.
Test: per-paragraph heat metrics correlate with predicted fire-degree.
"""
from __future__ import annotations
import io, sys, json
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

# LOCKED predictions — heat-phase-distinct subset
HEAT_PHASE_DISTINCT = {
    "f84r":  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1],
    "f82r":  [1, 1, 3, 2],
    "f78r":  [3, 2, 2, 2, 2, 2, 2, 2],
    "f86v3": [3, 2, 2, 2, 2, 2, 1],
    "f77r":  [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
}

# Heat-uniform control set (predicted uniform/minimal variation)
HEAT_UNIFORM = {
    "f75r":  [2, 2, 2],
    "f108v": [2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    "f79v":  [2, 2, 2, 2, 2, 2, 1],
}

HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}


def get_paragraph_data(folio):
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


def paragraph_metrics(para_tokens):
    n = len(para_tokens)
    if n == 0:
        return None
    qokeedy = sum(1 for t in para_tokens if t["word"] == "qokeedy")
    qokedy = sum(1 for t in para_tokens if t["word"] == "qokedy")
    qok_class = sum(1 for t in para_tokens if t["word"] in HEAT)
    gentle = sum(1 for t in para_tokens if t["e_depth"] >= 2)
    return {
        "n": n,
        "mean_e_depth": sum(t["e_depth"] for t in para_tokens) / n,
        "qokeedy_frac": qokeedy / n,
        "qokedy_frac": qokedy / n,
        "qok_class_frac": qok_class / n,
        "gentle_ratio": gentle / n,
        "balneum_score": (qokeedy - qokedy) / n,
    }


def spearman_rho(xs, ys):
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


def run_set(label, folios_predicted):
    print(f"\n{'=' * 80}")
    print(f"## {label}")
    print('=' * 80)

    metrics_to_test = ["mean_e_depth", "qokeedy_frac", "qok_class_frac",
                       "gentle_ratio", "balneum_score"]
    folio_results = []

    for folio, predicted in folios_predicted.items():
        paragraphs = get_paragraph_data(folio)
        if len(paragraphs) != len(predicted):
            if len(paragraphs) > len(predicted):
                paragraphs = paragraphs[:len(predicted)]
            else:
                predicted = predicted[:len(paragraphs)]

        para_metrics = [paragraph_metrics(p) for p in paragraphs if p]
        result = {"folio": folio, "predicted": predicted, "metrics": {}}
        print(f"\n{folio} (n={len(predicted)}, predicted {predicted}):")

        for metric in metrics_to_test:
            ys = [m[metric] for m in para_metrics if m]
            xs = predicted[:len(ys)]
            if len(set(xs)) > 1 and len(set(ys)) > 1:
                rho = spearman_rho(xs, ys)
                p = perm_p(xs, ys, rho, n_perm=2000)
            else:
                rho = 0.0
                p = 1.0
            result["metrics"][metric] = {"rho": rho, "p": p}
            sig = "★" if p < 0.05 else ("✓" if p < 0.10 else "·")
            print(f"  {metric:<18s}  rho={rho:+.3f}  p={p:.3f}  {sig}")

        folio_results.append(result)

    # Aggregate
    print(f"\n  {'Metric':<18s} {'mean_rho':>9s} {'positive':>9s} {'p<0.10':>8s} {'p<0.05':>8s}")
    print("  " + "-" * 60)
    aggregate = {}
    for metric in metrics_to_test:
        rhos = [r["metrics"][metric]["rho"] for r in folio_results]
        ps = [r["metrics"][metric]["p"] for r in folio_results]
        mean_rho = sum(rhos) / len(rhos)
        n_pos = sum(1 for r in rhos if r > 0)
        n_p10 = sum(1 for p in ps if p < 0.10)
        n_p05 = sum(1 for p in ps if p < 0.05)
        n = len(rhos)
        print(f"  {metric:<18s}  {mean_rho:+.3f}     {n_pos}/{n}        {n_p10}/{n}      {n_p05}/{n}")
        aggregate[metric] = {"mean_rho": mean_rho, "n_pos": n_pos,
                             "n_p10": n_p10, "n_p05": n_p05, "n_total": n}

    return {"folio_results": folio_results, "aggregate": aggregate}


print("Phase 645b — Refined Heat-Mode Progression")
print("=" * 80)
print()
print("Pre-classified subsets (LOCKED):")
print(f"  Heat-phase-distinct (n={len(HEAT_PHASE_DISTINCT)}): {list(HEAT_PHASE_DISTINCT.keys())}")
print(f"  Heat-uniform control (n={len(HEAT_UNIFORM)}): {list(HEAT_UNIFORM.keys())}")

primary = run_set("HEAT-PHASE-DISTINCT (primary test)", HEAT_PHASE_DISTINCT)
control = run_set("HEAT-UNIFORM (control)", HEAT_UNIFORM)

# Compare aggregates
print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)

print(f"\n  {'Metric':<18s} {'phase-distinct':>15s} {'heat-uniform':>15s} {'difference':>12s}")
print("  " + "-" * 70)
for metric in ["mean_e_depth", "qokeedy_frac", "qok_class_frac", "gentle_ratio", "balneum_score"]:
    pd_rho = primary["aggregate"][metric]["mean_rho"]
    hu_rho = control["aggregate"][metric]["mean_rho"]
    diff = pd_rho - hu_rho
    print(f"  {metric:<18s}  {pd_rho:+.3f}            {hu_rho:+.3f}            {diff:+.3f}")

# Verdict
best_metric = max(["mean_e_depth", "qokeedy_frac", "qok_class_frac", "gentle_ratio", "balneum_score"],
                   key=lambda m: primary["aggregate"][m]["mean_rho"])
print(f"\nBest metric on phase-distinct subset: {best_metric}")
print(f"  Phase-distinct mean rho: {primary['aggregate'][best_metric]['mean_rho']:+.3f}")
print(f"  Heat-uniform mean rho:   {control['aggregate'][best_metric]['mean_rho']:+.3f}")
print(f"  Difference:              {primary['aggregate'][best_metric]['mean_rho'] - control['aggregate'][best_metric]['mean_rho']:+.3f}")

primary_pos_pct = primary["aggregate"][best_metric]["n_pos"] / primary["aggregate"][best_metric]["n_total"]
primary_sig_count = primary["aggregate"][best_metric]["n_p05"]

print()
if primary["aggregate"][best_metric]["mean_rho"] > 0.5 and primary_pos_pct >= 0.8 and primary_sig_count >= 2:
    print("  VERDICT: STRONG SUPPORT for heat-encoding on heat-phase-distinct recipes.")
    print("    → Register new Tier 3 constraint")
elif primary["aggregate"][best_metric]["mean_rho"] > 0.4 and primary_pos_pct >= 0.6:
    print("  VERDICT: MODERATE SUPPORT — register provisionally with scope restriction")
elif primary["aggregate"][best_metric]["mean_rho"] > 0.2:
    print("  VERDICT: WEAK — direction consistent but signal modest")
else:
    print("  VERDICT: NULL — heat-encoding does not even hold on heat-phase-distinct subset")

# Write output
out = ROOT / "phases" / "HEAT_PROGRESSION_REFINED" / "results" / "test_results.json"
out.write_text(json.dumps({
    "test": "Phase 645b — Refined Heat-Mode Progression",
    "predictions_locked": True,
    "heat_phase_distinct": primary,
    "heat_uniform_control": control,
    "best_metric_on_phase_distinct": best_metric,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")

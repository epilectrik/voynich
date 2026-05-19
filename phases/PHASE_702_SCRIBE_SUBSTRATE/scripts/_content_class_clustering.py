"""
PHASE_702 expanded: content-class clustering across scribes.

Tests Reading C: substrate signature is content-class determined; scribe
identity is mediated through content-domain assignment. Three substrate
modes predicted:
  - period-2 (Section B execution: r21 negative, lag1 negative, lag2 positive)
  - sustain (matched-S: r21 positive, lag1 positive, lag2 positive)
  - flat (non-procedural: lag1 and lag2 both near zero, ratio undefined)

Synthesizes both experts' recommendations:
  - Ratio-valid gating (|lag1| > 0.015) before computing r21
  - N-matched downsample control on large cells
  - Multiple content-class cells per scribe where available
  - Predict: cells cluster by content class, not by scribe identity

If clustering holds: register three-mode content-gated framework as Tier 2.
If clustering fails: INDEX-only documentation, no constraint.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

ATTRIBUTION_CSV = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'data' / 'davis_scribe_attribution.csv'
OUT_PATH = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'results' / 'content_class_clustering.json'

rng = random.Random(7024)

# Pre-registered content-class definitions
SCRIBE2_BOTANICAL = {
    'f26r', 'f26v', 'f31r', 'f31v', 'f33r', 'f33v', 'f40r', 'f40v',
    'f34r', 'f34v', 'f39r', 'f39v', 'f43r', 'f43v', 'f46r', 'f46v',
    'f50r', 'f50v', 'f55r', 'f55v',
}
SCRIBE2_BALNEOLOGY = {f"f{n}{rv}" for n in range(75, 85) for rv in ['r', 'v']}
SCRIBE2_ROSE_OBVERSE = {'f85r1', 'f85r2'}

SCRIBE3_BOTANICAL_Q8_Q16 = {'f58r', 'f58v', 'f96r', 'f96v'}
MATCHED_S = {'f103r', 'f103v', 'f106r', 'f106v', 'f107r', 'f108r', 'f108v',
             'f111r', 'f112r', 'f112v', 'f113r', 'f113v', 'f114r', 'f114v',
             'f115r', 'f115v', 'f116r'}
UNMATCHED_S = {'f104r', 'f104v', 'f105r', 'f105v', 'f107v', 'f111v'}

# Scribe 1 — entire Currier-A portion. We'll split into thematic sub-cells.
SCRIBE1_HERBAL_PURE = {f"f{n}{rv}" for n in [1,2,3,4,5,6,7,8] for rv in ['r','v']}  # Q1
SCRIBE1_HERBAL_PURE |= {f"f{n}{rv}" for n in [9,10,11,13,14,15,16] for rv in ['r','v']}  # Q2 (no f12)
SCRIBE1_HERBAL_PURE |= {f"f{n}{rv}" for n in range(17, 25) for rv in ['r','v']}  # Q3
# Q4-7 Scribe 1 bifolia
SCRIBE1_HERBAL_MIXED = {'f25r','f25v','f32r','f32v',  # Q4 outer
                        'f27r','f27v','f30r','f30v',  # Q4 27/30
                        'f28r','f28v','f29r','f29v',  # Q4 inner
                        'f35r','f35v','f38r','f38v',  # Q5 35/38
                        'f36r','f36v','f37r','f37v',  # Q5 inner
                        'f42r','f42v','f47r','f47v',  # Q6 42/47
                        'f44r','f44v','f45r','f45v',  # Q6 inner
                        'f49r','f49v','f56r','f56v',  # Q7 outer
                        'f51r','f51v','f54r','f54v',  # Q7 51/54
                        'f52r','f52v','f53r','f53v'}  # Q7 inner
# Q15 + Q17 (botanical-pharma foldouts + recipes)
SCRIBE1_Q15_PHARMA = {'f87r','f87v','f88r','f88v','f89r1','f89r2','f89v1','f89v2',
                      'f90r1','f90r2','f90v1','f90v2'}
SCRIBE1_Q17_RECIPES = {'f99r','f99v','f100r','f100v','f101r1','f101r2','f101v1','f101v2',
                       'f102r1','f102r2','f102v1','f102v2'}


def load_attribution():
    attr = {}
    with open(ATTRIBUTION_CSV, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            attr[row['folio'].strip()] = row['scribe'].strip()
    return attr


def folio_match(folio, keys):
    if folio in keys:
        return folio
    if len(folio) > 2 and folio[-1].isdigit():
        stripped = folio[:-1]
        if stripped in keys:
            return stripped
    return None


def e_depth(word, morph):
    try:
        a = morph.atomize(word)
        return a.e_depth or 0
    except Exception:
        return 0


def lag_same_rate(seq, lag):
    if len(seq) <= lag:
        return 0.0, 0
    n_pairs = len(seq) - lag
    n_same = sum(1 for i in range(n_pairs) if seq[i] == seq[i + lag])
    return n_same / n_pairs, n_pairs


def lag_excess_for_paragraphs(paragraphs_depths, lag, n_perm=200, rng_local=None):
    if rng_local is None:
        rng_local = rng
    total_pairs = 0
    total_obs = 0
    total_null = 0.0
    for depths in paragraphs_depths:
        n = len(depths)
        if n <= lag:
            continue
        rate, pairs = lag_same_rate(depths, lag)
        total_pairs += pairs
        total_obs += int(round(rate * pairs))
        shuffled = list(depths)
        null_acc = 0.0
        for _ in range(n_perm):
            rng_local.shuffle(shuffled)
            r, _ = lag_same_rate(shuffled, lag)
            null_acc += r
        total_null += (null_acc / n_perm) * pairs
    if total_pairs == 0:
        return None
    return {
        "lag": lag, "n_pairs": total_pairs,
        "obs_rate": total_obs / total_pairs,
        "null_rate": total_null / total_pairs,
        "excess": (total_obs - total_null) / total_pairs,
    }


def bootstrap_lag_diff(paragraphs_depths, n_boot=200, n_perm=50):
    diffs = []
    lag1_samples = []
    lag2_samples = []
    n_paras = len(paragraphs_depths)
    if n_paras < 5:
        return None
    rng_boot = random.Random(70240)
    for _ in range(n_boot):
        sample_idx = [rng_boot.randrange(n_paras) for _ in range(n_paras)]
        sample = [paragraphs_depths[i] for i in sample_idx]
        rng_perm = random.Random(rng_boot.random())
        l1 = lag_excess_for_paragraphs(sample, 1, n_perm=n_perm, rng_local=rng_perm)
        l2 = lag_excess_for_paragraphs(sample, 2, n_perm=n_perm, rng_local=rng_perm)
        if l1 is None or l2 is None:
            continue
        lag1, lag2 = l1["excess"], l2["excess"]
        lag1_samples.append(lag1)
        lag2_samples.append(lag2)
        diffs.append(lag2 - lag1)
    if not diffs:
        return None
    return {
        "lag1_mean": sum(lag1_samples) / len(lag1_samples),
        "lag1_se": (sum((x - sum(lag1_samples)/len(lag1_samples))**2 for x in lag1_samples) / len(lag1_samples)) ** 0.5,
        "lag2_mean": sum(lag2_samples) / len(lag2_samples),
        "lag2_se": (sum((x - sum(lag2_samples)/len(lag2_samples))**2 for x in lag2_samples) / len(lag2_samples)) ** 0.5,
        "diff_mean": sum(diffs) / len(diffs),
        "diff_se": (sum((x - sum(diffs)/len(diffs))**2 for x in diffs) / len(diffs)) ** 0.5,
        "n_boot": len(diffs),
    }


def classify_mode(lag1, lag2, lag1_se=None, ratio_floor=0.015):
    """Classify a cell into period-2, sustain, or flat mode.

    Mode rules (pre-registered):
      - flat: |lag1| < ratio_floor (no significant sequential signature)
      - period-2: lag1 < 0 (alternation) AND lag2 > 0
      - sustain: lag1 > 0 AND lag2 > 0
      - period-3+ / other: lag1 > 0 AND lag2 < 0 (rare)
      - undefined: lag1 and lag2 both negative (rare)
    """
    if abs(lag1) < ratio_floor:
        return "flat"
    if lag1 < 0 and lag2 > 0:
        return "period-2"
    if lag1 > 0 and lag2 > 0:
        return "sustain"
    if lag1 > 0 and lag2 < 0:
        return "antisustain"  # rare, possible noise
    if lag1 < 0 and lag2 < 0:
        return "double-negative"  # rare, possible noise
    return "undefined"


def collect_paragraphs(folios_set, tx, attr, scribe_filter, currier_filter=None,
                        min_para=20, max_para=300):
    keys = set(attr.keys())
    current_para = defaultdict(list)
    paragraphs = []

    for t in tx.all(h_only=True):
        if not t.word or '*' in t.word:
            continue
        if currier_filter and t.language != currier_filter:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        if t.folio not in folios_set:
            continue
        matched = folio_match(t.folio, keys)
        if matched is None:
            continue
        if attr[matched] != scribe_filter:
            continue

        key = t.folio
        if t.par_initial and current_para[key]:
            paragraphs.append((key, current_para[key]))
            current_para[key] = []
        current_para[key].append(t.word.lower())

    for folio, p in current_para.items():
        if p:
            paragraphs.append((folio, p))

    return [(f, p) for (f, p) in paragraphs if min_para <= len(p) <= max_para]


def analyze_cell(label, folios_set, tx, morph, attr, scribe, currier):
    paras = collect_paragraphs(folios_set, tx, attr, scribe, currier)
    if not paras:
        return None
    n_tokens = sum(len(p) for (_, p) in paras)
    folios_covered = sorted(set(f for (f, _) in paras))
    depths = [[e_depth(w, morph) for w in p] for (f, p) in paras]

    l1 = lag_excess_for_paragraphs(depths, 1, n_perm=200)
    l2 = lag_excess_for_paragraphs(depths, 2, n_perm=200)
    if l1 is None or l2 is None:
        return None
    lag1, lag2 = l1["excess"], l2["excess"]
    boot = bootstrap_lag_diff(depths, n_boot=200, n_perm=50)

    mode = classify_mode(lag1, lag2)

    return {
        "label": label,
        "scribe": scribe,
        "currier": currier,
        "n_paragraphs": len(paras),
        "n_tokens": n_tokens,
        "n_folios": len(folios_covered),
        "lag1": lag1, "lag2": lag2,
        "lag2_minus_lag1": lag2 - lag1,
        "bootstrap": boot,
        "mode": mode,
    }


def n_matched_downsample_test(cell_a, cell_b, target_n, tx, morph, attr,
                                n_iter=30):
    """Downsample the larger cell to target_n (paragraph-level) repeatedly,
    re-test, report median z stability."""
    # Re-collect paragraphs for both
    paras_a = collect_paragraphs(cell_a["folios"], tx, attr,
                                  cell_a["scribe"], cell_a["currier"])
    paras_b = collect_paragraphs(cell_b["folios"], tx, attr,
                                  cell_b["scribe"], cell_b["currier"])

    depths_a = [[e_depth(w, morph) for w in p] for (f, p) in paras_a]
    depths_b = [[e_depth(w, morph) for w in p] for (f, p) in paras_b]

    # Identify which is larger by total tokens
    n_a = sum(len(d) for d in depths_a)
    n_b = sum(len(d) for d in depths_b)
    if n_a > n_b:
        larger, smaller, target = depths_a, depths_b, n_b
    else:
        larger, smaller, target = depths_b, depths_a, n_a

    z_values = []
    diff_values = []
    rng_m = random.Random(70250)
    for _ in range(n_iter):
        # Sample paragraphs from larger until cumulative N >= target
        shuffled = list(larger)
        rng_m.shuffle(shuffled)
        sampled = []
        cum = 0
        for d in shuffled:
            sampled.append(d)
            cum += len(d)
            if cum >= target:
                break

        boot_large = bootstrap_lag_diff(sampled, n_boot=80, n_perm=30)
        boot_small = bootstrap_lag_diff(smaller, n_boot=80, n_perm=30)
        if not (boot_large and boot_small):
            continue
        diff = boot_large["diff_mean"] - boot_small["diff_mean"]
        pooled_se = math.sqrt(boot_large["diff_se"]**2 + boot_small["diff_se"]**2)
        z = diff / pooled_se if pooled_se > 0 else float('nan')
        z_values.append(z)
        diff_values.append(diff)

    if not z_values:
        return None
    z_values.sort()
    diff_values.sort()
    return {
        "n_iter": len(z_values),
        "median_z": z_values[len(z_values) // 2],
        "z_ci80": [z_values[int(0.1 * len(z_values))], z_values[int(0.9 * len(z_values))]],
        "median_diff": diff_values[len(diff_values) // 2],
        "n_target": target,
    }


def main():
    print("Loading transcript + morphology + Davis attribution...")
    tx = Transcript()
    morph = Morphology()
    attr = load_attribution()

    print("\n" + "=" * 100)
    print("CONTENT-CLASS CLUSTERING ACROSS SCRIBES")
    print("Tests Reading C: substrate mode is content-determined; scribe identity is mediated")
    print("=" * 100)

    cells = [
        # (label, folios, scribe, currier, expected_mode)
        ("S1_herbal_pure_Q1-3",       SCRIBE1_HERBAL_PURE,        '1', 'A', 'flat?'),
        ("S1_herbal_mixed_Q4-7",      SCRIBE1_HERBAL_MIXED,       '1', 'A', 'flat?'),
        ("S1_Q15_pharma",             SCRIBE1_Q15_PHARMA,         '1', 'A', 'unknown'),
        ("S1_Q17_recipes",            SCRIBE1_Q17_RECIPES,        '1', 'A', 'unknown'),
        ("S2_botanical_Q4-7",         SCRIBE2_BOTANICAL,          '2', 'B', 'flat?'),
        ("S2_balneology_Q13",         SCRIBE2_BALNEOLOGY,         '2', 'B', 'period-2'),
        ("S2_rose_obverse_Q14",       SCRIBE2_ROSE_OBVERSE,       '2', 'B', 'unknown'),
        ("S3_botanical_Q8_Q16",       SCRIBE3_BOTANICAL_Q8_Q16,   '3', 'A', 'sustain?'),
        ("S3_matched_S_Q18",          MATCHED_S,                  '3', 'B', 'sustain'),
        ("S3_unmatched_S_Q18",        UNMATCHED_S,                '3', 'B', 'unknown'),
    ]

    results = {}
    print(f"\n{'Cell':<28}{'Scribe':>8}{'Currier':>8}{'N tokens':>10}{'lag1':>10}{'lag2':>10}{'mode':>14}")
    print("-" * 100)
    for label, folios, scribe, currier, expected in cells:
        r = analyze_cell(label, folios, tx, morph, attr, scribe, currier)
        if r is None:
            print(f"{label:<28}{scribe:>8}{currier:>8}{'(no data)':>10}")
            continue
        r["folios"] = folios
        r["expected_mode_pre_test"] = expected
        results[label] = r
        print(f"{label:<28}{scribe:>8}{currier:>8}{r['n_tokens']:>10}"
              f"{r['lag1']:>+10.4f}{r['lag2']:>+10.4f}{r['mode']:>14}")

    # ============================================================
    # Mode clustering analysis
    # ============================================================
    print("\n" + "=" * 100)
    print("MODE CLUSTERING (Reading C test)")
    print("=" * 100)

    by_mode = defaultdict(list)
    for label, r in results.items():
        if r['n_tokens'] >= 500:  # N floor for clustering
            by_mode[r["mode"]].append((label, r["scribe"], r["currier"], r["n_tokens"]))

    print(f"\nObserved modes across cells (N >= 500 tokens):")
    for mode, cells_in_mode in sorted(by_mode.items()):
        print(f"\n  {mode}:")
        for (label, scribe, currier, n) in cells_in_mode:
            print(f"    {label}  (Scribe {scribe}, Currier {currier}, N={n})")

    # Reading C predicts: same content class -> same mode, regardless of scribe
    # Check: botanical cells across scribes
    print(f"\n--- Within-content-class consistency check ---")
    botanical_cells = [(l, r) for l, r in results.items() if 'botanical' in l or 'herbal' in l]
    if len(botanical_cells) >= 2:
        modes = [r["mode"] for _, r in botanical_cells]
        n_distinct_modes = len(set(modes))
        print(f"  Botanical/herbal cells ({len(botanical_cells)}): modes = {modes}")
        if n_distinct_modes == 1:
            print(f"    -> SAME MODE across all botanical cells (any scribe) -- Reading C supported")
        elif n_distinct_modes == 2:
            print(f"    -> 2 distinct modes -- partial Reading C support; check N and methodology")
        else:
            print(f"    -> {n_distinct_modes} distinct modes -- Reading C weakened")

    # Same scribe across different content -> different modes
    print(f"\n--- Within-scribe content-flip check ---")
    by_scribe = defaultdict(list)
    for label, r in results.items():
        if r['n_tokens'] >= 500:
            by_scribe[r['scribe']].append((label, r['mode']))
    for scribe, cells_for_scribe in by_scribe.items():
        if len(cells_for_scribe) < 2:
            continue
        modes = [m for _, m in cells_for_scribe]
        n_distinct = len(set(modes))
        print(f"  Scribe {scribe} ({len(cells_for_scribe)} cells, N>=500): "
              f"modes = {modes} ({n_distinct} distinct)")

    # ============================================================
    # N-matched downsample controls on key comparisons
    # ============================================================
    print("\n" + "=" * 100)
    print("N-MATCHED DOWNSAMPLE CONTROLS")
    print("=" * 100)

    key_pairs = [
        ("S2_botanical_Q4-7", "S2_balneology_Q13"),
        ("S2_botanical_Q4-7", "S3_botanical_Q8_Q16"),  # cross-scribe botanical
        ("S3_matched_S_Q18",  "S3_unmatched_S_Q18"),
    ]
    nmatched_results = {}
    for la, lb in key_pairs:
        if la not in results or lb not in results:
            continue
        ra = results[la]
        rb = results[lb]
        print(f"\n  {la}  vs  {lb}:")
        print(f"    Raw N: {ra['n_tokens']} vs {rb['n_tokens']}")
        ctrl = n_matched_downsample_test(ra, rb, target_n=min(ra['n_tokens'], rb['n_tokens']),
                                         tx=tx, morph=morph, attr=attr, n_iter=20)
        if ctrl is None:
            print(f"    (insufficient data for matched test)")
            continue
        nmatched_results[f"{la}_vs_{lb}"] = ctrl
        print(f"    N-matched target: {ctrl['n_target']}")
        print(f"    Median z (n={ctrl['n_iter']} downsamples): {ctrl['median_z']:+.2f}")
        print(f"    80% CI on z: [{ctrl['z_ci80'][0]:+.2f}, {ctrl['z_ci80'][1]:+.2f}]")
        print(f"    Median diff: {ctrl['median_diff']:+.5f}")
        if abs(ctrl['median_z']) > 2.0:
            print(f"    -> Survives N-matching: real difference")
        elif abs(ctrl['median_z']) > 1.0:
            print(f"    -> Marginal under N-matching")
        else:
            print(f"    -> N-driven artifact; no real difference")

    # ============================================================
    # Verdict
    # ============================================================
    print("\n" + "=" * 100)
    print("PRE-REGISTERED VERDICT")
    print("=" * 100)

    # Reading C confirmed if:
    # 1. Botanical/herbal cells cluster into 1-2 modes (mostly same)
    # 2. Cross-scribe botanical comparison N-matched z not significant
    # 3. Scribe 2 balneology distinct from Scribe 2 botanical (survives N-matching)

    botanical_modes = set(r["mode"] for l, r in results.items()
                          if ('botanical' in l or 'herbal' in l) and r['n_tokens'] >= 500)

    nm_s2_content = nmatched_results.get("S2_botanical_Q4-7_vs_S2_balneology_Q13")
    nm_cross_botanical = nmatched_results.get("S2_botanical_Q4-7_vs_S3_botanical_Q8_Q16")

    s2_content_survives = nm_s2_content and abs(nm_s2_content["median_z"]) > 2.0
    cross_botanical_consistent = nm_cross_botanical and abs(nm_cross_botanical["median_z"]) < 1.5

    n_modes_observed = len(set(r["mode"] for r in results.values() if r['n_tokens'] >= 500))

    print(f"\nReading C predictions:")
    print(f"  Botanical/herbal cells share mode: {len(botanical_modes) <= 2} "
          f"(observed modes: {botanical_modes})")
    print(f"  Scribe 2 botanical vs balneology survives N-matching: {s2_content_survives}")
    print(f"  Scribe 2 botanical vs Scribe 3 botanical N-matched: "
          f"{'consistent' if cross_botanical_consistent else 'inconsistent'}")
    print(f"  Distinct substrate modes observed: {n_modes_observed}")

    if (len(botanical_modes) <= 2 and s2_content_survives
        and cross_botanical_consistent and n_modes_observed >= 2):
        verdict = ("READING C CONFIRMED: substrate signature is content-class determined. "
                   f"{n_modes_observed} substrate modes observed; "
                   f"botanical content shares mode across scribes; "
                   f"within-Scribe-2 content flip survives N-matching.")
    elif not s2_content_survives:
        verdict = ("READING C WEAKENED: Scribe 2 content flip does not survive N-matching. "
                   "Original z=-2.05 was N-driven artifact. INDEX-only, no constraint.")
    elif not cross_botanical_consistent:
        verdict = ("READING C MIXED: cross-scribe botanical comparison shows differences. "
                   "Scribes may have personal accent contributing alongside content effect.")
    else:
        verdict = "AMBIGUOUS: criteria partially met; document but do not register"

    print(f"\n  {verdict}")

    out = {
        "method": "Content-class clustering across Davis scribes (PHASE_702 expanded)",
        "test_design": "Reading C — substrate mode is content-determined, scribe-mediated",
        "ratio_valid_threshold": 0.015,
        "n_floor_for_clustering": 500,
        "per_cell_results": {k: {kk: vv for kk, vv in v.items() if kk != 'folios'}
                             for k, v in results.items()},
        "mode_clustering": dict(by_mode),
        "n_matched_controls": nmatched_results,
        "verdict": verdict,
        "reference_values": {
            "Voynich_Section_B_r21": -0.65,
            "Voynich_matched_S_r21": 0.66,
            "NL_Latin_r21_range": [-0.22, 0.05],
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

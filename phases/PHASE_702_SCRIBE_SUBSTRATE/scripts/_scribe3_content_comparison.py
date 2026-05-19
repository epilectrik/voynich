"""
PHASE_702 confirmation: within-Scribe-3 content comparison.

Mirror of Scribe-2 test (z=2.05 marginally supported Reading A). Scribe 3
wrote in distinct content domains:
  1. Q8 inner bifolium (f58/f65) and Q16 (f96) — botanical, transcript types
     this as Currier A (875 tokens, P-placement).
  2. Q18 starred paragraphs (f103-116) — matched-S material, Currier B
     (10,990 tokens, P-placement).
  3. Within Q18, project distinguishes matched-S vs unmatched-S folios.

Three partitions tested:
  - Scribe 3 botanical (Currier A typed, f58/f96)
  - Scribe 3 matched-S Q18 (Currier B)
  - Scribe 3 unmatched-S Q18 (Currier B)

If Scribe 3 r21 differs significantly across partitions: confirms Reading A
(content drives signature). The matched-S vs unmatched-S comparison is
particularly clean — same scribe, same quire, same dialect, same placement,
differing only in source-match status / sub-content.

Note: f58 is typed Currier A by the transcript. Davis assigns it to Scribe 3
(Q8 inner bifolium). The 875 Currier-A Scribe-3 tokens come from f58 and f96
per the audit. We use Currier A as a typed-content distinction here, not as
a different scribe.
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
OUT_PATH = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'results' / 'scribe3_content_comparison.json'

rng = random.Random(7023)

# Scribe 3's content partitions (from Davis Table 1 + audit)
# Currier A typed folios under Scribe 3 (per feasibility audit)
SCRIBE3_BOTANICAL_A = {'f58r', 'f58v', 'f96r', 'f96v'}

# Q18 starred paragraphs, matched-S vs unmatched-S (per project context)
MATCHED_S = {'f103r', 'f103v', 'f106r', 'f106v', 'f107r', 'f108r', 'f108v',
             'f111r', 'f112r', 'f112v', 'f113r', 'f113v', 'f114r', 'f114v',
             'f115r', 'f115v', 'f116r'}
UNMATCHED_S = {'f104r', 'f104v', 'f105r', 'f105v', 'f107v', 'f111v'}
# f116v is in Q18 but not classified as matched or unmatched in our reference set
ALL_Q18 = MATCHED_S | UNMATCHED_S | {'f116v'}


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


def bootstrap_r21(paragraphs_depths, n_boot=200, n_perm=50, eps=0.005):
    samples = []
    diffs = []
    n_paras = len(paragraphs_depths)
    if n_paras < 5:
        return None
    rng_boot = random.Random(70230)
    for _ in range(n_boot):
        sample_idx = [rng_boot.randrange(n_paras) for _ in range(n_paras)]
        sample = [paragraphs_depths[i] for i in sample_idx]
        rng_perm = random.Random(rng_boot.random())
        l1 = lag_excess_for_paragraphs(sample, 1, n_perm=n_perm, rng_local=rng_perm)
        l2 = lag_excess_for_paragraphs(sample, 2, n_perm=n_perm, rng_local=rng_perm)
        if l1 is None or l2 is None:
            continue
        lag1, lag2 = l1["excess"], l2["excess"]
        lag1_reg = lag1 if abs(lag1) >= eps else (eps if lag1 >= 0 else -eps)
        samples.append(lag2 / lag1_reg)
        diffs.append(lag2 - lag1)
    if not samples:
        return None
    samples.sort()
    diffs_sorted = sorted(diffs)
    mean = sum(samples) / len(samples)
    var = sum((x - mean) ** 2 for x in samples) / len(samples)
    diff_mean = sum(diffs) / len(diffs)
    diff_var = sum((x - diff_mean) ** 2 for x in diffs) / len(diffs)
    return {
        "r21_mean": mean, "r21_se": var ** 0.5,
        "r21_ci95": [samples[int(0.025 * len(samples))], samples[int(0.975 * len(samples))]],
        "lag2_minus_lag1_mean": diff_mean,
        "lag2_minus_lag1_se": diff_var ** 0.5,
        "lag2_minus_lag1_ci95": [diffs_sorted[int(0.025 * len(diffs_sorted))],
                                  diffs_sorted[int(0.975 * len(diffs_sorted))]],
        "n_boot": len(samples),
    }


def collect_paragraphs_for_folios(folios_set, tx, attr, scribe_filter='3',
                                   currier_filter=None, min_para=20, max_para=300):
    """Collect P-placement paragraphs from given folios, scribe-filtered.

    currier_filter: 'A', 'B', or None (any).
    """
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

    eligible = [(f, p) for (f, p) in paragraphs if min_para <= len(p) <= max_para]
    return eligible, paragraphs


def analyze_partition(label, folios_set, tx, morph, attr, currier_filter=None):
    paras, all_paras = collect_paragraphs_for_folios(folios_set, tx, attr,
                                                     scribe_filter='3',
                                                     currier_filter=currier_filter)
    print(f"\n  {label} (Currier={currier_filter or 'any'}):")
    print(f"    Folios in partition: {len(folios_set)}")
    print(f"    Paragraphs: {len(all_paras)} total, {len(paras)} eligible (20-300 tokens)")
    if not paras:
        return None
    n_tokens = sum(len(p) for (_, p) in paras)
    folios_covered = sorted(set(f for (f, _) in paras))
    print(f"    Folios with eligible paragraphs: {len(folios_covered)} ({', '.join(folios_covered[:6])}{'...' if len(folios_covered) > 6 else ''})")
    print(f"    Total tokens: {n_tokens}")

    depths = [[e_depth(w, morph) for w in p] for (f, p) in paras]
    l1 = lag_excess_for_paragraphs(depths, 1, n_perm=200)
    l2 = lag_excess_for_paragraphs(depths, 2, n_perm=200)
    l3 = lag_excess_for_paragraphs(depths, 3, n_perm=200)

    lag1, lag2, lag3 = l1["excess"], l2["excess"], l3["excess"]
    eps = 0.005
    lag1_reg = lag1 if abs(lag1) >= eps else (eps if lag1 >= 0 else -eps)
    r21 = lag2 / lag1_reg
    diff = lag2 - lag1

    boot = bootstrap_r21(depths, n_boot=200, n_perm=50)

    print(f"    Lag1 excess: {lag1:+.5f}")
    print(f"    Lag2 excess: {lag2:+.5f}")
    print(f"    Lag3 excess: {lag3:+.5f}")
    print(f"    r21 (regularized): {r21:+.4f}")
    print(f"    lag2 - lag1: {diff:+.5f}")
    if boot:
        print(f"    Bootstrap lag2-lag1: mean={boot['lag2_minus_lag1_mean']:+.5f}, "
              f"SE={boot['lag2_minus_lag1_se']:.5f}, "
              f"95% CI=[{boot['lag2_minus_lag1_ci95'][0]:+.5f}, {boot['lag2_minus_lag1_ci95'][1]:+.5f}]")

    return {
        "label": label,
        "currier_filter": currier_filter,
        "n_folios_in_partition": len(folios_set),
        "n_folios_with_paragraphs": len(folios_covered),
        "n_paragraphs_eligible": len(paras),
        "n_tokens": n_tokens,
        "folios_covered": folios_covered,
        "lag1_excess": lag1, "lag2_excess": lag2, "lag3_excess": lag3,
        "r21_regularized": r21, "lag2_minus_lag1": diff,
        "bootstrap": boot,
    }


def main():
    print("Loading transcript + morphology + Davis attribution...")
    tx = Transcript()
    morph = Morphology()
    attr = load_attribution()

    print("\n" + "=" * 90)
    print("WITHIN-SCRIBE-3 CONTENT COMPARISON (confirmation of Scribe-2 finding)")
    print("=" * 90)

    print("\nPartition definitions:")
    print(f"  Botanical (Q8/Q16): {len(SCRIBE3_BOTANICAL_A)} folios — typed Currier A")
    print(f"  Matched-S Q18: {len(MATCHED_S)} folios — typed Currier B")
    print(f"  Unmatched-S Q18: {len(UNMATCHED_S)} folios — typed Currier B")

    partitions = [
        ("botanical_Q8_Q16", SCRIBE3_BOTANICAL_A, 'A'),
        ("matched_S_Q18", MATCHED_S, 'B'),
        ("unmatched_S_Q18", UNMATCHED_S, 'B'),
    ]

    results = {}
    for label, folios, currier in partitions:
        r = analyze_partition(label, folios, tx, morph, attr, currier_filter=currier)
        if r:
            results[label] = r

    # Cross-partition summary
    print("\n" + "=" * 90)
    print("CROSS-PARTITION SUMMARY (all Scribe 3)")
    print("=" * 90)
    print(f"\n{'Partition':<22}{'Dialect':>8}{'N tok':>8}{'lag1':>10}{'lag2':>10}{'r21':>10}{'lag2-lag1':>12}")
    print("-" * 85)
    for label, r in results.items():
        print(f"{label:<22}{r['currier_filter']:>8}{r['n_tokens']:>8}"
              f"{r['lag1_excess']:>+10.4f}{r['lag2_excess']:>+10.4f}"
              f"{r['r21_regularized']:>+10.3f}{r['lag2_minus_lag1']:>+12.5f}")

    # Pairwise tests
    print("\n" + "=" * 90)
    print("PAIRWISE DIFFERENCE TESTS (lag2-lag1, bootstrap-SE-based)")
    print("=" * 90)
    labels = list(results.keys())
    pairwise = {}
    for i, l1 in enumerate(labels):
        for l2 in labels[i+1:]:
            r1 = results[l1]; r2 = results[l2]
            b1 = r1.get("bootstrap"); b2 = r2.get("bootstrap")
            if not (b1 and b2):
                continue
            diff = b1["lag2_minus_lag1_mean"] - b2["lag2_minus_lag1_mean"]
            pooled_se = math.sqrt(b1["lag2_minus_lag1_se"]**2 + b2["lag2_minus_lag1_se"]**2)
            z = diff / pooled_se if pooled_se > 0 else float('nan')
            pairwise[f"{l1}_vs_{l2}"] = {
                "diff_lag2_minus_lag1": diff, "pooled_SE": pooled_se, "z": z
            }
            interp = ("SIGNIFICANT (content drives)" if abs(z) > 2.0
                      else "MARGINAL" if abs(z) > 1.0
                      else "consistent (scribe-stable)")
            print(f"\n  {l1}  vs  {l2}:")
            print(f"    diff: {diff:+.5f}, pooled SE: {pooled_se:.5f}, z = {z:+.2f}  -> {interp}")

    # Verdict
    print("\n" + "=" * 90)
    print("VERDICT")
    print("=" * 90)
    z_values = [abs(p["z"]) for p in pairwise.values() if p["pooled_SE"] > 0]
    if not z_values:
        verdict = "INSUFFICIENT: <2 valid partitions"
    else:
        max_z = max(z_values)
        if max_z > 2.0:
            verdict = (f"READING A CONFIRMED (content-driven): max |z| = {max_z:.2f} > 2.0. "
                       "Scribe 3 produces different signatures on different content. "
                       "Replicates Scribe 2 finding.")
        elif max_z < 1.0:
            verdict = (f"READING B SUPPORTED (scribe-driven): max |z| = {max_z:.2f} < 1.0. "
                       "Scribe 3 maintains consistent signature across content types. "
                       "CONFLICTS with Scribe 2 finding — would need reconciliation.")
        else:
            verdict = (f"AMBIGUOUS: max |z| = {max_z:.2f}. "
                       "Direction matches Scribe-2 finding but not decisively.")

    print(f"\n  {verdict}")

    # Specific test: matched-S vs unmatched-S (cleanest, same scribe + same quire + same dialect)
    cleanest_key = "matched_S_Q18_vs_unmatched_S_Q18"
    if cleanest_key in pairwise:
        p = pairwise[cleanest_key]
        print(f"\nCLEANEST CONTROL — matched-S vs unmatched-S (same scribe, quire, dialect):")
        print(f"  diff = {p['diff_lag2_minus_lag1']:+.5f}, SE = {p['pooled_SE']:.5f}, z = {p['z']:+.2f}")
        if abs(p["z"]) > 2.0:
            print(f"  -> CONTENT differentiation within the same physical quire detected")
        elif abs(p["z"]) > 1.0:
            print(f"  -> MARGINAL differentiation; matched vs unmatched sub-content shows some shift")
        else:
            print(f"  -> NO sub-content differentiation within Q18 — matched and unmatched are equivalent")

    print(f"\nReference values:")
    print(f"  Voynich Section B r21 ~ -0.65 (period-2)")
    print(f"  Voynich matched-S r21 ~ +0.66 (sustain)")

    out = {
        "method": "Within-Scribe-3 content comparison (PHASE_702 confirmation)",
        "partitions_tested": [p[0] for p in partitions],
        "per_partition_results": results,
        "pairwise_z_tests": pairwise,
        "verdict": verdict,
        "reference_values": {
            "Voynich_Section_B_r21": -0.65,
            "Voynich_matched_S_r21": 0.66,
        },
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

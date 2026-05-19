"""
PHASE_702 follow-up: within-Scribe-2 content comparison.

Discriminating test for Reading A (recipe-driven) vs Reading B (scribe-driven):
  Compare Scribe 2's r21 across two distinct content types they wrote:
    - Botanical Q4-7 bifolia (Scribe 2's alternating bifolia)
    - Q13 balneology (entire quire — Section B reference territory)
    - Q14 Rose obverse (small N, supplementary)

  All three are Scribe 2, Currier B, P-placement, same paleographic hand.

If r21(botanical) ~ r21(balneology) ~ r21(rose), substrate signature is
SCRIBE-LOCAL (Reading B): Scribe 2 has a personal accent that persists
across content.

If r21 differs between partitions, substrate signature is CONTENT-DRIVEN
(Reading A): Scribe 2 is a transparent transmitter; the section's signature
passes through them.
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
OUT_PATH = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'results' / 'scribe2_content_comparison.json'

rng = random.Random(7022)

# Scribe 2's content partitions (from Davis Table 1)
SCRIBE2_BOTANICAL_BIFOLIA = {
    'f26r', 'f26v', 'f31r', 'f31v',  # Q4 bifolium 26/31
    'f33r', 'f33v', 'f40r', 'f40v',  # Q5 bifolium 33/40
    'f34r', 'f34v', 'f39r', 'f39v',  # Q5 bifolium 34/39
    'f43r', 'f43v', 'f46r', 'f46v',  # Q6 bifolium 43/46
    'f50r', 'f50v', 'f55r', 'f55v',  # Q7 bifolium 50/55
}

SCRIBE2_BALNEOLOGY = {f"f{n}{rv}" for n in range(75, 85) for rv in ['r', 'v']}

SCRIBE2_ROSE_OBVERSE = {'f85r1', 'f85r2'}


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
        "lag": lag,
        "n_pairs": total_pairs,
        "obs_rate": total_obs / total_pairs,
        "null_rate": total_null / total_pairs,
        "excess": (total_obs - total_null) / total_pairs,
    }


def bootstrap_r21(paragraphs_depths, n_boot=200, n_perm=50, eps=0.005):
    """Bootstrap r21 by resampling paragraphs.

    Uses regularized lag1 (lag1 + eps if |lag1| < eps) to suppress ratio
    explosions when lag1 happens near zero in some bootstrap samples.
    """
    samples = []
    diffs = []  # lag2 - lag1 (more stable than ratio)
    n_paras = len(paragraphs_depths)
    if n_paras < 5:
        return None
    rng_boot = random.Random(70220)
    for _ in range(n_boot):
        sample_idx = [rng_boot.randrange(n_paras) for _ in range(n_paras)]
        sample = [paragraphs_depths[i] for i in sample_idx]
        rng_perm = random.Random(rng_boot.random())
        l1 = lag_excess_for_paragraphs(sample, 1, n_perm=n_perm, rng_local=rng_perm)
        l2 = lag_excess_for_paragraphs(sample, 2, n_perm=n_perm, rng_local=rng_perm)
        if l1 is None or l2 is None:
            continue
        lag1 = l1["excess"]
        lag2 = l2["excess"]
        # Regularize for ratio stability
        lag1_reg = lag1 if abs(lag1) >= eps else (eps if lag1 >= 0 else -eps)
        r21 = lag2 / lag1_reg
        samples.append(r21)
        diffs.append(lag2 - lag1)
    if not samples:
        return None
    samples.sort()
    diffs_sorted = sorted(diffs)
    mean = sum(samples) / len(samples)
    var = sum((x - mean) ** 2 for x in samples) / len(samples)
    return {
        "r21_mean": mean,
        "r21_se": var ** 0.5,
        "r21_ci95": [samples[int(0.025 * len(samples))], samples[int(0.975 * len(samples))]],
        "lag2_minus_lag1_mean": sum(diffs) / len(diffs),
        "lag2_minus_lag1_se": (sum((x - sum(diffs)/len(diffs))**2 for x in diffs) / len(diffs)) ** 0.5,
        "lag2_minus_lag1_ci95": [diffs_sorted[int(0.025 * len(diffs_sorted))],
                                  diffs_sorted[int(0.975 * len(diffs_sorted))]],
        "n_boot": len(samples),
    }


def collect_paragraphs_for_folios(folios_set, tx, attr, scribe_filter='2',
                                   min_para=20, max_para=300):
    """Collect P-placement Currier B paragraphs from given folios, scribe-filtered."""
    keys = set(attr.keys())
    current_para = defaultdict(list)
    paragraphs = []  # list of (folio, word_list)

    for t in tx.all(h_only=True):
        if not t.word or '*' in t.word:
            continue
        if t.language != 'B':
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


def analyze_partition(label, folios_set, tx, morph, attr):
    paras, all_paras = collect_paragraphs_for_folios(folios_set, tx, attr)
    print(f"\n  {label}:")
    print(f"    Folios in partition: {len(folios_set)}")
    print(f"    Paragraphs collected: {len(all_paras)} total, {len(paras)} eligible (20-300 tokens)")
    if not paras:
        return None
    n_tokens = sum(len(p) for (_, p) in paras)
    folios_covered = sorted(set(f for (f, _) in paras))
    print(f"    Folios with eligible paragraphs: {len(folios_covered)}")
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
        print(f"    Bootstrap r21: mean={boot['r21_mean']:+.4f}, "
              f"SE={boot['r21_se']:.4f}, 95% CI=[{boot['r21_ci95'][0]:+.3f}, {boot['r21_ci95'][1]:+.3f}]")
        print(f"    Bootstrap lag2-lag1: mean={boot['lag2_minus_lag1_mean']:+.5f}, "
              f"SE={boot['lag2_minus_lag1_se']:.5f}, "
              f"95% CI=[{boot['lag2_minus_lag1_ci95'][0]:+.5f}, {boot['lag2_minus_lag1_ci95'][1]:+.5f}]")

    return {
        "label": label,
        "n_folios_in_partition": len(folios_set),
        "n_folios_with_paragraphs": len(folios_covered),
        "n_paragraphs_total": len(all_paras),
        "n_paragraphs_eligible": len(paras),
        "n_tokens": n_tokens,
        "folios_covered": folios_covered,
        "lag1_excess": lag1,
        "lag2_excess": lag2,
        "lag3_excess": lag3,
        "r21_regularized": r21,
        "lag2_minus_lag1": diff,
        "bootstrap": boot,
    }


def main():
    print("Loading transcript + morphology + Davis attribution...")
    tx = Transcript()
    morph = Morphology()
    attr = load_attribution()

    print("\n" + "=" * 90)
    print("WITHIN-SCRIBE-2 CONTENT COMPARISON")
    print("Tests whether Scribe 2's r21 is content-driven (Reading A) or scribe-driven (Reading B)")
    print("=" * 90)

    print("\nPartition definitions:")
    print(f"  Botanical (Q4-7 alternating bifolia): {len(SCRIBE2_BOTANICAL_BIFOLIA)} folios")
    print(f"  Balneology (Q13 entire): {len(SCRIBE2_BALNEOLOGY)} folios")
    print(f"  Rose obverse (Q14): {len(SCRIBE2_ROSE_OBVERSE)} folios")

    partitions = {
        "botanical_Q4-7": SCRIBE2_BOTANICAL_BIFOLIA,
        "balneology_Q13": SCRIBE2_BALNEOLOGY,
        "rose_obverse_Q14": SCRIBE2_ROSE_OBVERSE,
    }

    results = {}
    for label, folios in partitions.items():
        r = analyze_partition(label, folios, tx, morph, attr)
        if r:
            results[label] = r

    # Cross-partition comparison
    print("\n" + "=" * 90)
    print("CROSS-PARTITION SUMMARY (all Scribe 2)")
    print("=" * 90)
    print(f"\n{'Partition':<22}{'N tokens':>10}{'r21':>10}{'lag2-lag1':>14}{'boot SE (r21)':>16}")
    print("-" * 75)
    for label, r in results.items():
        boot = r.get("bootstrap")
        boot_se = boot["r21_se"] if boot else float('nan')
        print(f"{label:<22}{r['n_tokens']:>10}{r['r21_regularized']:>+10.4f}"
              f"{r['lag2_minus_lag1']:>+14.5f}{boot_se:>16.4f}")

    # Pairwise difference test (lag2-lag1 is more stable than ratio)
    print("\n" + "=" * 90)
    print("PAIRWISE DIFFERENCE TEST (on lag2-lag1, more stable than r21 ratio)")
    print("=" * 90)
    labels = list(results.keys())
    pairwise = {}
    for i, l1 in enumerate(labels):
        for l2 in labels[i+1:]:
            r1 = results[l1]
            r2 = results[l2]
            b1 = r1.get("bootstrap")
            b2 = r2.get("bootstrap")
            if not (b1 and b2):
                continue
            diff_means = b1["lag2_minus_lag1_mean"] - b2["lag2_minus_lag1_mean"]
            pooled_se = math.sqrt(b1["lag2_minus_lag1_se"]**2 + b2["lag2_minus_lag1_se"]**2)
            z = diff_means / pooled_se if pooled_se > 0 else float('nan')
            pairwise[f"{l1}_vs_{l2}"] = {
                "diff_lag2_minus_lag1": diff_means,
                "pooled_SE": pooled_se,
                "z": z,
            }
            print(f"\n  {l1}  vs  {l2}:")
            print(f"    diff in (lag2-lag1): {diff_means:+.5f}")
            print(f"    pooled SE: {pooled_se:.5f}")
            print(f"    z = {z:+.2f}")
            if abs(z) > 2.0:
                print(f"    -> SIGNIFICANT difference (|z|>2): content drives signature")
            elif abs(z) > 1.0:
                print(f"    -> MARGINAL difference (1<|z|<2)")
            else:
                print(f"    -> NO significant difference: scribe-consistent")

    # Verdict
    print("\n" + "=" * 90)
    print("VERDICT")
    print("=" * 90)

    z_values = [abs(p["z"]) for p in pairwise.values()]
    if not z_values:
        verdict = "INSUFFICIENT: <2 valid partitions"
    else:
        max_z = max(z_values)
        if max_z > 2.0:
            verdict = (f"READING A SUPPORTED (content-driven): max |z| = {max_z:.2f} > 2.0. "
                       "Same scribe produces different signatures on different content. "
                       "Substrate signature is content-driven; scribe is transparent transmitter.")
        elif max_z < 1.0:
            verdict = (f"READING B SUPPORTED (scribe-driven): max |z| = {max_z:.2f} < 1.0. "
                       "Same scribe produces consistent signature across content types. "
                       "Substrate signature is scribe-local (personal accent).")
        else:
            verdict = (f"AMBIGUOUS: max |z| = {max_z:.2f} (1.0 <= |z| <= 2.0). "
                       "Partial content effect within scribe; signal exists but is not decisive.")

    print(f"\n  {verdict}")

    # Reference values
    print(f"\nReference values for context:")
    print(f"  Voynich Section B (Q13 balneology) r21 ~ -0.65 (period-2)")
    print(f"  Voynich matched-S (Q18 starred paragraphs) r21 ~ +0.66 (sustain)")
    print(f"  NL Latin baselines r21 in [-0.22, +0.05]")

    out = {
        "method": "Within-Scribe-2 content partition test (PHASE_702 follow-up)",
        "question": "Does same scribe (paleographically identical hand) produce same r21 across different content?",
        "reading_A": "Recipe-driven: content determines signature; scribe is passthrough",
        "reading_B": "Scribe-driven: scribe has personal accent that persists across content",
        "partitions_tested": list(partitions.keys()),
        "per_partition_results": results,
        "pairwise_z_tests": pairwise,
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

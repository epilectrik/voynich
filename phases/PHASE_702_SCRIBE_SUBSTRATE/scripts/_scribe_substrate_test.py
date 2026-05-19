"""
PHASE_702 main test: Engineered substrate metrics per Davis scribe.

Computes for each scribe (2, 3, 4 - Currier B writers with N>=1000):
  - C2032 e-depth lag2/lag1 ratio (period-2 signature)
  - C2015 e-depth class entropy (bits per token)
  - C2022 Markov plateau order on e-depth class sequence

Within-paragraph shuffle null for C2032. Bootstrap by paragraph for SEs.

Pre-registered decision rules (locked from INDEX.md):
  Hypothesis A (substrate-as-grammar):  F-ratio <= 1.5 AND no scribe > 2sigma
  Hypothesis B (substrate-as-convention): F-ratio >= 3.0 AND >=1 scribe > 2sigma
  Ambiguous: 1.5 < F-ratio < 3.0 OR contradictory criteria
"""
from __future__ import annotations

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
import csv

ATTRIBUTION_CSV = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'data' / 'davis_scribe_attribution.csv'
OUT_PATH = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'results' / 'scribe_substrate_test.json'

rng = random.Random(702)


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


def build_paragraphs_per_scribe(currier='B'):
    """Build paragraph sequences per scribe in given Currier class."""
    tx = Transcript()
    attr = load_attribution()
    keys = set(attr.keys())

    # Per scribe -> list of (folio, paragraph_word_list)
    scribe_paras = defaultdict(list)
    current_para = defaultdict(list)
    current_folio_scribe = {}

    for t in tx.all(h_only=True):
        if not t.word or '*' in t.word:
            continue
        if t.language != currier:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue

        matched = folio_match(t.folio, keys)
        if matched is None:
            continue
        scribe = attr[matched]

        key = (scribe, t.folio)
        if t.par_initial and current_para[key]:
            scribe_paras[scribe].append((t.folio, current_para[key]))
            current_para[key] = []
        current_para[key].append(t.word.lower())

    for (scribe, folio), p in current_para.items():
        if p:
            scribe_paras[scribe].append((folio, p))

    return scribe_paras


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
    """Compute observed - shuffled-null lag-N same-value rate."""
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


def shannon_entropy(items):
    c = Counter(items)
    n = sum(c.values())
    if n == 0:
        return 0.0
    return -sum((v / n) * math.log2(v / n) for v in c.values() if v)


def ngram_surprise(tokens, order):
    if order == 0:
        return shannon_entropy(tokens)
    if len(tokens) <= order:
        return float("nan")
    counts = Counter()
    contexts = Counter()
    for i in range(len(tokens) - order):
        ctx = tuple(tokens[i:i + order])
        nxt = tokens[i + order]
        counts[(ctx, nxt)] += 1
        contexts[ctx] += 1
    V = len(set(tokens))
    total = 0.0
    n = len(tokens) - order
    for i in range(n):
        ctx = tuple(tokens[i:i + order])
        nxt = tokens[i + order]
        c_ctx_nxt = counts[(ctx, nxt)]
        c_ctx = contexts[ctx]
        p = (c_ctx_nxt + 1) / (c_ctx + V)
        total += -math.log2(p)
    return total / n


def markov_plateau(class_sequence, max_order=4):
    orders = {}
    for o in range(0, max_order + 1):
        orders[o] = ngram_surprise(class_sequence, o)
    plateau_order = None
    prev = orders[0]
    for o in range(1, max_order + 1):
        if math.isnan(orders[o]):
            break
        if prev - orders[o] < 0.1:
            plateau_order = o - 1
            break
        prev = orders[o]
    if plateau_order is None:
        plateau_order = max_order
    return orders, plateau_order


def bootstrap_r21(paragraphs_depths, n_boot=200, n_perm=50):
    """Bootstrap r21 by resampling paragraphs with replacement."""
    r21_samples = []
    n_paras = len(paragraphs_depths)
    if n_paras < 5:
        return None
    rng_boot = random.Random(7020)
    for _ in range(n_boot):
        sample_idx = [rng_boot.randrange(n_paras) for _ in range(n_paras)]
        sample = [paragraphs_depths[i] for i in sample_idx]
        rng_perm = random.Random(rng_boot.random())
        lag1 = lag_excess_for_paragraphs(sample, 1, n_perm=n_perm, rng_local=rng_perm)
        lag2 = lag_excess_for_paragraphs(sample, 2, n_perm=n_perm, rng_local=rng_perm)
        if lag1 is None or lag2 is None or abs(lag1["excess"]) < 1e-9:
            continue
        r21_samples.append(lag2["excess"] / lag1["excess"])
    if not r21_samples:
        return None
    r21_samples.sort()
    return {
        "mean": sum(r21_samples) / len(r21_samples),
        "se": (sum((x - sum(r21_samples) / len(r21_samples)) ** 2 for x in r21_samples) / len(r21_samples)) ** 0.5,
        "ci95_lo": r21_samples[int(0.025 * len(r21_samples))],
        "ci95_hi": r21_samples[int(0.975 * len(r21_samples))],
        "n_boot": len(r21_samples),
    }


def main():
    print("Loading Voynich transcript + morphology + Davis attribution...")
    morph = Morphology()

    # Build per-scribe paragraph collections (Currier B P-placement)
    scribe_paras = build_paragraphs_per_scribe(currier='B')

    # Filter: paragraphs must be >= 20 tokens for autocorrelation stability
    MIN_PARA = 20
    MAX_PARA = 300
    eligible_scribes = ['2', '3', '4']

    results_by_scribe = {}

    print()
    print("=" * 90)
    print("PER-SCRIBE ENGINEERED SUBSTRATE METRICS")
    print("Currier B, P-placement, paragraph length in [%d, %d]" % (MIN_PARA, MAX_PARA))
    print("=" * 90)

    for scribe in eligible_scribes:
        paras = [(f, p) for (f, p) in scribe_paras.get(scribe, [])
                 if MIN_PARA <= len(p) <= MAX_PARA]
        if not paras:
            print(f"\nScribe {scribe}: NO ELIGIBLE PARAGRAPHS")
            continue

        # Build depth sequences
        depths_per_para = [[e_depth(w, morph) for w in p] for (f, p) in paras]
        all_depths = [d for para in depths_per_para for d in para]
        n_paras = len(paras)
        n_tokens = len(all_depths)

        # C2015: e-depth class entropy
        entropy_bpt = shannon_entropy(all_depths)

        # C2022: Markov plateau
        orders, plateau = markov_plateau(all_depths, max_order=4)

        # C2032: lag1, lag2, lag3 excess + r21
        lag1 = lag_excess_for_paragraphs(depths_per_para, 1, n_perm=200)
        lag2 = lag_excess_for_paragraphs(depths_per_para, 2, n_perm=200)
        lag3 = lag_excess_for_paragraphs(depths_per_para, 3, n_perm=200)

        r21 = lag2["excess"] / lag1["excess"] if abs(lag1["excess"]) > 1e-9 else float("nan")
        r31 = lag3["excess"] / lag1["excess"] if abs(lag1["excess"]) > 1e-9 else float("nan")

        # Bootstrap SE on r21
        boot = bootstrap_r21(depths_per_para, n_boot=100, n_perm=50)

        # Folios covered
        folios = sorted(set(f for (f, _) in paras))

        results_by_scribe[scribe] = {
            "n_paragraphs": n_paras,
            "n_tokens": n_tokens,
            "n_folios": len(folios),
            "folios": folios,
            "C2015_entropy_bpt": entropy_bpt,
            "C2022_markov_orders_bpc": orders,
            "C2022_plateau_order": plateau,
            "C2032_lag1": lag1,
            "C2032_lag2": lag2,
            "C2032_lag3": lag3,
            "C2032_r21": r21,
            "C2032_r31": r31,
            "bootstrap_r21": boot,
        }

        print(f"\nScribe {scribe}:")
        print(f"  N paragraphs: {n_paras}, N tokens: {n_tokens}, N folios: {len(folios)}")
        print(f"  C2015 e-depth entropy: {entropy_bpt:.4f} bits/token")
        print(f"  C2022 Markov plateau order: {plateau}")
        print(f"  C2032 lag1 excess: {lag1['excess']:+.5f}")
        print(f"  C2032 lag2 excess: {lag2['excess']:+.5f}")
        print(f"  C2032 lag3 excess: {lag3['excess']:+.5f}")
        print(f"  C2032 r21 (lag2/lag1): {r21:+.4f}")
        if boot:
            print(f"  Bootstrap r21: mean={boot['mean']:+.4f}, SE={boot['se']:.4f}, "
                  f"95% CI=[{boot['ci95_lo']:+.4f}, {boot['ci95_hi']:+.4f}]")

    # Cross-scribe comparison
    print()
    print("=" * 90)
    print("CROSS-SCRIBE COMPARISON")
    print("=" * 90)

    r21_values = {s: r["C2032_r21"] for s, r in results_by_scribe.items()}
    boot_means = {s: r["bootstrap_r21"]["mean"] if r["bootstrap_r21"] else None
                  for s, r in results_by_scribe.items()}
    boot_ses = {s: r["bootstrap_r21"]["se"] if r["bootstrap_r21"] else None
                for s, r in results_by_scribe.items()}

    print(f"\n{'Scribe':<10}{'r21':>10}{'boot_mean':>12}{'boot_SE':>10}{'95% CI':>20}")
    print("-" * 60)
    for s in eligible_scribes:
        if s not in results_by_scribe:
            continue
        r = results_by_scribe[s]
        b = r["bootstrap_r21"]
        ci = f"[{b['ci95_lo']:+.3f},{b['ci95_hi']:+.3f}]" if b else "N/A"
        print(f"Scribe {s:<3}{r['C2032_r21']:>+10.4f}"
              f"{b['mean']:>+12.4f}"
              f"{b['se']:>10.4f}"
              f"{ci:>20}")

    # Pairwise comparison: is |r21_i - r21_j| > 2 * sqrt(SE_i^2 + SE_j^2)?
    print(f"\nPairwise scribe-r21 differences (z = diff / pooled_SE):")
    valid_scribes = [s for s in eligible_scribes if boot_means[s] is not None]
    pairwise = {}
    for i, s1 in enumerate(valid_scribes):
        for s2 in valid_scribes[i+1:]:
            diff = boot_means[s1] - boot_means[s2]
            pooled_se = math.sqrt(boot_ses[s1]**2 + boot_ses[s2]**2)
            z = diff / pooled_se if pooled_se > 0 else float('nan')
            pairwise[f"S{s1}_vs_S{s2}"] = {
                "diff": diff, "pooled_SE": pooled_se, "z": z
            }
            print(f"  Scribe {s1} vs Scribe {s2}: diff={diff:+.4f}, SE={pooled_se:.4f}, z={z:+.2f}")

    # F-ratio: between-scribe variance vs within-scribe variance
    if len(valid_scribes) >= 2:
        scribe_means = [boot_means[s] for s in valid_scribes]
        grand_mean = sum(scribe_means) / len(scribe_means)
        between_var = sum((m - grand_mean) ** 2 for m in scribe_means) / (len(scribe_means) - 1) if len(scribe_means) > 1 else 0
        within_var = sum(boot_ses[s] ** 2 for s in valid_scribes) / len(valid_scribes)
        f_ratio = between_var / within_var if within_var > 0 else float('inf')

        # Per-scribe z vs corpus mean
        z_vs_mean = {}
        for s in valid_scribes:
            z = (boot_means[s] - grand_mean) / boot_ses[s] if boot_ses[s] > 0 else float('nan')
            z_vs_mean[s] = z

        print(f"\nGrand mean r21: {grand_mean:+.4f}")
        print(f"Between-scribe variance: {between_var:.6f}")
        print(f"Within-scribe variance (pooled SE^2): {within_var:.6f}")
        print(f"F-ratio (between/within): {f_ratio:.3f}")

        print(f"\nPer-scribe z vs grand mean:")
        for s in valid_scribes:
            print(f"  Scribe {s}: z = {z_vs_mean[s]:+.2f}")

        # Pre-registered decision
        any_2sigma = any(abs(z) > 2.0 for z in z_vs_mean.values())
        if f_ratio <= 1.5 and not any_2sigma:
            verdict = "HYPOTHESIS A SUPPORTED: substrate-as-grammar (scribe-invariant)"
        elif f_ratio >= 3.0 and any_2sigma:
            verdict = "HYPOTHESIS B SUPPORTED: substrate-as-convention (scribe-variable)"
        else:
            verdict = "AMBIGUOUS: F-ratio in transition zone or contradictory criteria"

        print()
        print("=" * 90)
        print("PRE-REGISTERED VERDICT")
        print("=" * 90)
        print(f"\n  {verdict}")

        # Voynich reference: Section B r21 = -0.65; matched-S r21 = +0.66
        print(f"\nReference comparisons:")
        print(f"  Voynich Section B (Q13 balneology) r21 reference: ~-0.65 (period-2)")
        print(f"  Voynich matched-S (starred paragraphs) r21 reference: ~+0.66 (sustain)")
        print(f"  NL Latin baselines: r21 in [-0.22, +0.05]")
    else:
        verdict = "INSUFFICIENT: <2 eligible scribes for cross-scribe test"
        f_ratio = None
        between_var = within_var = grand_mean = None
        z_vs_mean = {}
        print(f"\n  {verdict}")

    # Save
    out = {
        "method": "PHASE_702 scribe x engineered-substrate metrics test",
        "pre_registered_decision_rules": {
            "Hypothesis A (substrate-as-grammar)": "F-ratio <= 1.5 AND no scribe > 2sigma from grand mean",
            "Hypothesis B (substrate-as-convention)": "F-ratio >= 3.0 AND >=1 scribe > 2sigma",
            "Ambiguous": "otherwise",
        },
        "filter": {
            "currier": "B",
            "placement": "P (paragraph text only)",
            "min_paragraph_length": MIN_PARA,
            "max_paragraph_length": MAX_PARA,
            "transcriber": "H",
        },
        "per_scribe": results_by_scribe,
        "cross_scribe": {
            "valid_scribes": valid_scribes if len(valid_scribes) >= 2 else [],
            "grand_mean_r21": grand_mean,
            "between_scribe_variance": between_var,
            "within_scribe_variance_pooled_SE_sq": within_var,
            "F_ratio": f_ratio,
            "z_vs_grand_mean": z_vs_mean,
            "pairwise_differences": pairwise if len(valid_scribes) >= 2 else {},
        },
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

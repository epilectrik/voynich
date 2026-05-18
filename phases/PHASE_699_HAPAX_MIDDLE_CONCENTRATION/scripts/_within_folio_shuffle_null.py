"""Within-folio shuffle null on hapax×dark RATE vs hapax ENRICHMENT correlation.

Expert verdict required this before any Finding 1 registration. Per
feedback_within_folio_shuffle_null_first.md: aggregate r in +0.15 to +0.65
range with no within-folio null = composition-shadow signature.

Null model: shuffle MIDDLE-to-folio assignments while preserving each folio's
total token count and the global MIDDLE frequency distribution. Recompute the
partial correlation under each shuffle. If observed partial r (0.40) is
within 2σ of the null mean, signal is composition shadow.

Pre-registered decision rule:
  z >= +2.0 → Finding 1 signal genuine, register at Tier 2/3
  z <  +2.0 → Composition shadow, register methodology correction alone
"""
import json
import math
import random
import sys, io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()
random.seed(42)


def collect_data():
    tx = Transcript()
    middle_folio = defaultdict(lambda: Counter())
    folio_totals = Counter()
    folio_middle_types = defaultdict(set)
    for t in tx.currier_b():
        if not t.word or t.is_uncertain:
            continue
        if not t.placement:
            continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middle_folio[m.middle][t.folio] += 1
                folio_totals[t.folio] += 1
                folio_middle_types[t.folio].add(m.middle)
        except Exception:
            pass
    return dict(middle_folio), dict(folio_totals), dict(folio_middle_types)


def pearson(x, y):
    n = len(x)
    if n < 2: return 0
    mx, my = sum(x)/n, sum(y)/n
    num = sum((x[i]-mx)*(y[i]-my) for i in range(n))
    dx = math.sqrt(sum((x[i]-mx)**2 for i in range(n)))
    dy = math.sqrt(sum((y[i]-my)**2 for i in range(n)))
    return num / (dx*dy) if dx*dy else 0


def partial_correlation(x, y, z):
    """Partial correlation of x,y controlling for z."""
    r_xy = pearson(x, y)
    r_xz = pearson(x, z)
    r_yz = pearson(y, z)
    denom = math.sqrt((1 - r_xz**2) * (1 - r_yz**2))
    if denom == 0: return 0
    return (r_xy - r_xz * r_yz) / denom


def compute_metrics(middle_folio_dict, folio_totals, dark_set):
    """Compute per-folio hapax_dark_rate, hapax_enrichment, TTR for a given MIDDLE-folio assignment."""
    # Frequency per MIDDLE
    middle_freq = {m: sum(fc.values()) for m, fc in middle_folio_dict.items()}
    # Hapax + dark sets
    hapax_set = set(m for m, f in middle_freq.items() if f == 1)
    hapax_dark = hapax_set & dark_set

    # Per-folio: hapax token count, hapax×dark token count
    folio_hapax = Counter()
    folio_hapax_dark = Counter()
    folio_types = defaultdict(set)
    for m, fc in middle_folio_dict.items():
        is_hapax = m in hapax_set
        is_hapax_dark = m in hapax_dark
        for folio, count in fc.items():
            folio_types[folio].add(m)
            if is_hapax:
                folio_hapax[folio] += count
            if is_hapax_dark:
                folio_hapax_dark[folio] += count

    # Per-folio metrics
    total_hapax = sum(folio_hapax.values())
    total_tokens = sum(folio_totals.values())
    folios = sorted(folio_totals.keys())
    hapax_enrich = []
    hapax_dark_rate = []
    ttr = []
    for f in folios:
        ft = folio_totals.get(f, 0)
        if ft == 0:
            hapax_enrich.append(0)
            hapax_dark_rate.append(0)
            ttr.append(0)
            continue
        expected_hapax = total_hapax * (ft / total_tokens)
        e = folio_hapax[f] / expected_hapax if expected_hapax > 0 else 0
        r = folio_hapax_dark[f] / ft
        t = len(folio_types[f]) / ft
        hapax_enrich.append(e)
        hapax_dark_rate.append(r)
        ttr.append(t)
    return hapax_enrich, hapax_dark_rate, ttr, folios


def shuffle_middle_folio_assignment(middle_folio, folio_totals, dark_set):
    """Generate a null assignment: preserve per-folio token counts and global
    MIDDLE frequency distribution, but randomize which MIDDLEs land where.

    Implementation: build a flat list of (middle, count) tokens; shuffle;
    redistribute to folios maintaining each folio's total count.
    """
    # Flat token list — each MIDDLE appears N times where N is its corpus count
    flat_middles = []
    for m, fc in middle_folio.items():
        n = sum(fc.values())
        flat_middles.extend([m] * n)
    random.shuffle(flat_middles)

    # Redistribute to folios
    new_middle_folio = defaultdict(lambda: Counter())
    idx = 0
    for folio, total in folio_totals.items():
        for _ in range(total):
            if idx >= len(flat_middles): break
            new_middle_folio[flat_middles[idx]][folio] += 1
            idx += 1
    return dict(new_middle_folio)


def main():
    print("Loading data...")
    middle_folio, folio_totals, folio_middle_types = collect_data()
    dark_data = json.loads((ROOT / "data/dark_pipeline_middles.json").read_text(encoding="utf-8"))
    dark_set = set(dark_data["middles"])
    print(f"  MIDDLEs: {len(middle_folio)}, Folios: {len(folio_totals)}, Tokens: {sum(folio_totals.values())}")

    # =================================================================
    # Observed: compute the partial correlation
    # =================================================================
    obs_enrich, obs_dark_rate, obs_ttr, folios = compute_metrics(middle_folio, folio_totals, dark_set)
    # Restrict to folios with any dark pipeline
    folios_with_dark = [i for i in range(len(folios)) if any(
        m in dark_set for m in folio_middle_types.get(folios[i], set())
    )]
    enrich_sub = [obs_enrich[i] for i in folios_with_dark]
    rate_sub = [obs_dark_rate[i] for i in folios_with_dark]
    ttr_sub = [obs_ttr[i] for i in folios_with_dark]

    obs_partial_r = partial_correlation(rate_sub, enrich_sub, ttr_sub)
    obs_raw_r = pearson(rate_sub, enrich_sub)
    print(f"\nObserved:")
    print(f"  Raw r(hapax_dark_rate, hapax_enrich): {obs_raw_r:.4f}")
    print(f"  Partial r (TTR-controlled): {obs_partial_r:.4f}")

    # =================================================================
    # Null distribution
    # =================================================================
    n_perms = 200
    print(f"\nGenerating null distribution (n={n_perms} permutations)...")
    null_partial_rs = []
    null_raw_rs = []
    for i in range(n_perms):
        if (i+1) % 50 == 0:
            print(f"  perm {i+1}/{n_perms}")
        shuffled = shuffle_middle_folio_assignment(middle_folio, folio_totals, dark_set)
        n_enrich, n_rate, n_ttr, n_folios = compute_metrics(shuffled, folio_totals, dark_set)
        # Restrict similarly to folios with dark pipeline in shuffled data
        n_folios_with_dark = [i for i in range(len(n_folios)) if any(
            m in dark_set for m in [m2 for m2, fc in shuffled.items() if n_folios[i] in fc]
        )]
        if len(n_folios_with_dark) < 5:
            null_partial_rs.append(0)
            null_raw_rs.append(0)
            continue
        n_enrich_sub = [n_enrich[i] for i in n_folios_with_dark]
        n_rate_sub = [n_rate[i] for i in n_folios_with_dark]
        n_ttr_sub = [n_ttr[i] for i in n_folios_with_dark]
        null_partial_rs.append(partial_correlation(n_rate_sub, n_enrich_sub, n_ttr_sub))
        null_raw_rs.append(pearson(n_rate_sub, n_enrich_sub))

    # Statistics
    mean_null = sum(null_partial_rs) / n_perms
    sd_null = math.sqrt(sum((r - mean_null)**2 for r in null_partial_rs) / n_perms)
    z = (obs_partial_r - mean_null) / sd_null if sd_null > 0 else 0

    mean_null_raw = sum(null_raw_rs) / n_perms
    sd_null_raw = math.sqrt(sum((r - mean_null_raw)**2 for r in null_raw_rs) / n_perms)
    z_raw = (obs_raw_r - mean_null_raw) / sd_null_raw if sd_null_raw > 0 else 0

    # P-value: how many null partial_rs >= observed?
    n_ge = sum(1 for r in null_partial_rs if r >= obs_partial_r)
    p_value = n_ge / n_perms

    print(f"\n=== WITHIN-FOLIO SHUFFLE NULL RESULT ===")
    print(f"  Observed partial r (TTR-controlled): {obs_partial_r:.4f}")
    print(f"  Null distribution: mean={mean_null:.4f}, SD={sd_null:.4f}")
    print(f"  z-score: {z:.3f}")
    print(f"  P(null >= observed): {p_value:.4f}")
    print(f"\n  Observed raw r: {obs_raw_r:.4f}")
    print(f"  Null raw r: mean={mean_null_raw:.4f}, SD={sd_null_raw:.4f}, z={z_raw:.3f}")

    print(f"\n=== PRE-REGISTERED DECISION RULE ===")
    print(f"  z >= +2.0 → Finding 1 signal genuine, register at Tier 2/3")
    print(f"  z <  +2.0 → Composition shadow, register methodology correction alone")
    print(f"\n  Observed partial r z: {z:.3f}")
    if z >= 2.0:
        print(f"  VERDICT: SIGNAL GENUINE (z={z:.2f} >= 2.0)")
    else:
        print(f"  VERDICT: COMPOSITION SHADOW (z={z:.2f} < 2.0)")
        print(f"  Finding 1 is folio-composition artifact, NOT register at correlation tier")

    OUT = ROOT / "phases/PHASE_699_HAPAX_MIDDLE_CONCENTRATION/results/within_folio_shuffle_null.json"
    OUT.write_text(json.dumps({
        "method": "Within-folio shuffle null: permute MIDDLE-folio assignment preserving per-folio token counts and global MIDDLE frequency",
        "n_perms": n_perms,
        "observed_partial_r": obs_partial_r,
        "observed_raw_r": obs_raw_r,
        "null_mean_partial": mean_null,
        "null_sd_partial": sd_null,
        "z_score_partial": z,
        "p_value": p_value,
        "null_mean_raw": mean_null_raw,
        "null_sd_raw": sd_null_raw,
        "z_score_raw": z_raw,
        "decision": "SIGNAL_GENUINE" if z >= 2.0 else "COMPOSITION_SHADOW",
    }, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()

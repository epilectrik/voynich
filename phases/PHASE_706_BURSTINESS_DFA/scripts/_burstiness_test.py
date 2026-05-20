"""
PHASE_706 Test 1: Burstiness β (Weibull shape parameter) for top-50 frequent
tokens.

Methodology (from Altmann et al. 2009 PLOS ONE):
  1. For each corpus, extract token sequence in reading order
  2. Identify top-50 most frequent tokens with >=20 occurrences
  3. For each token, compute inter-arrival times (gaps between consecutive
     positions in the sequence)
  4. Fit Weibull distribution to inter-arrival times
  5. Record shape parameter β
  6. Median/mean/IQR of β across the 50 tokens

Pre-registered thresholds (LOCKED):
  - β median < 0.85 → NL-like burstiness (semantic clustering)
  - β median > 0.95 → Poisson-like (no clustering)
  - 0.85 ≤ β median ≤ 0.95 → ambiguous

Sanity check: random shuffle of any corpus must give β ≈ 1.0
              NL baselines (Codicillus, Mesue, Brunschwig) must give β < 0.95
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

OUT_PATH = ROOT / 'phases' / 'PHASE_706_BURSTINESS_DFA' / 'results' / 'burstiness_results.json'

TOP_K = 50
MIN_OCCURRENCES = 20
N_RANDOM_NULL = 1

# Pre-registered thresholds (LOCKED before any runs)
NL_LIKE_THRESHOLD = 0.85
POISSON_THRESHOLD = 0.95


def load_voynich_tokens(currier='B'):
    """Load Voynich token sequence (H-track, P-placement) in reading order."""
    tx = Transcript()
    tokens = []
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != currier:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        tokens.append(t.word.lower())
    return tokens


def load_text_corpus(path, max_tokens=None):
    """Load a Latin/German plain-text corpus as a token sequence.

    Simple tokenization: split on whitespace, lowercase, strip punctuation.
    """
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    # Basic cleanup: lowercase, strip non-letter characters except space
    text = text.lower()
    # Replace non-alpha (keep spaces) with spaces
    text = re.sub(r'[^a-zäöüß\s]', ' ', text)
    tokens = text.split()
    # Filter very short tokens (single characters)
    tokens = [t for t in tokens if len(t) >= 2]
    if max_tokens:
        tokens = tokens[:max_tokens]
    return tokens


def compute_inter_arrival_times(token_seq, target_token):
    """Get positions of target_token in sequence; return diffs."""
    positions = [i for i, t in enumerate(token_seq) if t == target_token]
    if len(positions) < 2:
        return None
    return np.diff(positions)


def fit_weibull_beta(intervals):
    """Fit Weibull to inter-arrival intervals; return shape parameter β.

    Uses scipy.stats.weibull_min with location fixed at 0 (standard form).
    Returns (β, scale) or (None, None) if fit fails.
    """
    if intervals is None or len(intervals) < 5:
        return None, None
    try:
        # weibull_min.fit returns (shape, loc, scale)
        # Fix loc=0 (standard exponential family form)
        params = stats.weibull_min.fit(intervals, floc=0)
        shape, _, scale = params
        return float(shape), float(scale)
    except Exception:
        return None, None


def burstiness_for_corpus(tokens, label, top_k=TOP_K, min_occ=MIN_OCCURRENCES):
    """Compute burstiness β for top-K most frequent tokens in corpus."""
    if len(tokens) < 1000:
        return {"label": label, "error": f"corpus too small: {len(tokens)} tokens"}

    freq = Counter(tokens)
    # Top tokens with at least min_occ occurrences
    candidates = [t for t, c in freq.most_common() if c >= min_occ]
    target_tokens = candidates[:top_k]

    print(f"\n  {label}:")
    print(f"    Corpus size: {len(tokens)} tokens, {len(freq)} unique types")
    print(f"    Top-{len(target_tokens)} frequent tokens with >={min_occ} occurrences")
    print(f"    Top-5 by freq: {[(t, freq[t]) for t in target_tokens[:5]]}")

    betas = []
    per_token = []
    for tok in target_tokens:
        intervals = compute_inter_arrival_times(tokens, tok)
        beta, scale = fit_weibull_beta(intervals)
        if beta is not None:
            betas.append(beta)
            per_token.append({
                "token": tok,
                "freq": freq[tok],
                "beta": beta,
                "scale": scale,
                "mean_interval": float(np.mean(intervals)) if intervals is not None else None,
                "n_intervals": len(intervals) if intervals is not None else 0,
            })

    if not betas:
        return {"label": label, "error": "no successful Weibull fits"}

    betas_sorted = sorted(betas)
    n = len(betas)
    result = {
        "label": label,
        "n_tokens": len(tokens),
        "n_unique": len(freq),
        "n_top_tokens": len(target_tokens),
        "n_successful_fits": n,
        "beta_median": float(np.median(betas)),
        "beta_mean": float(np.mean(betas)),
        "beta_iqr": [float(betas_sorted[n // 4]), float(betas_sorted[3 * n // 4])],
        "beta_range": [float(min(betas)), float(max(betas))],
        "fraction_below_0_85": sum(1 for b in betas if b < 0.85) / n,
        "fraction_above_0_95": sum(1 for b in betas if b > 0.95) / n,
        "per_token_top10": per_token[:10],
    }

    # Apply pre-registered decision rule
    beta_med = result["beta_median"]
    if beta_med < NL_LIKE_THRESHOLD:
        verdict = "NL-LIKE (β median < 0.85, semantic clustering)"
    elif beta_med > POISSON_THRESHOLD:
        verdict = "POISSON-LIKE (β median > 0.95, no clustering)"
    else:
        verdict = "AMBIGUOUS (0.85 ≤ β median ≤ 0.95)"
    result["verdict"] = verdict
    print(f"    β median: {beta_med:.3f}  →  {verdict}")
    print(f"    β IQR: [{result['beta_iqr'][0]:.3f}, {result['beta_iqr'][1]:.3f}]")
    print(f"    Fraction β<0.85: {result['fraction_below_0_85']:.1%}; β>0.95: {result['fraction_above_0_95']:.1%}")

    return result


def main():
    print("=" * 90)
    print("PHASE_706 BURSTINESS TEST — Weibull β for top-50 frequent tokens")
    print("=" * 90)
    print(f"\nPre-registered thresholds (LOCKED):")
    print(f"  β median < {NL_LIKE_THRESHOLD} → NL-like (semantic clustering)")
    print(f"  β median > {POISSON_THRESHOLD} → Poisson (no clustering)")
    print(f"  {NL_LIKE_THRESHOLD} ≤ β median ≤ {POISSON_THRESHOLD} → ambiguous")
    print(f"\nTop-K = {TOP_K}, min occurrences per token = {MIN_OCCURRENCES}")

    all_results = {}

    # --- Voynich Currier B ---
    print("\nLoading Voynich Currier B (H-track, P-placement)...")
    voy_b = load_voynich_tokens('B')
    all_results['Voynich_Currier_B'] = burstiness_for_corpus(voy_b, "Voynich Currier B")

    # --- Voynich Currier A (additional baseline) ---
    print("\nLoading Voynich Currier A...")
    voy_a = load_voynich_tokens('A')
    all_results['Voynich_Currier_A'] = burstiness_for_corpus(voy_a, "Voynich Currier A")

    # --- Codicillus (NL Latin alchemy) ---
    print("\nLoading Codicillus Mercuriorum Latin...")
    cod_path = ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'
    if cod_path.exists():
        cod_tokens = load_text_corpus(cod_path)
        all_results['Codicillus_Latin'] = burstiness_for_corpus(cod_tokens, "Codicillus Latin")
    else:
        print(f"  ⚠ Not found: {cod_path}")

    # --- Mesue (NL Latin pharmacy) ---
    print("\nLoading Mesue Grabadin Latin...")
    mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'
    if mesue_path.exists():
        mesue_tokens = load_text_corpus(mesue_path)
        all_results['Mesue_Latin'] = burstiness_for_corpus(mesue_tokens, "Mesue Grabadin Latin")
    else:
        print(f"  ⚠ Not found: {mesue_path}")

    # --- Brunschwig 1512 (NL German) ---
    print("\nLoading Brunschwig 1512 ENHG...")
    brun_path = ROOT / 'sources' / 'brunschwig_1512' / 'brunschwig_1512_assembled.txt'
    if brun_path.exists():
        brun_tokens = load_text_corpus(brun_path)
        all_results['Brunschwig_1512'] = burstiness_for_corpus(brun_tokens, "Brunschwig 1512")
    else:
        print(f"  ⚠ Not found: {brun_path}")

    # --- Random null: Voynich Currier B shuffled ---
    print("\nComputing random null (Voynich B shuffled)...")
    rng = random.Random(706)
    voy_b_shuffled = list(voy_b)
    rng.shuffle(voy_b_shuffled)
    all_results['Random_Null_Voynich_B_Shuffled'] = burstiness_for_corpus(
        voy_b_shuffled, "Random Null (Voynich B shuffled)"
    )

    # --- Cross-corpus verdict ---
    print("\n" + "=" * 90)
    print("CROSS-CORPUS SUMMARY")
    print("=" * 90)
    print(f"\n{'Corpus':<40}{'N tokens':>12}{'β median':>12}{'verdict':>30}")
    print("-" * 96)
    for label, r in all_results.items():
        if 'error' in r:
            print(f"{label:<40}{'N/A':>12}{'N/A':>12}{r['error']:>30}")
        else:
            print(f"{label:<40}{r['n_tokens']:>12}{r['beta_median']:>12.3f}"
                  f"{r['verdict'].split(' (')[0]:>30}")

    # Sanity checks (per pre-registration)
    print("\n" + "=" * 90)
    print("SANITY CHECKS (per pre-registration)")
    print("=" * 90)
    sanity_pass = True
    if 'Random_Null_Voynich_B_Shuffled' in all_results:
        rn = all_results['Random_Null_Voynich_B_Shuffled']
        if 'beta_median' in rn:
            null_pass = 0.90 < rn['beta_median'] < 1.10
            print(f"  Random null β median = {rn['beta_median']:.3f} "
                  f"(expected ≈ 1.0 ± 0.10): {'PASS' if null_pass else 'FAIL'}")
            sanity_pass = sanity_pass and null_pass

    for label in ['Codicillus_Latin', 'Mesue_Latin', 'Brunschwig_1512']:
        if label in all_results and 'beta_median' in all_results[label]:
            r = all_results[label]
            nl_pass = r['beta_median'] < 0.95
            print(f"  {label} β median = {r['beta_median']:.3f} "
                  f"(expected < 0.95 for NL): {'PASS' if nl_pass else 'FAIL'}")
            sanity_pass = sanity_pass and nl_pass

    print(f"\nSanity floor: {'PASS — interpret Voynich result' if sanity_pass else 'FAIL — methodology issue, DO NOT interpret Voynich'}")

    out = {
        "method": "PHASE_706 burstiness test",
        "pre_registered_thresholds": {
            "NL_LIKE_THRESHOLD": NL_LIKE_THRESHOLD,
            "POISSON_THRESHOLD": POISSON_THRESHOLD,
            "TOP_K": TOP_K,
            "MIN_OCCURRENCES": MIN_OCCURRENCES,
        },
        "results_by_corpus": all_results,
        "sanity_floor_pass": sanity_pass,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

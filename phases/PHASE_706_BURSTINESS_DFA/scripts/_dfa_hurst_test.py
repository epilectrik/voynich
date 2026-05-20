"""
PHASE_706 Test 2: DFA Hurst exponent on token-length time series.

Methodology (standard DFA-2):
  1. For each corpus, build token-length time series (length in characters
     per token, in reading order)
  2. Compute profile: cumulative sum of (x_t − mean)
  3. For scales w in log-spaced range [10, N/4]:
     - Divide profile into non-overlapping windows of size w
     - Fit quadratic polynomial to each window, subtract trend
     - Compute std of detrended residuals
     - F(w) = mean of std across windows
  4. Fit log F(w) ~ H · log(w) → Hurst exponent H

Pre-registered thresholds (LOCKED):
  - H > 0.55 → NL-like persistence
  - 0.45 < H < 0.55 → random/uncorrelated
  - H < 0.45 → anti-persistent (unusual)

Sanity check: random shuffle of any corpus must give H ≈ 0.5
              NL baselines (Codicillus, Mesue, Brunschwig) must give H > 0.55
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

OUT_PATH = ROOT / 'phases' / 'PHASE_706_BURSTINESS_DFA' / 'results' / 'dfa_hurst_results.json'

# Pre-registered thresholds (LOCKED)
NL_LIKE_THRESHOLD = 0.55
RANDOM_LOW = 0.45
RANDOM_HIGH = 0.55
ANTI_PERSISTENT_THRESHOLD = 0.45


def load_voynich_lengths(currier='B'):
    """Load Voynich token-length sequence (H-track, P-placement)."""
    tx = Transcript()
    lengths = []
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != currier:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        lengths.append(len(t.word))
    return np.array(lengths)


def load_text_lengths(path, max_tokens=None):
    """Load token-length sequence from text corpus."""
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    text = text.lower()
    text = re.sub(r'[^a-zäöüß\s]', ' ', text)
    tokens = text.split()
    tokens = [t for t in tokens if len(t) >= 2]
    if max_tokens:
        tokens = tokens[:max_tokens]
    return np.array([len(t) for t in tokens])


def dfa_2(series, scales=None, q=2):
    """Standard DFA with polynomial-q detrending.

    Returns (scales_log, F_log, hurst_H).
    """
    n = len(series)
    if n < 100:
        return None, None, None

    # Default log-spaced scales from 10 to N/4
    if scales is None:
        scales = np.unique(np.logspace(np.log10(10), np.log10(n // 4), 30).astype(int))

    # Profile: cumulative sum of mean-subtracted
    profile = np.cumsum(series - np.mean(series))

    F_vals = []
    valid_scales = []
    for w in scales:
        if w < 4 or w > n // 2:
            continue
        # Forward windows
        n_windows = n // w
        if n_windows < 2:
            continue
        stds = []
        for i in range(n_windows):
            window = profile[i*w:(i+1)*w]
            x = np.arange(w)
            # Fit polynomial of order q, subtract
            try:
                coeffs = np.polyfit(x, window, q)
                trend = np.polyval(coeffs, x)
                residual = window - trend
                stds.append(np.std(residual))
            except (np.linalg.LinAlgError, np.RankWarning):
                continue
        if len(stds) >= 2:
            F_vals.append(np.mean(stds))
            valid_scales.append(w)

    if len(valid_scales) < 5:
        return None, None, None

    log_scales = np.log(valid_scales)
    log_F = np.log(F_vals)
    # Linear fit log F vs log w → slope = Hurst H
    H, intercept = np.polyfit(log_scales, log_F, 1)
    return log_scales, log_F, float(H)


def dfa_for_corpus(series, label):
    """Run DFA and report Hurst H."""
    if series is None or len(series) < 100:
        return {"label": label, "error": f"series too short: {len(series) if series is not None else 0}"}

    print(f"\n  {label}:")
    print(f"    Series length: {len(series)} tokens")
    print(f"    Mean length: {np.mean(series):.2f}, std: {np.std(series):.2f}")

    log_scales, log_F, H = dfa_2(series)
    if H is None:
        return {"label": label, "error": "DFA computation failed"}

    # Apply pre-registered decision
    if H > NL_LIKE_THRESHOLD:
        verdict = f"NL-LIKE (H={H:.3f} > 0.55, persistent long-range correlation)"
    elif H >= ANTI_PERSISTENT_THRESHOLD:
        verdict = f"RANDOM-LIKE (H={H:.3f}, uncorrelated)"
    else:
        verdict = f"ANTI-PERSISTENT (H={H:.3f} < 0.45, anti-correlated — unusual)"

    print(f"    DFA Hurst H: {H:.4f}  →  {verdict.split(' (')[0]}")

    return {
        "label": label,
        "n_tokens": len(series),
        "mean_length": float(np.mean(series)),
        "std_length": float(np.std(series)),
        "hurst_H": H,
        "log_scales": log_scales.tolist() if log_scales is not None else None,
        "log_F": log_F.tolist() if log_F is not None else None,
        "verdict": verdict,
    }


def main():
    print("=" * 90)
    print("PHASE_706 DFA HURST EXPONENT TEST")
    print("=" * 90)
    print(f"\nPre-registered thresholds (LOCKED):")
    print(f"  H > 0.55 → NL-like persistence (long-range correlation)")
    print(f"  0.45 ≤ H ≤ 0.55 → random/uncorrelated")
    print(f"  H < 0.45 → anti-persistent (unusual)")

    all_results = {}

    # --- Voynich Currier B ---
    print("\nLoading Voynich Currier B token-length series...")
    voy_b = load_voynich_lengths('B')
    all_results['Voynich_Currier_B'] = dfa_for_corpus(voy_b, "Voynich Currier B")

    # --- Voynich Currier A ---
    print("\nLoading Voynich Currier A...")
    voy_a = load_voynich_lengths('A')
    all_results['Voynich_Currier_A'] = dfa_for_corpus(voy_a, "Voynich Currier A")

    # --- Codicillus ---
    print("\nLoading Codicillus Latin...")
    cod_path = ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'
    if cod_path.exists():
        cod = load_text_lengths(cod_path)
        all_results['Codicillus_Latin'] = dfa_for_corpus(cod, "Codicillus Latin")

    # --- Mesue ---
    print("\nLoading Mesue Grabadin Latin...")
    mesue_path = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'
    if mesue_path.exists():
        mesue = load_text_lengths(mesue_path)
        all_results['Mesue_Latin'] = dfa_for_corpus(mesue, "Mesue Grabadin Latin")

    # --- Brunschwig ---
    print("\nLoading Brunschwig 1512...")
    brun_path = ROOT / 'sources' / 'brunschwig_1512' / 'brunschwig_1512_assembled.txt'
    if brun_path.exists():
        brun = load_text_lengths(brun_path)
        all_results['Brunschwig_1512'] = dfa_for_corpus(brun, "Brunschwig 1512")

    # --- Random null: shuffled Voynich B ---
    print("\nRandom null (Voynich B token-length shuffled)...")
    rng = np.random.default_rng(706)
    voy_b_shuffled = voy_b.copy()
    rng.shuffle(voy_b_shuffled)
    all_results['Random_Null_Voynich_B_Shuffled'] = dfa_for_corpus(
        voy_b_shuffled, "Random Null (Voynich B shuffled)"
    )

    # --- Cross-corpus summary ---
    print("\n" + "=" * 90)
    print("CROSS-CORPUS SUMMARY")
    print("=" * 90)
    print(f"\n{'Corpus':<40}{'N tokens':>12}{'Hurst H':>12}{'Verdict':>30}")
    print("-" * 96)
    for label, r in all_results.items():
        if 'error' in r:
            print(f"{label:<40}{'N/A':>12}{'N/A':>12}{r['error']:>30}")
        else:
            print(f"{label:<40}{r['n_tokens']:>12}{r['hurst_H']:>12.4f}"
                  f"{r['verdict'].split(' (')[0]:>30}")

    # Sanity checks
    print("\n" + "=" * 90)
    print("SANITY CHECKS")
    print("=" * 90)
    sanity_pass = True
    if 'Random_Null_Voynich_B_Shuffled' in all_results:
        rn = all_results['Random_Null_Voynich_B_Shuffled']
        if 'hurst_H' in rn:
            null_pass = 0.40 < rn['hurst_H'] < 0.60
            print(f"  Random null H = {rn['hurst_H']:.4f} "
                  f"(expected ≈ 0.5 ± 0.10): {'PASS' if null_pass else 'FAIL'}")
            sanity_pass = sanity_pass and null_pass

    for label in ['Codicillus_Latin', 'Mesue_Latin', 'Brunschwig_1512']:
        if label in all_results and 'hurst_H' in all_results[label]:
            r = all_results[label]
            nl_pass = r['hurst_H'] > 0.55
            print(f"  {label} H = {r['hurst_H']:.4f} "
                  f"(expected > 0.55 for NL): {'PASS' if nl_pass else 'FAIL'}")
            sanity_pass = sanity_pass and nl_pass

    print(f"\nSanity floor: {'PASS — interpret Voynich result' if sanity_pass else 'FAIL — methodology issue'}")

    out = {
        "method": "PHASE_706 DFA Hurst exponent test (DFA-2)",
        "pre_registered_thresholds": {
            "NL_LIKE_THRESHOLD": NL_LIKE_THRESHOLD,
            "RANDOM_LOW": RANDOM_LOW,
            "RANDOM_HIGH": RANDOM_HIGH,
            "ANTI_PERSISTENT_THRESHOLD": ANTI_PERSISTENT_THRESHOLD,
        },
        "results_by_corpus": all_results,
        "sanity_floor_pass": sanity_pass,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

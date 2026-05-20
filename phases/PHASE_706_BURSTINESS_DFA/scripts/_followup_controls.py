"""
PHASE_706 follow-up controls — required before registering C2042/C2043.

Both experts independently flagged two missing controls:

1. WITHIN-FOLIO SHUFFLE NULL: shuffle tokens within each folio (preserving
   folio membership and folio length). If β collapses toward 1.0 and H
   toward 0.5 under this null, the original signal was folio-scoped
   (recipe-burst, content-driven). If β/H survive within-folio shuffle,
   the signal is sub-folio sequential clustering (more NL-like, needs
   harder thought).

2. FLOOR-VS-DISCRIMINATOR via mensural notation: do β and H discriminate
   NL from non-NL-structured-symbolic systems? Mensural notation has
   topical structure (motet-by-motet vocabulary bursts) but is not NL.
   If mensural also gives β<0.85 and H>0.55, the metrics are FLOORS
   (any structured-symbolic system passes), not DISCRIMINATORS (only NL
   passes).

These controls discriminate the experts' two readings:
- Reading A (orthogonal axes, content-driven): within-folio shuffle should
  DESTROY β/H signal; mensural should also pass (because content-driven)
- Reading B (substrate over-claimed): within-folio shuffle should PRESERVE
  β/H signal; mensural should FAIL (β/H actually discriminate NL)
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

OUT_PATH = ROOT / 'phases' / 'PHASE_706_BURSTINESS_DFA' / 'results' / 'followup_controls.json'

TOP_K = 50
MIN_OCCURRENCES = 20
N_SHUFFLE_REPS = 20  # per-shuffle iterations to estimate null mean/std


def load_voynich_tokens_with_folio(currier='B'):
    """Load Voynich (token_string, folio) pairs in reading order."""
    tx = Transcript()
    tokens = []
    folios = []
    for t in tx.all(h_only=True):
        if not t.word.strip() or '*' in t.word:
            continue
        if t.language != currier:
            continue
        if not (t.placement and t.placement.startswith('P')):
            continue
        tokens.append(t.word.lower())
        folios.append(t.folio)
    return tokens, folios


def load_mensural_tokens():
    """Load mensural duration-class tokens (the same data used in C2032
    cross-corpus testing)."""
    streams_path = ROOT / 'phases' / 'MENSURAL_NOTATION_HYPOTHESIS' / 'results' / 'mensural_streams.json'
    if not streams_path.exists():
        return None
    d = json.loads(streams_path.read_text(encoding='utf-8'))
    per_motet = d.get('per_motet', {})
    # Flatten all motets, all voices, into one token sequence
    tokens = []
    for motet_id, voices in per_motet.items():
        for vid, voice in voices.items():
            for tok in voice.get('dur', []):
                if not tok.endswith('R'):  # drop rests, same as C2032
                    tokens.append(tok)
    return tokens


def compute_inter_arrival(token_seq, target):
    positions = [i for i, t in enumerate(token_seq) if t == target]
    if len(positions) < 2:
        return None
    return np.diff(positions)


def fit_weibull_beta(intervals):
    if intervals is None or len(intervals) < 5:
        return None
    try:
        shape, _, _ = stats.weibull_min.fit(intervals, floc=0)
        return float(shape)
    except Exception:
        return None


def burstiness_median(tokens, top_k=TOP_K, min_occ=MIN_OCCURRENCES):
    """Compute β median across top-K frequent tokens."""
    freq = Counter(tokens)
    targets = [t for t, c in freq.most_common() if c >= min_occ][:top_k]
    betas = []
    for tok in targets:
        intervals = compute_inter_arrival(tokens, tok)
        beta = fit_weibull_beta(intervals)
        if beta is not None:
            betas.append(beta)
    if not betas:
        return None, 0
    return float(np.median(betas)), len(betas)


def dfa_hurst(series, q=2):
    n = len(series)
    if n < 100:
        return None
    scales = np.unique(np.logspace(np.log10(10), np.log10(n // 4), 30).astype(int))
    profile = np.cumsum(series - np.mean(series))
    F_vals = []
    valid_scales = []
    for w in scales:
        if w < 4 or w > n // 2:
            continue
        n_windows = n // w
        if n_windows < 2:
            continue
        stds = []
        for i in range(n_windows):
            window = profile[i*w:(i+1)*w]
            x = np.arange(w)
            try:
                coeffs = np.polyfit(x, window, q)
                trend = np.polyval(coeffs, x)
                stds.append(np.std(window - trend))
            except Exception:
                continue
        if len(stds) >= 2:
            F_vals.append(np.mean(stds))
            valid_scales.append(w)
    if len(valid_scales) < 5:
        return None
    H, _ = np.polyfit(np.log(valid_scales), np.log(F_vals), 1)
    return float(H)


def within_folio_shuffle(tokens, folios, rng):
    """Shuffle token order WITHIN each folio (preserve folio membership)."""
    folio_to_indices = defaultdict(list)
    for i, f in enumerate(folios):
        folio_to_indices[f].append(i)
    new_tokens = list(tokens)
    for f, idx_list in folio_to_indices.items():
        # Get tokens for this folio, shuffle them, put back at same indices
        these_tokens = [tokens[i] for i in idx_list]
        rng.shuffle(these_tokens)
        for k, i in enumerate(idx_list):
            new_tokens[i] = these_tokens[k]
    return new_tokens


def main():
    print("=" * 90)
    print("PHASE_706 FOLLOW-UP CONTROLS")
    print("=" * 90)

    # ---- 1. Load data ----
    print("\nLoading Voynich Currier B...")
    voy_tokens, voy_folios = load_voynich_tokens_with_folio('B')
    print(f"  {len(voy_tokens)} tokens across {len(set(voy_folios))} folios")

    print("\nLoading mensural notation tokens (from MENSURAL_NOTATION_HYPOTHESIS)...")
    mensural_tokens = load_mensural_tokens()
    if mensural_tokens:
        print(f"  {len(mensural_tokens)} mensural duration tokens")

    # ---- 2. Original Voynich β and H (baseline for shuffle comparison) ----
    print("\n--- Original Voynich Currier B ---")
    voy_beta, n_fits = burstiness_median(voy_tokens)
    voy_lengths = np.array([len(t) for t in voy_tokens])
    voy_hurst = dfa_hurst(voy_lengths)
    print(f"  Original β = {voy_beta:.3f} (n fits = {n_fits})")
    print(f"  Original H = {voy_hurst:.4f}")

    # ---- 3. Within-folio shuffle null (CRITICAL CONTROL) ----
    print(f"\n--- Within-folio shuffle null ({N_SHUFFLE_REPS} reps) ---")
    null_betas = []
    null_hursts = []
    rng = random.Random(706706)
    rng_np = np.random.default_rng(706706)
    for rep in range(N_SHUFFLE_REPS):
        shuffled = within_folio_shuffle(voy_tokens, voy_folios, rng)
        # Burstiness on shuffled
        b, _ = burstiness_median(shuffled)
        if b is not None:
            null_betas.append(b)
        # DFA on shuffled
        shuffled_lengths = np.array([len(t) for t in shuffled])
        h = dfa_hurst(shuffled_lengths)
        if h is not None:
            null_hursts.append(h)
        if (rep + 1) % 5 == 0:
            print(f"    rep {rep+1}/{N_SHUFFLE_REPS}: β={b:.3f}, H={h:.3f}")

    null_beta_mean = float(np.mean(null_betas)) if null_betas else None
    null_beta_std = float(np.std(null_betas)) if null_betas else None
    null_hurst_mean = float(np.mean(null_hursts)) if null_hursts else None
    null_hurst_std = float(np.std(null_hursts)) if null_hursts else None

    print(f"\n  Within-folio shuffle null β: mean={null_beta_mean:.3f}, std={null_beta_std:.4f}")
    print(f"  Within-folio shuffle null H: mean={null_hurst_mean:.4f}, std={null_hurst_std:.4f}")
    print(f"\n  Original β = {voy_beta:.3f}")
    print(f"  Within-folio shuffle β = {null_beta_mean:.3f} ± {null_beta_std:.3f}")
    print(f"  Delta β: {voy_beta - null_beta_mean:+.4f}")
    print(f"  Original H = {voy_hurst:.4f}")
    print(f"  Within-folio shuffle H = {null_hurst_mean:.4f} ± {null_hurst_std:.4f}")
    print(f"  Delta H: {voy_hurst - null_hurst_mean:+.4f}")

    # Interpretation
    print("\n--- Within-folio shuffle interpretation ---")
    beta_collapsed = null_beta_mean is not None and null_beta_mean > 0.95
    hurst_collapsed = null_hurst_mean is not None and null_hurst_mean < 0.55
    if beta_collapsed and hurst_collapsed:
        wf_verdict = ("RECIPE-BURST CONFIRMED — β collapsed to >0.95 and H collapsed to <0.55 "
                      "under within-folio shuffle. Original signal was folio-scoped "
                      "(content-driven). Reading A (orthogonal axes) confirmed.")
    elif beta_collapsed or hurst_collapsed:
        wf_verdict = ("PARTIAL collapse — one metric collapsed under shuffle, one didn't. "
                      "Mixed signal; needs deeper thought.")
    else:
        wf_verdict = ("SUB-FOLIO STRUCTURAL — β and H survived within-folio shuffle. "
                      "Signal is sub-folio sequential clustering, more NL-like at micro-level. "
                      "Substrate quintet framing needs sharper re-examination.")
    print(f"\n  {wf_verdict}")

    # ---- 4. Mensural notation (floor-vs-discriminator) ----
    print(f"\n--- Mensural notation (floor-vs-discriminator) ---")
    if mensural_tokens:
        mens_beta, mens_n_fits = burstiness_median(mensural_tokens)
        mens_lengths = np.array([len(t) for t in mensural_tokens])
        mens_hurst = dfa_hurst(mens_lengths)
        print(f"  Mensural β = {mens_beta:.3f} (n fits = {mens_n_fits})")
        print(f"  Mensural H = {mens_hurst:.4f}")

        mens_beta_nl = mens_beta < 0.85
        mens_hurst_nl = mens_hurst > 0.55
        if mens_beta_nl and mens_hurst_nl:
            floor_verdict = ("FLOORS confirmed — mensural notation (non-NL structured symbolic) "
                             f"also gives β={mens_beta:.3f} <0.85 AND H={mens_hurst:.4f} >0.55. "
                             "β/H are 'structured-vs-random' metrics, NOT NL discriminators. "
                             "Voynich passing these is 'Voynich is structured,' not 'Voynich is NL.'")
        elif mens_beta_nl != mens_hurst_nl:
            floor_verdict = ("MIXED — one metric is floor (mensural passes), other is discriminator. "
                             "Need to specify which is which when registering.")
        else:
            floor_verdict = (f"DISCRIMINATORS confirmed — mensural β={mens_beta:.3f}, H={mens_hurst:.4f} "
                             "outside NL range. Voynich passing both is genuinely NL-like signal.")
        print(f"\n  {floor_verdict}")
    else:
        floor_verdict = "Mensural data not available"
        mens_beta = None
        mens_hurst = None
        print(f"  {floor_verdict}")

    # ---- 5. Combined verdict ----
    print("\n" + "=" * 90)
    print("COMBINED VERDICT")
    print("=" * 90)

    if beta_collapsed and hurst_collapsed:
        combined = ("READING A CONFIRMED — Voynich β/H come from folio-scoped content "
                    "deployment. Substrate quintet (sequential-grammar) and PHASE_706 (content-"
                    "deployment) measure orthogonal layers. Register C2042/C2043 as 'NL-like "
                    "content-deployment statistics' with explicit dual-layer framing.")
    else:
        combined = ("Within-folio shuffle did NOT fully collapse the signal. Original β/H "
                    "may include sub-folio sequential structure that's more NL-like than the "
                    "substrate quintet predicted. Registration framing needs sharper thought.")
    print(f"\n  {combined}")
    print(f"\n  Floor-vs-discriminator: {floor_verdict.split(' (')[0]}")

    out = {
        "method": "PHASE_706 follow-up controls — within-folio shuffle + mensural floor test",
        "voynich_b_original": {
            "beta_median": voy_beta,
            "hurst_H": voy_hurst,
        },
        "within_folio_shuffle_null": {
            "n_reps": N_SHUFFLE_REPS,
            "beta_mean": null_beta_mean,
            "beta_std": null_beta_std,
            "hurst_mean": null_hurst_mean,
            "hurst_std": null_hurst_std,
            "delta_beta_voynich_minus_null": (voy_beta - null_beta_mean) if voy_beta and null_beta_mean else None,
            "delta_hurst_voynich_minus_null": (voy_hurst - null_hurst_mean) if voy_hurst and null_hurst_mean else None,
            "interpretation": wf_verdict,
        },
        "mensural_floor_test": {
            "n_tokens": len(mensural_tokens) if mensural_tokens else 0,
            "beta_median": mens_beta,
            "hurst_H": mens_hurst,
            "interpretation": floor_verdict,
        },
        "combined_verdict": combined,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

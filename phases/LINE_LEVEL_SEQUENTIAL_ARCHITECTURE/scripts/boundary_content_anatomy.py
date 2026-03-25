"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 4: Boundary Content Anatomy

Decomposes C1729 boundary enrichment into specific feature channels.
Tests specification-closure asymmetry at first/last body lines.

Questions answered:
  1. Which of 18 feature channels drive first-line distinctiveness?
  2. Which channels drive last-line distinctiveness?
  3. Are first and last boundaries distinctive in the SAME or DIFFERENT ways?
  4. Does header echo (C1786) confound first-line results?
"""
import json
import math
import sys
import random
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, extract_line_features, compute_folio_prefix_dists,
    CHANNEL_NAMES, RESULTS_DIR, round_floats,
)

MIN_BODY_LINES = 7
BONFERRONI_TESTS = 36  # 18 channels x 2 boundaries
ALPHA = 0.05
CORRECTED_ALPHA = ALPHA / BONFERRONI_TESTS  # ~0.00139
N_BOOTSTRAP = 1000
RNG = random.Random(42)


# ============================================================
# Helpers
# ============================================================

def compute_cosine(a, b):
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def manual_ttest_1samp(diffs):
    """
    One-sample t-test on diffs (testing H0: mean = 0).
    Returns t-statistic and two-tailed p-value (normal approx for large n).
    """
    n = len(diffs)
    if n < 3:
        return 0.0, 1.0
    mean_d = sum(diffs) / n
    var_d = sum((d - mean_d) ** 2 for d in diffs) / (n - 1)
    std_d = var_d ** 0.5
    if std_d == 0:
        return 0.0, 1.0
    t_stat = mean_d / (std_d / n ** 0.5)
    # Normal approximation for p-value (valid for n > ~30)
    # Using complementary error function approximation
    p_value = 2.0 * _norm_sf(abs(t_stat))
    return t_stat, p_value


def _norm_sf(z):
    """Survival function of standard normal (1 - CDF), using rational approx."""
    # Abramowitz & Stegun 26.2.17 approximation
    if z < 0:
        return 1.0 - _norm_sf(-z)
    p = 0.2316419
    b1 = 0.319381530
    b2 = -0.356563782
    b3 = 1.781477937
    b4 = -1.821255978
    b5 = 1.330274429
    t = 1.0 / (1.0 + p * z)
    phi = math.exp(-z * z / 2.0) / (2.0 * math.pi) ** 0.5
    return phi * (b1 * t + b2 * t ** 2 + b3 * t ** 3 + b4 * t ** 4 + b5 * t ** 5)


def compute_jsd(p_dist, q_dist):
    """Jensen-Shannon divergence between two distributions (dicts)."""
    all_keys = set(list(p_dist.keys()) + list(q_dist.keys()))
    jsd = 0.0
    for k in all_keys:
        p = p_dist.get(k, 0.0)
        q = q_dist.get(k, 0.0)
        m = (p + q) / 2
        if p > 0 and m > 0:
            jsd += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            jsd += 0.5 * q * math.log2(q / m)
    return jsd


def mean_features(feature_dicts):
    """Compute element-wise mean of a list of feature dicts."""
    if not feature_dicts:
        return {ch: 0.0 for ch in CHANNEL_NAMES}
    result = {}
    for ch in CHANNEL_NAMES:
        vals = [fd[ch] for fd in feature_dicts if ch in fd]
        result[ch] = sum(vals) / len(vals) if vals else 0.0
    return result


# ============================================================
# Block 1: Extract boundary and interior features
# ============================================================

def extract_boundary_data(corpus, folio_prefix_dists):
    """
    For each paragraph with 7+ body lines, extract feature vectors for:
      - first body line
      - last body line
      - interior mean (body_lines[1:-1])

    Returns list of dicts, one per qualifying paragraph.
    """
    records = []

    for folio, fdata in sorted(corpus.items()):
        pfx_dist = folio_prefix_dists.get(folio, {})
        for para in fdata['paragraphs']:
            body = para['body_lines']
            if len(body) < MIN_BODY_LINES:
                continue

            first_feats = extract_line_features(body[0], pfx_dist)
            last_feats = extract_line_features(body[-1], pfx_dist)
            interior_lines = body[1:-1]
            interior_feat_list = [extract_line_features(ln, pfx_dist) for ln in interior_lines]
            interior_mean = mean_features(interior_feat_list)

            # Also extract header features for echo control
            header_feats = None
            if para['header_lines']:
                header_feats = extract_line_features(para['header_lines'][0], pfx_dist)

            records.append({
                'folio': folio,
                'para_id': para['id'],
                'first_feats': first_feats,
                'last_feats': last_feats,
                'interior_mean': interior_mean,
                'header_feats': header_feats,
                'n_interior': len(interior_lines),
            })

    return records


# ============================================================
# Block 2: Per-feature divergence tests
# ============================================================

def per_feature_divergence(records):
    """
    For each of 18 channels, compute:
      - Signed divergence: boundary_value - interior_mean (across paragraphs)
      - One-sample t-test on the divergences
      - Mean absolute divergence

    Returns first_divergence and last_divergence dicts.
    """
    first_div = {}
    last_div = {}

    for ch in CHANNEL_NAMES:
        # Compute per-paragraph diffs
        first_diffs = []
        last_diffs = []

        for rec in records:
            f_val = rec['first_feats'].get(ch, 0.0)
            l_val = rec['last_feats'].get(ch, 0.0)
            i_val = rec['interior_mean'].get(ch, 0.0)
            first_diffs.append(f_val - i_val)
            last_diffs.append(l_val - i_val)

        # First line
        mean_signed_f = sum(first_diffs) / len(first_diffs)
        mean_abs_f = sum(abs(d) for d in first_diffs) / len(first_diffs)
        t_stat_f, p_val_f = manual_ttest_1samp(first_diffs)
        significant_f = p_val_f < CORRECTED_ALPHA

        first_div[ch] = {
            'mean_signed': mean_signed_f,
            'mean_abs': mean_abs_f,
            't_stat': t_stat_f,
            'p_value': p_val_f,
            'significant': significant_f,
            'direction': 'ABOVE' if mean_signed_f > 0 else 'BELOW',
        }

        # Last line
        mean_signed_l = sum(last_diffs) / len(last_diffs)
        mean_abs_l = sum(abs(d) for d in last_diffs) / len(last_diffs)
        t_stat_l, p_val_l = manual_ttest_1samp(last_diffs)
        significant_l = p_val_l < CORRECTED_ALPHA

        last_div[ch] = {
            'mean_signed': mean_signed_l,
            'mean_abs': mean_abs_l,
            't_stat': t_stat_l,
            'p_value': p_val_l,
            'significant': significant_l,
            'direction': 'ABOVE' if mean_signed_l > 0 else 'BELOW',
        }

    return first_div, last_div


# ============================================================
# Block 3: Cosine similarity of divergence vectors + bootstrap CI
# ============================================================

def cosine_analysis(records):
    """
    Compute cosine similarity between first-line and last-line signed
    divergence vectors (18-dim). Bootstrap CI by resampling paragraphs.
    """
    n = len(records)

    def divergence_vectors(recs):
        """Compute 18-dim signed mean divergence vectors for first and last."""
        first_vec = []
        last_vec = []
        for ch in CHANNEL_NAMES:
            f_diffs = [r['first_feats'].get(ch, 0.0) - r['interior_mean'].get(ch, 0.0)
                       for r in recs]
            l_diffs = [r['last_feats'].get(ch, 0.0) - r['interior_mean'].get(ch, 0.0)
                       for r in recs]
            first_vec.append(sum(f_diffs) / len(f_diffs))
            last_vec.append(sum(l_diffs) / len(l_diffs))
        return first_vec, last_vec

    first_vec, last_vec = divergence_vectors(records)
    observed_cos = compute_cosine(first_vec, last_vec)

    # Bootstrap CI
    boot_cos = []
    for _ in range(N_BOOTSTRAP):
        sample = [records[RNG.randint(0, n - 1)] for _ in range(n)]
        fv, lv = divergence_vectors(sample)
        boot_cos.append(compute_cosine(fv, lv))

    boot_cos.sort()
    ci_lo = boot_cos[int(0.025 * N_BOOTSTRAP)]
    ci_hi = boot_cos[int(0.975 * N_BOOTSTRAP)]

    return observed_cos, [ci_lo, ci_hi], first_vec, last_vec


# ============================================================
# Block 4: Header echo control (C1786)
# ============================================================

def header_echo_control(records):
    """
    Compare first body line divergence with and without paragraphs where
    header and first body line share high feature overlap (JSD < 0.1).

    C1786 says header marking echoes into body. If removing echo-heavy
    paragraphs changes the first-line divergence pattern, header echo
    is a confound.
    """
    echo_threshold = 0.1

    # For each paragraph with header, compute feature-space overlap
    # between header and first body line
    echo_flags = []
    for rec in records:
        if rec['header_feats'] is None:
            echo_flags.append(False)
            continue

        # Compute a simple distance: mean abs diff across channels
        diffs = []
        for ch in CHANNEL_NAMES:
            h_val = rec['header_feats'].get(ch, 0.0)
            f_val = rec['first_feats'].get(ch, 0.0)
            # Normalize by channel scale: use interior mean as reference
            i_val = rec['interior_mean'].get(ch, 0.0)
            scale = max(abs(i_val), 0.01)
            diffs.append(abs(h_val - f_val) / scale)

        mean_diff = sum(diffs) / len(diffs)
        # Low mean_diff = high overlap = echo
        echo_flags.append(mean_diff < echo_threshold)

    n_echo = sum(echo_flags)
    n_no_echo = len(echo_flags) - n_echo

    # Compute first-line divergence WITHOUT echo paragraphs
    filtered_records = [r for r, is_echo in zip(records, echo_flags) if not is_echo]

    if len(filtered_records) < 10:
        return {
            'n_echo_paragraphs': n_echo,
            'n_non_echo_paragraphs': n_no_echo,
            'sufficient_data': False,
            'conclusion': 'INSUFFICIENT_DATA',
        }

    first_div_full, _ = per_feature_divergence(records)
    first_div_filtered, _ = per_feature_divergence(filtered_records)

    # Compare: how many channels change significance?
    sig_changes = 0
    channel_comparison = {}
    for ch in CHANNEL_NAMES:
        full_sig = first_div_full[ch]['significant']
        filt_sig = first_div_filtered[ch]['significant']
        changed = full_sig != filt_sig
        if changed:
            sig_changes += 1
        channel_comparison[ch] = {
            'full_significant': full_sig,
            'filtered_significant': filt_sig,
            'changed': changed,
            'full_p': first_div_full[ch]['p_value'],
            'filtered_p': first_div_filtered[ch]['p_value'],
        }

    # If many channels change, header echo is a confound
    confound_fraction = sig_changes / len(CHANNEL_NAMES)

    return {
        'n_echo_paragraphs': n_echo,
        'n_non_echo_paragraphs': n_no_echo,
        'sufficient_data': True,
        'n_significance_changes': sig_changes,
        'confound_fraction': confound_fraction,
        'channel_comparison': channel_comparison,
        'conclusion': 'HEADER_ECHO_CONFOUND' if confound_fraction > 0.25 else 'ECHO_CONTROLLED',
    }


# ============================================================
# Block 5: Verdict
# ============================================================

def determine_verdict(cosine_sim, ci_lo, ci_hi, first_div, last_div):
    """
    Determine boundary relationship:
      - ORTHOGONAL_BOUNDARIES: cosine ~ 0 (CI spans 0, |cos| < 0.3)
      - PARALLEL_BOUNDARIES: cosine ~ 1 (CI above 0.5)
      - ASYMMETRIC_BOUNDARIES: intermediate or anti-correlated
    """
    # Count significant channels per boundary
    first_sig = [ch for ch in CHANNEL_NAMES if first_div[ch]['significant']]
    last_sig = [ch for ch in CHANNEL_NAMES if last_div[ch]['significant']]

    if ci_lo > 0.5:
        verdict = 'PARALLEL_BOUNDARIES'
    elif ci_hi < -0.3:
        verdict = 'ANTI_PARALLEL_BOUNDARIES'
    elif abs(cosine_sim) < 0.3 and ci_lo < 0.0 < ci_hi:
        verdict = 'ORTHOGONAL_BOUNDARIES'
    else:
        verdict = 'ASYMMETRIC_BOUNDARIES'

    return verdict, first_sig, last_sig


# ============================================================
# Main
# ============================================================

def main():
    print("Building corpus...")
    corpus = build_corpus()
    folio_prefix_dists = compute_folio_prefix_dists(corpus)

    # Count paragraphs and folios
    total_paras = sum(len(fdata['paragraphs']) for fdata in corpus.values())
    print(f"  Total folios: {len(corpus)}, paragraphs: {total_paras}")

    # Block 1: Extract boundary data
    print("Extracting boundary and interior features...")
    records = extract_boundary_data(corpus, folio_prefix_dists)
    print(f"  Paragraphs with {MIN_BODY_LINES}+ body lines: {len(records)}")

    if len(records) < 15:
        print("ERROR: Insufficient paragraphs for analysis.")
        sys.exit(1)

    # Block 2: Per-feature divergence tests
    print("Computing per-feature divergence tests...")
    first_div, last_div = per_feature_divergence(records)

    first_sig_count = sum(1 for ch in CHANNEL_NAMES if first_div[ch]['significant'])
    last_sig_count = sum(1 for ch in CHANNEL_NAMES if last_div[ch]['significant'])
    print(f"  First line: {first_sig_count}/18 channels significant (Bonferroni alpha={CORRECTED_ALPHA:.5f})")
    print(f"  Last line:  {last_sig_count}/18 channels significant")

    # Block 3: Cosine similarity
    print("Computing cosine similarity of divergence vectors...")
    cosine_sim, cosine_ci, first_vec, last_vec = cosine_analysis(records)
    print(f"  Cosine similarity: {cosine_sim:.4f}  CI: [{cosine_ci[0]:.4f}, {cosine_ci[1]:.4f}]")

    # Block 4: Header echo control
    print("Running header echo control (C1786)...")
    echo_result = header_echo_control(records)
    print(f"  Echo paragraphs: {echo_result['n_echo_paragraphs']}, "
          f"non-echo: {echo_result['n_non_echo_paragraphs']}")
    print(f"  Echo control conclusion: {echo_result['conclusion']}")

    # Block 5: Verdict
    verdict, first_enriched, last_enriched = determine_verdict(
        cosine_sim, cosine_ci[0], cosine_ci[1], first_div, last_div
    )
    print(f"\n  VERDICT: {verdict}")
    print(f"  First-line enriched channels: {first_enriched}")
    print(f"  Last-line enriched channels:  {last_enriched}")

    # Assemble signed direction summary
    first_directions = {ch: first_div[ch]['direction'] for ch in CHANNEL_NAMES
                        if first_div[ch]['significant']}
    last_directions = {ch: last_div[ch]['direction'] for ch in CHANNEL_NAMES
                       if last_div[ch]['significant']}

    # Predictions based on verdict
    predictions = {}
    if verdict == 'ORTHOGONAL_BOUNDARIES':
        predictions = {
            'P1': 'First and last body lines serve different structural roles',
            'P2': 'First line carries specification/initialization signals',
            'P3': 'Last line carries closure/termination signals',
            'P4': 'Interior lines form a distinct operational core',
        }
    elif verdict == 'PARALLEL_BOUNDARIES':
        predictions = {
            'P1': 'Boundary lines share a common enrichment pattern vs interior',
            'P2': 'Boundaries may serve a shared framing/demarcation function',
            'P3': 'The enrichment is positional (boundary) not functional (start vs end)',
        }
    elif verdict == 'ASYMMETRIC_BOUNDARIES':
        predictions = {
            'P1': 'First and last lines partially overlap in enrichment but differ in emphasis',
            'P2': 'Some channels mark generic boundary effects, others are position-specific',
            'P3': 'The paragraph has graded structure: opening -> core -> closing',
        }
    else:  # ANTI_PARALLEL
        predictions = {
            'P1': 'First and last lines show opposite enrichment patterns',
            'P2': 'What is enriched at start is depleted at end, and vice versa',
            'P3': 'Strong directional architecture: specification -> operation -> closure',
        }

    # Build output
    result = {
        'phase': 623,
        'name': 'boundary_content_anatomy',
        'n_paragraphs': len(records),
        'min_body_lines': MIN_BODY_LINES,
        'bonferroni_alpha': CORRECTED_ALPHA,
        'n_bootstrap': N_BOOTSTRAP,
        'first_line_divergence': round_floats(first_div),
        'last_line_divergence': round_floats(last_div),
        'first_signed_directions': first_directions,
        'last_signed_directions': last_directions,
        'cosine_similarity': round(cosine_sim, 6),
        'cosine_bootstrap_ci': [round(cosine_ci[0], 6), round(cosine_ci[1], 6)],
        'first_enriched_channels': first_enriched,
        'last_enriched_channels': last_enriched,
        'header_echo_control': round_floats(echo_result),
        'verdict': verdict,
        'predictions': predictions,
    }

    result = round_floats(result)

    out_path = RESULTS_DIR / 'boundary_content_anatomy.json'
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults written to {out_path}")
    return result


if __name__ == '__main__':
    main()

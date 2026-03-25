"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 1: Sequential Channel Census

18-channel lag-1 MI census measuring sequential information between consecutive
body lines within paragraphs. Tests whether line ordering carries structured
information beyond what paragraph membership alone provides.

Blocks:
  1. Extract consecutive line pairs (body-body + cross-paragraph)
  2. Channel-by-channel MI census with paragraph-shuffled null
  3. Ablation decomposition (smoothness degradation per channel)
  4. Transfer entropy (top 5 channels, forward vs backward)
  5. Safety alternation (ey/ii cross-MI)
  6. Context partitioning (body-body vs cross-paragraph)
  7. Verdict

Extends C1727/C1728. Produces: sequential_channel_census.json
"""

import json
import math
import random
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, extract_line_features, compute_folio_prefix_dists,
    compute_mi, compute_binned_conditional_mi, compute_transfer_entropy,
    permutation_test_mi, CHANNEL_NAMES, N_PERM, RNG, RESULTS_DIR, round_floats,
)

# Constants
N_CHANNELS = 18
BONFERRONI_ALPHA = 0.05 / N_CHANNELS
MIN_BODY_LINES = 5
MI_EFFECT_FLOOR = 0.01  # bits


# ============================================================
# Block 1: Extract consecutive line pairs
# ============================================================

def extract_pairs(corpus, prefix_dists):
    """
    Returns list of dicts:
      {feat_n: dict, feat_n1: dict, folio: str, para_id: str, context_type: str}

    body_body: consecutive body lines within the same paragraph
    cross_paragraph: last body line of para N -> first body line of para N+1 (same folio)
    """
    pairs = []

    for folio, fdata in sorted(corpus.items()):
        pfx_dist = prefix_dists.get(folio, {})
        paras = fdata['paragraphs']

        # Track last body line features per paragraph for cross-paragraph pairs
        prev_last_body_feat = None
        prev_para_id = None

        for para in paras:
            body = para['body_lines']
            if len(body) < MIN_BODY_LINES:
                # Still compute features for cross-paragraph pairing
                if body:
                    first_feat = extract_line_features(body[0], pfx_dist)
                    last_feat = extract_line_features(body[-1], pfx_dist)
                    # Cross-paragraph pair
                    if prev_last_body_feat and first_feat:
                        pairs.append({
                            'feat_n': prev_last_body_feat,
                            'feat_n1': first_feat,
                            'folio': folio,
                            'para_id': f'{prev_para_id}->{para["id"]}',
                            'context_type': 'cross_paragraph',
                        })
                    prev_last_body_feat = last_feat if last_feat else None
                    prev_para_id = para['id']
                else:
                    prev_last_body_feat = None
                    prev_para_id = para['id']
                continue

            # Extract features for all body lines
            body_feats = []
            for line_dict in body:
                feat = extract_line_features(line_dict, pfx_dist)
                if feat:
                    body_feats.append((feat, line_dict))
                else:
                    body_feats.append((None, line_dict))

            # Create body-body consecutive pairs
            for i in range(len(body_feats) - 1):
                f_n, _ = body_feats[i]
                f_n1, _ = body_feats[i + 1]
                if f_n and f_n1:
                    pairs.append({
                        'feat_n': f_n,
                        'feat_n1': f_n1,
                        'folio': folio,
                        'para_id': para['id'],
                        'context_type': 'body_body',
                    })

            # Cross-paragraph pair: previous last -> current first
            first_feat = body_feats[0][0] if body_feats else None
            last_feat = body_feats[-1][0] if body_feats else None

            if prev_last_body_feat and first_feat:
                pairs.append({
                    'feat_n': prev_last_body_feat,
                    'feat_n1': first_feat,
                    'folio': folio,
                    'para_id': f'{prev_para_id}->{para["id"]}',
                    'context_type': 'cross_paragraph',
                })

            prev_last_body_feat = last_feat
            prev_para_id = para['id']

    return pairs


# ============================================================
# Block 2: Channel-by-channel MI census
# ============================================================

def _paragraph_shuffled_null(pairs_bb, channel, n_perm, rng):
    """
    Paragraph-shuffled null: shuffle line order WITHIN each paragraph,
    re-extract consecutive pairs, recompute MI for the given channel.

    This preserves paragraph composition while destroying sequential structure.
    """
    # Group body-body pairs by (folio, para_id)
    # We need the original line-level features grouped by paragraph
    para_groups = defaultdict(list)
    for p in pairs_bb:
        key = (p['folio'], p['para_id'])
        para_groups[key].append(p)

    # Reconstruct per-paragraph line sequences
    # For N consecutive pairs within a paragraph, there are N+1 lines
    para_line_sequences = {}
    for key, group_pairs in para_groups.items():
        # Sort by appearance order (they're already in order from extract_pairs)
        line_feats = [group_pairs[0]['feat_n']]
        for gp in group_pairs:
            line_feats.append(gp['feat_n1'])
        para_line_sequences[key] = line_feats

    observed_x = [p['feat_n'][channel] for p in pairs_bb]
    observed_y = [p['feat_n1'][channel] for p in pairs_bb]
    observed_mi = compute_mi(observed_x, observed_y)

    null_values = []
    for _ in range(n_perm):
        shuffled_x = []
        shuffled_y = []
        for key, line_feats in para_line_sequences.items():
            # Shuffle line order within this paragraph
            shuffled = list(line_feats)
            rng.shuffle(shuffled)
            # Re-extract consecutive pairs from shuffled order
            for i in range(len(shuffled) - 1):
                shuffled_x.append(shuffled[i][channel])
                shuffled_y.append(shuffled[i + 1][channel])

        null_mi = compute_mi(shuffled_x, shuffled_y)
        null_values.append(null_mi)

    null_mean = sum(null_values) / len(null_values) if null_values else 0.0
    null_std = (sum((v - null_mean) ** 2 for v in null_values) / len(null_values)) ** 0.5 if null_values else 0.0

    z_score = (observed_mi - null_mean) / null_std if null_std > 1e-12 else 0.0
    p_value = sum(1 for v in null_values if v >= observed_mi) / len(null_values) if null_values else 1.0

    return {
        'observed_mi': observed_mi,
        'null_mean': null_mean,
        'null_std': null_std,
        'z_score': z_score,
        'p_value': p_value,
    }


def run_channel_census(pairs):
    """
    For each of 18 channels: lag-1 MI, paragraph-shuffled null,
    z-score, p-value, partial MI (length-controlled), significance.
    """
    # Filter to body-body only for main census
    pairs_bb = [p for p in pairs if p['context_type'] == 'body_body']

    if len(pairs_bb) < 20:
        print('  WARNING: Too few body-body pairs for census')
        return {}

    print(f'  Body-body pairs for census: {len(pairs_bb)}')

    results = {}
    for ch_idx, channel in enumerate(CHANNEL_NAMES):
        t_ch = time.time()

        # Paragraph-shuffled null
        res = _paragraph_shuffled_null(pairs_bb, channel, N_PERM, RNG)

        # Partial MI controlling for line length
        partial_mi = None
        if channel != 'length':
            x = [p['feat_n'][channel] for p in pairs_bb]
            y = [p['feat_n1'][channel] for p in pairs_bb]
            condition = [p['feat_n']['length'] for p in pairs_bb]
            partial_mi = compute_binned_conditional_mi(x, y, condition)

        significant = (res['z_score'] > 3.0 and res['observed_mi'] > MI_EFFECT_FLOOR)

        results[channel] = {
            'observed_mi': res['observed_mi'],
            'null_mean': res['null_mean'],
            'null_std': res['null_std'],
            'z_score': res['z_score'],
            'p_value': res['p_value'],
            'partial_mi': partial_mi,
            'significant': significant,
        }

        sig_mark = ' ***' if significant else ''
        elapsed = time.time() - t_ch
        print(f'  [{ch_idx+1:2d}/18] {channel:20s}  MI={res["observed_mi"]:.4f}  '
              f'z={res["z_score"]:6.2f}  p={res["p_value"]:.4f}  '
              f'partial={partial_mi if partial_mi is not None else "N/A":>8}{sig_mark}  ({elapsed:.1f}s)')

    return results


# ============================================================
# Block 3: Ablation decomposition
# ============================================================

def _compute_cosine_similarity(vec_a, vec_b):
    """Cosine similarity between two dicts keyed by channel names."""
    dot = 0.0
    mag_a = 0.0
    mag_b = 0.0
    for ch in CHANNEL_NAMES:
        a = vec_a.get(ch, 0.0)
        b = vec_b.get(ch, 0.0)
        dot += a * b
        mag_a += a * a
        mag_b += b * b
    if mag_a < 1e-15 or mag_b < 1e-15:
        return 0.0
    return dot / (math.sqrt(mag_a) * math.sqrt(mag_b))


def _z_score_channels(pairs_bb):
    """Z-score each channel across all pairs (both feat_n and feat_n1)."""
    # Collect all values per channel
    channel_vals = defaultdict(list)
    for p in pairs_bb:
        for ch in CHANNEL_NAMES:
            channel_vals[ch].append(p['feat_n'][ch])
            channel_vals[ch].append(p['feat_n1'][ch])

    # Compute mean/std per channel
    stats = {}
    for ch in CHANNEL_NAMES:
        vals = channel_vals[ch]
        mean = sum(vals) / len(vals)
        std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
        stats[ch] = (mean, std if std > 1e-12 else 1.0)

    return stats


def run_ablation(pairs):
    """
    Ablation decomposition:
    1. Compute baseline smoothness (mean cosine similarity between consecutive
       z-scored line feature vectors)
    2. For each channel k: shuffle channel k within paragraphs, recompute smoothness
    3. Delta_k = (baseline - ablated_k) / baseline
    4. Test additivity: sum(delta_k) vs 1.0
    """
    pairs_bb = [p for p in pairs if p['context_type'] == 'body_body']
    if len(pairs_bb) < 20:
        return {}

    z_stats = _z_score_channels(pairs_bb)

    def z_score_feat(feat):
        return {ch: (feat[ch] - z_stats[ch][0]) / z_stats[ch][1] for ch in CHANNEL_NAMES}

    # Baseline smoothness
    baseline_sims = []
    for p in pairs_bb:
        zn = z_score_feat(p['feat_n'])
        zn1 = z_score_feat(p['feat_n1'])
        baseline_sims.append(_compute_cosine_similarity(zn, zn1))
    baseline_smooth = sum(baseline_sims) / len(baseline_sims) if baseline_sims else 0.0

    print(f'  Baseline smoothness (mean cosine): {baseline_smooth:.4f}')

    # Group by paragraph for within-paragraph shuffling
    para_groups = defaultdict(list)
    for p in pairs_bb:
        key = (p['folio'], p['para_id'])
        para_groups[key].append(p)

    # Reconstruct per-paragraph line sequences
    para_line_sequences = {}
    for key, group_pairs in para_groups.items():
        line_feats = [group_pairs[0]['feat_n']]
        for gp in group_pairs:
            line_feats.append(gp['feat_n1'])
        para_line_sequences[key] = line_feats

    results = {}
    for ch_idx, channel in enumerate(CHANNEL_NAMES):
        # Shuffle this channel's values within each paragraph
        ablated_sims = []
        for key, line_feats in para_line_sequences.items():
            n_lines = len(line_feats)
            # Extract channel values and shuffle
            ch_vals = [f[channel] for f in line_feats]
            shuffled_vals = list(ch_vals)
            RNG.shuffle(shuffled_vals)

            # Create ablated features
            ablated_feats = []
            for i, f in enumerate(line_feats):
                af = dict(f)
                af[channel] = shuffled_vals[i]
                ablated_feats.append(af)

            # Compute consecutive cosine similarities
            for i in range(n_lines - 1):
                zn = z_score_feat(ablated_feats[i])
                zn1 = z_score_feat(ablated_feats[i + 1])
                ablated_sims.append(_compute_cosine_similarity(zn, zn1))

        ablated_smooth = sum(ablated_sims) / len(ablated_sims) if ablated_sims else 0.0
        delta_frac = (baseline_smooth - ablated_smooth) / baseline_smooth if abs(baseline_smooth) > 1e-12 else 0.0

        results[channel] = {
            'ablated_smoothness': ablated_smooth,
            'delta_fraction': delta_frac,
        }
        print(f'  [{ch_idx+1:2d}/18] {channel:20s}  '
              f'ablated={ablated_smooth:.4f}  delta={delta_frac:+.4f}')

    # Additivity test
    total_delta = sum(r['delta_fraction'] for r in results.values())
    results['additivity_ratio'] = total_delta
    print(f'  Sum of deltas: {total_delta:.4f} (1.0 = perfectly additive)')

    results['baseline_smoothness'] = baseline_smooth
    return results


# ============================================================
# Block 4: Transfer entropy (top 5 channels)
# ============================================================

def run_transfer_entropy(pairs, significant_channels):
    """
    TE(ch_N -> ch_{N+1}) vs TE(ch_{N+1} -> ch_N) for top channels.

    Build time series per paragraph (sequence of channel values across body lines),
    concatenate preserving paragraph boundaries, compute TE.
    """
    pairs_bb = [p for p in pairs if p['context_type'] == 'body_body']
    if len(pairs_bb) < 20 or not significant_channels:
        return {}

    # Select top 5 by z-score
    top_channels = sorted(significant_channels, key=lambda ch: significant_channels[ch], reverse=True)[:5]

    # Build per-paragraph time series
    para_groups = defaultdict(list)
    for p in pairs_bb:
        key = (p['folio'], p['para_id'])
        para_groups[key].append(p)

    # Reconstruct line sequences per paragraph
    para_line_sequences = {}
    for key, group_pairs in para_groups.items():
        line_feats = [group_pairs[0]['feat_n']]
        for gp in group_pairs:
            line_feats.append(gp['feat_n1'])
        para_line_sequences[key] = line_feats

    results = {}
    for channel in top_channels:
        # Concatenate time series across paragraphs (preserving within-paragraph order)
        all_values = []
        for key, line_feats in para_line_sequences.items():
            if len(line_feats) >= 4:  # Need enough for TE
                vals = [f[channel] for f in line_feats]
                all_values.extend(vals)

        if len(all_values) < 30:
            results[channel] = {'te_forward': 0.0, 'te_backward': 0.0, 'asymmetry': 0.0,
                                'note': 'insufficient_data'}
            continue

        # Forward TE: source=line_N, target=line_N+1
        source = all_values[:-1]
        target = all_values[1:]
        te_forward = compute_transfer_entropy(source, target)

        # Backward TE: source=line_N+1, target=line_N
        te_backward = compute_transfer_entropy(target, source)

        # Asymmetry ratio
        te_sum = te_forward + te_backward
        asymmetry = (te_forward - te_backward) / te_sum if te_sum > 1e-12 else 0.0

        results[channel] = {
            'te_forward': te_forward,
            'te_backward': te_backward,
            'asymmetry': asymmetry,
            'n_values': len(all_values),
        }
        print(f'  {channel:20s}  TE_fwd={te_forward:.4f}  TE_bwd={te_backward:.4f}  '
              f'asym={asymmetry:+.3f}')

    return results


# ============================================================
# Block 5: Safety alternation (ey/ii cross-MI)
# ============================================================

def run_safety_alternation(pairs):
    """
    MI(ey_N, ii_{N+1}) and MI(ii_N, ey_{N+1}).
    Tests whether preventive safety (ey) and transformative safety (ii)
    channels alternate across consecutive lines.
    """
    pairs_bb = [p for p in pairs if p['context_type'] == 'body_body']
    if len(pairs_bb) < 20:
        return {}

    # ey -> ii: ey fraction on line N predicts ii fraction on line N+1
    ey_n = [p['feat_n']['ey_frac'] for p in pairs_bb]
    ii_n1 = [p['feat_n1']['ii_frac'] for p in pairs_bb]

    # ii -> ey: ii fraction on line N predicts ey fraction on line N+1
    ii_n = [p['feat_n']['ii_frac'] for p in pairs_bb]
    ey_n1 = [p['feat_n1']['ey_frac'] for p in pairs_bb]

    # Paragraph-shuffled null for ey->ii
    ey_to_ii_res = _paragraph_shuffled_null(pairs_bb, 'ii_frac', N_PERM, RNG)
    # Custom: use ey_n as x instead of ii_n
    ey_to_ii_mi = compute_mi(ey_n, ii_n1)
    ey_to_ii_null_vals = []
    # Group and shuffle for proper null
    para_groups = defaultdict(list)
    for p in pairs_bb:
        key = (p['folio'], p['para_id'])
        para_groups[key].append(p)
    para_line_sequences = {}
    for key, group_pairs in para_groups.items():
        line_feats = [group_pairs[0]['feat_n']]
        for gp in group_pairs:
            line_feats.append(gp['feat_n1'])
        para_line_sequences[key] = line_feats

    for _ in range(N_PERM):
        shuf_x = []
        shuf_y = []
        for key, line_feats in para_line_sequences.items():
            shuffled = list(line_feats)
            RNG.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                shuf_x.append(shuffled[i]['ey_frac'])
                shuf_y.append(shuffled[i + 1]['ii_frac'])
        ey_to_ii_null_vals.append(compute_mi(shuf_x, shuf_y))

    ey_ii_null_mean = sum(ey_to_ii_null_vals) / len(ey_to_ii_null_vals)
    ey_ii_null_std = (sum((v - ey_ii_null_mean) ** 2 for v in ey_to_ii_null_vals) /
                      len(ey_to_ii_null_vals)) ** 0.5
    ey_ii_z = ((ey_to_ii_mi - ey_ii_null_mean) / ey_ii_null_std
               if ey_ii_null_std > 1e-12 else 0.0)
    ey_ii_p = sum(1 for v in ey_to_ii_null_vals if v >= ey_to_ii_mi) / len(ey_to_ii_null_vals)

    # ii -> ey
    ii_to_ey_mi = compute_mi(ii_n, ey_n1)
    ii_to_ey_null_vals = []
    for _ in range(N_PERM):
        shuf_x = []
        shuf_y = []
        for key, line_feats in para_line_sequences.items():
            shuffled = list(line_feats)
            RNG.shuffle(shuffled)
            for i in range(len(shuffled) - 1):
                shuf_x.append(shuffled[i]['ii_frac'])
                shuf_y.append(shuffled[i + 1]['ey_frac'])
        ii_to_ey_null_vals.append(compute_mi(shuf_x, shuf_y))

    ii_ey_null_mean = sum(ii_to_ey_null_vals) / len(ii_to_ey_null_vals)
    ii_ey_null_std = (sum((v - ii_ey_null_mean) ** 2 for v in ii_to_ey_null_vals) /
                      len(ii_to_ey_null_vals)) ** 0.5
    ii_ey_z = ((ii_to_ey_mi - ii_ey_null_mean) / ii_ey_null_std
               if ii_ey_null_std > 1e-12 else 0.0)
    ii_ey_p = sum(1 for v in ii_to_ey_null_vals if v >= ii_to_ey_mi) / len(ii_to_ey_null_vals)

    result = {
        'ey_to_ii': {
            'mi': ey_to_ii_mi,
            'null_mean': ey_ii_null_mean,
            'null_std': ey_ii_null_std,
            'z_score': ey_ii_z,
            'p_value': ey_ii_p,
        },
        'ii_to_ey': {
            'mi': ii_to_ey_mi,
            'null_mean': ii_ey_null_mean,
            'null_std': ii_ey_null_std,
            'z_score': ii_ey_z,
            'p_value': ii_ey_p,
        },
    }

    print(f'  ey->ii:  MI={ey_to_ii_mi:.4f}  z={ey_ii_z:.2f}  p={ey_ii_p:.4f}')
    print(f'  ii->ey:  MI={ii_to_ey_mi:.4f}  z={ii_ey_z:.2f}  p={ii_ey_p:.4f}')

    return result


# ============================================================
# Block 6: Context partitioning (body-body vs cross-paragraph)
# ============================================================

def run_context_partition(pairs):
    """
    Partition into body-body and cross-paragraph.
    Report MI per context type for each channel.
    """
    pairs_bb = [p for p in pairs if p['context_type'] == 'body_body']
    pairs_cp = [p for p in pairs if p['context_type'] == 'cross_paragraph']

    print(f'  body-body pairs: {len(pairs_bb)}')
    print(f'  cross-paragraph pairs: {len(pairs_cp)}')

    results = {'body_body': {}, 'cross_paragraph': {}, 'n_body_body': len(pairs_bb),
               'n_cross_paragraph': len(pairs_cp)}

    for channel in CHANNEL_NAMES:
        # Body-body MI
        if len(pairs_bb) >= 20:
            x_bb = [p['feat_n'][channel] for p in pairs_bb]
            y_bb = [p['feat_n1'][channel] for p in pairs_bb]
            mi_bb = compute_mi(x_bb, y_bb)
        else:
            mi_bb = 0.0

        # Cross-paragraph MI
        if len(pairs_cp) >= 20:
            x_cp = [p['feat_n'][channel] for p in pairs_cp]
            y_cp = [p['feat_n1'][channel] for p in pairs_cp]
            mi_cp = compute_mi(x_cp, y_cp)
        else:
            mi_cp = 0.0

        ratio = mi_bb / mi_cp if mi_cp > 1e-12 else float('inf') if mi_bb > 1e-12 else 1.0

        results['body_body'][channel] = {'mi': mi_bb}
        results['cross_paragraph'][channel] = {'mi': mi_cp}

        if mi_bb > MI_EFFECT_FLOOR or mi_cp > MI_EFFECT_FLOOR:
            ratio_str = f'{ratio:.2f}' if ratio < 100 else 'inf'
            print(f'  {channel:20s}  BB={mi_bb:.4f}  CP={mi_cp:.4f}  ratio={ratio_str}')

    return results


# ============================================================
# Block 7: Verdict
# ============================================================

def compute_verdict(census_results, ablation_results, te_results, safety_results,
                    context_results):
    """Determine overall verdict based on census and ablation."""
    # Count significant channels
    sig_channels = [ch for ch, r in census_results.items()
                    if r.get('significant', False)]
    n_sig = len(sig_channels)

    # Check if length dominates ablation
    length_delta = ablation_results.get('length', {}).get('delta_fraction', 0.0)
    total_delta = sum(ablation_results.get(ch, {}).get('delta_fraction', 0.0)
                      for ch in CHANNEL_NAMES)
    length_share = length_delta / total_delta if abs(total_delta) > 1e-12 else 0.0

    # Build predictions
    predictions = {}

    # P1: Length dominance
    p1_result = f'{length_share:.0%}'
    p1_pass = length_share > 0.60
    predictions['P1_length_dominant'] = {
        'prediction': '>60% of ablation signal',
        'result': p1_result,
        'pass': p1_pass,
    }

    # P2: At least 5 significant channels
    predictions['P2_multi_channel'] = {
        'prediction': '>=5 channels significant (z>3, MI>0.01)',
        'result': f'{n_sig} channels',
        'pass': n_sig >= 5,
    }

    # P3: Cross-paragraph MI lower than body-body
    if context_results:
        bb_total = sum(context_results.get('body_body', {}).get(ch, {}).get('mi', 0.0)
                       for ch in CHANNEL_NAMES)
        cp_total = sum(context_results.get('cross_paragraph', {}).get(ch, {}).get('mi', 0.0)
                       for ch in CHANNEL_NAMES)
        bb_gt_cp = bb_total > cp_total
    else:
        bb_gt_cp = False
        bb_total = 0.0
        cp_total = 0.0
    predictions['P3_within_gt_cross'] = {
        'prediction': 'body-body MI > cross-paragraph MI',
        'result': f'BB={bb_total:.3f} vs CP={cp_total:.3f}',
        'pass': bb_gt_cp,
    }

    # P4: Transfer entropy asymmetry (forward > backward for majority)
    if te_results:
        fwd_wins = sum(1 for ch, r in te_results.items()
                       if isinstance(r, dict) and r.get('asymmetry', 0) > 0)
        total_te = len([ch for ch in te_results if isinstance(te_results[ch], dict)
                        and 'asymmetry' in te_results[ch]])
        te_majority = fwd_wins > total_te / 2 if total_te > 0 else False
    else:
        fwd_wins = 0
        total_te = 0
        te_majority = False
    predictions['P4_te_forward_dominant'] = {
        'prediction': 'TE forward > backward for majority of top channels',
        'result': f'{fwd_wins}/{total_te} channels forward-dominant',
        'pass': te_majority,
    }

    # P5: Safety alternation (at least one direction significant)
    if safety_results:
        ey_ii_sig = safety_results.get('ey_to_ii', {}).get('z_score', 0) > 2.0
        ii_ey_sig = safety_results.get('ii_to_ey', {}).get('z_score', 0) > 2.0
        safety_sig = ey_ii_sig or ii_ey_sig
    else:
        safety_sig = False
    predictions['P5_safety_alternation'] = {
        'prediction': 'ey<->ii cross-MI significant (z>2)',
        'result': f'ey->ii z={safety_results.get("ey_to_ii", {}).get("z_score", 0):.1f}, '
                  f'ii->ey z={safety_results.get("ii_to_ey", {}).get("z_score", 0):.1f}'
                  if safety_results else 'no data',
        'pass': safety_sig,
    }

    # Determine verdict
    if p1_pass and n_sig < 3:
        verdict = 'SEQUENTIAL_LENGTH_ONLY'
    elif p1_pass:
        verdict = 'SEQUENTIAL_LENGTH_DOMINANT'
    elif n_sig >= 5 and not p1_pass:
        verdict = 'SEQUENTIAL_MULTI_CHANNEL'
    elif n_sig >= 3:
        verdict = 'SEQUENTIAL_PARTIAL'
    else:
        verdict = 'SEQUENTIAL_WEAK'

    return {
        'verdict': verdict,
        'n_significant': n_sig,
        'significant_channels': sig_channels,
        'length_ablation_share': length_share,
        'predictions': predictions,
    }


# ============================================================
# Main
# ============================================================

def main():
    t0 = time.time()

    print('=' * 60)
    print('Phase 623 Script 1: Sequential Channel Census')
    print('=' * 60)

    # Build corpus
    print('\nBuilding corpus...')
    corpus = build_corpus()
    n_folios = len(corpus)
    n_paras = sum(len(fdata['paragraphs']) for fdata in corpus.values())
    n_body_lines = sum(
        len(para['body_lines'])
        for fdata in corpus.values()
        for para in fdata['paragraphs']
    )
    print(f'  Folios: {n_folios}, Paragraphs: {n_paras}, Body lines: {n_body_lines}')

    # Compute folio PREFIX distributions
    print('\nComputing folio PREFIX distributions...')
    prefix_dists = compute_folio_prefix_dists(corpus)

    # Extract pairs
    print('\nExtracting consecutive line pairs...')
    pairs = extract_pairs(corpus, prefix_dists)
    n_bb = sum(1 for p in pairs if p['context_type'] == 'body_body')
    n_cp = sum(1 for p in pairs if p['context_type'] == 'cross_paragraph')
    print(f'  Extracted {len(pairs)} consecutive line pairs '
          f'({n_bb} body-body, {n_cp} cross-paragraph)')

    # Block 2: Channel census
    print('\n' + '=' * 60)
    print('Block 2: Channel-by-channel MI census')
    print('=' * 60)
    census = run_channel_census(pairs)
    t_census = time.time()
    print(f'  Census complete ({t_census - t0:.1f}s)')

    # Identify significant channels for transfer entropy
    sig_for_te = {ch: census[ch]['z_score'] for ch in census
                  if census[ch].get('significant', False)}
    n_sig = len(sig_for_te)
    print(f'\n  Significant channels: {n_sig} / {N_CHANNELS}')

    # Block 3: Ablation
    print('\n' + '=' * 60)
    print('Block 3: Ablation decomposition')
    print('=' * 60)
    ablation = run_ablation(pairs)
    t_ablation = time.time()
    print(f'  Ablation complete ({t_ablation - t0:.1f}s)')

    # Block 4: Transfer entropy
    print('\n' + '=' * 60)
    print('Block 4: Transfer entropy (top 5 significant channels)')
    print('=' * 60)
    te = run_transfer_entropy(pairs, sig_for_te)
    t_te = time.time()
    print(f'  TE complete ({t_te - t0:.1f}s)')

    # Block 5: Safety alternation
    print('\n' + '=' * 60)
    print('Block 5: Safety alternation (ey/ii cross-MI)')
    print('=' * 60)
    safety = run_safety_alternation(pairs)
    t_safety = time.time()
    print(f'  Safety complete ({t_safety - t0:.1f}s)')

    # Block 6: Context partition
    print('\n' + '=' * 60)
    print('Block 6: Context partitioning')
    print('=' * 60)
    context = run_context_partition(pairs)
    t_context = time.time()
    print(f'  Context complete ({t_context - t0:.1f}s)')

    # Block 7: Verdict
    print('\n' + '=' * 60)
    print('Block 7: Verdict')
    print('=' * 60)
    verdict_info = compute_verdict(census, ablation, te, safety, context)
    verdict = verdict_info['verdict']
    predictions = verdict_info['predictions']

    print(f'\n  VERDICT: {verdict}')
    print(f'  Significant channels: {verdict_info["n_significant"]} / {N_CHANNELS}')
    print(f'  Length ablation share: {verdict_info["length_ablation_share"]:.1%}')
    print(f'\n  Predictions:')
    for pk, pv in predictions.items():
        status = 'PASS' if pv['pass'] else 'FAIL'
        print(f'    {pk}: {pv["prediction"]} -> {pv["result"]} [{status}]')

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        'phase': 623,
        'name': 'sequential_channel_census',
        'n_folios': n_folios,
        'n_paragraphs': n_paras,
        'n_body_lines': n_body_lines,
        'n_pairs': len(pairs),
        'n_body_body': n_bb,
        'n_cross_paragraph': n_cp,
        'channel_census': census,
        'ablation': ablation,
        'transfer_entropy': te,
        'safety_alternation': safety,
        'context_partition': context,
        'verdict': verdict,
        'verdict_detail': {
            'n_significant': verdict_info['n_significant'],
            'significant_channels': verdict_info['significant_channels'],
            'length_ablation_share': verdict_info['length_ablation_share'],
        },
        'predictions': predictions,
        'runtime_s': round(time.time() - t0, 1),
    }

    out_path = RESULTS_DIR / 'sequential_channel_census.json'
    with open(out_path, 'w') as f:
        json.dump(round_floats(output), f, indent=2)

    print(f'\nResults saved to {out_path}')
    print(f'Total runtime: {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()

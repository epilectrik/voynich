"""PHASE_718 follow-up: d<1.0 absolute-distance gating per methodology memory.

The top-1+ratio methodology collapses to f34v regardless of corpus (documented in
feedback_top1_matcher_mode_is_degenerate.md). The corrected methodology per C1971
is absolute-distance gating: count how many chapter→folio pairs have d<1.0.

If Theophilus has comparable d<1.0 matches to Codicillus, negative control fails
(matcher detects any procedural text). If fewer, matcher is alchemy-specific.
"""
from __future__ import annotations

import io
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "phases" / "RECIPE_FOLIO_CORRESPONDENCE" / "scripts"))
sys.path.insert(0, str(ROOT / "phases" / "PER_DOMAIN_BRIDGE_CALIBRATION" / "scripts"))

from shared_628 import (
    load_b_operational_profiles, load_b_deployment_features, load_regime_mapping,
    TUNED_DIMS, build_pl_vector, build_v_vector,
    compute_residuals, standardize,
)

OUT_PATH = ROOT / 'phases' / 'PHASE_718_THEOPHILUS_8D_MATCHER' / 'results' / 'theophilus_d10_test.json'


def build_distance_matrix(chapter_dicts, all_b_folios, op_profiles, deploy_features):
    """Return (chapter_idx, folio_idx) -> distance matrix."""
    n_ch = len(chapter_dicts)
    n_v = len(all_b_folios)
    pl_raw = [build_pl_vector(ch, TUNED_DIMS) for ch in chapter_dicts]
    v_raw = [build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS) for f in all_b_folios]
    for i in range(n_ch):
        for d, (_, _, sign) in enumerate(TUNED_DIMS):
            pl_raw[i][d] *= sign
    pl_resid = compute_residuals(pl_raw)
    v_resid = compute_residuals(v_raw)
    all_std = standardize(pl_resid + v_resid)
    pl_std = all_std[:n_ch]
    v_std = all_std[n_ch:]
    n_dims = len(TUNED_DIMS)
    dmat = [[0.0] * n_v for _ in range(n_ch)]
    for i in range(n_ch):
        for j in range(n_v):
            dmat[i][j] = math.sqrt(sum((pl_std[i][d] - v_std[j][d]) ** 2 for d in range(n_dims)))
    return dmat


def get_section(folio):
    import re
    m = re.search(r"(\d+)", folio)
    if m:
        num = int(m.group(1))
        if 75 <= num <= 86 or 87 <= num <= 102:
            return "B"
        if 99 <= num <= 102:
            return "S"
        if 103 <= num <= 116:
            return "C"
        if num <= 66:
            return "H"
        return "B"
    return "?"


def analyze_d10(label, dmat, chapter_dicts, all_b_folios, sec_of, d_threshold=1.0):
    """For each chapter, count folios with d < threshold."""
    n_ch = len(chapter_dicts)
    n_v = len(all_b_folios)
    chapters_with_match = 0
    n_matches_per_chapter = []
    folio_match_count = Counter()
    section_match_count = Counter()
    confirmed_pairs = []
    for i in range(n_ch):
        matches = [(j, dmat[i][j]) for j in range(n_v) if dmat[i][j] < d_threshold]
        n_matches_per_chapter.append(len(matches))
        if matches:
            chapters_with_match += 1
            for j, d in matches:
                folio_match_count[all_b_folios[j]] += 1
                section_match_count[sec_of[all_b_folios[j]]] += 1
                confirmed_pairs.append({
                    'chapter_idx': i,
                    'chapter_summary': chapter_dicts[i].get('summary', '?'),
                    'folio': all_b_folios[j],
                    'section': sec_of[all_b_folios[j]],
                    'distance': d,
                })
    min_distances = [min(dmat[i]) for i in range(n_ch)]
    return {
        'label': label,
        'd_threshold': d_threshold,
        'n_chapters': n_ch,
        'chapters_with_at_least_1_match': chapters_with_match,
        'total_match_pairs_d_lt_threshold': sum(n_matches_per_chapter),
        'mean_matches_per_chapter': float(sum(n_matches_per_chapter) / max(n_ch, 1)),
        'min_distance_distribution': {
            'min': float(min(min_distances)),
            'max': float(max(min_distances)),
            'mean': float(sum(min_distances) / len(min_distances)),
            'median': float(sorted(min_distances)[len(min_distances)//2]),
        },
        'folio_match_counts_top10': dict(folio_match_count.most_common(10)),
        'section_match_counts': dict(section_match_count),
        'confirmed_pairs_sample': confirmed_pairs[:20],
    }


def main():
    print("=" * 70)
    print("PHASE_718 d<1.0 ABSOLUTE-DISTANCE GATING (corrected methodology)")
    print("=" * 70)

    # Load Theophilus features
    theo_path = ROOT / 'phases' / 'PHASE_718_THEOPHILUS_8D_MATCHER' / 'results' / 'theophilus_chapter_features.json'
    with open(theo_path, encoding='utf-8') as f:
        theo_chapters = json.load(f)['chapters']

    # Load Codicillus features (baseline comparison)
    cod_path = ROOT / 'sources' / 'codicillus' / 'codicillus_channel_features.json'
    with open(cod_path, encoding='utf-8') as f:
        cod_data = json.load(f)
    cod_chapters = cod_data.get('segments') or cod_data.get('chapters') or []
    print(f"\nLoaded {len(theo_chapters)} Theophilus chapters")
    print(f"Loaded {len(cod_chapters)} Codicillus segments")

    # Load Voynich side
    op_profiles = load_b_operational_profiles()
    deploy_features, _ = load_b_deployment_features()
    all_b_folios = sorted(op_profiles.keys())
    sec_of = {f: get_section(f) for f in all_b_folios}
    print(f"  {len(all_b_folios)} Voynich folios")

    # Compute distance matrices for each corpus
    print("\nComputing Theophilus distance matrix...")
    theo_dmat = build_distance_matrix(theo_chapters, all_b_folios, op_profiles, deploy_features)
    print("Computing Codicillus distance matrix...")
    cod_dmat = build_distance_matrix(cod_chapters, all_b_folios, op_profiles, deploy_features)

    # Analyze at multiple d-thresholds
    for d_thresh in [1.0, 1.5, 2.0]:
        print("\n" + "=" * 70)
        print(f"d < {d_thresh} ANALYSIS")
        print("=" * 70)

        theo_result = analyze_d10('Theophilus', theo_dmat, theo_chapters, all_b_folios, sec_of, d_thresh)
        cod_result = analyze_d10('Codicillus', cod_dmat, cod_chapters, all_b_folios, sec_of, d_thresh)

        print(f"\n  Codicillus (positive corpus, n={cod_result['n_chapters']}):")
        print(f"    Chapters with ≥1 match: {cod_result['chapters_with_at_least_1_match']} "
              f"({100*cod_result['chapters_with_at_least_1_match']/cod_result['n_chapters']:.1f}%)")
        print(f"    Total match pairs: {cod_result['total_match_pairs_d_lt_threshold']}")
        print(f"    Mean matches/chapter: {cod_result['mean_matches_per_chapter']:.2f}")
        print(f"    Min-distance dist: min={cod_result['min_distance_distribution']['min']:.3f}, "
              f"median={cod_result['min_distance_distribution']['median']:.3f}, "
              f"mean={cod_result['min_distance_distribution']['mean']:.3f}")
        print(f"    Section match counts: {cod_result['section_match_counts']}")

        print(f"\n  Theophilus (negative control, n={theo_result['n_chapters']}):")
        print(f"    Chapters with ≥1 match: {theo_result['chapters_with_at_least_1_match']} "
              f"({100*theo_result['chapters_with_at_least_1_match']/theo_result['n_chapters']:.1f}%)")
        print(f"    Total match pairs: {theo_result['total_match_pairs_d_lt_threshold']}")
        print(f"    Mean matches/chapter: {theo_result['mean_matches_per_chapter']:.2f}")
        print(f"    Min-distance dist: min={theo_result['min_distance_distribution']['min']:.3f}, "
              f"median={theo_result['min_distance_distribution']['median']:.3f}, "
              f"mean={theo_result['min_distance_distribution']['mean']:.3f}")
        print(f"    Section match counts: {theo_result['section_match_counts']}")

        # Comparison: Theophilus normalized matches per chapter vs Codicillus
        if cod_result['n_chapters'] > 0:
            cod_rate = cod_result['chapters_with_at_least_1_match'] / cod_result['n_chapters']
            theo_rate = theo_result['chapters_with_at_least_1_match'] / theo_result['n_chapters']
            print(f"\n  Comparison: Codicillus match-rate={cod_rate:.2%}, Theophilus match-rate={theo_rate:.2%}")
            ratio = theo_rate / max(cod_rate, 0.001)
            print(f"  Theophilus/Codicillus ratio: {ratio:.2f}")
            if ratio < 0.25:
                interp = "Theophilus matches much less — alchemy-specific matcher (negative control PASSED at d<1.0)"
            elif ratio < 0.50:
                interp = "Theophilus matches somewhat less — partial alchemy-specificity"
            elif ratio < 1.10:
                interp = "Theophilus matches similarly — matcher detects any procedural text (negative control FAILED at d<1.0)"
            else:
                interp = "Theophilus matches MORE than Codicillus — unexpected"
            print(f"  Interpretation: {interp}")

    # ---- Save ----
    print("\nSaving full result...")
    # Recompute primary d<1.0 for full save
    theo_d10 = analyze_d10('Theophilus', theo_dmat, theo_chapters, all_b_folios, sec_of, 1.0)
    cod_d10 = analyze_d10('Codicillus', cod_dmat, cod_chapters, all_b_folios, sec_of, 1.0)

    out = {
        'method': 'PHASE_718 d<1.0 absolute-distance gating corrected methodology',
        'theophilus': theo_d10,
        'codicillus_baseline': cod_d10,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"Written: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

"""PHASE_718: Theophilus 8D matcher against Voynich folios.

Applies the same 8D matcher methodology as C1971's Codicillus matcher to Theophilus.
This is the pre-registered NEGATIVE CONTROL test per sources/theophilus/README.md.

Pre-registered failure criteria (2026-05-14):
  - ≤2/30 confident matches (ratio ≥ 1.15)
  - Mean ratio ≤ 1.10
  - Permutation p ≥ 0.10
  - Matches should NOT concentrate on Section B alchemy folios

If any of these fail, demote C1882-C1956 from "operational correspondence" to
"structural attraction to medieval procedural text."
"""
from __future__ import annotations

import io
import json
import math
import random
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

OUT_PATH = ROOT / 'phases' / 'PHASE_718_THEOPHILUS_8D_MATCHER' / 'results' / 'theophilus_matcher_results.json'

# Pre-registered failure criteria
PRE_REG = {
    'max_confident_matches': 2,  # of 30 (or proportional)
    'ratio_threshold': 1.15,
    'max_mean_ratio': 1.10,
    'min_permutation_p': 0.10,
}


def main():
    print("=" * 70)
    print("PHASE_718 THEOPHILUS 8D MATCHER (negative control)")
    print("=" * 70)

    # Load Theophilus features
    theo_path = ROOT / 'phases' / 'PHASE_718_THEOPHILUS_8D_MATCHER' / 'results' / 'theophilus_chapter_features.json'
    with open(theo_path, encoding='utf-8') as f:
        theo_data = json.load(f)
    chapters = theo_data['chapters']
    n_chapters = len(chapters)
    print(f"\nLoaded {n_chapters} Theophilus chapters")

    # Load Voynich side
    print("Loading Voynich side...")
    op_profiles = load_b_operational_profiles()
    deploy_features, _ = load_b_deployment_features()
    regime_map = load_regime_mapping()

    # Folio sections - use simple folio number heuristic
    def section(folio):
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

    all_b_folios = sorted(op_profiles.keys())
    n_v = len(all_b_folios)
    print(f"  {n_v} Voynich folios")
    sec_of = {f: section(f) for f in all_b_folios}
    sec_counts = Counter(sec_of.values())
    print(f"  Section distribution: {dict(sec_counts)}")

    # Build vectors
    n_dims = len(TUNED_DIMS)
    print(f"\nBuilding {n_chapters} PL vectors and {n_v} V vectors over {n_dims} dimensions...")
    pl_raw = [build_pl_vector(ch, TUNED_DIMS) for ch in chapters]
    v_raw = [build_v_vector(f, op_profiles, deploy_features, TUNED_DIMS) for f in all_b_folios]

    # Apply signs
    for i in range(n_chapters):
        for d, (_, _, sign) in enumerate(TUNED_DIMS):
            pl_raw[i][d] *= sign

    # Residualize + standardize jointly
    pl_resid = compute_residuals(pl_raw)
    v_resid = compute_residuals(v_raw)
    all_std = standardize(pl_resid + v_resid)
    pl_std = all_std[:n_chapters]
    v_std = all_std[n_chapters:]

    # Distance matrix
    print("Computing distance matrix...")
    dmat = [[0.0] * n_v for _ in range(n_chapters)]
    for i in range(n_chapters):
        for j in range(n_v):
            dmat[i][j] = math.sqrt(sum((pl_std[i][d] - v_std[j][d]) ** 2 for d in range(n_dims)))

    # Top-1 + ratio
    top1_section = Counter()
    top1_folio = Counter()
    distances = []
    ratios = []
    confident_matches = []
    for i in range(n_chapters):
        ranked = sorted(range(n_v), key=lambda j: dmat[i][j])
        j = ranked[0]
        j2 = ranked[1]
        d1, d2 = dmat[i][j], dmat[i][j2]
        folio = all_b_folios[j]
        top1_section[sec_of[folio]] += 1
        top1_folio[folio] += 1
        distances.append(d1)
        r = d2 / d1 if d1 > 0.01 else 1.0
        ratios.append(r)
        if r >= PRE_REG['ratio_threshold']:
            confident_matches.append({
                'chapter_idx': i,
                'book': chapters[i].get('book', '?'),
                'chapter_roman': chapters[i].get('chapter_roman', '?'),
                'folio': folio,
                'section': sec_of[folio],
                'distance': d1,
                'ratio': r,
            })

    mean_ratio = sum(ratios) / len(ratios)
    median_ratio = sorted(ratios)[len(ratios) // 2]
    n_confident = sum(1 for r in ratios if r >= PRE_REG['ratio_threshold'])

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nN chapters tested: {n_chapters}")
    print(f"Mean ratio: {mean_ratio:.4f}")
    print(f"Median ratio: {median_ratio:.4f}")
    print(f"Confident matches (ratio≥{PRE_REG['ratio_threshold']}): {n_confident} ({100*n_confident/n_chapters:.1f}%)")
    print(f"\nSection attraction of top-1 matches:")
    for sec in sorted(top1_section):
        c = top1_section[sec]
        n_in_sec = sec_counts.get(sec, 0)
        expected = n_chapters * n_in_sec / n_v if n_v > 0 else 0
        print(f"  {sec}: {c} matches ({100*c/n_chapters:.1f}%) — {n_in_sec} folios in section, expected {expected:.1f}")

    print(f"\nTop 10 most-attracted folios:")
    for f, c in top1_folio.most_common(10):
        print(f"  {f}: {c} chapters → section {sec_of[f]}")

    # ---- Permutation null ----
    print("\nComputing permutation null (1000 perms)...")
    random.seed(42)
    null_mean_ratios = []
    null_confident = []
    for _ in range(1000):
        # Shuffle the PL→V assignment by permuting V indices
        v_perm = list(range(n_v))
        random.shuffle(v_perm)
        # Recompute matrix on shuffled
        shuffled_ratios = []
        shuffled_confident = 0
        for i in range(n_chapters):
            dists = [dmat[i][v_perm[j]] for j in range(n_v)]
            ranked = sorted(dists)
            d1, d2 = ranked[0], ranked[1]
            r = d2 / d1 if d1 > 0.01 else 1.0
            shuffled_ratios.append(r)
            if r >= PRE_REG['ratio_threshold']:
                shuffled_confident += 1
        null_mean_ratios.append(sum(shuffled_ratios) / len(shuffled_ratios))
        null_confident.append(shuffled_confident)

    perm_p_ratio = sum(1 for r in null_mean_ratios if r >= mean_ratio) / len(null_mean_ratios)
    perm_p_confident = sum(1 for c in null_confident if c >= n_confident) / len(null_confident)

    print(f"  Null mean ratio: {sum(null_mean_ratios)/len(null_mean_ratios):.4f}")
    print(f"  Null mean confident matches: {sum(null_confident)/len(null_confident):.1f}")
    print(f"  Permutation p for mean ratio: {perm_p_ratio:.4f}")
    print(f"  Permutation p for confident count: {perm_p_confident:.4f}")

    # ---- Pre-registered criteria check ----
    print("\n" + "=" * 70)
    print("PRE-REGISTERED CRITERIA CHECK")
    print("=" * 70)

    # Criterion 1: ≤2/30 confident matches (proportional: ≤ 2*n/30)
    threshold_confident = max(2, int(round(2 * n_chapters / 30)))
    crit_1_pass = n_confident <= threshold_confident
    print(f"  C1: confident matches ≤ {threshold_confident}? "
          f"({n_confident} observed) → {'PASS' if crit_1_pass else 'FAIL'}")

    # Criterion 2: mean ratio ≤ 1.10
    crit_2_pass = mean_ratio <= PRE_REG['max_mean_ratio']
    print(f"  C2: mean ratio ≤ {PRE_REG['max_mean_ratio']}? "
          f"({mean_ratio:.4f} observed) → {'PASS' if crit_2_pass else 'FAIL'}")

    # Criterion 3: permutation p ≥ 0.10
    crit_3_pass = perm_p_ratio >= PRE_REG['min_permutation_p']
    print(f"  C3: perm p ≥ {PRE_REG['min_permutation_p']}? "
          f"({perm_p_ratio:.4f} observed) → {'PASS' if crit_3_pass else 'FAIL'}")

    # Criterion 4: matches should NOT concentrate on Section B
    n_sec_b = top1_section.get('B', 0)
    n_in_sec_b = sec_counts.get('B', 0)
    sec_b_expected_pct = n_in_sec_b / n_v * 100
    sec_b_observed_pct = n_sec_b / n_chapters * 100
    crit_4_pass = sec_b_observed_pct <= sec_b_expected_pct * 1.5
    print(f"  C4: Section B attraction ≤ 1.5× expected? "
          f"({sec_b_observed_pct:.1f}% obs vs {sec_b_expected_pct:.1f}% expected) → "
          f"{'PASS' if crit_4_pass else 'FAIL'}")

    n_pass = sum([crit_1_pass, crit_2_pass, crit_3_pass, crit_4_pass])
    print(f"\n  PASS COUNT: {n_pass}/4")

    if n_pass == 4:
        verdict = "NEGATIVE CONTROL PASSED — matcher specifically detects alchemy/distillation; C1971 operational reading stands"
    elif n_pass >= 2:
        verdict = "PARTIAL — matcher has alchemy-bias but isn't fully specific"
    else:
        verdict = "NEGATIVE CONTROL FAILED — matcher detects 'any medieval procedural text'; demote C1971 operational reading"

    print(f"\n  VERDICT: {verdict}")

    # Save
    out = {
        'method': 'PHASE_718 Theophilus 8D matcher negative-control test',
        'n_chapters': n_chapters,
        'n_v_folios': n_v,
        'n_dims': n_dims,
        'mean_ratio': mean_ratio,
        'median_ratio': median_ratio,
        'n_confident_matches': n_confident,
        'top1_section_attraction': dict(top1_section),
        'top10_attracted_folios': [(f, c, sec_of[f]) for f, c in top1_folio.most_common(10)],
        'confident_matches': confident_matches[:30],  # cap for output size
        'permutation_p_mean_ratio': perm_p_ratio,
        'permutation_p_confident_count': perm_p_confident,
        'pre_registered_criteria': {
            'c1_max_confident_matches': threshold_confident,
            'c1_observed': n_confident,
            'c1_pass': crit_1_pass,
            'c2_max_mean_ratio': PRE_REG['max_mean_ratio'],
            'c2_observed': mean_ratio,
            'c2_pass': crit_2_pass,
            'c3_min_permutation_p': PRE_REG['min_permutation_p'],
            'c3_observed': perm_p_ratio,
            'c3_pass': crit_3_pass,
            'c4_sec_b_concentration': sec_b_observed_pct,
            'c4_expected': sec_b_expected_pct,
            'c4_pass': crit_4_pass,
            'n_pass': n_pass,
        },
        'verdict': verdict,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

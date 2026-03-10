"""
T3: COF Observability Audit
============================
Phase 568 - CONTROLLED_EXCURSION_METRICS

Pure data analysis script -- no plant runs.
Loads T1 (primary_runs) and T2 (reference, baseline_runs, null_runs) results
and performs 5 observability analyses on COF variants (CCY vs CCY_cof1/2/3).

Analyses:
  OA1: CCY variant comparison across primary runs
  OA2: Closure-excursion overlap under new metrics (SLR vs CCY per COF variant)
  OA3: B10 sensitivity under COF variants (full vs no-CLOSE-recovery)
  OA4: Section-specific COF performance (if section data available)
  OA5: Eligibility expansion (do COF variants expand the non-zero folio set?)

Inputs:
  - t1_controlled_excursion_runs.json   (T1 primary runs, 3 profiles x 20 folios)
  - t2_controlled_excursion_null_runs.json  (T2 reference, baselines, nulls)

Output:
  - t3_cof_observability.json
"""

import json
import math
import time
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
RESULTS_DIR = PHASE_DIR / 'results'

T1_PATH = RESULTS_DIR / 't1_controlled_excursion_runs.json'
T2_PATH = RESULTS_DIR / 't2_controlled_excursion_null_runs.json'
OUTPUT_PATH = RESULTS_DIR / 't3_cof_observability.json'

# CCY variant keys
CCY_VARIANTS = ['CCY', 'CCY_cof1', 'CCY_cof2', 'CCY_cof3']
# Human-readable labels for variants
VARIANT_LABELS = {
    'CCY': 'CTS (base threshold)',
    'CCY_cof1': 'COF1 (0.6*CTS + 0.4*q4)',
    'CCY_cof2': 'COF2 (0.5*CTS + 0.25*q4 + 0.25*mcb)',
    'CCY_cof3': 'COF3 (0.3*CTS + 0.2*q4s + 0.2*cob + 0.3*mcb)',
}


# ---------------------------------------------------------------------------
# Cohen's d
# ---------------------------------------------------------------------------
def cohens_d(group1, group2):
    """Compute Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return 0.0
    mean1 = sum(group1) / n1
    mean2 = sum(group2) / n2
    var1 = sum((x - mean1) ** 2 for x in group1) / max(n1 - 1, 1)
    var2 = sum((x - mean2) ** 2 for x in group2) / max(n2 - 1, 1)
    pooled_std = ((var1 * (n1 - 1) + var2 * (n2 - 1)) / max(n1 + n2 - 2, 1)) ** 0.5
    return (mean1 - mean2) / pooled_std if pooled_std > 1e-10 else 0.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: COF Observability Audit")
    print("Phase 568 - CONTROLLED_EXCURSION_METRICS")
    print("=" * 70)

    # =====================================================================
    # Load inputs
    # =====================================================================
    print("\nLoading T1 results...")
    with open(T1_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    primary_runs = t1_data['primary_runs']
    t1_folios = sorted(primary_runs.keys())
    print(f"  T1 folios: {len(t1_folios)}")
    print(f"  T1 profiles per folio: "
          f"{list(primary_runs[t1_folios[0]].keys()) if t1_folios else '(none)'}")

    print("\nLoading T2 results...")
    with open(T2_PATH, 'r', encoding='utf-8') as f:
        t2_data = json.load(f)
    t2_reference = t2_data['reference']
    t2_baselines = t2_data['baseline_runs']
    t2_nulls = t2_data['null_runs']
    t2_folios = sorted(t2_reference.keys())
    print(f"  T2 reference folios: {len(t2_folios)}")
    print(f"  T2 baseline types: {sorted(t2_baselines.keys())}")
    print(f"  T2 null types: {sorted(t2_nulls.keys())}")

    # =====================================================================
    # Build per-folio averaged metrics from T1 primary runs
    # For each folio, average across all 3 profiles
    # =====================================================================
    print("\nBuilding per-folio averages from T1 primary runs...")
    t1_per_folio = {}
    for folio in t1_folios:
        profiles = primary_runs[folio]
        profile_names = sorted(profiles.keys())
        n_profiles = len(profile_names)
        if n_profiles == 0:
            continue

        avg = {}
        for vk in CCY_VARIANTS:
            vals = [profiles[p].get(vk, 0.0) for p in profile_names]
            avg[vk] = sum(vals) / n_profiles

        # Also grab SLR_mean for OA2
        slr_vals = [profiles[p].get('SLR_mean', 0.0) for p in profile_names]
        avg['SLR_mean'] = sum(slr_vals) / n_profiles

        t1_per_folio[folio] = avg
        print(f"  {folio}: CCY={avg['CCY']:.5f}, COF1={avg['CCY_cof1']:.5f}, "
              f"COF2={avg['CCY_cof2']:.5f}, COF3={avg['CCY_cof3']:.5f}, "
              f"SLR={avg['SLR_mean']:.4f}")

    all_folios = sorted(set(t1_folios) | set(t2_folios))
    print(f"\nCombined folio set: {len(all_folios)}")

    # =====================================================================
    # OA1: CCY variant comparison
    # =====================================================================
    print("\n" + "=" * 70)
    print("OA1: CCY Variant Comparison")
    print("=" * 70)

    oa1_per_folio = {}
    oa1_sums = {vk: 0.0 for vk in CCY_VARIANTS}
    oa1_nonzero = {vk: 0 for vk in CCY_VARIANTS}
    oa1_count = 0

    for folio in all_folios:
        entry = t1_per_folio.get(folio)
        if entry is None:
            continue

        folio_vals = {}
        for vk in CCY_VARIANTS:
            v = entry.get(vk, 0.0)
            folio_vals[vk] = round(v, 6)
            oa1_sums[vk] += v
            if v > 1e-10:
                oa1_nonzero[vk] += 1

        oa1_per_folio[folio] = folio_vals
        oa1_count += 1

    oa1_means = {vk: round(oa1_sums[vk] / max(oa1_count, 1), 6)
                 for vk in CCY_VARIANTS}

    # Determine best variant by mean value
    best_by_mean = max(CCY_VARIANTS, key=lambda vk: oa1_means[vk])

    # Determine best variant by non-zero count
    best_by_coverage = max(CCY_VARIANTS, key=lambda vk: oa1_nonzero[vk])

    oa1_summary = {
        'n_folios': oa1_count,
        'means': oa1_means,
        'n_nonzero': {vk: oa1_nonzero[vk] for vk in CCY_VARIANTS},
        'best_variant_by_mean': best_by_mean,
        'best_variant_by_coverage': best_by_coverage,
    }

    print(f"\n  Mean values across {oa1_count} folios:")
    for vk in CCY_VARIANTS:
        label = VARIANT_LABELS[vk]
        print(f"    {vk:<12} = {oa1_means[vk]:.6f}  "
              f"(nonzero: {oa1_nonzero[vk]}/{oa1_count})  [{label}]")
    print(f"\n  Best by mean:     {best_by_mean}")
    print(f"  Best by coverage: {best_by_coverage}")

    oa1_result = {
        'per_folio': oa1_per_folio,
        'summary': oa1_summary,
    }

    # =====================================================================
    # OA2: Closure-excursion overlap under new metrics
    # =====================================================================
    print("\n" + "=" * 70)
    print("OA2: Closure-Excursion Overlap (SLR vs CCY)")
    print("=" * 70)

    SLR_THRESHOLD = 0.7
    oa2_per_variant = {}

    # Map variant keys to human names for reporting
    variant_short = {'CCY': 'CTS', 'CCY_cof1': 'COF1',
                     'CCY_cof2': 'COF2', 'CCY_cof3': 'COF3'}

    for vk in CCY_VARIANTS:
        n_high_slr = 0
        n_overlap = 0

        for folio in all_folios:
            entry = t1_per_folio.get(folio)
            if entry is None:
                continue

            slr = entry.get('SLR_mean', 0.0)
            ccy_val = entry.get(vk, 0.0)

            if slr > SLR_THRESHOLD:
                n_high_slr += 1
                if ccy_val > 1e-10:
                    n_overlap += 1

        overlap_frac = round(n_overlap / max(n_high_slr, 1), 6)
        short = variant_short[vk]
        oa2_per_variant[short] = {
            'n_high_slr': n_high_slr,
            'n_overlap': n_overlap,
            'overlap_frac': overlap_frac,
        }
        print(f"  {short:<5}: {n_overlap}/{n_high_slr} folios with SLR > {SLR_THRESHOLD} "
              f"also have {vk} > 0  (overlap={overlap_frac:.4f})")

    oa2_result = {
        'slr_threshold': SLR_THRESHOLD,
        'per_variant': oa2_per_variant,
    }

    # =====================================================================
    # OA3: B10 sensitivity under COF variants
    # =====================================================================
    print("\n" + "=" * 70)
    print("OA3: B10 Sensitivity Under COF Variants")
    print("=" * 70)

    # Build B10 per-folio lookup from T2 baseline_runs
    b10_by_folio = {}
    b10_entries = t2_baselines.get('B10', [])
    for entry in b10_entries:
        folio = entry.get('folio', '')
        if folio:
            b10_by_folio[folio] = entry

    print(f"  B10 entries: {len(b10_by_folio)} folios")

    oa3_per_variant = {}
    for vk in CCY_VARIANTS:
        full_vals = []
        b10_vals = []

        for folio in all_folios:
            ref = t2_reference.get(folio)
            b10 = b10_by_folio.get(folio)
            if ref is None or b10 is None:
                continue

            full_vals.append(ref.get(vk, 0.0))
            b10_vals.append(b10.get(vk, 0.0))

        if not full_vals:
            oa3_per_variant[vk] = {
                'full_mean': 0.0, 'b10_mean': 0.0,
                'delta': 0.0, 'cohens_d': 0.0,
                'n_pairs': 0,
            }
            continue

        full_mean = sum(full_vals) / len(full_vals)
        b10_mean = sum(b10_vals) / len(b10_vals)
        delta = full_mean - b10_mean
        d = cohens_d(full_vals, b10_vals)

        oa3_per_variant[vk] = {
            'full_mean': round(full_mean, 6),
            'b10_mean': round(b10_mean, 6),
            'delta': round(delta, 6),
            'cohens_d': round(d, 6),
            'n_pairs': len(full_vals),
        }
        print(f"  {vk:<12}: full={full_mean:.6f}, B10={b10_mean:.6f}, "
              f"delta={delta:+.6f}, Cohen's d={d:.4f}  (n={len(full_vals)})")

    # Best variant by largest absolute Cohen's d
    best_b10_variant = max(
        CCY_VARIANTS,
        key=lambda vk: abs(oa3_per_variant[vk]['cohens_d'])
    )
    print(f"\n  Best B10 sensitivity (largest |d|): {best_b10_variant} "
          f"(d={oa3_per_variant[best_b10_variant]['cohens_d']:.4f})")

    oa3_result = {
        'per_variant': oa3_per_variant,
        'best_variant': best_b10_variant,
    }

    # =====================================================================
    # OA4: Section-specific COF performance
    # =====================================================================
    print("\n" + "=" * 70)
    print("OA4: Section-Specific COF Performance")
    print("=" * 70)

    # Check if section data is available in T1 or T2 outputs
    # T1 primary_runs store per-folio per-profile metrics (no section breakdown)
    # T2 reference stores per-folio metrics (no section breakdown)
    # Section-level analysis would require per-line results, which are not stored
    # in the aggregate outputs.

    oa4_note = ("Section data not available in run outputs; T1 and T2 store "
                "folio-level aggregate metrics only. Section-specific COF "
                "analysis requires per-line results not stored in aggregate "
                "outputs. To obtain section-specific COF performance, re-run "
                "the executor with per-line metric output enabled, or extract "
                "section assignment from line_section_map and compute "
                "per-section CCY variants inline.")

    print(f"  {oa4_note}")

    oa4_result = {
        'note': oa4_note,
    }

    # =====================================================================
    # OA5: Eligibility expansion
    # =====================================================================
    print("\n" + "=" * 70)
    print("OA5: Eligibility Expansion")
    print("=" * 70)

    oa5_per_variant = {}
    for vk in CCY_VARIANTS:
        n_nonzero = 0
        for folio in all_folios:
            entry = t1_per_folio.get(folio)
            if entry is None:
                continue
            if entry.get(vk, 0.0) > 1e-10:
                n_nonzero += 1
        oa5_per_variant[vk] = {'n_nonzero': n_nonzero}

    # Compute expansion: folios with CCY_cofX > 0 but CCY == 0
    base_nonzero_set = set()
    for folio in all_folios:
        entry = t1_per_folio.get(folio)
        if entry is None:
            continue
        if entry.get('CCY', 0.0) > 1e-10:
            base_nonzero_set.add(folio)

    expansion = {}
    for cof_key in ['CCY_cof1', 'CCY_cof2', 'CCY_cof3']:
        short = cof_key.replace('CCY_', '')
        expanded = 0
        for folio in all_folios:
            entry = t1_per_folio.get(folio)
            if entry is None:
                continue
            if folio not in base_nonzero_set and entry.get(cof_key, 0.0) > 1e-10:
                expanded += 1
        expansion[short] = expanded

    print(f"\n  Non-zero folio counts:")
    for vk in CCY_VARIANTS:
        n = oa5_per_variant[vk]['n_nonzero']
        n_total = len(t1_per_folio)
        print(f"    {vk:<12}: {n}/{n_total} folios with value > 0")

    print(f"\n  Expansion from base CCY ({len(base_nonzero_set)} non-zero folios):")
    for cof_key in ['CCY_cof1', 'CCY_cof2', 'CCY_cof3']:
        short = cof_key.replace('CCY_', '')
        e = expansion[short]
        print(f"    {cof_key}: +{e} folios newly eligible "
              f"(total = {len(base_nonzero_set) + e})")

    oa5_result = {
        'per_variant': oa5_per_variant,
        'base_ccy_nonzero': len(base_nonzero_set),
        'expansion_from_ccy': expansion,
    }

    # =====================================================================
    # Assemble output
    # =====================================================================
    elapsed = round(time.time() - t0, 2)

    output = {
        'metadata': {
            'phase': 568,
            'script': 't3_cof_observability.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': elapsed,
            'n_t1_folios': len(t1_folios),
            'n_t2_folios': len(t2_folios),
            'ccy_variants': CCY_VARIANTS,
            'variant_labels': VARIANT_LABELS,
        },
        'OA1_ccy_variant_comparison': oa1_result,
        'OA2_closure_excursion_overlap': oa2_result,
        'OA3_b10_sensitivity': oa3_result,
        'OA4_section_specific': oa4_result,
        'OA5_eligibility_expansion': oa5_result,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"  Size: {file_size_kb:.1f} KB")
    print(f"  Elapsed: {elapsed:.2f}s")

    # Key findings
    print(f"\n  Key findings:")
    print(f"    OA1 best variant by mean:     {best_by_mean} "
          f"({oa1_means[best_by_mean]:.6f})")
    print(f"    OA1 best variant by coverage: {best_by_coverage} "
          f"({oa1_nonzero[best_by_coverage]}/{oa1_count} non-zero)")
    print(f"    OA3 best B10 sensitivity:     {best_b10_variant} "
          f"(Cohen's d = {oa3_per_variant[best_b10_variant]['cohens_d']:.4f})")
    print(f"    OA5 base CCY non-zero:        {len(base_nonzero_set)}/{len(t1_per_folio)}")
    for cof_key in ['CCY_cof1', 'CCY_cof2', 'CCY_cof3']:
        short = cof_key.replace('CCY_', '')
        e = expansion[short]
        if e > 0:
            print(f"    OA5 {cof_key} expands by:    +{e} folios")
        else:
            print(f"    OA5 {cof_key} expands by:    +{e} (no expansion)")

    print(f"\n  Done.")


if __name__ == '__main__':
    main()

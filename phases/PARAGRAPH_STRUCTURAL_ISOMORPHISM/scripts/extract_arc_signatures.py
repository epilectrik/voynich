"""
Phase 624: PARAGRAPH_STRUCTURAL_ISOMORPHISM -- Script 1: Arc Signature Extraction

Extracts 27-dimensional arc signatures from Currier B paragraphs with >= 6 body
lines. Each paragraph's body is divided into three positional bins (OPEN,
INTERIOR, CLOSE) and 9 features are computed per bin, yielding a 27-dim vector
that captures the paragraph's internal instructional arc.

Also extracts:
  - 18-dim short arc signatures for paragraphs with 4-5 body lines
  - Header features for each eligible paragraph
  - PCA on section-residualized arc matrix
  - Diagnostic checks for C1836 (gradient), C1837 (anti-parallel), C1206 (kernel)

Output: phases/PARAGRAPH_STRUCTURAL_ISOMORPHISM/results/arc_signatures.json
"""

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Import shared utilities from the phase's shared module
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.PARAGRAPH_STRUCTURAL_ISOMORPHISM.scripts.shared_624 import (
    build_corpus,
    extract_arc_signature,
    extract_short_arc_signature,
    extract_header_features,
    z_normalize,
    pca_reduce,
    cosine_similarity,
    section_residualize,
    round_floats,
    MIN_BODY_LINES,
    MIN_BODY_LINES_SHORT,
    RESULTS_DIR,
    RNG,
    ARC_FEATURE_NAMES,
    BIN_NAMES,
)


# ============================================================
# Statistical helpers
# ============================================================

def _rank(values):
    """Assign ranks to values (average rank for ties)."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and values[indexed[j + 1]] == values[indexed[j]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(x, y):
    """Spearman rank correlation as Pearson on ranks (average ties)."""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)
    n = len(x)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    sx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    sy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 624, Script 1: Arc Signature Extraction")
    print("=" * 55)

    # ---- Step 1: Build corpus ----
    print("\n[1/10] Building corpus...")
    corpus = build_corpus()
    n_folios = len(corpus)
    total_b_paragraphs = sum(len(fdata['paragraphs']) for fdata in corpus.values())
    print(f"  {n_folios} folios, {total_b_paragraphs} total B paragraphs")

    # ---- Step 2: Collect eligible paragraphs (>= 6 body lines) ----
    print(f"\n[2/10] Extracting arc signatures (min_body={MIN_BODY_LINES})...")
    eligible = []
    all_paragraphs_meta = []  # Track all paragraphs for exclusion stats
    per_section_total = defaultdict(int)
    per_section_eligible = defaultdict(int)

    for folio in sorted(corpus.keys()):
        fdata = corpus[folio]
        section = fdata['section']
        regime = fdata['regime']
        for ordinal, para in enumerate(fdata['paragraphs']):
            n_body = len(para['body_lines'])
            per_section_total[section] += 1
            all_paragraphs_meta.append({
                'folio': folio,
                'section': section,
                'n_body': n_body,
            })

            if n_body < MIN_BODY_LINES:
                continue

            # Extract 27-dim arc signature
            arc_vector, arc_meta = extract_arc_signature(para, min_body=MIN_BODY_LINES)
            if arc_vector is None:
                continue

            # Extract header features
            hdr_vector, hdr_meta = extract_header_features(para)

            par_id = f"{folio}_{para['id']}"
            per_section_eligible[section] += 1

            # Package header features for output
            header_out = None
            if hdr_vector is not None:
                header_out = {
                    'vector': hdr_vector,
                    'gallows_type': hdr_meta.get('gallows_type', 'none'),
                    'prefix_composition': hdr_meta.get('prefix_composition', {}),
                }

            eligible.append({
                'par_id': par_id,
                'folio': folio,
                'section': section,
                'regime': regime,
                'n_body_lines': n_body,
                'ordinal': ordinal,
                'raw_vector': arc_vector,
                'header_features': header_out,
            })

    n_eligible = len(eligible)
    exclusion_rate = 1.0 - (n_eligible / total_b_paragraphs) if total_b_paragraphs > 0 else 0.0

    print(f"  Eligible: {n_eligible} / {total_b_paragraphs} "
          f"(exclusion rate: {exclusion_rate:.3f})")

    # Per-section breakdown
    per_section_info = {}
    for sec in sorted(per_section_total.keys()):
        total_s = per_section_total[sec]
        elig_s = per_section_eligible.get(sec, 0)
        exc_s = 1.0 - (elig_s / total_s) if total_s > 0 else 0.0
        per_section_info[sec] = {
            'eligible': elig_s,
            'total': total_s,
            'exclusion_rate': exc_s,
        }
        print(f"  Section {sec}: {elig_s}/{total_s} eligible "
              f"(exclusion: {exc_s:.3f})")

    # Check if we need to relax threshold
    if n_eligible < 80:
        relaxed_count = sum(
            1 for m in all_paragraphs_meta if m['n_body'] >= 5
        )
        print(f"\n  WARNING: Only {n_eligible} eligible paragraphs "
              f"(below 80 threshold).")
        print(f"  Relaxing to >= 5 body lines would yield {relaxed_count} "
              f"paragraphs (reduced reliability).")

    if n_eligible < 10:
        print("  ERROR: Too few paragraphs for analysis. Aborting.")
        return

    # ---- Step 3: Report metadata ----
    print(f"\n[3/10] Building metadata...")
    metadata = {
        'total_b_paragraphs': total_b_paragraphs,
        'eligible_count': n_eligible,
        'exclusion_rate': exclusion_rate,
        'min_body_lines': MIN_BODY_LINES,
        'per_section': per_section_info,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    # ---- Step 4: Diagnostic checks ----
    print("\n[4/10] Running diagnostic checks...")

    # 4a. Feature means per bin (verify C1836 gradient)
    n_features_per_bin = len(ARC_FEATURE_NAMES)
    feature_means_by_bin = {}
    for b_idx, bin_name in enumerate(BIN_NAMES):
        bin_means = [0.0] * n_features_per_bin
        for entry in eligible:
            for f_idx in range(n_features_per_bin):
                dim_idx = b_idx * n_features_per_bin + f_idx
                bin_means[f_idx] += entry['raw_vector'][dim_idx]
        bin_means = [v / n_eligible for v in bin_means]
        feature_means_by_bin[bin_name] = bin_means

    print("  Feature means by bin:")
    print(f"    {'Feature':22s}  {'OPEN':>8s}  {'INTERIOR':>8s}  {'CLOSE':>8s}")
    for f_idx, fname in enumerate(ARC_FEATURE_NAMES):
        vals = [feature_means_by_bin[bn][f_idx] for bn in BIN_NAMES]
        print(f"    {fname:22s}  {vals[0]:8.4f}  {vals[1]:8.4f}  {vals[2]:8.4f}")

    # 4b. OPEN vs CLOSE cosine similarity (verify C1837 anti-parallel)
    open_close_cosines = []
    for entry in eligible:
        vec = entry['raw_vector']
        open_vec = vec[:n_features_per_bin]
        close_vec = vec[2 * n_features_per_bin:]
        # Check that bin vectors are non-trivial before computing cosine
        open_norm = math.sqrt(sum(v * v for v in open_vec))
        close_norm = math.sqrt(sum(v * v for v in close_vec))
        if open_norm > 1e-12 and close_norm > 1e-12:
            cs = cosine_similarity(open_vec, close_vec)
            open_close_cosines.append(cs)

    if open_close_cosines:
        oc_mean = sum(open_close_cosines) / len(open_close_cosines)
        oc_std = math.sqrt(
            sum((v - oc_mean) ** 2 for v in open_close_cosines)
            / len(open_close_cosines)
        )
    else:
        oc_mean = 0.0
        oc_std = 0.0

    print(f"\n  OPEN vs CLOSE cosine similarity:")
    print(f"    Mean: {oc_mean:.4f}  Std: {oc_std:.4f}")
    if oc_mean < 0:
        print("    -> Confirms C1837 anti-parallel pattern (negative cosine)")
    else:
        print("    -> Does NOT confirm C1837 (cosine non-negative)")

    # 4c. Kernel gradient: log_ke_ratio and h_rate means by bin (verify C1206)
    # Identify indices for log_ke_ratio and h_rate in ARC_FEATURE_NAMES
    log_ke_idx = None
    h_rate_idx = None
    for f_idx, fname in enumerate(ARC_FEATURE_NAMES):
        if fname == 'log_ke_ratio':
            log_ke_idx = f_idx
        elif fname == 'h_rate':
            h_rate_idx = f_idx

    kernel_gradient = {}
    if log_ke_idx is not None:
        kernel_gradient['log_ke_ratio'] = {}
        for b_idx, bin_name in enumerate(BIN_NAMES):
            kernel_gradient['log_ke_ratio'][bin_name] = \
                feature_means_by_bin[bin_name][log_ke_idx]
        print(f"\n  Kernel gradient (log_ke_ratio):")
        for bn in BIN_NAMES:
            print(f"    {bn}: {kernel_gradient['log_ke_ratio'][bn]:.4f}")

    if h_rate_idx is not None:
        kernel_gradient['h_rate'] = {}
        for b_idx, bin_name in enumerate(BIN_NAMES):
            kernel_gradient['h_rate'][bin_name] = \
                feature_means_by_bin[bin_name][h_rate_idx]
        print(f"\n  Kernel gradient (h_rate):")
        for bn in BIN_NAMES:
            print(f"    {bn}: {kernel_gradient['h_rate'][bn]:.4f}")

    diagnostics = {
        'feature_means_by_bin': feature_means_by_bin,
        'open_close_cosine_mean': oc_mean,
        'open_close_cosine_std': oc_std,
        'kernel_gradient': kernel_gradient,
    }

    # ---- Step 5: Z-normalize all 27 dimensions ----
    print("\n[5/10] Z-normalizing arc signatures...")
    raw_vectors = [e['raw_vector'] for e in eligible]
    z_vectors, z_means, z_stds = z_normalize(raw_vectors)

    # Store z-normalized vectors
    for i, entry in enumerate(eligible):
        entry['z_normalized'] = z_vectors[i]

    n_zero_var = sum(1 for s in z_stds if s < 1e-12)
    print(f"  Z-normalized {n_eligible} vectors x 27 dims")
    if n_zero_var > 0:
        print(f"  WARNING: {n_zero_var} dimensions with near-zero variance")

    # ---- Step 6: Length confound check ----
    print("\n[6/10] Length confound check (Spearman with PC scores)...")
    # We'll do PCA first on z-normalized to check length, then redo on residualized

    # Quick preliminary PCA on z-normalized for length check
    prelim_reduced, prelim_eigvals, prelim_eigvecs, prelim_cumvar, prelim_ncomp = \
        pca_reduce(z_vectors, variance_threshold=0.90)

    lengths = [e['n_body_lines'] for e in eligible]
    length_pc_corr = {'length_dominates': False}

    if prelim_reduced and len(prelim_reduced[0]) >= 1:
        pc1_scores = [row[0] for row in prelim_reduced]
        rho1 = spearman_rho(lengths, pc1_scores)
        length_pc_corr['pc1_rho'] = rho1
        print(f"  PC1 vs n_body_lines: Spearman rho = {rho1:.4f}")
        if abs(rho1) > 0.30:
            print(f"    -> FLAG: |rho| > 0.30 -- length may confound PC1")
            length_pc_corr['length_dominates'] = True

        if len(prelim_reduced[0]) >= 2:
            pc2_scores = [row[1] for row in prelim_reduced]
            rho2 = spearman_rho(lengths, pc2_scores)
            length_pc_corr['pc2_rho'] = rho2
            print(f"  PC2 vs n_body_lines: Spearman rho = {rho2:.4f}")
            if abs(rho2) > 0.30:
                print(f"    -> FLAG: |rho| > 0.30 -- length may confound PC2")
                if not length_pc_corr['length_dominates']:
                    length_pc_corr['length_dominates'] = True
        else:
            length_pc_corr['pc2_rho'] = 0.0
    else:
        length_pc_corr['pc1_rho'] = 0.0
        length_pc_corr['pc2_rho'] = 0.0
        print("  WARNING: PCA produced insufficient components for length check")

    diagnostics['length_pc_correlation'] = length_pc_corr

    # ---- Step 7: Section-residualize ----
    print("\n[7/10] Section-residualizing...")
    section_labels = [e['section'] for e in eligible]
    residualized_vectors, section_means = section_residualize(
        z_vectors, section_labels
    )

    # Store residualized vectors
    for i, entry in enumerate(eligible):
        entry['section_residualized'] = residualized_vectors[i]

    print(f"  Section means computed for: {sorted(section_means.keys())}")
    for sec, mean_vec in sorted(section_means.items()):
        norm = math.sqrt(sum(v ** 2 for v in mean_vec))
        print(f"    {sec}: ||mean|| = {norm:.4f}")

    # ---- Step 8: PCA on section-residualized matrix ----
    print("\n[8/10] PCA on section-residualized arc signatures...")
    reduced, eigenvalues, eigenvectors, cumvar, n_components = \
        pca_reduce(residualized_vectors, variance_threshold=0.90)

    # PC scores for output
    pc_scores = reduced if reduced else []

    if eigenvalues:
        print(f"  Eigenvalues (top 10): "
              f"{[round(e, 4) for e in eigenvalues[:10]]}")
        print(f"  Cumulative variance (top 10): "
              f"{[round(c, 4) for c in cumvar[:10]]}")
        print(f"  Components at 90%: {n_components}")

        # Effective dimensionality: exp(entropy of normalized eigenvalues)
        total_var = sum(eigenvalues)
        if total_var > 0:
            normed = [e / total_var for e in eigenvalues if e > 0]
            entropy = -sum(p * math.log(p) for p in normed if p > 0)
            eff_dim = math.exp(entropy)
            print(f"  Effective dimensionality: {eff_dim:.2f}")
        else:
            eff_dim = 0.0
    else:
        print("  WARNING: PCA produced no eigenvalues")
        eff_dim = 0.0

    # ---- Step 9: Short-paragraph extraction (4-5 body lines) ----
    print(f"\n[9/10] Extracting short arc signatures "
          f"(body lines {MIN_BODY_LINES_SHORT}-{MIN_BODY_LINES - 1})...")
    short_paragraphs = []

    for folio in sorted(corpus.keys()):
        fdata = corpus[folio]
        section = fdata['section']
        for para in fdata['paragraphs']:
            n_body = len(para['body_lines'])
            if n_body < MIN_BODY_LINES_SHORT or n_body >= MIN_BODY_LINES:
                continue

            short_vector, short_meta = extract_short_arc_signature(
                para, min_body=MIN_BODY_LINES_SHORT
            )
            if short_vector is None:
                continue

            par_id = f"{folio}_{para['id']}"
            short_paragraphs.append({
                'par_id': par_id,
                'folio': folio,
                'section': section,
                'n_body_lines': n_body,
                'boundary_interior_vector': short_vector,
            })

    print(f"  Short paragraphs extracted: {len(short_paragraphs)}")

    # ---- Step 10: Header feature extraction ----
    # (Already extracted in step 2, stored in eligible entries)
    print("\n[10/10] Header features already extracted for all eligible paragraphs.")
    n_with_headers = sum(
        1 for e in eligible
        if e['header_features'] is not None
    )
    print(f"  Paragraphs with header features: {n_with_headers}/{n_eligible}")

    # ============================================================
    # Assemble output JSON
    # ============================================================
    print("\nAssembling output...")

    # Build paragraph entries
    paragraph_entries = []
    for i, entry in enumerate(eligible):
        par_entry = {
            'par_id': entry['par_id'],
            'folio': entry['folio'],
            'section': entry['section'],
            'regime': entry['regime'],
            'n_body_lines': entry['n_body_lines'],
            'ordinal': entry['ordinal'],
            'raw_vector': entry['raw_vector'],
            'z_normalized': entry['z_normalized'],
            'section_residualized': entry['section_residualized'],
            'header_features': entry['header_features'],
        }
        paragraph_entries.append(par_entry)

    # Build short paragraph entries
    short_entries = []
    for sp in short_paragraphs:
        short_entries.append({
            'par_id': sp['par_id'],
            'folio': sp['folio'],
            'section': sp['section'],
            'n_body_lines': sp['n_body_lines'],
            'boundary_interior_vector': sp['boundary_interior_vector'],
        })

    # Build PCA output
    pca_output = {
        'eigenvalues': list(eigenvalues) if eigenvalues else [],
        'cumulative_variance': list(cumvar) if cumvar else [],
        'n_components': n_components,
        'effective_dimensionality': eff_dim,
        'pc_scores': [list(row) for row in pc_scores] if pc_scores else [],
    }

    # Build section means output
    section_means_output = {
        sec: list(vec) for sec, vec in section_means.items()
    }

    output = {
        'metadata': metadata,
        'diagnostics': diagnostics,
        'paragraphs': paragraph_entries,
        'short_paragraphs': short_entries,
        'pca': pca_output,
        'section_means': section_means_output,
        'z_means': list(z_means),
        'z_stds': list(z_stds),
    }

    # Round all floats
    output = round_floats(output)

    # Write output
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'arc_signatures.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    # ============================================================
    # Summary table
    # ============================================================
    print("\n" + "=" * 55)
    print("SUMMARY")
    print("=" * 55)
    print(f"  Total B paragraphs:       {total_b_paragraphs}")
    print(f"  Eligible (>= {MIN_BODY_LINES} body):    {n_eligible}")
    print(f"  Exclusion rate:            {exclusion_rate:.3f}")
    print(f"  Short (4-5 body):          {len(short_paragraphs)}")
    print(f"  Arc dimensions:            27 (3 bins x {n_features_per_bin} features)")
    print(f"  PCA components at 90%:     {n_components}")
    if eigenvalues:
        print(f"  Effective dimensionality:  {eff_dim:.2f}")
    print(f"  OPEN-CLOSE cosine (mean):  {oc_mean:.4f}")
    print(f"  Length confound (PC1):     rho={length_pc_corr.get('pc1_rho', 0):.4f}")
    print(f"  Length confound (PC2):     rho={length_pc_corr.get('pc2_rho', 0):.4f}")
    print(f"  Length dominates:          {length_pc_corr.get('length_dominates', False)}")

    # Per-section summary
    print("\n  Per-section breakdown:")
    for sec in sorted(per_section_info.keys()):
        info = per_section_info[sec]
        print(f"    {sec}: {info['eligible']}/{info['total']} "
              f"(excl: {info['exclusion_rate']:.3f})")

    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()

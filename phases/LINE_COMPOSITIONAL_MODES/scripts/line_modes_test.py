"""
LINE_COMPOSITIONAL_MODES: Phase 431
=====================================
Investigates why tokens on the same line share MEDIAL atoms beyond what
sequential order explains (C1212: MEDIAL->MEDIAL z=3.4, 80% co-occurrence).

Context:
  - C1207: 5-6 atom correlation clusters (axes)
  - C1212: Within-line MEDIAL co-occurrence >> sequential structure
  - C1213: Axis switching 84.8% between tokens
  - C1206: Paragraph kernel gradient (h declines, k/e rises)
  - C678:  No discrete line types (silhouette=0.100)
  - C909:  96% of MIDDLEs are section-specific

Tests:
  T1:  Line axis profiles via PCA (continuous characterization)
  T2:  Line MEDIAL homogeneity (within-folio shuffle baseline)
  T3:  Line position effects (position within paragraph/folio)
  T4:  Slot-specific homogeneity (INITIAL vs MEDIAL vs TERMINAL)
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/LINE_COMPOSITIONAL_MODES/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# C1207 axis classification
AXIS_MAP = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE_T', 'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER',
    'q': 'OTHER', 'g': 'OTHER', 'x': 'OTHER',
}

AXES = ['ITERATION', 'MONITORING', 'ENERGY', 'CLOSURE', 'STRUCTURAL', 'STABILITY', 'FREE_T', 'OTHER']

N_SHUFFLES = 1000


# ============================================================
# DATA LOADING
# ============================================================

def load_lines():
    """Load Currier B tokens grouped by (folio, line) with atom decomposition."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_' and len(m.middle) >= 2:
            line_groups[(t.folio, t.line)].append({
                'word': t.word,
                'middle': m.middle,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'initial': m.middle[0],
                'terminal': m.middle[-1],
                'medial': m.middle[1] if len(m.middle) >= 3 else None,
                'is_daiin': m.middle == 'iin',
            })
    return line_groups


def line_axis_profile(tokens, slot='medial'):
    """Compute axis fraction vector for a line's tokens at the given slot."""
    counts = Counter()
    total = 0
    for t in tokens:
        atom = t.get(slot)
        if atom is None:
            continue
        axis = AXIS_MAP.get(atom, 'OTHER')
        counts[axis] += 1
        total += 1
    if total == 0:
        return None, 0
    return {ax: counts.get(ax, 0) / total for ax in AXES}, total


def entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


# ============================================================
# T1: LINE AXIS PROFILES VIA PCA
# ============================================================

def test_axis_profiles(line_groups):
    """Compute per-line axis profiles and do manual PCA."""
    print(f"\n{'='*70}")
    print("T1: LINE AXIS PROFILES (PCA on MEDIAL atom axis fractions)")
    print("=" * 70)

    # Build profile matrix
    profiles = []  # list of (key, section, profile_dict, n_tokens)
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        prof, n = line_axis_profile(tokens, slot='medial')
        if prof is not None and n >= 3:
            sec = tokens[0]['section']
            profiles.append((key, sec, prof, n))

    print(f"  Lines with >= 3 MEDIAL atoms: {len(profiles)}")

    # Convert to vectors
    vectors = []
    for _, _, prof, _ in profiles:
        vectors.append([prof[ax] for ax in AXES])

    # Center the data
    n_dim = len(AXES)
    means = [sum(v[i] for v in vectors) / len(vectors) for i in range(n_dim)]
    centered = [[v[i] - means[i] for i in range(n_dim)] for v in vectors]

    # Covariance matrix
    n = len(centered)
    cov = [[0.0] * n_dim for _ in range(n_dim)]
    for i in range(n_dim):
        for j in range(n_dim):
            cov[i][j] = sum(c[i] * c[j] for c in centered) / (n - 1)

    # Power iteration for top 2 eigenvectors
    def power_iteration(matrix, n_iter=200):
        dim = len(matrix)
        v = [random.gauss(0, 1) for _ in range(dim)]
        norm = sum(x**2 for x in v) ** 0.5
        v = [x / norm for x in v]
        for _ in range(n_iter):
            new_v = [sum(matrix[i][j] * v[j] for j in range(dim)) for i in range(dim)]
            eigenval = sum(new_v[i] * v[i] for i in range(dim))
            norm = sum(x**2 for x in new_v) ** 0.5
            if norm > 0:
                v = [x / norm for x in new_v]
        eigenval = sum(sum(cov[i][j] * v[j] for j in range(dim)) * v[i] for i in range(dim))
        return eigenval, v

    random.seed(42)
    eval1, evec1 = power_iteration(cov)

    # Deflate for PC2
    cov2 = [[cov[i][j] - eval1 * evec1[i] * evec1[j] for j in range(n_dim)] for i in range(n_dim)]
    eval2, evec2 = power_iteration(cov2)

    total_var = sum(cov[i][i] for i in range(n_dim))
    pct1 = eval1 / total_var * 100 if total_var > 0 else 0
    pct2 = eval2 / total_var * 100 if total_var > 0 else 0

    print(f"\n  PCA on {n_dim}-axis profile vectors:")
    print(f"    PC1: {pct1:.1f}% variance explained (eigenvalue={eval1:.4f})")
    print(f"    PC2: {pct2:.1f}% variance explained (eigenvalue={eval2:.4f})")
    print(f"    PC1+PC2: {pct1+pct2:.1f}%")

    print(f"\n  PC1 loadings (what drives the main axis of variation):")
    loadings1 = sorted(zip(AXES, evec1), key=lambda x: -abs(x[1]))
    for ax, load in loadings1:
        bar = '+' * int(abs(load) * 40) if load > 0 else '-' * int(abs(load) * 40)
        print(f"    {ax:>12}: {load:>+.3f} {bar}")

    print(f"\n  PC2 loadings:")
    loadings2 = sorted(zip(AXES, evec2), key=lambda x: -abs(x[1]))
    for ax, load in loadings2:
        bar = '+' * int(abs(load) * 40) if load > 0 else '-' * int(abs(load) * 40)
        print(f"    {ax:>12}: {load:>+.3f} {bar}")

    # Section mean profiles
    section_profiles = defaultdict(lambda: Counter())
    section_counts = Counter()
    for _, sec, prof, n in profiles:
        for ax in AXES:
            section_profiles[sec][ax] += prof[ax] * n
        section_counts[sec] += n

    print(f"\n  Section mean axis profiles (MEDIAL):")
    print(f"    {'Section':>8}  " + "".join(f"{ax[:8]:>10}" for ax in AXES))
    for sec in sorted(section_profiles.keys()):
        total_n = section_counts[sec]
        row = f"    {sec:>8}  "
        for ax in AXES:
            frac = section_profiles[sec][ax] / total_n if total_n > 0 else 0
            row += f"{frac:>10.3f}"
        print(row)

    # Compute between-section vs within-section variance
    # Project each line onto PC1, compute section means, compare
    pc1_scores = [sum(centered[i][j] * evec1[j] for j in range(n_dim))
                  for i in range(len(profiles))]

    section_pc1 = defaultdict(list)
    for idx, (_, sec, _, _) in enumerate(profiles):
        section_pc1[sec].append(pc1_scores[idx])

    grand_mean = sum(pc1_scores) / len(pc1_scores)
    ss_between = sum(len(vals) * (sum(vals)/len(vals) - grand_mean)**2
                     for vals in section_pc1.values())
    ss_total = sum((s - grand_mean)**2 for s in pc1_scores)
    r2_section = ss_between / ss_total if ss_total > 0 else 0

    print(f"\n  Section explains {r2_section:.1%} of PC1 variance")

    return {
        'n_lines': len(profiles),
        'pc1_var_pct': round(pct1, 1),
        'pc2_var_pct': round(pct2, 1),
        'pc1_loadings': {ax: round(l, 4) for ax, l in zip(AXES, evec1)},
        'pc2_loadings': {ax: round(l, 4) for ax, l in zip(AXES, evec2)},
        'section_r2_pc1': round(r2_section, 4),
    }


# ============================================================
# T2: LINE MEDIAL HOMOGENEITY
# ============================================================

def test_homogeneity(line_groups):
    """Test whether lines are more MEDIAL-homogeneous than within-folio shuffled."""
    print(f"\n{'='*70}")
    print("T2: LINE MEDIAL HOMOGENEITY (within-folio shuffle baseline)")
    print("=" * 70)

    # Compute observed per-line MEDIAL entropy, normalized by line length
    line_data = []  # (key, section, folio, medial_atoms, entropy, max_entropy)
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        medials = [t['medial'] for t in tokens if t['medial'] is not None]
        if len(medials) < 3:
            continue
        counts = Counter(medials)
        h = entropy(counts)
        max_h = math.log2(len(medials))  # max entropy if all unique
        norm_h = h / max_h if max_h > 0 else 0
        folio = tokens[0]['folio']
        sec = tokens[0]['section']
        line_data.append({
            'key': key,
            'section': sec,
            'folio': folio,
            'medials': medials,
            'entropy': h,
            'norm_entropy': norm_h,
            'n_medials': len(medials),
        })

    obs_mean_entropy = sum(d['norm_entropy'] for d in line_data) / len(line_data)
    print(f"  Lines with >= 3 MEDIAL atoms: {len(line_data)}")
    print(f"  Observed mean normalized entropy: {obs_mean_entropy:.4f}")

    # Group medial atoms by folio for within-folio shuffle
    folio_medials = defaultdict(list)  # folio -> [(line_key, medial_atom), ...]
    for d in line_data:
        for m in d['medials']:
            folio_medials[d['folio']].append((d['key'], m))

    # Shuffle: reassign medial atoms across lines within same folio
    random.seed(42)
    shuf_entropies = []
    for s in range(N_SHUFFLES):
        shuf_line_atoms = defaultdict(list)  # line_key -> [atoms]
        for folio, items in folio_medials.items():
            atoms = [a for _, a in items]
            keys = [k for k, _ in items]
            random.shuffle(atoms)
            for k, a in zip(keys, atoms):
                shuf_line_atoms[k].append(a)

        # Compute entropy for each shuffled line
        entropies = []
        for d in line_data:
            atoms = shuf_line_atoms[d['key']]
            if len(atoms) < 3:
                continue
            counts = Counter(atoms)
            h = entropy(counts)
            max_h = math.log2(len(atoms))
            norm_h = h / max_h if max_h > 0 else 0
            entropies.append(norm_h)
        if entropies:
            shuf_entropies.append(sum(entropies) / len(entropies))

    shuf_mean = sum(shuf_entropies) / len(shuf_entropies)
    shuf_std = (sum((e - shuf_mean)**2 for e in shuf_entropies) / len(shuf_entropies)) ** 0.5
    z = (obs_mean_entropy - shuf_mean) / shuf_std if shuf_std > 0 else 0

    print(f"  Shuffle mean normalized entropy: {shuf_mean:.4f}")
    print(f"  Shuffle std: {shuf_std:.4f}")
    print(f"  Z-score: {z:.2f}")
    if z < -2:
        print(f"  -> Lines are MORE homogeneous than shuffled (z={z:.1f})")
    elif z > 2:
        print(f"  -> Lines are LESS homogeneous than shuffled (z={z:.1f})")
    else:
        print(f"  -> No significant difference from shuffled")

    # Effect size
    reduction = (shuf_mean - obs_mean_entropy) / shuf_mean * 100 if shuf_mean > 0 else 0
    print(f"  Entropy reduction: {reduction:.1f}% below shuffled baseline")

    # Per-axis homogeneity: which axes drive the effect?
    print(f"\n  Per-axis within-line concentration (obs vs shuffled):")
    axis_obs = Counter()
    axis_total = 0
    for d in line_data:
        line_axis_counts = Counter()
        for m in d['medials']:
            ax = AXIS_MAP.get(m, 'OTHER')
            line_axis_counts[ax] += 1
        # Concentration = max fraction
        n = len(d['medials'])
        for ax, ct in line_axis_counts.items():
            axis_obs[ax] += ct
        axis_total += n

    # Daiin exclusion variant
    line_data_no_daiin = []
    for key in sorted(line_groups.keys()):
        tokens = [t for t in line_groups[key] if not t['is_daiin']]
        medials = [t['medial'] for t in tokens if t['medial'] is not None]
        if len(medials) < 3:
            continue
        counts = Counter(medials)
        h = entropy(counts)
        max_h = math.log2(len(medials))
        norm_h = h / max_h if max_h > 0 else 0
        folio = tokens[0]['folio'] if tokens else ''
        line_data_no_daiin.append({
            'key': key,
            'folio': folio,
            'medials': medials,
            'norm_entropy': norm_h,
        })

    if line_data_no_daiin:
        obs_no_daiin = sum(d['norm_entropy'] for d in line_data_no_daiin) / len(line_data_no_daiin)

        folio_medials_nd = defaultdict(list)
        for d in line_data_no_daiin:
            for m in d['medials']:
                folio_medials_nd[d['folio']].append((d['key'], m))

        shuf_nd = []
        for s in range(N_SHUFFLES):
            shuf_line_atoms = defaultdict(list)
            for folio, items in folio_medials_nd.items():
                atoms = [a for _, a in items]
                keys = [k for k, _ in items]
                random.shuffle(atoms)
                for k, a in zip(keys, atoms):
                    shuf_line_atoms[k].append(a)
            entropies = []
            for d in line_data_no_daiin:
                atoms = shuf_line_atoms[d['key']]
                if len(atoms) < 3:
                    continue
                counts = Counter(atoms)
                h_val = entropy(counts)
                max_h = math.log2(len(atoms))
                norm_h = h_val / max_h if max_h > 0 else 0
                entropies.append(norm_h)
            if entropies:
                shuf_nd.append(sum(entropies) / len(entropies))

        shuf_nd_mean = sum(shuf_nd) / len(shuf_nd)
        shuf_nd_std = (sum((e - shuf_nd_mean)**2 for e in shuf_nd) / len(shuf_nd)) ** 0.5
        z_nd = (obs_no_daiin - shuf_nd_mean) / shuf_nd_std if shuf_nd_std > 0 else 0
        print(f"\n  daiin-excluded: obs={obs_no_daiin:.4f}, shuf={shuf_nd_mean:.4f}, z={z_nd:.2f}")

    return {
        'n_lines': len(line_data),
        'obs_mean_norm_entropy': round(obs_mean_entropy, 4),
        'shuf_mean_norm_entropy': round(shuf_mean, 4),
        'z_score': round(z, 2),
        'entropy_reduction_pct': round(reduction, 1),
        'daiin_excluded_z': round(z_nd, 2) if line_data_no_daiin else None,
    }


# ============================================================
# T3: LINE POSITION EFFECTS
# ============================================================

def test_position_effects(line_groups):
    """Test whether line axis profiles depend on position within folio."""
    print(f"\n{'='*70}")
    print("T3: LINE POSITION EFFECTS (axis profile vs line position)")
    print("=" * 70)

    # Group lines by folio
    folio_lines = defaultdict(list)
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        prof, n = line_axis_profile(tokens, slot='medial')
        if prof is not None and n >= 2:
            folio = key[0]
            line_num = key[1]
            sec = tokens[0]['section']
            folio_lines[folio].append({
                'line': line_num,
                'section': sec,
                'profile': prof,
                'n': n,
            })

    # For each folio, assign position quintile
    quintile_profiles = defaultdict(lambda: {ax: [] for ax in AXES})
    for folio, lines in folio_lines.items():
        if len(lines) < 5:
            continue
        lines_sorted = sorted(lines, key=lambda x: x['line'])
        n_lines = len(lines_sorted)
        for idx, line in enumerate(lines_sorted):
            q = min(int(idx / n_lines * 5), 4)  # 0-4
            for ax in AXES:
                quintile_profiles[q][ax].append(line['profile'][ax])

    print(f"\n  Axis fractions by line position quintile (0=early, 4=late):")
    print(f"    {'Quintile':>8}  " + "".join(f"{ax[:8]:>10}" for ax in AXES) + "     N")
    for q in range(5):
        n_vals = len(quintile_profiles[q][AXES[0]])
        row = f"    {q:>8}  "
        for ax in AXES:
            vals = quintile_profiles[q][ax]
            mean_val = sum(vals) / len(vals) if vals else 0
            row += f"{mean_val:>10.3f}"
        row += f"  {n_vals:>5}"
        print(row)

    # Compute correlation of each axis with position
    print(f"\n  Axis vs position correlation (Pearson r):")
    results = {}
    for ax in AXES:
        all_pos = []
        all_vals = []
        for q in range(5):
            for v in quintile_profiles[q][ax]:
                all_pos.append(q)
                all_vals.append(v)
        if len(all_pos) < 10:
            continue
        mean_p = sum(all_pos) / len(all_pos)
        mean_v = sum(all_vals) / len(all_vals)
        cov_pv = sum((p - mean_p) * (v - mean_v) for p, v in zip(all_pos, all_vals)) / len(all_pos)
        std_p = (sum((p - mean_p)**2 for p in all_pos) / len(all_pos)) ** 0.5
        std_v = (sum((v - mean_v)**2 for v in all_vals) / len(all_vals)) ** 0.5
        r = cov_pv / (std_p * std_v) if std_p > 0 and std_v > 0 else 0
        print(f"    {ax:>12}: r={r:>+.3f}")
        results[ax] = round(r, 4)

    return {
        'quintile_n': {q: len(quintile_profiles[q][AXES[0]]) for q in range(5)},
        'position_correlations': results,
    }


# ============================================================
# T4: SLOT-SPECIFIC HOMOGENEITY
# ============================================================

def test_slot_homogeneity(line_groups):
    """Compare within-line homogeneity across INITIAL, MEDIAL, and TERMINAL slots."""
    print(f"\n{'='*70}")
    print("T4: SLOT-SPECIFIC HOMOGENEITY (INITIAL vs MEDIAL vs TERMINAL)")
    print("=" * 70)

    slots = ['initial', 'medial', 'terminal']
    results = {}

    for slot in slots:
        # Compute per-line entropy for this slot
        line_data = []
        for key in sorted(line_groups.keys()):
            tokens = line_groups[key]
            atoms = [t[slot] for t in tokens if t.get(slot) is not None]
            if len(atoms) < 3:
                continue
            counts = Counter(atoms)
            h = entropy(counts)
            max_h = math.log2(len(atoms))
            norm_h = h / max_h if max_h > 0 else 0
            folio = tokens[0]['folio']
            line_data.append({
                'key': key,
                'folio': folio,
                'atoms': atoms,
                'norm_entropy': norm_h,
            })

        obs_mean = sum(d['norm_entropy'] for d in line_data) / len(line_data)

        # Within-folio shuffle
        folio_atoms = defaultdict(list)
        for d in line_data:
            for a in d['atoms']:
                folio_atoms[d['folio']].append((d['key'], a))

        random.seed(42)
        shuf_means = []
        n_shuf = 500  # fewer for speed since 3 slots
        for s in range(n_shuf):
            shuf_line_atoms = defaultdict(list)
            for folio, items in folio_atoms.items():
                atoms = [a for _, a in items]
                keys = [k for k, _ in items]
                random.shuffle(atoms)
                for k, a in zip(keys, atoms):
                    shuf_line_atoms[k].append(a)

            entropies = []
            for d in line_data:
                atoms = shuf_line_atoms[d['key']]
                if len(atoms) < 3:
                    continue
                counts = Counter(atoms)
                h = entropy(counts)
                max_h = math.log2(len(atoms))
                norm_h = h / max_h if max_h > 0 else 0
                entropies.append(norm_h)
            if entropies:
                shuf_means.append(sum(entropies) / len(entropies))

        shuf_mean = sum(shuf_means) / len(shuf_means)
        shuf_std = (sum((e - shuf_mean)**2 for e in shuf_means) / len(shuf_means)) ** 0.5
        z = (obs_mean - shuf_mean) / shuf_std if shuf_std > 0 else 0
        reduction = (shuf_mean - obs_mean) / shuf_mean * 100 if shuf_mean > 0 else 0

        print(f"\n  {slot.upper():>10}: n_lines={len(line_data)}, "
              f"obs={obs_mean:.4f}, shuf={shuf_mean:.4f}, "
              f"z={z:.2f}, reduction={reduction:.1f}%")

        results[slot] = {
            'n_lines': len(line_data),
            'obs_mean_norm_entropy': round(obs_mean, 4),
            'shuf_mean_norm_entropy': round(shuf_mean, 4),
            'z_score': round(z, 2),
            'entropy_reduction_pct': round(reduction, 1),
        }

    # Summary comparison
    print(f"\n  Summary (higher |z| = more homogeneous than shuffled):")
    for slot in slots:
        r = results[slot]
        stars = "***" if abs(r['z_score']) > 5 else "**" if abs(r['z_score']) > 3 else "*" if abs(r['z_score']) > 2 else ""
        print(f"    {slot.upper():>10}: z={r['z_score']:>6.1f}, reduction={r['entropy_reduction_pct']:.1f}% {stars}")

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("LINE_COMPOSITIONAL_MODES -- Phase 431")
    print("=" * 70)

    print("\nLoading data...")
    line_groups = load_lines()
    n_tokens = sum(len(v) for v in line_groups.values())
    n_lines = len(line_groups)
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    results = {}

    # T1: Line axis profiles
    results['T1_axis_profiles'] = test_axis_profiles(line_groups)

    # T2: Line homogeneity
    results['T2_homogeneity'] = test_homogeneity(line_groups)

    # T3: Position effects
    results['T3_position'] = test_position_effects(line_groups)

    # T4: Slot-specific homogeneity
    results['T4_slot_homogeneity'] = test_slot_homogeneity(line_groups)

    # Save
    output_path = RESULTS_DIR / "line_modes_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

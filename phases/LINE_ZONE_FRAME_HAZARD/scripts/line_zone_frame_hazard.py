"""
Phase 528: Line Zone x Frame Hazard Interaction
=================================================

The three-zone line model (C1425-C1430: SPECIFICATION -> THERMAL_WORK -> CLOSURE)
and the frame hazard map (C1448: 7 HIGH frames, k-IMMUNE, e->y ZERO) were
discovered independently. This phase tests whether they interact -- whether
the line's positional grammar routes hazardous vs safe frames to specific zones.

Tests:
  T1.  Positional hazard gradient (quintile distribution of hazard classes)
  T2.  Zone x hazard contingency (chi-squared + Cramer's V)
  T3.  Safe pathway positioning (e->y quintile profile)
  T4.  k-IMMUNE positioning (k-HEAD quintile profile)
  T5.  Per-frame positional preference (individual HIGH frame profiles)
  T6.  Line-length interaction (short vs long lines)

Output: phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json
"""

import sys
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency, spearmanr, kruskal, mannwhitneyu

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FRAME HAZARD MAP (from data/decoder_maps.json, C1448)
# ============================================================
def load_frame_hazard_map():
    """Load the frame hazard classification map."""
    path = PROJECT_ROOT / 'data' / 'decoder_maps.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    entries = data['maps']['frame_hazard']['entries']
    return {k: v['value'] for k, v in entries.items()}


# ============================================================
# DATA LOADING
# ============================================================

def load_b_tokens():
    """Load all Currier B tokens with line position and frame classification.

    Returns list of dicts with keys:
        word, folio, line_key, position_in_line, line_length,
        quintile, middle, head, mods, term, frame_str, hazard_class
    """
    tx = Transcript()
    morph = Morphology()
    frame_map = load_frame_hazard_map()

    # Group tokens by (folio, line) to compute positions
    line_groups = defaultdict(list)
    for token in tx.currier_b():
        # Skip labels, uncertain tokens
        if token.placement.startswith('L'):
            continue
        if '*' in token.word:
            continue
        w = token.word.strip()
        if not w:
            continue

        line_key = (token.folio, token.line)
        line_groups[line_key].append(token)

    # Process each line to compute positions
    all_tokens = []
    for line_key, tokens in line_groups.items():
        line_len = len(tokens)
        if line_len < 2:
            continue  # Skip degenerate lines

        for idx, tok in enumerate(tokens):
            # Fractional position [0, 1]
            frac_pos = idx / (line_len - 1) if line_len > 1 else 0.5

            # Quintile (0-4)
            quintile = min(int(frac_pos * 5), 4)

            # Morphological decomposition
            m = morph.extract(tok.word.strip())
            if not m.middle:
                continue

            # HEAD+MOD*+TERM decomposition
            head, mods, term, frame_str = decompose_middle_hmt(m.middle)

            # Frame hazard classification
            if head == 'k':
                hazard_class = 'IMMUNE'
            elif frame_str:
                hazard_class = frame_map.get(frame_str, 'LOW')
            else:
                hazard_class = 'LOW'

            all_tokens.append({
                'word': tok.word.strip(),
                'folio': tok.folio,
                'line_key': f"{tok.folio}_{tok.line}",
                'position_in_line': idx,
                'line_length': line_len,
                'frac_pos': frac_pos,
                'quintile': quintile,
                'middle': m.middle,
                'prefix': m.prefix,
                'head': head,
                'mods': mods,
                'term': term,
                'frame_str': frame_str,
                'hazard_class': hazard_class,
                'section': tok.section,
            })

    return all_tokens


def cramers_v(table):
    """Compute Cramer's V from a contingency table (numpy array)."""
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    min_dim = min(table.shape) - 1
    if min_dim == 0 or n == 0:
        return 0.0
    return math.sqrt(chi2 / (n * min_dim))


# ============================================================
# TEST FUNCTIONS
# ============================================================

def t1_positional_hazard_gradient(tokens):
    """T1: Distribution of hazard classes across quintiles.

    Tests whether hazard is uniform or concentrated at specific line positions.
    """
    print("\n=== T1: Positional Hazard Gradient ===")

    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    # Build quintile x hazard_class contingency
    counts = defaultdict(lambda: defaultdict(int))
    total_by_q = Counter()
    total_by_h = Counter()

    for t in tokens:
        q = t['quintile']
        h = t['hazard_class']
        counts[q][h] += 1
        total_by_q[q] += 1
        total_by_h[h] += 1

    N = len(tokens)

    # Print distribution
    print(f"\nTotal tokens: {N}")
    print(f"\nHazard class distribution:")
    for h in hazard_classes:
        print(f"  {h}: {total_by_h[h]} ({total_by_h[h]/N*100:.1f}%)")

    print(f"\nQuintile x Hazard Class (enrichment vs marginal):")
    print(f"{'Q':>4s}  {'N':>6s}", end='')
    for h in hazard_classes:
        print(f"  {h:>8s}", end='')
    print()

    enrichments = {}
    for q in range(5):
        n_q = total_by_q[q]
        enrichments[q] = {}
        print(f"Q{q}  {n_q:6d}", end='')
        for h in hazard_classes:
            observed = counts[q][h]
            expected_rate = total_by_h[h] / N
            enrichment = (observed / n_q) / expected_rate if n_q > 0 and expected_rate > 0 else 0
            enrichments[q][h] = enrichment
            print(f"  {enrichment:8.3f}", end='')
        print()

    # Build contingency table for chi-squared
    table = np.array([[counts[q][h] for h in hazard_classes] for q in range(5)])

    # Remove zero columns
    col_sums = table.sum(axis=0)
    valid_cols = col_sums > 0
    table_valid = table[:, valid_cols]
    valid_classes = [h for h, v in zip(hazard_classes, valid_cols) if v]

    if table_valid.shape[1] >= 2:
        chi2, p, dof, _ = chi2_contingency(table_valid)
        V = cramers_v(table_valid)
        print(f"\nChi-squared: {chi2:.1f}, dof={dof}, p={p:.2e}")
        print(f"Cramer's V: {V:.4f}")
    else:
        chi2, p, dof, V = 0, 1, 0, 0

    # Mean position per hazard class
    print(f"\nMean fractional position by hazard class:")
    pos_by_class = defaultdict(list)
    for t in tokens:
        pos_by_class[t['hazard_class']].append(t['frac_pos'])

    for h in hazard_classes:
        if pos_by_class[h]:
            positions = pos_by_class[h]
            mean_p = np.mean(positions)
            std_p = np.std(positions)
            print(f"  {h}: mean={mean_p:.4f}, std={std_p:.4f}, N={len(positions)}")

    # Kruskal-Wallis: does position differ by hazard class?
    groups = [pos_by_class[h] for h in hazard_classes if len(pos_by_class[h]) >= 5]
    if len(groups) >= 2:
        kw_stat, kw_p = kruskal(*groups)
        # Effect size: eta-squared approximation
        kw_eta2 = (kw_stat - len(groups) + 1) / (N - len(groups))
        print(f"\nKruskal-Wallis (position ~ hazard_class): H={kw_stat:.1f}, p={kw_p:.2e}, eta2={kw_eta2:.4f}")
    else:
        kw_stat, kw_p, kw_eta2 = 0, 1, 0

    return {
        'test': 'T1_positional_hazard_gradient',
        'N': N,
        'hazard_class_counts': dict(total_by_h),
        'quintile_counts': dict(total_by_q),
        'enrichments': {str(q): enrichments[q] for q in range(5)},
        'chi2': chi2, 'p_chi2': p, 'dof': dof, 'cramers_v': V,
        'mean_position_by_class': {h: float(np.mean(pos_by_class[h])) for h in hazard_classes if pos_by_class[h]},
        'kruskal_wallis': {'H': kw_stat, 'p': kw_p, 'eta2': kw_eta2},
    }


def t2_zone_hazard_contingency(tokens):
    """T2: Three-zone model (SPEC/WORK/CLOSURE) x hazard class interaction.

    Zone mapping: Q0 = SPECIFICATION, Q1-Q3 = THERMAL_WORK, Q4 = CLOSURE
    """
    print("\n=== T2: Zone x Hazard Contingency ===")

    zones = ['SPECIFICATION', 'THERMAL_WORK', 'CLOSURE']
    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    def zone_of(q):
        if q == 0: return 'SPECIFICATION'
        elif q <= 3: return 'THERMAL_WORK'
        else: return 'CLOSURE'

    # Build zone x hazard contingency
    counts = defaultdict(lambda: defaultdict(int))
    total_by_zone = Counter()
    total_by_h = Counter()

    for t in tokens:
        z = zone_of(t['quintile'])
        h = t['hazard_class']
        counts[z][h] += 1
        total_by_zone[z] += 1
        total_by_h[h] += 1

    N = len(tokens)

    print(f"\nZone x Hazard Class (enrichment):")
    print(f"{'Zone':>16s}  {'N':>6s}", end='')
    for h in hazard_classes:
        print(f"  {h:>8s}", end='')
    print()

    enrichments = {}
    for z in zones:
        n_z = total_by_zone[z]
        enrichments[z] = {}
        print(f"{z:>16s}  {n_z:6d}", end='')
        for h in hazard_classes:
            observed = counts[z][h]
            expected_rate = total_by_h[h] / N
            enrichment = (observed / n_z) / expected_rate if n_z > 0 and expected_rate > 0 else 0
            enrichments[z][h] = enrichment
            print(f"  {enrichment:8.3f}", end='')
        print()

    # Build contingency table
    table = np.array([[counts[z][h] for h in hazard_classes] for z in zones])
    col_sums = table.sum(axis=0)
    valid_cols = col_sums > 0
    table_valid = table[:, valid_cols]
    valid_classes = [h for h, v in zip(hazard_classes, valid_cols) if v]

    if table_valid.shape[1] >= 2 and table_valid.shape[0] >= 2:
        chi2, p, dof, _ = chi2_contingency(table_valid)
        V = cramers_v(table_valid)
        print(f"\nChi-squared: {chi2:.1f}, dof={dof}, p={p:.2e}")
        print(f"Cramer's V: {V:.4f}")
    else:
        chi2, p, dof, V = 0, 1, 0, 0

    # Pairwise tests: SPEC vs WORK, WORK vs CLOSURE, SPEC vs CLOSURE
    pairwise = {}
    for za, zb in [('SPECIFICATION', 'THERMAL_WORK'), ('THERMAL_WORK', 'CLOSURE'), ('SPECIFICATION', 'CLOSURE')]:
        pair_table = np.array([[counts[za][h] for h in valid_classes],
                               [counts[zb][h] for h in valid_classes]])
        if pair_table.sum() > 0 and all(pair_table.sum(axis=1) > 0):
            c2, pp, dd, _ = chi2_contingency(pair_table)
            pv = cramers_v(pair_table)
            pairwise[f"{za}_vs_{zb}"] = {'chi2': c2, 'p': pp, 'V': pv}
            print(f"  {za} vs {zb}: chi2={c2:.1f}, p={pp:.2e}, V={pv:.4f}")

    return {
        'test': 'T2_zone_hazard_contingency',
        'enrichments': enrichments,
        'zone_counts': dict(total_by_zone),
        'chi2': chi2, 'p': p, 'dof': dof, 'cramers_v': V,
        'pairwise': pairwise,
    }


def t3_safe_pathway_positioning(tokens):
    """T3: Where does e->y concentrate within lines?

    C1459 says e->y is an ambient safe substrate, C1460 says early-line
    concentration (mean 0.463) with line-final avoidance (0.55x).
    Here we test the INTERACTION: is e->y's positional profile different from
    other safe (ZERO/IMMUNE) frames?
    """
    print("\n=== T3: Safe Pathway Positioning ===")

    ey_tokens = [t for t in tokens if t['frame_str'] == 'e->y']
    zero_non_ey = [t for t in tokens if t['hazard_class'] == 'ZERO' and t['frame_str'] != 'e->y']
    immune_tokens = [t for t in tokens if t['hazard_class'] == 'IMMUNE']
    high_tokens = [t for t in tokens if t['hazard_class'] == 'HIGH']

    print(f"\ne->y tokens: {len(ey_tokens)}")
    print(f"Other ZERO tokens: {len(zero_non_ey)}")
    print(f"IMMUNE tokens: {len(immune_tokens)}")
    print(f"HIGH tokens: {len(high_tokens)}")

    # Quintile distributions
    def quintile_dist(toks, label):
        q_counts = Counter(t['quintile'] for t in toks)
        total = len(toks)
        print(f"\n{label} quintile distribution:")
        for q in range(5):
            pct = q_counts[q] / total * 100 if total > 0 else 0
            print(f"  Q{q}: {q_counts[q]:5d} ({pct:5.1f}%)")
        return dict(q_counts)

    ey_q = quintile_dist(ey_tokens, "e->y")
    zero_q = quintile_dist(zero_non_ey, "Other ZERO")
    immune_q = quintile_dist(immune_tokens, "IMMUNE (k-HEAD)")
    high_q = quintile_dist(high_tokens, "HIGH")

    # Mean positions
    groups = {
        'e->y': [t['frac_pos'] for t in ey_tokens],
        'other_ZERO': [t['frac_pos'] for t in zero_non_ey],
        'IMMUNE': [t['frac_pos'] for t in immune_tokens],
        'HIGH': [t['frac_pos'] for t in high_tokens],
    }

    print(f"\nMean positions:")
    for label, positions in groups.items():
        if positions:
            print(f"  {label}: {np.mean(positions):.4f} (N={len(positions)})")

    # Mann-Whitney: e->y vs HIGH
    if groups['e->y'] and groups['HIGH']:
        u, p_mw = mannwhitneyu(groups['e->y'], groups['HIGH'], alternative='two-sided')
        # Rank-biserial correlation as effect size
        n1, n2 = len(groups['e->y']), len(groups['HIGH'])
        rbc = 1 - (2 * u) / (n1 * n2)
        print(f"\nMann-Whitney e->y vs HIGH: U={u:.0f}, p={p_mw:.2e}, r={rbc:.4f}")
    else:
        p_mw, rbc = 1, 0

    # Mann-Whitney: e->y vs IMMUNE
    if groups['e->y'] and groups['IMMUNE']:
        u2, p_mw2 = mannwhitneyu(groups['e->y'], groups['IMMUNE'], alternative='two-sided')
        n1, n2 = len(groups['e->y']), len(groups['IMMUNE'])
        rbc2 = 1 - (2 * u2) / (n1 * n2)
        print(f"Mann-Whitney e->y vs IMMUNE: U={u2:.0f}, p={p_mw2:.2e}, r={rbc2:.4f}")
    else:
        p_mw2, rbc2 = 1, 0

    # Enrichment: e->y quintile enrichment relative to corpus
    total_q = Counter(t['quintile'] for t in tokens)
    N = len(tokens)
    ey_enrichment = {}
    for q in range(5):
        corpus_rate = total_q[q] / N
        ey_rate = ey_q.get(q, 0) / len(ey_tokens) if len(ey_tokens) > 0 else 0
        ey_enrichment[q] = ey_rate / corpus_rate if corpus_rate > 0 else 0

    print(f"\ne->y enrichment by quintile:")
    for q in range(5):
        print(f"  Q{q}: {ey_enrichment[q]:.3f}x")

    return {
        'test': 'T3_safe_pathway_positioning',
        'ey_count': len(ey_tokens),
        'other_zero_count': len(zero_non_ey),
        'immune_count': len(immune_tokens),
        'high_count': len(high_tokens),
        'mean_positions': {k: float(np.mean(v)) for k, v in groups.items() if v},
        'ey_quintile_enrichment': {str(q): ey_enrichment[q] for q in range(5)},
        'ey_vs_high': {'p': p_mw, 'rank_biserial': rbc},
        'ey_vs_immune': {'p': p_mw2, 'rank_biserial': rbc2},
    }


def t4_immune_positioning(tokens):
    """T4: Where do k-HEAD (IMMUNE) frames concentrate?

    k is the ENERGY_MODULATOR (C103). C1428 says THERMAL peaks at Q1 then
    declines. Does k-HEAD follow this pattern, tracking THERMAL_WORK?
    """
    print("\n=== T4: k-IMMUNE Positioning ===")

    immune_tokens = [t for t in tokens if t['hazard_class'] == 'IMMUNE']
    non_immune = [t for t in tokens if t['hazard_class'] != 'IMMUNE']

    # Quintile enrichment
    total_q = Counter(t['quintile'] for t in tokens)
    immune_q = Counter(t['quintile'] for t in immune_tokens)
    N = len(tokens)
    N_imm = len(immune_tokens)

    print(f"\nIMMUNE (k-HEAD) tokens: {N_imm} ({N_imm/N*100:.1f}%)")

    enrichment = {}
    print(f"\nk-HEAD quintile enrichment:")
    for q in range(5):
        corpus_rate = total_q[q] / N
        imm_rate = immune_q[q] / N_imm if N_imm > 0 else 0
        enrichment[q] = imm_rate / corpus_rate if corpus_rate > 0 else 0
        print(f"  Q{q}: {enrichment[q]:.3f}x (N={immune_q[q]})")

    # Test monotonic trend: does k-HEAD track THERMAL's peak-then-decline?
    # Spearman of quintile vs enrichment
    q_vals = list(range(5))
    e_vals = [enrichment[q] for q in range(5)]
    rho, p_rho = spearmanr(q_vals, e_vals)
    print(f"\nSpearman (quintile vs enrichment): rho={rho:.4f}, p={p_rho:.4f}")

    # Mean position
    imm_positions = [t['frac_pos'] for t in immune_tokens]
    non_imm_positions = [t['frac_pos'] for t in non_immune]
    print(f"\nMean position IMMUNE: {np.mean(imm_positions):.4f}")
    print(f"Mean position non-IMMUNE: {np.mean(non_imm_positions):.4f}")

    # Does k-HEAD peak at Q1 like THERMAL?
    peak_q = max(range(5), key=lambda q: enrichment[q])
    print(f"Peak quintile: Q{peak_q} ({enrichment[peak_q]:.3f}x)")

    # Q1-Q3 (THERMAL_WORK zone) vs Q0+Q4 (boundary zones)
    work_zone = [t['frac_pos'] for t in immune_tokens if t['quintile'] in (1, 2, 3)]
    boundary_zone = [t['frac_pos'] for t in immune_tokens if t['quintile'] in (0, 4)]
    work_rate = len(work_zone) / N_imm if N_imm > 0 else 0
    expected_work_rate = sum(total_q[q] for q in (1, 2, 3)) / N
    work_enrichment = work_rate / expected_work_rate if expected_work_rate > 0 else 0
    print(f"\nTHERMAL_WORK zone (Q1-Q3): {work_rate*100:.1f}% of k-HEAD ({work_enrichment:.3f}x vs corpus)")

    return {
        'test': 'T4_immune_positioning',
        'N_immune': N_imm,
        'quintile_enrichment': {str(q): enrichment[q] for q in range(5)},
        'peak_quintile': peak_q,
        'spearman_trend': {'rho': rho, 'p': p_rho},
        'mean_position_immune': float(np.mean(imm_positions)),
        'mean_position_non_immune': float(np.mean(non_imm_positions)),
        'work_zone_enrichment': work_enrichment,
    }


def t5_per_frame_positional_preference(tokens):
    """T5: Do the 7 HIGH-hazard frames each have distinct positional preferences?

    HIGH frames from C1448: o->bare, d->y, a->l, a->r, o->r, e->e, a->n
    """
    print("\n=== T5: Per-Frame Positional Preferences ===")

    HIGH_FRAMES = ['o->bare', 'd->y', 'a->l', 'a->r', 'o->r', 'e->e', 'a->n']

    # Group by frame
    frame_data = defaultdict(list)
    for t in tokens:
        if t['frame_str'] in HIGH_FRAMES:
            frame_data[t['frame_str']].append(t)

    # Corpus quintile baseline
    total_q = Counter(t['quintile'] for t in tokens)
    N = len(tokens)

    print(f"\nPer-frame positional profiles:")
    print(f"{'Frame':>10s}  {'N':>5s}  {'Mean':>6s}  {'Q0':>6s}  {'Q1':>6s}  {'Q2':>6s}  {'Q3':>6s}  {'Q4':>6s}")

    frame_results = {}
    positions_by_frame = {}
    for frame in HIGH_FRAMES:
        toks = frame_data[frame]
        n = len(toks)
        if n == 0:
            continue

        positions = [t['frac_pos'] for t in toks]
        positions_by_frame[frame] = positions
        mean_pos = np.mean(positions)

        q_counts = Counter(t['quintile'] for t in toks)
        enrichments = {}
        row = f"{frame:>10s}  {n:5d}  {mean_pos:6.3f}"
        for q in range(5):
            corpus_rate = total_q[q] / N
            frame_rate = q_counts[q] / n if n > 0 else 0
            enrich = frame_rate / corpus_rate if corpus_rate > 0 else 0
            enrichments[str(q)] = enrich
            row += f"  {enrich:6.3f}"
        print(row)

        frame_results[frame] = {
            'N': n,
            'mean_position': float(mean_pos),
            'quintile_enrichment': enrichments,
        }

    # Kruskal-Wallis: do HIGH frames differ in position?
    groups = [positions_by_frame[f] for f in HIGH_FRAMES if f in positions_by_frame and len(positions_by_frame[f]) >= 5]
    if len(groups) >= 2:
        kw_stat, kw_p = kruskal(*groups)
        N_groups = sum(len(g) for g in groups)
        kw_eta2 = (kw_stat - len(groups) + 1) / (N_groups - len(groups))
        print(f"\nKruskal-Wallis (position ~ frame among HIGH): H={kw_stat:.1f}, p={kw_p:.2e}, eta2={kw_eta2:.4f}")
    else:
        kw_stat, kw_p, kw_eta2 = 0, 1, 0

    # Most initial-biased vs most final-biased
    if frame_results:
        sorted_by_pos = sorted(frame_results.items(), key=lambda x: x[1]['mean_position'])
        print(f"\nMost initial-biased HIGH frame: {sorted_by_pos[0][0]} (mean={sorted_by_pos[0][1]['mean_position']:.3f})")
        print(f"Most final-biased HIGH frame: {sorted_by_pos[-1][0]} (mean={sorted_by_pos[-1][1]['mean_position']:.3f})")
        print(f"Positional spread: {sorted_by_pos[-1][1]['mean_position'] - sorted_by_pos[0][1]['mean_position']:.3f}")

    return {
        'test': 'T5_per_frame_positional_preference',
        'frame_profiles': frame_results,
        'kruskal_wallis_among_high': {'H': kw_stat, 'p': kw_p, 'eta2': kw_eta2},
    }


def t6_line_length_interaction(tokens):
    """T6: Does the hazard gradient depend on line length?

    Short lines (<=7 tokens) vs long lines (>=12 tokens).
    Tests whether the zone x hazard interaction is line-length-dependent.
    """
    print("\n=== T6: Line-Length Interaction ===")

    short = [t for t in tokens if t['line_length'] <= 7]
    long_ = [t for t in tokens if t['line_length'] >= 12]
    medium = [t for t in tokens if 7 < t['line_length'] < 12]

    print(f"\nShort lines (<=7): {len(short)} tokens")
    print(f"Medium lines (8-11): {len(medium)} tokens")
    print(f"Long lines (>=12): {len(long_)} tokens")

    hazard_classes = ['HIGH', 'LOW', 'ZERO', 'IMMUNE']

    def compute_zone_hazard(toks, label):
        """Compute zone x hazard enrichment for a subset."""
        zones = ['SPECIFICATION', 'THERMAL_WORK', 'CLOSURE']

        def zone_of(q):
            if q == 0: return 'SPECIFICATION'
            elif q <= 3: return 'THERMAL_WORK'
            else: return 'CLOSURE'

        N = len(toks)
        if N < 20:
            return None

        counts = defaultdict(lambda: defaultdict(int))
        total_by_zone = Counter()
        total_by_h = Counter()

        for t in toks:
            z = zone_of(t['quintile'])
            h = t['hazard_class']
            counts[z][h] += 1
            total_by_zone[z] += 1
            total_by_h[h] += 1

        print(f"\n{label} zone x hazard enrichment:")
        print(f"{'Zone':>16s}", end='')
        for h in hazard_classes:
            print(f"  {h:>8s}", end='')
        print()

        enrichments = {}
        for z in zones:
            n_z = total_by_zone[z]
            enrichments[z] = {}
            print(f"{z:>16s}", end='')
            for h in hazard_classes:
                expected_rate = total_by_h[h] / N if N > 0 else 0
                observed_rate = counts[z][h] / n_z if n_z > 0 else 0
                enrich = observed_rate / expected_rate if expected_rate > 0 else 0
                enrichments[z][h] = enrich
                print(f"  {enrich:8.3f}", end='')
            print()

        # Chi-squared
        table = np.array([[counts[z][h] for h in hazard_classes] for z in zones])
        col_sums = table.sum(axis=0)
        valid = col_sums > 0
        table_v = table[:, valid]

        if table_v.shape[1] >= 2 and table_v.shape[0] >= 2:
            chi2, p, dof, _ = chi2_contingency(table_v)
            V = cramers_v(table_v)
            print(f"  Chi2={chi2:.1f}, p={p:.2e}, V={V:.4f}")
        else:
            chi2, p, V = 0, 1, 0

        return {
            'N': N,
            'enrichments': enrichments,
            'chi2': chi2, 'p': p, 'cramers_v': V,
        }

    short_res = compute_zone_hazard(short, "SHORT (<=7)")
    long_res = compute_zone_hazard(long_, "LONG (>=12)")
    medium_res = compute_zone_hazard(medium, "MEDIUM (8-11)")

    # HIGH rate at Q4 (CLOSURE): short vs long
    high_q4_short = sum(1 for t in short if t['quintile'] == 4 and t['hazard_class'] == 'HIGH')
    total_q4_short = sum(1 for t in short if t['quintile'] == 4)
    high_q4_long = sum(1 for t in long_ if t['quintile'] == 4 and t['hazard_class'] == 'HIGH')
    total_q4_long = sum(1 for t in long_ if t['quintile'] == 4)

    rate_short = high_q4_short / total_q4_short if total_q4_short > 0 else 0
    rate_long = high_q4_long / total_q4_long if total_q4_long > 0 else 0

    print(f"\nHIGH hazard rate at CLOSURE (Q4):")
    print(f"  Short: {rate_short:.3f} ({high_q4_short}/{total_q4_short})")
    print(f"  Long: {rate_long:.3f} ({high_q4_long}/{total_q4_long})")

    # Interaction test: 2x4 contingency (short/long) x (HIGH/LOW/ZERO/IMMUNE) within CLOSURE only
    closure_short = Counter(t['hazard_class'] for t in short if t['quintile'] == 4)
    closure_long = Counter(t['hazard_class'] for t in long_ if t['quintile'] == 4)

    int_table = np.array([[closure_short.get(h, 0) for h in hazard_classes],
                          [closure_long.get(h, 0) for h in hazard_classes]])
    col_valid = int_table.sum(axis=0) > 0
    int_table_v = int_table[:, col_valid]

    if int_table_v.shape[1] >= 2 and all(int_table_v.sum(axis=1) > 0):
        chi2_int, p_int, dof_int, _ = chi2_contingency(int_table_v)
        V_int = cramers_v(int_table_v)
        print(f"\nClosure hazard interaction (short vs long): chi2={chi2_int:.1f}, p={p_int:.2e}, V={V_int:.4f}")
    else:
        chi2_int, p_int, V_int = 0, 1, 0

    return {
        'test': 'T6_line_length_interaction',
        'short': short_res,
        'medium': medium_res,
        'long': long_res,
        'closure_high_rate': {'short': rate_short, 'long': rate_long},
        'closure_interaction': {'chi2': chi2_int, 'p': p_int, 'cramers_v': V_int},
    }


def t_extra_section_interaction(tokens):
    """Extra: Does the zone x hazard gradient differ by section?

    Tests whether sections (Bio, Herbal, Stars/Recipe) show different
    positional hazard routing.
    """
    print("\n=== T-Extra: Section x Zone x Hazard Interaction ===")

    # Map sections
    section_map = {}
    for t in tokens:
        s = t['section']
        if s not in section_map:
            section_map[s] = []
        section_map[s].append(t)

    print(f"\nSections: {', '.join(f'{s}({len(v)})' for s, v in sorted(section_map.items()))}")

    section_results = {}
    for sec, toks in sorted(section_map.items()):
        if len(toks) < 100:
            continue

        # HIGH hazard rate by zone
        def zone_of(q):
            if q == 0: return 'SPECIFICATION'
            elif q <= 3: return 'THERMAL_WORK'
            else: return 'CLOSURE'

        zones = ['SPECIFICATION', 'THERMAL_WORK', 'CLOSURE']
        high_by_zone = {}
        for z in zones:
            z_toks = [t for t in toks if zone_of(t['quintile']) == z]
            high_count = sum(1 for t in z_toks if t['hazard_class'] == 'HIGH')
            rate = high_count / len(z_toks) if z_toks else 0
            high_by_zone[z] = {'rate': rate, 'N': len(z_toks), 'high_count': high_count}

        print(f"\n  {sec}: HIGH hazard rate by zone:")
        for z in zones:
            d = high_by_zone[z]
            print(f"    {z}: {d['rate']*100:.1f}% ({d['high_count']}/{d['N']})")

        section_results[sec] = high_by_zone

    return {
        'test': 'T_extra_section_interaction',
        'section_results': section_results,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 528: Line Zone x Frame Hazard Interaction")
    print("=" * 60)

    # Load data
    print("\nLoading Currier B tokens...")
    tokens = load_b_tokens()
    print(f"Loaded {len(tokens)} tokens with frame classification")

    # Summary stats
    hazard_dist = Counter(t['hazard_class'] for t in tokens)
    print(f"\nHazard class distribution:")
    for h, c in hazard_dist.most_common():
        print(f"  {h}: {c} ({c/len(tokens)*100:.1f}%)")

    # Run all tests
    results = {}
    results['t1'] = t1_positional_hazard_gradient(tokens)
    results['t2'] = t2_zone_hazard_contingency(tokens)
    results['t3'] = t3_safe_pathway_positioning(tokens)
    results['t4'] = t4_immune_positioning(tokens)
    results['t5'] = t5_per_frame_positional_preference(tokens)
    results['t6'] = t6_line_length_interaction(tokens)
    results['t_extra'] = t_extra_section_interaction(tokens)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF FINDINGS")
    print("=" * 60)

    # Key finding 1: Is hazard positionally structured?
    v = results['t2']['cramers_v']
    p = results['t2']['p']
    print(f"\n1. Zone x Hazard Contingency: V={v:.4f}, p={p:.2e}")

    # Key finding 2: Position differences between hazard classes
    kw_eta2 = results['t1']['kruskal_wallis']['eta2']
    kw_p = results['t1']['kruskal_wallis']['p']
    print(f"2. Position ~ Hazard Class (KW): eta2={kw_eta2:.4f}, p={kw_p:.2e}")

    # Key finding 3: e->y vs HIGH position difference
    if 'ey_vs_high' in results['t3']:
        ey_high_p = results['t3']['ey_vs_high']['p']
        ey_high_r = results['t3']['ey_vs_high']['rank_biserial']
        print(f"3. e->y vs HIGH position: r={ey_high_r:.4f}, p={ey_high_p:.2e}")

    # Key finding 4: Do HIGH frames differ in position?
    kw_h = results['t5']['kruskal_wallis_among_high']
    print(f"4. Among HIGH frames (KW): H={kw_h['H']:.1f}, p={kw_h['p']:.2e}, eta2={kw_h['eta2']:.4f}")

    # Key finding 5: Line-length interaction
    closure_int = results['t6']['closure_interaction']
    print(f"5. Closure hazard x line length: V={closure_int['cramers_v']:.4f}, p={closure_int['p']:.2e}")

    # Save results
    output_path = RESULTS_DIR / 'line_zone_frame_hazard.json'

    # Clean numpy types for JSON
    def clean(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [clean(v) for v in obj]
        return obj

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean(results), f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()

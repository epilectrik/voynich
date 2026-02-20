"""Phase 409: Dark Pipeline Internal Architecture.

Phase 408 established the dark pipeline inventory (300 MIDDLEs, 50 atoms,
25 dark-exclusive + 25 shared). This phase probes the INTERNAL structure:
what drives dark-pipeline behavior if not atom selection (p=0.303)?

Tests:
  1. Dark-exclusive atom characterization (length, frequency, spread, Herfindahl)
  2. Ordering divergence source (do dark-exclusive atoms explain C1065 mismatches?)
  3. Atom positional slot grammar (INITIAL/MEDIAL/FINAL distribution)
  4. Folio-level density regression (what predicts dark-pipeline token count?)
  5. Dark pipeline line position (FIRST/MIDDLE/LAST vs general HT)
  6. Frequency modulation decomposition (JS divergence vs C1134 baseline)
"""
import json
import sys
import math
import os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer


# --- Utility functions ---

def round_floats(obj, digits=4):
    """Recursively round floats in nested dicts/lists."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def herfindahl(counts):
    """Herfindahl index (sum of squared shares). 1/N=uniform, 1.0=concentrated."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def jensen_shannon(p_counts, q_counts):
    """Jensen-Shannon divergence between two count distributions."""
    all_keys = set(p_counts.keys()) | set(q_counts.keys())
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total == 0 or q_total == 0:
        return 0.0
    js = 0.0
    for k in all_keys:
        p = p_counts.get(k, 0) / p_total
        q = q_counts.get(k, 0) / q_total
        m = (p + q) / 2
        if p > 0 and m > 0:
            js += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            js += 0.5 * q * math.log2(q / m)
    return js


def mann_whitney_u(xs, ys):
    """Manual Mann-Whitney U test. Returns U statistic, z-score, and two-sided p-value."""
    nx, ny = len(xs), len(ys)
    if nx == 0 or ny == 0:
        return {'U': 0, 'z': 0.0, 'p': 1.0, 'nx': nx, 'ny': ny}

    # Rank all values
    combined = [(v, 'x', i) for i, v in enumerate(xs)] + \
               [(v, 'y', i) for i, v in enumerate(ys)]
    combined.sort(key=lambda t: t[0])

    # Assign ranks with tie handling
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average rank
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # Sum ranks for group x
    r_x = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 'x')
    U_x = r_x - nx * (nx + 1) / 2

    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12) if (nx + ny + 1) > 0 else 1.0
    z = (U_x - mu) / sigma if sigma > 0 else 0.0

    # Two-sided p-value via normal approximation
    # Phi(z) approximation using error function
    p = 2 * (1 - _normal_cdf(abs(z)))

    return {'U': U_x, 'z': z, 'p': p, 'nx': nx, 'ny': ny}


def _normal_cdf(x):
    """Approximation of standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def fisher_exact_2x2(a, b, c, d):
    """Fisher's exact test for 2x2 table [[a,b],[c,d]].
    Returns odds ratio and two-sided p-value."""
    n = a + b + c + d
    # Log-factorial table
    log_fac = [0.0] * (n + 1)
    for i in range(2, n + 1):
        log_fac[i] = log_fac[i - 1] + math.log(i)

    def hypergeom_log_prob(x):
        """Log probability of observing x in cell (0,0)."""
        r0 = a + b  # row 0 total
        r1 = c + d  # row 1 total
        c0 = a + c  # col 0 total
        c1 = b + d  # col 1 total
        return (log_fac[r0] + log_fac[r1] + log_fac[c0] + log_fac[c1]
                - log_fac[n] - log_fac[x] - log_fac[r0 - x]
                - log_fac[c0 - x] - log_fac[r1 - c0 + x])

    # Range of valid x: max(0, c0-r1) to min(r0, c0)
    r0 = a + b
    r1 = c + d
    c0 = a + c
    x_min = max(0, c0 - r1)
    x_max = min(r0, c0)

    observed_log_p = hypergeom_log_prob(a)

    # Two-sided: sum probabilities <= observed
    p_value = 0.0
    for x in range(x_min, x_max + 1):
        lp = hypergeom_log_prob(x)
        if lp <= observed_log_p + 1e-10:  # tolerance for floating point
            p_value += math.exp(lp)

    p_value = min(p_value, 1.0)

    # Odds ratio
    if b * c == 0:
        odds_ratio = float('inf') if a * d > 0 else 0.0
    else:
        odds_ratio = (a * d) / (b * c)

    return {'odds_ratio': odds_ratio, 'p': p_value}


def chi_square_2xk(observed_2d):
    """Chi-square test on a 2xK contingency table.
    observed_2d: [[row0_col0, row0_col1, ...], [row1_col0, row1_col1, ...]]
    Returns chi2, df, p-value approximation."""
    n_rows = len(observed_2d)
    n_cols = len(observed_2d[0])
    n = sum(sum(row) for row in observed_2d)
    if n == 0:
        return {'chi2': 0.0, 'df': 0, 'p': 1.0}

    row_totals = [sum(row) for row in observed_2d]
    col_totals = [sum(observed_2d[r][c] for r in range(n_rows)) for c in range(n_cols)]

    chi2 = 0.0
    for r in range(n_rows):
        for c in range(n_cols):
            expected = row_totals[r] * col_totals[c] / n
            if expected > 0:
                chi2 += (observed_2d[r][c] - expected) ** 2 / expected

    df = (n_rows - 1) * (n_cols - 1)

    # P-value via chi-square CDF approximation (Wilson-Hilferty)
    if df > 0 and chi2 > 0:
        z = ((chi2 / df) ** (1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        p = 1 - _normal_cdf(z)
    else:
        p = 1.0

    return {'chi2': chi2, 'df': df, 'p': p}


def pearson_r(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


# --- Data loading ---

def load_data():
    """Load all input files, build populations, single B pass with line position tracking."""

    # 1. Load static data files
    with open(ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json',
              encoding='utf-8') as f:
        pp_role_data = json.load(f)

    with open(ROOT / 'phases/CROSS_SYSTEM_VOCABULARY_FLOW/results/ab_vocabulary_flow.json',
              encoding='utf-8') as f:
        vocab_flow = json.load(f)

    with open(ROOT / 'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)

    with open(ROOT / 'phases/MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE/results/t3_atom_bigram_grammar.json',
              encoding='utf-8') as f:
        c1065_data = json.load(f)

    with open(ROOT / 'phases/PP_PIPELINE_ATOM_DECOMPOSITION/results/pp_pipeline_atoms.json',
              encoding='utf-8') as f:
        p408_data = json.load(f)

    with open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
              encoding='utf-8') as f:
        class_map = json.load(f)

    # 2. Build population sets
    pp_role_map = pp_role_data['pp_role_map']
    unmatched_pp_list = pp_role_data['unmatched_pp']
    b_absent_set = set(vocab_flow['b1']['b_absent_middles'])
    dark_pipeline_set = set(unmatched_pp_list) - b_absent_set  # 300

    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])  # 85

    matched_pp_set = set()
    for mid, info in pp_role_map.items():
        if info['n_classes'] > 0:
            matched_pp_set.add(mid)

    classified_set = set(class_map['token_to_class'].keys())

    # 3. Extract Phase 408 atom lists
    dark_exclusive_atoms = set(p408_data['test3']['dark_exclusive_atoms'])  # 25
    shared_atoms = set(p408_data['test3']['shared_atoms'])  # 25
    comparison_details = p408_data['test5']['comparison_details']  # 14 tested + 6 NOT_FOUND

    # 4. Initialize MiddleAnalyzer
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # 5. Initialize transcript and morphology
    tx = Transcript()
    morph = Morphology()

    # 6. Single pass over B tokens — collect everything needed for all 6 tests
    # Per-token accumulators
    dark_tokens = []
    grammar_tokens = []
    ht_tokens = []   # non-grammar tokens (includes dark-pipeline)

    # Per-folio accumulators
    folio_dark_count = Counter()
    folio_ht_count = Counter()
    folio_grammar_count = Counter()
    folio_bridge_count = Counter()
    folio_total_count = Counter()
    folio_section = {}  # folio -> section

    # Per-line: track token indices within each line for position analysis
    line_tokens = defaultdict(list)  # (folio, line) -> [token_records in order]

    # Per-MIDDLE per-section frequency
    middle_section_freq = defaultdict(Counter)

    # Per-atom accumulators (for test 1)
    atom_b_freq = Counter()
    atom_b_folios = defaultdict(set)
    atom_section_freq = defaultdict(Counter)

    n_scanned = 0

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue

        n_scanned += 1
        m = morph.extract(word)
        mid = m.middle

        is_grammar = word in classified_set
        is_dark = (mid in dark_pipeline_set) if mid else False

        record = {
            'word': word,
            'folio': token.folio,
            'line': token.line,
            'section': token.section,
            'middle': mid,
            'is_grammar': is_grammar,
            'is_dark': is_dark,
            'par_initial': token.par_initial,
        }

        line_tokens[(token.folio, token.line)].append(record)

        folio_total_count[token.folio] += 1
        folio_section[token.folio] = token.section

        if is_grammar:
            grammar_tokens.append(record)
            folio_grammar_count[token.folio] += 1
        else:
            ht_tokens.append(record)
            folio_ht_count[token.folio] += 1

        if is_dark:
            dark_tokens.append(record)
            folio_dark_count[token.folio] += 1

        # Bridge token tracking
        if mid and mid in bridge_set:
            folio_bridge_count[token.folio] += 1

        # Per-MIDDLE section frequency
        if mid:
            middle_section_freq[mid][token.section] += 1

        # Per-atom tracking: count atoms in dark-pipeline MIDDLEs
        if is_dark and mid and mid_analyzer.is_compound(mid):
            atoms = mid_analyzer.get_maximal_atoms(mid)
            for atom in atoms:
                atom_b_freq[atom] += 1
                atom_b_folios[atom].add(token.folio)
                atom_section_freq[atom][token.section] += 1

    print(f"Scanned {n_scanned} B tokens")
    print(f"  Grammar: {len(grammar_tokens)}, HT/UN: {len(ht_tokens)}")
    print(f"  Dark-pipeline tokens: {len(dark_tokens)}")
    print(f"  Folios: {len(folio_section)}")

    return {
        'dark_pipeline_set': dark_pipeline_set,
        'bridge_set': bridge_set,
        'matched_pp_set': matched_pp_set,
        'classified_set': classified_set,
        'dark_exclusive_atoms': dark_exclusive_atoms,
        'shared_atoms': shared_atoms,
        'comparison_details': comparison_details,
        'mid_analyzer': mid_analyzer,
        'c1065_data': c1065_data,
        'dark_tokens': dark_tokens,
        'grammar_tokens': grammar_tokens,
        'ht_tokens': ht_tokens,
        'folio_dark_count': folio_dark_count,
        'folio_ht_count': folio_ht_count,
        'folio_grammar_count': folio_grammar_count,
        'folio_bridge_count': folio_bridge_count,
        'folio_total_count': folio_total_count,
        'folio_section': folio_section,
        'line_tokens': line_tokens,
        'middle_section_freq': middle_section_freq,
        'atom_b_freq': atom_b_freq,
        'atom_b_folios': atom_b_folios,
        'atom_section_freq': atom_section_freq,
        'n_scanned': n_scanned,
    }


# --- Test 1: Dark-Exclusive Atom Characterization ---

def test1_atom_characterization(data):
    """Characterize 25 dark-exclusive atoms vs 25 shared atoms."""
    dark_exc = data['dark_exclusive_atoms']
    shared = data['shared_atoms']
    atom_b_freq = data['atom_b_freq']
    atom_b_folios = data['atom_b_folios']
    atom_section_freq = data['atom_section_freq']

    def profile_atoms(atom_set, label):
        profiles = []
        herfs = []
        for atom in sorted(atom_set):
            freq = atom_b_freq.get(atom, 0)
            n_folios = len(atom_b_folios.get(atom, set()))
            sec_dist = atom_section_freq.get(atom, Counter())
            h = herfindahl(sec_dist)

            profiles.append({
                'atom': atom,
                'char_length': len(atom),
                'b_token_freq': freq,
                'folio_spread': n_folios,
                'section_herf': h,
                'dominant_section': sec_dist.most_common(1)[0][0] if sec_dist else 'none',
            })
            if freq > 0:  # Only include atoms actually observed in dark compounds
                herfs.append(h)

        mean_len = sum(p['char_length'] for p in profiles) / len(profiles) if profiles else 0
        mean_freq = sum(p['b_token_freq'] for p in profiles) / len(profiles) if profiles else 0
        mean_spread = sum(p['folio_spread'] for p in profiles) / len(profiles) if profiles else 0
        mean_herf = sum(herfs) / len(herfs) if herfs else 0

        return profiles, herfs, {
            'n_atoms': len(profiles),
            'n_observed': len(herfs),
            'mean_char_length': mean_len,
            'mean_b_token_freq': mean_freq,
            'mean_folio_spread': mean_spread,
            'mean_section_herf': mean_herf,
        }

    exc_profiles, exc_herfs, exc_summary = profile_atoms(dark_exc, 'dark_exclusive')
    shr_profiles, shr_herfs, shr_summary = profile_atoms(shared, 'shared')

    # Mann-Whitney U on Herfindahl: dark-exclusive vs shared
    mw = mann_whitney_u(exc_herfs, shr_herfs)

    # Verdict
    if mw['p'] < 0.05:
        if sum(exc_herfs) / len(exc_herfs) > sum(shr_herfs) / len(shr_herfs):
            verdict = 'CONCENTRATED'
        else:
            verdict = 'DISPERSED'
    else:
        verdict = 'EQUIVALENT'

    print(f"\nTest 1: Dark-Exclusive Atom Characterization")
    print(f"  Dark-exclusive: {exc_summary}")
    print(f"  Shared: {shr_summary}")
    print(f"  Mann-Whitney U: z={mw['z']:.3f}, p={mw['p']:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'dark_exclusive_summary': exc_summary,
        'shared_summary': shr_summary,
        'dark_exclusive_profiles': exc_profiles,
        'shared_profiles': shr_profiles,
        'mann_whitney': mw,
        'verdict': verdict,
    }


# --- Test 2: Ordering Divergence Source ---

def test2_ordering_divergence(data):
    """Test if dark-exclusive atoms explain C1065 mismatches."""
    dark_exc = data['dark_exclusive_atoms']
    comparison_details = data['comparison_details']

    # For each of 14 tested pairs (excluding NOT_FOUND), check dark-exclusive presence
    match_with_dark_exc = 0
    match_without_dark_exc = 0
    mismatch_with_dark_exc = 0
    mismatch_without_dark_exc = 0

    pair_analysis = []
    for pair in comparison_details:
        status = pair['dark_status']
        if status == 'NOT_FOUND':
            continue

        first = pair['c1065_first']
        second = pair['c1065_second']
        has_dark_exc = (first in dark_exc) or (second in dark_exc)

        pair_analysis.append({
            'first': first,
            'second': second,
            'status': status,
            'has_dark_exclusive': has_dark_exc,
            'first_is_dark_exc': first in dark_exc,
            'second_is_dark_exc': second in dark_exc,
        })

        if status == 'MATCH':
            if has_dark_exc:
                match_with_dark_exc += 1
            else:
                match_without_dark_exc += 1
        else:  # MISMATCH
            if has_dark_exc:
                mismatch_with_dark_exc += 1
            else:
                mismatch_without_dark_exc += 1

    # Fisher exact: 2x2 table
    # [[match_with_dark, match_without], [mismatch_with_dark, mismatch_without]]
    fisher = fisher_exact_2x2(
        match_with_dark_exc, match_without_dark_exc,
        mismatch_with_dark_exc, mismatch_without_dark_exc
    )

    total_tested = match_with_dark_exc + match_without_dark_exc + \
                   mismatch_with_dark_exc + mismatch_without_dark_exc

    # Verdict
    if fisher['p'] < 0.05:
        if fisher['odds_ratio'] < 1:
            verdict = 'ATOM_POOL_EFFECT'
        else:
            verdict = 'REVERSE_ENRICHMENT'
    else:
        verdict = 'GRAMMAR_MODIFICATION'

    print(f"\nTest 2: Ordering Divergence Source")
    print(f"  Tested pairs: {total_tested}")
    print(f"  MATCH with dark-exc: {match_with_dark_exc}, without: {match_without_dark_exc}")
    print(f"  MISMATCH with dark-exc: {mismatch_with_dark_exc}, without: {mismatch_without_dark_exc}")
    print(f"  Fisher exact: OR={fisher['odds_ratio']:.3f}, p={fisher['p']:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'contingency_table': {
            'match_with_dark_exc': match_with_dark_exc,
            'match_without_dark_exc': match_without_dark_exc,
            'mismatch_with_dark_exc': mismatch_with_dark_exc,
            'mismatch_without_dark_exc': mismatch_without_dark_exc,
        },
        'total_tested': total_tested,
        'fisher_exact': fisher,
        'pair_analysis': pair_analysis,
        'verdict': verdict,
    }


# --- Test 3: Atom Positional Slot Grammar ---

def test3_atom_slot_grammar(data):
    """Where do dark-exclusive vs shared atoms sit within compounds?"""
    dark_pipeline_set = data['dark_pipeline_set']
    dark_exc = data['dark_exclusive_atoms']
    shared = data['shared_atoms']
    mid_analyzer = data['mid_analyzer']

    # Multi-atom dark-pipeline compounds
    dark_compounds = [m for m in dark_pipeline_set if mid_analyzer.is_compound(m)]
    multi_atom = []
    for mid in dark_compounds:
        atoms = mid_analyzer.get_maximal_atoms(mid)
        if len(atoms) >= 2:
            multi_atom.append((mid, atoms))

    # Classify atom positions: INITIAL, MEDIAL, FINAL
    # For each atom occurrence in a multi-atom compound, determine position
    dark_exc_positions = Counter()  # {INITIAL, MEDIAL, FINAL}
    shared_positions = Counter()
    position_details = []

    for mid, atoms in multi_atom:
        # Locate atoms by string position
        atom_locs = []
        for atom in atoms:
            pos = mid.find(atom)
            if pos >= 0:
                atom_locs.append((pos, atom))
        atom_locs.sort(key=lambda x: x[0])

        if len(atom_locs) < 2:
            continue

        for idx, (pos, atom) in enumerate(atom_locs):
            if idx == 0:
                slot = 'INITIAL'
            elif idx == len(atom_locs) - 1:
                slot = 'FINAL'
            else:
                slot = 'MEDIAL'

            is_dark_exc = atom in dark_exc
            is_shared = atom in shared

            if is_dark_exc:
                dark_exc_positions[slot] += 1
            elif is_shared:
                shared_positions[slot] += 1

            position_details.append({
                'middle': mid,
                'atom': atom,
                'slot': slot,
                'atom_type': 'dark_exclusive' if is_dark_exc else ('shared' if is_shared else 'other'),
            })

    # Chi-square on 2x3 contingency: [dark_exc, shared] x [INITIAL, MEDIAL, FINAL]
    slots = ['INITIAL', 'MEDIAL', 'FINAL']
    observed = [
        [dark_exc_positions.get(s, 0) for s in slots],
        [shared_positions.get(s, 0) for s in slots],
    ]

    chi2_result = chi_square_2xk(observed)

    # Summary rates
    dark_exc_total = sum(dark_exc_positions.values())
    shared_total = sum(shared_positions.values())

    dark_exc_rates = {s: dark_exc_positions.get(s, 0) / dark_exc_total
                      if dark_exc_total > 0 else 0 for s in slots}
    shared_rates = {s: shared_positions.get(s, 0) / shared_total
                    if shared_total > 0 else 0 for s in slots}

    # Verdict
    if chi2_result['p'] < 0.05:
        verdict = 'SLOT_DIFFERENTIATED'
    else:
        verdict = 'SLOT_UNIFORM'

    print(f"\nTest 3: Atom Positional Slot Grammar")
    print(f"  Multi-atom compounds analyzed: {len(multi_atom)}")
    print(f"  Dark-exclusive positions: {dict(dark_exc_positions)} (n={dark_exc_total})")
    print(f"  Shared positions: {dict(shared_positions)} (n={shared_total})")
    print(f"  Dark-exc rates: {dark_exc_rates}")
    print(f"  Shared rates: {shared_rates}")
    print(f"  Chi-square: chi2={chi2_result['chi2']:.3f}, df={chi2_result['df']}, "
          f"p={chi2_result['p']:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'n_multi_atom_compounds': len(multi_atom),
        'dark_exclusive_positions': dict(dark_exc_positions),
        'shared_positions': dict(shared_positions),
        'dark_exclusive_rates': dark_exc_rates,
        'shared_rates': shared_rates,
        'observed_table': observed,
        'chi_square': chi2_result,
        'verdict': verdict,
    }


# --- Test 4: Folio-Level Density Regression ---

def test4_density_regression(data):
    """What predicts dark-pipeline token count per folio?"""
    folio_dark = data['folio_dark_count']
    folio_ht = data['folio_ht_count']
    folio_grammar = data['folio_grammar_count']
    folio_bridge = data['folio_bridge_count']
    folio_total = data['folio_total_count']
    folio_section = data['folio_section']

    # Build per-folio rate vectors
    folios = sorted(folio_total.keys())
    n_folios = len(folios)

    dark_rates = []
    ht_rates = []
    bridge_rates = []
    sections = []

    for f in folios:
        total = folio_total[f]
        if total == 0:
            continue
        dark_rates.append(folio_dark.get(f, 0) / total)
        ht_rates.append(folio_ht.get(f, 0) / total)
        bridge_rates.append(folio_bridge.get(f, 0) / total)
        sections.append(folio_section.get(f, 'unknown'))

    # 1. Section-only R² (ANOVA-style)
    grand_mean = sum(dark_rates) / len(dark_rates) if dark_rates else 0
    ss_total = sum((r - grand_mean) ** 2 for r in dark_rates)

    section_groups = defaultdict(list)
    for r, s in zip(dark_rates, sections):
        section_groups[s].append(r)

    ss_between = 0.0
    for s, vals in section_groups.items():
        group_mean = sum(vals) / len(vals)
        ss_between += len(vals) * (group_mean - grand_mean) ** 2

    section_r2 = ss_between / ss_total if ss_total > 0 else 0

    # Section means
    section_means = {s: sum(vals) / len(vals) for s, vals in section_groups.items()}
    section_counts = {s: len(vals) for s, vals in section_groups.items()}

    # 2. Within-section correlations
    within_section_corrs = {}
    for s, indices in defaultdict(list).items():
        pass  # will compute below

    # Compute within-section residuals and correlations
    dark_residuals = []
    ht_residuals = []
    bridge_residuals = []

    for r_dark, r_ht, r_bridge, s in zip(dark_rates, ht_rates, bridge_rates, sections):
        s_mean = section_means[s]
        dark_residuals.append(r_dark - s_mean)
        ht_residuals.append(r_ht)
        bridge_residuals.append(r_bridge)

    # Overall correlations
    corr_dark_ht = pearson_r(dark_rates, ht_rates)
    corr_dark_bridge = pearson_r(dark_rates, bridge_rates)

    # Within-section correlations (pool residuals)
    # For each section, compute correlation between dark_rate and ht_rate
    within_corrs = {}
    for s in sorted(section_groups.keys()):
        s_folios = [(dr, hr, br) for dr, hr, br, sec
                    in zip(dark_rates, ht_rates, bridge_rates, sections) if sec == s]
        if len(s_folios) >= 5:
            s_dark = [x[0] for x in s_folios]
            s_ht = [x[1] for x in s_folios]
            s_bridge = [x[2] for x in s_folios]
            within_corrs[s] = {
                'n': len(s_folios),
                'dark_ht_r': pearson_r(s_dark, s_ht),
                'dark_bridge_r': pearson_r(s_dark, s_bridge),
            }

    # 3. Variance decomposition
    ss_within = ss_total - ss_between
    within_fraction = ss_within / ss_total if ss_total > 0 else 0

    # Verdict
    if section_r2 > 0.50:
        verdict = 'SECTION_DOMINATED'
    elif corr_dark_ht > 0.50 and section_r2 < 0.30:
        verdict = 'HT_COVARIATE'
    elif corr_dark_bridge > 0.50 and section_r2 < 0.30:
        verdict = 'BRIDGE_COVARIATE'
    elif section_r2 > 0.30 and (corr_dark_ht > 0.30 or corr_dark_bridge > 0.30):
        verdict = 'MULTI_DETERMINED'
    else:
        verdict = 'UNEXPLAINED'

    print(f"\nTest 4: Folio-Level Density Regression")
    print(f"  Folios: {n_folios}")
    print(f"  Grand mean dark rate: {grand_mean:.4f}")
    print(f"  Section R²: {section_r2:.4f}")
    print(f"  Section means: {section_means}")
    print(f"  Overall corr(dark, HT): {corr_dark_ht:.4f}")
    print(f"  Overall corr(dark, bridge): {corr_dark_bridge:.4f}")
    print(f"  Within-section correlations: {within_corrs}")
    print(f"  Verdict: {verdict}")

    return {
        'n_folios': n_folios,
        'grand_mean_dark_rate': grand_mean,
        'section_r2': section_r2,
        'section_means': section_means,
        'section_counts': section_counts,
        'ss_total': ss_total,
        'ss_between': ss_between,
        'ss_within': ss_within,
        'within_fraction': within_fraction,
        'overall_corr_dark_ht': corr_dark_ht,
        'overall_corr_dark_bridge': corr_dark_bridge,
        'within_section_correlations': within_corrs,
        'verdict': verdict,
    }


# --- Test 5: Dark Pipeline Line Position ---

def test5_line_position(data):
    """Where in the line do dark-pipeline tokens appear?"""
    line_tokens = data['line_tokens']

    # Classify each token's line position: FIRST, MIDDLE, LAST
    dark_pos = Counter()
    general_ht_pos = Counter()
    grammar_pos = Counter()

    # Stratify by paragraph position
    dark_par1 = Counter()
    dark_body = Counter()
    ht_par1 = Counter()
    ht_body = Counter()

    for (folio, line), tokens in line_tokens.items():
        n = len(tokens)
        if n == 0:
            continue

        is_par1 = tokens[0].get('par_initial', False)

        for idx, tok in enumerate(tokens):
            # Determine line position
            if n == 1:
                pos = 'FIRST'  # solo token counts as first
            elif idx == 0:
                pos = 'FIRST'
            elif idx == n - 1:
                pos = 'LAST'
            else:
                pos = 'MIDDLE'

            is_dark = tok.get('is_dark', False)
            is_grammar = tok.get('is_grammar', False)

            if is_dark:
                dark_pos[pos] += 1
                if is_par1:
                    dark_par1[pos] += 1
                else:
                    dark_body[pos] += 1
            elif not is_grammar:
                # General HT (non-dark, non-grammar)
                general_ht_pos[pos] += 1
                if is_par1:
                    ht_par1[pos] += 1
                else:
                    ht_body[pos] += 1

            if is_grammar:
                grammar_pos[pos] += 1

    # Compute rates
    positions = ['FIRST', 'MIDDLE', 'LAST']

    def rates(counter):
        total = sum(counter.values())
        if total == 0:
            return {p: 0.0 for p in positions}, total
        return {p: counter.get(p, 0) / total for p in positions}, total

    dark_rates, dark_total = rates(dark_pos)
    ht_rates, ht_total = rates(general_ht_pos)
    grammar_rates, grammar_total = rates(grammar_pos)

    dark_par1_rates, dark_par1_total = rates(dark_par1)
    dark_body_rates, dark_body_total = rates(dark_body)
    ht_par1_rates, ht_par1_total = rates(ht_par1)
    ht_body_rates, ht_body_total = rates(ht_body)

    # Chi-square: dark-pipeline vs general-HT line position
    observed = [
        [dark_pos.get(p, 0) for p in positions],
        [general_ht_pos.get(p, 0) for p in positions],
    ]
    chi2_dark_vs_ht = chi_square_2xk(observed)

    # Chi-square: dark-pipeline vs grammar
    observed_dg = [
        [dark_pos.get(p, 0) for p in positions],
        [grammar_pos.get(p, 0) for p in positions],
    ]
    chi2_dark_vs_grammar = chi_square_2xk(observed_dg)

    # Compare to C803 reference: HT first=45.8%, last=42.9%, middle=25.7%
    c803_reference = {'FIRST': 0.458, 'LAST': 0.429, 'MIDDLE': 0.257}

    # Boundary rate = FIRST + LAST
    dark_boundary = dark_rates['FIRST'] + dark_rates['LAST']
    ht_boundary = ht_rates['FIRST'] + ht_rates['LAST']

    # Verdict
    if chi2_dark_vs_ht['p'] < 0.05:
        if dark_boundary > ht_boundary:
            if dark_boundary > 0.90:
                verdict = 'BOUNDARY_SUPER_ENRICHED'
            else:
                verdict = 'BOUNDARY_ENRICHED'
        elif dark_rates['MIDDLE'] > ht_rates['MIDDLE']:
            verdict = 'INTERIOR_ENRICHED'
        else:
            verdict = 'POSITION_DIVERGENT'
    else:
        verdict = 'POSITION_NEUTRAL'

    print(f"\nTest 5: Dark Pipeline Line Position")
    print(f"  Dark tokens: {dark_total}, General HT: {ht_total}, Grammar: {grammar_total}")
    print(f"  Dark rates: {dark_rates}")
    print(f"  General HT rates: {ht_rates}")
    print(f"  Grammar rates: {grammar_rates}")
    print(f"  C803 reference: {c803_reference}")
    print(f"  Dark boundary rate: {dark_boundary:.4f}")
    print(f"  HT boundary rate: {ht_boundary:.4f}")
    print(f"  Chi-square (dark vs HT): chi2={chi2_dark_vs_ht['chi2']:.3f}, "
          f"p={chi2_dark_vs_ht['p']:.4f}")
    print(f"  Chi-square (dark vs grammar): chi2={chi2_dark_vs_grammar['chi2']:.3f}, "
          f"p={chi2_dark_vs_grammar['p']:.4f}")
    print(f"  Verdict: {verdict}")

    return {
        'dark_position_counts': dict(dark_pos),
        'general_ht_position_counts': dict(general_ht_pos),
        'grammar_position_counts': dict(grammar_pos),
        'dark_rates': dark_rates,
        'general_ht_rates': ht_rates,
        'grammar_rates': grammar_rates,
        'dark_total': dark_total,
        'general_ht_total': ht_total,
        'grammar_total': grammar_total,
        'dark_boundary_rate': dark_boundary,
        'ht_boundary_rate': ht_boundary,
        'c803_reference': c803_reference,
        'chi_square_dark_vs_ht': chi2_dark_vs_ht,
        'chi_square_dark_vs_grammar': chi2_dark_vs_grammar,
        'stratification': {
            'dark_par1': {'rates': dark_par1_rates, 'n': dark_par1_total},
            'dark_body': {'rates': dark_body_rates, 'n': dark_body_total},
            'ht_par1': {'rates': ht_par1_rates, 'n': ht_par1_total},
            'ht_body': {'rates': ht_body_rates, 'n': ht_body_total},
        },
        'verdict': verdict,
    }


# --- Test 6: Frequency Modulation Decomposition ---

def test6_frequency_modulation(data):
    """Apply C1134's JS decomposition to dark-pipeline MIDDLEs only."""
    dark_pipeline_set = data['dark_pipeline_set']
    middle_section_freq = data['middle_section_freq']

    # Build per-section dark-pipeline MIDDLE frequency profiles
    sections = set()
    dark_section_profiles = defaultdict(Counter)  # section -> {middle: count}

    for mid in dark_pipeline_set:
        sec_dist = middle_section_freq.get(mid, Counter())
        for sec, count in sec_dist.items():
            sections.add(sec)
            dark_section_profiles[sec][mid] += count

    sections = sorted(sections)

    # Per-section stats
    section_stats = {}
    for sec in sections:
        profile = dark_section_profiles[sec]
        section_stats[sec] = {
            'n_middles': len(profile),
            'n_tokens': sum(profile.values()),
        }

    # Pairwise JS divergence between sections
    js_pairs = {}
    js_values = []
    for i, s1 in enumerate(sections):
        for s2 in sections[i + 1:]:
            js = jensen_shannon(dark_section_profiles[s1], dark_section_profiles[s2])
            key = f"{s1}_vs_{s2}"
            js_pairs[key] = js
            js_values.append(js)

    mean_js = sum(js_values) / len(js_values) if js_values else 0

    # Compare to C1134 PP baseline (mean JS = 0.124)
    c1134_baseline = 0.124
    ratio_to_baseline = mean_js / c1134_baseline if c1134_baseline > 0 else 0

    # Also compute JS using ALL dark-pipeline MIDDLEs (not just per-section)
    # to get the modulation magnitude
    # Per-section Herfindahl for dark MIDDLEs
    section_herfs = {}
    for sec in sections:
        section_herfs[sec] = herfindahl(dark_section_profiles[sec])

    # Verdict
    if ratio_to_baseline > 1.5:
        verdict = 'HYPER_MODULATED'
    elif ratio_to_baseline > 0.75:
        verdict = 'STANDARD_MODULATION'
    else:
        verdict = 'HYPO_MODULATED'

    print(f"\nTest 6: Frequency Modulation Decomposition")
    print(f"  Sections: {sections}")
    print(f"  Section stats: {section_stats}")
    print(f"  Pairwise JS divergences: {js_pairs}")
    print(f"  Mean JS: {mean_js:.4f}")
    print(f"  C1134 baseline: {c1134_baseline}")
    print(f"  Ratio to baseline: {ratio_to_baseline:.4f}")
    print(f"  Section Herfindahls: {section_herfs}")
    print(f"  Verdict: {verdict}")

    return {
        'sections': sections,
        'section_stats': section_stats,
        'pairwise_js': js_pairs,
        'mean_js': mean_js,
        'c1134_baseline': c1134_baseline,
        'ratio_to_baseline': ratio_to_baseline,
        'section_herfindahls': section_herfs,
        'verdict': verdict,
    }


# --- Synthesis ---

def synthesize(results):
    """Combine all test verdicts into an overall assessment."""
    verdicts = {f'test{i}': results[f'test{i}']['verdict'] for i in range(1, 7)}

    t1 = verdicts['test1']  # CONCENTRATED / DISPERSED / EQUIVALENT
    t2 = verdicts['test2']  # ATOM_POOL_EFFECT / GRAMMAR_MODIFICATION / REVERSE_ENRICHMENT
    t3 = verdicts['test3']  # SLOT_DIFFERENTIATED / SLOT_UNIFORM
    t4 = verdicts['test4']  # SECTION_DOMINATED / HT_COVARIATE / etc
    t5 = verdicts['test5']  # BOUNDARY_ENRICHED / etc
    t6 = verdicts['test6']  # HYPER_MODULATED / STANDARD_MODULATION / HYPO_MODULATED

    # Core question: what drives dark-pipeline structure?
    findings = []

    # Atom profile finding
    if t1 == 'CONCENTRATED':
        findings.append('Dark-exclusive atoms are more section-concentrated than shared atoms.')
    elif t1 == 'DISPERSED':
        findings.append('Dark-exclusive atoms are more dispersed than shared atoms.')
    else:
        findings.append('Dark-exclusive and shared atoms have equivalent section concentration.')

    # Ordering divergence finding
    if t2 == 'ATOM_POOL_EFFECT':
        findings.append('C1065 ordering divergence is driven by dark-exclusive atom pool.')
    elif t2 == 'GRAMMAR_MODIFICATION':
        findings.append('C1065 ordering divergence is NOT explained by atom pool — genuine grammar modification.')
    else:
        findings.append('Dark-exclusive atoms are enriched in MATCHING pairs (reverse of prediction).')

    # Slot grammar finding
    if t3 == 'SLOT_DIFFERENTIATED':
        findings.append('Dark-exclusive and shared atoms occupy different positional slots.')
    else:
        findings.append('Dark-exclusive and shared atoms occupy equivalent positional slots.')

    # Density driver
    findings.append(f'Density driver: {t4}.')

    # Line position finding
    findings.append(f'Line position: {t5}.')

    # Modulation finding
    findings.append(f'Frequency modulation: {t6}.')

    # Overall verdict synthesis
    if t2 == 'GRAMMAR_MODIFICATION' and t4 == 'SECTION_DOMINATED':
        overall = 'FREQUENCY_MODULATED_GRAMMAR_VARIANT'
        summary = ('Dark pipeline uses a genuine grammar variant (not atom-pool artifact). '
                   'Section identity dominates density. '
                   'Modulation profile: ' + t6 + '.')
    elif t2 == 'ATOM_POOL_EFFECT':
        overall = 'ATOM_POOL_DRIVEN_DIVERGENCE'
        summary = ('C1065 divergence is a vocabulary artifact of the dark-exclusive atom pool. '
                   'Density driver: ' + t4 + '.')
    elif t2 == 'GRAMMAR_MODIFICATION' and t6 == 'HYPER_MODULATED':
        overall = 'HYPER_MODULATED_VARIANT'
        summary = ('Dark pipeline is a genuine grammar variant with hyper-modulated '
                   'frequency profiles. Density driver: ' + t4 + '.')
    elif t2 == 'GRAMMAR_MODIFICATION':
        overall = 'GRAMMAR_VARIANT_MECHANISM_OPEN'
        summary = ('Dark pipeline is a genuine grammar variant. '
                   f'Density: {t4}. Modulation: {t6}. '
                   'Mechanism not fully resolved.')
    else:
        overall = 'UNRESOLVED'
        summary = 'Could not synthesize a clear verdict.'

    verdicts['overall'] = overall
    verdicts['summary'] = summary
    verdicts['findings'] = findings

    print(f"\n{'='*60}")
    print(f"OVERALL VERDICT: {overall}")
    for f in findings:
        print(f"  - {f}")
    print(f"\n  {summary}")
    print(f"{'='*60}")

    return verdicts


# --- Main ---

def main():
    print("Phase 409: Dark Pipeline Internal Architecture")
    print("=" * 60)

    data = load_data()

    # Validation
    print(f"\nValidation:")
    print(f"  Dark pipeline MIDDLEs: {len(data['dark_pipeline_set'])} (expect 300)")
    print(f"  Dark-exclusive atoms: {len(data['dark_exclusive_atoms'])} (expect 25)")
    print(f"  Shared atoms: {len(data['shared_atoms'])} (expect 25)")
    print(f"  Bridge MIDDLEs: {len(data['bridge_set'])} (expect 85)")
    print(f"  Folios: {len(data['folio_section'])} (expect ~83)")
    print(f"  B tokens scanned: {data['n_scanned']} (expect ~23243)")
    print(f"  Dark-pipeline tokens: {len(data['dark_tokens'])} (expect ~1696)")

    results = {}
    results['test1'] = test1_atom_characterization(data)
    results['test2'] = test2_ordering_divergence(data)
    results['test3'] = test3_atom_slot_grammar(data)
    results['test4'] = test4_density_regression(data)
    results['test5'] = test5_line_position(data)
    results['test6'] = test6_frequency_modulation(data)
    results['verdicts'] = synthesize(results)

    results['metadata'] = {
        'phase': 'DARK_PIPELINE_INTERNAL_ARCHITECTURE',
        'phase_number': 409,
        'script': 'dark_pipeline_internal.py',
        'n_dark_pipeline': len(data['dark_pipeline_set']),
        'n_dark_exclusive_atoms': len(data['dark_exclusive_atoms']),
        'n_shared_atoms': len(data['shared_atoms']),
        'n_bridge': len(data['bridge_set']),
        'n_folios': len(data['folio_section']),
        'n_b_tokens_scanned': data['n_scanned'],
        'n_dark_tokens': len(data['dark_tokens']),
    }

    # Write output
    out_dir = ROOT / 'phases/DARK_PIPELINE_INTERNAL_ARCHITECTURE/results'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'dark_pipeline_internal.json'

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {out_path}")
    size = out_path.stat().st_size
    print(f"Output size: {size:,} bytes")


if __name__ == '__main__':
    main()

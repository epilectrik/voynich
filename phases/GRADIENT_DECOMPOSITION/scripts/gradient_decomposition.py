"""
Phase 451: GRADIENT_DECOMPOSITION

Decomposes paragraph gradient constraints by suffix mode (A/B) to determine
whether observed gradients are:
  GENUINE  - survive within Mode B lines alone
  ARTIFACT - explained by shifting Mode A/B proportions through paragraph
  MIXTURE  - reduced but still significant within Mode B

Test Battery (7 tests, Bonferroni p < 0.007):
  T1: Mode proportion gradient (does Mode A concentrate early?)
  T2: Vocabulary rarity decomposition (retests C932)
  T3: Prep verb position decomposition (retests C933)
  T4: Kernel composition decomposition (retests C965)
  T5: FL reset decomposition (retests C1227)
  T6: PREFIX switch decomposition (retests C1228)
  T7: Suffix/PREFIX trajectory decomposition (retests C676)

References: C932, C933, C934, C965, C1206, C1227, C1228, C676, C1229, C1231, C1258
"""

import sys, json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy.stats import spearmanr, pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

N_PERM = 1000
BONFERRONI_ALPHA = 0.05 / 7  # 7 tests -> p < 0.007
RNG = np.random.RandomState(42)

# ── MODE CLASSIFICATION (C1231 centroids) ─────────────────────────

TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])


def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]
    for tok in line_toks:
        sfx = tok['suffix']
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


# ── FL STAGE MAP (C777) ──────────────────────────────────────────

FL_MIDDLES = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL',
}
FL_ORDERED = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']
FL_RANK = {s: i for i, s in enumerate(FL_ORDERED)}

# ── PREP MIDDLEs (C933) ──────────────────────────────────────────

PREP_MIDDLES = {'te', 'pch', 'tch', 'lch'}

# ── PREFIX FAMILIES (C676) ────────────────────────────────────────

PREFIX_FAMILIES = {
    'qo': 'qo', 'da': 'da', 'ot': 'ot', 'ch': 'ch', 'sh': 'sh',
    'ol': 'ol', 'ok': 'ok', 'ct': 'ct',
}

E_FAMILY_SUFFIXES = {'eey', 'ey', 'e'}


# ── DATA LOADING ──────────────────────────────────────────────────

def load_data():
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        tokens.append({
            'folio': t.folio,
            'line': t.line,
            'word': t.word,
            'middle': m.middle if m else '',
            'suffix': m.suffix if m else '',
            'prefix': m.prefix if m else '',
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'kernels': [c for c in 'khe' if c in (m.middle if m else '')],
        })

    # Group into folios -> paragraphs -> lines
    folio_tokens = defaultdict(list)
    for tok in tokens:
        folio_tokens[tok['folio']].append(tok)

    folios = {}
    for folio, ftoks in folio_tokens.items():
        ftoks.sort(key=lambda t: t['line'])
        lines_dict = defaultdict(list)
        for tok in ftoks:
            lines_dict[tok['line']].append(tok)
        line_nums = sorted(lines_dict.keys())

        paragraphs = []
        current_para = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append((ln, line_toks))
        if current_para:
            paragraphs.append(current_para)

        folios[folio] = paragraphs

    return folios, tokens


def build_annotated_paragraphs(folios, min_body_lines):
    """Build paragraphs with body lines annotated by mode and quintile."""
    paragraphs = []
    for folio, paras in folios.items():
        for para in paras:
            if len(para) < 2:
                continue
            body_lines = para[1:]  # skip header
            if len(body_lines) < min_body_lines:
                continue

            n_body = len(body_lines)
            annotated = []
            for li, (ln, toks) in enumerate(body_lines):
                norm_pos = li / (n_body - 1) if n_body > 1 else 0.0
                quintile = min(int(norm_pos * 5), 4)
                mode = classify_suffix_mode(toks)
                annotated.append({
                    'line_num': ln,
                    'toks': toks,
                    'mode': mode,
                    'norm_pos': norm_pos,
                    'quintile': quintile,
                    'body_index': li,
                    'n_toks': len(toks),
                })

            paragraphs.append({
                'folio': folio,
                'lines': annotated,
                'n_body': n_body,
            })
    return paragraphs


# ── RARITY CLASSIFICATION (C932 methodology) ─────────────────────

def build_folio_spread():
    """Count how many folios each MIDDLE appears in."""
    tx = Transcript()
    morph = Morphology()
    mid_folios = defaultdict(set)
    for t in tx.currier_b():
        if t.placement.startswith('L') or '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        if m and m.middle:
            mid_folios[m.middle].add(t.folio)
    return {mid: len(folios) for mid, folios in mid_folios.items()}


def classify_rarity(middle, folio_spread):
    n = folio_spread.get(middle, 0)
    if n == 1:
        return 'UNIQUE'
    elif n <= 5:
        return 'RARE'
    elif n <= 50:
        return 'COMMON'
    else:
        return 'UNIVERSAL'


# ── T1: MODE PROPORTION GRADIENT ──────────────────────────────────

def t1_mode_proportion_gradient(paragraphs):
    """T1: Does Mode A fraction change through the paragraph body?"""
    print("\nT1: Mode Proportion Gradient")
    print("-" * 60)

    # Per quintile: count Mode A and Mode B lines
    quintile_counts = {q: {'A': 0, 'B': 0} for q in range(5)}
    for para in paragraphs:
        for line in para['lines']:
            if line['mode']:
                quintile_counts[line['quintile']][line['mode']] += 1

    # Mode A fraction per quintile
    quintile_fracs = {}
    for q in range(5):
        total = quintile_counts[q]['A'] + quintile_counts[q]['B']
        quintile_fracs[q] = quintile_counts[q]['A'] / total if total > 0 else 0.0

    qs = list(range(5))
    fracs = [quintile_fracs[q] for q in qs]
    rho, p_param = spearmanr(qs, fracs)

    # Also compute per-paragraph Mode A fraction by position
    all_positions = []
    all_is_a = []
    for para in paragraphs:
        for line in para['lines']:
            if line['mode']:
                all_positions.append(line['norm_pos'])
                all_is_a.append(1.0 if line['mode'] == 'A' else 0.0)

    rho_line, p_line = spearmanr(all_positions, all_is_a)

    print(f"  Quintile Mode A fractions: {[f'{f:.3f}' for f in fracs]}")
    print(f"  Spearman rho (quintile): {rho:.4f} (p={p_param:.4f})")
    print(f"  Spearman rho (line-level): {rho_line:.4f} (p={p_line:.6f})")
    print(f"  Q0 Mode A: {fracs[0]:.3f}, Q4 Mode A: {fracs[4]:.3f}")

    direction = "Mode A concentrates EARLY" if rho < 0 else "Mode A concentrates LATE" if rho > 0 else "NO gradient"
    print(f"  Direction: {direction}")
    passes = abs(rho_line) > 0.03 and p_line < BONFERRONI_ALPHA
    print(f"  {'PASS' if passes else 'FAIL'}")

    return {
        'test': 'T1_mode_proportion_gradient',
        'quintile_mode_a_fracs': {str(q): round(f, 4) for q, f in quintile_fracs.items()},
        'quintile_rho': round(float(rho), 4),
        'quintile_p': round(float(p_param), 4),
        'line_level_rho': round(float(rho_line), 4),
        'line_level_p': round(float(p_line), 6),
        'direction': direction,
        'n_lines': len(all_positions),
        'n_paragraphs': len(paragraphs),
        'pass': bool(passes),
        'verdict': 'PASS' if passes else 'FAIL',
    }


# ── T2: VOCABULARY RARITY DECOMPOSITION (C932) ───────────────────

def t2_vocabulary_rarity(paragraphs, folio_spread):
    """T2: Does vocab rarity gradient survive within Mode B?"""
    print("\nT2: Vocabulary Rarity Decomposition (retests C932)")
    print("-" * 60)

    def compute_rarity_gradient(lines_by_quintile):
        """Compute RARE and UNIVERSAL fractions per quintile."""
        quintile_rare = {}
        quintile_universal = {}
        quintile_hapax = {}
        for q in range(5):
            toks = lines_by_quintile.get(q, [])
            middles = [t['middle'] for t in toks if t['middle']]
            if not middles:
                quintile_rare[q] = 0.0
                quintile_universal[q] = 0.0
                quintile_hapax[q] = 0.0
                continue
            rarities = [classify_rarity(m, folio_spread) for m in middles]
            n = len(rarities)
            quintile_rare[q] = sum(1 for r in rarities if r == 'RARE') / n
            quintile_universal[q] = sum(1 for r in rarities if r == 'UNIVERSAL') / n
            # Hapax: unique within this quintile's lines
            mid_counts = Counter(middles)
            quintile_hapax[q] = sum(1 for c in mid_counts.values() if c == 1) / len(mid_counts) if mid_counts else 0.0

        qs = list(range(5))
        rare_vals = [quintile_rare[q] for q in qs]
        univ_vals = [quintile_universal[q] for q in qs]

        if len(set(rare_vals)) <= 1:
            rare_r = 0.0
        else:
            rare_r, _ = pearsonr(qs, rare_vals)
        if len(set(univ_vals)) <= 1:
            univ_r = 0.0
        else:
            univ_r, _ = pearsonr(qs, univ_vals)

        return {
            'rare_fracs': [round(v, 4) for v in rare_vals],
            'universal_fracs': [round(v, 4) for v in univ_vals],
            'rare_r': round(float(rare_r), 4),
            'universal_r': round(float(univ_r), 4),
        }

    # Collect tokens by quintile for: all, Mode B, Mode A
    all_by_q = defaultdict(list)
    mode_b_by_q = defaultdict(list)
    mode_a_by_q = defaultdict(list)

    for para in paragraphs:
        for line in para['lines']:
            q = line['quintile']
            for tok in line['toks']:
                all_by_q[q].append(tok)
            if line['mode'] == 'B':
                for tok in line['toks']:
                    mode_b_by_q[q].append(tok)
            elif line['mode'] == 'A':
                for tok in line['toks']:
                    mode_a_by_q[q].append(tok)

    agg = compute_rarity_gradient(all_by_q)
    mode_b = compute_rarity_gradient(mode_b_by_q)
    mode_a = compute_rarity_gradient(mode_a_by_q)

    print(f"  AGGREGATE:  RARE r={agg['rare_r']}, UNIVERSAL r={agg['universal_r']}  (C932: -0.97, +0.92)")
    print(f"  MODE B:     RARE r={mode_b['rare_r']}, UNIVERSAL r={mode_b['universal_r']}")
    print(f"  MODE A:     RARE r={mode_a['rare_r']}, UNIVERSAL r={mode_a['universal_r']}")
    print(f"  Aggregate RARE fracs: {agg['rare_fracs']}")
    print(f"  Mode B RARE fracs:    {mode_b['rare_fracs']}")
    print(f"  Mode A RARE fracs:    {mode_a['rare_fracs']}")

    # Classification
    agg_mag = abs(agg['rare_r'])
    b_mag = abs(mode_b['rare_r'])
    if agg_mag < 0.3:
        classification = 'NO_GRADIENT'
    elif b_mag >= agg_mag * 0.5:
        classification = 'GENUINE'
    elif b_mag < 0.3:
        classification = 'ARTIFACT'
    else:
        classification = 'MIXTURE'

    print(f"  Classification: {classification}")

    return {
        'test': 'T2_vocabulary_rarity',
        'aggregate': agg,
        'mode_b': mode_b,
        'mode_a': mode_a,
        'classification': classification,
        'c932_reference': {'rare_r': -0.97, 'universal_r': 0.92},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── T3: PREP VERB POSITION (C933) ────────────────────────────────

def t3_prep_verb_position(paragraphs):
    """T3: Do prep verbs still concentrate early within Mode B?"""
    print("\nT3: Prep Verb Position Decomposition (retests C933)")
    print("-" * 60)

    # Collect prep verb positions by mode
    all_prep_pos = defaultdict(list)      # middle -> [norm_pos]
    mode_b_prep_pos = defaultdict(list)
    mode_a_prep_pos = defaultdict(list)

    for para in paragraphs:
        for line in para['lines']:
            for tok in line['toks']:
                if tok['middle'] in PREP_MIDDLES:
                    all_prep_pos[tok['middle']].append(line['norm_pos'])
                    if line['mode'] == 'B':
                        mode_b_prep_pos[tok['middle']].append(line['norm_pos'])
                    elif line['mode'] == 'A':
                        mode_a_prep_pos[tok['middle']].append(line['norm_pos'])

    results_detail = {}
    for mid in sorted(PREP_MIDDLES):
        agg_pos = np.mean(all_prep_pos[mid]) if all_prep_pos[mid] else 0.5
        b_pos = np.mean(mode_b_prep_pos[mid]) if mode_b_prep_pos[mid] else 0.5
        a_pos = np.mean(mode_a_prep_pos[mid]) if mode_a_prep_pos[mid] else 0.5
        results_detail[mid] = {
            'agg_mean_pos': round(float(agg_pos), 3),
            'mode_b_mean_pos': round(float(b_pos), 3),
            'mode_a_mean_pos': round(float(a_pos), 3),
            'n_all': len(all_prep_pos[mid]),
            'n_mode_b': len(mode_b_prep_pos[mid]),
            'n_mode_a': len(mode_a_prep_pos[mid]),
        }
        print(f"  {mid}: agg={agg_pos:.3f}  B={b_pos:.3f}  A={a_pos:.3f}  "
              f"(n: all={len(all_prep_pos[mid])}, B={len(mode_b_prep_pos[mid])}, A={len(mode_a_prep_pos[mid])})")

    # Aggregate: do all prep verbs still have position < 0.5 within Mode B?
    all_b_positions = []
    for mid in PREP_MIDDLES:
        all_b_positions.extend(mode_b_prep_pos[mid])

    if len(all_b_positions) >= 20:
        b_mean = np.mean(all_b_positions)
        # Permutation: shuffle positions within Mode B lines
        perm_means = []
        for _ in range(N_PERM):
            perm = RNG.permutation(all_b_positions)
            perm_means.append(np.mean(perm[:len(all_b_positions)]))
        p_value = np.mean([pm <= b_mean for pm in perm_means])
    else:
        b_mean = 0.5
        p_value = 1.0

    # Classification
    agg_mean_all = np.mean([np.mean(all_prep_pos[m]) for m in PREP_MIDDLES if all_prep_pos[m]])
    if b_mean < 0.45 and p_value < BONFERRONI_ALPHA:
        classification = 'GENUINE'
    elif b_mean >= 0.47:
        classification = 'ARTIFACT'
    else:
        classification = 'MIXTURE'

    print(f"\n  All prep verbs (Mode B): mean position = {b_mean:.3f} (agg = {agg_mean_all:.3f})")
    print(f"  Permutation p = {p_value:.4f}")
    print(f"  Classification: {classification}")

    return {
        'test': 'T3_prep_verb_position',
        'detail': results_detail,
        'mode_b_combined_mean_pos': round(float(b_mean), 4),
        'aggregate_combined_mean_pos': round(float(agg_mean_all), 4),
        'perm_p': round(float(p_value), 4),
        'classification': classification,
        'c933_reference': {'te': 0.394, 'pch': 0.429, 'tch': 0.424, 'lch': 0.445},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── T4: KERNEL COMPOSITION (C965) ────────────────────────────────

def t4_kernel_composition(paragraphs):
    """T4: Does kernel composition gradient survive within Mode B?"""
    print("\nT4: Kernel Composition Decomposition (retests C965)")
    print("-" * 60)

    def compute_kernel_gradient(lines_list):
        """Compute kernel fractions and partial Spearman rho vs position."""
        if len(lines_list) < 20:
            return {'h_rho': 0.0, 'e_rho': 0.0, 'k_rho': 0.0, 'n': 0}

        positions = []
        h_fracs = []
        e_fracs = []
        k_fracs = []
        lengths = []

        for line in lines_list:
            toks = line['toks']
            n = len(toks)
            if n == 0:
                continue
            h_count = sum(1 for t in toks if 'h' in t['kernels'])
            e_count = sum(1 for t in toks if 'e' in t['kernels'])
            k_count = sum(1 for t in toks if 'k' in t['kernels'])
            positions.append(line['norm_pos'])
            h_fracs.append(h_count / n)
            e_fracs.append(e_count / n)
            k_fracs.append(k_count / n)
            lengths.append(n)

        positions = np.array(positions)
        h_fracs = np.array(h_fracs)
        e_fracs = np.array(e_fracs)
        k_fracs = np.array(k_fracs)
        lengths = np.array(lengths)

        # Partial Spearman: residualize for line length via OLS
        def partial_spearman(x, y, z):
            """Spearman rho between x and y, controlling for z."""
            from scipy.stats import rankdata
            x_rank = rankdata(x)
            y_rank = rankdata(y)
            z_rank = rankdata(z)
            # Residualize x_rank and y_rank on z_rank
            z_mean = np.mean(z_rank)
            z_var = np.var(z_rank)
            if z_var < 1e-10:
                return spearmanr(x, y)
            x_res = x_rank - (np.cov(x_rank, z_rank)[0, 1] / z_var) * (z_rank - z_mean)
            y_res = y_rank - (np.cov(y_rank, z_rank)[0, 1] / z_var) * (z_rank - z_mean)
            return pearsonr(x_res, y_res)

        h_rho, h_p = partial_spearman(positions, h_fracs, lengths)
        e_rho, e_p = partial_spearman(positions, e_fracs, lengths)
        k_rho, k_p = partial_spearman(positions, k_fracs, lengths)

        # Quintile means
        quintile_h = [np.mean(h_fracs[(positions >= q/5) & (positions < (q+1)/5)])
                      if np.any((positions >= q/5) & (positions < (q+1)/5)) else 0
                      for q in range(5)]
        quintile_e = [np.mean(e_fracs[(positions >= q/5) & (positions < (q+1)/5)])
                      if np.any((positions >= q/5) & (positions < (q+1)/5)) else 0
                      for q in range(5)]

        return {
            'h_rho': round(float(h_rho), 4), 'h_p': round(float(h_p), 6),
            'e_rho': round(float(e_rho), 4), 'e_p': round(float(e_p), 6),
            'k_rho': round(float(k_rho), 4), 'k_p': round(float(k_p), 6),
            'n': len(positions),
            'quintile_h': [round(float(v), 4) for v in quintile_h],
            'quintile_e': [round(float(v), 4) for v in quintile_e],
        }

    # Collect lines by mode
    all_lines = []
    mode_b_lines = []
    mode_a_lines = []
    for para in paragraphs:
        for line in para['lines']:
            all_lines.append(line)
            if line['mode'] == 'B':
                mode_b_lines.append(line)
            elif line['mode'] == 'A':
                mode_a_lines.append(line)

    agg = compute_kernel_gradient(all_lines)
    mode_b = compute_kernel_gradient(mode_b_lines)
    mode_a = compute_kernel_gradient(mode_a_lines)

    print(f"  AGGREGATE:  h={agg['h_rho']} (p={agg['h_p']}), e={agg['e_rho']} (p={agg['e_p']}), k={agg['k_rho']}  (C965: h=+0.10, e=-0.09)")
    print(f"  MODE B:     h={mode_b['h_rho']} (p={mode_b['h_p']}), e={mode_b['e_rho']} (p={mode_b['e_p']}), k={mode_b['k_rho']}")
    print(f"  MODE A:     h={mode_a['h_rho']} (p={mode_a['h_p']}), e={mode_a['e_rho']} (p={mode_a['e_p']}), k={mode_a['k_rho']}")
    print(f"  Quintile h (agg): {agg.get('quintile_h', [])}")
    print(f"  Quintile h (B):   {mode_b.get('quintile_h', [])}")

    # Classification based on h_rho (the primary gradient in C965)
    agg_h = abs(agg['h_rho'])
    b_h = abs(mode_b['h_rho'])
    if agg_h < 0.03:
        classification = 'NO_GRADIENT'
    elif b_h >= agg_h * 0.5:
        classification = 'GENUINE'
    elif b_h < 0.03:
        classification = 'ARTIFACT'
    else:
        classification = 'MIXTURE'

    print(f"  Classification: {classification}")

    return {
        'test': 'T4_kernel_composition',
        'aggregate': agg,
        'mode_b': mode_b,
        'mode_a': mode_a,
        'classification': classification,
        'c965_reference': {'h_rho': 0.1005, 'e_rho': -0.0863, 'k_rho': -0.0027},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── T5: FL RESET DECOMPOSITION (C1227) ───────────────────────────

def t5_fl_reset(folios, min_body=6):
    """T5: Do FL resets concentrate at cross-mode transitions?"""
    print("\nT5: FL Reset Decomposition (retests C1227)")
    print("-" * 60)

    paragraphs = build_annotated_paragraphs(folios, min_body)

    # For each consecutive body line pair: extract FL transition and mode transition
    transition_types = {'BB': [], 'AB': [], 'BA': [], 'AA': []}
    all_transitions = []

    for para in paragraphs:
        lines = para['lines']
        for i in range(len(lines) - 1):
            curr = lines[i]
            nxt = lines[i + 1]
            if not curr['mode'] or not nxt['mode']:
                continue

            # Get last FL of current line
            curr_fl = None
            for tok in reversed(curr['toks']):
                stage = FL_MIDDLES.get(tok['middle'])
                if stage:
                    curr_fl = stage
                    break

            # Get first FL of next line
            nxt_fl = None
            for tok in nxt['toks']:
                stage = FL_MIDDLES.get(tok['middle'])
                if stage:
                    nxt_fl = stage
                    break

            if curr_fl is None or nxt_fl is None:
                continue

            is_regression = FL_RANK[nxt_fl] < FL_RANK[curr_fl]
            mode_pair = curr['mode'] + nxt['mode']

            transition_types[mode_pair].append({
                'from': curr_fl, 'to': nxt_fl,
                'regression': is_regression,
            })
            all_transitions.append({
                'from': curr_fl, 'to': nxt_fl,
                'regression': is_regression,
                'mode_pair': mode_pair,
            })

    # Compute regression rates by mode pair
    results_by_type = {}
    for mp in ['BB', 'AB', 'BA', 'AA']:
        trans = transition_types[mp]
        if not trans:
            results_by_type[mp] = {'regression_rate': 0.0, 'n': 0}
            continue
        reg_rate = sum(1 for t in trans if t['regression']) / len(trans)
        results_by_type[mp] = {
            'regression_rate': round(reg_rate, 4),
            'n': len(trans),
        }

    agg_reg = sum(1 for t in all_transitions if t['regression']) / len(all_transitions) if all_transitions else 0.0

    for mp in ['BB', 'AB', 'BA', 'AA']:
        r = results_by_type[mp]
        print(f"  {mp}: regression rate = {r['regression_rate']:.3f} (n={r['n']})")
    print(f"  Aggregate: {agg_reg:.3f} (C1227: 0.364)")

    # Is BB regression rate lower than cross-mode?
    bb_rate = results_by_type['BB']['regression_rate']
    cross_rates = []
    for mp in ['AB', 'BA']:
        if results_by_type[mp]['n'] > 0:
            cross_rates.append(results_by_type[mp]['regression_rate'])
    cross_mean = np.mean(cross_rates) if cross_rates else 0.0

    diff = cross_mean - bb_rate
    print(f"  BB rate: {bb_rate:.3f}, Cross-mode mean: {cross_mean:.3f}, diff: {diff:+.3f}")

    # Permutation: shuffle mode pair labels across transitions
    perm_diffs = []
    mode_labels = [t['mode_pair'] for t in all_transitions]
    regressions = [t['regression'] for t in all_transitions]

    for _ in range(N_PERM):
        perm_labels = list(mode_labels)
        RNG.shuffle(perm_labels)
        perm_bb_reg = [r for r, l in zip(regressions, perm_labels) if l == 'BB']
        perm_cross_reg = [r for r, l in zip(regressions, perm_labels) if l in ('AB', 'BA')]
        pbb = np.mean(perm_bb_reg) if perm_bb_reg else 0.0
        pcr = np.mean(perm_cross_reg) if perm_cross_reg else 0.0
        perm_diffs.append(pcr - pbb)

    p_value = np.mean([pd >= diff for pd in perm_diffs])
    print(f"  Permutation p = {p_value:.4f}")

    if diff > 0.05 and p_value < BONFERRONI_ALPHA:
        classification = 'ARTIFACT'  # FL resets are mode-transition events
    elif diff < 0.02:
        classification = 'GENUINE'  # FL resets are track-independent
    else:
        classification = 'MIXTURE'

    print(f"  Classification: {classification}")

    return {
        'test': 'T5_fl_reset',
        'by_mode_pair': results_by_type,
        'aggregate_regression_rate': round(float(agg_reg), 4),
        'bb_rate': round(float(bb_rate), 4),
        'cross_mode_mean_rate': round(float(cross_mean), 4),
        'diff': round(float(diff), 4),
        'perm_p': round(float(p_value), 4),
        'n_total': len(all_transitions),
        'classification': classification,
        'c1227_reference': {'aggregate_regression_rate': 0.364},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── T6: PREFIX SWITCH DECOMPOSITION (C1228) ──────────────────────

def t6_prefix_switch(folios, min_body=3):
    """T6: Are PREFIX switches really just mode alternation?"""
    print("\nT6: PREFIX Switch Decomposition (retests C1228)")
    print("-" * 60)

    paragraphs = build_annotated_paragraphs(folios, min_body)

    def prefix_distribution(toks):
        """Count PREFIX family distribution for a line."""
        counts = defaultdict(int)
        for tok in toks:
            pfx = tok['prefix']
            family = PREFIX_FAMILIES.get(pfx, 'other' if pfx else 'none')
            counts[family] += 1
        return counts

    def jensen_shannon(dist_a, dist_b):
        """JSD between two count distributions."""
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        n_a = sum(dist_a.values())
        n_b = sum(dist_b.values())
        if n_a == 0 or n_b == 0:
            return 0.0
        p = np.array([dist_a.get(k, 0) / n_a for k in all_keys])
        q = np.array([dist_b.get(k, 0) / n_b for k in all_keys])
        m = (p + q) / 2
        # Avoid log(0)
        p = np.maximum(p, 1e-10)
        q = np.maximum(q, 1e-10)
        m = np.maximum(m, 1e-10)
        kl_pm = np.sum(p * np.log2(p / m))
        kl_qm = np.sum(q * np.log2(q / m))
        return (kl_pm + kl_qm) / 2

    # Compute JSD for consecutive line pairs, stratified by mode transition
    jsds_by_type = {'BB': [], 'AB': [], 'BA': [], 'AA': [], 'all': []}

    for para in paragraphs:
        lines = para['lines']
        for i in range(len(lines) - 1):
            curr = lines[i]
            nxt = lines[i + 1]
            if not curr['mode'] or not nxt['mode']:
                continue

            dist_curr = prefix_distribution(curr['toks'])
            dist_nxt = prefix_distribution(nxt['toks'])
            jsd = jensen_shannon(dist_curr, dist_nxt)

            mode_pair = curr['mode'] + nxt['mode']
            jsds_by_type[mode_pair].append(jsd)
            jsds_by_type['all'].append(jsd)

    results_by_type = {}
    for mp in ['BB', 'AB', 'BA', 'AA', 'all']:
        vals = jsds_by_type[mp]
        results_by_type[mp] = {
            'mean_jsd': round(float(np.mean(vals)), 4) if vals else 0.0,
            'n': len(vals),
        }

    for mp in ['BB', 'AA', 'AB', 'BA', 'all']:
        r = results_by_type[mp]
        print(f"  {mp}: mean PREFIX JSD = {r['mean_jsd']:.4f} (n={r['n']})")

    within_jsds = jsds_by_type['BB'] + jsds_by_type['AA']
    cross_jsds = jsds_by_type['AB'] + jsds_by_type['BA']

    within_mean = np.mean(within_jsds) if within_jsds else 0.0
    cross_mean = np.mean(cross_jsds) if cross_jsds else 0.0
    diff = cross_mean - within_mean

    print(f"\n  Within-mode mean: {within_mean:.4f}")
    print(f"  Cross-mode mean:  {cross_mean:.4f}")
    print(f"  Diff (cross - within): {diff:+.4f}")
    print(f"  C1228 aggregate interior JSD: 0.470")

    # Permutation
    all_jsds = within_jsds + cross_jsds
    n_within = len(within_jsds)
    perm_diffs = []
    for _ in range(N_PERM):
        perm_idx = RNG.permutation(len(all_jsds))
        pw = np.mean([all_jsds[i] for i in perm_idx[:n_within]])
        pc = np.mean([all_jsds[i] for i in perm_idx[n_within:]])
        perm_diffs.append(pc - pw)

    p_value = np.mean([pd >= diff for pd in perm_diffs])
    print(f"  Permutation p = {p_value:.4f}")

    if diff > 0.03 and p_value < BONFERRONI_ALPHA:
        classification = 'ARTIFACT'  # PREFIX switching IS mode alternation
    elif diff < 0.01:
        classification = 'GENUINE'  # PREFIX switches within-mode too
    else:
        classification = 'MIXTURE'

    print(f"  Classification: {classification}")

    return {
        'test': 'T6_prefix_switch',
        'by_mode_pair': results_by_type,
        'within_mode_mean_jsd': round(float(within_mean), 4),
        'cross_mode_mean_jsd': round(float(cross_mean), 4),
        'diff': round(float(diff), 4),
        'perm_p': round(float(p_value), 4),
        'classification': classification,
        'c1228_reference': {'aggregate_interior_jsd': 0.470},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── T7: SUFFIX/PREFIX TRAJECTORY (C676) ──────────────────────────

def t7_morphological_trajectory(folios):
    """T7: Does PREFIX/suffix trajectory survive within Mode B?"""
    print("\nT7: Suffix/PREFIX Trajectory Decomposition (retests C676)")
    print("-" * 60)

    # Use folio-level positions (matching C676's methodology)
    all_lines = []
    mode_b_lines = []
    mode_a_lines = []

    for folio, paragraphs in folios.items():
        # Collect all lines for this folio
        folio_lines = []
        for para in paragraphs:
            for ln, toks in para:
                folio_lines.append((ln, toks))
        folio_lines.sort(key=lambda x: x[0])

        n_lines = len(folio_lines)
        if n_lines < 8:
            continue

        for li, (ln, toks) in enumerate(folio_lines):
            norm_pos = li / (n_lines - 1) if n_lines > 1 else 0.0
            mode = classify_suffix_mode(toks)

            # Compute per-line PREFIX and suffix features
            n = len(toks)
            if n == 0:
                continue
            qo_frac = sum(1 for t in toks if t['prefix'] == 'qo') / n
            bare_frac = sum(1 for t in toks if not t['suffix']) / n
            e_fam_frac = sum(1 for t in toks if t['suffix'] in E_FAMILY_SUFFIXES) / n

            entry = {
                'norm_pos': norm_pos,
                'qo_frac': qo_frac,
                'bare_frac': bare_frac,
                'e_fam_frac': e_fam_frac,
                'mode': mode,
            }
            all_lines.append(entry)
            if mode == 'B':
                mode_b_lines.append(entry)
            elif mode == 'A':
                mode_a_lines.append(entry)

    def compute_trajectory(lines_list):
        if len(lines_list) < 20:
            return {'qo_rho': 0.0, 'bare_rho': 0.0, 'e_fam_rho': 0.0, 'n': 0}
        pos = [l['norm_pos'] for l in lines_list]
        qo = [l['qo_frac'] for l in lines_list]
        bare = [l['bare_frac'] for l in lines_list]
        e_fam = [l['e_fam_frac'] for l in lines_list]

        qo_rho, qo_p = spearmanr(pos, qo)
        bare_rho, bare_p = spearmanr(pos, bare)
        e_rho, e_p = spearmanr(pos, e_fam)

        return {
            'qo_rho': round(float(qo_rho), 4), 'qo_p': round(float(qo_p), 6),
            'bare_rho': round(float(bare_rho), 4), 'bare_p': round(float(bare_p), 6),
            'e_fam_rho': round(float(e_rho), 4), 'e_fam_p': round(float(e_p), 6),
            'n': len(lines_list),
        }

    agg = compute_trajectory(all_lines)
    mode_b = compute_trajectory(mode_b_lines)
    mode_a = compute_trajectory(mode_a_lines)

    print(f"  AGGREGATE:  qo={agg['qo_rho']}, bare={agg['bare_rho']}, e_fam={agg['e_fam_rho']}  (C676: qo=-0.085, bare=+0.095, e_fam=-0.087)")
    print(f"  MODE B:     qo={mode_b['qo_rho']}, bare={mode_b['bare_rho']}, e_fam={mode_b['e_fam_rho']}")
    print(f"  MODE A:     qo={mode_a['qo_rho']}, bare={mode_a['bare_rho']}, e_fam={mode_a['e_fam_rho']}")

    # Classification based on bare_rho (the primary signal in C676)
    agg_bare = abs(agg['bare_rho'])
    b_bare = abs(mode_b['bare_rho'])
    if agg_bare < 0.03:
        classification = 'NO_GRADIENT'
    elif b_bare >= agg_bare * 0.5:
        classification = 'GENUINE'
    elif b_bare < 0.03:
        classification = 'ARTIFACT'
    else:
        classification = 'MIXTURE'

    print(f"  Classification: {classification}")

    return {
        'test': 'T7_morphological_trajectory',
        'aggregate': agg,
        'mode_b': mode_b,
        'mode_a': mode_a,
        'classification': classification,
        'c676_reference': {'qo_rho': -0.085, 'bare_rho': 0.095, 'e_fam_rho': -0.087},
        'pass': classification in ('GENUINE', 'MIXTURE'),
        'verdict': classification,
    }


# ── MAIN ──────────────────────────────────────────────────────────

def main():
    print("Phase 451: GRADIENT_DECOMPOSITION")
    print("=" * 60)

    print("\nLoading data...")
    folios, all_tokens = load_data()
    print(f"  {len(all_tokens)} tokens across {len(folios)} folios")

    print("\nBuilding folio spread for rarity classification...")
    folio_spread = build_folio_spread()
    print(f"  {len(folio_spread)} unique MIDDLEs")

    # Build paragraphs for T1-T4 (8+ body lines, matching C932)
    paragraphs_8 = build_annotated_paragraphs(folios, min_body_lines=8)
    print(f"  {len(paragraphs_8)} paragraphs with 8+ body lines (C932 dataset)")

    # Count modes
    n_a = sum(1 for p in paragraphs_8 for l in p['lines'] if l['mode'] == 'A')
    n_b = sum(1 for p in paragraphs_8 for l in p['lines'] if l['mode'] == 'B')
    print(f"  Mode A: {n_a}, Mode B: {n_b} lines")

    r1 = t1_mode_proportion_gradient(paragraphs_8)
    r2 = t2_vocabulary_rarity(paragraphs_8, folio_spread)
    r3 = t3_prep_verb_position(paragraphs_8)
    r4 = t4_kernel_composition(paragraphs_8)
    r5 = t5_fl_reset(folios, min_body=6)
    r6 = t6_prefix_switch(folios, min_body=3)
    r7 = t7_morphological_trajectory(folios)

    # ── SUMMARY ──
    results = [r1, r2, r3, r4, r5, r6, r7]
    classifications = {}
    for r in results[1:]:  # skip T1 (it's the mechanism, not a retest)
        name = r['test']
        classifications[name] = r.get('classification', 'UNKNOWN')

    print("\n" + "=" * 60)
    print("SUMMARY: Gradient Decomposition Results")
    print("-" * 60)
    print(f"  T1 Mode proportion gradient: {r1['verdict']}")
    for r in results[1:]:
        ref = r.get('test', '?')
        cls = r.get('classification', '?')
        print(f"  {ref}: {cls}")

    n_genuine = sum(1 for c in classifications.values() if c == 'GENUINE')
    n_artifact = sum(1 for c in classifications.values() if c == 'ARTIFACT')
    n_mixture = sum(1 for c in classifications.values() if c == 'MIXTURE')

    print(f"\n  GENUINE: {n_genuine}/6")
    print(f"  MIXTURE: {n_mixture}/6")
    print(f"  ARTIFACT: {n_artifact}/6")

    if n_artifact >= 4:
        overall = "GRADIENTS_ARE_ARTIFACTS -- Mode proportion shift explains most aggregate gradients"
    elif n_genuine >= 4:
        overall = "GRADIENTS_ARE_GENUINE -- within-track gradients are real"
    else:
        overall = "MIXED -- some gradients genuine, some artifacts of mode proportion"
    print(f"\n  OVERALL: {overall}")

    # Save
    output = {
        'phase': 'Phase 451: GRADIENT_DECOMPOSITION',
        'overall_verdict': overall,
        'n_genuine': n_genuine,
        'n_artifact': n_artifact,
        'n_mixture': n_mixture,
        'classifications': classifications,
        'T1': r1, 'T2': r2, 'T3': r3, 'T4': r4, 'T5': r5, 'T6': r6, 'T7': r7,
        'data_summary': {
            'n_tokens': len(all_tokens),
            'n_folios': len(folios),
            'n_paragraphs_8plus': len(paragraphs_8),
        },
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    out_path = Path(__file__).resolve().parents[1] / 'results' / 'gradient_decomposition.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

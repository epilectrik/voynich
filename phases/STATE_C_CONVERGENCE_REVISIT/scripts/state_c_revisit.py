#!/usr/bin/env python3
"""
Phase 513: STATE-C CONVERGENCE REVISIT

Tests whether the Tier 0 finding "57.8% of folios converge to STATE-C" (C074)
describes genuine sequential convergence or an artifact of folio-level thematic
envelopes. Motivated by paragraph independence findings (C1398-C1400).

Tests:
  T1: Section confound test for C325 completion gradient
  T2: Paragraph-level AXM terminal analysis
  T3: Sequential convergence test within folios (paragraph position vs AXM)
  T4: Paragraph independence replication for AXM
  T5: Folio theme sufficiency (does folio mean predict everything?)
  T6: Within-paragraph sequential analysis
  T7: Reframing assessment (synthesis)

Output: phases/STATE_C_CONVERGENCE_REVISIT/results/state_c_revisit.json
"""

import sys
import os
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, pearsonr, mannwhitneyu

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

# ============================================================
# LOAD DATA
# ============================================================

def load_class_map():
    """Load the 49-class token map and 6-state macro-automaton partition."""
    path = PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # 6-state macro-automaton (C976/C1010)
    automaton_path = PROJECT_ROOT / 'phases/MINIMAL_STATE_AUTOMATON/results/t3_merged_automaton.json'
    with open(automaton_path) as f:
        auto = json.load(f)

    # Build class -> macro-state mapping
    class_to_state = {}
    state_names = {}
    for sd in auto['state_descriptions']:
        sid = sd['state_id']
        state_names[sid] = '_'.join(sd['roles'])
        for c in sd['classes']:
            class_to_state[c] = sid

    # State 4 = AXM (the massive attractor, 67.7% of tokens)
    AXM_STATE = 4

    return token_to_class, class_to_state, state_names, AXM_STATE


def load_regime_map():
    """Load REGIME assignments per folio."""
    path = PROJECT_ROOT / 'data/regime_folio_mapping.json'
    with open(path) as f:
        d = json.load(f)
    return {k: v['regime'] for k, v in d['regime_assignments'].items()}


def build_paragraphs(tokens):
    """Build paragraphs from par_initial markers, same method as Phase 510."""
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t.folio].append(t)

    for folio in folio_tokens:
        folio_tokens[folio].sort(key=lambda t: (t.line, 0))

    paragraphs = []
    for folio, toks in sorted(folio_tokens.items()):
        par_idx = 0
        current_par = []
        for t in toks:
            if t.par_initial and current_par:
                paragraphs.append({
                    'folio': folio,
                    'par_idx': par_idx,
                    'tokens': current_par,
                    'section': current_par[0].section,
                })
                par_idx += 1
                current_par = [t]
            else:
                current_par.append(t)
        if current_par:
            paragraphs.append({
                'folio': folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0].section,
            })

    # Compute line info
    for par in paragraphs:
        lines = sorted(set(t.line for t in par['tokens']))
        par['n_lines'] = len(lines)
        par['lines'] = lines
        par['body_lines'] = len(lines) - 1 if len(lines) > 1 else 0

    return paragraphs


def classify_tokens(tokens, token_to_class, class_to_state):
    """Classify a list of tokens into macro-states. Returns list of state IDs."""
    states = []
    for t in tokens:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is not None:
            state = class_to_state.get(cls)
            if state is not None:
                states.append(state)
    return states


def axm_rate(states, axm_state):
    """Compute fraction of tokens in AXM state."""
    if not states:
        return None
    return sum(1 for s in states if s == axm_state) / len(states)


def terminal_axm(tokens, token_to_class, class_to_state, axm_state, n_terminal=3):
    """
    Classify the last n_terminal classified tokens' macro-state.
    Returns the fraction that are AXM, or None if insufficient tokens.
    """
    states = classify_tokens(tokens, token_to_class, class_to_state)
    if len(states) < n_terminal:
        return None
    terminal = states[-n_terminal:]
    return sum(1 for s in terminal if s == axm_state) / len(terminal)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("Phase 513: STATE-C CONVERGENCE REVISIT")
    print("=" * 70)

    # Load data
    print("\n[LOAD] Loading data...")
    tx = Transcript()
    morph = Morphology()
    tokens = list(tx.currier_b())
    print(f"  Total Currier B tokens: {len(tokens)}")

    token_to_class, class_to_state, state_names, AXM_STATE = load_class_map()
    regime_map = load_regime_map()

    print(f"  Token-to-class map: {len(token_to_class)} entries")
    print(f"  6-state automaton: {len(state_names)} states")
    print(f"  AXM state ID: {AXM_STATE} ({state_names[AXM_STATE]})")

    # Get folio ordering from corpus
    folio_order = []
    folio_section = {}
    for t in tokens:
        if t.folio not in folio_order:
            folio_order.append(t.folio)
        folio_section[t.folio] = t.section
    folio_position = {f: i / (len(folio_order) - 1) for i, f in enumerate(folio_order)}
    print(f"  Folios in order: {len(folio_order)}")

    # Build paragraphs
    paragraphs = build_paragraphs(tokens)
    print(f"  Total paragraphs: {len(paragraphs)}")

    # Filter to paragraphs with 3+ body lines (substantial paragraphs)
    MIN_BODY = 3
    pars = [p for p in paragraphs if p['body_lines'] >= MIN_BODY]
    print(f"  Paragraphs with {MIN_BODY}+ body lines: {len(pars)}")

    # Pre-compute: folio-level token groupings
    folio_tokens = defaultdict(list)
    for t in tokens:
        folio_tokens[t.folio].append(t)

    # Pre-compute: per-folio AXM rate
    folio_axm = {}
    for folio, ftoks in folio_tokens.items():
        states = classify_tokens(ftoks, token_to_class, class_to_state)
        folio_axm[folio] = axm_rate(states, AXM_STATE)

    # Pre-compute: per-paragraph states and AXM rates
    for par in pars:
        states = classify_tokens(par['tokens'], token_to_class, class_to_state)
        par['states'] = states
        par['axm_rate'] = axm_rate(states, AXM_STATE)
        par['terminal_axm'] = terminal_axm(par['tokens'], token_to_class,
                                            class_to_state, AXM_STATE, n_terminal=3)
        # Per-line states
        line_states = defaultdict(list)
        for t in par['tokens']:
            w = t.word.strip()
            if not w or '*' in w:
                continue
            cls = token_to_class.get(w)
            if cls is not None:
                state = class_to_state.get(cls)
                if state is not None:
                    line_states[t.line].append(state)
        par['line_states'] = dict(line_states)

    results = {'phase': 'Phase 513: STATE-C CONVERGENCE REVISIT',
               'n_tokens': len(tokens),
               'n_folios': len(folio_order),
               'n_paragraphs': len(pars),
               'AXM_STATE': AXM_STATE}

    # ============================================================
    # T1: Section Confound Test for C325
    # ============================================================
    print("\n" + "=" * 70)
    print("T1: Section Confound Test for C325 (Completion Gradient)")
    print("=" * 70)

    # Folio position vs STATE-C rate (raw)
    positions = []
    axm_rates = []
    sections = []
    for folio in folio_order:
        if folio in folio_axm and folio_axm[folio] is not None:
            positions.append(folio_position[folio])
            axm_rates.append(folio_axm[folio])
            sections.append(folio_section[folio])

    rho_raw, p_raw = spearmanr(positions, axm_rates)
    print(f"  Raw: folio_position vs AXM_rate: rho={rho_raw:.4f}, p={p_raw:.4f}")

    # Section vs folio position
    section_codes = {'H': 0, 'S': 1, 'B': 2, 'C': 3, 'T': 4}
    sec_nums = [section_codes.get(s, -1) for s in sections]
    rho_sec_pos, p_sec_pos = spearmanr(positions, sec_nums)
    print(f"  Section vs folio_position: rho={rho_sec_pos:.4f}, p={p_sec_pos:.4f}")

    # Within-section correlations
    within_section = {}
    for sec in sorted(set(sections)):
        mask = [i for i, s in enumerate(sections) if s == sec]
        if len(mask) < 5:
            within_section[sec] = {'n': len(mask), 'rho': None, 'p': None,
                                   'verdict': 'INSUFFICIENT'}
            continue
        sec_pos = [positions[i] for i in mask]
        sec_axm = [axm_rates[i] for i in mask]
        rho_within, p_within = spearmanr(sec_pos, sec_axm)
        within_section[sec] = {
            'n': len(mask),
            'rho': float(rho_within),
            'p': float(p_within),
            'mean_axm': float(np.mean(sec_axm)),
            'verdict': 'SIGNIFICANT' if p_within < 0.05 else 'NOT_SIGNIFICANT'
        }
        print(f"  Within {sec} (n={len(mask)}): rho={rho_within:.4f}, p={p_within:.4f}"
              f" mean_AXM={np.mean(sec_axm):.3f}")

    # Section means
    section_means = {}
    for sec in sorted(set(sections)):
        mask = [i for i, s in enumerate(sections) if s == sec]
        sec_axm = [axm_rates[i] for i in mask]
        section_means[sec] = float(np.mean(sec_axm))
    print(f"  Section AXM means: {section_means}")

    # Verdict: does within-section correlation survive?
    surviving = sum(1 for v in within_section.values()
                    if v.get('verdict') == 'SIGNIFICANT')
    tested = sum(1 for v in within_section.values()
                 if v.get('verdict') != 'INSUFFICIENT')
    t1_confound = surviving == 0
    t1_verdict = ('SECTION_CONFOUND' if t1_confound
                  else f'PARTIAL_SURVIVAL ({surviving}/{tested})')
    print(f"\n  T1 VERDICT: {t1_verdict}")
    print(f"    Raw gradient rho={rho_raw:.4f} {'collapses' if t1_confound else 'partly survives'}"
          f" within sections")

    results['T1_section_confound'] = {
        'raw_rho': float(rho_raw),
        'raw_p': float(p_raw),
        'section_position_rho': float(rho_sec_pos),
        'section_position_p': float(p_sec_pos),
        'within_section': within_section,
        'section_means': section_means,
        'verdict': t1_verdict,
    }

    # ============================================================
    # T2: Paragraph-Level AXM Terminal Analysis
    # ============================================================
    print("\n" + "=" * 70)
    print("T2: Paragraph-Level AXM Terminal Analysis")
    print("=" * 70)

    # What fraction of paragraphs terminate in AXM?
    valid_pars = [p for p in pars if p['terminal_axm'] is not None]
    terminal_axm_rates = [p['terminal_axm'] for p in valid_pars]
    overall_axm_rates = [p['axm_rate'] for p in valid_pars if p['axm_rate'] is not None]

    mean_terminal_axm = float(np.mean(terminal_axm_rates))
    mean_overall_axm = float(np.mean(overall_axm_rates))

    # Histogram of terminal AXM rates
    term_bins = Counter()
    for r in terminal_axm_rates:
        if r >= 0.9:
            term_bins['>=0.9'] += 1
        elif r >= 0.5:
            term_bins['0.5-0.9'] += 1
        else:
            term_bins['<0.5'] += 1

    print(f"  Valid paragraphs: {len(valid_pars)}")
    print(f"  Mean terminal AXM rate (last 3 tokens): {mean_terminal_axm:.4f}")
    print(f"  Mean overall AXM rate: {mean_overall_axm:.4f}")
    print(f"  Terminal distribution: {dict(term_bins)}")

    # Is terminal AXM predicted by section?
    sec_terminal = defaultdict(list)
    for p in valid_pars:
        sec_terminal[p['section']].append(p['terminal_axm'])

    print("\n  Terminal AXM by section:")
    sec_terminal_stats = {}
    for sec in sorted(sec_terminal.keys()):
        vals = sec_terminal[sec]
        sec_terminal_stats[sec] = {
            'n': len(vals),
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals)),
        }
        print(f"    {sec}: n={len(vals)}, mean={np.mean(vals):.4f}, std={np.std(vals):.4f}")

    # Is terminal AXM predicted by folio?
    folio_terminal = defaultdict(list)
    for p in valid_pars:
        folio_terminal[p['folio']].append(p['terminal_axm'])
    folio_term_means = {f: np.mean(v) for f, v in folio_terminal.items() if len(v) >= 2}

    # ICC-like: between-folio vs within-folio variance
    all_term = terminal_axm_rates
    overall_var = float(np.var(all_term))
    within_vars = []
    for f, vals in folio_terminal.items():
        if len(vals) >= 2:
            within_vars.append(np.var(vals))
    mean_within_var = float(np.mean(within_vars)) if within_vars else 0.0
    between_var = overall_var - mean_within_var
    icc_approx = between_var / overall_var if overall_var > 0 else 0.0

    print(f"\n  ICC-like (folio predicting terminal AXM): {icc_approx:.4f}")
    print(f"    Overall variance: {overall_var:.6f}")
    print(f"    Mean within-folio variance: {mean_within_var:.6f}")
    print(f"    Between-folio variance: {between_var:.6f}")

    results['T2_paragraph_terminal'] = {
        'n_valid': len(valid_pars),
        'mean_terminal_axm': mean_terminal_axm,
        'mean_overall_axm': mean_overall_axm,
        'terminal_distribution': dict(term_bins),
        'section_terminal': sec_terminal_stats,
        'folio_icc_approx': float(icc_approx),
        'verdict': ('FOLIO_DOMINATED' if icc_approx > 0.3
                    else 'PARAGRAPH_VARIABLE' if icc_approx < 0.1
                    else 'MIXED')
    }

    # ============================================================
    # T3: Sequential Convergence Within Folios
    # ============================================================
    print("\n" + "=" * 70)
    print("T3: Sequential Convergence Within Folios")
    print("=" * 70)

    # For each folio, do later paragraphs have higher AXM terminal rates?
    folio_pars = defaultdict(list)
    for p in valid_pars:
        folio_pars[p['folio']].append(p)

    # Sort paragraphs within each folio by index
    for folio in folio_pars:
        folio_pars[folio].sort(key=lambda p: p['par_idx'])

    # Per-folio correlation: paragraph position vs terminal AXM
    folio_rhos = {}
    global_positions = []
    global_terminal_axm = []
    for folio, fps in folio_pars.items():
        if len(fps) < 3:
            continue
        positions_within = list(range(len(fps)))
        term_rates = [p['terminal_axm'] for p in fps]
        if np.std(term_rates) < 1e-10:
            folio_rhos[folio] = {'n': len(fps), 'rho': 0.0, 'verdict': 'CONSTANT'}
            continue
        rho, p_val = spearmanr(positions_within, term_rates)
        folio_rhos[folio] = {
            'n': len(fps),
            'rho': float(rho),
            'p': float(p_val),
            'verdict': 'INCREASING' if rho > 0.3 else 'DECREASING' if rho < -0.3 else 'FLAT'
        }
        # Collect for global test
        n = len(fps)
        for i, p in enumerate(fps):
            global_positions.append(i / (n - 1) if n > 1 else 0.5)
            global_terminal_axm.append(p['terminal_axm'])

    # Count verdicts
    verdict_counts = Counter(v['verdict'] for v in folio_rhos.values())
    print(f"  Folios with 3+ paragraphs: {len(folio_rhos)}")
    print(f"  Verdict distribution: {dict(verdict_counts)}")

    # Mean rho across folios
    valid_rhos = [v['rho'] for v in folio_rhos.values() if v['rho'] != 0.0 or v['verdict'] != 'CONSTANT']
    mean_rho = float(np.mean(valid_rhos)) if valid_rhos else 0.0
    print(f"  Mean within-folio rho: {mean_rho:.4f}")

    # Global pooled test
    if global_positions:
        rho_global, p_global = spearmanr(global_positions, global_terminal_axm)
        print(f"  Global (pooled) paragraph_position vs terminal_AXM: rho={rho_global:.4f}, p={p_global:.4f}")
    else:
        rho_global, p_global = 0.0, 1.0

    t3_verdict = ('SEQUENTIAL_CONVERGENCE' if rho_global > 0.1 and p_global < 0.05
                  else 'NO_SEQUENTIAL_CONVERGENCE')
    print(f"\n  T3 VERDICT: {t3_verdict}")

    results['T3_sequential_convergence'] = {
        'n_folios_tested': len(folio_rhos),
        'verdict_distribution': dict(verdict_counts),
        'mean_within_folio_rho': mean_rho,
        'global_rho': float(rho_global),
        'global_p': float(p_global),
        'verdict': t3_verdict,
    }

    # ============================================================
    # T4: Paragraph Independence Replication for AXM
    # ============================================================
    print("\n" + "=" * 70)
    print("T4: Paragraph Independence Replication for AXM")
    print("=" * 70)

    # Adjacent paragraph AXM terminal rate correlation
    # Only folios with 3+ paragraphs
    adjacent_pairs = []
    for folio, fps in folio_pars.items():
        if len(fps) < 3:
            continue
        for i in range(len(fps) - 1):
            adjacent_pairs.append((fps[i]['terminal_axm'], fps[i+1]['terminal_axm']))

    if len(adjacent_pairs) >= 10:
        x_adj = [p[0] for p in adjacent_pairs]
        y_adj = [p[1] for p in adjacent_pairs]
        rho_adj, p_adj = spearmanr(x_adj, y_adj)
        print(f"  Adjacent pairs: {len(adjacent_pairs)}")
        print(f"  Adjacent paragraph AXM correlation: rho={rho_adj:.4f}, p={p_adj:.4f}")

        # Shuffle control: 1000 permutations within folio
        N_PERM = 1000
        shuffle_rhos = []
        for _ in range(N_PERM):
            shuffled_pairs = []
            for folio, fps in folio_pars.items():
                if len(fps) < 3:
                    continue
                term_rates = [p['terminal_axm'] for p in fps]
                np.random.shuffle(term_rates)
                for i in range(len(term_rates) - 1):
                    shuffled_pairs.append((term_rates[i], term_rates[i+1]))
            if len(shuffled_pairs) >= 10:
                sx = [p[0] for p in shuffled_pairs]
                sy = [p[1] for p in shuffled_pairs]
                sr, _ = spearmanr(sx, sy)
                shuffle_rhos.append(sr)

        if shuffle_rhos:
            mean_shuffle = float(np.mean(shuffle_rhos))
            # Two-sided permutation test: how often does |shuffle_rho| >= |observed_rho|?
            p_perm_twosided = float(sum(1 for sr in shuffle_rhos
                                        if abs(sr) >= abs(rho_adj)) / N_PERM)
            # One-sided: how often does shuffle_rho >= observed_rho?
            p_perm_onesided = float(sum(1 for sr in shuffle_rhos
                                        if sr >= rho_adj) / N_PERM)
            print(f"  Shuffle control: mean_rho={mean_shuffle:.4f}, "
                  f"std={np.std(shuffle_rhos):.4f}")
            print(f"  Permutation p-value (two-sided): {p_perm_twosided:.4f}")
            print(f"  Permutation p-value (one-sided): {p_perm_onesided:.4f}")
            p_perm = p_perm_twosided  # Use two-sided for verdict
        else:
            mean_shuffle = 0.0
            p_perm = 1.0
    else:
        rho_adj, p_adj = 0.0, 1.0
        mean_shuffle = 0.0
        p_perm = 1.0
        t4_note = 'Insufficient data'
        print("  INSUFFICIENT adjacent pairs")

    # Verdict based on BOTH effect size and significance
    # rho < 0.1 is negligible regardless of p-value
    if abs(rho_adj) < 0.1:
        t4_verdict = 'INDEPENDENT_NEGLIGIBLE_EFFECT'
        t4_note = (f'rho={rho_adj:.4f} is negligible; '
                   f'permutation p={p_perm:.4f} may reflect distributional artifacts')
    elif p_perm > 0.05:
        t4_verdict = 'INDEPENDENT'
        t4_note = 'Not significant'
    else:
        t4_verdict = 'SEQUENTIAL_COUPLING'
        t4_note = f'rho={rho_adj:.4f}, p={p_perm:.4f}'
    print(f"\n  T4 VERDICT: {t4_verdict}")
    print(f"    Note: {t4_note}")

    results['T4_independence'] = {
        'n_adjacent_pairs': len(adjacent_pairs),
        'adjacent_rho': float(rho_adj),
        'adjacent_p': float(p_adj),
        'shuffle_mean_rho': mean_shuffle,
        'permutation_p': p_perm,
        'verdict': t4_verdict,
        'note': t4_note,
    }

    # ============================================================
    # T5: Folio Theme Sufficiency
    # ============================================================
    print("\n" + "=" * 70)
    print("T5: Folio Theme Sufficiency")
    print("=" * 70)

    # Predict each paragraph's terminal AXM from folio's mean AXM (leave-one-out)
    folio_baseline_errors = []
    position_model_errors = []

    for folio, fps in folio_pars.items():
        if len(fps) < 3:
            continue

        term_rates = [p['terminal_axm'] for p in fps]
        n = len(term_rates)

        for i in range(n):
            # Leave-one-out folio mean
            loo_mean = np.mean([term_rates[j] for j in range(n) if j != i])
            folio_baseline_errors.append((term_rates[i] - loo_mean) ** 2)

            # Position-aware: linear interpolation of other paragraphs
            positions_other = [(j / (n - 1) if n > 1 else 0.5)
                               for j in range(n) if j != i]
            rates_other = [term_rates[j] for j in range(n) if j != i]
            pos_i = i / (n - 1) if n > 1 else 0.5
            if len(positions_other) >= 2:
                # Simple linear regression
                x = np.array(positions_other)
                y = np.array(rates_other)
                if np.std(x) > 1e-10:
                    slope, intercept = np.polyfit(x, y, 1)
                    pred = slope * pos_i + intercept
                else:
                    pred = np.mean(rates_other)
            else:
                pred = np.mean(rates_other)
            position_model_errors.append((term_rates[i] - pred) ** 2)

    if folio_baseline_errors:
        mse_folio = float(np.mean(folio_baseline_errors))
        mse_position = float(np.mean(position_model_errors))
        improvement = 1.0 - mse_position / mse_folio if mse_folio > 0 else 0.0
        print(f"  MSE (folio-mean baseline): {mse_folio:.6f}")
        print(f"  MSE (position-aware model): {mse_position:.6f}")
        print(f"  Position improvement: {improvement:.4f} ({improvement*100:.1f}%)")
    else:
        mse_folio, mse_position, improvement = 0.0, 0.0, 0.0

    t5_verdict = ('FOLIO_SUFFICIENT' if improvement < 0.02
                  else 'POSITION_ADDS_SIGNAL')
    print(f"\n  T5 VERDICT: {t5_verdict}")

    results['T5_folio_sufficiency'] = {
        'mse_folio_baseline': mse_folio,
        'mse_position_model': mse_position,
        'position_improvement': improvement,
        'verdict': t5_verdict,
    }

    # ============================================================
    # T6: Within-Paragraph Sequential Analysis
    # ============================================================
    print("\n" + "=" * 70)
    print("T6: Within-Paragraph Sequential Analysis")
    print("=" * 70)

    # Within each paragraph, do later lines have higher AXM rates?
    within_par_rhos = []
    within_par_data = []

    for par in pars:
        if not par['line_states']:
            continue
        lines_sorted = sorted(par['line_states'].keys())
        if len(lines_sorted) < 4:
            continue

        # AXM rate per line
        line_axm = []
        for ln in lines_sorted:
            states = par['line_states'][ln]
            if states:
                line_axm.append(sum(1 for s in states if s == AXM_STATE) / len(states))

        if len(line_axm) < 4:
            continue

        # Compute correlation of line position vs AXM rate
        line_pos = list(range(len(line_axm)))
        if np.std(line_axm) < 1e-10:
            within_par_rhos.append(0.0)
            continue
        rho_within, _ = spearmanr(line_pos, line_axm)
        within_par_rhos.append(float(rho_within))

        within_par_data.append({
            'folio': par['folio'],
            'par_idx': par['par_idx'],
            'n_lines': len(line_axm),
            'rho': float(rho_within),
            'first_half_axm': float(np.mean(line_axm[:len(line_axm)//2])),
            'second_half_axm': float(np.mean(line_axm[len(line_axm)//2:])),
        })

    if within_par_rhos:
        mean_rho_within = float(np.mean(within_par_rhos))
        median_rho_within = float(np.median(within_par_rhos))
        pct_positive = float(sum(1 for r in within_par_rhos if r > 0) / len(within_par_rhos))
        pct_negative = float(sum(1 for r in within_par_rhos if r < 0) / len(within_par_rhos))

        # One-sample test: is mean rho significantly > 0?
        from scipy.stats import wilcoxon
        try:
            w_stat, w_p = wilcoxon(within_par_rhos)
        except Exception:
            w_stat, w_p = 0.0, 1.0

        print(f"  Paragraphs analyzed: {len(within_par_rhos)}")
        print(f"  Mean within-paragraph rho (line_pos vs AXM): {mean_rho_within:.4f}")
        print(f"  Median: {median_rho_within:.4f}")
        print(f"  Fraction positive: {pct_positive:.3f}")
        print(f"  Fraction negative: {pct_negative:.3f}")
        print(f"  Wilcoxon test: stat={w_stat:.1f}, p={w_p:.4f}")

        # First vs second half comparison
        first_halves = [d['first_half_axm'] for d in within_par_data]
        second_halves = [d['second_half_axm'] for d in within_par_data]
        mean_first = float(np.mean(first_halves))
        mean_second = float(np.mean(second_halves))
        u_stat, u_p = mannwhitneyu(first_halves, second_halves, alternative='less')
        print(f"\n  First half mean AXM: {mean_first:.4f}")
        print(f"  Second half mean AXM: {mean_second:.4f}")
        print(f"  Mann-Whitney (first < second): U={u_stat:.0f}, p={u_p:.4f}")

        # By section
        sec_within = defaultdict(list)
        for d in within_par_data:
            sec = [p['section'] for p in pars
                   if p['folio'] == d['folio'] and p['par_idx'] == d['par_idx']]
            if sec:
                sec_within[sec[0]].append(d['rho'])

        print("\n  Within-paragraph rho by section:")
        sec_within_stats = {}
        for sec in sorted(sec_within.keys()):
            vals = sec_within[sec]
            sec_within_stats[sec] = {
                'n': len(vals),
                'mean_rho': float(np.mean(vals)),
                'pct_positive': float(sum(1 for r in vals if r > 0) / len(vals)),
            }
            print(f"    {sec}: n={len(vals)}, mean_rho={np.mean(vals):.4f}, "
                  f"pct_positive={sum(1 for r in vals if r > 0) / len(vals):.3f}")
    else:
        mean_rho_within = 0.0
        median_rho_within = 0.0
        pct_positive = 0.0
        pct_negative = 0.0
        w_p = 1.0
        mean_first = 0.0
        mean_second = 0.0
        u_p = 1.0
        sec_within_stats = {}

    t6_verdict = ('WITHIN_PARAGRAPH_CONVERGENCE' if mean_rho_within > 0.05 and w_p < 0.05
                  else 'NO_WITHIN_PARAGRAPH_CONVERGENCE')
    print(f"\n  T6 VERDICT: {t6_verdict}")

    results['T6_within_paragraph'] = {
        'n_paragraphs': len(within_par_rhos),
        'mean_rho': mean_rho_within,
        'median_rho': median_rho_within,
        'pct_positive': pct_positive,
        'pct_negative': pct_negative,
        'wilcoxon_p': float(w_p),
        'first_half_mean_axm': mean_first,
        'second_half_mean_axm': mean_second,
        'mannwhitney_p': float(u_p),
        'section_within_stats': sec_within_stats,
        'verdict': t6_verdict,
    }

    # ============================================================
    # T7: Reframing Assessment (Synthesis)
    # ============================================================
    print("\n" + "=" * 70)
    print("T7: Synthesis and Reframing Assessment")
    print("=" * 70)

    # Collect all verdicts
    verdicts = {
        'T1': results['T1_section_confound']['verdict'],
        'T2': results['T2_paragraph_terminal']['verdict'],
        'T3': results['T3_sequential_convergence']['verdict'],
        'T4': results['T4_independence']['verdict'],
        'T5': results['T5_folio_sufficiency']['verdict'],
        'T6': results['T6_within_paragraph']['verdict'],
    }

    print("\n  Summary of Verdicts:")
    for t, v in verdicts.items():
        print(f"    {t}: {v}")

    # Q1: Is C074's convergence better described as thematic envelope?
    t4_independent = verdicts['T4'] in ('INDEPENDENT', 'INDEPENDENT_NEGLIGIBLE_EFFECT')
    q1_thematic = (verdicts['T3'] == 'NO_SEQUENTIAL_CONVERGENCE' and t4_independent)
    q1_answer = ('YES - AXM dominance is a folio-level thematic property, '
                 'not sequential convergence' if q1_thematic
                 else 'PARTIALLY - some sequential signal detected')

    # Q2: Is C325's gradient a section confound?
    q2_confound = 'SECTION_CONFOUND' in verdicts['T1']
    q2_answer = ('YES - gradient collapses within sections'
                 if q2_confound
                 else f'PARTIAL - {verdicts["T1"]}')

    # Q3: Does sequential convergence exist at any scale?
    q3_within_par = verdicts['T6'] == 'WITHIN_PARAGRAPH_CONVERGENCE'
    q3_answer = ('WITHIN_PARAGRAPH_ONLY' if q3_within_par
                 else 'NO_AT_ANY_SCALE')

    # Q4: Should MONOSTATE be reframed?
    q4_reframe = q1_thematic and verdicts['T5'] == 'FOLIO_SUFFICIENT'
    q4_answer = ('REFRAME: MONOSTATE describes folio-level AXM thematic dominance, '
                 'not sequential convergence to a terminal state'
                 if q4_reframe
                 else 'PARTIAL REFRAME: MONOSTATE is mostly thematic but some '
                 'sequential signal exists')

    print(f"\n  Q1 (C074 as thematic envelope?): {q1_answer}")
    print(f"  Q2 (C325 section confound?): {q2_answer}")
    print(f"  Q3 (Sequential convergence at any scale?): {q3_answer}")
    print(f"  Q4 (Reframe MONOSTATE?): {q4_answer}")

    # Compose overall reframing narrative
    if q1_thematic and q2_confound:
        overall = ('FULL_REFRAME: C074/C084 convergence to STATE-C is better understood '
                   'as AXM dominance within each folio program. The folio-position '
                   'gradient (C325) is a section confound. Paragraphs within folios '
                   'are independently composed at this level. Sequential convergence '
                   + ('exists within paragraphs only.' if q3_within_par
                      else 'is not detected at any scale.'))
    elif q1_thematic:
        overall = ('PARTIAL_REFRAME: C074 convergence is primarily thematic (folio-level), '
                   f'not sequential. C325 gradient: {verdicts["T1"]}. '
                   + ('Within-paragraph convergence detected.' if q3_within_par
                      else 'No sequential convergence at any scale.'))
    else:
        overall = f'MINIMAL_REFRAME: Sequential signal detected. Details: {verdicts}'

    print(f"\n  OVERALL: {overall}")

    results['T7_synthesis'] = {
        'verdicts': verdicts,
        'Q1_thematic_envelope': q1_answer,
        'Q2_section_confound': q2_answer,
        'Q3_sequential_any_scale': q3_answer,
        'Q4_reframe_monostate': q4_answer,
        'overall_assessment': overall,
    }

    # ============================================================
    # Additional diagnostic: AXM rate by normalized paragraph position
    # ============================================================
    print("\n" + "=" * 70)
    print("Diagnostic: AXM by Paragraph Position Quintile")
    print("=" * 70)

    # Bin paragraphs by their normalized position within the folio
    quintile_rates = defaultdict(list)
    for folio, fps in folio_pars.items():
        if len(fps) < 3:
            continue
        n = len(fps)
        for i, p in enumerate(fps):
            q = min(4, int(5 * i / n))  # 0-4 quintile
            quintile_rates[q].append(p['terminal_axm'])

    print("  Quintile | n    | Mean Terminal AXM | Std")
    print("  " + "-" * 50)
    quintile_stats = {}
    for q in range(5):
        vals = quintile_rates[q]
        if vals:
            quintile_stats[f'Q{q}'] = {
                'n': len(vals),
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals)),
            }
            print(f"  Q{q}       | {len(vals):4d} | {np.mean(vals):.4f}            | {np.std(vals):.4f}")

    results['diagnostic_quintiles'] = quintile_stats

    # ============================================================
    # Save results
    # ============================================================
    output_path = RESULTS_DIR / 'state_c_revisit.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[SAVED] Results to {output_path}")
    print("Done.")


if __name__ == '__main__':
    main()

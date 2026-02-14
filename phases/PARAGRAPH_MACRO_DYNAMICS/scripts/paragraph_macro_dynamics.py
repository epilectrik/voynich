#!/usr/bin/env python3
"""
Phase 345: PARAGRAPH_MACRO_DYNAMICS
====================================
Tests whether paragraphs have characteristic macro-state signatures and
whether the spec→exec gradient (C932-C935) maps to macro-state dynamics.

Paragraph profiling (C840-C869) and the spec→exec gradient were established
BEFORE the 6-state macro-automaton (C1010, C1015). This phase connects them.

Tests:
  T1: Header vs body macro-state distribution
  T2: Specification vs execution zone macro-state shift
  T3: Paragraph-level AXM self-transition by ordinal
  T4: Gallows-initial CC enrichment
  T5: Paragraph-level macro-state entropy by ordinal
  T6: qo/chsh gradient ↔ macro-state correspondence

Depends on: C1010 (6-state partition), C1015 (transition matrix),
            C840-C869 (paragraph structure), C863 (ordinal EN gradient),
            C932-C935 (spec→exec gradient)
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, mannwhitneyu, spearmanr, fisher_exact

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}

CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']

# Gallows characters (EVA)
GALLOWS = {'p', 't', 'k', 'f'}


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load tokens, map to macro-states, build paragraph structure."""
    print("Loading data...")

    # Load token→class mapping
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    print(f"  {len(token_to_class)} tokens mapped to 49 classes")

    # Load paragraph inventory for ordinals
    with open(PROJECT / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'b_paragraph_inventory.json',
              encoding='utf-8') as f:
        par_inventory = json.load(f)
    print(f"  {par_inventory['paragraph_count']} paragraphs in inventory")

    # Build folio→ordinal→par_info lookup
    par_lookup = {}
    for par in par_inventory['paragraphs']:
        key = (par['folio'], par['paragraph_ordinal'])
        par_lookup[key] = par

    morph = Morphology()

    # Iterate B tokens, build paragraph-grouped data
    paragraphs = []
    current_par = None
    current_folio = None
    par_ordinal = 0

    for token in Transcript().currier_b():
        # Skip labels and uncertain
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        # Look up class and state
        cls = token_to_class.get(token.word)
        if cls is None:
            continue
        state = CLASS_TO_STATE.get(cls)
        if state is None:
            continue

        # Extract morphology
        m = morph.extract(token.word)
        prefix = m.prefix if m else None

        # Paragraph boundary detection
        if token.par_initial or token.folio != current_folio:
            if current_par is not None and current_par['tokens']:
                paragraphs.append(current_par)
            if token.folio != current_folio:
                current_folio = token.folio
                par_ordinal = 1
            else:
                par_ordinal += 1

            # Check if first token is gallows
            first_char = token.word[0] if token.word else ''
            is_gallows = first_char in GALLOWS

            current_par = {
                'folio': token.folio,
                'ordinal': par_ordinal,
                'tokens': [],
                'lines': defaultdict(list),
                'is_gallows_initial': is_gallows,
                'first_token_word': token.word,
            }

        if current_par is None:
            # Edge case: first token before any paragraph start
            current_folio = token.folio
            par_ordinal = 1
            first_char = token.word[0] if token.word else ''
            current_par = {
                'folio': token.folio,
                'ordinal': par_ordinal,
                'tokens': [],
                'lines': defaultdict(list),
                'is_gallows_initial': first_char in GALLOWS,
                'first_token_word': token.word,
            }

        current_par['tokens'].append({
            'word': token.word,
            'state': state,
            'cls': cls,
            'prefix': prefix,
            'line': token.line,
        })
        current_par['lines'][token.line].append({
            'word': token.word,
            'state': state,
            'prefix': prefix,
        })

    # Don't forget last paragraph
    if current_par is not None and current_par['tokens']:
        paragraphs.append(current_par)

    # Convert defaultdicts
    for par in paragraphs:
        par['lines'] = dict(par['lines'])
        par['line_count'] = len(par['lines'])
        par['token_count'] = len(par['tokens'])

    # Compute max ordinal per folio for position info
    folio_max_ord = defaultdict(int)
    for par in paragraphs:
        folio_max_ord[par['folio']] = max(folio_max_ord[par['folio']], par['ordinal'])
    for par in paragraphs:
        par['is_first'] = par['ordinal'] == 1
        par['is_last'] = par['ordinal'] == folio_max_ord[par['folio']]

    total_tokens = sum(p['token_count'] for p in paragraphs)
    print(f"  {len(paragraphs)} paragraphs built, {total_tokens} classified tokens")
    print(f"  {sum(1 for p in paragraphs if p['is_gallows_initial'])} gallows-initial paragraphs")

    return paragraphs


# ── Utility ──────────────────────────────────────────────────────────

def state_distribution(tokens):
    """Compute normalized macro-state distribution from token list."""
    counts = Counter(t['state'] for t in tokens)
    total = sum(counts.values())
    if total == 0:
        return {s: 0.0 for s in STATE_ORDER}
    return {s: counts.get(s, 0) / total for s in STATE_ORDER}


def state_counts(tokens):
    """Raw macro-state counts."""
    counts = Counter(t['state'] for t in tokens)
    return {s: counts.get(s, 0) for s in STATE_ORDER}


def chi2_test(dist_a_counts, dist_b_counts):
    """Chi-squared test on two count distributions."""
    table = np.array([[dist_a_counts.get(s, 0) for s in STATE_ORDER],
                      [dist_b_counts.get(s, 0) for s in STATE_ORDER]])
    # Remove columns that are all zero
    nonzero = table.sum(axis=0) > 0
    table = table[:, nonzero]
    if table.shape[1] < 2:
        return 0.0, 1.0, 0
    chi2, p, dof, _ = chi2_contingency(table)
    return chi2, p, dof


def shannon_entropy(tokens):
    """Shannon entropy over macro-state distribution."""
    counts = Counter(t['state'] for t in tokens)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * np.log2(p) for p in probs)


# ── T1: Header vs Body Macro-State Distribution ─────────────────────

def run_t1(paragraphs):
    """Test whether header lines (line 1) differ from body lines in macro-state."""
    print("\n" + "=" * 60)
    print("T1: Header vs Body Macro-State Distribution")
    print("=" * 60)

    header_tokens = []
    body_tokens = []

    for par in paragraphs:
        if par['line_count'] < 2:
            continue  # Need at least 2 lines for header/body split
        lines_sorted = sorted(par['lines'].keys(), key=lambda x: (len(str(x)), str(x)))
        header_line = lines_sorted[0]
        for line_id, toks in par['lines'].items():
            if line_id == header_line:
                header_tokens.extend(toks)
            else:
                body_tokens.extend(toks)

    print(f"  Header tokens: {len(header_tokens)}")
    print(f"  Body tokens: {len(body_tokens)}")

    header_dist = state_distribution(header_tokens)
    body_dist = state_distribution(body_tokens)
    header_cts = state_counts(header_tokens)
    body_cts = state_counts(body_tokens)

    print(f"\n  State distributions:")
    print(f"  {'State':<10} {'Header':>8} {'Body':>8} {'Delta':>8}")
    print(f"  {'-'*36}")
    for s in STATE_ORDER:
        delta = header_dist[s] - body_dist[s]
        print(f"  {s:<10} {header_dist[s]:>7.3f}  {body_dist[s]:>7.3f}  {delta:>+7.3f}")

    chi2, p, dof = chi2_test(header_cts, body_cts)
    print(f"\n  Chi-squared: {chi2:.2f}, dof={dof}, p={p:.6f}")

    # Check prediction: header CC or AXm elevated by ≥3pp
    cc_delta = header_dist['CC'] - body_dist['CC']
    axm_minor_delta = header_dist['AXm'] - body_dist['AXm']
    best_delta = max(cc_delta, axm_minor_delta)
    best_state = 'CC' if cc_delta >= axm_minor_delta else 'AXm'

    passed = p < 0.01 and best_delta >= 0.03
    verdict = "PASS" if passed else "FAIL"
    print(f"\n  Prediction: Header {best_state} elevated by {best_delta:+.3f} ({best_delta*100:+.1f}pp)")
    print(f"  Verdict: {verdict}")

    # Also note what IS elevated
    max_delta_state = max(STATE_ORDER, key=lambda s: header_dist[s] - body_dist[s])
    max_delta = header_dist[max_delta_state] - body_dist[max_delta_state]
    print(f"  Largest header elevation: {max_delta_state} ({max_delta:+.3f})")

    return {
        'header_tokens': len(header_tokens),
        'body_tokens': len(body_tokens),
        'header_dist': header_dist,
        'body_dist': body_dist,
        'chi2': float(chi2),
        'p': float(p),
        'dof': dof,
        'cc_delta': float(cc_delta),
        'axm_minor_delta': float(axm_minor_delta),
        'max_elevated_state': max_delta_state,
        'max_elevation': float(max_delta),
        'verdict': verdict,
    }


# ── T2: Specification vs Execution Zone ──────────────────────────────

def run_t2(paragraphs):
    """Test macro-state shift between spec zone (early body) and exec zone (late body)."""
    print("\n" + "=" * 60)
    print("T2: Specification vs Execution Zone Macro-State Shift")
    print("=" * 60)

    spec_tokens = []
    exec_tokens = []

    for par in paragraphs:
        if par['line_count'] < 4:
            continue  # Need ≥4 lines for meaningful zone split

        lines_sorted = sorted(par['lines'].keys(), key=lambda x: (len(str(x)), str(x)))
        n = len(lines_sorted)

        for i, line_id in enumerate(lines_sorted):
            if i == 0:
                continue  # Skip header (line 1)
            pos = i / max(n - 1, 1)
            toks = par['lines'][line_id]
            if pos < 0.4:
                spec_tokens.extend(toks)
            else:
                exec_tokens.extend(toks)

    print(f"  Spec tokens: {len(spec_tokens)}")
    print(f"  Exec tokens: {len(exec_tokens)}")

    spec_dist = state_distribution(spec_tokens)
    exec_dist = state_distribution(exec_tokens)
    spec_cts = state_counts(spec_tokens)
    exec_cts = state_counts(exec_tokens)

    print(f"\n  State distributions:")
    print(f"  {'State':<10} {'Spec':>8} {'Exec':>8} {'Delta':>8}")
    print(f"  {'-'*36}")
    for s in STATE_ORDER:
        delta = exec_dist[s] - spec_dist[s]
        print(f"  {s:<10} {spec_dist[s]:>7.3f}  {exec_dist[s]:>7.3f}  {delta:>+7.3f}")

    chi2, p, dof = chi2_test(spec_cts, exec_cts)
    print(f"\n  Chi-squared: {chi2:.2f}, dof={dof}, p={p:.6f}")

    # Check prediction: exec AXM > spec AXM by ≥3pp
    delta_axm = exec_dist['AXM'] - spec_dist['AXM']
    # Also check FQ: spec FQ > exec FQ
    delta_fq = spec_dist['FQ'] - exec_dist['FQ']

    passed = p < 0.01 and delta_axm >= 0.03
    verdict = "PASS" if passed else "FAIL"
    print(f"\n  Prediction: Exec AXM exceeds Spec by {delta_axm:+.3f} ({delta_axm*100:+.1f}pp)")
    print(f"  Spec FQ exceeds Exec by {delta_fq:+.3f} ({delta_fq*100:+.1f}pp)")
    print(f"  Verdict: {verdict}")

    return {
        'spec_tokens': len(spec_tokens),
        'exec_tokens': len(exec_tokens),
        'spec_dist': spec_dist,
        'exec_dist': exec_dist,
        'chi2': float(chi2),
        'p': float(p),
        'dof': dof,
        'delta_AXM': float(delta_axm),
        'delta_FQ_spec_minus_exec': float(delta_fq),
        'verdict': verdict,
    }


# ── T3: AXM Self-Transition by Paragraph Ordinal ────────────────────

def run_t3(paragraphs):
    """Test whether AXM self-transition rate differs by paragraph ordinal."""
    print("\n" + "=" * 60)
    print("T3: Paragraph-Level AXM Self-Transition by Ordinal")
    print("=" * 60)

    par_data = []
    for par in paragraphs:
        if par['token_count'] < 20:
            continue

        # Compute AXM self-transition
        tokens = par['tokens']
        axm_axm = 0
        axm_total = 0
        for i in range(len(tokens) - 1):
            if tokens[i]['state'] == 'AXM':
                axm_total += 1
                if tokens[i + 1]['state'] == 'AXM':
                    axm_axm += 1

        if axm_total < 5:
            continue

        axm_self = axm_axm / axm_total
        par_data.append({
            'ordinal': par['ordinal'],
            'axm_self': axm_self,
            'n_tokens': par['token_count'],
            'folio': par['folio'],
        })

    print(f"  Paragraphs with ≥20 tokens and ≥5 AXM: {len(par_data)}")

    # Split into early (ordinal 1-2) vs late (ordinal 5+)
    early = [p for p in par_data if p['ordinal'] <= 2]
    late = [p for p in par_data if p['ordinal'] >= 5]

    early_vals = [p['axm_self'] for p in early]
    late_vals = [p['axm_self'] for p in late]

    print(f"  Early (ord 1-2): n={len(early)}, mean AXM self={np.mean(early_vals):.3f}")
    print(f"  Late (ord 5+): n={len(late)}, mean AXM self={np.mean(late_vals):.3f}")

    if len(early) >= 3 and len(late) >= 3:
        U, p = mannwhitneyu(early_vals, late_vals, alternative='two-sided')
        delta = np.mean(late_vals) - np.mean(early_vals)
        print(f"  Mann-Whitney U={U:.1f}, p={p:.6f}, delta={delta:+.3f}")
    else:
        U, p, delta = 0, 1.0, 0.0
        print(f"  Insufficient data for test")

    # Also: Spearman correlation across all ordinals
    all_ords = [p['ordinal'] for p in par_data]
    all_axm = [p['axm_self'] for p in par_data]
    rho, rho_p = spearmanr(all_ords, all_axm)
    print(f"  Spearman(ordinal, AXM_self): rho={rho:.3f}, p={rho_p:.6f}")

    passed = p < 0.05
    verdict = "PASS" if passed else "FAIL"
    print(f"  Verdict: {verdict}")

    return {
        'n_paragraphs': len(par_data),
        'n_early': len(early),
        'n_late': len(late),
        'early_mean': float(np.mean(early_vals)) if early_vals else None,
        'late_mean': float(np.mean(late_vals)) if late_vals else None,
        'U': float(U),
        'p': float(p),
        'delta': float(delta),
        'spearman_rho': float(rho),
        'spearman_p': float(rho_p),
        'verdict': verdict,
    }


# ── T4: Gallows-Initial CC Enrichment ────────────────────────────────

def run_t4(paragraphs):
    """Test whether gallows-initial paragraph first tokens show CC enrichment."""
    print("\n" + "=" * 60)
    print("T4: Gallows-Initial CC Enrichment")
    print("=" * 60)

    gallows_first = []
    non_gallows_first = []

    for par in paragraphs:
        if not par['tokens']:
            continue
        first_tok = par['tokens'][0]
        if par['is_gallows_initial']:
            gallows_first.append(first_tok)
        else:
            non_gallows_first.append(first_tok)

    print(f"  Gallows-initial paragraphs: {len(gallows_first)}")
    print(f"  Non-gallows paragraphs: {len(non_gallows_first)}")

    gallows_cc = sum(1 for t in gallows_first if t['state'] == 'CC')
    non_gallows_cc = sum(1 for t in non_gallows_first if t['state'] == 'CC')

    gallows_rate = gallows_cc / max(len(gallows_first), 1)
    non_gallows_rate = non_gallows_cc / max(len(non_gallows_first), 1)

    print(f"  Gallows CC rate: {gallows_cc}/{len(gallows_first)} = {gallows_rate:.3f}")
    print(f"  Non-gallows CC rate: {non_gallows_cc}/{len(non_gallows_first)} = {non_gallows_rate:.3f}")

    # Fisher exact test: gallows vs non-gallows × CC vs non-CC
    table = np.array([
        [gallows_cc, len(gallows_first) - gallows_cc],
        [non_gallows_cc, len(non_gallows_first) - non_gallows_cc]
    ])
    odds_ratio, p = fisher_exact(table)

    print(f"  Fisher exact: OR={odds_ratio:.3f}, p={p:.6f}")

    passed = p < 0.05 and odds_ratio > 1.5
    verdict = "PASS" if passed else "FAIL"
    print(f"  Verdict: {verdict}")

    # Also show full state distribution for first tokens
    gallows_dist = state_distribution(gallows_first)
    non_gallows_dist = state_distribution(non_gallows_first)
    print(f"\n  First-token state distributions:")
    print(f"  {'State':<10} {'Gallows':>8} {'NonGall':>8} {'Delta':>8}")
    print(f"  {'-'*36}")
    for s in STATE_ORDER:
        delta = gallows_dist[s] - non_gallows_dist[s]
        print(f"  {s:<10} {gallows_dist[s]:>7.3f}  {non_gallows_dist[s]:>7.3f}  {delta:>+7.3f}")

    return {
        'n_gallows': len(gallows_first),
        'n_non_gallows': len(non_gallows_first),
        'gallows_cc_rate': float(gallows_rate),
        'non_gallows_cc_rate': float(non_gallows_rate),
        'OR': float(odds_ratio),
        'p': float(p),
        'gallows_first_dist': gallows_dist,
        'non_gallows_first_dist': non_gallows_dist,
        'verdict': verdict,
    }


# ── T5: Macro-State Entropy by Ordinal ───────────────────────────────

def run_t5(paragraphs):
    """Test whether macro-state entropy varies with paragraph ordinal."""
    print("\n" + "=" * 60)
    print("T5: Paragraph-Level Macro-State Entropy by Ordinal")
    print("=" * 60)

    par_data = []
    for par in paragraphs:
        if par['token_count'] < 10:
            continue
        ent = shannon_entropy(par['tokens'])
        par_data.append({
            'ordinal': par['ordinal'],
            'entropy': ent,
            'n_tokens': par['token_count'],
            'folio': par['folio'],
        })

    print(f"  Paragraphs with ≥10 tokens: {len(par_data)}")

    ords = [p['ordinal'] for p in par_data]
    ents = [p['entropy'] for p in par_data]

    rho, p = spearmanr(ords, ents)
    print(f"  Spearman(ordinal, entropy): rho={rho:.3f}, p={p:.6f}")

    # Early vs late comparison
    early = [p['entropy'] for p in par_data if p['ordinal'] <= 2]
    late = [p['entropy'] for p in par_data if p['ordinal'] >= 5]
    print(f"  Early (ord 1-2) mean entropy: {np.mean(early):.3f} (n={len(early)})")
    print(f"  Late (ord 5+) mean entropy: {np.mean(late):.3f} (n={len(late)})")

    passed = abs(rho) > 0.15 and p < 0.05
    verdict = "PASS" if passed else "FAIL"
    print(f"  Verdict: {verdict}")

    return {
        'n_paragraphs': len(par_data),
        'rho': float(rho),
        'p': float(p),
        'early_mean': float(np.mean(early)) if early else None,
        'late_mean': float(np.mean(late)) if late else None,
        'n_early': len(early),
        'n_late': len(late),
        'overall_mean_entropy': float(np.mean(ents)),
        'verdict': verdict,
    }


# ── T6: qo/chsh Gradient ↔ Macro-State ──────────────────────────────

def run_t6(paragraphs):
    """Test whether qo and ch/sh prefixes map to different macro-states."""
    print("\n" + "=" * 60)
    print("T6: qo/chsh Gradient ↔ Macro-State Correspondence")
    print("=" * 60)

    qo_tokens = []
    chsh_tokens = []

    for par in paragraphs:
        for tok in par['tokens']:
            pfx = tok['prefix']
            if pfx == 'qo':
                qo_tokens.append(tok)
            elif pfx in ('ch', 'sh'):
                chsh_tokens.append(tok)

    print(f"  qo-prefixed tokens: {len(qo_tokens)}")
    print(f"  ch/sh-prefixed tokens: {len(chsh_tokens)}")

    qo_dist = state_distribution(qo_tokens)
    chsh_dist = state_distribution(chsh_tokens)
    qo_cts = state_counts(qo_tokens)
    chsh_cts = state_counts(chsh_tokens)

    print(f"\n  State distributions:")
    print(f"  {'State':<10} {'qo':>8} {'ch/sh':>8} {'Delta':>8}")
    print(f"  {'-'*36}")
    for s in STATE_ORDER:
        delta = qo_dist[s] - chsh_dist[s]
        print(f"  {s:<10} {qo_dist[s]:>7.3f}  {chsh_dist[s]:>7.3f}  {delta:>+7.3f}")

    chi2, p, dof = chi2_test(qo_cts, chsh_cts)
    print(f"\n  Chi-squared: {chi2:.2f}, dof={dof}, p={p:.6f}")

    # Check prediction: qo shows elevated FL; ch/sh shows elevated AXM
    qo_fl = qo_dist['FL_HAZ'] + qo_dist['FL_SAFE']
    chsh_fl = chsh_dist['FL_HAZ'] + chsh_dist['FL_SAFE']
    fl_delta = qo_fl - chsh_fl

    qo_axm = qo_dist['AXM']
    chsh_axm = chsh_dist['AXM']
    axm_delta = chsh_axm - qo_axm

    print(f"\n  qo FL share: {qo_fl:.3f}, ch/sh FL share: {chsh_fl:.3f} (delta: {fl_delta:+.3f})")
    print(f"  qo AXM share: {qo_axm:.3f}, ch/sh AXM share: {chsh_axm:.3f} (delta: {axm_delta:+.3f})")

    passed = p < 0.01
    verdict = "PASS" if passed else "FAIL"

    # Direction check
    direction = "PREDICTED" if fl_delta > 0 and axm_delta > 0 else "UNEXPECTED"
    print(f"  Direction: {direction}")
    print(f"  Verdict: {verdict}")

    return {
        'n_qo': len(qo_tokens),
        'n_chsh': len(chsh_tokens),
        'qo_dist': qo_dist,
        'chsh_dist': chsh_dist,
        'chi2': float(chi2),
        'p': float(p),
        'dof': dof,
        'qo_fl_share': float(qo_fl),
        'chsh_fl_share': float(chsh_fl),
        'fl_delta': float(fl_delta),
        'axm_delta_chsh_minus_qo': float(axm_delta),
        'direction': direction,
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 345: PARAGRAPH_MACRO_DYNAMICS")
    print("=" * 60)

    paragraphs = load_data()

    results = {
        'metadata': {
            'phase': 345,
            'name': 'PARAGRAPH_MACRO_DYNAMICS',
            'total_paragraphs': len(paragraphs),
            'total_tokens': sum(p['token_count'] for p in paragraphs),
            'gallows_initial_count': sum(1 for p in paragraphs if p['is_gallows_initial']),
        }
    }

    results['t1_header_vs_body'] = run_t1(paragraphs)
    results['t2_spec_vs_exec'] = run_t2(paragraphs)
    results['t3_axm_self_by_ordinal'] = run_t3(paragraphs)
    results['t4_gallows_cc'] = run_t4(paragraphs)
    results['t5_entropy_by_ordinal'] = run_t5(paragraphs)
    results['t6_qo_chsh_macro_state'] = run_t6(paragraphs)

    # Synthesis
    tests = ['t1_header_vs_body', 't2_spec_vs_exec', 't3_axm_self_by_ordinal',
             't4_gallows_cc', 't5_entropy_by_ordinal', 't6_qo_chsh_macro_state']
    pass_count = sum(1 for t in tests if results[t]['verdict'] == 'PASS')

    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)
    print(f"\n  Results: {pass_count}/{len(tests)} PASS")
    for t in tests:
        v = results[t]['verdict']
        print(f"    {t}: {v}")

    if pass_count >= 4:
        overall = "PARAGRAPH_MACRO_DYNAMICS_CONFIRMED"
    elif pass_count >= 2:
        overall = "PARAGRAPH_MACRO_DYNAMICS_PARTIAL"
    else:
        overall = "PARAGRAPH_MACRO_DYNAMICS_NEGATIVE"

    print(f"\n  Overall verdict: {overall}")

    results['synthesis'] = {
        'pass_count': pass_count,
        'total': len(tests),
        'verdict': overall,
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'paragraph_macro_dynamics.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {RESULTS_DIR / 'paragraph_macro_dynamics.json'}")


if __name__ == '__main__':
    main()

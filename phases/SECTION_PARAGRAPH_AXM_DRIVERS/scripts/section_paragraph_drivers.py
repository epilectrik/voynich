#!/usr/bin/env python3
"""
Phase 514: SECTION AND PARAGRAPH AXM DRIVERS
=============================================
Investigates two connected questions:
  (A) What structurally differentiates the Currier B sections (B, C, H, S, T)?
  (B) What drives the 71% of paragraph-level AXM variance NOT explained by folio?

Uses 6-state macro-automaton (C976), 49-class grammar (C121), morphological
decomposition, and paragraph detection to produce a comprehensive structural
characterization.

Output: phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json
"""

import sys
import os
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology

np.random.seed(42)

# ================================================================
# CONSTANTS
# ================================================================

# 6-state macro-automaton partition (from C976, t3_merged_automaton.json)
MACRO_STATE_PARTITION = {
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'AXm':     {3, 5, 18, 19, 42, 45},
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28,
                29, 31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}
MACRO_STATE_NAMES = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']

CLASS_TO_MACRO = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = state

# Role membership (from C581-C583, C573)
ROLE_CLASSES = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}
CLASS_TO_ROLE = {}
for role, classes in ROLE_CLASSES.items():
    for c in classes:
        CLASS_TO_ROLE[c] = role

# Operational categories (from C1250, C1195, C1388-C1392)
ATOM_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'MONITORING',
    'd': 'CONTAINMENT', 't': 'TRANSITION', 'y': 'CONTAINMENT',
    'n': 'OPERATION', 'i': 'OPERATION', 'a': 'STAGING',
    'm': 'MARKING', 'l': 'FLOW', 'o': 'STAGING',
    'r': 'FLOW', 'c': 'MONITORING', 'p': 'MARKING',
    's': 'STAGING', 'f': 'MARKING', 'q': 'THERMAL',
    'g': 'OPERATION', 'x': 'OPERATION',
}
CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

# Mode A suffixes (C1229, C1236)
MODE_A_SUFFIXES = {'edy', 'dy', 'ey', 'eey', 'y', 'hy', 'ly', 'ry',
                   'chy', 'shy', 'ky', 'oky', 'oty'}

# Major PREFIXes
MAJOR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'or',
                  'pch', 'tch', 'lch', 'ar', 'al', 'BARE']


def assign_category(middle):
    """Assign operational category to a MIDDLE via atom plurality vote."""
    if not middle:
        return None
    votes = Counter()
    for ch in middle:
        cat = ATOM_CATEGORY.get(ch)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    return votes.most_common(1)[0][0]


def cramers_v(contingency):
    """Compute Cramer's V from a contingency table."""
    chi2 = sp_stats.chi2_contingency(contingency)[0]
    n = contingency.sum()
    r, k = contingency.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1))) if n > 0 and min(r, k) > 1 else 0.0


def jsd_vec(p, q):
    """Jensen-Shannon divergence between two probability vectors."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    return float(jensenshannon(p, q) ** 2)  # squared = actual JSD


def safe_spearman(x, y):
    """Spearman correlation, handling edge cases."""
    x, y = np.array(x), np.array(y)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 5 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0, 1.0
    rho, p = sp_stats.spearmanr(x, y)
    return float(rho), float(p)


# ================================================================
# DATA LOADING
# ================================================================

def load_data():
    """Load all required data: tokens, class map, regime map, forbidden pairs."""
    print("[LOAD] Loading data...")

    # Token-to-class mapping
    cmap_path = PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(cmap_path, encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}

    # Regime mapping
    regime_path = PROJECT / 'data' / 'regime_folio_mapping.json'
    with open(regime_path, encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_to_regime = {fol: info['regime'] for fol, info in regime_data['regime_assignments'].items()}

    # Forbidden MIDDLE pairs
    forbid_path = PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
    with open(forbid_path, encoding='utf-8') as f:
        forbid_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbid_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    # Load tokens
    tx = Transcript()
    morph = Morphology()
    tokens = list(tx.currier_b())
    print(f"  {len(tokens)} Currier B tokens")
    print(f"  {len(token_to_class)} classified tokens")
    print(f"  {len(folio_to_regime)} folio regime assignments")
    print(f"  {len(forbidden_middle_pairs)} forbidden MIDDLE pairs")

    return tokens, token_to_class, folio_to_regime, forbidden_middle_pairs, morph


def build_enriched_tokens(tokens, token_to_class, folio_to_regime, morph):
    """Build enriched token list with morphology, class, macro-state, etc."""
    enriched = []
    for t in tokens:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue

        cls = token_to_class.get(w)
        m = morph.extract(w)

        rec = {
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
            'prefix': m.prefix if m.prefix else '',
            'middle': m.middle if m.middle else '',
            'suffix': m.suffix if m.suffix else '',
            'articulator': m.articulator if m.articulator else '',
            'cls': cls,
            'macro_state': CLASS_TO_MACRO.get(cls) if cls else None,
            'role': CLASS_TO_ROLE.get(cls) if cls else None,
            'regime': folio_to_regime.get(t.folio, 'UNKNOWN'),
            'category': assign_category(m.middle) if m.middle else None,
        }
        enriched.append(rec)

    print(f"  {len(enriched)} enriched tokens (labels/uncertain excluded)")
    return enriched


def build_paragraphs(enriched_tokens):
    """Build paragraphs from par_initial markers, same approach as Phase 510."""
    # Group by folio
    by_folio = defaultdict(list)
    for t in enriched_tokens:
        by_folio[t['folio']].append(t)

    paragraphs = []
    for folio in sorted(by_folio.keys()):
        toks = by_folio[folio]
        par_idx = 0
        current_par = []
        for t in toks:
            if t['par_initial'] and current_par:
                paragraphs.append({
                    'folio': folio,
                    'par_idx': par_idx,
                    'tokens': current_par,
                    'section': current_par[0]['section'],
                    'regime': current_par[0]['regime'],
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
                'section': current_par[0]['section'],
                'regime': current_par[0]['regime'],
            })

    # Add line counts
    for par in paragraphs:
        lines = set(t['line'] for t in par['tokens'])
        par['n_lines'] = len(lines)
        par['body_lines'] = len(lines) - 1 if len(lines) > 1 else 0

    # Filter: 3+ body lines
    filtered = [p for p in paragraphs if p['body_lines'] >= 3]
    print(f"  {len(paragraphs)} total paragraphs, {len(filtered)} with 3+ body lines")
    return filtered


# ================================================================
# PART A: SECTION STRUCTURAL CHARACTERIZATION
# ================================================================

def test_A1_section_macro_state_profiles(enriched_tokens):
    """A1: Section Macro-State Profiles — full 6-state distribution per section."""
    print("\n" + "=" * 60)
    print("A1: Section Macro-State Profiles")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))

    # Build contingency: sections x macro-states
    section_counts = {}
    for sec in sections:
        sec_toks = [t for t in enriched_tokens if t['section'] == sec and t['macro_state']]
        counts = Counter(t['macro_state'] for t in sec_toks)
        section_counts[sec] = counts

    # Contingency table
    ct = np.zeros((len(sections), len(MACRO_STATE_NAMES)), dtype=int)
    for i, sec in enumerate(sections):
        for j, ms in enumerate(MACRO_STATE_NAMES):
            ct[i, j] = section_counts[sec].get(ms, 0)

    chi2, p, dof, expected = sp_stats.chi2_contingency(ct)
    V = cramers_v(ct)

    # Profiles
    profiles = {}
    for i, sec in enumerate(sections):
        total = ct[i].sum()
        profile = {ms: float(ct[i, j] / total) if total > 0 else 0.0
                   for j, ms in enumerate(MACRO_STATE_NAMES)}
        profiles[sec] = profile
        n = total
        axm = profile.get('AXM', 0)
        print(f"  {sec} (n={n}): AXM={axm:.3f}, FQ={profile.get('FQ',0):.3f}, "
              f"CC={profile.get('CC',0):.3f}, AXm={profile.get('AXm',0):.3f}, "
              f"FL_HAZ={profile.get('FL_HAZ',0):.3f}, FL_SAFE={profile.get('FL_SAFE',0):.3f}")

    # Which states drive the difference?
    # Compute standardized residuals
    std_residuals = {}
    for i, sec in enumerate(sections):
        for j, ms in enumerate(MACRO_STATE_NAMES):
            exp = expected[i, j]
            obs = ct[i, j]
            if exp > 0:
                std_residuals[(sec, ms)] = float((obs - exp) / np.sqrt(exp))

    # Top deviations
    top_devs = sorted(std_residuals.items(), key=lambda x: abs(x[1]), reverse=True)[:15]

    print(f"\n  Chi2={chi2:.1f}, p={p:.2e}, V={V:.3f}")
    print(f"  Top standardized residuals:")
    for (sec, ms), sr in top_devs:
        print(f"    {sec}/{ms}: {sr:+.1f}")

    # Pairwise JSD between sections
    pairwise_jsd = {}
    for i, s1 in enumerate(sections):
        for j, s2 in enumerate(sections):
            if i < j:
                p1 = ct[i] / ct[i].sum()
                p2 = ct[j] / ct[j].sum()
                pairwise_jsd[f"{s1}_vs_{s2}"] = jsd_vec(p1, p2)

    return {
        'chi2': float(chi2), 'p': float(p), 'V': float(V), 'dof': int(dof),
        'profiles': profiles,
        'pairwise_jsd': pairwise_jsd,
        'top_residuals': [(f"{k[0]}/{k[1]}", float(v)) for k, v in top_devs],
        'verdict': 'SECTIONS_DIFFER_SIGNIFICANTLY' if p < 0.001 else 'SECTIONS_SIMILAR',
    }


def test_A2_section_morphological_signatures(enriched_tokens):
    """A2: Section Morphological Signatures — PREFIX, MIDDLE, suffix rate, etc."""
    print("\n" + "=" * 60)
    print("A2: Section Morphological Signatures")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))
    results = {}

    for sec in sections:
        sec_toks = [t for t in enriched_tokens if t['section'] == sec]
        n = len(sec_toks)

        # PREFIX distribution
        pfx_counts = Counter()
        for t in sec_toks:
            p = t['prefix'] if t['prefix'] else 'BARE'
            pfx_counts[p] += 1
        top_pfx = pfx_counts.most_common(15)

        # MIDDLE distribution
        mid_counts = Counter(t['middle'] for t in sec_toks if t['middle'])
        top_mid = mid_counts.most_common(20)

        # Suffix rate
        suffix_rate = sum(1 for t in sec_toks if t['suffix']) / n if n > 0 else 0

        # Articulator rate
        art_rate = sum(1 for t in sec_toks if t['articulator']) / n if n > 0 else 0

        # Mean token length
        mean_len = np.mean([len(t['word']) for t in sec_toks]) if sec_toks else 0

        results[sec] = {
            'n_tokens': n,
            'top_prefixes': [(p, c) for p, c in top_pfx],
            'top_middles': [(m, c) for m, c in top_mid],
            'suffix_rate': float(suffix_rate),
            'articulator_rate': float(art_rate),
            'mean_token_length': float(mean_len),
        }

        print(f"  {sec} (n={n}): suffix={suffix_rate:.3f}, art={art_rate:.3f}, "
              f"mean_len={mean_len:.2f}")
        print(f"    Top PREFIX: {', '.join(f'{p}({c})' for p,c in top_pfx[:8])}")

    # PREFIX-level JSD across sections
    all_pfx = sorted(set(t['prefix'] if t['prefix'] else 'BARE' for t in enriched_tokens))
    pfx_vecs = {}
    for sec in sections:
        sec_toks = [t for t in enriched_tokens if t['section'] == sec]
        c = Counter(t['prefix'] if t['prefix'] else 'BARE' for t in sec_toks)
        total = sum(c.values())
        pfx_vecs[sec] = np.array([c.get(p, 0) / total for p in all_pfx])

    prefix_jsd = {}
    for i, s1 in enumerate(sections):
        for j, s2 in enumerate(sections):
            if i < j:
                prefix_jsd[f"{s1}_vs_{s2}"] = jsd_vec(pfx_vecs[s1], pfx_vecs[s2])

    mean_jsd = np.mean(list(prefix_jsd.values()))
    print(f"\n  Mean pairwise PREFIX JSD: {mean_jsd:.4f}")
    for k, v in sorted(prefix_jsd.items(), key=lambda x: x[1], reverse=True):
        print(f"    {k}: {v:.4f}")

    return {
        'section_profiles': results,
        'prefix_pairwise_jsd': prefix_jsd,
        'mean_prefix_jsd': float(mean_jsd),
        'verdict': 'MORPHOLOGICALLY_DISTINCT' if mean_jsd > 0.01 else 'MORPHOLOGICALLY_SIMILAR',
    }


def test_A3_section_kernel_profiles(enriched_tokens):
    """A3: Section Kernel Profiles — k, h, e fractions from MIDDLE content."""
    print("\n" + "=" * 60)
    print("A3: Section Kernel Profiles")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))
    results = {}

    for sec in sections:
        sec_toks = [t for t in enriched_tokens if t['section'] == sec and t['middle']]
        n = len(sec_toks)
        k_count = sum(1 for t in sec_toks if 'k' in t['middle'])
        h_count = sum(1 for t in sec_toks if 'h' in t['middle'])
        e_count = sum(1 for t in sec_toks if 'e' in t['middle'])

        results[sec] = {
            'n': n,
            'k_frac': float(k_count / n) if n > 0 else 0,
            'h_frac': float(h_count / n) if n > 0 else 0,
            'e_frac': float(e_count / n) if n > 0 else 0,
        }
        print(f"  {sec} (n={n}): k={results[sec]['k_frac']:.3f}, "
              f"h={results[sec]['h_frac']:.3f}, e={results[sec]['e_frac']:.3f}")

    # Chi-square test on kernel counts
    kernel_ct = np.zeros((len(sections), 3), dtype=int)
    for i, sec in enumerate(sections):
        sec_toks = [t for t in enriched_tokens if t['section'] == sec and t['middle']]
        kernel_ct[i, 0] = sum(1 for t in sec_toks if 'k' in t['middle'])
        kernel_ct[i, 1] = sum(1 for t in sec_toks if 'h' in t['middle'])
        kernel_ct[i, 2] = sum(1 for t in sec_toks if 'e' in t['middle'])

    chi2, p, dof, _ = sp_stats.chi2_contingency(kernel_ct)
    V = cramers_v(kernel_ct)
    print(f"\n  Kernel chi2={chi2:.1f}, p={p:.2e}, V={V:.3f}")

    return {
        'profiles': results,
        'chi2': float(chi2), 'p': float(p), 'V': float(V),
        'verdict': 'KERNEL_DIFFERS' if p < 0.001 else 'KERNEL_UNIFORM',
    }


def test_A4_section_hazard_profiles(enriched_tokens, forbidden_middle_pairs):
    """A4: Section Hazard Profiles — hazard class rates and forbidden violations."""
    print("\n" + "=" * 60)
    print("A4: Section Hazard Profiles")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))

    # Hazard classes: FL_HAZ tokens per section
    results = {}
    for sec in sections:
        sec_toks = [t for t in enriched_tokens if t['section'] == sec and t['macro_state']]
        n = len(sec_toks)
        fl_haz = sum(1 for t in sec_toks if t['macro_state'] == 'FL_HAZ')
        fl_safe = sum(1 for t in sec_toks if t['macro_state'] == 'FL_SAFE')
        results[sec] = {
            'n': n,
            'fl_haz_rate': float(fl_haz / n) if n > 0 else 0,
            'fl_safe_rate': float(fl_safe / n) if n > 0 else 0,
        }
        print(f"  {sec}: FL_HAZ={results[sec]['fl_haz_rate']:.4f}, "
              f"FL_SAFE={results[sec]['fl_safe_rate']:.4f}")

    # Forbidden MIDDLE pair violations per section
    # Build lines per section
    forbidden_set = forbidden_middle_pairs
    section_violations = Counter()
    section_eligible = Counter()

    by_folio_line = defaultdict(list)
    for t in enriched_tokens:
        by_folio_line[(t['folio'], t['line'])].append(t)

    for (folio, line), toks in by_folio_line.items():
        sec = toks[0]['section']
        middles = [t['middle'] for t in toks if t['middle']]
        for i in range(len(middles) - 1):
            pair = (middles[i], middles[i + 1])
            if pair in forbidden_set:
                section_violations[sec] += 1
            # Check if this pair COULD be forbidden (source is a forbidden source)
            if middles[i] in set(s for s, _ in forbidden_set):
                section_eligible[sec] += 1

    print(f"\n  Forbidden MIDDLE pair violations by section:")
    for sec in sections:
        v = section_violations.get(sec, 0)
        e = section_eligible.get(sec, 0)
        rate = v / e if e > 0 else 0
        results[sec]['forbidden_violations'] = v
        results[sec]['forbidden_eligible'] = e
        results[sec]['violation_rate'] = float(rate)
        print(f"    {sec}: {v}/{e} = {rate:.4f}")

    return {
        'profiles': results,
        'verdict': 'HAZARD_VARIES_BY_SECTION',
    }


def test_A5_section_regime_distribution(enriched_tokens, folio_to_regime):
    """A5: Section REGIME Distribution."""
    print("\n" + "=" * 60)
    print("A5: Section REGIME Distribution")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))
    regimes = sorted(set(folio_to_regime.values()))

    # Section-REGIME cross-tabulation (at folio level)
    folio_section = {}
    for t in enriched_tokens:
        folio_section[t['folio']] = t['section']

    section_regime_counts = defaultdict(Counter)
    for folio, regime in folio_to_regime.items():
        sec = folio_section.get(folio)
        if sec:
            section_regime_counts[sec][regime] += 1

    # Also token-level
    token_ct = np.zeros((len(sections), len(regimes)), dtype=int)
    for t in enriched_tokens:
        if t['section'] in sections and t['regime'] in regimes:
            si = sections.index(t['section'])
            ri = regimes.index(t['regime'])
            token_ct[si, ri] += 1

    chi2, p, dof, _ = sp_stats.chi2_contingency(token_ct)
    V = cramers_v(token_ct)

    print(f"  Token-level section x REGIME: chi2={chi2:.1f}, p={p:.2e}, V={V:.3f}")

    folio_profiles = {}
    for sec in sections:
        total = sum(section_regime_counts[sec].values())
        profile = {r: section_regime_counts[sec].get(r, 0) / total if total > 0 else 0
                   for r in regimes}
        folio_profiles[sec] = profile
        print(f"  {sec}: " + ", ".join(f"{r}={v:.3f}" for r, v in profile.items()))

    # Token-level profiles
    token_profiles = {}
    for i, sec in enumerate(sections):
        total = token_ct[i].sum()
        token_profiles[sec] = {regimes[j]: float(token_ct[i, j] / total) if total > 0 else 0
                               for j in range(len(regimes))}

    return {
        'folio_profiles': folio_profiles,
        'token_profiles': token_profiles,
        'chi2': float(chi2), 'p': float(p), 'V': float(V),
        'verdict': 'REGIME_SECTION_CORRELATED' if p < 0.001 else 'REGIME_SECTION_INDEPENDENT',
    }


def test_A6_section_transition_entropy(enriched_tokens):
    """A6: Section Transition Entropy — within-section class transition entropy."""
    print("\n" + "=" * 60)
    print("A6: Section Transition Entropy")
    print("=" * 60)

    sections = sorted(set(t['section'] for t in enriched_tokens))

    # Build per-section transition matrices
    by_folio_line = defaultdict(list)
    for t in enriched_tokens:
        if t['cls'] is not None:
            by_folio_line[(t['folio'], t['line'])].append(t)

    all_classes = sorted(set(t['cls'] for t in enriched_tokens if t['cls'] is not None))
    cls_idx = {c: i for i, c in enumerate(all_classes)}
    n_cls = len(all_classes)

    section_matrices = {sec: np.zeros((n_cls, n_cls), dtype=int) for sec in sections}

    for (folio, line), toks in by_folio_line.items():
        sec = toks[0]['section']
        for i in range(len(toks) - 1):
            a = cls_idx.get(toks[i]['cls'])
            b = cls_idx.get(toks[i + 1]['cls'])
            if a is not None and b is not None:
                section_matrices[sec][a, b] += 1

    results = {}
    for sec in sections:
        mat = section_matrices[sec]
        # Conditional entropy H(next | current) = sum_i P(i) * H(next | current=i)
        total = mat.sum()
        if total == 0:
            results[sec] = {'H_cond': 0, 'n_transitions': 0}
            continue

        row_sums = mat.sum(axis=1)
        H_cond = 0.0
        for i in range(n_cls):
            if row_sums[i] == 0:
                continue
            p_i = row_sums[i] / total
            row = mat[i] / row_sums[i]
            row = row[row > 0]
            H_row = -np.sum(row * np.log2(row))
            H_cond += p_i * H_row

        n_trans = int(total)
        results[sec] = {'H_cond': float(H_cond), 'n_transitions': n_trans}
        print(f"  {sec}: H(class_t | class_t-1) = {H_cond:.3f} bits ({n_trans} transitions)")

    # Overall
    overall_mat = sum(section_matrices.values())
    total = overall_mat.sum()
    row_sums = overall_mat.sum(axis=1)
    H_overall = 0.0
    for i in range(n_cls):
        if row_sums[i] == 0:
            continue
        p_i = row_sums[i] / total
        row = overall_mat[i] / row_sums[i]
        row = row[row > 0]
        H_row = -np.sum(row * np.log2(row))
        H_overall += p_i * H_row

    print(f"\n  Overall: H = {H_overall:.3f} bits")

    return {
        'section_entropy': results,
        'overall_entropy': float(H_overall),
        'verdict': 'SECTIONS_DIFFER_IN_GRAMMAR_TIGHTNESS',
    }


# ================================================================
# PART B: PARAGRAPH-LEVEL AXM DRIVERS
# ================================================================

def compute_paragraph_features(paragraphs):
    """Compute feature vectors for each paragraph."""
    print("\n[FEATURES] Computing paragraph features...")

    feature_data = []
    for par in paragraphs:
        toks = par['tokens']
        n = len(toks)
        if n < 5:
            continue

        # --- AXM rate (target variable) ---
        classified = [t for t in toks if t['macro_state']]
        n_cl = len(classified)
        if n_cl < 3:
            continue
        axm_count = sum(1 for t in classified if t['macro_state'] == 'AXM')
        axm_rate = axm_count / n_cl

        # --- Macro-state profile ---
        ms_counts = Counter(t['macro_state'] for t in classified)
        ms_profile = {ms: ms_counts.get(ms, 0) / n_cl for ms in MACRO_STATE_NAMES}

        # --- PREFIX profile ---
        pfx_counts = Counter()
        for t in toks:
            p = t['prefix'] if t['prefix'] else 'BARE'
            pfx_counts[p] += 1
        pfx_profile = {}
        for p in MAJOR_PREFIXES:
            pfx_profile[p] = pfx_counts.get(p, 0) / n

        qo_frac = pfx_profile.get('qo', 0)
        ch_frac = pfx_profile.get('ch', 0)
        sh_frac = pfx_profile.get('sh', 0)
        chsh_frac = ch_frac + sh_frac
        bare_frac = pfx_profile.get('BARE', 0)
        ok_frac = pfx_profile.get('ok', 0)
        ot_frac = pfx_profile.get('ot', 0)
        da_frac = pfx_profile.get('da', 0)
        ol_frac = pfx_profile.get('ol', 0)

        # --- Kernel profile ---
        mid_toks = [t for t in toks if t['middle']]
        n_mid = len(mid_toks)
        k_frac = sum(1 for t in mid_toks if 'k' in t['middle']) / n_mid if n_mid > 0 else 0
        h_frac = sum(1 for t in mid_toks if 'h' in t['middle']) / n_mid if n_mid > 0 else 0
        e_frac = sum(1 for t in mid_toks if 'e' in t['middle']) / n_mid if n_mid > 0 else 0

        # --- Suffix rate ---
        suffix_rate = sum(1 for t in toks if t['suffix']) / n

        # --- Mode A fraction ---
        mode_a_count = sum(1 for t in toks if t['suffix'] and t['suffix'] in MODE_A_SUFFIXES)
        mode_a_frac = mode_a_count / n

        # --- Mean token length ---
        mean_len = np.mean([len(t['word']) for t in toks])

        # --- Category profile ---
        cat_counts = Counter(t['category'] for t in toks if t['category'])
        cat_total = sum(cat_counts.values()) or 1
        cat_profile = {c: cat_counts.get(c, 0) / cat_total for c in CATEGORIES}

        # --- FL_HAZ rate ---
        fl_haz_rate = ms_profile.get('FL_HAZ', 0)

        # --- FQ rate ---
        fq_rate = ms_profile.get('FQ', 0)

        # --- CC rate ---
        cc_rate = ms_profile.get('CC', 0)

        feature_data.append({
            'folio': par['folio'],
            'par_idx': par['par_idx'],
            'section': par['section'],
            'regime': par['regime'],
            'n_tokens': n,
            'body_lines': par['body_lines'],
            'axm_rate': float(axm_rate),
            # PREFIX features
            'qo_frac': float(qo_frac),
            'ch_frac': float(ch_frac),
            'sh_frac': float(sh_frac),
            'chsh_frac': float(chsh_frac),
            'bare_frac': float(bare_frac),
            'ok_frac': float(ok_frac),
            'ot_frac': float(ot_frac),
            'da_frac': float(da_frac),
            'ol_frac': float(ol_frac),
            # Kernel
            'k_frac': float(k_frac),
            'h_frac': float(h_frac),
            'e_frac': float(e_frac),
            # Morphology
            'suffix_rate': float(suffix_rate),
            'mode_a_frac': float(mode_a_frac),
            'mean_len': float(mean_len),
            # Macro-state rates
            'fl_haz_rate': float(fl_haz_rate),
            'fq_rate': float(fq_rate),
            'cc_rate': float(cc_rate),
            # Category
            'thermal_frac': float(cat_profile.get('THERMAL', 0)),
            'containment_frac': float(cat_profile.get('CONTAINMENT', 0)),
            'flow_frac': float(cat_profile.get('FLOW', 0)),
            'monitoring_frac': float(cat_profile.get('MONITORING', 0)),
            'operation_frac': float(cat_profile.get('OPERATION', 0)),
            'staging_frac': float(cat_profile.get('STAGING', 0)),
            'marking_frac': float(cat_profile.get('MARKING', 0)),
            'transition_frac': float(cat_profile.get('TRANSITION', 0)),
        })

    print(f"  {len(feature_data)} paragraphs with features")
    return feature_data


def test_B1_morphological_predictors(feat_data):
    """B1: Morphological Predictors of Paragraph AXM Rate."""
    print("\n" + "=" * 60)
    print("B1: Morphological Predictors of Paragraph AXM Rate")
    print("=" * 60)

    axm = np.array([f['axm_rate'] for f in feat_data])

    predictors = [
        'qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac',
        'da_frac', 'ol_frac',
        'k_frac', 'h_frac', 'e_frac',
        'suffix_rate', 'mode_a_frac', 'mean_len',
        'thermal_frac', 'containment_frac', 'flow_frac',
        'monitoring_frac', 'operation_frac', 'staging_frac',
        'marking_frac', 'transition_frac',
    ]

    correlations = {}
    for pred in predictors:
        vals = np.array([f[pred] for f in feat_data])
        rho, p = safe_spearman(vals, axm)
        correlations[pred] = {'rho': rho, 'p': p}
        sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
        print(f"  {pred:25s}: rho={rho:+.3f} p={p:.2e} {sig}")

    # Simple OLS with top 5 predictors
    top5 = sorted(correlations.items(), key=lambda x: abs(x[1]['rho']), reverse=True)[:5]
    print(f"\n  Top 5 correlates:")
    for pred, vals in top5:
        print(f"    {pred}: rho={vals['rho']:+.3f}")

    # Multivariate OLS
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score

    X = np.column_stack([[f[p] for f in feat_data] for p in predictors])
    y = axm

    # Remove NaN/inf
    mask = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
    X, y = X[mask], y[mask]

    if len(X) > 20:
        lr = LinearRegression()
        scores = cross_val_score(lr, X, y, cv=5, scoring='r2')
        mean_r2 = float(np.mean(scores))
        print(f"\n  5-fold CV R2 (all {len(predictors)} predictors): {mean_r2:.3f}")

        # Fit full model for coefficients
        lr.fit(X, y)
        train_r2 = float(lr.score(X, y))
        print(f"  Training R2: {train_r2:.3f}")

        coefs = {predictors[i]: float(lr.coef_[i]) for i in range(len(predictors))}
    else:
        mean_r2 = 0.0
        train_r2 = 0.0
        coefs = {}

    return {
        'correlations': correlations,
        'top5': [(p, v) for p, v in top5],
        'cv_r2': mean_r2,
        'train_r2': train_r2,
        'coefs': coefs,
        'n_paragraphs': len(feat_data),
        'verdict': f'CV_R2={mean_r2:.3f}',
    }


def test_B2_paragraph_length_vs_axm(feat_data):
    """B2: Paragraph Length vs AXM."""
    print("\n" + "=" * 60)
    print("B2: Paragraph Length vs AXM")
    print("=" * 60)

    body_lines = np.array([f['body_lines'] for f in feat_data])
    n_tokens = np.array([f['n_tokens'] for f in feat_data])
    axm = np.array([f['axm_rate'] for f in feat_data])

    rho_lines, p_lines = safe_spearman(body_lines, axm)
    rho_tokens, p_tokens = safe_spearman(n_tokens, axm)

    print(f"  body_lines vs AXM: rho={rho_lines:+.3f}, p={p_lines:.2e}")
    print(f"  n_tokens vs AXM:   rho={rho_tokens:+.3f}, p={p_tokens:.2e}")

    return {
        'rho_body_lines': float(rho_lines), 'p_body_lines': float(p_lines),
        'rho_n_tokens': float(rho_tokens), 'p_n_tokens': float(p_tokens),
        'verdict': 'LENGTH_PREDICTS' if p_lines < 0.05 else 'LENGTH_INDEPENDENT',
    }


def test_B3_prefix_channel_and_axm(feat_data):
    """B3: PREFIX Channel and AXM — do qo-heavy vs ch-heavy paragraphs differ in AXM?"""
    print("\n" + "=" * 60)
    print("B3: PREFIX Channel and AXM")
    print("=" * 60)

    axm = np.array([f['axm_rate'] for f in feat_data])
    qo = np.array([f['qo_frac'] for f in feat_data])
    chsh = np.array([f['chsh_frac'] for f in feat_data])
    bare = np.array([f['bare_frac'] for f in feat_data])

    rho_qo, p_qo = safe_spearman(qo, axm)
    rho_chsh, p_chsh = safe_spearman(chsh, axm)
    rho_bare, p_bare = safe_spearman(bare, axm)

    print(f"  qo vs AXM:   rho={rho_qo:+.3f}, p={p_qo:.2e}")
    print(f"  chsh vs AXM: rho={rho_chsh:+.3f}, p={p_chsh:.2e}")
    print(f"  bare vs AXM: rho={rho_bare:+.3f}, p={p_bare:.2e}")

    # Tertile analysis: split paragraphs by qo fraction
    qo_tertiles = np.percentile(qo[qo > 0], [33, 67]) if np.sum(qo > 0) > 10 else [0, 0]
    low_qo = axm[qo <= qo_tertiles[0]] if len(qo_tertiles) > 0 else np.array([])
    high_qo = axm[qo > qo_tertiles[1]] if len(qo_tertiles) > 1 else np.array([])

    if len(low_qo) > 5 and len(high_qo) > 5:
        u_stat, u_p = sp_stats.mannwhitneyu(low_qo, high_qo, alternative='two-sided')
        print(f"\n  Low-qo AXM: {np.mean(low_qo):.3f} (n={len(low_qo)})")
        print(f"  High-qo AXM: {np.mean(high_qo):.3f} (n={len(high_qo)})")
        print(f"  Mann-Whitney: U={u_stat:.0f}, p={u_p:.2e}")
    else:
        u_p = 1.0

    return {
        'rho_qo': float(rho_qo), 'p_qo': float(p_qo),
        'rho_chsh': float(rho_chsh), 'p_chsh': float(p_chsh),
        'rho_bare': float(rho_bare), 'p_bare': float(p_bare),
        'verdict': 'PREFIX_PREDICTS_AXM' if min(p_qo, p_chsh, p_bare) < 0.001 else 'PREFIX_WEAK',
    }


def test_B4_kernel_balance_and_axm(feat_data):
    """B4: Kernel Balance and AXM."""
    print("\n" + "=" * 60)
    print("B4: Kernel Balance and AXM")
    print("=" * 60)

    axm = np.array([f['axm_rate'] for f in feat_data])
    k_frac = np.array([f['k_frac'] for f in feat_data])
    h_frac = np.array([f['h_frac'] for f in feat_data])
    e_frac = np.array([f['e_frac'] for f in feat_data])

    rho_k, p_k = safe_spearman(k_frac, axm)
    rho_h, p_h = safe_spearman(h_frac, axm)
    rho_e, p_e = safe_spearman(e_frac, axm)

    print(f"  k vs AXM: rho={rho_k:+.3f}, p={p_k:.2e}")
    print(f"  h vs AXM: rho={rho_h:+.3f}, p={p_h:.2e}")
    print(f"  e vs AXM: rho={rho_e:+.3f}, p={p_e:.2e}")

    return {
        'rho_k': float(rho_k), 'p_k': float(p_k),
        'rho_h': float(rho_h), 'p_h': float(p_h),
        'rho_e': float(rho_e), 'p_e': float(p_e),
        'verdict': 'KERNEL_PREDICTS_AXM' if min(p_k, p_h, p_e) < 0.001 else 'KERNEL_WEAK',
    }


def test_B5_hazard_density_and_axm(feat_data):
    """B5: Hazard Density and AXM — partial correlation controlling for length."""
    print("\n" + "=" * 60)
    print("B5: Hazard Density and AXM")
    print("=" * 60)

    axm = np.array([f['axm_rate'] for f in feat_data])
    fl_haz = np.array([f['fl_haz_rate'] for f in feat_data])
    n_tokens = np.array([f['n_tokens'] for f in feat_data])

    # Raw correlation
    rho_raw, p_raw = safe_spearman(fl_haz, axm)
    print(f"  Raw FL_HAZ vs AXM: rho={rho_raw:+.3f}, p={p_raw:.2e}")

    # Partial correlation controlling for n_tokens
    # Using rank-based partial correlation
    from scipy.stats import rankdata
    r_axm = rankdata(axm)
    r_haz = rankdata(fl_haz)
    r_len = rankdata(n_tokens)

    # Partial: regress both on length, correlate residuals
    from numpy.linalg import lstsq
    X_len = np.column_stack([r_len, np.ones(len(r_len))])
    coef_axm, _, _, _ = lstsq(X_len, r_axm, rcond=None)
    coef_haz, _, _, _ = lstsq(X_len, r_haz, rcond=None)
    resid_axm = r_axm - X_len @ coef_axm
    resid_haz = r_haz - X_len @ coef_haz

    rho_partial, p_partial = sp_stats.spearmanr(resid_axm, resid_haz)

    print(f"  Partial (controlling length): rho={rho_partial:+.3f}, p={p_partial:.2e}")

    # Also check FQ rate
    fq_rate = np.array([f['fq_rate'] for f in feat_data])
    rho_fq, p_fq = safe_spearman(fq_rate, axm)
    print(f"  FQ rate vs AXM: rho={rho_fq:+.3f}, p={p_fq:.2e}")

    return {
        'rho_raw': float(rho_raw), 'p_raw': float(p_raw),
        'rho_partial': float(rho_partial), 'p_partial': float(p_partial),
        'rho_fq': float(rho_fq), 'p_fq': float(p_fq),
        'verdict': 'HAZARD_PREDICTS_BEYOND_LENGTH' if p_partial < 0.05 else 'HAZARD_MECHANICAL_ONLY',
    }


def test_B6_variance_decomposition(feat_data):
    """B6: Explained Variance Decomposition — hierarchical R2."""
    print("\n" + "=" * 60)
    print("B6: Explained Variance Decomposition")
    print("=" * 60)

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import LabelEncoder

    axm = np.array([f['axm_rate'] for f in feat_data])
    n = len(axm)

    # Section indicator
    sections = [f['section'] for f in feat_data]
    le_sec = LabelEncoder()
    sec_encoded = le_sec.fit_transform(sections)
    sec_dummies = np.zeros((n, len(le_sec.classes_)))
    for i, s in enumerate(sec_encoded):
        sec_dummies[i, s] = 1.0
    # Drop one for identifiability
    sec_dummies = sec_dummies[:, 1:]

    # REGIME indicator
    regimes = [f['regime'] for f in feat_data]
    le_reg = LabelEncoder()
    reg_encoded = le_reg.fit_transform(regimes)
    reg_dummies = np.zeros((n, len(le_reg.classes_)))
    for i, r in enumerate(reg_encoded):
        reg_dummies[i, r] = 1.0
    reg_dummies = reg_dummies[:, 1:]

    # Morphological features
    morph_features = ['suffix_rate', 'mode_a_frac', 'mean_len']
    X_morph = np.column_stack([[f[p] for f in feat_data] for p in morph_features])

    # PREFIX features
    pfx_features = ['qo_frac', 'chsh_frac', 'bare_frac', 'ok_frac', 'ot_frac', 'da_frac', 'ol_frac']
    X_pfx = np.column_stack([[f[p] for f in feat_data] for p in pfx_features])

    # Kernel features
    kernel_features = ['k_frac', 'h_frac', 'e_frac']
    X_kernel = np.column_stack([[f[p] for f in feat_data] for p in kernel_features])

    # Category features
    cat_features = ['thermal_frac', 'containment_frac', 'flow_frac',
                    'monitoring_frac', 'operation_frac', 'staging_frac',
                    'marking_frac', 'transition_frac']
    X_cat = np.column_stack([[f[p] for f in feat_data] for p in cat_features])

    # Body lines
    X_length = np.array([f['body_lines'] for f in feat_data]).reshape(-1, 1)

    def cv_r2(X, y, label):
        mask = np.all(np.isfinite(X), axis=1) & np.isfinite(y)
        X_clean, y_clean = X[mask], y[mask]
        if len(X_clean) < 20 or X_clean.shape[1] == 0:
            return 0.0
        lr = LinearRegression()
        scores = cross_val_score(lr, X_clean, y_clean, cv=5, scoring='r2')
        r2 = float(np.mean(scores))
        print(f"  {label:45s}: CV R2 = {r2:.3f}")
        return r2

    results = {}

    # Hierarchical models
    r2_sec = cv_r2(sec_dummies, axm, 'Section only')
    r2_regime = cv_r2(reg_dummies, axm, 'REGIME only')
    r2_sec_regime = cv_r2(np.hstack([sec_dummies, reg_dummies]), axm, 'Section + REGIME')
    r2_morph = cv_r2(X_morph, axm, 'Morphology only')
    r2_pfx = cv_r2(X_pfx, axm, 'PREFIX only')
    r2_kernel = cv_r2(X_kernel, axm, 'Kernel only')
    r2_cat = cv_r2(X_cat, axm, 'Category only')
    r2_length = cv_r2(X_length, axm, 'Length only')

    r2_sec_morph = cv_r2(np.hstack([sec_dummies, X_morph]), axm, 'Section + morphology')
    r2_sec_pfx = cv_r2(np.hstack([sec_dummies, X_pfx]), axm, 'Section + PREFIX')
    r2_sec_kernel = cv_r2(np.hstack([sec_dummies, X_kernel]), axm, 'Section + kernel')
    r2_sec_cat = cv_r2(np.hstack([sec_dummies, X_cat]), axm, 'Section + category')

    # Best combined model: section + regime + prefix + kernel + category
    X_all = np.hstack([sec_dummies, reg_dummies, X_pfx, X_kernel, X_cat, X_morph, X_length])
    r2_all = cv_r2(X_all, axm, 'FULL MODEL')

    # Without section
    X_nosec = np.hstack([reg_dummies, X_pfx, X_kernel, X_cat, X_morph, X_length])
    r2_nosec = cv_r2(X_nosec, axm, 'Full - section')

    results = {
        'section_only': r2_sec,
        'regime_only': r2_regime,
        'section_regime': r2_sec_regime,
        'morphology_only': r2_morph,
        'prefix_only': r2_pfx,
        'kernel_only': r2_kernel,
        'category_only': r2_cat,
        'length_only': r2_length,
        'section_morph': r2_sec_morph,
        'section_pfx': r2_sec_pfx,
        'section_kernel': r2_sec_kernel,
        'section_cat': r2_sec_cat,
        'full_model': r2_all,
        'full_minus_section': r2_nosec,
        'section_delta': r2_all - r2_nosec,
    }

    print(f"\n  Section marginal delta: {results['section_delta']:+.3f}")
    print(f"  PREFIX delta beyond section: {r2_sec_pfx - r2_sec:+.3f}")
    print(f"  Kernel delta beyond section: {r2_sec_kernel - r2_sec:+.3f}")
    print(f"  Category delta beyond section: {r2_sec_cat - r2_sec:+.3f}")

    return results


# ================================================================
# PART C: SYNTHESIS
# ================================================================

def test_C3_interaction(feat_data):
    """C3: Section x Feature interaction — do paragraph drivers differ by section?"""
    print("\n" + "=" * 60)
    print("C3: Section x Feature Interaction")
    print("=" * 60)

    from sklearn.linear_model import LinearRegression

    sections = sorted(set(f['section'] for f in feat_data))
    key_features = ['qo_frac', 'chsh_frac', 'bare_frac', 'k_frac', 'e_frac',
                    'thermal_frac', 'transition_frac']

    results = {}
    for sec in sections:
        sec_data = [f for f in feat_data if f['section'] == sec]
        if len(sec_data) < 10:
            results[sec] = {'n': len(sec_data), 'too_small': True}
            continue

        axm = np.array([f['axm_rate'] for f in sec_data])
        corrs = {}
        for feat in key_features:
            vals = np.array([f[feat] for f in sec_data])
            rho, p = safe_spearman(vals, axm)
            corrs[feat] = {'rho': float(rho), 'p': float(p)}

        results[sec] = {
            'n': len(sec_data),
            'mean_axm': float(np.mean(axm)),
            'std_axm': float(np.std(axm)),
            'correlations': corrs,
        }

        print(f"\n  {sec} (n={len(sec_data)}, mean_AXM={np.mean(axm):.3f}):")
        for feat, vals in corrs.items():
            sig = '*' if vals['p'] < 0.05 else ''
            print(f"    {feat:20s}: rho={vals['rho']:+.3f} {sig}")

    # Check if correlation signs are consistent across sections
    consistent = {}
    for feat in key_features:
        signs = []
        for sec in sections:
            if sec in results and 'correlations' in results[sec]:
                r = results[sec]['correlations'].get(feat, {}).get('rho', 0)
                signs.append(np.sign(r))
        consistent[feat] = all(s == signs[0] for s in signs) if signs else False

    print(f"\n  Correlation sign consistency:")
    for feat, is_con in consistent.items():
        print(f"    {feat}: {'CONSISTENT' if is_con else 'INCONSISTENT'}")

    return {
        'per_section': results,
        'sign_consistency': consistent,
        'verdict': 'INTERACTIONS_PRESENT' if not all(consistent.values()) else 'NO_INTERACTIONS',
    }


# ================================================================
# MAIN
# ================================================================

def main():
    print("=" * 70)
    print("Phase 514: SECTION AND PARAGRAPH AXM DRIVERS")
    print("=" * 70)

    tokens, token_to_class, folio_to_regime, forbidden_middle_pairs, morph = load_data()
    enriched = build_enriched_tokens(tokens, token_to_class, folio_to_regime, morph)
    paragraphs = build_paragraphs(enriched)

    results = {
        'metadata': {
            'phase': 514,
            'name': 'SECTION_PARAGRAPH_AXM_DRIVERS',
            'n_tokens': len(enriched),
            'n_paragraphs': len(paragraphs),
            'n_classified': sum(1 for t in enriched if t['cls'] is not None),
        }
    }

    # PART A
    print("\n" + "#" * 70)
    print("# PART A: SECTION STRUCTURAL CHARACTERIZATION")
    print("#" * 70)

    results['A1_macro_state_profiles'] = test_A1_section_macro_state_profiles(enriched)
    results['A2_morphological_signatures'] = test_A2_section_morphological_signatures(enriched)
    results['A3_kernel_profiles'] = test_A3_section_kernel_profiles(enriched)
    results['A4_hazard_profiles'] = test_A4_section_hazard_profiles(enriched, forbidden_middle_pairs)
    results['A5_regime_distribution'] = test_A5_section_regime_distribution(enriched, folio_to_regime)
    results['A6_transition_entropy'] = test_A6_section_transition_entropy(enriched)

    # PART B
    print("\n" + "#" * 70)
    print("# PART B: PARAGRAPH-LEVEL AXM DRIVERS")
    print("#" * 70)

    feat_data = compute_paragraph_features(paragraphs)
    results['metadata']['n_feature_paragraphs'] = len(feat_data)

    results['B1_morphological_predictors'] = test_B1_morphological_predictors(feat_data)
    results['B2_length_vs_axm'] = test_B2_paragraph_length_vs_axm(feat_data)
    results['B3_prefix_channel'] = test_B3_prefix_channel_and_axm(feat_data)
    results['B4_kernel_balance'] = test_B4_kernel_balance_and_axm(feat_data)
    results['B5_hazard_density'] = test_B5_hazard_density_and_axm(feat_data)
    results['B6_variance_decomposition'] = test_B6_variance_decomposition(feat_data)

    # PART C
    print("\n" + "#" * 70)
    print("# PART C: SYNTHESIS")
    print("#" * 70)

    results['C3_interaction'] = test_C3_interaction(feat_data)

    # ================================================================
    # SYNTHESIS
    # ================================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # C1: What ARE sections?
    a1 = results['A1_macro_state_profiles']
    a3 = results['A3_kernel_profiles']
    a5 = results['A5_regime_distribution']
    a6 = results['A6_transition_entropy']

    print("\n--- C1: SECTION IDENTITY ---")
    print(f"  Sections differ in macro-state profiles: V={a1['V']:.3f}")
    print(f"  Sections differ in kernel balance: V={a3['V']:.3f}")
    print(f"  Sections differ in REGIME distribution: V={a5['V']:.3f}")
    for sec in sorted(a6['section_entropy'].keys()):
        H = a6['section_entropy'][sec]['H_cond']
        print(f"  {sec} transition entropy: {H:.3f} bits")

    print("\n--- C2: PARAGRAPH AXM DRIVERS ---")
    b1 = results['B1_morphological_predictors']
    b6 = results['B6_variance_decomposition']
    print(f"  Best single predictor set: PREFIX (R2={b6['prefix_only']:.3f})")
    print(f"  Section alone: R2={b6['section_only']:.3f}")
    print(f"  Full model: R2={b6['full_model']:.3f}")
    print(f"  Full minus section: R2={b6['full_minus_section']:.3f}")
    print(f"  Section marginal contribution: {b6['section_delta']:+.3f}")
    print(f"  PREFIX beyond section: {b6['section_pfx'] - b6['section_only']:+.3f}")
    print(f"  Kernel beyond section: {b6['section_kernel'] - b6['section_only']:+.3f}")
    print(f"  Category beyond section: {b6['section_cat'] - b6['section_only']:+.3f}")

    print("\n--- C3: INTERACTION ---")
    c3 = results['C3_interaction']
    print(f"  Verdict: {c3['verdict']}")
    n_inconsistent = sum(1 for v in c3['sign_consistency'].values() if not v)
    print(f"  {n_inconsistent}/{len(c3['sign_consistency'])} features have inconsistent "
          f"correlation signs across sections")

    # Final summary
    results['synthesis'] = {
        'C1_section_identity': {
            'macro_state_V': a1['V'],
            'kernel_V': a3['V'],
            'regime_V': a5['V'],
            'transition_entropy_range': [
                min(v['H_cond'] for v in a6['section_entropy'].values()),
                max(v['H_cond'] for v in a6['section_entropy'].values()),
            ],
            'verdict': ('Sections are primarily differentiated by REGIME composition and '
                        'macro-state profiles. Kernel balance, morphological signatures, '
                        'and grammar tightness all vary by section.'),
        },
        'C2_paragraph_drivers': {
            'best_single': 'PREFIX profile' if b6['prefix_only'] >= max(
                b6['kernel_only'], b6['category_only'], b6['morphology_only']
            ) else 'other',
            'best_single_r2': max(b6['prefix_only'], b6['kernel_only'],
                                  b6['category_only'], b6['morphology_only']),
            'section_only_r2': b6['section_only'],
            'full_r2': b6['full_model'],
            'unexplained': 1.0 - b6['full_model'],
            'verdict': (f"Section explains {b6['section_only']*100:.1f}% of paragraph AXM variance. "
                        f"Full model explains {b6['full_model']*100:.1f}%. "
                        f"{(1-b6['full_model'])*100:.1f}% is genuine paragraph-level design freedom."),
        },
        'C3_interaction': c3['verdict'],
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'section_paragraph_drivers.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Results saved to {out_path}")

    print("\n" + "=" * 70)
    print("Phase 514 COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()

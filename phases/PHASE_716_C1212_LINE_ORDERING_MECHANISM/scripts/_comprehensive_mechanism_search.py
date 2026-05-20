"""PHASE_716 comprehensive mechanism search.

Test all remaining hypotheses for C1727 line-ordering smoothness mechanism in
one comprehensive grid. Each test isolates a candidate mechanism by either:
  (A) ABLATION: remove feature subset, see if smoothness persists
  (B) RESIDUALIZATION: subtract group-mean (paragraph/section), see if signal collapses
  (C) SUBSET: use only specific features, see if smoothness exists in subset alone

Mechanisms tested:
  - Paragraph-level vocabulary pool (paragraph-mean residualization)
  - Section-level vocabulary (section-mean residualization)
  - Line length adjacency (length feature isolation/ablation)
  - HEAD distribution coherence (HEAD feature isolation/ablation)
  - TERM distribution coherence (TERM feature isolation/ablation)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

OUT_PATH = ROOT / 'phases' / 'PHASE_716_C1212_LINE_ORDERING_MECHANISM' / 'results' / 'comprehensive_mechanism_results.json'

HEAD_TYPES = ['a', 'e', 'o', 'k', 't', 'headless']
TERM_TYPES = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']
HEAD_IDX = {h: i for i, h in enumerate(HEAD_TYPES)}
TERM_IDX = {t: i for i, t in enumerate(TERM_TYPES)}

# Feature vector indices
HEAD_SLICE = slice(0, 6)       # 6 dims
TERM_SLICE = slice(6, 13)      # 7 dims
MODE_IDX_VEC = 13              # 1 dim
LENGTH_IDX_VEC = 14            # 1 dim

MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

# Section assignments (copied from LINE_ORDERING_INFORMATION_CONTENT)
SECTION_PREFIX_MAP = {}
# Approximate by folio number range — Currier B sections
def get_section(folio):
    """Map folio to section (B sub-categorization)."""
    # f75-89 = B (balneology), f99-102 = S (recipes), f103-116 = C (recipes), f86 = S
    if folio.startswith('f86'):
        return 'S'
    if folio.startswith('f9') and not folio.startswith('f9r') and not folio.startswith('f9v'):
        return 'S'
    if folio.startswith('f10') and not folio.startswith('f10r') and not folio.startswith('f10v'):
        return 'S' if folio[:5] in ['f100', 'f101', 'f102'] else 'C'
    if folio.startswith('f1') and folio[:4] in ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f111', 'f112', 'f113', 'f114', 'f115', 'f116']:
        return 'C'
    # f75-89 etc = B
    return 'B'

N_SHUFFLES = 500
SEED = 42


def atomize_suffix(suffix):
    if not suffix:
        return []
    atoms = []
    i = 0
    while i < len(suffix):
        if i + 1 < len(suffix) and suffix[i] == suffix[i+1] and suffix[i] in ('e', 'i'):
            atoms.append(suffix[i:i+2])
            i += 2
        else:
            atoms.append(suffix[i])
            i += 1
    return atoms


def get_line_mode(tokens_with_suffix):
    a_count = 0
    b_count = 0
    for suffix in tokens_with_suffix:
        if suffix:
            for atom in atomize_suffix(suffix):
                if atom in MODE_A_ATOMS:
                    a_count += 1
                elif atom in MODE_B_ATOMS:
                    b_count += 1
    if a_count + b_count == 0:
        return None
    return 'A' if a_count > b_count else 'B'


def build_line_features(line_tokens, morph):
    head_counts = np.zeros(len(HEAD_TYPES))
    term_counts = np.zeros(len(TERM_TYPES))
    suffixes = []
    n_valid = 0
    for tok in line_tokens:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m.middle:
            head, mods, term, frame = decompose_middle_hmt(m.middle)
            head = head if head else 'headless'
            if head in HEAD_IDX:
                head_counts[HEAD_IDX[head]] += 1
            if term in TERM_IDX:
                term_counts[TERM_IDX[term]] += 1
            n_valid += 1
        suffixes.append(m.suffix if m else None)
    if n_valid == 0:
        return None
    head_frac = head_counts / n_valid
    term_frac = term_counts / n_valid
    mode = get_line_mode(suffixes)
    mode_val = 1.0 if mode == 'A' else 0.0 if mode == 'B' else 0.5
    line_len = float(len(line_tokens))
    return np.concatenate([head_frac, term_frac, [mode_val], [line_len]])


def assemble_paragraphs():
    tx = Transcript()
    morph = Morphology()
    lines_dict = defaultdict(list)
    for t in tx.currier_b():
        w = t.word.strip()
        if not w:
            continue
        if t.placement.startswith('L'):
            continue
        lines_dict[(t.folio, t.line)].append(t)
    folio_lines = defaultdict(list)
    for (folio, line_num), tokens in sorted(lines_dict.items()):
        folio_lines[folio].append((line_num, tokens))
    paragraphs = {f: [t for _, t in lines] for f, lines in folio_lines.items() if len(lines) >= 3}
    return paragraphs, morph


# ---- Feature transformations ----

def transform_features(features, scheme, paragraph_id=None, paragraph_means=None,
                      section_id=None, section_means=None):
    """Apply transformation to features per scheme. Returns transformed feature vector
    or None if scheme excludes this case."""
    f = features.copy()
    if scheme == 'baseline':
        return f
    elif scheme == 'paragraph_mean_residualized':
        if paragraph_id and paragraph_id in paragraph_means:
            return f - paragraph_means[paragraph_id]
        return None
    elif scheme == 'section_mean_residualized':
        if section_id and section_id in section_means:
            return f - section_means[section_id]
        return None
    elif scheme == 'head_only':
        return f[HEAD_SLICE]
    elif scheme == 'term_only':
        return f[TERM_SLICE]
    elif scheme == 'length_only':
        return f[LENGTH_IDX_VEC:LENGTH_IDX_VEC+1]
    elif scheme == 'mode_only':
        return f[MODE_IDX_VEC:MODE_IDX_VEC+1]
    elif scheme == 'head_term_only':
        return np.concatenate([f[HEAD_SLICE], f[TERM_SLICE]])
    elif scheme == 'no_head':
        return np.concatenate([f[TERM_SLICE], f[MODE_IDX_VEC:MODE_IDX_VEC+1], f[LENGTH_IDX_VEC:LENGTH_IDX_VEC+1]])
    elif scheme == 'no_term':
        return np.concatenate([f[HEAD_SLICE], f[MODE_IDX_VEC:MODE_IDX_VEC+1], f[LENGTH_IDX_VEC:LENGTH_IDX_VEC+1]])
    elif scheme == 'no_length':
        return f[:LENGTH_IDX_VEC]
    elif scheme == 'no_mode':
        return np.concatenate([f[HEAD_SLICE], f[TERM_SLICE], f[LENGTH_IDX_VEC:LENGTH_IDX_VEC+1]])
    else:
        raise ValueError(scheme)


def compute_paragraph_and_section_means(paragraphs, morph):
    """Compute mean feature vector per paragraph and per section."""
    para_features = defaultdict(list)
    section_features = defaultdict(list)
    for folio, line_token_lists in paragraphs.items():
        section = get_section(folio)
        for tokens in line_token_lists:
            f = build_line_features(tokens, morph)
            if f is not None:
                para_features[folio].append(f)
                section_features[section].append(f)
    paragraph_means = {f: np.mean(np.array(fs), axis=0) for f, fs in para_features.items() if fs}
    section_means = {s: np.mean(np.array(fs), axis=0) for s, fs in section_features.items() if fs}
    return paragraph_means, section_means


def compute_score(paragraphs, morph, scheme, paragraph_means, section_means):
    """Compute sequential-structure-score across paragraphs under given scheme."""
    total = 0.0
    n_pairs = 0
    for folio, line_token_lists in paragraphs.items():
        section = get_section(folio)
        features = []
        for tokens in line_token_lists:
            f = build_line_features(tokens, morph)
            if f is None:
                continue
            f_trans = transform_features(f, scheme, paragraph_id=folio, paragraph_means=paragraph_means,
                                         section_id=section, section_means=section_means)
            if f_trans is not None:
                features.append(f_trans)
        if len(features) >= 2:
            features = np.array(features)
            diffs = np.diff(features, axis=0)
            total += float(np.sum(diffs ** 2))
            n_pairs += len(features) - 1
    return total, n_pairs


def shuffle_null(paragraphs, morph, scheme, paragraph_means, section_means,
                n_shuffles=N_SHUFFLES, seed=SEED):
    """Within-paragraph line-order shuffle null."""
    rng = np.random.default_rng(seed)
    para_features = {}
    for folio, line_token_lists in paragraphs.items():
        section = get_section(folio)
        features = []
        for tokens in line_token_lists:
            f = build_line_features(tokens, morph)
            if f is None:
                continue
            f_trans = transform_features(f, scheme, paragraph_id=folio, paragraph_means=paragraph_means,
                                         section_id=section, section_means=section_means)
            if f_trans is not None:
                features.append(f_trans)
        if len(features) >= 2:
            para_features[folio] = np.array(features)

    null_scores = []
    for trial in range(n_shuffles):
        trial_total = 0.0
        for folio, feats in para_features.items():
            perm = rng.permutation(len(feats))
            permuted = feats[perm]
            diffs = np.diff(permuted, axis=0)
            trial_total += float(np.sum(diffs ** 2))
        null_scores.append(trial_total)
    return np.array(null_scores)


def main():
    print("=" * 80)
    print("PHASE_716 COMPREHENSIVE MECHANISM SEARCH FOR C1727")
    print("=" * 80)

    print("\nAssembling Currier B paragraphs...")
    paragraphs, morph = assemble_paragraphs()
    print(f"  N paragraphs: {len(paragraphs)}")

    print("\nComputing paragraph and section means...")
    paragraph_means, section_means = compute_paragraph_and_section_means(paragraphs, morph)
    print(f"  N paragraph means: {len(paragraph_means)}")
    print(f"  N section means: {len(section_means)}  (sections: {list(section_means.keys())})")

    # All schemes to test
    schemes = [
        'baseline',
        'paragraph_mean_residualized',
        'section_mean_residualized',
        'head_only',
        'term_only',
        'length_only',
        'mode_only',
        'head_term_only',
        'no_head',
        'no_term',
        'no_length',
        'no_mode',
    ]

    print(f"\n{'Scheme':<32}{'observed':>12}{'null_mean':>12}{'null_std':>11}{'z':>9}{'p_emp':>9}{'collapse%':>12}")
    print("-" * 100)

    results = {}
    z_baseline = None
    for scheme in schemes:
        obs, n_pairs = compute_score(paragraphs, morph, scheme, paragraph_means, section_means)
        nulls = shuffle_null(paragraphs, morph, scheme, paragraph_means, section_means, n_shuffles=N_SHUFFLES)
        null_mean = float(nulls.mean())
        null_std = float(nulls.std())
        z = (obs - null_mean) / null_std if null_std > 0 else 0.0
        p_emp = float(np.mean(nulls <= obs))
        if scheme == 'baseline':
            z_baseline = z
            collapse = 0.0
        else:
            if z_baseline < 0 and z < 0:
                collapse = abs((z_baseline - z) / z_baseline * 100)
            elif z_baseline < 0:
                collapse = 100
            else:
                collapse = 0
        print(f"{scheme:<32}{obs:>12.1f}{null_mean:>12.1f}{null_std:>11.1f}{z:>+9.3f}{p_emp:>9.4f}{collapse:>11.1f}%")
        results[scheme] = {
            'observed': obs,
            'null_mean': null_mean,
            'null_std': null_std,
            'z_score': z,
            'p_empirical': p_emp,
            'n_pairs': n_pairs,
            'magnitude_collapse_vs_baseline_pct': collapse,
        }

    # ---- Analysis ----
    print("\n" + "=" * 80)
    print("MECHANISM ANALYSIS")
    print("=" * 80)

    print(f"\n  Baseline z (full 15-feature C1727 reproduction): {z_baseline:+.3f}")
    print(f"\n  ABLATION TESTS (remove feature subset, see if smoothness persists):")
    for s in ['no_head', 'no_term', 'no_mode', 'no_length']:
        z = results[s]['z_score']
        coll = results[s]['magnitude_collapse_vs_baseline_pct']
        print(f"    {s}: z={z:+.3f}, collapse={coll:.1f}%")

    print(f"\n  SUBSET TESTS (use only specific features):")
    for s in ['head_only', 'term_only', 'length_only', 'mode_only', 'head_term_only']:
        z = results[s]['z_score']
        coll = results[s]['magnitude_collapse_vs_baseline_pct']
        print(f"    {s}: z={z:+.3f}, collapse={coll:.1f}%")

    print(f"\n  RESIDUALIZATION TESTS:")
    for s in ['paragraph_mean_residualized', 'section_mean_residualized']:
        z = results[s]['z_score']
        coll = results[s]['magnitude_collapse_vs_baseline_pct']
        print(f"    {s}: z={z:+.3f}, collapse={coll:.1f}%")

    # Verdict
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    para_collapse = results['paragraph_mean_residualized']['magnitude_collapse_vs_baseline_pct']
    section_collapse = results['section_mean_residualized']['magnitude_collapse_vs_baseline_pct']

    if para_collapse >= 80:
        verdict = "PARAGRAPH COMPOSITIONAL HOMOGENEITY IS THE MECHANISM (paragraph-mean residualization collapses signal)"
    elif section_collapse >= 80:
        verdict = "SECTION COMPOSITIONAL HOMOGENEITY IS THE MECHANISM (section-mean residualization collapses signal)"
    elif para_collapse >= 50:
        verdict = "PARAGRAPH HOMOGENEITY PARTIAL MECHANISM"
    elif para_collapse >= 20:
        verdict = "PARAGRAPH HOMOGENEITY WEAK MECHANISM"
    else:
        verdict = "UNKNOWN MECHANISM — none of paragraph/section homogeneity collapses signal substantially"

    print(f"\n  VERDICT: {verdict}")

    # Identify which features carry the signal
    print(f"\n  Feature dimension where smoothness signal is strongest (subset z):")
    subset_z = {s: results[s]['z_score'] for s in ['head_only', 'term_only', 'length_only', 'mode_only']}
    ranked = sorted(subset_z.items(), key=lambda kv: kv[1])
    for s, z in ranked:
        print(f"    {s}: z={z:+.3f}")

    # Save
    out = {
        'method': 'PHASE_716 comprehensive mechanism search',
        'n_paragraphs': len(paragraphs),
        'n_shuffles': N_SHUFFLES,
        'baseline_z': z_baseline,
        'results_by_scheme': results,
        'verdict': verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

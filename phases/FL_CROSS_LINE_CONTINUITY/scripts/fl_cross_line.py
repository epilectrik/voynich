"""
Phase 353: FL Cross-Line Continuity Test

Tests whether FL stage at end of line N predicts FL stage at start of
line N+1 within paragraphs.

Key question: Do paragraphs have internal FL state tracking across lines,
or do lines sample FL independently (as predicted by C670/C681)?

Predictions:
  STATE CONTINUITY: Cross-line stage gap is small (line N+1 continues from N)
  LINE INDEPENDENCE (C681): Cross-line stage gap is large and negative
    (each line resets to INITIAL regardless of previous line's terminal state)

Inputs:
  C777: FL MIDDLE stage classification (17 MIDDLEs, 6 stages)
  C786: Within-line FL->FL transitions (27% forward, 68% same, 5% backward)
  C670: No adjacent-line vocabulary coupling
  C681: Sequential coupling is folio-mediated, not line-to-line
  C905: Cross-folio FL chaining falsified
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# FL MIDDLE STAGE DEFINITIONS (C777)
# ============================================================

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0),   'i': ('INITIAL', 0),
    'in': ('EARLY', 1),
    'r': ('MEDIAL', 2),     'ar': ('MEDIAL', 2),
    'al': ('LATE', 3),      'l': ('LATE', 3),      'ol': ('LATE', 3),
    'o': ('FINAL', 4),      'ly': ('FINAL', 4),    'am': ('FINAL', 4),
    'm': ('TERMINAL', 5),   'dy': ('TERMINAL', 5), 'ry': ('TERMINAL', 5), 'y': ('TERMINAL', 5)
}
FL_MIDDLES = set(FL_STAGE_MAP.keys())
STAGE_NAMES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

# Gallows characters for paragraph boundary detection (C827)
GALLOWS = {'k', 't', 'p', 'f'}

# ============================================================
# LOAD DATA
# ============================================================

print("Loading data...")
tx = Transcript()
morph = Morphology()

# Load class map for FLOW_OPERATOR role identification
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']
FL_CLASSES = {7, 30, 38, 40}

# Build per-folio, per-line token data
folio_lines = defaultdict(lambda: defaultdict(list))

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    mid = m.middle

    # Broad FL: any token with FL MIDDLE (~25% of tokens)
    is_fl_broad = mid in FL_MIDDLES

    # Narrow FL: FLOW_OPERATOR role only (4.7% of tokens)
    cls = int(token_to_class[w]) if w in token_to_class else None
    is_fl_narrow = cls in FL_CLASSES if cls is not None else False

    stage_name, stage_idx = FL_STAGE_MAP.get(mid, (None, None))

    folio_lines[token.folio][token.line].append({
        'word': w,
        'middle': mid,
        'is_fl_broad': is_fl_broad,
        'is_fl_narrow': is_fl_narrow,
        'fl_stage_name': stage_name,
        'fl_stage_idx': stage_idx,
    })

print(f"Loaded {len(folio_lines)} folios")


# ============================================================
# PARAGRAPH DETECTION
# ============================================================

def get_paragraphs(lines_dict):
    """Group lines into paragraphs by gallows-initial detection (C827)."""
    sorted_lines = sorted(lines_dict.items(), key=lambda x: str(x[0]))
    paragraphs = []
    current = []

    for line_id, tokens in sorted_lines:
        if not tokens:
            continue
        first_char = tokens[0]['word'][0] if tokens[0]['word'] else ''
        is_gallows = first_char in GALLOWS

        if is_gallows and current:
            paragraphs.append(current)
            current = [(line_id, tokens)]
        else:
            current.append((line_id, tokens))

    if current:
        paragraphs.append(current)

    return paragraphs


def get_line_fl_info(tokens, use_broad=True):
    """Extract FL stage information from a line's tokens."""
    fl_key = 'is_fl_broad' if use_broad else 'is_fl_narrow'
    fl_tokens = [t for t in tokens if t[fl_key] and t['fl_stage_idx'] is not None]

    if not fl_tokens:
        return None

    stages = [t['fl_stage_idx'] for t in fl_tokens]
    return {
        'count': len(fl_tokens),
        'first_stage': fl_tokens[0]['fl_stage_idx'],
        'last_stage': fl_tokens[-1]['fl_stage_idx'],
        'first_middle': fl_tokens[0]['middle'],
        'last_middle': fl_tokens[-1]['middle'],
        'mean_stage': float(np.mean(stages)),
        'stages': stages
    }


# ============================================================
# COLLECT CROSS-LINE PAIRS
# ============================================================

print("\nCollecting cross-line FL pairs...")

cross_line_pairs = {'broad': [], 'narrow': []}

for folio, lines_dict in folio_lines.items():
    paragraphs = get_paragraphs(lines_dict)

    for para_idx, para in enumerate(paragraphs):
        if len(para) < 2:
            continue

        para_key = f"{folio}_P{para_idx}"

        for method, use_broad in [('broad', True), ('narrow', False)]:
            # Check every strictly adjacent line pair in the paragraph
            for i in range(len(para) - 1):
                line_id_n, tokens_n = para[i]
                line_id_n1, tokens_n1 = para[i + 1]

                info_n = get_line_fl_info(tokens_n, use_broad=use_broad)
                info_n1 = get_line_fl_info(tokens_n1, use_broad=use_broad)

                if info_n and info_n1:
                    cross_line_pairs[method].append({
                        'folio': folio,
                        'para': para_key,
                        'line_n_last_stage': info_n['last_stage'],
                        'line_n1_first_stage': info_n1['first_stage'],
                        'line_n_mean_stage': info_n['mean_stage'],
                        'line_n1_mean_stage': info_n1['mean_stage'],
                        'line_n_last_middle': info_n['last_middle'],
                        'line_n1_first_middle': info_n1['first_middle'],
                    })


# ============================================================
# ANALYSIS
# ============================================================

results = {}

for method in ['broad', 'narrow']:
    pairs = cross_line_pairs[method]
    n = len(pairs)

    print(f"\n{'=' * 60}")
    label = 'ALL FL MIDDLEs (~25% of tokens)' if method == 'broad' else 'FLOW_OPERATOR role (4.7%)'
    print(f"METHOD: {label}")
    print(f"{'=' * 60}")
    print(f"Adjacent line pairs with FL on both: {n}")

    if n < 20:
        print("  INSUFFICIENT DATA")
        results[method] = {'n_pairs': n, 'verdict': 'INSUFFICIENT_DATA'}
        continue

    last_stages = np.array([p['line_n_last_stage'] for p in pairs])
    first_stages = np.array([p['line_n1_first_stage'] for p in pairs])
    mean_n = np.array([p['line_n_mean_stage'] for p in pairs])
    mean_n1 = np.array([p['line_n1_mean_stage'] for p in pairs])

    # --- Test A: Cross-line stage gap ---
    gaps = first_stages - last_stages
    mean_gap = float(np.mean(gaps))
    std_gap = float(np.std(gaps))

    print(f"\nA) Cross-line stage gap (first_N+1 - last_N):")
    print(f"   Mean gap: {mean_gap:.3f} +/- {std_gap:.3f}")
    print(f"   (Negative = reset toward INITIAL; ~0 = continuity)")

    # --- Test B: Endpoint correlation ---
    rho_ep, p_ep = stats.spearmanr(last_stages, first_stages)

    print(f"\nB) Endpoint stage correlation (last_N vs first_N+1):")
    print(f"   Spearman rho = {rho_ep:.4f}, p = {p_ep:.4f}")

    # --- Test C: Mean stage correlation ---
    rho_mean, p_mean = stats.spearmanr(mean_n, mean_n1)

    print(f"\nC) Mean stage correlation (mean_N vs mean_N+1):")
    print(f"   Spearman rho = {rho_mean:.4f}, p = {p_mean:.4f}")

    # --- Test D: Forward/same/backward proportions ---
    forward = int(np.sum(gaps > 0))
    same = int(np.sum(gaps == 0))
    backward = int(np.sum(gaps < 0))

    print(f"\nD) Cross-line transition direction (last_N -> first_N+1):")
    print(f"   Forward:  {100 * forward / n:.1f}% ({forward}/{n})")
    print(f"   Same:     {100 * same / n:.1f}% ({same}/{n})")
    print(f"   Backward: {100 * backward / n:.1f}% ({backward}/{n})")
    print(f"   [Within-line C786: 27.3% forward, 68.2% same, 4.5% backward]")

    # --- Test E: Permutation null ---
    np.random.seed(42)
    n_perms = 10000
    null_rhos_ep = []
    null_rhos_mean = []
    null_mean_gaps = []

    for _ in range(n_perms):
        shuf_first = np.random.permutation(first_stages)
        r, _ = stats.spearmanr(last_stages, shuf_first)
        null_rhos_ep.append(r)
        null_mean_gaps.append(float(np.mean(shuf_first - last_stages)))

        shuf_mean_n1 = np.random.permutation(mean_n1)
        r2, _ = stats.spearmanr(mean_n, shuf_mean_n1)
        null_rhos_mean.append(r2)

    perm_p_ep = float(np.mean(np.abs(null_rhos_ep) >= np.abs(rho_ep)))
    perm_p_mean = float(np.mean(np.abs(null_rhos_mean) >= np.abs(rho_mean)))
    null_gap_mean = float(np.mean(null_mean_gaps))

    print(f"\nE) Permutation test (N={n_perms}):")
    print(f"   Endpoint rho: observed={rho_ep:.4f}, p_perm={perm_p_ep:.4f}")
    print(f"   Mean-stage rho: observed={rho_mean:.4f}, p_perm={perm_p_mean:.4f}")
    print(f"   Gap null mean: {null_gap_mean:.3f} (observed: {mean_gap:.3f})")

    # --- Test F: Transition matrix ---
    trans_matrix = Counter()
    for p in pairs:
        trans_matrix[(p['line_n_last_stage'], p['line_n1_first_stage'])] += 1

    # Chi-squared independence
    last_dist = Counter(int(s) for s in last_stages)
    first_dist = Counter(int(s) for s in first_stages)
    observed_stages_last = sorted(last_dist.keys())
    observed_stages_first = sorted(first_dist.keys())

    if len(observed_stages_last) > 1 and len(observed_stages_first) > 1:
        chi2_val = 0
        for s1 in observed_stages_last:
            for s2 in observed_stages_first:
                obs = trans_matrix.get((s1, s2), 0)
                exp = (last_dist[s1] * first_dist[s2]) / n
                if exp > 0:
                    chi2_val += (obs - exp) ** 2 / exp
        chi2_df = (len(observed_stages_last) - 1) * (len(observed_stages_first) - 1)
        chi2_p = float(1 - stats.chi2.cdf(chi2_val, chi2_df))
    else:
        chi2_val, chi2_df, chi2_p = 0.0, 0, 1.0

    print(f"\nF) Chi-squared independence of transition matrix:")
    print(f"   chi2 = {chi2_val:.2f}, df = {chi2_df}, p = {chi2_p:.4f}")

    # --- Test G: Marginal distributions ---
    print(f"\nG) Marginal stage distributions:")
    print(f"   Last FL on line N:")
    for s in range(6):
        ct = last_dist.get(s, 0)
        if ct > 0:
            print(f"     {STAGE_NAMES[s]}: {ct} ({100 * ct / n:.1f}%)")
    print(f"   First FL on line N+1:")
    for s in range(6):
        ct = first_dist.get(s, 0)
        if ct > 0:
            print(f"     {STAGE_NAMES[s]}: {ct} ({100 * ct / n:.1f}%)")

    # --- Top transitions ---
    print(f"\n   Top cross-line transitions:")
    for (s1, s2), c in trans_matrix.most_common(10):
        direction = "FORWARD" if s2 > s1 else ("SAME" if s2 == s1 else "BACKWARD")
        print(f"     {STAGE_NAMES[s1]} -> {STAGE_NAMES[s2]}: {c} ({100 * c / n:.1f}%) [{direction}]")

    # --- Store results ---
    results[method] = {
        'n_pairs': n,
        'cross_line_gap': {
            'mean': mean_gap,
            'std': std_gap,
            'null_mean': null_gap_mean
        },
        'endpoint_correlation': {
            'rho': float(rho_ep),
            'p_parametric': float(p_ep),
            'p_permutation': perm_p_ep
        },
        'mean_stage_correlation': {
            'rho': float(rho_mean),
            'p_parametric': float(p_mean),
            'p_permutation': perm_p_mean
        },
        'transition_proportions': {
            'forward': forward, 'same': same, 'backward': backward,
            'forward_pct': float(100 * forward / n),
            'same_pct': float(100 * same / n),
            'backward_pct': float(100 * backward / n)
        },
        'within_line_comparison_c786': {
            'within_forward_pct': 27.3,
            'within_same_pct': 68.2,
            'within_backward_pct': 4.5
        },
        'chi2_independence': {
            'chi2': float(chi2_val), 'df': chi2_df, 'p': chi2_p
        },
        'marginal_distributions': {
            'last_stage': {STAGE_NAMES[k]: v for k, v in sorted(last_dist.items())},
            'first_stage': {STAGE_NAMES[k]: v for k, v in sorted(first_dist.items())}
        },
        'transition_matrix_top': [
            {'from': STAGE_NAMES[s1], 'to': STAGE_NAMES[s2], 'count': c}
            for (s1, s2), c in trans_matrix.most_common(20)
        ]
    }


# ============================================================
# OVERALL VERDICT
# ============================================================

print("\n" + "=" * 70)
print("OVERALL VERDICT")
print("=" * 70)

broad = results.get('broad', {})
if broad.get('verdict') == 'INSUFFICIENT_DATA':
    verdict = 'INSUFFICIENT_DATA'
    explanation = 'Not enough cross-line FL pairs to test.'
else:
    ep = broad['endpoint_correlation']
    ms = broad['mean_stage_correlation']
    chi = broad['chi2_independence']

    sig_tests = {
        'endpoint_rho': ep['p_permutation'] < 0.05,
        'mean_stage_rho': ms['p_permutation'] < 0.05,
        'chi2': chi['p'] < 0.05
    }
    sig_count = sum(sig_tests.values())

    print(f"\nSignificance summary (alpha=0.05):")
    for test, sig in sig_tests.items():
        print(f"  {test}: {'SIGNIFICANT' if sig else 'not significant'}")

    # Check effect sizes
    ep_rho = abs(ep['rho'])
    ms_rho = abs(ms['rho'])

    if sig_count == 0:
        verdict = 'FL_CROSS_LINE_INDEPENDENT'
        explanation = ('No significant cross-line FL stage correlation detected. '
                       'Lines sample FL stages independently, consistent with C670/C681.')
    elif sig_count == 1 and ep_rho < 0.1 and ms_rho < 0.1:
        verdict = 'FL_CROSS_LINE_INDEPENDENT'
        explanation = ('At most marginal significance with negligible effect size. '
                       'Consistent with folio-mediated coupling (C681), not state tracking.')
    elif sig_count <= 2 and ep_rho < 0.15:
        verdict = 'FL_CROSS_LINE_WEAK'
        explanation = ('Weak cross-line FL correlation, likely folio-mediated (C681). '
                       'No evidence of paragraph-level state tracking beyond shared folio context.')
    else:
        verdict = 'FL_CROSS_LINE_COUPLED'
        explanation = ('Significant cross-line FL stage correlation detected. '
                       'Paragraphs may have internal state tracking beyond folio-level context.')

    # Additional: compare with within-line (C786)
    tp = broad['transition_proportions']
    within_same = 68.2
    cross_same = tp['same_pct']
    print(f"\n  Cross-line SAME rate: {cross_same:.1f}% vs within-line: {within_same:.1f}%")
    if cross_same < within_same / 2:
        print("  -> Cross-line coherence much weaker than within-line (expected for independent lines)")

print(f"\nVERDICT: {verdict}")
print(f"{explanation}")

results['verdict'] = verdict
results['explanation'] = explanation

# Save
out_path = PROJECT_ROOT / 'phases' / 'FL_CROSS_LINE_CONTINUITY' / 'results' / 'fl_cross_line.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=float)

print(f"\nResults saved to {out_path}")

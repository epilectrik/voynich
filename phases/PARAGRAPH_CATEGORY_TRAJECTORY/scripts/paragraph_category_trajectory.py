"""
Phase 591: PARAGRAPH_CATEGORY_TRAJECTORY

Tests whether the 8-category fraction vector (C1250) shows systematic
trajectory across paragraph body line positions.

C963 established body homogeneity at role-fraction level. C1295 extended
this to thermal/category grain for termination prediction. Neither tested
whether categories drift, oscillate, or remain static across body positions.

Tests:
  T1: Raw category trajectory (quintile × 8-category, Spearman rho)
  T2: Length-controlled trajectory (partial Spearman, pooled + within-section) [DECISIVE]
  T3: Within- vs between-paragraph JSD (extends C1288 to body-line resolution)
  T4: Serial dependence via lag-k autocorrelation on category PCA
  T5: Category × suffix mode interaction
  T6: Kernel-mediated category shift (partial correlation controlling kernel fractions)

Controls: within-paragraph shuffle, length stratification, section stratification, folio shuffle

Provenance: C963, C1295, C1229, C1429, C965, C1250, C1288
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon

sys.path.insert(0, str(Path("C:/git/voynich").resolve()))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

PROJECT_ROOT = Path("C:/git/voynich").resolve()
RESULTS_PATH = PROJECT_ROOT / "phases/PARAGRAPH_CATEGORY_TRAJECTORY/results/paragraph_category_trajectory_results.json"

CATEGORIES = ['THERMAL', 'FLOW', 'TRANSITION', 'OPERATION', 'STAGING',
              'CONTAINMENT', 'MARKING', 'MONITORING']
N_CATS = len(CATEGORIES)
BONFERRONI_ALPHA = 0.05 / N_CATS  # 0.00625
N_SHUFFLE = 100
RNG = np.random.RandomState(42)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def assign_quintile(body_idx, n_body):
    """Assign a body line (0-indexed) to a quintile (0-4)."""
    if n_body <= 1:
        return 0
    return min(int((body_idx / (n_body - 1)) * 5), 4)


def partial_spearman(x, y, covariates):
    """Partial Spearman: rho(x, y | covariates) via residualization."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # Regress out covariates from both x and y
    x_resid = x.copy()
    y_resid = y.copy()
    for cov in covariates:
        cov = np.asarray(cov, dtype=float)
        # Skip constant covariates (no variance to regress out)
        if np.std(cov) < 1e-10:
            continue
        # Regress cov out of x_resid
        slope, intercept, _, _, _ = stats.linregress(cov, x_resid)
        x_resid = x_resid - (slope * cov + intercept)
        # Regress cov out of y_resid
        slope, intercept, _, _, _ = stats.linregress(cov, y_resid)
        y_resid = y_resid - (slope * cov + intercept)
    rho, p = stats.spearmanr(x_resid, y_resid)
    return float(rho), float(p)


def jsd_vectors(p, q):
    """JSD between two probability vectors (handle zeros)."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    # Ensure proper distributions
    p_sum, q_sum = p.sum(), q.sum()
    if p_sum == 0 or q_sum == 0:
        return float('nan')
    p = p / p_sum
    q = q / q_sum
    return float(jensenshannon(p, q) ** 2)  # squared JSD


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

# Build lines: (folio, line) -> [Token, ...]
lines_dict = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace("*", "").strip()
    if not word:
        continue
    lines_dict[(t.folio, t.line)].append(t)

# Build paragraphs using par_initial field
folio_lines = defaultdict(list)
for (f, l), toks in sorted(lines_dict.items()):
    folio_lines[f].append((l, toks))

all_paragraphs = []
for f in sorted(folio_lines):
    curr_par = []
    for l, toks in folio_lines[f]:
        if toks[0].par_initial and curr_par:
            all_paragraphs.append(curr_par)
            curr_par = []
        curr_par.append((f, l, toks))
    if curr_par:
        all_paragraphs.append(curr_par)

print(f"Total paragraphs: {len(all_paragraphs)}")

# Filter: gallows-initial only, 6+ total lines (5+ body lines)
GALLOWS = {'k', 't', 'p', 'f'}

def is_gallows_initial(toks):
    """Check if first token starts with a gallows character."""
    if not toks:
        return False
    word = toks[0].word.replace("*", "").strip()
    return word[:1] in GALLOWS if word else False

selected = []
excluded_non_gallows = 0
excluded_short = 0
for par in all_paragraphs:
    if not is_gallows_initial(par[0][2]):
        excluded_non_gallows += 1
        continue
    if len(par) < 6:  # need 5+ body lines
        excluded_short += 1
        continue
    selected.append(par)

print(f"Gallows-initial paragraphs with 6+ lines: {len(selected)}")
print(f"  Excluded (not gallows-initial): {excluded_non_gallows}")
print(f"  Excluded (too short): {excluded_short}")

# Section distribution of selected paragraphs
section_counts = Counter()
for par in selected:
    sec = par[0][2][0].section  # section of first token
    section_counts[sec] += 1
print(f"  Section distribution: {dict(section_counts)}")


# ---------------------------------------------------------------------------
# BUILD PER-BODY-LINE FEATURE MATRIX
# ---------------------------------------------------------------------------
print("\nBuilding per-body-line feature matrix...")

body_data = []  # list of dicts with all features per body line

for par_idx, par in enumerate(selected):
    folio = par[0][0]
    section = par[0][2][0].section
    body_lines = par[1:]  # skip header
    n_body = len(body_lines)

    for body_idx, (f, line_num, toks) in enumerate(body_lines):
        # Category fraction vector
        cat_counts = Counter()
        kernel_counts = Counter()
        n_tokens = 0
        bare_count = 0
        terminal_count = 0

        for tok in toks:
            word = tok.word.replace("*", "").strip()
            if not word:
                continue
            m = morph.extract(word)
            if not m.middle:
                continue
            n_tokens += 1

            # Category
            cat = cc.classify(m.middle)
            if cat:
                cat_counts[cat] += 1

            # Kernel
            if m.prefix in ('ch', 'sh'):
                kernel_counts['h'] += 1
            elif m.prefix in ('k',):
                kernel_counts['k'] += 1
            elif m.prefix in ('qo', 'o'):
                # qo is PREFIX, not kernel
                pass
            elif m.prefix is None:
                kernel_counts['headless'] += 1
            # e-kernel: tokens with e-HEAD (prefix starting with e or plain e)
            # Actually: kernel = HEAD atom. k-HEAD, h-HEAD (ch/sh), e-HEAD
            # Let's use the articulator/prefix properly
            # k-HEAD: prefix starts with k (but not ch/sh)
            # h-HEAD: prefix is ch or sh
            # e-HEAD: no prefix and middle starts with e, OR prefix is e-based
            # headless: no prefix at all
            # This is simplified - use the actual head classification

            # Suffix mode (C1229: A=spec/energy, B=continuation/bare)
            if m.suffix:
                # Check if terminal suffix
                if m.suffix in ('y', 'dy', 'hy', 'ly', 'ry',
                                'ey', 'edy', 'eey',
                                'am', 'om', 'em', 'im',
                                'in', 'an', 'on', 'en',
                                'al', 'ar', 'el', 'er', 'ol', 'or',
                                'eeol', 'eol', 'ool'):
                    terminal_count += 1
                else:
                    bare_count += 1
            else:
                bare_count += 1

        if n_tokens == 0:
            continue

        # Category fraction vector
        cat_vec = np.zeros(N_CATS)
        for i, cat_name in enumerate(CATEGORIES):
            cat_vec[i] = cat_counts.get(cat_name, 0) / n_tokens

        # Kernel fractions - simplified: use HEAD classification
        # k-HEAD: first char of word is k (and not followed by ch/sh pattern)
        # h-HEAD: prefix ch or sh
        # e-HEAD: prefix-less token where middle starts with e
        # headless: everything else with no prefix
        k_frac = kernel_counts.get('k', 0) / n_tokens
        h_frac = kernel_counts.get('h', 0) / n_tokens
        headless_frac = kernel_counts.get('headless', 0) / n_tokens
        # e-HEAD is complex - approximate as tokens with e-starting middles
        e_count = sum(1 for tok in toks
                      if tok.word.replace("*", "").strip()
                      and morph.extract(tok.word.replace("*", "").strip()).middle
                      and morph.extract(tok.word.replace("*", "").strip()).prefix is None
                      and morph.extract(tok.word.replace("*", "").strip()).middle.startswith('e'))
        e_frac = e_count / n_tokens

        # Suffix mode
        total_sfx = bare_count + terminal_count
        bare_frac = bare_count / total_sfx if total_sfx > 0 else 0.5
        suffix_mode = 'B' if bare_frac > 0.5 else 'A'

        norm_pos = body_idx / (n_body - 1) if n_body > 1 else 0.0
        quintile = assign_quintile(body_idx, n_body)

        body_data.append({
            'par_idx': par_idx,
            'folio': folio,
            'section': section,
            'body_idx': body_idx,
            'norm_pos': norm_pos,
            'quintile': quintile,
            'n_tokens': n_tokens,
            'cat_vec': cat_vec,
            'k_frac': k_frac,
            'h_frac': h_frac,
            'e_frac': e_frac,
            'headless_frac': headless_frac,
            'suffix_mode': suffix_mode,
            'bare_frac': bare_frac,
        })

print(f"Total body lines with data: {len(body_data)}")

# Convert to arrays for vectorized computation
positions = np.array([d['norm_pos'] for d in body_data])
quintiles = np.array([d['quintile'] for d in body_data])
n_tokens_arr = np.array([d['n_tokens'] for d in body_data], dtype=float)
cat_matrix = np.array([d['cat_vec'] for d in body_data])  # (N, 8)
par_ids = np.array([d['par_idx'] for d in body_data])
sections = np.array([d['section'] for d in body_data])
k_fracs = np.array([d['k_frac'] for d in body_data])
h_fracs = np.array([d['h_frac'] for d in body_data])
e_fracs = np.array([d['e_frac'] for d in body_data])
headless_fracs = np.array([d['headless_frac'] for d in body_data])
suffix_modes = np.array([d['suffix_mode'] for d in body_data])

N = len(body_data)
print(f"Feature matrix: {N} lines × {N_CATS} categories")


# ===========================================================================
# T1: RAW CATEGORY TRAJECTORY
# ===========================================================================
print("\n" + "=" * 60)
print("T1: Raw Category Trajectory")
print("=" * 60)

t1_results = {}
# Quintile means
quintile_means = np.zeros((5, N_CATS))
quintile_counts = np.zeros(5)
for q in range(5):
    mask = quintiles == q
    quintile_counts[q] = mask.sum()
    if mask.sum() > 0:
        quintile_means[q] = cat_matrix[mask].mean(axis=0)

t1_results['quintile_means'] = {
    f"Q{q}": {cat: round(float(quintile_means[q, i]), 6) for i, cat in enumerate(CATEGORIES)}
    for q in range(5)
}
t1_results['quintile_counts'] = {f"Q{q}": int(quintile_counts[q]) for q in range(5)}

# Spearman rho per category
t1_rhos = {}
for i, cat in enumerate(CATEGORIES):
    rho, p = stats.spearmanr(positions, cat_matrix[:, i])
    sig = "***" if p < BONFERRONI_ALPHA else ""
    t1_rhos[cat] = {'rho': round(float(rho), 6), 'p': float(p), 'significant': p < BONFERRONI_ALPHA}
    print(f"  {cat:14s}: rho={rho:+.4f}  p={p:.4e} {sig}")

t1_results['spearman_raw'] = t1_rhos
t1_n_sig = sum(1 for v in t1_rhos.values() if v['significant'])
print(f"  Significant (Bonferroni {BONFERRONI_ALPHA:.4f}): {t1_n_sig}/{N_CATS}")
t1_results['n_significant'] = t1_n_sig


# ===========================================================================
# T2: LENGTH-CONTROLLED CATEGORY TRAJECTORY (DECISIVE)
# ===========================================================================
print("\n" + "=" * 60)
print("T2: Length-Controlled Category Trajectory (DECISIVE)")
print("=" * 60)

t2_results = {'pooled': {}, 'within_section': {}}

# Pooled: partial Spearman controlling for n_tokens
print("\n  --- POOLED ---")
for i, cat in enumerate(CATEGORIES):
    rho, p = partial_spearman(positions, cat_matrix[:, i], [n_tokens_arr])
    sig = "***" if p < BONFERRONI_ALPHA else ""
    t2_results['pooled'][cat] = {'rho': round(float(rho), 6), 'p': float(p),
                                  'significant': p < BONFERRONI_ALPHA}
    print(f"  {cat:14s}: partial_rho={rho:+.4f}  p={p:.4e} {sig}")

t2_pooled_n_sig = sum(1 for v in t2_results['pooled'].values() if v['significant'])
print(f"  Pooled significant: {t2_pooled_n_sig}/{N_CATS}")

# Within-section: run T2 per section (only sections with enough data)
print("\n  --- WITHIN-SECTION ---")
unique_sections = sorted(set(sections))
for sec in unique_sections:
    sec_mask = sections == sec
    n_sec = sec_mask.sum()
    if n_sec < 30:
        print(f"  Section {sec}: N={n_sec} (too few, skipping)")
        t2_results['within_section'][sec] = {'n': int(n_sec), 'skipped': True}
        continue
    print(f"  Section {sec}: N={n_sec}")
    sec_results = {'n': int(n_sec), 'skipped': False, 'categories': {}}
    for i, cat in enumerate(CATEGORIES):
        rho, p = partial_spearman(
            positions[sec_mask], cat_matrix[sec_mask, i], [n_tokens_arr[sec_mask]])
        sig = "***" if p < BONFERRONI_ALPHA else ""
        sec_results['categories'][cat] = {
            'rho': round(float(rho), 6), 'p': float(p),
            'significant': p < BONFERRONI_ALPHA
        }
        if sig:
            print(f"    {cat:14s}: partial_rho={rho:+.4f}  p={p:.4e} {sig}")
    sec_n_sig = sum(1 for v in sec_results['categories'].values() if v['significant'])
    sec_results['n_significant'] = sec_n_sig
    if sec_n_sig == 0:
        print(f"    (no significant categories)")
    t2_results['within_section'][sec] = sec_results

# Check: any pooled-significant category that vanishes within-section?
t2_results['section_artifact_check'] = {}
for cat in CATEGORIES:
    if t2_results['pooled'][cat]['significant']:
        # Check if ANY section confirms it
        confirmed = False
        for sec in unique_sections:
            if sec in t2_results['within_section'] and not t2_results['within_section'][sec].get('skipped'):
                if t2_results['within_section'][sec]['categories'].get(cat, {}).get('significant', False):
                    confirmed = True
                    break
        t2_results['section_artifact_check'][cat] = {
            'pooled_sig': True, 'within_section_confirmed': confirmed
        }


# ===========================================================================
# T3: WITHIN- vs BETWEEN-PARAGRAPH CATEGORY JSD
# ===========================================================================
print("\n" + "=" * 60)
print("T3: Within- vs Between-Paragraph Category JSD")
print("=" * 60)

# Organize body lines by paragraph and folio
par_to_lines = defaultdict(list)
folio_to_lines = defaultdict(list)
for idx, d in enumerate(body_data):
    par_to_lines[d['par_idx']].append(idx)
    folio_to_lines[d['folio']].append(idx)

# Within-paragraph JSD
within_jsds = []
for par_idx, idxs in par_to_lines.items():
    if len(idxs) < 2:
        continue
    for i, j in combinations(idxs, 2):
        jsd = jsd_vectors(cat_matrix[i], cat_matrix[j])
        if not np.isnan(jsd):
            within_jsds.append(jsd)

# Between-paragraph-same-folio JSD (sample to keep tractable)
between_same_folio_jsds = []
for folio, idxs in folio_to_lines.items():
    # Group by paragraph
    par_groups = defaultdict(list)
    for idx in idxs:
        par_groups[body_data[idx]['par_idx']].append(idx)
    par_keys = list(par_groups.keys())
    if len(par_keys) < 2:
        continue
    # Sample pairs from different paragraphs (max 500 per folio)
    count = 0
    for pi, pj in combinations(par_keys, 2):
        for li in par_groups[pi][:3]:  # limit per paragraph
            for lj in par_groups[pj][:3]:
                jsd = jsd_vectors(cat_matrix[li], cat_matrix[lj])
                if not np.isnan(jsd):
                    between_same_folio_jsds.append(jsd)
                    count += 1
                if count > 500:
                    break
            if count > 500:
                break
        if count > 500:
            break

# Cross-folio JSD (sample ~5000 pairs)
cross_folio_jsds = []
all_folios = list(folio_to_lines.keys())
max_cross = 5000
cross_count = 0
for _ in range(max_cross * 3):  # oversample to account for same-folio rejection
    fi, fj = RNG.choice(len(all_folios), 2, replace=False)
    f1, f2 = all_folios[fi], all_folios[fj]
    i1 = RNG.choice(folio_to_lines[f1])
    i2 = RNG.choice(folio_to_lines[f2])
    jsd = jsd_vectors(cat_matrix[i1], cat_matrix[i2])
    if not np.isnan(jsd):
        cross_folio_jsds.append(jsd)
        cross_count += 1
    if cross_count >= max_cross:
        break

within_mean = float(np.mean(within_jsds)) if within_jsds else float('nan')
between_mean = float(np.mean(between_same_folio_jsds)) if between_same_folio_jsds else float('nan')
cross_mean = float(np.mean(cross_folio_jsds)) if cross_folio_jsds else float('nan')

# Ratio: within / between-same-folio
if between_mean > 0:
    within_between_ratio = within_mean / between_mean
else:
    within_between_ratio = float('nan')

print(f"  Within-paragraph JSD:           {within_mean:.6f}  (N={len(within_jsds)})")
print(f"  Between-paragraph-same-folio:   {between_mean:.6f}  (N={len(between_same_folio_jsds)})")
print(f"  Cross-folio JSD:                {cross_mean:.6f}  (N={len(cross_folio_jsds)})")
print(f"  Within/Between ratio:           {within_between_ratio:.4f}")

# Mann-Whitney: within vs between-same-folio
if len(within_jsds) > 10 and len(between_same_folio_jsds) > 10:
    mw_stat, mw_p = stats.mannwhitneyu(within_jsds, between_same_folio_jsds, alternative='less')
    print(f"  Mann-Whitney (within < between): U={mw_stat:.0f}  p={mw_p:.4e}")
else:
    mw_stat, mw_p = float('nan'), float('nan')

t3_results = {
    'within_paragraph': {'mean': within_mean, 'n': len(within_jsds),
                         'std': float(np.std(within_jsds)) if within_jsds else float('nan')},
    'between_same_folio': {'mean': between_mean, 'n': len(between_same_folio_jsds),
                           'std': float(np.std(between_same_folio_jsds)) if between_same_folio_jsds else float('nan')},
    'cross_folio': {'mean': cross_mean, 'n': len(cross_folio_jsds),
                    'std': float(np.std(cross_folio_jsds)) if cross_folio_jsds else float('nan')},
    'within_between_ratio': round(within_between_ratio, 6),
    'mann_whitney': {'U': float(mw_stat), 'p': float(mw_p)},
}

# Folio shuffle control for T3
print("\n  Folio shuffle control (100 permutations)...")
shuffle_within_means = []
for _ in range(N_SHUFFLE):
    # Shuffle paragraph assignments within each folio
    shuffled_par = par_ids.copy()
    for folio, idxs in folio_to_lines.items():
        perm = RNG.permutation(len(idxs))
        shuffled_par[np.array(idxs)] = par_ids[np.array(idxs)[perm]]

    # Recompute within-paragraph JSD with shuffled assignments
    shuf_par_to_lines = defaultdict(list)
    for idx in range(N):
        shuf_par_to_lines[int(shuffled_par[idx])].append(idx)
    shuf_jsds = []
    for pidx, sidxs in shuf_par_to_lines.items():
        if len(sidxs) < 2:
            continue
        for i, j in combinations(sidxs[:10], 2):  # cap per paragraph
            jsd = jsd_vectors(cat_matrix[i], cat_matrix[j])
            if not np.isnan(jsd):
                shuf_jsds.append(jsd)
    if shuf_jsds:
        shuffle_within_means.append(float(np.mean(shuf_jsds)))

if shuffle_within_means:
    folio_shuffle_mean = float(np.mean(shuffle_within_means))
    folio_shuffle_p = float(np.mean([1 if s <= within_mean else 0 for s in shuffle_within_means]))
    print(f"  Folio shuffle null JSD mean: {folio_shuffle_mean:.6f}")
    print(f"  Observed within < null fraction: {folio_shuffle_p:.3f}")
    t3_results['folio_shuffle'] = {
        'null_mean': folio_shuffle_mean,
        'observed_less_than_null_frac': folio_shuffle_p,
    }


# ===========================================================================
# T4: SERIAL DEPENDENCE VIA LAG-K AUTOCORRELATION
# ===========================================================================
print("\n" + "=" * 60)
print("T4: Serial Dependence via Lag-k Autocorrelation")
print("=" * 60)

# PCA on category matrix
cat_centered = cat_matrix - cat_matrix.mean(axis=0)
try:
    U, S, Vt = np.linalg.svd(cat_centered, full_matrices=False)
    pc_scores = cat_centered @ Vt[:2].T  # project onto first 2 PCs
    variance_explained = (S[:2] ** 2) / (S ** 2).sum()
    print(f"  PC1 variance: {variance_explained[0]:.3f}, PC2 variance: {variance_explained[1]:.3f}")
except Exception as e:
    print(f"  PCA failed: {e}")
    pc_scores = cat_matrix[:, :2]  # fallback
    variance_explained = np.array([0.0, 0.0])

# Compute within-paragraph lag-k autocorrelation for PC1 and PC2
def compute_lag_autocorrelation(scores, par_ids_arr, max_lag=3):
    """Compute mean lag-k autocorrelation within paragraphs."""
    results = {}
    unique_pars = np.unique(par_ids_arr)
    for lag in range(1, max_lag + 1):
        corrs = []
        for pid in unique_pars:
            mask = par_ids_arr == pid
            vals = scores[mask]
            if len(vals) <= lag:
                continue
            # Pearson correlation between vals[:-lag] and vals[lag:]
            x = vals[:-lag]
            y = vals[lag:]
            if len(x) < 3:
                continue
            if np.std(x) == 0 or np.std(y) == 0:
                continue
            r, _ = stats.pearsonr(x, y)
            if not np.isnan(r):
                corrs.append(r)
        if corrs:
            results[lag] = {
                'mean': float(np.mean(corrs)),
                'std': float(np.std(corrs)),
                'n_paragraphs': len(corrs),
            }
        else:
            results[lag] = {'mean': 0.0, 'std': 0.0, 'n_paragraphs': 0}
    return results

t4_results = {}
for pc_idx, pc_name in enumerate(['PC1', 'PC2']):
    ac = compute_lag_autocorrelation(pc_scores[:, pc_idx], par_ids)
    t4_results[pc_name] = ac
    for lag in sorted(ac):
        print(f"  {pc_name} lag-{lag}: r={ac[lag]['mean']:+.4f} ± {ac[lag]['std']:.4f}  (N_par={ac[lag]['n_paragraphs']})")

# Shuffle null for T4
print("\n  Shuffle null (100 permutations)...")
shuffle_autocorrs = {f'PC{pc+1}': {lag: [] for lag in range(1, 4)} for pc in range(2)}
for _ in range(N_SHUFFLE):
    shuffled_scores = pc_scores.copy()
    for pid in np.unique(par_ids):
        mask = par_ids == pid
        idxs = np.where(mask)[0]
        perm = RNG.permutation(len(idxs))
        shuffled_scores[idxs] = pc_scores[idxs[perm]]
    for pc_idx, pc_name in enumerate(['PC1', 'PC2']):
        ac = compute_lag_autocorrelation(shuffled_scores[:, pc_idx], par_ids)
        for lag in range(1, 4):
            if lag in ac:
                shuffle_autocorrs[pc_name][lag].append(ac[lag]['mean'])

t4_results['shuffle_null'] = {}
for pc_name in ['PC1', 'PC2']:
    t4_results['shuffle_null'][pc_name] = {}
    for lag in range(1, 4):
        null_vals = shuffle_autocorrs[pc_name][lag]
        if null_vals:
            observed = t4_results[pc_name][lag]['mean']
            null_mean = float(np.mean(null_vals))
            null_std = float(np.std(null_vals))
            p_val = float(np.mean([1 if abs(nv) >= abs(observed) else 0 for nv in null_vals]))
            t4_results['shuffle_null'][pc_name][lag] = {
                'null_mean': round(null_mean, 6),
                'null_std': round(null_std, 6),
                'observed': round(observed, 6),
                'p': round(p_val, 4),
            }
            print(f"  {pc_name} lag-{lag}: obs={observed:+.4f}  null={null_mean:+.4f}±{null_std:.4f}  p={p_val:.3f}")

t4_results['pca_variance_explained'] = [round(float(v), 4) for v in variance_explained]


# ===========================================================================
# T5: CATEGORY-SUFFIX MODE INTERACTION
# ===========================================================================
print("\n" + "=" * 60)
print("T5: Category × Suffix Mode Interaction")
print("=" * 60)

mode_a_mask = suffix_modes == 'A'
mode_b_mask = suffix_modes == 'B'
n_a = mode_a_mask.sum()
n_b = mode_b_mask.sum()
print(f"  Mode A lines: {n_a}, Mode B lines: {n_b}")

t5_results = {'n_mode_a': int(n_a), 'n_mode_b': int(n_b), 'categories': {}}

for i, cat in enumerate(CATEGORIES):
    a_vals = cat_matrix[mode_a_mask, i]
    b_vals = cat_matrix[mode_b_mask, i]
    # Mann-Whitney U test
    if len(a_vals) > 5 and len(b_vals) > 5:
        u_stat, u_p = stats.mannwhitneyu(a_vals, b_vals, alternative='two-sided')
        a_mean = float(np.mean(a_vals))
        b_mean = float(np.mean(b_vals))
        diff = a_mean - b_mean
        sig = "***" if u_p < BONFERRONI_ALPHA else ""
        t5_results['categories'][cat] = {
            'mode_a_mean': round(a_mean, 6),
            'mode_b_mean': round(b_mean, 6),
            'difference': round(diff, 6),
            'mann_whitney_U': float(u_stat),
            'p': float(u_p),
            'significant': u_p < BONFERRONI_ALPHA,
        }
        if sig:
            print(f"  {cat:14s}: A={a_mean:.4f}  B={b_mean:.4f}  diff={diff:+.4f}  p={u_p:.4e} {sig}")
    else:
        t5_results['categories'][cat] = {'insufficient_data': True}

t5_n_sig = sum(1 for v in t5_results['categories'].values() if v.get('significant', False))
t5_results['n_significant'] = t5_n_sig
print(f"  Significant (Bonferroni): {t5_n_sig}/{N_CATS}")
if t5_n_sig == 0:
    print("  (no significant mode-category coupling)")


# ===========================================================================
# T6: KERNEL-MEDIATED CATEGORY SHIFT (PARTIAL CORRELATION)
# ===========================================================================
print("\n" + "=" * 60)
print("T6: Kernel-Mediated Category Shift (Partial Correlation)")
print("=" * 60)

t6_results = {}
kernel_covariates = [n_tokens_arr, k_fracs, h_fracs, e_fracs, headless_fracs]

for i, cat in enumerate(CATEGORIES):
    # Partial Spearman: category ~ position | length + kernel fractions
    rho_full, p_full = partial_spearman(
        positions, cat_matrix[:, i], kernel_covariates)

    # Compare with T2 (length-only control)
    rho_length_only = t2_results['pooled'][cat]['rho']

    # Did kernel control collapse the signal?
    collapsed = (abs(rho_full) < abs(rho_length_only) * 0.5) or (p_full > 0.05)

    t6_results[cat] = {
        'rho_length_only': round(rho_length_only, 6),
        'rho_length_plus_kernel': round(float(rho_full), 6),
        'p_length_plus_kernel': float(p_full),
        'significant_after_kernel': p_full < BONFERRONI_ALPHA,
        'collapsed_by_kernel': collapsed,
    }
    tag = "COLLAPSED" if collapsed else "SURVIVES"
    sig = "***" if p_full < BONFERRONI_ALPHA else ""
    print(f"  {cat:14s}: rho_L={rho_length_only:+.4f} -> rho_LK={rho_full:+.4f}  "
          f"p={p_full:.4e}  [{tag}] {sig}")

t6_n_survive = sum(1 for v in t6_results.values() if v['significant_after_kernel'])
t6_n_collapsed = sum(1 for v in t6_results.values() if v['collapsed_by_kernel'])
print(f"  Survive kernel control (Bonferroni): {t6_n_survive}/{N_CATS}")
print(f"  Collapsed by kernel: {t6_n_collapsed}/{N_CATS}")


# ===========================================================================
# SHUFFLE NULL FOR T1-T2
# ===========================================================================
print("\n" + "=" * 60)
print("Shuffle Null Control (100 permutations)")
print("=" * 60)

unique_pars = np.unique(par_ids)
par_indices = {pid: np.where(par_ids == pid)[0] for pid in unique_pars}

shuffle_t1_sig_counts = []
shuffle_t2_sig_counts = []

for shuf_iter in range(N_SHUFFLE):
    # Permute body line positions within each paragraph
    shuffled_pos = positions.copy()
    for pid, idxs in par_indices.items():
        perm = RNG.permutation(len(idxs))
        shuffled_pos[idxs] = positions[idxs[perm]]

    # T1 null: raw Spearman
    n_sig = 0
    for i in range(N_CATS):
        rho, p = stats.spearmanr(shuffled_pos, cat_matrix[:, i])
        if p < BONFERRONI_ALPHA:
            n_sig += 1
    shuffle_t1_sig_counts.append(n_sig)

    # T2 null: partial Spearman (length-controlled)
    n_sig = 0
    for i in range(N_CATS):
        rho, p = partial_spearman(shuffled_pos, cat_matrix[:, i], [n_tokens_arr])
        if p < BONFERRONI_ALPHA:
            n_sig += 1
    shuffle_t2_sig_counts.append(n_sig)

shuffle_t1_mean = float(np.mean(shuffle_t1_sig_counts))
shuffle_t2_mean = float(np.mean(shuffle_t2_sig_counts))
shuffle_t1_p95 = float(np.percentile(shuffle_t1_sig_counts, 95))
shuffle_t2_p95 = float(np.percentile(shuffle_t2_sig_counts, 95))

print(f"  T1 null: mean sig = {shuffle_t1_mean:.2f}, p95 = {shuffle_t1_p95:.0f}  (observed: {t1_n_sig})")
print(f"  T2 null: mean sig = {shuffle_t2_mean:.2f}, p95 = {shuffle_t2_p95:.0f}  (observed: {t2_pooled_n_sig})")

shuffle_results = {
    't1': {'mean_sig': shuffle_t1_mean, 'p95_sig': shuffle_t1_p95,
            'observed_sig': t1_n_sig,
            'above_null': t1_n_sig > shuffle_t1_p95},
    't2': {'mean_sig': shuffle_t2_mean, 'p95_sig': shuffle_t2_p95,
            'observed_sig': t2_pooled_n_sig,
            'above_null': t2_pooled_n_sig > shuffle_t2_p95},
}


# ===========================================================================
# DECISION LOGIC
# ===========================================================================
print("\n" + "=" * 60)
print("DECISION LOGIC")
print("=" * 60)

# Check within-section confirmation for pooled-significant categories
pooled_sig_cats = [cat for cat in CATEGORIES if t2_results['pooled'][cat]['significant']]
within_sec_confirmed = any(
    t2_results['section_artifact_check'].get(cat, {}).get('within_section_confirmed', False)
    for cat in pooled_sig_cats
)

if t2_pooled_n_sig == 0:
    verdict = "H0_EXTENDED"
    verdict_detail = (
        f"C963 EXTENDED to 8-category resolution. "
        f"0/{N_CATS} categories show significant trajectory after length control "
        f"(Bonferroni alpha={BONFERRONI_ALPHA:.4f}). "
        f"Body lines are compositionally homogeneous at the finest available grain."
    )
elif t2_pooled_n_sig <= 2 and not within_sec_confirmed:
    verdict = "SECTION_ARTIFACT"
    verdict_detail = (
        f"SECTION ARTIFACT. {t2_pooled_n_sig}/{N_CATS} categories significant pooled "
        f"({', '.join(pooled_sig_cats)}) but NONE confirmed within-section. "
        f"Apparent trajectory is a section composition artifact."
    )
elif t2_pooled_n_sig <= 2 and within_sec_confirmed:
    verdict = "WEAK_SIGNAL"
    verdict_detail = (
        f"WEAK SIGNAL. {t2_pooled_n_sig}/{N_CATS} categories significant pooled "
        f"({', '.join(pooled_sig_cats)}), confirmed within-section. "
        f"Marginal effect — no new constraint, flag for future work."
    )
elif t2_pooled_n_sig >= 3 and t6_n_survive == 0:
    verdict = "H1a_KERNEL_MEDIATED"
    verdict_detail = (
        f"Category drift exists but is KERNEL-MEDIATED. "
        f"{t2_pooled_n_sig}/{N_CATS} significant after length control, "
        f"but 0/{N_CATS} survive kernel control (T6). "
        f"The category trajectory is fully explained by C965 kernel composition shift."
    )
elif t2_pooled_n_sig >= 3 and t6_n_survive > 0:
    verdict = "H1a_INDEPENDENT_TRAJECTORY"
    verdict_detail = (
        f"GENUINE INDEPENDENT category trajectory. "
        f"{t2_pooled_n_sig}/{N_CATS} significant after length control, "
        f"{t6_n_survive}/{N_CATS} survive kernel control (T6). "
        f"Category dynamics are NOT fully explained by kernel shift."
    )
else:
    verdict = "AMBIGUOUS"
    verdict_detail = (
        f"Ambiguous result. T2 pooled sig={t2_pooled_n_sig}, "
        f"T6 survive={t6_n_survive}. Requires manual interpretation."
    )

# Check for boundary effects
q0_deviations = 0
q4_deviations = 0
for i, cat in enumerate(CATEGORIES):
    q0_val = quintile_means[0, i]
    q4_val = quintile_means[4, i]
    interior_mean = quintile_means[1:4, i].mean()
    if interior_mean > 0:
        if abs(q0_val - interior_mean) / interior_mean > 0.15:
            q0_deviations += 1
        if abs(q4_val - interior_mean) / interior_mean > 0.15:
            q4_deviations += 1

boundary_note = ""
if (q0_deviations >= 3 or q4_deviations >= 3) and verdict == "H0_EXTENDED":
    boundary_note = (
        f" Note: {q0_deviations} Q0 and {q4_deviations} Q4 boundary deviations >15% "
        f"from interior mean, but these do not survive statistical testing."
    )

print(f"\n  VERDICT: {verdict}")
print(f"  {verdict_detail}{boundary_note}")


# ===========================================================================
# SAVE RESULTS
# ===========================================================================
print("\n" + "=" * 60)
print("Saving results...")
print("=" * 60)

RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

results = {
    "phase": "PARAGRAPH_CATEGORY_TRAJECTORY",
    "phase_number": 591,
    "verdict": verdict,
    "verdict_detail": verdict_detail + boundary_note,
    "counts": {
        "total_paragraphs": len(all_paragraphs),
        "selected_paragraphs": len(selected),
        "excluded_non_gallows": excluded_non_gallows,
        "excluded_short": excluded_short,
        "body_lines": N,
        "section_distribution": dict(section_counts),
    },
    "t1_raw_trajectory": t1_results,
    "t2_length_controlled": t2_results,
    "t3_jsd_comparison": t3_results,
    "t4_serial_dependence": t4_results,
    "t5_mode_category_interaction": t5_results,
    "t6_kernel_mediated": {
        "categories": t6_results,
        "n_survive_kernel": t6_n_survive,
        "n_collapsed": t6_n_collapsed,
    },
    "shuffle_null": shuffle_results,
    "boundary_check": {
        "q0_deviations_gt_15pct": q0_deviations,
        "q4_deviations_gt_15pct": q4_deviations,
    },
    "parameters": {
        "min_body_lines": 5,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "n_shuffles": N_SHUFFLE,
        "random_seed": 42,
        "categories": CATEGORIES,
    },
}

# Convert numpy types for JSON serialization
def convert_numpy(obj):
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    return obj

results = convert_numpy(results)

with open(RESULTS_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
print(f"\nDONE. Verdict: {verdict}")

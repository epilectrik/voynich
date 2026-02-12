#!/usr/bin/env python3
"""
B_FOLIO_TEMPORAL_PROFILE - Script 2: Folio Temporal Dynamics

Measures within-folio temporal evolution of hazard/escape events,
QO/CHSH lane balance, and hazard proximity metrics.

Tests:
  4. Escape/Hazard Density Trajectory (hazard + escape rates by quartile)
  5. Lane Balance Trajectory (QO fraction by quartile)
  6. Hazard Proximity Trajectory (distance-to-hazard by quartile)

Extends C548 (gateway front-loading rho=-0.368) from manuscript-level
to within-folio resolution.

Constraint references:
  C548: Gateway front-loading at manuscript level
  C109: 17 forbidden transitions
  C601: Hazard circuit FL_HAZ -> FQ_CONN -> EN_CHSH
  C645: CHSH post-hazard dominance (75.2%)
  C647: Morphological lane signature (QO k=70.7%, CHSH e=68.7%)

Dependencies:
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json
  - phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json
  - phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json
  - scripts/voynich.py (Transcript)

Output: results/folio_temporal_dynamics.json
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

# Role mapping (class -> role) per BCSC v1.2
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

# EN sub-family mapping for lane detection
EN_QO_CLASSES = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH_CLASSES = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR_CLASSES = {41}
ALL_EN_CLASSES = EN_QO_CLASSES | EN_CHSH_CLASSES | EN_MINOR_CLASSES

# Hazard-participating classes (FL_HAZ + FQ hazardous + EN_CHSH hazard targets)
HAZARD_CLASSES = {7, 30, 9, 23, 8, 31}


def line_sort_key(line_str):
    """Sort line numbers numerically, handle alphanumeric."""
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)


def get_en_subfamily(cls):
    """Classify EN token by lane subfamily."""
    if cls in EN_QO_CLASSES:
        return 'QO'
    elif cls in EN_CHSH_CLASSES:
        return 'CHSH'
    elif cls in EN_MINOR_CLASSES:
        return 'MINOR'
    return None


print("=" * 70)
print("B_FOLIO_TEMPORAL_PROFILE - Script 2: Folio Temporal Dynamics")
print("=" * 70)

# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================
print("\n--- Section 1: Load & Prepare ---")

# Load class token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)

if 'token_to_class' in ctm_raw:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
else:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw.items()}

print(f"  Loaded class_token_map: {len(token_to_class)} tokens mapped")

# Load regime mapping (authoritative v2, GMM k=4)
regime_path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)

folio_to_regime = {folio: data['regime'] for folio, data in regime_data['regime_assignments'].items()}

print(f"  Loaded regime mapping: {len(folio_to_regime)} folios (v2 authoritative)")

# Load forbidden transitions (17 pairs)
forbidden_path = PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
with open(forbidden_path, 'r', encoding='utf-8') as f:
    forbidden_raw = json.load(f)

forbidden_pairs = set()
for t in forbidden_raw['transitions']:
    forbidden_pairs.add((t['source'], t['target']))

print(f"  Loaded forbidden transitions: {len(forbidden_pairs)} pairs")

# Build per-folio, per-line token sequences
tx = Transcript()

folio_lines = defaultdict(lambda: defaultdict(list))
total_b_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    total_b_tokens += 1

    cls = token_to_class.get(token.word)
    role = CLASS_TO_ROLE.get(cls, 'UNCLASSIFIED') if cls is not None else 'UNCLASSIFIED'
    en_sub = get_en_subfamily(cls) if role == 'EN' else None
    is_hazard_class = cls in HAZARD_CLASSES if cls is not None else False

    folio_lines[token.folio][token.line].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'en_subfamily': en_sub,
        'is_hazard_class': is_hazard_class,
    })

n_folios = len(folio_lines)
n_lines_total = sum(len(lines) for lines in folio_lines.values())
print(f"  Total B tokens: {total_b_tokens}")
print(f"  Folios: {n_folios}, Lines: {n_lines_total}")

# ============================================================
# SECTION 2: PER-LINE DYNAMICS FEATURES
# ============================================================
print("\n--- Section 2: Per-Line Dynamics Features ---")

line_dynamics = []

for folio in sorted(folio_lines.keys()):
    lines_sorted = sorted(folio_lines[folio].keys(), key=line_sort_key)
    n_lines = len(lines_sorted)
    if n_lines == 0:
        continue

    for idx, line_num in enumerate(lines_sorted):
        tokens = folio_lines[folio][line_num]
        n_tok = len(tokens)
        if n_tok == 0:
            continue

        norm_pos = idx / max(n_lines - 1, 1)
        quartile = min(int(norm_pos * 4) + 1, 4)

        # Hazard-class token density
        hazard_class_count = sum(1 for t in tokens if t['is_hazard_class'])
        hazard_class_density = hazard_class_count / n_tok

        # Forbidden transition events (consecutive token pairs)
        forbidden_count = 0
        for i in range(len(tokens) - 1):
            pair = (tokens[i]['word'], tokens[i + 1]['word'])
            if pair in forbidden_pairs:
                forbidden_count += 1
        forbidden_density = forbidden_count / max(n_tok - 1, 1)

        # Escape detection: first EN after each hazard-class token
        escape_events = []
        for i, t in enumerate(tokens):
            if t['is_hazard_class']:
                for j in range(i + 1, len(tokens)):
                    next_cls = tokens[j]['class']
                    if next_cls is not None and next_cls in ALL_EN_CLASSES:
                        escape_events.append({
                            'hazard_pos': i,
                            'escape_pos': j,
                            'escape_subfamily': tokens[j]['en_subfamily'],
                        })
                        break
        escape_count = len(escape_events)
        escape_density = escape_count / n_tok

        # Escape subfamily breakdown
        escape_qo = sum(1 for e in escape_events if e['escape_subfamily'] == 'QO')
        escape_chsh = sum(1 for e in escape_events if e['escape_subfamily'] == 'CHSH')

        # Lane balance: QO fraction among EN tokens
        en_tokens = [t for t in tokens if t['role'] == 'EN']
        n_en = len(en_tokens)
        qo_count = sum(1 for t in en_tokens if t['en_subfamily'] == 'QO')
        chsh_count = sum(1 for t in en_tokens if t['en_subfamily'] == 'CHSH')
        qo_fraction = qo_count / (qo_count + chsh_count) if (qo_count + chsh_count) > 0 else None

        # Hazard proximity: min distance to nearest hazard-class token
        hazard_positions = [i for i, t in enumerate(tokens) if t['is_hazard_class']]
        if hazard_positions:
            non_hazard_distances = []
            qo_distances = []
            chsh_distances = []
            for i, t in enumerate(tokens):
                if not t['is_hazard_class']:
                    min_dist = min(abs(i - hp) for hp in hazard_positions)
                    non_hazard_distances.append(min_dist)
                    if t['en_subfamily'] == 'QO':
                        qo_distances.append(min_dist)
                    elif t['en_subfamily'] == 'CHSH':
                        chsh_distances.append(min_dist)
            mean_hazard_dist = float(np.mean(non_hazard_distances)) if non_hazard_distances else None
            mean_qo_hazard_dist = float(np.mean(qo_distances)) if qo_distances else None
            mean_chsh_hazard_dist = float(np.mean(chsh_distances)) if chsh_distances else None
        else:
            mean_hazard_dist = None
            mean_qo_hazard_dist = None
            mean_chsh_hazard_dist = None

        line_dynamics.append({
            'folio': folio,
            'line': line_num,
            'n_tokens': n_tok,
            'norm_pos': norm_pos,
            'quartile': quartile,
            'hazard_class_density': hazard_class_density,
            'hazard_class_count': hazard_class_count,
            'forbidden_density': forbidden_density,
            'forbidden_count': forbidden_count,
            'escape_density': escape_density,
            'escape_count': escape_count,
            'escape_qo': escape_qo,
            'escape_chsh': escape_chsh,
            'n_en': n_en,
            'qo_count': qo_count,
            'chsh_count': chsh_count,
            'qo_fraction': qo_fraction,
            'mean_hazard_dist': mean_hazard_dist,
            'mean_qo_hazard_dist': mean_qo_hazard_dist,
            'mean_chsh_hazard_dist': mean_chsh_hazard_dist,
            'regime': folio_to_regime.get(folio, 'UNKNOWN'),
        })

print(f"  Line dynamics computed: {len(line_dynamics)} lines")

# Summary stats
total_forbidden = sum(d['forbidden_count'] for d in line_dynamics)
total_escape = sum(d['escape_count'] for d in line_dynamics)
total_hazard_tokens = sum(d['hazard_class_count'] for d in line_dynamics)
lines_with_hazard = sum(1 for d in line_dynamics if d['hazard_class_count'] > 0)
lines_with_en = sum(1 for d in line_dynamics if d['n_en'] > 0)
lines_with_haz_dist = sum(1 for d in line_dynamics if d['mean_hazard_dist'] is not None)
print(f"  Total forbidden transition events: {total_forbidden}")
print(f"  Total hazard-class tokens: {total_hazard_tokens}")
print(f"  Total escape events: {total_escape}")
print(f"  Lines with hazard-class tokens: {lines_with_hazard}/{len(line_dynamics)} ({100*lines_with_hazard/len(line_dynamics):.1f}%)")
print(f"  Lines with EN tokens: {lines_with_en}/{len(line_dynamics)} ({100*lines_with_en/len(line_dynamics):.1f}%)")

from scipy.stats import spearmanr, kruskal
import warnings

regimes = sorted(set(d['regime'] for d in line_dynamics if d['regime'] != 'UNKNOWN'))


def safe_spearmanr(x, y):
    """Spearman that handles constant arrays."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if len(set(y)) <= 1:
            return 0.0, 1.0
        return spearmanr(x, y)


def safe_kruskal(*groups):
    """KW that handles all-identical values."""
    # Check if all values across all groups are the same
    all_vals = []
    for g in groups:
        all_vals.extend(g)
    if len(set(all_vals)) <= 1:
        return 0.0, 1.0
    try:
        return kruskal(*groups)
    except ValueError:
        return 0.0, 1.0

# ============================================================
# SECTION 3: TEST 4 - ESCAPE/HAZARD DENSITY TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: Escape/Hazard Density Trajectory")
print("=" * 70)

test4_results = {}

# 4a: Hazard-class token density trajectory
positions = np.array([d['norm_pos'] for d in line_dynamics])
hazard_vals = np.array([d['hazard_class_density'] for d in line_dynamics])
rho_haz, p_haz = safe_spearmanr(positions, hazard_vals)

haz_by_q = {q: [] for q in range(1, 5)}
for d in line_dynamics:
    haz_by_q[d['quartile']].append(d['hazard_class_density'])
haz_q_means = {q: float(np.mean(haz_by_q[q])) for q in range(1, 5)}
kw_haz_h, kw_haz_p = safe_kruskal(*[haz_by_q[q] for q in range(1, 5)])

sig = '*' if kw_haz_p < 0.05 else ''
print(f"\n  4a. Hazard-class density:")
print(f"    Spearman rho = {rho_haz:.4f}, p = {p_haz:.2e}")
print(f"    KW H = {kw_haz_h:.2f}, p = {kw_haz_p:.2e} {sig}")
print(f"    Q1={haz_q_means[1]:.4f}  Q2={haz_q_means[2]:.4f}  Q3={haz_q_means[3]:.4f}  Q4={haz_q_means[4]:.4f}")
print(f"    Slope: {haz_q_means[4] - haz_q_means[1]:+.4f}")

test4_results['hazard_class_density'] = {
    'spearman': {'rho': round(rho_haz, 4), 'p': float(p_haz)},
    'kruskal_wallis': {'H': round(kw_haz_h, 2), 'p': float(kw_haz_p)},
    'quartile_means': {f'Q{q}': round(haz_q_means[q], 4) for q in range(1, 5)},
}

# 4b: Forbidden transition density trajectory
forb_vals = np.array([d['forbidden_density'] for d in line_dynamics])
rho_forb, p_forb = safe_spearmanr(positions, forb_vals)

forb_by_q = {q: [] for q in range(1, 5)}
for d in line_dynamics:
    forb_by_q[d['quartile']].append(d['forbidden_density'])
forb_q_means = {q: float(np.mean(forb_by_q[q])) for q in range(1, 5)}
kw_forb_h, kw_forb_p = safe_kruskal(*[forb_by_q[q] for q in range(1, 5)])

sig = '*' if kw_forb_p < 0.05 else ''
print(f"\n  4b. Forbidden transition density:")
print(f"    Spearman rho = {rho_forb:.4f}, p = {p_forb:.2e}")
print(f"    KW H = {kw_forb_h:.2f}, p = {kw_forb_p:.2e} {sig}")
print(f"    Q1={forb_q_means[1]:.4f}  Q2={forb_q_means[2]:.4f}  Q3={forb_q_means[3]:.4f}  Q4={forb_q_means[4]:.4f}")

test4_results['forbidden_density'] = {
    'spearman': {'rho': round(rho_forb, 4), 'p': float(p_forb)},
    'kruskal_wallis': {'H': round(kw_forb_h, 2), 'p': float(kw_forb_p)},
    'quartile_means': {f'Q{q}': round(forb_q_means[q], 4) for q in range(1, 5)},
}

# 4c: Escape density trajectory
esc_vals = np.array([d['escape_density'] for d in line_dynamics])
rho_esc, p_esc = safe_spearmanr(positions, esc_vals)

esc_by_q = {q: [] for q in range(1, 5)}
for d in line_dynamics:
    esc_by_q[d['quartile']].append(d['escape_density'])
esc_q_means = {q: float(np.mean(esc_by_q[q])) for q in range(1, 5)}
kw_esc_h, kw_esc_p = safe_kruskal(*[esc_by_q[q] for q in range(1, 5)])

sig = '*' if kw_esc_p < 0.05 else ''
print(f"\n  4c. Escape density:")
print(f"    Spearman rho = {rho_esc:.4f}, p = {p_esc:.2e}")
print(f"    KW H = {kw_esc_h:.2f}, p = {kw_esc_p:.2e} {sig}")
print(f"    Q1={esc_q_means[1]:.4f}  Q2={esc_q_means[2]:.4f}  Q3={esc_q_means[3]:.4f}  Q4={esc_q_means[4]:.4f}")

test4_results['escape_density'] = {
    'spearman': {'rho': round(rho_esc, 4), 'p': float(p_esc)},
    'kruskal_wallis': {'H': round(kw_esc_h, 2), 'p': float(kw_esc_p)},
    'quartile_means': {f'Q{q}': round(esc_q_means[q], 4) for q in range(1, 5)},
}

# 4d: Escape/hazard ratio trajectory
print(f"\n  4d. Escape/hazard ratio by quartile:")
ratio_by_q = {}
for q in range(1, 5):
    q_lines = [d for d in line_dynamics if d['quartile'] == q]
    total_haz_q = sum(d['hazard_class_count'] for d in q_lines)
    total_esc_q = sum(d['escape_count'] for d in q_lines)
    ratio = total_esc_q / total_haz_q if total_haz_q > 0 else 0
    ratio_by_q[f'Q{q}'] = {
        'hazard_tokens': total_haz_q,
        'escape_events': total_esc_q,
        'ratio': round(ratio, 4),
    }
    print(f"    Q{q}: {total_haz_q} hazard tokens, {total_esc_q} escapes, ratio={ratio:.4f}")

test4_results['escape_hazard_ratio'] = ratio_by_q

# 4e: Escape subfamily trajectory
print(f"\n  4e. Escape subfamily by quartile:")
for q in range(1, 5):
    q_lines = [d for d in line_dynamics if d['quartile'] == q]
    total_esc = sum(d['escape_count'] for d in q_lines)
    total_qo = sum(d['escape_qo'] for d in q_lines)
    total_chsh = sum(d['escape_chsh'] for d in q_lines)
    qo_frac = total_qo / total_esc if total_esc > 0 else 0
    chsh_frac = total_chsh / total_esc if total_esc > 0 else 0
    print(f"    Q{q}: {total_esc} escapes: QO={total_qo} ({qo_frac:.1%}), CHSH={total_chsh} ({chsh_frac:.1%})")

# Regime stratification
print(f"\n  Regime stratification:")
test4_results['regime_stratified'] = {}
for regime in regimes:
    rfeats = [d for d in line_dynamics if d['regime'] == regime]
    rq_haz = {q: [] for q in range(1, 5)}
    for d in rfeats:
        rq_haz[d['quartile']].append(d['hazard_class_density'])
    rq_means = {q: float(np.mean(rq_haz[q])) if rq_haz[q] else 0 for q in range(1, 5)}
    slope = rq_means[4] - rq_means[1]
    test4_results['regime_stratified'][regime] = {
        'hazard_quartile_means': {f'Q{q}': round(rq_means[q], 4) for q in range(1, 5)},
        'hazard_slope': round(slope, 4),
    }
    print(f"    {regime}: hazard Q1={rq_means[1]:.4f} Q4={rq_means[4]:.4f} slope={slope:+.4f}")

# ============================================================
# SECTION 4: TEST 5 - LANE BALANCE TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: Lane Balance Trajectory")
print("=" * 70)

# Filter to lines with EN tokens (QO + CHSH > 0)
lane_lines = [d for d in line_dynamics if d['qo_fraction'] is not None]
print(f"\n  Lines with QO+CHSH EN tokens: {len(lane_lines)}/{len(line_dynamics)}")

lane_pos = np.array([d['norm_pos'] for d in lane_lines])
qo_vals = np.array([d['qo_fraction'] for d in lane_lines])
rho_qo, p_qo = safe_spearmanr(lane_pos, qo_vals)

qo_by_q = {q: [] for q in range(1, 5)}
for d in lane_lines:
    qo_by_q[d['quartile']].append(d['qo_fraction'])
qo_q_means = {q: float(np.mean(qo_by_q[q])) if qo_by_q[q] else 0 for q in range(1, 5)}
kw_qo_h, kw_qo_p = safe_kruskal(*[qo_by_q[q] for q in range(1, 5) if qo_by_q[q]])

sig = '*' if kw_qo_p < 0.05 else ''
print(f"  Spearman rho = {rho_qo:.4f}, p = {p_qo:.2e}")
print(f"  KW H = {kw_qo_h:.2f}, p = {kw_qo_p:.2e} {sig}")
print(f"  Q1={qo_q_means[1]:.4f}  Q2={qo_q_means[2]:.4f}  Q3={qo_q_means[3]:.4f}  Q4={qo_q_means[4]:.4f}")
print(f"  Slope: {qo_q_means[4] - qo_q_means[1]:+.4f}")

test5_results = {
    'n_lines_with_lane': len(lane_lines),
    'spearman': {'rho': round(rho_qo, 4), 'p': float(p_qo)},
    'kruskal_wallis': {'H': round(kw_qo_h, 2), 'p': float(kw_qo_p)},
    'quartile_means': {f'Q{q}': round(qo_q_means[q], 4) for q in range(1, 5)},
}

# Regime stratification
print(f"\n  Regime stratification:")
test5_results['regime_stratified'] = {}
for regime in regimes:
    rfeats = [d for d in lane_lines if d['regime'] == regime]
    rq = {q: [] for q in range(1, 5)}
    for d in rfeats:
        rq[d['quartile']].append(d['qo_fraction'])
    rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
    slope = rq_means[4] - rq_means[1]
    test5_results['regime_stratified'][regime] = {
        'quartile_means': {f'Q{q}': round(rq_means[q], 4) for q in range(1, 5)},
        'slope': round(slope, 4),
        'n_lines': len(rfeats),
    }
    print(f"    {regime} (n={len(rfeats)}): Q1={rq_means[1]:.4f} Q4={rq_means[4]:.4f} slope={slope:+.4f}")

# ============================================================
# SECTION 5: TEST 6 - HAZARD PROXIMITY TRAJECTORY
# ============================================================
print("\n" + "=" * 70)
print("TEST 6: Hazard Proximity Trajectory")
print("=" * 70)

# Filter to lines with hazard-class tokens (distance is defined)
haz_dist_lines = [d for d in line_dynamics if d['mean_hazard_dist'] is not None]
print(f"\n  Lines with hazard-class tokens: {len(haz_dist_lines)}/{len(line_dynamics)}")

dist_pos = np.array([d['norm_pos'] for d in haz_dist_lines])
dist_vals = np.array([d['mean_hazard_dist'] for d in haz_dist_lines])
rho_dist, p_dist = safe_spearmanr(dist_pos, dist_vals)

dist_by_q = {q: [] for q in range(1, 5)}
for d in haz_dist_lines:
    dist_by_q[d['quartile']].append(d['mean_hazard_dist'])
dist_q_means = {q: float(np.mean(dist_by_q[q])) if dist_by_q[q] else 0 for q in range(1, 5)}
kw_dist_h, kw_dist_p = safe_kruskal(*[dist_by_q[q] for q in range(1, 5) if dist_by_q[q]])

sig = '*' if kw_dist_p < 0.05 else ''
print(f"  Spearman rho = {rho_dist:.4f}, p = {p_dist:.2e}")
print(f"  KW H = {kw_dist_h:.2f}, p = {kw_dist_p:.2e} {sig}")
print(f"  Q1={dist_q_means[1]:.4f}  Q2={dist_q_means[2]:.4f}  Q3={dist_q_means[3]:.4f}  Q4={dist_q_means[4]:.4f}")
print(f"  Slope: {dist_q_means[4] - dist_q_means[1]:+.4f}")

test6_results = {
    'n_lines_with_hazard': len(haz_dist_lines),
    'spearman': {'rho': round(rho_dist, 4), 'p': float(p_dist)},
    'kruskal_wallis': {'H': round(kw_dist_h, 2), 'p': float(kw_dist_p)},
    'quartile_means': {f'Q{q}': round(dist_q_means[q], 4) for q in range(1, 5)},
}

# Lane stratification: QO vs CHSH distance-to-hazard
print(f"\n  Lane stratification (distance to hazard):")
qo_dist_lines = [d for d in line_dynamics if d['mean_qo_hazard_dist'] is not None]
chsh_dist_lines = [d for d in line_dynamics if d['mean_chsh_hazard_dist'] is not None]

lane_strat = {}
for lane_name, lane_data, dist_key in [
    ('QO', qo_dist_lines, 'mean_qo_hazard_dist'),
    ('CHSH', chsh_dist_lines, 'mean_chsh_hazard_dist'),
]:
    if len(lane_data) > 10:
        lp = np.array([d['norm_pos'] for d in lane_data])
        lv = np.array([d[dist_key] for d in lane_data])
        rho_l, p_l = safe_spearmanr(lp, lv)
        lq = {q: [] for q in range(1, 5)}
        for d in lane_data:
            lq[d['quartile']].append(d[dist_key])
        lq_means = {q: float(np.mean(lq[q])) if lq[q] else 0 for q in range(1, 5)}
        lane_strat[lane_name] = {
            'n_lines': len(lane_data),
            'spearman': {'rho': round(rho_l, 4), 'p': float(p_l)},
            'quartile_means': {f'Q{q}': round(lq_means[q], 4) for q in range(1, 5)},
            'overall_mean': round(float(np.mean(lv)), 4),
        }
        print(f"    {lane_name} (n={len(lane_data)}): mean={np.mean(lv):.3f}, rho={rho_l:.4f}, p={p_l:.2e}")
        print(f"      Q1={lq_means[1]:.4f}  Q2={lq_means[2]:.4f}  Q3={lq_means[3]:.4f}  Q4={lq_means[4]:.4f}")
    else:
        lane_strat[lane_name] = {'note': 'insufficient data', 'n_lines': len(lane_data)}
        print(f"    {lane_name}: insufficient data ({len(lane_data)} lines)")

test6_results['lane_stratified'] = lane_strat

# Regime stratification
print(f"\n  Regime stratification:")
test6_results['regime_stratified'] = {}
for regime in regimes:
    rfeats = [d for d in haz_dist_lines if d['regime'] == regime]
    rq = {q: [] for q in range(1, 5)}
    for d in rfeats:
        rq[d['quartile']].append(d['mean_hazard_dist'])
    rq_means = {q: float(np.mean(rq[q])) if rq[q] else 0 for q in range(1, 5)}
    slope = rq_means[4] - rq_means[1]
    test6_results['regime_stratified'][regime] = {
        'quartile_means': {f'Q{q}': round(rq_means[q], 4) for q in range(1, 5)},
        'slope': round(slope, 4),
        'n_lines': len(rfeats),
    }
    print(f"    {regime} (n={len(rfeats)}): Q1={rq_means[1]:.4f} Q4={rq_means[4]:.4f} slope={slope:+.4f}")

# ============================================================
# SECTION 6: REGIME STRATIFICATION SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("REGIME STRATIFICATION SUMMARY")
print("=" * 70)

print("\n  Trajectory slopes (Q4 - Q1) by regime:")
print(f"  {'Regime':<12} {'Hazard':>10} {'Escape':>10} {'QO_frac':>10} {'Haz_dist':>10}")
print("  " + "-" * 50)

for regime in regimes:
    # Hazard slope
    haz_slope = test4_results['regime_stratified'].get(regime, {}).get('hazard_slope', 0)
    # Escape slope (compute here)
    rfeats_esc = [d for d in line_dynamics if d['regime'] == regime]
    rq_esc = {q: [] for q in range(1, 5)}
    for d in rfeats_esc:
        rq_esc[d['quartile']].append(d['escape_density'])
    esc_q_means_r = {q: float(np.mean(rq_esc[q])) if rq_esc[q] else 0 for q in range(1, 5)}
    esc_slope = esc_q_means_r[4] - esc_q_means_r[1]
    # QO slope
    qo_slope = test5_results['regime_stratified'].get(regime, {}).get('slope', 0)
    # Hazard dist slope
    dist_slope = test6_results['regime_stratified'].get(regime, {}).get('slope', 0)

    print(f"  {regime:<12} {haz_slope:>+10.4f} {esc_slope:>+10.4f} {qo_slope:>+10.4f} {dist_slope:>+10.4f}")

# ============================================================
# SECTION 7: SUMMARY & SAVE
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\nScorecard:")
sp = test4_results['hazard_class_density']['spearman']
q1 = test4_results['hazard_class_density']['quartile_means']['Q1']
q4 = test4_results['hazard_class_density']['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T4a Hazard    rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

sp = test4_results['forbidden_density']['spearman']
q1 = test4_results['forbidden_density']['quartile_means']['Q1']
q4 = test4_results['forbidden_density']['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T4b Forbidden rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

sp = test4_results['escape_density']['spearman']
q1 = test4_results['escape_density']['quartile_means']['Q1']
q4 = test4_results['escape_density']['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T4c Escape    rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

sp = test5_results['spearman']
q1 = test5_results['quartile_means']['Q1']
q4 = test5_results['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T5  QO frac   rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

sp = test6_results['spearman']
q1 = test6_results['quartile_means']['Q1']
q4 = test6_results['quartile_means']['Q4']
sig = 'SIG' if sp['p'] < 0.05 else 'ns'
print(f"  T6  Haz dist  rho={sp['rho']:+.4f} Q1={q1:.4f} Q4={q4:.4f} slope={q4-q1:+.4f} [{sig}]")

# Verdict
sig_count = 0
all_tests = [
    test4_results['hazard_class_density'],
    test4_results['forbidden_density'],
    test4_results['escape_density'],
    test5_results,
    test6_results,
]
for t in all_tests:
    if 'spearman' in t and t['spearman']['p'] < 0.05:
        sig_count += 1

print(f"\n  Significant trajectories: {sig_count}/5 dynamics tests")

# Save results
results = {
    'metadata': {
        'phase': 'B_FOLIO_TEMPORAL_PROFILE',
        'script': 'folio_temporal_dynamics',
        'timestamp': datetime.now().isoformat(),
        'total_b_tokens': total_b_tokens,
        'total_folios': n_folios,
        'total_lines': n_lines_total,
        'total_forbidden_events': total_forbidden,
        'total_hazard_tokens': total_hazard_tokens,
        'total_escape_events': total_escape,
        'lines_with_hazard': lines_with_hazard,
        'lines_with_en': lines_with_en,
    },
    'test4_escape_hazard': test4_results,
    'test5_lane_balance': test5_results,
    'test6_hazard_proximity': test6_results,
}

output_path = RESULTS_DIR / 'folio_temporal_dynamics.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("\nDone.")

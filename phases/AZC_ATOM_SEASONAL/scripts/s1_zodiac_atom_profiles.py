#!/usr/bin/env python3
"""
Phase AZC_ATOM_SEASONAL - Script 1: Zodiac Atom Profiles
=========================================================
Analyze zodiac folios at atom level using atomize() to test whether
seasonal differentiation shows up in MOD/TERM atom distributions.

HEAD profiles are already known to be uniform per C1519.
"""

import sys
import io
import os
import json
from collections import Counter, defaultdict
from pathlib import Path
import math

# Windows stdout encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure repo root on path
os.chdir(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================

ZODIAC_FOLIOS = [
    'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v',
]

REFERENCE_FOLIO = 'f57v'

ALL_FOLIOS = ZODIAC_FOLIOS + [REFERENCE_FOLIO]

SEASONS = {
    'Spring': ['f70v1', 'f70v2', 'f71r'],
    'Summer': ['f72r2', 'f72r3', 'f72v1'],
    'Autumn': ['f72v2', 'f72v3', 'f73r'],
    'Winter': ['f71v', 'f72r1', 'f73v'],
}

HEAD_ATOMS_LIST = ['a', 'e', 'o', 'k', 't', 'headless']
MOD_ATOMS_LIST = ['p', 'f', 'i', 'c', 'd', 's']
TERM_ATOMS_LIST = ['y', 'n', 'm', 'h', 'l', 'r']

# ============================================================
# DATA COLLECTION
# ============================================================

tx = Transcript()
morph = Morphology()

# Collect per-folio data
folio_data = {}

for folio_id in ALL_FOLIOS:
    tokens = []
    for token in tx.azc():
        if token.folio != folio_id:
            continue
        if token.is_label:
            continue
        if not token.word.strip():
            continue
        if '*' in token.word:
            continue
        tokens.append(token)

    head_counts = Counter()
    mod_counts = Counter()
    term_counts = Counter()
    e_depths = []
    opacity_counts = Counter()
    atom_bigrams = Counter()
    unique_atoms = set()
    total_atomized = 0
    failed = 0

    for token in tokens:
        try:
            a = morph.atomize(token.word)
        except Exception:
            failed += 1
            continue

        total_atomized += 1

        # HEAD
        head = a.head
        if head:
            head_counts[head] += 1
        else:
            head_counts['headless'] += 1

        # MOD
        for m in a.mods:
            mod_counts[m] += 1

        # TERM
        term = a.term
        if term:
            term_counts[term] += 1

        # e_depth
        e_depths.append(a.e_depth)

        # opacity
        opacity_counts[a.terminal_opacity] += 1

        # atoms and bigrams
        atom_chars = [c for c, _, _ in a.atoms]
        for c in atom_chars:
            unique_atoms.add(c)
        for i in range(len(atom_chars) - 1):
            atom_bigrams[atom_chars[i] + atom_chars[i+1]] += 1

    # e_depth distribution
    e_depth_dist = Counter(e_depths)
    e_depth_mean = sum(e_depths) / len(e_depths) if e_depths else 0.0
    n_total = len(e_depths) if e_depths else 1
    e_depth_pcts = {
        '0': e_depth_dist.get(0, 0) / n_total * 100,
        '1': e_depth_dist.get(1, 0) / n_total * 100,
        '2': e_depth_dist.get(2, 0) / n_total * 100,
        '3+': sum(v for k, v in e_depth_dist.items() if k >= 3) / n_total * 100,
    }

    folio_data[folio_id] = {
        'token_count': len(tokens),
        'atomized': total_atomized,
        'failed': failed,
        'head_counts': dict(head_counts),
        'mod_counts': dict(mod_counts),
        'term_counts': dict(term_counts),
        'e_depth_mean': round(e_depth_mean, 3),
        'e_depth_pcts': {k: round(v, 1) for k, v in e_depth_pcts.items()},
        'opacity_counts': dict(opacity_counts),
        'unique_atoms': sorted(unique_atoms),
        'top_bigrams': dict(atom_bigrams.most_common(15)),
    }

# ============================================================
# SEASONAL AGGREGATION
# ============================================================

def aggregate_season(folios):
    agg = {
        'folios': folios,
        'token_count': 0,
        'head_counts': Counter(),
        'mod_counts': Counter(),
        'term_counts': Counter(),
        'e_depths_all': [],
        'opacity_counts': Counter(),
        'atom_bigrams': Counter(),
    }
    for f in folios:
        if f not in folio_data:
            continue
        d = folio_data[f]
        agg['token_count'] += d['atomized']
        agg['head_counts'].update(d['head_counts'])
        agg['mod_counts'].update(d['mod_counts'])
        agg['term_counts'].update(d['term_counts'])
        agg['opacity_counts'].update(d['opacity_counts'])
        agg['atom_bigrams'].update(d.get('top_bigrams', {}))
    # Recompute e_depth from per-folio means (weighted approx)
    return agg

# Re-collect e_depths at season level from raw tokens for accuracy
season_e_depths = {s: [] for s in SEASONS}

for token in tx.azc():
    if token.folio not in ZODIAC_FOLIOS:
        continue
    if token.is_label or not token.word.strip() or '*' in token.word:
        continue
    for season, folios in SEASONS.items():
        if token.folio in folios:
            try:
                a = morph.atomize(token.word)
                season_e_depths[season].append(a.e_depth)
            except Exception:
                pass
            break

season_data = {}
for season, folios in SEASONS.items():
    agg = aggregate_season(folios)
    depths = season_e_depths[season]
    n = len(depths) if depths else 1
    depth_dist = Counter(depths)
    agg['e_depth_mean'] = round(sum(depths) / n, 3) if depths else 0.0
    agg['e_depth_pcts'] = {
        '0': round(depth_dist.get(0, 0) / n * 100, 1),
        '1': round(depth_dist.get(1, 0) / n * 100, 1),
        '2': round(depth_dist.get(2, 0) / n * 100, 1),
        '3+': round(sum(v for k, v in depth_dist.items() if k >= 3) / n * 100, 1),
    }
    season_data[season] = agg

# ============================================================
# STATISTICAL TESTS
# ============================================================

def chi_squared(observed_matrix):
    """Chi-squared test on a matrix (list of lists). Returns chi2, dof, p-approx."""
    nrows = len(observed_matrix)
    ncols = len(observed_matrix[0])
    row_totals = [sum(row) for row in observed_matrix]
    col_totals = [sum(observed_matrix[r][c] for r in range(nrows)) for c in range(ncols)]
    grand_total = sum(row_totals)
    if grand_total == 0:
        return 0.0, 0, 1.0

    chi2 = 0.0
    for r in range(nrows):
        for c in range(ncols):
            expected = row_totals[r] * col_totals[c] / grand_total
            if expected > 0:
                chi2 += (observed_matrix[r][c] - expected) ** 2 / expected

    dof = (nrows - 1) * (ncols - 1)

    # Approximate p-value using Wilson-Hilferty approximation for chi2 CDF
    if dof == 0:
        return chi2, dof, 1.0
    z = (chi2 / dof) ** (1/3) - (1 - 2 / (9 * dof))
    z /= math.sqrt(2 / (9 * dof))
    # Standard normal CDF approximation
    p = 0.5 * math.erfc(z / math.sqrt(2))
    return round(chi2, 2), dof, round(p, 6)


def kl_divergence(p_dist, q_dist):
    """KL(P || Q) with smoothing."""
    eps = 1e-10
    return sum(p * math.log((p + eps) / (q + eps)) for p, q in zip(p_dist, q_dist))


def js_divergence(p_dist, q_dist):
    """Jensen-Shannon divergence."""
    m = [(p + q) / 2 for p, q in zip(p_dist, q_dist)]
    return (kl_divergence(p_dist, m) + kl_divergence(q_dist, m)) / 2


def normalize(counts_dict, keys):
    """Normalize counts to probability distribution over keys."""
    total = sum(counts_dict.get(k, 0) for k in keys)
    if total == 0:
        return [1.0 / len(keys)] * len(keys)
    return [counts_dict.get(k, 0) / total for k in keys]


# Chi-squared on MOD atoms by season
season_names = list(SEASONS.keys())
mod_matrix = []
for s in season_names:
    row = [season_data[s]['mod_counts'].get(a, 0) for a in MOD_ATOMS_LIST]
    mod_matrix.append(row)

mod_chi2, mod_dof, mod_p = chi_squared(mod_matrix)

# Chi-squared on TERM atoms by season
term_matrix = []
for s in season_names:
    row = [season_data[s]['term_counts'].get(a, 0) for a in TERM_ATOMS_LIST]
    term_matrix.append(row)

term_chi2, term_dof, term_p = chi_squared(term_matrix)

# Chi-squared on HEAD atoms by season
head_matrix = []
for s in season_names:
    row = [season_data[s]['head_counts'].get(a, 0) for a in HEAD_ATOMS_LIST]
    head_matrix.append(row)

head_chi2, head_dof, head_p = chi_squared(head_matrix)

# Chi-squared on opacity by season
opacity_keys = ['OPAQUE', 'TRANSPARENT', 'SEMI_TRANSPARENT', 'NONE']
opacity_matrix = []
for s in season_names:
    row = [season_data[s]['opacity_counts'].get(a, 0) for a in opacity_keys]
    opacity_matrix.append(row)

opacity_chi2, opacity_dof, opacity_p = chi_squared(opacity_matrix)

# Jensen-Shannon divergence on MOD profiles (all pairs)
js_mod_results = {}
for i, s1 in enumerate(season_names):
    for j, s2 in enumerate(season_names):
        if j <= i:
            continue
        p = normalize(season_data[s1]['mod_counts'], MOD_ATOMS_LIST)
        q = normalize(season_data[s2]['mod_counts'], MOD_ATOMS_LIST)
        js_mod_results[f"{s1} vs {s2}"] = round(js_divergence(p, q), 6)

# JS on TERM profiles
js_term_results = {}
for i, s1 in enumerate(season_names):
    for j, s2 in enumerate(season_names):
        if j <= i:
            continue
        p = normalize(season_data[s1]['term_counts'], TERM_ATOMS_LIST)
        q = normalize(season_data[s2]['term_counts'], TERM_ATOMS_LIST)
        js_term_results[f"{s1} vs {s2}"] = round(js_divergence(p, q), 6)

# ============================================================
# ENRICHMENT/DEPLETION ANALYSIS
# ============================================================

# For each MOD and TERM atom, compute per-season share vs global share
global_mod = Counter()
global_term = Counter()
for s in season_names:
    global_mod.update(season_data[s]['mod_counts'])
    global_term.update(season_data[s]['term_counts'])

enrichment = {'MOD': {}, 'TERM': {}}

for atom in MOD_ATOMS_LIST:
    global_rate = global_mod[atom] / max(sum(global_mod.values()), 1)
    for s in season_names:
        total_s = max(sum(season_data[s]['mod_counts'].get(a, 0) for a in MOD_ATOMS_LIST), 1)
        local_rate = season_data[s]['mod_counts'].get(atom, 0) / total_s
        ratio = local_rate / global_rate if global_rate > 0 else 0
        if abs(ratio - 1.0) > 0.15:  # >15% enrichment/depletion
            key = f"{atom}_{s}"
            enrichment['MOD'][key] = {
                'atom': atom,
                'season': s,
                'global_rate': round(global_rate, 4),
                'local_rate': round(local_rate, 4),
                'ratio': round(ratio, 3),
                'direction': 'ENRICHED' if ratio > 1 else 'DEPLETED',
            }

for atom in TERM_ATOMS_LIST:
    global_rate = global_term[atom] / max(sum(global_term.values()), 1)
    for s in season_names:
        total_s = max(sum(season_data[s]['term_counts'].get(a, 0) for a in TERM_ATOMS_LIST), 1)
        local_rate = season_data[s]['term_counts'].get(atom, 0) / total_s
        ratio = local_rate / global_rate if global_rate > 0 else 0
        if abs(ratio - 1.0) > 0.15:
            key = f"{atom}_{s}"
            enrichment['TERM'][key] = {
                'atom': atom,
                'season': s,
                'global_rate': round(global_rate, 4),
                'local_rate': round(local_rate, 4),
                'ratio': round(ratio, 3),
                'direction': 'ENRICHED' if ratio > 1 else 'DEPLETED',
            }

# ============================================================
# PRINT RESULTS
# ============================================================

print("=" * 80)
print("ZODIAC ATOM PROFILES - SEASONAL ANALYSIS")
print("=" * 80)

print("\n--- PER-FOLIO SUMMARY ---")
print(f"{'Folio':<10} {'Tokens':>7} {'Atom':>5} {'Fail':>5}  HEAD top3{'':>20}  MOD top3{'':>20}  e_depth")
for f in ALL_FOLIOS:
    d = folio_data[f]
    head_top = sorted(d['head_counts'].items(), key=lambda x: -x[1])[:3]
    mod_top = sorted(d['mod_counts'].items(), key=lambda x: -x[1])[:3]
    head_str = ' '.join(f"{k}:{v}" for k, v in head_top)
    mod_str = ' '.join(f"{k}:{v}" for k, v in mod_top)
    print(f"{f:<10} {d['token_count']:>7} {d['atomized']:>5} {d['failed']:>5}  {head_str:<30}  {mod_str:<30}  {d['e_depth_mean']:.3f}")

print("\n--- SEASONAL PROFILES ---")
for season in season_names:
    sd = season_data[season]
    print(f"\n  {season} ({sd['token_count']} tokens) - folios: {', '.join(sd['folios'])}")

    # HEAD
    total_h = max(sum(sd['head_counts'].get(a, 0) for a in HEAD_ATOMS_LIST), 1)
    print(f"    HEAD: ", end='')
    for a in HEAD_ATOMS_LIST:
        c = sd['head_counts'].get(a, 0)
        print(f"{a}={c}({c/total_h*100:.1f}%) ", end='')
    print()

    # MOD
    total_m = max(sum(sd['mod_counts'].get(a, 0) for a in MOD_ATOMS_LIST), 1)
    print(f"    MOD:  ", end='')
    for a in MOD_ATOMS_LIST:
        c = sd['mod_counts'].get(a, 0)
        print(f"{a}={c}({c/total_m*100:.1f}%) ", end='')
    print()

    # TERM
    total_t = max(sum(sd['term_counts'].get(a, 0) for a in TERM_ATOMS_LIST), 1)
    print(f"    TERM: ", end='')
    for a in TERM_ATOMS_LIST:
        c = sd['term_counts'].get(a, 0)
        print(f"{a}={c}({c/total_t*100:.1f}%) ", end='')
    print()

    # e_depth
    print(f"    e_depth: mean={sd['e_depth_mean']:.3f}  " +
          "  ".join(f"d{k}={v}%" for k, v in sd['e_depth_pcts'].items()))

    # opacity
    total_o = max(sum(sd['opacity_counts'].values()), 1)
    print(f"    Opacity: ", end='')
    for k in opacity_keys:
        c = sd['opacity_counts'].get(k, 0)
        print(f"{k}={c}({c/total_o*100:.1f}%) ", end='')
    print()

print("\n--- STATISTICAL TESTS ---")
print(f"\n  Chi-squared: MOD atoms by season")
print(f"    chi2={mod_chi2}, dof={mod_dof}, p={mod_p}")
print(f"    {'SIGNIFICANT (p<0.05)' if mod_p < 0.05 else 'NOT SIGNIFICANT (p>=0.05)'}")

print(f"\n  Chi-squared: TERM atoms by season")
print(f"    chi2={term_chi2}, dof={term_dof}, p={term_p}")
print(f"    {'SIGNIFICANT (p<0.05)' if term_p < 0.05 else 'NOT SIGNIFICANT (p>=0.05)'}")

print(f"\n  Chi-squared: HEAD atoms by season")
print(f"    chi2={head_chi2}, dof={head_dof}, p={head_p}")
print(f"    {'SIGNIFICANT (p<0.05)' if head_p < 0.05 else 'NOT SIGNIFICANT (p>=0.05)'}")

print(f"\n  Chi-squared: Terminal opacity by season")
print(f"    chi2={opacity_chi2}, dof={opacity_dof}, p={opacity_p}")
print(f"    {'SIGNIFICANT (p<0.05)' if opacity_p < 0.05 else 'NOT SIGNIFICANT (p>=0.05)'}")

print("\n--- JENSEN-SHANNON DIVERGENCE (MOD profiles) ---")
for pair, val in sorted(js_mod_results.items()):
    bar = '#' * int(val * 5000)
    print(f"    {pair:<25} JSD={val:.6f}  {bar}")

print("\n--- JENSEN-SHANNON DIVERGENCE (TERM profiles) ---")
for pair, val in sorted(js_term_results.items()):
    bar = '#' * int(val * 5000)
    print(f"    {pair:<25} JSD={val:.6f}  {bar}")

print("\n--- ENRICHMENT/DEPLETION (>15% from global rate) ---")
for layer in ['MOD', 'TERM']:
    items = enrichment[layer]
    if not items:
        print(f"\n  {layer}: No enrichment/depletion detected")
        continue
    print(f"\n  {layer}:")
    for key, info in sorted(items.items()):
        direction = info['direction']
        print(f"    {info['atom']} in {info['season']}: {direction} "
              f"(local={info['local_rate']:.4f} vs global={info['global_rate']:.4f}, "
              f"ratio={info['ratio']:.3f})")

print("\n--- f57v REFERENCE FOLIO ---")
d = folio_data.get('f57v', {})
if d:
    print(f"  Tokens: {d['token_count']}, Atomized: {d['atomized']}")
    total_m = max(sum(d['mod_counts'].get(a, 0) for a in MOD_ATOMS_LIST), 1)
    print(f"  MOD:  ", end='')
    for a in MOD_ATOMS_LIST:
        c = d['mod_counts'].get(a, 0)
        print(f"{a}={c}({c/total_m*100:.1f}%) ", end='')
    print()
    total_t = max(sum(d['term_counts'].get(a, 0) for a in TERM_ATOMS_LIST), 1)
    print(f"  TERM: ", end='')
    for a in TERM_ATOMS_LIST:
        c = d['term_counts'].get(a, 0)
        print(f"{a}={c}({c/total_t*100:.1f}%) ", end='')
    print()
    print(f"  e_depth: mean={d['e_depth_mean']:.3f}  " +
          "  ".join(f"d{k}={v}%" for k, v in d['e_depth_pcts'].items()))

# ============================================================
# SAVE JSON
# ============================================================

output = {
    'metadata': {
        'script': 's1_zodiac_atom_profiles.py',
        'zodiac_folios': ZODIAC_FOLIOS,
        'reference_folio': REFERENCE_FOLIO,
        'seasons': {k: v for k, v in SEASONS.items()},
    },
    'per_folio': folio_data,
    'seasonal': {},
    'statistics': {
        'chi_squared_MOD': {'chi2': mod_chi2, 'dof': mod_dof, 'p': mod_p},
        'chi_squared_TERM': {'chi2': term_chi2, 'dof': term_dof, 'p': term_p},
        'chi_squared_HEAD': {'chi2': head_chi2, 'dof': head_dof, 'p': head_p},
        'chi_squared_opacity': {'chi2': opacity_chi2, 'dof': opacity_dof, 'p': opacity_p},
        'js_divergence_MOD': js_mod_results,
        'js_divergence_TERM': js_term_results,
    },
    'enrichment': enrichment,
}

# Convert seasonal data for JSON (Counters -> dicts)
for season in season_names:
    sd = season_data[season]
    output['seasonal'][season] = {
        'folios': sd['folios'],
        'token_count': sd['token_count'],
        'head_counts': dict(sd['head_counts']),
        'mod_counts': dict(sd['mod_counts']),
        'term_counts': dict(sd['term_counts']),
        'e_depth_mean': sd['e_depth_mean'],
        'e_depth_pcts': sd['e_depth_pcts'],
        'opacity_counts': dict(sd['opacity_counts']),
    }

output_path = Path('phases/AZC_ATOM_SEASONAL/results/s1_zodiac_atom_profiles.json')
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n\nResults saved to {output_path}")
print("=" * 80)

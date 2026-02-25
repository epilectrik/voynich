"""
Phase 453: AZC_CATEGORY_SCATTERSHOT

8-test battery probing whether the 8-category operational system (C1250)
structures AZC's positional vocabulary. Motivated by C1264: bridge MIDDLEs
(skip AZC) are TRANSITION-enriched, dark pipeline MIDDLEs (go through AZC)
are MARKING-dominated. Does AZC mediate this sorting?

Bonferroni threshold: p < 0.00625 (0.05 / 8 tests).

Tests:
  T1: AZC position category profile (zone x category)
  T2: AZC family category divergence (Zodiac vs A/C)
  T3: AZC atom-level positional differentiation
  T4: AZC as category sorting mediator (bridge vs dark zones)
  T5: AZC-exclusive vocabulary category profile
  T6: AZC category profile predicts B escape rate
  T7: Within-zone category coherence
  T8: AZC section atom profile vs A section atom profile

References: C1250, C1264, C759, C442, C468, C1266, C1207, C946
"""

import json
import sys
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as sp_stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, load_middle_classes

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "AZC_CATEGORY_SCATTERSHOT" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERM = 1000
BONFERRONI_P = 0.00625
SEED = 42

# ================================================================
# CATEGORY MAPPING (from Phase 446/448/449/452)
# ================================================================
GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ALL_CATEGORIES = sorted(set(GLOSS_TO_CATEGORY.values()))

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {atom: GLOSS_TO_CATEGORY[gloss]
                    for atom, gloss in ATOM_GLOSSES.items()}

# C1207 AXIS clusters
AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
    'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER', 'q': 'OTHER',
}
AXIS_NAMES = sorted(set(AXIS.values()))

MAIN_ZONES = {'R', 'C', 'S', 'P'}


# ================================================================
# NUMPY JSON ENCODER
# ================================================================
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# ================================================================
# UTILITY (reused from Phase 452)
# ================================================================
def auto_assign_category(autogloss_atoms):
    if not autogloss_atoms:
        return None
    votes = Counter()
    for atom in autogloss_atoms:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    if len(winners) == 1:
        return winners[0]
    return sorted(winners)[0]


def build_category_map():
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(list(atoms_str))
            if cat:
                mid_to_cat[mid] = cat
    return mid_to_cat


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = np.array([c / total for c in counts.values() if c > 0], dtype=float)
    return float(-np.sum(probs * np.log2(probs)))


def middle_to_atom_vector(mid):
    vec = np.zeros(len(AXIS_NAMES), dtype=float)
    if not mid:
        return vec
    axis_idx = {name: i for i, name in enumerate(AXIS_NAMES)}
    for ch in mid:
        ax = AXIS.get(ch)
        if ax:
            vec[axis_idx[ax]] += 1
    total = vec.sum()
    if total > 0:
        vec /= total
    return vec


def cosine_sim(v1, v2):
    d1 = np.dot(v1, v2)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(d1 / (n1 * n2))


def jsd(p, q):
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / (p.sum() + 1e-30)
    q = q / (q.sum() + 1e-30)
    return float(jensenshannon(p, q) ** 2)


def verdict(p_val, effect=None, effect_threshold=None):
    if p_val < BONFERRONI_P:
        if effect_threshold is not None and effect is not None:
            if abs(effect) < effect_threshold:
                return 'WEAK'
        return 'PASS'
    elif p_val < 0.05:
        return 'WEAK'
    return 'FAIL'


def extract_zone(placement):
    """Extract major zone from AZC placement code."""
    if not placement:
        return None
    first = placement[0].upper()
    if first in MAIN_ZONES:
        return first
    return None


# ================================================================
# DATA LOADING
# ================================================================
def load_all_data():
    t0 = time.time()
    tx = Transcript()
    morph = Morphology()
    mid_to_cat = build_category_map()
    ri_middles, pp_middles = load_middle_classes()
    print(f"  Category map: {len(mid_to_cat)} MIDDLEs")
    print(f"  PP: {len(pp_middles)}, RI: {len(ri_middles)}")

    # AZC tokens
    azc_tokens = []
    for token in tx.azc():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        tc = 'PP' if mid in pp_middles else ('RI' if mid in ri_middles else 'UNK')
        cat = mid_to_cat.get(mid) if mid else None
        zone = extract_zone(token.placement)
        azc_tokens.append({
            'word': w, 'folio': token.folio, 'line': token.line,
            'placement': token.placement, 'zone': zone,
            'section': token.section,
            'prefix': m.prefix, 'middle': mid, 'suffix': m.suffix,
            'token_class': tc, 'category': cat,
        })
    print(f"  AZC tokens: {len(azc_tokens)}")
    zone_counts = Counter(t['zone'] for t in azc_tokens if t['zone'])
    print(f"  Zones: {dict(sorted(zone_counts.items()))}")

    # A tokens (for T8)
    a_tokens = []
    for token in tx.currier_a():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        tc = 'PP' if mid in pp_middles else ('RI' if mid in ri_middles else 'UNK')
        a_tokens.append({
            'word': w, 'folio': token.folio, 'section': token.section,
            'middle': mid, 'token_class': tc,
        })
    print(f"  A tokens: {len(a_tokens)}")

    # B tokens (for T6)
    b_tokens = []
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        b_tokens.append({
            'word': w, 'folio': token.folio,
            'prefix': m.prefix, 'middle': m.middle,
            'token_class': 'PP' if m.middle in pp_middles else 'other',
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Bridge and dark pipeline MIDDLEs
    bridge_path = (ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM'
                   / 'results' / 'bridge_selection.json')
    with open(bridge_path, encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])

    dark_path = ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path, encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_middles = set(dark_data['middles'])
    print(f"  Bridge: {len(bridge_middles)}, Dark: {len(dark_middles)}")

    dt = time.time() - t0
    print(f"  Data loaded in {dt:.1f}s")

    return (azc_tokens, a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles,
            bridge_middles, dark_middles)


# ================================================================
# T1: AZC Position Category Profile
# ================================================================
def test_t1(azc_tokens):
    print("\n=== T1: AZC Position Category Profile ===")
    t0 = time.time()

    # Category distribution per zone
    zone_cats = defaultdict(list)
    for tok in azc_tokens:
        if tok['zone'] and tok['token_class'] == 'PP' and tok['category']:
            zone_cats[tok['zone']].append(tok['category'])

    zones = sorted(zone_cats.keys())
    print(f"  Zones with categorized PP: {zones}")
    for z in zones:
        print(f"    {z}: {len(zone_cats[z])} tokens, dist: {dict(Counter(zone_cats[z]))}")

    if len(zones) < 2:
        return {'test': 'T1', 'verdict': 'SKIP', 'reason': 'too_few_zones'}

    # Build contingency table
    cats = ALL_CATEGORIES
    contingency = np.zeros((len(zones), len(cats)), dtype=int)
    for i, z in enumerate(zones):
        dist = Counter(zone_cats[z])
        for j, c in enumerate(cats):
            contingency[i, j] = dist.get(c, 0)

    # Remove empty columns
    nonzero = contingency.sum(axis=0) > 0
    cats_active = [c for c, nz in zip(cats, nonzero) if nz]
    contingency = contingency[:, nonzero]

    chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
    total = contingency.sum()
    cramers_v = float(np.sqrt(chi2 / (total * (min(len(zones), len(cats_active)) - 1))))

    vrd = verdict(float(p_val), cramers_v, 0.05)
    dt = time.time() - t0
    print(f"  Chi-sq: {float(chi2):.2f}, V: {cramers_v:.3f}, p: {float(p_val):.6f} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T1', 'verdict': vrd, 'p_value': float(p_val),
        'chi_squared': float(chi2), 'cramers_v': cramers_v,
        'zones': zones, 'categories': cats_active,
        'contingency': contingency.tolist(),
        'zone_totals': {z: len(zone_cats[z]) for z in zones},
    }


# ================================================================
# T2: AZC Family Category Divergence
# ================================================================
def test_t2(azc_tokens):
    print("\n=== T2: AZC Family Category Divergence ===")
    t0 = time.time()

    # Z = Zodiac, A+C = A/C family
    family_cats = defaultdict(list)
    for tok in azc_tokens:
        if tok['token_class'] == 'PP' and tok['category']:
            sec = tok['section']
            if sec == 'Z':
                family_cats['Zodiac'].append(tok['category'])
            elif sec in ('A', 'C'):
                family_cats['A/C'].append(tok['category'])

    families = sorted(family_cats.keys())
    print(f"  Families: {families}")
    for f in families:
        print(f"    {f}: {len(family_cats[f])} tokens")

    if len(families) < 2:
        return {'test': 'T2', 'verdict': 'SKIP', 'reason': 'too_few_families'}

    cats = ALL_CATEGORIES
    contingency = np.zeros((len(families), len(cats)), dtype=int)
    for i, f in enumerate(families):
        dist = Counter(family_cats[f])
        for j, c in enumerate(cats):
            contingency[i, j] = dist.get(c, 0)

    nonzero = contingency.sum(axis=0) > 0
    cats_active = [c for c, nz in zip(cats, nonzero) if nz]
    contingency = contingency[:, nonzero]

    chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
    total = contingency.sum()
    cramers_v = float(np.sqrt(chi2 / (total * (min(len(families), len(cats_active)) - 1))))

    # Per-category fractions for reporting
    family_dists = {}
    for f in families:
        dist = Counter(family_cats[f])
        total_f = sum(dist.values())
        family_dists[f] = {c: dist.get(c, 0) / total_f for c in cats_active}

    vrd = verdict(float(p_val), cramers_v, 0.05)
    dt = time.time() - t0
    print(f"  Chi-sq: {float(chi2):.2f}, V: {cramers_v:.3f}, p: {float(p_val):.6f} -> {vrd}")
    for f in families:
        top3 = sorted(family_dists[f].items(), key=lambda x: -x[1])[:3]
        print(f"    {f}: {', '.join(f'{c}={v:.2f}' for c, v in top3)}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T2', 'verdict': vrd, 'p_value': float(p_val),
        'chi_squared': float(chi2), 'cramers_v': cramers_v,
        'families': families, 'categories': cats_active,
        'contingency': contingency.tolist(),
        'family_distributions': family_dists,
        'family_totals': {f: len(family_cats[f]) for f in families},
    }


# ================================================================
# T3: AZC Atom-Level Positional Differentiation
# ================================================================
def test_t3(azc_tokens):
    print("\n=== T3: AZC Atom-Level Positional Differentiation ===")
    t0 = time.time()

    axis_idx = {name: i for i, name in enumerate(AXIS_NAMES)}

    # Per-zone aggregate atom profiles
    zone_atoms = defaultdict(lambda: np.zeros(len(AXIS_NAMES)))
    for tok in azc_tokens:
        mid = tok['middle']
        zone = tok['zone']
        if tok['token_class'] != 'PP' or not mid or not zone:
            continue
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                zone_atoms[zone][axis_idx[ax]] += 1

    zones = sorted(zone_atoms.keys())
    print(f"  Zones: {zones}")
    for z in zones:
        total = zone_atoms[z].sum()
        prof = zone_atoms[z] / (total + 1e-30)
        detail = ", ".join(f"{name}={prof[i]:.3f}" for i, name in enumerate(AXIS_NAMES))
        print(f"    {z} (n={int(total)}): {detail}")

    # Per-folio-zone atom profiles for KW test
    folio_zone_atoms = defaultdict(lambda: Counter())
    folio_zone_map = {}
    for tok in azc_tokens:
        mid = tok['middle']
        zone = tok['zone']
        if tok['token_class'] != 'PP' or not mid or not zone:
            continue
        key = (tok['folio'], zone)
        folio_zone_map[key] = zone
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                folio_zone_atoms[key][ax] += 1

    # Convert to fraction vectors
    folio_profiles = {}
    for key, counts in folio_zone_atoms.items():
        total = sum(counts.values())
        if total >= 5:
            folio_profiles[key] = {ax: counts.get(ax, 0) / total for ax in AXIS_NAMES}

    # Group by zone
    zone_folio_profiles = defaultdict(list)
    for key, prof in folio_profiles.items():
        zone = folio_zone_map[key]
        zone_folio_profiles[zone].append(prof)

    valid_zones = {z: ps for z, ps in zone_folio_profiles.items() if len(ps) >= 3}
    print(f"  Zones with 3+ folios: {sorted(valid_zones.keys())}")

    if len(valid_zones) < 2:
        return {'test': 'T3', 'verdict': 'SKIP', 'reason': 'too_few_zones'}

    # Kruskal-Wallis per axis
    kw_results = {}
    zone_names = sorted(valid_zones.keys())
    for ax in AXIS_NAMES:
        groups = [[p[ax] for p in valid_zones[z]] for z in zone_names]
        if all(len(g) >= 2 for g in groups):
            stat, p = sp_stats.kruskal(*groups)
            kw_results[ax] = {
                'H': float(stat), 'p': float(p),
                'means': {z: float(np.mean([p[ax] for p in valid_zones[z]]))
                          for z in zone_names}
            }

    n_sig = sum(1 for r in kw_results.values() if r.get('p', 1) < 0.05)
    any_bonf = any(r.get('p', 1) < BONFERRONI_P for r in kw_results.values())

    print("  Kruskal-Wallis per axis:")
    for ax in AXIS_NAMES:
        r = kw_results.get(ax, {})
        if 'H' in r:
            flag = '**' if r['p'] < BONFERRONI_P else ('*' if r['p'] < 0.05 else '')
            means = ", ".join(f"{z}={r['means'][z]:.3f}" for z in zone_names)
            print(f"    {ax:12s}: H={r['H']:.2f} p={r['p']:.4f} {flag}  [{means}]")

    vrd = 'PASS' if any_bonf else ('WEAK' if n_sig >= 2 else 'FAIL')
    overall_p = min((r.get('p', 1) for r in kw_results.values()), default=1.0)
    dt = time.time() - t0
    print(f"  {n_sig} axes at p<0.05, Bonferroni={any_bonf} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T3', 'verdict': vrd, 'min_p': float(overall_p),
        'n_sig_axes': n_sig, 'any_bonferroni': any_bonf,
        'kruskal_wallis': kw_results,
        'zones_tested': zone_names,
        'n_folios_per_zone': {z: len(ps) for z, ps in valid_zones.items()},
        'axis_names': AXIS_NAMES,
    }


# ================================================================
# T4: AZC as Category Sorting Mediator
# ================================================================
def test_t4(azc_tokens, bridge_middles, dark_middles, mid_to_cat):
    print("\n=== T4: AZC as Category Sorting Mediator ===")
    t0 = time.time()

    # Which bridge/dark MIDDLEs appear in AZC?
    azc_pp_middles = set(t['middle'] for t in azc_tokens
                        if t['token_class'] == 'PP' and t['middle'])
    bridge_in_azc = bridge_middles & azc_pp_middles
    dark_in_azc = dark_middles & azc_pp_middles
    print(f"  Bridge in AZC: {len(bridge_in_azc)} / {len(bridge_middles)}")
    print(f"  Dark in AZC: {len(dark_in_azc)} / {len(dark_middles)}")

    if len(bridge_in_azc) < 5 or len(dark_in_azc) < 5:
        return {'test': 'T4', 'verdict': 'SKIP', 'reason': 'too_few_overlap'}

    # Per MIDDLE: compute zone distribution
    mid_zone_counts = defaultdict(lambda: Counter())
    for tok in azc_tokens:
        mid = tok['middle']
        zone = tok['zone']
        if mid and zone and tok['token_class'] == 'PP':
            mid_zone_counts[mid][zone] += 1

    # Aggregate zone distributions for bridge vs dark
    zones = sorted(MAIN_ZONES)
    bridge_zone_total = Counter()
    dark_zone_total = Counter()
    for mid in bridge_in_azc:
        for z, c in mid_zone_counts[mid].items():
            bridge_zone_total[z] += c
    for mid in dark_in_azc:
        for z, c in mid_zone_counts[mid].items():
            dark_zone_total[z] += c

    print(f"  Bridge zone dist: {dict(bridge_zone_total)}")
    print(f"  Dark zone dist:   {dict(dark_zone_total)}")

    # Chi-squared on 2 x n_zones contingency
    contingency = np.zeros((2, len(zones)), dtype=int)
    for i, z in enumerate(zones):
        contingency[0, i] = bridge_zone_total.get(z, 0)
        contingency[1, i] = dark_zone_total.get(z, 0)

    nonzero = contingency.sum(axis=0) > 0
    zones_active = [z for z, nz in zip(zones, nonzero) if nz]
    contingency = contingency[:, nonzero]

    if contingency.shape[1] < 2:
        return {'test': 'T4', 'verdict': 'SKIP', 'reason': 'too_few_zones'}

    chi2, p_val, dof, expected = sp_stats.chi2_contingency(contingency)
    total = contingency.sum()
    cramers_v = float(np.sqrt(chi2 / (total * (min(2, len(zones_active)) - 1))))

    # Also: category x zone partial association (controlling for bridge/dark)
    # Does category predict zone BEYOND bridge/dark status?
    partial_results = None
    cat_zone_pairs = []
    for tok in azc_tokens:
        mid = tok['middle']
        zone = tok['zone']
        cat = tok['category']
        if not mid or not zone or not cat or tok['token_class'] != 'PP':
            continue
        pipeline = 'bridge' if mid in bridge_middles else ('dark' if mid in dark_middles else 'other')
        if pipeline in ('bridge', 'dark'):
            cat_zone_pairs.append((cat, zone, pipeline))

    if len(cat_zone_pairs) >= 50:
        # Test: does category predict zone after controlling for pipeline?
        # Simple: chi-sq within each pipeline group
        for pipe in ('bridge', 'dark'):
            subset = [(c, z) for c, z, p in cat_zone_pairs if p == pipe]
            if len(subset) >= 20:
                cats_sub = sorted(set(c for c, z in subset))
                zones_sub = sorted(set(z for c, z in subset))
                if len(cats_sub) >= 2 and len(zones_sub) >= 2:
                    ct = np.zeros((len(cats_sub), len(zones_sub)), dtype=int)
                    ci = {c: i for i, c in enumerate(cats_sub)}
                    zi = {z: i for i, z in enumerate(zones_sub)}
                    for c, z in subset:
                        ct[ci[c], zi[z]] += 1
                    try:
                        pc2, pp, _, _ = sp_stats.chi2_contingency(ct)
                        ptotal = ct.sum()
                        pv = float(np.sqrt(pc2 / (ptotal * (min(len(cats_sub), len(zones_sub)) - 1))))
                        if partial_results is None:
                            partial_results = {}
                        partial_results[pipe] = {
                            'chi2': float(pc2), 'p': float(pp),
                            'cramers_v': pv, 'n': len(subset)}
                    except ValueError:
                        pass

    vrd = verdict(float(p_val), cramers_v, 0.05)
    dt = time.time() - t0
    print(f"  Chi-sq: {float(chi2):.2f}, V: {cramers_v:.3f}, p: {float(p_val):.6f} -> {vrd}")
    if partial_results:
        for pipe, pr in partial_results.items():
            print(f"  Partial ({pipe}): chi2={pr['chi2']:.1f} V={pr['cramers_v']:.3f} p={pr['p']:.4f}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T4', 'verdict': vrd, 'p_value': float(p_val),
        'chi_squared': float(chi2), 'cramers_v': cramers_v,
        'bridge_in_azc': len(bridge_in_azc), 'dark_in_azc': len(dark_in_azc),
        'bridge_zone_dist': dict(bridge_zone_total),
        'dark_zone_dist': dict(dark_zone_total),
        'zones_active': zones_active,
        'contingency': contingency.tolist(),
        'partial_category_zone': partial_results,
    }


# ================================================================
# T5: AZC-Exclusive Vocabulary Category Profile
# ================================================================
def test_t5(azc_tokens, pp_middles, ri_middles, mid_to_cat, bridge_middles, dark_middles):
    print("\n=== T5: AZC-Exclusive Vocabulary Category Profile ===")
    t0 = time.time()

    # Find UNK MIDDLEs in AZC
    unk_middles = set()
    for tok in azc_tokens:
        mid = tok['middle']
        if mid and tok['token_class'] == 'UNK':
            unk_middles.add(mid)
    print(f"  UNK MIDDLEs in AZC: {len(unk_middles)}")

    # Assign categories to UNK MIDDLEs via atom plurality vote
    unk_to_cat = {}
    for mid in unk_middles:
        # First check if it's in the dictionary
        if mid in mid_to_cat:
            unk_to_cat[mid] = mid_to_cat[mid]
        else:
            # Auto-assign from character atoms
            cat = auto_assign_category(list(mid))
            if cat:
                unk_to_cat[mid] = cat

    n_assigned = len(unk_to_cat)
    print(f"  UNK MIDDLEs with category: {n_assigned} / {len(unk_middles)}")

    if n_assigned < 10:
        return {'test': 'T5', 'verdict': 'SKIP', 'reason': 'too_few_categorized'}

    unk_dist = Counter(unk_to_cat.values())
    print(f"  UNK category dist: {dict(unk_dist)}")

    # Compare to PP (bridge + dark combined)
    pp_cats = [mid_to_cat[m] for m in (bridge_middles | dark_middles) if m in mid_to_cat]
    pp_dist = Counter(pp_cats)

    # Compare to bridge
    bridge_cats = [mid_to_cat[m] for m in bridge_middles if m in mid_to_cat]
    bridge_dist = Counter(bridge_cats)

    # Compare to dark
    dark_cats = [mid_to_cat[m] for m in dark_middles if m in mid_to_cat]
    dark_dist = Counter(dark_cats)

    comparisons = {}
    for name, ref_dist in [('pp_all', pp_dist), ('bridge', bridge_dist), ('dark', dark_dist)]:
        cats = sorted(set(list(unk_dist.keys()) + list(ref_dist.keys())))
        if len(cats) < 2:
            continue
        ct = np.zeros((2, len(cats)), dtype=int)
        for i, c in enumerate(cats):
            ct[0, i] = unk_dist.get(c, 0)
            ct[1, i] = ref_dist.get(c, 0)
        try:
            c2, p, _, _ = sp_stats.chi2_contingency(ct)
            total = ct.sum()
            v = float(np.sqrt(c2 / (total * (min(2, len(cats)) - 1))))
            comparisons[name] = {
                'chi2': float(c2), 'p': float(p), 'cramers_v': v,
                'n_unk': sum(unk_dist.values()), 'n_ref': sum(ref_dist.values())}
            print(f"  vs {name}: chi2={c2:.1f} V={v:.3f} p={p:.4f}")
        except ValueError:
            comparisons[name] = {'error': 'chi2_failed'}

    # Best comparison for verdict
    best_p = min((c.get('p', 1.0) for c in comparisons.values() if 'p' in c), default=1.0)
    best_v = max((c.get('cramers_v', 0) for c in comparisons.values() if 'cramers_v' in c), default=0)
    vrd = verdict(best_p, best_v, 0.1)
    dt = time.time() - t0
    print(f"  Best: p={best_p:.6f}, V={best_v:.3f} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T5', 'verdict': vrd, 'p_value': best_p,
        'cramers_v': best_v,
        'n_unk_middles': len(unk_middles),
        'n_categorized': n_assigned,
        'unk_dist': dict(unk_dist),
        'comparisons': comparisons,
    }


# ================================================================
# T6: AZC Category Profile Predicts B Escape Rate
# ================================================================
def test_t6(azc_tokens, b_tokens, mid_to_cat, pp_middles):
    print("\n=== T6: AZC Category Profile Predicts B Escape Rate ===")
    t0 = time.time()

    # AZC PP MIDDLEs set
    azc_pp = set(t['middle'] for t in azc_tokens
                 if t['token_class'] == 'PP' and t['middle'])

    # Per B folio: compute qo-prefix rate (escape proxy) and category fractions of AZC-shared vocab
    b_folio_data = defaultdict(lambda: {'total': 0, 'qo': 0, 'cats': Counter()})
    for tok in b_tokens:
        folio = tok['folio']
        b_folio_data[folio]['total'] += 1
        if tok['prefix'] == 'qo':
            b_folio_data[folio]['qo'] += 1
        mid = tok['middle']
        if mid and mid in azc_pp and mid in mid_to_cat:
            b_folio_data[folio]['cats'][mid_to_cat[mid]] += 1

    # Build folio-level data
    folio_escape = {}
    folio_cat_fracs = {}
    for folio, data in b_folio_data.items():
        if data['total'] >= 20:
            folio_escape[folio] = data['qo'] / data['total']
            cat_total = sum(data['cats'].values())
            if cat_total >= 5:
                folio_cat_fracs[folio] = {c: data['cats'].get(c, 0) / cat_total
                                          for c in ALL_CATEGORIES}

    shared_folios = sorted(set(folio_escape.keys()) & set(folio_cat_fracs.keys()))
    print(f"  B folios with escape + category data: {len(shared_folios)}")

    if len(shared_folios) < 10:
        return {'test': 'T6', 'verdict': 'SKIP', 'reason': 'too_few_folios'}

    # Correlate each category fraction with escape rate
    escape_vals = np.array([folio_escape[f] for f in shared_folios])
    correlations = {}
    for cat in ALL_CATEGORIES:
        cat_vals = np.array([folio_cat_fracs[f].get(cat, 0) for f in shared_folios])
        if np.std(cat_vals) > 0:
            r, p = sp_stats.spearmanr(cat_vals, escape_vals)
            correlations[cat] = {'rho': float(r), 'p': float(p)}

    print("  Category-escape correlations:")
    n_sig = 0
    for cat in ALL_CATEGORIES:
        if cat in correlations:
            c = correlations[cat]
            flag = '**' if c['p'] < BONFERRONI_P else ('*' if c['p'] < 0.05 else '')
            if c['p'] < 0.05:
                n_sig += 1
            print(f"    {cat:12s}: rho={c['rho']:+.3f} p={c['p']:.4f} {flag}")

    any_bonf = any(c['p'] < BONFERRONI_P for c in correlations.values())
    min_p = min((c['p'] for c in correlations.values()), default=1.0)
    vrd = 'PASS' if any_bonf else ('WEAK' if n_sig >= 2 else 'FAIL')
    dt = time.time() - t0
    print(f"  {n_sig} sig at p<0.05, Bonferroni={any_bonf} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T6', 'verdict': vrd, 'min_p': float(min_p),
        'n_sig_categories': n_sig, 'any_bonferroni': any_bonf,
        'correlations': correlations,
        'n_folios': len(shared_folios),
        'mean_escape_rate': float(np.mean(escape_vals)),
    }


# ================================================================
# T7: Within-Zone Category Coherence
# ================================================================
def test_t7(azc_tokens, rng):
    print("\n=== T7: Within-Zone Category Coherence ===")
    t0 = time.time()

    # Group by (folio, line)
    groups = defaultdict(list)
    for tok in azc_tokens:
        if tok['token_class'] == 'PP' and tok['category']:
            groups[(tok['folio'], tok['line'])].append(tok['category'])

    valid = {k: v for k, v in groups.items() if len(v) >= 2}
    n_groups = len(valid)
    print(f"  Groups with 2+ categorized PP: {n_groups}")

    if n_groups < 10:
        return {'test': 'T7', 'verdict': 'SKIP', 'reason': 'too_few_groups',
                'n_groups': n_groups}

    # Observed mean entropy
    obs_entropies = [entropy(Counter(v)) for v in valid.values()]
    obs_mean = np.mean(obs_entropies)
    print(f"  Observed mean entropy: {obs_mean:.4f}")

    # Pool and shuffle
    all_cats = []
    group_sizes = []
    for v in valid.values():
        all_cats.extend(v)
        group_sizes.append(len(v))
    all_cats = np.array(all_cats)

    null_means = []
    for _ in range(N_PERM):
        shuffled = all_cats.copy()
        rng.shuffle(shuffled)
        idx = 0
        perm_ents = []
        for sz in group_sizes:
            chunk = shuffled[idx:idx+sz]
            perm_ents.append(entropy(Counter(chunk)))
            idx += sz
        null_means.append(np.mean(perm_ents))

    null_means = np.array(null_means)
    p_val = float(np.mean(null_means <= obs_mean))
    effect = float((np.mean(null_means) - obs_mean) / (np.std(null_means) + 1e-12))

    vrd = verdict(p_val)
    dt = time.time() - t0
    print(f"  Null mean: {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
    print(f"  Effect (Cohen d): {effect:.3f}")
    print(f"  p = {p_val:.6f} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T7', 'verdict': vrd, 'p_value': p_val,
        'obs_mean_entropy': float(obs_mean),
        'null_mean_entropy': float(np.mean(null_means)),
        'null_std': float(np.std(null_means)),
        'effect_cohen_d': effect,
        'n_groups': n_groups,
        'n_tokens': len(all_cats),
    }


# ================================================================
# T8: AZC Section Atom Profile vs A Section Atom Profile
# ================================================================
def test_t8(azc_tokens, a_tokens, pp_middles):
    print("\n=== T8: AZC Section Atom Profile vs A Section ===")
    t0 = time.time()

    axis_idx = {name: i for i, name in enumerate(AXIS_NAMES)}

    # A section atom profiles (recompute from Phase 452 C1266)
    a_section_atoms = defaultdict(lambda: np.zeros(len(AXIS_NAMES)))
    for tok in a_tokens:
        mid = tok['middle']
        sec = tok['section']
        if tok['token_class'] != 'PP' or not mid or not sec:
            continue
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                a_section_atoms[sec][axis_idx[ax]] += 1

    a_profiles = {}
    for sec, vec in a_section_atoms.items():
        total = vec.sum()
        if total > 0:
            a_profiles[sec] = vec / total

    print(f"  A sections: {sorted(a_profiles.keys())}")

    # AZC section atom profiles
    azc_section_atoms = defaultdict(lambda: np.zeros(len(AXIS_NAMES)))
    for tok in azc_tokens:
        mid = tok['middle']
        sec = tok['section']
        if tok['token_class'] != 'PP' or not mid or not sec:
            continue
        for ch in mid:
            ax = AXIS.get(ch)
            if ax:
                azc_section_atoms[sec][axis_idx[ax]] += 1

    azc_profiles = {}
    for sec, vec in azc_section_atoms.items():
        total = vec.sum()
        if total > 0:
            azc_profiles[sec] = vec / total

    print(f"  AZC sections: {sorted(azc_profiles.keys())}")

    for sec, prof in sorted(azc_profiles.items()):
        total = azc_section_atoms[sec].sum()
        detail = ", ".join(f"{name}={prof[i]:.3f}" for i, name in enumerate(AXIS_NAMES))
        print(f"    {sec} (n={int(total)}): {detail}")

    # Cross-system comparison: each AZC section vs each A section
    a_secs = sorted(a_profiles.keys())
    azc_secs = sorted(azc_profiles.keys())

    if len(a_secs) < 2 or len(azc_secs) < 2:
        return {'test': 'T8', 'verdict': 'SKIP', 'reason': 'too_few_sections'}

    # Pearson r and JSD for each pair
    cross_r = {}
    cross_jsd = {}
    for az_sec in azc_secs:
        for a_sec in a_secs:
            r, p = sp_stats.pearsonr(azc_profiles[az_sec], a_profiles[a_sec])
            j = jsd(azc_profiles[az_sec], a_profiles[a_sec])
            cross_r[(az_sec, a_sec)] = {'r': float(r), 'p': float(p)}
            cross_jsd[(az_sec, a_sec)] = float(j)

    print("\n  Cross-system Pearson r (AZC sec -> A sec):")
    header = "       " + "  ".join(f"{s:>6}" for s in a_secs)
    print(f"  {header}")
    for az_sec in azc_secs:
        row = f"  {az_sec:>5}  " + "  ".join(
            f"{cross_r[(az_sec, a_sec)]['r']:+.3f}" for a_sec in a_secs)
        print(row)

    print("\n  JSD (AZC sec -> A sec):")
    print(f"  {header}")
    for az_sec in azc_secs:
        row = f"  {az_sec:>5}  " + "  ".join(
            f"{cross_jsd[(az_sec, a_sec)]:.4f}" for a_sec in a_secs)
        print(row)

    # Are AZC sections differentiated from each other?
    azc_pairwise_jsd = {}
    for i in range(len(azc_secs)):
        for j in range(i+1, len(azc_secs)):
            j_val = jsd(azc_profiles[azc_secs[i]], azc_profiles[azc_secs[j]])
            azc_pairwise_jsd[(azc_secs[i], azc_secs[j])] = float(j_val)
    mean_internal_jsd = np.mean(list(azc_pairwise_jsd.values())) if azc_pairwise_jsd else 0

    # Does any AZC section preferentially match one A section?
    # For each AZC section, find closest A section
    closest_matches = {}
    for az_sec in azc_secs:
        best_a = min(a_secs, key=lambda a: cross_jsd[(az_sec, a)])
        closest_matches[az_sec] = {
            'closest_a_section': best_a,
            'jsd': cross_jsd[(az_sec, best_a)],
            'r': cross_r[(az_sec, best_a)]['r'],
        }

    # Verdict: is there systematic non-uniform correspondence?
    # If all AZC sections map to the same A section, that's uniform (FAIL)
    mapped_a = set(v['closest_a_section'] for v in closest_matches.values())
    diverse_mapping = len(mapped_a) >= 2

    # Check if AZC sections are internally differentiated
    vrd = 'PASS' if diverse_mapping and mean_internal_jsd > 0.005 else 'FAIL'
    if mean_internal_jsd > 0.002 and not diverse_mapping:
        vrd = 'WEAK'

    dt = time.time() - t0
    print(f"\n  Mean AZC internal JSD: {mean_internal_jsd:.4f}")
    print(f"  Closest A matches: {closest_matches}")
    print(f"  Diverse mapping: {diverse_mapping} -> {vrd}")
    print(f"  ({dt:.1f}s)")

    return {
        'test': 'T8', 'verdict': vrd,
        'mean_internal_jsd': mean_internal_jsd,
        'diverse_mapping': diverse_mapping,
        'closest_matches': closest_matches,
        'azc_pairwise_jsd': {f"{k[0]}-{k[1]}": v for k, v in azc_pairwise_jsd.items()},
        'cross_r': {f"{k[0]}-{k[1]}": v for k, v in cross_r.items()},
        'cross_jsd': {f"{k[0]}-{k[1]}": v for k, v in cross_jsd.items()},
        'a_profiles': {s: p.tolist() for s, p in a_profiles.items()},
        'azc_profiles': {s: p.tolist() for s, p in azc_profiles.items()},
        'axis_names': AXIS_NAMES,
    }


# ================================================================
# MAIN
# ================================================================
def main():
    print("=" * 60)
    print("Phase 453: AZC_CATEGORY_SCATTERSHOT")
    print("8-test battery: category system vs AZC positional structure")
    print("=" * 60)

    t_start = time.time()
    rng = np.random.RandomState(SEED)

    print("\n--- Loading data ---")
    (azc_tokens, a_tokens, b_tokens, mid_to_cat, ri_middles, pp_middles,
     bridge_middles, dark_middles) = load_all_data()

    # Coverage stats
    n_azc_with_cat = sum(1 for t in azc_tokens if t['category'])
    n_azc_pp = sum(1 for t in azc_tokens if t['token_class'] == 'PP')
    n_azc_pp_with_cat = sum(1 for t in azc_tokens
                            if t['token_class'] == 'PP' and t['category'])
    print(f"\n  AZC PP tokens with category: {n_azc_pp_with_cat} / {n_azc_pp} "
          f"({100*n_azc_pp_with_cat/(n_azc_pp+1e-9):.1f}%)")

    results = {
        'phase': 'AZC_CATEGORY_SCATTERSHOT',
        'phase_number': 453,
        'n_perm': N_PERM,
        'bonferroni_p': BONFERRONI_P,
        'seed': SEED,
        'data_summary': {
            'n_azc_tokens': len(azc_tokens),
            'n_a_tokens': len(a_tokens),
            'n_b_tokens': len(b_tokens),
            'n_middles_with_category': len(mid_to_cat),
            'n_pp_middles': len(pp_middles),
            'n_ri_middles': len(ri_middles),
            'n_bridge_middles': len(bridge_middles),
            'n_dark_middles': len(dark_middles),
            'azc_pp_category_coverage': f"{100*n_azc_pp_with_cat/(n_azc_pp+1e-9):.1f}%",
        },
        'tests': {},
    }

    # Run tests
    t1 = test_t1(azc_tokens)
    results['tests']['T1'] = t1

    t2 = test_t2(azc_tokens)
    results['tests']['T2'] = t2

    t3 = test_t3(azc_tokens)
    results['tests']['T3'] = t3

    t4 = test_t4(azc_tokens, bridge_middles, dark_middles, mid_to_cat)
    results['tests']['T4'] = t4

    t5 = test_t5(azc_tokens, pp_middles, ri_middles, mid_to_cat,
                 bridge_middles, dark_middles)
    results['tests']['T5'] = t5

    t6 = test_t6(azc_tokens, b_tokens, mid_to_cat, pp_middles)
    results['tests']['T6'] = t6

    t7 = test_t7(azc_tokens, rng)
    results['tests']['T7'] = t7

    t8 = test_t8(azc_tokens, a_tokens, pp_middles)
    results['tests']['T8'] = t8

    # Summary
    all_tests = [t1, t2, t3, t4, t5, t6, t7, t8]
    pass_count = sum(1 for t in all_tests if t.get('verdict') == 'PASS')
    weak_count = sum(1 for t in all_tests if t.get('verdict') == 'WEAK')
    fail_count = sum(1 for t in all_tests if t.get('verdict') == 'FAIL')
    skip_count = sum(1 for t in all_tests if t.get('verdict') == 'SKIP')

    if pass_count >= 4:
        overall = 'AZC_CATEGORY_STRUCTURED'
    elif pass_count >= 2:
        overall = 'PARTIAL_SIGNAL'
    else:
        overall = 'AZC_CATEGORY_ORTHOGONAL'

    results['summary'] = {
        'pass': pass_count, 'weak': weak_count,
        'fail': fail_count, 'skip': skip_count,
        'overall_verdict': overall,
    }

    total_time = time.time() - t_start
    results['runtime_seconds'] = round(total_time, 1)

    # Print summary table
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Test':<6} {'Verdict':<10} {'p-value':<12} {'Effect':<10}")
    print("-" * 40)
    for t in all_tests:
        name = t['test']
        vrd = t.get('verdict', '?')
        p = t.get('p_value', t.get('min_p', '-'))
        if isinstance(p, float):
            p_str = f"{p:.6f}"
        else:
            p_str = str(p)
        eff = t.get('effect_cohen_d', t.get('cramers_v', '-'))
        if isinstance(eff, float):
            eff_str = f"{eff:.3f}"
        else:
            eff_str = str(eff)
        print(f"{name:<6} {vrd:<10} {p_str:<12} {eff_str:<10}")

    print(f"\nPASS: {pass_count}, WEAK: {weak_count}, FAIL: {fail_count}, SKIP: {skip_count}")
    print(f"OVERALL: {overall}")
    print(f"Runtime: {total_time:.1f}s")

    # Save
    out_path = RESULTS_DIR / "azc_category_scattershot.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

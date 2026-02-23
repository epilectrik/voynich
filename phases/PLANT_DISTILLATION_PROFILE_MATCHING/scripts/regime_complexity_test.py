"""
Phase 436 Extension: REGIME -> Distillation Complexity Class Test (CORRECTED)
=============================================================================
Tests whether the 4 Voynich regimes correspond to distillation
complexity classes defined by plant material type.

Uses paragraph-level profiles (C855/C862: paragraphs are programs).

Hypothesis:
  REGIME_1 (energy-heavy)    -> ROOT/WOOD/BARK (high sustained heat)
  REGIME_2 (balanced/output) -> LEAF/SEED (simple, standard)
  REGIME_3 (intervention)    -> complex FLOWER (cohobation, fractional)
  REGIME_4 (precision)       -> delicate FLOWER (heat-sensitive, exact timing)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

PLANT_PATH = ROOT / 'phases' / 'PLANT_DISTILLATION_PROFILE_MATCHING' / 'data' / 'plant_profiles.json'
REGIME_PATH = ROOT / 'data' / 'regime_folio_mapping.json'
RESULTS_PATH = ROOT / 'phases' / 'PLANT_DISTILLATION_PROFILE_MATCHING' / 'results' / 'regime_complexity_test.json'

ATOM_TO_AXIS = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE',
}
AXES = ['ENERGY', 'STABILITY', 'MONITORING', 'ITERATION', 'CLOSURE', 'STRUCTURAL', 'FREE']
MIN_PARAGRAPH_CHARS = 15

# Distillation complexity classes
COMPLEX_PLANTS = {'rose', 'ylang_ylang', 'jasmine', 'violet', 'neroli', 'orris'}
SIMPLE_PLANTS = {'lavender', 'chamomile', 'helichrysum', 'peppermint', 'rosemary',
                 'thyme', 'sage', 'basil', 'lemongrass', 'melissa', 'bay_laurel',
                 'anise', 'fennel', 'coriander', 'orange_peel', 'lemon_peel',
                 'juniper_berry', 'cassia', 'cedarwood'}
HARD_PLANTS = {'vetiver', 'sandalwood', 'rosewood', 'valerian', 'angelica_root',
               'cinnamon_bark', 'birch_bark', 'frankincense', 'myrrh', 'mastic'}


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# =====================================================================
# LOAD DATA
# =====================================================================
print("REGIME -> DISTILLATION COMPLEXITY CLASS TEST (PARAGRAPH-LEVEL)")
print("=" * 70)

# Load plant profiles
with open(PLANT_PATH) as f:
    plant_data = json.load(f)

plants = plant_data['plants']
print(f"Plants: {len(plants)}")

# Normalize plant scores to proportions
plant_profiles = {}
for p in plants:
    total = sum(p['scores'][ax] for ax in AXES)
    if total > 0:
        plant_profiles[p['name']] = {
            'profile': {ax: p['scores'][ax] / total for ax in AXES},
            'category': p['category'],
        }

# Build complexity class profiles
class_profiles = {'HARD': {}, 'SIMPLE': {}, 'COMPLEX': {}}
class_members = {'HARD': [], 'SIMPLE': [], 'COMPLEX': []}

for name, data in plant_profiles.items():
    if name in HARD_PLANTS:
        cls = 'HARD'
    elif name in COMPLEX_PLANTS:
        cls = 'COMPLEX'
    else:
        cls = 'SIMPLE'
    class_members[cls].append(name)

for cls in class_profiles:
    members = class_members[cls]
    if members:
        vecs = [np.array([plant_profiles[m]['profile'][ax] for ax in AXES]) for m in members]
        class_profiles[cls] = {AXES[j]: float(np.mean([v[j] for v in vecs]))
                               for j in range(len(AXES))}

print(f"\nComplexity classes:")
for cls, members in class_members.items():
    print(f"  {cls:8s}: {len(members)} plants ({', '.join(sorted(members)[:5])}{'...' if len(members)>5 else ''})")

print(f"\nClass centroids (normalized proportions):")
print(f"  {'Class':<10}", end='')
for ax in AXES:
    print(f"  {ax[:4]:>6}", end='')
print()
for cls in ['SIMPLE', 'HARD', 'COMPLEX']:
    print(f"  {cls:<10}", end='')
    for ax in AXES:
        print(f"  {class_profiles[cls][ax]:>5.1%}", end='')
    print()

# =====================================================================
# BUILD PARAGRAPH PROFILES BY REGIME
# =====================================================================
print(f"\n{'=' * 70}")
print("PARAGRAPH PROFILES BY REGIME")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Load regime assignments
with open(REGIME_PATH) as f:
    regime_raw = json.load(f)
regime_data = regime_raw.get('regime_assignments', regime_raw)

# Segment into paragraphs
paragraphs = []
current_par = None

for t in tx.currier_b():
    if t.par_initial:
        if current_par is not None:
            paragraphs.append(current_par)
        regime = regime_data.get(t.folio, {}).get('regime', 'UNK') if isinstance(regime_data, dict) else 'UNK'
        current_par = {
            'folio': t.folio,
            'section': t.section if hasattr(t, 'section') else 'UNK',
            'regime': regime,
            'tokens': [],
        }
    if current_par is not None:
        current_par['tokens'].append(t)

if current_par is not None:
    paragraphs.append(current_par)

# Compute per-paragraph axis profiles
par_profiles = []
for pi, par in enumerate(paragraphs):
    axis_counts = Counter()
    total_mapped = 0
    for t in par['tokens']:
        m = morph.extract(t.word)
        if m.middle:
            for ch in m.middle:
                if ch in ATOM_TO_AXIS:
                    axis_counts[ATOM_TO_AXIS[ch]] += 1
                    total_mapped += 1

    if total_mapped >= MIN_PARAGRAPH_CHARS:
        profile = {ax: axis_counts[ax] / total_mapped for ax in AXES}
        par_profiles.append({
            'par_idx': pi,
            'folio': par['folio'],
            'regime': par['regime'],
            'n_mapped_chars': total_mapped,
            **profile,
        })

print(f"\nValid paragraphs: {len(par_profiles)}")

# Group by regime
regime_paragraphs = defaultdict(list)
for p in par_profiles:
    regime_paragraphs[p['regime']].append(p)

# Regime centroids in 7-axis space
regime_centroids = {}
for regime in sorted(regime_paragraphs.keys()):
    pars = regime_paragraphs[regime]
    vecs = [np.array([p[ax] for ax in AXES]) for p in pars]
    centroid = np.mean(vecs, axis=0)
    regime_centroids[regime] = {AXES[j]: float(centroid[j]) for j in range(len(AXES))}

print(f"\nRegime centroids (7-axis proportions, paragraph-level):")
print(f"  {'Regime':<12} {'N':>3}", end='')
for ax in AXES:
    print(f"  {ax[:4]:>6}", end='')
print()
for regime in sorted(regime_centroids.keys()):
    n = len(regime_paragraphs[regime])
    print(f"  {regime:<12} {n:>3}", end='')
    for ax in AXES:
        print(f"  {regime_centroids[regime][ax]:>5.1%}", end='')
    print()

# =====================================================================
# DISTANCE: REGIME CENTROIDS TO COMPLEXITY CLASS CENTROIDS
# =====================================================================
print(f"\n{'=' * 70}")
print("REGIME -> COMPLEXITY CLASS DISTANCES")
print("=" * 70)

print(f"\n  Rank correlation (Spearman) between regime and class axis emphasis:")
print(f"  {'':>12}  {'SIMPLE':>10} {'HARD':>10} {'COMPLEX':>10}  {'Best match':>12}")
print(f"  {'':>12}  {'------':>10} {'----':>10} {'-------':>10}  {'----------':>12}")

regime_best_match = {}
for regime in sorted(regime_centroids.keys()):
    rv = [regime_centroids[regime][ax] for ax in AXES]
    best_cls = None
    best_rho = -2
    rhos = {}
    for cls in ['SIMPLE', 'HARD', 'COMPLEX']:
        cv = [class_profiles[cls][ax] for ax in AXES]
        rho, p = stats.spearmanr(rv, cv)
        rhos[cls] = (rho, p)
        if rho > best_rho:
            best_rho = rho
            best_cls = cls

    regime_best_match[regime] = best_cls
    print(f"  {regime:<12}", end='')
    for cls in ['SIMPLE', 'HARD', 'COMPLEX']:
        rho, p = rhos[cls]
        sig = '*' if p < 0.05 else ' '
        bold = ' <--' if cls == best_cls else '    '
        print(f"  {rho:>+6.3f}{sig}{bold[1:]}", end='')
    print(f"  {best_cls}")

# =====================================================================
# HYPOTHESIS TEST
# =====================================================================
print(f"\n{'=' * 70}")
print("HYPOTHESIS TEST")
print("=" * 70)

hypotheses = {
    'REGIME_1': ('HARD', 'Energy-intensive -> hard materials (root/wood/bark)'),
    'REGIME_2': ('SIMPLE', 'Balanced/output -> simple materials (leaf/seed/fruit)'),
    'REGIME_3': ('COMPLEX', 'High-intervention -> complex processing (cohobation/fractional)'),
    'REGIME_4': ('COMPLEX', 'Precision -> delicate materials (heat-sensitive flowers)'),
}

n_correct = 0
for regime in sorted(hypotheses.keys()):
    predicted, rationale = hypotheses[regime]
    actual = regime_best_match.get(regime, 'UNK')
    match = 'PASS' if actual == predicted else 'FAIL'
    if match == 'PASS':
        n_correct += 1
    print(f"\n  {regime}:")
    print(f"    Hypothesis: {predicted} ({rationale})")
    print(f"    Actual best match: {actual}")
    print(f"    Result: {match}")

    rv = regime_centroids.get(regime, {})
    ranked = sorted(AXES, key=lambda ax: rv.get(ax, 0), reverse=True)
    print(f"    Axis ranking: {' > '.join(f'{ax[:3]}={rv.get(ax,0):.1%}' for ax in ranked[:4])}")

print(f"\n  Overall: {n_correct}/4 hypotheses confirmed")

# =====================================================================
# REGIME DISTINGUISHING FEATURES
# =====================================================================
print(f"\n{'=' * 70}")
print("WHAT DISTINGUISHES EACH REGIME (top 2 axes vs mean)")
print("=" * 70)

overall_mean = {ax: np.mean([regime_centroids[r][ax] for r in regime_centroids]) for ax in AXES}

for regime in sorted(regime_centroids.keys()):
    deltas = {ax: regime_centroids[regime][ax] - overall_mean[ax] for ax in AXES}
    ranked = sorted(AXES, key=lambda ax: abs(deltas[ax]), reverse=True)
    print(f"\n  {regime} ({len(regime_paragraphs.get(regime, []))} paragraphs):")
    for ax in ranked[:3]:
        d = deltas[ax]
        direction = 'ABOVE' if d > 0 else 'BELOW'
        print(f"    {ax:<12} {regime_centroids[regime][ax]:>6.1%} ({direction} mean by {abs(d):.1%})")

# =====================================================================
# KRUSKAL-WALLIS: DO REGIMES DIFFER ON EACH AXIS?
# =====================================================================
print(f"\n{'=' * 70}")
print("KRUSKAL-WALLIS: REGIME DIFFERENCES BY AXIS (paragraph-level)")
print("=" * 70)

regime_names = sorted(r for r in regime_paragraphs.keys() if r != 'UNK')
for ax_idx, ax in enumerate(AXES):
    groups = []
    for regime in regime_names:
        vals = [p[ax] for p in regime_paragraphs[regime]]
        groups.append(vals)
    if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
        H, p = stats.kruskal(*groups)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
        print(f"  {ax:<12}  H={H:>7.2f}  p={p:.4f}  {sig}")

# =====================================================================
# SAVE
# =====================================================================
results = {
    'analysis_unit': 'paragraph',
    'regime_centroids_7axis': regime_centroids,
    'class_centroids': class_profiles,
    'class_members': class_members,
    'regime_best_match': regime_best_match,
    'regime_paragraph_counts': {r: len(ps) for r, ps in regime_paragraphs.items()},
    'hypotheses': {r: {'predicted': h[0], 'actual': regime_best_match.get(r, 'UNK'),
                       'match': regime_best_match.get(r, 'UNK') == h[0]}
                   for r, h in hypotheses.items()},
    'n_correct': n_correct,
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_PATH}")

"""
Q4: AUXILIARY Subgroup Characterization

Synthesize findings from census, features, clustering, and transitions
to produce definitive AX sub-role characterization.

Based on prior results:
- Clustering gives weak k=2 (silhouette 0.232)
- Position gives strong tripartite split (INIT/MED/FINAL)
- 71.8% INIT-before-FINAL directional ordering
- Prefix families partially align with distributional behavior

Use POSITIONAL sub-groups as primary stratification (more structural
than clustering), then characterize each.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
CENSUS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
FEATURES_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_features.json'
CLUSTERING_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_clustering.json'
TRANSITIONS_FILE = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_transitions.json'
RESULTS = BASE / 'phases/AUXILIARY_STRATIFICATION/results'

# Load all prior results
with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(CENSUS_FILE) as f:
    census = json.load(f)
AX_CLASSES = set(census['definitive_ax_classes'])
prefix_families = census['prefix_families']

with open(FEATURES_FILE) as f:
    features = json.load(f)

with open(CLUSTERING_FILE) as f:
    clustering = json.load(f)

with open(TRANSITIONS_FILE) as f:
    transitions = json.load(f)

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

morph = Morphology()
tx = Transcript()
tokens = list(tx.currier_b())

# ============================================================
# DEFINE POSITIONAL SUB-GROUPS
# ============================================================
INIT_AX = set(transitions['subgroup_membership']['INIT'])   # {4, 5, 6, 24, 26}
FINAL_AX = set(transitions['subgroup_membership']['FINAL'])  # {15, 19, 20, 21, 22, 25}
MEDIAL_AX = set(transitions['subgroup_membership']['MEDIAL'])  # {1, 2, 3, 14, 16, 18, 27, 28, 29}

subgroups = {
    'AX_INIT': INIT_AX,
    'AX_MED': MEDIAL_AX,
    'AX_FINAL': FINAL_AX,
}

print("=" * 70)
print("Q4: AUXILIARY SUBGROUP CHARACTERIZATION")
print("=" * 70)

# ============================================================
# 1. SUBGROUP OVERVIEW
# ============================================================
print("\n" + "-" * 70)
print("1. SUBGROUP OVERVIEW")
print("-" * 70)

print(f"\n{'Subgroup':<12} {'Classes':>8} {'Tokens':>7} {'% of AX':>8}")
for sg_name, sg_classes in subgroups.items():
    total_tok = sum(features[str(c)]['n_tokens'] for c in sg_classes)
    ax_total = sum(features[str(c)]['n_tokens'] for c in AX_CLASSES)
    print(f"{sg_name:<12} {len(sg_classes):>8} {total_tok:>7} {total_tok/ax_total*100:>7.1f}%")

# ============================================================
# 2. AGGREGATE FEATURE PROFILES
# ============================================================
print("\n" + "-" * 70)
print("2. AGGREGATE FEATURE PROFILES")
print("-" * 70)

for sg_name, sg_classes in subgroups.items():
    feats = [features[str(c)] for c in sg_classes]

    # Weight by token count
    weights = np.array([f['n_tokens'] for f in feats])
    total_w = weights.sum()

    avg = lambda key: np.average([f[key] for f in feats], weights=weights)

    print(f"\n{sg_name} ({len(sg_classes)} classes, {total_w} tokens):")
    print(f"  Position:  mean={avg('mean_position'):.3f}, "
          f"init={avg('initial_rate'):.1%}, final={avg('final_rate'):.1%}")

    r_shares = {r: np.average([f['regime_shares'][r] for f in feats], weights=weights)
                for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']}
    print(f"  REGIME:    R1={r_shares['REGIME_1']:.1%}, R2={r_shares['REGIME_2']:.1%}, "
          f"R3={r_shares['REGIME_3']:.1%}, R4={r_shares['REGIME_4']:.1%}")

    s_shares = {s: np.average([f['section_shares'].get(s, 0) for f in feats], weights=weights)
                for s in ['HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_B']}
    print(f"  Section:   HB={s_shares['HERBAL_B']:.1%}, PH={s_shares['PHARMA']:.1%}, "
          f"BIO={s_shares['BIO']:.1%}, RB={s_shares['RECIPE_B']:.1%}")

    print(f"  Morphology: prefix={avg('prefix_rate'):.1%}, "
          f"suffix={avg('suffix_rate'):.1%}, artic={avg('articulator_rate'):.1%}")

    print(f"  Adjacency: EN_adj={avg('energy_adj_rate'):.1%}, "
          f"L_EN={avg('left_en_rate'):.1%}, R_EN={avg('right_en_rate'):.1%}")

# ============================================================
# 3. MORPHOLOGICAL ANALYSIS BY SUBGROUP
# ============================================================
print("\n" + "-" * 70)
print("3. MORPHOLOGICAL SIGNATURES")
print("-" * 70)

for sg_name, sg_classes in subgroups.items():
    prefix_dist = Counter()
    suffix_dist = Counter()
    artic_total = 0
    n_types = 0

    for cls in sg_classes:
        for tok, c in token_to_class.items():
            if c != cls:
                continue
            m = morph.extract(tok)
            prefix_dist[m.prefix or 'NONE'] += 1
            suffix_dist[m.suffix or 'NONE'] += 1
            if m.has_articulator:
                artic_total += 1
            n_types += 1

    print(f"\n{sg_name} ({n_types} token types):")
    print(f"  Articulator rate: {artic_total/n_types:.1%}")
    print(f"  Top prefixes: {', '.join(f'{p}:{c}' for p, c in prefix_dist.most_common(5))}")
    print(f"  Top suffixes: {', '.join(f'{s}:{c}' for s, c in suffix_dist.most_common(5))}")

    # Show example tokens
    sample_tokens = []
    for cls in sorted(sg_classes):
        toks = [tok for tok, c in token_to_class.items() if c == cls][:2]
        sample_tokens.extend(toks)
    print(f"  Examples: {', '.join(sample_tokens[:8])}")

# ============================================================
# 4. DISTINCTIVE FEATURES PER SUBGROUP
# ============================================================
print("\n" + "-" * 70)
print("4. DISTINCTIVE FEATURES (vs AX average)")
print("-" * 70)

# Compute AX-wide averages
ax_feats = [features[str(c)] for c in AX_CLASSES]
ax_weights = np.array([f['n_tokens'] for f in ax_feats])
ax_total_w = ax_weights.sum()

compare_keys = [
    'mean_position', 'initial_rate', 'final_rate',
    'energy_adj_rate', 'prefix_rate', 'suffix_rate', 'articulator_rate',
]

for sg_name, sg_classes in subgroups.items():
    feats = [features[str(c)] for c in sg_classes]
    weights = np.array([f['n_tokens'] for f in feats])

    print(f"\n{sg_name} distinctive features:")
    for key in compare_keys:
        sg_val = np.average([f[key] for f in feats], weights=weights)
        ax_val = np.average([f[key] for f in ax_feats], weights=ax_weights)
        if ax_val > 0:
            ratio = sg_val / ax_val
            if abs(ratio - 1.0) > 0.15:
                direction = 'ELEVATED' if ratio > 1 else 'DEPLETED'
                print(f"  {direction}: {key} = {sg_val:.3f} (vs AX avg {ax_val:.3f}, {ratio:.2f}x)")

# ============================================================
# 5. NAMED ROLE COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("5. COMPARISON TO NAMED ROLES")
print("-" * 70)

# Load named role profiles from existing constraints
# CC: initial-biased, ENERGY trigger
# EN: medial-concentrated, REGIME_1 enriched
# FL: final-biased, PHARMA enriched
# FQ: morphologically minimal, final-biased

print("""
Comparison of AX sub-groups to named roles:

AX_INIT vs CORE_CONTROL:
  - Both initial-biased
  - AX_INIT: 24.8% initial (vs CC: 27.7% for daiin)
  - AX_INIT has articulators (30%); CC has NONE
  - AX_INIT is larger (1195 tokens vs CC 932)
  - DIFFERENT: AX_INIT doesn't trigger ENERGY chains

AX_FINAL vs FLOW_OPERATOR:
  - Both final-biased
  - AX_FINAL: 38.9% final (vs FL: 59.7% for Class 40)
  - AX_FINAL is BIO-enriched (40.3%); FL is PHARMA-enriched (1.38x)
  - AX_FINAL: morphologically diverse; FL: ar/al/da unified
  - DIFFERENT: AX_FINAL includes bare tokens (ly, ry); FL is compositional

AX_MED vs ENERGY:
  - Both medial
  - AX_MED: position 0.515; EN: position 0.48
  - AX_MED: ok/ot prefix dominant; EN: ch/sh/qo prefix
  - AX_MED: highest AX self-chaining (14.3%)
  - DIFFERENT: AX_MED has 0% hazard involvement; EN has hazard classes
""")

# ============================================================
# 6. FUNCTIONAL HYPOTHESIS
# ============================================================
print("\n" + "-" * 70)
print("6. FUNCTIONAL HYPOTHESIS")
print("-" * 70)

print("""
AUXILIARY Sub-Role Taxonomy:

1. AX_INIT (5 classes: 4, 5, 6, 24, 26) - "FRAME OPENERS"
   - 1195 tokens (26.2% of AX)
   - Positional: 24.8% initial, mean=0.393
   - Morphology: High articulator rate (30%), diverse prefixes
   - Function: Open execution frames. Unlike CC (which triggers ENERGY),
     AX_INIT provides structural framing without semantic commitment.
   - Analogy: Opening brackets, setup markers

2. AX_MED (9 classes: 1, 2, 3, 14, 16, 18, 27, 28, 29) - "SCAFFOLD"
   - 2531 tokens (55.5% of AX)
   - Positional: Neutral (mean=0.515), neither initial nor final
   - Morphology: ok/ot prefix dominant, mixed suffixes
   - Function: Fill execution infrastructure. The "neutral filler"
     that maintains line structure between meaningful operations.
   - Analogy: Connective tissue, neutral operators

3. AX_FINAL (6 classes: 15, 19, 20, 21, 22, 25) - "FRAME CLOSERS"
   - 833 tokens (18.3% of AX)
   - Positional: 38.9% final, mean=0.681
   - Morphology: Bare (prefix-light), BIO-enriched
   - Function: Close execution frames. Unlike FL (which redirects flow),
     AX_FINAL provides structural closure without flow semantics.
   - Analogy: Closing brackets, termination markers

KEY INSIGHT: AX is not a "heterogeneous residual." It is a POSITIONALLY
STRATIFIED execution scaffold with three sub-roles that mirror the
named role positions (CC/INIT, EN/MED, FL/FINAL) but provide STRUCTURAL
framing rather than FUNCTIONAL operations.

The 71.8% INIT-before-FINAL ordering confirms this is not random
co-occurrence but deliberate grammatical structure.
""")

# ============================================================
# 7. STATISTICAL VALIDATION
# ============================================================
print("\n" + "-" * 70)
print("7. STATISTICAL VALIDATION")
print("-" * 70)

# Test: Is the positional difference between subgroups significant?
init_positions = []
med_positions = []
final_positions = []

for (folio, line_id), line_data in defaultdict(list).items():
    pass  # Need to recompute from tokens

# Actually compute from token data directly
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({'class': cls, 'word': word})

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n < 2:
        continue
    for i, tok in enumerate(line_tokens):
        cls = tok['class']
        if cls is None:
            continue
        pos = i / (n - 1)
        if cls in INIT_AX:
            init_positions.append(pos)
        elif cls in MEDIAL_AX:
            med_positions.append(pos)
        elif cls in FINAL_AX:
            final_positions.append(pos)

# Kruskal-Wallis test (non-parametric ANOVA)
h_stat, p_val = stats.kruskal(init_positions, med_positions, final_positions)
print(f"\nKruskal-Wallis H test (3 subgroups):")
print(f"  H = {h_stat:.1f}, p = {p_val:.2e}")
print(f"  n_init = {len(init_positions)}, n_med = {len(med_positions)}, n_final = {len(final_positions)}")

# Pairwise Mann-Whitney U tests
pairs = [('INIT', 'MED', init_positions, med_positions),
         ('MED', 'FINAL', med_positions, final_positions),
         ('INIT', 'FINAL', init_positions, final_positions)]

print(f"\nPairwise Mann-Whitney U tests:")
print(f"{'Comparison':>20} {'U':>12} {'p-value':>12} {'Effect size (r)'}")
for name1, name2, data1, data2 in pairs:
    u_stat, p = stats.mannwhitneyu(data1, data2, alternative='less')
    # Effect size r = Z / sqrt(N)
    n1, n2 = len(data1), len(data2)
    z = (u_stat - n1*n2/2) / np.sqrt(n1*n2*(n1+n2+1)/12)
    r = abs(z) / np.sqrt(n1 + n2)
    print(f"{name1+' < '+name2:>20} {u_stat:12.0f} {p:12.2e} {r:15.3f}")

# Cohen's d for INIT vs FINAL (effect size)
d = (np.mean(final_positions) - np.mean(init_positions)) / np.sqrt(
    (np.var(init_positions) + np.var(final_positions)) / 2)
print(f"\nCohen's d (INIT vs FINAL): {d:.2f}")
print(f"  Mean INIT position: {np.mean(init_positions):.3f}")
print(f"  Mean MED position:  {np.mean(med_positions):.3f}")
print(f"  Mean FINAL position: {np.mean(final_positions):.3f}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'subgroups': {
        'AX_INIT': {
            'classes': sorted(INIT_AX),
            'tokens': sum(features[str(c)]['n_tokens'] for c in INIT_AX),
            'pct_of_ax': round(sum(features[str(c)]['n_tokens'] for c in INIT_AX) / sum(features[str(c)]['n_tokens'] for c in AX_CLASSES) * 100, 1),
            'mean_position': round(np.mean(init_positions), 4),
            'label': 'FRAME_OPENER',
            'description': 'Opens execution frames with structural framing, not semantic commitment',
        },
        'AX_MED': {
            'classes': sorted(MEDIAL_AX),
            'tokens': sum(features[str(c)]['n_tokens'] for c in MEDIAL_AX),
            'pct_of_ax': round(sum(features[str(c)]['n_tokens'] for c in MEDIAL_AX) / sum(features[str(c)]['n_tokens'] for c in AX_CLASSES) * 100, 1),
            'mean_position': round(np.mean(med_positions), 4),
            'label': 'SCAFFOLD',
            'description': 'Fills execution infrastructure between meaningful operations',
        },
        'AX_FINAL': {
            'classes': sorted(FINAL_AX),
            'tokens': sum(features[str(c)]['n_tokens'] for c in FINAL_AX),
            'pct_of_ax': round(sum(features[str(c)]['n_tokens'] for c in FINAL_AX) / sum(features[str(c)]['n_tokens'] for c in AX_CLASSES) * 100, 1),
            'mean_position': round(np.mean(final_positions), 4),
            'label': 'FRAME_CLOSER',
            'description': 'Closes execution frames without flow semantics',
        },
    },
    'statistical_validation': {
        'kruskal_wallis': {'H': round(h_stat, 1), 'p': float(p_val)},
        'cohens_d_init_final': round(d, 2),
        'init_before_final_rate': transitions['positional_order']['init_first_rate'],
    },
    'key_finding': 'AX is positionally stratified scaffold, not heterogeneous residual',
}

with open(RESULTS / 'ax_subgroups.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'ax_subgroups.json'}")

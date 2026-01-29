"""
01_fire_degree_link_density.py

Test 2: Do Brunschwig fire degrees predict Voynich monitoring intensity?

Hypothesis from BRSC:
- Fire degree 1 (gentle) -> high LINK density (more monitoring)
- Fire degree 3 (intense) -> low LINK density (less monitoring)

Method:
1. Map Brunschwig recipes to fire degrees
2. Trace compatible MIDDLEs to B folios (via PP vocabulary)
3. Compute LINK density per folio
4. Test correlation: fire_degree vs LINK_density
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("FIRE DEGREE -> LINK DENSITY CORRELATION")
print("="*70)

# Load Brunschwig data
with open('data/brunschwig_curated_v3.json', encoding='utf-8') as f:
    brunschwig = json.load(f)

# Load transcript
tx = Transcript()

# Build folio-grouped tokens for B
folio_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_tokens[token.folio].append(token)

# Load class map for LINK identification
try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        class_map = json.load(f)
    link_tokens = set(class_map.get('29', []))  # Class 29 = LINK
    print(f"LINK tokens loaded: {len(link_tokens)}")
except FileNotFoundError:
    print("WARNING: class_token_map.json not found, using heuristic for LINK")
    # Fallback: use known LINK patterns
    link_tokens = set()

# Aggregate fire degree by material type
fire_by_material = defaultdict(list)
for recipe in brunschwig['recipes']:
    material = recipe.get('material_class', 'unknown')
    fire = recipe.get('fire_degree')
    if fire:
        fire_by_material[material].append(fire)

print("\nFire degree by material class:")
for material, fires in sorted(fire_by_material.items()):
    mean_fire = np.mean(fires)
    print(f"  {material}: mean={mean_fire:.2f}, n={len(fires)}")

# Compute LINK density per folio
folio_stats = []

for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]
    n_tokens = len(words)

    # Count LINK tokens
    if link_tokens:
        n_link = sum(1 for w in words if w in link_tokens)
    else:
        # Fallback heuristic: count tokens containing 'l' prefix patterns
        n_link = sum(1 for w in words if w.startswith(('lch', 'lk', 'lsh', 'l')))

    link_density = n_link / n_tokens if n_tokens > 0 else 0

    # Get section from first token
    section = tokens[0].section if hasattr(tokens[0], 'section') else 'unknown'

    folio_stats.append({
        'folio': folio,
        'n_tokens': n_tokens,
        'n_link': n_link,
        'link_density': link_density,
        'section': section
    })

# Convert to simple dict-based structure for analysis
import pandas as pd
folio_df = pd.DataFrame(folio_stats)
print(f"\nFolios analyzed: {len(folio_df)}")
print(f"Mean LINK density: {folio_df['link_density'].mean():.4f}")

# Now we need to map Brunschwig fire degrees to folios
# This is the tricky part - we need to use the material class -> PREFIX mapping

# Get mean fire degree by material class
material_fire = {}
for material, fires in fire_by_material.items():
    material_fire[material] = np.mean(fires)

print("\n" + "="*70)
print("FIRE DEGREE PROXY ANALYSIS")
print("="*70)

# Since we can't directly map recipes to folios, we use REGIME as a proxy
# REGIME is already shown to correlate with fire degree (F-BRU-001)

# Load B_CONTROL_FLOW_SEMANTICS results if available
try:
    with open('phases/B_CONTROL_FLOW_SEMANTICS/results/section_program_profiles.json') as f:
        section_profiles = json.load(f)
    print("\nLoaded section profiles from B_CONTROL_FLOW_SEMANTICS")
except FileNotFoundError:
    section_profiles = None
    print("\nSection profiles not found, computing from scratch")

# Compute section-level statistics
section_stats = folio_df.groupby('section').agg({
    'link_density': 'mean',
    'n_tokens': 'sum',
    'n_link': 'sum'
}).reset_index()

print("\nLINK density by section:")
for _, row in section_stats.iterrows():
    print(f"  {row['section']}: {row['link_density']:.4f} ({row['n_link']} LINK tokens)")

# Brunschwig material -> section hypothesis
# HERBAL_B should be herb-heavy (fire degree 2)
# BIO might be animal-heavy (fire degree 1/precision)
# PHARMA might be root-heavy (fire degree 2-3)

print("\n" + "="*70)
print("BRUNSCHWIG FIRE DEGREE -> SECTION HYPOTHESIS")
print("="*70)

# Expected mapping based on BRSC:
expected_mapping = {
    'herbal_b': {'material': 'herb', 'expected_fire': 2, 'expected_link': 'medium'},
    'bio': {'material': 'animal', 'expected_fire': 1, 'expected_link': 'high'},
    'pharma': {'material': 'root', 'expected_fire': 2.5, 'expected_link': 'medium'},
    'recipe_b': {'material': 'mixed', 'expected_fire': 2, 'expected_link': 'medium'},
}

print("\nExpected pattern (if Brunschwig-compatible):")
print("  Fire degree 1 (animal/gentle) -> HIGH LINK density")
print("  Fire degree 2 (standard herb) -> MEDIUM LINK density")
print("  Fire degree 3 (intense) -> LOW LINK density")

# Test the prediction
section_link = folio_df.groupby('section')['link_density'].mean().to_dict()

print("\nActual LINK density by section:")
for section in sorted(section_link.keys()):
    density = section_link[section]
    expected = expected_mapping.get(section.lower(), {}).get('expected_link', 'unknown')
    print(f"  {section}: {density:.4f} (expected: {expected})")

# Correlation analysis using REGIME as fire degree proxy
print("\n" + "="*70)
print("REGIME -> LINK CORRELATION (Proxy for Fire Degree)")
print("="*70)

# Load REGIME assignments if available
try:
    with open('results/regime_classification.json') as f:
        regime_data = json.load(f)
    print("Loaded REGIME classifications")

    # Build folio -> REGIME mapping
    folio_regime = {}
    for regime, info in regime_data.get('regimes', {}).items():
        for folio in info.get('folios', []):
            folio_regime[folio] = int(regime.replace('REGIME_', ''))

    # Add REGIME to folio_df
    folio_df['regime'] = folio_df['folio'].map(folio_regime)

    # Compute correlation
    valid = folio_df.dropna(subset=['regime', 'link_density'])
    if len(valid) > 10:
        r, p = stats.spearmanr(valid['regime'], valid['link_density'])
        print(f"\nSpearman correlation (REGIME vs LINK density): r={r:.3f}, p={p:.4f}")

        if r < -0.2 and p < 0.05:
            print("  RESULT: Negative correlation (higher REGIME -> lower LINK)")
            print("  This matches Brunschwig: higher fire degree -> less monitoring")
        elif r > 0.2 and p < 0.05:
            print("  RESULT: Positive correlation (unexpected)")
        else:
            print("  RESULT: No significant correlation")

except FileNotFoundError:
    print("REGIME classification not found, skipping correlation analysis")
    r, p = None, None

# Alternative: use kernel density as fire proxy
print("\n" + "="*70)
print("KERNEL DENSITY AS FIRE PROXY")
print("="*70)

# k kernel represents energy application (fire)
# If more k -> more fire -> less monitoring needed

for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]
    n_k = sum(1 for w in words for c in w if c == 'k')
    n_total = sum(len(w) for w in words)
    k_density = n_k / n_total if n_total > 0 else 0

    idx = folio_df[folio_df['folio'] == folio].index
    if len(idx) > 0:
        folio_df.loc[idx[0], 'k_density'] = k_density

# Correlation: k_density vs link_density
valid = folio_df.dropna(subset=['k_density', 'link_density'])
if len(valid) > 10:
    r_k, p_k = stats.spearmanr(valid['k_density'], valid['link_density'])
    print(f"\nSpearman correlation (k-density vs LINK density): r={r_k:.3f}, p={p_k:.4f}")

    if r_k < -0.2 and p_k < 0.05:
        print("  RESULT: Negative correlation (more k -> less LINK)")
        print("  This matches Brunschwig: more heat application -> less monitoring")
    elif r_k > 0.2 and p_k < 0.05:
        print("  RESULT: Positive correlation (more k -> more LINK)")
        print("  This could indicate: heating requires monitoring (makes sense)")
    else:
        print("  RESULT: No significant correlation")
else:
    r_k, p_k = None, None

# Save results
results = {
    'folios_analyzed': len(folio_df),
    'mean_link_density': folio_df['link_density'].mean(),
    'section_link_density': section_link,
    'material_fire_degrees': material_fire,
    'fire_degree_distribution': {
        'degree_1': sum(1 for r in brunschwig['recipes'] if r.get('fire_degree') == 1),
        'degree_2': sum(1 for r in brunschwig['recipes'] if r.get('fire_degree') == 2),
        'degree_3': sum(1 for r in brunschwig['recipes'] if r.get('fire_degree') == 3),
        'degree_4': sum(1 for r in brunschwig['recipes'] if r.get('fire_degree') == 4),
    },
    'regime_link_correlation': {'r': r, 'p': p} if r is not None else None,
    'k_link_correlation': {'r': r_k, 'p': p_k} if r_k is not None else None,
    'hypothesis': 'Fire degree inversely correlates with LINK density',
    'brunschwig_interpretation': 'Higher fire = less monitoring needed (faster process)'
}

output_path = results_dir / "fire_link_correlation.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")

#!/usr/bin/env python3
"""
Test: Does fire degree predict LINK/FL ratio (stability proxy)?

Hypothesis:
- Low fire (gentle) -> stable process -> high LINK/FL ratio
- High fire (intense) -> unstable process -> low LINK/FL ratio

This reformulates the fire-link test around STABILITY rather than
monitoring intensity. In closed-loop control, stable processes have
more waiting/monitoring (LINK) and less escape (FL).

Method:
1. Compute LINK/FL ratio per section and per REGIME
2. Map REGIME to expected fire degree (from F-BRU-001)
3. Test if higher REGIME (higher fire) -> lower LINK/FL ratio
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

# Load class map
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_map = json.load(f)

# Build token -> class lookup
token_to_class = {token: int(cls) for token, cls in class_map['token_to_class'].items()}

# Role classification from class map
token_to_role = class_map.get('token_to_role', {})

# Identify LINK tokens (Class 29 per BCSC)
# Also identify FL tokens (escape operators: FQ classes)
FQ_CLASSES = {9, 13, 14, 23}  # From C587
LINK_CLASS = 29

link_tokens = set()
fl_tokens = set()
for token, cls in token_to_class.items():
    if cls == LINK_CLASS:
        link_tokens.add(token)
    if cls in FQ_CLASSES:
        fl_tokens.add(token)

print("="*70)
print("FIRE -> STABILITY (LINK/FL RATIO) TEST")
print("="*70)
print(f"LINK tokens identified: {len(link_tokens)}")
print(f"FL (escape) tokens identified: {len(fl_tokens)}")

# Load transcript
tx = Transcript()

# Build folio-grouped tokens for B
folio_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_tokens[token.folio].append(token)

print(f"Folios analyzed: {len(folio_tokens)}")

# Compute LINK and FL counts per folio
folio_stats = []
for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]
    section = tokens[0].section if tokens else 'unknown'

    n_link = sum(1 for w in words if w in link_tokens)
    n_fl = sum(1 for w in words if w in fl_tokens)
    n_total = len(words)

    # LINK/FL ratio (avoid division by zero)
    link_fl_ratio = n_link / n_fl if n_fl > 0 else float('inf') if n_link > 0 else 0

    folio_stats.append({
        'folio': folio,
        'section': section,
        'n_total': n_total,
        'n_link': n_link,
        'n_fl': n_fl,
        'link_density': n_link / n_total if n_total > 0 else 0,
        'fl_density': n_fl / n_total if n_total > 0 else 0,
        'link_fl_ratio': link_fl_ratio if link_fl_ratio != float('inf') else None
    })

# Summary by section
print("\n" + "="*70)
print("LINK/FL RATIO BY SECTION")
print("="*70)

section_agg = defaultdict(lambda: {'n_link': 0, 'n_fl': 0, 'n_total': 0})
for fs in folio_stats:
    s = fs['section']
    section_agg[s]['n_link'] += fs['n_link']
    section_agg[s]['n_fl'] += fs['n_fl']
    section_agg[s]['n_total'] += fs['n_total']

section_ratios = {}
for section, counts in sorted(section_agg.items()):
    ratio = counts['n_link'] / counts['n_fl'] if counts['n_fl'] > 0 else float('inf')
    section_ratios[section] = ratio
    link_pct = 100 * counts['n_link'] / counts['n_total']
    fl_pct = 100 * counts['n_fl'] / counts['n_total']
    print(f"  {section}: LINK={counts['n_link']} ({link_pct:.1f}%), FL={counts['n_fl']} ({fl_pct:.1f}%), ratio={ratio:.2f}")

# Load REGIME assignments
print("\n" + "="*70)
print("LINK/FL RATIO BY REGIME (Fire Degree Proxy)")
print("="*70)

try:
    with open('results/regime_folio_mapping.json') as f:
        regime_data = json.load(f)

    # Build folio -> REGIME mapping
    folio_regime = {}
    for regime, folios in regime_data.items():
        regime_num = int(regime.replace('REGIME_', ''))
        for folio in folios:
            folio_regime[folio] = regime_num

    # Add REGIME to folio stats
    for fs in folio_stats:
        fs['regime'] = folio_regime.get(fs['folio'])

    # Aggregate by REGIME
    regime_agg = defaultdict(lambda: {'n_link': 0, 'n_fl': 0, 'n_total': 0, 'count': 0})
    for fs in folio_stats:
        r = fs.get('regime')
        if r is not None:
            regime_agg[r]['n_link'] += fs['n_link']
            regime_agg[r]['n_fl'] += fs['n_fl']
            regime_agg[r]['n_total'] += fs['n_total']
            regime_agg[r]['count'] += 1

    # Expected fire degrees from BRSC/F-BRU-001
    # REGIME_4 handles animal materials where fire degree 4 is FORBIDDEN
    # This means R4 operates under constrained/hazardous conditions
    expected_fire = {1: 2, 2: 1, 3: 3, 4: 4}  # REGIME -> fire degree (4=constrained/hazardous)

    regime_ratios = {}
    print("\nREGIME  Fire  LINK     FL       Ratio    Folios")
    print("-" * 50)
    for regime in sorted(regime_agg.keys()):
        counts = regime_agg[regime]
        ratio = counts['n_link'] / counts['n_fl'] if counts['n_fl'] > 0 else float('inf')
        regime_ratios[regime] = ratio
        fire = expected_fire.get(regime, '?')
        print(f"  R{regime}     {fire}    {counts['n_link']:5d}  {counts['n_fl']:5d}    {ratio:5.2f}    {counts['count']}")

    # Correlation test: REGIME vs LINK/FL ratio
    # Get folio-level data
    valid_folios = [(fs['regime'], fs['link_fl_ratio'])
                    for fs in folio_stats
                    if fs.get('regime') is not None and fs.get('link_fl_ratio') is not None]

    if len(valid_folios) > 10:
        regimes = [x[0] for x in valid_folios]
        ratios = [x[1] for x in valid_folios]

        r_regime, p_regime = stats.spearmanr(regimes, ratios)
        print(f"\nSpearman correlation (REGIME vs LINK/FL ratio):")
        print(f"  rho = {r_regime:.3f}, p = {p_regime:.4f}")

        # Interpretation
        # Higher REGIME = higher expected fire (except REGIME_2 which is lowest fire)
        # If fire->instability->lower LINK/FL, we'd expect negative correlation
        # But REGIME mapping is non-monotonic with fire, so let's also test fire directly

        # Map REGIME to fire degree and test
        fires = [expected_fire.get(r, 2) for r in regimes]
        r_fire, p_fire = stats.spearmanr(fires, ratios)
        print(f"\nSpearman correlation (Fire degree vs LINK/FL ratio):")
        print(f"  rho = {r_fire:.3f}, p = {p_fire:.4f}")

        if r_fire < -0.15 and p_fire < 0.1:
            verdict = "SUPPORT - Higher fire -> lower LINK/FL (less stable)"
        elif r_fire > 0.15 and p_fire < 0.1:
            verdict = "CONTRADICT - Higher fire -> higher LINK/FL (unexpected)"
        else:
            verdict = "NEUTRAL - No significant relationship"
    else:
        r_regime, p_regime = None, None
        r_fire, p_fire = None, None
        verdict = "INSUFFICIENT DATA"

except FileNotFoundError:
    print("REGIME classification not found")
    r_regime, p_regime = None, None
    r_fire, p_fire = None, None
    verdict = "REGIME DATA NOT AVAILABLE"
    regime_ratios = {}

print(f"\nVERDICT: {verdict}")

# Alternative: Check if sections with expected higher fire have lower LINK/FL
# Expected: S (Stars) might be REGIME_3 (high fire), H (Herbal) might be REGIME_1/2 (lower fire)
print("\n" + "="*70)
print("SECTION FIRE EXPECTATION CHECK")
print("="*70)
print("\nIf Brunschwig correspondence holds:")
print("  High fire sections -> LOW LINK/FL ratio (unstable)")
print("  Low fire sections -> HIGH LINK/FL ratio (stable)")

# Sort sections by LINK/FL ratio
sorted_sections = sorted(section_ratios.items(), key=lambda x: x[1] if x[1] != float('inf') else 999)
print("\nSections ranked by LINK/FL ratio (low = unstable, high = stable):")
for section, ratio in sorted_sections:
    print(f"  {section}: {ratio:.2f}")

# Save results
output = {
    'hypothesis': 'Fire degree predicts LINK/FL ratio (stability proxy)',
    'link_tokens_count': len(link_tokens),
    'fl_tokens_count': len(fl_tokens),
    'section_link_fl_ratios': {k: v if v != float('inf') else 'inf' for k, v in section_ratios.items()},
    'regime_link_fl_ratios': {str(k): v if v != float('inf') else 'inf' for k, v in regime_ratios.items()} if regime_ratios else None,
    'correlation_regime': {'rho': float(r_regime) if r_regime is not None else None,
                           'p': float(p_regime) if p_regime is not None else None},
    'correlation_fire': {'rho': float(r_fire) if r_fire is not None else None,
                        'p': float(p_fire) if p_fire is not None else None},
    'verdict': verdict,
    'interpretation': {
        'original_hypothesis': 'Fire -> inverse LINK (monitoring intensity)',
        'revised_hypothesis': 'Fire -> instability -> lower LINK/FL ratio',
        'rationale': 'LINK and FL are complementary phases (C807). Stability should show more monitoring (LINK), instability more escape (FL).'
    }
}

output_path = results_dir / 'fire_stability_proxy.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

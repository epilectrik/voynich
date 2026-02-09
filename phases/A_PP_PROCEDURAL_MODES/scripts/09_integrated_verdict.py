#!/usr/bin/env python3
"""
Test 9: Integrated Verdict

Synthesizes results from all tests to produce final phase verdict.
"""

import sys
import io
from pathlib import Path
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

results_dir = Path(__file__).parent.parent / 'results'

print("="*70)
print("A_PP_PROCEDURAL_MODES - INTEGRATED VERDICT")
print("="*70)

# Load all results
test_results = {}
test_files = [
    ('cluster_validity', '01_cluster_validity'),
    ('b_side_correlation', '02_b_side_correlation'),
    ('vocabulary_discrimination', '03_vocabulary_discrimination'),
    ('section_generalization', '04_section_generalization'),
    ('material_class_compatibility', '05_material_class_compatibility'),
]

for test_name, file_prefix in test_files:
    result_file = results_dir / f'{test_name}.json'
    if result_file.exists():
        with open(result_file) as f:
            test_results[test_name] = json.load(f)
        print(f"  Loaded: {test_name}")
    else:
        print(f"  Missing: {test_name}")

print()

# =========================================================================
# Summarize individual test results
# =========================================================================
print("="*70)
print("INDIVIDUAL TEST VERDICTS")
print("="*70)

verdicts = {}

# Test 1: Cluster Validity
if 'cluster_validity' in test_results:
    v = test_results['cluster_validity'].get('verdict', 'UNKNOWN')
    sil = test_results['cluster_validity'].get('silhouette_scores', {}).get('3', 0)
    stab = test_results['cluster_validity'].get('bootstrap_stability', 0)
    verdicts['cluster_validity'] = v
    print(f"\n1. Cluster Validity: {v}")
    print(f"   Silhouette (k=3): {sil:.3f}")
    print(f"   Bootstrap stability: {stab:.3f}")

# Test 2: B-Side Correlation
if 'b_side_correlation' in test_results:
    v = test_results['b_side_correlation'].get('verdict', 'UNKNOWN')
    verdicts['b_side_correlation'] = v
    print(f"\n2. B-Side Correlation: {v}")

# Test 3: Vocabulary Discrimination
if 'vocabulary_discrimination' in test_results:
    v = test_results['vocabulary_discrimination'].get('verdict', 'UNKNOWN')
    p_val = test_results['vocabulary_discrimination'].get('permutation_p_value', 1)
    jaccard = test_results['vocabulary_discrimination'].get('avg_jaccard', 0)
    verdicts['vocabulary_discrimination'] = v
    print(f"\n3. Vocabulary Discrimination: {v}")
    print(f"   Permutation p-value: {p_val:.4f}")
    print(f"   Average Jaccard: {jaccard:.3f}")

# Test 4: Section Generalization
if 'section_generalization' in test_results:
    v = test_results['section_generalization'].get('verdict', 'UNKNOWN')
    verdicts['section_generalization'] = v
    print(f"\n4. Section Generalization: {v}")

# Test 5: Material Class Compatibility
if 'material_class_compatibility' in test_results:
    v = test_results['material_class_compatibility'].get('verdict', 'UNKNOWN')
    c642 = test_results['material_class_compatibility'].get('c642_compatibility', 'UNKNOWN')
    verdicts['material_class_compatibility'] = v
    print(f"\n5. Material Class Compatibility: {v}")
    print(f"   C642 compatibility: {c642}")

# =========================================================================
# Compute overall verdict
# =========================================================================
print("\n" + "="*70)
print("OVERALL VERDICT")
print("="*70)

# Count verdicts
confirmed = sum(1 for v in verdicts.values() if v == 'CONFIRMED')
support = sum(1 for v in verdicts.values() if v in ['SUPPORT', 'PARTIAL'])
not_supported = sum(1 for v in verdicts.values() if v == 'NOT SUPPORTED')
conflict = sum(1 for v in verdicts.values() if v == 'CONFLICT')

print(f"\nVerdict counts:")
print(f"  CONFIRMED: {confirmed}")
print(f"  SUPPORT/PARTIAL: {support}")
print(f"  NOT SUPPORTED: {not_supported}")
print(f"  CONFLICT: {conflict}")

# Determine overall
if conflict > 0:
    overall = "CONFLICT"
    tier = "REQUIRES RESOLUTION"
elif confirmed >= 3:
    overall = "STRONG"
    tier = "Tier 2 (structural)"
elif confirmed >= 2 or confirmed + support >= 4:
    overall = "MODERATE"
    tier = "Tier 2 (structural) / Tier 3 (interpretation)"
elif confirmed >= 1 or support >= 2:
    overall = "WEAK"
    tier = "Tier 3 (interpretation only)"
else:
    overall = "NEGATIVE"
    tier = "No constraint"

print(f"\n{'='*50}")
print(f"OVERALL VERDICT: {overall}")
print(f"RECOMMENDED TIER: {tier}")
print(f"{'='*50}")

# =========================================================================
# Key findings summary
# =========================================================================
print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

findings = []

if 'cluster_validity' in test_results:
    sil = test_results['cluster_validity'].get('silhouette_scores', {}).get('3', 0)
    if sil > 0.25:
        findings.append(f"Three clusters have meaningful separation (silhouette={sil:.3f})")

if 'vocabulary_discrimination' in test_results:
    exclusive = test_results['vocabulary_discrimination'].get('exclusive_counts', {})
    total_exclusive = sum(int(v) for v in exclusive.values())
    if total_exclusive > 20:
        findings.append(f"Clusters have {total_exclusive} exclusive MIDDLEs (distinctive vocabulary)")

if 'material_class_compatibility' in test_results:
    c642 = test_results['material_class_compatibility'].get('c642_compatibility', '')
    if 'COMPATIBLE' in c642:
        findings.append("Material class mixing persists across clusters (C642 compatible)")

for i, finding in enumerate(findings, 1):
    print(f"\n{i}. {finding}")

# =========================================================================
# Constraint recommendation
# =========================================================================
print("\n" + "="*70)
print("CONSTRAINT RECOMMENDATION")
print("="*70)

if overall in ['STRONG', 'MODERATE']:
    print("""
PROPOSED CONSTRAINT: C895 - A PP Procedural Mode Clustering

Statement:
  Section H A folios cluster into 3 procedural modes by PP role composition:
  - Mode 1: HIGH CLOSURE + HIGH ESCAPE (output/hazard procedures)
  - Mode 2: HIGH CORE (pure processing procedures)
  - Mode 3: HIGH CROSS-REF (cross-referencing procedures)

  Clusters have distinctive MIDDLE vocabularies (exclusive terms per mode).
  Material class mixing persists across all modes (C642 compatible).

Tier: 2 (structure) / 3 (interpretation for mode labels)

Provenance:
  phases/A_PP_PROCEDURAL_MODES/

Related:
  - C642: Material class mixing (BOUNDING - modes are orthogonal to material)
  - C888: Section-specific architecture (EXTENDS to within-section)
  - C737: B-coverage clustering (ORTHOGONAL dimension)
""")
else:
    print("""
No constraint recommended.

The clustering structure exists but lacks:
- Sufficient validation (silhouette, stability)
- B-side operational correlation
- Cross-section generalization

Further investigation needed before constraint formation.
""")

# =========================================================================
# Save final results
# =========================================================================
output = {
    'phase': 'A_PP_PROCEDURAL_MODES',
    'date': '2026-01-30',
    'tests_run': list(test_results.keys()),
    'individual_verdicts': verdicts,
    'counts': {
        'confirmed': confirmed,
        'support': support,
        'not_supported': not_supported,
        'conflict': conflict,
    },
    'overall_verdict': overall,
    'recommended_tier': tier,
    'key_findings': findings,
}

output_path = results_dir / 'integrated_verdict.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nFinal results saved to {output_path}")

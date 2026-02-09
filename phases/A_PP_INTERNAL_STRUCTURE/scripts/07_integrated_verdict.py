#!/usr/bin/env python3
"""
Test 7: Integrated Verdict

Synthesizes results from all A_PP_INTERNAL_STRUCTURE tests.
"""

import sys
import io
from pathlib import Path
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

results_dir = Path(__file__).parent.parent / 'results'

print("="*70)
print("A_PP_INTERNAL_STRUCTURE - INTEGRATED VERDICT")
print("="*70)

# Load all results
test_results = {}
test_files = [
    ('pp_positional_preferences', '01'),
    ('pp_network_topology', '02'),
    ('with_without_ri_comparison', '04'),
    ('pp_gradient_analysis', '06'),
]

for test_name, num in test_files:
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
findings = []

# Test 1: Positional Preferences
if 'pp_positional_preferences' in test_results:
    r = test_results['pp_positional_preferences']
    v = r.get('verdict', 'UNKNOWN')
    verdicts['positional_preferences'] = v
    n_sig = r.get('n_middles_significant', 0)
    n_total = r.get('n_middles_tested', 1)
    ks_p = r.get('overall_ks_p', 1)
    print(f"\n1. Positional Preferences: {v}")
    print(f"   MIDDLEs with significant bias: {n_sig}/{n_total} ({100*n_sig/n_total:.1f}%)")
    print(f"   Overall KS test: p={ks_p:.4f}")

    if v in ['CONFIRMED', 'SUPPORT']:
        top_biased = r.get('top_biased_middles', [])[:3]
        if top_biased:
            findings.append(f"PP has positional preferences (e.g., {top_biased[0]['middle']} at position {top_biased[0]['mean_pos']:.2f})")

# Test 2: Network Topology
if 'pp_network_topology' in test_results:
    r = test_results['pp_network_topology']
    v = r.get('verdict', 'UNKNOWN')
    verdicts['network_topology'] = v
    cv = r.get('cv_degree', 0)
    print(f"\n2. Network Topology: {v}")
    print(f"   Degree CV: {cv:.2f}")
    print(f"   Nodes: {r.get('n_connected', 0)}, Edges: {r.get('n_edges', 0)}")

    if v in ['CONFIRMED', 'SUPPORT']:
        top_hubs = r.get('top_hubs', [])[:3]
        if top_hubs:
            hub_names = [h['middle'] for h in top_hubs]
            findings.append(f"PP network has hub structure (top hubs: {', '.join(hub_names)})")

# Test 4: WITH-RI vs WITHOUT-RI
if 'with_without_ri_comparison' in test_results:
    r = test_results['with_without_ri_comparison']
    v = r.get('verdict', 'UNKNOWN')
    verdicts['with_without_ri'] = v
    jaccard = r.get('jaccard_middles', 0)
    chi_p = r.get('chi_square_p', 1)
    print(f"\n4. WITH-RI vs WITHOUT-RI: {v}")
    print(f"   MIDDLE Jaccard: {jaccard:.3f}")
    print(f"   PREFIX chi-square p: {chi_p:.6f}")

    if v in ['CONFIRMED', 'SUPPORT']:
        findings.append(f"WITH-RI and WITHOUT-RI lines have different PP profiles (Jaccard={jaccard:.3f})")

# Test 6: Gradient Analysis
if 'pp_gradient_analysis' in test_results:
    r = test_results['pp_gradient_analysis']
    v = r.get('verdict', 'UNKNOWN')
    verdicts['gradient_analysis'] = v
    var_explained = r.get('variance_explained', [0])
    sec_p = r.get('section_separation_pc1_p', 1)
    print(f"\n6. Gradient Analysis: {v}")
    print(f"   PC1 variance: {100*var_explained[0]:.1f}%")
    print(f"   Section separation p: {sec_p:.4f}")

    if sec_p < 0.05:
        findings.append(f"PP variation is primarily section-driven (PC1 separates H/P, p={sec_p:.4f})")

# =========================================================================
# Compute overall verdict
# =========================================================================
print("\n" + "="*70)
print("OVERALL VERDICT")
print("="*70)

confirmed = sum(1 for v in verdicts.values() if v == 'CONFIRMED')
support = sum(1 for v in verdicts.values() if v == 'SUPPORT')
not_supported = sum(1 for v in verdicts.values() if v == 'NOT SUPPORTED')

print(f"\nVerdict counts:")
print(f"  CONFIRMED: {confirmed}")
print(f"  SUPPORT: {support}")
print(f"  NOT SUPPORTED: {not_supported}")

# Determine overall
if confirmed >= 2:
    overall = "STRONG"
    tier = "Tier 2 (structural)"
elif confirmed >= 1 or confirmed + support >= 3:
    overall = "MODERATE"
    tier = "Tier 2 (structural)"
elif support >= 2:
    overall = "WEAK"
    tier = "Tier 3 (interpretation)"
else:
    overall = "NEGATIVE"
    tier = "No constraint"

print(f"\n{'='*50}")
print(f"OVERALL VERDICT: {overall}")
print(f"RECOMMENDED TIER: {tier}")
print(f"{'='*50}")

# =========================================================================
# Key findings
# =========================================================================
print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

for i, finding in enumerate(findings, 1):
    print(f"\n{i}. {finding}")

if not findings:
    print("\nNo significant structural findings.")

# =========================================================================
# Constraint recommendation
# =========================================================================
print("\n" + "="*70)
print("CONSTRAINT RECOMMENDATION")
print("="*70)

if overall in ['STRONG', 'MODERATE']:
    print("""
PROPOSED CONSTRAINT: C896 - A PP Internal Structure

Statement:
  Currier A PP (procedural payload) vocabulary has internal organization:
""")
    for finding in findings:
        print(f"  - {finding}")

    print("""
Tier: 2 (structure)

Provenance:
  phases/A_PP_INTERNAL_STRUCTURE/

Related:
  - C234: A token position-freedom (REFINED - PP has some positional preferences)
  - C728: PP co-occurrence non-random (EXTENDED - network hub structure)
  - C888: Section-specific architecture (CONFIRMED - gradient is section-driven)
""")
else:
    print("""
No constraint recommended.

The tests found limited evidence of PP internal structure beyond
what's already captured by existing constraints (C234, C728, C888).

PP appears to be:
- Largely position-free (confirming C234)
- Co-occurrence governed by C475 incompatibility (confirming C728)
- Variation primarily driven by section (confirming C888)
""")

# =========================================================================
# Save results
# =========================================================================
output = {
    'phase': 'A_PP_INTERNAL_STRUCTURE',
    'date': '2026-01-30',
    'tests_run': list(test_results.keys()),
    'individual_verdicts': verdicts,
    'counts': {
        'confirmed': confirmed,
        'support': support,
        'not_supported': not_supported,
    },
    'overall_verdict': overall,
    'recommended_tier': tier,
    'key_findings': findings,
}

output_path = results_dir / 'integrated_verdict.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nFinal results saved to {output_path}")

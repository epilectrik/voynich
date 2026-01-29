"""
T5: Routing Topology Synthesis

Combine findings from T1-T4 to produce overall verdict:
- Does the A->B pipeline create meaningful operational differentiation?
- Is the manuscript a genuine conditional reference system?
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

print("=" * 70)
print("T5: A-RECORD B-ROUTING TOPOLOGY SYNTHESIS")
print("=" * 70)

results_dir = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results'

# Load all results
with open(results_dir / 't1_viability_profiles.json') as f:
    t1 = json.load(f)

with open(results_dir / 't2_clustering.json') as f:
    t2 = json.load(f)

with open(results_dir / 't3_pp_breadth.json') as f:
    t3 = json.load(f)

with open(results_dir / 't4_specificity.json') as f:
    t4 = json.load(f)

print("\n" + "=" * 70)
print("HYPOTHESIS EVALUATION:")
print("=" * 70)

# H1: A-records cluster by B-viability profile
h1_silhouette = t2.get('best_silhouette', 0)
h1_pass = h1_silhouette > 0.3  # Reasonable clustering threshold

print(f"\nH1 (Clustering): silhouette = {h1_silhouette:.3f}")
print(f"    Verdict: {'PASS' if h1_pass else 'FAIL'} (threshold: 0.3)")

# H2: Clusters are sharp
h2_ratio = t2.get('distance_ratio', 0)
h2_p = t2.get('mannwhitney_p', 1)
h2_pass = h2_ratio > 1.5 and h2_p < 0.05

print(f"\nH2 (Sharpness): between/within ratio = {h2_ratio:.2f}x, p = {h2_p:.4f}")
print(f"    Verdict: {'PASS' if h2_pass else 'FAIL'} (threshold: ratio > 1.5, p < 0.05)")

# H3: PP count predicts breadth (negative correlation)
h3_rho = t3.get('correlation', {}).get('spearman_rho', 0)
h3_p = t3.get('correlation', {}).get('p_value', 1)
h3_pass = h3_rho < -0.3 and h3_p < 0.001

print(f"\nH3 (PP->Breadth): rho = {h3_rho:.3f}, p = {h3_p:.4e}")
print(f"    Verdict: {'PASS' if h3_pass else 'FAIL'} (threshold: rho < -0.3, p < 0.001)")

# H4: >20% with >2x lift
h4_pct = t4.get('high_lift_pct', 0)
h4_pass = h4_pct >= 20

print(f"\nH4 (Specificity): {h4_pct:.1f}% with >2x lift")
print(f"    Verdict: {'PASS' if h4_pass else 'FAIL'} (threshold: >= 20%)")

# Overall synthesis
passed = sum([h1_pass, h2_pass, h3_pass, h4_pass])
total = 4

print("\n" + "=" * 70)
print("OVERALL SYNTHESIS:")
print("=" * 70)

print(f"\n  Hypotheses passed: {passed}/{total}")

# Key statistics
filtering_rate = t1.get('filtering_rate', 0)
narrow_records = t1.get('narrow_records', 0)
n_records = t1.get('n_a_records', 1)
narrow_pct = narrow_records / n_records * 100

print(f"\n  Key statistics:")
print(f"    Mean filtering rate: {filtering_rate*100:.1f}%")
print(f"    Narrow records (<10 viable): {narrow_pct:.1f}%")
print(f"    Best clustering k: {t2.get('best_k', 'N/A')}")

# Interpretation
print("\n" + "=" * 70)
print("INTERPRETATION:")
print("=" * 70)

if passed >= 3:
    verdict = "CONDITIONAL REFERENCE SYSTEM VALIDATED"
    tier = "Upgrade Section 0.E to Tier 2"
    interpretation = """
The A->AZC->B pipeline creates genuine operational differentiation:
- A-records cluster meaningfully by B-viability profile
- PP vocabulary creates predictable filtering
- Specific A-records route to specific B-folio subsets
- The manuscript IS a conditional procedure library
"""
elif passed >= 2:
    verdict = "PARTIAL SUPPORT FOR CONDITIONAL REFERENCE"
    tier = "Section 0.E remains Tier 3"
    interpretation = """
The A->B pipeline shows some differentiation structure:
- Filtering occurs but clusters are fuzzy
- Some specificity exists but is not dominant
- The conditional reference interpretation is plausible but not proven
"""
else:
    verdict = "CONDITIONAL REFERENCE NOT SUPPORTED"
    tier = "Revise Section 0.E interpretation"
    interpretation = """
The A->B pipeline does NOT create meaningful differentiation:
- A-records do not cluster cleanly by B-viability
- Filtering may be noise rather than structure
- The manuscript may NOT be a conditional reference system
- Alternative interpretations should be considered
"""

print(f"\n  VERDICT: {verdict}")
print(f"  Tier recommendation: {tier}")
print(interpretation)

# Save synthesis
output = {
    'hypotheses': {
        'H1_clustering': {'value': h1_silhouette, 'passed': h1_pass},
        'H2_sharpness': {'value': h2_ratio, 'p': h2_p, 'passed': h2_pass},
        'H3_pp_breadth': {'value': h3_rho, 'p': h3_p, 'passed': h3_pass},
        'H4_specificity': {'value': h4_pct, 'passed': h4_pass},
    },
    'passed_count': passed,
    'total_count': total,
    'key_stats': {
        'filtering_rate': filtering_rate,
        'narrow_record_pct': narrow_pct,
        'best_k': t2.get('best_k'),
    },
    'verdict': verdict,
    'tier_recommendation': tier,
}

out_path = results_dir / 't5_synthesis.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {out_path.name}")

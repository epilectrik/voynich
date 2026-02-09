"""
06_synthesis.py

CURRIER A STRUCTURE SYNTHESIS

Compile findings from all 5 tests and determine if we've moved from
"descriptive statistics" to "explanatory model".
"""

import json
from pathlib import Path

print("="*70)
print("CURRIER A STRUCTURE V2 - SYNTHESIS")
print("="*70)

results_dir = Path(__file__).parent.parent / 'results'

# =============================================================
# LOAD ALL TEST RESULTS
# =============================================================
print("\n[1/3] Loading test results...")

tests = {}

test_files = [
    ('position_cluster', 'position_cluster_analysis.json'),
    ('pp_composition', 'pp_composition_analysis.json'),
    ('ri_morphology', 'ri_morphology_analysis.json'),
    ('linker_targets', 'linker_target_analysis.json'),
    ('sequential_coherence', 'sequential_coherence_analysis.json')
]

for name, filename in test_files:
    filepath = results_dir / filename
    if filepath.exists():
        with open(filepath) as f:
            tests[name] = json.load(f)
        print(f"   ✓ Loaded {name}")
    else:
        print(f"   ✗ Missing {filename}")
        tests[name] = None

# =============================================================
# SUMMARIZE EACH TEST
# =============================================================
print("\n[2/3] Summarizing findings...")

print("\n" + "="*70)
print("TEST SUMMARIES")
print("="*70)

# Test 1: Position vs Cluster
print("\n1. FOLIO POSITION vs CLUSTER TYPE")
if tests['position_cluster']:
    t = tests['position_cluster']
    print(f"   Chi-squared: {t['chi_squared']:.2f} ({t['significance']})")
    print(f"   Verdict: {t['verdict']}")
    if t['strongest_patterns']:
        print("   Strongest patterns:")
        for pos, ct, ratio in t['strongest_patterns'][:3]:
            print(f"      {pos} → {ct}: {ratio:.2f}x")
else:
    print("   NOT RUN")

# Test 2: PP Composition
print("\n2. PP COMPOSITION IN FIRST LINES")
if tests['pp_composition']:
    t = tests['pp_composition']
    print(f"   Lines WITH RI: {t['n_with_ri']}, WITHOUT RI: {t['n_without_ri']}")
    print(f"   PP Jaccard similarity: {t['pp_vocabulary']['jaccard']:.3f}")
    print(f"   Verdict: {t['verdict']} / {t['vocab_verdict']}")
    if t['significant_differences']:
        print("   Significant PREFIX differences:")
        for prefix, ratio in t['significant_differences'][:3]:
            print(f"      {prefix}: {ratio:.2f}x")
else:
    print("   NOT RUN")

# Test 3: RI Morphology
print("\n3. RI MORPHOLOGY BY POSITION")
if tests['ri_morphology']:
    t = tests['ri_morphology']
    print(f"   Initial RI: {t['counts']['initial']}, Middle: {t['counts']['middle']}, Final: {t['counts']['final']}")
    print(f"   Average similarity: {t['similarity']['average']:.3f}")
    print(f"   Verdict: {t['verdict']}")
else:
    print("   NOT RUN")

# Test 4: Linker Targets
print("\n4. LINKER TARGET CHARACTERIZATION")
if tests['linker_targets']:
    t = tests['linker_targets']
    print(f"   Linker RI found: {len(t['linker_ri'])}")
    print(f"   Target folios: {t['known_targets']}")
    print(f"   Verdict: {t['verdict']}")
    if t['distinctive_features']:
        print("   Distinctive features:")
        for f in t['distinctive_features'][:3]:
            print(f"      {f}")
else:
    print("   NOT RUN")

# Test 5: Sequential Coherence
print("\n5. SEQUENTIAL COHERENCE")
if tests['sequential_coherence']:
    t = tests['sequential_coherence']
    print(f"   Paragraphs analyzed: {t['n_paragraphs']}")
    print(f"   Verdict: {t['verdict']}")
    if t['coherence_by_type']:
        print("   Coherence by type:")
        for ct, data in list(t['coherence_by_type'].items())[:3]:
            print(f"      {ct}: prefix_cont={data['prefix_continuity']:.3f}, entropy={data['cond_entropy']:.3f}")
else:
    print("   NOT RUN")

# =============================================================
# OVERALL SYNTHESIS
# =============================================================
print("\n" + "="*70)
print("SYNTHESIS: EXPLANATORY MODEL STATUS")
print("="*70)

gaps_addressed = 0
gaps_remaining = []

# Gap 1: No initial RI (53% of paragraphs)
if tests['pp_composition'] and tests['pp_composition']['verdict'] == 'TWO_OPENING_TYPES':
    print("\n✓ GAP 1 (No initial RI): ADDRESSED")
    print("   Two distinct paragraph opening types identified")
    gaps_addressed += 1
elif tests['pp_composition'] and tests['pp_composition']['vocab_verdict'] != 'SHARED_VOCABULARY':
    print("\n~ GAP 1 (No initial RI): PARTIALLY ADDRESSED")
    print("   Some vocabulary differentiation found")
    gaps_addressed += 0.5
else:
    print("\n✗ GAP 1 (No initial RI): NOT ADDRESSED")
    gaps_remaining.append("No initial RI in 53% of paragraphs")

# Gap 2: Paragraph size variance (2-12 lines)
if tests['position_cluster'] and tests['position_cluster']['verdict'] == 'POSITION_PREDICTS_CLUSTER':
    print("\n✓ GAP 2 (Paragraph size variance): ADDRESSED")
    print("   Position predicts cluster type - structural organization")
    gaps_addressed += 1
else:
    print("\n✗ GAP 2 (Paragraph size variance): NOT ADDRESSED")
    gaps_remaining.append("Paragraph size varies 2-12 lines")

# Gap 3: Middle-line RI
if tests['ri_morphology'] and tests['ri_morphology']['verdict'] == 'DISTINCT_FUNCTIONS':
    print("\n✓ GAP 3 (Middle-line RI): ADDRESSED")
    print("   Different RI positions have different morphology = different functions")
    gaps_addressed += 1
elif tests['ri_morphology'] and tests['ri_morphology']['verdict'] == 'MODERATE_VARIATION':
    print("\n~ GAP 3 (Middle-line RI): PARTIALLY ADDRESSED")
    print("   Some morphological variation by position")
    gaps_addressed += 0.5
else:
    print("\n✗ GAP 3 (Middle-line RI): NOT ADDRESSED")
    gaps_remaining.append("Middle-line RI function unclear")

# Gap 4: 5 cluster types
if tests['sequential_coherence'] and tests['sequential_coherence']['verdict'] == 'FUNCTIONAL_DIFFERENCES':
    print("\n✓ GAP 4 (5 cluster types): ADDRESSED")
    print("   Cluster types have different coherence patterns = functional")
    gaps_addressed += 1
else:
    print("\n✗ GAP 4 (5 cluster types): NOT ADDRESSED")
    gaps_remaining.append("5 cluster types unexplained")

# Gap 5: Linker sparsity
if tests['linker_targets'] and tests['linker_targets']['verdict'] == 'STRUCTURALLY_DISTINCT':
    print("\n✓ GAP 5 (Linker sparsity): ADDRESSED")
    print("   Linker targets are structurally distinct")
    gaps_addressed += 1
else:
    print("\n✗ GAP 5 (Linker sparsity): NOT ADDRESSED")
    gaps_remaining.append("Only 4 linker RI tokens unexplained")

# =============================================================
# FINAL VERDICT
# =============================================================
print("\n" + "="*70)
print("FINAL VERDICT")
print("="*70)

print(f"\nGaps addressed: {gaps_addressed}/5")

if gaps_addressed >= 4:
    overall = "STRONG"
    print("\n→ STRONG: We now have an EXPLANATORY MODEL for Currier A")
    print("   Paragraph structure is driven by identifiable factors")
elif gaps_addressed >= 2:
    overall = "MODERATE"
    print("\n→ MODERATE: Some explanatory progress made")
    print("   But key gaps remain in understanding A's generative process")
else:
    overall = "WEAK"
    print("\n→ WEAK: Still at DESCRIPTIVE level")
    print("   Gaps remain unexplained")

if gaps_remaining:
    print("\n   Remaining gaps:")
    for gap in gaps_remaining:
        print(f"   - {gap}")

# =============================================================
# POTENTIAL CONSTRAINTS
# =============================================================
print("\n" + "="*70)
print("POTENTIAL NEW CONSTRAINTS")
print("="*70)

potential_constraints = []

if tests['position_cluster'] and tests['position_cluster']['significance'] in ['HIGHLY_SIGNIFICANT', 'SIGNIFICANT']:
    potential_constraints.append({
        'id': 'C8XX',
        'title': 'Paragraph Position Predicts Structure',
        'content': f"Paragraph ordinal position within folio predicts cluster type (chi2={tests['position_cluster']['chi_squared']:.1f}, {tests['position_cluster']['significance']})",
        'source': 'CURRIER_A_STRUCTURE_V2'
    })

if tests['pp_composition'] and tests['pp_composition']['verdict'] == 'TWO_OPENING_TYPES':
    potential_constraints.append({
        'id': 'C8XX',
        'title': 'Two Paragraph Opening Types',
        'content': f"First lines WITH initial RI have different PP profiles than WITHOUT (Jaccard={tests['pp_composition']['pp_vocabulary']['jaccard']:.3f})",
        'source': 'CURRIER_A_STRUCTURE_V2'
    })

if tests['ri_morphology'] and tests['ri_morphology']['verdict'] != 'UNIFORM_FUNCTION':
    potential_constraints.append({
        'id': 'C8XX',
        'title': 'RI Morphology Varies by Position',
        'content': f"Initial, middle, and final RI tokens have different PREFIX distributions (similarity={tests['ri_morphology']['similarity']['average']:.3f})",
        'source': 'CURRIER_A_STRUCTURE_V2'
    })

if tests['sequential_coherence'] and tests['sequential_coherence']['verdict'] == 'FUNCTIONAL_DIFFERENCES':
    potential_constraints.append({
        'id': 'C8XX',
        'title': 'Cluster Types Have Different Coherence',
        'content': "Different paragraph cluster types exhibit different sequential coherence patterns",
        'source': 'CURRIER_A_STRUCTURE_V2'
    })

if potential_constraints:
    for c in potential_constraints:
        print(f"\n{c['id']}: {c['title']}")
        print(f"   {c['content']}")
else:
    print("\nNo new constraints warranted by current findings")

# =============================================================
# SAVE SYNTHESIS
# =============================================================
synthesis = {
    'phase': 'CURRIER_A_STRUCTURE_V2',
    'tests_run': [name for name, data in tests.items() if data is not None],
    'gaps_addressed': gaps_addressed,
    'gaps_remaining': gaps_remaining,
    'overall_verdict': overall,
    'potential_constraints': potential_constraints,
    'test_verdicts': {name: data.get('verdict') if data else None for name, data in tests.items()}
}

output_path = results_dir / 'synthesis.json'
with open(output_path, 'w') as f:
    json.dump(synthesis, f, indent=2)

print(f"\n\nSynthesis saved to: {output_path}")

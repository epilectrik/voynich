"""
12_all_categories_validation.py

Validate kernel patterns for ALL handling categories, not just PRECISION.

Expected patterns from BRSC:
- GENTLE (flowers): high e, low k (gentle heat preserves volatiles)
- STANDARD (herbs): balanced k/h/e
- CAREFUL (hot/dry): higher k (need more energy)
- PRECISION (animals): high k+e, low h (escape + auxiliary)
- INTENSE (gum/resin): high k (intense heat needed)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Morphology

results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("ALL CATEGORIES KERNEL VALIDATION")
print("="*70)

# Load data
with open(results_dir / "pp_brunschwig_match.json") as f:
    match_data = json.load(f)

with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

# Rebuild handling assignments from profiles
profiles = match_data['all_profiles']

morph = Morphology()

# PREFIX to role mapping
prefix_to_role = {
    'qo': 'ESCAPE',
    'ok': 'AUX',
    'ot': 'AUX',
    'da': 'FLOW',
    'ol': 'LINK',
    'or': 'LINK',
    'al': 'LINK',
    'ar': 'LINK',
    'ch': 'PHASE',
    'sh': 'PHASE',
    'k': 'ENERGY',
    's': 'STATE',
}

# Handling to expected roles
handling_to_roles = {
    'gentle': ['ESCAPE', 'LINK'],
    'standard': ['PHASE', 'ENERGY'],
    'careful': ['PHASE', 'AUX'],
    'intense': ['ENERGY', 'PHASE'],
    'precision': ['ESCAPE', 'AUX'],
}

def get_handling_type(prefix_profile):
    """Assign handling type based on PREFIX profile."""
    if not prefix_profile:
        return 'unknown'

    role_counts = Counter()
    for prefix, weight in prefix_profile.items():
        if prefix in prefix_to_role:
            role_counts[prefix_to_role[prefix]] += weight

    if not role_counts:
        return 'unknown'

    best_handling = None
    best_score = -1

    for handling, expected_roles in handling_to_roles.items():
        score = sum(role_counts.get(r, 0) for r in expected_roles)
        if score > best_score:
            best_score = score
            best_handling = handling

    return best_handling

def analyze_kernels(tokens):
    """Analyze kernel operators in paragraph tokens."""
    k_count = 0
    h_count = 0
    e_count = 0
    total = 0

    for t in tokens:
        word = t.get('word', '')
        if not word:
            continue
        try:
            m = morph.extract(word)
            middle = m.middle if m.middle else ''
            if 'k' in middle:
                k_count += 1
            if 'h' in middle:
                h_count += 1
            if 'e' in middle:
                e_count += 1
            total += 1
        except:
            pass

    if total == 0:
        return {'k': 0, 'h': 0, 'e': 0, 'total': 0}

    return {
        'k': k_count/total,
        'h': h_count/total,
        'e': e_count/total,
        'total': total
    }

# Group paragraphs by handling type and compute kernel profiles
handling_groups = defaultdict(list)

for p in profiles:
    handling = get_handling_type(p['prefix_profile'])
    para_id = p['para_id']
    tokens = para_tokens.get(para_id, [])

    if tokens:
        kernels = analyze_kernels(tokens)
        handling_groups[handling].append({
            'para_id': para_id,
            'initial_ri': p['initial_ri'],
            'kernels': kernels
        })

# Compute averages for each handling type
print("\n" + "="*70)
print("KERNEL PROFILES BY HANDLING TYPE")
print("="*70)

category_stats = {}

for handling in ['gentle', 'standard', 'careful', 'precision', 'intense', 'unknown']:
    paras = handling_groups.get(handling, [])
    if not paras:
        print(f"\n{handling.upper()}: No paragraphs")
        continue

    avg_k = sum(p['kernels']['k'] for p in paras) / len(paras)
    avg_h = sum(p['kernels']['h'] for p in paras) / len(paras)
    avg_e = sum(p['kernels']['e'] for p in paras) / len(paras)

    category_stats[handling] = {
        'count': len(paras),
        'k': avg_k,
        'h': avg_h,
        'e': avg_e,
        'k+e': avg_k + avg_e
    }

    print(f"\n{handling.upper()} ({len(paras)} paragraphs):")
    print(f"  Kernel: k={avg_k:.3f}, h={avg_h:.3f}, e={avg_e:.3f}")
    print(f"  k+e={avg_k+avg_e:.3f}, k/e ratio={avg_k/avg_e:.2f}" if avg_e > 0 else f"  k+e={avg_k+avg_e:.3f}")

    # Show sample RI MIDDLEs
    sample_ri = []
    for p in paras[:5]:
        sample_ri.extend(p['initial_ri'][:2])
    print(f"  Sample RI: {sample_ri[:8]}")

# Expected patterns check
print("\n" + "="*70)
print("PATTERN VALIDATION")
print("="*70)

expected = {
    'gentle': {'description': 'High e, low k (flowers)', 'test': lambda s: s['e'] > s['k']},
    'standard': {'description': 'Balanced', 'test': lambda s: abs(s['k'] - s['e']) < 0.1},
    'careful': {'description': 'Higher k (hot/dry herbs)', 'test': lambda s: s['k'] > 0.15},
    'precision': {'description': 'High k+e, low h (animals)', 'test': lambda s: s['k+e'] > 0.4 and s['h'] < 0.2},
}

for handling, exp in expected.items():
    if handling not in category_stats:
        print(f"\n{handling.upper()}: No data")
        continue

    stats = category_stats[handling]
    passed = exp['test'](stats)
    status = "PASS" if passed else "FAIL"

    print(f"\n{handling.upper()}: {exp['description']}")
    print(f"  Actual: k={stats['k']:.3f}, h={stats['h']:.3f}, e={stats['e']:.3f}")
    print(f"  Test: {status}")

# Material category summary
print("\n" + "="*70)
print("MATERIAL CATEGORY IDENTIFICATION SUMMARY")
print("="*70)

category_to_materials = {
    'gentle': 'Flowers (rose, violet, lily)',
    'standard': 'Common herbs (thyme, mint, sage)',
    'careful': 'Hot/dry herbs and roots (pepper, ginger)',
    'precision': 'Animal materials (chicken, ox blood)',
    'intense': 'Gums and resins (frankincense, myrrh)',
}

for handling, materials in category_to_materials.items():
    if handling in category_stats:
        count = category_stats[handling]['count']
        print(f"\n{handling.upper()}: {count} paragraphs")
        print(f"  Brunschwig materials: {materials}")

        # List RI MIDDLEs
        paras = handling_groups[handling]
        all_ri = []
        for p in paras:
            all_ri.extend(p['initial_ri'])
        ri_counts = Counter(all_ri)
        print(f"  Unique RI MIDDLEs: {len(ri_counts)}")
        print(f"  Top RIs: {ri_counts.most_common(5)}")

# Save results
output = {
    'category_stats': category_stats,
    'handling_groups': {
        h: [{'para_id': p['para_id'], 'initial_ri': p['initial_ri']} for p in paras]
        for h, paras in handling_groups.items()
    }
}

with open(results_dir / "all_categories_validation.json", 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n\nSaved to all_categories_validation.json")

"""
13_failure_diagnosis.py

Diagnose why CAREFUL and GENTLE categories failed kernel validation.

Questions:
1. Are the BRSC kernel predictions wrong?
2. Is the PREFIX -> handling classification wrong?
3. Are there data issues with Brunschwig recipes?
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
print("FAILURE DIAGNOSIS")
print("="*70)

# Load data
with open(results_dir / "pp_brunschwig_match.json") as f:
    match_data = json.load(f)

with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

profiles = match_data['all_profiles']

# ============================================================
# ISSUE 1: Check the handling classification logic
# ============================================================
print("\n" + "="*70)
print("ISSUE 1: HANDLING CLASSIFICATION LOGIC")
print("="*70)

# What prefixes dominate each category?
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

handling_to_roles = {
    'gentle': ['ESCAPE', 'LINK'],
    'standard': ['PHASE', 'ENERGY'],
    'careful': ['PHASE', 'AUX'],
    'precision': ['ESCAPE', 'AUX'],
}

def get_handling_and_roles(prefix_profile):
    if not prefix_profile:
        return 'unknown', {}

    role_counts = Counter()
    for prefix, weight in prefix_profile.items():
        if prefix in prefix_to_role:
            role_counts[prefix_to_role[prefix]] += weight

    if not role_counts:
        return 'unknown', {}

    best_handling = None
    best_score = -1

    for handling, expected_roles in handling_to_roles.items():
        score = sum(role_counts.get(r, 0) for r in expected_roles)
        if score > best_score:
            best_score = score
            best_handling = handling

    return best_handling, dict(role_counts)

# Group and analyze
handling_details = defaultdict(list)
for p in profiles:
    handling, roles = get_handling_and_roles(p['prefix_profile'])
    handling_details[handling].append({
        'para_id': p['para_id'],
        'prefix_profile': p['prefix_profile'],
        'roles': roles
    })

# Show what CAREFUL paragraphs actually look like
print("\nCAREFUL category (107 paragraphs) - What are their actual roles?")
careful_paras = handling_details.get('careful', [])
role_totals = Counter()
for p in careful_paras:
    for role, weight in p['roles'].items():
        role_totals[role] += weight

print(f"  Aggregate role weights: {dict(role_totals.most_common())}")

# Why is it classified as CAREFUL?
print("\n  CAREFUL requires: PHASE + AUX")
print("  Actual top roles show PHASE is dominant")

# Check prefix distribution
prefix_totals = Counter()
for p in careful_paras:
    for prefix, weight in (p['prefix_profile'] or {}).items():
        prefix_totals[prefix] += weight

print(f"\n  Top prefixes in CAREFUL: {prefix_totals.most_common(10)}")

# ============================================================
# ISSUE 2: GENTLE only has 2 paragraphs - who are they?
# ============================================================
print("\n" + "="*70)
print("ISSUE 2: GENTLE CATEGORY (only 2 paragraphs)")
print("="*70)

gentle_paras = handling_details.get('gentle', [])
for p in gentle_paras:
    print(f"\n{p['para_id']}:")
    print(f"  PREFIX profile: {p['prefix_profile']}")
    print(f"  Roles: {p['roles']}")

print("\nGENTLE requires: ESCAPE + LINK")
print("Only 2 paragraphs match this - is this too restrictive?")

# ============================================================
# ISSUE 3: Check BRSC predictions against Brunschwig data
# ============================================================
print("\n" + "="*70)
print("ISSUE 3: BRSC PREDICTIONS VS BRUNSCHWIG DATA")
print("="*70)

# Load Brunschwig signatures
with open(results_dir / "brunschwig_signatures.json") as f:
    brun_sigs = json.load(f)

print("\nBrunschwig material handling expectations:")
for material, handling in brun_sigs.get('material_handling', {}).items():
    print(f"  {material}: {handling}")

print("\nBrunschwig method -> kernel predictions:")
for method, kernels in brun_sigs.get('method_kernels', {}).items():
    print(f"  {method}: k={kernels['k']}, h={kernels['h']}, e={kernels['e']}")

# ============================================================
# ISSUE 4: What if the PREFIX -> handling mapping is wrong?
# ============================================================
print("\n" + "="*70)
print("ISSUE 4: ALTERNATIVE CLASSIFICATION")
print("="*70)

# What if we classify by DOMINANT prefix instead of role combination?
print("\nClassification by dominant PREFIX:")
dominant_groups = defaultdict(list)
for p in profiles:
    if p['prefix_profile']:
        dominant = max(p['prefix_profile'], key=p['prefix_profile'].get)
        dominant_groups[dominant].append(p['para_id'])

for prefix, paras in sorted(dominant_groups.items(), key=lambda x: -len(x[1])):
    print(f"  {prefix}: {len(paras)} paragraphs")

# ============================================================
# ISSUE 5: Does ch/sh really mean PHASE?
# ============================================================
print("\n" + "="*70)
print("ISSUE 5: QUESTIONING ch/sh = PHASE ASSUMPTION")
print("="*70)

print("\nThe assumption: ch/sh PREFIX = PHASE role")
print("This comes from BCSC role taxonomy")
print("")
print("But ch/sh is the MOST common prefix (71 + 29 = 100 paragraphs)")
print("Maybe ch/sh has multiple meanings depending on context?")

# Check if ch-dominant and sh-dominant paragraphs have different kernels
morph = Morphology()

def analyze_kernels(tokens):
    k_count = h_count = e_count = total = 0
    for t in tokens:
        word = t.get('word', '')
        if not word:
            continue
        try:
            m = morph.extract(word)
            middle = m.middle if m.middle else ''
            if 'k' in middle: k_count += 1
            if 'h' in middle: h_count += 1
            if 'e' in middle: e_count += 1
            total += 1
        except:
            pass
    if total == 0:
        return {'k': 0, 'h': 0, 'e': 0}
    return {'k': k_count/total, 'h': h_count/total, 'e': e_count/total}

ch_kernels = []
sh_kernels = []

for p in profiles:
    if not p['prefix_profile']:
        continue
    dominant = max(p['prefix_profile'], key=p['prefix_profile'].get)
    tokens = para_tokens.get(p['para_id'], [])
    if not tokens:
        continue

    kernels = analyze_kernels(tokens)
    if dominant == 'ch':
        ch_kernels.append(kernels)
    elif dominant == 'sh':
        sh_kernels.append(kernels)

if ch_kernels:
    avg_k = sum(k['k'] for k in ch_kernels) / len(ch_kernels)
    avg_h = sum(k['h'] for k in ch_kernels) / len(ch_kernels)
    avg_e = sum(k['e'] for k in ch_kernels) / len(ch_kernels)
    print(f"\nch-dominant ({len(ch_kernels)} paras): k={avg_k:.3f}, h={avg_h:.3f}, e={avg_e:.3f}")

if sh_kernels:
    avg_k = sum(k['k'] for k in sh_kernels) / len(sh_kernels)
    avg_h = sum(k['h'] for k in sh_kernels) / len(sh_kernels)
    avg_e = sum(k['e'] for k in sh_kernels) / len(sh_kernels)
    print(f"sh-dominant ({len(sh_kernels)} paras): k={avg_k:.3f}, h={avg_h:.3f}, e={avg_e:.3f}")

# ============================================================
# ISSUE 6: Is the problem that most Brunschwig recipes are similar?
# ============================================================
print("\n" + "="*70)
print("ISSUE 6: BRUNSCHWIG RECIPE HOMOGENEITY")
print("="*70)

# Count recipes by handling type
try:
    with open(Path(__file__).parent.parent.parent.parent / 'data' / 'brunschwig_curated_v3.json',
              encoding='utf-8') as f:
        brunschwig = json.load(f)

    degree_counts = Counter()
    for recipe in brunschwig.get('recipes', []):
        degree = recipe.get('fire_degree', 'unknown')
        degree_counts[degree] += 1

    print(f"\nBrunschwig fire degree distribution:")
    for degree, count in degree_counts.most_common():
        pct = 100 * count / sum(degree_counts.values())
        print(f"  Degree {degree}: {count} recipes ({pct:.1f}%)")

    print("\nFire degree -> Material type mapping:")
    print("  Degree 1 (gentle): Flowers, delicate")
    print("  Degree 2 (standard): Most herbs - THIS IS ~60% OF RECIPES")
    print("  Degree 3 (intense): Gums, resins")
    print("  Degree 4 (precision): Animals")

except Exception as e:
    print(f"Could not load Brunschwig: {e}")

# ============================================================
# CONCLUSIONS
# ============================================================
print("\n" + "="*70)
print("DIAGNOSTIC CONCLUSIONS")
print("="*70)

print("""
1. CAREFUL (107 paragraphs) is dominated by PHASE (ch/sh) roles
   - This is the "default" category catching most paragraphs
   - May represent standard herb processing (fire degree 2)
   - The kernel test expected higher k, but got k=0.114
   - POSSIBLE ISSUE: Our BRSC prediction for "careful" may be wrong

2. GENTLE (2 paragraphs) is too small to validate
   - Only paragraphs with ESCAPE+LINK get classified here
   - This might be correct (few flowers in Voynich?)
   - Or the classification is too restrictive

3. ~60% of Brunschwig recipes are fire degree 2 (standard herbs)
   - This means most materials produce similar signatures
   - Hard to discriminate within this large category

4. ch/sh (PHASE) is the dominant prefix across most paragraphs
   - This matches Brunschwig where most recipes are degree 2
   - But it means CAREFUL is a catch-all, not a specific category

5. PRECISION works because animals are DISTINCTIVE
   - ESCAPE+AUX is rare in the data
   - High k+e, low h is a unique kernel signature
   - Only 9 paragraphs match = specific identification

RECOMMENDATION:
- PRECISION (animals) and STANDARD (common herbs) are valid categories
- CAREFUL may just be "everything else" (not a meaningful category)
- GENTLE sample too small
- The methodology works best for DISTINCTIVE materials
""")

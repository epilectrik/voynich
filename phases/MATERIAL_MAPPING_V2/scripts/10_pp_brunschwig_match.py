"""
10_pp_brunschwig_match.py

Match PP patterns from A paragraphs against Brunschwig instruction signatures.

For paragraphs with initial RI:
1. Extract PREFIX profile from their PP tokens
2. Match against Brunschwig material handling patterns
3. Identify candidate material→RI mappings
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Morphology

results_dir = Path(__file__).parent.parent / "results"

print("="*70)
print("PP-BRUNSCHWIG MATCHING")
print("="*70)

# Load paragraph profiles
with open(results_dir / "pp_triangulation_v3.json") as f:
    tri_data = json.load(f)

profiles = tri_data['profiles']
print(f"Total paragraphs: {len(profiles)}")

# Filter to paragraphs with initial RI
has_init_ri = [p for p in profiles if p['first_line_ri']]
print(f"Paragraphs with initial RI: {len(has_init_ri)}")

# Load Brunschwig signatures
with open(results_dir / "brunschwig_signatures.json") as f:
    brun_sigs = json.load(f)

# Extract PREFIX from PP tokens for each paragraph
morph = Morphology()

def get_prefix_profile(pp_tokens):
    """Compute PREFIX distribution from PP tokens."""
    prefixes = []
    for t in pp_tokens:
        try:
            m = morph.extract(t['word'])
            if m.prefix:
                prefixes.append(m.prefix)
        except:
            pass

    if not prefixes:
        return {}

    counts = Counter(prefixes)
    total = sum(counts.values())
    return {p: count/total for p, count in counts.most_common(10)}

# Compute PREFIX profiles for each paragraph
print("\n" + "="*70)
print("PREFIX PROFILES FOR PARAGRAPHS WITH INITIAL RI")
print("="*70)

para_prefix_profiles = []
for p in has_init_ri:
    all_pp = p['first_line_pp'] + p['middle_pp']
    profile = get_prefix_profile(all_pp)

    # Get initial RI middles
    init_middles = [t['middle'] for t in p['first_line_ri']]

    para_prefix_profiles.append({
        'para_id': p['para_id'],
        'n_lines': p['n_lines'],
        'initial_ri': init_middles,
        'pp_count': len(all_pp),
        'prefix_profile': profile
    })

# Show examples
for pp in para_prefix_profiles[:10]:
    print(f"\n{pp['para_id']} ({pp['n_lines']} lines):")
    print(f"  Initial RI MIDDLEs: {pp['initial_ri']}")
    print(f"  PP tokens: {pp['pp_count']}")
    top_prefixes = list(pp['prefix_profile'].items())[:5]
    print(f"  Top PREFIXes: {top_prefixes}")

# Group by PREFIX pattern
print("\n" + "="*70)
print("GROUPING BY DOMINANT PREFIX")
print("="*70)

prefix_groups = defaultdict(list)
for pp in para_prefix_profiles:
    if pp['prefix_profile']:
        dominant = max(pp['prefix_profile'], key=pp['prefix_profile'].get)
        prefix_groups[dominant].append(pp)
    else:
        prefix_groups['NONE'].append(pp)

for prefix, paras in sorted(prefix_groups.items(), key=lambda x: -len(x[1])):
    print(f"\n{prefix}: {len(paras)} paragraphs")
    # Show sample MIDDLEs from this group
    sample_middles = []
    for p in paras[:5]:
        sample_middles.extend(p['initial_ri'][:2])
    print(f"  Sample RI MIDDLEs: {sample_middles[:10]}")

# Map PREFIX to Brunschwig handling
print("\n" + "="*70)
print("PREFIX TO BRUNSCHWIG HANDLING MAPPING")
print("="*70)

# From BCSC role taxonomy
prefix_to_role = {
    'qo': 'ESCAPE',  # Escape route
    'ok': 'AUX',     # Auxiliary
    'ot': 'AUX',
    'da': 'FLOW',    # Flow redirect
    'ol': 'LINK',    # Monitoring
    'or': 'LINK',
    'al': 'LINK',
    'ar': 'LINK',
    'ch': 'PHASE',   # Phase marker
    'sh': 'PHASE',
    'k': 'ENERGY',   # Energy operator
    's': 'STATE',    # State
}

# Brunschwig handling → expected roles
handling_to_roles = {
    'gentle': ['ESCAPE', 'LINK'],      # balneum marie - low heat, monitor closely
    'standard': ['PHASE', 'ENERGY'],   # per cinerem - normal distillation
    'careful': ['PHASE', 'AUX'],       # hot/dry - need auxiliary control
    'intense': ['ENERGY', 'PHASE'],    # per ignem - high heat
    'precision': ['ESCAPE', 'AUX'],    # animals - need escape + auxiliary (matches eoschso finding!)
}

# Assign handling type to each paragraph based on PREFIX profile
print("\nAssigning handling types based on PREFIX patterns:")

handling_assignments = defaultdict(list)
for pp in para_prefix_profiles:
    if not pp['prefix_profile']:
        handling_assignments['unknown'].append(pp)
        continue

    # Compute role profile from prefixes
    role_counts = Counter()
    for prefix, weight in pp['prefix_profile'].items():
        if prefix in prefix_to_role:
            role_counts[prefix_to_role[prefix]] += weight

    if not role_counts:
        handling_assignments['unknown'].append(pp)
        continue

    # Find best matching handling type
    best_handling = None
    best_score = -1

    for handling, expected_roles in handling_to_roles.items():
        score = sum(role_counts.get(r, 0) for r in expected_roles)
        if score > best_score:
            best_score = score
            best_handling = handling

    handling_assignments[best_handling].append({
        'para': pp,
        'role_profile': dict(role_counts),
        'score': best_score
    })

for handling, paras in sorted(handling_assignments.items(), key=lambda x: -len(x[1])):
    print(f"\n{handling.upper()}: {len(paras)} paragraphs")
    if handling != 'unknown' and paras:
        # Show top candidates (highest scores)
        sorted_paras = sorted(paras, key=lambda x: -x['score'])
        for item in sorted_paras[:3]:
            p = item['para']
            print(f"  {p['para_id']}: RI={p['initial_ri'][:2]}, score={item['score']:.2f}")
            print(f"    roles: {item['role_profile']}")

# Focus on PRECISION (animals)
print("\n" + "="*70)
print("PRECISION HANDLING CANDIDATES (Animals)")
print("="*70)
print("Expected pattern: ESCAPE + AUX dominant (matches chicken/ox finding)")

precision_paras = handling_assignments.get('precision', [])
if precision_paras:
    sorted_prec = sorted(precision_paras, key=lambda x: -x['score'])
    for item in sorted_prec[:10]:
        p = item['para']
        print(f"\n{p['para_id']}:")
        print(f"  Initial RI MIDDLEs: {p['initial_ri']}")
        print(f"  Role profile: {item['role_profile']}")
        print(f"  Match score: {item['score']:.3f}")

# Aggregate RI MIDDLEs by handling type
print("\n" + "="*70)
print("RI MIDDLE AGGREGATION BY HANDLING TYPE")
print("="*70)

for handling, items in handling_assignments.items():
    if handling == 'unknown':
        continue

    all_middles = []
    for item in items:
        if isinstance(item, dict):
            all_middles.extend(item['para']['initial_ri'])
        else:
            all_middles.extend(item['initial_ri'])

    middle_counts = Counter(all_middles)
    print(f"\n{handling.upper()} ({len(items)} paragraphs):")
    print(f"  Unique RI MIDDLEs: {len(middle_counts)}")
    print(f"  Top MIDDLEs: {middle_counts.most_common(10)}")

# Save results
output = {
    'total_with_initial_ri': len(has_init_ri),
    'handling_assignments': {
        h: len(items) for h, items in handling_assignments.items()
    },
    'precision_candidates': [
        {
            'para_id': item['para']['para_id'],
            'initial_ri': item['para']['initial_ri'],
            'score': item['score'],
            'role_profile': item['role_profile']
        }
        for item in precision_paras[:20]
    ] if precision_paras else [],
    'all_profiles': para_prefix_profiles
}

with open(results_dir / "pp_brunschwig_match.json", 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n\nSaved to pp_brunschwig_match.json")

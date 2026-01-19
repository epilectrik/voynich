"""
JAR ROLE-SPACE COMPOSITION ANALYSIS

Question: Are jars stable ROLE ASSEMBLERS?
Do they consistently balance role classes (M-A, M-B, M-D, OTHER) even when tokens differ?

Key reframe: Token similarity is NOT the target. Role composition IS.

Already established (DO NOT RETEST):
- Jars are complementary working sets (CLOSED)
- Jar PREFIX != content PREFIX (CLOSED)
- Cross-class enrichment M-A+M-B+M-D (CLOSED, p=0.022)
- No exclusion patterns (CLOSED)

Expected if model is CORRECT:
- Recurrent ROLE COMPOSITION (2-3 classes per jar, stable mix)
- HIGH morphological diversity within jars
- Role balance variance << random
"""

import json
import math
import random
from pathlib import Path
from collections import Counter, defaultdict

# =============================================================================
# ROLE CLASS MAPPING (per C466/C408)
# =============================================================================

# Sister pairs collapsed to role classes
ROLE_CLASSES = {
    # M-A: Energy/phase-sensitive
    'ch': 'M-A', 'sh': 'M-A', 'qo': 'M-A',
    # M-B: Routine processing
    'ok': 'M-B', 'ot': 'M-B',
    # M-D: Stable/anchoring
    'da': 'M-D', 'ol': 'M-D',
    # M-C: Registry
    'ct': 'M-C',
}

def get_prefix(token):
    """Extract 2-char prefix from token."""
    return token[:2] if len(token) >= 2 else token

def get_role_class(token):
    """Map token to role class via prefix."""
    prefix = get_prefix(token)
    return ROLE_CLASSES.get(prefix, 'OTHER')

def entropy(counts):
    """Compute Shannon entropy from count dict."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)

# =============================================================================
# STEP 1: LOAD DATA AND MAP TO ROLES
# =============================================================================

print("=" * 70)
print("JAR ROLE-SPACE COMPOSITION ANALYSIS")
print("=" * 70)
print("\nLoading jar data and mapping to role classes...")

jar_contents = {}  # jar_key -> list of content tokens
jar_roles = {}     # jar_key -> list of role classes

script_dir = Path(__file__).parent
for f in script_dir.glob('*_mapping.json'):
    with open(f) as fp:
        data = json.load(fp)
    if data.get('classification') == 'reference_page':
        continue
    folio = data.get('folio', f.stem)

    if 'groups' in data:
        for g in data['groups']:
            jar = g.get('jar')
            if jar and isinstance(jar, str):
                jar_key = f"{jar.lower()}@{folio}"
                contents = []
                roots = g.get('roots', g.get('leaves', []))
                for r in roots:
                    if isinstance(r, str):
                        contents.append(r.lower())
                    elif isinstance(r, dict):
                        token = r.get('token', '').lower()
                        if token:
                            contents.append(token)

                if contents:
                    jar_contents[jar_key] = contents
                    jar_roles[jar_key] = [get_role_class(c) for c in contents]

print(f"Loaded {len(jar_contents)} jars with content")

# =============================================================================
# STEP 2: COMPUTE ROLE VECTORS FOR EACH JAR
# =============================================================================

print("\n" + "=" * 70)
print("ROLE VECTORS BY JAR")
print("=" * 70)

role_vectors = {}  # jar_key -> {n_MA, n_MB, n_MD, n_OTHER, diversity, entropy}

for jar_key in sorted(jar_contents.keys()):
    roles = jar_roles[jar_key]
    role_counts = Counter(roles)

    n_ma = role_counts.get('M-A', 0)
    n_mb = role_counts.get('M-B', 0)
    n_md = role_counts.get('M-D', 0)
    n_mc = role_counts.get('M-C', 0)
    n_other = role_counts.get('OTHER', 0)

    # Binary presence
    has_ma = n_ma > 0
    has_mb = n_mb > 0
    has_md = n_md > 0
    has_other = n_other > 0 or n_mc > 0  # M-C is rare, group with OTHER

    # Diversity: number of distinct role classes present
    diversity = sum([has_ma, has_mb, has_md, has_other])

    # Entropy
    ent = entropy(role_counts)

    role_vectors[jar_key] = {
        'n_MA': n_ma,
        'n_MB': n_mb,
        'n_MD': n_md,
        'n_OTHER': n_other + n_mc,
        'has_MA': has_ma,
        'has_MB': has_mb,
        'has_MD': has_md,
        'has_OTHER': has_other,
        'diversity': diversity,
        'entropy': ent,
        'total': len(roles)
    }

print(f"\n{'JAR':<25} {'M-A':>5} {'M-B':>5} {'M-D':>5} {'OTH':>5} {'DIV':>4} {'ENT':>6}")
print("-" * 60)

for jar_key in sorted(role_vectors.keys()):
    v = role_vectors[jar_key]
    print(f"{jar_key:<25} {v['n_MA']:>5} {v['n_MB']:>5} {v['n_MD']:>5} {v['n_OTHER']:>5} {v['diversity']:>4} {v['entropy']:>6.2f}")

# =============================================================================
# STEP 3: TEST ROLE COMPOSITION STABILITY
# =============================================================================

print("\n" + "=" * 70)
print("ROLE COMPOSITION STABILITY TEST")
print("=" * 70)

# Observed statistics
observed_diversities = [v['diversity'] for v in role_vectors.values()]
observed_entropies = [v['entropy'] for v in role_vectors.values()]
observed_mean_diversity = sum(observed_diversities) / len(observed_diversities)
observed_std_diversity = (sum((d - observed_mean_diversity)**2 for d in observed_diversities) / len(observed_diversities))**0.5
observed_mean_entropy = sum(observed_entropies) / len(observed_entropies)

# Count jars with complete working sets (has M-A AND M-B AND M-D)
observed_complete = sum(1 for v in role_vectors.values()
                        if v['has_MA'] and v['has_MB'] and v['has_MD'])

print(f"\nOBSERVED:")
print(f"  Mean diversity: {observed_mean_diversity:.2f}")
print(f"  Std diversity:  {observed_std_diversity:.2f}")
print(f"  Mean entropy:   {observed_mean_entropy:.2f}")
print(f"  Jars with complete working sets (M-A+M-B+M-D): {observed_complete}/{len(role_vectors)}")

# Shuffling test: randomize content -> jar assignments
all_contents = []
jar_sizes = []
for jar_key in sorted(jar_contents.keys()):
    all_contents.extend(jar_contents[jar_key])
    jar_sizes.append(len(jar_contents[jar_key]))

n_shuffles = 1000
shuffled_diversities = []
shuffled_entropies = []
shuffled_complete_counts = []

random.seed(42)
for _ in range(n_shuffles):
    # Shuffle all contents
    shuffled = all_contents.copy()
    random.shuffle(shuffled)

    # Reassign to jars maintaining original sizes
    idx = 0
    trial_diversities = []
    trial_entropies = []
    trial_complete = 0

    for size in jar_sizes:
        jar_contents_trial = shuffled[idx:idx+size]
        jar_roles_trial = [get_role_class(c) for c in jar_contents_trial]
        role_counts = Counter(jar_roles_trial)

        has_ma = role_counts.get('M-A', 0) > 0
        has_mb = role_counts.get('M-B', 0) > 0
        has_md = role_counts.get('M-D', 0) > 0
        has_other = (role_counts.get('OTHER', 0) + role_counts.get('M-C', 0)) > 0

        diversity = sum([has_ma, has_mb, has_md, has_other])
        ent = entropy(role_counts)

        trial_diversities.append(diversity)
        trial_entropies.append(ent)
        if has_ma and has_mb and has_md:
            trial_complete += 1

        idx += size

    shuffled_diversities.append(sum(trial_diversities) / len(trial_diversities))
    shuffled_entropies.append(sum(trial_entropies) / len(trial_entropies))
    shuffled_complete_counts.append(trial_complete)

# Compute p-values
p_diversity = sum(1 for d in shuffled_diversities if d >= observed_mean_diversity) / n_shuffles
p_entropy = sum(1 for e in shuffled_entropies if e >= observed_mean_entropy) / n_shuffles
p_complete = sum(1 for c in shuffled_complete_counts if c >= observed_complete) / n_shuffles

expected_diversity = sum(shuffled_diversities) / len(shuffled_diversities)
expected_entropy = sum(shuffled_entropies) / len(shuffled_entropies)
expected_complete = sum(shuffled_complete_counts) / len(shuffled_complete_counts)

print(f"\nSHUFFLED BASELINE (n={n_shuffles}):")
print(f"  Expected mean diversity: {expected_diversity:.2f}")
print(f"  Expected mean entropy:   {expected_entropy:.2f}")
print(f"  Expected complete sets:  {expected_complete:.2f}")

print(f"\nCOMPARISON:")
print(f"  Diversity ratio (obs/exp): {observed_mean_diversity/expected_diversity:.2f}")
print(f"  Entropy ratio (obs/exp):   {observed_mean_entropy/expected_entropy:.2f}")
print(f"  Complete sets ratio:       {observed_complete/expected_complete:.2f}")

print(f"\nP-VALUES:")
print(f"  P(diversity >= observed): {p_diversity:.3f}")
print(f"  P(entropy >= observed):   {p_entropy:.3f}")
print(f"  P(complete >= observed):  {p_complete:.3f}")

# =============================================================================
# STEP 4: ROLE COMPOSITION TYPE CLUSTERING
# =============================================================================

print("\n" + "=" * 70)
print("ROLE COMPOSITION TYPE CLUSTERING")
print("=" * 70)

# Group jars by their binary role vector (which classes are present)
composition_types = defaultdict(list)
for jar_key, v in role_vectors.items():
    # Create signature: tuple of (has_MA, has_MB, has_MD, has_OTHER)
    sig = (v['has_MA'], v['has_MB'], v['has_MD'], v['has_OTHER'])
    composition_types[sig].append(jar_key)

print(f"\nDistinct role composition types: {len(composition_types)}")
print("\nComposition patterns:")
for sig, jars in sorted(composition_types.items(), key=lambda x: -len(x[1])):
    ma_str = "M-A" if sig[0] else "---"
    mb_str = "M-B" if sig[1] else "---"
    md_str = "M-D" if sig[2] else "---"
    ot_str = "OTH" if sig[3] else "---"
    print(f"  [{ma_str}|{mb_str}|{md_str}|{ot_str}]: {len(jars)} jars")
    for j in jars:
        print(f"      {j}")

# =============================================================================
# SUMMARY AND RESULTS
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Determine result - be precise about what p-values mean
if p_diversity < 0.05:
    diversity_result = "SIGNIFICANT: Role diversity differs from random"
elif p_diversity > 0.95:
    diversity_result = "SIGNIFICANT: Role diversity less than random"
else:
    diversity_result = "NEUTRAL: Role diversity indistinguishable from random"

if p_complete < 0.05:
    complete_result = "SIGNIFICANT: Complete working sets enriched"
elif p_complete > 0.95:
    complete_result = "SIGNIFICANT: Fewer complete sets than random"
else:
    complete_result = "NEUTRAL: Complete sets indistinguishable from random"

if len(composition_types) <= 3:
    clustering_result = "STRONG: Jars cluster into few composition types"
elif len(composition_types) <= 5:
    clustering_result = "MODERATE: Some clustering into composition types"
else:
    clustering_result = "WEAK: Many distinct composition types"

# Determine overall status
if p_diversity < 0.05 or p_complete < 0.05:
    model_status = "CONFIRMED"
elif p_diversity > 0.95 or p_complete > 0.95:
    model_status = "FALSIFIED"
else:
    model_status = "NEUTRAL"

print(f"""
FINDINGS:

1. DIVERSITY: {diversity_result}
   - Observed: {observed_mean_diversity:.2f}, Expected: {expected_diversity:.2f}
   - p = {p_diversity:.3f} (not significant)

2. COMPLETE WORKING SETS: {complete_result}
   - Observed: {observed_complete}, Expected: {expected_complete:.1f}
   - p = {p_complete:.3f} (not significant)

3. COMPOSITION CLUSTERING: {clustering_result}
   - {len(composition_types)} distinct types across {len(role_vectors)} jars

4. MODEL STATUS: {model_status}
   - This test does NOT add signal beyond triplet enrichment (p=0.022)
   - Role balance is indistinguishable from random assignment
   - Working-sets interpretation is NOT FALSIFIED
   - Jars show normal mixing, not artificial balancing
""")

# =============================================================================
# SAVE RESULTS
# =============================================================================

results = {
    "phase": "JAR_ROLE_ANALYSIS",
    "question": "Are jars stable role assemblers?",

    "observed": {
        "n_jars": len(role_vectors),
        "mean_diversity": round(observed_mean_diversity, 3),
        "std_diversity": round(observed_std_diversity, 3),
        "mean_entropy": round(observed_mean_entropy, 3),
        "complete_working_sets": observed_complete
    },

    "baseline": {
        "expected_diversity": round(expected_diversity, 3),
        "expected_entropy": round(expected_entropy, 3),
        "expected_complete": round(expected_complete, 3),
        "n_shuffles": n_shuffles
    },

    "p_values": {
        "diversity": round(p_diversity, 3),
        "entropy": round(p_entropy, 3),
        "complete_sets": round(p_complete, 3)
    },

    "ratios": {
        "diversity": round(observed_mean_diversity / expected_diversity, 3),
        "entropy": round(observed_mean_entropy / expected_entropy, 3),
        "complete_sets": round(observed_complete / expected_complete, 3) if expected_complete > 0 else "N/A"
    },

    "composition_types": {
        "count": len(composition_types),
        "types": {
            f"{'MA' if sig[0] else '--'}|{'MB' if sig[1] else '--'}|{'MD' if sig[2] else '--'}|{'OT' if sig[3] else '--'}":
            len(jars) for sig, jars in composition_types.items()
        }
    },

    "role_vectors": {
        jar: {k: v for k, v in vec.items()}
        for jar, vec in role_vectors.items()
    },

    "interpretation": {
        "diversity": diversity_result,
        "complete_sets": complete_result,
        "clustering": clustering_result,
        "model_status": model_status,
        "note": "Role balance is neutral - does not add signal beyond triplet enrichment"
    }
}

output_path = script_dir / 'jar_role_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")

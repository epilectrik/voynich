"""
02_content_material_category.py - Test if root vs leaf labels differ in handling signature

Question: Do root labels vs leaf labels show different handling profiles?

Under Brunschwig:
- Roots: May need more intensive preparation (CHOP, POUND)
- Leaves: May be more delicate (GATHER, STRIP)

Method:
1. Separate root vs leaf labels from PHARMA_LABEL_DECODING
2. Extract MIDDLEs for each
3. Compute PREFIX profile (handling signature)
4. Test if profiles differ
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 2: ROOT vs LEAF HANDLING PROFILES")
print("="*70)

# PREFIX classes (from constraint system)
HANDLING_PREFIXES = {
    'ENERGY': {'qo', 'ch', 'sh'},      # Energy/thermal operations
    'SCAFFOLD': {'ok', 'ot', 'ol', 'or', 'od', 'os'},  # Auxiliary scaffold
    'ANCHOR': {'da', 'sa'},             # Anchoring/reference
    'BARE': {None, '', 'o'}             # Bare (no prefix)
}

def classify_prefix(prefix):
    for category, prefixes in HANDLING_PREFIXES.items():
        if prefix in prefixes:
            return category
    return 'OTHER'

# ============================================================
# STEP 1: LOAD CONTENT LABELS (ROOT vs LEAF)
# ============================================================
print("\n--- Step 1: Loading Root and Leaf Labels ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

root_labels = []
leaf_labels = []

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        # Roots
        for item in group.get('roots', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                root_labels.append({'token': token, 'folio': folio})

        # Leaves
        for item in group.get('leaves', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                leaf_labels.append({'token': token, 'folio': folio})

print(f"Root labels: {len(root_labels)}")
print(f"Leaf labels: {len(leaf_labels)}")

# ============================================================
# STEP 2: EXTRACT MORPHOLOGY
# ============================================================
print("\n--- Step 2: Extracting Morphology ---")

def analyze_labels(labels, name):
    prefix_counts = Counter()
    handling_counts = Counter()
    middles = []

    for label in labels:
        m = morph.extract(label['token'])
        if not m:
            continue

        prefix_counts[m.prefix] += 1
        handling = classify_prefix(m.prefix)
        handling_counts[handling] += 1

        if m.middle:
            middles.append(m.middle)

    total = sum(handling_counts.values())

    print(f"\n{name} ({len(labels)} labels, {total} with morphology):")
    print(f"  Top prefixes: {prefix_counts.most_common(5)}")
    print(f"  Handling profile:")
    for cat in ['ENERGY', 'SCAFFOLD', 'ANCHOR', 'BARE', 'OTHER']:
        count = handling_counts[cat]
        pct = 100 * count / total if total > 0 else 0
        print(f"    {cat}: {count} ({pct:.1f}%)")

    return handling_counts, middles, total

root_handling, root_middles, root_total = analyze_labels(root_labels, "ROOTS")
leaf_handling, leaf_middles, leaf_total = analyze_labels(leaf_labels, "LEAVES")

# ============================================================
# STEP 3: STATISTICAL COMPARISON
# ============================================================
print("\n--- Step 3: Statistical Comparison ---")

# Build contingency table
categories = ['ENERGY', 'SCAFFOLD', 'ANCHOR', 'BARE', 'OTHER']
root_counts = [root_handling[c] for c in categories]
leaf_counts = [leaf_handling[c] for c in categories]

# Chi-square test
contingency = np.array([root_counts, leaf_counts])
# Remove zero columns
nonzero_cols = contingency.sum(axis=0) > 0
contingency_clean = contingency[:, nonzero_cols]
categories_clean = [c for c, nz in zip(categories, nonzero_cols) if nz]

if contingency_clean.shape[1] >= 2:
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_clean)
    # Cramer's V
    n = contingency_clean.sum()
    cramers_v = np.sqrt(chi2 / (n * (min(contingency_clean.shape) - 1))) if n > 0 else 0

    print(f"\nChi-square test (root vs leaf handling):")
    print(f"  Chi2 = {chi2:.2f}")
    print(f"  p-value = {p_value:.4f}")
    print(f"  Cramer's V = {cramers_v:.3f}")
    print(f"  {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
else:
    chi2, p_value, cramers_v = 0, 1, 0
    print("\nInsufficient categories for chi-square test")

# ============================================================
# STEP 4: SPECIFIC CATEGORY COMPARISONS
# ============================================================
print("\n--- Step 4: Specific Category Comparisons ---")

print(f"\n{'Category':<12} {'Root %':<10} {'Leaf %':<10} {'Difference'}")
print("-" * 45)

for cat in categories:
    root_pct = 100 * root_handling[cat] / root_total if root_total > 0 else 0
    leaf_pct = 100 * leaf_handling[cat] / leaf_total if leaf_total > 0 else 0
    diff = root_pct - leaf_pct
    print(f"{cat:<12} {root_pct:>6.1f}%    {leaf_pct:>6.1f}%    {diff:+.1f}")

# ============================================================
# STEP 5: MIDDLE OVERLAP
# ============================================================
print("\n--- Step 5: MIDDLE Overlap ---")

root_middle_set = set(root_middles)
leaf_middle_set = set(leaf_middles)

overlap = root_middle_set & leaf_middle_set
root_only = root_middle_set - leaf_middle_set
leaf_only = leaf_middle_set - root_middle_set

jaccard = len(overlap) / len(root_middle_set | leaf_middle_set) if (root_middle_set | leaf_middle_set) else 0

print(f"Root unique MIDDLEs: {len(root_middle_set)}")
print(f"Leaf unique MIDDLEs: {len(leaf_middle_set)}")
print(f"Overlap: {len(overlap)} (Jaccard = {jaccard:.3f})")
print(f"Root-only: {len(root_only)}")
print(f"Leaf-only: {len(leaf_only)}")

if overlap:
    print(f"\nShared MIDDLEs: {sorted(overlap)[:10]}...")
if root_only:
    print(f"Root-only MIDDLEs: {sorted(root_only)[:10]}...")
if leaf_only:
    print(f"Leaf-only MIDDLEs: {sorted(leaf_only)[:10]}...")

# ============================================================
# STEP 6: PREPARATION MIDDLE CO-OCCURRENCE
# ============================================================
print("\n--- Step 6: Preparation MIDDLE Association ---")

# Preparation MIDDLEs
PREP_MIDDLES = {'te': 'GATHER', 'pch': 'CHOP', 'lch': 'STRIP', 'tch': 'POUND', 'ksh': 'BREAK'}

# Build MIDDLE -> B lines with prep ops
middle_prep_assoc = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    for prep_m, prep_name in PREP_MIDDLES.items():
        if prep_m in m.middle:
            # This line has a prep op - record all MIDDLEs on this line
            # (simplified: just record this token's MIDDLE as associated with this prep)
            middle_prep_assoc[m.middle][prep_name] += 1

# Check which prep ops associate with root vs leaf MIDDLEs
root_prep = Counter()
leaf_prep = Counter()

for mid in root_middle_set:
    for prep, count in middle_prep_assoc.get(mid, {}).items():
        root_prep[prep] += count

for mid in leaf_middle_set:
    for prep, count in middle_prep_assoc.get(mid, {}).items():
        leaf_prep[prep] += count

print(f"\nPreparation operation associations:")
print(f"{'Prep Op':<10} {'Root':<10} {'Leaf':<10}")
print("-" * 30)
for prep in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'BREAK']:
    print(f"{prep:<10} {root_prep[prep]:<10} {leaf_prep[prep]:<10}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'content_material_category',
    'question': 'Do root vs leaf labels show different handling profiles?',
    'sample': {
        'root_labels': len(root_labels),
        'leaf_labels': len(leaf_labels),
        'root_with_morph': root_total,
        'leaf_with_morph': leaf_total
    },
    'handling_profiles': {
        'root': dict(root_handling),
        'leaf': dict(leaf_handling)
    },
    'statistics': {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v),
        'significant': bool(p_value < 0.05)
    },
    'middle_overlap': {
        'jaccard': float(jaccard),
        'shared': len(overlap),
        'root_only': len(root_only),
        'leaf_only': len(leaf_only)
    },
    'prep_associations': {
        'root': dict(root_prep),
        'leaf': dict(leaf_prep)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results' / 'content_material_category.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: ROOT vs LEAF HANDLING PROFILES")
print("="*70)

print(f"""
Do root vs leaf labels show different handling profiles?

Sample:
  Roots: {len(root_labels)} labels
  Leaves: {len(leaf_labels)} labels

Handling Profile Comparison:
  Chi2 = {chi2:.2f}, p = {p_value:.4f}
  Cramer's V = {cramers_v:.3f}

MIDDLE Overlap:
  Jaccard similarity = {jaccard:.3f}
  {'HIGH overlap - similar vocabulary' if jaccard > 0.3 else 'LOW overlap - distinct vocabulary' if jaccard < 0.1 else 'MODERATE overlap'}

Verdict: {'PROFILES DIFFER' if p_value < 0.05 and cramers_v > 0.1 else 'NO SIGNIFICANT DIFFERENCE'}
""")

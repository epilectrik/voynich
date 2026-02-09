"""
04_section_label_differentiation.py - Test if PHARMA labels differ from other sections

Question: Do PHARMA labels differ from HERBAL labels (if present) in Brunschwig-relevant dimensions?

Note: Most labels are in PHARMA section. This test checks if label morphology
varies by section context.

Method:
1. Group labels by section (using folio mapping)
2. Compare handling signature (PREFIX profile)
3. Compare MIDDLE profile
4. Test for section-specific vocabulary
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
print("TEST 4: SECTION-LEVEL LABEL DIFFERENTIATION")
print("="*70)

# Section assignment by folio (simplified - PHARMA folios)
PHARMA_FOLIOS = {
    'f88r', 'f89r1', 'f89r2', 'f89v1', 'f89v2', 'f90r1', 'f90r2',
    'f90v1', 'f90v2', 'f93r', 'f93v', 'f94r', 'f94v', 'f95r1',
    'f95r2', 'f95v1', 'f95v2', 'f96r', 'f96v', 'f99r', 'f99v',
    'f100r', 'f100v', 'f101r1', 'f101r2', 'f101v1', 'f101v2', 'f102r1',
    'f102r2', 'f102v1', 'f102v2'
}

HERBAL_FOLIOS = {
    'f1r', 'f1v', 'f2r', 'f2v', 'f3r', 'f3v', 'f4r', 'f4v',
    'f5r', 'f5v', 'f6r', 'f6v', 'f7r', 'f7v', 'f8r', 'f8v',
    'f9r', 'f9v', 'f10r', 'f10v', 'f11r', 'f11v', 'f13r', 'f13v',
    'f14r', 'f14v', 'f15r', 'f15v', 'f16r', 'f16v', 'f17r', 'f17v',
    'f18r', 'f18v', 'f19r', 'f19v', 'f20r', 'f20v', 'f21r', 'f21v',
    'f22r', 'f22v', 'f23r', 'f23v', 'f24r', 'f24v', 'f25r', 'f25v',
    'f26r', 'f26v', 'f27r', 'f27v', 'f28r', 'f28v', 'f29r', 'f29v',
    'f30r', 'f30v', 'f31r', 'f31v', 'f32r', 'f32v', 'f33r', 'f33v',
    'f34r', 'f34v', 'f35r', 'f35v', 'f36r', 'f36v', 'f37r', 'f37v',
    'f38r', 'f38v', 'f39r', 'f39v', 'f40r', 'f40v', 'f41r', 'f41v',
    'f42r', 'f42v', 'f43r', 'f43v', 'f44r', 'f44v', 'f45r', 'f45v',
    'f46r', 'f46v', 'f47r', 'f47v', 'f48r', 'f48v', 'f49r', 'f49v',
    'f50r', 'f50v', 'f51r', 'f51v', 'f52r', 'f52v', 'f53r', 'f53v',
    'f54r', 'f54v', 'f55r', 'f55v', 'f56r', 'f56v'
}

# PREFIX handling categories
HANDLING_PREFIXES = {
    'ENERGY': {'qo', 'ch', 'sh'},
    'SCAFFOLD': {'ok', 'ot', 'ol', 'or', 'od', 'os'},
    'ANCHOR': {'da', 'sa'},
    'BARE': {None, '', 'o'}
}

def classify_prefix(prefix):
    for category, prefixes in HANDLING_PREFIXES.items():
        if prefix in prefixes:
            return category
    return 'OTHER'

def get_section(folio):
    if folio in PHARMA_FOLIOS:
        return 'PHARMA'
    elif folio in HERBAL_FOLIOS:
        return 'HERBAL'
    else:
        return 'OTHER'

# ============================================================
# STEP 1: LOAD ALL LABELS WITH SECTION
# ============================================================
print("\n--- Step 1: Loading Labels by Section ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

labels_by_section = defaultdict(list)

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])
    section = get_section(folio)

    for group in data.get('groups', []):
        # Jar
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            labels_by_section[section].append({
                'token': jar, 'type': 'jar', 'folio': folio
            })

        # Roots
        for item in group.get('roots', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                labels_by_section[section].append({
                    'token': token, 'type': 'root', 'folio': folio
                })

        # Leaves
        for item in group.get('leaves', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                labels_by_section[section].append({
                    'token': token, 'type': 'leaf', 'folio': folio
                })

print("Labels by section:")
for section, labels in labels_by_section.items():
    print(f"  {section}: {len(labels)} labels")

# ============================================================
# STEP 2: COMPARE MORPHOLOGICAL PROFILES
# ============================================================
print("\n--- Step 2: Morphological Profiles by Section ---")

def analyze_section_morphology(labels, section_name):
    prefix_counts = Counter()
    handling_counts = Counter()
    middles = set()
    suffixes = Counter()

    for label in labels:
        m = morph.extract(label['token'])
        if not m:
            continue

        prefix_counts[m.prefix] += 1
        handling_counts[classify_prefix(m.prefix)] += 1

        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes[m.suffix] += 1

    total = sum(handling_counts.values())

    print(f"\n{section_name} ({len(labels)} labels, {total} with morphology):")
    print(f"  Top prefixes: {prefix_counts.most_common(5)}")
    print(f"  Unique MIDDLEs: {len(middles)}")
    print(f"  Top suffixes: {suffixes.most_common(5)}")

    print(f"  Handling profile:")
    for cat in ['ENERGY', 'SCAFFOLD', 'ANCHOR', 'BARE', 'OTHER']:
        count = handling_counts[cat]
        pct = 100 * count / total if total > 0 else 0
        print(f"    {cat}: {count} ({pct:.1f}%)")

    return {
        'prefix_counts': dict(prefix_counts),
        'handling_counts': dict(handling_counts),
        'unique_middles': list(middles),
        'suffix_counts': dict(suffixes),
        'total': total
    }

section_profiles = {}
for section, labels in labels_by_section.items():
    section_profiles[section] = analyze_section_morphology(labels, section)

# ============================================================
# STEP 3: STATISTICAL COMPARISON (IF MULTIPLE SECTIONS)
# ============================================================
print("\n--- Step 3: Statistical Comparison ---")

sections = list(labels_by_section.keys())

if len(sections) >= 2 and all(section_profiles[s]['total'] > 0 for s in sections):
    # Compare handling profiles
    categories = ['ENERGY', 'SCAFFOLD', 'ANCHOR', 'BARE', 'OTHER']

    contingency = []
    for section in sections:
        profile = section_profiles[section]['handling_counts']
        row = [profile.get(cat, 0) for cat in categories]
        contingency.append(row)

    contingency = np.array(contingency)
    # Remove zero columns
    nonzero_cols = contingency.sum(axis=0) > 0
    contingency_clean = contingency[:, nonzero_cols]

    if contingency_clean.shape[1] >= 2 and contingency_clean.shape[0] >= 2:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_clean)
        n = contingency_clean.sum()
        cramers_v = np.sqrt(chi2 / (n * (min(contingency_clean.shape) - 1))) if n > 0 else 0

        print(f"\nChi-square test (handling profile by section):")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  p-value = {p_value:.4f}")
        print(f"  Cramer's V = {cramers_v:.3f}")
        print(f"  {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
    else:
        chi2, p_value, cramers_v = 0, 1, 0
        print("Insufficient data for chi-square test")
else:
    chi2, p_value, cramers_v = 0, 1, 0
    print("Only one section with data - cannot compare")

# ============================================================
# STEP 4: VOCABULARY OVERLAP
# ============================================================
print("\n--- Step 4: MIDDLE Vocabulary Overlap ---")

if len(sections) >= 2:
    section_middles = {}
    for section in sections:
        section_middles[section] = set(section_profiles[section]['unique_middles'])

    # Pairwise Jaccard
    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            m1 = section_middles[s1]
            m2 = section_middles[s2]
            overlap = m1 & m2
            union = m1 | m2
            jaccard = len(overlap) / len(union) if union else 0

            print(f"\n{s1} vs {s2}:")
            print(f"  {s1} unique MIDDLEs: {len(m1)}")
            print(f"  {s2} unique MIDDLEs: {len(m2)}")
            print(f"  Overlap: {len(overlap)}")
            print(f"  Jaccard: {jaccard:.3f}")
else:
    jaccard = 1.0
    print("Only one section - no overlap computation")

# ============================================================
# STEP 5: LABEL TYPE DISTRIBUTION BY SECTION
# ============================================================
print("\n--- Step 5: Label Type Distribution by Section ---")

for section, labels in labels_by_section.items():
    type_counts = Counter(l['type'] for l in labels)
    total = len(labels)
    print(f"\n{section}:")
    for ltype, count in type_counts.most_common():
        pct = 100 * count / total if total > 0 else 0
        print(f"  {ltype}: {count} ({pct:.1f}%)")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'section_label_differentiation',
    'question': 'Do labels differ by section in Brunschwig-relevant dimensions?',
    'sections': list(sections),
    'label_counts': {s: len(labels_by_section[s]) for s in sections},
    'section_profiles': {
        s: {
            'handling_counts': section_profiles[s]['handling_counts'],
            'unique_middle_count': len(section_profiles[s]['unique_middles']),
            'total_with_morph': section_profiles[s]['total']
        }
        for s in sections
    },
    'statistics': {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v),
        'significant': bool(p_value < 0.05)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results' / 'section_label_differentiation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: SECTION-LEVEL LABEL DIFFERENTIATION")
print("="*70)

print(f"""
Do labels differ by section in Brunschwig-relevant dimensions?

Sections with labels: {len(sections)}
{'- ' + chr(10).join(f'{s}: {len(labels_by_section[s])} labels' for s in sections)}

Handling Profile Comparison:
  Chi2 = {chi2:.2f}, p = {p_value:.4f}
  Cramer's V = {cramers_v:.3f}

Verdict: {'SECTION DIFFERENTIATION' if p_value < 0.05 and cramers_v > 0.1 else 'NO SIGNIFICANT DIFFERENTIATION'}

{'Sections show different label handling profiles.' if p_value < 0.05 else 'Label handling profiles do not differ significantly by section.'}
Note: Most labels are in PHARMA section, limiting cross-section comparison power.
""")

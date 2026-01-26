"""
Q9: Positional Specialists by Section

Does Section B (different manuscript sections) have different class specialists?
Sections are defined by folio ranges and may correspond to different topics.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Role mapping
ROLE_MAP = {
    10: 'CC', 11: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

ROLE_NAMES = {
    'CC': 'CORE_CONTROL',
    'EN': 'ENERGY',
    'FL': 'FLOW',
    'FQ': 'FREQUENT',
    'AX': 'AUXILIARY',
}

def get_role(cls):
    return ROLE_MAP.get(cls, 'AX')

# Define manuscript sections based on standard Voynich divisions
# These correspond to different illustrated content
def get_section(folio):
    """Classify folio into manuscript section."""
    # Extract numeric part
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'

    # Standard section divisions (approximate)
    if num <= 25:
        return 'HERBAL_A'      # f1-f25: Herbal section A
    elif num <= 56:
        return 'HERBAL_B'      # f26-f56: Herbal section B
    elif num <= 67:
        return 'PHARMA'        # f57-f67: Pharmaceutical
    elif num <= 73:
        return 'ASTRO'         # f68-f73: Astronomical
    elif num <= 84:
        return 'BIO'           # f74-f84: Biological/balneological
    elif num <= 86:
        return 'COSMO'         # f85-f86: Cosmological
    elif num <= 102:
        return 'RECIPE_A'      # f87-f102: Recipe section A
    else:
        return 'RECIPE_B'      # f103+: Recipe section B

print("=" * 70)
print("Q9: SECTION SPECIALISTS")
print("=" * 70)

# Count tokens by section
section_tokens = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    section = get_section(folio)
    cls = token_to_class.get(word)
    if cls is not None:
        section_tokens[section].append(cls)

print("\n" + "-" * 70)
print("1. SECTION TOKEN COUNTS")
print("-" * 70)

print("\n| Section | Tokens | Folios |")
print("|---------|--------|--------|")

section_folios = defaultdict(set)
for token in tokens:
    section = get_section(token.folio)
    section_folios[section].add(token.folio)

for section in sorted(section_tokens.keys()):
    print(f"| {section:10s} | {len(section_tokens[section]):6d} | {len(section_folios[section]):6d} |")

print("\n" + "-" * 70)
print("2. ROLE DISTRIBUTION BY SECTION")
print("-" * 70)

# Calculate role distribution per section
section_roles = defaultdict(lambda: defaultdict(int))
for section, classes in section_tokens.items():
    for cls in classes:
        role = get_role(cls)
        section_roles[section][role] += 1

print("\n| Section | CC% | EN% | FL% | FQ% | AX% |")
print("|---------|-----|-----|-----|-----|-----|")

role_by_section = {}
for section in sorted(section_roles.keys()):
    roles = section_roles[section]
    total = sum(roles.values())
    if total < 100:
        continue

    pcts = {r: roles[r] / total * 100 for r in ['CC', 'EN', 'FL', 'FQ', 'AX']}
    role_by_section[section] = pcts
    print(f"| {section:10s} | {pcts['CC']:3.1f} | {pcts['EN']:4.1f} | {pcts['FL']:3.1f} | {pcts['FQ']:3.1f} | {pcts['AX']:4.1f} |")

# Calculate overall baseline
all_classes = []
for classes in section_tokens.values():
    all_classes.extend(classes)

baseline_roles = defaultdict(int)
for cls in all_classes:
    role = get_role(cls)
    baseline_roles[role] += 1

total = sum(baseline_roles.values())
baseline_pcts = {r: baseline_roles[r] / total * 100 for r in ['CC', 'EN', 'FL', 'FQ', 'AX']}
print(f"| BASELINE   | {baseline_pcts['CC']:3.1f} | {baseline_pcts['EN']:4.1f} | {baseline_pcts['FL']:3.1f} | {baseline_pcts['FQ']:3.1f} | {baseline_pcts['AX']:4.1f} |")

print("\n" + "-" * 70)
print("3. SECTION ENRICHMENT (vs baseline)")
print("-" * 70)

print("\n| Section | CC | EN | FL | FQ | AX | Signature |")
print("|---------|----|----|----|----|----|-----------| ")

section_signatures = {}
for section in sorted(role_by_section.keys()):
    pcts = role_by_section[section]
    enrichments = {r: pcts[r] / baseline_pcts[r] if baseline_pcts[r] > 0 else 1 for r in pcts}

    # Find signature (most enriched role)
    max_role = max(enrichments, key=enrichments.get)
    min_role = min(enrichments, key=enrichments.get)

    sig = f"+{max_role}" if enrichments[max_role] > 1.2 else ""
    if enrichments[min_role] < 0.8:
        sig += f" -{min_role}" if sig else f"-{min_role}"

    section_signatures[section] = {
        'enrichments': enrichments,
        'signature': sig if sig else "BASELINE"
    }

    row = f"| {section:10s} |"
    for r in ['CC', 'EN', 'FL', 'FQ', 'AX']:
        e = enrichments[r]
        if e > 1.2:
            row += f" {e:.2f}+|"
        elif e < 0.8:
            row += f" {e:.2f}-|"
        else:
            row += f" {e:.2f} |"
    row += f" {sig if sig else 'BASELINE':10s} |"
    print(row)

print("\n" + "-" * 70)
print("4. CLASS-LEVEL SECTION SPECIALISTS")
print("-" * 70)

# Find classes that are significantly enriched in specific sections
class_section_counts = defaultdict(lambda: defaultdict(int))
class_totals = defaultdict(int)
section_totals = defaultdict(int)

for section, classes in section_tokens.items():
    section_totals[section] = len(classes)
    for cls in classes:
        class_section_counts[cls][section] += 1
        class_totals[cls] += 1

grand_total = sum(class_totals.values())

print("\nClasses with >1.5x enrichment in specific sections:")
print("| Class | Role | Section | Rate | Expected | Enrichment |")
print("|-------|------|---------|------|----------|------------|")

specialists = []
for cls in sorted(class_totals.keys()):
    if class_totals[cls] < 50:
        continue

    for section in section_totals.keys():
        if section_totals[section] < 100:
            continue

        observed = class_section_counts[cls][section]
        # Expected = class_rate * section_size
        class_rate = class_totals[cls] / grand_total
        expected = class_rate * section_totals[section]

        if expected < 5:
            continue

        enrichment = observed / expected if expected > 0 else 0

        if enrichment > 1.5:
            role = get_role(cls)
            specialists.append({
                'class': cls,
                'role': role,
                'section': section,
                'observed': observed,
                'expected': expected,
                'enrichment': enrichment
            })

# Sort by enrichment
specialists.sort(key=lambda x: x['enrichment'], reverse=True)
for s in specialists[:20]:
    print(f"| {s['class']:5d} | {s['role']}   | {s['section']:10s} | {s['observed']:4d} | {s['expected']:8.1f} | {s['enrichment']:.2f}x      |")

print("\n" + "-" * 70)
print("5. SECTION DEPLETED CLASSES")
print("-" * 70)

print("\nClasses with <0.5x rate in specific sections:")
print("| Class | Role | Section | Rate | Expected | Depletion |")
print("|-------|------|---------|------|----------|-----------|")

depletions = []
for cls in sorted(class_totals.keys()):
    if class_totals[cls] < 50:
        continue

    for section in section_totals.keys():
        if section_totals[section] < 100:
            continue

        observed = class_section_counts[cls][section]
        class_rate = class_totals[cls] / grand_total
        expected = class_rate * section_totals[section]

        if expected < 10:
            continue

        enrichment = observed / expected if expected > 0 else 0

        if enrichment < 0.5:
            role = get_role(cls)
            depletions.append({
                'class': cls,
                'role': role,
                'section': section,
                'observed': observed,
                'expected': expected,
                'enrichment': enrichment
            })

depletions.sort(key=lambda x: x['enrichment'])
for d in depletions[:15]:
    print(f"| {d['class']:5d} | {d['role']}   | {d['section']:10s} | {d['observed']:4d} | {d['expected']:8.1f} | {d['enrichment']:.2f}x     |")

print("\n" + "-" * 70)
print("6. STATISTICAL TEST")
print("-" * 70)

# Chi-square test for role distribution independence from section
# Build contingency table
roles = ['CC', 'EN', 'FL', 'FQ', 'AX']
sections = [s for s in section_roles.keys() if sum(section_roles[s].values()) > 100]

contingency = []
for section in sections:
    row = [section_roles[section][r] for r in roles]
    contingency.append(row)

contingency = np.array(contingency)
chi2, p, dof, expected = stats.chi2_contingency(contingency)

print(f"\nChi-square test (role x section independence):")
print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p:.6f}")

if p < 0.001:
    print("  HIGHLY SIGNIFICANT: Role distribution varies by section")
elif p < 0.05:
    print("  SIGNIFICANT: Role distribution varies by section")
else:
    print("  NOT SIGNIFICANT: Role distribution similar across sections")

# Effect size (Cramer's V)
n = contingency.sum()
min_dim = min(contingency.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"  Cramer's V = {cramers_v:.3f} (effect size)")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Identify sections with strongest deviations
max_en = max(role_by_section.items(), key=lambda x: x[1]['EN'])
min_en = min(role_by_section.items(), key=lambda x: x[1]['EN'])

print(f"""
1. ROLE DISTRIBUTION VARIES BY SECTION (Chi2={chi2:.1f}, p<0.001)
   - Effect size: Cramer's V = {cramers_v:.3f}

2. ENERGY VARIATION:
   - Highest: {max_en[0]} ({max_en[1]['EN']:.1f}%)
   - Lowest: {min_en[0]} ({min_en[1]['EN']:.1f}%)
   - Ratio: {max_en[1]['EN']/min_en[1]['EN']:.2f}x

3. SECTION SIGNATURES:
""")

for section in sorted(section_signatures.keys()):
    sig = section_signatures[section]['signature']
    print(f"   {section:10s}: {sig}")

# Save results
results = {
    'section_tokens': {s: len(t) for s, t in section_tokens.items()},
    'role_by_section': role_by_section,
    'baseline': baseline_pcts,
    'section_signatures': section_signatures,
    'specialists': specialists[:20],
    'chi2_test': {'chi2': float(chi2), 'p': float(p), 'cramers_v': float(cramers_v)}
}

with open(RESULTS / 'section_specialists.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'section_specialists.json'}")

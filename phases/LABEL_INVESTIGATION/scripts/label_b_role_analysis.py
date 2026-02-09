"""
label_b_role_analysis.py - Check what B roles label PP bases appear in

Per C571: PREFIX selects role, MIDDLE carries material
Per C570: EN prefixes (ch/sh/qo) = operations, AX prefixes (ok/ot/bare) = scaffolding

Question: When label PP bases appear in B, are they in AX (material) or EN (operation) roles?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("LABEL PP BASES IN B: ROLE ANALYSIS")
print("="*70)

# Role classification by prefix (from C570-C571)
EN_PREFIXES = {'ch', 'sh', 'qo'}  # Operations
AX_MED_PREFIXES = {'ok', 'ot'}     # Auxiliary medium
AX_INIT_PREFIXES = {'ych', 'ysh'}  # Auxiliary initial (articulated)
# Bare prefixes (no prefix or o-only) = AX_FINAL

def classify_role(prefix):
    """Classify token role by prefix."""
    if prefix in EN_PREFIXES:
        return 'EN'
    elif prefix in AX_MED_PREFIXES:
        return 'AX_MED'
    elif prefix in AX_INIT_PREFIXES:
        return 'AX_INIT'
    elif prefix is None or prefix == '' or prefix == 'o':
        return 'AX_FINAL'
    else:
        return 'OTHER'

# ============================================================
# STEP 1: LOAD LABEL PP BASES
# ============================================================
print("\n--- Step 1: Loading Label PP Bases ---")

# Load from previous analysis
pipeline_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_pipeline.json'
with open(pipeline_path, 'r', encoding='utf-8') as f:
    pipeline_data = json.load(f)

# Extract unique PP bases from labels
label_pp_bases = set()
label_details = {}

for label in pipeline_data['label_details']:
    pp_base = label.get('pp_base')
    if pp_base:
        label_pp_bases.add(pp_base)
        if pp_base not in label_details:
            label_details[pp_base] = {
                'example_label': label['token'],
                'label_type': label['type'],
                'label_folio': label['folio']
            }

print(f"Unique PP bases from labels: {len(label_pp_bases)}")

# ============================================================
# STEP 2: BUILD B VOCABULARY BY MIDDLE AND ROLE
# ============================================================
print("\n--- Step 2: Analyzing B Tokens by MIDDLE and Role ---")

# For each PP base, count what roles it appears in
pp_base_roles = defaultdict(Counter)
pp_base_examples = defaultdict(list)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    role = classify_role(m.prefix)

    # Check if this MIDDLE contains any label PP base
    for pp_base in label_pp_bases:
        if pp_base in m.middle:
            pp_base_roles[pp_base][role] += 1
            if len(pp_base_examples[pp_base]) < 5:
                pp_base_examples[pp_base].append({
                    'word': t.word,
                    'middle': m.middle,
                    'prefix': m.prefix,
                    'role': role,
                    'folio': t.folio
                })

print(f"PP bases found in B: {len(pp_base_roles)}")

# ============================================================
# STEP 3: AGGREGATE ROLE DISTRIBUTION
# ============================================================
print("\n--- Step 3: Role Distribution ---")

total_by_role = Counter()
for pp_base, roles in pp_base_roles.items():
    for role, count in roles.items():
        total_by_role[role] += count

total = sum(total_by_role.values())

print(f"\nOverall role distribution of label PP bases in B:")
print(f"{'Role':<12} {'Count':<10} {'Percent'}")
print("-" * 35)
for role in ['EN', 'AX_MED', 'AX_INIT', 'AX_FINAL', 'OTHER']:
    count = total_by_role[role]
    pct = 100 * count / total if total > 0 else 0
    print(f"{role:<12} {count:<10} {pct:.1f}%")

# Compare to overall B role distribution
print("\n--- Baseline: Overall B Role Distribution ---")
b_baseline_roles = Counter()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m:
        role = classify_role(m.prefix)
        b_baseline_roles[role] += 1

b_total = sum(b_baseline_roles.values())

print(f"{'Role':<12} {'B baseline':<12} {'Label PP':<12} {'Ratio'}")
print("-" * 50)
for role in ['EN', 'AX_MED', 'AX_INIT', 'AX_FINAL', 'OTHER']:
    b_pct = 100 * b_baseline_roles[role] / b_total if b_total > 0 else 0
    label_pct = 100 * total_by_role[role] / total if total > 0 else 0
    ratio = label_pct / b_pct if b_pct > 0 else 0
    print(f"{role:<12} {b_pct:>6.1f}%     {label_pct:>6.1f}%      {ratio:.2f}x")

# ============================================================
# STEP 4: EXAMPLES
# ============================================================
print("\n--- Step 4: Example Label PP Bases in B ---")

# Show a few interesting examples
interesting_bases = ['ol', 'or', 'ai', 'ey', 'e', 'k']

for pp_base in interesting_bases:
    if pp_base in pp_base_roles:
        roles = pp_base_roles[pp_base]
        total_occ = sum(roles.values())
        examples = pp_base_examples.get(pp_base, [])

        label_info = label_details.get(pp_base, {})

        print(f"\nPP base '{pp_base}' (from label: {label_info.get('example_label', '?')}):")
        print(f"  B occurrences: {total_occ}")
        print(f"  Roles: {dict(roles)}")
        if examples:
            print(f"  Example B tokens:")
            for ex in examples[:3]:
                print(f"    {ex['word']} ({ex['role']}, {ex['folio']})")

# ============================================================
# STEP 5: JAR vs CONTENT ROLE COMPARISON
# ============================================================
print("\n--- Step 5: Jar vs Content Role Distribution ---")

jar_pp_bases = set()
content_pp_bases = set()

for label in pipeline_data['label_details']:
    pp_base = label.get('pp_base')
    if pp_base:
        if label['type'] == 'jar':
            jar_pp_bases.add(pp_base)
        elif label['type'] in ['root', 'leaf']:
            content_pp_bases.add(pp_base)

# Role distribution for jar vs content PP bases
jar_roles = Counter()
content_roles = Counter()

for pp_base, roles in pp_base_roles.items():
    if pp_base in jar_pp_bases:
        for role, count in roles.items():
            jar_roles[role] += count
    if pp_base in content_pp_bases:
        for role, count in roles.items():
            content_roles[role] += count

jar_total = sum(jar_roles.values())
content_total = sum(content_roles.values())

print(f"\n{'Role':<12} {'Jar PP %':<12} {'Content PP %'}")
print("-" * 40)
for role in ['EN', 'AX_MED', 'AX_INIT', 'AX_FINAL', 'OTHER']:
    jar_pct = 100 * jar_roles[role] / jar_total if jar_total > 0 else 0
    content_pct = 100 * content_roles[role] / content_total if content_total > 0 else 0
    print(f"{role:<12} {jar_pct:>6.1f}%      {content_pct:>6.1f}%")

# ============================================================
# STEP 6: LINE POSITION ANALYSIS
# ============================================================
print("\n--- Step 6: Line Position Analysis ---")

# Where in lines do label PP bases appear?
pp_base_positions = defaultdict(list)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    for pp_base in label_pp_bases:
        if pp_base in m.middle:
            # Get relative position in line
            # We need line info - use position if available
            pp_base_positions[pp_base].append(t.position if hasattr(t, 'position') else 0)

# For now, just check if we can get position data
if pp_base_positions:
    sample_base = list(pp_base_positions.keys())[0]
    print(f"Sample positions for '{sample_base}': {pp_base_positions[sample_base][:10]}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'summary': {
        'unique_label_pp_bases': len(label_pp_bases),
        'pp_bases_found_in_b': len(pp_base_roles)
    },
    'role_distribution': {
        'label_pp_in_b': dict(total_by_role),
        'b_baseline': dict(b_baseline_roles)
    },
    'jar_vs_content': {
        'jar_roles': dict(jar_roles),
        'content_roles': dict(content_roles)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_role_analysis.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: LABEL PP BASES IN B ROLES")
print("="*70)

# Calculate AX vs EN ratio
ax_total = total_by_role['AX_MED'] + total_by_role['AX_INIT'] + total_by_role['AX_FINAL']
en_total = total_by_role['EN']

ax_pct = 100 * ax_total / total if total > 0 else 0
en_pct = 100 * en_total / total if total > 0 else 0

# Baseline
b_ax = b_baseline_roles['AX_MED'] + b_baseline_roles['AX_INIT'] + b_baseline_roles['AX_FINAL']
b_en = b_baseline_roles['EN']
b_ax_pct = 100 * b_ax / b_total if b_total > 0 else 0
b_en_pct = 100 * b_en / b_total if b_total > 0 else 0

print(f"""
Do label PP bases appear in B where we'd expect materials?

Per C570-C571:
  - AX roles (ok/ot/bare) = scaffolding, carries material
  - EN roles (ch/sh/qo) = operations

Label PP bases in B:
  - AX roles: {ax_pct:.1f}%
  - EN roles: {en_pct:.1f}%

B baseline:
  - AX roles: {b_ax_pct:.1f}%
  - EN roles: {b_en_pct:.1f}%

Interpretation:
  Label PP bases appear {'MORE' if ax_pct > b_ax_pct else 'LESS'} often in AX (material) roles
  than the B baseline ({ax_pct:.1f}% vs {b_ax_pct:.1f}%).

  This {'SUPPORTS' if ax_pct > b_ax_pct else 'DOES NOT SUPPORT'} the hypothesis that
  label vocabulary preferentially appears in material-carrying positions.
""")

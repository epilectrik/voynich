"""
label_preparation_ops.py - Check if label PP bases appear with preparation operations

Preparation MIDDLEs (from REVERSE_BRUNSCHWIG_V2):
- te = GATHER (selection)
- pch = CHOP (mechanical)
- lch = STRIP (separation)
- tch = POUND (intensive)
- ksh = BREAK/WASH (rare)

Question: When label PP bases appear in B, do they co-occur with preparation operations?
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
print("LABEL PP BASES AND PREPARATION OPERATIONS")
print("="*70)

# Preparation MIDDLEs
PREP_MIDDLES = {
    'te': 'GATHER',
    'pch': 'CHOP',
    'lch': 'STRIP',
    'tch': 'POUND',
    'ksh': 'BREAK/WASH'
}

# ============================================================
# STEP 1: LOAD LABEL PP BASES
# ============================================================
print("\n--- Step 1: Loading Label PP Bases ---")

pipeline_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_pipeline.json'
with open(pipeline_path, 'r', encoding='utf-8') as f:
    pipeline_data = json.load(f)

label_pp_bases = set()
jar_pp_bases = set()
content_pp_bases = set()

for label in pipeline_data['label_details']:
    pp_base = label.get('pp_base')
    if pp_base:
        label_pp_bases.add(pp_base)
        if label['type'] == 'jar':
            jar_pp_bases.add(pp_base)
        elif label['type'] in ['root', 'leaf']:
            content_pp_bases.add(pp_base)

print(f"Total label PP bases: {len(label_pp_bases)}")
print(f"Jar PP bases: {len(jar_pp_bases)}")
print(f"Content PP bases: {len(content_pp_bases)}")

# ============================================================
# STEP 2: FIND LINES WITH BOTH LABEL PP AND PREP OPS
# ============================================================
print("\n--- Step 2: Finding Lines with Both Label PP and Prep Ops ---")

# Build line-level data
lines = defaultdict(list)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        key = (t.folio, t.line)
        lines[key].append({
            'word': t.word,
            'middle': m.middle,
            'prefix': m.prefix
        })

# For each line, check:
# 1. Does it contain a label PP base?
# 2. Does it contain a preparation MIDDLE?

cooccurrence = []
label_pp_lines = 0
prep_op_lines = 0
both_lines = 0

for (folio, line_num), tokens in lines.items():
    middles = [t['middle'] for t in tokens]

    # Check for label PP bases
    has_label_pp = False
    label_pps_found = []
    for m in middles:
        for pp in label_pp_bases:
            if pp in m:
                has_label_pp = True
                label_pps_found.append(pp)
                break

    # Check for preparation MIDDLEs
    has_prep = False
    prep_found = []
    for m in middles:
        for prep_m, prep_name in PREP_MIDDLES.items():
            if prep_m in m:
                has_prep = True
                prep_found.append((prep_m, prep_name))
                break

    if has_label_pp:
        label_pp_lines += 1
    if has_prep:
        prep_op_lines += 1
    if has_label_pp and has_prep:
        both_lines += 1
        cooccurrence.append({
            'folio': folio,
            'line': line_num,
            'label_pps': list(set(label_pps_found)),
            'prep_ops': list(set(prep_found)),
            'tokens': [t['word'] for t in tokens]
        })

total_lines = len(lines)

print(f"\nTotal B lines: {total_lines}")
print(f"Lines with label PP bases: {label_pp_lines} ({100*label_pp_lines/total_lines:.1f}%)")
print(f"Lines with prep operations: {prep_op_lines} ({100*prep_op_lines/total_lines:.1f}%)")
print(f"Lines with BOTH: {both_lines} ({100*both_lines/total_lines:.1f}%)")

# Expected if independent
expected_both = (label_pp_lines / total_lines) * (prep_op_lines / total_lines) * total_lines
print(f"Expected if independent: {expected_both:.1f}")
print(f"Observed/Expected: {both_lines/expected_both:.2f}x")

# ============================================================
# STEP 3: EXAMPLE CO-OCCURRENCES
# ============================================================
print("\n--- Step 3: Example Co-occurrences ---")

# Show some examples
for i, co in enumerate(cooccurrence[:10]):
    print(f"\n{co['folio']} line {co['line']}:")
    print(f"  Label PP bases: {co['label_pps']}")
    print(f"  Prep operations: {co['prep_ops']}")
    print(f"  Tokens: {' '.join(co['tokens'][:8])}{'...' if len(co['tokens']) > 8 else ''}")

# ============================================================
# STEP 4: WHICH PREP OPS CO-OCCUR WITH LABELS?
# ============================================================
print("\n--- Step 4: Prep Op Distribution with Labels ---")

prep_with_labels = Counter()
prep_baseline = Counter()

for (folio, line_num), tokens in lines.items():
    middles = [t['middle'] for t in tokens]

    # Check for label PP
    has_label_pp = any(pp in m for m in middles for pp in label_pp_bases)

    # Count prep ops
    for m in middles:
        for prep_m, prep_name in PREP_MIDDLES.items():
            if prep_m in m:
                prep_baseline[prep_name] += 1
                if has_label_pp:
                    prep_with_labels[prep_name] += 1

print(f"\n{'Prep Op':<15} {'With Labels':<15} {'Total':<10} {'Rate'}")
print("-" * 50)
for prep_name in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'BREAK/WASH']:
    with_labels = prep_with_labels[prep_name]
    total = prep_baseline[prep_name]
    rate = with_labels / total if total > 0 else 0
    print(f"{prep_name:<15} {with_labels:<15} {total:<10} {100*rate:.1f}%")

# ============================================================
# STEP 5: JAR vs CONTENT WITH PREP OPS
# ============================================================
print("\n--- Step 5: Jar vs Content with Prep Operations ---")

jar_with_prep = 0
content_with_prep = 0

for (folio, line_num), tokens in lines.items():
    middles = [t['middle'] for t in tokens]

    has_jar = any(pp in m for m in middles for pp in jar_pp_bases)
    has_content = any(pp in m for m in middles for pp in content_pp_bases)
    has_prep = any(prep_m in m for m in middles for prep_m in PREP_MIDDLES.keys())

    if has_jar and has_prep:
        jar_with_prep += 1
    if has_content and has_prep:
        content_with_prep += 1

jar_lines = sum(1 for k, toks in lines.items() if any(pp in t['middle'] for t in toks for pp in jar_pp_bases))
content_lines = sum(1 for k, toks in lines.items() if any(pp in t['middle'] for t in toks for pp in content_pp_bases))

print(f"\nJar PP lines with prep ops: {jar_with_prep}/{jar_lines} ({100*jar_with_prep/jar_lines:.1f}%)" if jar_lines > 0 else "No jar lines")
print(f"Content PP lines with prep ops: {content_with_prep}/{content_lines} ({100*content_with_prep/content_lines:.1f}%)" if content_lines > 0 else "No content lines")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: LABEL PP BASES AND PREPARATION OPERATIONS")
print("="*70)

print(f"""
Do label PP bases appear in B lines with preparation operations?

Co-occurrence rate:
  - Lines with BOTH label PP AND prep op: {both_lines}
  - Expected if independent: {expected_both:.1f}
  - Ratio: {both_lines/expected_both:.2f}x

{'ENRICHED' if both_lines > expected_both * 1.1 else 'DEPLETED' if both_lines < expected_both * 0.9 else 'AS EXPECTED'}:
Label PP bases {'DO' if both_lines > expected_both else 'DO NOT'} preferentially co-occur with preparation operations.

This {'SUPPORTS' if both_lines > expected_both else 'DOES NOT SUPPORT'} the hypothesis that labels identify
materials that appear in material-processing contexts (GATHER, CHOP, STRIP, POUND).
""")

# Save results
output = {
    'total_lines': total_lines,
    'label_pp_lines': label_pp_lines,
    'prep_op_lines': prep_op_lines,
    'both_lines': both_lines,
    'expected_both': expected_both,
    'ratio': both_lines / expected_both if expected_both > 0 else 0,
    'prep_distribution': dict(prep_with_labels),
    'examples': cooccurrence[:20]
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_prep_ops.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")

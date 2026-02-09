"""
05_prep_operation_cooccurrence.py - Test if label MIDDLEs co-occur with prep operations

Question: Do label MIDDLEs preferentially co-occur with specific preparation operations?

Method:
1. For each label MIDDLE, find B lines where it appears
2. Check if those lines contain preparation MIDDLEs (te, pch, lch, tch, ksh)
3. Compute prep operation distribution for each label type (jar, root, leaf)
4. Test for non-uniform distribution

Expected under Brunschwig:
- Root labels -> CHOP (pch), POUND (tch)
- Leaf labels -> STRIP (lch), GATHER (te)
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
print("TEST 5: LABEL MIDDLES AND PREP OPERATION CO-OCCURRENCE")
print("="*70)

# Preparation MIDDLEs (from Brunschwig interpretation)
PREP_MIDDLES = {
    'te': 'GATHER',
    'pch': 'CHOP',
    'lch': 'STRIP',
    'tch': 'POUND',
    'ksh': 'BREAK'
}

# ============================================================
# STEP 1: LOAD LABELS BY TYPE
# ============================================================
print("\n--- Step 1: Loading Labels by Type ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

labels_by_type = defaultdict(list)

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        # Jar
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            labels_by_type['jar'].append({'token': jar, 'folio': folio})

        # Roots
        for item in group.get('roots', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                labels_by_type['root'].append({'token': token, 'folio': folio})

        # Leaves
        for item in group.get('leaves', []):
            if isinstance(item, dict):
                token = item.get('token', '')
            elif isinstance(item, str):
                token = item
            else:
                continue
            if token:
                labels_by_type['leaf'].append({'token': token, 'folio': folio})

print("Labels by type:")
for ltype, labels in labels_by_type.items():
    print(f"  {ltype}: {len(labels)}")

# ============================================================
# STEP 2: BUILD LINE-LEVEL B DATA
# ============================================================
print("\n--- Step 2: Building B Line Data ---")

# Build line -> tokens mapping
b_lines = defaultdict(list)
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        key = (t.folio, t.line)
        b_lines[key].append({
            'word': t.word,
            'middle': m.middle
        })

print(f"B lines with morphology: {len(b_lines)}")

# ============================================================
# STEP 3: FOR EACH LABEL TYPE, FIND PREP CO-OCCURRENCE
# ============================================================
print("\n--- Step 3: Prep Operation Co-occurrence by Label Type ---")

def find_prep_cooccurrence(labels, label_type):
    """Find which prep operations co-occur with label MIDDLEs in B"""

    # Get label MIDDLEs
    label_middles = set()
    for label in labels:
        m = morph.extract(label['token'])
        if m and m.middle:
            label_middles.add(m.middle)

    print(f"\n{label_type.upper()}: {len(label_middles)} unique MIDDLEs")

    # For each B line, check if it has label MIDDLE and which prep ops
    prep_counts = Counter()  # Prep ops on lines with label MIDDLEs
    baseline_prep = Counter()  # All prep ops in B
    lines_with_label = 0
    lines_with_label_and_prep = 0

    for (folio, line_num), tokens in b_lines.items():
        middles = [t['middle'] for t in tokens]

        # Check for label MIDDLE
        has_label_middle = any(
            lm in mid or mid in lm  # Allow substring match
            for mid in middles
            for lm in label_middles
            if len(lm) >= 2
        )

        # Check for prep ops
        prep_on_line = []
        for mid in middles:
            for prep_m, prep_name in PREP_MIDDLES.items():
                if prep_m in mid:
                    prep_on_line.append(prep_name)
                    baseline_prep[prep_name] += 1

        if has_label_middle:
            lines_with_label += 1
            for prep in prep_on_line:
                prep_counts[prep] += 1
            if prep_on_line:
                lines_with_label_and_prep += 1

    print(f"  Lines with label MIDDLE: {lines_with_label}")
    print(f"  Lines with label AND prep: {lines_with_label_and_prep}")

    # Compute enrichment vs baseline
    print(f"\n  Prep operation distribution:")
    print(f"  {'Prep Op':<10} {'With Label':<12} {'Baseline':<12} {'Enrichment'}")
    print("  " + "-" * 50)

    enrichments = {}
    for prep_name in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'BREAK']:
        with_label = prep_counts[prep_name]
        baseline = baseline_prep[prep_name]

        # Compute enrichment ratio
        if lines_with_label > 0 and len(b_lines) > 0:
            label_rate = with_label / lines_with_label
            baseline_rate = baseline / len(b_lines)
            enrichment = label_rate / baseline_rate if baseline_rate > 0 else 0
        else:
            enrichment = 0

        enrichments[prep_name] = enrichment
        print(f"  {prep_name:<10} {with_label:<12} {baseline:<12} {enrichment:.2f}x")

    return {
        'label_middles': list(label_middles),
        'lines_with_label': lines_with_label,
        'lines_with_label_and_prep': lines_with_label_and_prep,
        'prep_counts': dict(prep_counts),
        'baseline_prep': dict(baseline_prep),
        'enrichments': enrichments
    }

results_by_type = {}
for label_type, labels in labels_by_type.items():
    results_by_type[label_type] = find_prep_cooccurrence(labels, label_type)

# ============================================================
# STEP 4: STATISTICAL TESTS
# ============================================================
print("\n--- Step 4: Statistical Tests ---")

# Test if jar, root, leaf have different prep profiles
# Build contingency table
label_types = ['jar', 'root', 'leaf']
prep_ops = ['GATHER', 'CHOP', 'STRIP', 'POUND', 'BREAK']

contingency = []
for ltype in label_types:
    row = [results_by_type[ltype]['prep_counts'].get(p, 0) for p in prep_ops]
    contingency.append(row)

contingency = np.array(contingency)

# Remove zero columns
nonzero_cols = contingency.sum(axis=0) > 0
contingency_clean = contingency[:, nonzero_cols]
prep_ops_clean = [p for p, nz in zip(prep_ops, nonzero_cols) if nz]

if contingency_clean.shape[1] >= 2 and contingency_clean.sum() > 0:
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_clean)
    n = contingency_clean.sum()
    cramers_v = np.sqrt(chi2 / (n * (min(contingency_clean.shape) - 1))) if n > 0 else 0

    print(f"\nChi-square test (prep ops by label type):")
    print(f"  Chi2 = {chi2:.2f}")
    print(f"  p-value = {p_value:.4f}")
    print(f"  Cramer's V = {cramers_v:.3f}")
    print(f"  {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
else:
    chi2, p_value, cramers_v = 0, 1, 0
    print("Insufficient data for chi-square test")

# ============================================================
# STEP 5: BRUNSCHWIG PREDICTION CHECK
# ============================================================
print("\n--- Step 5: Brunschwig Prediction Check ---")

print("""
Brunschwig prediction:
- Roots -> CHOP (pch), POUND (tch) - intensive preparation
- Leaves -> STRIP (lch), GATHER (te) - gentle handling
""")

# Calculate prediction alignment
root_intensive = (
    results_by_type['root']['prep_counts'].get('CHOP', 0) +
    results_by_type['root']['prep_counts'].get('POUND', 0)
)
root_gentle = (
    results_by_type['root']['prep_counts'].get('STRIP', 0) +
    results_by_type['root']['prep_counts'].get('GATHER', 0)
)

leaf_intensive = (
    results_by_type['leaf']['prep_counts'].get('CHOP', 0) +
    results_by_type['leaf']['prep_counts'].get('POUND', 0)
)
leaf_gentle = (
    results_by_type['leaf']['prep_counts'].get('STRIP', 0) +
    results_by_type['leaf']['prep_counts'].get('GATHER', 0)
)

print(f"\nActual distribution:")
print(f"  ROOT - Intensive (CHOP+POUND): {root_intensive}")
print(f"  ROOT - Gentle (STRIP+GATHER): {root_gentle}")
print(f"  LEAF - Intensive (CHOP+POUND): {leaf_intensive}")
print(f"  LEAF - Gentle (STRIP+GATHER): {leaf_gentle}")

# Fisher's exact for root intensive vs leaf gentle
contingency_pred = [[root_intensive, root_gentle], [leaf_intensive, leaf_gentle]]
if sum(sum(row) for row in contingency_pred) > 0:
    odds_ratio, p_fisher = stats.fisher_exact(contingency_pred)
    print(f"\nFisher's exact (root intensive vs leaf gentle):")
    print(f"  Odds ratio = {odds_ratio:.2f}")
    print(f"  p-value = {p_fisher:.4f}")
    print(f"  {'SUPPORTS' if odds_ratio > 1 and p_fisher < 0.05 else 'DOES NOT SUPPORT'} Brunschwig prediction")
else:
    odds_ratio, p_fisher = 1, 1
    print("Insufficient data for Fisher's exact")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'prep_operation_cooccurrence',
    'question': 'Do label MIDDLEs preferentially co-occur with specific preparation operations?',
    'results_by_type': {
        ltype: {
            'label_count': len(labels_by_type[ltype]),
            'unique_middles': len(results['label_middles']),
            'lines_with_label': results['lines_with_label'],
            'lines_with_label_and_prep': results['lines_with_label_and_prep'],
            'prep_counts': results['prep_counts'],
            'enrichments': results['enrichments']
        }
        for ltype, results in results_by_type.items()
    },
    'overall_statistics': {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v),
        'significant': bool(p_value < 0.05)
    },
    'brunschwig_prediction': {
        'root_intensive': int(root_intensive),
        'root_gentle': int(root_gentle),
        'leaf_intensive': int(leaf_intensive),
        'leaf_gentle': int(leaf_gentle),
        'fisher_odds_ratio': float(odds_ratio),
        'fisher_p_value': float(p_fisher),
        'supports_prediction': bool(odds_ratio > 1 and p_fisher < 0.05)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results' / 'prep_operation_cooccurrence.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: LABEL-PREP OPERATION CO-OCCURRENCE")
print("="*70)

print(f"""
Do label MIDDLEs preferentially co-occur with specific preparation operations?

Chi-square test (prep ops by label type):
  Chi2 = {chi2:.2f}, p = {p_value:.4f}
  Cramer's V = {cramers_v:.3f}

Brunschwig Prediction (root=intensive, leaf=gentle):
  Fisher's exact: odds ratio = {odds_ratio:.2f}, p = {p_fisher:.4f}

Verdict: {'PREP OP DIFFERENTIATION' if p_value < 0.05 else 'NO SIGNIFICANT DIFFERENTIATION'}

{'Different label types show different prep operation profiles.' if p_value < 0.05 else 'Label types do NOT show significantly different prep operation profiles.'}

Brunschwig alignment: {'SUPPORTED' if odds_ratio > 1 and p_fisher < 0.05 else 'NOT SUPPORTED'}
""")

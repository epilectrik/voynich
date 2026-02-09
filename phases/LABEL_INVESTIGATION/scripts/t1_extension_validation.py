"""
t1_extension_validation.py - Extension Validation for C923 Promotion

Goal: Promote C923 from Tier 3 to Tier 2 by analyzing full 222-label sample.

C923 claims: Extensions bifurcate into identification (r,a,o,k) vs operational (h,d,t)
- r-extension 10.9x enriched in labels (n=25)
- h/d/t absent from labels (0%)

This test:
1. Loads all 222 labels from PHARMA_LABEL_DECODING
2. Classifies RI vs PP using morphology
3. Extracts extension characters from RI tokens
4. Compares to Currier A TEXT RI baseline (per expert recommendation)
5. Reports chi-square + Cramer's V effect size
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 1: EXTENSION VALIDATION (C923 PROMOTION)")
print("="*70)

# ============================================================
# STEP 1: LOAD ALL LABELS FROM PHARMA_LABEL_DECODING
# ============================================================
print("\n--- Step 1: Loading Labels ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

all_labels = []
folio_labels = defaultdict(list)

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    # Extract labels from groups
    groups = data.get('groups', [])
    for group in groups:
        # Handle jar labels
        jar = group.get('jar')
        if jar:
            # Skip if jar is a list (uncertain/multiple values)
            if isinstance(jar, str):
                all_labels.append({'token': jar, 'folio': folio, 'type': 'jar'})
                folio_labels[folio].append({'token': jar, 'type': 'jar'})

        # Handle content labels (roots, leaves, labels)
        for key in ['roots', 'leaves', 'labels']:
            items = group.get(key, [])
            for item in items:
                if isinstance(item, dict):
                    token = item.get('token', '')
                elif isinstance(item, str):
                    token = item
                else:
                    continue  # Skip non-string items
                if token and isinstance(token, str):
                    content_type = 'root' if key == 'roots' else 'leaf' if key == 'leaves' else 'content'
                    all_labels.append({'token': token, 'folio': folio, 'type': content_type})
                    folio_labels[folio].append({'token': token, 'type': content_type})

print(f"Loaded {len(all_labels)} labels from {len(label_files)} files")
print(f"Folios with labels: {len(folio_labels)}")

# Show distribution by type
type_counts = Counter(l['type'] for l in all_labels)
print(f"Label types: {dict(type_counts)}")

# ============================================================
# STEP 2: BUILD PP VOCABULARY (for RI classification)
# ============================================================
print("\n--- Step 2: Building PP Vocabulary ---")

# PP = B MIDDLE vocabulary (shared between A and B)
pp_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        pp_middles.add(m.middle)

print(f"PP vocabulary size: {len(pp_middles)}")

# ============================================================
# STEP 3: CLASSIFY LABELS AS RI OR PP
# ============================================================
print("\n--- Step 3: Classifying Labels ---")

def classify_token(token):
    """Classify token as RI, PP, or UNKNOWN based on MIDDLE membership."""
    m = morph.extract(token)
    if not m or not m.middle:
        return 'UNKNOWN', m

    if m.middle in pp_middles:
        return 'PP', m
    else:
        return 'RI', m

def extract_extension(middle, pp_vocab):
    """
    Extract extension character(s) from RI MIDDLE.
    Extension = the part that differs from PP base.
    """
    if not middle:
        return None, None

    if middle in pp_vocab:
        return None, middle  # No extension, it IS PP

    # Try to find PP base
    # Check if middle starts with or ends with PP
    for pp in sorted(pp_vocab, key=len, reverse=True):
        if len(pp) < 2:
            continue

        # Check suffix extension (PP + ext)
        if middle.startswith(pp) and len(middle) > len(pp):
            ext = middle[len(pp):]
            return ext, pp

        # Check prefix extension (ext + PP)
        if middle.endswith(pp) and len(middle) > len(pp):
            ext = middle[:-len(pp)]
            return ext, pp

    # No PP base found - might be compound or different structure
    return None, None

label_classifications = []

for label in all_labels:
    token = label['token']
    cls, m = classify_token(token)

    ext = None
    pp_base = None
    if cls == 'RI' and m and m.middle:
        ext, pp_base = extract_extension(m.middle, pp_middles)

    label_classifications.append({
        'token': token,
        'folio': label['folio'],
        'label_type': label['type'],
        'class': cls,
        'middle': m.middle if m else None,
        'extension': ext,
        'pp_base': pp_base
    })

# Count classifications
class_counts = Counter(l['class'] for l in label_classifications)
print(f"Label classifications: {dict(class_counts)}")

ri_labels = [l for l in label_classifications if l['class'] == 'RI']
print(f"RI labels: {len(ri_labels)}")
print(f"RI labels with extracted extension: {sum(1 for l in ri_labels if l['extension'])}")

# ============================================================
# STEP 4: EXTRACT EXTENSIONS FROM RI LABELS
# ============================================================
print("\n--- Step 4: Extension Distribution in Labels ---")

label_extensions = []
for l in ri_labels:
    if l['extension']:
        # Single char extensions
        for char in l['extension']:
            label_extensions.append(char)

label_ext_counts = Counter(label_extensions)
print(f"Total extension chars in labels: {len(label_extensions)}")
print(f"Extension distribution in labels: {dict(label_ext_counts.most_common(15))}")

# Categorize: identification (r,a,o,k) vs operational (h,d,t)
id_extensions = {'r', 'a', 'o', 'k'}
op_extensions = {'h', 'd', 't'}

label_id_count = sum(label_ext_counts.get(e, 0) for e in id_extensions)
label_op_count = sum(label_ext_counts.get(e, 0) for e in op_extensions)
label_other_count = len(label_extensions) - label_id_count - label_op_count

print(f"\nLabel extensions by category:")
print(f"  Identification (r,a,o,k): {label_id_count} ({100*label_id_count/len(label_extensions):.1f}%)")
print(f"  Operational (h,d,t): {label_op_count} ({100*label_op_count/len(label_extensions):.1f}%)")
print(f"  Other: {label_other_count} ({100*label_other_count/len(label_extensions):.1f}%)")

# ============================================================
# STEP 5: BUILD BASELINE FROM CURRIER A TEXT RI TOKENS
# ============================================================
print("\n--- Step 5: Currier A Text RI Baseline ---")

# Get Currier A text tokens (exclude labels)
text_extensions = []

for t in tx.currier_a():
    # Skip labels (placement starts with L)
    if hasattr(t, 'placement') and str(t.placement).startswith('L'):
        continue

    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    # Check if RI (not in PP)
    if m.middle in pp_middles:
        continue  # PP, not RI

    # Extract extension
    ext, pp_base = extract_extension(m.middle, pp_middles)
    if ext:
        for char in ext:
            text_extensions.append(char)

text_ext_counts = Counter(text_extensions)
print(f"Total extension chars in A text: {len(text_extensions)}")
print(f"Extension distribution in A text: {dict(text_ext_counts.most_common(15))}")

text_id_count = sum(text_ext_counts.get(e, 0) for e in id_extensions)
text_op_count = sum(text_ext_counts.get(e, 0) for e in op_extensions)
text_other_count = len(text_extensions) - text_id_count - text_op_count

print(f"\nText extensions by category:")
print(f"  Identification (r,a,o,k): {text_id_count} ({100*text_id_count/len(text_extensions):.1f}%)")
print(f"  Operational (h,d,t): {text_op_count} ({100*text_op_count/len(text_extensions):.1f}%)")
print(f"  Other: {text_other_count} ({100*text_other_count/len(text_extensions):.1f}%)")

# ============================================================
# STEP 6: STATISTICAL TEST
# ============================================================
print("\n--- Step 6: Statistical Comparison ---")

# Contingency table: Labels vs Text × ID vs OP
# Using ID + OP only (excluding "other" for cleaner test)
contingency = np.array([
    [label_id_count, label_op_count],  # Labels
    [text_id_count, text_op_count]      # Text
])

print(f"\nContingency table (ID vs OP):")
print(f"           ID    OP")
print(f"Labels    {contingency[0,0]:4d}  {contingency[0,1]:4d}")
print(f"Text      {contingency[1,0]:4d}  {contingency[1,1]:4d}")

# Chi-square test
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

# Cramer's V effect size
n = contingency.sum()
min_dim = min(contingency.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0

print(f"\nChi-square test:")
print(f"  chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.2e}")
print(f"  Cramer's V = {cramers_v:.3f}")

# Effect size interpretation
if cramers_v < 0.1:
    effect_interp = "negligible"
elif cramers_v < 0.2:
    effect_interp = "small"
elif cramers_v < 0.4:
    effect_interp = "medium"
else:
    effect_interp = "large"
print(f"  Effect size: {effect_interp}")

# Fisher's exact for specific extensions
print("\n--- Per-Extension Analysis ---")
for ext in ['r', 'a', 'o', 'k', 'h', 'd', 't']:
    label_has = label_ext_counts.get(ext, 0)
    label_not = len(label_extensions) - label_has
    text_has = text_ext_counts.get(ext, 0)
    text_not = len(text_extensions) - text_has

    table = [[label_has, label_not], [text_has, text_not]]

    if label_has + text_has > 0:  # Only test if extension exists
        odds, fisher_p = stats.fisher_exact(table)
        label_pct = 100 * label_has / len(label_extensions) if label_extensions else 0
        text_pct = 100 * text_has / len(text_extensions) if text_extensions else 0
        enrichment = (label_pct / text_pct) if text_pct > 0 else float('inf')

        sig = "*" if fisher_p < 0.05 else ""
        print(f"  {ext}: label={label_pct:.1f}% text={text_pct:.1f}% enrichment={enrichment:.1f}x p={fisher_p:.4f} {sig}")

# ============================================================
# STEP 7: C923 PROMOTION VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: C923 PROMOTION")
print("="*70)

# Success criteria: p < 0.05 AND effect size >= 0.2
promotion_p = p_value < 0.05
promotion_effect = cramers_v >= 0.2

# Also check if operational is truly suppressed
label_op_pct = 100 * label_op_count / len(label_extensions) if label_extensions else 0
text_op_pct = 100 * text_op_count / len(text_extensions) if text_extensions else 0
op_suppression = label_op_pct < text_op_pct * 0.5  # At least 50% suppressed

print(f"""
Extension Bifurcation Test Results:

Sample Sizes:
  - Label extension chars: {len(label_extensions)}
  - Text extension chars: {len(text_extensions)}
  - Total: {len(label_extensions) + len(text_extensions)}

Primary Test (ID vs OP distribution):
  - Chi-square: {chi2:.2f}
  - p-value: {p_value:.2e}
  - Cramer's V: {cramers_v:.3f} ({effect_interp})
  - Statistical significance (p<0.05): {promotion_p}
  - Effect size threshold (V>=0.2): {promotion_effect}

Operational Suppression:
  - Labels: {label_op_pct:.1f}% operational
  - Text: {text_op_pct:.1f}% operational
  - Suppression (>50% reduction): {op_suppression}

PROMOTION TO TIER 2: {'SUPPORTED' if (promotion_p and promotion_effect and op_suppression) else 'NOT SUPPORTED'}
""")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'test': 'extension_validation',
    'goal': 'C923 promotion from Tier 3 to Tier 2',
    'sample_sizes': {
        'labels_total': len(all_labels),
        'labels_ri': len(ri_labels),
        'label_extensions': len(label_extensions),
        'text_extensions': len(text_extensions)
    },
    'label_distribution': {
        'identification': label_id_count,
        'operational': label_op_count,
        'other': label_other_count,
        'id_pct': float(100 * label_id_count / len(label_extensions)) if label_extensions else 0,
        'op_pct': float(100 * label_op_count / len(label_extensions)) if label_extensions else 0
    },
    'text_distribution': {
        'identification': text_id_count,
        'operational': text_op_count,
        'other': text_other_count,
        'id_pct': float(100 * text_id_count / len(text_extensions)) if text_extensions else 0,
        'op_pct': float(100 * text_op_count / len(text_extensions)) if text_extensions else 0
    },
    'statistics': {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v),
        'effect_interpretation': effect_interp
    },
    'per_extension': {
        ext: {
            'label_count': label_ext_counts.get(ext, 0),
            'text_count': text_ext_counts.get(ext, 0)
        }
        for ext in ['r', 'a', 'o', 'k', 'h', 'd', 't', 'l', 's', 'n', 'i', 'e', 'y']
    },
    'verdict': {
        'p_significant': bool(promotion_p),
        'effect_significant': bool(promotion_effect),
        'op_suppressed': bool(op_suppression),
        'promotion_supported': bool(promotion_p and promotion_effect and op_suppression)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'extension_validation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

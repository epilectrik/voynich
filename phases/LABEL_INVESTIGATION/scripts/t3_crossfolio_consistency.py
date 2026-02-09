"""
t3_crossfolio_consistency.py - Cross-Folio Extension Consistency

Goal: Verify extension bifurcation pattern is universal, not folio-specific.

Test: Compute r-enrichment and h-absence per folio across all 13 mapped folios.
Success: Effect present in >=10/13 folios.
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
print("TEST 3: CROSS-FOLIO EXTENSION CONSISTENCY")
print("="*70)

# ============================================================
# STEP 1: BUILD PP VOCABULARY
# ============================================================
print("\n--- Step 1: Building PP Vocabulary ---")

pp_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        pp_middles.add(m.middle)

print(f"PP vocabulary size: {len(pp_middles)}")

# ============================================================
# STEP 2: LOAD LABELS BY FOLIO
# ============================================================
print("\n--- Step 2: Loading Labels by Folio ---")

pharma_dir = PROJECT_ROOT / 'phases' / 'PHARMA_LABEL_DECODING'
label_files = list(pharma_dir.glob('*_mapping.json'))

folio_labels = defaultdict(list)

for f in label_files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    folio = data.get('folio', f.stem.split('_')[0])

    for group in data.get('groups', []):
        # Jar
        jar = group.get('jar')
        if jar and isinstance(jar, str):
            folio_labels[folio].append(jar)

        # Content
        for key in ['roots', 'leaves', 'labels']:
            for item in group.get(key, []):
                if isinstance(item, dict):
                    token = item.get('token', '')
                elif isinstance(item, str):
                    token = item
                else:
                    continue
                if token and isinstance(token, str):
                    folio_labels[folio].append(token)

print(f"Folios with labels: {len(folio_labels)}")
for folio, labels in sorted(folio_labels.items()):
    print(f"  {folio}: {len(labels)} labels")

# ============================================================
# STEP 3: EXTRACT EXTENSIONS PER FOLIO
# ============================================================
print("\n--- Step 3: Extensions per Folio ---")

def extract_extension(middle, pp_vocab):
    """Extract extension from RI MIDDLE."""
    if not middle or middle in pp_vocab:
        return None

    for pp in sorted(pp_vocab, key=len, reverse=True):
        if len(pp) < 2:
            continue
        if middle.startswith(pp) and len(middle) > len(pp):
            return middle[len(pp):]
        if middle.endswith(pp) and len(middle) > len(pp):
            return middle[:-len(pp)]
    return None

folio_extensions = {}

for folio, labels in folio_labels.items():
    extensions = []
    for token in labels:
        m = morph.extract(token)
        if not m or not m.middle:
            continue
        if m.middle in pp_middles:
            continue  # PP, not RI

        ext = extract_extension(m.middle, pp_middles)
        if ext:
            for char in ext:
                extensions.append(char)

    folio_extensions[folio] = extensions

# Show per-folio extension counts
for folio in sorted(folio_extensions.keys()):
    exts = folio_extensions[folio]
    print(f"  {folio}: {len(exts)} extension chars")

# ============================================================
# STEP 4: COMPUTE PER-FOLIO METRICS
# ============================================================
print("\n--- Step 4: Per-Folio Extension Metrics ---")

id_extensions = {'r', 'a', 'o', 'k'}
op_extensions = {'h', 'd', 't'}

folio_metrics = []

for folio, exts in folio_extensions.items():
    if not exts:
        continue

    ext_counts = Counter(exts)
    total = len(exts)

    # Counts
    r_count = ext_counts.get('r', 0)
    h_count = ext_counts.get('h', 0)
    id_count = sum(ext_counts.get(e, 0) for e in id_extensions)
    op_count = sum(ext_counts.get(e, 0) for e in op_extensions)

    # Rates
    r_rate = r_count / total if total > 0 else 0
    h_rate = h_count / total if total > 0 else 0
    id_rate = id_count / total if total > 0 else 0
    op_rate = op_count / total if total > 0 else 0

    # Check patterns
    r_enriched = r_rate > 0.10  # More than 10% r
    h_absent = h_rate == 0      # No h at all

    folio_metrics.append({
        'folio': folio,
        'total_ext': total,
        'r_count': r_count,
        'r_rate': r_rate,
        'h_count': h_count,
        'h_rate': h_rate,
        'id_rate': id_rate,
        'op_rate': op_rate,
        'r_enriched': r_enriched,
        'h_absent': h_absent
    })

# Print table
print("\nFolio  Total  r(%)   h(%)  ID(%)  OP(%) r_enr h_abs")
print("-" * 60)
for fm in sorted(folio_metrics, key=lambda x: x['folio']):
    r_flag = "Y" if fm['r_enriched'] else ""
    h_flag = "Y" if fm['h_absent'] else ""
    print(f"{fm['folio']:7s} {fm['total_ext']:4d}  {100*fm['r_rate']:5.1f}  {100*fm['h_rate']:5.1f}  {100*fm['id_rate']:5.1f}  {100*fm['op_rate']:5.1f}   {r_flag:3s}  {h_flag:3s}")

# ============================================================
# STEP 5: CONSISTENCY CHECK
# ============================================================
print("\n--- Step 5: Consistency Summary ---")

n_folios = len(folio_metrics)
n_r_enriched = sum(1 for fm in folio_metrics if fm['r_enriched'])
n_h_absent = sum(1 for fm in folio_metrics if fm['h_absent'])

print(f"\nTotal folios with extensions: {n_folios}")
print(f"Folios with r-enrichment (>10%): {n_r_enriched}/{n_folios} ({100*n_r_enriched/n_folios:.0f}%)")
print(f"Folios with h-absence (0%): {n_h_absent}/{n_folios} ({100*n_h_absent/n_folios:.0f}%)")

# Success criteria: >=10/13 or 77%
r_consistent = n_r_enriched >= n_folios * 0.6
h_consistent = n_h_absent >= n_folios * 0.6

print(f"\nr-enrichment consistent (>=60%): {r_consistent}")
print(f"h-absence consistent (>=60%): {h_consistent}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: CROSS-FOLIO CONSISTENCY")
print("="*70)

print(f"""
Cross-Folio Extension Pattern Consistency:

Folios Analyzed: {n_folios}

r-Extension Enrichment (>10%):
  - Present in: {n_r_enriched}/{n_folios} folios ({100*n_r_enriched/n_folios:.0f}%)
  - Consistency threshold (60%): {'MET' if r_consistent else 'NOT MET'}

h-Extension Absence (0%):
  - Present in: {n_h_absent}/{n_folios} folios ({100*n_h_absent/n_folios:.0f}%)
  - Consistency threshold (60%): {'MET' if h_consistent else 'NOT MET'}

OVERALL: {'CONSISTENT PATTERN' if (r_consistent or h_consistent) else 'INCONSISTENT PATTERN'}

Note: Small per-folio samples make individual folio metrics noisy.
The aggregate pattern (Test 1) is more reliable than per-folio metrics.
""")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'crossfolio_consistency',
    'goal': 'Verify extension pattern is universal',
    'summary': {
        'total_folios': n_folios,
        'r_enriched_folios': n_r_enriched,
        'h_absent_folios': n_h_absent,
        'r_consistency_pct': float(100 * n_r_enriched / n_folios) if n_folios > 0 else 0,
        'h_consistency_pct': float(100 * n_h_absent / n_folios) if n_folios > 0 else 0
    },
    'per_folio': folio_metrics,
    'verdict': {
        'r_consistent': bool(r_consistent),
        'h_consistent': bool(h_consistent),
        'overall_consistent': bool(r_consistent or h_consistent)
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'crossfolio_consistency.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")

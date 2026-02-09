"""
01_position_vs_cluster.py

TEST 1: FOLIO POSITION vs CLUSTER TYPE

Does paragraph ordinal position (first/middle/last in folio) predict cluster membership?

If YES → structural organization (position matters)
If NO → content-driven variance (material determines structure)

This is the MOST DISCRIMINATING test for understanding A's generative process.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("TEST 1: FOLIO POSITION vs CLUSTER TYPE")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY
# =============================================================
print("\n[1/4] Building paragraph inventory...")

# Identify paragraphs using par_initial and par_final markers
# Each paragraph starts with par_initial=True and ends with par_final=True

folio_paragraphs = defaultdict(list)  # folio -> list of paragraph dicts
current_para_tokens = []
current_folio = None
current_para_id = 0

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    # New folio = new paragraph numbering
    if t.folio != current_folio:
        # Save previous paragraph if exists
        if current_para_tokens:
            folio_paragraphs[current_folio].append({
                'tokens': current_para_tokens,
                'lines': sorted(set(tok.line for tok in current_para_tokens))
            })
        current_folio = t.folio
        current_para_tokens = []
        current_para_id = 0

    # New paragraph starts when we see par_initial=True
    if t.par_initial and current_para_tokens:
        folio_paragraphs[current_folio].append({
            'tokens': current_para_tokens,
            'lines': sorted(set(tok.line for tok in current_para_tokens))
        })
        current_para_tokens = []
        current_para_id += 1

    current_para_tokens.append(t)

# Save final paragraph
if current_para_tokens and current_folio:
    folio_paragraphs[current_folio].append({
        'tokens': current_para_tokens,
        'lines': sorted(set(tok.line for tok in current_para_tokens))
    })

total_paragraphs = sum(len(paras) for paras in folio_paragraphs.values())
print(f"   Found {total_paragraphs} paragraphs across {len(folio_paragraphs)} folios")

# =============================================================
# STEP 2: CLASSIFY EACH PARAGRAPH INTO CLUSTER TYPES
# =============================================================
print("[2/4] Classifying paragraphs into cluster types...")

def classify_paragraph(para_dict):
    """
    Classify paragraph into one of 5 cluster types based on C881 findings:
    - SHORT_RI_HEAVY: short paragraphs with high RI density
    - LINKER_RICH: paragraphs with linker RI
    - STANDARD: typical paragraph structure
    - NO_RI: paragraphs with no RI tokens
    - MIDDLE_RI_ONLY: paragraphs with RI only in middle (not first line)
    """
    tokens = para_dict['tokens']
    lines = para_dict['lines']

    if not tokens:
        return "EMPTY"

    # Get first line for analysis
    folio = tokens[0].folio
    first_line = lines[0] if lines else None

    # Count RI tokens across paragraph lines
    ri_tokens = []
    pp_tokens = []

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'RI':
                        ri_tokens.append((line, t))
                    elif t.token_class == 'PP':
                        pp_tokens.append((line, t))
        except:
            pass

    n_lines = len(lines)
    n_tokens = len(tokens)

    # Check for linkers (ct-prefix RI)
    linker_ri = [(l, t) for l, t in ri_tokens if t.word and t.word.startswith('ct')]
    has_linker = len(linker_ri) > 0

    # Check RI positions
    first_line_ri = [t for l, t in ri_tokens if l == first_line]
    other_line_ri = [t for l, t in ri_tokens if l != first_line]

    # Classification logic
    if len(ri_tokens) == 0:
        return "NO_RI"

    if has_linker:
        return "LINKER_RICH"

    if n_lines <= 3 and len(ri_tokens) / max(n_tokens, 1) > 0.15:
        return "SHORT_RI_HEAVY"

    if len(first_line_ri) == 0 and len(other_line_ri) > 0:
        return "MIDDLE_RI_ONLY"

    return "STANDARD"

# Classify all paragraphs
paragraph_data = []
for folio in sorted(folio_paragraphs.keys()):
    paragraphs = folio_paragraphs[folio]
    n_paragraphs = len(paragraphs)

    for idx, para in enumerate(paragraphs):
        # Determine position
        if n_paragraphs == 1:
            position = "ONLY"
        elif idx == 0:
            position = "FIRST"
        elif idx == n_paragraphs - 1:
            position = "LAST"
        else:
            position = "MIDDLE"

        cluster_type = classify_paragraph(para)

        paragraph_data.append({
            'folio': folio,
            'position': position,
            'cluster_type': cluster_type,
            'n_lines': len(para['lines']),
            'n_tokens': len(para['tokens']),
            'ordinal': idx,
            'total_in_folio': n_paragraphs
        })

print(f"   Classified {len(paragraph_data)} paragraphs")

# =============================================================
# STEP 3: CONTINGENCY TABLE AND CHI-SQUARED TEST
# =============================================================
print("[3/4] Building contingency table...")

# Build contingency table: position × cluster_type
contingency = defaultdict(Counter)
for p in paragraph_data:
    if p['cluster_type'] not in ['EMPTY', 'UNKNOWN']:
        contingency[p['position']][p['cluster_type']] += 1

# Get all positions and cluster types
positions = ['FIRST', 'MIDDLE', 'LAST', 'ONLY']
cluster_types = sorted(set(p['cluster_type'] for p in paragraph_data if p['cluster_type'] not in ['EMPTY', 'UNKNOWN']))

print(f"\n{'Position':<10}", end="")
for ct in cluster_types:
    print(f"{ct:<18}", end="")
print("TOTAL")
print("-" * (10 + 18 * len(cluster_types) + 6))

row_totals = {}
col_totals = Counter()
grand_total = 0

for pos in positions:
    row_sum = 0
    print(f"{pos:<10}", end="")
    for ct in cluster_types:
        count = contingency[pos].get(ct, 0)
        print(f"{count:<18}", end="")
        row_sum += count
        col_totals[ct] += count
    print(f"{row_sum}")
    row_totals[pos] = row_sum
    grand_total += row_sum

print("-" * (10 + 18 * len(cluster_types) + 6))
print(f"{'TOTAL':<10}", end="")
for ct in cluster_types:
    print(f"{col_totals[ct]:<18}", end="")
print(f"{grand_total}")

# Chi-squared test
print("\n[4/4] Chi-squared test...")

chi2 = 0
df = (len([p for p in positions if row_totals.get(p, 0) > 0]) - 1) * (len(cluster_types) - 1)

for pos in positions:
    if row_totals.get(pos, 0) == 0:
        continue
    for ct in cluster_types:
        observed = contingency[pos].get(ct, 0)
        expected = (row_totals[pos] * col_totals[ct]) / grand_total if grand_total > 0 else 0
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

print(f"\nChi-squared statistic: {chi2:.2f}")
print(f"Degrees of freedom: {df}")

# Chi-squared critical values
# df=12: p=0.05 is ~21.03, p=0.01 is ~26.22
# df=9: p=0.05 is ~16.92, p=0.01 is ~21.67
if df >= 9:
    crit_05 = 16.92 if df == 9 else 21.03
    crit_01 = 21.67 if df == 9 else 26.22
else:
    crit_05 = 12.59  # df=6
    crit_01 = 16.81

if chi2 > crit_01:
    print("p < 0.01 - HIGHLY SIGNIFICANT")
    significance = "HIGHLY_SIGNIFICANT"
elif chi2 > crit_05:
    print("p < 0.05 - SIGNIFICANT")
    significance = "SIGNIFICANT"
else:
    print("p >= 0.05 - NOT SIGNIFICANT")
    significance = "NOT_SIGNIFICANT"

# =============================================================
# STEP 4: ENRICHMENT ANALYSIS
# =============================================================
print("\n" + "="*70)
print("ENRICHMENT ANALYSIS")
print("="*70)

print("\nCluster type enrichment by position (ratio vs expected):")
print(f"{'Position':<10}", end="")
for ct in cluster_types:
    print(f"{ct:<18}", end="")
print()
print("-" * (10 + 18 * len(cluster_types)))

enrichment_data = {}
for pos in positions:
    if row_totals.get(pos, 0) == 0:
        continue
    enrichment_data[pos] = {}
    print(f"{pos:<10}", end="")
    for ct in cluster_types:
        observed = contingency[pos].get(ct, 0)
        expected = (row_totals[pos] * col_totals[ct]) / grand_total if grand_total > 0 else 0
        ratio = observed / expected if expected > 0 else 0
        enrichment_data[pos][ct] = ratio
        if ratio >= 1.5:
            print(f"{ratio:.2f}x ↑↑       ", end="")
        elif ratio >= 1.2:
            print(f"{ratio:.2f}x ↑        ", end="")
        elif ratio <= 0.5:
            print(f"{ratio:.2f}x ↓↓       ", end="")
        elif ratio <= 0.8:
            print(f"{ratio:.2f}x ↓        ", end="")
        else:
            print(f"{ratio:.2f}x          ", end="")
    print()

# =============================================================
# INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Find strongest patterns
patterns = []
for pos, data in enrichment_data.items():
    for ct, ratio in data.items():
        if ratio >= 1.5 or ratio <= 0.5:
            patterns.append((pos, ct, ratio))

patterns.sort(key=lambda x: abs(x[2] - 1), reverse=True)

if patterns:
    print("\nStrongest position-cluster associations:")
    for pos, ct, ratio in patterns[:5]:
        direction = "enriched" if ratio > 1 else "depleted"
        print(f"  - {pos} paragraphs are {ratio:.2f}x {direction} for {ct}")

if significance in ["HIGHLY_SIGNIFICANT", "SIGNIFICANT"]:
    print(f"\n→ POSITION MATTERS: Paragraph position DOES predict cluster type")
    print("  This suggests STRUCTURAL ORGANIZATION - folios have a layout pattern")
    verdict = "POSITION_PREDICTS_CLUSTER"
else:
    print(f"\n→ POSITION DOES NOT MATTER: Cluster type is CONTENT-DRIVEN")
    print("  Material determines structure, not position in folio")
    verdict = "CONTENT_DRIVEN"

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'FOLIO_POSITION_VS_CLUSTER_TYPE',
    'n_paragraphs': len(paragraph_data),
    'contingency_table': {pos: dict(contingency[pos]) for pos in positions if row_totals.get(pos, 0) > 0},
    'chi_squared': chi2,
    'degrees_of_freedom': df,
    'significance': significance,
    'enrichment': enrichment_data,
    'strongest_patterns': [(p[0], p[1], p[2]) for p in patterns[:10]],
    'verdict': verdict,
    'cluster_type_distribution': dict(Counter(p['cluster_type'] for p in paragraph_data))
}

output_path = Path(__file__).parent.parent / 'results' / 'position_cluster_analysis.json'
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

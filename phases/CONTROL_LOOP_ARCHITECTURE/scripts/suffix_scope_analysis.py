#!/usr/bin/env python3
"""
Gap 4: Suffix Scope Markers

Do -edy and -aiin function as scope markers (batch scope vs loop scope)?
- -edy appears to scope "this extraction pass" (terminal suffix = close batch)
- -aiin appears to scope "this iteration cycle" (checkpoint suffix = bounded loop)

Test: Is -edy enriched in Mode A (specification) and -aiin in Mode B (continuation)?

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/suffix_scope_analysis.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Key suffixes to analyze
SCOPE_SUFFIXES = {
    # Terminal (batch-close) suffixes
    'dy': 'TERMINAL',
    'edy': 'TERMINAL',
    'eey': 'TERMINAL',
    'ey': 'TERMINAL',
    'hy': 'TERMINAL',
    'ry': 'TERMINAL',
    'ly': 'TERMINAL',
    'am': 'TERMINAL',
    'om': 'TERMINAL',
    # Checkpoint (iteration) suffixes
    'ain': 'CHECKPOINT',
    'aiin': 'CHECKPOINT',
    'iin': 'CHECKPOINT',
    'oiin': 'CHECKPOINT',
    # Iterative suffixes
    'in': 'ITERATIVE',
    'an': 'ITERATIVE',
    's': 'ITERATIVE',
}

# ============================================================
# COLLECT LINE-LEVEL DATA FROM DECODED FOLIOS
# ============================================================
print("Decoding all B folios for suffix-mode analysis...")

b_folios = sorted(set(t.folio for t in tx.currier_b()))

# Collect suffix counts by mode
suffix_by_mode = {'A': Counter(), 'B': Counter(), None: Counter()}
suffix_by_zone = {'HEADER': Counter(), 'SPECIFICATION': Counter(), 'EXECUTION': Counter()}
suffix_total_by_mode = {'A': 0, 'B': 0, None: 0}

# Also collect per-suffix positional data
suffix_positions = defaultdict(list)  # suffix -> list of line positions

lines_processed = 0
for folio in b_folios:
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except Exception as e:
        continue

    for para in paragraphs:
        body_lines = [l for l in para.lines if not l.is_header]
        n_body = len(body_lines)
        if n_body == 0:
            continue

        for li, line_a in enumerate(body_lines):
            mode = line_a.suffix_mode
            zone = line_a.paragraph_zone
            line_pos = li / max(n_body - 1, 1)
            lines_processed += 1

            for tok in line_a.tokens:
                s = tok.morph.suffix
                suffix_by_mode[mode][s] += 1
                suffix_total_by_mode[mode] += 1
                if zone:
                    suffix_by_zone[zone][s] += 1
                if s:
                    suffix_positions[s].append(line_pos)

print(f"  Lines processed: {lines_processed}")
print(f"  Mode A lines: {suffix_total_by_mode['A']}")
print(f"  Mode B lines: {suffix_total_by_mode['B']}")
print(f"  Unclassified: {suffix_total_by_mode[None]}")

# ============================================================
# ANALYSIS 1: Suffix enrichment in Mode A vs Mode B
# ============================================================
print("\n=== SUFFIX ENRICHMENT BY MODE ===")

mode_a_total = suffix_total_by_mode['A']
mode_b_total = suffix_total_by_mode['B']

suffix_enrichment = {}
print(f"\n  {'Suffix':10s} {'Cat':12s} {'ModeA%':>8s} {'ModeB%':>8s} {'A/B':>6s} {'Scope':>10s}")
print(f"  {'-'*60}")

for suffix in sorted(SCOPE_SUFFIXES.keys(), key=lambda x: SCOPE_SUFFIXES[x]):
    cat = SCOPE_SUFFIXES[suffix]
    a_count = suffix_by_mode['A'].get(suffix, 0)
    b_count = suffix_by_mode['B'].get(suffix, 0)
    a_pct = a_count / mode_a_total * 100 if mode_a_total > 0 else 0
    b_pct = b_count / mode_b_total * 100 if mode_b_total > 0 else 0
    ratio = a_pct / b_pct if b_pct > 0 else float('inf')

    if a_count + b_count >= 20:
        # Determine scope hypothesis
        if cat == 'TERMINAL' and ratio > 1.2:
            scope = 'MODE_A'
        elif cat == 'CHECKPOINT' and ratio < 0.8:
            scope = 'MODE_B'
        elif cat == 'ITERATIVE' and ratio < 0.8:
            scope = 'MODE_B'
        else:
            scope = 'NEUTRAL'

        suffix_enrichment[suffix] = {
            'category': cat,
            'mode_a_count': a_count,
            'mode_b_count': b_count,
            'mode_a_pct': round(a_pct, 2),
            'mode_b_pct': round(b_pct, 2),
            'a_b_ratio': round(ratio, 2),
            'scope': scope,
        }
        marker = '***' if ratio > 1.5 or ratio < 0.67 else ''
        print(f"  -{suffix:9s} {cat:12s} {a_pct:7.2f}% {b_pct:7.2f}% {ratio:5.2f}x {scope:>10s} {marker}")

# ============================================================
# ANALYSIS 2: Category-level enrichment
# ============================================================
print("\n=== CATEGORY-LEVEL ENRICHMENT ===")

cat_a = Counter()
cat_b = Counter()
for suffix, cat in SCOPE_SUFFIXES.items():
    cat_a[cat] += suffix_by_mode['A'].get(suffix, 0)
    cat_b[cat] += suffix_by_mode['B'].get(suffix, 0)
# Add BARE
cat_a['BARE'] = suffix_by_mode['A'].get(None, 0)
cat_b['BARE'] = suffix_by_mode['B'].get(None, 0)

cat_enrichment = {}
for cat in ['TERMINAL', 'CHECKPOINT', 'ITERATIVE', 'BARE']:
    a_pct = cat_a[cat] / mode_a_total * 100 if mode_a_total > 0 else 0
    b_pct = cat_b[cat] / mode_b_total * 100 if mode_b_total > 0 else 0
    ratio = a_pct / b_pct if b_pct > 0 else float('inf')
    cat_enrichment[cat] = {
        'mode_a_pct': round(a_pct, 1),
        'mode_b_pct': round(b_pct, 1),
        'a_b_ratio': round(ratio, 2),
    }
    print(f"  {cat:12s}: A={a_pct:5.1f}%  B={b_pct:5.1f}%  ratio={ratio:.2f}x")

# ============================================================
# ANALYSIS 3: Suffix position within paragraph body
# ============================================================
print("\n=== SUFFIX POSITION IN PARAGRAPH BODY ===")
print("  (0=first body line, 1=last body line)")

suffix_position_summary = {}
for suffix in ['edy', 'dy', 'aiin', 'ain', 'iin', 'in', 'am', 'eey', 'ey']:
    positions = suffix_positions.get(suffix, [])
    if len(positions) < 10:
        continue
    mean = sum(positions) / len(positions)
    early = sum(1 for p in positions if p < 0.33)
    mid = sum(1 for p in positions if 0.33 <= p < 0.67)
    late = sum(1 for p in positions if p >= 0.67)
    n = len(positions)

    suffix_position_summary[suffix] = {
        'count': n,
        'mean_position': round(mean, 3),
        'early_pct': round(early/n*100, 1),
        'mid_pct': round(mid/n*100, 1),
        'late_pct': round(late/n*100, 1),
    }
    print(f"  -{suffix:6s}: n={n:5d}  mean={mean:.3f}  early={early/n*100:5.1f}%  mid={mid/n*100:5.1f}%  late={late/n*100:5.1f}%")

# ============================================================
# ANALYSIS 4: Suffix co-occurrence within lines
# ============================================================
print("\n=== SUFFIX CO-OCCURRENCE WITHIN LINES ===")
print("  (Which suffixes appear together in the same line?)")

# From decoded lines, collect suffix sets per line
suffix_cooccurrence = Counter()
lines_with_data = 0

for folio in b_folios:
    try:
        paragraphs2 = decoder.analyze_folio_paragraphs(folio)
    except:
        continue
    for para in paragraphs2:
        for line_a in para.lines:
            if line_a.is_header:
                continue
            suffixes_in_line = set()
            for tok in line_a.tokens:
                s = tok.morph.suffix
                if s and s in SCOPE_SUFFIXES:
                    suffixes_in_line.add(s)
            if len(suffixes_in_line) >= 2:
                lines_with_data += 1
                for s1 in sorted(suffixes_in_line):
                    for s2 in sorted(suffixes_in_line):
                        if s1 < s2:
                            suffix_cooccurrence[(s1, s2)] += 1

print(f"\n  Lines with 2+ classified suffixes: {lines_with_data}")
print(f"\n  Top co-occurrences:")
for (s1, s2), c in suffix_cooccurrence.most_common(15):
    cat1 = SCOPE_SUFFIXES.get(s1, '?')
    cat2 = SCOPE_SUFFIXES.get(s2, '?')
    print(f"    -{s1:6s}({cat1[:4]}) + -{s2:6s}({cat2[:4]}): {c:4d}")

# ============================================================
# ANALYSIS 5: Suffix by paragraph zone (SPECIFICATION vs EXECUTION)
# ============================================================
print("\n=== SUFFIX BY PARAGRAPH ZONE ===")

for zone in ['SPECIFICATION', 'EXECUTION']:
    total = sum(suffix_by_zone[zone].values())
    if total == 0:
        continue
    print(f"\n  {zone} (total tokens: {total}):")
    for suffix in ['edy', 'dy', 'aiin', 'ain', 'iin', 'am']:
        c = suffix_by_zone[zone].get(suffix, 0)
        print(f"    -{suffix:6s}: {c:4d} ({c/total*100:.2f}%)")
    bare = suffix_by_zone[zone].get(None, 0)
    print(f"    (bare) : {bare:4d} ({bare/total*100:.2f}%)")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'mode_token_counts': {'A': mode_a_total, 'B': mode_b_total},
    'suffix_enrichment_by_mode': suffix_enrichment,
    'category_enrichment': cat_enrichment,
    'suffix_position_in_body': suffix_position_summary,
    'suffix_cooccurrence_top': [
        {'pair': [s1, s2], 'count': c}
        for (s1, s2), c in suffix_cooccurrence.most_common(15)
    ],
    'hypothesis_test': {
        'edy_mode_a_enriched': suffix_enrichment.get('edy', {}).get('a_b_ratio', 0) > 1.0,
        'aiin_mode_b_enriched': suffix_enrichment.get('aiin', {}).get('a_b_ratio', 0) < 1.0,
        'terminal_mode_a': cat_enrichment.get('TERMINAL', {}).get('a_b_ratio', 0) > 1.0,
        'checkpoint_mode_b': cat_enrichment.get('CHECKPOINT', {}).get('a_b_ratio', 0) < 1.0,
    },
}

output_path = OUTPUT_DIR / 'suffix_scope_analysis.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")

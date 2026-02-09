#!/usr/bin/env python3
"""
Test 11: FL Structural Progression

Question: Does FL stage progress at line level or paragraph level?

Tests:
1. FL stage vs LINE NUMBER within paragraph
2. FL stage vs PARAGRAPH NUMBER within folio
3. FL stage vs LINE NUMBER within folio (ignoring paragraphs)
4. Mean FL stage by structural position
5. Correlation analysis at each level
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 11: FL STRUCTURAL PROGRESSION")
print("="*70)

# =========================================================================
# FL MIDDLE to Stage mapping (from C777)
# =========================================================================
FL_STAGES = {
    'ii': 0, 'i': 0,           # INITIAL = 0
    'in': 1,                    # EARLY = 1
    'r': 2, 'ar': 2,           # MEDIAL = 2
    'al': 3, 'l': 3, 'ol': 3,  # LATE = 3
    'o': 4, 'ly': 4, 'am': 4,  # FINAL = 4
    'm': 5, 'dy': 5, 'ry': 5, 'y': 5,  # TERMINAL = 5
}

STAGE_NAMES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']
FL_MIDDLES = set(FL_STAGES.keys())

# =========================================================================
# Build structural data
# =========================================================================
print("\nBuilding structural data...")

# Get all B tokens with structure
# Need to derive paragraph from par_initial flags
b_data = []
current_para = {}  # folio -> current para number

for token in tx.currier_b():
    if '*' not in token.word:
        folio = token.folio

        # Initialize para counter for new folio
        if folio not in current_para:
            current_para[folio] = 0

        # Increment para on par_initial
        if token.par_initial:
            current_para[folio] += 1

        b_data.append({
            'word': token.word,
            'folio': folio,
            'para': current_para[folio],
            'line': token.line,
            'par_initial': token.par_initial,
            'par_final': token.par_final,
        })

print(f"  Total B tokens: {len(b_data)}")

# Build folio -> paragraph -> line structure
folio_structure = defaultdict(lambda: defaultdict(list))
for t in b_data:
    folio_structure[t['folio']][t['para']].append(t)

# Compute paragraph ordinals within folios
para_ordinals = {}  # (folio, para) -> ordinal (1-based)
for folio, paras in folio_structure.items():
    sorted_paras = sorted(paras.keys())
    for i, para in enumerate(sorted_paras):
        para_ordinals[(folio, para)] = i + 1

# Compute line ordinals within paragraphs
line_ordinals_in_para = {}  # (folio, para, line) -> ordinal (1-based)
for folio, paras in folio_structure.items():
    for para, tokens in paras.items():
        lines = sorted(set(t['line'] for t in tokens))
        for i, line in enumerate(lines):
            line_ordinals_in_para[(folio, para, line)] = i + 1

# Compute line ordinals within folios
line_ordinals_in_folio = {}  # (folio, line) -> ordinal (1-based)
for folio, paras in folio_structure.items():
    all_lines = set()
    for para, tokens in paras.items():
        for t in tokens:
            all_lines.add(t['line'])
    sorted_lines = sorted(all_lines)
    for i, line in enumerate(sorted_lines):
        line_ordinals_in_folio[(folio, line)] = i + 1

print(f"  Folios: {len(folio_structure)}")
print(f"  Paragraphs: {len(para_ordinals)}")

# =========================================================================
# Collect FL tokens with structural positions
# =========================================================================
print("\nCollecting FL tokens...")

fl_tokens = []
for t in b_data:
    try:
        m = morph.extract(t['word'])
        if m.middle in FL_MIDDLES:
            stage = FL_STAGES[m.middle]
            fl_tokens.append({
                'word': t['word'],
                'middle': m.middle,
                'stage': stage,
                'stage_name': STAGE_NAMES[stage],
                'folio': t['folio'],
                'para': t['para'],
                'line': t['line'],
                'para_ordinal': para_ordinals.get((t['folio'], t['para']), 0),
                'line_in_para': line_ordinals_in_para.get((t['folio'], t['para'], t['line']), 0),
                'line_in_folio': line_ordinals_in_folio.get((t['folio'], t['line']), 0),
            })
    except:
        pass

print(f"  FL tokens: {len(fl_tokens)}")

# Stage distribution
stage_counts = Counter(t['stage_name'] for t in fl_tokens)
print("\n  Stage distribution:")
for stage in STAGE_NAMES:
    print(f"    {stage}: {stage_counts.get(stage, 0)}")

# =========================================================================
# Test 1: FL stage vs PARAGRAPH ORDINAL within folio
# =========================================================================
print("\n" + "="*70)
print("TEST 1: FL STAGE vs PARAGRAPH ORDINAL")
print("="*70)

# Group by paragraph ordinal
para_ord_stages = defaultdict(list)
for t in fl_tokens:
    if t['para_ordinal'] > 0:
        para_ord_stages[t['para_ordinal']].append(t['stage'])

print("\nMean FL stage by paragraph ordinal:")
print(f"{'Para Ord':<12} {'Mean Stage':<12} {'N':<8} {'Stage Name':<15}")
print("-"*50)

para_means = []
para_ords = []
for ord_num in sorted(para_ord_stages.keys()):
    if ord_num <= 10:  # Focus on first 10 paragraphs
        stages = para_ord_stages[ord_num]
        mean_stage = np.mean(stages)
        stage_name = STAGE_NAMES[int(round(mean_stage))]
        para_means.append(mean_stage)
        para_ords.append(ord_num)
        print(f"{ord_num:<12} {mean_stage:<12.2f} {len(stages):<8} {stage_name:<15}")

# Correlation
if len(para_ords) >= 3:
    r_para, p_para = stats.pearsonr(para_ords, para_means)
    rho_para, rho_p_para = stats.spearmanr(para_ords, para_means)
    print(f"\nCorrelation (paragraph ordinal vs FL stage):")
    print(f"  Pearson r = {r_para:.3f} (p = {p_para:.4f})")
    print(f"  Spearman rho = {rho_para:.3f} (p = {rho_p_para:.4f})")

    if p_para < 0.05:
        if r_para > 0:
            print("  ** FL stage INCREASES with paragraph ordinal **")
        else:
            print("  ** FL stage DECREASES with paragraph ordinal **")
    else:
        print("  No significant correlation")

# =========================================================================
# Test 2: FL stage vs LINE ORDINAL within paragraph
# =========================================================================
print("\n" + "="*70)
print("TEST 2: FL STAGE vs LINE ORDINAL WITHIN PARAGRAPH")
print("="*70)

# Group by line ordinal within paragraph
line_in_para_stages = defaultdict(list)
for t in fl_tokens:
    if t['line_in_para'] > 0:
        line_in_para_stages[t['line_in_para']].append(t['stage'])

print("\nMean FL stage by line ordinal within paragraph:")
print(f"{'Line Ord':<12} {'Mean Stage':<12} {'N':<8} {'Stage Name':<15}")
print("-"*50)

line_means = []
line_ords = []
for ord_num in sorted(line_in_para_stages.keys()):
    if ord_num <= 10:  # Focus on first 10 lines
        stages = line_in_para_stages[ord_num]
        mean_stage = np.mean(stages)
        stage_name = STAGE_NAMES[int(round(mean_stage))]
        line_means.append(mean_stage)
        line_ords.append(ord_num)
        print(f"{ord_num:<12} {mean_stage:<12.2f} {len(stages):<8} {stage_name:<15}")

# Correlation
if len(line_ords) >= 3:
    r_line, p_line = stats.pearsonr(line_ords, line_means)
    rho_line, rho_p_line = stats.spearmanr(line_ords, line_means)
    print(f"\nCorrelation (line ordinal within para vs FL stage):")
    print(f"  Pearson r = {r_line:.3f} (p = {p_line:.4f})")
    print(f"  Spearman rho = {rho_line:.3f} (p = {rho_p_line:.4f})")

    if p_line < 0.05:
        if r_line > 0:
            print("  ** FL stage INCREASES with line ordinal within paragraph **")
        else:
            print("  ** FL stage DECREASES with line ordinal within paragraph **")
    else:
        print("  No significant correlation")

# =========================================================================
# Test 3: FL stage vs LINE ORDINAL within folio
# =========================================================================
print("\n" + "="*70)
print("TEST 3: FL STAGE vs LINE ORDINAL WITHIN FOLIO")
print("="*70)

# Group by line ordinal within folio
line_in_folio_stages = defaultdict(list)
for t in fl_tokens:
    if t['line_in_folio'] > 0:
        line_in_folio_stages[t['line_in_folio']].append(t['stage'])

print("\nMean FL stage by line ordinal within folio (first 20 lines):")
print(f"{'Line Ord':<12} {'Mean Stage':<12} {'N':<8} {'Stage Name':<15}")
print("-"*50)

folio_line_means = []
folio_line_ords = []
for ord_num in sorted(line_in_folio_stages.keys()):
    if ord_num <= 20:
        stages = line_in_folio_stages[ord_num]
        if len(stages) >= 5:  # Minimum sample
            mean_stage = np.mean(stages)
            stage_name = STAGE_NAMES[int(round(mean_stage))]
            folio_line_means.append(mean_stage)
            folio_line_ords.append(ord_num)
            print(f"{ord_num:<12} {mean_stage:<12.2f} {len(stages):<8} {stage_name:<15}")

# Correlation
if len(folio_line_ords) >= 3:
    r_folio, p_folio = stats.pearsonr(folio_line_ords, folio_line_means)
    rho_folio, rho_p_folio = stats.spearmanr(folio_line_ords, folio_line_means)
    print(f"\nCorrelation (line ordinal within folio vs FL stage):")
    print(f"  Pearson r = {r_folio:.3f} (p = {p_folio:.4f})")
    print(f"  Spearman rho = {rho_folio:.3f} (p = {rho_p_folio:.4f})")

    if p_folio < 0.05:
        if r_folio > 0:
            print("  ** FL stage INCREASES with line ordinal within folio **")
        else:
            print("  ** FL stage DECREASES with line ordinal within folio **")
    else:
        print("  No significant correlation")

# =========================================================================
# Test 4: Normalized position analysis
# =========================================================================
print("\n" + "="*70)
print("TEST 4: NORMALIZED POSITION ANALYSIS")
print("="*70)

# Compute normalized positions
for t in fl_tokens:
    # Get max para ordinal for this folio
    folio = t['folio']
    max_para = max(para_ordinals.get((folio, p), 0)
                   for p in folio_structure[folio].keys())
    t['norm_para_pos'] = t['para_ordinal'] / max_para if max_para > 0 else 0

    # Get max line in this para
    para = t['para']
    max_line = max(line_ordinals_in_para.get((folio, para, l), 0)
                   for tok in folio_structure[folio][para]
                   for l in [tok['line']])
    t['norm_line_in_para'] = t['line_in_para'] / max_line if max_line > 0 else 0

# Bin by normalized paragraph position
norm_para_bins = defaultdict(list)
for t in fl_tokens:
    bin_idx = int(t['norm_para_pos'] * 5)  # 5 bins
    bin_idx = min(bin_idx, 4)  # Cap at 4
    norm_para_bins[bin_idx].append(t['stage'])

print("\nMean FL stage by normalized paragraph position (0-1):")
print(f"{'Position':<15} {'Mean Stage':<12} {'N':<8} {'Stage Name':<15}")
print("-"*50)

for bin_idx in range(5):
    stages = norm_para_bins[bin_idx]
    if stages:
        pos_range = f"{bin_idx*0.2:.1f}-{(bin_idx+1)*0.2:.1f}"
        mean_stage = np.mean(stages)
        stage_name = STAGE_NAMES[int(round(mean_stage))]
        print(f"{pos_range:<15} {mean_stage:<12.2f} {len(stages):<8} {stage_name:<15}")

# Bin by normalized line position within paragraph
norm_line_bins = defaultdict(list)
for t in fl_tokens:
    bin_idx = int(t['norm_line_in_para'] * 5)
    bin_idx = min(bin_idx, 4)
    norm_line_bins[bin_idx].append(t['stage'])

print("\nMean FL stage by normalized line position within paragraph (0-1):")
print(f"{'Position':<15} {'Mean Stage':<12} {'N':<8} {'Stage Name':<15}")
print("-"*50)

for bin_idx in range(5):
    stages = norm_line_bins[bin_idx]
    if stages:
        pos_range = f"{bin_idx*0.2:.1f}-{(bin_idx+1)*0.2:.1f}"
        mean_stage = np.mean(stages)
        stage_name = STAGE_NAMES[int(round(mean_stage))]
        print(f"{pos_range:<15} {mean_stage:<12.2f} {len(stages):<8} {stage_name:<15}")

# =========================================================================
# Test 5: Stage distribution by structural position
# =========================================================================
print("\n" + "="*70)
print("TEST 5: STAGE DISTRIBUTION BY POSITION")
print("="*70)

# First vs last paragraph
first_para = [t['stage'] for t in fl_tokens if t['para_ordinal'] == 1]
last_para = [t['stage'] for t in fl_tokens if t['norm_para_pos'] > 0.8]

if first_para and last_para:
    print("\nFirst paragraph vs Last paragraph (>0.8 normalized):")
    print(f"  First para mean stage: {np.mean(first_para):.2f} ({STAGE_NAMES[int(round(np.mean(first_para)))]})")
    print(f"  Last para mean stage: {np.mean(last_para):.2f} ({STAGE_NAMES[int(round(np.mean(last_para)))]})")

    u_stat, mw_p = stats.mannwhitneyu(first_para, last_para, alternative='two-sided')
    print(f"  Mann-Whitney p = {mw_p:.4f}")

    if mw_p < 0.05:
        if np.mean(first_para) < np.mean(last_para):
            print("  ** Later paragraphs have HIGHER FL stages **")
        else:
            print("  ** Earlier paragraphs have HIGHER FL stages **")

# First vs last line within paragraph
first_line = [t['stage'] for t in fl_tokens if t['line_in_para'] == 1]
last_line = [t['stage'] for t in fl_tokens if t['norm_line_in_para'] > 0.8]

if first_line and last_line:
    print("\nFirst line vs Last line within paragraph (>0.8 normalized):")
    print(f"  First line mean stage: {np.mean(first_line):.2f} ({STAGE_NAMES[int(round(np.mean(first_line)))]})")
    print(f"  Last line mean stage: {np.mean(last_line):.2f} ({STAGE_NAMES[int(round(np.mean(last_line)))]})")

    u_stat, mw_p_line = stats.mannwhitneyu(first_line, last_line, alternative='two-sided')
    print(f"  Mann-Whitney p = {mw_p_line:.4f}")

    if mw_p_line < 0.05:
        if np.mean(first_line) < np.mean(last_line):
            print("  ** Later lines have HIGHER FL stages **")
        else:
            print("  ** Earlier lines have HIGHER FL stages **")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: FL STRUCTURAL PROGRESSION")
print("="*70)

findings = []

# Paragraph level
if 'r_para' in dir() and abs(r_para) > 0.3:
    if p_para < 0.05:
        direction = "INCREASES" if r_para > 0 else "DECREASES"
        findings.append(f"PARAGRAPH LEVEL: FL stage {direction} with paragraph ordinal (r={r_para:.2f}, p={p_para:.4f})")

# Line within paragraph level
if 'r_line' in dir() and abs(r_line) > 0.3:
    if p_line < 0.05:
        direction = "INCREASES" if r_line > 0 else "DECREASES"
        findings.append(f"LINE-IN-PARA LEVEL: FL stage {direction} with line ordinal (r={r_line:.2f}, p={p_line:.4f})")

# Line within folio level
if 'r_folio' in dir() and abs(r_folio) > 0.3:
    if p_folio < 0.05:
        direction = "INCREASES" if r_folio > 0 else "DECREASES"
        findings.append(f"LINE-IN-FOLIO LEVEL: FL stage {direction} with line ordinal (r={r_folio:.2f}, p={p_folio:.4f})")

# First vs last comparisons
if 'mw_p' in dir() and mw_p < 0.05:
    findings.append(f"First vs last PARAGRAPH: significant difference (p={mw_p:.4f})")

if 'mw_p_line' in dir() and mw_p_line < 0.05:
    findings.append(f"First vs last LINE in para: significant difference (p={mw_p_line:.4f})")

if not findings:
    findings.append("NO significant structural progression detected at any level")

print("\nKey findings:")
for i, f in enumerate(findings, 1):
    print(f"  {i}. {f}")

# Determine verdict
if any('PARAGRAPH' in f and 'INCREASES' in f for f in findings):
    verdict = "PARAGRAPH-LEVEL"
    explanation = "FL stage progresses at paragraph level within folios"
elif any('LINE' in f and 'INCREASES' in f for f in findings):
    verdict = "LINE-LEVEL"
    explanation = "FL stage progresses at line level"
elif any('significant' in f.lower() for f in findings):
    verdict = "MIXED"
    explanation = "Some structural effect but not clean progression"
else:
    verdict = "POSITION-INDEPENDENT"
    explanation = "FL stage does not correlate with structural position"

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'n_fl_tokens': len(fl_tokens),
    'stage_counts': dict(stage_counts),
    'correlations': {
        'para_ordinal': {'r': float(r_para) if 'r_para' in dir() else None,
                         'p': float(p_para) if 'p_para' in dir() else None},
        'line_in_para': {'r': float(r_line) if 'r_line' in dir() else None,
                         'p': float(p_line) if 'p_line' in dir() else None},
        'line_in_folio': {'r': float(r_folio) if 'r_folio' in dir() else None,
                          'p': float(p_folio) if 'p_folio' in dir() else None},
    },
    'findings': findings,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'fl_structural_progression.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to {output_path}")

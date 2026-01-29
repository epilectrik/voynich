"""
T5: Compound Structure Predictors

Question: Does compound MIDDLE structure predict anything about token context?
- Section (H, S, B, P, C, T, Z, A)?
- Position (line-1 vs body)?
- Folio content type?

This tests whether compound/derived vocabulary has semantic distribution patterns.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Build MiddleAnalyzer
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer.get_core_middles()

print(f"Core MIDDLEs: {len(core_middles)}")
print(f"Classified types: {len(classified_tokens)}")

# Collect all B tokens with metadata
tokens_data = []

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    if not m.middle:
        continue

    is_un = w not in classified_tokens
    is_compound = mid_analyzer.is_compound(m.middle)

    tokens_data.append({
        'word': w,
        'middle': m.middle,
        'folio': token.folio,
        'line': token.line,
        'section': token.section,
        'is_un': is_un,
        'is_compound': is_compound,
        'middle_length': len(m.middle)
    })

print(f"Total tokens: {len(tokens_data)}")

# ============================================================
# ANALYSIS 1: Compound rate by section
# ============================================================
print("\n" + "="*60)
print("COMPOUND RATE BY SECTION")
print("="*60)

section_stats = defaultdict(lambda: {'total': 0, 'compound': 0, 'un': 0, 'un_compound': 0})

for t in tokens_data:
    sec = t['section']
    section_stats[sec]['total'] += 1
    if t['is_compound']:
        section_stats[sec]['compound'] += 1
    if t['is_un']:
        section_stats[sec]['un'] += 1
        if t['is_compound']:
            section_stats[sec]['un_compound'] += 1

print(f"\n{'Section':<10} {'Total':<8} {'Compound%':<12} {'UN%':<10} {'UN Compound%'}")
print("-" * 60)

section_compound_rates = {}
for sec in sorted(section_stats.keys()):
    s = section_stats[sec]
    cmp_rate = 100 * s['compound'] / s['total'] if s['total'] else 0
    un_rate = 100 * s['un'] / s['total'] if s['total'] else 0
    un_cmp_rate = 100 * s['un_compound'] / s['un'] if s['un'] else 0
    section_compound_rates[sec] = cmp_rate
    print(f"{sec:<10} {s['total']:<8} {cmp_rate:<12.1f} {un_rate:<10.1f} {un_cmp_rate:.1f}")

# ============================================================
# ANALYSIS 2: Compound rate by line position
# ============================================================
print("\n" + "="*60)
print("COMPOUND RATE BY LINE POSITION")
print("="*60)

# Determine first line per folio
folio_first_lines = {}
for t in tokens_data:
    f, l = t['folio'], t['line']
    if f not in folio_first_lines:
        folio_first_lines[f] = l
    elif l < folio_first_lines[f]:
        folio_first_lines[f] = l

line1_tokens = [t for t in tokens_data if t['line'] == folio_first_lines.get(t['folio'])]
body_tokens = [t for t in tokens_data if t['line'] != folio_first_lines.get(t['folio'])]

line1_compound = sum(1 for t in line1_tokens if t['is_compound'])
body_compound = sum(1 for t in body_tokens if t['is_compound'])

line1_rate = 100 * line1_compound / len(line1_tokens) if line1_tokens else 0
body_rate = 100 * body_compound / len(body_tokens) if body_tokens else 0

print(f"\nLine-1 compound rate: {line1_compound}/{len(line1_tokens)} = {line1_rate:.1f}%")
print(f"Body compound rate: {body_compound}/{len(body_tokens)} = {body_rate:.1f}%")
print(f"Difference: {line1_rate - body_rate:+.1f}pp")

# Line-1 UN specifically
line1_un = [t for t in line1_tokens if t['is_un']]
body_un = [t for t in body_tokens if t['is_un']]

line1_un_compound = sum(1 for t in line1_un if t['is_compound'])
body_un_compound = sum(1 for t in body_un if t['is_compound'])

line1_un_rate = 100 * line1_un_compound / len(line1_un) if line1_un else 0
body_un_rate = 100 * body_un_compound / len(body_un) if body_un else 0

print(f"\nLine-1 UN compound rate: {line1_un_compound}/{len(line1_un)} = {line1_un_rate:.1f}%")
print(f"Body UN compound rate: {body_un_compound}/{len(body_un)} = {body_un_rate:.1f}%")
print(f"Difference: {line1_un_rate - body_un_rate:+.1f}pp")

# ============================================================
# ANALYSIS 3: Folio-level compound density
# ============================================================
print("\n" + "="*60)
print("FOLIO-LEVEL COMPOUND DENSITY")
print("="*60)

folio_stats = defaultdict(lambda: {'total': 0, 'compound': 0, 'un': 0})

for t in tokens_data:
    f = t['folio']
    folio_stats[f]['total'] += 1
    if t['is_compound']:
        folio_stats[f]['compound'] += 1
    if t['is_un']:
        folio_stats[f]['un'] += 1

folio_compound_rates = {}
for f, s in folio_stats.items():
    folio_compound_rates[f] = 100 * s['compound'] / s['total'] if s['total'] else 0

rates = list(folio_compound_rates.values())
print(f"Folio compound rate: mean={np.mean(rates):.1f}%, std={np.std(rates):.1f}%")
print(f"  min={min(rates):.1f}%, max={max(rates):.1f}%")

# Top and bottom folios
sorted_folios = sorted(folio_compound_rates.items(), key=lambda x: x[1], reverse=True)
print(f"\nHighest compound rate folios:")
for f, r in sorted_folios[:5]:
    s = folio_stats[f]
    print(f"  {f}: {r:.1f}% ({s['compound']}/{s['total']} tokens)")

print(f"\nLowest compound rate folios:")
for f, r in sorted_folios[-5:]:
    s = folio_stats[f]
    print(f"  {f}: {r:.1f}% ({s['compound']}/{s['total']} tokens)")

# ============================================================
# ANALYSIS 4: Compound rate vs folio vocabulary uniqueness
# ============================================================
print("\n" + "="*60)
print("COMPOUND RATE VS FOLIO VOCABULARY UNIQUENESS")
print("="*60)

# For each folio, compute: compound rate and folio-unique MIDDLE rate
folio_middles = defaultdict(set)
for t in tokens_data:
    folio_middles[t['folio']].add(t['middle'])

# Global MIDDLE -> folio count
middle_folio_count = Counter()
for f, mids in folio_middles.items():
    for m in mids:
        middle_folio_count[m] += 1

folio_unique_rates = {}
for f, mids in folio_middles.items():
    fu_count = sum(1 for m in mids if middle_folio_count[m] == 1)
    folio_unique_rates[f] = 100 * fu_count / len(mids) if mids else 0

# Correlation between compound rate and folio-unique rate
compound_rates_list = [folio_compound_rates[f] for f in folio_compound_rates]
unique_rates_list = [folio_unique_rates[f] for f in folio_compound_rates]

correlation = np.corrcoef(compound_rates_list, unique_rates_list)[0, 1]
print(f"\nCorrelation (folio compound rate vs folio-unique rate): r = {correlation:.3f}")

if correlation > 0.5:
    print("STRONG positive: folios with more compounds have more unique vocabulary")
elif correlation > 0.2:
    print("MODERATE positive: some relationship between compounds and uniqueness")
elif correlation > -0.2:
    print("WEAK/NONE: compound rate and uniqueness are independent")
else:
    print("NEGATIVE: folios with more compounds have LESS unique vocabulary (unexpected)")

# ============================================================
# ANALYSIS 5: Does compound structure predict token function?
# ============================================================
print("\n" + "="*60)
print("COMPOUND STRUCTURE AND TOKEN FUNCTION")
print("="*60)

# Compare classified token compound rate by class (if we have class info)
class_compound = defaultdict(lambda: {'total': 0, 'compound': 0})

for t in tokens_data:
    if not t['is_un']:  # classified token
        word = t['word']
        cls = ctm['token_to_class'].get(word, 'UNKNOWN')
        class_compound[cls]['total'] += 1
        if t['is_compound']:
            class_compound[cls]['compound'] += 1

print(f"\nCompound rate by instruction class (top 10 by token count):")
sorted_classes = sorted(class_compound.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
for cls, stats in sorted_classes:
    rate = 100 * stats['compound'] / stats['total'] if stats['total'] else 0
    print(f"  Class {cls}: {rate:.1f}% compound ({stats['total']} tokens)")

# ============================================================
# ANALYSIS 6: Section-specific UN compound patterns
# ============================================================
print("\n" + "="*60)
print("SECTION-SPECIFIC UN COMPOUND PATTERNS")
print("="*60)

# For each section, show UN compound rate and compare to overall
overall_un = [t for t in tokens_data if t['is_un']]
overall_un_compound_rate = 100 * sum(1 for t in overall_un if t['is_compound']) / len(overall_un)

print(f"\nOverall UN compound rate: {overall_un_compound_rate:.1f}%")
print(f"\nBy section:")

section_un_rates = {}
for sec in sorted(section_stats.keys()):
    sec_un = [t for t in tokens_data if t['is_un'] and t['section'] == sec]
    if len(sec_un) >= 50:  # only sections with enough data
        rate = 100 * sum(1 for t in sec_un if t['is_compound']) / len(sec_un)
        section_un_rates[sec] = rate
        diff = rate - overall_un_compound_rate
        print(f"  {sec}: {rate:.1f}% ({len(sec_un)} UN tokens) [{diff:+.1f}pp vs overall]")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*60)
print("VERDICT")
print("="*60)

findings = []

# Line position effect
if line1_rate - body_rate > 5:
    findings.append(f"LINE_POSITION: Line-1 has higher compound rate (+{line1_rate - body_rate:.1f}pp)")

# Section variation
section_rates = list(section_compound_rates.values())
if max(section_rates) - min(section_rates) > 10:
    findings.append(f"SECTION_VARIATION: Compound rate varies by section ({min(section_rates):.1f}%-{max(section_rates):.1f}%)")

# Folio uniqueness correlation
if abs(correlation) > 0.3:
    direction = "positively" if correlation > 0 else "negatively"
    findings.append(f"FOLIO_UNIQUENESS: Compound rate {direction} correlates with vocabulary uniqueness (r={correlation:.2f})")

# Folio variation
if np.std(rates) > 5:
    findings.append(f"FOLIO_VARIATION: Compound rate varies across folios (std={np.std(rates):.1f}%)")

if findings:
    print("\nCompound structure DOES predict context:")
    for f in findings:
        print(f"  - {f}")
    verdict = "PREDICTIVE"
else:
    print("\nCompound structure does NOT strongly predict context")
    verdict = "NON_PREDICTIVE"

# Save results
results = {
    'by_section': {sec: {
        'total': section_stats[sec]['total'],
        'compound_rate': section_compound_rates.get(sec, 0),
        'un_rate': 100 * section_stats[sec]['un'] / section_stats[sec]['total'] if section_stats[sec]['total'] else 0
    } for sec in section_stats},
    'by_position': {
        'line1_compound_rate': line1_rate,
        'body_compound_rate': body_rate,
        'line1_un_compound_rate': line1_un_rate,
        'body_un_compound_rate': body_un_rate
    },
    'folio_level': {
        'mean_compound_rate': float(np.mean(rates)),
        'std_compound_rate': float(np.std(rates)),
        'uniqueness_correlation': float(correlation)
    },
    'findings': findings,
    'verdict': verdict
}

out_path = PROJECT_ROOT / 'phases' / 'COMPOUND_MIDDLE_ARCHITECTURE' / 'results' / 't5_compound_predictors.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")

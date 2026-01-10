"""
AZC B-Pattern Conformance Test

Tests whether B-side structural constraints hold in AZC:
- C382: Morphology encodes control phase
- C397: qo-prefix = escape route
- C408-C412: Sister pairs (ch-sh, ok-ot) equivalence classes

Goal: Confirm AZC follows B patterns OR reveal divergence
"""

import re
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

# Parse EVA transcription
data_path = Path(r"C:\git\voynich\data\transcriptions\voynich_eva.txt")

def parse_eva_file(filepath):
    """Parse EVA transcription into structured data"""
    records = []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse folio.line marker
            match = re.match(r'<(\w+)\.(\d+)>(.+)', line)
            if match:
                folio = match.group(1)
                line_num = int(match.group(2))
                content = match.group(3)

                # Tokenize (split on . and spaces, remove punctuation markers)
                raw_tokens = re.split(r'[.\s]+', content)
                tokens = []
                for t in raw_tokens:
                    # Clean up EVA markup
                    t = re.sub(r'[=\-,!?#@+*(){}[\]<>0-9]', '', t)
                    t = t.lower().strip()
                    if t and len(t) > 0:
                        tokens.append(t)

                for pos, token in enumerate(tokens):
                    records.append({
                        'folio': folio,
                        'line': line_num,
                        'position': pos,
                        'token': token
                    })

    return records

print("Loading EVA transcription...")
records = parse_eva_file(data_path)
print(f"Loaded {len(records)} tokens from {len(set(r['folio'] for r in records))} folios")

# Currier classification based on folio naming conventions
# This is approximate - in practice would use a lookup table
def classify_currier(folio):
    """Approximate Currier classification by folio ID"""
    # Based on standard Voynich scholarship:
    # Currier A: f1-f8, f15-f20, etc (herbal A)
    # Currier B: f39-f116 approximately (herbal B, pharma, bio, astro, cosmo)
    # AZC: f70-f73 (zodiac), f85-f86 (cosmo rosettes)

    # Parse folio number
    match = re.match(r'f?(\d+)', folio)
    if not match:
        return 'UNK'

    num = int(match.group(1))

    # Zodiac/cosmological pages (AZC candidates)
    if 67 <= num <= 73:
        return 'AZC'  # Zodiac pages
    elif 85 <= num <= 86:
        return 'AZC'  # Rosettes

    # Rough Currier split
    if num <= 8:
        return 'A'
    elif num <= 20:
        return 'A'
    elif num <= 57:
        return 'B'
    elif num <= 66:
        return 'B'  # Pharmaceutical
    elif num <= 84:
        return 'B'  # Biological
    elif num <= 116:
        return 'B'

    return 'UNK'

# Add Currier classification
for r in records:
    r['currier'] = classify_currier(r['folio'])

# Count by Currier type
currier_counts = Counter(r['currier'] for r in records)
print(f"\nCurrier distribution:")
for c, count in currier_counts.items():
    print(f"  {c}: {count} ({100*count/len(records):.1f}%)")

# Separate datasets
records_a = [r for r in records if r['currier'] == 'A']
records_b = [r for r in records if r['currier'] == 'B']
records_azc = [r for r in records if r['currier'] == 'AZC']

print(f"\nA tokens: {len(records_a)}")
print(f"B tokens: {len(records_b)}")
print(f"AZC tokens: {len(records_azc)}")

if len(records_azc) == 0:
    print("\nWARNING: No AZC tokens identified. Adjusting classification...")
    # Try to find zodiac-style folios
    folio_counts = Counter(r['folio'] for r in records)
    print(f"Available folios: {sorted(set(r['folio'] for r in records))[:20]}...")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: SISTER PAIRS (ch-sh, ok-ot)")
print("=" * 70)

def analyze_sister_pairs(tokens, label):
    """Analyze sister pair usage patterns"""
    token_list = [r['token'] for r in tokens]
    ch_count = sum(1 for t in token_list if t.startswith('ch'))
    sh_count = sum(1 for t in token_list if t.startswith('sh'))
    ok_count = sum(1 for t in token_list if 'ok' in t)
    ot_count = sum(1 for t in token_list if 'ot' in t)

    total = len(token_list)
    if total == 0:
        print(f"\n{label}: No tokens")
        return None

    print(f"\n{label} ({total} tokens):")
    print(f"  ch-prefix: {ch_count} ({100*ch_count/total:.2f}%)")
    print(f"  sh-prefix: {sh_count} ({100*sh_count/total:.2f}%)")
    print(f"  ch:sh ratio: {ch_count/max(sh_count,1):.2f}")
    print(f"  ok-containing: {ok_count} ({100*ok_count/total:.2f}%)")
    print(f"  ot-containing: {ot_count} ({100*ot_count/total:.2f}%)")
    print(f"  ok:ot ratio: {ok_count/max(ot_count,1):.2f}")

    return {
        'ch': ch_count, 'sh': sh_count,
        'ok': ok_count, 'ot': ot_count,
        'ch_sh_ratio': ch_count/max(sh_count,1),
        'ok_ot_ratio': ok_count/max(ot_count,1),
        'ch_rate': ch_count/total,
        'sh_rate': sh_count/total
    }

b_sisters = analyze_sister_pairs(records_b, "Currier B (baseline)")
a_sisters = analyze_sister_pairs(records_a, "Currier A")
azc_sisters = analyze_sister_pairs(records_azc, "AZC") if records_azc else None

# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: QO-PREFIX ESCAPE ROUTES")
print("=" * 70)

def analyze_qo_patterns(tokens, label):
    """Analyze qo-prefix usage as escape route"""
    token_list = [r['token'] for r in tokens]
    qo_count = sum(1 for t in token_list if t.startswith('qo'))
    total = len(token_list)

    if total == 0:
        print(f"\n{label}: No tokens")
        return 0

    qo_tokens = [t for t in token_list if t.startswith('qo')]
    top_qo = Counter(qo_tokens).most_common(5)

    print(f"\n{label}:")
    print(f"  qo-prefix: {qo_count} ({100*qo_count/total:.2f}%)")
    print(f"  Top qo- forms: {dict(top_qo)}")

    return qo_count / total

b_qo_rate = analyze_qo_patterns(records_b, "Currier B")
a_qo_rate = analyze_qo_patterns(records_a, "Currier A")
azc_qo_rate = analyze_qo_patterns(records_azc, "AZC") if records_azc else 0

print(f"\nqo-rate comparison:")
print(f"  B: {100*b_qo_rate:.2f}%")
print(f"  A: {100*a_qo_rate:.2f}%")
if records_azc:
    print(f"  AZC: {100*azc_qo_rate:.2f}%")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: LINE-POSITION MORPHOLOGY")
print("=" * 70)

def analyze_position_morphology(tokens, label):
    """Analyze prefix distribution by line position"""
    # Group by folio+line to get line length
    lines = defaultdict(list)
    for r in tokens:
        key = (r['folio'], r['line'])
        lines[key].append(r)

    # Categorize tokens by relative position
    initial = []  # First token in line
    final = []    # Last token in line
    middle = []   # Everything else

    for key, line_tokens in lines.items():
        if len(line_tokens) == 0:
            continue
        line_tokens = sorted(line_tokens, key=lambda x: x['position'])
        initial.append(line_tokens[0]['token'])
        final.append(line_tokens[-1]['token'])
        middle.extend(t['token'] for t in line_tokens[1:-1])

    print(f"\n{label}:")
    print(f"  Lines: {len(lines)}")

    # Check prefix distribution by position
    for prefix in ['ch', 'sh', 'qo', 'da', 'ol']:
        init_rate = sum(1 for t in initial if t.startswith(prefix)) / max(len(initial), 1)
        mid_rate = sum(1 for t in middle if t.startswith(prefix)) / max(len(middle), 1)
        fin_rate = sum(1 for t in final if t.startswith(prefix)) / max(len(final), 1)

        if init_rate > 0.001 or mid_rate > 0.001 or fin_rate > 0.001:
            print(f"  {prefix}-: initial={100*init_rate:.1f}%, middle={100*mid_rate:.1f}%, final={100*fin_rate:.1f}%")

    return {
        'initial': Counter(initial),
        'final': Counter(final),
        'middle': Counter(middle)
    }

b_pos = analyze_position_morphology(records_b, "Currier B")
a_pos = analyze_position_morphology(records_a, "Currier A")
if records_azc:
    azc_pos = analyze_position_morphology(records_azc, "AZC")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: FOLIO-LEVEL SISTER-ESCAPE CORRELATION")
print("=" * 70)

def analyze_folio_correlation(tokens, label):
    """Test ch-qo anticorrelation at folio level"""
    folio_stats = defaultdict(lambda: {'ch': 0, 'qo': 0, 'total': 0})

    for r in tokens:
        folio_stats[r['folio']]['total'] += 1
        if r['token'].startswith('ch'):
            folio_stats[r['folio']]['ch'] += 1
        if r['token'].startswith('qo'):
            folio_stats[r['folio']]['qo'] += 1

    # Filter to folios with enough tokens
    valid_folios = [(f, s) for f, s in folio_stats.items() if s['total'] >= 50]

    if len(valid_folios) < 5:
        print(f"\n{label}: Insufficient folios ({len(valid_folios)})")
        return None

    ch_rates = [s['ch']/s['total'] for f, s in valid_folios]
    qo_rates = [s['qo']/s['total'] for f, s in valid_folios]

    # Spearman correlation
    from scipy import stats
    rho, p = stats.spearmanr(ch_rates, qo_rates)

    print(f"\n{label}:")
    print(f"  Folios analyzed: {len(valid_folios)}")
    print(f"  ch-qo correlation: rho={rho:.3f}, p={p:.4f}")
    print(f"  C412 prediction: {'CONFIRMED (anticorrelated)' if rho < 0 and p < 0.05 else 'NOT CONFIRMED'}")

    return rho

try:
    b_corr = analyze_folio_correlation(records_b, "Currier B")
    a_corr = analyze_folio_correlation(records_a, "Currier A")
    if records_azc:
        azc_corr = analyze_folio_correlation(records_azc, "AZC")
except ImportError:
    print("\nScipy not available for correlation test")
    b_corr = a_corr = azc_corr = None

# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
| Pattern | B (baseline) | A | AZC | Notes |
|---------|--------------|---|-----|-------|""")

if b_sisters and a_sisters:
    print(f"| ch:sh ratio | {b_sisters['ch_sh_ratio']:.2f} | {a_sisters['ch_sh_ratio']:.2f} | {azc_sisters['ch_sh_ratio']:.2f if azc_sisters else 'N/A'} | Sister preference |")
    print(f"| ch rate | {100*b_sisters['ch_rate']:.1f}% | {100*a_sisters['ch_rate']:.1f}% | {100*azc_sisters['ch_rate']:.1f}% if azc_sisters else 'N/A' | |")

print(f"| qo rate | {100*b_qo_rate:.1f}% | {100*a_qo_rate:.1f}% | {100*azc_qo_rate:.1f}% | Escape route |")

if b_corr is not None:
    print(f"| ch-qo corr | {b_corr:.2f} | {a_corr:.2f if a_corr else 'N/A'} | {'%.2f' % azc_corr if azc_corr else 'N/A'} | Anticorrelation |")

print("\n" + "=" * 70)
print("FINDINGS")
print("=" * 70)

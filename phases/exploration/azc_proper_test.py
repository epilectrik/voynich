"""
AZC B-Pattern Conformance Test - PROPER DATA SOURCE

Using interlinear_full_words.txt which has standard Voynich vocabulary
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

data_path = Path(r"C:\git\voynich\data\transcriptions\interlinear_full_words.txt")

print("Loading interlinear transcription...")
records = []
with open(data_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        word = row.get('word', '').strip().lower()
        if word and word != 'na':
            records.append({
                'token': word,
                'folio': row.get('folio', ''),
                'section': row.get('section', ''),
                'language': row.get('language', ''),  # A or B
                'line': row.get('line_number', ''),
                'line_initial': row.get('line_initial', '0') == '1',
                'line_final': row.get('line_final', '0') == '1',
                'placement': row.get('placement', '')
            })

print(f"Loaded {len(records)} tokens")

# Classify by Currier type
# Language column gives A or B directly
# AZC needs to be identified by placement or other markers
records_a = [r for r in records if r['language'] == 'A']
records_b = [r for r in records if r['language'] == 'B']

# AZC identification - check placement codes
placements = Counter(r['placement'] for r in records)
print(f"\nPlacements: {placements.most_common(20)}")

# Check for zodiac/cosmo indicators
sections = Counter(r['section'] for r in records)
print(f"Sections: {sections}")

# For now, use A and B from language column
# AZC might need different identification
print(f"\nA tokens: {len(records_a)}")
print(f"B tokens: {len(records_b)}")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: SISTER PAIRS (ch-sh, ok-ot)")
print("=" * 70)

def analyze_sisters(tokens, label):
    token_list = [r['token'] for r in tokens]
    ch = sum(1 for t in token_list if t.startswith('ch'))
    sh = sum(1 for t in token_list if t.startswith('sh'))
    ok = sum(1 for t in token_list if 'ok' in t)
    ot = sum(1 for t in token_list if 'ot' in t)
    total = len(token_list)

    print(f"\n{label} ({total} tokens):")
    print(f"  ch-: {ch} ({100*ch/total:.2f}%)")
    print(f"  sh-: {sh} ({100*sh/total:.2f}%)")
    print(f"  ch:sh = {ch/max(sh,1):.1f}")
    print(f"  ok-containing: {ok} ({100*ok/total:.2f}%)")
    print(f"  ot-containing: {ot} ({100*ot/total:.2f}%)")

    return {'ch': ch, 'sh': sh, 'ok': ok, 'ot': ot, 'total': total}

a_sis = analyze_sisters(records_a, "Currier A")
b_sis = analyze_sisters(records_b, "Currier B")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: QO-PREFIX ESCAPE ROUTES (C397)")
print("=" * 70)

def analyze_qo(tokens, label):
    token_list = [r['token'] for r in tokens]
    qo = sum(1 for t in token_list if t.startswith('qo'))
    total = len(token_list)

    qo_tokens = [t for t in token_list if t.startswith('qo')]
    top_qo = Counter(qo_tokens).most_common(10)

    print(f"\n{label}:")
    print(f"  qo-prefix: {qo} ({100*qo/total:.2f}%)")
    print(f"  Top qo- forms: {dict(top_qo)}")

    return qo / total

a_qo = analyze_qo(records_a, "Currier A")
b_qo = analyze_qo(records_b, "Currier B")

print(f"\nC397 prediction: qo = 25-47% of tokens")
print(f"  A: {100*a_qo:.1f}% - {'IN RANGE' if 25 <= 100*a_qo <= 47 else 'OUT OF RANGE'}")
print(f"  B: {100*b_qo:.1f}% - {'IN RANGE' if 25 <= 100*b_qo <= 47 else 'OUT OF RANGE'}")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: TOP PREFIXES BY SYSTEM")
print("=" * 70)

def get_prefixes(tokens, n=2):
    prefixes = []
    for r in tokens:
        if len(r['token']) >= n:
            prefixes.append(r['token'][:n])
    return Counter(prefixes)

a_pre = get_prefixes(records_a)
b_pre = get_prefixes(records_b)

print("\nCurrier A top 15:")
for p, c in a_pre.most_common(15):
    print(f"  {p}: {c} ({100*c/len(records_a):.1f}%)")

print("\nCurrier B top 15:")
for p, c in b_pre.most_common(15):
    print(f"  {p}: {c} ({100*c/len(records_b):.1f}%)")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: ESCAPE-SISTER ANTICORRELATION (C412)")
print("=" * 70)

def folio_correlation(tokens, label):
    folio_stats = defaultdict(lambda: {'ch': 0, 'qo': 0, 'total': 0})
    for r in tokens:
        f = r['folio']
        folio_stats[f]['total'] += 1
        if r['token'].startswith('ch'):
            folio_stats[f]['ch'] += 1
        if r['token'].startswith('qo'):
            folio_stats[f]['qo'] += 1

    valid = [(f, s) for f, s in folio_stats.items() if s['total'] >= 50]
    if len(valid) < 5:
        print(f"\n{label}: Insufficient folios ({len(valid)})")
        return None

    ch_rates = [s['ch']/s['total'] for f, s in valid]
    qo_rates = [s['qo']/s['total'] for f, s in valid]

    rho, p = stats.spearmanr(ch_rates, qo_rates)
    print(f"\n{label}:")
    print(f"  Folios: {len(valid)}")
    print(f"  ch-qo correlation: rho={rho:.3f}, p={p:.4f}")
    print(f"  C412 (anticorrelation): {'CONFIRMED' if rho < -0.2 and p < 0.05 else 'NOT CONFIRMED'}")
    return rho

b_corr = folio_correlation(records_b, "Currier B")
a_corr = folio_correlation(records_a, "Currier A")

# ============================================================================
print("\n" + "=" * 70)
print("TEST 5: LINE POSITION PATTERNS")
print("=" * 70)

def position_analysis(tokens, label):
    initial = [r['token'] for r in tokens if r['line_initial']]
    final = [r['token'] for r in tokens if r['line_final']]

    print(f"\n{label}:")
    print(f"  Line-initial tokens: {len(initial)}")
    print(f"  Line-final tokens: {len(final)}")

    # Check qo- distribution
    qo_init = sum(1 for t in initial if t.startswith('qo')) / max(len(initial), 1)
    qo_fin = sum(1 for t in final if t.startswith('qo')) / max(len(final), 1)
    print(f"  qo- at line-initial: {100*qo_init:.1f}%")
    print(f"  qo- at line-final: {100*qo_fin:.1f}%")

    # Check ch- distribution
    ch_init = sum(1 for t in initial if t.startswith('ch')) / max(len(initial), 1)
    ch_fin = sum(1 for t in final if t.startswith('ch')) / max(len(final), 1)
    print(f"  ch- at line-initial: {100*ch_init:.1f}%")
    print(f"  ch- at line-final: {100*ch_fin:.1f}%")

position_analysis(records_b, "Currier B")
position_analysis(records_a, "Currier A")

# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

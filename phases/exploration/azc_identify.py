"""
Identify AZC tokens and compare patterns
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
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
        word = row.get('word', '').strip().lower()
        if word and word != 'na':
            records.append({
                'token': word,
                'folio': row.get('folio', ''),
                'section': row.get('section', ''),
                'language': row.get('language', ''),
                'placement': row.get('placement', ''),
            })

print(f"Loaded {len(records)} tokens")

# AZC identification strategies:
# 1. Section Z (Zodiac)
# 2. Section C (Cosmological)
# 3. Placement codes R, C, S (diagram regions)

# Strategy 1: Section-based
records_z = [r for r in records if r['section'] == 'Z']
records_c = [r for r in records if r['section'] == 'C']

print(f"\nSection Z (Zodiac): {len(records_z)} tokens")
print(f"Section C (Cosmo): {len(records_c)} tokens")

# Strategy 2: Placement-based (non-paragraph placements)
diagram_placements = ['R', 'R1', 'R2', 'R3', 'C', 'S', 'S1', 'S2', 'Q', 'L', 'L1', 'L2', 'X', 'Y', 'T']
records_diagram = [r for r in records if r['placement'] in diagram_placements]
print(f"Diagram placements: {len(records_diagram)} tokens")

# What language are diagram tokens?
diag_lang = Counter(r['language'] for r in records_diagram)
print(f"Diagram tokens by language: {diag_lang}")

# Use combination: Section Z + diagram placements
records_azc = [r for r in records if r['section'] == 'Z' or r['placement'] in diagram_placements]
azc_unique = set(r['folio'] for r in records_azc)
print(f"\nAZC candidates (Z or diagram): {len(records_azc)} tokens from {len(azc_unique)} folios")

# Get A and B excluding AZC
records_a = [r for r in records if r['language'] == 'A' and r not in records_azc]
records_b = [r for r in records if r['language'] == 'B' and r not in records_azc]

print(f"A (excluding AZC): {len(records_a)}")
print(f"B (excluding AZC): {len(records_b)}")
print(f"AZC: {len(records_azc)}")

# ============================================================================
print("\n" + "=" * 70)
print("COMPARING A / B / AZC")
print("=" * 70)

def analyze_system(tokens, label):
    if len(tokens) == 0:
        print(f"\n{label}: No tokens")
        return {}

    token_list = [r['token'] for r in tokens]
    total = len(token_list)

    # Prefixes
    qo = sum(1 for t in token_list if t.startswith('qo'))
    ch = sum(1 for t in token_list if t.startswith('ch'))
    sh = sum(1 for t in token_list if t.startswith('sh'))
    da = sum(1 for t in token_list if t.startswith('da'))
    ol = sum(1 for t in token_list if t.startswith('ol'))

    print(f"\n{label} ({total} tokens):")
    print(f"  qo-: {qo} ({100*qo/total:.1f}%)")
    print(f"  ch-: {ch} ({100*ch/total:.1f}%)")
    print(f"  sh-: {sh} ({100*sh/total:.1f}%)")
    print(f"  da-: {da} ({100*da/total:.1f}%)")
    print(f"  ol-: {ol} ({100*ol/total:.1f}%)")
    print(f"  ch:sh = {ch/max(sh,1):.2f}")

    return {
        'qo': qo/total,
        'ch': ch/total,
        'sh': sh/total,
        'da': da/total,
        'ch_sh_ratio': ch/max(sh,1)
    }

a_stats = analyze_system(records_a, "Currier A")
b_stats = analyze_system(records_b, "Currier B")
azc_stats = analyze_system(records_azc, "AZC")

# ============================================================================
print("\n" + "=" * 70)
print("AZC AFFINITY TEST")
print("=" * 70)

if azc_stats:
    print("\nFor each metric, is AZC closer to A or B?")

    for metric in ['qo', 'ch', 'sh', 'da', 'ch_sh_ratio']:
        azc_val = azc_stats.get(metric, 0)
        a_val = a_stats.get(metric, 0)
        b_val = b_stats.get(metric, 0)

        a_dist = abs(azc_val - a_val)
        b_dist = abs(azc_val - b_val)

        closer = "A" if a_dist < b_dist else "B"
        print(f"  {metric}: AZC={azc_val:.3f}, A={a_val:.3f}, B={b_val:.3f} -> closer to {closer}")

# ============================================================================
print("\n" + "=" * 70)
print("TOP AZC TOKENS")
print("=" * 70)

azc_tokens = Counter(r['token'] for r in records_azc)
print("\nTop 20 AZC tokens:")
for t, c in azc_tokens.most_common(20):
    print(f"  {t}: {c}")

# ============================================================================
print("\n" + "=" * 70)
print("AZC-EXCLUSIVE PATTERNS")
print("=" * 70)

# Get 2-char prefixes
def get_prefixes(tokens):
    return Counter(r['token'][:2] for r in tokens if len(r['token']) >= 2)

a_pre = get_prefixes(records_a)
b_pre = get_prefixes(records_b)
azc_pre = get_prefixes(records_azc)

a_total = len(records_a)
b_total = len(records_b)
azc_total = len(records_azc)

print("\nPrefixes ENRICHED in AZC vs B (>1.5x):")
for p, c in azc_pre.most_common(30):
    azc_rate = c / azc_total
    b_rate = b_pre.get(p, 0) / b_total
    if b_rate > 0 and azc_rate / b_rate > 1.5:
        print(f"  {p}: AZC={100*azc_rate:.1f}%, B={100*b_rate:.1f}%, ratio={azc_rate/b_rate:.1f}x")

print("\nPrefixes DEPLETED in AZC vs B (>2x):")
for p, c in b_pre.most_common(30):
    b_rate = c / b_total
    azc_rate = azc_pre.get(p, 0) / azc_total
    if azc_rate > 0 and b_rate / azc_rate > 2:
        print(f"  {p}: B={100*b_rate:.1f}%, AZC={100*azc_rate:.1f}%, ratio={b_rate/azc_rate:.1f}x depleted")

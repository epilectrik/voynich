"""
HT Line-Type Analysis - OTHER Category Breakdown

The "OTHER" category is large (30%). Let's break it down to understand what
types of tokens are NOT covered by the main grammar prefixes.
"""

from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

def get_ht_prefix(word):
    if word in {'y', 'f', 'd', 'r'}:
        return word
    y_prefixes = ['yche', 'ych', 'ysh', 'yqo', 'yt', 'yk', 'yp', 'yo', 'ya']
    for p in y_prefixes:
        if word.startswith(p):
            return p
    if word.startswith('y'):
        return 'y_other'
    for p in ['pch', 'dch', 'psh', 'ksh', 'ksc', 'op', 'sa', 'so', 'ka']:
        if word.startswith(p):
            return p
    return None

def get_detailed_class(word):
    """More detailed classification including OTHER breakdown."""
    # Escape
    if word.startswith('qok'):
        return 'qok_ESCAPE'
    # LINK
    if word.startswith('al') or (word.startswith('ol') and len(word) <= 4):
        return 'LINK'
    # Main grammar prefixes
    if word.startswith('ch') or word.startswith('ckh'):
        return 'ch_CONTROL'
    if word.startswith('sh'):
        return 'sh_CONTROL'
    if word.startswith('qo'):
        return 'qo_ENERGY'
    if word.startswith('ok'):
        return 'ok_ENERGY'
    if word.startswith('ot'):
        return 'ot_ENERGY'
    if word.startswith('da'):
        return 'da_INFRA'
    if word.startswith('ct'):
        return 'ct_INFRA'
    # L-operators
    if word.startswith('lk') or word.startswith('lch') or word.startswith('lsh'):
        return 'l_COMPOUND'
    if word.startswith('ls'):
        return 'l_COMPOUND'
    # Single-char primitives
    if len(word) == 1:
        return f'ATOM_{word}'
    # Y-tokens that appear within lines
    if word.startswith('y'):
        return 'y_INLINE'
    # Ar/or tokens
    if word.startswith('ar') or word.startswith('or'):
        return 'ar_or_NUCLEUS'
    # S-initial (not sh)
    if word.startswith('s') and not word.startswith('sh'):
        return 's_OTHER'
    # O-initial (not ok/ot/ol)
    if word.startswith('o') and not word.startswith('ok') and not word.startswith('ot') and not word.startswith('ol'):
        return 'o_OTHER'
    # T-initial
    if word.startswith('t'):
        return 't_OTHER'
    # K-initial
    if word.startswith('k') and not word.startswith('ks'):
        return 'k_OTHER'
    # P-initial (not pch/psh)
    if word.startswith('p') and not word.startswith('pch') and not word.startswith('psh'):
        return 'p_OTHER'
    # D-initial (not da/dch)
    if word.startswith('d') and not word.startswith('da') and not word.startswith('dch'):
        return 'd_OTHER'
    # F-initial
    if word.startswith('f'):
        return 'f_OTHER'
    # R-initial
    if word.startswith('r'):
        return 'r_OTHER'
    # L-initial (not covered above)
    if word.startswith('l'):
        return 'l_OTHER'
    # A-initial (not al/ar)
    if word.startswith('a'):
        return 'a_OTHER'
    # C-initial (not ch/ct/ckh)
    if word.startswith('c'):
        return 'c_OTHER'

    return 'UNKNOWN'

# Load data
tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 14:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()
            transcriber = parts[12].strip('"').strip()

            if word and not word.startswith('*'):
                tokens.append({
                    'word': word,
                    'folio': folio,
                    'language': language,
                    'line': line_num,
                    'transcriber': transcriber,
                    'folio_line': f"{folio}_{line_num}_{transcriber}"
                })

# Currier B only
b_tokens = [t for t in tokens if t['language'] == 'B']

# Group by lines
lines = defaultdict(list)
for t in b_tokens:
    lines[t['folio_line']].append(t)

# Get HT-initial lines
ht_lines = {}
for line_id, line_tokens in lines.items():
    if line_tokens:
        ht_pref = get_ht_prefix(line_tokens[0]['word'])
        if ht_pref:
            ht_lines[line_id] = (ht_pref, line_tokens)

print("=" * 80)
print("OTHER CATEGORY BREAKDOWN")
print("=" * 80)

# Collect all non-HT-initial tokens
all_detailed = Counter()
for line_id, (ht_pref, line_tokens) in ht_lines.items():
    for i, tok in enumerate(line_tokens):
        if i > 0:
            all_detailed[get_detailed_class(tok['word'])] += 1

print("\n### All grammar categories in HT-initial lines:")
total = sum(all_detailed.values())
for cat, cnt in all_detailed.most_common(30):
    print(f"  {cat:<20} {cnt:>6} ({100*cnt/total:>5.1f}%)")

# Now look at second-token position specifically
print("\n" + "=" * 80)
print("SECOND TOKEN DETAILED BREAKDOWN BY HT PREFIX")
print("=" * 80)

profiles = defaultdict(lambda: Counter())
for line_id, (ht_pref, line_tokens) in ht_lines.items():
    if len(line_tokens) >= 2:
        second = line_tokens[1]['word']
        profiles[ht_pref][get_detailed_class(second)] += 1

major = [p for p in profiles if sum(profiles[p].values()) >= 30]
major.sort(key=lambda x: -sum(profiles[x].values()))

for ht_pref in major:
    print(f"\n### {ht_pref.upper()} second-token breakdown:")
    total = sum(profiles[ht_pref].values())
    for cat, cnt in profiles[ht_pref].most_common(10):
        print(f"  {cat:<20} {cnt:>4} ({100*cnt/total:>5.1f}%)")

# ============================================================================
# SPECIFIC PATTERN ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("DISTINCTIVE SECOND-TOKEN PATTERNS")
print("=" * 80)

# Compute baseline for second tokens
baseline_2nd = Counter()
for ht_pref in major:
    baseline_2nd += profiles[ht_pref]

total_baseline = sum(baseline_2nd.values())
baseline_pct = {k: v/total_baseline for k, v in baseline_2nd.items()}

print("\n### Enrichment patterns (2nd token):")
for ht_pref in major:
    total = sum(profiles[ht_pref].values())
    if total < 30:
        continue

    enriched = []
    for cat, cnt in profiles[ht_pref].items():
        obs = cnt / total
        exp = baseline_pct.get(cat, 0)
        if exp > 0.02:  # Only consider categories with >2% baseline
            ratio = obs / exp
            if ratio > 1.5:
                enriched.append(f"{cat} {ratio:.1f}x")
            elif ratio < 0.5:
                enriched.append(f"{cat} {ratio:.1f}x")

    if enriched:
        print(f"\n{ht_pref.upper()}: {', '.join(enriched[:5])}")

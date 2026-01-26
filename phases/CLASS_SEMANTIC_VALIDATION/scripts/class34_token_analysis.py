"""
Q16: Class 34 Token Analysis

From C555: Class 33 depleted 0.20x in PHARMA, Class 34 enriched 1.90x.
What makes Class 34 PHARMA-preferred? Token-level investigation.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/CLASS_SEMANTIC_VALIDATION/results'

# Load transcript
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

# Load REGIME
with open(REGIME_FILE) as f:
    regime_data = json.load(f)

folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Section definition
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    else:
        return 'RECIPE'

print("=" * 70)
print("Q16: CLASS 34 TOKEN ANALYSIS")
print("=" * 70)

# 1. CLASS 33 vs 34 TOKENS
print("\n" + "-" * 70)
print("1. CLASS MEMBERSHIP")
print("-" * 70)

c33_tokens = set(class_to_tokens[33])
c34_tokens = set(class_to_tokens[34])

print(f"\nClass 33 tokens ({len(c33_tokens)}): {sorted(c33_tokens)[:20]}...")
print(f"Class 34 tokens ({len(c34_tokens)}): {sorted(c34_tokens)[:20]}...")

# 2. MORPHOLOGICAL COMPARISON
print("\n" + "-" * 70)
print("2. MORPHOLOGICAL STRUCTURE")
print("-" * 70)

def analyze_morphology(token_set, label):
    prefixes = Counter()
    middles = Counter()
    suffixes = Counter()
    articulators = Counter()

    for tok in token_set:
        m = morph.extract(tok)
        if m:
            if m.articulator:
                articulators[m.articulator] += 1
            if m.prefix:
                prefixes[m.prefix] += 1
            if m.middle:
                middles[m.middle] += 1
            if m.suffix:
                suffixes[m.suffix] += 1

    print(f"\n{label}:")
    print(f"  Articulators: {dict(articulators.most_common(5))}")
    print(f"  Prefixes: {dict(prefixes.most_common(5))}")
    print(f"  Middles: {dict(middles.most_common(5))}")
    print(f"  Suffixes: {dict(suffixes.most_common(5))}")

    return {'prefixes': prefixes, 'middles': middles, 'suffixes': suffixes, 'articulators': articulators}

m33 = analyze_morphology(c33_tokens, "Class 33")
m34 = analyze_morphology(c34_tokens, "Class 34")

# 3. TOKEN FREQUENCY BY SECTION
print("\n" + "-" * 70)
print("3. TOKEN FREQUENCY BY SECTION")
print("-" * 70)

# Count occurrences by token and section
token_section_counts = defaultdict(lambda: defaultdict(int))
section_totals = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    folio = token.folio
    section = get_section(folio)

    if word in c33_tokens or word in c34_tokens:
        token_section_counts[word][section] += 1
        section_totals[section] += 1

# Find tokens most enriched in PHARMA
print("\n| Token | Class | PHARMA | HERBAL | BIO | RECIPE | PHARMA% |")
print("|-------|-------|--------|--------|-----|--------|---------|")

pharma_enriched = []
for tok in sorted(set(c33_tokens) | set(c34_tokens)):
    counts = token_section_counts[tok]
    total = sum(counts.values())
    if total >= 5:  # Minimum 5 occurrences
        pharma_pct = counts['PHARMA'] / total * 100 if total > 0 else 0
        cls = 33 if tok in c33_tokens else 34
        pharma_enriched.append({
            'token': tok,
            'class': cls,
            'pharma': counts['PHARMA'],
            'herbal': counts['HERBAL'],
            'bio': counts['BIO'],
            'recipe': counts['RECIPE'],
            'pharma_pct': pharma_pct,
            'total': total
        })

pharma_enriched.sort(key=lambda x: -x['pharma_pct'])
for t in pharma_enriched[:15]:
    print(f"| {t['token']:5s} | {t['class']:5d} | {t['pharma']:6d} | {t['herbal']:6d} | {t['bio']:3d} | {t['recipe']:6d} | {t['pharma_pct']:6.1f}% |")

# 4. WHAT DISTINGUISHES PHARMA-PREFERRED TOKENS?
print("\n" + "-" * 70)
print("4. PHARMA-PREFERRED TOKEN CHARACTERISTICS")
print("-" * 70)

# Split by PHARMA preference
high_pharma = [t for t in pharma_enriched if t['pharma_pct'] >= 30]
low_pharma = [t for t in pharma_enriched if t['pharma_pct'] < 30]

print(f"\nHigh PHARMA preference (>=30%): {len(high_pharma)} tokens")
print(f"Low PHARMA preference (<30%): {len(low_pharma)} tokens")

# Morphology of high-PHARMA tokens
print("\nHigh-PHARMA token morphology:")
high_pharma_prefixes = Counter()
high_pharma_middles = Counter()
high_pharma_suffixes = Counter()

for t in high_pharma:
    tok = t['token']
    m = morph.extract(tok)
    if m:
        if m.prefix:
            high_pharma_prefixes[m.prefix] += 1
        if m.middle:
            high_pharma_middles[m.middle] += 1
        if m.suffix:
            high_pharma_suffixes[m.suffix] += 1

print(f"  Prefixes: {dict(high_pharma_prefixes.most_common(5))}")
print(f"  Middles: {dict(high_pharma_middles.most_common(5))}")
print(f"  Suffixes: {dict(high_pharma_suffixes.most_common(5))}")

# Class breakdown
high_pharma_c33 = sum(1 for t in high_pharma if t['class'] == 33)
high_pharma_c34 = sum(1 for t in high_pharma if t['class'] == 34)
print(f"\nClass 33 in high-PHARMA: {high_pharma_c33}")
print(f"Class 34 in high-PHARMA: {high_pharma_c34}")

# 5. DISTINGUISHING MORPHOLOGICAL FEATURES
print("\n" + "-" * 70)
print("5. CLASS 33 vs 34 MORPHOLOGICAL DIFFERENCES")
print("-" * 70)

# Find features unique or enriched in each class
all_prefixes = set(m33['prefixes'].keys()) | set(m34['prefixes'].keys())
all_middles = set(m33['middles'].keys()) | set(m34['middles'].keys())
all_suffixes = set(m33['suffixes'].keys()) | set(m34['suffixes'].keys())

print("\nPrefix distribution:")
for p in sorted(all_prefixes):
    c33_count = m33['prefixes'].get(p, 0)
    c34_count = m34['prefixes'].get(p, 0)
    if c33_count > 0 or c34_count > 0:
        ratio = c34_count / c33_count if c33_count > 0 else float('inf')
        print(f"  {p}: C33={c33_count}, C34={c34_count}, ratio={ratio:.2f}x")

print("\nMiddle distribution:")
for m_mid in sorted(all_middles)[:10]:  # Top 10
    c33_count = m33['middles'].get(m_mid, 0)
    c34_count = m34['middles'].get(m_mid, 0)
    if c33_count > 0 or c34_count > 0:
        ratio = c34_count / c33_count if c33_count > 0 else float('inf')
        print(f"  {m_mid}: C33={c33_count}, C34={c34_count}, ratio={ratio:.2f}x")

print("\nSuffix distribution:")
for s in sorted(all_suffixes):
    c33_count = m33['suffixes'].get(s, 0)
    c34_count = m34['suffixes'].get(s, 0)
    if c33_count > 0 or c34_count > 0:
        ratio = c34_count / c33_count if c33_count > 0 else float('inf')
        print(f"  {s}: C33={c33_count}, C34={c34_count}, ratio={ratio:.2f}x")

# 6. POSITION IN LINE ANALYSIS
print("\n" + "-" * 70)
print("6. LINE POSITION BY CLASS")
print("-" * 70)

# Analyze position distribution using line_initial and line_final attributes
c33_positions = {'initial': 0, 'medial': 0, 'final': 0}
c34_positions = {'initial': 0, 'medial': 0, 'final': 0}

for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls == 33:
        if token.line_initial:
            c33_positions['initial'] += 1
        elif token.line_final:
            c33_positions['final'] += 1
        else:
            c33_positions['medial'] += 1
    elif cls == 34:
        if token.line_initial:
            c34_positions['initial'] += 1
        elif token.line_final:
            c34_positions['final'] += 1
        else:
            c34_positions['medial'] += 1

c33_total = sum(c33_positions.values())
c34_total = sum(c34_positions.values())

print("\n| Class | Initial | Medial | Final | Total |")
print("|-------|---------|--------|-------|-------|")
print(f"| 33    | {c33_positions['initial']:7d} ({c33_positions['initial']/c33_total*100:.1f}%) | {c33_positions['medial']:6d} ({c33_positions['medial']/c33_total*100:.1f}%) | {c33_positions['final']:5d} ({c33_positions['final']/c33_total*100:.1f}%) | {c33_total:5d} |")
print(f"| 34    | {c34_positions['initial']:7d} ({c34_positions['initial']/c34_total*100:.1f}%) | {c34_positions['medial']:6d} ({c34_positions['medial']/c34_total*100:.1f}%) | {c34_positions['final']:5d} ({c34_positions['final']/c34_total*100:.1f}%) | {c34_total:5d} |")

# 7. CO-OCCURRENCE PATTERNS
print("\n" + "-" * 70)
print("7. CLASS CO-OCCURRENCE ON SAME LINE")
print("-" * 70)

# For each class, what other classes appear on same line?
c33_cooccurs = Counter()
c34_cooccurs = Counter()

for token in tokens:
    word = token.word.replace('*', '').strip()
    key = (token.folio, token.line)
    cls = token_to_class.get(word)

    if cls is not None:
        # Get all classes on this line
        line_classes = set()
        for t2 in tokens:
            if (t2.folio, t2.line) == key:
                w2 = t2.word.replace('*', '').strip()
                c2 = token_to_class.get(w2)
                if c2 is not None:
                    line_classes.add(c2)

        if cls == 33:
            for c2 in line_classes:
                if c2 != 33:
                    c33_cooccurs[c2] += 1
        elif cls == 34:
            for c2 in line_classes:
                if c2 != 34:
                    c34_cooccurs[c2] += 1

print("\nTop co-occurring classes with Class 33:")
for cls, count in c33_cooccurs.most_common(10):
    print(f"  Class {cls}: {count}")

print("\nTop co-occurring classes with Class 34:")
for cls, count in c34_cooccurs.most_common(10):
    print(f"  Class {cls}: {count}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

c33_pharma_rate = sum(1 for t in pharma_enriched if t['class'] == 33 and t['pharma_pct'] >= 30)
c34_pharma_rate = sum(1 for t in pharma_enriched if t['class'] == 34 and t['pharma_pct'] >= 30)

print(f"""
1. TOKEN COUNTS:
   - Class 33: {len(c33_tokens)} token types
   - Class 34: {len(c34_tokens)} token types

2. PHARMA PREFERENCE:
   - High-PHARMA Class 33 tokens: {c33_pharma_rate}
   - High-PHARMA Class 34 tokens: {c34_pharma_rate}

3. MORPHOLOGICAL DIFFERENCES:
   - Class 33 prefixes: {dict(m33['prefixes'].most_common(3))}
   - Class 34 prefixes: {dict(m34['prefixes'].most_common(3))}

4. POSITION PATTERNS:
   - Class 33: {c33_positions['initial']/c33_total*100:.1f}% initial, {c33_positions['medial']/c33_total*100:.1f}% medial, {c33_positions['final']/c33_total*100:.1f}% final
   - Class 34: {c34_positions['initial']/c34_total*100:.1f}% initial, {c34_positions['medial']/c34_total*100:.1f}% medial, {c34_positions['final']/c34_total*100:.1f}% final
""")

# Save results
results = {
    'class33_tokens': sorted(c33_tokens),
    'class34_tokens': sorted(c34_tokens),
    'class33_morphology': {
        'prefixes': dict(m33['prefixes']),
        'middles': dict(m33['middles']),
        'suffixes': dict(m33['suffixes'])
    },
    'class34_morphology': {
        'prefixes': dict(m34['prefixes']),
        'middles': dict(m34['middles']),
        'suffixes': dict(m34['suffixes'])
    },
    'pharma_enriched_tokens': pharma_enriched[:20],
    'position_distribution': {
        'class33': c33_positions,
        'class34': c34_positions
    }
}

with open(RESULTS / 'class34_token_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'class34_token_analysis.json'}")

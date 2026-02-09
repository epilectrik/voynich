"""
03_label_extension_profile.py - Extension profile in labels vs text

Question: Do labels (3.7x RI-enriched per C914) show different extension profiles than text?

Prediction: If labels identify specific instances and extensions encode operational context,
labels may show different extension distributions reflecting identification vs operational use.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
import pandas as pd
from collections import Counter, defaultdict
from scipy import stats
import json

morph = Morphology()
tx = Transcript()

# Build B vocabulary for extension detection
b_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

pp_sorted = sorted(b_middles, key=len, reverse=True)

def find_extension(ri_middle):
    for pp in pp_sorted:
        if len(pp) >= 2:
            if ri_middle.startswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[len(pp):]
            elif ri_middle.endswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[:-len(pp)]
    return None

# Load A tokens
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A']

# Split into labels vs text
labels = df_a[df_a['placement'].str.startswith('L', na=False)]
text = df_a[~df_a['placement'].str.startswith('L', na=False)]

print("="*70)
print("LABEL vs TEXT EXTENSION PROFILE")
print("="*70)

print(f"\nTotal A tokens: {len(df_a)}")
print(f"Labels: {len(labels)}")
print(f"Text: {len(text)}")

# Collect extensions
def get_extensions(dataframe):
    extensions = []
    for _, row in dataframe.iterrows():
        word = row['word']
        if pd.isna(word) or not isinstance(word, str):
            continue
        m = morph.extract(word)
        if m and m.middle and m.middle not in b_middles:
            ext = find_extension(m.middle)
            if ext and len(ext) == 1:
                extensions.append(ext)
    return extensions

label_extensions = get_extensions(labels)
text_extensions = get_extensions(text)

print(f"\nExtension tokens in labels: {len(label_extensions)}")
print(f"Extension tokens in text: {len(text_extensions)}")

# Extension profiles
label_counts = Counter(label_extensions)
text_counts = Counter(text_extensions)

print("\n" + "="*70)
print("EXTENSION DISTRIBUTION COMPARISON")
print("="*70)

# Get all extensions
all_ext = set(label_counts.keys()) | set(text_counts.keys())
key_extensions = ['h', 'k', 't', 'd', 'o', 'l', 's', 'e', 'a', 'r']

results = {
    'label_total': len(label_extensions),
    'text_total': len(text_extensions),
    'extensions': {}
}

print(f"\n{'Ext':<5} {'Label':<12} {'Text':<12} {'Label%':<10} {'Text%':<10} {'Enrichment':<12}")
print("-"*65)

enrichments = []
for ext in key_extensions:
    label_n = label_counts.get(ext, 0)
    text_n = text_counts.get(ext, 0)

    label_pct = 100 * label_n / len(label_extensions) if label_extensions else 0
    text_pct = 100 * text_n / len(text_extensions) if text_extensions else 0

    if text_pct > 0:
        enrichment = label_pct / text_pct
    else:
        enrichment = float('inf') if label_pct > 0 else 0

    marker = ""
    if enrichment > 1.5:
        marker = "LABEL+"
    elif enrichment < 0.67:
        marker = "TEXT+"

    print(f"'{ext}'   {label_n:<12} {text_n:<12} {label_pct:<10.1f} {text_pct:<10.1f} {enrichment:<10.2f}x {marker}")

    results['extensions'][ext] = {
        'label_count': label_n,
        'text_count': text_n,
        'label_pct': round(label_pct, 2),
        'text_pct': round(text_pct, 2),
        'enrichment': round(enrichment, 2) if enrichment != float('inf') else 'inf'
    }

    if label_n >= 3 and text_n >= 3:
        enrichments.append({
            'extension': ext,
            'label_pct': label_pct,
            'text_pct': text_pct,
            'enrichment': enrichment
        })

# Statistical test: Are distributions different?
print("\n" + "="*70)
print("STATISTICAL TEST: LABEL vs TEXT DISTRIBUTION")
print("="*70)

# Chi-square test on major extensions
major_ext = [e for e in key_extensions if label_counts.get(e, 0) >= 3 and text_counts.get(e, 0) >= 3]

if len(major_ext) >= 3:
    label_row = [label_counts.get(ext, 0) for ext in major_ext]
    text_row = [text_counts.get(ext, 0) for ext in major_ext]

    contingency = [label_row, text_row]
    chi2, p, dof, expected = stats.chi2_contingency(contingency)

    print(f"\nChi-square test (label vs text extension distribution):")
    print(f"  Extensions tested: {major_ext}")
    print(f"  Chi-square: {chi2:.2f}")
    print(f"  Degrees of freedom: {dof}")
    print(f"  p-value: {p:.4f}")

    if p < 0.001:
        print("  -> HIGHLY SIGNIFICANT: Labels have different extension profile than text")
    elif p < 0.05:
        print("  -> SIGNIFICANT: Labels have different extension profile than text")
    else:
        print("  -> Not significant: Similar extension profiles")

    results['chi_square'] = {'chi2': float(chi2), 'p_value': float(p), 'significant': bool(p < 0.05)}

# Per-extension tests
print("\n" + "="*70)
print("PER-EXTENSION SIGNIFICANCE (Fisher's exact)")
print("="*70)

significant_diffs = []
for ext in key_extensions:
    label_n = label_counts.get(ext, 0)
    text_n = text_counts.get(ext, 0)
    label_other = len(label_extensions) - label_n
    text_other = len(text_extensions) - text_n

    if label_n + text_n >= 10:  # Minimum for meaningful test
        contingency = [[label_n, label_other], [text_n, text_other]]
        odds, p = stats.fisher_exact(contingency)

        if p < 0.1:
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "~"
            direction = "LABEL" if odds > 1 else "TEXT"
            print(f"  '{ext}': p={p:.4f} {sig} -> {direction} enriched (OR={odds:.2f})")
            significant_diffs.append({
                'extension': ext,
                'p_value': round(p, 4),
                'odds_ratio': round(odds, 2),
                'direction': direction
            })

results['significant_diffs'] = significant_diffs

# Section breakdown for labels
print("\n" + "="*70)
print("LABEL EXTENSIONS BY SECTION")
print("="*70)

label_section_ext = defaultdict(list)
for _, row in labels.iterrows():
    word = row['word']
    section = row.get('section', 'UNK')
    if pd.isna(word) or not isinstance(word, str):
        continue
    if pd.isna(section):
        section = 'UNK'
    m = morph.extract(word)
    if m and m.middle and m.middle not in b_middles:
        ext = find_extension(m.middle)
        if ext and len(ext) == 1:
            label_section_ext[section].append(ext)

for section in sorted(label_section_ext.keys()):
    exts = label_section_ext[section]
    if len(exts) >= 5:
        counts = Counter(exts)
        print(f"\nSection {section} labels (n={len(exts)}):")
        for ext, count in counts.most_common(5):
            print(f"  '{ext}': {count} ({100*count/len(exts):.0f}%)")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

# Find most label-enriched and text-enriched
label_enriched = sorted(enrichments, key=lambda x: -x['enrichment'])[:3]
text_enriched = sorted(enrichments, key=lambda x: x['enrichment'])[:3]

print(f"""
Most LABEL-enriched extensions:
{chr(10).join(f"  '{e['extension']}': {e['enrichment']:.1f}x" for e in label_enriched if e['enrichment'] > 1)}

Most TEXT-enriched extensions:
{chr(10).join(f"  '{e['extension']}': {e['enrichment']:.2f}x" for e in text_enriched if e['enrichment'] < 1)}

If labels identify specific instances:
- Expect extensions that differentiate instances (possibly d, o)
- May under-represent operational context markers (h, k, t)

If labels serve same function as text:
- Extension profiles should be similar
""")

# Save results
output_path = 'phases/EXTENSION_DISTRIBUTION_PATTERNS/results/label_extension_profile.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")

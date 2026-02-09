"""
01_extension_section_profile.py - Extension distribution by section

Question: Do sections specialize by operation type as reflected in extension profiles?

Prediction: If extensions encode operational context (h=monitoring, k=energy, etc.),
sections should show distinct extension profiles matching their operational focus.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
import pandas as pd
from collections import defaultdict, Counter
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
text_only = df_a[~df_a['placement'].str.startswith('L', na=False)]

print("="*70)
print("EXTENSION DISTRIBUTION BY SECTION")
print("="*70)

# Collect extension data by section
section_extensions = defaultdict(list)
extension_sections = defaultdict(list)

for _, row in text_only.iterrows():
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
            section_extensions[section].append(ext)
            extension_sections[ext].append(section)

# Overall extension distribution
all_extensions = []
for exts in section_extensions.values():
    all_extensions.extend(exts)

total_ext = len(all_extensions)
ext_baseline = Counter(all_extensions)

print(f"\nTotal extension tokens: {total_ext}")
print(f"\nBaseline extension distribution:")
for ext, count in ext_baseline.most_common(10):
    print(f"  '{ext}': {count} ({100*count/total_ext:.1f}%)")

# Section profiles
print("\n" + "="*70)
print("EXTENSION PROFILE BY SECTION")
print("="*70)

section_profiles = {}
for section in sorted(section_extensions.keys()):
    exts = section_extensions[section]
    if len(exts) >= 20:  # Minimum sample
        ext_counts = Counter(exts)
        profile = {ext: count/len(exts) for ext, count in ext_counts.items()}
        section_profiles[section] = {
            'n': len(exts),
            'profile': profile,
            'counts': dict(ext_counts)
        }

        print(f"\nSection {section} (n={len(exts)}):")
        for ext, count in ext_counts.most_common(5):
            baseline_rate = ext_baseline[ext] / total_ext
            obs_rate = count / len(exts)
            enrichment = obs_rate / baseline_rate if baseline_rate > 0 else 0
            marker = "**" if enrichment > 1.5 else "*" if enrichment > 1.2 else ""
            print(f"  '{ext}': {count} ({100*obs_rate:.0f}%) vs baseline {100*baseline_rate:.0f}% [{enrichment:.1f}x] {marker}")

# Key extensions by section
print("\n" + "="*70)
print("KEY EXTENSION ENRICHMENTS BY SECTION")
print("="*70)

key_extensions = ['h', 'k', 't', 'd', 'o', 'l', 's']
results = {'sections': {}, 'enrichments': []}

print(f"\n{'Section':<10} {'n':<6} " + " ".join(f"'{e}'%  " for e in key_extensions))
print("-"*70)

for section in sorted(section_profiles.keys()):
    profile = section_profiles[section]
    n = profile['n']
    rates = []
    section_data = {'n': n, 'rates': {}}

    for ext in key_extensions:
        rate = profile['profile'].get(ext, 0)
        rates.append(f"{100*rate:4.0f}%  ")
        section_data['rates'][ext] = round(rate, 3)

        # Calculate enrichment
        baseline_rate = ext_baseline[ext] / total_ext
        if baseline_rate > 0:
            enrichment = rate / baseline_rate
            if enrichment > 1.5 or enrichment < 0.5:
                results['enrichments'].append({
                    'section': section,
                    'extension': ext,
                    'rate': round(rate, 3),
                    'baseline': round(baseline_rate, 3),
                    'enrichment': round(enrichment, 2)
                })

    results['sections'][section] = section_data
    print(f"{section:<10} {n:<6} " + "".join(rates))

# Statistical test: Chi-square for extension × section independence
print("\n" + "="*70)
print("STATISTICAL TEST: EXTENSION × SECTION INDEPENDENCE")
print("="*70)

# Build contingency table for major extensions and sections
major_ext = ['h', 'k', 't', 'd', 'o', 'l']
major_sections = [s for s in section_profiles.keys() if section_profiles[s]['n'] >= 30]

if len(major_sections) >= 2:
    contingency = []
    for section in major_sections:
        row = [section_profiles[section]['counts'].get(ext, 0) for ext in major_ext]
        contingency.append(row)

    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square test (extensions × sections):")
    print(f"  Sections: {major_sections}")
    print(f"  Extensions: {major_ext}")
    print(f"  Chi-square: {chi2:.1f}")
    print(f"  Degrees of freedom: {dof}")
    print(f"  p-value: {p:.2e}")

    if p < 0.001:
        print("  -> HIGHLY SIGNIFICANT: Extensions distribute non-uniformly across sections")
    elif p < 0.05:
        print("  -> SIGNIFICANT: Extensions distribute non-uniformly across sections")
    else:
        print("  -> Not significant: Extension distribution is uniform across sections")

    results['chi_square'] = {'chi2': float(chi2), 'p_value': float(p), 'dof': int(dof), 'significant': bool(p < 0.05)}

# Per-extension section concentration
print("\n" + "="*70)
print("SECTION CONCENTRATION BY EXTENSION")
print("="*70)

for ext in key_extensions:
    sections = extension_sections[ext]
    if len(sections) >= 10:
        section_counts = Counter(sections)
        total = len(sections)
        top_section, top_count = section_counts.most_common(1)[0]
        concentration = top_count / total

        print(f"\n'{ext}' extension (n={total}):")
        for sec, count in section_counts.most_common(3):
            print(f"  Section {sec}: {count} ({100*count/total:.0f}%)")

        results['enrichments'].append({
            'extension': ext,
            'top_section': top_section,
            'concentration': round(concentration, 2),
            'total': total
        })

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print("""
Key questions:
1. Do sections specialize in certain extensions?
2. Does h (monitoring) concentrate in specific sections?
3. Do k/t (energy/terminal) show section preferences?

If extensions encode operational context and sections represent operation types,
we expect non-uniform distribution with meaningful clustering.
""")

# Save results
output_path = 'phases/EXTENSION_DISTRIBUTION_PATTERNS/results/extension_section_profile.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")

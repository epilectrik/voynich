"""
02_zodiac_folio_patterns.py - Check zodiac folios for extension patterns

Question: Do other zodiac folios (f70v-f73v) show similar patterns to f57v?
- Extension vocabulary overlap
- h-exclusion from certain positions
- Periodicity in ring content

This tests whether f57v's pattern is unique or part of a zodiac-wide system.
"""
import sys
sys.path.insert(0, 'C:/git/voynich')
import pandas as pd
from collections import Counter, defaultdict
from scipy.stats import fisher_exact
import json

# Extension vocabulary (from C920)
extension_chars = {'a', 'c', 'd', 'e', 'f', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'y'}
kernel_primitives = {'k', 'e', 'h', 's', 't', 'd', 'l', 'o', 'c', 'r'}

# Load data
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

print("="*70)
print("ZODIAC FOLIO PATTERN ANALYSIS")
print("="*70)

# Known zodiac/cosmological folios
zodiac_folios = ['f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
                 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']
cosmo_folios = ['f57v', 'f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2',
                'f68r3', 'f68v1', 'f68v2', 'f68v3', 'f69r', 'f69v']
all_target_folios = ['f57v'] + zodiac_folios + [f for f in cosmo_folios if f != 'f57v']

results = {'folios': {}, 'summary': {}}

# Analyze each folio
print("\n" + "="*70)
print("FOLIO-BY-FOLIO ANALYSIS")
print("="*70)

for folio in all_target_folios:
    folio_data = df[df['folio'] == folio]
    if len(folio_data) == 0:
        continue

    folio_results = {
        'total_tokens': len(folio_data),
        'rings': {}
    }

    # Get ring positions
    ring_data = folio_data[folio_data['placement'].str.match(r'^R\d', na=False)]

    if len(ring_data) == 0:
        continue

    print(f"\n{'='*50}")
    print(f"FOLIO: {folio}")
    print(f"{'='*50}")
    print(f"Total tokens: {len(folio_data)}, Ring tokens: {len(ring_data)}")

    # Analyze by ring position
    for ring in sorted(ring_data['placement'].unique()):
        ring_tokens = ring_data[ring_data['placement'] == ring]
        words = ring_tokens['word'].dropna().tolist()

        if len(words) < 5:
            continue

        # Character analysis
        all_chars = ''.join(words).replace('*', '')
        char_set = set(all_chars)
        single_char_pct = 100 * sum(1 for w in words if len(w) == 1) / len(words)

        # Extension overlap
        ext_overlap = char_set & extension_chars
        ext_pct = 100 * len(ext_overlap) / len(char_set) if char_set else 0

        # h analysis
        h_count = all_chars.count('h')
        h_rate = 100 * h_count / len(all_chars) if all_chars else 0
        has_h = 'h' in char_set

        ring_results = {
            'tokens': len(words),
            'chars': len(all_chars),
            'unique_chars': len(char_set),
            'single_char_pct': round(single_char_pct, 1),
            'extension_overlap_pct': round(ext_pct, 1),
            'h_count': h_count,
            'h_rate': round(h_rate, 2),
            'has_h': has_h,
            'char_set': sorted(char_set)
        }

        folio_results['rings'][ring] = ring_results

        # Print summary
        h_marker = "NO h" if not has_h else f"h={h_rate:.1f}%"
        print(f"  {ring}: {len(words)} tokens, {single_char_pct:.0f}% single-char, "
              f"{ext_pct:.0f}% ext-overlap, {h_marker}")

        # Check for periodicity if high single-char
        if single_char_pct >= 80:
            clean_seq = ''.join(w for w in words if w != '*')
            print(f"    Sequence ({len(clean_seq)} chars): {clean_seq[:50]}...")

            # Test for 12-char period
            if len(clean_seq) >= 24:
                chunks = [clean_seq[i:i+12] for i in range(0, len(clean_seq), 12)]
                if len(chunks) >= 2:
                    # Check similarity between chunks
                    matches = sum(1 for i in range(min(12, len(chunks[0]), len(chunks[1])))
                                  if i < len(chunks[0]) and i < len(chunks[1])
                                  and chunks[0][i] == chunks[1][i])
                    similarity = matches / min(12, len(chunks[0]), len(chunks[1]))
                    print(f"    12-char period test: {similarity*100:.0f}% match between first two chunks")
                    ring_results['period_12_similarity'] = round(similarity, 2)

    results['folios'][folio] = folio_results

# Summary comparison
print("\n" + "="*70)
print("SUMMARY: COMPARISON TO f57v PATTERN")
print("="*70)

print("""
f57v R2 characteristics (reference):
- 100% single-char tokens
- 92% extension vocabulary overlap
- 0% h (categorically excluded)
- 12-char repeating period
""")

# Find similar rings
similar_rings = []
h_excluded_rings = []

for folio, folio_data in results['folios'].items():
    for ring, ring_data in folio_data.get('rings', {}).items():
        if ring_data['single_char_pct'] >= 75:
            similar_rings.append({
                'folio': folio,
                'ring': ring,
                'single_char_pct': ring_data['single_char_pct'],
                'ext_overlap': ring_data['extension_overlap_pct'],
                'h_rate': ring_data['h_rate'],
                'has_h': ring_data['has_h']
            })
        if not ring_data['has_h'] and ring_data['chars'] >= 20:
            h_excluded_rings.append({
                'folio': folio,
                'ring': ring,
                'chars': ring_data['chars'],
                'single_char_pct': ring_data['single_char_pct']
            })

print("\nHigh single-char rings (>=75%):")
print(f"{'Folio':<10} {'Ring':<6} {'Single%':<10} {'Ext%':<8} {'h-rate':<8}")
print("-"*50)
for r in sorted(similar_rings, key=lambda x: -x['single_char_pct']):
    print(f"{r['folio']:<10} {r['ring']:<6} {r['single_char_pct']:<10.0f} {r['ext_overlap']:<8.0f} {r['h_rate']:<8.1f}")

print("\nRings with 0% h (n>=20 chars):")
for r in h_excluded_rings:
    print(f"  {r['folio']} {r['ring']}: {r['chars']} chars, {r['single_char_pct']:.0f}% single-char")

results['summary']['similar_to_f57v'] = similar_rings
results['summary']['h_excluded'] = h_excluded_rings

# Statistical test: h-rate in zodiac vs f57v
print("\n" + "="*70)
print("STATISTICAL TEST: f57v vs OTHER ZODIAC FOLIOS")
print("="*70)

# Aggregate h-rates
f57v_h = 0
f57v_total = 0
other_h = 0
other_total = 0

for folio, folio_data in results['folios'].items():
    for ring, ring_data in folio_data.get('rings', {}).items():
        if folio == 'f57v':
            f57v_h += ring_data['h_count']
            f57v_total += ring_data['chars']
        elif folio in zodiac_folios:
            other_h += ring_data['h_count']
            other_total += ring_data['chars']

if f57v_total > 0 and other_total > 0:
    print(f"\nf57v all rings: {f57v_h}/{f57v_total} = {100*f57v_h/f57v_total:.1f}% h")
    print(f"Other zodiac all rings: {other_h}/{other_total} = {100*other_h/other_total:.1f}% h")

    contingency = [[f57v_h, f57v_total - f57v_h], [other_h, other_total - other_h]]
    odds, p = fisher_exact(contingency)
    print(f"\nFisher's exact: p = {p:.4f}")

    results['summary']['f57v_vs_zodiac'] = {
        'f57v_h_rate': round(f57v_h/f57v_total, 3),
        'zodiac_h_rate': round(other_h/other_total, 3),
        'p_value': round(p, 4)
    }

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

print(f"""
Findings:
- {len(similar_rings)} rings with >=75% single-char content
- {len(h_excluded_rings)} rings with 0% h (n>=20)

If f57v pattern is zodiac-wide:
- Other zodiac folios should show similar single-char rings
- h-exclusion should be systematic

If f57v is unique:
- Pattern specific to f57v's function
- Other zodiac folios use different encoding
""")

# Save results
output_path = 'phases/EXTENSION_DISTRIBUTION_PATTERNS/results/zodiac_folio_patterns.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")

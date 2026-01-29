"""
T3: AZC Folio Specialization

Question: Are any AZC folios specialists (narrow vocabulary) vs generalists (broad vocabulary)?

Method:
1. For each AZC folio, compute:
   - Vocabulary breadth (unique MIDDLEs / tokens)
   - Exclusivity (MIDDLEs appearing ONLY in this folio)
   - Cross-folio sharing (MIDDLEs shared with other AZC folios)
2. Classify folios as specialists (high exclusivity) vs generalists (high sharing)
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ZODIAC_FOLIOS = {
    'f72v3', 'f72v2', 'f72v1', 'f72r3', 'f72r2', 'f72r1',
    'f71v', 'f71r', 'f70v2', 'f70v1', 'f73v', 'f73r', 'f57v'
}

# Collect AZC tokens by folio (diagram text only)
print("Collecting AZC tokens...")
folio_tokens = defaultdict(list)
folio_middles = defaultdict(set)
folio_middle_counts = defaultdict(Counter)

for token in tx.azc():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    placement = getattr(token, 'placement', '')
    if placement.startswith('P'):
        continue

    m = morph.extract(w)
    if m.middle:
        folio_tokens[token.folio].append(w)
        folio_middles[token.folio].add(m.middle)
        folio_middle_counts[token.folio][m.middle] += 1

print(f"Found {len(folio_tokens)} AZC folios")

# Global MIDDLE census
all_middles = set()
middle_folio_count = Counter()  # How many folios each MIDDLE appears in

for folio, middles in folio_middles.items():
    all_middles.update(middles)
    for m in middles:
        middle_folio_count[m] += 1

print(f"Total unique MIDDLEs across AZC: {len(all_middles)}")

# Classify each MIDDLE by exclusivity
exclusive_middles = {m for m, count in middle_folio_count.items() if count == 1}
shared_middles = {m for m, count in middle_folio_count.items() if count > 1}
universal_middles = {m for m, count in middle_folio_count.items() if count >= len(folio_middles) * 0.75}

print(f"Exclusive (1 folio only): {len(exclusive_middles)}")
print(f"Shared (2+ folios): {len(shared_middles)}")
print(f"Universal (75%+ folios): {len(universal_middles)}")

# Analyze each folio
print("\n" + "="*60)
print("FOLIO SPECIALIZATION PROFILES")
print("="*60)

results = {
    'folio_stats': {},
    'summary': {},
}

for folio in sorted(folio_tokens.keys()):
    tokens = folio_tokens[folio]
    middles = folio_middles[folio]

    n_tokens = len(tokens)
    n_middles = len(middles)

    # Type-token ratio (vocabulary density)
    ttr = n_middles / n_tokens if n_tokens > 0 else 0

    # Exclusivity metrics
    exclusive = middles & exclusive_middles
    shared = middles & shared_middles
    universal = middles & universal_middles

    exclusivity_ratio = len(exclusive) / n_middles if n_middles > 0 else 0
    universality_ratio = len(universal) / n_middles if n_middles > 0 else 0

    family = 'Zodiac' if folio in ZODIAC_FOLIOS else 'A/C'

    results['folio_stats'][folio] = {
        'family': family,
        'tokens': n_tokens,
        'middles': n_middles,
        'ttr': round(ttr, 3),
        'exclusive_count': len(exclusive),
        'shared_count': len(shared),
        'universal_count': len(universal),
        'exclusivity_ratio': round(exclusivity_ratio, 3),
        'universality_ratio': round(universality_ratio, 3),
        'exclusive_middles': sorted(exclusive)[:10],  # Top 10 for inspection
    }

    print(f"{folio:8} ({family:6}): {n_tokens:4} tok, {n_middles:3} mid | "
          f"TTR={ttr:.2f} | excl={len(exclusive):2} ({exclusivity_ratio:.2f}) | "
          f"univ={len(universal):2} ({universality_ratio:.2f})")

# Family comparison
print("\n" + "="*60)
print("FAMILY COMPARISON")
print("="*60)

zodiac_stats = [v for k, v in results['folio_stats'].items() if v['family'] == 'Zodiac']
ac_stats = [v for k, v in results['folio_stats'].items() if v['family'] == 'A/C']

print(f"\nZodiac family ({len(zodiac_stats)} folios):")
print(f"  Mean tokens:          {np.mean([s['tokens'] for s in zodiac_stats]):.1f}")
print(f"  Mean MIDDLEs:         {np.mean([s['middles'] for s in zodiac_stats]):.1f}")
print(f"  Mean TTR:             {np.mean([s['ttr'] for s in zodiac_stats]):.3f}")
print(f"  Mean exclusivity:     {np.mean([s['exclusivity_ratio'] for s in zodiac_stats]):.3f}")
print(f"  Mean universality:    {np.mean([s['universality_ratio'] for s in zodiac_stats]):.3f}")

print(f"\nA/C family ({len(ac_stats)} folios):")
print(f"  Mean tokens:          {np.mean([s['tokens'] for s in ac_stats]):.1f}")
print(f"  Mean MIDDLEs:         {np.mean([s['middles'] for s in ac_stats]):.1f}")
print(f"  Mean TTR:             {np.mean([s['ttr'] for s in ac_stats]):.3f}")
print(f"  Mean exclusivity:     {np.mean([s['exclusivity_ratio'] for s in ac_stats]):.3f}")
print(f"  Mean universality:    {np.mean([s['universality_ratio'] for s in ac_stats]):.3f}")

# Statistical tests
from scipy import stats

zodiac_excl = [s['exclusivity_ratio'] for s in zodiac_stats]
ac_excl = [s['exclusivity_ratio'] for s in ac_stats]

t_stat, p_val = stats.ttest_ind(zodiac_excl, ac_excl)
print(f"\nExclusivity t-test: t={t_stat:.3f}, p={p_val:.4f}")

# Classification: specialist vs generalist
print("\n" + "="*60)
print("SPECIALIST vs GENERALIST CLASSIFICATION")
print("="*60)

# Specialists: above-median exclusivity
# Generalists: below-median exclusivity
all_excl = [v['exclusivity_ratio'] for v in results['folio_stats'].values()]
median_excl = np.median(all_excl)

specialists = [(k, v) for k, v in results['folio_stats'].items() if v['exclusivity_ratio'] >= median_excl]
generalists = [(k, v) for k, v in results['folio_stats'].items() if v['exclusivity_ratio'] < median_excl]

print(f"\nSpecialists (exclusivity >= {median_excl:.3f}): {len(specialists)}")
for folio, fstats in sorted(specialists, key=lambda x: x[1]['exclusivity_ratio'], reverse=True)[:10]:
    print(f"  {folio:8} ({fstats['family']:6}): excl={fstats['exclusivity_ratio']:.3f}, univ={fstats['universality_ratio']:.3f}")

print(f"\nGeneralists (exclusivity < {median_excl:.3f}): {len(generalists)}")
for folio, fstats in sorted(generalists, key=lambda x: x[1]['universality_ratio'], reverse=True)[:10]:
    print(f"  {folio:8} ({fstats['family']:6}): excl={fstats['exclusivity_ratio']:.3f}, univ={fstats['universality_ratio']:.3f}")

# Check if specialists cluster by family
specialist_zodiac = sum(1 for f, s in specialists if s['family'] == 'Zodiac')
generalist_zodiac = sum(1 for f, s in generalists if s['family'] == 'Zodiac')
zodiac_total = len(zodiac_stats)

specialist_ac = sum(1 for f, s in specialists if s['family'] == 'A/C')
generalist_ac = sum(1 for f, s in generalists if s['family'] == 'A/C')
ac_total = len(ac_stats)

print(f"\nSpecialist distribution:")
print(f"  Zodiac: {specialist_zodiac}/{zodiac_total} ({100*specialist_zodiac/zodiac_total:.1f}%)")
print(f"  A/C:    {specialist_ac}/{ac_total} ({100*specialist_ac/ac_total:.1f}%)")

# Chi-squared test for family x specialization
contingency = [[specialist_zodiac, generalist_zodiac], [specialist_ac, generalist_ac]]
chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
print(f"  Chi-squared: {chi2:.2f}, p={chi_p:.4f}")

# Summary
results['summary'] = {
    'total_azc_middles': len(all_middles),
    'exclusive_middles': len(exclusive_middles),
    'shared_middles': len(shared_middles),
    'universal_middles': len(universal_middles),
    'median_exclusivity': float(median_excl),
    'n_specialists': len(specialists),
    'n_generalists': len(generalists),
    'exclusivity_ttest_p': float(p_val),
    'family_specialist_chi2_p': float(chi_p),
    'zodiac_mean_exclusivity': float(np.mean(zodiac_excl)),
    'ac_mean_exclusivity': float(np.mean(ac_excl)),
}

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if chi_p < 0.01:
    verdict = "FAMILY_SPECIALIZED"
    print("Specialist/generalist pattern differs by family")
elif p_val < 0.05:
    verdict = "MODERATE_DIFFERENTIATION"
    print(f"Families show moderate exclusivity difference (p={p_val:.4f})")
else:
    verdict = "NO_CLEAR_SPECIALIZATION"
    print("No clear specialist/generalist pattern by family")

results['verdict'] = verdict

out_path = Path(__file__).parent.parent / 'results' / 't3_azc_specialization.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")

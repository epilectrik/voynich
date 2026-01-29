"""Recalculate PHARMA profile using only P-placement (text) tokens."""
import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

# Load class map for HT calculation
class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    raw_map = json.load(f)
class_map = raw_map.get('token_to_class', raw_map)

tx = Transcript()

def get_section(folio):
    num = int(''.join(c for c in folio if c.isdigit()))
    if 74 <= num <= 84:
        return 'BIO'
    elif 26 <= num <= 56:
        return 'HERBAL_B'
    elif 57 <= num <= 67:
        return 'PHARMA'
    elif num >= 103:
        return 'RECIPE_B'
    else:
        return 'OTHER'

print("=== PHARMA TEXT-ONLY ANALYSIS ===\n")

# Get all Currier B tokens
all_b = list(tx.currier_b())

# Separate by placement type
text_tokens = [t for t in all_b if t.placement.startswith('P')]
diagram_tokens = [t for t in all_b if t.placement.startswith('R') or t.placement.startswith('C')]
other_tokens = [t for t in all_b if not t.placement.startswith('P') and not t.placement.startswith('R') and not t.placement.startswith('C')]

print(f"Total Currier B tokens: {len(all_b)}")
print(f"  P-placement (text): {len(text_tokens)} ({len(text_tokens)/len(all_b):.1%})")
print(f"  R/C-placement (diagram): {len(diagram_tokens)} ({len(diagram_tokens)/len(all_b):.1%})")
print(f"  Other placement: {len(other_tokens)} ({len(other_tokens)/len(all_b):.1%})")

print("\n--- SECTION PROFILES (TEXT ONLY) ---\n")

# Calculate section profiles using TEXT ONLY
section_stats = {}
for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
    section_text = [t for t in text_tokens if get_section(t.folio) == section]
    if not section_text:
        continue

    # Count HT
    ht_count = sum(1 for t in section_text if t.word not in class_map and '*' not in t.word)
    valid_count = sum(1 for t in section_text if '*' not in t.word and t.word.strip())
    ht_rate = ht_count / valid_count if valid_count > 0 else 0

    # Unique folios
    folios = set(t.folio for t in section_text)

    section_stats[section] = {
        'tokens': valid_count,
        'ht_count': ht_count,
        'ht_rate': ht_rate,
        'folios': sorted(folios)
    }

print(f"{'Section':<12} {'Tokens':>10} {'HT':>10} {'HT Rate':>10} {'Folios':>8}")
print("-" * 52)
for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
    if section in section_stats:
        s = section_stats[section]
        print(f"{section:<12} {s['tokens']:>10} {s['ht_count']:>10} {s['ht_rate']:>10.1%} {len(s['folios']):>8}")

print("\n--- PHARMA DETAIL ---\n")

# PHARMA detail by folio
for folio in ['f57r', 'f66r', 'f66v']:
    folio_all = [t for t in all_b if t.folio == folio]
    folio_text = [t for t in text_tokens if t.folio == folio]

    all_valid = [t for t in folio_all if '*' not in t.word and t.word.strip()]
    text_valid = [t for t in folio_text if '*' not in t.word and t.word.strip()]

    if all_valid:
        all_ht = sum(1 for t in all_valid if t.word not in class_map) / len(all_valid)
    else:
        all_ht = 0

    if text_valid:
        text_ht = sum(1 for t in text_valid if t.word not in class_map) / len(text_valid)
    else:
        text_ht = 0

    placements = Counter(t.placement for t in folio_all)

    print(f"{folio}:")
    print(f"  All tokens: {len(folio_all)} (HT: {all_ht:.1%})")
    print(f"  Text only: {len(folio_text)} (HT: {text_ht:.1%})")
    print(f"  Placements: {dict(placements)}")
    print()

print("=== REVISED INTERPRETATION ===\n")

print("ORIGINAL ANALYSIS (included f66r diagram):")
print("  PHARMA HT rate: ~40%")
print("  Driven by f66r's 28 single-char margin labels")
print()

if 'PHARMA' in section_stats:
    pharma_text_ht = section_stats['PHARMA']['ht_rate']
    bio_text_ht = section_stats.get('BIO', {}).get('ht_rate', 0)
    print(f"CORRECTED ANALYSIS (text only):")
    print(f"  PHARMA HT rate: {pharma_text_ht:.1%}")
    print(f"  BIO HT rate: {bio_text_ht:.1%}")
    print(f"  Ratio: {pharma_text_ht/bio_text_ht:.2f}x" if bio_text_ht > 0 else "  Ratio: N/A")
    print()

    if pharma_text_ht > bio_text_ht * 1.2:
        print("VERDICT: PHARMA still elevated, but much less dramatic")
        print("  The 'PHARMA anomaly' was largely a PLACEMENT TYPE artifact")
    else:
        print("VERDICT: PHARMA is comparable to BIO when diagram excluded")
        print("  The 'PHARMA anomaly' was entirely a PLACEMENT TYPE artifact")

# Save results
results_dir = Path(__file__).parent.parent / 'results'
output = {
    'finding': 'f66r_is_diagram',
    'section_profiles_text_only': section_stats,
    'f66r_placement': {
        'R': 295,
        'M': 31,
        'W': 3,
        'P': 0
    },
    'pharma_text_folios': ['f57r', 'f66v'],
    'pharma_diagram_folios': ['f66r']
}

with open(results_dir / 'pharma_text_only.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nSaved to pharma_text_only.json")

"""Recalculate f66r profile properly - R is text, L/M are labels."""
import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    raw_map = json.load(f)
class_map = raw_map.get('token_to_class', raw_map)

tx = Transcript()
all_tokens = list(tx.all(h_only=True))

print("=== F66R PROPER ANALYSIS ===\n")

# Define what's "text" vs "labels"
def is_text(placement):
    """P = paragraph, R = ring - both are legitimate text."""
    return placement.startswith('P') or placement.startswith('R')

def is_label(placement):
    """L = label, M = margin - exclude from text analysis."""
    return placement.startswith('L') or placement.startswith('M')

# Analyze f66r
f66r = [t for t in all_tokens if t.folio == 'f66r']
f66r_text = [t for t in f66r if is_text(t.placement)]
f66r_labels = [t for t in f66r if is_label(t.placement)]

print(f"f66r total: {len(f66r)} tokens")
print(f"f66r text (P+R): {len(f66r_text)} tokens")
print(f"f66r labels (L+M): {len(f66r_labels)} tokens")

# HT rate for text only
text_valid = [t for t in f66r_text if '*' not in t.word and t.word.strip()]
ht_count = sum(1 for t in text_valid if t.word not in class_map)
print(f"\nf66r TEXT HT rate: {ht_count}/{len(text_valid)} = {ht_count/len(text_valid):.1%}")

# Show some R-placement tokens (the actual text)
print("\nSample R-placement (text) tokens:")
for t in f66r_text[:15]:
    is_ht = "HT" if t.word not in class_map else "PP"
    print(f"  {t.word:15} ({is_ht})")

# Now compare to other sections properly (P+R as text)
print("\n=== SECTION COMPARISON (P+R as text) ===\n")

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

# Currier B text tokens only
b_text = [t for t in all_tokens if t.language == 'B' and is_text(t.placement)]

section_stats = {}
for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
    section_tokens = [t for t in b_text if get_section(t.folio) == section]
    valid = [t for t in section_tokens if '*' not in t.word and t.word.strip()]

    if not valid:
        continue

    ht = sum(1 for t in valid if t.word not in class_map)
    section_stats[section] = {
        'tokens': len(valid),
        'ht': ht,
        'ht_rate': ht / len(valid)
    }

print(f"{'Section':<12} {'Tokens':>10} {'HT':>10} {'HT Rate':>10}")
print("-" * 44)
for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
    if section in section_stats:
        s = section_stats[section]
        print(f"{section:<12} {s['tokens']:>10} {s['ht']:>10} {s['ht_rate']:>10.1%}")

# PHARMA detail
print("\n=== PHARMA DETAIL ===\n")
for folio in ['f57r', 'f66r', 'f66v']:
    folio_all = [t for t in all_tokens if t.folio == folio and t.language == 'B']
    folio_text = [t for t in folio_all if is_text(t.placement)]
    folio_labels = [t for t in folio_all if is_label(t.placement)]

    valid = [t for t in folio_text if '*' not in t.word and t.word.strip()]
    ht = sum(1 for t in valid if t.word not in class_map) if valid else 0

    print(f"{folio}:")
    print(f"  Total: {len(folio_all)}, Text: {len(folio_text)}, Labels: {len(folio_labels)}")
    print(f"  Text HT rate: {ht/len(valid):.1%}" if valid else "  Text HT rate: N/A")
    print()

print("=== VERDICT ===\n")
print("R-placement IS operational text (just ring layout), not diagram labels.")
print("L/M-placement are margin labels - should exclude.")
print()
if 'PHARMA' in section_stats and 'BIO' in section_stats:
    ratio = section_stats['PHARMA']['ht_rate'] / section_stats['BIO']['ht_rate']
    print(f"PHARMA HT rate: {section_stats['PHARMA']['ht_rate']:.1%}")
    print(f"BIO HT rate: {section_stats['BIO']['ht_rate']:.1%}")
    print(f"Ratio: {ratio:.2f}x")
    print()
    if ratio > 1.5:
        print("PHARMA is genuinely HT-elevated (not an artifact)")
    else:
        print("PHARMA HT elevation is modest")

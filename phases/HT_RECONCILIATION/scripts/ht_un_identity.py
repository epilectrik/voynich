"""
HT_RECONCILIATION - Script 1: HT/UN Population Identity Confirmation
T1: Are HT tokens (excluded from 479-type grammar) the same as UN tokens (C610)?

GATE: If T1 FAIL, subsequent scripts should not run.
"""
import json, sys
import numpy as np
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# --- Load classified set (479 types, 49 classes) ---
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# --- Build HT population from B tokens ---
ht_type_counts = Counter()
classified_type_counts = Counter()
total_b = 0

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    total_b += 1
    if w in classified_tokens:
        classified_type_counts[w] += 1
    else:
        ht_type_counts[w] += 1

ht_types = set(ht_type_counts.keys())
ht_occ = sum(ht_type_counts.values())

# --- Load UN census ---
un_census_path = PROJECT_ROOT / 'phases' / 'UN_COMPOSITIONAL_MECHANICS' / 'results' / 'un_census.json'
with open(un_census_path, 'r', encoding='utf-8') as f:
    un_census = json.load(f)

un_n_types = un_census['inventory']['un_types']
un_n_occ = un_census['inventory']['un_tokens']

# UN census has a type list if available; otherwise we compare counts
# Check if un_census has an explicit type list
un_type_list = un_census.get('inventory', {}).get('un_type_list', None)

# Also check if there's a separate file with the actual UN type set
un_type_set = None
un_types_file = PROJECT_ROOT / 'phases' / 'UN_COMPOSITIONAL_MECHANICS' / 'results' / 'un_type_list.json'
if un_types_file.exists():
    with open(un_types_file, 'r', encoding='utf-8') as f:
        un_type_set = set(json.load(f))

# If we can't get the explicit list, we compare counts and note methodology
if un_type_list is not None:
    un_type_set = set(un_type_list)

# --- T1: Identity Comparison ---
print("=== T1: HT/UN Population Identity ===")
print()
print(f"HT population (from classified exclusion):")
print(f"  Types: {len(ht_types)}")
print(f"  Occurrences: {ht_occ}")
print(f"  Hapax: {sum(1 for t in ht_types if ht_type_counts[t] == 1)}")
print()
print(f"UN population (from un_census.json):")
print(f"  Types: {un_n_types}")
print(f"  Occurrences: {un_n_occ}")
print()

# Count-based comparison
type_match_pct = min(len(ht_types), un_n_types) / max(len(ht_types), un_n_types) * 100
occ_match_pct = min(ht_occ, un_n_occ) / max(ht_occ, un_n_occ) * 100

print(f"Count comparison:")
print(f"  Type count match: {type_match_pct:.2f}%")
print(f"  Occurrence count match: {occ_match_pct:.2f}%")
print(f"  Type delta: {abs(len(ht_types) - un_n_types)}")
print(f"  Occurrence delta: {abs(ht_occ - un_n_occ)}")

# Set-based comparison if we have the UN type list
jaccard = None
overlap = None
ht_only = None
un_only = None
if un_type_set is not None:
    overlap = ht_types & un_type_set
    ht_only = ht_types - un_type_set
    un_only_set = un_type_set - ht_types
    union = ht_types | un_type_set
    jaccard = len(overlap) / len(union) if union else 0.0
    print()
    print(f"Set comparison:")
    print(f"  Overlap: {len(overlap)} types")
    print(f"  HT-only: {len(ht_only)} types")
    print(f"  UN-only: {len(un_only_set)} types")
    print(f"  Jaccard: {jaccard:.6f}")
    if ht_only:
        ht_only_sorted = sorted(ht_only, key=lambda t: -ht_type_counts[t])[:10]
        print(f"  Top HT-only: {', '.join(f'{t}({ht_type_counts[t]})' for t in ht_only_sorted)}")
    if un_only_set:
        print(f"  Sample UN-only: {list(un_only_set)[:10]}")

# --- Verdict ---
# Both populations are defined by exclusion from the same 479-type set
# The only possible difference is in filtering (empty words, asterisk tokens)
if type_match_pct >= 99.0 and occ_match_pct >= 99.0:
    verdict = "PASS"
    detail = "Populations match within 1% on both types and occurrences"
elif type_match_pct >= 95.0 and occ_match_pct >= 95.0:
    verdict = "PASS_WITH_NOTE"
    detail = "Populations match within 5% - minor filtering differences"
else:
    verdict = "FAIL"
    detail = "Populations diverge significantly"

if jaccard is not None:
    if jaccard >= 0.99:
        verdict = "PASS"
        detail = f"Jaccard={jaccard:.6f}, near-perfect overlap"
    elif jaccard >= 0.95:
        verdict = "PASS_WITH_NOTE"
        detail = f"Jaccard={jaccard:.6f}, minor differences"

print()
print(f"T1 VERDICT: {verdict}")
print(f"  {detail}")

# --- Additional: HT morphological summary ---
print()
print("=== HT Morphological Summary ===")
prefix_counts = Counter()
has_articulator = 0
for w in ht_types:
    m = morph.extract(w)
    if m.prefix:
        prefix_counts[m.prefix] += 1
    if m.has_articulator:
        has_articulator += 1

print(f"  Types with articulator: {has_articulator} ({has_articulator/len(ht_types)*100:.1f}%)")
print(f"  Distinct prefixes: {len(prefix_counts)}")
top_pfx = prefix_counts.most_common(10)
for pfx, cnt in top_pfx:
    print(f"    {pfx}: {cnt} types")

# --- Save results ---
results = {
    "metadata": {
        "phase": "HT_RECONCILIATION",
        "script": "ht_un_identity.py",
        "test": "T1",
        "classified_types": len(classified_tokens),
        "total_b_tokens": total_b
    },
    "T1_identity": {
        "ht_types": len(ht_types),
        "ht_occurrences": ht_occ,
        "ht_hapax": sum(1 for t in ht_types if ht_type_counts[t] == 1),
        "un_types": un_n_types,
        "un_occurrences": un_n_occ,
        "type_match_pct": round(type_match_pct, 4),
        "occ_match_pct": round(occ_match_pct, 4),
        "jaccard": round(jaccard, 6) if jaccard is not None else None,
        "overlap_types": len(overlap) if overlap is not None else None,
        "ht_only_types": len(ht_only) if ht_only is not None else None,
        "un_only_types": len(un_only_set) if un_type_set is not None else None,
        "verdict": verdict,
        "detail": detail
    },
    "morphological_summary": {
        "types_with_articulator": has_articulator,
        "distinct_prefixes": len(prefix_counts),
        "top_prefixes": {pfx: cnt for pfx, cnt in top_pfx}
    }
}

out_path = PROJECT_ROOT / 'phases' / 'HT_RECONCILIATION' / 'results' / 'ht_un_identity.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print()
print(f"Results saved to {out_path}")

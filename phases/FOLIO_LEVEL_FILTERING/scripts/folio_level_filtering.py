"""
FOLIO_LEVEL_FILTERING Phase - Script 1: Folio-Level PP Pooling & B Filtering
Tests T3.1-T3.6 (C704-C709)

Hypothesis: The functional filtering unit for B vocabulary is the entire
A folio, not individual records or RI-bounded bundles. PP MIDDLEs distribute
homogeneously within A folios (C703), so pooling across all lines in a folio
yields the complete PP vocabulary specification.

Gate: T3.2 >= 25 classes AND T3.3 < 30% empty AND T3.5 < 0.6 Jaccard

Tests:
  T3.1: Folio PP Pool Size (C704)
  T3.2: Folio-Level Class Survival (C705)
  T3.3: B Line Viability Under Folio Filtering (C706)
  T3.4: Folio Usability Dynamic Range (C707)
  T3.5: Inter-Folio PP Discrimination (C708)
  T3.6: Section Invariance Check (C709)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy import stats as scipy_stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

# ── Role taxonomy (C560/C581: class 17 = CC) ──
CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']

print("=" * 70)
print("FOLIO_LEVEL_FILTERING - Folio-Level PP Pooling & B Filtering")
print("=" * 70)

# ── Load data ──
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# Load class map
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    cmap = json.load(f)
token_to_class = cmap['token_to_class']

# Load forbidden transitions
with open(PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json') as f:
    forbidden_data = json.load(f)
FORBIDDEN_PAIRS = [(t['source'], t['target']) for t in forbidden_data['transitions']]

# Load REGIME mapping
with open(PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json') as f:
    regime_map = json.load(f)

# ── Step 1: Build B token inventory ──
print("\nStep 1: Building B token inventory...")

b_tokens = {}       # token_str -> (prefix, middle, suffix)
b_by_middle = defaultdict(set)
b_by_prefix = defaultdict(set)
b_by_suffix = defaultdict(set)

for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)
        b_by_middle[m.middle].add(w)
        if m.prefix:
            b_by_prefix[m.prefix].add(w)
        if m.suffix:
            b_by_suffix[m.suffix].add(w)

b_middles_set = set(b_by_middle.keys())
b_prefixes_set = set(b_by_prefix.keys())
b_suffixes_set = set(b_by_suffix.keys())
b_token_class = {tok: int(cls) for tok, cls in token_to_class.items() if tok in b_tokens}

print(f"  B token types: {len(b_tokens)}")
print(f"  B unique MIDDLEs: {len(b_middles_set)}")

# ── Step 2: Build per-folio PP pools from A ──
print("\nStep 2: Building folio-level PP pools...")

folio_pp_middles = defaultdict(set)    # folio -> set of PP MIDDLEs
folio_pp_prefixes = defaultdict(set)   # folio -> set of PP PREFIXes
folio_pp_suffixes = defaultdict(set)   # folio -> set of PP SUFFIXes
folio_sections = {}                     # folio -> section
folio_n_lines = defaultdict(int)

# Also collect per-record PP counts for comparison
record_pp_counts = []

for fol in analyzer.get_folios():
    records = analyzer.analyze_folio(fol)
    folio_n_lines[fol] = len(records)

    for rec in records:
        rec_pp_middles = set()
        for t in rec.tokens:
            if t.is_pp:
                if t.middle:
                    folio_pp_middles[fol].add(t.middle)
                    rec_pp_middles.add(t.middle)
                if t.prefix:
                    folio_pp_prefixes[fol].add(t.prefix)
                if t.suffix:
                    folio_pp_suffixes[fol].add(t.suffix)
        record_pp_counts.append(len(rec_pp_middles))

# Get section info per folio
for token in tx.currier_a():
    if token.folio not in folio_sections:
        folio_sections[token.folio] = token.section

a_folios = sorted(folio_pp_middles.keys())
print(f"  A folios: {len(a_folios)}")

# ── Step 3: Apply C502.a filtering at folio level ──
print("\nStep 3: Applying C502.a full morphological filtering per folio...")

folio_legal_tokens = {}    # folio -> set of legal B tokens
folio_legal_classes = {}   # folio -> set of legal B class IDs

for fol in a_folios:
    pp_mids = folio_pp_middles[fol] & b_middles_set
    pp_prefs = folio_pp_prefixes[fol] & b_prefixes_set
    pp_sufs = folio_pp_suffixes[fol] & b_suffixes_set

    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in pp_mids:
            pref_ok = (pref is None or pref in pp_prefs)
            suf_ok = (suf is None or suf in pp_sufs)
            if pref_ok and suf_ok:
                legal.add(tok)

    folio_legal_tokens[fol] = legal
    folio_legal_classes[fol] = {b_token_class[t] for t in legal if t in b_token_class}

print(f"  Filtering complete for {len(folio_legal_tokens)} folios")

# ── Build B folio line inventories for viability tests ──
print("\nStep 4: Building B folio line inventories...")

b_folio_lines = defaultdict(lambda: defaultdict(list))  # b_folio -> line -> [tokens]
for token in tx.currier_b():
    b_folio_lines[token.folio][token.line].append(token.word)

# Select representative B folios (one per REGIME + largest)
b_folios_by_size = sorted(b_folio_lines.keys(), key=lambda f: len(b_folio_lines[f]), reverse=True)
largest_b = b_folios_by_size[0] if b_folios_by_size else None

regime_reps = {}
for regime, fols in regime_map.items():
    # Pick first available
    for f in fols:
        if f in b_folio_lines:
            regime_reps[regime] = f
            break

representative_b = list(set([largest_b] + list(regime_reps.values())))
representative_b = [f for f in representative_b if f]
print(f"  Representative B folios: {representative_b}")

results = {
    'metadata': {
        'phase': 'FOLIO_LEVEL_FILTERING',
        'script': 'folio_level_filtering.py',
        'tests': 'T3.1-T3.6 (C704-C709)',
        'n_a_folios': len(a_folios),
        'n_b_token_types': len(b_tokens),
        'representative_b_folios': representative_b,
    },
}

pass_count = 0


# ════════════════════════════════════════════════════════════════
# T3.1: Folio PP Pool Size (C704)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.1: FOLIO PP POOL SIZE (C704)")
print("=" * 70)

folio_pp_sizes = [len(folio_pp_middles[fol]) for fol in a_folios]
pp_arr = np.array(folio_pp_sizes)

rec_pp_arr = np.array(record_pp_counts)

print(f"\n  Folio-level PP MIDDLEs:")
print(f"    Mean: {np.mean(pp_arr):.1f}")
print(f"    Median: {np.median(pp_arr):.1f}")
print(f"    Min: {np.min(pp_arr)}, Max: {np.max(pp_arr)}")
print(f"    Std: {np.std(pp_arr):.1f}")
pcts = np.percentile(pp_arr, [5, 25, 50, 75, 95])
print(f"    Percentiles [5,25,50,75,95]: {[round(p, 1) for p in pcts]}")
print(f"\n  Record-level PP MIDDLEs (for comparison):")
print(f"    Mean: {np.mean(rec_pp_arr):.1f}")
print(f"    Median: {np.median(rec_pp_arr):.1f}")
print(f"\n  Expansion factor: {np.mean(pp_arr) / np.mean(rec_pp_arr):.1f}x")

t31_pass = float(np.mean(pp_arr)) >= 20

print(f"\n  PASS (mean >= 20): {t31_pass}")

if t31_pass:
    pass_count += 1

results['T3_1_folio_pp_pool'] = {
    'constraint': 'C704',
    'folio_mean': round(float(np.mean(pp_arr)), 2),
    'folio_median': round(float(np.median(pp_arr)), 2),
    'folio_min': int(np.min(pp_arr)),
    'folio_max': int(np.max(pp_arr)),
    'folio_std': round(float(np.std(pp_arr)), 2),
    'folio_percentiles': {
        'p5': round(float(pcts[0]), 1),
        'p25': round(float(pcts[1]), 1),
        'p50': round(float(pcts[2]), 1),
        'p75': round(float(pcts[3]), 1),
        'p95': round(float(pcts[4]), 1),
    },
    'record_mean': round(float(np.mean(rec_pp_arr)), 2),
    'expansion_factor': round(float(np.mean(pp_arr)) / float(np.mean(rec_pp_arr)), 2),
    'pass': t31_pass,
}


# ════════════════════════════════════════════════════════════════
# T3.2: Folio-Level Class Survival (C705)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.2: FOLIO-LEVEL CLASS SURVIVAL (C705)")
print("=" * 70)

folio_class_counts = [len(folio_legal_classes[fol]) for fol in a_folios]
cls_arr = np.array(folio_class_counts)

print(f"\n  Folio-level class survival:")
print(f"    Mean: {np.mean(cls_arr):.1f} / 49")
print(f"    Median: {np.median(cls_arr):.1f}")
print(f"    Min: {np.min(cls_arr)}, Max: {np.max(cls_arr)}")
print(f"    Std: {np.std(cls_arr):.1f}")
cls_pcts = np.percentile(cls_arr, [5, 25, 50, 75, 95])
print(f"    Percentiles [5,25,50,75,95]: {[round(p, 1) for p in cls_pcts]}")
print(f"\n  Record-level reference: 11.08 / 49 (C682)")
print(f"  Improvement: {np.mean(cls_arr) / 11.08:.1f}x")

# Role breakdown
print(f"\n  Role survival at folio level:")
for role in ROLES:
    role_classes = set(c for c, r in CLASS_TO_ROLE.items() if r == role)
    n_base = len(role_classes)
    role_survivals = [len(folio_legal_classes[fol] & role_classes) for fol in a_folios]
    r_arr = np.array(role_survivals)
    depl = sum(1 for x in r_arr if x == 0)
    print(f"    {role}: mean={np.mean(r_arr):.1f}/{n_base}, depletion={100*depl/len(r_arr):.1f}%")

t32_pass = float(np.mean(cls_arr)) >= 25

print(f"\n  PASS (mean >= 25/49): {t32_pass}")

if t32_pass:
    pass_count += 1

results['T3_2_class_survival'] = {
    'constraint': 'C705',
    'folio_mean': round(float(np.mean(cls_arr)), 2),
    'folio_median': round(float(np.median(cls_arr)), 2),
    'folio_min': int(np.min(cls_arr)),
    'folio_max': int(np.max(cls_arr)),
    'folio_std': round(float(np.std(cls_arr)), 2),
    'folio_percentiles': {
        'p5': round(float(cls_pcts[0]), 1),
        'p25': round(float(cls_pcts[1]), 1),
        'p50': round(float(cls_pcts[2]), 1),
        'p75': round(float(cls_pcts[3]), 1),
        'p95': round(float(cls_pcts[4]), 1),
    },
    'record_level_reference': 11.08,
    'improvement_factor': round(float(np.mean(cls_arr)) / 11.08, 2),
    'pass': t32_pass,
}


# ════════════════════════════════════════════════════════════════
# T3.3: B Line Viability Under Folio Filtering (C706)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.3: B LINE VIABILITY UNDER FOLIO FILTERING (C706)")
print("=" * 70)

# For each (A-folio, B-folio) pair, compute fraction of B lines with >= 1 legal token
pairing_empty_rates = []
pairing_details = []

for a_fol in a_folios:
    legal = folio_legal_tokens[a_fol]
    for b_fol in representative_b:
        b_lines = b_folio_lines[b_fol]
        n_lines = len(b_lines)
        n_empty = 0
        for line, tokens in b_lines.items():
            if not any(t in legal for t in tokens):
                n_empty += 1
        empty_rate = n_empty / n_lines if n_lines > 0 else 1.0
        pairing_empty_rates.append(empty_rate)
        pairing_details.append({
            'a_folio': a_fol,
            'b_folio': b_fol,
            'empty_rate': empty_rate,
            'n_lines': n_lines,
            'n_empty': n_empty,
        })

empty_arr = np.array(pairing_empty_rates)
mean_empty = float(np.mean(empty_arr))

print(f"\n  Total pairings: {len(empty_arr)}")
print(f"  Mean empty-line rate: {mean_empty:.4f} ({100*mean_empty:.1f}%)")
print(f"  Median: {np.median(empty_arr):.4f}")
print(f"  Min: {np.min(empty_arr):.4f}, Max: {np.max(empty_arr):.4f}")
print(f"  Record-level reference: ~78% (C690)")
print(f"\n  Distribution of empty rates:")
for threshold in [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0]:
    n_below = int(np.sum(empty_arr <= threshold))
    print(f"    <= {threshold:.0%}: {n_below} ({100*n_below/len(empty_arr):.1f}%)")

# Per B folio breakdown
print(f"\n  Per B folio mean empty rate:")
for b_fol in representative_b:
    rates = [d['empty_rate'] for d in pairing_details if d['b_folio'] == b_fol]
    print(f"    {b_fol}: {np.mean(rates):.4f} ({100*np.mean(rates):.1f}%)")

t33_pass = mean_empty < 0.30

print(f"\n  PASS (mean < 30% empty): {t33_pass}")

if t33_pass:
    pass_count += 1

results['T3_3_b_line_viability'] = {
    'constraint': 'C706',
    'n_pairings': len(empty_arr),
    'mean_empty_rate': round(mean_empty, 5),
    'median_empty_rate': round(float(np.median(empty_arr)), 5),
    'min_empty_rate': round(float(np.min(empty_arr)), 5),
    'max_empty_rate': round(float(np.max(empty_arr)), 5),
    'record_level_reference': 0.78,
    'pass': t33_pass,
}


# ════════════════════════════════════════════════════════════════
# T3.4: Folio Usability Dynamic Range (C707)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.4: FOLIO USABILITY DYNAMIC RANGE (C707)")
print("=" * 70)

# Composite usability: legality x role_coverage x (1 - empty_rate)
# where legality = fraction of legal B tokens / total B tokens
# role_coverage = fraction of 5 roles with >= 1 surviving class

usabilities = []
for a_fol in a_folios:
    legal = folio_legal_tokens[a_fol]
    classes = folio_legal_classes[a_fol]

    # Legality
    legality = len(legal) / len(b_tokens) if b_tokens else 0

    # Role coverage
    roles_present = 0
    for role in ROLES:
        role_classes = set(c for c, r in CLASS_TO_ROLE.items() if r == role)
        if classes & role_classes:
            roles_present += 1
    role_cov = roles_present / 5

    # Mean empty rate across representative B folios
    empty_rates = []
    for b_fol in representative_b:
        b_lines = b_folio_lines[b_fol]
        n_lines = len(b_lines)
        n_empty = sum(1 for tokens in b_lines.values() if not any(t in legal for t in tokens))
        empty_rates.append(n_empty / n_lines if n_lines > 0 else 1.0)
    mean_empty_fol = np.mean(empty_rates)

    usability = legality * role_cov * (1 - mean_empty_fol)
    usabilities.append({
        'folio': a_fol,
        'legality': legality,
        'role_coverage': role_cov,
        'empty_rate': mean_empty_fol,
        'usability': usability,
        'n_classes': len(classes),
        'n_legal_tokens': len(legal),
    })

usability_values = np.array([u['usability'] for u in usabilities])
best = max(usabilities, key=lambda u: u['usability'])
worst_nonzero = [u for u in usabilities if u['usability'] > 0]
worst = min(worst_nonzero, key=lambda u: u['usability']) if worst_nonzero else best

if worst['usability'] > 0:
    dyn_range = best['usability'] / worst['usability']
else:
    dyn_range = float('inf')

print(f"\n  Usability distribution:")
print(f"    Mean: {np.mean(usability_values):.4f}")
print(f"    Median: {np.median(usability_values):.4f}")
print(f"    Min: {np.min(usability_values):.4f}, Max: {np.max(usability_values):.4f}")
print(f"\n  Best pairing: {best['folio']} (usability={best['usability']:.4f}, "
      f"classes={best['n_classes']}, legality={best['legality']:.4f}, "
      f"role_cov={best['role_coverage']:.2f}, empty={best['empty_rate']:.3f})")
print(f"  Worst nonzero: {worst['folio']} (usability={worst['usability']:.4f})")
print(f"  Dynamic range: {dyn_range:.1f}x")
print(f"\n  Record-level reference: 266x range, best=0.107 (C693)")

# Top/bottom 5
sorted_u = sorted(usabilities, key=lambda u: u['usability'], reverse=True)
print(f"\n  Top 5:")
for u in sorted_u[:5]:
    print(f"    {u['folio']}: usability={u['usability']:.4f}, classes={u['n_classes']}, "
          f"tokens={u['n_legal_tokens']}, empty={u['empty_rate']:.3f}")
print(f"  Bottom 5:")
for u in sorted_u[-5:]:
    print(f"    {u['folio']}: usability={u['usability']:.4f}, classes={u['n_classes']}, "
          f"tokens={u['n_legal_tokens']}, empty={u['empty_rate']:.3f}")

t34_pass = dyn_range < 50 and best['usability'] > 0.3

print(f"\n  PASS (range < 50x AND best > 0.3): {t34_pass}")

if t34_pass:
    pass_count += 1

results['T3_4_usability_range'] = {
    'constraint': 'C707',
    'mean_usability': round(float(np.mean(usability_values)), 5),
    'median_usability': round(float(np.median(usability_values)), 5),
    'best': {
        'folio': best['folio'],
        'usability': round(best['usability'], 5),
        'n_classes': best['n_classes'],
        'legality': round(best['legality'], 5),
    },
    'worst_nonzero': {
        'folio': worst['folio'],
        'usability': round(worst['usability'], 5),
    },
    'dynamic_range': round(dyn_range, 2),
    'record_level_reference': {'range': 266, 'best': 0.107},
    'pass': t34_pass,
}


# ════════════════════════════════════════════════════════════════
# T3.5: Inter-Folio PP Discrimination (C708)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.5: INTER-FOLIO PP DISCRIMINATION (C708)")
print("=" * 70)

# Jaccard similarity between folio-level PP pools
inter_jaccards = []
for i in range(len(a_folios)):
    for j in range(i + 1, len(a_folios)):
        mids_i = folio_pp_middles[a_folios[i]]
        mids_j = folio_pp_middles[a_folios[j]]
        if mids_i and mids_j:
            union = mids_i | mids_j
            inter = mids_i & mids_j
            inter_jaccards.append(len(inter) / len(union))

inter_arr = np.array(inter_jaccards)

print(f"\n  Folio pairs: {len(inter_arr)}")
print(f"  Mean inter-folio Jaccard: {np.mean(inter_arr):.4f}")
print(f"  Median: {np.median(inter_arr):.4f}")
print(f"  Min: {np.min(inter_arr):.4f}, Max: {np.max(inter_arr):.4f}")
print(f"  Std: {np.std(inter_arr):.4f}")
j_pcts = np.percentile(inter_arr, [5, 25, 50, 75, 95])
print(f"  Percentiles [5,25,50,75,95]: {[round(p, 4) for p in j_pcts]}")

# Also: Jaccard of legal B CLASS sets
class_jaccards = []
for i in range(len(a_folios)):
    for j in range(i + 1, len(a_folios)):
        cls_i = folio_legal_classes[a_folios[i]]
        cls_j = folio_legal_classes[a_folios[j]]
        if cls_i and cls_j:
            union = cls_i | cls_j
            inter = cls_i & cls_j
            class_jaccards.append(len(inter) / len(union))

cls_j_arr = np.array(class_jaccards)
print(f"\n  Legal B CLASS Jaccard (for context):")
print(f"    Mean: {np.mean(cls_j_arr):.4f}")
print(f"    Median: {np.median(cls_j_arr):.4f}")

# Reference: C437 AZC folio orthogonality (Jaccard=0.056)
print(f"\n  Reference: C437 AZC folio Jaccard = 0.056")
print(f"  Reference: C689 single-record Jaccard = 0.199")

t35_pass = float(np.mean(inter_arr)) < 0.6

print(f"\n  PASS (mean Jaccard < 0.6): {t35_pass}")

if t35_pass:
    pass_count += 1

results['T3_5_discrimination'] = {
    'constraint': 'C708',
    'n_pairs': len(inter_arr),
    'pp_jaccard_mean': round(float(np.mean(inter_arr)), 5),
    'pp_jaccard_median': round(float(np.median(inter_arr)), 5),
    'pp_jaccard_min': round(float(np.min(inter_arr)), 5),
    'pp_jaccard_max': round(float(np.max(inter_arr)), 5),
    'pp_jaccard_std': round(float(np.std(inter_arr)), 5),
    'class_jaccard_mean': round(float(np.mean(cls_j_arr)), 5),
    'class_jaccard_median': round(float(np.median(cls_j_arr)), 5),
    'references': {
        'c437_azc_jaccard': 0.056,
        'c689_record_jaccard': 0.199,
    },
    'pass': t35_pass,
}


# ════════════════════════════════════════════════════════════════
# T3.6: Section Invariance Check (C709)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T3.6: SECTION INVARIANCE CHECK (C709)")
print("=" * 70)

# Stratify by A section
section_results = defaultdict(list)
for u in usabilities:
    sec = folio_sections.get(u['folio'], 'UNKNOWN')
    section_results[sec].append(u)

print(f"\n  A sections found: {sorted(section_results.keys())}")

section_viable = {}
for sec in sorted(section_results.keys()):
    sec_usabilities = [u['usability'] for u in section_results[sec]]
    sec_classes = [u['n_classes'] for u in section_results[sec]]
    n_viable = sum(1 for u in sec_usabilities if u > 0.01)
    section_viable[sec] = n_viable / len(sec_usabilities) if sec_usabilities else 0

    print(f"\n  Section {sec}: {len(section_results[sec])} folios")
    print(f"    Mean usability: {np.mean(sec_usabilities):.4f}")
    print(f"    Mean classes: {np.mean(sec_classes):.1f}")
    print(f"    Viable (>0.01): {n_viable}/{len(sec_usabilities)} ({100*n_viable/len(sec_usabilities):.1f}%)")

# Check if any section is systematically non-viable (< 10% viable)
dead_sections = [sec for sec, rate in section_viable.items() if rate < 0.10]
t36_pass = len(dead_sections) == 0

print(f"\n  Dead sections (<10% viable): {dead_sections if dead_sections else 'none'}")
print(f"\n  PASS (no dead section pairs): {t36_pass}")

if t36_pass:
    pass_count += 1

results['T3_6_section_invariance'] = {
    'constraint': 'C709',
    'sections': {},
    'dead_sections': dead_sections,
    'pass': t36_pass,
}

for sec in sorted(section_results.keys()):
    sec_u = [u['usability'] for u in section_results[sec]]
    sec_c = [u['n_classes'] for u in section_results[sec]]
    n_viable = sum(1 for u in sec_u if u > 0.01)
    results['T3_6_section_invariance']['sections'][sec] = {
        'n_folios': len(section_results[sec]),
        'mean_usability': round(float(np.mean(sec_u)), 5),
        'mean_classes': round(float(np.mean(sec_c)), 2),
        'viable_rate': round(n_viable / len(sec_u), 4) if sec_u else 0,
    }


# ════════════════════════════════════════════════════════════════
# GATE CHECK
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("GATE CHECK: Folio-Level Filtering")
print("=" * 70)

tests = ['T3.1 (C704)', 'T3.2 (C705)', 'T3.3 (C706)', 'T3.4 (C707)', 'T3.5 (C708)', 'T3.6 (C709)']
passes = [
    results['T3_1_folio_pp_pool']['pass'],
    results['T3_2_class_survival']['pass'],
    results['T3_3_b_line_viability']['pass'],
    results['T3_4_usability_range']['pass'],
    results['T3_5_discrimination']['pass'],
    results['T3_6_section_invariance']['pass'],
]

for test, passed in zip(tests, passes):
    status = "PASS" if passed else "FAIL"
    print(f"  {test}: {status}")

print(f"\n  Total passed: {pass_count}/6")

# Expert gate: T3.2 >= 25 classes AND T3.3 < 30% empty AND T3.5 < 0.6 Jaccard
core_gate = (results['T3_2_class_survival']['pass']
             and results['T3_3_b_line_viability']['pass']
             and results['T3_5_discrimination']['pass'])

print(f"  Core gate (T3.2 + T3.3 + T3.5): {'PASSED' if core_gate else 'FAILED'}")

results['gate'] = {
    'threshold': 'T3.2 >= 25 classes AND T3.3 < 30% empty AND T3.5 < 0.6 Jaccard',
    'passed': pass_count,
    'total': 6,
    'core_gate': 'PASSED' if core_gate else 'FAILED',
    'overall': 'PASSED' if core_gate else 'FAILED',
}

# ── Save ──
out_path = RESULTS_DIR / 'folio_level_filtering.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Saved: {out_path}")
print("\nDone.")

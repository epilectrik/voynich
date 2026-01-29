"""
A_RECORD_B_FILTERING Phase - Script 1: Survivor Population Profile
Tests 1-4 (C682-C685)

Question: What is the full population-level picture of A-record
filtering of the B vocabulary?

Tests:
  T1: Class Survival Distribution (C682)
  T2: Role Composition Under Filtering (C683)
  T3: Hazard Pruning Under Filtering (C684)
  T4: LINK and Kernel Survival Rates (C685)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
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

ROLE_TO_CLASSES = {}
for c, r in CLASS_TO_ROLE.items():
    ROLE_TO_CLASSES.setdefault(r, set()).add(c)

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']
B_ROLE_COUNTS = {r: len(ROLE_TO_CLASSES[r]) for r in ROLES}
ALL_49 = set(range(1, 50))

# ── Load data ──
print("=" * 70)
print("A_RECORD_B_FILTERING - Script 1: Survivor Population Profile")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# Load class map
with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    cmap = json.load(f)
token_to_class = cmap['token_to_class']  # str -> int

# Load forbidden transitions
with open(PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json') as f:
    forbidden_data = json.load(f)
FORBIDDEN_PAIRS = [(t['source'], t['target']) for t in forbidden_data['transitions']]
print(f"Loaded {len(FORBIDDEN_PAIRS)} forbidden transitions")

# ── Step 1: Build B token inventory with morphology ──
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

print(f"  B token types: {len(b_tokens)}")
print(f"  B unique MIDDLEs: {len(b_middles_set)}")
print(f"  B unique PREFIXes: {len(b_prefixes_set)}")
print(f"  B unique SUFFIXes: {len(b_suffixes_set)}")

# ── Step 2: Build A record morphology ──
print("\nStep 2: Building A record morphology profiles...")

a_record_morph = {}  # (folio, line) -> (prefixes, middles, suffixes)
for record in analyzer.iter_records():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in record.tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    a_record_morph[(record.folio, record.line)] = (prefixes, middles, suffixes)

print(f"  A records: {len(a_record_morph)}")

# ── Step 3: Full morphological filtering (C502.a) for every A record ──
print("\nStep 3: Computing legal B tokens per A record...")

# Pre-compute: for each B token, its (prefix, middle, suffix) and class
b_token_class = {}
for tok, cls in token_to_class.items():
    if tok in b_tokens:
        b_token_class[tok] = int(cls)

record_legal_tokens = {}   # (folio, line) -> set of legal B tokens
record_legal_classes = {}  # (folio, line) -> set of legal B classes

for (folio, line), (prefixes, middles, suffixes) in a_record_morph.items():
    pp_middles = middles & b_middles_set
    pp_prefixes = prefixes & b_prefixes_set
    pp_suffixes = suffixes & b_suffixes_set

    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                legal.add(tok)

    record_legal_tokens[(folio, line)] = legal
    record_legal_classes[(folio, line)] = {b_token_class[t] for t in legal if t in b_token_class}

print(f"  Filtering complete for {len(record_legal_tokens)} records")

# ════════════════════════════════════════════════════════════════
# TEST 1: Class Survival Distribution (C682)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 1: CLASS SURVIVAL DISTRIBUTION (C682)")
print("=" * 70)

class_counts = [len(classes) for classes in record_legal_classes.values()]
arr = np.array(class_counts)

t1_mean = float(np.mean(arr))
t1_median = float(np.median(arr))
t1_std = float(np.std(arr))
t1_min = int(np.min(arr))
t1_max = int(np.max(arr))
pcts = np.percentile(arr, [5, 25, 50, 75, 95])
zero_count = int(np.sum(arr == 0))

print(f"\n  Records: {len(arr)}")
print(f"  Mean class survival: {t1_mean:.2f} / 49")
print(f"  Median: {t1_median:.1f}")
print(f"  Std: {t1_std:.2f}")
print(f"  Min: {t1_min}, Max: {t1_max}")
print(f"  Percentiles [5,25,50,75,95]: {pcts}")
print(f"  Records with 0 classes: {zero_count} ({100*zero_count/len(arr):.1f}%)")
print(f"\n  [Sanity check C503.a: expected mean ~6.8, got {t1_mean:.2f}]")

# Token-level survival
token_counts = [len(toks) for toks in record_legal_tokens.values()]
tok_arr = np.array(token_counts)
tok_mean = float(np.mean(tok_arr))
tok_pcts = np.percentile(tok_arr, [5, 25, 50, 75, 95])
print(f"\n  Mean token survival: {tok_mean:.1f} / {len(b_tokens)}")
print(f"  Token percentiles [5,25,50,75,95]: {tok_pcts}")

# ════════════════════════════════════════════════════════════════
# TEST 2: Role Composition Under Filtering (C683)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 2: ROLE COMPOSITION UNDER FILTERING (C683)")
print("=" * 70)

# Per-record: role -> surviving class count
role_survival_all = {r: [] for r in ROLES}
role_depletion = {r: 0 for r in ROLES}

for (folio, line), classes in record_legal_classes.items():
    for role in ROLES:
        role_classes = ROLE_TO_CLASSES[role]
        surviving = len(classes & role_classes)
        role_survival_all[role].append(surviving)
        if surviving == 0:
            role_depletion[role] += 1

n_records = len(record_legal_classes)

print(f"\n  {'Role':<6} {'Baseline':>8} {'Mean Surv':>10} {'Surv %':>8} {'Depletion %':>12}")
print("  " + "-" * 50)
for role in ROLES:
    arr_r = np.array(role_survival_all[role])
    baseline = B_ROLE_COUNTS[role]
    mean_s = float(np.mean(arr_r))
    pct_s = 100 * mean_s / baseline if baseline > 0 else 0
    depl = 100 * role_depletion[role] / n_records
    print(f"  {role:<6} {baseline:>8} {mean_s:>10.2f} {pct_s:>7.1f}% {depl:>11.1f}%")

# Role entropy per record
role_entropies = []
for (folio, line), classes in record_legal_classes.items():
    counts = []
    for role in ROLES:
        counts.append(len(classes & ROLE_TO_CLASSES[role]))
    total = sum(counts)
    if total > 0:
        probs = [c / total for c in counts if c > 0]
        ent = -sum(p * np.log2(p) for p in probs)
    else:
        ent = 0.0
    role_entropies.append(ent)

ent_arr = np.array(role_entropies)
max_ent = np.log2(5)
print(f"\n  Role entropy: mean={np.mean(ent_arr):.3f}, median={np.median(ent_arr):.3f}")
print(f"  Max possible (5 roles): {max_ent:.3f}")
print(f"  Records with 0 entropy: {int(np.sum(ent_arr == 0))} ({100*np.sum(ent_arr==0)/n_records:.1f}%)")

# ════════════════════════════════════════════════════════════════
# TEST 3: Hazard Pruning Under Filtering (C684)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 3: HAZARD PRUNING UNDER FILTERING (C684)")
print("=" * 70)

hazard_counts = []
for (folio, line), legal in record_legal_tokens.items():
    active = 0
    for src, tgt in FORBIDDEN_PAIRS:
        if src in legal and tgt in legal:
            active += 1
    hazard_counts.append(active)

haz_arr = np.array(hazard_counts)
full_elimination = int(np.sum(haz_arr == 0))

print(f"\n  Forbidden transitions (unfiltered): {len(FORBIDDEN_PAIRS)}")
print(f"  Mean active per record: {np.mean(haz_arr):.2f}")
print(f"  Median active: {np.median(haz_arr):.1f}")
print(f"  Max active: {int(np.max(haz_arr))}")
print(f"  Full elimination (0/17): {full_elimination} ({100*full_elimination/n_records:.1f}%)")

# Distribution
haz_dist = Counter(int(h) for h in haz_arr)
print(f"\n  Distribution of active forbidden transitions:")
for k in sorted(haz_dist.keys()):
    pct = 100 * haz_dist[k] / n_records
    bar = '#' * int(pct / 2)
    print(f"    {k:>2}: {haz_dist[k]:>5} ({pct:>5.1f}%) {bar}")

# ════════════════════════════════════════════════════════════════
# TEST 4: LINK and Kernel Survival Rates (C685)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 4: LINK AND KERNEL SURVIVAL RATES (C685)")
print("=" * 70)

# Identify LINK tokens (contain 'ol' per C609)
b_link_tokens = {tok for tok in b_tokens if 'ol' in tok}
print(f"\n  B LINK token types: {len(b_link_tokens)}")

# Kernel characters
KERNEL_CHARS = {'k', 'h', 'e'}

link_densities = []
kernel_access = {'k': 0, 'h': 0, 'e': 0, 'any': 0}

for (folio, line), legal in record_legal_tokens.items():
    # LINK density
    legal_links = legal & b_link_tokens
    if len(legal) > 0:
        link_densities.append(len(legal_links) / len(legal))
    else:
        link_densities.append(0.0)

    # Kernel access: any legal token containing k, h, or e
    has_k = any('k' in tok for tok in legal)
    has_h = any('h' in tok for tok in legal)
    has_e = any('e' in tok for tok in legal)
    if has_k:
        kernel_access['k'] += 1
    if has_h:
        kernel_access['h'] += 1
    if has_e:
        kernel_access['e'] += 1
    if has_k or has_h or has_e:
        kernel_access['any'] += 1

link_arr = np.array(link_densities)
print(f"  LINK density: mean={np.mean(link_arr):.4f}, median={np.median(link_arr):.4f}")
print(f"  Records with 0 LINK tokens: {int(np.sum(link_arr == 0))} ({100*np.sum(link_arr==0)/n_records:.1f}%)")

print(f"\n  Kernel access:")
for kc in ['k', 'h', 'e', 'any']:
    pct = 100 * kernel_access[kc] / n_records
    print(f"    '{kc}': {kernel_access[kc]} ({pct:.1f}%)")
print(f"\n  [Sanity check C503.c: expected 97.6% kernel union, got {100*kernel_access['any']/n_records:.1f}%]")

# ════════════════════════════════════════════════════════════════
# Save results
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

results = {
    'metadata': {
        'phase': 'A_RECORD_B_FILTERING',
        'script': 'survivor_population_profile.py',
        'tests': 'T1-T4 (C682-C685)',
        'n_records': n_records,
        'n_b_token_types': len(b_tokens),
        'n_b_classes': 49,
    },
    'T1_class_survival_distribution': {
        'constraint': 'C682',
        'mean': t1_mean,
        'median': t1_median,
        'std': t1_std,
        'min': t1_min,
        'max': t1_max,
        'percentiles': {
            'p5': float(pcts[0]),
            'p25': float(pcts[1]),
            'p50': float(pcts[2]),
            'p75': float(pcts[3]),
            'p95': float(pcts[4]),
        },
        'zero_class_records': zero_count,
        'zero_class_pct': round(100 * zero_count / n_records, 2),
        'token_level': {
            'mean_legal_tokens': tok_mean,
            'percentiles': {
                'p5': float(tok_pcts[0]),
                'p25': float(tok_pcts[1]),
                'p50': float(tok_pcts[2]),
                'p75': float(tok_pcts[3]),
                'p95': float(tok_pcts[4]),
            },
        },
    },
    'T2_role_composition': {
        'constraint': 'C683',
        'baseline_classes': B_ROLE_COUNTS,
        'role_survival': {},
        'role_depletion_pct': {},
        'role_entropy': {
            'mean': round(float(np.mean(ent_arr)), 4),
            'median': round(float(np.median(ent_arr)), 4),
            'max_possible': round(max_ent, 4),
            'zero_entropy_count': int(np.sum(ent_arr == 0)),
        },
    },
    'T3_hazard_pruning': {
        'constraint': 'C684',
        'total_forbidden': len(FORBIDDEN_PAIRS),
        'mean_active': round(float(np.mean(haz_arr)), 3),
        'median_active': float(np.median(haz_arr)),
        'max_active': int(np.max(haz_arr)),
        'full_elimination_count': full_elimination,
        'full_elimination_pct': round(100 * full_elimination / n_records, 2),
        'distribution': {str(k): haz_dist[k] for k in sorted(haz_dist.keys())},
    },
    'T4_link_kernel_survival': {
        'constraint': 'C685',
        'link_token_types': len(b_link_tokens),
        'link_density_mean': round(float(np.mean(link_arr)), 5),
        'link_density_median': round(float(np.median(link_arr)), 5),
        'zero_link_records': int(np.sum(link_arr == 0)),
        'zero_link_pct': round(100 * float(np.sum(link_arr == 0)) / n_records, 2),
        'kernel_access': {
            'k_pct': round(100 * kernel_access['k'] / n_records, 2),
            'h_pct': round(100 * kernel_access['h'] / n_records, 2),
            'e_pct': round(100 * kernel_access['e'] / n_records, 2),
            'any_pct': round(100 * kernel_access['any'] / n_records, 2),
        },
    },
}

# Fill in per-role stats
for role in ROLES:
    arr_r = np.array(role_survival_all[role])
    baseline = B_ROLE_COUNTS[role]
    results['T2_role_composition']['role_survival'][role] = {
        'mean': round(float(np.mean(arr_r)), 3),
        'median': float(np.median(arr_r)),
        'survival_pct': round(100 * float(np.mean(arr_r)) / baseline, 2) if baseline > 0 else 0,
    }
    results['T2_role_composition']['role_depletion_pct'][role] = round(
        100 * role_depletion[role] / n_records, 2
    )

out_path = RESULTS_DIR / 'survivor_population_profile.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"  Saved: {out_path}")
print("\nDone.")

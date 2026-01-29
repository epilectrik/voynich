"""
RI_FUNCTIONAL_IDENTITY - RI-Gated Class Analysis

Identifies B classes that are ONLY reachable through PP vocabulary
found on RI-bearing lines (not on PP-pure lines within the same folio).

Questions:
  1. Which specific B classes are RI-gated?
  2. What roles do they belong to (CC, EN, FL, FQ, AX)?
  3. Are the RI-exclusive PP MIDDLEs a distinct morphological subgroup?
  4. Is this real or sampling artifact (63% vs 37% line split)?
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

print("=" * 70)
print("RI_FUNCTIONAL_IDENTITY - RI-Gated Class Analysis")
print("=" * 70)

# -- Load data --
tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

folios = analyzer.get_folios()

# -- Load class/role maps --
class_token_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_token_map_path, 'r') as f:
    class_token_map = json.load(f)

token_to_class = {tok: int(cls) for tok, cls in class_token_map['token_to_class'].items()}

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

# -- Build B token inventory --
b_tokens = {}
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set()
b_prefixes_set = set()
b_suffixes_set = set()
for tok, (pref, mid, suf) in b_tokens.items():
    b_middles_set.add(mid)
    if pref:
        b_prefixes_set.add(pref)
    if suf:
        b_suffixes_set.add(suf)

b_token_class = {tok: token_to_class[tok] for tok in b_tokens if tok in token_to_class}

# -- Pre-compute all records --
folio_records = {}
for fol in folios:
    folio_records[fol] = analyzer.analyze_folio(fol)

# -- Filtering function --
def filter_b(pp_middles, pp_prefixes, pp_suffixes):
    shared_mids = pp_middles & b_middles_set
    shared_prefs = pp_prefixes & b_prefixes_set
    shared_sufs = pp_suffixes & b_suffixes_set
    legal = set()
    for tok, (pref, mid, suf) in b_tokens.items():
        if mid in shared_mids:
            if (pref is None or pref in shared_prefs):
                if (suf is None or suf in shared_sufs):
                    legal.add(tok)
    classes = frozenset(b_token_class[t] for t in legal if t in b_token_class)
    return legal, classes

# -- Extract PP vocab from records --
def extract_pp_vocab(records):
    mids = set()
    prefs = set()
    sufs = set()
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mids.add(t.middle)
                if t.prefix:
                    prefs.add(t.prefix)
                if t.suffix:
                    sufs.add(t.suffix)
    return mids, prefs, sufs

# ============================================================
# 1. Identify RI-gated classes per folio
# ============================================================
print()
print("-" * 60)
print("1. RI-Gated B Classes Per Folio")
print("-" * 60)

# Pre-classify lines per folio
folio_pp_pure = {}
folio_ri_bearing = {}
for fol in folios:
    pure = []
    ri = []
    for rec in folio_records[fol]:
        if rec.ri_count > 0:
            ri.append(rec)
        else:
            pure.append(rec)
    folio_pp_pure[fol] = pure
    folio_ri_bearing[fol] = ri

# Per folio: which classes require RI-line PP?
ri_gated_class_counts = Counter()  # class -> how many folios gate it
pp_only_class_counts = Counter()   # class -> how many folios reach it without RI
all_folio_class_counts = Counter() # class -> how many folios reach it at all

ri_gated_per_folio = []

for fol in folios:
    pure_recs = folio_pp_pure[fol]
    all_recs = folio_records[fol]

    # PP-pure only classes
    a_mids, a_prefs, a_sufs = extract_pp_vocab(pure_recs)
    _, a_classes = filter_b(a_mids, a_prefs, a_sufs)

    # Full folio classes
    c_mids, c_prefs, c_sufs = extract_pp_vocab(all_recs)
    _, c_classes = filter_b(c_mids, c_prefs, c_sufs)

    # RI-gated = classes in C but not in A
    ri_gated = c_classes - a_classes
    ri_gated_per_folio.append(len(ri_gated))

    for cls in ri_gated:
        ri_gated_class_counts[cls] += 1
    for cls in a_classes:
        pp_only_class_counts[cls] += 1
    for cls in c_classes:
        all_folio_class_counts[cls] += 1

ri_gated_arr = np.array(ri_gated_per_folio)
print(f"  Mean RI-gated classes per folio: {np.mean(ri_gated_arr):.2f}")
print(f"  Median: {np.median(ri_gated_arr):.0f}")
print(f"  Max: {np.max(ri_gated_arr)}")
print(f"  Folios with 0 RI-gated: {np.sum(ri_gated_arr == 0)}")

# Distribution
print(f"\n  Distribution of RI-gated class count per folio:")
for n in range(int(np.max(ri_gated_arr)) + 1):
    ct = int(np.sum(ri_gated_arr == n))
    if ct > 0:
        print(f"    {n} gated: {ct} folios")

# ============================================================
# 2. Which specific classes are RI-gated? What roles?
# ============================================================
print()
print("-" * 60)
print("2. Specific RI-Gated Classes and Roles")
print("-" * 60)

# All classes that are ever RI-gated
all_ri_gated = set(ri_gated_class_counts.keys())
print(f"  Classes that are RI-gated in at least 1 folio: {len(all_ri_gated)}")

# Sort by frequency
print(f"\n  {'Class':>6} {'Role':>5} {'RI-gated folios':>16} {'PP-only folios':>15} {'Total folios':>13}")
for cls in sorted(all_ri_gated, key=lambda c: ri_gated_class_counts[c], reverse=True):
    role = CLASS_TO_ROLE.get(cls, '??')
    ri_ct = ri_gated_class_counts[cls]
    pp_ct = pp_only_class_counts.get(cls, 0)
    all_ct = all_folio_class_counts.get(cls, 0)
    print(f"  {cls:>6} {role:>5} {ri_ct:>16} {pp_ct:>15} {all_ct:>13}")

# Role breakdown
ri_gated_roles = Counter()
for cls in all_ri_gated:
    role = CLASS_TO_ROLE.get(cls, '??')
    ri_gated_roles[role] += ri_gated_class_counts[cls]

print(f"\n  RI-gated events by role:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    print(f"    {role}: {ri_gated_roles.get(role, 0)} folio-class events")

# Classes that are FREQUENTLY gated (>25% of folios)
freq_gated = {cls for cls, ct in ri_gated_class_counts.items() if ct > len(folios) * 0.25}
print(f"\n  Classes RI-gated in >25% of folios: {sorted(freq_gated)}")
for cls in sorted(freq_gated):
    role = CLASS_TO_ROLE.get(cls, '??')
    ri_ct = ri_gated_class_counts[cls]
    pp_ct = pp_only_class_counts.get(cls, 0)
    print(f"    Class {cls} ({role}): gated in {ri_ct} folios, PP-reachable in {pp_ct}")

# ============================================================
# 3. RI-Exclusive PP MIDDLEs: morphological profile
# ============================================================
print()
print("-" * 60)
print("3. RI-Exclusive PP MIDDLEs: Morphological Profile")
print("-" * 60)

# Global: PP MIDDLEs that appear only on RI-bearing lines (across all folios)
global_pure_pp_mids = set()
global_ri_pp_mids = set()

for fol in folios:
    for rec in folio_pp_pure[fol]:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                global_pure_pp_mids.add(t.middle)
    for rec in folio_ri_bearing[fol]:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                global_ri_pp_mids.add(t.middle)

globally_exclusive_to_ri = global_ri_pp_mids - global_pure_pp_mids
globally_exclusive_to_pure = global_pure_pp_mids - global_ri_pp_mids
globally_shared = global_pure_pp_mids & global_ri_pp_mids

print(f"  Global PP MIDDLE inventory:")
print(f"    Shared:               {len(globally_shared)}")
print(f"    Exclusive to PP-pure: {len(globally_exclusive_to_pure)}")
print(f"    Exclusive to RI-bearing: {len(globally_exclusive_to_ri)}")

# Morphological length distribution
shared_lengths = [len(m) for m in globally_shared]
pure_excl_lengths = [len(m) for m in globally_exclusive_to_pure]
ri_excl_lengths = [len(m) for m in globally_exclusive_to_ri]

print(f"\n  MIDDLE length (characters):")
print(f"    Shared:       mean={np.mean(shared_lengths):.2f}, median={np.median(shared_lengths):.1f}")
if pure_excl_lengths:
    print(f"    Pure-excl:    mean={np.mean(pure_excl_lengths):.2f}, median={np.median(pure_excl_lengths):.1f}")
if ri_excl_lengths:
    print(f"    RI-excl:      mean={np.mean(ri_excl_lengths):.2f}, median={np.median(ri_excl_lengths):.1f}")

# Frequency: how often do these MIDDLEs appear in A text?
mid_freq_a = Counter()
for fol in folios:
    for rec in folio_records[fol]:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mid_freq_a[t.middle] += 1

shared_freqs = [mid_freq_a[m] for m in globally_shared]
pure_excl_freqs = [mid_freq_a[m] for m in globally_exclusive_to_pure]
ri_excl_freqs = [mid_freq_a[m] for m in globally_exclusive_to_ri]

print(f"\n  Frequency in A text (token count):")
print(f"    Shared:       mean={np.mean(shared_freqs):.1f}, median={np.median(shared_freqs):.0f}")
if pure_excl_freqs:
    print(f"    Pure-excl:    mean={np.mean(pure_excl_freqs):.1f}, median={np.median(pure_excl_freqs):.0f}")
if ri_excl_freqs:
    print(f"    RI-excl:      mean={np.mean(ri_excl_freqs):.1f}, median={np.median(ri_excl_freqs):.0f}")

# How many folios use each MIDDLE?
mid_folio_count = defaultdict(set)
for fol in folios:
    for rec in folio_records[fol]:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                mid_folio_count[t.middle].add(fol)

shared_folio_cts = [len(mid_folio_count[m]) for m in globally_shared]
pure_excl_folio_cts = [len(mid_folio_count[m]) for m in globally_exclusive_to_pure]
ri_excl_folio_cts = [len(mid_folio_count[m]) for m in globally_exclusive_to_ri]

print(f"\n  Folio spread (number of folios using each MIDDLE):")
print(f"    Shared:       mean={np.mean(shared_folio_cts):.1f}, median={np.median(shared_folio_cts):.0f}")
if pure_excl_folio_cts:
    print(f"    Pure-excl:    mean={np.mean(pure_excl_folio_cts):.1f}, median={np.median(pure_excl_folio_cts):.0f}")
if ri_excl_folio_cts:
    print(f"    RI-excl:      mean={np.mean(ri_excl_folio_cts):.1f}, median={np.median(ri_excl_folio_cts):.0f}")

# ============================================================
# 4. Sampling artifact test
# ============================================================
print()
print("-" * 60)
print("4. Sampling Artifact Test")
print("-" * 60)

# If RI-bearing lines are 37% of lines, and PP MIDDLEs are randomly distributed,
# some MIDDLEs would appear only on RI-bearing lines by chance.
# Null model: for each PP MIDDLE with frequency f across n lines in a folio,
# probability it appears ONLY on RI-bearing lines = (r/n)^f where r = RI-bearing count
# (simplified: probability none of f appearances land on pp-pure lines)

# More precise: permutation test per folio
# For each folio, shuffle line type labels, count how many PP MIDDLEs become exclusive
np.random.seed(42)
N_PERMS = 1000

observed_ri_exclusive = []  # per folio: count of PP MIDDLEs exclusive to RI lines
null_ri_exclusive = []      # per folio: mean count under shuffling

for fol in folios:
    recs = folio_records[fol]
    n_lines = len(recs)
    if n_lines < 3:
        continue

    # Observed: which PP MIDDLEs are on which lines?
    line_pp_mids = []  # per line: set of PP MIDDLEs
    line_is_ri = []    # per line: bool
    for rec in recs:
        mids = set(t.middle for t in rec.tokens if t.is_pp and t.middle)
        line_pp_mids.append(mids)
        line_is_ri.append(rec.ri_count > 0)

    # Observed exclusive count
    obs_pure_mids = set()
    obs_ri_mids = set()
    for i in range(n_lines):
        if line_is_ri[i]:
            obs_ri_mids |= line_pp_mids[i]
        else:
            obs_pure_mids |= line_pp_mids[i]
    obs_exclusive = len(obs_ri_mids - obs_pure_mids)
    observed_ri_exclusive.append(obs_exclusive)

    # Null: shuffle labels
    null_counts = []
    labels_arr = np.array(line_is_ri)
    for _ in range(N_PERMS):
        np.random.shuffle(labels_arr)
        shuf_pure = set()
        shuf_ri = set()
        for i in range(n_lines):
            if labels_arr[i]:
                shuf_ri |= line_pp_mids[i]
            else:
                shuf_pure |= line_pp_mids[i]
        null_counts.append(len(shuf_ri - shuf_pure))
    null_ri_exclusive.append(float(np.mean(null_counts)))

observed_ri_exclusive = np.array(observed_ri_exclusive)
null_ri_exclusive = np.array(null_ri_exclusive)

obs_mean = float(np.mean(observed_ri_exclusive))
null_mean = float(np.mean(null_ri_exclusive))
ratio = obs_mean / null_mean if null_mean > 0 else float('inf')

# Paired test: is observed > null per folio?
diff = observed_ri_exclusive - null_ri_exclusive
t_stat, t_p = scipy_stats.ttest_1samp(diff, 0, alternative='greater')

print(f"  Observed RI-exclusive PP MIDDLEs per folio: mean={obs_mean:.2f}")
print(f"  Null (shuffled labels) expected:            mean={null_mean:.2f}")
print(f"  Ratio (observed/null):                      {ratio:.3f}")
print(f"  Paired t-test (observed > null): t={t_stat:.3f}, p={t_p:.4e}")

if t_p < 0.001:
    artifact_verdict = "NOT an artifact. RI-exclusive PP MIDDLEs exceed chance expectation."
elif t_p < 0.05:
    artifact_verdict = "Marginally significant. Some real effect but partially explained by sampling."
else:
    artifact_verdict = "SAMPLING ARTIFACT. RI-exclusive PP MIDDLEs explained by line count imbalance."

print(f"\n  VERDICT: {artifact_verdict}")

# Also: what fraction of observed exclusivity is explained by sampling?
explained_frac = null_mean / obs_mean if obs_mean > 0 else 1.0
print(f"  Sampling explains {explained_frac*100:.1f}% of observed RI exclusivity")
print(f"  Residual (real effect): {(1-explained_frac)*100:.1f}%")

# ============================================================
# 5. Which RI-gated classes are role-critical?
# ============================================================
print()
print("-" * 60)
print("5. RI-Gated Classes: Functional Impact")
print("-" * 60)

# For classes gated in >10% of folios: are they from critical roles?
threshold = len(folios) * 0.10
gated_above_10 = {cls for cls, ct in ri_gated_class_counts.items() if ct > threshold}

print(f"  Classes RI-gated in >10% of folios: {len(gated_above_10)}")
if gated_above_10:
    role_impact = Counter()
    for cls in gated_above_10:
        role = CLASS_TO_ROLE.get(cls, '??')
        role_impact[role] += 1
    print(f"  Role breakdown: {dict(role_impact)}")

    # Is FL disproportionately RI-gated? (FL is already fragile per C686)
    fl_gated = sum(1 for cls in gated_above_10 if CLASS_TO_ROLE.get(cls) == 'FL')
    fl_total = sum(1 for c in range(1, 50) if CLASS_TO_ROLE.get(c) == 'FL')
    print(f"  FL classes RI-gated: {fl_gated}/{fl_total}")

# ============================================================
# Summary
# ============================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
  RI-gated classes per folio: mean {np.mean(ri_gated_arr):.1f}, median {np.median(ri_gated_arr):.0f}
  Total classes ever RI-gated: {len(all_ri_gated)}
  Frequently gated (>25% folios): {sorted(freq_gated) if freq_gated else 'None'}

  RI-exclusive PP MIDDLEs:
    Global: {len(globally_exclusive_to_ri)} types exclusive to RI lines
    vs null (sampling): observed {obs_mean:.1f} vs expected {null_mean:.1f} per folio
    Sampling explains {explained_frac*100:.1f}%
    {artifact_verdict}

  RI-exclusive PP MIDDLEs are {'RARE singletons' if ri_excl_freqs and np.median(ri_excl_freqs) <= 2 else 'moderately frequent'}
  Folio spread: {'narrow' if ri_excl_folio_cts and np.median(ri_excl_folio_cts) <= 2 else 'broad'}
""")

# Save results
results = {
    'metadata': {
        'phase': 'RI_FUNCTIONAL_IDENTITY',
        'script': 'ri_gated_classes.py',
        'n_folios': len(folios),
    },
    'ri_gated_per_folio': {
        'mean': round(float(np.mean(ri_gated_arr)), 2),
        'median': round(float(np.median(ri_gated_arr)), 1),
        'max': int(np.max(ri_gated_arr)),
        'zero_count': int(np.sum(ri_gated_arr == 0)),
    },
    'ri_gated_classes': {
        'total_ever_gated': len(all_ri_gated),
        'frequently_gated_gt25pct': sorted(freq_gated) if freq_gated else [],
        'class_detail': {
            str(cls): {
                'role': CLASS_TO_ROLE.get(cls, '??'),
                'ri_gated_folios': ri_gated_class_counts[cls],
                'pp_reachable_folios': pp_only_class_counts.get(cls, 0),
            }
            for cls in sorted(all_ri_gated)
        },
        'role_event_counts': dict(ri_gated_roles),
    },
    'ri_exclusive_pp_middles': {
        'globally_exclusive_to_ri': len(globally_exclusive_to_ri),
        'globally_exclusive_to_pure': len(globally_exclusive_to_pure),
        'globally_shared': len(globally_shared),
        'ri_excl_median_freq': round(float(np.median(ri_excl_freqs)), 1) if ri_excl_freqs else 0,
        'ri_excl_median_folio_spread': round(float(np.median(ri_excl_folio_cts)), 1) if ri_excl_folio_cts else 0,
    },
    'sampling_artifact_test': {
        'observed_mean': round(obs_mean, 2),
        'null_mean': round(null_mean, 2),
        'ratio': round(ratio, 3),
        't_stat': round(t_stat, 3),
        'p_value': float(t_p),
        'sampling_explains_pct': round(explained_frac * 100, 1),
        'verdict': artifact_verdict,
    },
}

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
output_path = RESULTS_DIR / 'ri_gated_classes.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {output_path}")

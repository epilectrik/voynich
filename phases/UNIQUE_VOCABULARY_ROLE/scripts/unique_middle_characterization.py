"""
UNIQUE MIDDLE CHARACTERIZATION

Maps the 858 unique MIDDLEs (C531) into the ICC/UN/morphological framework.
4 sections: role distribution, UN overlap, morphological profile, line position.

Phase: UNIQUE_VOCABULARY_ROLE
"""

import os
import sys
import json
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import chi2_contingency, mannwhitneyu

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# Load shared data
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = ctm['token_to_class']
class_to_role = ctm['class_to_role']
ROLE_MAP = {
    'ENERGY_OPERATOR': 'EN',
    'AUXILIARY': 'AX',
    'FREQUENT_OPERATOR': 'FQ',
    'CORE_CONTROL': 'CC',
    'FLOW_OPERATOR': 'FL'
}

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

pp_middles = set(mc['a_shared_middles'])
ri_middles = set(mc['a_exclusive_middles'])

# PREFIX -> role prediction sets (C570, C611)
AX_PREFIXES = {'ol', 'lk', 'pch', 'yk', 'lch', 'te', 'po', 'so', 'or', 'ke',
               'tch', 'dch', 'se', 'de', 'pe', 'ko', 'to', 'do', 'ka', 'ta',
               'sa', 'ar', 'ct'}
EN_PREFIXES = {'qo', 'ch', 'sh', 'o', 'da', 'cph', 'ckh', 'sk', 'cp'}
FQ_PREFIXES = {'ch', 'sh', 'o', 'da'}  # overlap with EN; resolved by majority
FL_PREFIXES = {'s', 'p', 'f', 'r'}
CC_PREFIXES = set()  # CC fully resolved (C611)

# Build role prediction from PREFIX (simplified majority vote from C611)
def predict_role_from_prefix(prefix):
    if prefix in AX_PREFIXES:
        return 'AX'
    if prefix in {'qo', 'cph', 'ckh', 'sk', 'cp'}:
        return 'EN'
    if prefix in FL_PREFIXES:
        return 'FL'
    if prefix in {'ch', 'sh', 'o', 'da'}:
        return 'EN'  # EN majority for shared prefixes
    return None

tx = Transcript()
morph = Morphology()

# ============================================================
# BUILD BASE DATA STRUCTURES
# ============================================================

# Per-folio MIDDLE sets
folio_middles = defaultdict(set)
# All tokens with metadata
all_tokens = []

for token in tx.currier_b():
    word = token.word
    if not word or not word.strip():
        continue
    m = morph.extract(word)
    if not m.middle:
        continue
    folio_middles[token.folio].add(m.middle)

    # Role assignment
    if word in token_to_class:
        cls = str(token_to_class[word])
        role_full = class_to_role.get(cls, '')
        role = ROLE_MAP.get(role_full, 'UN')
    else:
        role = 'UN'

    all_tokens.append({
        'word': word,
        'folio': token.folio,
        'line': token.line,
        'section': token.section,
        'middle': m.middle,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'role': role,
        'line_pos': None,  # filled below
        'is_initial': token.line_initial,
        'is_final': token.line_final
    })

# Compute MIDDLE folio counts
middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for mid in middles:
        middle_folio_count[mid] += 1

unique_middles = set(mid for mid, cnt in middle_folio_count.items() if cnt == 1)
shared_middles = set(mid for mid, cnt in middle_folio_count.items() if cnt >= 2)

print("=" * 70)
print("UNIQUE MIDDLE CHARACTERIZATION")
print("=" * 70)
print(f"\nTotal B folios: {len(folio_middles)}")
print(f"Total distinct MIDDLEs: {len(middle_folio_count)}")
print(f"Unique MIDDLEs (1 folio): {len(unique_middles)}")
print(f"Shared MIDDLEs (2+ folios): {len(shared_middles)}")
print(f"Folios with unique MIDDLEs: {sum(1 for f in folio_middles if folio_middles[f] & unique_middles)}")

# Classify tokens
for t in all_tokens:
    t['is_unique'] = t['middle'] in unique_middles

# Build line sequences for position computation
line_tokens = defaultdict(list)
for i, t in enumerate(all_tokens):
    line_tokens[(t['folio'], t['line'])].append(i)

for key, indices in line_tokens.items():
    n = len(indices)
    for rank, idx in enumerate(indices):
        all_tokens[idx]['line_pos'] = rank / (n - 1) if n > 1 else 0.5

# ============================================================
# SECTION 1: ICC ROLE DISTRIBUTION OF UNIQUE MIDDLEs
# ============================================================

print("\n" + "=" * 70)
print("SECTION 1: ICC ROLE DISTRIBUTION")
print("=" * 70)

# For UN tokens, predict role from PREFIX
unique_role_counts = Counter()
shared_role_counts = Counter()
unique_predicted_role_counts = Counter()

for t in all_tokens:
    role = t['role']
    if role == 'UN' and t['prefix']:
        predicted = predict_role_from_prefix(t['prefix'])
        if predicted:
            role_with_prediction = predicted
        else:
            role_with_prediction = 'UN'
    else:
        role_with_prediction = role

    if t['is_unique']:
        unique_role_counts[role] += 1
        unique_predicted_role_counts[role_with_prediction] += 1
    else:
        shared_role_counts[role] += 1

unique_total = sum(unique_role_counts.values())
shared_total = sum(shared_role_counts.values())
all_total = unique_total + shared_total

print(f"\nTokens with unique MIDDLEs: {unique_total} ({100*unique_total/all_total:.1f}%)")
print(f"Tokens with shared MIDDLEs: {shared_total} ({100*shared_total/all_total:.1f}%)")

print(f"\nRole distribution (classified roles only):")
print(f"{'Role':<6} {'Unique':>8} {'Unique%':>8} {'Shared':>8} {'Shared%':>8}")
roles = ['EN', 'AX', 'FQ', 'FL', 'CC', 'UN']
for role in roles:
    u = unique_role_counts[role]
    s = shared_role_counts[role]
    up = 100 * u / unique_total if unique_total else 0
    sp = 100 * s / shared_total if shared_total else 0
    print(f"{role:<6} {u:>8} {up:>7.1f}% {s:>8} {sp:>7.1f}%")

print(f"\nRole distribution (with PREFIX prediction for UN):")
print(f"{'Role':<6} {'Unique':>8} {'%':>8}")
unique_pred_total = sum(unique_predicted_role_counts.values())
for role in roles:
    u = unique_predicted_role_counts[role]
    up = 100 * u / unique_pred_total if unique_pred_total else 0
    print(f"{role:<6} {u:>8} {up:>7.1f}%")

# Chi-squared: unique vs shared role distribution
print("\nChi-squared: unique vs shared role distribution")
obs = []
for role in roles:
    obs.append([unique_role_counts[role], shared_role_counts[role]])
obs = np.array(obs)
# Remove rows with zero total
mask = obs.sum(axis=1) > 0
obs_filtered = obs[mask]
if obs_filtered.shape[0] >= 2:
    chi2, p, dof, expected = chi2_contingency(obs_filtered)
    n_total = obs_filtered.sum()
    V = np.sqrt(chi2 / (n_total * (min(obs_filtered.shape) - 1)))
    print(f"  chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
    print(f"  Significant: {p < 0.05}")

# ============================================================
# SECTION 2: UN OVERLAP
# ============================================================

print("\n" + "=" * 70)
print("SECTION 2: UN OVERLAP")
print("=" * 70)

# MIDDLEs in UN tokens
un_middles = set()
classified_middles = set()
un_token_count = 0
un_unique_middle_token_count = 0

for t in all_tokens:
    if t['role'] == 'UN':
        un_middles.add(t['middle'])
        un_token_count += 1
        if t['is_unique']:
            un_unique_middle_token_count += 1
    else:
        classified_middles.add(t['middle'])

unique_in_un = unique_middles & un_middles
unique_in_classified = unique_middles & classified_middles
unique_in_both = unique_middles & un_middles & classified_middles
unique_only_un = unique_middles & un_middles - classified_middles
unique_only_classified = unique_middles & classified_middles - un_middles

print(f"\nUN token count: {un_token_count}")
print(f"UN MIDDLE types: {len(un_middles)}")
print(f"Classified MIDDLE types: {len(classified_middles)}")
print(f"\nUnique MIDDLE types: {len(unique_middles)}")
print(f"  In UN tokens: {len(unique_in_un)} ({100*len(unique_in_un)/len(unique_middles):.1f}%)")
print(f"  In classified tokens: {len(unique_in_classified)} ({100*len(unique_in_classified)/len(unique_middles):.1f}%)")
print(f"  In BOTH UN and classified: {len(unique_in_both)} ({100*len(unique_in_both)/len(unique_middles):.1f}%)")
print(f"  Only in UN: {len(unique_only_un)} ({100*len(unique_only_un)/len(unique_middles):.1f}%)")
print(f"  Only in classified: {len(unique_only_classified)} ({100*len(unique_only_classified)/len(unique_middles):.1f}%)")
print(f"\nUN tokens with unique MIDDLEs: {un_unique_middle_token_count} ({100*un_unique_middle_token_count/un_token_count:.1f}% of UN)")

# Hapax rate comparison
unique_middle_token_counts = Counter()
for t in all_tokens:
    if t['is_unique']:
        unique_middle_token_counts[t['word']] += 1
unique_hapax = sum(1 for w, c in unique_middle_token_counts.items() if c == 1)
unique_types = len(unique_middle_token_counts)
print(f"\nUnique MIDDLE token types: {unique_types}")
print(f"Unique MIDDLE hapax: {unique_hapax} ({100*unique_hapax/unique_types:.1f}%)")
print(f"UN hapax rate (C566): 74.1%")

# ============================================================
# SECTION 3: MORPHOLOGICAL PROFILE
# ============================================================

print("\n" + "=" * 70)
print("SECTION 3: MORPHOLOGICAL PROFILE")
print("=" * 70)

# Compare unique vs shared MIDDLE properties
unique_lengths = [len(t['middle']) for t in all_tokens if t['is_unique']]
shared_lengths = [len(t['middle']) for t in all_tokens if not t['is_unique']]

unique_suffix_rate = sum(1 for t in all_tokens if t['is_unique'] and t['suffix']) / max(unique_total, 1)
shared_suffix_rate = sum(1 for t in all_tokens if not t['is_unique'] and t['suffix']) / max(shared_total, 1)

unique_artic_rate = sum(1 for t in all_tokens if t['is_unique'] and t['articulator']) / max(unique_total, 1)
shared_artic_rate = sum(1 for t in all_tokens if not t['is_unique'] and t['articulator']) / max(shared_total, 1)

print(f"\n{'Metric':<30} {'Unique':>10} {'Shared':>10}")
print(f"{'MIDDLE length (mean)':<30} {np.mean(unique_lengths):>10.2f} {np.mean(shared_lengths):>10.2f}")
print(f"{'MIDDLE length (median)':<30} {np.median(unique_lengths):>10.1f} {np.median(shared_lengths):>10.1f}")
print(f"{'Suffix rate':<30} {100*unique_suffix_rate:>9.1f}% {100*shared_suffix_rate:>9.1f}%")
print(f"{'Articulator rate':<30} {100*unique_artic_rate:>9.1f}% {100*shared_artic_rate:>9.1f}%")

# Word length (full token)
unique_word_lengths = [len(t['word']) for t in all_tokens if t['is_unique']]
shared_word_lengths = [len(t['word']) for t in all_tokens if not t['is_unique']]
print(f"{'Word length (mean)':<30} {np.mean(unique_word_lengths):>10.2f} {np.mean(shared_word_lengths):>10.2f}")

# Mann-Whitney for length
stat, p_len = mannwhitneyu(unique_lengths, shared_lengths, alternative='two-sided')
print(f"\nMIDDLE length Mann-Whitney: U={stat:.0f}, p={p_len:.6f}")

stat_w, p_wlen = mannwhitneyu(unique_word_lengths, shared_word_lengths, alternative='two-sided')
print(f"Word length Mann-Whitney: U={stat_w:.0f}, p={p_wlen:.6f}")

# PP vs B-exclusive for unique MIDDLEs (type level)
unique_pp = unique_middles & pp_middles
unique_ri = unique_middles & ri_middles
unique_bexcl = unique_middles - pp_middles - ri_middles

print(f"\nUnique MIDDLE types by origin:")
print(f"  PP (A-shared): {len(unique_pp)} ({100*len(unique_pp)/len(unique_middles):.1f}%)")
print(f"  RI (A-exclusive): {len(unique_ri)} ({100*len(unique_ri)/len(unique_middles):.1f}%)")
print(f"  B-exclusive: {len(unique_bexcl)} ({100*len(unique_bexcl)/len(unique_middles):.1f}%)")

# PP atom containment: do unique MIDDLEs contain PP atoms?
pp_atoms = set()
for mid in pp_middles:
    if len(mid) <= 3:
        pp_atoms.add(mid)

unique_contains_pp = sum(1 for mid in unique_middles if any(atom in mid for atom in pp_atoms if len(atom) >= 2))
print(f"\nUnique MIDDLEs containing PP atom (len>=2): {unique_contains_pp} ({100*unique_contains_pp/len(unique_middles):.1f}%)")

# ============================================================
# SECTION 4: LINE POSITION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("SECTION 4: LINE POSITION DISTRIBUTION")
print("=" * 70)

unique_positions = [t['line_pos'] for t in all_tokens if t['is_unique'] and t['line_pos'] is not None]
shared_positions = [t['line_pos'] for t in all_tokens if not t['is_unique'] and t['line_pos'] is not None]

print(f"\n{'Metric':<30} {'Unique':>10} {'Shared':>10}")
print(f"{'Mean position':<30} {np.mean(unique_positions):>10.3f} {np.mean(shared_positions):>10.3f}")
print(f"{'Std position':<30} {np.std(unique_positions):>10.3f} {np.std(shared_positions):>10.3f}")

# Line-initial and line-final rates
unique_init = sum(1 for t in all_tokens if t['is_unique'] and t['is_initial'])
unique_final = sum(1 for t in all_tokens if t['is_unique'] and t['is_final'])
shared_init = sum(1 for t in all_tokens if not t['is_unique'] and t['is_initial'])
shared_final = sum(1 for t in all_tokens if not t['is_unique'] and t['is_final'])

print(f"{'Line-initial rate':<30} {100*unique_init/unique_total:>9.1f}% {100*shared_init/shared_total:>9.1f}%")
print(f"{'Line-final rate':<30} {100*unique_final/unique_total:>9.1f}% {100*shared_final/shared_total:>9.1f}%")

# Mann-Whitney for position
stat_pos, p_pos = mannwhitneyu(unique_positions, shared_positions, alternative='two-sided')
print(f"\nPosition Mann-Whitney: U={stat_pos:.0f}, p={p_pos:.6f}")

# Per-role position comparison
print(f"\nPer-role position comparison (unique vs shared):")
for role in ['EN', 'AX', 'FQ']:
    u_pos = [t['line_pos'] for t in all_tokens if t['is_unique'] and t['role'] == role and t['line_pos'] is not None]
    s_pos = [t['line_pos'] for t in all_tokens if not t['is_unique'] and t['role'] == role and t['line_pos'] is not None]
    if len(u_pos) >= 20 and len(s_pos) >= 20:
        stat_r, p_r = mannwhitneyu(u_pos, s_pos, alternative='two-sided')
        print(f"  {role}: unique mean={np.mean(u_pos):.3f} (n={len(u_pos)}), shared mean={np.mean(s_pos):.3f} (n={len(s_pos)}), p={p_r:.6f}")
    else:
        print(f"  {role}: insufficient data (unique n={len(u_pos)}, shared n={len(s_pos)})")

# UN tokens with unique MIDDLEs - position
un_unique_pos = [t['line_pos'] for t in all_tokens if t['is_unique'] and t['role'] == 'UN' and t['line_pos'] is not None]
un_shared_pos = [t['line_pos'] for t in all_tokens if not t['is_unique'] and t['role'] == 'UN' and t['line_pos'] is not None]
if len(un_unique_pos) >= 20 and len(un_shared_pos) >= 20:
    stat_un, p_un = mannwhitneyu(un_unique_pos, un_shared_pos, alternative='two-sided')
    print(f"  UN: unique mean={np.mean(un_unique_pos):.3f} (n={len(un_unique_pos)}), shared mean={np.mean(un_shared_pos):.3f} (n={len(un_shared_pos)}), p={p_un:.6f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'unique_middle_count': len(unique_middles),
    'shared_middle_count': len(shared_middles),
    'unique_token_count': unique_total,
    'shared_token_count': shared_total,
    'folios_with_unique': sum(1 for f in folio_middles if folio_middles[f] & unique_middles),
    'role_distribution': {
        'classified_only': {role: unique_role_counts[role] for role in roles},
        'with_prediction': {role: unique_predicted_role_counts[role] for role in roles}
    },
    'un_overlap': {
        'unique_in_un': len(unique_in_un),
        'unique_in_classified': len(unique_in_classified),
        'unique_in_both': len(unique_in_both),
        'unique_only_un': len(unique_only_un),
        'unique_only_classified': len(unique_only_classified),
        'un_tokens_with_unique_middle': un_unique_middle_token_count,
        'un_tokens_with_unique_middle_pct': round(100 * un_unique_middle_token_count / un_token_count, 1)
    },
    'morphology': {
        'unique_middle_length_mean': round(np.mean(unique_lengths), 2),
        'shared_middle_length_mean': round(np.mean(shared_lengths), 2),
        'middle_length_p': round(p_len, 6),
        'unique_word_length_mean': round(np.mean(unique_word_lengths), 2),
        'shared_word_length_mean': round(np.mean(shared_word_lengths), 2),
        'word_length_p': round(p_wlen, 6),
        'unique_suffix_rate': round(unique_suffix_rate, 3),
        'shared_suffix_rate': round(shared_suffix_rate, 3),
        'unique_artic_rate': round(unique_artic_rate, 3),
        'shared_artic_rate': round(shared_artic_rate, 3),
        'unique_pp_types': len(unique_pp),
        'unique_bexcl_types': len(unique_bexcl),
        'unique_pp_atom_containment_pct': round(100 * unique_contains_pp / len(unique_middles), 1)
    },
    'position': {
        'unique_mean_pos': round(np.mean(unique_positions), 3),
        'shared_mean_pos': round(np.mean(shared_positions), 3),
        'position_p': round(p_pos, 6),
        'unique_initial_rate': round(unique_init / unique_total, 3),
        'shared_initial_rate': round(shared_init / shared_total, 3),
        'unique_final_rate': round(unique_final / unique_total, 3),
        'shared_final_rate': round(shared_final / shared_total, 3)
    }
}

with open('phases/UNIQUE_VOCABULARY_ROLE/results/unique_middle_characterization.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Results saved to phases/UNIQUE_VOCABULARY_ROLE/results/unique_middle_characterization.json")
print("=" * 70)

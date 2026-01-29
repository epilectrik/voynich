"""
UNIQUE VOCABULARY BEHAVIOR

Tests whether tokens carrying unique MIDDLEs behave differently from
tokens carrying shared MIDDLEs. Script 1 established that ALL unique
MIDDLEs are UN tokens (0 classified), so comparisons are within the
UN population.

4 sections: UN-internal transition divergence, context signatures,
folio complexity coupling, REGIME/section concentration.

Phase: UNIQUE_VOCABULARY_ROLE
"""

import os
import sys
import json
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import chi2_contingency, mannwhitneyu, spearmanr, kruskal

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

with open('phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime

tx = Transcript()
morph = Morphology()

# AX-exclusive prefixes for role prediction (C570)
AX_PREFIXES = {'ol', 'lk', 'pch', 'yk', 'lch', 'te', 'po', 'so', 'or', 'ke',
               'tch', 'dch', 'se', 'de', 'pe', 'ko', 'to', 'do', 'ka', 'ta',
               'sa', 'ar', 'ct'}

def predict_role_from_prefix(prefix):
    if prefix in AX_PREFIXES:
        return 'AX'
    if prefix in {'qo', 'cph', 'ckh', 'sk', 'cp'}:
        return 'EN'
    if prefix in {'s', 'p', 'f', 'r'}:
        return 'FL'
    if prefix in {'ch', 'sh', 'o', 'da'}:
        return 'EN'
    return None

# ============================================================
# BUILD BASE DATA
# ============================================================

# Build per-folio MIDDLE sets for unique classification
folio_middles = defaultdict(set)
all_tokens = []

for token in tx.currier_b():
    word = token.word
    if not word or not word.strip():
        continue
    m = morph.extract(word)
    if not m.middle:
        continue

    folio_middles[token.folio].add(m.middle)

    if word in token_to_class:
        cls = str(token_to_class[word])
        role = ROLE_MAP.get(class_to_role.get(cls, ''), 'UN')
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
        'role': role
    })

middle_folio_count = defaultdict(int)
for folio, middles in folio_middles.items():
    for mid in middles:
        middle_folio_count[mid] += 1

unique_middles = set(mid for mid, cnt in middle_folio_count.items() if cnt == 1)

for t in all_tokens:
    t['is_unique'] = t['middle'] in unique_middles

# Build line sequences for transition analysis
line_sequences = defaultdict(list)
for i, t in enumerate(all_tokens):
    line_sequences[(t['folio'], t['line'])].append(i)

# Pre-compute predicted roles for all tokens
for t in all_tokens:
    if t['role'] == 'UN' and t['prefix']:
        predicted = predict_role_from_prefix(t['prefix'])
        t['predicted_role'] = predicted if predicted else 'UN'
    else:
        t['predicted_role'] = t['role']

print("=" * 70)
print("UNIQUE VOCABULARY BEHAVIOR")
print("=" * 70)
print(f"Total tokens: {len(all_tokens)}")
print(f"Unique MIDDLE tokens: {sum(1 for t in all_tokens if t['is_unique'])}")

# ============================================================
# SECTION 1: UN-INTERNAL TRANSITION DIVERGENCE
# ============================================================

print("\n" + "=" * 70)
print("SECTION 1: UN-INTERNAL TRANSITION DIVERGENCE")
print("Within UN tokens, do unique-MIDDLE tokens route differently from shared-MIDDLE tokens?")
print("=" * 70)

# For each UN token, find what follows it in the same line
un_unique_successors = Counter()
un_shared_successors = Counter()

for key, indices in line_sequences.items():
    for pos in range(len(indices) - 1):
        t = all_tokens[indices[pos]]
        t_next = all_tokens[indices[pos + 1]]
        if t['role'] == 'UN':
            next_role = t_next['role']
            if t['is_unique']:
                un_unique_successors[next_role] += 1
            else:
                un_shared_successors[next_role] += 1

roles = ['EN', 'AX', 'FQ', 'FL', 'CC', 'UN']
un_unique_total = sum(un_unique_successors.values())
un_shared_total = sum(un_shared_successors.values())

print(f"\nUN tokens with successors: unique={un_unique_total}, shared={un_shared_total}")
print(f"\n{'Role':<6} {'Unique':>8} {'Unique%':>8} {'Shared':>8} {'Shared%':>8}")
for role in roles:
    u = un_unique_successors[role]
    s = un_shared_successors[role]
    up = 100 * u / un_unique_total if un_unique_total else 0
    sp = 100 * s / un_shared_total if un_shared_total else 0
    print(f"{role:<6} {u:>8} {up:>7.1f}% {s:>8} {sp:>7.1f}%")

# Chi-squared
obs = [[un_unique_successors[r], un_shared_successors[r]] for r in roles]
obs = np.array(obs)
mask = obs.sum(axis=1) > 0
obs_f = obs[mask]
if obs_f.shape[0] >= 2:
    chi2, p, dof, _ = chi2_contingency(obs_f)
    n = obs_f.sum()
    V = np.sqrt(chi2 / (n * (min(obs_f.shape) - 1)))
    print(f"\nChi-squared (successor role): chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
    print(f"Significant: {p < 0.05}")

# Also test: do unique-MIDDLE UN tokens have different PREDECESSORS?
un_unique_predecessors = Counter()
un_shared_predecessors = Counter()

for key, indices in line_sequences.items():
    for pos in range(1, len(indices)):
        t = all_tokens[indices[pos]]
        t_prev = all_tokens[indices[pos - 1]]
        if t['role'] == 'UN':
            prev_role = t_prev['role']
            if t['is_unique']:
                un_unique_predecessors[prev_role] += 1
            else:
                un_shared_predecessors[prev_role] += 1

un_unique_pred_total = sum(un_unique_predecessors.values())
un_shared_pred_total = sum(un_shared_predecessors.values())

print(f"\nPredecessor distributions:")
print(f"{'Role':<6} {'Unique':>8} {'Unique%':>8} {'Shared':>8} {'Shared%':>8}")
for role in roles:
    u = un_unique_predecessors[role]
    s = un_shared_predecessors[role]
    up = 100 * u / un_unique_pred_total if un_unique_pred_total else 0
    sp = 100 * s / un_shared_pred_total if un_shared_pred_total else 0
    print(f"{role:<6} {u:>8} {up:>7.1f}% {s:>8} {sp:>7.1f}%")

obs_pred = [[un_unique_predecessors[r], un_shared_predecessors[r]] for r in roles]
obs_pred = np.array(obs_pred)
mask_p = obs_pred.sum(axis=1) > 0
obs_pf = obs_pred[mask_p]
if obs_pf.shape[0] >= 2:
    chi2_p, p_p, dof_p, _ = chi2_contingency(obs_pf)
    n_p = obs_pf.sum()
    V_p = np.sqrt(chi2_p / (n_p * (min(obs_pf.shape) - 1)))
    print(f"\nChi-squared (predecessor role): chi2={chi2_p:.2f}, p={p_p:.6f}, dof={dof_p}, V={V_p:.3f}")
    print(f"Significant: {p_p < 0.05}")

# Within EN-predicted UN: unique vs shared transitions
print("\n--- EN-predicted UN subset ---")
en_pred_unique_succ = Counter()
en_pred_shared_succ = Counter()

for key, indices in line_sequences.items():
    for pos in range(len(indices) - 1):
        t = all_tokens[indices[pos]]
        t_next = all_tokens[indices[pos + 1]]
        if t['role'] == 'UN' and t['predicted_role'] == 'EN':
            next_role = t_next['role']
            if t['is_unique']:
                en_pred_unique_succ[next_role] += 1
            else:
                en_pred_shared_succ[next_role] += 1

en_u_total = sum(en_pred_unique_succ.values())
en_s_total = sum(en_pred_shared_succ.values())
print(f"EN-predicted UN with successors: unique={en_u_total}, shared={en_s_total}")

if en_u_total >= 20 and en_s_total >= 20:
    print(f"\n{'Role':<6} {'Unique':>8} {'Unique%':>8} {'Shared':>8} {'Shared%':>8}")
    for role in roles:
        u = en_pred_unique_succ[role]
        s = en_pred_shared_succ[role]
        up = 100 * u / en_u_total if en_u_total else 0
        sp = 100 * s / en_s_total if en_s_total else 0
        print(f"{role:<6} {u:>8} {up:>7.1f}% {s:>8} {sp:>7.1f}%")

    obs_en = [[en_pred_unique_succ[r], en_pred_shared_succ[r]] for r in roles]
    obs_en = np.array(obs_en)
    mask_en = obs_en.sum(axis=1) > 0
    obs_enf = obs_en[mask_en]
    if obs_enf.shape[0] >= 2:
        chi2_en, p_en, dof_en, _ = chi2_contingency(obs_enf)
        n_en = obs_enf.sum()
        V_en = np.sqrt(chi2_en / (n_en * (min(obs_enf.shape) - 1)))
        print(f"\nChi-squared: chi2={chi2_en:.2f}, p={p_en:.6f}, dof={dof_en}, V={V_en:.3f}")

# ============================================================
# SECTION 2: CONTEXT SIGNATURES
# ============================================================

print("\n" + "=" * 70)
print("SECTION 2: CONTEXT SIGNATURES")
print("Do unique-MIDDLE tokens appear in specific bigram contexts?")
print("=" * 70)

# For each token, look at the bigram (prev_role, this_role, next_role)
# Compare unique vs shared for the preceding bigram
bigram_unique = Counter()
bigram_shared = Counter()

for key, indices in line_sequences.items():
    for pos in range(1, len(indices) - 1):
        t = all_tokens[indices[pos]]
        t_prev = all_tokens[indices[pos - 1]]
        t_next = all_tokens[indices[pos + 1]]
        if t['role'] == 'UN':
            bigram = (t_prev['role'], t_next['role'])
            if t['is_unique']:
                bigram_unique[bigram] += 1
            else:
                bigram_shared[bigram] += 1

# Top 10 bigrams for unique vs shared
print(f"\nTop 10 context bigrams (prev, next) for UNIQUE MIDDLE UN tokens:")
bu_total = sum(bigram_unique.values())
for bg, cnt in bigram_unique.most_common(10):
    print(f"  {bg[0]}->{bg[1]}: {cnt} ({100*cnt/bu_total:.1f}%)")

print(f"\nTop 10 context bigrams for SHARED MIDDLE UN tokens:")
bs_total = sum(bigram_shared.values())
for bg, cnt in bigram_shared.most_common(10):
    print(f"  {bg[0]}->{bg[1]}: {cnt} ({100*cnt/bs_total:.1f}%)")

# Are unique-MIDDLE UN tokens more likely to be adjacent to OTHER UN tokens?
unique_un_neighbor_rate = 0
shared_un_neighbor_rate = 0
unique_count = 0
shared_count = 0

for key, indices in line_sequences.items():
    for pos in range(len(indices)):
        t = all_tokens[indices[pos]]
        if t['role'] != 'UN':
            continue
        has_un_neighbor = False
        if pos > 0 and all_tokens[indices[pos-1]]['role'] == 'UN':
            has_un_neighbor = True
        if pos < len(indices) - 1 and all_tokens[indices[pos+1]]['role'] == 'UN':
            has_un_neighbor = True
        if t['is_unique']:
            unique_count += 1
            unique_un_neighbor_rate += int(has_un_neighbor)
        else:
            shared_count += 1
            shared_un_neighbor_rate += int(has_un_neighbor)

if unique_count > 0 and shared_count > 0:
    u_rate = unique_un_neighbor_rate / unique_count
    s_rate = shared_un_neighbor_rate / shared_count
    print(f"\nUN-neighbor rate:")
    print(f"  Unique MIDDLE UN: {100*u_rate:.1f}% (n={unique_count})")
    print(f"  Shared MIDDLE UN: {100*s_rate:.1f}% (n={shared_count})")

# ============================================================
# SECTION 3: FOLIO COMPLEXITY COUPLING
# ============================================================

print("\n" + "=" * 70)
print("SECTION 3: FOLIO COMPLEXITY COUPLING")
print("Does unique MIDDLE count predict folio-level metrics?")
print("=" * 70)

# Per-folio metrics
folio_unique_count = {}
folio_token_count = Counter()
folio_type_count = defaultdict(set)
folio_un_count = Counter()
folio_link_count = Counter()
folio_line_set = defaultdict(set)
folio_hazard_count = Counter()

# Hazard classes (from BCSC: classes involved in forbidden transitions)
HAZARD_CLASSES = {7, 8, 30, 38, 40, 47}  # FL, EN hazard, FL, FL, FL, EN

for t in all_tokens:
    f = t['folio']
    folio_token_count[f] += 1
    folio_type_count[f].add(t['word'])
    folio_line_set[f].add(t['line'])
    if t['role'] == 'UN':
        folio_un_count[f] += 1
    if 'ol' in t['word']:
        folio_link_count[f] += 1
    if t['word'] in token_to_class:
        cls = int(token_to_class[t['word']])
        if cls in HAZARD_CLASSES:
            folio_hazard_count[f] += 1

for f in folio_middles:
    folio_unique_count[f] = len(folio_middles[f] & unique_middles)

# Compute metrics for all folios
folios = sorted(folio_middles.keys())
unique_counts = [folio_unique_count[f] for f in folios]
token_counts = [folio_token_count[f] for f in folios]
ttr_vals = [len(folio_type_count[f]) / folio_token_count[f] if folio_token_count[f] else 0 for f in folios]
un_props = [folio_un_count[f] / folio_token_count[f] if folio_token_count[f] else 0 for f in folios]
link_dens = [folio_link_count[f] / folio_token_count[f] if folio_token_count[f] else 0 for f in folios]
hazard_dens = [folio_hazard_count[f] / folio_token_count[f] if folio_token_count[f] else 0 for f in folios]
# Unique density (normalized by token count)
unique_dens = [folio_unique_count[f] / folio_token_count[f] if folio_token_count[f] else 0 for f in folios]

correlations = {}
metrics = {
    'Token count': token_counts,
    'TTR': ttr_vals,
    'UN proportion': un_props,
    'LINK density': link_dens,
    'Hazard density': hazard_dens
}

print(f"\n{'Metric':<20} {'rho':>8} {'p-value':>10} {'Sig':>6}")
for name, vals in metrics.items():
    rho, p = spearmanr(unique_counts, vals)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
    print(f"{name:<20} {rho:>8.3f} {p:>10.6f} {sig:>6}")
    correlations[name] = {'rho': round(rho, 3), 'p': round(p, 6)}

# Also test unique density (normalized)
print(f"\nNormalized unique density correlations:")
for name, vals in metrics.items():
    if name != 'Token count':
        rho, p = spearmanr(unique_dens, vals)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
        print(f"  unique_density vs {name:<20} rho={rho:>7.3f}, p={p:.6f} {sig}")

# ============================================================
# SECTION 4: REGIME AND SECTION CONCENTRATION
# ============================================================

print("\n" + "=" * 70)
print("SECTION 4: REGIME AND SECTION CONCENTRATION")
print("=" * 70)

# Section-level analysis
folio_section = {}
for t in all_tokens:
    folio_section[t['folio']] = t['section']

section_unique_counts = defaultdict(list)
section_unique_dens = defaultdict(list)
for f in folios:
    sec = folio_section.get(f, 'unknown')
    section_unique_counts[sec].append(folio_unique_count[f])
    section_unique_dens[sec].append(folio_unique_count[f] / folio_token_count[f] if folio_token_count[f] else 0)

print(f"\nUnique MIDDLEs per folio by section:")
print(f"{'Section':<10} {'Folios':>8} {'Mean':>8} {'Median':>8} {'Mean dens':>10}")
for sec in sorted(section_unique_counts.keys()):
    vals = section_unique_counts[sec]
    dens = section_unique_dens[sec]
    print(f"{sec:<10} {len(vals):>8} {np.mean(vals):>8.1f} {np.median(vals):>8.1f} {100*np.mean(dens):>9.2f}%")

# Kruskal-Wallis: section predicts unique density?
sec_groups = [section_unique_dens[s] for s in sorted(section_unique_dens.keys()) if len(section_unique_dens[s]) >= 3]
if len(sec_groups) >= 2:
    H_sec, p_sec = kruskal(*sec_groups)
    print(f"\nKruskal-Wallis (section -> unique density): H={H_sec:.2f}, p={p_sec:.6f}")

# REGIME-level analysis
regime_unique_counts = defaultdict(list)
regime_unique_dens = defaultdict(list)
for f in folios:
    reg = folio_to_regime.get(f, 'unknown')
    regime_unique_counts[reg].append(folio_unique_count[f])
    regime_unique_dens[reg].append(folio_unique_count[f] / folio_token_count[f] if folio_token_count[f] else 0)

print(f"\nUnique MIDDLEs per folio by REGIME:")
print(f"{'REGIME':<12} {'Folios':>8} {'Mean':>8} {'Median':>8} {'Mean dens':>10}")
for reg in sorted(regime_unique_counts.keys()):
    vals = regime_unique_counts[reg]
    dens = regime_unique_dens[reg]
    print(f"{reg:<12} {len(vals):>8} {np.mean(vals):>8.1f} {np.median(vals):>8.1f} {100*np.mean(dens):>9.2f}%")

# Kruskal-Wallis: REGIME predicts unique density?
reg_groups = [regime_unique_dens[r] for r in sorted(regime_unique_dens.keys()) if len(regime_unique_dens[r]) >= 3]
if len(reg_groups) >= 2:
    H_reg, p_reg = kruskal(*reg_groups)
    print(f"\nKruskal-Wallis (REGIME -> unique density): H={H_reg:.2f}, p={p_reg:.6f}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'un_transition_divergence': {
        'successor': {
            'unique_total': un_unique_total,
            'shared_total': un_shared_total,
            'unique_dist': {r: un_unique_successors[r] for r in roles},
            'shared_dist': {r: un_shared_successors[r] for r in roles}
        },
        'predecessor': {
            'unique_total': un_unique_pred_total,
            'shared_total': un_shared_pred_total,
            'unique_dist': {r: un_unique_predecessors[r] for r in roles},
            'shared_dist': {r: un_shared_predecessors[r] for r in roles}
        }
    },
    'context': {
        'unique_un_neighbor_rate': round(u_rate, 3) if unique_count > 0 else None,
        'shared_un_neighbor_rate': round(s_rate, 3) if shared_count > 0 else None
    },
    'folio_coupling': correlations,
    'section_concentration': {
        sec: {
            'n': len(section_unique_counts[sec]),
            'mean': round(np.mean(section_unique_counts[sec]), 1),
            'mean_density': round(np.mean(section_unique_dens[sec]), 4)
        } for sec in sorted(section_unique_counts.keys())
    },
    'regime_concentration': {
        reg: {
            'n': len(regime_unique_counts[reg]),
            'mean': round(np.mean(regime_unique_counts[reg]), 1),
            'mean_density': round(np.mean(regime_unique_dens[reg]), 4)
        } for reg in sorted(regime_unique_counts.keys())
    }
}

with open('phases/UNIQUE_VOCABULARY_ROLE/results/unique_vocabulary_behavior.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 70)
print("Results saved to phases/UNIQUE_VOCABULARY_ROLE/results/unique_vocabulary_behavior.json")
print("=" * 70)

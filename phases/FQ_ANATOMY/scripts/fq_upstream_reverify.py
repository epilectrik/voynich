"""
FQ_ANATOMY Script 3: Upstream Re-Verification

Re-verify C550, C551, C552, C556 with corrected FQ={9,13,14,23}.
Old FQ was {9,20,21,23} per C559 (SUPERSEDED).

Follows AX_REVERIFICATION pattern: old vs new comparison with verdicts.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/FQ_ANATOMY/results'

# OLD role mapping (from role_transition_matrix.py line 43)
OLD_ROLE_MAP = {
    10: 'CC', 11: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 36: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 20: 'FQ', 21: 'FQ', 23: 'FQ',
}

# CORRECTED role mapping
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 14, 23}

def get_role_old(cls):
    if cls is None:
        return 'UN'
    return OLD_ROLE_MAP.get(cls, 'AX')

def get_role_new(cls):
    if cls is None:
        return 'UN'
    if cls in ICC_CC:
        return 'CC'
    if cls in ICC_EN:
        return 'EN'
    if cls in ICC_FL:
        return 'FL'
    if cls in ICC_FQ:
        return 'FQ'
    return 'AX'

# Load data
print("=" * 70)
print("FQ UPSTREAM RE-VERIFICATION")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Section mapping
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except Exception:
        return 'UNKNOWN'
    if num <= 25:
        return 'HERBAL_A'
    elif num <= 56:
        return 'HERBAL_B'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'RECIPE_A'
    else:
        return 'RECIPE_B'

# Build line structures with both old and new role assignments
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'word': word, 'class': cls, 'folio': token.folio,
        'role_old': get_role_old(cls),
        'role_new': get_role_new(cls),
    })

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
results = {
    'meta': {
        'phase': 'FQ_ANATOMY',
        'date': '2026-01-26',
        'old_fq': [9, 20, 21, 23],
        'new_fq': [9, 13, 14, 23],
    }
}

# ============================================================
# C550: ROLE TRANSITION GRAMMAR
# ============================================================
print("\n" + "=" * 70)
print("C550: ROLE TRANSITION GRAMMAR")
print("=" * 70)

def compute_transitions(role_key):
    """Compute transition matrix using the specified role key."""
    trans = defaultdict(lambda: defaultdict(int))
    role_n = defaultdict(int)
    total_t = 0
    for (folio, line_id), line_tokens in lines.items():
        for i in range(len(line_tokens) - 1):
            src = line_tokens[i][role_key]
            dst = line_tokens[i + 1][role_key]
            trans[src][dst] += 1
            role_n[src] += 1
            total_t += 1
        if line_tokens:
            role_n[line_tokens[-1][role_key]] += 1
    return trans, role_n, total_t

old_trans, old_role_n, old_total = compute_transitions('role_old')
new_trans, new_role_n, new_total = compute_transitions('role_new')

def compute_enrichments(trans, role_n, total_t):
    """Compute enrichment matrix."""
    total_roles = sum(role_n.values())
    dst_probs = {r: role_n[r] / total_roles for r in ROLES}
    enrichment = {}
    for src in ROLES:
        enrichment[src] = {}
        row_total = sum(trans[src].values())
        for dst in ROLES:
            obs = trans[src][dst] / row_total if row_total > 0 else 0
            exp = dst_probs[dst]
            enrichment[src][dst] = obs / exp if exp > 0 else 0
    return enrichment, dst_probs

old_enrich, old_dst = compute_enrichments(old_trans, old_role_n, old_total)
new_enrich, new_dst = compute_enrichments(new_trans, new_role_n, new_total)

# Key values
print(f"\nRole frequencies:")
print(f"{'Role':>4} {'Old_n':>7} {'Old_%':>7} {'New_n':>7} {'New_%':>7}")
for r in ROLES:
    old_pct = old_role_n[r] / sum(old_role_n.values()) * 100
    new_pct = new_role_n[r] / sum(new_role_n.values()) * 100
    print(f"  {r:>2} {old_role_n[r]:>7} {old_pct:>6.1f}% {new_role_n[r]:>7} {new_pct:>6.1f}%")

print(f"\nKey enrichment changes:")
key_transitions = [
    ('FQ', 'FQ', 'FQ self-transition'),
    ('FL', 'FQ', 'FL->FQ affinity'),
    ('FQ', 'FL', 'FQ->FL affinity'),
    ('EN', 'FQ', 'EN->FQ avoidance'),
    ('FQ', 'EN', 'FQ->EN'),
    ('CC', 'FQ', 'CC->FQ'),
    ('AX', 'FQ', 'AX->FQ'),
]

c550_changes = {}
for src, dst, label in key_transitions:
    old_v = old_enrich.get(src, {}).get(dst, 0)
    new_v = new_enrich.get(src, {}).get(dst, 0)
    change = new_v - old_v
    print(f"  {label:25s}: {old_v:.2f}x -> {new_v:.2f}x  ({change:+.2f})")
    c550_changes[f"{src}->{dst}"] = {'old': round(old_v, 3), 'new': round(new_v, 3)}

# Self-transition chi-squared for new
fq_row_new = sum(new_trans['FQ'].values())
fq_self_new = new_trans['FQ']['FQ']
fq_self_exp = fq_row_new * new_dst['FQ']
if fq_self_exp > 0:
    chi2_self = (fq_self_new - fq_self_exp) ** 2 / fq_self_exp
    p_self = 1 - stats.chi2.cdf(chi2_self, 1)
    print(f"\n  FQ self-transition: obs={fq_self_new}, exp={fq_self_exp:.1f}, chi2={chi2_self:.1f}, p={p_self:.4f}")

# Full enrichment matrix (new)
print(f"\nFull enrichment matrix (NEW):")
print(f"{'':>8}", end='')
for r in ROLES:
    print(f" {r:>5}", end='')
print()
for src in ROLES:
    print(f"  {src:>4}:", end='')
    for dst in ROLES:
        v = new_enrich[src][dst]
        print(f" {v:5.2f}", end='')
    print()

results['C550'] = {
    'old': {
        'FQ_self': round(old_enrich['FQ']['FQ'], 3),
        'FL_FQ': round(old_enrich['FL']['FQ'], 3),
        'FQ_FL': round(old_enrich['FQ']['FL'], 3),
        'EN_FQ': round(old_enrich['EN']['FQ'], 3),
        'FQ_rate': round(old_dst['FQ'] * 100, 2),
        'note': 'FQ={9,20,21,23}'
    },
    'new': {
        'FQ_self': round(new_enrich['FQ']['FQ'], 3),
        'FL_FQ': round(new_enrich['FL']['FQ'], 3),
        'FQ_FL': round(new_enrich['FQ']['FL'], 3),
        'EN_FQ': round(new_enrich['EN']['FQ'], 3),
        'FQ_rate': round(new_dst['FQ'] * 100, 2),
        'full_enrichment': {src: {dst: round(new_enrich[src][dst], 3) for dst in ROLES} for src in ROLES},
        'note': 'FQ={9,13,14,23}'
    },
    'changes': c550_changes,
    'verdict': 'check',
}

# ============================================================
# C551: GRAMMAR UNIVERSALITY
# ============================================================
print("\n" + "=" * 70)
print("C551: GRAMMAR UNIVERSALITY")
print("=" * 70)

def compute_regime_evenness(role_key):
    """Compute per-class regime entropy and universality."""
    class_regimes = defaultdict(Counter)
    for (folio, line_id), line_tokens in lines.items():
        regime = folio_regime.get(folio)
        if not regime:
            continue
        for tok in line_tokens:
            cls = tok['class']
            role = tok[role_key]
            if role == 'FQ':
                class_regimes[cls][regime] += 1

    REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    class_entropy = {}
    for cls, regime_counts in class_regimes.items():
        total = sum(regime_counts.values())
        if total < 10:
            continue
        probs = [regime_counts.get(r, 0) / total for r in REGIMES]
        entropy = 0
        for p in probs:
            if p > 0:
                entropy -= p * np.log2(p)
        max_entropy = np.log2(4)
        evenness = entropy / max_entropy if max_entropy > 0 else 0
        class_entropy[cls] = evenness

    mean_evenness = np.mean(list(class_entropy.values())) if class_entropy else 0
    universal = sum(1 for v in class_entropy.values() if v > 0.7)
    total_cls = len(class_entropy)
    return class_entropy, mean_evenness, universal, total_cls

old_entropy, old_mean, old_univ, old_n = compute_regime_evenness('role_old')
new_entropy, new_mean, new_univ, new_n = compute_regime_evenness('role_new')

print(f"\nOLD FQ regime evenness:")
for cls in sorted(old_entropy.keys()):
    print(f"  Class {cls}: {old_entropy[cls]:.4f}")
print(f"  Mean: {old_mean:.4f}, Universal: {old_univ}/{old_n}")

print(f"\nNEW FQ regime evenness:")
for cls in sorted(new_entropy.keys()):
    print(f"  Class {cls}: {new_entropy[cls]:.4f}")
print(f"  Mean: {new_mean:.4f}, Universal: {new_univ}/{new_n}")

# Determine verdict
if abs(new_mean - old_mean) < 0.05:
    c551_verdict = 'UNCHANGED'
elif new_mean > old_mean:
    c551_verdict = 'STRENGTHENED'
else:
    c551_verdict = 'WEAKENED'

print(f"\nVerdict: {c551_verdict}")

results['C551'] = {
    'old': {
        'mean_evenness': round(old_mean, 4),
        'universal_fraction': f"{old_univ}/{old_n}",
        'per_class': {str(k): round(v, 4) for k, v in sorted(old_entropy.items())},
    },
    'new': {
        'mean_evenness': round(new_mean, 4),
        'universal_fraction': f"{new_univ}/{new_n}",
        'per_class': {str(k): round(v, 4) for k, v in sorted(new_entropy.items())},
    },
    'verdict': c551_verdict,
}

# ============================================================
# C552: SECTION ROLE PROFILES
# ============================================================
print("\n" + "=" * 70)
print("C552: SECTION ROLE PROFILES")
print("=" * 70)

def compute_section_profiles(role_key):
    """Compute per-section role distribution."""
    section_role = defaultdict(Counter)
    for (folio, line_id), line_tokens in lines.items():
        section = get_section(folio)
        for tok in line_tokens:
            role = tok[role_key]
            section_role[section][role] += 1
    return section_role

old_sp = compute_section_profiles('role_old')
new_sp = compute_section_profiles('role_new')

SECTIONS = ['HERBAL_A', 'HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_A', 'RECIPE_B']

print(f"\nFQ% per section:")
print(f"{'Section':>12} {'Old_FQ%':>8} {'New_FQ%':>8} {'Change':>8}")
old_fq_pcts = {}
new_fq_pcts = {}
for sec in SECTIONS:
    old_total = sum(old_sp[sec].values())
    new_total = sum(new_sp[sec].values())
    old_fq = old_sp[sec]['FQ'] / old_total * 100 if old_total > 0 else 0
    new_fq = new_sp[sec]['FQ'] / new_total * 100 if new_total > 0 else 0
    old_fq_pcts[sec] = old_fq
    new_fq_pcts[sec] = new_fq
    print(f"  {sec:>10} {old_fq:>7.1f}% {new_fq:>7.1f}% {new_fq - old_fq:>+7.1f}")

# Enrichment (FQ% / overall FQ%)
old_total_all = sum(sum(old_sp[s].values()) for s in SECTIONS)
new_total_all = sum(sum(new_sp[s].values()) for s in SECTIONS)
old_fq_all = sum(old_sp[s]['FQ'] for s in SECTIONS)
new_fq_all = sum(new_sp[s]['FQ'] for s in SECTIONS)
old_fq_base = old_fq_all / old_total_all * 100 if old_total_all > 0 else 0
new_fq_base = new_fq_all / new_total_all * 100 if new_total_all > 0 else 0

print(f"\nFQ enrichment per section (vs baseline FQ%):")
print(f"  Baseline: old={old_fq_base:.1f}%, new={new_fq_base:.1f}%")
print(f"{'Section':>12} {'Old_enrich':>10} {'New_enrich':>10}")
for sec in SECTIONS:
    old_e = old_fq_pcts[sec] / old_fq_base if old_fq_base > 0 else 0
    new_e = new_fq_pcts[sec] / new_fq_base if new_fq_base > 0 else 0
    if old_fq_pcts[sec] > 0 or new_fq_pcts[sec] > 0:
        print(f"  {sec:>10} {old_e:>9.2f}x {new_e:>9.2f}x")

results['C552'] = {
    'old': {
        'fq_baseline': round(old_fq_base, 2),
        'per_section': {s: round(old_fq_pcts[s], 2) for s in SECTIONS},
    },
    'new': {
        'fq_baseline': round(new_fq_base, 2),
        'per_section': {s: round(new_fq_pcts[s], 2) for s in SECTIONS},
    },
    'verdict': 'check',
}

# ============================================================
# C556: POSITIONAL ENRICHMENT
# ============================================================
print("\n" + "=" * 70)
print("C556: POSITIONAL ENRICHMENT")
print("=" * 70)

def compute_positional_enrichment(role_key):
    """Compute per-role initial and final enrichment."""
    role_initial = defaultdict(int)
    role_final = defaultdict(int)
    role_total = defaultdict(int)
    total_tokens = 0
    total_initial = 0
    total_final = 0

    for (folio, line_id), line_tokens in lines.items():
        n = len(line_tokens)
        if n == 0:
            continue
        for i, tok in enumerate(line_tokens):
            role = tok[role_key]
            role_total[role] += 1
            total_tokens += 1
            if i == 0:
                role_initial[role] += 1
                total_initial += 1
            if i == n - 1:
                role_final[role] += 1
                total_final += 1

    base_init = total_initial / total_tokens if total_tokens > 0 else 0
    base_final = total_final / total_tokens if total_tokens > 0 else 0

    enrichment = {}
    for role in ROLES:
        n = role_total[role]
        if n == 0:
            continue
        init_rate = role_initial[role] / n
        fin_rate = role_final[role] / n
        enrichment[role] = {
            'initial_rate': init_rate,
            'final_rate': fin_rate,
            'initial_enrichment': init_rate / base_init if base_init > 0 else 0,
            'final_enrichment': fin_rate / base_final if base_final > 0 else 0,
            'n': n,
        }
    return enrichment

old_pos = compute_positional_enrichment('role_old')
new_pos = compute_positional_enrichment('role_new')

print(f"\nPositional enrichment (FQ focus):")
print(f"{'':>15} {'Old':>8} {'New':>8}")
for key in ['initial_rate', 'final_rate', 'initial_enrichment', 'final_enrichment']:
    old_v = old_pos.get('FQ', {}).get(key, 0)
    new_v = new_pos.get('FQ', {}).get(key, 0)
    print(f"  {key:>20}: {old_v:.4f} {new_v:.4f}")

print(f"\nAll roles positional enrichment (NEW):")
print(f"{'Role':>4} {'Init_rate':>10} {'Init_enrich':>12} {'Fin_rate':>10} {'Fin_enrich':>12}")
for r in ROLES:
    if r in new_pos:
        p = new_pos[r]
        print(f"  {r:>2} {p['initial_rate']:>10.4f} {p['initial_enrichment']:>11.2f}x {p['final_rate']:>10.4f} {p['final_enrichment']:>11.2f}x")

# Determine C556 verdict
old_fq_fin = old_pos.get('FQ', {}).get('final_enrichment', 0)
new_fq_fin = new_pos.get('FQ', {}).get('final_enrichment', 0)
# Core claim is "EN medial concentration" - FQ is secondary
if abs(new_fq_fin - old_fq_fin) < 0.2:
    c556_verdict = 'UNCHANGED'
elif abs(new_fq_fin - old_fq_fin) >= 0.5:
    c556_verdict = 'DIRECTION_SHIFTED'
else:
    c556_verdict = 'MINOR_SHIFT'

print(f"\nFQ final enrichment: {old_fq_fin:.2f}x -> {new_fq_fin:.2f}x")
print(f"Verdict: {c556_verdict}")

results['C556'] = {
    'old': {
        'FQ_initial_enrichment': round(old_pos.get('FQ', {}).get('initial_enrichment', 0), 3),
        'FQ_final_enrichment': round(old_fq_fin, 3),
        'FQ_n': old_pos.get('FQ', {}).get('n', 0),
        'note': 'FQ={9,20,21,23}'
    },
    'new': {
        'FQ_initial_enrichment': round(new_pos.get('FQ', {}).get('initial_enrichment', 0), 3),
        'FQ_final_enrichment': round(new_fq_fin, 3),
        'FQ_n': new_pos.get('FQ', {}).get('n', 0),
        'all_roles': {r: {
            'initial_enrichment': round(new_pos[r]['initial_enrichment'], 3),
            'final_enrichment': round(new_pos[r]['final_enrichment'], 3),
        } for r in ROLES if r in new_pos},
        'note': 'FQ={9,13,14,23}'
    },
    'verdict': c556_verdict,
}

# ============================================================
# OVERALL VERDICTS
# ============================================================
print("\n" + "=" * 70)
print("OVERALL VERDICTS")
print("=" * 70)

# Set C550 verdict based on directional consistency
old_self = old_enrich['FQ']['FQ']
new_self = new_enrich['FQ']['FQ']
old_fl_fq = old_enrich['FL']['FQ']
new_fl_fq = new_enrich['FL']['FQ']

# Check if key patterns are directionally preserved
self_preserved = (old_self > 1.0 and new_self > 1.0) or (old_self < 1.0 and new_self < 1.0)
fl_fq_preserved = (old_fl_fq > 1.0 and new_fl_fq > 1.0) or (old_fl_fq < 1.0 and new_fl_fq < 1.0)

if self_preserved and fl_fq_preserved:
    if abs(new_self - old_self) < 0.3:
        c550_verdict = 'UNCHANGED'
    else:
        c550_verdict = 'MAGNITUDES_SHIFTED'
else:
    c550_verdict = 'DIRECTION_CHANGED'

results['C550']['verdict'] = c550_verdict
print(f"  C550: {c550_verdict}")
print(f"    FQ self: {old_self:.2f}x -> {new_self:.2f}x")
print(f"    FL->FQ: {old_fl_fq:.2f}x -> {new_fl_fq:.2f}x")

print(f"  C551: {c551_verdict}")
print(f"    Mean evenness: {old_mean:.4f} -> {new_mean:.4f}")

# Set C552 verdict
max_shift = max(abs(new_fq_pcts[s] - old_fq_pcts[s]) for s in SECTIONS)
if max_shift < 2.0:
    c552_verdict = 'UNCHANGED'
else:
    c552_verdict = 'MAGNITUDES_SHIFTED'
results['C552']['verdict'] = c552_verdict
print(f"  C552: {c552_verdict}")
print(f"    Max section FQ% shift: {max_shift:.1f}pp")

print(f"  C556: {c556_verdict}")
print(f"    FQ final enrich: {old_fq_fin:.2f}x -> {new_fq_fin:.2f}x")

# Save
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'fq_upstream_reverify.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'fq_upstream_reverify.json'}")

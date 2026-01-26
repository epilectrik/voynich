"""
Script 4: EN Interleaving Anatomy

Deep analysis of the qo <-> ch/sh interleaving mechanism.
WHY does alternation happen? Positional? Section-driven? Triggered?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/EN_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
ALL_CLASSES = set(token_to_class.values())

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# EN class set (ICC-based)
ICC_EN_RAW = {8} | set(range(31, 50))
ICC_FL = {7, 30, 38, 40}
EN_CLASSES = (ICC_EN_RAW - ICC_FL) & ALL_CLASSES

# Subfamily definitions
QO_CLASSES = {32, 33, 36}
CHSH_CLASSES = {8, 31, 34}
MINOR_EN = EN_CLASSES - QO_CLASSES - CHSH_CLASSES

# Build token -> subfamily lookup
token_subfamily = {}
class_to_tokens = defaultdict(set)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].add(tok)
    if cls in QO_CLASSES:
        token_subfamily[tok] = 'QO'
    elif cls in CHSH_CLASSES:
        token_subfamily[tok] = 'CHSH'
    elif cls in MINOR_EN:
        token_subfamily[tok] = 'MINOR'

# Role map
ICC_CC = {10, 11, 12, 17}
ICC_FQ = {9, 13, 23}
AX_CLASSES = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}

def get_role(cls):
    if cls in ICC_CC: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    if cls in AX_CLASSES: return 'AX'
    return 'UN'

# Section mapper
def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except:
        return 'UNKNOWN'
    if num <= 25:
        return 'HERBAL_A'
    elif num <= 56:
        return 'HERBAL_B'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 73:
        return 'ASTRO'
    elif num <= 84:
        return 'BIO'
    elif num <= 86:
        return 'COSMO'
    elif num <= 102:
        return 'RECIPE_A'
    else:
        return 'RECIPE_B'

# ============================================================
# BUILD LINE STRUCTURES
# ============================================================
print("Building line structures...")

lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sf = token_subfamily.get(word)
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'role': get_role(cls) if cls else 'UN',
        'subfamily': sf,  # QO, CHSH, MINOR, or None
        'folio': token.folio,
    })

print("=" * 70)
print("EN INTERLEAVING ANATOMY")
print("=" * 70)

# ============================================================
# 1. POSITIONAL ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("1. POSITIONAL ANALYSIS: QO vs CH/SH within lines")
print("-" * 70)

qo_positions = []
chsh_positions = []
minor_positions = []

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    if n <= 1:
        continue
    for i, tok in enumerate(line_tokens):
        pos = i / (n - 1)
        if tok['subfamily'] == 'QO':
            qo_positions.append(pos)
        elif tok['subfamily'] == 'CHSH':
            chsh_positions.append(pos)
        elif tok['subfamily'] == 'MINOR':
            minor_positions.append(pos)

qo_arr = np.array(qo_positions)
chsh_arr = np.array(chsh_positions)

print(f"\nQO tokens: n={len(qo_arr)}, mean_pos={np.mean(qo_arr):.3f}, std={np.std(qo_arr):.3f}")
print(f"CH/SH tokens: n={len(chsh_arr)}, mean_pos={np.mean(chsh_arr):.3f}, std={np.std(chsh_arr):.3f}")
if minor_positions:
    minor_arr = np.array(minor_positions)
    print(f"MINOR tokens: n={len(minor_arr)}, mean_pos={np.mean(minor_arr):.3f}, std={np.std(minor_arr):.3f}")

# Mann-Whitney U test for positional difference
u_stat, u_p = stats.mannwhitneyu(qo_arr, chsh_arr, alternative='two-sided')
print(f"\nMann-Whitney U: U={u_stat:.0f}, p={u_p:.6f}")
print(f"Positional separation: {'SIGNIFICANT' if u_p < 0.01 else 'NOT SIGNIFICANT'}")

# Positional bins
bins = np.linspace(0, 1, 6)  # 5 bins: [0-0.2, 0.2-0.4, ..., 0.8-1.0]
qo_hist, _ = np.histogram(qo_arr, bins=bins)
chsh_hist, _ = np.histogram(chsh_arr, bins=bins)
qo_pct = qo_hist / qo_hist.sum() * 100
chsh_pct = chsh_hist / chsh_hist.sum() * 100

print(f"\n{'Bin':>10} {'QO%':>7} {'CHSH%':>7} {'Ratio':>7}")
for i in range(len(bins)-1):
    label = f"{bins[i]:.1f}-{bins[i+1]:.1f}"
    ratio = qo_pct[i] / chsh_pct[i] if chsh_pct[i] > 0 else float('inf')
    print(f"{label:>10} {qo_pct[i]:6.1f} {chsh_pct[i]:6.1f} {ratio:6.2f}x")

# ============================================================
# 2. CHAIN ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("2. CHAIN ANALYSIS: Consecutive EN subfamily runs")
print("-" * 70)

chains = []  # (type, length, folio, section, regime)

for (folio, line_id), line_tokens in lines.items():
    current_sf = None
    chain_len = 0
    section = get_section(folio)
    regime = folio_regime.get(folio, 'UNKNOWN')

    for tok in line_tokens:
        sf = tok['subfamily']
        if sf is None:
            # Non-EN token: emit current chain if any
            if current_sf and chain_len > 0:
                chains.append((current_sf, chain_len, folio, section, regime))
            current_sf = None
            chain_len = 0
        elif sf == current_sf:
            chain_len += 1
        else:
            # Subfamily switch
            if current_sf and chain_len > 0:
                chains.append((current_sf, chain_len, folio, section, regime))
            current_sf = sf
            chain_len = 1

    # Emit last chain
    if current_sf and chain_len > 0:
        chains.append((current_sf, chain_len, folio, section, regime))

# Chain statistics
chain_types = Counter(c[0] for c in chains)
chain_lengths = defaultdict(list)
for sf, length, _, _, _ in chains:
    chain_lengths[sf].append(length)

print(f"\nTotal chains: {len(chains)}")
for sf in ['QO', 'CHSH', 'MINOR']:
    if sf in chain_lengths:
        lens = chain_lengths[sf]
        print(f"  {sf}: {len(lens)} chains, mean_len={np.mean(lens):.2f}, "
              f"max={max(lens)}, median={np.median(lens):.0f}")

# ============================================================
# 3. TRANSITION ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("3. TRANSITION ANALYSIS: What follows what?")
print("-" * 70)

transition_counts = Counter()  # (from_sf, to_sf) -> count
trigger_counts = Counter()     # (role_before, switching_to_sf) -> count

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    prev_en_sf = None
    prev_role = None

    for i, tok in enumerate(line_tokens):
        sf = tok['subfamily']
        role = tok['role']

        if sf is not None:
            # EN token
            if prev_en_sf is not None and prev_en_sf != sf:
                # Subfamily switch!
                transition_counts[(prev_en_sf, sf)] += 1
                # What role immediately precedes this switch?
                if prev_role is not None:
                    trigger_counts[(prev_role, sf)] += 1
            prev_en_sf = sf

        prev_role = role

total_transitions = sum(transition_counts.values())
print(f"\nTotal subfamily transitions: {total_transitions}")
print(f"\n{'From':>6} -> {'To':>6} {'Count':>6} {'Pct':>7}")
for (from_sf, to_sf), count in sorted(transition_counts.items(), key=lambda x: -x[1]):
    pct = count / total_transitions * 100
    print(f"{from_sf:>6} -> {to_sf:>6} {count:>6} {pct:>6.1f}%")

# Interleaving rate (QO<->CHSH switches vs total)
qo_chsh_switches = transition_counts.get(('QO', 'CHSH'), 0) + transition_counts.get(('CHSH', 'QO'), 0)
same_family = transition_counts.get(('QO', 'QO'), 0) + transition_counts.get(('CHSH', 'CHSH'), 0)
core_transitions = qo_chsh_switches + same_family
interleave_rate = qo_chsh_switches / core_transitions if core_transitions > 0 else 0
print(f"\nCore QO<->CHSH interleaving rate: {interleave_rate:.1%} ({qo_chsh_switches}/{core_transitions})")

# ============================================================
# 4. TRIGGER ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("4. TRIGGER ANALYSIS: What precedes a subfamily switch?")
print("-" * 70)

# What role precedes entry into QO vs CHSH?
qo_triggers = Counter()
chsh_triggers = Counter()

for (folio, line_id), line_tokens in lines.items():
    for i, tok in enumerate(line_tokens):
        sf = tok['subfamily']
        if sf is None or i == 0:
            continue
        prev = line_tokens[i-1]
        if prev['subfamily'] == sf:
            continue  # Same subfamily — not a switch
        if prev['subfamily'] is not None and prev['subfamily'] != sf:
            # Direct subfamily switch (EN->EN)
            pass  # Already captured in transition_counts
        # What role precedes this EN subfamily token (when it's a new entry)?
        if prev['subfamily'] is None:
            # Non-EN -> EN entry
            if sf == 'QO':
                qo_triggers[prev['role']] += 1
            elif sf == 'CHSH':
                chsh_triggers[prev['role']] += 1

print(f"\nRole preceding QO entry (from non-EN):")
for role, count in qo_triggers.most_common(10):
    print(f"  {role}: {count} ({count/sum(qo_triggers.values())*100:.1f}%)")

print(f"\nRole preceding CHSH entry (from non-EN):")
for role, count in chsh_triggers.most_common(10):
    print(f"  {role}: {count} ({count/sum(chsh_triggers.values())*100:.1f}%)")

# Chi-square: are trigger profiles different?
roles_union = sorted(set(qo_triggers.keys()) | set(chsh_triggers.keys()))
qo_vals = [qo_triggers.get(r, 0) for r in roles_union]
chsh_vals = [chsh_triggers.get(r, 0) for r in roles_union]
if len(roles_union) >= 2:
    chi2, chi_p = stats.chisquare(qo_vals, f_exp=[sum(qo_vals)/len(roles_union)]*len(roles_union))
    chi2_2, chi_p_2 = stats.chi2_contingency(np.array([qo_vals, chsh_vals]) + 0.5)[:2]
    print(f"\nChi-square (trigger profile QO vs CHSH): chi2={chi2_2:.2f}, p={chi_p_2:.6f}")

# ============================================================
# 5. SECTION-SPECIFIC ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("5. SECTION-SPECIFIC INTERLEAVING")
print("-" * 70)

section_transitions = defaultdict(lambda: {'interleave': 0, 'same': 0})

for (folio, line_id), line_tokens in lines.items():
    section = get_section(folio)
    prev_core_sf = None

    for tok in line_tokens:
        sf = tok['subfamily']
        if sf in ('QO', 'CHSH'):
            if prev_core_sf is not None:
                if sf != prev_core_sf:
                    section_transitions[section]['interleave'] += 1
                else:
                    section_transitions[section]['same'] += 1
            prev_core_sf = sf

print(f"\n{'Section':>12} {'Interleave':>10} {'Same':>6} {'Total':>6} {'Rate':>7}")
section_rates = {}
for section in ['HERBAL_A', 'HERBAL_B', 'PHARMA', 'BIO', 'RECIPE_A', 'RECIPE_B', 'ASTRO', 'COSMO']:
    d = section_transitions[section]
    total = d['interleave'] + d['same']
    rate = d['interleave'] / total if total > 0 else 0
    section_rates[section] = rate
    if total > 0:
        print(f"{section:>12} {d['interleave']:>10} {d['same']:>6} {total:>6} {rate:>6.1%}")

# PHARMA should show reduced interleaving (C555: class 33 depleted)
pharma_rate = section_rates.get('PHARMA', 0)
herbal_rate = section_rates.get('HERBAL_B', 0)
bio_rate = section_rates.get('BIO', 0)
print(f"\nPHARMA interleaving: {pharma_rate:.1%}")
print(f"HERBAL_B interleaving: {herbal_rate:.1%}")
print(f"BIO interleaving: {bio_rate:.1%}")
if herbal_rate > 0:
    print(f"PHARMA/HERBAL_B ratio: {pharma_rate/herbal_rate:.2f}x")

# ============================================================
# 6. REGIME-SPECIFIC ANALYSIS
# ============================================================
print("\n" + "-" * 70)
print("6. REGIME-SPECIFIC INTERLEAVING")
print("-" * 70)

regime_transitions = defaultdict(lambda: {'interleave': 0, 'same': 0})

for (folio, line_id), line_tokens in lines.items():
    regime = folio_regime.get(folio, 'UNKNOWN')
    prev_core_sf = None

    for tok in line_tokens:
        sf = tok['subfamily']
        if sf in ('QO', 'CHSH'):
            if prev_core_sf is not None:
                if sf != prev_core_sf:
                    regime_transitions[regime]['interleave'] += 1
                else:
                    regime_transitions[regime]['same'] += 1
            prev_core_sf = sf

print(f"\n{'Regime':>12} {'Interleave':>10} {'Same':>6} {'Total':>6} {'Rate':>7}")
regime_rates = {}
for regime in sorted(regime_transitions.keys()):
    d = regime_transitions[regime]
    total = d['interleave'] + d['same']
    rate = d['interleave'] / total if total > 0 else 0
    regime_rates[regime] = rate
    print(f"{regime:>12} {d['interleave']:>10} {d['same']:>6} {total:>6} {rate:>6.1%}")

# ============================================================
# 7. MINOR CLASS PARTICIPATION
# ============================================================
print("\n" + "-" * 70)
print("7. MINOR CLASS PARTICIPATION IN INTERLEAVING")
print("-" * 70)

# Do MINOR EN classes participate in the QO<->CHSH alternation pattern?
# Or do they form their own chains / insert independently?
minor_adjacent_to = Counter()  # What subfamily is adjacent to MINOR tokens?
minor_position_in_chain = []   # Where do MINOR tokens appear relative to QO/CHSH?

for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        if tok['subfamily'] != 'MINOR':
            continue
        # Check left neighbor
        if i > 0 and line_tokens[i-1]['subfamily'] in ('QO', 'CHSH'):
            minor_adjacent_to[f"left_{line_tokens[i-1]['subfamily']}"] += 1
        if i < n-1 and line_tokens[i+1]['subfamily'] in ('QO', 'CHSH'):
            minor_adjacent_to[f"right_{line_tokens[i+1]['subfamily']}"] += 1
        # Non-EN neighbors
        if i > 0 and line_tokens[i-1]['subfamily'] is None:
            minor_adjacent_to['left_nonEN'] += 1
        if i < n-1 and line_tokens[i+1]['subfamily'] is None:
            minor_adjacent_to['right_nonEN'] += 1

print(f"\nMINOR EN classes: {sorted(MINOR_EN)}")
print(f"Total MINOR tokens in corpus: {sum(1 for t in tokens if token_subfamily.get(t.word.replace('*','').strip()) == 'MINOR')}")
print(f"\nMINOR adjacency profile:")
for key, count in minor_adjacent_to.most_common():
    print(f"  {key}: {count}")

# Per-class breakdown for MINOR
minor_class_counts = Counter()
for token in tokens:
    word = token.word.replace('*', '').strip()
    cls = token_to_class.get(word)
    if cls in MINOR_EN:
        minor_class_counts[cls] += 1

print(f"\nPer-class counts (MINOR):")
for cls, count in sorted(minor_class_counts.items()):
    print(f"  Class {cls}: {count} tokens")

# ============================================================
# 8. WITHIN-LINE SUBFAMILY ORDERING
# ============================================================
print("\n" + "-" * 70)
print("8. WITHIN-LINE SUBFAMILY ORDERING PATTERNS")
print("-" * 70)

# For lines with both QO and CHSH tokens, which appears first?
qo_first_count = 0
chsh_first_count = 0
both_count = 0

for (folio, line_id), line_tokens in lines.items():
    first_qo_pos = None
    first_chsh_pos = None
    for i, tok in enumerate(line_tokens):
        if tok['subfamily'] == 'QO' and first_qo_pos is None:
            first_qo_pos = i
        elif tok['subfamily'] == 'CHSH' and first_chsh_pos is None:
            first_chsh_pos = i

    if first_qo_pos is not None and first_chsh_pos is not None:
        both_count += 1
        if first_qo_pos < first_chsh_pos:
            qo_first_count += 1
        else:
            chsh_first_count += 1

print(f"\nLines with both QO and CHSH: {both_count}")
print(f"QO appears first: {qo_first_count} ({qo_first_count/both_count*100:.1f}%)" if both_count > 0 else "")
print(f"CHSH appears first: {chsh_first_count} ({chsh_first_count/both_count*100:.1f}%)" if both_count > 0 else "")

# Binomial test for ordering bias
if both_count > 0:
    binom_result = stats.binomtest(qo_first_count, both_count, 0.5, alternative='two-sided')
    binom_p = binom_result.pvalue
    print(f"Binomial test (50/50 null): p={binom_p:.6f}")
    print(f"Ordering bias: {'SIGNIFICANT' if binom_p < 0.01 else 'NOT SIGNIFICANT'}")

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'subfamily_definitions': {
        'QO': sorted(QO_CLASSES),
        'CHSH': sorted(CHSH_CLASSES),
        'MINOR': sorted(MINOR_EN),
    },
    'positional_analysis': {
        'qo_mean_pos': round(float(np.mean(qo_arr)), 4),
        'qo_std_pos': round(float(np.std(qo_arr)), 4),
        'chsh_mean_pos': round(float(np.mean(chsh_arr)), 4),
        'chsh_std_pos': round(float(np.std(chsh_arr)), 4),
        'mann_whitney_p': round(float(u_p), 6),
        'positional_separation': u_p < 0.01,
    },
    'chain_analysis': {
        sf: {
            'n_chains': len(chain_lengths.get(sf, [])),
            'mean_length': round(float(np.mean(chain_lengths[sf])), 2) if sf in chain_lengths else 0,
            'max_length': int(max(chain_lengths[sf])) if sf in chain_lengths else 0,
        }
        for sf in ['QO', 'CHSH', 'MINOR']
    },
    'transitions': {
        f'{from_sf}->{to_sf}': count
        for (from_sf, to_sf), count in transition_counts.items()
    },
    'core_interleaving_rate': round(interleave_rate, 4),
    'section_interleaving': {
        section: round(rate, 4) for section, rate in section_rates.items()
    },
    'regime_interleaving': {
        regime: round(rate, 4) for regime, rate in regime_rates.items()
    },
    'ordering': {
        'lines_with_both': both_count,
        'qo_first': qo_first_count,
        'chsh_first': chsh_first_count,
        'qo_first_pct': round(qo_first_count / both_count * 100, 2) if both_count > 0 else 0,
    },
    'minor_class_counts': dict(minor_class_counts),
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'en_interleaving.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'en_interleaving.json'}")

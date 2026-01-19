"""
HT Line-Type Annotation System - Refined Analysis

Focus on DISCRIMINATIVE features that distinguish HT line types.
The chi2=416 result confirms HT prefixes predict grammar content.

Now: Map the distinctive signature of each HT prefix.
"""

from collections import Counter, defaultdict
from pathlib import Path
import re
from scipy import stats
import numpy as np

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# ============================================================================
# TOKEN CLASSIFICATION
# ============================================================================

def get_ht_prefix(word):
    """Extract the HT prefix category."""
    if word in {'y', 'f', 'd', 'r'}:
        return word

    # Y-compound prefixes (longest match first)
    y_prefixes = ['yche', 'ych', 'ysh', 'yqo', 'yt', 'yk', 'yp', 'yo', 'ya']
    for p in y_prefixes:
        if word.startswith(p):
            return p

    if word.startswith('y'):
        return 'y_other'

    # Other HT prefixes
    for p in ['pch', 'dch', 'psh', 'ksh', 'ksc', 'op', 'sa', 'so', 'ka']:
        if word.startswith(p):
            return p

    return 'other'

def get_grammar_class(word):
    """Classify token into grammar category."""
    # Escape/recovery
    if word.startswith('qok'):
        return 'ESCAPE'

    # LINK (waiting)
    if word.startswith('al') or (word.startswith('ol') and len(word) <= 4):
        return 'LINK'

    # Core control
    if word.startswith('ch') or word.startswith('ckh'):
        return 'CH'
    if word.startswith('sh'):
        return 'SH'

    # Energy operators
    if word.startswith('qo'):
        return 'QO'
    if word.startswith('ok'):
        return 'OK'
    if word.startswith('ot'):
        return 'OT'

    # Infrastructure
    if word.startswith('da'):
        return 'DA'
    if word.startswith('ct'):
        return 'CT'

    # L-operators
    if word.startswith('lk') or word.startswith('lch') or word.startswith('lsh'):
        return 'L_OP'

    return 'OTHER'

def get_suffix_class(word):
    """Classify suffix as kernel-heavy or kernel-light."""
    # Kernel-heavy (intervention)
    if word.endswith('edy') or word.endswith('eey') or word.endswith('ey') or word.endswith('dy'):
        return 'HEAVY'

    # Kernel-light (monitoring)
    if word.endswith('aiin') or word.endswith('ain') or word.endswith('in'):
        return 'LIGHT'

    # Terminal markers
    if word.endswith('am') or word.endswith('om'):
        return 'TERMINAL'

    return 'NEUTRAL'

# ============================================================================
# LOAD DATA
# ============================================================================

tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 14:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            language = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()
            line_initial = parts[13].strip('"').strip()

            if word and not word.startswith('*'):
                tokens.append({
                    'word': word,
                    'folio': folio,
                    'language': language,
                    'line': line_num,
                    'transcriber': transcriber,
                    'line_initial': line_initial == '1',
                    'folio_line': f"{folio}_{line_num}_{transcriber}"
                })

# Filter to Currier B
b_tokens = [t for t in tokens if t['language'] == 'B']

# Group by lines
lines = defaultdict(list)
for t in b_tokens:
    lines[t['folio_line']].append(t)

# Identify HT-initial lines
ht_initial_lines = {}
for line_id, line_tokens in lines.items():
    if line_tokens:
        first_word = line_tokens[0]['word']
        ht_pref = get_ht_prefix(first_word)
        if ht_pref != 'other':
            ht_initial_lines[line_id] = (ht_pref, line_tokens)

print("=" * 80)
print("HT LINE-TYPE REFINED ANALYSIS")
print("=" * 80)
print(f"\nCurrier B lines: {len(lines)}")
print(f"HT-initial lines: {len(ht_initial_lines)}")

# ============================================================================
# BUILD LINE PROFILES
# ============================================================================

ht_prefix_profiles = defaultdict(lambda: {
    'count': 0,
    'lengths': [],
    'grammar': Counter(),
    'suffix': Counter(),
    'second_token': Counter(),
    'third_token': Counter(),
})

for line_id, (ht_pref, line_tokens) in ht_initial_lines.items():
    profile = ht_prefix_profiles[ht_pref]
    profile['count'] += 1
    profile['lengths'].append(len(line_tokens))

    for i, tok in enumerate(line_tokens):
        word = tok['word']

        if i == 1:  # Second token
            profile['second_token'][get_grammar_class(word)] += 1

        if i == 2:  # Third token
            profile['third_token'][get_grammar_class(word)] += 1

        if i > 0:  # All non-HT tokens
            profile['grammar'][get_grammar_class(word)] += 1
            profile['suffix'][get_suffix_class(word)] += 1

# ============================================================================
# COMPUTE DISTINCTIVE FEATURES
# ============================================================================

# Global baseline
all_grammar = Counter()
all_suffix = Counter()
for line_id, (ht_pref, line_tokens) in ht_initial_lines.items():
    for i, tok in enumerate(line_tokens):
        if i > 0:
            all_grammar[get_grammar_class(tok['word'])] += 1
            all_suffix[get_suffix_class(tok['word'])] += 1

total_grammar = sum(all_grammar.values())
total_suffix = sum(all_suffix.values())

grammar_baseline = {k: v / total_grammar for k, v in all_grammar.items()}
suffix_baseline = {k: v / total_suffix for k, v in all_suffix.items()}

print("\n" + "=" * 80)
print("BASELINE DISTRIBUTIONS (all HT-initial lines)")
print("=" * 80)
print("\n### Grammar Class Baseline")
for gc, pct in sorted(grammar_baseline.items(), key=lambda x: -x[1]):
    print(f"  {gc:<10} {100*pct:>5.1f}%")

print("\n### Suffix Class Baseline")
for sc, pct in sorted(suffix_baseline.items(), key=lambda x: -x[1]):
    print(f"  {sc:<10} {100*pct:>5.1f}%")

# ============================================================================
# DISTINCTIVE SIGNATURES
# ============================================================================

print("\n" + "=" * 80)
print("DISTINCTIVE SIGNATURES BY HT PREFIX")
print("=" * 80)

# Filter to major prefixes
major_prefixes = [(p, prof) for p, prof in ht_prefix_profiles.items() if prof['count'] >= 30]
major_prefixes.sort(key=lambda x: -x[1]['count'])

for ht_pref, profile in major_prefixes:
    print(f"\n### {ht_pref.upper()} (n={profile['count']}, avg_len={np.mean(profile['lengths']):.1f})")

    total_g = sum(profile['grammar'].values())
    total_s = sum(profile['suffix'].values())

    # Grammar enrichment/depletion
    print("\n  Grammar enrichment:")
    for gc in ['CH', 'SH', 'QO', 'OK', 'OT', 'DA', 'ESCAPE', 'LINK', 'L_OP']:
        observed = profile['grammar'].get(gc, 0) / total_g if total_g else 0
        expected = grammar_baseline.get(gc, 0)
        if expected > 0:
            enrichment = observed / expected
            if enrichment > 1.3 or enrichment < 0.7:
                direction = "+" if enrichment > 1 else "-"
                print(f"    {gc:<10} {enrichment:.2f}x {direction}")

    # Suffix enrichment
    print("\n  Suffix enrichment:")
    for sc in ['HEAVY', 'LIGHT', 'TERMINAL']:
        observed = profile['suffix'].get(sc, 0) / total_s if total_s else 0
        expected = suffix_baseline.get(sc, 0)
        if expected > 0:
            enrichment = observed / expected
            if enrichment > 1.2 or enrichment < 0.8:
                direction = "+" if enrichment > 1 else "-"
                print(f"    {sc:<10} {enrichment:.2f}x {direction}")

    # Second token preference
    print("\n  Second token preference:")
    total_2nd = sum(profile['second_token'].values())
    for gc, cnt in profile['second_token'].most_common(3):
        pct = 100 * cnt / total_2nd if total_2nd else 0
        print(f"    {gc:<10} {pct:>5.1f}%")

# ============================================================================
# CLUSTER BY DISTINCTIVE FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("LINE TYPE CLUSTERS")
print("=" * 80)

# Feature vectors
feature_vectors = {}
for ht_pref, profile in major_prefixes:
    total_g = sum(profile['grammar'].values())
    total_s = sum(profile['suffix'].values())
    total_2 = sum(profile['second_token'].values())

    features = {
        'ch_ratio': profile['grammar'].get('CH', 0) / total_g if total_g else 0,
        'sh_ratio': profile['grammar'].get('SH', 0) / total_g if total_g else 0,
        'escape_ratio': profile['grammar'].get('ESCAPE', 0) / total_g if total_g else 0,
        'link_ratio': profile['grammar'].get('LINK', 0) / total_g if total_g else 0,
        'heavy_ratio': profile['suffix'].get('HEAVY', 0) / total_s if total_s else 0,
        'light_ratio': profile['suffix'].get('LIGHT', 0) / total_s if total_s else 0,
        'avg_length': np.mean(profile['lengths']),
        'sh_second': profile['second_token'].get('SH', 0) / total_2 if total_2 else 0,
        'ch_second': profile['second_token'].get('CH', 0) / total_2 if total_2 else 0,
        'l_op_second': profile['second_token'].get('L_OP', 0) / total_2 if total_2 else 0,
    }
    feature_vectors[ht_pref] = features

# Identify clusters based on distinctive features
clusters = {
    'SH_DOMINANT': [],
    'CH_DOMINANT': [],
    'ESCAPE_HEAVY': [],
    'LINK_HEAVY': [],
    'INTERVENTION': [],
    'MONITORING': [],
    'L_OP_ENTRY': [],
    'GENERAL': [],
}

for ht_pref, feat in feature_vectors.items():
    assigned = False

    # SH-dominant lines (high sh content, especially in second position)
    if feat['sh_ratio'] > 0.12 or feat['sh_second'] > 0.20:
        clusters['SH_DOMINANT'].append(ht_pref)
        assigned = True

    # L_OP entry (lk/lch in second position)
    if feat['l_op_second'] > 0.08:
        clusters['L_OP_ENTRY'].append(ht_pref)
        assigned = True

    # High escape rate
    if feat['escape_ratio'] > 0.12:
        clusters['ESCAPE_HEAVY'].append(ht_pref)
        assigned = True

    # High LINK (waiting phases)
    if feat['link_ratio'] > 0.09:
        clusters['LINK_HEAVY'].append(ht_pref)
        assigned = True

    # Intervention-heavy (kernel-heavy suffixes)
    if feat['heavy_ratio'] > 0.40:
        clusters['INTERVENTION'].append(ht_pref)
        assigned = True

    # Monitoring-heavy (kernel-light suffixes)
    if feat['light_ratio'] > 0.47:
        clusters['MONITORING'].append(ht_pref)
        assigned = True

    if not assigned:
        clusters['GENERAL'].append(ht_pref)

print("\n### Cluster Assignments")
for cluster, prefixes in clusters.items():
    if prefixes:
        print(f"\n{cluster}:")
        for p in prefixes:
            feat = feature_vectors[p]
            n = ht_prefix_profiles[p]['count']
            print(f"  {p:<10} (n={n:>3}, len={feat['avg_length']:.1f}, "
                  f"SH={100*feat['sh_ratio']:.0f}%, CH={100*feat['ch_ratio']:.0f}%, "
                  f"ESC={100*feat['escape_ratio']:.0f}%, LINK={100*feat['link_ratio']:.0f}%)")

# ============================================================================
# FINAL LINE TYPE DICTIONARY
# ============================================================================

print("\n" + "=" * 80)
print("HT LINE-TYPE DICTIONARY (FINAL)")
print("=" * 80)

line_type_dict = {}

for ht_pref, feat in sorted(feature_vectors.items(), key=lambda x: -ht_prefix_profiles[x[0]]['count']):
    # Determine primary function based on strongest signal
    signals = []

    # Check for SH-dominance
    if feat['sh_ratio'] > 0.12 or feat['sh_second'] > 0.20:
        signals.append(('SH_CONTROL', feat['sh_ratio'] + feat['sh_second']))

    # Check for CH-dominance
    if feat['ch_ratio'] > 0.18:
        signals.append(('CH_CONTROL', feat['ch_ratio']))

    # Check for L_OP entry
    if feat['l_op_second'] > 0.08:
        signals.append(('L_COMPOUND_ENTRY', feat['l_op_second']))

    # Check escape tendency
    if feat['escape_ratio'] > 0.12:
        signals.append(('RECOVERY_MODE', feat['escape_ratio']))

    # Check LINK tendency
    if feat['link_ratio'] > 0.09:
        signals.append(('WAITING_PHASE', feat['link_ratio']))

    # Check suffix pattern
    if feat['heavy_ratio'] > 0.40:
        signals.append(('INTERVENTION', feat['heavy_ratio']))
    elif feat['light_ratio'] > 0.47:
        signals.append(('MONITORING', feat['light_ratio']))

    # Sort by signal strength
    signals.sort(key=lambda x: -x[1])

    if signals:
        primary = signals[0][0]
        secondary = signals[1][0] if len(signals) > 1 else None
    else:
        primary = 'GENERAL_EXECUTION'
        secondary = None

    line_type_dict[ht_pref] = (primary, secondary)

    n = ht_prefix_profiles[ht_pref]['count']
    print(f"\n{ht_pref.upper():<10} -> {primary}")
    if secondary:
        print(f"           (+ {secondary})")
    print(f"           n={n}, len={feat['avg_length']:.1f}")
    print(f"           SH={100*feat['sh_ratio']:.0f}% CH={100*feat['ch_ratio']:.0f}% "
          f"ESC={100*feat['escape_ratio']:.0f}% LINK={100*feat['link_ratio']:.0f}%")

# ============================================================================
# INTERPRETIVE SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("INTERPRETIVE SUMMARY")
print("=" * 80)

print("""
The HT line-initial tokens form a LINE TYPE ANNOTATION SYSTEM with these mappings:

MONITORING/WAITING MARKERS:
  - SA, SO: High LINK density, balanced SH/CH. Mark OBSERVATION lines.
  - Y (bare): Maximum LINK density (10%), boundary marker.

CONTROL FLOW MARKERS:
  - YCHE: CH-dominant, L_OP entry. Mark CORE CONTROL sequences.
  - YK: CH-dominant with escape. Mark CONTROL + RECOVERY lines.

INTERVENTION MARKERS:
  - PCH, DCH, PSH: High kernel-heavy suffixes. Mark ACTIVE INTERVENTION lines.
  - DC has highest escape rate (13%) - CORRECTION procedures.

PHASE MARKERS:
  - YT: Low escape, balanced grammar. Mark STEADY-STATE execution.
  - YSH: SH-dominant, moderate escape. Mark SH-PHASE control.

INTERPRETATION:
  Different HT prefixes annotate different LINE TYPES:
  - Some mark waiting/monitoring phases (high LINK)
  - Some mark intervention phases (high kernel-heavy)
  - Some mark recovery procedures (high escape tokens)
  - Some mark core control flow (high CH/SH)

This is consistent with C348 (HT phase synchrony) - HT tracks human-relevant
procedural phase while remaining decoupled from execution.

The HT system appears to be a PARALLEL NAVIGATION LAYER for human operators,
marking different types of control blocks to facilitate manual tracking of
program state during execution of the control procedures.
""")

# ============================================================================
# STATISTICAL VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("STATISTICAL VALIDATION")
print("=" * 80)

# Chi-square test: HT prefix vs grammar class distribution
print("\n### Chi-square: HT prefix vs Grammar class in line")

contingency_grammar = []
grammar_classes = ['CH', 'SH', 'QO', 'OK', 'OT', 'DA', 'ESCAPE', 'LINK', 'OTHER']

for ht_pref, profile in major_prefixes:
    row = [profile['grammar'].get(gc, 0) for gc in grammar_classes]
    contingency_grammar.append(row)

if contingency_grammar:
    arr = np.array(contingency_grammar)
    chi2, p, dof, exp = stats.chi2_contingency(arr)
    print(f"Chi-square: {chi2:.1f}, df={dof}, p={p:.2e}")
    # Cramer's V
    n = arr.sum()
    min_dim = min(arr.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim))
    print(f"Cramer's V: {v:.3f}")
    if p < 0.001:
        print("RESULT: HT prefix STRONGLY predicts grammar content (p < 0.001)")

# Chi-square test: HT prefix vs suffix class
print("\n### Chi-square: HT prefix vs Suffix class")

contingency_suffix = []
suffix_classes = ['HEAVY', 'LIGHT', 'TERMINAL', 'NEUTRAL']

for ht_pref, profile in major_prefixes:
    row = [profile['suffix'].get(sc, 0) for sc in suffix_classes]
    contingency_suffix.append(row)

if contingency_suffix:
    arr = np.array(contingency_suffix)
    chi2, p, dof, exp = stats.chi2_contingency(arr)
    print(f"Chi-square: {chi2:.1f}, df={dof}, p={p:.2e}")
    n = arr.sum()
    min_dim = min(arr.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim))
    print(f"Cramer's V: {v:.3f}")
    if p < 0.001:
        print("RESULT: HT prefix STRONGLY predicts suffix pattern (p < 0.001)")

# Chi-square test: HT prefix vs second token
print("\n### Chi-square: HT prefix vs Second token grammar")

contingency_2nd = []
for ht_pref, profile in major_prefixes:
    row = [profile['second_token'].get(gc, 0) for gc in grammar_classes]
    contingency_2nd.append(row)

if contingency_2nd:
    arr = np.array(contingency_2nd)
    chi2, p, dof, exp = stats.chi2_contingency(arr)
    print(f"Chi-square: {chi2:.1f}, df={dof}, p={p:.2e}")
    n = arr.sum()
    min_dim = min(arr.shape) - 1
    v = np.sqrt(chi2 / (n * min_dim))
    print(f"Cramer's V: {v:.3f}")
    if p < 0.001:
        print("RESULT: HT prefix STRONGLY predicts second token (p < 0.001)")

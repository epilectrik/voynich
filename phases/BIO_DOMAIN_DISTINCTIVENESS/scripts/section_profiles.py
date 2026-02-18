#!/usr/bin/env python3
"""
Phase 385 supplement: Full section profiling across all dimensions.

Profiles each section (B=Bio, S=Stars, H=Herbal, C=Cosmo, T=Recipe)
on the same dimensions used in T1-T4 of the main Phase 385 analysis:
kernel balance, hazard class distribution, LINK%, CC triggers, AXM self-rate.
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, BTokenAnalysis

# C109 hazard classes (from main script)
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]
HAZARD_CLASSES = {
    ('shey', 'aiin'): 'PHASE_ORDERING', ('shey', 'al'): 'PHASE_ORDERING',
    ('shey', 'c'): 'PHASE_ORDERING', ('chol', 'r'): 'PHASE_ORDERING',
    ('dy', 'chey'): 'PHASE_ORDERING', ('chey', 'chedy'): 'PHASE_ORDERING',
    ('chey', 'shedy'): 'PHASE_ORDERING',
    ('chedy', 'ee'): 'COMPOSITION_JUMP', ('dy', 'aiin'): 'COMPOSITION_JUMP',
    ('c', 'ee'): 'COMPOSITION_JUMP', ('shedy', 'aiin'): 'COMPOSITION_JUMP',
    ('l', 'chol'): 'CONTAINMENT_TIMING', ('ar', 'dal'): 'CONTAINMENT_TIMING',
    ('he', 't'): 'CONTAINMENT_TIMING', ('shedy', 'o'): 'CONTAINMENT_TIMING',
    ('or', 'dal'): 'RATE_MISMATCH',
    ('he', 'or'): 'ENERGY_OVERSHOOT',
}
HAZARD_SOURCES = set(a for a, b in FORBIDDEN_TRANSITIONS)

# ===================================================================
print("=" * 80)
print("PHASE 385 SUPPLEMENT: FULL SECTION PROFILING")
print("=" * 80)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load regime assignments
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Build token lists per folio
folio_tokens = defaultdict(list)
folio_section = {}

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens[tok.folio].append(tok)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

# Section names
SECTION_NAMES = {'B': 'Bio', 'S': 'Stars', 'H': 'Herbal', 'C': 'Cosmo', 'T': 'Recipe'}

# Group folios by section
section_folios = defaultdict(list)
for f, s in folio_section.items():
    section_folios[s].append(f)

# Print section overview
print(f"{'Section':<10} {'Name':<10} {'Folios':>6} {'Tokens':>8} {'REGIMEs'}")
print(f"{'-'*10} {'-'*10} {'-'*6} {'-'*8} {'-'*30}")
for s in sorted(section_folios.keys()):
    folios = section_folios[s]
    tokens = sum(len(folio_tokens[f]) for f in folios)
    regimes = Counter(folio_regime.get(f, '?') for f in folios)
    regime_str = ', '.join(f"{r}:{n}" for r, n in sorted(regimes.items()))
    print(f"{s:<10} {SECTION_NAMES.get(s, '?'):<10} {len(folios):>6} {tokens:>8} {regime_str}")
print()

# ===================================================================
# KERNEL BALANCE PER SECTION
# ===================================================================
print("-" * 80)
print("KERNEL BALANCE BY SECTION")
print("-" * 80)
print()

def count_kernels(folio_set):
    counts = Counter()
    for folio in folio_set:
        for tok in folio_tokens[folio]:
            m = morph.extract(tok.word)
            if m.middle:
                for c in m.middle:
                    if c in ('k', 'h', 'e'):
                        counts[c] += 1
    return counts

print(f"  {'Section':<10} {'k%':>8} {'h%':>8} {'e%':>8} {'k/e ratio':>10} {'k count':>8} {'h count':>8} {'e count':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

all_kernels = Counter()
for s in sorted(section_folios.keys()):
    kc = count_kernels(section_folios[s])
    total = sum(kc.values())
    if total == 0:
        continue
    k_pct = 100 * kc['k'] / total
    h_pct = 100 * kc['h'] / total
    e_pct = 100 * kc['e'] / total
    ke_ratio = kc['k'] / kc['e'] if kc['e'] > 0 else float('inf')
    print(f"  {s:<10} {k_pct:>7.1f}% {h_pct:>7.1f}% {e_pct:>7.1f}% {ke_ratio:>10.3f} {kc['k']:>8} {kc['h']:>8} {kc['e']:>8}")
    all_kernels += kc

total = sum(all_kernels.values())
print(f"  {'CORPUS':<10} {100*all_kernels['k']/total:>7.1f}% {100*all_kernels['h']/total:>7.1f}% {100*all_kernels['e']/total:>7.1f}% {all_kernels['k']/all_kernels['e']:>10.3f} {all_kernels['k']:>8} {all_kernels['h']:>8} {all_kernels['e']:>8}")

# Chi-square across all sections
sections_sorted = sorted(s for s in section_folios if s != 'T')  # exclude T (tiny)
kernel_matrix = []
for s in sections_sorted:
    kc = count_kernels(section_folios[s])
    kernel_matrix.append([kc['k'], kc['h'], kc['e']])
chi2, p, dof, _ = sp_stats.chi2_contingency(np.array(kernel_matrix))
print(f"\n  Chi-square (kernel x section, excl T): chi2={chi2:.1f}, dof={dof}, p={p:.2e}")
print()

# ===================================================================
# HAZARD PROFILE PER SECTION
# ===================================================================
print("-" * 80)
print("HAZARD PROFILE BY SECTION")
print("-" * 80)
print()

def count_hazard_sources(folio_set):
    """Count hazard-source events by hazard class."""
    class_counts = Counter()
    for folio in folio_set:
        toks = folio_tokens[folio]
        words = [t.word for t in toks]
        middles = []
        for w in words:
            m = morph.extract(w)
            middles.append(m.middle if m.middle else '')
        for i, mid in enumerate(middles):
            if mid in HAZARD_SOURCES:
                # Classify by best matching forbidden pair
                for (a, b), cls in HAZARD_CLASSES.items():
                    if a == mid:
                        class_counts[cls] += 1
                        break
    return class_counts

HAZ_ORDER = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING', 'RATE_MISMATCH', 'ENERGY_OVERSHOOT']

print(f"  {'Section':<10}", end='')
for hc in HAZ_ORDER:
    abbr = hc[:8]
    print(f" {abbr:>10}", end='')
print(f" {'Total':>8} {'Apparatus%':>10}")
print(f"  {'-'*10}", end='')
for _ in HAZ_ORDER:
    print(f" {'-'*10}", end='')
print(f" {'-'*8} {'-'*10}")

for s in sorted(section_folios.keys()):
    hc = count_hazard_sources(section_folios[s])
    total = sum(hc.values())
    if total == 0:
        continue
    print(f"  {s:<10}", end='')
    for h in HAZ_ORDER:
        pct = 100 * hc[h] / total if total > 0 else 0
        print(f" {pct:>9.1f}%", end='')
    apparatus = hc['CONTAINMENT_TIMING'] + hc['RATE_MISMATCH']
    app_pct = 100 * apparatus / total if total > 0 else 0
    print(f" {total:>8} {app_pct:>9.1f}%")

print()

# ===================================================================
# FOLIO-LEVEL PROFILES PER SECTION (medians)
# ===================================================================
print("-" * 80)
print("FOLIO-LEVEL PROFILE MEDIANS BY SECTION")
print("-" * 80)
print()

def compute_folio_profile(folio):
    """Compute operational profile for a single folio."""
    toks = folio_tokens[folio]
    if len(toks) < 20:
        return None

    kernels = Counter()
    lanes = Counter()
    link_count = 0
    hazard_sources = 0
    total_tokens = 0
    cc_triggers = Counter()

    words = [t.word for t in toks]
    middles = []

    for tok in toks:
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        total_tokens += 1

        # Kernel
        for c in m.middle:
            if c in ('k', 'h', 'e'):
                kernels[c] += 1

        # Lane
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            if lane:
                lanes[lane] += 1

        # LINK
        mid_kernel = decoder._get_middle_kernel(m.middle)
        if mid_kernel == 'LINK':
            link_count += 1

        # Hazard source
        if m.middle in HAZARD_SOURCES:
            hazard_sources += 1

        middles.append(m.middle)

    if total_tokens == 0:
        return None

    k_total = sum(kernels.values())
    lane_total = sum(lanes.values())

    # AXM self-transition (simplified: fraction of consecutive same-state pairs)
    states = []
    for tok in toks:
        m = morph.extract(tok.word)
        if m.middle:
            try:
                cls = decoder._token_to_class.get(m.middle)
                if cls is not None:
                    state = decoder.MACRO_STATE.get(cls)
                    if state:
                        states.append(state)
            except:
                pass

    axm_self = 0
    if len(states) > 1:
        same = sum(1 for i in range(len(states)-1) if states[i] == states[i+1])
        axm_self = same / (len(states) - 1)

    return {
        'k_pct': kernels['k'] / k_total if k_total > 0 else 0,
        'h_pct': kernels['h'] / k_total if k_total > 0 else 0,
        'e_pct': kernels['e'] / k_total if k_total > 0 else 0,
        'qo_pct': lanes.get('QO', 0) / lane_total if lane_total > 0 else 0,
        'chsh_pct': lanes.get('CHSH', 0) / lane_total if lane_total > 0 else 0,
        'link_pct': link_count / total_tokens,
        'haz_density': hazard_sources / total_tokens,
        'axm_self': axm_self,
        'tokens': total_tokens,
    }

DIMS = ['k_pct', 'h_pct', 'e_pct', 'qo_pct', 'chsh_pct', 'link_pct', 'haz_density', 'axm_self']
DIM_LABELS = {
    'k_pct': 'k kernel%', 'h_pct': 'h kernel%', 'e_pct': 'e kernel%',
    'qo_pct': 'QO lane%', 'chsh_pct': 'CHSH lane%', 'link_pct': 'LINK%',
    'haz_density': 'Haz density', 'axm_self': 'AXM self'
}

section_profiles = {}
for s in sorted(section_folios.keys()):
    profiles = []
    for f in section_folios[s]:
        p = compute_folio_profile(f)
        if p:
            profiles.append(p)
    section_profiles[s] = profiles

# Print header
print(f"  {'Dimension':<15}", end='')
for s in sorted(section_folios.keys()):
    name = SECTION_NAMES.get(s, s)
    n = len(section_profiles[s])
    print(f" {name+'('+str(n)+')':>12}", end='')
print()
print(f"  {'-'*15}", end='')
for s in sorted(section_folios.keys()):
    print(f" {'-'*12}", end='')
print()

for dim in DIMS:
    label = DIM_LABELS[dim]
    print(f"  {label:<15}", end='')
    for s in sorted(section_folios.keys()):
        vals = [p[dim] for p in section_profiles[s]]
        if vals:
            median = np.median(vals)
            print(f" {median:>11.3f}", end='')
        else:
            print(f" {'N/A':>11}", end='')
    print()

print()

# ===================================================================
# CC TRIGGER PROFILE PER SECTION
# ===================================================================
print("-" * 80)
print("CC TRIGGER PROFILE BY SECTION")
print("-" * 80)
print()

CC_TRIGGERS = {
    'daiin': 'FQ_FREQUENT', 'ol': 'CLOSE_FLOW', 'aiin': 'FQ_FREQUENT',
    'chol': 'CHSH_PRECISION', 'shol': 'CHSH_PRECISION',
    'chor': 'CHSH_PRECISION', 'shor': 'CHSH_PRECISION',
    'okaiin': 'QO_ENERGY', 'otaiin': 'QO_ENERGY', 'opaiin': 'QO_ENERGY',
    'qokaiin': 'QO_ENERGY', 'qotaiin': 'QO_ENERGY', 'qopaiin': 'QO_ENERGY',
    'okeey': 'QO_ENERGY', 'oteey': 'QO_ENERGY',
    'qokeey': 'QO_ENERGY', 'qoteey': 'QO_ENERGY',
    'okain': 'QO_ENERGY', 'otain': 'QO_ENERGY',
    'qokain': 'QO_ENERGY', 'qotain': 'QO_ENERGY',
}

def count_cc_triggers(folio_set):
    counts = Counter()
    for folio in folio_set:
        for tok in folio_tokens[folio]:
            if tok.word in CC_TRIGGERS:
                counts[CC_TRIGGERS[tok.word]] += 1
            # Also check by MIDDLE for broader coverage
            m = morph.extract(tok.word)
            if m.middle and m.prefix:
                lane = BTokenAnalysis._get_prefix_lane(m.prefix)
                mid_kernel = decoder._get_middle_kernel(m.middle)
                if mid_kernel == 'CC' or (m.middle in ('aiin', 'ain', 'aiiin')):
                    if lane == 'QO':
                        counts['QO_ENERGY'] += 1
                    elif lane == 'CHSH':
                        counts['CHSH_PRECISION'] += 1
    return counts

TRIGGER_ORDER = ['QO_ENERGY', 'CHSH_PRECISION', 'CLOSE_FLOW', 'FQ_FREQUENT']

print(f"  {'Section':<10}", end='')
for tc in TRIGGER_ORDER:
    abbr = tc[:10]
    print(f" {abbr:>12}", end='')
print(f" {'Total':>8}")
print(f"  {'-'*10}", end='')
for _ in TRIGGER_ORDER:
    print(f" {'-'*12}", end='')
print(f" {'-'*8}")

for s in sorted(section_folios.keys()):
    tc = count_cc_triggers(section_folios[s])
    total = sum(tc.values())
    if total == 0:
        continue
    print(f"  {s:<10}", end='')
    for t in TRIGGER_ORDER:
        pct = 100 * tc[t] / total if total > 0 else 0
        print(f" {pct:>11.1f}%", end='')
    print(f" {total:>8}")

print()

# ===================================================================
# REGIME COMPOSITION
# ===================================================================
print("-" * 80)
print("REGIME COMPOSITION BY SECTION")
print("-" * 80)
print()

print(f"  {'Section':<10} {'R1':>8} {'R2':>8} {'R3':>8} {'R4':>8} {'Folios':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for s in sorted(section_folios.keys()):
    folios = section_folios[s]
    regimes = Counter(folio_regime.get(f, '?') for f in folios)
    n = len(folios)
    print(f"  {s:<10}", end='')
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        pct = 100 * regimes.get(r, 0) / n if n > 0 else 0
        print(f" {pct:>7.0f}%", end='')
    print(f" {n:>8}")

print()

# ===================================================================
# PAIRWISE SECTION COMPARISONS (kernel, Mann-Whitney)
# ===================================================================
print("-" * 80)
print("PAIRWISE SECTION COMPARISONS (kernel k%, Mann-Whitney)")
print("-" * 80)
print()

sections = sorted(s for s in section_folios if len(section_profiles[s]) >= 3)
print(f"  {'Pair':<10} {'Med1':>8} {'Med2':>8} {'U':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*5}")

for i, s1 in enumerate(sections):
    for s2 in sections[i+1:]:
        v1 = [p['k_pct'] for p in section_profiles[s1]]
        v2 = [p['k_pct'] for p in section_profiles[s2]]
        if len(v1) < 3 or len(v2) < 3:
            continue
        u, p = sp_stats.mannwhitneyu(v1, v2, alternative='two-sided')
        med1 = np.median(v1)
        med2 = np.median(v2)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
        print(f"  {s1+'-'+s2:<10} {med1:>7.3f} {med2:>7.3f} {u:>8.0f} {p:>10.4f} {sig:>5}")

print()
print("=" * 80)
print("DONE")
print("=" * 80)

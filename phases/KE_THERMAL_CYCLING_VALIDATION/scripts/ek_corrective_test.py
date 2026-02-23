"""
Phase 437 Extension: ek as Corrective Thermal Response
======================================================
Tests whether ek (cool-first) is a corrective response to overheating,
while ke (heat-first) is normal thermal operation.

Hypothesis:
  ke = normal rhythm: "heat, then equilibrate"
  ek = corrective: "cool first, then resume heating" (skipped heat cycle)

Predictions:
  1. ek follows kch (precision monitoring) more than ke follows kch
  2. ek follows k-rich MIDDLEs more than ke follows k-rich MIDDLEs
  3. ek precedes ke more than ke precedes ek (correction -> resume)
  4. After ek, the system should return to ke (recovery complete)
  5. ek should concentrate in intensive sections / REGIME_1 (overheating risk)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

REGIME_PATH = ROOT / 'data' / 'regime_folio_mapping.json'
RESULTS_PATH = ROOT / 'phases' / 'KE_THERMAL_CYCLING_VALIDATION' / 'results' / 'ek_corrective_results.json'


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def kernel_content(middle):
    """Classify MIDDLE by dominant kernel."""
    if not middle:
        return 'NONE'
    k = sum(1 for ch in middle if ch == 'k')
    h = sum(1 for ch in middle if ch == 'h')
    e = sum(1 for ch in middle if ch == 'e')
    if k > e and k > h:
        return 'K_DOM'
    elif e > k and e > h:
        return 'E_DOM'
    elif h > k and h > e:
        return 'H_DOM'
    elif k == e and k > 0:
        return 'KE_TIED'
    else:
        return 'OTHER'


# =====================================================================
# LOAD DATA
# =====================================================================
print("EK CORRECTIVE THERMAL RESPONSE TEST")
print("=" * 70)

tx = Transcript()
morph = Morphology()

with open(REGIME_PATH) as f:
    regime_raw = json.load(f)
regime_data = regime_raw.get('regime_assignments', regime_raw)

# Build line-grouped tokens
line_groups = defaultdict(list)
for t in tx.currier_b():
    m = morph.extract(t.word)
    regime = regime_data.get(t.folio, {}).get('regime', 'UNK') if isinstance(regime_data, dict) else 'UNK'
    tok = {
        'word': t.word,
        'middle': m.middle if m.middle else '',
        'prefix': m.prefix if m.prefix else '',
        'suffix': m.suffix if m.suffix else '',
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'regime': regime,
    }
    line_groups[(t.folio, t.line)].append(tok)

# Identify ke, ek, kch tokens
def is_ke(mid):
    return mid == 'ke'

def is_ek(mid):
    return mid == 'ek'

def is_kch(mid):
    return mid and 'k' in mid and 'c' in mid and 'h' in mid

def is_ke_family(mid):
    """All atoms are k or e, with both present."""
    if not mid:
        return False
    return all(ch in {'k', 'e'} for ch in mid) and 'k' in mid and 'e' in mid

def has_k(mid):
    return mid and 'k' in mid

def has_h(mid):
    return mid and 'h' in mid

def has_e(mid):
    return mid and 'e' in mid


# =====================================================================
# T1: WHAT PRECEDES ke vs ek?
# =====================================================================
print(f"\n{'=' * 70}")
print("T1: WHAT PRECEDES ke vs ek?")
print("=" * 70)

# For each ke/ek token, record the preceding token's MIDDLE
ke_prev = []  # (prev_middle, prev_section, prev_regime)
ek_prev = []
other_prev = []

# Also track specific predecessor types
ke_after_kch = 0
ek_after_kch = 0
ke_after_k_rich = 0
ek_after_k_rich = 0
ke_after_e_rich = 0
ek_after_e_rich = 0
ke_after_h_containing = 0
ek_after_h_containing = 0
ke_total_with_prev = 0
ek_total_with_prev = 0

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(1, len(tokens)):
        curr = tokens[i]
        prev = tokens[i - 1]
        prev_mid = prev['middle']
        prev_kc = kernel_content(prev_mid)

        if is_ke(curr['middle']):
            ke_prev.append({'middle': prev_mid, 'kernel': prev_kc, 'section': curr['section'], 'regime': curr['regime']})
            ke_total_with_prev += 1
            if is_kch(prev_mid):
                ke_after_kch += 1
            if prev_kc == 'K_DOM':
                ke_after_k_rich += 1
            if prev_kc == 'E_DOM':
                ke_after_e_rich += 1
            if has_h(prev_mid):
                ke_after_h_containing += 1

        elif is_ek(curr['middle']):
            ek_prev.append({'middle': prev_mid, 'kernel': prev_kc, 'section': curr['section'], 'regime': curr['regime']})
            ek_total_with_prev += 1
            if is_kch(prev_mid):
                ek_after_kch += 1
            if prev_kc == 'K_DOM':
                ek_after_k_rich += 1
            if prev_kc == 'E_DOM':
                ek_after_e_rich += 1
            if has_h(prev_mid):
                ek_after_h_containing += 1

print(f"\n  ke tokens with predecessor: {ke_total_with_prev}")
print(f"  ek tokens with predecessor: {ek_total_with_prev}")

# Predecessor type comparison
print(f"\n  Predecessor type comparison:")
print(f"  {'Predecessor':<25} {'before ke':>12} {'before ek':>12} {'Prediction':>25}")
print(f"  {'-' * 24:<25} {'-' * 11:>12} {'-' * 11:>12} {'-' * 24:>25}")

ke_kch_rate = ke_after_kch / ke_total_with_prev if ke_total_with_prev else 0
ek_kch_rate = ek_after_kch / ek_total_with_prev if ek_total_with_prev else 0
print(f"  {'After kch (monitoring)':<25} {ke_kch_rate:>11.1%} {ek_kch_rate:>11.1%} {'ek > ke (corrective)':>25}")

ke_k_rate = ke_after_k_rich / ke_total_with_prev if ke_total_with_prev else 0
ek_k_rate = ek_after_k_rich / ek_total_with_prev if ek_total_with_prev else 0
print(f"  {'After K-dominant MIDDLE':<25} {ke_k_rate:>11.1%} {ek_k_rate:>11.1%} {'ek > ke (hot state)':>25}")

ke_e_rate = ke_after_e_rich / ke_total_with_prev if ke_total_with_prev else 0
ek_e_rate = ek_after_e_rich / ek_total_with_prev if ek_total_with_prev else 0
print(f"  {'After E-dominant MIDDLE':<25} {ke_e_rate:>11.1%} {ek_e_rate:>11.1%} {'ke > ek (cool state)':>25}")

ke_h_rate = ke_after_h_containing / ke_total_with_prev if ke_total_with_prev else 0
ek_h_rate = ek_after_h_containing / ek_total_with_prev if ek_total_with_prev else 0
print(f"  {'After h-containing':<25} {ke_h_rate:>11.1%} {ek_h_rate:>11.1%} {'ek > ke (monitoring)':>25}")

# Fisher exact tests
print(f"\n  Fisher exact tests (ke vs ek predecessor rates):")

# After kch
table_kch = [[ek_after_kch, ek_total_with_prev - ek_after_kch],
             [ke_after_kch, ke_total_with_prev - ke_after_kch]]
if all(sum(row) > 0 for row in table_kch):
    odds, p = stats.fisher_exact(table_kch, alternative='greater')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
    print(f"    ek after kch > ke after kch: OR={odds:.2f}, p={p:.4f} {sig}")

# After K-dominant
table_kdom = [[ek_after_k_rich, ek_total_with_prev - ek_after_k_rich],
              [ke_after_k_rich, ke_total_with_prev - ke_after_k_rich]]
if all(sum(row) > 0 for row in table_kdom):
    odds, p = stats.fisher_exact(table_kdom, alternative='greater')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
    print(f"    ek after K-DOM > ke after K-DOM: OR={odds:.2f}, p={p:.4f} {sig}")

# After E-dominant (ke should be higher)
table_edom = [[ke_after_e_rich, ke_total_with_prev - ke_after_e_rich],
              [ek_after_e_rich, ek_total_with_prev - ek_after_e_rich]]
if all(sum(row) > 0 for row in table_edom):
    odds, p = stats.fisher_exact(table_edom, alternative='greater')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
    print(f"    ke after E-DOM > ek after E-DOM: OR={odds:.2f}, p={p:.4f} {sig}")

# After h-containing
table_h = [[ek_after_h_containing, ek_total_with_prev - ek_after_h_containing],
           [ke_after_h_containing, ke_total_with_prev - ke_after_h_containing]]
if all(sum(row) > 0 for row in table_h):
    odds, p = stats.fisher_exact(table_h, alternative='greater')
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
    print(f"    ek after h-cont > ke after h-cont: OR={odds:.2f}, p={p:.4f} {sig}")

# Full predecessor kernel profile distribution
print(f"\n  Full predecessor kernel distribution:")
print(f"  {'Kernel':<10} {'before ke':>12} {'before ek':>12}")
ke_kernel_counts = Counter(p['kernel'] for p in ke_prev)
ek_kernel_counts = Counter(p['kernel'] for p in ek_prev)
all_kernels = sorted(set(list(ke_kernel_counts.keys()) + list(ek_kernel_counts.keys())))
for k in all_kernels:
    ke_n = ke_kernel_counts.get(k, 0)
    ek_n = ek_kernel_counts.get(k, 0)
    ke_pct = ke_n / len(ke_prev) if ke_prev else 0
    ek_pct = ek_n / len(ek_prev) if ek_prev else 0
    print(f"  {k:<10} {ke_pct:>11.1%} {ek_pct:>11.1%}")

# =====================================================================
# T2: WHAT FOLLOWS ke vs ek?
# =====================================================================
print(f"\n{'=' * 70}")
print("T2: WHAT FOLLOWS ke vs ek? (recovery pattern)")
print("=" * 70)

# After ek (corrective), does the system return to ke (normal)?
ke_next = Counter()
ek_next = Counter()
ke_next_middle = Counter()
ek_next_middle = Counter()

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        nxt = tokens[i + 1]
        nxt_mid = nxt['middle']

        if is_ke(curr['middle']):
            if is_ke(nxt_mid):
                ke_next['ke'] += 1
            elif is_ek(nxt_mid):
                ke_next['ek'] += 1
            elif is_ke_family(nxt_mid):
                ke_next['other_ke_fam'] += 1
            else:
                ke_next['non_ke_fam'] += 1
            ke_next_middle[nxt_mid] += 1

        elif is_ek(curr['middle']):
            if is_ke(nxt_mid):
                ek_next['ke'] += 1
            elif is_ek(nxt_mid):
                ek_next['ek'] += 1
            elif is_ke_family(nxt_mid):
                ek_next['other_ke_fam'] += 1
            else:
                ek_next['non_ke_fam'] += 1
            ek_next_middle[nxt_mid] += 1

ke_total_next = sum(ke_next.values())
ek_total_next = sum(ek_next.values())

print(f"\n  What follows ke (N={ke_total_next}):")
for cat in ['ke', 'ek', 'other_ke_fam', 'non_ke_fam']:
    n = ke_next.get(cat, 0)
    print(f"    -> {cat:<15}: {n:>4d} ({n/ke_total_next:.1%})" if ke_total_next else "")

print(f"\n  What follows ek (N={ek_total_next}):")
for cat in ['ke', 'ek', 'other_ke_fam', 'non_ke_fam']:
    n = ek_next.get(cat, 0)
    print(f"    -> {cat:<15}: {n:>4d} ({n/ek_total_next:.1%})" if ek_total_next else "")

# Key test: does ek -> ke more than ke -> ek? (correction -> resume)
ek_to_ke_rate = ek_next.get('ke', 0) / ek_total_next if ek_total_next else 0
ke_to_ek_rate = ke_next.get('ek', 0) / ke_total_next if ke_total_next else 0

print(f"\n  Correction -> Resume pattern:")
print(f"    ek -> ke (recovery complete): {ek_to_ke_rate:.1%}")
print(f"    ke -> ek (enter correction):  {ke_to_ek_rate:.1%}")
print(f"    Ratio: {ek_to_ke_rate / ke_to_ek_rate:.2f}x" if ke_to_ek_rate > 0 else "    Ratio: inf")

# Does ek -> ke happen more than expected by chance?
# Baseline: what fraction of all successors are ke?
all_next_middles = Counter()
for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(len(tokens) - 1):
        all_next_middles[tokens[i + 1]['middle']] += 1

total_successors = sum(all_next_middles.values())
ke_base_rate = all_next_middles.get('ke', 0) / total_successors
ek_base_rate = all_next_middles.get('ek', 0) / total_successors

print(f"\n  Baseline successor rates:")
print(f"    P(next=ke): {ke_base_rate:.1%}")
print(f"    P(next=ek): {ek_base_rate:.1%}")
print(f"    P(next=ke | after ek): {ek_to_ke_rate:.1%} ({ek_to_ke_rate/ke_base_rate:.1f}x baseline)")
print(f"    P(next=ek | after ke): {ke_to_ek_rate:.1%} ({ke_to_ek_rate/ek_base_rate:.1f}x baseline)" if ek_base_rate > 0 else "")

# Top 5 successors for each
print(f"\n  Top 5 successors of ke:")
for mid, cnt in ke_next_middle.most_common(5):
    print(f"    {mid:>8s}: {cnt:>4d} ({cnt/ke_total_next:.1%})")

print(f"\n  Top 5 successors of ek:")
for mid, cnt in ek_next_middle.most_common(5):
    print(f"    {mid:>8s}: {cnt:>4d} ({cnt/ek_total_next:.1%})")

# =====================================================================
# T3: ke vs ek DISTRIBUTION BY REGIME AND SECTION
# =====================================================================
print(f"\n{'=' * 70}")
print("T3: ke vs ek DISTRIBUTION BY REGIME AND SECTION")
print("=" * 70)

ke_regime = Counter()
ek_regime = Counter()
ke_section = Counter()
ek_section = Counter()

for key in sorted(line_groups.keys()):
    for tok in line_groups[key]:
        if is_ke(tok['middle']):
            ke_regime[tok['regime']] += 1
            ke_section[tok['section']] += 1
        elif is_ek(tok['middle']):
            ek_regime[tok['regime']] += 1
            ek_section[tok['section']] += 1

# ek/ke ratio by regime
print(f"\n  ek/ke ratio by REGIME:")
print(f"  {'REGIME':<12} {'ke':>6} {'ek':>6} {'ek/ke':>8} {'ek%':>8}")
regimes = sorted(set(list(ke_regime.keys()) + list(ek_regime.keys())))
regime_table = []
for reg in regimes:
    if reg == 'UNK':
        continue
    k = ke_regime.get(reg, 0)
    e = ek_regime.get(reg, 0)
    ratio = e / k if k > 0 else float('inf')
    ek_pct = e / (k + e) if (k + e) > 0 else 0
    regime_table.append([k, e])
    print(f"  {reg:<12} {k:>6d} {e:>6d} {ratio:>7.2f} {ek_pct:>7.1%}")

# Chi-squared: does ek/ke ratio differ by regime?
regime_arr = np.array([r for r in regime_table if sum(r) > 0])
if regime_arr.shape[0] >= 2:
    chi2, p_reg, dof, exp = stats.chi2_contingency(regime_arr)
    sig = '***' if p_reg < 0.001 else '**' if p_reg < 0.01 else '*' if p_reg < 0.05 else 'NS'
    print(f"\n  Chi-squared (ek/ke ratio x REGIME): {chi2:.2f}, df={dof}, p={p_reg:.4f} {sig}")

# ek/ke ratio by section
print(f"\n  ek/ke ratio by SECTION:")
print(f"  {'Section':<12} {'ke':>6} {'ek':>6} {'ek/ke':>8} {'ek%':>8}")
sections = sorted(set(list(ke_section.keys()) + list(ek_section.keys())))
section_table = []
for sec in sections:
    k = ke_section.get(sec, 0)
    e = ek_section.get(sec, 0)
    ratio = e / k if k > 0 else float('inf')
    ek_pct = e / (k + e) if (k + e) > 0 else 0
    section_table.append([k, e])
    print(f"  {sec:<12} {k:>6d} {e:>6d} {ratio:>7.2f} {ek_pct:>7.1%}")

section_arr = np.array([r for r in section_table if sum(r) > 0])
if section_arr.shape[0] >= 2:
    chi2_s, p_sec, dof_s, exp_s = stats.chi2_contingency(section_arr)
    sig = '***' if p_sec < 0.001 else '**' if p_sec < 0.01 else '*' if p_sec < 0.05 else 'NS'
    print(f"\n  Chi-squared (ek/ke ratio x SECTION): {chi2_s:.2f}, df={dof_s}, p={p_sec:.4f} {sig}")

# =====================================================================
# T4: WITHIN-LINE ke/ek SEQUENCING PATTERNS
# =====================================================================
print(f"\n{'=' * 70}")
print("T4: WITHIN-LINE ke/ek SEQUENCING")
print("=" * 70)

# For lines that contain both ke and ek, what is the typical order?
lines_with_both = 0
ke_before_ek = 0
ek_before_ke = 0
ke_ek_sequences = []

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    ke_positions = []
    ek_positions = []
    for i, tok in enumerate(tokens):
        if is_ke(tok['middle']):
            ke_positions.append(i)
        elif is_ek(tok['middle']):
            ek_positions.append(i)

    if ke_positions and ek_positions:
        lines_with_both += 1
        # Record the sequence of ke/ek events in this line
        events = []
        for i, tok in enumerate(tokens):
            if is_ke(tok['middle']):
                events.append(('ke', i))
            elif is_ek(tok['middle']):
                events.append(('ek', i))

        # Check pairwise ordering
        for j in range(len(events) - 1):
            if events[j][0] == 'ke' and events[j+1][0] == 'ek':
                ke_before_ek += 1
            elif events[j][0] == 'ek' and events[j+1][0] == 'ke':
                ek_before_ke += 1

        ke_ek_sequences.append(events)

print(f"\n  Lines containing both ke and ek: {lines_with_both}")
print(f"  ke -> ek transitions (enter correction): {ke_before_ek}")
print(f"  ek -> ke transitions (resume normal):    {ek_before_ke}")
if ke_before_ek > 0:
    print(f"  ek->ke / ke->ek ratio: {ek_before_ke / ke_before_ek:.2f}")

# Show some example sequences
print(f"\n  Example ke/ek sequences within lines (first 10):")
for seq in ke_ek_sequences[:10]:
    pattern = ' -> '.join(f'{ev[0]}@{ev[1]}' for ev in seq)
    print(f"    {pattern}")

# =====================================================================
# T5: FULL TRANSITION MATRIX (ke-family internal)
# =====================================================================
print(f"\n{'=' * 70}")
print("T5: ke-FAMILY TRANSITION MATRIX")
print("=" * 70)

# Among consecutive ke-family tokens, what are the transitions?
ke_fam_transitions = Counter()
ke_fam_total = 0

for key in sorted(line_groups.keys()):
    tokens = line_groups[key]
    for i in range(len(tokens) - 1):
        curr_mid = tokens[i]['middle']
        next_mid = tokens[i + 1]['middle']
        if is_ke_family(curr_mid) and is_ke_family(next_mid):
            ke_fam_transitions[(curr_mid, next_mid)] += 1
            ke_fam_total += 1

print(f"\n  Consecutive ke-family pairs: {ke_fam_total}")
print(f"\n  {'Source':>8} -> {'Target':>8}   {'Count':>6} {'%':>7}")
for (src, tgt), cnt in ke_fam_transitions.most_common(15):
    print(f"  {src:>8} -> {tgt:>8}   {cnt:>6d} {cnt/ke_fam_total:>6.1%}")

# =====================================================================
# VERDICT
# =====================================================================
print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

print(f"\n  Hypothesis: ek = corrective response to overheating")
print(f"             ke = normal thermal operation")

# Summarize key findings
print(f"\n  1. Predecessor asymmetry:")
print(f"     ek after kch: {ek_kch_rate:.1%} vs ke after kch: {ke_kch_rate:.1%}")
print(f"     ek after K-DOM: {ek_k_rate:.1%} vs ke after K-DOM: {ke_k_rate:.1%}")
print(f"     ek after E-DOM: {ek_e_rate:.1%} vs ke after E-DOM: {ke_e_rate:.1%}")

print(f"\n  2. Successor asymmetry:")
print(f"     ek -> ke (recovery): {ek_to_ke_rate:.1%} ({ek_to_ke_rate/ke_base_rate:.1f}x baseline)")
print(f"     ke -> ek (enter correction): {ke_to_ek_rate:.1%} ({ke_to_ek_rate/ek_base_rate:.1f}x baseline)" if ek_base_rate > 0 else "")

print(f"\n  3. Within-line ordering:")
print(f"     ek -> ke: {ek_before_ke} (resume after correction)")
print(f"     ke -> ek: {ke_before_ek} (enter correction)")

# =====================================================================
# SAVE
# =====================================================================
results = {
    'ke_total': ke_total_with_prev,
    'ek_total': ek_total_with_prev,
    'T1_predecessor': {
        'ek_after_kch': ek_kch_rate,
        'ke_after_kch': ke_kch_rate,
        'ek_after_k_dom': ek_k_rate,
        'ke_after_k_dom': ke_k_rate,
        'ek_after_e_dom': ek_e_rate,
        'ke_after_e_dom': ke_e_rate,
    },
    'T2_successor': {
        'ek_to_ke_rate': ek_to_ke_rate,
        'ke_to_ek_rate': ke_to_ek_rate,
        'ke_baseline_rate': ke_base_rate,
        'ek_baseline_rate': ek_base_rate,
    },
    'T3_regime_section': {
        'regime_p': round(float(p_reg), 6) if 'p_reg' in dir() else None,
        'section_p': round(float(p_sec), 6) if 'p_sec' in dir() else None,
    },
    'T4_within_line': {
        'lines_with_both': lines_with_both,
        'ke_before_ek': ke_before_ek,
        'ek_before_ke': ek_before_ke,
    },
}

with open(RESULTS_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {RESULTS_PATH}")

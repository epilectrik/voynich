"""
A_RECORD_B_FILTERING Phase - Script 3: Instance Trace Analysis
Tests 9-12 (C690-C693)

Question: What does a filtered B folio actually look like?
Which lines survive? Does the program remain coherent?
What fails - MIDDLE, PREFIX, or SUFFIX?

Tests:
  T9:  Line-Level Legality Map (C690)
  T10: Program Coherence Under Filtering (C691)
  T11: Failure Mode Distribution (C692)
  T12: Usability Gradient (C693)
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

# ── Load data ──
print("=" * 70)
print("A_RECORD_B_FILTERING - Script 3: Instance Trace Analysis")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
    cmap = json.load(f)
token_to_class = cmap['token_to_class']

with open(PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json') as f:
    regime_map = json.load(f)
folio_to_regime = {}
for regime, folios in regime_map.items():
    for f_name in folios:
        folio_to_regime[f_name] = regime

# ── Build B inventory ──
print("\nBuilding B token inventory...")
b_tokens = {}
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

# ── Build B folio structure: folio -> [(line_num, [token_words])] ──
print("Building B folio line structure...")
folio_lines = defaultdict(lambda: defaultdict(list))  # folio -> line -> [words]
for token in tx.currier_b():
    folio_lines[token.folio][token.line].append(token.word)

# Compute folio stats
folio_stats = {}
for folio, lines in folio_lines.items():
    n_lines = len(lines)
    n_tokens = sum(len(words) for words in lines.values())
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    folio_stats[folio] = {'n_lines': n_lines, 'n_tokens': n_tokens, 'regime': regime}

print(f"  B folios: {len(folio_stats)}")

# ── Build A record profiles + filtering ──
print("Building A record profiles and filtering...")
record_profiles = []

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

    legal_classes = frozenset(b_token_class[t] for t in legal if t in b_token_class)

    record_profiles.append({
        'folio': record.folio,
        'line': record.line,
        'composition': record.composition,
        'pp_middle_count': len(pp_middles),
        'pp_prefixes': pp_prefixes,
        'pp_middles': pp_middles,
        'pp_suffixes': pp_suffixes,
        'legal_tokens': legal,
        'legal_classes': legal_classes,
        'n_classes': len(legal_classes),
    })

n_records = len(record_profiles)
print(f"  Records: {n_records}")

# ── Select 8 representative A records ──
print("\nSelecting 8 representative A records...")

# Sort by PP MIDDLE count for selection
by_pp = sorted(record_profiles, key=lambda r: r['pp_middle_count'])
by_classes = sorted(record_profiles, key=lambda r: r['n_classes'])

# Selection
def pick_by_pp(target, profiles=by_pp):
    """Pick record closest to target PP count."""
    return min(profiles, key=lambda r: abs(r['pp_middle_count'] - target))

def pick_by_comp(comp):
    """Pick first record with given composition."""
    for r in record_profiles:
        if r['composition'] == comp and r['n_classes'] > 0:
            return r
    # fallback: any with that composition
    for r in record_profiles:
        if r['composition'] == comp:
            return r
    return None

# PP MIDDLE stats for targeting
pp_counts = [r['pp_middle_count'] for r in record_profiles]
pp_median = np.median(pp_counts)
pp_p95 = np.percentile(pp_counts, 95)

selected_records = {}

# Minimal-PP: lowest PP count (0-1)
minimal = [r for r in by_pp if r['pp_middle_count'] <= 1]
if minimal:
    selected_records['Minimal-PP'] = minimal[0]
else:
    selected_records['Minimal-PP'] = by_pp[0]

# Low-PP: PP ~2-3
low = [r for r in by_pp if 2 <= r['pp_middle_count'] <= 3]
selected_records['Low-PP'] = low[len(low)//2] if low else pick_by_pp(2)

# Median-PP
selected_records['Median-PP'] = pick_by_pp(pp_median)

# High-PP: top 5%
high = [r for r in by_pp if r['pp_middle_count'] >= pp_p95]
selected_records['High-PP'] = high[len(high)//2] if high else by_pp[-1]

# PURE_RI
pure_ri = pick_by_comp('PURE_RI')
if pure_ri:
    selected_records['PURE_RI'] = pure_ri
else:
    selected_records['PURE_RI'] = by_pp[0]  # fallback

# PURE_PP
pure_pp = pick_by_comp('PURE_PP')
if pure_pp:
    selected_records['PURE_PP'] = pure_pp

# Max-classes (least restrictive)
for r in reversed(by_classes):
    if r['n_classes'] > 0:
        selected_records['Max-classes'] = r
        break

# Min-classes (most restrictive, > 0)
for r in by_classes:
    if r['n_classes'] > 0:
        selected_records['Min-classes'] = r
        break

print(f"\n  Selected {len(selected_records)} representative records:")
for name, rec in selected_records.items():
    print(f"    {name:<14}: {rec['folio']}:{rec['line']}, PP={rec['pp_middle_count']}, "
          f"classes={rec['n_classes']}, comp={rec['composition']}")

# ── Select 4 representative B folios ──
print("\nSelecting 4 representative B folios...")

selected_folios = {}

# Per-REGIME: pick median-length folio
for target_regime in ['REGIME_1', 'REGIME_2', 'REGIME_4']:
    regime_folios = [(f, s) for f, s in folio_stats.items() if s['regime'] == target_regime]
    if regime_folios:
        regime_folios.sort(key=lambda x: x[1]['n_lines'])
        mid_idx = len(regime_folios) // 2
        folio_name = regime_folios[mid_idx][0]
        selected_folios[target_regime] = folio_name

# Largest folio
largest = max(folio_stats.items(), key=lambda x: x[1]['n_lines'])
selected_folios['Largest'] = largest[0]

print(f"\n  Selected {len(selected_folios)} representative folios:")
for name, folio in selected_folios.items():
    s = folio_stats[folio]
    print(f"    {name:<12}: {folio}, {s['n_lines']} lines, {s['n_tokens']} tokens, {s['regime']}")

# ════════════════════════════════════════════════════════════════
# TEST 9: Line-Level Legality Map (C690)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 9: LINE-LEVEL LEGALITY MAP (C690)")
print("=" * 70)

pairing_results = {}

for rec_name, rec in selected_records.items():
    legal_set = rec['legal_tokens']

    for fol_name, fol_id in selected_folios.items():
        key = f"{rec_name}|{fol_name}"
        lines = folio_lines[fol_id]

        line_data = []
        for line_num in sorted(lines.keys()):
            words = lines[line_num]
            total = len(words)
            legal_count = sum(1 for w in words if w in legal_set)
            legal_frac = legal_count / total if total > 0 else 0

            # Roles of legal tokens
            legal_roles = set()
            for w in words:
                if w in legal_set and w in b_token_class:
                    cls = b_token_class[w]
                    if cls in CLASS_TO_ROLE:
                        legal_roles.add(CLASS_TO_ROLE[cls])

            line_data.append({
                'line': line_num,
                'total': total,
                'legal': legal_count,
                'frac': legal_frac,
                'roles': sorted(legal_roles),
            })

        n_lines = len(line_data)
        mean_frac = np.mean([d['frac'] for d in line_data]) if line_data else 0
        empty_lines = sum(1 for d in line_data if d['legal'] == 0)
        thin_lines = sum(1 for d in line_data if 0 < d['legal'] <= 2)

        pairing_results[key] = {
            'record': f"{rec['folio']}:{rec['line']}",
            'folio': fol_id,
            'rec_name': rec_name,
            'fol_name': fol_name,
            'n_lines': n_lines,
            'mean_legality': float(mean_frac),
            'empty_lines': empty_lines,
            'empty_pct': 100 * empty_lines / n_lines if n_lines > 0 else 0,
            'thin_lines': thin_lines,
            'line_data': line_data,
        }

# Print summary
print(f"\n  {'Pairing':<35} {'Lines':>5} {'MeanLeg':>8} {'Empty':>6} {'Thin':>5}")
print("  " + "-" * 65)
for key in sorted(pairing_results.keys()):
    p = pairing_results[key]
    print(f"  {key:<35} {p['n_lines']:>5} {p['mean_legality']:>7.1%} "
          f"{p['empty_lines']:>5}({p['empty_pct']:>4.0f}%) {p['thin_lines']:>5}")

# Positional analysis: does legality vary with line position?
print("\n  Positional analysis (legality vs normalized position):")
all_fracs = []
all_npos = []
for key, p in pairing_results.items():
    n = p['n_lines']
    for i, ld in enumerate(p['line_data']):
        npos = (i + 0.5) / n if n > 0 else 0.5
        all_fracs.append(ld['frac'])
        all_npos.append(npos)

if len(all_fracs) > 10:
    rho, p_val = scipy_stats.spearmanr(all_npos, all_fracs)
    print(f"    Spearman rho = {rho:.4f}, p = {p_val:.4g}")
else:
    rho, p_val = 0, 1
    print(f"    Insufficient data for correlation")

# ════════════════════════════════════════════════════════════════
# TEST 10: Program Coherence Under Filtering (C691)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 10: PROGRAM COHERENCE UNDER FILTERING (C691)")
print("=" * 70)

# Operational completeness: line has at least one token from:
#   - setup group (CC or AX)
#   - work group (EN or FQ)
#   - close group (FL or CC)

SETUP_ROLES = {'CC', 'AX'}
WORK_ROLES = {'EN', 'FQ'}
CLOSE_ROLES = {'FL', 'CC'}

coherence_results = {}
for key, p in pairing_results.items():
    complete_lines = 0
    has_setup_lines = 0
    has_work_lines = 0
    has_close_lines = 0

    for ld in p['line_data']:
        roles = set(ld['roles'])
        has_setup = bool(roles & SETUP_ROLES)
        has_work = bool(roles & WORK_ROLES)
        has_close = bool(roles & CLOSE_ROLES)
        if has_setup:
            has_setup_lines += 1
        if has_work:
            has_work_lines += 1
        if has_close:
            has_close_lines += 1
        if has_setup and has_work and has_close:
            complete_lines += 1

    n = p['n_lines']
    # Maximum consecutive empty/thin lines
    max_gap = 0
    current_gap = 0
    for ld in p['line_data']:
        if ld['legal'] <= 2:
            current_gap += 1
            max_gap = max(max_gap, current_gap)
        else:
            current_gap = 0

    coherence_results[key] = {
        'complete_frac': complete_lines / n if n > 0 else 0,
        'setup_frac': has_setup_lines / n if n > 0 else 0,
        'work_frac': has_work_lines / n if n > 0 else 0,
        'close_frac': has_close_lines / n if n > 0 else 0,
        'max_gap': max_gap,
    }

print(f"\n  {'Pairing':<35} {'Complete':>8} {'Setup':>6} {'Work':>6} {'Close':>6} {'MaxGap':>7}")
print("  " + "-" * 75)
for key in sorted(coherence_results.keys()):
    c = coherence_results[key]
    print(f"  {key:<35} {c['complete_frac']:>7.1%} {c['setup_frac']:>5.1%} "
          f"{c['work_frac']:>5.1%} {c['close_frac']:>5.1%} {c['max_gap']:>7}")

# ════════════════════════════════════════════════════════════════
# TEST 11: Failure Mode Distribution (C692)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 11: FAILURE MODE DISTRIBUTION (C692)")
print("=" * 70)

# For each illegal token in the 32 pairings, diagnose failure
overall_failures = Counter()  # 'MIDDLE', 'PREFIX', 'SUFFIX'
role_failures = defaultdict(Counter)  # role -> failure mode counter

for rec_name, rec in selected_records.items():
    pp_middles = rec['pp_middles']
    pp_prefixes = rec['pp_prefixes']
    pp_suffixes = rec['pp_suffixes']
    legal_set = rec['legal_tokens']

    for fol_name, fol_id in selected_folios.items():
        lines = folio_lines[fol_id]
        for line_num in sorted(lines.keys()):
            for w in lines[line_num]:
                if w in legal_set:
                    continue
                if w not in b_tokens:
                    continue

                pref, mid, suf = b_tokens[w]
                cls = b_token_class.get(w)
                role = CLASS_TO_ROLE.get(cls, 'UNK') if cls else 'UNK'

                # Diagnose failure
                if mid not in pp_middles:
                    mode = 'MIDDLE'
                elif pref is not None and pref not in pp_prefixes:
                    mode = 'PREFIX'
                elif suf is not None and suf not in pp_suffixes:
                    mode = 'SUFFIX'
                else:
                    mode = 'PASSTHROUGH'  # should not happen

                overall_failures[mode] += 1
                role_failures[role][mode] += 1

total_failures = sum(overall_failures.values())
print(f"\n  Total illegal token instances: {total_failures}")
print(f"\n  Overall failure decomposition:")
for mode in ['MIDDLE', 'PREFIX', 'SUFFIX', 'PASSTHROUGH']:
    count = overall_failures[mode]
    pct = 100 * count / total_failures if total_failures > 0 else 0
    print(f"    {mode:<12}: {count:>6} ({pct:>5.1f}%)")

print(f"\n  By role:")
print(f"  {'Role':<6} {'Total':>6} {'MIDDLE':>8} {'PREFIX':>8} {'SUFFIX':>8}")
print("  " + "-" * 40)
for role in ROLES + ['UNK']:
    rf = role_failures[role]
    total_r = sum(rf.values())
    if total_r == 0:
        continue
    mid_pct = 100 * rf['MIDDLE'] / total_r
    pre_pct = 100 * rf['PREFIX'] / total_r
    suf_pct = 100 * rf['SUFFIX'] / total_r
    print(f"  {role:<6} {total_r:>6} {mid_pct:>7.1f}% {pre_pct:>7.1f}% {suf_pct:>7.1f}%")

# ════════════════════════════════════════════════════════════════
# TEST 12: Usability Gradient (C693)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 12: USABILITY GRADIENT (C693)")
print("=" * 70)

usability_matrix = {}

for rec_name in selected_records:
    for fol_name in selected_folios:
        key = f"{rec_name}|{fol_name}"
        p = pairing_results[key]
        c = coherence_results[key]

        legality_frac = p['mean_legality']
        role_coverage = np.mean([c['setup_frac'], c['work_frac'], c['close_frac']])
        empty_rate = p['empty_pct'] / 100.0

        usability_matrix[key] = {
            'legality': round(float(legality_frac), 4),
            'role_coverage': round(float(role_coverage), 4),
            'empty_rate': round(float(empty_rate), 4),
            'composite': round(float(legality_frac * role_coverage * (1 - empty_rate)), 4),
        }

# Print matrix: records as rows, folios as columns
print(f"\n  Composite Usability (legality * role_coverage * (1 - empty_rate)):")
print(f"\n  {'Record':<16}", end="")
for fn in sorted(selected_folios.keys()):
    print(f" {fn:>12}", end="")
print()
print("  " + "-" * (16 + 13 * len(selected_folios)))

for rn in selected_records:
    print(f"  {rn:<16}", end="")
    for fn in sorted(selected_folios.keys()):
        key = f"{rn}|{fn}"
        u = usability_matrix[key]
        print(f" {u['composite']:>11.3f}", end="")
    print()

# Find best/worst
all_usab = [(k, v['composite']) for k, v in usability_matrix.items()]
all_usab.sort(key=lambda x: x[1])

worst = all_usab[0]
best = all_usab[-1]
# Dynamic range among non-zero
nonzero = [x for x in all_usab if x[1] > 0]

print(f"\n  Best:  {best[0]} = {best[1]:.4f}")
print(f"  Worst: {worst[0]} = {worst[1]:.4f}")
if nonzero:
    print(f"  Dynamic range (nonzero): {nonzero[-1][1]/nonzero[0][1]:.1f}x")

# Unusable folios (>50% empty lines)
unusable = [(k, v) for k, v in pairing_results.items() if v['empty_pct'] > 50]
print(f"\n  Pairings with >50% empty lines: {len(unusable)} / {len(pairing_results)}")
for k, v in unusable:
    print(f"    {k}: {v['empty_pct']:.0f}% empty")

# ════════════════════════════════════════════════════════════════
# Save results
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

# Strip non-serializable fields from line_data
pairing_serial = {}
for key, p in pairing_results.items():
    pairing_serial[key] = {
        'record': p['record'],
        'folio': p['folio'],
        'rec_name': p['rec_name'],
        'fol_name': p['fol_name'],
        'n_lines': p['n_lines'],
        'mean_legality': p['mean_legality'],
        'empty_lines': p['empty_lines'],
        'empty_pct': round(p['empty_pct'], 2),
        'thin_lines': p['thin_lines'],
    }

results = {
    'metadata': {
        'phase': 'A_RECORD_B_FILTERING',
        'script': 'instance_trace_analysis.py',
        'tests': 'T9-T12 (C690-C693)',
        'n_pairings': len(pairing_results),
        'selected_records': {name: f"{r['folio']}:{r['line']} (PP={r['pp_middle_count']}, "
                            f"classes={r['n_classes']}, comp={r['composition']})"
                            for name, r in selected_records.items()},
        'selected_folios': {name: f"{fol} ({folio_stats[fol]['n_lines']} lines, "
                           f"{folio_stats[fol]['regime']})"
                           for name, fol in selected_folios.items()},
    },
    'T9_legality_map': {
        'constraint': 'C690',
        'pairings': pairing_serial,
        'positional_correlation': {
            'spearman_rho': round(float(rho), 4),
            'p_value': float(p_val),
        },
    },
    'T10_program_coherence': {
        'constraint': 'C691',
        'pairings': {k: {
            'complete_frac': round(v['complete_frac'], 4),
            'setup_frac': round(v['setup_frac'], 4),
            'work_frac': round(v['work_frac'], 4),
            'close_frac': round(v['close_frac'], 4),
            'max_gap': v['max_gap'],
        } for k, v in coherence_results.items()},
    },
    'T11_failure_modes': {
        'constraint': 'C692',
        'total_failures': total_failures,
        'overall': {mode: overall_failures[mode] for mode in ['MIDDLE', 'PREFIX', 'SUFFIX', 'PASSTHROUGH']},
        'overall_pct': {mode: round(100 * overall_failures[mode] / total_failures, 2)
                       if total_failures > 0 else 0
                       for mode in ['MIDDLE', 'PREFIX', 'SUFFIX', 'PASSTHROUGH']},
        'by_role': {role: dict(role_failures[role]) for role in ROLES + ['UNK']
                    if sum(role_failures[role].values()) > 0},
    },
    'T12_usability_gradient': {
        'constraint': 'C693',
        'matrix': usability_matrix,
        'best': {'pairing': best[0], 'composite': best[1]},
        'worst': {'pairing': worst[0], 'composite': worst[1]},
        'unusable_count': len(unusable),
        'unusable_pairings': [k for k, v in unusable],
    },
}

out_path = RESULTS_DIR / 'instance_trace_analysis.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"  Saved: {out_path}")
print("\nDone.")

#!/usr/bin/env python3
"""
s1_aiin_family_census.py — Comprehensive census of the -aiin atom family across all systems.

Phase: AIIN_CROSS_SYSTEM
Purpose: Profile every token containing the ii+n atom subsequence (aiin family)
         and i+n without ii (ain family) across Currier A, B, and AZC.

Uses: scripts/voynich.py canonical library
"""

import sys
import io
import os
import json
from collections import Counter, defaultdict
from pathlib import Path

# Windows stdout encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RESULTS_DIR = REPO_ROOT / 'phases' / 'AIIN_CROSS_SYSTEM' / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. Collect all tokens per system with atomization
# ============================================================
def collect_system(name, token_iter):
    """Collect tokens from an iterator, atomize each, classify aiin/ain family."""
    records = []
    for tok in token_iter:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        a = morph.atomize(w)
        atom_chars = [c for c, _, _ in a.atoms]

        # Check for ii+n subsequence (aiin family)
        has_iin = False
        for idx in range(len(atom_chars) - 2):
            if atom_chars[idx] == 'i' and atom_chars[idx+1] == 'i' and atom_chars[idx+2] == 'n':
                has_iin = True
                break

        # Check for i+n but NOT ii+n (ain family)
        has_in_not_iin = False
        if not has_iin:
            for idx in range(len(atom_chars) - 1):
                if atom_chars[idx] == 'i' and atom_chars[idx+1] == 'n':
                    has_in_not_iin = True
                    break

        records.append({
            'word': w,
            'system': name,
            'folio': tok.folio,
            'section': tok.section,
            'line': tok.line,
            'line_initial': tok.line_initial,
            'prefix': a.prefix,
            'articulator': a.articulator,
            'is_headless': a.is_headless,
            'head': a.head,
            'pseudo_head': atom_chars[0] if a.is_headless and atom_chars else None,
            'atoms': atom_chars,
            'atom_roles': [(c, r) for c, r, _ in a.atoms],
            'i_depth': a.i_depth,
            'terminal': a.term,
            'terminal_opacity': a.terminal_opacity,
            'aiin_family': has_iin,
            'ain_family': has_in_not_iin,
        })
    return records


print("Loading and atomizing all tokens...")
all_records = {}

# Currier A — exclude labels and uncertain by default
a_tokens = list(collect_system('A', tx.currier_a()))
all_records['A'] = a_tokens
print(f"  Currier A: {len(a_tokens)} tokens")

# Currier B
b_tokens = list(collect_system('B', tx.currier_b()))
all_records['B'] = b_tokens
print(f"  Currier B: {len(b_tokens)} tokens")

# AZC — use azc() but filter out labels, empty, uncertain
azc_raw = []
for tok in tx.azc():
    if tok.is_label:
        continue
    if not tok.word.strip() or '*' in tok.word:
        continue
    azc_raw.append(tok)
azc_tokens = list(collect_system('AZC', iter(azc_raw)))
all_records['AZC'] = azc_tokens
print(f"  AZC: {len(azc_tokens)} tokens")

print()


# ============================================================
# Helper: print a frequency table
# ============================================================
def print_freq_table(counter, title, top_n=None, total=None):
    """Print a frequency table from a Counter."""
    print(f"\n  {title}")
    print(f"  {'Item':<25} {'Count':>8} {'%':>8}")
    print(f"  {'-'*25} {'-'*8} {'-'*8}")
    items = counter.most_common(top_n)
    for item, count in items:
        pct = 100.0 * count / total if total else 0
        label = str(item) if item is not None else '(none)'
        print(f"  {label:<25} {count:>8} {pct:>7.1f}%")
    shown = sum(c for _, c in items)
    if top_n and shown < sum(counter.values()):
        remaining = sum(counter.values()) - shown
        print(f"  {'(other)':<25} {remaining:>8} {100.0*remaining/total if total else 0:>7.1f}%")


# ============================================================
# 2. VALIDATION CHECKPOINTS
# ============================================================
print("=" * 70)
print("VALIDATION CHECKPOINTS")
print("=" * 70)

# daiin count in B and line-initial %
b_daiin = [r for r in b_tokens if r['word'] == 'daiin']
b_daiin_li = [r for r in b_daiin if r['line_initial']]
if b_daiin:
    li_pct = 100.0 * len(b_daiin_li) / len(b_daiin)
    print(f"  C557: daiin line-initial in B = {li_pct:.1f}% (expected ~27.7%)")
else:
    print("  C557: NO daiin found in B — ERROR")

# daiin A-enriched vs B
a_daiin = [r for r in a_tokens if r['word'] == 'daiin']
a_daiin_rate = len(a_daiin) / len(a_tokens) if a_tokens else 0
b_daiin_rate = len(b_daiin) / len(b_tokens) if b_tokens else 0
if b_daiin_rate > 0:
    enrichment = a_daiin_rate / b_daiin_rate
    print(f"  C241: daiin A-enrichment = {enrichment:.2f}x (expected ~1.62x)")
    print(f"         A: {len(a_daiin)}/{len(a_tokens)} = {100*a_daiin_rate:.2f}%")
    print(f"         B: {len(b_daiin)}/{len(b_tokens)} = {100*b_daiin_rate:.2f}%")

# daiin = 51.7% of DA marker class (C265)
a_da_prefix = [r for r in a_tokens if r['prefix'] == 'da']
if a_da_prefix:
    da_daiin = [r for r in a_da_prefix if r['word'] == 'daiin']
    da_pct = 100.0 * len(da_daiin) / len(a_da_prefix)
    print(f"  C265: daiin = {da_pct:.1f}% of DA-prefix class in A (expected ~51.7%)")

# daiin ~4.6% of A tokens
if a_tokens:
    a_daiin_pct = 100.0 * len(a_daiin) / len(a_tokens)
    print(f"  daiin = {a_daiin_pct:.1f}% of A tokens (expected ~4.6%)")

print()


# ============================================================
# 3. PER-SYSTEM FAMILY INVENTORY
# ============================================================
print("=" * 70)
print("PER-SYSTEM FAMILY INVENTORY")
print("=" * 70)

json_output = {'systems': {}, 'validation': {}, 'comparisons': {}}

for sys_name in ['A', 'B', 'AZC']:
    tokens = all_records[sys_name]
    total = len(tokens)
    aiin_fam = [r for r in tokens if r['aiin_family']]
    ain_fam = [r for r in tokens if r['ain_family']]

    print(f"\n--- {sys_name} ({total} tokens) ---")
    print(f"  aiin-family: {len(aiin_fam)} ({100.0*len(aiin_fam)/total:.2f}%)")
    print(f"  ain-family (no ii): {len(ain_fam)} ({100.0*len(ain_fam)/total:.2f}%)")

    # Bare aiin (no prefix)
    bare_aiin = [r for r in aiin_fam if r['word'] == 'aiin']
    print(f"  Bare 'aiin': {len(bare_aiin)} ({100.0*len(bare_aiin)/total:.2f}%)")

    # daiin
    daiin = [r for r in aiin_fam if r['word'] == 'daiin']
    print(f"  'daiin': {len(daiin)} ({100.0*len(daiin)/total:.2f}%)")

    # Other prefixed forms top 15
    word_counts = Counter(r['word'] for r in aiin_fam)
    other = {w: c for w, c in word_counts.items() if w not in ('aiin', 'daiin')}
    other_counter = Counter(other)
    print_freq_table(other_counter, f"Other aiin-family forms (top 15)", top_n=15, total=len(aiin_fam))

    # Headed vs headless
    headed = [r for r in aiin_fam if not r['is_headless']]
    headless = [r for r in aiin_fam if r['is_headless']]
    print(f"\n  Headed: {len(headed)} ({100.0*len(headed)/max(len(aiin_fam),1):.1f}%)")
    print(f"  Headless: {len(headless)} ({100.0*len(headless)/max(len(aiin_fam),1):.1f}%)")

    # Type/token ratio
    types = set(r['word'] for r in aiin_fam)
    print(f"  Types: {len(types)}, Tokens: {len(aiin_fam)}, TTR: {len(types)/max(len(aiin_fam),1):.3f}")

    json_output['systems'][sys_name] = {
        'total_tokens': total,
        'aiin_family_count': len(aiin_fam),
        'aiin_family_pct': round(100.0 * len(aiin_fam) / total, 3),
        'ain_family_count': len(ain_fam),
        'ain_family_pct': round(100.0 * len(ain_fam) / total, 3),
        'bare_aiin_count': len(bare_aiin),
        'daiin_count': len(daiin),
        'headed_count': len(headed),
        'headless_count': len(headless),
        'unique_types': len(types),
        'type_list': sorted(types),
        'word_freq': dict(word_counts.most_common()),
    }


# ============================================================
# 4. HEAD DOMAIN DISTRIBUTION WITHIN THE FAMILY
# ============================================================
print("\n" + "=" * 70)
print("HEAD DOMAIN DISTRIBUTION (aiin-family)")
print("=" * 70)

for sys_name in ['A', 'B', 'AZC']:
    tokens = all_records[sys_name]
    aiin_fam = [r for r in tokens if r['aiin_family']]

    headed = [r for r in aiin_fam if not r['is_headless']]
    headless = [r for r in aiin_fam if r['is_headless']]

    head_counter = Counter(r['head'] for r in headed)
    pseudo_counter = Counter(r['pseudo_head'] for r in headless)

    print(f"\n--- {sys_name} ---")
    print_freq_table(head_counter, "HEAD atoms (headed tokens)", total=len(headed) if headed else 1)
    print_freq_table(pseudo_counter, "PSEUDO_HEAD atoms (headless tokens)", total=len(headless) if headless else 1)

    # Overall HEAD distribution for the system
    all_headed = [r for r in tokens if not r['is_headless']]
    overall_head = Counter(r['head'] for r in all_headed)
    print_freq_table(overall_head, f"Overall HEAD distribution ({sys_name})", top_n=10, total=len(all_headed) if all_headed else 1)

    json_output['systems'][sys_name]['aiin_head_dist'] = dict(head_counter)
    json_output['systems'][sys_name]['aiin_pseudo_head_dist'] = dict(pseudo_counter)
    json_output['systems'][sys_name]['overall_head_dist'] = dict(overall_head.most_common(10))


# ============================================================
# 5. PREFIX COMPOSITION PER SYSTEM
# ============================================================
print("\n" + "=" * 70)
print("PREFIX COMPOSITION (aiin-family)")
print("=" * 70)

prefix_tables = {}
for sys_name in ['A', 'B', 'AZC']:
    aiin_fam = [r for r in all_records[sys_name] if r['aiin_family']]
    prefix_counter = Counter(r['prefix'] if r['prefix'] else '(none)' for r in aiin_fam)
    prefix_tables[sys_name] = prefix_counter

    print(f"\n--- {sys_name} ---")
    print_freq_table(prefix_counter, "PREFIX frequency", total=len(aiin_fam) if aiin_fam else 1)

    json_output['systems'][sys_name]['aiin_prefix_dist'] = dict(prefix_counter)

# Chi-squared test: prefix composition across A vs B
print("\n  Chi-squared test: A vs B prefix composition")
try:
    from scipy.stats import chi2_contingency
    import numpy as np

    # Build contingency table from shared prefix set
    all_prefixes_set = sorted(set(list(prefix_tables['A'].keys()) + list(prefix_tables['B'].keys())))
    obs = []
    for sys_name in ['A', 'B']:
        row = [prefix_tables[sys_name].get(p, 0) for p in all_prefixes_set]
        obs.append(row)
    obs = np.array(obs)
    # Remove columns that are all zero
    mask = obs.sum(axis=0) > 0
    obs = obs[:, mask]
    chi2, p_val, dof, expected = chi2_contingency(obs)
    print(f"    chi2 = {chi2:.2f}, dof = {dof}, p = {p_val:.2e}")
    if p_val < 0.001:
        print("    => Highly significant difference in prefix composition between A and B")
    elif p_val < 0.05:
        print("    => Significant difference")
    else:
        print("    => No significant difference")
    json_output['comparisons']['prefix_chi2_A_vs_B'] = {'chi2': round(chi2, 3), 'p': float(f'{p_val:.6e}'), 'dof': dof}
except ImportError:
    print("    (scipy not available — skipping chi-squared test)")


# ============================================================
# 6. COMPARISON: aiin-family vs ain-family
# ============================================================
print("\n" + "=" * 70)
print("COMPARISON: aiin-family vs ain-family")
print("=" * 70)

for sys_name in ['A', 'B', 'AZC']:
    tokens = all_records[sys_name]
    total = len(tokens)
    aiin_fam = [r for r in tokens if r['aiin_family']]
    ain_fam = [r for r in tokens if r['ain_family']]

    print(f"\n--- {sys_name} ---")
    print(f"  aiin-family: {len(aiin_fam)} ({100.0*len(aiin_fam)/total:.2f}%)")
    print(f"  ain-family:  {len(ain_fam)} ({100.0*len(ain_fam)/total:.2f}%)")

    # HEAD distribution comparison
    aiin_heads = Counter()
    for r in aiin_fam:
        h = r['head'] if not r['is_headless'] else f"PH:{r['pseudo_head']}"
        aiin_heads[h] += 1

    ain_heads = Counter()
    for r in ain_fam:
        h = r['head'] if not r['is_headless'] else f"PH:{r['pseudo_head']}"
        ain_heads[h] += 1

    print_freq_table(aiin_heads, "aiin-family HEAD/PH distribution", top_n=10, total=len(aiin_fam) if aiin_fam else 1)
    print_freq_table(ain_heads, "ain-family HEAD/PH distribution", top_n=10, total=len(ain_fam) if ain_fam else 1)

    # Terminal comparison
    aiin_terms = Counter(r['terminal'] for r in aiin_fam)
    ain_terms = Counter(r['terminal'] for r in ain_fam)
    print_freq_table(aiin_terms, "aiin-family terminal atoms", total=len(aiin_fam) if aiin_fam else 1)
    print_freq_table(ain_terms, "ain-family terminal atoms", total=len(ain_fam) if ain_fam else 1)

    json_output['comparisons'][f'{sys_name}_aiin_vs_ain'] = {
        'aiin_count': len(aiin_fam),
        'ain_count': len(ain_fam),
        'aiin_terminals': dict(aiin_terms),
        'ain_terminals': dict(ain_terms),
    }


# ============================================================
# 7. SECTION DISTRIBUTION IN A
# ============================================================
print("\n" + "=" * 70)
print("SECTION DISTRIBUTION IN CURRIER A (aiin-family)")
print("=" * 70)

a_aiin = [r for r in all_records['A'] if r['aiin_family']]
a_all = all_records['A']

# Section counts
section_total = Counter(r['section'] for r in a_all)
section_aiin = Counter(r['section'] for r in a_aiin)

print(f"\n  {'Section':<10} {'Total':>8} {'aiin-fam':>10} {'Rate%':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*10} {'-'*8}")
for sec in sorted(section_total.keys()):
    t = section_total[sec]
    a = section_aiin.get(sec, 0)
    rate = 100.0 * a / t if t > 0 else 0
    print(f"  {sec:<10} {t:>8} {a:>10} {rate:>7.2f}%")

json_output['section_distribution_A'] = {
    sec: {
        'total': section_total[sec],
        'aiin_family': section_aiin.get(sec, 0),
        'rate_pct': round(100.0 * section_aiin.get(sec, 0) / section_total[sec], 3) if section_total[sec] > 0 else 0
    }
    for sec in sorted(section_total.keys())
}


# ============================================================
# 8. TYPE/TOKEN RATIO SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("TYPE/TOKEN RATIO SUMMARY (aiin-family)")
print("=" * 70)

print(f"\n  {'System':<10} {'Types':>8} {'Tokens':>8} {'TTR':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8}")
for sys_name in ['A', 'B', 'AZC']:
    aiin_fam = [r for r in all_records[sys_name] if r['aiin_family']]
    types = set(r['word'] for r in aiin_fam)
    ttr = len(types) / len(aiin_fam) if aiin_fam else 0
    print(f"  {sys_name:<10} {len(types):>8} {len(aiin_fam):>8} {ttr:>8.3f}")


# ============================================================
# SAVE JSON
# ============================================================
# Add validation checkpoints to JSON
json_output['validation'] = {
    'daiin_B_line_initial_pct': round(100.0 * len(b_daiin_li) / max(len(b_daiin), 1), 2),
    'daiin_A_enrichment': round(enrichment, 3) if b_daiin_rate > 0 else None,
    'daiin_A_count': len(a_daiin),
    'daiin_B_count': len(b_daiin),
    'daiin_A_pct': round(100.0 * len(a_daiin) / max(len(a_tokens), 1), 3),
}

output_path = RESULTS_DIR / 's1_aiin_family_census.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, indent=2, ensure_ascii=False)

print(f"\n\nResults saved to: {output_path}")
print("Done.")

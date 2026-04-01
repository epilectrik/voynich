"""
S4: Safety Architecture — Cross-System ii-Extension Analysis
=============================================================
Phase: AIIN_CROSS_SYSTEM
Purpose: Test whether the ii-extension safety routing mechanism (C1480-C1482)
         operates in Currier A and AZC, not just B.

Falsifiable prediction: If ii-tokens in A have the same HEAD/TERMINAL
morphological anatomy as B -> safety architecture is construction-layer.
If they diverge -> execution-layer only.

Constraints tested:
  C1480: i selects a-HEAD at 89%
  C1482: 94% n-terminal lock, 0% hazard for double-ii
  C1731: A ii-ratio 0.730 vs B 0.540
  C1732-C1733: ii in a-HEAD domain, ee in other domains
"""

import sys
import os
import json
from collections import Counter
from pathlib import Path

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Run from repo root
os.chdir(Path(__file__).resolve().parents[3])
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology
from scipy.stats import chi2_contingency

tx = Transcript()
morph = Morphology()

# --- Load tokens per system (H-only, no labels, no uncertain, no empty) ---
tokens_a = list(tx.currier_a())
tokens_b = list(tx.currier_b())
# AZC iterator doesn't exclude labels/uncertain by default, do it manually
tokens_azc = [t for t in tx.azc() if not t.is_label and not t.is_uncertain and t.word.strip()]

systems = {'A': tokens_a, 'B': tokens_b, 'AZC': tokens_azc}


def atomize_safe(word):
    """Atomize with error handling."""
    try:
        return morph.atomize(word)
    except Exception:
        return None


def get_head(atom_result):
    """Get HEAD char or 'headless'."""
    if atom_result is None:
        return 'ERROR'
    h = atom_result.head
    return h if h else 'headless'


def get_term(atom_result):
    """Get TERM char or 'none'."""
    if atom_result is None:
        return 'ERROR'
    t = atom_result.term
    return t if t else 'none'


def has_ii_n(atom_result):
    """Check if token contains ii+n pattern (aiin-family)."""
    if atom_result is None:
        return False
    chars = [c for c, _, _ in atom_result.atoms]
    has_ii = False
    for idx in range(len(chars) - 1):
        if chars[idx] == 'i' and chars[idx + 1] == 'i':
            has_ii = True
            break
    return has_ii and atom_result.term == 'n'


# --- Atomize all tokens per system ---
print("=" * 70)
print("S4: SAFETY ARCHITECTURE — CROSS-SYSTEM ii-EXTENSION ANALYSIS")
print("=" * 70)
print()

system_data = {}
for sname, token_list in systems.items():
    pairs = [(t.word, atomize_safe(t.word)) for t in token_list]
    system_data[sname] = pairs
    valid = sum(1 for _, a in pairs if a is not None)
    print(f"  {sname}: {len(token_list)} tokens, {valid} atomized successfully")

# Also keep raw token objects for B hazard analysis later
system_tokens = {sname: tlist for sname, tlist in systems.items()}

print()

# =====================================================================
# 1. ii-TOKEN CENSUS PER SYSTEM
# =====================================================================
print("=" * 70)
print("1. ii-TOKEN CENSUS PER SYSTEM")
print("=" * 70)

census = {}
for sname, pairs in system_data.items():
    counts = Counter()
    for word, atom in pairs:
        if atom is None:
            continue
        idepth = atom.i_depth
        if idepth == 0:
            counts['i0'] += 1
        elif idepth == 1:
            counts['i1'] += 1
        else:
            counts['i2+'] += 1
    total = sum(counts.values())
    census[sname] = {
        'total': total,
        'i0': counts['i0'],
        'i1': counts['i1'],
        'i2+': counts['i2+'],
        'ii_rate': counts['i2+'] / total if total else 0,
        'i1_rate': counts['i1'] / total if total else 0,
    }
    print(f"\n  {sname} (n={total}):")
    print(f"    i_depth=0:  {counts['i0']:>6} ({counts['i0']/total:.1%})")
    print(f"    i_depth=1:  {counts['i1']:>6} ({counts['i1']/total:.1%})")
    print(f"    i_depth>=2: {counts['i2+']:>6} ({counts['i2+']/total:.1%})")

# Validate C1731: A ii-ratio 0.730 vs B 0.540
# C1731 may refer to ratio among i-bearing tokens
print("\n  --- C1731 Validation ---")
for sname in ['A', 'B']:
    c = census[sname]
    i_bearing = c['i1'] + c['i2+']
    if i_bearing > 0:
        ii_among_i = c['i2+'] / i_bearing
        print(f"  {sname}: ii/(i1+ii) = {ii_among_i:.3f}  (ii among i-bearing tokens)")
    print(f"  {sname}: ii/total = {c['ii_rate']:.3f}  (ii among all tokens)")

# =====================================================================
# 2. n-TERMINAL LOCK RATE FOR ii-TOKENS PER SYSTEM
# =====================================================================
print("\n" + "=" * 70)
print("2. n-TERMINAL LOCK RATE FOR ii-TOKENS")
print("=" * 70)

nterm_data = {}
for sname, pairs in system_data.items():
    ii_terms = Counter()
    i1_terms = Counter()
    ii_total = 0
    i1_total = 0
    for word, atom in pairs:
        if atom is None:
            continue
        t = get_term(atom)
        if atom.i_depth >= 2:
            ii_terms[t] += 1
            ii_total += 1
        elif atom.i_depth == 1:
            i1_terms[t] += 1
            i1_total += 1

    ii_n_rate = ii_terms.get('n', 0) / ii_total if ii_total else 0
    i1_n_rate = i1_terms.get('n', 0) / i1_total if i1_total else 0
    nterm_data[sname] = {
        'ii_total': ii_total,
        'ii_n_count': ii_terms.get('n', 0),
        'ii_n_rate': ii_n_rate,
        'ii_terminal_dist': dict(ii_terms.most_common()),
        'i1_total': i1_total,
        'i1_n_count': i1_terms.get('n', 0),
        'i1_n_rate': i1_n_rate,
        'i1_terminal_dist': dict(i1_terms.most_common()),
    }

    print(f"\n  {sname} — ii-tokens (i_depth>=2, n={ii_total}):")
    print(f"    n-terminal: {ii_terms.get('n', 0)} ({ii_n_rate:.1%})")
    print(f"    Terminal dist: {dict(ii_terms.most_common(10))}")
    print(f"  {sname} — single-i tokens (i_depth=1, n={i1_total}):")
    print(f"    n-terminal: {i1_terms.get('n', 0)} ({i1_n_rate:.1%})")
    print(f"    Terminal dist: {dict(i1_terms.most_common(10))}")

# Chi-squared: n-terminal rate of ii-tokens in A vs B
print("\n  --- Null Hypothesis: ii-tokens in A have same n-terminal rate as B ---")
a_n = nterm_data['A']['ii_n_count']
a_other = nterm_data['A']['ii_total'] - a_n
b_n = nterm_data['B']['ii_n_count']
b_other = nterm_data['B']['ii_total'] - b_n

nterm_chi2_ab = None
if min(a_n + a_other, b_n + b_other) > 0:
    table = [[a_n, a_other], [b_n, b_other]]
    chi2, p, dof, expected = chi2_contingency(table)
    n_total_ab = sum(sum(r) for r in table)
    cramers_v = (chi2 / n_total_ab) ** 0.5 if n_total_ab > 0 else 0
    print(f"    Contingency table: A=[{a_n}, {a_other}], B=[{b_n}, {b_other}]")
    print(f"    Chi2={chi2:.4f}, p={p:.6f}, dof={dof}, Cramer's V={cramers_v:.4f}")
    print(f"    {'REJECT' if p < 0.05 else 'FAIL TO REJECT'} null at p<0.05")
    nterm_chi2_ab = {'chi2': chi2, 'p': p, 'dof': dof, 'cramers_v': cramers_v}
else:
    print("    Insufficient data for chi-squared test")

# =====================================================================
# 3. HEAD DISTRIBUTION OF ii-TOKENS PER SYSTEM
# =====================================================================
print("\n" + "=" * 70)
print("3. HEAD DISTRIBUTION BY i_depth AND SYSTEM")
print("=" * 70)

head_data = {}
for sname, pairs in system_data.items():
    head_by_depth = {0: Counter(), 1: Counter(), '2+': Counter()}
    for word, atom in pairs:
        if atom is None:
            continue
        h = get_head(atom)
        d = atom.i_depth
        if d == 0:
            head_by_depth[0][h] += 1
        elif d == 1:
            head_by_depth[1][h] += 1
        else:
            head_by_depth['2+'][h] += 1

    head_data[sname] = {}
    for depth_key in [0, 1, '2+']:
        ctr = head_by_depth[depth_key]
        total = sum(ctr.values())
        head_data[sname][str(depth_key)] = {
            'total': total,
            'dist': dict(ctr.most_common()),
            'a_rate': ctr.get('a', 0) / total if total else 0,
        }
        label = f"i_depth={depth_key}" if depth_key != '2+' else "i_depth>=2"
        a_rate = ctr.get('a', 0) / total if total else 0
        print(f"\n  {sname} -- {label} (n={total}):")
        print(f"    a-HEAD rate: {a_rate:.1%}")
        print(f"    Dist: {dict(ctr.most_common())}")

# C1480 validation: ii selects a-HEAD at 89%
print("\n  --- C1480 Validation: ii selects a-HEAD ---")
for sname in systems:
    d = head_data[sname]['2+']
    print(f"    {sname}: a-HEAD = {d['a_rate']:.1%} (n={d['total']})")

# Chi-squared: a-HEAD concentration of ii-tokens across A, B, AZC
print("\n  --- Chi2: a-HEAD of ii-tokens across systems ---")
rows = []
row_labels = []
head_chi2_systems = None
for sname in ['A', 'B', 'AZC']:
    d = head_data[sname]['2+']
    a_count = d['dist'].get('a', 0)
    other_count = d['total'] - a_count
    if d['total'] > 0:
        rows.append([a_count, other_count])
        row_labels.append(sname)

if len(rows) >= 2 and all(sum(r) > 0 for r in rows):
    chi2, p, dof, expected = chi2_contingency(rows)
    n_total = sum(sum(r) for r in rows)
    cramers_v = (chi2 / n_total) ** 0.5 if n_total > 0 else 0
    print(f"    Systems: {row_labels}")
    print(f"    Table: {rows}")
    print(f"    Chi2={chi2:.4f}, p={p:.6f}, dof={dof}, Cramer's V={cramers_v:.4f}")
    print(f"    {'REJECT' if p < 0.05 else 'FAIL TO REJECT'} null at p<0.05")
    head_chi2_systems = {'chi2': chi2, 'p': p, 'dof': dof, 'cramers_v': cramers_v,
                         'systems': row_labels, 'table': rows}
else:
    print("    Insufficient data")

# =====================================================================
# 4. ii vs ee COMPLEMENTARY DOMAINS (C1732-C1733)
# =====================================================================
print("\n" + "=" * 70)
print("4. ii vs ee COMPLEMENTARY DOMAINS")
print("=" * 70)

domain_data = {}
for sname, pairs in system_data.items():
    a_head_ii = 0
    a_head_ee = 0
    a_head_total = 0
    e_head_ii = 0
    e_head_ee = 0
    e_head_total = 0
    k_head_ii = 0
    k_head_ee = 0
    k_head_total = 0

    ee_heads = Counter()
    ee_total = 0

    for word, atom in pairs:
        if atom is None:
            continue
        h = get_head(atom)
        has_ii = atom.i_depth >= 2
        has_ee = atom.e_depth >= 2

        if h == 'a':
            a_head_total += 1
            if has_ii:
                a_head_ii += 1
            if has_ee:
                a_head_ee += 1
        elif h == 'e':
            e_head_total += 1
            if has_ii:
                e_head_ii += 1
            if has_ee:
                e_head_ee += 1
        elif h == 'k':
            k_head_total += 1
            if has_ii:
                k_head_ii += 1
            if has_ee:
                k_head_ee += 1

        if has_ee:
            ee_heads[h] += 1
            ee_total += 1

    domain_data[sname] = {
        'a_head_total': a_head_total,
        'a_head_ii_count': a_head_ii,
        'a_head_ii_rate': a_head_ii / a_head_total if a_head_total else 0,
        'a_head_ee_count': a_head_ee,
        'a_head_ee_rate': a_head_ee / a_head_total if a_head_total else 0,
        'e_head_total': e_head_total,
        'e_head_ii_count': e_head_ii,
        'e_head_ii_rate': e_head_ii / e_head_total if e_head_total else 0,
        'e_head_ee_count': e_head_ee,
        'e_head_ee_rate': e_head_ee / e_head_total if e_head_total else 0,
        'k_head_total': k_head_total,
        'k_head_ii_count': k_head_ii,
        'k_head_ii_rate': k_head_ii / k_head_total if k_head_total else 0,
        'k_head_ee_count': k_head_ee,
        'k_head_ee_rate': k_head_ee / k_head_total if k_head_total else 0,
        'ee_total': ee_total,
        'ee_head_dist': dict(ee_heads.most_common()),
    }

    print(f"\n  {sname}:")
    print(f"    a-HEAD tokens: {a_head_total}")
    if a_head_total:
        print(f"      uses ii: {a_head_ii} ({a_head_ii/a_head_total:.1%})")
        print(f"      uses ee: {a_head_ee} ({a_head_ee/a_head_total:.1%})")
    else:
        print(f"      uses ii: 0")
        print(f"      uses ee: 0")
    print(f"    e-HEAD tokens: {e_head_total}")
    if e_head_total:
        print(f"      uses ii: {e_head_ii} ({e_head_ii/e_head_total:.1%})")
        print(f"      uses ee: {e_head_ee} ({e_head_ee/e_head_total:.1%})")
    else:
        print(f"      uses ii: 0")
        print(f"      uses ee: 0")
    print(f"    k-HEAD tokens: {k_head_total}")
    if k_head_total:
        print(f"      uses ii: {k_head_ii} ({k_head_ii/k_head_total:.1%})")
        print(f"      uses ee: {k_head_ee} ({k_head_ee/k_head_total:.1%})")
    else:
        print(f"      uses ii: 0")
        print(f"      uses ee: 0")
    print(f"    ee-token HEAD dist: {dict(ee_heads.most_common())}")

# =====================================================================
# 5. aiin-FAMILY SHARE OF ALL ii-TOKENS
# =====================================================================
print("\n" + "=" * 70)
print("5. aiin-FAMILY SHARE OF ALL ii-TOKENS")
print("=" * 70)

aiin_data = {}
for sname, pairs in system_data.items():
    ii_tokens = []
    aiin_count = 0
    non_aiin_ii = []

    for word, atom in pairs:
        if atom is None:
            continue
        if atom.i_depth >= 2:
            ii_tokens.append((word, atom))
            if has_ii_n(atom):
                aiin_count += 1
            else:
                non_aiin_ii.append((word, atom))

    total_ii = len(ii_tokens)
    aiin_rate = aiin_count / total_ii if total_ii else 0
    aiin_data[sname] = {
        'total_ii': total_ii,
        'aiin_count': aiin_count,
        'aiin_rate': aiin_rate,
        'non_aiin_count': len(non_aiin_ii),
        'non_aiin_examples': [w for w, _ in non_aiin_ii[:20]],
    }

    print(f"\n  {sname} -- ii-tokens: {total_ii}")
    print(f"    aiin-family (ii+n terminal): {aiin_count} ({aiin_rate:.1%})")
    if total_ii:
        print(f"    non-aiin ii: {len(non_aiin_ii)} ({len(non_aiin_ii)/total_ii:.1%})")
    else:
        print(f"    non-aiin ii: 0")
    if non_aiin_ii:
        examples = [w for w, _ in non_aiin_ii[:15]]
        print(f"    Non-aiin examples: {examples}")

# =====================================================================
# 6. NON-aiin ii-TOKENS SAFETY PROFILE
# =====================================================================
print("\n" + "=" * 70)
print("6. NON-aiin ii-TOKEN SAFETY PROFILE")
print("=" * 70)

nonaiin_data = {}
for sname, pairs in system_data.items():
    terms = Counter()
    heads = Counter()
    count = 0

    for word, atom in pairs:
        if atom is None:
            continue
        if atom.i_depth >= 2 and not has_ii_n(atom):
            count += 1
            terms[get_term(atom)] += 1
            heads[get_head(atom)] += 1

    nonaiin_data[sname] = {
        'count': count,
        'terminal_dist': dict(terms.most_common()),
        'head_dist': dict(heads.most_common()),
        'n_rate': terms.get('n', 0) / count if count else 0,
    }

    print(f"\n  {sname} -- non-aiin ii-tokens (n={count}):")
    print(f"    Terminal dist: {dict(terms.most_common())}")
    print(f"    HEAD dist: {dict(heads.most_common())}")
    if count:
        print(f"    n-terminal rate even here: {terms.get('n', 0)/count:.1%}")

# =====================================================================
# 7. HAZARD PARTICIPATION (B ONLY)
# =====================================================================
print("\n" + "=" * 70)
print("7. HAZARD PARTICIPATION (B ONLY -- frame_hazard via RecordAnalyzer)")
print("=" * 70)

from scripts.voynich import BFolioDecoder

hazard_results = {}
try:
    decoder = BFolioDecoder()

    hazard_ii = Counter()
    hazard_nonii = Counter()
    ii_hazard_high = []
    total_ii_b = 0
    total_nonii_b = 0

    for word, atom_res in system_data['B']:
        if atom_res is None:
            continue
        try:
            bt = decoder.analyze_token(word)
            fh = bt.frame_hazard or 'UNKNOWN'
        except Exception:
            fh = 'ERROR'
        if atom_res.i_depth >= 2:
            hazard_ii[fh] += 1
            total_ii_b += 1
            if fh == 'HIGH':
                ii_hazard_high.append(word)
        else:
            hazard_nonii[fh] += 1
            total_nonii_b += 1

    print(f"\n  ii-tokens (i_depth>=2) hazard distribution (n={total_ii_b}):")
    for k, v in hazard_ii.most_common():
        pct = f" ({v/total_ii_b:.1%})" if total_ii_b else ""
        print(f"    {k}: {v}{pct}")
    if ii_hazard_high:
        print(f"    HIGH-hazard ii-tokens: {ii_hazard_high[:10]}")
    else:
        print(f"    No HIGH-hazard ii-tokens found (confirms C1482: 0% hazard)")

    print(f"\n  non-ii tokens hazard distribution (n={total_nonii_b}):")
    for k, v in hazard_nonii.most_common():
        pct = f" ({v/total_nonii_b:.1%})" if total_nonii_b else ""
        print(f"    {k}: {v}{pct}")

    hazard_results = {
        'ii_total': total_ii_b,
        'ii_hazard_dist': dict(hazard_ii.most_common()),
        'ii_high_count': hazard_ii.get('HIGH', 0),
        'ii_high_rate': hazard_ii.get('HIGH', 0) / total_ii_b if total_ii_b else 0,
        'nonii_total': total_nonii_b,
        'nonii_hazard_dist': dict(hazard_nonii.most_common()),
        'nonii_high_rate': hazard_nonii.get('HIGH', 0) / total_nonii_b if total_nonii_b else 0,
    }
except Exception as e:
    print(f"  BFolioDecoder hazard check failed: {e}")
    import traceback
    traceback.print_exc()
    hazard_results = {'error': str(e)}

# =====================================================================
# 8. A-SPECIFIC NULL HYPOTHESIS: ii vs non-ii HEAD profiles
# =====================================================================
print("\n" + "=" * 70)
print("8. A-SPECIFIC NULL HYPOTHESIS: ii vs non-ii HEAD PROFILES IN A")
print("=" * 70)

a_ii_heads = Counter()
a_nonii_heads = Counter()
for word, atom in system_data['A']:
    if atom is None:
        continue
    h = get_head(atom)
    if atom.i_depth >= 2:
        a_ii_heads[h] += 1
    else:
        a_nonii_heads[h] += 1

print(f"\n  A ii-tokens HEAD (n={sum(a_ii_heads.values())}):")
print(f"    {dict(a_ii_heads.most_common())}")
print(f"\n  A non-ii tokens HEAD (n={sum(a_nonii_heads.values())}):")
print(f"    {dict(a_nonii_heads.most_common())}")

# Chi-squared: ii vs non-ii HEAD profile in A
all_heads_a = sorted(set(list(a_ii_heads.keys()) + list(a_nonii_heads.keys())))
ii_row = [a_ii_heads.get(h, 0) for h in all_heads_a]
nonii_row = [a_nonii_heads.get(h, 0) for h in all_heads_a]

a_null_test = None
if sum(ii_row) > 0 and sum(nonii_row) > 0:
    table = [ii_row, nonii_row]
    chi2, p, dof, expected = chi2_contingency(table)
    n_total = sum(ii_row) + sum(nonii_row)
    cramers_v = (chi2 / n_total) ** 0.5 if n_total > 0 else 0
    print(f"\n  Chi2 test (ii vs non-ii HEAD distribution in A):")
    print(f"    Categories: {all_heads_a}")
    print(f"    ii-row:    {ii_row}")
    print(f"    nonii-row: {nonii_row}")
    print(f"    Chi2={chi2:.4f}, p={p:.2e}, dof={dof}, Cramer's V={cramers_v:.4f}")
    print(f"    {'REJECT' if p < 0.05 else 'FAIL TO REJECT'} null at p<0.05")
    if p < 0.05:
        print(f"    -> ii-tokens in A have DIFFERENT HEAD profile than non-ii tokens")
        print(f"    -> Safety encoding IS morphological (construction-layer evidence)")
    else:
        print(f"    -> ii-tokens in A have SAME HEAD profile as non-ii tokens")
        print(f"    -> No construction-layer evidence")
    a_null_test = {'chi2': chi2, 'p': p, 'dof': dof, 'cramers_v': cramers_v,
                   'categories': all_heads_a, 'ii_row': ii_row, 'nonii_row': nonii_row}
else:
    print("  Insufficient data for chi-squared test")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 70)
print("SUMMARY: CROSS-SYSTEM SAFETY ARCHITECTURE")
print("=" * 70)

for sname in ['A', 'B', 'AZC']:
    d = head_data[sname]['2+']
    n = nterm_data[sname]
    print(f"\n  {sname}:")
    print(f"    ii-token a-HEAD rate: {d['a_rate']:.1%} (n={d['total']})")
    print(f"    ii-token n-terminal rate: {n['ii_n_rate']:.1%} (n={n['ii_total']})")
    print(f"    aiin-family share: {aiin_data[sname]['aiin_rate']:.1%}")

# Verdict
a_ahead = head_data['A']['2+']['a_rate']
b_ahead = head_data['B']['2+']['a_rate']
a_nterm = nterm_data['A']['ii_n_rate']
b_nterm = nterm_data['B']['ii_n_rate']

print(f"\n  VERDICT:")
if abs(a_ahead - b_ahead) < 0.10 and abs(a_nterm - b_nterm) < 0.10:
    verdict = "CONSTRUCTION-LAYER: ii safety anatomy is shared across A and B"
    print(f"    {verdict}")
    print(f"    a-HEAD gap: {abs(a_ahead - b_ahead):.1%}, n-terminal gap: {abs(a_nterm - b_nterm):.1%}")
elif abs(a_ahead - b_ahead) < 0.10:
    verdict = "PARTIAL: HEAD anatomy shared, terminal diverges"
    print(f"    {verdict}")
else:
    verdict = "EXECUTION-LAYER: ii anatomy diverges between A and B"
    print(f"    {verdict}")

# =====================================================================
# SAVE JSON
# =====================================================================
output = {
    'script': 's4_safety_architecture.py',
    'phase': 'AIIN_CROSS_SYSTEM',
    'purpose': 'Test cross-system ii-extension safety routing (C1480-C1482)',
    'verdict': verdict,
    'census': census,
    'n_terminal_lock': nterm_data,
    'n_terminal_chi2_ab': nterm_chi2_ab,
    'head_distribution': {
        sname: {
            depth: {
                'total': head_data[sname][depth]['total'],
                'a_rate': head_data[sname][depth]['a_rate'],
                'dist': head_data[sname][depth]['dist'],
            }
            for depth in ['0', '1', '2+']
        }
        for sname in systems
    },
    'head_chi2_across_systems': head_chi2_systems,
    'complementary_domains': domain_data,
    'aiin_family': aiin_data,
    'non_aiin_ii_profile': nonaiin_data,
    'hazard_participation_b': hazard_results,
    'a_null_hypothesis_test': a_null_test,
}

out_path = Path('phases/AIIN_CROSS_SYSTEM/results/s4_safety_architecture.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n  Results saved to {out_path}")
print("  Done.")

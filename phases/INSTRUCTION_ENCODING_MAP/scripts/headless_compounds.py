"""
Phase 506 Test 1: Headless Compounds
======================================

Investigates the 467 compound MIDDLE types that lack a valid HEAD atom
per C1393/C1394's HEAD + MOD* + TERM grammar.

Headless = first atom is NOT in HEAD set {a, e, o} or FREE set {k, t}.

Tests:
  1. Headless Inventory — count, fraction, first-atom distribution, top 20
  2. Category Distribution — headed vs headless category profiles
  3. Abbreviation Test — do headed versions of headless compounds exist?
  4. PREFIX Context — do headless compounds cluster under specific PREFIXes?
  5. Positional Context — line position and paragraph header distribution
"""

import sys
import os
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1393 / C1394
HEAD_ONLY = {'a', 'o'}       # Always initial (86%+, 57%+)
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}  # Always terminal (71-99%)
FREE = {'k', 't'}             # HEAD when first, TERM when last
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}   # Medial modifiers
EXTENSIBLE = {'e', 'i'}       # Can repeat consecutively (C1197)

# Combined: atoms that can legally head a compound
HEAD_SET = HEAD_ONLY | FREE | {'e'}   # e can be HEAD (e-initial very common)

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}


# --- Atom decomposition (from instruction_map.py) -----------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms, respecting extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch in EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def is_compound(middle):
    """Check if a MIDDLE has 2+ atoms (compound)."""
    return len(atomize(middle)) >= 2


def first_atom_base(middle):
    """Get the base character of the first atom."""
    atoms = atomize(middle)
    if not atoms:
        return None
    return atoms[0][0]  # First char of first atom (handles 'ee', 'eee')


def is_headless(middle):
    """Check if a compound MIDDLE lacks a valid HEAD atom."""
    if not is_compound(middle):
        return False
    base = first_atom_base(middle)
    return base not in HEAD_SET


# --- Data Loading -------------------------------------------------

def load_data():
    """Load all Currier B tokens with morphology, category, and position info."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    records = []
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        cat = cc.classify(m.middle) or 'UNKNOWN'
        records.append({
            'word': tok.word,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'category': cat,
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
        })

    return records


# === TEST 1: Headless Inventory ===================================

def test1_inventory(records):
    """Count headless vs headed compounds, first-atom distribution, top 20."""
    print("=" * 80)
    print("TEST 1: Headless Compound Inventory")
    print("=" * 80)

    # Aggregate by MIDDLE type
    mid_counts = Counter()
    for r in records:
        mid_counts[r['middle']] += 1

    # Partition into single-atom, headed compound, headless compound
    single_types, single_toks = 0, 0
    headed_types, headed_toks = 0, 0
    headless_types, headless_toks = 0, 0
    headless_mids = {}
    headed_mids = {}

    for mid, count in mid_counts.items():
        if not is_compound(mid):
            single_types += 1
            single_toks += count
        elif is_headless(mid):
            headless_types += 1
            headless_toks += count
            headless_mids[mid] = count
        else:
            headed_types += 1
            headed_toks += count
            headed_mids[mid] = count

    total_compound_types = headed_types + headless_types
    total_compound_toks = headed_toks + headless_toks

    print(f"\nPopulation overview:")
    print(f"  Single-atom MIDDLEs: {single_types} types, {single_toks} tokens")
    print(f"  Headed compounds:   {headed_types} types, {headed_toks} tokens")
    print(f"  Headless compounds: {headless_types} types, {headless_toks} tokens")
    print(f"\n  Headless fraction (types):  {headless_types}/{total_compound_types} = "
          f"{100*headless_types/total_compound_types:.1f}%")
    print(f"  Headless fraction (tokens): {headless_toks}/{total_compound_toks} = "
          f"{100*headless_toks/total_compound_toks:.1f}%")

    # First-atom distribution of headless compounds
    first_atom_dist = Counter()
    first_atom_toks = Counter()
    for mid, count in headless_mids.items():
        base = first_atom_base(mid)
        first_atom_dist[base] += 1
        first_atom_toks[base] += count

    print(f"\nFirst-atom distribution of headless compounds:")
    print(f"  {'Atom':<6} {'Types':>6} {'%types':>8} {'Tokens':>8} {'%tokens':>8}  Role       Gloss")
    for atom, cnt in first_atom_dist.most_common():
        role = 'MODIFIER' if atom in MOD_ONLY else 'TERMINAL' if atom in TERM_ONLY else '???'
        gloss = ATOM_GLOSS.get(atom, '?')
        print(f"  {atom:<6} {cnt:>6} {100*cnt/headless_types:>7.1f}% "
              f"{first_atom_toks[atom]:>8} {100*first_atom_toks[atom]/headless_toks:>7.1f}%  "
              f"{role:<10} {gloss}")

    # Top 20 headless compounds by token frequency
    print(f"\nTop 20 headless compounds by token frequency:")
    print(f"  {'MIDDLE':<12} {'Tokens':>7} {'Atoms':<20} {'Glosses':<35}")
    for mid, count in Counter(headless_mids).most_common(20):
        atoms = atomize(mid)
        atom_str = ' + '.join(atoms)
        gloss_str = ' + '.join(ATOM_GLOSS.get(a[0], '?') for a in atoms)
        print(f"  {mid:<12} {count:>7} {atom_str:<20} {gloss_str:<35}")

    return {
        'single_types': single_types, 'single_tokens': single_toks,
        'headed_types': headed_types, 'headed_tokens': headed_toks,
        'headless_types': headless_types, 'headless_tokens': headless_toks,
        'headless_type_fraction': headless_types / total_compound_types if total_compound_types else 0,
        'headless_token_fraction': headless_toks / total_compound_toks if total_compound_toks else 0,
        'first_atom_distribution': {a: {'types': first_atom_dist[a], 'tokens': first_atom_toks[a]}
                                    for a in first_atom_dist},
        'top20': [{'middle': mid, 'tokens': count, 'atoms': atomize(mid)}
                  for mid, count in Counter(headless_mids).most_common(20)],
        'headless_mids': headless_mids,
        'headed_mids': headed_mids,
    }


# === TEST 2: Category Distribution ================================

def test2_categories(records, t1_result):
    """Compare category profiles of headed vs headless compounds."""
    print("\n" + "=" * 80)
    print("TEST 2: Category Distribution — Headed vs Headless")
    print("=" * 80)

    headless_mids = set(t1_result['headless_mids'].keys())
    headed_mids = set(t1_result['headed_mids'].keys())

    # Gather token-level category counts
    headed_cats = Counter()
    headless_cats = Counter()
    for r in records:
        mid = r['middle']
        cat = r['category']
        if mid in headless_mids:
            headless_cats[cat] += 1
        elif mid in headed_mids:
            headed_cats[cat] += 1

    all_cats = sorted(set(headed_cats.keys()) | set(headless_cats.keys()))
    h_total = sum(headed_cats.values())
    hl_total = sum(headless_cats.values())

    print(f"\n  {'Category':<15} {'Headed':>7} {'%':>7}  {'Headless':>9} {'%':>7}  {'Ratio':>7}")
    contingency = []
    for cat in all_cats:
        hc = headed_cats.get(cat, 0)
        hlc = headless_cats.get(cat, 0)
        hp = 100 * hc / h_total if h_total else 0
        hlp = 100 * hlc / hl_total if hl_total else 0
        ratio = hlp / hp if hp > 0 else float('inf')
        print(f"  {cat:<15} {hc:>7} {hp:>6.1f}%  {hlc:>9} {hlp:>6.1f}%  {ratio:>6.2f}x")
        contingency.append([hc, hlc])

    # Chi-squared test
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    # Cramer's V
    n = sum(sum(row) for row in contingency)
    k = min(len(contingency), 2)
    v = (chi2 / (n * (k - 1))) ** 0.5 if n * (k - 1) > 0 else 0
    print(f"\n  Chi2 = {chi2:.1f}, p = {p:.2e}, dof = {dof}, Cramer's V = {v:.3f}")

    # Which categories are most enriched in headless?
    enriched = []
    for cat in all_cats:
        hp = headed_cats.get(cat, 0) / h_total if h_total else 0
        hlp = headless_cats.get(cat, 0) / hl_total if hl_total else 0
        ratio = hlp / hp if hp > 0 else float('inf')
        enriched.append((cat, ratio))
    enriched.sort(key=lambda x: -x[1])
    print(f"\n  Enrichment ranking (headless / headed):")
    for cat, ratio in enriched:
        direction = "ENRICHED" if ratio > 1.5 else "DEPLETED" if ratio < 0.67 else "similar"
        print(f"    {cat:<15} {ratio:.2f}x  {direction}")

    return {
        'headed_cats': dict(headed_cats),
        'headless_cats': dict(headless_cats),
        'chi2': chi2, 'p': p, 'cramers_v': v,
        'enrichment': {cat: r for cat, r in enriched},
    }


# === TEST 3: Abbreviation Test ====================================

def test3_abbreviation(records, t1_result):
    """For each headless compound, check if headed versions exist."""
    print("\n" + "=" * 80)
    print("TEST 3: Abbreviation Test — Do Headed Versions Exist?")
    print("=" * 80)

    headless_mids = t1_result['headless_mids']
    all_mid_counts = Counter()
    for r in records:
        all_mid_counts[r['middle']] += 1

    possible_heads = sorted(HEAD_SET)  # a, e, k, o, t

    results = []
    # Focus on headless compounds with 5+ tokens (reliable)
    frequent_headless = {m: c for m, c in headless_mids.items() if c >= 5}
    print(f"\n  Testing {len(frequent_headless)} headless compounds with 5+ tokens")
    print(f"\n  {'Headless':<12} {'H_tok':>6} {'Headed versions found':>40} {'H/(H+all_headed)':>18}")

    abbreviation_data = []
    for mid, hless_count in sorted(frequent_headless.items(), key=lambda x: -x[1]):
        headed_versions = {}
        for head_atom in possible_heads:
            candidate = head_atom + mid
            if candidate in all_mid_counts:
                headed_versions[candidate] = all_mid_counts[candidate]

        total_headed = sum(headed_versions.values())
        ratio = hless_count / (hless_count + total_headed) if (hless_count + total_headed) > 0 else 1.0

        if headed_versions:
            hv_str = ', '.join(f"{m}({c})" for m, c in sorted(headed_versions.items(), key=lambda x: -x[1]))
        else:
            hv_str = '(none)'

        print(f"  {mid:<12} {hless_count:>6} {hv_str:>40} {ratio:>17.3f}")

        abbreviation_data.append({
            'headless': mid,
            'headless_tokens': hless_count,
            'headed_versions': headed_versions,
            'total_headed_tokens': total_headed,
            'headless_fraction': ratio,
        })

    # Summary statistics
    has_headed = sum(1 for d in abbreviation_data if d['headed_versions'])
    no_headed = sum(1 for d in abbreviation_data if not d['headed_versions'])
    avg_ratio = sum(d['headless_fraction'] for d in abbreviation_data) / len(abbreviation_data) if abbreviation_data else 0

    print(f"\n  Summary (N={len(abbreviation_data)} headless with 5+ tokens):")
    print(f"    Has headed version: {has_headed} ({100*has_headed/len(abbreviation_data):.1f}%)")
    print(f"    No headed version:  {no_headed} ({100*no_headed/len(abbreviation_data):.1f}%)")
    print(f"    Mean headless fraction: {avg_ratio:.3f}")
    print(f"    (1.0 = no headed versions exist; 0.5 = equally common)")

    # Categorize: abbreviation (<0.5), dominant (>0.8), mixed
    abbrev_count = sum(1 for d in abbreviation_data if d['headed_versions'] and d['headless_fraction'] < 0.5)
    dominant_count = sum(1 for d in abbreviation_data if d['headless_fraction'] >= 0.8)
    mixed_count = len(abbreviation_data) - abbrev_count - dominant_count
    print(f"\n  Classification:")
    print(f"    Likely abbreviation (headless < 50% of total):   {abbrev_count}")
    print(f"    Headless dominant   (headless >= 80% of total):  {dominant_count}")
    print(f"    Mixed / ambiguous:                               {mixed_count}")

    return {
        'tested_count': len(abbreviation_data),
        'has_headed_version': has_headed,
        'no_headed_version': no_headed,
        'mean_headless_fraction': avg_ratio,
        'abbreviation_count': abbrev_count,
        'dominant_count': dominant_count,
        'mixed_count': mixed_count,
        'details': abbreviation_data[:30],  # Top 30 for JSON
    }


# === TEST 4: PREFIX Context =======================================

def test4_prefix_context(records, t1_result):
    """Compare PREFIX distribution for headed vs headless compounds."""
    print("\n" + "=" * 80)
    print("TEST 4: PREFIX Context — Headed vs Headless")
    print("=" * 80)

    headless_mids = set(t1_result['headless_mids'].keys())
    headed_mids = set(t1_result['headed_mids'].keys())

    headed_pfx = Counter()
    headless_pfx = Counter()
    for r in records:
        mid = r['middle']
        pfx = r['prefix'] or 'BARE'
        if mid in headless_mids:
            headless_pfx[pfx] += 1
        elif mid in headed_mids:
            headed_pfx[pfx] += 1

    all_pfx = sorted(set(headed_pfx.keys()) | set(headless_pfx.keys()),
                     key=lambda x: -(headed_pfx.get(x, 0) + headless_pfx.get(x, 0)))
    h_total = sum(headed_pfx.values())
    hl_total = sum(headless_pfx.values())

    print(f"\n  {'PREFIX':<10} {'Headed':>7} {'%':>7}  {'Headless':>9} {'%':>7}  {'Ratio':>7}")
    contingency = []
    for pfx in all_pfx[:20]:  # Top 20 prefixes
        hc = headed_pfx.get(pfx, 0)
        hlc = headless_pfx.get(pfx, 0)
        hp = 100 * hc / h_total if h_total else 0
        hlp = 100 * hlc / hl_total if hl_total else 0
        ratio = hlp / hp if hp > 0 else float('inf')
        print(f"  {pfx:<10} {hc:>7} {hp:>6.1f}%  {hlc:>9} {hlp:>6.1f}%  {ratio:>6.2f}x")
        contingency.append([hc, hlc])

    # Chi-squared for prefix distribution
    if len(contingency) >= 2:
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        n = sum(sum(row) for row in contingency)
        k = min(len(contingency), 2)
        v = (chi2 / (n * (k - 1))) ** 0.5 if n * (k - 1) > 0 else 0
        print(f"\n  Chi2 = {chi2:.1f}, p = {p:.2e}, Cramer's V = {v:.3f}")
    else:
        chi2, p, v = 0, 1, 0

    # BARE rate comparison
    bare_headed = 100 * headed_pfx.get('BARE', 0) / h_total if h_total else 0
    bare_headless = 100 * headless_pfx.get('BARE', 0) / hl_total if hl_total else 0
    print(f"\n  BARE rate: headed={bare_headed:.1f}%, headless={bare_headless:.1f}%")
    print(f"  BARE ratio (headless/headed): {bare_headless/bare_headed:.2f}x" if bare_headed > 0 else "")

    return {
        'headed_prefix_dist': dict(headed_pfx),
        'headless_prefix_dist': dict(headless_pfx),
        'chi2': chi2, 'p': p, 'cramers_v': v,
        'bare_rate_headed': bare_headed,
        'bare_rate_headless': bare_headless,
    }


# === TEST 5: Positional Context ===================================

def test5_position(records, t1_result):
    """Compare line position and paragraph position for headed vs headless."""
    print("\n" + "=" * 80)
    print("TEST 5: Positional Context — Headed vs Headless")
    print("=" * 80)

    headless_mids = set(t1_result['headless_mids'].keys())
    headed_mids = set(t1_result['headed_mids'].keys())

    # Build per-line token lists to compute normalized position
    # Group by (folio, line)
    line_groups = defaultdict(list)
    for i, r in enumerate(records):
        line_groups[(r['folio'], r['line'])].append(i)

    # Compute normalized position for each record
    for indices in line_groups.values():
        n = len(indices)
        for pos, idx in enumerate(indices):
            records[idx]['norm_pos'] = pos / (n - 1) if n > 1 else 0.5

    # Position distributions
    headed_positions = []
    headless_positions = []
    headed_initial, headed_final = 0, 0
    headless_initial, headless_final = 0, 0
    headed_par_initial, headless_par_initial = 0, 0
    headed_par_final, headless_par_final = 0, 0
    h_n, hl_n = 0, 0

    for r in records:
        mid = r['middle']
        if mid in headless_mids:
            headless_positions.append(r.get('norm_pos', 0.5))
            hl_n += 1
            if r['line_initial']:
                headless_initial += 1
            if r['line_final']:
                headless_final += 1
            if r['par_initial']:
                headless_par_initial += 1
            if r['par_final']:
                headless_par_final += 1
        elif mid in headed_mids:
            headed_positions.append(r.get('norm_pos', 0.5))
            h_n += 1
            if r['line_initial']:
                headed_initial += 1
            if r['line_final']:
                headed_final += 1
            if r['par_initial']:
                headed_par_initial += 1
            if r['par_final']:
                headed_par_final += 1

    # Mean position
    h_mean = sum(headed_positions) / len(headed_positions) if headed_positions else 0
    hl_mean = sum(headless_positions) / len(headless_positions) if headless_positions else 0

    print(f"\n  Line position statistics:")
    print(f"    {'Metric':<25} {'Headed':>10} {'Headless':>10}")
    print(f"    {'Mean normalized pos':<25} {h_mean:>10.3f} {hl_mean:>10.3f}")
    print(f"    {'Line-initial rate':<25} {100*headed_initial/h_n:>9.1f}% {100*headless_initial/hl_n:>9.1f}%")
    print(f"    {'Line-final rate':<25} {100*headed_final/h_n:>9.1f}% {100*headless_final/hl_n:>9.1f}%")
    print(f"    {'Par-initial rate':<25} {100*headed_par_initial/h_n:>9.1f}% {100*headless_par_initial/hl_n:>9.1f}%")
    print(f"    {'Par-final rate':<25} {100*headed_par_final/h_n:>9.1f}% {100*headless_par_final/hl_n:>9.1f}%")
    print(f"    {'N tokens':<25} {h_n:>10} {hl_n:>10}")

    # Mann-Whitney U for positional difference
    if headed_positions and headless_positions:
        u_stat, u_p = stats.mannwhitneyu(headed_positions, headless_positions, alternative='two-sided')
        print(f"\n  Mann-Whitney U = {u_stat:.0f}, p = {u_p:.2e}")
    else:
        u_stat, u_p = 0, 1

    # Position quintile comparison
    print(f"\n  Position quintile distribution:")
    def quintile_dist(positions, n_tok):
        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.001]
        labels = ['Q1(0-0.2)', 'Q2(0.2-0.4)', 'Q3(0.4-0.6)', 'Q4(0.6-0.8)', 'Q5(0.8-1.0)']
        counts = [0] * 5
        for p in positions:
            for i in range(5):
                if bins[i] <= p < bins[i + 1]:
                    counts[i] += 1
                    break
        return {labels[i]: 100 * counts[i] / len(positions) if positions else 0 for i in range(5)}

    h_quint = quintile_dist(headed_positions, h_n)
    hl_quint = quintile_dist(headless_positions, hl_n)
    print(f"    {'Quintile':<15} {'Headed':>8} {'Headless':>10}")
    for q in h_quint:
        print(f"    {q:<15} {h_quint[q]:>7.1f}% {hl_quint.get(q, 0):>9.1f}%")

    # Paragraph header test: is the token on the first line of a paragraph?
    # Use par_initial flag
    par_init_ratio_headed = headed_par_initial / h_n if h_n else 0
    par_init_ratio_headless = headless_par_initial / hl_n if hl_n else 0

    print(f"\n  Paragraph-initial enrichment:")
    print(f"    Headed:   {100*par_init_ratio_headed:.1f}%")
    print(f"    Headless: {100*par_init_ratio_headless:.1f}%")
    if par_init_ratio_headed > 0:
        print(f"    Ratio:    {par_init_ratio_headless/par_init_ratio_headed:.2f}x")

    return {
        'headed_mean_pos': h_mean,
        'headless_mean_pos': hl_mean,
        'headed_initial_rate': headed_initial / h_n if h_n else 0,
        'headless_initial_rate': headless_initial / hl_n if hl_n else 0,
        'headed_final_rate': headed_final / h_n if h_n else 0,
        'headless_final_rate': headless_final / hl_n if hl_n else 0,
        'headed_par_initial_rate': par_init_ratio_headed,
        'headless_par_initial_rate': par_init_ratio_headless,
        'mann_whitney_u': u_stat, 'mann_whitney_p': u_p,
        'headed_quintiles': h_quint,
        'headless_quintiles': hl_quint,
    }


# === MAIN =========================================================

def main():
    print("Phase 506 Test 1: Headless Compounds")
    print("=" * 80)
    print("Loading Currier B data...")

    records = load_data()
    print(f"  Loaded {len(records)} tokens\n")

    # Run tests
    t1 = test1_inventory(records)
    t2 = test2_categories(records, t1)
    t3 = test3_abbreviation(records, t1)
    t4 = test4_prefix_context(records, t1)
    t5 = test5_position(records, t1)

    # ===== SYNTHESIS ==============================================
    print("\n" + "=" * 80)
    print("SYNTHESIS")
    print("=" * 80)

    print(f"\n1. INVENTORY: {t1['headless_types']} headless compound types "
          f"({100*t1['headless_type_fraction']:.1f}% of compound types), "
          f"{t1['headless_tokens']} tokens ({100*t1['headless_token_fraction']:.1f}%)")

    # What atoms start headless compounds?
    fa = t1['first_atom_distribution']
    top_atom = max(fa, key=lambda a: fa[a]['tokens'])
    role = 'MODIFIER' if top_atom in MOD_ONLY else 'TERMINAL'
    print(f"   Dominant first atom: {top_atom} ({role}, {ATOM_GLOSS.get(top_atom, '?')})")

    print(f"\n2. CATEGORIES: Chi2={t2['chi2']:.1f}, V={t2['cramers_v']:.3f}")
    enriched = t2['enrichment']
    for cat, ratio in sorted(enriched.items(), key=lambda x: -x[1])[:3]:
        print(f"   {cat}: {ratio:.2f}x enriched in headless")

    print(f"\n3. ABBREVIATION: {t3['has_headed_version']}/{t3['tested_count']} have headed versions, "
          f"mean headless fraction={t3['mean_headless_fraction']:.3f}")
    if t3['abbreviation_count'] > 0:
        print(f"   {t3['abbreviation_count']} likely abbreviations, "
              f"{t3['dominant_count']} headless-dominant, {t3['mixed_count']} mixed")
    else:
        print(f"   Headless forms are dominant — NOT abbreviations of headed forms")

    print(f"\n4. PREFIX: V={t4['cramers_v']:.3f}")
    print(f"   BARE rate: headed={t4['bare_rate_headed']:.1f}%, headless={t4['bare_rate_headless']:.1f}%")

    print(f"\n5. POSITION: mean pos headed={t5['headed_mean_pos']:.3f}, headless={t5['headless_mean_pos']:.3f}")
    print(f"   Mann-Whitney p={t5['mann_whitney_p']:.2e}")
    print(f"   Par-initial: headed={100*t5['headed_par_initial_rate']:.1f}%, "
          f"headless={100*t5['headless_par_initial_rate']:.1f}%")

    # Verdict
    print(f"\n{'='*80}")
    print("VERDICT")
    print(f"{'='*80}")
    # Determine interpretation based on results
    if t1['headless_token_fraction'] > 0.3:
        print("  Headless compounds are a MAJOR population — not edge cases.")
    else:
        print("  Headless compounds are a MINOR population — specialized subgrammar.")

    if t3['mean_headless_fraction'] > 0.8:
        print("  NOT abbreviations — headless forms are primary, not shortened headed forms.")
    elif t3['mean_headless_fraction'] < 0.5:
        print("  Likely ABBREVIATIONS — headed versions are more common.")
    else:
        print("  MIXED — some abbreviations, some independent forms.")

    if t2['cramers_v'] > 0.15:
        print(f"  Category divergence is GENUINE (V={t2['cramers_v']:.3f}) — "
              f"headless compounds encode different operations.")
    else:
        print(f"  Category divergence is WEAK (V={t2['cramers_v']:.3f}) — "
              f"headless compounds are a grammatical variant, not a semantic class.")

    # === SAVE RESULTS =============================================
    output = {
        'test1_inventory': {k: v for k, v in t1.items()
                            if k not in ('headless_mids', 'headed_mids')},
        'test2_categories': t2,
        'test3_abbreviation': t3,
        'test4_prefix': t4,
        'test5_position': t5,
    }

    out_path = RESULTS_DIR / 'headless_compounds.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

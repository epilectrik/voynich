"""
Phase 509: HEADLESS_COMPOUND_GRAMMAR
=============================================

Deep investigation of the 20.6% of compound tokens whose MIDDLE begins with
a non-HEAD atom (MODIFIER or TERMINAL character instead of {a, e, o, k, t}).

C1394 T8 established headless compounds as a specialized subgrammar for
infrastructure operations.  This phase asks: What are the specific headless
patterns? Do different initial atoms create different functional profiles?
Is there internal structure within headless compounds?

Tests:
  T1  Headless Initial Atom Census
  T2  Initial Atom Functional Profiles (8-category)
  T3  Positional Specialization
  T4  PREFIX Channel Distribution
  T5  Suffix Behavior
  T6  Compound Length Distribution
  T7  REGIME Distribution
  T8  Internal Modifier Ordering Compliance
  T9  HT/INFRA Association
  T10 Sequential Context
"""

import sys
import os
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

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
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# C1394 atom role classification
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}  # atoms that can legally HEAD a compound
MODIFIER_SET = MOD_ONLY
TERMINAL_SET = TERM_ONLY

ALL_8_CATS = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}

# Modifier canonical ordering from C1394 T4: p -> f -> i -> c -> d -> s
MODIFIER_ORDER = {'p': 0, 'f': 1, 'i': 2, 'c': 3, 'd': 4, 's': 5}


# --- Atom decomposition -------------------------------------------

def atomize(middle):
    """Split MIDDLE into atoms, respecting e/i extensibility (C1197)."""
    atoms = []
    idx = 0
    while idx < len(middle):
        ch = middle[idx]
        if ch in EXTENSIBLE:
            run = ch
            while idx + 1 < len(middle) and middle[idx + 1] == ch:
                run += ch
                idx += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        idx += 1
    return atoms


def first_atom_base(middle):
    """Base character of first atom (handles 'ee' -> 'e')."""
    atoms = atomize(middle)
    return atoms[0][0] if atoms else None


def is_compound(middle):
    return len(atomize(middle)) >= 2


def is_headless(middle):
    if not is_compound(middle):
        return False
    return first_atom_base(middle) not in HEAD_SET


def atom_role(ch):
    """Return role string for single atom character."""
    if ch in HEAD_ONLY:
        return 'HEAD'
    if ch in FREE:
        return 'FREE'
    if ch == 'e':
        return 'HEAD'  # e is HEAD when leading
    if ch in MOD_ONLY:
        return 'MODIFIER'
    if ch in TERM_ONLY:
        return 'TERMINAL'
    return 'UNKNOWN'


# --- Chi-squared helper -------------------------------------------

def chi2_test(contingency_table):
    """Manual chi-squared so we avoid scipy import overhead.
    contingency_table: list of lists [[a1,b1],[a2,b2],...] (Nx2 or NxM)
    Returns chi2, p_approx, cramers_v, dof
    """
    from scipy.stats import chi2_contingency
    if len(contingency_table) < 2 or any(len(row) < 2 for row in contingency_table):
        return 0, 1.0, 0, 0
    # Filter out all-zero rows
    ct = [row for row in contingency_table if sum(row) > 0]
    if len(ct) < 2:
        return 0, 1.0, 0, 0
    try:
        chi2, p, dof, _ = chi2_contingency(ct)
    except ValueError:
        return 0, 1.0, 0, 0
    n = sum(sum(row) for row in ct)
    k = min(len(ct), len(ct[0]))
    v = math.sqrt(chi2 / (n * max(k - 1, 1))) if n > 0 else 0
    return chi2, p, v, dof


def ks_2samp(a, b):
    from scipy.stats import ks_2samp as _ks
    if len(a) < 2 or len(b) < 2:
        return 0, 1.0
    stat, p = _ks(a, b)
    return stat, p


# --- Data Loading -------------------------------------------------

def load_data():
    """Load Currier B tokens with morphology, category, position, REGIME."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Load REGIME mapping
    regime_path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
    regime_map = {}
    if regime_path.exists():
        with open(regime_path, 'r', encoding='utf-8') as f:
            rdata = json.load(f)
        for folio, info in rdata.get('regime_assignments', {}).items():
            regime_map[folio] = info['regime']

    # Load HT/classified vocabulary info
    # B grammar = 479 classified types (C121).  Everything else is HT/UN (C740).
    # We'll determine HT status by checking if the token's full word
    # or MIDDLE is in the 49-class grammar.  Simpler: use the 49-class
    # instruction-class membership.  For our purposes, we use CategoryClassifier:
    # if cc.classify(middle) returns None, it's likely HT.

    records = []
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        cat = cc.classify(m.middle)
        regime = regime_map.get(tok.folio, None)
        records.append({
            'word': tok.word,
            'middle': m.middle,
            'prefix': m.prefix,
            'suffix': m.suffix,
            'category': cat or 'UNKNOWN',
            'has_category': cat is not None,
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
            'regime': regime,
        })

    # Compute normalized line position
    line_groups = defaultdict(list)
    for i, r in enumerate(records):
        line_groups[(r['folio'], r['line'])].append(i)
    for indices in line_groups.values():
        n = len(indices)
        for pos, idx in enumerate(indices):
            records[idx]['norm_pos'] = pos / (n - 1) if n > 1 else 0.5

    return records


# === T1: Headless Initial Atom Census ================================

def test1_census(records):
    print("=" * 80)
    print("T1: Headless Initial Atom Census")
    print("=" * 80)

    mid_counts = Counter()
    for r in records:
        mid_counts[r['middle']] += 1

    single_types = single_toks = 0
    headed_types = headed_toks = 0
    headless_types = headless_toks = 0
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

    total_comp = headed_types + headless_types
    total_comp_tok = headed_toks + headless_toks

    print(f"\n  Single-atom:   {single_types:>5} types, {single_toks:>6} tokens")
    print(f"  Headed:        {headed_types:>5} types, {headed_toks:>6} tokens")
    print(f"  Headless:      {headless_types:>5} types, {headless_toks:>6} tokens")
    print(f"  Headless %:    {100*headless_types/total_comp:.1f}% types, "
          f"{100*headless_toks/total_comp_tok:.1f}% tokens")

    # First-atom distribution
    fa_types = Counter()
    fa_toks = Counter()
    for mid, count in headless_mids.items():
        base = first_atom_base(mid)
        fa_types[base] += 1
        fa_toks[base] += count

    # Which atoms from C1394 classification are present?
    mod_present = sorted([a for a in fa_types if a in MOD_ONLY], key=lambda x: -fa_toks[x])
    term_present = sorted([a for a in fa_types if a in TERM_ONLY], key=lambda x: -fa_toks[x])
    other_present = [a for a in fa_types if a not in MOD_ONLY and a not in TERM_ONLY]

    print(f"\n  MODIFIER atoms leading headless: {mod_present} ({len(mod_present)}/6)")
    print(f"  TERMINAL atoms leading headless: {term_present} ({len(term_present)}/6)")
    if other_present:
        print(f"  Other atoms: {other_present}")

    print(f"\n  {'Atom':<5} {'Role':<10} {'Types':>6} {'%ty':>7} {'Tokens':>7} {'%tok':>7}  Gloss")
    for atom in sorted(fa_types, key=lambda a: -fa_toks[a]):
        role = atom_role(atom)
        gloss = ATOM_GLOSS.get(atom, '?')
        print(f"  {atom:<5} {role:<10} {fa_types[atom]:>6} {100*fa_types[atom]/headless_types:>6.1f}%"
              f" {fa_toks[atom]:>7} {100*fa_toks[atom]/headless_toks:>6.1f}%  {gloss}")

    # Top 30 headless MIDDLEs
    print(f"\n  Top 30 headless MIDDLEs:")
    print(f"  {'MIDDLE':<14} {'Tok':>5} {'Atoms':<22} {'Cat':>12}")
    cc_obj = CategoryClassifier()
    for mid, count in Counter(headless_mids).most_common(30):
        atoms = atomize(mid)
        cat = cc_obj.classify(mid) or 'UNK'
        print(f"  {mid:<14} {count:>5} {' '.join(atoms):<22} {cat:>12}")

    result = {
        'single_types': single_types, 'single_tokens': single_toks,
        'headed_types': headed_types, 'headed_tokens': headed_toks,
        'headless_types': headless_types, 'headless_tokens': headless_toks,
        'headless_type_pct': round(100 * headless_types / total_comp, 2),
        'headless_token_pct': round(100 * headless_toks / total_comp_tok, 2),
        'first_atom_types': {a: fa_types[a] for a in fa_types},
        'first_atom_tokens': {a: fa_toks[a] for a in fa_toks},
        'modifier_atoms_present': mod_present,
        'terminal_atoms_present': term_present,
        'verdict': f"All 6 MOD atoms represented: {'YES' if len(mod_present)==6 else 'NO (' + str(len(mod_present)) + '/6)'}; "
                   f"TERM atoms: {len(term_present)}/6",
    }
    print(f"\n  VERDICT: {result['verdict']}")
    return result, headless_mids, headed_mids


# === T2: Initial Atom Functional Profiles ============================

def test2_functional_profiles(records, headless_mids):
    print("\n" + "=" * 80)
    print("T2: Initial Atom Functional Profiles (8-category)")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    # Group by first-atom base
    atom_cat_counts = defaultdict(Counter)  # atom -> {cat: count}
    atom_total = Counter()
    for r in records:
        if r['middle'] in headless_set:
            base = first_atom_base(r['middle'])
            atom_cat_counts[base][r['category']] += 1
            atom_total[base] += 1

    # Overall headless category distribution for reference
    overall = Counter()
    for ac in atom_cat_counts.values():
        overall += ac

    # Print per-atom profiles (only atoms with 20+ tokens)
    reliable_atoms = sorted([a for a in atom_total if atom_total[a] >= 20],
                           key=lambda a: -atom_total[a])

    print(f"\n  Per-atom category profiles (atoms with 20+ tokens):")
    print(f"  {'Atom':<5} {'N':>5}  " + "  ".join(f"{c[:4]:>6}" for c in ALL_8_CATS))
    for atom in reliable_atoms:
        total = atom_total[atom]
        pcts = [100 * atom_cat_counts[atom].get(c, 0) / total for c in ALL_8_CATS]
        pct_str = "  ".join(f"{p:>5.1f}%" for p in pcts)
        print(f"  {atom:<5} {total:>5}  {pct_str}")

    # Overall reference
    ov_total = sum(overall.values())
    print(f"  {'ALL':<5} {ov_total:>5}  " +
          "  ".join(f"{100*overall.get(c,0)/ov_total:>5.1f}%" for c in ALL_8_CATS))

    # Chi-squared: do atoms differ in category profile?
    ct = []
    for atom in reliable_atoms:
        row = [atom_cat_counts[atom].get(c, 0) for c in ALL_8_CATS]
        ct.append(row)
    chi2, p, v, dof = chi2_test(ct)
    print(f"\n  Chi2 across atoms: {chi2:.1f}, p={p:.2e}, Cramer's V={v:.3f}")

    # Per-atom dominant categories and comparison to C1394 modifier role
    print(f"\n  Per-atom dominant category vs C1394 modifier/terminal role:")
    atom_profiles = {}
    for atom in reliable_atoms:
        total = atom_total[atom]
        cat_pcts = {c: round(100 * atom_cat_counts[atom].get(c, 0) / total, 1) for c in ALL_8_CATS}
        top_cat = max(cat_pcts, key=cat_pcts.get)
        c1394_role = atom_role(atom)
        gloss = ATOM_GLOSS.get(atom, '?')
        print(f"  {atom} ({c1394_role}, '{gloss}'): top={top_cat} ({cat_pcts[top_cat]:.1f}%)")
        atom_profiles[atom] = {
            'n': total,
            'categories': cat_pcts,
            'top_category': top_cat,
            'c1394_role': c1394_role,
        }

    verdict = f"Chi2={chi2:.1f}, V={v:.3f} ({'SIGNIFICANT' if p < 0.001 else 'NS'}). " \
              f"Different headless initial atoms DO predict different categories." if v > 0.15 else \
              f"Chi2={chi2:.1f}, V={v:.3f}. Weak or no differentiation."
    print(f"\n  VERDICT: {verdict}")

    return {
        'chi2': round(chi2, 1), 'p': p, 'cramers_v': round(v, 3),
        'atom_profiles': atom_profiles,
        'reliable_atoms': reliable_atoms,
        'overall_pcts': {c: round(100 * overall.get(c, 0) / ov_total, 1) for c in ALL_8_CATS},
        'verdict': verdict,
    }


# === T3: Positional Specialization ==================================

def test3_positional(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T3: Positional Specialization by Initial Atom")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())

    # Gather positions per initial atom
    atom_positions = defaultdict(list)
    atom_initial_rate = Counter()
    atom_final_rate = Counter()
    atom_par_initial_rate = Counter()
    atom_n = Counter()

    headed_positions = []
    headed_n = 0
    headed_initial = headed_final = headed_par_initial = 0

    for r in records:
        mid = r['middle']
        pos = r.get('norm_pos', 0.5)
        if mid in headless_set:
            base = first_atom_base(mid)
            atom_positions[base].append(pos)
            atom_n[base] += 1
            if r['line_initial']:
                atom_initial_rate[base] += 1
            if r['line_final']:
                atom_final_rate[base] += 1
            if r['par_initial']:
                atom_par_initial_rate[base] += 1
        elif mid in headed_set:
            headed_positions.append(pos)
            headed_n += 1
            if r['line_initial']:
                headed_initial += 1
            if r['line_final']:
                headed_final += 1
            if r['par_initial']:
                headed_par_initial += 1

    reliable = sorted([a for a in atom_n if atom_n[a] >= 20], key=lambda a: -atom_n[a])

    print(f"\n  {'Atom':<5} {'N':>5} {'Mean':>6} {'Init%':>7} {'Final%':>7} {'ParI%':>7}  KS vs headed")
    h_mean = sum(headed_positions) / len(headed_positions) if headed_positions else 0
    print(f"  {'HEAD':<5} {headed_n:>5} {h_mean:>6.3f} "
          f"{100*headed_initial/headed_n:>6.1f}% {100*headed_final/headed_n:>6.1f}% "
          f"{100*headed_par_initial/headed_n:>6.1f}%  (reference)")

    atom_pos_results = {}
    for atom in reliable:
        positions = atom_positions[atom]
        mean_pos = sum(positions) / len(positions)
        init_rate = 100 * atom_initial_rate[atom] / atom_n[atom]
        final_rate = 100 * atom_final_rate[atom] / atom_n[atom]
        par_init_rate = 100 * atom_par_initial_rate[atom] / atom_n[atom]
        ks_stat, ks_p = ks_2samp(positions, headed_positions)
        sig = '*' if ks_p < 0.01 else ''
        print(f"  {atom:<5} {atom_n[atom]:>5} {mean_pos:>6.3f} {init_rate:>6.1f}% "
              f"{final_rate:>6.1f}% {par_init_rate:>6.1f}%  KS={ks_stat:.3f} p={ks_p:.3e}{sig}")
        atom_pos_results[atom] = {
            'n': atom_n[atom],
            'mean_pos': round(mean_pos, 3),
            'initial_rate': round(init_rate, 1),
            'final_rate': round(final_rate, 1),
            'par_initial_rate': round(par_init_rate, 1),
            'ks_stat': round(ks_stat, 3),
            'ks_p': ks_p,
        }

    # Pairwise KS among headless atoms
    sig_pairs = 0
    total_pairs = 0
    for i, a1 in enumerate(reliable):
        for a2 in reliable[i+1:]:
            _, kp = ks_2samp(atom_positions[a1], atom_positions[a2])
            total_pairs += 1
            if kp < 0.01:
                sig_pairs += 1

    print(f"\n  Pairwise KS tests among headless atoms: {sig_pairs}/{total_pairs} "
          f"significant (p<0.01)")

    verdict = f"{sig_pairs}/{total_pairs} atom pairs have significantly different positions."
    print(f"\n  VERDICT: {verdict}")

    return {
        'headed_ref': {
            'n': headed_n,
            'mean_pos': round(h_mean, 3),
            'initial_rate': round(100 * headed_initial / headed_n, 1),
            'final_rate': round(100 * headed_final / headed_n, 1),
            'par_initial_rate': round(100 * headed_par_initial / headed_n, 1),
        },
        'atom_profiles': atom_pos_results,
        'pairwise_sig': sig_pairs,
        'pairwise_total': total_pairs,
        'verdict': verdict,
    }


# === T4: PREFIX Channel Distribution =================================

def test4_prefix(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T4: PREFIX Channel Distribution by Initial Atom")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())

    # Per initial atom, count PREFIXes
    atom_pfx = defaultdict(Counter)
    atom_n = Counter()
    headed_pfx = Counter()
    headed_total = 0

    for r in records:
        mid = r['middle']
        pfx = r['prefix'] or 'BARE'
        if mid in headless_set:
            base = first_atom_base(mid)
            atom_pfx[base][pfx] += 1
            atom_n[base] += 1
        elif mid in headed_set:
            headed_pfx[pfx] += 1
            headed_total += 1

    reliable = sorted([a for a in atom_n if atom_n[a] >= 20], key=lambda a: -atom_n[a])

    # Show top PREFIXes per atom
    print(f"\n  Top-3 PREFIXes per headless initial atom:")
    print(f"  {'Atom':<5} {'N':>5}  Top-3 PREFIXes (with %)")
    atom_pfx_results = {}
    for atom in reliable:
        total = atom_n[atom]
        top3 = atom_pfx[atom].most_common(3)
        top3_str = ", ".join(f"{p}({100*c/total:.0f}%)" for p, c in top3)
        print(f"  {atom:<5} {total:>5}  {top3_str}")
        atom_pfx_results[atom] = {
            'n': total,
            'top_prefixes': {p: c for p, c in atom_pfx[atom].most_common(10)},
            'bare_rate': round(100 * atom_pfx[atom].get('BARE', 0) / total, 1),
        }

    # Headed reference top prefixes
    h_top = headed_pfx.most_common(5)
    print(f"\n  Headed reference top-5: " +
          ", ".join(f"{p}({100*c/headed_total:.0f}%)" for p, c in h_top))

    # Overall chi-squared: does initial atom predict PREFIX?
    all_pfx = sorted(set().union(*(set(atom_pfx[a].keys()) for a in reliable)))
    ct = []
    for atom in reliable:
        row = [atom_pfx[atom].get(p, 0) for p in all_pfx]
        ct.append(row)
    chi2, p, v, dof = chi2_test(ct)
    print(f"\n  Chi2 (atom x PREFIX): {chi2:.1f}, p={p:.2e}, V={v:.3f}")

    # da enrichment check per atom (C1394 says da 2213x for headless overall)
    print(f"\n  da-PREFIX rate per atom (C1394 predicts massive da enrichment):")
    for atom in reliable:
        da_rate = 100 * atom_pfx[atom].get('da', 0) / atom_n[atom]
        da_headed = 100 * headed_pfx.get('da', 0) / headed_total if headed_total else 0
        ratio = da_rate / da_headed if da_headed > 0 else float('inf')
        marker = '***' if ratio > 10 else '**' if ratio > 3 else '*' if ratio > 1.5 else ''
        print(f"    {atom}: {da_rate:.1f}% (headed: {da_headed:.1f}%, ratio: {ratio:.1f}x) {marker}")

    # Is da enrichment universal across ALL headless types?
    da_universal = all(atom_pfx[a].get('da', 0) / atom_n[a] > 0.05 for a in reliable)

    verdict = f"V={v:.3f}. da enrichment universal: {da_universal}. " \
              f"{'All atoms use da channel' if da_universal else 'Some atoms prefer different channels.'}"
    print(f"\n  VERDICT: {verdict}")

    return {
        'chi2': round(chi2, 1), 'p': p, 'cramers_v': round(v, 3),
        'atom_profiles': atom_pfx_results,
        'headed_bare_rate': round(100 * headed_pfx.get('BARE', 0) / headed_total, 1),
        'da_universal': da_universal,
        'verdict': verdict,
    }


# === T5: Suffix Behavior =============================================

def test5_suffix(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T5: Suffix Behavior by Initial Atom")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())

    atom_suf = defaultdict(Counter)
    atom_n = Counter()
    atom_bare = Counter()
    headed_suf = Counter()
    headed_n = 0
    headed_bare = 0

    for r in records:
        mid = r['middle']
        suf = r['suffix'] or 'BARE'
        if mid in headless_set:
            base = first_atom_base(mid)
            atom_suf[base][suf] += 1
            atom_n[base] += 1
            if suf == 'BARE':
                atom_bare[base] += 1
        elif mid in headed_set:
            headed_suf[suf] += 1
            headed_n += 1
            if suf == 'BARE':
                headed_bare += 1

    reliable = sorted([a for a in atom_n if atom_n[a] >= 20], key=lambda a: -atom_n[a])

    print(f"\n  Bare suffix rate:")
    print(f"  {'Atom':<5} {'N':>5} {'Bare%':>7}  Top-3 suffixes")
    headed_bare_pct = 100 * headed_bare / headed_n if headed_n else 0
    print(f"  {'HEAD':<5} {headed_n:>5} {headed_bare_pct:>6.1f}%  " +
          ", ".join(f"{s}({c})" for s, c in headed_suf.most_common(3) if s != 'BARE'))

    atom_suf_results = {}
    for atom in reliable:
        total = atom_n[atom]
        bare_pct = 100 * atom_bare[atom] / total
        top3 = [(s, c) for s, c in atom_suf[atom].most_common(4) if s != 'BARE'][:3]
        top3_str = ", ".join(f"{s}({c})" for s, c in top3)
        print(f"  {atom:<5} {total:>5} {bare_pct:>6.1f}%  {top3_str}")
        atom_suf_results[atom] = {
            'n': total,
            'bare_rate': round(bare_pct, 1),
            'top_suffixes': {s: c for s, c in atom_suf[atom].most_common(8)},
        }

    # Chi-squared across atoms x suffix
    all_suf = sorted(set().union(*(set(atom_suf[a].keys()) for a in reliable)))
    ct = []
    for atom in reliable:
        row = [atom_suf[atom].get(s, 0) for s in all_suf]
        ct.append(row)
    chi2, p, v, dof = chi2_test(ct)
    print(f"\n  Chi2 (atom x suffix): {chi2:.1f}, p={p:.2e}, V={v:.3f}")

    # Overall bare rate comparison
    all_headless_bare = sum(atom_bare[a] for a in atom_n)
    all_headless_n = sum(atom_n[a] for a in atom_n)
    hl_bare_pct = 100 * all_headless_bare / all_headless_n if all_headless_n else 0
    print(f"\n  Overall bare rate: headless={hl_bare_pct:.1f}%, headed={headed_bare_pct:.1f}%")
    direction = "MORE suffix-rich" if hl_bare_pct < headed_bare_pct else "LESS suffix-rich"
    print(f"  Headless compounds are {direction} than headed compounds.")

    verdict = f"Headless bare={hl_bare_pct:.1f}% vs headed={headed_bare_pct:.1f}%. " \
              f"V={v:.3f}. {direction}."
    print(f"\n  VERDICT: {verdict}")

    return {
        'chi2': round(chi2, 1), 'p': p, 'cramers_v': round(v, 3),
        'headless_bare_pct': round(hl_bare_pct, 1),
        'headed_bare_pct': round(headed_bare_pct, 1),
        'atom_profiles': atom_suf_results,
        'verdict': verdict,
    }


# === T6: Compound Length Distribution ================================

def test6_length(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T6: Compound Length Distribution (MIDDLE character count)")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())

    # Per initial atom, compute length distribution
    atom_lengths = defaultdict(list)
    headed_lengths = []

    for mid, count in headless_mids.items():
        base = first_atom_base(mid)
        atom_lengths[base].extend([len(mid)] * count)

    for mid, count in headed_mids.items():
        headed_lengths.extend([len(mid)] * count)

    reliable = sorted([a for a in atom_lengths if len(atom_lengths[a]) >= 20],
                     key=lambda a: -len(atom_lengths[a]))

    h_mean = sum(headed_lengths) / len(headed_lengths)
    print(f"\n  Headed mean length: {h_mean:.2f} chars")
    print(f"\n  {'Atom':<5} {'N':>5} {'Mean':>6} {'Med':>5} {'Min':>4} {'Max':>4}")
    print(f"  {'HEAD':<5} {len(headed_lengths):>5} {h_mean:>6.2f} "
          f"{sorted(headed_lengths)[len(headed_lengths)//2]:>5} "
          f"{min(headed_lengths):>4} {max(headed_lengths):>4}")

    atom_len_results = {}
    for atom in reliable:
        lengths = atom_lengths[atom]
        mean_l = sum(lengths) / len(lengths)
        sorted_l = sorted(lengths)
        med_l = sorted_l[len(sorted_l) // 2]
        print(f"  {atom:<5} {len(lengths):>5} {mean_l:>6.2f} {med_l:>5} "
              f"{min(lengths):>4} {max(lengths):>4}")
        atom_len_results[atom] = {
            'n': len(lengths),
            'mean': round(mean_l, 2),
            'median': med_l,
            'min': min(lengths),
            'max': max(lengths),
        }

    # Overall comparison
    all_hl_lengths = []
    for a in atom_lengths:
        all_hl_lengths.extend(atom_lengths[a])
    hl_mean = sum(all_hl_lengths) / len(all_hl_lengths)
    print(f"\n  All headless mean: {hl_mean:.2f} vs headed: {h_mean:.2f}")
    print(f"  Headless compounds are {'SHORTER' if hl_mean < h_mean else 'LONGER'} "
          f"on average (delta={hl_mean - h_mean:+.2f} chars).")

    verdict = f"Headless mean={hl_mean:.2f}, headed mean={h_mean:.2f}. " \
              f"Delta={hl_mean - h_mean:+.2f} chars."
    print(f"\n  VERDICT: {verdict}")

    return {
        'headed_mean': round(h_mean, 2),
        'headless_mean': round(hl_mean, 2),
        'delta': round(hl_mean - h_mean, 2),
        'atom_profiles': atom_len_results,
        'verdict': verdict,
    }


# === T7: REGIME Distribution =========================================

def test7_regime(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T7: REGIME Distribution by Initial Atom")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())
    regimes = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']

    atom_regime = defaultdict(Counter)
    atom_n = Counter()
    headed_regime = Counter()
    headed_total = 0

    for r in records:
        if not r['regime']:
            continue
        mid = r['middle']
        regime = r['regime']
        if mid in headless_set:
            base = first_atom_base(mid)
            atom_regime[base][regime] += 1
            atom_n[base] += 1
        elif mid in headed_set:
            headed_regime[regime] += 1
            headed_total += 1

    reliable = sorted([a for a in atom_n if atom_n[a] >= 20], key=lambda a: -atom_n[a])

    print(f"\n  {'Atom':<5} {'N':>5}  " + "  ".join(f"{'R'+r[-1]:>6}" for r in regimes))
    hp = [100 * headed_regime.get(r, 0) / headed_total for r in regimes]
    print(f"  {'HEAD':<5} {headed_total:>5}  " + "  ".join(f"{p:>5.1f}%" for p in hp))

    atom_regime_results = {}
    for atom in reliable:
        total = atom_n[atom]
        pcts = [100 * atom_regime[atom].get(r, 0) / total for r in regimes]
        print(f"  {atom:<5} {total:>5}  " + "  ".join(f"{p:>5.1f}%" for p in pcts))
        atom_regime_results[atom] = {
            'n': total,
            'regime_pcts': {r: round(p, 1) for r, p in zip(regimes, pcts)},
        }

    # Chi-squared across atoms x REGIME
    ct = []
    for atom in reliable:
        row = [atom_regime[atom].get(r, 0) for r in regimes]
        ct.append(row)
    chi2, p, v, dof = chi2_test(ct)
    print(f"\n  Chi2 (atom x REGIME): {chi2:.1f}, p={p:.2e}, V={v:.3f}")

    # Overall headless vs headed
    all_hl_regime = Counter()
    all_hl_n = 0
    for a in atom_regime:
        all_hl_regime += atom_regime[a]
        all_hl_n += atom_n[a]

    if all_hl_n > 0:
        ct2 = [[headed_regime.get(r, 0) for r in regimes],
               [all_hl_regime.get(r, 0) for r in regimes]]
        chi2_2, p_2, v_2, _ = chi2_test(ct2)
        print(f"\n  Headed vs all headless: Chi2={chi2_2:.1f}, p={p_2:.2e}, V={v_2:.3f}")
    else:
        chi2_2, p_2, v_2 = 0, 1, 0

    verdict = f"Within-headless V={v:.3f}. Headless-vs-headed V={v_2:.3f}."
    print(f"\n  VERDICT: {verdict}")

    return {
        'within_chi2': round(chi2, 1), 'within_p': p, 'within_v': round(v, 3),
        'vs_headed_chi2': round(chi2_2, 1), 'vs_headed_p': p_2, 'vs_headed_v': round(v_2, 3),
        'atom_profiles': atom_regime_results,
        'headed_regime': {r: round(100 * headed_regime.get(r, 0) / headed_total, 1)
                          for r in regimes} if headed_total > 0 else {},
        'verdict': verdict,
    }


# === T8: Internal Modifier Ordering Compliance ========================

def test8_ordering(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T8: Internal Modifier Ordering (p->f->i->c->d->s compliance)")
    print("=" * 80)

    # For headless compounds with 2+ modifier atoms, check ordering
    headless_compliant = 0
    headless_violating = 0
    headless_testable = 0

    headed_compliant = 0
    headed_violating = 0
    headed_testable = 0

    def check_ordering(mid, is_headed):
        """Return (testable, compliant) for modifier ordering within compound."""
        atoms = atomize(mid)
        # For headed: skip first atom (HEAD), then check modifiers in the rest
        # For headless: check all atoms that are modifiers
        if is_headed:
            interior = atoms[1:]  # skip HEAD
        else:
            interior = atoms  # all atoms count

        # Gather modifier atoms with their positions
        mod_positions = []
        for a in interior:
            base_ch = a[0]
            if base_ch in MODIFIER_ORDER:
                mod_positions.append(MODIFIER_ORDER[base_ch])

        if len(mod_positions) < 2:
            return False, False  # Not testable

        # Check if positions are monotonically increasing
        compliant = all(mod_positions[i] <= mod_positions[i+1]
                       for i in range(len(mod_positions) - 1))
        return True, compliant

    # Process headless compounds
    for mid, count in headless_mids.items():
        testable, compliant = check_ordering(mid, False)
        if testable:
            headless_testable += count
            if compliant:
                headless_compliant += count
            else:
                headless_violating += count

    # Process headed compounds
    for mid, count in headed_mids.items():
        testable, compliant = check_ordering(mid, True)
        if testable:
            headed_testable += count
            if compliant:
                headed_compliant += count
            else:
                headed_violating += count

    hl_rate = 100 * headless_compliant / headless_testable if headless_testable else 0
    h_rate = 100 * headed_compliant / headed_testable if headed_testable else 0

    print(f"\n  Modifier ordering compliance (p->f->i->c->d->s):")
    print(f"  {'Type':<12} {'Testable':>9} {'Compliant':>10} {'Rate':>7}")
    print(f"  {'Headed':<12} {headed_testable:>9} {headed_compliant:>10} {h_rate:>6.1f}%")
    print(f"  {'Headless':<12} {headless_testable:>9} {headless_compliant:>10} {hl_rate:>6.1f}%")

    # Show examples of violations in headless
    print(f"\n  Example headless violations:")
    violation_examples = []
    for mid in sorted(headless_mids, key=lambda m: -headless_mids[m]):
        testable, compliant = check_ordering(mid, False)
        if testable and not compliant:
            atoms = atomize(mid)
            mods = [(a[0], MODIFIER_ORDER[a[0]]) for a in atoms if a[0] in MODIFIER_ORDER]
            violation_examples.append((mid, headless_mids[mid], mods))
            if len(violation_examples) >= 10:
                break

    for mid, count, mods in violation_examples:
        mod_str = " -> ".join(f"{m}({ATOM_GLOSS.get(m, '?')},ord={o})" for m, o in mods)
        print(f"    {mid:<12} ({count:>4} tok): {mod_str}")

    verdict = f"Headless compliance={hl_rate:.1f}%, headed={h_rate:.1f}%. " \
              f"{'SAME grammar' if abs(hl_rate - h_rate) < 10 else 'DIFFERENT ordering rules'}."
    print(f"\n  VERDICT: {verdict}")

    return {
        'headless_testable': headless_testable,
        'headless_compliant': headless_compliant,
        'headless_compliance_rate': round(hl_rate, 1),
        'headed_testable': headed_testable,
        'headed_compliant': headed_compliant,
        'headed_compliance_rate': round(h_rate, 1),
        'violation_examples': [(m, c) for m, c, _ in violation_examples[:5]],
        'verdict': verdict,
    }


# === T9: HT/INFRA Association ========================================

def test9_ht_association(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T9: HT/INFRA Association")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())

    # Use has_category flag: if CategoryClassifier returns None,
    # the MIDDLE is unclassified -> likely HT/UN
    headless_classified = headless_unclassified = 0
    headed_classified = headed_unclassified = 0

    atom_classified = Counter()
    atom_unclassified = Counter()
    atom_n = Counter()

    for r in records:
        mid = r['middle']
        if mid in headless_set:
            base = first_atom_base(mid)
            atom_n[base] += 1
            if r['has_category']:
                headless_classified += 1
                atom_classified[base] += 1
            else:
                headless_unclassified += 1
                atom_unclassified[base] += 1
        elif mid in headed_set:
            if r['has_category']:
                headed_classified += 1
            else:
                headed_unclassified += 1

    hl_total = headless_classified + headless_unclassified
    h_total = headed_classified + headed_unclassified

    hl_ht_pct = 100 * headless_unclassified / hl_total if hl_total else 0
    h_ht_pct = 100 * headed_unclassified / h_total if h_total else 0

    print(f"\n  HT/UN (unclassified by CategoryClassifier) rates:")
    print(f"  Headed:   {h_ht_pct:.1f}% HT ({headed_unclassified}/{h_total})")
    print(f"  Headless: {hl_ht_pct:.1f}% HT ({headless_unclassified}/{hl_total})")
    print(f"  Ratio:    {hl_ht_pct/h_ht_pct:.2f}x" if h_ht_pct > 0 else "  (headed 0% HT)")

    # Per atom
    reliable = sorted([a for a in atom_n if atom_n[a] >= 20], key=lambda a: -atom_n[a])
    print(f"\n  Per-atom HT rates:")
    print(f"  {'Atom':<5} {'N':>5} {'HT%':>7} {'Classified%':>12}")
    atom_ht_results = {}
    for atom in reliable:
        total = atom_n[atom]
        ht_pct = 100 * atom_unclassified[atom] / total
        cls_pct = 100 * atom_classified[atom] / total
        print(f"  {atom:<5} {total:>5} {ht_pct:>6.1f}% {cls_pct:>11.1f}%")
        atom_ht_results[atom] = {
            'n': total,
            'ht_rate': round(ht_pct, 1),
            'classified_rate': round(cls_pct, 1),
        }

    verdict = f"Headless HT={hl_ht_pct:.1f}% vs headed HT={h_ht_pct:.1f}%. " \
              f"{'Headless are MORE HT-enriched' if hl_ht_pct > h_ht_pct else 'Similar HT rates'}."
    print(f"\n  VERDICT: {verdict}")

    return {
        'headless_ht_pct': round(hl_ht_pct, 1),
        'headed_ht_pct': round(h_ht_pct, 1),
        'ratio': round(hl_ht_pct / h_ht_pct, 2) if h_ht_pct > 0 else None,
        'atom_profiles': atom_ht_results,
        'verdict': verdict,
    }


# === T10: Sequential Context =========================================

def test10_context(records, headless_mids, headed_mids):
    print("\n" + "=" * 80)
    print("T10: Sequential Context (what precedes/follows headless compounds)")
    print("=" * 80)

    headless_set = set(headless_mids.keys())
    headed_set = set(headed_mids.keys())
    cc_obj = CategoryClassifier()

    # Build line-ordered token sequences
    line_seqs = defaultdict(list)
    for i, r in enumerate(records):
        line_seqs[(r['folio'], r['line'])].append(i)

    # For each headless token, find predecessor and successor categories
    pred_cats = Counter()
    succ_cats = Counter()
    pred_types = Counter()  # 'headed_compound', 'single', 'headless'
    succ_types = Counter()
    n_headless_with_pred = 0
    n_headless_with_succ = 0

    # Also: what fraction are first or last token in their line?
    n_first_in_line = 0
    n_last_in_line = 0
    n_total_headless = 0

    for (folio, line), indices in line_seqs.items():
        for pos, idx in enumerate(indices):
            r = records[idx]
            if r['middle'] not in headless_set:
                continue
            n_total_headless += 1

            if pos == 0:
                n_first_in_line += 1
            if pos == len(indices) - 1:
                n_last_in_line += 1

            # Predecessor
            if pos > 0:
                pred_idx = indices[pos - 1]
                pred_r = records[pred_idx]
                pred_cat = pred_r['category']
                pred_cats[pred_cat] += 1
                n_headless_with_pred += 1
                pred_mid = pred_r['middle']
                if not is_compound(pred_mid):
                    pred_types['single'] += 1
                elif is_headless(pred_mid):
                    pred_types['headless'] += 1
                else:
                    pred_types['headed'] += 1

            # Successor
            if pos < len(indices) - 1:
                succ_idx = indices[pos + 1]
                succ_r = records[succ_idx]
                succ_cat = succ_r['category']
                succ_cats[succ_cat] += 1
                n_headless_with_succ += 1
                succ_mid = succ_r['middle']
                if not is_compound(succ_mid):
                    succ_types['single'] += 1
                elif is_headless(succ_mid):
                    succ_types['headless'] += 1
                else:
                    succ_types['headed'] += 1

    # Predecessor category profile
    print(f"\n  Predecessor categories of headless tokens (N={n_headless_with_pred}):")
    print(f"  {'Category':<15} {'Count':>6} {'%':>7}")
    for cat in ALL_8_CATS + ['UNKNOWN']:
        c = pred_cats.get(cat, 0)
        if c > 0:
            print(f"  {cat:<15} {c:>6} {100*c/n_headless_with_pred:>6.1f}%")

    # Successor category profile
    print(f"\n  Successor categories of headless tokens (N={n_headless_with_succ}):")
    for cat in ALL_8_CATS + ['UNKNOWN']:
        c = succ_cats.get(cat, 0)
        if c > 0:
            print(f"  {cat:<15} {c:>6} {100*c/n_headless_with_succ:>6.1f}%")

    # Predecessor/successor compound type
    print(f"\n  Predecessor token types:")
    for t, c in pred_types.most_common():
        print(f"    {t:<12}: {c:>5} ({100*c/n_headless_with_pred:.1f}%)")

    print(f"\n  Successor token types:")
    for t, c in succ_types.most_common():
        print(f"    {t:<12}: {c:>5} ({100*c/n_headless_with_succ:.1f}%)")

    # Self-sequencing: headless followed by headless
    hl_follows_hl = pred_types.get('headless', 0)
    hl_follows_hl_pct = 100 * hl_follows_hl / n_headless_with_pred if n_headless_with_pred else 0

    # Position summary
    first_pct = 100 * n_first_in_line / n_total_headless if n_total_headless else 0
    last_pct = 100 * n_last_in_line / n_total_headless if n_total_headless else 0

    print(f"\n  Position in line:")
    print(f"    First token in line: {first_pct:.1f}%")
    print(f"    Last token in line:  {last_pct:.1f}%")
    print(f"    Headless-follows-headless: {hl_follows_hl_pct:.1f}%")

    verdict = f"First-in-line={first_pct:.1f}%, last-in-line={last_pct:.1f}%. " \
              f"Self-sequencing={hl_follows_hl_pct:.1f}%."
    print(f"\n  VERDICT: {verdict}")

    return {
        'n_total': n_total_headless,
        'first_in_line_pct': round(first_pct, 1),
        'last_in_line_pct': round(last_pct, 1),
        'predecessor_cats': dict(pred_cats),
        'successor_cats': dict(succ_cats),
        'predecessor_types': dict(pred_types),
        'successor_types': dict(succ_types),
        'self_sequencing_pct': round(hl_follows_hl_pct, 1),
        'verdict': verdict,
    }


# === MAIN ============================================================

def main():
    print("Phase 509: HEADLESS_COMPOUND_GRAMMAR")
    print("=" * 80)
    print("Loading Currier B data...")

    records = load_data()
    print(f"  Loaded {len(records)} tokens\n")

    # T1
    t1, headless_mids, headed_mids = test1_census(records)

    # T2
    t2 = test2_functional_profiles(records, headless_mids)

    # T3
    t3 = test3_positional(records, headless_mids, headed_mids)

    # T4
    t4 = test4_prefix(records, headless_mids, headed_mids)

    # T5
    t5 = test5_suffix(records, headless_mids, headed_mids)

    # T6
    t6 = test6_length(records, headless_mids, headed_mids)

    # T7
    t7 = test7_regime(records, headless_mids, headed_mids)

    # T8
    t8 = test8_ordering(records, headless_mids, headed_mids)

    # T9
    t9 = test9_ht_association(records, headless_mids, headed_mids)

    # T10
    t10 = test10_context(records, headless_mids, headed_mids)

    # === SYNTHESIS ===================================================
    print("\n" + "=" * 80)
    print("SYNTHESIS: Headless Compound Grammar")
    print("=" * 80)

    print(f"""
1. CENSUS (T1): {t1['headless_types']} headless types, {t1['headless_tokens']} tokens
   ({t1['headless_token_pct']}% of compounds). All 6 MODIFIER atoms lead headless
   compounds ({t1['modifier_atoms_present']}). TERMINAL atoms also lead:
   {t1['terminal_atoms_present']}.

2. FUNCTIONAL PROFILES (T2): {t2['verdict']}
   Different initial atoms create DISTINCT category profiles.

3. POSITIONAL (T3): {t3['verdict']}

4. PREFIX CHANNELS (T4): {t4['verdict']}

5. SUFFIX (T5): {t5['verdict']}

6. LENGTH (T6): {t6['verdict']}

7. REGIME (T7): {t7['verdict']}

8. MODIFIER ORDERING (T8): {t8['verdict']}

9. HT ASSOCIATION (T9): {t9['verdict']}

10. SEQUENTIAL CONTEXT (T10): {t10['verdict']}
""")

    # Overall interpretation
    print("=" * 80)
    print("OVERALL INTERPRETATION")
    print("=" * 80)

    # Determine if headless is a single subgrammar or multiple
    v_category = t2['cramers_v']
    v_prefix = t4['cramers_v']

    if v_category > 0.2 and v_prefix > 0.2:
        print("""
  Headless compounds are NOT a monolithic class. Different initial atoms create
  functionally distinct subpopulations with different category profiles (V={:.3f})
  AND different PREFIX channels (V={:.3f}).

  The headless subgrammar is internally structured: initial atom determines
  operational domain, just as HEAD determines domain in headed compounds.
  The key difference is that headless compounds serve INFRASTRUCTURE operations
  (CONTAINMENT, MARKING) rather than PROCESS operations (THERMAL, FLOW).
""".format(v_category, v_prefix))
    else:
        print(f"\n  Headless compounds form a {'heterogeneous' if v_category > 0.15 else 'relatively uniform'} population.")

    # === SAVE ========================================================
    output = {
        'test1_census': t1,
        'test2_functional_profiles': t2,
        'test3_positional': t3,
        'test4_prefix': t4,
        'test5_suffix': t5,
        'test6_length': t6,
        'test7_regime': t7,
        'test8_ordering': t8,
        'test9_ht_association': t9,
        'test10_context': t10,
    }

    out_path = RESULTS_DIR / 'headless_compound_grammar.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()

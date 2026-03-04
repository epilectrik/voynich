"""
A-Exclusive MIDDLE Slot Grammar Test
======================================

Tests whether Currier A-exclusive MIDDLEs (those appearing ONLY in A, never in B)
follow the same HEAD + MOD* + TERM instruction encoding as Currier B compounds.

Background (C1393/C1394):
- 18 atoms in 4 slot roles: HEAD {a,e,o,k,t}, MOD {p,f,i,c,d,s}, TERM {l,r,h,y,m,n,k,t}
- k,t are FREE/DUAL (HEAD when first, TERM when last)
- 9/18 atoms pair-locked (standalone <10%): c,n,a,h,i,p,d,f,o
- Modifier ordering: p -> f -> i -> c -> d -> s
- Frame (HEAD+TERM) predicts 64% of operational category in B

Tests:
  1. Population Census: A-exclusive vs bridge vs B-exclusive MIDDLEs
  2. Compound Rate: fraction of multi-atom A-exclusive MIDDLEs
  3. Slot Compliance: HEAD/MOD/TERM slot assignment for A-exclusive compounds
  4. Slot Violation Rate: comparison with B's 6.4% (macro-atom model)
  5. Modifier Ordering: p->f->i->c->d->s compliance in A-exclusive
  6. Atom Frequency Distribution: compare A-exclusive vs B distributions
  7. Pair-Lock Status: are the same 9 atoms pair-locked in A?
  8. HEAD Distribution: does A favor different HEAD atoms?
  9. TERM Distribution: does A favor different TERM atoms?
 10. Frame Category Coherence: does HEAD x TERM predict category in A?
 11. Chi-squared: statistical test of slot assignment distributions A vs B
"""

import sys
import os
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats
import numpy as np

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

# Atom classifications per C1393 / C1394 / C1209 / C1210
HEAD_ONLY = {'a', 'o'}           # Always initial (86%+, 57%+)
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}  # Always terminal (71-99%)
FREE = {'k', 't'}                # HEAD when first, TERM when last
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}   # Medial modifiers
EXTENSIBLE = {'e', 'i'}          # Can repeat consecutively (C1197)

# Combined sets
HEAD_SET = HEAD_ONLY | FREE | {'e'}   # e can be HEAD (e-initial very common)
TERM_SET = TERM_ONLY | FREE           # k/t terminal when last
ALL_ATOMS = HEAD_ONLY | TERM_ONLY | FREE | MOD_ONLY | {'e'}  # 18 atoms

# Canonical modifier order (C1393)
MOD_ORDER = ['p', 'f', 'i', 'c', 'd', 's']
MOD_RANK = {m: i for i, m in enumerate(MOD_ORDER)}

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}


# --- Atom Decomposition -------------------------------------------

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


def decompose(middle):
    """Decompose a MIDDLE into HEAD, MOD_STACK, TERM.

    Returns (head, mod_stack, term, violation_type) where:
    - head: first atom if it can be HEAD
    - term: last atom if it can be TERM
    - mod_stack: everything in between
    - violation_type: None if clean, else string describing violation
    """
    atoms = atomize(middle)

    if len(atoms) == 0:
        return None, [], None, 'empty'

    if len(atoms) == 1:
        return atoms[0], [], None, None  # Single atom, no structure to violate

    # Determine HEAD: first atom
    head = None
    head_base = atoms[0][0]
    if head_base in HEAD_SET or head_base in FREE:
        head = atoms[0]
    else:
        return None, atoms, None, 'headless'

    # Determine TERM: last atom
    term = None
    term_base = atoms[-1][0]
    if len(atoms) >= 2:
        if term_base in TERM_SET:
            term = atoms[-1]
        elif term_base in MOD_ONLY:
            term = None  # Last atom is a modifier - no terminal (open compound)

    # MOD stack: everything between HEAD and TERM
    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    # Check for violations in mod stack
    violation = None
    for mod in mod_stack:
        base = mod[0]
        if base not in MOD_ONLY and base not in EXTENSIBLE:
            # A HEAD or TERM atom in modifier position
            if base in HEAD_ONLY:
                violation = f'head_in_mod({base})'
            elif base in TERM_ONLY:
                violation = f'term_in_mod({base})'
            elif base in FREE:
                pass  # k/t in middle position is allowed per C1393

    return head, mod_stack, term, violation


def check_modifier_order(mod_stack):
    """Check if modifier atoms follow the canonical p->f->i->c->d->s ordering.

    Returns (compliant, total_pairs) where compliant is number of pairs
    that follow canonical order, total_pairs is testable pairs.
    """
    mod_bases = [m[0] for m in mod_stack if m[0] in MOD_RANK]
    if len(mod_bases) < 2:
        return 0, 0  # Not testable

    compliant = 0
    total = 0
    for i in range(len(mod_bases) - 1):
        a, b = mod_bases[i], mod_bases[i + 1]
        if a in MOD_RANK and b in MOD_RANK and a != b:
            total += 1
            if MOD_RANK[a] < MOD_RANK[b]:
                compliant += 1

    return compliant, total


# --- Data Loading -------------------------------------------------

def load_data():
    """Load MIDDLEs from both Currier A and B, classify as A-exclusive, bridge, B-exclusive."""
    tx = Transcript()
    morph = Morphology()

    # Collect all MIDDLEs by system
    a_middles = Counter()
    b_middles = Counter()

    for tok in tx.currier_a():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle:
            a_middles[m.middle] += 1

    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle:
            b_middles[m.middle] += 1

    # Partition into populations
    a_set = set(a_middles.keys())
    b_set = set(b_middles.keys())

    a_exclusive = {m: a_middles[m] for m in a_set - b_set}
    bridge = {m: a_middles[m] + b_middles[m] for m in a_set & b_set}
    b_exclusive = {m: b_middles[m] for m in b_set - a_set}

    return a_middles, b_middles, a_exclusive, bridge, b_exclusive


# --- Tests --------------------------------------------------------

def test1_census(a_exclusive, bridge, b_exclusive, a_middles, b_middles):
    """Population census."""
    print("=" * 80)
    print("TEST 1: Population Census")
    print("=" * 80)

    print(f"\n  A-exclusive MIDDLEs:  {len(a_exclusive):>6} types, {sum(a_exclusive.values()):>8} tokens")
    print(f"  Bridge MIDDLEs:       {len(bridge):>6} types, {sum(bridge.values()):>8} tokens")
    print(f"  B-exclusive MIDDLEs:  {len(b_exclusive):>6} types, {sum(b_exclusive.values()):>8} tokens")
    print(f"  Total A MIDDLEs:      {len(a_middles):>6} types, {sum(a_middles.values()):>8} tokens")
    print(f"  Total B MIDDLEs:      {len(b_middles):>6} types, {sum(b_middles.values()):>8} tokens")

    # Length distribution of A-exclusive
    len_dist = Counter(len(m) for m in a_exclusive)
    print(f"\n  A-exclusive length distribution:")
    for length in sorted(len_dist):
        print(f"    len={length}: {len_dist[length]:>5} types")

    return {
        'a_exclusive_types': len(a_exclusive),
        'a_exclusive_tokens': sum(a_exclusive.values()),
        'bridge_types': len(bridge),
        'bridge_tokens': sum(bridge.values()),
        'b_exclusive_types': len(b_exclusive),
        'b_exclusive_tokens': sum(b_exclusive.values()),
        'a_exclusive_length_dist': {str(k): v for k, v in sorted(len_dist.items())},
    }


def test2_compound_rate(a_exclusive, b_middles):
    """Compound rate comparison."""
    print("\n" + "=" * 80)
    print("TEST 2: Compound Rate (multi-atom MIDDLEs)")
    print("=" * 80)

    a_single = {m: c for m, c in a_exclusive.items() if len(atomize(m)) == 1}
    a_compound = {m: c for m, c in a_exclusive.items() if len(atomize(m)) >= 2}

    b_single = {m: c for m, c in b_middles.items() if len(atomize(m)) == 1}
    b_compound = {m: c for m, c in b_middles.items() if len(atomize(m)) >= 2}

    a_comp_type_rate = len(a_compound) / len(a_exclusive) if a_exclusive else 0
    a_comp_tok_rate = sum(a_compound.values()) / sum(a_exclusive.values()) if a_exclusive else 0
    b_comp_type_rate = len(b_compound) / len(b_middles) if b_middles else 0
    b_comp_tok_rate = sum(b_compound.values()) / sum(b_middles.values()) if b_middles else 0

    print(f"\n  A-exclusive: {len(a_single)} single + {len(a_compound)} compound = {len(a_exclusive)} total")
    print(f"    Compound type rate:  {a_comp_type_rate:.1%}")
    print(f"    Compound token rate: {a_comp_tok_rate:.1%}")
    print(f"\n  B (all MIDDLEs): {len(b_single)} single + {len(b_compound)} compound = {len(b_middles)} total")
    print(f"    Compound type rate:  {b_comp_type_rate:.1%}")
    print(f"    Compound token rate: {b_comp_tok_rate:.1%}")

    # Fisher exact test on type counts: compound vs single x A-exclusive vs B
    table = [[len(a_compound), len(a_single)],
             [len(b_compound), len(b_single)]]
    odds, fisher_p = stats.fisher_exact(table)
    print(f"\n  Fisher exact (types): OR={odds:.3f}, p={fisher_p:.4f}")

    return {
        'a_single_types': len(a_single), 'a_compound_types': len(a_compound),
        'a_comp_type_rate': round(a_comp_type_rate, 4),
        'a_comp_token_rate': round(a_comp_tok_rate, 4),
        'b_single_types': len(b_single), 'b_compound_types': len(b_compound),
        'b_comp_type_rate': round(b_comp_type_rate, 4),
        'b_comp_token_rate': round(b_comp_tok_rate, 4),
        'fisher_p': fisher_p,
        'fisher_or': round(odds, 3),
    }, a_compound


def test3_slot_compliance(a_compound, b_middles):
    """Slot compliance for A-exclusive compounds."""
    print("\n" + "=" * 80)
    print("TEST 3: Slot Compliance (HEAD/MOD/TERM assignment)")
    print("=" * 80)

    def analyze_population(middles_dict, label):
        """Decompose all compounds and count violations."""
        results = {
            'total': 0, 'valid_head': 0, 'valid_term': 0,
            'headless': 0, 'open_term': 0,
            'mod_violations': 0, 'clean': 0,
            'head_dist': Counter(), 'term_dist': Counter(),
            'violations': [],
            'decompositions': {},
        }

        for mid, count in middles_dict.items():
            atoms = atomize(mid)
            if len(atoms) < 2:
                continue  # Skip single-atom

            results['total'] += 1
            head, mods, term, vtype = decompose(mid)
            results['decompositions'][mid] = (head, mods, term, vtype)

            if head is not None:
                results['valid_head'] += 1
                results['head_dist'][head[0]] += count  # Weight by token freq
            else:
                results['headless'] += 1

            if term is not None:
                results['valid_term'] += 1
                results['term_dist'][term[0]] += count
            else:
                results['open_term'] += 1

            if vtype is None:
                results['clean'] += 1
            elif vtype == 'headless':
                pass  # Already counted
            else:
                results['mod_violations'] += 1
                results['violations'].append((mid, vtype, count))

        return results

    a_results = analyze_population(a_compound, 'A-exclusive')

    # Also analyze B compounds for comparison
    b_compound = {m: c for m, c in b_middles.items() if len(atomize(m)) >= 2}
    b_results = analyze_population(b_compound, 'B')

    for label, res in [('A-exclusive', a_results), ('B (all)', b_results)]:
        total = res['total']
        if total == 0:
            print(f"\n  {label}: No compounds to analyze")
            continue

        head_rate = res['valid_head'] / total
        term_rate = res['valid_term'] / total
        clean_rate = res['clean'] / total
        headless_rate = res['headless'] / total

        print(f"\n  {label} ({total} compound types):")
        print(f"    Valid HEAD (first atom in HEAD set):  {res['valid_head']:>5} ({head_rate:.1%})")
        print(f"    Headless (first atom not in HEAD):    {res['headless']:>5} ({headless_rate:.1%})")
        print(f"    Valid TERM (last atom in TERM set):   {res['valid_term']:>5} ({term_rate:.1%})")
        print(f"    Open TERM (last atom is MOD):         {res['open_term']:>5} ({res['open_term']/total:.1%})")
        print(f"    Mod violations (HEAD/TERM in MOD pos):{res['mod_violations']:>5} ({res['mod_violations']/total:.1%})")
        print(f"    Clean decompositions:                 {res['clean']:>5} ({clean_rate:.1%})")

        if res['violations']:
            print(f"\n    Violation examples (up to 10):")
            for mid, vtype, count in sorted(res['violations'], key=lambda x: -x[2])[:10]:
                print(f"      {mid:>15}  violation={vtype}  freq={count}")

    # Statistical comparison: headless rate
    a_headless = a_results['headless']
    a_headed = a_results['valid_head']
    b_headless = b_results['headless']
    b_headed = b_results['valid_head']

    if a_headless + a_headed > 0 and b_headless + b_headed > 0:
        table = [[a_headed, a_headless], [b_headed, b_headless]]
        odds, p = stats.fisher_exact(table)
        print(f"\n  Headless rate comparison (Fisher exact):")
        print(f"    A-exclusive: {a_headless}/{a_headless+a_headed} = {a_headless/(a_headless+a_headed):.1%}")
        print(f"    B:           {b_headless}/{b_headless+b_headed} = {b_headless/(b_headless+b_headed):.1%}")
        print(f"    OR={odds:.3f}, p={p:.4f}")
    else:
        odds, p = None, None

    return {
        'a_exclusive': {
            'total': a_results['total'],
            'valid_head': a_results['valid_head'],
            'headless': a_results['headless'],
            'valid_term': a_results['valid_term'],
            'open_term': a_results['open_term'],
            'mod_violations': a_results['mod_violations'],
            'clean': a_results['clean'],
            'headless_rate': round(a_results['headless'] / a_results['total'], 4) if a_results['total'] > 0 else 0,
            'clean_rate': round(a_results['clean'] / a_results['total'], 4) if a_results['total'] > 0 else 0,
        },
        'b': {
            'total': b_results['total'],
            'valid_head': b_results['valid_head'],
            'headless': b_results['headless'],
            'valid_term': b_results['valid_term'],
            'open_term': b_results['open_term'],
            'mod_violations': b_results['mod_violations'],
            'clean': b_results['clean'],
            'headless_rate': round(b_results['headless'] / b_results['total'], 4) if b_results['total'] > 0 else 0,
            'clean_rate': round(b_results['clean'] / b_results['total'], 4) if b_results['total'] > 0 else 0,
        },
        'fisher_headless_p': p,
        'fisher_headless_or': round(odds, 3) if odds is not None else None,
    }, a_results, b_results


def test4_modifier_ordering(a_results, b_results):
    """Check modifier ordering compliance."""
    print("\n" + "=" * 80)
    print("TEST 4: Modifier Ordering (p->f->i->c->d->s)")
    print("=" * 80)

    results = {}

    for label, res in [('A-exclusive', a_results), ('B', b_results)]:
        total_compliant = 0
        total_pairs = 0
        examples = []

        for mid, (head, mods, term, vtype) in res['decompositions'].items():
            if head is None or len(mods) < 2:
                continue
            c, t = check_modifier_order(mods)
            total_compliant += c
            total_pairs += t
            if t > 0:
                mod_str = '->'.join(m[0] for m in mods if m[0] in MOD_RANK)
                examples.append((mid, mod_str, c, t))

        if total_pairs > 0:
            rate = total_compliant / total_pairs
            print(f"\n  {label}:")
            print(f"    Compliant modifier pairs: {total_compliant}/{total_pairs} = {rate:.1%}")
            print(f"    Compounds with 2+ modifiers: {len(examples)}")

            if examples:
                print(f"    Examples (up to 10):")
                for mid, mod_str, c, t in sorted(examples, key=lambda x: -x[3])[:10]:
                    status = 'OK' if c == t else f'VIOLATION ({c}/{t})'
                    print(f"      {mid:>15}  mods: {mod_str:>15}  {status}")
        else:
            rate = None
            print(f"\n  {label}: No testable modifier pairs")

        results[label] = {
            'compliant_pairs': total_compliant,
            'total_pairs': total_pairs,
            'compliance_rate': round(rate, 4) if rate is not None else None,
            'compounds_with_multi_mod': len(examples),
        }

    # Statistical comparison if both have data
    a_data = results.get('A-exclusive', {})
    b_data = results.get('B', {})
    if a_data.get('total_pairs', 0) > 0 and b_data.get('total_pairs', 0) > 0:
        a_c, a_t = a_data['compliant_pairs'], a_data['total_pairs']
        b_c, b_t = b_data['compliant_pairs'], b_data['total_pairs']
        table = [[a_c, a_t - a_c], [b_c, b_t - b_c]]
        odds, p = stats.fisher_exact(table)
        print(f"\n  Order compliance comparison (Fisher exact): OR={odds:.3f}, p={p:.4f}")
        results['fisher_p'] = p
        results['fisher_or'] = round(odds, 3)

    return results


def test5_atom_frequency(a_exclusive, b_middles):
    """Compare atom frequency distributions between A-exclusive and B."""
    print("\n" + "=" * 80)
    print("TEST 5: Atom Frequency Distribution")
    print("=" * 80)

    def get_atom_dist(middles_dict):
        """Count atom occurrences across all MIDDLEs (type-weighted, not token-weighted)."""
        counts = Counter()
        for mid in middles_dict:
            for atom in atomize(mid):
                base = atom[0]
                counts[base] += 1
        return counts

    a_dist = get_atom_dist(a_exclusive)
    b_dist = get_atom_dist(b_middles)

    # Normalize
    a_total = sum(a_dist.values())
    b_total = sum(b_dist.values())

    all_atoms_seen = sorted(set(list(a_dist.keys()) + list(b_dist.keys())))

    print(f"\n  {'Atom':>6} {'A-excl':>8} {'A%':>7} {'B':>8} {'B%':>7} {'A/B Ratio':>10}")
    print(f"  {'-'*6} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*10}")

    ratios = {}
    for atom in all_atoms_seen:
        a_n = a_dist.get(atom, 0)
        b_n = b_dist.get(atom, 0)
        a_pct = 100 * a_n / a_total if a_total > 0 else 0
        b_pct = 100 * b_n / b_total if b_total > 0 else 0
        ratio = a_pct / b_pct if b_pct > 0 else float('inf')
        ratios[atom] = ratio
        marker = '**' if abs(ratio - 1.0) > 0.5 else ''
        print(f"  {atom:>6} {a_n:>8} {a_pct:>6.1f}% {b_n:>8} {b_pct:>6.1f}% {ratio:>9.2f}x {marker}")

    # Chi-squared test on full distributions
    a_vec = [a_dist.get(atom, 0) for atom in all_atoms_seen]
    b_vec = [b_dist.get(atom, 0) for atom in all_atoms_seen]
    contingency = [a_vec, b_vec]
    chi2, p, dof, expected = stats.chi2_contingency(contingency)
    n = a_total + b_total
    k = len(all_atoms_seen)
    cramers_v = (chi2 / (n * (min(2, k) - 1))) ** 0.5 if n > 0 else 0

    print(f"\n  Chi-squared: chi2={chi2:.1f}, p={p:.2e}, V={cramers_v:.3f}")

    # Top divergent atoms
    print(f"\n  Most A-enriched: {sorted(ratios.items(), key=lambda x: -x[1])[:3]}")
    print(f"  Most B-enriched: {sorted(ratios.items(), key=lambda x: x[1])[:3]}")

    return {
        'a_atom_dist': {atom: a_dist.get(atom, 0) for atom in all_atoms_seen},
        'b_atom_dist': {atom: b_dist.get(atom, 0) for atom in all_atoms_seen},
        'chi2': round(chi2, 1),
        'p': p,
        'cramers_v': round(cramers_v, 3),
        'ratios': {atom: round(ratios[atom], 3) if ratios[atom] != float('inf') else 'inf' for atom in all_atoms_seen},
    }


def test6_pair_lock(a_exclusive, b_middles, a_middles):
    """Check if atoms that are pair-locked in B are also pair-locked in A (using FULL A, not just exclusive).

    Note: A-exclusive MIDDLEs are by definition all compound (single atoms like k, e, etc.
    are shared with B and thus in the bridge set). So we must use FULL A MIDDLE inventory
    to test standalone rates — otherwise every atom trivially shows 0% standalone.
    """
    print("\n" + "=" * 80)
    print("TEST 6: Pair-Lock Status (standalone < 10%)")
    print("  NOTE: Using FULL A inventory (not just A-exclusive) for standalone rates")
    print("=" * 80)

    def standalone_rates(middles_dict):
        """For each atom, what fraction of its appearances are as standalone single-atom MIDDLEs?"""
        standalone_count = Counter()
        total_count = Counter()

        for mid, count in middles_dict.items():
            atoms = atomize(mid)
            for atom in atoms:
                base = atom[0]
                total_count[base] += count
            if len(atoms) == 1:
                base = atoms[0][0]
                standalone_count[base] += count

        rates = {}
        for atom in total_count:
            if total_count[atom] > 0:
                rates[atom] = standalone_count.get(atom, 0) / total_count[atom]
            else:
                rates[atom] = 0
        return rates, standalone_count, total_count

    # Use FULL A and FULL B for fair comparison
    a_rates, a_stand, a_total = standalone_rates(a_middles)
    b_rates, b_stand, b_total = standalone_rates(b_middles)

    # Known B pair-locked atoms (C1393): c, n, a, h, i, p, d, f, o
    b_pairlocked = {'c', 'n', 'a', 'h', 'i', 'p', 'd', 'f', 'o'}

    all_atoms_seen = sorted(set(list(a_rates.keys()) + list(b_rates.keys())))

    print(f"\n  {'Atom':>6} {'A-stand%':>9} {'A-lock?':>8} {'B-stand%':>9} {'B-lock?':>8} {'Match':>6}")
    print(f"  {'-'*6} {'-'*9} {'-'*8} {'-'*9} {'-'*8} {'-'*6}")

    matches = 0
    testable = 0
    for atom in all_atoms_seen:
        a_r = a_rates.get(atom, 0)
        b_r = b_rates.get(atom, 0)
        a_lock = a_r < 0.10
        b_lock = b_r < 0.10

        # Only count if atom appears in both
        if atom in a_rates and atom in b_rates:
            testable += 1
            match = a_lock == b_lock
            if match:
                matches += 1
            match_str = 'YES' if match else 'NO'
        else:
            match_str = 'n/a'

        a_lock_str = 'LOCK' if a_lock else 'FREE'
        b_lock_str = 'LOCK' if b_lock else 'FREE'

        print(f"  {atom:>6} {a_r:>8.1%} {a_lock_str:>8} {b_r:>8.1%} {b_lock_str:>8} {match_str:>6}")

    agreement = matches / testable if testable > 0 else 0
    print(f"\n  Agreement: {matches}/{testable} = {agreement:.1%}")

    return {
        'a_standalone_rates': {atom: round(a_rates.get(atom, 0), 4) for atom in all_atoms_seen},
        'b_standalone_rates': {atom: round(b_rates.get(atom, 0), 4) for atom in all_atoms_seen},
        'pair_lock_agreement': round(agreement, 4),
        'matches': matches,
        'testable': testable,
    }


def test7_head_term_dist(a_results, b_results):
    """Compare HEAD and TERM distributions between A and B compounds."""
    print("\n" + "=" * 80)
    print("TEST 7: HEAD and TERM Distribution Comparison")
    print("=" * 80)

    result_data = {}

    for slot_name in ['HEAD', 'TERM']:
        dist_key = f'{slot_name.lower()}_dist'
        a_dist = a_results.get(dist_key, Counter())
        b_dist = b_results.get(dist_key, Counter())

        a_total = sum(a_dist.values())
        b_total = sum(b_dist.values())

        all_vals = sorted(set(list(a_dist.keys()) + list(b_dist.keys())))

        print(f"\n  --- {slot_name} Distribution (token-weighted) ---")
        print(f"  {'Val':>6} {'A-excl':>8} {'A%':>7} {'B':>8} {'B%':>7} {'A/B':>7}")

        for val in all_vals:
            a_n = a_dist.get(val, 0)
            b_n = b_dist.get(val, 0)
            a_pct = 100 * a_n / a_total if a_total > 0 else 0
            b_pct = 100 * b_n / b_total if b_total > 0 else 0
            ratio = a_pct / b_pct if b_pct > 0 else float('inf')
            print(f"  {val:>6} {a_n:>8} {a_pct:>6.1f}% {b_n:>8} {b_pct:>6.1f}% {ratio:>6.2f}x")

        # Chi-squared
        if a_total > 0 and b_total > 0:
            a_vec = [a_dist.get(v, 0) for v in all_vals]
            b_vec = [b_dist.get(v, 0) for v in all_vals]
            # Add small pseudocount to avoid zero rows
            a_vec_safe = [max(x, 0.5) for x in a_vec]
            b_vec_safe = [max(x, 0.5) for x in b_vec]
            try:
                chi2, p, dof, expected = stats.chi2_contingency([a_vec_safe, b_vec_safe])
                n = sum(a_vec_safe) + sum(b_vec_safe)
                k = len(all_vals)
                v = (chi2 / (n * (min(2, k) - 1))) ** 0.5 if n > 0 else 0
                print(f"  Chi2={chi2:.1f}, p={p:.2e}, V={v:.3f}")
            except Exception as e:
                chi2, p, v = 0, 1, 0
                print(f"  (Chi2 test failed: {e})")
        else:
            chi2, p, v = 0, 1, 0

        result_data[slot_name] = {
            'a_dist': {str(k): int(v) for k, v in a_dist.items()},
            'b_dist': {str(k): int(v) for k, v in b_dist.items()},
            'chi2': round(chi2, 1),
            'p': p,
            'cramers_v': round(v, 3),
        }

    return result_data


def classify_any_middle(cc, middle):
    """Classify any MIDDLE by atom plurality vote, even if not in dictionary.

    Uses CategoryClassifier's built-in classify first; falls back to
    direct atom vote for MIDDLEs not in middle_dictionary.json.
    """
    result = cc.classify(middle)
    if result is not None:
        return result
    # Fall back to atom plurality vote (same method as CategoryClassifier._auto_assign)
    return cc._auto_assign(middle) or 'UNKNOWN'


def test8_frame_category(a_compound, a_exclusive, cc, b_middles):
    """Check if HEAD x TERM predicts category in A-exclusive compounds.

    Also computes B frame coherence for direct comparison.
    """
    print("\n" + "=" * 80)
    print("TEST 8: Frame Category Coherence (A-exclusive vs B)")
    print("=" * 80)

    def compute_frame_coherence(compounds, label, classifier):
        """Compute frame -> category coherence for a set of compounds."""
        frame_data = defaultdict(lambda: {'types': set(), 'tokens': 0, 'cats': Counter()})

        for mid, count in compounds.items():
            head, mods, term, vtype = decompose(mid)
            if head is None:
                continue

            head_key = head[0]
            term_key = term[0] if term else '-'
            cat = classify_any_middle(classifier, mid)

            frame = (head_key, term_key)
            frame_data[frame]['types'].add(mid)
            frame_data[frame]['tokens'] += count
            frame_data[frame]['cats'][cat] += count

        total_correct = 0
        total_tokens = 0
        for (h, t), data in frame_data.items():
            if data['cats']:
                dom = data['cats'].most_common(1)[0][1]
                total_correct += dom
                total_tokens += data['tokens']

        coherence = total_correct / total_tokens if total_tokens > 0 else 0
        return frame_data, coherence, total_tokens

    # A-exclusive
    a_frame_data, a_coherence, a_tokens = compute_frame_coherence(a_compound, 'A-exclusive', cc)

    # B for comparison
    b_compound = {m: c for m, c in b_middles.items() if len(atomize(m)) >= 2}
    b_frame_data, b_coherence, b_tokens = compute_frame_coherence(b_compound, 'B', cc)

    print(f"\n  A-exclusive frame category coherence: {a_coherence:.1%} ({a_tokens} tokens)")
    print(f"  B frame category coherence:           {b_coherence:.1%} ({b_tokens} tokens)")
    print(f"  (B baseline from C1394: ~64%)")

    # Check UNKNOWN rate
    a_unknown = 0
    a_total = 0
    for mid in a_compound:
        cat = classify_any_middle(cc, mid)
        a_total += 1
        if cat == 'UNKNOWN':
            a_unknown += 1
    print(f"\n  A-exclusive UNKNOWN rate: {a_unknown}/{a_total} = {a_unknown/a_total:.1%}")

    frame_data = a_frame_data  # Use A for the detailed display

    # Overall coherence
    total_correct = 0
    total_tokens = 0
    for (h, t), data in frame_data.items():
        if data['cats']:
            dom = data['cats'].most_common(1)[0][1]
            total_correct += dom
            total_tokens += data['tokens']

    coherence = total_correct / total_tokens if total_tokens > 0 else 0
    print(f"\n  Overall frame -> category coherence: {coherence:.1%}")
    print(f"  (B baseline from C1394: ~64%)")

    # Top frames
    print(f"\n  {'Frame':>8} {'Types':>6} {'Tokens':>7} {'Dom.Cat':>12} {'Coher%':>7}")
    for (h, t), data in sorted(frame_data.items(), key=lambda x: -x[1]['tokens'])[:15]:
        dom = data['cats'].most_common(1)[0]
        pct = 100 * dom[1] / data['tokens'] if data['tokens'] > 0 else 0
        examples = sorted(data['types'], key=lambda m: -a_exclusive.get(m, 0))[:3]
        ex_str = ', '.join(examples)
        print(f"  {h}->{t:>3}  {len(data['types']):>5}  {data['tokens']:>6}  {dom[0]:>12} {pct:>6.1f}%  {ex_str}")

    return {
        'frame_category_coherence': round(coherence, 4),
        'total_frames': len(frame_data),
        'total_tokens': total_tokens,
        'top_frames': [
            {
                'frame': f"{h}->{t}",
                'types': len(data['types']),
                'tokens': data['tokens'],
                'dominant_cat': data['cats'].most_common(1)[0][0] if data['cats'] else None,
                'coherence': round(data['cats'].most_common(1)[0][1] / data['tokens'], 4) if data['tokens'] > 0 else 0,
            }
            for (h, t), data in sorted(frame_data.items(), key=lambda x: -x[1]['tokens'])[:15]
        ]
    }


def test9_slot_chi2(a_results, b_results):
    """Chi-squared comparison of slot assignment distributions."""
    print("\n" + "=" * 80)
    print("TEST 9: Slot Assignment Distribution Comparison (A vs B)")
    print("=" * 80)

    # Count atoms in each slot position for A-exclusive and B
    def count_slot_assignments(decomp_results):
        slot_counts = {'HEAD': Counter(), 'MOD': Counter(), 'TERM': Counter()}
        for mid, (head, mods, term, vtype) in decomp_results.get('decompositions', {}).items():
            if head is not None:
                slot_counts['HEAD'][head[0]] += 1
            for mod in mods:
                slot_counts['MOD'][mod[0]] += 1
            if term is not None:
                slot_counts['TERM'][term[0]] += 1
        return slot_counts

    a_slots = count_slot_assignments(a_results)
    b_slots = count_slot_assignments(b_results)

    results = {}
    for slot in ['HEAD', 'MOD', 'TERM']:
        a_dist = a_slots[slot]
        b_dist = b_slots[slot]
        all_vals = sorted(set(list(a_dist.keys()) + list(b_dist.keys())))

        a_total = sum(a_dist.values())
        b_total = sum(b_dist.values())

        print(f"\n  --- {slot} Slot ---")
        print(f"  {'Atom':>6} {'A-excl':>8} {'A%':>7} {'B':>8} {'B%':>7}")

        for val in all_vals:
            a_n = a_dist.get(val, 0)
            b_n = b_dist.get(val, 0)
            a_pct = 100 * a_n / a_total if a_total > 0 else 0
            b_pct = 100 * b_n / b_total if b_total > 0 else 0
            print(f"  {val:>6} {a_n:>8} {a_pct:>6.1f}% {b_n:>8} {b_pct:>6.1f}%")

        if a_total > 0 and b_total > 0 and len(all_vals) > 1:
            a_vec = [a_dist.get(v, 0) + 0.5 for v in all_vals]
            b_vec = [b_dist.get(v, 0) + 0.5 for v in all_vals]
            try:
                chi2, p, dof, expected = stats.chi2_contingency([a_vec, b_vec])
                n = sum(a_vec) + sum(b_vec)
                k = len(all_vals)
                v = (chi2 / (n * (min(2, k) - 1))) ** 0.5 if n > 0 else 0
                print(f"  Chi2={chi2:.1f}, p={p:.2e}, V={v:.3f}")
                results[slot] = {'chi2': round(chi2, 1), 'p': p, 'cramers_v': round(v, 3)}
            except Exception as e:
                print(f"  (Chi2 failed: {e})")
                results[slot] = {'chi2': 0, 'p': 1, 'cramers_v': 0}
        else:
            results[slot] = {'chi2': 0, 'p': 1, 'cramers_v': 0}

    return results


def test10_top_a_exclusive_examples(a_compound, cc):
    """Show top A-exclusive compounds with full decomposition."""
    print("\n" + "=" * 80)
    print("TEST 10: Top A-Exclusive Compound Examples")
    print("=" * 80)

    entries = []
    for mid, count in sorted(a_compound.items(), key=lambda x: -x[1])[:50]:
        head, mods, term, vtype = decompose(mid)
        cat = classify_any_middle(cc, mid)

        head_str = head if head else '-'
        mod_str = '+'.join(mods) if mods else '-'
        term_str = term if term else '-'
        atoms = atomize(mid)

        entries.append({
            'middle': mid,
            'freq': count,
            'atoms': atoms,
            'head': head_str,
            'mods': mod_str,
            'term': term_str,
            'category': cat,
            'violation': vtype,
        })

    print(f"\n  {'MIDDLE':>15} {'FREQ':>5} {'HEAD':>5} {'MODS':>12} {'TERM':>5} {'CAT':>12} {'VIOLATION':>15}")
    print(f"  {'-'*15} {'-'*5} {'-'*5} {'-'*12} {'-'*5} {'-'*12} {'-'*15}")

    for e in entries:
        v_str = e['violation'] if e['violation'] else '-'
        print(f"  {e['middle']:>15} {e['freq']:>5} {e['head']:>5} {e['mods']:>12} {e['term']:>5} {e['category']:>12} {v_str:>15}")

    return entries[:50]


# --- Synthesis ----------------------------------------------------

def synthesis(t1, t2, t3, t4, t5, t6, t7, t8, t9, t10):
    """Pull together all tests into a verdict."""
    print("\n" + "=" * 80)
    print("SYNTHESIS: Does A-Exclusive MIDDLE Grammar Match B?")
    print("=" * 80)

    verdicts = []

    # 1. Compound rate
    a_rate = t2['a_comp_type_rate']
    b_rate = t2['b_comp_type_rate']
    print(f"\n  1. Compound rate: A={a_rate:.1%} vs B={b_rate:.1%}")
    if abs(a_rate - b_rate) < 0.10:
        verdicts.append(('Compound rate', 'MATCH', f'A={a_rate:.1%} vs B={b_rate:.1%}'))
    else:
        verdicts.append(('Compound rate', 'DIVERGE', f'A={a_rate:.1%} vs B={b_rate:.1%}'))

    # 2. Headless rate
    a_headless = t3['a_exclusive']['headless_rate']
    b_headless = t3['b']['headless_rate']
    print(f"  2. Headless rate: A={a_headless:.1%} vs B={b_headless:.1%}")
    if abs(a_headless - b_headless) < 0.10:
        verdicts.append(('Headless rate', 'MATCH', f'A={a_headless:.1%} vs B={b_headless:.1%}'))
    else:
        verdicts.append(('Headless rate', 'DIVERGE', f'A={a_headless:.1%} vs B={b_headless:.1%}'))

    # 3. Clean decomposition rate
    a_clean = t3['a_exclusive']['clean_rate']
    b_clean = t3['b']['clean_rate']
    print(f"  3. Clean decomposition: A={a_clean:.1%} vs B={b_clean:.1%}")
    if abs(a_clean - b_clean) < 0.10:
        verdicts.append(('Clean decomposition', 'MATCH', f'A={a_clean:.1%} vs B={b_clean:.1%}'))
    else:
        verdicts.append(('Clean decomposition', 'DIVERGE', f'A={a_clean:.1%} vs B={b_clean:.1%}'))

    # 4. Modifier ordering
    a_mod_rate = t4.get('A-exclusive', {}).get('compliance_rate')
    b_mod_rate = t4.get('B', {}).get('compliance_rate')
    if a_mod_rate is not None and b_mod_rate is not None:
        print(f"  4. Modifier order compliance: A={a_mod_rate:.1%} vs B={b_mod_rate:.1%}")
        if abs(a_mod_rate - b_mod_rate) < 0.15:
            verdicts.append(('Modifier order', 'MATCH', f'A={a_mod_rate:.1%} vs B={b_mod_rate:.1%}'))
        else:
            verdicts.append(('Modifier order', 'DIVERGE', f'A={a_mod_rate:.1%} vs B={b_mod_rate:.1%}'))
    else:
        verdicts.append(('Modifier order', 'UNTESTABLE', 'insufficient data'))

    # 5. Atom distribution
    v_atoms = t5['cramers_v']
    print(f"  5. Atom distribution divergence: V={v_atoms:.3f}")
    if v_atoms < 0.15:
        verdicts.append(('Atom distribution', 'MATCH', f'V={v_atoms:.3f}'))
    elif v_atoms < 0.30:
        verdicts.append(('Atom distribution', 'PARTIAL', f'V={v_atoms:.3f}'))
    else:
        verdicts.append(('Atom distribution', 'DIVERGE', f'V={v_atoms:.3f}'))

    # 6. Pair-lock agreement
    agreement = t6['pair_lock_agreement']
    print(f"  6. Pair-lock agreement: {agreement:.1%}")
    if agreement >= 0.80:
        verdicts.append(('Pair-lock', 'MATCH', f'{agreement:.1%}'))
    elif agreement >= 0.60:
        verdicts.append(('Pair-lock', 'PARTIAL', f'{agreement:.1%}'))
    else:
        verdicts.append(('Pair-lock', 'DIVERGE', f'{agreement:.1%}'))

    # 7. Frame category coherence
    a_coherence = t8['frame_category_coherence']
    print(f"  7. Frame category coherence: A={a_coherence:.1%} (B baseline ~64%)")
    if a_coherence >= 0.55:
        verdicts.append(('Frame coherence', 'MATCH', f'A={a_coherence:.1%}'))
    elif a_coherence >= 0.40:
        verdicts.append(('Frame coherence', 'PARTIAL', f'A={a_coherence:.1%}'))
    else:
        verdicts.append(('Frame coherence', 'DIVERGE', f'A={a_coherence:.1%}'))

    # Summary
    match_count = sum(1 for v in verdicts if v[1] == 'MATCH')
    partial_count = sum(1 for v in verdicts if v[1] == 'PARTIAL')
    diverge_count = sum(1 for v in verdicts if v[1] == 'DIVERGE')
    total = len([v for v in verdicts if v[1] != 'UNTESTABLE'])

    print(f"\n  Summary: {match_count} MATCH, {partial_count} PARTIAL, {diverge_count} DIVERGE / {total} testable")

    if match_count >= total * 0.7:
        overall = 'SHARED_GRAMMAR'
        print(f"\n  VERDICT: {overall}")
        print("  A-exclusive MIDDLEs follow the same HEAD+MOD*+TERM instruction encoding as B.")
        print("  The instruction architecture is MANUSCRIPT-WIDE.")
    elif diverge_count >= total * 0.5:
        overall = 'DIVERGENT_GRAMMAR'
        print(f"\n  VERDICT: {overall}")
        print("  A-exclusive MIDDLEs have systematically different composition rules from B.")
    else:
        overall = 'PARTIALLY_SHARED'
        print(f"\n  VERDICT: {overall}")
        print("  A-exclusive MIDDLEs share the slot grammar framework but with quantitative differences.")

    return {
        'verdicts': [{'test': v[0], 'result': v[1], 'detail': v[2]} for v in verdicts],
        'match_count': match_count,
        'partial_count': partial_count,
        'diverge_count': diverge_count,
        'testable': total,
        'overall_verdict': overall,
    }


# --- Main ---------------------------------------------------------

def main():
    print("A-Exclusive MIDDLE Slot Grammar Test")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    a_middles, b_middles, a_exclusive, bridge, b_exclusive = load_data()
    cc = CategoryClassifier()

    # Run tests
    t1 = test1_census(a_exclusive, bridge, b_exclusive, a_middles, b_middles)
    t2, a_compound = test2_compound_rate(a_exclusive, b_middles)

    if not a_compound:
        print("\nNo A-exclusive compounds found. Cannot proceed.")
        return

    t3, a_decomp_results, b_decomp_results = test3_slot_compliance(a_compound, b_middles)

    # Need decompositions as dicts for downstream
    a_res_dict = {
        'decompositions': a_decomp_results['decompositions'],
        'head_dist': a_decomp_results['head_dist'],
        'term_dist': a_decomp_results['term_dist'],
    }
    b_res_dict = {
        'decompositions': b_decomp_results['decompositions'],
        'head_dist': b_decomp_results['head_dist'],
        'term_dist': b_decomp_results['term_dist'],
    }

    t4 = test4_modifier_ordering(a_res_dict, b_res_dict)
    t5 = test5_atom_frequency(a_exclusive, b_middles)
    t6 = test6_pair_lock(a_exclusive, b_middles, a_middles)
    t7 = test7_head_term_dist(a_res_dict, b_res_dict)
    t8 = test8_frame_category(a_compound, a_exclusive, cc, b_middles)
    t9 = test9_slot_chi2(a_res_dict, b_res_dict)
    t10 = test10_top_a_exclusive_examples(a_compound, cc)

    synth = synthesis(t1, t2, t3, t4, t5, t6, t7, t8, t9, t10)

    # Save results
    json_results = {
        'test1_census': t1,
        'test2_compound_rate': t2,
        'test3_slot_compliance': t3,
        'test4_modifier_ordering': {k: v for k, v in t4.items() if k not in ('decompositions',)},
        'test5_atom_frequency': t5,
        'test6_pair_lock': t6,
        'test7_head_term_dist': t7,
        'test8_frame_category': t8,
        'test9_slot_chi2': t9,
        'test10_top_examples': [
            {
                'middle': e['middle'],
                'freq': e['freq'],
                'head': e['head'],
                'mods': e['mods'],
                'term': e['term'],
                'category': e['category'],
                'violation': e['violation'],
            }
            for e in t10
        ],
        'synthesis': synth,
    }

    json_path = RESULTS_DIR / 'a_exclusive_slot_grammar.json'
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"\nJSON results saved to: {json_path}")


if __name__ == '__main__':
    main()

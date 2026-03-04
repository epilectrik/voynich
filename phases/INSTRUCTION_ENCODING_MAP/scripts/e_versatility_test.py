"""
Phase 506 Test 4: e-Atom Versatility
=====================================

C1394 found e-headed compounds are the most category-diverse (37% purity).
This tests whether e is a true operational domain ("cooling") or a generic/
default HEAD that takes its category from modifiers.

Tests:
  1. e-compound category diversity (entropy comparison across HEADs)
  2. Modifier dominance under e (does modifier determine category more?)
  3. e as default (is e a pre-HEAD modifier in disguise?)
  4. e-extensibility in HEAD position (does ee/eee change category?)
  5. e in non-HEAD positions (modifier-position behavior)
  6. Cross-HEAD comparison (same frame, different HEAD -> same category?)
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

import random
random.seed(42)

# --- Configuration ------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom slot classifications (C1209/C1210/C1393)
HEAD_ONLY = {'a', 'o'}
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}
EXTENSIBLE = {'e', 'i'}
HEAD_SET = HEAD_ONLY | FREE | {'e'}
TERM_SET = TERM_ONLY | FREE
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}

ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}


# --- Utilities ----------------------------------------------------

def atomize(middle):
    """Split MIDDLE into atoms, collapsing extensible runs (ee, ii)."""
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
    """Decompose MIDDLE into (HEAD, MOD_STACK, TERM)."""
    atoms = atomize(middle)
    if not atoms:
        return None, [], None
    if len(atoms) == 1:
        return atoms[0], [], None

    head = None
    head_base = atoms[0][0]
    if head_base in HEAD_SET or head_base in FREE:
        head = atoms[0]
    else:
        return None, atoms, None

    term = None
    if len(atoms) >= 2:
        term_base = atoms[-1][0]
        if term_base in TERM_SET:
            term = atoms[-1]

    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def shannon_entropy(counts):
    """Shannon entropy in bits from a dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def cramers_v(contingency):
    """Cramer's V from a contingency table (dict of dicts)."""
    # Build matrix
    rows = sorted(contingency.keys())
    all_cols = set()
    for r in rows:
        all_cols.update(contingency[r].keys())
    cols = sorted(all_cols)
    if not rows or not cols:
        return 0.0

    # Total
    N = sum(contingency[r].get(c, 0) for r in rows for c in cols)
    if N == 0:
        return 0.0

    # Row and column totals
    row_totals = {r: sum(contingency[r].get(c, 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency[r].get(c, 0) for r in rows) for c in cols}

    # Chi-squared
    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = contingency[r].get(c, 0)
            exp = row_totals[r] * col_totals[c] / N
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    k = min(len(rows), len(cols))
    if k <= 1:
        return 0.0
    return math.sqrt(chi2 / (N * (k - 1)))


# --- Data Loading -------------------------------------------------

def load_data():
    """Load Currier B MIDDLEs with frequencies, categories, and decompositions."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    middles = Counter()
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue
        m = morph.extract(tok.word)
        if m.middle:
            middles[m.middle] += 1

    categories = {}
    for mid in middles:
        categories[mid] = cc.classify(mid) or 'UNKNOWN'

    return middles, categories


# --- Test 1: e-Compound Category Diversity -------------------------

def test1_category_diversity(middles, categories):
    """Compare category entropy across HEAD atoms."""
    print("=" * 70)
    print("TEST 1: e-Compound Category Diversity")
    print("=" * 70)

    # Group compounds by HEAD atom
    head_cats = defaultdict(lambda: Counter())  # head_base -> category counts
    head_tokens = defaultdict(int)

    for mid, freq in middles.items():
        head, mods, term = decompose(mid)
        if head is None:
            continue
        head_base = head[0]
        if head_base not in HEAD_ATOMS:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue
        head_cats[head_base][cat] += freq
        head_tokens[head_base] += freq

    print("\nRaw entropy by HEAD atom:")
    print(f"  {'HEAD':<6} {'Tokens':>8} {'Entropy':>8} {'Max Cat':>14} {'Max %':>8} {'Cats >10%':>10}")
    print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*14} {'-'*8} {'-'*10}")

    results = {}
    for h in sorted(HEAD_ATOMS):
        if h not in head_cats:
            continue
        ent = shannon_entropy(head_cats[h])
        total = sum(head_cats[h].values())
        dom_cat = head_cats[h].most_common(1)[0]
        dom_pct = dom_cat[1] / total * 100
        cats_gt10 = sum(1 for c, v in head_cats[h].items() if v / total > 0.10)
        print(f"  {h:<6} {total:>8} {ent:>8.3f} {dom_cat[0]:>14} {dom_pct:>7.1f}% {cats_gt10:>10}")
        results[h] = {
            'tokens': total,
            'entropy': round(ent, 4),
            'dominant_category': dom_cat[0],
            'dominant_pct': round(dom_pct, 1),
            'cats_above_10pct': cats_gt10,
            'distribution': {c: v for c, v in head_cats[h].most_common()},
        }

    # Subsample control: equalize token counts
    min_tokens = min(head_tokens[h] for h in HEAD_ATOMS if h in head_cats)
    print(f"\n  Subsample control (N={min_tokens} per HEAD, 1000 iterations):")

    # Build per-HEAD token-level lists
    head_token_lists = defaultdict(list)
    for mid, freq in middles.items():
        head, mods, term = decompose(mid)
        if head is None:
            continue
        head_base = head[0]
        if head_base not in HEAD_ATOMS:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue
        head_token_lists[head_base].extend([cat] * freq)

    N_ITER = 1000
    sub_entropies = defaultdict(list)
    for _ in range(N_ITER):
        for h in HEAD_ATOMS:
            if h not in head_token_lists or len(head_token_lists[h]) < min_tokens:
                continue
            sample = random.sample(head_token_lists[h], min_tokens)
            counts = Counter(sample)
            sub_entropies[h].append(shannon_entropy(counts))

    print(f"  {'HEAD':<6} {'Mean Ent':>9} {'Std':>8} {'Min':>8} {'Max':>8}")
    print(f"  {'-'*6} {'-'*9} {'-'*8} {'-'*8} {'-'*8}")
    for h in sorted(HEAD_ATOMS):
        if h not in sub_entropies:
            continue
        vals = sub_entropies[h]
        mean_e = sum(vals) / len(vals)
        std_e = (sum((v - mean_e)**2 for v in vals) / len(vals)) ** 0.5
        results[h]['subsampled_entropy_mean'] = round(mean_e, 4)
        results[h]['subsampled_entropy_std'] = round(std_e, 4)
        print(f"  {h:<6} {mean_e:>9.3f} {std_e:>8.4f} {min(vals):>8.3f} {max(vals):>8.3f}")

    # Verdict
    e_ent = results.get('e', {}).get('entropy', 0)
    other_ents = [results[h]['entropy'] for h in HEAD_ATOMS if h != 'e' and h in results]
    e_rank = sum(1 for x in other_ents if x >= e_ent)  # 0 = highest

    e_sub = results.get('e', {}).get('subsampled_entropy_mean', 0)
    other_subs = [results[h].get('subsampled_entropy_mean', 0) for h in HEAD_ATOMS if h != 'e' and h in results]
    e_sub_rank = sum(1 for x in other_subs if x >= e_sub)

    print(f"\n  VERDICT: e raw entropy rank {e_rank + 1}/5 (1=highest)")
    print(f"  VERDICT: e subsampled entropy rank {e_sub_rank + 1}/5")
    if e_rank == 0 and e_sub_rank == 0:
        print(f"  => e is genuinely the most category-diverse HEAD, survives sample-size control")
    elif e_sub_rank > 0:
        print(f"  => e diversity partially explained by sample size")

    return results


# --- Test 2: Modifier Dominance Under e ----------------------------

def test2_modifier_dominance(middles, categories):
    """Test if modifiers determine category more strongly under e than other HEADs."""
    print("\n" + "=" * 70)
    print("TEST 2: Modifier Dominance Under e")
    print("=" * 70)

    # For each HEAD, build contingency: modifier_string -> category
    head_contingencies = defaultdict(lambda: defaultdict(Counter))
    head_mod_counts = defaultdict(int)

    for mid, freq in middles.items():
        head, mods, term = decompose(mid)
        if head is None or not mods:
            continue
        head_base = head[0]
        if head_base not in HEAD_ATOMS:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue

        mod_str = '+'.join(m[0] for m in mods)  # Use base chars
        head_contingencies[head_base][mod_str][cat] += freq
        head_mod_counts[head_base] += freq

    print(f"\n  Cramer's V(modifier -> category) by HEAD:")
    print(f"  {'HEAD':<6} {'N tokens':>9} {'N mods':>7} {'V':>8} {'Interpretation':>30}")
    print(f"  {'-'*6} {'-'*9} {'-'*7} {'-'*8} {'-'*30}")

    results = {}
    for h in sorted(HEAD_ATOMS):
        if h not in head_contingencies or len(head_contingencies[h]) < 2:
            continue
        v = cramers_v(head_contingencies[h])
        n_mods = len(head_contingencies[h])
        n_tok = head_mod_counts[h]
        interp = "MOD dominates" if v > 0.5 else "MOD moderate" if v > 0.3 else "HEAD dominates"
        print(f"  {h:<6} {n_tok:>9} {n_mods:>7} {v:>8.3f} {interp:>30}")
        results[h] = {
            'n_tokens': n_tok,
            'n_modifiers': n_mods,
            'cramers_v': round(v, 4),
            'interpretation': interp,
        }

    # Also: for e, show the top modifiers and their categories
    if 'e' in head_contingencies:
        print(f"\n  Top modifiers under e-HEAD:")
        print(f"  {'Modifier':<12} {'Tokens':>8} {'Dom Cat':>14} {'Dom %':>8}")
        print(f"  {'-'*12} {'-'*8} {'-'*14} {'-'*8}")
        mod_totals = {}
        for mod_str, cat_counts in head_contingencies['e'].items():
            total = sum(cat_counts.values())
            mod_totals[mod_str] = total
        for mod_str in sorted(mod_totals, key=mod_totals.get, reverse=True)[:15]:
            cat_counts = head_contingencies['e'][mod_str]
            total = sum(cat_counts.values())
            dom = cat_counts.most_common(1)[0]
            print(f"  {mod_str:<12} {total:>8} {dom[0]:>14} {dom[1]/total*100:>7.1f}%")

    # Verdict
    e_v = results.get('e', {}).get('cramers_v', 0)
    other_vs = [results[h]['cramers_v'] for h in HEAD_ATOMS if h != 'e' and h in results]
    e_highest = all(e_v >= v for v in other_vs) if other_vs else False

    print(f"\n  VERDICT: e V={e_v:.3f}", end="")
    if e_highest:
        print(" (HIGHEST) => modifiers dominate category under e more than other HEADs")
        print("  => e is relatively TRANSPARENT to modifier effects")
    else:
        higher = [h for h in HEAD_ATOMS if h != 'e' and h in results and results[h]['cramers_v'] > e_v]
        print(f" (not highest; {', '.join(higher)} higher)")
        print("  => e is NOT uniquely transparent; modifier dominance is similar across HEADs")

    return results


# --- Test 3: e as Default -----------------------------------------

def test3_e_as_default(middles, categories):
    """Test if e in HEAD position is acting as a pre-HEAD modifier."""
    print("\n" + "=" * 70)
    print("TEST 3: e as Default HEAD")
    print("=" * 70)

    # 3a: For e-initial compounds with 3+ atoms, what's the second atom?
    print("\n  3a: Second atom in e-initial 3+ atom compounds:")
    second_atoms = Counter()
    e_compounds_3plus = {}
    for mid, freq in middles.items():
        atoms = atomize(mid)
        if len(atoms) < 3:
            continue
        if atoms[0][0] != 'e':
            continue
        second_base = atoms[1][0]
        second_atoms[second_base] += freq
        e_compounds_3plus[mid] = freq

    total_3plus = sum(second_atoms.values())
    print(f"  Total e-initial 3+ atom tokens: {total_3plus}")
    print(f"  {'2nd Atom':<10} {'Tokens':>8} {'%':>8} {'HEAD?':>8}")
    print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8}")
    for atom, count in second_atoms.most_common():
        is_head = "YES" if atom in HEAD_ATOMS else "no"
        print(f"  {atom:<10} {count:>8} {count/total_3plus*100:>7.1f}% {is_head:>8}")

    head_fraction = sum(c for a, c in second_atoms.items() if a in HEAD_ATOMS) / total_3plus if total_3plus else 0

    # 3b: Compare ed (e+d) vs ked (k+e+d) — is e playing the same role?
    print(f"\n  3b: Role comparison: e in ed vs e in ked")
    pairs = [
        ('ed', 'ked'), ('ey', 'key'), ('edy', 'kedy'),
        ('ek', 'oek'), ('el', 'oel'), ('eod', 'keod'),
    ]
    print(f"  {'e-initial':<12} {'cat':>14} {'other':<12} {'cat':>14} {'Same?':>8}")
    print(f"  {'-'*12} {'-'*14} {'-'*12} {'-'*14} {'-'*8}")
    for e_form, other_form in pairs:
        e_cat = categories.get(e_form, '(absent)')
        o_cat = categories.get(other_form, '(absent)')
        same = "YES" if e_cat == o_cat and e_cat != '(absent)' else "no" if e_cat != '(absent)' and o_cat != '(absent)' else "N/A"
        print(f"  {e_form:<12} {e_cat:>14} {other_form:<12} {o_cat:>14} {same:>8}")

    # 3c: HEAD reassignment test — if we strip e and use next atom as HEAD
    print(f"\n  3c: HEAD reassignment test (strip initial e, use 2nd atom as HEAD)")
    # For e-initial 3+ atom compounds, compare:
    #   original category (with e as HEAD)
    #   reassigned category (next atom as HEAD, via vote without leading e)
    cc = CategoryClassifier()
    match_count = 0
    improve_count = 0
    total_test = 0
    for mid, freq in e_compounds_3plus.items():
        orig_cat = categories.get(mid, 'UNKNOWN')
        if orig_cat == 'UNKNOWN':
            continue
        atoms = atomize(mid)
        stripped = ''.join(atoms[1:])  # Remove leading e/ee/eee
        stripped_cat = cc.classify(stripped) or 'UNKNOWN'
        if stripped_cat == 'UNKNOWN':
            continue
        total_test += freq
        if stripped_cat == orig_cat:
            match_count += freq

    if total_test > 0:
        print(f"  Tokens tested: {total_test}")
        print(f"  Same category after stripping e: {match_count} ({match_count/total_test*100:.1f}%)")
        print(f"  Category CHANGED by stripping e: {total_test - match_count} ({(total_test-match_count)/total_test*100:.1f}%)")
    else:
        print("  (insufficient data)")

    result = {
        'second_atom_distribution': {a: c for a, c in second_atoms.most_common()},
        'head_class_second_fraction': round(head_fraction, 4),
        'total_3plus_tokens': total_3plus,
        'strip_e_test': {
            'tokens_tested': total_test,
            'same_category': match_count,
            'same_pct': round(match_count / total_test * 100, 1) if total_test else 0,
        },
    }

    # Verdict
    print(f"\n  VERDICT:")
    if head_fraction > 0.5:
        print(f"  => {head_fraction*100:.1f}% of second atoms are HEAD-class -> e MAY be a pre-HEAD modifier")
    else:
        print(f"  => Only {head_fraction*100:.1f}% of second atoms are HEAD-class -> e is genuine HEAD")

    if total_test > 0 and match_count / total_test > 0.8:
        print(f"  => Stripping e rarely changes category ({match_count/total_test*100:.1f}% same) -> e is TRANSPARENT")
    elif total_test > 0:
        print(f"  => Stripping e changes category {(total_test-match_count)/total_test*100:.1f}% of the time -> e CONTRIBUTES to category")

    return result


# --- Test 4: e-Extensibility in HEAD Position ----------------------

def test4_e_extensibility(middles, categories):
    """Test whether e-depth in HEAD position modulates category."""
    print("\n" + "=" * 70)
    print("TEST 4: e-Extensibility in HEAD Position")
    print("=" * 70)

    # Group by (e_depth, rest_of_middle) -> category counts
    depth_groups = defaultdict(lambda: Counter())  # (depth, rest) -> cat counts
    depth_totals = defaultdict(lambda: Counter())  # depth -> cat counts

    for mid, freq in middles.items():
        atoms = atomize(mid)
        if not atoms or atoms[0][0] != 'e':
            continue
        e_depth = len(atoms[0])  # 1='e', 2='ee', 3='eee', etc
        rest = ''.join(atoms[1:])
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue
        depth_groups[(e_depth, rest)][cat] += freq
        depth_totals[e_depth][cat] += freq

    # Overall category distribution by e-depth
    print(f"\n  Category distribution by e-depth (HEAD position):")
    print(f"  {'Depth':<8} {'Tokens':>8} {'Entropy':>8} {'Top Cat':>14} {'Top %':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*14} {'-'*8}")

    depth_results = {}
    for depth in sorted(depth_totals.keys()):
        ent = shannon_entropy(depth_totals[depth])
        total = sum(depth_totals[depth].values())
        dom = depth_totals[depth].most_common(1)[0]
        print(f"  e{'e'*(depth-1):<6} {total:>8} {ent:>8.3f} {dom[0]:>14} {dom[1]/total*100:>7.1f}%")
        depth_results[depth] = {
            'tokens': total,
            'entropy': round(ent, 4),
            'dominant_cat': dom[0],
            'dominant_pct': round(dom[1] / total * 100, 1),
            'distribution': {c: v for c, v in depth_totals[depth].most_common()},
        }

    # For shared frames: compare category across e-depths
    print(f"\n  Shared frames across e-depths (e+X vs ee+X):")
    frame_pairs = defaultdict(dict)  # rest -> {depth: cat_counts}
    for (depth, rest), cat_counts in depth_groups.items():
        total = sum(cat_counts.values())
        if total >= 5:  # minimum for comparison
            frame_pairs[rest][depth] = cat_counts

    matched = 0
    shifted = 0
    shift_examples = []
    for rest in sorted(frame_pairs, key=lambda r: sum(sum(v.values()) for v in frame_pairs[r].values()), reverse=True):
        depths = frame_pairs[rest]
        if len(depths) < 2:
            continue
        sorted_depths = sorted(depths.keys())
        for i in range(len(sorted_depths) - 1):
            d1, d2 = sorted_depths[i], sorted_depths[i + 1]
            dom1 = depths[d1].most_common(1)[0][0]
            dom2 = depths[d2].most_common(1)[0][0]
            n1 = sum(depths[d1].values())
            n2 = sum(depths[d2].values())
            if dom1 == dom2:
                matched += 1
            else:
                shifted += 1
                if len(shift_examples) < 10:
                    shift_examples.append({
                        'rest': rest,
                        'd1': d1, 'd2': d2,
                        'cat1': dom1, 'cat2': dom2,
                        'n1': n1, 'n2': n2,
                    })

    total_pairs = matched + shifted
    print(f"  Frame pairs compared: {total_pairs}")
    if total_pairs > 0:
        print(f"  Same dominant category: {matched} ({matched/total_pairs*100:.1f}%)")
        print(f"  Category shifted: {shifted} ({shifted/total_pairs*100:.1f}%)")
        if shift_examples:
            print(f"\n  Category shift examples:")
            for ex in shift_examples:
                form1 = 'e' * ex['d1'] + ex['rest']
                form2 = 'e' * ex['d2'] + ex['rest']
                print(f"    {form1} ({ex['cat1']}, n={ex['n1']}) vs {form2} ({ex['cat2']}, n={ex['n2']})")

    result = {
        'depth_distributions': {str(d): v for d, v in depth_results.items()},
        'frame_pairs_compared': total_pairs,
        'same_category': matched,
        'shifted': shifted,
        'shift_examples': shift_examples[:5],
    }

    print(f"\n  VERDICT:")
    if total_pairs > 0 and shifted / total_pairs > 0.3:
        print(f"  => e-depth changes category in {shifted/total_pairs*100:.1f}% of frames -> e-depth is FUNCTIONAL")
    elif total_pairs > 0:
        print(f"  => e-depth preserves category in {matched/total_pairs*100:.1f}% of frames -> e-depth modulates INTENSITY, not domain")
    else:
        print(f"  => insufficient shared frames for comparison")

    return result


# --- Test 5: e in Non-HEAD Positions -------------------------------

def test5_e_nonhead(middles, categories):
    """Test e's behavior in modifier position vs canonical modifiers."""
    print("\n" + "=" * 70)
    print("TEST 5: e in Non-HEAD Positions")
    print("=" * 70)

    # Find compounds where e is in modifier position (not first, not last for 3+ atoms)
    e_mod_cats = Counter()     # When e is in MODIFIER position
    e_head_cats = Counter()    # When e is in HEAD position
    other_mod_cats = defaultdict(Counter)  # Other modifier atoms -> cat counts
    e_mod_tokens = 0
    e_head_tokens = 0

    for mid, freq in middles.items():
        atoms = atomize(mid)
        if len(atoms) < 2:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue

        head, mods, term = decompose(mid)
        if head is None:
            continue
        head_base = head[0]

        # Check if e is the HEAD
        if head_base == 'e':
            e_head_cats[cat] += freq
            e_head_tokens += freq

        # Check for e in modifier position
        for mod in mods:
            mod_base = mod[0]
            if mod_base == 'e':
                e_mod_cats[cat] += freq
                e_mod_tokens += freq
            elif mod_base in MOD_ONLY:
                other_mod_cats[mod_base][cat] += freq

    print(f"\n  e in modifier position: {e_mod_tokens} tokens")
    print(f"  e in HEAD position: {e_head_tokens} tokens")

    if e_mod_tokens > 0:
        print(f"\n  Category distribution when e is MODIFIER:")
        for cat, count in e_mod_cats.most_common():
            print(f"    {cat:<14} {count:>6} ({count/e_mod_tokens*100:.1f}%)")

    if e_head_tokens > 0:
        print(f"\n  Category distribution when e is HEAD:")
        for cat, count in e_head_cats.most_common():
            print(f"    {cat:<14} {count:>6} ({count/e_head_tokens*100:.1f}%)")

    # Compare V for e-in-modifier vs canonical modifiers
    # For each modifier atom, compute V(modifier_presence -> category)
    # Build contingency: for MIDDLEs containing this atom in modifier position
    # vs not containing it, what's the category distribution?
    print(f"\n  Cramer's V for modifier atoms (effect on category when present in MOD slot):")
    print(f"  {'Atom':<8} {'V':>8} {'N tokens':>10}")
    print(f"  {'-'*8} {'-'*8} {'-'*10}")

    # For e-as-modifier, build contingency: {has_e_mod: {cat: count}}
    all_mod_atoms = list(MOD_ONLY) + ['e']
    mod_v_results = {}

    for test_atom in sorted(all_mod_atoms):
        # Contingency: "present" vs "absent" as rows, categories as columns
        contingency = {'present': Counter(), 'absent': Counter()}
        for mid, freq in middles.items():
            atoms = atomize(mid)
            if len(atoms) < 3:  # Need HEAD + MOD + TERM minimum
                continue
            cat = categories.get(mid, 'UNKNOWN')
            if cat == 'UNKNOWN':
                continue
            head, mods, term = decompose(mid)
            if head is None or not mods:
                continue

            mod_bases = [m[0] for m in mods]
            if test_atom in mod_bases:
                contingency['present'][cat] += freq
            else:
                contingency['absent'][cat] += freq

        n_present = sum(contingency['present'].values())
        n_total = n_present + sum(contingency['absent'].values())
        if n_present >= 10 and n_total >= 50:
            v = cramers_v(contingency)
            label = " <-- e" if test_atom == 'e' else ""
            print(f"  {test_atom:<8} {v:>8.3f} {n_present:>10}{label}")
            mod_v_results[test_atom] = {'v': round(v, 4), 'n_present': n_present}

    result = {
        'e_mod_tokens': e_mod_tokens,
        'e_head_tokens': e_head_tokens,
        'e_mod_distribution': {c: v for c, v in e_mod_cats.most_common()},
        'e_head_distribution': {c: v for c, v in e_head_cats.most_common()},
        'modifier_v_values': mod_v_results,
    }

    print(f"\n  VERDICT:")
    if e_mod_tokens < 50:
        print(f"  => Only {e_mod_tokens} tokens with e in modifier position; too rare for conclusion")
    else:
        e_mod_ent = shannon_entropy(e_mod_cats)
        e_head_ent = shannon_entropy(e_head_cats)
        print(f"  => e-as-modifier entropy: {e_mod_ent:.3f}, e-as-HEAD entropy: {e_head_ent:.3f}")
        if abs(e_mod_ent - e_head_ent) < 0.3:
            print(f"  => Similar diversity in both positions -> e behaves consistently")
        elif e_mod_ent < e_head_ent:
            print(f"  => Less diverse as modifier -> e is more focused (category-shifting) in MOD position")
        else:
            print(f"  => More diverse as modifier -> e remains versatile even outside HEAD")

    return result


# --- Test 6: Cross-HEAD Comparison --------------------------------

def test6_cross_head(middles, categories):
    """Compare category distributions for the same frame under different HEADs."""
    print("\n" + "=" * 70)
    print("TEST 6: Cross-HEAD Frame Comparison")
    print("=" * 70)

    # Build: frame (mod+term string) -> {head: {cat: count}}
    frame_heads = defaultdict(lambda: defaultdict(Counter))
    frame_totals = defaultdict(lambda: defaultdict(int))

    for mid, freq in middles.items():
        head, mods, term = decompose(mid)
        if head is None:
            continue
        head_base = head[0]
        if head_base not in HEAD_ATOMS:
            continue
        cat = categories.get(mid, 'UNKNOWN')
        if cat == 'UNKNOWN':
            continue

        # Frame = everything after HEAD
        mod_str = ''.join(m[0] for m in mods) if mods else ''
        term_str = term[0] if term else '-'
        frame = f"{mod_str}|{term_str}"
        frame_heads[frame][head_base][cat] += freq
        frame_totals[frame][head_base] += freq

    # Find frames shared by multiple HEADs
    shared_frames = {f: d for f, d in frame_heads.items() if len(d) >= 2}
    print(f"\n  Frames shared by 2+ HEADs: {len(shared_frames)}")

    # For each shared frame, compare dominant categories
    same_dom = 0
    diff_dom = 0
    examples = []

    # Also compute pairwise JSD for each frame
    from math import log2

    def jsd(p, q):
        """Jensen-Shannon divergence."""
        all_keys = set(p.keys()) | set(q.keys())
        p_total = sum(p.values())
        q_total = sum(q.values())
        if p_total == 0 or q_total == 0:
            return 1.0
        divergence = 0.0
        for k in all_keys:
            pk = p.get(k, 0) / p_total
            qk = q.get(k, 0) / q_total
            mk = (pk + qk) / 2
            if pk > 0 and mk > 0:
                divergence += 0.5 * pk * log2(pk / mk)
            if qk > 0 and mk > 0:
                divergence += 0.5 * qk * log2(qk / mk)
        return divergence

    pair_jsds = defaultdict(list)  # (head1, head2) -> list of JSD values
    min_tokens_per_head = 10

    for frame, head_data in sorted(shared_frames.items(),
                                     key=lambda x: sum(sum(v.values()) for v in x[1].values()),
                                     reverse=True):
        # Filter to heads with enough tokens
        eligible_heads = {h: cats for h, cats in head_data.items()
                         if sum(cats.values()) >= min_tokens_per_head}
        if len(eligible_heads) < 2:
            continue

        heads = sorted(eligible_heads.keys())
        dominants = {h: eligible_heads[h].most_common(1)[0][0] for h in heads}

        # Pairwise comparisons
        for i in range(len(heads)):
            for j in range(i + 1, len(heads)):
                h1, h2 = heads[i], heads[j]
                j_val = jsd(eligible_heads[h1], eligible_heads[h2])
                pair_jsds[(h1, h2)].append(j_val)
                if dominants[h1] == dominants[h2]:
                    same_dom += 1
                else:
                    diff_dom += 1

        # Collect examples
        if len(examples) < 15:
            mod_part, term_part = frame.split('|')
            for h in heads:
                total_h = sum(eligible_heads[h].values())
                dom_h = eligible_heads[h].most_common(1)[0]
                mid_str = h + (mod_part if mod_part else '') + (term_part if term_part != '-' else '')
                if len(examples) < 15:
                    pass  # We'll print them below

    total_comparisons = same_dom + diff_dom
    print(f"  Pairwise HEAD comparisons (min {min_tokens_per_head} tokens): {total_comparisons}")
    if total_comparisons > 0:
        print(f"  Same dominant category: {same_dom} ({same_dom/total_comparisons*100:.1f}%)")
        print(f"  Different dominant: {diff_dom} ({diff_dom/total_comparisons*100:.1f}%)")

    # Mean JSD by HEAD pair
    print(f"\n  Mean JSD between HEAD pairs:")
    print(f"  {'Pair':<10} {'Mean JSD':>10} {'N frames':>10}")
    print(f"  {'-'*10} {'-'*10} {'-'*10}")
    pair_jsd_results = {}
    for (h1, h2) in sorted(pair_jsds.keys()):
        vals = pair_jsds[(h1, h2)]
        mean_j = sum(vals) / len(vals) if vals else 0
        print(f"  {h1}-{h2:<7} {mean_j:>10.3f} {len(vals):>10}")
        pair_jsd_results[f"{h1}-{h2}"] = {'mean_jsd': round(mean_j, 4), 'n_frames': len(vals)}

    # Show concrete examples: top shared frames
    print(f"\n  Top shared frames (detailed):")
    shown = 0
    for frame, head_data in sorted(shared_frames.items(),
                                     key=lambda x: sum(sum(v.values()) for v in x[1].values()),
                                     reverse=True):
        eligible = {h: cats for h, cats in head_data.items()
                   if sum(cats.values()) >= min_tokens_per_head}
        if len(eligible) < 2:
            continue
        mod_part, term_part = frame.split('|')
        term_display = term_part if term_part != '-' else ''
        print(f"\n    Frame: _+{mod_part if mod_part else '(none)'}+{term_display if term_display else '(none)'}")
        for h in sorted(eligible.keys()):
            total_h = sum(eligible[h].values())
            dom = eligible[h].most_common(1)[0]
            mid_str = h + mod_part + term_display
            print(f"      {mid_str:<12} n={total_h:>5} -> {dom[0]:<14} ({dom[1]/total_h*100:.0f}%)")
        shown += 1
        if shown >= 10:
            break

    # Compute: is e's divergence from other HEADs higher or lower than inter-HEAD average?
    e_pairs = {k: v for k, v in pair_jsd_results.items() if 'e' in k.split('-')}
    non_e_pairs = {k: v for k, v in pair_jsd_results.items() if 'e' not in k.split('-')}
    e_mean = sum(v['mean_jsd'] for v in e_pairs.values()) / len(e_pairs) if e_pairs else 0
    non_e_mean = sum(v['mean_jsd'] for v in non_e_pairs.values()) / len(non_e_pairs) if non_e_pairs else 0

    result = {
        'shared_frames': len(shared_frames),
        'total_comparisons': total_comparisons,
        'same_dominant': same_dom,
        'different_dominant': diff_dom,
        'same_pct': round(same_dom / total_comparisons * 100, 1) if total_comparisons else 0,
        'pair_jsd': pair_jsd_results,
        'e_pair_mean_jsd': round(e_mean, 4),
        'non_e_pair_mean_jsd': round(non_e_mean, 4),
    }

    print(f"\n  VERDICT:")
    print(f"  => e-involving pairs mean JSD: {e_mean:.3f}")
    print(f"  => non-e pairs mean JSD: {non_e_mean:.3f}")
    if total_comparisons > 0 and diff_dom / total_comparisons > 0.5:
        print(f"  => HEADs MATTER: different HEAD changes category {diff_dom/total_comparisons*100:.1f}% of the time")
        if e_mean > non_e_mean * 1.2:
            print(f"  => e is MORE divergent from other HEADs -> e provides UNIQUE domain information")
        elif e_mean < non_e_mean * 0.8:
            print(f"  => e is LESS divergent -> e converges with other HEADs (more generic)")
        else:
            print(f"  => e divergence is TYPICAL among HEADs")
    elif total_comparisons > 0:
        print(f"  => HEADs share category {same_dom/total_comparisons*100:.1f}% -> HEAD less important than frame")

    return result


# --- Main ---------------------------------------------------------

def main():
    print("Phase 506 Test 4: e-Atom Versatility")
    print("=" * 70)

    middles, categories = load_data()
    compound_middles = {m: f for m, f in middles.items() if len(atomize(m)) >= 2}
    print(f"Total unique MIDDLEs: {len(middles)}")
    print(f"Compound MIDDLEs (2+ atoms): {len(compound_middles)}")
    print(f"Total tokens: {sum(middles.values())}")
    print(f"Compound tokens: {sum(compound_middles.values())}")

    results = {}
    results['test1'] = test1_category_diversity(middles, categories)
    results['test2'] = test2_modifier_dominance(middles, categories)
    results['test3'] = test3_e_as_default(middles, categories)
    results['test4'] = test4_e_extensibility(middles, categories)
    results['test5'] = test5_e_nonhead(middles, categories)
    results['test6'] = test6_cross_head(middles, categories)

    # --- Overall Synthesis -----------------------------------------
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # Collect key metrics
    e_ent = results['test1'].get('e', {}).get('entropy', 0)
    e_sub_ent = results['test1'].get('e', {}).get('subsampled_entropy_mean', 0)
    other_sub_ents = [results['test1'][h].get('subsampled_entropy_mean', 0)
                      for h in HEAD_ATOMS if h != 'e' and h in results['test1']]
    e_ent_rank = sum(1 for x in other_sub_ents if x >= e_sub_ent) + 1

    e_mod_v = results['test2'].get('e', {}).get('cramers_v', 0)
    other_mod_vs = [results['test2'][h]['cramers_v'] for h in HEAD_ATOMS
                    if h != 'e' and h in results['test2']]
    e_mod_rank = sum(1 for x in other_mod_vs if x >= e_mod_v) + 1

    strip_same = results['test3'].get('strip_e_test', {}).get('same_pct', 0)
    head_2nd = results['test3'].get('head_class_second_fraction', 0)

    e_pair_jsd = results['test6'].get('e_pair_mean_jsd', 0)
    non_e_jsd = results['test6'].get('non_e_pair_mean_jsd', 0)

    print(f"\n  Key findings:")
    print(f"  1. e entropy rank: {e_ent_rank}/5 (subsampled) - {'MOST diverse' if e_ent_rank == 1 else 'NOT most diverse'}")
    print(f"  2. Modifier V under e: {e_mod_v:.3f} (rank {e_mod_rank}/5) - {'HIGHEST' if e_mod_rank == 1 else 'not highest'}")
    print(f"  3. Stripping e preserves category: {strip_same:.1f}% - {'TRANSPARENT' if strip_same > 70 else 'CONTRIBUTES' if strip_same < 50 else 'MIXED'}")
    print(f"  4. 2nd atom is HEAD-class: {head_2nd*100:.1f}%")
    print(f"  5. e-involving pair JSD: {e_pair_jsd:.3f} vs non-e: {non_e_jsd:.3f}")

    # Classification
    transparent_score = 0
    domain_score = 0

    if e_ent_rank == 1:
        transparent_score += 1
    else:
        domain_score += 1

    if e_mod_rank == 1:
        transparent_score += 1
    else:
        domain_score += 1

    if strip_same > 70:
        transparent_score += 1
    elif strip_same < 50:
        domain_score += 1

    if head_2nd > 0.5:
        transparent_score += 1
    else:
        domain_score += 1

    if e_pair_jsd < non_e_jsd * 0.8:
        transparent_score += 1
    elif e_pair_jsd > non_e_jsd * 1.2:
        domain_score += 1

    print(f"\n  Transparent HEAD score: {transparent_score}/5")
    print(f"  Domain-specific HEAD score: {domain_score}/5")

    if transparent_score >= 4:
        verdict = "e is a TRANSPARENT/DEFAULT HEAD - category determined primarily by modifiers/terminals"
    elif domain_score >= 4:
        verdict = "e is a DOMAIN-SPECIFIC HEAD - genuinely encodes 'cooling/thermal stabilization'"
    elif transparent_score > domain_score:
        verdict = "e LEANS transparent but retains some domain specificity"
    elif domain_score > transparent_score:
        verdict = "e LEANS domain-specific but is more versatile than k/t/a/o"
    else:
        verdict = "e is MIXED - neither purely transparent nor purely domain-locked"

    print(f"\n  FINAL VERDICT: {verdict}")

    results['synthesis'] = {
        'e_entropy_rank': e_ent_rank,
        'e_modifier_v_rank': e_mod_rank,
        'strip_e_same_pct': strip_same,
        'head_second_fraction': round(head_2nd, 4),
        'e_pair_jsd': e_pair_jsd,
        'non_e_pair_jsd': non_e_jsd,
        'transparent_score': transparent_score,
        'domain_score': domain_score,
        'verdict': verdict,
    }

    # Save
    out_path = RESULTS_DIR / 'e_versatility_test.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()

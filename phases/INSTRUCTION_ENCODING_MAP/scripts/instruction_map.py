"""
Phase 505: Instruction Encoding Map
====================================

Maps compound MIDDLEs as HEAD + MOD* + TERM instruction encodings.

Decomposition rules (from C1393 / C1209 / C1210):
- HEAD atoms: {a, e, o} always initial + {k, t} when in first position
- TERM atoms: {l, r, h, y, m, n} always terminal + {k, t} when in last position
- MOD atoms: {p, c, i, f, d, s} medial modifiers
- Only e and i can repeat (extensibility, C1197)
- k and t are FREE: HEAD when first, TERM when last

Tests:
  1. HEAD x TERM frame matrix
  2. Modifier injection effects (top frames)
  3. Individual modifier category effects
  4. Full compound decomposition table
  5. Modifier order semantics
"""

import sys
import os
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

# --- Configuration ---------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Atom classifications per C1209 / C1210 / C1393
HEAD_ONLY = {'a', 'o'}       # Always initial (86%+, 57%+)
TERM_ONLY = {'l', 'r', 'h', 'y', 'm', 'n'}  # Always terminal (71-99%)
FREE = {'k', 't'}             # HEAD when first, TERM when last
MOD_ONLY = {'p', 'c', 'i', 'f', 'd', 's'}   # Medial modifiers
EXTENSIBLE = {'e', 'i'}       # Can repeat consecutively (C1197)

# Combined sets for position assignment
HEAD_SET = HEAD_ONLY | FREE | {'e'}   # e can be HEAD (e-initial very common)
TERM_SET = TERM_ONLY | FREE           # k/t terminal when last

# Atom glosses from C1195
ATOM_GLOSS = {
    'a': 'yield', 'e': 'cool', 'o': 'arrange', 'k': 'heat', 't': 'transfer',
    'p': 'pause', 'c': 'adjust', 'i': 'iterate', 'f': 'flag',
    'd': 'mark', 's': 'sequence',
    'l': 'state', 'r': 'respond', 'h': 'watch', 'y': 'end',
    'm': 'final', 'n': 'halt',
}

# --- Data Loading ----------------------------------------------

def load_data():
    """Load Currier B MIDDLEs with frequencies and categories."""
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

    # Classify each
    categories = {}
    for mid in middles:
        categories[mid] = cc.classify(mid) or 'UNKNOWN'

    return middles, categories

# --- Atom Decomposition ---------------------------------------

def atomize(middle):
    """Split a MIDDLE string into individual atoms, respecting extensibility.

    Returns list of atom strings. Extended atoms (ee, eee, ii) are kept
    as single units for counting but decomposed for slot assignment.
    """
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        # Collect runs of extensible atoms
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

    Returns (head, mod_stack, term) where:
    - head: first atom if it can be HEAD
    - term: last atom if it can be TERM
    - mod_stack: everything in between

    For single atoms: (atom, [], None)
    For 2-atom: (head, [], term) if both qualify
    """
    atoms = atomize(middle)

    if len(atoms) == 0:
        return None, [], None

    if len(atoms) == 1:
        return atoms[0], [], None

    # Determine HEAD: first atom
    head = None
    head_base = atoms[0][0]  # First character of first atom (handles 'ee', 'ii')
    if head_base in HEAD_SET or head_base in FREE:
        head = atoms[0]
    else:
        # First atom isn't a valid HEAD - treat whole thing as unstructured
        return None, atoms, None

    # Determine TERM: last atom
    term = None
    term_base = atoms[-1][0]  # First char of last atom
    if len(atoms) >= 2:
        if term_base in TERM_SET:
            term = atoms[-1]
        elif term_base in MOD_ONLY:
            # Last atom is a modifier - no terminal
            term = None

    # MOD stack: everything between HEAD and TERM
    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def compose_gloss(head, mod_stack, term):
    """Build a composed gloss string from decomposition."""
    parts = []
    if head:
        base = head[0]
        g = ATOM_GLOSS.get(base, '?')
        if len(head) > 1:
            g = f"{g}({'x'.join([base]*len(head))})"
        parts.append(g)
    for mod in mod_stack:
        base = mod[0]
        g = ATOM_GLOSS.get(base, '?')
        if len(mod) > 1:
            g = f"{g}({'x'.join([base]*len(mod))})"
        parts.append(g)
    if term:
        base = term[0]
        g = ATOM_GLOSS.get(base, '?')
        if len(term) > 1:
            g = f"{g}({'x'.join([base]*len(term))})"
        parts.append(g)
    return ' + '.join(parts)


# --- Test 1: HEAD x TERM Frame Matrix -------------------------

def test1_frame_matrix(middles, categories):
    """Build HEAD x TERM frame matrix for all compound MIDDLEs."""
    print("=" * 80)
    print("TEST 1: HEAD x TERM Frame Matrix")
    print("=" * 80)

    # Only compound MIDDLEs (length >= 2)
    compounds = {m: c for m, c in middles.items() if len(m) >= 2}
    print(f"\nTotal compound MIDDLEs: {len(compounds)} types, {sum(compounds.values())} tokens")

    # Decompose all compounds
    frame_data = defaultdict(lambda: {'types': set(), 'tokens': 0, 'cats': Counter()})
    decompositions = {}

    unstructured = 0
    for mid, count in compounds.items():
        head, mods, term = decompose(mid)
        decompositions[mid] = (head, mods, term)

        if head is None:
            unstructured += 1
            continue

        head_key = head[0] if head else '?'  # Base char
        term_key = term[0] if term else '-'   # '-' means no terminal

        frame = (head_key, term_key)
        frame_data[frame]['types'].add(mid)
        frame_data[frame]['tokens'] += count
        cat = categories.get(mid, 'UNKNOWN')
        frame_data[frame]['cats'][cat] += count

    print(f"Unstructured (no valid HEAD): {unstructured}")

    # Get all HEAD and TERM values
    heads_seen = sorted(set(f[0] for f in frame_data))
    terms_seen = sorted(set(f[1] for f in frame_data))

    # Print matrix - types
    print(f"\n{'Frame Matrix (unique types)':^80}")
    print(f"{'':>6}", end='')
    for t in terms_seen:
        print(f"  {t:>5}", end='')
    print(f"  {'TOTAL':>6}")

    for h in heads_seen:
        print(f"{h:>6}", end='')
        row_total = 0
        for t in terms_seen:
            val = len(frame_data[(h, t)]['types'])
            row_total += val
            if val > 0:
                print(f"  {val:>5}", end='')
            else:
                print(f"  {'·':>5}", end='')
        print(f"  {row_total:>6}")

    # Print matrix - tokens
    print(f"\n{'Frame Matrix (token counts)':^80}")
    print(f"{'':>6}", end='')
    for t in terms_seen:
        print(f"  {t:>5}", end='')
    print(f"  {'TOTAL':>6}")

    for h in heads_seen:
        print(f"{h:>6}", end='')
        row_total = 0
        for t in terms_seen:
            val = frame_data[(h, t)]['tokens']
            row_total += val
            if val > 0:
                print(f"  {val:>5}", end='')
            else:
                print(f"  {'·':>5}", end='')
        print(f"  {row_total:>6}")

    # Print matrix - dominant category
    print(f"\n{'Frame Matrix (dominant category)':^80}")
    print(f"{'':>6}", end='')
    for t in terms_seen:
        print(f"  {t:>8}", end='')
    print()

    for h in heads_seen:
        print(f"{h:>6}", end='')
        for t in terms_seen:
            cats = frame_data[(h, t)]['cats']
            if cats:
                dom = cats.most_common(1)[0][0]
                print(f"  {dom[:8]:>8}", end='')
            else:
                print(f"  {'·':>8}", end='')
        print()

    # Top 15 frames by token count
    print(f"\n{'Top 15 Frames by Token Count':^80}")
    print(f"{'Frame':>10} {'Types':>6} {'Tokens':>7} {'Dom.Cat':>12} {'Cat%':>6}  Examples")

    sorted_frames = sorted(frame_data.items(), key=lambda x: -x[1]['tokens'])
    for (h, t), data in sorted_frames[:15]:
        dom_cat = data['cats'].most_common(1)[0]
        pct = 100 * dom_cat[1] / data['tokens']
        examples = sorted(data['types'], key=lambda m: -middles[m])[:4]
        ex_str = ', '.join(examples)
        print(f"  {h}->{t:>3}   {len(data['types']):>5}  {data['tokens']:>6}  {dom_cat[0]:>12} {pct:>5.1f}%  {ex_str}")

    return frame_data, decompositions


# --- Test 2: Modifier Injection Effects -----------------------

def test2_modifier_injection(middles, categories, frame_data, decompositions):
    """For top 5 frames, show all compounds and check category consistency."""
    print("\n" + "=" * 80)
    print("TEST 2: Modifier Injection Effects")
    print("=" * 80)

    sorted_frames = sorted(frame_data.items(), key=lambda x: -x[1]['tokens'])

    results = {}

    for (h, t), data in sorted_frames[:5]:
        frame_key = f"{h}->{t}"
        print(f"\n{'-' * 70}")
        print(f"Frame: {frame_key} ({len(data['types'])} types, {data['tokens']} tokens)")
        print(f"{'-' * 70}")

        # All compounds in this frame, sorted by frequency
        frame_mids = sorted(data['types'], key=lambda m: -middles[m])

        cats_in_frame = Counter()
        entries = []

        print(f"  {'MIDDLE':>15} {'Freq':>6} {'Mods':>15} {'Category':>12}")
        for mid in frame_mids:
            head, mods, term = decompositions[mid]
            mod_str = '+'.join(mods) if mods else '(none)'
            cat = categories.get(mid, 'UNKNOWN')
            cats_in_frame[cat] += middles[mid]
            freq = middles[mid]
            print(f"  {mid:>15} {freq:>6} {mod_str:>15} {cat:>12}")
            entries.append({
                'middle': mid, 'freq': freq,
                'mods': mods, 'mod_str': mod_str, 'category': cat
            })

        # Category consistency
        total = sum(cats_in_frame.values())
        dom_cat = cats_in_frame.most_common(1)[0]
        consistency = 100 * dom_cat[1] / total if total > 0 else 0

        print(f"\n  Category distribution:")
        for cat, cnt in cats_in_frame.most_common():
            print(f"    {cat:>15}: {cnt:>5} ({100*cnt/total:.1f}%)")
        print(f"  Frame category consistency: {consistency:.1f}% ({dom_cat[0]})")

        results[frame_key] = {
            'types': len(data['types']),
            'tokens': data['tokens'],
            'consistency': round(consistency, 1),
            'dominant_cat': dom_cat[0],
            'entries': entries
        }

    return results


# --- Test 3: Individual Modifier Effects ----------------------

def test3_modifier_effects(middles, categories, decompositions):
    """Test whether individual modifiers shift categories."""
    print("\n" + "=" * 80)
    print("TEST 3: Individual Modifier Effects")
    print("=" * 80)

    # For each modifier, gather category distribution WITH and WITHOUT
    mod_atoms = ['p', 'c', 'i', 'f', 'd', 's']

    results = {}

    for mod_atom in mod_atoms:
        with_mod = Counter()  # categories when modifier present
        without_mod = Counter()  # categories when modifier absent

        # Also track: same-frame pairs (with/without this modifier)
        frame_pairs = []

        for mid, count in middles.items():
            if len(mid) < 2:
                continue
            head, mods, term = decompositions.get(mid, (None, [], None))
            if head is None:
                continue

            cat = categories.get(mid, 'UNKNOWN')
            mod_chars = set()
            for m in mods:
                mod_chars.add(m[0])

            if mod_atom in mod_chars:
                with_mod[cat] += count
            else:
                without_mod[cat] += count

        # Print
        print(f"\n{'-' * 60}")
        print(f"Modifier: {mod_atom} ({ATOM_GLOSS.get(mod_atom, '?')})")
        print(f"{'-' * 60}")

        total_with = sum(with_mod.values())
        total_without = sum(without_mod.values())

        all_cats = sorted(set(list(with_mod.keys()) + list(without_mod.keys())))

        print(f"  {'Category':>15} {'WITH':>8} {'%':>6} {'WITHOUT':>8} {'%':>6} {'Shift':>7}")

        shifts = {}
        for cat in all_cats:
            w = with_mod.get(cat, 0)
            wo = without_mod.get(cat, 0)
            wp = 100 * w / total_with if total_with > 0 else 0
            wop = 100 * wo / total_without if total_without > 0 else 0
            shift = wp - wop
            shifts[cat] = shift
            marker = '**' if abs(shift) > 5 else ''
            print(f"  {cat:>15} {w:>8} {wp:>5.1f}% {wo:>8} {wop:>5.1f}% {shift:>+6.1f}% {marker}")

        print(f"  {'TOTAL':>15} {total_with:>8}        {total_without:>8}")

        # Chi-squared test
        from scipy import stats
        obs_with = []
        obs_without = []
        for cat in all_cats:
            obs_with.append(with_mod.get(cat, 0))
            obs_without.append(without_mod.get(cat, 0))

        if total_with > 0 and total_without > 0:
            contingency = [obs_with, obs_without]
            chi2, p, dof, expected = stats.chi2_contingency(contingency)
            # Cramer's V
            n = total_with + total_without
            k = len(all_cats)
            v = (chi2 / (n * (min(2, k) - 1))) ** 0.5 if n > 0 else 0
            print(f"  Chi² = {chi2:.1f}, p = {p:.2e}, Cramer's V = {v:.3f}")
        else:
            chi2, p, v = 0, 1, 0

        # Find strongest shift
        max_shift_cat = max(shifts, key=lambda x: abs(shifts[x]))

        results[mod_atom] = {
            'gloss': ATOM_GLOSS.get(mod_atom, '?'),
            'with_count': total_with,
            'without_count': total_without,
            'chi2': round(chi2, 1),
            'p': p,
            'cramers_v': round(v, 3),
            'strongest_shift': max_shift_cat,
            'shift_magnitude': round(shifts[max_shift_cat], 1)
        }

    # Summary
    print(f"\n{'Modifier Effect Summary':^60}")
    print(f"  {'Mod':>4} {'Gloss':>10} {'V':>6} {'Strongest Shift':>20} {'Mag':>7}")
    for mod_atom in mod_atoms:
        r = results[mod_atom]
        sig = '***' if r['p'] < 0.001 else '**' if r['p'] < 0.01 else '*' if r['p'] < 0.05 else ''
        print(f"  {mod_atom:>4} {r['gloss']:>10} {r['cramers_v']:>6.3f} {r['strongest_shift']:>20} {r['shift_magnitude']:>+6.1f}% {sig}")

    return results


# --- Test 4: Full Compound Decomposition Table ----------------

def test4_full_table(middles, categories, decompositions):
    """Produce comprehensive table of all compounds (freq >= 5)."""
    print("\n" + "=" * 80)
    print("TEST 4: Full Compound Decomposition Table")
    print("=" * 80)

    # Filter: compounds with freq >= 5
    entries = []
    for mid, count in middles.items():
        if len(mid) < 2 or count < 5:
            continue

        head, mods, term = decompositions.get(mid, (None, [], None))
        cat = categories.get(mid, 'UNKNOWN')

        head_str = head if head else '-'
        mod_str = '+'.join(mods) if mods else '-'
        term_str = term if term else '-'

        gloss = compose_gloss(head, mods, term)

        head_sort = head[0] if head else 'z'
        term_sort = term[0] if term else 'z'

        entries.append({
            'middle': mid,
            'head': head_str,
            'mod_stack': mod_str,
            'term': term_str,
            'category': cat,
            'freq': count,
            'gloss': gloss,
            'head_sort': head_sort,
            'term_sort': term_sort,
        })

    # Sort by HEAD, then TERM, then frequency
    entries.sort(key=lambda x: (x['head_sort'], x['term_sort'], -x['freq']))

    # Print table
    print(f"\n  {'MIDDLE':>12} {'HEAD':>5} {'MODS':>12} {'TERM':>5} {'CAT':>12} {'FREQ':>5}  GLOSS")
    print(f"  {'-'*12} {'-'*5} {'-'*12} {'-'*5} {'-'*12} {'-'*5}  {'-'*30}")

    current_head = None
    for e in entries:
        if e['head_sort'] != current_head:
            current_head = e['head_sort']
            if current_head != entries[0]['head_sort']:
                print()

        print(f"  {e['middle']:>12} {e['head']:>5} {e['mod_stack']:>12} {e['term']:>5} {e['category']:>12} {e['freq']:>5}  {e['gloss']}")

    print(f"\n  Total compounds (freq >= 5): {len(entries)}")

    # Save to file
    out_path = RESULTS_DIR / 'compound_table.txt'
    with open(out_path, 'w') as f:
        f.write("Phase 505: Full Compound Decomposition Table\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"{'MIDDLE':>12} {'HEAD':>5} {'MODS':>12} {'TERM':>5} {'CATEGORY':>12} {'FREQ':>5}  GLOSS\n")
        f.write(f"{'-'*12} {'-'*5} {'-'*12} {'-'*5} {'-'*12} {'-'*5}  {'-'*35}\n")

        current_head = None
        for e in entries:
            if e['head_sort'] != current_head:
                current_head = e['head_sort']
                if current_head != entries[0]['head_sort']:
                    f.write("\n")
            f.write(f"{e['middle']:>12} {e['head']:>5} {e['mod_stack']:>12} {e['term']:>5} {e['category']:>12} {e['freq']:>5}  {e['gloss']}\n")

        f.write(f"\nTotal compounds (freq >= 5): {len(entries)}\n")

    print(f"\n  Saved to: {out_path}")

    return entries


# --- Test 5: Modifier Order Semantics -------------------------

def test5_modifier_order(middles, categories, decompositions):
    """Analyze modifier sequences for procedural meaning."""
    print("\n" + "=" * 80)
    print("TEST 5: Modifier Order Semantics")
    print("=" * 80)

    # Collect all compounds with 2+ modifiers
    multi_mod = []
    mod_pairs = Counter()
    mod_triples = Counter()

    for mid, count in middles.items():
        if len(mid) < 2:
            continue
        head, mods, term = decompositions.get(mid, (None, [], None))
        if head is None or len(mods) < 2:
            continue

        # Get modifier base chars
        mod_bases = [m[0] for m in mods]
        cat = categories.get(mid, 'UNKNOWN')

        multi_mod.append({
            'middle': mid,
            'head': head,
            'mods': mods,
            'mod_bases': mod_bases,
            'term': term,
            'cat': cat,
            'freq': count,
            'gloss': compose_gloss(head, mods, term),
        })

        # Count pairs
        for i in range(len(mod_bases) - 1):
            pair = (mod_bases[i], mod_bases[i+1])
            mod_pairs[pair] += count

        # Count triples
        for i in range(len(mod_bases) - 2):
            triple = (mod_bases[i], mod_bases[i+1], mod_bases[i+2])
            mod_triples[triple] += count

    print(f"\nCompounds with 2+ modifiers: {len(multi_mod)} types")

    # Sort by frequency
    multi_mod.sort(key=lambda x: -x['freq'])

    # Show top 30
    print(f"\n  {'MIDDLE':>15} {'HEAD':>5} {'MOD SEQ':>15} {'TERM':>5} {'CAT':>12} {'FREQ':>5}  GLOSS")
    print(f"  {'-'*15} {'-'*5} {'-'*15} {'-'*5} {'-'*12} {'-'*5}  {'-'*35}")

    for entry in multi_mod[:30]:
        h_str = entry['head'] if entry['head'] else '-'
        t_str = entry['term'] if entry['term'] else '-'
        mod_seq = '->'.join(entry['mods'])
        print(f"  {entry['middle']:>15} {h_str:>5} {mod_seq:>15} {t_str:>5} {entry['cat']:>12} {entry['freq']:>5}  {entry['gloss']}")

    # Modifier pair analysis
    print(f"\n{'Modifier Pair Frequencies':^60}")
    print(f"  {'Pair':>8} {'Glossed':>25} {'Tokens':>7}")
    for (a, b), cnt in mod_pairs.most_common(20):
        glossed = f"{ATOM_GLOSS.get(a,'?')} -> {ATOM_GLOSS.get(b,'?')}"
        print(f"  {a}->{b:>4}   {glossed:>25} {cnt:>7}")

    # Modifier triple analysis
    if mod_triples:
        print(f"\n{'Modifier Triple Frequencies':^60}")
        print(f"  {'Triple':>12} {'Glossed':>40} {'Tokens':>7}")
        for (a, b, c), cnt in mod_triples.most_common(10):
            glossed = f"{ATOM_GLOSS.get(a,'?')} -> {ATOM_GLOSS.get(b,'?')} -> {ATOM_GLOSS.get(c,'?')}"
            print(f"  {a}->{b}->{c:>4}   {glossed:>40} {cnt:>7}")

    # Group by modifier combination (unordered) to see if order matters
    print(f"\n{'Same Modifiers, Different Orders':^70}")
    combo_groups = defaultdict(list)
    for entry in multi_mod:
        combo = tuple(sorted(entry['mod_bases']))
        combo_groups[combo].append(entry)

    shown = 0
    for combo, entries in sorted(combo_groups.items(), key=lambda x: -sum(e['freq'] for e in x[1])):
        if len(entries) < 2:
            continue
        # Check if different orderings exist
        orderings = set()
        for e in entries:
            orderings.add(tuple(e['mod_bases']))
        if len(orderings) < 2:
            continue

        shown += 1
        if shown > 10:
            break

        combo_str = '+'.join(combo)
        print(f"\n  Modifier set: {{{combo_str}}}")
        for e in sorted(entries, key=lambda x: -x['freq']):
            ord_str = '->'.join(e['mod_bases'])
            print(f"    {e['middle']:>12}  order: {ord_str:>10}  {e['cat']:>12}  {e['freq']:>4}  {e['gloss']}")

    if shown == 0:
        print("  (No modifier sets appear in multiple orderings)")

    return multi_mod


# --- Additional Analysis: Frame Category Coherence ------------

def frame_coherence_analysis(frame_data, middles, categories):
    """Overall analysis of how well HEAD×TERM determines category."""
    print("\n" + "=" * 80)
    print("SYNTHESIS: Frame Category Coherence")
    print("=" * 80)

    total_correct = 0
    total_tokens = 0
    frame_stats = []

    for (h, t), data in frame_data.items():
        if not data['cats']:
            continue
        dom_cat = data['cats'].most_common(1)[0]
        correct = dom_cat[1]
        total = data['tokens']
        total_correct += correct
        total_tokens += total
        pct = 100 * correct / total if total > 0 else 0
        frame_stats.append({
            'frame': f"{h}->{t}",
            'types': len(data['types']),
            'tokens': total,
            'dom_cat': dom_cat[0],
            'pct': pct
        })

    overall_coherence = 100 * total_correct / total_tokens if total_tokens > 0 else 0

    print(f"\n  Overall frame -> category coherence: {overall_coherence:.1f}%")
    print(f"  (If you know HEAD and TERM, you can predict the category this often)")

    # Coherence distribution
    high = [f for f in frame_stats if f['pct'] >= 80]
    medium = [f for f in frame_stats if 50 <= f['pct'] < 80]
    low = [f for f in frame_stats if f['pct'] < 50]

    print(f"\n  Frames with >=80% coherence: {len(high)} ({sum(f['tokens'] for f in high)} tokens)")
    print(f"  Frames with 50-79% coherence: {len(medium)} ({sum(f['tokens'] for f in medium)} tokens)")
    print(f"  Frames with <50% coherence: {len(low)} ({sum(f['tokens'] for f in low)} tokens)")

    # HEAD-level coherence
    print(f"\n{'HEAD-Level Category Dominance':^60}")
    head_cats = defaultdict(Counter)
    for (h, t), data in frame_data.items():
        for cat, cnt in data['cats'].items():
            head_cats[h][cat] += cnt

    for h in sorted(head_cats):
        total = sum(head_cats[h].values())
        dom = head_cats[h].most_common(1)[0]
        pct = 100 * dom[1] / total
        top3 = head_cats[h].most_common(3)
        top3_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top3)
        print(f"  HEAD={h}: {pct:.0f}% {dom[0]:>12}  (total {total:>5})  [{top3_str}]")

    # TERM-level coherence
    print(f"\n{'TERM-Level Category Dominance':^60}")
    term_cats = defaultdict(Counter)
    for (h, t), data in frame_data.items():
        for cat, cnt in data['cats'].items():
            term_cats[t][cat] += cnt

    for t in sorted(term_cats):
        total = sum(term_cats[t].values())
        dom = term_cats[t].most_common(1)[0]
        pct = 100 * dom[1] / total
        top3 = term_cats[t].most_common(3)
        top3_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top3)
        print(f"  TERM={t}: {pct:.0f}% {dom[0]:>12}  (total {total:>5})  [{top3_str}]")

    return overall_coherence


# --- Main -----------------------------------------------------

def main():
    print("Phase 505: Instruction Encoding Map")
    print("=" * 80)
    print()

    # Load data
    middles, categories = load_data()
    print(f"Loaded {len(middles)} unique MIDDLEs, {sum(middles.values())} tokens")

    # Pre-compute all decompositions
    decompositions = {}
    for mid in middles:
        if len(mid) >= 2:
            decompositions[mid] = decompose(mid)

    # Run tests
    frame_data, decompositions_full = test1_frame_matrix(middles, categories)
    # Merge decompositions
    decompositions.update(decompositions_full)

    t2_results = test2_modifier_injection(middles, categories, frame_data, decompositions)
    t3_results = test3_modifier_effects(middles, categories, decompositions)
    t4_entries = test4_full_table(middles, categories, decompositions)
    t5_multi = test5_modifier_order(middles, categories, decompositions)

    coherence = frame_coherence_analysis(frame_data, middles, categories)

    # Save JSON results
    json_results = {
        'test1_summary': {
            'total_frames': len(frame_data),
            'top_frames': [
                {
                    'frame': f"{h}->{t}",
                    'types': len(data['types']),
                    'tokens': data['tokens'],
                    'dominant_cat': data['cats'].most_common(1)[0][0] if data['cats'] else None,
                }
                for (h, t), data in sorted(frame_data.items(), key=lambda x: -x[1]['tokens'])[:15]
            ]
        },
        'test2_top_frame_consistency': t2_results,
        'test3_modifier_effects': t3_results,
        'test4_compound_count': len(t4_entries),
        'test5_multi_mod_count': len(t5_multi),
        'synthesis': {
            'overall_frame_category_coherence': round(coherence, 1),
        }
    }

    json_path = RESULTS_DIR / 'instruction_map.json'
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"\nJSON results saved to: {json_path}")


if __name__ == '__main__':
    main()

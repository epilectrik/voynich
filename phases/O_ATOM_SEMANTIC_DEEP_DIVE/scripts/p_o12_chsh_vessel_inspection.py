"""
P-O12: CHSH+o compound readings confirm vessel inspection

CHSH prefixes (ch/sh) select the monitoring/testing domain. When combined
with o-containing MIDDLEs, the result should be "monitor/check the vessel."

Tests:
1. Category profile of CHSH+o tokens vs CHSH+non-o tokens
2. Suffix mode profile: CHSH+o should lean Mode B (steady-state)
3. BARE suffix enrichment in CHSH+o
4. Top specific CHSH+o compounds with categories

Pass criterion: CHSH+o MONITORING+CONTAINMENT >= 60%; Mode B >= 65%;
BARE suffix >= 50%. At least 2/3 sub-tests pass.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, CategoryClassifier


def normal_cdf(x):
    """Approximate CDF of standard normal distribution."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.8212560 + t * 1.3302744))))
    return 1.0 - p if x > 0 else p


def main():
    tx = Transcript()
    morph = Morphology()
    decoder = BFolioDecoder()
    cc = CategoryClassifier()

    # ---------------------------------------------------------------------------
    # Build suffix mode lookup: (folio, line) -> mode
    # ---------------------------------------------------------------------------
    folio_line_mode = {}  # (folio, line) -> 'A' or 'B'

    # Collect all folios first
    all_folios = set()
    for token in tx.currier_b():
        if token.word and '*' not in token.word:
            all_folios.add(token.folio)

    for folio in all_folios:
        try:
            line_analyses = decoder.analyze_folio_lines(folio)
            if line_analyses:
                for la in line_analyses:
                    if hasattr(la, 'line_id') and hasattr(la, 'suffix_mode'):
                        folio_line_mode[(folio, la.line_id)] = la.suffix_mode
        except Exception:
            pass

    # ---------------------------------------------------------------------------
    # Classify all CHSH-prefixed tokens
    # ---------------------------------------------------------------------------
    chsh_o_tokens = []     # CHSH-prefixed with o in MIDDLE
    chsh_nono_tokens = []  # CHSH-prefixed without o in MIDDLE
    all_b_tokens = []      # All B tokens for baseline

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle if m.middle else ''
        pfx = m.prefix if m.prefix else ''
        suffix = m.suffix if m.suffix else ''

        cat = cc.classify(mid)
        mode = folio_line_mode.get((token.folio, token.line))
        is_bare = (suffix == '' or suffix is None)

        entry = {
            'word': w,
            'middle': mid,
            'prefix': pfx,
            'suffix': suffix,
            'category': cat,
            'mode': mode,
            'is_bare': is_bare,
            'folio': token.folio,
            'line': token.line,
        }

        all_b_tokens.append(entry)

        # Check if CHSH-prefixed
        is_chsh = pfx.startswith('ch') or pfx.startswith('sh')
        if is_chsh:
            has_o = 'o' in mid
            if has_o:
                chsh_o_tokens.append(entry)
            else:
                chsh_nono_tokens.append(entry)

    print("=" * 70)
    print("P-O12: CHSH+o compound readings (vessel inspection)")
    print("=" * 70)
    print(f"\nTotal B tokens: {len(all_b_tokens)}")
    print(f"CHSH+o tokens: {len(chsh_o_tokens)}")
    print(f"CHSH+non-o tokens: {len(chsh_nono_tokens)}")
    print(f"CHSH total: {len(chsh_o_tokens) + len(chsh_nono_tokens)}")

    if len(chsh_o_tokens) < 10:
        print("\nINSUFFICIENT CHSH+o tokens for analysis")
        print("\nSUMMARY: P-O12 CANNOT BE EVALUATED")
        return

    # ---------------------------------------------------------------------------
    # Test 1: Category profiles
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 1: Category profiles")
    print("=" * 70)

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                   'TRANSITION', 'MARKING', 'MONITORING']

    def category_profile(tokens):
        cats = [t['category'] for t in tokens if t['category']]
        total = len(cats)
        if total == 0:
            return {}, 0
        counts = Counter(cats)
        return {c: counts.get(c, 0) / total for c in CATEGORIES}, total

    prof_o, n_o_cat = category_profile(chsh_o_tokens)
    prof_nono, n_nono_cat = category_profile(chsh_nono_tokens)
    prof_all_chsh, n_all_chsh = category_profile(chsh_o_tokens + chsh_nono_tokens)

    print(f"\n{'Category':<14} {'CHSH+o':>8} {'CHSH+non-o':>12} {'CHSH_all':>10} {'Ratio':>8}")
    print("-" * 55)
    for cat in CATEGORIES:
        o_frac = prof_o.get(cat, 0)
        nono_frac = prof_nono.get(cat, 0)
        all_frac = prof_all_chsh.get(cat, 0)
        ratio = o_frac / nono_frac if nono_frac > 0 else float('inf')
        print(f"  {cat:<12} {o_frac:>7.1%}  {nono_frac:>11.1%}  {all_frac:>9.1%}  {ratio:>7.2f}x")

    monitor_contain_o = prof_o.get('MONITORING', 0) + prof_o.get('CONTAINMENT', 0)
    print(f"\n  CHSH+o MONITORING+CONTAINMENT: {monitor_contain_o:.1%}")
    print(f"  (Criterion: >= 60%)")

    # ---------------------------------------------------------------------------
    # Test 2: Suffix mode profile
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 2: Suffix mode profile")
    print("=" * 70)

    def mode_profile(tokens):
        modes = [t['mode'] for t in tokens if t['mode'] in ('A', 'B')]
        total = len(modes)
        if total == 0:
            return 0.0, 0.0, 0
        mode_a = sum(1 for m in modes if m == 'A')
        mode_b = sum(1 for m in modes if m == 'B')
        return mode_a / total, mode_b / total, total

    a_o, b_o, n_mode_o = mode_profile(chsh_o_tokens)
    a_nono, b_nono, n_mode_nono = mode_profile(chsh_nono_tokens)
    a_all, b_all, n_mode_all = mode_profile(chsh_o_tokens + chsh_nono_tokens)

    print(f"\n{'Group':<16} {'Mode A':>8} {'Mode B':>8} {'N':>6}")
    print("-" * 42)
    print(f"  CHSH+o        {a_o:>7.1%}  {b_o:>7.1%}  {n_mode_o:>5}")
    print(f"  CHSH+non-o    {a_nono:>7.1%}  {b_nono:>7.1%}  {n_mode_nono:>5}")
    print(f"  CHSH all      {a_all:>7.1%}  {b_all:>7.1%}  {n_mode_all:>5}")

    print(f"\n  CHSH+o Mode B fraction: {b_o:.1%}")
    print(f"  (Criterion: >= 65%)")

    # ---------------------------------------------------------------------------
    # Test 3: BARE suffix enrichment
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 3: BARE suffix analysis")
    print("=" * 70)

    def bare_rate(tokens):
        total = len(tokens)
        if total == 0:
            return 0.0, 0
        bare = sum(1 for t in tokens if t['is_bare'])
        return bare / total, total

    bare_o, n_bare_o = bare_rate(chsh_o_tokens)
    bare_nono, n_bare_nono = bare_rate(chsh_nono_tokens)
    bare_all, n_bare_all = bare_rate(all_b_tokens)

    print(f"\n{'Group':<16} {'BARE%':>8} {'N':>6}")
    print("-" * 35)
    print(f"  CHSH+o        {bare_o:>7.1%}  {n_bare_o:>5}")
    print(f"  CHSH+non-o    {bare_nono:>7.1%}  {n_bare_nono:>5}")
    print(f"  All B tokens  {bare_all:>7.1%}  {n_bare_all:>5}")

    if bare_nono > 0:
        enrichment = bare_o / bare_nono
        print(f"\n  CHSH+o BARE enrichment vs CHSH+non-o: {enrichment:.2f}x")

    print(f"\n  CHSH+o BARE fraction: {bare_o:.1%}")
    print(f"  (Criterion: >= 50%)")

    # Suffix type breakdown for CHSH+o
    print(f"\n  CHSH+o suffix type breakdown:")
    suffix_counts = Counter()
    for t in chsh_o_tokens:
        s = t['suffix'] if t['suffix'] else 'BARE'
        suffix_counts[s] += 1
    for s, c in suffix_counts.most_common(10):
        print(f"    {s:<10} {c:>5} ({c/len(chsh_o_tokens):.1%})")

    # ---------------------------------------------------------------------------
    # Test 4: Top specific CHSH+o compounds
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 4: Top specific CHSH+o compound tokens")
    print("=" * 70)

    # Group by prefix + middle combination
    compound_data = defaultdict(lambda: {'count': 0, 'categories': [], 'modes': [], 'suffixes': []})

    for t in chsh_o_tokens:
        key = f"{t['prefix']}+{t['middle']}"
        compound_data[key]['count'] += 1
        if t['category']:
            compound_data[key]['categories'].append(t['category'])
        if t['mode'] in ('A', 'B'):
            compound_data[key]['modes'].append(t['mode'])
        compound_data[key]['suffixes'].append(t['suffix'] if t['suffix'] else 'BARE')

    # Sort by frequency
    sorted_compounds = sorted(compound_data.items(), key=lambda x: x[1]['count'], reverse=True)

    print(f"\n{'Compound':<18} {'N':>4} {'Top Category':>14} {'Mode B%':>8} {'BARE%':>7}")
    print("-" * 55)
    for comp, data in sorted_compounds[:20]:
        n = data['count']
        cats = Counter(data['categories'])
        top_cat = cats.most_common(1)[0][0] if cats else '-'
        modes = data['modes']
        mode_b_pct = sum(1 for m in modes if m == 'B') / len(modes) if modes else 0
        bare_pct = sum(1 for s in data['suffixes'] if s == 'BARE') / len(data['suffixes'])
        print(f"  {comp:<16} {n:>4}  {top_cat:>13}  {mode_b_pct:>7.1%}  {bare_pct:>6.1%}")

    # ---------------------------------------------------------------------------
    # Additional: CHSH+o per ch vs sh prefix
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Additional: ch+o vs sh+o comparison")
    print("=" * 70)

    ch_o = [t for t in chsh_o_tokens if t['prefix'].startswith('ch')]
    sh_o = [t for t in chsh_o_tokens if t['prefix'].startswith('sh')]

    print(f"\n  ch+o tokens: {len(ch_o)}")
    print(f"  sh+o tokens: {len(sh_o)}")

    if len(ch_o) >= 5 and len(sh_o) >= 5:
        prof_ch_o, _ = category_profile(ch_o)
        prof_sh_o, _ = category_profile(sh_o)

        print(f"\n  {'Category':<14} {'ch+o':>8} {'sh+o':>8}")
        print(f"  {'-'*32}")
        for cat in CATEGORIES:
            if prof_ch_o.get(cat, 0) > 0.01 or prof_sh_o.get(cat, 0) > 0.01:
                print(f"  {cat:<12}  {prof_ch_o.get(cat, 0):>7.1%}  {prof_sh_o.get(cat, 0):>7.1%}")

        # Mode comparison
        _, b_ch, n_ch = mode_profile(ch_o)
        _, b_sh, n_sh = mode_profile(sh_o)
        print(f"\n  Mode B: ch+o={b_ch:.1%} (N={n_ch}), sh+o={b_sh:.1%} (N={n_sh})")
        print(f"  C929: sh=passive monitor, ch=active test")
        print(f"  Expectation: sh+o (passive vessel check) may lean more Mode B than ch+o (active vessel test)")

    # ---------------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("SUMMARY: P-O12 CHSH+o vessel inspection")
    print("=" * 70)

    t1_pass = monitor_contain_o >= 0.60
    t2_pass = b_o >= 0.65
    t3_pass = bare_o >= 0.50

    print(f"\n  Test 1 (MONITORING+CONTAINMENT >= 60%): {monitor_contain_o:.1%}")
    print(f"    Pass?                                  {'PASS' if t1_pass else 'FAIL'}")
    print(f"\n  Test 2 (Mode B >= 65%):                  {b_o:.1%}")
    print(f"    Pass?                                  {'PASS' if t2_pass else 'FAIL'}")
    print(f"\n  Test 3 (BARE suffix >= 50%):              {bare_o:.1%}")
    print(f"    Pass?                                  {'PASS' if t3_pass else 'FAIL'}")

    tests_passed = sum([t1_pass, t2_pass, t3_pass])
    print(f"\n  OVERALL: {tests_passed}/3 sub-tests passed")
    print(f"  VERDICT: {'PASS' if tests_passed >= 2 else 'FAIL'} (need 2/3)")

    # Additional observations
    print(f"\n  Key observations:")
    print(f"    CHSH+o tokens: {len(chsh_o_tokens)} ({len(chsh_o_tokens)/(len(chsh_o_tokens)+len(chsh_nono_tokens)):.1%} of all CHSH)")
    print(f"    Top CHSH+o MIDDLEs: {', '.join(c[0] for c in sorted_compounds[:5])}")


if __name__ == '__main__':
    main()

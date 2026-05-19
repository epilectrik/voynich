"""
PHASE_705 follow-up: y-class line-position verification.

Crazy-expert flag: y-class (ary/aly/dary/daly/ory/oly) showed ZERO observed
adjacency with r-class or l-class in PHASE_705's bigram analysis (N=320
LATE-LATE bigrams). Could be:

(a) Genuine structural fact: y-class doesn't participate in within-line
    closure adjacency
(b) C539 redux: y-class is line-final-locked, so by definition has no
    in-line right-neighbor

Test: what fraction of y-class tokens occur at line-final position in
Currier B P-placement?
  - If >85%: zero-adjacency is C539 expression, not a new finding
  - If <50%: y-class participates within-line but doesn't cluster with
    r/l class adjacency — genuinely interesting non-participation
  - Between: gray zone
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_705_TERMINAL_ATOM_GEN' / 'results' / 'y_class_position_check.json'

R_CLASS = ['ar', 'dar', 'or']
L_CLASS = ['al', 'dal', 'ol']
Y_CLASS = ['ary', 'aly', 'dary', 'daly', 'ory', 'oly']


def main():
    print("=" * 80)
    print("Y-CLASS LINE-FINAL POSITION VERIFICATION")
    print("=" * 80)

    tx = Transcript()
    morph = Morphology()

    # For each line, find max token position (final position)
    # Then count y-class tokens at final vs non-final positions
    line_tokens = defaultdict(list)  # (folio, line) -> [(idx, middle)]

    for t in tx.currier_b(h_only=True, exclude_labels=True, exclude_uncertain=True):
        if not (t.placement and t.placement.startswith('P')):
            continue
        if not t.word.strip():
            continue
        word = t.word.lower()
        try:
            m = morph.extract(word)
            middle = m.middle
        except Exception:
            middle = None
        key = (t.folio, t.line)
        if key[1] is None or key[1] == '':
            continue
        line_tokens[key].append((len(line_tokens[key]), middle))

    # Now build position stats per class
    stats = {}
    for class_name, class_members in [('r', R_CLASS), ('l', L_CLASS), ('y', Y_CLASS)]:
        n_total = 0
        n_final = 0
        n_initial = 0
        n_penult = 0
        single_line_count = 0  # lines where this token is the only one
        per_middle = defaultdict(lambda: {'total': 0, 'final': 0, 'penult': 0, 'initial': 0})

        for (folio, line), tokens in line_tokens.items():
            n_in_line = len(tokens)
            for (idx, middle) in tokens:
                if middle not in class_members:
                    continue
                n_total += 1
                per_middle[middle]['total'] += 1
                if n_in_line == 1:
                    single_line_count += 1
                    per_middle[middle]['final'] += 1
                    per_middle[middle]['initial'] += 1
                else:
                    if idx == n_in_line - 1:
                        n_final += 1
                        per_middle[middle]['final'] += 1
                    if idx == n_in_line - 2:
                        n_penult += 1
                        per_middle[middle]['penult'] += 1
                    if idx == 0:
                        n_initial += 1
                        per_middle[middle]['initial'] += 1

        stats[class_name] = {
            'class_members': class_members,
            'n_total_tokens': n_total,
            'n_line_final': n_final,
            'n_penultimate': n_penult,
            'n_line_initial': n_initial,
            'n_in_single_token_lines': single_line_count,
            'pct_final': n_final / n_total if n_total else 0.0,
            'pct_penult': n_penult / n_total if n_total else 0.0,
            'pct_initial': n_initial / n_total if n_total else 0.0,
            'per_middle': {m: dict(v) for m, v in per_middle.items()},
        }

    print(f"\n{'class':<8}{'N':>6}{'%final':>10}{'%penult':>10}{'%initial':>10}{'single_line':>14}")
    print("-" * 60)
    for c in ['r', 'l', 'y']:
        s = stats[c]
        if s['n_total_tokens'] == 0:
            continue
        print(f"{c:<8}{s['n_total_tokens']:>6}"
              f"{s['pct_final']*100:>9.1f}%"
              f"{s['pct_penult']*100:>9.1f}%"
              f"{s['pct_initial']*100:>9.1f}%"
              f"{s['n_in_single_token_lines']:>14}")

    print(f"\nPer-MIDDLE breakdown (y-class):")
    print(f"{'middle':<10}{'total':>8}{'final':>8}{'%final':>10}")
    print("-" * 40)
    for m in Y_CLASS:
        v = stats['y']['per_middle'].get(m, {'total': 0, 'final': 0})
        pct = v['final'] / v['total'] * 100 if v['total'] else 0
        print(f"{m:<10}{v['total']:>8}{v['final']:>8}{pct:>9.1f}%")

    print(f"\nPer-MIDDLE breakdown (r-class, for comparison):")
    print(f"{'middle':<10}{'total':>8}{'final':>8}{'%final':>10}")
    print("-" * 40)
    for m in R_CLASS:
        v = stats['r']['per_middle'].get(m, {'total': 0, 'final': 0})
        pct = v['final'] / v['total'] * 100 if v['total'] else 0
        print(f"{m:<10}{v['total']:>8}{v['final']:>8}{pct:>9.1f}%")

    print(f"\nPer-MIDDLE breakdown (l-class):")
    print(f"{'middle':<10}{'total':>8}{'final':>8}{'%final':>10}")
    print("-" * 40)
    for m in L_CLASS:
        v = stats['l']['per_middle'].get(m, {'total': 0, 'final': 0})
        pct = v['final'] / v['total'] * 100 if v['total'] else 0
        print(f"{m:<10}{v['total']:>8}{v['final']:>8}{pct:>9.1f}%")

    # Verdict
    print(f"\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    y_pct = stats['y']['pct_final']
    r_pct = stats['r']['pct_final']
    l_pct = stats['l']['pct_final']
    print(f"\ny-class line-final %: {y_pct*100:.1f}%")
    print(f"r-class line-final %: {r_pct*100:.1f}%")
    print(f"l-class line-final %: {l_pct*100:.1f}%")

    if y_pct > 0.85:
        verdict = (f"C539 REDUX: y-class is line-final-locked ({y_pct*100:.1f}% at line-final). "
                   "Zero adjacency with r/l class is C539-expression, not a new finding. "
                   "Do not register y-class non-participation as separate finding.")
    elif y_pct > 0.60 and r_pct < 0.50 and l_pct < 0.50:
        verdict = (f"Y-CLASS PREFERENTIAL LINE-FINAL: y-class is {y_pct*100:.1f}% line-final vs "
                   f"r-class {r_pct*100:.1f}% and l-class {l_pct*100:.1f}% — preferential but not "
                   "exclusive lock. y-class non-adjacency partially driven by line-final routing "
                   "but with residual structural distinctness. Borderline registration candidate.")
    else:
        verdict = (f"Y-CLASS GENUINELY DISTINCT: y-class only {y_pct*100:.1f}% line-final yet shows "
                   f"zero adjacency to r/l class. Real structural non-participation finding, "
                   "not C539 redux. Worth investigating.")

    print(f"\n  {verdict}")

    out = {
        "method": "PHASE_705 follow-up: y-class line-position verification",
        "question": "Is y-class zero-adjacency C539 redux (line-final lock) or genuine non-participation?",
        "stats_by_class": stats,
        "verdict": verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()

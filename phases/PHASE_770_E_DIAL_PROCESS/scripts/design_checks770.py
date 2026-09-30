#!/usr/bin/env python3
"""PHASE_770 design-stage checks, run before any calibration or lock.

Only transcription agreement, occurrence counts and codicology are computed here. No statistic of any dial by folio,
page position, paragraph order or page turn is computed on B.

1. Agreement: for each candidate dial, on tokens aligned between two transcriptions of the same line (PHASE_758 rule)
   whose dial frame is identical, the confusion matrix of the unit outcome and Cohen's kappa. H vs F (interlinear
   file, same line ids) and H vs ZL 3b (lines matched by content: ZL line ids can differ from H's).
2. Counts (H track, P placement): occurrences, frames, informative occurrences (cells spanning >= 2 folios; PHASE_769
   cell definition) and the pooled rate of the marked outcome, with and without f76r (coded R in H, P in ZL).
3. Codicology of the B pages from the ZL page variables ($Q quire, $B bifolium, $F leaf position, $P page position):
   reading-order transitions (leaf turn, opening, panel, gap), chains, and sheet-face pairs of conjoint leaves.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'phases/PHASE_769_E_DIAL_SETTING/scripts'))
sys.path.insert(0, str(ROOT / 'phases/PHASE_770_E_DIAL_PROCESS/scripts'))
import ed769 as E  # noqa: E402
import ed769b as B  # noqa: E402

OUT = ROOT / 'phases/PHASE_770_E_DIAL_PROCESS/results'
GLYPH_RE = E.GLYPH_RE
GALLOWS = {'k': 'k', 't': 't', 'p': 'p', 'f': 'f', 'ckh': 'k', 'cth': 't', 'cph': 'p', 'cfh': 'f'}
DIALS = ('E', 'CS', 'KT', 'KTH', 'OKOT', 'MIN', 'BENCH')
MISSING_LEAVES = {12, 59, 60, 61, 62, 63, 64, 74, 91, 92, 97, 98, 109, 110}


def units(w, dial):
    """Outcomes (0/1) of the dial's units in the token and the dial frame (shared engine: ed770.units)."""
    import ed770
    out, fr = ed770.units(w, dial)
    return [y for y, _, _ in out[dial]], fr


def load_b_h_plus(extra=('f76r',)):
    """load_b_h with the R-placement lines of the listed folios added (f76r: paragraph text coded R in H, P in ZL)."""
    from scripts.voynich import Transcript
    pv = E.zl_page_vars()
    rows = []
    for t in Transcript().currier_b(exclude_uncertain=False):
        pl = t.placement or ''
        if not (pl.startswith('P') or (t.folio in extra and pl.startswith('R'))):
            continue
        w = t.word.strip()
        if not w:
            continue
        rows.append((w, t.folio, t.line, t.par_initial, t.section, '*' in w))
    return E._assemble(rows, pv)


# ------------------------------------------------------------------------------------------------ 1. agreement
def align(h, o):
    pairs = []
    sm = difflib.SequenceMatcher(None, h, o, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
            pairs.extend(zip(h[i1:i2], o[j1:j2]))
    return pairs


def kappa(conf):
    n = conf.sum()
    if n == 0:
        return None
    po = np.trace(conf) / n
    pe = (conf.sum(0) * conf.sum(1)).sum() / n ** 2
    return float((po - pe) / (1 - pe)) if pe < 1 else None


def agreement(H, O):
    conf = {d: np.zeros((2, 2), int) for d in DIALS}
    n_h = Counter()
    for key, h in H.items():
        o = O.get(key)
        if o is None:
            continue
        for a in h:
            if '*' not in a:
                for d in DIALS:
                    n_h[d] += len(units(a, d)[0])
        for a, b in align(h, o):
            if '*' in a or '*' in b:
                continue
            for d in DIALS:
                ya, fa = units(a, d)
                yb, fb = units(b, d)
                if fa != fb or len(ya) != len(yb):
                    continue
                for x, z in zip(ya, yb):
                    conf[d][x, z] += 1
    return {d: {'kappa': kappa(conf[d]), 'confusion_[H0|H1][O0|O1]': conf[d].tolist(), 'n_compared': int(conf[d].sum()),
                'n_H_on_covered_lines': int(n_h[d]),
                'share_compared': float(conf[d].sum() / n_h[d]) if n_h[d] else None} for d in DIALS}


# ------------------------------------------------------------------------------------------------ 2. counts
def counts(recs, dial):
    import ed770
    O = ed770.occurrences(recs, dial)
    y, inf = O['y'], O['informative']
    cy = defaultdict(set)
    for c, v in zip(O['cell'], y):
        cy[c].add(v)
    var = np.array([inf[i] and len(cy[c]) == 2 for i, c in enumerate(O['cell'])])
    return {'occurrences': int(len(y)), 'frames': int(O['n_tokens']), 'informative': int(inf.sum()),
            'informative_with_variation': int(var.sum()),
            'rate_marked_informative': float(y[inf].mean()) if inf.any() else None,
            'folios': len(set(O['folio'].tolist()))}


# ------------------------------------------------------------------------------------------------ 3. codicology
def codicology(pages):
    pv = E.zl_page_vars()
    info = []
    for p in pages:
        v = pv.get(p, {})
        m = re.match(r'f(\d+)([rv])(\d*)$', p)
        info.append({'page': p, 'leaf': int(m.group(1)), 'side': m.group(2), 'panel': m.group(3) or None,
                     'Q': v.get('Q'), 'B': v.get('B'), 'F': v.get('F'), 'P': v.get('P'), 'hand': v.get('H'),
                     'illus': v.get('I')})
    trans = []
    for a, b in zip(info, info[1:]):
        foldout = bool(a['panel'] or b['panel'])
        if a['leaf'] == b['leaf'] and a['side'] == b['side']:
            kind = 'panel'
        elif a['leaf'] == b['leaf'] and a['side'] == 'r' and b['side'] == 'v':
            kind = 'leaf_turn'
        elif a['side'] == 'v' and b['side'] == 'r' and b['leaf'] == a['leaf'] + 1:
            kind = 'opening'
        else:
            kind = 'gap'
        trans.append({'from': a['page'], 'to': b['page'], 'kind': kind, 'foldout': foldout,
                      'cross_quire': a['Q'] != b['Q'], 'same_hand': a['hand'] == b['hand']})
    usable = [t['kind'] in ('leaf_turn', 'opening') and not t['foldout'] for t in trans]
    chains, cur = [], [info[0]['page']]
    for t, u in zip(trans, usable):
        if u:
            cur.append(t['to'])
        else:
            chains.append(cur)
            cur = [t['to']]
    chains.append(cur)
    chains = [c for c in chains if len(c) >= 2]
    # conjoint leaves: same quire and bifolium number, two distinct leaf numbers
    bif = defaultdict(set)
    for p, v in pv.items():
        m = re.match(r'f(\d+)[rv]', p)
        if m and v.get('Q') and v.get('B'):
            bif[(v['Q'], v['B'])].add(int(m.group(1)))
    present = set(pages)
    faces = []
    for (q, b), leaves in sorted(bif.items()):
        if len(leaves) != 2:
            continue
        lo, hi = sorted(leaves)
        for face, (x, y) in (('inner', (f'f{lo}v', f'f{hi}r')), ('outer', (f'f{lo}r', f'f{hi}v'))):
            if x in present and y in present:
                faces.append({'quire': q, 'bifolium': b, 'face': face, 'pages': [x, y],
                              'reading_adjacent': face == 'inner' and hi == lo + 1})
    return {'pages': info, 'transitions': trans,
            'transition_counts': dict(Counter((t['kind'], t['foldout'], t['cross_quire']) for t in trans).items()),
            'usable_transitions': int(sum(usable)),
            'usable_by_kind': dict(Counter(t['kind'] for t, u in zip(trans, usable) if u)),
            'usable_cross_quire': int(sum(1 for t, u in zip(trans, usable) if u and t['cross_quire'])),
            'usable_hand_change': int(sum(1 for t, u in zip(trans, usable) if u and not t['same_hand'])),
            'chains': chains, 'n_chains': len(chains), 'sheet_faces': faces}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {'note': 'design-stage checks; no dial statistic by folio, position or page turn computed on B'}
    H, F = B.track_lines('H'), B.track_lines('F')
    zl = defaultdict(list)
    for r in E.load_b_zl():
        zl[r[2]].append(r[0])
    # ZL numbers its loci in one sequence per page (text, labels, sentinels), so equal line ids can name different
    # lines: map H lines to ZL lines by content (ed770.zl_content_map), then align tokens within the mapped lines
    import ed770
    cmap = ed770.zl_content_map(H, zl)
    zl_mapped = {hk: zl[zk] for hk, zk in cmap.items()}
    res['zl_line_mapping'] = {'H_lines': len(H), 'content_mapped': len(cmap),
                              'identical_id': sum(1 for k, v in cmap.items() if k == v),
                              'identical_id_but_other_line': sum(1 for k in H if k in zl and k in cmap and cmap[k] != k)}
    print('ZL line mapping', res['zl_line_mapping'], flush=True)
    res['agreement_H_F'] = agreement(H, F)
    res['agreement_H_ZL'] = agreement(H, zl_mapped)
    for name, ag in (('H-F', res['agreement_H_F']), ('H-ZL', res['agreement_H_ZL'])):
        for d, v in ag.items():
            print(f"{name} {d:5s} kappa {v['kappa']:.3f}  n {v['n_compared']:5d}  share {v['share_compared']:.2f}  "
                  f"{v['confusion_[H0|H1][O0|O1]']}", flush=True)
    import ed770
    recs = E.load_b_h()
    recs_plus = ed770.fix_hands(load_b_h_plus(), {'f115r': '3'})       # the PHASE_770 analysis set
    res['counts_phase769_set'] = {d: counts(recs, d) for d in DIALS}
    res['counts_analysis_set'] = {d: counts(recs_plus, d) for d in DIALS}
    for d in DIALS:
        print('counts', d, 'analysis set', res['counts_analysis_set'][d], '| PHASE_769 set informative',
              res['counts_phase769_set'][d]['informative'], flush=True)
    f76 = [r for r in recs_plus if r[1] == 'f76r']
    res['f76r'] = {'tokens': len(f76), 'lines': len({r[2] for r in f76}), 'paragraphs': len({r[5] for r in f76})}
    print('f76r', res['f76r'], flush=True)
    pages = list(dict.fromkeys(r[1] for r in recs_plus))
    res['codicology'] = codicology(pages)
    c = res['codicology']
    print('usable transitions', c['usable_transitions'], c['usable_by_kind'], 'cross-quire', c['usable_cross_quire'],
          'hand change', c['usable_hand_change'], 'chains', c['n_chains'], [len(x) for x in c['chains']], flush=True)
    print('transition counts', c['transition_counts'], flush=True)
    print('sheet faces (both pages B):', len(c['sheet_faces']),
          Counter((f['quire'], f['face'], f['reading_adjacent']) for f in c['sheet_faces']), flush=True)
    res['codicology']['transition_counts'] = {str(k): v for k, v in c['transition_counts'].items()}
    json.dump(res, open(OUT / 'design_checks.json', 'w'), indent=1)
    print('written', OUT / 'design_checks.json')


if __name__ == '__main__':
    main()

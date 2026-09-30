#!/usr/bin/env python3
"""PHASE_771 locked run (see ../PRE_REGISTRATION.md; v2 after the lean-expert lock audit).

  python run771.py              verifies the lock tag and the input checksums, reads the test material, and writes
                                results/phase771_results.json and results/run_log.txt
  python run771.py --dry        runs every code path on a DECOY copy of the data: label o-words replaced by random
                                paragraph o-words; break-adjacent words replaced by random paragraph words of the same
                                language and section; writes results/dryrun/
  python run771.py --checksums  writes results/calib/input_checksums.json (done once, before the lock commit)
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

LOCK = 'phase771-lock'
PHASE = 'phases/PHASE_771_LABEL_O_AND_DRAWING_BREAKS'
NBOOT, NFIT_R, NPOW, BPOW, SEED = 2000, 2000, 200, 500, 7712
DRY = '--dry' in sys.argv
OUT = Z.ROOT / PHASE / ('results/dryrun' if DRY else 'results')
INPUTS = ('data/transcriptions/reference/ZL_official.txt', 'data/transcriptions/interlinear_full_words.txt',
          'scripts/voynich.py')
CHECKSUMS = Z.ROOT / PHASE / 'results/calib/input_checksums.json'
PURE = {'o = qo without q', 'ordinary o-words', 'o added to a word'}
LOGF = None


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(msg, flush=True)
    if LOGF is not None:
        LOGF.write(msg + '\n')
        LOGF.flush()


def sha256(path):
    return hashlib.sha256((Z.ROOT / path).read_bytes()).hexdigest()


def verify_lock():
    root = Z.ROOT
    r = subprocess.run(['git', 'rev-parse', '--verify', LOCK], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, f'lock tag {LOCK} not found'
    for sub in ('scripts', 'PRE_REGISTRATION.md', 'results/calib'):
        r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/{sub}'], cwd=root)
        assert r.returncode == 0, f'{sub} changed since the lock tag'
    r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--', f'{PHASE}/scripts',
                        f'{PHASE}/results/calib'], cwd=root, capture_output=True, text=True)
    assert not r.stdout.strip(), f'untracked files under scripts/ or results/calib/: {r.stdout.split()}'
    sums = json.loads(CHECKSUMS.read_text())
    for p in INPUTS:
        assert sha256(p) == sums[p], f'input changed since the lock: {p}'
    log('lock verified:', LOCK, '| input checksums match | no untracked files')


# ------------------------------------------------------------------------------------------------------- decoy data
def make_decoy(recs, rng):
    """Label o-words -> random paragraph o-words; break-adjacent words -> random paragraph words of the same language
    and section (random line positions)."""
    recs = copy.deepcopy(recs)
    text_o, by_ls = [], defaultdict(list)
    for r in recs:
        if r['kind'].startswith('P'):
            for seg in r['segments']:
                for w, _ in seg:
                    if Z.readable(w):
                        by_ls[(r['lang'], r['section'])].append(w)
                        if w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                            text_o.append(w)
    for r in recs:
        if r['kind'].startswith('L'):
            for seg in r['segments']:
                for i, (w, sep) in enumerate(seg):
                    if Z.readable(w) and w.startswith('o') and not w.startswith('qo'):
                        seg[i] = (text_o[rng.integers(len(text_o))], sep)
        elif r['kind'].startswith('P') and len(r['segments']) > 1:
            pool = by_ls[(r['lang'], r['section'])]
            segs = r['segments']
            for j in range(len(segs) - 1):
                if segs[j]:
                    segs[j][-1] = (pool[rng.integers(len(pool))], segs[j][-1][1])
                if segs[j + 1]:
                    segs[j + 1][0] = (pool[rng.integers(len(pool))], segs[j + 1][0][1])
    return recs


# ------------------------------------------------------------------------------------------------------------ Arm L
MIN_REF_FRAGILE = 50


def min_ref_l4(cnts, groups):
    """Smallest reference component size over the length groups with L >= 4 (all reference sets in cnts)."""
    return int(min(sum(c[L][k].sum() for L in g) for c in cnts for g in groups if min(g) >= 4 for k in S.REFS))


def fit_grouped(items, cnt, rng, groups=S.FINE, alpha_text=None, fit_check=False):
    comps = S.comps_grouped(cnt, groups)
    fols, C = S.grouped_counts(items, groups)
    w = S.grouped_fit(C, comps)
    boots = S.grouped_boot(C, comps, rng, NBOOT)
    lo, hi = np.quantile(boots, 0.025, axis=0), np.quantile(boots, 0.975, axis=0)
    Ctot = C.sum(0)
    exp = np.einsum('k,gkc->gc', w, comps) * Ctot.sum(1, keepdims=True)
    out = {'n_words': int(Ctot.sum()), 'n_folios': len(fols),
           'weights': dict(zip(S.REFS, np.round(w, 4).tolist())),
           'ci95': {k: [round(float(a), 4), round(float(b), 4)] for k, a, b in zip(S.REFS, lo, hi)},
           'call': S.label_call(lo),
           'observed': dict(zip(S.CATS, Ctot.sum(0).astype(int).tolist())),
           'expected': dict(zip(S.CATS, np.round(exp.sum(0), 1).tolist()))}
    out['min_ref_L4plus'] = min_ref_l4([cnt], groups)
    out['feeds_fragile'] = out['min_ref_L4plus'] >= MIN_REF_FRAGILE
    if fit_check:
        a_lab = S.label_alpha(C)
        a_fc = min(alpha_text, a_lab)
        p = S.grouped_fit_check_p(C, comps, a_fc, rng, NFIT_R)
        out.update({'alpha_labels': round(a_lab, 2), 'alpha_fit_check': round(a_fc, 2), 'fit_check_p': round(p, 4),
                    'flag_no_mixture_fits': bool(p < 0.01)})
        prng = np.random.default_rng(77120)
        pw = S.power_grouped(C.sum(2).astype(int), comps, a_lab, prng, NPOW, BPOW,
                             {t: np.eye(3)[i].tolist() for i, t in enumerate(S.REFS)})
        out['power_at_label_clustering'] = {t: pw[t].get(name, 0.0) for t, name in
                                            zip(S.REFS, ('o = qo without q', 'ordinary o-words', 'o added to a word'))}
    return out


def arm_l(recs, lines, rng):
    cnt = S.references_by_length(lines)
    alpha_text = S.dirichlet_concentration(S.text_folio_matrix(lines, 'o'))[0]
    items = S.label_o_items(recs)
    prim = fit_grouped(items, cnt, rng, alpha_text=alpha_text, fit_check=True)
    res = {'alpha_text_o': round(alpha_text, 2), 'ref_sizes': S.ref_sizes(cnt), 'primary': prim}
    log('Arm L primary:', json.dumps({k: prim[k] for k in ('n_words', 'n_folios', 'weights', 'ci95', 'call')}))
    log('  fit check p', prim['fit_check_p'], '| alpha labels', prim['alpha_labels'], '| power at label clustering',
        prim['power_at_label_clustering'])
    sens = {}
    # s1 language-matched references: groups = language x length stratum (AZC labels keep the pooled references)
    lang_cnt = {'A': S.references_by_length(lines, lang='A'), 'B': S.references_by_length(lines, lang='B'), '*': cnt}
    comps_l = np.concatenate([S.comps_grouped(lang_cnt[g]) for g in ('A', 'B', '*')])
    lg = lambda lang: {'A': 0, 'B': 1}.get(lang, 2)
    fols = sorted({it[0] for it in items})
    fi = {f: i for i, f in enumerate(fols)}
    gi = S.group_index(S.FINE)
    C1 = np.zeros((len(fols), comps_l.shape[0], len(S.CATS)))
    for f, lang, sec, kind, L, c in items:
        C1[fi[f], lg(lang) * len(S.FINE) + gi[L], S.CIDX[c]] += 1
    w1 = S.grouped_fit(C1, comps_l)
    b1 = S.grouped_boot(C1, comps_l, rng, NBOOT)
    lo1 = np.quantile(b1, 0.025, axis=0)
    sens['s1_language_matched'] = {'weights': dict(zip(S.REFS, np.round(w1, 4).tolist())),
                                   'ci95': {k: [round(float(a), 4), round(float(b), 4)] for k, a, b in
                                            zip(S.REFS, lo1, np.quantile(b1, 0.975, axis=0))},
                                   'call': S.label_call(lo1), 'n_words': len(items)}
    sens['s1_language_matched']['min_ref_L4plus'] = min_ref_l4(list(lang_cnt.values()), S.FINE)
    sens['s1_language_matched']['feeds_fragile'] = sens['s1_language_matched']['min_ref_L4plus'] >= MIN_REF_FRAGILE
    sens['s2_line_initial_refs_no_par_first'] = fit_grouped(
        items, S.references_by_length(lines, line_initial_only=True, exclude_par_first=True), rng)
    lines3 = S.text_lines(recs, merge_uncertain=True)
    sens['s3_merged_spaces'] = fit_grouped(S.label_o_items(recs, merge_uncertain=True),
                                           S.references_by_length(lines3), rng)
    if not DRY:
        sens['s4_h_track'] = fit_grouped(S.label_o_items(recs, h_track=True), cnt, rng)
    by_sys = defaultdict(list)
    for it in items:
        by_sys[S.label_system(it[2])].append(it)
    s5 = {k: fit_grouped(v, cnt, rng) for k, v in sorted(by_sys.items()) if len(v) >= 20}
    sens['s6_init_without_o_q'] = fit_grouped(items, S.references_by_length(lines, init_exclude_oq=True), rng)
    azc_lines = S.text_lines(recs, kinds=('R', 'C'))
    azc_items = [it for it in items if it[2] in ('Z', 'C', 'A')]
    if azc_items:
        azc_cnt = S.references_by_length(azc_lines)
        sens['s7_azc_labels_vs_azc_ring_text'] = fit_grouped(azc_items, azc_cnt, rng, groups=S.COARSE)
        sens['s7_azc_labels_vs_azc_ring_text']['ref_sizes'] = S.ref_sizes(azc_cnt, S.COARSE)
    sens['s8_type_weighted_refs'] = fit_grouped(items, S.references_by_length(lines, type_weighted=True), rng)
    res['sensitivity'] = sens
    res['s5_systems'] = s5
    for k, v in sens.items():
        log(f'  {k}: {v["call"]} {v["weights"]} (min ref L>=4: {v["min_ref_L4plus"]}, feeds fragile: '
            f'{v["feeds_fragile"]})')
    for k, v in s5.items():
        log(f'  s5 {k}: n={v["n_words"]} folios={v["n_folios"]} {v["call"]} {v["weights"]}')
    # verdict assembly (pre-registered)
    call = prim['call']
    powers = prim['power_at_label_clustering']
    verdict = call
    if call == 'MIXED / UNRESOLVED' and min(powers.values()) < 0.8:
        verdict = 'UNINFORMATIVE'
    if prim['flag_no_mixture_fits']:
        verdict += ' [no mixture of the three fits]'
    other_pure = sorted({v['call'] for v in list(sens.values()) + list(s5.values())
                         if v['feeds_fragile'] and v['call'] in PURE and v['call'] != call})
    fragile = bool(other_pure)
    if fragile:
        verdict += ' [fragile: ' + '; '.join(other_pure) + ']'
    top = lambda v: max(v['weights'], key=v['weights'].get)
    same_top = len({top(v) for v in s5.values()}) == 1 if s5 else False
    res['verdict'] = verdict
    res['fragile'] = fragile
    res['mixed_is_evidence_of_within_label_mixture'] = bool(call == 'MIXED / UNRESOLVED' and not
                                                            prim['flag_no_mixture_fits'] and
                                                            min(powers.values()) >= 0.8 and same_top)
    res['s5_same_largest_weight'] = same_top
    log('  Arm L VERDICT:', verdict)
    res['descriptive_stem_families'] = stem_families(recs, lines, rng)
    log('  stem families:', json.dumps(res['descriptive_stem_families']))
    return res


def stem_families(recs, lines, rng):
    T = Counter(w for ln in lines for s in ln['segs'] for w in s if Z.readable(w))
    labs = [w for f, l, s, w in S.label_o_word_strings(recs)]

    def fam(x, self_o=0):
        return T['qo' + x], T['o' + x] - self_o, T[x]

    def summarise(rows):
        rows = [r for r in rows if sum(r) > 0]
        if not rows:
            return {'n_with_family': 0}
        a = np.array(rows, float)
        pooled = a.sum(0) / a.sum()
        per = (a / a.sum(1, keepdims=True)).mean(0)
        return {'n_with_family': len(rows), 'pooled_share_qoX_oX_X': np.round(pooled, 3).tolist(),
                'mean_share_qoX_oX_X': np.round(per, 3).tolist()}
    lab_rows = [fam(w[1:]) for w in labs]
    text_o = [w for ln in lines for s in ln['segs'] for w in s
              if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2]
    ctrl_rows = [fam(w[1:], self_o=1) for w in text_o]
    binf = lambda r: int(np.log2(max(sum(r), 1)))
    by_bin = defaultdict(list)
    for r in ctrl_rows:
        if sum(r) > 0:
            by_bin[binf(r)].append(r)
    matched = []
    for r in lab_rows:
        if sum(r) > 0 and by_bin.get(binf(r)):
            pool = by_bin[binf(r)]
            matched.append(pool[rng.integers(len(pool))])
    return {'labels': {'n_label_words': len(labs), **summarise(lab_rows)},
            'text_o_words_matched': summarise(matched)}


# ------------------------------------------------------------------------------------------------------------ Arm E
def arm_e(recs, lines, rng, cal):
    words, breaks = S.edge_tables(lines)
    attested = Counter(w['word'] for w in words)
    cut = lambda b: attested[b['pre'] + b['post']] >= 2
    one_unit = lambda b: len(Z.units(b['post'])) == 1 or len(Z.units(b['pre'])) == 1
    w2, b2 = S.edge_tables(S.text_lines(recs, merge_uncertain=True))
    res = {'n_breaks_cut_word_candidates': sum(cut(b) for b in breaks)}
    for lang in ('A', 'B'):
        for side in ('start', 'end'):
            key = f'{lang}_{side}'
            c = cal['arm_E'][key]
            p_seg = c['seg']['calls'].get('E-seg', 0.0)
            p_line = c['line']['calls'].get('E-line', 0.0)
            evaluable = p_seg >= 0.8 and p_line >= 0.8
            r = S.EdgeArm(words, breaks, lang, side, seed=771).evaluate(B=NBOOT, rng=rng)
            r['evaluable'] = evaluable
            r['calibrated_power'] = {'E-seg': p_seg, 'E-line': p_line}
            sens = {
                't1_no_single_unit_words': S.EdgeArm(words, [b for b in breaks if not one_unit(b)], lang, side, 771),
                't2_merged_spaces': S.EdgeArm(w2, b2, lang, side, 771),
                't3_relative_position': S.EdgeArm(words, breaks, lang, side, 771, match='rel'),
                't4_single_break_lines': S.EdgeArm(words, [b for b in breaks if b['n_breaks_line'] == 1], lang, side,
                                                   771),
                't5_no_cut_word_candidates': S.EdgeArm(words, [b for b in breaks if not cut(b)], lang, side, 771)}
            sres = {k: a.evaluate(B=NBOOT, rng=rng) for k, a in sens.items()}
            r['sensitivity'] = {k: {'I': round(v['I'], 3), 'ci95': [round(x, 3) for x in v['ci95']],
                                    'call': v['call'], 'n_breaks': v['n_breaks']} for k, v in sres.items()}
            opposite = {'E-seg': 'E-line', 'E-line': 'E-seg'}.get(r['call'])
            r['fragile'] = bool(opposite and any(v['call'] == opposite for v in sres.values()))
            verdict = r['call'] if evaluable else f'descriptive ({r["call"]})'
            if r['fragile']:
                verdict += ' [fragile]'
            r['verdict'] = verdict
            res[key] = r
            log(f'Arm E {key}: n={r["n_breaks"]} folios={r["n_break_folios"]} I={r["I"]:.3f} '
                f'CI=[{r["ci95"][0]:.3f}, {r["ci95"][1]:.3f}] -> {verdict}')
            for k, v in r['sensitivity'].items():
                log(f'    {k}: I={v["I"]} CI={v["ci95"]} {v["call"]} (n={v["n_breaks"]})')
    arm_level = {}
    for side in ('start', 'end'):
        a, b = res[f'A_{side}'], res[f'B_{side}']
        if a['evaluable'] and b['evaluable'] and a['call'] == b['call']:
            arm_level[side] = a['call']
        else:
            arm_level[side] = 'no arm-level statement (languages differ or a cell is descriptive)'
    res['arm_level'] = arm_level
    log('  Arm E arm-level:', arm_level)
    res['descriptive'] = edge_descriptives(words, breaks)
    log('  descriptive:', json.dumps(res['descriptive']))
    return res


def edge_descriptives(words, breaks):
    if str(Z.ROOT) not in sys.path:
        sys.path.insert(0, str(Z.ROOT))
    from scripts.voynich import Morphology
    m = Morphology()
    art = lambda w: bool(m.extract(w).has_articulator)
    out = {}
    for lang in ('A', 'B'):
        W = [w for w in words if w['lang'] == lang]
        Bk = [b for b in breaks if b['lang'] == lang]
        init = [w['word'] for w in W if w['i_start'] == 0 and not w['par_first_line']]
        fin = [w['word'] for w in W if w['i_end'] == 0 and not w['par_last_line']]
        mid = [w['word'] for w in W if w['i_start'] > 0 and w['i_end'] > 0]
        post = [b['post'] for b in Bk]
        pre = [b['pre'] for b in Bk]
        rate = lambda ws, f: round(float(np.mean([f(w) for w in ws])), 4) if ws else None
        out[lang] = {
            'articulator_rate': {'continuation_line_initial': rate(init, art), 'mid': rate(mid, art),
                                 'post_break': rate(post, art)},
            'bare_aiin_count': {'post_break': sum(w == 'aiin' for w in post),
                                'continuation_line_initial': sum(w == 'aiin' for w in init),
                                'mid_rate': rate(mid, lambda w: w == 'aiin')},
            'm_final_rate': {'continuation_line_final': rate(fin, lambda w: w.endswith('m')),
                             'mid': rate(mid, lambda w: w.endswith('m')),
                             'pre_break': rate(pre, lambda w: w.endswith('m'))}}
    return out


def main():
    global LOGF
    if '--checksums' in sys.argv:
        CHECKSUMS.write_text(json.dumps({p: sha256(p) for p in INPUTS}, indent=1))
        print('wrote', CHECKSUMS)
        return
    t0 = time.time()
    if not DRY:
        verify_lock()                                   # before any data is loaded or the log is opened
    OUT.mkdir(parents=True, exist_ok=True)
    LOGF = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
    rng = np.random.default_rng(SEED)
    recs = Z.load()
    if DRY:
        log('DRY RUN on a decoy copy of the data (no lock check; no real label or break glyph is read)')
        recs = make_decoy(recs, np.random.default_rng(99))
    else:
        log('lock verified before loading:', LOCK)
    cal = json.loads((Z.ROOT / PHASE / 'results/calib/cal771.json').read_text())
    lines = S.text_lines(recs)
    res = {'dry': DRY, 'arm_L': arm_l(recs, lines, rng)}
    res['arm_E'] = arm_e(recs, lines, rng, cal)
    res['runtime_s'] = round(time.time() - t0, 1)
    (OUT / 'phase771_results.json').write_text(json.dumps(res, indent=1))
    log('done', res['runtime_s'], 's')
    LOGF.close()


if __name__ == '__main__':
    main()

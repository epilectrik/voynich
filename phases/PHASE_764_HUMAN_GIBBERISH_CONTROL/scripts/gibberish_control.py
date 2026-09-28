#!/usr/bin/env python3
"""PHASE_764 — human gibberish vs Currier B boundary coupling. Definitions: ../PRE_REGISTRATION.md (locked 839f565).

Order: data -> matched references -> certification (B-vs-B positive control, shuffled-G negative control)
-> real-order G statistics -> variants and sensitivities -> descriptive -> locked verdict.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import g764 as G  # noqa: E402
from prelock_b_checks import flat, folio_sections  # noqa: E402

OUT = G.ROOT / 'phases/PHASE_764_HUMAN_GIBBERISH_CONTROL/results'
OUT.mkdir(parents=True, exist_ok=True)
LOG = open(OUT / 'run_log.txt', 'w', encoding='utf-8')
T0 = time.time()
R_SHUF, N_REF, N_BOOT, P_MIN = 200, 200, 1000, 197
RES = {'phase': 'PHASE_764', 'pre_registration_commit': '839f565'}


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(f'[{time.time() - T0:6.0f}s] {msg}', flush=True)
    LOG.write(f'[{time.time() - T0:6.0f}s] {msg}\n')
    LOG.flush()


def save(name='gibberish_control.json'):
    json.dump(RES, open(OUT / name, 'w', encoding='utf-8'), indent=1,
              default=lambda o: o.item() if hasattr(o, 'item') else str(o))


# ------------------------------------------------------------------------------------------ statistics per chunk
def s1_excess(segs, rng, topk=None, edge_fixed=False, normalise=False):
    C = G.Chunk(segs, topk=topk)
    o, m, p, e = G.shuffle_corrected(C, G.stat_S1, R_SHUF, rng, edge_fixed=edge_fixed)
    if normalise:
        h = G.entropy_F1(C)
        return e / h if h > 0 else float('nan')
    return e


def s2_excess(segs, rng):
    return G.shuffle_corrected(G.Chunk(segs), G.stat_S2, R_SHUF, rng)[3]


def s3_excess(segs, rng):
    return G.shuffle_corrected(G.Chunk(segs), G.stat_S3, R_SHUF, rng)[3]


def recut(segs, lengths, rng):
    out = []
    for s in segs:
        i = 0
        while i < len(s):
            L = max(1, int(rng.choice(lengths)))
            out.append(s[i:i + L])
            i += L
    return [x for x in out if x]


# ------------------------------------------------------------------------------------------ B chunk drawing
class BPool:
    def __init__(self, corpus, fsec):
        self.segs, self.sec, self.fol = flat(corpus, fsec)
        self.pairs = np.array([len(s) - 1 for s in self.segs])
        self.fol_arr = np.array(self.fol)
        self.folios = sorted(set(self.fol))
        fw = np.array([self.pairs[self.fol_arr == f].sum() for f in self.folios], float)
        self.fw = fw / fw.sum()
        self.idx_of = {f: np.flatnonzero(self.fol_arr == f) for f in self.folios}

    def draw(self, P, rng, single_folio=False, exclude=None, tries=200):
        for _ in range(tries):
            f = self.folios[rng.choice(len(self.folios), p=self.fw)]
            if exclude is not None and f == exclude:
                continue
            start = int(rng.choice(self.idx_of[f]))
            j = start
            while j < len(self.segs) and self.sec[j] == self.sec[start] and (not single_folio or self.fol[j] == f):
                if exclude is not None and self.fol[j] == exclude:
                    break
                j += 1
            ch = G.chunk_pairs(self.segs[start:j], 0, P)
            if ch is not None:
                # folios touched
                used, got, k = set(), 0, start
                while got < P and k < j:
                    used.add(self.fol[k])
                    got += max(0, len(self.segs[k]) - 1)
                    k += 1
                return ch, f, len(used) > 1
        return None, None, None


# ------------------------------------------------------------------------------------------ AUC machinery
def auc_rows(g_vals, ref_vals):
    """g_vals: (n,), ref_vals: list of arrays (ref for each sample). Returns per-sample P(ref > g)."""
    out = []
    for g, ref in zip(g_vals, ref_vals):
        ref = np.asarray(ref, float)
        ref = ref[np.isfinite(ref)]
        out.append(float(((ref > g).sum() + 0.5 * (ref == g).sum()) / len(ref)))
    return np.array(out)


def auc_boot(g_vals, ref_vals, ref_blocks, rng, n=N_BOOT):
    """Bootstrap: resample samples; within each, resample reference items in blocks (block labels)."""
    g_vals = np.asarray(g_vals, float)
    k = len(g_vals)
    point = float(auc_rows(g_vals, ref_vals).mean())
    grouped = []
    for ref, blk in zip(ref_vals, ref_blocks):
        ref = np.asarray(ref, float)
        d = defaultdict(list)
        for v, b in zip(ref, blk):
            d[b].append(v)
        grouped.append([np.array(v) for v in d.values()])
    stats = []
    for _ in range(n):
        pick = rng.integers(0, k, k)
        vals = []
        for i in pick:
            blocks = grouped[i]
            sel = rng.integers(0, len(blocks), len(blocks))
            ref = np.concatenate([blocks[j] for j in sel])
            ref = ref[np.isfinite(ref)]
            g = g_vals[i]
            vals.append(((ref > g).sum() + 0.5 * (ref == g).sum()) / len(ref))
        stats.append(np.mean(vals))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return {'auc': point, 'lo': float(lo), 'hi': float(hi), 'half_width': float((hi - lo) / 2)}


def label(ci):
    if ci['lo'] >= 0.80:
        return 'NOT REPRODUCED'
    if ci['lo'] >= 0.30 and ci['hi'] <= 0.70:
        return 'REPRODUCED'
    if ci['hi'] < 0.30:
        return 'EXCEEDED'
    return 'UNRESOLVED'


# ------------------------------------------------------------------------------------------ main
def main():
    rng_draw = np.random.default_rng(764)
    rng_s = np.random.default_rng(7641)
    rng_b = np.random.default_rng(7642)
    fsec = folio_sections()
    B = BPool(G.load_b_zl(True), fsec)
    B_all = BPool(G.load_b_zl(False), fsec)
    B_h = BPool(G.load_b_h(), fsec)
    B_eva = BPool(G.load_b_zl(True, unit='EVA'), fsec)
    gib = G.load_gibberish()
    mean = G.load_meaningful()
    mean_names = sorted(mean)
    Pn = {k: G.n_pairs(v) for k, v in gib.items()}
    incl = sorted([k for k in gib if Pn[k] >= P_MIN])
    RES['data'] = {'B_words': sum(len(s) for s in B.segs), 'G_samples': len(gib), 'G_included_S1': incl,
                   'G_pairs': Pn, 'M_texts': len(mean)}
    log('G included for S1:', len(incl), '| M texts:', len(mean))
    seglen = {k: [len(s) for s in gib[k]] for k in gib}

    # ---------------- matched references (B chunks, M chunks) -- no G statistic yet
    refs = {}
    for k in incl:
        P = Pn[k]
        b = [B.draw(P, rng_draw) for _ in range(N_REF)]
        m_chunks = []
        for name in mean_names:
            segs = mean[name]
            for _ in range(50):
                st = int(rng_draw.integers(0, len(segs)))
                stream = segs[st:st + 400]
                rw = G.rewrap(stream, seglen[k], rng_draw)
                ch = G.chunk_pairs(rw, 0, P)
                if ch is not None:
                    m_chunks.append((name, ch))
                    break
        refs[k] = {'B': b, 'M': m_chunks}
    log('references drawn')
    cross_share = float(np.mean([x[2] for k in incl for x in refs[k]['B']]))
    RES['B_reference_cross_folio_share'] = cross_share

    def ref_stat(k, fn, which='B'):
        if which == 'B':
            return [fn(ch) for ch, f, c in refs[k]['B']], [f for ch, f, c in refs[k]['B']]
        return [fn(ch) for name, ch in refs[k]['M']], [name for name, ch in refs[k]['M']]

    S1 = lambda segs: s1_excess(segs, rng_s)  # noqa: E731
    B_S1 = {k: ref_stat(k, S1) for k in incl}
    log('B reference S1 computed')

    # ---------------- certification (ii) positive control, (iii) negative control
    pos_vals, pos_refs, pos_blocks = [], [], []
    for k in incl:
        ch, f, _ = B.draw(Pn[k], rng_draw, single_folio=True)
        if ch is None:
            continue
        pos_vals.append(S1(ch))
        ref = [(v, fo) for (v, fo), (c2, f2, cr) in zip(zip(*B_S1[k]), refs[k]['B']) if fo != f]
        pos_refs.append([v for v, _ in ref])
        pos_blocks.append([fo for _, fo in ref])
    pos = auc_boot(pos_vals, pos_refs, pos_blocks, rng_b)
    pos['label'] = label(pos)
    neg_vals = []
    for k in incl:
        C = G.Chunk(gib[k])
        order = C.perms(1, rng_s)[0]
        words = [C.words[i] for i in order]
        segs, pos_i = [], 0
        for s in gib[k]:
            segs.append(words[pos_i:pos_i + len(s)])
            pos_i += len(s)
        neg_vals.append(S1(segs))
    neg = auc_boot(neg_vals, [B_S1[k][0] for k in incl], [B_S1[k][1] for k in incl], rng_b)
    neg['label'] = label(neg)
    certified = bool(pos['label'] == 'REPRODUCED' and pos['half_width'] <= 0.15 and neg['label'] == 'NOT REPRODUCED')
    RES['certification'] = {'power_prelock': 'met (0.895 at P=224; 80% at ~197)', 'positive_control': pos,
                            'negative_control': neg, 'certified': certified}
    log('certification: positive', pos, '| negative', neg, '| certified', certified)
    save()

    # ---------------- real-order G statistics (primary)
    g_s1 = np.array([S1(gib[k]) for k in incl])
    prim = auc_boot(g_s1, [B_S1[k][0] for k in incl], [B_S1[k][1] for k in incl], rng_b)
    prim['label'] = label(prim)
    M_S1 = {k: ref_stat(k, S1, 'M') for k in incl}
    mg = auc_boot(g_s1, [M_S1[k][0] for k in incl], [M_S1[k][1] for k in incl], rng_b)
    # AUC_BM: P(B chunk > M chunk), per sample over all combos, bootstrap over samples and folio blocks
    bm_point = []
    for k in incl:
        bv = np.array(B_S1[k][0]); mv = np.array(M_S1[k][0])
        bm_point.append(float((bv[:, None] > mv[None, :]).mean() + 0.5 * (bv[:, None] == mv[None, :]).mean()))
    bm_boot = []
    for _ in range(N_BOOT):
        pick = rng_b.integers(0, len(incl), len(incl))
        vals = []
        for i in pick:
            k = incl[i]
            bv = np.array(B_S1[k][0])[rng_b.integers(0, N_REF, N_REF)]
            mv = np.array(M_S1[k][0])[rng_b.integers(0, len(M_S1[k][0]), len(M_S1[k][0]))]
            vals.append((bv[:, None] > mv[None, :]).mean())
        bm_boot.append(np.mean(vals))
    bm = {'auc': float(np.mean(bm_point)), 'lo': float(np.percentile(bm_boot, 2.5)), 'hi': float(np.percentile(bm_boot, 97.5))}
    RES['S1'] = {'G_values': dict(zip(incl, g_s1.tolist())),
                 'B_ref_median': {k: float(np.median(B_S1[k][0])) for k in incl},
                 'M_ref_median': {k: float(np.median(M_S1[k][0])) for k in incl},
                 'AUC_BG': prim, 'AUC_MG': mg, 'AUC_BM': bm}
    log('S1 primary AUC_BG', prim, '| AUC_MG', mg, '| AUC_BM', bm)
    save()

    # ---------------- variants V1-V5
    variants = {}
    # V1 EVA
    B_eva_S1 = {}
    for k in incl:
        vals, blk = [], []
        for _ in range(N_REF):
            ch, f, _ = B_eva.draw(Pn[k], rng_draw)
            vals.append(S1(ch)); blk.append(f)
        B_eva_S1[k] = (vals, blk)
    variants['V1_EVA'] = auc_boot(g_s1, [B_eva_S1[k][0] for k in incl], [B_eva_S1[k][1] for k in incl], rng_b)
    # V2 top-6, V4 edge-fixed, V5 normalised
    for name, kw in (('V2_top6', {'topk': 6}), ('V4_edge_fixed', {'edge_fixed': True}), ('V5_normalised', {'normalise': True})):
        fn = lambda segs, kw=kw: s1_excess(segs, rng_s, **kw)  # noqa: E731
        g_v = np.array([fn(gib[k]) for k in incl])
        refv = {k: ref_stat(k, fn) for k in incl}
        variants[name] = auc_boot(g_v, [refv[k][0] for k in incl], [refv[k][1] for k in incl], rng_b)
    # V3 segment-matched null for B
    v3 = {}
    for k in incl:
        vals, blk = [], []
        for _ in range(N_REF):
            for _t in range(50):
                ch, f, _ = B.draw(3 * Pn[k], rng_draw)
                if ch is None:
                    continue
                rc = recut(ch, seglen[k], rng_draw)
                c2 = G.chunk_pairs(rc, 0, Pn[k])
                if c2 is not None:
                    vals.append(S1(c2)); blk.append(f)
                    break
        v3[k] = (vals, blk)
    variants['V3_segment_matched'] = auc_boot(g_s1, [v3[k][0] for k in incl], [v3[k][1] for k in incl], rng_b)
    for v in variants.values():
        v['label'] = label(v)
    RES['variants'] = variants
    log('variants', {k: (round(v['auc'], 3), v['label']) for k, v in variants.items()})
    save()

    # ---------------- sensitivities (not verdict-bearing)
    sens = {}
    for name, pool in (('ZL_all_spaces', B_all), ('H_track', B_h)):
        ref = {}
        for k in incl:
            vals, blk = [], []
            for _ in range(N_REF):
                ch, f, _ = pool.draw(Pn[k], rng_draw)
                vals.append(S1(ch)); blk.append(f)
            ref[k] = (vals, blk)
        sens[name] = auc_boot(g_s1, [ref[k][0] for k in incl], [ref[k][1] for k in incl], rng_b)
        sens[name]['label'] = label(sens[name])
    single = {}
    for k in incl:
        vals, blk = [], []
        for _ in range(N_REF):
            ch, f, _ = B.draw(Pn[k], rng_draw, single_folio=True)
            if ch is not None:
                vals.append(S1(ch)); blk.append(f)
        single[k] = (vals, blk)
    sens['single_folio_reference'] = auc_boot(g_s1, [single[k][0] for k in incl], [single[k][1] for k in incl], rng_b)
    sens['single_folio_reference']['label'] = label(sens['single_folio_reference'])
    RES['sensitivities'] = sens
    log('sensitivities', {k: (round(v['auc'], 3), v['label']) for k, v in sens.items()})
    save()

    # ---------------- descriptive
    desc = {}
    band = [(np.percentile(B_S1[k][0], 5), np.percentile(B_S1[k][0], 95)) for k in incl]
    desc['J_G'] = float(np.mean([lo <= g <= hi for g, (lo, hi) in zip(g_s1, band)]))
    desc['J_M'] = float(np.mean([np.mean([lo <= v <= hi for v in M_S1[k][0]]) for k, (lo, hi) in zip(incl, band)]))
    # S2 aggregate
    s2_g = np.array([s2_excess(gib[k], rng_s) for k in incl])
    w = np.array([Pn[k] for k in incl], float)
    g_mean = float((s2_g * w).sum() / w.sum())
    B_S2 = {k: [s2_excess(ch, rng_s) for ch, f, c in refs[k]['B']] for k in incl}
    sets = np.array([[B_S2[k][j] for k in incl] for j in range(N_REF)])
    set_means = (sets * w[None, :]).sum(1) / w.sum()
    desc['S2'] = {'G_weighted_mean': g_mean, 'B_set_means_median': float(np.median(set_means)),
                  'G_percentile_in_B': float((set_means <= g_mean).mean())}
    # S3 (B vs G only), S4, near-repeat, retention, H(F1)
    s3_g = np.array([s3_excess(gib[k], rng_s) for k in incl])
    B_S3 = {k: [s3_excess(ch, rng_s) for ch, f, c in refs[k]['B']] for k in incl}
    desc['S3_AUC_BG'] = float(auc_rows(s3_g, [B_S3[k] for k in incl]).mean())

    def summ(fn):
        g = [fn(G.Chunk(gib[k])) for k in incl]
        b = [np.median([fn(G.Chunk(ch)) for ch, f, c in refs[k]['B'][:50]]) for k in incl]
        m = [np.median([fn(G.Chunk(ch)) for name, ch in refs[k]['M']]) for k in incl]
        return {'G_median': float(np.median(g)), 'B_median': float(np.median(b)), 'M_median': float(np.median(m))}
    desc['S4_repetition'] = summ(G.repetition_S4)
    desc['near_repeat_rate'] = summ(G.near_repeat_rate)
    desc['retention_E_1_over_n'] = summ(G.retention)
    desc['H_F1'] = summ(G.entropy_F1)
    RES['descriptive'] = desc
    log('descriptive', json.dumps(desc))
    save()

    # ---------------- locked verdict
    lab = prim['label']
    opposite = {'NOT REPRODUCED': {'REPRODUCED', 'EXCEEDED'}, 'REPRODUCED': {'NOT REPRODUCED'},
                'EXCEEDED': {'NOT REPRODUCED'}}
    flips = [n for n, v in variants.items() if v['label'] in opposite.get(lab, set())]
    final = 'UNRESOLVED' if flips else lab
    if not certified:
        verdict = 'UNINFORMATIVE AT THIS SIZE'
    elif final == 'NOT REPRODUCED':
        verdict = 'B-DISTINCT'
    elif final == 'REPRODUCED' or (final == 'EXCEEDED' and variants['V2_top6']['label'] == 'EXCEEDED'
                                   and variants['V5_normalised']['label'] == 'EXCEEDED'):
        verdict = 'GIBBERISH-COMPATIBLE'
    else:
        verdict = 'MIXED / UNRESOLVED'
    floor = None
    if final == 'NOT REPRODUCED' and bm['lo'] >= 0.80:
        floor = 'B exceeds both human gibberish and human meaningful text on S1; the contrast is not specific to meaninglessness'
    if prim['lo'] >= 0.30 and prim['hi'] <= 0.70 and bm['lo'] >= 0.30 and bm['hi'] <= 0.70:
        floor = 'human-written text in general reaches this level at this size'
    RES['verdict'] = {'S1_label': lab, 'variant_flips': flips, 'S1_final': final, 'certified': certified,
                      'floor_rule': floor, 'VERDICT': verdict}
    RES['runtime_s'] = time.time() - T0
    log('VERDICT (locked rules):', verdict, '| S1', lab, '| flips', flips, '| floor', floor)
    save()


if __name__ == '__main__':
    main()

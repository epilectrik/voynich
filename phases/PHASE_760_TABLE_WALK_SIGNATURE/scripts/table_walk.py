#!/usr/bin/env python3
"""PHASE_760 — table-walk signature. See ../PRE_REGISTRATION.md (locked, commit 785f797).

Per-slot kept-coordinate counts for adjacent tokens (PREFIX/MIDDLE/SUFFIX; glyph frame first/interior/last unit),
against N1 (zone-preserving line shuffle), N_EDGE (PHASE_756 N5 kernel, glyph-unit edges, beta = 4), N0 and NP;
known-effect checks; rotation test among eligible triples.
All coordinates are precomputed per vocabulary type; each replicate is O(n) vectorized.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Morphology, Transcript  # noqa: E402

spec = importlib.util.spec_from_file_location(
    'n5', ROOT / 'phases/PHASE_756_C957_JOINT_NULL/scripts/c957_joint_null_n5.py')
N5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N5)

OUT = ROOT / 'phases/PHASE_760_TABLE_WALK_SIGNATURE/results'
OUT.mkdir(parents=True, exist_ok=True)
SEED, R = 760, 1000
GLYPH_RE = re.compile(r'c[tkpf]h|[cs]h|i+[nrlm]|.')
SLOTS = ['PREFIX', 'MIDDLE', 'SUFFIX']
GSLOTS = ['FIRST', 'INTERIOR', 'LAST']


def log(*a):
    print(*a, flush=True)


# ================================================================================================ data
lines, secs, keys = N5.load_primary()
D = N5.Data(lines, secs, 'GLYPH')
vocab = D.vocab
V = len(vocab)
morph = Morphology()


def enc(values):
    """Map values to ints; None/'' -> -1."""
    ids = {}
    out = np.full(len(values), -1, dtype=np.int64)
    for i, v in enumerate(values):
        if v:
            out[i] = ids.setdefault(v, len(ids))
    return out


ext = [morph.extract(w) for w in vocab]
P = enc([m.prefix for m in ext])
M = enc([m.middle for m in ext])
S = enc([m.suffix for m in ext])
TUP = enc([f"{m.prefix}|{m.middle}|{m.suffix}" for m in ext])
SUFSTR = np.array([m.suffix or '' for m in ext], dtype=object)


def head_of(w):
    try:
        a = morph.atomize(w)
        for ch, role, _ in a.atoms:
            if role == 'HEAD':
                return ch
    except Exception:
        return None
    return None


HEAD = enc([head_of(w) for w in vocab])
units = [GLYPH_RE.findall(w) for w in vocab]
GF = enc([u[0] for u in units])
GI = enc([''.join(u[1:-1]) if len(u) > 2 else '' for u in units])
GL = enc([u[-1] for u in units])
GTUP = enc([' '.join(u) for u in units])
FRAMES = {'primary': ([P, M, S], TUP, SLOTS), 'glyph': ([GF, GI, GL], GTUP, GSLOTS)}
n_empty_middle = int(sum(1 for w in (x for ln in lines for x in ln if x) if not morph.extract(w).middle))

# gated pairs: consecutive certain tokens in the same line, line with >= 5 certain tokens
tok0 = D.tok0
n = len(tok0)
cert_per_line = np.array([sum(w is not None for w in ln) for ln in lines])
gated_line = cert_per_line >= 5
pair_ok = np.zeros(n - 1, dtype=bool)
pair_ok[:] = D.valid_edge[:-1] & gated_line[D.line_of[:-1]]
trip_ok = pair_ok[:-1] & pair_ok[1:]
section_of_pair = np.array([secs[li] for li in D.line_of[:-1]])


# ================================================================================================ statistics
def pair_arrays(tok, frame):
    coords, tup, _ = FRAMES[frame]
    a, b = tok[:-1], tok[1:]
    a = np.where(pair_ok, a, 0)
    b = np.where(pair_ok, b, 0)
    nonid = pair_ok & (tup[a] != tup[b])
    kept = [(c[a] >= 0) & (c[a] == c[b]) & nonid for c in coords]
    comp = [(c[a] >= 0) & (c[b] >= 0) & pair_ok for c in coords]
    return a, b, nonid, kept, comp


def stats(tok, frame='primary'):
    a, b, nonid, kept, comp = pair_arrays(tok, frame)
    out = {f'K_{s}': int(k.sum()) for s, k in zip(FRAMES[frame][2], kept)}
    if frame == 'primary':
        same_head = nonid & (HEAD[a] >= 0) & (HEAD[a] == HEAD[b])
        out['same_head_pairs'] = int(same_head.sum())
        out['M_kept_given_same_head_rate'] = float((kept[1] & same_head).sum() / max(same_head.sum(), 1))
        out['K_SUFFIX_without_dy'] = int((kept[2] & (SUFSTR[a] != 'dy')).sum())
        out['K_SUFFIX_dy'] = int((kept[2] & (SUFSTR[a] == 'dy')).sum())
        out['same_head_pairs_rate'] = float(same_head.sum() / max(nonid.sum(), 1))
        nk = sum(k.astype(int) for k in kept)
        ncomp = sum(c.astype(int) for c in comp)
        for kk in (2, 3):
            m = nonid & (ncomp == kk)
            for j in range(4):
                out[f'bin_k{kk}_{j}'] = int((m & (nk == j)).sum())
        # sensitivity: empty treated as a value
        coords = FRAMES['primary'][0]
        kept_e = [(c[a] == c[b]) & nonid for c in coords]
        nk_e = sum(k.astype(int) for k in kept_e)
        for j in range(4):
            out[f'bin_emptyvalue_{j}'] = int((nonid & (nk_e == j)).sum())
    out['nonidentical_pairs'] = int(nonid.sum())
    out['identical_tuple_pairs'] = int((pair_ok & ~nonid).sum())
    return out


def section_stats(tok):
    a, b, nonid, kept, comp = pair_arrays(tok, 'primary')
    return {sec: {f'K_{s}': int((k & (section_of_pair == sec)).sum()) for s, k in zip(SLOTS, kept)}
            for sec in sorted(set(secs))}


def rotation(tok):
    a, b, nonid, kept, comp = pair_arrays(tok, 'primary')
    nk = sum(k.astype(int) for k in kept)
    exactly_one = nonid & (nk == 1)
    lab = np.full(n - 1, -1)
    for i, k in enumerate(kept):
        lab[k & exactly_one] = i
    t = np.flatnonzero(trip_ok & exactly_one[:-1] & exactly_one[1:])
    return lab[t], lab[t + 1]


# ================================================================================================ nulls
def gen_N1(rng):
    tok = tok0.copy()
    keysr = rng.random(len(D.mov_pos))
    order = np.lexsort((keysr, D.line_of[D.mov_pos]))
    tok[D.mov_pos] = tok0[D.mov_pos][order]
    return tok


def gen_N0(rng):
    """Full within-line shuffle of certain tokens (blockers fixed)."""
    tok = tok0.copy()
    cert = np.flatnonzero(tok0 >= 0)
    order = np.lexsort((rng.random(len(cert)), D.line_of[cert]))
    tok[cert] = tok0[cert][order]
    return tok


# paragraphs (H, P placement; paragraph starts where a line's first token is paragraph-initial)
tx = Transcript()
par_start = {}
for t in tx.currier_b(exclude_uncertain=False):
    if not (t.placement and t.placement.startswith('P')):
        continue
    k = (t.folio, t.line)
    if k not in par_start:
        par_start[k] = bool(t.par_initial)
par_id_line = np.zeros(len(lines), dtype=np.int64)
pid = -1
prev_folio = None
for li, k in enumerate(keys):
    if par_start.get(k) or k[0] != prev_folio or pid < 0:
        pid += 1
    par_id_line[li] = pid
    prev_folio = k[0]


def gen_NP(rng):
    tok = tok0.copy()
    cert = np.flatnonzero(tok0 >= 0)
    grp = par_id_line[D.line_of[cert]] * 3 + D.zone[cert]
    order = np.lexsort((rng.random(len(cert)), grp))
    slots = cert[np.argsort(grp, kind='stable')]
    tok[slots] = tok0[cert][order]
    return tok


def run_null(gen, name):
    rng = np.random.default_rng(SEED)
    reps = {'primary': [], 'glyph': []}
    for _ in range(R):
        t = gen(rng)
        reps['primary'].append(stats(t, 'primary'))
        reps['glyph'].append(stats(t, 'glyph'))
    log(f"  null {name}: done")
    return reps


def run_nedge():
    reps = {'primary': [], 'glyph': []}
    diag = {'fc': [], 'tv': [], 'chain_K': defaultdict(list)}
    for beta in (4.0, 2.0):
        reps = {'primary': [], 'glyph': []}
        diag = {'fc': [], 'tv': [], 'chain_K': defaultdict(list)}
        for c in range(4):
            start = 'real' if c < 2 else 'N1'
            ck = defaultdict(list)

            def on_sample(tok, C, L1, ck=ck):
                sp, sg = stats(tok, 'primary'), stats(tok, 'glyph')
                reps['primary'].append(sp)
                reps['glyph'].append(sg)
                diag['fc'].append(N5.frac_changed(D, tok))
                diag['tv'].append(max(N5.group_tv(D, C)))
                for s in SLOTS:
                    ck[s].append(sp[f'K_{s}'])
            N5.run_chain(D, beta, 76000 + c, start, 2000, 1000, 250, 10, on_sample)
            for s in SLOTS:
                diag['chain_K'][s].append(ck[s])
        fc, tv = float(np.mean(diag['fc'])), float(np.mean(diag['tv']))
        log(f"  N_EDGE beta={beta}: fraction changed {fc:.3f}, max section TV {tv:.4f}")
        if fc >= 0.50 and tv <= 0.02:
            break
    rhat = {s: N5.rhat_rank(np.array(diag['chain_K'][s])) for s in SLOTS}
    return reps, {'beta': beta, 'fraction_changed': fc, 'max_section_tv': tv, 'rhat_K': rhat,
                  'achieved': bool(fc >= 0.50 and tv <= 0.02)}


def compare(real, reps, key, direction='up'):
    vals = np.array([r[key] for r in reps], dtype=float)
    obs = float(real[key])
    up = float((1 + (vals >= obs).sum()) / (1 + len(vals)))
    lo = float((1 + (vals <= obs).sum()) / (1 + len(vals)))
    return {'obs': obs, 'null_mean': float(vals.mean()), 'null_sd': float(vals.std()), 'excess': obs - float(vals.mean()),
            'p_up': up, 'p_low': lo, 'p': up if direction == 'up' else lo, 'MDE80': 2.485 * float(vals.std())}


# ================================================================================================ main
def main():
    t0 = time.time()
    real = {'primary': stats(tok0, 'primary'), 'glyph': stats(tok0, 'glyph')}
    log(f"real primary: {real['primary']}")
    log(f"gated pairs: {int(pair_ok.sum())}; effective movable pairs under N1: "
        f"{int((pair_ok & (np.isin(np.arange(n - 1), D.mov_pos) | np.isin(np.arange(1, n), D.mov_pos))).sum())}; "
        f"tokens with empty MIDDLE: {n_empty_middle}")
    nulls = {'N1': run_null(gen_N1, 'N1'), 'N0': run_null(gen_N0, 'N0'), 'NP': run_null(gen_NP, 'NP')}
    nedge, nedge_diag = run_nedge()
    nulls['N_EDGE'] = nedge
    res = {}
    for nn, reps in nulls.items():
        res[nn] = {'primary': {k: compare(real['primary'], reps['primary'], k)
                               for k in real['primary']},
                   'glyph': {k: compare(real['glyph'], reps['glyph'], k) for k in real['glyph']}}
    # per-slot verdicts
    slot_rows = {}
    for s, g in zip(SLOTS, GSLOTS):
        k = f'K_{s}'
        p1, pe = res['N1']['primary'][k]['p_up'], res['N_EDGE']['primary'][k]['p_up']
        if s == 'PREFIX':
            check = True
            check_note = 'excess is new relative to C549 alternation by construction'
        elif s == 'MIDDLE':
            c = res['N1']['primary']['M_kept_given_same_head_rate']
            check = c['p_up'] < 0.05
            check_note = f"conditional on same HEAD: p_up {c['p_up']:.4f}"
        else:
            c = res['N1']['primary']['K_SUFFIX_without_dy']
            check = c['p_up'] < 0.05
            check_note = f"without dy->dy: p_up {c['p_up']:.4f}"
        gl = res['N1']['glyph'][f'K_{g}']['p_up']
        new_pos = p1 < 0.01 / 3 and pe < 0.01 / 3 and check and gl < 0.05 and nedge_diag['achieved']
        slot_rows[s] = {'p_up_N1': p1, 'p_up_N_EDGE': pe, 'p_low_N1': res['N1']['primary'][k]['p_low'],
                        'p_low_N_EDGE': res['N_EDGE']['primary'][k]['p_low'],
                        'excess_N1': res['N1']['primary'][k]['excess'], 'excess_N_EDGE': res['N_EDGE']['primary'][k]['excess'],
                        'known_effect_check_pass': bool(check), 'check_note': check_note,
                        'glyph_frame_p_up_N1': gl, 'new_positive': bool(new_pos),
                        'MDE80_N1_pairs': res['N1']['primary'][k]['MDE80']}
        log(f"{s}: obs {real['primary'][k]} | N1 excess {slot_rows[s]['excess_N1']:+.1f} p_up {p1:.4f} p_low "
            f"{slot_rows[s]['p_low_N1']:.4f} | N_EDGE excess {slot_rows[s]['excess_N_EDGE']:+.1f} p_up {pe:.4f} p_low "
            f"{slot_rows[s]['p_low_N_EDGE']:.4f} | check {check} ({check_note}) | glyph p_up {gl:.4f} -> new_positive={new_pos}")
    # rotation
    l1, l2 = rotation(tok0)
    rng = np.random.default_rng(SEED)
    diag_obs = int((l1 == l2).sum())
    perm = np.array([int((l1 == rng.permutation(l2)).sum()) for _ in range(10_000)])
    rot = {'eligible_triples': int(len(l1)), 'table': [[int(((l1 == i) & (l2 == j)).sum()) for j in range(3)] for i in range(3)],
           'diagonal_obs': diag_obs, 'diagonal_null_mean': float(perm.mean()),
           'p_deficit': float((1 + (perm <= diag_obs).sum()) / 10_001),
           'p_excess': float((1 + (perm >= diag_obs).sum()) / 10_001), 'MDE80': 2.485 * float(perm.std())}
    log(f"rotation: {rot}")
    any_new = any(r['new_positive'] for r in slot_rows.values())
    if any_new and rot['p_deficit'] < 0.01:
        verdict = 'TABLE-WALK SIGNATURE'
    elif any_new and rot['p_deficit'] >= 0.05:
        verdict = 'SLOT PERSISTENCE (no walk)'
    elif not any_new:
        verdict = 'NO SIGNATURE'
    else:
        verdict = 'INCONCLUSIVE'
    known = {
        'C549_prefix_alternation_reproduced_N1': res['N1']['primary']['K_PREFIX']['p_low'] < 0.05,
        'C549_prefix_alternation_reproduced_N_EDGE': res['N_EDGE']['primary']['K_PREFIX']['p_low'] < 0.05,
        'C1002_dy_self_repetition_N1': res['N1']['primary']['K_SUFFIX_dy'],
        'C1002_dy_self_repetition_N_EDGE': res['N_EDGE']['primary']['K_SUFFIX_dy'],
        'C1562_same_head_N1': res['N1']['primary']['same_head_pairs'],
        'C1562_same_head_N_EDGE': res['N_EDGE']['primary']['same_head_pairs'],
    }
    sec_real = section_stats(tok0)
    rng = np.random.default_rng(SEED)
    sec_null = [section_stats(gen_N1(rng)) for _ in range(200)]
    sections = {sec: {k: {'obs': sec_real[sec][k], 'N1_mean': float(np.mean([x[sec][k] for x in sec_null]))}
                      for k in sec_real[sec]} for sec in sec_real}
    out = {'phase': 'PHASE_760', 'pre_registration_commit': '785f797', 'real': real, 'n_empty_middle_tokens': n_empty_middle,
           'gated_pairs': int(pair_ok.sum()), 'N_EDGE_diagnostics': nedge_diag, 'tests': res, 'slots': slot_rows,
           'rotation': rot, 'known_effects': known, 'sections_descriptive_N1_200reps': sections, 'verdict': verdict,
           'runtime_s': round(time.time() - t0, 1)}
    json.dump(out, open(OUT / 'table_walk.json', 'w', encoding='utf-8'), indent=1, default=float)
    log(f"VERDICT (locked rules): {verdict}  ({out['runtime_s']}s)")


if __name__ == '__main__':
    main()

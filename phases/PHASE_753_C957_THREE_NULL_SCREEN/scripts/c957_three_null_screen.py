#!/usr/bin/env python3
"""PHASE_753 — C957 three-null screen. See ../PRE_REGISTRATION.md (locked 2026-09-27, commit 4f6373c).

N0: full within-line permutation (C957's original null; replication).
N1: zone-preserving within-line shuffle (PRIMARY): INITIAL and FINAL fixed, MEDIAL permuted.
N2: edge-glyph generator: INITIAL kept; each later token drawn from real tokens in the same zone that follow a
    token ending in the same final EVA character as the previously generated token.
N3: POST-HOC joint null (added after the v1 run, NOT part of the locked verdict): within each line, MEDIAL tokens
    are permuted only among tokens with the same (first EVA char, last EVA char) signature. Line composition,
    zones and every boundary's (last glyph -> first glyph) transition are preserved exactly.

N4: POST-HOC joint null (v3): each line keeps its INITIAL and FINAL tokens and its multiset of MEDIAL tokens;
    MEDIAL tokens are re-ordered sequentially, each pick drawn from the line's remaining MEDIAL tokens with
    probability proportional to the real corpus rate T[last glyph of previous token -> first glyph of candidate]
    (the last pick also weighted by the transition into the FINAL token). Composition and zones are exact;
    boundary coupling is reproduced statistically. N3 turned out degenerate (changes ~13% of positions).

v2 (2026-09-27): v1 computed per-pair zero frequencies only for pairs that were candidates under the same null,
so pairs untracked under N2 defaulted to P0=0 and were falsely flagged "robust". v2 runs pass 1 for all nulls,
tracks one union set in every pass 2, and reports P0 only for tracked pairs. Screen-level statistics were
unaffected by the bug.

Two passes per null with identical seeds: pass 1 -> expected counts E_M; pass 2 -> zero counts among each
null's own candidate set, per-pair zero frequencies.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

OUT = ROOT / 'phases/PHASE_753_C957_THREE_NULL_SCREEN/results'
OUT.mkdir(parents=True, exist_ok=True)

MIN_TOKEN_FREQ = 10
E_PRIMARY, E_SENS = 5.0, 3.0
R = {'N0': 1000, 'N1': 1000, 'N2': 500, 'N3': 1000, 'N4': 500}
SEEDS = {'N0': 7530, 'N1': 7531, 'N2': 7532, 'N3': 7533, 'N4': 7534}
C957_ORIGINAL = [('chedy', 'aiin'), ('shedy', 'aiin'), ('chey', 'chedy'), ('chey', 'shedy')]  # extended below from file


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------ data
def load_lines():
    tx = Transcript()
    lines = defaultdict(list)
    for t in tx.currier_b():
        w = t.word.replace('*', '').strip()
        if w:
            lines[(t.folio, t.line)].append(w)
    return list(lines.values())


line_list = load_lines()
tok_counts = Counter(w for ln in line_list for w in ln)
common = sorted(w for w, c in tok_counts.items() if c >= MIN_TOKEN_FREQ)
K = len(common)
cid = {w: i for i, w in enumerate(common)}
vocab = sorted(tok_counts)
vid = {w: i for i, w in enumerate(vocab)}
v_common = np.array([cid.get(w, -1) for w in vocab], dtype=np.int64)          # vocab id -> common id or -1
glyphs = sorted({w[-1] for w in vocab})
gid = {g: i for i, g in enumerate(glyphs)}
v_lastglyph = np.array([gid[w[-1]] for w in vocab], dtype=np.int64)

# flat arrays
tokens = np.array([vid[w] for ln in line_list for w in ln], dtype=np.int64)
line_id = np.array([li for li, ln in enumerate(line_list) for _ in ln], dtype=np.int64)
pos = np.array([p for ln in line_list for p in range(len(ln))], dtype=np.int64)
L = np.array([len(ln) for ln in line_list for _ in ln], dtype=np.int64)
zone = np.where(pos == 0, 0, np.where(pos == L - 1, 2, 1))                     # 0 INITIAL, 1 MEDIAL, 2 FINAL
n_tok = len(tokens)
same_line_next = np.zeros(n_tok, dtype=bool)
same_line_next[:-1] = line_id[:-1] == line_id[1:]

log(f"lines={len(line_list)} tokens={n_tok} common={K} vocab={len(vocab)} glyphs={len(glyphs)}")


def pair_counts(tok_arr):
    """Counts of ordered common×common within-line adjacent pairs, as a flat K*K vector."""
    a = v_common[tok_arr[:-1]]
    b = v_common[tok_arr[1:]]
    ok = same_line_next[:-1] & (a >= 0) & (b >= 0)
    return np.bincount(a[ok] * K + b[ok], minlength=K * K)


real = pair_counts(tokens)
log(f"real common bigrams: {real.sum()}")

# ------------------------------------------------------------------------------------------------ nulls
def gen_N0(rng):
    keys = rng.random(n_tok)
    order = np.lexsort((keys, line_id))
    return tokens[order]


def gen_N1(rng):
    keys = rng.random(n_tok)
    order = np.lexsort((keys, zone, line_id))       # within line: INITIAL first, MEDIAL shuffled, FINAL last
    return tokens[order]


# N2 pools: (last glyph of preceding real token, zone of this token) -> array of vocab ids (real occurrences)
pool = defaultdict(list)
zone_pool = defaultdict(list)
for i in range(1, n_tok):
    if line_id[i] == line_id[i - 1]:
        pool[(v_lastglyph[tokens[i - 1]], zone[i])].append(tokens[i])
        zone_pool[zone[i]].append(tokens[i])
pool = {k: np.array(v, dtype=np.int64) for k, v in pool.items()}
zone_pool = {k: np.array(v, dtype=np.int64) for k, v in zone_pool.items()}
max_len = int(L.max())
line_start = np.array([np.flatnonzero(line_id == li)[0] for li in range(len(line_list))])
line_len = np.array([len(ln) for ln in line_list])
n2_fallback = Counter()


def gen_N2(rng):
    out = tokens.copy()                              # position 0 of every line keeps its real INITIAL token
    for p in range(1, max_len):
        live = np.flatnonzero(line_len > p)
        idx = line_start[live] + p
        prev_glyph = v_lastglyph[out[idx - 1]]
        z = np.where(p == line_len[live] - 1, 2, 1)
        keys = prev_glyph * 3 + z
        for key in np.unique(keys):
            sel = idx[keys == key]
            g, zz = divmod(int(key), 3)
            src = pool.get((g, zz))
            if src is None or len(src) == 0:
                src = zone_pool[zz]
                n2_fallback['fallback'] += len(sel)
            else:
                n2_fallback['pooled'] += len(sel)
            out[sel] = src[rng.integers(0, len(src), size=len(sel))]
    return out


sig = np.array([gid[w[0]] * len(glyphs) + gid[w[-1]] if w[0] in gid else -1 for w in vocab], dtype=np.int64)
# first chars may not be in the final-glyph alphabet: give them their own ids
first_ids = {c: i for i, c in enumerate(sorted({w[0] for w in vocab}))}
sig = np.array([first_ids[w[0]] * len(glyphs) + gid[w[-1]] for w in vocab], dtype=np.int64)
medial_idx = np.flatnonzero(zone == 1)
medial_group = line_id[medial_idx] * (len(first_ids) * len(glyphs) + 1) + sig[tokens[medial_idx]]
slot_order = medial_idx[np.lexsort((pos[medial_idx], medial_group))]
group_sorted = np.sort(medial_group)


def gen_N3(rng):
    out = tokens.copy()
    keys = rng.random(len(medial_idx))
    tok_order = medial_idx[np.lexsort((keys, medial_group))]
    out[slot_order] = tokens[tok_order]
    return out


# ---- N4: edge-weighted within-line reordering (composition + zones exact, edge coupling statistical)
NF, NL_ = len(first_ids), len(glyphs)
v_firstglyph = np.array([first_ids[w[0]] for w in vocab], dtype=np.int64)
T = np.full((NL_, NF), 0.5)
for i in range(n_tok - 1):
    if same_line_next[i]:
        T[v_lastglyph[tokens[i]], v_firstglyph[tokens[i + 1]]] += 1
T = T / T.sum(axis=1, keepdims=True)
n_lines = len(line_list)
m_len = np.maximum(line_len - 2, 0)
max_m = int(m_len.max())
MED = np.full((n_lines, max(max_m, 1)), -1, dtype=np.int64)
for li in range(n_lines):
    if m_len[li] > 0:
        MED[li, :m_len[li]] = tokens[line_start[li] + 1: line_start[li] + 1 + m_len[li]]
MED_first = np.where(MED >= 0, v_firstglyph[np.maximum(MED, 0)], 0)
MED_last = np.where(MED >= 0, v_lastglyph[np.maximum(MED, 0)], 0)
final_tok = tokens[line_start + line_len - 1]
final_first = v_firstglyph[final_tok]
line_rows = np.arange(n_lines)


def gen_N4(rng):
    out = tokens.copy()
    avail = MED >= 0
    prev_last = v_lastglyph[tokens[line_start]]
    for p in range(max_m):
        live = m_len > p
        if not live.any():
            break
        w = T[prev_last[:, None], MED_first] * avail
        last_pick = live & (m_len == p + 1)
        if last_pick.any():
            w[last_pick] *= T[MED_last[last_pick], final_first[last_pick][:, None]]
        w = w[live]
        cw = np.cumsum(w, axis=1)
        u = rng.random(w.shape[0]) * cw[:, -1]
        choice = (cw < u[:, None]).sum(axis=1)
        rows = line_rows[live]
        picked = MED[rows, choice]
        out[line_start[rows] + 1 + p] = picked
        avail[rows, choice] = False
        prev_last[rows] = v_lastglyph[picked]
    return out


GEN = {'N0': gen_N0, 'N1': gen_N1, 'N2': gen_N2, 'N3': gen_N3, 'N4': gen_N4}


def edge_dist(tok_arr):
    """Distribution of (last glyph, first glyph) over within-line adjacent pairs."""
    a = v_lastglyph[tok_arr[:-1]][same_line_next[:-1]]
    b = v_firstglyph[tok_arr[1:]][same_line_next[:-1]]
    c = np.bincount(a * NF + b, minlength=NL_ * NF).astype(float)
    return c / c.sum()


def null_diagnostics(name, reps=50):
    rng = np.random.default_rng(12345)
    real_e = edge_dist(tokens)
    ch, tv = [], []
    for _ in range(reps):
        g = GEN[name](rng)
        ch.append(float((g != tokens).mean()))
        tv.append(float(0.5 * np.abs(edge_dist(g) - real_e).sum()))
    return {'fraction_positions_changed': round(float(np.mean(ch)), 3),
            'edge_distribution_TV_vs_real': round(float(np.mean(tv)), 4)}

# ------------------------------------------------------------------------------------------------ analysis
analytic = None
src_c = np.zeros(K)
tgt_c = np.zeros(K)
for i in range(n_tok - 1):
    if same_line_next[i]:
        a, b = v_common[tokens[i]], v_common[tokens[i + 1]]
        if a >= 0 and b >= 0:
            src_c[a] += 1
            tgt_c[b] += 1
analytic = np.outer(src_c, tgt_c).ravel() / real.sum()
analytic_cand = analytic >= E_PRIMARY
log(f"analytic candidates (E>=5): {analytic_cand.sum()}  real zeros among them: {int((real[analytic_cand] == 0).sum())}")


def pass1(name):
    t0 = time.time()
    rng = np.random.default_rng(SEEDS[name])
    total = np.zeros(K * K, dtype=np.float64)
    for r in range(R[name]):
        total += pair_counts(GEN[name](rng))
    log(f"{name} pass1 {time.time() - t0:.1f}s")
    return total / R[name]


def summ(Znull, zreal):
    return {'Z_real': int(zreal), 'null_mean': float(Znull.mean()), 'null_sd': float(Znull.std()),
            'null_q95': float(np.quantile(Znull, 0.95)), 'null_q99': float(np.quantile(Znull, 0.99)),
            'null_max': int(Znull.max()),
            'p_one_sided': float((1 + (Znull >= zreal).sum()) / (1 + len(Znull)))}


def pass2(name, E, track):
    t0 = time.time()
    cand5, cand3 = E >= E_PRIMARY, E >= E_SENS
    rng = np.random.default_rng(SEEDS[name])
    Z5, Z3, Z_an = [], [], []
    zero_hits = np.zeros(K * K, dtype=np.int64)
    for r in range(R[name]):
        z = pair_counts(GEN[name](rng)) == 0
        Z5.append(int((z & cand5).sum()))
        Z3.append(int((z & cand3).sum()))
        Z_an.append(int((z & analytic_cand).sum()))
        zero_hits[track] += z[track]
    Z5, Z3, Z_an = map(np.array, (Z5, Z3, Z_an))
    res = {'replicates': R[name], 'seed': SEEDS[name], 'runtime_pass2_s': round(time.time() - t0, 1),
           'n_candidates_E5': int(cand5.sum()), 'n_candidates_E3': int(cand3.sum()),
           'E5': summ(Z5, int((cand5 & (real == 0)).sum())), 'E3': summ(Z3, int((cand3 & (real == 0)).sum())),
           'analytic_candidates': summ(Z_an, int((real[analytic_cand] == 0).sum())),
           'E': E, 'P0': np.where(track, zero_hits / R[name], np.nan)}
    log(f"{name}: E5 Z_real={res['E5']['Z_real']} null {res['E5']['null_mean']:.2f}±{res['E5']['null_sd']:.2f} "
        f"q99={res['E5']['null_q99']} p={res['E5']['p_one_sided']:.4f} | E3 Z_real={res['E3']['Z_real']} "
        f"null {res['E3']['null_mean']:.2f} q95={res['E3']['null_q95']} p={res['E3']['p_one_sided']:.4f} | "
        f"analytic Z_real={res['analytic_candidates']['Z_real']} null {res['analytic_candidates']['null_mean']:.2f}")
    return res


NULLS = ('N0', 'N1', 'N2', 'N3', 'N4')
diagnostics = {name: null_diagnostics(name) for name in NULLS}
for name, dgn in diagnostics.items():
    log(f"diagnostic {name}: {dgn}")
E_all = {name: pass1(name) for name in NULLS}
track = analytic_cand & (real == 0)
for name in NULLS:
    track |= (E_all[name] >= E_SENS) & (real == 0)
log(f"tracked pairs (union of real zeros that are E>=3 under any null, plus analytic): {int(track.sum())}")
results = {}
for name in NULLS:
    results[name] = pass2(name, E_all[name], track)
    json.dump({'interim_done': list(results)}, open(OUT / 'interim.json', 'w'))

# ------------------------------------------------------------------------------------------------ verdict
p1, p2 = results['N1']['E5']['p_one_sided'], results['N2']['E5']['p_one_sided']
p1s, p2s = results['N1']['E3']['p_one_sided'], results['N2']['E3']['p_one_sided']
if p1 < 0.01 and p2 < 0.01 and p1s < 0.05 and p2s < 0.05:
    verdict = 'CERTIFIED'
elif p1 >= 0.05:
    verdict = 'POSITIONAL'
elif p1 < 0.01 and p2 >= 0.05:
    verdict = 'PHONOTACTIC'
else:
    verdict = 'INCONCLUSIVE'
log(f"VERDICT (locked rules): {verdict}  [p_N1={p1:.4f}, p_N2={p2:.4f}; E3: p_N1={p1s:.4f}, p_N2={p2s:.4f}]")


def name_pair(k):
    return common[k // K], common[k % K]


def rev(k):
    a, b = divmod(k, K)
    return b * K + a


# per-pair table: union of analytic-candidate real zeros and N1/N2 E3 real zeros
pairs = np.flatnonzero(track).tolist()
per_pair = []
for k in pairs:
    a, b = name_pair(k)
    row = {'pair': f'{a}->{b}', 'real': int(real[k]), 'E_analytic': round(float(analytic[k]), 2)}
    for name in NULLS:
        row[f'E_{name}'] = round(float(results[name]['E'][k]), 2)
        row[f'P0_{name}'] = round(float(results[name]['P0'][k]), 4)
    rk = rev(k)
    row['reverse_real'] = int(real[rk])
    row['reverse_E_N1'] = round(float(results['N1']['E'][rk]), 2)
    # pre-registered definition (N1 and N2), plus the post-hoc joint-null definition (N1, N2 and N3)
    row['robust_zero'] = bool(row['P0_N1'] < 0.01 and row['P0_N2'] < 0.01)
    row['robust_zero_incl_N3'] = bool(row['robust_zero'] and row['P0_N3'] < 0.01)
    row['robust_zero_N1_N2_N4'] = bool(row['robust_zero'] and row['P0_N4'] < 0.01)
    row['robust_zero_N4_only'] = bool(row['P0_N4'] < 0.01)
    per_pair.append(row)
per_pair.sort(key=lambda r: (r['P0_N4'], r['P0_N1']))

# segmentation check for robust zeros: concatenated spellings across all transcriber tracks
tx = Transcript()
all_words = Counter()
h_words = Counter()
for t in tx.all(h_only=False):
    w = t.word.replace('*', '').strip()
    if w:
        all_words[w] += 1
        if t.transcriber == 'H':
            h_words[w] += 1
for row in per_pair:
    if row['robust_zero']:
        a, b = row['pair'].split('->')
        row['concat_H'] = h_words.get(a + b, 0)
        row['concat_all_tracks'] = all_words.get(a + b, 0)
        row['segmentation_suspect'] = row['concat_all_tracks'] > 0

log("\nper-pair (robust zeros first):")
for r in per_pair[:30]:
    log(f"  {r['pair']:<20} E_an={r['E_analytic']:5.2f} | N1 E={r['E_N1']:5.2f} P0={r['P0_N1']:.3f} | "
        f"N2 E={r['E_N2']:5.2f} P0={r['P0_N2']:.3f} | N4 E={r['E_N4']:5.2f} P0={r['P0_N4']:.3f} | "
        f"rev={r['reverse_real']}/{r['reverse_E_N1']:.1f} robust={r['robust_zero']} joint={r['robust_zero_incl_N3']}"
        + (f" concat={r.get('concat_all_tracks')}" if r['robust_zero'] else ''))

out = {
    'phase': 'PHASE_753', 'pre_registration_commit': '4f6373c',
    'data': {'lines': len(line_list), 'tokens': n_tok, 'common_tokens': K, 'real_common_bigrams': int(real.sum()),
             'analytic_candidates_E5': int(analytic_cand.sum()),
             'analytic_real_zeros': int((real[analytic_cand] == 0).sum())},
    'n2_fallback': dict(n2_fallback),
    'nulls': {name: {k: v for k, v in res.items() if k not in ('E', 'P0')}
              for name, res in results.items()},
    'post_hoc_N3_note': 'N3 was added after the v1 run; it does not enter the locked verdict. It is degenerate (see diagnostics).',
    'post_hoc_N4_note': 'N4 was added after N3 proved degenerate; it does not enter the locked verdict.',
    'null_diagnostics': diagnostics,
    'script_version': 'v2 (per-pair tracking fixed; N3 added)',
    'verdict': verdict,
    'per_pair': per_pair,
}
json.dump(out, open(OUT / 'c957_three_null_screen.json', 'w', encoding='utf-8'), indent=1)
log(f"written {OUT / 'c957_three_null_screen.json'}")

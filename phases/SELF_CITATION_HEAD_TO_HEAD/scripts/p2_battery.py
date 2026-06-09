"""Phase 1b: score the fitted self-citation generator against the locked kill battery.

Kills (PRE_REGISTRATION Phase-0 re-lock):
  K1' directional token-level forbidden bigrams (9 ordered pairs, O/E; + identity-free census)
  K2  production-process: adjacent-vs-nonadjacent line copy-explainability gap
  K4  period-2 e-depth: signed lag1 & lag2 (Section B, within-line)
  K3  post-trigger CHSH rate (Tier-B, expected floor)
Controls (P6): M2 49-class Markov baseline, within-folio scramble.
Criterion (P3): B reproduced on a statistic iff inside generator-ensemble central 95%.
"""
import json, sys
from collections import OrderedDict, Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'results'
N_GEN, N_CTRL = 200, 60


def pr(*a):
    sys.stdout.buffer.write((' '.join(str(x) for x in a) + '\n').encode('ascii', 'replace'))
    sys.stdout.flush()


# ---------------- corpus ----------------
tx = Transcript()
folio_lines = OrderedDict()
folio_section = {}
for t in tx.currier_b():
    if t.is_label:
        continue
    w = t.word.strip()
    if not w or '*' in w:
        continue
    folio_lines.setdefault(t.folio, OrderedDict()).setdefault(t.line, []).append(w)
    folio_section[t.folio] = t.section
folio_lines = {f: list(ls.values()) for f, ls in folio_lines.items()}
ALPHA = sorted({c for ls in folio_lines.values() for ln in ls for w in ln for c in w})

PAIRS = [('chedy', 'aiin'), ('shedy', 'aiin'), ('qokeedy', 'ol'), ('chedy', 'ar'),
         ('ol', 'qokain'), ('ol', 'qokedy'), ('qokeedy', 'aiin'),
         ('chey', 'chedy'), ('chey', 'shedy')]
TRIGGERS = {'chedy', 'shedy', 'qokeedy', 'chey', 'ol'}

morph = Morphology()
_ED = {}
def edepth(w):
    if w not in _ED:
        try:
            _ED[w] = morph.atomize(w).e_depth
        except Exception:
            _ED[w] = 0
    return _ED[w]


_NLD = {}
def nld(a, b):
    if a == b:
        return 0.0
    k = (a, b) if a < b else (b, a)
    v = _NLD.get(k)
    if v is None:
        la, lb = len(a), len(b)
        prev = list(range(lb + 1))
        for i in range(1, la + 1):
            cur = [i] + [0] * lb
            ca = a[i - 1]
            for j in range(1, lb + 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != b[j - 1]))
            prev = cur
        v = prev[lb] / max(la, lb)
        _NLD[k] = v
    return v


# ---------------- battery statistics ----------------
def k1_stats(flines, rng):
    """(forward O/E, reverse O/E, joint forward E, census count) for the 9 pairs."""
    obs = Counter()
    for ls in flines.values():
        for ln in ls:
            for a, b in zip(ln, ln[1:]):
                obs[(a, b)] += 1
    # analytic E under within-line shuffle, only over types present per line
    need = set(PAIRS) | {(b, a) for a, b in PAIRS}
    E = defaultdict(float)
    cnt_global = Counter(w for ls in flines.values() for ln in ls for w in ln)
    top = set(w for w, _ in cnt_global.most_common(100))
    Ecen = defaultdict(float)
    for ls in flines.values():
        for ln in ls:
            n = len(ln)
            if n < 2:
                continue
            c = Counter(ln)
            keys = list(c)
            for a in keys:
                for b in keys:
                    if a == b:
                        continue
                    e = c[a] * c[b] / n
                    if (a, b) in need:
                        E[(a, b)] += e
                    if a in top and b in top:
                        Ecen[(a, b)] += e
    fE = sum(E[p] for p in PAIRS)
    fO = sum(obs[p] for p in PAIRS)
    rE = sum(E[(b, a)] for a, b in PAIRS)
    rO = sum(obs[(b, a)] for a, b in PAIRS)
    census = sum(1 for (a, b), e in Ecen.items()
                 if e >= 5 and obs[(a, b)] == 0 and obs[(b, a)] >= 1)
    return (fO / fE if fE else np.nan, rO / rE if rE else np.nan, fE, census)


def k2_stat(flines, rng):
    """mean copy-explainability gap: adjacent minus non-adjacent (negative = copy signature)."""
    adj, non = [], []
    for ls in flines.values():
        L = len(ls)
        if L < 5:
            continue
        for i in range(L - 1):
            adj.append(_explain(ls[i + 1], ls[i]))
        for _ in range(L - 1):
            i = int(rng.integers(0, L - 3))
            j = int(rng.integers(i + 3, L))
            non.append(_explain(ls[j], ls[i]))
    return float(np.mean(adj) - np.mean(non))


def _explain(target, source):
    if not target or not source:
        return 1.0
    src = list(set(source))
    return float(np.mean([min(nld(w, v) for v in src) for w in target]))


def k4_stats(flines):
    """pooled within-line e-depth autocorr lag1 & lag2, Section-B folios only."""
    x1a, x1b, x2a, x2b = [], [], [], []
    for f, ls in flines.items():
        if folio_section.get(f) != 'B':
            continue
        for ln in ls:
            e = [edepth(w) for w in ln]
            for i in range(len(e) - 1):
                x1a.append(e[i]); x1b.append(e[i + 1])
            for i in range(len(e) - 2):
                x2a.append(e[i]); x2b.append(e[i + 2])
    def r(u, v):
        u, v = np.array(u, float), np.array(v, float)
        return float(np.corrcoef(u, v)[0, 1]) if u.std() > 0 and v.std() > 0 else 0.0
    return r(x1a, x1b), r(x2a, x2b)


def k3_stat(flines):
    """P(next ch/sh | cur in TRIGGERS) - P(next ch/sh | cur freq-matched non-trigger)."""
    cnt = Counter(w for ls in flines.values() for ln in ls for w in ln)
    trig_f = {w: cnt[w] for w in TRIGGERS if cnt[w] > 0}
    ctrl = set()
    ranked = [w for w, _ in cnt.most_common()]
    for w in trig_f:
        i = ranked.index(w)
        for c in ranked[max(0, i - 4): i + 5]:
            if c not in TRIGGERS:
                ctrl.add(c); break
    def rate(S):
        hit = tot = 0
        for ls in flines.values():
            for ln in ls:
                for a, b in zip(ln, ln[1:]):
                    if a in S:
                        tot += 1
                        hit += b.startswith('ch') or b.startswith('sh')
        return hit / tot if tot else np.nan
    return float(rate(TRIGGERS) - rate(ctrl))


def battery(flines, rng):
    f_oe, r_oe, fE, census = k1_stats(flines, rng)
    l1, l2 = k4_stats(flines)
    return dict(k1_fwd_OE=f_oe, k1_rev_OE=r_oe, k1_fwdE=fE, k1_census=census,
                k2_gap=k2_stat(flines, rng), k4_lag1=l1, k4_lag2=l2,
                k3_chsh=k3_stat(flines))


# ---------------- generator (same as p1) ----------------
fitres = json.load(open(OUT / 'p1_generator_fit.json', encoding='utf-8'))
PARAMS = tuple(fitres['best_params'])
pr("fitted params:", tuple(round(x, 3) for x in PARAMS))


def _pos(n, p_edge, rng):
    if n <= 1:
        return 0
    if rng.random() < p_edge:
        return 0 if rng.random() < 0.5 else n - 1
    return int(rng.integers(0, n))


def mutate(w, p_sub, p_ins, p_del, p_edge, rng):
    r = rng.random()
    if r < p_sub or (len(w) <= 1 and r >= p_sub + p_ins):
        i = _pos(len(w), p_edge, rng)
        return w[:i] + ALPHA[int(rng.integers(0, len(ALPHA)))] + w[i + 1:]
    if r < p_sub + p_ins:
        i = _pos(len(w) + 1, p_edge, rng)
        return w[:i] + ALPHA[int(rng.integers(0, len(ALPHA)))] + w[i:]
    i = _pos(len(w), p_edge, rng)
    return w[:i] + w[i + 1:] if len(w) > 1 else w


def generate(params, rng):
    q, w_above, p_exact, p_sub, p_ins, p_second, p_edge, p_far = params
    p_del = max(0.0, 1.0 - p_sub - p_ins)
    out = {}
    for f, lines in folio_lines.items():
        gen_lines = [list(lines[0])]
        stream = list(lines[0])
        for li in range(1, len(lines)):
            above = gen_lines[li - 1]
            cur = []
            for _ in range(len(lines[li])):
                r = rng.random()
                if above and r < w_above:
                    src = above[int(rng.integers(0, len(above)))]
                elif r < w_above + p_far:
                    src = stream[int(rng.integers(0, len(stream)))]
                else:
                    d = max(1, int(rng.geometric(1.0 - q)))
                    src = stream[-min(d, len(stream))]
                w = src
                if rng.random() >= p_exact:
                    w = mutate(w, p_sub, p_ins, p_del, p_edge, rng)
                    if rng.random() < p_second:
                        w = mutate(w, p_sub, p_ins, p_del, p_edge, rng)
                cur.append(w)
                stream.append(w)
            gen_lines.append(cur)
        out[f] = gen_lines
    return out


# ---------------- M2 control (49-class Markov + class-conditional emission) ----------------
ctm = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
                     encoding='utf-8'))
tok2class = {t: int(c) for t, c in ctm['token_to_class'].items()}
chains = []          # per line: list of (class, token) classified subsequence
for f, ls in folio_lines.items():
    for ln in ls:
        ch = [(tok2class[w], w) for w in ln if w in tok2class]
        if len(ch) >= 2:
            chains.append((f, ch))
trans = defaultdict(Counter)
starts = Counter()
emis = defaultdict(Counter)
for f, ch in chains:
    starts[ch[0][0]] += 1
    for (a, _), (b, _) in zip(ch, ch[1:]):
        trans[a][b] += 1
    for c, w in ch:
        emis[c][w] += 1
def _sampler(counter):
    ks = list(counter); ps = np.array([counter[k] for k in ks], float); ps /= ps.sum()
    return ks, ps
START_K, START_P = _sampler(starts)
TRANS = {a: _sampler(c) for a, c in trans.items()}
EMIS = {c: _sampler(cc) for c, cc in emis.items()}


def generate_m2(rng):
    out = defaultdict(list)
    for f, ch in chains:
        n = len(ch)
        c = START_K[int(rng.choice(len(START_K), p=START_P))]
        line = [EMIS[c][0][int(rng.choice(len(EMIS[c][0]), p=EMIS[c][1]))]]
        for _ in range(n - 1):
            ks, ps = TRANS.get(c, (START_K, START_P))
            c = ks[int(rng.choice(len(ks), p=ps))]
            line.append(EMIS[c][0][int(rng.choice(len(EMIS[c][0]), p=EMIS[c][1]))])
        out[f].append(line)
    return dict(out)


def generate_scramble(rng):
    out = {}
    for f, ls in folio_lines.items():
        toks = [w for ln in ls for w in ln]
        rng.shuffle(toks)
        it = iter(toks)
        out[f] = [[next(it) for _ in ln] for ln in ls]
    return out


# ---------------- run ----------------
pr("\nB battery...")
rngB = np.random.default_rng(0)
B = battery(folio_lines, rngB)
pr("  B:", json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in B.items()}))

ens = defaultdict(list)
for i in range(N_GEN):
    rng = np.random.default_rng(10_000 + i)
    g = generate(PARAMS, rng)
    s = battery(g, rng)
    for k, v in s.items():
        ens[k].append(v)
    if (i + 1) % 50 == 0:
        pr(f"  generator ensemble {i+1}/{N_GEN}")

m2 = defaultdict(list)
for i in range(N_CTRL):
    rng = np.random.default_rng(50_000 + i)
    s = battery(generate_m2(rng), rng)
    for k, v in s.items():
        m2[k].append(v)
scr = defaultdict(list)
for i in range(N_CTRL):
    rng = np.random.default_rng(90_000 + i)
    s = battery(generate_scramble(rng), rng)
    for k, v in s.items():
        scr[k].append(v)

pr("\n=== HEAD-TO-HEAD RESULTS (B vs fitted self-citation ensemble; M2 + scramble controls) ===")
pr(f"{'stat':>10} {'B':>9} | {'gen mean':>9} {'gen 2.5%':>9} {'gen 97.5%':>9} {'B pctl':>7} {'repro?':>7} | {'M2':>8} {'scramble':>8}")
verdict = {}
for k in ('k1_fwd_OE', 'k1_rev_OE', 'k1_fwdE', 'k1_census', 'k2_gap', 'k4_lag1', 'k4_lag2', 'k3_chsh'):
    e = np.array(ens[k], float)
    lo, hi = np.percentile(e, [2.5, 97.5])
    pct = float((e <= B[k]).mean())
    ok = lo <= B[k] <= hi
    verdict[k] = dict(B=B[k], gen_mean=float(e.mean()), lo=float(lo), hi=float(hi),
                      pctl=pct, reproduced=bool(ok),
                      m2=float(np.mean(m2[k])), scramble=float(np.mean(scr[k])))
    pr(f"{k:>10} {B[k]:>9.3f} | {e.mean():>9.3f} {lo:>9.3f} {hi:>9.3f} {pct:>7.2f} "
       f"{'YES' if ok else 'NO':>7} | {np.mean(m2[k]):>8.3f} {np.mean(scr[k]):>8.3f}")

json.dump(dict(B=B, generator={k: list(map(float, v)) for k, v in ens.items()},
               m2_mean={k: float(np.mean(v)) for k, v in m2.items()},
               scramble_mean={k: float(np.mean(v)) for k, v in scr.items()},
               verdict=verdict, params=list(PARAMS)),
          open(OUT / 'p2_battery.json', 'w'), indent=1)
pr(f"\nresults -> {OUT / 'p2_battery.json'}")

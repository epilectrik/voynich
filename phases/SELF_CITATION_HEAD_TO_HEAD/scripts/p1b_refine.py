"""Phase 1a refinement: add long-range copy mode (p_far: uniform-over-stream source =
frequency-proportional = Yule-Simon -> Zipf), targeted probes of the high-reuse corner,
and coordinate hill-climb. Kernel stays UNIFORM-over-glyphs (locked). 8 params (<=10 budget).
"""
import json, sys
from collections import OrderedDict, Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'results'


def pr(*a):
    sys.stdout.buffer.write((' '.join(str(x) for x in a) + '\n').encode('ascii', 'replace'))
    sys.stdout.flush()


tx = Transcript()
folio_lines = OrderedDict()
for t in tx.currier_b():
    if t.is_label:
        continue
    w = t.word.strip()
    if not w or '*' in w:
        continue
    folio_lines.setdefault(t.folio, OrderedDict()).setdefault(t.line, []).append(w)
folio_lines = {f: list(ls.values()) for f, ls in folio_lines.items()}
ALPHA = sorted({c for ls in folio_lines.values() for ln in ls for w in ln for c in w})


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
    """params: q, w_above, p_exact, p_sub, p_ins, p_second, p_edge, p_far"""
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
                    src = stream[int(rng.integers(0, len(stream)))]   # long-range: Yule-Simon
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


# ---- fit stats / loss (identical to p1) ----
def ed1_mean_neighbors(tlist, top=800):
    tset = set(tlist)
    masked = defaultdict(set)
    delsig = defaultdict(set)
    for w in tset:
        for i in range(len(w)):
            masked[(i, w[:i] + '*' + w[i + 1:])].add(w)
            delsig[w[:i] + w[i + 1:]].add(w)
    out = []
    for w in tlist[:top]:
        nb = set()
        for i in range(len(w)):
            nb |= masked[(i, w[:i] + '*' + w[i + 1:])]
            d = w[:i] + w[i + 1:]
            if d in tset:
                nb.add(d)
        nb |= delsig.get(w, set())
        nb.discard(w)
        out.append(len(nb))
    return float(np.mean(out))


def _ed1(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def fit_stats(flines):
    toks = [w for ls in flines.values() for ln in ls for w in ln]
    cnt = Counter(toks)
    chk = [2000, 5000, 10000, 15000, 20000]
    seen, growth, ci = set(), [], 0
    for i, w in enumerate(toks, 1):
        seen.add(w)
        if ci < len(chk) and i == chk[ci]:
            growth.append(len(seen)); ci += 1
    while len(growth) < len(chk):
        growth.append(len(seen))
    fr = np.array(sorted(cnt.values(), reverse=True)[:1000], float)
    zipf = float(np.polyfit(np.log(np.arange(1, len(fr) + 1)), np.log(fr), 1)[0])
    same = ed1 = pairs = 0
    for ls in flines.values():
        for ln in ls:
            for a, b in zip(ln, ln[1:]):
                pairs += 1
                if a == b:
                    same += 1
                elif _ed1(a, b):
                    ed1 += 1
    L = np.array([len(w) for w in toks], float)
    return dict(growth=growth, zipf=zipf, adj_same=same / pairs, adj_ed1=ed1 / pairs,
                len_mean=float(L.mean()), len_sd=float(L.std()),
                ed1_density=ed1_mean_neighbors([w for w, _ in cnt.most_common()]),
                n_types=len(cnt))


B_STATS = fit_stats(folio_lines)


def loss(s):
    g = np.array(s['growth'], float) / np.array(B_STATS['growth'], float) - 1
    return float(np.sum([np.mean(g ** 2),
        ((s['zipf'] - B_STATS['zipf']) / abs(B_STATS['zipf'])) ** 2,
        ((s['adj_same'] - B_STATS['adj_same']) / max(B_STATS['adj_same'], 1e-3)) ** 2,
        ((s['adj_ed1'] - B_STATS['adj_ed1']) / max(B_STATS['adj_ed1'], 1e-3)) ** 2,
        ((s['len_mean'] - B_STATS['len_mean']) / B_STATS['len_mean']) ** 2,
        ((s['len_sd'] - B_STATS['len_sd']) / B_STATS['len_sd']) ** 2,
        ((s['ed1_density'] - B_STATS['ed1_density']) / B_STATS['ed1_density']) ** 2,
        2.0 * ((s['n_types'] / B_STATS['n_types']) - 1) ** 2]))


def ev(p, reps=2):
    return float(np.mean([loss(fit_stats(generate(p, np.random.default_rng(7000 + r))))
                          for r in range(reps)]))


# targeted probes: high reuse, balanced ins/del, strong long-range copy
probes = []
for p_exact in (0.55, 0.7, 0.8):
    for p_far in (0.2, 0.45, 0.7):
        for p_ins in (0.12, 0.2):
            probes.append((0.92, 0.25, p_exact, 1 - 2 * p_ins - 0.0, 0, 0, 0, 0))
probes = []
for p_exact in (0.55, 0.7, 0.8):
    for p_far in (0.2, 0.45, 0.7):
        for p_ins in (0.12, 0.20):
            p_sub = 1.0 - 2 * p_ins            # p_del = p_ins (length-stable)
            probes.append((0.92, 0.25, p_exact, p_sub, p_ins, 0.15, 0.45, p_far))
# carry forward the p1 best (with p_far=0)
prev = json.load(open(OUT / 'p1_generator_fit.json', encoding='utf-8'))
probes.append(tuple(prev['best_params']) + (0.0,))

scored = sorted(((ev(p), p) for p in probes), key=lambda x: x[0])
pr("probe results (top 5):")
for L0, p in scored[:5]:
    pr(f"  loss {L0:8.3f}  params {tuple(round(x, 3) for x in p)}")

# coordinate hill-climb from best probe
best_loss, best = scored[0]
BOUNDS = [(0.3, 0.995), (0, 0.8), (0.2, 0.95), (0.1, 0.85), (0.02, 0.4),
          (0, 0.5), (0, 0.95), (0, 0.9)]
step = [0.08, 0.08, 0.08, 0.08, 0.05, 0.08, 0.1, 0.1]
improved = True
it = 0
while improved and it < 4:
    improved = False
    it += 1
    for d in range(8):
        for sgn in (+1, -1):
            cand = list(best)
            cand[d] = float(np.clip(cand[d] + sgn * step[d], *BOUNDS[d]))
            if cand[3] + cand[4] > 0.97 or cand[1] + cand[7] > 0.95:
                continue
            L0 = ev(tuple(cand))
            if L0 < best_loss - 1e-3:
                best_loss, best = L0, tuple(cand)
                improved = True
    pr(f"  hill-climb pass {it}: loss {best_loss:.3f}  params {tuple(round(x,3) for x in best)}")
    step = [s * 0.6 for s in step]

s_best = fit_stats(generate(best, np.random.default_rng(99)))
pr("\n=== REFINED BEST ===")
pr("params (q,w_above,p_exact,p_sub,p_ins,p_second,p_edge,p_far):",
   tuple(round(x, 3) for x in best), " loss", round(best_loss, 3))
for k in ('zipf', 'adj_same', 'adj_ed1', 'len_mean', 'len_sd', 'ed1_density', 'n_types'):
    bv, gv = B_STATS[k], s_best[k]
    pr(f"  {k:>12}  B {bv if isinstance(bv,int) else round(bv,4):>10}   gen {gv if isinstance(gv,int) else round(gv,4):>10}")
pr(f"  {'growth':>12}  B {B_STATS['growth']}  gen {s_best['growth']}")

json.dump(dict(best_params=list(best), best_loss=best_loss,
               B_stats=B_STATS, gen_stats=s_best, model='8-param with p_far (Yule-Simon)'),
          open(OUT / 'p1_generator_fit.json', 'w'), indent=1)
pr(f"\nfit -> {OUT / 'p1_generator_fit.json'}")

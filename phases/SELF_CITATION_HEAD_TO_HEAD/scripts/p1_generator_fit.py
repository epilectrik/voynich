"""Phase 1a: implement + fit the Timm-Schinner self-citation generator (PRE_REGISTRATION P1-P2).

Model (per lock):
  - per folio: seed = the folio's REAL first line (T&S take page openings as given);
    line layout (number of lines, tokens per line) = real; everything else generated.
  - each new token: pick a source token from already-written material on the page --
    with prob w_above uniformly from the line directly above, else geometric back over
    the written stream (P(d) ~ q^d); then with prob p_exact copy verbatim, else mutate:
    1 edit drawn from {substitute, insert, delete} with locked UNIFORM glyph kernel;
    with prob p_second a second uniform edit is applied.
  - free parameters (6): q, w_above, p_exact, p_sub, p_ins (p_del = 1-p_sub-p_ins), p_second.

FIT set (locked, P1): vocabulary growth curve, edit-distance-1 neighbor density,
adjacent-identical + adjacent-ed1 rates, Zipf slope, token-length mean/sd.
Kill statistics are NOT in the fit set.
"""
import json, math, sys
from collections import OrderedDict, Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'results'
OUT.mkdir(exist_ok=True)


def pr(*a):
    sys.stdout.buffer.write((' '.join(str(x) for x in a) + '\n').encode('ascii', 'replace'))
    sys.stdout.flush()


# ---------------- corpus ----------------
tx = Transcript()
folio_lines = OrderedDict()        # folio -> [ [tokens], [tokens], ... ] in order
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
ALL_B = [w for ls in folio_lines.values() for ln in ls for w in ln]
ALPHA = sorted({c for w in ALL_B for c in w})
pr(f"corpus: {len(ALL_B)} tokens, {len(set(ALL_B))} types, {len(folio_lines)} folios, "
   f"alphabet {len(ALPHA)} glyphs")


# ---------------- generator ----------------
def generate(params, rng):
    """Return synthetic folio_lines with same layout; seeds = real first lines."""
    q, w_above, p_exact, p_sub, p_ins, p_second, p_edge = params
    p_del = max(0.0, 1.0 - p_sub - p_ins)
    out = {}
    for f, lines in folio_lines.items():
        gen_lines = [list(lines[0])]                  # seed: real first line
        stream = list(lines[0])
        for li in range(1, len(lines)):
            n = len(lines[li])
            above = gen_lines[li - 1]
            cur = []
            for _ in range(n):
                # --- choose source ---
                if above and rng.random() < w_above:
                    src = above[int(rng.integers(0, len(above)))]
                else:
                    # geometric back over stream (d=1 -> last written token)
                    d = 1 + int(rng.geometric(1.0 - q)) - 1
                    d = min(d if d >= 1 else 1, len(stream))
                    src = stream[-d]
                # --- copy or mutate ---
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


def _pos(n, p_edge, rng):
    """edit position: with prob p_edge at a word edge (T&S prefix/suffix ops), else uniform."""
    if n <= 1:
        return 0
    if rng.random() < p_edge:
        return 0 if rng.random() < 0.5 else n - 1
    return int(rng.integers(0, n))


def mutate(w, p_sub, p_ins, p_del, p_edge, rng):
    r = rng.random()
    if r < p_sub or (len(w) <= 1 and r >= p_sub + p_ins):   # forbid deleting to empty
        i = _pos(len(w), p_edge, rng)
        c = ALPHA[int(rng.integers(0, len(ALPHA)))]
        return w[:i] + c + w[i + 1:]
    if r < p_sub + p_ins:
        i = _pos(len(w) + 1, p_edge, rng)
        c = ALPHA[int(rng.integers(0, len(ALPHA)))]
        return w[:i] + c + w[i:]
    i = _pos(len(w), p_edge, rng)
    return w[:i] + w[i + 1:] if len(w) > 1 else w


# ---------------- fit statistics ----------------
def ed1_mean_neighbors(types, top=800):
    """mean # of edit-distance-1 neighbors among `types`, for the `top` most frequent."""
    tlist = list(types)
    tset = set(tlist)
    # substitution: masked keys
    masked = defaultdict(set)
    delsig = defaultdict(set)
    for w in tset:
        for i in range(len(w)):
            masked[(i, w[:i] + '*' + w[i + 1:])].add(w)
            delsig[w[:i] + w[i + 1:]].add(w)
    cnt = {}
    for w in tlist[:top]:
        nb = set()
        for i in range(len(w)):
            nb |= masked[(i, w[:i] + '*' + w[i + 1:])]
            d = w[:i] + w[i + 1:]
            if d in tset:
                nb.add(d)
            nb |= delsig.get(w, set()) and set()      # placeholder, see below
        # insertions into w = words whose deletion gives w
        nb |= delsig.get(w, set())
        nb.discard(w)
        cnt[w] = len(nb)
    return float(np.mean(list(cnt.values())))


def fit_stats(flines):
    toks = [w for ls in flines.values() for ln in ls for w in ln]
    n = len(toks)
    cnt = Counter(toks)
    by_freq = [w for w, _ in cnt.most_common()]
    # vocab growth at checkpoints
    chk = [2000, 5000, 10000, 15000, 20000]
    seen, growth, ci = set(), [], 0
    for i, w in enumerate(toks, 1):
        seen.add(w)
        if ci < len(chk) and i == chk[ci]:
            growth.append(len(seen)); ci += 1
    while len(growth) < len(chk):
        growth.append(len(seen))
    # Zipf slope (top 1000)
    fr = np.array(sorted(cnt.values(), reverse=True)[:1000], float)
    rk = np.arange(1, len(fr) + 1, dtype=float)
    zipf = float(np.polyfit(np.log(rk), np.log(fr), 1)[0])
    # adjacent rates (within line)
    same = ed1 = pairs = 0
    for ls in flines.values():
        for ln in ls:
            for a, b in zip(ln, ln[1:]):
                pairs += 1
                if a == b:
                    same += 1
                elif _ed1(a, b):
                    ed1 += 1
    # token length
    L = np.array([len(w) for w in toks], float)
    return dict(growth=growth, zipf=zipf,
                adj_same=same / pairs, adj_ed1=ed1 / pairs,
                len_mean=float(L.mean()), len_sd=float(L.std()),
                ed1_density=ed1_mean_neighbors(by_freq),
                n_types=len(cnt))


def _ed1(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or a == b:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    # a shorter by 1: check deletion
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


B_STATS = fit_stats(folio_lines)
pr("B fit-stats:", json.dumps({k: (v if not isinstance(v, float) else round(v, 4))
                               for k, v in B_STATS.items()}))


def loss(s):
    g = np.array(s['growth'], float) / np.array(B_STATS['growth'], float) - 1
    terms = [float(np.mean(g ** 2)),
             ((s['zipf'] - B_STATS['zipf']) / abs(B_STATS['zipf'])) ** 2,
             ((s['adj_same'] - B_STATS['adj_same']) / max(B_STATS['adj_same'], 1e-3)) ** 2,
             ((s['adj_ed1'] - B_STATS['adj_ed1']) / max(B_STATS['adj_ed1'], 1e-3)) ** 2,
             ((s['len_mean'] - B_STATS['len_mean']) / B_STATS['len_mean']) ** 2,
             ((s['len_sd'] - B_STATS['len_sd']) / B_STATS['len_sd']) ** 2,
             ((s['ed1_density'] - B_STATS['ed1_density']) / B_STATS['ed1_density']) ** 2,
             2.0 * ((s['n_types'] / B_STATS['n_types']) - 1) ** 2]
    return float(np.sum(terms))


# ---------------- random search then refine ----------------
rng0 = np.random.default_rng(123)
def draw():
    return (float(rng0.uniform(0.3, 0.995)),   # q (geometric locality)
            float(rng0.uniform(0.0, 0.8)),     # w_above
            float(rng0.uniform(0.3, 0.95)),    # p_exact (heavy verbatim reuse allowed)
            float(rng0.uniform(0.1, 0.8)),     # p_sub
            float(rng0.uniform(0.02, 0.4)),    # p_ins (p_del = 1-p_sub-p_ins, clipped)
            float(rng0.uniform(0.0, 0.4)),     # p_second
            float(rng0.uniform(0.0, 0.9)))     # p_edge (T&S edge-op bias; glyph kernel stays uniform)

N_SEARCH = 300
results = []
for it in range(N_SEARCH):
    p = draw()
    if p[3] + p[4] > 0.95:
        continue
    g = generate(p, np.random.default_rng(1000 + it))
    s = fit_stats(g)
    results.append((loss(s), p, s))
    if (it + 1) % 30 == 0:
        results.sort(key=lambda x: x[0])
        pr(f"  search {it+1}/{N_SEARCH}  best loss {results[0][0]:.4f}  params {tuple(round(x,3) for x in results[0][1])}")

results.sort(key=lambda x: x[0])
# refine top-3 with 3 reps each (average loss over seeds)
refined = []
for L0, p, _ in results[:5]:
    ls = []
    for r in range(3):
        g = generate(p, np.random.default_rng(5000 + r))
        ls.append(loss(fit_stats(g)))
    refined.append((float(np.mean(ls)), p))
refined.sort(key=lambda x: x[0])
best_loss, best = refined[0]
g = generate(best, np.random.default_rng(99))
s_best = fit_stats(g)

pr("\n=== BEST FIT ===")
pr("params (q, w_above, p_exact, p_sub, p_ins, p_second, p_edge):",
   tuple(round(x, 3) for x in best), " mean loss", round(best_loss, 4))
pr(f"{'stat':>12} {'B':>10} {'generator':>10}")
for k in ('zipf', 'adj_same', 'adj_ed1', 'len_mean', 'len_sd', 'ed1_density', 'n_types'):
    pr(f"{k:>12} {B_STATS[k]:>10.4f} {s_best[k]:>10.4f}" if isinstance(B_STATS[k], float)
       else f"{k:>12} {B_STATS[k]:>10} {s_best[k]:>10}")
pr(f"{'growth':>12} {B_STATS['growth']} vs {s_best['growth']}")

json.dump(dict(best_params=list(best), best_loss=best_loss,
               B_stats={k: v for k, v in B_STATS.items()},
               gen_stats={k: v for k, v in s_best.items()},
               n_search=N_SEARCH),
          open(OUT / 'p1_generator_fit.json', 'w'), indent=1)
pr(f"\nfit -> {OUT / 'p1_generator_fit.json'}")

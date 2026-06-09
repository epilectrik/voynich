"""P4a verification: strict word-adjacency for (a) the C783 class-level pairs and
(b) the C957 token-level forbidden bigrams + their reverse directions.

Rules out the chain-adjacency artifact (classified-token chains skip unclassified words)
before concluding anything about the class-level O/E ~= 1 result.
Null: within-line shuffle of the FULL line (all tokens), strict adjacency, 300 perms.
"""
import json, sys
from collections import defaultdict, OrderedDict, Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

rng = np.random.default_rng(7)
OUT = Path(__file__).resolve().parents[1] / 'results'


def pr(*a):
    sys.stdout.buffer.write((' '.join(str(x) for x in a) + '\n').encode('ascii', 'replace'))


ctm = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
                     encoding='utf-8'))
tok2class = {t: int(c) for t, c in ctm['token_to_class'].items()}

tx = Transcript()
lines = OrderedDict()
for t in tx.currier_b():
    if t.is_label:
        continue
    w = t.word.strip()
    if not w or '*' in w:
        continue
    lines.setdefault((t.folio, t.line), []).append(w)
seqs = [ws for ws in lines.values() if len(ws) > 1]

CLASS_PAIRS = [(12, 23), (12, 9), (17, 23), (17, 9), (10, 23), (10, 9), (11, 23), (11, 9),
               (10, 12), (10, 17), (11, 12), (11, 17),
               (32, 12), (32, 17), (31, 12), (31, 17), (23, 9)]
TOKEN_PAIRS = [('chedy', 'aiin'), ('shedy', 'aiin'), ('qokeedy', 'ol'), ('chedy', 'ar'),
               ('ol', 'qokain'), ('ol', 'qokedy'), ('qokeedy', 'aiin'),
               ('chey', 'chedy'), ('chey', 'shedy')]


def count_strict(seqs):
    ccnt = Counter()   # (classA, classB) strict word-adjacent
    tcnt = Counter()   # (wordA, wordB) strict word-adjacent
    for ws in seqs:
        for a, b in zip(ws, ws[1:]):
            tcnt[(a, b)] += 1
            ca, cb = tok2class.get(a), tok2class.get(b)
            if ca is not None and cb is not None:
                ccnt[(ca, cb)] += 1
    return ccnt, tcnt


obs_c, obs_t = count_strict(seqs)

want_c = set(CLASS_PAIRS) | {(b, a) for a, b in CLASS_PAIRS}
want_t = set(TOKEN_PAIRS) | {(b, a) for a, b in TOKEN_PAIRS}
null_c = defaultdict(list)
null_t = defaultdict(list)
for it in range(300):
    sh = []
    for ws in seqs:
        s = list(ws)
        rng.shuffle(s)
        sh.append(s)
    cc, tt = count_strict(sh)
    for k in want_c:
        null_c[k].append(cc.get(k, 0))
    for k in want_t:
        null_t[k].append(tt.get(k, 0))

pr("=== STRICT word-adjacency, CLASS level (C783 pairs) ===")
pr(f"{'pair':>10} {'obs_fwd':>7} {'exp_fwd':>8} {'obs_bwd':>7} {'exp_bwd':>8}  note")
agg_of = agg_ef = agg_ob = agg_eb = 0.0
n_live = 0
rows_c = []
for (A, B) in CLASS_PAIRS:
    ef = float(np.mean(null_c[(A, B)]))
    eb = float(np.mean(null_c[(B, A)]))
    of, ob = obs_c.get((A, B), 0), obs_c.get((B, A), 0)
    live = max(ef, eb) >= 5
    n_live += live
    if live:
        agg_of += of; agg_ef += ef; agg_ob += ob; agg_eb += eb
    rows_c.append(dict(pair=[A, B], obs_fwd=of, exp_fwd=round(ef, 2),
                       obs_bwd=ob, exp_bwd=round(eb, 2), live=bool(live)))
    pr(f"  {A:>3}->{B:<3} {of:>7} {ef:>8.2f} {ob:>7} {eb:>8.2f}  {'LIVE' if live else 'sparse'}")
pr(f"\nN_live(strict) = {n_live}/17")
if agg_ef:
    pr(f"AGGREGATE over live pairs: forbidden O/E = {agg_of:.0f}/{agg_ef:.1f} = "
       f"{agg_of/agg_ef:.3f}   reciprocal O/E = {agg_ob:.0f}/{agg_eb:.1f} = {agg_ob/agg_eb:.3f}")

pr("\n=== STRICT word-adjacency, TOKEN level (C957 forbidden bigrams + reverses) ===")
pr(f"{'bigram':>18} {'obs':>4} {'exp':>7} {'z':>6}   {'REVERSE obs':>11} {'exp':>7}")
rows_t = []
for (a, b) in TOKEN_PAIRS:
    ef = float(np.mean(null_t[(a, b)])); sf = float(np.std(null_t[(a, b)])) or 1e-9
    eb = float(np.mean(null_t[(b, a)]))
    of, ob = obs_t.get((a, b), 0), obs_t.get((b, a), 0)
    z = (of - ef) / sf
    rows_t.append(dict(bigram=[a, b], obs=of, exp=round(ef, 2), z=round(z, 1),
                       rev_obs=ob, rev_exp=round(eb, 2)))
    pr(f"  {a:>8}->{b:<8} {of:>4} {ef:>7.2f} {z:>6.1f}   {ob:>11} {eb:>7.2f}")

json.dump(dict(class_level=dict(rows=rows_c, n_live=n_live,
                                agg_forbidden_OE=round(agg_of/agg_ef, 3) if agg_ef else None,
                                agg_reciprocal_OE=round(agg_ob/agg_eb, 3) if agg_eb else None),
               token_level=rows_t),
          open(OUT / 'p0b_strict_adjacency.json', 'w'), indent=1)
pr(f"\nresults -> {OUT / 'p0b_strict_adjacency.json'}")

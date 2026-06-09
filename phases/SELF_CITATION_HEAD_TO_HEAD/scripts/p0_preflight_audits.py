"""Phase 0 pre-flight audits for the self-citation head-to-head (PRE_REGISTRATION.md P4).

P4a: C783 denominator audit -- max expected adjacent count per forbidden pair under a
     frequency-preserving within-line class shuffle. Pair live iff max-exp >= 5.
     N_live <= 4 => K1 dead as standalone kill.
P4b: C458 frequency-matched CV audit -- folio-level CV of hazard vs recovery vocabulary,
     each compared against random token-sets matched on per-type corpus frequency.
     K5 live iff |CV_haz - CV_rec| >= 0.40 survives frequency matching.
"""
import json, sys
from collections import defaultdict, OrderedDict, Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript  # noqa: E402

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parents[1] / 'results'
OUT.mkdir(exist_ok=True)


def pr(*a):
    sys.stdout.buffer.write((' '.join(str(x) for x in a) + '\n').encode('ascii', 'replace'))


# --- corpus: per-line class chains (H-track B, no labels, no uncertain) ---
ctm = json.load(open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json',
                     encoding='utf-8'))
tok2class = {t: int(c) for t, c in ctm['token_to_class'].items()}

tx = Transcript()
lines = OrderedDict()          # (folio,line) -> [class ids, classified tokens only]
folio_tokens = defaultdict(int)   # folio -> total B tokens (classified + not)
folio_classcnt = defaultdict(Counter)  # folio -> Counter(token word) classified only
type_freq = Counter()          # classified token type -> corpus count
n_tot = n_classified = 0
for t in tx.currier_b():
    if t.is_label:
        continue
    w = t.word.strip()
    if not w or '*' in w:
        continue
    n_tot += 1
    folio_tokens[t.folio] += 1
    c = tok2class.get(w)
    if c is None:
        continue
    n_classified += 1
    lines.setdefault((t.folio, t.line), []).append(c)
    folio_classcnt[t.folio][w] += 1
    type_freq[w] += 1
pr(f"corpus: {n_tot} B tokens, {n_classified} classified ({n_classified/n_tot*100:.1f}%), "
   f"{len(lines)} lines, {len(folio_tokens)} folios")

# =====================================================================================
# P4a -- C783 denominator audit
# =====================================================================================
PAIRS = [(12, 23), (12, 9), (17, 23), (17, 9), (10, 23), (10, 9), (11, 23), (11, 9),
         (10, 12), (10, 17), (11, 12), (11, 17),
         (32, 12), (32, 17), (31, 12), (31, 17),
         (23, 9)]

# observed adjacency on the classified chain per line; analytic expectation under
# within-line shuffle: E[ordered adjacent (A,B)] = c_A * c_B / n  (A != B)
obs = Counter()
exp = defaultdict(float)
for seq in lines.values():
    n = len(seq)
    if n < 2:
        continue
    for a, b in zip(seq, seq[1:]):
        obs[(a, b)] += 1
    cnt = Counter(seq)
    for (A, B) in set(PAIRS) | {(b, a) for a, b in PAIRS}:
        if cnt[A] and cnt[B]:
            exp[(A, B)] += cnt[A] * cnt[B] / n

# permutation verification of the analytic expectation (200 shuffles)
perm = defaultdict(list)
seqs = [s for s in lines.values() if len(s) > 1]
for _ in range(200):
    tot = Counter()
    for s in seqs:
        sh = list(s)
        rng.shuffle(sh)
        for a, b in zip(sh, sh[1:]):
            if (a, b) in exp:
                tot[(a, b)] += 1
    for k in exp:
        perm[k].append(tot[k])

pr("\n=== P4a: C783 DENOMINATOR AUDIT (live iff max expected >= 5) ===")
pr(f"{'pair':>10} {'obs_fwd':>7} {'obs_bwd':>7} {'exp_fwd':>8} {'exp_bwd':>8} "
   f"{'perm_fwd':>8} {'maxexp':>7}  status")
n_live = 0
p4a = []
for (A, B) in PAIRS:
    ef, eb = exp[(A, B)], exp[(B, A)]
    pf = float(np.mean(perm[(A, B)])) if perm[(A, B)] else 0.0
    mx = max(ef, eb)
    live = mx >= 5
    n_live += live
    p4a.append(dict(pair=[A, B], obs_fwd=obs[(A, B)], obs_bwd=obs[(B, A)],
                    exp_fwd=round(ef, 2), exp_bwd=round(eb, 2), max_exp=round(mx, 2),
                    live=bool(live)))
    pr(f"  {A:>3}->{B:<3} {obs[(A,B)]:>7} {obs[(B,A)]:>7} {ef:>8.2f} {eb:>8.2f} "
       f"{pf:>8.2f} {mx:>7.2f}  {'LIVE' if live else 'sparse'}")
pr(f"\nN_live = {n_live} / 17   ->  K1 {'LIVE (stake the salvage statistic)' if n_live > 4 else 'DEAD as standalone kill (pre-registered: N_live <= 4)'}")

# salvage statistic over live pairs: aggregate O/E forbidden vs reciprocal
live_pairs = [(A, B) for (A, B) in PAIRS if max(exp[(A, B)], exp[(B, A)]) >= 5]
salvage = None
if live_pairs:
    of = sum(obs[(A, B)] for A, B in live_pairs)
    ef = sum(exp[(A, B)] for A, B in live_pairs)
    ob = sum(obs[(B, A)] for A, B in live_pairs)
    eb = sum(exp[(B, A)] for A, B in live_pairs)
    salvage = dict(n_live_pairs=len(live_pairs),
                   forbidden_OE=round(of / ef, 3) if ef else None,
                   reciprocal_OE=round(ob / eb, 3) if eb else None,
                   forbidden_obs=of, forbidden_exp=round(ef, 1),
                   reciprocal_obs=ob, reciprocal_exp=round(eb, 1))
    pr(f"\nSALVAGE (live pairs only): forbidden-direction O/E = {of}/{ef:.1f} = {of/ef:.3f}"
       f"   reciprocal O/E = {ob}/{eb:.1f} = {ob/eb:.3f}")
    pr("  directional asymmetry = forbidden suppressed AND reciprocal at-null")

# =====================================================================================
# P4b -- C458 frequency-matched CV audit
# =====================================================================================
HAZ_CLASSES = {9, 10, 11, 12, 17, 23, 31, 32}   # C783 forbidden-pair participants
HAZ_ALT = {7, 8, 9, 11, 23, 30, 31, 33, 41}     # robustness: "9 hazard-involved" set
REC_CLASSES = {38, 40}                            # FL_SAFE escape (C586)

class_types = defaultdict(set)
for w, c in tok2class.items():
    if type_freq[w] > 0:
        class_types[c].add(w)


def set_types(classes):
    return sorted(set().union(*(class_types[c] for c in classes if c in class_types)))


def folio_cv(types, min_tok=50, as_count=False):
    """CV across folios of the set's density (or raw count)."""
    ts = set(types)
    vals = []
    for f, tot in folio_tokens.items():
        if tot < min_tok:
            continue
        c = sum(n for w, n in folio_classcnt[f].items() if w in ts)
        vals.append(c if as_count else c / tot)
    vals = np.array(vals, float)
    m = vals.mean()
    return (vals.std() / m if m > 0 else np.nan), m


def freq_matched_null(types, n_iter=500):
    """CV distribution of random type-sets matched per-type on corpus frequency."""
    all_types = sorted(type_freq)
    freqs = np.array([type_freq[t] for t in all_types], float)
    order = np.argsort(freqs)
    sorted_types = [all_types[i] for i in order]
    sorted_freqs = freqs[order]
    out = []
    for _ in range(n_iter):
        pick = set()
        for t in types:
            f0 = type_freq[t]
            i = int(np.searchsorted(sorted_freqs, f0))
            lo, hi = max(0, i - 25), min(len(sorted_types), i + 25)  # nearest-rank window
            for _try in range(60):
                cand = sorted_types[int(rng.integers(lo, hi))]
                if cand not in pick:
                    pick.add(cand)
                    break
        cv, _ = folio_cv(pick)
        out.append(cv)
    return np.array(out)


pr("\n=== P4b: C458 FREQUENCY-MATCHED CV AUDIT ===")
res_b = {}
for name, classes in [('hazard(C783-participants)', HAZ_CLASSES),
                      ('hazard(9-involved alt)', HAZ_ALT),
                      ('recovery(FL_SAFE 38/40)', REC_CLASSES)]:
    ts = set_types(classes)
    tokn = sum(type_freq[t] for t in ts)
    cv_d, mean_d = folio_cv(ts)
    cv_c, _ = folio_cv(ts, as_count=True)
    null = freq_matched_null(ts)
    pct = float((null <= cv_d).mean())
    res_b[name] = dict(n_types=len(ts), n_tokens=tokn, cv_density=round(float(cv_d), 3),
                       cv_rawcount=round(float(cv_c), 3),
                       matched_null_cv_mean=round(float(null.mean()), 3),
                       matched_null_cv_sd=round(float(null.std()), 3),
                       percentile_vs_null=round(pct, 3))
    pr(f"  {name:28s} types={len(ts):3d} tokens={tokn:6d}  CV(density)={cv_d:.3f}  "
       f"CV(rawcount)={cv_c:.3f}  freq-matched null CV={null.mean():.3f}+-{null.std():.3f}"
       f"  pctile={pct:.2f}")

cv_h = res_b['hazard(C783-participants)']['cv_density']
cv_r = res_b['recovery(FL_SAFE 38/40)']['cv_density']
nh = res_b['hazard(C783-participants)']
nr = res_b['recovery(FL_SAFE 38/40)']
raw_gap = abs(cv_h - cv_r)
# frequency-corrected gap: residual CVs (observed minus own frequency-matched expectation)
resid_h = cv_h - nh['matched_null_cv_mean']
resid_r = cv_r - nr['matched_null_cv_mean']
corr_gap = abs(resid_h - resid_r)
pr(f"\n  RAW density-CV gap |haz-rec| = {raw_gap:.3f}")
pr(f"  residual vs own freq-matched null: hazard {resid_h:+.3f}, recovery {resid_r:+.3f}")
pr(f"  FREQUENCY-CORRECTED gap = {corr_gap:.3f}")
verdict = ('LIVE' if corr_gap >= 0.40 else
           'INCONCLUSIVE' if corr_gap >= 0.25 else 'DEAD (frequency shadow)')
pr(f"  K5 verdict vs locked thresholds (>=0.40 live, 0.25-0.40 inconclusive): {verdict}")

json.dump(dict(p4a=dict(pairs=p4a, n_live=n_live,
                        k1_verdict=('LIVE' if n_live > 4 else 'DEAD'), salvage=salvage),
               p4b=dict(sets=res_b, raw_gap=round(raw_gap, 3),
                        residual_hazard=round(resid_h, 3),
                        residual_recovery=round(resid_r, 3),
                        frequency_corrected_gap=round(corr_gap, 3),
                        k5_verdict=verdict),
               corpus=dict(n_tokens=n_tot, n_classified=n_classified)),
          open(OUT / 'p0_preflight_audits.json', 'w'), indent=1)
pr(f"\nresults -> {OUT / 'p0_preflight_audits.json'}")

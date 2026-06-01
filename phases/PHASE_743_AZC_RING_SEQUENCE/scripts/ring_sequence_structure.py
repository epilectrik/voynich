"""PHASE 743 - Is an AZC ring a SEQUENCE or a SET?

The serialization audit (PHASE_742) proved the BLOCK order between rings is a transcription artifact.
But the order WITHIN a single continuous ring locus (@Cc) is genuine ANGULAR reading order (the scribe
wrote the ring around the circle; the transcriber recorded it in that order from the start-gap). So we can
ask, cleanly, whether AZC ring text has LOCAL SEQUENTIAL STRUCTURE.

TEST: for each long single-placement ring locus (>=12 tokens, ordered within-locus by line_initial index),
lag-1 agreement rate for a feature = mean over adjacent pairs of [feat_i == feat_{i+1}]. NULL = within-ring
shuffle (preserves the ring's exact multiset, destroys order) -- the lesson-compliant first control. Per-ring
z = (obs - null_mean)/null_std; Stouffer-combine across rings; count rings individually significant.
Features: PREFIX, MIDDLE, token-class (RI/PP/INFRA). Also a first-half-vs-second-half vocab DRIFT test.

structure beyond shuffle -> rings are language-like SEQUENCES; none -> rings are unordered LABEL-SETS.
"""
import sys, functools, json
from collections import defaultdict
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

OUT = Path('phases/PHASE_743_AZC_RING_SEQUENCE/results'); OUT.mkdir(parents=True, exist_ok=True)
tx = Transcript(); morph = Morphology()
try:
    ra = RecordAnalyzer()
except Exception:
    ra = None

# ---- build ring loci: (folio,line_number) single-placement, >=12 tokens, ordered by line_initial ----
loci = defaultdict(list)
for t in tx.azc(h_only=True):
    w = (t.word or '').strip()
    if not w or '*' in w: continue
    pl = t.placement
    if not pl: continue
    # position index within locus
    li = getattr(t, 'line_initial', None)
    loci[(t.folio, t.line, pl)].append((li, w))

rings = []
for (fol, ln, pl), toks in loci.items():
    if len(toks) < 12: continue
    # order by line_initial index when available, else keep file order
    try:
        toks_sorted = sorted(toks, key=lambda x: int(x[0]))
    except (TypeError, ValueError):
        toks_sorted = toks
    words = [w for _, w in toks_sorted]
    rings.append({'folio': fol, 'line': ln, 'placement': pl, 'words': words})
print(f"Ring loci (single-placement, >=12 tokens): {len(rings)}  "
      f"(sizes {min(len(r['words']) for r in rings)}-{max(len(r['words']) for r in rings)}, "
      f"total {sum(len(r['words']) for r in rings)} tokens)")

def feat_prefix(w): return morph.extract(w).prefix or '_'
def feat_middle(w): return morph.extract(w).middle or '_'
def feat_tclass(w):
    if ra is None: return '_'
    try: return ra.classify_token(w, morph.extract(w))
    except Exception:
        try: return ra.classify_token(w)
        except Exception: return '_'

def lag1_agreement(seq):
    if len(seq) < 2: return None
    return np.mean([seq[i] == seq[i + 1] for i in range(len(seq) - 1)])

def test_feature(name, fn, B=5000, seed=0):
    rng = np.random.default_rng(seed)
    zs = []; n_sig = 0; obs_tot = []; null_tot = []
    for r in rings:
        seq = [fn(w) for w in r['words']]
        obs = lag1_agreement(seq)
        if obs is None: continue
        perms = np.empty(B)
        arr = np.array(seq, dtype=object)
        for b in range(B):
            p = rng.permutation(arr)
            perms[b] = np.mean(p[:-1] == p[1:])
        mu, sd = perms.mean(), perms.std()
        z = (obs - mu) / sd if sd > 1e-9 else 0.0
        zs.append(z); obs_tot.append(obs); null_tot.append(mu)
        if obs > np.percentile(perms, 95): n_sig += 1
    zs = np.array(zs)
    stouffer = zs.sum() / np.sqrt(len(zs)) if len(zs) else 0.0
    print(f"  [{name:9s}] rings={len(zs)}  mean obs lag1-agree={np.mean(obs_tot):.3f} vs null {np.mean(null_tot):.3f}"
          f"  Stouffer Z={stouffer:+.2f}  rings sig(p<.05)={n_sig}/{len(zs)}")
    return {'feature': name, 'n_rings': len(zs), 'mean_obs': round(float(np.mean(obs_tot)), 4),
            'mean_null': round(float(np.mean(null_tot)), 4), 'stouffer_z': round(float(stouffer), 3),
            'n_rings_sig': int(n_sig)}

print("\nLAG-1 ADJACENCY STRUCTURE (obs vs within-ring shuffle):")
res = {'n_rings': len(rings), 'features': {}}
for nm, fn in [('prefix', feat_prefix), ('middle', feat_middle), ('tclass', feat_tclass)]:
    res['features'][nm] = test_feature(nm, fn)

# ---- DRIFT: first-half vs second-half vocab divergence vs shuffle ----
def jaccard(a, b):
    A, Bs = set(a), set(b); u = A | Bs
    return len(A & Bs) / len(u) if u else 1.0
rng = np.random.default_rng(1); drift_z = []
for r in rings:
    w = r['words']; h = len(w) // 2
    if h < 4: continue
    obs = jaccard(w[:h], w[h:])
    perms = []
    arr = np.array(w, dtype=object)
    for _ in range(2000):
        p = rng.permutation(arr); perms.append(jaccard(p[:h], p[h:]))
    perms = np.array(perms); sd = perms.std()
    if sd > 1e-9: drift_z.append((obs - perms.mean()) / sd)
drift_z = np.array(drift_z)
drift_stouffer = drift_z.sum() / np.sqrt(len(drift_z)) if len(drift_z) else 0.0
print(f"\nDRIFT (half-vs-half Jaccard vs shuffle): rings={len(drift_z)}  Stouffer Z={drift_stouffer:+.2f}  "
      f"(negative = early/late vocab MORE separated than chance = positional drift)")
res['drift'] = {'n_rings': len(drift_z), 'stouffer_z': round(float(drift_stouffer), 3)}

# verdict
maxabs = max(abs(res['features'][f]['stouffer_z']) for f in res['features'])
res['verdict'] = ('SEQUENCE: local adjacency structure beyond the multiset' if maxabs > 3
                  else ('SET: no within-ring order structure (rings are unordered label-bags)' if maxabs < 2
                        else 'AMBIGUOUS / weak'))
print(f"\nVERDICT: {res['verdict']}  (max |Stouffer Z| across features = {maxabs:.2f})")
(OUT / 'ring_sequence_structure.json').write_text(json.dumps(res, indent=2))
print(f"Saved {OUT / 'ring_sequence_structure.json'}")

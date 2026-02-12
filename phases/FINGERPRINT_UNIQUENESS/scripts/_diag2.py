import sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'C:/git/voynich')
from collections import defaultdict, Counter
from scripts.voynich import Transcript, Morphology
import numpy as np

print('Loading records...', flush=True)
t0 = time.time()

tx = Transcript()
morph = Morphology()
with open('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)
t2c = {t: int(c) for t, c in ctm['token_to_class'].items()}

records = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    cls = t2c.get(w)
    if cls is None:
        continue
    m = morph.extract(w)
    records[(token.folio, token.line)].append({
        'middle': m.middle if m.middle else '_NONE_',
    })
records = dict(records)
print(f'Loaded {len(records)} records in {time.time()-t0:.1f}s', flush=True)

# Test incompatibility computation
print('Computing incompatibility...', flush=True)
t0 = time.time()

record_middles = []
all_middles = set()
for rec in records.values():
    middles = set(t['middle'] for t in rec if t['middle'] != '_NONE_')
    if len(middles) >= 2:
        record_middles.append(middles)
        all_middles.update(middles)

mid_list = sorted(all_middles)
mid_idx = {m: i for i, m in enumerate(mid_list)}
n_mid = len(mid_list)
print(f'  {n_mid} unique MIDDLEs, {len(record_middles)} records with 2+ MIDDLEs', flush=True)

cooccur = set()
for middles in record_middles:
    idx_list = sorted(mid_idx[m] for m in middles)
    for a in range(len(idx_list)):
        for b in range(a + 1, len(idx_list)):
            cooccur.add((idx_list[a], idx_list[b]))

n_possible = n_mid * (n_mid - 1) // 2
n_compat = len(cooccur)
incomp = 1.0 - n_compat / n_possible
print(f'  Incompatibility: {incomp:.4f} ({n_compat}/{n_possible} compatible pairs)', flush=True)
print(f'  Time: {time.time()-t0:.2f}s', flush=True)

# Test token shuffle speed
print('Testing shuffle speed (10 iterations)...', flush=True)
t0 = time.time()
rng = np.random.default_rng(42)
all_tokens = []
record_keys = []
record_sizes = []
for key, rec in records.items():
    record_keys.append(key)
    record_sizes.append(len(rec))
    all_tokens.extend(rec)

for i in range(10):
    shuffled = list(all_tokens)
    rng.shuffle(shuffled)
    nr = {}
    idx = 0
    for key, size in zip(record_keys, record_sizes):
        nr[key] = shuffled[idx:idx + size]
        idx += size
    # Recompute incomp
    rm2 = []
    am2 = set()
    for rec in nr.values():
        mids = set(t['middle'] for t in rec if t['middle'] != '_NONE_')
        if len(mids) >= 2:
            rm2.append(mids)
            am2.update(mids)
    ml2 = sorted(am2)
    mi2 = {m: j for j, m in enumerate(ml2)}
    co2 = set()
    for mids in rm2:
        il = sorted(mi2[m] for m in mids)
        for a in range(len(il)):
            for b in range(a+1, len(il)):
                co2.add((il[a], il[b]))
    n_p2 = len(ml2) * (len(ml2)-1) // 2
    inc2 = 1.0 - len(co2) / n_p2 if n_p2 > 0 else 0

print(f'  10 shuffles + incomp in {time.time()-t0:.1f}s ({(time.time()-t0)/10:.2f}s each)', flush=True)
print(f'  Last shuffle incomp: {inc2:.4f}', flush=True)

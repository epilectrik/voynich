"""CONTROL for the class-layer 5-gram null result.

The class-layer 5-gram null gave real I=0.264 >> synth I=0.221 (z=+3.83) — C2023 survives.
But is that 5-gram structurally under-producing ANY token-adjacency MI (artifact), or is
it specific to the class projection?

DISCRIMINATING CONTROL: run the SAME 5-gram null at the MIDDLE layer.
C2023 found the MIDDLE layer at z=-0.39 under shuffle (NO excess sequential structure).
PREDICTION:
- If 5-gram-null MIDDLE layer ALSO shows real ~= synth (z near 0) -> the 5-gram does NOT
  generically deflate adjacency MI; the class-layer excess is real and class-specific. BULLETPROOF.
- If 5-gram-null MIDDLE layer shows real >> synth (z high) -> the 5-gram deflates all
  adjacency MI; the class-layer "survival" is an artifact. RESULT VOID.

Same corpus, same lines, same 5-gram. Only the projection changes (middle string instead of class id).
flush=True + JSON.
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

N_SHUFFLE = 30
N_SYNTH = 200
ORDER = 5
RESULTS = PROJECT_ROOT / 'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/middle_layer_control.json'


def entropy(counts):
    total = sum(counts.values())
    if total == 0: return 0.0
    h = 0.0
    for c in counts.values():
        if c:
            p = c / total; h -= p * math.log2(p)
    return h

def cond_entropy(joint, marg):
    total = sum(marg.values())
    if total == 0: return 0.0
    h = 0.0
    for x, n_x in marg.items():
        h += (n_x / total) * entropy(joint.get(x, {}))
    return h

def MI_from_lines(lines):
    hm = Counter(); joint = defaultdict(Counter); marg = Counter()
    for line in lines:
        clean = [c for c in line if c is not None]
        for c in clean: hm[c] += 1
        for a, b in zip(clean, clean[1:]):
            joint[a][b] += 1; marg[a] += 1
    return entropy(hm) - cond_entropy(joint, marg), sum(marg.values())

def shuffle_null(lines, n, seed=0):
    rng = random.Random(seed)
    seqs = [[c for c in line if c is not None] for line in lines]
    mis = []
    for _ in range(n):
        sl = []
        for s in seqs:
            ss = s[:]; rng.shuffle(ss); sl.append(ss)
        mi, _ = MI_from_lines(sl); mis.append(mi)
    mean = sum(mis)/len(mis)
    sd = (sum((x-mean)**2 for x in mis)/len(mis))**0.5 if len(mis) > 1 else 0.0
    return mean, sd

print('Loading Currier B (same filter as class-layer test)...', flush=True)
tx = Transcript(); morph = Morphology()
by_line = defaultdict(list)
for tok in tx.all(h_only=True):
    if not tok.word or tok.is_uncertain: continue
    if tok.language != 'B': continue
    if not (tok.placement and tok.placement.startswith('P')): continue
    by_line[(tok.folio, tok.line)].append(tok.word)

# Cache middles
mid_cache = {}
def get_mid(w):
    if w in mid_cache: return mid_cache[w]
    try:
        m = morph.extract(w)
        v = m.middle if (m.middle is not None and m.suffix is not None) else None
    except Exception:
        v = None
    mid_cache[w] = v
    return v

word_lines = []
for key in sorted(by_line.keys()):
    wl = [w for w in by_line[key] if get_mid(w) is not None]
    if wl: word_lines.append(wl)
n_tokens = sum(len(l) for l in word_lines)
print(f'  {len(word_lines)} lines, {n_tokens} tokens', flush=True)

# MIDDLE-layer real measurement
real_mid_lines = [[get_mid(w) for w in wl] for wl in word_lines]
real_mi, n_pairs = MI_from_lines(real_mid_lines)
sh_mean, sh_sd = shuffle_null(real_mid_lines, N_SHUFFLE)
z_shuffle = (real_mi - sh_mean) / sh_sd if sh_sd > 0 else float('nan')
print(f'\n=== MIDDLE-layer REAL ===', flush=True)
print(f'  Real I(middle;prev) = {real_mi:.4f} (n_pairs={n_pairs})', flush=True)
print(f'  Shuffle null = {sh_mean:.4f} +/- {sh_sd:.4f}  z={z_shuffle:+.2f}  (C2023 reported -0.39)', flush=True)

# 5-gram
def train(lines, order):
    c = defaultdict(Counter)
    for wl in lines:
        s = ' '.join(wl); p = '\x01'*(order-1)+s+'\x02'
        for i in range(order-1, len(p)): c[p[i-(order-1):i]][p[i]] += 1
    return c
def sample_line(counts, order, target, rng):
    out=[]; ctx='\x01'*(order-1); buf=[]; att=0
    while len(out)<target and att<target*60:
        att+=1; cand=counts.get(ctx)
        if not cand: ctx='\x01'*(order-1); continue
        ch=rng.choices(list(cand.keys()),weights=list(cand.values()),k=1)[0]
        if ch=='\x02':
            if buf: out.append(''.join(buf)); buf=[]
            ctx='\x01'*(order-1)
            if len(out)>=target: break
            continue
        if ch==' ':
            if buf: out.append(''.join(buf)); buf=[]
            ctx=(ctx+ch)[-(order-1):]; continue
        buf.append(ch); ctx=(ctx+ch)[-(order-1):]
    if buf and len(out)<target: out.append(''.join(buf))
    return out[:target]

counts = train(word_lines, ORDER)
print(f'\n=== MIDDLE-layer 5-gram null ({N_SYNTH} synth) ===', flush=True)
rng = random.Random(42)
synth_mis = []
for s in range(N_SYNTH):
    sl = [sample_line(counts, ORDER, len(wl), rng) for wl in word_lines]
    sml = [[get_mid(w) for w in wl] for wl in sl]
    mi, _ = MI_from_lines(sml); synth_mis.append(mi)
    if (s+1) % 50 == 0:
        print(f'  [{s+1}/{N_SYNTH}] synth I mean = {sum(synth_mis)/len(synth_mis):.4f}', flush=True)

synth_mean = sum(synth_mis)/len(synth_mis)
synth_sd = (sum((x-synth_mean)**2 for x in synth_mis)/len(synth_mis))**0.5
z_5gram = (real_mi - synth_mean)/synth_sd if synth_sd > 0 else float('nan')
p_emp = sum(1 for m in synth_mis if m >= real_mi)/len(synth_mis)

print(f'\n=== MIDDLE-layer CONTROL RESULT ===', flush=True)
print(f'  Real I(middle;prev) = {real_mi:.4f}', flush=True)
print(f'  Shuffle null        = {sh_mean:.4f} (z={z_shuffle:+.2f})', flush=True)
print(f'  5-gram synth I       = {synth_mean:.4f} +/- {synth_sd:.4f}', flush=True)
print(f'  z_5gram             = {z_5gram:+.2f}', flush=True)
print(f'  p_emp                = {p_emp:.4f}', flush=True)
print(f'\n=== INTERPRETATION ===', flush=True)
if z_5gram < 2.0:
    print(f'  MIDDLE layer shows NO 5-gram excess (z={z_5gram:+.2f}) — matches C2023 shuffle z=-0.39.', flush=True)
    print(f'  CONTROL PASSES: the 5-gram does NOT generically deflate adjacency MI.', flush=True)
    print(f'  The class-layer excess (z=+3.83) is real and class-projection-specific. BULLETPROOF.', flush=True)
else:
    print(f'  MIDDLE layer ALSO shows 5-gram excess (z={z_5gram:+.2f}) — the 5-gram deflates all', flush=True)
    print(f'  adjacency MI. The class-layer "survival" may be an artifact. RESULT IN QUESTION.', flush=True)

RESULTS.write_text(json.dumps({
    'real_mi': real_mi, 'n_pairs': n_pairs,
    'shuffle_mean': sh_mean, 'shuffle_sd': sh_sd, 'z_shuffle': z_shuffle,
    'synth_mean': synth_mean, 'synth_sd': synth_sd, 'z_5gram': z_5gram, 'p_emp': p_emp,
    'control_passes': bool(z_5gram < 2.0),
}, indent=2))
print(f'\nWritten to {RESULTS}', flush=True)

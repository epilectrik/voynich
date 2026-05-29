"""Required controls before registering the class-layer 5-gram null result.

Per expert adjudication:
CONTROL 1 (per-synth own-shuffle excess): the rigorous bias-cancelled metric. For each
  synth corpus, compute synth_I AND synth's OWN shuffle null; synth_excess = synth_I -
  synth_own_shuffle. Compare distribution of synth_excess to real_excess (real_I - real_shuffle).
  This cancels the MI estimator bias and the composition-fidelity gap.
CONTROL 2 (coverage / bridging): unmapped tokens are currently dropped, BRIDGING neighbors
  (clean=[c for c in line if c is not None]). Test a BREAK-BIGRAM variant (unmapped token
  breaks the adjacency) for both real and synth; confirm the excess holds. Report synth
  unmapped fraction.

VERDICT: real_excess > 95th percentile of per-synth excess distribution -> C2023's first-order
  class structure is NOT reproducible from local character statistics. CLEAN SURVIVAL.

flush=True + JSON.
"""
import json, math, random, sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

N_SYNTH = 100
N_SHUFFLE_PER = 12
ORDER = 5
RESULTS = PROJECT_ROOT / 'phases/PHASE_733_CLASS_LAYER_5GRAM_NULL/results/controls_v2.json'

def entropy(counts):
    t = sum(counts.values())
    if not t: return 0.0
    return -sum((c/t)*math.log2(c/t) for c in counts.values() if c)

def cond_entropy(joint, marg):
    t = sum(marg.values())
    if not t: return 0.0
    return sum((n/t)*entropy(joint.get(x,{})) for x,n in marg.items())

def MI(class_lines, bridge=True):
    """I(class;prev). bridge=True drops None and bridges; bridge=False breaks bigram at None."""
    hm = Counter(); joint = defaultdict(Counter); marg = Counter()
    for line in class_lines:
        if bridge:
            seq = [c for c in line if c is not None]
            for c in seq: hm[c]+=1
            for a,b in zip(seq, seq[1:]):
                joint[a][b]+=1; marg[a]+=1
        else:
            for c in line:
                if c is not None: hm[c]+=1
            for a,b in zip(line, line[1:]):
                if a is not None and b is not None:
                    joint[a][b]+=1; marg[a]+=1
    return entropy(hm) - cond_entropy(joint, marg)

def shuffle_excess(class_lines, n_shuf, rng, bridge=True):
    """real_or_synth_I - its own shuffle mean."""
    base = MI(class_lines, bridge=bridge)
    seqs = [[c for c in line if c is not None] for line in class_lines]
    shuf_mis = []
    for _ in range(n_shuf):
        sl = []
        for s in seqs:
            ss = s[:]; rng.shuffle(ss); sl.append(ss)
        shuf_mis.append(MI(sl, bridge=True))
    return base - (sum(shuf_mis)/len(shuf_mis)), base

print('Loading Currier B...', flush=True)
tx = Transcript(); morph = Morphology()
by_line = defaultdict(list)
for tok in tx.all(h_only=True):
    if not tok.word or tok.is_uncertain: continue
    if tok.language != 'B': continue
    if not (tok.placement and tok.placement.startswith('P')): continue
    by_line[(tok.folio, tok.line)].append(tok.word)
ms_cache = {}
def has_ms(w):
    if w in ms_cache: return ms_cache[w]
    try:
        m = morph.extract(w); v = m.middle is not None and m.suffix is not None
    except Exception: v = False
    ms_cache[w] = v; return v
word_lines = []
for k in sorted(by_line.keys()):
    wl = [w for w in by_line[k] if has_ms(w)]
    if wl: word_lines.append(wl)
n_tokens = sum(len(l) for l in word_lines)
cm = json.load(open(PROJECT_ROOT/'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'))
ttc = cm['token_to_class']
def cl(wl): return [ttc.get(w) for w in wl]
real_lines = [cl(wl) for wl in word_lines]
print(f'  {len(word_lines)} lines, {n_tokens} tokens', flush=True)

rng = random.Random(0)
# REAL excess (own shuffle), both bridge modes
real_excess_bridge, real_I_bridge = shuffle_excess(real_lines, 30, rng, bridge=True)
real_excess_break, real_I_break = shuffle_excess(real_lines, 30, rng, bridge=False)
print(f'\nREAL excess over own shuffle:', flush=True)
print(f'  bridge mode: I={real_I_bridge:.4f}, excess={real_excess_bridge:+.4f}', flush=True)
print(f'  break  mode: I={real_I_break:.4f}, excess={real_excess_break:+.4f}', flush=True)

# 5-gram
def train(lines, order):
    c = defaultdict(Counter)
    for wl in lines:
        s=' '.join(wl); p='\x01'*(order-1)+s+'\x02'
        for i in range(order-1,len(p)): c[p[i-(order-1):i]][p[i]]+=1
    return c
def samp(counts, order, target, rng):
    out=[];ctx='\x01'*(order-1);buf=[];a=0
    while len(out)<target and a<target*60:
        a+=1;cand=counts.get(ctx)
        if not cand: ctx='\x01'*(order-1);continue
        ch=rng.choices(list(cand.keys()),weights=list(cand.values()),k=1)[0]
        if ch=='\x02':
            if buf:out.append(''.join(buf));buf=[]
            ctx='\x01'*(order-1)
            if len(out)>=target:break
            continue
        if ch==' ':
            if buf:out.append(''.join(buf));buf=[]
            ctx=(ctx+ch)[-(order-1):];continue
        buf.append(ch);ctx=(ctx+ch)[-(order-1):]
    if buf and len(out)<target:out.append(''.join(buf))
    return out[:target]
counts = train(word_lines, ORDER)

print(f'\nPer-synth own-shuffle excess ({N_SYNTH} synth x {N_SHUFFLE_PER} shuffles each)...', flush=True)
srng = random.Random(42)
synth_excess_bridge = []; synth_excess_break = []; synth_unmapped = []
for s in range(N_SYNTH):
    sl = [samp(counts, ORDER, len(wl), srng) for wl in word_lines]
    scl = [cl(wl) for wl in sl]
    stok = sum(len(l) for l in sl)
    smapped = sum(1 for line in scl for c in line if c is not None)
    synth_unmapped.append(1 - smapped/stok if stok else 0)
    eb, _ = shuffle_excess(scl, N_SHUFFLE_PER, srng, bridge=True)
    ek, _ = shuffle_excess(scl, N_SHUFFLE_PER, srng, bridge=False)
    synth_excess_bridge.append(eb); synth_excess_break.append(ek)
    if (s+1)%25==0:
        print(f'  [{s+1}/{N_SYNTH}] synth excess(bridge) mean={sum(synth_excess_bridge)/len(synth_excess_bridge):+.4f}', flush=True)

def summary(real_exc, synth_excs, label):
    m = sum(synth_excs)/len(synth_excs)
    sd = (sum((x-m)**2 for x in synth_excs)/len(synth_excs))**0.5
    z = (real_exc - m)/sd if sd>0 else float('nan')
    p = sum(1 for x in synth_excs if x >= real_exc)/len(synth_excs)
    pct95 = sorted(synth_excs)[int(0.95*len(synth_excs))]
    print(f'\n  [{label}] real_excess={real_exc:+.4f}', flush=True)
    print(f'    synth excess: mean={m:+.4f} sd={sd:.4f} 95pct={pct95:+.4f}', flush=True)
    print(f'    z={z:+.2f}  p_emp(synth>=real)={p:.4f}  real>95pct={real_exc>pct95}', flush=True)
    return {'real_excess':real_exc,'synth_mean':m,'synth_sd':sd,'synth_95pct':pct95,'z':z,'p_emp':p,'real_above_95':bool(real_exc>pct95)}

print('\n=== CONTROL RESULTS ===', flush=True)
res_bridge = summary(real_excess_bridge, synth_excess_bridge, 'BRIDGE')
res_break = summary(real_excess_break, synth_excess_break, 'BREAK-BIGRAM')
unmapped_mean = sum(synth_unmapped)/len(synth_unmapped)
print(f'\n  Synth unmapped fraction: {unmapped_mean:.3f} (real unmapped: {1-8755/14006:.3f})', flush=True)

clean = res_bridge['p_emp']<0.05 and res_break['p_emp']<0.05
print(f'\n=== VERDICT ===', flush=True)
if clean:
    print('  CLEAN SURVIVAL: real first-order class excess exceeds per-synth excess under BOTH', flush=True)
    print('  bridge and break-bigram modes. Not a coverage/bridging artifact. Not a character-statistic shadow.', flush=True)
    print('  Claim scope: first-order class structure not reproducible from local char statistics;', flush=True)
    print('  corroborates C976-C978 macro-automaton. NOT "above-Markov" (needs trigram), NOT hazard framework.', flush=True)
else:
    print('  DOES NOT cleanly survive the per-synth control. Reconsider.', flush=True)

RESULTS.write_text(json.dumps({
    'bridge': res_bridge, 'break_bigram': res_break,
    'synth_unmapped_mean': unmapped_mean, 'real_unmapped': 1-8755/14006,
    'clean_survival': bool(clean), 'n_synth': N_SYNTH, 'n_shuffle_per': N_SHUFFLE_PER,
}, indent=2))
print(f'\nWritten to {RESULTS}', flush=True)

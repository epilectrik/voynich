"""M2-vs-5-gram decomposition: which of M2's generative-sufficiency tests are
character-5-gram-floor, and which does M2 genuinely earn?

Resolves the C1025 scope-flag from PHASE_733. C1025 found M2 (49-class Markov +
forbidden suppression) passes 12/15 tests, but M0 (i.i.d. tokens) already passes 11/15
(marginal floor). The only sequential-discriminating tests are B1 (6-state spectral gap;
M0 fails, M1+ pass) and B3 (forbidden violations; only M2 passes).

A character 5-gram is strictly more powerful than M0 (captures morphology + local sequence).
This adds the 5-gram as a 6th model to the IDENTICAL battery (import the validated functions),
run through the same compute_metrics + evaluate_tests, and compare columns.

KEY: B1 here = 6-state spectral gap (real 0.894) = C978's actual number, which PHASE_733
did NOT re-measure (it used raw-49 lambda2). So this also directly tests C978 under 5-gram null.

PRE-REGISTERED predictions (locked):
- B1 (6-state spectral gap): 5-gram FAILS (per PHASE_733 lambda2 result; macro-eigenstructure
  not character-reproducible). If so, B1 is genuine above-character-Markov = C2061/C978 vindicated.
- B3 (forbidden violations): 5-gram PASSES (per PHASE_732, forbidden pairs mostly Markov-trivial).
  If so, M2's unique contribution over M1 is character-Markov-floor.
- Net prediction: 5-gram passes ~11-13/15; M2's "sufficiency" reduces to B1 (real macro-structure)
  + floor; the forbidden-suppression credit (B3) is character-reproducible.

flush + JSON. Reuses validated battery (no re-implementation of metrics).
"""
import sys, json, functools, importlib.util, random
import numpy as np
from pathlib import Path
print = functools.partial(print, flush=True)
PROJECT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))

# Import the validated battery module
spec = importlib.util.spec_from_file_location(
    'gensuff', str(PROJECT/'phases/GENERATIVE_SUFFICIENCY/scripts/generative_sufficiency.py'))
gs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gs)

RESULTS = PROJECT/'phases/PHASE_734_M2_VS_5GRAM/results/m2_vs_5gram.json'
ORDER = 5
TEST_NAMES = ['A1','A2','A3','A4','B1','B2','B3','B4','B5','C1','C2','C3','D1','D2','D3']

# ===== 5-gram generator (plugs into the battery as a 6th model) =====
_NGRAM_CACHE = {}
def _train_5gram(lines_words):
    from collections import defaultdict, Counter
    counts = defaultdict(Counter)
    for words in lines_words:
        s = ' '.join(words); p = '\x01'*(ORDER-1)+s+'\x02'
        for i in range(ORDER-1, len(p)): counts[p[i-(ORDER-1):i]][p[i]] += 1
    return {k: (list(v.keys()), np.array(list(v.values()), float)) for k, v in counts.items()}

def _sample_line(counts, target_n, rng):
    out=[]; ctx='\x01'*(ORDER-1); buf=[]; att=0
    while len(out)<target_n and att<target_n*60:
        att+=1; cand=counts.get(ctx)
        if not cand: ctx='\x01'*(ORDER-1); continue
        chars, w = cand; ch = chars[rng.choice(len(chars), p=w/w.sum())]
        if ch=='\x02':
            if buf: out.append(''.join(buf)); buf=[]
            ctx='\x01'*(ORDER-1)
            if len(out)>=target_n: break
            continue
        if ch==' ':
            if buf: out.append(''.join(buf)); buf=[]
            ctx=(ctx+ch)[-(ORDER-1):]; continue
        buf.append(ch); ctx=(ctx+ch)[-(ORDER-1):]
    if buf and len(out)<target_n: out.append(''.join(buf))
    return out[:target_n]

def generate_5gram(params, rng):
    """5-gram model: char-5-gram trained on real lines, generate matched-length token lines."""
    key = id(params)
    if key not in _NGRAM_CACHE:
        # reconstruct real token lines from the stored real corpus
        real_lines = params['_real_line_words']
        _NGRAM_CACHE[key] = _train_5gram(real_lines)
    counts = _NGRAM_CACHE[key]
    t2c = params['token_to_class']
    corpus = []
    for length in params['line_lengths']:
        toks = _sample_line(counts, length, rng)
        line = [{'word': w, 'cls': t2c.get(w, 1)} for w in toks]
        corpus.append(line)
    return corpus

# ===== run =====
print('Loading battery data...')
all_tokens, lines, params = gs.load_data()
morph = params['morph']
params['_real_tokens'] = all_tokens
# store real token lines for 5-gram training
params['_real_line_words'] = [[tok['word'] for tok in line] for line in lines]

real_metrics = gs.compute_metrics(lines, params, morph)
print(f"Real: B1 6-state spectral gap={real_metrics['B1_spectral_gap']:.4f}, B3 forbidden={real_metrics['B3_forbidden']}")

generators = {'M0':gs.generate_m0,'M1':gs.generate_m1,'M2':gs.generate_m2,
              'M3':gs.generate_m3,'M4':gs.generate_m4,'5GRAM':generate_5gram}
N_INST = gs.N_INST

col = {}  # model -> {test -> mean pass}
b1_vals = {}; b3_vals = {}
for mname, gen in generators.items():
    print(f'\n=== {mname}: {N_INST} instantiations ===')
    test_pass = {t: [] for t in TEST_NAMES}
    b1s=[]; b3s=[]
    for inst in range(N_INST):
        rng = np.random.RandomState(42 + inst*1000 + (hash(mname) % 10000))
        corpus = gen(params, rng)
        m = gs.compute_metrics(corpus, params, morph)
        tests = gs.evaluate_tests(m, real_metrics)
        for t in TEST_NAMES:
            test_pass[t].append(1.0 if tests.get(t) else 0.0)
        b1s.append(m['B1_spectral_gap']); b3s.append(m['B3_forbidden'])
    col[mname] = {t: float(np.mean(test_pass[t])) for t in TEST_NAMES}
    b1_vals[mname] = (float(np.mean(b1s)), float(np.std(b1s)))
    b3_vals[mname] = (float(np.mean(b3s)), float(np.std(b3s)))
    total = sum(col[mname].values())
    print(f'  {mname} passes {total:.1f}/15  | B1 gap={b1_vals[mname][0]:.4f}  B3 forbidden={b3_vals[mname][0]:.1f}')
    RESULTS.write_text(json.dumps({'col':col,'b1':b1_vals,'b3':b3_vals,'real_b1':real_metrics['B1_spectral_gap'],'real_b3':real_metrics['B3_forbidden']}, indent=2))

# ===== comparison table =====
print(f'\n{"="*72}')
print('PER-TEST PASS RATES (M0=i.i.d floor, 5GRAM=char-5-gram, M2=class+forbidden)')
print(f'{"="*72}')
print(f'{"test":>5} {"M0":>5} {"M1":>5} {"M2":>5} {"5GRAM":>6}   note')
for t in TEST_NAMES:
    m0=col['M0'][t]; m1=col['M1'][t]; m2=col['M2'][t]; fg=col['5GRAM'][t]
    note=''
    if m2>=0.5 and fg>=0.5 and m0<0.5: note='M2 earns over M0; 5gram ALSO gets it (char-floor)'
    elif m2>=0.5 and fg<0.5 and m0<0.5: note='M2 earns; 5gram FAILS -> above-char-Markov'
    elif m0>=0.5: note='marginal floor (M0 passes)'
    elif m2<0.5 and fg<0.5: note='nobody passes'
    print(f'{t:>5} {m0:>5.2f} {m1:>5.2f} {m2:>5.2f} {fg:>6.2f}   {note}')

print(f'\n=== KEY DISCRIMINATORS ===')
print(f'  B1 6-state spectral gap (real {real_metrics["B1_spectral_gap"]:.4f}): '
      f'M2 gap={b1_vals["M2"][0]:.4f} (pass {col["M2"]["B1"]:.2f}), 5gram gap={b1_vals["5GRAM"][0]:.4f} (pass {col["5GRAM"]["B1"]:.2f})')
print(f'  B3 forbidden (real {real_metrics["B3_forbidden"]}): '
      f'M2={b3_vals["M2"][0]:.1f} (pass {col["M2"]["B3"]:.2f}), 5gram={b3_vals["5GRAM"][0]:.1f} (pass {col["5GRAM"]["B3"]:.2f})')

fg_total = sum(col['5GRAM'].values()); m2_total = sum(col['M2'].values()); m0_total = sum(col['M0'].values())
print(f'\n  5GRAM total: {fg_total:.1f}/15   M2 total: {m2_total:.1f}/15   M0 total: {m0_total:.1f}/15')
b1_above = col['5GRAM']['B1'] < 0.5 and col['M2']['B1'] >= 0.5
b3_floor = col['5GRAM']['B3'] >= 0.5 and col['M2']['B3'] >= 0.5
print(f'\n  B1 above-char-Markov (5gram fails, M2 passes): {b1_above}')
print(f'  B3 char-floor (5gram passes too): {b3_floor}')
print(f'\n  INTERPRETATION: M2 genuinely earns the tests where 5gram fails but M2 passes;')
print(f'  tests where 5gram also passes are character-Markov-floor (M2 not earning over a char model).')

RESULTS.write_text(json.dumps({'col':col,'b1':b1_vals,'b3':b3_vals,
    'real_b1':real_metrics['B1_spectral_gap'],'real_b3':real_metrics['B3_forbidden'],
    'fg_total':fg_total,'m2_total':m2_total,'m0_total':m0_total,
    'b1_above_char_markov':bool(b1_above),'b3_char_floor':bool(b3_floor)}, indent=2))
print(f'\nWritten to {RESULTS}')

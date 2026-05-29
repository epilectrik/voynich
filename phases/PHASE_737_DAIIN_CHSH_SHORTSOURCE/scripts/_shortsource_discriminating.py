"""PHASE_737: daiin->CHSH short-source discriminating test (pre-registered in PHASE_735).

QUESTION (C2064 ambiguity): daiin->ch/sh survives the 5-gram null (z=4.05), but is that
(A) genuine lane-routing/attraction toward CHSH, or
(B) a char-signature artifact -- the char-5-gram cannot recover the source token's
    routing-relevant identity at the token boundary, so it mispredicts the successor
    and any such source shows a spurious positive excess regardless of routing?

MECHANISTIC FRAME: at a token boundary the order-5 char context is the last 4 chars of
"<source> ". For a SHORT source (len<=3) the FULL token sits inside that context
("ol " fits) -> the char model HAS the source identity and should reproduce its routing
-> DEMOTE. For a LONG source (daiin -> context "iin ") the identity is lost -> spurious
excess. ol (the canonical short CHSH-router, C817 lane-conditional 93.2%) already DEMOTED
(z=0.60) -> prior leans artifact. Test whether OTHER short high-CHSH sources survive.

PRE-REGISTERED DECISION RULE (locked, from PHASE_735 INDEX line 33):
  >=2 short witnesses survive  -> general lane-attraction is REAL (routing mechanism)
  <2  short witnesses survive  -> char-signature ARTIFACT (daiin survival is trivial;
                                  C2064 stays measurement-only, mechanism = artifact)

WITNESS SELECTION (mechanical, locked BEFORE null results):
  - source token has >= MIN_N non-line-final occurrences in Currier B
  - SHORT: char length <= 3
  - HIGH-CHSH: real unconditional ->ch/sh rate >= 1.5 * corpus base rate
  - WITNESS SET = short AND high-chsh AND N>=MIN_N (test ALL qualifying)
  - daiin (long ref, expect survive) and ol (short ref, expect demote) tested for
    calibration regardless of witness membership; NOT counted in the >=2 tally.

METRIC: per-synth-own-shuffle excess (identical to PHASE_733/735).
  real_excess = M_real - mean(M_real_within_line_shuffle)
  synth_excess = M_synth - mean(M_synth_OWN_within_line_shuffle)   [per synth corpus]
  p_emp = fraction of synth_excess >= real_excess.
SURVIVES: p_emp < Bonferroni alpha (0.05 / n_witness). Uncorrected p<0.05 also reported.

N_synth=200, N_shuffle_per=12, order=5. Identical 5-gram machinery to PHASE_735.
"""
import sys, json, functools, random
import numpy as np
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
PROJECT = Path('C:/git/voynich')
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript

RESULTS = PROJECT/'phases/PHASE_737_DAIIN_CHSH_SHORTSOURCE/results/shortsource_discriminating.json'
N_SYNTH=200; N_SHUF=12; ORDER=5
MIN_N=30; SHORT_MAXLEN=3; HIGH_MULT=1.5
TGT=('ch','sh')

print('Loading Currier B...')
tx=Transcript()
ld=defaultdict(list)
for tok in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w=tok.word.strip()
    if not w or '*' in w: continue
    ld[(tok.folio,tok.line)].append(w)
word_lines=[ld[k] for k in sorted(ld.keys())]
ntok=sum(len(l) for l in word_lines)
print(f'  {len(word_lines)} lines, {ntok} tokens')

# ===== corpus base rate + per-source ->CHSH table (real data; selection only) =====
base_hit=base_tot=0
src_tot=defaultdict(int); src_hit=defaultdict(int)
for l in word_lines:
    for i in range(len(l)-1):
        base_tot+=1
        nxt_chsh = l[i+1].startswith(TGT)
        if nxt_chsh: base_hit+=1
        src_tot[l[i]]+=1
        if nxt_chsh: src_hit[l[i]]+=1
base_rate=base_hit/base_tot
print(f'  corpus base P(next starts ch/sh) = {base_rate:.4f}')
print(f'  HIGH-CHSH threshold = {HIGH_MULT}*base = {HIGH_MULT*base_rate:.4f}')

# build table for sources with N>=MIN_N
rows=[]
for s,tot in src_tot.items():
    if tot<MIN_N: continue
    rate=src_hit[s]/tot
    rows.append((s,len(s),tot,rate))
rows.sort(key=lambda r:-r[3])

print(f'\n  Sources with N>={MIN_N}, ranked by ->ch/sh rate (showing short + top):')
print(f'  {"src":>10} {"len":>3} {"N":>5} {"->chsh":>7}  {"SHORT":>5} {"HIGH":>4}  {"WITNESS":>7}')
witnesses=[]
for s,ln,tot,rate in rows:
    is_short = ln<=SHORT_MAXLEN
    is_high  = rate>=HIGH_MULT*base_rate
    is_wit   = is_short and is_high
    if is_wit: witnesses.append(s)
    if is_short or rate>=HIGH_MULT*base_rate or s in ('daiin','ol'):
        print(f'  {s:>10} {ln:>3} {tot:>5} {rate:>7.4f}  {str(is_short):>5} {str(is_high):>4}  {str(is_wit):>7}')

# references (calibration, not counted)
refs=[r for r in ('daiin','ol') if r in src_tot and src_tot[r]>=MIN_N]
test_sources = list(dict.fromkeys(witnesses + refs))  # witnesses first, refs appended, dedup
print(f'\n  WITNESS SET ({len(witnesses)}): {witnesses}')
print(f'  REFERENCES (calibration, not in >=2 tally): {[r for r in refs if r not in witnesses]}')
print(f'  TESTING ({len(test_sources)}): {test_sources}')

def cond_prefix(lines, src, tgt=TGT):
    tot=hit=0
    for l in lines:
        for i in range(len(l)-1):
            if l[i]==src:
                tot+=1
                if l[i+1].startswith(tgt): hit+=1
    return hit/tot if tot else 0.0

def shuffle_lines(lines,rng):
    out=[]
    for l in lines:
        ll=l[:]; rng.shuffle(ll); out.append(ll)
    return out
def excess(lines, fn, n_shuf, rng):
    base=fn(lines)
    sh=[fn(shuffle_lines(lines,rng)) for _ in range(n_shuf)]
    return base-np.mean(sh), base

# ===== real excesses =====
rng=random.Random(0)
real_excess={}; real_val={}
for s in test_sources:
    e,v=excess(word_lines, lambda l,s=s: cond_prefix(l,s), 30, rng)
    real_excess[s]=e; real_val[s]=v
    print(f'  REAL {s}->chsh: rate={v:.4f} excess-over-shuffle={e:+.4f}')

# ===== 5-gram (identical to PHASE_735) =====
def train(lines,order):
    c=defaultdict(lambda: defaultdict(int))
    for wl in lines:
        s=' '.join(wl); p='\x01'*(order-1)+s+'\x02'
        for i in range(order-1,len(p)): c[p[i-(order-1):i]][p[i]]+=1
    return {k:(list(v.keys()),np.array(list(v.values()),float)) for k,v in c.items()}
def samp(counts,order,target,rng):
    out=[];ctx='\x01'*(order-1);buf=[];a=0
    while len(out)<target and a<target*60:
        a+=1;cand=counts.get(ctx)
        if not cand: ctx='\x01'*(order-1);continue
        chars,w=cand; ch=chars[rng.choice(len(chars),p=w/w.sum())]
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

counts5=train(word_lines,ORDER)
print(f'\n5-gram: {len(counts5)} contexts. Running {N_SYNTH} synth corpora...')
synth_excess={s:[] for s in test_sources}
prng=random.Random(42); nprng=np.random.RandomState(42)
for si in range(N_SYNTH):
    synth=[samp(counts5,ORDER,len(wl),nprng) for wl in word_lines]
    for s in test_sources:
        e,_=excess(synth, lambda l,s=s: cond_prefix(l,s), N_SHUF, prng)
        synth_excess[s].append(e)
    if (si+1)%25==0:
        print(f'  [{si+1}/{N_SYNTH}]')
        RESULTS.write_text(json.dumps({'base_rate':base_rate,'real_excess':real_excess,
            'real_val':real_val,'witnesses':witnesses,'synth_progress':si+1},indent=2))

# ===== verdicts =====
alpha_bonf = 0.05/len(witnesses) if witnesses else 0.05
print(f'\n{"="*94}')
print(f'Bonferroni alpha = 0.05/{len(witnesses)} = {alpha_bonf:.4f}')
print(f'{"source":>10} {"len":>3} {"N":>5} {"role":>9} {"real_exc":>9} {"synth_exc":>10} {"z":>6} {"p":>6}  {"unc<.05":>7} {"bonf":>6}')
print('-'*94)
out={}
for s in test_sources:
    se=np.array(synth_excess[s]); m=se.mean(); sd=se.std()
    z=(real_excess[s]-m)/sd if sd>0 else float('inf')
    p=float((se>=real_excess[s]).mean())
    role = 'WITNESS' if s in witnesses else 'ref'
    unc = p<0.05
    bonf = (s in witnesses) and (p<alpha_bonf)
    print(f'{s:>10} {len(s):>3} {src_tot[s]:>5} {role:>9} {real_excess[s]:>+9.4f} {m:>+10.4f} {z:>6.2f} {p:>6.3f}  {str(unc):>7} {str(bonf):>6}')
    out[s]={'len':len(s),'N':src_tot[s],'role':role,'real_rate':real_val[s],
            'real_excess':real_excess[s],'synth_excess_mean':float(m),'synth_excess_sd':float(sd),
            'z':float(z),'p_emp':p,'survives_uncorrected':unc,'survives_bonferroni':bonf}

# ===== pre-registered decision =====
wit_surv_bonf = [s for s in witnesses if out[s]['survives_bonferroni']]
wit_surv_unc  = [s for s in witnesses if out[s]['survives_uncorrected']]
print(f'\n{"="*94}')
print(f'WITNESS survivors (Bonferroni, alpha={alpha_bonf:.4f}): {wit_surv_bonf}  (n={len(wit_surv_bonf)})')
print(f'WITNESS survivors (uncorrected p<0.05):              {wit_surv_unc}  (n={len(wit_surv_unc)})')
verdict_bonf = 'LANE-ATTRACTION REAL' if len(wit_surv_bonf)>=2 else 'CHAR-SIGNATURE ARTIFACT'
verdict_unc  = 'LANE-ATTRACTION REAL' if len(wit_surv_unc)>=2 else 'CHAR-SIGNATURE ARTIFACT'
print(f'\nPRE-REGISTERED VERDICT (>=2 witnesses survive):')
print(f'  Bonferroni:   {verdict_bonf}')
print(f'  Uncorrected:  {verdict_unc}')
print(f'\nCalibration refs: daiin (long, expect SURVIVE) -> p={out.get("daiin",{}).get("p_emp")}; '
      f'ol (short, expect DEMOTE) -> p={out.get("ol",{}).get("p_emp")}')

RESULTS.write_text(json.dumps({
    'base_rate':base_rate,'high_threshold':HIGH_MULT*base_rate,'min_n':MIN_N,'short_maxlen':SHORT_MAXLEN,
    'witnesses':witnesses,'references':[r for r in refs if r not in witnesses],
    'alpha_bonferroni':alpha_bonf,'metrics':out,
    'witness_survivors_bonferroni':wit_surv_bonf,'witness_survivors_uncorrected':wit_surv_unc,
    'verdict_bonferroni':verdict_bonf,'verdict_uncorrected':verdict_unc,'n_synth':N_SYNTH},indent=2))
print(f'\nWritten to {RESULTS}')

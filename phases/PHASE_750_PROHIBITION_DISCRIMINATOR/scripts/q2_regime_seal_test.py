"""
Q2 — Is C2076's "sealed/self-contained" REGIME-real or a corpus-average artifact?

PRE-REGISTERED PREDICTION (crazy-expert, locked):
  The seal-BREAKING operations should be REGIME-stratified, concentrated in R3
  (open-cycle batch, aii-unseal enriched per C1247) and ~absent in R1 (sealed).
  Two metrics:
    (a) aii "unseal" by regime  -- reconfirm C1247 (R3 14/20 vs R1 1/32)
    (b) cross-line LATE->EARLY full FL reset by regime -- the NEW leg (C1227's 33)

KILL-CONDITION (locked):
  - KILL (corpus-average artifact): R1 ~= R3 on BOTH metrics -> "self-contained"
    is a corpus average, do NOT harden C2076.
  - SURVIVE (REGIME-real): R1 ~= 0 and R3 carries the seal-breaking -> C2076
    sharpens to "grammar encodes BOTH sealed-batch (R1) AND open-cohobation (R3)."

C2070 DISCIPLINE: REGIME is a soft gradient; report raw R1-vs-R3 AND within-section
  (R1 ~= Bio confound). FL state is terminal-suffix-based -> adjacent to the
  'terminal_rate' GMM-defining feature; flag as partial on-axis risk (the cross-line
  RESET is a dynamic, not the static rate, so off-axis-ish, but noted).
Method for (b) reproduces apparatus_transition_detection.py (C1227) exactly.
"""
import json, sys
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

def pr(*a): sys.stdout.buffer.write((' '.join(str(x) for x in a)+'\n').encode('ascii','replace'))

FL_STATES = {'EARLY': {'i','ii','in'},
             'MEDIAL': {'r','ar','al','l','ol'},
             'LATE': {'o','ly','am','m','dy','ry','y'}}
STATE_ORDER = {'EARLY':0,'MEDIAL':1,'LATE':2}
def fl_stage(mid):
    for s,ms in FL_STATES.items():
        if mid in ms: return s
    return None

ROOT = Path(__file__).resolve().parents[3]
reg = json.load(open(ROOT/'data'/'regime_folio_mapping.json'))['regime_assignments']
def regime(folio):
    r = reg.get(folio); return r['regime'] if r else None

tx = Transcript(); morph = Morphology()
# group tokens by (folio,line) in order; track par markers + section
line_tokens = defaultdict(list); folio_lines = defaultdict(list); line_meta = {}
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w: continue
    key = (t.folio, t.line)
    m = morph.extract(w)
    line_tokens[key].append(fl_stage(m.middle) if m.middle else None)
    if key not in line_meta:
        line_meta[key] = {'folio':t.folio,'section':t.section,'pi':False,'pf':False}
        folio_lines[t.folio].append(key)
    if t.par_initial: line_meta[key]['pi']=True
    if t.par_final:   line_meta[key]['pf']=True

# build paragraphs
paragraphs=[]
for folio,keys in folio_lines.items():
    cur=[]
    for key in keys:
        if line_meta[key]['pi'] and cur: paragraphs.append(cur); cur=[]
        cur.append(key)
        if line_meta[key]['pf']: paragraphs.append(cur); cur=[]
    if cur: paragraphs.append(cur)

# per-line first/last FL ; collect cross-line pairs from body (after header), 6+ body lines
MIN_BODY = 6
pairs=[]  # (folio, section, regime, from, to, regression)
for par in paragraphs:
    recs=[]
    for lk in par:
        fls=[s for s in line_tokens[lk] if s is not None]
        recs.append((fls[0] if fls else None, fls[-1] if fls else None))
    body = recs[1:]
    if len(body) < MIN_BODY: continue
    folio = line_meta[par[0]]['folio']; section = line_meta[par[0]]['section']
    rg = regime(folio)
    for i in range(len(body)-1):
        last_fl = body[i][1]; first_fl = body[i+1][0]
        if last_fl in STATE_ORDER and first_fl in STATE_ORDER:
            reggr = STATE_ORDER[last_fl]-STATE_ORDER[first_fl]
            pairs.append((folio, section, rg, last_fl, first_fl, reggr))

# ---- fidelity check vs C1227 ----
n_pairs=len(pairs)
le = [p for p in pairs if p[3]=='LATE' and p[4]=='EARLY']
regr = [p for p in pairs if p[5]>0]
pr(f"FIDELITY vs C1227: total cross-line pairs={n_pairs} (C1227=707), regressions={len(regr)} ({100*len(regr)/n_pairs:.1f}%, C1227=36.4%), LATE->EARLY={len(le)} (C1227=33)")

# ---- (b) LATE->EARLY by regime: RATE = LE / total pairs in that regime ----
by_reg_total=Counter(p[2] for p in pairs)
by_reg_le=Counter(p[2] for p in le)
reg_sizes={'REGIME_1':32,'REGIME_2':15,'REGIME_3':20,'REGIME_4':15}
pr("\n(b) CROSS-LINE LATE->EARLY FULL RESET by regime:")
for rg in ['REGIME_1','REGIME_2','REGIME_3','REGIME_4']:
    tot=by_reg_total[rg]; n=by_reg_le[rg]
    pr(f"  {rg} (n_folios={reg_sizes[rg]}): {n} LATE->EARLY / {tot} pairs = {100*n/tot if tot else 0:.2f}%")
# within-section (control R1~=Bio): LATE->EARLY rate by section x regime
pr("\n  within-section (R1 vs R3), LATE->EARLY rate:")
sec_reg_tot=Counter((p[1],p[2]) for p in pairs); sec_reg_le=Counter((p[1],p[2]) for p in le)
secs=sorted(set(p[1] for p in pairs))
for s in secs:
    row=[]
    for rg in ['REGIME_1','REGIME_3']:
        tot=sec_reg_tot[(s,rg)]; n=sec_reg_le[(s,rg)]
        row.append(f"{rg.split('_')[1]}={n}/{tot}({100*n/tot if tot else 0:.1f}%)")
    pr(f"    section {s}: "+"  ".join(row))

# ---- (a) aii "unseal" by regime (reconfirm C1247) ----
folio_has_aii=defaultdict(bool); aii_tok=Counter(); reg_tok=Counter()
for t in tx.currier_b():
    w=t.word.strip()
    if not w or '*' in w: continue
    rg=regime(t.folio)
    if rg: reg_tok[rg]+=1
    if w=='aii':
        folio_has_aii[t.folio]=True
        if rg: aii_tok[rg]+=1
pr("\n(a) aii 'unseal' by regime (reconfirm C1247):")
for rg in ['REGIME_1','REGIME_2','REGIME_3','REGIME_4']:
    folios=[f for f in reg if reg[f]['regime']==rg]
    nf=sum(1 for f in folios if folio_has_aii.get(f))
    rate=1000*aii_tok[rg]/reg_tok[rg] if reg_tok[rg] else 0
    pr(f"  {rg}: {nf}/{len(folios)} folios contain aii ; aii rate={rate:.3f}/1000 tokens")

# ---- verdict ----
r1=by_reg_le['REGIME_1']/by_reg_total['REGIME_1'] if by_reg_total['REGIME_1'] else 0
r3=by_reg_le['REGIME_3']/by_reg_total['REGIME_3'] if by_reg_total['REGIME_3'] else 0
pr(f"\nVERDICT INPUT: LATE->EARLY rate R1={100*r1:.2f}% vs R3={100*r3:.2f}% (ratio R3/R1={r3/r1 if r1 else float('inf'):.2f})")
json.dump({'n_pairs':n_pairs,'late_early_total':len(le),
           'le_by_regime':{k:by_reg_le[k] for k in reg_sizes},
           'pairs_by_regime':{k:by_reg_total[k] for k in reg_sizes},
           'aii_folios_by_regime':{rg:sum(1 for f in reg if reg[f]['regime']==rg and folio_has_aii.get(f)) for rg in reg_sizes}},
          open(ROOT/'phases'/'PHASE_750_PROHIBITION_DISCRIMINATOR'/'results'/'q2_regime_seal.json','w'),indent=2)
pr("\nwrote results/q2_regime_seal.json")

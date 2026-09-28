#!/usr/bin/env python3
"""
DECISIVE TEST v3 — EXACT canonical C2032 metric (heat-cycle MIDDLE-class for Voynich,
registered e-count high-e class for NL), extended to SYLLABLE-segmented NL.
Ported verbatim from MENSURAL_NOTATION_HYPOTHESIS/_length_stratified_c2032.py.

Judge on SIGN PATTERN (period-2 = lag1<0 & lag2>0; persistence = lag1>0 & lag2>0);
r21 is reported but is brittle when |lag1|~0.

PRE-REGISTERED:
  Voynich B should reproduce period-2 (lag1<0, lag2>0, r21~-0.66).
  VINDICATE my syllable theory iff some syllabified-NL corpus flips to period-2 (lag1<0 & lag2>0, r21<-0.40).
  KILL it iff syllabified NL stays persistence (lag1>0) / NL-range, as advisor/lean predict.
"""
import functools, json, random, re, sys
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
ROOT = Path("C:/git/voynich"); sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology
rng = random.Random(696); morph = Morphology(); tx = Transcript()
VOWELS = set('aeiouyàáâãäåæèéêëìíîïòóôõöøùúûüýÿœ')

def syllabify(w):
    n=len(w); isv=[c in VOWELS for c in w]
    if not any(isv): return [w]
    nuclei=[]; j=0
    while j<n:
        if isv[j]:
            k=j
            while k<n and isv[k]: k+=1
            nuclei.append((j,k)); j=k
        else: j+=1
    if len(nuclei)<=1: return [w]
    bounds=[0]
    for idx in range(len(nuclei)-1):
        ec=nuclei[idx][1]; sn=nuclei[idx+1][0]; cons=sn-ec
        bounds.append(ec if cons<=1 else ec+1)
    bounds.append(n)
    return [w[bounds[b]:bounds[b+1]] for b in range(len(bounds)-1) if w[bounds[b]:bounds[b+1]]]

# ---- canonical class definitions ----
def middle_class_3(word):
    try:
        m=morph.extract(word); mid=m.middle or ""
        return (mid or word.lower())[:3]
    except Exception:
        return word.lower()[:3]
def is_heat_cycle(cls): return cls in ("kee","ee") or cls.startswith("kee") or cls=="ke"
def latin_class(word):
    e=word.count("e")
    return "e3" if e>=3 else ("e2" if e==2 else "lo")
def is_high_e(cls): return cls in ("e2","e3")

def lag_n(paras_cls, lag, marker, n_perm=200):
    op=os_=0; ns=0.0
    for cl in paras_cls:
        if len(cl)<lag+1: continue
        for i in range(len(cl)-lag):
            if marker(cl[i]):
                op+=1
                if cl[i]==cl[i+lag]: os_+=1
        sh=list(cl)
        for _ in range(n_perm):
            rng.shuffle(sh)
            for i in range(len(sh)-lag):
                if marker(sh[i]) and sh[i]==sh[i+lag]: ns+=1.0/n_perm
    if op==0: return None
    return {'n':op,'excess':(os_-ns)/op}
def r21(paras_cls, marker):
    a=lag_n(paras_cls,1,marker); b=lag_n(paras_cls,2,marker)
    if not a or not b: return None
    e1,e2=a['excess'],b['excess']
    return {'lag1':e1,'lag2':e2,'n1':a['n'],'r21':(e2/e1 if abs(e1)>1e-9 else None)}

def voynich_B_paras():
    fp=defaultdict(list); cur=defaultdict(list)
    for t in tx.all(h_only=True):
        if not t.word or t.is_uncertain or t.language!="B": continue
        if not (t.placement and t.placement.startswith("P")): continue
        if t.par_initial and cur[t.folio]:
            fp[t.folio].append(cur[t.folio]); cur[t.folio]=[]
        cur[t.folio].append(t.word.lower())
    for f,p in cur.items():
        if p: fp[f].append(p)
    return [p for ps in fp.values() for p in ps]

def nl_paras(path, skip=0, min_words=5, max_paras=3000):
    txt='\n'.join(Path(path).read_text(encoding='utf-8',errors='ignore').split('\n')[skip:])
    out=[]
    for b in re.split(r"\n\s*\n", txt):
        ws=[re.sub(r"[^a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]","",w.lower()) for w in b.split()]
        ws=[w for w in ws if 3<=len(w)<=30]
        if len(ws)>=min_words: out.append(ws)
        if len(out)>=max_paras: break
    return out

def show(label, seg, r):
    if not r: print(f"  {label:<16}{seg:<9} (insufficient)"); return
    sign = "PERIOD-2" if (r['lag1']<0 and r['lag2']>0) else ("persistence" if (r['lag1']>0 and r['lag2']>0) else "mixed/decay")
    rr = f"{r['r21']:+.3f}" if r['r21'] is not None else "  n/a"
    print(f"  {label:<16}{seg:<9} lag1={r['lag1']:+.4f} lag2={r['lag2']:+.4f} n1={r['n1']:<6} r21={rr}  [{sign}]")

def main():
    print("=== VOYNICH-B replication (heat-cycle MIDDLE-class, canonical) ===")
    vb=voynich_B_paras()
    show('VOYNICH-B','token', r21([[middle_class_3(w) for w in p] for p in vb], is_heat_cycle))
    NL={'Codicillus(La)':('sources/codicillus/codicillus_complete_latin.txt',0),
        'Mesue(La)':('sources/mesue_grabadin/mesue_grabadin_latin_full.txt',0),
        'Dante(It)':('sources/italian_german/dante_inferno.txt',0),
        'Brunschwig(De)':('sources/brunschwig_1500/brunschwig_1500_corrected.txt',0)}
    print("\n=== NL e-count high-e class (registered Latin analog): word vs syllable ===")
    for name,(path,skip) in NL.items():
        paras=nl_paras(ROOT/path,skip)
        if not paras: print(f"  (missing {name})"); continue
        show(name,'word', r21([[latin_class(w) for w in p] for p in paras], is_high_e))
        show(name,'syllable', r21([[latin_class(s) for w in p for s in syllabify(w)] for p in paras], is_high_e))
    print("\nVoynich-B target: PERIOD-2 (r21~-0.66). KILL my theory if syllable-NL stays persistence/decay.")

if __name__=='__main__': main()

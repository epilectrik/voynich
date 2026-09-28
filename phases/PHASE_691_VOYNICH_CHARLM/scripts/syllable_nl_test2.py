#!/usr/bin/env python3
"""
DECISIVE TEST v2 — faithful C2031/C2032 (e-depth period-2 alternation), uniform across
Voynich tokens / word-NL / syllable-NL.

Method = canonical _length_stratified_c2032.py (per-paragraph lag-N same-class excess vs
within-paragraph shuffle null, r21 = lag2_excess/lag1_excess), but with a UNIFORM class
applicable to every segmentation: CLASS(unit) = e-depth bucket = min(count('e'), 3).
This is faithful because C2031 IS the e-depth sequential-asymmetry finding, and directly
tests my "e-stacking = vowel length" claim. Marked class = high-e starting points.

PRE-REGISTERED (locked):
  Voynich B should reproduce strong NEGATIVE r21 (period-2 alternation; canonical -0.66).
  My theory's DYNAMIC claim is VINDICATED iff some syllabified-NL corpus reaches r21 < -0.40
    (period-2 alternation emerges from syllabification).
  My theory's DYNAMIC claim is KILLED iff syllabified NL stays r21 >= 0 (persistence/sustain),
    matching the advisor/lean prediction that adjacent syllables CORRELATE, not alternate.
"""
import functools, json, random, re, sys
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
ROOT = Path("C:/git/voynich"); sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology
PHASE = ROOT/'phases'/'PHASE_691_VOYNICH_CHARLM'
rng = random.Random(696)
morph = Morphology(); tx = Transcript()
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

def e_bucket(u): return min(u.count('e'), 3)

def lag_same(paras_classes, lag, hi_thresh, n_perm=100):
    op=os_=0; ns=0.0
    for cl in paras_classes:
        if len(cl)<lag+1: continue
        for i in range(len(cl)-lag):
            if cl[i]>=hi_thresh:
                op+=1
                if cl[i]==cl[i+lag]: os_+=1
        sh=list(cl)
        for _ in range(n_perm):
            rng.shuffle(sh)
            for i in range(len(sh)-lag):
                if sh[i]>=hi_thresh and sh[i]==sh[i+lag]: ns+=1.0/n_perm
    if op==0: return None
    return {'n':op,'excess':(os_-ns)/op}

def r21(paras_classes, hi_thresh):
    a=lag_same(paras_classes,1,hi_thresh); b=lag_same(paras_classes,2,hi_thresh)
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

def nl_paras(path, skip=0, min_words=5, max_paras=2500):
    txt='\n'.join(Path(path).read_text(encoding='utf-8',errors='ignore').split('\n')[skip:])
    out=[]
    for b in re.split(r"\n\s*\n", txt):
        ws=[re.sub(r"[^a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]","",w.lower()) for w in b.split()]
        ws=[w for w in ws if 3<=len(w)<=30]
        if len(ws)>=min_words: out.append(ws)
        if len(out)>=max_paras: break
    return out

def classes_word(paras): return [[e_bucket(w) for w in p] for p in paras]
def classes_syl(paras):  return [[e_bucket(s) for w in p for s in syllabify(w)] for p in paras]

def report(label, seg, pc):
    for thr,tag in [(2,'e>=2'),(1,'e>=1')]:
        r=r21(pc, thr)
        if r and r['r21'] is not None:
            print(f"  {label:<16}{seg:<9}{tag:<6} lag1={r['lag1']:+.4f} lag2={r['lag2']:+.4f} "
                  f"n1={r['n1']:<6} r21={r['r21']:+.3f}")
        else:
            print(f"  {label:<16}{seg:<9}{tag:<6} (insufficient)")
        if seg=='word' and thr==2: break   # words: only need primary marker

def main():
    print("=== VOYNICH-B reference (e-depth class, per-paragraph) ===")
    vb=voynich_B_paras()
    report('VOYNICH-B','token', [[e_bucket(w) for w in p] for p in vb])
    NL={'Codicillus(La)':('sources/codicillus/codicillus_complete_latin.txt',0),
        'Mesue(La)':('sources/mesue_grabadin/mesue_grabadin_latin_full.txt',0),
        'Dante(It)':('sources/italian_german/dante_inferno.txt',0),
        'Brunschwig(De)':('sources/brunschwig_1500/brunschwig_1500_corrected.txt',0)}
    print("\n=== NATURAL LANGUAGE: word-segmented vs syllable-segmented ===")
    for name,(path,skip) in NL.items():
        paras=nl_paras(ROOT/path,skip)
        if not paras: print(f"  (missing {name})"); continue
        report(name,'word', classes_word(paras))
        report(name,'syllable', classes_syl(paras))
    print("\nVoynich-B target: strong NEGATIVE r21 (period-2). KILL my dynamics if syllable NL r21>=0.")
    print("VINDICATE my dynamics if any syllable NL r21 < -0.40.")

if __name__=='__main__': main()

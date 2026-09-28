#!/usr/bin/env python3
"""
DECISIVE TEST of the syllable-segmentation NL theory (experts' convergent design).

PRE-REGISTERED predictions (locked before looking):
  STATIC (my reframe): syllable-segmenting NL moves token length + token-entropy + type
    structure TOWARD Voynich (away from word-segmented NL). -> reframe correct on statics.
  CHAR-LEVEL (lean): char h1/h2 are segmentation-INVARIANT; Voynich's low char entropy gap
    vs NL survives regardless. Syllabification cannot touch it.
  DISCRIMINATOR (C2032): syllable-segmented NL r21 stays in NL range (|r21|<0.30), does NOT
    reproduce Voynich B's -0.66 period-2 anti-persistence.
    * KILL my theory's dynamic claim if NO syllabified NL corpus reaches r21 < -0.56.
    * VINDICATE my theory's dynamics only if some syllabified NL hits r21 in [-0.76,-0.56].
  REPETITION: syllabification does NOT create Voynich-level adjacent repetition -> repetition
    is a separate Voynich-specific feature, not a segmentation artifact.

Method = PHASE_717 _corpus_c2032_test.py exactly (most-common token chain-excess, within-chunk
shuffle null, chunk_size=1000, r21=lag2/lag1). Uniform across Voynich / word-NL / syllable-NL.
"""
import functools, json, math, random, re, sys
from collections import Counter
from pathlib import Path
print = functools.partial(print, flush=True)
ROOT = Path("C:/git/voynich")
PHASE = ROOT/'phases'/'PHASE_691_VOYNICH_CHARLM'
random.seed(42)
N_PERM = 100

VOWELS = set('aeiouyàáâãäåæèéêëìíîïòóôõöøùúûüýÿœ')

def syllabify(w):
    """Maximal-onset heuristic: V-CV for single consonant, VC-CV for clusters."""
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
        end_cur=nuclei[idx][1]; start_next=nuclei[idx+1][0]; cons=start_next-end_cur
        bounds.append(end_cur if cons<=1 else end_cur+1)
    bounds.append(n)
    return [w[bounds[b]:bounds[b+1]] for b in range(len(bounds)-1) if w[bounds[b]:bounds[b+1]]]

# ---- C2032 (verbatim method from PHASE_717) ----
def class_chain_excess(seqs, target, lags=(1,2,3), n_perm=N_PERM):
    out={}
    for lag in lags:
        oh=op=0
        for seq in seqs:
            for i in range(len(seq)-lag):
                if seq[i]==target:
                    op+=1
                    if seq[i+lag]==target: oh+=1
        obs=oh/op if op else 0.0
        nrs=[]
        for _ in range(n_perm):
            nh=npp=0
            for seq in seqs:
                perm=seq.copy(); random.shuffle(perm)
                for i in range(len(perm)-lag):
                    if perm[i]==target:
                        npp+=1
                        if perm[i+lag]==target: nh+=1
            nrs.append(nh/npp if npp else 0.0)
        out[lag]=obs-(sum(nrs)/len(nrs))
    return out

def chunks(words, cs=1000):
    return [words[i:i+cs] for i in range(0,len(words),cs) if len(words[i:i+cs])>=50]

def char_entropy(tokens):
    """segmentation-invariant char h1 and h2 on concatenated token chars (no spaces)."""
    s=''.join(tokens)
    c1=Counter(s); tot=len(s)
    h1=-sum((v/tot)*math.log2(v/tot) for v in c1.values())
    bg=Counter(zip(s,s[1:])); pc=Counter(s[:-1])
    h2=0.0; tb=sum(bg.values())
    for (a,b),v in bg.items():
        p_ab=v/tb; p_b_given_a=v/pc[a]
        h2-=p_ab*math.log2(p_b_given_a)
    return h1,h2

def analyze(tokens, label, seg='word'):
    if len(tokens)<500: return {'label':label,'seg':seg,'error':f'n={len(tokens)}'}
    cnt=Counter(tokens); target=cnt.most_common(1)[0][0]
    seqs=chunks(tokens)
    ch=class_chain_excess(seqs,target)
    r21=ch[2]/ch[1] if abs(ch[1])>1e-9 else float('nan')
    lens=[len(t) for t in tokens]
    rep=sum(1 for i in range(len(tokens)-1) if tokens[i]==tokens[i+1])/(len(tokens)-1)
    h1,h2=char_entropy(tokens[:20000])
    return {'label':label,'seg':seg,'n':len(tokens),'vocab':len(cnt),
            'mean_len':sum(lens)/len(lens),'std_len':(sum((l-sum(lens)/len(lens))**2 for l in lens)/len(lens))**.5,
            'top_freq':cnt[target]/len(tokens),'adj_rep':rep,
            'char_h1':h1,'char_h2':h2,'lag1':ch[1],'lag2':ch[2],'r21':r21}

def load_nl(path, skip=0, maxw=40000):
    p=Path(path)
    if not p.exists(): return None
    text='\n'.join(p.read_text(encoding='utf-8',errors='replace').split('\n')[skip:]).lower()
    words=re.findall(r'[a-zàáâãäåæçèéêëìíîïñòóôõöøùúûüýÿœß]+',text)
    words=[w for w in words if 3<=len(w)<=30 and not re.search(r'(.)\1{4,}',w)]
    return words[:maxw]

def voynich_B():
    toks=[]
    for sp in ['train','val','test']:
        for x in open(PHASE/'data'/f'corpus_{sp}.jsonl',encoding='utf-8'):
            r=json.loads(x)
            if r.get('section')=='B': toks+=r['tokens']
    return toks

def main():
    NL={'Codicillus(La)':('sources/codicillus/codicillus_complete_latin.txt',0),
        'Mesue(La)':('sources/mesue_grabadin/mesue_grabadin_latin_full.txt',0),
        'Dante(It)':('sources/italian_german/dante_inferno.txt',0),
        'Brunschwig(De)':('sources/brunschwig_1500/brunschwig_1500_corrected.txt',0)}
    rows=[]
    vb=voynich_B()
    rows.append(analyze(vb,'VOYNICH-B','token'))
    for name,(path,skip) in NL.items():
        w=load_nl(ROOT/path,skip)
        if not w: print(f"  (missing {name}: {path})"); continue
        rows.append(analyze(w,name,'word'))
        syl=[s for word in w for s in syllabify(word)]
        rows.append(analyze(syl,name,'syllable'))

    hdr=f"{'corpus':<16}{'seg':<9}{'n':>7}{'vocab':>7}{'mlen':>6}{'slen':>6}{'topf':>7}{'adjR':>7}{'ch1':>6}{'ch2':>6}{'lag1':>8}{'lag2':>8}{'r21':>8}"
    print(hdr); print('-'*len(hdr))
    for r in rows:
        if 'error' in r: print(f"{r['label']:<16}{r['seg']:<9} {r['error']}"); continue
        print(f"{r['label']:<16}{r['seg']:<9}{r['n']:>7}{r['vocab']:>7}{r['mean_len']:>6.2f}{r['std_len']:>6.2f}"
              f"{r['top_freq']:>7.3f}{r['adj_rep']:>7.3f}{r['char_h1']:>6.2f}{r['char_h2']:>6.2f}"
              f"{r['lag1']:>+8.4f}{r['lag2']:>+8.4f}{r['r21']:>+8.3f}")
    print("\nVoynich-B reference r21 = -0.66 (target). NL-range |r21|<0.30.")
    print("DISCRIMINATOR: does any SYLLABLE row reach r21<-0.56? (vindicate) or stay >-0.36? (kill my dynamics)")
    (PHASE/'results'/'predictions'/'syllable_nl_test.json').write_text(json.dumps(rows,indent=2))

if __name__=='__main__': main()

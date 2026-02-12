"""Scan candidate folios for REGIME_3 fingerprint match."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
from scripts.voynich import BFolioDecoder, Transcript

dec = BFolioDecoder()

# Candidates: union of both R3 lists + aggressive folios + some R1/R4 for comparison
candidates = [
    # Primary R3 list
    'f103r', 'f104v', 'f114v', 'f115r', 'f116r', 'f31r', 'f33r', 'f33v',
    'f39r', 'f46r', 'f77r', 'f81r', 'f83v', 'f86v4', 'f95r1', 'f95r2',
    # Secondary R3 list
    'f26r', 'f34r', 'f78v', 'f81v', 'f84v', 'f94r', 'f114r',
    # A few known R1/R2 for contrast
    'f103v', 'f75r', 'f26v',
]
# Deduplicate
candidates = sorted(set(candidates))

r3_mids = {'eed', 'eod', 'ed', 'eeo'}

print(f"{'FOLIO':<10} {'TOK':>4} {'e%':>5} {'k%':>5} {'R3mid':>6} {'CC%':>5} {'CHSH%':>6} {'QO%':>5} {'OK%':>5} {'VERDICT':<15}")
print('-' * 90)

results = []
for folio in candidates:
    try:
        lines = dec.analyze_folio_lines(folio)
    except:
        continue
    if not lines:
        continue

    tokens = [tok for la in lines for tok in la.tokens]
    total = len(tokens)
    if total < 20:
        continue

    # Kernel counts
    kern = Counter()
    for t in tokens:
        if t.kernels:
            for kk in t.kernels:
                kern[kk] += 1
    e_pct = kern.get('e', 0) / total * 100
    k_pct = kern.get('k', 0) / total * 100

    # R3 MIDDLE markers
    mid_counts = Counter()
    for t in tokens:
        if t.morph and t.morph.middle:
            mid_counts[t.morph.middle] += 1
    r3_mid_count = sum(mid_counts.get(m, 0) for m in r3_mids)
    r3_mid_pct = r3_mid_count / total * 100

    # CC markers (daiin pattern + bare ol)
    cc_count = sum(1 for t in tokens if 'daiin' in t.word or t.word == 'ol')
    cc_pct = cc_count / total * 100

    # CHSH vs QO
    chsh = sum(1 for t in tokens if t.morph and t.morph.prefix in ('ch', 'sh'))
    chsh += sum(1 for t in tokens if t.morph and t.morph.prefix2 in ('ch', 'sh'))
    qo = sum(1 for t in tokens if t.morph and t.morph.prefix == 'qo')
    chsh_pct = chsh / total * 100
    qo_pct = qo / total * 100

    # OK vessel
    ok = sum(1 for t in tokens if t.morph and t.morph.prefix == 'ok')
    ok_pct = ok / total * 100

    # R3 score: e-dominant + R3 mids + high CC + high CEI (low LINK = high QO)
    # e > k, R3 mids present, CC enriched, QO elevated
    score = 0
    if e_pct > k_pct:
        score += 3  # e-dominant
    score += min(r3_mid_pct * 2, 6)  # R3 MIDDLEs (up to 6 pts)
    score += min(cc_pct, 5)  # CC concentration (up to 5 pts)
    if qo_pct > 15:
        score += 2  # elevated QO

    verdict = ''
    if score >= 10:
        verdict = 'STRONG R3'
    elif score >= 6:
        verdict = 'POSSIBLE R3'
    elif e_pct > k_pct:
        verdict = 'e-dom (weak)'
    else:
        verdict = 'NOT R3'

    results.append((folio, total, e_pct, k_pct, r3_mid_pct, cc_pct, chsh_pct, qo_pct, ok_pct, score, verdict))

# Sort by score descending
results.sort(key=lambda x: -x[9])

for r in results:
    folio, total, e_pct, k_pct, r3_mid_pct, cc_pct, chsh_pct, qo_pct, ok_pct, score, verdict = r
    print(f"{folio:<10} {total:4d} {e_pct:5.1f} {k_pct:5.1f} {r3_mid_pct:6.1f} {cc_pct:5.1f} {chsh_pct:6.1f} {qo_pct:5.1f} {ok_pct:5.1f} {verdict:<15} ({score:.1f})")

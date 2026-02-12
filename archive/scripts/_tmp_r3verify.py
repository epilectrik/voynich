"""Deep verification of f104v as REGIME_3 folio."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
from scripts.voynich import BFolioDecoder, Transcript

dec = BFolioDecoder()
folio = 'f104v'

lines = dec.analyze_folio_lines(folio)
tokens = [tok for la in lines for tok in la.tokens]
total = len(tokens)

print(f"FOLIO: {folio}")
print(f"Total tokens: {total}")
print(f"Total lines: {len(lines)}")
print()

# 1. Kernel distribution
kern = Counter()
for t in tokens:
    if t.kernels:
        for kk in t.kernels:
            kern[kk] += 1
print("=== KERNEL DISTRIBUTION ===")
for k, c in kern.most_common():
    print(f"  {k}: {c} ({c/total*100:.1f}%)")
e_count = kern.get('e', 0)
k_count = kern.get('k', 0)
h_count = kern.get('h', 0)
print(f"\n  e-dominant: {'YES' if e_count > k_count else 'NO'} (e={e_count}, k={k_count})")
print()

# 2. MIDDLE distribution (top 20)
mid = Counter()
for t in tokens:
    if t.morph and t.morph.middle:
        mid[t.morph.middle] += 1
print("=== TOP 20 MIDDLEs ===")
r3_mids = {'eed', 'eod', 'ed', 'eeo'}
for m, c in mid.most_common(20):
    tag = ' *** R3 MARKER' if m in r3_mids else ''
    print(f"  {m:8s}: {c:3d} ({c/total*100:.1f}%){tag}")
r3_mid_total = sum(mid.get(m, 0) for m in r3_mids)
print(f"\n  R3 MIDDLE total: {r3_mid_total} ({r3_mid_total/total*100:.1f}%)")
print()

# 3. PREFIX distribution (top 15)
pref = Counter()
for t in tokens:
    if t.morph and t.morph.prefix:
        pref[t.morph.prefix] += 1
    if t.morph and t.morph.prefix2:
        pref[t.morph.prefix2] += 1
print("=== PREFIX DISTRIBUTION ===")
for p, c in pref.most_common(15):
    print(f"  {p:8s}: {c:3d} ({c/total*100:.1f}%)")
chsh = pref.get('ch', 0) + pref.get('sh', 0)
qo = pref.get('qo', 0)
print(f"\n  CHSH: {chsh} ({chsh/total*100:.1f}%)")
print(f"  QO: {qo} ({qo/total*100:.1f}%)")
print(f"  QO/CHSH ratio: {qo/chsh:.2f}" if chsh > 0 else "  QO/CHSH ratio: N/A")
print()

# 4. SUFFIX distribution
suf = Counter()
for t in tokens:
    if t.morph and t.morph.suffix:
        suf[t.morph.suffix] += 1
print("=== SUFFIX DISTRIBUTION ===")
for s, c in suf.most_common(10):
    print(f"  {s:8s}: {c:3d} ({c/total*100:.1f}%)")
print()

# 5. CC markers (daiin + ol)
daiin_count = sum(1 for t in tokens if 'daiin' in t.word)
ol_count = sum(1 for t in tokens if t.word == 'ol')
print(f"=== CORE CONTROL MARKERS ===")
print(f"  daiin-containing: {daiin_count} ({daiin_count/total*100:.1f}%)")
print(f"  bare 'ol': {ol_count} ({ol_count/total*100:.1f}%)")
print(f"  CC total: {daiin_count + ol_count} ({(daiin_count + ol_count)/total*100:.1f}%)")
print()

# 6. R3 fingerprint summary
print("=" * 60)
print("R3 FINGERPRINT VERIFICATION")
print("=" * 60)
checks = []
# e-dominant
checks.append(('e-dominant kernel', e_count > k_count, f"e={e_count} vs k={k_count}"))
# R3 MIDDLEs enriched
checks.append(('R3 MIDDLEs present (eed/eod/ed/eeo)', r3_mid_total > 0, f"{r3_mid_total} tokens ({r3_mid_total/total*100:.1f}%)"))
# CC enrichment
cc_total = daiin_count + ol_count
checks.append(('CC enrichment (>4%)', cc_total/total > 0.04, f"{cc_total/total*100:.1f}%"))
# CHSH high
checks.append(('CHSH prefix high (>25%)', chsh/total > 0.25, f"{chsh/total*100:.1f}%"))
# QO elevated
checks.append(('QO elevated (>15%)', qo/total > 0.15, f"{qo/total*100:.1f}%"))

passed = 0
for name, result, detail in checks:
    status = 'PASS' if result else 'FAIL'
    if result:
        passed += 1
    print(f"  [{status}] {name}: {detail}")

print(f"\n  SCORE: {passed}/{len(checks)} checks passed")
if passed >= 4:
    print(f"  VERDICT: CONFIRMED REGIME_3")
elif passed >= 3:
    print(f"  VERDICT: LIKELY REGIME_3")
else:
    print(f"  VERDICT: NOT REGIME_3")

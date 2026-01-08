"""Quick check of prefix system overlap."""

A_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
B_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'lc', 'lk', 'ls']
HT_TOP_PREFIXES = ['yk', 'op', 'yt', 'so', 'al', 'po', 'do', 'to', 'pc', 'ke', 'dc', 'sa', 'yc', 'oc', 'oe']

a_set = set(A_PREFIXES)
b_set = set(B_PREFIXES)
ht_set = set(HT_TOP_PREFIXES)

print("=" * 60)
print("PREFIX SYSTEM OVERLAP ANALYSIS")
print("=" * 60)
print()
print(f"A/B prefixes: {sorted(a_set)}")
print(f"HT prefixes:  {sorted(ht_set)}")
print()
print(f"A intersection HT: {sorted(a_set & ht_set) if a_set & ht_set else 'NONE'}")
print(f"B intersection HT: {sorted(b_set & ht_set) if b_set & ht_set else 'NONE'}")
print(f"HT-only (not in A or B): {sorted(ht_set - a_set - b_set)}")
print()
print("=" * 60)
print("VERDICT")
print("=" * 60)
print()
if not (a_set & ht_set):
    print("The prefix systems are COMPLETELY DISJOINT.")
    print("HT uses an entirely different prefix vocabulary than Currier A and B.")
    print()
    print("THREE DISTINCT NOTATION SYSTEMS:")
    print("  1. Currier A: ch-, qo-, sh-, da-, ok-, ot-, ct-, ol-")
    print("  2. Currier B: Same as A + lc-, lk-, ls- (grammar operators)")
    print("  3. Human Track: yk-, op-, yt-, so-, po-, do-, sa-, ke-, dc-, pc-, ...")
else:
    print(f"Some overlap exists: {a_set & ht_set}")

"""Cross-reference dark pipeline material candidates with Currier A registry.
Test: do fch/cs/eckh RI derivatives in A cluster on folios that correspond
to their B-folio material usage?"""
import sys, io, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load all tokens
all_a = list(tx.currier_a())
all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

with open('C:/git/voynich/data/dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

# Target dark MIDDLEs
TARGETS = {
    'fch': 'mercury',
    'cs': 'gold',
    'eckh': 'volatile liquid',
    'lch': 'apparatus (control)',
    'lk': 'fire (control)',
    'cth': 'state-transition (control)',
    'rai': 'metallic',
    'eet': 'cooling transfer',
    'tsh': 'cohobation',
}

print("=" * 90)
print("DARK PIPELINE → CURRIER A CROSS-REFERENCE")
print("=" * 90)

for dark_mid, label in TARGETS.items():
    # Find all B tokens containing this dark MIDDLE
    b_folios = defaultdict(int)
    for t in all_b:
        m = morph.extract(t.word)
        if m.middle == dark_mid:
            b_folios[t.folio] += 1

    # Find all A tokens where this dark MIDDLE appears as a substring of the MIDDLE
    # (RI = PP + extension, so the dark MIDDLE may be embedded in a longer A MIDDLE)
    a_tokens_exact = []
    a_tokens_contains = []
    a_folios_exact = defaultdict(int)
    a_folios_contains = defaultdict(int)

    for t in all_a:
        m = morph.extract(t.word)
        if m.middle:
            if m.middle == dark_mid:
                a_tokens_exact.append(t)
                a_folios_exact[t.folio] += 1
            elif dark_mid in m.middle and len(m.middle) > len(dark_mid):
                a_tokens_contains.append(t)
                a_folios_contains[t.folio] += 1

    total_a = len(a_tokens_exact) + len(a_tokens_contains)

    if total_a == 0 and len(b_folios) == 0:
        continue

    print(f"\n{'='*80}")
    print(f"  {dark_mid} = {label}")
    print(f"  B folios: {len(b_folios)} ({sum(b_folios.values())} tokens)")
    print(f"  A exact match: {len(a_tokens_exact)} tokens on {len(a_folios_exact)} folios")
    print(f"  A contains (RI derivatives): {len(a_tokens_contains)} tokens on {len(a_folios_contains)} folios")

    if a_tokens_exact:
        print(f"\n  A EXACT MATCHES:")
        for f in sorted(a_folios_exact, key=lambda x: -a_folios_exact[x]):
            print(f"    {f}: x{a_folios_exact[f]}")

    if a_tokens_contains:
        print(f"\n  A RI DERIVATIVES (dark MIDDLE embedded in longer MIDDLE):")
        # Show the actual derivative MIDDLEs
        deriv_mids = Counter()
        for t in a_tokens_contains:
            m = morph.extract(t.word)
            deriv_mids[m.middle] += 1
        print(f"    Derivative MIDDLEs: {dict(deriv_mids.most_common(10))}")

        print(f"    A folio distribution:")
        for f in sorted(a_folios_contains, key=lambda x: -a_folios_contains[x])[:15]:
            print(f"      {f}: x{a_folios_contains[f]}")
        if len(a_folios_contains) > 15:
            print(f"      ... and {len(a_folios_contains)-15} more")

    # Check B-A folio correspondence
    # For each B folio with this dark MIDDLE, which A folios have corresponding content?
    if b_folios and (a_folios_exact or a_folios_contains):
        all_a_folios = set(a_folios_exact.keys()) | set(a_folios_contains.keys())
        b_folio_set = set(b_folios.keys())

        # Check if A folios share folio NUMBERS with B folios (recto/verso or nearby)
        # A folios are typically different pages from B folios, but may share section neighborhoods
        b_sections = set()
        for t in all_b:
            if t.folio in b_folio_set:
                b_sections.add(t.section)

        a_in_b_sections = 0
        a_total = len(all_a_folios)
        for f in all_a_folios:
            a_toks = [t for t in all_a if t.folio == f]
            if a_toks and a_toks[0].section in b_sections:
                a_in_b_sections += 1

        if a_total > 0:
            print(f"\n  B sections where {dark_mid} appears: {b_sections}")
            print(f"  A folios in same sections: {a_in_b_sections}/{a_total} ({100*a_in_b_sections/a_total:.0f}%)")

print("\n\n" + "=" * 90)
print("SUMMARY: Which dark MIDDLEs have A-system presence?")
print("=" * 90)
for dark_mid, label in TARGETS.items():
    a_exact = sum(1 for t in all_a if morph.extract(t.word).middle == dark_mid)
    a_contains = sum(1 for t in all_a if morph.extract(t.word).middle and dark_mid in morph.extract(t.word).middle and morph.extract(t.word).middle != dark_mid)
    b_count = sum(1 for t in all_b if morph.extract(t.word).middle == dark_mid)
    print(f"  {dark_mid:>6s} ({label:>20s}): B={b_count:3d}  A_exact={a_exact:3d}  A_deriv={a_contains:3d}")

"""Compare bridge MIDDLE profiles: fch-positive (compound) vs NONE (simple) herbal folios.
Do compound preparations show different operational vocabulary?"""
import sys, io, json
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

with open('C:/git/voynich/data/dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# From our clustering results
COMPOUND = ['f39r', 'f40v', 'f50r', 'f66v']  # fch-positive, alcohol compound
SIMPLE = ['f26r', 'f26v', 'f31v', 'f33r', 'f33v', 'f34r', 'f34v', 'f39v', 'f40r',
          'f41r', 'f41v', 'f46r', 'f48r', 'f48v', 'f50v', 'f55r', 'f55v',
          'f94r', 'f94v', 'f95r1', 'f95r2', 'f95v1']  # NONE group
FULL_COMPOUND = ['f31r']  # fch+eckh+rai

def folio_profile(folios, label):
    """Get aggregate operational profile for a set of folios."""
    all_toks = [t for t in all_b if t.folio in folios]
    n = len(all_toks)

    # PREFIX distribution
    prefixes = Counter()
    # Bridge vs dark MIDDLE distribution
    bridge_mids = Counter()
    dark_mids = Counter()
    # Key operational tokens
    dar = sum(1 for t in all_toks if t.word == 'dar')
    dal = sum(1 for t in all_toks if t.word == 'dal')
    chekar = sum(1 for t in all_toks if t.word == 'chekar')
    daiin = sum(1 for t in all_toks if t.word == 'daiin')
    shedy = sum(1 for t in all_toks if t.word == 'shedy')
    chedy = sum(1 for t in all_toks if t.word == 'chedy')
    qokedy = sum(1 for t in all_toks if t.word == 'qokedy')
    qokeedy = sum(1 for t in all_toks if t.word == 'qokeedy')

    e_depths = []
    for t in all_toks:
        a = morph.atomize(t.word)
        if a.prefix:
            prefixes[a.prefix] += 1
        m = morph.extract(t.word)
        if m.middle:
            if m.middle in dp_set:
                dark_mids[m.middle] += 1
            else:
                bridge_mids[m.middle] += 1
        e_depths.append(a.e_depth)

    gentle = sum(1 for e in e_depths if e >= 2)
    avg_e = sum(e_depths) / len(e_depths) if e_depths else 0

    print(f"\n{'='*80}")
    print(f"  {label}: {len(folios)} folios, {n} tokens")
    print(f"{'='*80}")
    print(f"  PREFIX: qo={100*prefixes.get('qo',0)/n:.1f}% ch={100*prefixes.get('ch',0)/n:.1f}% "
          f"sh={100*prefixes.get('sh',0)/n:.1f}% ok={100*prefixes.get('ok',0)/n:.1f}% "
          f"da={100*prefixes.get('da',0)/n:.1f}% ol={100*prefixes.get('ol',0)/n:.1f}%")
    print(f"  Gentle heat: {100*gentle/n:.1f}% | Mean e-depth: {avg_e:.2f}")
    print(f"  dar={dar} dal={dal} chekar={chekar} daiin={daiin}")
    print(f"  shedy={shedy} chedy={chedy} qokedy={qokedy} qokeedy={qokeedy}")
    print(f"  Per-folio dar: {dar/len(folios):.1f} | Per-folio dal: {dal/len(folios):.1f}")
    print(f"  Bridge MIDDLEs: {len(bridge_mids)} unique, {sum(bridge_mids.values())} tokens")
    print(f"  Dark MIDDLEs: {len(dark_mids)} unique, {sum(dark_mids.values())} tokens")
    print(f"  Dark %: {100*sum(dark_mids.values())/n:.1f}%")

    # Top bridge MIDDLEs
    print(f"\n  Top 15 bridge MIDDLEs:")
    for mid, count in bridge_mids.most_common(15):
        rate = 1000 * count / n
        print(f"    {mid:>8s}: {count:4d} ({rate:5.1f} per 1000)")

    return prefixes, bridge_mids, dark_mids, n

print("COMPOUND (alcohol) vs SIMPLE (no alcohol) HERBAL FOLIOS")

p_comp, b_comp, d_comp, n_comp = folio_profile(COMPOUND, "COMPOUND (fch+, 4 folios)")
p_simp, b_simp, d_simp, n_simp = folio_profile(SIMPLE, "SIMPLE (no fch, 22 folios)")
p_full, b_full, d_full, n_full = folio_profile(FULL_COMPOUND, "FULL COMPOUND (f31r only)")

# Compare: which bridge MIDDLEs are ENRICHED in compound vs simple?
print(f"\n\n{'='*80}")
print("BRIDGE MIDDLEs ENRICHED IN COMPOUND vs SIMPLE")
print(f"{'='*80}")
print(f"\n  {'MIDDLE':>8s} {'Comp/1k':>8s} {'Simp/1k':>8s} {'Ratio':>7s} {'Reading':>20s}")
print(f"  {'-'*55}")

enriched = []
for mid in set(list(b_comp.keys()) + list(b_simp.keys())):
    comp_rate = 1000 * b_comp.get(mid, 0) / n_comp if n_comp > 0 else 0
    simp_rate = 1000 * b_simp.get(mid, 0) / n_simp if n_simp > 0 else 0
    if comp_rate > 0 and simp_rate > 0:
        ratio = comp_rate / simp_rate
        if ratio > 2.0 or ratio < 0.5:
            enriched.append((ratio, mid, comp_rate, simp_rate))

enriched.sort(reverse=True)
for ratio, mid, comp_rate, simp_rate in enriched[:15]:
    print(f"  {mid:>8s} {comp_rate:8.1f} {simp_rate:8.1f} {ratio:7.2f}x")

print(f"\n  --- DEPLETED in compound (enriched in simple) ---")
for ratio, mid, comp_rate, simp_rate in enriched[-15:]:
    print(f"  {mid:>8s} {comp_rate:8.1f} {simp_rate:8.1f} {ratio:7.2f}x")

# Bridge MIDDLEs UNIQUE to compound folios (not on any simple folio)
comp_unique = set(b_comp.keys()) - set(b_simp.keys())
simp_unique = set(b_simp.keys()) - set(b_comp.keys())
print(f"\n  Bridge MIDDLEs UNIQUE to compound: {len(comp_unique)}")
if comp_unique:
    for mid in sorted(comp_unique, key=lambda m: -b_comp[m])[:10]:
        print(f"    {mid}: {b_comp[mid]}x")
print(f"  Bridge MIDDLEs UNIQUE to simple: {len(simp_unique)}")

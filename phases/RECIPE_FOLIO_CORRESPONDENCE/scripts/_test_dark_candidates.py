"""Test dark pipeline material candidates corpus-wide.
fch = mercury? cs = gold? cth = organic? eet = balneum product?"""
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

# Build per-folio dark MIDDLE inventory for ALL 83 folios
folio_darks = defaultdict(lambda: defaultdict(int))
folio_tokens = defaultdict(int)
all_folios = sorted(set(t.folio for t in all_b))

for t in all_b:
    folio_tokens[t.folio] += 1
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        folio_darks[t.folio][m.middle] += 1

# Known recipe associations
MERCURY_FOLIOS = {'f107r', 'f79r', 'f81v', 'f78v', 'f108r', 'f82v'}  # recipes involving mercury/mercury-water
NON_MERCURY_FOLIOS = {'f75r', 'f82r', 'f83r', 'f84r', 'f66r', 'f80r', 'f77v'}  # recipes without mercury

GOLD_FOLIOS = {'f84r', 'f81v'}  # recipes explicitly using gold
NON_GOLD_FOLIOS = {'f75r', 'f76r', 'f79r', 'f82r', 'f83r', 'f112r', 'f80r', 'f77v', 'f108r'}

ORGANIC_FOLIOS = {'f75r', 'f82r', 'f80r', 'f76v', 'f78v', 'f112r'}  # honey, wax, flesh, lunaria, ferment
MINERAL_FOLIOS = {'f107r', 'f116r', 'f66r'}  # lead, quicksilver, amalgam

BALNEUM_FOLIOS = {'f75r', 'f84r', 'f81v', 'f103r', 'f112r', 'f108r', 'f82r'}  # explicit balneum in recipe
NON_BALNEUM_FOLIOS = {'f79r', 'f116r', 'f66r', 'f83r', 'f107r'}  # no balneum

def test_candidate(dark_mid, pos_folios, neg_folios, label):
    """Test whether a dark MIDDLE concentrates on positive vs negative folios."""
    pos_count = sum(folio_darks[f].get(dark_mid, 0) for f in pos_folios)
    neg_count = sum(folio_darks[f].get(dark_mid, 0) for f in neg_folios)
    pos_tok = sum(folio_tokens[f] for f in pos_folios)
    neg_tok = sum(folio_tokens[f] for f in neg_folios)

    pos_rate = 1000 * pos_count / pos_tok if pos_tok > 0 else 0
    neg_rate = 1000 * neg_count / neg_tok if neg_tok > 0 else 0
    ratio = pos_rate / neg_rate if neg_rate > 0 else float('inf') if pos_rate > 0 else 0

    print(f"\n  {dark_mid} = {label}?")
    print(f"    Positive folios ({len(pos_folios)}): {pos_count} tokens in {pos_tok} total = {pos_rate:.2f} per 1000")
    print(f"    Negative folios ({len(neg_folios)}): {neg_count} tokens in {neg_tok} total = {neg_rate:.2f} per 1000")
    print(f"    Enrichment: {ratio:.2f}x")

    # Now check ALL 83 folios
    all_with = []
    all_without = []
    for f in all_folios:
        count = folio_darks[f].get(dark_mid, 0)
        if count > 0:
            all_with.append((f, count, folio_tokens[f]))

    print(f"    Corpus-wide: {len(all_with)}/82 folios have {dark_mid}")
    if len(all_with) <= 20:
        for f, c, n in sorted(all_with, key=lambda x: -x[1]):
            in_pos = '*' if f in pos_folios else ' '
            in_neg = 'X' if f in neg_folios else ' '
            section = ''
            toks = [t for t in all_b if t.folio == f]
            if toks:
                section = toks[0].section
            print(f"      {in_pos}{in_neg} {f:>8s} (sec={section}): x{c}")
    else:
        # Just show top 10
        for f, c, n in sorted(all_with, key=lambda x: -x[1])[:10]:
            in_pos = '*' if f in pos_folios else ' '
            in_neg = 'X' if f in neg_folios else ' '
            toks = [t for t in all_b if t.folio == f]
            section = toks[0].section if toks else '?'
            print(f"      {in_pos}{in_neg} {f:>8s} (sec={section}): x{c}")
        print(f"      ... and {len(all_with)-10} more")

    verdict = 'SUPPORTED' if ratio >= 2.0 else 'WEAK' if ratio >= 1.3 else 'FAILED'
    print(f"    VERDICT: {verdict}")
    return ratio

print("=" * 80)
print("CORPUS-WIDE DARK PIPELINE CANDIDATE TESTS")
print("=" * 80)

print("\n--- TEST 1: fch = mercury/mercury-water ---")
test_candidate('fch', MERCURY_FOLIOS, NON_MERCURY_FOLIOS, 'mercury')

print("\n--- TEST 2: cs = gold ---")
test_candidate('cs', GOLD_FOLIOS, NON_GOLD_FOLIOS, 'gold')

print("\n--- TEST 3: cth = organic material ---")
test_candidate('cth', ORGANIC_FOLIOS, MINERAL_FOLIOS, 'organic')

print("\n--- TEST 4: eet = balneum-processed product ---")
test_candidate('eet', BALNEUM_FOLIOS, NON_BALNEUM_FOLIOS, 'balneum product')

print("\n--- TEST 5: eckh = lunaria/plant liquid ---")
LUNARIA_FOLIOS = {'f112v', 'f82r', 'f80r'}
NON_LUNARIA_FOLIOS = {'f84r', 'f107r', 'f116r', 'f66r', 'f83r'}
test_candidate('eckh', LUNARIA_FOLIOS, NON_LUNARIA_FOLIOS, 'lunaria/plant')

print("\n--- TEST 6: lsh = ash/fire medium ---")
ASH_FOLIOS = {'f76r', 'f77v', 'f80r', 'f79r', 'f116r'}
NON_ASH_FOLIOS = {'f75r', 'f84r', 'f81v', 'f103r'}
test_candidate('lsh', ASH_FOLIOS, NON_ASH_FOLIOS, 'ash/fire medium')

print("\n--- TEST 7: rai = metallic quality ---")
METAL_FOLIOS = {'f107r', 'f84r', 'f81v', 'f66r'}
NON_METAL_FOLIOS = {'f75r', 'f82r', 'f80r', 'f83r', 'f112r'}
test_candidate('rai', METAL_FOLIOS, NON_METAL_FOLIOS, 'metallic')

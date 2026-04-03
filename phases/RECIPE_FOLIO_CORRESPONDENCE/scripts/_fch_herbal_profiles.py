"""Profile the 4 fch-positive herbal folios: f39r, f40v, f50r, f66v.
What makes each distinctive? Can we match to Brunschwig recipe types?"""
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

PREFIX_GLOSS = {
    'qo': 'HEAT-SRC', 'ch': 'TEST', 'sh': 'MONITOR', 'ok': 'VESSEL',
    'ot': 'OPS-STATE', 'da': 'SETUP', 'ol': 'CONTINUE',
}

# Also include f31r (MERCURY+VOLATILE+METALLIC) for comparison
targets = ['f39r', 'f40v', 'f50r', 'f66v', 'f31r']

for folio in targets:
    toks = [t for t in all_b if t.folio == folio]
    n = len(toks)

    # Basic profile
    prefixes = Counter()
    e_depths = []
    dar_count = 0
    dal_count = 0
    chekar_count = 0
    for t in toks:
        a = morph.atomize(t.word)
        if a.prefix:
            prefixes[a.prefix] += 1
        e_depths.append(a.e_depth)
        if t.word == 'dar': dar_count += 1
        if t.word == 'dal': dal_count += 1
        if t.word == 'chekar': chekar_count += 1

    gentle = sum(1 for e in e_depths if e >= 2)
    avg_e = sum(e_depths) / len(e_depths) if e_depths else 0

    # Dark inventory with line context
    darks = []
    lines = defaultdict(list)
    for t in toks:
        lines[t.line].append(t)

    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            line_words = [x.word for x in lines[t.line]]
            darks.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': morph.atomize(t.word).prefix or '-',
                'suffix': m.suffix or '-',
                'line': t.line,
            })

    print("=" * 90)
    print(f"  {folio}: {n} tokens, {len(darks)} dark tokens")
    print(f"  Top prefixes: {', '.join(f'{p}={c}' for p, c in prefixes.most_common(5))}")
    qo_pct = 100 * prefixes.get('qo', 0) / n
    ch_pct = 100 * prefixes.get('ch', 0) / n
    sh_pct = 100 * prefixes.get('sh', 0) / n
    ok_pct = 100 * prefixes.get('ok', 0) / n
    print(f"  qo={qo_pct:.1f}% ch={ch_pct:.1f}% sh={sh_pct:.1f}% ok={ok_pct:.1f}%")
    print(f"  Gentle heat: {100*gentle/n:.1f}% | dar={dar_count} dal={dal_count} chekar={chekar_count}")
    print(f"  Mean e-depth: {avg_e:.2f}")
    print(f"\n  Dark MIDDLEs:")
    for d in darks:
        a = morph.atomize(d['word'])
        atoms = '.'.join(g for c, role, g in a.atoms if g)
        print(f"    L{d['line']:>3s} [{d['prefix']}+{d['middle']}+{d['suffix']}] = {atoms}  ({d['word']})")
    print()

# Comparison: Brunschwig recipe types
print("=" * 90)
print("BRUNSCHWIG RECIPE TYPE PREDICTIONS")
print("=" * 90)
print("""
Brunschwig's compound preparations differ by:
  1. SIMPLE aqua vitae (degree 1 balneum, just wine distilled)
  2. COMPOSITA with herbs (steep herbs in AV, redistill)
  3. COMPOSITA with spices (add spices to 2nd distillation)
  4. COMPOSITA with precious substances (gold leaf, musk, ambergris added after distilling)
  5. BALSAM (gums+resins+oils, 3-fraction distillation)
  6. THERIAC/MITHRIDATE (60+ ingredients, months of maturation)

Key discriminators from dark pipeline:
  - fch alone = basic AV compound (herbs in alcohol)
  - fch + eckh = volatile compound (careful thermal management needed)
  - fch + rai = metal-containing compound (gold leaf, antimony)
  - fch + eckh + rai = full compound with metal + volatile (f31r = rosewater with all markers)
""")

for folio in targets:
    toks = [t for t in all_b if t.folio == folio]
    darks_set = set()
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            darks_set.add(m.middle)

    has_fch = 'fch' in darks_set
    has_eckh = 'eckh' in darks_set
    has_rai = 'rai' in darks_set
    has_cs = 'cs' in darks_set

    if has_fch and has_eckh and has_rai:
        pred = "FULL COMPOUND (metal + volatile + alcohol) — Brunschwig type 4-6"
    elif has_fch and has_eckh:
        pred = "VOLATILE COMPOUND (careful thermal + alcohol) — Brunschwig type 2-3"
    elif has_fch and has_rai:
        pred = "METAL COMPOUND (gold/antimony + alcohol) — Brunschwig type 4"
    elif has_fch:
        pred = "HERB COMPOUND (herbs steeped in alcohol) — Brunschwig type 2"
    elif has_eckh:
        pred = "VOLATILE SIMPLE (careful distillation, no alcohol) — NOT compound"
    else:
        pred = "SIMPLE DISTILLATION (no alcohol, no compound)"

    n = len(toks)
    gentle = sum(1 for t in toks if morph.atomize(t.word).e_depth >= 2)
    dar = sum(1 for t in toks if t.word == 'dar')

    print(f"\n  {folio} ({n} tok, gentle={100*gentle/n:.0f}%, dar={dar}):")
    print(f"    Material markers: fch={'Y' if has_fch else 'N'} eckh={'Y' if has_eckh else 'N'} rai={'Y' if has_rai else 'N'} cs={'Y' if has_cs else 'N'}")
    print(f"    PREDICTION: {pred}")

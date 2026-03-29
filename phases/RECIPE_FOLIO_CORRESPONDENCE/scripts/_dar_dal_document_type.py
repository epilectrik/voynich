"""
Document type classification via dar:dal ratio.

Hypothesis: dar (setup:receive = add material) and dal (setup:level = set
a parameter) distinguish two document types:
  PROCEDURE folios: dar > dal (adding materials, executing recipes)
  SPECIFICATION folios: dal > dar (setting levels, describing equipment)

Test across all 83 Currier B folios.
"""

import sys, io
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

def safe_int(x):
    try: return int(x)
    except: return 0

folios = sorted(set(t.folio for t in all_b))

# ═══ COMPUTE PER-FOLIO dar/dal ═══
folio_data = []

for folio in folios:
    toks = [t for t in all_b if t.folio == folio]
    n = len(toks)
    if n < 20:
        continue

    words = [t.word for t in toks]
    dar_n = words.count('dar')
    dal_n = words.count('dal')
    section = toks[0].section

    flines = sorted(set(t.line for t in toks), key=safe_int)

    # t-gallows ratio
    para_gallows = []
    for li in flines:
        lt = [t for t in toks if t.line == li]
        if lt and lt[0].word and lt[0].word[0] in 'tkpf' and len(lt[0].word) > 1:
            para_gallows.append(lt[0].word[0])
    t_gal = para_gallows.count('t')
    tot_gal = len(para_gallows)

    # qokal count
    qokal_n = words.count('qokal')

    # Classify
    if dar_n > dal_n and dar_n >= 2:
        doc_type = 'PROCEDURE'
    elif dal_n > dar_n and dal_n >= 2:
        doc_type = 'SPECIFICATION'
    elif dar_n == dal_n and dar_n >= 2:
        doc_type = 'BALANCED'
    elif dar_n + dal_n <= 1:
        doc_type = 'MINIMAL'
    else:
        doc_type = 'LOW'

    folio_data.append({
        'folio': folio, 'n': n, 'section': section,
        'dar': dar_n, 'dal': dal_n,
        'ratio': dar_n / dal_n if dal_n > 0 else (99 if dar_n > 0 else 0),
        'doc_type': doc_type,
        't_gal': t_gal, 'tot_gal': tot_gal,
        'qokal': qokal_n,
    })

# ═══ SUMMARY ═══
print("DOCUMENT TYPE CLASSIFICATION VIA dar:dal RATIO")
print("=" * 100)

type_counts = Counter(d['doc_type'] for d in folio_data)
print(f"\n  Total folios: {len(folio_data)}")
for dt, ct in type_counts.most_common():
    print(f"    {dt:15s}: {ct:3d} ({100*ct/len(folio_data):.0f}%)")

# ═══ PROCEDURE FOLIOS ═══
print("\n\n" + "=" * 100)
print("PROCEDURE FOLIOS (dar > dal, dar >= 2)")
print("=" * 100)

procs = sorted([d for d in folio_data if d['doc_type'] == 'PROCEDURE'],
               key=lambda d: -d['dar'])

print(f"\n  {'Folio':>8s} {'N':>5s} {'Sec':>4s} {'dar':>4s} {'dal':>4s} {'ratio':>6s} {'qokal':>6s} {'tG':>6s}")
print(f"  {'-'*50}")
for d in procs:
    r = f"{d['ratio']:.1f}" if d['ratio'] < 50 else 'INF'
    print(f"  {d['folio']:>8s} {d['n']:5d} {d['section']:>4s} {d['dar']:4d} {d['dal']:4d} {r:>6s} {d['qokal']:6d} {d['t_gal']:2d}/{d['tot_gal']:2d}")

# ═══ SPECIFICATION FOLIOS ═══
print("\n\n" + "=" * 100)
print("SPECIFICATION FOLIOS (dal > dar, dal >= 2)")
print("=" * 100)

specs = sorted([d for d in folio_data if d['doc_type'] == 'SPECIFICATION'],
               key=lambda d: -d['dal'])

print(f"\n  {'Folio':>8s} {'N':>5s} {'Sec':>4s} {'dar':>4s} {'dal':>4s} {'ratio':>6s} {'qokal':>6s} {'tG':>6s}")
print(f"  {'-'*50}")
for d in specs:
    r = f"{d['ratio']:.1f}" if d['ratio'] < 50 else '0:N'
    print(f"  {d['folio']:>8s} {d['n']:5d} {d['section']:>4s} {d['dar']:4d} {d['dal']:4d} {r:>6s} {d['qokal']:6d} {d['t_gal']:2d}/{d['tot_gal']:2d}")

# ═══ SECTION DISTRIBUTION ═══
print("\n\n" + "=" * 100)
print("DOCUMENT TYPE BY SECTION")
print("=" * 100)

sec_type = defaultdict(Counter)
for d in folio_data:
    sec_type[d['section']][d['doc_type']] += 1

for sec in sorted(sec_type.keys()):
    total = sum(sec_type[sec].values())
    print(f"\n  Section {sec} ({total} folios):")
    for dt, ct in sec_type[sec].most_common():
        print(f"    {dt:15s}: {ct:3d} ({100*ct/total:.0f}%)")

# ═══ ADJACENCY PATTERNS ═══
print("\n\n" + "=" * 100)
print("ADJACENCY: Do specifications sit next to procedures?")
print("=" * 100)

folio_type = {d['folio']: d['doc_type'] for d in folio_data}
folio_list = [d['folio'] for d in folio_data]

spec_neighbors = []
for i, f in enumerate(folio_list):
    if folio_type[f] == 'SPECIFICATION':
        prev_f = folio_list[i-1] if i > 0 else None
        next_f = folio_list[i+1] if i < len(folio_list)-1 else None
        prev_type = folio_type.get(prev_f, '?')
        next_type = folio_type.get(next_f, '?')
        print(f"  {f}: [{prev_f}({prev_type})] <- SPEC -> [{next_f}({next_type})]")

# ═══ dar AND dal TOTALS ═══
print("\n\n" + "=" * 100)
print("CORPUS TOTALS")
print("=" * 100)

total_dar = sum(d['dar'] for d in folio_data)
total_dal = sum(d['dal'] for d in folio_data)
print(f"\n  Total dar: {total_dar}")
print(f"  Total dal: {total_dal}")
print(f"  Corpus ratio: {total_dar/total_dal:.2f}:1 (dar:dal)")

# How many folios have NEITHER
neither = sum(1 for d in folio_data if d['dar'] == 0 and d['dal'] == 0)
print(f"  Folios with neither: {neither}/{len(folio_data)}")

# ═══ KNOWN MATCHES CHECK ═══
print("\n\n" + "=" * 100)
print("KNOWN RECIPE MATCHES: Document type")
print("=" * 100)

known = {
    'f75r': ('Ch19', 'Aqua vitae — repeated distillation with material additions'),
    'f76r': ('Ch18', 'Element separation — silver-plate purity test'),
    'f77v': ('Ch27', 'Furnace specification — equipment description'),
    'f84r': ('Ch14', 'Gold dissolution — balneum mariae'),
    'f108r': ('Ch16', 'Two-phase element separation'),
}

for folio, (ch, desc) in known.items():
    dt = folio_type.get(folio, '?')
    d = next((x for x in folio_data if x['folio'] == folio), None)
    if d:
        print(f"  {folio} ({ch}): {dt:15s}  dar={d['dar']} dal={d['dal']}  -- {desc}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)

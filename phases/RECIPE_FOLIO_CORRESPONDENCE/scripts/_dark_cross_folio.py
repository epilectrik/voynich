"""Cross-folio dark MIDDLE analysis: which dark MIDDLEs share across recipe-matched folios?"""
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

FOLIOS = {
    'f75r': {'ch': 'Ch19M', 'materials': ['honey', 'wax', 'aqua_vitae'], 'apparatus': ['cucurbit', 'alembic', 'balneum'], 'process': ['distillation', 'fermentation', 'cohobation']},
    'f76r': {'ch': 'Ch18P', 'materials': ['composite_stone', 'silver_plate'], 'apparatus': ['alembic', 'vessel'], 'process': ['distillation', 'rectification', 'washing', 'silver_test']},
    'f84r': {'ch': 'Ch14P', 'materials': ['gold', 'quintessence', 'silver_water', 'twelve_E'], 'apparatus': ['cucurbit', 'balneum'], 'process': ['dissolution', 'putrefaction', 'balneum']},
    'f79r': {'ch': 'Ch12M', 'materials': ['sublimated_mercury', 'mercury_water', 'stone_water'], 'apparatus': ['alembic'], 'process': ['sublimation', 'dissolution', 'distillation', 'congelation']},
    'f82r': {'ch': 'Ch22M', 'materials': ['lunaria_moisture', 'flesh_substance'], 'apparatus': ['cucurbit', 'glass_cover', 'wax_seal'], 'process': ['maceration', 'ash_distillation', 'sealing']},
    'f76v': {'ch': 'Ch15M', 'materials': ['tincture_ferment', 'H'], 'apparatus': [], 'process': ['liquefaction', 'fixation', 'binding']},
    'f103r': {'ch': 'Ch16M', 'materials': ['ferment_B', 'ferment_E', 'ferment_G'], 'apparatus': ['chambers'], 'process': ['multiplication', 'balneum', 'ash_drying']},
    'f77v': {'ch': 'Ch27M', 'materials': [], 'apparatus': ['5_furnaces', 'shelves', 'conduits', 'covers'], 'process': ['calcination', 'distillation', 'imbibition', 'balneum', 'correction']},
    'f81v': {'ch': 'Ch18M', 'materials': ['mercury_water', 'gold'], 'apparatus': ['cucurbit', 'alembic'], 'process': ['balneum', 'cohobation', 'rectification', 'dissolution']},
    'f112r': {'ch': 'Ch11M', 'materials': ['ruby_liquor'], 'apparatus': ['alembic'], 'process': ['balneum', 'cohobation', 'ash_distillation', 'calcination', 'washing']},
    'f112v': {'ch': 'Ch1M', 'materials': ['lunaria_liquor'], 'apparatus': ['alembic', 'furnace'], 'process': ['distillation', 'sublimation', 'separation']},
    'f116r': {'ch': 'Ch4M', 'materials': ['sublimated_substance', 'quicksilver'], 'apparatus': [], 'process': ['fixation', 'sublimation', 'fusibility_test']},
    'f78v': {'ch': 'Ch14M', 'materials': ['mercury_water', 'sulfur', 'sweetness_mixings'], 'apparatus': ['cucurbit'], 'process': ['dissolution', 'congelation', 'rubification', 'balneum', 'ash_drying']},
    'f83r': {'ch': 'Ch9P', 'materials': ['D', 'C', 'sawdust', 'marc'], 'apparatus': ['cucurbit', 'alembic', 'furnace', 'phials'], 'process': ['grinding', 'sealing', 'graduated_fire', 'distillation']},
    'f108r': {'ch': 'Ch16P', 'materials': ['putrefied_composite'], 'apparatus': ['alembic', 'aludel', 'balneum'], 'process': ['balneum', 'ash_distillation', 'separation']},
    'f107r': {'ch': 'Ch44M', 'materials': ['lead_earth', 'quicksilver', 'rubified_sulfur'], 'apparatus': [], 'process': ['coagulation', 'sublimation', 'projection']},
    'f80r': {'ch': 'Ch21-25M', 'materials': ['capon_flesh', 'lunaria_moisture', 'bones'], 'apparatus': ['alembic'], 'process': ['ash_distillation', 'maceration', 'combination']},
    'f82v': {'ch': 'Ch28M', 'materials': [], 'apparatus': ['cover', 'alembic', 'cucurbit'], 'process': ['specification']},
    'f66r': {'ch': 'Ch24P', 'materials': ['amalgam'], 'apparatus': [], 'process': ['fixation', 'sublimation']},
}

# Build dark MIDDLE -> folio presence map
dark_folio_map = defaultdict(set)
dark_folio_count = defaultdict(lambda: defaultdict(int))

for folio in FOLIOS:
    toks = [t for t in all_b if t.folio == folio]
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            dark_folio_map[m.middle].add(folio)
            dark_folio_count[m.middle][folio] += 1

# Find dark MIDDLEs shared across 3+ matched folios
print("=" * 100)
print("DARK MIDDLEs SHARED ACROSS 3+ MATCHED FOLIOS")
print("=" * 100)

shared = [(mid, folios) for mid, folios in dark_folio_map.items() if len(folios) >= 3]
shared.sort(key=lambda x: -len(x[1]))

for mid, folios in shared:
    folio_list = sorted(folios)
    print(f"\n  DARK MIDDLE: {mid} ({len(folios)} folios)")

    # What materials/processes do these folios share?
    all_materials = set()
    all_apparatus = set()
    all_processes = set()
    for f in folio_list:
        info = FOLIOS[f]
        all_materials.update(info['materials'])
        all_apparatus.update(info['apparatus'])
        all_processes.update(info['process'])

    # What materials are COMMON across all folios with this dark middle?
    if len(folio_list) >= 2:
        common_materials = set(FOLIOS[folio_list[0]]['materials'])
        common_apparatus = set(FOLIOS[folio_list[0]]['apparatus'])
        common_processes = set(FOLIOS[folio_list[0]]['process'])
        for f in folio_list[1:]:
            common_materials &= set(FOLIOS[f]['materials'])
            common_apparatus &= set(FOLIOS[f]['apparatus'])
            common_processes &= set(FOLIOS[f]['process'])
    else:
        common_materials = set()
        common_apparatus = set()
        common_processes = set()

    for f in folio_list:
        info = FOLIOS[f]
        count = dark_folio_count[mid][f]
        print(f"    {f} ({info['ch']}): x{count}  materials={info['materials']}")

    if common_materials:
        print(f"    >>> SHARED MATERIALS: {common_materials}")
    if common_apparatus:
        print(f"    >>> SHARED APPARATUS: {common_apparatus}")
    if common_processes:
        print(f"    >>> SHARED PROCESSES: {common_processes}")
    if not common_materials and not common_apparatus and not common_processes:
        print(f"    >>> No common materials/apparatus/processes across all folios")
        print(f"    >>> All materials present: {all_materials}")

# Also show folio-exclusive dark MIDDLEs (appear on only 1 matched folio)
print("\n\n" + "=" * 100)
print("FOLIO-EXCLUSIVE DARK MIDDLEs (unique to 1 matched folio)")
print("=" * 100)

for folio in sorted(FOLIOS.keys()):
    info = FOLIOS[folio]
    exclusive = []
    toks = [t for t in all_b if t.folio == folio]
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            if len(dark_folio_map[m.middle] & set(FOLIOS.keys())) == 1:
                exclusive.append(m.middle)

    if exclusive:
        unique_exc = sorted(set(exclusive))
        print(f"\n  {folio} ({info['ch']}): {len(unique_exc)} exclusive dark MIDDLEs")
        print(f"    Materials: {info['materials']}")
        print(f"    Exclusive: {unique_exc}")

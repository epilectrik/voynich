"""Build dark pipeline inventory for all matched folios with line-level context."""
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

# Our confirmed/strong folios with recipe matches
FOLIOS = [
    ('f75r', 'Ch19M', 'Aqua vitae (honey+wax, 9x reflux, balneum)'),
    ('f76r', 'Ch18P', 'Element separation (silver-plate test)'),
    ('f84r', 'Ch14P', 'Gold dissolution (gold+quintessence, balneum+putrefaction)'),
    ('f79r', 'Ch12M', 'Mercury sublimation to elixir (mercury-water+stone-water)'),
    ('f82r', 'Ch22M', 'Lunaria maceration (lunaria+flesh, sealed 3 days)'),
    ('f76v', 'Ch15M', 'Ferment conversion (join H, bind)'),
    ('f103r', 'Ch16M', 'Ferment multiplication (chambers B+E+G, balneum)'),
    ('f77v', 'Ch27M', 'Furnace specification (5 furnaces, 3 fire types)'),
    ('f81v', 'Ch18M', 'Potable gold (mercury-water+gold, cohobation, rectification)'),
    ('f112r', 'Ch11M', 'Red mercury tincture (ruby liquor, cohobation, calcination)'),
    ('f112v', 'Ch1M', 'Lunaria to quicksilver (lunaria liquor, separation)'),
    ('f116r', 'Ch4M', 'Fixation (sublimated substance, fusibility test, quicksilver)'),
    ('f78v', 'Ch14M', 'Composite ferments (mercury-water+sulfur, dissolve/congeal/rubify)'),
    ('f83r', 'Ch9P', 'First distillation (grind D+C, sawdust fire, graduated)'),
    ('f108r', 'Ch16P', 'Element separation (putrefied composite, balneum then ash)'),
    ('f107r', 'Ch44M', 'Quicksilver coagulation (lead earth+quicksilver+sulfur)'),
    ('f80r', 'Ch21-25M', 'Animal ash chain (capon flesh+lunaria+bones)'),
    ('f82v', 'Ch28M', 'Vessel specification (cover+alembic+cucurbit)'),
    ('f66r', 'Ch24P', 'Fixation (repeated sublimation, escalating fire)'),
]

for folio, chapter, recipe in FOLIOS:
    toks = [t for t in all_b if t.folio == folio]

    # Build line index
    lines = defaultdict(list)
    for t in toks:
        lines[int(t.line)].append(t)

    # Find dark tokens with context
    dark_tokens = []
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            ln = int(t.line)
            line_words = [x.word for x in lines[ln]]
            pos_in_line = line_words.index(t.word) if t.word in line_words else -1

            # Get surrounding context (2 tokens before, 2 after)
            before = line_words[max(0,pos_in_line-2):pos_in_line]
            after = line_words[pos_in_line+1:pos_in_line+3]

            a = morph.atomize(t.word)
            dark_tokens.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': a.prefix or '-',
                'suffix': m.suffix or '-',
                'line': ln,
                'par_initial': t.par_initial,
                'line_initial': t.line_initial,
                'before': before,
                'after': after,
            })

    if not dark_tokens:
        continue

    # Group by dark middle
    by_middle = defaultdict(list)
    for dt in dark_tokens:
        by_middle[dt['middle']].append(dt)

    print("=" * 100)
    print(f"  {folio} | {chapter} | {recipe}")
    print(f"  {len(dark_tokens)} dark tokens, {len(by_middle)} unique dark MIDDLEs, {len(toks)} total tokens")
    print("=" * 100)

    for mid in sorted(by_middle.keys(), key=lambda m: -len(by_middle[m])):
        entries = by_middle[mid]
        print(f"\n  DARK MIDDLE: {mid} (x{len(entries)})")
        for dt in entries:
            pfx = dt['prefix']
            sfx = dt['suffix']
            before_str = ' '.join(dt['before']) if dt['before'] else '(start)'
            after_str = ' '.join(dt['after']) if dt['after'] else '(end)'
            pos_tags = []
            if dt['par_initial']:
                pos_tags.append('PAR-INIT')
            if dt['line_initial']:
                pos_tags.append('LINE-INIT')
            pos_str = f" [{','.join(pos_tags)}]" if pos_tags else ''
            print(f"    L{dt['line']:>2d}: ...{before_str} [{pfx}+{mid}+{sfx}] {after_str}...{pos_str}")

    print()

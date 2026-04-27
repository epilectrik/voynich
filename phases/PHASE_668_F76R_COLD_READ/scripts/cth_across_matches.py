"""
Where does the observer-exclusive MIDDLE 'ecth'/'cth' appear across
matched folios? Does it correlate with recipe sections that describe
observing a transfer or deposition?

Also check the other top observer MIDDLEs for cross-folio patterns.
"""
import sys, io, json
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

MATCHED = {
    'f75r': 'III.19 aqua vitae (9x reflux, honey+wax)',
    'f76r': 'II.16 element separation (silver-plate test)',
    'f84r': 'II.12 gold dissolution (balneum + putrefaction)',
    'f79r': 'III.12 mercury sublimation -> elixir',
    'f82r': 'III.22 lunaria maceration (3-day sealed)',
    'f103r': 'III.16 ferment multiplication (multi-chamber)',
    'f76v': 'III.15 ferment conversion (join H + bind)',
    'f77v': 'III.27 furnace specification',
    'f81v': 'III.18 potable gold / water of life',
    'f82v': 'III.28 vessel specification',
    'f112r': 'III.11 red mercury tincture (cohobation)',
    'f112v': 'III.1 lunaria -> quicksilver (pipeline origin)',
    'f116r': 'III.4 fixation / fusibility test',
    'f107r': 'III.44 quicksilver coagulation',
    'f80r': 'III.21-25 animal ash chain',
}

OBSERVE = {'ch', 'sh'}
TARGET_MIDDLES = ['ecth', 'cth', 'ckh', 'cfh', 'eoke', 'cthh', 'ecthe']

# Collect all observer MIDDLEs per folio, with line positions
folio_obs = defaultdict(list)
folio_total_obs = Counter()

for t in tx.currier_b():
    a = morph.atomize(t.word)
    if a.prefix not in OBSERVE:
        continue
    mid = morph.extract(t.word).middle
    if not mid:
        continue
    folio_obs[t.folio].append({
        'line': t.line,
        'word': t.word,
        'prefix': a.prefix,
        'middle': mid,
    })
    folio_total_obs[t.folio] += 1

# Report target MIDDLEs on matched folios
print('=== Transfer/observation MIDDLEs across matched folios ===\n')

for target in TARGET_MIDDLES:
    print(f'--- MIDDLE: {target} ---')
    found_any = False
    for folio in sorted(MATCHED.keys()):
        hits = [o for o in folio_obs[folio] if o['middle'] == target]
        total = folio_total_obs[folio]
        if hits:
            found_any = True
            lines = [h['line'] for h in hits]
            words = [f"{h['prefix']}:{h['word']}" for h in hits]
            # Get total lines on this folio
            def line_num(s):
                return int(''.join(c for c in str(s) if c.isdigit()) or '0')
            all_lines = set(line_num(o['line']) for o in folio_obs[folio])
            max_line = max(all_lines) if all_lines else 0
            min_line = min(all_lines) if all_lines else 0
            lines_int = [line_num(l) for l in lines]
            pct_positions = [f'{(l - min_line)/(max_line - min_line)*100:.0f}%'
                           if max_line > min_line else '?' for l in lines_int]
            print(f'  {folio} ({MATCHED[folio][:45]})')
            print(f'    n={len(hits)}/{total} obs tokens  lines={lines}  positions={pct_positions}')
            for h in hits[:5]:
                print(f'      L{h["line"]} {h["word"]:<20s} [{h["prefix"]}]')
    if not found_any:
        print(f'  (not found on any matched folio)')
    print()

# Also: what's the corpus-wide folio distribution of ecth/cth?
print('=== ecth folio distribution (all Currier B) ===')
ecth_folios = Counter()
cth_folios = Counter()
for folio, obs_list in folio_obs.items():
    for o in obs_list:
        if o['middle'] == 'ecth':
            ecth_folios[folio] += 1
        if o['middle'] == 'cth':
            cth_folios[folio] += 1

print(f'\necth: {sum(ecth_folios.values())} tokens across {len(ecth_folios)} folios')
for f, n in ecth_folios.most_common(15):
    matched = ' *MATCHED*' if f in MATCHED else ''
    recipe = f' ({MATCHED[f][:40]})' if f in MATCHED else ''
    print(f'  {f}: {n}{matched}{recipe}')

print(f'\ncth: {sum(cth_folios.values())} tokens across {len(cth_folios)} folios')
for f, n in cth_folios.most_common(15):
    matched = ' *MATCHED*' if f in MATCHED else ''
    recipe = f' ({MATCHED[f][:40]})' if f in MATCHED else ''
    print(f'  {f}: {n}{matched}{recipe}')

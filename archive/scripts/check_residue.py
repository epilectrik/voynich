"""Check the non-EVA-valid residue from FG-3 test."""
import csv
from pathlib import Path

BASE = Path(r'C:\git\voynich')
TRANSCRIPTION = BASE / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load data
data = []
with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t', quotechar='"')
    for row in reader:
        data.append(row)

# Get B folios
b_folios = sorted(set(row['folio'] for row in data if row.get('language') == 'B'))

# Known prefixes
HT_PREFIXES = ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'do', 'ta',
               'ke', 'al', 'ko', 'se', 'to', 'yd', 'od', 'pk', 'dk', 'sk']
HT_EXTENDED = ['psh', 'tsh', 'ksh', 'ksch', 'pch', 'tch', 'dch', 'fch', 'rch', 'sch',
               'po', 'te', 'ps', 'ts', 'ks', 'ds', 'ckh', 'cth', 'cph', 'cks']
B_GRAMMAR_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'ar', 'or', 'dy']
ALL_KNOWN = HT_PREFIXES + HT_EXTENDED + B_GRAMMAR_PREFIXES

eva_glyphs = set('aeiodychkstlopqfrn')

anomalous = []
for folio in b_folios:
    tokens = [row['word'] for row in data if row['folio'] == folio]
    if not tokens:
        continue
    first = tokens[0]
    has_known = any(first.startswith(p) for p in ALL_KNOWN)
    if not has_known:
        is_eva_valid = all(c in eva_glyphs for c in first) and len(first) >= 2
        anomalous.append((folio, first, is_eva_valid))

print(f'Total anomalous starts: {len(anomalous)}')
print(f'EVA-valid: {sum(1 for _,_,v in anomalous if v)}')
print(f'Non-EVA-valid: {sum(1 for _,_,v in anomalous if not v)}')
print()
print('Non-EVA-valid tokens:')
for folio, token, valid in anomalous:
    if not valid:
        bad_chars = [c for c in token if c not in eva_glyphs]
        print(f'  {folio}: "{token}" (non-EVA chars: {bad_chars})')

print()
print('All anomalous (for reference):')
for folio, token, valid in anomalous:
    status = 'EVA-valid' if valid else 'NON-EVA'
    print(f'  {folio}: "{token}" [{status}]')

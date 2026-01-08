#!/usr/bin/env python3
"""
Verify if the two transcriptions are the SAME TEXT with different encoding,
or DIFFERENT readings of the manuscript.
"""
import re
from collections import Counter

with open('data/transcriptions/voynich_eva.txt', 'r', encoding='utf-8', errors='replace') as f:
    ours = f.read()
with open('data/transcriptions/ZL_official.txt', 'r', encoding='utf-8', errors='replace') as f:
    zl = f.read()

out = open('validity_report.txt', 'w', encoding='utf-8')

out.write('='*60 + '\n')
out.write('TRANSCRIPTION VALIDITY ANALYSIS\n')
out.write('='*60 + '\n\n')

# Test 1: Word count per folio
out.write('TEST 1: Word counts per folio\n')
out.write('-'*40 + '\n')

our_folio_words = {}
for m in re.finditer(r'<(\d+[rv]\d*)\.(\d+)>([^<]+)', ours):
    folio = m.group(1)
    text = m.group(3)
    words = [w for w in re.split(r'[.\s,]+', text) if w and w not in '-=']
    our_folio_words[folio] = our_folio_words.get(folio, 0) + len(words)

zl_folio_words = {}
for m in re.finditer(r'<f(\d+[rv]\d*)\.(\d+)[^>]*>([^<]+)', zl):
    folio = m.group(1)
    text = m.group(3)
    text = re.sub(r'\[[^\]]+\]', '', text)
    text = re.sub(r'\{[^}]+\}', '', text)
    words = [w for w in re.split(r'[.\s,]+', text) if w and w not in '-=']
    zl_folio_words[folio] = zl_folio_words.get(folio, 0) + len(words)

matches = close = mismatch = 0
for folio in sorted(set(our_folio_words.keys()) & set(zl_folio_words.keys())):
    ours_count = our_folio_words[folio]
    zl_count = zl_folio_words[folio]
    if ours_count == zl_count:
        matches += 1
    elif abs(ours_count - zl_count) / max(ours_count, zl_count) < 0.1:
        close += 1
    else:
        mismatch += 1
        if mismatch <= 10:
            out.write(f'  MISMATCH: {folio} - Ours: {ours_count}, ZL: {zl_count}\n')

total = matches + close + mismatch
out.write(f'\nExact matches: {matches}/{total} ({100*matches/total:.1f}%)\n')
out.write(f'Close (within 10%): {close}/{total} ({100*close/total:.1f}%)\n')
out.write(f'Mismatch: {mismatch}/{total} ({100*mismatch/total:.1f}%)\n')

# Test 2: First word comparison
out.write('\n' + '='*60 + '\n')
out.write('TEST 2: First word of each folio (position-aligned)\n')
out.write('-'*40 + '\n\n')

for folio_num in ['1r', '1v', '2r', '2v', '3r', '3v', '4r', '4v', '5r', '5v']:
    our_match = re.search(rf'<{folio_num}\.1>([^<]+)', ours)
    zl_match = re.search(rf'<f{folio_num}\.1[^>]*>([^<]+)', zl)
    if our_match and zl_match:
        our_text = our_match.group(1).strip()
        zl_text = re.sub(r'<%>', '', zl_match.group(1).strip())
        zl_text = re.sub(r'\[[^\]]+\]', '', zl_text)
        our_word1 = our_text.split('.')[0] if '.' in our_text else our_text[:10]
        zl_word1 = zl_text.split('.')[0] if '.' in zl_text else zl_text[:10]
        out.write(f'{folio_num}: OURS="{our_word1:15}" ZL="{zl_word1:15}"\n')

# Test 3: Character mapping
out.write('\n' + '='*60 + '\n')
out.write('TEST 3: Character mapping derivation\n')
out.write('-'*40 + '\n')

word_pairs = []
for m in re.finditer(r'<(\d+[rv]\d*)\.(\d+)>([^<]+)', ours):
    folio, line, text = m.groups()
    our_words = [w for w in re.split(r'[.\s,]+', text) if w and len(w) > 2]
    zl_match = re.search(rf'<f{folio}\.{line}[^>]*>([^<]+)', zl)
    if zl_match:
        zl_text = re.sub(r'<%>', '', zl_match.group(1))
        zl_text = re.sub(r'\[[^\]]+\]', '', zl_text)
        zl_words = [w for w in re.split(r'[.\s,]+', zl_text) if w and len(w) > 2]
        if len(our_words) == len(zl_words):
            for ow, zw in zip(our_words, zl_words):
                if len(ow) == len(zw):
                    word_pairs.append((ow, zw))

char_map = {}
for our_word, zl_word in word_pairs[:1000]:
    if len(our_word) == len(zl_word):
        for oc, zc in zip(our_word, zl_word):
            if oc not in char_map:
                char_map[oc] = Counter()
            char_map[oc][zc] += 1

out.write(f'\nFound {len(word_pairs)} word pairs with matching lengths\n\n')

consistent = inconsistent = 0
if char_map:
    out.write('Derived mapping (our char -> most common ZL char):\n')
    for oc in sorted(char_map.keys()):
        counts = char_map[oc]
        total_c = sum(counts.values())
        best = counts.most_common(1)[0]
        pct = 100 * best[1] / total_c
        if pct > 50:
            consistent += 1
            marker = 'OK'
        else:
            inconsistent += 1
            marker = 'INCONSISTENT'
        out.write(f"  '{oc}' -> '{best[0]}' ({pct:.0f}% of {total_c}) [{marker}]\n")
    out.write(f'\nConsistent: {consistent}, Inconsistent: {inconsistent}\n')

# VERDICT
out.write('\n' + '='*60 + '\n')
out.write('VERDICT\n')
out.write('='*60 + '\n\n')

word_match_pct = 100 * (matches + close) / total if total > 0 else 0

if word_match_pct > 90 and consistent > inconsistent:
    out.write('STATUS: SAME TEXT, DIFFERENT ENCODING\n\n')
    out.write('PROJECT IMPACT: VALID - structural patterns preserved\n')
elif word_match_pct > 70:
    out.write('STATUS: PARTIALLY ALIGNED\n\n')
    out.write('PROJECT IMPACT: LIKELY VALID\n')
else:
    out.write('STATUS: SIGNIFICANTLY DIFFERENT\n\n')
    out.write('PROJECT IMPACT: REQUIRES REVIEW\n')

out.close()
print('Report written to validity_report.txt')

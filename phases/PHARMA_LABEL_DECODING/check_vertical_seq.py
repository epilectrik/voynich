"""Check if f49v vertical character sequence forms Currier A tokens."""
import csv

# Load Currier A vocabulary
a_vocab = set()
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H' and row.get('language') == 'A':
            word = row.get('word', '')
            if word and word != '???':
                a_vocab.add(word)

# The vertical sequence from f49v (illegibles removed)
seq = 'foryekspoyepoyedysky'

print(f'Vertical sequence (illegibles removed): {seq}')
print(f'Length: {len(seq)} characters')
print(f'Currier A vocabulary size: {len(a_vocab)}')
print()

# Find all substrings that match A vocabulary
matches = []
for length in range(2, 12):
    for i in range(len(seq) - length + 1):
        sub = seq[i:i+length]
        if sub in a_vocab:
            matches.append((sub, i, length))

print('Substrings found in Currier A vocabulary:')
if matches:
    for w, p, l in sorted(set(matches), key=lambda x: (-x[2], x[1])):
        print(f'  {w:12} (len={l}) at position {p}')
else:
    print('  None found!')

# Also check the original sequence with illegibles as potential breaks
print()
print('Original sequence with illegibles (*):')
orig = ['f', 'o', 'r', 'y', 'e', '*', 'k', 's', 'p', 'o', '*', 'y', 'e', '*', '*', 'p', 'o', '*', 'y', 'e', '*', 'd', 'y', 's', 'k', 'y']
print(' '.join(orig))
print()

# Split by illegibles and check each segment
segments = ''.join(orig).split('*')
segments = [s for s in segments if s]  # remove empty
print('Segments split by illegible marks:')
for i, seg in enumerate(segments):
    in_vocab = 'YES' if seg in a_vocab else 'no'
    print(f'  {i+1}. "{seg}" - in A vocab: {in_vocab}')

# Check if any segment is a valid token
print()
print('Segment token matches:')
for seg in segments:
    if seg in a_vocab:
        print(f'  "{seg}" is a valid Currier A token!')

# Now check f49v transcript
print()
print('=' * 60)
print('f49v TRANSCRIPT TOKENS')
print('=' * 60)

f49v_tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('folio') == 'f49v' and row.get('transcriber') == 'H':
            f49v_tokens.append(row)

print(f'f49v has {len(f49v_tokens)} tokens (H transcriber)')
print()

# Group by line
from collections import defaultdict
by_line = defaultdict(list)
for t in f49v_tokens:
    by_line[t.get('line_number')].append(t.get('word'))

print('Tokens by line:')
for line_num in sorted(by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    words = by_line[line_num]
    print(f'  Line {line_num:3}: {" ".join(words)}')

# Check placement codes for single-character tokens
print()
print('=' * 60)
print('SINGLE-CHARACTER TOKENS - PLACEMENT ANALYSIS')
print('=' * 60)

single_char_tokens = [t for t in f49v_tokens if len(t.get('word', '')) == 1]
print(f'Found {len(single_char_tokens)} single-character tokens')
print()
print('Char  Line  Placement  Line-Initial?')
print('-' * 40)
for t in single_char_tokens:
    char = t.get('word')
    line = t.get('line_number')
    placement = t.get('placement', 'N/A')
    line_init = t.get('line_initial', '')
    print(f'{char:5} {line:5} {placement:10} {line_init}')

# Check L placement across entire manuscript
print()
print('=' * 60)
print('L PLACEMENT ACROSS MANUSCRIPT')
print('=' * 60)

from collections import Counter
placements = Counter()
l_folios = Counter()
l_tokens_by_folio = defaultdict(list)

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H':
            p = row.get('placement', '')
            placements[p] += 1
            if p == 'L':
                folio = row.get('folio')
                l_folios[folio] += 1
                l_tokens_by_folio[folio].append(row.get('word'))

print('All placement codes (H transcriber):')
for p, c in placements.most_common(15):
    print(f'  {p:10} {c:6}')

print()
print(f'Total folios with L placement: {len(l_folios)}')
print()
print('Folios with L placement:')
for folio, c in l_folios.most_common():
    tokens = l_tokens_by_folio[folio]
    sample = ' '.join(tokens[:8])
    if len(tokens) > 8:
        sample += '...'
    print(f'  {folio}: {c} tokens - {sample}')

# Deep comparison of f49v and f76r
print()
print('=' * 60)
print('f49v vs f76r COMPARISON')
print('=' * 60)

# Reload with full data
all_tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H':
            all_tokens.append(row)

f49v_all = [t for t in all_tokens if t.get('folio') == 'f49v']
f76r_all = [t for t in all_tokens if t.get('folio') == 'f76r']

print(f'\nf49v: {len(f49v_all)} total tokens, Currier: {f49v_all[0].get("language") if f49v_all else "?"}')
print(f'f76r: {len(f76r_all)} total tokens, Currier: {f76r_all[0].get("language") if f76r_all else "?"}')

# L-placement characters
f49v_L = [t.get('word') for t in f49v_all if t.get('placement') == 'L']
f76r_L = [t.get('word') for t in f76r_all if t.get('placement') == 'L']

print(f'\nf49v L-placement chars ({len(f49v_L)}): {" ".join(f49v_L)}')
print(f'f76r L-placement chars ({len(f76r_L)}): {" ".join(f76r_L)}')

# Character inventory comparison
f49v_chars = set(c for c in f49v_L if c != '*')
f76r_chars = set(c for c in f76r_L if c != '*')
print(f'\nf49v unique chars: {sorted(f49v_chars)}')
print(f'f76r unique chars: {sorted(f76r_chars)}')
print(f'Overlap: {sorted(f49v_chars & f76r_chars)}')
print(f'Only in f49v: {sorted(f49v_chars - f76r_chars)}')
print(f'Only in f76r: {sorted(f76r_chars - f76r_chars)}')

# Get the P-placement (regular text) tokens
f49v_P = [t.get('word') for t in f49v_all if t.get('placement') == 'P']
f76r_P = [t.get('word') for t in f76r_all if t.get('placement') == 'P']

print(f'\n--- Regular text (P placement) ---')
print(f'f49v: {len(f49v_P)} tokens')
print(f'f76r: {len(f76r_P)} tokens')

# Vocabulary comparison
f49v_vocab = set(f49v_P)
f76r_vocab = set(f76r_P)

# Load all A vocab for comparison
all_a_tokens = [t for t in all_tokens if t.get('language') == 'A']
all_a_vocab = set(t.get('word') for t in all_a_tokens)

# Unique to these folios
f49v_unique = f49v_vocab - (all_a_vocab - f49v_vocab)
f76r_unique = f76r_vocab - (all_a_vocab - f76r_vocab)

# Actually calculate what's ONLY on these folios
vocab_by_folio = defaultdict(set)
for t in all_a_tokens:
    vocab_by_folio[t.get('folio')].add(t.get('word'))

f49v_exclusive = set()
for word in f49v_vocab:
    appears_elsewhere = any(word in vocab_by_folio[f] for f in vocab_by_folio if f != 'f49v')
    if not appears_elsewhere:
        f49v_exclusive.add(word)

f76r_exclusive = set()
for word in f76r_vocab:
    appears_elsewhere = any(word in vocab_by_folio[f] for f in vocab_by_folio if f != 'f76r')
    if not appears_elsewhere:
        f76r_exclusive.add(word)

print(f'\nf49v exclusive vocabulary (not on any other A folio): {len(f49v_exclusive)}')
if f49v_exclusive:
    print(f'  {sorted(f49v_exclusive)[:20]}')

print(f'\nf76r exclusive vocabulary (not on any other folio): {len(f76r_exclusive)}')
if f76r_exclusive:
    print(f'  {sorted(f76r_exclusive)[:20]}')

# Shared between f49v and f76r
shared = f49v_vocab & f76r_vocab
print(f'\nShared vocabulary between f49v and f76r: {len(shared)} tokens')

# PREFIX distribution
def get_prefix(word):
    prefixes = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or', 'ar', 'al', 'da', 'ct']
    for p in prefixes:
        if word.startswith(p):
            return p
    return 'other'

f49v_prefixes = Counter(get_prefix(w) for w in f49v_P if w and w != '???')
f76r_prefixes = Counter(get_prefix(w) for w in f76r_P if w and w != '???')

print(f'\n--- PREFIX distribution ---')
print('PREFIX     f49v    f76r')
for p in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'other']:
    f49v_pct = f49v_prefixes[p] / len(f49v_P) * 100 if f49v_P else 0
    f76r_pct = f76r_prefixes[p] / len(f76r_P) * 100 if f76r_P else 0
    print(f'{p:10} {f49v_pct:5.1f}%   {f76r_pct:5.1f}%')

# What placements does f76r actually have?
print()
print('=' * 60)
print('f76r PLACEMENT BREAKDOWN')
print('=' * 60)
f76r_placements = Counter(t.get('placement') for t in f76r_all)
print('Placement distribution:')
for p, c in f76r_placements.most_common():
    print(f'  {p}: {c} tokens')

# Show some f76r content by placement
print('\nf76r content by placement:')
for placement in ['L', 'C', 'R', 'S', 'R1', 'R2']:
    tokens = [t.get('word') for t in f76r_all if t.get('placement') == placement]
    if tokens:
        sample = ' '.join(tokens[:10])
        print(f'  {placement}: {sample}{"..." if len(tokens) > 10 else ""}')

# f49v exclusive words analysis
print()
print('=' * 60)
print('f49v EXCLUSIVE VOCABULARY ANALYSIS')
print('=' * 60)
print(f'f49v has {len(f49v_exclusive)} words found NOWHERE else in Currier A:')
for word in sorted(f49v_exclusive):
    print(f'  {word}')

# Check if these exclusive words share unusual patterns
print('\nPattern analysis of exclusive words:')
unusual_chars = Counter()
for word in f49v_exclusive:
    for char in word:
        unusual_chars[char] += 1
print('Character frequency in exclusive vocabulary:')
for char, count in unusual_chars.most_common(15):
    print(f'  {char}: {count}')

# Compare f49v to typical A folio vocabulary size
a_folio_vocab_sizes = {}
for folio, vocab in vocab_by_folio.items():
    # Check if folio is A
    folio_lang = None
    for t in all_tokens:
        if t.get('folio') == folio:
            folio_lang = t.get('language')
            break
    if folio_lang == 'A':
        a_folio_vocab_sizes[folio] = len(vocab)

print(f'\n--- Currier A folio vocabulary sizes ---')
print(f'Mean: {sum(a_folio_vocab_sizes.values())/len(a_folio_vocab_sizes):.1f}')
print(f'f49v: {a_folio_vocab_sizes.get("f49v", 0)}')
print(f'f49v rank: #{sorted(a_folio_vocab_sizes.values(), reverse=True).index(a_folio_vocab_sizes.get("f49v", 0)) + 1} of {len(a_folio_vocab_sizes)}')

# What IS f76r?
print()
print('=' * 60)
print('WHAT IS f76r?')
print('=' * 60)

# Get f76r metadata
f76r_sample = f76r_all[0] if f76r_all else {}
print(f'Folio: f76r')
print(f'Section: {f76r_sample.get("section")}')
print(f'Quire: {f76r_sample.get("quire")}')
print(f'Language: {f76r_sample.get("language")}')
print(f'Total tokens: {len(f76r_all)}')

# Compare to AZC folios
print('\n--- Token counts: f76r vs AZC folios ---')
azc_folios = set()
for t in all_tokens:
    if t.get('language') not in ['A', 'B']:
        azc_folios.add(t.get('folio'))

# Actually check which folios are unclassified (AZC)
azc_token_counts = {}
b_token_counts = {}
for t in all_tokens:
    folio = t.get('folio')
    lang = t.get('language')
    if lang == 'B':
        b_token_counts[folio] = b_token_counts.get(folio, 0) + 1
    elif lang not in ['A', 'B'] and lang:
        azc_token_counts[folio] = azc_token_counts.get(folio, 0) + 1

print(f'f76r tokens: {len(f76r_all)}')
print(f'f76r is classified as: {f76r_sample.get("language")}')

if azc_token_counts:
    print(f'\nAZC folio token counts (top 10):')
    for folio, count in sorted(azc_token_counts.items(), key=lambda x: -x[1])[:10]:
        print(f'  {folio}: {count}')

print(f'\nCurrier B folio token counts (top 10):')
for folio, count in sorted(b_token_counts.items(), key=lambda x: -x[1])[:10]:
    marker = ' <-- f76r' if folio == 'f76r' else ''
    print(f'  {folio}: {count}{marker}')

# What does the R placement mean for f76r?
print('\n--- f76r line structure ---')
f76r_by_line = defaultdict(list)
for t in f76r_all:
    f76r_by_line[t.get('line_number')].append({
        'word': t.get('word'),
        'placement': t.get('placement')
    })

print(f'Number of lines: {len(f76r_by_line)}')
print('\nFirst 10 lines:')
for line_num in sorted(f76r_by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0)[:10]:
    tokens = f76r_by_line[line_num]
    placements = set(t['placement'] for t in tokens)
    words = ' '.join(t['word'] for t in tokens)
    print(f'  Line {line_num:3} [{",".join(placements)}]: {words[:60]}{"..." if len(words) > 60 else ""}')

# Which lines have L markers on f76r?
print('\n--- f76r L-marker lines ---')
l_lines = []
for line_num, tokens in f76r_by_line.items():
    l_tokens = [t for t in tokens if t['placement'] == 'L']
    if l_tokens:
        l_char = l_tokens[0]['word']
        other_words = [t['word'] for t in tokens if t['placement'] != 'L']
        l_lines.append((int(line_num) if line_num.isdigit() else 0, line_num, l_char, other_words))

print(f'Lines with L markers: {len(l_lines)}')
for _, line_num, l_char, words in sorted(l_lines):
    print(f'  Line {line_num:3}: [{l_char}] {" ".join(words[:6])}...')

# Check spacing pattern
print('\nLine number pattern:')
line_nums = [x[0] for x in sorted(l_lines)]
print(f'  L-marker lines: {line_nums}')
if len(line_nums) > 1:
    gaps = [line_nums[i+1] - line_nums[i] for i in range(len(line_nums)-1)]
    print(f'  Gaps between: {gaps}')

# Compare f49v - every line has an L marker
print('\n--- f49v L-marker pattern ---')
f49v_by_line = defaultdict(list)
for t in f49v_all:
    f49v_by_line[t.get('line_number')].append({
        'word': t.get('word'),
        'placement': t.get('placement')
    })

f49v_l_lines = []
for line_num, tokens in f49v_by_line.items():
    l_tokens = [t for t in tokens if t['placement'] == 'L']
    if l_tokens:
        f49v_l_lines.append(int(line_num) if line_num.isdigit() else 0)

print(f'f49v: {len(f49v_l_lines)} lines with L markers out of {len(f49v_by_line)} total lines')
print(f'f76r: {len(l_lines)} lines with L markers out of {len(f76r_by_line)} total lines')

# Full L-placement analysis across manuscript
print()
print('=' * 60)
print('FULL L-PLACEMENT (LABEL) ANALYSIS')
print('=' * 60)

# Gather all L-placement tokens
l_tokens_all = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H' and row.get('placement', '').startswith('L'):
            l_tokens_all.append(row)

print(f'Total L-placement tokens (H track): {len(l_tokens_all)}')

# Separate single-char vs multi-char labels
single_char_labels = [t for t in l_tokens_all if len(t.get('word', '')) == 1]
multi_char_labels = [t for t in l_tokens_all if len(t.get('word', '')) > 1]

print(f'Single-character labels: {len(single_char_labels)} ({len(single_char_labels)/len(l_tokens_all)*100:.1f}%)')
print(f'Multi-character labels: {len(multi_char_labels)} ({len(multi_char_labels)/len(l_tokens_all)*100:.1f}%)')

# Which folios have single-char labels?
single_char_by_folio = defaultdict(list)
for t in single_char_labels:
    single_char_by_folio[t.get('folio')].append(t.get('word'))

print(f'\nFolios with single-character labels: {len(single_char_by_folio)}')
print('Folio        Count  Chars')
print('-' * 40)
for folio, chars in sorted(single_char_by_folio.items(), key=lambda x: -len(x[1])):
    print(f'{folio:12} {len(chars):5}  {" ".join(chars[:15])}{"..." if len(chars) > 15 else ""}')

# What are the unique single chars used as labels?
all_single_chars = [t.get('word') for t in single_char_labels]
char_freq = Counter(all_single_chars)
print(f'\nUnique single-character labels: {len(char_freq)}')
print('Character frequency:')
for char, count in char_freq.most_common():
    print(f'  {char}: {count}')

# Compare to the 10 single-char primitives from C085
primitives = set('setdlohckr')
label_chars = set(char_freq.keys())
print(f'\nPrimitives (C085): {sorted(primitives)}')
print(f'Label chars: {sorted(label_chars)}')
print(f'In primitives: {sorted(label_chars & primitives)}')
print(f'NOT in primitives: {sorted(label_chars - primitives)}')

# Deep dive into f49v structure - is this instructional?
print()
print('=' * 60)
print('f49v INSTRUCTIONAL ANALYSIS')
print('=' * 60)

# Get full f49v data with all fields
print('f49v metadata:')
if f49v_all:
    sample = f49v_all[0]
    print(f'  Section: {sample.get("section")}')
    print(f'  Quire: {sample.get("quire")}')
    print(f'  Language: {sample.get("language")}')
    print(f'  Hand: {sample.get("hand")}')

# Show the complete line-by-line structure
print('\nComplete f49v structure (L-char | Line content):')
print('-' * 70)
for line_num in sorted(f49v_by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    tokens = f49v_by_line[line_num]
    l_char = None
    p_words = []
    for t in tokens:
        if t['placement'] == 'L':
            l_char = t['word']
        else:
            p_words.append(t['word'])

    # The margin numbers 1-5 align with positions 2-6 of the L-sequence
    # So line 1 has 'f' (position 1), line 2 has 'o' (position 2, number=1), etc.
    margin_num = ''
    line_int = int(line_num) if line_num.isdigit() else 0
    if 2 <= line_int <= 6:
        margin_num = str(line_int - 1)  # lines 2-6 have margin numbers 1-5

    p_text = ' '.join(p_words)
    print(f'Line {line_num:2} [{l_char or "-":1}] {("["+margin_num+"]") if margin_num else "   "} {p_text[:55]}{"..." if len(p_text) > 55 else ""}')

# What's the relationship between the L-chars and the content?
print()
print('Observations:')
print('- Margin numbers 1-5 appear on lines 2-6')
print('- L-chars on lines 2-6: o, r, y, e, *')
print('- This suggests: "These 5 characters (o,r,y,e,?) are numbered 1-5"')
print()
print('First character is "f" (line 1, no number) - possibly a starting marker?')

# Check if f49v vocabulary appears elsewhere
print()
print('--- f49v Vocabulary Context ---')
# How much of f49v text vocab is shared with rest of A?
f49v_p_vocab = set(t['word'] for t in f49v_all if t.get('placement') == 'P')
other_a_vocab = set()
for t in all_tokens:
    if t.get('language') == 'A' and t.get('folio') != 'f49v':
        other_a_vocab.add(t.get('word'))

shared_with_a = f49v_p_vocab & other_a_vocab
only_f49v = f49v_p_vocab - other_a_vocab

print(f'f49v P-placement vocabulary: {len(f49v_p_vocab)} types')
print(f'Shared with other A folios: {len(shared_with_a)} ({len(shared_with_a)/len(f49v_p_vocab)*100:.1f}%)')
print(f'Exclusive to f49v: {len(only_f49v)} ({len(only_f49v)/len(f49v_p_vocab)*100:.1f}%)')

# NUMERAL SYSTEM ANALYSIS
print()
print('=' * 60)
print('POTENTIAL NUMERAL SYSTEM ANALYSIS')
print('=' * 60)

# The numbered characters
numeral_map = {
    'f': '0',  # f could be 0!
    'o': '1',
    'r': '2',
    'y': '3',
    'e': '4',
    '*': '5'  # illegible but position 5
}

# The full L-character sequence
l_sequence = ['f', 'o', 'r', 'y', 'e', '*', 'k', 's', 'p', 'o', '*', 'y', 'e', '*', '*', 'p', 'o', '*', 'y', 'e', '*', 'd', 'y', 's', 'k', 'y']

print('L-character sequence with numeral substitution:')
print()
print('Pos  Char  Numeral?')
print('-' * 25)
for i, char in enumerate(l_sequence, 1):
    num = numeral_map.get(char, '-')
    print(f'{i:3}  {char:4}  {num}')

# Show the sequence with substitutions
print()
print('Sequence with numerals substituted:')
substituted = [numeral_map.get(c, c) for c in l_sequence]
print(' '.join(substituted))

# Look for patterns in the numeral positions
print()
print('Grouping by apparent structure:')
# Group based on non-numeral breaks
current_group = []
groups = []
for c in l_sequence:
    if c in numeral_map:
        current_group.append(numeral_map[c])
    else:
        if current_group:
            groups.append(''.join(current_group))
            current_group = []
        groups.append(f'[{c}]')
if current_group:
    groups.append(''.join(current_group))

print(' '.join(groups))

# Count occurrences of each numeral character
print()
print('Numeral character frequency in L-column:')
for char, num in numeral_map.items():
    count = l_sequence.count(char)
    print(f'  {char} (={num}): {count} occurrences')

# What numbers could these represent?
print()
print('Possible number interpretations:')
print('If reading numeral groups as multi-digit numbers:')
numeral_groups = [g for g in groups if not g.startswith('[')]
for g in numeral_groups:
    if len(g) > 0:
        # Could be positional (like 12345) or additive
        as_positional = g  # e.g., "12345"
        as_additive = sum(int(d) for d in g)  # e.g., 1+2+3+4+5=15
        print(f'  "{g}" - positional: {g}, additive: {as_additive}')

# With f=0, analyze the base-6 pattern
print()
print('=' * 60)
print('BASE-6 ANALYSIS (f=0, o=1, r=2, y=3, e=4, *=5)')
print('=' * 60)

print('\nFirst 6 characters form the KEY: f o r y e * = 0 1 2 3 4 5')
print('This is a complete base-6 digit demonstration!')
print()

# Check repeating patterns
print('Looking for repeating digit patterns:')
# Convert to digits
digit_seq = []
marker_positions = []
for i, c in enumerate(l_sequence):
    if c in numeral_map:
        digit_seq.append((i, numeral_map[c]))
    else:
        marker_positions.append((i, c))

# Find repeating subsequences
digit_only = ''.join(d for _, d in digit_seq)
print(f'Digit-only sequence: {digit_only}')
print()

# Look for repeated patterns
from collections import Counter
# Check for 2-grams, 3-grams, 4-grams, 5-grams
for n in range(2, 6):
    ngrams = [digit_only[i:i+n] for i in range(len(digit_only) - n + 1)]
    ngram_counts = Counter(ngrams)
    repeats = [(ng, c) for ng, c in ngram_counts.items() if c > 1]
    if repeats:
        print(f'{n}-grams that repeat:')
        for ng, c in sorted(repeats, key=lambda x: -x[1]):
            print(f'  "{ng}" appears {c} times')

# Note about r=2
print()
print('CRITICAL OBSERVATION:')
print(f'  r (=2) appears only {l_sequence.count("r")} time(s) in the sequence')
print(f'  This is ONLY in the initial key "012345"')
print(f'  The digit "2" is ABSENT from all subsequent numbers!')
print()

# What about the markers?
print('Non-numeral markers in sequence:')
markers_only = [c for c in l_sequence if c not in numeral_map]
print(f'  Markers: {markers_only}')
print(f'  Unique markers: {sorted(set(markers_only))}')

# Check: do these characters appear as standalone tokens elsewhere?
print()
print('=' * 60)
print('DO NUMERAL CHARS APPEAR STANDALONE ELSEWHERE?')
print('=' * 60)

numeral_chars = ['o', 'r', 'y', 'e']
non_numeral_chars = ['f', 'k', 's', 'p', 'd']

print('Checking for single-character tokens in main text (P-placement):')
single_char_p_tokens = defaultdict(list)
for t in all_tokens:
    word = t.get('word', '')
    if len(word) == 1 and t.get('placement', '').startswith('P'):
        single_char_p_tokens[word].append(t.get('folio'))

print('\nNumeral candidates (o, r, y, e):')
for char in numeral_chars:
    folios = single_char_p_tokens.get(char, [])
    if folios:
        unique_folios = set(folios)
        print(f'  {char}: {len(folios)} occurrences on {len(unique_folios)} folios: {sorted(unique_folios)[:10]}{"..." if len(unique_folios) > 10 else ""}')
    else:
        print(f'  {char}: NOT FOUND as standalone token')

print('\nNon-numeral markers (f, k, s, p, d):')
for char in non_numeral_chars:
    folios = single_char_p_tokens.get(char, [])
    if folios:
        unique_folios = set(folios)
        print(f'  {char}: {len(folios)} occurrences on {len(unique_folios)} folios: {sorted(unique_folios)[:10]}{"..." if len(unique_folios) > 10 else ""}')
    else:
        print(f'  {char}: NOT FOUND as standalone token')

# Check if these characters commonly START tokens (as prefixes)
print()
print('As token-initial characters (how often do tokens START with these?):')
char_initial_counts = defaultdict(int)
total_tokens = 0
for t in all_tokens:
    word = t.get('word', '')
    if word and t.get('placement', '').startswith('P'):
        total_tokens += 1
        if word[0] in numeral_chars + non_numeral_chars:
            char_initial_counts[word[0]] += 1

print('\nNumeral candidates as token-initial:')
for char in numeral_chars:
    count = char_initial_counts.get(char, 0)
    pct = count / total_tokens * 100 if total_tokens > 0 else 0
    print(f'  {char}-initial: {count:5} ({pct:.2f}%)')

print('\nNon-numeral markers as token-initial:')
for char in non_numeral_chars:
    count = char_initial_counts.get(char, 0)
    pct = count / total_tokens * 100 if total_tokens > 0 else 0
    print(f'  {char}-initial: {count:5} ({pct:.2f}%)')

# PATTERN ANALYSIS: Do lines with same label have similar content?
print()
print('=' * 60)
print('f49v: DO LINES WITH SAME LABEL HAVE SIMILAR CONTENT?')
print('=' * 60)

# Group f49v lines by their L-character
lines_by_label = defaultdict(list)
for line_num in sorted(f49v_by_line.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    tokens = f49v_by_line[line_num]
    l_char = None
    p_words = []
    for t in tokens:
        if t['placement'] == 'L':
            l_char = t['word']
        else:
            p_words.append(t['word'])
    if l_char:
        lines_by_label[l_char].append({
            'line': line_num,
            'words': p_words,
            'text': ' '.join(p_words)
        })

# For each label that appears multiple times, compare the lines
print('Labels that appear multiple times:')
for label, lines in sorted(lines_by_label.items(), key=lambda x: -len(x[1])):
    if len(lines) > 1:
        print(f'\n[{label}] appears {len(lines)} times:')
        for line_data in lines:
            print(f'  Line {line_data["line"]:2}: {line_data["text"][:60]}...')

        # Check for vocabulary overlap between lines with same label
        if len(lines) >= 2:
            vocab_sets = [set(l['words']) for l in lines]
            # Pairwise Jaccard
            if len(vocab_sets) == 2:
                intersection = vocab_sets[0] & vocab_sets[1]
                union = vocab_sets[0] | vocab_sets[1]
                jaccard = len(intersection) / len(union) if union else 0
                print(f'  Vocabulary overlap (Jaccard): {jaccard:.3f}')
                if intersection:
                    print(f'  Shared words: {intersection}')
            else:
                # Multiple lines - check all-way intersection
                common = vocab_sets[0]
                for vs in vocab_sets[1:]:
                    common = common & vs
                print(f'  Words common to ALL {len(lines)} lines: {common if common else "none"}')

# Check PREFIX patterns - do lines with same label have similar PREFIX distributions?
print()
print('PREFIX patterns by label:')

def get_prefix(word):
    prefixes = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or', 'ar', 'al', 'da']
    for p in prefixes:
        if word.startswith(p):
            return p
    return 'other'

for label, lines in sorted(lines_by_label.items(), key=lambda x: -len(x[1])):
    if len(lines) > 1:
        all_words = []
        for l in lines:
            all_words.extend(l['words'])
        prefix_counts = Counter(get_prefix(w) for w in all_words if w)
        total = sum(prefix_counts.values())
        top_prefixes = prefix_counts.most_common(3)
        pct_str = ', '.join(f'{p}:{c/total*100:.0f}%' for p,c in top_prefixes)
        print(f'  [{label}] ({len(lines)} lines, {total} tokens): {pct_str}')

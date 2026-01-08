"""
Test: Are y-, o-, k- tokens in Currier A a separate layer or part of the system?
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Load Currier A tokens with section info
a_tokens = []
a_by_section = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                if word:
                    a_tokens.append((word, section))
                    a_by_section[section].append(word)

print(f'Total Currier A tokens: {len(a_tokens)}')
print(f'Sections: {list(a_by_section.keys())}')

# Identify initial tokens (start with y, o, k, s but NOT a known prefix)
def is_non_prefix_initial(token, initial):
    if not token.startswith(initial):
        return False
    # Check it's not starting with a known prefix
    for p in PREFIXES:
        if token.startswith(p):
            return False
    return True

y_tokens = [(t, s) for t, s in a_tokens if is_non_prefix_initial(t, 'y')]
o_tokens = [(t, s) for t, s in a_tokens if t.startswith('o') and not any(t.startswith(p) for p in ['ok', 'ot', 'ol'])]
k_tokens = [(t, s) for t, s in a_tokens if t.startswith('k') and not t.startswith('ok')]
s_tokens = [(t, s) for t, s in a_tokens if t.startswith('s') and not t.startswith('sh')]

print(f'\n=== NON-PREFIX INITIAL TOKENS ===')
print(f'y- initial: {len(y_tokens)} ({100*len(y_tokens)/len(a_tokens):.1f}%)')
print(f'o- initial (not ok/ot/ol): {len(o_tokens)} ({100*len(o_tokens)/len(a_tokens):.1f}%)')
print(f'k- initial: {len(k_tokens)} ({100*len(k_tokens)/len(a_tokens):.1f}%)')
print(f's- initial (not sh): {len(s_tokens)} ({100*len(s_tokens)/len(a_tokens):.1f}%)')

total_initial = len(y_tokens) + len(o_tokens) + len(k_tokens) + len(s_tokens)
print(f'\nTOTAL non-prefix initials: {total_initial} ({100*total_initial/len(a_tokens):.1f}%)')

# TEST 1: Section distribution - are they section-conditioned like prefixes?
print(f'\n=== TEST 1: SECTION DISTRIBUTION ===')
print('If these are system tokens, they should be section-conditioned.')
print('If they are scribal/human-layer, they should be uniform across sections.\n')

for name, tokens in [('y-', y_tokens), ('k-', k_tokens)]:
    section_dist = Counter(s for t, s in tokens)
    total = len(tokens)
    print(f'{name} by section:')
    for section in sorted(section_dist.keys()):
        count = section_dist[section]
        # Compare to overall section distribution
        section_total = len(a_by_section[section])
        expected_pct = 100 * section_total / len(a_tokens)
        actual_pct = 100 * count / total
        print(f'  {section}: {count} ({actual_pct:.1f}%) [expected {expected_pct:.1f}%]')
    print()

# TEST 2: Do they combine with known prefixes?
print(f'\n=== TEST 2: COMBINATION WITH PREFIXES ===')
print('If y- is an INITIAL slot, tokens like "ychol" should decompose as y- + ch- + ol')

def find_prefix_after(token, initial):
    remainder = token[len(initial):]
    for p in PREFIXES:
        if remainder.startswith(p):
            return p
    return None

y_with_prefix = [(t, find_prefix_after(t, 'y')) for t, s in y_tokens]
has_prefix = sum(1 for t, p in y_with_prefix if p)
print(f'\ny- tokens with PREFIX after y-: {has_prefix}/{len(y_tokens)} ({100*has_prefix/len(y_tokens):.1f}%)')

prefix_counts = Counter(p for t, p in y_with_prefix if p)
print(f'\nWhich prefixes appear after y-:')
for p, count in prefix_counts.most_common():
    print(f'  y + {p}-: {count}')

# TEST 3: Are y- tokens REQUIRED for block identity?
print(f'\n=== TEST 3: BLOCK IDENTITY TEST ===')
print('If we strip y- from tokens, do blocks still have unique identity?')

# For this we need to check if yXXX and XXX ever appear in the same context
y_stripped = set()
for t, s in y_tokens:
    stripped = t[1:]  # Remove y-
    y_stripped.add(stripped)

# How many of these stripped forms also exist as standalone tokens?
all_tokens = set(t for t, s in a_tokens)
overlap = y_stripped.intersection(all_tokens)
print(f'\ny- stripped forms that also exist without y-: {len(overlap)}/{len(y_stripped)}')
print(f'Examples: {list(overlap)[:20]}')

# TEST 4: Most common y- tokens - what do they look like?
print(f'\n=== TEST 4: MOST COMMON INITIAL TOKENS ===')
print('\nMost common y- tokens:')
y_counter = Counter(t for t, s in y_tokens)
for tok, count in y_counter.most_common(15):
    prefix_after = find_prefix_after(tok, 'y')
    print(f'  {tok}: {count}  [y + {prefix_after or "???"}...]')

print('\nMost common k- tokens:')
k_counter = Counter(t for t, s in k_tokens)
for tok, count in k_counter.most_common(15):
    print(f'  {tok}: {count}')

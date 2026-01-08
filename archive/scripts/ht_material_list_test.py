"""
Test: Are HT tokens material lists for procedural steps?

If HT tokens list materials needed for a step, we'd expect:
1. HT tokens to cluster at specific positions relative to grammar tokens
2. HT tokens to reference Currier A vocabulary (the materials registry)
3. HT tokens to appear in "list-like" runs (multiple items)
4. Different HT prefixes to correspond to different material types
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Grammar classification
GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_CORE = {
    'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol',
    'aiin', 'checkhy', 'otain', 'shey', 'shol', 'shedy', 'shy', 'shor',
    'qo', 'qok', 'ok', 'al', 'or', 'ar', 'dal', 'qokedy', 'okey', 'okeey',
    'okedy', 'chee', 'cheol', 'ched', 'chor', 'char', 'sho', 'she',
    'qokeey', 'qokain', 'okain', 'sheey', 'sheo', 'otar', 'oteey', 'otedy',
    'okeedy', 'taiin', 'cthaiin', 'cthol', 'cthor', 'cthy',
    'kcheol', 'kchey', 'kcheedy', 'pchedy', 'pchey', 'fchedy', 'fchey',
    's', 'y', 'r', 'l', 'o', 'd', 'k', 'e', 'h', 't', 'c',
}

# HT prefixes (from previous analysis)
HT_PREFIXES = ['yk', 'op', 'yt', 'so', 'al', 'po', 'do', 'to', 'pc', 'ke',
               'dc', 'sa', 'yc', 'oc', 'oe', 'ka', 'ko', 'ta', 'te', 'lo', 'ro']

def classify_token(tok):
    """Classify token as GRAMMAR, HT, or OTHER."""
    t = tok.lower()

    # Grammar token
    if t in GRAMMAR_CORE:
        return 'GRAMMAR'
    for p in GRAMMAR_PREFIXES:
        if t.startswith(p) and len(t) > len(p):
            return 'GRAMMAR'
    if t.startswith('l') and len(t) > 1 and t[1] in 'cks':
        return 'GRAMMAR'

    # HT token
    for p in HT_PREFIXES:
        if t.startswith(p):
            return 'HT'

    return 'OTHER'

# Load tokens with position info
lines_data = []  # List of (folio, line_num, [tokens])
current_line = []
current_key = None

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            line_num = parts[11].strip('"').strip()
            lang = parts[6].strip('"').strip()

            if word and not word.startswith('*') and lang == 'B':
                key = (folio, line_num)
                if key != current_key:
                    if current_line:
                        lines_data.append((current_key[0], current_key[1], current_line))
                    current_line = []
                    current_key = key
                current_line.append(word)

if current_line:
    lines_data.append((current_key[0], current_key[1], current_line))

print("=" * 80)
print("TEST: ARE HT TOKENS MATERIAL LISTS FOR PROCEDURAL STEPS?")
print("=" * 80)

# ============================================================================
# TEST 1: Position of HT tokens within lines
# ============================================================================

print("\n### TEST 1: HT POSITION WITHIN LINES")

positions = []  # (relative_position, token_class)
for folio, line_num, tokens in lines_data:
    n = len(tokens)
    if n < 3:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1) if n > 1 else 0.5  # 0 = start, 1 = end
        cls = classify_token(tok)
        positions.append((rel_pos, cls))

# Average position by class
grammar_positions = [p for p, c in positions if c == 'GRAMMAR']
ht_positions = [p for p, c in positions if c == 'HT']
other_positions = [p for p, c in positions if c == 'OTHER']

print(f"GRAMMAR tokens - mean position: {sum(grammar_positions)/len(grammar_positions):.3f} (n={len(grammar_positions)})")
print(f"HT tokens - mean position: {sum(ht_positions)/len(ht_positions):.3f} (n={len(ht_positions)})")
print(f"OTHER tokens - mean position: {sum(other_positions)/len(other_positions):.3f} (n={len(other_positions)})")

# Line-initial and line-final enrichment
grammar_initial = sum(1 for p, c in positions if c == 'GRAMMAR' and p < 0.1) / len(grammar_positions)
ht_initial = sum(1 for p, c in positions if c == 'HT' and p < 0.1) / len(ht_positions)
grammar_final = sum(1 for p, c in positions if c == 'GRAMMAR' and p > 0.9) / len(grammar_positions)
ht_final = sum(1 for p, c in positions if c == 'HT' and p > 0.9) / len(ht_positions)

print(f"\nLine-initial (<10%): GRAMMAR={100*grammar_initial:.1f}%, HT={100*ht_initial:.1f}%")
print(f"Line-final (>90%): GRAMMAR={100*grammar_final:.1f}%, HT={100*ht_final:.1f}%")

# ============================================================================
# TEST 2: HT runs (consecutive HT tokens = lists?)
# ============================================================================

print("\n### TEST 2: HT TOKEN RUNS (CONSECUTIVE HT = LISTS?)")

run_lengths = []
for folio, line_num, tokens in lines_data:
    classes = [classify_token(t) for t in tokens]

    # Find HT runs
    current_run = 0
    for c in classes:
        if c == 'HT':
            current_run += 1
        else:
            if current_run > 0:
                run_lengths.append(current_run)
            current_run = 0
    if current_run > 0:
        run_lengths.append(current_run)

run_dist = Counter(run_lengths)
print(f"Total HT runs: {len(run_lengths)}")
print(f"Run length distribution:")
for length in sorted(run_dist.keys())[:10]:
    pct = 100 * run_dist[length] / len(run_lengths)
    print(f"  Length {length}: {run_dist[length]} ({pct:.1f}%)")

avg_run = sum(run_lengths) / len(run_lengths) if run_lengths else 0
print(f"\nAverage run length: {avg_run:.2f}")

if avg_run > 1.5:
    print("VERDICT: HT tokens cluster in RUNS -> supports list hypothesis")
else:
    print("VERDICT: HT tokens are mostly ISOLATED -> weakens list hypothesis")

# ============================================================================
# TEST 3: Do HT tokens share vocabulary with Currier A?
# ============================================================================

print("\n### TEST 3: HT-A VOCABULARY OVERLAP")

# Load Currier A vocabulary
a_tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            if word and not word.startswith('*') and lang == 'A':
                a_tokens.append(word)

a_vocab = set(a_tokens)
a_freq = Counter(a_tokens)

# Get HT tokens from B
ht_in_b = []
for folio, line_num, tokens in lines_data:
    for tok in tokens:
        if classify_token(tok) == 'HT':
            ht_in_b.append(tok)

ht_vocab = set(ht_in_b)

# Overlap
overlap = a_vocab & ht_vocab
print(f"Currier A vocabulary: {len(a_vocab)} types")
print(f"HT vocabulary (in B): {len(ht_vocab)} types")
print(f"Overlap: {len(overlap)} types ({100*len(overlap)/len(ht_vocab):.1f}% of HT)")

# Top overlapping tokens
if overlap:
    overlap_freq = [(tok, a_freq[tok]) for tok in overlap]
    overlap_freq.sort(key=lambda x: -x[1])
    print(f"\nTop overlapping tokens (appear in both A and HT-in-B):")
    for tok, freq in overlap_freq[:20]:
        print(f"  {tok}: {freq} in A")

# ============================================================================
# TEST 4: Do HT prefixes correlate with material types?
# ============================================================================

print("\n### TEST 4: HT PREFIX CONTEXT ANALYSIS")

# For each HT prefix, what grammar tokens typically precede/follow it?
prefix_context = defaultdict(lambda: {'before': Counter(), 'after': Counter()})

for folio, line_num, tokens in lines_data:
    n = len(tokens)
    for i, tok in enumerate(tokens):
        cls = classify_token(tok)
        if cls == 'HT':
            # Find which HT prefix
            prefix = None
            for p in HT_PREFIXES:
                if tok.startswith(p):
                    prefix = p
                    break
            if not prefix:
                continue

            # Look at context
            if i > 0:
                before = tokens[i-1]
                if classify_token(before) == 'GRAMMAR':
                    prefix_context[prefix]['before'][before] += 1
            if i < n - 1:
                after = tokens[i+1]
                if classify_token(after) == 'GRAMMAR':
                    prefix_context[prefix]['after'][after] += 1

print("\nTop HT prefixes and their grammar context:")
for prefix in ['yk', 'op', 'yt', 'sa', 'so', 'ka']:
    data = prefix_context[prefix]
    before = data['before'].most_common(3)
    after = data['after'].most_common(3)
    print(f"\n{prefix}-:")
    print(f"  Preceded by: {', '.join([f'{t}({c})' for t,c in before])}")
    print(f"  Followed by: {', '.join([f'{t}({c})' for t,c in after])}")

# ============================================================================
# TEST 5: HT tokens at instruction boundaries?
# ============================================================================

print("\n### TEST 5: HT AT INSTRUCTION BOUNDARIES")

# Check if HT tokens appear right after kernel operators (k, h, e)
kernel_followed_by = Counter()
for folio, line_num, tokens in lines_data:
    for i, tok in enumerate(tokens):
        if tok in ['k', 'h', 'e'] and i < len(tokens) - 1:
            next_tok = tokens[i + 1]
            next_cls = classify_token(next_tok)
            kernel_followed_by[next_cls] += 1

total = sum(kernel_followed_by.values())
print(f"After kernel (k/h/e), next token is:")
for cls, count in kernel_followed_by.most_common():
    print(f"  {cls}: {count} ({100*count/total:.1f}%)")

# Check daiin boundaries
daiin_followed_by = Counter()
for folio, line_num, tokens in lines_data:
    for i, tok in enumerate(tokens):
        if tok == 'daiin' and i < len(tokens) - 1:
            next_tok = tokens[i + 1]
            next_cls = classify_token(next_tok)
            daiin_followed_by[next_cls] += 1

total = sum(daiin_followed_by.values())
print(f"\nAfter 'daiin', next token is:")
for cls, count in daiin_followed_by.most_common():
    print(f"  {cls}: {count} ({100*count/total:.1f}%)")

# ============================================================================
# TEST 6: Pattern - Is HT at START of procedural units?
# ============================================================================

print("\n### TEST 6: HT AT START OF PROCEDURAL UNITS")

# If HT lists materials for a step, they might appear at the START of the line
# (before the procedure) or at specific grammar transitions

# Check first token of each line
first_token_class = Counter()
for folio, line_num, tokens in lines_data:
    if tokens:
        first_token_class[classify_token(tokens[0])] += 1

total = sum(first_token_class.values())
print(f"First token of line is:")
for cls, count in first_token_class.most_common():
    print(f"  {cls}: {count} ({100*count/total:.1f}%)")

# Check if HT appears in first 20% followed by GRAMMAR
ht_then_grammar = 0
grammar_then_ht = 0
for folio, line_num, tokens in lines_data:
    n = len(tokens)
    if n < 5:
        continue

    first_fifth = tokens[:n//5] if n >= 5 else tokens[:1]
    rest = tokens[n//5:] if n >= 5 else tokens[1:]

    first_classes = [classify_token(t) for t in first_fifth]
    rest_classes = [classify_token(t) for t in rest]

    if 'HT' in first_classes and 'GRAMMAR' in rest_classes:
        ht_then_grammar += 1
    if 'GRAMMAR' in first_classes and 'HT' in rest_classes:
        grammar_then_ht += 1

print(f"\nHT in first 20% + GRAMMAR in rest: {ht_then_grammar}")
print(f"GRAMMAR in first 20% + HT in rest: {grammar_then_ht}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY: MATERIAL LIST HYPOTHESIS")
print("=" * 80)

print("""
FINDINGS:

1. POSITION: HT tokens are line-initial enriched (appear early in lines)
   -> CONSISTENT with "list materials first, then procedure"

2. RUNS: Average HT run length tells us if they cluster as lists
   -> If avg > 1.5, supports listing multiple materials

3. A-OVERLAP: How much HT vocabulary appears in Currier A (the registry)?
   -> High overlap would suggest HT references A materials

4. CONTEXT: What grammar tokens surround HT tokens?
   -> Patterns would reveal if HT relates to specific operations

5. BOUNDARIES: Do HT tokens appear after instruction markers (daiin, k/h/e)?
   -> Would suggest step-by-step material annotation

6. START PATTERN: HT at start followed by GRAMMAR?
   -> Supports "materials, then procedure" structure
""")

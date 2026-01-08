"""
Test: Are HT tokens tracking state changes through procedures?

If HT tracks changing state, we'd expect:
1. Different HT prefixes at different positions in the folio
2. HT prefix sequences that progress (not random)
3. Correlation between HT prefix and nearby grammar context
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

HT_PREFIXES = ['yk', 'op', 'yt', 'so', 'al', 'po', 'do', 'to', 'pc', 'ke',
               'dc', 'sa', 'yc', 'oc', 'oe', 'ka', 'ko', 'ta', 'te', 'lo', 'ro']

GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_CORE = {'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol', 'aiin'}

def get_ht_prefix(tok):
    for p in HT_PREFIXES:
        if tok.startswith(p):
            return p
    return None

def is_grammar(tok):
    if tok in GRAMMAR_CORE:
        return True
    for p in GRAMMAR_PREFIXES:
        if tok.startswith(p) and len(tok) > len(p):
            return True
    return False

# Load by folio with line order
folios = defaultdict(list)  # folio -> [(line_num, [tokens])]

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 11:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            line_num = int(parts[11].strip('"').strip()) if parts[11].strip('"').strip().isdigit() else 0
            lang = parts[6].strip('"').strip()

            if word and not word.startswith('*') and lang == 'B':
                if not folios[folio] or folios[folio][-1][0] != line_num:
                    folios[folio].append((line_num, []))
                folios[folio][-1][1].append(word)

print("=" * 80)
print("TEST: DO HT PREFIXES CHANGE THROUGH FOLIOS?")
print("=" * 80)

# ============================================================================
# TEST 1: HT prefix distribution by position in folio
# ============================================================================

print("\n### TEST 1: HT PREFIX BY FOLIO POSITION")

prefix_by_position = defaultdict(Counter)  # position_bin -> Counter of prefixes

for folio, lines in folios.items():
    n_lines = len(lines)
    if n_lines < 5:
        continue

    for i, (line_num, tokens) in enumerate(lines):
        # Position: 0-4 = first 20%, 5-9 = next 20%, etc.
        pos_bin = int((i / n_lines) * 5)  # 0, 1, 2, 3, 4

        for tok in tokens:
            prefix = get_ht_prefix(tok)
            if prefix:
                prefix_by_position[pos_bin][prefix] += 1

print("Position bins (0=start, 4=end) - top 5 prefixes at each position:")
for pos in range(5):
    data = prefix_by_position[pos]
    top5 = data.most_common(5)
    total = sum(data.values())
    print(f"\nPosition {pos} (n={total}):")
    for p, c in top5:
        print(f"  {p}: {c} ({100*c/total:.1f}%)")

# ============================================================================
# TEST 2: HT prefix sequences within folios
# ============================================================================

print("\n" + "=" * 80)
print("### TEST 2: HT PREFIX TRANSITIONS (Bigrams)")
print("=" * 80)

# Track HT prefix -> next HT prefix transitions
prefix_transitions = Counter()

for folio, lines in folios.items():
    prev_prefix = None
    for line_num, tokens in lines:
        for tok in tokens:
            prefix = get_ht_prefix(tok)
            if prefix:
                if prev_prefix:
                    prefix_transitions[(prev_prefix, prefix)] += 1
                prev_prefix = prefix

print("\nTop HT prefix transitions:")
print(f"{'From':<8} {'To':<8} {'Count':>8}")
print("-" * 30)
for (p1, p2), count in prefix_transitions.most_common(20):
    print(f"{p1:<8} {p2:<8} {count:>8}")

# Check self-transitions (same prefix repeating)
total_transitions = sum(prefix_transitions.values())
self_transitions = sum(count for (p1, p2), count in prefix_transitions.items() if p1 == p2)
print(f"\nSelf-transitions (same prefix): {self_transitions} ({100*self_transitions/total_transitions:.1f}%)")

# ============================================================================
# TEST 3: HT prefix correlation with grammar context
# ============================================================================

print("\n" + "=" * 80)
print("### TEST 3: HT PREFIX × GRAMMAR CONTEXT")
print("=" * 80)

# For each HT prefix, what grammar prefix most commonly precedes it?
ht_preceded_by = defaultdict(Counter)

for folio, lines in folios.items():
    for line_num, tokens in lines:
        for i, tok in enumerate(tokens):
            prefix = get_ht_prefix(tok)
            if prefix and i > 0:
                prev_tok = tokens[i-1]
                for gp in GRAMMAR_PREFIXES:
                    if prev_tok.startswith(gp):
                        ht_preceded_by[prefix][gp] += 1
                        break

print("What grammar prefix precedes each HT prefix?")
print(f"{'HT Prefix':<10} {'Top Grammar Predecessors':<50}")
print("-" * 60)
for ht_p in ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'po']:
    data = ht_preceded_by[ht_p]
    if data:
        top3 = data.most_common(3)
        total = sum(data.values())
        desc = ", ".join([f"{gp}({100*c/total:.0f}%)" for gp, c in top3])
        print(f"{ht_p:<10} {desc:<50}")

# ============================================================================
# TEST 4: Specific HT prefix patterns
# ============================================================================

print("\n" + "=" * 80)
print("### TEST 4: ARE HT PREFIXES FUNCTIONALLY DISTINCT?")
print("=" * 80)

# Hypothesis: Different HT prefixes serve different roles
# yk- might track one thing, sa- another, etc.

# Check position distribution for each prefix
prefix_position_stats = {}
for folio, lines in folios.items():
    n_lines = len(lines)
    if n_lines < 5:
        continue

    for i, (line_num, tokens) in enumerate(lines):
        rel_pos = i / n_lines  # 0 to 1

        for j, tok in enumerate(tokens):
            prefix = get_ht_prefix(tok)
            if prefix:
                if prefix not in prefix_position_stats:
                    prefix_position_stats[prefix] = {'folio_pos': [], 'line_pos': []}
                prefix_position_stats[prefix]['folio_pos'].append(rel_pos)
                line_rel = j / len(tokens) if len(tokens) > 1 else 0.5
                prefix_position_stats[prefix]['line_pos'].append(line_rel)

print("HT prefix positional preferences:")
print(f"{'Prefix':<8} {'Folio Pos':>12} {'Line Pos':>12} {'n':>8}")
print("-" * 45)

for prefix in ['yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'po', 'ke', 'al']:
    if prefix in prefix_position_stats:
        data = prefix_position_stats[prefix]
        folio_mean = sum(data['folio_pos']) / len(data['folio_pos'])
        line_mean = sum(data['line_pos']) / len(data['line_pos'])
        n = len(data['folio_pos'])
        print(f"{prefix:<8} {folio_mean:>12.3f} {line_mean:>12.3f} {n:>8}")

# ============================================================================
# TEST 5: Do HT tokens form a progression through folios?
# ============================================================================

print("\n" + "=" * 80)
print("### TEST 5: HT PROGRESSION CHECK")
print("=" * 80)

# If HT tracks state, we might see progression patterns
# e.g., yk- early -> sa- middle -> so- late

# For each folio, get the sequence of HT prefixes
folio_progressions = []
for folio, lines in folios.items():
    seq = []
    for line_num, tokens in lines:
        for tok in tokens:
            prefix = get_ht_prefix(tok)
            if prefix:
                seq.append(prefix)
    if len(seq) >= 5:
        folio_progressions.append(seq)

# Check first vs last HT prefix in each folio
first_prefix = Counter()
last_prefix = Counter()
for seq in folio_progressions:
    first_prefix[seq[0]] += 1
    last_prefix[seq[-1]] += 1

print("First HT prefix in folios:")
for p, c in first_prefix.most_common(5):
    print(f"  {p}: {c}")

print("\nLast HT prefix in folios:")
for p, c in last_prefix.most_common(5):
    print(f"  {p}: {c}")

# Check if first != last significantly
if first_prefix and last_prefix:
    first_top = first_prefix.most_common(1)[0][0]
    last_top = last_prefix.most_common(1)[0][0]
    print(f"\nMost common first: {first_top}, Most common last: {last_top}")
    if first_top != last_top:
        print("DIFFERENT -> suggests progression through folio")
    else:
        print("SAME -> no clear progression")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

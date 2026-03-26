"""Quick test: what tokens appear adjacent to 'dar' (setup input)?
If material identity is encoded, different recipes should have different
tokens near dar. If not, we'll see the same generic tokens everywhere."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript
from collections import Counter, defaultdict

tx = Transcript()

# ── 1. dar neighbors on f75r ──
print("=" * 70)
print("DAR NEIGHBORS ON f75r")
print("=" * 70)

f75r_lines = defaultdict(list)
for t in tx.currier_b():
    if t.folio == 'f75r' and not t.is_label:
        f75r_lines[t.line].append(t.word)

for line_num in sorted(f75r_lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    words = f75r_lines[line_num]
    for i, w in enumerate(words):
        if w == 'dar':
            before = words[i-1] if i > 0 else '(START)'
            after = words[i+1] if i < len(words)-1 else '(END)'
            print(f"  L{line_num:>2s}: ...{before} >> dar << {after}...")

# ── 2. dar neighbors across ALL Currier B ──
print("\n" + "=" * 70)
print("DAR NEIGHBORS ACROSS ALL CURRIER B")
print("=" * 70)

# Build per-folio, per-line token lists
all_lines = defaultdict(lambda: defaultdict(list))
for t in tx.currier_b():
    if not t.is_label:
        all_lines[t.folio][t.line].append(t.word)

before_dar = Counter()
after_dar = Counter()
dar_contexts = []

for folio in sorted(all_lines.keys()):
    for line_num in sorted(all_lines[folio].keys(), key=lambda x: int(x) if x.isdigit() else 0):
        words = all_lines[folio][line_num]
        for i, w in enumerate(words):
            if w == 'dar':
                b = words[i-1] if i > 0 else '(START)'
                a = words[i+1] if i < len(words)-1 else '(END)'
                before_dar[b] += 1
                after_dar[a] += 1
                dar_contexts.append((folio, line_num, b, a))

total_dar = len(dar_contexts)
print(f"\nTotal 'dar' occurrences in Currier B: {total_dar}")

print(f"\nMost common token BEFORE dar:")
for w, c in before_dar.most_common(15):
    pct = 100 * c / total_dar
    print(f"  {w:20s}: {c:4d} ({pct:5.1f}%)")

print(f"\nMost common token AFTER dar:")
for w, c in after_dar.most_common(15):
    pct = 100 * c / total_dar
    print(f"  {w:20s}: {c:4d} ({pct:5.1f}%)")

# ── 3. Are dar neighbors folio-specific or universal? ──
print("\n" + "=" * 70)
print("FOLIO SPECIFICITY: do different folios have different dar-neighbors?")
print("=" * 70)

# For each folio, collect the set of dar-neighbors
folio_before = defaultdict(Counter)
folio_after = defaultdict(Counter)
for folio, line_num, b, a in dar_contexts:
    folio_before[folio][b] += 1
    folio_after[folio][a] += 1

# Show folios with 3+ dar occurrences
print(f"\nFolios with 3+ dar tokens (before >> dar << after):")
for folio in sorted(folio_before.keys()):
    n = sum(folio_before[folio].values())
    if n >= 3:
        top_b = folio_before[folio].most_common(3)
        top_a = folio_after[folio].most_common(3)
        b_str = ', '.join(f"{w}:{c}" for w, c in top_b)
        a_str = ', '.join(f"{w}:{c}" for w, c in top_a)
        print(f"  {folio:8s} (n={n:2d}): before=[{b_str}]  after=[{a_str}]")

# ── 4. Check the matched folios specifically ──
print("\n" + "=" * 70)
print("MATCHED FOLIO COMPARISON")
print("=" * 70)

matched = {'f75r': 'Ch19 aqua vitae (honey+wax)',
           'f76r': 'Ch18 element separation',
           'f113v': 'Ch12 mercury sublimation'}

for folio, recipe in matched.items():
    print(f"\n  {folio} ({recipe}):")
    folio_dars = [(ln, b, a) for f, ln, b, a in dar_contexts if f == folio]
    if not folio_dars:
        print("    No 'dar' tokens found")
    else:
        for ln, b, a in folio_dars:
            print(f"    L{ln:>2s}: {b} >> dar << {a}")

# ── 5. Double-dar sequences ──
print("\n" + "=" * 70)
print("DOUBLE-DAR SEQUENCES (dar dar)")
print("=" * 70)

double_dar_count = 0
for folio in sorted(all_lines.keys()):
    for line_num in sorted(all_lines[folio].keys(), key=lambda x: int(x) if x.isdigit() else 0):
        words = all_lines[folio][line_num]
        for i in range(len(words) - 1):
            if words[i] == 'dar' and words[i+1] == 'dar':
                double_dar_count += 1
                ctx = ' '.join(words[max(0,i-2):i+4])
                print(f"  {folio} L{line_num}: ...{ctx}...")

print(f"\nTotal double-dar: {double_dar_count}")

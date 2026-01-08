"""Analyze context around pure-daiin lines."""
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Build ordered list of lines per folio
folio_lines = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[1].strip('"').strip() if len(parts) > 1 else ''
                line_num = parts[2].strip('"').strip() if len(parts) > 2 else ''

                if folio not in folio_lines:
                    folio_lines[folio] = {}
                if line_num not in folio_lines[folio]:
                    folio_lines[folio][line_num] = []
                if word:
                    folio_lines[folio][line_num].append(word)

# Find daiin-only lines and their context
print("DAIIN LINE CONTEXTS")
print("=" * 70)

daiin_contexts = []
markers = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

for folio in sorted(folio_lines.keys()):
    lines = folio_lines[folio]
    line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    for i, ln in enumerate(line_nums):
        tokens = lines[ln]
        # Check if this is a daiin-only line
        if all(t == 'daiin' for t in tokens) and len(tokens) > 0:
            daiin_count = len(tokens)

            # Get previous line
            prev_tokens = []
            if i > 0:
                prev_ln = line_nums[i-1]
                prev_tokens = lines[prev_ln]

            # Get next line
            next_tokens = []
            if i < len(line_nums) - 1:
                next_ln = line_nums[i+1]
                next_tokens = lines[next_ln]

            # Find markers in surrounding lines
            prev_marker = None
            for t in prev_tokens:
                for m in markers:
                    if t.startswith(m):
                        prev_marker = m
                        break
                if prev_marker:
                    break

            next_marker = None
            for t in next_tokens:
                for m in markers:
                    if t.startswith(m):
                        next_marker = m
                        break
                if next_marker:
                    break

            daiin_contexts.append({
                'folio': folio,
                'line': ln,
                'count': daiin_count,
                'prev': prev_tokens[:5],  # First 5 tokens
                'next': next_tokens[:5],
                'prev_marker': prev_marker,
                'next_marker': next_marker
            })

print(f"Total daiin-only lines: {len(daiin_contexts)}")
print()

# Show first 20 examples
print("First 20 examples with context:")
print("-" * 70)
for ctx in daiin_contexts[:20]:
    print(f"Folio {ctx['folio']}, Line {ctx['line']}: {ctx['count']}x daiin")
    print(f"  PREV [{ctx['prev_marker']}]: {' '.join(ctx['prev'])}")
    print(f"  NEXT [{ctx['next_marker']}]: {' '.join(ctx['next'])}")
    print()

# Statistics on surrounding markers
print("=" * 70)
print("MARKER PATTERNS AROUND DAIIN LINES")
print("=" * 70)

prev_marker_counts = Counter(ctx['prev_marker'] for ctx in daiin_contexts)
next_marker_counts = Counter(ctx['next_marker'] for ctx in daiin_contexts)

print("\nMarker on PREVIOUS line:")
for m, ct in prev_marker_counts.most_common():
    print(f"  {m}: {ct}")

print("\nMarker on NEXT line:")
for m, ct in next_marker_counts.most_common():
    print(f"  {m}: {ct}")

# Check if daiin count correlates with anything
print()
print("=" * 70)
print("DAIIN COUNT DISTRIBUTION BY PRECEDING MARKER")
print("=" * 70)

for marker in markers:
    counts = [ctx['count'] for ctx in daiin_contexts if ctx['prev_marker'] == marker]
    if counts:
        print(f"\n{marker}: n={len(counts)}")
        print(f"  mean={sum(counts)/len(counts):.1f}, min={min(counts)}, max={max(counts)}")

# Which folios have the most daiin lines?
print()
print("=" * 70)
print("FOLIOS WITH MOST DAIIN LINES")
print("=" * 70)
folio_daiin = Counter(ctx['folio'] for ctx in daiin_contexts)
for folio, ct in folio_daiin.most_common(15):
    total_lines = len(folio_lines[folio])
    print(f"  {folio}: {ct} daiin lines / {total_lines} total ({100*ct/total_lines:.1f}%)")

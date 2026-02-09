"""Test 02: -ey Suffix Contextual Analysis

Question: What role does -ey play in procedural lines? It's early-leaning (mean pos 0.435),
part of the e-family (cooling/stability), but what does it *do* in context?

Method:
  1. Find all B tokens ending in -ey
  2. For each occurrence, extract the full line with glosses
  3. Show what tokens precede and follow -ey tokens
  4. Group by common -ey token types (chey, shey, qokchey, etc.)
  5. Display glossed lines for pattern recognition

Expected: If -ey has a consistent procedural role, lines containing it
should share structural similarities (e.g., always followed by energy tokens,
always preceded by setup tokens, etc.)
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology, TokenDictionary

tx = Transcript()
morph = Morphology()
td = TokenDictionary()

# Collect all B tokens indexed by folio+line
tokens = list(tx.currier_b())
print(f"Total B tokens: {len(tokens)}")

# Build line index: (folio, line) -> [tokens in order]
line_index = defaultdict(list)
for t in tokens:
    line_index[(t.folio, t.line)].append(t)

# Find all -ey tokens
ey_tokens = []
for t in tokens:
    m = morph.extract(t.word)
    if m.suffix == 'ey':
        ey_tokens.append(t)

print(f"Tokens with -ey suffix: {len(ey_tokens)}")
print(f"Unique -ey types: {len(set(t.word for t in ey_tokens))}")

# Group by token type
ey_by_type = defaultdict(list)
for t in ey_tokens:
    ey_by_type[t.word].append(t)

# Helper: gloss a token
def gloss(word):
    g = td.get_gloss(word)
    if g:
        return g
    # Fall back to morphological description
    m = morph.extract(word)
    parts = []
    if m.prefix:
        parts.append(m.prefix)
    if m.middle:
        parts.append(m.middle)
    if m.suffix:
        parts.append(f'-{m.suffix}')
    return '+'.join(parts) if parts else '?'

# Helper: render a line with glosses
def render_line(folio, line_num):
    line_tokens = line_index.get((folio, line_num), [])
    parts = []
    for t in line_tokens:
        g = td.get_gloss(t.word)
        m = morph.extract(t.word)
        is_ey = (m.suffix == 'ey')
        if g:
            display = f"{t.word}({g})"
        else:
            display = f"{t.word}"
        if is_ey:
            display = f">>>{display}<<<"
        parts.append(display)
    return '  '.join(parts)

# ============================================================
# ANALYSIS 1: Most common -ey token types
# ============================================================
print(f"\n{'='*80}")
print(f"MOST COMMON -ey TOKEN TYPES")
print(f"{'='*80}")

type_counts = Counter(t.word for t in ey_tokens)
for word, count in type_counts.most_common(25):
    m = morph.extract(word)
    g = td.get_gloss(word) or '(no gloss)'
    prefix = m.prefix or '-'
    middle = m.middle or '-'
    print(f"  {word:<16} {count:>4}x  prefix={prefix:<4} middle={middle:<8} gloss={g}")

# ============================================================
# ANALYSIS 2: What comes BEFORE and AFTER -ey tokens?
# ============================================================
print(f"\n{'='*80}")
print(f"BIGRAM CONTEXT: What precedes/follows -ey tokens?")
print(f"{'='*80}")

preceding_suffixes = Counter()
following_suffixes = Counter()
preceding_words = Counter()
following_words = Counter()

for t in ey_tokens:
    line_tokens = line_index[(t.folio, t.line)]
    idx = next((i for i, lt in enumerate(line_tokens) if lt is t), None)
    if idx is None:
        continue

    if idx > 0:
        prev = line_tokens[idx - 1]
        preceding_words[prev.word] += 1
        pm = morph.extract(prev.word)
        preceding_suffixes[pm.suffix or '(none)'] += 1

    if idx < len(line_tokens) - 1:
        nxt = line_tokens[idx + 1]
        following_words[nxt.word] += 1
        nm = morph.extract(nxt.word)
        following_suffixes[nm.suffix or '(none)'] += 1

print(f"\nSuffix of PRECEDING token:")
for sfx, count in preceding_suffixes.most_common(15):
    pct = count / len(ey_tokens) * 100
    print(f"  -{sfx:<8} {count:>4}x  ({pct:.1f}%)")

print(f"\nSuffix of FOLLOWING token:")
for sfx, count in following_suffixes.most_common(15):
    pct = count / len(ey_tokens) * 100
    print(f"  -{sfx:<8} {count:>4}x  ({pct:.1f}%)")

print(f"\nTop PRECEDING words:")
for word, count in preceding_words.most_common(15):
    g = td.get_gloss(word) or ''
    print(f"  {word:<16} {count:>4}x  {g}")

print(f"\nTop FOLLOWING words:")
for word, count in following_words.most_common(15):
    g = td.get_gloss(word) or ''
    print(f"  {word:<16} {count:>4}x  {g}")

# ============================================================
# ANALYSIS 3: Position in line (confirming early bias)
# ============================================================
print(f"\n{'='*80}")
print(f"POSITION ANALYSIS")
print(f"{'='*80}")

positions = []
for t in ey_tokens:
    line_tokens = line_index[(t.folio, t.line)]
    idx = next((i for i, lt in enumerate(line_tokens) if lt is t), 0)
    line_len = len(line_tokens)
    if line_len > 1:
        pos_frac = idx / (line_len - 1)
    else:
        pos_frac = 0.5
    positions.append((pos_frac, idx, line_len))

# Position by slot number (absolute)
slot_counts = Counter(p[1] for p in positions)
print(f"\nAbsolute slot position (0 = line start):")
for slot in sorted(slot_counts.keys())[:10]:
    count = slot_counts[slot]
    pct = count / len(positions) * 100
    bar = '#' * int(pct)
    print(f"  slot {slot:>2}: {count:>4}x ({pct:>5.1f}%)  {bar}")

# Is -ey the FIRST content token? (slot 0 or 1)
first_two = sum(1 for p in positions if p[1] <= 1)
pct_first = first_two / len(positions) * 100
print(f"\n  -ey in first 2 slots: {first_two}/{len(positions)} ({pct_first:.1f}%)")

# ============================================================
# ANALYSIS 4: Prefix distribution for -ey tokens
# ============================================================
print(f"\n{'='*80}")
print(f"PREFIX DISTRIBUTION for -ey tokens")
print(f"{'='*80}")

prefix_counts = Counter()
for t in ey_tokens:
    m = morph.extract(t.word)
    prefix_counts[m.prefix or '(none)'] += 1

for prefix, count in prefix_counts.most_common(20):
    pct = count / len(ey_tokens) * 100
    print(f"  {prefix:<8} {count:>4}x  ({pct:.1f}%)")

# ============================================================
# ANALYSIS 5: Middle distribution for -ey tokens
# ============================================================
print(f"\n{'='*80}")
print(f"MIDDLE DISTRIBUTION for -ey tokens")
print(f"{'='*80}")

middle_counts = Counter()
for t in ey_tokens:
    m = morph.extract(t.word)
    middle_counts[m.middle or '(none)'] += 1

for middle, count in middle_counts.most_common(20):
    pct = count / len(ey_tokens) * 100
    print(f"  {middle:<12} {count:>4}x  ({pct:.1f}%)")

# ============================================================
# ANALYSIS 6: Sample glossed lines for top -ey types
# ============================================================
print(f"\n{'='*80}")
print(f"GLOSSED LINE SAMPLES (top -ey types)")
print(f"{'='*80}")

for word, count in type_counts.most_common(12):
    g = td.get_gloss(word) or '(no gloss)'
    print(f"\n--- {word} ({count}x, gloss: {g}) ---")
    occurrences = ey_by_type[word]
    # Show up to 8 diverse lines (different folios preferred)
    seen_folios = set()
    shown = 0
    for t in occurrences:
        if shown >= 8:
            break
        if t.folio in seen_folios and shown >= 4:
            continue
        seen_folios.add(t.folio)
        rendered = render_line(t.folio, t.line)
        print(f"  {t.folio}.{t.line:>2}: {rendered}")
        shown += 1

# ============================================================
# ANALYSIS 7: Compare -ey lines vs -dy lines for same stems
# ============================================================
print(f"\n{'='*80}")
print(f"MINIMAL PAIRS: -ey vs -dy on same stems")
print(f"{'='*80}")
print(f"Stems that appear with both -ey and -dy suffixes:\n")

# Build stem -> suffix -> occurrences
stem_map = defaultdict(lambda: defaultdict(list))
for t in tokens:
    m = morph.extract(t.word)
    if m.middle and m.suffix in ('ey', 'dy'):
        stem = (m.prefix or '') + m.middle
        stem_map[stem][m.suffix].append(t)

pair_count = 0
for stem in sorted(stem_map.keys()):
    if 'ey' in stem_map[stem] and 'dy' in stem_map[stem]:
        ey_list = stem_map[stem]['ey']
        dy_list = stem_map[stem]['dy']
        if len(ey_list) >= 3 and len(dy_list) >= 3:
            pair_count += 1
            # Mean positions
            def mean_pos(tok_list):
                pos = []
                for t in tok_list:
                    lt = line_index[(t.folio, t.line)]
                    idx = next((i for i, x in enumerate(lt) if x is t), 0)
                    ll = len(lt)
                    pos.append(idx / max(ll - 1, 1))
                return sum(pos) / len(pos)

            ey_pos = mean_pos(ey_list)
            dy_pos = mean_pos(dy_list)

            ey_word = stem + 'ey'
            dy_word = stem + 'dy'
            ey_gloss = td.get_gloss(ey_word) or '?'
            dy_gloss = td.get_gloss(dy_word) or '?'

            print(f"  STEM '{stem}':")
            print(f"    -{stem}ey  n={len(ey_list):>3}  pos={ey_pos:.3f}  gloss={ey_gloss}")
            print(f"    -{stem}dy  n={len(dy_list):>3}  pos={dy_pos:.3f}  gloss={dy_gloss}")

            # Show 2 sample lines each
            for label, tok_list in [('ey', ey_list), ('dy', dy_list)]:
                for t in tok_list[:2]:
                    rendered = render_line(t.folio, t.line)
                    print(f"      {label} {t.folio}.{t.line:>2}: {rendered}")
            print()

print(f"Total minimal pairs (stem+ey vs stem+dy, n>=3 each): {pair_count}")

# ============================================================
# Save summary
# ============================================================
results = {
    'total_ey_tokens': len(ey_tokens),
    'unique_ey_types': len(set(t.word for t in ey_tokens)),
    'top_types': [
        {'word': w, 'count': c, 'gloss': td.get_gloss(w)}
        for w, c in type_counts.most_common(25)
    ],
    'position_stats': {
        'mean': round(sum(p[0] for p in positions) / len(positions), 3),
        'pct_first_two_slots': round(first_two / len(positions) * 100, 1),
        'slot_distribution': {str(k): v for k, v in sorted(slot_counts.items())[:8]},
    },
    'preceding_suffix_top5': [
        {'suffix': s, 'count': c} for s, c in preceding_suffixes.most_common(5)
    ],
    'following_suffix_top5': [
        {'suffix': s, 'count': c} for s, c in following_suffixes.most_common(5)
    ],
    'prefix_distribution': {p: c for p, c in prefix_counts.most_common(15)},
    'middle_distribution': {m: c for m, c in middle_counts.most_common(15)},
    'minimal_pair_count': pair_count,
}

out_path = Path('phases/GLOSS_RESEARCH/results/02_ey_suffix_context.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path}")

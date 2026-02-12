"""Do compound MIDDLE glosses make sense in procedural context?

Renders full lines containing folio-unique MIDDLEs to see whether
the composed glosses read as coherent procedural sequences.
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, BFolioDecoder

# --- Setup ---
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# --- Find folio-unique MIDDLEs ---
folio_middles = defaultdict(set)
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        folio_middles[m.middle].add(t.folio)

unique_middles = {mid for mid, folios in folio_middles.items() if len(folios) == 1}

# --- Build line groupings from transcript (not BTokenAnalysis) ---
def get_folio_lines(folio):
    """Get tokens grouped by line for a folio, with BTokenAnalysis attached."""
    # Get raw transcript tokens for line info
    raw_tokens = [t for t in tx.currier_b() if t.folio == folio]
    lines_raw = defaultdict(list)
    for t in raw_tokens:
        lines_raw[t.line].append(t)

    # Get BTokenAnalysis for glosses
    analysis = decoder.analyze_folio(folio)
    # Build word->analysis lookup (ordered, handle duplicates)
    analysis_queue = defaultdict(list)
    for ta in analysis.tokens:
        analysis_queue[ta.word].append(ta)

    # Match raw tokens to analyses
    lines_analyzed = defaultdict(list)
    used = defaultdict(int)
    for line_id in sorted(lines_raw.keys()):
        for raw_t in lines_raw[line_id]:
            w = raw_t.word
            idx = used[w]
            if w in analysis_queue and idx < len(analysis_queue[w]):
                lines_analyzed[line_id].append(analysis_queue[w][idx])
                used[w] += 1

    return lines_analyzed


# --- Render full lines for distinctive folios ---
test_folios = ['f114r', 'f105v', 'f86v6', 'f115r', 'f105r']

for folio in test_folios:
    lines = get_folio_lines(folio)

    # Find lines containing folio-unique MIDDLEs
    interesting_lines = []
    for line_id, tokens in sorted(lines.items()):
        has_unique = False
        for ta in tokens:
            m = morph.extract(ta.word)
            if m and m.middle and m.middle in unique_middles:
                has_unique = True
                break
        if has_unique:
            interesting_lines.append((line_id, tokens))

    print(f"\n{'='*80}")
    print(f"FOLIO {folio}: Lines containing folio-unique MIDDLEs")
    print(f"  ({len(interesting_lines)} lines with unique tokens, "
          f"{len(lines)} total lines)")
    print(f"{'='*80}")

    shown = 0
    for line_id, tokens in interesting_lines:
        if shown >= 6:
            break
        shown += 1

        print(f"\n  Line {line_id}:")

        # Show raw tokens
        raw = ' '.join(ta.word for ta in tokens)
        print(f"    Raw: {raw}")

        # Show interpreted sequence
        print(f"    Interpreted:")
        for ta in tokens:
            m = morph.extract(ta.word)
            mid_str = m.middle if m else '?'
            is_unique = m and m.middle and m.middle in unique_middles
            marker = ' ***' if is_unique else ''

            interp = ta.interpretive()

            print(f"      {ta.word:14s} [{mid_str:10s}] -> {interp:45s}{marker}")

        # Show flow rendering
        print(f"    Flow sequence:")
        flow_parts = []
        for ta in tokens:
            fg = ta.flow_gloss()
            if fg:
                op = fg.get('operation', '')
                ctrl = fg.get('control_flow', '')
                compact = f"{op}"
                if ctrl:
                    compact += f" ({ctrl})"
                flow_parts.append(compact)
        print(f"      {' -> '.join(flow_parts)}")

# --- Coherence analysis: do extension glosses match their line's theme? ---
print(f"\n\n{'='*80}")
print("EXTENSION CHARACTER CONTEXT ANALYSIS")
print("Do extension chars match the operational context of their line?")
print(f"{'='*80}")

# For each extension char, what kernels/prefixes appear in the same line?
ext_line_context = defaultdict(lambda: {'kernels': Counter(), 'prefixes': Counter(),
                                         'count': 0})

mid_analyzer = decoder.mid_analyzer

# Use raw transcript tokens (have .line attribute)
b_tokens = list(tx.currier_b())
line_groups = defaultdict(list)
for t in b_tokens:
    line_groups[(t.folio, t.line)].append(t)

for (folio, line_id), raw_tokens in line_groups.items():
    # Find extension chars in this line
    line_ext_chars = set()
    line_kernels = Counter()

    for t in raw_tokens:
        m = morph.extract(t.word)
        if not m or not m.middle:
            continue

        # Approximate kernel from core middle
        if m.middle in mid_analyzer._core_middles:
            if m.middle.startswith('k') or 'k' in m.middle[:2]:
                line_kernels['k'] += 1
            elif m.middle.startswith('e') or m.middle == 'ee':
                line_kernels['e'] += 1
            elif m.middle.startswith('h') or 'h' in m.middle[:2]:
                line_kernels['h'] += 1

        # Check if compound with extensions
        if m.middle not in mid_analyzer._core_middles:
            for atom in sorted(mid_analyzer._core_middles, key=len, reverse=True):
                idx = m.middle.find(atom)
                if idx >= 0:
                    pre = m.middle[:idx]
                    post = m.middle[idx + len(atom):]
                    if len(pre) + len(post) <= 3:
                        for ch in pre + post:
                            line_ext_chars.add(ch)
                    break

    # Record context for each extension char
    for ch in line_ext_chars:
        ext_line_context[ch]['kernels'].update(line_kernels)
        ext_line_context[ch]['count'] += 1

print(f"\n{'ext':>4s} {'gloss':>20s} {'lines':>6s}  "
      f"{'k-lines':>8s} {'e-lines':>8s} {'h-lines':>8s}  "
      f"{'interpretation':>40s}")
print("-" * 110)

with open('data/middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)['middles']

ext_glosses = {name: entry.get('gloss', '?')
               for name, entry in mid_dict.items() if len(name) == 1}

for ch in sorted(ext_line_context.keys(),
                 key=lambda c: ext_line_context[c]['count'], reverse=True):
    ctx = ext_line_context[ch]
    gloss = ext_glosses.get(ch, '?')
    k_lines = ctx['kernels'].get('k', 0)
    e_lines = ctx['kernels'].get('e', 0)
    h_lines = ctx['kernels'].get('h', 0)
    total = ctx['count']

    # Does the extension's gloss match the dominant kernel context?
    k_pct = 100 * k_lines / max(total, 1)
    e_pct = 100 * e_lines / max(total, 1)
    h_pct = 100 * h_lines / max(total, 1)

    # Interpret
    if ch == 'k' and k_pct > 30:
        note = "COHERENT: 'heat' ext appears in heat-heavy lines"
    elif ch == 'e' and e_pct > 20:
        note = "COHERENT: 'cool' ext appears in cool-heavy lines"
    elif ch == 'h' and h_pct > 15:
        note = "COHERENT: 'hazard' ext in monitoring lines"
    elif ch == 'o':
        note = "UBIQUITOUS: 'work' appears everywhere (generic modifier)"
    elif ch == 'd':
        note = "UBIQUITOUS: 'mark' appears everywhere (annotation)"
    elif ch in ('s', 't', 'r', 'i', 'p', 'a', 'c', 'f', 'l'):
        note = f"OPERATIONAL: '{gloss}' - procedural qualifier"
    else:
        note = ""

    gloss_str = gloss or f'?{ch}'
    print(f"  {ch:>2s} {gloss_str:>20s} {total:>6d}  "
          f"k={k_pct:5.1f}%  e={e_pct:5.1f}%  h={h_pct:5.1f}%  "
          f"{note}")

# --- Check: do long-extension compounds cluster in specific line positions? ---
print(f"\n\n{'='*80}")
print("LINE POSITION OF COMPOUND MIDDLEs")
print("(Do complex compounds cluster at start, middle, or end of lines?)")
print(f"{'='*80}")

position_counts = {'first_third': Counter(), 'mid_third': Counter(),
                   'last_third': Counter()}
total_by_pos = Counter()

# Use pre-built line_groups from raw transcript
for (folio, line_id), raw_tokens in line_groups.items():
    n = len(raw_tokens)
    if n < 3:
        continue

    for i, t in enumerate(raw_tokens):
        m = morph.extract(t.word)
        if not m or not m.middle:
            continue

        # Determine position
        if i < n / 3:
            pos = 'first_third'
        elif i < 2 * n / 3:
            pos = 'mid_third'
        else:
            pos = 'last_third'

        # Is this a compound?
        if m.middle not in mid_analyzer._core_middles:
            ext_len = 0
            for atom in sorted(mid_analyzer._core_middles, key=len, reverse=True):
                idx = m.middle.find(atom)
                if idx >= 0:
                    pre = m.middle[:idx]
                    post = m.middle[idx + len(atom):]
                    ext_len = len(pre) + len(post)
                    break

            if ext_len == 0:
                position_counts[pos]['novel'] += 1
            elif ext_len <= 2:
                position_counts[pos]['short_ext'] += 1
            elif ext_len <= 3:
                position_counts[pos]['med_ext'] += 1
            else:
                position_counts[pos]['long_ext'] += 1
        else:
            position_counts[pos]['core'] += 1
        total_by_pos[pos] += 1

print(f"\n{'Position':<15s} {'Core':>8s} {'Short(1-2)':>10s} {'Med(3)':>8s} {'Long(4+)':>10s} {'Novel':>8s}")
print("-" * 65)
for pos in ['first_third', 'mid_third', 'last_third']:
    total = total_by_pos[pos] or 1
    core_pct = 100 * position_counts[pos]['core'] / total
    short_pct = 100 * position_counts[pos]['short_ext'] / total
    med_pct = 100 * position_counts[pos]['med_ext'] / total
    long_pct = 100 * position_counts[pos]['long_ext'] / total
    novel_pct = 100 * position_counts[pos]['novel'] / total
    print(f"  {pos:<13s} {core_pct:7.1f}% {short_pct:9.1f}% {med_pct:7.1f}% {long_pct:9.1f}% {novel_pct:7.1f}%")

# --- Read-through of one paragraph with all glosses ---
print(f"\n\n{'='*80}")
print("FULL PARAGRAPH READ-THROUGH: f86v6 (section S, highly distinctive)")
print("Every token glossed, compounds marked with ***")
print(f"{'='*80}")

f86_lines = get_folio_lines('f86v6')

# Show first 8 lines
for line_id, tokens in sorted(f86_lines.items())[:8]:
    print(f"\n  Line {line_id}:")
    for ta in tokens:
        m = morph.extract(ta.word)
        is_unique = m and m.middle and m.middle in unique_middles
        marker = '***' if is_unique else '   '
        interp = ta.interpretive()
        print(f"    {marker} {ta.word:14s} -> {interp}")

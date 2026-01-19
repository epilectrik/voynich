"""
CAS-POST Part 2: Articulator Deployment and Mixed-Entry Analysis
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
ARTICULATORS = ['yk', 'yt', 'kch', 'ks', 'ko', 'yd', 'ysh', 'ych']

def get_core_prefix(token):
    for p in CORE_PREFIXES:
        if token.startswith(p):
            return p
    return None

def get_articulator(token):
    for a in ARTICULATORS:
        if token.startswith(a):
            return a
    return None

def get_prefix_after_articulator(token):
    """Get core prefix that appears after an articulator."""
    art = get_articulator(token)
    if art:
        remainder = token[len(art):]
        for p in CORE_PREFIXES:
            if remainder.startswith(p):
                return p
    return None

# Load entries
entries = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    current_entry = None

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            # Filter to H (PRIMARY) transcriber only
            transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
            if transcriber != 'H':
                continue

            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if word:
                    entry_key = f"{folio}_{line_num}"
                    if current_entry is None or current_entry['key'] != entry_key:
                        if current_entry:
                            entries.append(current_entry)
                        current_entry = {
                            'key': entry_key,
                            'folio': folio,
                            'section': section,
                            'tokens': []
                        }
                    current_entry['tokens'].append(word)

    if current_entry:
        entries.append(current_entry)


def classify_entry(entry):
    """Classify as exclusive (1 prefix) or mixed (multiple)."""
    prefixes = set()
    for t in entry['tokens']:
        p = get_core_prefix(t)
        if p:
            prefixes.add(p)
    return 'exclusive' if len(prefixes) <= 1 else 'mixed'


def detect_repetition(tokens):
    n = len(tokens)
    if n < 4:
        return None, 0
    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break
                if matches:
                    return block, count
    return None, 0


print("=" * 80)
print("CAS-POST PART 2: ARTICULATOR DEPLOYMENT ANALYSIS")
print("=" * 80)

# 1. Articulator association with PREFIX families
print("\n### 1. ARTICULATOR x PREFIX ASSOCIATION")
print("-" * 60)
print("Which core prefixes appear AFTER each articulator?\n")

art_prefix_matrix = defaultdict(Counter)
art_alone = Counter()

for entry in entries:
    for token in entry['tokens']:
        art = get_articulator(token)
        if art:
            prefix_after = get_prefix_after_articulator(token)
            if prefix_after:
                art_prefix_matrix[art][prefix_after] += 1
            else:
                art_alone[art] += 1

print(f"{'ART':<8}", end='')
for p in CORE_PREFIXES:
    print(f"{p:>8}", end='')
print(f"{'(alone)':>10}")
print("-" * 80)

for art in ARTICULATORS:
    total = sum(art_prefix_matrix[art].values()) + art_alone[art]
    if total >= 20:
        print(f"{art:<8}", end='')
        for p in CORE_PREFIXES:
            count = art_prefix_matrix[art][p]
            pct = 100 * count / total if total else 0
            print(f"{pct:>7.1f}%", end='')
        alone_pct = 100 * art_alone[art] / total if total else 0
        print(f"{alone_pct:>9.1f}%")


# 2. Articulator density: exclusive vs mixed entries
print("\n\n### 2. ARTICULATOR IN EXCLUSIVE vs MIXED ENTRIES")
print("-" * 60)

exclusive_art = 0
exclusive_total = 0
mixed_art = 0
mixed_total = 0

for entry in entries:
    mode = classify_entry(entry)
    art_count = sum(1 for t in entry['tokens'] if get_articulator(t))
    total_count = len(entry['tokens'])

    if mode == 'exclusive':
        exclusive_art += art_count
        exclusive_total += total_count
    else:
        mixed_art += art_count
        mixed_total += total_count

print(f"\nExclusive entries: {exclusive_art}/{exclusive_total} articulated ({100*exclusive_art/exclusive_total:.1f}%)")
print(f"Mixed entries: {mixed_art}/{mixed_total} articulated ({100*mixed_art/mixed_total:.1f}%)")


# 3. Articulator density vs repetition
print("\n\n### 3. ARTICULATOR DENSITY BY REPETITION COUNT")
print("-" * 60)

rep_art = defaultdict(lambda: {'art': 0, 'total': 0})
for entry in entries:
    block, rep_count = detect_repetition(entry['tokens'])
    if rep_count >= 2:
        art_count = sum(1 for t in entry['tokens'] if get_articulator(t))
        rep_art[rep_count]['art'] += art_count
        rep_art[rep_count]['total'] += len(entry['tokens'])

print(f"\n{'Rep Count':<12} {'Art Tokens':>12} {'Total':>12} {'Density':>12}")
print("-" * 50)
for rep in sorted(rep_art.keys()):
    data = rep_art[rep]
    density = 100 * data['art'] / data['total'] if data['total'] else 0
    print(f"{rep}x{'':<10} {data['art']:>12} {data['total']:>12} {density:>11.1f}%")


print("\n\n" + "=" * 80)
print("CAS-POST PART 2: MIXED-ENTRY INTERACTION PROFILING")
print("=" * 80)

# 4. Which prefix combinations occur in mixed entries?
print("\n### 4. PREFIX CO-OCCURRENCE IN MIXED ENTRIES")
print("-" * 60)

prefix_pairs = Counter()
mixed_entries = [e for e in entries if classify_entry(e) == 'mixed']

for entry in mixed_entries:
    prefixes = set()
    for t in entry['tokens']:
        p = get_core_prefix(t)
        if p:
            prefixes.add(p)

    # Count all pairs
    prefix_list = sorted(prefixes)
    for i in range(len(prefix_list)):
        for j in range(i+1, len(prefix_list)):
            pair = (prefix_list[i], prefix_list[j])
            prefix_pairs[pair] += 1

print(f"\nMost common prefix pairs in mixed entries:")
for pair, count in prefix_pairs.most_common(15):
    print(f"  {pair[0]} + {pair[1]}: {count}")


# 5. Articulator usage increase with mixing
print("\n\n### 5. ARTICULATOR DENSITY BY PREFIX COUNT")
print("-" * 60)

prefix_count_art = defaultdict(lambda: {'art': 0, 'total': 0})
for entry in entries:
    prefixes = set(get_core_prefix(t) for t in entry['tokens'] if get_core_prefix(t))
    prefix_count = len(prefixes)
    art_count = sum(1 for t in entry['tokens'] if get_articulator(t))

    prefix_count_art[prefix_count]['art'] += art_count
    prefix_count_art[prefix_count]['total'] += len(entry['tokens'])

print(f"\n{'Prefix Count':<14} {'Art Tokens':>12} {'Total':>12} {'Density':>12}")
print("-" * 55)
for count in sorted(prefix_count_art.keys()):
    data = prefix_count_art[count]
    if data['total'] >= 100:
        density = 100 * data['art'] / data['total'] if data['total'] else 0
        print(f"{count:<14} {data['art']:>12} {data['total']:>12} {density:>11.1f}%")


# 6. Section-specific prefix mixing patterns
print("\n\n### 6. PREFIX MIXING BY SECTION")
print("-" * 60)

section_mixing = defaultdict(lambda: Counter())
for entry in mixed_entries:
    prefixes = frozenset(get_core_prefix(t) for t in entry['tokens'] if get_core_prefix(t))
    section_mixing[entry['section']][prefixes] += 1

for section in ['H', 'P', 'T']:
    print(f"\n{section} section - most common prefix combinations:")
    for combo, count in section_mixing[section].most_common(5):
        print(f"  {'+'.join(sorted(combo))}: {count}")


print("\n\n" + "=" * 80)
print("SYNTHESIS: ARTICULATOR DEPLOYMENT RULES")
print("=" * 80)

print("""
Based on the above analysis:

1. ARTICULATOR-PREFIX AFFINITY:
   - yt/yk strongly prefer CH family
   - kch almost exclusively precedes OL
   - Articulators are NOT random attachments

2. ENTRY MODE EFFECT:
   - Articulator density similar in exclusive vs mixed
   - Articulators do NOT compensate for mixing

3. REPETITION EFFECT:
   - Articulator density appears stable across repetition counts
   - Repetition does NOT suppress articulation

4. MIXING PATTERNS:
   - CH+DA, CH+QO, CH+SH are most common pairs
   - CH appears in nearly all mixed entries
   - Some prefixes rarely mix (CT, OL?)

5. SECTION VARIATION:
   - Each section has characteristic mixing patterns
   - Sections are NOT just scaled versions of each other
""")

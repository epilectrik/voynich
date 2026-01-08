"""
CAS-POST: Post-Closure Internal Comparative Analysis of Currier A

Exploiting the closed structure to extract secondary regularities.
NO new axes, NO semantics, NO grammar changes.
"""

from collections import defaultdict, Counter
from pathlib import Path
import math

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Fixed structural components (from CAS closure)
CORE_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
ARTICULATORS = ['yk', 'yt', 'kch', 'ks', 'ko', 'yd', 'ysh', 'ych']
SUFFIXES = ['daiin', 'aiin', 'ain', 'in', 'dy', 'edy', 'ody', 'or', 'eor', 'ar',
            'ol', 'eol', 'al', 'chy', 'hy', 'y', 'ey', 'am', 'om']


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


def get_suffix(token):
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(s):
            return s
    return None


def entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0
    ent = 0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


# Load data with full structure
entries = []
tokens_by_section = defaultdict(list)
entries_by_section = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    current_entry = None

    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if word:
                    entry_key = f"{folio}_{line_num}"
                    tokens_by_section[section].append(word)

                    # Group by entry
                    if current_entry is None or current_entry['key'] != entry_key:
                        if current_entry:
                            entries.append(current_entry)
                            entries_by_section[current_entry['section']].append(current_entry)
                        current_entry = {
                            'key': entry_key,
                            'folio': folio,
                            'section': section,
                            'tokens': []
                        }
                    current_entry['tokens'].append(word)

    if current_entry:
        entries.append(current_entry)
        entries_by_section[current_entry['section']].append(current_entry)


def detect_repetition(tokens):
    """Detect repeating block structure."""
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


def classify_entry(entry):
    """Classify entry as exclusive (one prefix family) or mixed (multiple)."""
    tokens = entry['tokens']
    prefixes = set()
    for t in tokens:
        p = get_core_prefix(t)
        if p:
            prefixes.add(p)

    if len(prefixes) <= 1:
        return 'exclusive'
    else:
        return 'mixed'


print("=" * 80)
print("CAS-POST: SECTION-LEVEL CONFIGURATION PROFILES")
print("=" * 80)

sections = ['H', 'P', 'T']

# 1. PREFIX distribution by section
print("\n### 1. PREFIX DISTRIBUTION BY SECTION")
print("-" * 60)

prefix_by_section = {s: Counter() for s in sections}
for section, tokens in tokens_by_section.items():
    for t in tokens:
        p = get_core_prefix(t)
        if p:
            prefix_by_section[section][p] += 1

print(f"\n{'PREFIX':<8}", end='')
for s in sections:
    print(f"{s:>10}", end='')
print(f"{'Chi2 sig':>12}")
print("-" * 50)

for prefix in CORE_PREFIXES:
    print(f"{prefix:<8}", end='')
    total = sum(prefix_by_section[s][prefix] for s in sections)
    for s in sections:
        count = prefix_by_section[s][prefix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>9.1f}%", end='')
    print()

# Calculate section concentration for each prefix
print("\nSection concentration (max % in one section):")
for prefix in CORE_PREFIXES:
    total = sum(prefix_by_section[s][prefix] for s in sections)
    if total:
        max_pct = max(100 * prefix_by_section[s][prefix] / total for s in sections)
        max_section = max(sections, key=lambda s: prefix_by_section[s][prefix])
        print(f"  {prefix}: {max_pct:.1f}% in {max_section}")


# 2. Articulator density by section
print("\n\n### 2. ARTICULATOR DENSITY BY SECTION")
print("-" * 60)

art_by_section = {s: 0 for s in sections}
total_by_section = {s: len(tokens_by_section[s]) for s in sections}

for section, tokens in tokens_by_section.items():
    for t in tokens:
        if get_articulator(t):
            art_by_section[section] += 1

print(f"\n{'Section':<10} {'Total Tokens':>15} {'Articulators':>15} {'Density':>10}")
print("-" * 55)
for s in sections:
    density = 100 * art_by_section[s] / total_by_section[s] if total_by_section[s] else 0
    print(f"{s:<10} {total_by_section[s]:>15} {art_by_section[s]:>15} {density:>9.1f}%")


# 3. SUFFIX mode balance by section
print("\n\n### 3. SUFFIX DISTRIBUTION BY SECTION")
print("-" * 60)

suffix_by_section = {s: Counter() for s in sections}
for section, tokens in tokens_by_section.items():
    for t in tokens:
        suf = get_suffix(t)
        if suf:
            suffix_by_section[section][suf] += 1

# Top 10 suffixes overall
all_suffixes = Counter()
for s in sections:
    all_suffixes.update(suffix_by_section[s])

print(f"\n{'SUFFIX':<12}", end='')
for s in sections:
    print(f"{s:>10}", end='')
print()
print("-" * 45)

for suffix, _ in all_suffixes.most_common(12):
    print(f"-{suffix:<11}", end='')
    total = sum(suffix_by_section[s][suffix] for s in sections)
    for s in sections:
        count = suffix_by_section[s][suffix]
        pct = 100 * count / total if total else 0
        print(f"{pct:>9.1f}%", end='')
    print()


# 4. Repetition uniformity vs variance
print("\n\n### 4. REPETITION PATTERNS BY SECTION")
print("-" * 60)

rep_by_section = {s: [] for s in sections}
for entry in entries:
    block, count = detect_repetition(entry['tokens'])
    if count >= 2:
        rep_by_section[entry['section']].append(count)

print(f"\n{'Section':<10} {'Entries w/rep':>15} {'Mean rep':>10} {'Std':>10} {'Uniform%':>10}")
print("-" * 60)

for s in sections:
    reps = rep_by_section[s]
    if reps:
        mean_rep = sum(reps) / len(reps)
        variance = sum((r - mean_rep)**2 for r in reps) / len(reps)
        std_rep = variance ** 0.5
        # Uniform = all same count
        most_common = Counter(reps).most_common(1)[0]
        uniform_pct = 100 * most_common[1] / len(reps)
        print(f"{s:<10} {len(reps):>15} {mean_rep:>10.2f} {std_rep:>10.2f} {uniform_pct:>9.1f}%")
    else:
        print(f"{s:<10} {'0':>15}")


# 5. Entry mode (exclusive vs mixed) by section
print("\n\n### 5. ENTRY MODE BY SECTION")
print("-" * 60)

mode_by_section = {s: Counter() for s in sections}
for entry in entries:
    mode = classify_entry(entry)
    mode_by_section[entry['section']][mode] += 1

print(f"\n{'Section':<10} {'Exclusive':>12} {'Mixed':>12} {'Exclusive%':>12}")
print("-" * 50)

for s in sections:
    exc = mode_by_section[s]['exclusive']
    mix = mode_by_section[s]['mixed']
    total = exc + mix
    exc_pct = 100 * exc / total if total else 0
    print(f"{s:<10} {exc:>12} {mix:>12} {exc_pct:>11.1f}%")


# 6. Section archetypes summary
print("\n\n" + "=" * 80)
print("SECTION ARCHETYPES (Structural Only)")
print("=" * 80)

print("""
Based on the above metrics, each section exhibits a distinct configuration:

SECTION H (Herbal):
""")

h_metrics = {
    'dominant_prefix': max(CORE_PREFIXES, key=lambda p: prefix_by_section['H'][p]),
    'art_density': 100 * art_by_section['H'] / total_by_section['H'],
    'exclusive_pct': 100 * mode_by_section['H']['exclusive'] / sum(mode_by_section['H'].values()),
}
print(f"  - Dominant prefix: {h_metrics['dominant_prefix']}")
print(f"  - Articulator density: {h_metrics['art_density']:.1f}%")
print(f"  - Exclusive entry rate: {h_metrics['exclusive_pct']:.1f}%")

print("\nSECTION P (Pharmaceutical):")
p_metrics = {
    'dominant_prefix': max(CORE_PREFIXES, key=lambda p: prefix_by_section['P'][p]),
    'art_density': 100 * art_by_section['P'] / total_by_section['P'],
    'exclusive_pct': 100 * mode_by_section['P']['exclusive'] / sum(mode_by_section['P'].values()),
}
print(f"  - Dominant prefix: {p_metrics['dominant_prefix']}")
print(f"  - Articulator density: {p_metrics['art_density']:.1f}%")
print(f"  - Exclusive entry rate: {p_metrics['exclusive_pct']:.1f}%")

print("\nSECTION T (Text/Other):")
t_metrics = {
    'dominant_prefix': max(CORE_PREFIXES, key=lambda p: prefix_by_section['T'][p]),
    'art_density': 100 * art_by_section['T'] / total_by_section['T'],
    'exclusive_pct': 100 * mode_by_section['T']['exclusive'] / sum(mode_by_section['T'].values()),
}
print(f"  - Dominant prefix: {t_metrics['dominant_prefix']}")
print(f"  - Articulator density: {t_metrics['art_density']:.1f}%")
print(f"  - Exclusive entry rate: {t_metrics['exclusive_pct']:.1f}%")

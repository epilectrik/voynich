"""What makes Voynich B folios different from each other?

The operational matching showed all 82 folios cluster tightly in 12-dim
profile space (prep MIDDLEs, kernel ratios, suffix rates). This script
asks: what dimensions ACTUALLY discriminate between folios?

Examines: full MIDDLE vocabulary, prefix specifics, paragraph structure,
compound MIDDLE patterns, extension characters, token length, FL stages.
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import (BFolioDecoder, Transcript, Morphology,
                              MiddleAnalyzer)

# --- Setup ---
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer._core_middles

b_folios = sorted(set(t.folio for t in tx.currier_b()))
print(f"Profiling {len(b_folios)} Currier B folios...\n")

# --- Collect per-folio features ---
folio_data = {}

for i, folio in enumerate(b_folios):
    tokens = [t for t in tx.currier_b() if t.folio == folio]
    if not tokens:
        continue

    # Group by line and paragraph
    lines = defaultdict(list)
    paragraphs = set()
    for t in tokens:
        lines[t.line].append(t)
        if '.' in t.line:
            paragraphs.add(t.line.split('.')[0])
        else:
            paragraphs.add(t.line)

    # Morphological analysis
    middles = []
    prefixes = []
    suffixes = []
    articulators = []
    word_lengths = []
    middle_lengths = []
    compound_count = 0
    extension_chars = Counter()

    for t in tokens:
        m = morph.extract(t.word)
        word_lengths.append(len(t.word))
        if m:
            if m.middle:
                middles.append(m.middle)
                middle_lengths.append(len(m.middle))
                # Check compound
                if m.middle not in core_middles:
                    decomp = None
                    best_ext = 999
                    for atom in sorted(core_middles, key=len, reverse=True):
                        idx = m.middle.find(atom)
                        if idx >= 0:
                            pre = m.middle[:idx]
                            post = m.middle[idx + len(atom):]
                            ext_len = len(pre) + len(post)
                            if ext_len <= 3 and ext_len < best_ext:
                                decomp = (atom, pre, post)
                                best_ext = ext_len
                    if decomp:
                        compound_count += 1
                        for ch in decomp[1] + decomp[2]:
                            extension_chars[ch] += 1
            if m.prefix:
                prefixes.append(m.prefix)
            if m.suffix:
                suffixes.append(m.suffix)
            if m.articulator:
                articulators.append(m.articulator)

    middle_freq = Counter(middles)
    prefix_freq = Counter(prefixes)
    suffix_freq = Counter(suffixes)
    tc = len(tokens) or 1

    # Top-5 MIDDLEs
    top5_middles = middle_freq.most_common(5)

    # Unique MIDDLEs (appear only in this folio across all B)
    # Will compute after collecting all
    folio_data[folio] = {
        'token_count': len(tokens),
        'line_count': len(lines),
        'paragraph_count': len(paragraphs),
        'tokens_per_line': len(tokens) / len(lines) if lines else 0,
        'unique_middle_count': len(middle_freq),
        'middle_freq': middle_freq,
        'prefix_freq': prefix_freq,
        'suffix_freq': suffix_freq,
        'top5_middles': top5_middles,
        'compound_rate': compound_count / tc,
        'extension_chars': extension_chars,
        'mean_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
        'mean_middle_length': sum(middle_lengths) / len(middle_lengths) if middle_lengths else 0,
        'articulator_rate': len(articulators) / tc,
        'prefix_diversity': len(prefix_freq) / tc,
        'suffix_diversity': len(suffix_freq) / tc,
        'middle_diversity': len(middle_freq) / tc,
    }

    if (i + 1) % 20 == 0:
        print(f"  {i + 1}/{len(b_folios)}...")

# --- Compute folio-unique MIDDLEs ---
# A MIDDLE is "folio-unique" if it only appears in one folio
all_middle_folios = defaultdict(set)
for folio, data in folio_data.items():
    for mid in data['middle_freq']:
        all_middle_folios[mid].add(folio)

for folio, data in folio_data.items():
    unique_mids = [m for m in data['middle_freq']
                   if len(all_middle_folios[m]) == 1]
    data['folio_unique_middles'] = unique_mids
    data['folio_unique_count'] = len(unique_mids)
    data['folio_unique_rate'] = len(unique_mids) / data['unique_middle_count'] if data['unique_middle_count'] else 0

# --- Compute variance across folios for each numeric feature ---
numeric_features = [
    'token_count', 'line_count', 'paragraph_count', 'tokens_per_line',
    'unique_middle_count', 'compound_rate', 'mean_word_length',
    'mean_middle_length', 'articulator_rate', 'prefix_diversity',
    'suffix_diversity', 'middle_diversity', 'folio_unique_count',
    'folio_unique_rate',
]

print(f"\n{'='*70}")
print(f"FEATURE VARIANCE ACROSS {len(folio_data)} FOLIOS")
print(f"{'='*70}")
print(f"{'Feature':<25s} {'Mean':>8s} {'Std':>8s} {'CV':>8s} {'Min':>8s} {'Max':>8s}")
print(f"{'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

feature_cv = {}
for feat in numeric_features:
    vals = [folio_data[f][feat] for f in folio_data]
    mean_v = sum(vals) / len(vals)
    std_v = (sum((v - mean_v)**2 for v in vals) / len(vals)) ** 0.5
    cv = std_v / mean_v if mean_v > 0 else 0
    min_v = min(vals)
    max_v = max(vals)
    feature_cv[feat] = cv
    print(f"{feat:<25s} {mean_v:8.3f} {std_v:8.3f} {cv:8.3f} {min_v:8.3f} {max_v:8.3f}")

# --- Rank by coefficient of variation (higher = more discriminating) ---
print(f"\n{'='*70}")
print(f"FEATURES RANKED BY DISCRIMINATION POWER (CV)")
print(f"{'='*70}")
for feat, cv in sorted(feature_cv.items(), key=lambda x: x[1], reverse=True):
    bar = '#' * int(cv * 20)
    print(f"  {feat:<25s} CV={cv:.3f} {bar}")

# --- Top-5 MIDDLE overlap analysis ---
# How much do folios share their top MIDDLEs?
print(f"\n{'='*70}")
print(f"TOP-5 MIDDLE VOCABULARY OVERLAP")
print(f"{'='*70}")

all_top5 = {}
for folio, data in folio_data.items():
    all_top5[folio] = set(m for m, c in data['top5_middles'])

# Pairwise Jaccard similarity of top-5 MIDDLEs
jaccard_sims = []
folios_list = sorted(folio_data.keys())
for i in range(len(folios_list)):
    for j in range(i + 1, len(folios_list)):
        s1 = all_top5[folios_list[i]]
        s2 = all_top5[folios_list[j]]
        if s1 or s2:
            jacc = len(s1 & s2) / len(s1 | s2)
            jaccard_sims.append(jacc)

mean_jacc = sum(jaccard_sims) / len(jaccard_sims) if jaccard_sims else 0
print(f"Mean pairwise Jaccard (top-5 MIDDLEs): {mean_jacc:.3f}")
print(f"  1.0 = all folios have identical top-5")
print(f"  0.0 = all folios have completely different top-5")

# Most common top-5 MIDDLEs across all folios
global_top5 = Counter()
for folio, data in folio_data.items():
    for m, c in data['top5_middles']:
        global_top5[m] += 1

print(f"\nMIDDLEs appearing in most folios' top-5:")
for mid, count in global_top5.most_common(15):
    pct = 100 * count / len(folio_data)
    print(f"  '{mid}': in {count}/{len(folio_data)} folios' top-5 ({pct:.0f}%)")

# --- Extension character distribution ---
print(f"\n{'='*70}")
print(f"EXTENSION CHARACTER DISTRIBUTION")
print(f"{'='*70}")

global_ext = Counter()
for folio, data in folio_data.items():
    global_ext.update(data['extension_chars'])

print(f"Extension chars (modifiers on compound MIDDLEs):")
for ch, count in global_ext.most_common(20):
    print(f"  '{ch}': {count} occurrences")

# --- Most distinctive folios ---
print(f"\n{'='*70}")
print(f"MOST DISTINCTIVE FOLIOS (by folio-unique MIDDLE count)")
print(f"{'='*70}")

by_unique = sorted(folio_data.items(), key=lambda x: x[1]['folio_unique_count'], reverse=True)
for folio, data in by_unique[:15]:
    uniq_examples = data['folio_unique_middles'][:5]
    print(f"  {folio:8s}: {data['folio_unique_count']:3d} unique MIDDLEs "
          f"(of {data['unique_middle_count']}) "
          f"| examples: {', '.join(uniq_examples)}")

print(f"\nLEAST DISTINCTIVE FOLIOS")
for folio, data in by_unique[-10:]:
    print(f"  {folio:8s}: {data['folio_unique_count']:3d} unique MIDDLEs "
          f"(of {data['unique_middle_count']})")

# --- Most different folio pairs ---
print(f"\n{'='*70}")
print(f"MOST DIFFERENT FOLIO PAIRS (by top-5 MIDDLE Jaccard distance)")
print(f"{'='*70}")

pair_distances = []
for i in range(len(folios_list)):
    for j in range(i + 1, len(folios_list)):
        s1 = all_top5[folios_list[i]]
        s2 = all_top5[folios_list[j]]
        if s1 or s2:
            jacc = len(s1 & s2) / len(s1 | s2)
            pair_distances.append((1 - jacc, folios_list[i], folios_list[j]))

pair_distances.sort(reverse=True)
for dist, f1, f2 in pair_distances[:10]:
    t1 = ', '.join(m for m, c in folio_data[f1]['top5_middles'])
    t2 = ', '.join(m for m, c in folio_data[f2]['top5_middles'])
    print(f"  {f1} vs {f2}: distance={dist:.2f}")
    print(f"    {f1}: {t1}")
    print(f"    {f2}: {t2}")

# --- Paragraph count distribution ---
print(f"\n{'='*70}")
print(f"PARAGRAPH COUNT DISTRIBUTION")
print(f"{'='*70}")
para_counts = Counter(data['paragraph_count'] for data in folio_data.values())
for pc, count in sorted(para_counts.items()):
    bar = '#' * count
    print(f"  {pc} paragraphs: {count} folios {bar}")

# --- Write results ---
output = {
    'title': 'Folio Discrimination Analysis',
    'folio_count': len(folio_data),
    'feature_cv': feature_cv,
    'top5_overlap': {
        'mean_jaccard': round(mean_jacc, 4),
        'most_common_top5': [(m, c) for m, c in global_top5.most_common(15)],
    },
    'most_distinctive': [
        {'folio': f, 'unique_count': d['folio_unique_count'],
         'total_middles': d['unique_middle_count'],
         'examples': d['folio_unique_middles'][:10]}
        for f, d in by_unique[:20]
    ],
    'paragraph_distribution': dict(para_counts),
}

with open('results/folio_discrimination.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote results to results/folio_discrimination.json")

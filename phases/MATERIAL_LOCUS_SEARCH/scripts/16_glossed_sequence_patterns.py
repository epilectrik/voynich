#!/usr/bin/env python3
"""
Test 16: Glossed Token Sequence Pattern Mining

Uses middle_dictionary.json glosses to decode token sequences per line,
identifies "gloss gaps" (unglossed rare MIDDLEs between operational tokens),
and determines whether these gaps are systematically positioned (suggesting
material encoding) or randomly distributed (suggesting vocabulary incompleteness).
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# ============================================================
# Configuration
# ============================================================
TARGET_FOLIOS = {
    'B': ['f78r', 'f76r'],
    'H': ['f43r', 'f39r'],
    'S': ['f107r', 'f111r'],
    'T': ['f66r', 'f85r1'],
    'C': ['f86v3', 'f86v5'],
}

OUTPUT_PATH = Path(__file__).parent.parent / 'results' / 'glossed_sequence_patterns.json'

# ============================================================
# Levenshtein distance
# ============================================================
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    return prev_row[-1]


# ============================================================
# Load data
# ============================================================
print("Loading transcript and morphology...")
tx = Transcript()
morph = Morphology()

dict_path = Path(__file__).parent.parent.parent.parent / 'data' / 'middle_dictionary.json'
with open(dict_path) as f:
    mid_dict_raw = json.load(f)

mid_dict = mid_dict_raw.get('middles', mid_dict_raw)

# Build gloss lookup: middle_string -> gloss
gloss_lookup = {}
glossed_middles = set()
for mid_str, info in mid_dict.items():
    if isinstance(info, dict):
        g = info.get('gloss')
        if g:
            gloss_lookup[mid_str] = g
            glossed_middles.add(mid_str)

print(f"Glossed MIDDLEs: {len(glossed_middles)}")
print(f"Total dictionary entries: {len(mid_dict)}")

# ============================================================
# Collect tokens by folio+line
# ============================================================
all_target_folios = set()
for folios in TARGET_FOLIOS.values():
    all_target_folios.update(folios)

# Map folio -> section
folio_to_section = {}
for sec, folios in TARGET_FOLIOS.items():
    for f in folios:
        folio_to_section[f] = sec

# Collect tokens: folio -> line -> [tokens in order]
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if token.folio in all_target_folios:
        folio_line_tokens[token.folio][token.line].append(token)

# Also get global MIDDLE frequency for "rare" classification
all_b_middles = Counter()
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_':
        all_b_middles[m.middle] += 1

# ============================================================
# Build gloss sequences
# ============================================================
print("\n" + "="*80)
print("GLOSS SEQUENCES BY FOLIO")
print("="*80)

# Data collection structures
folio_sequences = {}  # folio -> {line -> gloss_seq}
all_gaps = []  # list of gap info dicts
gap_by_section = defaultdict(list)
gap_positions = defaultdict(int)  # 'line_start', 'line_end', 'line_mid', 'par_start'
all_gloss_bigrams = Counter()
all_gloss_trigrams = Counter()
section_bigrams = defaultdict(Counter)
section_trigrams = defaultdict(Counter)
glossed_count = 0
unglossed_count = 0
total_tokens_processed = 0

# Compute common MIDDLEs set (top 100 by frequency)
common_middles = set(m for m, c in all_b_middles.most_common(100))

for section, folios in TARGET_FOLIOS.items():
    for folio in folios:
        print(f"\n--- {folio} (section {section}) ---")
        folio_sequences[folio] = {}
        lines = sorted(folio_line_tokens[folio].keys(), key=lambda x: int(x) if x.isdigit() else 0)

        if not lines:
            print(f"  [No lines found for {folio}]")
            continue

        for line_num in lines:
            tokens = folio_line_tokens[folio][line_num]
            gloss_seq = []

            for idx, token in enumerate(tokens):
                total_tokens_processed += 1
                m = morph.extract(token.word)
                mid = m.middle if (m.middle and m.middle != '_EMPTY_') else None

                if mid is None:
                    gloss_seq.append(('--', token.word, None))
                    continue

                gloss = gloss_lookup.get(mid)
                if gloss:
                    gloss_seq.append((gloss, token.word, mid))
                    glossed_count += 1
                else:
                    gloss_seq.append(('?', token.word, mid))
                    unglossed_count += 1

                    # Analyze this gap
                    freq = all_b_middles.get(mid, 0)

                    # Minimum edit distance to any glossed MIDDLE
                    min_dist = 999
                    closest_glossed = None
                    for gm in glossed_middles:
                        d = levenshtein(mid, gm)
                        if d < min_dist:
                            min_dist = d
                            closest_glossed = gm

                    # Minimum edit distance to common MIDDLEs
                    min_dist_common = 999
                    closest_common = None
                    for cm in common_middles:
                        d = levenshtein(mid, cm)
                        if d < min_dist_common:
                            min_dist_common = d
                            closest_common = cm

                    # Position classification
                    is_line_start = (idx == 0)
                    is_line_end = (idx == len(tokens) - 1)
                    is_par_start = token.par_initial
                    pos_label = 'par_start' if is_par_start else ('line_start' if is_line_start else ('line_end' if is_line_end else 'line_mid'))

                    gap_info = {
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'position_in_line': idx,
                        'total_in_line': len(tokens),
                        'pos_label': pos_label,
                        'middle': mid,
                        'word': token.word,
                        'frequency': freq,
                        'min_dist_glossed': min_dist,
                        'closest_glossed': closest_glossed,
                        'closest_glossed_gloss': gloss_lookup.get(closest_glossed, '?'),
                        'min_dist_common': min_dist_common,
                        'closest_common': closest_common,
                        'morphologically_distinct': min_dist > 2,
                    }
                    all_gaps.append(gap_info)
                    gap_by_section[section].append(gap_info)
                    gap_positions[pos_label] += 1

            folio_sequences[folio][line_num] = gloss_seq

            # Print the gloss sequence
            display = []
            for gloss, word, mid in gloss_seq:
                if gloss == '--':
                    display.append(f"[{word}:no-mid]")
                elif gloss == '?':
                    display.append(f"[{word}:{mid}:?]")
                else:
                    display.append(gloss)
            print(f"  L{line_num}: {' -> '.join(display)}")

            # Collect n-grams (only from glossed tokens)
            glosses_only = [g for g, w, m in gloss_seq if g not in ('--', '?')]
            for i in range(len(glosses_only) - 1):
                bg = (glosses_only[i], glosses_only[i+1])
                all_gloss_bigrams[bg] += 1
                section_bigrams[section][bg] += 1
            for i in range(len(glosses_only) - 2):
                tg = (glosses_only[i], glosses_only[i+1], glosses_only[i+2])
                all_gloss_trigrams[tg] += 1
                section_trigrams[section][tg] += 1


# ============================================================
# Analysis: Gloss gap patterns
# ============================================================
print("\n" + "="*80)
print("GLOSS GAP ANALYSIS")
print("="*80)

print(f"\nTotal tokens processed: {total_tokens_processed}")
print(f"Glossed: {glossed_count} ({100*glossed_count/max(1,total_tokens_processed):.1f}%)")
print(f"Unglossed (gaps): {len(all_gaps)} ({100*len(all_gaps)/max(1,total_tokens_processed):.1f}%)")

print(f"\n--- Gap Position Distribution ---")
for pos, count in sorted(gap_positions.items(), key=lambda x: -x[1]):
    pct = 100 * count / max(1, len(all_gaps))
    print(f"  {pos}: {count} ({pct:.1f}%)")

# Expected distribution (null model): proportion of token positions that are line_start/line_end/etc.
pos_expected = defaultdict(int)
for folio in all_target_folios:
    for line_num, tokens in folio_line_tokens[folio].items():
        for idx, token in enumerate(tokens):
            is_line_start = (idx == 0)
            is_line_end = (idx == len(tokens) - 1)
            is_par_start = token.par_initial
            pos_label = 'par_start' if is_par_start else ('line_start' if is_line_start else ('line_end' if is_line_end else 'line_mid'))
            pos_expected[pos_label] += 1

print(f"\n--- Expected Position Distribution (null model) ---")
total_pos = sum(pos_expected.values())
for pos in sorted(gap_positions.keys()):
    exp_count = pos_expected.get(pos, 0)
    exp_pct = 100 * exp_count / max(1, total_pos)
    obs_pct = 100 * gap_positions.get(pos, 0) / max(1, len(all_gaps))
    enrichment = obs_pct / max(0.01, exp_pct)
    print(f"  {pos}: expected {exp_pct:.1f}%, observed {obs_pct:.1f}%, enrichment {enrichment:.2f}x")

print(f"\n--- Gap Distribution by Section ---")
for sec in ['B', 'H', 'S', 'T', 'C']:
    gaps = gap_by_section.get(sec, [])
    n_tokens_sec = sum(len(tokens) for folio in TARGET_FOLIOS[sec] for tokens in folio_line_tokens[folio].values())
    rate = 100 * len(gaps) / max(1, n_tokens_sec)
    distinct = sum(1 for g in gaps if g['morphologically_distinct'])
    print(f"  Section {sec}: {len(gaps)} gaps in {n_tokens_sec} tokens ({rate:.1f}%), {distinct} morphologically distinct (dist>2)")

print(f"\n--- Morphological Distinctiveness of Gap MIDDLEs ---")
dist_counts = Counter()
for g in all_gaps:
    d = g['min_dist_glossed']
    bucket = '0' if d == 0 else ('1' if d == 1 else ('2' if d == 2 else ('3' if d == 3 else '4+')))
    dist_counts[bucket] += 1
for bucket in ['0', '1', '2', '3', '4+']:
    c = dist_counts.get(bucket, 0)
    pct = 100 * c / max(1, len(all_gaps))
    print(f"  Distance {bucket}: {c} ({pct:.1f}%)")

print(f"\n--- Gap MIDDLEs by Frequency ---")
freq_buckets = {'hapax (1)': 0, 'rare (2-5)': 0, 'moderate (6-20)': 0, 'common (>20)': 0}
for g in all_gaps:
    f = g['frequency']
    if f <= 1:
        freq_buckets['hapax (1)'] += 1
    elif f <= 5:
        freq_buckets['rare (2-5)'] += 1
    elif f <= 20:
        freq_buckets['moderate (6-20)'] += 1
    else:
        freq_buckets['common (>20)'] += 1
for bucket, count in freq_buckets.items():
    pct = 100 * count / max(1, len(all_gaps))
    print(f"  {bucket}: {count} ({pct:.1f}%)")

# Focus on morphologically distinct gaps (the interesting ones)
print(f"\n--- Morphologically Distinct Gap MIDDLEs (dist>2 from glossed) ---")
distinct_gaps = [g for g in all_gaps if g['morphologically_distinct']]
print(f"  Count: {len(distinct_gaps)} out of {len(all_gaps)} total gaps")
if distinct_gaps:
    # Group by section
    for sec in ['B', 'H', 'S', 'T', 'C']:
        sec_distinct = [g for g in distinct_gaps if g['section'] == sec]
        if sec_distinct:
            mids = Counter(g['middle'] for g in sec_distinct)
            print(f"  Section {sec} ({len(sec_distinct)} distinct gaps):")
            for mid, count in mids.most_common(10):
                example = next(g for g in sec_distinct if g['middle'] == mid)
                print(f"    {mid} (x{count}, freq={example['frequency']}, closest={example['closest_glossed']}={example['closest_glossed_gloss']}, dist={example['min_dist_glossed']})")

# ============================================================
# Repeated subsequence patterns
# ============================================================
print(f"\n" + "="*80)
print("REPEATED GLOSS SUBSEQUENCES")
print("="*80)

print(f"\n--- Most Common Gloss Bigrams (across all folios) ---")
for bg, count in all_gloss_bigrams.most_common(20):
    print(f"  {bg[0]} -> {bg[1]}: {count}")

print(f"\n--- Most Common Gloss Trigrams ---")
for tg, count in all_gloss_trigrams.most_common(15):
    print(f"  {tg[0]} -> {tg[1]} -> {tg[2]}: {count}")

# Section-specific patterns: find bigrams that appear in only one section
print(f"\n--- Section-Specific Bigrams (appear in only one section, count>=2) ---")
for sec in ['B', 'H', 'S', 'T', 'C']:
    unique_bgs = []
    for bg, count in section_bigrams[sec].most_common():
        if count >= 2:
            # Check other sections
            in_others = any(section_bigrams[other_sec][bg] > 0 for other_sec in ['B', 'H', 'S', 'T', 'C'] if other_sec != sec)
            if not in_others:
                unique_bgs.append((bg, count))
    if unique_bgs:
        print(f"  Section {sec}:")
        for bg, count in unique_bgs[:5]:
            print(f"    {bg[0]} -> {bg[1]}: {count}")

# Cross-section patterns: find bigrams that appear in 3+ sections
print(f"\n--- Cross-Section Bigrams (appear in 3+ sections, suggesting shared procedures) ---")
cross_bgs = []
for bg, count in all_gloss_bigrams.most_common():
    if count >= 3:
        sections_present = [sec for sec in ['B', 'H', 'S', 'T', 'C'] if section_bigrams[sec][bg] > 0]
        if len(sections_present) >= 3:
            cross_bgs.append((bg, count, sections_present))
if cross_bgs:
    for bg, count, secs in cross_bgs[:10]:
        print(f"  {bg[0]} -> {bg[1]}: {count} (sections: {', '.join(secs)})")

# ============================================================
# Narrative assessment
# ============================================================
print(f"\n" + "="*80)
print("NARRATIVE ASSESSMENT")
print("="*80)

# Calculate key metrics for verdict
total_gap_rate = len(all_gaps) / max(1, total_tokens_processed)
distinct_ratio = len(distinct_gaps) / max(1, len(all_gaps))

# Position non-uniformity: chi-square-like metric
position_labels = ['line_start', 'line_end', 'line_mid', 'par_start']
pos_observed_pcts = {p: gap_positions.get(p, 0) / max(1, len(all_gaps)) for p in position_labels}
pos_expected_pcts = {p: pos_expected.get(p, 0) / max(1, total_pos) for p in position_labels}
pos_enrichments = {p: pos_observed_pcts[p] / max(0.001, pos_expected_pcts[p]) for p in position_labels}
max_enrichment = max(pos_enrichments.values()) if pos_enrichments else 1.0

# Section variation
section_gap_rates = {}
for sec in ['B', 'H', 'S', 'T', 'C']:
    n_tok = sum(len(tokens) for folio in TARGET_FOLIOS[sec] for tokens in folio_line_tokens[folio].values())
    n_gap = len(gap_by_section.get(sec, []))
    section_gap_rates[sec] = n_gap / max(1, n_tok)
rate_range = max(section_gap_rates.values()) - min(section_gap_rates.values()) if section_gap_rates else 0

print(f"Gap rate: {100*total_gap_rate:.1f}%")
print(f"Morphologically distinct fraction: {100*distinct_ratio:.1f}%")
print(f"Max positional enrichment: {max_enrichment:.2f}x")
print(f"Section gap rate range: {100*rate_range:.1f} percentage points")

# Verdict logic
position_systematic = max_enrichment > 1.5
section_specific = rate_range > 0.05  # >5 pp difference
has_distinct_gaps = len(distinct_gaps) > 5

if position_systematic and section_specific:
    verdict = "PASS"
    narrative = (
        f"Gloss gaps are systematically positioned (max enrichment {max_enrichment:.2f}x at "
        f"{max(pos_enrichments, key=pos_enrichments.get)}) and section-specific "
        f"(gap rate range {100*rate_range:.1f}pp). "
        f"{len(distinct_gaps)} gaps involve morphologically distinct MIDDLEs (edit distance >2 from any glossed MIDDLE), "
        f"suggesting these are not simple variants of known operations but potentially encode "
        f"material-specific or context-specific information that the operational gloss system does not capture."
    )
elif position_systematic or section_specific:
    verdict = "WEAK_PASS"
    narrative = (
        f"Partial systematic signal: position_systematic={position_systematic} (enrichment {max_enrichment:.2f}x), "
        f"section_specific={section_specific} (range {100*rate_range:.1f}pp). "
        f"Gaps show some structure but not enough to definitively distinguish material encoding from vocabulary incompleteness."
    )
else:
    verdict = "FAIL"
    narrative = (
        f"Gloss gaps appear randomly distributed. Positional enrichment is only {max_enrichment:.2f}x "
        f"and section gap rates differ by only {100*rate_range:.1f}pp. "
        f"This is more consistent with vocabulary incompleteness than systematic material encoding."
    )

print(f"\nVerdict: {verdict}")
print(f"Narrative: {narrative}")

# ============================================================
# Build output JSON
# ============================================================
# Example gloss sequences (first 5 lines per folio)
example_sequences = {}
for folio, lines in folio_sequences.items():
    sorted_lines = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)
    example_sequences[folio] = {}
    for line_num in sorted_lines[:5]:
        seq = lines[line_num]
        example_sequences[folio][line_num] = [
            {'gloss': g, 'word': w, 'middle': m} for g, w, m in seq
        ]

# Repeated subsequences
repeated_bigrams = [
    {'pattern': list(bg), 'count': count}
    for bg, count in all_gloss_bigrams.most_common(20)
]
repeated_trigrams = [
    {'pattern': list(tg), 'count': count}
    for tg, count in all_gloss_trigrams.most_common(15)
]

# Section-specific bigrams for JSON
section_specific_json = {}
for sec in ['B', 'H', 'S', 'T', 'C']:
    unique_bgs = []
    for bg, count in section_bigrams[sec].most_common():
        if count >= 2:
            in_others = any(section_bigrams[other_sec][bg] > 0 for other_sec in ['B', 'H', 'S', 'T', 'C'] if other_sec != sec)
            if not in_others:
                unique_bgs.append({'pattern': list(bg), 'count': count})
    if unique_bgs:
        section_specific_json[sec] = unique_bgs[:5]

# Cross-section bigrams for JSON
cross_section_json = []
for bg, count, secs in cross_bgs[:10] if cross_bgs else []:
    cross_section_json.append({'pattern': list(bg), 'count': count, 'sections': secs})

output = {
    'test': 'T16_glossed_sequence_patterns',
    'description': 'Glossed token sequence pattern mining using middle_dictionary.json',
    'folios_analyzed': {sec: folios for sec, folios in TARGET_FOLIOS.items()},
    'summary': {
        'total_tokens': total_tokens_processed,
        'glossed_tokens': glossed_count,
        'gloss_gaps': len(all_gaps),
        'gap_rate_pct': round(100 * total_gap_rate, 1),
        'morphologically_distinct_gaps': len(distinct_gaps),
        'distinct_fraction_pct': round(100 * distinct_ratio, 1),
    },
    'gap_position_distribution': {
        pos: {
            'count': gap_positions.get(pos, 0),
            'observed_pct': round(100 * pos_observed_pcts.get(pos, 0), 1),
            'expected_pct': round(100 * pos_expected_pcts.get(pos, 0), 1),
            'enrichment': round(pos_enrichments.get(pos, 0), 2),
        }
        for pos in position_labels
    },
    'gap_by_section': {
        sec: {
            'total_tokens': sum(len(tokens) for folio in TARGET_FOLIOS[sec] for tokens in folio_line_tokens[folio].values()),
            'gaps': len(gap_by_section.get(sec, [])),
            'gap_rate_pct': round(100 * section_gap_rates.get(sec, 0), 1),
            'morphologically_distinct': sum(1 for g in gap_by_section.get(sec, []) if g['morphologically_distinct']),
        }
        for sec in ['B', 'H', 'S', 'T', 'C']
    },
    'gap_frequency_distribution': freq_buckets,
    'gap_edit_distance_distribution': {k: v for k, v in sorted(dist_counts.items())},
    'example_sequences': example_sequences,
    'repeated_subsequences': {
        'bigrams': repeated_bigrams,
        'trigrams': repeated_trigrams,
    },
    'section_specific_patterns': section_specific_json,
    'cross_section_patterns': cross_section_json,
    'distinct_gap_examples': [
        {
            'middle': g['middle'],
            'word': g['word'],
            'folio': g['folio'],
            'section': g['section'],
            'position': g['pos_label'],
            'frequency': g['frequency'],
            'closest_glossed': g['closest_glossed'],
            'closest_glossed_gloss': g['closest_glossed_gloss'],
            'edit_distance': g['min_dist_glossed'],
        }
        for g in sorted(distinct_gaps, key=lambda x: -x['min_dist_glossed'])[:30]
    ],
    'verdict': verdict,
    'narrative': narrative,
    'methodology': {
        'gloss_source': 'data/middle_dictionary.json (v2.0, 340 glossed MIDDLEs)',
        'morphological_distinctiveness': 'Levenshtein distance >2 from any glossed MIDDLE',
        'position_enrichment': 'Observed vs expected gap rate by position (line_start/end/mid/par_start)',
        'section_specificity': 'Gap rate variation across B/H/S/T/C sections',
        'pass_criteria': 'Max positional enrichment >1.5x AND section gap rate range >5pp',
    },
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {OUTPUT_PATH}")

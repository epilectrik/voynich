#!/usr/bin/env python3
"""
Test 12: Cross-Paragraph Material Persistence Within Folios

Question: Do folio-persistent rare MIDDLEs (appearing in >80% of a folio's
paragraphs but in <15 folios total) exist as material markers?

Method:
1. Load all Currier B tokens (H track, no labels, no uncertain).
2. Compute folio count for each MIDDLE (how many folios does it appear in?).
3. Define "rare" MIDDLEs as those appearing in <15 folios (out of ~82 B folios).
4. For each folio with 3+ paragraphs:
   - For each rare MIDDLE on that folio, compute what fraction of the folio's
     paragraphs contain it.
   - Flag MIDDLEs appearing in >80% of paragraphs as "folio-persistent".
5. Collect all folio-persistent rare MIDDLEs.
6. Test edit distance from common MIDDLEs:
   - Common = appears in 40+ folios.
   - For each persistent rare MIDDLE, compute Levenshtein distance to nearest
     common MIDDLE.
   - Per C939 methodology: if most are distance-1, they're operational variants
     (not material markers).
7. Check section distribution: are persistent rare MIDDLEs section-specific?

Pass criteria: Rare-persistent MIDDLEs exist (>10), are morphologically distant
               (mean distance > 2.0), section-specific.
Fail criteria: All distance-1 from common MIDDLEs -- operational variants, not
               material markers.
"""

import sys
import json
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# CONSTANTS
# ============================================================
RESULTS_DIR = Path('C:/git/voynich/phases/MATERIAL_LOCUS_SEARCH/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = RESULTS_DIR / 'cross_paragraph_persistence.json'

RARE_FOLIO_THRESHOLD = 15       # MIDDLE appears in <15 folios -> "rare"
COMMON_FOLIO_THRESHOLD = 40     # MIDDLE appears in 40+ folios -> "common"
MIN_PARAGRAPHS_PER_FOLIO = 3    # Only test folios with 3+ paragraphs
PERSISTENCE_THRESHOLD = 0.80    # MIDDLE must appear in >80% of folio paragraphs
DISTANCE_PASS_THRESHOLD = 2.0   # Mean Levenshtein distance for PASS


# ============================================================
# Levenshtein distance (simple DP implementation)
# ============================================================
def levenshtein(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
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
# STEP 1: Load Currier B tokens and extract MIDDLEs
# ============================================================
print("Loading Currier B tokens...")
tx = Transcript()
morph = Morphology()

# Collect all B tokens with their metadata and extracted MIDDLE
all_tokens = []
for t in tx.currier_b():
    m = morph.extract(t.word)
    mid = m.middle
    if not mid or mid == '_EMPTY_':
        continue
    all_tokens.append({
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'section': t.section,
        'middle': mid,
        'par_initial': t.par_initial,
    })

print(f"Total Currier B tokens with valid MIDDLE: {len(all_tokens)}")

# ============================================================
# STEP 2: Build paragraph structures using par_initial flags
# ============================================================
print("\nBuilding paragraph structures...")

# Build paragraphs: each paragraph is a list of tokens
paragraphs = []
current_par = None
par_num_by_folio = defaultdict(int)

for t in all_tokens:
    folio = t['folio']
    if t['par_initial']:
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'middles': set(),
        }
        paragraphs.append(current_par)

    if current_par is not None and current_par['folio'] == folio:
        current_par['middles'].add(t['middle'])
    elif current_par is None or current_par['folio'] != folio:
        # Tokens before first par_initial in a new folio: create implicit paragraph
        par_num_by_folio[folio] += 1
        current_par = {
            'folio': folio,
            'section': t['section'],
            'par_num': par_num_by_folio[folio],
            'middles': {t['middle']},
        }
        paragraphs.append(current_par)

print(f"Total paragraphs: {len(paragraphs)}")

# ============================================================
# STEP 3: Pre-compute per-folio and per-MIDDLE statistics
# ============================================================
print("\nComputing per-folio and per-MIDDLE statistics...")

# Group paragraphs by folio
folio_paragraphs = defaultdict(list)
for p in paragraphs:
    folio_paragraphs[p['folio']].append(p)

# Folio count per MIDDLE: how many distinct folios contain each MIDDLE?
middle_folios = defaultdict(set)
for t in all_tokens:
    middle_folios[t['middle']].add(t['folio'])

middle_folio_count = {mid: len(folios) for mid, folios in middle_folios.items()}

# Section per folio (take majority section from tokens)
folio_sections = defaultdict(Counter)
for t in all_tokens:
    folio_sections[t['folio']][t['section']] += 1

folio_section = {}
for folio, sec_counts in folio_sections.items():
    folio_section[folio] = sec_counts.most_common(1)[0][0]

# Classify MIDDLEs
all_middles = set(middle_folio_count.keys())
rare_middles = {m for m, c in middle_folio_count.items() if c < RARE_FOLIO_THRESHOLD}
common_middles = {m for m, c in middle_folio_count.items() if c >= COMMON_FOLIO_THRESHOLD}

total_b_folios = len(folio_paragraphs)
print(f"Total Currier B folios: {total_b_folios}")
print(f"Unique MIDDLEs: {len(all_middles)}")
print(f"Rare MIDDLEs (<{RARE_FOLIO_THRESHOLD} folios): {len(rare_middles)}")
print(f"Common MIDDLEs (>={COMMON_FOLIO_THRESHOLD} folios): {len(common_middles)}")

# Folios with enough paragraphs
eligible_folios = {f: pars for f, pars in folio_paragraphs.items()
                   if len(pars) >= MIN_PARAGRAPHS_PER_FOLIO}
print(f"Folios with >= {MIN_PARAGRAPHS_PER_FOLIO} paragraphs: {len(eligible_folios)}")


# ============================================================
# STEP 4: Find folio-persistent rare MIDDLEs
# ============================================================
print("\nSearching for folio-persistent rare MIDDLEs...")

# For each eligible folio, check which rare MIDDLEs persist across >80% of paragraphs
persistent_records = []  # list of (middle, folio, paragraph_fraction, n_paragraphs)

for folio, pars in eligible_folios.items():
    n_pars = len(pars)
    # Collect all rare MIDDLEs present on this folio
    folio_rare_middles = set()
    for p in pars:
        folio_rare_middles.update(p['middles'] & rare_middles)

    # For each rare MIDDLE, compute paragraph persistence
    for mid in folio_rare_middles:
        pars_with_mid = sum(1 for p in pars if mid in p['middles'])
        frac = pars_with_mid / n_pars
        if frac > PERSISTENCE_THRESHOLD:
            persistent_records.append({
                'middle': mid,
                'folio': folio,
                'section': folio_section.get(folio, 'UNK'),
                'paragraph_fraction': round(frac, 4),
                'n_paragraphs': n_pars,
                'paragraphs_with_middle': pars_with_mid,
                'folio_count': middle_folio_count[mid],
            })

# Deduplicate: unique persistent (middle, folio) pairs
n_persistent_pairs = len(persistent_records)
persistent_middles = sorted(set(r['middle'] for r in persistent_records))
n_persistent_middles = len(persistent_middles)

print(f"Folio-persistent rare MIDDLE instances: {n_persistent_pairs}")
print(f"Unique persistent rare MIDDLEs: {n_persistent_middles}")

# Diagnostic: show the distribution of paragraph persistence fractions
# to understand whether the threshold is too strict or the phenomenon is absent
print("\n--- Diagnostic: Paragraph persistence distribution for rare MIDDLEs ---")
all_fracs = []
for folio, pars in eligible_folios.items():
    n_pars = len(pars)
    folio_rare_middles = set()
    for p in pars:
        folio_rare_middles.update(p['middles'] & rare_middles)
    for mid in folio_rare_middles:
        pars_with_mid = sum(1 for p in pars if mid in p['middles'])
        frac = pars_with_mid / n_pars
        all_fracs.append(frac)

if all_fracs:
    # Bucket the fractions
    buckets = {'0-20%': 0, '20-40%': 0, '40-60%': 0, '60-80%': 0, '80-100%': 0}
    for f in all_fracs:
        if f <= 0.20:
            buckets['0-20%'] += 1
        elif f <= 0.40:
            buckets['20-40%'] += 1
        elif f <= 0.60:
            buckets['40-60%'] += 1
        elif f <= 0.80:
            buckets['60-80%'] += 1
        else:
            buckets['80-100%'] += 1
    print(f"  Total (rare MIDDLE, eligible folio) pairs: {len(all_fracs)}")
    for bucket, count in buckets.items():
        print(f"  {bucket}: {count} ({count/len(all_fracs):.1%})")

    # Show the highest-persistence cases
    # Gather individual records with frac > 0.50
    near_persistent = []
    for folio, pars in eligible_folios.items():
        n_pars = len(pars)
        folio_rare_middles_local = set()
        for p in pars:
            folio_rare_middles_local.update(p['middles'] & rare_middles)
        for mid in folio_rare_middles_local:
            pars_with_mid = sum(1 for p in pars if mid in p['middles'])
            frac = pars_with_mid / n_pars
            if frac > 0.50:
                near_persistent.append((mid, folio, frac, pars_with_mid, n_pars,
                                        middle_folio_count[mid]))

    near_persistent.sort(key=lambda x: -x[2])
    print(f"\n  Near-persistent cases (frac > 50%): {len(near_persistent)}")
    for mid, folio, frac, pw, np_, fc in near_persistent[:20]:
        print(f"    {mid:15s} folio={folio:6s} frac={frac:.2f} "
              f"({pw}/{np_} pars) folio_count={fc}")
    # If strict threshold yields nothing, try relaxed thresholds to characterize
    # the boundary
    if n_persistent_middles == 0:
        print("\n  Relaxed threshold scan:")
        for test_thresh in [0.70, 0.60, 0.50]:
            relaxed_count = sum(1 for f in all_fracs if f > test_thresh)
            relaxed_unique = set()
            for folio, pars in eligible_folios.items():
                n_pars = len(pars)
                folio_rare_middles_local = set()
                for p in pars:
                    folio_rare_middles_local.update(p['middles'] & rare_middles)
                for mid in folio_rare_middles_local:
                    pars_with_mid = sum(1 for p in pars if mid in p['middles'])
                    frac = pars_with_mid / n_pars
                    if frac > test_thresh:
                        relaxed_unique.add(mid)
            print(f"    >{test_thresh:.0%} threshold: {relaxed_count} instances, "
                  f"{len(relaxed_unique)} unique MIDDLEs")

print("--- End diagnostic ---\n")

# If strict threshold (>80%) yields nothing, use >60% for the distance/section
# analysis to still provide informative results
if n_persistent_middles == 0:
    RELAXED_THRESHOLD = 0.60
    print(f"Strict >80% threshold yielded 0 results. "
          f"Running analysis with relaxed >{RELAXED_THRESHOLD:.0%} threshold...")
    for folio, pars in eligible_folios.items():
        n_pars = len(pars)
        folio_rare_middles_local = set()
        for p in pars:
            folio_rare_middles_local.update(p['middles'] & rare_middles)
        for mid in folio_rare_middles_local:
            pars_with_mid = sum(1 for p in pars if mid in p['middles'])
            frac = pars_with_mid / n_pars
            if frac > RELAXED_THRESHOLD:
                persistent_records.append({
                    'middle': mid,
                    'folio': folio,
                    'section': folio_section.get(folio, 'UNK'),
                    'paragraph_fraction': round(frac, 4),
                    'n_paragraphs': n_pars,
                    'paragraphs_with_middle': pars_with_mid,
                    'folio_count': middle_folio_count[mid],
                })

    n_persistent_pairs = len(persistent_records)
    persistent_middles = sorted(set(r['middle'] for r in persistent_records))
    n_persistent_middles = len(persistent_middles)
    folio_persistent_counts = Counter()
    for r in persistent_records:
        folio_persistent_counts[r['folio']] += 1

    print(f"Relaxed: {n_persistent_pairs} instances, "
          f"{n_persistent_middles} unique persistent rare MIDDLEs")
    used_threshold = RELAXED_THRESHOLD
else:
    used_threshold = PERSISTENCE_THRESHOLD

if persistent_records:
    # Show top examples sorted by persistence fraction then folio count
    sorted_records = sorted(persistent_records,
                            key=lambda r: (-r['paragraph_fraction'], r['folio_count']))
    print("\nTop 20 persistent rare MIDDLE instances:")
    for r in sorted_records[:20]:
        print(f"  {r['middle']:15s} folio={r['folio']:6s} section={r['section']:3s} "
              f"par_frac={r['paragraph_fraction']:.2f} "
              f"({r['paragraphs_with_middle']}/{r['n_paragraphs']} pars) "
              f"folio_count={r['folio_count']}")


# ============================================================
# STEP 5: Edit distance analysis
# ============================================================
print("\n=== Edit Distance Analysis ===")

if not persistent_middles or not common_middles:
    print("Cannot compute distances: no persistent or common MIDDLEs found.")
    distances = {}
    mean_distance = 0.0
    median_distance = 0.0
    distance_1_count = 0
    distance_1_fraction = 0.0
else:
    # Pre-compute: for each persistent rare MIDDLE, find nearest common MIDDLE
    common_list = sorted(common_middles)
    distances = {}

    for mid in persistent_middles:
        min_dist = float('inf')
        nearest = None
        for cmid in common_list:
            d = levenshtein(mid, cmid)
            if d < min_dist:
                min_dist = d
                nearest = cmid
        distances[mid] = {
            'distance': min_dist,
            'nearest_common': nearest,
            'folio_count': middle_folio_count[mid],
        }

    dist_values = [d['distance'] for d in distances.values()]
    mean_distance = sum(dist_values) / len(dist_values)
    sorted_dists = sorted(dist_values)
    median_distance = sorted_dists[len(sorted_dists) // 2]
    distance_1_count = sum(1 for d in dist_values if d <= 1)
    distance_1_fraction = distance_1_count / len(dist_values) if dist_values else 0.0

    print(f"Persistent rare MIDDLEs analyzed: {len(distances)}")
    print(f"Mean distance to nearest common: {mean_distance:.2f}")
    print(f"Median distance to nearest common: {median_distance:.1f}")
    print(f"Distance <= 1 (operational variants): {distance_1_count}/{len(dist_values)} "
          f"({distance_1_fraction:.1%})")
    print(f"Distance >= 3 (morphologically distinct): "
          f"{sum(1 for d in dist_values if d >= 3)}/{len(dist_values)}")

    # Show distance distribution
    dist_counter = Counter(dist_values)
    print("\nDistance distribution:")
    for d in sorted(dist_counter.keys()):
        bar = '#' * dist_counter[d]
        print(f"  d={d}: {dist_counter[d]:3d} {bar}")

    # Show sample entries
    print("\nSample persistent rare MIDDLEs with nearest common:")
    for mid in sorted(distances.keys(), key=lambda m: distances[m]['distance'])[:15]:
        info = distances[mid]
        print(f"  {mid:15s} -> {info['nearest_common']:15s} dist={info['distance']} "
              f"(rare in {info['folio_count']} folios)")


# ============================================================
# STEP 6: Section distribution analysis
# ============================================================
print("\n=== Section Distribution Analysis ===")

# Which sections do persistent rare MIDDLEs appear in?
persistent_section_counts = Counter()
persistent_by_section = defaultdict(set)  # section -> set of persistent MIDDLEs

for r in persistent_records:
    persistent_section_counts[r['section']] += 1
    persistent_by_section[r['section']].add(r['middle'])

all_sections = sorted(persistent_section_counts.keys())
print(f"Sections with persistent rare MIDDLEs: {all_sections}")
for s in all_sections:
    unique_mids = persistent_by_section[s]
    print(f"  {s}: {persistent_section_counts[s]} instances, "
          f"{len(unique_mids)} unique MIDDLEs")

# Section specificity: what fraction of persistent rare MIDDLEs are section-exclusive?
section_exclusive_middles = set()
multi_section_middles = set()

middle_sections = defaultdict(set)
for r in persistent_records:
    middle_sections[r['middle']].add(r['section'])

for mid, secs in middle_sections.items():
    if len(secs) == 1:
        section_exclusive_middles.add(mid)
    else:
        multi_section_middles.add(mid)

n_exclusive = len(section_exclusive_middles)
n_multi = len(multi_section_middles)
exclusive_fraction = n_exclusive / n_persistent_middles if n_persistent_middles > 0 else 0.0

print(f"\nSection-exclusive persistent rare MIDDLEs: {n_exclusive}/{n_persistent_middles} "
      f"({exclusive_fraction:.1%})")
print(f"Multi-section persistent rare MIDDLEs: {n_multi}/{n_persistent_middles}")

if section_exclusive_middles:
    print("\nSection-exclusive examples:")
    for mid in sorted(section_exclusive_middles)[:15]:
        secs = middle_sections[mid]
        d_info = distances.get(mid, {})
        dist_str = f"dist={d_info.get('distance', '?')}" if d_info else "dist=?"
        print(f"  {mid:15s} section={list(secs)[0]:3s} "
              f"folio_count={middle_folio_count[mid]} {dist_str}")


# ============================================================
# STEP 7: Folio-level persistence patterns
# ============================================================
print("\n=== Folio-Level Persistence Patterns ===")

# How many persistent rare MIDDLEs per folio?
folio_persistent_counts = Counter()
for r in persistent_records:
    folio_persistent_counts[r['folio']] += 1

if folio_persistent_counts:
    count_values = list(folio_persistent_counts.values())
    mean_per_folio = sum(count_values) / len(count_values)
    max_per_folio = max(count_values)
    print(f"Folios with at least one persistent rare MIDDLE: {len(folio_persistent_counts)}")
    print(f"Mean persistent rare MIDDLEs per folio: {mean_per_folio:.1f}")
    print(f"Max persistent rare MIDDLEs on a single folio: {max_per_folio}")

    # Show the most "material-rich" folios
    print("\nFolios with most persistent rare MIDDLEs:")
    for folio, count in folio_persistent_counts.most_common(10):
        section = folio_section.get(folio, 'UNK')
        n_pars = len(folio_paragraphs[folio])
        mids = [r['middle'] for r in persistent_records if r['folio'] == folio]
        print(f"  {folio:6s} section={section:3s} pars={n_pars} "
              f"persistent_rare={count}: {', '.join(sorted(mids))}")
else:
    print("No folios with persistent rare MIDDLEs found.")


# ============================================================
# STEP 8: Determine verdict
# ============================================================
print("\n" + "=" * 60)

strict_threshold_yielded_zero = (used_threshold != PERSISTENCE_THRESHOLD)
has_enough_persistent = n_persistent_middles > 10
morphologically_distant = mean_distance > DISTANCE_PASS_THRESHOLD
section_specific = exclusive_fraction > 0.50
low_variant_fraction = distance_1_fraction < 0.50

# Note: if we had to relax the threshold, the best possible verdict is MARGINAL
# (the strict >80% criterion was not met)
threshold_note = ""
if strict_threshold_yielded_zero:
    threshold_note = (
        f" Note: strict >80% threshold yielded 0 results; "
        f"analysis uses relaxed >{used_threshold:.0%} threshold."
    )

if has_enough_persistent and morphologically_distant and section_specific and not strict_threshold_yielded_zero:
    verdict = 'PASS'
    interpretation = (
        f"Folio-persistent rare MIDDLEs exist as material markers. "
        f"Found {n_persistent_middles} unique rare MIDDLEs that persist across "
        f">{PERSISTENCE_THRESHOLD:.0%} of their host folio's paragraphs. "
        f"Mean Levenshtein distance to nearest common MIDDLE is {mean_distance:.2f} "
        f"(threshold: {DISTANCE_PASS_THRESHOLD}), indicating morphological independence. "
        f"{exclusive_fraction:.0%} are section-exclusive, supporting material-locus interpretation. "
        f"Only {distance_1_fraction:.0%} are distance-1 variants of common MIDDLEs."
    )
elif has_enough_persistent and morphologically_distant and section_specific and strict_threshold_yielded_zero:
    verdict = 'MARGINAL'
    interpretation = (
        f"Folio-persistent rare MIDDLEs show partial material marker signal at relaxed threshold. "
        f"Strict >80% paragraph persistence yielded 0 results. "
        f"At >{used_threshold:.0%} threshold: {n_persistent_middles} unique persistent rare MIDDLEs. "
        f"Mean Levenshtein distance to nearest common MIDDLE: {mean_distance:.2f} "
        f"(>{DISTANCE_PASS_THRESHOLD}), indicating morphological independence. "
        f"{exclusive_fraction:.0%} are section-exclusive. "
        f"Only {distance_1_fraction:.0%} are distance-1 variants. "
        f"The signal exists but requires a weaker persistence criterion."
    )
elif has_enough_persistent and (morphologically_distant or section_specific):
    verdict = 'MARGINAL'
    interpretation = (
        f"Folio-persistent rare MIDDLEs partially support material marker hypothesis. "
        f"Found {n_persistent_middles} unique persistent rare MIDDLEs "
        f"(at >{used_threshold:.0%} threshold). "
        f"Mean distance to common MIDDLEs: {mean_distance:.2f} "
        f"(threshold: {DISTANCE_PASS_THRESHOLD}). "
        f"Section-exclusive fraction: {exclusive_fraction:.0%}. "
        f"Distance-1 variant fraction: {distance_1_fraction:.0%}. "
        f"{'Morphological distance supports independence' if morphologically_distant else 'Too close to common vocabulary'}. "
        f"{'Section specificity supports material signal' if section_specific else 'Insufficient section specificity'}."
        f"{threshold_note}"
    )
elif has_enough_persistent and not morphologically_distant and not section_specific:
    verdict = 'FAIL'
    interpretation = (
        f"Folio-persistent rare MIDDLEs are operational variants, not material markers. "
        f"Found {n_persistent_middles} persistent rare MIDDLEs but mean distance to "
        f"common MIDDLEs is only {mean_distance:.2f} (<{DISTANCE_PASS_THRESHOLD}), "
        f"and {distance_1_fraction:.0%} are distance-1 variants. "
        f"Only {exclusive_fraction:.0%} are section-exclusive. "
        f"These are likely morphological variants of common vocabulary rather than "
        f"independent material markers.{threshold_note}"
    )
else:
    verdict = 'FAIL'
    interpretation = (
        f"Insufficient folio-persistent rare MIDDLEs found. "
        f"Only {n_persistent_middles} unique persistent rare MIDDLEs "
        f"(threshold: >10). "
        f"At the strict >80% paragraph persistence level, zero rare MIDDLEs qualify. "
        f"The phenomenon of cross-paragraph material persistence does not exist "
        f"at the tested thresholds."
    )

print(f"=== VERDICT: {verdict} ===")
print(interpretation)


# ============================================================
# STEP 9: Build output JSON
# ============================================================

# Build top examples list for JSON
top_persistent_examples = []
if persistent_records:
    sorted_records = sorted(persistent_records,
                            key=lambda r: (-r['paragraph_fraction'], r['folio_count']))
    for r in sorted_records[:30]:
        d_info = distances.get(r['middle'], {})
        top_persistent_examples.append({
            'middle': r['middle'],
            'folio': r['folio'],
            'section': r['section'],
            'paragraph_fraction': r['paragraph_fraction'],
            'n_paragraphs': r['n_paragraphs'],
            'paragraphs_with_middle': r['paragraphs_with_middle'],
            'folio_count': r['folio_count'],
            'nearest_common_middle': d_info.get('nearest_common', None),
            'distance_to_nearest_common': d_info.get('distance', None),
        })

# Distance distribution
dist_distribution = {}
if distances:
    dist_values_all = [d['distance'] for d in distances.values()]
    for d_val in sorted(set(dist_values_all)):
        dist_distribution[str(d_val)] = sum(1 for x in dist_values_all if x == d_val)

# Section breakdown
section_breakdown = {}
for s in all_sections:
    unique_mids_in_section = persistent_by_section[s]
    section_breakdown[s] = {
        'instances': persistent_section_counts[s],
        'unique_middles': len(unique_mids_in_section),
        'example_middles': sorted(unique_mids_in_section)[:10],
    }

output = {
    'test': 'cross_paragraph_persistence',
    'test_number': 12,
    'question': ('Do folio-persistent rare MIDDLEs (appearing in >80% of a '
                 'folio\'s paragraphs but in <15 folios total) exist as '
                 'material markers?'),
    'method': {
        'description': (
            'For each Currier B folio with 3+ paragraphs, identify rare MIDDLEs '
            '(<15 folios) that persist across >80% of paragraphs. Test whether '
            'these are morphologically distinct from common MIDDLEs (40+ folios) '
            'using Levenshtein distance, and whether they are section-specific.'
        ),
        'rare_folio_threshold': RARE_FOLIO_THRESHOLD,
        'common_folio_threshold': COMMON_FOLIO_THRESHOLD,
        'min_paragraphs_per_folio': MIN_PARAGRAPHS_PER_FOLIO,
        'persistence_threshold_strict': PERSISTENCE_THRESHOLD,
        'persistence_threshold_used': used_threshold,
        'strict_threshold_yielded_zero': strict_threshold_yielded_zero,
        'distance_pass_threshold': DISTANCE_PASS_THRESHOLD,
    },
    'data_summary': {
        'total_b_tokens_with_middle': len(all_tokens),
        'total_paragraphs': len(paragraphs),
        'total_b_folios': total_b_folios,
        'eligible_folios': len(eligible_folios),
        'unique_middles': len(all_middles),
        'rare_middles': len(rare_middles),
        'common_middles': len(common_middles),
    },
    'persistence_results': {
        'folio_persistent_rare_instances': n_persistent_pairs,
        'unique_persistent_rare_middles': n_persistent_middles,
        'folios_with_persistent_rare': len(folio_persistent_counts),
        'mean_persistent_per_folio': round(
            sum(folio_persistent_counts.values()) / len(folio_persistent_counts), 2
        ) if folio_persistent_counts else 0.0,
        'top_examples': top_persistent_examples,
    },
    'edit_distance_analysis': {
        'n_analyzed': len(distances),
        'mean_distance': round(mean_distance, 3),
        'median_distance': median_distance,
        'distance_1_count': distance_1_count,
        'distance_1_fraction': round(distance_1_fraction, 4),
        'distance_distribution': dist_distribution,
        'sample_entries': {
            mid: {
                'nearest_common': info['nearest_common'],
                'distance': info['distance'],
                'folio_count': info['folio_count'],
            }
            for mid, info in sorted(distances.items(),
                                    key=lambda x: x[1]['distance'])[:20]
        } if distances else {},
    },
    'section_analysis': {
        'sections_represented': all_sections,
        'section_breakdown': section_breakdown,
        'section_exclusive_count': n_exclusive,
        'multi_section_count': n_multi,
        'exclusive_fraction': round(exclusive_fraction, 4),
    },
    'pass_criteria': {
        'min_persistent_middles': 10,
        'min_mean_distance': DISTANCE_PASS_THRESHOLD,
        'min_exclusive_fraction': 0.50,
        'checks': {
            'enough_persistent': has_enough_persistent,
            'morphologically_distant': morphologically_distant,
            'section_specific': section_specific,
            'low_variant_fraction': low_variant_fraction,
        },
    },
    'verdict': verdict,
    'interpretation': interpretation,
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nOutput written to {OUTPUT_PATH}")

"""
22_pp_profile_by_subtype.py

PP PROFILE BY PARAGRAPH SUB-TYPE

Compare PP token profiles across all discovered sub-types:
- FIRST WITHOUT-RI (preamble/setup)
- MIDDLE WITHOUT-RI (process annotations)
- LAST WITHOUT-RI (closure records)
- FIRST WITH-RI
- MIDDLE WITH-RI
- LAST WITH-RI

Look for distinctive PREFIX and MIDDLE signatures.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, RecordAnalyzer

print("="*70)
print("PP PROFILE BY PARAGRAPH SUB-TYPE")
print("="*70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# =============================================================
# STEP 1: BUILD PARAGRAPH INVENTORY BY POSITION AND TYPE
# =============================================================
print("\n[1/3] Building paragraph inventory...")

folio_paragraphs = defaultdict(list)
current_para_tokens = []
current_folio = None

for t in tx.currier_a():
    if not t.word or '*' in t.word:
        continue

    if t.folio != current_folio:
        if current_para_tokens:
            folio_paragraphs[current_folio].append(current_para_tokens)
        current_folio = t.folio
        current_para_tokens = []

    if t.par_initial and current_para_tokens:
        folio_paragraphs[current_folio].append(current_para_tokens)
        current_para_tokens = []

    current_para_tokens.append(t)

if current_para_tokens and current_folio:
    folio_paragraphs[current_folio].append(current_para_tokens)

def has_initial_ri(para_tokens, analyzer):
    if not para_tokens:
        return False
    folio = para_tokens[0].folio
    first_line = para_tokens[0].line
    try:
        record = analyzer.analyze_record(folio, first_line)
        if record:
            for t in record.tokens:
                if t.token_class == 'RI':
                    return True
    except:
        pass
    return False

def get_pp_data(para_tokens, analyzer, morph):
    """Get PP prefixes and middles from a paragraph."""
    if not para_tokens:
        return Counter(), Counter()

    folio = para_tokens[0].folio
    lines = sorted(set(t.line for t in para_tokens))
    prefixes = Counter()
    middles = Counter()

    for line in lines:
        try:
            record = analyzer.analyze_record(folio, line)
            if record:
                for t in record.tokens:
                    if t.token_class == 'PP' and t.word:
                        try:
                            m = morph.extract(t.word)
                            if m.prefix:
                                prefixes[m.prefix] += 1
                            if m.middle:
                                middles[m.middle] += 1
                        except:
                            pass
        except:
            pass
    return prefixes, middles

# Classify into 6 sub-types
subtypes = {
    'FIRST_WITHOUT_RI': [],
    'MIDDLE_WITHOUT_RI': [],
    'LAST_WITHOUT_RI': [],
    'FIRST_WITH_RI': [],
    'MIDDLE_WITH_RI': [],
    'LAST_WITH_RI': []
}

for folio, paragraphs in folio_paragraphs.items():
    n = len(paragraphs)

    for i, para_tokens in enumerate(paragraphs):
        if not para_tokens:
            continue

        is_with_ri = has_initial_ri(para_tokens, analyzer)
        ri_type = 'WITH_RI' if is_with_ri else 'WITHOUT_RI'

        if n == 1:
            position = 'ONLY'  # Treat as FIRST for simplicity
            key = f'FIRST_{ri_type}'
        elif i == 0:
            position = 'FIRST'
            key = f'FIRST_{ri_type}'
        elif i == n - 1:
            position = 'LAST'
            key = f'LAST_{ri_type}'
        else:
            position = 'MIDDLE'
            key = f'MIDDLE_{ri_type}'

        prefixes, middles = get_pp_data(para_tokens, analyzer, morph)
        subtypes[key].append({
            'folio': folio,
            'position': position,
            'prefixes': prefixes,
            'middles': middles
        })

print(f"\nSub-type counts:")
for key, data in subtypes.items():
    print(f"   {key}: {len(data)}")

# =============================================================
# STEP 2: AGGREGATE PP PREFIXES BY SUB-TYPE
# =============================================================
print("\n[2/3] Aggregating PP prefixes...")

def aggregate_counter(data_list, field):
    total = Counter()
    for d in data_list:
        total.update(d[field])
    return total

subtype_prefixes = {k: aggregate_counter(v, 'prefixes') for k, v in subtypes.items()}
subtype_middles = {k: aggregate_counter(v, 'middles') for k, v in subtypes.items()}

# Get all prefixes
all_prefixes = set()
for prefixes in subtype_prefixes.values():
    all_prefixes.update(prefixes.keys())
all_prefixes = sorted(all_prefixes)

# Compute totals
subtype_totals = {k: sum(v.values()) for k, v in subtype_prefixes.items()}

# =============================================================
# STEP 3: COMPARE PREFIX PROFILES
# =============================================================
print("\n[3/3] Comparing PREFIX profiles...")

# Overall baseline
overall_prefixes = Counter()
for prefixes in subtype_prefixes.values():
    overall_prefixes.update(prefixes)
overall_total = sum(overall_prefixes.values())

print(f"\nPP PREFIX DISTRIBUTION BY SUB-TYPE (% of each sub-type's PP tokens):")
print(f"{'PREFIX':<8}", end="")
for key in ['FIRST_WITHOUT_RI', 'MIDDLE_WITHOUT_RI', 'LAST_WITHOUT_RI', 'FIRST_WITH_RI', 'MIDDLE_WITH_RI', 'LAST_WITH_RI']:
    short = key.replace('WITHOUT_RI', 'WO').replace('WITH_RI', 'W').replace('FIRST_', 'F_').replace('MIDDLE_', 'M_').replace('LAST_', 'L_')
    print(f"{short:>8}", end="")
print(f"{'OVERALL':>8}")
print("-" * 64)

# Show major prefixes
major_prefixes = [p for p in all_prefixes if overall_prefixes[p] / overall_total > 0.02]

for prefix in sorted(major_prefixes):
    print(f"{prefix:<8}", end="")
    for key in ['FIRST_WITHOUT_RI', 'MIDDLE_WITHOUT_RI', 'LAST_WITHOUT_RI', 'FIRST_WITH_RI', 'MIDDLE_WITH_RI', 'LAST_WITH_RI']:
        total = subtype_totals[key]
        pct = 100 * subtype_prefixes[key][prefix] / total if total > 0 else 0
        print(f"{pct:>7.1f}%", end="")
    overall_pct = 100 * overall_prefixes[prefix] / overall_total
    print(f"{overall_pct:>7.1f}%")

# =============================================================
# HIGHLIGHT SIGNIFICANT DIFFERENCES
# =============================================================
print("\n" + "="*70)
print("SIGNIFICANT PREFIX DIFFERENCES (>1.5x vs overall)")
print("="*70)

for key in ['FIRST_WITHOUT_RI', 'MIDDLE_WITHOUT_RI', 'LAST_WITHOUT_RI', 'FIRST_WITH_RI', 'MIDDLE_WITH_RI', 'LAST_WITH_RI']:
    total = subtype_totals[key]
    enriched = []
    depleted = []

    for prefix in major_prefixes:
        subtype_pct = 100 * subtype_prefixes[key][prefix] / total if total > 0 else 0
        overall_pct = 100 * overall_prefixes[prefix] / overall_total

        if overall_pct > 0:
            ratio = subtype_pct / overall_pct
            if ratio >= 1.5:
                enriched.append((prefix, ratio))
            elif ratio <= 0.67:
                depleted.append((prefix, ratio))

    if enriched or depleted:
        print(f"\n{key}:")
        if enriched:
            enriched.sort(key=lambda x: -x[1])
            print(f"  ENRICHED: {', '.join(f'{p} ({r:.1f}x)' for p, r in enriched[:5])}")
        if depleted:
            depleted.sort(key=lambda x: x[1])
            print(f"  DEPLETED: {', '.join(f'{p} ({r:.1f}x)' for p, r in depleted[:5])}")

# =============================================================
# DISTINCTIVE SIGNATURES
# =============================================================
print("\n" + "="*70)
print("DISTINCTIVE SIGNATURES")
print("="*70)

# Find prefixes that distinguish WITHOUT_RI sub-types from each other
print("\nComparing WITHOUT-RI sub-types:")

wo_keys = ['FIRST_WITHOUT_RI', 'MIDDLE_WITHOUT_RI', 'LAST_WITHOUT_RI']
for prefix in major_prefixes:
    pcts = []
    for key in wo_keys:
        total = subtype_totals[key]
        pct = 100 * subtype_prefixes[key][prefix] / total if total > 0 else 0
        pcts.append(pct)

    # Check if there's significant variation
    if max(pcts) > 0 and max(pcts) / (min(pcts) + 0.1) > 1.5:
        print(f"  {prefix}: FIRST={pcts[0]:.1f}%, MIDDLE={pcts[1]:.1f}%, LAST={pcts[2]:.1f}%")

# Compare WITH_RI sub-types
print("\nComparing WITH-RI sub-types:")
w_keys = ['FIRST_WITH_RI', 'MIDDLE_WITH_RI', 'LAST_WITH_RI']
for prefix in major_prefixes:
    pcts = []
    for key in w_keys:
        total = subtype_totals[key]
        pct = 100 * subtype_prefixes[key][prefix] / total if total > 0 else 0
        pcts.append(pct)

    if max(pcts) > 0 and max(pcts) / (min(pcts) + 0.1) > 1.5:
        print(f"  {prefix}: FIRST={pcts[0]:.1f}%, MIDDLE={pcts[1]:.1f}%, LAST={pcts[2]:.1f}%")

# =============================================================
# FUNCTIONAL INTERPRETATION
# =============================================================
print("\n" + "="*70)
print("FUNCTIONAL INTERPRETATION")
print("="*70)

# Map prefixes to functional categories (from BCSC)
prefix_functions = {
    'ch': 'PHASE_CONTROL',
    'sh': 'PHASE_CONTROL',
    'qo': 'ENERGY/ESCAPE',
    'ko': 'ENERGY',
    'da': 'FLOW_REDIRECT',
    'ol': 'LINK/MONITOR',
    'or': 'LINK/MONITOR',
    'ok': 'AUXILIARY',
    'ot': 'AUXILIARY',
    'ct': 'LINKER'
}

print("\nFunctional profile by sub-type:")
for key in ['FIRST_WITHOUT_RI', 'MIDDLE_WITHOUT_RI', 'LAST_WITHOUT_RI']:
    total = subtype_totals[key]
    func_totals = defaultdict(int)

    for prefix, count in subtype_prefixes[key].items():
        func = prefix_functions.get(prefix, 'OTHER')
        func_totals[func] += count

    print(f"\n{key}:")
    for func in ['PHASE_CONTROL', 'ENERGY/ESCAPE', 'FLOW_REDIRECT', 'LINK/MONITOR', 'AUXILIARY', 'LINKER']:
        pct = 100 * func_totals[func] / total if total > 0 else 0
        if pct > 1:
            print(f"  {func}: {pct:.1f}%")

# =============================================================
# SAVE RESULTS
# =============================================================
results = {
    'test': 'PP_PROFILE_BY_SUBTYPE',
    'counts': {k: len(v) for k, v in subtypes.items()},
    'prefix_profiles': {
        k: {p: 100 * subtype_prefixes[k][p] / subtype_totals[k] if subtype_totals[k] > 0 else 0
            for p in major_prefixes}
        for k in subtypes.keys()
    }
}

output_path = Path(__file__).parent.parent / 'results' / 'pp_profile_by_subtype.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")

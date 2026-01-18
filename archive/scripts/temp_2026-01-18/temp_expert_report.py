"""Generate complete expert diagnostic report."""
import sys
sys.path.insert(0, 'apps/constraint_flow_visualizer')

from pathlib import Path
from collections import Counter, defaultdict

from core.data_loader import get_data_store, PROJECT_ROOT
from core.constraint_bundle import compute_bundle
from core.azc_projection import project_bundle, ZONES, _get_consolidated_zone
from core.reachability_engine import compute_reachability
from core.morphology import decompose_token

print('='*80)
print('COMPLETE EXPERT DIAGNOSTIC REPORT')
print('Constraint Flow Visualizer - B Tab Differentiation Issue')
print('='*80)
print()

# Load data silently
import io
from contextlib import redirect_stdout
with redirect_stdout(io.StringIO()):
    store = get_data_store()

print('SECTION 1: PROBLEM STATEMENT')
print('-'*80)
print('''
The user reported: "when I select a currier A register, I can see the legal
instructions shrink.. but the currier B tab never changes"

After implementing the expert-prescribed three-set model:
- Grammar tab DOES show zone-dependent class restriction (47→43 classes C→S)
- BUT all 82 B folios show UNREACHABLE regardless of which A entry is selected
- No differentiation occurs between different A entries
''')

print('SECTION 2: IMPLEMENTATION SUMMARY')
print('-'*80)
print('''
Per expert correction, implemented three-set model in azc_projection.py:

  1. zone_legal_middles = {MIDDLEs legal in this zone per zone_legality data}
  2. folio_middles = {MIDDLEs in this AZC folio's vocabulary}
  3. effective_legal = zone_legal_middles ∩ folio_middles

Class reachability computed from effective_legal domain.
B reachability aggregates across compatible AZC folios (union).

Files modified:
  - core/data_loader.py: Added azc_folio_middles field and loader
  - core/azc_projection.py: Three-set model in compute_zone_reachability()
  - core/reachability_engine.py: Folio compatibility + aggregation
''')

print('SECTION 3: DATA INVENTORY')
print('-'*80)

# Zone legality data
print(f'Zone Legality Data (middle_zone_legality.json):')
print(f'  Total MIDDLEs: {len(store.middle_zone_legality)}')
zone_counts = {'C': 0, 'P': 0, 'R': 0, 'S': 0}
for zones in store.middle_zone_legality.values():
    for z in zones:
        if z in zone_counts:
            zone_counts[z] += 1
print(f'  Legal in C: {zone_counts["C"]}, P: {zone_counts["P"]}, R: {zone_counts["R"]}, S: {zone_counts["S"]}')
print(f'  Sample MIDDLEs: {sorted(store.middle_zone_legality.keys())[:15]}')
print()

# AZC folio vocabularies
all_folio_middles = set()
for middles in store.azc_folio_middles.values():
    all_folio_middles.update(middles)
print(f'AZC Folio Vocabularies (extracted from transcript):')
print(f'  Total folios: {len(store.azc_folio_middles)}')
print(f'  Total unique MIDDLEs across all folios: {len(all_folio_middles)}')
vocab_sizes = [len(v) for v in store.azc_folio_middles.values()]
print(f'  Vocabulary sizes: min={min(vocab_sizes)}, max={max(vocab_sizes)}, avg={sum(vocab_sizes)/len(vocab_sizes):.1f}')
print()

# Orphan analysis
zone_legal_set = set(store.middle_zone_legality.keys())
orphan_middles = all_folio_middles - zone_legal_set
common_middles = all_folio_middles & zone_legal_set
print(f'MIDDLE Set Comparison:')
print(f'  In zone_legality: {len(zone_legal_set)}')
print(f'  In folio vocabularies: {len(all_folio_middles)}')
print(f'  INTERSECTION (usable): {len(common_middles)}')
print(f'  ORPHANS (in folios but not in legality): {len(orphan_middles)}')
print(f'  Orphan ratio: {len(orphan_middles)/len(all_folio_middles)*100:.1f}%')
print()

# B folio footprints
print(f'B Folio Class Footprints:')
print(f'  Total B folios: {len(store.b_folio_class_footprints)}')
footprint_sizes = [len(v) for v in store.b_folio_class_footprints.values()]
print(f'  Footprint sizes: min={min(footprint_sizes)}, max={max(footprint_sizes)}, avg={sum(footprint_sizes)/len(footprint_sizes):.1f}')
print()

# Instruction classes
print(f'Instruction Classes:')
print(f'  Total: {len(store.classes)}')
classes_with_middles = sum(1 for c in store.classes.values() if c.middles)
classes_with_effective_middles = sum(1 for c in store.classes.values() if any(m for m in c.middles if m))
print(f'  With any MIDDLEs: {classes_with_middles}')
print(f'  With non-empty MIDDLEs: {classes_with_effective_middles}')
print()

print('SECTION 4: THE CRITICAL BUG')
print('-'*80)
print(f'''
The zone_legality data contains only {len(zone_legal_set)} MIDDLEs.
The AZC folio vocabularies contain {len(all_folio_middles)} unique MIDDLEs.

When computing: effective_legal = zone_legal ∩ folio_vocab

Only {len(common_middles)} MIDDLEs survive the intersection!
{len(orphan_middles)} MIDDLEs ({len(orphan_middles)/len(all_folio_middles)*100:.1f}%) are ORPHANS - they exist in
folio vocabularies but have NO zone legality entry.

Orphan MIDDLEs are excluded from effective_legal, which means:
- Classes requiring orphan MIDDLEs are always PRUNED
- This affects B folio reachability
''')

print('SECTION 5: IMPACT ON CLASS REACHABILITY')
print('-'*80)

# Test with a token
token = 'chedy'
bundle = compute_bundle(token)
projection = project_bundle(bundle)
b_reach = compute_reachability(projection)

reachable = b_reach.grammar_by_zone['C'].reachable_classes
pruned = b_reach.grammar_by_zone['C'].pruned_classes

print(f'Test token: {token} (MIDDLEs: {bundle.middles})')
print(f'Grammar in zone C: {len(reachable)} reachable, {len(pruned)} pruned')
print(f'Pruned classes: {sorted(pruned)}')
print()

print('Pruned Class Details:')
for class_id in sorted(pruned):
    cls = store.classes.get(class_id)
    if cls:
        effective = sorted([m for m in cls.middles if m])
        print(f'  Class {class_id} ({cls.role}):')
        print(f'    Needs MIDDLEs: {effective}')
        for m in effective:
            in_legality = m in zone_legal_set
            in_folios = m in all_folio_middles
            print(f'      "{m}": in_zone_legality={in_legality}, in_folio_vocab={in_folios}')
print()

print('SECTION 6: IMPACT ON B FOLIO REACHABILITY')
print('-'*80)

# Check which classes B folios need
all_b_required = set()
for classes in store.b_folio_class_footprints.values():
    all_b_required.update(classes)

missing_for_b = all_b_required - reachable
print(f'All B folios collectively require: {len(all_b_required)} distinct classes')
print(f'Classes missing from grammar: {sorted(missing_for_b)}')
print()

# How many B folios need each missing class
print('Missing class impact:')
for class_id in sorted(missing_for_b):
    count = sum(1 for classes in store.b_folio_class_footprints.values() if class_id in classes)
    print(f'  Class {class_id}: required by {count}/{len(store.b_folio_class_footprints)} B folios ({count/len(store.b_folio_class_footprints)*100:.0f}%)')
print()

print('SECTION 7: ROOT CAUSE ANALYSIS')
print('-'*80)
print('''
The compute_middle_zone_legality.py script generates zone_legality data.
It filters to: transcriber='H', language='NA' (AZC only), MIN_OCCURRENCES=5

Current output: 45 MIDDLEs

But AZC folio vocabularies (same filter: H-track, language=NA) yield 468 MIDDLEs.

HYPOTHESIS: The zone_legality script uses a different MIDDLE extraction method
or has additional filtering that excludes most MIDDLEs.
''')

# Check what the zone legality script actually does
legality_script = PROJECT_ROOT / "scripts" / "compute_middle_zone_legality.py"
if legality_script.exists():
    print(f'Zone legality script exists at: {legality_script}')
else:
    legality_script = PROJECT_ROOT / "apps" / "constraint_flow_visualizer" / "scripts" / "compute_middle_zone_legality.py"
    if legality_script.exists():
        print(f'Zone legality script exists at: {legality_script}')
    else:
        print('Zone legality script NOT FOUND')
print()

print('SECTION 8: DATA SOURCE COMPARISON')
print('-'*80)

# Check what MIDDLEs actually appear in the transcript for AZC
transcript_path = PROJECT_ROOT / "data" / "transcriptions" / "interlinear_full_words.txt"
azc_middles_raw = Counter()
azc_tokens_by_middle = defaultdict(list)

with open(transcript_path, 'r', encoding='utf-8') as f:
    f.readline()  # Skip header
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 13:
            continue
        token = parts[0].strip('"').strip()
        language = parts[6].strip('"').strip()
        transcriber = parts[12].strip('"').strip()

        if transcriber != 'H' or language != 'NA':
            continue

        morph = decompose_token(token)
        if morph.middle:
            azc_middles_raw[morph.middle] += 1
            if len(azc_tokens_by_middle[morph.middle]) < 3:
                azc_tokens_by_middle[morph.middle].append(token)

print(f'Direct transcript scan (H-track, language=NA):')
print(f'  Unique MIDDLEs found: {len(azc_middles_raw)}')
print(f'  Total MIDDLE occurrences: {sum(azc_middles_raw.values())}')
print()

# MIDDLEs with >= 5 occurrences (the threshold used in zone_legality script)
frequent_middles = {m for m, c in azc_middles_raw.items() if c >= 5}
print(f'MIDDLEs with >= 5 occurrences: {len(frequent_middles)}')
print()

# Compare to zone_legality
in_both = frequent_middles & zone_legal_set
in_transcript_only = frequent_middles - zone_legal_set
in_legality_only = zone_legal_set - frequent_middles

print(f'Comparison (frequent transcript MIDDLEs vs zone_legality):')
print(f'  In both: {len(in_both)}')
print(f'  In transcript (>=5) but NOT in zone_legality: {len(in_transcript_only)}')
print(f'  In zone_legality but NOT in transcript (>=5): {len(in_legality_only)}')
print()

if in_transcript_only:
    print(f'Sample MIDDLEs missing from zone_legality:')
    for m in sorted(in_transcript_only)[:10]:
        print(f'    "{m}": {azc_middles_raw[m]} occurrences, e.g. {azc_tokens_by_middle[m]}')
print()

print('SECTION 9: RECOMMENDED FIXES')
print('-'*80)
print('''
OPTION A: Fix zone_legality data generation
  - Review compute_middle_zone_legality.py for filtering bugs
  - Ensure it captures all MIDDLEs from H-track AZC tokens
  - Expected output: ~400+ MIDDLEs, not 45

OPTION B: Treat orphan MIDDLEs as all-zone-legal
  - In compute_zone_reachability(), if a MIDDLE has no zone_legality entry
    but exists in folio vocabulary, treat it as legal in all zones
  - This is a workaround, not a fix

OPTION C: Use folio vocabulary as the primary legality source
  - Skip zone_legality intersection entirely
  - effective_legal = folio_middles (zone filtering happens elsewhere)
  - Only viable if zone constraints are encoded differently

RECOMMENDED: Option A - the data is incomplete
''')

print('SECTION 10: VERIFICATION TEST')
print('-'*80)
print('If zone_legality contained all 468 folio MIDDLEs, what would happen?')
print()

# Simulate full legality
simulated_reachable = set(range(1, 50))
for class_id in list(simulated_reachable):
    cls = store.classes.get(class_id)
    if not cls:
        continue
    effective = {m for m in cls.middles if m}
    if not effective:
        continue
    # With full legality, all folio MIDDLEs would be in effective domain
    if not (effective & all_folio_middles):
        simulated_reachable.discard(class_id)

simulated_pruned = set(range(1, 50)) - simulated_reachable
print(f'With complete zone_legality data:')
print(f'  Simulated reachable: {len(simulated_reachable)} classes')
print(f'  Simulated pruned: {len(simulated_pruned)} classes: {sorted(simulated_pruned)}')

# Check B folio reachability with simulated grammar
b_reachable_count = sum(1 for classes in store.b_folio_class_footprints.values()
                        if set(classes) <= simulated_reachable)
print(f'  B folios that would be REACHABLE: {b_reachable_count}/{len(store.b_folio_class_footprints)}')
print()

print('='*80)
print('END OF REPORT')
print('='*80)

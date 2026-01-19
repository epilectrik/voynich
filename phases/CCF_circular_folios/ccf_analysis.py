# CCF Analysis - Circular Control Folio Structural Analysis
# Pre-registered falsification tests for circular folios
# NO semantic interpretation - purely operational analysis

import json
import re
import random
import math
from collections import defaultdict, Counter
from datetime import datetime

print("=" * 70)
print("CIRCULAR CONTROL FOLIO (CCF) ANALYSIS")
print("Pre-registered structural test suite")
print("=" * 70)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_corpus():
    """Load corpus and identify circular folios."""
    records = []
    with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 12:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                # Remove quotes from all fields
                parts = [p.strip('"') for p in parts]
                records.append({
                    'word': parts[0],
                    'folio': parts[2],
                    'section': parts[3],
                    'language': parts[6] if len(parts) > 6 else 'U',
                    'line': parts[11] if len(parts) > 11 else '0',
                    'placement': parts[10] if len(parts) > 10 else 'P1'
                })
    return records

def identify_circular_folios(records):
    """Identify circular folios from the corpus."""
    # Known circular/astrological folios: f67-f73 range
    circular_pattern = re.compile(r'^f(67|68|69|70|71|72|73)')

    circular_folios = defaultdict(list)
    all_folios = defaultdict(list)

    for r in records:
        folio = r['folio']
        all_folios[folio].append(r)
        if circular_pattern.match(folio):
            circular_folios[folio].append(r)

    return circular_folios, all_folios

# =============================================================================
# LOAD FROZEN GRAMMAR AND INSTRUCTION CLASSES
# =============================================================================

def load_frozen_grammar():
    """Load the 49 frozen instruction classes."""
    try:
        with open('C:/git/voynich/phase20a_operator_equivalence.json', 'r') as f:
            equiv_data = json.load(f)
        return equiv_data
    except:
        return None

def load_transition_grammar():
    """Load canonical grammar with forbidden transitions."""
    try:
        with open('C:/git/voynich/phase20d_canonical_grammar.json', 'r') as f:
            grammar = json.load(f)
        return grammar
    except:
        return None

# =============================================================================
# MAIN EXECUTION
# =============================================================================

print("\n[1] Loading corpus...")
records = load_corpus()
print(f"    Loaded {len(records)} records")

print("\n[2] Identifying circular folios...")
circular_folios, all_folios = identify_circular_folios(records)
print(f"    Found {len(circular_folios)} circular folio variants")
print(f"    Total circular records: {sum(len(v) for v in circular_folios.values())}")

if len(circular_folios) > 0:
    print("\n    Circular folios found:")
    for folio in sorted(circular_folios.keys()):
        print(f"      {folio}: {len(circular_folios[folio])} records")
else:
    print("\n    No circular folios found in f67-f73 range.")
    print("\n    Checking all unique folios...")
    unique_folios = sorted(set(r['folio'] for r in records))
    print(f"    Total unique folios: {len(unique_folios)}")
    # Show some samples
    print("    Sample folio IDs:", unique_folios[:20])

    # Look for any folios that might be circular based on other patterns
    # Try f85-f86 (rosettes) or other candidates
    for pattern_name, pattern in [
        ("f85/f86 rosettes", re.compile(r'^f(85|86)')),
        ("f57 (central diagram)", re.compile(r'^f57')),
        ("f67-f73 extended", re.compile(r'^f(67|68|69|70|71|72|73)')),
    ]:
        matches = [f for f in unique_folios if pattern.match(f)]
        if matches:
            print(f"    {pattern_name}: {matches}")

print("\n[3] Loading frozen grammar...")
equiv_classes = load_frozen_grammar()
if equiv_classes:
    print(f"    Loaded equivalence classes")
else:
    print("    WARNING: Could not load phase20a_operator_equivalence.json")

grammar = load_transition_grammar()
if grammar:
    print(f"    Loaded canonical grammar")
else:
    print("    WARNING: Could not load phase20d_canonical_grammar.json")

# Show all unique folios for inspection
print("\n[4] All unique folios in corpus:")
unique_folios = sorted(set(r['folio'] for r in records))
for i, f in enumerate(unique_folios):
    if i < 100 or f.startswith('f6') or f.startswith('f7') or f.startswith('f8'):
        print(f"    {f}", end="")
        if (i + 1) % 10 == 0:
            print()
print()

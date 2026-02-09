"""
01_extract_a_record_profiles.py

Extract profiles for A records containing potential material RI tokens.

For each A record with material RI:
- Extract PP tokens
- Compute PREFIX profile
- Find B folio convergence (where PP tokens appear)
- Determine REGIME membership
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("A RECORD PROFILE EXTRACTION")
print("="*70)

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Known animal RI tokens from previous work
KNOWN_ANIMAL_RI = {
    'eoschso': 'chicken (ennen) - HIGH CONFIDENCE',
    'teold': 'scharlach family (ESCAPE, no AUX)',
    'chald': 'scharlach family (ESCAPE, no AUX)',
    'eyd': 'blood (blut) family (weak)',
}

# Load B folio token data for convergence analysis
print("\nBuilding B folio token index...")
b_tokens_by_folio = defaultdict(set)
b_folios_by_token = defaultdict(set)

for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    b_tokens_by_folio[token.folio].add(token.word)
    b_folios_by_token[token.word].add(token.folio)

print(f"  B folios indexed: {len(b_tokens_by_folio)}")
print(f"  Unique B tokens: {len(b_folios_by_token)}")

# Load REGIME assignment from validated data
regime_mapping_path = Path(__file__).parent.parent.parent / "REGIME_SEMANTIC_INTERPRETATION" / "results" / "regime_folio_mapping.json"
if regime_mapping_path.exists():
    with open(regime_mapping_path) as f:
        REGIME_FOLIOS = json.load(f)
    print(f"  Loaded REGIME mapping from {regime_mapping_path}")
else:
    # Fallback
    REGIME_FOLIOS = {
        'REGIME_1': ['f57r', 'f57v', 'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v'],
        'REGIME_2': ['f78r', 'f78v', 'f79r', 'f79v', 'f80r', 'f80v', 'f81r', 'f81v'],
        'REGIME_3': ['f83r', 'f83v', 'f84r', 'f84v', 'f85r1', 'f85v1'],
        'REGIME_4': ['f40v', 'f41v', 'f94v', 'f95v1'],
    }
    print("  Using fallback REGIME mapping")

# Create folio -> REGIME lookup
folio_to_regime = {}
for regime, folios in REGIME_FOLIOS.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"  REGIME folios mapped: {len(folio_to_regime)}")

# Extract A records
print("\nExtracting A records...")
a_records = defaultdict(list)

for token in tx.currier_a():
    if '*' in token.word or not token.word.strip():
        continue
    record_key = f"{token.folio}:{token.line}"
    a_records[record_key].append(token)

print(f"  Total A records: {len(a_records)}")

# Identify RI vs PP tokens
# PP tokens are found in B; RI tokens are A-specific
print("\nClassifying tokens by pipeline position...")

pp_tokens = set()  # Tokens that appear in B
ri_tokens = set()  # Tokens that only appear in A

for record_key, tokens in a_records.items():
    for token in tokens:
        word = token.word
        if word in b_folios_by_token:
            pp_tokens.add(word)
        else:
            ri_tokens.add(word)

print(f"  PP tokens (appear in B): {len(pp_tokens)}")
print(f"  RI tokens (A-specific): {len(ri_tokens)}")

# Find records with potential material RI tokens
# Material RI criteria: folio-unique or very rare in A
print("\nFinding records with material RI tokens...")

# Count RI token occurrences in A
ri_occurrences = Counter()
ri_folios = defaultdict(set)
for record_key, tokens in a_records.items():
    folio = record_key.split(':')[0]
    for token in tokens:
        if token.word in ri_tokens:
            ri_occurrences[token.word] += 1
            ri_folios[token.word].add(folio)

# Material RI candidates: folio-unique (appear in 1 folio only)
folio_unique_ri = {t for t, folios in ri_folios.items() if len(folios) == 1}
print(f"  Folio-unique RI tokens: {len(folio_unique_ri)}")

# Extract profiles for records containing folio-unique RI
def compute_prefix_profile(tokens):
    """Compute PREFIX distribution for a set of tokens."""
    prefix_counts = Counter()
    total = 0

    for token in tokens:
        try:
            m = morph.extract(token.word if hasattr(token, 'word') else token)
            if m.prefix:
                prefix_counts[m.prefix] += 1
                total += 1
        except:
            pass

    if total == 0:
        return {}

    return {prefix: count / total for prefix, count in prefix_counts.items()}

def compute_b_convergence(pp_words):
    """Find which B folios the PP tokens converge to."""
    folio_counts = Counter()
    for word in pp_words:
        for folio in b_folios_by_token.get(word, []):
            folio_counts[folio] += 1
    return folio_counts

def get_regime_membership(convergent_folios):
    """Determine REGIME membership from convergent B folios."""
    regime_counts = Counter()
    for folio, count in convergent_folios.items():
        regime = folio_to_regime.get(folio, 'UNKNOWN')
        regime_counts[regime] += count
    return regime_counts

# Process all A records
print("\nProcessing A records...")
profiles = []

for record_key, tokens in a_records.items():
    words = [t.word for t in tokens]

    # Classify tokens in this record
    record_ri = [w for w in words if w in ri_tokens]
    record_pp = [w for w in words if w in pp_tokens]

    # Check for known animal RI
    known_animals_in_record = [w for w in record_ri if w in KNOWN_ANIMAL_RI]

    # Check for folio-unique RI
    folio_unique_in_record = [w for w in record_ri if w in folio_unique_ri]

    # Only profile records with material RI candidates
    if not (known_animals_in_record or folio_unique_in_record):
        continue

    # Compute PP prefix profile
    pp_prefix_profile = compute_prefix_profile(record_pp)

    # Compute B convergence
    convergence = compute_b_convergence(record_pp)

    # Get REGIME membership
    regime_membership = get_regime_membership(convergence)

    profile = {
        'record_id': record_key,
        'folio': record_key.split(':')[0],
        'all_tokens': words,
        'ri_tokens': record_ri,
        'pp_tokens': record_pp,
        'known_animal_ri': known_animals_in_record,
        'folio_unique_ri': folio_unique_in_record,
        'pp_prefix_profile': pp_prefix_profile,
        'b_convergence': dict(convergence.most_common(10)),
        'n_convergent_folios': len(convergence),
        'regime_membership': dict(regime_membership),
        'primary_regime': regime_membership.most_common(1)[0][0] if regime_membership else 'UNKNOWN',
    }

    # Compute signature for matching
    # Normalize prefix profile to match Brunschwig signature format
    normalized_prefix = {
        'qo': pp_prefix_profile.get('qo', 0),
        'ch_sh': pp_prefix_profile.get('ch', 0) + pp_prefix_profile.get('sh', 0),
        'ok_ot': pp_prefix_profile.get('ok', 0) + pp_prefix_profile.get('ot', 0),
        'da': pp_prefix_profile.get('da', 0),
        'ol_or': pp_prefix_profile.get('ol', 0) + pp_prefix_profile.get('or', 0),
    }
    profile['normalized_prefix_profile'] = normalized_prefix

    # REGIME as number
    regime_num = {'REGIME_1': 1, 'REGIME_2': 2, 'REGIME_3': 3, 'REGIME_4': 4}.get(
        profile['primary_regime'], 0)
    profile['regime_number'] = regime_num

    profiles.append(profile)

print(f"\nExtracted {len(profiles)} A record profiles")

# Show known animal profiles
print("\n" + "="*70)
print("KNOWN ANIMAL PROFILES")
print("="*70)

animal_profiles = [p for p in profiles if p['known_animal_ri']]
for p in animal_profiles:
    print(f"\n{p['record_id']}: {', '.join(p['known_animal_ri'])}")
    print(f"  All tokens: {' '.join(p['all_tokens'])}")
    print(f"  RI: {', '.join(p['ri_tokens'])}")
    print(f"  PP: {', '.join(p['pp_tokens'])}")
    print(f"  PP prefix profile: {p['pp_prefix_profile']}")
    print(f"  Normalized: qo={p['normalized_prefix_profile']['qo']:.2f}, "
          f"ch_sh={p['normalized_prefix_profile']['ch_sh']:.2f}, "
          f"ok_ot={p['normalized_prefix_profile']['ok_ot']:.2f}")
    print(f"  Converges to {p['n_convergent_folios']} B folios")
    print(f"  Primary REGIME: {p['primary_regime']}")

# Show high-potential profiles (folio-unique RI with good convergence)
print("\n" + "="*70)
print("HIGH-POTENTIAL PROFILES (folio-unique RI, 3+ convergent folios)")
print("="*70)

high_potential = [p for p in profiles
                  if p['folio_unique_ri']
                  and p['n_convergent_folios'] >= 3
                  and not p['known_animal_ri']]

for p in sorted(high_potential, key=lambda x: -x['n_convergent_folios'])[:15]:
    print(f"\n{p['record_id']}: {', '.join(p['folio_unique_ri'])}")
    print(f"  PP tokens: {', '.join(p['pp_tokens'][:5])}{'...' if len(p['pp_tokens']) > 5 else ''}")
    print(f"  Converges to {p['n_convergent_folios']} B folios")
    print(f"  Top convergent: {list(p['b_convergence'].items())[:3]}")
    print(f"  REGIME: {p['regime_membership']}")

# Summary statistics
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\nTotal profiles extracted: {len(profiles)}")
print(f"  With known animal RI: {len(animal_profiles)}")
print(f"  With folio-unique RI: {len([p for p in profiles if p['folio_unique_ri']])}")
print(f"  High-potential (3+ convergence): {len(high_potential)}")

# REGIME distribution
regime_dist = Counter(p['primary_regime'] for p in profiles)
print(f"\nPrimary REGIME distribution:")
for regime, count in regime_dist.most_common():
    print(f"  {regime}: {count}")

# Save profiles
output = {
    'total_profiles': len(profiles),
    'known_animal_count': len(animal_profiles),
    'folio_unique_count': len([p for p in profiles if p['folio_unique_ri']]),
    'high_potential_count': len(high_potential),
    'profiles': profiles,
    'known_animal_ri': KNOWN_ANIMAL_RI,
    'regime_distribution': dict(regime_dist),
}

output_path = results_dir / "a_record_profiles.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")

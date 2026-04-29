"""
Phase 640 Sub-Phase 2: Compositional expansion.

For every token in the baseline, generate an operational definition
from atom glosses + PREFIX channel + category + positional profile.
Assign confidence tiers D2-D4 based on atom confidence and consistency.

Reads b_dictionary_v0.1.json (with seeds), outputs b_dictionary_v0.2.json
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
input_path = os.path.join(results_dir, 'b_dictionary_v0.1.json')

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = data['entries']

# ============================================================
# PREFIX CHANNEL DEFINITIONS
# ============================================================
PREFIX_CHANNELS = {
    'qo': ('HEAT SOURCE', 'At the heat source/fire'),
    'ch': ('ACTIVE CHECK', 'Actively check/test'),
    'sh': ('PASSIVE MONITOR', 'Passively observe/watch'),
    'ok': ('VESSEL MGMT', 'At the vessel/apparatus'),
    'ot': ('TRANSFER RATE', 'Monitor transfer/drip rate'),
    'da': ('INFRASTRUCTURE', 'Material/infrastructure handling'),
    'po': ('STATE/POSITION', 'Mark operational state/position'),
    'so': ('SEQUENCE', 'Mark sequence position'),
    'sa': ('ITERATION', 'Iterative cycle channel'),
    'ol': ('CONTINUATION', 'Sustain/continue current state'),
    'or': ('FLOW ROUTING', 'Route flow/respond'),
    'op': ('OPERATIONAL', 'Operational arrangement'),
    'te': ('TRANSFER EXEC', 'Execute transfer operation'),
    'ke': ('STEADY HEAT', 'Steady-state thermal'),
    'ko': ('HEAT ARRANGE', 'Arrange heat/thermal setup'),
    'lk': ('EQUIPMENT FIRE', 'Equipment/furnace sustained'),
    'lch': ('EQUIPMENT CHECK', 'Check equipment state'),
    'lsh': ('EQUIPMENT WATCH', 'Monitor equipment'),
    'pch': ('PREP ARRANGE', 'Preparation/arrangement specification'),
    'al': ('YIELD STATE', 'Yield to state'),
    'ka': ('HEAT YIELD', 'Heat to yield'),
    'ta': ('TRANSFER YIELD', 'Transfer to yield'),
    'to': ('TRANSFER STATE', 'Transfer state/position'),
    'ro': ('RESPOND ARRANGE', 'Respond and arrange'),
    'do': ('EXECUTE ARRANGE', 'Execute arrangement'),
    None: ('BARE', 'Unmodified/generic'),
}

# ============================================================
# ATOM GLOSS LOOKUP
# ============================================================
ATOM_GLOSSES = {
    # LOCKED
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'bind/contain', 'a': 'yield', 'm': 'final',
    # SOLID
    'd': 'do/execute', 't': 'transfer', 'l': 'state', 'o': 'arrange',
    'c': 'adjust', 'p': 'pause',
    # PLAUSIBLE
    'f': 'flag', 's': 'sequence', 'r': 'respond', 'q': '?',
}

ATOM_TIERS = {
    'k': 'LOCKED', 'e': 'LOCKED', 'h': 'LOCKED', 'y': 'LOCKED',
    'i': 'LOCKED', 'n': 'LOCKED', 'a': 'LOCKED', 'm': 'LOCKED',
    'd': 'SOLID', 't': 'SOLID', 'l': 'SOLID', 'o': 'SOLID',
    'c': 'SOLID', 'p': 'SOLID',
    'f': 'PLAUSIBLE', 's': 'PLAUSIBLE', 'r': 'PLAUSIBLE', 'q': 'PLAUSIBLE',
}

def generate_workshop_reading(prefix, atoms, e_depth):
    """Generate a human-readable workshop instruction from prefix + atoms."""
    if not atoms:
        return None

    # PREFIX channel
    px_info = PREFIX_CHANNELS.get(prefix, PREFIX_CHANNELS.get(None))
    channel = px_info[1] if px_info else ''

    # Build atom reading
    parts = []
    for at in atoms:
        char = at['char']
        role = at['role']
        gloss = ATOM_GLOSSES.get(char, '?')

        if role == 'HEAD':
            if char == 'k': parts.append('heat')
            elif char == 'e': parts.append('cool/stabilize')
            elif char == 'o': parts.append('arrange')
            elif char == 't': parts.append('transfer')
            elif char == 'a': parts.append('yield')
            else: parts.append(gloss)
        elif role == 'MOD':
            if char == 'e':
                pass  # e-depth handled separately
            elif char == 'd': parts.append('execute')
            elif char == 'c': parts.append('with adjustment')
            elif char == 'i': parts.append('iteratively')
            elif char == 'p': parts.append('with pause')
            elif char == 's': parts.append('in sequence')
            elif char == 'f': parts.append('(flagged/cautious)')
            elif char == 'k': parts.append('under heat')
            elif char == 'h': parts.append('while watching')
            elif char == 't': parts.append('with transfer')
            elif char == 'o': parts.append('in arrangement')
            elif char == 'a': parts.append('to yield')
            else: parts.append(gloss)
        elif role == 'TERM':
            if char == 'y': parts.append('done')
            elif char == 'n': parts.append('and contain')
            elif char == 'm': parts.append('to completion')
            elif char == 'l': parts.append('to state')
            elif char == 'r': parts.append('and respond')
            elif char == 'h': parts.append('while monitoring')
            else: parts.append(gloss)

    # Add e-depth qualifier
    if e_depth is not None and e_depth >= 2:
        parts.insert(0, 'gently' if e_depth == 2 else 'very gently')

    # Combine
    action = ' '.join(parts)
    if channel and prefix:
        return f"{channel}: {action}"
    return action


def assign_confidence(entry, atoms):
    """Assign confidence tier based on atom quality and consistency."""
    if entry.get('confidence') in ('D0', 'D1'):
        return entry['confidence']  # Don't downgrade seeds

    if not atoms:
        return 'U'

    # Check atom tiers
    atom_chars = [at['char'] for at in atoms]
    tiers = [ATOM_TIERS.get(c, 'PLAUSIBLE') for c in atom_chars]

    has_plausible = 'PLAUSIBLE' in tiers
    all_locked_solid = all(t in ('LOCKED', 'SOLID') for t in tiers)

    freq = entry.get('frequency', 0)
    folio_count = entry.get('folio_count', 0)

    # D2: all atoms LOCKED/SOLID, appears on multiple folios
    if all_locked_solid and folio_count >= 3:
        return 'D2'

    # D3: has PLAUSIBLE atoms but reasonable frequency
    if freq >= 5 and folio_count >= 2:
        return 'D3'

    # D4: very low frequency or single-folio
    if freq >= 2:
        return 'D4'

    # U: hapax with weak atoms
    return 'U' if has_plausible else 'D4'


# ============================================================
# PROCESS ALL ENTRIES
# ============================================================
print("Generating compositional definitions...")

stats = {'D0': 0, 'D1': 0, 'D2': 0, 'D3': 0, 'D4': 0, 'U': 0}
total_freq_covered = {'D0': 0, 'D1': 0, 'D2': 0, 'D3': 0, 'D4': 0, 'U': 0}

for word, entry in entries.items():
    atoms = entry.get('atoms', [])
    prefix = entry.get('prefix')
    e_depth = entry.get('e_depth')

    # Generate workshop reading if not already seeded
    if not entry.get('workshop_reading'):
        reading = generate_workshop_reading(prefix, atoms, e_depth)
        if reading:
            entry['workshop_reading'] = reading

    # Generate operational definition if not already seeded
    if not entry.get('operational_def'):
        if atoms:
            # Build from atom gloss
            gloss = entry.get('atom_gloss', '')
            px_info = PREFIX_CHANNELS.get(prefix, PREFIX_CHANNELS.get(None))
            channel_name = px_info[0] if px_info else 'BARE'

            # Simple operational def from channel + gloss
            entry['operational_def'] = f"[{channel_name}] {gloss}"

    # Assign confidence
    conf = assign_confidence(entry, atoms)
    entry['confidence'] = conf

    stats[conf] += 1
    total_freq_covered[conf] += entry.get('frequency', 0)

total = data['metadata']['total_tokens']

print(f"\nConfidence distribution:")
print(f"{'Tier':<6} {'Types':<8} {'Tokens':<8} {'Coverage':<10}")
print("-" * 35)
cumulative = 0
for tier in ['D0', 'D1', 'D2', 'D3', 'D4', 'U']:
    cumulative += total_freq_covered[tier]
    print(f"{tier:<6} {stats[tier]:<8} {total_freq_covered[tier]:<8} {100*cumulative/total:.1f}% cumul")

# Save
output_path = os.path.join(results_dir, 'b_dictionary_v0.2.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\nWrote {output_path}")

# Generate expanded cheat sheet — top 100
cheat_path = os.path.join(results_dir, 'b_dictionary_top100.md')
with open(cheat_path, 'w', encoding='utf-8') as f:
    f.write("# Voynich B Dictionary — Top 100 Tokens\n\n")
    f.write(f"43 seeded (D0/D1), remainder compositional (D2+)\n\n")
    f.write(f"| # | Token | Freq | Tier | Workshop Reading |\n")
    f.write(f"|---|-------|------|------|------------------|\n")

    sorted_entries = sorted(entries.values(), key=lambda e: -e.get('frequency', 0))
    for i, e in enumerate(sorted_entries[:100], 1):
        reading = e.get('workshop_reading', e.get('operational_def', ''))
        if reading and len(reading) > 80:
            reading = reading[:77] + '...'
        f.write(f"| {i} | {e['token']} | {e['frequency']} | {e.get('confidence','')} | {reading or ''} |\n")

print(f"Wrote {cheat_path}")

# Show some example D2 definitions
print(f"\nSample D2 definitions (compositional, not seeded):")
d2_samples = [e for e in sorted_entries if e.get('confidence') == 'D2'][:15]
for e in d2_samples:
    print(f"  {e['token']:<20s} freq={e['frequency']:>4d}  {e.get('workshop_reading','')[:70]}")

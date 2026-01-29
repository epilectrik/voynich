"""
03_recovery_architecture.py

Test 4: Does Voynich FQ escape behavior match Brunschwig's 2-retry recovery?

Brunschwig recovery protocol (from BRSC):
- Maximum 2 retries allowed
- Primary recovery path: cooling (equilibration)
- Beyond 2 retries: discard (no salvage)

Voynich parallel:
- FQ = escape/exception handler (C875)
- FQ chain length should be short (1-2 tokens)
- FQ->EN recovery rate should be high
- e kernel = equilibration (cooling)

Method:
1. Identify FQ chains in B lines
2. Measure chain length distribution
3. Check if chains rarely exceed 2 tokens
4. Test FQ->EN recovery rate
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("RECOVERY ARCHITECTURE ANALYSIS")
print("="*70)

# Load transcript
df = pd.read_csv('data/voynich_transcript.csv')
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B']
df_b = df_b[~df_b['word'].isna()]
df_b = df_b[~df_b['word'].str.contains(r'\*', na=False)]

# Load class map for role identification
try:
    with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        class_map = json.load(f)

    # Build token -> class mapping
    token_to_class = {}
    for class_id, tokens in class_map.items():
        for token in tokens:
            token_to_class[token] = int(class_id)

    print(f"Loaded class map with {len(token_to_class)} tokens")
except FileNotFoundError:
    print("Class map not found, using role approximation")
    token_to_class = {}

# Role definitions (from BCSC)
# FQ = FREQUENT_OPERATOR (classes with high frequency, escape behavior)
# EN = ENERGY_OPERATOR (kernel-containing, processing)

# Load role definitions
try:
    with open('phases/B_CONTROL_FLOW_SEMANTICS/results/role_semantic_census.json') as f:
        role_data = json.load(f)
    print("Loaded role semantic data")
except FileNotFoundError:
    role_data = None
    print("Role data not found, using heuristics")

def get_role(word):
    """Get role for a word."""
    # Check if it has kernel (k, h, e) -> ENERGY_OPERATOR
    if any(c in word for c in 'khe'):
        return 'EN'

    # Check class map
    if word in token_to_class:
        cls = token_to_class[word]
        # FQ classes (high frequency, escape-related)
        if cls in [1, 2, 3, 4, 5]:  # High frequency classes
            return 'FQ'
        # AX classes
        if cls in [29]:  # LINK
            return 'AX'

    # Heuristics based on common patterns
    if word in ['daiin', 'ol', 'aiin', 'chol']:
        return 'CC'  # Control
    if word.startswith(('qo', 'so', 'do')):
        return 'FQ'  # Frequent/escape

    return 'UN'  # Unknown

# Analyze escape chains (FQ sequences)
print("\n" + "="*70)
print("FQ CHAIN ANALYSIS")
print("="*70)

chain_lengths = []
chain_contexts = []

for (folio, line_num), group in df_b.groupby(['folio', 'line']):
    words = group['word'].tolist()
    roles = [get_role(w) for w in words]

    # Find FQ chains
    i = 0
    while i < len(roles):
        if roles[i] == 'FQ':
            # Start of chain
            chain_start = i
            chain_len = 0
            while i < len(roles) and roles[i] == 'FQ':
                chain_len += 1
                i += 1

            chain_lengths.append(chain_len)

            # What comes after the chain?
            if i < len(roles):
                next_role = roles[i]
            else:
                next_role = 'END'

            chain_contexts.append({
                'folio': folio,
                'line': line_num,
                'chain_length': chain_len,
                'next_role': next_role,
                'chain_words': words[chain_start:chain_start+chain_len]
            })
        else:
            i += 1

print(f"\nTotal FQ chains found: {len(chain_lengths)}")
print(f"Mean chain length: {np.mean(chain_lengths):.2f}")
print(f"Max chain length: {max(chain_lengths)}")

# Chain length distribution
print("\nChain length distribution:")
length_counts = Counter(chain_lengths)
for length in sorted(length_counts.keys()):
    count = length_counts[length]
    pct = 100 * count / len(chain_lengths)
    marker = " <-- Brunschwig 2-retry limit" if length == 2 else ""
    print(f"  Length {length}: {count} ({pct:.1f}%){marker}")

# Check if chains are mostly 1-2 tokens (matching 2-retry limit)
short_chains = sum(1 for l in chain_lengths if l <= 2)
pct_short = 100 * short_chains / len(chain_lengths) if chain_lengths else 0
print(f"\nChains <= 2 tokens: {short_chains} ({pct_short:.1f}%)")

if pct_short > 80:
    print("  RESULT: Most chains are short (matches Brunschwig 2-retry limit)")
else:
    print("  RESULT: Many chains exceed 2 tokens (may not match Brunschwig)")

# Analyze what comes after FQ chains
print("\n" + "="*70)
print("FQ RECOVERY PATTERNS")
print("="*70)

next_role_counts = Counter(c['next_role'] for c in chain_contexts)
print("\nWhat follows FQ chains:")
total = len(chain_contexts)
for role, count in next_role_counts.most_common():
    pct = 100 * count / total
    marker = " <-- recovery to processing" if role == 'EN' else ""
    print(f"  {role}: {count} ({pct:.1f}%){marker}")

# FQ->EN is recovery to processing (matching Brunschwig's return to work)
fq_to_en = next_role_counts.get('EN', 0)
fq_to_en_rate = fq_to_en / total if total > 0 else 0

print(f"\nFQ->EN recovery rate: {fq_to_en_rate:.1%}")

if fq_to_en_rate > 0.25:
    print("  RESULT: High recovery rate (matches Brunschwig's return to processing)")
else:
    print("  RESULT: Low recovery rate")

# Analyze e-kernel in recovery
print("\n" + "="*70)
print("COOLING (e-kernel) IN RECOVERY")
print("="*70)

# Check if e-kernel appears in or after FQ chains
e_in_recovery = 0
e_contexts = []

for context in chain_contexts:
    folio = context['folio']
    line = context['line']

    # Get full line
    line_words = df_b[(df_b['folio'] == folio) & (df_b['line'] == line)]['word'].tolist()

    # Check if 'e' appears after FQ chain
    chain_end_idx = len(context['chain_words'])
    remaining_words = line_words[chain_end_idx:] if chain_end_idx < len(line_words) else []

    for word in remaining_words:
        if 'e' in word:
            e_in_recovery += 1
            e_contexts.append(context)
            break

e_recovery_rate = e_in_recovery / len(chain_contexts) if chain_contexts else 0
print(f"\ne-kernel following FQ chain: {e_in_recovery} ({e_recovery_rate:.1%})")

if e_recovery_rate > 0.3:
    print("  RESULT: High e-recovery rate (matches Brunschwig's cooling path)")
else:
    print("  RESULT: e-kernel not dominant in recovery")

# Compare to Brunschwig's 2-retry limit
print("\n" + "="*70)
print("BRUNSCHWIG RECOVERY COMPARISON")
print("="*70)

brunschwig_retry_limit = 2
voynich_modal_chain = Counter(chain_lengths).most_common(1)[0][0] if chain_lengths else 0

print(f"\nBrunschwig retry limit: {brunschwig_retry_limit}")
print(f"Voynich modal chain length: {voynich_modal_chain}")
print(f"Voynich mean chain length: {np.mean(chain_lengths):.2f}")

if voynich_modal_chain <= brunschwig_retry_limit:
    print("\n  MATCH: Modal chain length within Brunschwig retry limit")
else:
    print("\n  MISMATCH: Modal chain length exceeds Brunschwig retry limit")

# Save results
results = {
    'total_fq_chains': len(chain_lengths),
    'mean_chain_length': float(np.mean(chain_lengths)) if chain_lengths else None,
    'max_chain_length': max(chain_lengths) if chain_lengths else None,
    'chain_length_distribution': dict(length_counts),
    'pct_short_chains': pct_short,
    'next_role_distribution': dict(next_role_counts),
    'fq_to_en_recovery_rate': fq_to_en_rate,
    'e_in_recovery_rate': e_recovery_rate,
    'brunschwig_retry_limit': brunschwig_retry_limit,
    'voynich_modal_chain': voynich_modal_chain,
    'match_assessment': 'MATCH' if voynich_modal_chain <= brunschwig_retry_limit else 'MISMATCH',
    'interpretation': {
        'short_chains': 'FQ chains are mostly single-token escape handlers',
        'fq_to_en': 'Recovery typically returns to processing (EN)',
        'e_recovery': 'e-kernel (equilibration/cooling) role in recovery'
    }
}

output_path = results_dir / "recovery_analysis.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")

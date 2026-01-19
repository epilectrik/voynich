"""Phase S-1: Structural Primitive Candidate Extraction.

A structural element is a token whose primary constraint is positional or
relational rather than semantic or content-bearing, and whose functional
role is determined entirely by the formal system it is embedded in.

MANDATORY CRITERIA (token must pass ALL FOUR):
1. Appear across systems (A and/or B), or across incompatible sub-contexts
2. Exhibit role inversion or role specialization depending on context
3. Have high frequency relative to payload words
4. Show constrained adjacency patterns (what can/cannot neighbor it)

This script implements OBJECTIVE FILTERS ONLY for candidate extraction.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
grammar_path = project_root / 'results' / 'canonical_grammar.json'

# Load grammar to identify B grammar classes
with open(grammar_path) as f:
    grammar = json.load(f)

# Build token -> grammar class mapping
token_to_class = {}
terminals = grammar.get('terminals', {}).get('list', [])
for t in terminals:
    symbol = t.get('symbol')
    role = t.get('role')
    if symbol and role:
        token_to_class[symbol] = role

# Load transcription data
a_tokens = []
b_tokens = []
a_by_marker = defaultdict(list)  # marker -> tokens in entries with that marker
a_by_section = defaultdict(list)  # section -> tokens
b_by_section = defaultdict(list)

MARKERS = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'yk', 'yt']

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            # Filter to H (PRIMARY) transcriber track only
            transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
            if transcriber != 'H':
                continue
            word = parts[0].strip('"').strip().lower()
            section = parts[3].strip('"').strip()
            lang = parts[6].strip('"').strip()

            if not word:
                continue

            if lang == 'A':
                a_tokens.append(word)
                a_by_section[section].append(word)
                # Identify marker for this token
                for m in MARKERS:
                    if word.startswith(m):
                        a_by_marker[m].append(word)
                        break
            elif lang == 'B':
                b_tokens.append(word)
                b_by_section[section].append(word)

# Compute frequencies
a_freq = Counter(a_tokens)
b_freq = Counter(b_tokens)
total_a = len(a_tokens)
total_b = len(b_tokens)

print("=" * 70)
print("PHASE S-1: STRUCTURAL PRIMITIVE CANDIDATE EXTRACTION")
print("=" * 70)
print(f"\nCorpus: {total_a} A tokens, {total_b} B tokens")
print(f"Unique: {len(a_freq)} A types, {len(b_freq)} B types")

# =============================================================================
# FILTER 1: High frequency (>= 0.5% in A or B)
# =============================================================================
print("\n" + "=" * 70)
print("FILTER 1: HIGH FREQUENCY (>= 0.5% in either corpus)")
print("=" * 70)

freq_threshold = 0.005  # 0.5%
high_freq_tokens = set()

for tok, ct in a_freq.items():
    if ct / total_a >= freq_threshold:
        high_freq_tokens.add(tok)

for tok, ct in b_freq.items():
    if ct / total_b >= freq_threshold:
        high_freq_tokens.add(tok)

print(f"\nTokens passing frequency filter: {len(high_freq_tokens)}")

# Show top candidates
combined = []
for tok in high_freq_tokens:
    a_ct = a_freq.get(tok, 0)
    b_ct = b_freq.get(tok, 0)
    a_pct = 100 * a_ct / total_a if total_a > 0 else 0
    b_pct = 100 * b_ct / total_b if total_b > 0 else 0
    combined.append((tok, a_ct, b_ct, a_pct, b_pct))

combined.sort(key=lambda x: x[1] + x[2], reverse=True)
print(f"\nTop 30 high-frequency tokens:")
print(f"{'Token':<15} {'A count':>8} {'A %':>8} {'B count':>8} {'B %':>8} {'Grammar Class':<20}")
print("-" * 75)
for tok, a_ct, b_ct, a_pct, b_pct in combined[:30]:
    gc = token_to_class.get(tok, '-')
    print(f"{tok:<15} {a_ct:>8} {a_pct:>7.2f}% {b_ct:>8} {b_pct:>7.2f}% {gc:<20}")

# =============================================================================
# FILTER 2: Appears in multiple formal contexts (A AND B)
# =============================================================================
print("\n" + "=" * 70)
print("FILTER 2: APPEARS IN BOTH A AND B")
print("=" * 70)

both_systems = []
for tok in high_freq_tokens:
    a_ct = a_freq.get(tok, 0)
    b_ct = b_freq.get(tok, 0)
    if a_ct > 0 and b_ct > 0:
        both_systems.append((tok, a_ct, b_ct))

both_systems.sort(key=lambda x: x[1] + x[2], reverse=True)
print(f"\nTokens appearing in BOTH A and B: {len(both_systems)}")
print(f"\n{'Token':<15} {'A count':>8} {'B count':>8} {'A:B Ratio':>10} {'Grammar Class':<20}")
print("-" * 70)
for tok, a_ct, b_ct in both_systems[:30]:
    ratio = a_ct / b_ct if b_ct > 0 else float('inf')
    gc = token_to_class.get(tok, '-')
    print(f"{tok:<15} {a_ct:>8} {b_ct:>8} {ratio:>10.2f} {gc:<20}")

# =============================================================================
# FILTER 3: Not exclusive to one marker class in A
# =============================================================================
print("\n" + "=" * 70)
print("FILTER 3: NOT MARKER-EXCLUSIVE (appears with multiple markers)")
print("=" * 70)

# Count which markers each token appears with
token_marker_sets = defaultdict(set)
for marker, tokens in a_by_marker.items():
    for tok in tokens:
        token_marker_sets[tok].add(marker)

# For tokens in A, check how many markers they appear with
multi_marker_tokens = []
for tok, a_ct, b_ct in both_systems:
    markers_seen = token_marker_sets.get(tok, set())
    if len(markers_seen) >= 2 or (a_ct > 0 and len(markers_seen) == 0):
        # Either appears with multiple markers OR doesn't start with any marker
        is_marker_prefix = any(tok.startswith(m) for m in MARKERS)
        multi_marker_tokens.append((tok, a_ct, b_ct, len(markers_seen), is_marker_prefix))

print(f"\nTokens not exclusive to single marker: {len(multi_marker_tokens)}")
print(f"\n{'Token':<15} {'A count':>8} {'B count':>8} {'Markers':>8} {'Is Marker':>10}")
print("-" * 60)
for tok, a_ct, b_ct, n_markers, is_marker in multi_marker_tokens[:30]:
    print(f"{tok:<15} {a_ct:>8} {b_ct:>8} {n_markers:>8} {'Yes' if is_marker else 'No':>10}")

# =============================================================================
# FILTER 4: Has grammar class in B (indicates structural role)
# =============================================================================
print("\n" + "=" * 70)
print("FILTER 4: HAS GRAMMAR CLASS IN B")
print("=" * 70)

grammar_tokens = []
for tok, a_ct, b_ct, n_markers, is_marker in multi_marker_tokens:
    gc = token_to_class.get(tok)
    if gc:
        grammar_tokens.append((tok, a_ct, b_ct, gc))

print(f"\nTokens with grammar class: {len(grammar_tokens)}")
print(f"\n{'Token':<15} {'A count':>8} {'B count':>8} {'A:B Ratio':>10} {'Grammar Class':<20}")
print("-" * 70)
for tok, a_ct, b_ct, gc in grammar_tokens:
    ratio = a_ct / b_ct if b_ct > 0 else float('inf')
    print(f"{tok:<15} {a_ct:>8} {b_ct:>8} {ratio:>10.2f} {gc:<20}")

# =============================================================================
# FINAL CANDIDATES: Strong structural primitive candidates
# =============================================================================
print("\n" + "=" * 70)
print("FINAL CANDIDATES: STRUCTURAL PRIMITIVE CANDIDATES")
print("=" * 70)

# Compute A:B ratio for prioritization
# Structural primitives likely show system polarity (strong A or B bias)
final_candidates = []
for tok, a_ct, b_ct, gc in grammar_tokens:
    ratio = a_ct / b_ct if b_ct > 0 else float('inf')
    # Calculate polarity (how asymmetric is the distribution)
    total = a_ct + b_ct
    a_share = a_ct / total
    b_share = b_ct / total
    polarity = abs(a_share - b_share)  # 0 = balanced, 1 = fully one-sided
    final_candidates.append((tok, a_ct, b_ct, ratio, polarity, gc))

# Sort by polarity (most polarized first)
final_candidates.sort(key=lambda x: x[4], reverse=True)

print(f"\nCandidates sorted by system polarity (A vs B asymmetry):")
print(f"\n{'Token':<12} {'A ct':>6} {'B ct':>6} {'A:B':>8} {'Polarity':>10} {'Grammar Class':<20}")
print("-" * 70)
for tok, a_ct, b_ct, ratio, polarity, gc in final_candidates:
    print(f"{tok:<12} {a_ct:>6} {b_ct:>6} {ratio:>8.2f} {polarity:>10.3f} {gc:<20}")

# =============================================================================
# TIER-1 CANDIDATES: Most promising structural primitives
# =============================================================================
print("\n" + "=" * 70)
print("TIER-1 CANDIDATES (Polarity > 0.3, already known to have grammar role)")
print("=" * 70)

tier1 = [(tok, a_ct, b_ct, ratio, polarity, gc)
         for tok, a_ct, b_ct, ratio, polarity, gc in final_candidates
         if polarity > 0.3]

print(f"\nTier-1 candidates: {len(tier1)}")
for tok, a_ct, b_ct, ratio, polarity, gc in tier1:
    affinity = "A-enriched" if ratio > 1 else "B-enriched"
    print(f"\n  {tok}:")
    print(f"    Grammar class: {gc}")
    print(f"    A count: {a_ct}, B count: {b_ct}")
    print(f"    Ratio: {ratio:.2f} ({affinity})")
    print(f"    Polarity: {polarity:.3f}")

# =============================================================================
# SAVE RESULTS
# =============================================================================
results = {
    'total_a_tokens': total_a,
    'total_b_tokens': total_b,
    'high_freq_count': len(high_freq_tokens),
    'both_systems_count': len(both_systems),
    'final_candidates': [
        {
            'token': tok,
            'a_count': a_ct,
            'b_count': b_ct,
            'ratio': ratio,
            'polarity': polarity,
            'grammar_class': gc
        }
        for tok, a_ct, b_ct, ratio, polarity, gc in final_candidates
    ],
    'tier1_candidates': [tok for tok, *_ in tier1]
}

output_path = Path(__file__).parent / 'sp_phase1_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to {output_path}")

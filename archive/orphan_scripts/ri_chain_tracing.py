#!/usr/bin/env python3
"""
RI Chain Tracing: Trace procedural lineage through RI token connections.

Hypothesis: If RI encodes procedural specifications:
- OUTPUT RI (final position) = what a procedure produces
- INPUT RI (initial position) = what a procedure requires
- Chains form when one record's OUTPUT appears as another's INPUT

This would reveal the actual procedure network in Currier A.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np

# Fix console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("RI CHAIN TRACING: PROCEDURAL LINEAGE ANALYSIS")
print("="*70)

# Build paragraph data with INPUT and OUTPUT RI
paragraphs = []
current_folio = None
current_para = []
current_line = None
para_idx = 0

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        para_idx = 0
        continue

    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'para_idx': para_idx,
        'tokens': [t.word for t in current_para],
        'record_id': f"{current_folio}:{para_idx}"
    })

print(f"\nTotal paragraphs (A records): {len(paragraphs)}")

# Extract INPUT RI (first 1-3 tokens) and OUTPUT RI (last 1-3 tokens)
def get_ri_tokens(para, position='input', n=3):
    """Get RI tokens from input (first n) or output (last n) positions."""
    tokens = para['tokens']
    if len(tokens) < 4:
        return []

    if position == 'input':
        return tokens[:n]
    else:  # output
        return tokens[-n:]

# Build the connection graph
# output_to_records: RI token -> records that OUTPUT this token
# input_to_records: RI token -> records that INPUT this token

output_to_records = defaultdict(list)
input_to_records = defaultdict(list)

for para in paragraphs:
    record_id = para['record_id']

    input_ri = get_ri_tokens(para, 'input', 3)
    output_ri = get_ri_tokens(para, 'output', 3)

    para['input_ri'] = input_ri
    para['output_ri'] = output_ri

    for token in input_ri:
        input_to_records[token].append(record_id)

    for token in output_ri:
        output_to_records[token].append(record_id)

print(f"Unique INPUT RI tokens: {len(input_to_records)}")
print(f"Unique OUTPUT RI tokens: {len(output_to_records)}")

# Find LINKING tokens: tokens that appear as OUTPUT somewhere and INPUT elsewhere
linking_tokens = set(output_to_records.keys()) & set(input_to_records.keys())
print(f"\nLINKING tokens (appear as both OUTPUT and INPUT): {len(linking_tokens)}")

# Build edges: (source_record, target_record) where source's OUTPUT = target's INPUT
edges = []
for token in linking_tokens:
    sources = output_to_records[token]  # Records that output this token
    targets = input_to_records[token]   # Records that input this token

    for src in sources:
        for tgt in targets:
            if src != tgt:  # No self-loops
                edges.append((src, tgt, token))

print(f"Total edges (potential procedure links): {len(edges)}")

# Build adjacency for graph analysis
from collections import deque

adj = defaultdict(list)  # record -> list of (target, token)
in_degree = Counter()
out_degree = Counter()

for src, tgt, token in edges:
    adj[src].append((tgt, token))
    out_degree[src] += 1
    in_degree[tgt] += 1

all_records = set(p['record_id'] for p in paragraphs)
connected_records = set(adj.keys()) | set(in_degree.keys())

print(f"\nRecords with connections: {len(connected_records)} / {len(all_records)} ({100*len(connected_records)/len(all_records):.1f}%)")

# Analyze degree distribution
print(f"\n{'='*70}")
print("DEGREE DISTRIBUTION")
print("="*70)

print(f"\nOUT-DEGREE (number of downstream connections):")
out_counts = Counter(out_degree.values())
for deg in sorted(out_counts.keys())[:10]:
    print(f"  {deg} connections: {out_counts[deg]} records")

print(f"\nIN-DEGREE (number of upstream connections):")
in_counts = Counter(in_degree.values())
for deg in sorted(in_counts.keys())[:10]:
    print(f"  {deg} connections: {in_counts[deg]} records")

# Find HUBS: records with high out-degree (many downstream procedures)
print(f"\n{'='*70}")
print("OUTPUT HUBS (records feeding many procedures)")
print("="*70)

top_out = out_degree.most_common(15)
print(f"\n{'Record':<15} {'Out-Degree':<12} {'Output RI tokens':<40}")
print("-"*70)

record_lookup = {p['record_id']: p for p in paragraphs}
for record_id, deg in top_out:
    para = record_lookup.get(record_id)
    if para:
        out_ri = ', '.join(para['output_ri'][:3])
        print(f"{record_id:<15} {deg:<12} {out_ri:<40}")

# Find SINKS: records with high in-degree (many inputs converge)
print(f"\n{'='*70}")
print("INPUT SINKS (records receiving from many procedures)")
print("="*70)

top_in = in_degree.most_common(15)
print(f"\n{'Record':<15} {'In-Degree':<12} {'Input RI tokens':<40}")
print("-"*70)

for record_id, deg in top_in:
    para = record_lookup.get(record_id)
    if para:
        in_ri = ', '.join(para['input_ri'][:3])
        print(f"{record_id:<15} {deg:<12} {in_ri:<40}")

# Find CHAINS: sequences of connected records
print(f"\n{'='*70}")
print("CHAIN ANALYSIS")
print("="*70)

def find_chains(adj, max_length=10):
    """Find all chains (paths) in the graph."""
    chains = []
    visited_starts = set()

    # Start from records with in_degree=0 or low in_degree (source nodes)
    sources = [r for r in adj.keys() if in_degree.get(r, 0) == 0]

    # Also include high out-degree nodes as potential chain starts
    if not sources:
        sources = [r for r, _ in out_degree.most_common(50)]

    for start in sources[:100]:  # Limit search
        if start in visited_starts:
            continue

        # BFS to find chains
        queue = deque([(start, [start], [])])  # (current, path, tokens)

        while queue:
            current, path, tokens = queue.popleft()

            if len(path) >= max_length:
                chains.append((path, tokens))
                continue

            neighbors = adj.get(current, [])
            if not neighbors:
                if len(path) > 1:
                    chains.append((path, tokens))
                continue

            for next_node, token in neighbors:
                if next_node not in path:  # Avoid cycles in this path
                    queue.append((next_node, path + [next_node], tokens + [token]))

    return chains

chains = find_chains(adj, max_length=6)

# Analyze chain lengths
chain_lengths = [len(c[0]) for c in chains]
length_dist = Counter(chain_lengths)

print(f"\nChain length distribution:")
for length in sorted(length_dist.keys()):
    print(f"  Length {length}: {length_dist[length]} chains")

# Show example chains
print(f"\n{'='*70}")
print("EXAMPLE PROCEDURE CHAINS")
print("="*70)

# Sort by length descending
chains.sort(key=lambda x: -len(x[0]))

shown = 0
for path, tokens in chains[:20]:
    if len(path) >= 3:  # Only show chains of length 3+
        print(f"\nChain (length {len(path)}):")
        for i, record_id in enumerate(path):
            para = record_lookup.get(record_id)
            if para:
                in_ri = ', '.join(para['input_ri'][:2])
                out_ri = ', '.join(para['output_ri'][:2])
                link_token = tokens[i-1] if i > 0 else '-'
                print(f"  [{i+1}] {record_id:<12} IN: {in_ri:<20} OUT: {out_ri:<20} (linked by: {link_token})")
        shown += 1
        if shown >= 10:
            break

# Analyze linking tokens - which tokens form the most connections?
print(f"\n{'='*70}")
print("TOP LINKING TOKENS (procedural connectors)")
print("="*70)

token_edge_count = Counter()
for src, tgt, token in edges:
    token_edge_count[token] += 1

print(f"\n{'Token':<15} {'Edges':<10} {'As Output':<12} {'As Input':<12}")
print("-"*50)

for token, count in token_edge_count.most_common(25):
    n_out = len(output_to_records[token])
    n_in = len(input_to_records[token])
    print(f"{token:<15} {count:<10} {n_out:<12} {n_in:<12}")

# Cross-folio analysis: Do chains cross folios?
print(f"\n{'='*70}")
print("CROSS-FOLIO CHAINS")
print("="*70)

cross_folio_chains = []
same_folio_chains = []

for path, tokens in chains:
    if len(path) >= 2:
        folios = set(r.split(':')[0] for r in path)
        if len(folios) > 1:
            cross_folio_chains.append((path, tokens, folios))
        else:
            same_folio_chains.append((path, tokens))

print(f"\nSame-folio chains: {len(same_folio_chains)}")
print(f"Cross-folio chains: {len(cross_folio_chains)}")

if cross_folio_chains:
    print(f"\nExample cross-folio chains:")
    for path, tokens, folios in cross_folio_chains[:5]:
        print(f"  {' -> '.join(path[:5])}{'...' if len(path) > 5 else ''}")
        print(f"    Folios: {sorted(folios)}")

# Summary statistics
print(f"\n{'='*70}")
print("SUMMARY")
print("="*70)

print(f"""
RI Chain Tracing Results:
- Total A records: {len(paragraphs)}
- Records with connections: {len(connected_records)} ({100*len(connected_records)/len(all_records):.1f}%)
- Linking tokens: {len(linking_tokens)}
- Total edges: {len(edges)}

Graph Structure:
- Max out-degree: {max(out_degree.values()) if out_degree else 0}
- Max in-degree: {max(in_degree.values()) if in_degree else 0}
- Chains found: {len(chains)}
- Max chain length: {max(chain_lengths) if chain_lengths else 0}
- Cross-folio chains: {len(cross_folio_chains)}

Interpretation:
""")

if len(chains) > 0 and max(chain_lengths) >= 3:
    print("CHAINS EXIST: A records form procedural networks.")
    print("Output of one procedure becomes input to another.")
    if len(cross_folio_chains) > len(same_folio_chains) * 0.1:
        print("Cross-folio links exist: procedures span multiple folios.")
else:
    print("LIMITED CHAINING: Most connections are local, not sequential.")

# Save results
output = {
    'total_records': len(paragraphs),
    'connected_records': len(connected_records),
    'connection_rate': len(connected_records) / len(all_records),
    'linking_tokens': len(linking_tokens),
    'total_edges': len(edges),
    'chains_found': len(chains),
    'max_chain_length': max(chain_lengths) if chain_lengths else 0,
    'cross_folio_chains': len(cross_folio_chains),
    'same_folio_chains': len(same_folio_chains),
    'top_linking_tokens': [{'token': t, 'edges': c} for t, c in token_edge_count.most_common(20)],
    'top_output_hubs': [{'record': r, 'out_degree': d} for r, d in top_out[:10]],
    'top_input_sinks': [{'record': r, 'in_degree': d} for r, d in top_in[:10]],
    'chain_length_distribution': dict(length_dist)
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_chain_tracing.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")

#!/usr/bin/env python3
"""
Test 2: PP Co-occurrence Network Topology

Question: What is the structure of PP co-occurrence, and which PP are hubs?

Builds a co-occurrence graph from same-line PP pairs and analyzes
network centrality metrics.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

RI_PREFIXES = {'po', 'do', 'so', 'to', 'ko', 'qo', 'ch', 'sh'}

print("="*70)
print("TEST 2: PP CO-OCCURRENCE NETWORK TOPOLOGY")
print("="*70)

# Build co-occurrence graph
# Nodes = PP MIDDLEs, Edges = same-line co-occurrence

edge_weights = Counter()  # (middle1, middle2) -> count
node_counts = Counter()  # middle -> total occurrences

line_data = defaultdict(list)

for token in tx.currier_a():
    if '*' in token.word:
        continue
    line_data[(token.folio, token.line)].append(token.word)

# Process each line
for (folio, line), tokens in line_data.items():
    # Extract PP MIDDLEs from this line
    pp_middles = []
    for token in tokens:
        try:
            m = morph.extract(token)
            if m.prefix not in RI_PREFIXES and m.middle:
                pp_middles.append(m.middle)
        except:
            pass

    # Count individual nodes
    for middle in pp_middles:
        node_counts[middle] += 1

    # Count co-occurrences (unordered pairs)
    unique_middles = list(set(pp_middles))
    for i in range(len(unique_middles)):
        for j in range(i + 1, len(unique_middles)):
            m1, m2 = sorted([unique_middles[i], unique_middles[j]])
            edge_weights[(m1, m2)] += 1

print(f"\nNetwork statistics:")
print(f"  Nodes (unique MIDDLEs): {len(node_counts)}")
print(f"  Edges (co-occurrence pairs): {len(edge_weights)}")
print(f"  Total edge weight: {sum(edge_weights.values())}")

# =========================================================================
# Compute centrality metrics
# =========================================================================
print("\n" + "="*70)
print("CENTRALITY METRICS")
print("="*70)

# Build adjacency structure
adjacency = defaultdict(lambda: defaultdict(int))
for (m1, m2), weight in edge_weights.items():
    adjacency[m1][m2] += weight
    adjacency[m2][m1] += weight

# Filter to nodes with sufficient connections
MIN_DEGREE = 5
connected_nodes = [m for m in node_counts if len(adjacency[m]) >= MIN_DEGREE]
print(f"\nNodes with degree >= {MIN_DEGREE}: {len(connected_nodes)}")

# Compute degree centrality
degree_centrality = {}
for node in connected_nodes:
    degree_centrality[node] = len(adjacency[node])

# Compute weighted degree (strength)
strength = {}
for node in connected_nodes:
    strength[node] = sum(adjacency[node].values())

# Compute betweenness centrality (approximate - expensive for large graphs)
# Using a simplified approach: count how many shortest paths go through each node
# For efficiency, we'll use a sampling approach

def compute_betweenness_sample(nodes, adjacency, n_samples=500):
    """Approximate betweenness by sampling node pairs."""
    betweenness = {n: 0 for n in nodes}

    if len(nodes) < 3:
        return betweenness

    # Sample random pairs
    np.random.seed(42)
    for _ in range(n_samples):
        # Pick two random nodes
        source, target = np.random.choice(nodes, 2, replace=False)

        # BFS to find shortest path
        visited = {source}
        queue = [(source, [source])]
        found_path = None

        while queue and found_path is None:
            current, path = queue.pop(0)
            for neighbor in adjacency[current]:
                if neighbor == target:
                    found_path = path + [neighbor]
                    break
                if neighbor not in visited and neighbor in nodes:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # Count intermediate nodes
        if found_path and len(found_path) > 2:
            for node in found_path[1:-1]:
                betweenness[node] += 1

    return betweenness

print("\nComputing betweenness centrality (sampled)...")
betweenness = compute_betweenness_sample(connected_nodes, adjacency)

# Normalize
max_betweenness = max(betweenness.values()) if betweenness else 1
betweenness_norm = {n: v / max_betweenness for n, v in betweenness.items()}

# =========================================================================
# Identify hub nodes
# =========================================================================
print("\n" + "="*70)
print("HUB NODES (High Degree)")
print("="*70)

# Sort by degree
by_degree = sorted(degree_centrality.items(), key=lambda x: -x[1])

print(f"\n{'MIDDLE':<12} {'Degree':<8} {'Strength':<10} {'Betweenness':<12} {'Freq':<8}")
print("-"*55)

hub_nodes = []
for middle, degree in by_degree[:20]:
    str_val = strength.get(middle, 0)
    btw_val = betweenness_norm.get(middle, 0)
    freq = node_counts[middle]
    hub_nodes.append({'middle': middle, 'degree': degree, 'strength': str_val,
                      'betweenness': btw_val, 'frequency': freq})
    print(f"{middle:<12} {degree:<8} {str_val:<10} {btw_val:<12.3f} {freq:<8}")

# =========================================================================
# Identify bridge nodes (high betweenness relative to degree)
# =========================================================================
print("\n" + "="*70)
print("BRIDGE NODES (High Betweenness / Degree)")
print("="*70)

bridge_ratio = {}
for node in connected_nodes:
    if degree_centrality[node] > 0:
        bridge_ratio[node] = betweenness_norm[node] / (degree_centrality[node] / max(degree_centrality.values()))

by_bridge = sorted(bridge_ratio.items(), key=lambda x: -x[1])

print(f"\n{'MIDDLE':<12} {'Bridge Ratio':<14} {'Degree':<8} {'Betweenness':<12}")
print("-"*50)

bridge_nodes = []
for middle, ratio in by_bridge[:15]:
    if ratio > 0:
        deg = degree_centrality[middle]
        btw = betweenness_norm[middle]
        bridge_nodes.append({'middle': middle, 'bridge_ratio': ratio, 'degree': deg, 'betweenness': btw})
        print(f"{middle:<12} {ratio:<14.3f} {deg:<8} {btw:<12.3f}")

# =========================================================================
# Degree distribution analysis
# =========================================================================
print("\n" + "="*70)
print("DEGREE DISTRIBUTION")
print("="*70)

degrees = list(degree_centrality.values())
print(f"\nDegree statistics:")
print(f"  Mean: {np.mean(degrees):.1f}")
print(f"  Median: {np.median(degrees):.1f}")
print(f"  Max: {max(degrees)}")
print(f"  Min: {min(degrees)}")

# Test for power-law (scale-free) vs random
# Simple test: coefficient of variation
cv = np.std(degrees) / np.mean(degrees)
print(f"  Coefficient of variation: {cv:.2f}")

if cv > 1.5:
    print("  -> High variance suggests scale-free (hub-dominated) structure")
elif cv > 1.0:
    print("  -> Moderate variance suggests partial hub structure")
else:
    print("  -> Low variance suggests more uniform (random-like) structure")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: PP NETWORK TOPOLOGY")
print("="*70)

top_hubs = [h['middle'] for h in hub_nodes[:5]]
top_bridges = [b['middle'] for b in bridge_nodes[:5] if b['bridge_ratio'] > 0.1]

print(f"""
Network size: {len(connected_nodes)} nodes, {len(edge_weights)} edges

Top 5 hubs (high degree):
  {', '.join(top_hubs)}

Top bridges (high betweenness/degree):
  {', '.join(top_bridges) if top_bridges else 'None identified'}

Degree distribution:
  Mean degree: {np.mean(degrees):.1f}
  CV: {cv:.2f}
""")

# Determine verdict
if cv > 1.5 and len(top_bridges) > 0:
    verdict = "CONFIRMED"
    explanation = "PP network has clear hub-and-bridge structure"
elif cv > 1.0 or len([h for h in hub_nodes if h['degree'] > 2 * np.mean(degrees)]) > 3:
    verdict = "SUPPORT"
    explanation = "PP network shows some hub structure"
else:
    verdict = "NOT SUPPORTED"
    explanation = "PP network is relatively uniform"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'n_nodes': len(node_counts),
    'n_edges': len(edge_weights),
    'n_connected': len(connected_nodes),
    'mean_degree': float(np.mean(degrees)),
    'cv_degree': cv,
    'top_hubs': hub_nodes[:10],
    'top_bridges': bridge_nodes[:10],
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'pp_network_topology.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\nResults saved to {output_path}")

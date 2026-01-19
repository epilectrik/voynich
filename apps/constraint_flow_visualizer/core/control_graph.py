"""
Control Graph - B Grammar as Labeled Transition System

Represents the 49-class grammar as a directed graph where:
- Nodes = instruction classes (1-49)
- Edges = legal transitions between classes

Per C121: 49 classes universal. Per C124: 100% coverage.
Per C468-C470: AZC masks edges by vocabulary availability.

This is pure structure - no simulation, timing, or semantics.
"""

from dataclasses import dataclass, field
from typing import Set, Dict, Tuple, Optional


@dataclass
class ControlGraphState:
    """State of the control graph under a legality field."""
    total_classes: int = 49
    reachable_classes: int = 49
    total_edges: int = 0
    reachable_edges: int = 0
    forbidden_edges: int = 17  # Always 17 (invariant per C109)
    atomic_hazards: int = 3    # Always 3 (invariant - classes 7,9,23)
    decomposable_hazards_active: int = 6
    decomposable_hazards_suppressed: int = 0
    scc_count: int = 0


class ControlGraph:
    """
    Represents the 49-class grammar as a transition graph.

    Uses adjacency sets instead of networkx for simplicity.
    """

    def __init__(self):
        self.nodes: Set[int] = set()
        self.edges: Set[Tuple[int, int]] = set()
        self.node_types: Dict[int, str] = {}

    def add_node(self, node_id: int, node_type: str = 'standard'):
        self.nodes.add(node_id)
        self.node_types[node_id] = node_type

    def add_edge(self, from_node: int, to_node: int):
        self.edges.add((from_node, to_node))

    def remove_edges_involving(self, nodes_to_remove: Set[int]):
        """Remove all edges involving the given nodes."""
        self.edges = {
            (u, v) for u, v in self.edges
            if u not in nodes_to_remove and v not in nodes_to_remove
        }

    def get_degree(self, node: int) -> int:
        """Get total degree (in + out) for a node."""
        in_degree = sum(1 for (_, v) in self.edges if v == node)
        out_degree = sum(1 for (u, _) in self.edges if u == node)
        return in_degree + out_degree

    def copy(self) -> 'ControlGraph':
        """Create a copy of this graph."""
        new_graph = ControlGraph()
        new_graph.nodes = self.nodes.copy()
        new_graph.edges = self.edges.copy()
        new_graph.node_types = self.node_types.copy()
        return new_graph

    def compute_sccs(self) -> int:
        """
        Compute number of strongly connected components using Kosaraju's algorithm.
        Returns count of SCCs with more than one node or with self-loops.
        """
        if not self.nodes:
            return 0

        # Build adjacency lists
        adj = {n: [] for n in self.nodes}
        adj_rev = {n: [] for n in self.nodes}
        for u, v in self.edges:
            if u in adj and v in adj:
                adj[u].append(v)
                adj_rev[v].append(u)

        # First DFS to get finish order
        visited = set()
        finish_order = []

        def dfs1(node):
            stack = [(node, False)]
            while stack:
                n, processed = stack.pop()
                if processed:
                    finish_order.append(n)
                    continue
                if n in visited:
                    continue
                visited.add(n)
                stack.append((n, True))
                for neighbor in adj.get(n, []):
                    if neighbor not in visited:
                        stack.append((neighbor, False))

        for node in self.nodes:
            if node not in visited:
                dfs1(node)

        # Second DFS on reversed graph
        visited.clear()
        scc_count = 0

        def dfs2(start):
            component = []
            stack = [start]
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)
                component.append(n)
                for neighbor in adj_rev.get(n, []):
                    if neighbor not in visited:
                        stack.append(neighbor)
            return component

        for node in reversed(finish_order):
            if node not in visited:
                component = dfs2(node)
                # Count SCCs that are non-trivial (>1 node or has self-loop)
                has_self_loop = any((n, n) in self.edges for n in component)
                if len(component) > 1 or has_self_loop:
                    scc_count += 1

        return scc_count


def classify_node(class_id: int, data_store) -> str:
    """Classify a node for visualization coloring."""
    if class_id in data_store.kernel_classes:
        return 'kernel'
    if class_id in data_store.atomic_hazard_classes:
        return 'atomic_hazard'
    if class_id in data_store.decomposable_hazard_classes:
        return 'decomposable_hazard'
    return 'standard'


def build_baseline_graph(data_store) -> ControlGraph:
    """
    Build unconstrained grammar graph.

    Nodes: 49 instruction classes
    Edges: All legal transitions (excluding 17 forbidden per C109)
    """
    graph = ControlGraph()

    # Add all 49 classes as nodes
    for i in range(1, 50):
        node_type = classify_node(i, data_store)
        graph.add_node(i, node_type)

    # Add all legal transitions (full connectivity minus forbidden)
    forbidden = data_store.forbidden_class_pairs
    for i in range(1, 50):
        for j in range(1, 50):
            if (i, j) not in forbidden:
                graph.add_edge(i, j)

    return graph


def build_conditioned_graph(
    baseline: ControlGraph,
    reachable_classes: Set[int],
    data_store
) -> ControlGraph:
    """
    Apply AZC legality field to grammar graph.

    Per C468: Legality inheritance - constraints propagate causally.
    Per C469: Categorical resolution - vocabulary availability, not parameters.
    Per C470: MIDDLE restrictions transfer intact.

    Masking is SUBTRACTIVE ONLY - we remove edges, never add.
    """
    graph = baseline.copy()

    # Mask edges involving pruned classes
    pruned = set(range(1, 50)) - reachable_classes
    graph.remove_edges_involving(pruned)

    # Update node types for pruned classes
    for class_id in pruned:
        graph.node_types[class_id] = 'pruned'

    return graph


def compute_graph_state(
    graph: ControlGraph,
    data_store,
    is_conditioned: bool = False
) -> ControlGraphState:
    """Compute metrics for the graph state."""
    # Count reachable nodes (those with at least one edge)
    nodes_with_edges = set()
    for u, v in graph.edges:
        nodes_with_edges.add(u)
        nodes_with_edges.add(v)

    reachable = len(nodes_with_edges) if is_conditioned else 49

    # Count SCCs
    scc_count = graph.compute_sccs()

    # Hazard class analysis
    atomic = data_store.atomic_hazard_classes
    decomposable = data_store.decomposable_hazard_classes

    # For decomposable, check which still have edges
    active_decomp = len([c for c in decomposable if graph.get_degree(c) > 0])
    suppressed_decomp = len(decomposable) - active_decomp

    return ControlGraphState(
        total_classes=49,
        reachable_classes=reachable,
        total_edges=len(graph.edges),
        reachable_edges=len(graph.edges),
        forbidden_edges=17,  # Invariant per C109
        atomic_hazards=3,    # Invariant - always active
        decomposable_hazards_active=active_decomp,
        decomposable_hazards_suppressed=suppressed_decomp,
        scc_count=scc_count
    )

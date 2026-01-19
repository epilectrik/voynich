"""
Verification tests for Control Loop Visualization Tab.

Tests per plan:
1. Unit test - graph construction (49 nodes, 17 forbidden, 3 atomic)
2. Metrics computation
3. Conditioned graph construction
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("CONTROL LOOP VISUALIZATION TESTS")
print("=" * 60)

# =============================================================================
# TEST 1: Data Store Loading
# =============================================================================
print("\n[TEST 1] Data Store Loading")
print("-" * 40)

from core.data_loader import get_data_store

ds = get_data_store()

print(f"  Kernel classes: {ds.kernel_classes}")
print(f"  Atomic hazard classes: {ds.atomic_hazard_classes}")
print(f"  Decomposable hazard classes: {ds.decomposable_hazard_classes}")
print(f"  Forbidden class pairs count: {len(ds.forbidden_class_pairs)}")

test1_pass = (
    len(ds.kernel_classes) > 0 and
    ds.atomic_hazard_classes == {7, 9, 23} and
    len(ds.decomposable_hazard_classes) == 6
)
print(f"\nTest 1 Result: {'PASS' if test1_pass else 'FAIL'}")

# =============================================================================
# TEST 2: Baseline Graph Construction
# =============================================================================
print("\n[TEST 2] Baseline Graph Construction")
print("-" * 40)

from core.control_graph import build_baseline_graph, compute_graph_state

baseline = build_baseline_graph(ds)

print(f"  Nodes: {len(baseline.nodes)} (expected 49)")
print(f"  Edges: {len(baseline.edges)}")

# Should have 49*49 - 17 forbidden - self-loops consideration
# Actually edges include self-loops in this implementation
expected_edges_approx = 49 * 49 - len(ds.forbidden_class_pairs)
print(f"  Expected edges (approx): {expected_edges_approx}")

test2_pass = len(baseline.nodes) == 49
print(f"\nTest 2 Result: {'PASS' if test2_pass else 'FAIL'}")

# =============================================================================
# TEST 3: Graph State Computation
# =============================================================================
print("\n[TEST 3] Graph State Computation")
print("-" * 40)

state = compute_graph_state(baseline, ds)

print(f"  Total classes: {state.total_classes} (expected 49)")
print(f"  Reachable classes: {state.reachable_classes}")
print(f"  Forbidden edges: {state.forbidden_edges} (expected 17)")
print(f"  Atomic hazards: {state.atomic_hazards} (expected 3)")
print(f"  Decomposable hazards active: {state.decomposable_hazards_active}")
print(f"  SCC count: {state.scc_count}")

test3_pass = (
    state.total_classes == 49 and
    state.forbidden_edges == 17 and
    state.atomic_hazards == 3
)
print(f"\nTest 3 Result: {'PASS' if test3_pass else 'FAIL'}")

# =============================================================================
# TEST 4: Conditioned Graph (Simulated AZC Restriction)
# =============================================================================
print("\n[TEST 4] Conditioned Graph Construction")
print("-" * 40)

from core.control_graph import build_conditioned_graph

# Simulate AZC restriction: remove classes 30, 33, 41 (some decomposable hazards)
reachable = set(range(1, 50)) - {30, 33, 41}
print(f"  Simulating: 3 classes pruned (30, 33, 41)")
print(f"  Reachable classes: {len(reachable)}")

conditioned = build_conditioned_graph(baseline, reachable, ds)
conditioned_state = compute_graph_state(conditioned, ds, is_conditioned=True)

print(f"  Conditioned reachable: {conditioned_state.reachable_classes}")
print(f"  Conditioned edges: {conditioned_state.reachable_edges}")
print(f"  Decomposable hazards suppressed: {conditioned_state.decomposable_hazards_suppressed}")

test4_pass = (
    conditioned_state.reachable_classes < 49 and
    conditioned_state.decomposable_hazards_suppressed >= 3
)
print(f"\nTest 4 Result: {'PASS' if test4_pass else 'FAIL'}")

# =============================================================================
# TEST 5: SCC Algorithm Verification
# =============================================================================
print("\n[TEST 5] SCC Algorithm")
print("-" * 40)

scc_count = baseline.compute_sccs()
print(f"  Baseline SCC count: {scc_count}")

# With nearly full connectivity (minus 17 forbidden), should have at least 1 major SCC
test5_pass = scc_count >= 1
print(f"\nTest 5 Result: {'PASS' if test5_pass else 'FAIL'}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
all_pass = test1_pass and test2_pass and test3_pass and test4_pass and test5_pass
print(f"  Test 1 (Data Store):        {'PASS' if test1_pass else 'FAIL'}")
print(f"  Test 2 (Baseline Graph):    {'PASS' if test2_pass else 'FAIL'}")
print(f"  Test 3 (Graph State):       {'PASS' if test3_pass else 'FAIL'}")
print(f"  Test 4 (Conditioned Graph): {'PASS' if test4_pass else 'FAIL'}")
print(f"  Test 5 (SCC Algorithm):     {'PASS' if test5_pass else 'FAIL'}")
print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)

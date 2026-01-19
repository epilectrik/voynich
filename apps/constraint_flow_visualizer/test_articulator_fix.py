"""
Verification tests for articulator filtering fix (C291-C292).

Run from apps/constraint_flow_visualizer directory.
"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("ARTICULATOR FIX VERIFICATION TESTS")
print("=" * 60)

# =============================================================================
# TEST 1: Unit test - articulator detection
# =============================================================================
print("\n[TEST 1] Unit test - articulator detection")
print("-" * 40)

from core.morphology import is_articulator

test_cases = [
    ('kchedy', True),   # kch- articulator
    ('tchedy', True),   # tch- articulator
    ('ykedy', True),    # yk- articulator
    ('ytaiin', True),   # yt- articulator
    ('schol', True),    # sch- articulator
    ('chedy', False),   # ch- base prefix
    ('shol', False),    # sh- base prefix
    ('daiin', False),   # da- infrastructure
    ('ol', False),      # minimal
    ('qokaiin', False), # qo- base prefix
]

test1_pass = True
for token, expected in test_cases:
    result = is_articulator(token)
    status = "PASS" if result == expected else "FAIL"
    if result != expected:
        test1_pass = False
    print(f"  {status}: is_articulator('{token}') = {result} (expected {expected})")

print(f"\nTest 1 Result: {'PASS' if test1_pass else 'FAIL'}")

# =============================================================================
# TEST 2: Integration test - articulator MIDDLEs excluded from AZC
# =============================================================================
print("\n[TEST 2] Integration test - articulator MIDDLEs excluded")
print("-" * 40)

from core.data_loader import get_data_store
from core.constraint_bundle import extract_azc_active_middles

ds = get_data_store()

# Test with mixed tokens (articulators + base prefixes)
test_tokens = ['kchedy', 'tchol', 'ykain', 'chedy', 'daiin', 'shol', 'qokaiin']
result = extract_azc_active_middles(test_tokens, ds)
print(f"  Input tokens: {test_tokens}")
print(f"  AZC-active MIDDLEs extracted: {result}")

# The exclusive articulator MIDDLEs that should NOT be in result
exclusive_middles = ['eat', 'eed', 'olsh']
test2_pass = True
for m in exclusive_middles:
    if m in result:
        print(f"  FAIL: '{m}' should NOT be extracted (articulator-exclusive)")
        test2_pass = False
    else:
        print(f"  OK: '{m}' correctly excluded")

print(f"\nTest 2 Result: {'PASS' if test2_pass else 'FAIL'}")

# =============================================================================
# TEST 3: Regression test - base prefixes still work
# =============================================================================
print("\n[TEST 3] Regression test - base prefixes still extract MIDDLEs")
print("-" * 40)

# These are base prefix tokens that should still contribute MIDDLEs
base_tokens = ['chedy', 'shol', 'qokaiin', 'okaiin', 'daiin']
result3 = extract_azc_active_middles(base_tokens, ds)
print(f"  Input tokens: {base_tokens}")
print(f"  AZC-active MIDDLEs: {result3}")

# Check that base prefix morphology still works
from core.morphology import decompose_token
test3_pass = True

# Test tokens WITH expected MIDDLEs
tokens_with_middles = [
    ('chedy', 'e'),    # ch- + -e- + -dy
    ('qokaiin', 'k'),  # qo- + -k- + -aiin
]
for token, expected_middle in tokens_with_middles:
    m = decompose_token(token)
    if m.is_valid and m.middle == expected_middle:
        print(f"  OK: '{token}' -> MIDDLE='{m.middle}' (expected '{expected_middle}')")
    else:
        print(f"  FAIL: '{token}' decomposition unexpected: middle='{m.middle}'")
        test3_pass = False

# Test token WITHOUT middle (just prefix+suffix) - should still be valid
m_shol = decompose_token('shol')
if m_shol.is_valid and m_shol.prefix == 'sh' and m_shol.suffix == 'ol':
    print(f"  OK: 'shol' -> prefix='sh' suffix='ol' (no MIDDLE, expected)")
else:
    print(f"  FAIL: 'shol' decomposition unexpected")
    test3_pass = False

print(f"\nTest 3 Result: {'PASS' if test3_pass else 'FAIL'}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
all_pass = test1_pass and test2_pass and test3_pass
print(f"  Test 1 (Articulator Detection):  {'PASS' if test1_pass else 'FAIL'}")
print(f"  Test 2 (AZC Exclusion):          {'PASS' if test2_pass else 'FAIL'}")
print(f"  Test 3 (Base Prefix Regression): {'PASS' if test3_pass else 'FAIL'}")
print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)

"""
Integration test for the damaged token recovery system.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('archive', 1)[0])

from lib import load_transcription, get_recovery_stats

print("=" * 60)
print("RECOVERY SYSTEM INTEGRATION TEST")
print("=" * 60)

# Test 1: Basic load
tokens = load_transcription()
print('\nTEST 1: Basic load')
print(f'  Total tokens: {len(tokens)}')
print(f'  Sample: {tokens[:5]}')

# Test 2: Recovery with CERTAIN only
certain = load_transcription(apply_recovery=True, min_confidence='CERTAIN')
damaged_before = sum(1 for t in tokens if '*' in t)
damaged_certain = sum(1 for t in certain if '*' in t)
print(f'\nTEST 2: CERTAIN recovery')
print(f'  Damaged before: {damaged_before}')
print(f'  Damaged after: {damaged_certain}')
print(f'  Recovered: {damaged_before - damaged_certain}')

# Test 3: Recovery with HIGH
high = load_transcription(apply_recovery=True, min_confidence='HIGH')
damaged_high = sum(1 for t in high if '*' in t)
print(f'\nTEST 3: HIGH recovery')
print(f'  Damaged after: {damaged_high}')
print(f'  Recovered: {damaged_before - damaged_high}')

# Test 4: Recovery with AMBIGUOUS
ambig = load_transcription(apply_recovery=True, min_confidence='AMBIGUOUS')
damaged_ambig = sum(1 for t in ambig if '*' in t)
print(f'\nTEST 4: AMBIGUOUS recovery')
print(f'  Damaged after: {damaged_ambig}')
print(f'  Recovered: {damaged_before - damaged_ambig}')

# Test 5: Verify no extra tokens introduced
print(f'\nTEST 5: Token count consistency')
print(f'  Original: {len(tokens)}')
print(f'  After recovery: {len(ambig)}')
diff = len(ambig) - len(tokens)
print(f'  Difference: {diff}', '(PASS)' if diff == 0 else '(FAIL)')

# Summary
print('\n' + '=' * 60)
print('RECOVERY SYSTEM SUMMARY')
print('=' * 60)
stats = get_recovery_stats()
print(f"""
Patch file statistics:
  CERTAIN:   {stats['CERTAIN']:>4} patches (unique match)
  HIGH:      {stats['HIGH']:>4} patches (2-5 candidates)
  AMBIGUOUS: {stats['AMBIGUOUS']:>4} patches (>5 candidates)
  Total:     {stats['total']:>4} recoverable

Recovery rates:
  CERTAIN only:    {damaged_before - damaged_certain:>4} / {damaged_before} = {100*(damaged_before-damaged_certain)/damaged_before:.1f}%
  + HIGH:          {damaged_before - damaged_high:>4} / {damaged_before} = {100*(damaged_before-damaged_high)/damaged_before:.1f}%
  + AMBIGUOUS:     {damaged_before - damaged_ambig:>4} / {damaged_before} = {100*(damaged_before-damaged_ambig)/damaged_before:.1f}%

Unrecoverable (no matching tokens in vocabulary): {damaged_ambig}
""")

# Verify all tests passed
all_passed = (diff == 0)
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)

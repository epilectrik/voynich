"""
Focused test: Are -hy tokens procedural connectors?

Key question: Do -hy tokens appear BETWEEN operational sequences
more than expected by chance?
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter, defaultdict
import random

tx = Transcript()
morph = Morphology()

b_tokens = list(tx.currier_b())

print("=" * 70)
print("PROCEDURAL CONNECTOR HYPOTHESIS TEST")
print("=" * 70)

# Define operational MIDDLEs (everything we've mapped as operations)
OPERATIONAL = {
    # PREP
    'te', 'pch', 'lch', 'tch', 'ksh',
    # CORE
    'k', 't', 'e',
    # EXT
    'ke', 'kch',
    # e-absorbed
    'edy', 'ey', 'eey', 'ed', 'eo', 'eol', 'ee', 'eeo',
    # a-absorbed (some are operational)
    'al', 'ar',
    # o-absorbed
    'ol', 'or',
    # vowel cores
    'a', 'o'
}

# Infrastructure MIDDLEs
INFRA = {'iin', 'in', 'aiin', 'ain', 'l', 'r', 'd', 'am'}

def is_operational(middle):
    return middle in OPERATIONAL

def is_infra(middle):
    return middle in INFRA

def is_hy_token(token):
    m = morph.extract(token.word)
    return m.suffix == 'hy'

# Group by line
by_line = defaultdict(list)
for t in b_tokens:
    by_line[(t.folio, t.line)].append(t)

print("\n1. POSITION BETWEEN OPERATIONS")
print("-" * 60)
print("If -hy tokens are connectors, they should appear BETWEEN operational tokens")

# For each -hy token, check if it's flanked by operational tokens
hy_between_ops = 0
hy_between_infra = 0
hy_between_mixed = 0
hy_at_boundary = 0
total_hy_with_context = 0

for (folio, line), tokens in by_line.items():
    for i, t in enumerate(tokens):
        if is_hy_token(t):
            if i > 0 and i < len(tokens) - 1:
                total_hy_with_context += 1
                prev_m = morph.extract(tokens[i-1].word)
                next_m = morph.extract(tokens[i+1].word)

                prev_op = is_operational(prev_m.middle)
                next_op = is_operational(next_m.middle)
                prev_inf = is_infra(prev_m.middle)
                next_inf = is_infra(next_m.middle)

                if prev_op and next_op:
                    hy_between_ops += 1
                elif prev_inf and next_inf:
                    hy_between_infra += 1
                elif (prev_op and next_inf) or (prev_inf and next_op):
                    hy_between_mixed += 1
                else:
                    hy_at_boundary += 1

print(f"\n-hy tokens with both neighbors: {total_hy_with_context}")
print(f"  Between two OPs:     {hy_between_ops} ({hy_between_ops/total_hy_with_context*100:.1f}%)")
print(f"  Between two INFRAs:  {hy_between_infra} ({hy_between_infra/total_hy_with_context*100:.1f}%)")
print(f"  Between OP<->INFRA:  {hy_between_mixed} ({hy_between_mixed/total_hy_with_context*100:.1f}%)")
print(f"  Other context:       {hy_at_boundary} ({hy_at_boundary/total_hy_with_context*100:.1f}%)")

# 2. Compare to baseline - what's the expected rate?
print("\n2. BASELINE COMPARISON")
print("-" * 60)

# For ALL mid-line tokens, what's the OP-OP flanking rate?
all_between_ops = 0
all_between_infra = 0
all_between_mixed = 0
all_other = 0
total_mid = 0

for (folio, line), tokens in by_line.items():
    for i in range(1, len(tokens) - 1):
        total_mid += 1
        prev_m = morph.extract(tokens[i-1].word)
        next_m = morph.extract(tokens[i+1].word)

        prev_op = is_operational(prev_m.middle)
        next_op = is_operational(next_m.middle)
        prev_inf = is_infra(prev_m.middle)
        next_inf = is_infra(next_m.middle)

        if prev_op and next_op:
            all_between_ops += 1
        elif prev_inf and next_inf:
            all_between_infra += 1
        elif (prev_op and next_inf) or (prev_inf and next_op):
            all_between_mixed += 1
        else:
            all_other += 1

print(f"All mid-line tokens: {total_mid}")
print(f"  Between two OPs:     {all_between_ops} ({all_between_ops/total_mid*100:.1f}%)")
print(f"  Between two INFRAs:  {all_between_infra} ({all_between_infra/total_mid*100:.1f}%)")
print(f"  Between OP<->INFRA:  {all_between_mixed} ({all_between_mixed/total_mid*100:.1f}%)")
print(f"  Other context:       {all_other} ({all_other/total_mid*100:.1f}%)")

# 3. Enrichment calculation
print("\n3. ENRICHMENT ANALYSIS")
print("-" * 60)

expected_hy_between_ops = all_between_ops / total_mid * total_hy_with_context
expected_hy_between_mixed = all_between_mixed / total_mid * total_hy_with_context

ops_enrichment = hy_between_ops / expected_hy_between_ops if expected_hy_between_ops > 0 else 0
mixed_enrichment = hy_between_mixed / expected_hy_between_mixed if expected_hy_between_mixed > 0 else 0

print(f"\nOP<->OP context:")
print(f"  Observed: {hy_between_ops}")
print(f"  Expected: {expected_hy_between_ops:.1f}")
print(f"  Enrichment: {ops_enrichment:.2f}x")

print(f"\nOP<->INFRA context (boundary crossing):")
print(f"  Observed: {hy_between_mixed}")
print(f"  Expected: {expected_hy_between_mixed:.1f}")
print(f"  Enrichment: {mixed_enrichment:.2f}x")

# 4. Sequence analysis - does -hy connect operational runs?
print("\n" + "=" * 70)
print("4. OPERATIONAL RUN ANALYSIS")
print("=" * 70)
print("Does -hy appear at boundaries between operational 'runs'?")

def get_runs(tokens):
    """Identify runs of consecutive operational or infra tokens"""
    runs = []
    current_run = []
    current_type = None

    for t in tokens:
        m = morph.extract(t.word)
        if is_operational(m.middle):
            token_type = 'OP'
        elif is_infra(m.middle):
            token_type = 'INFRA'
        elif m.suffix == 'hy':
            token_type = 'HY'
        else:
            token_type = 'OTHER'

        if token_type == current_type:
            current_run.append((t, token_type))
        else:
            if current_run:
                runs.append((current_type, len(current_run)))
            current_run = [(t, token_type)]
            current_type = token_type

    if current_run:
        runs.append((current_type, len(current_run)))

    return runs

# Look at what comes before and after -hy in run sequences
hy_transitions = Counter()
for (folio, line), tokens in by_line.items():
    runs = get_runs(tokens)
    for i, (run_type, run_len) in enumerate(runs):
        if run_type == 'HY':
            prev_type = runs[i-1][0] if i > 0 else 'START'
            next_type = runs[i+1][0] if i < len(runs)-1 else 'END'
            hy_transitions[(prev_type, next_type)] += 1

print("\n-hy appears in transitions between:")
for (prev, next), count in hy_transitions.most_common(10):
    print(f"  {prev:>6} -> HY -> {next:<6}: {count}")

# 5. The critical question
print("\n" + "=" * 70)
print("5. CRITICAL CONNECTOR EVIDENCE")
print("=" * 70)

# Does -hy specifically connect OP runs to INFRA runs or vice versa?
op_to_infra = hy_transitions.get(('OP', 'INFRA'), 0)
infra_to_op = hy_transitions.get(('INFRA', 'OP'), 0)
op_to_op = hy_transitions.get(('OP', 'OP'), 0)
infra_to_infra = hy_transitions.get(('INFRA', 'INFRA'), 0)

total_transitions = sum(hy_transitions.values())

print(f"""
-hy TRANSITION PATTERNS:

OP -> HY -> INFRA:     {op_to_infra:>4} ({op_to_infra/total_transitions*100:.1f}%) - operation completion
INFRA -> HY -> OP:     {infra_to_op:>4} ({infra_to_op/total_transitions*100:.1f}%) - operation initiation
OP -> HY -> OP:        {op_to_op:>4} ({op_to_op/total_transitions*100:.1f}%) - operation chaining
INFRA -> HY -> INFRA:  {infra_to_infra:>4} ({infra_to_infra/total_transitions*100:.1f}%) - infra linking

BOUNDARY CROSSING (OP<->INFRA): {op_to_infra + infra_to_op} ({(op_to_infra + infra_to_op)/total_transitions*100:.1f}%)
""")

# 6. Final verdict
print("=" * 70)
print("6. VERDICT: IS -hy A PROCEDURAL CONNECTOR?")
print("=" * 70)

boundary_pct = (op_to_infra + infra_to_op) / total_transitions * 100 if total_transitions > 0 else 0

if boundary_pct > 30:
    verdict = "STRONG EVIDENCE"
    interpretation = "Yes - -hy tokens preferentially appear at OP<->INFRA boundaries"
elif boundary_pct > 20:
    verdict = "MODERATE EVIDENCE"
    interpretation = "Likely - -hy shows elevated boundary crossing"
else:
    verdict = "WEAK EVIDENCE"
    interpretation = "Uncertain - -hy appears in diverse contexts"

print(f"""
Boundary crossing rate: {boundary_pct:.1f}%

VERDICT: {verdict}

{interpretation}
""")

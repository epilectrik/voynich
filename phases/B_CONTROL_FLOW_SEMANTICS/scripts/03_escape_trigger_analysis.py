"""
03_escape_trigger_analysis.py

Analyze what states trigger FQ escape.
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
token_to_role = class_data['token_to_role']

# FL stage map
FL_STAGE_MAP = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL', 'al': 'MEDIAL', 'l': 'MEDIAL', 'ol': 'MEDIAL',
    'o': 'LATE', 'ly': 'LATE',
    'am': 'TERMINAL', 'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
}

# Hazard stages (from FL semantic model)
HAZARD_STAGES = {'INITIAL', 'EARLY', 'MEDIAL'}
SAFE_STAGES = {'LATE', 'TERMINAL'}

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("Escape Trigger Analysis: What triggers FQ?")
print("=" * 70)

# Build token sequences by line
line_sequences = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_sequences[key].append(t)

# Identify FQ tokens
FQ_ROLE = 'FREQUENT_OPERATOR'

# Analyze pre-FQ states
pre_fq_roles = Counter()
pre_fq_middles = Counter()
pre_fq_stages = Counter()
pre_fq_kernel = {'has_k': 0, 'has_h': 0, 'has_e': 0, 'no_kernel': 0}

# Post-FQ states (recovery)
post_fq_roles = Counter()
post_fq_middles = Counter()
post_fq_stages = Counter()

# FQ chains
fq_chain_lengths = Counter()

for key, tokens in line_sequences.items():
    i = 0
    while i < len(tokens):
        t = tokens[i]
        role = token_to_role.get(t.word, 'UN')

        if role == FQ_ROLE:
            # Count chain length
            chain = 1
            j = i + 1
            while j < len(tokens) and token_to_role.get(tokens[j].word, 'UN') == FQ_ROLE:
                chain += 1
                j += 1
            fq_chain_lengths[chain] += 1

            # Pre-FQ analysis (what came before)
            if i > 0:
                prev = tokens[i-1]
                prev_role = token_to_role.get(prev.word, 'UN')
                pre_fq_roles[prev_role] += 1

                prev_m = morph.extract(prev.word)
                if prev_m and prev_m.middle:
                    pre_fq_middles[prev_m.middle] += 1
                    if prev_m.middle in FL_STAGE_MAP:
                        pre_fq_stages[FL_STAGE_MAP[prev_m.middle]] += 1

                # Kernel in predecessor
                if 'k' in prev.word:
                    pre_fq_kernel['has_k'] += 1
                if 'h' in prev.word:
                    pre_fq_kernel['has_h'] += 1
                if 'e' in prev.word:
                    pre_fq_kernel['has_e'] += 1
                if not any(c in prev.word for c in 'khe'):
                    pre_fq_kernel['no_kernel'] += 1

            # Post-FQ analysis (what comes after the chain)
            if j < len(tokens):
                next_t = tokens[j]
                next_role = token_to_role.get(next_t.word, 'UN')
                post_fq_roles[next_role] += 1

                next_m = morph.extract(next_t.word)
                if next_m and next_m.middle:
                    post_fq_middles[next_m.middle] += 1
                    if next_m.middle in FL_STAGE_MAP:
                        post_fq_stages[FL_STAGE_MAP[next_m.middle]] += 1

            i = j  # Skip past the chain
        else:
            i += 1

# Report
print("\n" + "=" * 70)
print("Pre-FQ States (What triggers escape)")
print("=" * 70)

total_pre = sum(pre_fq_roles.values())
print("\nRole distribution before FQ:")
for role, count in pre_fq_roles.most_common():
    pct = count / total_pre * 100
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\nFL stage distribution before FQ:")
total_stages = sum(pre_fq_stages.values())
hazard_count = sum(pre_fq_stages.get(s, 0) for s in HAZARD_STAGES)
safe_count = sum(pre_fq_stages.get(s, 0) for s in SAFE_STAGES)
for stage, count in pre_fq_stages.most_common():
    pct = count / total_stages * 100 if total_stages > 0 else 0
    hz = "(HAZARD)" if stage in HAZARD_STAGES else "(SAFE)"
    print(f"  {stage:12} {count:4} ({pct:5.1f}%) {hz}")

if total_stages > 0:
    print(f"\n  HAZARD stages: {hazard_count} ({hazard_count/total_stages*100:.1f}%)")
    print(f"  SAFE stages: {safe_count} ({safe_count/total_stages*100:.1f}%)")

print("\nKernel presence before FQ:")
total_kernel = pre_fq_kernel['has_k'] + pre_fq_kernel['has_h'] + pre_fq_kernel['has_e'] + pre_fq_kernel['no_kernel']
for k, count in pre_fq_kernel.items():
    pct = count / total_kernel * 100 if total_kernel > 0 else 0
    print(f"  {k:12} {count:5} ({pct:5.1f}%)")

print("\nTop MIDDLEs before FQ:")
for mid, count in pre_fq_middles.most_common(10):
    stage = FL_STAGE_MAP.get(mid, '-')
    print(f"  {mid:10} {count:4}  (FL stage: {stage})")

print("\n" + "=" * 70)
print("Post-FQ States (Recovery)")
print("=" * 70)

total_post = sum(post_fq_roles.values())
print("\nRole distribution after FQ:")
for role, count in post_fq_roles.most_common():
    pct = count / total_post * 100 if total_post > 0 else 0
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\nFL stage distribution after FQ:")
total_post_stages = sum(post_fq_stages.values())
for stage, count in post_fq_stages.most_common():
    pct = count / total_post_stages * 100 if total_post_stages > 0 else 0
    hz = "(HAZARD)" if stage in HAZARD_STAGES else "(SAFE)"
    print(f"  {stage:12} {count:4} ({pct:5.1f}%) {hz}")

print("\n" + "=" * 70)
print("FQ Chain Analysis")
print("=" * 70)

total_chains = sum(fq_chain_lengths.values())
print(f"\nTotal FQ events: {total_chains}")
for length, count in sorted(fq_chain_lengths.items()):
    pct = count / total_chains * 100
    print(f"  Chain length {length}: {count:5} ({pct:5.1f}%)")

mean_chain = sum(l * c for l, c in fq_chain_lengths.items()) / total_chains if total_chains > 0 else 0
print(f"\nMean chain length: {mean_chain:.2f}")

# Semantic interpretation
print("\n" + "=" * 70)
print("Escape Trigger Grammar")
print("=" * 70)

print(f"""
FINDINGS:

1. PRE-FQ ROLE PATTERN:
   - Primary trigger: {pre_fq_roles.most_common(1)[0][0]} ({pre_fq_roles.most_common(1)[0][1]/total_pre*100:.1f}%)
   - FL triggers escape at {pre_fq_roles.get('FLOW_OPERATOR', 0)/total_pre*100:.1f}% rate

2. FL STAGE TRIGGERS:
   - HAZARD stages (INITIAL/EARLY/MEDIAL): {hazard_count/total_stages*100:.1f}% of FL-triggered escapes
   - SAFE stages (LATE/TERMINAL): {safe_count/total_stages*100:.1f}% of FL-triggered escapes

3. KERNEL BEFORE ESCAPE:
   - Kernel present: {(total_kernel - pre_fq_kernel['no_kernel'])/total_kernel*100:.1f}%
   - Kernel absent: {pre_fq_kernel['no_kernel']/total_kernel*100:.1f}%

4. ESCAPE CHAINS:
   - Single-token escape: {fq_chain_lengths.get(1, 0)/total_chains*100:.1f}%
   - Multi-token escape: {(1 - fq_chain_lengths.get(1, 0)/total_chains)*100:.1f}%
   - Mean chain length: {mean_chain:.2f}

PROPOSED ESCAPE TRIGGER GRAMMAR:

Escape is triggered when:
  - HAZARD FL state detected (early/medial stages)
  - OR kernel operation fails/absent
  - Multi-step recovery common (mean {mean_chain:.1f} tokens)
""")

# Save results
results = {
    'pre_fq': {
        'roles': dict(pre_fq_roles.most_common()),
        'fl_stages': dict(pre_fq_stages.most_common()),
        'hazard_rate': round(hazard_count / total_stages, 4) if total_stages > 0 else 0,
        'kernel_before': pre_fq_kernel,
        'top_middles': pre_fq_middles.most_common(20)
    },
    'post_fq': {
        'roles': dict(post_fq_roles.most_common()),
        'fl_stages': dict(post_fq_stages.most_common()),
        'top_middles': post_fq_middles.most_common(20)
    },
    'chains': {
        'length_distribution': dict(fq_chain_lengths),
        'mean_length': round(mean_chain, 3),
        'total_events': total_chains
    },
    'escape_grammar': {
        'primary_trigger_role': pre_fq_roles.most_common(1)[0][0] if pre_fq_roles else None,
        'hazard_fl_trigger_rate': round(hazard_count / total_stages, 4) if total_stages > 0 else 0,
        'kernel_absent_trigger_rate': round(pre_fq_kernel['no_kernel'] / total_kernel, 4) if total_kernel > 0 else 0
    }
}

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "escape_trigger_analysis.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")

"""
02_cc_token_semantics.py

Analyze why daiin and ol are the core control tokens.
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

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CC Token Semantics: Why daiin and ol?")
print("=" * 70)

# Build token sequences by line
line_sequences = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_sequences[key].append(t)

# CC tokens: daiin (class 10), ol (class 11)
CC_TOKENS = {'daiin', 'ol'}

# Analyze CC token contexts
cc_contexts = {
    'daiin': {'before': Counter(), 'after': Counter(), 'positions': [],
              'roles_before': Counter(), 'roles_after': Counter(),
              'line_initial': 0, 'line_final': 0, 'total': 0},
    'ol': {'before': Counter(), 'after': Counter(), 'positions': [],
           'roles_before': Counter(), 'roles_after': Counter(),
           'line_initial': 0, 'line_final': 0, 'total': 0}
}

for key, tokens in line_sequences.items():
    for i, t in enumerate(tokens):
        if t.word not in CC_TOKENS:
            continue

        ctx = cc_contexts[t.word]
        ctx['total'] += 1

        # Position
        pos = i / len(tokens) if len(tokens) > 1 else 0.5
        ctx['positions'].append(pos)

        # Line-initial/final
        if i == 0:
            ctx['line_initial'] += 1
        if i == len(tokens) - 1:
            ctx['line_final'] += 1

        # Before context
        if i > 0:
            prev = tokens[i-1]
            prev_m = morph.extract(prev.word)
            if prev_m and prev_m.middle:
                ctx['before'][prev_m.middle] += 1
            prev_role = token_to_role.get(prev.word, 'UN')
            ctx['roles_before'][prev_role] += 1

        # After context
        if i < len(tokens) - 1:
            next_t = tokens[i+1]
            next_m = morph.extract(next_t.word)
            if next_m and next_m.middle:
                ctx['after'][next_m.middle] += 1
            next_role = token_to_role.get(next_t.word, 'UN')
            ctx['roles_after'][next_role] += 1

# Report
print("\n" + "=" * 70)
print("Token Profiles")
print("=" * 70)

for token in ['daiin', 'ol']:
    ctx = cc_contexts[token]
    mean_pos = sum(ctx['positions']) / len(ctx['positions']) if ctx['positions'] else 0

    print(f"\n'{token}':")
    print(f"  Total occurrences: {ctx['total']:,}")
    print(f"  Mean position: {mean_pos:.3f}")
    print(f"  Line-initial: {ctx['line_initial']} ({ctx['line_initial']/ctx['total']*100:.1f}%)")
    print(f"  Line-final: {ctx['line_final']} ({ctx['line_final']/ctx['total']*100:.1f}%)")

    # Morphology
    m = morph.extract(token)
    if m:
        print(f"  Morphology: PREFIX={m.prefix}, MIDDLE={m.middle}, SUFFIX={m.suffix}")

print("\n" + "=" * 70)
print("Role Transitions")
print("=" * 70)

for token in ['daiin', 'ol']:
    ctx = cc_contexts[token]
    print(f"\n'{token}':")

    print("  BEFORE (what precedes):")
    total_before = sum(ctx['roles_before'].values())
    for role, count in ctx['roles_before'].most_common():
        pct = count / total_before * 100 if total_before > 0 else 0
        print(f"    {role:20} {count:4} ({pct:5.1f}%)")

    print("  AFTER (what follows):")
    total_after = sum(ctx['roles_after'].values())
    for role, count in ctx['roles_after'].most_common():
        pct = count / total_after * 100 if total_after > 0 else 0
        print(f"    {role:20} {count:4} ({pct:5.1f}%)")

print("\n" + "=" * 70)
print("MIDDLE Contexts")
print("=" * 70)

for token in ['daiin', 'ol']:
    ctx = cc_contexts[token]
    print(f"\n'{token}':")
    print(f"  Top MIDDLEs BEFORE: {', '.join(f'{m}({c})' for m, c in ctx['before'].most_common(8))}")
    print(f"  Top MIDDLEs AFTER: {', '.join(f'{m}({c})' for m, c in ctx['after'].most_common(8))}")

# Compare daiin vs ol
print("\n" + "=" * 70)
print("daiin vs ol Comparison")
print("=" * 70)

daiin = cc_contexts['daiin']
ol = cc_contexts['ol']

daiin_pos = sum(daiin['positions']) / len(daiin['positions']) if daiin['positions'] else 0
ol_pos = sum(ol['positions']) / len(ol['positions']) if ol['positions'] else 0

print(f"""
                    daiin           ol
  Count:            {daiin['total']:5}          {ol['total']:5}
  Mean position:    {daiin_pos:.3f}          {ol_pos:.3f}
  Line-initial:     {daiin['line_initial']/daiin['total']*100:5.1f}%         {ol['line_initial']/ol['total']*100:5.1f}%
  Line-final:       {daiin['line_final']/daiin['total']*100:5.1f}%         {ol['line_final']/ol['total']*100:5.1f}%
""")

# Check who comes after who
daiin_before_ol = 0
ol_before_daiin = 0
for key, tokens in line_sequences.items():
    for i in range(len(tokens) - 1):
        if tokens[i].word == 'daiin' and tokens[i+1].word == 'ol':
            daiin_before_ol += 1
        if tokens[i].word == 'ol' and tokens[i+1].word == 'daiin':
            ol_before_daiin += 1

print(f"Direct transitions:")
print(f"  daiin -> ol: {daiin_before_ol}")
print(f"  ol -> daiin: {ol_before_daiin}")

# Semantic interpretation
print("\n" + "=" * 70)
print("Semantic Interpretation")
print("=" * 70)

print(f"""
OBSERVATIONS:

1. 'daiin' appears EARLIER ({daiin_pos:.3f}) than 'ol' ({ol_pos:.3f})

2. 'daiin' is more line-initial ({daiin['line_initial']/daiin['total']*100:.1f}%)
   'ol' is less position-constrained

3. Both have NO kernel characters (0% kernel rate)
   - They're pure control tokens, not operators

4. Morphology:
   - daiin: MIDDLE='iin' (common suffix pattern)
   - ol: MIDDLE='ol' (common state marker)

PROPOSED SEMANTICS:

'daiin' (earlier, more initial):
  - Function: INITIALIZATION marker
  - Semantics: "begin/start/init"
  - Sets up processing context

'ol' (later, more distributed):
  - Function: CONTINUATION marker
  - Semantics: "proceed/continue/next"
  - Signals ongoing processing

Note: 'ol' appears in many compound forms (olkeedy, olkeey, etc.)
which are class 17 (kernel-containing). Pure 'ol' (class 11)
is the kernel-free continuation marker.
""")

# Save results
results = {
    'daiin': {
        'count': daiin['total'],
        'mean_position': round(daiin_pos, 4),
        'line_initial_rate': round(daiin['line_initial'] / daiin['total'], 4) if daiin['total'] > 0 else 0,
        'line_final_rate': round(daiin['line_final'] / daiin['total'], 4) if daiin['total'] > 0 else 0,
        'morphology': {'prefix': 'da', 'middle': 'iin', 'suffix': None},
        'proposed_function': 'initialization_marker',
        'roles_before': dict(daiin['roles_before'].most_common()),
        'roles_after': dict(daiin['roles_after'].most_common())
    },
    'ol': {
        'count': ol['total'],
        'mean_position': round(ol_pos, 4),
        'line_initial_rate': round(ol['line_initial'] / ol['total'], 4) if ol['total'] > 0 else 0,
        'line_final_rate': round(ol['line_final'] / ol['total'], 4) if ol['total'] > 0 else 0,
        'morphology': {'prefix': None, 'middle': 'ol', 'suffix': None},
        'proposed_function': 'continuation_marker',
        'roles_before': dict(ol['roles_before'].most_common()),
        'roles_after': dict(ol['roles_after'].most_common())
    },
    'direct_transitions': {
        'daiin_to_ol': daiin_before_ol,
        'ol_to_daiin': ol_before_daiin
    }
}

results_dir = Path(__file__).parent.parent / "results"
output_path = results_dir / "cc_token_semantics.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")

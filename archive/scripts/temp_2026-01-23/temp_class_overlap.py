"""Check if instruction class tokens appear in Currier A."""
import pandas as pd
import json

# Load instruction classes
with open('results/phase20a_operator_equivalence.json', 'r') as f:
    classes = json.load(f)

# Get all instruction class tokens
all_class_tokens = set()
for cls in classes['classes']:
    all_class_tokens.update(cls['members'])

print(f"Total unique tokens in 49 instruction classes: {len(all_class_tokens)}")

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# Get vocabulary by system
a_tokens = set(df[df['language'] == 'A']['word'].dropna().unique())
b_tokens = set(df[df['language'] == 'B']['word'].dropna().unique())

print(f"\nCurrier A vocabulary: {len(a_tokens)} unique tokens")
print(f"Currier B vocabulary: {len(b_tokens)} unique tokens")

# Check overlap
class_tokens_in_a = all_class_tokens & a_tokens
class_tokens_in_b = all_class_tokens & b_tokens
class_tokens_in_both = all_class_tokens & a_tokens & b_tokens
class_tokens_b_only = all_class_tokens & b_tokens - a_tokens

print(f"\nInstruction class tokens that appear in A: {len(class_tokens_in_a)}")
print(f"Instruction class tokens that appear in B: {len(class_tokens_in_b)}")
print(f"Instruction class tokens in BOTH (PP): {len(class_tokens_in_both)}")
print(f"Instruction class tokens B-ONLY: {len(class_tokens_b_only)}")

# Show some examples
print(f"\n--- Examples of PP instruction tokens (in both A and B) ---")
for token in sorted(class_tokens_in_both)[:20]:
    print(f"  {token}")

print(f"\n--- Examples of B-only instruction tokens ---")
for token in sorted(class_tokens_b_only)[:20]:
    print(f"  {token}")

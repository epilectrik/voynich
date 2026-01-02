# Debug CCF token mapping to instruction classes
import json
from collections import Counter

# Load CCF tokens
records = []
with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r', encoding='latin-1') as f:
    f.readline()  # skip header
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            parts = [p.strip('"') for p in parts]
            folio = parts[2]
            if folio.startswith('f67') or folio.startswith('f68') or folio.startswith('f69') or \
               folio.startswith('f70') or folio.startswith('f71') or folio.startswith('f72') or folio.startswith('f73'):
                records.append(parts[0])

ccf_tokens = Counter(records)
print(f"CCF unique tokens: {len(ccf_tokens)}")
print(f"CCF total occurrences: {sum(ccf_tokens.values())}")
print("\nTop 30 CCF tokens:")
for token, count in ccf_tokens.most_common(30):
    print(f"  {token}: {count}")

# Load instruction classes
with open('C:/git/voynich/phase20a_operator_equivalence.json', 'r') as f:
    equiv_data = json.load(f)

# Build member set
all_class_members = set()
for cls in equiv_data['classes']:
    for member in cls['members']:
        all_class_members.add(member)

print(f"\n\nInstruction class members: {len(all_class_members)}")
print("Sample class members:", list(all_class_members)[:30])

# Check overlap
ccf_token_set = set(ccf_tokens.keys())
overlap = ccf_token_set & all_class_members
print(f"\n\nDirect overlap: {len(overlap)}")
print("Overlapping tokens:", list(overlap)[:20])

# Check for partial matches (prefix/suffix)
partial_matches = 0
for ccf_token in list(ccf_tokens.keys())[:100]:
    for class_member in all_class_members:
        if ccf_token.startswith(class_member) or class_member.startswith(ccf_token):
            partial_matches += 1
            break

print(f"\nPartial matches (first 100 CCF tokens): {partial_matches}")

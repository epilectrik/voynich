"""Check which Currier language the morphology-classified folios belong to."""

from pathlib import Path

filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# All folios by Currier language
currier_a = set()
currier_b = set()

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
            if folio:
                if lang == 'A':
                    currier_a.add(folio)
                elif lang == 'B':
                    currier_b.add(folio)

morphology_folios = ['f26r', 'f26v', 'f31r', 'f34r', 'f39r', 'f41v', 'f43r', 'f55v',
                     'f33r', 'f39v', 'f40r', 'f40v', 'f46v', 'f50r', 'f50v',
                     'f33v', 'f41r', 'f46r', 'f48r', 'f48v', 'f55r']

print("Morphology-classified folios by Currier language:")
print("-" * 50)
a_count = 0
b_count = 0
neither = 0

for mf in morphology_folios:
    if mf in currier_a:
        print(f"  {mf}: Currier A")
        a_count += 1
    elif mf in currier_b:
        print(f"  {mf}: Currier B")
        b_count += 1
    else:
        print(f"  {mf}: NOT FOUND")
        neither += 1

print(f"\nSummary: {a_count} in A, {b_count} in B, {neither} not found")

# List Currier A folios that have herbal section markers
print("\n\nCurrier A folios (for new morphology classification):")
print("-" * 50)
for f in sorted(currier_a)[:50]:
    print(f"  {f}")
print(f"  ... ({len(currier_a)} total)")

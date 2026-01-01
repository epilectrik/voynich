import csv

folios = set()
with open('data/transcriptions/interlinear_full_words.txt', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        folio = row.get('folio', '').strip().strip('"')
        folios.add(folio)

zodiac_prefixes = ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73']
zodiac = sorted([x for x in folios if any(x.startswith(p) for p in zodiac_prefixes)])

print("Zodiac folios found:")
for f in zodiac:
    print(f"  {f}")

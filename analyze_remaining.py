"""Analyze remaining untranslated words across first 5 folios."""
import json
import sys
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

dict_path = project_root / "dictionary.json"
with open(dict_path) as f:
    dictionary = json.load(f)

data_dir = project_root / "data" / "transcriptions"
corpus = load_corpus(str(data_dir))

entries = dictionary['entries']
folios = ["f1r", "f1v", "f2r", "f2v", "f3r"]

# Get untranslated words per folio
untrans_by_folio = {}
all_untrans = Counter()

for folio in folios:
    words = [w.text for w in corpus.words if w.folio == folio]
    untrans = [w for w in words if w not in entries]
    untrans_by_folio[folio] = Counter(untrans)
    all_untrans.update(untrans)

print("=== Untranslated words across first 5 folios ===\n")
print(f"Total untranslated word tokens: {sum(all_untrans.values())}")
print(f"Unique untranslated words: {len(all_untrans)}\n")

print("Top 30 most frequent untranslated (from these 5 folios only):")
for word, count in all_untrans.most_common(30):
    folios_in = [f for f, c in untrans_by_folio.items() if word in c]
    print(f"  {word:<20} {count:>3}x  [{', '.join(folios_in)}]")

print("\n\n=== Words unique to each folio ===\n")
for folio in folios:
    unique = [w for w in untrans_by_folio[folio] if all_untrans[w] == untrans_by_folio[folio][w]]
    if unique:
        print(f"{folio}: {len(unique)} unique untranslated words")
        for w in list(unique)[:10]:
            print(f"  {w}")

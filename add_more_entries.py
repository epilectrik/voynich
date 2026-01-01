"""Add more entries based on morphological patterns and frequency analysis."""
import json
import sys
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.parser.voynich_parser import load_corpus

# Load dictionary
dict_path = project_root / "dictionary.json"
with open(dict_path) as f:
    dictionary = json.load(f)

# Load corpus
data_dir = project_root / "data" / "transcriptions"
corpus = load_corpus(str(data_dir))

# Get all words
all_words = [w.text for w in corpus.words]
word_freq = Counter(all_words)

# Get untranslated words
entries = dictionary['entries']
untranslated = [(w, c) for w, c in word_freq.most_common() if w not in entries]

print(f"Total unique words: {len(word_freq)}")
print(f"Translated: {len(entries)}")
print(f"Untranslated: {len(untranslated)}")
print(f"\nTop 50 untranslated words:")
for w, c in untranslated[:50]:
    print(f"  {w:<20} ({c}x)")

# Analyze patterns in untranslated words
print("\n\n=== Pattern Analysis ===")

# Words ending in common suffixes
suffix_groups = {}
for word, _ in untranslated:
    if word.endswith('aiin'):
        suffix_groups.setdefault('-aiin', []).append(word)
    elif word.endswith('ain'):
        suffix_groups.setdefault('-ain', []).append(word)
    elif word.endswith('ol'):
        suffix_groups.setdefault('-ol', []).append(word)
    elif word.endswith('ar'):
        suffix_groups.setdefault('-ar', []).append(word)
    elif word.endswith('or'):
        suffix_groups.setdefault('-or', []).append(word)
    elif word.endswith('ey'):
        suffix_groups.setdefault('-ey', []).append(word)
    elif word.endswith('y'):
        suffix_groups.setdefault('-y', []).append(word)

for suffix, words in sorted(suffix_groups.items(), key=lambda x: -len(x[1])):
    print(f"\n{suffix} ({len(words)} words):")
    for w in words[:10]:
        print(f"  {w}")

# Words starting with common prefixes
prefix_groups = {}
for word, _ in untranslated:
    if word.startswith('ot'):
        prefix_groups.setdefault('ot-', []).append(word)
    elif word.startswith('ch'):
        prefix_groups.setdefault('ch-', []).append(word)
    elif word.startswith('sh'):
        prefix_groups.setdefault('sh-', []).append(word)
    elif word.startswith('qo'):
        prefix_groups.setdefault('qo-', []).append(word)
    elif word.startswith('ok'):
        prefix_groups.setdefault('ok-', []).append(word)
    elif word.startswith('da'):
        prefix_groups.setdefault('da-', []).append(word)
    elif word.startswith('ol'):
        prefix_groups.setdefault('ol-', []).append(word)

print("\n\n=== Prefix Groups ===")
for prefix, words in sorted(prefix_groups.items(), key=lambda x: -len(x[1])):
    print(f"\n{prefix} ({len(words)} words):")
    for w in words[:10]:
        print(f"  {w} ({word_freq[w]}x)")

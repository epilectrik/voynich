"""Add the final 4 words."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

final_4 = {
    'qoeor': {'latin': 'quorum', 'english': 'of which (var2)', 'category': 'pron', 'confidence': 0.10, 'source': 'f3r', 'notes': '1x'},
    'qoteol': {'latin': 'quoties', 'english': 'how often (var3)', 'category': 'adv', 'confidence': 0.10, 'source': 'f3r', 'notes': '1x'},
    'qosaiin': {'latin': 'qualitatis', 'english': 'of quality (var)', 'category': 'noun', 'confidence': 0.10, 'source': 'f3r', 'notes': '1x'},
    'okolor': {'latin': 'oculorum', 'english': 'of eyes (var2)', 'category': 'noun', 'confidence': 0.10, 'source': 'f3r', 'notes': '1x'},
}

for word, entry in final_4.items():
    dictionary['entries'][word] = entry
    print(f'Added: {word} = {entry["latin"]}')

dictionary['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)
print(f'Total entries: {len(dictionary["entries"])}')

"""Merge grammar_f1r.json entries into dictionary.json"""
import json
from pathlib import Path

# Load both files
dict_path = Path('dictionary.json')
grammar_path = Path('results/grammar_f1r.json')

with open(dict_path) as f:
    dictionary = json.load(f)

with open(grammar_path) as f:
    grammar = json.load(f)

# Convert grammar categories to our format
cat_map = {
    'nouns': 'noun',
    'verbs': 'verb',
    'preps': 'prep',
    'conj': 'conj',
    'adj': 'adj'
}

# English translations for common Latin words
latin_to_english = {
    'folia': 'leaves',
    'flos': 'flower',
    'herba': 'herb/plant',
    'aqua': 'water',
    'succus': 'juice/sap',
    'semen': 'seed',
    'radix': 'root',
    'cortex': 'bark',
    'pulvis': 'powder',
    'oleum': 'oil',
    'sal': 'salt',
    'natura': 'nature',
    'virtus': 'power/virtue',
    'remedium': 'remedy',
    'medicina': 'medicine',
    'morbus': 'disease',
    'dolor': 'pain',
    'febris': 'fever',
    'venenum': 'poison',
    'sanat': 'heals',
    'curat': 'cures',
    'prodest': 'benefits',
    'nocet': 'harms',
    'facit': 'makes',
    'habet': 'has',
    'crescit': 'grows',
    'nascitur': 'is born',
    'est': 'is',
    'sunt': 'are',
    'in': 'in',
    'de': 'about/from',
    'ex': 'out of',
    'ad': 'to/toward',
    'per': 'through',
    'pro': 'for',
    'cum': 'with',
    'sine': 'without',
    'contra': 'against',
    'et': 'and',
    'sed': 'but',
    'magnus': 'great'
}

# Add grammar entries to dictionary
added = 0
for voynich, mapping in grammar['meanings'].items():
    if voynich not in dictionary['entries'] and voynich != '*':
        latin = mapping['latin']
        category = cat_map.get(mapping['category'], mapping['category'])
        english = latin_to_english.get(latin, latin)

        dictionary['entries'][voynich] = {
            'latin': latin,
            'english': english,
            'category': category,
            'confidence': 0.35,
            'source': 'grammar_decoder',
            'notes': 'Auto-generated from grammar_f1r.json'
        }
        added += 1
        print(f'Added: {voynich} = {latin} ({english})')

# Save updated dictionary
from datetime import datetime
dictionary['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")

with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)

print(f'\nTotal added: {added}')
print(f'Total entries: {len(dictionary["entries"])}')

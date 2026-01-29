"""
04_f66r_investigation.py - What is f66r?

f66r has 28 single-character "paragraphs" followed by 9 normal paragraphs.
Characters: y, o, s, d, f, x, r, t, c, l, p

Is this:
A) An index/table of contents?
B) Labels for a diagram?
C) A completely different document type?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load data
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    par_results = Path(__file__).resolve().parents[3] / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    print("=== F66R INVESTIGATION ===\n")

    # Get f66r paragraphs
    f66r_pars = [p for p in inventory['paragraphs'] if p.get('folio') == 'f66r']
    f66r_pars.sort(key=lambda x: x['par_id'])

    print(f"f66r paragraphs: {len(f66r_pars)}")

    # === 1. PARAGRAPH SEQUENCE ===
    print("\n--- 1. PARAGRAPH SEQUENCE ---\n")

    for p in f66r_pars:
        par_id = p['par_id']
        tokens = tokens_by_par.get(par_id, [])
        words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]
        lines = p.get('lines', [])

        if len(words) <= 3:
            print(f"{par_id}: {' '.join(words)} (lines: {lines})")
        else:
            print(f"{par_id}: {' '.join(words[:5])}... ({len(words)} tokens, lines: {lines})")

    # === 2. SINGLE-CHAR ANALYSIS ===
    print("\n--- 4. SINGLE-CHAR TOKEN ANALYSIS ---\n")

    single_chars = []
    for p in f66r_pars:
        par_id = p['par_id']
        tokens = tokens_by_par.get(par_id, [])
        words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]

        if len(words) == 1 and len(words[0]) == 1:
            char = words[0]
            line = p.get('lines', ['?'])[0] if p.get('lines') else '?'
            single_chars.append((char, line, par_id))

    print(f"Single-character paragraphs: {len(single_chars)}")
    print("\nCharacter sequence:")
    chars_only = [c for c, _, _ in single_chars]
    print(f"  {' '.join(chars_only)}")

    # Check if it's an alphabet or pattern
    char_counter = Counter(chars_only)
    print(f"\nCharacter frequencies:")
    for char, count in char_counter.most_common():
        print(f"  {char}: {count}")

    # === 5. ARE THESE KERNEL CHARACTERS? ===
    print("\n--- 5. KERNEL CHARACTER CHECK ---\n")

    KERNEL = {'k', 'h', 'e'}
    PRIMITIVES = {'s', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r'}
    GALLOWS = {'t', 'k', 'p', 'f'}

    kernel_count = sum(1 for c in chars_only if c in KERNEL)
    primitive_count = sum(1 for c in chars_only if c in PRIMITIVES)
    gallows_count = sum(1 for c in chars_only if c in GALLOWS)

    print(f"Kernel characters (k,h,e): {kernel_count}/{len(chars_only)}")
    print(f"Primitive characters: {primitive_count}/{len(chars_only)}")
    print(f"Gallows characters: {gallows_count}/{len(chars_only)}")

    # === 6. COMPARE F66R NORMAL PARAGRAPHS TO OTHER PHARMA ===
    print("\n--- 6. F66R NORMAL PARAGRAPHS vs REST OF PHARMA ---\n")

    f66r_normal_pars = []
    f66r_label_pars = []

    for p in f66r_pars:
        par_id = p['par_id']
        tokens = tokens_by_par.get(par_id, [])
        words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]

        if len(words) >= 6:
            f66r_normal_pars.append(par_id)
        else:
            f66r_label_pars.append(par_id)

    # Get f57r and f66v paragraphs
    other_pharma_pars = []
    for p in inventory['paragraphs']:
        folio = p.get('folio', '')
        if folio in ['f57r', 'f66v']:
            tokens = tokens_by_par.get(p['par_id'], [])
            words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]
            if len(words) >= 6:
                other_pharma_pars.append(p['par_id'])

    def get_ht_rate(par_ids):
        ht = 0
        total = 0
        for par_id in par_ids:
            for t in tokens_by_par.get(par_id, []):
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                if word not in class_map:
                    ht += 1
        return ht / total if total > 0 else 0

    f66r_normal_ht = get_ht_rate(f66r_normal_pars)
    other_pharma_ht = get_ht_rate(other_pharma_pars)

    print(f"f66r normal paragraphs (6+): {len(f66r_normal_pars)}, HT rate: {f66r_normal_ht:.1%}")
    print(f"f57r + f66v paragraphs (6+): {len(other_pharma_pars)}, HT rate: {other_pharma_ht:.1%}")

    # === 7. WHAT'S IN THE NORMAL F66R PARAGRAPHS? ===
    print("\n--- 7. F66R NORMAL PARAGRAPH CONTENT ---\n")

    for par_id in f66r_normal_pars[:5]:
        tokens = tokens_by_par.get(par_id, [])
        words = [t['word'] for t in tokens if t['word'] and '*' not in t['word']]
        ht_count = sum(1 for w in words if w not in class_map)

        print(f"{par_id}: {len(words)} tokens, {ht_count} HT ({ht_count/len(words):.1%})")
        print(f"  {' '.join(words[:12])}...")
        print()

    # === VERDICT ===
    print("=== VERDICT ===\n")

    print(f"f66r structure:")
    print(f"  - {len(f66r_label_pars)} label paragraphs (single-char or tiny)")
    print(f"  - {len(f66r_normal_pars)} normal paragraphs")
    print(f"  - Single-char sequence: {' '.join(chars_only)}")
    print(f"  - Characters are {primitive_count}/{len(chars_only)} primitives ({primitive_count/len(chars_only):.1%})")

    if primitive_count / len(chars_only) > 0.8:
        print("\n  INTERPRETATION: Single-chars are PRIMITIVE INDEX labels")
        print("  f66r may be a reference/index folio listing primitive operations")
    else:
        print("\n  INTERPRETATION: Unknown structure - may be diagram labels")

    # Save
    output = {
        'folio': 'f66r',
        'total_paragraphs': len(f66r_pars),
        'label_paragraphs': len(f66r_label_pars),
        'normal_paragraphs': len(f66r_normal_pars),
        'single_char_sequence': chars_only,
        'char_frequencies': dict(char_counter),
        'primitive_rate': primitive_count / len(chars_only) if chars_only else 0,
        'normal_par_ht_rate': f66r_normal_ht
    }

    with open(results_dir / 'f66r_investigation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to f66r_investigation.json")

if __name__ == '__main__':
    main()

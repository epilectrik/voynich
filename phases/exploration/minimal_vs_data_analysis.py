"""
MINIMAL vs DATA Token Analysis for Currier A

Exploring the functional distinction between:
- MINIMAL: prefix + suffix only (no middle)
- DATA: prefix + middle + suffix (has content payload)

Research questions:
1. What's the overall ratio?
2. Do certain prefixes favor MINIMAL or DATA?
3. Are there positional patterns (line-initial/final)?
4. Section-level variation?
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

# Import the morphology functions from folio_viewer
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'apps' / 'script_explorer'))
from ui.folio_viewer import (
    segment_word_4component, get_a_token_role,
    KNOWN_PREFIXES, KNOWN_SUFFIXES, A_STRUCTURAL_TOKENS
)

# Currier A folios
CURRIER_A_FOLIOS = {
    '100r', '100v', '101r1', '101v2', '102r1', '102r2', '102v1', '102v2',
    '10r', '10v', '11r', '11v', '13r', '13v', '14r', '14v', '15r', '15v',
    '16r', '16v', '17r', '17v', '18r', '18v', '19r', '19v', '1r', '1v',
    '20r', '20v', '21r', '21v', '22r', '22v', '23r', '23v', '24r', '24v',
    '25r', '25v', '27r', '27v', '28r', '28v', '29r', '29v', '2r', '2v',
    '30r', '30v', '32r', '32v', '35r', '35v', '36r', '36v', '37r', '37v',
    '38r', '38v', '3r', '3v', '42r', '42v', '44r', '44v', '45r', '45v',
    '47r', '47v', '49r', '49v', '4r', '4v', '51r', '51v', '52r', '52v',
    '53r', '53v', '54r', '54v', '56r', '56v', '58r', '58v', '5r', '5v',
    '6r', '6v', '7r', '7v', '87r', '87v', '88r', '88v', '89r1', '89r2',
    '89v1', '89v2', '8r', '8v', '90r1', '90r2', '90v1', '90v2', '93r', '93v',
    '96r', '96v', '99r', '99v', '9r', '9v'
}


def load_currier_a_tokens():
    """Load all tokens from Currier A folios with position info."""
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            folio = row.get('folio', '').strip('"').replace('f', '')
            if folio in CURRIER_A_FOLIOS:
                word = row.get('word', '').strip('"')
                if word and not word.startswith('*'):
                    tokens.append({
                        'word': word,
                        'folio': folio,
                        'section': row.get('section', '').strip('"'),
                        'line': row.get('line', ''),
                        'position': row.get('wid', ''),  # word position in line
                    })
    return tokens


def analyze_token(token):
    """Analyze a single token and return its role and morphology."""
    word = token['word']
    articulator, prefix, middle, suffix = segment_word_4component(word)
    role = get_a_token_role(word)

    return {
        **token,
        'articulator': articulator,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'role': role,
        'has_middle': bool(middle),
    }


def main():
    print("=" * 60)
    print("MINIMAL vs DATA Token Analysis - Currier A")
    print("=" * 60)

    # Load and analyze tokens
    raw_tokens = load_currier_a_tokens()
    print(f"\nLoaded {len(raw_tokens)} tokens from Currier A folios")

    tokens = [analyze_token(t) for t in raw_tokens]

    # 1. Overall role distribution
    print("\n" + "=" * 60)
    print("1. OVERALL ROLE DISTRIBUTION")
    print("=" * 60)

    role_counts = Counter(t['role'] for t in tokens)
    total = len(tokens)
    for role, count in role_counts.most_common():
        pct = count / total * 100
        print(f"  {role:15s}: {count:5d} ({pct:5.1f}%)")

    # 2. MINIMAL vs DATA by prefix
    print("\n" + "=" * 60)
    print("2. MINIMAL vs DATA BY PREFIX FAMILY")
    print("=" * 60)

    prefix_roles = defaultdict(lambda: {'MINIMAL': 0, 'DATA': 0, 'OTHER': 0})
    for t in tokens:
        prefix = t['prefix'].lower() if t['prefix'] else 'none'
        role = t['role']
        if role == 'MINIMAL':
            prefix_roles[prefix]['MINIMAL'] += 1
        elif role == 'DATA':
            prefix_roles[prefix]['DATA'] += 1
        else:
            prefix_roles[prefix]['OTHER'] += 1

    print(f"\n  {'Prefix':<8} {'MINIMAL':>8} {'DATA':>8} {'Other':>8} {'%DATA':>8}")
    print("  " + "-" * 44)
    for prefix in sorted(prefix_roles.keys(), key=lambda p: prefix_roles[p]['MINIMAL'] + prefix_roles[p]['DATA'], reverse=True)[:15]:
        counts = prefix_roles[prefix]
        m, d, o = counts['MINIMAL'], counts['DATA'], counts['OTHER']
        total_md = m + d
        pct_data = (d / total_md * 100) if total_md > 0 else 0
        print(f"  {prefix:<8} {m:>8} {d:>8} {o:>8} {pct_data:>7.1f}%")

    # 3. Positional patterns
    print("\n" + "=" * 60)
    print("3. POSITIONAL PATTERNS (Line Position)")
    print("=" * 60)

    # Group by line to find first/last positions
    lines = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line'])
        lines[key].append(t)

    position_roles = {'first': Counter(), 'last': Counter(), 'middle': Counter()}
    for line_tokens in lines.values():
        if len(line_tokens) >= 1:
            position_roles['first'][line_tokens[0]['role']] += 1
            position_roles['last'][line_tokens[-1]['role']] += 1
        if len(line_tokens) >= 3:
            for t in line_tokens[1:-1]:
                position_roles['middle'][t['role']] += 1

    print(f"\n  {'Position':<10} {'MINIMAL':>10} {'DATA':>10} {'%MINIMAL':>10}")
    print("  " + "-" * 42)
    for pos in ['first', 'last', 'middle']:
        m = position_roles[pos].get('MINIMAL', 0)
        d = position_roles[pos].get('DATA', 0)
        total = m + d
        pct = (m / total * 100) if total > 0 else 0
        print(f"  {pos:<10} {m:>10} {d:>10} {pct:>9.1f}%")

    # 4. Section patterns
    print("\n" + "=" * 60)
    print("4. SECTION PATTERNS")
    print("=" * 60)

    section_roles = defaultdict(lambda: {'MINIMAL': 0, 'DATA': 0})
    for t in tokens:
        section = t['section'] if t['section'] else 'unknown'
        if t['role'] == 'MINIMAL':
            section_roles[section]['MINIMAL'] += 1
        elif t['role'] == 'DATA':
            section_roles[section]['DATA'] += 1

    print(f"\n  {'Section':<10} {'MINIMAL':>10} {'DATA':>10} {'%DATA':>10}")
    print("  " + "-" * 42)
    for section in sorted(section_roles.keys()):
        m = section_roles[section]['MINIMAL']
        d = section_roles[section]['DATA']
        total = m + d
        pct = (d / total * 100) if total > 0 else 0
        print(f"  {section:<10} {m:>10} {d:>10} {pct:>9.1f}%")

    # 5. Most common MINIMAL and DATA tokens
    print("\n" + "=" * 60)
    print("5. MOST COMMON TOKENS BY ROLE")
    print("=" * 60)

    minimal_tokens = Counter(t['word'] for t in tokens if t['role'] == 'MINIMAL')
    data_tokens = Counter(t['word'] for t in tokens if t['role'] == 'DATA')

    print("\n  Top 15 MINIMAL tokens:")
    for word, count in minimal_tokens.most_common(15):
        art, pre, mid, suf = segment_word_4component(word)
        print(f"    {word:<15} {count:>5}  [{pre}] + () + [{suf}]")

    print("\n  Top 15 DATA tokens:")
    for word, count in data_tokens.most_common(15):
        art, pre, mid, suf = segment_word_4component(word)
        print(f"    {word:<15} {count:>5}  [{pre}] + ({mid}) + [{suf}]")

    # 6. Middle component analysis
    print("\n" + "=" * 60)
    print("6. MIDDLE COMPONENT INVENTORY")
    print("=" * 60)

    middle_counts = Counter(t['middle'] for t in tokens if t['middle'])
    print(f"\n  Unique middle components: {len(middle_counts)}")
    print("\n  Top 20 middle components:")
    for mid, count in middle_counts.most_common(20):
        print(f"    '{mid}'  : {count:>5}")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()

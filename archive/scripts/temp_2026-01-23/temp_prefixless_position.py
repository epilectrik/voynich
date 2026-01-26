#!/usr/bin/env python3
"""
Check if prefix-less tokens are positionally special (first on folio/line).
"""

import csv
from collections import Counter, defaultdict

ARTICULATORS = ['y', 'k', 'l', 'p', 'd', 'f', 'r', 's', 't']

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct',
            'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
            'lk', 'yk', 'lsh', 'ke', 'te', 'se', 'de', 'pe',
            'ko', 'to', 'so', 'do', 'po', 'ka', 'ta', 'sa', 'al', 'ar', 'or']
PREFIXES = sorted(set(PREFIXES), key=len, reverse=True)

def find_prefix(token):
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p):
            return p, token[len(p):]
    return None, token

def has_prefix(token):
    """Check if token has prefix (directly or with articulator)."""
    prefix, _ = find_prefix(token)
    if prefix:
        return True

    # Check for articulator + prefix
    for art in ARTICULATORS:
        if token.startswith(art) and len(token) > len(art):
            after_art = token[len(art):]
            prefix, _ = find_prefix(after_art)
            if prefix:
                return True
    return False

# Collect token data with position
tokens_data = []

with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip().strip('"') != 'H':
            continue
        if row.get('language', '').strip() != 'A':
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        folio = row.get('folio', '').strip()
        line = row.get('line_number', '').strip()
        line_initial = row.get('line_initial', '').strip()
        line_final = row.get('line_final', '').strip()
        par_initial = row.get('par_initial', '').strip()

        tokens_data.append({
            'word': word,
            'folio': folio,
            'line': line,
            'line_initial': line_initial == '1',
            'line_final': line_final == '1',
            'par_initial': par_initial == '1',
            'has_prefix': has_prefix(word)
        })

print("="*70)
print("PREFIX-LESS TOKEN POSITION ANALYSIS")
print("="*70)

prefixed = [t for t in tokens_data if t['has_prefix']]
prefixless = [t for t in tokens_data if not t['has_prefix']]

print(f"\nTotal Currier A tokens: {len(tokens_data)}")
print(f"  Prefixed: {len(prefixed)} ({100*len(prefixed)/len(tokens_data):.1f}%)")
print(f"  Prefix-less: {len(prefixless)} ({100*len(prefixless)/len(tokens_data):.1f}%)")

# ============================================================
# CHECK: First token on paragraph (par_initial)?
# ============================================================
print("\n" + "="*70)
print("1. PARAGRAPH-INITIAL TOKENS")
print("="*70)

prefixless_par_init = [t for t in prefixless if t['par_initial']]
prefixed_par_init = [t for t in prefixed if t['par_initial']]
total_par_init = len([t for t in tokens_data if t['par_initial']])

if total_par_init > 0:
    print(f"\nTotal paragraph-initial tokens: {total_par_init}")
    print(f"  Prefixed: {len(prefixed_par_init)} ({100*len(prefixed_par_init)/total_par_init:.1f}%)")
    print(f"  Prefix-less: {len(prefixless_par_init)} ({100*len(prefixless_par_init)/total_par_init:.1f}%)")

    overall_prefixless_rate = 100 * len(prefixless) / len(tokens_data)
    par_prefixless_rate = 100 * len(prefixless_par_init) / total_par_init

    print(f"\nPrefix-less rate comparison:")
    print(f"  Overall: {overall_prefixless_rate:.1f}%")
    print(f"  Paragraph-initial: {par_prefixless_rate:.1f}%")

    if par_prefixless_rate > overall_prefixless_rate * 1.5:
        print(f"  --> PARAGRAPH-INITIAL ENRICHED ({par_prefixless_rate/overall_prefixless_rate:.1f}x)")

    print(f"\nParagraph-initial prefix-less tokens:")
    for t in prefixless_par_init[:20]:
        print(f"  {t['folio']}.{t['line']}: {t['word']}")
else:
    print("  No paragraph-initial markers found")

# ============================================================
# CHECK: First token on line?
# ============================================================
print("\n" + "="*70)
print("2. LINE-INITIAL TOKENS")
print("="*70)

prefixless_line_init = [t for t in prefixless if t['line_initial']]
prefixed_line_init = [t for t in prefixed if t['line_initial']]
total_line_init = len([t for t in tokens_data if t['line_initial']])

if total_line_init > 0:
    print(f"\nTotal line-initial tokens: {total_line_init}")
    print(f"  Prefixed: {len(prefixed_line_init)} ({100*len(prefixed_line_init)/total_line_init:.1f}%)")
    print(f"  Prefix-less: {len(prefixless_line_init)} ({100*len(prefixless_line_init)/total_line_init:.1f}%)")

    overall_prefixless_rate = 100 * len(prefixless) / len(tokens_data)
    line_prefixless_rate = 100 * len(prefixless_line_init) / total_line_init

    print(f"\nPrefix-less rate comparison:")
    print(f"  Overall: {overall_prefixless_rate:.1f}%")
    print(f"  Line-initial: {line_prefixless_rate:.1f}%")

    if line_prefixless_rate > overall_prefixless_rate * 1.5:
        print(f"  --> LINE-INITIAL ENRICHED ({line_prefixless_rate/overall_prefixless_rate:.1f}x)")
    elif line_prefixless_rate < overall_prefixless_rate * 0.67:
        print(f"  --> LINE-INITIAL DEPLETED ({line_prefixless_rate/overall_prefixless_rate:.2f}x)")
    else:
        print(f"  --> Similar rates")
else:
    print("  No line-initial markers found")

# ============================================================
# CHECK: Line-final tokens
# ============================================================
print("\n" + "="*70)
print("3. LINE-FINAL TOKENS")
print("="*70)

prefixless_line_final = [t for t in prefixless if t['line_final']]
prefixed_line_final = [t for t in prefixed if t['line_final']]
total_line_final = len([t for t in tokens_data if t['line_final']])

if total_line_final > 0:
    print(f"\nTotal line-final tokens: {total_line_final}")
    print(f"  Prefixed: {len(prefixed_line_final)} ({100*len(prefixed_line_final)/total_line_final:.1f}%)")
    print(f"  Prefix-less: {len(prefixless_line_final)} ({100*len(prefixless_line_final)/total_line_final:.1f}%)")

    line_final_prefixless_rate = 100 * len(prefixless_line_final) / total_line_final

    print(f"\nPrefix-less rate comparison:")
    print(f"  Overall: {overall_prefixless_rate:.1f}%")
    print(f"  Line-final: {line_final_prefixless_rate:.1f}%")

# ============================================================
# CHECK: What ARE the prefix-less tokens?
# ============================================================
print("\n" + "="*70)
print("4. PREFIX-LESS TOKEN VOCABULARY")
print("="*70)

prefixless_words = Counter(t['word'] for t in prefixless)

print(f"\nUnique prefix-less token types: {len(prefixless_words)}")
print(f"\nMost common prefix-less tokens:")
for word, cnt in prefixless_words.most_common(30):
    print(f"  {word}: {cnt}")

# ============================================================
# CHECK: Starting characters of prefix-less
# ============================================================
print("\n" + "="*70)
print("5. STARTING CHARACTERS OF PREFIX-LESS TOKENS")
print("="*70)

prefixless_starts = Counter(t['word'][0] for t in prefixless if t['word'])

print(f"\nStarting character distribution:")
for char, cnt in prefixless_starts.most_common():
    pct = 100 * cnt / len(prefixless)
    print(f"  '{char}': {cnt} ({pct:.1f}%)")

# ============================================================
# CHECK: Are these recognizable patterns?
# ============================================================
print("\n" + "="*70)
print("6. PATTERN ANALYSIS OF PREFIX-LESS TOKENS")
print("="*70)

# Check for common starting patterns
starting_bigrams = Counter(t['word'][:2] for t in prefixless if len(t['word']) >= 2)
print(f"\nMost common starting bigrams:")
for bg, cnt in starting_bigrams.most_common(15):
    pct = 100 * cnt / len(prefixless)
    print(f"  '{bg}': {cnt} ({pct:.1f}%)")

# Check if any look like they should have prefix
print(f"\nPrefix-less tokens that START with a known prefix string:")
potential_prefix_issues = []
for t in prefixless:
    word = t['word']
    for p in PREFIXES:
        if word.startswith(p) and len(word) > len(p):
            # Why wasn't this recognized as having prefix?
            # Check: maybe the prefix IS the whole word after suffix strip?
            potential_prefix_issues.append((word, p))
            break

print(f"  Count: {len(potential_prefix_issues)}")
if potential_prefix_issues:
    print(f"  Examples:")
    for word, p in potential_prefix_issues[:15]:
        print(f"    {word} starts with '{p}'")

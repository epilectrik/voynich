#!/usr/bin/env python3
"""
Analyze paragraphs within specific B folios to understand what distinguishes them.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

tx = Transcript()

GALLOWS = {'k', 't', 'p', 'f'}

# Build line-grouped tokens per folio
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

# Identify paragraphs per folio
def get_paragraphs(folio):
    """Return list of paragraphs, each paragraph is list of (line_num, [tokens])"""
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []

    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue

        first_word = tokens[0].word
        # Check if gallows-initial (new paragraph)
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))

    if current_para:
        paragraphs.append(current_para)

    return paragraphs

# Count paragraphs per folio
folio_para_count = {}
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    folio_para_count[folio] = len(paras)

# Find good candidate folios (5-8 paragraphs)
print("="*70)
print("FOLIOS WITH 5-8 PARAGRAPHS")
print("="*70)

good_folios = [(f, c) for f, c in folio_para_count.items() if 5 <= c <= 8]
good_folios.sort(key=lambda x: (-x[1], x[0]))

for f, c in good_folios[:15]:
    total_tokens = sum(len(folio_line_tokens[f][l]) for l in folio_line_tokens[f])
    print(f"  {f}: {c} paragraphs, {total_tokens} tokens")

# Detailed analysis of a specific folio
def analyze_folio(folio):
    print(f"\n{'='*70}")
    print(f"DETAILED ANALYSIS: {folio}")
    print("="*70)

    paragraphs = get_paragraphs(folio)
    print(f"\nTotal paragraphs: {len(paragraphs)}")

    for i, para in enumerate(paragraphs):
        print(f"\n{'-'*50}")
        print(f"PARAGRAPH {i+1}")
        print("-"*50)

        # Get all tokens in this paragraph
        all_tokens = []
        for line_num, tokens in para:
            all_tokens.extend(tokens)

        words = [t.word for t in all_tokens]

        # First token (gallows marker)
        first_word = words[0] if words else ""
        gallows = first_word[0] if first_word else "?"

        print(f"  Gallows marker: {gallows}")
        print(f"  First token: {first_word}")
        print(f"  Lines: {len(para)}")
        print(f"  Tokens: {len(all_tokens)}")

        # Unique vocabulary
        unique_words = set(words)
        print(f"  Unique tokens: {len(unique_words)}")

        # Show first few tokens of each line
        print(f"  Content preview:")
        for line_num, tokens in para[:3]:  # First 3 lines
            line_words = [t.word for t in tokens[:8]]  # First 8 tokens
            print(f"    L{line_num}: {' '.join(line_words)}...")
        if len(para) > 3:
            print(f"    ... ({len(para)-3} more lines)")

        # Analyze PREFIX distribution
        prefixes = defaultdict(int)
        for w in words:
            if len(w) >= 2:
                # Simple prefix extraction (first 2-3 chars before common middles)
                for plen in [3, 2]:
                    prefix = w[:plen]
                    if prefix in ['qok', 'che', 'she', 'cho', 'sho', 'pch', 'tch', 'dch']:
                        prefixes[prefix] += 1
                        break
                    elif prefix[:2] in ['qo', 'ch', 'sh', 'po', 'tc', 'pc', 'dc', 'ok', 'ot']:
                        prefixes[prefix[:2]] += 1
                        break

        if prefixes:
            top_prefixes = sorted(prefixes.items(), key=lambda x: -x[1])[:5]
            print(f"  Top prefixes: {', '.join([f'{p}({c})' for p,c in top_prefixes])}")

        # Check for kernel characters
        k_count = sum(w.count('k') for w in words)
        h_count = sum(w.count('h') for w in words)
        e_count = sum(w.count('e') for w in words)
        total_kernel = k_count + h_count + e_count
        if total_kernel > 0:
            print(f"  Kernel: k={k_count}({100*k_count/total_kernel:.0f}%) h={h_count}({100*h_count/total_kernel:.0f}%) e={e_count}({100*e_count/total_kernel:.0f}%)")

# Analyze a couple of folios
print("\n" + "="*70)
print("SELECTING FOLIOS FOR DETAILED ANALYSIS")
print("="*70)

# Pick one from the good list
if good_folios:
    target_folio = good_folios[0][0]
    analyze_folio(target_folio)

    if len(good_folios) > 3:
        target_folio2 = good_folios[3][0]
        analyze_folio(target_folio2)

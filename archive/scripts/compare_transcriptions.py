#!/usr/bin/env python3
"""Compare our transcription against official ZL to check if project is valid."""
import re
from collections import Counter

# Read both files
with open('data/transcriptions/voynich_eva.txt', 'r', encoding='utf-8', errors='replace') as f:
    ours = f.read()
with open('data/transcriptions/ZL_official.txt', 'r', encoding='utf-8', errors='replace') as f:
    zl = f.read()

# Write output to file to avoid encoding issues
out = open('comparison_report.txt', 'w', encoding='utf-8')

# Extract f2v from both
our_pattern = re.compile(r'<2v\.(\d+)>(.+)')
zl_pattern = re.compile(r'<f2v\.(\d+)[^>]*>(.+)')

out.write('=== LINE BY LINE COMPARISON (f2v) ===\n\n')
out.write('OUR TRANSCRIPTION:\n')
our_lines = {}
for m in our_pattern.finditer(ours):
    line_num, text = m.groups()
    text = text.strip().rstrip('-=')
    our_lines[line_num] = text
    out.write(f'  Line {line_num}: {text}\n')

out.write('\nZL OFFICIAL:\n')
zl_lines = {}
for m in zl_pattern.finditer(zl):
    line_num, text = m.groups()
    text = re.sub(r'<%>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[[^\]]+\]', '', text)
    text = text.strip()
    zl_lines[line_num] = text
    out.write(f'  Line {line_num}: {text}\n')

out.write('\n=== TOKEN COUNT COMPARISON ===\n')
for line_num in sorted(our_lines.keys(), key=int):
    our_tokens = len([t for t in re.split(r'[.\s,]+', our_lines[line_num]) if t])
    zl_tok = zl_lines.get(line_num, '')
    zl_tokens = len([t for t in re.split(r'[.\s,]+', zl_tok) if t]) if zl_tok else 0
    match = 'OK' if our_tokens == zl_tokens else 'DIFF'
    out.write(f'  Line {line_num}: Ours={our_tokens} tokens, ZL={zl_tokens} [{match}]\n')

out.write('\n=== STRUCTURAL STATISTICS ===\n')

# Count total folios in each
our_folios = set(re.findall(r'<(\d+[rv]\d*)\.', ours))
zl_folios = set(re.findall(r'<f(\d+[rv]\d*)\.', zl))
out.write(f'Total folios - Ours: {len(our_folios)}, ZL: {len(zl_folios)}\n')
out.write(f'Overlap: {len(our_folios & zl_folios)} folios in common\n')

# Count lines
our_line_count = len(re.findall(r'<\d+[rv]\d*\.\d+>', ours))
zl_line_count = len(re.findall(r'<f\d+[rv]\d*\.\d+', zl))
out.write(f'Total lines - Ours: {our_line_count}, ZL: {zl_line_count}\n')

# Character frequency analysis
out.write('\n=== CHARACTER FREQUENCY (letters only) ===\n')
our_letters = re.sub(r'[^a-zA-Z]', '', ours).lower()
zl_letters = re.sub(r'[^a-zA-Z]', '', zl).lower()

our_freq = Counter(our_letters)
zl_freq = Counter(zl_letters)

out.write(f'Ours top 15: {our_freq.most_common(15)}\n')
out.write(f'ZL top 15:   {zl_freq.most_common(15)}\n')

out.write('\n=== KEY QUESTION: Same data, different encoding? ===\n\n')

# Compare word structure patterns (dots as separators)
our_words = re.findall(r'[a-zA-Z0-9]+', ours)
zl_words = re.findall(r'[a-zA-Z]+', zl)

our_word_lens = Counter(len(w) for w in our_words[:1000])
zl_word_lens = Counter(len(w) for w in zl_words[:1000])

out.write('Word length distribution (first 1000 words):\n')
out.write(f'  Ours: {dict(sorted(our_word_lens.items()))}\n')
out.write(f'  ZL:   {dict(sorted(zl_word_lens.items()))}\n')

# Check if digit usage in ours correlates with specific EVA chars
out.write('\n=== DIGIT ANALYSIS IN OUR FILE ===\n')
digit_count = Counter(re.findall(r'\d', ours))
out.write(f'Digit frequency: {dict(sorted(digit_count.items()))}\n')
out.write(f'Total digits: {sum(digit_count.values())}\n')
out.write(f'Total letters: {len(our_letters)}\n')
out.write(f'Digit ratio: {sum(digit_count.values()) / (len(our_letters) + sum(digit_count.values())) * 100:.1f}%\n')

# CRITICAL: Check where our transcription came from
out.write('\n=== CRITICAL ASSESSMENT ===\n\n')

# Check first line of f1r in both
our_f1r = re.search(r'<1r\.1>(.+)', ours)
zl_f1r = re.search(r'<f1r\.1[^>]*>(.+)', zl)

if our_f1r and zl_f1r:
    our_text = our_f1r.group(1).strip()
    zl_text = re.sub(r'<[^>]+>', '', zl_f1r.group(1)).strip()
    zl_text = re.sub(r'\[[^\]]+\]', '', zl_text)

    out.write('First line of f1r:\n')
    out.write(f'  OURS: {our_text[:60]}...\n')
    out.write(f'  ZL:   {zl_text[:60]}...\n\n')

# Check if there's any recognizable pattern
out.write('Looking for encoding relationship...\n')

# In ZL, common bigrams are: ch, sh, ai, ii, ol, or, ar, etc.
# In ours, we see: 1o, o8, 8a, etc.
# Let's see if 1=ch, 8=d, etc.

out.write('\nHypothesis test: Does our "1" = ZL "ch"?\n')
our_1_count = ours.count('1')
zl_ch_count = zl.count('ch')
out.write(f'  Our "1" count: {our_1_count}\n')
out.write(f'  ZL "ch" count: {zl_ch_count}\n')

out.write('\nHypothesis test: Does our "8" = ZL "d"?\n')
our_8_count = ours.count('8')
zl_d_count = zl.count('d')
out.write(f'  Our "8" count: {our_8_count}\n')
out.write(f'  ZL "d" count: {zl_d_count}\n')

out.write('\nHypothesis test: Does our "9" = ZL "y"?\n')
our_9_count = ours.count('9')
zl_y_count = zl.count('y')
out.write(f'  Our "9" count: {our_9_count}\n')
out.write(f'  ZL "y" count: {zl_y_count}\n')

out.close()
print('Report written to comparison_report.txt')

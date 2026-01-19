#!/usr/bin/env python3
"""Quick baseline check."""

with open('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', 'r') as f:
    header = f.readline()
    initial = 0
    final = 0
    total = 0
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 15:
            transcriber = parts[12].strip('"') if len(parts) > 12 else ''
            if transcriber != 'H':
                continue
            lang = parts[6].strip('"')
            if lang == 'A':
                total += 1
                li = parts[13].strip('"')
                lf = parts[14].strip('"')
                if li == '1':
                    initial += 1
                if lf == '1':
                    final += 1

print(f'Total A tokens: {total}')
print(f'Line-initial: {initial} ({100*initial/total:.1f}%)')
print(f'Line-final: {final} ({100*final/total:.1f}%)')
print(f'Baseline boundary rate: ~{100*(initial+final)/total/2:.1f}% per position')

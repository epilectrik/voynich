#!/usr/bin/env python3
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']

# Check lines containing sparse flower tokens
print("SPARSE FLOWER TOKEN LINES:")
print()

for token, folio in [('ockho', 'f3v'), ('ysho', 'f44r'), ('okaro', 'f89v2')]:
    # Find which line
    token_df = df[(df['folio'] == folio)]
    # Need to find actual line
    for line in token_df['line_number'].unique():
        line_df = token_df[token_df['line_number'] == line]
        words = list(line_df['word'])
        if any(token in str(w) for w in words):
            print(f"{token} in {folio}:{line}")
            print(f"  Words: {words}")
            print(f"  Placements: {list(line_df['placement'])}")
            print()
            break

print("RICH ANIMAL TOKEN LINES (for comparison):")
print()

for token, folio in [('eoschso', 'f90r1'), ('eyd', 'f89r2')]:
    token_df = df[(df['folio'] == folio)]
    for line in token_df['line_number'].unique():
        line_df = token_df[token_df['line_number'] == line]
        words = list(line_df['word'])
        if any(token in str(w) for w in words):
            print(f"{token} in {folio}:{line}")
            print(f"  Words: {words[:15]}...")
            print(f"  Placements: {list(line_df['placement'])[:15]}...")
            print()
            break

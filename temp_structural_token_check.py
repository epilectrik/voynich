"""Check if key structural tokens are consistent across transcribers."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Key structural tokens from BCSC and CASC
structural_tokens = [
    'daiin', 'aiin', 'chedy', 'chey', 'shedy', 'or', 'ol', 'ar', 'al',
    'qokeedy', 'qokedy', 'qokaiin', 'cheol', 'shey', 'chol', 'chor',
    'dy', 'y', 'n', 'r', 'l', 'am', 'an'
]

print("Structural token counts by transcriber:\n")
print(f"{'Token':<12} {'H':<8} {'F':<8} {'C':<8} {'U':<8} {'V':<8} {'Ratio':>8}")
print("-" * 60)

for token in structural_tokens:
    h_count = len(df[(df['transcriber'] == 'H') & (df['word'] == token)])
    f_count = len(df[(df['transcriber'] == 'F') & (df['word'] == token)])
    c_count = len(df[(df['transcriber'] == 'C') & (df['word'] == token)])
    u_count = len(df[(df['transcriber'] == 'U') & (df['word'] == token)])
    v_count = len(df[(df['transcriber'] == 'V') & (df['word'] == token)])

    # Ratio of total to H
    total = h_count + f_count + c_count + u_count + v_count
    ratio = total / h_count if h_count > 0 else 0

    print(f"{token:<12} {h_count:<8} {f_count:<8} {c_count:<8} {u_count:<8} {v_count:<8} {ratio:>8.2f}x")

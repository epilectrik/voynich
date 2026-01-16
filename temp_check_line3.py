"""Check line numbering in f1r."""
import pandas as pd

DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

# Get all f1r lines
f1r = df[df['folio'] == 'f1r']

print(f"f1r has {len(f1r)} tokens total")
print(f"\nLine numbers in transcript: {sorted(f1r['line_number'].unique())}")

# Find where 'syaiir' appears
syaiir = f1r[f1r['word'] == 'syaiir']
print(f"\n'syaiir' appears on line(s): {syaiir['line_number'].unique()}")

# Get that line
line_num = syaiir['line_number'].iloc[0]
that_line = f1r[f1r['line_number'] == line_num]
print(f"\nLine {line_num} tokens ({len(that_line)}):")
for _, row in that_line.iterrows():
    print(f"  {row['word']}")

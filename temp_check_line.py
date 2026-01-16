"""Find the line with 'syaiir sheky or ykaiin shod cthoary cthes daraiin sa'."""
import pandas as pd

DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

# Search for lines containing 'syaiir'
syaiir_rows = df[df['word'] == 'syaiir']
print(f"Found 'syaiir' in {len(syaiir_rows)} places:")

for _, row in syaiir_rows.iterrows():
    folio = row['folio']
    line_num = row['line_number']
    section = row['section']
    currier = row['language']

    # Get all tokens on this line
    line_tokens = df[(df['folio'] == folio) & (df['line_number'] == line_num)]['word'].tolist()
    print(f"\n{folio} line {line_num} (section={section}, currier={currier}):")
    print(f"  {' '.join(str(t) for t in line_tokens)}")

    # Check if 'or' is in this line
    if 'or' in line_tokens:
        print(f"  ** Contains 'or' **")

"""Check standalone 'or' tokens in AZC folios."""
import pandas as pd

DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

# Get AZC section codes
azc_sections = {'Z', 'A', 'C'}

# Find standalone "or" tokens
or_tokens = df[df['word'] == 'or']
print(f"Total 'or' tokens in corpus: {len(or_tokens)}")

# In AZC sections
or_azc = or_tokens[or_tokens['section'].isin(azc_sections)]
print(f"'or' in AZC sections: {len(or_azc)}")

if len(or_azc) > 0:
    print(f"\nFolios with 'or':")
    for folio in sorted(or_azc['folio'].unique()):
        count = len(or_azc[or_azc['folio'] == folio])
        print(f"  {folio}: {count}")

    print(f"\nUnique AZC folios: {len(or_azc['folio'].unique())}")

    # Check line context - are these single-token lines?
    print(f"\nSample lines with 'or':")
    for _, row in or_azc.head(5).iterrows():
        folio = row['folio']
        line_num = row['line_number']
        # Get all tokens on this line
        line_tokens = df[(df['folio'] == folio) & (df['line_number'] == line_num)]['word'].tolist()
        print(f"  {folio} line {line_num}: {line_tokens}")

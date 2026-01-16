"""Check what sections the 'or'-heavy folios are in."""
import pandas as pd

DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

# Get folios with lots of 'or'
or_heavy = ['f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']

print("Sections for or-heavy folios:")
for folio in or_heavy:
    folio_data = df[df['folio'] == folio]
    if len(folio_data) > 0:
        sections = folio_data['section'].unique()
        print(f"  {folio}: {sections}")

print("\n\nNow checking Z/A/C specifically:")
azc_sections = {'Z', 'A', 'C'}
or_tokens = df[df['word'] == 'or']
or_azc_true = or_tokens[or_tokens['section'].isin(azc_sections)]

print(f"'or' in Z/A/C sections only: {len(or_azc_true)}")
print(f"\nFolios:")
for folio in sorted(or_azc_true['folio'].unique()):
    section = or_azc_true[or_azc_true['folio'] == folio]['section'].iloc[0]
    count = len(or_azc_true[or_azc_true['folio'] == folio])
    print(f"  {folio} ({section}): {count}")

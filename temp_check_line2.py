"""Check f1r line 3 structure carefully."""
import pandas as pd

DATA_PATH = "data/transcriptions/interlinear_full_words.txt"
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

# Get f1r line 3 specifically
line3 = df[(df['folio'] == 'f1r') & (df['line_number'] == 3)]

print(f"f1r line 3 has {len(line3)} tokens in transcript")
print(f"\nTokens:")
for i, (_, row) in enumerate(line3.iterrows()):
    print(f"  {i+1}: {row['word']}")

# Also check what the explorer would load
print("\n\nUsing FolioLoader:")
from apps.azc_folio_animator.core.folio_loader import FolioLoader

loader = FolioLoader()
loader.load()

folio = loader.get_folio('1r')
if folio and len(folio.lines) >= 3:
    line = folio.lines[2]  # 0-indexed
    print(f"Explorer shows line 3 with {len(line)} tokens:")
    for i, t in enumerate(line):
        print(f"  {i+1}: {t.text}")

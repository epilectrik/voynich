"""Debug the token count discrepancy."""
from apps.script_explorer.core.transcription import TranscriptionLoader

loader = TranscriptionLoader()
loader.load_interlinear("data/transcriptions/interlinear_full_words.txt")

folio = loader.get_folio('1r')
if folio:
    for line in folio.lines[:5]:  # First 5 lines
        print(f"Line {line.line_number}: {len(line.tokens)} tokens")
        print(f"  Text: {line.text[:100]}...")
        print(f"  Tokens: {line.tokens[:15]}...")
        print()

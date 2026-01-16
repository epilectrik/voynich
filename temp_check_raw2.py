"""Check ALL transcribers for f1r line 3."""
with open("data/transcriptions/interlinear_full_words.txt", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all rows for f1r line 3 (any transcriber)
by_transcriber = {}
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= 13:
        folio = parts[2].strip('"').lower()
        transcriber = parts[12].strip('"') if len(parts) > 12 else 'UNK'
        line_num_raw = parts[11].strip('"') if len(parts) > 11 else ''
        word = parts[0].strip('"')

        if folio == 'f1r':
            try:
                line_num = int(line_num_raw)
                if line_num == 3:
                    if transcriber not in by_transcriber:
                        by_transcriber[transcriber] = []
                    by_transcriber[transcriber].append(word)
            except:
                pass

print("f1r line 3 by transcriber:")
for t, words in by_transcriber.items():
    print(f"\n  {t}: {len(words)} tokens")
    print(f"    {words[:12]}...")

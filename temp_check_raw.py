"""Check raw transcript data for f1r line 3."""
with open("data/transcriptions/interlinear_full_words.txt", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Header:", lines[0][:200])
print()

# Find rows for f1r with line 3
count = 0
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= 13:
        folio = parts[2].strip('"').lower()
        transcriber = parts[12].strip('"') if len(parts) > 12 else ''
        line_num_raw = parts[11].strip('"') if len(parts) > 11 else ''
        word = parts[0].strip('"')

        if folio == 'f1r' and transcriber == 'H':
            # Try converting line_num to int
            try:
                line_num = int(line_num_raw)
                if line_num == 3:
                    count += 1
                    if count <= 15:
                        print(f"Row {count}: word='{word}', line_num_raw='{line_num_raw}'")
            except:
                pass

print(f"\nTotal rows for f1r line 3 (transcriber H): {count}")

import pathlib, base64, sys
data = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
decoded = base64.b64decode(data).decode('utf-8')
pathlib.Path(sys.argv[2]).write_text(decoded, encoding='utf-8')
print('Written', pathlib.Path(sys.argv[2]).stat().st_size, 'bytes')

import base64, pathlib, sys
content = pathlib.Path(sys.argv[1]).read_bytes()
pathlib.Path(sys.argv[2]).write_text(base64.b64encode(content).decode(), encoding='utf-8')
print('Encoded', len(content), 'bytes')

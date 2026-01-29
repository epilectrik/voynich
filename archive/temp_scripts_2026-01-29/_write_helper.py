import pathlib, base64, sys
p=pathlib.Path(sys.argv[1])
p.write_bytes(base64.b64decode(sys.argv[2]))
print(p.stat().st_size)
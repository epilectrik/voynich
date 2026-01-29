import pathlib, sys
lines = []
for f in sorted(pathlib.Path(sys.argv[1]).glob("_chunk*.txt")):
    lines.append(f.read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2])
out.write_text("".join(lines), encoding="utf-8")
print("Assembled", out.stat().st_size, "bytes from", len(lines), "chunks")

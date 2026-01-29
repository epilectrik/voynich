import sys, pathlib
target = sys.argv[1]
data = sys.stdin.read()
pathlib.Path(target).write_text(data, encoding='utf-8')
print('Written', len(data), 'chars')

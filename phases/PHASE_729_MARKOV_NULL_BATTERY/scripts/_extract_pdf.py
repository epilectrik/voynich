import sys
try:
    from pypdf import PdfReader
    lib = 'pypdf'
except ImportError:
    try:
        from PyPDF2 import PdfReader
        lib = 'PyPDF2'
    except ImportError:
        print('NEED_INSTALL')
        sys.exit(1)

print(f'Using {lib}')
path = r'C:\Users\epilectrik\.claude\projects\C--git-voynich\9aebb236-c22c-48f8-9d8d-a12db3211bc9\tool-results\webfetch-1779767035791-aq6ng5.bin'
r = PdfReader(path)
print(f'Pages: {len(r.pages)}')
out_path = r'C:\git\voynich\_wilken_key.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    for i, p in enumerate(r.pages):
        f.write(f'\n===== PAGE {i+1} =====\n')
        try:
            f.write(p.extract_text() or '')
        except Exception as e:
            f.write(f'[extraction error: {e}]')
print(f'Wrote {out_path}')

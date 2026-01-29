import pathlib
target = pathlib.Path(r'C:/git/voynich/phases/RI_FUNCTIONAL_IDENTITY/scripts/line_type_comparison.py')
# Read template from sibling file
tmpl = pathlib.Path(r'C:/git/voynich/_template.py').read_text(encoding='utf-8')
target.write_text(tmpl, encoding='utf-8')
print('Written', target.stat().st_size, 'bytes to', target)

import pathlib
import textwrap

def gen():
    return open(r"C:\gitoynich\_script_template.txt", "r", encoding="utf-8").read()

target = pathlib.Path(r"C:\gitoynich\phases\RI_FUNCTIONAL_IDENTITY\scripts\line_type_comparison.py")
target.write_text(gen(), encoding="utf-8")
print("Written", target.stat().st_size, "bytes")

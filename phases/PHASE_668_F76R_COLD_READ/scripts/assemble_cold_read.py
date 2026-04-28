"""
Assemble a cold read .md file by combining:
1. Header section (recipe, predictions, overview) from the existing cold read
2. Per-paragraph: recipe-says line + generated workshop tables + structural profile from existing
3. Cross-paragraph patterns + verdict from existing
"""
import sys

folio = sys.argv[1] if len(sys.argv) > 1 else 'f84r'
cold_read_path = f'phases/PHASE_668_F76R_COLD_READ/results/cold_reads/{folio}_cold_read.md'
tables_path = f'phases/PHASE_668_F76R_COLD_READ/results/data/{folio}_workshop_tables.md'

# Read existing cold read
with open(cold_read_path, encoding='utf-8') as f:
    lines = f.readlines()

# Read generated tables
with open(tables_path, encoding='utf-8') as f:
    tables = f.read()

# Find section boundaries
header_end = None  # line before "## Paragraph 1"
p1_recipe_says = None
p1_struct_start = None
p2_header = None
p2_recipe_says = None
p2_struct_start = None
p3_header = None
p3_recipe_says = None
p3_struct_start = None
cross_para_start = None

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('## Paragraph 1'):
        header_end = i
    elif stripped.startswith('**Recipe says:**') and p1_recipe_says is None:
        p1_recipe_says = i
    elif stripped.startswith('### P1 Structural'):
        p1_struct_start = i
    elif stripped.startswith('## Paragraph 2'):
        p2_header = i
    elif stripped.startswith('**Recipe says:**') and p2_recipe_says is None and p2_header is not None:
        p2_recipe_says = i
    elif stripped.startswith('### P2 Structural'):
        p2_struct_start = i
    elif stripped.startswith('## Paragraph 3'):
        p3_header = i
    elif stripped.startswith('**Recipe says:**') and p3_recipe_says is None and p3_header is not None:
        p3_recipe_says = i
    elif stripped.startswith('### P3 Structural'):
        p3_struct_start = i
    elif stripped.startswith('## Cross-Paragraph'):
        cross_para_start = i

# Split tables by paragraph (L1-L12 = P1, L13-L14 = P2, L15+ = P3)
# We'll use the line numbers from the decode to split
table_lines = tables.split('\n')
p1_tables = []
p2_tables = []
p3_tables = []
current_target = None

for tl in table_lines:
    if tl.startswith('**L'):
        # Extract line number
        import re
        m = re.match(r'\*\*L(\d+)', tl)
        if m:
            lnum = int(m.group(1))
            if lnum <= 12:
                current_target = p1_tables
            elif lnum <= 14:
                current_target = p2_tables
            else:
                current_target = p3_tables
    if current_target is not None:
        current_target.append(tl)

# Assemble output
output = []

# 1. Header through "## Paragraph 1" line
output.extend(lines[:header_end + 1])

# 2. P1 recipe-says line
output.append(lines[p1_recipe_says])
output.append('\n')
output.append('### Line-by-Line Token Reading (v2 workshop readings)\n')
output.append('\n')
output.append('Every token on every line. Reading source: **B Dict** = B Operational Dictionary, **Comp-v2** = composed workshop reading from atoms, **---** = truly unrecognized.\n')
output.append('\n')

# P1 tables
output.append('\n'.join(p1_tables))
output.append('\n\n')

# P1 structural profile through P2 header
for i in range(p1_struct_start, p2_header):
    output.append(lines[i])

# P2 header + recipe-says
output.append(lines[p2_header])
output.append(lines[p2_recipe_says])
output.append('\n')
output.append('### Line-by-Line Token Reading (v2 workshop readings)\n')
output.append('\n')

# P2 tables
output.append('\n'.join(p2_tables))
output.append('\n\n')

# P2 structural profile through P3 header
for i in range(p2_struct_start, p3_header):
    output.append(lines[i])

# P3 header + recipe-says
output.append(lines[p3_header])
output.append(lines[p3_recipe_says])
output.append('\n')
output.append('### Line-by-Line Token Reading (v2 workshop readings)\n')
output.append('\n')

# P3 tables
output.append('\n'.join(p3_tables))
output.append('\n\n')

# P3 structural profile through cross-paragraph
for i in range(p3_struct_start, cross_para_start):
    output.append(lines[i])

# Cross-paragraph patterns + verdict to end
for i in range(cross_para_start, len(lines)):
    output.append(lines[i])

# Write output
with open(cold_read_path, 'w', encoding='utf-8') as f:
    f.write(''.join(output))

print(f'Assembled {cold_read_path}')
print(f'P1 tables: {len(p1_tables)} lines')
print(f'P2 tables: {len(p2_tables)} lines')
print(f'P3 tables: {len(p3_tables)} lines')

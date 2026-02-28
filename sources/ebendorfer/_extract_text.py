"""Extract plain text from Ebendorfer Chronica Austriae TEI-XML (openMGH).

Handles:
- Page breaks (<pb>) -> [Page N] markers
- Line breaks (<lb>) -> newlines
- Split words (<w corresp="...">) -> rejoined using lemma attribute
- Italic markers (<hi rend="ITALICS">) -> just text
- Editorial additions (angle brackets) -> preserved
"""
import re

INPUT = r"C:\git\voynich\sources\ebendorfer\extracted\bsb00000693.xml"
OUTPUT = r"C:\git\voynich\sources\ebendorfer\ebendorfer_chronica_austriae.txt"

with open(INPUT, 'r', encoding='utf-8') as f:
    xml = f.read()

# Extract just the body content
body_match = re.search(r'<body>(.*?)</body>', xml, re.DOTALL)
if not body_match:
    raise ValueError("Could not find <body> in XML")
body = body_match.group(1)

# Step 1: Handle split words using the lemma attribute
# Split words come in pairs with shared corresp="#wN #wM"
# Strategy: replace the first <w> with the full lemma, delete the second <w>

# Collect all split word pairs
# First pass: find all <w> elements with corresp attributes
w_elements = list(re.finditer(
    r'<w\s+lemma="([^"]*)"\s+xml:id="(w\d+)"\s+corresp="(#w\d+\s+#w\d+)">(.*?)</w>',
    body, re.DOTALL
))

# Build replacement map
# For each pair, the first element gets the lemma, second gets deleted
pairs = {}  # corresp_key -> [first_match, second_match]
for m in w_elements:
    lemma = m.group(1)
    wid = m.group(2)
    corresp = m.group(3)
    ids = [x.lstrip('#') for x in corresp.split()]
    if len(ids) == 2:
        key = tuple(ids)
        if key not in pairs:
            pairs[key] = []
        pairs[key].append(m)

# Build replacement list (position, length, replacement_text)
replacements = []
for key, matches in pairs.items():
    if len(matches) == 2:
        first, second = matches
        lemma = first.group(1)
        # First element -> lemma text
        replacements.append((first.start(), first.end(), lemma))
        # Second element -> empty (delete it, plus any preceding line break)
        # We need to also remove the <lb> before the second element
        replacements.append((second.start(), second.end(), ''))

# Apply replacements in reverse order to preserve positions
replacements.sort(key=lambda x: x[0], reverse=True)
for start, end, text in replacements:
    body = body[:start] + text + body[end:]

# Step 2: Handle any remaining <w> elements (not split, just annotated)
body = re.sub(r'<w\s+[^>]*>([^<]*)</w>', r'\1', body)
# Nested: <w ...><hi ...>text</hi></w>
body = re.sub(r'<w\s+[^>]*>(.*?)</w>', lambda m: re.sub(r'<[^>]+>', '', m.group(1)), body, flags=re.DOTALL)

# Step 3: Convert page breaks to markers
body = re.sub(r'<pb[^>]*\bn="([^"]*)"[^>]*/>', r'\n\n[Page \1]\n', body)

# Step 4: Convert line breaks to newlines
body = re.sub(r'<lb[^>]*/>', '\n', body)

# Step 5: Strip all remaining XML tags
body = re.sub(r'<[^>]+>', '', body)

# Step 6: Clean up whitespace
body = re.sub(r'[ \t]+', ' ', body)  # collapse horizontal whitespace
body = re.sub(r' *\n *', '\n', body)  # trim spaces around newlines
body = re.sub(r'\n{3,}', '\n\n', body)  # collapse excessive blank lines

# Step 7: Remove orphaned line breaks between a replaced split word
# After deletion, there may be empty lines or stray newlines where the second
# half of a split word was removed. Clean those up.
# Pattern: a word fragment at end of line followed by empty line
body = re.sub(r'\n\n+(\[Page)', r'\n\n\1', body)  # preserve page markers

# Remove completely empty lines that aren't before [Page markers
lines = body.split('\n')
cleaned = []
for i, line in enumerate(lines):
    if line.strip() == '':
        # Keep blank line only before [Page or after [Page
        if i+1 < len(lines) and lines[i+1].strip().startswith('[Page'):
            cleaned.append('')
        elif i > 0 and lines[i-1].strip().startswith('[Page'):
            continue  # skip blank after page marker
        elif i > 0 and cleaned and cleaned[-1] == '':
            continue  # skip consecutive blanks
        else:
            cleaned.append('')
    else:
        cleaned.append(line)
body = '\n'.join(cleaned)

# Write output
header = """THOMAS EBENDORFER: CHRONICA AUSTRIAE
=====================================

Source: MGH Scriptores Rerum Germanicarum, Nova Series, vol. 13
Editor: Alphons Lhotsky
Published: Berlin-Zurich: Weidmann, 1967
Digital source: openMGH (https://www.mgh.de/en/digital-mgh/openmgh/)
Download: https://data.mgh.de/openmgh/bsb00000693.zip
License: CC BY 4.0 (annotations by MGH/BSB); text in public domain

Extracted from TEI-XML by automated script.
Page numbers in [brackets] refer to the Lhotsky 1967 edition.

=====================================

"""

output = header + body.strip() + '\n'

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(output)

# Stats
page_count = body.count('[Page ')
line_count = len([l for l in body.split('\n') if l.strip()])
char_count = len(body)

# Verify some known split words
test_words = ['futurorum', 'ignorans', 'lectorem', 'congregatis']
found = {w: w in body for w in test_words}
print(f"Extracted {line_count} text lines across {page_count} pages")
print(f"Output: {OUTPUT}")
print(f"File size: {len(output):,} bytes")
print(f"Split word tests: {found}")

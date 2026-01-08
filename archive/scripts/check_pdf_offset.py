import fitz
doc = fitz.open('C:/git/voynich/data/scans/Voynich_Manuscript.pdf')

# Check first 10 pages by extracting small preview
print(f"Total pages: {len(doc)}")
print("\nFirst 10 pages (check for cover/title pages):")
for i in range(min(10, len(doc))):
    page = doc[i]
    # Get page dimensions to see if consistent
    rect = page.rect
    print(f"Page {i}: {rect.width:.0f}x{rect.height:.0f}")

# If f2v = p004 (page 4), that's index 3
# PDF structure: page 0-1 might be covers, then f1r starts
print("\nIf PDF has covers, the mapping might be:")
print("  PDF page 0 = cover?")
print("  PDF page 1 = f1r")
print("  PDF page 2 = f1v")
print("  PDF page 3 = f2r")
print("  PDF page 4 = f2v (matches p004)")

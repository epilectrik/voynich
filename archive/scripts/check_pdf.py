import fitz
doc = fitz.open('C:/git/voynich/data/scans/Voynich_Manuscript.pdf')
for i in range(min(10, len(doc))):
    page = doc[i]
    text = page.get_text().strip()[:100]
    print(f'Page {i}: {text if text else "[no text - image only]"}')

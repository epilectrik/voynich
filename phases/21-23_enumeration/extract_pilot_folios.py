#!/usr/bin/env python3
"""
Extract pilot folio images from Voynich Manuscript PDF.
Creates a folio-to-page mapping and extracts images for visual coding.
"""

import fitz
import os
import json

PDF_PATH = r'C:\git\voynich\data\scans\Voynich_Manuscript.pdf'
OUTPUT_DIR = r'C:\git\voynich\data\scans\extracted'

# The 30 pilot folios from pilot_folio_verification_report.json
PILOT_FOLIOS = [
    "f38r", "f25r", "f11r", "f11v", "f5v", "f10v", "f38v", "f5r", "f36r", "f30v",
    "f22v", "f9v", "f90v2", "f32v", "f17r", "f18r", "f9r", "f20v", "f2r", "f47v",
    "f24v", "f56r", "f42r", "f49v", "f51v", "f45v", "f3v", "f29v", "f4v", "f23v"
]

def build_folio_page_mapping():
    """
    Build a mapping from folio IDs to PDF page numbers.
    Voynich PDF structure (holybooks version):
    - Page 0-2: Cover/intro pages
    - Page 3+: Manuscript pages

    Folio numbering: f1r, f1v, f2r, f2v, ... (recto then verso)
    Some folios are missing or have special sections (f90v2).
    """
    mapping = {}

    # Standard folio sequence (approximate - may need adjustment)
    # The holybooks PDF seems to start manuscript proper around page 3
    # Each folio has 2 sides (r and v), so folio N corresponds to pages:
    # f1r = page 3, f1v = page 4, f2r = page 5, f2v = page 6, etc.

    # However, the actual PDF may have variations. Let's use a known mapping.
    # Based on typical Voynich PDF organization:

    # Basic formula: for folio N, r/v:
    # page_num = offset + (N-1)*2 + (0 if 'r' else 1)

    offset = 2  # Adjust based on PDF structure

    for folio in PILOT_FOLIOS:
        if folio == "f90v2":
            # Special case: f90v2 is a foldout section
            # This is on a later page, need to determine manually
            mapping[folio] = None  # Will be set manually
            continue

        # Parse folio ID
        folio_num_str = folio[1:-1]  # Remove 'f' and 'r'/'v'
        side = folio[-1]  # 'r' or 'v'

        try:
            folio_num = int(folio_num_str)
        except ValueError:
            print(f"Could not parse folio: {folio}")
            mapping[folio] = None
            continue

        # Calculate page number
        page_num = offset + (folio_num - 1) * 2 + (0 if side == 'r' else 1)
        mapping[folio] = page_num

    return mapping


def extract_folio_image(doc, page_num, folio_id, output_dir, dpi=150):
    """Extract a single page as an image."""
    if page_num is None or page_num >= doc.page_count:
        print(f"Invalid page number for {folio_id}: {page_num}")
        return None

    page = doc[page_num]

    # Convert to image
    mat = fitz.Matrix(dpi/72, dpi/72)  # Scale factor for DPI
    pix = page.get_pixmap(matrix=mat)

    output_path = os.path.join(output_dir, f"{folio_id}.png")
    pix.save(output_path)
    print(f"Extracted {folio_id} (page {page_num}) -> {output_path}")

    return output_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Building folio-to-page mapping...")
    mapping = build_folio_page_mapping()

    # Save mapping for reference
    mapping_path = os.path.join(OUTPUT_DIR, 'folio_page_mapping.json')
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Saved mapping to {mapping_path}")

    print(f"\nOpening PDF: {PDF_PATH}")
    doc = fitz.open(PDF_PATH)
    print(f"PDF has {doc.page_count} pages")

    print(f"\nExtracting {len(PILOT_FOLIOS)} pilot folios...")
    extracted = []

    for folio in PILOT_FOLIOS:
        page_num = mapping.get(folio)
        result = extract_folio_image(doc, page_num, folio, OUTPUT_DIR)
        if result:
            extracted.append(folio)

    doc.close()

    print(f"\nExtracted {len(extracted)}/{len(PILOT_FOLIOS)} folios")
    if len(extracted) < len(PILOT_FOLIOS):
        missing = set(PILOT_FOLIOS) - set(extracted)
        print(f"Missing: {missing}")


if __name__ == "__main__":
    main()
